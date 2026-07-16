# Knowledge capture — facts live in a skill, not only in a plan

Loaded every session. Answers "where does a fact about the project's environment go once I've
learned it?" A companion to `CLAUDE.md`'s "capture what you learned" step: this is the specific
case of a **design-driving fact about the environment** — a setting, a confirmed absence, an id, a
verified permission, a product decision baked into the setup.

## The rule

**A design-driving fact about the environment lives in a description-matched skill (or a runbook it
links), never only in a plan or design spec.** Plans and specs are retired to `docs/plans/archive/`
once their work ships (see `.claude/rules/plans.md`) — they don't resurface on their own. A skill
fires by description-match every time its topic comes up, in every future session and every
subagent. A fact recorded only in an archived plan is a fact the project has forgotten; the next
session (or subagent) that needs it will re-derive it or re-ask the human for something already
established.

**Before asking the human a factual question, consult the skills and runbooks first.** Search
`.claude/skills/` and `docs/runbooks/` for the fact before raising it as a question. A documented
fact — a confirmed setting, a verified permission, a standing "no, that doesn't exist here" — must
not be re-asked. If you find yourself about to ask something a skill already answers, that's a
signal you skipped the lookup, not that the fact needs re-confirming.

## What this looks like in practice

- Learned a standing environment fact while implementing (a project/account id, an org policy, a
  "no X here" absence, a verified-and-set permission)? Write it into the matching skill (or create
  one, or add a runbook row) in the same change — don't leave it only in the plan's prose.
- About to ask "is X configured?" / "has this permission been granted?" / "does Y exist here?" —
  check the relevant skill/runbook first. Only ask if the lookup comes up empty.
- Writing a plan that depends on an environment fact you just confirmed? Cite the skill/runbook,
  don't just restate the fact in the plan — the plan archives, the skill doesn't.

## Never re-ask for something already provisioned

The same discipline extends from *facts* to *provisioning* — a value, permission, scope, role, or
resource share that has already been set or granted. Re-asking the human to set or grant something
that's already in place is itself a human-in-the-loop failure — the mirror image of re-asking a
settled fact.

- **A live deployment implies its grants exist.** If a service is running in an environment, its
  required secrets, roles, and resource shares are — by definition — already provisioned there.
  Don't ask the human to "make sure X is granted" for something that is demonstrably working;
  record it as verified instead (below).
- **Keep a permission ledger** — a durable "what's already set / granted, never re-ask" index (e.g.
  `docs/runbooks/permission-ledger.md`, added the first time you confirm a grant, the way any
  runbook is created on first need). It is the companion to the `manual-steps` skill: manual-steps
  tracks what's *still outstanding*; the ledger records what's *done*. Consult it before asking the
  human to set or grant anything — if the item is recorded there, assume it's in place and proceed;
  only ask if the ledger has no entry for it.
