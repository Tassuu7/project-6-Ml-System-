# DataMorph Studio - REST API Specification

Detailed HTTP REST API contract for DataMorph Studio v2.4.0.

---

## Endpoints Overview

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/health` | Healthcheck and server version info |
| `GET` | `/api/transformers` | List all registered transformer types |
| `GET` | `/api/datasets` | List all ingested datasets |
| `GET` | `/api/datasets?id={id}` | Ingested dataset profile and sample records |
| `POST` | `/api/auth/login` | User authentication & signed token generation |
| `POST` | `/api/datasets/upload` | Ingest CSV or JSON tabular datasets |
| `POST` | `/api/pipeline/execute` | Execute complete DAG preprocessing pipeline |
| `POST` | `/api/transform/preview` | Real-time live single-transformer preview |
| `POST` | `/api/monitoring/drift` | Statistical drift (PSI & KS test) calculation |
| `POST` | `/api/export` | Export processed dataset as CSV or JSON |

---

## Sample Request: Execute Pipeline
```json
POST /api/pipeline/execute
Content-Type: application/json

{
  "dataset_id": "ds_4a1b2c3d",
  "steps": [
    {
      "name": "ImputeMissingAges",
      "type": "SimpleImputer",
      "columns": ["age"],
      "params": {"strategy": "median"}
    },
    {
      "name": "ScaleSalaries",
      "type": "StandardScaler",
      "columns": ["annual_income", "credit_score"],
      "params": {"with_mean": true, "with_std": true}
    },
    {
      "name": "EncodeCountries",
      "type": "OneHotEncoder",
      "columns": ["country"],
      "params": {"drop_first": true}
    }
  ]
}
```

## Sample Response: Execute Pipeline
```json
{
  "status": "success",
  "transformed_dataset_id": "ds_trans_ds_4a1b2c3d",
  "shape": [250, 8],
  "preview": [
    {
      "customer_id": 1001,
      "age": 34,
      "annual_income": 0.421,
      "credit_score": 0.812,
      "churn": 0,
      "country_France": 0,
      "country_Germany": 0,
      "country_USA": 1
    }
  ],
  "python_code": "...",
  "dag": {
    "pipeline_id": "ActivePreprocessingDAG",
    "step_count": 3
  }
}
```
