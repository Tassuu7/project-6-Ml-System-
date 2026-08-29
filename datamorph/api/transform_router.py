"""
DataMorph Studio - Real-time Interactive Transformer Preview Router
Applies quick single-step transformations on dataset columns for interactive UI preview.
"""

from datamorph.pipeline.registry import TransformerRegistry
from datamorph.api.dataset_router import ACTIVE_DATASETS


def handle_transform_preview(body: dict) -> tuple:
    dataset_id = body.get("dataset_id")
    t_type = body.get("transformer_type")
    columns = body.get("columns", [])
    params = body.get("params", {})

    df = ACTIVE_DATASETS.get(dataset_id)
    if df is None:
        return 404, {"error": "Dataset not found in memory"}

    try:
        transformer = TransformerRegistry.create(t_type, columns=columns, **params)
        transformed = transformer.fit_transform(df)
        return 200, {
            "transformed_columns": transformed.columns,
            "preview": transformed.head(15).to_dict_records(),
            "shape": list(transformed.shape),
            "fitted_params": transformer.get_params()
        }
    except Exception as e:
        return 400, {"error": f"Transformation failed: {e}"}
