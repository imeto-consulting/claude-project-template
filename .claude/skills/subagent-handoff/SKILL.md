---
name: subagent-handoff
description: Use whenever you dispatch a subagent to do real work (implement a task, review, investigate). Layers a delivery contract on top of superpowers:subagent-driven-development so the handoff carries intent in and proves the outcome out — a subagent can't come back vague or "done" without evidence.
---

# Subagent handoff

A reliability layer over `superpowers:subagent-driven-development` (and
`superpowers:dispatching-parallel-agents`). Use that skill's flow; add the three rules below to
every dispatch. The failure mode this prevents: a subagent reports "done", the dispatcher marks
it done on faith, and nobody checked the actual user-observable result.

## 1. Carry intent IN — every prompt opens with the goal

Start each subagent prompt with a **Goal** section, copied verbatim from the plan's Goal (the
user-observable outcome, not the mechanism). Instruct the subagent: *if the task as specified
doesn't serve this goal, stop and report `BLOCKED` with why* — don't build the wrong thing well.

## 2. Fixed report shape — so it can't come back vague

The subagent's final message must answer three questions, explicitly:

1. **What I did** — the concrete change or finding.
2. **How I verified the goal** — the user-observable check actually run (a command + its output,
   a file read, a request/response). Not "tests pass." If nothing was verified, say so.
3. **What I assumed / deviated** — anywhere it diverged from the spec or goal.

Reject and re-dispatch any report missing one of the three.

## 3. Verify outcomes OUT — before marking done

For any task whose goal is user-observable, the **dispatcher** runs its own verification before
marking it done — don't mark done on the subagent's word alone. Run the command, read the file,
hit the endpoint. Lint and unit tests passing are hygiene; they are not proof the goal is met.
(See `superpowers:verification-before-completion` and `.claude/rules/plans.md`.)

## Isolate the session in a worktree (default for plan implementation)

Run plan implementation in a **dedicated worktree** (`superpowers:using-git-worktrees`), not the
primary checkout — always, not only when subagents conflict. A worktree has its own HEAD, so a
concurrent session sharing the clone can't switch your branch or revert your commit under you.
**One worktree per session.** Before any commit or push, confirm `git rev-parse --abbrev-ref HEAD`
is your branch (not `main`), and stage only your own files (`git add <paths>`, never `git add -A`
in a shared tree — it sweeps another session's uncommitted work into your commit).

## Subagents share the primary checkout's `.git` — so the controller commits, not the subagent

A git worktree shares one `.git` with the primary checkout, and a **dispatched subagent's `cd` does
not persist across its Bash calls** — each tool call runs in a fresh shell whose cwd is the
*primary* working directory. So `cd <worktree>` in one call is gone by the `git commit` in a later
call, and the commit lands on the **primary checkout's branch (`main`)** — not the worktree branch
— even when the subagent reports "confirmed branch is `<feature>`" (that check ran in yet another
fresh shell). A subagent that also runs `git push` puts the stray commit on shared `origin/main`,
bypassing review. This recurs even with `cd`-based guards written into the brief: policing subagent
git per-call does not hold under pressure.

**Default: the controller commits; subagents don't touch git.** For plan implementation, have the
subagent **edit files and run tests only**, and report back the changed file paths plus the test
command and its output. The **controller** — which is durably anchored in the worktree (its cwd
persists across your own calls) — does every `git add <paths>` / `commit` / `push`. This removes the
shared-`.git` hazard entirely rather than relying on per-call discipline in every subagent, and
keeps staging explicit (`git add <paths>`, never `git add -A` in a shared tree).

**Recovery if a stray commit lands:** `git cherry-pick` it onto the worktree branch, then restore
the strayed branch — `git revert` (safe, non-destructive) if it was already pushed to shared
`origin/main`, or `git reset --hard origin/main` on a purely-local stray.

**Fallback — only if a subagent genuinely must run git** (e.g. a long autonomous multi-commit task):
(1) the brief tells it to run *all* git ops as `git -C <absolute-worktree-path> …` (add/commit/branch
— never a bare `cd && git`), since `-C` is per-invocation and immune to the non-persisting cwd; and
(2) the controller still verifies each task's commit actually landed on the worktree branch before
marking it done — `git -C <worktree> log` shows the new HEAD, and the branch grows by exactly the
task's commits. The final review-package (`git merge-base main HEAD`..HEAD) surfaces a stray as a
*missing* commit.

## When dispatching several at once

Parallel subagents must have non-overlapping scope (separate files/dirs) — see
`superpowers:dispatching-parallel-agents`. If they'd edit the same files, give each its own git
worktree (`superpowers:using-git-worktrees`) and, before each commit, confirm the worktree is on
its own branch, not `main`. Drive a worktree with `git -C <path> …` rather than
`cd <path> && git …` — the `cd`-compound form triggers a permission prompt on every variation
and breaks your flow.
