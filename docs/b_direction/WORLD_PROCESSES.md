# WITNESS B-Direction — World-Side Independent Processes

**Date:** 2026-04-25
**Doc reference:** `WITNESS_WORLD_BUILDING_ELEMENTS_AND_SCALE.md` §5 priority 3
**Status:** Formal promotion of 3 existing processes to standalone-process status.

---

## 0. Purpose

Per work directive §5 priority 3, formalize 3 world-side processes
that operate independently of agent actions:

1. **Rumor propagation**
2. **Crowd attention / blame concentration**
3. **Authority response / vigilance**

"Formal promotion" means:
- Document operating semantics and per-tick autonomy
- Empirically verify each runs with NO agent activity
- Score 척도 1 (World-side Autonomy) per scale in WORLD_BUILDING doc

---

## 1. Process inventory

### 1.1 Process P1 — Rumor Propagation

**Module**: `engine/world/information/rumor_registry.py`
**Class**: `Rumor` + `RumorRegistry`

**Per-tick autonomous behavior**:
- All active rumors **propagate** via social_network (each rumor's
  reach grows by `propagation_rate` × neighbors per tick)
- All active rumors **decay** by `decay_rate` per tick
- Rumors with intensity < `cleanup_threshold` are removed
- **Distortion accumulates** at `distortion_gain` per tick

**Required input**: existing `Rumor` objects in registry (seeded by
`spawn()` from agent action handlers OR scenario seed_rumors).

**Output to world**:
- Per-target_role rumor intensity changes shame_climate, blame_concentration
- Active forgiveness rumors trigger Phase 2a recovery (Iter 56-66 verified)
- Rumor reach changes information topology

**Autonomy level**: HIGH — once seeded, runs with no agent input.

### 1.2 Process P2 — Crowd Attention / Blame Concentration

**Module**: `engine/world/crowd_dynamics/state.py`
**Function**: `step_crowd(state: CrowdState)`

**Per-tick autonomous behavior**:
- `density` decays at `density_decay` rate
- `alignment_strength` decays at `alignment_decay` rate
- `volatility` drifts toward equilibrium
- `shame_climate` decays at `shame_climate_decay` rate
- `authority_vigilance` decays at `authority_vigilance_decay` rate
- `blame_concentration` per-target decays at `blame_decay` rate
- `rumor_intensity` decays
- `accusation_amplification` decays
- Phase transition check (`idle → gathered → aligned → lynch_mode`)
  based on density + alignment thresholds

**Required input**: agent actions inject into crowd via `inject_*`
helpers; otherwise crowd decays.

**Output to world**:
- Crowd state → agent pressures via `_update_agent_state_from_world`
- Phase transition can trigger collective events
- Memory persistence (shame_climate, authority_vigilance) is the
  KEY world-memory channel

**Autonomy level**: MEDIUM — decay runs autonomously; updates need
event injection.

### 1.3 Process P3 — Authority Response / Vigilance

**Module**: `engine/world/crowd_dynamics/state.py` (authority_vigilance
field) + `engine/world/micro_world/world.py` (event handlers)

**Per-tick autonomous behavior**:
- `authority_vigilance` is part of CrowdState; decays per tick via
  step_crowd
- When `guard_approaches` event seeds, authority_vigilance increases
  in target crowd
- Higher authority_vigilance → higher `social_threat` pressure on
  agents at that location

**Required input**: `guard_approaches` events (seeded or potentially
event-driven from rule violations).

**Output to world**:
- Authority pressure → agent fear, motif activation (conceal, withdraw)
- Long-tail vigilance memory after authority moments
- Could trigger arrest events at very high vigilance (currently
  unused capability)

**Autonomy level**: LOW-MEDIUM — vigilance decays autonomously but
generation is event-triggered. Less independent than rumor.

---

## 2. World autonomy verification (empirical probe)

To formally promote these as "world-side processes," they must
demonstrate that world state changes WITHOUT agent activity.

### 2.1 Test design

Probe `scripts/b_direction/run_world_autonomy_probe.py` (companion
file):

- Build accusation MicroWorld
- Seed 1 rumor + 1 accusation event + 1 guard_approaches event
- **Disable agent decision step** (or use empty agent set)
- Run 100 ticks
- Measure: do rumor intensity, blame_concentration, shame_climate,
  authority_vigilance evolve over time?

If world state evolves with no agents → autonomy confirmed.
If state is static → world is reactive-only (척도 1 score = 1).

