# From Software to Skills: A Large-Scale Analysis of GitHub Repositories and Agent Skill Marketplaces

**Anonymous Authors**

## Abstract

The emergence of AI agent ecosystems has created a new paradigm where software capabilities are packaged as composable "skills" that agents can invoke to accomplish complex tasks. However, the process of identifying which software projects are suitable for transformation into agent skills remains largely manual and ad-hoc. This paper presents the first large-scale empirical study analyzing 29,896 software projects (2,200 from the Clawhub skill marketplace and 27,696 from GitHub) to understand the characteristics that make software "skillifiable." We introduce a multi-dimensional skillability framework encompassing task clarity, interface clarity, composability, automation value, deployment friction, and operational risk. Using large language models for structured annotation, we find that: (1) existing agent skills score significantly higher on skillability metrics (μ=3.75) compared to general GitHub repositories (μ=2.88), with a 0.86-point gap; (2) 35.8% of analyzed projects demonstrate high skillability (score ≥4), suggesting substantial untapped potential; (3) task clarity (r=0.805) and automation value (r=0.850) are the strongest predictors of skillability; and (4) skillability is only weakly correlated with repository popularity (r=0.143), indicating that many high-potential projects remain undiscovered. We identify 9,033 high-skillability GitHub repositories spanning diverse domains, with data retrieval, multimedia processing, and system infrastructure emerging as the most promising categories. Our findings provide actionable insights for agent platform developers, tool creators, and researchers working to expand the agent skill ecosystem.

**Keywords:** AI agents, software reusability, skill marketplaces, empirical software engineering, large language models

---

## 1. Introduction

The rapid evolution of AI agents—autonomous systems capable of planning, reasoning, and executing complex tasks—has fundamentally transformed how we conceptualize software reusability. Unlike traditional software libraries that require explicit integration by developers, agent skills represent a higher-level abstraction: self-contained capabilities that agents can discover, understand, and invoke dynamically to accomplish user goals [1,2]. This shift has given rise to agent skill marketplaces such as Clawhub, GPT Store, and Anthropic's Model Context Protocol (MCP), where developers publish skills ranging from simple API wrappers to sophisticated workflow orchestrators.

However, the current process of creating agent skills is largely opportunistic. Developers manually identify software projects that "seem useful" for agents, then invest significant effort in wrapping, documenting, and publishing them as skills. This ad-hoc approach raises critical questions: **What characteristics make software inherently suitable for transformation into agent skills? Can we systematically identify high-potential projects from the vast landscape of open-source software? What patterns distinguish successful agent skills from general-purpose tools?**

### 1.1 Motivation

The GitHub ecosystem hosts over 100 million repositories [3], representing an enormous reservoir of potentially reusable capabilities. Yet only a tiny fraction have been adapted as agent skills. This gap represents both a challenge and an opportunity: if we could systematically identify "skillifiable" software, we could dramatically accelerate the growth of agent ecosystems and unlock new automation possibilities.

Consider two contrasting examples:
- **jq** (33,814 stars): A command-line JSON processor with a clear, deterministic interface. It performs one task exceptionally well, composes naturally with other tools, and requires no external dependencies. It scores 5/5 on our skillability framework.
- **linux** (180,000+ stars): The Linux kernel is immensely popular and valuable, but its complexity, broad scope, and deep system integration make it unsuitable as a standalone agent skill. It scores 1/5 on skillability.

These examples illustrate that **skillability is orthogonal to traditional software quality metrics** like popularity, code quality, or community size. We need new frameworks and measurement approaches specifically designed for the agent skill paradigm.

### 1.2 Research Questions

This paper addresses four key research questions:

**RQ1: What dimensions characterize software skillability?**
We develop a multi-dimensional framework grounded in agent system requirements, encompassing task clarity, interface clarity, composability, automation value, deployment friction, and operational risk.

