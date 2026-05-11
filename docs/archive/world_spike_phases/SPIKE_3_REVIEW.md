# Spike 3 Review Packet — Factions + Rumours + Cross-Layer Chain

> **Audience**: external LLM reviewers (Gemini, ChatGPT, etc.) — same venue
> as [SPIKE_1_REVIEW.md](SPIKE_1_REVIEW.md) and [SPIKE_2_REVIEW.md](SPIKE_2_REVIEW.md).
> **Ask**: §5 has 7 targeted questions. Please answer those and flag any
> modelling or methodological risks you see.
> **Scope under review**: Spike 3 Phase 3A (factions independent) + 3B
> (crowd → zealot militancy) + 3C (rumour graph + seeding pipeline) +
> 3D (rumour → jesus_movement influence). Spike 1 covered world layers
> 1/2/3/5-crowd; Spike 2 covered Person×World integration. This doc
> covers what's new on top.

---

## §1. Context in one page

### 1.1 Where Spike 3 fits

```
Spike 1 (landed)         Spike 2 (landed)             Spike 3 (this doc)
──────────────────       ─────────────────────         ─────────────────────
Layer 1 calendar         Sync Layer plumbing          Layer 4 factions (3A)
Layer 2 economy          IntegratedWorldRunner        Cross-layer: crowd→
Layer 3 politics         world↔agent translation      militancy (3B)
Layer 5 crowd            agent→world WorldEffects     Layer 5 rumours (3C)
                         1 world day = 12 person     Cross-layer: rumour→
                         substeps                     jesus_movement (3D)
```

Tick order (final, DAG-verified by
`tests/test_world/test_layer_dag.py::test_tick_order_is_a_dag`):

```
calendar → crowd → economy → politics → rumours → factions
```

The order is chosen so that every cross-layer edge is same-tick safe
(declared in `describe_dynamics()["causal_dependencies"]`). The
`aggregated_effects` bundle from the SyncLayer is treated as a
previous-world-day pseudo-source; it's whitelisted in the DAG check.

### 1.2 What Phase 3A–3D delivered

