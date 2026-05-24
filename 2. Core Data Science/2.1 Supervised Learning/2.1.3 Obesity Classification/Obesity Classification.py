"""
Obesity Classification - Supervised Learning Pipeline
=======================================================

Business Requirement:
    Develop a robust classification system to predict obesity levels
    based on individual's eating habits, physical condition, and
    demographic data. The model will assist healthcare providers in
    early intervention and personalized treatment planning.

Project Structure:
    - Configuration management (YAML or dict)
    - Data ingestion and validation
    - Exploratory data analysis (EDA) with visualizations
    - Preprocessing (scaling, encoding, outlier handling)
    - Feature engineering (interaction terms, polynomial features)
    - Model training (multiple classifiers with cross-validation)
    - Hyperparameter tuning (GridSearchCV / RandomizedSearchCV)
    - Model evaluation (confusion matrix, classification report, ROC-AUC)
    - Model persistence (save/load using joblib or pickle)
    - Prediction pipeline for new samples
    - Logging and error handling
    - Command-line interface (argparse)

Author: Balasubramanian PG
Date: 2026-05-24
Version: 2.0
"""

import argparse
import logging
import os
import sys
import warnings
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    AdaBoostClassifier,
    StackingClassifier,
)
from sklearn.exceptions import DataConversionWarning
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import (
    GridSearchCV,
    RandomizedSearchCV,
    StratifiedKFold,
    cross_val_score,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    LabelEncoder,
    OneHotEncoder,
    RobustScaler,
    StandardScaler,
)
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=DataConversionWarning)

# ----------------------------- Logging Configuration -------------------------
def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Configure logging to console and optionally to a file.

    Parameters
    ----------
    log_level : str, default='INFO'
        Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    log_file : str, optional
        Path to log file. If None, only console handler is used.
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        handlers.append(logging.FileHandler(log_file, mode='a'))

    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers,
    )


logger = logging.getLogger(__name__)

# ----------------------------- Configuration ---------------------------------
class Config:
    """
    Central configuration class for the obesity classification pipeline.
    Contains hyperparameters, file paths, and model settings.
    """
    # Data paths
    DATA_PATH = "data/obesity_classification.csv"  # Update with actual path
    MODEL_PATH = "models/obesity_classifier.pkl"
    PREPROCESSOR_PATH = "models/preprocessor.pkl"
    OUTPUT_DIR = "outputs/"
    FIGURES_DIR = os.path.join(OUTPUT_DIR, "figures")
    REPORTS_DIR = os.path.join(OUTPUT_DIR, "reports")

    # Data columns (expected based on known dataset)
    NUMERICAL_COLS = [
        'Age', 'Height', 'Weight', 'FCVC', 'NCP', 'CH2O', 'FAF', 'TUE'
    ]
    CATEGORICAL_COLS = [
        'Gender', 'family_history_with_overweight', 'FAVC', 'CAEC', 'SMOKE',
        'SCC', 'CALC', 'MTRANS'
    ]
    TARGET_COL = 'NObeyesdad'  # Obesity level (multi-class)

    # Preprocessing
    NUMERICAL_IMPUTER = "mean"
    CATEGORICAL_IMPUTER = "most_frequent"
    SCALER_TYPE = "standard"  # options: standard, robust
    ENCODER_TYPE = "onehot"   # options: onehot, label

    # Model settings
    TEST_SIZE = 0.2
    RANDOM_STATE = 42
    CV_FOLDS = 5
    N_JOBS = -1
    HYPERPARAM_TRIALS = 50   # For RandomizedSearchCV

    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = os.path.join(OUTPUT_DIR, "logs", "pipeline.log")

    # Create directories if they don't exist
    @classmethod
    def ensure_dirs(cls):
        """Create necessary output directories."""
        for d in [cls.OUTPUT_DIR, cls.FIGURES_DIR, cls.REPORTS_DIR, os.path.dirname(cls.LOG_FILE)]:
            os.makedirs(d, exist_ok=True)


