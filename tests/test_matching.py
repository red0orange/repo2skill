"""Tests for validation/match_clawhub_github.py."""

import pytest

from validation.match_clawhub_github import (
    build_clawhub_index,
    extract_github_link,
    match_skill_to_clawhub_stats,
    match_skill_to_github,
    normalize_name,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_SKILL_WITH_SOURCE_URL = {
    "slug": "my-tool",
    "displayName": "My Tool",
    "sourceUrl": "https://github.com/example-owner/example-repo",
    "stats": {"stars": 10, "downloads": 5, "installsAllTime": 50, "versions": 2},
    "latestVersion": {"version": "1.0.0", "license": "MIT"},
}

SAMPLE_SKILL_WITHOUT_GITHUB = {
    "slug": "chef",
    "displayName": "Chef",
    "summary": "Help users cook.",
    "stats": {"stars": 2, "downloads": 0, "installsAllTime": 3, "versions": 1},
    "latestVersion": {"version": "0.1.0", "license": None},
}

SAMPLE_SKILL_SPECIAL_CHARS = {
    "slug": "m3u8-media-downloader",
    "displayName": "M3U8 Media Downloader",
    "stats": {"stars": 42, "downloads": 100, "installsAllTime": 500, "versions": 3},
    "latestVersion": {"version": "2.1.0", "license": "Apache-2.0"},
}


# ---------------------------------------------------------------------------
# extract_github_link
# ---------------------------------------------------------------------------


def test_extract_github_link_from_url():
    """Skill with a sourceUrl pointing to GitHub returns (repo, 'high', 'direct_link')."""
    repo, confidence, method = extract_github_link(SAMPLE_SKILL_WITH_SOURCE_URL)
    assert repo == "example-owner/example-repo"
    assert confidence == "high"
    assert method == "direct_link"


def test_extract_github_link_from_repository_field():
    """Skill with a 'repository' field pointing to GitHub is handled."""
    skill = {
        "slug": "some-skill",
        "displayName": "Some Skill",
        "repository": "https://github.com/org/repo.git",
    }
    repo, confidence, method = extract_github_link(skill)
    assert repo == "org/repo"
    assert confidence == "high"
    assert method == "direct_link"


def test_extract_github_link_missing():
    """Skill without any GitHub field returns (None, None, None)."""
    repo, confidence, method = extract_github_link(SAMPLE_SKILL_WITHOUT_GITHUB)
    assert repo is None
    assert confidence is None
    assert method is None


def test_extract_github_link_empty_skill():
    """Empty skill dict returns (None, None, None)."""
    repo, confidence, method = extract_github_link({})
    assert (repo, confidence, method) == (None, None, None)


def test_extract_github_link_from_homepage():
    """Skill with a 'homepage' field containing a GitHub URL is matched."""
    skill = {
        "slug": "some-skill",
        "displayName": "Some Skill",
        "homepage": "https://github.com/myorg/myrepo",
    }
    repo, confidence, method = extract_github_link(skill)
    assert repo == "myorg/myrepo"
    assert confidence == "high"
    assert method == "direct_link"


def test_extract_github_link_from_website():
    """Skill with a 'website' field containing a GitHub URL is matched."""
    skill = {
        "slug": "another-skill",
        "displayName": "Another Skill",
        "website": "https://github.com/anotherrorg/anotherrepo",
    }
    repo, confidence, method = extract_github_link(skill)
    assert repo == "anotherrorg/anotherrepo"
    assert confidence == "high"
    assert method == "direct_link"


# ---------------------------------------------------------------------------
# normalize_name
# ---------------------------------------------------------------------------


def test_normalize_name_lowercases():
    """normalize_name lowercases the input."""
    assert normalize_name("Chef") == "chef"


def test_normalize_name_strips_whitespace():
    """normalize_name strips leading/trailing whitespace."""
    assert normalize_name("  Chef  ") == "chef"


def test_normalize_name_removes_special_chars():
    """normalize_name removes non-alphanumeric, non-space characters."""
    result = normalize_name("M3U8 Media Downloader!")
    assert result == "m3u8 media downloader"


def test_normalize_name_collapses_spaces():
    """normalize_name collapses multiple spaces into one."""
    result = normalize_name("My   Tool")
    assert result == "my tool"


def test_normalize_name_empty_string():
    """normalize_name handles empty string without error."""
    assert normalize_name("") == ""


# ---------------------------------------------------------------------------
# build_clawhub_index
# ---------------------------------------------------------------------------


def test_build_clawhub_index_keys():
    """build_clawhub_index creates normalized display-name and slug entries."""
    skills = [SAMPLE_SKILL_WITHOUT_GITHUB, SAMPLE_SKILL_SPECIAL_CHARS]
    index = build_clawhub_index(skills)

    # Normalized display names
    assert "chef" in index
    assert "m3u8 media downloader" in index

    # Slugs
    assert "chef" in index
    assert "m3u8-media-downloader" in index


def test_build_clawhub_index_values():
    """Index values are the original skill dicts."""
    skills = [SAMPLE_SKILL_WITHOUT_GITHUB]
    index = build_clawhub_index(skills)
    assert index["chef"] is SAMPLE_SKILL_WITHOUT_GITHUB


def test_build_clawhub_index_empty():
    """build_clawhub_index handles empty list."""
    index = build_clawhub_index([])
    assert index == {}


def test_build_clawhub_index_missing_fields():
    """build_clawhub_index skips skills that lack displayName and slug."""
    skill = {"summary": "No name here"}
    index = build_clawhub_index([skill])
    # Nothing should be indexed (no displayName, no slug)
    assert index == {}


# ---------------------------------------------------------------------------
# match_skill_to_clawhub_stats
# ---------------------------------------------------------------------------


def test_match_skill_to_clawhub_stats_exact():
    """Exact name match returns the expected stats dict."""
    skills = [SAMPLE_SKILL_WITHOUT_GITHUB, SAMPLE_SKILL_SPECIAL_CHARS]
    index = build_clawhub_index(skills)

    result = match_skill_to_clawhub_stats("Chef", index)

    assert result is not None
    assert result["slug"] == "chef"
    assert result["displayName"] == "Chef"
    assert result["stars"] == 2
    assert result["versions"] == 1
    assert result["latest_version"] == "0.1.0"


def test_match_skill_to_clawhub_stats_case_insensitive():
    """Name matching is case-insensitive."""
    skills = [SAMPLE_SKILL_WITHOUT_GITHUB]
    index = build_clawhub_index(skills)
    result = match_skill_to_clawhub_stats("CHEF", index)
    assert result is not None
    assert result["slug"] == "chef"


def test_match_skill_to_clawhub_stats_special_chars():
    """Name with special characters is matched after normalization."""
    skills = [SAMPLE_SKILL_SPECIAL_CHARS]
    index = build_clawhub_index(skills)
    result = match_skill_to_clawhub_stats("M3U8 Media Downloader", index)
    assert result is not None
    assert result["stars"] == 42
    assert result["installs_all_time"] == 500


def test_match_skill_to_clawhub_stats_no_match():
    """Unmatched name returns None."""
    skills = [SAMPLE_SKILL_WITHOUT_GITHUB]
    index = build_clawhub_index(skills)
    result = match_skill_to_clawhub_stats("NonExistentSkillXYZ12345", index)
    assert result is None


def test_match_skill_to_clawhub_stats_partial():
    """Partial name match still finds a skill."""
    skills = [SAMPLE_SKILL_SPECIAL_CHARS]
    index = build_clawhub_index(skills)
    # "m3u8 media" is a substring of "m3u8 media downloader"
    result = match_skill_to_clawhub_stats("M3U8 Media", index)
    assert result is not None
    assert result["slug"] == "m3u8-media-downloader"


def test_match_skill_to_clawhub_stats_returns_license():
    """Returned stats include the license field."""
    skills = [SAMPLE_SKILL_SPECIAL_CHARS]
    index = build_clawhub_index(skills)
    result = match_skill_to_clawhub_stats("M3U8 Media Downloader", index)
    assert result is not None
    assert result["license"] == "Apache-2.0"


# ---------------------------------------------------------------------------
# match_skill_to_github
# ---------------------------------------------------------------------------


def test_match_skill_to_github_with_source_url():
    """Skill with sourceUrl pointing to GitHub is matched correctly."""
    result = match_skill_to_github(SAMPLE_SKILL_WITH_SOURCE_URL)
    assert result["skill_id"] == "my-tool"
    assert result["skill_name"] == "My Tool"
    assert result["github_repo"] == "example-owner/example-repo"
    assert result["match_confidence"] == "high"
    assert result["match_method"] == "direct_link"


def test_match_skill_to_github_no_link():
    """Skill without GitHub link returns None for repo fields."""
    result = match_skill_to_github(SAMPLE_SKILL_WITHOUT_GITHUB)
    assert result["skill_id"] == "chef"
    assert result["skill_name"] == "Chef"
    assert result["github_repo"] is None
    assert result["match_confidence"] is None
    assert result["match_method"] is None


def test_match_skill_to_github_mock_search():
    """mock_search=True simulates a search hit when no direct link exists."""
    result = match_skill_to_github(SAMPLE_SKILL_WITHOUT_GITHUB, mock_search=True)
    assert result["github_repo"] is not None
    assert result["match_method"] == "name_search"
    assert result["match_confidence"] == "low"


def test_match_skill_to_github_result_keys():
    """Result dict always contains exactly the expected keys."""
    result = match_skill_to_github(SAMPLE_SKILL_WITHOUT_GITHUB)
    expected_keys = {"skill_id", "skill_name", "github_repo", "match_confidence", "match_method"}
    assert set(result.keys()) == expected_keys
