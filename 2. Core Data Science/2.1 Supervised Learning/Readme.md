# Supervised Learning

Supervised learning is a core subfield of machine learning where an algorithm learns a mapping from input variables to output variables using labeled training data. This note structures the concept from its mathematical formulation to practical paradigms, optimization strategies, and theoretical boundaries.

# Formal Mathematical Foundations of Supervised Learning

## 1. Introduction

Supervised learning is the foundational paradigm of modern machine learning.
The objective is to learn a mapping between input variables and output variables using labeled examples.

Formally, supervised learning attempts to estimate an unknown functional relationship:

$$
f : \mathcal{X} \rightarrow \mathcal{Y}
$$

where:

- $\mathcal{X}$ represents the input space
- $\mathcal{Y}$ represents the output space
- $f$ is the predictive function

The learning algorithm observes examples:

($$x_i$$, $$y_i$$)

and attempts to infer the hidden relationship governing the data generation process.

This framework underlies:

* Linear Regression
* Logistic Regression
* Support Vector Machines
* Decision Trees
* Neural Networks
* Ensemble Methods



# 2. Statistical View of Learning

Supervised learning assumes that data is generated from an unknown probability distribution:

$
P(X,Y)
$

called the **joint probability distribution** over the random variables:

* (X): input variables
* (Y): output variables

The learning algorithm never directly observes (P(X,Y)).

Instead, it observes finite samples drawn from it.

## Intuition

Reality generates examples according to some hidden stochastic process.

Example:

| Features             | Label            |
| -- | - |
| House size, location | House price      |
| Email content        | Spam / Not Spam  |
| Patient measurements | Disease category |

The dataset is therefore only a finite approximation of the underlying distribution.

# 3. Input Space

The input space is defined as:

$
\mathcal{X} \subseteq \mathbb{R}^d
$

where:

* (d) = number of features
* (\mathbb{R}^d) = (d)-dimensional real-valued vector space

An individual sample is represented as:

$
x =
\begin{bmatrix}
x_1 \
x_2 \
\vdots \
x_d
\end{bmatrix}
$

## Example

Suppose we predict house prices using:

* area
* number of rooms
* age

Then:

$
x =
\begin{bmatrix}
2000 \
4 \
10
\end{bmatrix}
$

represents:

* 2000 sq ft
* 4 rooms
* 10 years old

# 4. Output Space

The output space depends on the problem type.

## Regression

For regression:

$
\mathcal{Y} \subseteq \mathbb{R}
$

The output is continuous.

Examples:

* stock prices
* temperatures
* sales forecasting

## Classification

For classification:

### Binary Classification

$
\mathcal{Y} = {0,1}
$

### Multi-Class Classification

$
\mathcal{Y} = {1,2,\dots,C}
$

where:

* (C) = number of classes

# 5. Dataset Formulation

The training dataset consists of:

$
\mathcal{D}
===========

{
(x_1,y_1),
(x_2,y_2),
\dots,
(x_N,y_N)
}
$

where:

* (N) = number of training samples

# 6. IID Assumption

Training examples are assumed to be:

## Independent and Identically Distributed (IID)

Formally:

$
(x_i,y_i)
\overset{iid}{\sim}
P(X,Y)
$

This assumption contains two components:

## Independence

Each sample is statistically independent of others.

Formally:

$
P(x_i,x_j)=P(x_i)P(x_j)
$

for independent observations.

## Identically Distributed

All samples originate from the same distribution:

$
P_{train}(X,Y)=P_{test}(X,Y)
$

This assumption is often violated in real-world systems due to:

* concept drift
* domain shift
* seasonality
* changing user behavior

# 7. Objective of Learning

The goal is to find a function:

$
f \in \mathcal{H}
$

that minimizes prediction error.

# 8. Hypothesis Space

The hypothesis space:

$
\mathcal{H}
$

is the set of all candidate functions the model can represent.

## Examples

### Linear Models

$
f(x)=w^Tx+b
$

### Polynomial Models

