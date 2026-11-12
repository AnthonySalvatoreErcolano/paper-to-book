#!/usr/bin/env python3
"""paper-to-book pipeline.  See CLAUDE.md for the process and the rules.

  p2b.py new <slug> --arxiv ID | --pdf URL  --baseline "calculus; linear algebra; …" [--title …]
  p2b.py request <slug> <arxiv|url|pdf|doi|s2refs> <ref> --why "…" [--id ID]
  p2b.py fetch [<slug> | --all]            (runs in GitHub Actions: downloads requested sources)
  p2b.py extract <slug>                    concepts.json from the paper's LaTeX (or PDF text)
  p2b.py ledger <slug>                     verify every ledger quote against its source text
  p2b.py map <slug>                        check map.json; write build/map.html
  p2b.py lean-names [--all]                write lean/Books/<Slug>/Names.lean (#check every lean= name)
  p2b.py lean-report --log FILE            parse a `lake build` log into books/*/reports/lean.json
  p2b.py checks [--all]                    run books/*/checks/*.py, write reports/checks.json
  p2b.py build <slug>                      chapters + the paper -> build/book.pdf
  p2b.py status <slug>                     where the book stands
"""
import argparse, datetime as dt, difflib, gzip, hashlib, html as htmllib, io, json, re, shutil
import subprocess, sys, tarfile, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOKS = ROOT / "books"
LEAN = ROOT / "lean"
PIPE = ROOT / "pipeline"
UA = "paper-to-book/1.0 (personal study tool; https://github.com/AnthonySalvatoreErcolano/paper-to-book)"
THEOREMISH = ("definition", "theorem", "lemma", "proposition", "corollary")


def die(msg):
    sys.exit("error: " + msg)


def book_dir(slug):
    d = BOOKS / slug
    if not (d / "book.json").exists():
        die(f"no book '{slug}' (books/{slug}/book.json missing)")
    return d


def load_json(p, default=None):
    p = Path(p)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def save_json(p, data):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def pascal(slug):
    return "".join(w.capitalize() for w in re.split(r"[^A-Za-z0-9]+", slug) if w)


# --------------------------------------------------------------------------- text normalisation
LIG = {"ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl", "’": "'", "‘": "'", "“": '"', "”": '"',
       "–": "-", "—": "-", "−": "-", "\u00ad": ""}


def norm(text):
    """Normalise text so a quote copied from a source matches however the source was encoded:
    unicode forms, ligatures, line-break hyphenation, LaTeX markup, case and spacing."""
    t = unicodedata.normalize("NFKC", text)
    for a, b in LIG.items():
        t = t.replace(a, b)
    t = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", t)              # hyphenated line breaks
    t = re.sub(r"\\(?:emph|textit|textbf|mathrm|mathbf|mathit|text|operatorname|mathcal|mathbb)\s*", "", t)
    t = re.sub(r"\\[A-Za-z]+\*?", " ", t)                        # other LaTeX commands
    t = re.sub(r"[{}$~^_\\]", " ", t)
    t = t.lower()
    t = re.sub(r"[^\w]+", " ", t)
    return " ".join(t.split())


# --------------------------------------------------------------------------- new / request
def cmd_new(a):
    d = BOOKS / a.slug
    if (d / "book.json").exists():
        die(f"book '{a.slug}' already exists")
    paper = {"arxiv": a.arxiv} if a.arxiv else {"pdf": a.pdf}
    save_json(d / "book.json", {
        "slug": a.slug, "title": a.title or "", "paper": paper, "paper_source": "paper",
        "baseline": [b.strip() for b in a.baseline.split(";") if b.strip()],
        "created": now(), "status": {"stage": 1, "map_approved": False, "chapters_approved": []},
    })
    for sub in ("sources", "chapters", "checks", "reports", "build"):
        (d / sub).mkdir(parents=True, exist_ok=True)
    (d / "ledger.jsonl").touch()
    save_json(d / "requests" / "fetch.json", [])
    add_request(a.slug, "arxiv" if a.arxiv else "pdf", a.arxiv or a.pdf, "the paper", "paper")
    if a.arxiv:
        add_request(a.slug, "s2refs", a.arxiv, "the paper's references with open-access links", "paper-refs")
    (LEAN / "Books" / pascal(a.slug)).mkdir(parents=True, exist_ok=True)
    print(f"created books/{a.slug}. Commit and push: the fetch workflow will retrieve the paper.")


