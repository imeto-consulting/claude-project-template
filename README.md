# Claude Code project template

A starter for building small personal projects **mostly agentically** with Claude Code — you
do the thinking and the deciding, Claude does most of the typing. It comes pre-wired with the
[Superpowers](https://github.com/obra/superpowers) workflow and a light set of rules and skills
so your repo stays clean and your work stays *provable*.

The idea: think it through with Claude, write the plan down, bake in a way to **verify it works
from the start**, then let agents build while you review. Aim for *lagom* (just-right)
over-engineering — the smallest version that ships and that you can prove works.

---

## New to agentic development? Start here

Three kinds of building blocks shape how Claude behaves in this repo. Knowing which is which
makes the rest of this README click:

- **Plugins** — installed bundles of capabilities (skills, slash-commands, sometimes tools).
  You install them once. The big one here is **Superpowers**, which provides the
  brainstorm→plan→build workflow. Plugins are listed in [`.claude/settings.json`](.claude/settings.json).
- **Skills** — focused, reusable procedures Claude pulls in *when they're relevant* (or when you
  type `/skill-name`). Some come from plugins (e.g. `superpowers:brainstorming`); some are local
  to this repo, in [`.claude/skills/`](.claude/skills/). Local skills often build *on top of*
  plugin skills.
- **Rules** — project instructions in [`.claude/rules/`](.claude/rules/) that load into context
  automatically and shape behavior in the background. You don't invoke them. A rule either loads
  **every session** (no `paths:` header — like `mandate.md`) or **only when you touch matching
  files** (a `paths:` header — like `plans.md`, which loads when you work in `docs/plans/`).

A couple more terms used below:

- **Spec / plan** — a *spec* (or "design doc") captures *what* you're building and why; a *plan*
  breaks it into small checkbox tasks. Both live in [`docs/plans/`](docs/plans/).
- **Worktree** — a second checkout of your repo on its own branch, so an agent can build a
  feature without disturbing your main working copy.
- **Subagent** — a fresh Claude instance dispatched to do one task in its own context, then
  report back. Good for parallel work and keeping the main conversation focused.

> Rules are the guardrails (always on). Plugin skills are the heavy machinery (brainstorm, plan,
> execute). Local skills are the glue and the contracts that hold *your* conventions in place.

---

## Getting started

1. **Use this as a template** (or copy the files into a new repo) and open it in Claude Code.
2. **Install the plugin** — first session only. If prompted to install
   `superpowers@claude-plugins-official`, accept. Otherwise run
   `/plugin install superpowers@claude-plugins-official`. It stays enabled afterward.
3. **Orient.** Ask Claude to run the `inventory` skill — it reports what's in flight and proposes
   a next move. On an empty repo it'll just say "nothing yet."
4. **Tell Claude what you want to build** and follow the loop below.

---

## The workflow, end to end

Here is one full trip around the loop, with the piece that does the work named at each step.
**P** = plugin, **S** = local skill, **R** = rule.

```
   ┌─ orient ──────────────────────────────────────────────────────────────┐
   │  inventory (S) reads docs/ROADMAP.md + docs/plans/ → "here's the state" │
   └────────────────────────────────────────────────────────────────────────┘
                │
   idea ───►  docs/ROADMAP.md  (jot it under Now / Next / Later)
                │
   design ──► superpowers:brainstorming (P) ──► spec in docs/plans/*-design.md
                │   audit-validation (S): grep the code before trusting a claim
                │   commit the spec right away
                ▼
   plan ────► superpowers:writing-plans (P) ──► plan in docs/plans/*.md
                │   plans.md (R): Goal · Scope · Verification (+ RCA if it follows a failure)
                │   commit the plan BEFORE branching a worktree
                ▼
   build ───► using-git-worktrees (P)  +  subagent-driven-development (P)
                │   subagent-handoff (S): goal in, evidence out, fixed report shape
                │   test-driven-development / systematic-debugging (P)
                │   mandate.md (R): when to just-do vs. ask
                ▼
   verify ──► verification-before-completion (P): run the plan's check, capture real output
                │
   land ────► commit-commands (P): /commit or /commit-push-pr   (github plugin for PR review)
                │   settings.json puts `git push` behind a confirm; merge the worktree to main
                ▼
   close ───► close-out (S): all [x] → archive plan, paste evidence, update both roadmaps
                │
   improve ─► retro (S) every few plans: did we honor the rules? fix the ones that didn't
                │   skill-creator (P): turn a hard-won pattern into a new skill
                └──────────────► (back to orient)
```

### Phase by phase

**0. Orient.** At the top of a session, the `inventory` **skill** gives you a one-screen read of
active plans, any drift, and a proposed next move — so you don't start cold. Two **rules** are
already in context: `mandate.md` (always) and, once you're working in `docs/plans/`, `plans.md`.

**1. Capture the idea (roadmap).** Add a line to [`docs/ROADMAP.md`](docs/ROADMAP.md) under
**Now**, **Next**, or **Later**. The roadmap is the human index of where the project is going.