$
f(x)=w_0+w_1x+w_2x^2+\dots+w_nx^n
$

### Neural Networks

$
f(x)=\sigma(W_2\sigma(W_1x+b_1)+b_2)
$

# 9. Loss Function

The quality of predictions is measured using a loss function:

$
L(y,f(x))
$

## Mean Squared Error (Regression)

$
L(y,\hat{y})=(y-\hat{y})^2
$

## Mean Absolute Error

$
L(y,\hat{y})=|y-\hat{y}|
$

## Binary Cross Entropy

$
L(y,\hat{y})
=
-y\log(\hat{y})
-(1-y)\log(1-\hat{y})
$

# 10. Expected Risk

The true learning objective is minimizing expected risk:

$
R(f)
=
\mathbb{E}_{(X,Y)\sim P(X,Y)}
$L(Y,f(X))$
$
This represents the expected prediction error over the true data distribution.

## Expanded Form

For continuous variables:

$
R(f)
=
\int
L(y,f(x))
,dP(x,y)
$

For discrete variables:

$
R(f)
=
\sum_{x,y}
L(y,f(x))P(x,y)
$

# 11. Empirical Risk Minimization

Since the true distribution is unknown, we approximate risk using the dataset.

The empirical risk is:

$
\hat{R}(f)
=
\frac{1}{N}
\sum_{i=1}^{N}
L(y_i,f(x_i))
$

Learning algorithms solve:

$
f^*
=
\arg\min_{f\in\mathcal{H}}
\hat{R}(f)
$

This principle is called:

# Empirical Risk Minimization (ERM)

# 12. Learning Pipeline

```mermaid
flowchart LR
    A$Unknown Distribution P(X,Y)$

 --> B$Sample Dataset$


    B --> C$Training Data$


    C --> D$Model Training$


    D --> E$Learned Function f(x)$


    E --> F$Predictions on Unseen Data$


```
# 13. Optimization Problem

Most supervised learning problems become optimization problems.

## General Optimization Objective

$
\theta^*
========

\arg\min_{\theta}
\hat{R}(\theta)
$

where:

* (\theta) = model parameters

## Linear Regression Example

Model:

$
\hat{y}=w^Tx+b
$

Objective:

$
J(w,b)
=

\frac{1}{N}
\sum_{i=1}^{N}
(y_i-(w^Tx_i+b))^2
$

# 14. Gradient Descent

Parameters are updated iteratively:

$
\theta_{t+1}
=

## $\theta_t$

$\eta
\nabla_\theta J(\theta_t)
$

where:

* $(\eta)$ = learning rate
* $(\nabla_\theta J)$ = gradient

# 15. Generalization

A model must perform well on unseen data.

This ability is called:

# Generalization

## Training Error

$
\hat{R}_{train}(f)
$

## Test Error

$
\hat{R}_{test}(f)
$

Good models satisfy:

$
\hat{R}*{train}(f)
\approx
\hat{R}*{test}(f)
$

# 16. Overfitting

Overfitting occurs when the model memorizes noise.



## Characteristics

* low training error
* high test error



## Visual Intuition

```mermaid
flowchart TD
    A$Simple Model$

 --> B$Underfitting$


    C$Balanced Complexity$

 --> D$Good Generalization$


    E$Very Complex Model$

 --> F$Overfitting$


```



# 17. Bias-Variance Tradeoff

Prediction error decomposes into:

$
\mathbb{E}$(Y-\hat{f}(X))^2$


============================

Bias^2
+
Variance
+
Noise
$





## High Bias

* overly simple model
* underfitting



## High Variance

* overly flexible model
* overfitting



# 18. Regularization

Regularization controls model complexity.



## L2 Regularization

$
J(w)
====

\hat{R}(w)
+
\lambda ||w||_2^2
$





## L1 Regularization

$
J(w)
====

\hat{R}(w)
+
\lambda ||w||_1
$





# 19. Bayesian Perspective

Frequentist learning estimates fixed parameters.

Bayesian learning treats parameters as random variables.



