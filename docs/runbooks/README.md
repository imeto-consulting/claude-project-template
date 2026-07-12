# Runbooks

Durable, step-by-step instructions for the **human-only** steps a delivery depends on — the things
no tool can do: OAuth consent, a secret value, a cloud IAM role, sharing a resource with a service
account, a DNS record, a cross-repo PR. One file per topic.

See the [`manual-steps`](../../.claude/skills/manual-steps/SKILL.md) skill for how to write one:
the *symptom* it fixes, **clickable links** (console + vendor doc), and **numbered, copy-pasteable**
steps — verified against the external system's own docs, never from memory. This directory starts
empty; add a runbook the first time a delivery hits a genuinely-human step.
