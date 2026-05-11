# WITNESS B-Direction — World Memory Layer Formalization

**Date:** 2026-04-25
**Doc reference:** `WITNESS_WORLD_BUILDING_ELEMENTS_AND_SCALE.md` §5 priority 4
**Status:** Formal documentation of existing memory channels + design
spec for proposed new channels. **No new variables added** (per freeze
discipline §6).

---

## 0. Purpose

Per work directive §5.4, formalize:
- **Generation conditions**: when does this memory increase?
- **Maintenance / decay**: how does it persist or fade?
- **Downstream effects**: action space, pressure, event spawn

For each existing channel, plus design spec for proposed new ones.

---

## 1. Existing memory channels — operational specification

### 1.1 `shame_climate` (CrowdState.shame_climate)

**Class**: ACTIVE memory (all 3 functions wired).

**Generation**:
- `inject_crowd_event(crowd, "public_accusation", intensity)`:
  `shame_climate += intensity * 0.4`, capped at 1.0
  (engine/world/crowd_dynamics/state.py:198-201)
- Other events may indirectly contribute via inject helpers

**Maintenance**:
- **No auto-decay** (Iter 43 removed). Persists indefinitely unless
  reduced by Phase 2a forgiveness rumor.

**Decay (consumption)**:
- Phase 2a forgiveness rumor (engine/world/micro_world/world.py:211-213):
  `crowd.shame_climate -= rumor.intensity * 0.1` per active forgiveness
  rumor per tick.
- shame_repair seed event:
  `crowd.shame_climate -= intensity * 0.5`
  (world.py:836-838)

**Downstream effects**:
- → `shame_exposure pressure` for agents at same location, scaled by
  `role.climate_sensitivity` (world.py:441-445)
- shame_exposure pressure feeds `_conceal` and `_remain_present` motifs
- Indirectly affects all motif top-2 ranking competition

**Scale-1 contribution**: HIGH — shame_climate is the primary world-memory
channel feeding agent dynamics.

---

### 1.2 `authority_vigilance` (CrowdState.authority_vigilance)

**Class**: DEAD memory (generated + persists, but NO downstream coupling
since Iter 38).

**Generation**:
- `inject_crowd_event(crowd, "authority_suppression", intensity)`:
  `authority_vigilance += intensity * 0.5`, capped at 1.0
  (state.py:212-214)
- Triggered by `guard_approaches` event handler in MicroWorld

**Maintenance**:
- `authority_vigilance_decay = 0.02` constant **defined but not applied**
  (Iter 43 removed memory field decay from step_crowd; see state.py:136-139
  comment). So in current code, authority_vigilance NEVER decays.

**Decay (consumption)**:
- None.

**Downstream effects**:
- **None**. Iter 38 ablated authority_vigilance pressure coupling
  (world.py:446 comment). No motif or pressure reads it.
- Logged in step.crowd_state_snapshot (world.py:294) for trajectory.

**Verdict**: This is a **PERSISTENT INERT memory channel** —
empirically observable in trajectory logs but mechanistically inert.

**Recommended action**: Either:
- (a) RE-WIRE coupling: `physical_threat += authority_vigilance * 2`
  (would restore the original Iter 4 design intent)
- (b) FORMALLY ANNOTATE as logging-only (RESERVE), like the slow_state
  fields per Iter 89 audit

Currently (a) and (b) are both unannotated — recommendation: pick one
during branch decision phase.

---

### 1.3 `blame_concentration` (CrowdState.blame_concentration[role])

**Class**: ACTIVE memory (all 3 functions wired).

**Generation**:
- `inject_crowd_event(crowd, "public_accusation", intensity)` increases
  `blame_concentration[target_role]` (state.py inject_crowd_event)
- Various deny/conceal actions may trigger blame injection in handlers

**Maintenance**:
- **Auto-decay**: `blame_decay = 0.04` per tick per target. Targets dropped
  when value ≤ 0.01 (state.py:120-126).

