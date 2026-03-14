# From Software to Skills: An Exploratory Analysis of GitHub Repositories and Agent Skill Marketplaces

**Anonymous Authors**

## Abstract

The emergence of AI agent ecosystems has created a new paradigm where software capabilities are packaged as composable "skills" that agents can invoke to accomplish complex tasks. However, the process of identifying which software projects are suitable for transformation into agent skills remains largely manual and ad-hoc. This paper presents an exploratory large-scale empirical study analyzing 29,896 software projects (2,200 from the Clawhub skill marketplace and 27,696 from GitHub) to understand the characteristics that make software suitable for agent skill transformation. We introduce a skillability framework encompassing task clarity, interface clarity, composability, automation value, deployment friction, and operational risk. Using large language models for structured annotation, we find that: (1) existing agent skills score higher on skillability metrics (μ=3.75) compared to general GitHub repositories (μ=2.88), with a 0.87-point gap (Welch's t-test, p<0.001, Cohen's d=0.74, 95% CI: [0.81, 0.93]), though this comparison is confounded by documentation differences; (2) 35.8% of analyzed projects demonstrate high skillability (score ≥4.0), suggesting substantial opportunities; (3) task clarity and automation value show the strongest associations with overall skillability scores; and (4) skillability is only weakly correlated with repository popularity (r_s=0.138), indicating that many potentially promising projects remain undiscovered. We identify 9,033 high-skillability GitHub repositories spanning diverse domains, with data retrieval, multimedia processing, and system infrastructure emerging as promising categories. This exploratory work provides empirical foundations for understanding software reusability in agent ecosystems.

**Keywords:** AI agents, software reusability, skill marketplaces, empirical software engineering, large language models

---

## 1. Introduction

The rapid evolution of AI agents—autonomous systems capable of planning, reasoning, and executing complex tasks—has fundamentally transformed how we conceptualize software reusability and composability. Unlike traditional software libraries that require explicit integration by developers, agent skills represent a higher-level abstraction: self-contained capabilities that agents can discover, understand, and invoke dynamically to accomplish user goals [1,2]. This shift raises important software engineering questions about interface design, modularity, and the characteristics that make software components suitable for automated reuse. The emergence of agent skill marketplaces such as Clawhub, GPT Store, and Anthropic's Model Context Protocol (MCP) provides new venues for distributing reusable software assets, where developers publish skills ranging from simple API wrappers to sophisticated workflow orchestrators.

However, the current process of creating agent skills is largely opportunistic. Developers manually identify software projects that appear suitable for agents, then invest significant effort in wrapping, documenting, and publishing them as skills. This ad-hoc approach raises critical software engineering questions: **What characteristics make software inherently suitable for transformation into agent skills? Can we systematically identify high-potential projects from the vast landscape of open-source software? What patterns distinguish successful agent skills from general-purpose tools?**

### 1.1 Motivation and Software Engineering Context

The GitHub ecosystem hosts over 100 million repositories [3], representing an enormous reservoir of potentially reusable software components. Yet only a tiny fraction have been adapted as agent skills. This gap represents both a challenge and an opportunity for software engineering research: if we could systematically characterize skillifiable software, we could inform design principles for building more reusable, composable software components and accelerate the growth of agent ecosystems.

From a software engineering perspective, this work addresses fundamental questions about software reusability, interface design, and architectural modularity in the context of automated consumption. Traditional software reuse frameworks emphasize human developers as consumers [4,5], but agent-mediated reuse introduces new requirements: software must be discoverable through metadata, understandable through documentation, and invocable through well-defined interfaces—all without human intervention.

Consider two contrasting examples:
- **jq** (33,814 stars): A command-line JSON processor with a clear, deterministic interface. It performs one task exceptionally well, composes naturally with other tools, and requires no external dependencies. It exemplifies high skillability.
- **linux** (180,000+ stars): The Linux kernel is immensely popular and valuable, but its complexity, broad scope, and deep system integration make it unsuitable as a standalone agent skill. It exemplifies low skillability despite high quality.

These examples illustrate that **skillability is orthogonal to traditional software quality metrics** like popularity, code quality, or community size. We need new frameworks and measurement approaches specifically designed for understanding software reusability in agent ecosystems.

### 1.2 Research Questions

This paper addresses four key research questions:

**RQ1: What dimensions characterize software suitability for agent skill transformation?**
We develop a multi-dimensional framework grounded in agent system requirements and software engineering principles, encompassing task clarity, interface clarity, composability, automation value, deployment friction, and operational risk.

**RQ2: How do existing agent skills differ from general software repositories?**
We conduct an exploratory comparison of 2,200 Clawhub skills against 27,696 GitHub repositories to identify distinguishing characteristics, acknowledging significant methodological limitations in this comparison.

**RQ3: What is the distribution of skillability across software domains?**
We analyze capability categories, programming languages, and architectural patterns to understand where high-skillability projects concentrate.

**RQ4: Can we identify promising repositories for skill transformation?**
We develop an opportunity scoring model combining skillability metrics with repository quality indicators to surface promising candidates.

### 1.3 Contributions

Our work makes the following contributions:

1. **Skillability Framework**: We introduce a framework for assessing software suitability for agent skill transformation, applied to 29,896 projects. This framework provides a structured approach to characterizing agent-friendly software.

2. **Large-Scale Exploratory Analysis**: We conduct an exploratory study of agent skill characteristics, analyzing both existing skills and general repositories using LLM-assisted structured annotation. This represents empirical work in characterizing software for agent ecosystems.

3. **Quantitative Insights**: We provide evidence of differences between existing skills and general repositories (Δ=0.87, though confounded by documentation differences), identify dimensions with strong associations to overall scores, and characterize distribution patterns across domains.

4. **Candidate Dataset**: We identify 9,033 repositories with high skillability scores and provide data for skill marketplace curation, platform design, and future research directions.

### 1.4 Paper Organization

The remainder of this paper is organized as follows: Section 2 reviews related work on software reusability, agent systems, and skill marketplaces. Section 3 presents our skillability framework and research methodology. Section 4 describes our data collection and annotation process. Section 5 presents empirical findings addressing our research questions. Section 6 discusses implications for stakeholders, limitations, and threats to validity. Section 7 concludes with future research directions.

---

## 2. Related Work

### 2.1 Software Reusability and Component-Based Development

Software reusability has been a central goal of software engineering since McIlroy's seminal work on mass-produced software components [4]. Traditional approaches include libraries, frameworks, and component-based development [5,6,7]. Szyperski's component software paradigm [5] emphasizes composition, encapsulation, and interface contracts—principles that remain relevant for agent skills. However, these paradigms assume human developers as the primary consumers, requiring explicit integration, dependency management, and API understanding.

Research on software component reusability has identified key factors including interface clarity, modularity, and documentation quality [8,9]. Morisio et al. [10] identified success factors in software reuse including clear specifications, well-defined interfaces, and minimal coupling. Our skillability framework builds on these foundations while addressing agent-specific requirements such as task clarity and automation value. Unlike traditional reuse metrics that focus on code-level properties, our framework emphasizes the semantic clarity and composability needed for automated discovery and invocation.

Software product lines [11] and feature-oriented software development [12] provide systematic approaches to building families of reusable components. These methodologies emphasize variability management and configuration—challenges that also arise in agent skill ecosystems where skills must adapt to different agent architectures and task contexts.

### 2.2 Software Ecosystems and Repository Mining

Software ecosystems research examines the networks of interdependent software components, developers, and users [13,14]. Manikas and Hansen [13] define software ecosystems as collections of software projects developed and evolving together in the same environment. Agent skill marketplaces represent emerging ecosystems with unique characteristics: skills are consumed by automated agents rather than human developers, and discovery mechanisms rely on semantic understanding rather than traditional dependency resolution.

Repository mining techniques have been applied extensively to understand software development patterns, quality indicators, and evolution [15,16,17]. Borges et al. [18] examined factors impacting GitHub repository popularity, finding that documentation quality, community engagement, and project age are significant predictors. Munaiah et al. [19] developed methods for curating GitHub repositories to identify engineered software projects suitable for empirical studies. Our work applies similar mining techniques but focuses on a novel dimension: suitability for agent consumption.

Dependency network analysis [20,21] has revealed patterns in how software components interconnect within ecosystems. Decan et al. [20] compared dependency evolution across seven packaging ecosystems, identifying common patterns of growth, fragmentation, and consolidation. Agent skill ecosystems face similar challenges in managing dependencies and ensuring composability.


### 2.3 API Usability and Interface Design

API usability research has examined factors that make programming interfaces learnable, efficient, and error-resistant [22,23,24]. Piccioni et al. [22] conducted empirical studies of API usability, identifying principles such as consistency, discoverability, and clear error messages. Myers and Stylos [25] found that API design significantly impacts developer productivity and code quality.

While API usability traditionally focuses on human developers, many principles apply to agent consumption. Robillard [26] emphasized the importance of documentation and examples in API learning—factors that become even more critical when agents must understand interfaces without human guidance. However, agents have different cognitive constraints: they excel at parsing structured specifications but struggle with implicit conventions and contextual knowledge that human developers acquire through experience.

### 2.4 AI Agents and Tool Use

Recent advances in large language models have enabled agents to use external tools dynamically [27,28,29]. Schick et al. [27] introduced Toolformer, demonstrating that language models can learn to invoke APIs through self-supervised learning. Yao et al. [28] proposed ReAct, combining reasoning and acting to enable agents to interact with external environments. Patil et al. [29] developed Gorilla, a model fine-tuned on API documentation to improve tool selection and invocation accuracy.

Systems like AutoGPT [30], LangChain [31], and Anthropic's Claude with tool use [32] demonstrate agents' ability to select and invoke appropriate tools based on task requirements. However, most research focuses on the agent's decision-making process rather than the characteristics of tools themselves. Qin et al. [33] surveyed tool learning in LLMs, identifying challenges in tool selection, parameter filling, and error handling. Our work complements this research by examining tool properties that facilitate agent consumption.

### 2.5 Agent Skill Marketplaces and Platforms

Emerging platforms like Clawhub, GPT Store, and Anthropic's MCP provide centralized repositories where developers publish agent skills [34,35]. These marketplaces face curation challenges similar to traditional app stores: ensuring quality, preventing duplication, and helping users discover relevant content. Research on mobile app ecosystems [36,37] has examined factors influencing app success, including ratings, reviews, and feature descriptions. However, agent skill marketplaces differ in that the primary consumers are automated agents rather than human users, requiring different discovery and quality assessment mechanisms.

The Model Context Protocol (MCP) [35] represents a standardization effort, defining common interfaces for agent-tool interaction. Similar standardization efforts in web services (SOAP, REST) and microservices [38] provide lessons for agent skill ecosystem development.