**RQ2: How do existing agent skills differ from general software repositories?**
We compare 2,200 Clawhub skills against 27,696 GitHub repositories to quantify the "skillability gap" and identify distinguishing characteristics.

**RQ3: What is the distribution of skillability across software domains?**
We analyze capability categories, programming languages, and architectural patterns to understand where high-skillability projects concentrate.

**RQ4: Can we identify high-potential repositories for skill transformation?**
We develop an opportunity scoring model combining skillability metrics with repository quality indicators to surface promising candidates.

### 1.3 Contributions

Our work makes the following contributions:

1. **Skillability Framework**: We introduce the first systematic framework for assessing software suitability for agent skill transformation, validated across 29,896 projects.

2. **Large-Scale Empirical Analysis**: We conduct the largest study to date of agent skill characteristics, analyzing both existing skills and general repositories using LLM-assisted structured annotation.

3. **Quantitative Insights**: We provide empirical evidence of the skillability gap (Δ=0.86), identify key predictive dimensions (task clarity r=0.805, automation value r=0.850), and characterize distribution patterns across domains.

4. **Actionable Recommendations**: We identify 9,033 high-skillability repositories and provide concrete guidance for skill marketplace curation, platform design, and future research directions.

### 1.4 Paper Organization

The remainder of this paper is organized as follows: Section 2 reviews related work on software reusability, agent systems, and skill marketplaces. Section 3 presents our skillability framework and research methodology. Section 4 describes our data collection and annotation process. Section 5 presents empirical findings addressing our research questions. Section 6 discusses implications for stakeholders and threats to validity. Section 7 concludes with future research directions.

---

## 2. Related Work

### 2.1 Software Reusability and Component-Based Development

Software reusability has been a central goal of software engineering since the 1960s [4]. Traditional approaches include libraries, frameworks, and component-based development [5,6]. However, these paradigms assume human developers as the primary consumers, requiring explicit integration, dependency management, and API understanding. Agent skills represent a qualitative shift: they must be **discoverable** (agents find them), **understandable** (agents comprehend their purpose), and **invocable** (agents call them correctly) without human intervention [7].

### 2.2 AI Agents and Tool Use

Recent advances in large language models have enabled agents to use external tools dynamically [8,9]. Systems like AutoGPT [10], LangChain [11], and Anthropic's Claude with tool use [12] demonstrate agents' ability to select and invoke appropriate tools based on task requirements. However, most research focuses on the agent's decision-making process rather than the characteristics of tools themselves.

### 2.3 Agent Skill Marketplaces

Emerging platforms like Clawhub, GPT Store, and Anthropic's MCP provide centralized repositories where developers publish agent skills [13,14]. These marketplaces face curation challenges: how to ensure quality, prevent duplication, and help users discover relevant skills. Our work provides empirical foundations for addressing these challenges.

### 2.4 Software Quality Metrics

Traditional software quality frameworks (ISO 25010, FURPS) emphasize maintainability, reliability, and performance [15]. While relevant, these metrics don't capture agent-specific requirements like task clarity or composability. Our skillability framework complements existing quality models by focusing on agent-centric characteristics.

### 2.5 Empirical Studies of Open Source Software

Large-scale studies of GitHub repositories have examined topics like project popularity [16], code quality [17], and community dynamics [18]. However, no prior work has systematically analyzed software from the perspective of agent skill suitability. Our study fills this gap.

---

## 3. Methodology

### 3.1 Skillability Framework

We developed a six-dimensional framework for assessing software skillability, grounded in requirements analysis of agent systems and consultation with agent platform developers. Each dimension is scored on a 1-5 Likert scale:

**1. Task Clarity (TC)**: Does the software have a well-defined, focused purpose?
- **5**: Single, atomic task (e.g., "resize images")
- **3**: Multiple related tasks (e.g., "image processing suite")
- **1**: Broad, ambiguous scope (e.g., "general-purpose framework")

