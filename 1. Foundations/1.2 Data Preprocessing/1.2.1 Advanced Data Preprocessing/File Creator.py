import os
import re

# 1. Define the target directory
target_dir = r"C:\Users\balasubramanian.pg\Music\1. Foundations\1.2 Data Preprocessing\1.2.1 Advanced Data Preprocessing"

# Create the directories if they don't exist
os.makedirs(target_dir, exist_ok=True)

# 2. Paste the generated list here
raw_text = """
1. **Mechanisms of Missingness:** Understanding if data is Missing Completely At Random (MCAR), Missing At Random (MAR), or Missing Not At Random (MNAR) is crucial for selecting advanced imputation strategies.
2. **Algorithmic Imputation:** Using predictive machine learning algorithms (e.g., Random Forests, k-NN) to predict and fill in missing values based on the complex relationships with other features.
3. **K-Nearest Neighbors (KNN) Imputation:** Imputing missing values using the mean or median of the k most similar complete data points, using a distance metric like Euclidean or Manhattan.
4. **Distance Weighting in KNN:** Improving KNN imputation by weighting the contribution of neighboring points inversely to their distance, giving closer points more influence.
5. **Multiple Imputation by Chained Equations (MICE):** A highly robust statistical method that models each feature with missing values as a function of other features in a round-robin fashion, repeating over multiple iterations.
6. **Iterative Imputer (scikit-learn):** The Python implementation inspired by MICE, which fits a sequence of regression models (like Bayesian Ridge or Extra Trees) to iteratively estimate missing values.
7. **MissForest:** A non-parametric, Random Forest-based implementation of iterative imputation that naturally handles non-linear relationships, interactions, and mixed data types (categorical and continuous).
8. **Deep Learning Imputation (Datawig/Autoencoders):** Using deep neural networks or denoising autoencoders to learn latent representations of data to reconstruct missing values in highly complex datasets.
9. **Matrix Factorization for Imputation:** Decomposing a dataset into lower-dimensional matrices (as used in recommendation systems like SVD) to estimate missing entries.
10. **Temporal Imputation (Forward/Backward Fill):** Advanced when combined with grouping; propagating the last known observation forward (LOCF) or next known backward (NOCB) within specific time-series entities (e.g., per user).
11. **Interpolation (Time Series):** Estimating missing values by drawing a mathematical curve (linear, spline, polynomial) between known data points in sequential data.
12. **Spline Interpolation:** A piecewise polynomial interpolation that is smoother and more robust to extreme values than standard polynomial interpolation for missing time-series gaps.
13. **Seasonal/Cyclic Imputation:** Imputing missing time-series data using historical averages for that specific seasonal period (e.g., replacing a missing Tuesday value with the average of all other Tuesdays).
14. **Adding Missingness Indicators:** Creating a new binary feature that flags whether a value was missing, allowing the model to learn if the missingness itself (MAR/MNAR) contains predictive signal.
15. **Expectation-Maximization (EM) Imputation:** A statistical algorithm that alternates between estimating missing values (Expectation) and optimizing model parameters (Maximization) until convergence.
16. **Hot-Deck Imputation:** Replacing missing values with actual observed values from similar, randomly chosen "donor" records in the same dataset to preserve natural variance.
17. **Cold-Deck Imputation:** Similar to hot-deck, but the "donor" records are pulled from an entirely separate, external dataset or historical baseline.
18. **Censored Data Handling:** Treating data where the exact value is unknown but bounded (e.g., "Income > $100k") using survival analysis techniques rather than treating it as purely missing.
19. **Imputation Leakage:** The critical error of calculating imputation parameters (like MICE distributions or KNN clusters) over the entire dataset rather than fitting strictly on the training set.
20. **Evaluating Imputation Quality:** Using techniques like cross-validation on artificially corrupted datasets to calculate RMSE/MAE between imputed values and known original values.
21. **High Cardinality Features:** Categorical variables with hundreds or thousands of unique levels (e.g., ZIP codes, IP addresses) where standard One-Hot Encoding creates massive, sparse, unmanageable matrices.
22. **Target Encoding (Mean Encoding):** Replacing a categorical value with the mean of the target variable for that category. Highly effective for high cardinality but prone to severe overfitting.
23. **Smoothing in Target Encoding:** Adding a regularization parameter to Target Encoding that blends the category's specific target mean with the overall global target mean based on the category's sample size.
24. **Leave-One-Out Encoding (LOO):** A variation of Target Encoding where the target value of the current row is excluded from the mean calculation to prevent the model from memorizing the target.
25. **K-Fold Target Encoding:** Splitting data into k folds and encoding categories in one fold using target statistics calculated only from the other k-1 folds to rigorously prevent data leakage.
26. **Weight of Evidence (WoE) Encoding:** Used primarily in binary classification and credit scoring, replacing categories with the natural log of the ratio of the proportion of positive events to negative events.
27. **Information Value (IV):** A metric derived from WoE that quantifies the predictive power of a categorical feature, used simultaneously as an encoding and feature selection mechanism.
28. **Feature Hashing (Hashing Trick):** Applying a hash function to categorical strings to map them into a fixed number of integer buckets (columns), eliminating the need to maintain a vocabulary dictionary.
29. **Hash Collisions:** The main drawback of feature hashing where two distinct categories are mapped to the same column; usually tolerated because machine learning models can often unentangle the signal.
30. **Entity Embeddings:** Mapping high-cardinality categorical variables into a continuous, low-dimensional vector space using neural networks, similar to word embeddings in NLP.
31. **Frequency/Count Encoding:** Replacing categories with their frequency count in the dataset, useful when the rarity or commonality of a category is naturally predictive.
32. **Helmert Encoding:** A statistical contrast encoding where each category is compared to the mean of the subsequent categories, useful in hierarchical or ordered classification.
33. **Sum Encoding (Deviation Encoding):** Comparing the mean of the dependent variable for a given category to the overall mean of the dependent variable.
34. **CatBoost Encoder:** A specialized target encoding method popularized by the CatBoost algorithm that relies on the concept of "ordering" the dataset and calculating target statistics cumulatively.
35. **Binary Encoding:** A hybrid approach where categories are converted to ordinal integers, which are then converted to binary code, and the digits are split into separate columns (logarithmic dimensionality).
36. **BaseN Encoding:** A generalization of Binary Encoding that converts integers to a specified base (e.g., Base 4), offering a tradeoff between memory efficiency and model interpretability.
37. **Grouping Rare Levels:** Preprocessing high cardinality features by identifying categories that appear below a certain threshold (e.g., <1%) and grouping them all into a single "Other" category.
38. **Fuzzy String Matching for Categoricals:** Using distance metrics (e.g., Levenshtein distance) to identify and merge slight misspellings of the same categorical entity (e.g., "New York" and "New Yrk").
39. **Temporal Encoding of Categoricals:** Sorting categorical occurrences by time and encoding them based on their recency or historical trend rather than static averages.
40. **Cyclical Feature Encoding:** Transforming cyclical categories (e.g., months, days, hours) using sine and cosine transformations to preserve their circular nature (e.g., December is adjacent to January).
41. **Multivariate Outliers:** Data points that are not extreme in any single dimension but represent an unusual combination of values across multiple dimensions.
42. **Mahalanobis Distance:** A multivariate distance metric that measures how many standard deviations a point is away from the mean of a distribution, accounting for the correlations between variables.
43. **Isolation Forests:** An unsupervised algorithm that detects anomalies by randomly partitioning data; anomalies are isolated closer to the root of the decision trees, resulting in shorter path lengths.
44. **Local Outlier Factor (LOF):** A density-based algorithm that compares the local density of a point to the local densities of its neighbors, identifying points that are substantially less dense (anomalies).
45. **DBSCAN for Outliers:** Density-Based Spatial Clustering of Applications with Noise; points that do not belong to any dense cluster are explicitly labeled as noise/outliers (-1).
46. **Minimum Covariance Determinant (MCD):** A robust estimator of multivariate location and scatter, generating an Elliptic Envelope to identify outliers in Gaussian-distributed data.
47. **One-Class SVM:** A variation of the Support Vector Machine trained entirely on "normal" data to learn a decision boundary; anything falling outside this boundary is flagged as an outlier.
48. **Autoencoders for Anomaly Detection:** Training a neural network to reconstruct normal input data; outliers are identified by having unusually high reconstruction errors.
49. **Robust Z-Score (Modified Z-Score):** Replacing the mean and standard deviation in the Z-score calculation with the Median and Median Absolute Deviation (MAD), which are highly resistant to outliers.
50. **Winsorization:** A capping strategy where extreme values (e.g., top and bottom 1%) are replaced by the exact value at that specific percentile boundary, preserving the data point but blunting its extremity.
51. **Trimming (Truncation):** Simply dropping the extreme percentile rows from the dataset entirely; risky as it results in data loss, but sometimes necessary for highly skewed noise.
52. **Log-Plus-One (log1p) Transformation:** Used to heavily compress large outlier values in highly skewed data without creating negative infinities when exact zeroes are present in the dataset.
53. **Capping via IQR:** Defining upper and lower bounds using the Interquartile Range (Q1 - 1.5 * IQR and Q3 + 1.5 * IQR) and clipping values to these boundaries.
54. **Outliers as Missing Values:** A hybrid strategy where identified extreme outliers are converted to NaNs and then handled using advanced imputation techniques (like MICE) to estimate a reasonable value.
55. **Contextual Outliers:** Identifying anomalies that are only extreme within a specific context (e.g., a temperature of 30°C in winter is an outlier, but normal in summer), requiring grouped outlier detection.
56. **Power Transformations:** A family of transformations applied to stabilize variance and make data more Gaussian-like, critical for linear models and neural networks.
57. **Box-Cox Transformation:** A parametric power transform that automatically searches for the optimal lambda parameter to normalize data, but strictly requires all input data to be strictly positive (>0).
58. **Yeo-Johnson Transformation:** An extension of the Box-Cox transformation that effectively normalizes data and handles positive, zero, and negative values.
59. **Quantile Transformation:** A non-linear transformation that maps a feature's probability density directly to a target distribution (usually standard normal or uniform), completely erasing original outliers.
60. **Interaction Features:** Creating new features by multiplying, dividing, adding, or subtracting two or more existing features to capture synergistic effects (e.g., X1 * X2).
61. **Polynomial Features:** Expanding a feature set by generating new features that are polynomials of the original features up to a specified degree (e.g., X, X^2, X^3), allowing linear models to fit curves.
62. **Feature Crosses:** A synthetic feature formed by multiplying (crossing) two or more categorical features, allowing models to learn specific combinations (e.g., "Gender=Male AND Occupation=Nurse").
63. **Mathematical Transformations:** Creating domain-specific features using non-linear math (e.g., log, square root, reciprocal) to match known physical or business realities.
64. **Binning (Discretization):** Converting continuous variables into discrete categorical bins to handle non-linear relationships or reduce the impact of minor observational errors.
65. **Equal-Width Binning:** Dividing the range of continuous data into N bins of the exact same size; highly sensitive to outliers.
66. **Equal-Frequency (Quantile) Binning:** Dividing data into N bins such that each bin contains roughly the same number of observations, naturally handling skewness and outliers.
67. **K-Means Binning:** Using 1D K-Means clustering to find natural groupings in continuous data and using the cluster assignments as the new discrete bins.
68. **MDLP (Minimum Description Length Principle) Binning:** A supervised discretization method that uses decision trees and target variable entropy to find the optimal cut points for binning a continuous feature.
69. **Geospatial Feature Generation:** Extracting actionable features from raw coordinates, such as "distance to nearest city center," "bearing," or "Haversine distance" between two points.
70. **Date/Time Feature Extraction:** Decomposing timestamps into multiple granular features: hour, day of week, is_weekend, is_holiday, quarter, or days_since_last_event.
71. **Recency, Frequency, Monetary (RFM) Features:** Standardized aggregations used in customer analytics preprocessing to summarize behavioral data into three highly predictive continuous features.
72. **Aggregated Group Features:** Calculating statistical summaries (mean, max, min, std) of a numerical feature grouped by a categorical feature (e.g., "average transaction amount per user") and merging it back.
73. **Dimensionality Expansion:** Deliberately increasing the number of features via Basis Expansions (like Splines or Radial Basis Functions) to make data linearly separable in higher dimensions.
74. **Spline Transformations:** Creating piecewise polynomial features to model complex, wiggly relationships smoothly, avoiding the erratic behavior of high-degree global polynomials (Runge's phenomenon).
75. **Automated Feature Engineering (Featuretools):** Using frameworks that apply "Deep Feature Synthesis" to automatically generate hundreds of aggregated and relational features from multiple linked database tables.
76. **Class Imbalance Problem:** When one class (majority) vastly outnumbers another (minority) in classification, causing models to heavily bias toward predicting the majority class.
77. **Random Undersampling:** Randomly removing examples from the majority class until it matches the size of the minority class. Can cause significant loss of valuable information.
78. **Random Oversampling:** Randomly duplicating examples from the minority class to balance the dataset. Increases training time and heavily risks overfitting.
79. **SMOTE (Synthetic Minority Over-sampling Technique):** Creating artificial minority examples by interpolating new points along the line segments joining k-nearest minority class neighbors.
80. **SMOTE-NC (Nominal and Continuous):** An extension of SMOTE capable of handling datasets containing both continuous and categorical (nominal) features.
81. **Borderline-SMOTE:** A variation of SMOTE that only generates synthetic samples near the decision boundary between classes, where misclassification is most likely.
82. **ADASYN (Adaptive Synthetic Sampling):** Similar to SMOTE, but automatically dynamically generates more synthetic data in regions of the feature space where the density of minority examples is low.
83. **Tomek Links:** An undersampling technique that finds pairs of closest neighbors belonging to opposite classes and removes the majority class instance to clarify the decision boundary.
84. **Edited Nearest Neighbors (ENN):** An undersampling method that removes majority class instances if their k nearest neighbors mostly belong to the minority class, cleaning up noisy borders.
85. **SMOTE + Tomek (Hybrid):** Combining oversampling (SMOTE) with undersampling (Tomek Links) to first expand the minority class and then clean up the overlapping noisy boundaries.
86. **Cluster Centroids:** An undersampling method that replaces groups of majority class samples with the centroid of a K-Means cluster, preserving variance better than random dropping.
87. **NearMiss Algorithms:** A family of undersampling methods that retain majority class examples based on their specific distance to minority class examples (e.g., keeping majority points closest to minority points).
88. **Cost-Sensitive Learning (Class Weights):** Modifying the algorithm's loss function during preprocessing (via class_weight='balanced') to penalize mistakes on the minority class more severely, avoiding sampling altogether.
89. **Imbalanced Regression:** Handling skewness in continuous target variables by preprocessing with SMOTE for Regression (SMOTER) or applying specialized weighting mechanisms.
90. **Stratified Sampling:** Ensuring that train/test/validation splits perfectly maintain the original imbalanced class distribution, preventing test sets from containing zero minority examples.
91. **Data Augmentation as Oversampling:** In image/text data, applying transformations (cropping, rotating, synonym replacement) specifically to minority class data to balance the set organically.
92. **Evaluation Metrics for Imbalance:** Recognizing that preprocessing imbalanced data invalidates Accuracy; optimization must be tied to Precision, Recall, F1-Score, or AUCPR (Area Under Precision-Recall Curve).
93. **Ensemble Resampling (Balanced Random Forest):** Modifying the bagging process of Random Forests so that each bootstrap sample heavily undersamples the majority class.
94. **EasyEnsemble:** An algorithm that creates multiple independent subsets of the majority class, pairs each with the full minority class, and trains an ensemble of AdaBoost classifiers.
95. **Focal Loss Adjustment:** An advanced objective function modification (often used in Neural Networks) that dynamically scales cross-entropy loss based on prediction confidence, heavily focusing on hard-to-predict minority classes.
96. **Stationarity:** The property where a time series' statistical properties (mean, variance) do not change over time. Many advanced forecasting models require stationary data as input.
97. **Differencing:** Subtracting the previous observation from the current observation to remove trends and force a time series toward stationarity.
98. **Seasonal Differencing:** Subtracting the observation from the same season in the previous cycle (e.g., Y_t - Y_{t-12} for monthly data) to eliminate seasonal patterns.
99. **Lag Features:** Creating new predictors by shifting the target variable back in time (e.g., using sales from T-1, T-2, T-3 as features to predict sales at T).
100. **Rolling Window Statistics:** Calculating statistical measures (mean, std, min, max) over a sliding historical window (e.g., "7-day rolling average") to capture local time-series momentum.
101. **Expanding Window Statistics:** Similar to rolling windows, but the window size continuously grows from the start of the series to the current point, capturing the entire history up to T.
102. **Exponentially Weighted Moving Averages (EWMA):** A rolling average where more recent observations are given exponentially higher weight, responding faster to recent changes than a simple moving average.
103. **Time Series Decomposition:** Preprocessing by mathematically splitting a time series into three constituent parts: Trend, Seasonality, and Residual (noise), often using STL (Seasonal and Trend decomposition using Loess).
104. **Fourier Transformations for Seasonality:** Generating sine and cosine features at various frequencies to model complex, multiple-seasonality patterns (e.g., daily and yearly patterns simultaneously).
105. **Dynamic Time Warping (DTW) Alignment:** An advanced technique to align two time-series sequences that may vary in speed or timing, ensuring features are compared at the correct temporal phase.
106. **Handling Irregular Time Series:** Preprocessing data with inconsistent timestamp intervals by resampling the data to a fixed frequency (e.g., strictly hourly) and imputing or aggregating the gaps.
107. **Downsampling / Aggregation:** Reducing the frequency of time series data (e.g., converting minutes to days) using aggregation functions like sum, mean, or last-value-observed.
108. **Upsampling / Interpolation:** Increasing the frequency of time series data (e.g., converting days to hours) and filling the newly created gaps with interpolation logic.
109. **Lead Features (Future Information):** Creating features representing future events (e.g., "days until next major holiday") which are legitimate predictors, unlike standard target leakage.
110. **Autocorrelation Analysis (ACF/PACF):** Using Auto-Correlation and Partial Auto-Correlation Functions as analytical preprocessing steps to determine the exact optimal number of lag features to generate.
111. **Log Return Transformation:** In financial time series, converting raw prices to logarithmic returns to achieve stationarity, normalize scale, and ensure symmetry.
112. **Fractional Differencing:** An advanced alternative to integer differencing (1st or 2nd order) that achieves stationarity while preserving maximum memory (correlation) of the original series.
113. **Time-Series Cross-Validation Splits:** Preprocessing the data-splitting phase using TimeSeriesSplit (rolling origin) to prevent data leakage from the future into the past.
114. **Calendar Anomalies:** Engineering features to flag specific temporal anomalies like "payday," "black friday," or "leap year day" that severely distort baseline models.
115. **Target Scaling in Time Series:** Scaling time-series targets requires careful inverse-transformation post-prediction; parameters must be learned only on the rolling training window to prevent leakage.
116. **Tokenization:** The foundational process of breaking raw text into smaller units (tokens) such as words, sentences, or subwords.
117. **Subword Tokenization (BPE/WordPiece):** Advanced tokenization that breaks rare words into subword units (e.g., "unhappiness" -> "un", "happi", "ness") to handle Out-Of-Vocabulary (OOV) words.
118. **Stopword Removal:** Filtering out highly common words (e.g., "the", "is", "and") that carry little semantic meaning to reduce dimensionality and noise.
119. **Stemming:** A crude heuristic process that chops the ends off words to reduce them to their root form (e.g., "running" -> "run", "better" -> "bett").
120. **Lemmatization:** An advanced morphological analysis that uses a dictionary (lexicon) to return the actual, linguistically correct base dictionary form of a word (e.g., "better" -> "good").
121. **Part-of-Speech (POS) Tagging:** Assigning grammatical tags (Noun, Verb, Adjective) to words in context, often used to filter text (e.g., keeping only nouns for topic modeling).
122. **Named Entity Recognition (NER) Masking:** Identifying entities like People, Organizations, or Dates, and preprocessing the text by replacing them with generic tags (e.g., replacing "John" with <PERSON>).
123. **N-Grams:** Combining consecutive words into single tokens (bigrams = 2 words, trigrams = 3 words) to capture local context and phrase meaning (e.g., "not good" vs "good").
124. **Bag of Words (BoW / CountVectorizer):** Representing text as a matrix of token counts, ignoring word order but capturing vocabulary presence.
125. **TF-IDF (Term Frequency-Inverse Document Frequency):** An advanced vectorizer that down-weights words that appear frequently across all documents while up-weighting rare, highly informative words specific to a document.
126. **Word2Vec (Static Embeddings):** A neural network-based technique that maps words to dense vectors in a continuous multi-dimensional space, capturing semantic relationships (e.g., King - Man + Woman = Queen).
127. **GloVe (Global Vectors):** An embedding technique similar to Word2Vec but relies on global word co-occurrence matrices rather than local context windows.
128. **FastText:** An extension of Word2Vec developed by Facebook that learns embeddings for subwords/character n-grams, allowing it to generate embeddings for misspelled or out-of-vocabulary words.
129. **Contextual Embeddings (Transformer-based):** Utilizing models like BERT to extract embeddings where the vector for a word changes based on its surrounding context (e.g., "bank" of a river vs. financial "bank").
130. **Text Cleaning (Regex):** Using Regular Expressions for aggressive text preprocessing: stripping HTML tags, removing URLs, handling emojis, and stripping punctuation.
131. **Spell Checking and Correction:** Using distance algorithms or probabilistic models to autocorrect misspelled words before tokenization to reduce vocabulary fragmentation.
132. **Padding and Truncating:** In deep learning NLP pipelines, ensuring all text sequences are the exact same length by adding zero-tokens (padding) or cutting off long text (truncating).
133. **OOV (Out-of-Vocabulary) Tokens:** Standardizing preprocessing by explicitly mapping any word not seen during training to a special <UNK> token to handle unexpected production data gracefully.
134. **Text Augmentation (Synonym Replacement):** Artificially expanding text datasets by randomly replacing words with their WordNet synonyms.
135. **Text Augmentation (Back-Translation):** Translating text to another language and then back to the original language to create grammatical variations of the same semantic meaning.
136. **Image Normalization:** Scaling pixel values (typically 0-255) to a [0, 1] or [-1, 1] range, or subtracting the ImageNet mean and dividing by the standard deviation for transfer learning.
137. **Image Resizing and Aspect Ratio:** Forcing all images into a fixed resolution (e.g., 224x224) using interpolation methods (bilinear, bicubic) while handling aspect ratio distortion via padding (letterboxing).
138. **Data Augmentation (Spatial Transformations):** Randomly rotating, flipping, cropping, or scaling images during pipeline loading to prevent model memorization and increase robustness.
139. **Data Augmentation (Color Jittering):** Randomly altering the brightness, contrast, saturation, and hue of images to simulate different lighting conditions.
140. **Advanced Image Augmentation (MixUp):** Generating a new image and label by taking a weighted linear combination of two randomly selected images and their one-hot encoded labels.
141. **Advanced Image Augmentation (CutMix):** Cutting a spatial patch from one image and pasting it onto another, with the target label updated proportionally to the area of the patch.
142. **Audio Pre-emphasis:** Applying a high-pass filter to raw audio waveforms to balance the frequency spectrum, amplifying high frequencies which generally have smaller magnitudes.
143. **Audio Framing and Windowing:** Slicing a continuous audio signal into short, overlapping frames (e.g., 25ms) and applying a window function (like Hamming) to prevent edge artifacts.
144. **Spectrogram Generation:** Converting 1D audio waveforms into 2D visual representations of frequencies over time using the Short-Time Fourier Transform (STFT).
145. **Mel-Spectrograms:** Scaling the frequency axis of a spectrogram to the Mel Scale, which mimics the non-linear human perception of pitch (more resolution at low frequencies).
146. **MFCC (Mel-Frequency Cepstral Coefficients):** Applying a Discrete Cosine Transform to a Mel-spectrogram to extract highly compressed, decorrelated features commonly used in speech recognition.
147. **Audio Augmentation (Time Stretching):** Slightly speeding up or slowing down audio samples without changing the pitch to create synthetic training data.
148. **Audio Augmentation (Pitch Shifting):** Altering the pitch of the audio up or down while keeping the duration constant.
149. **Background Noise Injection:** Randomly mixing varying levels of static or background environmental noise into clean audio arrays to improve model robustness.
150. **Bounding Box Scaling:** In object detection preprocessing, mathematically adjusting bounding box coordinate labels when the underlying image is resized or cropped.
151. **Curse of Dimensionality:** The phenomenon where as the number of features increases, the feature space becomes exponentially sparse, degrading distance metrics and causing severe overfitting.
152. **Principal Component Analysis (PCA):** A linear dimensionality reduction technique that finds orthogonal axes (Principal Components) that capture the maximum variance in the data.
153. **Variance Explained in PCA:** Preprocessing data by retaining only the number of principal components necessary to capture a target threshold (e.g., 95%) of the total dataset variance.
154. **Scaling Requirement for PCA:** PCA is highly sensitive to the scale of input features; data must be standard-scaled (mean=0, variance=1) prior to PCA application.
155. **Truncated SVD (Singular Value Decomposition):** A variant of PCA that works directly on sparse matrices (like TF-IDF matrices) without needing to dense-ify them, commonly used in NLP (Latent Semantic Analysis).
156. **Kernel PCA:** An extension of PCA using kernel methods (e.g., RBF, Polynomial) to perform non-linear dimensionality reduction by mapping data into higher-dimensional spaces before projecting it down.
157. **Independent Component Analysis (ICA):** A statistical technique aiming to decompose a multivariate signal into additive subcomponents that are maximally statistically independent (often used in signal processing like EEG).
158. **Factor Analysis:** A generative model that assumes observed variables are linear combinations of a few underlying, unobserved latent variables (factors) plus specific noise.
159. **t-SNE (t-Distributed Stochastic Neighbor Embedding):** A powerful non-linear technique specifically designed for transforming high-dimensional data into 2D or 3D for visualization; rarely used as a direct input for models.
160. **UMAP (Uniform Manifold Approximation and Projection):** A modern, fast non-linear dimensionality reduction technique that preserves both local and global data structures better than t-SNE, increasingly used in ML pipelines.
161. **Linear Discriminant Analysis (LDA) as Preprocessing:** A supervised dimensionality reduction method that finds the feature subspace that maximizes class separability; requires target labels.
162. **Autoencoders for Dimensionality Reduction:** Training neural networks with a narrow "bottleneck" layer; the output of this bottleneck layer serves as a non-linear, compressed feature representation.
163. **Feature Agglomeration:** Applying hierarchical clustering algorithms to features (rather than rows) and grouping highly correlated features together into single representative features.
164. **Non-Negative Matrix Factorization (NMF):** A dimensionality reduction technique used when data is strictly non-negative (e.g., pixel intensities, text counts), resulting in easily interpretable additive parts.
165. **Random Projections:** A computationally efficient technique based on the Johnson-Lindenstrauss lemma, mapping high-dimensional data to a lower-dimensional subspace using random matrices while preserving pairwise distances.
166. **Data Leakage:** The catastrophic error of allowing information from outside the training dataset (specifically the validation/test set or future temporal data) to influence the preprocessing parameters.
167. **Fit vs. Transform:** The strict rule that preprocessing objects (scalers, imputers) must be strictly fit() only on the training data, and only transform() applied to test data.
168. **Leakage in Cross-Validation:** Performing operations like SMOTE, Target Encoding, or PCA on the entire dataset before performing cross-validation splits, invalidating the CV performance metrics.
169. **scikit-learn Pipeline (Pipeline):** A sequential object that chains together multiple preprocessing steps and a final estimator, guaranteeing that preprocessing logic is sequentially executed without leakage during cross-validation.
170. **scikit-learn ColumnTransformer:** A meta-estimator that allows different preprocessing pipelines to be applied concurrently to different subsets of columns (e.g., One-Hot Encoding for categorical, Scaling for continuous).
171. **Custom Transformers:** Building custom classes extending BaseEstimator and TransformerMixin to integrate complex, proprietary business-logic data transformations directly into safe ML pipelines.
172. **Stateless vs. Stateful Preprocessing:** Stateless steps (e.g., log transformation, dropping a column) require no memory of the data. Stateful steps (e.g., standard scaling, target encoding) "learn" parameters and must be carefully managed to avoid leakage.
173. **FeatureUnion:** An older, parallel-pipeline mechanism to combine the output of multiple transformer objects into a single wide feature space (largely superseded by ColumnTransformer).
174. **Pipeline Caching (Memory):** Utilizing memory caching arguments in scikit-learn pipelines to save the state of computationally expensive preprocessing steps (like grid search with complex imputations) to avoid re-computation.
175. **Imputation inside CV Folds:** Ensuring that algorithms like MICE or KNN Imputation strictly relearn their distributions and neighbors on every single unique fold of a K-Fold cross-validation loop.
176. **Target Encoding Leakage:** The severe risk where calculating target means over the whole training set memorizes the target; mitigated strictly by inner-fold CV calculating the means.
177. **Reproducibility in Pipelines:** Using explicit random seeds (random_state) in preprocessing steps that utilize randomness (like SMOTE, Isolation Forests, randomized imputation) to ensure deterministic pipeline execution.
178. **Handling Unknown Categories in Production:** Configuring encoders (like OneHotEncoder(handle_unknown='ignore')) to gracefully drop or map to zero any novel categorical values observed during inference.
179. **Data Drift Monitoring Pre-Pipeline:** Advanced production systems track the distributional properties of incoming data before preprocessing to alert if scaling parameters or imputation statistics are severely outdated.
180. **Serialization of Pipelines:** Exporting the entire preprocessing sequence alongside the model (via pickle, joblib, or ONNX) to ensure the exact same transform logic is perfectly replicated in the deployment environment.
"""