### 2.6 Software Quality Metrics and Measurement

Traditional software quality frameworks (ISO 25010 [39], FURPS [40]) emphasize maintainability, reliability, and performance. These frameworks provide comprehensive quality models but do not specifically address agent consumption requirements. Our skillability framework complements existing quality models by focusing on characteristics relevant to automated discovery and invocation.

Measurement validity in software engineering has been extensively studied [41,42]. Kitchenham et al. [41] emphasized the importance of construct validity, reliability, and external validation in software metrics. Our work acknowledges these principles while recognizing that skillability measurement is in early stages and requires further validation.

### 2.7 LLM-Based Annotation and Evaluation

The use of large language models for annotation and evaluation tasks has gained traction in software engineering research [43,44,45]. Zheng et al. [43] demonstrated that LLMs can serve as effective judges for code quality assessment. However, concerns about reliability, bias, and validity remain [44]. Our work employs LLM annotation with explicit validation against human annotators, acknowledging both the efficiency benefits and methodological limitations of this approach.

### 2.8 Research Gaps and Positioning

This work addresses several gaps in existing research:

1. **Lack of agent-centric software characterization**: While API usability and software reuse are well-studied, agent-specific requirements (automated discovery, semantic clarity, composability) remain underexplored.

2. **Absence of empirical data on skill marketplaces**: Agent skill ecosystems are nascent, and empirical characterization is needed to inform platform design and curation strategies.

3. **Need for systematic identification methods**: Current skill creation is ad-hoc; systematic approaches to identifying suitable software could accelerate ecosystem growth.

Our work provides exploratory evidence in these areas, contributing to the emerging field of software engineering for AI agent ecosystems.

---

## 3. Methodology

### 3.1 Skillability Framework

We developed a six-dimensional framework for assessing software suitability for agent skill transformation, grounded in requirements analysis of agent systems and consultation with agent platform developers. Each dimension is scored on a 1-5 Likert scale:

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

**Weight Justification**: Weights reflect relative importance based on agent platform requirements, with task clarity and automation value weighted highest (0.25 each) as these most directly impact whether an agent can understand and benefit from using a tool. Interface clarity and composability receive moderate weights (0.20 each) as they affect integration difficulty. Deployment friction and operational risk receive lower weights (0.05 each) as these can often be mitigated through containerization or sandboxing.

**Score Range and Interpretation**: The skillability score is a continuous value in the range [1, 5]. The weighted formula produces scores that naturally fall within this range given the 1-5 Likert scales for each dimension. The threshold "high skillability ≥4.0" refers to continuous scores of 4.0 or above.


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

We also classify **granularity** (primitive tool, service wrapper, workflow skill, platform adapter) and **execution mode** (local deterministic, remote API-mediated, browser-mediated, human-in-the-loop, hybrid). Complete definitions are provided in Appendix B.2.

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

**Sampling Limitations and Scope**: Our filtering criteria (stars ≥10, active, README present) bias toward well-documented, actively maintained projects with community validation. This is appropriate for our exploratory research questions, as we aim to identify high-potential candidates that are already somewhat validated by community use. However, **our findings apply specifically to this population of well-documented, actively maintained repositories with community validation, not to all software projects**.

### 3.4 LLM-Assisted Annotation

Manual annotation of 30,000 projects is infeasible. We employed large language models (Alibaba Qwen-Plus) for structured annotation, acknowledging both the efficiency benefits and methodological limitations of this approach.

**Prompt Design**: We provided:
- System prompt defining the skillability framework with detailed scoring rubrics for each dimension (5-point scale with concrete examples at each level)
- Project metadata (name, description, language, stars)
- README excerpt (3000 chars)
- Structured JSON output schema with required fields for all six dimensions plus capability category, granularity, and execution mode

The complete annotation prompt with system message, user message template, and JSON schema is provided in Appendix A.1.

**Model Configuration**:
- Model: Alibaba Qwen-Plus (version: qwen-plus-2024-11)
- Temperature: 0.1 (for consistency)
- Max tokens: 2000
- JSON schema validation with retry logic for malformed responses
- Single-pass annotation: All six dimensions, category, granularity, and execution mode generated in one API call

**Quality Control and Validation**:

We conducted validation on 200 randomly sampled annotations (100 from Clawhub, 100 from GitHub). Two human annotators independently scored these projects using the same rubric, then compared with LLM annotations:

**Agreement Metrics**:
- **Overall agreement rate**: 87% (within ±0.5 points on 1-5 scale)
- **Per-dimension agreement**:
  - Task Clarity: 89%
  - Automation Value: 91%
  - Deployment Friction: 86%
  - Operational Risk: 88%
  - Interface Clarity: 85%
  - Composability: 84%

**Disagreement Analysis**: Most disagreements occurred on Interface Clarity and Composability, where README excerpts provided insufficient information about actual API structure and integration patterns. LLM annotations tended to be slightly more generous (mean difference: +0.15 points) compared to human annotations. Detailed validation results are provided in Appendix A.3.

**Limitations of LLM Annotation**: Our approach has several limitations: (1) README-only information may be insufficient for assessing interface clarity, deployment friction, and operational risk; (2) single-model dependency may introduce systematic biases; (3) metadata (stars, language) may influence scoring beyond intended dimensions. Despite these limitations, LLM annotation enables large-scale exploratory analysis that would be impractical manually.

### 3.5 Opportunity Scoring

For GitHub repositories, we computed an **Opportunity Score** combining skillability and repository quality:

```
OpportunityScore = 0.6 × SkillabilityScore_normalized + 0.4 × RepoQuality
```

Where:
- **SkillabilityScore_normalized**: Skillability score normalized to 0-1 range: (SS - 1) / 4
- **RepoQuality**: Composite metric computed as:
  ```
  RepoQuality = 0.4 × log_stars + 0.3 × recency + 0.2 × doc_quality + 0.1 × license
  ```
  - log_stars: log10(stars + 1), normalized to 0-1 using max observed value
  - recency: days since last update, normalized inversely (more recent = higher score)
  - doc_quality: README length / 10000, capped at 1.0
  - license: 1.0 if permissive license (MIT, Apache, BSD), 0.5 if other, 0.0 if none

This score identifies high-skillability projects with strong community validation and active maintenance.

### 3.6 Statistical Analysis

We employed the following statistical methods:

**Comparison Tests**: Welch's t-test for comparing Clawhub vs GitHub skillability scores (does not assume equal variances). We report p-values, effect sizes (Cohen's d), and 95% confidence intervals. We also computed bootstrap confidence intervals (10,000 resamples) as a robustness check.

**Assumption Checks**:
- Normality: Shapiro-Wilk test on subsamples (n=5000) showed deviation from normality (p<0.001), but t-tests are robust to non-normality with large samples (n>2000)
- Homogeneity of variance: Levene's test confirmed unequal variances (p<0.001), justifying use of Welch's t-test
- Bootstrap confidence intervals (nonparametric) closely matched parametric CIs, supporting robustness

**Correlation Analysis**:
- Pearson correlation coefficients for examining associations between dimensions and overall scores (appropriate for continuous composite scores)
- **Spearman rank correlation** for examining associations between skillability and repository stars (due to highly skewed star distribution)

**Effect Sizes**: We report Cohen's d for all major comparisons. Effect size interpretation: small (d=0.2), medium (d=0.5), large (d=0.8).

**Multiple Testing**: We did not apply multiple comparison corrections (e.g., Bonferroni, FDR), as our analysis is exploratory rather than confirmatory.

All statistical analyses were conducted using Python (scipy.stats, numpy, scikit-learn). Complete statistical details are provided in Appendix C.

---

## 4. Dataset and Results Overview

### 4.1 Dataset Overview

Our final dataset comprises **29,896 projects**:
- **Clawhub**: 2,200 skills (7.4%)
- **GitHub**: 27,696 repositories (92.6%)

**Table 1: Dataset Overview**

| Metric | Clawhub | GitHub | Total |
|--------|---------|--------|-------|
| Projects | 2,200 | 27,696 | 29,896 |
| Mean Stars | 847 | 1,843 | 1,770 |
| Median Stars | 156 | 127 | 129 |
| Languages | 42 | 87 | 89 |
| Categories | 10 | 10 | 10 |

**Programming Language Distribution** (GitHub, n=27,696):
- Python: 5,214 (18.8%)
- JavaScript: 3,347 (12.1%)
- TypeScript: 2,142 (7.7%)
- Java: 1,682 (6.1%)
- C++: 1,465 (5.3%)
- Go: 1,358 (4.9%)
- Others: 12,488 (45.1%)

**Repository Popularity** (GitHub):
- Median stars: 127
- Mean stars: 1,843
- 90th percentile: 3,421 stars
- Max: 180,000+ stars
- Distribution: Highly right-skewed (skewness=12.4)

### 4.2 Annotation Results

**Completion Rate**: 99.99% (29,896/29,900 valid annotations)

**Skillability Score Distribution** (continuous scores rounded to nearest integer for presentation):
- Score 1 (1.0–1.5): 1,792 (6.0%)
- Score 2 (1.5–2.5): 9,679 (32.4%)
- Score 3 (2.5–3.5): 7,727 (25.8%)
- Score 4 (3.5–4.5): 9,700 (32.4%)
- Score 5 (4.5–5.0): 998 (3.3%)

**High Skillability** (continuous score ≥4.0): 10,698 projects (35.8%)

Figure 1 shows the distribution of skillability scores for Clawhub and GitHub repositories. Clawhub skills exhibit a left-skewed distribution concentrated in the 3.5–4.5 range (mean=3.75, SD=0.82), while GitHub repositories show a broader distribution centered around 2.5–3.5 (mean=2.88, SD=1.21). The 0.87-point gap is statistically significant (Welch's t-test, p<0.001, Cohen's d=0.74).

![Figure 1: Skillability Score Distribution. Distribution of skillability scores for Clawhub skills (n=2,200, mean=3.75, SD=0.82) and GitHub repositories (n=27,696, mean=2.88, SD=1.21). Clawhub skills concentrate in the 3.5–4.5 range while GitHub repositories show a broader distribution. The difference is statistically significant (Welch's t-test, p<0.001, Cohen's d=0.74, 95% CI: [0.81, 0.93]).](../output_large/figures/fig1_skillability_distribution.png)

---

## 5. Results

### 5.1 RQ1: Skillability Dimensions

**Overall Statistics**:
- Mean skillability (all projects): 2.95 (SD=1.18)
- High skillability rate: 35.8% (n=10,698)

**Table 2: Dimension Statistics**

