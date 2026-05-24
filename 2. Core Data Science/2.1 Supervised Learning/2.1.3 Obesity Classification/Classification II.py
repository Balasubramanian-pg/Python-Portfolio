#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Obesity Classification - Explainability, Ensembles, and Production Readiness
======================================================================================

This module extends the basic supervised learning pipeline with advanced techniques:
    - Model explainability (SHAP, LIME, Partial Dependence)
    - Calibration and reliability curves
    - Threshold tuning for business metrics
    - Stacking and voting ensembles
    - Feature importance and selection
    - Adversarial validation for data shift
    - Concept drift detection
    - A/B testing framework for model comparison
    - Production inference optimizations
    - Model monitoring and alerting

Author: Data Science Team (Advanced Analytics)
Date: 2026-05-24
Version: 3.0
"""

import json
import logging
import pickle
import warnings
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.special import softmax
from scipy.stats import ks_2samp, wasserstein_distance
from sklearn.base import BaseEstimator, ClassifierMixin, clone
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.ensemble import StackingClassifier, VotingClassifier
from sklearn.inspection import partial_dependence
from sklearn.metrics import (
    brier_score_loss,
    classification_report,
    confusion_matrix,
    f1_score,
    log_loss,
    precision_recall_curve,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.utils import resample

# Optional advanced libraries
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    warnings.warn("SHAP not installed. Install with: pip install shap")

try:
    from lime.lime_tabular import LimeTabularExplainer
    LIME_AVAILABLE = True
except ImportError:
    LIME_AVAILABLE = False
    warnings.warn("LIME not installed. Install with: pip install lime")

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

logger = logging.getLogger(__name__)


# ----------------------------- Advanced Configuration ------------------------
class AdvancedConfig:
    """Configuration for advanced analysis and production features."""
    # SHAP settings
    SHAP_SAMPLE_SIZE = 100  # Number of background samples for KernelExplainer
    SHAP_PLOT_TOP_FEATURES = 15

    # Calibration settings
    CALIBRATION_METHOD = 'sigmoid'  # 'sigmoid' or 'isotonic'
    CALIBRATION_CV = 5

    # Threshold optimization
    THRESHOLD_OPTIMIZATION_METRIC = 'f1'  # 'f1', 'precision', 'recall', 'cost'
    COST_MATRIX = {  # False Positive and False Negative costs (business-specific)
        'FN_cost': 10.0,  # Missing an obese patient (high cost)
        'FP_cost': 1.0    # False alarm (low cost)
    }

    # Ensemble settings
    ENSEMBLE_USE_STACKING = True
    STACKING_META_LEARNER = 'logistic'  # 'logistic' or 'random_forest'

    # Drift detection
    DRIFT_ALPHA = 0.05
    DRIFT_WINDOW_SIZE = 1000  # Number of samples to monitor per batch

    # A/B testing
    AB_TEST_TRAFFIC_SPLIT = 0.5  # 50% control, 50% treatment
    AB_TEST_CONFIDENCE_LEVEL = 0.95

    # Monitoring
    MONITOR_METRICS = ['accuracy', 'f1', 'log_loss', 'brier_score']


# ----------------------------- Model Explainability -------------------------
class ModelExplainer:
    """
    Provide model interpretability using SHAP and LIME.
    """
    def __init__(self, model: Any, preprocessor: Any, X_train: np.ndarray,
                 feature_names: List[str], config: AdvancedConfig):
        self.model = model
        self.preprocessor = preprocessor
        self.X_train = X_train
        self.feature_names = feature_names
        self.config = config
        self.shap_explainer = None
        self.lime_explainer = None

    def fit_shap(self, sample_X: Optional[np.ndarray] = None) -> None:
        """
        Initialize SHAP explainer (KernelExplainer for any model).
        """
        if not SHAP_AVAILABLE:
            logger.warning("SHAP not available. Skipping SHAP explanation.")
            return
        background = sample_X if sample_X is not None else self.X_train[:self.config.SHAP_SAMPLE_SIZE]
        logger.info("Initializing SHAP KernelExplainer...")
        # For classification, use model.predict_proba
        def predict_proba_wrapper(x):
            return self.model.predict_proba(x)
        self.shap_explainer = shap.KernelExplainer(predict_proba_wrapper, background)
        logger.info("SHAP explainer ready.")

    def explain_instance(self, X_instance: np.ndarray, class_idx: int = 0) -> Optional[Any]:
        """
        Generate SHAP values for a single instance.

        Parameters
        ----------
        X_instance : np.ndarray
            Single sample (must be preprocessed).
        class_idx : int
            Class index to explain.

        Returns
        -------
        SHAP values or None if not available.
        """
        if self.shap_explainer is None:
            logger.error("SHAP explainer not fitted. Call fit_shap first.")
            return None
        shap_values = self.shap_explainer.shap_values(X_instance.reshape(1, -1))
        # shap_values is list for multi-class, index by class
        if isinstance(shap_values, list):
            return shap_values[class_idx]
        return shap_values

    def plot_shap_summary(self, X_sample: np.ndarray, class_names: List[str]) -> None:
        """
        Create SHAP summary plot for a sample of data.
        """
        if not SHAP_AVAILABLE or self.shap_explainer is None:
            logger.warning("SHAP not available or not initialized.")
            return
        shap_values = self.shap_explainer.shap_values(X_sample)
        plt.figure(figsize=(12, 8))
        # For multi-class, plot for each class or use max prediction
        if isinstance(shap_values, list):
            # Plot for class with highest average prediction
            avg_pred = self.model.predict_proba(X_sample).mean(axis=0)
            top_class = np.argmax(avg_pred)
            shap.summary_plot(shap_values[top_class], X_sample, feature_names=self.feature_names, show=False)
            plt.title(f"SHAP Summary - Class: {class_names[top_class]}")
        else:
            shap.summary_plot(shap_values, X_sample, feature_names=self.feature_names, show=False)
        plt.tight_layout()
        plt.savefig("outputs/figures/shap_summary.png")
        plt.close()
        logger.info("SHAP summary plot saved.")

    def lime_explain(self, X_raw: pd.DataFrame, instance_index: int,
                     class_names: List[str]) -> Optional[Any]:
        """
        Generate LIME explanation for a single instance.

        Parameters
        ----------
        X_raw : pd.DataFrame
            Original (untransformed) data.
        instance_index : int
            Index of the instance to explain.
        class_names : list
            Target class names.

        Returns
        -------
        LIME explanation object or None.
        """
        if not LIME_AVAILABLE:
            logger.warning("LIME not available.")
            return None
        # Get transformed training data for LIME explainer
        X_train_transformed = self.X_train
        # Create LIME explainer on raw features? LIME works on transformed space typically.
        # Simpler: use original feature space with custom mapping.
        # For brevity, we'll use a simplified LIME tabular explainer.
        feature_names_raw = X_raw.columns.tolist()
        lime_explainer = LimeTabularExplainer(
            X_raw.values,
            feature_names=feature_names_raw,
            class_names=class_names,
            mode='classification',
            training_labels=self.preprocessor.target_encoder.transform(X_raw[self.preprocessor.config.TARGET_COL]) if hasattr(self.preprocessor, 'target_encoder') else None
        )
        instance = X_raw.iloc[instance_index].values.reshape(1, -1)
        exp = lime_explainer.explain_instance(instance[0], self.model.predict_proba, num_features=10)
        exp.save_to_file("outputs/figures/lime_explanation.html")
        logger.info(f"LIME explanation saved for instance {instance_index}")
        return exp


# ----------------------------- Model Calibration ----------------------------
class ModelCalibrator:
    """
    Calibrate model probabilities using Platt scaling or isotonic regression.
    """
    def __init__(self, config: AdvancedConfig):
        self.config = config
        self.calibrated_model = None

    def calibrate(self, model: Any, X_train: np.ndarray, y_train: np.ndarray) -> Any:
        """
        Return a calibrated version of the model.
        """
        logger.info(f"Calibrating model using {self.config.CALIBRATION_METHOD}...")
        calibrated = CalibratedClassifierCV(
            model, method=self.config.CALIBRATION_METHOD,
            cv=self.config.CALIBRATION_CV
        )
        calibrated.fit(X_train, y_train)
        self.calibrated_model = calibrated
        logger.info("Calibration completed.")
        return calibrated

    def plot_calibration_curve(self, model: Any, X_test: np.ndarray, y_test: np.ndarray,
                               class_idx: int = 0) -> None:
        """
        Plot reliability curve for a specific class.
        """
        proba = model.predict_proba(X_test)[:, class_idx]
        fraction_of_positives, mean_predicted_value = calibration_curve(
            y_test == class_idx, proba, n_bins=10
        )
        plt.figure(figsize=(8, 6))
        plt.plot(mean_predicted_value, fraction_of_positives, 's-', label='Model')
        plt.plot([0, 1], [0, 1], 'k--', label='Perfectly calibrated')
        plt.xlabel('Mean predicted probability')
        plt.ylabel('Fraction of positives')
        plt.title(f'Calibration curve (Class {class_idx})')
        plt.legend()
        plt.tight_layout()
        plt.savefig("outputs/figures/calibration_curve.png")
        plt.close()
        logger.info("Calibration curve saved.")

    def brier_score(self, model: Any, X_test: np.ndarray, y_test: np.ndarray) -> float:
        """
        Compute Brier score (lower is better).
        """
        proba = model.predict_proba(X_test)
        if proba.shape[1] > 2:
            # Multi-class: use average Brier score
            brier = np.mean([brier_score_loss(y_test == i, proba[:, i]) for i in range(proba.shape[1])])
        else:
            brier = brier_score_loss(y_test, proba[:, 1])
        logger.info(f"Brier score: {brier:.4f}")
        return brier


# ----------------------------- Threshold Optimization -----------------------
class ThresholdOptimizer:
    """
    Optimize classification threshold based on business metrics.
    """
    def __init__(self, config: AdvancedConfig):
        self.config = config
        self.optimal_thresholds = {}

    def find_optimal_threshold(self, y_true: np.ndarray, y_proba: np.ndarray,
                               metric: str = 'f1') -> float:
        """
        Find threshold that maximizes the chosen metric (for binary or one-vs-rest).

        Parameters
        ----------
        y_true : binary array (0/1)
        y_proba : predicted probabilities for positive class
        metric : 'f1', 'precision', 'recall', 'cost'

        Returns
        -------
        best_threshold : float
        """
        precision, recall, thresholds = precision_recall_curve(y_true, y_proba)
        # Remove last threshold (1.0) because precision/recall have n_thresholds+1 points
        thresholds = thresholds[:-1] if len(thresholds) > len(precision) else thresholds
        if metric == 'f1':
            f1_scores = 2 * (precision[:-1] * recall[:-1]) / (precision[:-1] + recall[:-1] + 1e-8)
            best_idx = np.argmax(f1_scores)
        elif metric == 'precision':
            best_idx = np.argmax(precision[:-1])
        elif metric == 'recall':
            best_idx = np.argmax(recall[:-1])
        elif metric == 'cost':
            fn_cost = self.config.COST_MATRIX['FN_cost']
            fp_cost = self.config.COST_MATRIX['FP_cost']
            n_pos = y_true.sum()
            n_neg = len(y_true) - n_pos
            # Total cost = FP * fp_cost + FN * fn_cost
            # Approximate from threshold
            costs = []
            for t in thresholds:
                y_pred = (y_proba >= t).astype(int)
                tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
                cost = fp * fp_cost + fn * fn_cost
                costs.append(cost)
            best_idx = np.argmin(costs)
        else:
            raise ValueError(f"Unknown metric: {metric}")
        best_threshold = thresholds[best_idx]
        logger.info(f"Optimal threshold for {metric}: {best_threshold:.4f}")
        return best_threshold

    def optimize_for_model(self, model: Any, X_val: np.ndarray, y_val: np.ndarray,
                           n_classes: int) -> Dict[int, float]:
        """
        Compute optimal thresholds for each class (one-vs-rest).
        """
        proba = model.predict_proba(X_val)
        thresholds = {}
        for i in range(n_classes):
            y_true_bin = (y_val == i).astype(int)
            y_proba = proba[:, i]
            thr = self.find_optimal_threshold(y_true_bin, y_proba, metric=self.config.THRESHOLD_OPTIMIZATION_METRIC)
            thresholds[i] = thr
        self.optimal_thresholds = thresholds
        return thresholds

    def apply_thresholds(self, proba: np.ndarray) -> np.ndarray:
        """
        Apply optimized thresholds to probability matrix.
        Assumes thresholds are stored for each class.
        """
        if not self.optimal_thresholds:
            raise ValueError("No thresholds found. Run optimize_for_model first.")
        n_classes = len(self.optimal_thresholds)
        # One-vs-rest: assign class if proba > threshold, else 0, then argmax
        binary_preds = np.zeros_like(proba)
        for i in range(n_classes):
            binary_preds[:, i] = (proba[:, i] >= self.optimal_thresholds[i]).astype(int)
        # In case of multiple positive classes, choose the one with highest proba
        # Simpler: use argmax but override with thresholded? For robustness:
        final_preds = np.argmax(proba, axis=1)
        # If threshold not met for predicted class, set to default (most frequent)
        for i in range(proba.shape[0]):
            pred_class = final_preds[i]
            if proba[i, pred_class] < self.optimal_thresholds[pred_class]:
                # Fallback: choose class with highest probability above threshold
                candidates = [c for c in range(n_classes) if proba[i, c] >= self.optimal_thresholds[c]]
                if candidates:
                    final_preds[i] = max(candidates, key=lambda c: proba[i, c])
                # else keep original (or we could set to 0)
        return final_preds


# ----------------------------- Advanced Ensembles ---------------------------
class AdvancedEnsemble:
    """
    Build stacking and voting ensembles for better performance.
    """
    def __init__(self, config: AdvancedConfig):
        self.config = config
        self.ensemble_model = None

    def build_stacking(self, base_models: List[Tuple[str, Any]], X_train: np.ndarray,
                       y_train: np.ndarray) -> StackingClassifier:
        """
        Create a stacking ensemble with cross-validated predictions.
        """
        if self.config.STACKING_META_LEARNER == 'logistic':
            meta_learner = LogisticRegression(max_iter=1000, random_state=42)
        else:
            meta_learner = RandomForestClassifier(n_estimators=100, random_state=42)

        stacking = StackingClassifier(
            estimators=base_models,
            final_estimator=meta_learner,
            cv=5,
            stack_method='predict_proba'
        )
        stacking.fit(X_train, y_train)
        self.ensemble_model = stacking
        logger.info("Stacking ensemble created and trained.")
        return stacking

    def build_voting(self, base_models: List[Tuple[str, Any]], voting: str = 'soft') -> VotingClassifier:
        """
        Create a voting classifier (soft or hard).
        """
        voting_clf = VotingClassifier(estimators=base_models, voting=voting)
        self.ensemble_model = voting_clf
        logger.info(f"Voting ensemble ({voting}) created.")
        return voting_clf


# ----------------------------- Adversarial Validation -----------------------
class AdversarialValidator:
    """
    Detect data shift between train and test sets using a classifier.
    """
    def __init__(self, config: AdvancedConfig):
        self.config = config
        self.adversarial_model = None
        self.performance = None

    def run_adversarial_check(self, X_train: pd.DataFrame, X_test: pd.DataFrame,
                              target_col: Optional[str] = None) -> float:
        """
        Train a classifier to distinguish train vs test. High AUC indicates shift.

        Returns
        -------
        auc : float
            ROC-AUC of the adversarial classifier.
        """
        # Create labels: 0 for train, 1 for test
        train_labels = np.zeros(X_train.shape[0])
        test_labels = np.ones(X_test.shape[0])
        X_combined = pd.concat([X_train, X_test], axis=0)
        y_combined = np.concatenate([train_labels, test_labels])

        # Simple model (e.g., RandomForest) to detect shift
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import cross_val_score

        model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        cv_scores = cross_val_score(model, X_combined, y_combined, cv=5, scoring='roc_auc')
        mean_auc = np.mean(cv_scores)
        logger.info(f"Adversarial validation AUC: {mean_auc:.4f}")
        if mean_auc > 0.7:
            logger.warning("Significant data shift detected between train and test sets!")
        else:
            logger.info("No severe data shift detected.")
        self.performance = mean_auc
        return mean_auc


# ----------------------------- Concept Drift Detection ----------------------
class ConceptDriftDetector:
    """
    Monitor model performance over time using statistical tests.
    """
    def __init__(self, config: AdvancedConfig, reference_data: np.ndarray,
                 reference_predictions: np.ndarray, reference_targets: np.ndarray):
        self.config = config
        self.ref_data = reference_data
        self.ref_preds = reference_predictions
        self.ref_targets = reference_targets
        self.drift_alerts = []

    def detect_drift(self, new_data: np.ndarray, new_targets: np.ndarray,
                     window_size: int = 1000) -> Dict[str, Any]:
        """
        Detect drift using KS test (feature distribution) and performance drop.

        Returns
        -------
        dict with drift status and metrics.
        """
        # Feature distribution drift (KS test for each feature)
        drift_features = []
        for i in range(self.ref_data.shape[1]):
            ks_stat, p_value = ks_2samp(self.ref_data[:, i], new_data[:, i])
            if p_value < self.config.DRIFT_ALPHA:
                drift_features.append(i)
        # Performance drift (accuracy drop)
        from sklearn.metrics import accuracy_score
        ref_acc = accuracy_score(self.ref_targets, self.ref_preds)
        new_preds = self.ref_preds  # In real scenario, predict with model
        # Simulating: we need the model to predict on new data; we assume it's passed
        # For brevity, we assume new_preds is provided separately.
        # We'll compute accuracy on new data if targets given.
        if new_targets is not None and new_preds is not None:
            new_acc = accuracy_score(new_targets, new_preds)
            acc_drop = ref_acc - new_acc
        else:
            acc_drop = 0.0

        drift_detected = (len(drift_features) > 0) or (acc_drop > 0.05)
        alert = {
            'timestamp': datetime.now(),
            'drift_detected': drift_detected,
            'drifted_features': drift_features,
            'accuracy_drop': acc_drop,
            'ks_stats': [ks_2samp(self.ref_data[:, i], new_data[:, i])[0] for i in range(self.ref_data.shape[1])]
        }
        if drift_detected:
            self.drift_alerts.append(alert)
            logger.warning(f"Concept drift detected at {alert['timestamp']}. Features: {drift_features}")
        return alert


# ----------------------------- A/B Testing Framework ------------------------
class ABTestFramework:
    """
    Compare two models (control vs treatment) using online A/B testing.
    """
    def __init__(self, config: AdvancedConfig):
        self.config = config
        self.results = {'control': [], 'treatment': []}

    def assign_treatment(self, user_id: str) -> str:
        """
        Deterministic assignment based on hash to ensure consistency.
        """
        import hashlib
        hash_val = int(hashlib.md5(user_id.encode()).hexdigest(), 16) % 100
        if hash_val < self.config.AB_TEST_TRAFFIC_SPLIT * 100:
            return 'treatment'
        else:
            return 'control'

    def log_prediction(self, user_id: str, model_name: str, predicted_class: int,
                       actual_class: Optional[int] = None, metadata: Dict = None):
        """
        Log prediction for later analysis.
        """
        record = {
            'timestamp': datetime.now(),
            'user_id': user_id,
            'model': model_name,
            'prediction': predicted_class,
            'actual': actual_class,
            'metadata': metadata or {}
        }
        if model_name == 'control':
            self.results['control'].append(record)
        else:
            self.results['treatment'].append(record)

    def evaluate_ab_test(self, metric: str = 'accuracy') -> Dict[str, Any]:
        """
        Compare performance of control and treatment using statistical test.
        """
        from scipy.stats import chi2_contingency, ttest_ind
        # Collect actual vs predicted for both groups
        control_correct = sum(1 for r in self.results['control'] if r['actual'] is not None and r['prediction'] == r['actual'])
        control_total = len([r for r in self.results['control'] if r['actual'] is not None])
        treat_correct = sum(1 for r in self.results['treatment'] if r['actual'] is not None and r['prediction'] == r['actual'])
        treat_total = len([r for r in self.results['treatment'] if r['actual'] is not None])

        if control_total == 0 or treat_total == 0:
            return {'error': 'Insufficient data'}

        # 2x2 contingency table for accuracy
        table = np.array([[control_correct, control_total - control_correct],
                          [treat_correct, treat_total - treat_correct]])
        chi2, p, dof, expected = chi2_contingency(table)
        significant = p < (1 - self.config.AB_TEST_CONFIDENCE_LEVEL)
        result = {
            'control_accuracy': control_correct / control_total,
            'treatment_accuracy': treat_correct / treat_total,
            'p_value': p,
            'significant': significant,
            'sample_sizes': (control_total, treat_total)
        }
        logger.info(f"A/B Test result: {result}")
        return result


# ----------------------------- Production Inference Optimizations -----------
class InferenceOptimizer:
    """
    Optimize model inference for latency and throughput.
    """
    @staticmethod
    def batch_predict(model: Any, X: np.ndarray, batch_size: int = 32) -> np.ndarray:
        """
        Perform batch prediction to reduce overhead.
        """
        n_samples = X.shape[0]
        predictions = []
        for i in range(0, n_samples, batch_size):
            batch = X[i:i+batch_size]
            preds = model.predict(batch)
            predictions.append(preds)
        return np.concatenate(predictions)

    @staticmethod
    def quantize_model(model: Any, X_calibration: np.ndarray, dtype=np.float16) -> Any:
        """
        Attempt to quantize model weights (simplified; use ONNX or TensorRT for production).
        """
        # This is a placeholder; actual quantization requires framework-specific tools.
        logger.warning("Quantization not fully implemented. Use ONNX or TensorRT for production.")
        return model

    @staticmethod
    def profile_inference(model: Any, X: np.ndarray, n_iterations: int = 100) -> Dict[str, float]:
        """
        Measure inference latency.
        """
        import time
        latencies = []
        for _ in range(n_iterations):
            start = time.perf_counter()
            _ = model.predict(X)
            end = time.perf_counter()
            latencies.append((end - start) * 1000)  # ms
        return {
            'mean_latency_ms': np.mean(latencies),
            'std_latency_ms': np.std(latencies),
            'p95_latency_ms': np.percentile(latencies, 95),
            'p99_latency_ms': np.percentile(latencies, 99)
        }


# ----------------------------- Model Monitoring -----------------------------
class ModelMonitor:
    """
    Monitor model performance and data quality over time.
    """
    def __init__(self, config: AdvancedConfig, model: Any, preprocessor: Any,
                 reference_metrics: Dict[str, float]):
        self.config = config
        self.model = model
        self.preprocessor = preprocessor
        self.reference_metrics = reference_metrics
        self.alerts = []

    def evaluate_performance(self, X: np.ndarray, y_true: np.ndarray) -> Dict[str, float]:
        """
        Compute current performance metrics.
        """
        y_pred = self.model.predict(X)
        if hasattr(self.model, "predict_proba"):
            y_proba = self.model.predict_proba(X)
            logloss = log_loss(y_true, y_proba)
            brier = brier_score_loss(y_true, y_proba[:, 1]) if y_proba.shape[1] == 2 else np.nan
        else:
            logloss = np.nan
            brier = np.nan
        acc = accuracy_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred, average='weighted')
        metrics = {
            'accuracy': acc,
            'f1': f1,
            'log_loss': logloss,
            'brier_score': brier
        }
        return metrics

    def check_drift_vs_reference(self, current_metrics: Dict[str, float],
                                 threshold: float = 0.05) -> bool:
        """
        Alert if any metric drops below reference threshold.
        """
        drift_detected = False
        for metric in self.config.MONITOR_METRICS:
            if metric in current_metrics and metric in self.reference_metrics:
                rel_change = (current_metrics[metric] - self.reference_metrics[metric]) / (self.reference_metrics[metric] + 1e-8)
                if metric in ['log_loss', 'brier_score']:
                    # Lower is better; increase is bad
                    if rel_change > threshold:
                        drift_detected = True
                        alert_msg = f"Metric {metric} degraded: {current_metrics[metric]:.4f} vs ref {self.reference_metrics[metric]:.4f}"
                        logger.warning(alert_msg)
                        self.alerts.append(alert_msg)
                else:
                    # Higher is better; decrease is bad
                    if rel_change < -threshold:
                        drift_detected = True
                        alert_msg = f"Metric {metric} degraded: {current_metrics[metric]:.4f} vs ref {self.reference_metrics[metric]:.4f}"
                        logger.warning(alert_msg)
                        self.alerts.append(alert_msg)
        return drift_detected


# ----------------------------- Integration and Example -----------------------
def advanced_analysis_demo():
    """
    Demonstration of advanced features using the previously trained model.
    This assumes the basic pipeline has already produced a trained model and preprocessor.
    """
    # Load pre-trained objects (from basic pipeline)
    from joblib import load
    config = AdvancedConfig()
    try:
        model = load("models/obesity_classifier.pkl")
        preprocessor = load("models/preprocessor.pkl")
        logger.info("Loaded pre-trained model and preprocessor.")
    except FileNotFoundError:
        logger.error("Pre-trained model not found. Run the basic pipeline first.")
        return

    # Simulate some test data (in practice, load from validation set)
    # For demo, we'll create dummy data
    np.random.seed(42)
    X_dummy = np.random.randn(200, len(preprocessor.config.NUMERICAL_COLS + preprocessor.config.CATEGORICAL_COLS))
    y_dummy = np.random.randint(0, 7, size=200)  # 7 obesity classes

    # 1. Model explainability
    if SHAP_AVAILABLE:
        explainer = ModelExplainer(model, preprocessor, X_dummy, preprocessor.config.NUMERICAL_COLS + preprocessor.config.CATEGORICAL_COLS, config)
        explainer.fit_shap(X_dummy[:100])
        explainer.plot_shap_summary(X_dummy[:50], preprocessor.target_encoder.classes_)

    # 2. Calibration
    calibrator = ModelCalibrator(config)
    calibrated = calibrator.calibrate(model, X_dummy, y_dummy)
    calibrator.plot_calibration_curve(calibrated, X_dummy, y_dummy, class_idx=0)
    brier = calibrator.brier_score(calibrated, X_dummy, y_dummy)
    print(f"Calibrated Brier score: {brier:.4f}")

    # 3. Threshold optimization
    opt = ThresholdOptimizer(config)
    proba = model.predict_proba(X_dummy)
    thresholds = opt.optimize_for_model(model, X_dummy, y_dummy, n_classes=7)
    print("Optimal thresholds:", thresholds)

    # 4. Adversarial validation (requires original train/test splits)
    # We'll simulate with random splits
    X_train_sim = np.random.randn(1000, 10)
    X_test_sim = np.random.randn(500, 10)
    adv = AdversarialValidator(config)
    adv.run_adversarial_check(pd.DataFrame(X_train_sim), pd.DataFrame(X_test_sim))

    # 5. Concept drift detection
    ref_data = X_dummy[:100]
    ref_preds = model.predict(ref_data)
    ref_targets = y_dummy[:100]
    drift_detector = ConceptDriftDetector(config, ref_data, ref_preds, ref_targets)
    new_data = X_dummy[100:200]
    new_targets = y_dummy[100:200]
    drift_alert = drift_detector.detect_drift(new_data, new_targets)
    print("Drift alert:", drift_alert)

    # 6. A/B testing simulation
    ab = ABTestFramework(config)
    # Simulate user predictions
    for user_id in [f"user_{i}" for i in range(100)]:
        group = ab.assign_treatment(user_id)
        # In real scenario, get predictions from both models
        pred = np.random.randint(0, 7)
        actual = np.random.randint(0, 7)
        ab.log_prediction(user_id, group, pred, actual)
    ab_result = ab.evaluate_ab_test()
    print("A/B test result:", ab_result)

    # 7. Inference profiling
    profile = InferenceOptimizer.profile_inference(model, X_dummy[:10])
    print("Inference profile (ms):", profile)

    # 8. Model monitoring
    ref_metrics = {'accuracy': 0.85, 'f1': 0.84, 'log_loss': 0.45}
    monitor = ModelMonitor(config, model, preprocessor, ref_metrics)
    current_metrics = monitor.evaluate_performance(X_dummy, y_dummy)
    drift = monitor.check_drift_vs_reference(current_metrics)
    print("Performance drift detected:", drift)

    logger.info("Advanced analysis demo completed.")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    advanced_analysis_demo()
