"""
DataMorph Studio - Transformer Plugin Registry
Enables dynamic discovery and instantiation of all built-in preprocessing algorithms.
"""

from typing import Dict, Type, Any, List
from datamorph.transformers.base import BaseTransformer
from datamorph.transformers.imputation.simple import SimpleImputer
from datamorph.transformers.imputation.knn import KNNImputer
from datamorph.transformers.imputation.mice import MICEImputer
from datamorph.transformers.imputation.indicator import MissingIndicator
from datamorph.transformers.scaling.standard import StandardScaler
from datamorph.transformers.scaling.minmax import MinMaxScaler
from datamorph.transformers.scaling.robust import RobustScaler
from datamorph.transformers.scaling.maxabs import MaxAbsScaler
from datamorph.transformers.scaling.quantile import QuantileTransformer
from datamorph.transformers.scaling.power import PowerTransformer
from datamorph.transformers.scaling.normalizer import VectorNormalizer
from datamorph.transformers.encoding.onehot import OneHotEncoder
from datamorph.transformers.encoding.ordinal import OrdinalEncoder
from datamorph.transformers.encoding.target import TargetEncoder
from datamorph.transformers.encoding.woe import WeightOfEvidenceEncoder
from datamorph.transformers.encoding.catboost import CatBoostEncoder
from datamorph.transformers.encoding.frequency import FrequencyEncoder
from datamorph.transformers.encoding.binary import BinaryEncoder
from datamorph.transformers.outliers.zscore import ZScoreOutlierDetector
from datamorph.transformers.outliers.iqr import IQROutlierRemover
from datamorph.transformers.outliers.isolation_forest import IsolationForestOutliers
from datamorph.transformers.outliers.winsorizer import Winsorizer
from datamorph.transformers.temporal.cyclical import CyclicalDateTimeEncoder
from datamorph.transformers.temporal.datetime_extractor import DateTimeFeatureExtractor
from datamorph.transformers.temporal.lag_lead import LagLeadFeatureGenerator
from datamorph.transformers.temporal.rolling_window import RollingWindowAggregator
from datamorph.transformers.text.cleaner import TextCleaner
from datamorph.transformers.text.tokenizer import RegexTokenizer
from datamorph.transformers.text.tfidf import TFIDFVectorizer
from datamorph.transformers.text.count_vectorizer import CountVectorizer
from datamorph.transformers.discretization.equal_width import EqualWidthDiscretizer
from datamorph.transformers.discretization.equal_frequency import EqualFrequencyDiscretizer
from datamorph.transformers.discretization.kmeans_binning import KMeansDiscretizer
from datamorph.transformers.selection.variance import VarianceThresholdSelector
from datamorph.transformers.selection.correlation import CorrelationFilterSelector
from datamorph.transformers.selection.mutual_info import MutualInformationSelector
from datamorph.transformers.selection.chi_square import ChiSquareSelector
from datamorph.transformers.selection.pca import PrincipalComponentAnalysis
from datamorph.transformers.augmentation.smote import SyntheticMinorityOverSampler
from datamorph.transformers.augmentation.noise_injection import GaussianNoiseInjector
from datamorph.transformers.augmentation.mixup import MixupAugmenter
from datamorph.transformers.augmentation.undersample import RandomUnderSampler


class TransformerRegistry:
    """Central catalog of available preprocessing transformers."""
    _catalog: Dict[str, Type[BaseTransformer]] = {
        "SimpleImputer": SimpleImputer,
        "KNNImputer": KNNImputer,
        "MICEImputer": MICEImputer,
        "MissingIndicator": MissingIndicator,
        "StandardScaler": StandardScaler,
        "MinMaxScaler": MinMaxScaler,
        "RobustScaler": RobustScaler,
        "MaxAbsScaler": MaxAbsScaler,
        "QuantileTransformer": QuantileTransformer,
        "PowerTransformer": PowerTransformer,
        "VectorNormalizer": VectorNormalizer,
        "OneHotEncoder": OneHotEncoder,
        "OrdinalEncoder": OrdinalEncoder,
        "TargetEncoder": TargetEncoder,
        "WeightOfEvidenceEncoder": WeightOfEvidenceEncoder,
        "CatBoostEncoder": CatBoostEncoder,
        "FrequencyEncoder": FrequencyEncoder,
        "BinaryEncoder": BinaryEncoder,
        "ZScoreOutlierDetector": ZScoreOutlierDetector,
        "IQROutlierRemover": IQROutlierRemover,
        "IsolationForestOutliers": IsolationForestOutliers,
        "Winsorizer": Winsorizer,
        "CyclicalDateTimeEncoder": CyclicalDateTimeEncoder,
        "DateTimeFeatureExtractor": DateTimeFeatureExtractor,
        "LagLeadFeatureGenerator": LagLeadFeatureGenerator,
        "RollingWindowAggregator": RollingWindowAggregator,
        "TextCleaner": TextCleaner,
        "RegexTokenizer": RegexTokenizer,
        "TFIDFVectorizer": TFIDFVectorizer,
        "CountVectorizer": CountVectorizer,
        "EqualWidthDiscretizer": EqualWidthDiscretizer,
        "EqualFrequencyDiscretizer": EqualFrequencyDiscretizer,
        "KMeansDiscretizer": KMeansDiscretizer,
        "VarianceThresholdSelector": VarianceThresholdSelector,
        "CorrelationFilterSelector": CorrelationFilterSelector,
        "MutualInformationSelector": MutualInformationSelector,
        "ChiSquareSelector": ChiSquareSelector,
        "PrincipalComponentAnalysis": PrincipalComponentAnalysis,
        "SyntheticMinorityOverSampler": SyntheticMinorityOverSampler,
        "GaussianNoiseInjector": GaussianNoiseInjector,
        "MixupAugmenter": MixupAugmenter,
        "RandomUnderSampler": RandomUnderSampler,
    }

    @classmethod
    def get(cls, name: str) -> Type[BaseTransformer]:
        if name not in cls._catalog:
            raise KeyError(f"Transformer '{name}' is not registered in DataMorph catalog")
        return cls._catalog[name]

    @classmethod
    def list_all(cls) -> List[str]:
        return list(cls._catalog.keys())

    @classmethod
    def create(cls, name: str, **kwargs) -> BaseTransformer:
        t_cls = cls.get(name)
        return t_cls(**kwargs)
