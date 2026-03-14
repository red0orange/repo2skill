"""Tests for feature engineering functions."""

import math
import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from validation.features import (
    parse_bool,
    log_transform,
    encode_capability,
    encode_granularity,
    encode_language,
    extract_features_for_classification,
    SKILLABILITY_DIMS,
    VALID_CAPABILITIES,
    VALID_GRANULARITIES,
)
from validation.preprocess_data import train_test_split_stratified


# ---------------------------------------------------------------------------
# parse_bool
# ---------------------------------------------------------------------------

def test_parse_bool():
    assert parse_bool("True") == 1
    assert parse_bool("False") == 0
    assert parse_bool("true") == 1
    assert parse_bool("false") == 0
    assert parse_bool(True) == 1
    assert parse_bool(False) == 0
    assert parse_bool(1) == 1
    assert parse_bool(0) == 0
    assert parse_bool("") == 0
    assert parse_bool(None) == 0
    assert parse_bool("1") == 0  # non-"True" strings that don't match "true" -> 0
    # "TRUE" also matches
    assert parse_bool("TRUE") == 1


# ---------------------------------------------------------------------------
# log_transform
# ---------------------------------------------------------------------------

def test_log_transform():
    # log(0 + 1) = 0
    assert log_transform(0) == pytest_approx(math.log(1))
    # log(1 + 1) = log(2)
    assert abs(log_transform(1) - math.log(2)) < 1e-9
    # log(99 + 1) = log(100)
    assert abs(log_transform(99) - math.log(100)) < 1e-9
    # None -> 0
    assert log_transform(None) == 0.0
    # NaN -> 0
    assert log_transform(float("nan")) == 0.0
    # String numeric
    assert abs(log_transform("4") - math.log(5)) < 1e-9


def pytest_approx(val):
    """Simple helper - just return val (used for readability, compare with abs diff)."""
    return val


# ---------------------------------------------------------------------------
# encode_capability
# ---------------------------------------------------------------------------

def test_encode_capability_known():
    result = encode_capability("code_devops")
    assert result["cap_code_devops"] == 1
    # All others must be 0
    for cap in VALID_CAPABILITIES:
        if cap != "code_devops":
            assert result[f"cap_{cap}"] == 0, f"cap_{cap} should be 0"
    # Total number of keys equals total capabilities
    assert len(result) == len(VALID_CAPABILITIES)


def test_encode_capability_unknown():
    result = encode_capability("unknown_capability")
    for cap in VALID_CAPABILITIES:
        assert result[f"cap_{cap}"] == 0
    result_none = encode_capability(None)
    for cap in VALID_CAPABILITIES:
        assert result_none[f"cap_{cap}"] == 0


# ---------------------------------------------------------------------------
# encode_granularity
# ---------------------------------------------------------------------------

def test_encode_granularity_known():
    result = encode_granularity("workflow_skill")
    assert result["gran_workflow_skill"] == 1
    for gran in VALID_GRANULARITIES:
        if gran != "workflow_skill":
            assert result[f"gran_{gran}"] == 0, f"gran_{gran} should be 0"
    assert len(result) == len(VALID_GRANULARITIES)

    result_pp = encode_granularity("primitive_tool")
    assert result_pp["gran_primitive_tool"] == 1
    assert result_pp["gran_workflow_skill"] == 0


# ---------------------------------------------------------------------------
# extract_features_for_classification
# ---------------------------------------------------------------------------

def test_extract_features_classification_has_all_skillability_dims():
    sample_row = {
        "label": 1,
        "task_clarity": 4,
        "interface_clarity": 5,
        "composability": 3,
        "automation_value": 4,
        "deployment_friction": 2,
        "operational_risk": 2,
        "skillability_core": 0.55,
        "has_license": "False",
        "language": "Python",
        "archived": "False",
        "primary_capability": "knowledge_workflow_research",
        "granularity": "workflow_skill",
    }
    top_languages = ["Python", "JavaScript", "TypeScript"]
    features = extract_features_for_classification(sample_row, top_languages)

    for dim in SKILLABILITY_DIMS:
        assert dim in features, f"Missing skillability dim: {dim}"
        assert features[dim] == float(sample_row[dim])

    assert "skillability_core" in features
    assert abs(features["skillability_core"] - 0.55) < 1e-9


def test_extract_features_no_github_stars():
    """github_stars must NOT appear as a classification feature (it is confounded)."""
    sample_row = {
        "label": 0,
        "task_clarity": 5,
        "interface_clarity": 5,
        "composability": 4,
        "automation_value": 5,
        "deployment_friction": 3,
        "operational_risk": 3,
        "skillability_core": 0.8,
        "github_stars": 1562,
        "has_license": "True",
        "language": "JavaScript",
        "archived": "False",
        "primary_capability": "web_automation",
        "granularity": "service_wrapper",
    }
    top_languages = ["Python", "JavaScript", "TypeScript"]
    features = extract_features_for_classification(sample_row, top_languages)

    assert "github_stars" not in features, "github_stars must not be in classification features"


# ---------------------------------------------------------------------------
# train_test_split_stratified
# ---------------------------------------------------------------------------

def test_train_test_split_stratified_balance():
    # Build a synthetic dataset: 80 class-0, 20 class-1
    X = list(range(100))
    y = [0] * 80 + [1] * 20

    X_train, X_test, y_train, y_test = train_test_split_stratified(X, y, test_size=0.2, random_state=42)

    # Total sizes
    assert len(X_train) + len(X_test) == 100
    assert len(y_train) + len(y_test) == 100

    # Class balance check — each split should have roughly the same ratio
    train_pos = sum(1 for lbl in y_train if lbl == 1)
    test_pos = sum(1 for lbl in y_test if lbl == 1)

    # In train: expect ~16 positives (80% of 20)
    # In test:  expect ~4  positives (20% of 20)
    assert 12 <= train_pos <= 20, f"Train positives {train_pos} out of expected ~16"
    assert 1 <= test_pos <= 8, f"Test positives {test_pos} out of expected ~4"

    # Verify no data leakage — train + test indices are disjoint
    # (X values are unique integers in this test)
    assert set(X_train).isdisjoint(set(X_test)), "Train and test sets must be disjoint"
