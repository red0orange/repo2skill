#!/usr/bin/env python3
"""Generate validation figures for paper."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import roc_curve, precision_recall_curve, auc
from sklearn.calibration import calibration_curve
import xgboost as xgb

from config_validation import VALIDATION_OUTPUT_DIR

# Fix path resolution - config gives relative path from project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
OUTPUT_DIR = PROJECT_ROOT / VALIDATION_OUTPUT_DIR
FIGURES_DIR = OUTPUT_DIR / "figures"
ANALYSIS_DIR = OUTPUT_DIR / "analysis"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
sns.set_style("whitegrid")

def load_data():
    """Load test data."""
    with open(OUTPUT_DIR / "X_test_classification.json") as f:
        X_test_dicts = json.load(f)
    with open(OUTPUT_DIR / "y_test_classification.json") as f:
        y_test = np.array(json.load(f), dtype=int)
    with open(OUTPUT_DIR / "X_train_classification.json") as f:
        X_train_dicts = json.load(f)
    with open(OUTPUT_DIR / "y_train_classification.json") as f:
        y_train = np.array(json.load(f), dtype=int)
    with open(OUTPUT_DIR / "feature_names_classification.json") as f:
        feature_names = json.load(f)

    # Convert dicts to arrays
    X_test = np.array([[d[f] for f in feature_names] for d in X_test_dicts], dtype=float)
    X_train = np.array([[d[f] for f in feature_names] for d in X_train_dicts], dtype=float)

    return X_train, y_train, X_test, y_test, feature_names

def train_models(X_train, y_train):
    """Train baseline and full models."""
    scale_pos_weight = np.sum(y_train == 0) / np.sum(y_train == 1)

    baseline_model = xgb.XGBClassifier(scale_pos_weight=scale_pos_weight, random_state=42, eval_metric='logloss')
    baseline_model.fit(X_train[:, :2], y_train)

    full_model = xgb.XGBClassifier(scale_pos_weight=scale_pos_weight, random_state=42, eval_metric='logloss')
    full_model.fit(X_train, y_train)

    return baseline_model, full_model

def plot_roc_pr_curves(X_test, y_test, baseline_model, full_model):
    """Generate ROC and PR curves."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    baseline_proba = baseline_model.predict_proba(X_test[:, :2])[:, 1]
    full_proba = full_model.predict_proba(X_test)[:, 1]

    baseline_fpr, baseline_tpr, _ = roc_curve(y_test, baseline_proba)
    full_fpr, full_tpr, _ = roc_curve(y_test, full_proba)
    axes[0].plot(baseline_fpr, baseline_tpr, label=f'Baseline (AUC={auc(baseline_fpr, baseline_tpr):.4f})', linewidth=2)
    axes[0].plot(full_fpr, full_tpr, label=f'Full Model (AUC={auc(full_fpr, full_tpr):.4f})', linewidth=2)
    axes[0].plot([0, 1], [0, 1], 'k--', alpha=0.3)
    axes[0].set_xlabel('False Positive Rate')
    axes[0].set_ylabel('True Positive Rate')
    axes[0].set_title('ROC Curves')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    baseline_prec, baseline_rec, _ = precision_recall_curve(y_test, baseline_proba)
    full_prec, full_rec, _ = precision_recall_curve(y_test, full_proba)
    axes[1].plot(baseline_rec, baseline_prec, label=f'Baseline (AUC={auc(baseline_rec, baseline_prec):.4f})', linewidth=2)
    axes[1].plot(full_rec, full_prec, label=f'Full Model (AUC={auc(full_rec, full_prec):.4f})', linewidth=2)
    axes[1].axhline(y=y_test.mean(), color='k', linestyle='--', alpha=0.3, label='Random')
    axes[1].set_xlabel('Recall')
    axes[1].set_ylabel('Precision')
    axes[1].set_title('Precision-Recall Curves')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "roc_pr_curves.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved ROC/PR curves")

def plot_feature_importance(full_model, feature_names):
    """Generate feature importance bar chart."""
    importances = full_model.feature_importances_
    indices = np.argsort(importances)[-15:]
    plt.figure(figsize=(10, 6))
    plt.barh(range(len(indices)), importances[indices])
    plt.yticks(range(len(indices)), [feature_names[i] for i in indices])
    plt.xlabel('Feature Importance')
    plt.title('Top 15 Feature Importances (XGBoost)')
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "feature_importance.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved feature importance")

def plot_ablation_study():
    """Generate ablation study plot."""
    with open(ANALYSIS_DIR / "dimension_importance.json") as f:
        data = json.load(f)
    ablation = data["single_dim_auc"]
    dims = list(ablation.keys())
    aucs = list(ablation.values())
    plt.figure(figsize=(10, 6))
    plt.barh(range(len(dims)), aucs)
    plt.yticks(range(len(dims)), dims)
    plt.xlabel('AUC')
    plt.title('Ablation Study: Individual Dimension Performance')
    plt.axvline(x=0.5, color='k', linestyle='--', alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "ablation_study.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved ablation study")

def plot_shap_summary():
    """Generate SHAP summary plot."""
    with open(ANALYSIS_DIR / "dimension_importance.json") as f:
        data = json.load(f)
    shap_data = data["shap_importance"]
    features = list(shap_data.keys())
    values = list(shap_data.values())
    indices = np.argsort(values)[-15:]
    plt.figure(figsize=(10, 6))
    plt.barh(range(len(indices)), [values[i] for i in indices])
    plt.yticks(range(len(indices)), [features[i] for i in indices])
    plt.xlabel('Mean |SHAP Value|')
    plt.title('Top 15 Features by SHAP Importance')
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "shap_summary.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved SHAP summary")

def plot_calibration_curves(X_test, y_test, baseline_model, full_model):
    """Generate calibration curves."""
    baseline_proba = baseline_model.predict_proba(X_test[:, :2])[:, 1]
    full_proba = full_model.predict_proba(X_test)[:, 1]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, proba, name in [(axes[0], baseline_proba, 'Baseline'), (axes[1], full_proba, 'Full Model')]:
        frac_pos, mean_pred = calibration_curve(y_test, proba, n_bins=10)
        ax.plot(mean_pred, frac_pos, 's-', label='Model')
        ax.plot([0, 1], [0, 1], 'k--', label='Perfect')
        ax.set_xlabel('Predicted Probability')
        ax.set_ylabel('Actual Fraction')
        ax.set_title(f'{name} Calibration')
        ax.legend()
        ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "calibration_curves.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved calibration curves")

if __name__ == "__main__":
    print("Loading data...")
    X_train, y_train, X_test, y_test, feature_names = load_data()
    print("Training models...")
    baseline_model, full_model = train_models(X_train, y_train)
    print("Generating figures...")
    plot_roc_pr_curves(X_test, y_test, baseline_model, full_model)
    plot_feature_importance(full_model, feature_names)
    plot_ablation_study()
    plot_shap_summary()
    plot_calibration_curves(X_test, y_test, baseline_model, full_model)
    print("\nAll validation figures generated successfully!")

