# Link targets

The brief's `[...]` markers are the only route from the email back into the
platform. This file is the contract for what they resolve to, and
`scripts/check_fidelity.py` enforces it before every send.

## The host is configuration, not text

Every link is `{appHost}{route}`, where `appHost` is the single value in
[`../assets/brief-config.json`](../assets/brief-config.json) —
`https://app.opensport.io`, the production platform, by default. Point it at
another host only for a test deployment, and change it there, nowhere else.

The templates never carry a host. They carry finished links
(`{{alert_link}}`, `{{alerts_index}}`, …) that you compose from `appHost` and a
route below. A host placeholder left in a template — `{{app_base}}` and the like
— reaches the reader as a link that goes nowhere, and nothing about the email
looks wrong until someone clicks. The fidelity check fails any link that
carries an unfilled placeholder or a host other than `appHost`.

## The alert link — the athlete's Alerts tab, opened on the alert

```
/performance-manager/athlete-performance-dashboard/athlete/{athleteId}?tab=alerts&alert={alertId}
```

Both ids come straight from the MCP: `alertId` from the alert row, and
`athleteId` from that same row (on the squad sweep) or from the argument the
per-athlete call was made with. The query parameter is `alert`, not `alertId`.
Never pair one row's `alertId` with another row's athlete — the check fails a
link whose athlete and alert are not one row.

**Why this route.** It opens the exact alert, expanded, and it does not depend
on a date:

- The athlete's Alerts tab fetches that athlete's alerts **filtered on the
  server and across their whole history**, so the alert is in what the page
  loads however old its session is.
- An alert named by `?alert=` **opens expanded** in place, with the same detail
  the alerts list expands into — not merely highlighted.
- A merged weekly alert, which carries no single `sessionDate`, links exactly
  like any other: no date is needed.

It is also the route the MCP tools' own descriptions name for `alertId`.

**Why not the alerts list's own deep link**
(`/performance-manager/ai-insights/ai-alerts/{alertId}`). That page has no
by-id lookup: it can open an alert only if the alert is already in the window
of alerts it loaded — a bounded date window, under a row cap. An alert outside
it shows *"this alert hasn't loaded yet"* or *"older than the loaded window"*
instead of the alert. An earlier version of this file chose that route with the
session date pinned on the link; the athlete route needs no such workaround, so
it replaces it.

## Signed out, and after sign-in

The platform's sign-in keeps the full path **and query** of the page that asked
for it and returns there once the reader has signed in. A reader who opens the
email signed out therefore lands on the same alert, opened, after signing in —
not on the platform's home page. Two exceptions, both outside the brief's
control:

- A user who has not finished onboarding is sent to onboarding first.
- **The athlete profile sits behind the organisation's `athletes` view.** An
  organisation without that view is redirected to the alerts index rather than
  shown the profile. Confirm the view once per customer rather than per brief.

## The other markers

| Marker | Route |
|---|---|
| `[evidence →]` / `open →` | the alert link above |
| `[all N past threshold →]` | `/performance-manager/ai-insights/ai-alerts` — the alerts index |
| `[roster →]` | `/performance-manager/athlete-performance-dashboard` |
| `[<date> session →]` | `/performance-manager/data-health/{sessionExternalId}` — the session id the alert and session-metrics tools return verbatim (e.g. `catapult-0d34719d-…`) |

Nothing else. A link to any other route fails the check.

## When an id is missing

Never build a link from an empty value, and never fill one in. Three states,
keyed on what the payload actually carries:

| You have | Link | Say in the brief |
|---|---|---|
| `athleteId` + `alertId` from one row | the alert link above | nothing — it does what it says |
| `athleteId` only | `/performance-manager/athlete-performance-dashboard/athlete/{athleteId}?tab=alerts` | that the link opens the athlete's alerts, not the individual one |
| neither | `/performance-manager/ai-insights/ai-alerts` | that the link is to the list |

**Disclose every downgrade.** A link that silently resolves to less than the
reader expects is the disclosure-drop these guardrails exist to prevent, and it
is easy to do by accident — a partial link still looks like a link.

## Where this is going

If the alert payload gains a ready-made URL field, prefer it over composing one
— provided its host is `appHost` and its route is the one above, which the check
still verifies.