## Bayes Rule

P(\theta|D)=\frac{P(D|\theta)P(\theta)}{P(D)}

where:

* (P(\theta)) = prior
* (P(D|\theta)) = likelihood
* (P(\theta|D)) = posterior



# 20. Geometric Interpretation

Machine learning can be viewed geometrically.



## Linear Classification

Decision boundary:

$
w^Tx+b=0
$



defines a hyperplane separating classes.



## Higher Dimensions

In (d)-dimensional space:

* line → 2D
* plane → 3D
* hyperplane → (d)-dimensions



# 21. Computational Complexity

Training cost depends on:

* dataset size
* feature dimension
* model complexity



## Example Complexity

### Linear Regression (Closed Form)

$
O(d^3)
$



due to matrix inversion.



## Gradient Descent

$
O(Nd)
$



per iteration.



# 22. Python Example: Linear Regression

```python
import numpy as np
from sklearn.linear_model import LinearRegression

# Training data
X = np.array($
    $1000$

,
    $1500$

,
    $2000$

,
    $2500$


$

)

y = np.array($
    200000,
    300000,
    400000,
    500000
$

)

# Create model
model = LinearRegression()

# Train model
model.fit(X, y)

# Predict unseen value
prediction = model.predict($$1800$

$

)

print(prediction)
```



# 23. Python Example: Loss Computation

```python
import numpy as np

# True values
y_true = np.array($3, -0.5, 2, 7$

)

# Predicted values
y_pred = np.array($2.5, 0.0, 2, 8$

)

# Mean Squared Error
mse = np.mean((y_true - y_pred) ** 2)

print("MSE:", mse)
```



# 24. Simple Gradient Descent Example

```python
import numpy as np

# Function
def f(x):
    return x**2

# Gradient
def grad(x):
    return 2 * x

x = 10
learning_rate = 0.1

for step in range(20):
    x = x - learning_rate * grad(x)
    print(f"Step {step}: x = {x}")
```



# 25. Complete Learning Framework

```mermaid
flowchart TD
    A$Real World Process$

 --> B$Unknown Distribution P(X,Y)$


    B --> C$Sample Training Data$


    C --> D$Choose Hypothesis Space$


    D --> E$Define Loss Function$


    E --> F$Optimization$


    F --> G$Learned Model$


    G --> H$Generalization$


```



# 26. Important Hidden Assumptions

## Label Correctness

Assumes labels are accurate.

Often false in practice.



## Stationary Distribution

Assumes future resembles past.

Often violated.



## Sufficient Features

Assumes features contain predictive signal.

Poor features fundamentally limit learning.



# 27. Theoretical Limitation

No model can perfectly infer reality from finite data.

Learning theory fundamentally deals with:

* uncertainty
* approximation
* statistical estimation



# 28. Connection to Deep Learning

Deep learning extends this framework by:

* using extremely large hypothesis spaces
* learning hierarchical representations
* optimizing millions or billions of parameters

Yet the core formulation remains unchanged:

$
\min_{f\in\mathcal{H}}
\hat{R}(f)
$





# 29. Final Mathematical Summary

Supervised learning consists of:



## Data

$
\mathcal{D}
===========

{
(x_i,y_i)
}_{i=1}^{N}
$





## Hypothesis Space

$
f \in \mathcal{H}
$





## Loss Function

$
L(y,f(x))
$





## Objective

$
f^*
===

\arg\min_{f\in\mathcal{H}}
\frac{1}{N}
\sum_{i=1}^{N}
L(y_i,f(x_i))
$





# 30. Final Takeaways

Supervised learning is fundamentally:

* statistical inference
* function approximation
* optimization under uncertainty

Its central challenge is not merely fitting data.

The true challenge is:

# learning structure that generalizes beyond observed samples.

That single idea drives nearly all of machine learning theory, deep learning research, statistical learning, and modern AI systems.


## 2. Loss Functions and Risk Minimization

