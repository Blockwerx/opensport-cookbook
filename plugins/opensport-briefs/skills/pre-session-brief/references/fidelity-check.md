# The fidelity check

`scripts/check_fidelity.py` compares the rendered brief with the MCP payloads it
was built from. It is the gate for rule 12, and for the link contract in
`link-targets.md`. A brief is sent only when the critic's verdict is `send`
**and** this check passes; the two are not substitutes — the critic reads
wording, the check reads figures and links.

## What the run must keep

Save every MCP tool result **verbatim**, one file per call, into the run's
`payloads/` directory, wrapped with the call that produced it:

```json
{ "tool": "get_athlete_alerts",
  "arguments": { "athleteId": "…", "startDate": "…", "endDate": "…" },
  "result": { "content": [ { "type": "text", "text": "…" }, … ] } }
```

The wrapper matters: per-athlete alert rows do not repeat the athlete id, so the
`arguments` are what tie a row to its athlete. Do not edit, summarise or merge
payloads — the check is only as good as the evidence it is given.

Then write `run.json` beside them:

```json
{ "runDate": "2026-10-23",
  "generatedAt": "2026-10-23T06:40:00+01:00",
  "window": { "start": "2026-10-15", "end": "2026-10-21" },
  "derived": { "roster": ["…ids"], "trained": ["…"], "noSessionInWindow": ["…"],
               "unclassified": ["…"], "alerted": ["…"], "red": ["…"],
               "flagged": ["…"], "carded": ["…"], "screened": ["…"] } }
```

`derived` is the denominator funnel from steps 2–3 — each count given as the
athlete ids it counts, so the number can be checked rather than asserted. Only
those names are accepted; any other name fails. Omit a count you do not render.

## Running it

```bash
python3 scripts/check_fidelity.py --brief <run>/brief.html \
  --payloads <run>/payloads --run <run>/run.json
```

Exit `0` pass, `1` fail, `2` unreadable input (treat as fail). `--json` gives
the same result machine-readably. The host comes from
`assets/brief-config.json`; `--config` points at another file for a test
deployment. Python 3, standard library only.

Run it on the **final rendered HTML** — after the last critic revision — and on
the plain-text alternative too. A figure changed after the check is unchecked.

## What it proves

- **Every number traces.** Each number, date and time in the brief equals, at
  the brief's display precision, a value in the payloads — a numeric field, or a
  figure inside a named text field (`message`, `definition`, a headline) — or a
  derived count from `run.json`, or a rate between two of them (flagged of
  trained, red of alerted, carded of flagged). Dates may also be the run date.
- **Per athlete.** Inside a table row that links to one athlete, a figure must
  come from that athlete's payload or a squad-wide one. A real value borrowed
  from another athlete's alert fails.
- **The statistic matches.** A number next to *maximum / peak / highest*,
  *median*, *average / mean* or *minimum* must come from a field whose name,
  rule or definition says the same. A median quoted as a 28-day maximum fails
  even though the value is real.
- **The label matches.** A number must equal a field that its own label names,
  per `assets/figure-labels.json`. Count words anywhere in the number's clause
  (*trained*, *past threshold*, *carry a red*, *athletes*, …) restrict it to
  those derived counts — "3 carry a red" fails when 3 athletes are flagged but
  one is red. A measure binds tightly — a `%` or `-day` suffix, or *ACR* /
  *ratio* within three words — and restricts it to percentage, window or ratio
  fields. A whole number below 10 with no label fails outside an athlete row:
  small integers are everywhere in the payloads (severity-band counts, window
  lengths), so value alone traces nothing. Inside an athlete row, an unlabelled
  small number may only be one of that athlete's alert measurements
  (`inAthleteRowDefault`). Every failure of this kind names the label table.
- **No review or feedback figures.** A number beside *reviewed*, *actioned*,
  *feedback*, *intervention* or *learning loop* fails: no OpenSport MCP tool
  returns those counts, so any such figure was made up.
- **Links.** Each link uses `appHost`, has no unfilled placeholder, follows a
  route in `link-targets.md`, and names ids found in the payloads — an alert
  link's athlete and alert must be one row.
- **Funnel integrity.** Every derived id is in a payload; carded ⊆ flagged ⊆
  trained; trained, no-session and unclassified do not overlap; every `trained`
  athlete has an alert row with a session date inside `window`.

## What it does not prove

- **That a matched number is the right one.** Matching is by value within the
  fields a label allows. Labels narrow the candidates; they do not identify
  the one field the figure was taken from. A number of 10 or more with no
  label still matches by value alone.
- **An invented count that equals a count named beside it.** Several count
  labels in one clause are an OR, because a sentence such as "3 of the 4
  athletes who trained are past threshold, not 3 of 6" names its counts
  anywhere in the clause, not next to each number. So an invented count passes
  if it happens to equal any derived count the clause names: "4 athletes past
  threshold trained twice" passes when 4 trained, and *athletes* is itself the
  roster label, so "6 athletes did extras" passes on a 6-athlete roster. The
  critic, not this check, catches a true number attached to a false claim.
- **Prose.** A sentence with no number — an invented match report, a cause — is
  not checked here. Rule 12 still forbids it; the critic checks it.
- **Unit and phrasing.** "% of" versus "% above", and units, are rules 4 and 5,
  for the critic.

## The label table

`assets/figure-labels.json` is the one place the brief's wording meets the
payload's field names: `counts` (phrase → derived count), `measures` (suffix or
phrase → field globs), `smallIntegerBelow`, and `inAthleteRowDefault`. A
template that renames a count — "who trained" becoming "who played" — leaves
its number unlabelled. `scripts/tests` renders every count slot in
`brief-template.md`, `slack-template.md` and `email-daily.html` and fails if a
slot lost its label, so change a template's count wording and the table
together. A new `{{slot}}` in a template must also be classified in that test.

When the check fails, fix the brief — remove the element whose field is
missing — and re-run it. Do not add a payload, edit one, or declare a derived
count to make a figure pass.
