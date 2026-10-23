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

The failure to prevent is a complete, correct, unreadable brief — every figure
twice, behind repeated disclaimers. Completeness lives behind links.

Before drafting anything, load `../_shared/brief-generation-rules.md`. Those twelve
rules are the acceptance criteria, and rules 1, 3, 4, 9, 10, 11 and 12 block a
send. Rule 12 is the floor under all of them: **render only MCP fields; a
missing field leaves the element out, never filled in.**

## Inputs

Session date (default today), window (7 days back), cards (default 5; 4–6
acceptable, never pad), recipients (from the routine).

## Steps

### 1. Sweep the squad — check which sweep you have first

Read `references/squad-sweep.md` first. `get_squad_alerts` is the one-call
sweep but **is not on every deployment** — verify with `help` rather than
assuming. Without it the sweep is a parallel fan-out over `list_athletes` +
`get_athlete_alerts`; the reference carries the call budget, the per-athlete
cap, and the `aggregationType` attribution rules.

Either way, call `list_athletes` for the roster total, positions and groups.

**Save every tool result verbatim** (this step's and step 4's) per
`references/fidelity-check.md` — the send gate checks the brief against them.

### 2. Establish the denominators before anything else

Most likely step to be skipped; rule 1 blocks the send without it. From the
alert rows' `sessionDate`, partition the roster:

- **trained** — has at least one in-window session
- **no session in window** — has alerts, none in window
- **unclassified** — returned no alerts at all; session presence unconfirmed

The headline rate is `past threshold ÷ trained`, never `÷ roster`. Above ~90%,
the finding is that the threshold barely discriminated on a loading week —
lead with that; it is the most useful thing in the brief.

### 3. Rank, and be explicit that it is a ranking

**Collapse same-fact rows first (rule 7).** The feed returns one observation as
several rules — collapse on `(athleteId, triggerSessionId, observedValueUnit ??
unit, observedValue)` before counting anything. Ranking on raw row counts ranks
athletes by rule overlap, not by risk.

Then: recency gate → distinct alert families → severity, **excluding
still-building** → magnitude of the dominant *above-baseline* excursion →
session date.

Two guards (`references/squad-sweep.md`): rank only *above-baseline*
excursions — an underload is not a loading risk — and apply rule 2's three
baseline screens first. On a live sweep, all top five raw excursions were
deceleration artefacts.

State how many were flagged and how many are shown, and link the rest.

### 4. Fill the evidence for shortlisted athletes only

For each carded athlete — **all of them, symmetrically** (rule: parallel
cards):

- `get_athlete_load_trend` — the weekly series and its `dataSufficient` flag
- `get_athlete_session_metrics` — the individual session rows for the strip
- `get_acr` — the ratio, band and data-sufficiency flag

Give every card the same fields. Where one athlete's field is missing, the
card says so in words — no figure (rule 12) — rather than silently omitting
what a sibling card carries.

### 5. Identify which signal moved

One phrase per card: `braking, not volume` / `volume step-change` / `rate of
change` / `speed exposure`. Attribution, **not** a routing decision: never pair
it with an intervention or say what it means for today's session (rule 9).

Where session content confounds two signals (scrummaging inflates a front-row
forward's volume and braking alike), say they are one signal and name the
confound — a caveat on the reading, which is allowed.

### 6. Draft against the template

Use `assets/brief-template.md` verbatim — fixed order, and the per-field rules
for what a `Not real if →` and a `Worth opening →` may say.

Build every `[...]` marker from `references/link-targets.md`: `appHost` from
`assets/brief-config.json` plus the athlete's Alerts-tab route with that row's
`alertId`, which opens the exact alert. Never write a host or a host
placeholder into a template. When an id is missing, that file's table says
which weaker link to take — and every downgrade is disclosed in the brief.

### 7. Gate through the critic (mandatory)

Hand the draft to the `brief-critic` subagent. It returns a per-rule verdict.

- Fix every violation and re-submit **once**.
- If a **blocking** rule (1, 3, 4, 9, 10, 11, 12) still fails, do not send.
  Report the violation and stop.
- Non-blocking violations that survive two passes are listed in the run log
  and the brief goes out — do not loop.

### 8. Fidelity check (mandatory)

Render the final brief, write `run.json`, and run
`scripts/check_fidelity.py` per `references/fidelity-check.md`. Any unmatched
figure or bad link: remove the element (rule 12), re-render, re-run — never
edit a payload or add a derived count to make it pass. Still failing after one
fix, or exit 2: do not send; report the unmatched lines and stop.

### 9. Send, and log

Send only when the critic verdict is `send` **and** the fidelity check passes.
Send to the configured recipients. Emit a one-line run log: window, roster
total, trained, flagged, carded, critic verdicts, fidelity result, and anything
the sweep could not classify.

## Guardrails

- **Never invent an athlete name.** Hashed pseudonyms (`Athlete 1A2B3C4D`) mean
  egress PII redaction is on for that org. Report the pseudonym as given;
  redaction is not a defect to work around.
- **Never fill a gap.** A missing field leaves its element out (rule 12); a
  null unit or an unresolvable link is stated as a gap. No review or "learning
  loop" figures — no MCP tool returns them. Shortening a brief must never delete
  a disclosure while keeping the behaviour it disclosed.
- **Never suggest, recommend or prescribe** — not even softened ("consider",
  "pending sign-off"). If a line could change what an athlete does today, cut
  it (rule 9).
- **Never imply a clearance**, for a carded athlete or an uncarded one.
- **Never let length be the fix.** If the brief is too long, move provenance
  behind links. Reasoning, falsifiers and caveats are the product.
- **Leave a place for a human to record that they looked** — the `Seen by`
  line is the only workflow element the brief carries.

## Output shape

A sent email plus a run log line. The what-moved list fits one phone screen;
one signal and one figure per athlete; the denominator in the first three
lines; every falsifier; the verbatim boundary and the data cutoff. Lengths per
`references/rendering.md`: **~190 words daily, ~600 review** — two briefs, not
one at two lengths.
