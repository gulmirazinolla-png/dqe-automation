---
name: generate-parquet-dq-tests
description: >-
  Creates one PyTest data-quality test module per Parquet dataset from
  docs/parquet-aggregated-data-mapping.md. Invoke explicitly when the PyTest DQ
  Framework exists and a mapping is available; refuse framework, Jenkins,
  fixture, or unrelated changes.
disable-model-invocation: true
---

# Generate Parquet DQ tests

Complete this skill as **Step 2** of the PyTest DQ assignment. Read first:

- `PyTest DQ Framework/docs/test-automation-strategy.md` — **§5 Skill contract**, **§6 Test design standard**
- `docs/parquet-aggregated-data-mapping.md` — dataset definitions (expected SQL comes from here)

**Do not** paste expected SQL for the three named datasets into this skill.  
**Do not** instruct the agent to copy SQL from `data_dev/`.

Finish all template placeholders before use. Run the **Skill review** checklist before using the skill to generate tests.

## When this skill applies

Use this skill explicitly to generate or update dataset-specific Parquet DQ test
modules after the PyTest DQ Framework and its fixtures/library are present.
Generate only one module per requested dataset under
`PyTest DQ Framework/tests/dq checks/parquet_files/`.

Do not use this skill to create or change framework/library code, fixtures,
`conftest.py`, pytest configuration, Jenkins, pipeline code, or mapping files.
If the framework, required fixtures/methods, or mapping is missing, stop and
report the prerequisite instead of fabricating a substitute. If the mapping
does not provide enough information to derive a correct source query, identify
the missing mapping detail and ask for it; do not infer it from another source.

## Inputs you must have

1. Dataset name, matching its folder under `/parquet_data/`.
2. The mapping at `docs/parquet-aggregated-data-mapping.md`, which is the
   exclusive source for output columns, source columns/tables, grain,
   transformations/measures, joins when specified, filters, and partitioning.
3. Author name and requirement/ticket identifier for the test module header.

Read the mapping directly. If it is absent or lacks a join key, transformation,
or other fact required to build the expected query, stop and request the
missing information. Never fill gaps using `data_dev/`, ETL/parquet-loader SQL,
parquet previews, or guessed schema behavior.

## Hard rules

1. Create one file named `test_<dataset_name>.py` in
   `PyTest DQ Framework/tests/dq checks/parquet_files/` for each requested
   dataset. Do not combine datasets.
2. Source/expected data is queried from Postgres using `db_connection`.
   Target/actual data is read from Parquet using `parquet_reader`. Never swap
   these fixtures.
3. Derive expected SQL exclusively from the mapping. Do not read or copy SQL
   from `data_dev/`, parquet-loader code, or previews. Never rewrite or adjust
   expected SQL merely to make a test pass; report discrepancies as mapping vs
   pipeline defects.
4. Do not add `UNION`, extra `WHERE` clauses, `CASE`, sign changes, or other
   transformations unless the mapping explicitly specifies them. Do not guess
   missing joins or transformation details.
5. Keep `source_data` output aliases and grain identical to the mapped Parquet
   schema. Use only mapped output columns in the target-shaped expected result.
6. Read the target at `/parquet_data/<dataset_name>` with
   `include_subfolders=True`, including partition subfolders.
7. Every test has `@pytest.mark.parquet_data` and a dataset-specific marker
   `@pytest.mark.<dataset_name>`. Only the not-empty smoke test also has
   `@pytest.mark.smoke`.
8. Include a smoke/non-empty check, data-completeness check, row-count check,
   uniqueness check, and not-null check. The not-null column list must contain
   every mapped output column for the dataset.
9. Use the existing `data_quality_library` fixture and its
   `DataQualityLibrary` checks. Do not reimplement these checks, compare target
   data to itself, or add empty/always-pass assertions.
10. Do not edit framework code or any file outside the allowed dataset test
    module(s), unless the user separately requests that work.

## Workflow

1. Confirm the framework fixtures and methods exist. Read the requested
   dataset's complete mapping entry in
   `docs/parquet-aggregated-data-mapping.md`; do not consult `data_dev/`.
2. Record every mapped target column, its source, grouping/grain, measure or
   transformation, applicable filter, and partition rule. Determine the join
   path only from mapping information. If any required query detail is absent,
   stop and request clarification.
3. Derive a Postgres `source_query` that returns one row per mapped grain,
   applies only mapped transformations and filters, and aliases every selected
   expression to its target column name. Do not try to reproduce the ETL SQL.
