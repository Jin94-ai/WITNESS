# Spike 5 Part 2 — Progress memo

> **Scope**: Phase 5B (peripheral agents) + Phase 5D (economy enrichment).
> **Completion date**: 2026-04-22.
> **Rule**: no new counterfactual intervention JSON, no paper_data
> regeneration, no external review packet, engine/ untouched.

---

## Phase 5B — Peripheral agents

**Done.** Two Full agents + four Light agents, all behind the same
`BaseWorldAgent` Protocol introduced in Part 1.

### Full agents

- `world/agents/pilate.py` — `PilateAgent` (state: alertness / political_pressure
  / wife_dream_influence; 4 actions: delay_judgment, consult_rome, wash_hands,
  order_action). Two canonical constraints: day 13 wife-dream state_effect,
  day 14 forced wash_hands.
- `world/agents/caiaphas.py` — `CaiaphasAgent` hub (state: sanhedrin_authority
  / roman_relationship / theological_anxiety; 4 actions: convene_sanhedrin,
  appeal_to_rome, temple_decree, confront_movement). Exposes `hub_reaches`
  for behavior-test introspection — `convene_sanhedrin` touches both
  `pharisees` and `sadducees` (hub property).

Both use the multi-path emitter pattern
(`_ACTION_EMITTERS: dict[str, list[tuple[str, str | None]]]`) and the
free-decision-vs-canonical-override short-circuit from Jesus (Part 1).

### Light agents

- `world/agents/light/barabbas.py` — `BarabbasAgent`, active only on
  `canonical_activation_days` (default [14], trial scene). Outside that,
  returns an `idle` no-op.
- `world/agents/light/disciples.py` — shared `_BaseDisciple` + three
  subclasses `JohnAgent`, `JamesAgent`, `ThomasAgent`. Profile axes:
  `theological_understanding`, `confusion_resistance`, `witness_propensity`,
  `political_sensitivity`, `rumour_trust_bias`. Each disciple's profile tilts
  the same 4-action weight (witness / discuss / follow / react_political)
  differently — the structural foundation for later graded-proximity control
  experiments (Spike 7+).

### Content

```
content/worlds/jerusalem_ad30/agents/
  pilate_profile.json      — canonical constraints + emitter magnitudes
  caiaphas_profile.json    — hub channels (pharisees/sadducees overlap)
  light_disciples.json     — shared profiles for John/James/Thomas
  barabbas_profile.json    — canonical_activation_days: [14]
```

### Tests (`tests/test_world/test_pilate_caiaphas_agents.py`, 12 tests)

All 9 spec-required tests (§3.4) plus 3 supplementary. Highlights:

- `test_pilate_delays_judgment_under_political_pressure` — spec #1
- `test_pilate_wash_hands_triggered_by_canonical_constraint` — spec #2
- `test_caiaphas_convenes_sanhedrin_when_theological_anxiety_high` — spec #3
- `test_caiaphas_hub_role_connects_pharisees_and_sadducees` — spec #4
  (≥2 actions reach each faction; `convene_sanhedrin` in both sets)
- `test_barabbas_activates_at_canonical_trial_scene` — spec #5
- `test_john_witness_action_more_frequent_than_thomas` — spec #6
- `test_thomas_rumour_trust_lower_than_james` — spec #7
- `test_james_reacts_to_political_tension_more_than_john` — spec #8
- `test_disciples_differ_in_response_to_same_event` — spec #9
  (graded-proximity foundation: 3 disciples, same context, ≥2 distinct
  action choices)

---

## Phase 5D — Economy enrichment

