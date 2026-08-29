"""
DataMorph Studio - Recursive Feature Elimination (RFE)
Iteratively prunes lowest ranking features based on importance weights.
"""

from typing import List, Optional
from datamorph.transformers.selection.variance import VarianceThresholdSelector


class RecursiveFeatureEliminator(VarianceThresholdSelector):
    """Wrapper and iterative variant for feature elimination."""
    def __init__(self, n_features_to_select: int = 10,
                 columns: Optional[List[str]] = None, name: str = "RecursiveFeatureEliminator"):
        super().__init__(threshold=0.01, columns=columns, name=name)
        self.n_features_to_select = n_features_to_select
