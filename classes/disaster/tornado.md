# disaster.tornado

**Parent:** `disaster` · **Since:** v0.1
A tornado touching down, and its immediate human and property impact.

## Fields (normative)

| field | type | rule |
|---|---|---|
| `deaths` | count | People the source states were killed. Numbers only when stated: "at least 12 dead" → `{"min":12}`. "Death toll rising" states no number → `null` with the quote. Never mentioned → no claim. |
| `injuries` | count | People the source states were injured. Same rule as `deaths`. |
| `homes_destroyed` | count | Homes the source states were destroyed. Same rule — "homes were torn apart" states no number → `null`. Plural wording is not a number; do not infer `{"min":2}`. |
| `ef_rating` | enum(EF0\|EF1\|EF2\|EF3\|EF4\|EF5) | Only when the source states an official Enhanced Fujita rating. A reporter's "powerful" or "monster" is not a rating. |
| `rescue_ongoing` | bool | `true` only when the source describes rescue operations actively underway as of writing; `false` only when it states operations have ended. |

Types: `count` = non-negative integer, `{"min"?,"max"?}`, or `null` · `bool` = `true`/`false` · `enum(…)` = exactly one listed token.

**Agreement:** not yet measured — scores land with the first CI encoder pool. Until then every field above is provisional.

## Questions (non-normative extraction guidance)

Ask each question against the source. Every answer must be backed by a verbatim quote from the source; **no quote, no claim.**

- **deaths** — How many people does the source state were killed? Answer with the stated number; if the source raises deaths without giving a number, answer `null` and quote the sentence; if deaths are never mentioned, make no claim.
- **injuries** — How many people does the source state were injured? Same procedure.
- **homes_destroyed** — How many homes does the source state were destroyed? Same procedure.
- **ef_rating** — Does the source state an official EF rating for this tornado? Only quote an explicit rating.
- **rescue_ongoing** — Does the source describe rescue operations underway right now? Quote the sentence that says so.

## `where` locus

This is a physical event: `where` is the touchdown locality — a `geo:` or `gn:` ID when the place resolves, otherwise the source's place phrase verbatim.

## Fixtures

| fixture | notes |
|---|---|
| [`fixtures/disaster.tornado/coastal-herald/`](../../fixtures/disaster.tornado/coastal-herald/) | Sensationalized report that raises deaths and home damage without stating numbers (→ `null` claims), describes an active rescue, and carries one attributed expert forecast. The apocalyptic framing encodes to nothing. |
| [`fixtures/disaster.tornado/regionx-courier/`](../../fixtures/disaster.tornado/regionx-courier/) | Sober day-after report on the same event (same derived event key): quantified casualties and damage with attribution (`by`) and as-of times (`t`), an official EF rating, rescue concluded. Pairs with `coastal-herald` for the `tools/diff.py` demo. |
