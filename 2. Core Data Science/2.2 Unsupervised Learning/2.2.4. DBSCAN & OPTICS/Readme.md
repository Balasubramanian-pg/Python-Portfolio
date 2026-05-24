# Study Note: Density-Based Clustering (DBSCAN & OPTICS)

Density-based clustering algorithms identify clusters as continuous, high-density regions in the feature space separated by regions of low density. Unlike centroid-based methods (such as K-Means), density-based algorithms do not assume spherical cluster shapes and do not require the number of clusters $K$ to be specified a priori.

---

## 1. Formal Mathematical Definitions of DBSCAN

**DBSCAN** (Density-Based Spatial Clustering of Applications with Noise) relies on two primary user-defined hyperparameters:
*   $\epsilon \in \mathbb{R}^+$ (Epsilon): The radius defining the neighborhood of a point.
*   $\text{MinPts} \in \mathbb{Z}^+$: The minimum number of points required to form a dense region.

Let $X = \{\mathbf{x}_1, \mathbf{x}_2, \dots, \mathbf{x}_N\}$ be a dataset where each point $\mathbf{x}_i \in \mathbb{R}^d$, and let $d(\mathbf{x}_i, \mathbf{x}_j)$ denote a metric (typically Euclidean distance).

### Definition 1: $\epsilon$-Neighborhood
The $\epsilon$-neighborhood of a point $\mathbf{x} \in X$, denoted as $N_{\epsilon}(\mathbf{x})$, is the set of points situated within distance $\epsilon$ of $\mathbf{x}$:
$$N_{\epsilon}(\mathbf{x}) = \{ \mathbf{y} \in X \mid d(\mathbf{x}, \mathbf{y}) \le \epsilon \}$$

### Definition 2: Core, Border, and Noise Points
A point $\mathbf{x}$ is classified based on the cardinality of its neighborhood $|N_{\epsilon}(\mathbf{x})|$:
1.  **Core Point:** $\mathbf{x}$ is a core point if it contains at least $\text{MinPts}$ in its neighborhood:
    $$|N_{\epsilon}(\mathbf{x})| \ge \text{MinPts}$$
2.  **Border Point:** $\mathbf{x}$ is a border point if it is not a core point, but lies within the $\epsilon$-neighborhood of a core point $\mathbf{y}$:
    $$|N_{\epsilon}(\mathbf{x})| < \text{MinPts} \quad \text{and} \quad \exists \, \mathbf{y} \in X \text{ such that } \mathbf{x} \in N_{\epsilon}(\mathbf{y}) \text{ where } \mathbf{y} \text{ is a core point.}$$
3.  **Noise Point (Outlier):** $\mathbf{x}$ is a noise point if it is neither a core point nor a border point.

```text
       * (Border Point)
      /
     / \ \epsilon
    /   \
   *     o (Core Point)
        / \
       /   * (Border Point)
      
                 * (Noise Point - Isolated)
```

---

### Definition 3: Direct Density-Reachability
A point $\mathbf{p}$ is *directly density-reachable* from a point $\mathbf{q}$ with respect to $\epsilon$ and $\text{MinPts}$ if:
1.  $\mathbf{p} \in N_{\epsilon}(\mathbf{q})$
2.  $\mathbf{q}$ is a core point.

*Note: This relation is asymmetric if one point is a core point and the other is a border point.*

### Definition 4: Density-Reachability
A point $\mathbf{p}$ is *density-reachable* from a point $\mathbf{q}$ if there exists a chain of points $\mathbf{p}_1, \mathbf{p}_2, \dots, \mathbf{p}_n \in X$ with $\mathbf{p}_1 = \mathbf{q}$ and $\mathbf{p}_n = \mathbf{p}$ such that $\mathbf{p}_{i+1}$ is directly density-reachable from $\mathbf{p}_i$ for all $i \in \{1, \dots, n-1\}$.

### Definition 5: Density-Connectivity
A point $\mathbf{p}$ is *density-connected* to a point $\mathbf{q}$ if there exists an intermediate point $\mathbf{o} \in X$ such that both $\mathbf{p}$ and $\mathbf{q}$ are density-reachable from $\mathbf{o}$.

*Note: Unlike reachability, density-connectivity is symmetric and defines the actual structure of a cluster.*

```text
  p <--- (density-reachable) --- o --- (density-reachable) ---> q
  \_____________________________________________________________/
                     Density-Connected (Symmetric)
```

### Definition 6: Cluster
A cluster $C \subseteq X$ is a non-empty subset satisfying two conditions:
1.  **Maximality:** If $\mathbf{p} \in C$ and $\mathbf{q}$ is density-reachable from $\mathbf{p}$, then $\mathbf{q} \in C$.
2.  **Connectivity:** For all $\mathbf{p}, \mathbf{q} \in C$, $\mathbf{p}$ is density-connected to $\mathbf{q}$.

---

## 2. The DBSCAN Algorithm

DBSCAN discovers clusters by propagating connectivity starting from core points:

1.  **Initialization:** Mark all points as unvisited.
2.  **Core Check:** For each unvisited point $\mathbf{x}_i \in X$:
    *   Compute $N_{\epsilon}(\mathbf{x}_i)$.
    *   If $|N_{\epsilon}(\mathbf{x}_i)| \ge \text{MinPts}$, mark $\mathbf{x}_i$ as a core point and initiate a new cluster $C$.
    *   Otherwise, mark $\mathbf{x}_i$ temporarily as noise (it may be updated to a border point later).