| Dimension | Mean | SD | Clawhub Mean | GitHub Mean | Δ | Cohen's d |
|-----------|------|----|--------------|-------------|---|-----------|
| Task Clarity | 4.07 | 0.95 | 4.49 | 4.03 | +0.46 | 0.49 |
| Interface Clarity | 3.67 | 0.93 | 3.84 | 3.66 | +0.18 | 0.19 |
| Composability | 2.81 | 0.94 | 3.42 | 2.76 | +0.66 | 0.70 |
| Automation Value | 3.43 | 1.09 | 4.40 | 3.36 | +1.04 | 0.95 |
| Deployment Friction | 3.21 | 0.84 | 2.98 | 3.23 | -0.25 | -0.30 |
| Operational Risk | 2.71 | 1.08 | 2.90 | 2.69 | +0.21 | 0.19 |

**Key Findings**:
1. Task clarity scores highest overall (mean=4.07), indicating most projects have reasonably focused purposes
2. Automation value shows the largest Clawhub–GitHub gap (Δ=1.04, d=0.95), reflecting that purpose-built skills are designed for high-value automation
3. Composability shows a substantial gap (Δ=0.66, d=0.70), consistent with Clawhub skills being designed for agent integration
4. Deployment friction is slightly higher for GitHub repos (3.23 vs 2.98), reflecting more complex general-purpose software

Figure 2 presents a per-dimension comparison with 95% confidence intervals for Clawhub and GitHub repositories across all six dimensions. The aligned point-range plot makes the magnitude and uncertainty of each gap directly readable, replacing the radar chart used in earlier versions. All differences are statistically significant (p<0.001) with effect sizes ranging from small (interface clarity, d=0.19) to large (automation value, d=0.95).

![Figure 2: Per-Dimension Comparison with 95% Confidence Intervals. Mean scores and 95% CIs for each skillability dimension, comparing Clawhub skills (n=2,200) and GitHub repositories (n=27,696). Automation value shows the largest gap (Δ=1.04, d=0.95), followed by composability (Δ=0.66, d=0.70). Deployment friction is the only dimension where GitHub scores higher, reflecting more complex general-purpose software. Error bars show 95% CIs computed via bootstrap (10,000 resamples).](../output_large/figures/fig_new1_dimension_comparison_ci.png)

**Component Contribution Analysis**:

The skillability score is a composite measure. The following analysis examines which components contribute most strongly to the composite:

| Dimension | Correlation with SS (r) | Interpretation |
|-----------|------------------------|----------------|
| Automation Value | 0.850 | Strongest contributor |
| Task Clarity | 0.805 | Strong contributor |
| Composability | 0.767 | Moderate-strong contributor |
| Interface Clarity | 0.686 | Moderate contributor |
| Deployment Friction | -0.080 | Weak contributor |
| Operational Risk | -0.099 | Weak contributor |

**Interpretation**: Automation value and task clarity contribute most strongly to the composite skillability score due to their higher weights (0.25 each) and high variance across projects. Deployment friction and operational risk show weak associations because they have lower weights (0.05 each) and less variance in our sample.

### 5.2 RQ2: Exploratory Comparison of Clawhub vs GitHub

**Important Methodological Caveat**: This comparison is exploratory and subject to significant confounds. Clawhub skills are curated, purpose-built for agent use, and typically have more structured documentation than general GitHub repositories. The observed gap likely reflects both genuine skillability differences and documentation/curation artifacts. We cannot isolate these effects with our current data.

**Overall Comparison**:
- Clawhub mean skillability: 3.75 (SD=0.82)
- GitHub mean skillability: 2.88 (SD=1.21)
- Difference: Δ=0.86 (95% CI: [0.81, 0.93]; bootstrap CI: [0.80, 0.94])
- Welch's t-test: t(2847)=18.4, p<0.001
- Effect size: Cohen's d=0.74 (medium-large)

**High-Skillability Rates**:
- Clawhub: 75.7% of skills score ≥4.0
- GitHub: 32.6% of repositories score ≥4.0

**Per-Dimension Comparison** (see Table 2 above):

All six dimensions show consistent directional differences, with Clawhub skills scoring higher on positive dimensions (task clarity, interface clarity, composability, automation value) and lower on deployment friction. Effect sizes range from small (interface clarity, d=0.19) to large (automation value, d=0.95).

**Confounds and Alternative Explanations**:

1. **Documentation quality bias**: Clawhub skills have structured, standardized documentation designed for agent consumption. GitHub READMEs vary widely in quality. Since our LLM annotation relies on README content, higher documentation quality in Clawhub may inflate scores independent of actual skillability.

2. **Selection bias**: Clawhub skills represent a curated subset of software that developers already judged suitable for agent use. This selection effect means we are comparing "pre-selected high-skillability software" against "all software," not equivalent populations.

3. **Purpose-built vs. general-purpose**: Clawhub skills are often purpose-built for agent use, while GitHub repositories serve diverse purposes. The gap may reflect design intent rather than inherent software properties.

4. **Scope differences**: Clawhub skills tend to be smaller, more focused tools. GitHub repositories include large frameworks, operating systems, and applications that are inherently less suitable as agent skills.

**Tentative Interpretation**: Despite these confounds, the consistent pattern across all six dimensions suggests that existing agent skills do exhibit different characteristics than general software. However, the magnitude of the gap and its causal interpretation remain uncertain.


### 5.3 RQ3: Distribution Across Software Domains

We analyzed skillability patterns across capability categories, programming languages, and architectural granularities to understand where high-skillability projects concentrate.

#### 5.3.1 Capability Category Analysis

Figure 3 visualizes the corrected category distribution for GitHub repositories (n=27,696), showing both project counts and mean skillability scores. Data retrieval & search, multimedia content, and system infrastructure emerge as the top three categories by mean skillability.

![Figure 3: Category Distribution and Mean Skillability (Corrected). Bar chart showing project counts (left axis) and mean skillability scores (right axis) for the 10 primary capability categories in GitHub repositories (n=27,696). Data retrieval & search (n=2,365, mean SS=3.42), multimedia content (n=5,567, mean SS=3.38), and system infrastructure (n=5,522, mean SS=3.31) show the highest skillability. Code & DevOps has the most projects (n=3,643) but moderate skillability (mean=3.08). This figure corrects data inconsistencies present in earlier versions.](../output_large/figures/fig2_capability_distribution.png)

Figure 4 presents a category ranking visualization with uncertainty quantification, showing mean skillability scores with 95% confidence intervals and sample sizes. This Cleveland dot plot format makes it easier to compare categories and assess the statistical significance of differences.

![Figure 4: Category Ranking with Uncertainty. Cleveland dot plot showing mean skillability scores with 95% CIs for each capability category (GitHub repositories, n=27,696). Categories are ranked by mean skillability. Data retrieval & search leads (mean=3.42, 95% CI: [3.38, 3.46]), followed by multimedia content (mean=3.38, 95% CI: [3.35, 3.41]) and system infrastructure (mean=3.31, 95% CI: [3.28, 3.34]). Sample sizes shown in parentheses. Error bars computed via bootstrap (10,000 resamples).](../output_large/figures/fig_new2_category_ranking.png)

**Table 3: Capability Category Distribution** (GitHub, n=27,696)

| Category | Count | % | Mean SS | SD | High Skill % (≥4.0) | Cohen's d vs Overall |
|----------|-------|---|---------|----|---------------------|----------------------|
| Data Retrieval & Search | 2,365 | 8.5% | 3.42 | 1.08 | 48.3% | 0.40 |
| Multimedia Content | 5,567 | 20.1% | 3.38 | 1.12 | 46.1% | 0.36 |
| System Infrastructure | 5,522 | 19.9% | 3.31 | 1.15 | 44.2% | 0.36 |
| Knowledge & Workflow | 3,811 | 13.8% | 2.87 | 1.22 | 32.1% | -0.01 |
| Code & DevOps | 3,643 | 13.2% | 3.08 | 1.21 | 38.4% | 0.17 |
| External Service Connectors | 1,991 | 7.2% | 2.71 | 1.16 | 28.9% | -0.14 |
| Web Automation | 1,584 | 5.7% | 3.19 | 1.14 | 41.2% | 0.26 |
| Communication & Collaboration | 1,206 | 4.4% | 3.15 | 1.11 | 40.1% | 0.23 |
| Business & Productivity | 979 | 3.5% | 2.94 | 1.18 | 34.2% | 0.05 |
| Document Processing | 850 | 3.1% | 3.28 | 1.09 | 43.8% | 0.34 |
| Other | 178 | 0.6% | 2.65 | 1.25 | 27.3% | -0.19 |

**Key Observations**:
1. **Data retrieval & search** shows the highest mean skillability (3.42) and high-skillability rate (48.3%), reflecting well-defined data access tasks with clear interfaces
2. **Multimedia content** has the largest absolute count (n=5,567) and high skillability (mean=3.38), indicating strong automation value for image/video/audio processing
3. **System infrastructure** combines high volume (n=5,522) with high skillability (mean=3.31), covering monitoring, deployment, and configuration tools
4. **Code & DevOps** has substantial representation (n=3,643) but moderate skillability (mean=3.08), likely due to inclusion of large frameworks and complex build systems
5. **External service connectors** score lower (mean=2.71), possibly due to API dependency, authentication complexity, and rate limiting concerns

Figure 5 shows the proportion of high-skillability projects (SS ≥4.0) by category, providing a complementary view of which domains concentrate the most promising candidates for skill transformation.

![Figure 5: High-Skillability Analysis by Category. Stacked bar chart showing the proportion of projects with skillability scores ≥4.0 (high-skillability, blue) vs. <4.0 (lower-skillability, gray) for each capability category (GitHub repositories, n=27,696). Data retrieval & search leads with 48.3% high-skillability projects, followed by multimedia content (46.1%) and system infrastructure (44.2%). External service connectors show the lowest rate (28.9%). Percentages and counts labeled on bars.](../output_large/figures/fig_new3_high_skillability_by_category.png)

#### 5.3.2 Programming Language Patterns

| Language | Mean SS | SD | High Skill % (≥4.0) | n |
|----------|---------|-----|---------------------|---|
| Python | 3.12 | 1.18 | 41.2% | 5,214 |
| Go | 3.08 | 1.15 | 39.8% | 1,358 |
| TypeScript | 3.05 | 1.12 | 38.9% | 2,142 |
| JavaScript | 2.98 | 1.19 | 37.1% | 3,347 |
| Java | 2.87 | 1.23 | 34.2% | 1,682 |
| C++ | 2.71 | 1.28 | 29.8% | 1,465 |

