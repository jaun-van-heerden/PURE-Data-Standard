#!/usr/bin/env python3
"""PURE v0.1 corroboration — count evidence roots, not reports.

Usage:
    python3 tools/roots.py REPORT.json [REPORT.json ...]

Resolves declared derivation (`via` claims) among the given reports,
collapses each derivation chain to its root, and shows for every
claimed value how many INDEPENDENT roots support it. Fifty
republications of one wire story are one root.

Root counts are provenance breadth, not truth (SPEC.md §9): they are
not sybil-resistant and always decompose into the source list printed
here.
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


def short(url, n=50):
    s = url.removeprefix("https://").removeprefix("http://")
    return s[: n - 1] + "…" if len(s) > n else s


def find_root(url, by_url, seen=None):
    """Follow via edges to the ultimate root. A via target outside the
    given set is itself the root (unknown work, still collapses chains)."""
    seen = seen or set()
    if url in seen:
        return url  # cycle guard: treat as its own root
    seen.add(url)
    report = by_url.get(url)
    if report is None:
        return url
    vias = [c["v"] for c in report["claims"] if c["f"] == "via" and isinstance(c["v"], str)]
    if not vias:
        return url
    return find_root(vias[0], by_url, seen)


def main():
    paths = sys.argv[1:]
    if not paths:
        print(__doc__.strip())
        return 2
    reports = [json.load(open(p, encoding="utf-8")) for p in paths]
    by_url = {r["source"]["url"]: r for r in reports}

    keys = {event_key(r) for r in reports}
    if len(keys) == 1:
        print(f"{len(reports)} reports · event key: {keys.pop()}\n")
    else:
        print(f"WARNING: reports span {len(keys)} event keys — comparison may be meaningless:")
        for k in sorted(keys, key=str):
            print(f"  {k}")
        print()

    root_of = {url: find_root(url, by_url) for url in by_url}
    w = max(len(short(u)) for u in by_url) + 2
    print("report".ljust(w) + "root")
    print("-" * w + "----")
    for url in by_url:
        r = root_of[url]
        print(short(url).ljust(w) + ("(self) — independent root" if r == url else f"via → {short(r)}"))
    roots = set(root_of.values())
    print(f"\ndistinct roots: {len(roots)}\n")

    support = {}
    for url, report in by_url.items():
        for c in report["claims"]:
            if c["f"] in ("what", "when", "where", "via", "said"):
                continue
            key = (c["f"], canon(c["v"]))
            support.setdefault(key, {"roots": set(), "reports": 0})
            support[key]["roots"].add(root_of[url])
            support[key]["reports"] += 1

    print("value support (independent roots, not reports):")
    fw = max(len(f"{f}={v}") for f, v in support) + 2
    for (f, v), s in sorted(support.items()):
        n_roots, n_reports = len(s["roots"]), s["reports"]
        note = f"  ({n_reports} reports)" if n_reports > n_roots else ""
        print(f"  {(f + '=' + v).ljust(fw)}{n_roots} root{'s' if n_roots != 1 else ''}{note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
