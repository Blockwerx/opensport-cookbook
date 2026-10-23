#!/usr/bin/env python3
"""Fidelity check: does every figure and link in a rendered brief come from the
MCP payloads it was built from?

Deterministic and stdlib-only, so it can run as a gate in any scheduler. It does
not judge wording -- that is the brief-critic's job. It answers two questions
the critic cannot answer reliably by reading:

1. Every number in the brief matches, at the brief's own display precision, a
   value in the saved MCP payloads -- or one of the derived counts the skill's
   rules define (the denominator funnel), verified against those payloads.
   A number next to a statistic word ("maximum", "median", "average") must also
   come from a field whose own name or description carries that statistic, so a
   median quoted as a maximum fails even though the value matches. A number next
   to a review / feedback word fails unless a payload field is about reviews --
   no OpenSport MCP tool returns one today.

2. Every link uses the configured platform host, carries no unfilled template
   placeholder, matches a route in references/link-targets.md, and names ids
   that exist in the payloads (an alert link's athlete and alert must be one
   alert row).

Usage:
  check_fidelity.py --brief brief.html --payloads payloads/ [--run run.json]
                    [--config ../assets/brief-config.json] [--json]

Exit status: 0 pass, 1 fail, 2 bad input. See references/fidelity-check.md.
"""
from __future__ import annotations

import argparse
import html.parser
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG = HERE.parent / "assets" / "brief-config.json"

# --------------------------------------------------------------------------
# Vocabulary
# --------------------------------------------------------------------------

# A brief word on the left obliges the matched field to carry one of the
# provenance tokens on the right. "review" has no MCP field today, so any
# number beside those words fails -- that is the point.
CONCEPTS: dict[str, tuple[set[str], set[str]]] = {
    "max": ({"max", "maximum", "peak", "highest"}, {"max", "maximum", "peak", "highest"}),
    "median": ({"median"}, {"median"}),
    "mean": ({"average", "mean", "avg"}, {"average", "mean", "avg"}),
    "min": ({"min", "minimum", "lowest"}, {"min", "minimum", "lowest"}),
    "review": (
        {"review", "reviewed", "reviews", "actioned", "acknowledged", "intervention",
         "interventions", "feedback", "loop"},
        {"review", "reviewed", "reviews", "actioned", "acknowledged", "intervention",
         "interventions", "feedback"},
    ),
}
CONTEXT_WORDS = 3  # words either side of a number that can attach a concept

# Keys whose string value describes the numbers beside it.
DESCRIPTOR_KEYS = {
    "alertType", "alertTypes", "definition", "title", "valueLabel", "bandText",
    "metric", "label", "name", "description", "baselineLabel", "baselineType",
    "aggregationType", "valueType", "unit", "observedValueUnit", "categoryLabel",
}

# The derived counts the skill's rules define (SKILL.md steps 2-3, rule 1).
DERIVED_NAMES = {
    "roster", "trained", "noSessionInWindow", "unclassified", "alerted", "red",
    "flagged", "carded", "screened",
}
SUBSETS = [("carded", "flagged"), ("flagged", "trained"), ("red", "alerted"),
           ("trained", "roster"), ("noSessionInWindow", "roster"),
           ("unclassified", "roster"), ("alerted", "roster"), ("screened", "roster")]
DISJOINT = [("trained", "noSessionInWindow"), ("trained", "unclassified"),
            ("noSessionInWindow", "unclassified")]
RATES = [("flagged", "trained"), ("red", "alerted"), ("carded", "flagged")]

MONTHS = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}

PLACEHOLDER = re.compile(r"\{\{[^{}]*\}\}|\{\{|\}\}|%7B%7B|%7D%7D", re.I)

# --------------------------------------------------------------------------
# Payload side
# --------------------------------------------------------------------------


@dataclass
class Candidate:
    value: float
    source: str           # human-readable path, e.g. 03-get_acr.json:result.ratio
    tokens: frozenset     # provenance tokens for the concept check
    athlete: str | None = None  # whose payload it came from; None = squad-wide


