# Spike 5 Part 1 — Progress memo

> **Scope**: Phase 5C (spatial model) + Phase 5A (Jesus agent).
> **Completion date**: 2026-04-22.
> **Rule**: no counterfactual experiments, no intervention JSON
> updates, no paper_data regeneration, no external review packet.

---

## Phase 5C — Spatial model

**Done.** New package `world/space/` with 4 modules:

- `location.py` — `Location` immutable dataclass + `default_locations()`
  returning the 6 canonical AD-30 places (`temple`, `upper_room`,
  `gethsemane`, `praetorium`, `bethany`, `galilee_distant`) + the
  `transit` reserved placeholder. Each location carries three unit-scaled
  scalars (crowd_density / surveillance_level / economic_activity) and a
  `region` tag used by movement cost.
- `position.py` — `AgentPosition` snapshot + mutable `SpatialState`
  (place / begin_move / advance_one_substep / where / agents_at /
  same_location).
- `movement.py` — 2-substep intra-Jerusalem cost, 4-substep cross-region
  cost, overridable via `plan_move(..., override_cost=...)`.
- `rumour_spatial.py` — `spatial_propagation_factor`: 1.5× same-location,
  0.3× cross-location only when a transit agent bridges the pair, 0
  otherwise. Also `visible_state_for` — local-only view of world state
  (information asymmetry primitive).

### Rumour integration

`world.core.world_state.Rumor` gained two optional fields:
`source_location: str | None = None` and `age_in_substeps: int = 0`.
`RumorLayer` carries them forward across ticks and loads them from
`initial_rumors` config entries. Existing public API untouched —
preserves ABSOLUTE RULE #6 and all 62+ existing world tests.

### Tests (`tests/test_world/test_spatial.py`, 16 tests)

All 6 spec-required tests (§3.3) plus 10 supplementary. Highlights:

- `test_agent_at_temple_sees_temple_crowd_density` — visibility primitive
- `test_agent_at_gethsemane_cannot_see_praetorium_directly` — info asymmetry
- `test_rumour_propagates_faster_within_same_location` — same-location 1.5×
- `test_rumour_reaches_distant_location_via_transit_agent` — carrier required
- `test_agent_movement_takes_expected_substeps` — 2-substep move cost
- `test_pilate_receives_galilee_news_with_delay` — carrier enables 0.3×

---

## Phase 5A — Jesus agent

**Done.** Three pieces:

### `content/jesus/` (new content pack)

- `initial_state.json` — Jesus at `galilee_distant` start, low fear,
  high hope/love, `son_of_god` understanding, `shepherd` communal role.
- `behavior_profile.json` — 5 actions, every `visible_signal` cites
  개역개정 directly (Matt 5:3, Mark 1:41, Matt 23:13, Luke 5:16,
  John 21:17). ABSOLUTE RULE #2 (canonical preservation) preserved.

### `content/worlds/jerusalem_ad30/jesus_profile.json`

World-layer tuning (action base weights, bonus thresholds, influence-
path magnitudes) + two canonical constraints:

- day_index 9 → forced `teach` at `temple` (passover_entry)
- day_index 10 → forced `confront` at `temple` (temple_cleanse)

### `world/agents/`

- `base.py` — `BaseWorldAgent` Protocol (runtime_checkable) +
  `WorldAgentContext` + `WorldActionDecision` + `ContentBackedWorldAgent`
  default adapter. Peter/Judas/etc. satisfy the protocol via the
  default adapter — Jesus is the first content-driven subclass.
- `jesus.py` — `JesusAgent` with:
  - `decide(ctx)` / `decide_with_outcome(ctx)` entry points
  - Canonical constraint short-circuit (hard override on the two fixed days)
  - Free-decision weight computation: 5 action weights adjusted by
    disciple understanding, co-located pharisees, crowd density,
    fatigue, co-located suffering
  - **Multi-path influence emitter** (`_ACTION_EMITTERS`): `teach`, `heal`,
    and `bless` all route into `faction_influence_jesus_movement`
    (direct / crowd-testimony / disciple-witness paths) — structural
    insurance against the future `remove_jesus` experiment collapsing the
    faction to a single choke point.

### Tests (`tests/test_world/test_jesus_agent.py`, 10 tests)

All 7 spec tests (§4.4) plus 3 supplementary:

- `test_jesus_teaches_more_when_disciple_understanding_low`
- `test_jesus_withdraws_when_crowd_density_high`
- `test_jesus_heal_at_temple_generates_high_intensity_rumour`
- `test_jesus_confront_pharisees_increases_roman_alertness`
- **`test_jesus_influence_reaches_factions_via_multiple_paths`** —
  asserts ≥3 actions emit into `faction_influence_jesus_movement`. This
  is the single-point-failure-avoidance pin Lee requested in §4.2.2.
- `test_jesus_canonical_event_on_passover_triggers_entry`
- `test_jesus_agent_uses_same_base_interface_as_peter`
- `test_jesus_from_world_profile_path_loads_canonical_constraints`
- `test_all_jesus_visible_signals_cite_korean_scripture` — string match
  "개역개정" in every visible_signal; compliance guard for RULE #2.
- `test_jesus_canonical_event_on_temple_cleanse_forces_confront`

---

## Part 1 completion checklist

- [x] Jesus agent reacts to surrounding state (not canonical-only replay)
- [x] Jesus satisfies the same BaseWorldAgent protocol as Peter's adapter
- [x] ≥3 distinct action paths reach `faction_influence_jesus_movement`
- [x] 6 working locations with distinguishable crowd/surveillance/economy
- [x] Rumours propagate faster within a single location (1.5× vs 0.3×)
- [x] Agents see only their own location directly;
      cross-location info requires a transit carrier
- [x] `1137 → 1163` fast tests green (all existing + 26 new)
- [x] ruff clean on `world/space/` + `world/agents/` + tests
- [x] mypy clean on `world/` (only pre-existing `engine/world.py:268` remains)
- [x] Layer DAG test (ABSOLUTE RULE #9) still green

---

## Deliberate restraint

Per Rule #10, this Part did not:
- add any new `InterventionSpec` or intervention JSON
- touch `docs/world/paper_data/` or regenerate snapshots
- write an external-review packet (SPIKE_5_REVIEW.md)
- extend `BatchInterventionRunner` to expose Jesus
- integrate `JesusAgent.decide()` into `IntegratedWorldRunner`

All those are Part 2 / Spike 7+ scope.

---

## Blocked items surfaced during work

None. Spec §7 block-and-ask conditions did not trigger:
- No ABSOLUTE RULES × requirements conflict.
- 1137 existing tests stayed green throughout.
- No Layer DAG cycle needed (new modules are read-only siblings of
  existing layers, not new tick participants in Part 1).
- 6 locations covered all needed places.
- Jesus canonical constraints cleanly coexist with probabilistic free-
  decision weights (canonical short-circuits first).

---

## Files touched

```
new: world/space/__init__.py
new: world/space/location.py
new: world/space/position.py
new: world/space/movement.py
new: world/space/rumour_spatial.py
new: world/agents/__init__.py
new: world/agents/base.py
new: world/agents/jesus.py
new: content/jesus/initial_state.json
new: content/jesus/behavior_profile.json
new: content/worlds/jerusalem_ad30/jesus_profile.json
new: tests/test_world/test_spatial.py
new: tests/test_world/test_jesus_agent.py
edit: world/core/world_state.py (Rumor fields: source_location, age_in_substeps)
edit: world/social/rumors.py (carry + seed the new Rumor fields)
```

Zero `engine/` edits.
