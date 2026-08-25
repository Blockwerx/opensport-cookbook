# First run, without a terminal

For someone who wants to *use* the brief rather than adapt it. You will not need
to type a command — you paste a request, and the assistant does the setup and
tells you what it needs.

If you are comfortable with the command line, [the README](../README.md) has the
two-line version instead.

## Before you start

**Claude Code.** The desktop app is fine — this works the same there as in a
terminal.

**The OpenSport connector, switched on.** Your OpenSport contact sets this up.
The brief reads your squad's training-load alerts through it, so nothing below
works until it is on.

## 1 · Install it

Paste this and send it. Replace `SOURCE` with whatever you were given — either
`Blockwerx/opensport-cookbook`, or the path to a folder if someone sent you one.

```
I want to set up the OpenSport pre-session brief. I'm not a developer — please
do the work yourself and explain what you're doing in plain language.

Install it:

1. Add this plugin marketplace: SOURCE
2. From it, install the plugin called opensport-briefs.
3. Confirm it installed, and tell me what came with it — there should be a skill
   called pre-session-brief and a subagent called brief-critic.

Then check I'm ready to run it:

4. Check whether the OpenSport connector is switched on, and tell me either way.
   Don't try to set it up yourself — if it's off, say so and I'll go to my
   OpenSport contact.
5. Tell me whether I need to restart before the plugin will work, and if so,
   exactly what to do and what to paste when I come back.

While you do this:

- Don't send, email or post anything today.
- If a step fails, stop and tell me what failed and what you need from me. Don't
  try a workaround or another route without asking me first.
- If you need me to approve something, tell me what it does before I approve it.
```

You will see permission prompts as it works. Approving them with **always
allow** saves you approving the same thing every day.

## 2 · Run it once

Restart the app first if you were asked to. Then:

```
Run the pre-session brief for the senior squad, 7 days back, 5 cards.
Show it to me here — don't send it anywhere.
```

The first run on a squad of about 80 athletes takes a few minutes. The brief
never sends itself: it drafts, checks itself against its own rules, and hands
you the result.

**If you want it emailed**, that needs a mail connector switched on in the same
place, alongside OpenSport. Without one, a scheduled run will produce a brief
and deliver nothing.

## 3 · Have it arrive every morning

Open **Scheduled → New task** and paste this as the instructions:

```
Run the pre-session-brief skill for today's session.

Squad: senior squad
Window: 7 days back from today
Cards: 5

Report observations only — no suggestions, no recommendations, no status labels.

Send to the configured recipients when the brief-critic gate passes. If a
blocking rule fails after one revision pass, do not send — reply to me with the
failing rule and the offending lines instead.
```

Two things worth knowing:

- **Click *Run now* once** and approve the prompts, or the first scheduled run
  sits waiting for you overnight and you wake up to nothing.
- **A local task only fires while the app is open and the machine is awake.**

The last paragraph of that prompt matters more than it looks. *After one
revision pass* lets the brief fix itself once before giving up; without it, a
single wording slip on the first draft means no brief at all — which reads like
the thing is broken when it is actually working exactly as designed.

## What to look at on the first few mornings

Three failures that look like successes. The
[full list is in getting-started](getting-started.md#what-to-check-on-the-first-few-runs).

- **The headline count.** It should read *N of the M who trained* — not *N of
  your whole roster*. On a loading week nearly everyone who trained is past
  threshold, so a rate against the roster makes a normal week look like a
  crisis.
- **The closing statement**, all four clauses, including *absence of a card is
  not clearance*. A brief naming five athletes has, in writing, declined to name
  the rest.
- **Length.** Around 600 words. If one arrives at 1,500, the tiering has
  collapsed and the provenance is sitting in the email instead of behind links.

## When something goes wrong

Say what happened, in your own words, to the assistant that ran it — *"the
brief came back but the links don't open anything"* is enough. It has the skill
and the rules in front of it and can usually tell you which of the two is at
fault.

One known limit worth naming so you don't report it as a bug: **alert links
depend on your deployment.** Where the server does not yet hand over an alert's
id, links fall back to the athlete's profile, which highlights the row rather
than opening the alert. The brief says when it has fallen back — a silent
fallback would be the defect, not the fallback itself.
