# DataMorph Studio - Production-Level ML Data Preprocessing Platform

DataMorph Studio is an enterprise-grade Machine Learning data preprocessing, feature engineering, and data quality orchestration platform built natively in Python.

---

## Key Features

1. **Native High-Performance DataFrame Engine**:
   - Column-oriented in-memory data structures with vector math, quantiles, and missing data detection.
2. **30+ Production Transformers**:
   - **Imputation**: Simple (Mean/Median/Mode), KNN, MICE, Iterative, Missing Indicator.
   - **Scaling**: Standard, MinMax, Robust, MaxAbs, Quantile, Power (Yeo-Johnson & Box-Cox), Vector Normalizer.
   - **Encoding**: One-Hot, Ordinal, Target (Bayes Smoothed), Weight of Evidence (WoE), CatBoost-style, Frequency, Binary.
   - **Outliers**: Z-Score, IQR (Tukey's Fences), Isolation Forest, LOF, Mahalanobis Distance, Winsorizer.
   - **Temporal**: Cyclical (Sin/Cos), Date-Time Feature Extractor, Lag/Lead Generator, Rolling Window Aggregators.
   - **Text**: Text Cleaner, Regex Tokenizer, TF-IDF Vectorizer, Bag-of-Words Count Vectorizer, Sentiment Lexicon Features.
   - **Discretization**: Equal-Width, Equal-Frequency (Quantile), 1D K-Means Clustering, Custom Cut Points.
   - **Feature Selection**: Variance Threshold, Correlation Filter, Mutual Information, Chi-Square (X2), RFE, PCA.
   - **Augmentation**: SMOTE (Synthetic Minority Over-sampling), Gaussian Noise Injection, Mixup, Majority Under-Sampling.
3. **Interactive DAG Pipeline Engine**:
   - Topological sorting, cycle detection, execution telemetry, and lineage tracking.
4. **Data Drift & Quality Monitoring**:
   - Population Stability Index (PSI) and Kolmogorov-Smirnov 2-sample distribution shift detection.
5. **Interactive UI Dashboard**:
   - Modern responsive web studio with data inspector, DAG builder, transformer lab, and code generator.
6. **Zero External Framework Dependencies**:
   - Runs out-of-the-box on standard Python 3.8+.

---

## Quick Start

### 1. Run the Server
```bash
python run_server.py
```
Access the application at: `http://localhost:8000`

### 2. Login Credentials
- **Username**: `admin`
- **Password**: `admin123`

### 3. Run Test Suites
```bash
python -m unittest discover tests
```

### 4. Measure Production LOC
```bash
python measure.py
```
