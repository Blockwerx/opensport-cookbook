"""Tests for check_fidelity.py. Run from the skill directory:

    python3 -m unittest discover -s scripts/tests

All fixtures are synthetic: invented athletes, ids and figures.
"""
import json
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


class Rounding(unittest.TestCase):
    def test_display_rounding_is_honoured(self):
        # observedValue 6.56 shows as 6.6 at one decimal, and as 7 at none.
        self.assertTrue(check_html("<p>reading 6.6 today</p>")["pass"])
        self.assertTrue(check_html("<p>reading 7 today</p>")["pass"])
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
