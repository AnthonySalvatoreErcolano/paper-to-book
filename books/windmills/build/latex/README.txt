Windmills: A Prerequisite Book: LaTeX source

Compile with XeLaTeX (it uses system OpenType fonts):

    xelatex main
    xelatex main
    makeindex main
    xelatex main

Needs a TeX distribution with XeLaTeX and the TeX Gyre and Latin Modern fonts
(TeX Live or MiKTeX both include them; on MiKTeX, missing packages install on first run).

  main.tex           title page, contents, order of the parts, sources list, index
  p2bbook.sty        fonts, page layout, environments, source-note markers, HOL4 notation
  chapters/*.tex     one file per chapter: edit or add chapters here, then \include them in main.tex
  chapters/paper.tex the paper, page by page, with its reader's guide
  paper.pdf          the paper as published

This is a snapshot. The Markdown chapters in the paper-to-book repository remain the
source the pipeline checks; edits made here are not re-checked against the ledger or Lean.
