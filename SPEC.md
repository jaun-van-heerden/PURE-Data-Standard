# PURE v0.1 — Core Specification

*Status: draft. This page is the entire normative core. Class files add fields; nothing adds concepts.*

## 1. Report

A report is one encoder's reading of one source, as a single JSON document:

```json
{"pure": "<spec-revision>", "source": {"url": "…", "sha256": "…", "retrievedAt": "…"}, "revises": "<report-id>", "claims": []}
```

`pure` pins a git revision (commit or tag) of this spec repo. `source.sha256` is the SHA-256 of the source bytes the encoder read; `retrievedAt` is when they were fetched (ISO-8601 UTC). `revises` is optional and names a report this one corrects.

A report's ID is `sha256:` + the SHA-256 of its canonical bytes (§6). Reports are immutable; nothing is ever edited or deleted.

## 2. Claim

```json
{"f": "field", "v": value, "q": "verbatim quote", "by": "attributor", "t": "instant"}
```

`f`, `v`, `q` are required; `by`, `t` are optional; no other keys. `q` MUST be a verbatim substring of the source bytes — a report is invalid if any `q` is not found. **No quote, no claim.**

`v: null` with `q` means the source addressed the field but stated no value. A field with no claim means the source never addressed it. Encoders never infer, estimate, or fill.

`by` present means the source attributes the value to someone else: a `wd:` ID when resolvable, otherwise the source's attribution phrase verbatim. Absent `by` is the source's own voice. `t` is the instant the value was current, when the source states one.

## 3. Values

One of: string · integer · `{"min"?, "max"?}` (integers, non-empty) · ISO-8601 date/time (UTC) · ID (`wd:` Wikidata, `gn:` GeoNames, `geo:` geohash, or an event-class path) · `null`. Units are fixed per field by the class file. Numbers only when the source states numbers.

## 4. Reserved fields

Required in every report: `what` (an event class = a path in this repo), `when`, `where`. `where` is the event's locus: a `geo:`/`gn:` ID for physical events when resolvable, otherwise the source's place phrase verbatim; non-physical classes name their locus field in the class file.

Reserved, optional: `via` (URL or name of a work this source derives from — quoted like any claim) and `said` (attributed statement; `by` required).

## 5. Event key

Derived, never stored: `what | utcDay(when) | cell(where)`, where `cell` is the first 4 geohash characters for `geo:` loci and the verbatim value otherwise. Reports sharing a key describe the same event. Fuzzier matching is a query-time concern, not protocol.

## 6. Canonical form

RFC 8785 (JCS), UTF-8, NFC strings. Claims are sorted by `f` (Unicode code point order), ties broken by the claim's full canonical bytes. A report file stores exactly its canonical bytes (a single trailing newline is permitted).

## 7. The spec repo

The standard is one git repo. Each path under `classes/` is an event class; each class is one markdown file containing a normative field table (name, type, value rule), non-normative extraction questions, and fixtures (source → expected claims). A field enters the table only when independent encoders demonstrably agree on it across the fixtures; anything unproven uses an `ext:` prefix. Reports pin a revision of this repo; forks inherit full history and old reports validate forever.

## 8. Conformance

An encoder is conformant at a revision iff it reproduces every fixture's claims exactly. `tools/validate.py` checks reports against §1–§6 and a class file.

## 9. Corroboration

Support for a value is the number of distinct roots after collapsing `via` edges and overlapping-quote fingerprints — fifty republications of one wire story are one root. Root counts are **provenance breadth, not truth**: they are not sybil-resistant, MUST always decompose into their inspectable source list, and MUST NOT be rendered as a trust score.

## 10. Neutrality

PURE records who claimed what, on which evidence. It never states what is true. Conflicting reports coexist; readers compute their own consensus.
