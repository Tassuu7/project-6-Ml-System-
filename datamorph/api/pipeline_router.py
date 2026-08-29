"""
DataMorph Studio - Pipeline API Router
Handles DAG creation, step configuration, step execution, and compilation.
"""

from datamorph.pipeline.dag import PipelineDAG
from datamorph.pipeline.step import PipelineStep
from datamorph.pipeline.runner import PipelineRunner
from datamorph.pipeline.registry import TransformerRegistry
from datamorph.pipeline.compiler import PipelineCompiler
from datamorph.api.dataset_router import ACTIVE_DATASETS


def handle_execute_pipeline(db, body: dict) -> tuple:
    dataset_id = body.get("dataset_id")
    steps_config = body.get("steps", [])
    df = ACTIVE_DATASETS.get(dataset_id)

    if df is None:
        meta = db.get("datasets", dataset_id)
        if meta and os.path.exists(meta.get("filepath", "")):
            from datamorph.storage.reader import DatasetReader
            df = DatasetReader.read_csv(meta["filepath"])
            ACTIVE_DATASETS[dataset_id] = df
        else:
            return 404, {"error": "Dataset not found"}

    dag = PipelineDAG(name="ActivePreprocessingDAG")
    for s_conf in steps_config:
        t_type = s_conf.get("type")
        cols = s_conf.get("columns", [])
        if not cols:
            if t_type in ("StandardScaler", "MinMaxScaler", "RobustScaler", "MaxAbsScaler", "QuantileTransformer", "PowerTransformer", "VectorNormalizer", "ZScoreOutlierDetector", "IQROutlierRemover"):
                cols = df.numeric_columns()
            elif t_type in ("OneHotEncoder", "OrdinalEncoder", "FrequencyEncoder", "BinaryEncoder"):
                cols = df.categorical_columns()
            else:
                cols = df.columns
        params = s_conf.get("params", {})
        transformer = TransformerRegistry.create(t_type, columns=cols, **params)
        step = PipelineStep(name=s_conf.get("name", t_type), transformer=transformer, depends_on=s_conf.get("depends_on", []))
        dag.add_step(step)

    runner = PipelineRunner()
    try:
        transformed_df = runner.run(dag, df)
        transformed_id = f"ds_trans_{dataset_id}"
        ACTIVE_DATASETS[transformed_id] = transformed_df

        python_code = PipelineCompiler.to_python_script(dag)
        return 200, {
            "status": "success",
            "transformed_dataset_id": transformed_id,
            "shape": list(transformed_df.shape),
            "preview": transformed_df.head(200).to_dict_records(),
            "python_code": python_code,
            "dag": dag.to_dict()
        }
    except Exception as e:
        return 500, {"error": str(e)}
