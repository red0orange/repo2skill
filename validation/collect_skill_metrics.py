"""Extract and structure Clawhub skill marketplace metrics."""

import json
import argparse
import logging
from pathlib import Path
from typing import Any
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_matches(matches_path: str) -> list:
    """Load matches from Task 2 output.

    Args:
        matches_path: Path to clawhub_github_matches.json

    Returns:
        List of match dictionaries
    """
    with open(matches_path) as f:
        data = json.load(f)
    return data.get('matches', [])


def load_extracted_clawhub(extracted_path: str) -> dict:
    """Load Clawhub items from extracted_data.jsonl, indexed by URL.

    Args:
        extracted_path: Path to extracted_data.jsonl

    Returns:
        Dictionary mapping URL -> extracted item
    """
    extracted_by_url = {}
    with open(extracted_path) as f:
        for line in f:
            item = json.loads(line)
            if item.get('source') == 'clawhub':
                extracted_by_url[item.get('url')] = item
    return extracted_by_url


def extract_skill_metrics(match: dict, extracted_item: dict | None) -> dict:
    """Combine match marketplace stats with skillability scores.

    Args:
        match: Match dictionary from clawhub_github_matches.json
        extracted_item: Extracted item from extracted_data.jsonl (or None)

    Returns:
        Dictionary with combined metrics
    """
    marketplace_stats = match.get('marketplace_stats', {})
    downloads = marketplace_stats.get('downloads', 0)

    metrics = {
        'skill_id': match.get('skill_id'),
        'skill_name': match.get('skill_name'),
        'stars': marketplace_stats.get('stars', 0),
        'downloads': downloads,
        'installs_all_time': marketplace_stats.get('installs_all_time', 0),
        'versions': marketplace_stats.get('versions', 0),
        'has_license': marketplace_stats.get('license') is not None,
        'is_popular': marketplace_stats.get('installs_all_time', 0) > 0,
        'log_downloads': float(np.log1p(downloads)),
    }

    # Add skillability scores from extracted data
    if extracted_item:
        metrics.update({
            'task_clarity': extracted_item.get('task_clarity'),
            'interface_clarity': extracted_item.get('interface_clarity'),
            'composability': extracted_item.get('composability'),
            'automation_value': extracted_item.get('automation_value'),
            'deployment_friction': extracted_item.get('deployment_friction'),
            'operational_risk': extracted_item.get('operational_risk'),
            'skillability_core': extracted_item.get('skillability_core'),
            'opportunity_score': extracted_item.get('opportunity_score'),
            'primary_capability': extracted_item.get('primary_capability'),
            'granularity': extracted_item.get('granularity'),
        })
    else:
        # Provide None values if extracted data not available
        metrics.update({
            'task_clarity': None,
            'interface_clarity': None,
            'composability': None,
            'automation_value': None,
            'deployment_friction': None,
            'operational_risk': None,
            'skillability_core': None,
            'opportunity_score': None,
            'primary_capability': None,
            'granularity': None,
        })

    return metrics


def collect_metrics(matches_path: str, extracted_path: str, output_path: str) -> dict:
    """Main function: combine match data with extracted skillability scores.

    Args:
        matches_path: Path to clawhub_github_matches.json
        extracted_path: Path to extracted_data.jsonl
        output_path: Path to save skill_metrics.json

    Returns:
        Dictionary with metrics and stats
    """
    logger.info(f"Loading matches from {matches_path}")
    matches = load_matches(matches_path)
    logger.info(f"Loaded {len(matches)} matches")

    logger.info(f"Loading extracted data from {extracted_path}")
    extracted_by_url = load_extracted_clawhub(extracted_path)
    logger.info(f"Loaded {len(extracted_by_url)} Clawhub items with skillability scores")

    # Extract metrics for each match
    metrics_list = []
    missing_extracted = 0

    for match in matches:
        url = match.get('extracted_url')
        extracted_item = extracted_by_url.get(url)

        if not extracted_item:
            missing_extracted += 1
            logger.warning(f"No extracted data for {url}")

        metric = extract_skill_metrics(match, extracted_item)
        metrics_list.append(metric)

    if missing_extracted > 0:
        logger.warning(f"Missing extracted data for {missing_extracted} matches")

    # Compute statistics
    downloads_list = [m['downloads'] for m in metrics_list if m['downloads'] is not None]
    installs_list = [m['installs_all_time'] for m in metrics_list if m['installs_all_time'] is not None]
    skillability_list = [m['skillability_core'] for m in metrics_list if m['skillability_core'] is not None]

    stats = {
        'total': len(metrics_list),
        'with_downloads': sum(1 for d in downloads_list if d > 0),
        'with_installs': sum(1 for i in installs_list if i > 0),
        'with_stars': sum(1 for m in metrics_list if m['stars'] > 0),
        'median_downloads': float(np.median(downloads_list)) if downloads_list else 0,
        'median_installs': float(np.median(installs_list)) if installs_list else 0,
        'avg_skillability_core': float(np.mean(skillability_list)) if skillability_list else 0,
    }

    result = {
        'metrics': metrics_list,
        'stats': stats,
    }

    # Save output
    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)

    logger.info(f"Saved metrics to {output_path}")
    logger.info(f"Stats: {stats}")

    return result


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Extract Clawhub skill marketplace metrics and skillability scores'
    )
    parser.add_argument(
        '--matches',
        default='output/validation/clawhub_github_matches.json',
        help='Path to clawhub_github_matches.json'
    )
    parser.add_argument(
        '--extracted',
        help='Path to extracted_data.jsonl (auto-detected from config if not provided)'
    )
    parser.add_argument(
        '--output',
        default='output/validation/skill_metrics.json',
        help='Path to save skill_metrics.json'
    )

    args = parser.parse_args()

    # If extracted path not provided, try to get from config
    extracted_path = args.extracted
    if not extracted_path:
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from validation.config_validation import EXTRACTED_DATA_PATH
            extracted_path = EXTRACTED_DATA_PATH
        except ImportError:
            raise ValueError("Could not find extracted_data.jsonl. Provide --extracted flag.")

    collect_metrics(args.matches, extracted_path, args.output)


if __name__ == '__main__':
    main()
