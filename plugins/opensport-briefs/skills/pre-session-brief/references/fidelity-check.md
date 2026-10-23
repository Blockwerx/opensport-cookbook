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

- **That a matched number is the right one.** Matching is by value. A small
  integer outside an athlete row can coincide with an unrelated field; the
  per-row scoping and the statistic check narrow this, they do not close it.
- **Prose.** A sentence with no number — an invented match report, a cause — is
  not checked here. Rule 12 still forbids it; the critic checks it.
- **Unit and phrasing.** "% of" versus "% above", and units, are rules 4 and 5,
  for the critic.

When the check fails, fix the brief — remove the element whose field is
missing — and re-run it. Do not add a payload, edit one, or declare a derived
count to make a figure pass.
