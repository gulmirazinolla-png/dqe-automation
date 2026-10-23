from pathlib import Path

import pandas as pd


class ParquetReader:
    def process(self, path, include_subfolders=True):
        parquet_path = Path(path)
        if not parquet_path.exists():
            raise FileNotFoundError(f"Parquet path does not exist: {parquet_path}")

        if parquet_path.is_file():
            return pd.read_parquet(parquet_path)

        search = parquet_path.rglob("*") if include_subfolders else parquet_path.glob("*")
        parquet_files = [
            file
            for file in search
            if file.is_file() and file.suffix.lower() in {".parquet", ".pq"}
        ]
        if not parquet_files:
            raise FileNotFoundError(f"No Parquet files found under: {parquet_path}")

        if include_subfolders:
            # Read the directory as a dataset to preserve partition columns.
            return pd.read_parquet(parquet_path)

        return pd.concat(
            [pd.read_parquet(file) for file in parquet_files],
            ignore_index=True,
        )
