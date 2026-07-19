# PURE Data Standard

**News you can view-source.**

PURE inverts how news is stored. Today the article is the source of truth and data is scraped from it, lossily. Under PURE, the structured record is the canonical artifact — hashed, immutable, comparable worldwide — and any article is just one possible rendering of it (in any language, at any reading level, by any LLM). Anyone can encode anyone's article; no publisher cooperation is required. And PURE never says what is true: it records **who claimed what, backed by which exact words**, and lets readers count independent sources themselves.

The entire normative core is one page: **[SPEC.md](SPEC.md)**.

## The example

A sensationalized report:

> **Apocalyptic Tornado Strikes Coastal City - Death Toll Rising!**
>
> In a cataclysmic event of unprecedented proportions, a monstrous tornado ripped through the coastal city, leaving a path of destruction in its wake. Scenes of chaos and devastation unfolded as homes were torn apart, cars tossed like toys, and lives shattered in an instant. Rescue teams battled against the odds to save survivors trapped beneath the rubble, while the death toll continued to climb by the hour. Experts warn that this could be just the beginning of a new era of extreme weather events brought on by climate change, leaving residents in fear and uncertainty about what the future may hold.

compiles to this PURE report (pretty-printed here; the stored form is canonical single-line JSON — see the [fixture](fixtures/disaster.tornado/coastal-herald/expected.json)):

```json
{
  "pure": "v0.1",
  "source": {
    "url": "https://coastal-herald.example/apocalyptic-tornado",
    "sha256": "542e980bcc8b59e4b6fd43ad48811caa2f43117812e579b55d182ae0bcda538d",
    "retrievedAt": "2024-02-18T22:14:03Z"
  },
  "claims": [
    {"f": "deaths", "v": null, "q": "the death toll continued to climb by the hour"},
    {"f": "homes_destroyed", "v": null, "q": "homes were torn apart"},
    {"f": "rescue_ongoing", "v": true, "q": "Rescue teams battled against the odds to save survivors trapped beneath the rubble"},
    {"f": "said", "by": "Experts",
     "v": "this could be just the beginning of a new era of extreme weather events brought on by climate change",
     "q": "Experts warn that this could be just the beginning of a new era of extreme weather events brought on by climate change"},
    {"f": "what", "v": "disaster.tornado", "q": "a monstrous tornado ripped through the coastal city"},
    {"f": "when", "v": "2024-02-18", "q": "Date: February 18, 2024"},
    {"f": "where", "v": "Coastal City, Region X, Country Y", "q": "Coastal City, Region X, Country Y"}
  ]
}
```

Report ID: `sha256:e377f20b…` · Event key: `disaster.tornado|2024-02-18|Coastal City, Region X, Country Y`

Read what the encoding *says*:

- **Every claim carries `q` — the exact quote that backs it.** No quote, no claim. A claim whose quote is not a verbatim substring of the source is invalid, mechanically.
- **`v: null` is information.** The article *raised* deaths and home damage but stated no numbers — "the death toll continued to climb" is not a count. The apocalyptic headline compiles into its own indictment.
- **Subjectivity survives as attribution.** "Experts warn…" is kept — as the objective fact that experts said it (`said` + `by`), not as a fact about the weather.
- **Sensationalism compiles to nothing.** "Cataclysmic proportions," "cars tossed like toys," "lives shattered" — there is no field to claim, so the framing is discarded by construction, not by editorial judgment.

> **A confession that doubles as the pitch:** an earlier version of this README encoded this same article as `"fatalities": 2, "injuries": "10+"` — numbers that appear nowhere in the prose. Even the standard's own authors hallucinated when values didn't require quotes. Under v0.1 that encoding is not merely discouraged; it is **impossible to validate**.

## How it works — the whole model in eight concepts

1. **Claim** — `{f, v, q, by?, t?}`: field, value, verbatim quote, optional attributor, optional as-of instant. The only primitive.
2. **Report** — a sealed, immutable bag of claims about one source. Its ID is the hash of its canonical bytes.
3. **Values** — string, integer, `{min?,max?}`, ISO date, ID (`wd:`/`gn:`/`geo:`), or `null`. Numbers only when the source states numbers.
4. **Reserved fields** — `what`, `when`, `where` (required); `via` (declared derivation); `said` (attributed statements).
5. **Event key** — derived, never stored: `what | day | cell(where)`. Independent encoders converge on the same join key with zero coordination, so everyone's reports on the same event line up.
6. **Canonical form** — RFC 8785; sorted claims. Convergence is measured per *claim*, not per report.
7. **Class files** — one markdown file per event type ([`classes/disaster/tornado.md`](classes/disaster/tornado.md)) is simultaneously the taxonomy node (its path), the schema (its field table), the extraction guidance (its questions), and the test suite (its fixtures). A field enters the standard only when independent encoders demonstrably agree on it. Unproven fields use `ext:`.
8. **Corroboration** — count evidence *roots*, not reports: fifty outlets republishing one wire story are one root.

