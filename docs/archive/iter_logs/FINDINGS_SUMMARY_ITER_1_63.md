# WITNESS B-Direction — Consolidated Findings (Iter 1-63)

**Date:** 2026-04-24
**Scope:** All iterations through Iter 63 (post stabilization phase).
**Supersedes:** `FINDINGS_SUMMARY_ITER_1_48.md`

---

## 0. Executive Summary

A generative world engine operating on ~6-12 agents, 3-4
locations, 10 role clusters, produces **agent-level emergent motif
dynamics** with long-horizon **limit cycle** behavior.

Scenario-level aggregates show 4 labelable arc patterns (A/B/C/D),
but these are aggregate views of per-agent motif competitions.

**Updated Loop (Iter 51-63)** added 3 structural safeguards on top
of the pre-Iter-50 kernel:
- Event contract lint (Iter 51) — catches producer/consumer
  mismatches before runtime drift
- Component Ledger (Iter 52) — single-source-of-truth classifying
  every kernel component
- Drift prevention rules — prevent silent reclassification
  (demonstrated Iter 60)

All §15 completion conditions met (6/6). Updated Loop §6 criteria
7/8 met (only external readability blind check remains, requires
human).

**One-line claim:** *63 iterations + 18 retractions produced a
stable kernel + stabilization infrastructure. The kernel is no
longer in exploration mode; it's in maintenance mode with
explicit drift guards.*

---

## 1. What Changed Since Iter 48

Iter 49: Updated Loop 작업지시서 적용 시작.

### 1.1 Priority 1 — Interpretation Stabilization (Iter 51-52)

**Iter 51: Event contract lint.**
- Built `engine/world/event_registry.py` as single-source event
  names.
- Built `scripts/b_direction/audit_event_contract.py` scanner.
- Built `tests/test_world_process/test_event_contract.py` (6 tests
  enforcing registry consistency).
- Discovered: **Active contract = 2 events** (forgiveness_emitted,
  public_confession). Before Iter 34 M6 fix, 0 active contracts.
- Surfaced: 4 legacy v3 orphan consumers, 12 dead emissions.

**Iter 52: Component Ledger.**
- Built `docs/b_direction/COMPONENT_LEDGER.md` classifying 20
  components (KERNEL/CONDITIONAL KERNEL/SUPPORT/CONTEXTUAL/
  INERT/DEPRECATED).
- 5 drift-prevention rules.
- Flagged 3 HIGH-uncertainty items for ablation.

### 1.2 Priority 2 — Prior Ablation (Iter 53)

Conditional invariance ratio across 4 prior conditions:
- No priors (DEFAULT): 3.88
- Weak (α=0.3): 4.34
- Current (Iter 11 setup): 3.64
- Strong (sharpened): 4.69

All STRONG (≥3.0). Spread 1.05. **Conditional invariance is
prior-independent.** Layer 1 mechanism in pressure_sensitivity +
motif_tendency + affordance_pack (NOT priors).

### 1.3 Priority 3 — Topology Fingerprint Re-audit (Iter 54)

Added 3 dynamics axes:
- D1 reversal density
- D2 memory tail (final shame_climate)
- D3 relation restructuring magnitude

Clustering on dynamics axes:
- Group 1: calling alone
- Group 2: accusation alone (vs Iter 22 saying acc ≈ scr)
- Group 3: scarcity + sacred
- Group 4: private_crisis

Iter 22's "accusation ≈ scarcity" was static-only. On dynamics,
accusation has D3=4.89 (high relation restructuring) vs scarcity
D3=1.15. Topology is a **polymorphic concept** — different axes
reveal different structure.

### 1.4 Priority 4 — Limit Cycle Source (Iter 55-56, 58-59)

**Iter 55 correlation analysis** → cycle source candidate:
forgiveness rumor Phase 2a loop. Period ~30 ticks.

**Iter 56 P1 ablation** → source identification CONFIRMED.
Disabling Phase 2a → cycles drop from 3.3 to 0 per agent (100%
elimination). Unexpected secondary: confess count 4× higher under
ablation (confess becomes local-only without Phase 2a transmitter).

**Iter 58 P2 decay sweep** → FAILED. Period doesn't scale as
1/decay. Proposed two-term model (rumor lifetime + blame rebuild).

