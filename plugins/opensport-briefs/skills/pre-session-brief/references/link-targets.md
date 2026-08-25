# Link targets

The brief's `[...]` markers are the only route from the email back into the
platform. This file is the contract for what they resolve to.

Base URL is the customer's OpenSport host — `https://app.opensport.io` in
production. Every path below is relative to it.

## The alert link — use the athlete profile, not the alerts list

```
/performance-manager/ai-insights/ai-alerts/{alertId}?dateFrom={sessionDate}&dateTo={sessionDate}
```

`alertId` and `sessionDate` both come straight off the alert. **Every link
carries its own row's date** — one brief routinely spans several sessions, so a
single shared date breaks the majority while the first link you test still
opens.

## Why the date is on the link, and not a detail

The obvious objection to this route is real, and it is what an earlier version
of this file ruled it out on: the alerts page resolves an id only against alerts
it has **already loaded** — there is no by-id lookup behind it — and it bounds
its own fetch by **session date**, while an alert feed is ordered by the
generation stamp. Two axes that disagree.

They disagree only if the window is *shared*. It is not: `?dateFrom`/`?dateTo`
are read by `useAlertDateRange` and fed into the **server query**, so pinning
both to that row's own `sessionDate` asks for one day rather than asking one
window to hold a heterogeneous feed. The axis mismatch dissolves per link.

It also clears the harder limit, which is the cap rather than the axis. The list
is capped — a real deployment reported *500 of 3,306 alerts* — so an unpinned
deep link to anything outside the first page fails with *"this alert hasn't
loaded yet."* One day's worth is comfortably inside it.

And it fixes a second symptom that looks unrelated: a row that expands and then
vanishes while you are reading it. With one day of data, paging settles at once,
so nothing re-renders the expansion away.

## What the athlete profile does instead

`/performance-manager/athlete-performance-dashboard/athlete/{athleteId}?tab=alerts&alert={alertId}`
**only scrolls to the row and highlights it.** Nothing expands. The reader
arrives at a highlighted row they still have to click, which is most of the
distance the link was supposed to close. Use it only as the fallback below.

## The other markers

| Marker | Target |
|---|---|
| `[evidence →]` | the athlete's alert, per the pattern above |
| `[all N →]` | `/performance-manager/ai-insights/ai-alerts` — the alerts index |
| `[roster →]` | `/performance-manager/athlete-performance-dashboard` |
| `[<date> session →]` | `/performance-manager/data-health/{sessionExternalId}` — the session id `get_athlete_alerts` and `get_athlete_session_metrics` return verbatim (e.g. `catapult-0d34719d-…`) |

## Two limits to state, not assume

**`alertId` is not on every deployment.** It is being added to the alert
payload; a server without it returns alerts with no id. Never build a link from
an empty value — and note there are **three** states here, not two, because you
almost always still hold the `athleteId` the tool was called with:

| You have | Link | Say in the brief |
|---|---|---|
| `athleteId` + `alertId` | the full pattern above | nothing — it does what it says |
| `athleteId` only | the same path **without** `?alert=` — the athlete's Alerts tab | that the link opens the athlete's alerts, not the individual one |
| neither | `/performance-manager/ai-insights/ai-alerts` | that the link is to the list |

The middle row is the common one on an older deployment, and it is worth taking
over the index: it is already scoped to the right athlete, so the reader lands
among a handful of rows rather than the whole squad's.

**Whichever row you are on, disclose the downgrade.** Shipping a link that
silently resolves to less than the reader expects is the disclosure-drop these
guardrails exist to prevent, and it is easy to do by accident — a partial link
still looks like a link. Written after doing exactly that: a brief generated
half an hour before the id reached the environment carried athlete-scoped links
and said nothing about it.

**The athlete profile sits behind the `athletes` view.** An organisation
without that view is redirected to the alerts index rather than shown the
profile, so the link is only as good as that entitlement. Worth confirming once
per customer rather than per brief.

## Where this is going

A forthcoming server change returns `alertUrl` as a field on the alert. Once
that lands, the brief
reads a URL rather than composing one from a route described in prose, and this
file becomes a note about what the field means instead of a construction
recipe. Prefer `alertUrl` over this pattern the moment it is available.