@dataclass
class Payloads:
    numbers: list[Candidate] = field(default_factory=list)
    dates: dict[tuple[int, int, int], str] = field(default_factory=dict)
    times: dict[str, str] = field(default_factory=dict)
    strings: set[str] = field(default_factory=set)
    # (athleteId or None, alertId) for every alert row
    alert_rows: list[tuple[str | None, str]] = field(default_factory=list)
    # athleteId -> set of session dates seen on that athlete's alert rows
    athlete_dates: dict[str, set[str]] = field(default_factory=dict)
    athlete_ids: set[str] = field(default_factory=set)


def split_tokens(text: str) -> set[str]:
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    return {t for t in re.split(r"[^a-z0-9]+", text.lower()) if t}


ISO_DATE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2}))?")


def load_payloads(paths: list[Path]) -> Payloads:
    p = Payloads()
    files: list[Path] = []
    for path in paths:
        files.extend(sorted(path.glob("*.json")) if path.is_dir() else [path])
    if not files:
        raise ValueError("no payload files found")
    for f in files:
        doc = json.loads(f.read_text())
        context_athlete = None
        if isinstance(doc, dict) and "result" in doc and "tool" in doc:
            args = doc.get("arguments") or {}
            context_athlete = args.get("athleteId")
            if context_athlete:
                p.athlete_ids.add(context_athlete)
            label = f"{f.name}:{doc['tool']}"
            doc = doc["result"]
        else:
            label = f.name
        _walk_result(doc, label, p, context_athlete)
    return p


def _walk_result(doc, label, p, athlete):
    """An MCP CallToolResult carries JSON as text items; unwrap them."""
    if isinstance(doc, dict) and isinstance(doc.get("content"), list):
        for i, item in enumerate(doc["content"]):
            text = item.get("text") if isinstance(item, dict) else None
            if not isinstance(text, str):
                continue
            try:
                inner = json.loads(text)
            except ValueError:
                _add_prose(text, f"{label}.content[{i}] (headline)", set(), p, athlete)
                continue
            _walk(inner, f"{label}.content[{i}]", p, athlete, [])
        if "structuredContent" in doc:
            _walk(doc["structuredContent"], f"{label}.structuredContent", p, athlete, [])
    else:
        _walk(doc, label, p, athlete, [])


def _walk(node, path, p, athlete, keys):
    if isinstance(node, dict):
        descr = set()
        for k in DESCRIPTOR_KEYS & node.keys():
            v = node[k]
            for s in (v if isinstance(v, list) else [v]):
                if isinstance(s, str):
                    descr |= split_tokens(s)
        row_athlete = node.get("athleteId") or athlete
        if isinstance(node.get("athleteId"), str):
            p.athlete_ids.add(node["athleteId"])
        if isinstance(node.get("alertId"), str):
            p.alert_rows.append((row_athlete, node["alertId"]))
            _collect_session_dates(node, row_athlete, p)
        for k, v in node.items():
            _walk_leaf(k, v, f"{path}.{k}", p, row_athlete, keys + [k], descr)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            _walk(v, f"{path}[{i}]", p, athlete, keys)


def _walk_leaf(k, v, path, p, athlete, keys, descr):
    if isinstance(v, (dict, list)):
        _walk(v, path, p, athlete, keys)
        return
    tokens = frozenset(split_tokens(" ".join(keys)) | descr)
    if isinstance(v, bool) or v is None:
        return
    if isinstance(v, (int, float)):
        p.numbers.append(Candidate(float(v), path, tokens, athlete))
        return
    if not isinstance(v, str):
        return
    p.strings.add(v)
    if k in ("id",) and athlete is None:
        p.athlete_ids.add(v)
    m = ISO_DATE.match(v)
    if m:
        y, mo, d = int(m[1]), int(m[2]), int(m[3])
        p.dates.setdefault((y, mo, d), path)
        if m[4]:
            p.times.setdefault(f"{int(m[4])}:{m[5]}", path)
        return
    if " " in v:  # prose field: its numbers are named by the field
        _add_prose(v, path, set(tokens), p, athlete)


