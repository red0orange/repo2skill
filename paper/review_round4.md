# Round 4 Review: Figure/Table Review and Integration

## Overall Assessment

Figure/table package NOT submission-ready. Biggest problem is consistency: manuscript discusses four figures, directory contains eight, and several PNGs don't match values, numbering, or claims in paper. Creates immediate credibility risk for ICSE submission.

Current tables communicate main results reasonably well, but visual story incomplete and uneven. Some plots useful, but several are wrong chart type, disconnected from text, or generated from different dataset/version.

## Critical Issues

1. **Figure Numbering Inconsistent**: Paper says Figure 2 is radar chart and Figure 3 is category chart, but filenames are `fig2_capability_distribution.png` and `fig3_dimension_radar.png`. Must reconcile.

2. **Orphaned Figures**: Only Figures 1-4 referenced/captioned in manuscript, but output_large/figures/ contains Figures 1-8. Figures 5-8 effectively orphaned.

3. **Data Mismatch - fig2**: Doesn't match Table 3. Table 3 sums to n=27,696 (GitHub sample), figure bars sum to 29,716. Uses different category labels ("Knowledge Workflow Research" vs paper taxonomy).

4. **Correlation Contradiction - fig8**: Reports "Correlation: 0.003", directly contradicts paper's stated r_s=0.138 / r_pearson=0.142. MUST FIX.

5. **Malformed Table 2**: Header row contains literal `\\n` before first data row. May render incorrectly.

6. **Table 4 Structure**: Labeled as table but actually a list of category-wise examples. Structurally weak and hard to scan for conference paper.

## Major Issues

1. **Radar Chart Not Best Choice**: fig3_dimension_radar.png makes exact magnitude comparison harder than grouped dot/bar plot. Claim is about consistent differences with effect sizes.

2. **Under-Serves Research Questions**: RQ1/RQ2 get one distribution plot and one radar chart. RQ3/RQ4 would benefit from uncertainty-aware comparisons and clearer ranking visuals.

3. **Detached Captions**: Figure captions in separate "Figure Captions" section rather than integrated with figure placement. Risky for readability and production.

4. **Exploratory EDA Style**: fig4 (language), fig5 (granularity), fig6 (execution mode) look like exploratory EDA rather than publication figures. Simple count bars without direct linkage to research claim, uncertainty, or comparative baseline.

5. **Inconsistent Visual Design**: Styling inconsistent across figures, colors arbitrary rather than semantically assigned, some titles oversized relative to plot area.

## Missing Visualizations

1. **Per-Dimension Comparison (RQ1/RQ2)**: Aligned point-ranges or grouped bars with 95% CIs for Clawhub vs GitHub across all six dimensions.

2. **Category Ranking (RQ3)**: Cleveland dot plot with CI bars and category counts combining mean skillability with uncertainty and sample size.

3. **High-Skillability Threshold Analysis**: Show proportion of projects with SS >= 4.0 by category/language/granularity.

4. **RQ4 Candidate Repositories**: Top repositories by opportunity score, or scatter/ranking plot of opportunity score vs stars colored by category.

5. **Validity/Reliability Figure**: Annotation agreement, validation sample breakdown, or sensitivity analysis summary visualization.

6. **Language/Granularity/Execution Mode**: If retained, should support explicit claim in text or move to appendix.

## Figure-Specific Feedback

### Figure 1 (fig1_skillability_distribution.png)
- **Status**: Reasonable and readable
- **Issue**: Two separate histograms make comparison less immediate
- **Recommendation**: Consider shared-bin overlaid densities, mirrored histograms, or ECDFs. If scores effectively ordinal 1-5, bar/distribution plot may be cleaner.

### Figure 2 (fig2_capability_distribution.png)
- **Status**: NOT ACCEPTABLE
- **Issues**:
  - Doesn't match Table 3 or manuscript taxonomy
  - Shows only counts, not "distribution and mean skillability scores" per caption
  - Data inconsistency (29,716 vs 27,696)
