"""Shared helpers for prompt building, metadata normalization, and I/O."""

from __future__ import annotations

import asyncio
import html
import json
from pathlib import Path
from typing import Any, Awaitable, Dict, Optional, Sequence

SYSTEM_PROMPT = """You are an expert research annotator for studying software projects as potential agent skills.

Your task is to analyze one item (either a GitHub repository or a Clawhub skill) and output a single JSON object.

Rules:
1. Focus on the primary user-facing capability, not implementation details.
2. Be conservative. Do not overstate skillability.
3. A project is skillifiable only if it has a clear task boundary, can be wrapped as an agent-callable unit, and offers practical automation value.
4. Frameworks, SDKs, resource lists, tutorials, datasets should not be rated as highly skillifiable unless they expose a reusable task-level capability.
5. Use only the allowed enum values.
6. Output valid JSON only, with no markdown and no extra commentary."""

EXTRACTION_SCHEMA = """Return a JSON object with these fields:
{
  "primary_capability": "<one of: code_devops, data_retrieval_search, document_processing, web_automation, communication_collaboration, knowledge_workflow_research, business_productivity_ops, multimedia_content, system_infrastructure, external_service_connector>",
  "granularity": "<one of: primitive_tool, service_wrapper, workflow_skill, platform_adapter>",
  "execution_mode": "<one of: local_deterministic, remote_api_mediated, browser_mediated, human_in_the_loop, hybrid>",
  "task_clarity": <1-5>,
  "interface_clarity": <1-5>,
  "composability": <1-5>,
  "deployment_friction": <1-5>,
  "automation_value": <1-5>,
  "operational_risk": <1-5>,
  "skillability_score": <1-5>,
  "skillability_rationale": "<brief explanation>"
}

Scoring guidance:
- task_clarity, interface_clarity, composability, automation_value: higher is better
- deployment_friction, operational_risk: higher is worse
- skillability_score is overall 1-5"""


def extract_license_name(value: Any) -> Optional[str]:
    """Normalize license fields coming from different upstream schemas."""
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned or None
    if isinstance(value, dict):
        for key in ("spdx_id", "name", "key"):
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()
    return None


def build_clawhub_metadata(skill: Dict[str, Any]) -> Dict[str, Any]:
    """Build normalized metadata for a Clawhub skill extraction result."""
    return {
        "id": skill.get("slug", ""),
        "source": "clawhub",
        "name": skill.get("displayName", ""),
        "description": skill.get("summary", ""),
        "url": f"https://clawhub.ai/skills/{skill.get('slug', '')}",
        "stars": skill.get("stats", {}).get("stars", 0),
        "language": None,
        "archived": False,
        "license": extract_license_name(skill.get("latestVersion", {}).get("license")),
    }


def build_github_metadata(repo: Dict[str, Any]) -> Dict[str, Any]:
    """Build normalized metadata for a GitHub repository extraction result."""
    return {
        "id": repo.get("full_name", ""),
        "source": "github",
        "name": repo.get("full_name", ""),
        "description": repo.get("description", ""),
        "url": repo.get("html_url", ""),
        "stars": repo.get("stargazers_count", 0),
        "language": repo.get("language", ""),
        "archived": repo.get("archived", False),
        "license": extract_license_name(repo.get("license")),
    }


def parse_json_response(response: str) -> Optional[Dict[str, Any]]:
    """Parse model output that may be plain JSON or wrapped in code fences."""
    if not response:
        return None

    if "```json" in response:
        json_str = response.split("```json", maxsplit=1)[1].split("```", maxsplit=1)[0].strip()
    elif "```" in response:
        json_str = response.split("```", maxsplit=1)[1].split("```", maxsplit=1)[0].strip()
    else:
        json_str = response.strip()

    return json.loads(json_str)


def build_clawhub_prompt(
    skill: Dict[str, Any],
    *,
    include_slug: bool = True,
    include_skill_md: bool = True,
    skill_md_chars: int = 5000,
) -> str:
    """Build the user prompt for a Clawhub skill."""
    sections = [
        "Analyze the following Clawhub skill:",
        "",
        f"Name: {skill.get('displayName', '')}",
    ]

    if include_slug:
        sections.append(f"Slug: {skill.get('slug', '')}")

    sections.append(f"Summary: {skill.get('summary', '')}")

    if include_skill_md:
        skill_md = ""
        for file_info in skill.get("files", []):
            if file_info.get("path") == "SKILL.md":
                skill_md = file_info.get("content", "")[:skill_md_chars]
                break
        sections.extend(
            [
                "",
                f"SKILL.md content (first {skill_md_chars} chars):",
                skill_md,
            ]
        )

    sections.extend(["", EXTRACTION_SCHEMA])
    return "\n".join(sections)


def build_github_prompt(repo: Dict[str, Any], *, readme_chars: int = 5000) -> str:
    """Build the user prompt for a GitHub repository."""
    topics = ", ".join(repo.get("topics", []))
    readme = repo.get("readme_content", "")[:readme_chars]
    sections = [
        "Analyze the following GitHub repository:",
        "",
        f"Name: {repo.get('full_name', '')}",
        f"Description: {repo.get('description', '')}",
        f"Language: {repo.get('language', '')}",
        f"Topics: {topics}",
        f"Stars: {repo.get('stargazers_count', 0)}",
        "",
        f"README (first {readme_chars} chars):",
        readme,
        "",
        EXTRACTION_SCHEMA,
    ]
    return "\n".join(sections)


def build_user_prompt(item: Dict[str, Any], source: str, *, readme_chars: int = 5000) -> str:
    """Dispatch prompt construction based on data source."""
    if source == "clawhub":
        return build_clawhub_prompt(item)
    return build_github_prompt(item, readme_chars=readme_chars)


async def gather_extraction_results(
    task_pairs: Sequence[tuple[Awaitable[Optional[Dict[str, Any]]], Dict[str, Any]]]
) -> list[Dict[str, Any]]:
    """Await extraction tasks in parallel and merge successful results with metadata."""
    task_results = await asyncio.gather(*(task for task, _ in task_pairs))
    merged_results = []

    for result, (_, metadata) in zip(task_results, task_pairs):
        if result:
            result.update(metadata)
            merged_results.append(result)

    return merged_results


def escape_html(value: Any) -> str:
    """Escape arbitrary values for HTML output."""
    return html.escape(str(value), quote=True)


def ensure_parent_dir(path: str | Path) -> None:
    """Create the parent directory for an output file if needed."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
