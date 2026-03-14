# LaTeX Paper

This directory contains a local ACM-style LaTeX version of the paper based on `paper/paper_v7.md`.

## Files

- `main.tex`: main paper source
- `Makefile`: convenience build target
- `latexmkrc`: local `latexmk` configuration

## Build

From this directory:

```bash
make
```

or:

```bash
latexmk -pdf main.tex
```

The paper references figure assets directly from:

- `../output_large/figures/`
- `../output/validation/figures/`

## Notes

- The source is optimized for local compilation first.
- Citations are preserved using a manual bibliography to avoid adding an extra BibTeX maintenance step while the text is still changing quickly.
- If you later want a camera-ready ACM submission version, the next cleanup step should be splitting `main.tex` into section files and switching the bibliography to a `.bib` database.