def _add_prose(text, path, tokens, p, athlete=None):
    tokens = frozenset(tokens | split_tokens(text))
    for fig in extract_figures(text):
        if fig.kind == "number":
            p.numbers.append(Candidate(fig.value, f"{path} (text)", tokens, athlete))
        elif fig.kind == "date" and fig.value[0] is not None:
            p.dates.setdefault(fig.value, f"{path} (text)")


def _collect_session_dates(row, athlete, p):
    if not athlete:
        return
    dates = p.athlete_dates.setdefault(athlete, set())
    if isinstance(row.get("sessionDate"), str):
        dates.add(row["sessionDate"][:10])
    for s in row.get("contributingSessions") or []:
        if isinstance(s, dict) and isinstance(s.get("sessionDate"), str):
            dates.add(s["sessionDate"][:10])


# --------------------------------------------------------------------------
# Brief side
# --------------------------------------------------------------------------

BLOCK_TAGS = {"td", "th", "tr", "div", "p", "br", "li", "h1", "h2", "h3", "h4",
              "h5", "h6", "table", "section", "blockquote", "pre"}


class _HTMLText(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.links: list[str] = []
        self.rows: list[tuple[int, int, set]] = []  # (start, end, athletes linked)
        self._open_rows: list[tuple[int, set]] = []
        self._skip = 0
        self._len = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script", "head", "title"):
            self._skip += 1
        if tag in BLOCK_TAGS:
            self._add("\n")
        if tag == "a":
            href = dict(attrs).get("href")
            if href is not None:
                self.links.append(href)
                m = re.search(r"/athlete/([^/?#]+)", href)
                if m and self._open_rows:
                    self._open_rows[-1][1].add(m[1])
        if tag == "tr":
            self._open_rows.append((self._len, set()))

    def handle_endtag(self, tag):
        if tag in ("style", "script", "head", "title"):
            self._skip = max(0, self._skip - 1)
        if tag in BLOCK_TAGS:
            self._add("\n")
        if tag == "tr" and self._open_rows:
            start, athletes = self._open_rows.pop()
            self.rows.append((start, self._len, athletes))

    def handle_data(self, data):
        if not self._skip:
            self._add(data)

    def _add(self, s):
        self.parts.append(s)
        self._len += len(s)


URL = re.compile(r"https?://[^\s)\]>\"']+|\{\{[^}]*\}\}/[^\s)\]>\"']*")
MD_LINK = re.compile(r"\]\(([^)\s]+)\)")


def read_brief(path: Path) -> tuple[str, list[str], list]:
    raw = path.read_text()
    rows: list = []
    if path.suffix.lower() in (".html", ".htm") or raw.lstrip().startswith("<"):
        parser = _HTMLText()
        parser.feed(raw)
        text = "".join(parser.parts)
        links = parser.links + URL.findall(text)
        rows = parser.rows
    else:
        text = raw
        links = MD_LINK.findall(raw) + [u for u in URL.findall(raw)
                                        if u not in MD_LINK.findall(raw)]
    text = text.replace("\xa0", " ")
    return text, links, rows


def row_athlete(offset: int, rows) -> str | None:
    """The athlete a figure belongs to: the innermost table row around it that
    links to exactly one athlete. Squad-level figures sit outside such rows."""
    best = None
    for start, end, athletes in rows:
        if start <= offset < end and len(athletes) == 1:
            if best is None or end - start < best[1] - best[0]:
                best = (start, end, next(iter(athletes)))
    return best[2] if best else None


ID_PATTERNS = [
    re.compile(r"https?://\S+"),
    re.compile(r"\{\{[^}]*\}\}"),
    re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b"),
    re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I),
    # hashed pseudonyms and hex ids: mixed letters and digits, 6+ chars
    re.compile(r"\b(?=[0-9A-Fa-f]*[A-Fa-f])(?=[0-9A-Fa-f]*\d)[0-9A-Fa-f]{6,}\b"),
    # provider session ids, alert ids: word-ish tokens joined by - or _ with digits
    re.compile(r"\b[A-Za-z]+[-_][\w-]*\d[\w-]*\b"),
]