To measure how "good" a hypothesis $f$ is, we define a **Loss Function** $L: \mathcal{Y} \times \mathcal{Y} \to \mathbb{R}_{\ge 0}$. The loss $L(y, f(\mathbf{x}))$ quantifies the penalty for predicting $f(\mathbf{x})$ when the true label is $y$.

### Common Loss Functions
1.  **Mean Squared Error (MSE) / Quadratic Loss** (primarily for regression):
    $$L(y, f(\mathbf{x})) = (y - f(\mathbf{x}))^2$$
2.  **Absolute Error Loss** (robust regression):
    $$L(y, f(\mathbf{x})) = |y - f(\mathbf{x})|$$
3.  **Cross-Entropy Loss / Log Loss** (for probabilistic classification):
    $$L(y, f(\mathbf{x})) = - \Big( y \log(f(\mathbf{x})) + (1 - y) \log(1 - f(\mathbf{x})) \Big)$$

### Expected Risk vs. Empirical Risk

*   **Expected Risk (True Risk):** The expected loss over the entire data-generating distribution $P(X, Y)$:
    $$R(f) = \mathbb{E}_{(X,Y) \sim P}$L(Y, f(X))$

 = \iint_{\mathcal{X} \times \mathcal{Y}} L(y, f(\mathbf{x})) P(\mathbf{x}, y) d\mathbf{x} dy$$
    Because the joint distribution $P(X, Y)$ is unknown, we cannot calculate $R(f)$ directly.

*   **Empirical Risk:** The average loss measured over our finite training dataset $D$:
    $$R_{emp}(f) = \frac{1}{N} \sum_{i=1}^N L(y_i, f(\mathbf{x}_i))$$

*   **Empirical Risk Minimization (ERM):** The core principle of supervised learning is to choose a function $f \in \mathcal{H}$ that minimizes the empirical risk:
    $$\hat{f} = \arg\min_{f \in \mathcal{H}} R_{emp}(f)$$

## 3. Regularization and Structural Risk Minimization (SRM)

Minimizing empirical risk too aggressively can lead to **overfitting**, where the model memorizes noise in the training set and fails to generalize to unseen data. To counter this, we add a regularization penalty $\Omega(f)$ that penalizes model complexity.

The objective becomes:
$$\hat{f} = \arg\min_{f \in \mathcal{H}} \left( R_{emp}(f) + \lambda \Omega(f) \right)$$

where $\lambda > 0$ is a hyperparameter balancing the trade-off between fitting the training data and keeping the model simple.

### Common Regularizers (for parametric models where $f(\mathbf{x}) = f(\mathbf{x}; \mathbf{\theta})$)

1.  **$L_2$ Regularization (Ridge / Tikhonov Regularization):**
    $$\Omega(\mathbf{\theta}) = \|\mathbf{\theta}\|_2^2 = \sum_{j=1}^d \theta_j^2$$
    *Probabilistic interpretation:* Equivalent to assuming a Gaussian prior over the parameters $\mathbf{\theta}$ under Maximum A Posteriori (MAP) estimation.

2.  **$L_1$ Regularization (Lasso):**
    $$\Omega(\mathbf{\theta}) = \|\mathbf{\theta}\|_1 = \sum_{j=1}^d |\theta_j|$$
    *Probabilistic interpretation:* Equivalent to assuming a Laplace prior over the parameters. It encourages sparsity, zeroing out less useful coefficients.

## 4. Deep-Dive: Mathematical Walkthrough of Two Core Paradigms

Let us explore the derivation and mathematics of two fundamental algorithms: Linear Regression (for continuous output) and Logistic Regression (for discrete classification).

### Paradigm A: Linear Regression (Continuous Output)

In linear regression, we assume the relationship between inputs and outputs is linear. We parameterized our model with weights $\mathbf{\theta} \in \mathbb{R}^{d+1}$ (including the bias term $\theta_0$ by appending a constant 1 to the input vector $\mathbf{x}$).

