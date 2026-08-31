# Daily brief — ChatGPT edition

The pre-session daily brief as **one self-contained prompt** for ChatGPT with
the OpenSport connector. Same rules and layout as the Claude skill in
`plugins/opensport-briefs/`, distilled to run without file references —
ChatGPT loads nothing, so everything the brief must obey is in the prompt
itself.

**How to use (no setup beyond the connector):**

1. Make sure the OpenSport connector is connected (and reconnected if it was
   created before 25 Aug 2026 — see the note at the end).
2. For a one-off: paste the prompt below into a new chat with the connector
   enabled.
3. For every morning: ChatGPT → **Scheduled** → **New task** → paste the same
   prompt as the task instructions, set the time, save.

The prompt, verbatim — copy everything inside the fence:

```
Produce today's OpenSport daily brief for the senior squad, using the OpenSport connector.

WHAT IT IS — a short, scannable table of the ~5 athletes whose training-load
figures moved most vs their own baseline in the last 7 days. It reports
observations only. Never make a suggestion, a recommendation, a training
adjustment, or an availability/injury judgement — if you catch yourself
writing "consider", "should", "monitor" or "modify", delete the sentence.

DATA — call get_squad_alerts once for the last 7 days (severity red), then
paginate with the returned cursor until you have read EVERY page. If you
cannot finish the pages, say how many rows of how many you read — never
present a partial scan as the squad picture. Use list_athletes once for the
roster total.

EXCLUDE before ranking, and say what you excluded:
- Any row whose message contains "Rule processing error" (engine fault, not an athlete).
- Any percentage built on a baseline the row itself does not trust: baseline null, or baselineStatus/state building or incomplete. No baseline, no percentage — state the raw figure or drop the row.
- Deceleration baselines below 1.0 (implausible for a senior collision-sport athlete), baselines below half the squad median for that same alert type in this run, and athletes whose same-type baselines disagree by more than 1.5x within the window (unstable). One line: "N larger excursions screened out on untrustworthy baselines — screened is not cleared."

RANK by how far the figure moved from that athlete's own baseline — never by
severity (in a loaded week nearly everyone is red, so severity separates
nobody; say so with the real numbers: "X of Y athletes with alerts carry a
red"). Mark the largest two rows with a red circle emoji. If one rule type
dominates the table, say so in one line — concentration is a fact about the
week, not five independent problems.

READ FIELDS AS NAMED, never inferred: percentageOfBaseline 228 means 228% OF
baseline; percentageAboveBaseline 128 means 128% ABOVE. Quote observedValue vs
baselineValue. State a unit only when unitVerified is true; otherwise give the
bare number. Round to at most 1 decimal.

FORMAT — exactly this shape, nothing before the title:

**{n} to look at before today** · {Mon D Mon} · senior squad

`{reds}` of `{alerted}` athletes with alerts this week carry a red. Severity separates nobody, so this ranks by how far a figure moved.

| | Athlete | Pos | Why | |
|---|---|---|---|---|
| {red circle or blank} | {Name} | {Pos} | {3-6 word reason} · `{observed}` vs `{baseline}`{ unit} | [open]({link}) |

{red circle} = largest two. Ranked by excursion size, not by concern.
{one-line rule-concentration note, if one rule dominates}
{one-line screened-out note} — screened is not cleared.
Read {rows} of {total} alert rows across {pages} page(s).

Training-load pattern only. No recommendation is made or implied. Not a
medical, injury-risk or return-to-play judgement. Absence of a card is not
clearance.

Figures as of {date} for sessions to {latest session date}.

LINKS — build each athlete's link exactly as
https://app.opensport.io/performance-manager/athlete-performance-dashboard/athlete/{athleteId}?tab=alerts&alert={alertId}
using that row's own athleteId and alertId (the query parameter is alert, not alertId).

LENGTH — the whole brief under ~200 words outside the table. Completeness
lives behind the links, not in the prose.

If get_squad_alerts is not among your available tools, do not fall back to
athlete-by-athlete calls and do not report the capability as missing — tell
the user their OpenSport connector predates the tool and needs to be removed
and re-added once.
```

**The last paragraph matters.** A connector created before a tool shipped
never surfaces it (that is why the reconnect exists as a step). The final
instruction stops the brief from silently degrading into a 60-call sweep — the
failure mode that produced the 28 Aug incident.

**What was deliberately dropped from the Claude skill:** the critic gate (no
subagents in ChatGPT — the blocking rules are inlined as instructions
instead), the HTML email template (ChatGPT's scheduled tasks deliver the chat
output; the markdown table is the visual layer), and the file-reference
structure (nothing to load).
