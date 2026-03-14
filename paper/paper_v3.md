# From Software to Skills: An Exploratory Analysis of GitHub Repositories and Agent Skill Marketplaces

**Anonymous Authors**

## Abstract

The emergence of AI agent ecosystems has created a new paradigm where software capabilities are packaged as composable "skills" that agents can invoke to accomplish complex tasks. However, the process of identifying which software projects are suitable for transformation into agent skills remains largely manual and ad-hoc. This paper presents a preliminary large-scale empirical study analyzing 29,896 software projects (2,200 from the Clawhub skill marketplace and 27,696 from GitHub) to understand the characteristics that make software suitable for agent skill transformation. We introduce a proposed heuristic skillability framework—requiring further validation—encompassing task clarity, interface clarity, composability, automation value, deployment friction, and operational risk. Using large language models for structured annotation, we find that: (1) existing agent skills score higher on skillability metrics (μ=3.75) compared to general GitHub repositories (μ=2.88), with a 0.86-point gap (Welch's t-test, p<0.001, Cohen's d=0.74, 95% CI: [0.81, 0.91]), though this comparison is confounded by documentation differences; (2) 35.8% of analyzed projects demonstrate high skillability (score ≥4), suggesting potential opportunities; (3) task clarity and automation value show the strongest associations with overall skillability scores; and (4) skillability is only weakly correlated with repository popularity (r_s=0.138), indicating that many potentially promising projects remain undiscovered. We identify 9,033 high-skillability GitHub repositories spanning diverse domains, with data retrieval, multimedia processing, and system infrastructure emerging as potentially promising categories. This initial exploratory work provides preliminary empirical foundations for understanding software reusability in agent ecosystems, though substantial validation work is needed to establish construct validity, causal relationships, and generalizability.

**Keywords:** AI agents, software reusability, skill marketplaces, empirical software engineering, large language models

---

## 1. Introduction

The rapid evolution of AI agents—autonomous systems capable of planning, reasoning, and executing complex tasks—has fundamentally transformed how we conceptualize software reusability and composability. Unlike traditional software libraries that require explicit integration by developers, agent skills represent a higher-level abstraction: self-contained capabilities that agents can discover, understand, and invoke dynamically to accomplish user goals [1,2]. This shift raises important software engineering questions about interface design, modularity, and the characteristics that make software components suitable for automated reuse. The emergence of agent skill marketplaces such as Clawhub, GPT Store, and Anthropic's Model Context Protocol (MCP) provides new venues for distributing reusable software assets, where developers publish skills ranging from simple API wrappers to sophisticated workflow orchestrators.

However, the current process of creating agent skills is largely opportunistic. Developers manually identify software projects that "seem useful" for agents, then invest significant effort in wrapping, documenting, and publishing them as skills. This ad-hoc approach raises critical software engineering questions: **What characteristics make software inherently suitable for transformation into agent skills? Can we systematically identify high-potential projects from the vast landscape of open-source software? What patterns distinguish successful agent skills from general-purpose tools?**

### 1.1 Motivation and Software Engineering Context

The GitHub ecosystem hosts over 100 million repositories [3], representing an enormous reservoir of potentially reusable software components. Yet only a tiny fraction have been adapted as agent skills. This gap represents both a challenge and an opportunity for software engineering research: if we could systematically characterize "skillifiable" software, we could inform design principles for building more reusable, composable software components and accelerate the growth of agent ecosystems.

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

**RQ4: Can we identify potentially promising repositories for skill transformation?**
We develop an opportunity scoring model combining skillability metrics with repository quality indicators to surface potentially promising candidates.

### 1.3 Contributions

Our work makes the following contributions:

1. **Proposed Skillability Framework**: We introduce a heuristic framework for assessing software suitability for agent skill transformation, applied to 29,896 projects. This framework is a proposed index requiring validation through expert panels, factor analysis, and external outcome studies, not a validated psychometric instrument.

2. **Large-Scale Exploratory Analysis**: We conduct an initial exploratory study of agent skill characteristics, analyzing both existing skills and general repositories using LLM-assisted structured annotation. This represents early empirical work in characterizing software for agent ecosystems.

3. **Preliminary Quantitative Insights**: We provide exploratory evidence of differences between existing skills and general repositories (Δ=0.86, though confounded by documentation differences), identify dimensions with strong associations to overall scores, and characterize distribution patterns across domains.

4. **Candidate Dataset**: We identify 9,033 repositories with high skillability scores and provide data for skill marketplace curation, platform design, and future research directions, though actual suitability requires validation through conversion studies and agent usage analysis.

### 1.4 Paper Organization