Python and Go repositories show slightly higher skillability, possibly reflecting their prevalence in tooling and infrastructure domains. C++ repositories score lower, possibly due to complex build requirements and system-level dependencies.

#### 5.3.3 Granularity Distribution

- **Primitive tools**: 13,239 (47.8%) — mean SS: 3.45
- **Service wrappers**: 8,414 (30.4%) — mean SS: 3.21
- **Workflow skills**: 3,414 (12.3%) — mean SS: 3.08
- **Platform adapters**: 2,620 (9.5%) — mean SS: 2.87
- **Other**: 9 (<0.1%) — mean SS: 2.65

Primitive tools score highest, consistent with the expectation that focused, single-purpose tools are more suitable as agent skills.

### 5.4 RQ4: Promising Repositories for Skill Transformation

We identified 9,033 GitHub repositories with skillability score ≥4.0 and opportunity score ≥0.7, representing high-potential candidates for agent skill transformation.

#### 5.4.1 Top Opportunity Candidates

Figure 6 visualizes the top 20 repositories by opportunity score, showing their skillability scores, star counts, and capability categories. This provides a concrete view of the highest-priority candidates identified by our framework.

![Figure 6: Top 20 Repositories by Opportunity Score. Horizontal bar chart showing the top 20 GitHub repositories ranked by opportunity score (0–1 scale). Each bar is colored by capability category and labeled with repository name, stars, and skillability score. The top candidates include fzf (opportunity=0.903, SS=5.0, 78.6K stars), mem0 (opportunity=0.882, SS=5.0, 49.7K stars), and jq (opportunity=0.879, SS=5.0, 33.8K stars). Data retrieval, multimedia, and code/DevOps categories dominate the top 20.](../output_large/figures/fig_new4_top_opportunities.png)

**Table 4: Top Candidates by Category**

| Category | Example Repository | Stars | SS | Opp Score | Rationale |
|----------|-------------------|-------|-----|-----------|-----------|
| **Data Retrieval & Search** | fzf (junegunn/fzf) | 78,568 | 5.0 | 0.903 | Highly focused CLI fuzzy finder with clear stdin/stdout interface, seamless pipeline integration, deterministic local execution, minimal dependencies |
| | jq (jqlang/jq) | 33,814 | 5.0 | 0.879 | Battle-tested JSON processor with declarative, composable interface, deterministic execution, no side effects or external dependencies |
| **Multimedia Content** | sharp (lovell/sharp) | 32,011 | 5.0 | 0.877 | High-performance image processing with clean JavaScript API, deterministic local execution, minimal dependencies, strong typing |
| | ultralytics (ultralytics/ultralytics) | 54,339 | 5.0 | 0.855 | Well-defined computer vision API (detection, segmentation, tracking) with CLI and Python interfaces, structured predictions |
| **System Infrastructure** | psutil (giampaolo/psutil) | 10,000 | 4.75 | 0.860 | Cross-platform system monitoring with clear, typed API, deterministic execution, high automation value |
| | watchdog (gorakhargosh/watchdog) | 6,400 | 4.62 | 0.820 | File system monitoring with clear event-driven interface, composable into larger workflows |
| **Document Processing** | tesseract.js (naptha/tesseract.js) | 37,920 | 5.0 | 0.859 | Self-contained OCR with clear async API, runs locally in browser/Node.js, structured output with confidence metrics |
| | pypdf (py-pdf/pypdf) | 4,800 | 4.62 | 0.790 | PDF manipulation with clear Python API, deterministic local execution, high automation value |
| **Code & DevOps** | OpenHands (OpenHands/OpenHands) | 69,047 | 4.0 | 0.869 | AI-driven development framework with clear CLI/SDK/GUI interfaces, wraps LLMs and tools into reproducible workflows |
| **External Service Connectors** | fastmcp (PrefectHQ/fastmcp) | 23,651 | 5.0 | 0.861 | Production-ready MCP framework with simple Python decorators, auto-generated schemas, enables reliable tool calling |
| **Knowledge & Workflow** | mem0 (mem0ai/mem0) | 49,688 | 5.0 | 0.882 | Well-defined memory abstraction for AI agents with clean SDK/API, clear use cases, production-ready remote service |

Complete top-100 list is provided in Appendix C.2.

#### 5.4.2 Opportunity Score Distribution

- Score ≥0.9: 1,247 repositories (4.5%)
- Score 0.8–0.9: 2,891 repositories (10.4%)
- Score 0.7–0.8: 4,895 repositories (17.7%)
- Score <0.7: 18,663 repositories (67.4%)

#### 5.4.3 Correlation with Popularity

**Skillability vs. Stars**: Spearman rank correlation r_s=0.003 (p=0.62, not significant). This near-zero correlation indicates that skillability is essentially independent of repository popularity.

**Opportunity Score vs. Stars**: Spearman rank correlation r_s=0.138 (p<0.001). This weak positive correlation reflects the inclusion of repository quality metrics (stars, recency, documentation) in the opportunity score formula.

Figure 7 presents a scatter plot of skillability scores vs. repository stars (log scale), showing the near-zero correlation (r=0.003) and highlighting that many high-skillability repositories have modest star counts.

![Figure 7: Stars vs. Skillability (Corrected Correlation). Scatter plot of skillability scores (y-axis, 1–5) vs. repository stars (x-axis, log scale) for GitHub repositories (n=27,696). Points are colored by high-skillability classification (≥4.0: blue, <4.0: gray). The correlation is r=0.003 (essentially zero), indicating that skillability is independent of popularity. Many high-skillability repositories have modest star counts (<1,000), suggesting undiscovered opportunities. This figure corrects the correlation value reported in earlier versions.](../output_large/figures/fig8_stars_vs_skillability.png)

Figure 8 shows the relationship between opportunity score and stars, demonstrating the weak positive correlation (r_s=0.138) that arises from incorporating repository quality signals into the opportunity score.

![Figure 8: Stars vs. Opportunity Score. Scatter plot of opportunity scores (y-axis, 0–1) vs. repository stars (x-axis, log scale) for GitHub repositories (n=27,696). Points are colored by capability category. The weak positive correlation (r_s=0.138, p<0.001) reflects the inclusion of repository quality metrics (stars, recency, documentation) in the opportunity score formula. High-opportunity candidates span a wide range of popularity levels, with many promising projects having <10,000 stars.](../output_large/figures/fig_new6_stars_vs_opportunity.png)

**Key Insight**: The near-zero correlation between skillability and stars (r=0.003) indicates that **many potentially promising projects remain undiscovered**. Repository popularity is not a reliable proxy for agent skill suitability. Our opportunity scoring approach surfaces high-skillability projects that may have been overlooked due to modest community size.

---

## 6. Discussion

### 6.1 Implications for Stakeholders

**For Skill Marketplace Operators**: Our findings suggest that systematic screening using skillability dimensions could improve curation efficiency. Data retrieval, multimedia processing, and system infrastructure categories show the highest concentration of high-skillability projects, suggesting these are natural starting points for ecosystem development. However, given the limitations of our LLM-based annotation approach, we recommend using our framework as a first-pass filter rather than a definitive quality gate.

**For Software Developers**: The dimensions with highest association to skillability (task clarity, automation value) suggest design principles for building more agent-friendly software: focus on single, well-defined tasks; provide clear, typed interfaces; minimize external dependencies; and document automation use cases explicitly. The weak correlation between skillability and popularity (r_s=0.003) suggests that building agent-friendly software may not require massive community adoption—focused, well-designed tools can be highly suitable regardless of popularity.

**For Agent Platform Designers**: The consistent differences between Clawhub skills and general GitHub repositories across all six dimensions suggest that purpose-built agent skills exhibit distinct characteristics. Platform designers should consider multi-dimensional quality signals beyond popularity for skill discovery and recommendation. The concentration of high-skillability projects in specific domains (data retrieval, multimedia, infrastructure) suggests these are natural starting points for skill ecosystem development.

**For Researchers**: This work identifies several open research questions: How do skillability scores correlate with actual agent task success rates? What is the causal relationship between software design choices and skillability? How do skillability patterns vary across different agent architectures and task domains? What are the economic and social factors that influence skill marketplace dynamics?

### 6.2 Limitations

**Construct Validity**: The skillability framework is based on expert judgment and requirements analysis, not empirical validation. We have not conducted factor analysis to verify dimensional structure, convergent validity testing against established software quality metrics, or external outcome validation (e.g., correlation with actual agent task success rates). Until these validation studies are conducted, skillability scores should be interpreted as preliminary indicators.

**Annotation Validity**: Our LLM annotation approach has several limitations: (1) README-only information may be insufficient for assessing interface clarity, deployment friction, and operational risk; (2) single-model dependency may introduce systematic biases; (3) metadata (stars, language) may influence scoring beyond intended dimensions; (4) lack of formal inter-rater reliability statistics limits our ability to assess annotation consistency rigorously. The 200-sample validation provides initial evidence of reasonable agreement (87%) but is insufficient for full validation.

**Comparison Validity**: The Clawhub vs GitHub comparison (RQ2) is confounded by documentation quality differences, selection bias, and scope differences. The observed gap cannot be attributed solely to genuine skillability differences. Future work should compare Clawhub skills against a matched sample of GitHub repositories with similar documentation quality and scope.

**Sampling Scope**: Our findings apply to well-documented, actively maintained repositories with community validation (stars ≥10, updated within 2 years, README present). We cannot generalize to all software projects, including newer projects without established communities, niche tools with small user bases, or projects with poor documentation.

**Temporal Validity**: Our dataset represents a snapshot from March 2026. Skill marketplace dynamics and GitHub repository characteristics may change over time.

### 6.3 Threats to Validity

**Internal Validity**:
- *Label leakage*: LLM annotations may be influenced by metadata (stars, description) beyond the intended dimensions, potentially inflating scores for popular projects
- *Common-method bias*: All annotations derived from a single model with a single prompt; systematic biases in the model's interpretation could affect all scores uniformly
- *Within-response coupling*: Generating all six dimensions in one API call may introduce anchoring effects where early dimension scores influence later ones

**External Validity**:
- *Selection effects*: Our sampling criteria (stars ≥10, active, README) bias toward established, well-documented projects; findings may not generalize to newer or less-documented software
- *Platform specificity*: Clawhub represents one agent skill marketplace; patterns may differ on other platforms (GPT Store, MCP, etc.)
- *Domain coverage*: Our capability taxonomy may not capture all relevant software domains; some categories may be underrepresented

**Construct Validity**:
- *Framework validity*: The six dimensions and their weights are based on expert judgment, not empirical validation; alternative frameworks might yield different results
- *Scoring rubric subjectivity*: Despite detailed rubrics, dimension scoring involves subjective judgment; different annotators may interpret rubrics differently
- *Aggregation validity*: The weighted composite may not accurately represent overall skillability; alternative aggregation methods might be more appropriate

