"""Tests for model training utilities in validation/models.py."""

import sys
import os
import numpy as np
import pytest

# Ensure project root is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from validation.models import (
    select_features,
    dicts_to_matrix,
    compute_metrics,
    cross_validate_model,
    train_logistic_regression,
    BASELINE_FEATURE_PREFIXES,
)


# ---------------------------------------------------------------------------
# Fixtures / shared test data
# ---------------------------------------------------------------------------

SAMPLE_FEATURE_NAMES = [
    "task_clarity",
    "interface_clarity",
    "composability",
    "skillability_core",
    "has_license",
    "archived",
    "lang_Python",
    "lang_JavaScript",
    "lang_TypeScript",
    "cap_code_devops",
    "gran_primitive_tool",
]

SAMPLE_X = [
    {
        "task_clarity": 4.0,
        "interface_clarity": 3.0,
        "composability": 5.0,
        "skillability_core": 0.7,
        "has_license": 1.0,
        "archived": 0.0,
        "lang_Python": 1,
        "lang_JavaScript": 0,
        "lang_TypeScript": 0,
        "cap_code_devops": 1,
        "gran_primitive_tool": 0,
    },
    {
        "task_clarity": 2.0,
        "interface_clarity": 2.0,
        "composability": 3.0,
        "skillability_core": 0.4,
        "has_license": 0.0,
        "archived": 1.0,
        "lang_Python": 0,
        "lang_JavaScript": 1,
        "lang_TypeScript": 0,
        "cap_code_devops": 0,
        "gran_primitive_tool": 1,
    },
    {
        "task_clarity": 5.0,
        "interface_clarity": 5.0,
        "composability": 4.0,
        "skillability_core": 0.9,
        "has_license": 1.0,
        "archived": 0.0,
        "lang_Python": 0,
        "lang_JavaScript": 0,
        "lang_TypeScript": 1,
        "cap_code_devops": 0,
        "gran_primitive_tool": 0,
    },
]


# ---------------------------------------------------------------------------
# test_select_features_baseline
# ---------------------------------------------------------------------------

def test_select_features_baseline():
    """Baseline prefix selection selects only has_license and archived (no lang_* due to data leakage)."""
    filtered_X, selected_names = select_features(
        SAMPLE_X, SAMPLE_FEATURE_NAMES, BASELINE_FEATURE_PREFIXES
    )

    # Must include has_license and archived
    assert "has_license" in selected_names
    assert "archived" in selected_names

    # Must NOT include lang_ features (they are confounded: all 0 for Clawhub, at least 1 for GitHub)
    assert "lang_Python" not in selected_names
    assert "lang_JavaScript" not in selected_names
    assert "lang_TypeScript" not in selected_names

    # Must NOT include skillability or capability or granularity features
    assert "task_clarity" not in selected_names
    assert "interface_clarity" not in selected_names
    assert "skillability_core" not in selected_names
    assert "cap_code_devops" not in selected_names
    assert "gran_primitive_tool" not in selected_names

    # Filtered X should have the same number of samples
    assert len(filtered_X) == len(SAMPLE_X)

    # Each filtered sample should only contain selected features
    for sample in filtered_X:
        for key in sample:
            assert key in selected_names, f"Unexpected key '{key}' in filtered sample"

    # Each filtered sample should contain all selected features
    for sample in filtered_X:
        for name in selected_names:
            assert name in sample, f"Missing key '{name}' in filtered sample"


def test_select_features_custom_prefixes():
    """Custom prefix selection returns correct subset."""
    filtered_X, selected_names = select_features(
        SAMPLE_X, SAMPLE_FEATURE_NAMES, ["cap_", "gran_"]
    )
    assert "cap_code_devops" in selected_names
    assert "gran_primitive_tool" in selected_names
    assert "has_license" not in selected_names
    assert "lang_Python" not in selected_names


def test_select_features_empty_prefixes():
    """Empty prefix list returns empty feature set."""
    filtered_X, selected_names = select_features(SAMPLE_X, SAMPLE_FEATURE_NAMES, [])
    assert selected_names == []
    assert len(filtered_X) == len(SAMPLE_X)
    for sample in filtered_X:
        assert sample == {}


# ---------------------------------------------------------------------------
# test_dicts_to_matrix_shape
# ---------------------------------------------------------------------------

def test_dicts_to_matrix_shape():
    """Correct matrix shape and column ordering."""
    matrix = dicts_to_matrix(SAMPLE_X, SAMPLE_FEATURE_NAMES)

    assert matrix.shape == (3, len(SAMPLE_FEATURE_NAMES))
    assert matrix.dtype == np.float64


def test_dicts_to_matrix_ordering():
    """Matrix columns follow feature_names order exactly."""
    matrix = dicts_to_matrix(SAMPLE_X, SAMPLE_FEATURE_NAMES)

    # Check first sample values against known data
    first = SAMPLE_X[0]
    for j, name in enumerate(SAMPLE_FEATURE_NAMES):
        expected = float(first[name])
        actual = matrix[0, j]
        assert abs(actual - expected) < 1e-9, (
            f"Column {j} ('{name}'): expected {expected}, got {actual}"
        )


