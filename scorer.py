"""Scoring module for calculating opportunity scores."""

import math
from typing import Dict, Any


def calculate_skillability_core(data: Dict[str, Any], weights: Dict[str, float]) -> float:
    """Calculate core skillability score.

    Args:
        data: Extracted data with dimension scores
        weights: Weight dictionary for each dimension

    Returns:
        Skillability core score (0-1)
    """
    score = 0.0

    # Positive dimensions (normalized to 0-1)
    score += weights['task_clarity'] * (data.get('task_clarity', 3) - 1) / 4
    score += weights['interface_clarity'] * (data.get('interface_clarity', 3) - 1) / 4
    score += weights['composability'] * (data.get('composability', 3) - 1) / 4
    score += weights['automation_value'] * (data.get('automation_value', 3) - 1) / 4

    # Reverse-code negative dimensions, then apply their positive weights.
    score += weights['deployment_friction'] * (5 - data.get('deployment_friction', 3)) / 4
    score += weights['operational_risk'] * (5 - data.get('operational_risk', 3)) / 4

    return max(0.0, min(1.0, score))


def calculate_repo_quality(data: Dict[str, Any]) -> float:
    """Calculate repository quality score (GitHub only).

    Args:
        data: Repository data

    Returns:
        Quality score (0-1)
    """
    if data.get('source') != 'github':
        return 0.0

    score = 0.0

    # Stars (log scale, normalized)
    stars = data.get('stars', 0)
    if stars > 0:
        log_stars = math.log10(stars + 1)
        # Normalize: log10(100) = 2, log10(100000) = 5
        normalized_stars = min(1.0, (log_stars - 2) / 3)
        score += 0.5 * normalized_stars

    # Has license
    if data.get('license'):
        score += 0.3

    # Not archived
    if not data.get('archived', False):
        score += 0.2

    return score


def calculate_opportunity_score(data: Dict[str, Any],
                                skillability_weights: Dict[str, float],
                                opportunity_weights: Dict[str, float]) -> float:
    """Calculate final opportunity score.

    Args:
        data: Extracted data
        skillability_weights: Weights for skillability dimensions
        opportunity_weights: Weights for final score components

    Returns:
        Opportunity score (0-1)
    """
    skillability_core = calculate_skillability_core(data, skillability_weights)
    repo_quality = calculate_repo_quality(data)

    opportunity_score = (
        opportunity_weights['skillability_core'] * skillability_core +
        opportunity_weights['repo_quality'] * repo_quality
    )

    return max(0.0, min(1.0, opportunity_score))


def add_scores_to_data(items: list, skillability_weights: Dict[str, float],
                       opportunity_weights: Dict[str, float]) -> list:
    """Add calculated scores to all items.

    Args:
        items: List of extracted data items
        skillability_weights: Weights for skillability dimensions
        opportunity_weights: Weights for final score components

    Returns:
        Items with added score fields
    """
    for item in items:
        item['skillability_core'] = calculate_skillability_core(item, skillability_weights)
        item['repo_quality'] = calculate_repo_quality(item)
        item['opportunity_score'] = calculate_opportunity_score(
            item, skillability_weights, opportunity_weights
        )

    return items
