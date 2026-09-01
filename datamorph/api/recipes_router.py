"""
DataMorph Studio - Recipes API Router
Provides pre-built enterprise domain pipeline templates and user-saved custom recipes.
"""

import time
from typing import Dict, List, Any, Optional

DEFAULT_TEMPLATES = [
    {
        "id": "recipe_churn_prediction",
        "name": "Customer Churn Feature Engineering",
        "category": "Customer Analytics",
        "description": "Standardized preprocessing for churn classification: missing value imputation, robust scaling, and one-hot encoding.",
        "icon": "👥",
        "steps": [
            {"name": "Median Imputer", "type": "SimpleImputer", "params": {"strategy": "median"}, "columns": []},
            {"name": "Standard Scaler", "type": "StandardScaler", "params": {}, "columns": []},
            {"name": "Categorical Encoder", "type": "OneHotEncoder", "params": {}, "columns": []}
        ]
    },
    {
        "id": "recipe_credit_risk",
        "name": "Credit Risk Scoring & Discretization",
        "category": "FinTech & Banking",
        "description": "Quantile discretization, outlier removal via IQR boundaries, and monotonic weight-of-evidence binning.",
        "icon": "💳",
        "steps": [
            {"name": "IQR Outlier Filter", "type": "IQROutlierRemover", "params": {"factor": 1.5}, "columns": []},
            {"name": "Quantile Binner", "type": "EqualFrequencyDiscretizer", "params": {"n_bins": 5}, "columns": []},
            {"name": "MinMax Scaler", "type": "MinMaxScaler", "params": {}, "columns": []}
        ]
    },
    {
        "id": "recipe_fraud_detection",
        "name": "Fraud Detection Feature Pipeline",
        "category": "Cybersecurity & Fraud",
        "description": "Handles extreme transaction skewness using PowerTransformer, Z-Score anomaly filtering, and frequency encoding.",
        "icon": "🛡️",
        "steps": [
            {"name": "Power Transformation", "type": "PowerTransformer", "params": {"method": "box-cox"}, "columns": []},
            {"name": "Z-Score Anomaly Detector", "type": "ZScoreOutlierDetector", "params": {"threshold": 3.0}, "columns": []},
            {"name": "Frequency Encoder", "type": "FrequencyEncoder", "params": {}, "columns": []}
        ]
    },
    {
        "id": "recipe_nlp_text",
        "name": "Text & NLP Tabular Preprocessing",
        "category": "NLP & Unstructured",
        "description": "TF-IDF vectorizer, N-Gram token synthesis, text length extraction, and lower-casing.",
        "icon": "📝",
        "steps": [
            {"name": "Text Normalizer", "type": "TextCleanerTransformer", "params": {}, "columns": []},
            {"name": "TF-IDF Vectorizer", "type": "TfidfFeatureExtractor", "params": {"max_features": 20}, "columns": []}
        ]
    },
    {
        "id": "recipe_timeseries",
        "name": "Time Series Lag & Rolling Statistics",
        "category": "Forecasting & IoT",
        "description": "Extracts temporal cyclical encodings (sin/cos of hour/day), rolling mean windows, and lag features.",
        "icon": "⏱️",
        "steps": [
            {"name": "Cyclical Time Encoder", "type": "CyclicalDateTransformer", "params": {}, "columns": []},
            {"name": "Rolling Window Aggregator", "type": "RollingWindowFeatureExtractor", "params": {"window_size": 7}, "columns": []}
        ]
    },
    {
        "id": "recipe_healthcare_clinical",
        "name": "Clinical Healthcare Data Cleaning",
        "category": "Healthcare & Life Sciences",
        "description": "Handles sparse biomarker records via KNN imputation, clipping physiological bounds, and ordinal lab encoding.",
        "icon": "🏥",
        "steps": [
            {"name": "KNN Missing Imputer", "type": "KNNImputer", "params": {"n_neighbors": 5}, "columns": []},
            {"name": "Robust Scaler", "type": "RobustScaler", "params": {}, "columns": []}
        ]
    },
    {
        "id": "recipe_high_dim_prune",
        "name": "High-Dimensional Feature Pruning",
        "category": "Feature Selection",
        "description": "Variance threshold filtering, pairwise correlation pruning, and recursive feature ranking.",
        "icon": "✂️",
        "steps": [
            {"name": "Variance Threshold Selector", "type": "VarianceThresholdSelector", "params": {"threshold": 0.01}, "columns": []},
            {"name": "Correlation Filter", "type": "CorrelationFilterSelector", "params": {"threshold": 0.85}, "columns": []}
        ]
    }
]

def handle_get_recipes(db) -> tuple:
    """Returns all pre-built templates plus user-saved custom recipes."""
    custom_recipes = db.get_all("recipes")
    custom_list = list(custom_recipes.values()) if isinstance(custom_recipes, dict) else []
    
    return 200, {
        "status": "success",
        "templates": DEFAULT_TEMPLATES,
        "custom_recipes": custom_list,
        "total_recipes": len(DEFAULT_TEMPLATES) + len(custom_list)
    }

def handle_save_recipe(db, body: dict) -> tuple:
    """Saves a new custom recipe definition."""
    name = body.get("name")
    if not name:
        return 400, {"error": "Recipe name is required"}
    
    recipe_id = f"rcp_{int(time.time() * 1000)}"
    recipe = {
        "id": recipe_id,
        "name": name,
        "category": body.get("category", "Custom User Recipes"),
        "description": body.get("description", "User-configured pipeline recipe"),
        "icon": body.get("icon", "⚡"),
        "steps": body.get("steps", []),
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    }
    
    db.set("recipes", recipe_id, recipe)
    return 200, {"status": "success", "recipe": recipe}