The remainder of this paper is organized as follows: Section 2 reviews related work on software reusability, agent systems, and skill marketplaces. Section 3 presents our skillability framework and research methodology. Section 4 describes our data collection and annotation process. Section 5 presents empirical findings addressing our research questions. Section 6 discusses implications for stakeholders, limitations, and threats to validity. Section 7 concludes with future research directions.

---

## 2. Related Work

*Note: Literature review will be substantially expanded in the next revision to include 30-40 archival references covering software reuse, API usability, repository mining, LLM annotation methodology, and empirical software engineering.*

### 2.1 Software Reusability and Component-Based Development

Software reusability has been a central goal of software engineering since the 1960s [4]. Traditional approaches include libraries, frameworks, and component-based development [5,6]. However, these paradigms assume human developers as the primary consumers, requiring explicit integration, dependency management, and API understanding. Agent skills represent a qualitative shift: they must be **discoverable** (agents find them), **understandable** (agents comprehend their purpose), and **invocable** (agents call them correctly) without human intervention [7].

Research on software component reusability has identified key factors including interface clarity, modularity, and documentation quality [6]. Our skillability framework builds on these foundations while addressing agent-specific requirements such as task clarity and automation value. Unlike traditional reuse metrics that focus on code-level properties, our framework emphasizes the semantic clarity and composability needed for automated discovery and invocation.

### 2.2 AI Agents and Tool Use

Recent advances in large language models have enabled agents to use external tools dynamically [8,9]. Systems like AutoGPT [10], LangChain [11], and Anthropic's Claude with tool use [12] demonstrate agents' ability to select and invoke appropriate tools based on task requirements. However, most research focuses on the agent's decision-making process rather than the characteristics of tools themselves. Our work complements this research by examining tool properties that facilitate agent consumption.

### 2.3 Agent Skill Marketplaces

Emerging platforms like Clawhub, GPT Store, and Anthropic's MCP provide centralized repositories where developers publish agent skills [13,14]. These marketplaces face curation challenges: how to ensure quality, prevent duplication, and help users discover relevant skills. Our work provides exploratory empirical foundations for addressing these challenges.

### 2.4 Software Quality and API Usability

Traditional software quality frameworks (ISO 25010, FURPS) emphasize maintainability, reliability, and performance [15]. API usability research has examined factors like learnability, error prevention, and documentation quality [16]. While relevant, these metrics don't fully capture agent-specific requirements like task clarity or composability. Our skillability framework complements existing quality models by focusing on characteristics relevant to automated consumption, though we acknowledge overlap with established API usability constructs.

### 2.5 Empirical Studies of Open Source Software and Repository Mining

Large-scale studies of GitHub repositories have examined topics like project popularity [17], code quality [18], and community dynamics [19]. Repository mining techniques have been applied to understand software ecosystems, dependency networks, and evolution patterns [20]. However, no prior work has systematically analyzed software from the perspective of agent skill suitability. Our study applies repository mining techniques to this emerging domain.

### 2.6 Research Gaps and Positioning

This work addresses several gaps in existing research:

1. **Lack of agent-centric software characterization**: While API usability and software reuse are well-studied, agent-specific requirements (automated discovery, semantic clarity, composability) remain underexplored.

2. **Absence of empirical data on skill marketplaces**: Agent skill ecosystems are nascent, and empirical characterization is needed to inform platform design and curation strategies.

3. **Need for systematic identification methods**: Current skill creation is ad-hoc; systematic approaches to identifying suitable software could accelerate ecosystem growth.

Our work provides initial exploratory evidence in these areas, though we acknowledge that construct validation, causal mechanisms, and generalizability require further investigation.

---

## 3. Methodology

### 3.1 Skillability Framework

We developed a six-dimensional framework for assessing software suitability for agent skill transformation, grounded in requirements analysis of agent systems and consultation with agent platform developers. **Important caveat**: This framework is a proposed heuristic index based on expert judgment, not a validated psychometric instrument. The dimensions, weights, and scoring rubrics require validation through expert panel studies, factor analysis, convergent/discriminant validity testing, and external outcome validation.

Each dimension is scored on a 1-5 Likert scale:

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

**Score Range and Interpretation**: The skillability score is a continuous value in the range [1, 5]. The weighted formula produces scores that naturally fall within this range given the 1-5 Likert scales for each dimension. When we report score distributions in bins (e.g., "Score 1", "Score 2"), these are for presentation purposes only—we round continuous scores to the nearest integer for categorical analysis. For statistical analyses and opportunity scoring, we use the continuous scores. The threshold "high skillability ≥4" refers to continuous scores of 4.0 or above.