def test_dicts_to_matrix_missing_keys():
    """Missing keys in a sample are filled with 0.0."""
    partial_X = [{"has_license": 1.0}]  # missing many keys
    feature_names = ["has_license", "archived", "lang_Python"]
    matrix = dicts_to_matrix(partial_X, feature_names)

    assert matrix.shape == (1, 3)
    assert matrix[0, 0] == 1.0   # has_license
    assert matrix[0, 1] == 0.0   # archived (missing)
    assert matrix[0, 2] == 0.0   # lang_Python (missing)


def test_dicts_to_matrix_single_feature():
    """Single-feature matrix has correct shape."""
    X = [{"has_license": 0.0}, {"has_license": 1.0}]
    matrix = dicts_to_matrix(X, ["has_license"])
    assert matrix.shape == (2, 1)
    assert matrix[0, 0] == 0.0
    assert matrix[1, 0] == 1.0


# ---------------------------------------------------------------------------
# test_compute_metrics_perfect
# ---------------------------------------------------------------------------

def test_compute_metrics_perfect():
    """Perfect predictions give AUC-ROC = 1.0 and PR-AUC = 1.0."""
    y_true = np.array([0, 0, 0, 1, 1, 1])
    # Perfect probabilities: positives get 1.0, negatives get 0.0
    y_pred = np.array([0.0, 0.0, 0.0, 1.0, 1.0, 1.0])

    metrics = compute_metrics(y_true, y_pred)

    assert abs(metrics["auc_roc"] - 1.0) < 1e-9, f"Expected AUC=1.0, got {metrics['auc_roc']}"
    assert abs(metrics["pr_auc"] - 1.0) < 1e-9, f"Expected PR-AUC=1.0, got {metrics['pr_auc']}"
    assert abs(metrics["precision_at_k"] - 1.0) < 1e-9, (
        f"Expected precision@k=1.0, got {metrics['precision_at_k']}"
    )


def test_compute_metrics_returns_dict_keys():
    """compute_metrics returns all required keys."""
    y_true = np.array([0, 1, 0, 1])
    y_pred = np.array([0.3, 0.7, 0.4, 0.6])

    metrics = compute_metrics(y_true, y_pred)

    assert "auc_roc" in metrics
    assert "pr_auc" in metrics
    assert "precision_at_k" in metrics


# ---------------------------------------------------------------------------
# test_compute_metrics_random
# ---------------------------------------------------------------------------

def test_compute_metrics_random():
    """Random predictions (shuffled labels) give AUC close to 0.5."""
    rng = np.random.RandomState(seed=0)
    n = 1000
    # 10% positive rate
    y_true = np.array([1] * 100 + [0] * 900)
    # Completely random scores (not correlated with y_true)
    y_pred = rng.uniform(0, 1, n)

    metrics = compute_metrics(y_true, y_pred)

    # With random predictions on 1000 samples, AUC should be very close to 0.5
    assert 0.35 <= metrics["auc_roc"] <= 0.65, (
        f"Expected AUC~0.5 for random predictions, got {metrics['auc_roc']}"
    )


def test_compute_metrics_values_are_floats():
    """All returned metric values are Python floats."""
    y_true = np.array([0, 0, 1, 1])
    y_pred = np.array([0.2, 0.3, 0.7, 0.8])
    metrics = compute_metrics(y_true, y_pred)

    for key, val in metrics.items():
        assert isinstance(val, float), f"Metric '{key}' is {type(val)}, expected float"


# ---------------------------------------------------------------------------
# test_cross_validate_returns_required_keys
# ---------------------------------------------------------------------------

def test_cross_validate_returns_required_keys():
    """cross_validate_model returns all required keys."""
    # Build a tiny dataset: 20 samples, 5 positives
    rng = np.random.RandomState(42)
    n = 40
    X = rng.randn(n, 3)
    y = np.array([1] * 5 + [0] * 35)

    cv_results = cross_validate_model(train_logistic_regression, X, y, cv_folds=3)

    required_keys = {"mean_auc", "std_auc", "mean_pr_auc", "std_pr_auc", "fold_results"}
    for key in required_keys:
        assert key in cv_results, f"Missing key '{key}' in CV results"

    # fold_results should have one entry per fold
    assert len(cv_results["fold_results"]) == 3

    # Each fold entry must have fold, auc_roc, pr_auc
    for fold in cv_results["fold_results"]:
        assert "fold" in fold
        assert "auc_roc" in fold
        assert "pr_auc" in fold


def test_cross_validate_auc_range():
    """CV AUC should be in [0, 1]."""
    rng = np.random.RandomState(0)
    n = 60
    X = rng.randn(n, 5)
    y = np.array([1] * 10 + [0] * 50)

    cv_results = cross_validate_model(train_logistic_regression, X, y, cv_folds=3)

    assert 0.0 <= cv_results["mean_auc"] <= 1.0
    assert cv_results["std_auc"] >= 0.0


def test_cross_validate_std_non_negative():
    """CV std should be non-negative."""
    rng = np.random.RandomState(1)
    n = 50
    X = rng.randn(n, 4)
    y = np.array([1] * 8 + [0] * 42)

    cv_results = cross_validate_model(train_logistic_regression, X, y, cv_folds=3)

    assert cv_results["std_auc"] >= 0.0
    assert cv_results["std_pr_auc"] >= 0.0
