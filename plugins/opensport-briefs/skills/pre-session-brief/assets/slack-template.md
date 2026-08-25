# Slack template

The same facts as the email, at the same density as the matching brief. Slack is
not a paste target for the email body — the table is what makes it scannable,
and plain text is not.

`{{...}}` are substitutions. Probed rendering support, not assumed: tables,
inline `code`, `---`, bold, italic, emoji and code blocks all render;
**blockquotes do not**.

---

## Daily

```
🏉 *{{n_cards}} to look at before today* · {{date}} · {{squad}}

`{{n_red}}` of `{{n_alerted}}` athletes with alerts this week carry a red. {{denominator_note}}

| | **Athlete** | **Pos** | **Why** | |
|---|---|---|---|---|
| {{marker}} | `{{code}}` | {{pos}} | {{why}} · `{{observed}}` vs `{{baseline}}`{{unit}} | [open]({{alert_link}}) |

🔴 = largest two. Ranked by excursion size, not by concern.
🔵 {{rule_concentration_note}}
⚠️ {{screened_note}} — *screened is not cleared*. <{{screened_link}}|see it>
⬜ {{coverage_note}}

_{{boundary_statement}}_
_Sent automatically · sessions to {{date}} · <{{alerts_index}}|all alerts>_
```

One table row per carded athlete. Every figure in backticks — the monospace chip
is what separates the number from the prose, and without it the row reads as a
sentence with digits in it.

## Review

Same header and same table, then one block per athlete:

```
*`{{code}}` — {{why}}*
{{detail}}
*Not real if →* {{falsifier}}
*Worth opening →* {{pointer}}
<{{alert_link}}|open the alert →>
```

Then the residuals under `*What the screens removed*`, then the boundary
statement. `Not real if →` names a data condition and never an action;
`Worth opening →` names evidence and never a training change. Rule 9 blocks a
send either way.

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
