# paper-to-book

Give it a research paper; it builds a book of everything you need to read that paper, from a
background you choose, and ends with the paper itself.

* **Sourced:** every definition, theorem, and prerequisite link is backed by a verbatim quotation
  from a retrieved source, checked automatically (`pipeline/p2b.py ledger`).
* **Formally checked:** statements are linked to Lean's mathlib; GitHub Actions builds them and records the result.
* **Reviewed:** each chapter is independently reviewed before you see it, and you approve the map and every chapter.

Start a book by asking Claude: *"make a book from this paper: <arXiv link>"*. The process and its
rules are in [CLAUDE.md](CLAUDE.md).

| Path | What |
|------|------|
| `pipeline/p2b.py` | the command-line tool (new, request, fetch, extract, ledger, map, build, …) |
| `pipeline/pandoc/` | chapter-to-LaTeX filter and the book template |
| `pipeline/map_viewer.html` | interactive prerequisite map |
| `lean/` | Lean project on mathlib (pinned); one folder per book |
| `.github/workflows/` | fetch sources, build Lean, run computational checks |
| `books/<slug>/` | one folder per book |
