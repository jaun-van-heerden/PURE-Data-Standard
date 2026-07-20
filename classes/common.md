# common — fields shared by all classes

Fields whose meaning is class-independent live here instead of a class table, under the same ratchet as everything else (GOVERNANCE.md). Validate reports against both files:

```
python3 tools/validate.py REPORT.json --source SOURCE --class classes/common.md --class classes/<class>.md
```

## Fields (normative)

| field | type | rule |
|---|---|---|
| `location.name` | string | The source's stated place phrase, verbatim. No normalization, no gazetteer lookup. |
| `location.lat` | number | Stated latitude, decimal degrees (WGS84), full stated precision. Only when the source states coordinates — never derived from a name. |
| `location.lon` | number | Stated longitude, same rule as `location.lat`. |

**Agreement:** not yet measured — provisional, like everything pre-CI. First observed in `fixtures/disaster.tornado/nws-effingham/`.

## Reserved facet names (guidance)

Sources state place in many shapes — coordinates, a venue, an address, an administrative area. When a source states one of these, use **these names under `ext:`** (e.g. `ext:location.venue`), so encoders converge instead of inventing dialects. Each is one claim, with its own quote; each drops the `ext:` prefix and enters the table above once real reports use it and agreement is measured (GOVERNANCE.md — evidence precedes normativity):

| name | meaning |
|---|---|
| `location.venue` | Named facility where the event occurred ("Westfield Shopping Centre", "Alton Towers"), verbatim. |
| `location.venue_type` | Kind of facility, as stated ("shopping centre", "theme park"). Free string until usage justifies an enum; OSM's tag vocabulary is the likely enum source when it does. |
| `location.address` | Stated street address, verbatim. |
| `location.locality` | Stated city / town / suburb. |
| `location.region` | Stated state / province / county. |
| `location.country` | Stated country — ISO 3166-1 alpha-2 when resolvable, else verbatim. |
| `location.postcode` | Stated postal code. |

## The pattern

`where` (SPEC §4) is always **one value** — the locus ID that feeds the event key. Everything else about place is a `location.*` claim: one facet per claim, each independently comparable across outlets, each carrying its own quote. `tools/show.py` folds them into a single `location` object in the event-shaped view.

For venue-centric events, prefer a `geo:` locus when the venue resolves to a point (spatial keys join across encoders who know the place by different names); the venue's *name* is a `location.venue` claim either way. Never manufacture facets the source didn't state — a stated venue does not imply an address, coordinates, or a postcode.
