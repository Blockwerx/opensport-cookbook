# Sweeping the squad

How to get one window's alerts for a whole roster. Read this before step 1 —
which path you take changes the cost of the run by two orders of magnitude.

## Check which sweep you have

`get_squad_alerts` is the one-call squad sweep. **It is not on every
deployment.** Verify before planning around it: call `help`, or check the
registered tool list. Do not assume it exists — a deployment without it exposes
six tools (`help`, `list_athletes`, `get_athlete_alerts`, `get_acr`,
`get_athlete_load_trend`, `get_athlete_session_metrics`) and no squad sweep.

The tool is being added to the server. Until your deployment exposes it,
Path B below is the only sweep available.

## Path A — `get_squad_alerts` available

Call it with `startDate` and `endDate`, paging `cursor` until exhausted. The
headline states the true total across the window, how many athletes are
affected, what was collapsed, and whether the page was truncated. Do not reason
from a truncated first page without saying so in the brief.

Useful filters: `severity` (`red` / `amber` / `yellow` / `info`), `category`
(`injury_risk` / `performance` / `workload`), `primaryPosition`,
`primaryGroup`. Note that position and group filter the returned **page**, not
the underlying query — the headline explains the difference.

## Path B — fan out

`list_athletes` with `limit: 200` (one page covers a roster of about 80
athletes, and the headline states the true total), then `get_athlete_alerts`
once per athlete. On an 80-athlete squad that is roughly 80 calls, and it is
the dominant cost of the whole run.

**Do not run this serially in one agent.** Measured on a Premiership-sized
roster, a serial sweep ran past 120 calls and did not finish inside a single
session's credential lifetime. That measurement is why the one-call squad
sweep exists.

Slice it instead: partition the roster by `primaryPosition` and run the slices
in parallel, each returning a compact per-athlete summary rather than raw
payloads. Six slices of 13–14 athletes completes. Keep the returns small — the
raw feed for one heavily-alerted athlete is thousands of tokens, and the sweep
only needs, per athlete: latest `sessionDate`, whether any session falls in
window, the distinct in-window alert families, a de-duplicated severity count,
which alerts carry `baselineStatus`, and the two or three largest excursions.

Four things that bite:

**Same-fact duplication.** Several rules fire on one figure, so one observation
arrives as several rows — collapse on `(athleteId, triggerSessionId,
observedValueUnit ?? unit, observedValue)` before counting or ranking. See
rule 7. `get_squad_alerts` does this for you; the fan-out does not.

**The 50-alert cap.** `get_athlete_alerts` caps `limit` at 50, and a single
athlete can hold far more — 119 observed on one athlete over a season. Fifty
rows covered roughly the last 8 days for that athlete, so a 7-day window fits,
with little margin. The response says `Showing 50 of N … (truncated)`. If the
oldest row returned still falls inside your window, you did not see the whole
window: say so rather than reporting a count.

**Weekly conditions are collapsed.** A condition the engine raised against
several sessions of one week comes back **once**, with `contributingSessionIds`
listing the sessions it drew on. Count it once, not once per session.

**No `severityBand` on this path.** You get raw `severity`
(`low`/`moderate`/`high`/`critical`) with no reconciliation against the
`red`/`amber`/`yellow`/`info` filter vocabulary, and nothing marks a
still-building baseline as unrankable. Apply it yourself: any alert carrying
`baselineStatus` is `info`-equivalent regardless of severity.

**`aggregationType` decides attribution.** Before attributing any figure to a
session, read it:

| `aggregationType` | Means |
|---|---|
| `single_session` | one session's figure — `sourceSessionId` when it differs from `triggerSessionId` |
| `daily_total` | that day's sessions summed (`contributingSessionIds`) — **not** one session |
| `weekly` | the week's total over `windowStartDate`–`windowEndDate` |

Never say a session produced a daily or weekly aggregate.

## Partitioning the roster (step 2's input)

From the alert rows' `sessionDate`, split the roster three ways:

- **trained** — at least one in-window session
- **no session in window** — has alerts, none in window
- **unclassified** — returned no alerts at all, so session presence is
  unconfirmed either way

Only the first is a valid denominator for a "past threshold" rate. The third is
not zero and not safe — it is unknown, and the brief says so.

On path B this partition is a by-product of the fan-out you already paid for.
On path A the headline gives affected-athlete counts, but session presence for
the *unalerted* remainder still needs `get_athlete_session_metrics` if you want
to claim it — otherwise report those athletes as unclassified.

## Ranking the swept set

Two failures found on a live sweep of about 80 athletes, both of which put
fake cards at
the top of the brief.

**Direction.** `percentageAboveBaseline` is signed. `Load_Underload` and a
below-average week return large negatives — real observations, but not loading
risk, and not what a pre-session brief is deciding. Rank on above-baseline
excursions only. On the live sweep, 8 of 52 in-window athletes had their
largest excursion *below* baseline; ranked on absolute magnitude they compete
with genuine overload cases.

**Near-zero baselines.** `High_Deceleration_Count` returned baselines of 0.67,
0.68, 0.78, 0.89 and 1.01 against a squad norm near 2–3, yielding +800%, +500%,
+500%, +424% and +254%. **None carried `baselineStatus`.** Ranked raw, those
five occupied the entire top five and displaced every real finding. Screen them
with the plausibility floor in rule 2 and raise them as a data-quality
question.

For reference, the same sweep after screening: the top card was a +178%
deceleration excursion on a 1.97 baseline, and the five athletes a human had
independently picked the previous week ranked #2, #3, #5, #7 and #10 of 43 —
so the ranking is defensible once the artefacts are gone, and not before.
