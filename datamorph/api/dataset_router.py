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

from datamorph.monitoring.recommendations_engine import RecommendationsEngine
from datamorph.storage.version_manager import DatasetVersionManager
from datamorph.api.activity_router import log_system_activity

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
    
    # Log system activity
    log_system_activity(
        db,
        action_type="dataset_upload",
        title=f"Dataset Ingested: {filename}",
        details=f"Uploaded {len(df)} records across {len(df.columns)} features (Quality Score: {quality['quality_score']}%).",
        metadata={"dataset_id": dataset_id, "rows": len(df), "columns": len(df.columns)},
        level="success"
    )
    
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
    
    # Calculate smart recommendations
    recs = RecommendationsEngine.generate_recommendations(df) if df is not None else []
    
    return 200, {
        "metadata": meta,
        "profile": profile,
        "recommendations": recs,
        "preview": df.head(200).to_dict_records() if df else []
    }


def handle_get_recommendations(db, dataset_id: str) -> tuple:
    df = ACTIVE_DATASETS.get(dataset_id)
    if df is None:
        meta = db.get("datasets", dataset_id)
        if meta and os.path.exists(meta.get("filepath", "")):
            df = DatasetReader.read_csv(meta["filepath"])
            ACTIVE_DATASETS[dataset_id] = df
        else:
            return 404, {"error": f"Dataset '{dataset_id}' not found"}
            
    recs = RecommendationsEngine.generate_recommendations(df)
    return 200, {"status": "success", "dataset_id": dataset_id, "recommendations": recs}


def handle_get_versions(db, dataset_id: str) -> tuple:
    meta = db.get("datasets", dataset_id)
    if not meta:
        return 404, {"error": f"Dataset '{dataset_id}' not found"}
        
    df = ACTIVE_DATASETS.get(dataset_id)
    if df is None and os.path.exists(meta["filepath"]):
        df = DatasetReader.read_csv(meta["filepath"])
        ACTIVE_DATASETS[dataset_id] = df

    # Build version lineage
    versions = [
        {"version": "v1.0", "label": "Initial Ingestion", "timestamp": "2026-08-31 09:00:00", "rows": meta.get("rows", 0), "columns": len(meta.get("columns", [])), "is_current": True}
    ]
    
    # Check if transformed version exists
    trans_id = f"ds_trans_{dataset_id}"
    trans_df = ACTIVE_DATASETS.get(trans_id)
    if trans_df is not None:
        diff = DatasetVersionManager.compute_schema_diff(df, trans_df)
        versions.append({
            "version": "v2.0",
            "label": "Pipeline Processed",
            "timestamp": "2026-08-31 10:30:00",
            "rows": trans_df.shape[0],
            "columns": trans_df.shape[1],
            "is_current": True,
            "diff": diff
        })
        versions[0]["is_current"] = False
        
    return 200, {"status": "success", "dataset_id": dataset_id, "versions": versions}

