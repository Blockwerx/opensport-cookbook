# Brief generation rules

Eleven rules governing any athlete-facing or staff-facing brief this plugin
generates from OpenSport MCP tool output. Each is phrased so a reviewer — human
or the `brief-critic` subagent — can say "this draft violates rule 4" and point
at a line.

Rules 1, 3, 4, 9, 10 and 11 are **blocking**: a draft that violates one is not
sent.

---

## 1. Every rate states its denominator (BLOCKING)

A count-over-population figure is never published against the roster total when
a smaller population is the true denominator.

- Wrong: `50 of 82 past threshold` — 31 of those 82 did not train.
- Right: `50 of the 51 athletes who trained are past threshold`.

Derive `trained` from in-window `sessionDate` on the alert rows. State the
residual explicitly: athletes that returned no alerts at all cannot be
classified either way, so say so — `6 athletes returned no alerts; session
presence unconfirmed`.

A rate above ~90% is a finding about the threshold, not about the athletes.
Say which it is.

## 2. Never assert a baseline window the alert does not declare

Windows come from a **static per-alert-type spec table** in the server's alert
value contract, not from the data. Two consequences, both easy to get wrong:

**Most alert types declare no baseline window at all.** Only a handful carry
`baselineWindowDays` (`Weekly_Max_vs_28Day_Max`, `Daily_Load_vs_28Day_Max`,
`Weekly_Load_vs_28Day_Average`, `Four_Week_Load_Change`). Many declare only
`observationWindowDays`; some declare neither. `High_Sprint_Frequency_7D` — the
sprint-count alert — declares a 7-day *observation* window and **no baseline
window whatsoever**.

So: quote the window next to the figure when the alert declares one. When it
does not, say the basis is undeclared. Never generalise one alert's window
across the brief, and never invent a window for an alert that has none.

- Wrong: a preamble claiming all figures rest on "28-day baselines" — for
  sprint counts that window is not merely unquoted, it does not exist.
- Right: the declared window beside the figure that declares it; "baseline
  basis not declared for this alert type" beside the ones that don't.

**A declared window is intent, not evidence.** `baselineWindowDays: 28` is the
rule's designed window, hardcoded. It is not a claim that 28 days of data
exist. Data sufficiency is a separate signal — `dataSufficient`,
`baselineStatus`, `baselineStateReason`. A brief may not read a declared window
as proof of history, and may not read thin history as invalidating a declared
window. They are different facts; state whichever you actually have.

**Sanity-check the baseline you were given — `baselineStatus` does not catch
everything.** Not every rule participates in the baseline-building guard, so a
thin baseline can arrive with no flag on it at all and be treated as trusted.

Measured on a Premiership-sized roster of about 80 athletes,
`High_Deceleration_Count` returned baselines of **0.67, 0.68, 0.78, 0.89 and
1.01** — against a squad norm of roughly 2–3 — producing excursions of
**+800%, +500%, +500%, +424% and +254%**. None of those
alerts carried `baselineStatus`. Nothing in the payload marked them as
unusable, and they were the four largest excursions in the entire squad.

So apply a plausibility floor before publishing or ranking any ratio:

- Compare the baseline against the same metric's baseline for other athletes.
  An order-of-magnitude outlier is an artefact, not a finding.
- Treat a sub-unit deceleration baseline, or any baseline that would need the
  athlete to have almost no history, as untrusted **whatever the payload says**.
- A very large percentage off a small absolute difference is the signature.
  `4.67 vs 0.78` is +500% and about 4 m/s² — the ratio is dramatic, the
  quantity is not.

Report these as a data-quality question, not as an athlete's risk. And prefer
the absolute figure to the ratio whenever the baseline is doubtful.

## 3. An untrusted baseline yields no percentage (BLOCKING)

When an alert carries `baselineStatus` (`building`, `zero_baseline`,
`data_incomplete`), the server has already nulled `baselineValue` and degraded
`valueType` to `unknown`. That is deliberate — the rule re-emitted `value` in
natural units and set a placeholder baseline.

