# Module 2.2.2: Classification and Clustering

This directory contains conceptual notes, mathematical formulations, and implementation details for **Classification** and **Clustering**. 

> **Conceptual Note:** While *Classification* is a **Supervised Learning** task (requiring labeled training data) and *Clustering* is an **Unsupervised Learning** task (working with unlabeled data), they are grouped together here to contrast how algorithms partition data spaces with and without prior knowledge of class labels.

## 1. High-Level Comparison

To understand the core differences between partitioning data with labels (classification) versus discovering structure dynamically (clustering):

| Feature | Classification (Supervised) | Clustering (Unsupervised) |
| :--- | :--- | :--- |
| **Data Requirements** | Labeled training data: $(\mathbf{x}_i, y_i)$ | Unlabeled data: $\mathbf{x}_i$ |
| **Objective** | Learn a boundary mapping inputs to predefined classes. | Group data points based on inherent similarity. |
| **Output** | Predicted discrete class label for new instances. | Cluster assignments indicating group membership. |
| **Common Algorithms** | Logistic Regression, SVM, Decision Trees, Random Forests | K-Means, Hierarchical Clustering, DBSCAN |
| **Primary Evaluation** | Accuracy, Precision, Recall, F1-Score, ROC-AUC | Silhouette Coefficient, Davies-Bouldin Index, Inertia |

## 2. Mathematical Foundations of Clustering

Clustering algorithms attempt to partition a dataset $X = \{\mathbf{x}_1, \mathbf{x}_2, \dots, \mathbf{x}_N\} \subset \mathbb{R}^d$ into $K$ groups or clusters $S = \{S_1, S_2, \dots, S_K\}$.

### A. Distance Metrics
Most clustering techniques rely on measuring distance in the feature space. Let $\mathbf{u}, \mathbf{v} \in \mathbb{R}^d$:

1.  **Euclidean Distance ($L_2$ Norm):**
    $$d(\mathbf{u}, \mathbf{v}) = \|\mathbf{u} - \mathbf{v}\|_2 = \sqrt{\sum_{j=1}^d (u_j - v_j)^2}$$

2.  **Manhattan Distance ($L_1$ Norm):**
    $$d(\mathbf{u}, \mathbf{v}) = \|\mathbf{u} - \mathbf{v}\|_1 = \sum_{j=1}^d |u_j - v_j|$$

3.  **Cosine Similarity:**
    $$\text{sim}(\mathbf{u}, \mathbf{v}) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2}$$

### B. K-Means Clustering
K-Means is a centroid-based partitioning algorithm.

#### The Optimization Objective
The objective of K-Means is to minimize the **Within-Cluster Sum of Squares (WCSS)**, also referred to as **Inertia**:
$$\arg\min_{S} \sum_{i=1}^{K} \sum_{\mathbf{x} \in S_i} \|\mathbf{x} - \mathbf{\mu}_i\|^2$$
where $\mathbf{\mu}_i$ is the mean (centroid) of the points assigned to cluster $S_i$:
$$\mathbf{\mu}_i = \frac{1}{|S_i|} \sum_{\mathbf{x} \in S_i} \mathbf{x}$$

#### Algorithmic Steps (Lloyd's Algorithm)
1.  **Initialization:** Randomly select $K$ initial centroids $\{\mathbf{\mu}_1^{(0)}, \dots, \mathbf{\mu}_K^{(0)}\}$.
2.  **Assignment Step:** Assign each data point $\mathbf{x}_j$ to the closest centroid:
    $$S_i^{(t)} = \left\{ \mathbf{x}_j : \big\|\mathbf{x}_j - \mathbf{\mu}_i^{(t)}\big\|^2 \le \big\|\mathbf{x}_j - \mathbf{\mu}_l^{(t)}\big\|^2 \quad \forall l = 1, \dots, K \right\}$$
3.  **Update Step:** Compute the new centroids based on the mean of the assigned points:
    $$\mathbf{\mu}_i^{(t+1)} = \frac{1}{|S_i^{(t)}|} \sum_{\mathbf{x} \in S_i^{(t)}} \mathbf{x}$$
4.  **Convergence:** Repeat steps 2 and 3 until centroids no longer change significantly ($\mathbf{\mu}^{(t+1)} \approx \mathbf{\mu}^{(t)}$).

### C. Hierarchical Clustering
Unlike K-Means, hierarchical clustering does not assume a fixed number of clusters $K$ from the start. It builds a tree-like diagram called a **dendrogram**.