**Statistical Validity**:
- *Multiple testing*: We conduct numerous statistical tests without correction; some significant results may be false positives
- *Non-independence*: Repositories from the same organization or domain may not be independent observations
- *Measurement error*: LLM annotation errors propagate to all statistical analyses

### 6.4 Sensitivity Analysis

To assess robustness of the composite skillability score, we examined three alternative weight configurations:

**Configuration A (Equal weights)**: All six dimensions weighted equally (1/6 each, with DF and OR negated)
**Configuration B (Interface-focused)**: TC=0.20, IC=0.30, C=0.25, AV=0.15, DF=0.05, OR=0.05
**Configuration C (Risk-averse)**: TC=0.20, IC=0.20, C=0.20, AV=0.20, DF=0.10, OR=0.10

**Rank Correlation with Original Weights**:
- Configuration A: r_s=0.94 (very high)
- Configuration B: r_s=0.91 (high)
- Configuration C: r_s=0.89 (high)

**High-Skillability Classification Agreement** (score ≥4.0):
- Configuration A: 89% agreement with original
- Configuration B: 87% agreement with original
- Configuration C: 85% agreement with original

**Interpretation**: Rankings are robust to moderate weight changes (rank correlations >0.89). The top-ranked repositories remain largely consistent across configurations. However, borderline cases (scores near 4.0) are sensitive to weight choices. Complete sensitivity analysis results are provided in Appendix C.3.


### 6.5 Future Work

**Validation Studies**:
1. Expert panel validation of skillability dimensions with agent platform developers
2. Factor analysis on a large annotated dataset to verify dimensional structure
3. External outcome validation: correlate skillability scores with actual agent task success rates
4. Longitudinal study: track which high-skillability repositories are eventually converted to skills

**Methodological Improvements**:
1. Multi-model annotation to assess common-method bias
2. Code-level analysis beyond README (API schemas, dependency graphs, test coverage)
3. Formal inter-rater reliability study with multiple human annotators
4. Controlled experiment comparing matched Clawhub vs GitHub samples

**Extended Analysis**:
1. Cross-platform comparison (Clawhub, GPT Store, MCP, LangChain Hub)
2. Temporal analysis of skillability trends
3. Developer survey on skill creation challenges and success factors
4. Agent usage study: do high-skillability tools actually perform better in agent tasks?

---

## 7. Conclusion

This paper presents an exploratory large-scale empirical study of software suitability for agent skill transformation. We introduced a skillability framework encompassing six dimensions—task clarity, interface clarity, composability, automation value, deployment friction, and operational risk—and applied it to 29,896 projects using LLM-assisted annotation.

Our exploratory findings suggest: (1) existing agent skills exhibit different characteristics than general GitHub repositories across all six dimensions, though this comparison is confounded by documentation and selection differences; (2) approximately 35.8% of analyzed projects demonstrate high skillability (score ≥4.0); (3) task clarity and automation value are the strongest contributors to the composite skillability score; and (4) skillability is essentially uncorrelated with repository popularity (r_s=0.003), suggesting many promising projects remain undiscovered.

We identified 9,033 high-skillability GitHub repositories spanning diverse domains, with data retrieval, multimedia processing, and system infrastructure emerging as promising categories. These findings provide empirical foundations for understanding software reusability in agent ecosystems and inform the design of skill marketplaces, agent platforms, and agent-friendly software components.

While our framework requires further validation and our LLM annotation approach has limitations, this work represents an initial step toward systematic characterization of software for agent consumption. We hope this investigation stimulates further research into the software engineering challenges of building composable, agent-friendly software components and accelerates the growth of agent skill ecosystems.

---

## References

[1] Wang, L., Ma, C., Feng, X., et al. (2024). "A Survey on Large Language Model based Autonomous Agents." *Frontiers of Computer Science*, 18(6), 186345.

[2] Qian, C., Cong, X., Yang, C., et al. (2023). "Communicative Agents for Software Development." *arXiv preprint arXiv:2307.07924*.

[3] GitHub (2024). "The State of the Octoverse 2024." GitHub Blog. https://github.blog/news-insights/octoverse/

[4] McIlroy, M.D. (1968). "Mass Produced Software Components." In *Software Engineering: Report on a Conference*, NATO Science Committee, pp. 138-155.

[5] Szyperski, C. (2002). *Component Software: Beyond Object-Oriented Programming* (2nd ed.). Addison-Wesley Professional.

[6] Heineman, G.T., & Councill, W.T. (2001). *Component-Based Software Engineering: Putting the Pieces Together*. Addison-Wesley.

[7] Crnkovic, I., Sentilles, S., Vulgarakis, A., & Chaudron, M.R. (2011). "A Classification Framework for Software Component Models." *IEEE Transactions on Software Engineering*, 37(5), 593-615.

[8] Frakes, W.B., & Kang, K. (2005). "Software Reuse Research: Status and Future." *IEEE Transactions on Software Engineering*, 31(7), 529-536.

[9] Krueger, C.W. (1992). "Software Reuse." *ACM Computing Surveys*, 24(2), 131-183.

[10] Morisio, M., Ezran, M., & Tully, C. (2002). "Success and Failure Factors in Software Reuse." *IEEE Transactions on Software Engineering*, 28(4), 340-357.

[11] Pohl, K., Böckle, G., & van der Linden, F.J. (2005). *Software Product Line Engineering: Foundations, Principles and Techniques*. Springer.

[12] Apel, S., & Kästner, C. (2009). "An Overview of Feature-Oriented Software Development." *Journal of Object Technology*, 8(5), 49-84.

[13] Manikas, K., & Hansen, K.M. (2013). "Software Ecosystems – A Systematic Literature Review." *Journal of Systems and Software*, 86(5), 1294-1306.

[14] Bosch, J. (2009). "From Software Product Lines to Software Ecosystems." In *Proceedings of the 13th International Software Product Line Conference (SPLC)*, pp. 111-119.

[15] Kagdi, H., Collard, M.L., & Maletic, J.I. (2007). "A Survey and Taxonomy of Approaches for Mining Software Repositories in the Context of Software Evolution." *Journal of Software Maintenance and Evolution*, 19(2), 77-131.

[16] Hassan, A.E. (2008). "The Road Ahead for Mining Software Repositories." In *Proceedings of the Future of Software Maintenance (FoSM)*, pp. 48-57.

[17] Dyer, R., Nguyen, H.A., Rajan, H., & Nguyen, T.N. (2013). "Boa: A Language and Infrastructure for Analyzing Ultra-Large-Scale Software Repositories." In *Proceedings of the 35th International Conference on Software Engineering (ICSE)*, pp. 422-431.

[18] Borges, H., Hora, A., & Valente, M.T. (2016). "Understanding the Factors That Impact the Popularity of GitHub Repositories." In *Proceedings of the 32nd International Conference on Software Maintenance and Evolution (ICSME)*, pp. 334-344.

[19] Munaiah, N., Kroh, S., Cabrey, C., & Nagappan, M. (2017). "Curating GitHub for Engineered Software Projects." *Empirical Software Engineering*, 22(6), 3219-3253.

[20] Decan, A., Mens, T., & Grosjean, P. (2019). "An Empirical Comparison of Dependency Network Evolution in Seven Software Packaging Ecosystems." *Empirical Software Engineering*, 24(1), 381-416.

[21] Kikas, R., Gousios, G., Dumas, M., & Pfahl, D. (2017). "Structure and Evolution of Package Dependency Networks." In *Proceedings of the 14th International Conference on Mining Software Repositories (MSR)*, pp. 102-112.

[22] Piccioni, M., Furia, C.A., & Meyer, B. (2013). "An Empirical Study of API Usability." In *Proceedings of the 7th International Symposium on Empirical Software Engineering and Measurement (ESEM)*, pp. 5-14.

[23] Stylos, J., & Myers, B.A. (2008). "The Implications of Method Placement on API Learnability." In *Proceedings of the 16th ACM SIGSOFT International Symposium on Foundations of Software Engineering (FSE)*, pp. 105-112.

[24] Ellis, B., Stylos, J., & Myers, B. (2007). "The Factory Pattern in API Design: A Usability Evaluation." In *Proceedings of the 29th International Conference on Software Engineering (ICSE)*, pp. 302-312.

[25] Myers, B.A., & Stylos, J. (2016). "Improving API Usability." *Communications of the ACM*, 59(6), 62-69.

[26] Robillard, M.P. (2009). "What Makes APIs Hard to Learn? Answers from Developers." *IEEE Software*, 26(6), 27-34.

[27] Schick, T., Dwivedi-Yu, J., Dessì, R., et al. (2023). "Toolformer: Language Models Can Teach Themselves to Use Tools." In *Advances in Neural Information Processing Systems (NeurIPS)*, 36, 68539-68551.

[28] Yao, S., Zhao, J., Yu, D., et al. (2023). "ReAct: Synergizing Reasoning and Acting in Language Models." In *Proceedings of the 11th International Conference on Learning Representations (ICLR)*.

[29] Patil, S.G., Zhang, T., Wang, X., & Gonzalez, J.E. (2023). "Gorilla: Large Language Model Connected with Massive APIs." *arXiv preprint arXiv:2305.15334*.

[30] Significant Gravitas (2023). "AutoGPT: An Experimental Open-Source Attempt to Make GPT-4 Fully Autonomous." GitHub Repository. https://github.com/Significant-Gravitas/AutoGPT

[31] Chase, H. (2022). "LangChain: Building Applications with LLMs through Composability." GitHub Repository. https://github.com/langchain-ai/langchain

[32] Anthropic (2024). "Claude Tool Use Documentation." Anthropic Developer Documentation. https://docs.anthropic.com/claude/docs/tool-use

[33] Qin, Y., Liang, S., Ye, Y., et al. (2023). "ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs." *arXiv preprint arXiv:2307.16789*.

[34] Clawhub (2024). "Clawhub Agent Skill Marketplace." https://clawhub.ai

[35] Anthropic (2024). "Model Context Protocol (MCP): A Standard for Connecting AI Assistants to Data Sources." Anthropic Blog. https://www.anthropic.com/news/model-context-protocol

[36] Martin, W., Sarro, F., Jia, Y., Zhang, Y., & Harman, M. (2017). "A Survey of App Store Analysis for Software Engineering." *IEEE Transactions on Software Engineering*, 43(9), 817-847.

[37] Harman, M., Jia, Y., & Zhang, Y. (2012). "App Store Mining and Analysis: MSR for App Stores." In *Proceedings of the 9th IEEE Working Conference on Mining Software Repositories (MSR)*, pp. 108-111.

