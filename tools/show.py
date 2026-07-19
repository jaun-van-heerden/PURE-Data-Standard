#!/usr/bin/env python3
"""PURE v0.1 show — the hierarchical, event-shaped view of a report.

Folds a report's flat claims into the nested event object implied by the
dotted field names (casualties.deaths -> {"casualties": {"deaths": ...}}).

This is a VIEW, never the stored form: flat claims keep one fact = one
unit (which is what makes diffing, corroboration counting, and agreement
measurement trivial); the tree keeps humans oriented. The fold is lossy
by default (quotes dropped) — use --receipts to keep every value's
quote, attribution, and as-of time.

Usage:
    python3 tools/show.py REPORT.json [--receipts]
"""
import argparse
import hashlib
import json
import sys


def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def set_path(tree, dotted, value):
    parts = dotted.split(".")
    node = tree
    for p in parts[:-1]:
        nxt = node.setdefault(p, {})
        if not isinstance(nxt, dict):
            sys.exit(f"field conflict: {dotted!r} nests under an existing leaf {p!r}")
        node = nxt
    leaf = parts[-1]
    if leaf in node:  # two claims on one field -> list
        prev = node[leaf]
        node[leaf] = prev if isinstance(prev, list) else [prev]
        node[leaf].append(value)
    else:
        node[leaf] = value


def leaf(claim, receipts):
    if not receipts:
        return claim["v"]
    out = {"value": claim["v"]}
    for k, name in (("by", "by"), ("t", "asOf"), ("q", "quote")):
        if k in claim:
            out[name] = claim[k]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("report")
    ap.add_argument("--receipts", action="store_true")
    args = ap.parse_args()

    report = json.load(open(args.report, encoding="utf-8"))
    rid = "sha256:" + hashlib.sha256(canon(report).encode("utf-8")).hexdigest()

    event, body, ext, statements, via = {}, {}, {}, [], []
    for c in report["claims"]:
        f = c["f"]
        if f in ("what", "when", "where"):
            event[f] = leaf(c, args.receipts)
        elif f == "said":
            s = {"by": c.get("by"), "statement": c["v"]}
            if args.receipts:
                s["quote"] = c["q"]
            statements.append(s)
        elif f == "via":
            via.append(c["v"])
        elif f.startswith("ext:"):
            set_path(ext, f[4:], leaf(c, args.receipts))
        else:
            set_path(body, f, leaf(c, args.receipts))

    view = {"event": event, **body}
    if ext:
        view["ext"] = ext
    if statements:
        view["statements"] = statements
    if via:
        view["via"] = via if len(via) > 1 else via[0]
    what, when, where = (report_val(report, k) for k in ("what", "when", "where"))
    view["report"] = {
        "id": rid,
        "eventKey": event_key(what, when, where),
        "pure": report["pure"],
        "source": report["source"]["url"],
        "retrievedAt": report["source"]["retrievedAt"],
    }
    print(json.dumps(view, indent=2, ensure_ascii=False))
    return 0


def report_val(report, f):
    for c in report["claims"]:
        if c["f"] == f:
            return c["v"]
    return None


def event_key(what, when, where):
    if not all(isinstance(x, str) for x in (what, when, where)):
        return None
    cell = where[4:8] if where.startswith("geo:") else where
    return f"{what}|{when[:10]}|{cell}"


if __name__ == "__main__":
    sys.exit(main())
