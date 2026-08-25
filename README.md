# OpenSport Cookbook

Worked examples for building agentic workflows on the **OpenSport MCP server** —
the prompts, skills, subagents and generation rules behind them, in full, so you
can install them, read how they work, and adapt them to your own squad.

These are not screenshots of a product. They are the actual artefacts: a skill
file an agent follows, a rules file it is held to, and a reviewer subagent that
blocks output which breaks those rules.

## What's here

| Recipe | What it does |
|---|---|
| [`pre-session-brief`](plugins/opensport-briefs/skills/pre-session-brief/SKILL.md) | Sweeps a squad's training-load alerts and writes one short staff email naming the handful of athletes whose data moved most, with each figure's provenance and limits stated. |

Supporting pieces for that recipe:

- [`brief-generation-rules.md`](plugins/opensport-briefs/skills/_shared/brief-generation-rules.md)
  — eleven rules the output is held to. Five of them block a send.
- [`brief-critic`](plugins/opensport-briefs/agents/brief-critic.md) — a subagent
  that reviews each draft against those rules and refuses the ones that fail.
- [`brief-template.md`](plugins/opensport-briefs/skills/pre-session-brief/assets/brief-template.md)
  — the output structure.
- [`squad-sweep.md`](plugins/opensport-briefs/skills/pre-session-brief/references/squad-sweep.md)
  — how to read a whole roster's alerts, and the traps in doing it.
- [`sample-output.txt`](examples/pre-session-brief/sample-output.txt) — a
  synthetic example of the finished email.

## Install it

```bash
/plugin marketplace add Blockwerx/opensport-cookbook
```

Then install the plugin:

```bash
/plugin install opensport-briefs@opensport-cookbook
```

You will also need the OpenSport MCP server connected, so the skill has data to
read. See [docs/getting-started.md](docs/getting-started.md).

Two other routes, depending on who is setting it up:

- **Without a terminal.** [docs/first-run.md](docs/first-run.md) walks through
  the same install by pasting requests rather than typing commands, and covers
  the connector, the first run and scheduling it.
- **Without installing anything.** [docs/no-install-prompt.md](docs/no-install-prompt.md)
  is a single prompt for a plain chat window. It reproduces the six blocking
  rules inline, and states plainly what it gives up by doing so.

## What these recipes will not do

**They report. They do not advise.** No recipe here suggests a training change,
assigns an availability status, or tells a coach what to do with a session. That
is a deliberate boundary, enforced by a blocking rule and checked by the critic
subagent — see [docs/what-this-does-not-do.md](docs/what-this-does-not-do.md).

If you want an assistant's opinion on an athlete's session, you can ask for one
directly. That is your decision to make and to own. What these recipes will not
do is make it for you, unprompted, at six in the morning.

## Why the rules file is the interesting part

The hard problem in generating a brief like this is not fetching data. It is
that a complete, arithmetically correct brief can still be unreadable — or
worse, confidently wrong in ways nothing in the payload flags.

The rules file is where that lives. A sample of what it catches:

- A rate published against the wrong denominator. "50 of 82 past threshold"
  sounds like a crisis; if 31 of those 82 did not train, the real figure is 50
  of 51, and the finding is about the threshold rather than the athletes.
- A percentage computed against a baseline the server has already declined to
  vouch for.
- A ratio off a near-zero baseline. On one live sweep, the five largest
  excursions in the squad were all measurement artefacts, and none of them
  carried a warning flag.
- The same observation counted four times, because four rules fired on one
  figure.
- A figure presented as stable when the engine recomputes it nightly.

Each rule states the failure it prevents, so you can judge whether it applies
to your setup rather than taking it on faith.

## Adapting a recipe

| To change | Edit |
|---|---|
| What the email looks like | `assets/brief-template.md` |
| What is and isn't allowed in the output | `skills/_shared/brief-generation-rules.md` |
| Which tools are called, in what order | the skill's `SKILL.md` |
| How strictly it's enforced | `agents/brief-critic.md` |
| Cadence, recipients, squad | the routine prompt |

The routine prompt is deliberately thin. Everything that governs the output
lives in versioned files, so changing the brief is a diff you can review rather
than a prompt you retune.

## Feedback

Issues and pull requests welcome. If a rule is wrong for your context, or a
recipe hits something these files do not cover, that is worth telling us.

Contributing? See [CONTRIBUTING.md](CONTRIBUTING.md) — everything here is
customer-facing, which constrains what can go in a file more than it usually
would.