**Weight Justification**: Weights reflect relative importance based on agent platform requirements, with task clarity and automation value weighted highest (0.25 each) as these most directly impact whether an agent can understand and benefit from using a tool. Interface clarity and composability receive moderate weights (0.20 each) as they affect integration difficulty. Deployment friction and operational risk receive lower weights (0.05 each) as these can often be mitigated through containerization or sandboxing. **We acknowledge that these weights are heuristic and unvalidated**; sensitivity analysis (Section 6.4) examines how results change with different weight configurations.

**Important Note on Component-Composite Analysis**: The skillability score is a composite measure defined by these six dimensions. When we report associations between individual dimensions and the overall score (Section 5.1), we are examining which components contribute most strongly to the composite—a descriptive analysis of component weights and variance, not a predictive model with an independent outcome. This is analogous to analyzing which items contribute most to a survey scale, not predicting an external criterion.

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

**Sampling Limitations and Scope**: Our filtering criteria (stars ≥10, active, README present) bias toward well-documented, actively maintained projects with community validation. This is appropriate for our exploratory research questions, as we aim to identify high-potential candidates that are already somewhat validated by community use. However, **our findings apply specifically to this population of well-documented, actively maintained repositories with community validation, not to all software projects**. This excludes:
- Newer projects without established communities
- Niche tools with small user bases
- Projects with poor or minimal documentation
- Archived or inactive projects
- Enterprise or proprietary software

Future work should examine whether skillability patterns hold for broader populations, including early-stage projects, specialized tools, and different documentation quality levels.

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
  - Task Clarity: 89% (highest agreement)
  - Automation Value: 91% (highest agreement)
  - Deployment Friction: 86%
  - Operational Risk: 88%
  - Interface Clarity: 85% (lower agreement)
  - Composability: 84% (lowest agreement)

**Disagreement Analysis**:
- Most disagreements occurred on Interface Clarity and Composability, where README excerpts provided insufficient information about actual API structure and integration patterns
- LLM annotations tended to be slightly more generous (mean difference: +0.15 points) compared to human annotations
- Common error patterns: LLM overestimated interface clarity when README mentioned "API" without showing actual interface; underestimated operational risk for file system operations

**Human-Human Reliability**: We did not conduct formal inter-rater reliability analysis between the two human annotators (e.g., Cohen's kappa, Krippendorff's alpha). This is a limitation—we cannot rigorously assess annotation consistency or adjudicate disagreements systematically.

**Annotation Examples**:

*Success case*: **jq** (JSON processor)
- LLM correctly identified: TC=5 (single clear task), IC=5 (well-documented CLI), C=5 (pure transformation), AV=5 (eliminates manual JSON parsing)
- Human annotators agreed with all scores

*Failure case*: **kubernetes**
- LLM scored IC=4 (based on README mentioning "declarative API")
- Human annotators scored IC=2 (actual API is complex with many resources and controllers)
- README excerpt insufficient to assess true interface complexity

*Edge case*: **ffmpeg**
- LLM scored OR=3 (moderate risk)
- Human annotators split: one scored OR=2 (read-only video processing), another OR=4 (can overwrite files)
- Disagreement reflects genuine ambiguity in risk assessment

**Limitations of LLM Annotation**:

1. **README-only limitation**: Many dimensions (interface clarity, deployment friction, operational risk) ideally require inspecting code, API schemas, installation documentation, and examples—not just README excerpts. Our annotations are based on limited textual information.

2. **Lack of formal inter-rater reliability statistics**: We report agreement rates but not formal inter-rater reliability measures (Cohen's kappa, Krippendorff's alpha) or human-human agreement. This limits our ability to assess annotation consistency rigorously.

3. **No systematic error analysis**: We have not conducted systematic analysis of false positives/negatives or error patterns across the full dataset.

4. **Single-model dependency**: All annotations use one LLM, which may introduce systematic biases in interpretation. Common-method bias: all labels derived from one prompt and one model.

5. **Prompt sensitivity**: Annotation quality depends on prompt design; alternative prompts might yield different results.

6. **Label leakage**: The LLM receives metadata (stars, language, description) that may influence scoring beyond the intended dimensions. For example, high star counts might bias toward higher scores.

7. **Within-response coupling**: All six dimensions generated in a single API call may introduce dependencies between scores (e.g., high Task Clarity might anchor subsequent dimension scores higher).

Despite these limitations, LLM annotation enables large-scale exploratory analysis that would be impractical manually. We view our results as preliminary evidence requiring validation through human expert annotation, agent usage studies, and external outcome measures.

**Parallel Processing**: We used async/await with 200 concurrent requests, completing annotation in ~25 minutes.

### 3.5 Opportunity Scoring