- **Recommendation**: Regenerate from correct dataset with proper taxonomy

### Figure 3 (fig3_dimension_radar.png)
- **Status**: Legible but weak choice
- **Issues**:
  - Radar weak for analytical comparison
  - Visually exaggerates area differences
- **Recommendation**: Replace with horizontal dot plot or slope chart across dimensions

### Figure 4 (fig4_language_distribution.png)
- **Status**: Clean but unnecessary in main paper
- **Issues**:
  - Purely descriptive, not referenced in text
- **Recommendation**: Pair language frequency with mean skillability or high-skillability rate, or move to appendix

### Figure 5 (fig5_granularity_distribution.png)
- **Status**: Unreferenced and inconsistent
- **Issues**:
  - Inconsistent with text counts
- **Recommendation**: Regenerate from same data as paper or remove

### Figure 6 (fig6_execution_mode_distribution.png)
- **Status**: Potentially interesting but tangential
- **Issues**:
  - Paper doesn't discuss execution mode as analyzed factor
- **Recommendation**: Remove or add analysis to text

### Figure 7 (fig7_correlation_heatmap.png)
- **Status**: One of stronger unused figures
- **Issues**:
  - Aligns with component contribution discussion but not referenced
  - Correlation ≠ contribution
- **Recommendation**: Use in appendix if framed carefully

### Figure 8 (fig8_stars_vs_skillability.png)
- **Status**: Sensible approach but data inconsistent
- **Issues**:
  - Reported correlation (0.003) inconsistent with paper (0.138/0.142)
  - Y-axis discrete 1-5
- **Recommendation**: Fix correlation, consider box/violin-by-star-bin or jittered strip with trend line

## Recommendations

### Critical Actions
1. **Full Data Audit**: Every number in every figure must match exact dataset version used in paper
2. **Fix Numbering**: Reconcile figure numbers between text and files
3. **Fix Correlations**: Correct fig8 correlation to match paper
4. **Fix Table 2**: Remove malformed `\\n` in header
5. **Regenerate fig2**: Match Table 3 data and taxonomy

### Major Improvements
1. **Reduce Main Figures**: 4-5 high-value figures tightly tied to RQ1-RQ4, move descriptive distributions to appendix
2. **Replace Radar Chart**: Use CI-based comparison plot
3. **Replace Category Bar Chart**: Use category ranking plot showing mean skillability, uncertainty, sample size together
4. **Fix Integration**: Every included figure referenced in text, numbered consistently, with caption describing what's plotted, dataset scope, key takeaway
5. **Convert Table 4**: Real table with columns: Category, Repository, Stars, SS, Opportunity Score, Why promising

### Polish
1. **Clean Table Formatting**: Table 2 should indicate lower values better for negative dimensions
2. **Add Uncertainty**: Key tables should include uncertainty where relevant
3. **Appendix Material**: Keep fig7_correlation_heatmap.png as appendix unless explicitly used for RQ
4. **Recheck Counts**: Verify all counts in language/granularity/execution-mode plots match manuscript totals

## Priority Actions for Paper Update

**Critical (Must Fix)**:
1. Audit and fix all data inconsistencies
2. Reconcile figure numbering
3. Fix correlation in fig8
4. Regenerate fig2 with correct data
5. Fix Table 2 formatting

**High Priority**:
1. Create proper per-dimension comparison plot
2. Create category ranking visualization
3. Integrate figures properly in text
4. Convert Table 4 to proper table format
5. Move orphaned figures to appendix or remove

**Medium Priority**:
1. Improve visual design consistency
2. Add missing visualizations (high-skillability threshold, RQ4 candidates)
3. Add uncertainty to visualizations
4. Polish captions and integration

## Next Steps

Create paper_v4_figures.md that:
1. Fixes all data inconsistencies
2. Properly integrates existing figures
3. Creates missing critical visualizations
4. Moves descriptive figures to appendix
5. Ensures all numbers match between text and figures
