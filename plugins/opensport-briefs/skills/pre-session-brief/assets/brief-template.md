# Brief template

Fixed structure for the pre-session brief email. Order is not negotiable:
what moved, then framing, then evidence, then residuals, then the boundary.

**This brief reports observations only.** It carries no instruction, no status
label and no suggested change — see rule 9, which blocks a send. The reader
decides what to do; the brief's job is to put the right five athletes and the
right five figures in front of them before they decide.

`{{...}}` are substitutions. `[...]` are links into the platform — see
`../references/link-targets.md` for what each one resolves to. The alert link is the
alert's own route with its session date pinned, which is what makes it expand
rather than merely highlight; that file says why. Figures follow
rule 6 display precision — whole numbers for load and counts, one decimal for
magnitudes and multipliers.

---

```
SUBJECT   {{n}} athletes moved most this week · sharpest: {{pos_a}}, {{pos_b}}
PREVIEW   {{n}} of {{trained}} who trained are past threshold. {{one_line_limit}}
```

Subject names what the brief contains, not a verdict count. No "modify 4,
monitor 1" — that is a decision the brief does not make.

---

```
{{date}} · pre-session · {{squad}} · data to {{cutoff}}

WHAT MOVED THIS WEEK
  ▲ {{id}}  {{position}}   {{driver}} — {{headline_figure}}
  ▲ {{id}}  {{position}}   {{driver}} — {{headline_figure}}
    {{id}}  {{position}}   {{driver}} — {{headline_figure}}
    {{id}}  {{position}}   {{driver}} — {{headline_figure}}
    {{id}}  {{position}}   {{driver}} — {{headline_figure}}

  ▲ = largest two excursions.  Ranked by excursion size, not by concern.
```

`driver` is which signal moved, as attribution: `braking, not volume` /
`volume step-change` / `rate of change` / `speed exposure`. It reads the
figures. It does not imply a response to them.

`headline_figure` is the single most decisive number, in the form
`observed vs baseline, +N%`. One figure per athlete on this list.

There is no action column, and no line describing what this does to the
session. If a reader wants to change something, that is theirs to decide from
the evidence below.

---

```
READ THE {{flagged}} THE RIGHT WAY
{{flagged}} of the {{trained}} athletes who trained this week are past
threshold — not {{flagged}} of {{roster}}. {{discrimination_note}}
                                                          [all {{flagged}} →]
{{artefact_note}}

{{limitation_line}}
```

`discrimination_note` — when the rate is high, say what it means: in a loading
week the threshold separated almost nobody, so this is a fact about the week's
programming rather than N athletes independently at risk.

`artefact_note` — if any athlete was excluded from the ranking under rule 2's
three screens, say how many, **which screen removed them** (implausible level,
out of family, or unstable baseline), and say plainly that excluded is not
cleared. Reporting the screen matters: an unstable baseline is a different
statement about the data than a low one.

`limitation_line` — the systemic caveat, two lines maximum, positioned *after*
the list and framed as a boundary. Per-alert windows, not a global claim
(rule 2).

---

```
THE EVIDENCE — LARGEST TWO

▲ {{id}} · {{position}} · {{driver}}
  {{evidence_line_1}}
  {{evidence_line_2}}
  Not real if → {{falsifier}}
  Worth opening → {{what_to_inspect}}
  {{baseline_provenance}}                    [evidence →] [{{extra_link}} →]
```

Then, in the same shape and with the same fields:

```
THE EVIDENCE — THE OTHERS

{{id}} · {{position}} · {{driver}}
  {{evidence_line_1}}
  {{evidence_line_2}}
  Not real if → {{falsifier}}
  Worth opening → {{what_to_inspect}}
  {{baseline_provenance}}                                  [evidence →]
```

Card rules:

- Two evidence lines. The first is the decisive figure. The second is the
  qualifier or the counter-observation — including one that weakens the case
  ("volume is the weak part of this"), which builds trust rather than costing
  it.
- `falsifier` is one sentence naming a **data condition** that would make the
  observation wrong — a contact block inflating GPS load, a thin baseline, a
  deliberately light prior period. It must not name an action.
- `what_to_inspect` names evidence, never a training change: the session
  breakdown, the deceleration distribution, the wellness screen, the sprint
  distribution across sessions. Pointing at data is not prescribing.
- `baseline_provenance` is that card's own declared window and sufficiency —
  `Baseline 28-day declared` or `Baseline basis not declared for this rule`.
  Per card, never global.
- Every card has every field. A field with no data reads
  `Load history unavailable for this athlete`, never nothing.

---

```
ALSO
{{residual_cohorts}}

{{drift_note}}

Training-load pattern only. No recommendation is made or implied. Not a
medical, injury-risk or return-to-play judgement. Absence of a card is not
clearance.

Seen by ______________  at ________

Generated unattended by OpenSport, {{gen_time}}, from data to {{cutoff}}.
Unreviewed by any clinician. Full figures and provenance in the platform.
```

`residual_cohorts` covers athletes outside the window and those returning no
alerts. For an athlete with no load data the wording is: **no load data means
no assessment, not a negative one** — never an aphorism, and never something a
skimming reader could take as either safe or alarming.

`drift_note` states that computed percentages are a snapshot and may read
differently later, because the engine re-evaluates historical alerts (rule 10).

The boundary statement is verbatim per rule 11, all four clauses, at any
length. **No "pending sign-off" line** — there is no recommendation awaiting
approval. The `Seen by` line stays: a retained, timestamped, automated document
should record that a human read it.
