"""Generate all figures for the paper."""

import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import Counter

# Set style
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10

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
    stats = json.load(f)

print(f"Loaded {len(data)} items")

# Figure 1: Skillability Score Distribution Comparison
print("\nGenerating Figure 1: Skillability Distribution...")
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# Clawhub
clawhub_scores = [d['skillability_score'] for d in clawhub_data]
axes[0].hist(clawhub_scores, bins=[0.5, 1.5, 2.5, 3.5, 4.5, 5.5],
             color='#3498db', alpha=0.7, edgecolor='black')
axes[0].set_xlabel('Skillability Score')
axes[0].set_ylabel('Count')
axes[0].set_title(f'Clawhub Skills (n={len(clawhub_data):,}, μ={np.mean(clawhub_scores):.2f})')
axes[0].set_xticks([1, 2, 3, 4, 5])
axes[0].grid(axis='y', alpha=0.3)

# GitHub
github_scores = [d['skillability_score'] for d in github_data]
axes[1].hist(github_scores, bins=[0.5, 1.5, 2.5, 3.5, 4.5, 5.5],
             color='#e74c3c', alpha=0.7, edgecolor='black')
axes[1].set_xlabel('Skillability Score')
axes[1].set_ylabel('Count')
axes[1].set_title(f'GitHub Repos (n={len(github_data):,}, μ={np.mean(github_scores):.2f})')
axes[1].set_xticks([1, 2, 3, 4, 5])
axes[1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(figures_dir / 'fig1_skillability_distribution.png', bbox_inches='tight')
plt.close()
print(f"  ✓ Saved: fig1_skillability_distribution.png")

# Figure 2: Capability Category Distribution
print("\nGenerating Figure 2: Capability Distribution...")
fig, ax = plt.subplots(figsize=(12, 7))

# Only use the 10 main capability categories
main_capabilities = [
    'code_devops',
    'data_retrieval_search',
    'document_processing',
    'web_automation',
    'communication_collaboration',
    'knowledge_workflow_research',
    'business_productivity_ops',
    'multimedia_content',
    'system_infrastructure',
    'external_service_connector'
]

# Count only main categories
capability_counts = {}
for item in data:
    cap = item.get('primary_capability', 'unknown')
    if cap in main_capabilities:
        capability_counts[cap] = capability_counts.get(cap, 0) + 1

capabilities = sorted(capability_counts.items(), key=lambda x: x[1], reverse=True)
cap_names = [c[0].replace('_', ' ').title() for c in capabilities]
cap_values = [c[1] for c in capabilities]

bars = ax.barh(cap_names, cap_values, color='#2ecc71', alpha=0.8, edgecolor='black')
ax.set_xlabel('Count', fontsize=12)
ax.set_ylabel('Capability Category', fontsize=12)
ax.set_title('Distribution of Primary Capability Categories', fontsize=14, fontweight='bold')
ax.grid(axis='x', alpha=0.3)

# Add value labels
for i, (bar, val) in enumerate(zip(bars, cap_values)):
    ax.text(val + 100, i, f'{val:,} ({val/len(data)*100:.1f}%)',
            va='center', fontsize=10)

plt.tight_layout()
plt.savefig(figures_dir / 'fig2_capability_distribution.png', bbox_inches='tight', dpi=300)
plt.close()
print(f"  ✓ Saved: fig2_capability_distribution.png")

# Figure 3: Dimension Radar Chart Comparison
print("\nGenerating Figure 3: Dimension Comparison...")
dimensions = ['Task\nClarity', 'Interface\nClarity', 'Composability',
              'Automation\nValue', 'Deployment\nFriction', 'Operational\nRisk']
dim_keys = ['task_clarity', 'interface_clarity', 'composability',
            'automation_value', 'deployment_friction', 'operational_risk']

clawhub_means = [stats['skillability_analysis']['dimensions'][k]['clawhub_mean'] for k in dim_keys]
github_means = [stats['skillability_analysis']['dimensions'][k]['github_mean'] for k in dim_keys]

# Close the plot
clawhub_means += clawhub_means[:1]
github_means += github_means[:1]

angles = np.linspace(0, 2 * np.pi, len(dimensions), endpoint=False).tolist()
angles += angles[:1]

fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
ax.plot(angles, clawhub_means, 'o-', linewidth=2, label='Clawhub', color='#3498db')
ax.fill(angles, clawhub_means, alpha=0.25, color='#3498db')
ax.plot(angles, github_means, 'o-', linewidth=2, label='GitHub', color='#e74c3c')
ax.fill(angles, github_means, alpha=0.25, color='#e74c3c')

ax.set_xticks(angles[:-1])
ax.set_xticklabels(dimensions, size=10)
ax.set_ylim(0, 5)
ax.set_yticks([1, 2, 3, 4, 5])
ax.set_yticklabels(['1', '2', '3', '4', '5'])
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
ax.set_title('Skillability Dimensions: Clawhub vs GitHub', pad=20, fontsize=13)
ax.grid(True)

plt.tight_layout()
plt.savefig(figures_dir / 'fig3_dimension_radar.png', bbox_inches='tight')
plt.close()
print(f"  ✓ Saved: fig3_dimension_radar.png")

# Figure 4: Language Distribution (Top 10)
print("\nGenerating Figure 4: Language Distribution...")
fig, ax = plt.subplots(figsize=(10, 6))

lang_dist = stats['language_distribution']
top_langs = list(lang_dist.items())[:10]
lang_names = [l[0] for l in top_langs]
lang_counts = [l[1] for l in top_langs]

bars = ax.barh(lang_names[::-1], lang_counts[::-1], color='#9b59b6', alpha=0.8, edgecolor='black')
ax.set_xlabel('Count')
ax.set_title('Top 10 Programming Languages in GitHub Repos')
ax.grid(axis='x', alpha=0.3)

# Add percentage labels
for i, (bar, val) in enumerate(zip(bars, lang_counts[::-1])):
    ax.text(val + 50, i, f'{val:,} ({val/len(github_data)*100:.1f}%)',
            va='center', fontsize=9)

plt.tight_layout()
plt.savefig(figures_dir / 'fig4_language_distribution.png', bbox_inches='tight')
plt.close()
print(f"  ✓ Saved: fig4_language_distribution.png")

# Figure 5: Granularity Distribution
print("\nGenerating Figure 5: Granularity Distribution...")
fig, ax = plt.subplots(figsize=(10, 6))

# Only use the 4 main granularity types
main_granularities = ['primitive_tool', 'service_wrapper', 'workflow_skill', 'platform_adapter']

# Count only main granularities
granularity_counts = {}
for item in data:
    gran = item.get('granularity', 'unknown')
    if gran in main_granularities:
        granularity_counts[gran] = granularity_counts.get(gran, 0) + 1

gran_items = sorted(granularity_counts.items(), key=lambda x: x[1], reverse=True)
gran_names = [g[0].replace('_', ' ').title() for g in gran_items]
gran_counts = [g[1] for g in gran_items]

bars = ax.bar(gran_names, gran_counts, color='#f39c12', alpha=0.8, edgecolor='black', width=0.6)
ax.set_ylabel('Count', fontsize=12)
ax.set_xlabel('Granularity Type', fontsize=12)
ax.set_title('Distribution of Granularity Types', fontsize=14, fontweight='bold')
ax.grid(axis='y', alpha=0.3)

# Add value labels
for bar, val in zip(bars, gran_counts):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 200,
            f'{val:,}\n({val/len(data)*100:.1f}%)',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(figures_dir / 'fig5_granularity_distribution.png', bbox_inches='tight', dpi=300)
plt.close()
print(f"  ✓ Saved: fig5_granularity_distribution.png")

# Figure 6: Execution Mode Distribution
print("\nGenerating Figure 6: Execution Mode Distribution...")
fig, ax = plt.subplots(figsize=(12, 6))

# Only use the 5 main execution modes
main_execution_modes = ['local_deterministic', 'remote_api_mediated', 'browser_mediated', 
                        'human_in_the_loop', 'hybrid']

# Count only main execution modes
execution_counts = {}
for item in data:
    exec_mode = item.get('execution_mode', 'unknown')
    if exec_mode in main_execution_modes:
        execution_counts[exec_mode] = execution_counts.get(exec_mode, 0) + 1

exec_items = sorted(execution_counts.items(), key=lambda x: x[1], reverse=True)
exec_names = [e[0].replace('_', ' ').title() for e in exec_items]
exec_counts = [e[1] for e in exec_items]

bars = ax.bar(exec_names, exec_counts, color='#1abc9c', alpha=0.8, edgecolor='black', width=0.6)
ax.set_ylabel('Count', fontsize=12)
ax.set_xlabel('Execution Mode', fontsize=12)
ax.set_title('Distribution of Execution Modes', fontsize=14, fontweight='bold')
ax.grid(axis='y', alpha=0.3)

# Add value labels
for bar, val in zip(bars, exec_counts):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 200,
            f'{val:,}\n({val/len(data)*100:.1f}%)',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.xticks(rotation=20, ha='right')
plt.tight_layout()
plt.savefig(figures_dir / 'fig6_execution_mode_distribution.png', bbox_inches='tight', dpi=300)
plt.close()
print(f"  ✓ Saved: fig6_execution_mode_distribution.png")

# Figure 7: Correlation Heatmap
print("\nGenerating Figure 7: Dimension Correlations...")
fig, ax = plt.subplots(figsize=(10, 8))

# Calculate correlation matrix
dim_keys_full = ['task_clarity', 'interface_clarity', 'composability',
                 'automation_value', 'deployment_friction', 'operational_risk',
                 'skillability_score']
dim_labels = ['Task\nClarity', 'Interface\nClarity', 'Composability',
              'Automation\nValue', 'Deployment\nFriction', 'Operational\nRisk',
              'Skillability\nScore']

corr_matrix = np.zeros((len(dim_keys_full), len(dim_keys_full)))
for i, dim1 in enumerate(dim_keys_full):
    for j, dim2 in enumerate(dim_keys_full):
        values1 = [d[dim1] for d in data]
        values2 = [d[dim2] for d in data]
        corr_matrix[i, j] = np.corrcoef(values1, values2)[0, 1]

sns.heatmap(corr_matrix, annot=True, fmt='.3f', cmap='RdYlGn', center=0,
            xticklabels=dim_labels, yticklabels=dim_labels,
            cbar_kws={'label': 'Correlation'}, ax=ax, vmin=-1, vmax=1)
ax.set_title('Correlation Matrix of Skillability Dimensions', pad=15)

plt.tight_layout()
plt.savefig(figures_dir / 'fig7_correlation_heatmap.png', bbox_inches='tight')
plt.close()
print(f"  ✓ Saved: fig7_correlation_heatmap.png")

# Figure 8: Stars vs Skillability (GitHub)
print("\nGenerating Figure 8: Stars vs Skillability...")
fig, ax = plt.subplots(figsize=(10, 6))

github_with_scores = [d for d in github_data if d['stars'] > 0]
stars = [np.log10(d['stars'] + 1) for d in github_with_scores]
skillability = [d['skillability_score'] for d in github_with_scores]

# Create hexbin plot
hexbin = ax.hexbin(stars, skillability, gridsize=30, cmap='YlOrRd', mincnt=1)
ax.set_xlabel('log10(Stars + 1)')
ax.set_ylabel('Skillability Score')
ax.set_title('GitHub Repository Popularity vs Skillability')
ax.set_ylim(0.5, 5.5)
ax.set_yticks([1, 2, 3, 4, 5])
ax.grid(True, alpha=0.3)

# Add colorbar
cbar = plt.colorbar(hexbin, ax=ax)
cbar.set_label('Count')

# Add correlation text
corr = stats['github_quality_analysis']['stars_skillability_correlation']
ax.text(0.05, 0.95, f'Correlation: {corr:.3f}',
        transform=ax.transAxes, fontsize=11,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.tight_layout()
plt.savefig(figures_dir / 'fig8_stars_vs_skillability.png', bbox_inches='tight')
plt.close()
print(f"  ✓ Saved: fig8_stars_vs_skillability.png")

print("\n" + "="*60)
print("✅ All figures generated successfully!")
print(f"📁 Figures saved to: {figures_dir}")
print("="*60)
