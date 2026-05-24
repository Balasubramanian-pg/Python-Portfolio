# Study Note: Principal Component Analysis (PCA)

Principal Component Analysis (PCA) is an unsupervised linear dimensionality reduction technique. Given a high-dimensional dataset, PCA projects the data onto a lower-dimensional subspace while preserving as much of the data's variance as possible (or, equivalently, minimizing the reconstruction error).

## 1. Formal Mathematical Formulation

Let $X \in \mathbb{R}^{N \times d}$ represent a dataset containing $N$ observations, where each observation $\mathbf{x}_i \in \mathbb{R}^d$ is a row vector. 

### Preprocessing: Centering the Data
To simplify the mathematics, we must first center the dataset by subtracting the sample mean $\mathbf{\mu} = \frac{1}{N} \sum_{i=1}^N \mathbf{x}_i$ from each observation:

$$\mathbf{x}_i \leftarrow \mathbf{x}_i - \mathbf{\mu}$$

For the remainder of this derivation, we assume that the dataset is zero-mean ($\sum_{i=1}^N \mathbf{x}_i = \mathbf{0}$). 

The **Sample Covariance Matrix** $\Sigma \in \mathbb{R}^{d \times d}$ is defined as:
$$\Sigma = \frac{1}{N} X^T X = \frac{1}{N} \sum_{i=1}^N \mathbf{x}_i^T \mathbf{x}_i$$

The matrix $\Sigma$ is symmetric ($\Sigma = \Sigma^T$) and positive semi-definite ($\mathbf{v}^T \Sigma \mathbf{v} \geq 0$ for any $\mathbf{v} \in \mathbb{R}^d$).

## 2. Derivation: Maximizing Projected Variance

We seek a unit vector $\mathbf{w}_1 \in \mathbb{R}^d$ (with $\|\mathbf{w}_1\|_2 = 1$) such that when the centered data points are projected onto this direction, the variance of the projected points is maximized.

The projection of a centered data point $\mathbf{x}_i$ onto the vector $\mathbf{w}_1$ is given by the scalar projection:
$$z_i = \mathbf{x}_i \mathbf{w}_1$$

The sample mean of the projected data is zero because the original data is centered:
$$\bar{z} = \frac{1}{N} \sum_{i=1}^N \mathbf{x}_i \mathbf{w}_1 = \left(\frac{1}{N} \sum_{i=1}^N \mathbf{x}_i\right) \mathbf{w}_1 = \mathbf{0}$$

Thus, the variance of the projected data is:
$$\sigma_{\text{projected}}^2 = \frac{1}{N} \sum_{i=1}^N (z_i - \bar{z})^2 = \frac{1}{N} \sum_{i=1}^N (\mathbf{x}_i \mathbf{w}_1)^2$$

Rewriting this in vector notation:
$$\sigma_{\text{projected}}^2 = \frac{1}{N} \sum_{i=1}^N (\mathbf{w}_1^T \mathbf{x}_i^T) (\mathbf{x}_i \mathbf{w}_1) = \mathbf{w}_1^T \left( \frac{1}{N} \sum_{i=1}^N \mathbf{x}_i^T \mathbf{x}_i \right) \mathbf{w}_1 = \mathbf{w}_1^T \Sigma \mathbf{w}_1$$

### Constrained Optimization via Lagrange Multipliers
To find the direction $\mathbf{w}_1$ that maximizes this variance subject to the constraint $\|\mathbf{w}_1\|_2^2 = \mathbf{w}_1^T \mathbf{w}_1 = 1$, we formulate the Lagrangian:

$$\mathcal{L}(\mathbf{w}_1, \lambda) = \mathbf{w}_1^T \Sigma \mathbf{w}_1 - \lambda (\mathbf{w}_1^T \mathbf{w}_1 - 1)$$

where $\lambda$ is the Lagrange multiplier. 

Taking the gradient of $\mathcal{L}$ with respect to $\mathbf{w}_1$ and setting it to $\mathbf{0}$:
$$\nabla_{\mathbf{w}_1} \mathcal{L} = 2\Sigma \mathbf{w}_1 - 2\lambda \mathbf{w}_1 = \mathbf{0}$$

Dividing by 2 yields the classic **eigenvalue equation**:
$$\Sigma \mathbf{w}_1 = \lambda \mathbf{w}_1$$

### Selecting the Principal Components
This result proves that any direction $\mathbf{w}$ that extremizes the projected variance must be an **eigenvector** of the covariance matrix $\Sigma$. 