**Done.** Three independent sub-layers, no `EconomyState` mutation
(Rule #6/#7 preserved), no same-substep feedback (Rule #9 preserved).

### Sub-layers

- `world/economy/temple_economy.py` — `TempleEconomyLayer` (state:
  money_changer_fee, sacrifice_animal_price, temple_tax, crowd_frustration).
  Inputs: `active_feast`, `jesus_cleansing_fired_last_tick`,
  `caiaphas_decree_intensity_last_tick`. Exports `frustration_channel`
  (→ jesus_movement.sympathy, indirect).
- `world/economy/taxation.py` — `TaxationLayer` (state: collection_intensity,
  tax_collector_activity, collection_cycle_day). Input:
  `pilate_political_pressure_last_tick`. Exports `zealot_militancy_channel`
  and `crowd_frustration_channel`.
- `world/economy/cross_economy.py` — `CrossEconomyCoordinator` aggregates
  three channels (temple→jesus_sympathy, taxation→zealot_militancy,
  staple→discontent) as an `EconomyChannels` snapshot. Read-only — each
  sub-layer keeps its own tick.

### Content

```
content/worlds/jerusalem_ad30/economy/
  temple_economy_config.json   — initial_state + dynamics + bounds
  taxation_config.json         — initial_state + dynamics + bounds
```

### Tests (`tests/test_world/test_economy_expansion.py`, 8 tests)

All 8 spec-required tests (§4.4):

- `test_temple_economy_passover_price_spike` — spec #1
- `test_jesus_temple_cleansing_disrupts_money_changer` — spec #2
- `test_caiaphas_temple_decree_adjusts_sacrifice_price` — spec #3
- `test_pilate_political_pressure_raises_taxation_intensity` — spec #4
- `test_taxation_spike_increases_zealot_militancy_channel` — spec #5
- `test_temple_shock_reaches_jesus_movement_via_crowd_frustration` — spec #6
  (indirect path pin)
- `test_three_economies_independent_but_connected` — spec #7
  (each layer evolves independently; coordinator exposes all three channels)
- `test_no_same_tick_feedback_in_economy_layer` — spec #8, ABSOLUTE RULE #9
  guard

---

## Part 2 completion checklist

- [x] Pilate, Caiaphas live as Full agents
- [x] Barabbas, John, James, Thomas live as Light agents
- [x] 3 disciples produce differing responses to the same context
  (graded-proximity foundation)
- [x] Caiaphas hub reaches both pharisees and sadducees
- [x] Temple Economy + Taxation exist as independent modules
- [x] Three economy layers' indirect paths work
- [x] Jesus `confront` / cleansing drops temple fee + sacrifice price
- [x] Pilate `political_pressure` raises taxation intensity
- [x] **1163 → 1176 fast tests green** (all existing + 12 agent + 8 economy
  behavior tests; overlap with Part 1 explains the +13 delta vs +20 new)
- [x] ruff clean on `world/` + `tests/test_world/`
- [x] mypy clean on `world/` (pre-existing `engine/simulation/world.py:268`
  error unchanged per Rule #6 no-engine-edit)
- [x] Layer DAG test (ABSOLUTE RULE #9) still green
- [x] Spike 4 intervention regression (3 interventions) still green

---

## Deliberate restraint

Per Rule #10, this Part did not:

- add any new `InterventionSpec` or intervention JSON
  (no `remove_jesus`, `remove_pilate`, `remove_caiaphas`)
- touch `docs/world/paper_data/` or regenerate snapshots
- write an external-review packet
- wire the new sub-layers into `IntegratedWorldRunner` (Part 3+ scope)
- extend `BatchInterventionRunner` (Part 3+ scope)
- rewire the existing `lenient_pilate` intervention through the new
  `PilateAgent` (pure agent-layer add; the intervention still works on the
  pre-existing `PoliticsState.roman_alertness_floor` path). Spike 4
  regression unaffected.

---

## Blocked items surfaced during work

None. Spec §7 block-and-ask conditions did not trigger:

- No ABSOLUTE RULES × requirements conflict.
- 1163 existing tests stayed green throughout.
- Caiaphas hub did not introduce Layer DAG cycles (agents read factions,
  not the reverse in same-substep).
- Temple Economy ↔ Taxation same-tick feedback avoided — both consume
  *last_tick* inputs.
- `lenient_pilate` intervention regression still passes (politics-layer
  path unchanged; agent addition is additive).
- Light disciple profiles scoped to new JSON file
  (`light_disciples.json`) — zero collision with existing Peter content.

---

## Files touched

```
new: world/agents/pilate.py
new: world/agents/caiaphas.py
new: world/agents/light/__init__.py
new: world/agents/light/disciples.py
new: world/agents/light/barabbas.py
new: world/economy/temple_economy.py
new: world/economy/taxation.py
new: world/economy/cross_economy.py
new: content/worlds/jerusalem_ad30/agents/pilate_profile.json
new: content/worlds/jerusalem_ad30/agents/caiaphas_profile.json
new: content/worlds/jerusalem_ad30/agents/light_disciples.json
new: content/worlds/jerusalem_ad30/agents/barabbas_profile.json
new: content/worlds/jerusalem_ad30/economy/temple_economy_config.json
new: content/worlds/jerusalem_ad30/economy/taxation_config.json
new: tests/test_world/test_pilate_caiaphas_agents.py
new: tests/test_world/test_economy_expansion.py
edit: world/agents/__init__.py (export new agents)
edit: world/economy/__init__.py (export new sub-layers)
```

Zero `engine/` edits. Zero existing-content edits.

---

## Spike 5 total (Part 1 + Part 2)

**Agents (Full, 5):** Jesus, Peter, Judas, Pilate, Caiaphas
**Agents (Light, 4):** John, James, Thomas, Barabbas
**Space:** 6 locations + movement cost + information asymmetry
**Economy:** 3 layers (staple, temple, taxation) + cross-coordinator
**Structural insurance (future experiments):**
- ≥3 action paths into `faction_influence_jesus_movement`
- Caiaphas hub reaches both pharisees and sadducees
- 3 indirect economy paths wired
- Natural 4-level chain proximity (direct / semi / indirect / unrelated)

Experiments: **0 new interventions this spike**. Spike 4's three
interventions remain as regression tests. Experiments resume in Spike 7+.
