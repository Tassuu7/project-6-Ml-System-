# DataMorph Studio - Complete Enterprise User Guide & Handbook

Welcome to the DataMorph Studio User Guide. This comprehensive handbook walks through setting up, configuring, transforming, monitoring, and deploying production machine learning data preprocessing pipelines.

---

## Table of Contents
1. [System Overview & Architecture](#1-system-overview--architecture)
2. [Getting Started & Installation](#2-getting-started--installation)
3. [Authentication & RBAC](#3-authentication--rbac)
4. [Dataset Ingestion & Quality Auditing](#4-dataset-ingestion--quality-auditing)
5. [Visual DAG Pipeline Orchestration](#5-visual-dag-pipeline-orchestration)
6. [Transformer Library Guide](#6-transformer-library-guide)
   - 6.1 Imputation Strategies
   - 6.2 Feature Scaling & Normalization
   - 6.3 Categorical Encoding
   - 6.4 Outlier Detection & Winsorization
   - 6.5 Temporal & Time-Series Engineering
   - 6.6 Natural Language & Text Vectorization
   - 6.7 Discretization & Binning
   - 6.8 Dimensionality Reduction & Feature Selection
   - 6.9 Data Augmentation & Imbalance Handling
7. [Statistical Data Drift Monitoring (PSI & KS Test)](#7-statistical-data-drift-monitoring)
8. [Feature Store Integration](#8-feature-store-integration)
9. [Code Generation & Python Compilation](#9-code-generation--python-compilation)
10. [REST API Reference & Webhooks](#10-rest-api-reference--webhooks)
11. [Production Deployment Best Practices](#11-production-deployment-best-practices)

---

## 1. System Overview & Architecture

DataMorph Studio was engineered from the ground up to eliminate the friction between exploratory data analysis (EDA) and production feature pipelines. In standard ML workflows, data scientists experiment with Jupyter notebooks, creating complex, untracked transformations that engineers must rewrite in high-performance production code.

DataMorph Studio bridges this gap with:
- **Declarative Pipeline DAGs**: Graph representations of transformations that guarantee acyclicity and reproducibility.
- **Native Pure Python Matrix Engine**: High-performance in-memory DataFrame and Series implementations with zero mandatory external binary dependencies.
- **Bi-directional Code Export**: Interactive visual builder compiles directly into production Python / Pandas / Scikit-Learn deployment scripts.
- **Continuous Distribution Drift Tracking**: Built-in Population Stability Index (PSI) and Kolmogorov-Smirnov monitors that alert teams before model performance degrades.

---

## 2. Getting Started & Installation

### Prerequisites
- Python 3.8, 3.9, 3.10, 3.11, or 3.12.
- Any modern web browser (Chrome, Firefox, Safari, Edge).

### Launching DataMorph Studio
```bash
python run_server.py
```
Upon execution, the terminal displays:
```
==================================================
  DATAMORPH STUDIO - ML PREPROCESSING PLATFORM    
==================================================
  Local URL  : http://localhost:8000
  Login URL  : http://localhost:8000/login.html
  Username   : admin
  Password   : admin123
==================================================
```

---

## 3. Authentication & RBAC

DataMorph Studio includes secure token-based authentication using PBKDF2-HMAC-SHA256 password hashing and HMAC-SHA256 signed bearer tokens.

### Roles and Permissions:
- **Lead ML Engineer / Admin**: Full access to all dataset uploads, pipeline executions, feature store mutations, and user provisioning.
- **Data Scientist**: Access to dataset workspace, DAG builder, transformer lab, and drift monitoring.
- **MLOps Engineer**: Access to pipeline runner, monitoring metrics, drift alerts, and export webhooks.

---

## 4. Dataset Ingestion & Quality Auditing

### Supported Ingestion Formats
1. **CSV (Comma Separated Values)**: Automated delimiter sniffing, header detection, and type inference.
2. **JSON Records**: Nested object flattening and record matrix parsing.
3. **Cloud Connectors**: Direct streams from AWS S3, Snowflake, PostgreSQL, and Kafka topics.

### Automated Data Quality Auditing (DQA)
When a dataset is uploaded, DataMorph Studio immediately runs a multi-point diagnostic check:
- **Missingness Ratio**: Calculates per-feature and overall null cell percentages.
- **Cardinality Audit**: Flags zero-variance constant columns and ID-candidate columns.
- **Duplicate Detection**: Hashes row vectors to detect redundant duplicate observations.
- **Composite Quality Score**: Generates a normalized score (0 to 100) and letter grade (A+, A, B, C, D).

---

## 5. Visual DAG Pipeline Orchestration

The DAG Pipeline orchestrator arranges transformers as nodes in a directed graph. Each step defines:
- **Step ID**: Unique deterministic identifier.
- **Transformer Type**: Selected from the 30+ registered transformers.
- **Target Columns**: Features to transform.
- **Dependencies (`depends_on`)**: Preceding step IDs required before execution.

### Graph Validation & Topological Sorting
The orchestrator implements Kahn's algorithm to resolve execution order:
1. Computes in-degree for all pipeline nodes.
2. Initializes queue with zero in-degree root nodes.
3. Iteratively evaluates dependencies and decrements in-degree counts.
4. Detects and rejects circular dependency cycles before memory allocation.

---

## 6. Transformer Library Guide

### 6.1 Imputation Strategies
- `SimpleImputer`: High-speed central tendency replacements (`mean`, `median`, `mode`, `constant`).
- `KNNImputer`: Multi-attribute Euclidean distance k-nearest neighbor imputation.
- `MICEImputer`: Multivariate Imputation by Chained Equations for complex feature interactions.
- `MissingIndicator`: Generates binary feature flags marking missing status.

### 6.2 Feature Scaling & Normalization
- `StandardScaler`: Normalizes features to `mu = 0` and `sigma = 1`.
- `MinMaxScaler`: Linearly scales feature values into `[min, max]` intervals.
- `RobustScaler`: Outlier-resistant scaling using median and Interquartile Range (IQR).
- `MaxAbsScaler`: Scales by maximum absolute value while preserving sparsity.
- `QuantileTransformer`: Maps non-linear distributions to uniform or Gaussian profiles.
- `PowerTransformer`: Yeo-Johnson and Box-Cox variance stabilization.
- `VectorNormalizer`: Row-wise L1/L2/Max unit vector normalization.

### 6.3 Categorical Encoding
- `OneHotEncoder`: Expands nominal categories into orthogonal indicator features.
- `OrdinalEncoder`: Assigns deterministic integer ranks.
- `TargetEncoder`: Empirical Bayes smoothed target mean encoding.
- `WeightOfEvidenceEncoder`: Credit risk log-odds transformation with Information Value (IV).
- `CatBoostEncoder`: Online streaming target encoder preventing target leakage.
- `FrequencyEncoder`: Replaces categories with normalized occurrence probabilities.
- `BinaryEncoder`: Base-2 bit expansion for high-cardinality nominal variables.

### 6.4 Outlier Remediation
- `ZScoreOutlierDetector`: Parametric standard deviation thresholding.
- `IQROutlierRemover`: Non-parametric Tukey's fence clipping.
- `IsolationForestOutliers`: Multi-dimensional ensemble tree isolation.
- `Winsorizer`: Percentile quantile capping (5th/95th percentiles).

### 6.5 Temporal & Time-Series Engineering
- `CyclicalDateTimeEncoder`: Sine and Cosine trigonometric decomposition of hours/days/months.
- `DateTimeFeatureExtractor`: Granular calendar attribute parsing (year, month, day, weekday, is_weekend).
- `LagLeadFeatureGenerator`: Autoregressive lag and forward-looking lead shifts.
- `RollingWindowAggregator`: Sliding window rolling statistics (`mean`, `std`, `min`, `max`).

### 6.6 Natural Language & Text Vectorization
- `TextCleaner`: Case normalization, punctuation removal, number stripping.
- `RegexTokenizer`: Custom regex token array extraction.
- `TFIDFVectorizer`: Term Frequency - Inverse Document Frequency vector computation.
- `CountVectorizer`: Bag-of-words token count matrices.
- `SentimentFeatureExtractor`: Lexicon-based positive/negative word counts and polarity ratios.

### 6.7 Discretization & Binning
- `EqualWidthDiscretizer`: Divides continuous ranges into equal scalar intervals.
- `EqualFrequencyDiscretizer`: Quantile-based probability mass binning.
- `KMeansDiscretizer`: 1D K-Means cluster centroid grouping.
- `CustomBinDiscretizer`: Manual domain cut point specification.

### 6.8 Dimensionality Reduction & Feature Selection
- `VarianceThresholdSelector`: Constant and low-variance feature pruning.
- `CorrelationFilterSelector`: Collinear feature pair elimination.
- `MutualInformationSelector`: Non-linear Shannon entropy ranking.
- `ChiSquareSelector`: Categorical independence contingency testing.
- `PrincipalComponentAnalysis (PCA)`: Orthogonal variance projection.

### 6.9 Data Augmentation & Imbalance Handling
- `SyntheticMinorityOverSampler (SMOTE)`: Minority class feature interpolation.
- `GaussianNoiseInjector`: Normal perturbation regularizer.
- `MixupAugmenter`: Convex linear combinations of sample pairs.
- `RandomUnderSampler`: Majority class down-sampling.

---

## 7. Statistical Data Drift Monitoring

DataMorph Studio monitors feature distributions over time using two key statistical metrics:

### Population Stability Index (PSI)
$$PSI = \sum \left( P_{current}(i) - P_{baseline}(i) \right) \times \ln\left( \frac{P_{current}(i)}{P_{baseline}(i)} \right)$$

- `PSI < 0.10`: Distribution is stable; no retraining needed.
- `0.10 <= PSI < 0.25`: Moderate shift; monitor closely.
- `PSI >= 0.25`: Significant drift detected; automatic pipeline trigger required.

### Kolmogorov-Smirnov (KS) Test
$$D = \sup_x |F_{baseline}(x) - F_{current}(x)|$$
Calculates the maximum vertical divergence between the two cumulative distribution functions (CDFs).

---

## 8. Feature Store Integration

The integrated Feature Store maintains versioned feature views and entity lookups:
- Register feature views from any pipeline output.
- Tag and catalog feature definitions with lineage graphs.
- Real-time online lookup endpoints for low-latency model inference.

---

## 9. Code Generation & Python Compilation

Every DAG pipeline can be compiled into a standalone Python deployment script:
1. In the Web UI, navigate to the **Code Generator** tab.
2. Click **Copy Code** or **Export Python Script**.
3. The generated script runs with zero dependencies on external orchestration engines.

---

## 10. REST API Reference & Webhooks

Integrate DataMorph Studio into existing CI/CD or MLOps pipelines using standard HTTP requests:
- `POST /api/datasets/upload`: Stream CSV or JSON data.
- `POST /api/pipeline/execute`: Trigger end-to-end preprocessing DAG.
- `POST /api/monitoring/drift`: Check drift status and receive alert webhooks.
- `POST /api/export`: Request export in CSV or JSON format.

---

## 11. Production Deployment Best Practices

1. **Persist Baseline Profiles**: Always save golden reference datasets when training models to ensure accurate drift benchmarks.
2. **Handle Imputation Before Scaling**: Ensure missing values are imputed before applying variance-dependent scalers like `StandardScaler`.
3. **Use Bayes Smoothed Target Encoding**: For high-cardinality categorical features, configure smoothing `weight >= 10.0` to avoid target overfitting.
4. **Monitor PSI in Staging**: Run daily drift audits on production inference logs to catch data pipeline schema anomalies before they impact downstream prediction quality.
