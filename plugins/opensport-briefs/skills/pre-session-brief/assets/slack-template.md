# Slack template

The same facts as the email, at the same density as the matching brief. Slack is
not a paste target for the email body — the table is what makes it scannable,
and plain text is not.

`{{...}}` are substitutions. Probed rendering support, not assumed: tables,
inline `code`, `---`, bold, italic, emoji and code blocks all render;
**blockquotes do not**.

## Which markdown this is

**Standard markdown** — `**bold**`, `_italic_`, `[text](url)` — because that is
what the Slack MCP takes, and the MCP is how a scheduled brief posts. State the
flavour rather than inferring it: Slack's own `chat.postMessage` mrkdwn is a
*different* language that reads `*bold*` and `<url|text>`, and the two sets are
mutually exclusive. Mixed, whichever half is wrong renders as literal text in
the middle of the brief — visible to the reader, invisible to the author who
probed the other half.

If a deployment posts through `chat.postMessage` instead, convert the whole
template, not the markers that happen to look broken.

**One trap that survives either flavour:** never end a line with a bare URL when
the next line starts with an emoji. Slack auto-links across the newline and the
line breaks are destroyed. Every link below is wrapped, which is also why.

---

## Daily

```
🏉 **{{n_cards}} to look at before today** · {{date}} · {{squad}}

`{{n_red}}` of `{{n_alerted}}` athletes with alerts this week carry a red. {{denominator_note}}

| | **Athlete** | **Pos** | **Why** | |
|---|---|---|---|---|
| {{marker}} | `{{code}}` | {{pos}} | {{why}} · `{{observed}}` vs `{{baseline}}`{{unit}} | [open]({{alert_link}}) |

🔴 = largest two. Ranked by excursion size, not by concern.
🔵 {{rule_concentration_note}}
⚠️ {{screened_note}} — _screened is not cleared_. [see it]({{screened_link}})
⬜ {{coverage_note}}

_Training-load pattern only. No recommendation is made or implied. Not a medical, injury-risk or return-to-play judgement. Absence of a card is not clearance._
_Sent automatically · sessions to {{date}} · [all alerts]({{alerts_index}})_
```

One table row per carded athlete. Every figure in backticks — the monospace chip
is what separates the number from the prose, and without it the row reads as a
sentence with digits in it.

The boundary statement is written out rather than substituted. R11 is blocking
and the critic greps the artefact for the four clauses verbatim; behind a
`{{boundary_statement}}` there is nothing for it to find, and the clause that
goes missing in a length trim is the last one. It is the same reason the email
template carries it in full.

## Review

Same header and same table, then one block per athlete:

```
**`{{code}}` — {{why}}**
{{detail}}
**Not real if →** {{falsifier}}
**Worth opening →** {{pointer}}
[open the alert →]({{alert_link}})
```

Then the residuals under `**What the screens removed**`, then the boundary
statement in full — all four clauses, on the review as on the daily.

`Not real if →` names a data condition and never an action; `Worth opening →`
names evidence and never a training change. Rule 9 blocks a send either way.

## The band markers

The leading emoji is the only thing carrying severity-of-attention, so it has to
be consistent between the two channels and across runs:

| | |
|---|---|
| 🔴 | one of the two largest excursions |
| 🔵 | context that changes how a figure should be read |
| ⚠️ | something removed by a screen — **removed is not cleared** |
| ⬜ | coverage and provenance |

## Posting it where it is being discussed

Put `---` between your own commentary and the brief, and say which is which
above the line. Otherwise the reader cannot tell what would arrive tomorrow from
what you are saying about it today, and the caveats read as opinion rather than
as part of the artefact.