### 2.2 Score interpretation (per WORLD_BUILDING §3 scale)

| Score | Description |
|---|---|
| 0 | World fully passive |
| 1 | World responds only to events |
| 2 | Some processes autonomous |
| 3 | Multiple processes autonomous + cross-influence |

---

## 3. Cross-process interaction

Per directive, processes should "서로 영향을 주며 독립적으로 움직임"
(mutual influence + independent motion).

Current cross-influence chains:

### 3.1 Rumor → Crowd
- `rumor_intensity` field on CrowdState driven by active rumors
  targeting that crowd location
- Active accusation rumor → crowd blame_concentration accumulates

### 3.2 Crowd → Authority (partial)
- High alignment + high density → could trigger collective
  events (currently not all wired)
- shame_climate accumulation may affect future authority_vigilance
  via event handlers (depends on Phase 1 logic)

### 3.3 Authority → Crowd
- guard_approaches event → authority_vigilance up in crowd
- High authority_vigilance → reduces alignment_strength (suppression)
- Iter 24 'authority raid' tests verified this chain

### 3.4 Rumor → Authority
- Rumors don't directly affect authority_vigilance
- Could be wired: high-credibility threat rumor → authority_vigilance
  bump (currently absent)

### 3.5 Cross-influence map (current)

```
Rumor ──▶ Crowd ◀── Authority
   │         │
   └─────────┴──▶ Agent pressure ──▶ Agent action
                      ▲                  │
                      │                  ▼
                      └─── Crowd events / new rumors ──┘
```

Bidirectional in 2 of 3 pairs (rumor↔crowd, authority↔crowd).
Rumor↔authority is one-directional (authority can suppress; rumor
doesn't trigger authority directly).

---

## 4. Memory channels (interim — Priority 4 expansion target)

World-memory fields on CrowdState (existing):
- `shame_climate` — slow decay (HL ~tens of ticks)
- `authority_vigilance` — slow decay
- `blame_concentration[role]` — per-target slow decay
- `rumor_intensity` — fast decay (driven by active rumors)
- `accusation_amplification` — moderate decay

Memory channels NOT formally tracked (proposed for Priority 4):
- `unresolved_group_tension`
- `forgiveness_trace`
- `rumor_residue` (separate from active intensity)
- `public_attention_trail`

These are explicitly listed in WORLD_BUILDING §5 priority 4 as
"World Memory 정식 계층화" candidates for next iteration.

---

## 5. Process formalization checklist

Per directive §5 priority 3 goals:
- [x] 사람 없이도 world state가 움직임 — verified by Section 2 probe
- [x] 사람 행동이 world-level 변화를 남김 — already established (Iter 3-66)
- [x] world가 다음 사건 가능성 지형을 바꿈 — partially (memory fields)

---

## 6. Implications for branch decision

### Score on 척도 1 (World-side Autonomy) — MEASURED

**Score 3 / 3** (after empirical probe, 2026-04-25):

Frozen-agents condition (B) at t=100:
- **Rumor process**: AUTONOMOUS (rumor count 1→2→0; propagation +
  decay observed without agent action)
- **Crowd state process**: AUTONOMOUS (density 0.40→0.00,
  shame_climate 0.00→0.40, blame decay all happen autonomously)
- **Authority process**: AUTONOMOUS (authority_vigilance 0.00→0.25
  via guard_approaches handler injecting authority_suppression into
  crowd, then decaying)

**Caveat** (process-bug exposed by probe): The accusation scenario
seed events had `guard_approaches` at `location: "upper_room"`, but
upper_room has NO CrowdState. The handler silently skipped. Probe
fixed by retargeting to `priest_courtyard`. **Original scenario
should be similarly audited** — `guard_approaches` events targeting
crowdless locations are no-ops.

### Implications
- Score 2 is consistent with "Stage B: 세계 흐름 커널 확보" per
  WORLD_BUILDING §4
- Promoting to Stage C (읽히는 세계 입구) requires readability validation
  (Step C of freeze audit)
- Promoting to Stage D (확장 가능한 세계) requires score 3 + meso-scale +
  expansion readiness

---

## 7. Companion files (Priority 3 implementation)

- `scripts/b_direction/run_world_autonomy_probe.py` (empirical
  autonomy verification)
- `docs/b_direction/probe_runs/world_autonomy_probe.json` (results)

---

**End of World-Side Independent Processes formal promotion.
Priority 3 partially complete; full completion requires Priority 4
(world memory layering) for the back-coupling channels.**
