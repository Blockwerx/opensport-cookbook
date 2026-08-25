# Running it without installing anything

The [pre-session brief](../plugins/opensport-briefs/skills/pre-session-brief/SKILL.md)
is a Claude Code plugin, and installing it is the supported path — see
[first-run.md](first-run.md).

This page is for the other case: you want the brief in a plain chat window,
Claude.ai or ChatGPT, with no install. Paste the prompt below into a new
conversation. You will need the **OpenSport connector enabled in that
conversation**, or the assistant has no data to read.

## What you give up, and why it matters

The installed version hands each draft to a separate reviewer — the
`brief-critic` subagent — which checks it against eleven rules and **refuses**
the ones that fail. Neither Claude.ai nor ChatGPT has subagents, so the prompt
below asks the same assistant that wrote the draft to check its own work.

That is weaker, and not by a little. A writer reviewing their own draft
rationalises; an independent reviewer starting from the rules does not. The six
blocking rules are reproduced in full below so the check has something concrete
to fail against, but the check is **requested rather than enforced**.

Concretely: do not wire this version to send anything unattended. Read what it
produces before it goes anywhere near a coach.

---

## The prompt

```
You are producing a pre-session training-load brief for performance staff from
OpenSport data, read through the OpenSport connector.

If the OpenSport connector is not available in this conversation, stop and tell
me — do not answer from general knowledge or invent figures.

RUN PARAMETERS
Squad: senior squad
Window: 7 days back from today
Cards: the 5 athletes whose data moved most

WHAT TO DO

1. Sweep the squad's training-load alerts for the window. Prefer a squad-level
   sweep tool if the deployment has one; otherwise list the athletes and fetch
   each athlete's alerts.

2. Establish the denominators before anything else. Derive who trained from
   in-window sessionDate on the alert rows. Athletes returning no alerts at all
   cannot be classified either way — count them separately and say so.

3. Screen every baseline before you rank anything against it. A very large
   percentage off a small absolute difference is the signature of a measurement
   artefact, not a finding. Apply all three screens and report how many athletes
   each one removed:
   - Physical plausibility: a deceleration baseline below 1.0 m/s2 is not a
     plausible senior-athlete baseline. Exclude on level alone.
   - Out of family: exclude a baseline below half the squad median for the same
     alert type in this same run. Compute the median from this run.
   - Instability: if an athlete's in-window alerts of the same type disagree on
     baseline by more than 1.5x (max / min), the baseline is untrusted whatever
     its level.

4. Collapse duplicates before counting or ranking. The feed raises several rules
   against one figure, so one observation arrives as several rows. Collapse on
   (athleteId, triggerSessionId, observedValueUnit or unit, observedValue), keep
   the highest-severity row, and keep the other rule names as a list. Never
   count raw rows as findings.

5. Rank by the size of the excursion, and say on the page that this is ranked by
   excursion size, not by concern.

6. Draft the brief. Around 600 words. One card per athlete: the observation, the
   one signal that moved, the provenance of the figure, and a "Not real if"
   line naming what would make the observation wrong.

THE SIX RULES THAT BLOCK A SEND

R1. Every rate states its denominator. Never publish a count against the roster
total when a smaller population is the true denominator. "50 of 82 past
threshold" is wrong when 31 of the 82 did not train; "50 of the 51 who trained"
is right. A rate above about 90% is a finding about the threshold, not about the
athletes — say which it is.

R3. An untrusted baseline yields no percentage. When an alert carries
baselineStatus (building, zero_baseline, data_incomplete) the server has already
nulled the baseline deliberately. Do not compute a ratio, a percentage or a
multiplier from it, and do not reconstruct one from an earlier call. State the
observation in natural units and quote baselineStateReason.

R4. Value type is read, never inferred. percentageOfBaseline and
percentageAboveBaseline differ by exactly 100. Say "228% of baseline" or "145%
above baseline" according to the field, never convert between the phrasings, and
recompute from observed / baseline rather than trusting the phrasing you were
handed.

R9. No suggestion, no recommendation. Report what the data did; never say what
to do about it. No load instructions, no status labels (MODIFY, MONITOR,
Modified, Full), no framing that assumes an intervention, and no softened forms
— "suggested", "consider", "you may want to", "pending sign-off" are the same
act with a disclaimer attached. The test for every line: could this change what
an athlete does today? If yes, cut it. Naming which signal moved ("braking, not
volume"), what would invalidate the observation, and what evidence to look at
next are all permitted — they describe the data rather than prescribing a
response.

R10. Figures are a snapshot — stamp them. The engine re-evaluates historical
alerts and baselines move, so the same session can read 145% above baseline one
morning and 128% two days later. Quote each alert's own evaluation stamp as well
as its session date, never present a percentage as a stable property of a
session, and never restate a figure from an older brief. Sort and window on
sessionDate, never on timestamp.

R11. Carry this boundary statement verbatim, at any length:

  Training-load pattern only. No recommendation is made or implied. Not a
  medical, injury-risk or return-to-play judgement. Absence of a card is not
  clearance.

All four clauses. "Pending sign-off" does not substitute and must not appear.
Alongside it, state the data cutoff.

BEFORE YOU SHOW ME ANYTHING

Re-read your own draft against R1, R3, R4, R9, R10 and R11 one at a time, and
report a pass or fail for each with the line you are judging. If any fails, fix
it and say what you changed. If you cannot fix it, show me the draft with the
failure named rather than quietly softening it.

Then show me the brief here. Do not email, post or send it anywhere.
```

---

## After the first run

Three things to check yourself, because they are the failures that look like
successes:

- **The headline count** reads *N of the M who trained*, not *N of the roster*.
- **The boundary statement** is there, all four clauses.
- **The percentages carry a stamp**, and no percentage sits on a baseline the
  brief said it could not trust.

If you find yourself checking these every morning, that is the argument for
installing the plugin version instead — the critic checks them for you, and
refuses the brief rather than reporting the problem underneath it.