## Try it

```
$ python3 tools/validate.py fixtures/disaster.tornado/coastal-herald/expected.json \
    --source fixtures/disaster.tornado/coastal-herald/source.txt \
    --class  classes/disaster/tornado.md
VALID: fixtures/disaster.tornado/coastal-herald/expected.json
  report id: sha256:e377f20bd1d25e82c9e36ddf991be15ff4ee62406c3711716d663dcba6818014
  event key: disaster.tornado|2024-02-18|Coastal City, Region X, Country Y
```

The validator is a single dependency-free file. It rejects fabricated quotes, hallucinated values, enum violations, unsorted claims, and non-canonical bytes.

## Compare two outlets — the point of all of this

A second fixture encodes a sober day-after report on the same tornado from a different outlet. The two encoders never coordinated, yet both reports derive the **same event key**, so they join automatically:

```
$ python3 tools/diff.py fixtures/disaster.tornado/coastal-herald/expected.json \
                        fixtures/disaster.tornado/regionx-courier/expected.json

A: https://coastal-herald.example/apocalyptic-tornado  (retrieved 2024-02-18T22:14:03Z)
B: https://regionx-courier.example/tornado-damage-assessment  (retrieved 2024-02-19T10:30:00Z)
event key: disaster.tornado|2024-02-18|Coastal City, Region X, Country Y  — same event

field            A                                    B                                              verdict
---------------  -----------------------------------  ---------------------------------------------  ------------
deaths           null                                 2 · by the county sheriff · as of 2024-02-19   B quantifies
ef_rating        —                                    "EF3" · by The National Weather Bureau         B only
homes_destroyed  null                                 37 · by The emergency office                   B quantifies
injuries         —                                    {"min":14} · by the county sheriff · as of…    B only
rescue_ongoing   true                                 false · by The emergency office · as of 2024…  DIFFER
said             "this could be just the beginning…"  —                                              A only
what             "disaster.tornado"                   "disaster.tornado"                             agree
when             "2024-02-18"                         "2024-02-18"                                   agree
where            "Coastal City, Region X, Country Y"  "Coastal City, Region X, Country Y"            agree

evidence roots: 2 — neither report declares derivation (via).
Root counts are provenance breadth, not truth (SPEC.md §9).
```

Read the table:

- **`B quantifies` is not a contradiction.** Outlet A raised the death toll without a number (`null` + quote); outlet B states `2`, attributed to the county sheriff. And note the full circle: the "2" this repo's old README *hallucinated* now enters legitimately — stated by a source, carried with its attribution.
- **`DIFFER` on `rescue_ongoing` is time, not conflict.** A (Sunday 22:14) describes an active rescue; B reports it concluded Sunday evening. Twelve hours passed between retrievals — this is exactly why claims carry `t` and reports carry `retrievedAt`, and why the death-toll-over-time query works.
- **Two evidence roots.** Neither report derives from the other, so corroboration counts 2. Had B carried `via: coastal-herald…`, it would count 1.

## Count independent roots — the anti-bandwagon query

A third fixture is a republication: the Country Y Daily Mirror repeats the Courier's numbers and credits it — which becomes a `via` claim, quoted like any other ("according to a report by the Region X Courier"). Run corroboration across all three:

```
$ python3 tools/roots.py fixtures/disaster.tornado/*/expected.json

3 reports · event key: disaster.tornado|2024-02-18|Coastal City, Region X, Country Y

report                                              root
--------------------------------------------------------
coastal-herald.example/apocalyptic-tornado          (self) — independent root
countryy-mirror.example/coastal-city-tornado-kill…  via → regionx-courier.example/tornado-damage-assessment
regionx-courier.example/tornado-damage-assessment   (self) — independent root

distinct roots: 2

value support (independent roots, not reports):
  deaths=2              1 root  (2 reports)
  deaths=null           1 root
  ef_rating="EF3"       1 root  (2 reports)
  homes_destroyed=37    1 root  (2 reports)
  ...
```

