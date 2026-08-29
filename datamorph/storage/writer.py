"""
DataMorph Studio - Dataset Export Writer
Exports processed DataFrame matrices into CSV, JSON records, and Parquet metadata.
"""

import csv
import json
import os
from typing import Optional
from datamorph.core.dataframe import DataFrame
from datamorph.core.exceptions import DatasetStorageError


class DatasetWriter:
    """Exports DataFrame objects into persistent storage files."""

    @classmethod
    def write_csv(cls, df: DataFrame, filepath: str, delimiter: str = ",") -> str:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
            records = df.to_dict_records()
            cols = df.columns

            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=cols, delimiter=delimiter)
                writer.writeheader()
                for r in records:
                    # Clean None values for CSV output
                    clean_row = {k: ("" if v is None else v) for k, v in r.items()}
                    writer.writerow(clean_row)

            return filepath
        except Exception as e:
            raise DatasetStorageError(f"Failed writing CSV to '{filepath}': {e}", filepath=filepath)

    @classmethod
    def write_json(cls, df: DataFrame, filepath: str) -> str:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
            records = df.to_dict_records()
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump({"records": records, "shape": list(df.shape)}, f, indent=2)
            return filepath
        except Exception as e:
            raise DatasetStorageError(f"Failed writing JSON to '{filepath}': {e}", filepath=filepath)
