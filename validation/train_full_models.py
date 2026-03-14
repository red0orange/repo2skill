"""Train full models: metadata + skillability features."""
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
    FULL_FEATURE_PREFIXES,
)
from validation.config_validation import VALIDATION_OUTPUT_DIR, RANDOM_STATE


def train_and_evaluate_full(data_dir: str, output_dir: str):
    """
    Load preprocessed data, select FULL feature set, train 3 models,
    evaluate with 5-fold CV and holdout test set.

    Load baseline results from output_dir/models/baseline_results.json for comparison.

    Save to output_dir/models/full_results.json:
    {
        "feature_set": "full",
        "features_used": [...],
        "models": {
            "logistic_regression": {
                "cv_auc_mean": ..., "cv_auc_std": ...,
                "test_auc": ..., "test_pr_auc": ...,
                "auc_lift_over_baseline": ...,  # test_auc - baseline_test_auc
            },
            "random_forest": {...},
            "xgboost": {...}
        },
        "best_model": "xgboost",  # model with highest test_auc
        "best_test_auc": ...
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

    # Load baseline results for comparison
    baseline_results_path = output_dir / "models" / "baseline_results.json"
    if not baseline_results_path.exists():
        raise FileNotFoundError(f"Baseline results not found at {baseline_results_path}")

    with open(baseline_results_path) as f:
        baseline_results = json.load(f)

    baseline_test_aucs = {
        model_name: metrics["test_auc"]
        for model_name, metrics in baseline_results["models"].items()
    }

    # Select full features (metadata + skillability dimensions)
    print("Selecting full features...")
    X_train_filtered, selected_names = select_features(
        X_train_full, feature_names, FULL_FEATURE_PREFIXES
    )
    X_test_filtered, _ = select_features(
        X_test_full, feature_names, FULL_FEATURE_PREFIXES
    )

    print(f"Selected {len(selected_names)} full features: {selected_names}")

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

    print("\n=== Full Model Training (with Skillability Features) ===")
    print(f"Features selected: {len(selected_names)} features")

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

        baseline_auc = baseline_test_aucs[model_name]
        auc_lift = test_metrics["auc_roc"] - baseline_auc

        models_results[model_name] = {
            "cv_auc_mean": cv_results["mean_auc"],
            "cv_auc_std": cv_results["std_auc"],
            "cv_pr_auc_mean": cv_results["mean_pr_auc"],
            "cv_pr_auc_std": cv_results["std_pr_auc"],
            "cv_fold_results": cv_results["fold_results"],
            "test_auc": test_metrics["auc_roc"],
            "test_pr_auc": test_metrics["pr_auc"],
            "test_precision_at_k": test_metrics["precision_at_k"],
            "auc_lift_over_baseline": auc_lift,
        }

        print(f"  CV AUC: {cv_results['mean_auc']:.4f} +/- {cv_results['std_auc']:.4f}")
        print(f"  Test AUC: {test_metrics['auc_roc']:.4f}, Test PR-AUC: {test_metrics['pr_auc']:.4f}")

    # Find best model by test AUC
    best_model_name = max(models_results, key=lambda m: models_results[m]["test_auc"])
    best_test_auc = models_results[best_model_name]["test_auc"]

    # Compile final results
    results = {
        "feature_set": "full",
        "features_used": selected_names,
        "n_features": len(selected_names),
        "n_train": len(y_train),
        "n_test": len(y_test),
        "train_positive_rate": float(y_train_arr.mean()),
        "test_positive_rate": float(y_test_arr.mean()),
        "models": models_results,
        "best_model": best_model_name,
        "best_test_auc": best_test_auc,
    }

    output_path = output_dir / "models" / "full_results.json"
    save_model_results(results, str(output_path))
    print(f"\nResults saved to: {output_path}")

    # Print comparison table
    print("\n=== Comparison: Baseline vs Full Model ===")
    print(f"{'Model':<20} | {'Baseline AUC':<15} | {'Full AUC':<15} | {'Lift':<10}")
    print("-" * 65)
    for model_name in ["logistic_regression", "random_forest", "xgboost"]:
        baseline_auc = baseline_test_aucs[model_name]
        full_auc = models_results[model_name]["test_auc"]
        lift = full_auc - baseline_auc
        print(
            f"{model_name:<20} | {baseline_auc:<15.4f} | {full_auc:<15.4f} | {lift:+.4f}"
        )

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Train full classification models with skillability features.")
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

    results = train_and_evaluate_full(args.data_dir, args.output_dir)

    print("\n=== Summary ===")
    print(f"Best model: {results['best_model']} with test AUC: {results['best_test_auc']:.4f}")
    for model_name, metrics in results["models"].items():
        print(
            f"{model_name}: Test AUC={metrics['test_auc']:.4f}, "
            f"PR-AUC={metrics['test_pr_auc']:.4f}, "
            f"CV AUC={metrics['cv_auc_mean']:.4f}+/-{metrics['cv_auc_std']:.4f}, "
            f"Lift={metrics['auc_lift_over_baseline']:+.4f}"
        )
