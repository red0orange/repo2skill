"""Robustness analysis: performance across subgroups and sensitivity tests."""
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
    FULL_FEATURE_PREFIXES,
)
from validation.config_validation import VALIDATION_OUTPUT_DIR, RANDOM_STATE

# Capability column names (one-hot encoded)
CAPABILITY_COLUMNS = [
    "cap_code_devops",
    "cap_data_retrieval_search",
    "cap_document_processing",
    "cap_web_automation",
    "cap_communication_collaboration",
    "cap_knowledge_workflow_research",
    "cap_business_productivity_ops",
    "cap_multimedia_content",
    "cap_system_infrastructure",
    "cap_external_service_connector",
]


def subgroup_analysis_by_capability(X_test, y_test, model, feature_names) -> dict:
    """
    For each primary_capability category, compute AUC on that subgroup.
    Items can belong to multiple categories (one-hot encoded).
    Return: {capability: {"auc": float, "n_positive": int, "n_total": int}}
    """
    y_test_arr = np.array(y_test)

    # Get predictions for all test items
    pred_all = model.predict_proba(X_test)[:, 1]

    results = {}

    # For each capability column, find items in that subgroup
    for cap_col in CAPABILITY_COLUMNS:
        if cap_col not in feature_names:
            continue
        col_idx = feature_names.index(cap_col)
        mask = X_test[:, col_idx] == 1

        n_total = int(mask.sum())
        if n_total == 0:
            results[cap_col] = {"auc": None, "n_positive": 0, "n_total": 0, "pr_auc": None}
            continue

        y_sub = y_test_arr[mask]
        pred_sub = pred_all[mask]
        n_positive = int(y_sub.sum())

        if n_positive == 0 or n_positive == n_total:
            # Cannot compute AUC with only one class
            results[cap_col] = {
                "auc": None,
                "pr_auc": None,
                "n_positive": n_positive,
                "n_total": n_total,
                "note": "only one class in subgroup",
            }
            continue

        auc = float(roc_auc_score(y_sub, pred_sub))
        pr_auc = float(average_precision_score(y_sub, pred_sub))
        results[cap_col] = {
            "auc": auc,
            "pr_auc": pr_auc,
            "n_positive": n_positive,
            "n_total": n_total,
            "positive_rate": float(n_positive / n_total),
        }

    # Also compute "no capability assigned" subgroup
    # Items where none of the cap_ columns are set to 1
    cap_indices = [feature_names.index(c) for c in CAPABILITY_COLUMNS if c in feature_names]
    if cap_indices:
        cap_matrix = X_test[:, cap_indices]
        no_cap_mask = (cap_matrix.sum(axis=1) == 0)
        n_total_no_cap = int(no_cap_mask.sum())
        if n_total_no_cap > 0:
            y_no_cap = y_test_arr[no_cap_mask]
            pred_no_cap = pred_all[no_cap_mask]
            n_pos_no_cap = int(y_no_cap.sum())
            if n_pos_no_cap > 0 and n_pos_no_cap < n_total_no_cap:
                auc_no_cap = float(roc_auc_score(y_no_cap, pred_no_cap))
                pr_auc_no_cap = float(average_precision_score(y_no_cap, pred_no_cap))
            else:
                auc_no_cap = None
                pr_auc_no_cap = None
            results["no_capability_assigned"] = {
                "auc": auc_no_cap,
                "pr_auc": pr_auc_no_cap,
                "n_positive": n_pos_no_cap,
                "n_total": n_total_no_cap,
                "positive_rate": float(n_pos_no_cap / n_total_no_cap) if n_total_no_cap > 0 else 0.0,
            }

    return results