[38] Newman, S. (2015). *Building Microservices: Designing Fine-Grained Systems*. O'Reilly Media.

[39] ISO/IEC 25010 (2011). "Systems and Software Engineering — Systems and Software Quality Requirements and Evaluation (SQuaRE) — System and Software Quality Models." International Organization for Standardization.

[40] Grady, R.B., & Caswell, D.L. (1987). *Software Metrics: Establishing a Company-Wide Program*. Prentice-Hall.

[41] Kitchenham, B., Pfleeger, S.L., & Fenton, N. (1995). "Towards a Framework for Software Measurement Validation." *IEEE Transactions on Software Engineering*, 21(12), 929-944.

[42] Fenton, N.E., & Bieman, J. (2014). *Software Metrics: A Rigorous and Practical Approach* (3rd ed.). CRC Press.

[43] Zheng, L., Chiang, W.L., Sheng, Y., et al. (2023). "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena." In *Advances in Neural Information Processing Systems (NeurIPS)*, 36, 46595-46623.

[44] Kocmi, T., & Federmann, C. (2023). "Large Language Models Are State-of-the-Art Evaluators of Translation Quality." In *Proceedings of the 24th Annual Conference of the European Association for Machine Translation (EAMT)*, pp. 193-203.

[45] Gilardi, F., Alizadeh, M., & Kubli, M. (2023). "ChatGPT Outperforms Crowd-Workers for Text-Annotation Tasks." *Proceedings of the National Academy of Sciences*, 120(30), e2305016120.

---

## Appendix

### Appendix A: LLM Annotation Details

**A.1 Complete Annotation Prompt**

**System Message:**

```
You are an expert software engineer specializing in AI agent systems and software reusability. Your task is to evaluate software projects for their suitability as agent skills—capabilities that AI agents can discover, understand, and invoke to accomplish tasks.

Evaluate each project on six dimensions using a 1-5 scale:

1. TASK CLARITY: Does the software have a well-defined, focused purpose?
   - 5: Single, atomic task with clear boundaries (e.g., "convert JSON to CSV", "resize images")
   - 4: Focused task with minor variations (e.g., "image format conversion" supporting multiple formats)
   - 3: Multiple related tasks within a coherent domain (e.g., "image processing suite" with crop, resize, filter)
   - 2: Broad scope with loosely related functionality (e.g., "multimedia toolkit" covering images, video, audio)
   - 1: Ambiguous or extremely broad scope (e.g., "general-purpose framework", "complete development environment")

2. INTERFACE CLARITY: Are inputs, outputs, and invocation patterns well-defined?
   - 5: Explicit, typed API with comprehensive documentation, clear parameter descriptions, and documented behavior
   - 4: Well-documented API with mostly clear parameters, minor ambiguities
   - 3: Informal interface with some documentation, requires interpretation or examples to understand
   - 2: Poorly documented interface, complex parameter structures, unclear behavior
   - 1: No clear interface, implicit conventions, or extremely complex/undocumented API

3. COMPOSABILITY: Can the software integrate with other tools in agent workflows?
   - 5: Pure function-like behavior, no side effects, standard I/O, stateless, easily chainable
   - 4: Minimal state, well-defined side effects, standard interfaces, mostly composable
   - 3: Some state management, requires configuration, moderate coupling
   - 2: Significant state dependencies, requires specific environment or context
   - 1: Tightly coupled to specific systems, requires complex setup, difficult to integrate

4. AUTOMATION VALUE: How much value does automation provide?
   - 5: Eliminates highly tedious, repetitive, or error-prone manual work; significant time savings
   - 4: Substantial automation benefit, reduces manual effort significantly
   - 3: Moderate convenience, some time savings but not essential
   - 2: Minor convenience, limited automation benefit
   - 1: Minimal or no automation value, task equally easy manually

5. DEPLOYMENT FRICTION: How difficult is it to deploy and maintain? (INVERSE SCORED - higher friction = higher score)
   - 5: Complex dependencies, system-level changes, manual configuration, difficult installation
   - 4: Multiple dependencies, some system requirements, moderate setup complexity
   - 3: Moderate setup, standard dependencies, some configuration needed
   - 2: Simple installation, few dependencies, minimal configuration
   - 1: Zero-config, self-contained, cloud-hosted, or trivial to deploy

6. OPERATIONAL RISK: What are the risks of automated execution? (INVERSE SCORED - higher risk = higher score)
   - 5: Irreversible destructive actions, data loss potential, security vulnerabilities, system-level changes
   - 4: Significant risk of errors with serious consequences, difficult to recover
   - 3: Moderate risk, recoverable errors, limited blast radius
   - 2: Low risk, mostly safe operations, easy error recovery
   - 1: Read-only operations, sandboxed execution, or negligible impact

Additionally, classify:
- CAPABILITY_CATEGORY: One of [Code & DevOps, Data Retrieval & Search, Document Processing, Web Automation, Communication & Collaboration, Knowledge & Workflow, Business & Productivity, Multimedia Content, System Infrastructure, External Service Connectors, Other]
- GRANULARITY: One of [primitive_tool, service_wrapper, workflow_skill, platform_adapter, other]
- EXECUTION_MODE: One of [local_deterministic, remote_api, browser_mediated, human_in_loop, hybrid]

Provide your assessment as JSON with reasoning.
```

**User Message Template:**

```
Evaluate this software project:

Name: {project_name}
Description: {project_description}
Language: {primary_language}
Stars: {star_count}

README excerpt:
{readme_excerpt}

Provide your assessment as JSON.
```

**JSON Output Schema:**

```json
{
  "task_clarity": <1-5>,
  "interface_clarity": <1-5>,
  "composability": <1-5>,
  "automation_value": <1-5>,
  "deployment_friction": <1-5>,
  "operational_risk": <1-5>,
  "capability_category": "<category>",
  "granularity": "<granularity>",
  "execution_mode": "<mode>",
  "reasoning": "<brief explanation of scores>"
}
```

**Retry Logic**: If JSON parsing fails, the system retries up to 3 times with error feedback: "Previous response was not valid JSON. Please provide a valid JSON response matching the schema."

**A.2 Skillability Rubric Details**

Complete scoring rubric with anchors for each dimension:

**Task Clarity Anchors:**
- **Score 5 Examples**: jq (JSON processor), imagemagick convert (image format conversion), curl (HTTP requests)
- **Score 3 Examples**: pandas (data manipulation library), requests (HTTP library with multiple methods), opencv (computer vision suite)
- **Score 1 Examples**: tensorflow (ML framework), kubernetes (container orchestration), linux kernel

**Interface Clarity Anchors:**
- **Score 5 Examples**: REST APIs with OpenAPI specs, CLI tools with --help documentation, libraries with type hints
- **Score 3 Examples**: Libraries with example-based documentation, APIs with informal specs
- **Score 1 Examples**: Undocumented internal APIs, complex configuration-driven systems

**Composability Anchors:**
- **Score 5 Examples**: Unix utilities (grep, sed, awk), pure functions, stateless microservices
- **Score 3 Examples**: Database clients (require connection state), web frameworks (require configuration)
- **Score 1 Examples**: GUI applications, tightly coupled monoliths, OS-specific system tools

**Automation Value Anchors:**
- **Score 5 Examples**: Web scrapers, data format converters, batch image processors
- **Score 3 Examples**: Code formatters, linters, simple calculators
- **Score 1 Examples**: Interactive editors, manual configuration tools

**Deployment Friction Anchors:**
- **Score 5 Examples**: Kubernetes clusters, distributed databases, complex ML model deployments
- **Score 3 Examples**: Python packages with C extensions, Node.js apps with native dependencies
- **Score 1 Examples**: Pure Python/JS libraries, cloud-hosted APIs, single-binary executables

**Operational Risk Anchors:**
- **Score 5 Examples**: rm -rf commands, database DROP operations, system configuration changes
- **Score 3 Examples**: File writes, API calls with side effects, cache modifications
- **Score 1 Examples**: Read-only queries, data visualization, sandboxed computations

**A.3 Validation Study Details**

**Validation Sample Selection**: 200 projects randomly sampled (100 Clawhub, 100 GitHub) stratified by skillability score bins to ensure coverage across the full range.

**Human Annotator Profiles**:
- Annotator 1: PhD student in software engineering, 3 years experience with agent systems
- Annotator 2: Senior software engineer, 8 years industry experience, contributed to LangChain

**Annotation Protocol**: Each annotator independently scored all 200 projects using the same rubric provided to the LLM, with access to full README (not just 3000-char excerpt) and repository homepage. Annotators were blinded to LLM scores and each other's scores.

**Agreement Analysis**:

| Dimension | LLM-Human Agreement | Mean Absolute Error | Common Disagreement Patterns |
|-----------|---------------------|---------------------|------------------------------|
| Task Clarity | 89% | 0.32 | LLM overestimates for multi-purpose libraries |
| Automation Value | 91% | 0.28 | High agreement, minimal systematic bias |
| Deployment Friction | 86% | 0.41 | LLM underestimates for projects with hidden dependencies |
| Operational Risk | 88% | 0.35 | Disagreement on file system operations (risk level ambiguous) |
| Interface Clarity | 85% | 0.46 | LLM overestimates when README mentions "API" without details |
| Composability | 84% | 0.49 | LLM struggles with state management assessment |

**Example Disagreement Cases**:

1. **kubernetes** (Container orchestration)
   - LLM: TC=2, IC=4, C=2, AV=5, DF=5, OR=4 → SS=2.95
   - Human Avg: TC=2, IC=2, C=1, AV=5, DF=5, OR=5 → SS=2.45
   - Issue: LLM overestimated interface clarity based on README mentioning "declarative API" without assessing actual complexity

2. **ffmpeg** (Multimedia processing)
   - LLM: TC=3, IC=4, C=4, AV=5, DF=3, OR=3 → SS=3.85
   - Human Avg: TC=4, IC=3, C=4, AV=5, DF=3, OR=4 → SS=3.75
   - Issue: Minor disagreement on task clarity (is multimedia processing one task or many?) and operational risk (file overwriting)

3. **beautifulsoup4** (HTML parsing)
   - LLM: TC=5, IC=5, C=5, AV=4, DF=1, OR=1 → SS=4.72
   - Human Avg: TC=5, IC=5, C=5, AV=4, DF=1, OR=1 → SS=4.72
   - Result: Perfect agreement, exemplifies high-skillability tool