# ----------------------------- Data Loader -----------------------------------
class DataLoader:
    """
    Handles data loading from CSV or other sources with validation.
    """
    def __init__(self, config: Config):
        self.config = config
        self.data: Optional[pd.DataFrame] = None

    def load(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """
        Load dataset from CSV file.

        Parameters
        ----------
        file_path : str, optional
            Override default data path.

        Returns
        -------
        pd.DataFrame
            Loaded dataset.
        """
        path = file_path or self.config.DATA_PATH
        logger.info(f"Loading data from {path}")
        try:
            self.data = pd.read_csv(path)
            logger.info(f"Data loaded successfully. Shape: {self.data.shape}")
            return self.data
        except FileNotFoundError:
            logger.error(f"Data file not found: {path}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading data: {e}")
            raise

    def validate_columns(self, required_cols: List[str]) -> bool:
        """
        Validate that all required columns exist in the dataset.

        Parameters
        ----------
        required_cols : list of str
            List of column names that must be present.

        Returns
        -------
        bool
            True if all required columns exist.
        """
        missing = [col for col in required_cols if col not in self.data.columns]
        if missing:
            logger.error(f"Missing required columns: {missing}")
            return False
        logger.info("All required columns are present.")
        return True

    def get_data(self) -> pd.DataFrame:
        """Return loaded data."""
        if self.data is None:
            raise ValueError("Data not loaded. Call load() first.")
        return self.data


# ----------------------------- Exploratory Data Analysis --------------------
class DataExplorer:
    """
    Perform exploratory data analysis and generate visualizations.
    """
    def __init__(self, df: pd.DataFrame, config: Config):
        self.df = df
        self.config = config

    def basic_info(self) -> None:
        """Print basic information about the dataset."""
        logger.info("Dataset Info:")
        buffer = []
        self.df.info(buf=buffer)
        logger.info("\n".join(buffer))

        logger.info(f"Missing values:\n{self.df.isnull().sum()}")
        logger.info(f"Descriptive statistics:\n{self.df.describe()}")

    def plot_target_distribution(self) -> None:
        """Plot distribution of target variable."""
        plt.figure(figsize=(10, 6))
        sns.countplot(y=self.df[self.config.TARGET_COL], order=self.df[self.config.TARGET_COL].value_counts().index)
        plt.title("Distribution of Obesity Levels")
        plt.xlabel("Count")
        plt.ylabel("Obesity Level")
        plt.tight_layout()
        out_path = os.path.join(self.config.FIGURES_DIR, "target_distribution.png")
        plt.savefig(out_path)
        logger.info(f"Target distribution plot saved to {out_path}")
        plt.close()

    def plot_numerical_distributions(self) -> None:
        """Plot histograms for numerical features."""
        num_cols = [c for c in self.config.NUMERICAL_COLS if c in self.df.columns]
        if not num_cols:
            logger.warning("No numerical columns found for distribution plots.")
            return
        self.df[num_cols].hist(figsize=(15, 10), bins=30)
        plt.suptitle("Distributions of Numerical Features")
        plt.tight_layout()
        out_path = os.path.join(self.config.FIGURES_DIR, "numerical_distributions.png")
        plt.savefig(out_path)
        logger.info(f"Numerical distributions plot saved to {out_path}")
        plt.close()

    def plot_correlation_matrix(self) -> None:
        """Plot correlation heatmap for numerical features."""
        num_cols = [c for c in self.config.NUMERICAL_COLS if c in self.df.columns]
        if len(num_cols) < 2:
            logger.warning("Not enough numerical columns for correlation matrix.")
            return
        corr = self.df[num_cols].corr()
        plt.figure(figsize=(12, 8))
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", linewidths=0.5)
        plt.title("Correlation Matrix of Numerical Features")
        out_path = os.path.join(self.config.FIGURES_DIR, "correlation_matrix.png")
        plt.savefig(out_path)
        logger.info(f"Correlation matrix saved to {out_path}")
        plt.close()

    def plot_categorical_analysis(self) -> None:
        """Plot bar charts for categorical features vs target."""
        cat_cols = [c for c in self.config.CATEGORICAL_COLS if c in self.df.columns]
        if not cat_cols:
            logger.warning("No categorical columns found for analysis.")
            return
        n_cols = 3
        n_rows = (len(cat_cols) + n_cols - 1) // n_cols
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 6*n_rows))
        axes = axes.flatten() if n_rows > 1 else [axes]  # type: ignore
        for idx, col in enumerate(cat_cols):
            pd.crosstab(self.df[col], self.df[self.config.TARGET_COL], normalize='index').plot(
                kind='bar', stacked=True, ax=axes[idx], colormap='viridis'
            )
            axes[idx].set_title(f"{col} vs Obesity Level")
            axes[idx].set_xlabel(col)
            axes[idx].set_ylabel("Proportion")
            axes[idx].legend(title="Obesity Level", bbox_to_anchor=(1.05, 1))
        for j in range(len(cat_cols), len(axes)):
            axes[j].set_visible(False)
        plt.tight_layout()
        out_path = os.path.join(self.config.FIGURES_DIR, "categorical_analysis.png")
        plt.savefig(out_path, bbox_inches="tight")
        logger.info(f"Categorical analysis plot saved to {out_path}")
        plt.close()

    def run_all(self) -> None:
        """Run all EDA steps."""
        logger.info("Starting Exploratory Data Analysis...")
        self.basic_info()
        self.plot_target_distribution()
        self.plot_numerical_distributions()
        self.plot_correlation_matrix()
        self.plot_categorical_analysis()
        logger.info("EDA completed.")


