# WITNESS B-Direction — Kernel Freeze State

**Freeze date:** 2026-04-25
**Branch:** main
**Git SHA:** `2ec0da125fbb0d334b159351ef1967c058acb0e0`
**Last commit:** `2ec0da1 chore: tidy root -- move spec/research/demo files into docs/ + examples/`
**Iterations executed:** Iter 1-89 (89 total; 25 of those in the 65-89 stabilization block)
**Lifetime retractions:** 25 (M1-M14 pre-Iter-50 + M15-M25 post)

---

## 0. Purpose

This document freezes the B-direction MicroWorld kernel as of 2026-04-25.
It defines **the baseline** against which the post-loop audit (Claim
Status Matrix, Inert/Reserve Audit, Mixed-Arc Probe) is performed.

No further iteration-style probes are admitted against this baseline
until the freeze audit concludes.

---

## 1. Active scenarios (in scripts/b_direction/)

| Scenario | Builder | Cast | Locations | Seed events |
|---|---|---|---|---|
| accusation | `run_accusation_scene.py` | 10 agents (disciples, priests, outsiders, crowd) | upper_room, priest_courtyard, city_street | 2 × public_accusation, guard_approaches |
| scarcity | `run_scarcity_scene.py` | 12 agents (merchants, family, fishers, priest, soldier, crowd, outsider, strategist) | marketplace, granary, poor_quarter | public_accusation (merchant), guard_approaches |
| sacred | `run_sacred_gathering.py` | 8 agents (prophet, priest, disciples, crowd, family) | temple_outer_court, temple_inner, city_street | prayer_invitation, miracle_witnessed, public_accusation (spiritual_wanderer) |

Notes:
- **Sacred scenario events** (`prayer_invitation`, `miracle_witnessed`) are
  **registered but dormant** (no downstream coupling). See Iter 77, 89.
- Sacred scenario character comes from **cast composition + crowd
  baselines + location tags**, not from sacred event flavor.

---

## 2. Active world processes (engine/world/micro_world/world.py)

The MicroWorld `step()` executes the following phases per tick:

1. **Phase 0** — seed events injection at scheduled ticks
2. **Phase 1** — event handler side-effects (blame, alignment, shame_climate)
3. **Phase 2** — crowd decay + rumor registry step (decay rumors, propagate)
4. **Phase 2a** — forgiveness rumor counter-pressure loop (KERNEL)
    - Crowd-layer: reduces blame_concentration, alignment_strength, shame_climate
    - Agent-layer: reduces per-agent shame/guilt/fear on target_role
5. **Phase 2b** — `_update_agent_state_from_world` (pressure → agent state)
6. **Phase 3** — agent decisions via `activate_motifs` + `select_action`
7. **Phase 4** — action application (`_apply_agent_action`) + self-consequences
8. **Phase 5** — history append, step object return

---

## 3. Active motif classes (engine/persona/motif.py)

14 motif activators defined and computed per tick per agent:

| Motif | Primary inputs | Role in cycle |
|---|---|---|
| conceal | shame_exposure pressure, social_threat, fear | Dominant in high-shame phase |
| confess | guilt + hope + forgiveness events (recent) | **Recovery-trigger** + feedback-runaway (M24) |
| confront | authority_vigilance pressure, anger | Rare firing |
| withdraw | isolation_pressure, fear | Secondary escape |
| flee | physical_threat, escape_routes | Rare |
| remain_present | inverse-pressure + love/loyalty | Dominant fallback |
| observe_wait | calm regime | Baseline high |
| grieve | grief + guilt + suffering events | Arc D driver (indicator, not cause) |
| weep | grief + moral_injury | Related to grieve |
| seek_repair | guilt + hope + relation bonds | Recovery adjacent |
| pray | awe + sacred_proximity | Sacred scenario decorative |
| stay_awake | ambient vigilance | Rare |
| assert_loyalty | loyalty + public_exposure | Specific trigger |
| discuss_with_disciples | peer_presence + info_urgency | Specific trigger |

**Empirically dominant at activate_motifs level** (Iter 84):
- remain_present: ~56% primary in baseline B
- conceal: ~33% primary in B; ~52% in P1 ablation (C)
- All other motifs: <5% primary

**Grieve-as-driver-motif** (from `step.agent_motifs`) differs from
grieve-as-activator-primary. Driver attribution via top-2 contribution
to chosen action; grieve is driver ~12% in B, ~2% in C.

---

## 4. Active role priors (engine/population/role_cluster.py)

