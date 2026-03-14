#!/usr/bin/env python3
"""
Large-scale parallel analysis with async processing.
Supports 30,000+ samples with checkpoint recovery.
"""

import asyncio
import aiohttp
import json
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).parent))

import config_large as config
from data_sampler import prepare_samples
from scorer import add_scores_to_data
from analyzer import (
    analyze_capability_distribution,
    analyze_skillability_distribution,
    get_top_candidates,
    generate_summary_stats
)
from visualizer import generate_all_plots
from report_generator import generate_html_report


class AsyncGLMClient:
    """Async GLM API client with rate limiting and retry."""

    def __init__(self, api_key: str, api_url: str, model: str,
                 temperature: float, max_retries: int, max_concurrent: int):
        self.api_key = api_key
        self.api_url = api_url
        self.model = model
        self.temperature = temperature
        self.max_retries = max_retries
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def call_api(self, messages: list) -> Optional[str]:
        """Call GLM API with async and retry logic."""
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
                async with self.semaphore:
                    async with self.session.post(
                        self.api_url,
                        headers=headers,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=60)
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            return result['choices'][0]['message']['content']
                        elif response.status == 429:
                            wait_time = (2 ** attempt) * 2
                            await asyncio.sleep(wait_time)
                        else:
                            text = await response.text()
                            print(f"API error {response.status}: {text[:200]}")
                            await asyncio.sleep(2 ** attempt)

            except Exception as e:
                print(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)

        return None

    async def extract_structured_data(self, item: Dict[str, Any],
                                     source: str) -> Optional[Dict[str, Any]]:
        """Extract structured data from item."""
        system_prompt = self._get_system_prompt()
        user_prompt = self._get_user_prompt(item, source)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = await self.call_api(messages)
        if not response:
            return None

        # Parse JSON response
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()

            data = json.loads(json_str)
            return data

        except json.JSONDecodeError as e:
            return None

    def _get_system_prompt(self) -> str:
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
        name = skill.get('displayName', '')
        summary = skill.get('summary', '')

        return f"""Analyze the following Clawhub skill:

Name: {name}
Summary: {summary}

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
}}"""

    def _get_github_prompt(self, repo: Dict[str, Any]) -> str:
        name = repo.get('full_name', '')
        description = repo.get('description', '')
        language = repo.get('language', '')
        topics = ', '.join(repo.get('topics', []))
        stars = repo.get('stargazers_count', 0)
        readme = repo.get('readme_content', '')[:3000]  # Limit to 3k chars for speed

        return f"""Analyze the following GitHub repository:

Name: {name}
Description: {description}
Language: {language}
Topics: {topics}
Stars: {stars}

README (first 3000 chars):
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
}}"""


async def process_batch(client: AsyncGLMClient, items: List[tuple],
                       source: str) -> List[Dict[str, Any]]:
    """Process a batch of items in parallel."""
    tasks = []
    for item, metadata in items:
        task = client.extract_structured_data(item, source)
        tasks.append((task, metadata))

    results = []
    for task, metadata in tasks:
        result = await task
        if result:
            result.update(metadata)
            results.append(result)

    return results


