---
name: manual-steps
description: Use when delivering, deploying, or closing out ANY work that depends on a step only a human can perform — an OAuth consent / redirect-URI registration, a secret *value*, a cloud IAM role or console click, sharing a resource with a service account, a DNS record, or a cross-repo PR. Collect every such step and hand the user an explicit, actionable checklist BEFORE calling the work delivered, and track it to done; never silently drop one. Triggers on standing up or deploying a service/integration, wiring OAuth / secrets / IAM, and at close-out.
---

# Surfacing manual steps — the human handoff you must never drop

The mandate ("do everything you have a tool for; don't over-ask", `.claude/rules/mandate.md`) has a
mirror image: the few steps you genuinely **cannot** do must be **surfaced explicitly**, never
silently skipped. A dropped manual step is how "shipped" becomes "broken in prod" — an unregistered
OAuth callback URI, a version-less secret, a skipped cross-repo PR: none surfaced, each a silent
breakage that costs a deploy incident and hours of a non-working service.

## The rule

**A human-only step is part of the delivery, not an aside — it is never skipped.** A feature whose
manual step isn't done is not delivered; it's broken. When work depends on such a step, then
**before** calling it delivered you MUST:

1. **Collect** every such step — the exact artifact and value ("register
   `https://<host>/auth/callback` in the OAuth client"), not a vague "set up OAuth."
2. **Write it into a runbook** in `docs/runbooks/` — the durable deliverable, not an ephemeral chat
   message. **Always** include: the *symptom* it fixes (the exact error the reader hits without it),
   **clickable links** (the console URL, the vendor-doc URL), and **numbered step-by-step**
   instructions with copy-pasteable values. One file per topic; extend an existing runbook rather
   than duplicating it.
   - **EXACT, not gestural.** Each step is either the **literal command** with real values or the
     **exact console path + the exact control/privilege name**. "Raise its access level", "go to
     settings", "grant the right permission" are **not steps** — they're shrugs the reader can't act
     on. If you're about to write a vague verb, you don't know the step yet — go find it.
   - **Verify an EXTERNAL system's steps against that system's own docs before writing them — never
     from memory.** Console menus, auth mechanisms, and privilege names drift and are easy to
     misremember. Fetch the vendor's doc and confirm the exact path/mechanism. (Ties to
     `.claude/rules/knowledge-capture.md`: consult before asserting.)
3. **Point the user at the runbook** in your reply (link + one-line "do these N steps"), and **track
   it** as a ROADMAP delivery thread (`.claude/rules/plans.md`) naming each open step. Discharge each
   the moment it lands; a pile of open threads is drift.
4. **Never silently drop one.** "Out of scope / non-blocking / someone will do it" is the failure
   mode.
5. **The runbook is the answer — don't re-narrate steps in chat.** Once a human-only step exists, the
   runbook is where it lives; your reply *links to it*. When the user asks about that step again — or
   a follow-up ("which command?", "where exactly?") — **update the runbook to be more exact, then
   point there**; do **not** retype the steps into chat turn after turn. Re-narrating in chat is the
   failure mode: it isn't durable, each retelling drifts from the last, and it wastes the exchange. If
   you catch yourself pasting steps into a reply for the second time, that's the signal the runbook
   entry is missing or too vague — fix *it*.

Do **not** surface a step you actually have a tool for — that's over-asking (see
`.claude/rules/mandate.md`). This skill is only for the genuinely-human steps below.

## What is typically human-only

- **OAuth consent screen + OAuth clients** — creating/editing a client, and **registering a new
  host's redirect/callback URI** (`https://<host>/auth/callback`). A missing redirect URI →
  `redirect_uri_mismatch` and auth never completes. (Infrastructure-as-code often can't manage OAuth
  clients — check before assuming you can automate it.)
- **Secret *values*** — IaC can create the container; a human supplies the value. A mounted secret
  with **no version** often won't even boot the service.
- **Cloud IAM roles / privileges / a console click** the IaC can't (or doesn't yet) express.
- **Sharing a resource with a service account** — a shared calendar, a spreadsheet, a doc/DB. If the
  service account is not granted broad delegation, it sees only what it is explicitly shared; until
  the share is done the tool 403s / 404s.
- **DNS records** the IaC can't express.
- **Cross-repo work** — a PR in another repository your change depends on (e.g. a shared
  template/marketplace). Do it in the same slice, or surface it as a required follow-up.

## The test

"Can I do this with a tool I have?" → do it, don't ask (mandate). "Is this genuinely human-only —
a value / consent / role / share / console click / other-repo I can't reach?" → **collect it,
surface it as a checklist, track it to done.** The step you drop is the one that breaks prod.
