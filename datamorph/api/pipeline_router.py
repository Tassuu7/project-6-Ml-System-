import time
import os
from datamorph.pipeline.dag import PipelineDAG
from datamorph.pipeline.step import PipelineStep
from datamorph.pipeline.runner import PipelineRunner
from datamorph.pipeline.registry import TransformerRegistry
from datamorph.pipeline.compiler import PipelineCompiler
from datamorph.api.dataset_router import ACTIVE_DATASETS
from datamorph.api.runs_router import record_pipeline_run
from datamorph.api.activity_router import log_system_activity


def handle_execute_pipeline(db, body: dict) -> tuple:
    dataset_id = body.get("dataset_id")
    steps_config = body.get("steps", [])
    pipeline_name = body.get("name", "ActivePreprocessingDAG")
    df = ACTIVE_DATASETS.get(dataset_id)

    if df is None:
        meta = db.get("datasets", dataset_id)
        if meta and os.path.exists(meta.get("filepath", "")):
            from datamorph.storage.reader import DatasetReader
            df = DatasetReader.read_csv(meta["filepath"])
            ACTIVE_DATASETS[dataset_id] = df
        else:
            return 404, {"error": "Dataset not found"}

    start_time = time.time()
    dag = PipelineDAG(name=pipeline_name)
    step_records = []

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
        step_name = s_conf.get("name", t_type)
        step = PipelineStep(name=step_name, transformer=transformer, depends_on=s_conf.get("depends_on", []))
        dag.add_step(step)
        step_records.append({"name": step_name, "type": t_type, "columns": cols, "params": params})

    runner = PipelineRunner()
    try:
        rows_in, cols_in = df.shape
        transformed_df = runner.run(dag, df)
        rows_out, cols_out = transformed_df.shape
        duration_ms = round((time.time() - start_time) * 1000.0, 2)

        transformed_id = f"ds_trans_{dataset_id}"
        ACTIVE_DATASETS[transformed_id] = transformed_df

        python_code = PipelineCompiler.to_python_script(dag)

        # Record Execution Run
        run_record = {
            "pipeline_name": pipeline_name,
            "dataset_id": dataset_id,
            "user": "admin",
            "status": "completed",
            "duration_ms": duration_ms,
            "rows_in": rows_in,
            "rows_out": rows_out,
            "cols_in": cols_in,
            "cols_out": cols_out,
            "steps": step_records,
            "total_steps": len(steps_config)
        }
        run_id = record_pipeline_run(db, run_record)

        # Log Activity
        log_system_activity(
            db,
            action_type="pipeline_execution",
            title=f"Pipeline Executed: {pipeline_name}",
            details=f"Processed {rows_out} rows across {len(steps_config)} transformer steps in {duration_ms}ms.",
            metadata={"run_id": run_id, "dataset_id": dataset_id, "duration_ms": duration_ms},
            level="success"
        )

        return 200, {
            "status": "success",
            "run_id": run_id,
            "duration_ms": duration_ms,
            "transformed_dataset_id": transformed_id,
            "shape": list(transformed_df.shape),
            "preview": transformed_df.head(200).to_dict_records(),
            "python_code": python_code,
            "dag": dag.to_dict(),
            "steps_executed": step_records
        }
    except Exception as e:
        duration_ms = round((time.time() - start_time) * 1000.0, 2)
        # Record Failed Run
        run_record = {
            "pipeline_name": pipeline_name,
            "dataset_id": dataset_id,
            "user": "admin",
            "status": "failed",
            "error": str(e),
            "duration_ms": duration_ms,
            "steps": step_records,
            "total_steps": len(steps_config)
        }
        record_pipeline_run(db, run_record)
        log_system_activity(
            db,
            action_type="pipeline_failed",
            title=f"Pipeline Failed: {pipeline_name}",
            details=f"Execution failed: {str(e)}",
            level="error"
        )
        return 500, {"error": str(e), "duration_ms": duration_ms}

