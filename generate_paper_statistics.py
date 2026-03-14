"""Generate comprehensive statistics for the paper."""

import json
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 10

# Load data
print("Loading data...")
data = []
with open('output_large/extracted_data.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            data.append(json.loads(line))

print(f"Total items: {len(data)}")

# Separate by source
clawhub_data = [d for d in data if d['source'] == 'clawhub']
github_data = [d for d in data if d['source'] == 'github']

print(f"Clawhub: {len(clawhub_data)}")
print(f"GitHub: {len(github_data)}")

# Statistics dictionary
stats = {
    'overview': {},
    'capability_distribution': {},
    'granularity_distribution': {},
    'execution_mode_distribution': {},
    'skillability_analysis': {},
    'comparison': {},
    'top_opportunities': []
}

# 1. Overview Statistics
stats['overview'] = {
    'total_items': len(data),
    'clawhub_count': len(clawhub_data),
    'github_count': len(github_data),
    'avg_skillability_overall': np.mean([d['skillability_score'] for d in data]),
    'avg_skillability_clawhub': np.mean([d['skillability_score'] for d in clawhub_data]),
    'avg_skillability_github': np.mean([d['skillability_score'] for d in github_data]),
    'high_skillability_count': len([d for d in data if d['skillability_score'] >= 4]),
    'high_skillability_percentage': len([d for d in data if d['skillability_score'] >= 4]) / len(data) * 100
}

# 2. Capability Distribution
capability_counter = Counter([d['primary_capability'] for d in data])
stats['capability_distribution']['overall'] = dict(capability_counter)
stats['capability_distribution']['clawhub'] = dict(Counter([d['primary_capability'] for d in clawhub_data]))
stats['capability_distribution']['github'] = dict(Counter([d['primary_capability'] for d in github_data]))

# 3. Granularity Distribution
granularity_counter = Counter([d['granularity'] for d in data])
stats['granularity_distribution']['overall'] = dict(granularity_counter)
stats['granularity_distribution']['clawhub'] = dict(Counter([d['granularity'] for d in clawhub_data]))
stats['granularity_distribution']['github'] = dict(Counter([d['granularity'] for d in github_data]))

# 4. Execution Mode Distribution
execution_counter = Counter([d['execution_mode'] for d in data])
stats['execution_mode_distribution']['overall'] = dict(execution_counter)
stats['execution_mode_distribution']['clawhub'] = dict(Counter([d['execution_mode'] for d in clawhub_data]))
stats['execution_mode_distribution']['github'] = dict(Counter([d['execution_mode'] for d in github_data]))

# 5. Skillability Dimension Analysis
dimensions = ['task_clarity', 'interface_clarity', 'composability',
              'automation_value', 'deployment_friction', 'operational_risk']

stats['skillability_analysis']['dimensions'] = {}
for dim in dimensions:
    stats['skillability_analysis']['dimensions'][dim] = {
        'overall_mean': np.mean([d[dim] for d in data]),
        'overall_std': np.std([d[dim] for d in data]),
        'clawhub_mean': np.mean([d[dim] for d in clawhub_data]),
        'github_mean': np.mean([d[dim] for d in github_data]),
        'correlation_with_skillability': np.corrcoef(
            [d[dim] for d in data],
            [d['skillability_score'] for d in data]
        )[0, 1]
    }

# 6. Skillability Score Distribution
skillability_scores = [d['skillability_score'] for d in data]
stats['skillability_analysis']['score_distribution'] = {
    'score_1': len([s for s in skillability_scores if s == 1]),
    'score_2': len([s for s in skillability_scores if s == 2]),
    'score_3': len([s for s in skillability_scores if s == 3]),
    'score_4': len([s for s in skillability_scores if s == 4]),
    'score_5': len([s for s in skillability_scores if s == 5])
}

# 7. Comparison Analysis
stats['comparison']['skillability_gap'] = (
    stats['overview']['avg_skillability_clawhub'] -
    stats['overview']['avg_skillability_github']
)

# Calculate percentage of high-skillability items by source
clawhub_high = len([d for d in clawhub_data if d['skillability_score'] >= 4])
github_high = len([d for d in github_data if d['skillability_score'] >= 4])

stats['comparison']['high_skillability_rate'] = {
    'clawhub': clawhub_high / len(clawhub_data) * 100,
    'github': github_high / len(github_data) * 100
}

# 8. Language Distribution (GitHub only)
github_languages = [d['language'] for d in github_data if d.get('language')]
language_counter = Counter(github_languages)
stats['language_distribution'] = dict(language_counter.most_common(15))

# 9. Stars vs Skillability (GitHub only)
github_with_opportunity = [d for d in github_data if 'opportunity_score' in d]
if github_with_opportunity:
    stars = [d['stars'] for d in github_with_opportunity]
    skillability = [d['skillability_score'] for d in github_with_opportunity]
    opportunity = [d['opportunity_score'] for d in github_with_opportunity]

    stats['github_quality_analysis'] = {
        'stars_skillability_correlation': np.corrcoef(stars, skillability)[0, 1],
        'stars_opportunity_correlation': np.corrcoef(stars, opportunity)[0, 1],
        'avg_stars_high_skillability': np.mean([d['stars'] for d in github_with_opportunity if d['skillability_score'] >= 4]),
        'avg_stars_low_skillability': np.mean([d['stars'] for d in github_with_opportunity if d['skillability_score'] < 4])
    }

# 10. Top Opportunities
with open('output_large/top_candidates.json', 'r', encoding='utf-8') as f:
    top_candidates = json.load(f)

stats['top_opportunities'] = {
    'count': len(top_candidates),
    'top_10': top_candidates[:10],
    'avg_opportunity_score': np.mean([c['opportunity_score'] for c in top_candidates]),
    'capability_breakdown': dict(Counter([c['primary_capability'] for c in top_candidates[:100]]))
}

# Save statistics
output_path = Path('output_large/paper_statistics.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(stats, f, indent=2, ensure_ascii=False)

print(f"\n✅ Statistics saved to {output_path}")

# Print key findings
print("\n" + "="*60)
print("KEY FINDINGS")
print("="*60)
print(f"\n1. Dataset Overview:")
print(f"   - Total analyzed: {stats['overview']['total_items']:,}")
print(f"   - Clawhub skills: {stats['overview']['clawhub_count']:,}")
print(f"   - GitHub repos: {stats['overview']['github_count']:,}")

print(f"\n2. Skillability Scores:")
print(f"   - Overall average: {stats['overview']['avg_skillability_overall']:.2f}")
print(f"   - Clawhub average: {stats['overview']['avg_skillability_clawhub']:.2f}")
print(f"   - GitHub average: {stats['overview']['avg_skillability_github']:.2f}")
print(f"   - High skillability (≥4): {stats['overview']['high_skillability_count']:,} ({stats['overview']['high_skillability_percentage']:.1f}%)")

print(f"\n3. Skillability Gap:")
print(f"   - Clawhub vs GitHub: +{stats['comparison']['skillability_gap']:.2f}")
print(f"   - Clawhub high-skill rate: {stats['comparison']['high_skillability_rate']['clawhub']:.1f}%")
print(f"   - GitHub high-skill rate: {stats['comparison']['high_skillability_rate']['github']:.1f}%")

print(f"\n4. Top Capability Categories:")
for cap, count in sorted(capability_counter.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"   - {cap}: {count:,} ({count/len(data)*100:.1f}%)")

print(f"\n5. Top Programming Languages (GitHub):")
for lang, count in list(language_counter.most_common(5)):
    print(f"   - {lang}: {count:,} ({count/len(github_data)*100:.1f}%)")

print(f"\n6. Dimension Correlations with Skillability:")
for dim in dimensions:
    corr = stats['skillability_analysis']['dimensions'][dim]['correlation_with_skillability']
    print(f"   - {dim}: {corr:.3f}")

print("\n" + "="*60)
