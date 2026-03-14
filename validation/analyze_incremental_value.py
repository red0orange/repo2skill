"""Quantify the incremental predictive value of skillability features."""
import json
import sys
import os
from pathlib import Path

import numpy as np

# Ensure project root is on path when run directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sklearn.metrics import roc_auc_score, average_precision_score

from validation.models import (
    select_features,
    dicts_to_matrix,
    train_xgboost,
    BASELINE_FEATURE_PREFIXES,
    FULL_FEATURE_PREFIXES,
)
from validation.config_validation import VALIDATION_OUTPUT_DIR, RANDOM_STATE


def bootstrap_auc_difference(y_true, pred_baseline, pred_full, n_bootstrap=1000, seed=42) -> dict:
    """
    Bootstrap confidence interval for AUC difference (full - baseline).
    Sample with replacement n_bootstrap times.
    Return: {mean_diff, ci_lower, ci_upper, p_value_one_sided}
    p_value = fraction of bootstrap samples where diff <= 0
    """
    rng = np.random.RandomState(seed)
    y_true = np.array(y_true)
    pred_baseline = np.array(pred_baseline)
    pred_full = np.array(pred_full)

    n = len(y_true)
    diffs = []

    for _ in range(n_bootstrap):
        indices = rng.choice(n, size=n, replace=True)
        y_bs = y_true[indices]
        # Skip if bootstrap sample has only one class
        if len(np.unique(y_bs)) < 2:
            continue
        auc_baseline_bs = roc_auc_score(y_bs, pred_baseline[indices])
        auc_full_bs = roc_auc_score(y_bs, pred_full[indices])
        diffs.append(auc_full_bs - auc_baseline_bs)

    diffs = np.array(diffs)
    mean_diff = float(np.mean(diffs))
    ci_lower = float(np.percentile(diffs, 2.5))
    ci_upper = float(np.percentile(diffs, 97.5))
    # p_value: fraction of bootstrap samples where diff <= 0 (one-sided test H0: diff <= 0)
    p_value = float(np.mean(diffs <= 0))

    return {
        "mean_diff": mean_diff,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "p_value_one_sided": p_value,
    }


def precision_at_k(y_true, y_scores, k=None) -> float:
    """Precision at K (K = number of positives in y_true if not specified)."""
    y_true = np.array(y_true)
    y_scores = np.array(y_scores)

    if k is None:
        k = int(np.sum(y_true))

    if k == 0:
        return 0.0

    top_k_indices = np.argsort(y_scores)[::-1][:k]
    return float(np.mean(y_true[top_k_indices]))