def add_request(slug, kind, ref, why, rid=None):
    path = BOOKS / slug / "requests" / "fetch.json"
    reqs = load_json(path, [])
    rid = rid or re.sub(r"[^a-z0-9]+", "-", f"{kind}-{ref}".lower()).strip("-")[:60]
    if any(r["id"] == rid for r in reqs):
        print(f"already requested: {rid}")
        return rid
    reqs.append({"id": rid, "type": kind, "ref": ref, "why": why, "requested": now(), "done": False})
    save_json(path, reqs)
    print(f"requested {rid}: {kind} {ref}")
    return rid


def cmd_request(a):
    book_dir(a.slug)
    if a.type not in ("arxiv", "url", "pdf", "doi", "s2refs"):
        die("type must be arxiv, url, pdf, doi or s2refs")
    add_request(a.slug, a.type, a.ref, a.why, a.id)


# --------------------------------------------------------------------------- fetch (CI)
def http_get(url, accept=None):
    import requests
    h = {"User-Agent": UA}
    if accept:
        h["Accept"] = accept
    r = requests.get(url, headers=h, timeout=60)
    r.raise_for_status()
    return r


def pdf_text(data):
    from pypdf import PdfReader
    rd = PdfReader(io.BytesIO(data))
    return "\n\n".join(f"[[page {i + 1}]]\n" + (p.extract_text() or "") for i, p in enumerate(rd.pages))


def html_text(data):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(data, "html.parser")
    for t in soup(["script", "style", "nav", "header", "footer"]):
        t.decompose()
    # keep the TeX of rendered maths (MathJax/KaTeX/Wikipedia alt text) so formulas can be quoted
    for img in soup.find_all("img", alt=True):
        img.replace_with(" " + img["alt"] + " ")
    for ann in soup.find_all("annotation"):
        ann.replace_with(" " + ann.get_text() + " ")
    return "\n".join(l.strip() for l in soup.get_text("\n").splitlines() if l.strip())


def fetch_one(slug, req):
    out = BOOKS / slug / "sources" / req["id"]
    out.mkdir(parents=True, exist_ok=True)
    meta = {"id": req["id"], "type": req["type"], "ref": req["ref"], "why": req.get("why", ""),
            "fetched": now(), "files": {}}

    def keep(name, data):
        (out / name).write_bytes(data)
        meta["files"][name] = hashlib.sha256(data).hexdigest()

    kind, ref = req["type"], req["ref"]
    if kind == "arxiv":
        aid = re.sub(r"^(arxiv:|https?://arxiv\.org/(abs|pdf)/)", "", ref, flags=re.I).removesuffix(".pdf")
        api = http_get(f"https://export.arxiv.org/api/query?id_list={aid}").text
        keep("arxiv-meta.xml", api.encode())
        absp = http_get(f"https://arxiv.org/abs/{aid}").text
        m = re.search(r'href="(https?://[^"]*(?:creativecommons|licenses)[^"]*)"', absp)
        meta["license"] = m.group(1) if m else "arXiv non-exclusive license (default)"
        meta["title"] = " ".join(re.search(r"<entry>.*?<title>(.*?)</title>", api, re.S).group(1).split())
        meta["authors"] = re.findall(r"<author>\s*<name>(.*?)</name>", api)
        pdf = http_get(f"https://arxiv.org/pdf/{aid}").content
        keep("paper.pdf", pdf)
        texts = [pdf_text(pdf)]
        try:
            src = http_get(f"https://arxiv.org/e-print/{aid}").content
            keep("source.bin", src)
            sdir = out / "src"
            sdir.mkdir(exist_ok=True)
            try:
                with tarfile.open(fileobj=io.BytesIO(src)) as tf:
                    for mbr in tf.getmembers():
                        if mbr.isfile() and ".." not in mbr.name and not mbr.name.startswith("/"):
                            tf.extract(mbr, sdir)
            except tarfile.ReadError:
                (sdir / "main.tex").write_bytes(gzip.decompress(src) if src[:2] == b"\x1f\x8b" else src)
            meta["latex"] = sorted(str(p.relative_to(out)) for p in sdir.rglob("*.tex"))
            texts.append(latex_text(sdir))
        except Exception as e:                                  # some papers have PDF only
            meta["latex_error"] = str(e)
        (out / "text.txt").write_text("\n\n".join(texts), encoding="utf-8")
    elif kind in ("url", "pdf"):
        r = http_get(ref)
        data = r.content
        is_pdf = kind == "pdf" or data[:4] == b"%PDF"
        keep("raw.pdf" if is_pdf else "raw.html", data)
        meta["final_url"] = r.url
        (out / "text.txt").write_text(pdf_text(data) if is_pdf else html_text(data), encoding="utf-8")
    elif kind == "doi":
        j = http_get(f"https://api.crossref.org/works/{ref}").json()["message"]
        keep("crossref.json", json.dumps(j, indent=1).encode())
        meta["title"] = (j.get("title") or [""])[0]
        (out / "text.txt").write_text(json.dumps(j, indent=1), encoding="utf-8")
    elif kind == "s2refs":
        aid = ref if ref.startswith(("arXiv:", "DOI:")) else f"arXiv:{ref}"
        fields = "title,authors,year,venue,externalIds,openAccessPdf,url"
        j = http_get(f"https://api.semanticscholar.org/graph/v1/paper/{aid}/references?fields={fields}&limit=1000").json()
        keep("references.json", json.dumps(j, indent=1).encode())
        lines = []
        for item in j.get("data", []):
            p = item.get("citedPaper") or {}
            lines.append(f"{p.get('title')} | {', '.join(a.get('name', '') for a in p.get('authors') or [])} | "
                         f"{p.get('year')} | {json.dumps(p.get('externalIds'))} | {(p.get('openAccessPdf') or {}).get('url')}")
        (out / "text.txt").write_text("\n".join(lines), encoding="utf-8")
    save_json(out / "meta.json", meta)


