"""Train baseline models using only metadata features (no skillability)."""
import json
import sys
import os
from pathlib import Path

# Ensure project root is on path when run directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from validation.models import (
    select_features,
    dicts_to_matrix,
    train_logistic_regression,
    train_random_forest,
    train_xgboost,
    cross_validate_model,
    compute_metrics,
    save_model_results,
    BASELINE_FEATURE_PREFIXES,
)
from validation.config_validation import VALIDATION_OUTPUT_DIR, RANDOM_STATE


def train_and_evaluate_baseline(data_dir: str, output_dir: str):
    """
    Load preprocessed data, select baseline features, train 3 models,
    evaluate with 5-fold CV and holdout test set.

    Save to output_dir/models/baseline_results.json:
    {
        "feature_set": "baseline",
        "features_used": [...],
        "models": {
            "logistic_regression": {"cv_auc_mean": ..., "cv_auc_std": ..., "test_auc": ..., "test_pr_auc": ...},
            "random_forest": {...},
            "xgboost": {...}
        }
    }
    """
    data_dir = Path(data_dir)
    output_dir = Path(output_dir)

    print("Loading data...")
    with open(data_dir / "feature_names_classification.json") as f:
        feature_names = json.load(f)

    with open(data_dir / "X_train_classification.json") as f:
        X_train_full = json.load(f)

    with open(data_dir / "y_train_classification.json") as f:
        y_train = json.load(f)

    with open(data_dir / "X_test_classification.json") as f:
        X_test_full = json.load(f)

    with open(data_dir / "y_test_classification.json") as f:
        y_test = json.load(f)

    print(f"Train size: {len(X_train_full)}, Test size: {len(X_test_full)}")

    # Select baseline features only (metadata — no skillability dimensions)
    print("Selecting baseline features...")
    X_train_filtered, selected_names = select_features(
        X_train_full, feature_names, BASELINE_FEATURE_PREFIXES
    )
    X_test_filtered, _ = select_features(
        X_test_full, feature_names, BASELINE_FEATURE_PREFIXES
    )

    print(f"Selected {len(selected_names)} baseline features: {selected_names}")

    # Convert to numpy matrices
    X_train_mat = dicts_to_matrix(X_train_filtered, selected_names)
    X_test_mat = dicts_to_matrix(X_test_filtered, selected_names)

    import numpy as np
    y_train_arr = np.array(y_train)
    y_test_arr = np.array(y_test)

    print(f"Train matrix shape: {X_train_mat.shape}")
    print(f"Test matrix shape: {X_test_mat.shape}")
    print(f"Train positive rate: {y_train_arr.mean():.4f}")
    print(f"Test positive rate: {y_test_arr.mean():.4f}")

    model_configs = [
        ("logistic_regression", train_logistic_regression),
        ("random_forest", train_random_forest),
        ("xgboost", train_xgboost),
    ]

    models_results = {}

    for model_name, model_fn in model_configs:
        print(f"\nTraining {model_name}...")

        # Cross-validation
        print(f"  Running 5-fold cross-validation...")
        cv_results = cross_validate_model(model_fn, X_train_mat, y_train_arr)

        # Train on full training set and evaluate on test set
        print(f"  Training on full train set and evaluating on test set...")
        final_model = model_fn(X_train_mat, y_train_arr)
        y_pred_proba = final_model.predict_proba(X_test_mat)[:, 1]
        test_metrics = compute_metrics(y_test_arr, y_pred_proba)

        models_results[model_name] = {
            "cv_auc_mean": cv_results["mean_auc"],
            "cv_auc_std": cv_results["std_auc"],
            "cv_pr_auc_mean": cv_results["mean_pr_auc"],
            "cv_pr_auc_std": cv_results["std_pr_auc"],
            "cv_fold_results": cv_results["fold_results"],
            "test_auc": test_metrics["auc_roc"],
            "test_pr_auc": test_metrics["pr_auc"],
            "test_precision_at_k": test_metrics["precision_at_k"],
        }

        print(f"  CV AUC: {cv_results['mean_auc']:.4f} +/- {cv_results['std_auc']:.4f}")
        print(f"  Test AUC: {test_metrics['auc_roc']:.4f}, Test PR-AUC: {test_metrics['pr_auc']:.4f}")

    # Compile final results
    results = {
        "feature_set": "baseline",
        "features_used": selected_names,
        "n_features": len(selected_names),
        "n_train": len(y_train),
        "n_test": len(y_test),
        "train_positive_rate": float(y_train_arr.mean()),
        "test_positive_rate": float(y_test_arr.mean()),
        "models": models_results,
    }

    output_path = output_dir / "models" / "baseline_results.json"
    save_model_results(results, str(output_path))
    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Train baseline classification models.")
    parser.add_argument(
        "--data-dir",
        default=VALIDATION_OUTPUT_DIR,
        help="Directory containing preprocessed data files",
    )
    parser.add_argument(
        "--output-dir",
        default=VALIDATION_OUTPUT_DIR,
        help="Directory for saving results",
    )
    args = parser.parse_args()

    results = train_and_evaluate_baseline(args.data_dir, args.output_dir)

    print("\n=== Summary ===")
    for model_name, metrics in results["models"].items():
        print(
            f"{model_name}: Test AUC={metrics['test_auc']:.4f}, "
            f"PR-AUC={metrics['test_pr_auc']:.4f}, "
            f"CV AUC={metrics['cv_auc_mean']:.4f}+/-{metrics['cv_auc_std']:.4f}"
        )
