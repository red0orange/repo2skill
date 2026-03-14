"""HTML report generator."""

import os
from typing import Dict, List, Any
from datetime import datetime

from pipeline_utils import escape_html, ensure_parent_dir


def generate_html_report(summary_stats: Dict[str, Any],
                        top_candidates: List[Dict[str, Any]],
                        figures_dir: str,
                        output_path: str):
    """Generate HTML report with analysis results.

    Args:
        summary_stats: Summary statistics
        top_candidates: Top candidate items
        figures_dir: Directory containing figure files
        output_path: Path to save HTML report
    """
    report_dir = os.path.dirname(os.path.abspath(output_path))
    capability_figure = os.path.relpath(
        os.path.join(figures_dir, "capability_distribution.png"),
        report_dir,
    )
    skillability_figure = os.path.relpath(
        os.path.join(figures_dir, "skillability_distribution.png"),
        report_dir,
    )
    candidates_figure = os.path.relpath(
        os.path.join(figures_dir, "top_candidates_scatter.png"),
        report_dir,
    )

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Software2Skill Analysis Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .subtitle {{
            margin-top: 10px;
            opacity: 0.9;
        }}
        .section {{
            background: white;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h2 {{
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-top: 0;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }}
        .stat-label {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }}
        .stat-value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #333;
        }}
        .figure {{
            margin: 20px 0;
            text-align: center;
        }}
        .figure img {{
            max-width: 100%;
            border-radius: 5px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .figure-caption {{
            margin-top: 10px;
            color: #666;
            font-style: italic;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #667eea;
            color: white;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .score-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 3px;
            font-weight: bold;
            font-size: 0.9em;
        }}
        .score-high {{
            background-color: #d4edda;
            color: #155724;
        }}
        .score-medium {{
            background-color: #fff3cd;
            color: #856404;
        }}
        .score-low {{
            background-color: #f8d7da;
            color: #721c24;
        }}
        .repo-link {{
            color: #667eea;
            text-decoration: none;
        }}
        .repo-link:hover {{
            text-decoration: underline;
        }}
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 40px;
            padding: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Software2Skill Analysis Report</h1>
        <div class="subtitle">From Repositories to Skills: Measuring the Emerging Software Substrate for AI Agents</div>
        <div class="subtitle">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
    </div>

    <div class="section">
        <h2>📈 Summary Statistics</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Items Analyzed</div>
                <div class="stat-value">{summary_stats['total_items']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Clawhub Skills</div>
                <div class="stat-value">{summary_stats['clawhub_count']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">GitHub Repos</div>
                <div class="stat-value">{summary_stats['github_count']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Clawhub Skillability</div>
                <div class="stat-value">{summary_stats['clawhub_avg_skillability']:.2f}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg GitHub Skillability</div>
                <div class="stat-value">{summary_stats['github_avg_skillability']:.2f}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">High Skillability Repos (≥4)</div>
                <div class="stat-value">{summary_stats['github_high_skillability_count']}</div>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>📊 Capability Distribution</h2>
        <div class="figure">
            <img src="{escape_html(capability_figure)}" alt="Capability Distribution">
            <div class="figure-caption">Comparison of capability distribution between Clawhub skills and GitHub repositories</div>
        </div>
    </div>

    <div class="section">
        <h2>📊 Skillability Distribution</h2>
        <div class="figure">
            <img src="{escape_html(skillability_figure)}" alt="Skillability Distribution">
            <div class="figure-caption">Distribution of skillability scores for Clawhub skills and GitHub repositories</div>
        </div>
    </div>

    <div class="section">
        <h2>🎯 Top 20 GitHub Candidates</h2>
        <div class="figure">
            <img src="{escape_html(candidates_figure)}" alt="Top Candidates Scatter">
            <div class="figure-caption">Scatter plot of top candidates by skillability core and repo quality</div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Repository</th>
                    <th>Capability</th>
                    <th>Skillability</th>
                    <th>Opportunity Score</th>
                    <th>Stars</th>
                </tr>
            </thead>
            <tbody>
"""

    # Add top candidates to table
    for i, candidate in enumerate(top_candidates[:20], 1):
        name = escape_html(candidate.get('name', 'Unknown'))
        url = escape_html(candidate.get('url', '#'))
        capability = escape_html(candidate.get('primary_capability', 'unknown').replace('_', ' ').title())
        skillability = candidate.get('skillability_score', 0)
        opportunity = candidate.get('opportunity_score', 0)
        stars = candidate.get('stars', 0)

        # Determine score badge class
        if skillability >= 4:
            badge_class = 'score-high'
        elif skillability >= 3:
            badge_class = 'score-medium'
        else:
            badge_class = 'score-low'

        html += f"""
                <tr>
                    <td>{i}</td>
                    <td><a href="{url}" class="repo-link" target="_blank">{name}</a></td>
                    <td>{capability}</td>
                    <td><span class="score-badge {badge_class}">{skillability:.1f}</span></td>
                    <td>{opportunity:.3f}</td>
                    <td>{stars:,}</td>
                </tr>
"""

    html += """
            </tbody>
        </table>
    </div>

    <div class="section">
        <h2>💡 Key Findings</h2>
        <ul>
            <li><strong>Capability Coverage:</strong> The analysis reveals which capability classes are well-represented in Clawhub versus GitHub.</li>
            <li><strong>Skillability Gap:</strong> Many high-quality GitHub repositories show strong skillability potential but are not yet available as agent skills.</li>
            <li><strong>Opportunity Areas:</strong> The top candidates represent high-potential projects that could be transformed into valuable agent skills.</li>
        </ul>
    </div>

    <div class="footer">
        <p>Generated by Software2Skill Analysis Pipeline</p>
        <p>Research Project: From Repositories to Skills</p>
    </div>
</body>
</html>
"""

    ensure_parent_dir(output_path)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Saved HTML report to {output_path}")