def analyze_incremental_value(data_dir: str, output_dir: str) -> dict:
    """
    Main analysis:
    1. Re-train XGBoost baseline and full models on train split
    2. Get per-item predictions on test split
    3. Bootstrap CI for AUC difference
    4. Precision@K comparison
    5. McNemar-like analysis: items correctly predicted by full but not baseline

    Return and save results to output_dir/analysis/incremental_value.json.
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

    y_train_arr = np.array(y_train)
    y_test_arr = np.array(y_test)

    print(f"Train size: {len(X_train_full)}, Test size: {len(X_test_full)}")
    print(f"Test positive rate: {y_test_arr.mean():.4f}")

    # --- Baseline model (has_license + archived) ---
    print("\nTraining baseline XGBoost model...")
    X_train_base_filtered, base_features = select_features(
        X_train_full, feature_names, BASELINE_FEATURE_PREFIXES
    )
    X_test_base_filtered, _ = select_features(
        X_test_full, feature_names, BASELINE_FEATURE_PREFIXES
    )
    X_train_base = dicts_to_matrix(X_train_base_filtered, base_features)
    X_test_base = dicts_to_matrix(X_test_base_filtered, base_features)

    model_baseline = train_xgboost(X_train_base, y_train_arr)
    pred_baseline = model_baseline.predict_proba(X_test_base)[:, 1]

    auc_baseline = roc_auc_score(y_test_arr, pred_baseline)
    pr_auc_baseline = average_precision_score(y_test_arr, pred_baseline)
    pak_baseline = precision_at_k(y_test_arr, pred_baseline)

    print(f"  Baseline AUC: {auc_baseline:.4f}, PR-AUC: {pr_auc_baseline:.4f}")
    print(f"  Baseline Precision@K: {pak_baseline:.4f}")

    # --- Full model (baseline + 6 skillability dims + capability + granularity) ---
    print("\nTraining full XGBoost model...")
    X_train_full_filtered, full_features = select_features(
        X_train_full, feature_names, FULL_FEATURE_PREFIXES
    )
    X_test_full_filtered, _ = select_features(
        X_test_full, feature_names, FULL_FEATURE_PREFIXES
    )
    X_train_mat = dicts_to_matrix(X_train_full_filtered, full_features)
    X_test_mat = dicts_to_matrix(X_test_full_filtered, full_features)

    model_full = train_xgboost(X_train_mat, y_train_arr)
    pred_full = model_full.predict_proba(X_test_mat)[:, 1]

    auc_full = roc_auc_score(y_test_arr, pred_full)
    pr_auc_full = average_precision_score(y_test_arr, pred_full)
    pak_full = precision_at_k(y_test_arr, pred_full)

    print(f"  Full AUC: {auc_full:.4f}, PR-AUC: {pr_auc_full:.4f}")
    print(f"  Full Precision@K: {pak_full:.4f}")

    # --- Bootstrap CI for AUC difference ---
    print("\nComputing bootstrap CI for AUC difference (1000 samples)...")
    bootstrap_results = bootstrap_auc_difference(
        y_test_arr, pred_baseline, pred_full, n_bootstrap=1000, seed=RANDOM_STATE
    )
    print(f"  AUC lift: {bootstrap_results['mean_diff']:.4f} "
          f"[{bootstrap_results['ci_lower']:.4f}, {bootstrap_results['ci_upper']:.4f}]")
    print(f"  p-value (one-sided, H0: diff<=0): {bootstrap_results['p_value_one_sided']:.4f}")

    # --- McNemar-like analysis ---
    # Items correctly ranked by full but not baseline
    # "Correctly ranked": positive items ranked above median threshold
    threshold_baseline = np.median(pred_baseline[y_test_arr == 1])
    threshold_full = np.median(pred_full[y_test_arr == 1])

    correct_baseline = (pred_baseline >= threshold_baseline) == y_test_arr.astype(bool)
    correct_full = (pred_full >= threshold_full) == y_test_arr.astype(bool)

    gained_by_full = int(np.sum(correct_full & ~correct_baseline))
    lost_by_full = int(np.sum(~correct_full & correct_baseline))

    # Actual lift in observed AUC
    auc_lift_observed = auc_full - auc_baseline
    pr_auc_lift = pr_auc_full - pr_auc_baseline

    # Interpret
    p_val = bootstrap_results["p_value_one_sided"]
    if p_val < 0.001:
        significance = "highly significant (p < 0.001)"
    elif p_val < 0.01:
        significance = "significant (p < 0.01)"
    elif p_val < 0.05:
        significance = "significant (p < 0.05)"
    else:
        significance = "not significant (p >= 0.05)"

    interpretation = (
        f"Skillability features provide a {auc_lift_observed:.4f} AUC lift over the baseline "
        f"(from {auc_baseline:.4f} to {auc_full:.4f}). "
        f"The 95% bootstrap CI is [{bootstrap_results['ci_lower']:.4f}, "
        f"{bootstrap_results['ci_upper']:.4f}], which is {significance}. "
        f"Precision@K improved from {pak_baseline:.4f} to {pak_full:.4f} "
        f"(+{pak_full - pak_baseline:.4f}). "
        f"PR-AUC lift: {pr_auc_lift:.4f} "
        f"(from {pr_auc_baseline:.4f} to {pr_auc_full:.4f}). "
        f"The full model gained correct predictions on {gained_by_full} items and lost {lost_by_full} "
        f"compared to the baseline, net improvement: {gained_by_full - lost_by_full} items."
    )
    print(f"\nInterpretation: {interpretation}")

    results = {
        "baseline_auc": float(auc_baseline),
        "full_auc": float(auc_full),
        "auc_lift": float(auc_lift_observed),
        "auc_lift_bootstrap_mean": float(bootstrap_results["mean_diff"]),
        "auc_lift_ci_95": [float(bootstrap_results["ci_lower"]), float(bootstrap_results["ci_upper"])],
        "auc_lift_p_value": float(bootstrap_results["p_value_one_sided"]),
        "baseline_pr_auc": float(pr_auc_baseline),
        "full_pr_auc": float(pr_auc_full),
        "pr_auc_lift": float(pr_auc_lift),
        "baseline_precision_at_k": float(pak_baseline),
        "full_precision_at_k": float(pak_full),
        "precision_at_k_lift": float(pak_full - pak_baseline),
        "mcnemar_items_gained_by_full": gained_by_full,
        "mcnemar_items_lost_by_full": lost_by_full,
        "mcnemar_net_improvement": gained_by_full - lost_by_full,
        "n_bootstrap": 1000,
        "baseline_features": base_features,
        "full_features": full_features,
        "n_test": int(len(y_test_arr)),
        "n_test_positive": int(np.sum(y_test_arr)),
        "interpretation": interpretation,
    }

    out_path = output_dir / "analysis" / "incremental_value.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {out_path}")

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Analyze incremental value of skillability features.")
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

    results = analyze_incremental_value(args.data_dir, args.output_dir)

    print("\n=== Summary ===")
    print(f"Baseline AUC:   {results['baseline_auc']:.4f}")
    print(f"Full AUC:       {results['full_auc']:.4f}")
    print(f"AUC Lift:       {results['auc_lift']:.4f}")
    print(f"95% CI:         [{results['auc_lift_ci_95'][0]:.4f}, {results['auc_lift_ci_95'][1]:.4f}]")
    print(f"p-value:        {results['auc_lift_p_value']:.4f}")
    print(f"PR-AUC Lift:    {results['pr_auc_lift']:.4f}")
