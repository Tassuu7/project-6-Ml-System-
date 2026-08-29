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

    if not columns:
        if t_type in ("StandardScaler", "MinMaxScaler", "RobustScaler", "MaxAbsScaler", "QuantileTransformer", "PowerTransformer", "VectorNormalizer", "ZScoreOutlierDetector", "IQROutlierRemover", "GaussianNoiseInjector"):
            columns = df.numeric_columns()
        elif t_type in ("OneHotEncoder", "OrdinalEncoder", "FrequencyEncoder", "BinaryEncoder"):
            columns = df.categorical_columns()
        else:
            columns = df.columns

    try:
        transformer = TransformerRegistry.create(t_type, columns=columns, **params)
        transformed = transformer.fit_transform(df)
        return 200, {
            "transformed_columns": transformed.columns,
            "preview": transformed.head(100).to_dict_records(),
            "shape": list(transformed.shape),
            "fitted_params": transformer.get_params()
        }
    except Exception as e:
        return 400, {"error": f"Transformation failed: {e}"}
