"""Analyze which skillability dimensions are most predictive."""
import json
import sys
import os
from pathlib import Path

import numpy as np

# Ensure project root is on path when run directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sklearn.metrics import roc_auc_score

from validation.models import (
    select_features,
    dicts_to_matrix,
    train_xgboost,
    FULL_FEATURE_PREFIXES,
)
from validation.config_validation import VALIDATION_OUTPUT_DIR, RANDOM_STATE

# The 6 skillability dimension feature names
SKILLABILITY_DIMS = [
    "task_clarity",
    "interface_clarity",
    "composability",
    "automation_value",
    "deployment_friction",
    "operational_risk",
]


def get_feature_importance_xgboost(model, feature_names) -> dict:
    """Extract XGBoost feature importance scores (gain-based)."""
    # gain-based importance
    importance_dict = model.get_booster().get_score(importance_type="gain")
    # Map f0, f1, ... to actual feature names
    # XGBoost uses feature names if set, otherwise f0, f1, ...
    try:
        # Try to get by feature name directly
        named_importance = {name: float(importance_dict.get(name, 0.0)) for name in feature_names}
    except Exception:
        # Fall back to index-based
        named_importance = {}
        for i, name in enumerate(feature_names):
            key = f"f{i}"
            named_importance[name] = float(importance_dict.get(key, 0.0))

    # Normalize so values sum to 1
    total = sum(named_importance.values())
    if total > 0:
        named_importance = {k: v / total for k, v in named_importance.items()}

    return named_importance


def get_shap_values(model, X_test_matrix, feature_names) -> dict:
    """
    Compute SHAP values for XGBoost model.
    Return: {feature: mean_abs_shap_value for each feature}
    """
    import shap

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test_matrix)

    # shap_values shape: (n_samples, n_features)
    mean_abs_shap = np.abs(shap_values).mean(axis=0)

    return {name: float(val) for name, val in zip(feature_names, mean_abs_shap)}


def dimension_ablation_study(X_train, y_train, X_test, y_test,
                              feature_names, dim_names, n_bootstrap=20) -> dict:
    """
    Ablation: for each skillability dimension, remove it and measure AUC drop.
    dim_names: the 6 skillability dimension names
    Return: {dim_name: auc_drop for each dimension}
    """
    y_train_arr = np.array(y_train)
    y_test_arr = np.array(y_test)

    # Train full model for reference AUC
    print("  Training full model for ablation reference...")
    full_model = train_xgboost(X_train, y_train_arr)
    pred_full = full_model.predict_proba(X_test)[:, 1]
    auc_full = roc_auc_score(y_test_arr, pred_full)
    print(f"  Full model AUC: {auc_full:.4f}")

    ablation_results = {}
    for dim in dim_names:
        if dim not in feature_names:
            print(f"  Dimension '{dim}' not in feature_names, skipping.")
            ablation_results[dim] = None
            continue

        # Find the column index for this dimension
        dim_idx = feature_names.index(dim)

        # Zero out that feature column
        X_train_ablated = X_train.copy()
        X_test_ablated = X_test.copy()
        X_train_ablated[:, dim_idx] = 0.0
        X_test_ablated[:, dim_idx] = 0.0

        # Re-train with that feature zeroed out
        model_ablated = train_xgboost(X_train_ablated, y_train_arr)
        pred_ablated = model_ablated.predict_proba(X_test_ablated)[:, 1]
        auc_ablated = roc_auc_score(y_test_arr, pred_ablated)
        auc_drop = auc_full - auc_ablated

        print(f"  Ablation [{dim}]: AUC={auc_ablated:.4f}, Drop={auc_drop:.4f}")
        ablation_results[dim] = float(auc_drop)

    return ablation_results