def sensitivity_analysis_class_ratio(X_train, y_train, X_test, y_test,
                                      feature_names, ratios=None) -> dict:
    """
    Vary the scale_pos_weight (class imbalance ratio) in XGBoost.
    Default is neg_count/pos_count. Here we multiply by each ratio.
    Report AUC and PR-AUC for each ratio.
    """
    if ratios is None:
        ratios = [0.5, 1.0, 2.0]

    y_train_arr = np.array(y_train)
    y_test_arr = np.array(y_test)

    pos_count = int(np.sum(y_train_arr))
    neg_count = int(len(y_train_arr) - pos_count)
    base_scale_pos_weight = neg_count / pos_count if pos_count > 0 else 1.0

    print(f"  Base scale_pos_weight: {base_scale_pos_weight:.2f} "
          f"(neg={neg_count}, pos={pos_count})")

    from xgboost import XGBClassifier

    results = {}
    for ratio in ratios:
        spw = base_scale_pos_weight * ratio
        model = XGBClassifier(
            scale_pos_weight=spw,
            n_estimators=100,
            random_state=RANDOM_STATE,
            eval_metric="logloss",
            use_label_encoder=False,
            verbosity=0,
        )
        model.fit(X_train, y_train_arr)
        pred = model.predict_proba(X_test)[:, 1]

        auc = float(roc_auc_score(y_test_arr, pred))
        pr_auc = float(average_precision_score(y_test_arr, pred))

        results[str(ratio)] = {
            "scale_pos_weight": float(spw),
            "ratio_multiplier": ratio,
            "auc": auc,
            "pr_auc": pr_auc,
        }
        print(f"  Ratio {ratio}x (spw={spw:.2f}): AUC={auc:.4f}, PR-AUC={pr_auc:.4f}")

    return results


def cross_dataset_stability(X_train_dicts, X_test_dicts, y_train, y_test,
                             feature_names) -> dict:
    """
    Assess stability by varying train/test split via 5 random seeds.
    Report AUC variance across seeds.
    """
    from sklearn.model_selection import StratifiedShuffleSplit

    X_all_dicts = X_train_dicts + X_test_dicts
    y_all = np.array(y_train + y_test)

    # Select features from combined dataset
    from validation.models import select_features, dicts_to_matrix
    X_all_filtered, full_feats = select_features(
        X_all_dicts, feature_names, FULL_FEATURE_PREFIXES
    )
    X_all_mat = dicts_to_matrix(X_all_filtered, full_feats)

    aucs = []
    pr_aucs = []
    seeds = [0, 1, 2, 3, 4]

    for seed in seeds:
        sss = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=seed)
        for train_idx, test_idx in sss.split(X_all_mat, y_all):
            X_tr = X_all_mat[train_idx]
            y_tr = y_all[train_idx]
            X_te = X_all_mat[test_idx]
            y_te = y_all[test_idx]

            model = train_xgboost(X_tr, y_tr)
            pred = model.predict_proba(X_te)[:, 1]

            auc = float(roc_auc_score(y_te, pred))
            pr_auc = float(average_precision_score(y_te, pred))
            aucs.append(auc)
            pr_aucs.append(pr_auc)
            print(f"  Seed {seed}: AUC={auc:.4f}, PR-AUC={pr_auc:.4f}")

    return {
        "seeds": seeds,
        "aucs": aucs,
        "pr_aucs": pr_aucs,
        "auc_mean": float(np.mean(aucs)),
        "auc_std": float(np.std(aucs)),
        "pr_auc_mean": float(np.mean(pr_aucs)),
        "pr_auc_std": float(np.std(pr_aucs)),
    }