**Decay (consumption)**:
- Phase 2a forgiveness rumor (world.py:174-180):
  `crowd.blame_concentration[rumor.target_role] -= rumor.intensity * 0.5`
  per active forgiveness rumor per tick. Removed when below 0.01.

**Downstream effects**:
- Used in `compute_phase` to determine lynch_mode threshold
  (state.py:88-90: `max_blame >= TIPPING_BLAME` + lynch emotion = lynch_mode)
- Affects information_topology / rumor propagation indirectly
- Visible in step.crowd_state_snapshot

**Scale-1 contribution**: MEDIUM — blame_concentration drives crowd phase
transitions but doesn't directly feed agent pressure (in current wiring).

---

### 1.4 `rumor_intensity` (CrowdState.rumor_intensity)

**Class**: SECONDARY memory (synced from active rumors; not stored
independently).

**Generation**:
- Set per-tick from active rumor count + intensity (computed not stored).
- Direct injection possible via inject_crowd_event for some event types.

**Maintenance**:
- `rumor_intensity_decay = 0.08` per tick.

**Downstream effects**:
- Visible in trajectory; some narrative rendering.
- Currently NOT directly read by agent pressure or motif activator.

**Class refinement**: Mostly a derived/displayed field. Real rumor state
lives in RumorRegistry's individual Rumor objects.

---

### 1.5 `accusation_amplification` (CrowdState)

**Class**: TRANSIENT memory (fast decay).

**Generation**:
- inject_crowd_event for accusation-related events.

**Maintenance**:
- Decay 0.1 per tick (faster than other fields).

**Downstream effects**:
- Some inject_crowd_event branches read it for amplification.
- Iter 60 audit classified as low-coupling.

---

### 1.6 Active rumor reach (RumorRegistry per-rumor `reach` set)

**Class**: ACTIVE memory at rumor-individual level.

**Generation**:
- `RumorRegistry.spawn(...)` creates rumor with initial `reach`
  (typically the originator + immediate seeded recipients).

**Maintenance**:
- Per-tick propagation: each tick, reach grows by propagation_rate ×
  neighbors via social_network.
- Per-tick decay: rumor.intensity decays at rumor.decay_rate.
- Cleanup: rumor with intensity < cleanup_threshold removed.

**Downstream effects**:
- Active forgiveness rumor → Phase 2a recovery
- Active accusation/threat rumor → indirect pressure via crowd memory
- Information topology: who knows what when

---

## 2. Channel summary table

| Channel | Generation | Decay | Consumer | Class |
|---|---|---|---|---|
| shame_climate | accusation events | none | Phase 2a + shame_repair | **ACTIVE** |
| authority_vigilance | guard_approaches | none (decay constant defined but not applied) | none (Iter 38) | **DEAD** |
| blame_concentration[r] | accusation event | 0.04/tick | Phase 2a | **ACTIVE** |
| rumor_intensity | derived | 0.08/tick | display only | TRANSIENT |
| accusation_amplification | inject | 0.1/tick | injection helpers | TRANSIENT |
| Rumor.reach | spawn | per-cleanup | Phase 2a, info topology | **ACTIVE** |
| Rumor.intensity | spawn | rumor.decay_rate | Phase 2a | **ACTIVE** |

**Active memory channels: 4** (shame_climate, blame_concentration[r],
Rumor.reach, Rumor.intensity).

**Dead memory channels: 1** (authority_vigilance).

**Transient (non-memory) fields: 2** (rumor_intensity, accusation_amplification).

---

## 3. Proposed new channels (DESIGN ONLY, NO IMPLEMENTATION YET)

Per directive §5.4 candidates:

### 3.1 `forgiveness_trace` (proposed)

**Purpose**: Track recent forgiveness activity at crowd / role level so
that downstream events can reference "this place / role recently
received forgiveness."

