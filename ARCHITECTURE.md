# DataMorph Studio - Architectural Design

```
+-------------------------------------------------------------------------------+
|                             DataMorph Studio UI                               |
| (Responsive HTML5 / CSS3 / Vanilla JS SPA Dashboard & DAG Pipeline Builder)   |
+-------------------------------------------------------------------------------+
                                      | HTTP / REST API
+-------------------------------------------------------------------------------+
|                                REST API Layer                                 |
|  - Auth Router         - Dataset Router        - Pipeline Router              |
|  - Transform Router    - Monitoring Router     - Export Router                |
+-------------------------------------------------------------------------------+
                                      |
+-------------------------------------------------------------------------------+
|                            Orchestration & Core                               |
|  - Pipeline DAG Engine (Topological Sort, Dependency Validation)              |
|  - Execution Context & Step Telemetry                                         |
|  - Native In-Memory DataFrame & Series Matrix                                 |
|  - Data Lineage & Provenance Graph Tracker                                    |
+-------------------------------------------------------------------------------+
                                      |
+-------------------------------------------------------------------------------+
|                         Transformer Subsystems (30+)                          |
|  - Imputation (Simple, KNN, MICE, Iterative, Indicator)                       |
|  - Scaling (Standard, MinMax, Robust, MaxAbs, Quantile, Power, Normalizer)    |
|  - Encoding (OneHot, Ordinal, Target, WoE, CatBoost, Frequency, Binary)       |
|  - Outliers (Z-Score, IQR, Isolation Forest, LOF, Mahalanobis, Winsorize)     |
|  - Temporal (Cyclical, Date-Time, Lag/Lead, Rolling Windows)                  |
|  - Text (Cleaner, Tokenizer, TF-IDF, Count Vectorizer, Sentiment)             |
|  - Discretization (Equal-Width, Equal-Freq, KMeans, Custom)                   |
|  - Selection (Variance, Correlation, Mutual Info, Chi-Square, RFE, PCA)       |
|  - Augmentation (SMOTE, Gaussian Noise, Mixup, Random Under-Sampling)         |
+-------------------------------------------------------------------------------+
                                      |
+-------------------------------------------------------------------------------+
|                        Monitoring & Storage Engine                            |
|  - Statistical Drift Detector (PSI, Kolmogorov-Smirnov, Total Variation)      |
|  - Automated Data Quality Auditor & Profiler                                  |
|  - CSV/JSON Reader & Writer                                                   |
|  - In-Memory Feature Store & JSON Document Database                           |
+-------------------------------------------------------------------------------+
```
