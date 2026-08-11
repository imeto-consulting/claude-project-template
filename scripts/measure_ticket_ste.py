"""Measure GitHub issue bodies against the descriptive-text rules in `handoff-style`.

An INSTRUMENT, not a gate. A test-suite gate was rejected twice — for runbooks ("a grep cannot tell
a checked fact from the word 'none'") and for tickets, which live on the forge and would need a
network call from CI to see at all. Run it when you want the number. Stdlib only, and `gh` is needed
only for the issue mode.

    python3 scripts/measure_ticket_ste.py --open
    python3 scripts/measure_ticket_ste.py --state all --limit 40
    python3 scripts/measure_ticket_ste.py --file docs/runbooks/*.md

Counting follows the skill: a parenthetical, an inline-code span, a quoted string and a hyphenated
word each count as one word (STE 8.5-8.7). Fenced code, table rows, `<details>` blocks and
blockquotes are dropped before counting — a ticket carries evidence, and evidence is never rewritten.

Exit code 1 when any issue still violates, so a sweep can assert on it.
"""
import argparse
import json
import re
import subprocess

_FENCED = re.compile(r"```.*?```", re.S)
_DETAILS = re.compile(r"<details>.*?</details>", re.S)
_TABLE_ROW = re.compile(r"^\s*\|.*$", re.M)
_BLOCKQUOTE = re.compile(r"^\s*>.*$", re.M)
_INLINE_CODE = re.compile(r"`[^`]*`")
_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_PARENTHETICAL = re.compile(r"\([^)]*\)")
# STE 8.6: a quoted string is ONE word. Only double and smart quotes — an apostrophe is a
# contraction, not a delimiter. Collapsing these also keeps a semicolon INSIDE a quote out of the
# semicolon count, which is right: quoted material is evidence and is never rewritten.
_QUOTED = re.compile(r"[\"“][^\"“”]*[\"”]")
# The separator swallows trailing markup so a sentence ending in bold ("...the tax.**") still
# splits, and the lookahead admits a sentence opening on an issue ref (#785), a digit or a link.
# A narrower pattern silently welds two sentences into one over-length false positive.
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])[*_`\"'”]*\s+(?=[A-Z0-9*_`\"'“#\[])")
# A list item is its own block. Without this, consecutive bullets have no blank line between them,
# so they measure as one run-on sentence AND as one over-six-sentence paragraph.
_BLOCK_SPLIT = re.compile(r"\n\s*\n|\n(?=\s*(?:[-*+]|\d+\.)\s)")
# A block's leading ordinal marker ("1. ", "**1. ") is a list marker, not a sentence. Left in, its
# full stop splits and the marker counts as a sentence of its own, inflating the paragraph count.
_LEADING_MARKER = re.compile(r"^\s*[*_]{0,2}\d+[.)]\s+")


def strip_exempt(text: str) -> str:
    """Drop every span the standard exempts, then reduce inline code to one token."""
    for pattern in (_FENCED, _DETAILS, _TABLE_ROW, _BLOCKQUOTE):
        text = pattern.sub(" ", text)
    text = _LINK.sub(r"\1", text)
    text = _INLINE_CODE.sub("CODE", text)
    return _QUOTED.sub("QUOTE", text)


def sentences(paragraph: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_SPLIT.split(paragraph.strip()) if s.strip()]


def words(sentence: str) -> int:
    """STE counting: a parenthetical or an inline-code span is one word (8.5, 8.6)."""
    sentence = _QUOTED.sub("QUOTE", _INLINE_CODE.sub("CODE", sentence))
    return len(_PARENTHETICAL.sub(" PAREN ", sentence).split())


def measure(body: str) -> dict:
    clean = strip_exempt(body or "")
    counts = {"sentences": 0, "over_25": 0, "longest": 0,
              "semicolons": clean.count(";"), "paragraphs": 0, "over_6_sentences": 0}
    for paragraph in _BLOCK_SPLIT.split(clean):
        found = sentences(_LEADING_MARKER.sub("", paragraph))
        if not found:
            continue
        counts["paragraphs"] += 1
        counts["over_6_sentences"] += len(found) > 6
        for sentence in found:
            length = words(sentence)
            counts["sentences"] += 1
            counts["longest"] = max(counts["longest"], length)
            counts["over_25"] += length > 25
    return counts


def measure_paths(paths) -> list[tuple[str, dict]]:
    """Measure local Markdown files with the SAME rules an issue body gets.

    `measure()` never cared where the text came from, but `main()` could only reach the forge — so
    in-repo pages held to the same descriptive-text rules were being measured by hand-rolled scratch
    scripts. This exposes what already worked.
    """
    import pathlib

    return [(str(p), measure(pathlib.Path(p).read_text())) for p in paths]


def _fetch(state: str, limit: int) -> list[dict]:
    out = subprocess.run(
        ["gh", "issue", "list", "--limit", str(limit), "--state", state,
         "--json", "number,title,body,author"],
        capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", choices=("open", "closed", "all"), default="all")
    # SUPPRESS, not a default: two actions sharing a dest means the LAST one's default wins, so a
    # plain default here would silently clobber --state's "all".
    parser.add_argument("--open", dest="state", action="store_const", const="open",
                        default=argparse.SUPPRESS, help="shorthand for --state open")
    parser.add_argument("--limit", type=int, default=40)
    parser.add_argument("--file", nargs="+", metavar="PATH",
                        help="measure local Markdown files instead of GitHub issues")
    args = parser.parse_args()

    if args.file:
        rows = measure_paths(args.file)
        offenders = [(name, r) for name, r in rows if r["over_25"] or r["semicolons"]]
        for name, r in rows:
            print(f"{name}: sentences {r['sentences']}  over 25 words {r['over_25']}  "
                  f"longest {r['longest']}w  semicolons {r['semicolons']}  "
                  f"paragraphs over 6 sentences {r['over_6_sentences']}")
        return 1 if offenders else 0

    issues = _fetch(args.state, args.limit)
    total = {"sentences": 0, "over_25": 0, "semicolons": 0}
    offenders = []
    for issue in issues:
        result = measure(issue.get("body") or "")
        for key in total:
            total[key] += result[key]
        if result["over_25"] or result["semicolons"]:
            offenders.append((result["over_25"], result["semicolons"], result["longest"],
                              issue["number"], issue["title"][:58]))

    share = total["over_25"] / max(total["sentences"], 1)
    print(f"{len(issues)} issues ({args.state})   sentences {total['sentences']}   "
          f"over 25 words {total['over_25']} ({share:.0%})   semicolons {total['semicolons']}")
    for over, semi, longest, number, title in sorted(offenders, reverse=True):
        print(f"  #{number:<5} {over:>3} long (max {longest:>3}w), {semi:>2} semi   {title}")
    return 1 if offenders else 0


if __name__ == "__main__":
    raise SystemExit(main())