This is the whole anti-bandwagon idea in one line: **`deaths=2` appears in two reports but has one root.** Every published death toll traces back through the Courier to a single attributed statement by the county sheriff. Fifty more republications would still be one root. (And the honest caveat, always: roots measure provenance breadth, not truth — a motivated adversary can fabricate roots; see SPEC.md §9.)

## Render it back

The loop closes with any LLM:

```
$ python3 tools/render.py fixtures/disaster.tornado/coastal-herald/expected.json --lang Afrikaans
```

This prints a self-contained, model-agnostic prompt: render only the claims, say "raised without a figure" for `null` values, attribute everything carrying `by`, no adjectives beyond the data, and end with the source URL and report ID — the `view-source` line of the rendered article. Because the data is language-neutral, the same report renders to calm prose in any language at any reading level.

## First real encoding

The fourth fixture is not fiction: it is the National Weather Service damage survey (public domain) for the **June 17, 2026 Effingham, Illinois EF3 tornado**, fetched from a stable archive URL and encoded through the class file's questions:

```
$ python3 tools/ingest.py fetch <archive-url> --out fixtures/disaster.tornado/nws-effingham
$ python3 tools/ingest.py prompt fixtures/disaster.tornado/nws-effingham \
    --class classes/disaster/tornado.md          # paste into any LLM, or answer by hand
$ python3 tools/ingest.py seal fixtures/disaster.tornado/nws-effingham --claims claims.json
$ python3 tools/validate.py fixtures/disaster.tornado/nws-effingham/expected.json \
    --source fixtures/disaster.tornado/nws-effingham/source.txt --class classes/disaster/tornado.md
VALID — event key: disaster.tornado|2026-06-17|dnby
```

Every quote in the report was extracted programmatically from the fetched bytes, and `deaths: 0` is a *claim* (the survey states zero) — meaningfully different from the fictional Herald's `null` (raised, unquantified) and from silence.

Reality immediately forced the spec to evolve — which is the design working, not failing:

- **Decimal numbers** (v0.1 allowed only integers; the survey's path length is `31.83` miles) — SPEC §3 amended.
- **Event-local dates in the key** (the tornado began 7:56 PM CDT — already June 18 in UTC; keying on UTC would split this event from every source that calls it "the June 17 tornado") — SPEC §5 amended.
- **Units stay in `ext:` field names** (`ext:peak_wind_mph`) — conversion is inference; SI units get fixed at promotion time.
- **Per-location counts are not totals** (the narrative destroys "two single-family homes" at one intersection — that is not `homes_destroyed` for the event) — class-file rule sharpened.

## Repository layout

```
SPEC.md                      the one-page normative core
classes/<parent>/<class>.md  one file per event class: fields + questions + fixtures
fixtures/<class>/<name>/     source.txt + expected.json (canonical bytes)
tools/validate.py            reference validator
tools/diff.py                field-by-field comparison of two reports
tools/roots.py               corroboration: collapse via chains, count roots
tools/render.py              report → neutral prose, via any LLM
tools/ingest.py              fetch source → extraction prompt → seal report
```

## Contributing a field

Open a PR that edits one class file: add the field row (name, type, value rule), its extraction question, and at least one fixture demonstrating it. The merge criterion is demonstrated inter-encoder agreement on the fixtures — measured, not voted. Until CI lands, agreement is checked manually by re-encoding fixtures with independent models.

## Honest limits

Root counting defeats bandwagons (declared syndication, verbatim copying). It does **not** defeat a motivated adversary: LLM paraphrase makes thirty "independent" tellings of one fabrication cheap and textually undetectable, and honest outlets stripping citations inflate root counts without malice. Root counts are provenance breadth, not truth — they always decompose into an inspectable source list and are never a trust score. Real sybil resistance requires the identity layer below.

## Roadmap

- **v0.1** — claim/report core, first class file, fixtures, validator.
- **v0.1.1 (this)** — first real encoding (NWS Effingham EF3) + `tools/ingest.py`; spec amendments it forced: decimal numbers, event-local dates in keys.
- **v0.2** — encoder identity: signed reports, keys, reputation; CI that measures per-field agreement and publishes scores in class files.
- **v0.3** — transparency log (Certificate-Transparency-style) for publish timestamps; fetch-archive convention so quotes stay verifiable as sources rot.

**Rejected by design:** blockchain, tokens, committees, and any mechanism by which the protocol itself would adjudicate truth.
