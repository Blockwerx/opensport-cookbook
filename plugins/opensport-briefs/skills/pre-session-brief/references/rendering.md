# Rendering: two briefs, two channels

The recipe defines *what may be said*. This defines *how it arrives*, and the
two decisions it turns on are easy to get backwards.

## 1. Two briefs, not one brief at two lengths

They answer different questions at different moments. Conflating them is how the
short one becomes the long one with things deleted — which is the worst of both,
because what gets deleted first is the caveats.

| | **Daily** | **Review** |
|---|---|---|
| When | Before each training session | Weekly, or when something needs investigating |
| Question | *Is there anyone I should look at before this session?* | *What is actually going on with this athlete?* |
| Read on | A phone, in about twenty seconds | A desk |
| Carries | Names, one phrase each, the figure, a link — plus the boundary statement | Evidence lines, the falsifier, the provenance, the residuals |
| Length | ~190 words | ~600 |

**The daily's discipline: anything that can be a link IS a link.**

That is not truncation. A falsifier answers *"why might this be wrong"* — a
question you only ask once you have stopped to look, and stopping to look means
clicking through. Dropping it from the daily is not losing a safeguard; it is
putting it where the reader will actually use it.

This is also why "too wordy" and "drive them back into the app" are one problem
rather than two. The link is what satisfies both, and treating them separately
produces a brief that is shorter *and* still a dead end.

**What never moves to a link:** the boundary statement, in full, all four
clauses, on both briefs. Rule 11 is not a length decision.

## 2. Email is HTML, and Slack is not email

Both render from one set of facts. They must never disagree — they differ in
density, never in content. Diff them before sending.

### Email must be HTML, not plain text

A plain-text brief looks aligned in a monospace editor and arrives broken.
**Gmail renders `text/plain` in a proportional font**, so column alignment, box
rules and any ASCII gutter collapse into ragged text. Send `text/html` with a
plain-text alternative that does not depend on alignment.

Gmail-safe means: layout in `<table>`, colour via `bgcolor` and inline `style`,
and nothing else. Specifically **not** available:

| | |
|---|---|
| `<svg>` inline | stripped |
| `data:` URI in `<img>` | stripped |
| `cid:` + inline attachment | the Gmail API rewrites `Content-ID` to its own `ii_…` value, so the reference never matches and the sanitiser deletes the whole `<img>`. The attachment still arrives, so this one fails while looking like it worked |
| CSS custom properties | ignored — inline literal hex |
| External stylesheets | ignored |

An image in the header therefore requires a **publicly hosted raster**. Until
one exists, use a wordmark rather than passing off a coloured shape as a logo.

### Slack renders more than you would expect

Measured by posting and reading the message back, not assumed: **tables ✅**,
inline `code` ✅ (a monospace chip), `---` dividers ✅, emoji ✅, code blocks
✅, **blockquotes ✅**.

**Write standard markdown, not Slack's mrkdwn.** Both survive — the MCP
converts `[text](url)` to `<url|text>` and passes an already-`<url|text>`
through untouched — which is exactly why a template that mixes them looks fine
and is not. Emphasis is where it bites: `**bold**` becomes bold, but a
mrkdwn-style `*bold*` is converted to `_italic_`. A header written the Slack way
arrives italic and nothing reports an error.

An earlier version of this file said blockquotes do not render. They do. That
claim came from recollection rather than a probe, in a paragraph whose first
two words are "probed, not assumed" — which is the more useful lesson than the
fact itself.

Tables matter: they are what makes the summary scannable where plain text is
not. Put each figure in backticks so the numbers separate from the prose.

### When you post the brief somewhere it is being discussed

Put a divider between your commentary and the brief, and say which is which.
Without it a reader cannot tell what would arrive tomorrow from what you are
saying about it today, and the caveats read as your opinion rather than as part
of the artefact.
