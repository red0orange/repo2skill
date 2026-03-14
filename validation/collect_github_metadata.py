"""Extract GitHub repository metadata from existing extracted dataset.

This module extracts GitHub repository metadata from the extracted_data.jsonl file.
No GitHub API calls are needed since all required data is already present.
"""

import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import Counter

from config_validation import EXTRACTED_DATA_PATH, GITHUB_METADATA_PATH

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def extract_github_metadata(item: dict) -> Optional[dict]:
    """
    Extract and normalize GitHub metadata fields from an extracted item.

    Args:
        item: A data item from extracted_data.jsonl

    Returns:
        Dict with normalized GitHub metadata fields, or None if not a GitHub item.
        Returns dict with:
        - repo_name: str (owner/repo format)
        - github_url: str
        - stars: int
        - language: str or None
        - archived: bool
        - has_license: bool
        - license_name: str or None
        - task_clarity: int (1-5)
        - interface_clarity: int (1-5)
        - composability: int (1-5)
        - automation_value: int (1-5)
        - deployment_friction: int (1-5)
        - operational_risk: int (1-5)
        - skillability_core: float (0-1)
        - opportunity_score: float (0-1)
        - primary_capability: str or None
        - granularity: str or None
    """
    # Skip if not a GitHub item
    if item.get("source") != "github":
        return None

    try:
        # Extract basic repo information
        repo_name = item.get("name", "")
        github_url = item.get("url", "")

        if not repo_name or not github_url:
            logger.warning(f"Skipping item with missing name or url: {item.get('id')}")
            return None

        # Extract repository metadata
        stars = item.get("stars")
        if stars is not None:
            stars = int(stars) if stars >= 0 else None
        else:
            stars = None

        language = item.get("language")
        if language == "":  # Treat empty string as None
            language = None

        archived = bool(item.get("archived", False))

        license_name = item.get("license")
        if license_name == "":  # Treat empty string as None
            license_name = None
        has_license = license_name is not None

        # Extract skillability dimensions
        metadata = {
            "repo_name": repo_name,
            "github_url": github_url,
            "stars": stars,
            "language": language,
            "archived": archived,
            "has_license": has_license,
            "license_name": license_name,
            "task_clarity": int(item.get("task_clarity", 0)),
            "interface_clarity": int(item.get("interface_clarity", 0)),
            "composability": int(item.get("composability", 0)),
            "automation_value": int(item.get("automation_value", 0)),
            "deployment_friction": int(item.get("deployment_friction", 0)),
            "operational_risk": int(item.get("operational_risk", 0)),
            "skillability_core": float(item.get("skillability_core", 0.0)),
            "opportunity_score": float(item.get("opportunity_score", 0.0)),
            "primary_capability": item.get("primary_capability"),
            "granularity": item.get("granularity"),
        }

        return metadata

    except Exception as e:
        logger.error(f"Error extracting metadata from item {item.get('id')}: {e}")
        return None


def collect_metadata(extracted_path: str, output_path: str) -> Dict[str, Any]:
    """
    Load all GitHub items from extracted_data.jsonl, extract metadata, save to JSON.

    Args:
        extracted_path: Path to extracted_data.jsonl
        output_path: Path where to save the output JSON file

    Returns:
        Dict with keys:
        - metadata: List of extracted GitHub metadata dicts
        - stats: Dict with statistics about the collection
    """
    metadata_list = []
    github_items = 0
    skipped_items = 0

    # Statistics counters
    has_stars_count = 0
    has_language_count = 0
    has_license_count = 0
    archived_count = 0
    languages = Counter()
    licenses = Counter()

    logger.info(f"Reading from {extracted_path}")

    try:
        with open(extracted_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue

                try:
                    item = json.loads(line)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON at line {line_num}: {e}")
                    continue

                # Process GitHub items
                if item.get("source") == "github":
                    github_items += 1
                    extracted = extract_github_metadata(item)

                    if extracted:
                        metadata_list.append(extracted)

                        # Update statistics
                        if extracted["stars"] is not None:
                            has_stars_count += 1
                        if extracted["language"] is not None:
                            has_language_count += 1
                            languages[extracted["language"]] += 1
                        if extracted["has_license"]:
                            has_license_count += 1
                            if extracted["license_name"]:
                                licenses[extracted["license_name"]] += 1
                        if extracted["archived"]:
                            archived_count += 1
                    else:
                        skipped_items += 1

                # Progress logging every 5000 lines
                if line_num % 5000 == 0:
                    logger.info(f"Processed {line_num} lines, extracted {len(metadata_list)} GitHub items")

    except FileNotFoundError:
        logger.error(f"File not found: {extracted_path}")
        raise
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        raise

    # Prepare output directory
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Prepare statistics
    stats = {
        "total": len(metadata_list),
        "total_github_items_in_source": github_items,
        "skipped": skipped_items,
        "has_stars": has_stars_count,
        "has_language": has_language_count,
        "has_license": has_license_count,
        "archived": archived_count,
        "top_languages": dict(languages.most_common(20)),
        "top_licenses": dict(licenses.most_common(20)),
    }

    # Prepare output dictionary
    output_data = {
        "metadata": metadata_list,
        "stats": stats,
    }

    # Save to JSON file
    logger.info(f"Writing output to {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    logger.info(f"Successfully saved metadata for {len(metadata_list)} GitHub repositories")

    return output_data


def print_stats(stats: Dict[str, Any]) -> None:
    """Print statistics in a human-readable format."""
    print("\n" + "="*70)
    print("GitHub Metadata Collection Statistics")
    print("="*70)
    print(f"\nTotal GitHub repositories extracted: {stats['total']}")
    print(f"Total GitHub items in source: {stats['total_github_items_in_source']}")
    print(f"Skipped items: {stats['skipped']}")

    print(f"\nMetadata coverage:")
    print(f"  - Repositories with stars: {stats['has_stars']} ({100*stats['has_stars']/stats['total']:.1f}%)")
    print(f"  - Repositories with language: {stats['has_language']} ({100*stats['has_language']/stats['total']:.1f}%)")
    print(f"  - Repositories with license: {stats['has_license']} ({100*stats['has_license']/stats['total']:.1f}%)")
    print(f"  - Archived repositories: {stats['archived']} ({100*stats['archived']/stats['total']:.1f}%)")

    if stats['top_languages']:
        print(f"\nTop 10 programming languages:")
        for lang, count in list(stats['top_languages'].items())[:10]:
            pct = 100 * count / stats['total']
            print(f"  - {lang}: {count} ({pct:.1f}%)")

    if stats['top_licenses']:
        print(f"\nTop 10 licenses:")
        for lic, count in list(stats['top_licenses'].items())[:10]:
            pct = 100 * count / stats['total']
            print(f"  - {lic}: {count} ({pct:.1f}%)")

    print("\n" + "="*70 + "\n")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Extract GitHub metadata from existing dataset"
    )
    parser.add_argument(
        "--extracted",
        type=str,
        default=EXTRACTED_DATA_PATH,
        help=f"Path to extracted_data.jsonl (default: {EXTRACTED_DATA_PATH})"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=GITHUB_METADATA_PATH,
        help=f"Path for output JSON file (default: {GITHUB_METADATA_PATH})"
    )

    args = parser.parse_args()

    logger.info(f"Starting GitHub metadata collection")
    logger.info(f"Input: {args.extracted}")
    logger.info(f"Output: {args.output}")

    result = collect_metadata(args.extracted, args.output)
    print_stats(result["stats"])

    logger.info("GitHub metadata collection completed successfully")


if __name__ == "__main__":
    main()