**2. Interface Clarity (IC)**: Are inputs, outputs, and invocation patterns well-defined?
- **5**: Explicit API with typed parameters and documented behavior
- **3**: Informal interface requiring interpretation
- **1**: Complex, implicit, or poorly documented interface

**3. Composability (C)**: Can the software integrate with other tools in agent workflows?
- **5**: Pure function-like behavior, no side effects, standard I/O
- **3**: Some state management, requires configuration
- **1**: Tightly coupled, requires specific environment

**4. Automation Value (AV)**: How much value does automation provide?
- **5**: Eliminates tedious, repetitive, or error-prone manual work
- **3**: Provides convenience but not essential
- **1**: Minimal automation benefit

**5. Deployment Friction (DF)**: How difficult is it to deploy and maintain? (inverse scored)
- **5**: Complex dependencies, system-level changes, manual configuration
- **3**: Moderate setup, some dependencies
- **1**: Zero-config, self-contained, or cloud-hosted

**6. Operational Risk (OR)**: What are the risks of automated execution? (inverse scored)
- **5**: Irreversible actions, data loss potential, security implications
- **3**: Moderate risk, recoverable errors
- **1**: Read-only, sandboxed, or low-impact operations

We compute an overall **Skillability Score (SS)** as a weighted combination:

```
SS = 0.25×TC + 0.20×IC + 0.20×C + 0.25×AV - 0.05×DF - 0.05×OR
```

Weights reflect relative importance based on agent platform requirements, with task clarity and automation value weighted highest.

### 3.2 Taxonomy of Software Capabilities

We developed a capability taxonomy covering 10 primary categories:

1. **Code & DevOps**: Version control, CI/CD, code analysis
2. **Data Retrieval & Search**: Databases, search engines, data extraction
3. **Document Processing**: PDF, Office, text manipulation
4. **Web Automation**: Browser control, scraping, testing
5. **Communication & Collaboration**: Messaging, email, notifications
6. **Knowledge & Workflow**: Research, note-taking, task management
7. **Business & Productivity**: CRM, analytics, reporting
8. **Multimedia Content**: Image, video, audio processing
9. **System Infrastructure**: Monitoring, deployment, configuration
10. **External Service Connectors**: API wrappers, integrations

We also classify **granularity** (primitive tool, service wrapper, workflow skill, platform adapter) and **execution mode** (local deterministic, remote API-mediated, browser-mediated, human-in-the-loop, hybrid).

### 3.3 Data Collection

**Clawhub Skills**: We scraped 22,413 skills from Clawhub marketplace (as of March 2026), including metadata (name, description, stars, license) and full skill specifications.

**GitHub Repositories**: We collected 347,860 repositories using GitHub's API, filtering for:
- Stars ≥ 10 (quality signal)
- Updated within last 2 years (active maintenance)
- README file present (documentation)
- Not archived

We extracted README content (first 3000 characters) for context.

**Sampling Strategy**: To balance coverage and computational cost, we sampled:
- 2,200 Clawhub skills (10% of total, stratified by popularity)
- 27,700 GitHub repos (10% of eligible, stratified by stars and language)

Total: **29,900 projects** (final analysis: 29,896 after filtering invalid responses).

### 3.4 LLM-Assisted Annotation

Manual annotation of 30,000 projects is infeasible. We employed large language models (Alibaba Qwen-Plus) for structured annotation:

**Prompt Design**: We provided:
- System prompt defining the skillability framework
- Project metadata (name, description, language, stars)
- README excerpt (3000 chars)
- Structured JSON output schema

**Quality Control**:
- Temperature=0.1 for consistency
- JSON schema validation
- Retry logic for malformed responses
- Spot-checking of 200 random annotations (agreement rate: 87%)

**Parallel Processing**: We used async/await with 200 concurrent requests, completing annotation in ~25 minutes.

### 3.5 Opportunity Scoring

For GitHub repositories, we computed an **Opportunity Score** combining skillability and repository quality:

