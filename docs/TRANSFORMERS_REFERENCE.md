# DataMorph Studio - Complete Transformers Reference Manual

This document provides mathematical formulations, algorithmic specifications, hyperparameter definitions, and production guidelines for all 30+ built-in transformers in DataMorph Studio.

---

## 1. Imputation Subsystem (`datamorph.transformers.imputation`)

### SimpleImputer
- **Mathematical Formula**:
  - Mean: `x_hat = (1/N) * sum(x_i)`
  - Median: `x_hat = middle(sort(x))`
  - Mode: `x_hat = argmax(count(x_k))`
- **Parameters**: `strategy` (`mean`, `median`, `mode`, `constant`, `forward_fill`, `backward_fill`), `fill_value`.
- **Complexity**: Time O(N), Space O(1).

### KNNImputer
- **Mathematical Formula**:
  - Distance: `d(x, y) = sqrt(sum((x_j - y_j)^2))` for shared observed attributes.
  - Value: `x_hat = (1/K) * sum(y_k)`.
- **Parameters**: `n_neighbors` (default: 5).
- **Complexity**: Time O(N * M * K), Space O(N * M).

### MICEImputer (Multivariate Imputation by Chained Equations)
- **Algorithm**:
  1. Specify imputation model for each variable with missing data.
  2. Impute initial mean values for all missing entries.
  3. For each variable `j = 1 to P`, fit regression `y_j ~ X_{-j}` on observed entries and predict missing.
  4. Repeat for `max_iter` cycles until convergence.
- **Parameters**: `max_iter` (default: 5).

### MissingIndicator
- **Formula**: `indicator_j = 1 if x_j is null else 0`.
- **Parameters**: `prefix` (default: `"missing_"`).

---

## 2. Scaling Subsystem (`datamorph.transformers.scaling`)

### StandardScaler
- **Formula**: `z = (x - mu) / sigma` where `mu = mean(x)` and `sigma = std(x)`.
- **Properties**: Zero mean, unit variance. Preserves distribution shape.

### MinMaxScaler
- **Formula**: `x_scaled = ((x - x_min) / (x_max - x_min)) * (max_range - min_range) + min_range`.
- **Properties**: Bounds values strictly inside `[feature_range]`.

### RobustScaler
- **Formula**: `x_robust = (x - median(x)) / (Q3(x) - Q1(x))`.
- **Properties**: Outlier-resilient feature scaling based on Interquartile Range (IQR).

### MaxAbsScaler
- **Formula**: `x_scaled = x / max(|x|)`.
- **Properties**: Retains exact zero sparsity structure in sparse arrays.

### QuantileTransformer
- **Formula**: Rank transformation mapping empirical CDF `F(x)` to Uniform `U(0, 1)` or Normal `N(0, 1)`.

### PowerTransformer (Yeo-Johnson & Box-Cox)
- **Formula (Yeo-Johnson)**:
  - For `y >= 0`: `((y + 1)^lambda - 1) / lambda` if `lambda != 0` else `log(y + 1)`
  - For `y < 0`: `-((-y + 1)^(2 - lambda) - 1) / (2 - lambda)` if `lambda != 2` else `-log(-y + 1)`

### VectorNormalizer
- **Formula**: `x_norm = x / ||x||_p` where `p in {L1, L2, max}`.

---

## 3. Categorical Encoding Subsystem (`datamorph.transformers.encoding`)

### OneHotEncoder
- **Formula**: Creates binary indicator vectors for each unique categorical level.

### OrdinalEncoder
- **Formula**: Maps distinct levels to ordered integer ranks `0, 1, ..., k-1`.

### TargetEncoder (Empirical Bayes Smoothed)
- **Formula**: `S_i = (n_i * y_bar_i + weight * y_bar_global) / (n_i + weight)`.
- **Properties**: Prevents target leakage and handles small category subsets gracefully.

### WeightOfEvidenceEncoder (WoE)
- **Formula**: `WoE_i = ln( (Distribution_Good_i) / (Distribution_Bad_i) )`.
- **Information Value**: `IV = sum( (Dist_Good_i - Dist_Bad_i) * WoE_i )`.

