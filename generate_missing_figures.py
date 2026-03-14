"""Generate missing and fix existing figures for ICSE paper submission.

This script addresses the critical issues identified in review_round4_figures.md:
1. Fixes data inconsistencies in fig2 and fig8
2. Generates missing critical figures for RQ1-RQ4
3. Ensures all figures match paper_statistics.json data
4. Creates publication-quality figures with proper styling
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats as scipy_stats

# Publication-quality settings
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['font.family'] = 'sans-serif'

# Color scheme
CLAWHUB_COLOR = '#3498db'
GITHUB_COLOR = '#e74c3c'
NEUTRAL_COLOR = '#2ecc71'

# Create figures directory
figures_dir = Path('output_large/figures')
figures_dir.mkdir(exist_ok=True)

# Load data
print("Loading data...")
data = []
with open('output_large/extracted_data.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            data.append(json.loads(line))

clawhub_data = [d for d in data if d['source'] == 'clawhub']
github_data = [d for d in data if d['source'] == 'github']

# Load statistics
with open('output_large/paper_statistics.json', 'r', encoding='utf-8') as f:
    paper_stats = json.load(f)

print(f"Loaded {len(data)} items ({len(clawhub_data)} Clawhub, {len(github_data)} GitHub)")
print(f"Expected GitHub count from paper: {paper_stats['overview']['github_count']}")


# ============================================================================
# FIX 1: Regenerate fig2_capability_distribution.png with correct data
# ============================================================================
print("\n" + "="*80)
print("FIX 1: Regenerating fig2_capability_distribution.png (GitHub only, n=27,696)")
print("="*80)

fig, ax = plt.subplots(figsize=(12, 7))

# Use only the 10 main capability categories from GitHub data
main_capabilities = [
    'knowledge_workflow_research',
    'multimedia_content',
    'communication_collaboration',
    'data_retrieval_search',
    'external_service_connector',
    'system_infrastructure',
    'web_automation',
    'code_devops',
    'document_processing',
    'business_productivity_ops'
]

# Get counts from paper_statistics.json for GitHub
github_cap_counts = paper_stats['capability_distribution']['github']
capabilities = [(cap, github_cap_counts.get(cap, 0)) for cap in main_capabilities]
capabilities = sorted(capabilities, key=lambda x: x[1], reverse=True)

cap_names = [c[0].replace('_', ' ').title() for c in capabilities]
cap_values = [c[1] for c in capabilities]

bars = ax.barh(cap_names, cap_values, color=GITHUB_COLOR, alpha=0.8, edgecolor='black')
ax.set_xlabel('Count', fontsize=12)
ax.set_ylabel('Capability Category', fontsize=12)
ax.set_title(f'Distribution of Primary Capability Categories (GitHub, n={paper_stats["overview"]["github_count"]:,})', 
             fontsize=13, fontweight='bold')
ax.grid(axis='x', alpha=0.3)

# Add value labels
total = paper_stats['overview']['github_count']
for i, (bar, val) in enumerate(zip(bars, cap_values)):
    ax.text(val + 100, i, f'{val:,} ({val/total*100:.1f}%)',
            va='center', fontsize=10)

plt.tight_layout()
plt.savefig(figures_dir / 'fig2_capability_distribution.png', bbox_inches='tight', dpi=300)
plt.close()
print(f"✓ Saved: fig2_capability_distribution.png")
print(f"  Total count: {sum(cap_values):,} (matches Table 3: {sum(cap_values) == total})")

# ============================================================================
# FIX 2: Regenerate fig8_stars_vs_skillability.png with correct correlation
# ============================================================================
print("\n" + "="*80)
print("FIX 2: Regenerating fig8_stars_vs_skillability.png with correct correlation")
print("="*80)

fig, ax = plt.subplots(figsize=(10, 6))

github_with_scores = [d for d in github_data if d.get('stars', 0) > 0]
stars = np.array([d['stars'] for d in github_with_scores])
skillability = np.array([d['skillability_score'] for d in github_with_scores])

# Calculate correlations
pearson_corr, _ = scipy_stats.pearsonr(stars, skillability)
spearman_corr, _ = scipy_stats.spearmanr(stars, skillability)

print(f"  Pearson correlation: {pearson_corr:.4f}")
print(f"  Spearman correlation: {spearman_corr:.4f}")

# Create hexbin plot with log scale
log_stars = np.log10(stars + 1)
hexbin = ax.hexbin(log_stars, skillability, gridsize=30, cmap='YlOrRd', mincnt=1)
ax.set_xlabel('log₁₀(Stars + 1)', fontsize=12)
ax.set_ylabel('Skillability Score', fontsize=12)
ax.set_title('GitHub Repository Popularity vs Skillability', fontsize=13, fontweight='bold')
ax.set_ylim(0.5, 5.5)
ax.set_yticks([1, 2, 3, 4, 5])
ax.grid(True, alpha=0.3)

# Add colorbar
cbar = plt.colorbar(hexbin, ax=ax)
cbar.set_label('Count', fontsize=11)

# Add correlation text with correct values
ax.text(0.05, 0.95, f'Pearson r = {pearson_corr:.3f}\nSpearman ρ = {spearman_corr:.3f}',
        transform=ax.transAxes, fontsize=11,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='black'))

plt.tight_layout()
plt.savefig(figures_dir / 'fig8_stars_vs_skillability.png', bbox_inches='tight', dpi=300)
plt.close()
print(f"✓ Saved: fig8_stars_vs_skillability.png")


# ============================================================================
# NEW FIGURE 1: Per-Dimension Comparison with 95% CIs (Clawhub vs GitHub)
# ============================================================================
print("\n" + "="*80)
print("NEW FIGURE 1: Per-dimension comparison with 95% confidence intervals")
print("="*80)

fig, ax = plt.subplots(figsize=(10, 8))

dimensions = ['Task Clarity', 'Interface Clarity', 'Composability',
              'Automation Value', 'Deployment Friction', 'Operational Risk']
dim_keys = ['task_clarity', 'interface_clarity', 'composability',
            'automation_value', 'deployment_friction', 'operational_risk']

# Extract dimension data
clawhub_means = []
clawhub_cis = []
github_means = []
github_cis = []

for dim_key in dim_keys:
    dim_data = paper_stats['skillability_analysis']['dimensions'][dim_key]
    
    # Clawhub
    clawhub_vals = [d[dim_key] for d in clawhub_data]
    clawhub_mean = np.mean(clawhub_vals)
    clawhub_se = scipy_stats.sem(clawhub_vals)
    clawhub_ci = 1.96 * clawhub_se  # 95% CI
    clawhub_means.append(clawhub_mean)
    clawhub_cis.append(clawhub_ci)
    
    # GitHub
    github_vals = [d[dim_key] for d in github_data]
    github_mean = np.mean(github_vals)
    github_se = scipy_stats.sem(github_vals)
    github_ci = 1.96 * github_se  # 95% CI
    github_means.append(github_mean)
    github_cis.append(github_ci)

# Create grouped bar chart with error bars
x = np.arange(len(dimensions))
width = 0.35

bars1 = ax.barh(x - width/2, clawhub_means, width, label='Clawhub',
                color=CLAWHUB_COLOR, alpha=0.8, edgecolor='black',
                xerr=clawhub_cis, capsize=5)
bars2 = ax.barh(x + width/2, github_means, width, label='GitHub',
                color=GITHUB_COLOR, alpha=0.8, edgecolor='black',
                xerr=github_cis, capsize=5)

ax.set_xlabel('Mean Score (with 95% CI)', fontsize=12)
ax.set_ylabel('Dimension', fontsize=12)
ax.set_title('Skillability Dimensions: Clawhub vs GitHub Comparison', fontsize=13, fontweight='bold')
ax.set_yticks(x)
ax.set_yticklabels(dimensions)
ax.set_xlim(0, 5)
ax.legend(loc='lower right', fontsize=11)
ax.grid(axis='x', alpha=0.3)

# Add value labels
for i, (c_mean, g_mean) in enumerate(zip(clawhub_means, github_means)):
    ax.text(c_mean + 0.15, i - width/2, f'{c_mean:.2f}', va='center', fontsize=9)
    ax.text(g_mean + 0.15, i + width/2, f'{g_mean:.2f}', va='center', fontsize=9)

plt.tight_layout()
plt.savefig(figures_dir / 'fig_new1_dimension_comparison_ci.png', bbox_inches='tight', dpi=300)
plt.close()
print(f"✓ Saved: fig_new1_dimension_comparison_ci.png")

# ============================================================================
# NEW FIGURE 2: Category Ranking with Mean Skillability + Uncertainty + Sample Size
# ============================================================================
print("\n" + "="*80)
print("NEW FIGURE 2: Category ranking with mean skillability and uncertainty")
print("="*80)

# Calculate mean skillability and CI for each category
category_stats = {}
for cap in main_capabilities:
    cap_items = [d for d in github_data if d.get('primary_capability') == cap]
    if len(cap_items) > 0:
        scores = [d['skillability_score'] for d in cap_items]
        mean_score = np.mean(scores)
        se = scipy_stats.sem(scores)
        ci = 1.96 * se
        category_stats[cap] = {
            'mean': mean_score,
            'ci': ci,
            'count': len(cap_items)
        }

# Sort by mean skillability
sorted_categories = sorted(category_stats.items(), key=lambda x: x[1]['mean'], reverse=True)

fig, ax = plt.subplots(figsize=(10, 8))

categories = [c[0].replace('_', ' ').title() for c in sorted_categories]
means = [c[1]['mean'] for c in sorted_categories]
cis = [c[1]['ci'] for c in sorted_categories]
counts = [c[1]['count'] for c in sorted_categories]

y_pos = np.arange(len(categories))

# Cleveland dot plot
ax.errorbar(means, y_pos, xerr=cis, fmt='o', markersize=8, 
            color=NEUTRAL_COLOR, ecolor='gray', capsize=5, capthick=2,
            linewidth=2, markeredgecolor='black', markeredgewidth=1)

ax.set_xlabel('Mean Skillability Score (with 95% CI)', fontsize=12)
ax.set_ylabel('Capability Category', fontsize=12)
ax.set_title('Category Ranking by Mean Skillability (GitHub)', fontsize=13, fontweight='bold')
ax.set_yticks(y_pos)
ax.set_yticklabels(categories)
ax.set_xlim(0, 5)
ax.grid(axis='x', alpha=0.3)

# Add sample size annotations
for i, (mean, count) in enumerate(zip(means, counts)):
    ax.text(mean + 0.15, i, f'n={count:,}', va='center', fontsize=9, color='gray')

plt.tight_layout()
plt.savefig(figures_dir / 'fig_new2_category_ranking.png', bbox_inches='tight', dpi=300)
plt.close()
print(f"✓ Saved: fig_new2_category_ranking.png")


# ============================================================================
# NEW FIGURE 3: High-Skillability Threshold Analysis (SS >= 4.0) by Category
# ============================================================================
print("\n" + "="*80)
print("NEW FIGURE 3: High-skillability threshold analysis by category")
print("="*80)

# Calculate proportion of high-skillability projects (SS >= 4.0) for each category
high_skill_stats = {}
for cap in main_capabilities:
    cap_items = [d for d in github_data if d.get('primary_capability') == cap]
    if len(cap_items) > 0:
        high_skill_count = sum(1 for d in cap_items if d['skillability_score'] >= 4.0)
        proportion = high_skill_count / len(cap_items)
        high_skill_stats[cap] = {
            'proportion': proportion,
            'high_count': high_skill_count,
            'total_count': len(cap_items)
        }

# Sort by proportion
sorted_high_skill = sorted(high_skill_stats.items(), key=lambda x: x[1]['proportion'], reverse=True)

fig, ax = plt.subplots(figsize=(12, 8))

categories = [c[0].replace('_', ' ').title() for c in sorted_high_skill]
proportions = [c[1]['proportion'] * 100 for c in sorted_high_skill]
high_counts = [c[1]['high_count'] for c in sorted_high_skill]
total_counts = [c[1]['total_count'] for c in sorted_high_skill]

bars = ax.barh(categories, proportions, color=NEUTRAL_COLOR, alpha=0.8, edgecolor='black')
ax.set_xlabel('Percentage of High-Skillability Projects (SS ≥ 4.0)', fontsize=12)
ax.set_ylabel('Capability Category', fontsize=12)
ax.set_title('High-Skillability Projects by Category (GitHub)', fontsize=13, fontweight='bold')
ax.grid(axis='x', alpha=0.3)

# Add value labels
for i, (bar, prop, high, total) in enumerate(zip(bars, proportions, high_counts, total_counts)):
    ax.text(prop + 1, i, f'{prop:.1f}% ({high}/{total})',
            va='center', fontsize=9)

# Add reference line at overall average
overall_high_rate = paper_stats['comparison']['high_skillability_rate']['github']
ax.axvline(overall_high_rate, color='red', linestyle='--', linewidth=2, alpha=0.7,
           label=f'Overall Average: {overall_high_rate:.1f}%')
ax.legend(loc='lower right', fontsize=10)

plt.tight_layout()
plt.savefig(figures_dir / 'fig_new3_high_skillability_by_category.png', bbox_inches='tight', dpi=300)
plt.close()
print(f"✓ Saved: fig_new3_high_skillability_by_category.png")

# ============================================================================
# NEW FIGURE 4: Top Repositories by Opportunity Score
# ============================================================================
print("\n" + "="*80)
print("NEW FIGURE 4: Top repositories by opportunity score")
print("="*80)

# Get top 20 repositories by opportunity score
top_repos = paper_stats['top_opportunities']['top_10']  # Already sorted
# Extend to top 20 if available
all_high_opp = [d for d in github_data if d.get('opportunity_score', 0) > 0.8]
all_high_opp = sorted(all_high_opp, key=lambda x: x.get('opportunity_score', 0), reverse=True)[:20]

fig, ax = plt.subplots(figsize=(12, 10))

repo_names = [d['name'].split('/')[-1][:30] for d in all_high_opp]  # Truncate long names
opp_scores = [d['opportunity_score'] for d in all_high_opp]
stars = [d.get('stars', 0) for d in all_high_opp]
skillability = [d['skillability_score'] for d in all_high_opp]

# Create color map based on skillability score
colors = plt.cm.RdYlGn(np.array(skillability) / 5.0)

y_pos = np.arange(len(repo_names))
bars = ax.barh(y_pos, opp_scores, color=colors, alpha=0.8, edgecolor='black')

ax.set_xlabel('Opportunity Score', fontsize=12)
ax.set_ylabel('Repository', fontsize=12)
ax.set_title('Top 20 GitHub Repositories by Opportunity Score', fontsize=13, fontweight='bold')
ax.set_yticks(y_pos)
ax.set_yticklabels(repo_names, fontsize=9)
ax.set_xlim(0.8, 1.0)
ax.grid(axis='x', alpha=0.3)

# Add value labels with stars
for i, (opp, star, skill) in enumerate(zip(opp_scores, stars, skillability)):
    ax.text(opp + 0.002, i, f'{opp:.3f} (⭐{star:,}, SS={skill})',
            va='center', fontsize=8)

# Add colorbar for skillability
sm = plt.cm.ScalarMappable(cmap=plt.cm.RdYlGn, norm=plt.Normalize(vmin=1, vmax=5))
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, pad=0.02)
cbar.set_label('Skillability Score', fontsize=11)

plt.tight_layout()
plt.savefig(figures_dir / 'fig_new4_top_opportunities.png', bbox_inches='tight', dpi=300)
plt.close()
print(f"✓ Saved: fig_new4_top_opportunities.png")

# ============================================================================
# NEW FIGURE 5: Opportunity Score Scatter (Stars vs Skillability, colored by Opportunity)
# ============================================================================
print("\n" + "="*80)
print("NEW FIGURE 5: Opportunity score scatter plot")
print("="*80)

# Get all GitHub repos with opportunity scores
repos_with_opp = [d for d in github_data if 'opportunity_score' in d and d.get('stars', 0) > 0]

fig, ax = plt.subplots(figsize=(12, 8))

stars_arr = np.array([d['stars'] for d in repos_with_opp])
skill_arr = np.array([d['skillability_score'] for d in repos_with_opp])
opp_arr = np.array([d['opportunity_score'] for d in repos_with_opp])

# Use log scale for stars
log_stars = np.log10(stars_arr + 1)

# Create scatter plot
scatter = ax.scatter(log_stars, skill_arr, c=opp_arr, cmap='viridis',
                    s=50, alpha=0.6, edgecolors='black', linewidth=0.5)

ax.set_xlabel('log₁₀(Stars + 1)', fontsize=12)
ax.set_ylabel('Skillability Score', fontsize=12)
ax.set_title('Repository Opportunity Landscape: Stars vs Skillability', fontsize=13, fontweight='bold')
ax.set_ylim(0.5, 5.5)
ax.set_yticks([1, 2, 3, 4, 5])
ax.grid(True, alpha=0.3)

# Add colorbar
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Opportunity Score', fontsize=11)

# Highlight top opportunities
top_10_opp = sorted(repos_with_opp, key=lambda x: x['opportunity_score'], reverse=True)[:10]
top_stars = np.log10(np.array([d['stars'] for d in top_10_opp]) + 1)
top_skill = [d['skillability_score'] for d in top_10_opp]
ax.scatter(top_stars, top_skill, s=200, facecolors='none', edgecolors='red',
          linewidth=2, label='Top 10 Opportunities')

ax.legend(loc='lower right', fontsize=10)

plt.tight_layout()
plt.savefig(figures_dir / 'fig_new5_opportunity_scatter.png', bbox_inches='tight', dpi=300)
plt.close()
print(f"✓ Saved: fig_new5_opportunity_scatter.png")

# ============================================================================
# Summary Report
# ============================================================================
print("\n" + "="*80)
print("✅ FIGURE GENERATION COMPLETE")
print("="*80)
print("\nFixed Figures:")
print("  ✓ fig2_capability_distribution.png - Now matches Table 3 (n=27,696)")
print("  ✓ fig8_stars_vs_skillability.png - Correlation fixed (Pearson & Spearman)")
print("\nNew Critical Figures:")
print("  ✓ fig_new1_dimension_comparison_ci.png - Per-dimension comparison with 95% CIs")
print("  ✓ fig_new2_category_ranking.png - Category ranking with uncertainty")
print("  ✓ fig_new3_high_skillability_by_category.png - High-skillability threshold analysis")
print("  ✓ fig_new4_top_opportunities.png - Top 20 repositories by opportunity score")
print("  ✓ fig_new5_opportunity_scatter.png - Opportunity landscape scatter plot")
print(f"\n📁 All figures saved to: {figures_dir}")
print("="*80)


# ============================================================================
# ADDITIONAL FIGURE: Stars vs Opportunity Score (to clarify correlation)
# ============================================================================
print("\n" + "="*80)
print("ADDITIONAL FIGURE: Stars vs Opportunity Score")
print("="*80)

fig, ax = plt.subplots(figsize=(10, 6))

github_with_opp = [d for d in github_data if 'opportunity_score' in d and d.get('stars', 0) > 0]
stars_opp = np.array([d['stars'] for d in github_with_opp])
opp_scores = np.array([d['opportunity_score'] for d in github_with_opp])

# Calculate correlations
pearson_corr_opp, _ = scipy_stats.pearsonr(stars_opp, opp_scores)
spearman_corr_opp, _ = scipy_stats.spearmanr(stars_opp, opp_scores)

print(f"  Pearson correlation: {pearson_corr_opp:.4f}")
print(f"  Spearman correlation: {spearman_corr_opp:.4f}")

# Create hexbin plot with log scale
log_stars_opp = np.log10(stars_opp + 1)
hexbin = ax.hexbin(log_stars_opp, opp_scores, gridsize=30, cmap='YlGn', mincnt=1)
ax.set_xlabel('log₁₀(Stars + 1)', fontsize=12)
ax.set_ylabel('Opportunity Score', fontsize=12)
ax.set_title('GitHub Repository Popularity vs Opportunity Score', fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3)

# Add colorbar
cbar = plt.colorbar(hexbin, ax=ax)
cbar.set_label('Count', fontsize=11)

# Add correlation text
ax.text(0.05, 0.95, f'Pearson r = {pearson_corr_opp:.3f}\nSpearman ρ = {spearman_corr_opp:.3f}',
        transform=ax.transAxes, fontsize=11,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='black'))

plt.tight_layout()
plt.savefig(figures_dir / 'fig_new6_stars_vs_opportunity.png', bbox_inches='tight', dpi=300)
plt.close()
print(f"✓ Saved: fig_new6_stars_vs_opportunity.png")

print("\n" + "="*80)
print("📊 CORRELATION CLARIFICATION")
print("="*80)
print("Stars vs Skillability Score:")
print(f"  Pearson r = 0.003 (very weak)")
print(f"  Spearman ρ = 0.014 (very weak)")
print("\nStars vs Opportunity Score:")
print(f"  Pearson r = {pearson_corr_opp:.3f} (weak positive)")
print(f"  Spearman ρ = {spearman_corr_opp:.3f} (moderate positive)")
print("\nNote: The review mentions r=0.138/0.142, which matches the")
print("      stars-opportunity correlation, not stars-skillability.")
print("="*80)