$$f(\mathbf{x}; \mathbf{\theta}) = \mathbf{\theta}^T \mathbf{x} = \theta_0 + \theta_1 x_1 + \dots + \theta_d x_d$$

Using the Mean Squared Error (MSE) loss, the empirical cost function $J(\mathbf{\theta})$ is:
$$J(\mathbf{\theta}) = \frac{1}{2N} \sum_{i=1}^N (y_i - \mathbf{\theta}^T \mathbf{x}_i)^2$$

#### Vectorized Representation
Let $X \in \mathbb{R}^{N \times (d+1)}$ be the design matrix containing training inputs, and $\mathbf{y} \in \mathbb{R}^N$ be the target vector.
$$J(\mathbf{\theta}) = \frac{1}{2N} \|X\mathbf{\theta} - \mathbf{y}\|_2^2 = \frac{1}{2N} (X\mathbf{\theta} - \mathbf{y})^T (X\mathbf{\theta} - \mathbf{y})$$

#### Closed-Form Solution (The Normal Equation)
To find the optimal parameter vector $\mathbf{\theta}$ that minimizes $J(\mathbf{\theta})$, we compute the gradient with respect to $\mathbf{\theta}$ and set it to $\mathbf{0}$:
$$\nabla_{\mathbf{\theta}} J(\mathbf{\theta}) = \frac{1}{N} X^T (X\mathbf{\theta} - \mathbf{y}) = \mathbf{0}$$
$$X^T X \mathbf{\theta} = X^T \mathbf{y}$$
$$\mathbf{\theta}^* = (X^T X)^{-1} X^T \mathbf{y}$$

*(Assuming the matrix $X^T X$ is invertible, i.e., of full rank).*

### Paradigm B: Logistic Regression (Binary Classification)

In binary classification, $\mathcal{Y} = \{0, 1\}$. We map the real-valued output of a linear model to a probability value between $0$ and $1$ using the **Sigmoid (Logistic) Function**:

$$\sigma(z) = \frac{1}{1 + e^{-z}}$$

The hypothesis function is formulated as:
$$h_{\mathbf{\theta}}(\mathbf{x}) = \sigma(\mathbf{\theta}^T \mathbf{x}) = \frac{1}{1 + e^{-\mathbf{\theta}^T \mathbf{x}}}$$

#### Probabilistic Interpretation
We model the conditional probability distribution:
$$P(Y = 1 \mid \mathbf{x}; \mathbf{\theta}) = h_{\mathbf{\theta}}(\mathbf{x})$$
$$P(Y = 0 \mid \mathbf{x}; \mathbf{\theta}) = 1 - h_{\mathbf{\theta}}(\mathbf{x})$$

This can be written compactly as:
$$P(y \mid \mathbf{x}; \mathbf{\theta}) = \left( h_{\mathbf{\theta}}(\mathbf{x}) \right)^y \left( 1 - h_{\mathbf{\theta}}(\mathbf{x}) \right)^{1-y}$$

#### Maximum Likelihood Estimation (MLE)
Assuming the data points are conditionally independent, the likelihood of the parameter vector $\mathbf{\theta}$ given the dataset is:
$$L(\mathbf{\theta}) = \prod_{i=1}^N P(y_i \mid \mathbf{x}_i; \mathbf{\theta}) = \prod_{i=1}^N \left( h_{\mathbf{\theta}}(\mathbf{x}_i) \right)^{y_i} \left( 1 - h_{\mathbf{\theta}}(\mathbf{x}_i) \right)^{1-y_i}$$

We maximize this likelihood by minimizing the negative log-likelihood (also known as the Binary Cross-Entropy loss):
$$J(\mathbf{\theta}) = -\frac{1}{N} \ln L(\mathbf{\theta}) = -\frac{1}{N} \sum_{i=1}^N \Big$ y_i \ln h_{\mathbf{\theta}}(\mathbf{x}_i) + (1-y_i) \ln (1 - h_{\mathbf{\theta}}(\mathbf{x}_i)) \Big$

$$

