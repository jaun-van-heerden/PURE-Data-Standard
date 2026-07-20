#!/usr/bin/env python3
"""PURE v0.1 report validator.

Usage:
    python3 tools/validate.py REPORT.json [--source SOURCE_FILE] [--class CLASS_FILE.md]

Checks a report against the core spec (SPEC.md):
  - structure: report and claim key sets, required reserved claims
  - grounding: every claim's `q` is a verbatim substring of the source
  - integrity: source sha256 matches, claims sorted, canonical bytes
  - fields: claim fields exist in the class file table, `ext:`, or reserved
Prints the report ID and derived event key on success. Exit 0 = valid.

RFC 8785 note: this validator covers the value types the core spec allows
(strings, numbers, {min,max}, booleans, null). Decimal numbers serialize
per RFC 8785's ECMAScript shortest round-trip rule (Python's json matches
for ordinary decimals).
"""
import argparse
import hashlib
import json
import math
import re
import sys

RESERVED = {"what", "when", "where", "via", "said"}
REPORT_KEYS_REQUIRED = {"pure", "source", "claims"}
REPORT_KEYS_ALLOWED = REPORT_KEYS_REQUIRED | {"revises"}
SOURCE_KEYS = {"url", "sha256", "retrievedAt"}
CLAIM_KEYS_REQUIRED = {"f", "v", "q"}
CLAIM_KEYS_ALLOWED = CLAIM_KEYS_REQUIRED | {"by", "t"}

errors = []


def err(msg):
    errors.append(msg)


def canon(obj):
    """RFC 8785 canonical serialization for spec-allowed value types."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def check_value(v, where):
    if v is None or isinstance(v, (str, bool)):
        return
    if isinstance(v, (int, float)):
        if isinstance(v, float) and not math.isfinite(v):
            err(f"{where}: numbers must be finite")
        return
    if isinstance(v, dict):
        if not v or not set(v) <= {"min", "max"}:
            err(f"{where}: object values must be {{min?,max?}} and non-empty")
        for k, n in v.items():
            if not isinstance(n, (int, float)):
                err(f"{where}: {k} must be a number")
        return
    err(f"{where}: unsupported value type {type(v).__name__}")


def parse_class_fields(path):
    """Extract field names and types from the class file's normative table."""
    fields = {}
    in_table = False
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line.startswith("|"):
            in_table = False
            continue
        cells = [c.strip().strip("`") for c in re.split(r"(?<!\\)\|", line.strip("|"))]
        if not cells:
            continue
        if cells[0].lower() == "field":
            in_table = True
            continue
        if set(cells[0]) <= {"-", " ", ":"}:
            continue
        if in_table and cells[0]:
            fields[cells[0]] = cells[1] if len(cells) > 1 else ""
    return fields


def check_field_type(claim, ftype):
    f, v = claim["f"], claim["v"]
    t = ftype.replace("\\|", "|")
    if t == "count":
        ok = v is None or (isinstance(v, int) and v >= 0) or isinstance(v, dict)
        if not ok:
            err(f"claim {f}: count must be a non-negative integer, {{min?,max?}}, or null")
    elif t == "bool":
        if not (v is None or isinstance(v, bool)):
            err(f"claim {f}: bool must be true, false, or null")
    elif t == "string":
        if not (v is None or isinstance(v, str)):
            err(f"claim {f}: string field must be a string or null")
    elif t == "number":
        if not (v is None or (isinstance(v, (int, float)) and not isinstance(v, bool))):
            err(f"claim {f}: number field must be a number or null")
    elif t.startswith("enum(") and t.endswith(")"):
        allowed = t[5:-1].split("|")
        if not (v is None or v in allowed):
            err(f"claim {f}: value {v!r} not in enum {allowed}")


