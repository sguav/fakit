# tests/test_all.py

# Import individual test modules so pytest can discover and run them
import tests.test_change_authors
import tests.test_change_messages
import tests.test_change_dates

# Optionally, you can define a simple meta-test to call all tests manually
# but pytest will already discover and run all functions starting with `test_`
# in the imported modules, so this is mostly for organizational clarity.
def test_all_features():
    # This is a placeholder; actual test functions are executed by pytest automatically
    pass
