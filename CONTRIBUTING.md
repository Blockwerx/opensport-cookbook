# Contributing

This repository is read by customers. That single fact drives most of what
follows.

## Nothing internal ships

Every file here is customer-facing, including the ones inside `plugins/` that
look like implementation detail. Before you open a PR, check your diff for:

- **Ticket keys.** No `OS-1234`, no issue numbers, no "closes …". Keep the
  reasoning and drop the reference: "it is being added to the alert payload"
  says everything "it reaches the payload in OS-3406" does, to a reader who
  cannot open the ticket.
- **Internal source paths.** No `src/tools/someFile.ts`. Describe the contract
  instead — "the server's alert value contract" — because a customer cannot
  read the file and does not need to.
- **Internal provenance.** No "observed on dev", no branch names, no "the
  connector token expired". Keep the measurement, lose the war story: "measured
  on a roster of about 80 athletes" carries the useful part.
- **Timestamps and dates that reference internal events.** This one is easy to
  miss because it does not look like an identifier.
- **Real customer data.** No club names, no real athlete identifiers, not even
  pseudonymised ones — a redacted pseudonym still carries a real squad's shape.
  Examples must be synthetic and labelled as such.
- **Absolute paths.** Nothing under `/Users/` or `/home/`. Reference files by a
  path relative to the file doing the referencing.

A quick sweep that catches most of it:

```bash
grep -rnE "OS-[0-9]{3,4}|\.ts\b|on dev|/Users/|[0-9]{2}:[0-9]{2}" . --include="*.md" --include="*.txt"
```

## Numbers need provenance

Where a rule states a threshold, say where the number came from and how
sensitive the answer is to it. A cutoff presented without that is a number the
next contributor cannot argue with or improve.

If a number is provisional — derived from one run, one squad, one week — say
so, and say what would settle it. Rule 2 in
[`brief-generation-rules.md`](plugins/opensport-briefs/skills/_shared/brief-generation-rules.md)
is the worked example.

## Rules earn their place by naming a failure

Each rule in a generation-rules file states the specific failure it prevents,
so a reader can judge whether it applies to their setup. "Be careful with
baselines" is not a rule. "A baseline below half the squad median for the same
alert type is an artefact, and here is the distribution that shows why" is.

Prefer adding a rule with evidence over tightening one without.

## Recipes report, they do not advise

No recipe here suggests a training change, assigns an availability status, or
tells a coach what to do with a session — including in softened forms
("consider", "suggested", "pending sign-off"). This is enforced by a blocking
rule and by the `brief-critic` subagent, and explained to customers in
[`docs/what-this-does-not-do.md`](docs/what-this-does-not-do.md).

If you are adding a recipe, read that page first. It is the repository's
position, not one recipe's setting.

## Layout

```
plugins/<plugin>/
  .claude-plugin/plugin.json
  skills/<skill-name>/SKILL.md          ← under 8 KB; overflow goes to references/
  skills/<skill-name>/assets/           ← templates, prompts
  skills/<skill-name>/references/       ← loaded on demand
  skills/_shared/                       ← shared across skills in the plugin
  agents/                               ← subagents
```

Register a new plugin in [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json).
Keep `SKILL.md` under 8 KB — it is loaded in full whenever the skill triggers,
so detail belongs in `references/`, which is loaded only when needed.

Reference shared files by a path relative to the referencing file
(`../_shared/brief-generation-rules.md`), never absolutely.

## Testing a change

Install from your branch and confirm the plugin still loads:

```bash
/plugin marketplace add /path/to/your/checkout
/plugin install <plugin>@opensport-cookbook
```

If you changed a recipe's behaviour rather than its prose, run it end to end
against a real deployment and say so in the PR. Reading a skill file is not the
same as running it — both findings that reshaped rule 2 came from a run, not a
read.

Say plainly in the PR what you did **not** verify. An unverified claim stated
as verified is worse than a gap you named.
