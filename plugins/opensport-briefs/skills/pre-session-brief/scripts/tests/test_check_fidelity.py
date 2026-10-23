"""Tests for check_fidelity.py. Run from the skill directory:

    python3 -m unittest discover -s scripts/tests

All fixtures are synthetic: invented athletes, ids and figures.
"""
import html
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import check_fidelity as cf  # noqa: E402

FIX = HERE / "fixtures"
PAYLOADS = [FIX / "payloads"]
RUN = json.loads((FIX / "run.json").read_text())
HOST = "https://app.opensport.io"
PROFILE = f"{HOST}/performance-manager/athlete-performance-dashboard/athlete"
A1 = "0a1b2c3d-0000-4000-8000-000000000001"
A2 = "0a1b2c3d-0000-4000-8000-000000000002"


def check(name, run=RUN):
    return cf.run_check(FIX / name, PAYLOADS, run, HOST)


def check_html(body, run=RUN):
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(body)
    try:
        return cf.run_check(Path(f.name), PAYLOADS, run, HOST)
    finally:
        Path(f.name).unlink()


def unmatched(result):
    return {u["figure"]: u["reason"] for u in result["unmatched"]}


class PassingBrief(unittest.TestCase):
    def test_every_figure_and_link_traces(self):
        r = check("brief-pass.html")
        self.assertTrue(r["pass"], r)
        self.assertGreater(r["figures"], 20)
        self.assertEqual(r["links"], 4)

    def test_cli_exit_codes(self):
        args = ["--payloads", str(FIX / "payloads"), "--run", str(FIX / "run.json")]
        self.assertEqual(cf.main(["--brief", str(FIX / "brief-pass.html"), *args]), 0)
        self.assertEqual(cf.main(["--brief", str(FIX / "brief-fail-median.html"), *args]), 1)
        self.assertEqual(cf.main(["--brief", str(FIX / "nope.html"), *args]), 2)


class TicketExamples(unittest.TestCase):
    def test_median_shown_as_maximum_fails(self):
        u = unmatched(check("brief-fail-median.html"))
        self.assertIn("3,900", u)
        self.assertIn("max", u["3,900"])

    def test_figure_absent_from_payload_fails(self):
        u = unmatched(check("brief-fail-median.html"))
        self.assertIn("87", u)

    def test_window_borrowed_from_another_athlete_fails(self):
        # 28 is a real baselineWindowDays -- on a different athlete's alert.
        u = unmatched(check("brief-fail-median.html"))
        self.assertIn("another athlete", u["28"])

    def test_invented_learning_loop_line_fails(self):
        u = unmatched(check("brief-fail-learning-loop.html"))
        self.assertEqual(set(u), {"3", "5", "60%"})
        self.assertIn("review", u["3"])

    def test_placeholder_and_wrong_host_links_fail(self):
        bad = {b["reason"] for b in check("brief-fail-links.html")["badLinks"]}
        self.assertEqual(len(bad), 2)
        self.assertTrue(any("placeholder" in b for b in bad))
        self.assertTrue(any("configured platform host" in b for b in bad))


class LabelMatching(unittest.TestCase):
    SQUAD = PAYLOADS + [FIX / "payloads-squad"]

    def test_invented_small_count_fails(self):
        # get_squad_alerts carries a squad-wide 2 (amber/yellow counts), so
        # value-only matching would accept both invented lines. "2 players
        # trained twice" is named, and 2 is neither the roster nor trained;
        # "2 stayed on for extras" is named by nothing, so it cannot be traced.
        p = cf.load_payloads(self.SQUAD)
        self.assertTrue(any(c.value == 2 and c.athlete is None for c in p.numbers))
        r = cf.run_check(FIX / "brief-fail-invented-count.html", self.SQUAD, RUN, HOST)
        got = {u["context"]: u["reason"] for u in r["unmatched"]}
        self.assertEqual(set(got), {"2 players trained twice this week",
                                    "2 stayed on for extras"})
        self.assertIn("labelled as roster / trained in assets/figure-labels.json",
                      got["2 players trained twice this week"])
        self.assertIn("no label from assets/figure-labels.json", got["2 stayed on for extras"])

    def test_unlabelled_small_count_fails(self):
        reason = unmatched(check_html("<p>3 today</p>"))["3"]
        self.assertIn("no label from assets/figure-labels.json", reason)

    def test_count_must_match_its_own_derived_field(self):
        # 3 is flagged and carded, but not red (1)
        self.assertFalse(check_html("<p>3 carry a red</p>")["pass"])
        self.assertTrue(check_html("<p>1 carries a red</p>")["pass"])
        reason = unmatched(check_html("<p>3 carry a red</p>"))["3"]
        self.assertIn("red in assets/figure-labels.json", reason)

    def test_wrapped_html_paragraph_keeps_its_labels(self):
        # A source newline inside <p> is whitespace, not a clause break.
        self.assertTrue(check_html("<p>3 of the 4 athletes who trained are past\n"
                                   "threshold</p>")["pass"])


