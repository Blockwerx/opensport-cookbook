# What these recipes do not do

A short page, because the boundary matters more than the feature list.

## They report. They do not advise.

Every recipe in this repository surfaces what the data did. None of them says
what to do about it.

That means no recipe here will tell you to cap an athlete's volume, hold them
out of a block, cut change-of-direction work, or mark them modified, monitored
or available. There is no recommendation feature in OpenSport, and a generated
load instruction is not one an automated brief is entitled to give.

This is enforced, not merely intended. It is rule 9 of
[`brief-generation-rules.md`](../plugins/opensport-briefs/skills/_shared/brief-generation-rules.md),
it blocks a send, and the [`brief-critic`](../plugins/opensport-briefs/agents/brief-critic.md)
subagent greps for it before anything is delivered — including for the softened
forms, because "suggested", "consider" and "pending sign-off" are the same act
with a disclaimer attached.

The test the critic applies to every line: **could this change what an athlete
does today?** If yes, it does not ship.

### What that leaves in

Three things that describe the data rather than prescribing a response:

- **Which signal moved**, as attribution — `braking, not volume`. That reads
  the figures. It does not imply what to do about them.
- **What would make the observation wrong** — a contact block inflating GPS
  load, a thin baseline, a deliberately light prior period. A condition, never
  an action.
- **What to look at next to check it** — the session breakdown, the
  deceleration distribution, the wellness screen. Pointing at evidence is not
  prescribing a training change.

### Why we drew it here

When we tested an earlier version of the brief on practitioners, the most
frequent request was the opposite of this: a performance lead and a head coach
both wanted the email organised around what to change about the session. It is
genuinely the more useful document.

We are not shipping it, because the usefulness is borrowed. An unattended
system that emails a prescription every morning has taken a decision that
belongs to the person who knows the athlete, the plan and the week — and it has
put that decision in a retained, timestamped document that will be read back to
someone if an athlete gets hurt.

If you want a model's opinion on a session, ask for one. You will get a
considered answer and you will own the choice to have asked. That is a
different thing from having one arrive uninvited.

## They are not a medical or injury-risk judgement

Every generated brief carries this, verbatim, at any length:

> Training-load pattern only. No recommendation is made or implied. Not a
> medical, injury-risk or return-to-play judgement. Absence of a card is not
> clearance.

The last clause is the one people miss. A brief that names five athletes has,
in writing, declined to name the rest. **Not carded is not cleared** — it means
the brief did not rank that athlete in its top few, nothing more. On a loading
week, nearly everyone who trained will be past threshold.

## They do not see everything

An athlete with no GPS session in the window produces no load signal. The brief
says so explicitly, and phrases it as *no load data means no assessment, not a
negative one* — because the alternative reading, that silence means fine, is
the dangerous one.

Nor is the ranking a risk ranking. Recipes here order athletes by the size of
the excursion in their data, and say so on the page: *ranked by excursion size,
not by concern.*

## Figures are a snapshot

The insight engine re-evaluates historical alerts, so a baseline moves as
history accumulates. The same session's deceleration alert can read 145% above
baseline one morning and 128% two days later — nothing changed about the
session, the comparison moved underneath it.

So computed percentages in a brief are stamped, and absolute observations are
preferred wherever the ratio is doubtful. If you archive briefs and compare
them week to week, compare the absolute figures, not the percentages.