To determine which eigenvector maximizes the variance, we substitute the eigenvalue relation back into our projected variance equation:
$$\sigma_{\text{projected}}^2 = \mathbf{w}_1^T \Sigma \mathbf{w}_1 = \mathbf{w}_1^T (\lambda \mathbf{w}_1) = \lambda (\mathbf{w}_1^T \mathbf{w}_1) = \lambda$$

**Conclusion:** The variance of the data projected onto an eigenvector is equal to its corresponding eigenvalue. To maximize the variance, we must choose the eigenvector corresponding to the **largest eigenvalue** ($\lambda_1$). This vector $\mathbf{w}_1$ is the **first principal component**.

To find the $k$-th principal component $\mathbf{w}_k$, we repeat this optimization under the additional constraint that $\mathbf{w}_k$ must be orthogonal to all previously discovered components ($\mathbf{w}_k^T \mathbf{w}_j = 0$ for $j < k$). This yields the eigenvector corresponding to the $k$-th largest eigenvalue $\lambda_k$.

## 3. The PCA Algorithm

Given a raw data matrix $X_{\text{raw}} \in \mathbb{R}^{N \times d}$ and a target dimensionality $k < d$:

1. **Center and Scale:** Compute the mean $\mathbf{\mu}$ of each feature and subtract it. Optionally, divide by the standard deviation if features have different units (this computes the correlation matrix instead of the covariance matrix).
2. **Compute Covariance:** Construct $\Sigma = \frac{1}{N} X^T X$.
3. **Eigendecomposition:** Compute the eigenvalues $\Lambda = \{\lambda_1, \dots, \lambda_d\}$ and eigenvectors $W = \{\mathbf{w}_1, \dots, \mathbf{w}_d\}$ of $\Sigma$.
4. **Sort and Select:** Sort the eigenvectors such that $\lambda_1 \ge \lambda_2 \ge \dots \ge \lambda_d$. Select the top $k$ eigenvectors to form the projection matrix $W_k \in \mathbb{R}^{d \times k}$:
   $$W_k = \begin{bmatrix} \vert & \vert & & \vert \\ \mathbf{w}_1 & \mathbf{w}_2 & \dots & \mathbf{w}_k \\ \vert & \vert & & \vert \end{bmatrix}$$
5. **Project:** Transform the original centered data matrix $X$ into the lower-dimensional representation $Z \in \mathbb{R}^{N \times k}$:
   $$Z = X W_k$$

## 4. Alternate Perspective: Minimizing Reconstruction Error

Instead of maximizing variance, PCA can also be derived by finding a lower-dimensional linear manifold that minimizes the sum of squared distances between the original data points and their orthogonal projections onto the manifold.

Let $\hat{\mathbf{x}}_i$ be the reconstruction of the original centered vector $\mathbf{x}_i$ using $k$ orthogonal basis vectors $W_k$:
$$\hat{\mathbf{x}}_i = \sum_{j=1}^k (\mathbf{x}_i \mathbf{w}_j) \mathbf{w}_j^T$$

The optimization objective is to minimize the **Reconstruction Mean Squared Error (MSE)**:
$$J = \frac{1}{N} \sum_{i=1}^N \|\mathbf{x}_i - \hat{\mathbf{x}}_i\|_2^2$$

Through algebraic expansion (using Pythagorean theorem properties of orthogonal projections), it can be shown that minimizing this reconstruction error is mathematically equivalent to maximizing the projected variance. Both perspectives lead to the exact same eigenvalue problem.

## 5. Explained Variance Ratio

To determine how many principal components ($k$) to retain, we compute the **Explained Variance Ratio (EVR)** for each component. The proportion of total variance explained by the $j$-th principal component is:

$$\text{EVR}_j = \frac{\lambda_j}{\sum_{i=1}^d \lambda_i}$$

The cumulative explained variance for $k$ components is:
$$\text{Cumulative EVR}_k = \frac{\sum_{j=1}^k \lambda_j}{\sum_{i=1}^d \lambda_i}$$

Typically, practitioners select a value for $k$ that preserves a target percentage of the total variance (e.g., $95\%$ or $99\%$).

## 6. Assumptions and Limitations

1. **Linearity:** PCA assumes that the underlying manifold of the data is linear. If the data lies on a curved structure (e.g., a Swiss roll), PCA will fail to capture the true low-dimensional structure. Non-linear methods like Kernel PCA or t-SNE are preferred in these scenarios.
2. **Mean and Variance as Sufficient Statistics:** By utilizing the covariance matrix, PCA assumes that the data's distribution can be adequately described by its mean and variance (which is strictly true for Gaussian distributions).
3. **Orthogonality:** PCA constrains principal components to be mutually orthogonal, which may not align with the physical processes that generated the features.