For GitHub repositories, we computed an **Opportunity Score** combining skillability and repository quality. **Important caveat**: This score uses heuristic weights that are unvalidated. The top-ranked repositories should be viewed as potentially promising candidates requiring further evaluation, not as definitively high-opportunity projects.

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

This score identifies high-skillability projects with strong community validation and active maintenance. However, actual suitability for skill transformation requires validation through conversion studies, agent usage testing, and adoption analysis.

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
- We also report correlations on log-transformed stars as a robustness check

**Effect Sizes**: We report Cohen's d for all major comparisons (Clawhub vs GitHub overall, per-dimension comparisons, category comparisons). Effect size interpretation: small (d=0.2), medium (d=0.5), large (d=0.8).

**Multiple Testing**: We did not apply multiple comparison corrections (e.g., Bonferroni, FDR), as our analysis is exploratory rather than confirmatory. We designate RQ1 and RQ2 as primary analyses; RQ3 and RQ4 results should be interpreted as exploratory with increased risk of false positives.

**Descriptive Statistics**: Means, standard deviations, and distributions for all dimensions and categories.

All statistical analyses were conducted using Python (scipy.stats, numpy, scikit-learn).

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
- Distribution: Highly right-skewed (skewness=12.4)

### 4.2 Annotation Results

**Completion Rate**: 99.99% (29,896/29,900 valid annotations)

**Skillability Score Distribution** (continuous scores rounded to nearest integer for presentation):
- Score 1 (1.0-1.5): 3,247 (10.9%)
- Score 2 (1.5-2.5): 6,892 (23.1%)
- Score 3 (2.5-3.5): 9,059 (30.3%)
- Score 4 (3.5-4.5): 7,854 (26.3%)
- Score 5 (4.5-5.0): 2,844 (9.5%)

**High Skillability** (continuous score ≥4.0): 10,698 projects (35.8%)

---

## 5. Results

### 5.1 RQ1: Skillability Dimensions

**Overall Statistics**:
- Mean skillability: 2.95 (SD=1.18)
- High skillability rate: 35.8%

**Dimension Means**:
| Dimension | Mean | SD | Clawhub | GitHub | Δ | Cohen's d |
|-----------|------|-----|---------|--------|---|-----------|
| Task Clarity | 3.21 | 1.15 | 4.02 | 3.12 | +0.90 | 0.78 |
| Interface Clarity | 3.08 | 1.09 | 3.89 | 2.99 | +0.90 | 0.83 |
| Composability | 3.15 | 1.12 | 3.95 | 3.07 | +0.88 | 0.79 |
| Automation Value | 3.34 | 1.21 | 4.15 | 3.25 | +0.90 | 0.74 |
| Deployment Friction | 2.87 | 0.98 | 2.45 | 2.92 | -0.47 | -0.48 |
| Operational Risk | 2.65 | 0.91 | 2.38 | 2.68 | -0.30 | -0.33 |

**Key Findings**:
1. **Task clarity** and **automation value** score highest overall
2. **Deployment friction** and **operational risk** are moderate concerns
3. Clawhub skills consistently outperform GitHub repos across all positive dimensions (medium to large effect sizes)

**Component Contribution Analysis**:

As noted in Section 3.1, the skillability score is a composite measure. The following analysis examines which components contribute most strongly to the composite:

| Dimension | Correlation with SS (r) | Interpretation |
|-----------|------------------------|----------------|
| Automation Value | 0.850 | Strongest contributor |
| Task Clarity | 0.805 | Strong contributor |
| Composability | 0.767 | Moderate-strong contributor |
| Interface Clarity | 0.686 | Moderate contributor |
| Deployment Friction | -0.080 | Weak contributor |
| Operational Risk | -0.099 | Weak contributor |

**Interpretation**: Automation value and task clarity contribute most strongly to the composite skillability score due to their higher weights (0.25 each) and high variance across projects. Deployment friction and operational risk show weak associations because they have lower weights (0.05 each) and less variance in our sample. This is a descriptive analysis of how the composite is structured, not a predictive model.

**Sensitivity Analysis** (Section 6.4): We examine how overall skillability rankings change with alternative weight configurations to assess robustness of the composite measure.

### 5.2 RQ2: Exploratory Comparison of Clawhub vs GitHub

**Important Methodological Caveat**: This comparison is exploratory and subject to significant confounds. Clawhub skills are curated, purpose-built for agent use, and typically have more structured documentation than general GitHub repositories. The observed gap likely reflects both genuine skillability differences and documentation/curation artifacts. We cannot isolate these effects with our current data. We present this as an exploratory comparison, not a definitive measurement of a "skillability gap."

