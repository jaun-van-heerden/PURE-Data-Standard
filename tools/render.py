#!/usr/bin/env python3
"""PURE v0.1 renderer — turn a report back into neutral prose, via any LLM.

Usage:
    python3 tools/render.py REPORT.json [--lang LANGUAGE]

Prints a self-contained, model-agnostic prompt to stdout. Paste it into
any LLM (or pipe it to a CLI). The repo stays dependency-free and the
protocol stays model-agnostic: the prompt is the tool.

Round-trip note: a conformant rendering must re-extract to the same
claims (SPEC.md §8 measures this on fixtures, per claim).
"""
import argparse
import hashlib
import json
import sys

PROMPT = """You are rendering a PURE data report into a short, neutral news brief{lang}.

Rules — follow all of them:
1. State ONLY what the claims below say. Every sentence must trace to a claim; add no facts, context, or speculation of your own.
2. A claim with "v": null means the source raised that topic WITHOUT stating a value — say exactly that (e.g. "the report referred to deaths without giving a figure"). Never invent a number.
3. A claim with "by" is attributed: name the attributor in the sentence ("according to …", "… said"). A "said" claim is a statement someone made — report that they said it; do not assert its content as fact.
4. Include "t" (as-of) times where present; note the retrieval time if it matters for currency.
5. A "via" claim means this source derives from another work — say so.
6. No adjectives, framing, or emotion beyond the data. Plain declarative sentences. 60–150 words.
7. End with exactly this line:
   Source: {url} (retrieved {retrieved}) · PURE report {rid}

THE REPORT:
{report}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("report")
    ap.add_argument("--lang", help="target language, e.g. 'Afrikaans' (default: English)")
    args = ap.parse_args()

    raw = open(args.report, "rb").read()
    report = json.loads(raw)
    canonical = json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    rid = "sha256:" + hashlib.sha256(canonical).hexdigest()

    print(PROMPT.format(
        lang=f", written in {args.lang}" if args.lang else "",
        url=report["source"]["url"],
        retrieved=report["source"]["retrievedAt"],
        rid=rid,
        report=json.dumps(report, indent=2, ensure_ascii=False),
    ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