**Generation**:
- Each Phase 2a forgiveness rumor consumption tick:
  `crowd.forgiveness_trace[target_role] += rumor.intensity * 0.05`,
  capped at 1.0.

**Maintenance**:
- Slow decay: 0.01 per tick (HL ~70 ticks). Per-role keys.

**Downstream effects (proposed)**:
- → reduced future shame_climate accumulation rate for that role
- → motif activator could read `forgiveness_trace[agent.role_id]` to
  bias toward repair/seek_repair over confess
- → narrative logs could mark "place of recent forgiveness"

**Coupling cost**: 1 new field on CrowdState + ~5 lines in Phase 2a
loop + optional motif coupling.

**Status**: NOT IMPLEMENTED. Design only.

### 3.2 `rumor_residue[content_tag]` (proposed)

**Purpose**: Track that a rumor of type X "passed through" even after
its active intensity decayed to zero. Long-tail world memory of
information that moved.

**Generation**:
- When a Rumor.intensity falls below cleanup_threshold (about to be
  removed), add `crowd.rumor_residue[rumor.content_tag] += 0.3`.

**Maintenance**:
- Slow decay 0.005 per tick (HL ~140 ticks).

**Downstream effects (proposed)**:
- → biases future rumor spawn (re-seeding rate higher in places
  with prior rumor traces)
- → information_topology can read residue to detect "informational
  echo chambers"
- → narrative: "this is a place that has heard this kind of rumor before"

**Status**: NOT IMPLEMENTED. Design only.

### 3.3 `unresolved_group_tension` (proposed)

**Purpose**: Track collective unresolved conflict at crowd level.
Distinct from blame_concentration (which is target-specific) — this
is overall-tension residue.

**Generation**:
- When alignment_strength is high but blame_concentration is split
  across multiple targets (faction-like state):
  `unresolved_group_tension += 0.05`

**Maintenance**:
- Slow decay 0.01 per tick.

**Downstream effects (proposed)**:
- → contagion_susceptibility multiplier (high tension makes future
  events more contagious)
- → pre-disposition for lynch_mode phase transition

**Status**: NOT IMPLEMENTED. Design only.

---

## 4. Decision criteria for implementing proposed channels

Per freeze discipline (no mass new variables):
- **Implement only if Branch B simplification justifies**, OR
- **Implement only if readability blind reveals a gap** that the new
  channel would close.

Recommended order if implementation is approved:
1. **forgiveness_trace** first — directly extends M24 finding (confess-
   feedback) into long-term memory. Low coupling cost.
2. **rumor_residue** second — extends information topology, useful for
   broader-world phase.
3. **unresolved_group_tension** third — feeds meso-scale (Priority 5).

DO NOT implement all three at once.

---

## 5. authority_vigilance — IMMEDIATE ACTION REQUIRED

The biggest finding of this audit: **authority_vigilance is a
persistent inert memory channel**.

It accumulates from guard_approaches events, never decays in current
step_crowd code, and has no downstream consumer (Iter 38 removed).
Yet it's still computed and logged.

This is the kind of "decorative wire" the freeze + audit phase aims to
catch.

**Recommended action options**:

### Option A — Re-wire (restore Iter 4 design intent)
Add to `_compute_agent_pressures` (world.py:443-445 area):
```python
pressures["physical_threat"] = min(
    10.0,
    pressures["physical_threat"] + crowd.authority_vigilance * 2 * role_cs,
)
```

This restores authority_vigilance as an active memory channel feeding
physical_threat pressure. Iter 38 ablation showed LOW-EFFECT, but with
proper testing (post-freeze) it could become SUPPORT-level.

### Option B — Annotate as inert
Update CrowdState.authority_vigilance docstring:
```python
authority_vigilance: float = 0.0  # 0-1
"""Memory of authority suppression events. Accumulates from
guard_approaches events. STATUS (2026-04-25): NO downstream coupling
(Iter 38 removed). Logged in trajectory + narrator. Cycle-mechanism
INERT. RESERVE for v1.0 / future re-wiring."""
```