**Iter 59 P4 deny intensity sweep** → FAILED. Period doesn't
scale with deny intensity either.

**Refined (M16)**: Cycle period ≈ 30 tk is **emergent property
of interacting dynamics**. No single parameter scales it cleanly.
Robust against ±2× parameter changes.

### 1.5 Priority 6 — Mixed-Arc Coexistence (Iter 57)

Injected high guilt into 3 agents of accusation scenario:
- agent_04 priest: stayed Arc B (conceal, confirmed Iter 46
  authority cast-conditional)
- agent_06 outsider: shifted to Arc D (grieve 0.191)
- agent_09 disciple: shifted to Arc D (grieve 0.200)
- 7 uninjected agents: normal patterns unchanged

**Coexistence CONFIRMED.** 3+ per-agent arcs in one scenario.
Findings from clean scenarios hold under mixed pressure.

### 1.6 Stabilization Cleanup (Iter 60-63)

**Iter 60: Drift prevention rule 1 demonstrated.** Planned
deletion of 4 "orphan consumer" branches blocked by discovery
they're shared with PersonV3Loop + rubric critics + tests.
Reclassified DEPRECATED → CROSS-PIPELINE.

**Iter 61: blend_power SUPPORT validated.** Quadratic (P=2) is
local optimum. Linear (P=1) costs 5pp in scarcity. Cubic (P=3)
worse than both.

**Iter 62: recovery_bias INERT confirmed.** Bit-identical output
over 50× range. No runtime reader; pure v3 legacy data carrier.

**Iter 63: relation_bias INERT confirmed.** Bit-identical over
20× range. Scenario builders' archetype relation_bias tuning is
cosmetic. **Layer 1 mechanism narrowed from 4 to 3 components**
(relation_bias dropped).

---

## 2. Current Engine State (Iter 63)

### 2.1 Test health
- 181 B-direction tests green (was 175 pre-Iter-51; +6 event
  contract tests)
- Rule #1 preserved

### 2.2 Kernel summary

**KERNEL (9 components):**
- Motif layer (motif_tendency + activate_motifs + quadratic blend)
- Pressure_sensitivity (role field)
- Crowd dynamics (CrowdState + blame)
- Rumor layer + action→rumor amplification
- Spatial pressures
- State transition rules
- **Forgiveness rumor Phase 2a loop** (cycle source, P1 confirmed)
- Active contract events (forgiveness_emitted, public_confession)

**CONDITIONAL KERNEL (1):**
- motif_action_priors (kernel for transitions, not invariance)

**SUPPORT (5, was 6):**
- Quadratic top-2 blend (Iter 61 validated)
- Affordance_pack
- climate_sensitivity
- Shame_climate field
- Action consequences on self
- Role transition

**INERT (3, was 1):**
- authority_vigilance field (Iter 38 confirmed)
- recovery_bias persona field (Iter 62 confirmed)
- **relation_bias persona field (Iter 63 confirmed)**

**CROSS-PIPELINE (1):**
- 4 legacy v3 consumer branches in motif activator (motif shared
  with PersonV3Loop)

**INFRASTRUCTURE (4 ablation toggles, default = production):**
- `forgiveness_phase_enabled` (Iter 56)
- `forgiveness_rumor_decay_override` (Iter 58)
- `deny_blame_intensity_override` (Iter 59)
- `blend_power` (Iter 61)

---

## 3. Core Findings (confidence-ranked, post-Iter-63)

### F1. WORLD_FLOW_LOOP methodology (highest)

63 iterations. **18 refinements/retractions** (28.6%). Methodology
repeatedly catches overclaim, including conceptual framings.
Updated Loop added formal Phase 0 gates and component ledger
discipline.

### F2. Two-layer decomposition (Iter 21)

Layer 1 (role signature, prior-dominated) vs Layer 2 (scenario
outcomes, pressure-responsive). **Refined Iter 63**: Layer 1
driver set is 3 components, not 4.

### F3. Autonomous emergent recovery (Iter 34-36, 55-56)

Rise_then_fall at agent level:
- accusation: 60% CI [51.7%, 66.7%] (Iter 36)
- scarcity: 96% CI [91.2%, 100%]
- sacred: 91% CI [86.0%, 96.0%]

Mechanism: forgiveness rumor Phase 2a loop (Iter 55-56 source +
ablation).

