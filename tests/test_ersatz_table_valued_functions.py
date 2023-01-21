import sqlite3
from ersatz_table_valued_functions import rewrite

def test_rewrite_noop():
    """SQL that doesn't have a function call in it should be ignored."""
    candidate = 'SELECT * FROM func'
    assert rewrite(candidate, {}) == candidate

def test_rewrite_noop_unknown_function():
    """Functions we don't recognize should be ignored."""
    candidate = 'SELECT * FROM func()'
    assert rewrite(candidate, {}) == candidate

def test_rewrite_case_match():
    """SQL that has a function call in it should be rewritten."""
    mappings = {
        'FUNC': ['foo', 'bar']
    }

    candidate = 'SELECT foo FROM func(1, 2)'
    rewritten = rewrite(candidate, mappings)
    assert candidate != rewritten

    # Verify the query works if we replace FUNC(1, 2) with a literal JSON value
    con = sqlite3.connect(':memory:')
    rv = con.execute(rewritten.replace('FUNC(1, 2)', "'[[1, 2], [2, 3]]'")).fetchall()

    assert rv == [(1,), (2,)]
