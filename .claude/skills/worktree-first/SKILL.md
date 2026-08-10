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
#   … edit, commit, push, open PR, merge on green …
git -C <primary-clone> worktree remove .claude/worktrees/<name>   # once the PR reads MERGED
git -C <primary-clone> worktree prune                             # never --force
```

File tools too: operate on the **worktree** path. Absolute paths into the main checkout edit the
wrong tree even while your shell is in the worktree.

## Removing it — on MERGED, by you, from the primary checkout

Each of the three properties has a failure behind it:

- **`PR == MERGED` is the key.** Proof the content reached `main`. *Pushed* is not the same thing —
  a pushed-but-unmerged branch still has work to land.
- **Run it from the primary checkout** (`git -C <primary> …`), never from inside the tree you are
  removing: a session standing in a directory that vanishes loses its footing. Harnesses also tend
  to revert the shell CWD to the primary between tool calls, so `git -C` is the natural form anyway.
- **Plain `remove`, never `--force`.** It refuses on a dirty tree, and that refusal is the guard —
  if it fires, something in there is still live. Stop and look; don't override.

**Remove your own tree as soon as your PR merges — don't defer it to a periodic cleanup.** Measured
in a downstream project that deferred it: **78 worktrees = 45 GB**, ~580 MB each, since every
worktree is a full checkout with its own virtualenv. A cleanup handed to a later session's goodwill
is a cleanup that does not happen. A periodic sweep is still worth having, but as a *backstop* for
trees whose session ended without merging — not as the primary path.

Only your **own** worktree, only after **your** merge: someone else's merged tree may still host a
live session doing follow-up work.

**Never surface any of this to the user** — creation, removal, or the reasoning — in any message. A
"the worktree stays on disk for the next sweep" line is noise, not transparency; it also invites a
question about bookkeeping that you then have to answer.

### Don't "improve" the MERGED key into a commit-graph test

If the repo **squash-merges**, both obvious graph tests break, in opposite directions:

| Key | Verdict |
| --- | --- |
| `git merge-base --is-ancestor <branch> main` | **Wrong.** A squashed branch's commits are never ancestors of `main` — reports merged work as unmerged-and-reapable, inverted. |
| `git log main..<branch>` empty (`ahead == 0`) | **Wrong, oppositely.** Squashing leaves the pre-squash commits "ahead" forever, so merged work reads as unmerged. |
| `git log @{u}..HEAD` empty | **Wrong and dangerous.** A branch with no upstream makes the command error; `wc -l` then prints `0`, so "nothing stranded" is indistinguishable from a failed check. |
| **PR state `MERGED` + clean tree** | **Correct.** The forge's merge state is the authoritative evidence the content landed. |

Two mechanical traps when scripting a sweep: a **branch name is not its directory name** (map them
by parsing `git worktree list --porcelain`, since `git -C ""` silently runs against the primary
checkout instead of failing), and **exclude the tree you are standing in** — a fresh worktree is
clean and 0-ahead until its first commit, so any content-based gate reaps it out from under the
running session.

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
