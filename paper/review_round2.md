# Round 2 Review: Deep Strengthening

## Overall Assessment

The paper is improved over Round 1 and now reads as an exploratory empirical study rather than an overclaimed validation paper. The authors explicitly acknowledge key limitations. However, the empirical methodology is still not ICSE-publishable. Main blockers: construct validity, fairness of comparison, weak annotation validation, and unresolved statistical specification issues.

## Critical Issues (Must Fix)

1. **Confounded Comparison**: Clawhub items annotated from full skill specifications, GitHub from only first 3000 README characters. This invalidates strong interpretation of the 0.86-point gap. Need fair comparison based on equivalent evidence sources or matched design.

2. **Insufficient Construct Validation**: No factor analysis, convergent/discriminant validation, expert panel validation, or weight sensitivity analysis. Why should this weighted score be trusted as scientific construct rather than plausible heuristic?

3. **Mathematically Inconsistent Scoring**: Weighted formula yields continuous score whose natural range is not 1-5, yet paper reports integer score bins 1-5 and normalizes as `(SS - 1) / 4`. Unclear whether scores are rounded, clipped, rescaled, or continuous. Affects threshold `>=4`, all distributions, and opportunity score.

4. **Weak LLM Annotation Validation**: 200-item spot check with "agreement within ±0.5" insufficient without human-human reliability, adjudication protocol, formal IRR, and error analysis. Nearly all results depend on these labels - reject-level risk.

5. **Tautological Findings**: Component-vs-composite correlations still presented as result despite being descriptive, not predictive. Will be seen as circular at ICSE unless replaced with externally grounded analysis.

6. **Missing Reproducibility Material**: Appendices claim to contain prompt, rubric, taxonomy, statistical details, but sections are placeholders. Figures/tables absent. Methods-heavy paper cannot ship with missing methodological artifacts.

## Major Issues (Should Fix)

1. **Statistical Rigor Below ICSE**: Uses Welch's t-test and Pearson correlations but doesn't report assumption checks, robustness checks, or rationale for treating weighted Likert composite as interval-scaled. Need bootstrap CIs and nonparametric robustness checks.

2. **Multiple Testing Dismissed Casually**: "Exploratory" doesn't justify no correction when reporting multiple dimensions, categories, correlations, subgroup comparisons. Should mark primary analysis set and treat rest as exploratory with FDR control.

3. **Wrong Correlation for Popularity**: GitHub stars highly skewed; Pearson on raw stars sensitive to outliers. Should report Spearman and scatter on log-stars or robust regression.

4. **Sampling Not Defended Against Selection Effects**: Filters (stars >= 10, recent activity, README present, non-archived) select for polished projects. Claims must be limited to that population, not "software projects" broadly.

5. **Arbitrary Unvalidated Opportunity Score**: Weights in both SS and OpportunityScore are expert-chosen, unsupported by sensitivity or downstream validation. "Top candidates" are rankings by heuristic, not empirical findings.

6. **Threats to Validity Missing Items**: Label leakage from metadata supplied to LLM, common-method bias from deriving all labels from one prompt/model, dependence between sampling/measurement/outcomes.

## Minor Issues (Nice to Fix)

1. **Report Effect Sizes Broadly**: Only main mean comparison has Cohen's d; category and subgroup differences need effect sizes too.

2. **Clarify Annotation Process**: Were six dimensions single-pass or multi-pass annotated? If one prompt generated all labels jointly, likely within-response coupling.

3. **Explain Threshold**: "High skillability" (`>=4`) looks arbitrary.

4. **Add Concrete Examples**: False-positive and false-negative annotation examples would make limitations more credible.

5. **Stronger Table/Figure Integration**: Text references figures not present. Figure list gives names but no captions or interpretation guidance.

## Strengths

- Removes strongest overclaims
- Explicitly labels study as exploratory
- Acknowledges circularity of component-to-composite correlations
- Much more transparent about annotation and comparison limitations
- Threats-to-validity organized along standard construct/internal/external/conclusion structure
- Statistical reporting modestly better (test, effect size, CI named for headline comparison)

## Specific Recommendations

1. **Redesign RQ2 for Fair Comparison**: Re-annotate both corpora using equivalent textual evidence, or create matched subset where both sides have comparable interface documentation.

2. **Stabilize Construct Before Adding Scale**: Provide gold set with expert annotation, report human-human IRR and LLM-human IRR, run weight sensitivity analyses. If infeasible, narrow claims further and present score as heuristic index.

3. **Fix Score Definition**: State exact score range, whether scores continuous or discretized, how bins formed, how normalization done. Math and reported distributions don't line up.

4. **Replace Component/Composite Correlation**: Use leave-one-dimension-out robustness, external outcome association, or predictive validity against downstream label.

5. **Upgrade Statistics Section**: Add assumption checks, bootstrap CIs, nonparametric robustness tests, Spearman for stars, treatment of multiplicity.

6. **Complete Appendices and Figures**: Prompt, rubric, taxonomy, statistical appendix, actual figures are essential, not optional.

7. **Improve Data Presentation**: Every figure should answer one RQ, include self-contained caption, show uncertainty, avoid decorative charts. Radar chart (Figure 3) poor choice for comparing six dimensions - use coefficient plot or grouped interval plot.

## Priority Actions for Round 3

**Critical**:
- Fix score definition and mathematical consistency
- Add construct validation or further narrow claims
- Complete all appendix materials
- Create all figures with proper captions
- Redesign RQ2 comparison or acknowledge as exploratory only

**High Priority**:
- Upgrade statistical rigor (bootstrap, nonparametric, Spearman)
- Add effect sizes for all comparisons
- Address multiple testing
- Expand threats to validity
- Add concrete annotation examples

**Medium Priority**:
- Improve figure quality and integration
- Add sensitivity analyses
- Clarify annotation process details
- Justify threshold choices

## Bottom Line

Now a more self-aware exploratory paper, but still lacks methodological control and statistical grounding for ICSE acceptance. Path to publishability: narrow claims, fix score specification, make RQ2 fair, substantially strengthen validation of annotation pipeline and construct.