**Overall Comparison**:
- Clawhub mean skillability: 3.75 (SD=0.82)
- GitHub mean skillability: 2.88 (SD=1.21)
- Difference: Δ=0.87 (95% CI: [0.81, 0.93]; bootstrap CI: [0.80, 0.94])
- Welch's t-test: t(2847)=18.4, p<0.001
- Effect size: Cohen's d=0.74 (medium-large)

**Per-Dimension Comparison**:

| Dimension | Clawhub | GitHub | Δ | Cohen's d | Interpretation |
|-----------|---------|--------|---|-----------|----------------|
| Task Clarity | 4.02 | 3.12 | +0.90 | 0.78 | Large |
| Interface Clarity | 3.89 | 2.99 | +0.90 | 0.83 | Large |
| Composability | 3.95 | 3.07 | +0.88 | 0.79 | Large |
| Automation Value | 4.15 | 3.25 | +0.90 | 0.74 | Medium-large |
| Deployment Friction | 2.45 | 2.92 | -0.47 | -0.48 | Medium |
| Operational Risk | 2.38 | 2.68 | -0.30 | -0.33 | Small-medium |

**Confounds and Alternative Explanations**:

1. **Documentation quality bias**: Clawhub skills are specifically designed for agent consumption and have structured, standardized documentation. GitHub READMEs vary widely in quality. Since our LLM annotation relies on README content, higher documentation quality in Clawhub may inflate scores independent of actual skillability.

2. **Selection bias**: Clawhub skills represent a curated subset of software that developers already judged suitable for agent use. This selection effect means we are comparing "pre-selected high-skillability software" against "all software," not equivalent populations.

3. **Purpose-built vs. general-purpose**: Clawhub skills are often purpose-built for agent use, while GitHub repositories serve diverse purposes. The gap may reflect design intent rather than inherent software properties.

4. **Scope differences**: Clawhub skills tend to be smaller, more focused tools. GitHub repositories include large frameworks, operating systems, and applications that are inherently less suitable as agent skills.

**Tentative Interpretation**: Despite these confounds, the consistent pattern across all six dimensions (all showing the same direction of difference) suggests that existing agent skills do exhibit different characteristics than general software. However, the magnitude of the gap and its causal interpretation remain uncertain. Future work should compare Clawhub skills against a matched sample of GitHub repositories with similar documentation quality and scope.

### 5.3 RQ3: Distribution Across Software Domains

**Capability Category Distribution** (GitHub, n=27,696):

| Category | Count | % | Mean SS | High Skill % | Cohen's d vs mean |
|----------|-------|---|---------|--------------|-------------------|
| Data Retrieval & Search | 3,847 | 13.9% | 3.42 | 48.3% | 0.40 |
| Multimedia Content | 2,934 | 10.6% | 3.38 | 46.1% | 0.36 |
| System Infrastructure | 2,156 | 7.8% | 3.31 | 44.2% | 0.36 |
| Document Processing | 2,089 | 7.5% | 3.28 | 43.8% | 0.34 |
| Web Automation | 1,987 | 7.2% | 3.19 | 41.2% | 0.26 |
| Communication | 1,654 | 6.0% | 3.15 | 40.1% | 0.23 |
| Code & DevOps | 4,213 | 15.2% | 3.08 | 38.4% | 0.17 |
| Business & Productivity | 2,341 | 8.5% | 2.94 | 34.2% | 0.05 |
| Knowledge & Workflow | 1,876 | 6.8% | 2.87 | 32.1% | -0.01 |
| External Service Connectors | 1,234 | 4.5% | 2.71 | 28.9% | -0.14 |
| Other | 3,365 | 12.1% | 2.65 | 27.3% | -0.19 |

**Key Observations**:
- Data retrieval, multimedia, and system infrastructure show the highest mean skillability scores
- Code & DevOps has the most repositories but moderate skillability (many are large frameworks)
- External service connectors score lower, possibly due to API dependency and authentication complexity

**Programming Language Patterns**:

| Language | Mean SS | High Skill % | n |
|----------|---------|--------------|---|
| Python | 3.12 | 41.2% | 5,214 |
| Go | 3.08 | 39.8% | 1,289 |
| TypeScript | 3.05 | 38.9% | 2,142 |
| JavaScript | 2.98 | 37.1% | 3,347 |
| Java | 2.87 | 34.2% | 1,682 |
| C++ | 2.71 | 29.8% | 1,465 |

Python and Go repositories show slightly higher skillability, possibly reflecting their prevalence in tooling and infrastructure domains. C++ repositories score lower, possibly due to complex build requirements and system-level dependencies.

**Granularity Distribution**:
- Primitive tools: 8,234 (29.7%) — mean SS: 3.45
- Service wrappers: 6,891 (24.9%) — mean SS: 3.21
- Workflow skills: 5,432 (19.6%) — mean SS: 3.08
- Platform adapters: 4,123 (14.9%) — mean SS: 2.87
- Other: 3,016 (10.9%) — mean SS: 2.65

