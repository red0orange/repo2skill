"""Tests for skillability and opportunity scoring."""

from scorer import (
    add_scores_to_data,
    calculate_opportunity_score,
    calculate_repo_quality,
    calculate_skillability_core,
)


WEIGHTS = {
    "task_clarity": 0.25,
    "interface_clarity": 0.20,
    "composability": 0.20,
    "automation_value": 0.25,
    "deployment_friction": 0.05,
    "operational_risk": 0.05,
}

OPPORTUNITY_WEIGHTS = {
    "skillability_core": 0.6,
    "repo_quality": 0.4,
}


def test_low_friction_and_risk_increase_skillability_score():
    safe_item = {
        "task_clarity": 4,
        "interface_clarity": 4,
        "composability": 4,
        "automation_value": 4,
        "deployment_friction": 1,
        "operational_risk": 1,
    }
    risky_item = {
        **safe_item,
        "deployment_friction": 5,
        "operational_risk": 5,
    }

    assert calculate_skillability_core(safe_item, WEIGHTS) > calculate_skillability_core(risky_item, WEIGHTS)


def test_calculate_repo_quality_only_applies_to_github_items():
    github_item = {"source": "github", "stars": 1000, "license": "MIT", "archived": False}
    clawhub_item = {"source": "clawhub", "stars": 1000, "license": "MIT", "archived": False}

    assert calculate_repo_quality(github_item) > 0
    assert calculate_repo_quality(clawhub_item) == 0.0


def test_calculate_opportunity_score_is_clamped():
    item = {
        "source": "github",
        "task_clarity": 5,
        "interface_clarity": 5,
        "composability": 5,
        "automation_value": 5,
        "deployment_friction": 1,
        "operational_risk": 1,
        "stars": 1_000_000,
        "license": "MIT",
        "archived": False,
    }

    score = calculate_opportunity_score(item, WEIGHTS, OPPORTUNITY_WEIGHTS)
    assert 0.0 <= score <= 1.0


def test_add_scores_to_data_populates_all_score_fields():
    items = [
        {
            "source": "github",
            "task_clarity": 4,
            "interface_clarity": 3,
            "composability": 4,
            "automation_value": 5,
            "deployment_friction": 2,
            "operational_risk": 2,
            "stars": 500,
            "license": "MIT",
            "archived": False,
        }
    ]

    scored = add_scores_to_data(items, WEIGHTS, OPPORTUNITY_WEIGHTS)
    assert "skillability_core" in scored[0]
    assert "repo_quality" in scored[0]
    assert "opportunity_score" in scored[0]
