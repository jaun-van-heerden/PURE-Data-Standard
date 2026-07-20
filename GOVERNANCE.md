# How the Spec Evolves

**The philosophy in one sentence: the spec is a record of demonstrated agreement — never a plan for it.**

PURE grows the way a dictionary grows: by recording usage that already exists and has proven convergent. It never grows the way committee standards grow — by imagining what someone might someday need. A dictionary with speculative words is wrong; a spec with speculative fields is wrong in exactly the same way.

## Three layers, three speeds

**1. The core (SPEC.md) — constitutional, nearly frozen.**
The claim shape, report shape, values, canonical form, reserved fields, event key, corroboration rule, neutrality. The core changes only when reality produces a **counterexample** — a real source that *cannot be encoded* under current rules — never because someone has a better idea. (Both v0.1.1 amendments were counterexamples: a stated `31.83 miles` that couldn't be a value; a stated `7:56 PM CDT` that broke the event key. Neither was an improvement; both were impossibilities.) Every core change must keep every previously sealed report valid at its pinned revision, and the concept count may never rise — a new concept must delete at least one.

**2. The vocabulary (class files) — earned, continuously.**
Fields and classes enter the normative tables exclusively through the ratchet below. Nothing enters by argument, foresight, seniority, or authority — including the maintainer's.

**3. The guidance (questions, prompts, tools) — free.**
Non-normative material changes freely, with one boundary: a guidance change that alters fixture outputs was actually a vocabulary change, and follows the ratchet.

## The ratchet — the only path to normative

```
wild (ext:, anyone, anytime)  →  observed (recorded in the class file)  →  normative (field table)
```

- **Anyone may use any `ext:` field at any time. No permission.** This is the pressure valve that prevents a million directions: every experiment, niche need, and disagreement has a sanctioned home *inside* the standard, so divergence happens harmlessly at the edge instead of contentiously at the center.
- A field becomes **observed** when real, independent reports keep using it. Observation is recorded, not judged.
- A field becomes **normative** when a PR carries fixtures and measured inter-encoder agreement clears the bar. At promotion, its name, type, unit, and rule **freeze forever**.

The ratchet is one-way for meaning: a normative field is never renamed, never repurposed, never redefined. If its meaning turns out wrong, it is deprecated (old data stays valid forever) and a replacement earns its own way in. A field whose agreement collapses on new fixtures is flagged and deprecated the same way — the table must keep earning itself.

**Classes follow the same ratchet.** A new class file requires real fixtures from independent sources, and must show that existing classes plus `ext:` *cannot* encode its events — if they can, the answer is promoting `ext:` fields, not a new class. Class paths, like field names, never move once normative. Fields whose meaning is class-independent (e.g. `location.*`) live in `classes/common.md` under the same ratchet — being common is a property a field demonstrates, not a bucket to design into.

## Disputes are settled by encoding, not debating

When contributors disagree about a rule, a field, or a boundary, the resolution is mechanical: each side contributes fixtures, encoders run, agreement is measured. Whatever converges wins; if neither converges, neither enters. **Arguments without fixtures are conversation, not contribution.** The maintainer's job is to run the measurement and enforce this document — they hold a veto over core amendments and no power at all over vocabulary.

## The single fitness function

Every change answers one question: **will two strangers encoding the same article agree more often after this change?** More expressive but less convergent is rejected, no matter how useful. Simplicity is not a style preference here; it is what convergence physically requires.

## Releases

The repo may churn daily; **meaning changes only at tags.** Reports pin tags; tags are immutable; nothing between tags is normative. Every release note lists: fields promoted (with their agreement scores), fields deprecated, core counterexamples if any (rare), and what was deleted.

## What never changes

- Anyone can encode anyone's article — no permission, no publisher cooperation.
- The protocol never adjudicates truth.
- Sealed reports validate forever at their pinned revision.
- The core spec fits on one page.
- Boring tech only (JSON, git, hashes) — nothing a solo developer can't carry.

## The failure modes, and the lock on each

| Spiral | Lock |
|---|---|
| Design by taste / committee bloat | Measurement is the only authority |
| Speculative fields ("we might need…") | Evidence precedes normativity — no fixtures, no field |
| Core creep | Counterexample-only amendments; concept count may not rise |
| Meaning drift | Semantics freeze at promotion; deprecate, never repurpose |
| Breaking old data | Revision pinning; forward-only change |
| Dialect wars | `ext:` is the sanctioned dialect space; the ratchet is the only merge path |
| Class proliferation | New class must prove existing classes + `ext:` cannot encode it |
| Scope absorbed out of fear of forks | Forks are survivable by design (flat claims, pinned revisions), so "no" stays cheap |
| Model-era rot | Prompts are guidance; only declarations and fixtures are normative |