def save_checkpoint(data: List[Dict], checkpoint_path: str):
    """Save checkpoint to disk."""
    with open(checkpoint_path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')


def load_checkpoint(checkpoint_path: str) -> List[Dict]:
    """Load checkpoint from disk."""
    if not Path(checkpoint_path).exists():
        return []

    data = []
    with open(checkpoint_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data


async def main():
    """Main analysis pipeline with parallel processing."""
    print("=" * 60)
    print("Large-Scale Software2Skill Analysis")
    print(f"Target: {config.CLAWHUB_SAMPLE_SIZE + config.GITHUB_SAMPLE_SIZE:,} samples")
    print(f"Concurrency: {config.MAX_CONCURRENT_REQUESTS}")
    print("=" * 60)

    # Create output directories
    Path(config.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    Path(config.CHECKPOINT_DIR).mkdir(parents=True, exist_ok=True)
    Path(config.FIGURES_DIR).mkdir(parents=True, exist_ok=True)

    # Step 1: Data Sampling
    print("\n[Step 1/6] Sampling data...")
    samples = prepare_samples(
        config.CLAWHUB_DATA_PATH,
        config.GITHUB_DATA_PATH,
        config.README_DIR,
        config.CLAWHUB_SAMPLE_SIZE,
        config.GITHUB_SAMPLE_SIZE
    )

    # Prepare items with metadata
    clawhub_items = []
    for skill in samples['clawhub']:
        metadata = {
            'id': skill.get('slug', ''),
            'source': 'clawhub',
            'name': skill.get('displayName', ''),
            'description': skill.get('summary', ''),
            'url': f"https://clawhub.ai/skills/{skill.get('slug', '')}",
            'stars': skill.get('stats', {}).get('stars', 0),
            'language': None,
            'archived': False,
            'license': skill.get('latestVersion', {}).get('license')
        }
        clawhub_items.append((skill, metadata))

    github_items = []
    for repo in samples['github']:
        metadata = {
            'id': repo.get('full_name', ''),
            'source': 'github',
            'name': repo.get('full_name', ''),
            'description': repo.get('description', ''),
            'url': repo.get('html_url', ''),
            'stars': repo.get('stargazers_count', 0),
            'language': repo.get('language', ''),
            'archived': repo.get('archived', False),
            'license': repo.get('license', '')
        }
        github_items.append((repo, metadata))

    total_items = len(clawhub_items) + len(github_items)

    # Step 2: Parallel LLM Extraction
    print(f"\n[Step 2/6] Extracting structured data with {config.MAX_CONCURRENT_REQUESTS} concurrent requests...")
    print(f"Total items: {total_items:,}")

    checkpoint_path = f"{config.CHECKPOINT_DIR}/extraction_checkpoint.jsonl"
    extracted_data = load_checkpoint(checkpoint_path)
    processed_ids = {item['id'] for item in extracted_data}

    print(f"Loaded {len(extracted_data):,} items from checkpoint")

    async with AsyncGLMClient(
        config.GLM_API_KEY,
        config.GLM_API_URL,
        config.GLM_MODEL,
        config.GLM_TEMPERATURE,
        config.GLM_MAX_RETRIES,
        config.MAX_CONCURRENT_REQUESTS
    ) as client:

        # Process Clawhub
        clawhub_todo = [(item, meta) for item, meta in clawhub_items
                       if meta['id'] not in processed_ids]

        if clawhub_todo:
            print(f"\nProcessing {len(clawhub_todo):,} Clawhub skills...")
            with tqdm(total=len(clawhub_todo), desc="Clawhub") as pbar:
                for i in range(0, len(clawhub_todo), config.BATCH_SIZE):
                    batch = clawhub_todo[i:i + config.BATCH_SIZE]
                    results = await process_batch(client, batch, 'clawhub')
                    extracted_data.extend(results)
                    pbar.update(len(batch))

                    # Save checkpoint
                    if len(extracted_data) % config.CHECKPOINT_INTERVAL == 0:
                        save_checkpoint(extracted_data, checkpoint_path)

        # Process GitHub
        github_todo = [(item, meta) for item, meta in github_items
                      if meta['id'] not in processed_ids]

        if github_todo:
            print(f"\nProcessing {len(github_todo):,} GitHub repos...")
            with tqdm(total=len(github_todo), desc="GitHub") as pbar:
                for i in range(0, len(github_todo), config.BATCH_SIZE):
                    batch = github_todo[i:i + config.BATCH_SIZE]
                    results = await process_batch(client, batch, 'github')
                    extracted_data.extend(results)
                    pbar.update(len(batch))

                    # Save checkpoint
                    if len(extracted_data) % config.CHECKPOINT_INTERVAL == 0:
                        save_checkpoint(extracted_data, checkpoint_path)

    print(f"\n✓ Successfully extracted {len(extracted_data):,}/{total_items:,} items")

    # Save final extracted data
    save_checkpoint(extracted_data, config.EXTRACTED_DATA_PATH)
    print(f"✓ Saved extracted data to {config.EXTRACTED_DATA_PATH}")

    # Step 3: Calculate Scores
    print("\n[Step 3/6] Calculating opportunity scores...")
    extracted_data = add_scores_to_data(
        extracted_data,
        config.SKILLABILITY_WEIGHTS,
        config.OPPORTUNITY_WEIGHTS
    )
    save_checkpoint(extracted_data, config.EXTRACTED_DATA_PATH)

    # Step 4: Analysis
    print("\n[Step 4/6] Analyzing distributions...")
    cap_dist = analyze_capability_distribution(extracted_data)
    skill_dist = analyze_skillability_distribution(extracted_data)
    top_candidates = get_top_candidates(extracted_data, k=100)  # Top-100 for large scale
    summary_stats = generate_summary_stats(extracted_data)

    # Save top candidates
    with open(config.TOP_CANDIDATES_PATH, 'w', encoding='utf-8') as f:
        json.dump(top_candidates, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved top candidates to {config.TOP_CANDIDATES_PATH}")

    # Step 5: Visualization
    print("\n[Step 5/6] Generating visualizations...")
    generate_all_plots(cap_dist, skill_dist, top_candidates, config.FIGURES_DIR)

    # Step 6: Report Generation
    print("\n[Step 6/6] Generating HTML report...")
    generate_html_report(
        summary_stats,
        top_candidates,
        config.FIGURES_DIR,
        config.ANALYSIS_REPORT_PATH
    )

    # Print summary
    print("\n" + "=" * 60)
    print("Analysis Complete!")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"  Total items analyzed: {summary_stats['total_items']:,}")
    print(f"  Clawhub skills: {summary_stats['clawhub_count']:,}")
    print(f"  GitHub repos: {summary_stats['github_count']:,}")
    print(f"  Avg Clawhub skillability: {summary_stats['clawhub_avg_skillability']:.2f}")
    print(f"  Avg GitHub skillability: {summary_stats['github_avg_skillability']:.2f}")
    print(f"  High skillability repos (≥4): {summary_stats['github_high_skillability_count']:,}")

    print(f"\n📁 Output files:")
    print(f"  - Extracted data: {config.EXTRACTED_DATA_PATH}")
    print(f"  - Top candidates: {config.TOP_CANDIDATES_PATH}")
    print(f"  - HTML report: {config.ANALYSIS_REPORT_PATH}")
    print(f"  - Figures: {config.FIGURES_DIR}/")

    print(f"\n🌐 Open the report:")
    print(f"  file://{Path(config.ANALYSIS_REPORT_PATH).absolute()}")


if __name__ == "__main__":
    asyncio.run(main())