def sanitize_filename(filename):
    """Remove illegal characters from filenames across OSes."""
    return re.sub(r'[\\/*?:"<>|]', "-", filename)

# 3. Parse the text and generate files
# Split by newline
lines = raw_text.strip().split('\n')
count = 0

for line in lines:
    line = line.strip()
    
    # Check if the line starts with a number
    if not line or not line[0].isdigit():
        continue
    
    # Split the number from the rest of the text
    parts = line.split('. ', 1)
    if len(parts) != 2:
        continue
        
    num_str = parts[0]
    rest_of_line = parts[1]
    
    # Extract the title and the description
    # Pattern looks for text between ** **, optionally followed by a colon
    try:
        title_split = rest_of_line.split('**', 2)
        if len(title_split) >= 3:
            # Clean up the title (remove colons and whitespace)
            title = title_split[1].replace(':', '').strip()
            
            # Clean up description (remove leading colons or spaces)
            desc = title_split[2].strip()
            if desc.startswith(':'):
                desc = desc[1:].strip()
        else:
            # Fallback if asterisks formatting is weird
            title = f"Topic {num_str}"
            desc = rest_of_line
            
    except Exception as e:
        print(f"Failed parsing line: {line}\nError: {e}")
        continue

    # Format output filename (e.g., 001 - Target Encoding.md)
    safe_title = sanitize_filename(title)
    file_name = f"{int(num_str):03d} - {safe_title}.md"
    file_path = os.path.join(target_dir, file_name)
    
    # Write to Markdown file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\n")
        f.write(f"{desc}\n")
        
    count += 1

print(f"✅ Successfully created {count} markdown files in '{target_dir}'!")