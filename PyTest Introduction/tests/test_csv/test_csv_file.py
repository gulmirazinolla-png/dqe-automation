import re

import pytest

EXPECTED_SCHEMA = ["id", "name", "age", "email", "is_active"]
EMAIL_PATTERN = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")


def test_file_not_empty(csv_data):
    assert not csv_data.empty, "The CSV file is empty"


@pytest.mark.validate_csv
def test_validate_schema(csv_data, validate_schema):
    validate_schema(csv_data.columns.tolist(), EXPECTED_SCHEMA)


@pytest.mark.validate_csv
@pytest.mark.skip(reason="Age validation is skipped on purpose (homework requirement)")
def test_age_column_valid(csv_data):
    invalid = csv_data[~csv_data["age"].between(0, 100)]
    assert invalid.empty, f"Ages outside 0-100 found:\n{invalid}"


@pytest.mark.validate_csv
def test_email_column_valid(csv_data):
    invalid = csv_data[~csv_data["email"].astype(str).apply(lambda e: bool(EMAIL_PATTERN.match(e)))]
    assert invalid.empty, f"Invalid email addresses found:\n{invalid[['id', 'email']]}"


@pytest.mark.validate_csv
@pytest.mark.xfail(reason="The CSV file contains a duplicate row (id 4)")
def test_duplicates(csv_data):
    duplicates = csv_data[csv_data.duplicated(keep=False)]
    assert duplicates.empty, f"Duplicate rows found:\n{duplicates}"


@pytest.mark.parametrize("id, is_active", [(1, False), (2, True)])
def test_active_players(csv_data, id, is_active):
    actual = csv_data.loc[csv_data["id"] == id, "is_active"].iloc[0]
    assert actual == is_active, f"id={id}: expected is_active={is_active}, got {actual}"


def test_active_player(csv_data):
    actual = csv_data.loc[csv_data["id"] == 2, "is_active"].iloc[0]
    assert actual == True, f"id=2: expected is_active=True, got {actual}"