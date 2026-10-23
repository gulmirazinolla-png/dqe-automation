# Defect Summary

| Dataset | Check | Expected (from mapping/Postgres) | Actual (parquet) | Likely cause |
|---|---|---|---|---|
| facility_type_avg_time_spent_per_visit_date | count | 35,489 rows | 25,809 rows | 9,680 rows lost in transformation |
| facility_type_avg_time_spent_per_visit_date | completeness | 0 source rows missing | 9,680 source rows missing from target, 0 extra | source rows from early visit dates (starting 2000-01-01) absent from parquet |
| facility_type_avg_time_spent_per_visit_date | full_data_set | 0 source rows missing | 9,680 source rows missing from target, 0 extra | same as above |
| facility_name_min_time_spent_per_visit_date | count | 35,489 rows | 44,378 rows | 8,889 extra rows in target |
| facility_name_min_time_spent_per_visit_date | completeness | no extra target rows | 8,889 target rows not in source | duplicated rows in target |
| facility_name_min_time_spent_per_visit_date | full_data_set | no extra target rows | 8,889 target rows not in source | duplicated rows in target |
| facility_name_min_time_spent_per_visit_date | uniqueness | 0 duplicate keys | 17,778 rows failed | 8,889 duplicate keys, each appearing twice in target |
| patient_sum_treatment_cost_per_facility_type | count | 120 rows | 64 rows | 56 rows lost in transformation |
| patient_sum_treatment_cost_per_facility_type | completeness | all source rows present | 75 source rows missing, 19 target rows not in source | sum_treatment_cost negated (wrong sign) for some patients, plus lost rows |
| patient_sum_treatment_cost_per_facility_type | full_data_set | all source rows present | 75 source rows missing, 19 target rows not in source | same as above |
| patient_sum_treatment_cost_per_facility_type | not-null | 0 NULLs | 4 rows with NULL full_name (one per facility type, values about ±26M) | facility-type-level totals with the patient name lost in transformation |