def strip_comments(tex):
    """LaTeX comments never appear in the published paper, so they must not be quotable."""
    return re.sub(r"(?<!\\)%.*", "", tex)


def latex_text(sdir):
    return "\n".join(strip_comments(p.read_text(encoding="utf-8", errors="replace")) for p in sorted(sdir.rglob("*.tex")))


def cmd_retext(a):
    """Rebuild a source's text.txt from its raw files (after a change to text extraction)."""
    out = book_dir(a.slug) / "sources" / a.id
    meta = load_json(out / "meta.json")
    parts = []
    for name in ("paper.pdf", "raw.pdf"):
        if (out / name).exists():
            parts.append(pdf_text((out / name).read_bytes()))
    if (out / "raw.html").exists():
        parts.append(html_text((out / "raw.html").read_bytes()))
    if (out / "src").exists():
        parts.append(latex_text(out / "src"))
    (out / "text.txt").write_text("\n\n".join(parts), encoding="utf-8")
    meta["retexted"] = now()
    save_json(out / "meta.json", meta)
    print(f"rebuilt sources/{a.id}/text.txt ({sum(len(x.split()) for x in parts)} words)")


def cmd_fetch(a):
    slugs = [p.parent.parent.name for p in BOOKS.glob("*/requests/fetch.json")] if a.all else [a.slug]
    failed = 0
    for slug in slugs:
        path = BOOKS / slug / "requests" / "fetch.json"
        reqs = load_json(path, [])
        for req in reqs:
            if req.get("done"):
                continue
            try:
                fetch_one(slug, req)
                req["done"], req["error"] = True, None
                print(f"fetched {slug}/{req['id']}")
            except Exception as e:
                req["error"] = f"{e.__class__.__name__}: {e}"
                failed += 1
                print(f"FAILED {slug}/{req['id']}: {req['error']}")
        save_json(path, reqs)
    if failed:
        print(f"{failed} request(s) failed; see requests/fetch.json")


# --------------------------------------------------------------------------- extract
def paper_source_dir(d):
    return d / "sources" / "paper"


def main_tex(src):
    texs = sorted(src.rglob("*.tex"))
    for t in texs:
        if r"\documentclass" in t.read_text(encoding="utf-8", errors="replace"):
            return t
    return texs[0] if texs else None


def flatten(tex, seen=None):
    seen = seen or set()
    if tex in seen or not tex.exists():
        return ""
    seen.add(tex)
    text = tex.read_text(encoding="utf-8", errors="replace")
    text = re.sub(r"(?<!\\)%.*", "", text)

    def inc(m):
        name = m.group(1).strip()
        p = (tex.parent / name)
        if not p.suffix:
            p = p.with_suffix(".tex")
        return flatten(p, seen)
    return re.sub(r"\\(?:input|include)\{([^}]+)\}", inc, text)