3.  **Expansion:** If $\mathbf{x}_i$ is a core point, add all points in $N_{\epsilon}(\mathbf{x}_i)$ to a queue $Q$. For each point $\mathbf{p} \in Q$:
    *   If $\mathbf{p}$ is marked as noise, change its status to a border point of cluster $C$.
    *   If $\mathbf{p}$ is unvisited:
        *   Mark $\mathbf{p}$ as visited and assign it to cluster $C$.
        *   Compute $N_{\epsilon}(\mathbf{p})$. If $\mathbf{p}$ is a core point, append all points in $N_{\epsilon}(\mathbf{p})$ to $Q$.
4.  **Iteration:** Repeat until all points in the dataset are marked as visited.

---

## 3. Dealing with Multi-Density Data: OPTICS

A major limitation of DBSCAN is its reliance on a single global density threshold ($\epsilon$). In datasets containing clusters of varying densities, a single choice of $\epsilon$ will either merge dense clusters or classify sparser clusters as noise.

**OPTICS** (Ordering Points To Identify the Clustering Structure) generalizes DBSCAN to handle multi-density datasets by creating a linear ordering of database points based on their density structure [1].

### Mathematical Foundation of OPTICS

OPTICS introduces two mathematical metrics: **Core Distance** and **Reachability Distance** [1].

#### Definition 7: Core Distance
The core distance of a point $\mathbf{p}$ is the minimum distance $\epsilon'$ ($\epsilon' \le \epsilon$) such that $\mathbf{p}$ would be classified as a core point:

$$\text{core-dist}_{\epsilon, \text{MinPts}}(\mathbf{p}) = \begin{cases} \text{UNDEFINED} & \text{if } |N_{\epsilon}(\mathbf{p})| < \text{MinPts} \\ d(\mathbf{p}, \mathbf{n}_{\text{MinPts}}) & \text{otherwise} \end{cases}$$

where $\mathbf{n}_{\text{MinPts}}$ is the $\text{MinPts}$-nearest neighbor of $\mathbf{p}$.

#### Definition 8: Reachability Distance
The reachability distance of a point $\mathbf{p}$ relative to a core point $\mathbf{o}$ is the maximum of the core distance of $\mathbf{o}$ and the actual distance between $\mathbf{p}$ and $\mathbf{o}$ [1]:

$$\text{reachability-dist}_{\epsilon, \text{MinPts}}(\mathbf{p}, \mathbf{o}) = \begin{cases} \text{UNDEFINED} & \text{if } \text{core-dist}_{\epsilon, \text{MinPts}}(\mathbf{o}) \text{ is UNDEFINED} \\ \max(\text{core-dist}_{\epsilon, \text{MinPts}}(\mathbf{o}), d(\mathbf{o}, \mathbf{p})) & \text{otherwise} \end{cases}$$

```text
                  p 
                 / 
                /   Actual Distance d(o, p)
               /
      [      o      ]  <-- Core-Distance circle of o
```

### The Reachability Plot
OPTICS processes points sequentially, always choosing the next point that has the minimum reachability distance from the currently processed points. 

Plotting the reachability distance of each point in the resulting order yields a **Reachability Plot**. Valleys in this plot represent high-density clusters, while peaks represent boundaries or noise points. By drawing a horizontal line across this plot (corresponding to a specific $\epsilon$), one can extract DBSCAN-like clusters for any density threshold.

```text
  Reachability Dist.
    ^
    |   |     |             |
    |   |     |   /\        |
    |   |__   |  /  \    /\ |
    |  /   \  |_/    \  /  \|
    | /     \ /       \/    \
    +-----------------------------> Sorted Order of Points
       Valleys = Dense Clusters
```

---

## 4. Advantages, Limitations, and Computational Complexity

### Advantages
*   **Arbitrary Shapes:** Can capture non-convex geometries (e.g., spirals, concentric rings).
*   **Robustness to Noise:** Explicitly isolates anomalies as noise points rather than forcing them into clusters.
*   **No Prior $K$ Specification:** Dynamically calculates the number of clusters based on spatial density.

### Limitations
*   **The Curse of Dimensionality:** In high-dimensional spaces ($d \gg 10$), distance metrics like Euclidean distance become concentrated, and density contrasts diminish.
*   **Boundary Point Ambiguity:** Points on the shared boundary of two dense clusters can be assigned to either cluster depending on processing order.
*   **Parameter Sensitivity:** Small changes in $\epsilon$ can lead to drastically different cluster formations.

### Computational Complexity
*   **Worst-Case Time Complexity:** $O(N^2)$ without indexing, where $N$ is the number of points, because calculating the $\epsilon$-neighborhood for every point requires pairwise distance computations.
*   **Optimized Time Complexity:** $O(N \log N)$ when using spatial index structures like $R^*$-Trees or $KD$-Trees (valid for low-to-moderate dimensions $d \le 10$).
*   **Space Complexity:** $O(N)$ to store point states, neighborhoods, and cluster labels.

---

## References

[1] M. Ankerst, M. M. Breunig, H.-P. Kriegel, and J. Sander, "OPTICS: Ordering points to identify the clustering structure," in *Proceedings of the 1999 ACM SIGMOD International Conference on Management of Data*, 1999, pp. 49–60.