- **3A (loop #9)**: `FactionLayer` + `FactionSnapshot`/`FactionState`
  (Tier-3 statistical blocs, not Pydantic agents). 6 AD-30 factions
  (pharisees, sadducees, essenes, zealots, jesus_movement,
  baptist_remnant) with independent influence drift + growth rate +
  Gaussian noise. Clamped to [0, 10].
- **3B (loop #11)**: same-tick edge `crowd.crowd_density ≥ threshold →
  zealot militancy += step·dt`. Threshold brake required by reviewer #2.
- **3C (loop #13, loop #14 activation)**: Layer 5 rumour graph. Each
  `Rumor` carries spread/credibility/age. Update rule reads crowd density
  for spread drive, decays credibility over time, expires by age.
  Seeding comes from `aggregated_effects["rumor_seed"]` (SyncLayer
  THRESHOLD aggregation). **Fixed bug**: Korean visible_signal didn't
  match English rumour-keyword list, so sync mapping also scans
  `action_id` (always English per engine convention).
- **3D (loop #15)**: same-tick edge
  `rumors.active_intensity · rumor_gain · dt →
  rumor_sensitive_factions` (default `{jesus_movement}`). The chain
  Judas → rumour → jesus_movement is closed.

### 1.3 Constraints honoured

- **Engine unchanged**: 1003 Person-Engine tests remain green.
- **Every cross-layer edge has a brake** (threshold / saturation / delay /
  age expiry); `describe_dynamics()["brake_type"]` records which.
- **Optional layers**: a caller can omit `faction_layer` / `rumor_layer`
  and the rest of the world still ticks — Spike 1+2 demos unchanged.
- **DAG rule #9**: all same-tick deps point to already-ticked layers;
  any back-edge must be marked `@prev_tick`.

---

## §2. Architecture delta

### 2.1 Updated layer dependencies

```
calendar    (deterministic, no deps)
crowd       ← calendar.pilgrim_influx_target
economy     ← calendar.pilgrim_influx_target      (+3-day IIR delay)
politics    ← calendar.active_feast, calendar.days_to_next_passover,
              crowd.crowd_density                 (+threshold on density)
rumours     ← crowd.crowd_density (drive),
              aggregated_effects.rumor_seed       (+age expiry, cred decay)
factions    ← crowd.crowd_density (→ zealot militancy, threshold),
              rumours.active_intensity (→ jesus_movement influence)
```

The Sync Layer sits over the top: before each world tick it hands in
`aggregated_effects` from the prior world day, then runs Person-Engine
substeps against the EnvironmentState derived from the new WorldState.
Spike 3 did not change the Sync Layer except for the action→effect
mapping fix in §1.2.

### 2.2 Folder deltas (Spike 3 only)

```
world/
├── core/world_state.py        + Rumor, RumorState, FactionSnapshot/State, RomanStance
├── factions/
│   └── factions.py            NEW — FactionLayer (Phase 3A + 3B + 3D)
├── social/
│   └── rumors.py              NEW — RumorLayer (Phase 3C)
└── simulation/
    └── world_tick.py          +faction_layer, +rumor_layer (both optional)

content/worlds/jerusalem_ad30/world_config.json
                              + factions_config (6 factions)
                              + rumors_config (spread/decay params)

tests/test_world/
├── test_factions.py           NEW — 18 tests (Phase 3A independent,
│                                    3B edge, 3D edge, DAG, WorldTick)
├── test_rumors.py             NEW — 12 tests (shape, dynamics, expiry,
│                                    seeding, aggregation helper, DAG)
├── test_layer_dag.py          +rumors/factions in TICK_ORDER
└── test_world_numbers_scripts.py  +Phase 3B + 3D content-level pins

scripts/
├── world_numbers.py           +faction influence mean, zealot militancy
│                              trajectory, rumour metrics
└── world_figures.py           (unchanged in Spike 3 — could be extended)
```

---

## §3. Empirical behaviour (seed 0–2, 90 days, AD-30 content)

### 3.1 Phase 3A agent-less faction drift

From `docs/world/paper_data/world_numbers.json::spike1_world_only`:

| Faction           | Target | 90-day mean | Note |
|-------------------|:------:|:-----------:|------|
| pharisees         |  6.0   | 6.06        | stable |
| sadducees         |  5.0   | 5.01        | stable |
| essenes           |  1.5   | 1.52        | isolated, tau=90d |
| zealots           |  2.5   | 2.99        | growth_rate +0.01/day |
| **jesus_movement**|  3.0   | **3.90**    | growth_rate +0.03/day |
| baptist_remnant   |  0.2   | 0.40        | decaying toward 0.2 |

With no rumours (agent-less), jesus_movement settles at target + 30 · 0.03 ≈ 3.9.

### 3.2 Phase 3B militancy signature

| Metric | Value (5-seed mean) |
|---|---|
| militancy_threshold_hits | 12 (crowd ≥ 5 for 12 days) |
| zealot_militancy_max | 9.25 |
| zealot_militancy_at_passover | 8.00 |

Zealot militancy rises during Passover (crowd ≥ threshold) then decays
when the city empties. The effect is zealot-specific; other factions'
militancy remains a flat noise walk.

### 3.3 Phase 3D counterfactual chain

This is the headline Spike 3 result. From `spike2_integrated_peter` vs
`spike2_judas_removed` (3-seed mean, 90 days):

| Metric | Full (4 agents) | Judas removed | Δ |
|---|:---:|:---:|:---:|
| trigger_count | 212 | 77 | **−64%** |
| rumours seeded | 77 | **0** | **−100%** |
| rumor_intensity_max | 12.0 | **0** | **−100%** |
| jesus_movement final influence | **9.90** | **3.80** | **−62%** |
| pharisees final influence (control) | 6.18 | 6.18 | 0% |
| Peter final fear | 9.90 | 9.59 | −3% (saturation) |

Two independent validations of the chain:
1. **rumours=0 without Judas** — because only Judas's `inform_authorities`
   / `betray` actions trigger the rumour-keyword scan.
2. **jesus_movement falls back to Phase-3A baseline (3.80 ≈ 3.79)**
   while pharisees is unchanged → the rumour→faction edge is specific,
   not a global noise floor shift.

Both findings are now pinned:
- `test_phase_3b_content_behaviour_pin`
- `test_phase_3d_judas_removal_collapses_jesus_movement_influence`
  (requires ≥40% jesus_movement drop and <20% pharisees drift).

### 3.4 Test / quality counts

- **1118 fast tests green** (1003 person-engine + 115+ world)
- **ruff world/ tests/ scripts/**: all clean
- **mypy world/**: no issues on 22 source files
- Spike 1+2 tests completely unchanged

---

## §4. Known trade-offs and limits

| Issue | Mitigation now | Future |
|-------|----------------|--------|
| Rumour seed uses keyword scan on action_id | works for current English action_ids | Phase 3E should let content declare `world_effect_emitters` explicitly per AgentAction |
| jesus_movement saturates at ceiling 10 in integrated mode | `overflow_pressure`-style raw field not yet added to factions | needed for "engine is driving at ceiling" differentiation — analogous to Spike 2 A-2 |
| Only Judas seeds rumours | Content-specific; no Peter action contains the keyword list | Phase 3E+ adds more scripture-anchored rumour sources (temple cleansing, healing) |
| Rumour content is templated (`seed_content` string) | single-valued; all seeds create same `"agent_emitted_rumor"` text | Phase 3F adds action→content mapping per agent |
| Faction influence isn't fed BACK to engine's EnvironmentState | No path from faction → agent fear | Phase 3G: Sync Layer extended percept with `jesus_movement_visibility` |
| Fear / alertness saturate at ceilings | Compare mid-run snapshots only; final-value tests are uninformative | Add raw-value overflow fields per Spike 2 A-2 lesson |

---

## §5. Questions for the reviewer

### Q1. Same-tick rumour → faction edge

Rumours are ticked before factions in the same world day. A rumour
seeded by yesterday's agents (via `aggregated_effects`) thus influences
today's faction influence growth with a 0-day lag. Is the 0-day lag
correct for the "rumour spreads and persuades" narrative, or should we
insert a 1-tick delay (`@prev_tick`) so that a rumour must "settle" one
world-day before it shifts influence? We lean toward keeping
same-tick — the Sync Layer already introduced a 1-day latency between
an agent's action and the rumour's arrival. But we'd welcome a sanity
check on double-lag vs single-lag.

### Q2. Specificity of the jesus_movement edge

The rumour-sensitivity set `{jesus_movement}` is content-configured.
Only one faction is boosted; pharisees is the explicit control. Should
we (a) expand the set to `{jesus_movement, zealots}` since rumours of
betrayal would plausibly lift militant opposition too, (b) add a
faction-specific gain vector rather than a shared `rumor_gain`, or (c)
keep it minimal pending reviewer input? The current design is (c).

### Q3. Rumour expiry + content pack coupling

`RumorLayer` garbage-collects a rumour when `age_days > max_age_days`
(default 30) OR when both spread and credibility are ≈ 0. With
AD-30 feast density the rumour pool reaches ~10–15 active rumours in
peak. Is 30 days the right cap? The historical half-life of a rumour
in a pre-literate agrarian city is ... we frankly don't know. Would
you recommend:
- keeping 30 days as a placeholder,
- tightening to 14 days (approximating one feast cycle),
- letting content override per-rumour (`max_age_days` in seed config)?

### Q4. Rumour seed intensity vs one-per-day cap

Currently every world day in which ≥ 1 agent emits a rumour-keyword
action → one new rumour (because the `rumor_seed` channel is THRESHOLD
at 0.5, collapsing N emitters to a single 1.0 signal). The cap hides
the "many agents telling the same rumour amplifies it" dynamic. Should
we switch rumor_seed to `sum` aggregation and pass the magnitude into
the new rumour's initial spread? If so, at what scaling?

### Q5. Counterfactual specificity threshold

The pin test requires:
- jesus_movement drop ≥ 40% when Judas is removed
- pharisees drift < 20% across the same removal

Is 40/20 the right ratio for "specific, not global noise"? The
empirical observations are 62%/0%, so we have 22 pp headroom. If you
think the threshold should be tighter (e.g., 50%/10%), we can raise
it — the cost is brittleness under future content tuning.

### Q6. Phase numbering / roadmap

Our working assignment:

- Phase 3A — factions independent dynamics
- Phase 3B — crowd → zealot militancy (first cross-layer edge)
- Phase 3C — rumour graph + seeding pipeline
- Phase 3D — rumour → jesus_movement influence
- Phase 3E (planned) — explicit content-side emitter declaration
- Phase 3F (planned) — per-action rumour content mapping
- Phase 3G (planned) — faction influence back into agent EnvironmentState

Is this phase staircase sensible? Which missing piece would you move
earlier?

### Q7. "Engine universality" status after Spike 3

`CLAUDE.md` ABSOLUTE RULE #5 permits "engine universality" after the
Talleyrand scenario demonstrated POM scorecard asymmetry on the v0.5
engine. Spike 3 is built on top; no second scenario has been adapted
to the world engine yet. Should we (a) wait for a second
world-engine scenario (e.g., `content/worlds/arles_1888/`) before
re-asserting "engine universality" for v2.0, or (b) claim the scope
narrowly — "the AD-30 world engine accommodates the 4-layer world
dynamics without modification" — pending a second world? We lean (a).

---

## §6. How to verify

```bash
# Regenerate snapshot (3.3s).
python scripts/world_numbers.py

# Render figures (world_figures.py is Spike 1+2-scoped — Phase 3 figures TODO).
python scripts/world_figures.py

# Full world-engine test suite (116 tests).
pytest tests/test_world/ -q

# Content-level Phase 3B + 3D counterfactual pins.
pytest tests/test_world/test_world_numbers_scripts.py \
    -k "phase_3b or phase_3d" -v

# Full regression — Person Engine unaffected by Spike 3.
pytest -m "not slow and not archived" -q
```

Canonical numbers live in
[docs/world/paper_data/world_numbers.json](paper_data/world_numbers.json).
The `spike2_integrated_peter.aggregate` and `spike2_judas_removed.aggregate`
dicts are the direct counterfactual comparison for §3.3.

---

## §7. Output format we would prefer

```
## §5 answers
Q1. …
Q2. …
…
Q7. …

## §4 table additions / corrections
- New issue: …
  - Symptom: …
  - Proposed mitigation: …

## Overall judgement
Spike 3 is ready to close and move to Spike 4 (variable-intervention
experiments): YES / NO / CONDITIONAL
Conditions (if any): …
```

Thanks for the critical read.
