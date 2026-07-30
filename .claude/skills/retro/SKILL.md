---
name: retro
description: Periodic re-read of recently shipped work against the project's own rules, to catch workflow drift and fix the rules that didn't fire. Use after archiving a few plans, every couple of weeks, or when the user says "let's retro." Where inventory is "what's hanging now" and close-out is "this plan is done", retro is "did the last N plans honor the workflow we said we follow?"
---

# Retro

**Announce at start:** "Running retro — re-reading the last N plans against our rules."

The improvement loop. The template only gets sharper if drift gets caught and the rules get
fixed. This skill finds the drift and commits the fix — it does not just report.

Cadence: after ~3 plans archive, every ~2 weeks, or on request. Not every session (too costly).

## Steps

### 1. Gather

```bash
ls -t docs/plans/archive/*.md 2>/dev/null | grep -v ROADMAP | head -3
git log --since="2 weeks ago" --oneline
```

Skim each archived plan and its commits.

### 2. Plan-format drift (against `.claude/rules/plans.md`)

For each plan, score yes/no:
- Opened with **Goal** in plain user language, not mechanism?
- **Scope** explicit (in, and what was left out)?
- **Verification** observed the goal, not just "lint passed"?
- Close-out captured real **evidence** (test output, exit codes)?
- Archived when done — didn't drift unarchived in `docs/plans/`?

Any "no" is a finding.

### 3. Workflow drift (against `.claude/rules/mandate.md`)

Read the execution's commits and messages:
- Were Tier 1 actions just done, or punted with "want me to…?"
- Were Tier 3 (destructive / outward-facing) actions escalated, not silently taken?

Every "want me to…?" for something the mandate calls Tier 1 is a finding.

### Context-budget drift — and the prune

**A retro that only ADDS is incomplete.** The natural failure mode is a ratchet: every retro adds a
rule and none ever removes one, so `CLAUDE.md` and the skill listings grow without limit — and they
are paid in every session *and every dispatched subagent*.

```bash
python3 scripts/check_context_budget.py
```

1. **Report the delta** since the last retro — total, and which artifact moved.
2. **Act on every warning**: a skill listing near the 1,536-char cap (past it, the tail is invisible
   to routing), a body over 400 lines (a loaded skill stays in context across turns, and compaction
   keeps only its first ~5,000 tokens).
3. **Prune at least one rule per pass.** Candidates are *behavioural scaffolding* — an exhortation to
   verify, to not over-ask, to report faithfully. **Never a fact** (an id, a path, a gotcha, a gate
   command): facts help a weaker model tier *more*, not less. Prove it by stubbing the line out and
   running the case it was written for.
4. **If the budget grew**, say so plainly and name what to cut next time. A ceiling raised to
   accommodate accretion is the failure the ceiling exists to prevent.

### 4. Output + fix

If clean: `Retro <date> — N plans reviewed: clean.`

If findings: list each (what drifted, which rule should have caught it, why it didn't), then —
per `.claude/rules/mandate.md` Tier 2 — **make the rule/skill edits in the same commit**, with the
reasoning in the message. A retro that lists findings without committing fixes is half a retro.

## Not this skill

- Not code review (that's per-PR). Not `inventory` (that's "now"). Not `close-out` (that's one plan).
- Don't debate findings: if a rule didn't fire, fix the rule. If it was right but unused, fix the
  skill that should have invoked it. If both were right but attention slipped, shorten the cadence.
