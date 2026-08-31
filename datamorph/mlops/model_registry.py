"""
DataMorph Studio - Production Model & Transformer Registry
Manages versioned model artifacts, stage transitions (Staging/Production/Archived),
signature validation, and immutable execution metadata.
"""

import time
import json
from typing import Dict, List, Any, Optional


class ModelArtifact:
    """Represents a versioned deployment artifact with signature and metrics."""
    def __init__(self, model_id: str, name: str, version: str, stage: str = "Staging",
                 parameters: Optional[Dict[str, Any]] = None, metrics: Optional[Dict[str, float]] = None):
        self.model_id = model_id
        self.name = name
        self.version = version
        self.stage = stage  # 'Development', 'Staging', 'Production', 'Archived'
        self.parameters = parameters or {}
        self.metrics = metrics or {}
        self.created_at = time.time()
        self.transition_history: List[Dict[str, Any]] = [{
            "from_stage": None, "to_stage": stage, "timestamp": self.created_at, "comment": "Initial registration"
        }]

    def transition_to(self, new_stage: str, comment: str = ""):
        valid_stages = {"Development", "Staging", "Production", "Archived"}
        if new_stage not in valid_stages:
            raise ValueError(f"Invalid stage '{new_stage}'. Must be one of {valid_stages}")
        self.transition_history.append({
            "from_stage": self.stage,
            "to_stage": new_stage,
            "timestamp": time.time(),
            "comment": comment
        })
        self.stage = new_stage

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "name": self.name,
            "version": self.version,
            "stage": self.stage,
            "parameters": self.parameters,
            "metrics": self.metrics,
            "created_at": self.created_at,
            "transition_history": self.transition_history
        }


class ModelRegistry:
    """Enterprise MLOps Model Registry maintaining catalog lifecycle."""
    def __init__(self):
        self._artifacts: Dict[str, Dict[str, ModelArtifact]] = {}

    def register_model(self, name: str, version: str, parameters: Optional[Dict[str, Any]] = None,
                       metrics: Optional[Dict[str, float]] = None) -> ModelArtifact:
        model_id = f"{name}_v{version}_{int(time.time())}"
        artifact = ModelArtifact(model_id, name, version, parameters=parameters, metrics=metrics)
        self._artifacts.setdefault(name, {})[version] = artifact
        return artifact

    def get_production_model(self, name: str) -> Optional[ModelArtifact]:
        versions = self._artifacts.get(name, {})
        for art in versions.values():
            if art.stage == "Production":
                return art
        return None

    def list_all_models(self) -> List[Dict[str, Any]]:
        result = []
        for name, vers in self._artifacts.items():
            for ver, art in vers.items():
                result.append(art.to_dict())
        return result