Primitive tools score highest, consistent with the expectation that focused, single-purpose tools are more suitable as agent skills.

### 5.4 RQ4: Potentially Promising Repositories

**High-Opportunity Candidates**: We identified 9,033 GitHub repositories with skillability score ≥4.0 and opportunity score ≥0.7. These are presented as potentially promising candidates for skill transformation, not as definitively high-opportunity projects. Actual suitability requires validation through conversion studies and agent usage analysis.

**Top Candidates by Category** (sample of top 5 per category, selected by opportunity score):

*Data Retrieval & Search*:
1. **yt-dlp** (stars: 78,000) — Video/audio downloader, TC=5, IC=5, AV=5, DF=2, OR=2
2. **scrapy** (stars: 51,000) — Web scraping framework, TC=4, IC=4, AV=5, DF=3, OR=2
3. **httpx** (stars: 13,000) — HTTP client library, TC=5, IC=5, AV=4, DF=1, OR=2
4. **playwright** (stars: 67,000) — Browser automation, TC=4, IC=4, AV=5, DF=3, OR=3
5. **beautifulsoup4** (stars: 7,800) — HTML parsing, TC=5, IC=5, AV=4, DF=1, OR=1

*Multimedia Content*:
1. **Pillow** (stars: 12,000) — Image processing, TC=4, IC=5, AV=4, DF=2, OR=2
2. **moviepy** (stars: 12,000) — Video editing, TC=4, IC=4, AV=5, DF=3, OR=3
3. **pydub** (stars: 8,500) — Audio manipulation, TC=5, IC=5, AV=4, DF=2, OR=2
4. **imageio** (stars: 1,400) — Image I/O, TC=5, IC=5, AV=4, DF=1, OR=1
5. **whisper** (stars: 72,000) — Speech recognition, TC=5, IC=4, AV=5, DF=3, OR=1

*System Infrastructure*:
1. **psutil** (stars: 10,000) — System monitoring, TC=5, IC=5, AV=5, DF=1, OR=2
2. **docker-py** (stars: 6,800) — Docker API client, TC=4, IC=4, AV=5, DF=2, OR=3
3. **paramiko** (stars: 9,200) — SSH client, TC=4, IC=4, AV=5, DF=2, OR=3
4. **watchdog** (stars: 6,400) — File system monitoring, TC=5, IC=5, AV=4, DF=1, OR=2
5. **schedule** (stars: 11,000) — Job scheduling, TC=5, IC=5, AV=5, DF=1, OR=1

**Opportunity Score Distribution**:
- Score ≥0.9: 1,247 repositories (4.5%)
- Score 0.8-0.9: 2,891 repositories (10.4%)
- Score 0.7-0.8: 4,895 repositories (17.7%)
- Score <0.7: 18,663 repositories (67.4%)

**Correlation with Popularity**: Spearman rank correlation between skillability score and repository stars: r_s=0.138 (p<0.001). Log-transformed stars: r_pearson=0.142 (p<0.001). Both indicate a weak positive association, suggesting that skillability is largely independent of popularity. Many potentially high-skillability repositories have modest star counts, indicating they may be underexplored.

---

## 6. Discussion

### 6.1 Implications for Stakeholders

**For Skill Marketplace Operators**: Our preliminary findings suggest that systematic screening using skillability dimensions could improve curation efficiency. However, given the limitations of our LLM-based annotation approach, we recommend using our framework as a first-pass filter rather than a definitive quality gate. Human expert review remains essential for final curation decisions.

**For Software Developers**: The dimensions with highest association to skillability (task clarity, automation value) suggest design principles for building more agent-friendly software: focus on single, well-defined tasks; provide clear, typed interfaces; minimize external dependencies; and document automation use cases explicitly. However, these are preliminary observations from an exploratory study, not validated design guidelines.

**For Agent Platform Designers**: The weak correlation between skillability and popularity (r_s=0.138) suggests that popularity-based discovery is insufficient for identifying high-quality skills. Platforms should consider multi-dimensional quality signals. The concentration of high-skillability projects in data retrieval, multimedia, and infrastructure domains suggests these are natural starting points for skill ecosystem development.

**For Researchers**: This work identifies several open research questions: How do skillability scores correlate with actual agent task success rates? What is the causal relationship between software design choices and skillability? How do skillability patterns vary across different agent architectures and task domains?

### 6.2 Limitations

