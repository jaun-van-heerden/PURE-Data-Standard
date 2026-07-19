# disaster.tornado

**Parent:** `disaster` · **Since:** v0.1
A tornado touching down, and its immediate human and property impact.

## Fields (normative)

Field names are dotted paths — the event's hierarchy lives in the names (`tools/show.py` folds them into the tree).

| field | type | rule |
|---|---|---|
| `casualties.deaths` | count | People the source states were killed. Numbers only when stated: "at least 12 dead" → `{"min":12}`. "Death toll rising" states no number → `null` with the quote. Never mentioned → no claim. |
| `casualties.injuries` | count | People the source states were injured. Same rule as `casualties.deaths`. |
| `damage.homes_destroyed` | count | Homes the source states were destroyed. Same rule — "homes were torn apart" states no number → `null`. Plural wording is not a number; do not infer `{"min":2}`. Only an event-total counts: per-location counts inside a survey narrative ("destruction of two single-family homes" at one intersection) are not totals — do not sum them; if no total is stated, make no claim. |
| `ef_rating` | enum(EF0\|EF1\|EF2\|EF3\|EF4\|EF5) | Only when the source states an official Enhanced Fujita rating. A reporter's "powerful" or "monster" is not a rating. |
| `rescue_ongoing` | bool | `true` only when the source describes rescue operations actively underway as of writing; `false` only when it states operations have ended. |

Types: `count` = non-negative integer, `{"min"?,"max"?}`, or `null` · `bool` = `true`/`false` · `enum(…)` = exactly one listed token.

**Agreement:** not yet measured — scores land with the first CI encoder pool. Until then every field above is provisional.

## Questions (non-normative extraction guidance)

Ask each question against the source. Every answer must be backed by a verbatim quote from the source; **no quote, no claim.**

- **casualties.deaths** — How many people does the source state were killed? Answer with the stated number; if the source raises deaths without giving a number, answer `null` and quote the sentence; if deaths are never mentioned, make no claim.
- **casualties.injuries** — How many people does the source state were injured? Same procedure.
- **damage.homes_destroyed** — How many homes does the source state were destroyed? Same procedure.
- **ef_rating** — Does the source state an official EF rating for this tornado? Only quote an explicit rating.
- **rescue_ongoing** — Does the source describe rescue operations underway right now? Quote the sentence that says so.

## `where` locus

This is a physical event: `where` is the touchdown locality — a `geo:` or `gn:` ID when the place resolves, otherwise the source's place phrase verbatim.

## Observed `ext:` fields (candidates for promotion)

Fields real sources kept stating that the table above doesn't cover. Per SPEC §7 they stay `ext:` until independent encoders demonstrably agree on them. Policy: `ext:` fields carry the **source's unit in the field name** (no conversion at encode time — conversion is inference); promotion into the normative table is where an SI unit gets fixed.

| field | first seen | meaning |
|---|---|---|
| `ext:peak_wind_mph` | nws-effingham | estimated peak wind as stated |
| `ext:path.length_mi` | nws-effingham | path length as stated |
| `ext:path.width_max_yd` | nws-effingham | maximum path width as stated |
| `ext:path.end_time` | nws-effingham | event end instant, event-local offset |
| `ext:path.end_geo` | nws-effingham | lift point as a `geo:` geohash |
| `ext:location.name` | nws-effingham | stated place name, verbatim |
| `ext:location.lat` | nws-effingham | stated latitude, full precision |
| `ext:location.lon` | nws-effingham | stated longitude, full precision |

Place richness follows the same pattern as everything else: `where` stays a single locus ID (it feeds the event key), and stated place facets — name, exact coordinates — are sibling `location.*` claims, each with its own quote. Three precision tiers, each fit for purpose: the key cell joins (~geohash-4), the `where` ID locates (geohash-6), `location.lat/lon` measure (as stated).

## Fixtures

| fixture | notes |
|---|---|
| [`fixtures/disaster.tornado/coastal-herald/`](../../fixtures/disaster.tornado/coastal-herald/) | Sensationalized report that raises deaths and home damage without stating numbers (→ `null` claims), describes an active rescue, and carries one attributed expert forecast. The apocalyptic framing encodes to nothing. |
| [`fixtures/disaster.tornado/regionx-courier/`](../../fixtures/disaster.tornado/regionx-courier/) | Sober day-after report on the same event (same derived event key): quantified casualties and damage with attribution (`by`) and as-of times (`t`), an official EF rating, rescue concluded. Pairs with `coastal-herald` for the `tools/diff.py` demo. |
| [`fixtures/disaster.tornado/countryy-mirror/`](../../fixtures/disaster.tornado/countryy-mirror/) | Republication that credits the Courier — a `via` claim, quoted like any other. All three fixtures together drive the `tools/roots.py` demo: 3 reports, 2 independent roots; every number traces to one root. |
| [`fixtures/disaster.tornado/nws-effingham/`](../../fixtures/disaster.tornado/nws-effingham/) | **First real source**: the NWS Lincoln IL damage survey (public domain) for the June 17, 2026 Effingham EF3. First-hand basis, stated zero (`casualties.deaths: 0` is a claim), five `ext:` fields, event-local date in the key (`2026-06-17`, though 7:56 PM CDT is June 18 UTC). Encoded via `tools/ingest.py`. |
