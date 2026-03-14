#!/usr/bin/env python3
"""
Software2Skill Analysis - Main Pipeline
Uses Alibaba Bailian to analyze Clawhub skills and GitHub repositories.
"""

import asyncio
import aiohttp
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import config
from data_sampler import prepare_samples
from pipeline_utils import (
    SYSTEM_PROMPT,
    build_clawhub_metadata,
    build_clawhub_prompt,
    build_github_metadata,
    build_github_prompt,
    ensure_parent_dir,
    gather_extraction_results,
    parse_json_response,
)
from scorer import add_scores_to_data
from analyzer import (
    analyze_capability_distribution,
    analyze_granularity_distribution,
    analyze_skillability_distribution,
    generate_summary_stats,
    get_top_candidates,
)
from report_generator import generate_html_report
from visualizer import generate_all_plots


class AsyncBailianClient:
    """Async Bailian client with bounded concurrency and retries."""

    def __init__(self, api_key: str, api_url: str, model: str, temperature: float, max_retries: int):
        self.api_key = api_key
        self.api_url = api_url
        self.model = model
        self.temperature = temperature
        self.max_retries = max_retries
        self.semaphore = asyncio.Semaphore(config.MAX_CONCURRENT_REQUESTS)
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> "AsyncBailianClient":
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.session:
            await self.session.close()

    async def call_api(self, messages: list[dict[str, str]]) -> Optional[str]:
        """Call Bailian chat completions API."""
        if not self.api_key:
            raise ValueError("BAILIAN_API_KEY is not configured. Set it in the environment or .env.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }

        for attempt in range(self.max_retries):
            try:
                async with self.semaphore:
                    assert self.session is not None
                    async with self.session.post(
                        self.api_url,
                        headers=headers,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=60),
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            return result["choices"][0]["message"]["content"]
                        if response.status == 429:
                            await asyncio.sleep((2 ** attempt) * 2)
                            continue

                        message = await response.text()
                        print(f"API error {response.status}: {message[:200]}")
                        await asyncio.sleep(2 ** attempt)
            except Exception as exc:
                print(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {exc}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)

        return None

    async def extract_structured_data(self, item: Dict[str, Any], source: str) -> Optional[Dict[str, Any]]:
        """Extract structured labels and scores for one item."""
        user_prompt = build_clawhub_prompt(item) if source == "clawhub" else build_github_prompt(item)
        response = await self.call_api(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ]
        )
        if not response:
            return None

        try:
            return parse_json_response(response)
        except ValueError:
            return None


async def process_items(
    client: AsyncBailianClient,
    items: List[Dict[str, Any]],
    source: str,
) -> List[Dict[str, Any]]:
    """Process items in batches and merge model output with metadata."""
    metadata_builder = build_clawhub_metadata if source == "clawhub" else build_github_metadata
    results: List[Dict[str, Any]] = []

    for batch_start in range(0, len(items), config.BATCH_SIZE):
        batch = items[batch_start:batch_start + config.BATCH_SIZE]
        task_pairs = [
            (client.extract_structured_data(item, source), metadata_builder(item))
            for item in batch
        ]
        results.extend(await gather_extraction_results(task_pairs))
        print(f"  Processed {min(batch_start + len(batch), len(items))}/{len(items)} {source} items")

    return results


async def main() -> None:
    """Run the full Software2Skill pipeline."""
    print("=" * 60)
    print("Software2Skill Analysis Pipeline")
    print("Using Alibaba Bailian API")
    print("=" * 60)

    print("\n[Step 1/6] Sampling data...")
    samples = prepare_samples(
        config.CLAWHUB_DATA_PATH,
        config.GITHUB_DATA_PATH,
        config.README_DIR,
        config.CLAWHUB_SAMPLE_SIZE,
        config.GITHUB_SAMPLE_SIZE,
    )

    print("\n[Step 2/6] Extracting structured data with Bailian API...")
    async with AsyncBailianClient(
        config.BAILIAN_API_KEY,
        config.BAILIAN_API_URL,
        config.BAILIAN_MODEL,
        config.BAILIAN_TEMPERATURE,
        config.BAILIAN_MAX_RETRIES,
    ) as client:
        print(f"\nProcessing {len(samples['clawhub'])} Clawhub skills...")
        clawhub_results = await process_items(client, samples["clawhub"], "clawhub")

        print(f"\nProcessing {len(samples['github'])} GitHub repos...")
        github_results = await process_items(client, samples["github"], "github")

    extracted_data = clawhub_results + github_results
    total_items = len(samples["clawhub"]) + len(samples["github"])
    print(f"\n✓ Successfully extracted {len(extracted_data)}/{total_items} items")

    print("\n[Step 3/6] Calculating opportunity scores...")
    extracted_data = add_scores_to_data(
        extracted_data,
        config.SKILLABILITY_WEIGHTS,
        config.OPPORTUNITY_WEIGHTS,
    )

    Path(config.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    ensure_parent_dir(config.EXTRACTED_DATA_PATH)
    with open(config.EXTRACTED_DATA_PATH, "w", encoding="utf-8") as file:
        json.dump(extracted_data, file, indent=2, ensure_ascii=False)
    print(f"✓ Saved extracted data to {config.EXTRACTED_DATA_PATH}")

    print("\n[Step 4/6] Analyzing distributions...")
    cap_dist = analyze_capability_distribution(extracted_data)
    analyze_granularity_distribution(extracted_data)
    skill_dist = analyze_skillability_distribution(extracted_data)
    top_candidates = get_top_candidates(extracted_data, k=20)
    summary_stats = generate_summary_stats(extracted_data)

    ensure_parent_dir(config.TOP_CANDIDATES_PATH)
    with open(config.TOP_CANDIDATES_PATH, "w", encoding="utf-8") as file:
        json.dump(top_candidates, file, indent=2, ensure_ascii=False)
    print(f"✓ Saved top candidates to {config.TOP_CANDIDATES_PATH}")

    print("\n[Step 5/6] Generating visualizations...")
    generate_all_plots(cap_dist, skill_dist, top_candidates, config.FIGURES_DIR)

    print("\n[Step 6/6] Generating HTML report...")
    generate_html_report(
        summary_stats,
        top_candidates,
        config.FIGURES_DIR,
        config.ANALYSIS_REPORT_PATH,
    )

    print("\n" + "=" * 60)
    print("Analysis Complete!")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"  Total items analyzed: {summary_stats['total_items']}")
    print(f"  Clawhub skills: {summary_stats['clawhub_count']}")
    print(f"  GitHub repos: {summary_stats['github_count']}")
    print(f"  Avg Clawhub skillability: {summary_stats['clawhub_avg_skillability']:.2f}")
    print(f"  Avg GitHub skillability: {summary_stats['github_avg_skillability']:.2f}")
    print(f"  High skillability repos (≥4): {summary_stats['github_high_skillability_count']}")
    print(f"\n📁 Output files:")
    print(f"  - Extracted data: {config.EXTRACTED_DATA_PATH}")
    print(f"  - Top candidates: {config.TOP_CANDIDATES_PATH}")
    print(f"  - HTML report: {config.ANALYSIS_REPORT_PATH}")
    print(f"  - Figures: {config.FIGURES_DIR}/")
    print(f"\n🌐 Open the report:")
    print(f"  file://{Path(config.ANALYSIS_REPORT_PATH).absolute()}")


if __name__ == "__main__":
    asyncio.run(main())
