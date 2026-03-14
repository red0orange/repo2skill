# Round 5 Review: Final Figure/Table Polish

## Overall Assessment

Figure/table package NOT YET submission-ready for ICSE. Overall visual narrative is strong: moves from dataset overview → score distributions → dimensions → domain patterns → opportunity candidates. But several main-text figures inconsistent with captions, tables, or surrounding claims. These inconsistencies serious enough to undermine trust in results.

## Remaining Issues (BLOCKING)

### 1. RQ3 Category Figures Internally Inconsistent
- **Figure 3**: Described as showing both counts AND mean skillability, but rendered figure only shows counts
- **Figure 4**: Described as ranking categories by mean skillability, but plotted ordering/values don't match Table 3
- **Figure 5**: WORST - Caption/text say Data Retrieval leads and External Service Connectors lowest, but actual chart shows opposite pattern
- **Fix**: Regenerate all three figures from final analysis outputs, then re-check text and captions against regenerated numbers

### 2. RQ4 Correlation Figures Don't Match Statistical Claims
- **Text (lines 519-531)**: Reports Spearman r_s=0.003 and r_s=0.138
- **Figure 7**: Displays both Pearson and Spearman with different in-plot statistics
- **Figure 8**: Displays values that don't match caption or text
- **Fix**: Pick one statistic family, recompute once, make text/captions/figure annotations identical

### 3. Multiple Captions Misdescribe Visual Encoding
- **Figure 6**: Said to be colored by capability category, but actual figure uses continuous skillability color scale
- **Figure 7**: Said to show blue/gray point classes, but actual figure is hexbin density plot
- **Figure 8**: Said to be colored by capability category, but is actually density heatmap
- **Fix**: Either regenerate plots to match captions OR rewrite captions to match plots

### 4. Uneven Figure Integration
- **Table 1**: Presented without real interpretive callout in text
- **Table 4**: Only lightly integrated
- **Language/Granularity sections**: Don't point readers to appendix figures (A1/A2/A3)
- **Fix**: Add explicit references like "Appendix Fig. A1/A2/A3" in RQ3 language/granularity discussion

### 5. Table 4 Looks Selective
- Only 7 categories represented although title implies category-complete summary
- **Fix**: Either include all categories OR rename to "Selected Top Candidates by Category" and explain selection rule

### 6. Figure Density for Two-Column Layout
- **Figure 6**: Repository labels and inline annotations will likely become cramped after downscaling
- **Fix**: Reduce annotation density or move detailed labels to appendix, keep cleaner top-10/top-15 main-text version

## Strengths

1. **Good Story Arc**: Figures 1-2 establish construct, Figures 3-5 localize where it appears, Figures 6-8 operationalize opportunity-finding claim

2. **Strong Core Figures**: Figures 1 and 2 are clear, interpretable, aligned with narrative

3. **Correct Design Decision**: Replacing radar chart with CI-based comparison plot was right choice

4. **Good Table Content**: Tables 2 and 3 contain right statistics for ICSE: means, dispersion, effect sizes, rates

5. **Sensible Organization**: Moving lower-priority descriptive plots to appendix is appropriate

## Final Polish Recommendations

1. **Standardize Figure Style**: One color meaning per figure, one correlation convention, one terminology set for "high-skillability"

2. **Add Table Callouts**: One sentence before each table stating exactly what reader should take away

3. **Add Appendix Cross-References**: From main text where appendix figures support claims

4. **Shorten Captions**: After fixing inconsistencies, some captions repeat too much numeric detail already in text

5. **Check Legibility**: Ensure every main-text figure remains legible at final ACM two-column width, especially label font sizes

## Submission Readiness

**NEEDS MAJOR FIXES**

Package is close conceptually, but current figure inconsistencies are submission-blocking. Once RQ3/RQ4 figures regenerated and reconciled with text/tables, should move to "needs minor fixes" quickly.

## Priority Actions

**Critical (Must Fix Before Submission)**:
1. Regenerate Figure 3 to show both counts AND mean skillability
2. Regenerate Figure 4 with correct category ranking matching Table 3
3. Regenerate Figure 5 with correct ordering (Data Retrieval highest, not lowest)
4. Fix all correlation values to be consistent (pick Spearman or Pearson, use consistently)
5. Fix all caption mismatches (Figures 6, 7, 8)

**High Priority**:
1. Add appendix figure references in text
2. Fix Table 4 scope or rename
3. Add table callouts
4. Reduce Figure 6 annotation density

**Medium Priority**:
1. Standardize figure styling
2. Shorten captions
3. Check two-column legibility

## Next Steps

Create paper_final_v2.md that:
1. Fixes all data inconsistencies in figures
2. Corrects all caption mismatches
3. Adds proper figure integration
4. Ensures all numbers match between text, tables, and figures
5. Ready for ICSE submission
