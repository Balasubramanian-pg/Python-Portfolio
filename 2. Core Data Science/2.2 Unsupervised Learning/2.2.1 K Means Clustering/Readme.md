# Study Note: K-Means Clustering

K-Means is an unsupervised, iterative partition-based clustering algorithm. Its objective is to divide $N$ observations into $K$ distinct, non-overlapping clusters where each observation belongs to the cluster with the nearest mean (centroid).

## 1. Formal Mathematical Formulation

Let $X = \{\mathbf{x}_1, \mathbf{x}_2, \dots, \mathbf{x}_N\}$ be a dataset where each instance $\mathbf{x}_i \in \mathbb{R}^d$. We seek to partition $X$ into $K$ sets $S = \{S_1, S_2, \dots, S_K\}$ to minimize the **Within-Cluster Sum of Squares (WCSS)**, also referred to as the **distortion function** or **inertia**:

$$J(S, \mathbf{M}) = \sum_{k=1}^K \sum_{\mathbf{x} \in S_k} \|\mathbf{x} - \mathbf{\mu}_k\|_2^2$$

where:
*   $\mathbf{M} = \{\mathbf{\mu}_1, \dots, \mathbf{\mu}_K\}$ is the set of cluster centroids.
*   $\mathbf{\mu}_k \in \mathbb{R}^d$ is the centroid of cluster $S_k$.
*   $\|\cdot\|_2$ denotes the standard Euclidean ($L_2$) distance.

## 2. Derivation: Why the Sample Mean Minimizes WCSS

During the update step of the algorithm, we fix the cluster assignments $S$ and solve for the optimal centroids $\mathbf{M}$. For a single cluster $S_k$, we find the centroid $\mathbf{\mu}_k$ that minimizes the local cost $J_k$:

$$J_k(\mathbf{\mu}_k) = \sum_{\mathbf{x} \in S_k} \|\mathbf{x} - \mathbf{\mu}_k\|_2^2$$

To find the minimum, we compute the gradient of $J_k$ with respect to $\mathbf{\mu}_k$ and set it to zero:

$$\nabla_{\mathbf{\mu}_k} J_k(\mathbf{\mu}_k) = \nabla_{\mathbf{\mu}_k} \sum_{\mathbf{x} \in S_k} (\mathbf{x} - \mathbf{\mu}_k)^T (\mathbf{x} - \mathbf{\mu}_k)$$

Using vector calculus rules ($\nabla_{\mathbf{z}} (\mathbf{a} - \mathbf{z})^T(\mathbf{a} - \mathbf{z}) = -2(\mathbf{a} - \mathbf{z})$):

$$\nabla_{\mathbf{\mu}_k} J_k(\mathbf{\mu}_k) = \sum_{\mathbf{x} \in S_k} -2(\mathbf{x} - \mathbf{\mu}_k) = \mathbf{0}$$

Now, expand the summation:

$$-2 \sum_{\mathbf{x} \in S_k} \mathbf{x} + 2 \sum_{\mathbf{x} \in S_k} \mathbf{\mu}_k = \mathbf{0}$$

Since $\mathbf{\mu}_k$ does not depend on the index of summation, $\sum_{\mathbf{x} \in S_k} \mathbf{\mu}_k = |S_k| \mathbf{\mu}_k$, where $|S_k|$ is the cardinality (number of elements) of the cluster:

$$\sum_{\mathbf{x} \in S_k} \mathbf{x} = |S_k| \mathbf{\mu}_k$$

$$\mathbf{\mu}_k^* = \frac{1}{|S_k|} \sum_{\mathbf{x} \in S_k} \mathbf{x}$$

**Conclusion:** The arithmetic mean of the observations assigned to a cluster is the mathematically optimal centroid under a squared Euclidean distance loss.

## 3. The K-Means++ Initialization Strategy

Standard K-means is highly sensitive to the initial placement of centroids, often getting trapped in local minima. **K-Means++** addresses this by scattering initial centroids across the feature space before running the optimization loops.

### Initialization Algorithm
1.  Choose the first centroid $\mathbf{\mu}_1$ uniformly at random from the dataset $X$.
2.  For each data point $\mathbf{x} \in X$, compute the distance $D(\mathbf{x})$ to the nearest centroid already selected:
    $$D(\mathbf{x}) = \min_{p} \|\mathbf{x} - \mathbf{\mu}_p\|_2$$
3.  Select the next centroid $\mathbf{\mu}_k$ randomly from $X$ with a probability proportional to the squared distance $D(\mathbf{x})^2$:
    $$P(\mathbf{x}_i) = \frac{D(\mathbf{x}_i)^2}{\sum_{j=1}^N D(\mathbf{x}_j)^2}$$
4.  Repeat steps 2 and 3 until $K$ centroids have been initialized.

This initialization guarantees an approximation ratio of $O(\log K)$ to the optimal clustering solution in expectation.

## 4. Selecting the Optimal Number of Clusters ($K$)

Since $K$ is a hyperparameter that must be set a priori, two primary mathematical methods are used to determine its optimal value:

### A. The Elbow Method
Plot the WCSS (inertia) as a function of $K$:
$$WCSS(K) = \sum_{k=1}^K \sum_{\mathbf{x} \in S_k} \|\mathbf{x} - \mathbf{\mu}_k\|_2^2$$

*   As $K$ increases, WCSS naturally decreases (reaching $0$ when $K=N$).
*   The optimal $K$ is typically identified at the "elbow" of the curve, representing the point of diminishing returns where adding another cluster yields a significantly smaller decrease in WCSS.

```text
  WCSS (Inertia)
    ^
    |  \
    |   \
    |    \
    |     \ 
    |      \  <-- Elbow Point (Optimal K)
    |       \_________
    |                 \________
    +-----------------------------> K (Number of Clusters)
```

### B. Silhouette Analysis
The Silhouette Coefficient evaluates how well-separated and cohesive clusters are. For a point $\mathbf{x}_i$:

$$s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}$$

Where:
*   $a(i) = \frac{1}{|S_I| - 1} \sum_{\mathbf{x}_j \in S_I, j \neq i} \|\mathbf{x}_i - \mathbf{x}_j\|_2$ (mean intra-cluster distance)
*   $b(i) = \min_{J \neq I} \frac{1}{|S_J|} \sum_{\mathbf{x}_j \in S_J} \|\mathbf{x}_i - \mathbf{x}_j\|_2$ (mean nearest-cluster distance)

We compute the average Silhouette Coefficient across all points for different values of $K$. A higher average score indicates better-defined cluster partitions.

## 5. Algorithmic Limitations and Assumptions

K-Means makes specific geometric assumptions about the data structure:

1.  **Spherical Cluster Assumption:** K-Means assumes clusters are spherical and isotropic. It struggles with elongated, non-convex, or manifold shapes (e.g., concentric circles).
2.  **Equal Cluster Variance:** The algorithm assumes clusters have similar variances and densities. It can partition highly dense clusters incorrectly when they are close to sparse ones.
3.  **Sensitivity to Feature Scaling:** Because K-Means relies on Euclidean distance, features with larger numerical ranges will dominate the objective function. **Min-Max scaling** or **Standardization (Z-score normalization)** is mathematically required:
    $$x'_{ij} = \frac{x_{ij} - \mu_j}{\sigma_j}$$
4.  **Sensitivity to Outliers:** Outliers significantly distort the calculation of the cluster mean (the centroid update), pulling the boundary away from the true dense regions. Use of median-based variants (e.g., K-Medoids) can mitigate this.
