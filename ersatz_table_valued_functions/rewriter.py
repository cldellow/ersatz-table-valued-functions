from sqlglot import parse_one, exp

DUMMY_FUNCTION_NAME = 'DUMMY_FUNCTION_NAME'

# Goal: translate any SELECT expression that has the simple form of
#
# SELECT foo FROM func('bar')
#
# into
#
# WITH _ersatz_1 AS (
#   SELECT json_extract(value, '$[0]') AS foo
#   FROM json_each((SELECT func('bar')))
# ) SELECT foo FROM _ersatz_1
#
# Limitations:
# - We do minimal processing -- table aliases, column aliases will cause things to break
# - Joining other tables doesn't work, you can only invoke the function with a literal,
#   or the result of a subquery
#
# The keys in `mappings` should be upper-case.
def rewrite(sql, mappings):
    if not might_have_function_calls_(sql, mappings):
        return sql

    parsed = parse_one(sql)

    counter = 0
    rewritten = False

    def transformer(node):
        nonlocal rewritten
        nonlocal counter

        if isinstance(node, exp.Select):
            # 1. Check to see if this should be rewritten.

            # We only support when the FROM clause has 1 entry that is a function.

            from_exprs = node.args['from'].expressions

            if len(from_exprs) != 1:
                return node

            from_expr = from_exprs[0]


            # Is it an anonymous function?
            if not isinstance(from_expr.this, exp.Anonymous):
                return node

            func_expr = from_expr.this

            func_name = func_expr.this.upper()
            if not func_name in mappings:
                return node

            column_names = mappings[func_name]

            # 2. Rewrite it.
            counter += 1

            # We're a little lazy here -- we parse a template query,
            # then transform _that_ query. This lets us avoid knowing
            # much about how sqlglot's OM works.

            cte_name = '_ersatz_{}'.format(counter)
            columns = []
            for i, column_name in enumerate(column_names):
                columns.append("json_extract(value, '$[{}]') AS \"{}\"".format(i, column_name))

            new_select = parse_one(
                'SELECT {} FROM json_each((SELECT {}()))'.format(
                    ', '.join(columns),
                    DUMMY_FUNCTION_NAME
                )
            )

            # Transform our new select so that DUMMY_FUNCTION_NAME() is replaced with the user's
            # func_expr
            new_select = replace_func_(new_select, func_expr)

            # Transform our old select so that;
            # - the new select is available as a CTE
            # - the from clause uses the CTE

            rv = node.from_(cte_name, append=False)
            rv = rv.with_(cte_name, new_select)
            rewritten = True
            return rv

        return node

    transformed = parsed.transform(transformer)

    if not rewritten:
        return sql

    return transformed.sql()

def replace_func_(expr, func_expr):
    def transformer(node):
        if isinstance(node, exp.Anonymous) and node.this == DUMMY_FUNCTION_NAME:
            return func_expr

        return node

    return expr.transform(transformer)

def might_have_function_calls_(sql, mappings):
    # We want to be very non-invasive, so don't even try parsing the SQL unless
    # it looks like it has a function reference in it.

    upper = sql.upper()
    for key in mappings.keys():
        if ' {}('.format(key) in upper:
            return True

    return False