10 role clusters with profile_prior + motif_tendency + affordance_pack:

| Role | motif_tendency highlights | Cycle tendency |
|---|---|---|
| disciple_follower | varies with archetype | Cycles via confess/conceal |
| authority_priest | observe_wait 1.3, confront 1.2 | Absorbs blame, no cycling |
| soldier_enforcer | varies | Cycles |
| crowd_participant | varies | Cycles (dominant cohort) |
| outsider | varies | Variable (low motif coherence) |
| merchant | varies | Used in scarcity |
| family_anchor | remain_present high | Protective, low cycling |
| fisherman | varies | Cycles under scarcity |
| elite_strategist | observe_wait high | Low cycling |
| spiritual_wanderer | awe-related | Sacred scenario |

---

## 5. Active feedback loops

### 5.1 Phase 2a forgiveness loop (KERNEL)
- confess action → spawn forgiveness rumor (always unconditional)
- Phase 2a consumes active forgiveness rumors → reduces shame/guilt/fear
- **Negative feedback** on confess-motif activation via state reduction

### 5.2 confess events_recent feedback (M24, verified)
- confess action → spawn `forgiveness_emitted` + `public_confession` events
- `events_recent` includes these events (binary presence within lookback window)
- confess motif reads events_recent → activation rises
- Under Phase 2a OFF: no shame recovery → confession keeps firing → events accumulate → runaway

### 5.3 Crowd-agent pressure loop
- agent actions → inject_crowd_event → blame/alignment shifts
- crowd state → shame_exposure / social_threat pressures → agent motif activation
- Bidirectional but mediated by Phase 2a cleanup

### 5.4 Rumor propagation
- rumors spawn by actions (deny, confess, withdraw_in_fear)
- propagate via social_network each tick
- decay at rumor-type-specific rate
- target_role-specific consumption by Phase 2a

---

## 6. Ablation toggles in MicroWorldConfig (13 total)

All default to production behavior; all reversible.

| # | Toggle | Iter added | Default | Purpose |
|:-:|---|:-:|:-:|---|
| 1 | forgiveness_phase_enabled | 56 | True | P1 ablation (Phase 2a whole) |
| 2 | forgiveness_rumor_decay_override | 58 | None | P2 test |
| 3 | deny_blame_intensity_override | 59 | None | P4 test |
| 4 | blend_power | 61 | 2.0 | Selector blend exponent |
| 5 | forgiveness_rumor_intensity_override | 65 | None | P3 amplitude test |
| 6 | forgiveness_crowd_layer_enabled | 67 | True | Crowd-layer sub-block |
| 7 | forgiveness_agent_layer_enabled | 67 | True | Agent-layer sub-block |
| 8 | forgiveness_agent_shame_enabled | 71 | True | Shame decrement |
| 9 | forgiveness_agent_guilt_enabled | 71 | True | Guilt decrement |
| 10 | forgiveness_agent_fear_enabled | 71 | True | Fear decrement |
| 11 | forgiveness_agent_shame_multiplier | 72 | None (=0.4) | Shame mag override |
| 12 | forgiveness_agent_guilt_multiplier | 72 | None (=0.3) | Guilt mag override |
| 13 | forgiveness_agent_fear_multiplier | 72 | None (=0.2) | Fear mag override |

---

## 7. Known dormant / decoupled components

### 7.1 Dormant events (registered but no consumer)
(Confirmed Iter 77 + event_registry.py audit)
- `prayer_invitation`
- `miracle_witnessed`
- + 4 other legacy v3 events in `LEGACY_V3_EVENTS` frozenset

### 7.2 Narrative-only state fields (INERT in MicroWorld)
(Confirmed Iter 78 empirical + Iter 89 static analysis)
- `awe`
- `moral_injury`
- `identity_shift`
- `trust_scar`
- `event_trauma`
- `breach_count`

These fields:
- Are defined in `engine/core/state.py`
- Are NOT read by any motif activator
- Are NOT updated by MicroWorld step
- Are read by: latent_drive (v1.0 unused), narrator (rendering), trajectory (logging)
- **Cannot be deleted** (break state-pack loaders + narrator + trajectory)

### 7.3 Defined-but-unwired rules
- `engine/rules/slow_recovery.py` → `SlowStateFieldRecoveryRule`
  - Not imported anywhere in engine or tests
  - Would update trust_scar / event_trauma if instantiated
  - Default constructor is zero-effect sentinel