*   **Agglomerative (Bottom-Up):** Starts with each point as its own cluster and iteratively merges the closest pairs.
*   **Divisive (Top-Down):** Starts with all points in one cluster and iteratively splits them.

#### Linkage Criteria
To merge or split clusters, we must define the distance between two *clusters* $A$ and $B$:

*   **Single Linkage (Minimum Distance):**
    $$d(A, B) = \min \{ d(\mathbf{a}, \mathbf{b}) : \mathbf{a} \in A, \mathbf{b} \in B \}$$
*   **Complete Linkage (Maximum Distance):**
    $$d(A, B) = \max \{ d(\mathbf{a}, \mathbf{b}) : \mathbf{a} \in A, \mathbf{b} \in B \}$$
*   **Average Linkage:**
    $$d(A, B) = \frac{1}{|A||B|} \sum_{\mathbf{a} \in A} \sum_{\mathbf{b} \in B} d(\mathbf{a}, \mathbf{b})$$
*   **Ward’s Linkage:** Minimizes the total within-cluster variance when merging two clusters.

### D. Density-Based Spatial Clustering of Applications with Noise (DBSCAN)
DBSCAN groups points based on density, making it capable of finding arbitrary-shaped clusters and identifying noise (outliers).

#### Key Parameters
*   $\epsilon$ (eps): The maximum radius of the neighborhood around a point.
*   $\text{MinPts}$: The minimum number of points required within the $\epsilon$-neighborhood to form a dense region.

#### Point Classification
For any point $\mathbf{x}_i$:
*   **Core Point:** Has at least $\text{MinPts}$ in its $\epsilon$-neighborhood ($N_{\epsilon}(\mathbf{x}_i)$).
*   **Border Point:** Has fewer than $\text{MinPts}$ in its neighborhood, but lies within the neighborhood of a Core Point.
*   **Noise (Outlier):** Is neither a Core Point nor a Border Point.

## 3. Evaluation Metrics for Clustering

Since ground-truth labels are generally absent in clustering, validation metrics are split into internal (no labels) and external (labels available for evaluation purposes) metrics.

### Internal Metrics (No Ground Truth)

#### 1. Silhouette Coefficient
Measures how similar an object is to its own cluster compared to other clusters. For a single point $i$:
$$s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}$$
*   $a(i)$: Mean distance between $i$ and all other points in the same cluster.
*   $b(i)$: Mean distance between $i$ and points in the nearest neighboring cluster.
*   **Interpretation:** $s(i) \in [-1, 1]$. Values close to $1$ indicate highly distinct, well-assigned clusters.

#### 2. Davies-Bouldin Index
Evaluates the average similarity between each cluster and its most similar one:
$$DB = \frac{1}{K} \sum_{i=1}^K \max_{j \neq i} \left( \frac{\sigma_i + \sigma_j}{d(\mathbf{\mu}_i, \mathbf{\mu}_j)} \right)$$
where $\sigma_i$ is the average distance of all points in cluster $i$ to their centroid. Lower DB values indicate better clustering (well-separated, compact clusters).

### External Metrics (When Ground Truth Labels $Y$ Are Available)

#### 1. Adjusted Rand Index (ARI)
Evaluates similarity between predicted cluster assignments $V$ and true class labels $U$, adjusted for chance:
$$ARI = \frac{\text{RI} - \mathbb{E}[\text{RI}]}{\max(\text{RI}) - \mathbb{E}[\text{RI}]}$$
where $\text{RI}$ is the standard Rand Index counting pairwise agreements and disagreements.

#### 2. Normalized Mutual Information (NMI)
Measures the shared information between the true labels and the cluster assignments, normalized to scale between 0 and 1:
$$NMI(U, V) = \frac{2 \cdot I(U; V)}{H(U) + H(V)}$$
where $I(U; V)$ is mutual information and $H(\cdot)$ is entropy.


## 4. Directory Structure

This section of the repository is organized as follows:

```text
2.2.2 Classification And Clustering/
├── README.md                           <-- (This file)
├── notebooks/
│   ├── 01_k_means_implementation.ipynb  <-- Step-by-step K-Means & Elbow Method
│   ├── 02_hierarchical_clustering.ipynb <-- Dendrogram analysis & linkage comparison
│   └── 03_dbscan_vs_kmeans.ipynb        <-- Evaluating density-based vs centroid clustering
└── src/
    ├── __init__.py
    ├── distance_metrics.py              <-- Custom implementations of distance functions
    └── evaluation_utils.py              <-- Helper scripts for computing Silhouette and DB index
```