4. Create `test_<dataset_name>.py` in
   `PyTest DQ Framework/tests/dq checks/parquet_files/`. Use `db_connection`
   for `source_data`, `parquet_reader` for `target_data`, and the full skeleton
   below. Replace placeholders with the requested dataset's mapping-derived
   information, author, and requirement ID.
5. Add the `parquet_data` and dataset-specific marker to every check. Add
   `smoke` only to `test_check_dataset_is_not_empty`. Include all five
   mandatory check types and list all mapped output columns in the not-null
   check.
6. Keep `check_data_completeness` as the required source-to-target comparison.
   The framework's `check_data_full_data_set` is an equivalent alias for that
   comparison; the skeleton includes it as a separate named check for callers
   that require that API. Do not substitute it for or omit the required
   completeness test.

## Template

Use this complete module skeleton for each dataset. Replace only placeholders;
keep the source/target direction and fixtures as shown. The additional
full-data-set check calls the framework alias described above.

```python
"""
Description: Data Quality checks for <dataset_name> dataset.
Requirement(s): <requirement_id>
Author(s): <author_name>
"""

import pytest


@pytest.fixture(scope='module')
def source_data(db_connection):
    source_query = """
    -- expected query derived from mapping (grain + measures + joins)
    """
    return db_connection.get_data_sql(source_query)


@pytest.fixture(scope='module')
def target_data(parquet_reader):
    target_path = '/parquet_data/<dataset_name>'
    return parquet_reader.process(target_path, include_subfolders=True)


@pytest.mark.parquet_data
@pytest.mark.smoke
@pytest.mark.<dataset_name>
def test_check_dataset_is_not_empty(target_data, data_quality_library):
    data_quality_library.check_dataset_is_not_empty(target_data)


@pytest.mark.parquet_data
@pytest.mark.<dataset_name>
def test_check_data_completeness(source_data, target_data, data_quality_library):
    data_quality_library.check_data_completeness(source_data, target_data)


@pytest.mark.parquet_data
@pytest.mark.<dataset_name>
def test_check_data_full_data_set(source_data, target_data, data_quality_library):
    data_quality_library.check_data_full_data_set(source_data, target_data)


@pytest.mark.parquet_data
@pytest.mark.<dataset_name>
def test_check_count(source_data, target_data, data_quality_library):
    data_quality_library.check_count(source_data, target_data)


@pytest.mark.parquet_data
@pytest.mark.<dataset_name>
def test_check_uniqueness(target_data, data_quality_library):
    data_quality_library.check_duplicates(target_data)


@pytest.mark.parquet_data
@pytest.mark.<dataset_name>
def test_check_not_null_values(target_data, data_quality_library):
    data_quality_library.check_not_null_values(target_data, ['<col_1>', '<col_2>', '<col_3>'])
```

## SQL derivation (generic)

Derive the expected query from the requested dataset's mapping entry only:

- Use the source tables and source columns named by the mapping. Join tables
  only along an explicitly supplied mapping join path/key; if it is not
  specified, stop for clarification rather than guessing.
- Select dimensions at the mapping's stated grain and group by those dimensions
  when measures are aggregated. The expected result must have one row per
  mapped grain.
- Apply each mapped measure and transformation exactly, including any stated
  rounding or name-format rule. Do not add unlisted calculations.
- Alias each selected expression to the exact mapped target-column name.
- Apply only explicit mapping filters. Respect date granularity, partition
  rules, and any omitted date components as described by the mapping; do not
  invent additional filtering or partition predicates.
- Use standard, readable SQL that returns the columns and row shape needed for
  direct comparison to Parquet. Do not place concrete dataset SQL in this
  skill.

## After generation

Do not run the generated tests unless the user asks. If asked to run them, use
the project's documented pytest invocation and report failures accurately.
Never edit mapping-derived expected SQL simply to get a green run. Preserve the
failure evidence and report the dataset, failed check, mapping expectation, and
observed discrepancy so the transformation can be investigated.

---

## Skill review (self-check before Step 3)

Reject your own skill if any of these are true:

- [ ] Contains concrete expected SQL for `facility_name_min_time_spent_per_visit_date`, `facility_type_avg_time_spent_per_visit_date`, or `patient_sum_treatment_cost_per_facility_type`
- [ ] Tells the agent to use `data_dev/` or parquet loader SQL
- [ ] Omits completeness, count, uniqueness, or not-null
- [ ] Swaps Postgres vs Parquet fixtures or generates trivial always-pass checks
- [ ] Any section still contains an unfinished placeholder
