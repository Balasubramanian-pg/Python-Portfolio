# Skincare Review Sentiment Classification Project

This repository contains an end-to-end Natural Language Processing (NLP) pipeline designed to classify customer skincare product reviews into positive, neutral, or negative categories. It features a complete workflow from raw text processing to modeling and deployment-ready inference.

## Overview

Customer feedback in the beauty and skincare industry often contains domain-specific terminology (e.g., "breakouts," "clogged pores," "white cast"). This project implements a machine learning approach to analyze such feedback. 

To ensure the codebase is self-contained and immediately runnable, the workflow includes a synthetic data generator that reflects typical customer sentiments and terminology.

## Core Features

### Data Simulation
Generates balanced skincare-specific review texts representing diverse customer experiences (e.g., product efficacy, side effects, packaging issues).

### Exploratory Data Analysis
Analyzes class distributions and investigates correlation metrics between review lengths and underlying sentiment.

### Text Preprocessing
Standardizes raw reviews using natural language cleaning techniques:
* Lowercase normalization
* Non-alphabetic character removal
* English stopword filtering (using NLTK)
* Word lemmatization (using WordNet)

### Feature Extraction
Converts unstructured text into a numerical format utilizing Term Frequency-Inverse Document Frequency (TF-IDF) vectorization, capturing both unigrams and bigrams.

### Model Training and Evaluation
Trains a Logistic Regression classifier configured with balanced class weights to handle potentially skewed distributions. Evaluates results using precision, recall, F1-score, and confusion matrix visualizations.

### Predictive Inference Pipeline
Exposes a unified function to accept raw text strings and output predicted sentiment classifications alongside confidence probabilities.

## Requirements

The project is designed to run in any standard Python environment supporting Jupyter Notebooks. The primary dependencies include:

* Python 3.8 or higher
* pandas
* numpy
* matplotlib
* seaborn
* nltk
* scikit-learn

## Getting Started

### Installation

Clone this repository to your local machine:

git clone https://github.com/yourusername/skincare-review-nlp.git
cd skincare-review-nlp

Install the required Python packages:

pip install pandas numpy matplotlib seaborn nltk scikit-learn

### Running the Project

1. Open the provided `skincare_review_nlp.ipynb` notebook in your preferred environment (e.g., VS Code, JupyterLab, or Google Colab).
2. Execute the cells sequentially. The notebook handles download requirements for NLTK resources automatically during execution.

## Pipeline Details

### Text Processing Logic
The custom preprocessor converts strings into clean token streams. For instance:
* Input: "I love this moisturizer! It keeps my skin hydrated all day and does not break me out."
* Cleaned: "love moisturizer keep skin hydrated day break"

This representation minimizes vocabulary dimensionality and groups inflected forms of words (e.g., "keeps" and "keeping" both resolve to "keep").

### Vectorization
The text is vectorized using a TF-IDF transformer configured with a maximum of 1,000 features. Both single words and two-word combinations (bigrams) are analyzed to capture contextual modifiers like "not bad" or "very dry."

### Classification
A Logistic Regression algorithm is employed. It serves as a strong, interpretable baseline for text classification tasks, particularly when paired with high-dimensional sparse inputs like TF-IDF vectors.

## Limitations and Future Work

While this setup demonstrates a complete NLP pipeline, there are areas for potential optimization:
* Dataset Scale: The baseline model trains on synthetic data. Real-world applications should utilize larger, annotated datasets like the Amazon Fine Food or Sephora Review datasets.
* Modeling Upgrades: For complex syntax or sarcasm detection, classical classifiers can be replaced with deep learning architectures or pre-trained transformer models such as BERT.
