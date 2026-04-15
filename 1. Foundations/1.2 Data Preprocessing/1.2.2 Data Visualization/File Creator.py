import os
import re

# 1. Define the target directory
target_dir = r"C:\Users\balasubramanian.pg\Music\files\1. Foundations\1.2 Data Preprocessing\1.2.2 Data Visualization"

# Create the directories if they don't exist
os.makedirs(target_dir, exist_ok=True)

# 2. Paste the generated list here
raw_text = """
1. **Exploratory Data Analysis (EDA):** The process of using visual and statistical methods to understand dataset characteristics, identify patterns, and spot anomalies before formal modeling.
2. **Anscombe’s Quartet:** A set of four datasets with nearly identical simple statistical properties that appear vastly different when graphed, highlighting the necessity of visualizing data rather than relying solely on summary statistics.
3. **The Datasaurus Dozen:** A modern extension of Anscombe’s Quartet demonstrating that datasets can have the same mean, variance, and correlation but form entirely different shapes (like a dinosaur) when plotted.
4. **Preprocessing vs. Presentation Visualization:** Preprocessing visualization is quick, iterative, and meant for the data scientist to discover insights; presentation visualization is polished, annotated, and meant to communicate findings to stakeholders.
5. **Continuous vs. Discrete Data Visualization:** Continuous data (e.g., height, temperature) is typically visualized using continuous axes (e.g., histograms, line plots), while discrete data (e.g., categories, counts) uses distinct visual markers (e.g., bar charts).
6. **Data-Ink Ratio:** A principle by Edward Tufte suggesting that the majority of ink used in a graphic should represent data, minimizing non-essential elements (chartjunk) to make EDA faster and clearer.
7. **Overplotting:** A common issue in large datasets where data points overlap excessively on a plot, hiding the true distribution and requiring techniques like transparency (alpha) or jittering to resolve.
8. **Small Multiples (Trellis/Facet Displays):** A series of similar graphs or charts using the same scale and axes, allowing for quick visual comparisons across different subsets or categories of data.
9. **Dimensionality in Visualization:** The human eye easily perceives 2D and 3D space; visualizing >3 dimensions requires mapping extra variables to color, size, shape, or using dimensionality reduction techniques.
10. **Visualizing Graphical Integrity:** Ensuring axes start at appropriate baselines (often zero for bar charts) and that scaling is proportional, preventing misleading interpretations during data cleaning.
11. **Histograms:** The foundational plot for continuous data, partitioning a variable into continuous bins and representing the frequency of observations in each bin with bars.
12. **Bin Size Selection:** The choice of bin width drastically alters a histogram's shape; too few bins obscure data structure, while too many bins create a noisy plot. 
13. **Kernel Density Estimation (KDE):** A non-parametric way to estimate the probability density function of a continuous variable, producing a smooth curve that represents the data distribution.
14. **Box Plots (Box-and-Whisker):** A standardized way of displaying the distribution of data based on a five-number summary: minimum, first quartile, median, third quartile, and maximum.
15. **Violin Plots:** A combination of a box plot and a KDE plot, showing the summary statistics while also revealing the full density distribution of the data on both sides.
16. **Rug Plots:** A plot that displays individual data points as small tick marks along an axis, often combined with KDEs or histograms to show exact data locations.
17. **Quantile-Quantile (Q-Q) Plots:** A probability plot comparing the quantiles of two distributions (usually the data's distribution against a theoretical normal distribution) to check for normality.
18. **Empirical Cumulative Distribution Function (eCDF):** A step function that visualizes the proportion of data points less than or equal to a certain value, useful for exact percentile readings without binning bias.
19. **Dot Plots (Continuous):** Plots that represent individual observations as dots along a single axis, highly effective for small continuous datasets where histograms are too coarse.
20. **Visualizing Skewness:** Visual confirmation of asymmetry in a distribution; right-skewed data has a long right tail, while left-skewed data has a long left tail.
21. **Visualizing Kurtosis:** Visualizing the "tailedness" of a distribution; leptokurtic distributions have sharp peaks and fat tails, while platykurtic distributions are flatter.
22. **Visualizing Bimodal/Multimodal Distributions:** Identifying datasets with two or more distinct peaks via KDEs or histograms, which usually indicates the presence of mixed sub-populations requiring feature engineering.
23. **Log-Scaled Axes:** Applying a logarithmic scale to an axis to visualize highly skewed data (e.g., income, website traffic) so that small and large values can be examined simultaneously.
24. **Frequency Polygons:** Similar to histograms, but using lines connecting the midpoints of bins instead of bars, allowing multiple distributions to be overlaid on a single plot cleanly.
25. **Strip Plots (1D Scatter):** A scatter plot along a single axis, representing continuous values. Overlapping points are often separated using a small amount of random noise (jitter).
26. **Bar Charts:** The standard visualization for categorical variables, using the length of rectangular bars to represent the frequency or proportion of each category.
27. **Count Plots:** A specific type of bar chart that strictly displays the count of observations in each categorical bin.
28. **Pie Charts:** Circular charts divided into sectors to illustrate numerical proportion. Generally discouraged in EDA because humans struggle to compare angles accurately.
29. **Donut Charts:** A variation of a pie chart with a blank center. While slightly easier to read than pie charts by focusing the eye on arc length, bar charts remain preferred for EDA.
30. **Waffle Charts:** A grid-based visualization representing proportions (often 10x10 squares), providing a clearer alternative to pie charts for visualizing percentages.
31. **Treemaps:** A method for displaying hierarchical data using nested rectangles, where the area of each rectangle corresponds to its value or frequency.
32. **Pareto Charts:** A bar chart sorted in descending order of frequency, combined with an overlaid line graph showing the cumulative total, useful for identifying the "vital few" categories.
33. **Word Clouds:** A visual representation of text data where word size correlates with frequency; useful for a quick, albeit imprecise, glance at dominant categorical text values.
34. **Lollipop Charts:** A variation of a bar chart utilizing a line with a dot at the end, providing a cleaner, higher data-ink ratio when there are many categories.
35. **Radial Bar Charts:** Bar charts plotted on a polar coordinate system; though aesthetically pleasing, they distort data perception and are generally avoided in rigorous preprocessing.
36. **Scatter Plots:** The primary tool for visualizing the relationship between two continuous variables, plotting one variable on the x-axis and the other on the y-axis.
37. **Alpha Blending:** Adjusting the transparency of points in a scatter plot to reveal the density of overlapping points rather than a solid mass of color.
38. **Hexbin Plots:** A bivariate histogram that divides the scatter plot space into hexagonal bins, coloring them based on the number of points inside, solving severe overplotting.
39. **2D Density Plots (2D KDE):** Contour plots that represent the density of data points in a 2D space, displaying smooth topographical lines of data concentration.
40. **Contour Plots:** Used to represent a 3D surface on a 2D plane using contour lines, useful when a third continuous variable is predicted by two continuous features.
41. **Line Plots:** Used primarily when the x-axis represents a continuous, ordered variable (like time or distance) to show trends and connections between individual observations.
42. **Bubble Charts:** A scatter plot where a third continuous variable dictates the size of the markers, allowing 3D data to be viewed in two dimensions.
43. **Marginal Histograms:** A scatter plot accompanied by univariate histograms along the x and y axes, providing simultaneous viewing of bivariate relationships and univariate distributions.
44. **Jointplots:** A composite visualization (common in Seaborn) that combines bivariate scatter/hex/KDE plots with their respective univariate marginal plots.
45. **Regression Plots (lmplot):** A scatter plot overlaid with a linear regression line and a translucent confidence interval band to visually assess linear relationships.
46. **Correlograms:** A visual representation of a correlation matrix, usually displaying scatter plots for multiple variables along with their correlation coefficients.
47. **Trend Lines (LOESS/LOWESS):** Locally weighted scatterplot smoothing curves added to scatter plots to reveal non-linear trends in noisy data.
48. **Visualizing Homoscedasticity:** Inspecting a scatter plot (often residuals vs. fitted values) to ensure the variance of a variable is consistent across the range of another variable.
49. **Visualizing Heteroscedasticity:** Identifying a "cone" or "fan" shape in a scatter plot, indicating that the variance changes across values, often prompting a data transformation.
50. **Distance Matrices:** Heatmaps that visualize the pairwise distances (e.g., Euclidean, Manhattan) between data points, useful in clustering preprocessing.
51. **Grouped Box Plots:** Displaying multiple box plots side-by-side to compare the distribution of a continuous variable across different categories.
52. **Grouped Violin Plots:** Displaying violin plots side-by-side to compare both summary statistics and exact density shapes across distinct categorical groups.
53. **Swarm Plots:** A categorical scatter plot where points are adjusted along the categorical axis so they don't overlap, revealing the true spread and count of data.
54. **Point Plots:** Plots that display point estimates (like the mean) and confidence intervals as dots and error bars, with lines connecting them to show trends across categories.
55. **Ridge Plots (Joyplots):** Partially overlapping density plots for different categories, creating a 3D mountain-range effect that is highly space-efficient for comparing many groups.
56. **Overlaid KDE Plots:** Plotting multiple KDE curves on the exact same axes (distinguished by color) to directly compare continuous distributions between a few categories.
57. **Facet Grids (Categorical):** Splitting data by category into separate subplots within a grid, allowing for clean comparison without overlapping lines or points.
58. **Strip Plots with Jitter:** A categorical scatter plot where points are given slight random horizontal shifts (jitter) to prevent them from stacking directly on top of each other.
59. **Bar Charts with Error Bars:** Standard bar charts representing the mean of a continuous variable per category, combined with error bars to show variance, standard deviation, or confidence intervals.
60. **Notched Box Plots:** Box plots featuring a narrowing "notch" around the median; if the notches of two boxes do not overlap, it suggests their medians are significantly different.
61. **Boxen Plots (Letter-Value Plots):** An advancement of the box plot optimized for large datasets, drawing successive, narrower boxes to represent further quantiles beyond the standard IQR.
62. **Waterfall Charts:** A visualization showing how an initial continuous value is affected by a series of positive and negative categorical intermediate values, leading to a final value.
63. **Radar Charts (Spider Charts):** A graphical method of displaying multivariate data in the form of a 2D chart of three or more quantitative variables represented on axes starting from the same point.
64. **Candlestick Charts:** Specialized visualizations used in finance to show the open, high, low, and close prices for a continuous variable (price) over discrete categories (time intervals).
65. **Raincloud Plots:** A comprehensive, multi-layered plot combining a half-violin plot (the 'cloud'), a box plot, and a jittered strip plot (the 'rain') for maximum statistical transparency.
66. **Stacked Bar Charts:** A bar chart where categorical sub-groups are placed on top of one another to show the total size of the group as well as the sub-group breakdown.
67. **Grouped (Clustered) Bar Charts:** A bar chart where sub-groups are placed side-by-side, making it easier to compare the absolute values of specific sub-groups across main categories.
68. **100% Stacked Bar Charts:** A stacked bar chart where all bars are scaled to equal the same height (100%), explicitly visualizing the relative percentage of sub-groups within categories.
69. **Mosaic Plots (Marimekko Charts):** A graphical representation of a contingency table where both the x and y axes are scaled proportionally to category frequencies.
70. **Cross-tabulation Heatmaps:** Using a matrix to visualize the frequency of occurrences between two categorical variables, mapping higher frequencies to darker or hotter colors.
71. **Sankey Diagrams:** A flow diagram in which the width of the arrows is proportional to the flow quantity, excellent for showing how data transitions from one categorical state to another.
72. **Alluvial Diagrams:** A specific type of Sankey diagram used to represent changes in network structure over time or multiple categorical variables.
73. **Chord Diagrams:** A circular visualization that displays inter-relationships and flows between categorical entities, with links connecting entities along the circle's perimeter.
74. **Network Graphs:** Visualizing entities (nodes) and their categorical relationships (edges), used heavily in graph data preprocessing and social network analysis.
75. **Dumbbell Plots:** Also known as connected dot plots, used to highlight the difference (gap) between two categories across various metrics.
76. **Pairplots (Scatterplot Matrices):** A grid of scatter plots showing all bivariate relationships in a dataset simultaneously, with the diagonal showing univariate distributions.
77. **3D Scatter Plots:** Adding a z-axis to a scatter plot to visualize three continuous variables, though they often require interactive rotation to be fully understood.
78. **Parallel Coordinates:** A visualization where multiple vertical axes represent different features, and individual data points are represented as lines connecting across the axes.
79. **Andrews Curves:** A technique for visualizing high-dimensional data by mapping each observation to a continuous mathematical function (Fourier series) plotted over a defined range.
80. **RadViz:** A non-linear multidimensional visualization where features are mapped uniformly around a circle, and data points are placed inside based on "spring tension" tied to feature values.
81. **Correlation Heatmaps:** A 2D matrix visualizing the Pearson, Spearman, or Kendall correlation coefficients between all pairs of continuous variables using a diverging color scale.
82. **Clustermaps:** A correlation heatmap paired with hierarchical clustering dendrograms on the rows and columns, automatically grouping highly correlated variables together.
83. **Bubble Charts (Multivariate):** Using the x-axis, y-axis, bubble size, and bubble color to simultaneously visualize four different continuous or categorical features.
84. **Trellis Displays (Multivariate Faceting):** Creating a grid of 2D plots (like scatter plots) where rows represent one categorical variable and columns represent another.
85. **PCA Biplots:** A visualization resulting from Principal Component Analysis, displaying both the reduced data points (scores) and the original variables (loadings) in a 2D space.
86. **t-SNE Visualization:** Plotting the 2D or 3D output of t-Distributed Stochastic Neighbor Embedding, a non-linear dimensionality reduction technique excellent for visual clustering of complex data.
87. **UMAP Visualization:** Uniform Manifold Approximation and Projection plots; similar to t-SNE but faster and better at preserving global data structure alongside local clustering.
88. **Glyph Plots (e.g., Chernoff Faces):** Representing multivariate data by mapping variables to features of a shape or symbol (like facial features); historically notable, though rarely used in modern pipelines.
89. **3D Contour Plots:** Extending contour lines into 3D space to show the intersection and interactions of three continuous variables.
90. **Multi-level Treemaps:** Using treemaps to show 3+ levels of categorical hierarchy simultaneously by nesting boxes within boxes within boxes.
91. **Missingno Library:** A dedicated Python library offering specific tools for the visualization of missing data behavior and patterns in pandas DataFrames.
92. **Missingness Matrix:** A dense grid (sparkline style) where data is black and missing values are white, instantly revealing where gaps occur across all features and observations.
93. **Missingness Bar Chart:** A simple univariate bar chart showing the total count or percentage of non-null values for each feature in the dataset.
94. **Missingness Heatmap:** A correlation heatmap specifically showing the nullity correlation: how strongly the presence or absence of one variable affects the presence of another.
95. **Missingness Dendrogram:** A tree diagram that hierarchically clusters features based on the similarity of their missing data patterns.
96. **Shadow Matrices:** A technique where missing values are replaced by a boolean flag (True/False for missingness), which is then visualized against other features to check for missingness bias.
97. **Visualizing MCAR (Missing Completely At Random):** Using shadow matrices to show that the distribution of missing values has absolutely no relationship to any other variables in the dataset.
98. **Visualizing MAR (Missing At Random):** Using visualizations to prove that the missingness in one variable can be explained or predicted by the observed values of other variables.
99. **Visualizing MNAR (Missing Not At Random):** Recognizing patterns where the missingness is related to the unobserved value itself (often requires domain knowledge, difficult to purely visualize).
100. **Highlighting Imputed Values:** Plotting data post-imputation and using color or markers to distinguish between original data points and algorithmically imputed data points.
101. **Pre- vs. Post-Imputation KDE Plots:** Overlaying the density curve of a variable before missing value imputation and after, ensuring the imputation didn't severely warp the natural distribution.
102. **Margin Plots:** Scatter plots that include missing data points drawn on the margins (axes) to see if missing values in one variable are clustered at specific ranges of the other variable.
103. **Bipartite Graphs for Missingness:** Modeling rows and columns as nodes in a graph to visualize complex missingness networks in highly sparse datasets.
104. **Nullity Correlation Thresholding:** Filtering a missingness heatmap to only show correlations above a certain threshold (e.g., > 0.5) to quickly find variables that are co-missing.
105. **Temporal Missing Data Visualization:** Using timeline plots to see if missing data occurs in sequential blocks (e.g., sensor failure periods) rather than randomly.
106. **Box Plot Whiskers (IQR Method):** Visually identifying outliers as any dots falling outside the "whiskers" of a box plot, which are typically calculated as 1.5 * Interquartile Range (IQR).
107. **Scatter Plot Outliers:** Visually identifying points that fall far away from the main cluster or expected trendline in a bivariate continuous space.
108. **Z-Score Visualization:** Plotting normalized data and drawing strict vertical/horizontal lines at Z=3 and Z=-3 to visually isolate statistically significant univariate outliers.
109. **Isolation Forest Visualizations:** Plotting the anomaly scores generated by an Isolation Forest algorithm as a color gradient overlaid on a scatter plot to highlight predicted outliers.
110. **DBSCAN Clustering for Noise:** Visualizing the output of DBSCAN where core/boundary points are colored by cluster, and outlier/noise points are marked with distinct black crosses.
111. **Cook’s Distance Plots:** A stem plot or scatter plot used in regression preprocessing to visualize the influence of individual data points; points above a certain threshold are highly influential outliers.
112. **Mahalanobis Distance Plots:** Visualizing the multi-dimensional distance of points from the mean of the dataset, effectively spotting multivariate outliers that univariate plots miss.
113. **Time Series Spikes:** Plotting a continuous variable over time to instantly spot transient spikes or drops (anomalies) that deviate from rolling averages.
114. **Histogram Long Tails:** Spotting extreme values by noticing a histogram with a massive x-axis range but only invisible, microscopic bars at the far ends.
115. **Q-Q Plot Deviations:** Identifying outliers by looking for points at the extreme top-right or bottom-left of a Q-Q plot that curve sharply away from the theoretical straight line.
116. **Local Outlier Factor (LOF) Visualization:** Using bubble charts where the size of the bubble corresponds to the LOF score, making local anomalies (anomalies relative to their neighborhood) visually pop.
117. **Residual Plots:** Plotting the residuals (errors) of a preliminary model against predicted values to spot outliers that the baseline model utterly fails to capture.
118. **Leverage vs. Residual Plots:** A diagnostic plot combining leverage (how extreme an x-value is) and residual (how extreme the y-value is) to spot dangerous outliers that pull regression lines.
119. **Control Charts (UCL/LCL):** Time series plots featuring an Upper Control Limit and Lower Control Limit, used heavily in industrial data preprocessing to spot processes going out of bounds.
120. **Extreme Value Analysis (EVA) Visualization:** Specialized plots like the Return Level plot to assess the probability of extreme events occurring in tail distributions.
121. **Pre/Post Log Transformation:** Placing two histograms side-by-side to show how a log transform converts a heavily right-skewed distribution into a more normal, bell-shaped distribution.
122. **Visualizing Box-Cox/Yeo-Johnson Transforms:** Using Q-Q plots to visually verify that power transformations have successfully stabilized variance and coerced data toward normality.
123. **Visualizing Standard Scaling (Z-score):** Side-by-side scatter plots showing that the spatial relationship of points remains identical, but the axes have been shifted to mean=0 and variance=1.
124. **Visualizing Min-Max Scaling:** Showing how the distribution shape is perfectly preserved while the x-axis limits are strictly squashed to a [0, 1] range.
125. **Visualizing Robust Scaling:** Demonstrating how scaling using medians and quantiles handles datasets with extreme outliers better than standard scaling, visualized via box plots.
126. **Visualizing Quantile Transformation:** Showing how this non-linear transformation forcibly maps an arbitrary distribution into a perfect uniform or standard normal distribution.
127. **Power Transformer Effects:** Comparing raw skewed data vs. power-transformed data using overlaid KDE plots to verify preprocessing success.
128. **Binarization Visualization:** Showing a histogram of continuous data alongside a bar chart of the resulting 0s and 1s after applying a specific threshold.
129. **Discretization/Binning Visualization:** Plotting continuous data with vertical lines indicating bin boundaries, alongside a bar chart of the newly created categorical bins.
130. **Visualizing Clipping/Winsorizing:** Using histograms to show how capping extreme values results in large artificial "spikes" at the designated upper and lower percentile limits.
131. **Polynomial Features Visualization:** Visualizing how mapping a 1D feature to 2D (e.g., x and x^2) allows a previously non-linear relationship to be separated by a linear plane.
132. **Moving Average Smoothing Viz:** Overlaying a raw, noisy time-series line plot with a thicker, smoother line representing a rolling mean transformation.
133. **Differencing in Time Series Viz:** Plotting raw non-stationary data next to its first-order difference to visually confirm the removal of trends and achievement of stationarity.
134. **Seasonal Decomposition Plots:** A 4-panel plot showing the original time series, its extracted Trend, its extracted Seasonality, and the remaining Residual noise.
135. **Target Encoding Visualization:** Plotting original categorical strings against the newly mapped continuous target-mean values to ensure the encoding logic visually makes sense.
136. **Feature Importance Bar Charts:** Extracting the feature_importances_ attribute from tree-based models (e.g., Random Forest) and plotting them as a sorted horizontal bar chart.
137. **SHAP Value Summary Plots:** A dense dot plot showing how high or low values of every feature positively or negatively impact the target variable's prediction.
138. **SHAP Dependence Plots:** A scatter plot of a single feature's values versus its SHAP values, visualizing non-linear effects and interactions with a second feature (via color mapping).
139. **SHAP Force Plots:** Interactive, single-prediction visualizations showing which features are "pushing" the prediction higher and which are "pushing" it lower.
140. **Permutation Importance Boxplots:** Visualizing the drop in model performance when a feature's values are randomly shuffled, plotted as boxplots over multiple cross-validation folds.
141. **Recursive Feature Elimination (RFE) Curves:** A line plot showing the number of features retained on the x-axis and model performance on the y-axis, highlighting the optimal number of features.
142. **Lasso Regression Coefficient Paths:** A line plot showing how feature coefficients shrink to exactly zero as the L1 regularization penalty (alpha) increases, acting as visual feature selection.
143. **Scree Plots (PCA):** A line plot showing the fraction of total variance explained by each principal component, used to find the "elbow" where adding components provides diminishing returns.
144. **Cumulative Explained Variance Plots:** A step plot accumulating the variance from a PCA scree plot, showing how many principal components are needed to reach a target variance (e.g., 90%).
145. **Loading Plots (PCA):** A plot visualizing the correlation of original variables with the first two principal components, showing how features group together in the new vector space.
146. **Mutual Information Bar Plots:** Visualizing the mutual information scores between each feature and the target, indicating both linear and non-linear dependencies.
147. **Chi-Square Scores Visualization:** Using bar charts to visualize the highest scoring categorical features when tested against a categorical target variable.
148. **ANOVA F-value Visualization:** Plotting the F-statistic of continuous features against a categorical target to see which features best separate the classes.
149. **Volcano Plots:** A scatter plot used often in bioinformatics showing statistical significance (p-value) vs. magnitude of change (fold change), quickly identifying the most meaningful features.
150. **Feature Correlation Dendrograms:** Visualizing hierarchical clustering of features based on their correlation, useful for identifying collinear feature groups to drop.
151. **Choropleth Maps:** Visualizing aggregated data over predefined regions (e.g., states, countries) using a color gradient.
152. **Point/Dot Density Maps:** Plotting exact lat/long coordinates as dots on a map to visually assess geographical distribution, density, and clustering.
153. **Geospatial Heatmaps:** Applying a 2D KDE to geographical points to show "hotspots" of data activity independent of predefined regional borders.
154. **Hexbin Maps:** Dividing a map into a hexagonal grid and coloring hexagons based on point density, reducing overplotting in dense geographical datasets.
155. **Proportional Symbol Maps:** Placing symbols (like circles) on a map where the size of the symbol is proportional to a specific numeric feature at that location.
156. **Flow Maps:** Drawing lines between geographic coordinates to visualize movement or network connections, with line thickness representing volume.
157. **Cartograms:** Maps where the geometry of regions is distorted to be proportional to a specific variable (e.g., making high-population states physically larger on the map).
158. **Bounding Box Visualization:** Drawing min/max lat/long rectangles on a map to verify that all spatial data points fall within the expected geographical study area.
159. **Coordinate Outlier Detection:** Visually identifying incorrect GPS data (e.g., points in the middle of the ocean for land-based data) by overlaying points on a base map.
160. **Spatial Join Visualization:** Plotting points from one dataset over polygons of another dataset to verify that a spatial merge (e.g., assigning points to specific zip codes) worked correctly.
161. **Token Length Histograms:** Plotting the distribution of document lengths (number of words/tokens) to identify empty strings or massive outlier documents.
162. **N-gram Frequency Bar Charts:** Visualizing the top 20 most frequent bigrams (2 words) or trigrams (3 words) to understand common phrases in unstructured text.
163. **TF-IDF Word Clouds:** Creating word clouds where word size is dictated by Term Frequency-Inverse Document Frequency scores rather than raw counts, highlighting unique identifiers.
164. **Zipf’s Law Plots:** A log-log scatter plot of word rank vs. word frequency to verify natural language distribution and identify abnormal bot-generated text.
165. **Topic Modeling Visualization (pyLDAvis):** An interactive D3 visualization showing extracted topic clusters as circles in 2D space and bar charts of their most relevant terms.
166. **Spectrograms:** Visualizing audio data where the x-axis is time, the y-axis is frequency, and color intensity represents amplitude (loudness).
167. **Waveform Plots:** The most basic audio visualization showing amplitude over time, useful for spotting silent periods or massive audio clipping anomalies.
168. **Mel-Frequency Cepstral Coefficients (MFCCs) Heatmap:** Visualizing extracted audio features commonly used in machine learning as a 2D heatmap.
169. **Word Embedding Scatter Plots:** Visualizing complex word vectors (Word2Vec, GloVe) after PCA/t-SNE reduction to see if mathematically similar words group together visually.
170. **Stopword Distribution Plots:** Comparing the frequency of stopwords versus meaningful words to tune the strictness of text-cleaning pipelines.
171. **Sequential Color Palettes:** Using a gradient of a single color (e.g., light blue to dark blue) to represent continuous data progressing from low to high.
172. **Diverging Color Palettes:** Using two contrasting colors merging into a neutral middle (e.g., red to white to blue) to visualize data that deviates from a critical midpoint (like 0).
173. **Categorical Color Palettes:** Using visually distinct, unrelated colors to separate discrete, unordered categories.
174. **Color Blindness Accessibility:** Utilizing color palettes (like Viridis, Cividis, or ColorBrewer) that are decipherable by individuals with red-green or blue-yellow color vision deficiencies.
175. **Gestalt Principles in Visualization:** Utilizing psychological principles like Proximity, Similarity, and Enclosure to group data points naturally in the viewer's mind.
176. **Avoiding Misleading Axes:** A core EDA rule; manipulating the Y-axis limits (e.g., starting a bar chart at 50 instead of 0) visually exaggerates minor differences and compromises data integrity.
177. **Aspect Ratios (Banking to 45 Degrees):** Adjusting the width and height of a plot so that trend lines roughly follow a 45-degree angle, optimizing the human eye's ability to detect rate changes.
178. **Animation in EDA:** Using time as a visual dimension (e.g., animated scatter plots) to see how multivariate relationships evolve, though often less practical than small multiples for static reports.
179. **Interactive EDA (Plotly/Bokeh):** Generating HTML-based plots that allow panning, zooming, and hovering for exact values, dramatically speeding up anomaly investigation compared to static images.
180. **Matplotlib vs. Seaborn Context:** Matplotlib is the foundational Python engine for arbitrary plot construction, while Seaborn is a high-level wrapper specifically designed to make statistical EDA plots with minimal code.
"""

def sanitize_filename(filename):
    """Remove illegal characters from filenames across OSes."""
    return re.sub(r'[\\/*?:"<>|]', "-", filename)

# 3. Parse the text and generate files
lines = raw_text.strip().split('\n')
count = 0

for line in lines:
    line = line.strip()
    
    # Skip section headers (like ### A. Core Concepts) and empty lines
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
            # Fallback if formatting is weird
            title = f"Topic {num_str}"
            desc = rest_of_line
            
    except Exception as e:
        print(f"Failed parsing line: {line}\nError: {e}")
        continue

    # Format output filename (e.g., 001 - Exploratory Data Analysis (EDA).md)
    safe_title = sanitize_filename(title)
    file_name = f"{int(num_str):03d} - {safe_title}.md"
    file_path = os.path.join(target_dir, file_name)
    
    # Write to Markdown file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\n")
        f.write(f"{desc}\n")
        
    count += 1

print(f"✅ Successfully created {count} markdown files in '{target_dir}'!")