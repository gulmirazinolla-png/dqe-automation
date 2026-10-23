"""
Description: Data Quality checks for facility_name_min_time_spent_per_visit_date dataset.
Requirement(s): DQE-HW-1
Author(s): Mira
"""

import pandas as pd
import pytest


@pytest.fixture(scope='module')
def source_data(db_connection):
    source_query = """
    SELECT
        f.facility_name AS facility_name,
        DATE(v.visit_timestamp) AS visit_date,
        MIN(v.duration_minutes) AS min_time_spent
    FROM visits v
    JOIN facilities f ON v.facility_id = f.id
    GROUP BY f.facility_name, DATE(v.visit_timestamp)
    """
    source = db_connection.get_data_sql(source_query)
    source["visit_date"] = pd.to_datetime(source["visit_date"])
    source["min_time_spent"] = source["min_time_spent"].astype(float)
    return source


@pytest.fixture(scope='module')
def target_data(parquet_reader):
    target_path = '/parquet_data/facility_name_min_time_spent_per_visit_date'
    target = parquet_reader.process(target_path, include_subfolders=True)
    target = target.drop(columns=["partition_date"], errors="ignore")
    target["visit_date"] = pd.to_datetime(target["visit_date"])
    target["min_time_spent"] = target["min_time_spent"].astype(float)
    return target


@pytest.mark.parquet_data
@pytest.mark.smoke
@pytest.mark.facility_name_min_time_spent_per_visit_date
def test_check_dataset_is_not_empty(target_data, data_quality_library):
    data_quality_library.check_dataset_is_not_empty(target_data)


@pytest.mark.parquet_data
@pytest.mark.facility_name_min_time_spent_per_visit_date
def test_check_data_completeness(source_data, target_data, data_quality_library):
    data_quality_library.check_data_completeness(source_data, target_data)


@pytest.mark.parquet_data
@pytest.mark.facility_name_min_time_spent_per_visit_date
def test_check_data_full_data_set(source_data, target_data, data_quality_library):
    data_quality_library.check_data_full_data_set(source_data, target_data)


@pytest.mark.parquet_data
@pytest.mark.facility_name_min_time_spent_per_visit_date
def test_check_count(source_data, target_data, data_quality_library):
    data_quality_library.check_count(source_data, target_data)


@pytest.mark.parquet_data
@pytest.mark.facility_name_min_time_spent_per_visit_date
def test_check_uniqueness(target_data, data_quality_library):
    data_quality_library.check_duplicates(target_data, ['facility_name', 'visit_date'])


@pytest.mark.parquet_data
@pytest.mark.facility_name_min_time_spent_per_visit_date
def test_check_not_null_values(target_data, data_quality_library):
    data_quality_library.check_not_null_values(
        target_data, ['facility_name', 'visit_date', 'min_time_spent']
    )