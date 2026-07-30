---
name: cross-model-prompting
description: How to write an instruction that several different models must obey — the three layers (facts, structure, tier scaffolding) and which layer is allowed to vary. Read before writing or editing any model-facing text that more than one model consumes, before assuming a prompt fix must be per-model, and when deciding whether guidance belongs in a tool description, a shared instruction, or a per-tier addendum.
---

# Cross-model prompting

Prompting advice is model-specific and it changes. Anthropic's Claude-5 guidance says to *remove*
verification instructions; Google's Gemini guidance says to add structure, examples and a pre-send
self-check. Both are right, for their model. The mistake is applying either to a shared artifact.

**Split every model-facing text into three layers by who owns the divergence.**

## Layer 1 — Facts and contracts (model-independent)

Ids, paths, gotchas, argument shapes, what a write actually does, the gate command. These never vary
by model, they live **once**, and they help a weaker model *more* than a stronger one.

Never tier-gate a fact. When cutting a prompt, this layer stays.

## Layer 2 — Structure (cheap for everyone, harmful to none)

Labelled lists over prose blobs. Delimiters. An inline example per rule. An explicit output format.
Critical constraints last.

Structure is not a model-specific tax: a delimited, example-carrying instruction is at worst neutral
for a frontier model and decisive for a small one. **So write shared artifacts to the structural bar
of the weakest consumer.** You pay ~nothing on the strongest.

## Layer 3 — Scaffolding (genuinely per-tier — compose it, never bake it in)

Anti-satisficing persistence directives, pre-send self-checks, negation handling, thinking/effort
settings, delegation caps, verbosity instructions.

This is where models genuinely disagree, and it is the **only** layer allowed to vary. Compose it per
model at call time; never write it into an artifact a second model also reads.

## Before you assume a fix must be per-model, trace who reads what

Most "we need per-model prompts" conclusions dissolve once you check which consumer actually reads
which artifact. Build the table for your project — artifact, who reads it, is it cross-family — and
you will usually find only **one** genuinely shared surface (typically tool descriptions, which every
consumer reads). Layer-3 scaffolding must never go there.

The corollary matters as much: an artifact only one model family reads does **not** need per-model
composition, however tempting the symmetry.

## The authoring bar vs the contract

> **A pass from one model is an authoring bar, never a contract.**

Gate a shared artifact with the *strongest* consumer's judgement, write it to the *weakest*
consumer's structural bar, and keep per-tier scaffolding in a composed layer that never touches the
artifact.

## Record rejections, with what would reopen them

A per-model change you considered and rejected is a standing claim about what won't work. Write it
down with its rationale and with the evidence that would change your mind — otherwise the next
session re-derives it, or quietly does the opposite. See
[`knowledge-capture.md`](../../rules/knowledge-capture.md).