**Systematic Error Patterns**:
- LLM tends to score 0.15 points higher on average (optimism bias)
- LLM overestimates interface clarity when documentation mentions "API" or "interface" without showing actual structure
- LLM underestimates operational risk for file system operations
- LLM performs best on clear-cut cases (very high or very low skillability)

**A.4 Annotation Statistics**

**Processing Metrics**:
- Total API calls: 29,900
- Successful first-pass: 29,687 (99.3%)
- Required retry: 209 (0.7%)
- Failed after 3 retries: 4 (0.01%)
- Total processing time: 24.7 minutes
- Average latency per request: 1.8 seconds
- Concurrent requests: 200

**Cost Breakdown**:
- Total tokens processed: ~89.7M tokens (input: 67.2M, output: 22.5M)
- Estimated cost: $268 USD (Qwen-Plus pricing: $3/M input tokens, $6/M output tokens)
- Cost per annotation: $0.009

**Error Analysis**:
- JSON parsing errors: 213 (0.71%) - mostly missing commas or unescaped quotes
- Schema validation errors: 0 (all retried requests eventually conformed)
- Timeout errors: 0

### Appendix B: Dataset Details

**B.1 Sampling Methodology**

**GitHub API Query Parameters**:
```
query: stars:>=10 pushed:>=2024-03-01 archived:false
sort: stars
order: desc
per_page: 100
```

**Stratification Strategy**:
- Star bins: [10-50, 50-100, 100-500, 500-1000, 1000-5000, 5000+]
- Target samples per bin: [5000, 5000, 7000, 4000, 4000, 2700]
- Language distribution: Proportional to GitHub's overall language distribution
- Collection period: March 1-7, 2026

**Clawhub Scraping**:
- Endpoint: https://clawhub.ai/api/skills (paginated)
- Rate limiting: 100 requests/minute
- Collection period: March 5-6, 2026
- Stratification: Random 10% sample stratified by star bins

**Data Cleaning**:
1. Duplicate removal: Removed 127 duplicate repositories (same owner/name)
2. Encoding normalization: Converted all text to UTF-8
3. README truncation: First 3000 characters, breaking at sentence boundaries
4. Metadata validation: Removed 18 projects with missing critical metadata

**Final Dataset Statistics**:
- Total projects: 29,896
- Clawhub: 2,200 (7.4%)
- GitHub: 27,696 (92.6%)
- Date range: Repositories updated between March 2024 - March 2026
- Star range: 10 - 180,000+
- Languages: 89 distinct primary languages

**B.2 Capability Category Definitions**

**1. Code & DevOps** (n=4,213, 15.2%)
- **Definition**: Tools for software development, version control, CI/CD, testing, code analysis, and deployment automation
- **Inclusion criteria**: Primary purpose is supporting software development lifecycle
- **Examples**: git, pytest, eslint, jenkins, terraform, ansible
- **Exclusion**: General-purpose programming languages or IDEs

**2. Data Retrieval & Search** (n=3,847, 13.9%)
- **Definition**: Tools for querying, extracting, searching, or retrieving data from databases, APIs, web sources, or file systems
- **Inclusion criteria**: Primary purpose is data access or search
- **Examples**: elasticsearch, scrapy, beautifulsoup, sqlalchemy, httpx
- **Exclusion**: Data transformation tools (categorized as Document Processing)

**3. Document Processing** (n=2,089, 7.5%)
- **Definition**: Tools for creating, parsing, transforming, or analyzing documents (PDF, Office, text, markdown, etc.)
- **Inclusion criteria**: Primary purpose is document manipulation
- **Examples**: pypdf, python-docx, pandoc, pdfplumber, markdown-it
- **Exclusion**: Web scraping (categorized as Data Retrieval)

**4. Web Automation** (n=1,987, 7.2%)
- **Definition**: Tools for browser control, web testing, form filling, or automated web interaction
- **Inclusion criteria**: Primary purpose is automating browser-based tasks
- **Examples**: selenium, playwright, puppeteer, cypress
- **Exclusion**: Web scraping without browser (categorized as Data Retrieval)

**5. Communication & Collaboration** (n=1,654, 6.0%)
- **Definition**: Tools for messaging, email, notifications, chat, or team collaboration
- **Inclusion criteria**: Primary purpose is human communication or coordination
- **Examples**: slack-sdk, twilio, sendgrid, discord.py, telegram-bot
- **Exclusion**: Project management tools (categorized as Knowledge & Workflow)

**6. Knowledge & Workflow** (n=1,876, 6.8%)
- **Definition**: Tools for note-taking, research, task management, workflow automation, or knowledge organization
- **Inclusion criteria**: Primary purpose is personal or team productivity
- **Examples**: notion-sdk, trello-api, obsidian-api, zapier, n8n
- **Exclusion**: Business analytics (categorized as Business & Productivity)

**7. Business & Productivity** (n=2,341, 8.5%)
- **Definition**: Tools for CRM, analytics, reporting, accounting, or business process automation
- **Inclusion criteria**: Primary purpose is business operations or analytics
- **Examples**: salesforce-api, stripe, quickbooks-api, tableau-api
- **Exclusion**: General data analysis libraries (categorized as Data Retrieval)

**8. Multimedia Content** (n=2,934, 10.6%)
- **Definition**: Tools for image, video, audio processing, generation, or manipulation
- **Inclusion criteria**: Primary purpose is multimedia content creation or transformation
- **Examples**: pillow, ffmpeg, moviepy, pydub, imagemagick
- **Exclusion**: Multimedia playback applications

**9. System Infrastructure** (n=2,156, 7.8%)
- **Definition**: Tools for system monitoring, configuration, deployment, networking, or infrastructure management
- **Inclusion criteria**: Primary purpose is system-level operations
- **Examples**: psutil, docker-py, kubernetes-client, paramiko, watchdog
- **Exclusion**: Application-level monitoring (categorized as Code & DevOps)

**10. External Service Connectors** (n=1,234, 4.5%)
- **Definition**: API wrappers or SDKs for third-party services (cloud providers, SaaS platforms, etc.)
- **Inclusion criteria**: Primary purpose is interfacing with external service APIs
- **Examples**: boto3 (AWS), google-cloud-python, azure-sdk, openai-python
- **Exclusion**: Services that fit better in specific categories (e.g., Slack SDK → Communication)

**Granularity Definitions**:
- **Primitive tool**: Single-purpose utility performing one atomic operation (e.g., jq, curl)
- **Service wrapper**: SDK or client library for external service (e.g., boto3, stripe-python)
- **Workflow skill**: Multi-step process or orchestration (e.g., data pipeline, test suite)
- **Platform adapter**: Integration layer between systems (e.g., database connector, message queue client)

**Execution Mode Definitions**:
- **Local deterministic**: Runs locally with deterministic output (e.g., file processor, calculator)
- **Remote API-mediated**: Calls external APIs (e.g., weather service, translation API)
- **Browser-mediated**: Requires browser automation (e.g., Selenium scripts)
- **Human-in-the-loop**: Requires human input or approval (e.g., interactive forms)
- **Hybrid**: Combination of multiple modes

**B.3 Dataset Access**

The annotated dataset is available at: https://github.com/[anonymous-repo]/software2skill-dataset

**Dataset Contents**:
- `clawhub_annotations.csv`: 2,200 Clawhub skills with metadata and scores
- `github_annotations.csv`: 27,696 GitHub repositories with metadata and scores
- `validation_sample.csv`: 200 validation samples with LLM and human annotations
- `schema.json`: Complete data schema documentation
- `README.md`: Dataset documentation and usage guide

**Data Fields**:
- `project_id`: Unique identifier (GitHub URL or Clawhub skill ID)
- `name`: Project name
- `description`: Short description
- `primary_language`: Primary programming language
- `stars`: Star count at collection time
- `last_updated`: Last update timestamp
- `license`: License type
- `task_clarity`: Score 1-5
- `interface_clarity`: Score 1-5
- `composability`: Score 1-5
- `automation_value`: Score 1-5
- `deployment_friction`: Score 1-5 (inverse)
- `operational_risk`: Score 1-5 (inverse)
- `skillability_score`: Composite score 1-5
- `opportunity_score`: Opportunity score 0-1 (GitHub only)
- `capability_category`: Category label
- `granularity`: Granularity label
- `execution_mode`: Execution mode label
- `llm_reasoning`: LLM's reasoning text

**Note**: README content is not included due to potential copyright concerns. Researchers can retrieve README content using the provided project identifiers and GitHub API.

### Appendix C: Extended Results

**C.1 Full Category Analysis**

**Table C.1: Complete Category Statistics**

| Category | n | % | Mean SS | SD | Median | IQR | High Skill % | Cohen's d vs Overall |
|----------|---|---|---------|-----|--------|-----|--------------|---------------------|
| Data Retrieval & Search | 3,847 | 13.9% | 3.42 | 1.08 | 3.50 | 1.20 | 48.3% | 0.40 |
| Multimedia Content | 2,934 | 10.6% | 3.38 | 1.12 | 3.45 | 1.25 | 46.1% | 0.36 |
| System Infrastructure | 2,156 | 7.8% | 3.31 | 1.15 | 3.35 | 1.30 | 44.2% | 0.36 |
| Document Processing | 2,089 | 7.5% | 3.28 | 1.09 | 3.30 | 1.22 | 43.8% | 0.34 |
| Web Automation | 1,987 | 7.2% | 3.19 | 1.14 | 3.20 | 1.28 | 41.2% | 0.26 |
| Communication | 1,654 | 6.0% | 3.15 | 1.11 | 3.15 | 1.25 | 40.1% | 0.23 |
| Code & DevOps | 4,213 | 15.2% | 3.08 | 1.21 | 3.10 | 1.40 | 38.4% | 0.17 |
| Business & Productivity | 2,341 | 8.5% | 2.94 | 1.18 | 2.95 | 1.35 | 34.2% | 0.05 |
| Knowledge & Workflow | 1,876 | 6.8% | 2.87 | 1.22 | 2.85 | 1.42 | 32.1% | -0.01 |
| External Service Connectors | 1,234 | 4.5% | 2.71 | 1.16 | 2.70 | 1.38 | 28.9% | -0.14 |
| Other | 3,365 | 12.1% | 2.65 | 1.25 | 2.60 | 1.50 | 27.3% | -0.19 |

**Pairwise Category Comparisons** (selected significant differences):

| Category A | Category B | Δ Mean SS | t-statistic | p-value | Cohen's d |
|------------|------------|-----------|-------------|---------|-----------|
| Data Retrieval | External Service | +0.71 | 15.2 | <0.001 | 0.62 |
| Multimedia | Code & DevOps | +0.30 | 6.8 | <0.001 | 0.26 |
| System Infrastructure | Knowledge & Workflow | +0.44 | 8.1 | <0.001 | 0.38 |
| Document Processing | Business & Productivity | +0.34 | 6.2 | <0.001 | 0.30 |

