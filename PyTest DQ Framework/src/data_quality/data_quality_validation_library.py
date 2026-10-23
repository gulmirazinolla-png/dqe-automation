import pandas as pd


class DataQualityLibrary:
    """Validation checks for pandas DataFrames."""

    @staticmethod
    def _check_columns(df, column_names):
        missing_columns = [column for column in column_names if column not in df.columns]
        if missing_columns:
            raise ValueError(f"Columns not found in DataFrame: {missing_columns}")

    @staticmethod
    def _result(check_name, failed_rows):
        sample = failed_rows.head(5).to_dict(orient="records")
        message = (
            f"{check_name}: {len(failed_rows)} rows failed. "
            f"Sample rows: {sample}"
        )
        assert failed_rows.empty, message
        return message

    @staticmethod
    def check_count(source, target):
        source_count = len(source)
        target_count = len(target)
        difference = abs(source_count - target_count)
        message = (
            f"Row count check failed: source has {source_count} rows, "
            f"target has {target_count} rows ({difference} row difference). "
            f"Source sample: {source.head(5).to_dict(orient='records')}; "
            f"target sample: {target.head(5).to_dict(orient='records')}"
        )
        assert source_count == target_count, message
        return f"Row count check passed: both DataFrames have {source_count} rows."

    @staticmethod
    def check_duplicates(df, column_names=None):
        columns = list(column_names) if column_names is not None else list(df.columns)
        DataQualityLibrary._check_columns(df, columns)
        duplicate_rows = df[df.duplicated(subset=columns, keep=False)]
        return DataQualityLibrary._result("Duplicate check", duplicate_rows)

    @staticmethod
    def check_not_null_values(df, column_names=None):
        columns = list(column_names) if column_names is not None else list(df.columns)
        DataQualityLibrary._check_columns(df, columns)
        null_rows = df[df[columns].isna().any(axis=1)]
        return DataQualityLibrary._result("Not-null check", null_rows)

    @staticmethod
    def check_data_completeness(source, target):
        source_columns = list(source.columns)
        if len(source_columns) != len(target.columns) or set(source_columns) != set(target.columns):
            raise ValueError(
                "Completeness check requires source and target to have the same columns."
            )

        target = target[source_columns]
        occurrence_column = "__dq_occurrence"
        while occurrence_column in source_columns:
            occurrence_column += "_"
        indicator_column = "__dq_merge_status"
        while indicator_column in source_columns or indicator_column == occurrence_column:
            indicator_column += "_"

        # Match duplicate rows by occurrence so excess copies count as missing.
        if source_columns:
            source_occurrences = source.groupby(
                source_columns, dropna=False, sort=False
            ).cumcount()
            target_occurrences = target.groupby(
                source_columns, dropna=False, sort=False
            ).cumcount()
        else:
            source_occurrences = pd.Series(range(len(source)), index=source.index)
            target_occurrences = pd.Series(range(len(target)), index=target.index)

        source_rows = source.copy()
        source_rows[occurrence_column] = source_occurrences.to_numpy()
        target_rows = target.copy()
        target_rows[occurrence_column] = target_occurrences.to_numpy()

        comparison = source_rows.merge(
            target_rows,
            on=source_columns + [occurrence_column],
            how="outer",
            indicator=indicator_column,
            sort=False,
        )
        source_missing = comparison.loc[
            comparison[indicator_column] == "left_only", source_columns
        ]
        target_missing = comparison.loc[
            comparison[indicator_column] == "right_only", source_columns
        ]

        message = (
            "Data completeness check failed: "
            f"{len(source_missing)} source rows missing from target; "
            f"{len(target_missing)} target rows missing from source. "
            f"Source-only samples: {source_missing.head(5).to_dict(orient='records')}; "
            f"target-only samples: {target_missing.head(5).to_dict(orient='records')}"
        )
        assert source_missing.empty and target_missing.empty, message
        return (
            "Data completeness check passed: source and target contain the same rows."
        )

    @staticmethod
    def check_data_full_data_set(source, target):
        return DataQualityLibrary.check_data_completeness(source, target)

    @staticmethod
    def check_dataset_is_not_empty(df):
        message = (
            f"Dataset is empty: {len(df)} rows found. "
            f"Sample rows: {df.head(5).to_dict(orient='records')}"
        )
        assert not df.empty, message
        return f"Dataset is not empty: {len(df)} rows found."