**2. Design → spec.** Run `superpowers:brainstorming` (**plugin**). It asks Socratic questions to
pull the real intent out of you — answer stream-of-thought, just react until the shape feels
right. It writes a spec; the `plans.md` **rule** redirects it to
`docs/plans/<date>-<topic>-design.md` (not under any plugin's name). If your idea rests on a claim
about existing code ("X is missing", "Y is slow"), the `audit-validation` **skill** says: grep and
confirm it *before* planning. **Commit the spec immediately.**

**3. Plan.** Run `superpowers:writing-plans` (**plugin**). It turns the spec into small checkbox
tasks. The `plans.md` **rule** requires every plan to open with **Goal** (user-observable
outcome), **Scope** (what's in, what's out), and **Verification** (a *runnable* check — a test or
a command with expected output, not "looks right"). If the plan follows a previous failure, it
also cites the root cause (**RCA**). **Commit the plan before you branch a worktree** — a worktree
branches from `main` as it is now, so an uncommitted plan won't be inside it.

**4. Implement.** For anything bigger than a quick fix, isolate the work with
`superpowers:using-git-worktrees` (**plugin**), then let `superpowers:subagent-driven-development`
(**plugin**) run one **subagent** per task. Wrap every dispatch in the `subagent-handoff`
**skill**: the subagent's prompt opens with the goal, it must report *what it did / how it
verified the goal / what it assumed*, and you verify the user-observable result before marking the
task done. `test-driven-development` and `systematic-debugging` (**plugin**) guide the coding and
any bug-hunting. The `mandate.md` **rule** keeps the agent moving — it does reversible, mechanical
work outright and only stops to ask for genuinely strategic or outward-facing calls.

**5. Verify.** Before claiming done, `superpowers:verification-before-completion` (**plugin**) runs
the plan's Verification check and captures the real output. Evidence, not "should pass."

**6. Land on main.** Use the `commit-commands` **plugin**: `/commit` for a local commit, or
`/commit-push-pr` to push and open a pull request (the **github** plugin helps review/merge it).
`git push` is behind a confirm in [`.claude/settings.json`](.claude/settings.json) — outward-facing
actions get a human nod, matching the mandate. Merge the worktree branch back to `main`.

**7. Close out.** When every box is `- [x]`, run the `close-out` **skill**. It refuses to finish
without evidence, archives the plan *and its design spec* to `docs/plans/archive/`, updates both
roadmaps — removes the line from `docs/ROADMAP.md` and appends it to the shipped log at
`docs/plans/archive/ROADMAP.md` — and keeps `README.md` honest if the work changed what the
project does. And it draws the line between *green* and *delivered*: passing tests mean the code
works, not that the people it's for can use it — if getting it to them is a separate step, that
step stays on the roadmap as open work.

**8. Improve.** Every few plans, run the `retro` **skill**: it re-reads recently shipped plans
against the rules, finds where the workflow drifted, and **fixes the rule that should have caught
it**. When you discover a pattern worth keeping, the `skill-creator` **plugin** turns it into a new
skill. This is how the template gets sharper with every project.

---

## Who does what (quick reference)

| Stage        | Does the work                                                   | Type             |
| ------------ | -------------------------------------------------------------- | ---------------- |
| Orient       | `inventory`                                                     | local skill      |
| Always on    | `mandate.md` (when to act vs. ask)                              | rule             |
| In `docs/plans/` | `plans.md` (how plans are written)                         | rule (path-scoped) |
| Idea         | `docs/ROADMAP.md`                                               | doc              |
| Design       | `superpowers:brainstorming` + `audit-validation`               | plugin + local skill |
| Plan         | `superpowers:writing-plans`                                     | plugin skill     |
| Isolate      | `superpowers:using-git-worktrees`                              | plugin skill     |
| Build        | `superpowers:subagent-driven-development` + `subagent-handoff` | plugin + local skill |
| Debug / test | `superpowers:test-driven-development` / `systematic-debugging` | plugin skills    |
| Verify       | `superpowers:verification-before-completion`                   | plugin skill     |
| Commit / PR  | `commit-commands`, `github`                                     | plugins          |
| Close out    | `close-out`                                                     | local skill      |
| Improve      | `retro`, `skill-creator`                                        | local skill + plugin |

---

## Where everything lives

| File / folder                | What it's for                                              |
| ---------------------------- | --------------------------------------------------------- |
| `CLAUDE.md`                  | The brief Claude reads every session (the workflow above) |
| `docs/ROADMAP.md`            | Now / Next / Later — what you're working on               |
| `docs/plans/`                | Specs and active implementation plans                     |
| `docs/plans/archive/`        | Finished plans + the shipped log (`ROADMAP.md`)           |
| `.claude/settings.json`      | Enabled plugins and permissions                            |
| `.claude/rules/plans.md`     | How plans are written (loads when you work in `docs/plans/`) |
| `.claude/rules/mandate.md`   | When the agent acts on its own vs. asks you                |
| `.claude/skills/`            | `close-out`, `inventory`, `audit-validation`, `subagent-handoff`, `retro` |

## Why plans live in `docs/plans/`

Superpowers defaults to saving plans under `docs/superpowers/...`, which stamps the plugin's name
into your repo. This template overrides that — plans are *your* decision records, so they live in
`docs/plans/`, version-controlled and readable in a diff. See
[`.claude/rules/plans.md`](.claude/rules/plans.md).

## Make it yours

**When you start a real project from this template**, make it yours right away — rewrite the top
of `CLAUDE.md` to describe *your* project (not "a starter template"), and replace this `README.md`
with a real README for what you're building. Don't copy this workflow essay into your repo; keep
the workflow by linking back here instead. A README that still describes the template is the most
common drift there is.

**As you use it**, when you land on a pattern worth keeping, ask Claude to turn it into a skill
(`skill-creator`) or a rule in `.claude/rules/`. The `retro` skill exists to feed this loop — and
to push those improvements *back here*, so the next project inherits them. The template gets
sharper with every project.
