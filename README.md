# ersatz-table-valued-functions

[![PyPI](https://img.shields.io/pypi/v/ersatz-table-valued-functions.svg)](https://pypi.org/project/ersatz-table-valued-functions/)
[![Changelog](https://img.shields.io/github/v/release/cldellow/ersatz-table-valued-functions?include_prereleases&label=changelog)](https://github.com/cldellow/ersatz-table-valued-functions/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/cldellow/ersatz-table-valued-functions/blob/main/LICENSE)

A bad idea.

**ersatz** *(adj.)*: made or used as a substitute, typically an inferior one, for something else.

## Installation

Install this library using `pip`:

    pip install ersatz-table-valued-functions

## Usage

This library lets you rewrite queries like:

```sql
SELECT root, square FROM tbl_squares(3)
```

into queries like:

```sql
WITH _ersatz_1 AS (
  SELECT
    JSON_EXTRACT(value, '$[0]') AS "root",
    JSON_EXTRACT(value, '$[1]') AS "square"
  FROM JSON_EACH((SELECT tbl_squares(3)))
)
SELECT root, square FROM _ersatz_1
```

That is: it translates a query that _looks_ like it needs a table-valued function
into one that uses a scalar-valued function that returns a JSON 2D array.


To use it:

```python
from ersatz_table_valued_functions import rewrite

rewrite('SELECT root, square FROM tbl_squares(3)', { 'TBL_SQUARES': ['root', 'square'] })
```


## Development

To contribute to this library, first checkout the code. Then create a new virtual environment:

    cd ersatz-table-valued-functions
    python -m venv venv
    source venv/bin/activate

Now install the dependencies and test dependencies:

    pip install -e '.[test]'

To run the tests:

    pytest
