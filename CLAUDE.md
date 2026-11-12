# paper-to-book

Turns one research paper into a self-contained book: the prerequisites a reader needs,
built up from a stated baseline, ending with the paper itself, printed in full, so
the reader can read it straight through after finishing the book.

This file is the contract for every session that works here. Follow it exactly.

## The hard rules (anti-hallucination)

1. **No claim from memory.** Every definition, theorem statement, historical attribution,
   and prerequisite link in the map or the book must be backed by a **ledger entry**
   (`books/<slug>/ledger.jsonl`) whose `quote` is copied *verbatim* from a source file in
   `books/<slug>/sources/`. Sources get there only by retrieval (see "Fetching").
2. **`python pipeline/p2b.py ledger <slug>` must pass** before a map or chapter is shown to
   the user. It checks every quote really occurs in its source text. A failing quote is
   fixed by re-copying the source text, never by editing the quote to match a belief.
3. **Theorem hypotheses are quoted, not paraphrased.** A `.theorem` or `.definition` block
   carries `ledger=` and its quoted statement; prose explanation goes around it.
4. **Citations only from records.** Bibliography entries come from the paper's own `.bib`/
   bibliography or from fetched Crossref / arXiv / Semantic Scholar metadata. Never type a
   title, year, DOI, page or theorem number from memory.
5. **Mathlib names only from the mathlib source or the Lean report.** A `lean=` name is shown
   as verified only when `books/<slug>/reports/lean.json` says the file checked. Anything
   unverifiable is printed as *not formally checked*; anything unsourced is printed in red
   as UNSOURCED. Never hide either.
6. **Independent review.** Each chapter is reviewed by a separate agent that has not seen the
   writing session's reasoning (`reports/review-chNN.md`), against the sources, before the user
   sees it. The reviewer looks for missing hypotheses, invalid proof steps, notation clashes,
   and any statement not covered by a ledger entry.
7. **Checkpoints belong to the user.** Stop after the map (stage 3) and after each chapter
   (stage 5) for the user's approval. Never write chapters on an unapproved map.

## Stages

| # | Stage | Command / artefact | Gate |
|---|-------|--------------------|------|
| 1 | Start a book | `p2b.py new <slug> --arxiv ID --baseline "…"` | |
| 2 | Retrieve the paper | push → GitHub Actions `fetch` commits `sources/` | |
| 3 | Extract concepts | `p2b.py extract <slug>` → `concepts.json` (definitions, theorems, undefined terms, citations, with line numbers) | |
| 4 | Expand the map | write `map.json` + ledger entries; request sources as needed (`p2b.py request`) | `ledger` + `map` pass |
| — | **Checkpoint 1** | `p2b.py map <slug>` → `build/map.html`; publish it for the user | user approves |
| 5 | Write chapters | `chapters/NN-*.md`, Lean file `lean/Books/<Slug>/ChNN.lean`, checks `checks/chNN_*.py` | ledger + Lean + checks + review pass |
| — | **Checkpoint 2** | `p2b.py build <slug>` → `build/book.pdf`; send to user | user approves each chapter |
| 6 | The paper | `p2b.py build` appends the paper with a reader's guide and per-page margin notes linking concepts to chapters | |
| 7 | Refine later | any edit → re-run ledger/Lean/checks → rebuild | |

`books/<slug>/book.json` records the current stage and approvals (`status`). Update it as you go,
and read it first when resuming a book.

## Fetching (the workspace has no open internet)

Retrieval, Lean, and Python checks run on GitHub Actions, which has full network access:

* Add entries with `python pipeline/p2b.py request <slug> <type> <ref> --why "…"`
  (types: `arxiv`, `url`, `pdf`, `doi`, `s2refs`) and push. The **fetch** workflow downloads them
  raw, extracts text to `sources/<id>/text.txt`, and commits. `git pull` to get them.
* Pushing `lean/**` runs **lean** (mathlib build) and commits `books/*/reports/lean.json`.
* Pushing `books/*/checks/**` runs **checks** (sympy etc.) and commits `reports/checks.json`.

Good open sources: the paper's arXiv source, arXiv papers it cites, nLab, Wikipedia,
ProofWiki, Stacks Project, open textbooks (author PDFs), mathlib docs. Prefer two
independent sources for anything subtle.

## Chapter format

Pandoc Markdown with LaTeX math. Structured blocks are fenced divs:

```
::: {.definition #def-involution ledger=L0003 lean=Function.Involutive}
An **involution** on a set $X$ is a map $f : X \to X$ with $f(f(x)) = x$ for all $x$.
:::

::: {.quote ledger=L0003}
verbatim text from the source, shown set apart and attributed
:::
```

Classes: `definition`, `theorem`, `lemma`, `proposition`, `corollary`, `example`, `proof`,
`exercise`, `quote`, `inpaper` (where the concept is used in the paper), `remark`.
A `definition`/`theorem`/`lemma`/`proposition`/`corollary` without `ledger=` renders as UNSOURCED.

## Layout of a book

```
books/<slug>/
  book.json          title, paper, baseline, status, approvals
  requests/fetch.json
  sources/<id>/      meta.json, raw files, text.txt   (written by the fetch workflow)
  concepts.json      stage 3 output
  map.json           nodes and edges (each edge and node backed by the ledger)
  ledger.jsonl       one claim per line
  chapters/NN-*.md
  checks/*.py        computational checks (run in CI)
  reports/           ledger.json, map.json, lean.json, checks.json, review-chNN.md
  build/             map.html, book.tex, book.pdf
lean/Books/<Slug>/ChNN.lean
```