def robustness_analysis(data_dir: str, output_dir: str) -> dict:
    """
    Main robustness analysis:
    1. Subgroup analysis by capability category
    2. Sensitivity analysis varying class weight ratio
    3. Cross-split stability (5 random seeds)

    Save to output_dir/analysis/robustness.json.
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

    # --- 1. Train the primary model ---
    print("\nTraining primary XGBoost model...")
    model = train_xgboost(X_train_mat, y_train_arr)
    pred_full = model.predict_proba(X_test_mat)[:, 1]
    overall_auc = float(roc_auc_score(y_test_arr, pred_full))
    overall_pr_auc = float(average_precision_score(y_test_arr, pred_full))
    print(f"Overall AUC: {overall_auc:.4f}, PR-AUC: {overall_pr_auc:.4f}")

    # --- 2. Subgroup analysis by capability ---
    print("\nRunning subgroup analysis by capability category...")
    subgroup_results = subgroup_analysis_by_capability(
        X_test_mat, y_test, model, full_feature_names
    )
    for cap, metrics in subgroup_results.items():
        if metrics.get("auc") is not None:
            print(f"  {cap}: AUC={metrics['auc']:.4f}, "
                  f"n={metrics['n_total']}, n_pos={metrics['n_positive']}")
        else:
            note = metrics.get("note", "AUC undefined")
            print(f"  {cap}: {note}, n={metrics['n_total']}")

    # --- 3. Sensitivity analysis: class weight ratio ---
    print("\nRunning sensitivity analysis (class weight ratios)...")
    sensitivity_results = sensitivity_analysis_class_ratio(
        X_train_mat, y_train_arr, X_test_mat, y_test_arr,
        full_feature_names, ratios=[0.5, 1.0, 2.0]
    )

    # --- 4. Cross-split stability ---
    print("\nRunning cross-split stability analysis (5 random seeds)...")
    stability_results = cross_dataset_stability(
        X_train_dicts, X_test_dicts, y_train, y_test, feature_names
    )

    # --- Summarize subgroup AUC differences ---
    valid_subgroup_aucs = {
        cap: metrics["auc"]
        for cap, metrics in subgroup_results.items()
        if metrics.get("auc") is not None
    }
    if valid_subgroup_aucs:
        max_cap = max(valid_subgroup_aucs, key=valid_subgroup_aucs.get)
        min_cap = min(valid_subgroup_aucs, key=valid_subgroup_aucs.get)
        auc_range = valid_subgroup_aucs[max_cap] - valid_subgroup_aucs[min_cap]
    else:
        max_cap = min_cap = None
        auc_range = 0.0

    # AUC spread in sensitivity analysis
    sensitivity_aucs = [v["auc"] for v in sensitivity_results.values()]
    sensitivity_auc_range = max(sensitivity_aucs) - min(sensitivity_aucs)

    overall_summary = (
        f"Robustness analysis on {len(y_test_arr)} test items "
        f"(positive rate: {y_test_arr.mean():.4f}). "
        f"Overall AUC: {overall_auc:.4f}, PR-AUC: {overall_pr_auc:.4f}. "
        f"Subgroup AUC ranges from {valid_subgroup_aucs.get(min_cap, 'N/A')} "
        f"({min_cap}) to {valid_subgroup_aucs.get(max_cap, 'N/A')} ({max_cap}), "
        f"a range of {auc_range:.4f}. "
        f"Sensitivity to class weight ratio: AUC range of {sensitivity_auc_range:.4f} "
        f"across multipliers [0.5, 1.0, 2.0]. "
        f"Cross-split stability: AUC = {stability_results['auc_mean']:.4f} "
        f"+/- {stability_results['auc_std']:.4f} across 5 random seeds."
    )
    print(f"\nSummary: {overall_summary}")

    results = {
        "overall_auc": overall_auc,
        "overall_pr_auc": overall_pr_auc,
        "n_test": int(len(y_test_arr)),
        "n_test_positive": int(y_test_arr.sum()),
        "test_positive_rate": float(y_test_arr.mean()),
        "subgroup_by_capability": subgroup_results,
        "sensitivity_class_ratio": sensitivity_results,
        "cross_split_stability": stability_results,
        "subgroup_auc_max": {
            "capability": max_cap,
            "auc": valid_subgroup_aucs.get(max_cap),
        },
        "subgroup_auc_min": {
            "capability": min_cap,
            "auc": valid_subgroup_aucs.get(min_cap),
        },
        "subgroup_auc_range": float(auc_range),
        "sensitivity_auc_range": float(sensitivity_auc_range),
        "overall_summary": overall_summary,
    }

    out_path = output_dir / "analysis" / "robustness.json"
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

    parser = argparse.ArgumentParser(description="Run robustness analysis.")
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

    results = robustness_analysis(args.data_dir, args.output_dir)

    print("\n=== Summary ===")
    print(results["overall_summary"])
    print("\nSubgroup AUCs (by capability):")
    for cap, metrics in sorted(results["subgroup_by_capability"].items()):
        auc_val = metrics.get("auc")
        if auc_val is not None:
            print(f"  {cap}: AUC={auc_val:.4f}, n={metrics['n_total']}, "
                  f"n_pos={metrics['n_positive']}")
        else:
            print(f"  {cap}: AUC=N/A, n={metrics['n_total']}")
