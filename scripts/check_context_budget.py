#!/usr/bin/env python3
"""Measure — and cap — the context loaded into EVERY session and every subagent.

Three artifacts are paid before any work starts:

* `CLAUDE.md` — the shared brief, re-paid in full inside every dispatched subagent.
* `.claude/rules/*.md` **without** `paths:` frontmatter. A path-scoped rule (`plans.md`) loads only
  inside its directory, so it is deliberately NOT counted.
* Each skill's `description:` + `when_to_use:` — the *listing*. A skill's body is paid only when the
  skill fires, so the body is warned about but never counted toward the budget.

Run it directly for the table; `tests/test_context_budget.py` runs it as the gate.

    uv run python scripts/check_context_budget.py

**Token counts are a `bytes/4` proxy, and that is deliberate.** The accurate method
(`messages.count_tokens`) needs an API key and a network call, which a repo hygiene check should
not require; `tiktoken` is OpenAI's tokenizer and undercounts Claude by ~15-20% (more on code), so
it is worse than the proxy rather than better. A ceiling only needs to be deterministic and
directionally correct.

Stdlib only, and takes an optional repo path — so it runs in any project, with or without a test
runner: `python3 scripts/check_context_budget.py [repo]`. Wire it into whatever gate the project
already has (pytest, a lint job, a pre-push hook).

**What to cut when it fails: facts stay, behavioural scaffolding goes.** A fact is something the
model cannot derive — an id, a path, a gotcha, the gate command — and it helps a weaker model tier
*more*, not less. Behavioural scaffolding is what a capable model now does unprompted (verify before
claiming done, don't over-ask). Delete the second kind, and prove it: stub the line out, run the case
it was written for, and keep it deleted only if behaviour holds.
"""
from __future__ import annotations

import pathlib
import re
import sys
from dataclasses import dataclass, field

# Raise this ONLY with a reason in the commit message. It ratchets down as scaffolding is removed;
# it must never drift up to accommodate accretion — that is the failure it exists to prevent.
CEILING_TOKENS = 6_000

# `description` + `when_to_use` are truncated at 1,536 chars in the skill listing, so text past the
# cap is silently invisible to routing. Warn early enough to leave room for an edit.
LISTING_CAP_CHARS = 1_536
LISTING_WARN_CHARS = 1_400

# A loaded skill's body stays in context across turns, and auto-compaction re-attaches only the
# first ~5,000 tokens of each skill. Past this, split into SKILL.md + reference/ (see slack-block-kit).
BODY_WARN_LINES = 400

_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def _tokens(chars: int) -> int:
    return chars // 4


def _frontmatter(text: str) -> str:
    m = _FRONTMATTER.match(text)
    return m.group(1) if m else ""


def _field(frontmatter: str, name: str) -> str:
    """A YAML scalar that may fold across lines, read up to the next top-level key."""
    m = re.search(rf"^{name}:\s*(.*?)(?=\n[A-Za-z_-]+:|\Z)", frontmatter, re.S | re.M)
    return m.group(1).strip() if m else ""


@dataclass
class Report:
    rows: list[tuple[str, int]] = field(default_factory=list)   # (label, chars)
    warnings: list[str] = field(default_factory=list)

    @property
    def total_chars(self) -> int:
        return sum(c for _, c in self.rows)

    @property
    def total_tokens(self) -> int:
        return _tokens(self.total_chars)

    def table(self) -> str:
        width = max((len(label) for label, _ in self.rows), default=10)
        lines = [f"{'artifact'.ljust(width)}   chars   ~tokens", "-" * (width + 18)]
        for label, chars in sorted(self.rows, key=lambda r: -r[1]):
            lines.append(f"{label.ljust(width)} {chars:7d} {_tokens(chars):9d}")
        lines.append("-" * (width + 18))
        lines.append(f"{'ALWAYS-ON TOTAL'.ljust(width)} {self.total_chars:7d} {self.total_tokens:9d}"
                     f"   (ceiling {CEILING_TOKENS})")
        return "\n".join(lines)


def measure(repo: pathlib.Path) -> Report:
    report = Report()

    brief = repo / "CLAUDE.md"
    if brief.exists():
        report.rows.append(("CLAUDE.md", len(brief.read_text(encoding="utf-8"))))

    # Non-recursive globs: a git worktree under .claude/worktrees/ carries its own .claude/ tree,
    # and rglob would double-count every skill in every worktree on disk.
    for rule in sorted((repo / ".claude" / "rules").glob("*.md")):
        text = rule.read_text(encoding="utf-8")
        if re.search(r"^paths:", _frontmatter(text), re.M):
            continue                                    # path-scoped: not always-on
        report.rows.append((f"rules/{rule.name}", len(text)))

    listing_chars = 0
    for skill in sorted((repo / ".claude" / "skills").glob("*/SKILL.md")):
        text = skill.read_text(encoding="utf-8")
        fm = _frontmatter(text)
        name = skill.parent.name
        listing = len(_field(fm, "description")) + len(_field(fm, "when_to_use"))
        listing_chars += listing
        if listing > LISTING_CAP_CHARS:
            report.warnings.append(
                f"{name}: listing is {listing} chars — OVER the {LISTING_CAP_CHARS}-char cap; "
                "the tail is truncated and invisible to routing")
        elif listing > LISTING_WARN_CHARS:
            report.warnings.append(
                f"{name}: listing is {listing} chars, near the {LISTING_CAP_CHARS}-char cap")
        body_lines = len(text.splitlines())
        if body_lines > BODY_WARN_LINES:
            report.warnings.append(
                f"{name}: body is {body_lines} lines — a loaded skill stays in context across "
                "turns and compaction keeps only its first ~5,000 tokens; split into "
                "SKILL.md + reference/")
    if listing_chars:
        report.rows.append(("skill listings (description + when_to_use)", listing_chars))

    return report


def main(argv: list[str]) -> int:
    repo = pathlib.Path(argv[1]) if len(argv) > 1 else pathlib.Path(__file__).resolve().parents[1]
    report = measure(repo)
    print(report.table())
    print("\n(tokens are a documented bytes/4 proxy — see this script's docstring)")
    if report.warnings:
        print(f"\n{len(report.warnings)} warning(s) — not counted in the budget, still worth fixing:")
        for w in report.warnings:
            print(f"  - {w}")
    if report.total_tokens > CEILING_TOKENS:
        print(f"\nFAIL: {report.total_tokens} tokens is over the {CEILING_TOKENS} ceiling.")
        return 1
    print(f"\nOK: {report.total_tokens} <= {CEILING_TOKENS}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
