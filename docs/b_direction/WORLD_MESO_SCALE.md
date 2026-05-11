# WITNESS B-Direction — Meso-Scale Formal Layer

**Date:** 2026-04-25
**Doc reference:** `WITNESS_WORLD_BUILDING_ELEMENTS_AND_SCALE.md` §5.5
**Status:** Map existing CrowdState fields to meso-scale concepts +
implement 1 new field (public_suspicion).

---

## 0. Purpose

Per work directive §5.5, formalize meso-scale (crowd / group / public
mood) as middle layer between individual and macro-world.

**§5.5 candidates** (verbatim from directive):
- public_suspicion
- blame_concentration
- group_cohesion
- local_trust_climate
- crowd_attention_lock

Audit each: does it already exist? If not, design + implement.

---

## 1. Existing → meso-scale concept mapping

### 1.1 `blame_concentration` → blame_concentration

**Status**: ALREADY EXISTS as `CrowdState.blame_concentration[role]`.

Per-target dict tracking blame intensity. Decays at 0.04/tick. Consumed
by Phase 2a forgiveness rumor (target-specific reduction). Drives
`compute_phase` lynch_mode threshold.

**Verdict**: COMPLETE — already a real meso-scale field.

---

### 1.2 `group_cohesion` → alignment_strength

**Status**: ALREADY EXISTS as `CrowdState.alignment_strength`.

Range 0-1. Decays at 0.05/tick (HL ~14 ticks). Self-reinforcing above
0.4 (contagion boost). Drives `compute_phase` (gathered, aligned,
lynch_mode classifications).

Inverse: `fragmentation` field tracks dis-cohesion (defiant_voice
events).

**Verdict**: COMPLETE — alignment_strength + fragmentation cover this
concept.

---

### 1.3 `crowd_attention_lock` → density

**Status**: PARTIAL EXISTS as `CrowdState.density`.

Range 0-1. Decays at 0.015/tick (slow drift). Does NOT have explicit
"lock" semantics — could re-decay even when attention is acute.

**Refinement option**: Add a "density_lock_floor" field that prevents
density from dropping below a threshold while certain events are active
(public_accusation, guard_approaches). Not implemented yet — would be
a new variable.

**Verdict**: PARTIAL — density covers this 80%; "lock" semantics
absent.

---

### 1.4 `local_trust_climate` → (NOT EXISTS)

**Status**: NEW — no existing field.

**Distinct from authority_vigilance**: trust between crowd members vs
between members and authority. Distinct from cohesion (which can be
high but rooted in fear vs trust).

**Design (deferred — would be new variable)**:
- Generation: peer-positive actions (assert_loyalty, public_devotion,
  visible_grief in shared context)
- Decay: 0.01/tick (slow)
- Downstream: feeds remain_present motif inverse-pressure (high trust
  → less perceived threat)

**Verdict**: DESIGN ONLY — not implementing this iteration. Would
deserve a Priority 5 follow-up.

---

### 1.5 `public_suspicion` → (NOT EXISTS — IMPLEMENTING THIS ITER)

**Status**: NEW. Best candidate for minimal addition.

**Distinct from blame_concentration**: blame is target-specific
(`{"disciple_follower": 0.7}`). public_suspicion is general crowd-state
suspicion not yet attached to a specific target.

**Use case**: After guard_approaches event, public is "suspicious"
even before targeting anyone. After a denied accusation, suspicion
lingers. After multiple confessions, suspicion fades.

**Design**:
- Range: 0.0-1.0
- Generation:
  - guard_approaches event: `+0.3` (general public alarm)
  - public_accusation event: `+0.2` (general state of suspicion)
  - active threat rumor presence: `+0.05/tick` if any rumor with
    content_tag in {"threat_to_authority", "misdeed", "accusation"}
- Decay:
  - Auto: 0.02/tick (HL ~35 ticks)
  - Reduced by: shame_repair event (-0.1) + Phase 2a forgiveness
    rumor consumption (-0.03/tick per rumor)
- Downstream:
  - → `social_threat` pressure: `social_threat += public_suspicion * 2`
    in `_compute_agent_pressures`
  - This couples meso-scale state to agent motif activation