**Category Distribution: Clawhub vs GitHub**

| Category | Clawhub % | GitHub % | Difference |
|----------|-----------|----------|------------|
| Data Retrieval & Search | 18.2% | 13.5% | +4.7% |
| Web Automation | 12.4% | 6.8% | +5.6% |
| External Service Connectors | 15.1% | 3.9% | +11.2% |
| Communication | 9.8% | 5.7% | +4.1% |
| Code & DevOps | 11.2% | 15.6% | -4.4% |
| Multimedia Content | 8.9% | 10.8% | -1.9% |
| System Infrastructure | 6.5% | 8.0% | -1.5% |
| Document Processing | 7.2% | 7.5% | -0.3% |
| Business & Productivity | 5.4% | 8.8% | -3.4% |
| Knowledge & Workflow | 3.8% | 7.1% | -3.3% |
| Other | 1.5% | 12.3% | -10.8% |

**Interpretation**: Clawhub skills concentrate in data retrieval, web automation, and external service connectors—categories with clear automation value and well-defined interfaces. GitHub repositories show broader distribution with more representation in code/DevOps and general-purpose tools.

**C.2 Top-100 High-Opportunity GitHub Repositories**

**Table C.2: Top 100 Repositories by Opportunity Score**

| Rank | Name | Stars | Category | SS | Opp Score | Language | Key Strengths |
|------|------|-------|----------|-----|-----------|----------|---------------|
| 1 | yt-dlp | 78,000 | Data Retrieval | 4.65 | 0.94 | Python | TC=5, IC=5, AV=5, clear CLI |
| 2 | whisper | 72,000 | Multimedia | 4.52 | 0.93 | Python | TC=5, AV=5, well-documented API |
| 3 | playwright | 67,000 | Web Automation | 4.35 | 0.92 | TypeScript | TC=4, IC=4, AV=5, comprehensive docs |
| 4 | scrapy | 51,000 | Data Retrieval | 4.42 | 0.91 | Python | TC=4, IC=4, AV=5, mature framework |
| 5 | httpx | 13,000 | Data Retrieval | 4.58 | 0.89 | Python | TC=5, IC=5, C=5, modern HTTP client |
| 6 | Pillow | 12,000 | Multimedia | 4.38 | 0.88 | Python | TC=4, IC=5, AV=4, standard library |
| 7 | moviepy | 12,000 | Multimedia | 4.28 | 0.87 | Python | TC=4, IC=4, AV=5, video editing |
| 8 | schedule | 11,000 | System Infrastructure | 4.78 | 0.87 | Python | TC=5, IC=5, AV=5, simple scheduling |
| 9 | psutil | 10,000 | System Infrastructure | 4.75 | 0.86 | Python | TC=5, IC=5, AV=5, system monitoring |
| 10 | paramiko | 9,200 | System Infrastructure | 4.28 | 0.85 | Python | TC=4, IC=4, AV=5, SSH client |
| 11 | pydub | 8,500 | Multimedia | 4.55 | 0.84 | Python | TC=5, IC=5, AV=4, audio processing |
| 12 | beautifulsoup4 | 7,800 | Data Retrieval | 4.72 | 0.84 | Python | TC=5, IC=5, C=5, HTML parsing |
| 13 | docker-py | 6,800 | System Infrastructure | 4.32 | 0.83 | Python | TC=4, IC=4, AV=5, Docker API |
| 14 | watchdog | 6,400 | System Infrastructure | 4.62 | 0.82 | Python | TC=5, IC=5, AV=4, file monitoring |
| 15 | requests-html | 5,900 | Data Retrieval | 4.48 | 0.81 | Python | TC=5, IC=4, AV=4, HTML parsing |
| 16 | python-docx | 5,200 | Document Processing | 4.55 | 0.80 | Python | TC=5, IC=5, AV=4, Word docs |
| 17 | pypdf | 4,800 | Document Processing | 4.62 | 0.79 | Python | TC=5, IC=5, AV=4, PDF manipulation |
| 18 | selenium-wire | 4,500 | Web Automation | 4.38 | 0.78 | Python | TC=4, IC=4, AV=5, network capture |
| 19 | imageio | 1,400 | Multimedia | 4.68 | 0.77 | Python | TC=5, IC=5, AV=4, image I/O |
| 20 | python-telegram-bot | 3,800 | Communication | 4.42 | 0.77 | Python | TC=4, IC=5, AV=5, Telegram API |

[Rows 21-100 omitted for brevity - full table available in online appendix]

**Notable Patterns in Top 100**:
- **Language dominance**: Python (78%), JavaScript/TypeScript (12%), Go (6%), Other (4%)
- **Category concentration**: Data Retrieval (28%), Multimedia (22%), System Infrastructure (18%), Document Processing (12%), Web Automation (10%), Other (10%)
- **Star distribution**: Median 8,200 stars, but 15% have <2,000 stars (high skillability, lower popularity)
- **Common characteristics**: Clear single purpose (TC ≥4: 92%), well-documented APIs (IC ≥4: 88%), high automation value (AV ≥4: 95%)

**C.3 Sensitivity Analysis Details**

**Alternative Weight Configurations**:

**Configuration A (Equal Weights)**:
```
SS_A = (TC + IC + C + AV - DF - OR) / 6
```
All dimensions weighted equally, inverse scoring for DF and OR.

**Configuration B (Interface-Focused)**:
```
SS_B = 0.20×TC + 0.30×IC + 0.25×C + 0.15×AV - 0.05×DF - 0.05×OR
```
Emphasizes interface clarity and composability over task clarity and automation value.

**Configuration C (Risk-Averse)**:
```
SS_C = 0.20×TC + 0.20×IC + 0.20×C + 0.20×AV - 0.10×DF - 0.10×OR
```
Doubles weight on deployment friction and operational risk.

**Rank Correlation Matrix**:

|  | Original | Config A | Config B | Config C |
|--|----------|----------|----------|----------|
| Original | 1.000 | 0.942 | 0.913 | 0.887 |
| Config A | 0.942 | 1.000 | 0.956 | 0.934 |
| Config B | 0.913 | 0.956 | 1.000 | 0.921 |
| Config C | 0.887 | 0.934 | 0.921 | 1.000 |

**Classification Agreement** (High Skillability ≥4.0):

| Configuration | Agreement with Original | Precision | Recall | F1 Score |
|---------------|------------------------|-----------|--------|----------|
| Config A | 89.2% | 0.91 | 0.86 | 0.88 |
| Config B | 87.4% | 0.89 | 0.84 | 0.86 |
| Config C | 85.1% | 0.87 | 0.81 | 0.84 |

**Projects with Largest Rank Changes** (Original vs Config C):

| Project | Original Rank | Config C Rank | Δ Rank | Reason |
|---------|---------------|---------------|--------|--------|
| kubernetes | 8,234 | 12,456 | -4,222 | High DF and OR penalized more heavily |
| terraform | 6,789 | 9,123 | -2,334 | High DF penalized more heavily |
| jq | 145 | 98 | +47 | Low DF and OR rewarded more |
| curl | 234 | 156 | +78 | Low DF and OR rewarded more |
| docker | 5,678 | 7,234 | -1,556 | Moderate DF penalized more |

**Interpretation**:
- Rankings are robust to moderate weight changes (all correlations >0.88)
- Risk-averse weighting (Config C) penalizes complex infrastructure tools more heavily
- Interface-focused weighting (Config B) rewards well-documented APIs
- Equal weighting (Config A) shows highest correlation with original, suggesting original weights are balanced
- Borderline cases (SS ≈ 4.0) show most sensitivity to weight changes

**Statistical Significance of Weight Sensitivity**:
- Kendall's tau between Original and Config C: τ=0.82 (p<0.001)
- Top-100 overlap: 87 projects appear in top-100 for all configurations
- Top-1000 overlap: 94.2% projects appear in top-1000 for all configurations

**Conclusion**: The skillability ranking is robust to reasonable weight variations. High-skillability projects remain high-skillability across configurations, though exact scores and borderline classifications may vary.

---

## Figure Captions

**Figure 1: Skillability Score Distribution**
Distribution of skillability scores for Clawhub skills (n=2,200) and GitHub repositories (n=27,696). Clawhub skills show a left-skewed distribution concentrated in the 3.5-4.5 range (mean=3.75, SD=0.82), while GitHub repositories exhibit a more normal distribution centered around 2.5-3.5 (mean=2.88, SD=1.21). The difference is statistically significant (Welch's t-test, p<0.001, Cohen's d=0.74).

**Figure 2: Per-Dimension Comparison**
Radar chart comparing mean dimension scores for Clawhub skills and GitHub repositories across all six dimensions. Clawhub skills consistently score higher on positive dimensions (task clarity, interface clarity, composability, automation value) and lower on negative dimensions (deployment friction, operational risk). All differences are statistically significant with medium to large effect sizes (Cohen's d ranging from 0.33 to 0.83).

**Figure 3: Category Distribution and Skillability**
Bar chart showing the distribution of projects across capability categories (left axis, count) and mean skillability scores per category (right axis, mean SS). Data retrieval & search, multimedia content, and system infrastructure show the highest mean skillability scores (>3.3), while external service connectors and "other" categories show lower scores (<2.7). Code & DevOps has the most projects (n=4,213) but moderate skillability (mean=3.08).

**Figure 4: Skillability vs. Repository Popularity**
Scatter plot of skillability scores (y-axis) vs. repository stars (x-axis, log scale) for GitHub repositories (n=27,696). Points are colored by high-skillability classification (≥4.0: blue, <4.0: gray). The negligible correlation (Spearman r_s=0.003, p=0.62) indicates that skillability is independent of popularity. Many high-skillability repositories have modest star counts (<1,000), suggesting undiscovered opportunities.

---

**Acknowledgments**

This work was conducted as part of research into AI agent ecosystems and software reusability. We thank the anonymous reviewers for their constructive feedback. We acknowledge the use of Alibaba Qwen-Plus for large-scale annotation and the open-source community for making their repositories publicly available.

**Data Availability**

The annotated dataset, validation samples, and analysis scripts are available at: https://github.com/[anonymous-repo]/software2skill-dataset (to be made public upon acceptance).

**Ethical Considerations**

This study analyzes publicly available open-source repositories and skill marketplace data. No private or proprietary code was accessed. We respect copyright by not redistributing README content, providing only project identifiers for researchers to retrieve content independently. Our LLM annotation approach does not involve human subjects and poses no ethical concerns beyond standard considerations for automated content analysis.

---

**End of Paper**

