SALib is an open-source Python library for **sensitivity analysis**. It's used in systems modeling to understand how changes to a model's inputs or external factors affect its outputs. The library provides implementations for several popular sensitivity analysis methods.

---

### Key Features and Methods

The library includes a variety of sensitivity analysis techniques, such as:

* **Sobol Sensitivity Analysis:** A variance-based method that calculates first-order, second-order, and total-order sensitivity indices. This helps determine which inputs have the most influence on the output.
* **Method of Morris:** A screening method that efficiently identifies influential inputs with fewer model runs compared to other methods.
* **eFAST and RBD-FAST:** Fourier-based methods for estimating sensitivity indices.
* **Delta Moment-Independent Measure:** A measure that is not based on variance, making it useful for analyzing models with non-monotonic relationships.
* **DGSM:** A derivative-based method for global sensitivity analysis.

---

### How to Use SALib

SALib can be used in two main ways: a procedural approach and a method chaining approach. Both methods require defining a **problem dictionary** that specifies the number of variables, their names, and their bounds.

#### Procedural Approach

This approach involves calling functions sequentially to perform the steps of a sensitivity analysis:

1.  **Define the Problem:** Create a dictionary with `'num_vars'`, `'names'`, and `'bounds'`.
2.  **Generate Samples:** Use a sampling function, such as `saltelli.sample()`, to create a set of input values for the model.
3.  **Run the Model:** Evaluate your model using the generated samples to produce an output for each set of inputs.
4.  **Analyze the Results:** Use an analysis function, like `sobol.analyze()`, to calculate the sensitivity indices from the model's outputs.

#### Method Chaining Approach

Introduced in SALib v1.4, this approach provides a more streamlined workflow:

1.  **Define the Problem:** Use `ProblemSpec` to define the parameters and outputs of your model.
2.  **Chain the Calls:** Chain together the sampling, evaluation, and analysis steps in a single sequence.
3.  **Extract Results:** The `ProblemSpec` object will store the samples, results, and analysis, which can be accessed individually.

Basic plotting functionality is also included in this approach for visualizing the results.

---

### Installation and Requirements

To install SALib, you can use pip or conda. The library requires **NumPy**, **SciPy**, **matplotlib**, and **pandas**. It is officially supported for **Python 3**.

* `pip install SALib`
* `conda install SALib`

---

### Citing SALib

If you use SALib in your work, the authors request that you cite one of their papers. The most recent is from 2022, which focuses on SALib 2.0. The 2017 paper is the original publication introducing the library.

---

### Resources and Community

SALib has comprehensive documentation on **ReadTheDocs** and a growing community. There are several projects, blogs, and videos that use or discuss the library, which are a great resource for learning more about its applications. Contributions to the project are also welcome and can be made by submitting a pull request or creating an issue.