def _mask_ids(text: str) -> str:
    for pat in ID_PATTERNS:
        text = pat.sub(lambda m: " " * len(m.group(0)), text)
    return text


DATE_ISO = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
DATE_DMY = re.compile(
    r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?"
    r"(?:,?\s+(\d{4}))?\b", re.I)
DATE_MDY = re.compile(
    r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+(\d{1,2})(?:st|nd|rd|th)?"
    r"(?:,?\s+(\d{4}))?\b", re.I)
TIME = re.compile(r"\b(\d{1,2}):(\d{2})\b")
NUMBER = re.compile(r"(?<![\w.])([+\-−]?)(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?(?!\d)(\s?%)?")


def _num(m) -> float:
    return float(m.group(2).replace(",", "") + (m.group(3) or ""))


@dataclass
class Figure:
    kind: str        # number | date | time
    text: str
    offset: int
    value: object
    decimals: int
    context: str
    concepts: set


def extract_figures(text: str) -> list[Figure]:
    figures: list[Figure] = []
    masked = _mask_ids(text)

    def blank(s, m):
        return s[:m.start()] + " " * (m.end() - m.start()) + s[m.end():]

    for pat, kind in ((DATE_ISO, "iso"), (DATE_DMY, "dmy"), (DATE_MDY, "mdy")):
        for m in list(pat.finditer(masked)):
            if kind == "iso":
                val = (int(m[1]), int(m[2]), int(m[3]))
            elif kind == "dmy":
                val = (int(m[3]) if m[3] else None, MONTHS[m[2][:3].lower()], int(m[1]))
            else:
                val = (int(m[3]) if m[3] else None, MONTHS[m[1][:3].lower()], int(m[2]))
            figures.append(Figure("date", m.group(0), m.start(), val, 0, _context(text, m), set()))
            masked = blank(masked, m)
    for m in list(TIME.finditer(masked)):
        figures.append(Figure("time", m.group(0), m.start(), f"{int(m[1])}:{m[2]}", 0,
                              _context(text, m), set()))
        masked = blank(masked, m)
    for m in NUMBER.finditer(masked):
        decimals = len(m.group(3)) - 1 if m.group(3) else 0
        ctx = _context(text, m)
        figures.append(Figure("number", m.group(0).strip(), m.start(), _num(m), decimals, ctx,
                              _concepts_near(text, m)))
    return figures


def _clause_bounds(text, m):
    seps = re.compile(r"\n|[.;!?](?:\s|$)|·|\|")
    start = 0
    for s in seps.finditer(text, 0, m.start()):
        start = s.end()
    end_m = seps.search(text, m.end())
    return start, end_m.start() if end_m else len(text)


def _context(text, m) -> str:
    start, end = _clause_bounds(text, m)
    return " ".join(text[start:end].split())


def _concepts_near(text, m) -> set:
    start, end = _clause_bounds(text, m)
    before = re.findall(r"[A-Za-z]+", text[start:m.start()])[-CONTEXT_WORDS:]
    after = re.findall(r"[A-Za-z]+", text[m.end():end])[:CONTEXT_WORDS]
    words = {w.lower() for w in before + after}
    return {name for name, (brief_words, _) in CONCEPTS.items() if words & brief_words}


# --------------------------------------------------------------------------
# Derived counts
# --------------------------------------------------------------------------