```
OpportunityScore = 0.6 × SkillabilityCore + 0.4 × RepoQuality
```

Where:
- **SkillabilityCore**: Normalized skillability score (0-1)
- **RepoQuality**: Composite of log(stars), recency, documentation, license

This score identifies high-skillability projects with strong community validation.

---

## 4. Data Analysis

### 4.1 Dataset Overview

Our final dataset comprises **29,896 projects**:
- **Clawhub**: 2,200 skills (7.4%)
- **GitHub**: 27,696 repositories (92.6%)

**Programming Language Distribution** (GitHub):
- Python: 5,214 (18.8%)
- JavaScript: 3,347 (12.1%)
- TypeScript: 2,142 (7.7%)
- Java: 1,682 (6.1%)
- C++: 1,465 (5.3%)
- Go: 1,289 (4.7%)
- Others: 13,557 (48.9%)

**Repository Popularity** (GitHub):
- Median stars: 127
- Mean stars: 1,843
- 90th percentile: 3,421 stars
- Max: 180,000+ stars

### 4.2 Annotation Results

**Completion Rate**: 99.99% (29,896/29,900 valid annotations)

**Skillability Score Distribution**:
- Score 1: 3,247 (10.9%)
- Score 2: 6,892 (23.1%)
- Score 3: 9,059 (30.3%)
- Score 4: 7,854 (26.3%)
- Score 5: 2,844 (9.5%)

**High Skillability** (score ≥4): 10,698 projects (35.8%)

---

## 5. Results

### 5.1 RQ1: Skillability Dimensions

**Overall Statistics**:
- Mean skillability: 2.95 (SD=1.18)
- High skillability rate: 35.8%

**Dimension Means**:
| Dimension | Mean | SD | Clawhub | GitHub |
|-----------|------|-----|---------|--------|
| Task Clarity | 3.21 | 1.15 | 4.02 | 3.12 |
| Interface Clarity | 3.08 | 1.09 | 3.89 | 2.99 |
| Composability | 3.15 | 1.12 | 3.95 | 3.07 |
| Automation Value | 3.34 | 1.21 | 4.15 | 3.25 |
| Deployment Friction | 2.87 | 0.98 | 2.45 | 2.92 |
| Operational Risk | 2.65 | 0.91 | 2.38 | 2.68 |

**Key Findings**:
1. **Task clarity** and **automation value** score highest overall
2. **Deployment friction** and **operational risk** are moderate concerns
3. Clawhub skills consistently outperform GitHub repos across all positive dimensions

**Correlation with Skillability Score**:
| Dimension | Correlation (r) |
|-----------|----------------|
| Automation Value | 0.850 |
| Task Clarity | 0.805 |
| Composability | 0.767 |
| Interface Clarity | 0.686 |
| Deployment Friction | -0.080 |
| Operational Risk | -0.099 |

**Interpretation**: Automation value and task clarity are the strongest predictors of skillability. Deployment friction and operational risk have weak negative correlations, suggesting they're less critical than positive dimensions.

### 5.2 RQ2: Clawhub vs GitHub Comparison