### F4. Conditional role invariance (Iter 14-18, validated Iter 53)

- Within-topology: 3.83×, CI [3.43, 4.33]
- Cross-topology: 4.93-7.85×
- **Prior-independent** (Iter 53: ratios 3.56-4.69 across 4 prior
  conditions)

### F5. Agent-level topology emergence (Iter 47-48)

Scenarios are ensemble-level phenomena where minority drives
observable dynamics. Confirmed at mixed-arc (Iter 57 coexistence).

### F6. Long-horizon limit cycle (Iter 50, refined Iter 58-59)

Crisis scenarios produce limit cycles:
- Period ~30 tk (emergent, robust to ±2× parameter changes)
- Source: forgiveness rumor Phase 2a loop (ablation-proven)
- NOT a simple 1-parameter clock

### F7. Role priors CONDITIONAL KERNEL (Iter 7, 19, 20)

Transition scenarios: 21× effect.
Standalone scenarios: no effect (build scripts hardcode DEFAULT).
Conditional invariance: prior-independent (Iter 53).

---

## 4. Effect-Size Table (Final, post-Iter 63)

| Finding | Metric | Value | CI/Context |
|---|---|---|---|
| Conditional invariance (within-topology) | ratio | 3.83× | 95% CI [3.43, 4.33] n=20 |
| Conditional invariance (cross-topology) | ratio | 4.93-7.85× | 3 pairs |
| Prior-independence (Iter 53) | ratio spread | 3.56-4.69 | 4 conditions |
| Transition action-JS | ratio | 21× | n=5 |
| D-flow accusation | rise_fall fraction | 60.0% | [51.7%, 66.7%] n=20 |
| D-flow scarcity | rise_fall fraction | 96.3% | [91.2%, 100%] n=20 |
| D-flow sacred | rise_fall fraction | 91.0% | [86.0%, 96.0%] n=20 |
| Limit cycle period | mean, tight distrib | 31.6 tk | stdev 14.6 n=84 periods |
| Phase 2a ablation (Iter 56) | reversals drop | 3.3 → 0 | 100% elimination |
| Arc D F1 (at guilt=6) | JS vs calling | 0.205 | private_crisis cast |
| blend_power scarcity sensitivity (Iter 61) | rate delta | 5pp | P=1 vs P=2 |

---

## 5. Retraction Log (18 total)

### Numerical / scope corrections
| # | Iter | Correction |
|:-:|:-:|---|
| M1 | 19 | Iter 11 blame diversification via priors: build scripts hardcoded DEFAULT |
| M2 | 15 | Iter 14 ratio 8.46× → 3.83× bootstrap CI |
| M3 | 20 | Iter 19 Iter 7 scope narrow partial reversal (21× transition valid) |
| M4 | 22 | Iter 9: 3 scenarios → 2 topologies → 4 topologies → agent-level emergence |
| M5 | 6 | Iter 1-5 incremental keeps all noise-level |
| M10 | 41 | Iter 40 Arc D at F1=0.154 borderline at n=20 |
| M11 | 46 | Arc D cast-conditional (not universal) |

### Mechanism / framework corrections
| # | Iter | Correction |
|:-:|:-:|---|
| M6 | 34 | External shock for recovery: name mismatch hid autonomous path |
| M7 | 35 | Sacred 8% failure: repair was suppressing, autonomous = 88% |
| M8 | 37 | Iter 27 climate_sensitivity LOW-EFFECT → SUPPORT (13pp sacred) |
| M9 | 40 | Iter 24 engine bistable → quadstable |
| M12 | 47 | Engine has N discrete topologies → topology is agent-level |
| M13 | 48 | Arc B = everyone in crisis → minority-driven aggregate |
| M14 | 50 | Arc C single rise_then_fall → limit cycle (long horizon) |
| M15 | 58 | Iter 55 cycle period ∝ rumor lifetime → two-term model |
| M16 | 59 | Two-term model fails → period is emergent (no single-param scaling) |
| M17 | 60 | Iter 51 DEPRECATED classification → CROSS-PIPELINE |
| M18 | 63 | Iter 20 Layer 1 driver set: 4 components → 3 (relation_bias INERT) |

18 refinements across 63 iterations (28.6% rate). Most are scope
or mechanism refinements; few are full reversals.

