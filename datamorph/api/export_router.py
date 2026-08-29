"""
DataMorph Studio - Export & Recipe Packaging Router
Exports cleaned CSVs, JSON data recipes, and Python deployment scripts.
"""

import os
from datamorph.storage.writer import DatasetWriter
from datamorph.api.dataset_router import ACTIVE_DATASETS


def handle_export(body: dict) -> tuple:
    dataset_id = body.get("dataset_id")
    export_format = body.get("format", "csv").lower()

    df = ACTIVE_DATASETS.get(dataset_id)
    if df is None:
        return 404, {"error": "Dataset not found"}

    export_path = os.path.join("data", "exports", f"{dataset_id}_export.{export_format}")
    if export_format == "json":
        DatasetWriter.write_json(df, export_path)
    else:
        DatasetWriter.write_csv(df, export_path)

    return 200, {
        "export_url": f"/api/exports/download?file={os.path.basename(export_path)}",
        "filepath": export_path,
        "rows": len(df),
        "columns": df.columns
    }