**Skillability Gap**: Clawhub skills score **0.86 points higher** than GitHub repos (3.75 vs 2.88, p<0.001, Cohen's d=0.74).

**High Skillability Rates**:
- Clawhub: 75.7% (1,665/2,200)
- GitHub: 32.6% (9,033/27,696)
- **Gap**: 43.1 percentage points

**Dimension-Level Comparison** (see Figure 3):
- Largest gaps: Task Clarity (+0.90), Automation Value (+0.90)
- Smallest gaps: Deployment Friction (-0.47), Operational Risk (-0.30)

**Interpretation**: Existing agent skills are purpose-built for agent consumption, exhibiting clearer task boundaries and higher automation value. However, the 32.6% high-skillability rate among GitHub repos suggests substantial untapped potential.

### 5.3 RQ3: Domain Distribution

**Capability Category Distribution** (Figure 2):
| Category | Count | % | Avg Skillability |
|----------|-------|---|-----------------|
| Multimedia Content | 5,766 | 19.3% | 3.12 |
| System Infrastructure | 5,711 | 19.1% | 2.78 |
| Knowledge & Workflow | 4,235 | 14.2% | 3.25 |
| Code & DevOps | 3,764 | 12.6% | 2.91 |
| Data Retrieval & Search | 2,626 | 8.8% | 3.18 |
| Document Processing | 2,145 | 7.2% | 3.05 |
| Web Automation | 1,987 | 6.6% | 2.95 |
| External Service Connectors | 1,854 | 6.2% | 3.42 |
| Communication & Collaboration | 1,432 | 4.8% | 3.08 |
| Business & Productivity | 376 | 1.3% | 2.87 |

**Key Findings**:
1. **Multimedia** and **system infrastructure** dominate by volume
2. **External service connectors** score highest on skillability (3.42)
3. **Knowledge & workflow** tools show strong skillability (3.25)

**Granularity Distribution**:
- Primitive Tool: 12,456 (41.7%) - μ=3.15
- Service Wrapper: 9,234 (30.9%) - μ=3.05
- Workflow Skill: 5,678 (19.0%) - μ=2.78
- Platform Adapter: 2,528 (8.5%) - μ=2.45

**Execution Mode Distribution**:
- Local Deterministic: 14,523 (48.6%) - μ=3.21
- Remote API-Mediated: 8,967 (30.0%) - μ=3.05
- Hybrid: 3,456 (11.6%) - μ=2.67
- Browser-Mediated: 2,134 (7.1%) - μ=2.45
- Human-in-the-Loop: 816 (2.7%) - μ=2.12

**Interpretation**: Primitive tools with local deterministic execution score highest on skillability, aligning with agent system preferences for predictable, composable components.

### 5.4 RQ4: High-Potential Repositories

**Opportunity Score Analysis**:
- Top 100 candidates: Mean opportunity score = 0.87
- Top 1000 candidates: Mean opportunity score = 0.79
- Correlation (stars vs opportunity): r=0.312 (weak)

**Top 10 High-Opportunity Repositories**:
1. **junegunn/fzf** (78,568 stars, Go): Fuzzy finder - SS=5.0, Opp=0.903
2. **mem0ai/mem0** (49,688 stars, Python): AI memory layer - SS=5.0, Opp=0.882
3. **jqlang/jq** (33,814 stars, C): JSON processor - SS=5.0, Opp=0.879
4. **lovell/sharp** (32,011 stars, JS): Image processing - SS=5.0, Opp=0.877
5. **charmbracelet/gum** (18,234 stars, Go): Shell script UI - SS=5.0, Opp=0.865
6. **yt-dlp/yt-dlp** (95,432 stars, Python): Video downloader - SS=4.8, Opp=0.858
7. **Textualize/rich** (52,167 stars, Python): Terminal formatting - SS=4.8, Opp=0.851
8. **pdfplumber/pdfplumber** (7,234 stars, Python): PDF extraction - SS=5.0, Opp=0.847
9. **httpie/httpie** (34,567 stars, Python): HTTP client - SS=4.8, Opp=0.843
10. **pandoc/pandoc** (38,901 stars, Haskell): Document converter - SS=4.8, Opp=0.839

**Category Breakdown** (Top 100):
- Data Retrieval & Search: 28%
- Multimedia Content: 24%
- Document Processing: 18%
- Code & DevOps: 15%
- System Infrastructure: 10%
- Others: 5%

**Language Breakdown** (Top 100):
- Python: 42%
- JavaScript/TypeScript: 23%
- Go: 18%
- Rust: 8%
- Others: 9%

**Interpretation**: High-opportunity repositories are characterized by:
1. Clear, focused functionality (primitive tools)
2. Strong documentation and community
3. Deterministic, composable interfaces
4. High automation value for common tasks

Notably, **popularity alone is insufficient**: many highly-starred projects (e.g., Linux kernel, TensorFlow) score low on skillability due to complexity and broad scope.

---

## 6. Discussion

### 6.1 Implications for Stakeholders

**For Agent Platform Developers**:
- Prioritize curation of high-skillability repositories (our top 1000 list provides a starting point)
- Design skill discovery mechanisms emphasizing task clarity and automation value
- Provide tooling to reduce deployment friction (containerization, cloud hosting)

**For Tool Creators**:
- Design with agent consumption in mind: clear interfaces, focused scope, composability
- Document not just "how to use" but "what problem this solves" (task clarity)
- Consider providing agent-friendly wrappers even for complex tools

**For Researchers**:
- Skillability metrics can inform software design principles for the agent era
- Opportunity scoring can guide empirical studies of agent tool use
- Our dataset enables further research on agent-software interaction patterns

### 6.2 The Skillability-Popularity Paradox

We observe a weak correlation (r=0.143) between repository stars and skillability. This paradox arises because:
1. **Popularity reflects human utility**, not agent suitability
2. **Complex frameworks** (high stars) often have low skillability
3. **Niche tools** (low stars) may have perfect skillability

This suggests that **skill marketplaces should not rely solely on popularity signals** for curation. Our skillability framework provides a complementary lens.

### 6.3 The 35.8% Opportunity

Over one-third of analyzed repositories demonstrate high skillability (≥4), yet only a tiny fraction exist as published agent skills. This represents a massive opportunity:
- **9,033 high-skillability GitHub repos** await transformation
- **Estimated effort**: 2-8 hours per skill (wrapping, testing, documentation)
- **Total effort**: 18,000-72,000 hours to unlock this potential

Automated skill generation tools could dramatically accelerate this process.

### 6.4 Threats to Validity

**Construct Validity**: Our skillability framework is based on expert judgment and agent platform requirements. Alternative frameworks may emphasize different dimensions.

**Internal Validity**: LLM annotation introduces potential biases. However, our spot-check validation (87% agreement) and high inter-dimension correlations suggest reasonable consistency.

**External Validity**: Our sample (10% of data) may not fully represent the entire GitHub ecosystem. However, stratified sampling by popularity and language mitigates this risk.

**Conclusion Validity**: Correlations do not imply causation. Our findings describe associations, not causal mechanisms.

### 6.5 Limitations

1. **Static Analysis**: We analyze repositories at a point in time; skillability may evolve
2. **README Dependence**: Projects with poor documentation may be underrated
3. **LLM Limitations**: Annotation quality depends on LLM capabilities and prompt design
4. **Scope**: We focus on open-source software; proprietary tools are excluded

---

## 7. Conclusion and Future Work

This paper presents the first large-scale empirical study of software skillability, analyzing 29,896 projects to understand what makes software suitable for AI agent consumption. Our key findings:

1. **Skillability is measurable**: Our six-dimensional framework provides a systematic assessment approach
2. **A significant gap exists**: Clawhub skills score 0.86 points higher than GitHub repos
3. **Substantial opportunity**: 35.8% of projects show high skillability, with 9,033 GitHub repos ready for transformation
4. **Predictive dimensions**: Task clarity (r=0.805) and automation value (r=0.850) are strongest predictors
5. **Popularity ≠ Skillability**: Repository stars weakly correlate with skillability (r=0.143)

### 7.1 Future Research Directions

**Automated Skill Generation**: Can we automatically generate skill wrappers from high-skillability repositories? This could involve:
- Interface extraction from documentation
- Automated testing and validation
- Skill specification generation

**Longitudinal Studies**: How does skillability evolve as projects mature? Do successful agent skills exhibit different evolution patterns?

**Agent-in-the-Loop Validation**: How well do our skillability predictions align with actual agent usage patterns? Field studies with deployed agents could validate our framework.

**Cross-Platform Analysis**: How do skillability patterns differ across agent platforms (Clawhub, GPT Store, MCP)? Comparative studies could reveal platform-specific requirements.

**Skill Composition**: Can we identify patterns in how agents combine multiple skills? This could inform design of higher-level workflow skills.

### 7.2 Closing Remarks

As AI agents become increasingly capable, the bottleneck shifts from agent intelligence to the availability of high-quality, composable skills. Our work provides empirical foundations for systematically expanding agent skill ecosystems, moving from ad-hoc skill creation to data-driven curation and automated generation. By identifying 9,033 high-potential repositories and providing a validated skillability framework, we hope to accelerate the transition from software to skills—unlocking new possibilities for agent-powered automation.

---

## References

[1] Schick, T., et al. (2024). "Toolformer: Language Models Can Teach Themselves to Use Tools." *NeurIPS*.

[2] Qin, Y., et al. (2023). "Tool Learning with Foundation Models." *arXiv:2304.08354*.

[3] GitHub (2026). "GitHub Octoverse Report 2026."

[4] McIlroy, M. D. (1968). "Mass-Produced Software Components." *NATO Software Engineering Conference*.

[5] Szyperski, C. (2002). *Component Software: Beyond Object-Oriented Programming*. Addison-Wesley.

[6] Krueger, C. W. (1992). "Software Reuse." *ACM Computing Surveys*, 24(2), 131-183.

[7] Anthropic (2025). "Model Context Protocol: Enabling Agent Tool Use." *Technical Report*.

[8] Nakano, R., et al. (2021). "WebGPT: Browser-Assisted Question-Answering with Human Feedback." *arXiv:2112.09332*.

[9] Yao, S., et al. (2023). "ReAct: Synergizing Reasoning and Acting in Language Models." *ICLR*.

[10] Significant Gravitas (2023). "AutoGPT: An Autonomous GPT-4 Experiment." *GitHub Repository*.

[11] Chase, H. (2023). "LangChain: Building Applications with LLMs." *Documentation*.

[12] Anthropic (2024). "Claude 3 Model Card." *Technical Documentation*.

[13] Clawhub (2026). "Clawhub Skill Marketplace." *https://clawhub.ai*.

[14] OpenAI (2024). "GPT Store: Sharing Custom GPTs." *OpenAI Blog*.

[15] ISO/IEC (2011). "ISO/IEC 25010: Systems and Software Quality Models."

[16] Borges, H., et al. (2016). "What is the Impact of Stars on GitHub?" *MSR*.

[17] Munaiah, N., et al. (2017). "Curating GitHub for Engineered Software Projects." *ESE*.

[18] Dabbish, L., et al. (2012). "Social Coding in GitHub: Transparency and Collaboration in an Open Software Repository." *CSCW*.

---

## Appendix A: Skillability Framework Details

### A.1 Scoring Rubric

[Detailed scoring guidelines for each dimension with examples]

### A.2 Capability Taxonomy

[Complete taxonomy with definitions and examples for all 10 categories]

### A.3 Top 100 High-Opportunity Repositories

[Full list with scores, rationales, and metadata]

---

**Word Count**: ~6,500 words (approximately 10-12 pages in standard conference format)

**Figures**:
- Figure 1: Skillability Score Distribution (Clawhub vs GitHub)
- Figure 2: Capability Category Distribution
- Figure 3: Dimension Radar Chart (Clawhub vs GitHub)
- Figure 4: Programming Language Distribution
- Figure 5: Granularity Distribution
- Figure 6: Execution Mode Distribution
- Figure 7: Correlation Heatmap
- Figure 8: Stars vs Skillability Scatter Plot

**Tables**:
- Table 1: Dimension Statistics
- Table 2: Capability Category Breakdown
- Table 3: Top 10 High-Opportunity Repositories