def single_dimension_auc(X_train_dicts, X_test_dicts, y_train, y_test, dim_names) -> dict:
    """
    For each dimension, train a model using only that dimension as feature.
    Returns {dim_name: auc_with_only_that_dim}
    """
    y_train_arr = np.array(y_train)
    y_test_arr = np.array(y_test)

    single_dim_results = {}
    for dim in dim_names:
        # Build matrices with just this single dimension
        X_train_single = np.array([[s.get(dim, 0.0)] for s in X_train_dicts])
        X_test_single = np.array([[s.get(dim, 0.0)] for s in X_test_dicts])

        model = train_xgboost(X_train_single, y_train_arr)
        pred = model.predict_proba(X_test_single)[:, 1]

        # Guard against degenerate case
        if len(np.unique(y_test_arr)) < 2:
            auc = 0.5
        else:
            auc = roc_auc_score(y_test_arr, pred)

        print(f"  Single dim [{dim}]: AUC={auc:.4f}")
        single_dim_results[dim] = float(auc)

    return single_dim_results


def analyze_dimensions(data_dir: str, output_dir: str) -> dict:
    """
    Main analysis:
    1. Train XGBoost on full features
    2. Get feature importance (gain-based from XGBoost)
    3. Compute SHAP values
    4. Ablation study (6 skillability dims only)
    5. Single-dimension AUC (train with each dim alone)

    Save to output_dir/analysis/dimension_importance.json.
    """
    data_dir = Path(data_dir)
    output_dir = Path(output_dir)

    print("Loading data...")
    with open(data_dir / "feature_names_classification.json") as f:
        feature_names = json.load(f)

    with open(data_dir / "X_train_classification.json") as f:
        X_train_dicts = json.load(f)

    with open(data_dir / "y_train_classification.json") as f:
        y_train = json.load(f)

    with open(data_dir / "X_test_classification.json") as f:
        X_test_dicts = json.load(f)

    with open(data_dir / "y_test_classification.json") as f:
        y_test = json.load(f)

    y_train_arr = np.array(y_train)
    y_test_arr = np.array(y_test)

    # Select full features
    X_train_filtered, full_feature_names = select_features(
        X_train_dicts, feature_names, FULL_FEATURE_PREFIXES
    )
    X_test_filtered, _ = select_features(
        X_test_dicts, feature_names, FULL_FEATURE_PREFIXES
    )

    X_train_mat = dicts_to_matrix(X_train_filtered, full_feature_names)
    X_test_mat = dicts_to_matrix(X_test_filtered, full_feature_names)

    print(f"Full feature set: {len(full_feature_names)} features")
    print(f"Train shape: {X_train_mat.shape}, Test shape: {X_test_mat.shape}")

    # --- 1. Train XGBoost full model ---
    print("\nTraining XGBoost full model...")
    model = train_xgboost(X_train_mat, y_train_arr)
    pred_full = model.predict_proba(X_test_mat)[:, 1]
    auc_full = roc_auc_score(y_test_arr, pred_full)
    print(f"Full model AUC: {auc_full:.4f}")

    # Set feature names on the booster for named importance lookup
    model.get_booster().feature_names = full_feature_names

    # --- 2. Feature importance (gain-based) ---
    print("\nComputing gain-based feature importance...")
    feature_importance = get_feature_importance_xgboost(model, full_feature_names)
    # Sort by importance descending
    feat_imp_sorted = dict(
        sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
    )
    print("Top 10 features by gain:")
    for feat, score in list(feat_imp_sorted.items())[:10]:
        print(f"  {feat}: {score:.4f}")

    # --- 3. SHAP values ---
    print("\nComputing SHAP values...")
    shap_importance = get_shap_values(model, X_test_mat, full_feature_names)
    shap_sorted = dict(
        sorted(shap_importance.items(), key=lambda x: x[1], reverse=True)
    )
    print("Top 10 features by SHAP:")
    for feat, score in list(shap_sorted.items())[:10]:
        print(f"  {feat}: {score:.4f}")

    # --- 4. Ablation study ---
    print("\nRunning ablation study on skillability dimensions...")
    # Only ablate dimensions that are in our full feature set
    dims_to_ablate = [d for d in SKILLABILITY_DIMS if d in full_feature_names]
    ablation_auc_drop = dimension_ablation_study(
        X_train_mat, y_train_arr, X_test_mat, y_test_arr,
        full_feature_names, dims_to_ablate, n_bootstrap=20
    )

    # --- 5. Single-dimension AUC ---
    print("\nComputing single-dimension AUC for each skillability dimension...")
    single_dim_auc = single_dimension_auc(
        X_train_dicts, X_test_dicts, y_train, y_test, SKILLABILITY_DIMS
    )

    # --- Determine top 3 dimensions by SHAP importance (among skillability dims) ---
    shap_skill_dims = {
        d: shap_importance.get(d, 0.0) for d in SKILLABILITY_DIMS
    }
    top_3_by_shap = sorted(shap_skill_dims.keys(), key=lambda x: shap_skill_dims[x], reverse=True)[:3]
    print(f"\nTop 3 dimensions (by SHAP): {top_3_by_shap}")

    # Top 3 by gain-based importance among skillability dims
    gain_skill_dims = {
        d: feature_importance.get(d, 0.0) for d in SKILLABILITY_DIMS
    }
    top_3_by_gain = sorted(gain_skill_dims.keys(), key=lambda x: gain_skill_dims[x], reverse=True)[:3]
    print(f"Top 3 dimensions (by gain): {top_3_by_gain}")

    # Top 3 by ablation AUC drop
    ablation_valid = {k: v for k, v in ablation_auc_drop.items() if v is not None}
    top_3_by_ablation = sorted(ablation_valid.keys(), key=lambda x: ablation_valid[x], reverse=True)[:3]
    print(f"Top 3 dimensions (by ablation drop): {top_3_by_ablation}")

    results = {
        "full_model_auc": float(auc_full),
        "feature_importance": feat_imp_sorted,
        "shap_importance": shap_sorted,
        "ablation_auc_drop": ablation_auc_drop,
        "single_dim_auc": single_dim_auc,
        "top_3_dimensions_by_shap": top_3_by_shap,
        "top_3_dimensions_by_gain": top_3_by_gain,
        "top_3_dimensions_by_ablation": top_3_by_ablation,
        # Consensus top 3 (union of all three methods, ranked by SHAP)
        "top_3_dimensions": top_3_by_shap,
        "skillability_dim_importance_shap": shap_skill_dims,
        "skillability_dim_importance_gain": gain_skill_dims,
        "full_feature_names": full_feature_names,
    }

    out_path = output_dir / "analysis" / "dimension_importance.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    def _convert(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, dict):
            return {k: _convert(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_convert(v) for v in obj]
        return obj

    with open(out_path, "w") as f:
        json.dump(_convert(results), f, indent=2)
    print(f"\nResults saved to: {out_path}")

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Analyze skillability dimension importance.")
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

    results = analyze_dimensions(args.data_dir, args.output_dir)

    print("\n=== Summary ===")
    print(f"Full model AUC: {results['full_model_auc']:.4f}")
    print(f"\nTop 3 dimensions (SHAP): {results['top_3_dimensions_by_shap']}")
    print(f"Top 3 dimensions (gain): {results['top_3_dimensions_by_gain']}")
    print(f"Top 3 dimensions (ablation): {results['top_3_dimensions_by_ablation']}")
    print("\nSHAP importance for skillability dims:")
    for dim, val in sorted(results["skillability_dim_importance_shap"].items(),
                           key=lambda x: x[1], reverse=True):
        print(f"  {dim}: {val:.4f}")
    print("\nAblation AUC drop:")
    for dim, drop in sorted(results["ablation_auc_drop"].items(),
                             key=lambda x: x[1] if x[1] else -1, reverse=True):
        print(f"  {dim}: {drop:.4f}")
