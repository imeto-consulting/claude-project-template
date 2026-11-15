#!/usr/bin/env python3
"""Token use of this project's Claude Code sessions, from the local transcripts.

Claude Code keeps every session as JSONL under ~/.claude/projects/<encoded path>/, subagents in
<session>/subagents/. This reads the directory for this repo (and its worktrees, whose encoded
paths start with the same prefix) and prints:
spend split main vs subagents, by agent type and model, the most expensive subagents, and cache
misses: turns that rewrote more than 50k tokens of context after a pause longer than that turn's
cache lifetime (5 minutes, or 1 hour with `subagentPromptCacheTtl`), grouped by the tool call the
agent was waiting on, and how many subagent cache writes were 5m vs 1h.

Dollars are API list prices per million tokens (input, output, 5m cache write, 1h cache write,
cache read): edit PRICES when they change. They compare runs; they are not the bill.
Stdlib only.

    python3 scripts/token_usage.py [--since 2026-01-31] [--top 15] [--project /path/to/repo]
"""
import argparse
import collections
import datetime as dt
import glob
import json
import os
import re
import subprocess

PRICES = {  # input, output, cache write 5m, cache write 1h, cache read
    "opus": (5, 25, 6.25, 10, 0.5),
    "fable": (5, 25, 6.25, 10, 0.5),
    "sonnet": (3, 15, 3.75, 6, 0.3),
    "haiku": (1, 5, 1.25, 2, 0.1),
}
MISS_TOKENS = 50_000


def family(model):
    return next((k for k in PRICES if k in (model or "")), "opus")


def price(model):
    return PRICES[family(model)]


def turn_cost(model, u):
    i, o, w5, w1, r = price(model)
    cc = u.get("cache_creation") or {}
    w1t = cc.get("ephemeral_1h_input_tokens", 0)
    w5t = cc.get("ephemeral_5m_input_tokens", 0) if cc else u.get("cache_creation_input_tokens", 0)
    return (u.get("input_tokens", 0) * i + u.get("output_tokens", 0) * o + w5t * w5 + w1t * w1
            + u.get("cache_read_input_tokens", 0) * r) / 1e6


def waited_on(tool):
    name, cmd = tool or ("?", "")
    if name != "Bash":
        return name
    m = re.findall(r"(make [\w-]+|npm (?:run )?[\w-]+|pytest|go test|cargo \w+|sleep|until|gh run watch|docker \w+|python3? [\w/.-]+)", cmd)
    return "Bash: " + (m[-1] if m else cmd[:40].replace("\n", " "))


def read(path, since):
    """One transcript: deduplicated assistant turns with the tool call that preceded each."""
    turns, seen, last_tool = [], set(), None
    with open(path) as f:
        lines = f.readlines()
    for line in lines:
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("type") != "assistant":
            continue
        m = d.get("message") or {}
        u, mid = m.get("usage"), m.get("id")
        if u and mid not in seen and d.get("timestamp", "") >= since:
            seen.add(mid)
            ts = dt.datetime.fromisoformat(d["timestamp"].replace("Z", "+00:00"))
            turns.append((ts, m.get("model"), u, last_tool))
        for b in m.get("content") or []:
            if isinstance(b, dict) and b.get("type") == "tool_use":
                inp = b.get("input") or {}
                last_tool = (b["name"], inp.get("command") or "")
    return turns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="")
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--project", help="repo path (default: this git checkout)")
    args = ap.parse_args()

    project = args.project or subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip() or os.getcwd()
    encoded = re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(project))
    roots = glob.glob(os.path.expanduser("~/.claude/projects/") + glob.escape(encoded) + "*")
    if not roots:
        raise SystemExit(f"no transcripts under ~/.claude/projects/{encoded}*")
    spend = collections.Counter()
    by_type = collections.defaultdict(lambda: [0, 0.0, 0])
    misses = collections.defaultdict(lambda: [0, 0.0])
    agents = []
    ttl_writes = collections.Counter()
    for root in roots:
        for path in glob.glob(root + "/**/*.jsonl", recursive=True):
            sub = "/subagents/" in path
            meta_path = path[:-6] + ".meta.json"
            meta = {}
            if os.path.exists(meta_path):
                with open(meta_path) as f:
                    meta = json.load(f)
            turns = read(path, args.since)
            if not turns:
                continue
            cost, prev, ctx = 0.0, None, 0
            for ts, model, u, tool in turns:
                c = turn_cost(model, u)
                cost += c
                ctx = max(ctx, u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0))
                gap = (ts - prev).total_seconds() if prev else 0
                prev = ts
                cw = u.get("cache_creation_input_tokens", 0)
                cc = u.get("cache_creation") or {}
                one_hour = cc.get("ephemeral_1h_input_tokens", 0) > 0
                if sub:
                    ttl_writes["1h" if one_hour else "5m"] += cw
                if sub and cw > MISS_TOKENS and gap > (3600 if one_hour else 300):
                    k = waited_on(tool)
                    misses[k][0] += 1
                    misses[k][1] += cw * price(model)[3 if one_hour else 2] / 1e6
            spend["subagents" if sub else "main"] += cost
            if sub:
                model = family(meta.get("model") or turns[0][1])
                k = (meta.get("agentType", "?"), model)
                by_type[k][0] += 1
                by_type[k][1] += cost
                by_type[k][2] += len(turns)
                agents.append((cost, len(turns), ctx, model, meta.get("description", "")))

    total = sum(spend.values()) or 1
    print(f"Total ${total:,.0f}: main ${spend['main']:,.0f}, subagents ${spend['subagents']:,.0f} "
          f"({spend['subagents'] / total:.0%})\n")
    print("Subagents by type and model: count, $, turns")
    for (t, m), (n, c, tn) in sorted(by_type.items(), key=lambda kv: -kv[1][1]):
        print(f"  {t:24} {m:8} {n:4} ${c:7,.0f} {tn:6}")
    print(f"\nTop {args.top} subagents: $, turns, peak context, model, description")
    for c, tn, ctx, m, desc in sorted(agents, reverse=True)[: args.top]:
        print(f"  ${c:6,.0f} {tn:5} {ctx / 1000:5.0f}k {m:8} {desc[:60]}")
    w = sum(ttl_writes.values()) or 1
    print(f"\nSubagent cache writes: 5m {ttl_writes['5m'] / w:.0%}, 1h {ttl_writes['1h'] / w:.0%}")
    print("Subagent cache misses after a pause past the cache lifetime, by what the agent waited on: count, $")
    for k, (n, c) in sorted(misses.items(), key=lambda kv: -kv[1][1])[: args.top]:
        print(f"  ${c:6,.0f} {n:4}  {k}")


if __name__ == "__main__":
    main()