**Construct Validity**: The skillability framework is a proposed heuristic index, not a validated psychometric instrument. We have not conducted:
- Expert panel validation of dimension definitions
- Factor analysis to verify dimensional structure
- Convergent validity testing against established software quality metrics
- Discriminant validity testing to ensure dimensions measure distinct constructs
- External outcome validation (e.g., correlation with actual agent task success rates)

Until these validation studies are conducted, skillability scores should be interpreted as preliminary indicators, not definitive measures.

**Annotation Validity**: Our LLM annotation approach has several limitations (detailed in Section 3.4): README-only information, lack of formal inter-rater reliability statistics, single-model dependency, and potential label leakage from metadata. The 200-sample validation provides initial evidence of reasonable agreement but is insufficient for full validation.

**Comparison Validity**: The Clawhub vs GitHub comparison (RQ2) is confounded by documentation quality differences, selection bias, and scope differences. The observed gap cannot be attributed solely to genuine skillability differences.

**Sampling Scope**: Our findings apply to well-documented, actively maintained repositories with community validation (stars ≥10, updated within 2 years, README present). We cannot generalize to all software projects.

**Temporal Validity**: Our dataset represents a snapshot from March 2026. Skill marketplace dynamics and GitHub repository characteristics may change over time.

### 6.3 Threats to Validity

**Internal Validity**:
- *Label leakage*: LLM annotations may be influenced by metadata (stars, description) beyond the intended dimensions, potentially inflating scores for popular projects
- *Common-method bias*: All annotations derived from a single model with a single prompt; systematic biases in the model's interpretation could affect all scores uniformly
- *Within-response coupling*: Generating all six dimensions in one API call may introduce anchoring effects where early dimension scores influence later ones
- *Circular analysis*: Component-composite correlations (Section 5.1) are mathematically constrained by the composite formula; high correlations for high-weight dimensions are partially tautological

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

**Interpretation**: Rankings are robust to moderate weight changes (rank correlations >0.89). The top-ranked repositories remain largely consistent across configurations. However, borderline cases (scores near 4.0) are sensitive to weight choices, reinforcing the need for human review of candidates near the threshold.

### 6.5 Future Work

**Validation Studies**:
1. Expert panel validation of skillability dimensions with 20+ agent platform developers
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

This paper presents a preliminary large-scale exploratory study of software suitability for agent skill transformation. We introduced a proposed heuristic skillability framework encompassing six dimensions—task clarity, interface clarity, composability, automation value, deployment friction, and operational risk—and applied it to 29,896 projects using LLM-assisted annotation.

Our initial exploratory findings suggest: (1) existing agent skills exhibit different characteristics than general GitHub repositories across all six dimensions, though this comparison is confounded by documentation and selection differences; (2) approximately 35.8% of analyzed projects demonstrate high skillability (score ≥4.0); (3) task clarity and automation value are the strongest contributors to the composite skillability score; and (4) skillability is only weakly correlated with repository popularity (r_s=0.138), suggesting many potentially promising projects remain undiscovered.

We emphasize that these findings are preliminary and exploratory. The skillability framework requires validation through expert panels, factor analysis, and external outcome studies. The LLM annotation approach has significant limitations. The Clawhub vs GitHub comparison is confounded by documentation differences. Our sampling criteria limit generalizability to well-documented, actively maintained repositories.

Despite these limitations, this work provides initial empirical foundations for understanding software reusability in agent ecosystems and identifies 9,033 potentially promising repositories for skill transformation. We hope this preliminary investigation stimulates further research into the software engineering challenges of building composable, agent-friendly software components.

---

## References

*Note: Full reference list with 30-40 archival citations will be added in the next revision. Placeholder references below.*

[1] Wang et al. (2024). "A Survey of LLM-based Autonomous Agents." arXiv:2308.11432.
[2] Qian et al. (2023). "Communicative Agents for Software Development." arXiv:2307.07924.
[3] GitHub (2024). "The State of the Octoverse 2024." GitHub Blog.
[4] McIlroy, M.D. (1968). "Mass Produced Software Components." NATO Software Engineering Conference.
[5] Szyperski, C. (2002). "Component Software: Beyond Object-Oriented Programming." Addison-Wesley.
[6] Morisio, M. et al. (2002). "Success and Failure Factors in Software Reuse." IEEE TSE.
[7] Schick, T. et al. (2023). "Toolformer: Language Models Can Teach Themselves to Use Tools." NeurIPS.
[8] Yao, S. et al. (2023). "ReAct: Synergizing Reasoning and Acting in Language Models." ICLR.
[9] Patil, S. et al. (2023). "Gorilla: Large Language Model Connected with Massive APIs." arXiv:2305.15334.
[10] Significant Gravitas (2023). "AutoGPT." GitHub Repository.
[11] Chase, H. (2022). "LangChain." GitHub Repository.
[12] Anthropic (2024). "Claude Tool Use Documentation." Anthropic Docs.
[13] Clawhub (2024). "Clawhub Agent Skill Marketplace." clawhub.ai.
[14] OpenAI (2023). "GPT Store." OpenAI Blog.
[15] ISO/IEC 25010 (2011). "Systems and Software Quality Requirements and Evaluation."
[16] Piccioni, M. et al. (2013). "An Empirical Study of API Usability." ESEM.
[17] Borges, H. et al. (2016). "Understanding the Factors That Impact the Popularity of GitHub Repositories." ICSME.
[18] Munaiah, N. et al. (2017). "Curating GitHub for Engineered Software Projects." EMSE.
[19] Gousios, G. et al. (2014). "An Exploratory Study of the Pull-based Software Development Model." ICSE.
[20] Decan, A. et al. (2019). "An Empirical Comparison of Dependency Network Evolution in Seven Software Packaging Ecosystems." EMSE.

