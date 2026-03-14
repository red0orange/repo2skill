#!/usr/bin/env python3
"""
Software2Skill Analysis - Main Pipeline
Analyzes Clawhub skills and GitHub repositories to identify skillification opportunities.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

import config
from data_sampler import prepare_samples
from glm_client import GLMClient
from scorer import add_scores_to_data
from analyzer import (
    analyze_capability_distribution,
    analyze_granularity_distribution,
    analyze_skillability_distribution,
    get_top_candidates,
    generate_summary_stats
)
from visualizer import generate_all_plots
from report_generator import generate_html_report


def main():
    """Main analysis pipeline."""
    print("=" * 60)
    print("Software2Skill Analysis Pipeline")
    print("=" * 60)

    # Step 1: Data Sampling
    print("\n[Step 1/6] Sampling data...")
    samples = prepare_samples(
        config.CLAWHUB_DATA_PATH,
        config.GITHUB_DATA_PATH,
        config.README_DIR,
        config.CLAWHUB_SAMPLE_SIZE,
        config.GITHUB_SAMPLE_SIZE
    )

    # Step 2: LLM Extraction
    print("\n[Step 2/6] Extracting structured data with GLM API...")
    client = GLMClient(
        config.GLM_API_KEY,
        config.GLM_API_URL,
        config.GLM_MODEL,
        config.GLM_TEMPERATURE,
        config.GLM_MAX_RETRIES
    )

    extracted_data = []
    total_items = len(samples['clawhub']) + len(samples['github'])
    current = 0

    # Process Clawhub skills
    print(f"\nProcessing {len(samples['clawhub'])} Clawhub skills...")
    for skill in samples['clawhub']:
        current += 1
        print(f"  [{current}/{total_items}] {skill.get('displayName', 'Unknown')[:50]}...")

        result = client.extract_structured_data(skill, 'clawhub')
        if result:
            # Add metadata
            result['id'] = skill.get('slug', '')
            result['source'] = 'clawhub'
            result['name'] = skill.get('displayName', '')
            result['description'] = skill.get('summary', '')
            result['url'] = f"https://clawhub.ai/skills/{skill.get('slug', '')}"
            result['stars'] = skill.get('stats', {}).get('stars', 0)
            result['language'] = None
            result['archived'] = False
            result['license'] = skill.get('latestVersion', {}).get('license')

            extracted_data.append(result)
        else:
            print(f"    ⚠️  Failed to extract data")

    # Process GitHub repos
    print(f"\nProcessing {len(samples['github'])} GitHub repos...")
    for repo in samples['github']:
        current += 1
        print(f"  [{current}/{total_items}] {repo.get('full_name', 'Unknown')[:50]}...")

        result = client.extract_structured_data(repo, 'github')
        if result:
            # Add metadata
            result['id'] = repo.get('full_name', '')
            result['source'] = 'github'
            result['name'] = repo.get('full_name', '')
            result['description'] = repo.get('description', '')
            result['url'] = repo.get('html_url', '')
            result['stars'] = repo.get('stargazers_count', 0)
            result['language'] = repo.get('language', '')
            result['archived'] = repo.get('archived', False)
            result['license'] = repo.get('license', '')

            extracted_data.append(result)
        else:
            print(f"    ⚠️  Failed to extract data")

    print(f"\n✓ Successfully extracted {len(extracted_data)}/{total_items} items")

    # Step 3: Calculate Scores
    print("\n[Step 3/6] Calculating opportunity scores...")
    extracted_data = add_scores_to_data(
        extracted_data,
        config.SKILLABILITY_WEIGHTS,
        config.OPPORTUNITY_WEIGHTS
    )

    # Save extracted data
    Path(config.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    with open(config.EXTRACTED_DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved extracted data to {config.EXTRACTED_DATA_PATH}")

    # Step 4: Analysis
    print("\n[Step 4/6] Analyzing distributions...")
    cap_dist = analyze_capability_distribution(extracted_data)
    gran_dist = analyze_granularity_distribution(extracted_data)
    skill_dist = analyze_skillability_distribution(extracted_data)
    top_candidates = get_top_candidates(extracted_data, k=20)
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
    main()
