"""Visualization module for generating charts."""

import matplotlib

matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Any
from pathlib import Path


def plot_capability_distribution(cap_dist: Dict[str, Dict[str, int]], output_path: str):
    """Plot capability distribution comparison.

    Args:
        cap_dist: Capability distribution by source
        output_path: Path to save the figure
    """
    # Get all capabilities
    all_caps = set(cap_dist['clawhub'].keys()) | set(cap_dist['github'].keys())
    all_caps = sorted(all_caps)

    clawhub_counts = [cap_dist['clawhub'].get(cap, 0) for cap in all_caps]
    github_counts = [cap_dist['github'].get(cap, 0) for cap in all_caps]

    # Create figure
    fig, ax = plt.subplots(figsize=(14, 6))

    x = np.arange(len(all_caps))
    width = 0.35

    ax.bar(x - width/2, clawhub_counts, width, label='Clawhub', alpha=0.8)
    ax.bar(x + width/2, github_counts, width, label='GitHub', alpha=0.8)

    ax.set_xlabel('Capability Class', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    ax.set_title('Capability Distribution: Clawhub vs GitHub', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([cap.replace('_', '\n') for cap in all_caps], rotation=45, ha='right', fontsize=9)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved capability distribution plot to {output_path}")


def plot_skillability_distribution(skill_dist: Dict[str, List[float]], output_path: str):
    """Plot skillability score distribution.

    Args:
        skill_dist: Skillability scores by source
        output_path: Path to save the figure
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Clawhub histogram
    if skill_dist['clawhub']:
        ax1.hist(skill_dist['clawhub'], bins=5, range=(1, 6), alpha=0.7, color='steelblue', edgecolor='black')
        ax1.set_xlabel('Skillability Score', fontsize=11)
        ax1.set_ylabel('Count', fontsize=11)
        ax1.set_title('Clawhub Skillability Distribution', fontsize=12, fontweight='bold')
        ax1.set_xticks([1, 2, 3, 4, 5])
        ax1.grid(axis='y', alpha=0.3)

    # GitHub histogram
    if skill_dist['github']:
        ax2.hist(skill_dist['github'], bins=5, range=(1, 6), alpha=0.7, color='coral', edgecolor='black')
        ax2.set_xlabel('Skillability Score', fontsize=11)
        ax2.set_ylabel('Count', fontsize=11)
        ax2.set_title('GitHub Skillability Distribution', fontsize=12, fontweight='bold')
        ax2.set_xticks([1, 2, 3, 4, 5])
        ax2.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved skillability distribution plot to {output_path}")


def plot_top_candidates_scatter(top_candidates: List[Dict[str, Any]], output_path: str):
    """Plot scatter plot of top candidates.

    Args:
        top_candidates: List of top candidate items
        output_path: Path to save the figure
    """
    if not top_candidates:
        print("No candidates to plot")
        return

    # Extract data
    skillability_cores = [item.get('skillability_core', 0) for item in top_candidates]
    repo_qualities = [item.get('repo_quality', 0) for item in top_candidates]
    stars = [item.get('stars', 100) for item in top_candidates]
    capabilities = [item.get('primary_capability', 'unknown') for item in top_candidates]

    # Create color map
    unique_caps = list(set(capabilities))
    colors = plt.cm.tab10(np.linspace(0, 1, len(unique_caps)))
    cap_to_color = {cap: colors[i] for i, cap in enumerate(unique_caps)}
    point_colors = [cap_to_color[cap] for cap in capabilities]

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))

    # Normalize star sizes for visualization
    sizes = [np.log10(s + 1) * 50 for s in stars]

    scatter = ax.scatter(skillability_cores, repo_qualities, s=sizes, c=point_colors,
                        alpha=0.6, edgecolors='black', linewidth=0.5)

    ax.set_xlabel('Skillability Core Score', fontsize=12)
    ax.set_ylabel('Repo Quality Score', fontsize=12)
    ax.set_title('Top 20 GitHub Candidates', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    # Add legend for capabilities
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w',
                                 markerfacecolor=cap_to_color[cap], markersize=8,
                                 label=cap.replace('_', ' ').title())
                      for cap in unique_caps]
    ax.legend(handles=legend_elements, loc='best', fontsize=9)

    # Annotate top 5
    for i in range(min(5, len(top_candidates))):
        name = top_candidates[i].get('name', '').split('/')[-1][:20]
        ax.annotate(name, (skillability_cores[i], repo_qualities[i]),
                   xytext=(5, 5), textcoords='offset points',
                   fontsize=8, alpha=0.7)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved top candidates scatter plot to {output_path}")


def generate_all_plots(cap_dist: Dict, skill_dist: Dict, top_candidates: List[Dict],
                       figures_dir: str):
    """Generate all visualization plots.

    Args:
        cap_dist: Capability distribution data
        skill_dist: Skillability distribution data
        top_candidates: Top candidate items
        figures_dir: Directory to save figures
    """
    Path(figures_dir).mkdir(parents=True, exist_ok=True)

    plot_capability_distribution(cap_dist, f"{figures_dir}/capability_distribution.png")
    plot_skillability_distribution(skill_dist, f"{figures_dir}/skillability_distribution.png")
    plot_top_candidates_scatter(top_candidates, f"{figures_dir}/top_candidates_scatter.png")
