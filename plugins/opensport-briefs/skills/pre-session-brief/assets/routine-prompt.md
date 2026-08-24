# Routine prompt

The prompt the scheduled cloud routine runs. Deliberately thin: it names the
skill and the run parameters, and gets out of the way. Everything that governs
the output lives in the skill and its rules file, so the brief can be changed
by editing those rather than by re-tuning a prompt in a scheduling UI.

Paste the block below as the routine's prompt.

---

```
Run the pre-session-brief skill for today's session.

Squad: senior squad
Window: 7 days back from today
Cards: 5

Report observations only — no suggestions, no recommendations, no status
labels.

Send to the configured recipients when the brief-critic gate passes. If a
blocking rule fails after one revision pass, do not send — reply to me with the
failing rule and the offending lines instead.
```

---

## Why it is this short

The first version of this brief was tuned by writing more prompt. That is what
produced a 1,650-word email: each instruction added a thing to state, nothing
removed a thing, and the accumulated result was a document that stated every
figure twice in four unit systems. A thin prompt plus a versioned rules file
inverts that — the rules can say *don't*, and the critic enforces it.

## Schedule

Before the first session of the day, early enough that the data cutoff is the
previous day's last session and late enough that overnight ingestion has
settled. Check what the brief's own `data to …` line reports on the first few
runs; if the cutoff is consistently mid-previous-day, the routine is firing
ahead of ingestion, not the brief mis-stating it.

Fixture days and rest days are not the same as training days. A brief on a day
with no session behind it has nothing to report — if that case matters, add
it to the skill as an early exit rather than trying to encode it here.

## Changing the output

| Want to change | Edit |
|---|---|
| What the email looks like | `assets/brief-template.md` |
| What is or isn't allowed | `../_shared/brief-generation-rules.md` |
| Which tools are called, in what order | `SKILL.md` steps |
| How strictly it's enforced | `agents/brief-critic.md` |
| Recipients, cadence, squad | this prompt |

Do not add output instructions to this prompt. If the brief is wrong, one of
the four files above is wrong, and fixing it there fixes every future run.

## First-run checklist

Watch for these on the first two or three runs, because they are the failures
that look like successes:

- **Denominator.** The headline should read `N of the M who trained`, not
  `N of <roster>`. If it reports the roster total, step 2 was skipped.
- **Per-card baseline provenance.** Every card should carry its own basis —
  `Baseline 28-day declared`, or `Baseline basis not declared for this rule`
  where the alert declares none. Days-on-record is not a baseline window; a
  card quoting one, or a single global claim about baselines, means rule 2
  was violated and the critic missed it.
- **The boundary statement.** All four clauses, including "No recommendation
  is made or implied" and "Absence of a card is not clearance."
- **Link targets.** Built per `references/link-targets.md` — the athlete
  profile's Alerts tab, not the ai-alerts list. If alert deep-links resolve to the alerts index rather than
  the specific alert, the brief must say so. Silent fallback is the defect —
  not the fallback itself.
- **Length.** ~600 words. If it comes back at 1,200+, the tiering collapsed:
  provenance is in the email instead of behind links.
