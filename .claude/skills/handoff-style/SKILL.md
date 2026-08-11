---
name: handoff-style
description: Use when writing text a human reads and acts on — a runbook, a step you hand to a person, a GitHub issue body or triage comment, a PR description, or a README. Carries the eight Simplified Technical English rules, which of them bind prose versus numbered steps, the runbook and ticket skeletons, and the step-then-NOTE shape.
---

# Handoff writing — Simplified Technical English

[`manual-steps`](../manual-steps/SKILL.md) decides **whether** a step is yours to hand over and
**why** it matters. This skill decides **how it reads** — for a runbook, an issue, a triage comment,
a PR description and a README alike.

Your reader may be doing a console click under time pressure, or picking up a ticket cold, and
cannot ask you a question. English may be their second language. ASD-STE100 Simplified Technical
English was written for exactly that reader — aircraft maintenance procedures followed by non-native
speakers, where a misread sentence is expensive.

## Why a shape, and not just a goal

`manual-steps` already says *"numbered, imperative, each step ending in its outcome."* A downstream
project measured its own 143 runbook steps against that:

- **51%** ended in nothing.
- **37%** carried more than one instruction.
- **33%** ran past 20 words.
- Five of nineteen files had no numbered procedure at all.

The rule was not wrong. It was stated as a **goal**, with no shape to copy and no limit on a
sentence. A writer in a hurry then satisfied it by writing prose that mentioned outcomes.

This skill gives you a shape instead, and limits you either met or did not. After the rewrite, that
project measured 352 steps across 18 procedures. None was missing its outcome, over 20 words, or
holding two instructions. The standard is reachable, not aspirational.

## The eight rules

| # | The rule | STE |
|---|---|---|
| 1 | Use a maximum of 20 words in an instruction. | 5.1 |
| 2 | Write one instruction in each step. | 5.2 |
| 3 | Write the instruction in the imperative, in the active voice. | 5.3, 3.6 |
| 4 | If there is a condition, write it first, then a comma, then the command. | 5.4 |
| 5 | Write a NOTE only to give information. Never put an instruction in a NOTE. | 5.5 |
| 6 | End each step with its outcome. | *ours* |
| 7 | Do not use a semicolon. | 8.1 |
| 8 | In descriptive text, use a maximum of 25 words in a sentence and 6 sentences in a paragraph. | 6.3, 6.6 |

Count words the way STE does. Each of these is **one** word:

- a parenthetical (8.5)
- an inline-code span
- a **quoted string** (8.6)
- a hyphenated word (8.7)

A fenced code block does not count at all. The 20 words are the **commanded action only**. The
`→ *outcome*` marker and any `NOTE` are not part of the instruction, so a NOTE may be as long as it
needs to be.

⚠️ **A full stop inside a quoted value is not a second instruction.** `Enter "… group membership. No
delete, no super admin."` is one step. Treat each single-word unit above as opaque before you judge
sentence count, or you will split steps that were already correct.

Rule 6 is ours, not ASD's. It is what `manual-steps` already meant, made checkable.

### Which rules bind which text

A runbook is mostly instructions. A ticket is mostly descriptive text. The eight rules do not all
apply to both.

| Text | Rules that bind |
|---|---|
| Descriptive text — an issue body, a comment, a PR description, a README, a runbook's prose | 3 (imperative/active), 7 (no semicolon), 8 (25 words, 6 sentences) |
| A numbered procedure — runbook steps, a repro, fix steps inside a ticket | all eight |

A ticket exempts three spans a runbook does not, because a ticket carries evidence: a **table row**,
a **`<details>` block**, and a **blockquote**. Quoted material is never rewritten, so it is never
measured. A colleague's message, a model's verbatim output and a log line are evidence — shortening
one falsifies the record.

Three more STE rules help but are not rules here:

- Keep multi-word nouns to three words (2.1).
- Use the `-ing` form only as a noun (3.5).
- Use a vertical list for complex text (4.3).

## What to deliberately NOT adopt

**Part 2, the 875-word approved dictionary.** ASD grants free reuse only to:

- its member associations, and their member companies
- those companies' customers
- ICCAIA members
- defence ministries of member countries, and A4A
- airworthiness authorities, and universities

Most companies are none of these. The spec says *"Unauthorized distribution of ASD-STE100 … is
strictly prohibited."* Read it free at <https://www.asd-ste100.org> — Issue 9, 2025-01-15.
**Cite rule numbers. Ship no word list.**

**A project-local approved-verb list in its place.** Rule 3 already forces the imperative, and a list
would reject a correct verb nobody thought to add.

**A second safety convention.** STE section 7 says what a `⚠️` line already says — name the risk,
lead with the command, state the consequence. Keep using `⚠️`.

**A mechanical checker as a GATE.** Rejected twice downstream, for two different reasons:

- **Runbooks** — *a grep cannot tell a checked fact from the word "none".*
- **Tickets** — they live on the forge, so a test-suite gate cannot see them without a network call
  from CI. That call is flaky and slow, for prose a grep judges badly.

`scripts/measure_ticket_ste.py` ships as an **instrument** instead. Run it when you want the number,
over issues or over local Markdown.

⚠️ **That instrument was wrong four times before it was right.** Every fix came from pointing it at
real prose rather than at its own fixtures:

- It welded a sentence opening on an issue ref.
- It welded consecutive bullets into one run-on.
- It counted a quoted string word-by-word.
- It counted a bold ordinal marker as a sentence.

The first two inflated a measured baseline from 47 to 55. This is CLAUDE.md's *"for a guard, also
assert the detector works"*, applied to a measurement. Re-verify it against your own prose before
you trust a number it gives you.

## The runbook skeleton

```markdown
# <What the reader achieves>

**Who:** <who can do this, and what they must already hold>
**How long:** <honest estimate, and the number of clicks or commands>
**Urgency:** BLOCKING | NEEDED SOON | OPTIONAL HYGIENE
**Result:** <one sentence: what is true when this is done>

## Why this is a human step

<The proof you cannot do it yourself. Show the check you ran.>

## What is broken until you do it

<The concrete consequence. If the honest answer is "nothing observable", say that.>

## ⚠️ Before you start

<Only when there is a hazard. Name the symptom, especially a silent one.>

## Steps

1. <Imperative sentence, 20 words or fewer.> → *<what you now have>*

   NOTE: <information only, never an instruction>

## If it does not work

- **<Symptom>** — <cause and fix.>
```

The three prose sections are already required by `manual-steps`. The skeleton only fixes their names
and their order, so every runbook puts them in the same place.

`⚠️ Before you start` and `If it does not work` are optional. The four header lines and `Steps` are
not.

**A step that is already done keeps its marker:** `✅ DONE 2026-07-24`. That is live state, not
prose. Never delete it during a rewrite.

**A step that is not the reader's** says so and stops: *"The rest is mine. No human is needed."*

## Where the reasoning goes: step, then NOTE

The reasoning does not leave the page and it does not block the step. The step is the action and its
outcome. The `NOTE` under it carries the why.

Hoisting all reasoning into a section above the steps was considered and rejected. It separates a
warning from the step it warns about. That is the failure `manual-steps` calls out for silent
symptoms.

### The worked example

One numbered item holding five instructions, two parentheticals, a semicolon and 72 words:

> 3. Privileges → **Admin API privileges** → **Users**: check **Read**, **Create**, and **Update**.
>    Leave **Delete** unchecked (there is no `users.delete` tool by design — deletion stays a
>    deliberate human action). Also check **Admin API privileges** → **Groups** → **Read** and
>    **Update** (Read for the `hasMember` gate on the password and membership tools; Update for the
>    membership writes those tools make). Save.

After — six steps, at most 12 words each, every one ending in its outcome:

> 3. Click **Privileges** → **Admin API privileges** → **Users**. → *The user privileges open.*
> 4. Select **Read**, **Create** and **Update**. → *Three boxes are selected.*
> 5. Do not select **Delete**. → *Delete stays clear.*
>
>    NOTE: No tool deletes a user. A person deletes a user, on purpose.
>
> 6. Click **Admin API privileges** → **Groups**. → *The group privileges open.*
> 7. Select **Read** and **Update**. → *Two boxes are selected.*
>
>    NOTE: Read makes the membership gate work. Update lets the two group tools write.
>
> 8. Click **Save**. → *The role page shows six privileges.*

## The ticket skeleton

Measured downstream across the 40 most recent issues: hand-written bodies ran **20% of sentences over
25 words**, longest **81 words**, with **42 semicolons**. Bodies filed through a tool ran **3%**,
because a tool forces short named fields. The shape does the work, so hand-written tickets get one
too.

```markdown
**Impact:** <who or what is blocked — one sentence>
**Next step:** <the one action this ticket asks for>

## What is wrong
<Two or three sentences. Use "## What is missing" for an enhancement.>

## Evidence
<Measurement, table, run id, trace, quoted output. Verbatim quotes stay verbatim.>

## What was already tried
<Optional. So the next attempt does not repeat a dead end.>

## Likely fix
<One paragraph. If it is a procedure, number the steps and take all eight rules.>
```

**Two header lines, not the runbook's four.** Labels already carry type and readiness. A duplicated
field goes stale, and a ticket whose header disagrees with its label is worse than one with no
header.

A **triage comment** takes the same three descriptive-text rules. It needs no skeleton — it is a
finding, not a document.

## PR descriptions and READMEs

The same three descriptive-text rules, and no skeleton. One addition for a PR: **lead with what it
delivers, not with how it is built.** The reviewer decides whether to read the diff from your first
sentence.

## Read it back before you commit

1. **Does every step start with a verb the reader performs?** Open, Click, Select, Enter, Paste, Run,
   Copy, Confirm. If a step starts with a noun, rewrite it.
2. **Does every step end with `→ *…*`?** If you cannot name the outcome, you do not know the step.
3. **Does any step hold two instructions?** Look for `and then`, a semicolon, or a second capital
   letter after a full stop. Split it.
4. **Is any instruction longer than 20 words?** Count a parenthetical as one word. Split it.
5. **Does a NOTE tell the reader to do something?** Move that into a step.
6. **Do the four header lines exist, and is the urgency honest?** An optional item labelled BLOCKING
   is how the real BLOCKING ones stop being believed.
7. **Could a colleague do this cold, with no access to you?** If not, name what is missing.
8. **For a ticket: can a reader act on the first two lines alone?** If `Impact` and `Next step` do
   not tell them who is blocked and what is being asked, the body will not either.
9. **Did you rewrite something quoted?** Restore it. Evidence is verbatim.