---

## 6. §15 Completion Conditions (Final)

| # | Condition | Status |
|:-:|---|:-:|
| 1 | 1+ scenario C_propagating | ✓ |
| 2 | Events propagate ≥2 layers | ✓ |
| 3 | World memory changes possibility | ✓ |
| 4 | 3+ distinct arcs | ✓ (4 scenario labels + per-agent variety) |
| 5 | Dominant/dead/over-dominant | ✓ |
| 6 | Loop ≥3x methodology | ✓✓✓ (63 iterations) |

All 6 met.

## 7. Updated Loop §6 Completion Criteria (post-Iter 63)

| # | Criterion | Status | Iter |
|:-:|---|:-:|:-:|
| 1 | event mismatch lint | ✓ | 51 |
| 2 | analysis unit separation | ✓ | 51-63 |
| 3 | role priors ablation | ✓ | 53 |
| 4 | topology fingerprint | ✓ | 54 |
| 5 | limit cycle source | ✓✓ (P1 confirmed, P2/P4 refined) | 55-56-58-59 |
| 6 | external readability | **✗** (needs human) | — |
| 7 | mixed-arc preservation | ✓ | 57 |
| 8 | component ledger | ✓ (drift rules demonstrated) | 52-60-62-63 |

**7/8 criteria met.** Only criterion 6 blocked on human evaluator.

---

## 8. What This Work Does NOT Claim

- NOT universality
- NOT narrative-generative "solved" (external readability owed)
- NOT agent-level topology is the ONLY framing
- NOT the 18 retractions invalidate findings — most are
  refinements of magnitude or scope

Post-Iter-63 caveats:
- relation_bias INERT in B-direction but still required for v3
  content JSON compat (deletion blocked)
- Cycle period model admits no simple form; characterization is
  "emergent ~30 tk, robust"
- Single external evaluator would unlock readability criterion

---

## 9. Open Questions (updated)

1. **External readability** — Lee or outsider blind eval.
2. **P3 prediction** (rumor intensity × amplitude) — not tested.
3. **Multi-parameter cycle grid** — could reveal higher-order
   scaling invisible to 1-D sweeps.
4. **200+ tick long-horizon per scenario** — only accusation
   tested at this depth.
5. **Per-critic audit** — rubric critics' use of legacy v3 events
   (are some dead within legacy too?).

---

## 10. The Single Most Important Sentence (updated)

> **Through 63 iterations and 18 retractions, WORLD_FLOW_LOOP
> produced not just the engine findings but the STABILIZATION
> INFRASTRUCTURE around them — event contract lint, component
> ledger with drift rules, 4 reversible ablation toggles. The
> engine is in maintenance mode, not exploration mode.
> Misclassification was caught twice during cleanup (Iter 60
> DEPRECATED → CROSS-PIPELINE; Iter 63 SUPPORT → INERT) — ledger
> discipline working in practice.**

---

## 11. Artifacts Index

All iteration reports in `docs/b_direction/probe_runs/`:
- LOOP_ITER_1.md through LOOP_ITER_63.md
- LOOP_ITER_27_LAYER_AUDIT.md

Probe scripts in `scripts/b_direction/` (60+ scripts).

Engine state (key files at Iter 63):
- `engine/world/micro_world/world.py` — MicroWorld + 4 ablation
  toggles
- `engine/persona/motif.py` — activator with peer-signal wiring
- `engine/persona/selector.py` — blend_power parameterized
- `engine/world/event_registry.py` — contract registry
- `engine/population/role_cluster.py` — 10 roles with motif_tendency
  + climate_sensitivity + motif_action_priors
- `engine/population/transitions.py` — role transition mechanism

Summary documents (chronological):
- `FINDINGS_SUMMARY_ITER_1_32.md`
- `FINDINGS_SUMMARY_ITER_1_43.md`
- `FINDINGS_SUMMARY_ITER_1_48.md`
- `FINDINGS_SUMMARY_ITER_1_63.md` (this)

Component Ledger:
- `docs/b_direction/COMPONENT_LEDGER.md` (v1.2, post Iter 63
  updates)

---

**End of refreshed summary. Kernel state at Iter 63 is stable +
maintained. Stabilization phase near-complete (only human
readability eval blocks full completion).**