**Why this addition is justified during freeze**:
1. Adds 1 variable (not "대량") with clear coupling
2. Provides genuinely new dynamic (general suspicion vs targeted blame)
3. Reuses existing event handlers (guard_approaches, public_accusation,
   shame_repair) — no new event types
4. Couples to existing pressure system (social_threat)
5. Has clear decay → not persistent dead memory

---

## 2. Score on Scale-5 (Meso-scale Reality)

Per WORLD_BUILDING §3.5:
- 0 = no meso, only individuals
- 1 = crowd proxy exists
- 2 = group / crowd node working
- 3 = faction / public_mood / blame_concentration also exist

**Pre-implementation score**: 2 (CrowdState provides density, alignment,
blame_concentration, dominant_emotion — clearly working group/crowd
nodes).

**Post public_suspicion implementation**: 2.5 — moves toward 3 by adding
"public mood" channel distinct from targeted blame. To reach 3 we'd
need at least 1 more (local_trust_climate) + faction-level state.

---

## 3. Implementation plan

### 3.1 Add field

`engine/world/crowd_dynamics/state.py`:
```python
# Iter 90 (post-freeze WORLD_MESO_SCALE addition):
# Public suspicion — general crowd suspicion not target-specific.
# Distinct from blame_concentration (which is per-target).
# Couples to social_threat pressure for all agents at this location.
public_suspicion: float = 0.0  # 0-1, ACTIVE meso-scale memory

# Decay constant
public_suspicion_decay: float = 0.02  # HL ~35 ticks
```

### 3.2 Add decay in step_crowd

```python
state.public_suspicion = max(
    0.0, state.public_suspicion - state.public_suspicion_decay,
)
```

### 3.3 Add generation in inject_crowd_event

```python
# In existing event_type branches, add public_suspicion +=:
elif event_type == "public_accusation":
    # ...existing code...
    state.public_suspicion = min(1.0, state.public_suspicion + 0.2)
elif event_type == "authority_suppression":
    # ...existing code...
    state.public_suspicion = min(1.0, state.public_suspicion + 0.3)
```

### 3.4 Add coupling in _compute_agent_pressures

```python
# In world.py:_compute_agent_pressures, after shame_climate coupling:
pressures["social_threat"] = min(
    10.0,
    pressures["social_threat"] + crowd.public_suspicion * 2,
)
```

### 3.5 Add reduction in shame_repair handler

```python
# In world.py:_apply_seed_event, shame_repair branch:
crowd.public_suspicion = max(
    0.0, crowd.public_suspicion - 0.1,
)
```

### 3.6 Add reduction in Phase 2a (forgiveness consumption)

```python
# In world.py Phase 2a crowd-layer block:
crowd.public_suspicion = max(
    0.0, crowd.public_suspicion - rumor.intensity * 0.03,
)
```

---

## 4. Empirical probe (companion script)

`scripts/b_direction/run_meso_scale_probe.py`:
- Run accusation + (with public_suspicion) vs (without via patch)
- Measure rev/agent + final shame + cycle dynamics
- Verify public_suspicion accumulates and decays as designed
- Verify social_threat pressure responds to public_suspicion

---

## 5. What could still be wrong (H4)

- Adding `public_suspicion` couples to existing `social_threat` pressure
  but social_threat already has multiple sources (alignment_strength,
  density, authority_reach). May be near-saturated; new contribution
  could be invisible.
- Coupling magnitude `public_suspicion * 2` is a guess; needs
  parameter sweep (deferred per freeze rules).
- Decay 0.02/tick is similar to authority_vigilance_decay (which was
  observed to NEVER apply due to Iter 43); need to verify decay
  actually fires in step_crowd.

---

## 6. What I did NOT try (H2)

- 4 other meso-scale candidates (group_cohesion, crowd_attention_lock,
  local_trust_climate, etc.) deferred to design only.
- Faction-level state (would push score to 3).
- Cross-crowd interactions (e.g., suspicion in priest_courtyard
  bleeds to city_street).

---

## 7. Branch implications

- Pro Branch A: 1 new meso channel + 5 documented = readability layer
  has more "world feel"
- Pro Branch C: meso-scale is broader-world prerequisite
- Pro Branch B: even 1 new variable adds complexity if unused; need
  empirical evidence of contribution

The empirical probe (Section 4) decides.

---

**End of Meso-Scale Formal Layer doc. Implementation in companion
edit + probe.**
