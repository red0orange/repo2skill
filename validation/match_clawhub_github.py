"""Clawhub-GitHub matching functions for validation experiments.

Key insight: Current Clawhub data has no sourceUrl or repository fields,
so extract_github_link returns (None, None, None) for all current skills.
The primary useful function is match_skill_to_clawhub_stats which matches
by display name to retrieve marketplace metrics.
"""

import re
from typing import Dict, Optional, Tuple, Any


def extract_github_link(skill: dict) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Try to extract a GitHub repository link from a Clawhub skill.

    Checks the skill's sourceUrl and repository fields for a GitHub URL,
    then parses out the owner/repo path.

    Args:
        skill: Clawhub skill dict, potentially containing sourceUrl or
               repository fields.

    Returns:
        Tuple of (repo_name, confidence, method) where repo_name is in
        "owner/repo" format, or (None, None, None) if no GitHub link found.
        In practice, all current Clawhub skills lack these fields, so this
        returns (None, None, None) for all current data.
    """
    github_pattern = re.compile(
        r"github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git)?(?:[/?#].*)?$"
    )

    # Fields to check, in priority order
    candidate_fields = ["sourceUrl", "repository", "homepage", "website"]

    for field in candidate_fields:
        value = skill.get(field)
        if not value or not isinstance(value, str):
            continue
        match = github_pattern.search(value)
        if match:
            repo_name = match.group(1).rstrip("/")
            return (repo_name, "high", "direct_link")

    return (None, None, None)


def normalize_name(name: str) -> str:
    """Normalize a skill name for fuzzy matching.

    Lowercases, strips whitespace, and removes non-alphanumeric characters
    (keeping spaces for readability before final strip).

    Args:
        name: Raw skill display name.

    Returns:
        Normalized name suitable for comparison.
    """
    # Lowercase
    name = name.lower()
    # Remove characters that are not letters, digits, or spaces
    name = re.sub(r"[^a-z0-9 ]", "", name)
    # Collapse multiple spaces and strip edges
    name = re.sub(r"\s+", " ", name).strip()
    return name


def build_clawhub_index(clawhub_skills: list) -> dict:
    """Build a lookup index from the full Clawhub skills dataset.

    Creates two kinds of entries for each skill:
    - normalized displayName -> skill_data
    - slug -> skill_data  (for slug-based lookup)

    If two skills have the same normalized name or slug the later entry
    wins; in practice slugs are unique.

    Args:
        clawhub_skills: List of Clawhub skill dicts as loaded from
            clawhub_skills_complete.json.

    Returns:
        Dict mapping normalized_name or slug -> skill_data.
    """
    index: Dict[str, Any] = {}

    for skill in clawhub_skills:
        display_name = skill.get("displayName", "")
        slug = skill.get("slug", "")

        if display_name:
            key = normalize_name(display_name)
            if key:
                index[key] = skill

        if slug:
            # Slugs are already lowercase-hyphenated; store as-is
            index[slug] = skill

    return index


def match_skill_to_clawhub_stats(skill_name: str, clawhub_index: dict) -> Optional[dict]:
    """Match a skill name to Clawhub marketplace stats via display name lookup.

    Attempts an exact match on the normalized name first, then falls back to
    a partial (substring) match against all normalized index keys.

    Args:
        skill_name: The skill's display name (e.g. "Chef", "M3U8 Media Downloader").
        clawhub_index: Dict returned by build_clawhub_index.

    Returns:
        Dict with marketplace stats extracted from the matched skill, or None
        if no match is found.  The returned dict has the shape:
        {
            "slug": str,
            "displayName": str,
            "stars": int,
            "downloads": int,
            "installs_all_time": int,
            "versions": int,
            "latest_version": str | None,
            "license": str | None,
        }
    """
    normalized = normalize_name(skill_name)

    # 1. Exact match on normalized display name or slug
    skill_data = clawhub_index.get(normalized)

    # 2. Try matching against the raw slug (hyphens -> spaces)
    if skill_data is None:
        slug_key = skill_name.lower().replace(" ", "-")
        skill_data = clawhub_index.get(slug_key)

    # 3. Partial match: check if normalized name appears as substring of any key
    # Only partial match on longer keys (≥ 3 chars) to avoid false positives from short slugs
    if skill_data is None and normalized:
        for key, candidate in clawhub_index.items():
            if len(key) >= 3 and len(normalized) >= 3 and (normalized in key or key in normalized):
                skill_data = candidate
                break

    if skill_data is None:
        return None

    stats = skill_data.get("stats", {})
    latest = skill_data.get("latestVersion", {}) or {}

    return {
        "slug": skill_data.get("slug"),
        "displayName": skill_data.get("displayName"),
        "stars": stats.get("stars", 0),
        "downloads": stats.get("downloads", 0),
        "installs_all_time": stats.get("installsAllTime", 0),
        "versions": stats.get("versions", 0),
        "latest_version": latest.get("version"),
        "license": latest.get("license"),
    }


def match_skill_to_github(
    skill: dict,
    use_search: bool = True,
    mock_search: bool = False,
) -> dict:
    """Attempt to match a Clawhub skill to its GitHub repository.

    This is kept for API compatibility with the original plan.  Currently,
    all Clawhub skills lack sourceUrl / repository fields, so the direct-link
    extraction always returns None and the function reports no match.

    Args:
        skill: Clawhub skill dict.
        use_search: Accepted for API compatibility but has no effect in this implementation.
            When GitHub search is implemented (Task 3), wire it up here.
        mock_search: If True, simulate a successful search result for testing.

    Returns:
        Dict with keys:
        {
            "skill_id": str,
            "skill_name": str,
            "github_repo": str | None,
            "match_confidence": str | None,
            "match_method": str | None,
        }
    """
    skill_id = skill.get("slug") or skill.get("id", "")
    skill_name = skill.get("displayName") or skill.get("name", "")

    repo_name, confidence, method = extract_github_link(skill)

    if repo_name is None and mock_search:
        # Used in unit tests to simulate a search hit without real API calls
        repo_name = "mock-owner/mock-repo"
        confidence = "low"
        method = "name_search"

    return {
        "skill_id": skill_id,
        "skill_name": skill_name,
        "github_repo": repo_name,
        "match_confidence": confidence,
        "match_method": method,
    }
