# From Software Repositories to Agent Skills

[![Project Homepage](https://img.shields.io/badge/Homepage-Visit-green)](https://red0orange.github.io/repo2skill/)
[![Paper](https://img.shields.io/badge/Paper-PDF-red)](https://github.com/red0orange/repo2skill/blob/main/main.pdf)
[![Website](https://img.shields.io/badge/Website-Docs-blue)](docs/index.html)

An empirical study analyzing 29,896 software artifacts to understand which open-source repositories are suitable for transformation into AI agent skills.

The default extraction backend in this repository is Alibaba Bailian (`qwen-plus`).

## 📊 Key Findings

- **35.8%** of analyzed projects show high skillability potential
- **9,033** GitHub repositories identified as promising conversion candidates
- Skillability is **independent of popularity** (Spearman r_s = 0.003)
- High-potential projects concentrate in **Data Retrieval, Multimedia, and System Infrastructure**

## 🎯 What is Skillability?

Skillability measures how suitable a software project is for transformation into an agent-facing skill across six dimensions:

1. **Task Clarity** - How focused and well-bounded the purpose is
2. **Interface Clarity** - How explicit the invocation interface is
3. **Composability** - How naturally it fits into workflows
4. **Automation Value** - How much manual effort it removes
5. **Deployment Friction** - Difficulty to deploy (reverse-coded)
6. **Operational Risk** - Risk of automated execution (reverse-coded)

**Formula**: `SS = 0.25×TC + 0.20×IC + 0.20×C + 0.25×AV + 0.05×DF' + 0.05×OR'`

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
cp .env.example .env
# edit .env and set BAILIAN_API_KEY
```

### Run Analysis Pipeline

```bash
# 1. Crawl GitHub repositories
python crawl_github_repos.py

# 2. Sample data
python data_sampler.py

# 3. Run skillability scoring
python main.py

# 4. Generate visualizations
python generate_paper_figures.py
```

## 📁 Project Structure

```
├── paper/                      # Paper manuscript and figures
│   ├── paper_v7.md            # Latest paper version
│   └── assets/                # Figures used in the Markdown paper
├── latex/                      # Optional LaTeX/PDF paper version
│   ├── main.tex               # Main source
│   └── main.pdf               # Built paper PDF
├── docs/                       # Interactive visualization website
│   ├── index.html             # Main page
│   ├── repos.json             # Top 250 repositories
│   └── assets/                # Figure images
├── output/                     # Generated analysis outputs (gitignored)
├── validation/                 # Validation scripts
├── main.py                     # Main analysis pipeline
├── scorer.py                   # Skillability scoring logic
├── visualizer.py               # Visualization generation
├── crawl_github_repos.py       # GitHub data collection
├── scrape_clawhub_skills.py    # Clawhub marketplace scraper
└── requirements.txt            # Python dependencies
```

## 🌐 Interactive Website

View the interactive visualization at `docs/index.html` featuring:
- Six-dimension skillability framework
- Distribution analysis across 29,896 artifacts
- Category rankings and insights
- Paginated table of 250 top-ranked repositories

Deploy to GitHub Pages by publishing the `docs/` directory.

## 📈 Results

### Dataset Overview
- **Total artifacts**: 29,896 (2,200 Clawhub + 27,696 GitHub)
- **High-skillability rate**: 35.8% overall (75.7% Clawhub, 32.6% GitHub)
- **Mean skillability**: 2.95 overall (3.75 Clawhub, 2.88 GitHub)

### Top Categories by Skillability
1. Data Retrieval & Search (3.42, 48.3% high-skillability)
2. Multimedia Content (3.38, 46.1%)
3. System Infrastructure (3.31, 44.2%)

## 📄 Citation

```bibtex
@article{skillability2026,
  title={From Software Repositories to Agent Skills: An Exploratory Empirical Study of Skillability in Open-Source Ecosystems},
  author={Anonymous Authors},
  year={2026}
}
```

## 📝 License

MIT

## Notes

Generated outputs under `output/` and `output_large/` are intentionally not tracked.
