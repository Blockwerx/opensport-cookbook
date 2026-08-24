# Link targets

The brief's `[...]` markers are the only route from the email back into the
platform. This file is the contract for what they resolve to.

Base URL is the customer's OpenSport host — `https://app.opensport.io` in
production. Every path below is relative to it.

## The alert link — use the athlete profile, not the alerts list

```
/performance-manager/athlete-performance-dashboard/athlete/{athleteId}?tab=alerts&alert={alertId}
```

Both ids come straight from `get_athlete_alerts`: `athleteId` is what the tool
was called with, `alertId` is on the alert. **The query parameter is `alert`,
not `alertId`.**

**Do not link `/performance-manager/ai-insights/ai-alerts/{alertId}`.** It looks
like the more direct target and it is the wrong one for this brief. That page
resolves an id only against alerts it has already loaded — there is no by-id
lookup behind it — and it bounds its own fetch by **session date**. This feed is
ordered by the alert's generation stamp. The two axes disagree exactly where it
matters: an alert this brief calls recent, raised against a session weeks
older, is inside the generation window and outside the session-date one, so the
link expands nothing and lands the reader on a list.

The athlete profile bounds by the generation stamp instead, which is the same
axis the brief ranks on. It also navigates by `athleteId`, so the *navigation*
half of the link is correct even for a merged weekly alert, where the surviving
record's `alertId` is one of several.

## The other markers

| Marker | Target |
|---|---|
| `[evidence →]` | the athlete's alert, per the pattern above |
| `[all N →]` | `/performance-manager/ai-insights/ai-alerts` — the alerts index |
| `[roster →]` | `/performance-manager/athlete-performance-dashboard` |
| `[<date> session →]` | `/performance-manager/data-health/{sessionExternalId}` — the session id `get_athlete_alerts` and `get_athlete_session_metrics` return verbatim (e.g. `catapult-0d34719d-…`) |

## Two limits to state, not assume

**`alertId` is not on every deployment.** It reaches the alert payload in
OS-3406; a server without it returns alerts with no id. When it is absent, fall
back to `[all N →]` (the alerts index, which needs no id) and say in the brief
that the link is to the list rather than the alert. Never build a link from an
empty value.

**The athlete profile sits behind the `athletes` view.** An organisation
without that view is redirected to the alerts index rather than shown the
profile, so the link is only as good as that entitlement. Worth confirming once
per customer rather than per brief.

## Where this is going

OS-3416 returns `alertUrl` as a field on the alert. Once that lands, the brief
reads a URL rather than composing one from a route described in prose, and this
file becomes a note about what the field means instead of a construction
recipe. Prefer `alertUrl` over this pattern the moment it is available.
