# Getting started

What you need, how to install a recipe, and how to run the pre-session brief for
the first time.

## Prerequisites

**A Claude Code install.** The recipes here are Claude Code plugins — skills,
subagents and prompts. Available in the terminal, the desktop app, the web app,
and the VS Code and JetBrains extensions.

**The OpenSport MCP server, connected.** The recipes read your squad's data
through it. Your OpenSport contact will supply the connection details. Once it
is connected, confirm what your deployment exposes:

```
Ask: what can the OpenSport integration do?
```

That calls the server's own `help` tool, which is version-locked to your
deployment — so it is authoritative about your setup in a way this document
cannot be.

**A squad with GPS data.** The pre-session brief reads training-load alerts, so
it needs sessions on record. It will run against a thin history, and it will
tell you the history is thin rather than quietly comparing against nothing.

## Install

Add this repository as a plugin marketplace:

```bash
/plugin marketplace add Blockwerx/opensport-cookbook
```

Then install the brief recipes:

```bash
/plugin install opensport-briefs@opensport-cookbook
```

## First run

Ask for it in your own words:

```
Run the pre-session brief for today.
```

The skill will:

1. Check which squad-sweep tool your deployment has, and pick its approach
   accordingly.
2. Establish the denominators — who trained this week, who did not, and who it
   cannot classify.
3. Rank the athletes whose data moved most, screening out measurement
   artefacts.
4. Pull the supporting evidence for the shortlist.
5. Draft against the template.
6. Hand the draft to the `brief-critic` subagent, which checks it against every
   generation rule and refuses it if a blocking rule fails.
7. Report — it does not send anything until you have said where it should go.

A first run on a squad of about 80 athletes takes a few minutes, most of it in
step 1.

## What to check on the first few runs

These are the failures that look like successes:

- **The denominator.** The headline should read *N of the M who trained*, not
  *N of your whole roster*. If it reports the roster total, step 2 was skipped.
- **Per-card baseline provenance.** Each athlete should carry its own basis —
  `Baseline 28-day declared`, or `Baseline basis not declared for this rule`.
  A single global claim about baselines means a rule was violated.
- **The boundary statement**, all four clauses, including *absence of a card is
  not clearance*.
- **Length.** Around 190 words for a daily brief, 600 for a review. If a daily
  comes back at review length, the tiering has collapsed and provenance is
  sitting in the email instead of behind links.
- **Artefact screening.** If the brief's largest excursions are all
  deceleration figures in the hundreds of percent, check the baselines they are
  measured against. See rule 2.

## Scheduling it

Once you are happy with the output, the brief can run on a schedule as a Claude
Code routine. The prompt to use is in
[`routine-prompt.md`](../plugins/opensport-briefs/skills/pre-session-brief/assets/routine-prompt.md),
and it is deliberately short — everything that governs the output lives in the
skill's versioned files rather than in the scheduling prompt.

Schedule it early enough that the data cutoff is the previous day's last
session, and late enough that overnight ingestion has settled. Check what the
brief's own `data to …` line reports on the first few runs: if the cutoff is
consistently mid-previous-day, the routine is firing ahead of ingestion.

## Adapting it

Start with [`brief-generation-rules.md`](../plugins/opensport-briefs/skills/_shared/brief-generation-rules.md).
Each rule names the failure it prevents, so you can judge which apply to your
setup. Changing a rule changes every future brief, and the critic enforces
whatever the file says.

If you want a different shape of email, edit
[`brief-template.md`](../plugins/opensport-briefs/skills/pre-session-brief/assets/brief-template.md).
If you want different data, edit the skill's steps.

One thing worth reading before you adapt anything:
[what these recipes do not do](what-this-does-not-do.md).
