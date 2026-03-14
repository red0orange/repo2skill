"""Analysis and statistics module."""

from collections import Counter
from typing import Dict, List, Any


def analyze_capability_distribution(items: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
    """Analyze capability distribution by source.

    Args:
        items: List of extracted items

    Returns:
        Dictionary with capability counts by source
    """
    clawhub_caps = []
    github_caps = []

    for item in items:
        cap = item.get('primary_capability', 'unknown')
        if item.get('source') == 'clawhub':
            clawhub_caps.append(cap)
        else:
            github_caps.append(cap)

    return {
        'clawhub': dict(Counter(clawhub_caps)),
        'github': dict(Counter(github_caps))
    }


def analyze_granularity_distribution(items: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
    """Analyze granularity distribution by source."""
    clawhub_gran = []
    github_gran = []

    for item in items:
        gran = item.get('granularity', 'unknown')
        if item.get('source') == 'clawhub':
            clawhub_gran.append(gran)
        else:
            github_gran.append(gran)

    return {
        'clawhub': dict(Counter(clawhub_gran)),
        'github': dict(Counter(github_gran))
    }


def analyze_skillability_distribution(items: List[Dict[str, Any]]) -> Dict[str, List[float]]:
    """Analyze skillability score distribution by source."""
    clawhub_scores = []
    github_scores = []

    for item in items:
        score = item.get('skillability_score', 0)
        if item.get('source') == 'clawhub':
            clawhub_scores.append(score)
        else:
            github_scores.append(score)

    return {
        'clawhub': clawhub_scores,
        'github': github_scores
    }


def get_top_candidates(items: List[Dict[str, Any]], k: int = 20) -> List[Dict[str, Any]]:
    """Get top K candidates by opportunity score.

    Args:
        items: List of items with scores
        k: Number of top candidates to return

    Returns:
        Top K items sorted by opportunity_score
    """
    # Filter GitHub repos only
    github_items = [item for item in items if item.get('source') == 'github']

    # Sort by opportunity score
    sorted_items = sorted(github_items, key=lambda x: x.get('opportunity_score', 0), reverse=True)

    return sorted_items[:k]


def generate_summary_stats(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate summary statistics.

    Args:
        items: List of all items

    Returns:
        Dictionary with summary statistics
    """
    clawhub_items = [item for item in items if item.get('source') == 'clawhub']
    github_items = [item for item in items if item.get('source') == 'github']

    clawhub_skillability = [item.get('skillability_score', 0) for item in clawhub_items]
    github_skillability = [item.get('skillability_score', 0) for item in github_items]

    return {
        'total_items': len(items),
        'clawhub_count': len(clawhub_items),
        'github_count': len(github_items),
        'clawhub_avg_skillability': sum(clawhub_skillability) / len(clawhub_skillability) if clawhub_skillability else 0,
        'github_avg_skillability': sum(github_skillability) / len(github_skillability) if github_skillability else 0,
        'github_high_skillability_count': len([s for s in github_skillability if s >= 4])
    }
