"""
DataMorph Studio - Core Data Types & Enumerations
Defines the fundamental data types, schemas, and metadata structures
for the DataMorph ML data preprocessing engine.
"""

from enum import Enum
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
import datetime


class DataType(str, Enum):
    """Supported fundamental feature types in DataMorph Studio."""
    NUMERIC_INT = "int"
    NUMERIC_FLOAT = "float"
    CATEGORICAL_NOMINAL = "nominal"
    CATEGORICAL_ORDINAL = "ordinal"
    DATETIME = "datetime"
    TIMESTAMP = "timestamp"
    TEXT = "text"
    BOOLEAN = "boolean"
    BINARY = "binary"
    VECTOR = "vector"
    UNKNOWN = "unknown"


class ImputationStrategy(str, Enum):
    """Strategies for handling missing values in datasets."""
    MEAN = "mean"
    MEDIAN = "median"
    MODE = "mode"
    CONSTANT = "constant"
    KNN = "knn"
    MICE = "mice"
    FORWARD_FILL = "forward_fill"
    BACKWARD_FILL = "backward_fill"
    DROP_ROWS = "drop_rows"
    DROP_COLUMNS = "drop_columns"
    INDICATOR = "indicator"


class ScalingStrategy(str, Enum):
    """Feature scaling and normalization algorithms."""
    STANDARD = "standard"
    MINMAX = "minmax"
    ROBUST = "robust"
    MAXABS = "maxabs"
    QUANTILE_UNIFORM = "quantile_uniform"
    QUANTILE_NORMAL = "quantile_normal"
    POWER_YEO_JOHNSON = "power_yeo_johnson"
    POWER_BOX_COX = "power_box_cox"
    L1_NORMALIZER = "l1_normalizer"
    L2_NORMALIZER = "l2_normalizer"


class EncodingStrategy(str, Enum):
    """Categorical encoding strategies."""
    ONE_HOT = "one_hot"
    ORDINAL = "ordinal"
    TARGET = "target"
    WEIGHT_OF_EVIDENCE = "woe"
    CATBOOST = "catboost"
    FREQUENCY = "frequency"
    BINARY = "binary"
    LABEL = "label"
    HASHING = "hashing"


class OutlierStrategy(str, Enum):
    """Outlier detection and remediation techniques."""
    Z_SCORE = "z_score"
    IQR = "iqr"
    ISOLATION_FOREST = "isolation_forest"
    LOCAL_OUTLIER_FACTOR = "lof"
    MAHALANOBIS = "mahalanobis"
    WINSORIZE = "winsorize"
    TRUNCATE = "truncate"
    FLAG_ONLY = "flag_only"


class DiscretizationStrategy(str, Enum):
    """Binning and continuous-to-discrete strategies."""
    EQUAL_WIDTH = "equal_width"
    EQUAL_FREQUENCY = "equal_frequency"
    KMEANS = "kmeans"
    CUSTOM_EDGES = "custom_edges"


class FeatureSelectionStrategy(str, Enum):
    """Feature selection and dimensional reduction techniques."""
    VARIANCE_THRESHOLD = "variance_threshold"
    CORRELATION_FILTER = "correlation_filter"
    MUTUAL_INFORMATION = "mutual_information"
    CHI_SQUARE = "chi_square"
    RFE = "recursive_feature_elimination"
    PCA = "pca"


class AugmentationStrategy(str, Enum):
    """Data augmentation and sampling techniques."""
    SMOTE = "smote"
    NOISE_INJECTION = "noise_injection"
    MIXUP = "mixup"
    RANDOM_UNDERSAMPLE = "random_undersample"
    TOMEK_LINKS = "tomek_links"


class PipelineExecutionStatus(str, Enum):
    """Lifecycle statuses for pipeline dag steps and runs."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


@dataclass
class ColumnMetadata:
    """Metadata describing a single column/feature in a dataset."""
    name: str
    dtype: DataType
    nullable: bool = True
    missing_count: int = 0
    missing_pct: float = 0.0
    distinct_count: int = 0
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    mean_value: Optional[float] = None
    std_value: Optional[float] = None
    categories: Optional[List[str]] = None
    cardinality: Optional[int] = None
    sample_values: List[Any] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


@dataclass
class DatasetMetadata:
    """High-level metadata for an uploaded or transformed dataset."""
    dataset_id: str
    name: str
    source_filename: str
    row_count: int
    column_count: int
    memory_usage_bytes: int
    created_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())
    columns: Dict[str, ColumnMetadata] = field(default_factory=dict)
    target_column: Optional[str] = None
    id_column: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    version: int = 1