def event_key(claims):
    by_f = {}
    for c in claims:
        by_f.setdefault(c["f"], c)
    what = by_f.get("what", {}).get("v")
    when = by_f.get("when", {}).get("v")
    where = by_f.get("where", {}).get("v")
    if not all(isinstance(x, str) for x in (what, when, where)):
        return None
    day = when[:10]
    cell = where[4:8] if where.startswith("geo:") else where
    return f"{what}|{day}|{cell}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("report")
    ap.add_argument("--source")
    ap.add_argument("--class", dest="class_files", action="append", default=[],
                    help="class file(s); repeat for classes/common.md + the event class")
    args = ap.parse_args()

    raw = open(args.report, "rb").read()
    try:
        report = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"INVALID: not JSON: {e}")
        return 1

    if not isinstance(report, dict):
        print("INVALID: report must be a JSON object")
        return 1
    missing = REPORT_KEYS_REQUIRED - set(report)
    extra = set(report) - REPORT_KEYS_ALLOWED
    if missing:
        err(f"report: missing keys {sorted(missing)}")
    if extra:
        err(f"report: unknown keys {sorted(extra)}")

    src = report.get("source")
    if not isinstance(src, dict) or set(src) != SOURCE_KEYS:
        err(f"report.source: must have exactly keys {sorted(SOURCE_KEYS)}")
        src = src if isinstance(src, dict) else {}

    claims = report.get("claims")
    if not isinstance(claims, list) or not claims:
        err("report.claims: must be a non-empty array")
        claims = []

    source_text = None
    if args.source:
        src_bytes = open(args.source, "rb").read()
        source_text = src_bytes.decode("utf-8")
        actual = hashlib.sha256(src_bytes).hexdigest()
        if src.get("sha256") != actual:
            err(f"source.sha256 mismatch: report says {src.get('sha256')}, file is {actual}")

    class_fields = None
    if args.class_files:
        class_fields = {}
        for cf in args.class_files:
            class_fields.update(parse_class_fields(cf))

    seen_f = set()
    for i, c in enumerate(claims):
        where = f"claims[{i}]"
        if not isinstance(c, dict):
            err(f"{where}: must be an object")
            continue
        missing = CLAIM_KEYS_REQUIRED - set(c)
        extra = set(c) - CLAIM_KEYS_ALLOWED
        if missing:
            err(f"{where}: missing keys {sorted(missing)}")
        if extra:
            err(f"{where}: unknown keys {sorted(extra)}")
        f = c.get("f")
        if not isinstance(f, str) or not f:
            err(f"{where}: f must be a non-empty string")
            continue
        seen_f.add(f)
        q = c.get("q")
        if not isinstance(q, str) or not q:
            err(f"{where} ({f}): q must be a non-empty string — no quote, no claim")
        elif source_text is not None and q not in source_text:
            err(f"{where} ({f}): q is not a verbatim substring of the source: {q!r}")
        check_value(c.get("v"), f"{where} ({f})")
        if f == "said" and "by" not in c:
            err(f"{where}: said requires by")
        if class_fields is not None and f not in RESERVED and not f.startswith("ext:"):
            if f not in class_fields:
                err(f"{where}: field {f!r} not in class file, not reserved, not ext:")
            else:
                check_field_type(c, class_fields[f])

    for req in ("what", "when", "where"):
        if req not in seen_f:
            err(f"report: required claim {req!r} is absent")

    keyed = [(c["f"], canon(c)) for c in claims if isinstance(c, dict) and isinstance(c.get("f"), str)]
    if keyed != sorted(keyed):
        err("report.claims: not sorted by (f, canonical bytes)")

    canonical = canon(report).encode("utf-8")
    if raw.rstrip(b"\n") != canonical:
        err("report file is not in canonical form (RFC 8785 bytes)")

    if errors:
        print(f"INVALID: {args.report}")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"VALID: {args.report}")
    print(f"  report id: sha256:{hashlib.sha256(canonical).hexdigest()}")
    key = event_key(claims)
    if key:
        print(f"  event key: {key}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