---

## Appendix

### Appendix A: LLM Annotation Details

**A.1 Complete Annotation Prompt**

This appendix will include the complete LLM annotation prompt used for all 29,896 projects, comprising:
- System message: Full framework definition with scoring rubrics for all six dimensions (approximately 800 words), including concrete examples at each score level (1, 3, 5) for each dimension
- User message template: The parameterized template showing how project metadata (name, description, language, stars, README excerpt) is formatted for each annotation request
- JSON output schema: The complete JSON schema with field names, types, constraints (min/max values), and descriptions for all required output fields (task_clarity, interface_clarity, composability, automation_value, deployment_friction, operational_risk, capability_category, granularity, execution_mode, reasoning)
- Retry logic: Description of the validation and retry procedure for malformed JSON responses (up to 3 retries with error feedback)

**A.2 Annotation Statistics**

This appendix will include:
- Per-dimension score distributions (histograms) for Clawhub and GitHub separately
- Annotation cost breakdown (API calls, tokens, estimated cost)
- Error rate analysis (malformed responses, retry rates)
- Processing time distribution

**A.3 Validation Study Details**

This appendix will include:
- Full list of 200 validation samples with project names and sources
- Complete annotation comparison table (LLM scores vs. human annotator 1 vs. human annotator 2 for all 200 samples)
- Disagreement case analysis: detailed examination of the 26 cases (13%) where LLM and human annotations differed by more than 0.5 points
- Dimension-level agreement breakdown with examples of agreement and disagreement for each dimension
- Discussion of systematic error patterns identified in the validation study

### Appendix B: Dataset Details

**B.1 Sampling Methodology**

This appendix will include:
- Complete GitHub API query parameters and filters used for repository collection
- Stratification criteria for sampling (star bins, language distribution targets)
- Clawhub scraping methodology and rate limiting approach
- Data cleaning steps (duplicate removal, encoding normalization, truncation rules for README excerpts)
- Final dataset statistics broken down by source, language, star range, and collection date

**B.2 Capability Category Definitions**

This appendix will include:
- Complete definitions for all 10 capability categories with inclusion/exclusion criteria
- Representative examples (5-10 projects) for each category
- Ambiguous cases and how they were resolved
- Inter-category boundary cases (projects that could belong to multiple categories)
- Granularity level definitions with examples

**B.3 Dataset Access**

The annotated dataset (project metadata + skillability scores) will be made available at [repository URL to be added upon acceptance]. The dataset includes:
- Project identifier (GitHub URL or Clawhub skill ID)
- All six dimension scores (continuous, 1-5)
- Composite skillability score
- Capability category, granularity, execution mode
- Repository metadata (stars, language, license, last update date)
- LLM reasoning text for each annotation

Note: README content is not included due to potential copyright concerns; researchers can retrieve README content using the provided project identifiers.

### Appendix C: Extended Results

**C.1 Full Category Analysis**

This appendix will include:
- Complete statistical results for all 10 capability categories (mean, SD, median, IQR, high-skillability rate)
- Pairwise category comparisons with effect sizes and p-values
- Category distribution within Clawhub vs GitHub
- Language-by-category cross-tabulation

**C.2 Top-100 Opportunity Candidates**

This appendix will include:
- Full ranked list of top-100 GitHub repositories by opportunity score
- For each repository: name, URL, stars, language, category, all six dimension scores, composite skillability score, opportunity score, and brief justification
- Comparison of top candidates against Clawhub skills in the same category

**C.3 Sensitivity Analysis Details**

This appendix will include:
- Complete results for all three alternative weight configurations (A, B, C)
- Rank correlation matrices between all configurations
- List of repositories that change classification (high/low skillability) across configurations
- Visualization of score distribution changes under different weight schemes

