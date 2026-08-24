---
name: pre-session-brief
description: >
  Generate the OpenSport pre-session brief — a short, tiered staff email that
  surfaces the handful of athletes whose training-load data moved most this
  week, with every figure's provenance and limits stated correctly. Reports
  observations only: it makes no suggestion and no recommendation.
  Reads the squad through the OpenSport MCP server, ranks the sharpest cases,
  drafts against a fixed template, then gates the draft through the
  `brief-critic` subagent before anything is sent.

  Use when asked to: "run the pre-session brief", "generate today's brief",
  "pre-session brief for <date>", "squad brief before the session", "draft the
  loading brief", "run the brief routine". Also invoked by the scheduled cloud
  routine that emails the brief before the first session of the day.

  Do not use when the ask is to read or triage alerts interactively ("what's
  Athlete X's ACWR", "show me today's alerts") — call the MCP tools directly
  for that. This skill exists to produce the *email*, and its value is the
  tiering and the guardrails, not the data access.
---

# Pre-session brief

Produce one email: **the five-ish athletes whose load data moved most this
week**, with the evidence available but not in the way.

The brief reports and stops: no instruction, no availability verdict, no
suggested change — rule 9 blocks a send on any of those. Staff decide; the
brief puts the right athletes and figures in front of them first.

The failure mode this skill exists to prevent is not missing data — it is a
complete, correct, unreadable brief. A draft that states every figure twice, in
four unit systems, behind five repetitions of an AI disclaimer, is a draft
nobody reads. Completeness lives behind links.

Before drafting anything, load `../_shared/brief-generation-rules.md`. Those eleven
rules are the acceptance criteria, and rules 1, 3, 4, 9, 10 and 11 block a
send.

## Inputs

Session date (default today), data window (7 days back), cards to show
(default 5; 4–6 acceptable, never pad to a number), recipients (from the
routine).

## Steps

### 1. Sweep the squad — check which sweep you have first

Read `references/squad-sweep.md` first. `get_squad_alerts` is the one-call
sweep but **is not on every deployment** — verify with `help` rather than
assuming. Without it the sweep is a parallel fan-out over `list_athletes` +
`get_athlete_alerts`; the reference carries the call budget, the per-athlete
cap, and the `aggregationType` attribution rules.

Either way, call `list_athletes` for the roster total, positions and groups.

### 2. Establish the denominators before anything else

Most likely step to be skipped; rule 1 blocks the send without it. From the
alert rows' `sessionDate`, partition the roster:

- **trained** — has at least one in-window session
- **no session in window** — has alerts, none in window
- **unclassified** — returned no alerts at all; session presence unconfirmed

The headline rate is `past threshold ÷ trained`, never `÷ roster`. If that rate
is above ~90%, the finding is that the threshold barely discriminated on a
loading week — lead with that, because it is a statement about the session
plan, and it is the most useful thing in the brief.

### 3. Rank, and be explicit that it is a ranking

**Collapse same-fact rows first (rule 7).** The feed returns one observation as
several rules — collapse on `(athleteId, triggerSessionId, observedValueUnit ??
unit, observedValue)` before counting anything. Ranking on raw row counts ranks
athletes by rule overlap, not by risk.

Then: recency gate → distinct alert families → severity, **excluding
still-building** → magnitude of the dominant *above-baseline* excursion →
session date.

Two guards on that magnitude step, both in `references/squad-sweep.md`: rank
only *above-baseline* excursions (the field is signed — an underload is not a
loading risk), and apply rule 2's three baseline screens before ranking. On a
live sweep, five of the top five raw excursions were deceleration artefacts.

State how many were flagged and how many are shown. Five cards out of fifty
flagged is a tenth of the sweep; say so and link the rest.

### 4. Fill the evidence for shortlisted athletes only

For each carded athlete — **all of them, symmetrically** (rule: parallel
cards):

- `get_athlete_load_trend` — the weekly series and its `dataSufficient` flag
- `get_athlete_session_metrics` — the individual session rows for the strip
- `get_acr` — the ratio, band and data-sufficiency flag

Give every card the same fields. If one athlete's load history is unavailable,
the card says so; it does not silently omit the field while a sibling card
carries it.

### 5. Identify which signal moved

One phrase per card: `braking, not volume` / `volume step-change` / `rate of
change` / `speed exposure`. This is attribution — it names the signal the
figures point at. It is **not** a routing decision: never pair it with an
intervention or say what it means for today's session (rule 9).

Where two signals are confounded by session content — a front-row forward's
volume and braking, both inflated by scrummaging — say they are one signal and
name the confound. That is a caveat on the reading, which is allowed.

### 6. Draft against the template

Use `assets/brief-template.md` verbatim. Order is fixed: what moved, framing,
evidence, residuals, boundary. The template carries the per-field rules,
including what a `Not real if →` and a `Worth opening →` may and may not say.

Build every `[...]` marker from `references/link-targets.md`. The alert link is
the athlete profile's Alerts tab, **not** the ai-alerts page — that one windows
on session date while this feed orders by generation stamp, so the alerts this
brief surfaces are exactly the ones it cannot expand. Where `alertId` is
absent, fall back to the index **and say the link is to the list**; an
undisclosed downgrade is the disclosure-drop these guardrails exist to prevent.

### 7. Gate through the critic (mandatory)

Hand the draft to the `brief-critic` subagent. It returns a per-rule verdict.

- Fix every violation and re-submit **once**.
- If a **blocking** rule (1, 3, 4, 9, 10, 11) still fails, do not send. Report the
  violation and stop.
- Non-blocking violations that survive two passes are listed in the run log
  and the brief goes out — do not loop.

### 8. Send, and log

Send to the configured recipients. Emit a one-line run log: window, roster
total, trained, flagged, carded, critic verdicts, and anything the sweep could
not classify.

## Guardrails

- **Never invent an athlete name.** Hashed pseudonyms (`Athlete 1A2B3C4D`) mean
  egress PII redaction is on for that org. Report the pseudonym as given;
  redaction is not a defect to work around.
- **Never fill a gap by inference.** A missing baseline, a null unit, an
  unresolvable link: state the gap. Shortening a brief must never delete a
  disclosure while keeping the behaviour it disclosed.
- **Never suggest, recommend or prescribe.** No load instruction, no status
  label, no "consider", no "pending sign-off". Rule 9 is blocking and a
  softened prescription still violates it. If a line could change what an
  athlete does today, cut it.
- **Never imply a clearance**, for a carded athlete or an uncarded one.
- **Never let length be the fix.** If the brief is too long, move provenance
  behind links. Reasoning, falsifiers and caveats are the product.
- **Leave a place for a human to record that they looked** — the `Seen by`
  line is the only workflow element the brief carries.

## Output shape

A sent email plus a one-line run log. The email fits its what-moved list on one
phone screen without scrolling; names which signal moved per athlete with one
figure for it; states the correct denominator in the first three lines; carries
every falsifier, one sentence each; and ends with the verbatim boundary
statement and the data cutoff. Target ~600 words — treat 900 as a defect to
investigate, not a budget.
