"""
DataMorph Studio - Iterative Imputer
Models each feature with missing values as a function of other features.
"""

from typing import List, Optional
from datamorph.transformers.imputation.mice import MICEImputer


class IterativeImputer(MICEImputer):
    """Alias and wrapper for iterative regression imputation."""
    def __init__(self, max_iter: int = 10, columns: Optional[List[str]] = None, name: str = "IterativeImputer"):
        super().__init__(max_iter=max_iter, columns=columns, name=name)