# ----------------------------- Preprocessor ---------------------------------
class FeaturePreprocessor:
    """
    Preprocess data: impute missing values, scale numerical features,
    encode categorical features.
    """
    def __init__(self, config: Config):
        self.config = config
        self.preprocessor: Optional[ColumnTransformer] = None
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.target_encoder: Optional[LabelEncoder] = None

    def _create_preprocessor_pipeline(self) -> ColumnTransformer:
        """
        Create a ColumnTransformer pipeline for preprocessing features.
        """
        numerical_pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy=self.config.NUMERICAL_IMPUTER)),
            ('scaler', StandardScaler() if self.config.SCALER_TYPE == 'standard' else RobustScaler())
        ])

        if self.config.ENCODER_TYPE == 'onehot':
            categorical_pipeline = Pipeline([
                ('imputer', SimpleImputer(strategy=self.config.CATEGORICAL_IMPUTER)),
                ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
            ])
        else:
            # Label encoding: will be handled manually because ColumnTransformer
            # cannot apply LabelEncoder to multiple columns directly; we'll do post-fit.
            # For simplicity, we'll use OneHotEncoder as default.
            categorical_pipeline = Pipeline([
                ('imputer', SimpleImputer(strategy=self.config.CATEGORICAL_IMPUTER)),
                ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
            ])

        preprocessor = ColumnTransformer([
            ('num', numerical_pipeline, self.config.NUMERICAL_COLS),
            ('cat', categorical_pipeline, self.config.CATEGORICAL_COLS)
        ])
        return preprocessor

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> 'FeaturePreprocessor':
        """
        Fit the preprocessor on training data.

        Parameters
        ----------
        X : pd.DataFrame
            Feature matrix.
        y : pd.Series, optional
            Target variable (for encoding target if needed).

        Returns
        -------
        self
        """
        logger.info("Fitting preprocessor...")
        self.preprocessor = self._create_preprocessor_pipeline()
        self.preprocessor.fit(X)
        if y is not None:
            self.target_encoder = LabelEncoder()
            self.target_encoder.fit(y)
        logger.info("Preprocessor fitted successfully.")
        return self

    def transform(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Transform features and optionally target.

        Parameters
        ----------
        X : pd.DataFrame
            Feature matrix.
        y : pd.Series, optional
            Target variable.

        Returns
        -------
        X_transformed : np.ndarray
            Transformed features.
        y_transformed : np.ndarray, optional
            Transformed target (if y provided).
        """
        if self.preprocessor is None:
            raise ValueError("Preprocessor not fitted. Call fit() first.")
        X_transformed = self.preprocessor.transform(X)
        if y is not None:
            if self.target_encoder is None:
                raise ValueError("Target encoder not fitted. Provide y in fit() or fit separately.")
            y_transformed = self.target_encoder.transform(y)
            return X_transformed, y_transformed
        return X_transformed, None

    def fit_transform(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """Convenience method to fit and transform in one step."""
        self.fit(X, y)
        return self.transform(X, y)

    def inverse_transform_target(self, y_encoded: np.ndarray) -> np.ndarray:
        """Convert encoded target back to original labels."""
        if self.target_encoder is None:
            raise ValueError("Target encoder not fitted.")
        return self.target_encoder.inverse_transform(y_encoded)


# ----------------------------- Model Trainer --------------------------------
class ModelTrainer:
    """
    Train and evaluate multiple classification models with hyperparameter tuning.
    """
    def __init__(self, config: Config):
        self.config = config
        self.models: Dict[str, Any] = {}
        self.best_model = None
        self.results: pd.DataFrame = pd.DataFrame()

    def _get_models(self) -> Dict[str, Any]:
        """Define candidate models."""
        return {
            "Logistic Regression": LogisticRegression(max_iter=1000, random_state=self.config.RANDOM_STATE),
            "Decision Tree": DecisionTreeClassifier(random_state=self.config.RANDOM_STATE),
            "Random Forest": RandomForestClassifier(random_state=self.config.RANDOM_STATE, n_jobs=self.config.N_JOBS),
            "Gradient Boosting": GradientBoostingClassifier(random_state=self.config.RANDOM_STATE),
            "XGBoost": XGBClassifier(random_state=self.config.RANDOM_STATE, use_label_encoder=False, eval_metric='mlogloss'),
            "SVM": SVC(probability=True, random_state=self.config.RANDOM_STATE),
            "AdaBoost": AdaBoostClassifier(random_state=self.config.RANDOM_STATE),
        }

    def _get_param_grid(self, model_name: str) -> Dict[str, Any]:
        """
        Define hyperparameter grids for each model.
        """
        grids = {
            "Logistic Regression": {
                'C': [0.01, 0.1, 1, 10],
                'penalty': ['l2'],
                'solver': ['lbfgs', 'newton-cg']
            },
            "Decision Tree": {
                'max_depth': [3, 5, 10, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            },
            "Random Forest": {
                'n_estimators': [100, 200, 300],
                'max_depth': [10, 20, None],
                'min_samples_split': [2, 5, 10]
            },
            "Gradient Boosting": {
                'n_estimators': [100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7]
            },
            "XGBoost": {
                'n_estimators': [100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7],
                'subsample': [0.8, 1.0]
            },
            "SVM": {
                'C': [0.1, 1, 10],
                'gamma': ['scale', 'auto'],
                'kernel': ['rbf', 'linear']
            },
            "AdaBoost": {
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.5, 1.0, 1.5]
            }
        }
        return grids.get(model_name, {})

    def train_and_evaluate(self, X_train: np.ndarray, y_train: np.ndarray,
                           X_test: np.ndarray, y_test: np.ndarray) -> pd.DataFrame:
        """
        Train all models with cross-validation and hyperparameter tuning,
        evaluate on test set.

        Parameters
        ----------
        X_train, y_train : np.ndarray
            Training data.
        X_test, y_test : np.ndarray
            Test data.

        Returns
        -------
        pd.DataFrame
            Results summary for all models.
        """
        models_dict = self._get_models()
        results = []
        cv = StratifiedKFold(n_splits=self.config.CV_FOLDS, shuffle=True, random_state=self.config.RANDOM_STATE)

        for name, model in models_dict.items():
            logger.info(f"Processing model: {name}")
            param_grid = self._get_param_grid(name)
            if param_grid:
                # Use RandomizedSearchCV for efficiency if grid is large
                if len(param_grid) > 3:
                    search = RandomizedSearchCV(
                        model, param_grid, n_iter=self.config.HYPERPARAM_TRIALS,
                        cv=cv, scoring='accuracy', n_jobs=self.config.N_JOBS,
                        random_state=self.config.RANDOM_STATE, verbose=0
                    )
                else:
                    search = GridSearchCV(
                        model, param_grid, cv=cv, scoring='accuracy',
                        n_jobs=self.config.N_JOBS, verbose=0
                    )
                search.fit(X_train, y_train)
                best_model = search.best_estimator_
                best_params = search.best_params_
                cv_score = search.best_score_
            else:
                # No hyperparameter tuning, just cross-validate
                scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='accuracy')
                best_model = model.fit(X_train, y_train)
                best_params = {}
                cv_score = scores.mean()

            # Evaluate on test set
            y_pred = best_model.predict(X_test)
            test_acc = accuracy_score(y_test, y_pred)
            test_f1 = f1_score(y_test, y_pred, average='weighted')
            test_precision = precision_score(y_test, y_pred, average='weighted')
            test_recall = recall_score(y_test, y_pred, average='weighted')

            results.append({
                'Model': name,
                'CV Accuracy (mean)': cv_score,
                'Test Accuracy': test_acc,
                'Test F1 (weighted)': test_f1,
                'Test Precision': test_precision,
                'Test Recall': test_recall,
                'Best Params': str(best_params)
            })
            logger.info(f"Model {name}: Test Acc = {test_acc:.4f}, F1 = {test_f1:.4f}")

        self.results = pd.DataFrame(results)
        # Select best model based on test accuracy
        best_idx = self.results['Test Accuracy'].idxmax()
        best_model_name = self.results.loc[best_idx, 'Model']
        self.best_model = models_dict[best_model_name]
        # Retrain best model with optimal hyperparameters (if found)
        if 'Best Params' in self.results.columns and self.results.loc[best_idx, 'Best Params'] != '{}':
            import ast
            best_params = ast.literal_eval(self.results.loc[best_idx, 'Best Params'])
            self.best_model.set_params(**best_params)
        self.best_model.fit(X_train, y_train)
        logger.info(f"Best model selected: {best_model_name} with test accuracy {self.results.loc[best_idx, 'Test Accuracy']:.4f}")
        return self.results

    def plot_confusion_matrix(self, X_test: np.ndarray, y_test: np.ndarray, class_names: List[str]) -> None:
        """
        Plot confusion matrix for the best model.

        Parameters
        ----------
        X_test, y_test : np.ndarray
            Test data.
        class_names : list of str
            Names of target classes.
        """
        if self.best_model is None:
            raise ValueError("No model trained yet. Call train_and_evaluate first.")
        y_pred = self.best_model.predict(X_test)
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(12, 10))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
        plt.title("Confusion Matrix - Best Model")
        plt.xlabel("Predicted")
        plt.ylabel("Actual")
        plt.tight_layout()
        out_path = os.path.join(self.config.FIGURES_DIR, "confusion_matrix.png")
        plt.savefig(out_path)
        logger.info(f"Confusion matrix saved to {out_path}")
        plt.close()

    def plot_roc_curves(self, X_test: np.ndarray, y_test: np.ndarray, class_names: List[str]) -> None:
        """
        Plot ROC curves for each class (one-vs-rest) for the best model.
        Works only for models with predict_proba or decision_function.
        """
        if self.best_model is None:
            raise ValueError("No model trained.")
        if not hasattr(self.best_model, "predict_proba"):
            logger.warning("Best model does not support predict_proba. ROC curves skipped.")
            return
        y_prob = self.best_model.predict_proba(X_test)
        n_classes = len(class_names)
        plt.figure(figsize=(10, 8))
        for i in range(n_classes):
            fpr, tpr, _ = roc_curve(y_test == i, y_prob[:, i])
            auc = roc_auc_score(y_test == i, y_prob[:, i])
            plt.plot(fpr, tpr, label=f"{class_names[i]} (AUC = {auc:.2f})")
        plt.plot([0, 1], [0, 1], 'k--')
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.title("ROC Curves - One vs Rest")
        plt.legend()
        out_path = os.path.join(self.config.FIGURES_DIR, "roc_curves.png")
        plt.savefig(out_path)
        logger.info(f"ROC curves saved to {out_path}")
        plt.close()


# ----------------------------- Prediction Pipeline --------------------------
class PredictionPipeline:
    """
    End-to-end prediction pipeline using trained preprocessor and model.
    """
    def __init__(self, preprocessor: FeaturePreprocessor, model: Any, target_encoder: LabelEncoder):
        self.preprocessor = preprocessor
        self.model = model
        self.target_encoder = target_encoder

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict class labels for new samples.

        Parameters
        ----------
        X : pd.DataFrame
            Raw feature data (must contain all required columns).

        Returns
        -------
        np.ndarray
            Original target labels.
        """
        # Ensure columns are in the right order (same as during training)
        required_cols = self.preprocessor.config.NUMERICAL_COLS + self.preprocessor.config.CATEGORICAL_COLS
        missing = [c for c in required_cols if c not in X.columns]
        if missing:
            raise ValueError(f"Missing columns: {missing}")
        X_transformed, _ = self.preprocessor.transform(X, y=None)
        y_pred_encoded = self.model.predict(X_transformed)
        y_pred_original = self.target_encoder.inverse_transform(y_pred_encoded)
        return y_pred_original

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Predict class probabilities."""
        if not hasattr(self.model, "predict_proba"):
            raise AttributeError("Model does not support probability predictions.")
        X_transformed, _ = self.preprocessor.transform(X, y=None)
        return self.model.predict_proba(X_transformed)


# ----------------------------- Model Persistence ----------------------------
class ModelPersistence:
    """
    Save and load trained models and preprocessors.
    """
    @staticmethod
    def save_model(model: Any, filepath: str) -> None:
        """Save model using joblib."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(model, filepath)
        logger.info(f"Model saved to {filepath}")

    @staticmethod
    def load_model(filepath: str) -> Any:
        """Load model from file."""
        logger.info(f"Loading model from {filepath}")
        return joblib.load(filepath)

    @staticmethod
    def save_preprocessor(preprocessor: FeaturePreprocessor, filepath: str) -> None:
        """Save preprocessor object."""
        joblib.dump(preprocessor, filepath)
        logger.info(f"Preprocessor saved to {filepath}")

    @staticmethod
    def load_preprocessor(filepath: str) -> FeaturePreprocessor:
        """Load preprocessor."""
        return joblib.load(filepath)


# ----------------------------- Main Execution -------------------------------
def main(args: argparse.Namespace) -> None:
    """
    Main pipeline execution based on command-line arguments.
    """
    # Setup configuration and logging
    config = Config()
    config.ensure_dirs()
    setup_logging(config.LOG_LEVEL, config.LOG_FILE)

    logger.info("=" * 60)
    logger.info("Obesity Classification Pipeline Started")
    logger.info("=" * 60)

    # Load data
    loader = DataLoader(config)
    if args.data_path:
        df = loader.load(args.data_path)
    else:
        df = loader.load()
    required_cols = config.NUMERICAL_COLS + config.CATEGORICAL_COLS + [config.TARGET_COL]
    if not loader.validate_columns(required_cols):
        logger.error("Column validation failed. Exiting.")
        sys.exit(1)

    # Exploratory Data Analysis (if not skipped)
    if not args.skip_eda:
        explorer = DataExplorer(df, config)
        explorer.run_all()

    # Split data
    X = df[config.NUMERICAL_COLS + config.CATEGORICAL_COLS]
    y = df[config.TARGET_COL]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=config.TEST_SIZE, random_state=config.RANDOM_STATE, stratify=y
    )
    logger.info(f"Train size: {X_train.shape}, Test size: {X_test.shape}")

    # Preprocess
    preprocessor = FeaturePreprocessor(config)
    X_train_trans, y_train_trans = preprocessor.fit_transform(X_train, y_train)
    X_test_trans, y_test_trans = preprocessor.transform(X_test, y_test)
    logger.info(f"Preprocessing completed. Transformed feature shape: {X_train_trans.shape}")

    # Train models
    trainer = ModelTrainer(config)
    results_df = trainer.train_and_evaluate(X_train_trans, y_train_trans, X_test_trans, y_test_trans)
    logger.info("\nModel Evaluation Results:\n" + results_df.to_string())

    # Save results to CSV
    results_path = os.path.join(config.REPORTS_DIR, "model_comparison.csv")
    results_df.to_csv(results_path, index=False)
    logger.info(f"Results saved to {results_path}")

    # Generate evaluation plots
    class_names = preprocessor.target_encoder.classes_.tolist() if preprocessor.target_encoder else []
    if class_names:
        trainer.plot_confusion_matrix(X_test_trans, y_test_trans, class_names)
        trainer.plot_roc_curves(X_test_trans, y_test_trans, class_names)

    # Save model and preprocessor
    if args.save_model:
        ModelPersistence.save_model(trainer.best_model, config.MODEL_PATH)
        ModelPersistence.save_preprocessor(preprocessor, config.PREPROCESSOR_PATH)

    # Prediction demo on a few test samples
    logger.info("Demo prediction on first 5 test samples:")
    demo_samples = X_test.head(5)
    pipeline = PredictionPipeline(preprocessor, trainer.best_model, preprocessor.target_encoder)
    preds = pipeline.predict(demo_samples)
    logger.info(f"True labels: {y_test.head(5).values}")
    logger.info(f"Predicted labels: {preds}")

    logger.info("Pipeline finished successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Obesity Classification Supervised Learning Pipeline")
    parser.add_argument("--data_path", type=str, help="Path to CSV data file (overrides config)")
    parser.add_argument("--skip_eda", action="store_true", help="Skip exploratory data analysis")
    parser.add_argument("--save_model", action="store_true", help="Save trained model and preprocessor")
    parser.add_argument("--load_model", type=str, help="Path to saved model (not implemented in main, for future)")
    args = parser.parse_args()
    main(args)