### Option C — Remove
Delete authority_vigilance from CrowdState entirely (low cost; no
consumers). Update inject_crowd_event to drop authority_suppression
side effect. But: would break trajectory schema; possibly v1.0 latent
drive references; not recommended in freeze.

**My recommendation: Option B (annotate)**. Defer Option A to post-Step-C
branch decision. If Branch B (simplification) wins → keep annotated.
If Branch A or C → consider re-wire.

---

## 6. Memory channel scoring per Scale-3 (World Memory)

Per WORLD_BUILDING §3.3:
- 0 = matter-of-fact tick reset
- 1 = transient residue
- 2 = meaningful residue + re-exposure effect
- 3 = multiple memory channels working simultaneously

**Current measured score (post Iter 1 autonomy probe, this doc audit)**:
- 4 ACTIVE channels (shame_climate, blame_concentration, Rumor.reach,
  Rumor.intensity)
- shame_climate has clear re-exposure effect (drives shame_exposure
  pressure indefinitely until Phase 2a clears)
- Multiple channels work simultaneously in any non-trivial scenario

**Score: 2** (meaningful residue + re-exposure, multiple channels).

To reach **3**: need at least 2 channels in independent feedback loops
(currently most channels feed Phase 2a but Phase 2a is single-channel
recovery). Adding forgiveness_trace + rumor_residue would help.

---

## 7. Branch decision implications

### What this audit reveals

1. **shame_climate is the only structurally important memory channel**
   for cycle dynamics. Other "memory" fields are either inert
   (authority_vigilance) or local to rumor lifecycle.

2. **Adding new memory channels** before readability validation is
   premature (Priority 4 partial — design done, implementation
   deferred).

3. **authority_vigilance** is a clear cleanup target — Option B
   annotation is low-risk and brings honest documentation.

### Branch implications
- **Pro Branch B**: clear cleanup target (authority_vigilance) + 3
  proposed new channels NOT implemented = simplification preserved
- **Pro Branch A**: forgiveness_trace would directly support narrative
  layer ("place of recent forgiveness")
- **Pro Branch C**: rumor_residue + unresolved_group_tension are
  broader-world prerequisites

---

## 8. What could still be wrong (H4)

- Static analysis based; possible that authority_vigilance is read by
  some path I didn't grep (e.g., narrator, trajectory aggregations,
  v1.0 latent drive).
- "Inert" claim for authority_vigilance assumes Iter 38's coupling
  removal is still in effect. Should verify by ablation.
- Proposed new channels (3.1-3.3) are designs without empirical
  validation. May not produce expected dynamics.
- Scale-3 score of 2 is my classification; could differ under different
  scoring criteria.

---

## 9. What I did NOT try (H2)

- Empirical ablation of authority_vigilance (set max value, observe
  any change — would confirm "no downstream effect" empirically).
- Implementation of any proposed new channel (deferred per discipline).
- Cross-pipeline check for authority_vigilance consumers (latent_drive
  etc.).

---

## 10. Conclusion

**Priority 4 partial completion**:
- ✅ Existing channels formalized (Section 1-2)
- ✅ Proposed new channels designed (Section 3) — implementation deferred
- ✅ Scoring per Scale-3 (Section 6) — current Score 2
- ⚠ authority_vigilance Action A/B/C decision pending — recommend Option B
  annotation as low-risk during freeze

**Score 2 on Scale-3 World Memory** consistent with Stage B kernel
(per WORLD_BUILDING §4).

To advance to Stage C/D requires:
- Step C readability verifying memory channels are perceptible to
  human reader
- One or more new channels (forgiveness_trace recommended first)
- Or simplification of authority_vigilance dead path

---

**End of World Memory Layer Formalization. Companion to
WORLD_PROCESSES.md. Implementation of new channels deferred to post
branch decision.**
