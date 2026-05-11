# WITNESS Story Candidates — peter_scarcity_baseline

> *Stage 6 / Stage 7 output*. Each card below is a *creator-facing*
> abstraction over a `StoryThread`, built deterministically (no LLM)
> from source-derived moments, an IdentityResolver, and conflict-typed
> templates.
>
> **What this is**: a set of *story seeds* you can take into film, novel,
> game, or drama work. Each card states what the simulation produced
> — agent identity, pressure pattern, turning points, unresolved
> question — without writing the story itself.
>
> **What this is not**: completed prose, dialogue, screenplay, or any
> emotion-narrated content. See each card's *Risk notes* for explicit
> disclosures.

## Run summary

- candidates total: **4**
- format coverage: film_scene, game_branch, game_quest_branch, novel_chapter, short_story

---

## S01 — Loyalty Strained by Survival Pressure

> **source thread**: `T01` · **conflict**: `loyalty_vs_survival`
> **main**: Peter · **supporting / context**: James, core disciples

### One-line premise

Peter tries to stay present as fear and public pressure slowly turn loyalty into silence.

### Arc summary

fear intensifies → authority pressure closes in → shame relaxes → fear eases → unresolved tension lingers

### Key turning points

| Tick | Label | Provenance | Summary |
|---:|---|---|---|
| 14 | sustained pressure begins | `source_derived` | Peter fear stays above 7.0 for 14 ticks (peak 10.00) |
| 15 | co-occurring pressure | `source_inferred` | agents fear rises while authority_vigilance rises (co-occurrence at t=15) |
| 15 | world pressure shift | `source_derived` | world.authority_vigilance rises (+0.250) |

### Relationship dynamics

- Peter ↔ core disciples: sustained pressure on Peter while group co-presence persists (group context only).
- Peter ↔ James: parallel pressure shifts in authority_vigilance, fear (co-occurring within thread, not a directional relationship signal).

### World pressure context

authority pressure closes in

### Unresolved question

> Will the central agents stay in place or withdraw under pressure?

### Adaptation hooks

- **film_scene**: A quiet scene where Peter stays physically present but emotionally withdraws as authority pressure enters the room.
- **novel_chapter**: A chapter tracking the slow conversion of loyalty into fear-driven silence.
- **game_quest_branch**: The player must choose to confess, hide, or stay silent as public suspicion rises around Peter.

### Evidence

Built from 21 linked moments across 3 pressure type(s) and 4 moment type(s).
- provenance: source_derived=20, source_inferred=1, not_used=0

### Risk notes

- No dialogue generated.
- No unstated event added.
- Premise is inferred from pressure pattern, not directly authored by the engine.


---

## S02 — Uncertainty Lingers Without Commitment

> **source thread**: `T02` · **conflict**: `uncertainty_vs_commitment`
> **main**: Andrew · **supporting / context**: outer crowd B

### One-line premise

Andrew stays near the group but remains uncommitted as pressure rises around them.

### Arc summary

fear intensifies → shame relaxes → fear eases → shame accumulates → unresolved tension lingers

### Key turning points

| Tick | Label | Provenance | Summary |
|---:|---|---|---|
| 15 | sustained pressure begins | `source_derived` | Andrew fear stays above 7.0 for 52 ticks (peak 10.00) |
| 141 | sustained pressure begins | `source_derived` | Andrew fear stays above 7.0 for 60 ticks until end of run (peak 10.00) |

### Relationship dynamics

- Andrew ↔ outer crowd B: sustained pressure on Andrew while group co-presence persists (group context only).

### World pressure context

_(none)_

### Unresolved question

> Is a commitment moment coming, or does drift continue?

### Adaptation hooks

- **short_story**: A piece on a character who stays in the room but never makes the move.
- **game_branch**: A branch where postponed decisions compound into a closed door.

### Evidence

Built from 9 linked moments across 2 pressure type(s) and 2 moment type(s).
- provenance: source_derived=9, source_inferred=0, not_used=0

### Risk notes

- No dialogue generated.
- No unstated event added.
- Premise is inferred from pressure pattern, not directly authored by the engine.


---

## S03 — Uncertainty Lingers Without Commitment

> **source thread**: `T03` · **conflict**: `uncertainty_vs_commitment`
> **main**: James · **supporting / context**: core disciples

### One-line premise

James watches without committing as conditions shift around them.

### Arc summary

fear intensifies → shame accumulates → shame relaxes → fear eases → unresolved tension lingers

### Key turning points

| Tick | Label | Provenance | Summary |
|---:|---|---|---|
| 12 | sustained pressure begins | `source_derived` | James fear stays above 7.0 for 64 ticks (peak 10.00) |
| 141 | sustained pressure begins | `source_derived` | James fear stays above 7.0 for 60 ticks until end of run (peak 10.00) |

### Relationship dynamics

- James ↔ core disciples: sustained pressure on James while group co-presence persists (group context only).

### World pressure context

_(none)_

### Unresolved question

> Is a commitment moment coming, or does drift continue?

### Adaptation hooks

- **short_story**: A piece on a character who stays in the room but never makes the move.
- **game_branch**: A branch where postponed decisions compound into a closed door.

### Evidence

Built from 12 linked moments across 2 pressure type(s) and 2 moment type(s).
- provenance: source_derived=12, source_inferred=0, not_used=0

### Risk notes

- No dialogue generated.
- No unstated event added.
- Premise is inferred from pressure pattern, not directly authored by the engine.


---

## S04 — Uncertainty Lingers Without Commitment

> **source thread**: `T04` · **conflict**: `uncertainty_vs_commitment`
> **main**: John · **supporting / context**: outer crowd B

### One-line premise

John stays under pressure without a commitment moment — drift continues.

### Arc summary

shame accumulates → fear intensifies → shame relaxes → fear eases → unresolved tension lingers

### Key turning points

| Tick | Label | Provenance | Summary |
|---:|---|---|---|
| 15 | sustained pressure begins | `source_derived` | John fear stays above 7.0 for 13 ticks (peak 10.00) |

### Relationship dynamics

- John ↔ outer crowd B: sustained pressure on John while group co-presence persists (group context only).

### World pressure context

_(none)_

### Unresolved question

> Is a commitment moment coming, or does drift continue?

### Adaptation hooks

- **short_story**: A piece on a character who stays in the room but never makes the move.
- **game_branch**: A branch where postponed decisions compound into a closed door.

### Evidence

Built from 16 linked moments across 2 pressure type(s) and 2 moment type(s).
- provenance: source_derived=16, source_inferred=0, not_used=0

### Risk notes

- No dialogue generated.
- No unstated event added.
- Premise is inferred from pressure pattern, not directly authored by the engine.


---

## Cross-reference

- Source threads: [data/narrative/story_threads.json](../../data/narrative/story_threads.json)
- Underlying moments: [data/narrative/moments.json](../../data/narrative/moments.json)
- Plan: [WITNESS_STORY_EMERGENCE_IMPLEMENTATION_PLAN.md](../WITNESS_STORY_EMERGENCE_IMPLEMENTATION_PLAN.md)
- Provenance ledger (per-field): [WITNESS_PROVENANCE_TABLE_PETER_SCARCITY.md](../demo/WITNESS_PROVENANCE_TABLE_PETER_SCARCITY.md)

*Generated by* `scripts/narrative/build_story_candidates.py`.
