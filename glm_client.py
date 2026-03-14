"""GLM API client for structured extraction."""

import json
import time
import requests
from typing import Dict, Any, Optional


class GLMClient:
    """Client for GLM API with retry logic."""

    def __init__(self, api_key: str, api_url: str, model: str, temperature: float, max_retries: int):
        self.api_key = api_key
        self.api_url = api_url
        self.model = model
        self.temperature = temperature
        self.max_retries = max_retries

    def call_api(self, messages: list) -> Optional[str]:
        """Call GLM API with retry logic.

        Args:
            messages: List of message dictionaries

        Returns:
            Response content or None if failed
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature
        }

        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=60
                )

                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content']
                elif response.status_code == 429:
                    # Rate limit, wait and retry
                    wait_time = (2 ** attempt) * 2
                    print(f"Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"API error {response.status_code}: {response.text}")
                    time.sleep(2 ** attempt)

            except Exception as e:
                print(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)

        return None

    def extract_structured_data(self, item: Dict[str, Any], source: str) -> Optional[Dict[str, Any]]:
        """Extract structured data from a Clawhub skill or GitHub repo.

        Args:
            item: Raw item data
            source: 'clawhub' or 'github'

        Returns:
            Extracted structured data or None if failed
        """
        system_prompt = self._get_system_prompt()
        user_prompt = self._get_user_prompt(item, source)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = self.call_api(messages)
        if not response:
            return None

        # Parse JSON response
        try:
            # Try to extract JSON from markdown code blocks
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()

            data = json.loads(json_str)
            return data

        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {e}")
            print(f"Response: {response[:500]}")
            return None

    def _get_system_prompt(self) -> str:
        """Get system prompt for extraction."""
        return """You are an expert research annotator for studying software projects as potential agent skills.

Your task is to analyze one item (either a GitHub repository or a Clawhub skill) and output a single JSON object.

Rules:
1. Focus on the primary user-facing capability, not implementation details.
2. Be conservative. Do not overstate skillability.
3. A project is skillifiable only if it has a clear task boundary, can be wrapped as an agent-callable unit, and offers practical automation value.
4. Frameworks, SDKs, resource lists, tutorials, datasets should not be rated as highly skillifiable unless they expose a reusable task-level capability.
5. Use only the allowed enum values.
6. Output valid JSON only, with no markdown and no extra commentary."""

    def _get_user_prompt(self, item: Dict[str, Any], source: str) -> str:
        """Generate user prompt for a specific item."""
        if source == 'clawhub':
            return self._get_clawhub_prompt(item)
        else:
            return self._get_github_prompt(item)

    def _get_clawhub_prompt(self, skill: Dict[str, Any]) -> str:
        """Generate prompt for Clawhub skill."""
        # Extract relevant fields
        name = skill.get('displayName', '')
        slug = skill.get('slug', '')
        summary = skill.get('summary', '')

        # Get SKILL.md content if available
        skill_md = ""
        files = skill.get('files', [])
        for f in files:
            if f.get('path') == 'SKILL.md':
                skill_md = f.get('content', '')[:5000]
                break

        prompt = f"""Analyze the following Clawhub skill:

Name: {name}
Slug: {slug}
Summary: {summary}

SKILL.md content (first 5000 chars):
{skill_md}

Return a JSON object with these fields:
{{
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
}}

Scoring guidance:
- task_clarity, interface_clarity, composability, automation_value: higher is better
- deployment_friction, operational_risk: higher is worse
- skillability_score is overall 1-5"""

        return prompt

    def _get_github_prompt(self, repo: Dict[str, Any]) -> str:
        """Generate prompt for GitHub repo."""
        name = repo.get('full_name', '')
        description = repo.get('description', '')
        language = repo.get('language', '')
        topics = ', '.join(repo.get('topics', []))
        stars = repo.get('stargazers_count', 0)
        readme = repo.get('readme_content', '')[:5000]

        prompt = f"""Analyze the following GitHub repository:

Name: {name}
Description: {description}
Language: {language}
Topics: {topics}
Stars: {stars}

README (first 5000 chars):
{readme}

Return a JSON object with these fields:
{{
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
}}

Scoring guidance:
- task_clarity, interface_clarity, composability, automation_value: higher is better
- deployment_friction, operational_risk: higher is worse
- skillability_score is overall 1-5"""

        return prompt