def derive(run: dict, p: Payloads, errors: list[str]) -> list[Candidate]:
    counts = run.get("derived") or {}
    window = run.get("window") or {}
    sets: dict[str, set] = {}
    for name, ids in counts.items():
        if name not in DERIVED_NAMES:
            errors.append(f"derived count '{name}' is not one the skill's rules define "
                          f"({', '.join(sorted(DERIVED_NAMES))})")
            continue
        if not isinstance(ids, list) or not all(isinstance(i, str) for i in ids):
            errors.append(f"derived count '{name}' must list athlete ids")
            continue
        sets[name] = set(ids)
        unknown = sorted(set(ids) - p.athlete_ids)
        if unknown:
            errors.append(f"derived count '{name}' names athletes absent from every "
                          f"payload: {', '.join(unknown[:5])}")
    for a, b in SUBSETS:
        if a in sets and b in sets and not sets[a] <= sets[b]:
            errors.append(f"derived '{a}' is not a subset of '{b}': "
                          f"{', '.join(sorted(sets[a] - sets[b])[:5])}")
    for a, b in DISJOINT:
        if a in sets and b in sets and sets[a] & sets[b]:
            errors.append(f"derived '{a}' and '{b}' overlap: "
                          f"{', '.join(sorted(sets[a] & sets[b])[:5])}")
    if "trained" in sets:
        lo, hi = window.get("start"), window.get("end")
        if not (lo and hi):
            errors.append("derived 'trained' needs run.window.start/end to be verified")
        else:
            for aid in sorted(sets["trained"]):
                if not any(lo <= d <= hi for d in p.athlete_dates.get(aid, ())):
                    errors.append(f"derived 'trained' lists {aid}, but no alert row for that "
                                  f"athlete has a session dated {lo}..{hi}")
    out = [Candidate(float(len(s)), f"derived:{n}", frozenset(split_tokens(n)))
           for n, s in sets.items()]
    for a, b in RATES:
        if a in sets and b in sets and sets[b]:
            out.append(Candidate(100.0 * len(sets[a]) / len(sets[b]),
                                 f"derived:{a}/{b} rate", frozenset({"rate"})))
    return out


# --------------------------------------------------------------------------
# Matching
# --------------------------------------------------------------------------


def _close(display: float, decimals: int, v: float) -> bool:
    return abs(abs(v) - abs(display)) <= 0.5 * 10 ** -decimals + 1e-9


def check_number(fig: Figure, pool: list[Candidate], athlete: str | None = None
                 ) -> tuple[bool, str]:
    hits = [c for c in pool if _close(fig.value, fig.decimals, c.value)]
    if athlete:
        scoped = [c for c in hits if c.athlete in (None, athlete)]
        if hits and not scoped:
            return False, ("this value exists only in another athlete's payload, not in "
                           "the payload of the athlete this row links to")
        hits = scoped
    if not hits:
        return False, "no payload field or defined derived count has this value"
    for concept in fig.concepts:
        need = CONCEPTS[concept][1]
        hits = [c for c in hits if c.tokens & need]
        if not hits:
            if concept == "review":
                return False, ("stated as a review/feedback figure; no MCP field carries "
                               "review or feedback counts")
            return False, (f"stated as a {concept}, but no field with this value is "
                           f"described as a {concept}")
    return True, hits[0].source


def check_date(fig: Figure, p: Payloads, run: dict) -> tuple[bool, str]:
    y, mo, d = fig.value
    allowed = dict(p.dates)
    for key in ("generatedAt", "runDate"):
        m = ISO_DATE.match(str(run.get(key) or ""))
        if m:
            allowed.setdefault((int(m[1]), int(m[2]), int(m[3])), f"run.{key}")
    for (yy, mm, dd), src in allowed.items():
        if mm == mo and dd == d and (y is None or y == yy):
            try:
                date(yy, mm, dd)
            except ValueError:
                continue
            return True, src
    return False, "no payload date (or run date) matches"


def check_time(fig: Figure, p: Payloads, run: dict) -> tuple[bool, str]:
    m = ISO_DATE.match(str(run.get("generatedAt") or ""))
    if m and m[4] and f"{int(m[4])}:{m[5]}" == fig.value:
        return True, "run.generatedAt"
    if fig.value in p.times:
        return True, p.times[fig.value]
    return False, "no payload timestamp (or run.generatedAt) has this time"


# --------------------------------------------------------------------------
# Links
# --------------------------------------------------------------------------

ATHLETE_ROUTE = re.compile(r"^/performance-manager/athlete-performance-dashboard/athlete/([^/]+)$")
SESSION_ROUTE = re.compile(r"^/performance-manager/data-health/([^/]+)$")
STATIC_ROUTES = {"/performance-manager/ai-insights/ai-alerts",
                 "/performance-manager/athlete-performance-dashboard"}