So: do not compute a ratio, a percentage or a multiplier from it. Do not
reconstruct one from a prior call. State the natural-unit observation and the
reason the baseline is unusable, quoting `baselineStateReason`.

Never let a `building`-state alert sit in a list of quantified findings as
though it were one. `info` severity means "no trustworthy comparison yet,
whatever the raw severity" — it is not a mild risk.

## 4. Value type is read, never inferred (BLOCKING)

`valueType` distinguishes `percentageOfBaseline` from
`percentageAboveBaseline`. These differ by exactly 100 and have been misread
before (for example: `Weekly_Accel_Decel_Load value:169.7` is *% of* baseline;
reading it as *% above* overstates by 100).

- `percentageOfBaseline` → "228% **of** baseline"
- `percentageAboveBaseline` → "145% **above** baseline"

Never convert between the two phrasings. Never describe a `magnitude` value as
a percentage; magnitudes are unsigned by contract.

This blocks a send because the failure is silent: a figure phrased the wrong
way is wrong by exactly 100, and nothing in the sentence looks odd. It is
checkable without the payload — the brief prints `observed vs baseline`, so
`observed ÷ baseline` gives "% of" and `(observed ÷ baseline) − 1` gives
"% above". Recompute rather than trusting the phrasing.

## 5. Unverified units are stated without a unit

If `unitVerified` is `false` or `unit` is `null`, publish the figure bare. Do
not borrow a unit from a different payload that happens to name one — a null
unit can never be verified.

## 6. Display precision, not payload precision

Tool payloads round to two decimals. That is a serialization floor, not a
display policy. For a reader:

| Quantity | Display |
|---|---|
| Load (AU), distance | whole number |
| Counts (sprints, sessions) | whole number, and **baselines too** |
| Magnitude (m/s²) | one decimal |
| Multiplier, ratio | one decimal |
| Percentage | whole number |

`336 sprints vs 164.33` is a violation: nobody runs a third of a sprint.

Counts are identifiable without judgement — the spec sets `countBased: true`
(e.g. `High_Sprint_Frequency_7D`) and `observedValueUnit: "count"`. When either
is present, the observed value **and its baseline** render as integers.

## 7. One quantity, one form — and collapse the input first

**The alert feed already contains the same fact several times.** The engine
raises multiple rules against one figure, so `get_athlete_alerts` returns one
observation as several rows. Measured on a live squad: one athlete's Friday
session
returns `Load_Overload`, `Daily_Load_vs_28Day_Max`, `Season_Max_Achieved` and
`Weekly_Max_vs_28Day_Max` **all reporting the same load**. One fact, four rows.

So before counting or ranking anything, collapse on
`(athleteId, triggerSessionId, observedValueUnit ?? unit, observedValue)`.
Keep the highest-severity row and retain the other rule names as a list — which
conditions fired is information, but they are not four findings.

Two consequences:

- **Never count raw alert rows as findings.** "Six high-severity alerts" may be
  two facts. A severity tally taken before the collapse is inflated, and
  ranking athletes by it ranks them by how many rules happen to overlap.
- `get_squad_alerts` performs this collapse for you and exposes the rule list
  as `alertTypes`. On the fan-out path you must do it yourself.

Then, in the brief itself: a given quantity appears once, in exactly one form.
Absolute, versus-baseline, as-a-percentage, as-a-weekly-total, as-a-multiple
and as a sparkline point are six renderings of one number — pick the one that
carries the observation and drop the rest to the linked detail view.

Corollary: no figure appears in both a sentence and a table.

## 8. No hedge verbs

No "looks like", "reads as", "on my reading", "appears to". Uncertainty lives
in one named field — `Not real if →` — or in a stated confidence line. Never in
a verb, and never as a per-card disclaimer repeated on every card: repetition
converts a disclaimer into wallpaper and reads as defensiveness.

State the driver flat: `braking, not volume`.

## 9. No suggestion, no recommendation (BLOCKING)

**The brief reports what the data did. It never says what to do about it.**
There is no recommendation feature in the product, and a generated load
instruction is not one this system is entitled to give — a coach who wants an
LLM's opinion on an athlete's session can ask for it themselves and own that
choice. A brief that arrives unasked, unattended and prescriptive takes that
decision away from them.

