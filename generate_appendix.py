"""Generate detailed appendix with top candidates."""

import json
from pathlib import Path

# Load top candidates
with open('output_large/top_candidates.json', 'r', encoding='utf-8') as f:
    candidates = json.load(f)

# Generate appendix
output = []
output.append("# Appendix: Top 100 High-Opportunity Repositories for Agent Skill Transformation\n")
output.append("This appendix provides detailed information about the top 100 GitHub repositories identified as having the highest potential for transformation into agent skills.\n")
output.append(f"\n**Selection Criteria**: Opportunity Score ≥ {candidates[99]['opportunity_score']:.3f}\n")
output.append(f"**Total Candidates**: {len(candidates)} repositories\n")
output.append("\n---\n")

# Generate table
output.append("\n## Top 100 Repositories\n")
output.append("\n| Rank | Repository | Stars | Language | Skillability | Opportunity | Category | Rationale (Excerpt) |")
output.append("\n|------|------------|-------|----------|--------------|-------------|----------|---------------------|")

for i, repo in enumerate(candidates[:100], 1):
    name = repo['name']
    stars = f"{repo['stars']:,}"
    lang = repo.get('language', 'N/A')[:15]
    skill_score = repo['skillability_score']
    opp_score = f"{repo['opportunity_score']:.3f}"
    category = repo['primary_capability'].replace('_', ' ').title()[:20]
    rationale = repo['skillability_rationale'][:80] + "..."

    output.append(f"\n| {i} | [{name}]({repo['url']}) | {stars} | {lang} | {skill_score}/5 | {opp_score} | {category} | {rationale} |")

# Detailed descriptions for top 20
output.append("\n\n---\n")
output.append("\n## Detailed Analysis: Top 20 Repositories\n")

for i, repo in enumerate(candidates[:20], 1):
    output.append(f"\n### {i}. {repo['name']}\n")
    output.append(f"\n**URL**: {repo['url']}")
    output.append(f"\n**Stars**: {repo['stars']:,}")
    output.append(f"\n**Language**: {repo.get('language', 'N/A')}")
    output.append(f"\n**Description**: {repo.get('description', 'N/A')}")
    output.append(f"\n\n**Skillability Metrics**:")
    output.append(f"\n- Overall Score: {repo['skillability_score']}/5")
    output.append(f"\n- Task Clarity: {repo['task_clarity']}/5")
    output.append(f"\n- Interface Clarity: {repo['interface_clarity']}/5")
    output.append(f"\n- Composability: {repo['composability']}/5")
    output.append(f"\n- Automation Value: {repo['automation_value']}/5")
    output.append(f"\n- Deployment Friction: {repo['deployment_friction']}/5")
    output.append(f"\n- Operational Risk: {repo['operational_risk']}/5")
    output.append(f"\n\n**Classification**:")
    output.append(f"\n- Primary Capability: {repo['primary_capability'].replace('_', ' ').title()}")
    output.append(f"\n- Granularity: {repo['granularity'].replace('_', ' ').title()}")
    output.append(f"\n- Execution Mode: {repo['execution_mode'].replace('_', ' ').title()}")
    output.append(f"\n\n**Opportunity Score**: {repo['opportunity_score']:.3f}")
    output.append(f"\n\n**Skillability Rationale**:")
    output.append(f"\n{repo['skillability_rationale']}")
    output.append("\n\n---")

# Category breakdown
output.append("\n\n## Category Distribution (Top 100)\n")
from collections import Counter
category_counts = Counter([r['primary_capability'] for r in candidates[:100]])
output.append("\n| Category | Count | Percentage |")
output.append("\n|----------|-------|------------|")
for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
    cat_name = cat.replace('_', ' ').title()
    pct = count / 100 * 100
    output.append(f"\n| {cat_name} | {count} | {pct:.1f}% |")

# Language breakdown
output.append("\n\n## Language Distribution (Top 100)\n")
lang_counts = Counter([r.get('language', 'Unknown') for r in candidates[:100]])
output.append("\n| Language | Count | Percentage |")
output.append("\n|----------|-------|------------|")
for lang, count in sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)[:15]:
    pct = count / 100 * 100
    output.append(f"\n| {lang} | {count} | {pct:.1f}% |")

# Save appendix
appendix_path = Path('paper/APPENDIX_TOP_CANDIDATES.md')
appendix_path.parent.mkdir(exist_ok=True)
with open(appendix_path, 'w', encoding='utf-8') as f:
    f.write(''.join(output))

print(f"✅ Appendix generated: {appendix_path}")
print(f"   - Top 100 repositories listed")
print(f"   - Top 20 with detailed analysis")
print(f"   - Category and language breakdowns included")