def check_link(href: str, host: str, p: Payloads) -> str | None:
    if PLACEHOLDER.search(href):
        return "unfilled template placeholder in the link"
    if not href.startswith(host + "/"):
        return f"host is not the configured platform host {host}"
    parts = urlsplit(href)
    q = {k: v[0] for k, v in parse_qs(parts.query, keep_blank_values=True).items()}
    path = parts.path.rstrip("/") or "/"
    if path in STATIC_ROUTES:
        return None if not q else "query string on a route that takes none"
    m = SESSION_ROUTE.match(path)
    if m and m[1] != "metric-watchlist":
        return None if m[1] in p.strings else f"session id {m[1]} is in no payload"
    m = ATHLETE_ROUTE.match(path)
    if m:
        athlete = m[1]
        if athlete not in p.athlete_ids:
            return f"athlete id {athlete} is in no payload"
        if set(q) == {"tab", "alert"} and q["tab"] == "alerts":
            if any(a == athlete and al == q["alert"] for a, al in p.alert_rows):
                return None
            return f"no alert row pairs athlete {athlete} with alert {q['alert']}"
        if q == {"tab": "alerts"} or not q:
            return None
        return "athlete route with query parameters outside the link contract"
    return "route is not in references/link-targets.md"


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------


def run_check(brief: Path, payload_paths: list[Path], run: dict, host: str) -> dict:
    p = load_payloads(payload_paths)
    errors: list[str] = []
    pool = p.numbers + derive(run, p, errors)
    text, links, rows = read_brief(brief)
    unmatched, matched = [], 0
    for m in PLACEHOLDER.finditer(text):
        lo = text.rfind("\n", 0, m.start()) + 1
        hi = text.find("\n", m.end())
        unmatched.append({"figure": m.group(0), "context": text[lo:hi].strip(),
                          "reason": "unfilled template placeholder in the text"})
    figures = extract_figures(text)
    for fig in figures:
        if fig.kind == "number":
            ok, why = check_number(fig, pool, row_athlete(fig.offset, rows))
        elif fig.kind == "date":
            ok, why = check_date(fig, p, run)
        else:
            ok, why = check_time(fig, p, run)
        if ok:
            matched += 1
        else:
            unmatched.append({"figure": fig.text, "context": fig.context, "reason": why})
    bad_links = []
    for href in dict.fromkeys(links):
        why = check_link(href, host, p)
        if why:
            bad_links.append({"href": href, "reason": why})
    passed = not unmatched and not bad_links and not errors
    return {"pass": passed, "figures": len(figures), "matched": matched,
            "unmatched": unmatched, "links": len(dict.fromkeys(links)),
            "badLinks": bad_links, "derivedErrors": errors}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--brief", required=True, type=Path)
    ap.add_argument("--payloads", required=True, nargs="+", type=Path,
                    help="saved MCP tool results: files or directories of *.json")
    ap.add_argument("--run", type=Path, help="run.json: window, generatedAt, derived counts")
    ap.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        host = json.loads(a.config.read_text())["appHost"].rstrip("/")
        run = json.loads(a.run.read_text()) if a.run else {}
        result = run_check(a.brief, a.payloads, run, host)
    except (OSError, ValueError, KeyError) as e:
        print(f"FIDELITY: ERROR — {e}", file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"FIDELITY: {'PASS' if result['pass'] else 'FAIL'}")
        print(f"  figures {result['figures']}, matched {result['matched']}, "
              f"unmatched {len(result['unmatched'])}; links {result['links']}, "
              f"bad {len(result['badLinks'])}")
        for u in result["unmatched"]:
            print(f"  UNMATCHED  {u['figure']!r} in \"{u['context']}\" — {u['reason']}")
        for b in result["badLinks"]:
            print(f"  BAD LINK   {b['href']} — {b['reason']}")
        for e in result["derivedErrors"]:
            print(f"  DERIVED    {e}")
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