SKILL = HERE.parent.parent
TEMPLATES = ["assets/brief-template.md", "assets/slack-template.md", "assets/email-daily.html"]
SLOT = re.compile(r"\{\{(\w+)\}\}")
A4 = "0a1b2c3d-0000-4000-8000-000000000004"

# Every count slot, with the run.json count it renders and the label kinds
# (figure-labels.json "counts") that may name it. {{n}} is the carded count in
# the subject line and the flagged count in the preview.
COUNT_SLOTS = {
    "n": ({"carded", "flagged"}, 3), "n_cards": ({"carded"}, 3),
    "flagged": ({"flagged"}, 3), "trained": ({"trained"}, 4),
    "roster": ({"roster"}, 6), "n_red": ({"red"}, 1), "n_alerted": ({"alerted"}, 5),
}
# Computed sentences that carry counts, in the wording the templates describe.
NOTE_SLOTS = {
    "denominator_note": "3 of the 4 athletes who trained are past threshold (75%), not 3 of 6.",
    "artefact_note": "1 athlete excluded by the unstable-baseline screen; excluded is not "
                     "cleared.",
    "screened_note": "1 athlete screened out for an unstable baseline",
    "coverage_note": "1 athlete had alerts but no session in the window; 1 returned no "
                     "alerts, so session presence is unconfirmed.",
    "residual_cohorts": "1 athlete had alerts but no session in the window. 1 returned no "
                        "alerts: no load data means no assessment, not a negative one.",
}
# Everything else renders without a count.
TEXT_SLOTS = {
    "date": "23 Oct 2026", "cutoff": "21 Oct 2026", "gen_time": "23 Oct 2026 06:40",
    "squad": "senior squad", "pos_a": "Back", "pos_b": "Forward", "pos": "Back",
    "position": "Back", "id": "Athlete 1A2B3C4D", "code": "1A2B3C4D", "marker": "",
    "driver": "braking, not volume", "why": "braking, not volume",
    "headline_figure": "braking well above baseline", "observed": "high",
    "baseline": "usual", "unit": "", "one_line_limit": "Per-alert windows.",
    "discrimination_note": "In a loading week the threshold separates few athletes.",
    "limitation_line": "Per-alert windows, not a global claim.",
    "rule_concentration_note": "Most cards come from one rule family.",
    "drift_note": "Percentages are a snapshot and may read differently later.",
    "evidence_line_1": "Braking well above baseline.", "evidence_line_2": "Volume is flat.",
    "falsifier": "A contact block inflating load.", "what_to_inspect": "the session breakdown",
    "baseline_provenance": "Baseline basis not declared for this rule",
    "extra_link": "session", "detail": "Braking well above baseline.",
    "pointer": "the session breakdown",
    "alert_link": f"{PROFILE}/{A1}?tab=alerts&alert=alert_7f3e9c21_sess0101",
    "screened_link": f"{PROFILE}/{A4}?tab=alerts",
    "alerts_index": f"{HOST}/performance-manager/ai-insights/ai-alerts",
}


def _md_to_html(md):
    """The template's fenced blocks as a rendered message: one paragraph per
    line, a lowercase-led line continuing the one above (a wrapped sentence)."""
    paras = []
    for block in re.findall(r"^```\n(.*?)^```", md, re.S | re.M):
        for line in block.splitlines():
            line = line.strip()
            if not line:
                continue
            if paras and line[0].islower():
                paras[-1] += " " + line
            else:
                paras.append(line)
    out = []
    for para in paras:
        para = re.sub(r"\*\*|`", "", para)
        para = re.sub(r"\[([^\]]*)\]\(([^)]*)\)", "\x01\\2\x02\\1\x03", para)
        para = re.sub(r"\[([^\]]*)\]", r"\1", para)
        para = html.escape(para, quote=False)
        para = re.sub("\x01(.*?)\x02(.*?)\x03", r'<a href="\1">\2</a>', para)
        out.append(f"<p>{para}</p>")
    return "\n".join(out)


def _template_html(rel):
    raw = (SKILL / rel).read_text()
    if rel.endswith(".md"):
        return _md_to_html(raw)
    return re.sub(r"<!--.*?-->", "", raw, flags=re.S)


