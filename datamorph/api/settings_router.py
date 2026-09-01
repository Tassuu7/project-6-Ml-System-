"""
DataMorph Studio - Settings & Configuration API Router
Stores and manages user profile, appearance theme, quality thresholds, and drift thresholds.
"""

from typing import Dict, List, Any

DEFAULT_SETTINGS = {
    "profile": {
        "full_name": "Shaik Tasleema Sadiya",
        "username": "admin",
        "email": "shaiktasleemasadiya7@gmail.com",
        "role": "Lead ML Engineer & Data Architect",
        "initials": "ST"
    },
    "appearance": {
        "theme": "dark",
        "sidebar_collapsed": False,
        "density": "comfortable",
        "font_size": "medium"
    },
    "pipeline": {
        "default_execution_mode": "sequential",
        "auto_validate_schemas": True,
        "max_preview_rows": 200,
        "timeout_seconds": 60
    },
    "quality_thresholds": {
        "missing_value_warn_pct": 5.0,
        "missing_value_critical_pct": 20.0,
        "duplicate_warn_pct": 2.0,
        "outlier_iqr_multiplier": 1.5
    },
    "drift_thresholds": {
        "psi_stable_cutoff": 0.1,
        "psi_warning_cutoff": 0.2,
        "psi_critical_cutoff": 0.25,
        "ks_alpha_significance": 0.05
    }
}

def handle_get_settings(db) -> tuple:
    """Returns current user settings or default settings."""
    settings = db.get("system", "settings")
    if not settings:
        settings = DEFAULT_SETTINGS
    return 200, {"status": "success", "settings": settings}

def handle_update_settings(db, body: dict) -> tuple:
    """Updates user and application settings."""
    current = db.get("system", "settings") or dict(DEFAULT_SETTINGS)
    
    for section, vals in body.items():
        if section in current and isinstance(vals, dict):
            current[section].update(vals)
        else:
            current[section] = vals
            
    db.set("system", "settings", current)
    return 200, {"status": "success", "settings": current}
