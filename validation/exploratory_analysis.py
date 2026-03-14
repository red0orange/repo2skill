"""
Exploratory Data Analysis for validation dataset.

Analyzes integrated dataset and generates EDA plots/statistics.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import json
import os
from pathlib import Path


def run_eda(data_path, metrics_path, output_dir):
    """
    Run exploratory data analysis on the validation dataset.

    Args:
        data_path: Path to integrated_data.csv
        metrics_path: Path to skill_metrics.json
        output_dir: Directory to save plots and stats
    """
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Load data
    print("Loading data...")
    df = pd.read_csv(data_path)

    with open(metrics_path, 'r') as f:
        metrics_data = json.load(f)

    print(f"Dataset shape: {df.shape}")
    print(f"Number of skills: {len(metrics_data.get('metrics', []))}")

    # 1. Data Quality Check
    print("\n" + "="*60)
    print("1. DATA QUALITY CHECK")
    print("="*60)

    print("\nMissing values per column:")
    missing = df.isnull().sum()
    for col, count in missing[missing > 0].items():
        print(f"  {col}: {count} ({100*count/len(df):.2f}%)")

    print("\nClass balance:")
    class_counts = df['source'].value_counts()
    for source, count in class_counts.items():
        print(f"  {source}: {count} ({100*count/len(df):.2f}%)")

    # 2. Class Distribution
    print("\n" + "="*60)
    print("2. CLASS DISTRIBUTION")
    print("="*60)

    fig, ax = plt.subplots(figsize=(10, 6))
    class_counts = df['source'].value_counts()
    colors = ['#1f77b4', '#ff7f0e']
    bars = ax.bar(class_counts.index, class_counts.values, color=colors, alpha=0.8, edgecolor='black')
    ax.set_ylabel('Count', fontsize=12, fontweight='bold')
    ax.set_xlabel('Source', fontsize=12, fontweight='bold')
    ax.set_title('Class Distribution: Clawhub vs GitHub', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}',
                ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'class_distribution.png'), dpi=100, bbox_inches='tight')
    plt.close()
    print("Saved: class_distribution.png")

    # 3. Skillability Score by Class
    print("\n" + "="*60)
    print("3. SKILLABILITY SCORE BY CLASS")
    print("="*60)

    for source in ['clawhub', 'github']:
        source_data = df[df['source'] == source]['skillability_core']
        print(f"\n{source.upper()}:")
        print(f"  Mean: {source_data.mean():.4f}")
        print(f"  Median: {source_data.median():.4f}")
        print(f"  Std Dev: {source_data.std():.4f}")
        print(f"  Min: {source_data.min():.4f}")
        print(f"  Max: {source_data.max():.4f}")

    fig, ax = plt.subplots(figsize=(10, 6))
    data_to_plot = [df[df['source'] == 'clawhub']['skillability_core'].dropna(),
                    df[df['source'] == 'github']['skillability_core'].dropna()]
    bp = ax.boxplot(data_to_plot, labels=['Clawhub', 'GitHub'], patch_artist=True,
                    showmeans=True, meanline=True)

    # Color boxes
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax.set_ylabel('Skillability Score', fontsize=12, fontweight='bold')
    ax.set_title('Skillability Core Distribution by Class', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'skillability_by_class.png'), dpi=100, bbox_inches='tight')
    plt.close()
    print("\nSaved: skillability_by_class.png")

    # 4. Per-dimension scores by class
    print("\n" + "="*60)
    print("4. SKILLABILITY DIMENSION SCORES BY CLASS")
    print("="*60)

    dimensions = ['task_clarity', 'interface_clarity', 'composability',
                  'automation_value', 'deployment_friction', 'operational_risk']

    dimension_means = {}
    for source in ['clawhub', 'github']:
        dimension_means[source] = {}
        print(f"\n{source.upper()}:")
        for dim in dimensions:
            mean_val = df[df['source'] == source][dim].mean()
            dimension_means[source][dim] = mean_val
            print(f"  {dim}: {mean_val:.4f}")

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(dimensions))
    width = 0.35

    clawhub_vals = [dimension_means['clawhub'][dim] for dim in dimensions]
    github_vals = [dimension_means['github'][dim] for dim in dimensions]

    bars1 = ax.bar(x - width/2, clawhub_vals, width, label='Clawhub',
                   color='#1f77b4', alpha=0.8, edgecolor='black')
    bars2 = ax.bar(x + width/2, github_vals, width, label='GitHub',
                   color='#ff7f0e', alpha=0.8, edgecolor='black')

    ax.set_ylabel('Mean Score', fontsize=12, fontweight='bold')
    ax.set_title('Skillability Dimensions by Class', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([d.replace('_', '\n') for d in dimensions], fontsize=10)
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'dimension_scores_by_class.png'), dpi=100, bbox_inches='tight')
    plt.close()
    print("\nSaved: dimension_scores_by_class.png")

    # 5. Clawhub marketplace distribution
    print("\n" + "="*60)
    print("5. CLAWHUB MARKETPLACE DISTRIBUTION")
    print("="*60)

    clawhub_df = df[df['source'] == 'clawhub'].copy()

    # Convert to numeric, handling missing values
    clawhub_df['clawhub_downloads'] = pd.to_numeric(clawhub_df['clawhub_downloads'], errors='coerce')
    clawhub_df['clawhub_installs'] = pd.to_numeric(clawhub_df['clawhub_installs'], errors='coerce')

    # Create log-transformed versions
    clawhub_df['log_downloads'] = np.log1p(clawhub_df['clawhub_downloads'].fillna(0))
    clawhub_df['log_installs'] = np.log1p(clawhub_df['clawhub_installs'].fillna(0))

    print(f"\nClawhub items: {len(clawhub_df)}")
    print(f"Downloads - Mean: {clawhub_df['clawhub_downloads'].mean():.2f}, "
          f"Median: {clawhub_df['clawhub_downloads'].median():.2f}")
    print(f"Installs - Mean: {clawhub_df['clawhub_installs'].mean():.2f}, "
          f"Median: {clawhub_df['clawhub_installs'].median():.2f}")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].hist(clawhub_df['log_downloads'].dropna(), bins=30, color='#1f77b4',
                 alpha=0.7, edgecolor='black')
    axes[0].set_xlabel('log(Downloads + 1)', fontsize=11, fontweight='bold')
    axes[0].set_ylabel('Frequency', fontsize=11, fontweight='bold')
    axes[0].set_title('Distribution of log(Downloads)', fontsize=12, fontweight='bold')
    axes[0].grid(axis='y', alpha=0.3, linestyle='--')

    axes[1].hist(clawhub_df['log_installs'].dropna(), bins=30, color='#ff7f0e',
                 alpha=0.7, edgecolor='black')
    axes[1].set_xlabel('log(Installs + 1)', fontsize=11, fontweight='bold')
    axes[1].set_ylabel('Frequency', fontsize=11, fontweight='bold')
    axes[1].set_title('Distribution of log(Installs)', fontsize=12, fontweight='bold')
    axes[1].grid(axis='y', alpha=0.3, linestyle='--')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'marketplace_distribution.png'), dpi=100, bbox_inches='tight')
    plt.close()
    print("Saved: marketplace_distribution.png")

    # 6. Skillability vs marketplace performance correlation
    print("\n" + "="*60)
    print("6. SKILLABILITY VS MARKETPLACE PERFORMANCE")
    print("="*60)

    # Remove rows with missing log_downloads
    correlation_data = clawhub_df[['skillability_core', 'log_downloads']].dropna()

    if len(correlation_data) > 1:
        # Calculate Pearson correlation
        correlation = correlation_data['skillability_core'].corr(correlation_data['log_downloads'])
        print(f"\nPearson Correlation (skillability_core vs log_downloads): {correlation:.4f}")
        print(f"Sample size: {len(correlation_data)}")
    else:
        correlation = 0
        print("Insufficient data for correlation")

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(correlation_data['skillability_core'], correlation_data['log_downloads'],
              alpha=0.6, s=50, color='#1f77b4', edgecolor='black', linewidth=0.5)
    ax.set_xlabel('Skillability Core Score', fontsize=12, fontweight='bold')
    ax.set_ylabel('log(Downloads + 1)', fontsize=12, fontweight='bold')
    ax.set_title(f'Skillability vs Downloads (r={correlation:.4f})',
                fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'skillability_vs_downloads.png'), dpi=100, bbox_inches='tight')
    plt.close()
    print("Saved: skillability_vs_downloads.png")

    # 7. Language distribution
    print("\n" + "="*60)
    print("7. LANGUAGE DISTRIBUTION")
    print("="*60)

    github_df = df[df['source'] == 'github']
    language_counts = github_df['language'].value_counts().head(15)

    print(f"\nTop 15 languages in GitHub repos:")
    for lang, count in language_counts.items():
        print(f"  {lang}: {count}")

    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.barh(range(len(language_counts)), language_counts.values,
                   color='#2ca02c', alpha=0.8, edgecolor='black')
    ax.set_yticks(range(len(language_counts)))
    ax.set_yticklabels(language_counts.index, fontsize=10)
    ax.set_xlabel('Number of Repositories', fontsize=12, fontweight='bold')
    ax.set_title('Top 15 Languages in GitHub Repositories', fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3, linestyle='--')

    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, language_counts.values)):
        ax.text(val, i, f' {int(val)}', va='center', fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'language_distribution.png'), dpi=100, bbox_inches='tight')
    plt.close()
    print("Saved: language_distribution.png")

    # 8. Summary Statistics
    print("\n" + "="*60)
    print("8. SUMMARY STATISTICS")
    print("="*60)

    summary_stats = {
        'dataset': {
            'total_samples': int(len(df)),
            'clawhub_samples': int(len(df[df['source'] == 'clawhub'])),
            'github_samples': int(len(df[df['source'] == 'github'])),
        },
        'skillability_core': {
            'clawhub': {
                'mean': float(df[df['source'] == 'clawhub']['skillability_core'].mean()),
                'median': float(df[df['source'] == 'clawhub']['skillability_core'].median()),
                'std': float(df[df['source'] == 'clawhub']['skillability_core'].std()),
            },
            'github': {
                'mean': float(df[df['source'] == 'github']['skillability_core'].mean()),
                'median': float(df[df['source'] == 'github']['skillability_core'].median()),
                'std': float(df[df['source'] == 'github']['skillability_core'].std()),
            },
        },
        'dimensions': dimension_means,
        'marketplace': {
            'clawhub_count': int(len(clawhub_df)),
            'downloads_mean': float(clawhub_df['clawhub_downloads'].mean()) if len(clawhub_df) > 0 else 0,
            'installs_mean': float(clawhub_df['clawhub_installs'].mean()) if len(clawhub_df) > 0 else 0,
        },
        'correlation': {
            'skillability_vs_downloads': float(correlation),
        },
        'languages': {
            'top_15': language_counts.to_dict(),
        },
    }

    with open(os.path.join(output_dir, 'summary_stats.json'), 'w') as f:
        json.dump(summary_stats, f, indent=2)
    print("Saved: summary_stats.json")

    print("\n" + "="*60)
    print("EDA COMPLETED SUCCESSFULLY")
    print("="*60)
    print(f"\nGenerated files in {output_dir}:")
    print("  - class_distribution.png")
    print("  - skillability_by_class.png")
    print("  - dimension_scores_by_class.png")
    print("  - marketplace_distribution.png")
    print("  - skillability_vs_downloads.png")
    print("  - language_distribution.png")
    print("  - summary_stats.json")


if __name__ == '__main__':
    import sys

    # Default paths
    data_path = '/home/red0orange/Projects/OpenClawAnalysis/software2skill_analysis/.worktrees/validation/software2skill_analysis/output/validation/integrated_data.csv'
    metrics_path = '/home/red0orange/Projects/OpenClawAnalysis/software2skill_analysis/.worktrees/validation/software2skill_analysis/output/validation/skill_metrics.json'
    output_dir = '/home/red0orange/Projects/OpenClawAnalysis/software2skill_analysis/.worktrees/validation/software2skill_analysis/output/validation/eda'

    run_eda(data_path, metrics_path, output_dir)
