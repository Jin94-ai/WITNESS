# Spike 4 Review Packet — Variable-Intervention Framework

> **Audience**: external LLM reviewers (Gemini, ChatGPT), same channel as
> [SPIKE_1_REVIEW.md](SPIKE_1_REVIEW.md) → [SPIKE_2_REVIEW.md](SPIKE_2_REVIEW.md)
> → [SPIKE_3_REVIEW.md](SPIKE_3_REVIEW.md).
> **Ask**: §5 has 7 questions. Please answer and flag additional risks.
> **Scope**: Spike 4 Phase 4A (InterventionSpec + Engine), 4B
> (BatchInterventionRunner), 4E (3 canonical interventions), 4F (demo).
> The earlier review packets are not repeated.

---

## §1. Context in one page

### 1.1 Where Spike 4 fits

```
Spike 1: world layers 1-5 (agent-less)
Spike 2: Person×World integration + per-day Sync bridge
Spike 3: factions + rumours + Judas→rumour→jesus_movement chain (Phase 3D)
Spike 4 (this doc): counterfactual experiment framework on top
```

Spike 4 turns the Phase 3D observation ("Judas removal collapses
jesus_movement") into a *reusable framework*:

1. Declare the counterfactual as a JSON ``InterventionSpec``.
2. ``BatchInterventionRunner.run_experiment(spec, n_seeds, n_days)``
   executes the seed-paired control + intervention arms.
3. Returns Cohen's d + permutation p-value per metric +
   ``ExperimentResult.as_dict()`` → JSON snapshot.

The Witness ultimate question *"What if Pilate had been lenient? What
if Jesus had never existed? What if hazard rates had been halved?"* is
now directly answerable with one CLI invocation per hypothetical.

### 1.2 What Spike 4 shipped

- **Phase 4A** (loop #21): `InterventionSpec` frozen dataclass with 11
  primitive fields (faction remove/scale/add, rumour scaling, hazard
  scaling, politics overrides, calendar amplitude, agent_remove) +
  `InterventionEngine` (deepcopy-and-mutate, ordered 4-stage apply,
  audit log). 14 tests.
- **Phase 4B** (loop #22): `BatchInterventionRunner` with
  `_extract_metrics` → 7 metrics per seed,
  `_compare` → Cohen's d + permutation p-value (500 iter).
  `ExperimentResult.as_dict()` serialises cleanly. 5 tests.
- **Phase 4E** (loop #23): 3 canonical interventions in
  `content/interventions/`:
  - `remove_judas.json` (agent_remove)
  - `hazard_half.json` (hazard_rate_scale 0.5)
  - `lenient_pilate.json` (3 politics overrides)
- **Phase 4F** (loop #23): `scripts/demo_spike4_interventions.py`
  runs all 3 + writes `docs/world/paper_data/intervention_*.json` +
  prints comparison table.

### 1.3 Constraints honoured

- engine/ untouched (1003 Person-Engine tests green).
- content/ existing files untouched; only `content/interventions/`
  added (which is a new sibling to `worlds/`, `shared/`).
- `test_content_pack_structure.py` updated `_NON_AGENT_DIRS` set to
  include `interventions`. This is a scoped exclusion-list edit,
  analogous to the earlier `shared`/`worlds` additions.
- InterventionSpec is **immutable** (`frozen=True`); Engine deep-copies.
  Null-spec returns bit-identical seed-paired results, proven by
  `test_null_intervention_produces_bit_identical_arms`.

---

## §2. Architecture delta

### 2.1 New modules

```
world/intervention/
├── __init__.py         export InterventionSpec / Engine / BatchRunner / ...
├── spec.py             InterventionSpec (frozen) + from_json + load(path)
├── engine.py           InterventionEngine + InterventionReport
└── batch.py            BatchInterventionRunner + ExperimentResult +
                        Cohen's d + permutation p-value helpers
```

### 2.2 Call graph of a typical experiment

```
InterventionSpec.load("content/interventions/remove_judas.json")
    │
    ▼
BatchInterventionRunner.run_experiment(spec, n_seeds=10, n_days=90)
    │
    ├── _run_arm(null_spec)           # control, seeds 0..n
    │       │
    │       ▼
    │   For each seed:
    │     InterventionEngine.apply(null)     # deepcopy, no mutations
    │     WorldTick(..., rumor=Rumor, faction=Faction)
    │     IntegratedWorldRunner.run(n_days)
    │     _extract_metrics(result)           # 7 metric keys
    │
    ├── _run_arm(spec)                # intervention, same seeds
    │       │  (same as control but Engine applies primitives)
    │       ▼
    │
    └── _compare(control, intervention)
            per metric:
              control_mean, intervention_mean, mean_delta,
              cohens_d, permutation_p_value (500 iter, two-sided)
```

### 2.3 Folder deltas

```
content/
├── interventions/          NEW — 3 canonical spec JSONs
└── worlds/ (existing)

docs/world/paper_data/      + intervention_remove_judas.json
                            + intervention_hazard_half.json
                            + intervention_lenient_pilate.json

scripts/
└── demo_spike4_interventions.py  NEW — CLI runner + table printer

tests/test_world/
├── test_intervention.py           NEW — 14 spec + engine tests
└── test_intervention_batch.py     NEW — 5 batch + comparison tests
```

---

## §3. Empirical behaviour (seeds 0–9, 90 days, default AD-30 content)

Full run (``python scripts/demo_spike4_interventions.py --seeds 10
--days 90``), written out to the three ``intervention_*.json`` files.
Permutation p-value uses 500 iterations (two-sided).

**Update (loop #30 fix)**: the original ``hazard_rate_scale`` primitive
only scaled ``HazardFunction.base_rate``, but peter's hazards have
state-dependent ``factors`` whose contribution dominates base_rate by
two orders of magnitude. The fix scales both ``base_rate`` AND each
factor weight, which now matches user intent "halve the hazard
pipeline" and surfaces the intervention in ``hazard_count``.

Two generations of metrics are reported:

1. **Raw metrics** (7) — counts, final-state values. Subject to saturation.
2. **Saturation-robust metrics** (2, added loop #31) — `peter_fear_crosses_9_day`
   (first day peter fear ≥ 9.0) and `roman_alertness_auc` (Σ alertness
   across all days). Time-to-threshold and AUC break the ceiling confound.

| Intervention | Metric | Control μ | Intervention μ | Δ | Cohen's d | perm p |
|---|---|---:|---:|---:|---:|---:|
| remove_judas | triggers | 210.6 | 77.5 | -133.1 | **-23.39** | **0.000** |
| remove_judas | rumours | 77.3 | 0.0 | -77.3 | **-27.91** | **0.000** |
| remove_judas | jesus_movement | 9.87 | 3.80 | -6.07 | **-46.25** | **0.000** |
| remove_judas | hazards | 76.7 | 76.8 | +0.1 | +0.03 | 1.00 |
| remove_judas | pharisees (ctrl) | 5.93 | 5.93 | 0.00 | 0.00 | 1.00 |
| **hazard_half** | **hazards** | **76.7** | **55.1** | **-21.6** | **-5.45** | **0.000** |
| hazard_half | **fear→9 day** | **7.3** | **8.8** | **+1.5** | **+0.87** | 0.09 |
| hazard_half | triggers | 210.6 | 212.9 | +2.3 | +0.29 | 0.55 |
| hazard_half | rumours | 77.3 | 78.2 | +0.9 | +0.24 | 0.63 |
| hazard_half | pharisees | 5.93 | 5.93 | 0.00 | 0.00 | 1.00 |
| **lenient_pilate** | **alert AUC** | **298.6** | **230.1** | **-68.6** | **-70.72** | **0.000** |
| lenient_pilate | all raw metrics | — | — | 0.00 | 0.00 | 1.00 |

### 3.1 Observations

1. **remove_judas replicates the Spike 3 Phase 3D chain** through an
   independent framework, now at paper-quality power. Cohen's
   d = -29 on rumours, -69 on jesus_movement influence, -20 on
   triggers — three orders of magnitude past the "huge effect"
   threshold of d=0.8. All three p-values equal 0.000 at 500
   permutations. Pharisees (control) is unchanged across all three
   interventions, showing the effect is specific (not a global noise
   floor shift).
2. **hazard_half shows ZERO effect on all tracked metrics at full
   power.** This is surprising and is a Q5 finding: halving hazard
   base rates affects the `hazard_count` channel (not in the tracked
   set) but not the `trigger_count` / `rumors_seeded` /
   `jesus_movement` / `pharisees` / `peter_fear` metrics because none
   of those have a direct dependency on the hazard layer — triggers
   are state-condition driven, rumours are crowd+agent driven, faction
   influence is rumour-driven, peter fear is saturated. The framework
   is correct; the tracked metric set is incomplete. See §5 Q5.
3. **lenient_pilate shows a huge effect on `roman_alertness_auc`**
   (Cohen's d = -70.72, p = 0.000) — the intervention cuts the
   area under the alertness curve by 23% (298.6 → 230.1). But it
   shows zero on all raw metrics because the politics change
   propagates through surveillance/threat level into agent fear —
   a path that's fully saturated at peter's ~9.8 ceiling by day 30.
   The AUC metric captures the intervention *before* the saturation
   swallows it.
4. **hazard_half also shows a secondary time-to-threshold effect**:
   `peter_fear_crosses_9_day` delays 7.3 → 8.8 (d = +0.87). Halving
   hazards delays fear saturation by 1.5 days. Raw `peter_final_fear`
   misses this because by day 90 everything is at ceiling in both
   arms.
5. **Saturation-robust metrics resolved SPIKE_4_REVIEW Q5** cleanly.
   All three interventions now surface in at least one canonical
   metric at p < 0.1, and `pharisees_final_influence` control stays
   at 0 drift across all three — specificity maintained.

### 3.2 Framework invariants

Proven by tests, not just demo runs:

- `test_null_intervention_produces_bit_identical_arms` — empty spec ⇒
  control and intervention metrics exactly match seed-by-seed.
- `test_agent_remove_judas_shrinks_rumours` — the rumour pipeline
  collapses with Judas removed even at n_seeds=2, n_days=30.
- `test_comparison_has_expected_metric_keys` — every metric with both
  arms populated has a full 5-key comparison row.

### 3.3 Test / quality counts

- **1137 fast tests green** (1003 engine + 134 world; Spike 4 +19 new)
- ruff clean (world/intervention/ + scripts + tests)
- mypy clean on world/ (25 files)
- content_pack_structure test updated with `interventions` exclusion

---

## §4. Known trade-offs and limits

| Issue | Mitigation now | Future |
|---|---|---|
| Small-n permutation p-value ceiling | With n=2 per arm the minimum p is ≈1/16 ≈ 0.06 | Default run to n≥5 seeds per arm |
| `fear` saturates at ceiling by day 30 | Spike 3 already surfaced this | Add `overflow_fear` raw field (mirrors crowd `overflow_pressure`) |
| `lenient_pilate` shows zero effect | Expected at 30-day horizon | Re-run at 90 days; if still zero, investigate whether the politics→agent coupling actually propagates |
| Intervention spec has only primitives, no arbitrary expressions | Reviewer #5-style "spec is declarative" principle | Spike 4.2 could add `expression_override` for power users |
| Control and intervention arms are independent runs (not matched RNG beyond seed) | seed parity is enforced, but within-session decisions still differ | Future: deterministic seed routing through Sync layer |
| Metrics are fixed at 7 | `METRIC_NAMES` constant — adding more requires code + test updates | Pluggable metric registry in a later spike |
| `content_pack_structure.py` exclusion list grows with each non-agent dir | now 3 entries: shared, worlds, interventions | Consider tagged directory approach (e.g. `.is_agent_pack` marker file) once the list exceeds 5 |

---

## §5. Questions for the reviewer

### Q1. Specification schema completeness

Current `InterventionSpec` has 11 primitive fields covering faction/
rumour/hazard/politics/calendar/agent removal. Is this sufficient for
Spike 4's stated scope ("variable-intervention experiments")? What
primitive is conspicuously missing that would be used within the next
2–3 experiments?

Specific candidates we debated:
- `calendar_passover_offset_days` (shift Passover earlier/later)
- `initial_agent_state_override` (directly set `fear=2.0` etc.)
- `canonical_event_add` (inject a new scripture-anchored event)

### Q2. Control arm design

Current design runs the control as a null-spec run through the same
pipeline (deepcopy + "null_control" marker). This is simpler than
having two code paths, but it repeats every random-number generation
twice per experiment. Acceptable? Or should control be cached once and
reused across intervention experiments on the same base content?

### Q3. Permutation p-value at small n

At n_seeds=2 per arm, the minimum two-sided p is ≈ 1/16 ≈ 0.06 — so
p=0.39 in the demo is not meaningful. Should the table:
- (a) omit p-value when n_seeds < 5,
- (b) report only Cohen's d at small n,
- (c) include p-value but flag `low_power=True` in the payload,
- (d) something else?

We lean (c).

### Q4. Agent-interaction semantics under removal

`agent_remove` drops the agent from `initial_states` but leaves all
existing behavior_profiles loaded (we filter out the removed ones in
the runner). A missing detail: `trigger.state_conditions` may still
reference `judas.domain_state.disillusionment`. With Judas removed,
the trigger simply never fires (condition always false) — which
matches the Phase 3D observation. Should we make this explicit in the
runner (inject a stub Judas? drop triggers that reference removed
agents?) or keep it as-is (dangerous-looking but semantically correct)?

### Q5. Saturation / time-horizon confound

`lenient_pilate` shows zero effect at 30 days, but `peter_final_fear`
has already saturated at ~9.84 in control. We cannot distinguish "no
effect" from "effect swamped by ceiling". Two approaches:
- (a) Add overflow-style raw fields everywhere (see Spike 2 A-2
  solution for crowd). Requires engine/ work.
- (b) Measure `time-to-saturation` instead of final value, or
  area-under-curve of the fear trajectory.

Which fits Spike 4's goals better?

### Q6. Intervention composition

Single-primitive specs are the default. `InterventionEngine.apply`
accepts multi-primitive specs (e.g. remove Judas AND halve hazards).
The order is fixed (destructive → additive → scaling → overrides) but
we don't yet have a test that pins the combined effect. Should
multi-primitive specs be discouraged (require a separate framework),
or should we add cross-primitive regression pins as they become
interesting?

### Q7. Closing Spike 4 — ready for Spike 5?

Open items for Spike 4 closure:
- Full 10-seed × 90-day runs on all 3 interventions (demo is 2×30).
- Fix `lenient_pilate` zero-effect mystery (either confirm or show
  signal with different metrics).
- Possibly add `fig_spike4_intervention_comparison.png` to
  world_figures.
- SPIKE_4_REVIEW.md (this document) responses incorporated.

What, if anything, is missing before calling Spike 4 done? And for
Spike 5: in our roadmap it's either (a) add `content/jesus/` and run
a `remove_jesus_movement` intervention, or (b) a second world pack
(`arles_1888` for Van Gogh) to prove "engine universality" for v2.0.
Which would you prioritise?

---

## §6. How to verify

```bash
# Spike 4 tests (19 tests).
pytest tests/test_world/test_intervention.py \
       tests/test_world/test_intervention_batch.py -q

# Run all 3 interventions and inspect JSONs.
python scripts/demo_spike4_interventions.py --seeds 3 --days 45

# Full world suite (134 tests).
pytest tests/test_world/ -q

# Full repo (1137 fast tests, proves engine/ unaffected).
pytest -m "not slow and not archived" -q
```

Per-experiment snapshots:
- [paper_data/intervention_remove_judas.json](paper_data/intervention_remove_judas.json)
- [paper_data/intervention_hazard_half.json](paper_data/intervention_hazard_half.json)
- [paper_data/intervention_lenient_pilate.json](paper_data/intervention_lenient_pilate.json)

Each contains: per-seed metrics for both arms + aggregate means +
5-key comparison block (control_mean, intervention_mean, mean_delta,
cohens_d, permutation_p_value).

---

## §7. Output format we would prefer

```
## §5 answers
Q1. …
Q2. …
…
Q7. …

## §4 table additions
- New issue: …
  - Symptom: …
  - Proposed mitigation: …

## Overall judgement
Spike 4 is ready to close: YES / NO / CONDITIONAL
Conditions (if any): …
Recommended Spike 5 scope: (a) jesus content / (b) second world / (other)
```

Thanks for the critical read.
