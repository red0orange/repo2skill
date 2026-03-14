"""Tests for shared pipeline utilities."""

from pipeline_utils import (
    build_clawhub_metadata,
    build_github_metadata,
    parse_json_response,
)


def test_parse_json_response_from_plain_json():
    result = parse_json_response('{"value": 1, "name": "demo"}')
    assert result == {"value": 1, "name": "demo"}


def test_parse_json_response_from_markdown_code_block():
    payload = """```json
{"primary_capability": "web_automation"}
```"""
    result = parse_json_response(payload)
    assert result == {"primary_capability": "web_automation"}


def test_build_clawhub_metadata_normalizes_license():
    skill = {
        "slug": "demo-skill",
        "displayName": "Demo Skill",
        "summary": "Short summary",
        "stats": {"stars": 7},
        "latestVersion": {"license": "MIT"},
    }
    metadata = build_clawhub_metadata(skill)

    assert metadata["id"] == "demo-skill"
    assert metadata["source"] == "clawhub"
    assert metadata["license"] == "MIT"
    assert metadata["archived"] is False


def test_build_github_metadata_extracts_license_name_from_dict():
    repo = {
        "full_name": "org/project",
        "description": "Demo repo",
        "html_url": "https://github.com/org/project",
        "stargazers_count": 42,
        "language": "Python",
        "archived": False,
        "license": {"spdx_id": "Apache-2.0", "name": "Apache License 2.0"},
    }
    metadata = build_github_metadata(repo)

    assert metadata["id"] == "org/project"
    assert metadata["source"] == "github"
    assert metadata["license"] == "Apache-2.0"
    assert metadata["stars"] == 42
