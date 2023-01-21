from ersatz_table_valued_functions import example_function


def test_example_function():
    assert example_function() == 2