### 7.4 Fields previously reclassified INERT (Component Ledger)
- `authority_vigilance` (pre-Iter-50)
- `recovery_bias` (Iter 62, 50× ablation bit-identical)
- `relation_bias` (Iter 63)

### 7.5 CROSS-PIPELINE retained components
- Orphan motif-activator branches for legacy v3 events (Iter 60)
- Narrative-only state fields (retained for v1.0 + narrator + trajectory consumers)

---

## 8. Test state

**Full test suite: 1647 passed, 4 warnings** (verified at freeze, 2026-04-25).
- `tests/test_world_process/` (event contract + core)
- `tests/test_world/` (3-layer separation + world logic)
- Plus test_person/, test_rubric/, test_persona/, test_engine/, test_peter/, etc.

Previous iteration reports cited "287 tests green" for the world subset
(`tests/test_world/` + `tests/test_world_process/`). Full repo suite is 1647.

Event contract lint: 6/6 pass (registry audit).

---

## 9. Noise floor (Iter 70)

For **rev/agent** measurement under `(N=5 seeds, 200 tk, PYHASH pinned)`:
- stdev = 0.388
- span = 1.10 across 10 hash seeds
- Triage rule: effect/stdev ≥ 3.0σ SAFE, 1.5-3.0σ MARGINAL, < 1.5σ HASH-NOISE

For **event presence frequency** under `(N=5 seeds, 100 tk, PYHASH=0)` (Iter 86):
- B stdev ~7%, C stdev ~20% (bimodal), D stdev ~12%
- Binary-valued data; aggregate as presence-frequency not mean

Period noise across (N=5, 200 tk): CV ~5.5% (Iter 65) to 12.3% (Iter 74);
configuration-dependent, not fully characterized.

---

## 10. Probes and metrics (current definitions)

### Probe infrastructure
- Single seed by default; 5 seeds for ablation tests; 10 for noise floor
- PYHASH=0 pinned (Iter 70+) for deterministic baseline
- 100-200 tick horizons (200 for cycle-period measurements)

### Metrics
- **rev/agent**: count of smoothed-direction reversals in shame time-series
  (window=20, direction-change threshold abs(Δ)>=0.05)
- **amp-thresholded rev/agent** (Iter 69): filter with peak-trough >= 1.0
- **grieve_frac**: fraction of ticks where `step.agent_motifs == "grieve"`
  (measures **driver motif** from `select_action`, not activate_motifs primary)
- **forgiveness_emitted presence %**: fraction of motif-activation calls where
  `events_recent` contains `forgiveness_emitted`

### Arc labels (surface classification only — M21)
- Arc A, B, C, D differ in motif composition
- All share Phase 2a shame recovery channel
- Labels do not imply different mechanisms

---

## 11. Snapshot manifest

### Source files (critical, unchanged from freeze)
- `engine/world/micro_world/world.py` — step pipeline + 13 toggles
- `engine/world/event_registry.py` — event contract single-source
- `engine/persona/motif.py` — 14 motif activators
- `engine/persona/selector.py` — select_action + driver-motif attribution
- `engine/population/role_cluster.py` — 10 role clusters
- `engine/population/transitions.py` — role transition mechanism

### Documentation snapshots
- `docs/b_direction/COMPONENT_LEDGER.md` (as of Iter 89)
- `docs/b_direction/FINDINGS_SUMMARY_ITER_1_63.md` (Iter 64)
- `docs/b_direction/FINDINGS_SUMMARY_ITER_64_74.md` (Iter 75)
- `docs/b_direction/FINDINGS_SUMMARY_ITER_75_86.md` (Iter 87)
- `docs/b_direction/probe_runs/LOOP_ITER_1.md` through `LOOP_ITER_89.md`

### Probe scripts (in scripts/b_direction/)
- 60 iteration-labeled probe scripts
- 3 scenario builders (accusation, scarcity, sacred)
- 2 auxiliary (counterfactual_probe, audit_event_contract)

---

## 12. Freeze declaration

**The kernel described above is the freeze baseline for the
post-loop audit phase** (Freeze → Claim Matrix → Readability Blind
→ Inert Audit → Mixed-Arc Probe → Branch Decision).

During audit:
- No new iteration-style probes
- No Phase 2a / shame / confess further drilling
- No new variables or layers
- No neural-policy probes
- No "universality now confirmed" claims
- No single-seed major conclusions

Freeze holds until branch decision (A readability / B simplification /
C broader world).

---

**End of Kernel Freeze. Subsequent audits reference this document for
the baseline.**