### CatBoostEncoder
- **Formula**: Dynamic online target accumulator with prior smoothing.

### FrequencyEncoder
- **Formula**: `freq_i = count(category_i) / N_total`.

### BinaryEncoder
- **Formula**: Encodes integer category IDs into base-2 binary bit vectors.

---

## 4. Outlier Remediation Subsystem (`datamorph.transformers.outliers`)

### ZScoreOutlierDetector
- **Rule**: Outlier if `|x - mu| / sigma > threshold`.

### IQROutlierRemover (Tukey's Fences)
- **Rule**: Lower fence = `Q1 - 1.5 * IQR`, Upper fence = `Q3 + 1.5 * IQR`.

### IsolationForestOutliers
- **Algorithm**: Recursive random tree partitioning isolating anomalous observations at shallow depths.

### Winsorizer
- **Rule**: Clip values below `lower_quantile` (e.g., 5th percentile) and above `upper_quantile` (e.g., 95th percentile).

---

## 5. Temporal & Time-Series Subsystem (`datamorph.transformers.temporal`)

### CyclicalDateTimeEncoder
- **Trigonometric Form**: `x_sin = sin(2 * pi * t / T)`, `x_cos = cos(2 * pi * t / T)`.

### DateTimeFeatureExtractor
- Extracts: `year`, `month`, `day`, `dayofweek`, `hour`, `is_weekend`.

### LagLeadFeatureGenerator
- Generates historical lag steps `t-1, t-2, ..., t-k` and forward lead steps `t+1`.

### RollingWindowAggregator
- Computes sliding window aggregations (`mean`, `std`, `min`, `max`).

---

## 6. Text Processing Subsystem (`datamorph.transformers.text`)

### TextCleaner
- Cleans whitespace, lowercases text, removes numbers and punctuation.

### RegexTokenizer
- Segments strings into lexical token lists via regular expressions.

### TFIDFVectorizer
- **Formula**: `TF-IDF(t, d, D) = TF(t, d) * ln((1 + |D|) / (1 + DF(t)))`.

### CountVectorizer
- Generates token frequency count occurrences.

### SentimentFeatureExtractor
- Calculates positive, negative word counts, and sentiment polarity ratios.

---

## 7. Discretization Subsystem (`datamorph.transformers.discretization`)

### EqualWidthDiscretizer
- Divides continuous numerical range into `k` intervals of equal width: `W = (max - min) / k`.

### EqualFrequencyDiscretizer
- Divides data into `k` bins each containing equal probability mass (quantiles).

### KMeansDiscretizer
- Clusters continuous scalar space using 1D K-Means centroids.

### CustomBinDiscretizer
- Divides data based on arbitrary user-provided cut thresholds.

---

## 8. Feature Selection Subsystem (`datamorph.transformers.selection`)

### VarianceThresholdSelector
- Eliminates constant and quasi-constant features where `Var(X) < threshold`.

### CorrelationFilterSelector
- Drops collinear feature pairs where `|r_xy| >= threshold`.

### MutualInformationSelector
- Ranks features by Shannon mutual information `I(X; Y) = H(X) + H(Y) - H(X, Y)`.

### ChiSquareSelector
- Ranks categorical independence using Pearson's Chi-Square `X^2 = sum((O - E)^2 / E)`.

### PrincipalComponentAnalysis (PCA)
- Projects data onto orthogonal linear combination eigenvectors maximizing captured variance.

---

## 9. Data Augmentation Subsystem (`datamorph.transformers.augmentation`)

### SyntheticMinorityOverSampler (SMOTE)
- Interpolates synthetic minority examples: `x_new = x_i + lambda * (x_nn - x_i)`.

### GaussianNoiseInjector
- Injects Gaussian jitter: `x_noisy = x + N(0, sigma * std(x))`.

### MixupAugmenter
- Constructs linear combinations: `x_mix = lambda * x1 + (1 - lambda) * x2`.

### RandomUnderSampler
- Randomly samples majority classes to balance class distribution.
