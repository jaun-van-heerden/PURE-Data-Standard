#!/usr/bin/env python3
"""PURE v0.1 report diff — field-by-field comparison of two reports.

Usage:
    python3 tools/diff.py A.json B.json

Confirms the reports share an event key, then prints one row per field:
who claims what, backed by whom, as of when — and whether they agree.
`null` versus a stated value is not a conflict: it means one source
raised the topic without quantifying it.
"""
import json
import sys


def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def event_key(report):
    first = {}
    for c in report["claims"]:
        first.setdefault(c["f"], c)
    what, when, where = (first.get(k, {}).get("v") for k in ("what", "when", "where"))
    if not all(isinstance(x, str) for x in (what, when, where)):
        return None
    cell = where[4:8] if where.startswith("geo:") else where
    return f"{what}|{when[:10]}|{cell}"


def fmt(claim, width=52):
    if claim is None:
        return "—"
    parts = [canon(claim["v"])]
    if "by" in claim:
        parts.append(f"by {claim['by']}")
    if "t" in claim:
        parts.append(f"as of {claim['t']}")
    s = " · ".join(parts)
    return s[: width - 1] + "…" if len(s) > width else s


def verdict(a, b):
    if a is None:
        return "B only"
    if b is None:
        return "A only"
    if canon(a["v"]) == canon(b["v"]):
        return "agree"
    if a["v"] is None:
        return "B quantifies"
    if b["v"] is None:
        return "A quantifies"
    return "DIFFER"


def main():
    if len(sys.argv) != 3:
        print(__doc__.strip())
        return 2
    A = json.load(open(sys.argv[1], encoding="utf-8"))
    B = json.load(open(sys.argv[2], encoding="utf-8"))

    print(f"A: {A['source']['url']}  (retrieved {A['source']['retrievedAt']})")
    print(f"B: {B['source']['url']}  (retrieved {B['source']['retrievedAt']})")
    ka, kb = event_key(A), event_key(B)
    if ka == kb:
        print(f"event key: {ka}  — same event")
    else:
        print(f"event keys DIFFER — these may not be the same event:\n  A: {ka}\n  B: {kb}")
    print()

    rows = []
    fields = sorted({c["f"] for c in A["claims"]} | {c["f"] for c in B["claims"]})
    for f in fields:
        ca = [c for c in A["claims"] if c["f"] == f]
        cb = [c for c in B["claims"] if c["f"] == f]
        if f == "said":
            for c in ca:
                rows.append((f, fmt(c), "—", "A only"))
            for c in cb:
                rows.append((f, "—", fmt(c), "B only"))
            continue
        a = ca[0] if ca else None
        b = cb[0] if cb else None
        rows.append((f, fmt(a), fmt(b), verdict(a, b)))

    header = ("field", "A", "B", "verdict")
    widths = [max(len(r[i]) for r in rows + [header]) for i in range(4)]
    line = "  ".join(h.ljust(w) for h, w in zip(header, widths))
    print(line)
    print("  ".join("-" * w for w in widths))
    for r in rows:
        print("  ".join(c.ljust(w) for c, w in zip(r, widths)))

    via = sum(1 for r in (A, B) for c in r["claims"] if c["f"] == "via")
    roots = 2 - via if via < 2 else "≤2"
    print()
    if via == 0:
        print("evidence roots: 2 — neither report declares derivation (via).")
        print("Root counts are provenance breadth, not truth (SPEC.md §9).")
    else:
        print(f"declared via edges: {via} → distinct roots: {roots}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
