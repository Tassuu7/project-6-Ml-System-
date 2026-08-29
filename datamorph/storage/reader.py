"""
DataMorph Studio - Dataset Ingestion Reader
Parses CSV, JSON, and raw stream tabular formats into DataMorph DataFrame objects.
"""

import csv
import json
import os
from typing import Optional, List, Dict, Any
from datamorph.core.dataframe import DataFrame
from datamorph.core.exceptions import DatasetStorageError


class DatasetReader:
    """Reads structured tabular data from disk into DataFrame instances."""

    @classmethod
    def read_csv(cls, filepath: str, delimiter: str = ",",
                 has_header: bool = True, max_rows: Optional[int] = None) -> DataFrame:
        if not os.path.exists(filepath):
            raise DatasetStorageError(f"File not found: {filepath}", filepath=filepath)

        try:
            with open(filepath, "r", encoding="utf-8-sig", errors="replace") as f:
                reader = csv.reader(f, delimiter=delimiter)
                rows = []
                for idx, r in enumerate(reader):
                    if max_rows and idx > max_rows:
                        break
                    rows.append(r)

            if not rows:
                return DataFrame()

            if has_header:
                headers = [h.strip() for h in rows[0]]
                data_rows = rows[1:]
            else:
                headers = [f"col_{i}" for i in range(len(rows[0]))]
                data_rows = rows

            # Pivot to column dictionary
            col_data: Dict[str, List[Any]] = {h: [] for h in headers}
            for row in data_rows:
                for idx, h in enumerate(headers):
                    val = row[idx].strip() if idx < len(row) else None
                    if val == "" or val == "NA" or val == "null" or val == "None" or val == "NaN":
                        col_data[h].append(None)
                    else:
                        # Try parsing numeric
                        try:
                            if "." in val or "e" in val.lower():
                                col_data[h].append(float(val))
                            else:
                                col_data[h].append(int(val))
                        except ValueError:
                            col_data[h].append(val)

            df = DataFrame()
            for h in headers:
                df.add_column(h, col_data[h])
            return df

        except Exception as e:
            raise DatasetStorageError(f"Error parsing CSV '{filepath}': {e}", filepath=filepath)

    @classmethod
    def read_json(cls, filepath: str) -> DataFrame:
        if not os.path.exists(filepath):
            raise DatasetStorageError(f"File not found: {filepath}", filepath=filepath)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return DataFrame(data)
            elif isinstance(data, dict) and "records" in data:
                return DataFrame(data["records"])
            else:
                return DataFrame([data])
        except Exception as e:
            raise DatasetStorageError(f"Error parsing JSON '{filepath}': {e}", filepath=filepath)
