from pathlib import Path

import pandas as pd
import pytest


DATA_FILE = Path(__file__).resolve().parent.parent / "src" / "data" / "data.csv"

#fixture for a path to the CSV file
@pytest.fixture(scope="session")
def path_to_file():
    return DATA_FILE


##fixture that reads it and returns its content
@pytest.fixture(scope="session")
def csv_data(path_to_file):
    return pd.read_csv(path_to_file)


#fixture that validates
@pytest.fixture(scope="session")
def validate_schema():
    def _validate(actual_schema, expected_schema):
        assert list(actual_schema) == list(expected_schema), (
            f"Schema mismatch: expected {list(expected_schema)}, "
            f"got {list(actual_schema)}"
        )
    return _validate


#hook to mark unmarked tests with a custom mark
def pytest_collection_modifyitems(items):
    for item in items:
        if not list(item.iter_markers()):
            item.add_marker(pytest.mark.unmarked)