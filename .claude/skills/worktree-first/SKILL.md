---
name: worktree-first
description: Use when about to create or switch a git branch, run git checkout / git switch / git checkout -b, start implementing a plan, or commit any work in a clone that more than one session may share (parallel agents, a dispatched subagent, or you plus a human in an editor). Triggers on thoughts like "I'll just branch here", "it's only docs", "I'll switch back to main after", or "no other session is running".
---

# Worktree-first — the primary checkout never leaves `main`

## The rule

When a single clone is shared by more than one session — parallel Claude sessions, a dispatched
subagent, or you plus a human watching in an editor — **the primary checkout stays on `main`,
always.** Every commit-producing task (code, docs, plans, close-outs, config) happens in a
dedicated git **worktree** on its own branch.

`git checkout <branch>` / `git switch` / `git checkout -b` in the primary checkout switches HEAD
for *every* session sharing the clone: commits land on the wrong branch, one session reverts
another's work, and the human loses track of which branch they're on. A worktree has its own
HEAD, so none of that can happen.

**Violating the letter of this rule is violating its spirit.** "I'll switch back" is the bug, not
the mitigation. Mechanics of worktrees: `superpowers:using-git-worktrees`.

## Do this instead

```
git worktree add .claude/worktrees/<name> -b <branch> main   # isolated HEAD, based on main
cd .claude/worktrees/<name>                                  # do ALL the work here
#   … edit, commit, push, open PR …
git worktree remove .claude/worktrees/<name>                 # once pushed / merged
```

File tools too: operate on the **worktree** path. Absolute paths into the main checkout edit the
wrong tree even while your shell is in the worktree.

## Red flags — STOP

- About to run `git checkout -b` / `git switch` / `git checkout <branch>` in the primary checkout.
- "It's just docs / one file / a quick fix — a worktree is overkill."
- "I'll switch the primary back to `main` right after."
- "No other session is running right now." (You can't know that — the clone is shared by design.)
- On `main` in the primary checkout and about to commit feature work.

## Rationalizations

| Excuse | Reality |
|--------|---------|
| "Just docs — branching is overkill" | A branch switch in the primary hits every session regardless of what changed. A worktree is two commands. |
| "I'll switch back to main after" | A concurrent session reads/commits during your window; the round-trip switch is exactly the failure mode. |
| "The tool said 'branch first' on the default branch" | Yes — branch in a **worktree**, never by switching the primary checkout's HEAD. |
| "No other session is active" | The clone is shared by design; you cannot verify it, and the human may glance at the checkout any moment. |

## Verify you're isolated

- In your work session: `git rev-parse --git-dir` shows `…/.git/worktrees/<name>` (a worktree),
  not a bare `.git`.
- The primary checkout still reads `main`: `git -C <primary-clone> branch --show-current` → `main`.
