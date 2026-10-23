import os

import pytest

from src.connectors.postgres.postgres_connector import PostgresConnectorContextManager
from src.connectors.file_system.parquet_reader import ParquetReader
from src.data_quality.data_quality_validation_library import DataQualityLibrary


def pytest_addoption(parser):
    # CLI defaults follow the PostgreSQL environment, with local development defaults.
    parser.addoption("--db_host", action="store", default=os.environ.get("POSTGRES_HOST", "localhost"))
    parser.addoption("--db_port", action="store", default=os.environ.get("POSTGRES_PORT", "5434"))
    parser.addoption("--db_name", action="store", default=os.environ.get("POSTGRES_DB", "mydatabase"))
    parser.addoption("--db_user", action="store", default=os.environ.get("POSTGRES_USER"))
    parser.addoption("--db_password", action="store", default=os.environ.get("POSTGRES_PASSWORD"))


@pytest.fixture(scope="session")
def db_connection(request):
    db_user = request.config.getoption("db_user")
    db_password = request.config.getoption("db_password")
    missing = [
        option
        for option, value in (("--db_user", db_user), ("--db_password", db_password))
        if not value
    ]
    if missing:
        pytest.fail(f"Missing required database options: {', '.join(missing)}")

    with PostgresConnectorContextManager(
        db_host=request.config.getoption("db_host"),
        db_port=int(request.config.getoption("db_port")),
        db_name=request.config.getoption("db_name"),
        db_user=db_user,
        db_password=db_password,
    ) as db_connector:
        yield db_connector


@pytest.fixture(scope="session")
def parquet_reader():
    return ParquetReader()


@pytest.fixture(scope="session")
def data_quality_library():
    return DataQualityLibrary()