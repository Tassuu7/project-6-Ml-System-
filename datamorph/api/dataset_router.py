"""
DataMorph Studio - Dataset API Router
Handles dataset upload, inspection, schema extraction, profiling, and quality scoring.
"""

import os
import uuid
from datamorph.storage.reader import DatasetReader
from datamorph.storage.writer import DatasetWriter
from datamorph.monitoring.quality_audit import DataQualityAuditor
from datamorph.monitoring.profiler import DatasetProfiler

ACTIVE_DATASETS = {}


def handle_upload(db, filename: str, content_str: str) -> tuple:
    dataset_id = f"ds_{uuid.uuid4().hex[:8]}"
    upload_path = os.path.join("data", "uploads", f"{dataset_id}_{filename}")
    os.makedirs(os.path.dirname(upload_path), exist_ok=True)

    with open(upload_path, "w", encoding="utf-8") as f:
        f.write(content_str)

    df = DatasetReader.read_csv(upload_path)
    ACTIVE_DATASETS[dataset_id] = df

    auditor = DataQualityAuditor()
    quality = auditor.audit(df)

    metadata = {
        "dataset_id": dataset_id,
        "name": filename,
        "filepath": upload_path,
        "rows": len(df),
        "columns": df.columns,
        "numeric_columns": df.numeric_columns(),
        "categorical_columns": df.categorical_columns(),
        "quality_score": quality["quality_score"],
        "grade": quality["grade"],
    }
    db.set("datasets", dataset_id, metadata)
    return 200, {"dataset": metadata, "preview": df.head(200).to_dict_records()}


def handle_get_dataset(db, dataset_id: str) -> tuple:
    meta = db.get("datasets", dataset_id)
    if not meta:
        return 404, {"error": f"Dataset '{dataset_id}' not found"}

    df = ACTIVE_DATASETS.get(dataset_id)
    if df is None and os.path.exists(meta["filepath"]):
        df = DatasetReader.read_csv(meta["filepath"])
        ACTIVE_DATASETS[dataset_id] = df

    profiler = DatasetProfiler()
    profile = profiler.profile(df) if df is not None else {}
    return 200, {"metadata": meta, "profile": profile, "preview": df.head(200).to_dict_records() if df else []}
