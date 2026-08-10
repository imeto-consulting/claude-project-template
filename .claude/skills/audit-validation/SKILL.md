---
name: audit-validation
description: Verify a factual premise before you plan — not only claims about the code, but claims about a spec, a doc, or your own earlier measurements. Triggers on "the audit says", "the analysis found", "X is N lines", "the docs say X does Y", "X doesn't exist yet", or any file/symbol/size/pattern/behaviour claim that would shape a plan.
---

# Audit validation — verify the premise before you plan

Before writing a plan against a claim, verify the claim against its source. Audits, AI-generated
analyses, vendor docs, and your own half-remembered measurements all drift from reality. Check first.

**A plan's premises are not covered by its Verification section.** That section proves the
*outcome*; nothing proves the *inputs*. A plan can be perfectly shaped — Goal, Scope, runnable
Verification — and still be built on three false facts.

## The rule

For every claim that would change the plan's shape, run a one-line verification before
brainstorming or writing the plan.

| Claim shape                        | Verify with                              |
| ---------------------------------- | ---------------------------------------- |
| "File X exists / is gone"          | `ls <path>` / `test -f <path>`           |
| "X is N lines"                     | `wc -l <path>` — and **compare it to the threshold you are about to apply** |
| "Pattern P appears M times"        | `grep -rc '<pattern>' <path>`            |
| "Symbol/module X doesn't exist"    | `grep -rn '<name>' .` / `find . -name`   |
| "X is duplicated across A, B, C"   | grep a unique line from the block; read a sample to confirm it's real duplication |
| "Feature X isn't built yet"        | check the **remote** default branch, not just the working tree: `git fetch` then `git show origin/main:<path>` / `git log origin/main --oneline -i --grep=<topic>` |
| **"The spec/docs say X does Y"**   | **re-open the doc and quote the line** — see below |
| **"I measured M earlier"**         | re-run the measurement, or quote the output you are relying on |

Local `main` routinely lags the remote by several merged PRs, so a grep of the working tree can miss
an already-shipped feature. If the human says they "already set up X," trust that and verify against
the remote, not a local snapshot.

## Quote the line; never paraphrase a spec you have already read

The most expensive failures here are not unread sources — they are **sources you read, summarised,
and then planned against the summary**. Having the doc open is what creates the confidence; the
paraphrase is what carries the error. So when a plan depends on how something external behaves,
paste the sentence. If you cannot find a sentence to paste, you do not know the behaviour.

Worked example from a downstream project: a plan shipped three false premises, all three checkable
from material already in context minutes earlier — including "the five files over 400 lines", one of
which was **391**, below the threshold named in the same sentence. Nothing needed new research. The
plan was written from the *narrative* rather than from the measurements taken to support it.

## How to apply

1. Read the claim until you can list its specific assertions.
2. For each assertion that matters, run the matching check above — *before* writing anything.
3. Record the actual measurement next to the claim in the plan's Scope. Note discrepancies.
4. If a check shows the premise is wrong: don't paper over it. Reframe the plan around the real
   code state, or close it with a one-line "premise didn't hold" note.

## Not this skill's job

Writing the plan (`superpowers:writing-plans`) or exploring intent
(`superpowers:brainstorming`). This is a one-step intake check; normal plan workflow follows.
