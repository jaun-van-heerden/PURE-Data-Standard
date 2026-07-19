#!/usr/bin/env python3
"""PURE v0.1 ingest — fetch a source, build the extraction prompt, seal the report.

Usage:
    python3 tools/ingest.py fetch URL --out DIR
    python3 tools/ingest.py prompt DIR --class CLASS_FILE.md
    python3 tools/ingest.py seal DIR --claims CLAIMS.json [--pure REV] [--out FILE]
    python3 tools/ingest.py geo LAT LON [PRECISION]

The three-step flow keeps the protocol model-agnostic:
  fetch   snapshots the exact source bytes (they are what quotes verify against)
  prompt  prints a self-contained extraction prompt for any LLM — or a human
  seal    turns the returned claims array into a canonical, hashed report

`geo` encodes a lat/lon to a geohash locus ID (e.g. for `where`).
Validate the sealed report with tools/validate.py. Stdlib only.
"""
import argparse
import hashlib
import json
import sys
import urllib.request
from datetime import datetime, timezone

UA = "PURE-encoder/0.1 (+https://github.com/jaun-van-heerden/PURE-Data-Standard)"

PROMPT = """You are a PURE encoder. Compile the source below into a JSON array of claims.

A claim is {{"f": field, "v": value, "q": verbatim quote, "by": attributor?, "t": as-of instant?}}.

Rules — all of them:
1. `q` MUST be copied verbatim from the source, byte for byte (including line
   breaks if the quote spans lines). No quote, no claim.
2. Values: string | number | {{"min"?,"max"?}} | ISO-8601 date/time | ID
   (wd:/gn:/geo:/class path) | null. Numbers only when the source states
   numbers ("at least 12" -> {{"min":12}}; a stated 0 is a claim).
3. `v: null` + quote = the source raised the field but stated no value.
   If the source never addresses a field, make NO claim for it.
   Never infer, estimate, sum, or convert beyond stated units/timezones.
4. Required claims: `what` (event class), `when` (event start; keep the
   event-local UTC offset if a local time is stated, e.g.
   2026-06-17T19:56-05:00), `where` (geo:/gn: ID if resolvable, else the
   source's place phrase verbatim).
5. `by` = who the source attributes the value to (their phrase, verbatim),
   only when attributed. `said` claims (attributed statements) require `by`.
6. `via` = URL or name of a work this source derives from, if it credits one.
7. Fields not in the class file use an `ext:` prefix; put the unit in the
   field name (e.g. ext:peak_wind_mph) — do not convert units.
8. If the source describes MULTIPLE events, encode only the one named in the
   request and return claims for it alone.

Output: ONLY the JSON array of claims. No commentary.

=== CLASS FILE ===
{class_file}

=== SOURCE ({url}) ===
{source}
=== END SOURCE ==="""


def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def geohash(lat, lon, precision=6):
    b32 = "0123456789bcdefghjkmnpqrstuvwxyz"
    lat_lo, lat_hi, lon_lo, lon_hi = -90.0, 90.0, -180.0, 180.0
    out, bits, ch, even = "", 0, 0, True
    while len(out) < precision:
        if even:
            mid = (lon_lo + lon_hi) / 2
            if lon >= mid:
                ch = ch << 1 | 1
                lon_lo = mid
            else:
                ch = ch << 1
                lon_hi = mid
        else:
            mid = (lat_lo + lat_hi) / 2
            if lat >= mid:
                ch = ch << 1 | 1
                lat_lo = mid
            else:
                ch = ch << 1
                lat_hi = mid
        even = not even
        bits += 1
        if bits == 5:
            out += b32[ch]
            bits, ch = 0, 0
    return out


def cmd_fetch(args):
    req = urllib.request.Request(args.url, headers={"User-Agent": UA})
    data = urllib.request.urlopen(req, timeout=30).read()
    import os
    os.makedirs(args.out, exist_ok=True)
    open(f"{args.out}/source.txt", "wb").write(data)
    meta = {
        "url": args.url,
        "sha256": hashlib.sha256(data).hexdigest(),
        "retrievedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    json.dump(meta, open(f"{args.out}/meta.json", "w"), indent=2)
    print(f"fetched {len(data)} bytes -> {args.out}/source.txt")
    print(f"sha256: {meta['sha256']}")
    print(f"retrievedAt: {meta['retrievedAt']}")


def cmd_prompt(args):
    source = open(f"{args.dir}/source.txt", encoding="utf-8").read()
    meta = json.load(open(f"{args.dir}/meta.json"))
    class_file = open(args.class_file, encoding="utf-8").read()
    print(PROMPT.format(class_file=class_file, url=meta["url"], source=source))


def cmd_seal(args):
    meta = json.load(open(f"{args.dir}/meta.json"))
    claims = json.load(open(args.claims))
    if not isinstance(claims, list):
        sys.exit("claims file must be a JSON array of claims")
    claims.sort(key=lambda c: (c["f"], canon(c)))
    report = {"pure": args.pure, "source": meta, "claims": claims}
    data = canon(report).encode("utf-8")
    out = args.out or f"{args.dir}/report.json"
    open(out, "wb").write(data + b"\n")
    print(f"sealed -> {out}")
    print(f"report id: sha256:{hashlib.sha256(data).hexdigest()}")
    print(f"validate:  python3 tools/validate.py {out} --source {args.dir}/source.txt")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("url")
    f.add_argument("--out", required=True)
    p = sub.add_parser("prompt")
    p.add_argument("dir")
    p.add_argument("--class", dest="class_file", required=True)
    s = sub.add_parser("seal")
    s.add_argument("dir")
    s.add_argument("--claims", required=True)
    s.add_argument("--pure", default="v0.1.1")
    s.add_argument("--out")
    g = sub.add_parser("geo")
    g.add_argument("lat", type=float)
    g.add_argument("lon", type=float)
    g.add_argument("precision", nargs="?", type=int, default=6)
    args = ap.parse_args()
    if args.cmd == "fetch":
        cmd_fetch(args)
    elif args.cmd == "prompt":
        cmd_prompt(args)
    elif args.cmd == "seal":
        cmd_seal(args)
    elif args.cmd == "geo":
        print("geo:" + geohash(args.lat, args.lon, args.precision))


if __name__ == "__main__":
    main()
