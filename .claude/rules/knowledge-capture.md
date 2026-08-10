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

**This applies with extra force to a change shipped as a direct PR with no plan**, where the facts
live only in the commit message — less discoverable than an archived plan, since nothing greps
commit bodies by topic. Land the facts in a skill **in the same PR**.

**Search the skill BODY, not only its `reference/` files — silence in one file is not absence.** A
skill's `SKILL.md` is what loads by default; `reference/` holds the overflow. Grepping one file,
finding nothing, and concluding the fact is unrecorded is a real and repeated failure — in one case
walking straight into the trap the skill body documented in terms, including the sentence naming the
exact thing not to do. `grep -r` over the whole skill directory costs the same as one file.

**Before asking the human a factual question, consult the skills and runbooks first.** Search
`.claude/skills/` and `docs/runbooks/` for the fact before raising it as a question. A documented
fact — a confirmed setting, a verified permission, a standing "no, that doesn't exist here" — must
not be re-asked. If you find yourself about to ask something a skill already answers, that's a
signal you skipped the lookup, not that the fact needs re-confirming.

## Also covered: a REJECTED option, and a PATTERN that worked

"Environment fact" reads as settings and permissions. Extend it: a **design decision and its
rationale** — especially an option you **rejected** — and a **solution pattern that generalizes past
its own use case** are design-driving facts too, and they rot in an archive the same way. A rejection
is a standing claim about what won't work; if it is wrong, nothing will tell you, because the plan
holding it never resurfaces.

The cost, measured in a downstream project: one plan rejected building a bulk primitive as useless.
**Two days later** another plan built exactly that primitive — one read instead of ~60 — and cited
the rejection nowhere. When the same problem class came round a third time, the pattern that had
solved it was still buried in a plan about something else, so it wasn't there to reach for.

So: when a plan rejects an option, or lands a pattern that generalizes, write it into the matching
skill in the same change — **with the rationale**, so a later session can recognise when the
rationale no longer holds. **If a later plan implements something an earlier plan rejected, go update
the rejection** rather than quietly proceeding.

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
