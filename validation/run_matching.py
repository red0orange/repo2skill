"""Batch match extracted Clawhub skills to full Clawhub dataset for marketplace stats."""

import json
import sys
import warnings
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from validation.match_clawhub_github import build_clawhub_index, match_skill_to_clawhub_stats
from validation.config_validation import (
    CLAWHUB_COMPLETE_PATH,
    EXTRACTED_DATA_PATH,
    MATCHES_PATH,
)

try:
    from tqdm import tqdm
    _HAS_TQDM = True
except ImportError:
    _HAS_TQDM = False


def load_extracted_clawhub_items(path: str) -> list:
    """Load only Clawhub items from extracted_data.jsonl.

    Args:
        path: Path to the extracted_data.jsonl file.

    Returns:
        List of dicts where source == 'clawhub'.
    """
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                warnings.warn(f"Skipping malformed JSON at line {line_num}: {e}")
                continue
            if record.get("source") == "clawhub":
                items.append(record)
    return items


def extract_slug_from_url(url: str) -> Optional[str]:
    """Extract skill slug from clawhub URL like https://clawhub.ai/skills/chef.

    Args:
        url: A Clawhub skill URL.

    Returns:
        The slug string (e.g. 'chef'), or None if URL does not match expected pattern.
    """
    if not url or not isinstance(url, str):
        return None
    # Expected form: https://clawhub.ai/skills/{slug}
    prefix = "https://clawhub.ai/skills/"
    if url.startswith(prefix):
        slug = url[len(prefix):].strip("/").split("?")[0].split("#")[0]
        if slug:
            return slug
    return None


def run_matching(extracted_path: str, clawhub_path: str, output_path: str) -> dict:
    """Match all extracted Clawhub items to full Clawhub dataset.

    For each Clawhub item in the extracted data:
    1. Try slug-based lookup first (derived from URL).
    2. Fall back to name-based matching via match_skill_to_clawhub_stats.
    3. Record match result and marketplace stats.

    Args:
        extracted_path: Path to extracted_data.jsonl.
        clawhub_path: Path to clawhub_skills_complete.json.
        output_path: Path where the result JSON will be written.

    Returns:
        The result dict (also written to output_path).
    """
    # Load full Clawhub dataset and build index
    print(f"Loading full Clawhub dataset...", end=" ", flush=True)
    with open(clawhub_path, "r", encoding="utf-8") as f:
        clawhub_skills = json.load(f)
    print(f"{len(clawhub_skills)} skills loaded")

    clawhub_index = build_clawhub_index(clawhub_skills)

    # Load extracted Clawhub items
    print(f"Loading extracted Clawhub items...", end=" ", flush=True)
    items = load_extracted_clawhub_items(extracted_path)
    print(f"{len(items)} items")

    # Match each item
    print("Matching skills...")

    matches = []
    matched_by_slug = 0
    matched_by_name = 0
    no_match = 0
    total = len(items)

    iterator = tqdm(items, desc="Matching") if _HAS_TQDM else items

    for idx, item in enumerate(iterator):
        if not _HAS_TQDM and idx > 0 and idx % 100 == 0:
            print(f"  Progress: {idx}/{total} ({100.0 * idx / total:.1f}%)")

        skill_name = item.get("name", "")
        url = item.get("url", "")
        slug = extract_slug_from_url(url) or item.get("id", "")

        matched = False
        match_method = None
        marketplace_stats = None

        # 1. Slug-based lookup via clawhub_index
        if slug and slug in clawhub_index:
            skill_data = clawhub_index[slug]
            stats = skill_data.get("stats", {})
            latest = skill_data.get("latestVersion", {}) or {}
            marketplace_stats = {
                "stars": stats.get("stars", 0),
                "downloads": stats.get("downloads", 0),
                "installs_all_time": stats.get("installsAllTime", 0),
                "versions": stats.get("versions", 0),
                "latest_version": latest.get("version"),
                "license": latest.get("license"),
                "matched_slug": skill_data.get("slug"),
                "matched_display_name": skill_data.get("displayName"),
            }
            matched = True
            match_method = "slug"
            matched_by_slug += 1

        # 2. Name-based matching via match_skill_to_clawhub_stats
        if not matched and skill_name:
            stats_result = match_skill_to_clawhub_stats(skill_name, clawhub_index)
            if stats_result is not None:
                marketplace_stats = {
                    "stars": stats_result.get("stars", 0),
                    "downloads": stats_result.get("downloads", 0),
                    "installs_all_time": stats_result.get("installs_all_time", 0),
                    "versions": stats_result.get("versions", 0),
                    "latest_version": stats_result.get("latest_version"),
                    "license": stats_result.get("license"),
                    "matched_slug": stats_result.get("slug"),
                    "matched_display_name": stats_result.get("displayName"),
                }
                matched = True
                match_method = "name"
                matched_by_name += 1

        if not matched:
            no_match += 1

        matches.append(
            {
                "skill_id": slug or skill_name,
                "skill_name": skill_name,
                "extracted_url": url,
                "matched": matched,
                "match_method": match_method,
                "marketplace_stats": marketplace_stats,
            }
        )

    match_rate = (matched_by_slug + matched_by_name) / total * 100 if total > 0 else 0.0

    result = {
        "matches": matches,
        "stats": {
            "total": total,
            "matched_by_slug": matched_by_slug,
            "matched_by_name": matched_by_name,
            "no_match": no_match,
            "match_rate": round(match_rate, 4),
        },
    }

    # Write output
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    # Print summary
    print()
    print("Matching complete!")
    print(f"  Matched by slug: {matched_by_slug} ({100.0 * matched_by_slug / total:.1f}%)")
    print(f"  Matched by name: {matched_by_name} ({100.0 * matched_by_name / total:.1f}%)")
    print(f"  No match:        {no_match} ({100.0 * no_match / total:.1f}%)")
    print(f"  Total match rate: {match_rate:.1f}%")
    print()
    print(f"Results saved to: {output_path}")

    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Match extracted Clawhub skills to marketplace data"
    )
    parser.add_argument(
        "--extracted",
        default=EXTRACTED_DATA_PATH,
        help="Path to extracted_data.jsonl (default: %(default)s)",
    )
    parser.add_argument(
        "--clawhub",
        default=CLAWHUB_COMPLETE_PATH,
        help="Path to clawhub_skills_complete.json (default: %(default)s)",
    )
    parser.add_argument(
        "--output",
        default=MATCHES_PATH,
        help="Output JSON path (default: %(default)s)",
    )
    args = parser.parse_args()

    run_matching(args.extracted, args.clawhub, args.output)
