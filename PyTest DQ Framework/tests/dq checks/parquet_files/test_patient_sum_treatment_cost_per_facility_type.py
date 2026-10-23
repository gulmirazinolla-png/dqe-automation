"""
Description: Data Quality checks for patient_sum_treatment_cost_per_facility_type dataset.
Requirement(s): DQE-HW-1
Author(s): Mira
"""

import pandas as pd
import pytest

@pytest.fixture(scope='module')
def source_data(db_connection):
    source_query = """
    SELECT
        f.facility_type AS facility_type,
        p.first_name || ' ' || p.last_name AS full_name,
        SUM(v.treatment_cost) AS sum_treatment_cost
    FROM visits v
    JOIN facilities f ON v.facility_id = f.id
    JOIN patients p ON v.patient_id = p.id
    GROUP BY f.facility_type, p.first_name, p.last_name
    """
    source = db_connection.get_data_sql(source_query)
    source["sum_treatment_cost"] = source["sum_treatment_cost"].astype(float)
    return source


@pytest.fixture(scope='module')
def target_data(parquet_reader):
    target_path = '/parquet_data/patient_sum_treatment_cost_per_facility_type'
    target = parquet_reader.process(target_path, include_subfolders=True)
    target = target.drop(columns=["partition_date", "facility_type_partition"], errors="ignore")
    target["sum_treatment_cost"] = target["sum_treatment_cost"].astype(float)
    return target


@pytest.mark.parquet_data
@pytest.mark.smoke
@pytest.mark.patient_sum_treatment_cost_per_facility_type
def test_check_dataset_is_not_empty(target_data, data_quality_library):
    data_quality_library.check_dataset_is_not_empty(target_data)


@pytest.mark.parquet_data
@pytest.mark.patient_sum_treatment_cost_per_facility_type
def test_check_data_completeness(source_data, target_data, data_quality_library):
    data_quality_library.check_data_completeness(source_data, target_data)


@pytest.mark.parquet_data
@pytest.mark.patient_sum_treatment_cost_per_facility_type
def test_check_data_full_data_set(source_data, target_data, data_quality_library):
    data_quality_library.check_data_full_data_set(source_data, target_data)


@pytest.mark.parquet_data
@pytest.mark.patient_sum_treatment_cost_per_facility_type
def test_check_count(source_data, target_data, data_quality_library):
    data_quality_library.check_count(source_data, target_data)


@pytest.mark.parquet_data
@pytest.mark.patient_sum_treatment_cost_per_facility_type
def test_check_uniqueness(target_data, data_quality_library):
    data_quality_library.check_duplicates(target_data, ['facility_type', 'full_name'])


@pytest.mark.parquet_data
@pytest.mark.patient_sum_treatment_cost_per_facility_type
def test_check_not_null_values(target_data, data_quality_library):
    data_quality_library.check_not_null_values(
        target_data, ['facility_type', 'full_name', 'sum_treatment_cost']
    )
    negative_cost_rows = target_data.loc[target_data['sum_treatment_cost'] < 0]
    assert negative_cost_rows.empty, (
        "Non-negative treatment cost check failed: "
        f"{len(negative_cost_rows)} rows have negative sum_treatment_cost. "
        f"Sample rows: {negative_cost_rows.head(5).to_dict(orient='records')}"
    )