def cmd_extract(a):
    d = book_dir(a.slug)
    src = paper_source_dir(d)
    if not (src / "meta.json").exists():
        die("the paper hasn't been fetched yet (push, wait for the fetch workflow, then git pull)")
    out = {"paper": load_json(src / "meta.json"), "environments": [], "emphasised": [], "citations": [],
           "bibliography": [], "sections": []}
    tex = main_tex(src / "src") if (src / "src").exists() else None
    if tex:
        text = flatten(tex)
        lines = text.splitlines()
        names = {"definition": "definition", "theorem": "theorem", "lemma": "lemma", "proposition": "proposition",
                 "corollary": "corollary", "example": "example", "remark": "remark"}
        for m in re.finditer(r"\\newtheorem\*?\{(\w+)\}(?:\[\w+\])?\{([^}]+)\}", text):
            names[m.group(1)] = m.group(2).lower()

        def line_of(pos):
            return text.count("\n", 0, pos) + 1
        for env, kind in names.items():                      # one search per environment type
            pat = r"\\begin\{" + re.escape(env) + r"\*?\}(\[[^\]]*\])?(.*?)\\end\{" + re.escape(env) + r"\*?\}"
            for m in re.finditer(pat, text, re.S):
                out["environments"].append({"kind": kind, "label": (m.group(1) or "").strip("[]"),
                                            "line": line_of(m.start()), "text": " ".join(m.group(2).split())[:1500]})
        out["environments"].sort(key=lambda e: e["line"])
        for m in re.finditer(r"\\(?:emph|textit|textbf)\{([^{}]{3,80})\}", text):
            out["emphasised"].append({"term": " ".join(m.group(1).split()), "line": line_of(m.start())})
        for m in re.finditer(r"\\(sub)*section\*?\{([^}]*)\}", text):
            out["sections"].append({"level": 1 + (len(m.group(1) or "") // 3), "title": m.group(2), "line": line_of(m.start())})
        for m in re.finditer(r"\\cite[pt]?\*?(?:\[[^\]]*\])?\{([^}]+)\}", text):
            ctx = " ".join(text[max(0, m.start() - 200):m.end() + 80].split())
            for key in m.group(1).split(","):
                out["citations"].append({"key": key.strip(), "line": line_of(m.start()), "context": ctx})
        for bib in list(src.rglob("*.bbl")) + list(src.rglob("*.bib")):
            out["bibliography"].append({"file": str(bib.relative_to(src)),
                                        "text": bib.read_text(encoding="utf-8", errors="replace")[:200000]})
        out["latex_main"] = str(tex.relative_to(src))
    else:
        out["note"] = "no LaTeX source; work from text.txt (PDF text)"
    save_json(d / "concepts.json", out)
    print(f"concepts.json: {len(out['environments'])} environments, {len(out['emphasised'])} emphasised terms, "
          f"{len(set(c['key'] for c in out['citations']))} cited works, {len(out['sections'])} sections")


# --------------------------------------------------------------------------- ledger
def read_ledger(d):
    out = []
    for n, line in enumerate((d / "ledger.jsonl").read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                e = json.loads(line)
            except json.JSONDecodeError as ex:
                die(f"ledger.jsonl line {n}: {ex}")
            e["_line"] = n
            out.append(e)
    return out


_src_cache = {}


def source_text(d, sid):
    key = (str(d), sid)
    if key not in _src_cache:
        p = d / "sources" / sid / "text.txt"
        _src_cache[key] = norm(p.read_text(encoding="utf-8", errors="replace")) if p.exists() else None
    return _src_cache[key]


def check_ledger(d, quiet=False):
    entries = read_ledger(d)
    report, ids = {}, set()
    for e in entries:
        eid = e.get("id", f"line{e['_line']}")
        problems = []
        if eid in ids:
            problems.append("duplicate id")
        ids.add(eid)
        for f in ("id", "kind", "claim", "source", "quote"):
            if not e.get(f):
                problems.append(f"missing '{f}'")
        if e.get("kind") == "edge" and not (e.get("from") and e.get("to")):
            problems.append("edge entries need 'from' and 'to'")
        text = source_text(d, e.get("source", "")) if e.get("source") else None
        if e.get("source") and text is None:
            problems.append(f"source '{e['source']}' not fetched (no sources/{e['source']}/text.txt)")
        q = norm(e.get("quote", ""))
        if text is not None and q:
            if len(q) < 20:
                problems.append("quote too short to be checkable (under 20 characters)")
            elif q not in text:
                sm = difflib.SequenceMatcher(None, text, q, autojunk=False)
                blk = max(sm.get_matching_blocks(), key=lambda b: b.size)
                near = text[max(0, blk.a - 40): blk.a + len(q) + 40]
                problems.append(f"quote NOT found in source; nearest text: «{near[:300]}»")
        report[eid] = {"ok": not problems, "problems": problems, "kind": e.get("kind"), "source": e.get("source"),
                       "node": e.get("node"), "from": e.get("from"), "to": e.get("to")}
    save_json(d / "reports" / "ledger.json", {"checked": now(), "entries": report})
    bad = {k: v for k, v in report.items() if not v["ok"]}
    if not quiet:
        print(f"ledger: {len(report)} entries, {len(report) - len(bad)} verified, {len(bad)} failing")
        for k, v in bad.items():
            print(f"  ✗ {k}: " + "; ".join(v["problems"]))
    return report, entries


def cmd_ledger(a):
    report, _ = check_ledger(book_dir(a.slug))
    if any(not v["ok"] for v in report.values()):
        sys.exit(1)


# --------------------------------------------------------------------------- map
def check_map(d, quiet=False):
    m = load_json(d / "map.json")
    if not m:
        die("no map.json yet")
    ledger, entries = check_ledger(d, quiet=True)
    nodes = {n["id"]: n for n in m["nodes"]}
    problems = []
    for n in m["nodes"]:
        for r in n.get("requires", []):
            if r not in nodes:
                problems.append(f"{n['id']}: requires unknown node '{r}'")
    # acyclic + topological order (Kahn)
    indeg = {k: 0 for k in nodes}
    for n in nodes.values():
        for r in n.get("requires", []):
            if r in nodes:
                indeg[n["id"]] += 1
    order, ready = [], sorted(k for k, v in indeg.items() if v == 0)
    users = {k: [n["id"] for n in nodes.values() if k in n.get("requires", [])] for k in nodes}
    while ready:
        k = ready.pop(0)
        order.append(k)
        for u in users[k]:
            indeg[u] -= 1
            if indeg[u] == 0:
                ready.append(u)
    if len(order) != len(nodes):
        problems.append("the map has a cycle among: " + ", ".join(k for k in nodes if k not in order))
    # grounding: every non-baseline node has a verified definition; every edge a verified edge entry
    by_def = {e["node"] for e in entries if e.get("kind") in ("definition", "theorem") and ledger.get(e["id"], {}).get("ok")}
    edge_ok = {}
    for e in entries:
        if e.get("kind") == "edge":
            ok = ledger.get(e["id"], {}).get("ok")
            tgt = nodes.get(e["to"])
            if ok and tgt:
                terms = [norm(t) for t in tgt.get("terms", [tgt.get("title", "")]) if t]
                if not any(t and t in norm(e["quote"]) for t in terms):
                    problems.append(f"edge {e['id']} ({e['from']} → {e['to']}): quote doesn't mention any term of '{e['to']}'")
                    ok = False
            edge_ok.setdefault((e["from"], e["to"]), False)
            edge_ok[(e["from"], e["to"])] |= bool(ok)
    status = {}
    for n in m["nodes"]:
        st = {"defined": n.get("baseline") or n["id"] in by_def, "edges": {}}
        if not st["defined"]:
            problems.append(f"{n['id']}: no verified definition in the ledger")
        for r in n.get("requires", []):
            # a link down to the assumed background needs no citation; every other link does
            st["edges"][r] = edge_ok.get((n["id"], r), False) or bool(nodes.get(r, {}).get("baseline"))
            if not st["edges"][r]:
                problems.append(f"edge {n['id']} → {r}: no verified ledger entry")
        status[n["id"]] = st
    rep = {"checked": now(), "order": order, "problems": problems, "nodes": status}
    save_json(d / "reports" / "map.json", rep)
    if not quiet:
        print(f"map: {len(nodes)} nodes, {sum(len(n.get('requires', [])) for n in nodes.values())} edges, "
              f"{len(problems)} problems")
        for p in problems:
            print("  ✗ " + p)
    return m, rep


def cmd_map(a):
    d = book_dir(a.slug)
    m, rep = check_map(d)
    book = load_json(d / "book.json")
    lean = load_json(d / "reports" / "lean.json", {}) or {}
    ledger = load_json(d / "reports" / "ledger.json", {}).get("entries", {})
    entries = {e["id"]: e for e in read_ledger(d)}
    data = {"book": book, "map": m, "report": rep, "lean": lean.get("names", {}),
            "ledger": {k: {**entries[k], **v} for k, v in ledger.items() if k in entries}}
    tpl = (PIPE / "map_viewer.html").read_text(encoding="utf-8")
    out = d / "build" / "map.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(tpl.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False).replace("</", "<\\/")),
                   encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}")
    if rep["problems"]:
        sys.exit(1)


# --------------------------------------------------------------------------- Lean
LEAN_ATTR = re.compile(r"\blean=([^\s}]+)")


def lean_names(d):
    names = set()
    for ch in sorted((d / "chapters").glob("*.md")):
        for m in LEAN_ATTR.finditer(ch.read_text(encoding="utf-8")):
            names.update(x for x in m.group(1).strip("\"'").split(",") if x)
    m = load_json(d / "map.json", {}) or {}
    for n in m.get("nodes", []):
        names.update(n.get("mathlib", []))
    return sorted(names)


def cmd_lean_names(a):
    slugs = [p.parent.name for p in BOOKS.glob("*/book.json")] if a.all else [a.slug]
    imports = []
    for slug in slugs:
        d = book_dir(slug)
        mod = pascal(slug)
        folder = LEAN / "Books" / mod
        folder.mkdir(parents=True, exist_ok=True)
        chapters = sorted(p.stem for p in folder.glob("Ch*.lean"))
        lines = ["-- Generated by pipeline/p2b.py lean-names: one #check per Lean name the book uses.",
                 "import Mathlib"] + [f"import Books.{mod}.{c}" for c in chapters] + ["", "open Book"]
        names = lean_names(d)
        for n in names:
            lines.append(f"#check @{n}  -- p2b:name {n}")
        (folder / "Names.lean").write_text("\n".join(lines) + "\n", encoding="utf-8")
        imports += [f"import Books.{mod}.{c}" for c in chapters] + [f"import Books.{mod}.Names"]
        print(f"{slug}: {len(names)} names, {len(chapters)} chapter files")
    (LEAN / "Books.lean").write_text("\n".join(["-- Generated by p2b.py lean-names"] + imports) + "\n", encoding="utf-8")


def cmd_lean_report(a):
    log = Path(a.log).read_text(encoding="utf-8", errors="replace")
    # lines like:  error: ././Books/Zagier/Ch02.lean:14:2: unknown identifier ...
    diag = re.compile(r"(error|warning): (?:\./)*(Books/[^:]+\.lean):(\d+):(\d+): (.*)")
    issues = {}
    for m in diag.finditer(log):
        issues.setdefault(m.group(2), []).append({"level": m.group(1), "line": int(m.group(3)), "message": m.group(5)[:500]})
    built = "Build completed successfully" in log or re.search(r"\bBuilt Books\b", log) is not None
    for slug_dir in BOOKS.glob("*/book.json"):
        slug = slug_dir.parent.name
        mod = pascal(slug)
        folder = LEAN / "Books" / mod
        files, names = {}, {}
        for f in sorted(folder.glob("*.lean")):
            rel = f"Books/{mod}/{f.name}"
            iss = issues.get(rel, [])
            errs = [i for i in iss if i["level"] == "error"]
            sorry = [i for i in iss if "sorry" in i["message"]]
            files[f.name] = {"ok": not errs and not sorry, "errors": errs, "sorry": sorry,
                             "warnings": [i for i in iss if i["level"] == "warning" and i not in sorry]}
            if f.name == "Names.lean":
                src_lines = f.read_text(encoding="utf-8").splitlines()
                bad_lines = {i["line"] for i in errs}
                for ln, text in enumerate(src_lines, 1):
                    m = re.search(r"-- p2b:name (\S+)", text)
                    if m:
                        names[m.group(1)] = ln not in bad_lines
        save_json(BOOKS / slug / "reports" / "lean.json",
                  {"checked": now(), "build_ok": built and not any(i["level"] == "error" for v in issues.values() for i in v),
                   "files": files, "names": names})
        print(f"{slug}: {sum(1 for v in names.values() if v)}/{len(names)} names verified; "
              f"{sum(1 for v in files.values() if v['ok'])}/{len(files)} files clean")


# --------------------------------------------------------------------------- computational checks (CI)
def cmd_checks(a):
    slugs = [p.parent.name for p in BOOKS.glob("*/book.json")] if a.all else [a.slug]
    for slug in slugs:
        d = book_dir(slug)
        res = {}
        for f in sorted((d / "checks").glob("*.py")):
            try:
                r = subprocess.run([sys.executable, str(f)], capture_output=True, text=True, timeout=600, cwd=f.parent)
                res[f.name] = {"ok": r.returncode == 0, "stdout": r.stdout[-4000:], "stderr": r.stderr[-4000:]}
            except subprocess.TimeoutExpired:
                res[f.name] = {"ok": False, "stdout": "", "stderr": "timed out after 600 s"}
        save_json(d / "reports" / "checks.json", {"checked": now(), "checks": res})
        print(f"{slug}: {sum(v['ok'] for v in res.values())}/{len(res)} checks passed")


# --------------------------------------------------------------------------- build
def tex_escape(s):
    rep = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
           "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(rep.get(c, c) for c in s)


def cmd_build(a):
    d = book_dir(a.slug)
    book = load_json(d / "book.json")
    ledger, entries = check_ledger(d, quiet=True)
    m = load_json(d / "map.json", {"nodes": []}) or {"nodes": []}
    lean = load_json(d / "reports" / "lean.json", {}) or {}
    sources = {}
    for meta in sorted((d / "sources").glob("*/meta.json")):
        j = load_json(meta)
        sources[j["id"]] = j.get("title") or j.get("final_url") or j.get("ref")
    ent = {e["id"]: e for e in entries}
    status = {
        "ledger_ok": sorted(k for k, v in ledger.items() if v["ok"]),
        "ledger_source": {k: e.get("source", "") for k, e in ent.items()},
        "ledger_locator": {k: e.get("locator", "") for k, e in ent.items()},
        "source_label": sources,
        "lean_ok": sorted(k for k, v in (lean.get("names") or {}).items() if v),
        "lean_checked": sorted((lean.get("names") or {}).keys()),
    }
    bdir = d / "build"
    bdir.mkdir(exist_ok=True)
    save_json(bdir / "status.json", {"p2b": status})
    chapters = sorted((d / "chapters").glob("*.md"))
    if not chapters:
        die("no chapters yet")
    body = []
    for ch in chapters:
        r = subprocess.run(["pandoc", str(ch), "-f", "markdown+tex_math_dollars+fenced_divs+bracketed_spans",
                            "-t", "latex", "--top-level-division=chapter",
                            "--lua-filter", str(PIPE / "pandoc" / "book.lua"),
                            "--metadata-file", str(bdir / "status.json")],
                           capture_output=True, text=True)
        if r.returncode:
            die(f"pandoc failed on {ch.name}:\n{r.stderr}")
        body.append(r.stdout)
    # the paper, with a reader's guide and per-page margin notes
    paper_pdf = d / "sources" / book.get("paper_source", "paper") / "paper.pdf"
    if not paper_pdf.exists():
        alt = d / "sources" / book.get("paper_source", "paper") / "raw.pdf"
        paper_pdf = alt if alt.exists() else None
    paper_part = paper_part_tex(d, book, m, paper_pdf, chapters)
    tpl = (PIPE / "pandoc" / "book.tex").read_text(encoding="utf-8")
    pmeta = load_json(d / "sources" / book.get("paper_source", "paper") / "meta.json", {}) or {}
    title = book.get("title") or pmeta.get("title") or book["slug"]
    tex = (tpl.replace("%%TITLE%%", tex_escape(title))
              .replace("%%SUBTITLE%%", tex_escape("A prerequisite book for " + (pmeta.get("title") or "the paper")))
              .replace("%%AUTHORS%%", tex_escape(", ".join(pmeta.get("authors", []))))
              .replace("%%BASELINE%%", tex_escape("; ".join(book.get("baseline", []))))
              .replace("%%BODY%%", "\n".join(body))
              .replace("%%PAPER%%", paper_part)
              .replace("%%SOURCES%%", sources_tex(d, ent, ledger, sources)))
    (bdir / "book.tex").write_text(tex, encoding="utf-8")
    for _ in range(3):                                       # contents, references, index
        r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", "book.tex"],
                           cwd=bdir, capture_output=True, text=True)
        if r.returncode:
            die("xelatex failed:\n" + r.stdout[-3000:])
        subprocess.run(["makeindex", "-q", "book.idx"], cwd=bdir, capture_output=True)
    print(f"wrote {(bdir / 'book.pdf').relative_to(ROOT)}")


def paper_part_tex(d, book, m, paper_pdf, chapters):
    if not paper_pdf:
        return r"\part{The Paper}\chapter*{The paper}(The paper's PDF has not been fetched.)"
    from pypdf import PdfReader
    rd = PdfReader(str(paper_pdf))
    chap_of = {}
    for i, ch in enumerate(chapters, 1):
        fm = re.match(r"---\n(.*?)\n---", ch.read_text(encoding="utf-8"), re.S)
        nodes = re.findall(r"[\w-]+", re.search(r"node:\s*\[?([^\]\n]*)", fm.group(1)).group(1)) if fm and "node:" in fm.group(1) else []
        for n in nodes:
            chap_of.setdefault(n, i)
    terms = []
    for n in m.get("nodes", []):
        if n["id"] in chap_of:
            for t in n.get("terms", [n.get("title", "")]):
                if t:
                    terms.append((norm(t), n.get("title", n["id"]), chap_of[n["id"]]))
    pages = []
    guide_rows = {}
    for i, p in enumerate(rd.pages, 1):
        t = " " + norm(p.extract_text() or "") + " "
        hits = {}
        for nt, title, ch in terms:
            if nt and f" {nt} " in t:
                hits.setdefault(title, ch)
        notes = sorted(hits.items(), key=lambda x: x[1])[:9]
        for title, ch in notes:
            guide_rows.setdefault(title, (ch, i))
        note = r"\\".join(rf"{tex_escape(tt)} \hfill Ch.~{ch}" for tt, ch in notes) or r"\textit{}"
        pages.append(rf"\includepdf[pages={i},scale=0.86,offset=-0.55in 0in,pagecommand={{\papernote{{{note}}}}}]{{{paper_pdf.resolve()}}}")
    rows = "\n".join(rf"{tex_escape(t)} & Chapter~{c} & p.~{p} of the paper\\" for t, (c, p) in
                     sorted(guide_rows.items(), key=lambda x: (x[1][1], x[1][0])))
    return (r"\part{The Paper}" "\n" r"\chapter*{Reader's guide to the paper}\addcontentsline{toc}{chapter}{Reader's guide to the paper}"
            "\nThe paper follows exactly as published. In the margin of each page are the concepts from this book "
            "that appear on it, with the chapter that teaches them. The first appearance of each:\n\n"
            r"\begin{longtable}{p{0.5\textwidth}ll}" "\n" + rows + "\n" r"\end{longtable}" "\n"
            + "\n".join(pages))


def sources_tex(d, ent, ledger, labels):
    used = sorted({e.get("source") for e in ent.values() if e.get("source")})
    items = []
    for sid in used:
        meta = load_json(d / "sources" / sid / "meta.json", {}) or {}
        where = meta.get("final_url") or meta.get("ref") or ""
        if meta.get("type") == "arxiv":
            where = f"arXiv:{meta.get('ref')}"
        n = sum(1 for e in ent.values() if e.get("source") == sid)
        ok = sum(1 for k, e in ent.items() if e.get("source") == sid and ledger.get(k, {}).get("ok"))
        items.append(rf"\item[\texttt{{{tex_escape(sid)}}}] {tex_escape(labels.get(sid) or '')}. "
                     rf"\url{{{where}}} --- {ok} of {n} quotations verified (retrieved {tex_escape(meta.get('fetched', '')[:10])}).")
    return r"\begin{description}" + "\n".join(items) + r"\end{description}" if items else "(none)"


# --------------------------------------------------------------------------- status
def cmd_status(a):
    d = book_dir(a.slug)
    b = load_json(d / "book.json")
    reqs = load_json(d / "requests" / "fetch.json", [])
    print(f"{b['slug']}: stage {b['status']['stage']}, map approved: {b['status']['map_approved']}, "
          f"chapters approved: {b['status']['chapters_approved']}")
    print(f"  sources: {sum(r.get('done', False) for r in reqs)}/{len(reqs)} fetched"
          + "".join(f"\n    ✗ {r['id']}: {r['error']}" for r in reqs if r.get("error")))
    for name in ("ledger", "map", "lean", "checks"):
        rep = load_json(d / "reports" / f"{name}.json")
        print(f"  {name}: {'checked ' + rep['checked'] if rep else 'not run yet'}")
    print(f"  chapters: {', '.join(p.name for p in sorted((d / 'chapters').glob('*.md'))) or 'none'}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("new"); p.add_argument("slug"); g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--arxiv"); g.add_argument("--pdf"); p.add_argument("--baseline", required=True); p.add_argument("--title")
    p = sp.add_parser("request"); p.add_argument("slug"); p.add_argument("type"); p.add_argument("ref")
    p.add_argument("--why", required=True); p.add_argument("--id")
    p = sp.add_parser("fetch"); p.add_argument("slug", nargs="?"); p.add_argument("--all", action="store_true")
    p = sp.add_parser("retext"); p.add_argument("slug"); p.add_argument("id")
    for name in ("extract", "ledger", "map", "build", "status"):
        sp.add_parser(name).add_argument("slug")
    p = sp.add_parser("lean-names"); p.add_argument("slug", nargs="?"); p.add_argument("--all", action="store_true")
    p = sp.add_parser("lean-report"); p.add_argument("--log", required=True)
    p = sp.add_parser("checks"); p.add_argument("slug", nargs="?"); p.add_argument("--all", action="store_true")
    a = ap.parse_args()
    {"new": cmd_new, "request": cmd_request, "fetch": cmd_fetch, "extract": cmd_extract, "ledger": cmd_ledger,
     "map": cmd_map, "lean-names": cmd_lean_names, "lean-report": cmd_lean_report, "checks": cmd_checks,
     "build": cmd_build, "status": cmd_status, "retext": cmd_retext}[a.cmd](a)


if __name__ == "__main__":
    main()