class TemplateSlots(unittest.TestCase):
    """Wording drift in a template must fail here, not in a live brief: every
    count slot, rendered, carries a label from assets/figure-labels.json for
    the count it stands for, and the rendered template passes the check."""

    RUN = {**RUN, "derived": {**RUN["derived"], "screened": [A4]}}

    def test_every_slot_is_classified(self):
        known = set(COUNT_SLOTS) | set(NOTE_SLOTS) | set(TEXT_SLOTS)
        for rel in TEMPLATES:
            with self.subTest(template=rel):
                self.assertLessEqual(set(SLOT.findall(_template_html(rel))), known)

    def test_count_slots_are_labelled_and_pass(self):
        def value(name):
            if name in COUNT_SLOTS:
                return str(COUNT_SLOTS[name][1])
            return NOTE_SLOTS.get(name, TEXT_SLOTS.get(name, ""))

        for rel in TEMPLATES:
            with self.subTest(template=rel):
                doc = _template_html(rel)
                # Where each count slot lands in the extracted text: render with
                # letter-only sentinels, extract, then swap the values in.
                order = [m[1] for m in SLOT.finditer(doc) if m[1] in COUNT_SLOTS]
                it = iter(range(len(order)))
                sentinel = SLOT.sub(
                    lambda m: (f"QQ{chr(65 + next(it))}QQ" if m[1] in COUNT_SLOTS
                               else html.escape(value(m[1]))), doc)
                parser = cf._HTMLText()
                parser.feed(sentinel)
                text, slots = "".join(parser.parts).replace("\xa0", " "), []
                for i, name in enumerate(order):
                    mark = f"QQ{chr(65 + i)}QQ"
                    at = text.index(mark)
                    text = text[:at] + value(name) + text[at + len(mark):]
                    slots.append((at, name))
                self.assertTrue(slots, "template has no count slot")
                figures = {f.offset: f for f in cf.extract_figures(text)}
                for at, name in slots:
                    fig = figures[at]
                    kinds, _ = COUNT_SLOTS[name]
                    self.assertTrue(fig.counts & kinds,
                                    f"{{{{{name}}}}} in \"{fig.context}\" carries "
                                    f"{sorted(fig.counts) or 'no'} count label, "
                                    f"expected one of {sorted(kinds)}")

                rendered = SLOT.sub(lambda m: html.escape(value(m[1])), doc)
                with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
                    f.write(rendered)
                try:
                    r = cf.run_check(Path(f.name), PAYLOADS, self.RUN, HOST)
                finally:
                    Path(f.name).unlink()
                self.assertTrue(r["pass"], (r["unmatched"], r["badLinks"],
                                            r["derivedErrors"]))


class Rounding(unittest.TestCase):
    def test_display_rounding_is_honoured(self):
        # observedValue 6.56 shows as 6.6 at one decimal, and as 7 at none.
        self.assertTrue(check_html("<p>reading 6.6 today</p>")["pass"])
        # A whole number below 10 needs a label; inside the athlete's row it
        # defaults to that athlete's alert measurements.
        self.assertTrue(check_html(f'<table><tr><td>reading 7 today</td><td>'
                                   f'<a href="{PROFILE}/{A1}">x</a></td></tr></table>')["pass"])
        self.assertFalse(check_html("<p>reading 6.5 today</p>")["pass"])

    def test_derived_rate_rounds_to_whole_percent(self):
        # flagged 3 / trained 4
        self.assertTrue(check_html("<p>75% of those who trained</p>")["pass"])
        self.assertFalse(check_html("<p>76% of those who trained</p>")["pass"])


class Links(unittest.TestCase):
    def test_alert_link_must_pair_athlete_and_alert(self):
        good = f'<a href="{PROFILE}/{A1}?tab=alerts&alert=alert_7f3e9c21_sess0101">x</a>'
        swapped = f'<a href="{PROFILE}/{A2}?tab=alerts&alert=alert_7f3e9c21_sess0101">x</a>'
        self.assertTrue(check_html(good)["pass"])
        r = check_html(swapped)
        self.assertIn("no alert row pairs", r["badLinks"][0]["reason"])

    def test_route_outside_contract_fails(self):
        r = check_html(f'<a href="{HOST}/performance-manager/ai-insights/ai-alerts/'
                       f'alert_7f3e9c21_sess0101">x</a>')
        self.assertIn("link-targets", r["badLinks"][0]["reason"])

    def test_athlete_alerts_tab_fallback_is_allowed(self):
        self.assertTrue(check_html(f'<a href="{PROFILE}/{A1}?tab=alerts">x</a>')["pass"])


class Derived(unittest.TestCase):
    def test_undeclared_count_name_fails(self):
        run = json.loads(json.dumps(RUN))
        run["derived"]["reviewed"] = [A1]
        r = check("brief-pass.html", run)
        self.assertFalse(r["pass"])
        self.assertTrue(any("reviewed" in e for e in r["derivedErrors"]))

    def test_trained_needs_an_in_window_session(self):
        run = json.loads(json.dumps(RUN))
        run["derived"]["trained"].append("0a1b2c3d-0000-4000-8000-000000000004")
        r = check("brief-pass.html", run)
        self.assertTrue(any("no alert row" in e for e in r["derivedErrors"]))

    def test_without_derived_counts_the_funnel_does_not_trace(self):
        u = unmatched(check("brief-pass.html", {k: v for k, v in RUN.items()
                                                 if k != "derived"}))
        self.assertIn("75%", u)


class Extraction(unittest.TestCase):
    def test_pseudonyms_ids_and_unit_superscripts_are_not_figures(self):
        figs = cf.extract_figures("Athlete 1A2B3C4D 6.6 m/s² catapult-0d34719d-x1")
        self.assertEqual([f.text for f in figs], ["6.6"])

    def test_dates_and_times(self):
        figs = cf.extract_figures("sessions to 21 Oct 2026, generated 06:40")
        self.assertEqual([f.kind for f in figs], ["date", "time"])


if __name__ == "__main__":
    unittest.main()