Forbidden, whatever the hedging around it:

- Imperative load instructions — "cap high-speed volume", "reduce total
  volume", "hold at or below 453 AU", "no maximal sprint work", "drop the
  highest-intensity block", "flatten the ramp".
- Status labels that encode a decision — `MODIFY`, `MONITOR`, `Modified`,
  `Full`, "modify 4, monitor 1", availability or selection verdicts.
- Framing that assumes an intervention — "what this does to today", "your
  high-volume block loses three forwards", "re-check Monday", anything that
  tells the reader which session block to change.
- Softened forms. "Suggested", "draft recommendation", "consider", "you may
  want to", "pending sign-off" are the same act with a disclaimer attached.
  A prescription labelled draft is still a prescription.

Permitted, because they describe the data rather than the athlete's session:

- **Which signal moved**, as attribution: `braking, not volume`,
  `volume step-change`, `rate of change`. This reads the figures, it does not
  prescribe a response to them.
- **What would invalidate the observation** — the `Not real if →` field. It
  qualifies the reading, and does not become a recommendation as long as it
  names a data condition rather than an action.
- **What the reader might look at next** to check the observation: the session
  breakdown, the wellness screen, the deceleration distribution. Naming the
  evidence is not prescribing a training change.

The test: could this line change what an athlete does today? If yes, it does
not belong in the brief. Surface the observation and stop.

## 10. Figures are a snapshot — stamp them (BLOCKING)

**The engine re-evaluates historical alerts, and baselines move.** This is
observed, not theoretical, and it is a known upstream behaviour: the nightly
run re-stamps `timestamp` — the *evaluation* stamp — so an alert can carry
today's stamp for a session dated months ago. `sessionDate` is the axis a coach
means by "recent"; `timestamp` is not. Never window or sort on `timestamp`.

For one athlete's 21 Aug session, the deceleration
alert read `6.56 vs 2.67` (145.4% above) when a brief was generated on 22 Aug,
and `6.56 vs 2.87` (128.4% above) when the same alert was re-read on 24 Aug —
same session, same observed value, a baseline that had risen. The baseline
climbs monotonically through the series as history accumulates
(1.87 → 2.02 → 2.18 → 2.34 → 2.54 → 2.87). Day-counts drift the same way: an
athlete quoted at "26 of 28 days on record" read 25 two days later.

Consequences a brief must respect:

- Quote each alert's own `timestamp` / `evaluationDate` basis, not just the
  session date. A reader who opens the platform later will see different
  percentages for the same session and must be able to tell why.
- Never present a percentage as a stable property of a session. Absolute
  observations (session load, sprint count) are stable; anything computed
  against a baseline is not.
- Never restate a figure from an older brief. Re-read it.

The stamp is blocking because an unstamped percentage is a number the platform
will contradict, in front of the person you sent it to.

## 11. The boundary statement, verbatim (BLOCKING)

Every generated brief carries this, unabridged, regardless of length:

> Training-load pattern only. No recommendation is made or implied. Not a
> medical, injury-risk or return-to-play judgement. Absence of a card is not
> clearance.

The second and fourth clauses are not optional. A brief that flags N athletes
and details a
subset has, in writing, declined to detail the remainder — "not carded" must
never be readable as "cleared".

A workflow caveat ("pending sign-off") does **not** substitute, and must not
appear at all: it says who signs the document rather than what kind of
statement it is, and it implies there is a recommendation awaiting approval.
There isn't one — see rule 9.

Alongside it, state that generation was unattended and unreviewed, and give
the data cutoff.

---

## Tiering (not a rule — the structure the rules assume)

- **Email** carries the observation and one reason per athlete.
- **Platform links** carry provenance, paired baselines, weekly totals,
  sparklines, methodology, and every flagged athlete not shown.
- Every reasoning block (`Not real if →`) is retained somewhere. The reasoning
  is the differentiator; it is the *placement* that is wrong when a brief reads
  as too long.