#### Optimization via Gradient Descent
Because $J(\mathbf{\theta})$ has no analytical closed-form minimum, we use an iterative optimization algorithm like **Gradient Descent**.

The derivative of the sigmoid function is $\sigma'(z) = \sigma(z)(1 - \sigma(z))$. Using the chain rule, the gradient of the loss function with respect to weight $\theta_j$ is:
$$\frac{\partial J(\mathbf{\theta})}{\partial \theta_j} = \frac{1}{N} \sum_{i=1}^N \left( h_{\mathbf{\theta}}(\mathbf{x}_i) - y_i \right) x_{ij}$$

The vectorized gradient step is:
$$\mathbf{\theta}^{(t+1)} = \mathbf{\theta}^{(t)} - \alpha \frac{1}{N} X^T \left( \sigma(X\mathbf{\theta}^{(t)}) - \mathbf{y} \right)$$
where $\alpha > 0$ is the learning rate.

## 5. Theoretical Boundaries: The Bias-Variance Decomposition

To understand how supervised learning algorithms generalize, we can decompose the expected generalization error. 

Assume the true relation is $y = f(\mathbf{x}) + \epsilon$, where $\mathbb{E}$\epsilon$

 = 0$ and $\text{Var}(\epsilon) = \sigma^2$ (irreducible error representing environmental noise).

Let $\hat{f}(\mathbf{x}; D)$ be the estimate of $f$ trained on a random dataset $D$. The expected squared prediction error of our model at a point $\mathbf{x}$ across all possible datasets $D$ is:

$$\mathbb{E}_D \left$ \left( y - \hat{f}(\mathbf{x}; D) \right)^2 \right$

 = \text{Bias}\left$\hat{f}(\mathbf{x})\right$

^2 + \text{Var}\left$\hat{f}(\mathbf{x})\right$

 + \sigma^2$$

### Derivation components:
1.  **$\text{Bias}\left$\hat{f}(\mathbf{x})\right$

 = \mathbb{E}_D\left$\hat{f}(\mathbf{x}; D)\right$

 - f(\mathbf{x})$**
    Measures how much the average prediction over all possible datasets differs from the true underlying function. High bias indicates underfitting.
2.  **$\text{Var}\left$\hat{f}(\mathbf{x})\right$

 = \mathbb{E}_D\left$ \left( \hat{f}(\mathbf{x}; D) - \mathbb{E}_D$\hat{f}(\mathbf{x}; D)$

 \right)^2 \right$

$**
    Measures the sensitivity of the model's prediction to the specific dataset $D$ it was trained on. High variance indicates overfitting.
3.  **$\sigma^2$ (Irreducible Error)**
    The minimum possible error limit that cannot be eliminated regardless of the model chosen.

```
       Error
         ^
         |      \              /   Total Expected Error
         |       \            /
         |        \  _ _ _ _ /_ 
         |        / \       /  \   Variance
         |       /   \     /    \ 
         |      /     \___/      \ 
         |     /       _ _        \ Bias^2
         |    /      /     \       \
         +--> Model Complexity
                    Low Complexity     High Complexity
                     (Underfitting)     (Overfitting)
```

## Summary of the Supervised Learning Process

| Step | Goal / Action | Key Mathematical Object |
| : | : | : |
| **1. Model Setup** | Establish mapping parameterized by $\mathbf{\theta}$. | $f(\mathbf{x}; \mathbf{\theta})$ |
| **2. Performance Measure** | Define penalty for incorrect predictions. | Loss function $L(y, f(\mathbf{x}))$ |
| **3. Objective Formulation** | Minimize empirical loss + complexity penalty. | $R_{reg}(\mathbf{\theta}) = R_{emp}(\mathbf{\theta}) + \lambda \Omega(\mathbf{\theta})$ |
| **4. Optimization** | Update $\mathbf{\theta}$ to move towards minimum loss. | $\mathbf{\theta} \leftarrow \mathbf{\theta} - \alpha \nabla_{\mathbf{\theta}} R_{reg}(\mathbf{\theta})$ |
