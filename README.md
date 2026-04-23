# Witness (v1.2)

> **Ultimate vision**: A narrative simulator where the player experiences a historical figure's life as a witness.
> Multi-agent + trigger-mediated + hazard-driven. Learn from simulation to construct life trajectories.
> Ask: **"What was the moment that made the difference?"**

---

## What it does

Witness simulates historical figures as interacting agents in a stochastic process. Events don't happen at fixed times — they emerge from agent interactions, internal state accumulation, and environmental pressure. Run thousands of times with varied parameters, and observe which paths emerge, which conditions produce which outcomes, and where the bifurcation points are.

**Peter scenario**: 4 agents (Peter + Judas + Caiaphas + Crowd). Arrest emerges from Judas's disillusionment accumulation → betrayal → arrest trigger. v1.2 extends to 5-phase 3-year public-ministry arc (calling → Galilean ministry → confession+transfiguration → journey → passion).

**Van Gogh scenario**: 3 agents (Van Gogh + Gauguin + Theo). Gauguin's departure emerges from frustration accumulation → departure trigger.

**Talleyrand scenario** (v1.2, third-scenario universality proof): 1 agent navigating 6 French regime transitions (1789–1830). Distinct dynamics type — regime-driven rather than emotion-driven — demonstrating engine neutrality. See `REVIEW_RESPONSE_V1_2.md` §6 and Paper Draft §Appendix E.

All three use **identical engine code**. Only `content/` differs.

## Version roadmap (v0.7)

| Version | Focus | Status |
|---------|-------|--------|
| v0.5 | Rule-based symbolic simulator + validation framework | Complete |
| v0.6 | Paper draft — 8–10 core findings consolidated | In progress |
| v0.7 | Trace pipeline (§2 entries) + player view filter + drive hooks | Complete |
| v1.0 | Predictive latent drive bottleneck (PyTorch training) | **Stage 2 in progress** (LDA-based first learned encoder; PyTorch MLP next) |
| v1.1 | Relational graph (node drive + edge tension) | Planned |
| **v1.2 (current)** | **Phase-linked continuous life + Talleyrand 3rd scenario + Stage 2 bridge** | **5-phase arc + universality proof + LearnedLinearEncoder** |
| v2.0 | Narrative Witness renderer (player experience) | Planned |

See `DESIGN.md` for full roadmap; `DESIGN_LATENT_DRIVE.md` for v1.0 architecture.

## Quick start

```bash
python -m venv venv && source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt

# Peter multi-agent (4 agents, 100 runs)
python main.py --multi

# Van Gogh multi-agent (3 agents)
python main.py --multi --person vangogh --runs 50

# v0.7 trace pipeline demo (sim → trace → player view → JSONL → narrative)
python demo_v07.py --scenario peter
python demo_v07.py --scenario vangogh --seed 0

# v1.2 phase-linked arc demo (Peter 공생애, absolute-time output)
python demo_phased.py --seed 0                 # 4-phase (~101 days, 2 agents)
python demo_phased.py --seed 0 --full-passion  # 5-phase + legacy 500-tick passion (~143 days, 4 agents)
python demo_phased.py --with-recovery          # opt-in slow state recovery rule
python demo_phased.py --show-drive --encoder learned  # v1.0 Stage 2 LDA encoder + drive trajectory

# Legacy comprehensive demo
python demo.py --quick

# Single-agent mode (legacy)
python main.py --person peter
python main.py --person vangogh --runs 50

# Tests
pytest -m "not slow and not archived"  # 1003 fast tests (~65s)
pytest -m archived                     # 33 Tier 3 archived tests
pytest                                 # all ~1167 tests
```

## v1.2 Phase-linked life architecture (new in this version)

Peter scenario extends from the 50-day passion to a 3-year public ministry arc (소명 → 갈릴리 → 고백/변화산 → 여정 → 수난). Two interoperable modes:

- **legacy-phase5**: `phases=None` → the original v0.7 500-tick scenario, bit-exact preserved (arrest 100%, Cohen's d=-6.87, sword_drawn Phi=0.95 all intact).
- **linked-life**: `phases=[01..05]` → full arc with state handoff between phases. `PhaseHandoffSpec` carries slow state (moral_injury, event_trauma, identity_shift, trust_scar) forward + explicit field mapping for fast state (emotions, obedience_maturity).

| Module | Purpose |
|--------|---------|
| `engine/core/phase.py` | `Phase`, `PhaseExitCondition`, `PhaseHandoffSpec`, `FieldMapping` |
| `engine/simulation/phased_world.py` | `PhasedSimulationWorld`, `PhasedMultiAgentResult`, per-phase `canonical_events_path` loading |
| `engine/simulation/time_axis.py` | Absolute-hours coordinates (`ticks_to_absolute_hours`, `extract_field_trajectory_absolute`) |
| `engine/rules/inhibitor.py` | `FieldAttenuationRule` + `FieldAmplificationRule` — content-configurable cross-agent field dynamics |
| `engine/rules/slow_recovery.py` | `SlowStateFieldRecoveryRule` — opt-in field-specific slow state recovery (moral_injury/trust_scar/identity_shift; event_trauma intentionally excluded per PTSD model) |
| `HazardFunction.base_rate_unit` | `"per_tick"` (legacy default) or `"per_hour"` (phase-variable Poisson rate) |

All engine rules are `dt_hours`-aware via `RuleContext.dt_hours`, so per-hour rates behave consistently across phases with different `tick_scale_hours` (e.g., 2h/tick dense phases vs 24h/tick sparse phases).

## Third scenario and universality (v1.2 Iter 54–57)

**Talleyrand** (`content/talleyrand/`): a regime-driven scenario spanning 1789–1830 (ancien régime → revolution → directory → consulate → empire → bourbon restoration → July monarchy). Distinct from Peter (emotion-driven rare-action bottleneck) and Van Gogh (isolation-breakdown) — the engine handles all three without modification. Cross-scenario POM scorecard asymmetry (Talleyrand-on-Peter = 0%, Talleyrand-on-Talleyrand ≥ 80%) grounds the scope-limited claim: *engine is scenario-agnostic, patterns are scenario-specific*. Full writeup in `REVIEW_RESPONSE_V1_2.md` and `PAPER_DRAFT_V06.md` Appendix E.

## Stage 2 bridge: first learned encoder (v1.2 Iter 72–74)

`engine/core/latent_drive.py::LearnedLinearEncoder` uses sklearn Linear Discriminant Analysis to produce a *learned* state→drive projection (random baseline → 1.25× improvement on Peter). Opt-in via `TrainingConfig(use_learned_linear=True)` or `demo_phased.py --encoder learned`. Next step: PyTorch MLP encoder (requires `torch` install). Feasibility spectrum per scenario: VG 6.04 / Peter 1.91 / Talleyrand 0.05–0.07 (deferred — policy gap identified in Iter 69).

## Key findings

| Finding | Evidence |
|---------|----------|
| Arrest emerges from agent interaction | 100/100 runs 100% spontaneous (n=100 replication, not tick-fixed) |
| Arrest tick varies across seeds | mean 199, std 42.5, range [116, 287] (unimodal per Hartigan/BIC) |
| Threshold-triggered regime switch | disillusionment ~8 — below: deadline-dependent. Above: spontaneous |
| Causal bottleneck | surveillance → betray (63 ± 30 ticks) |
| Counterfactual (Judas removal) | Cohen's d = −6.87, permutation p < 0.001 |
| Crowd effect | +0.62 fear, −24 tick arrest timing |
| Trigger robustness | +20% threshold → 44 tick delay, not failure |
| Engine generality | Peter AND Van Gogh: identical engine, isomorphic POM bottleneck (sword_drawn ↔ self_harm, Phi>0.95) |
| Cross-scenario distribution | KS D=0.567 (α=0.01): surface timing differs, deep structure isomorphic |
| Forecast accuracy | disill@200 → 86% [78%, 91%] (n=100), partial holdout test 89% |
| Behavioral signal precedes state | withdraw rate r=−0.94, noise-robust across σ∈[0, 0.2] |

## How it works

### Multi-agent simulation

```
SimulationWorld (per tick):
  1. AgentScheduler: determine activation order
  2. Each agent: select voluntary action from BehaviorProfile
  3. Apply cross-agent effects (StateEffect.target_agent_id)
  4. TriggerEngine: evaluate state/action conditions -> generate events
  5. HazardEngine: probabilistic event firing
  6. RuleEngine: apply state transition rules
  7. Environment dynamics
```

### Hazard-driven events

```
hazard = f(fear, fatigue, surveillance, crowd_pressure, ...)
P(event) = 1 - exp(-hazard * dt)
```

### Trigger system

```
TriggerCondition: agent_A.disillusionment >= 8.0
ActionTriggerCondition: agent_A performed "betray"
-> Trigger fires -> generates event -> affects all agents
-> Deadline fallback if conditions never met
```

### Fast/slow state

- **Fast** (emotions): homeostasis pulls toward baseline
- **Slow** (scars): moral_injury, identity_shift -- irreversible accumulation

## Project structure

```
engine/                    # Universal engine (person-agnostic, 0 hardcoding)
  core/                    # AgentState, HazardEngine, TriggerEngine, AgentAction
  rules/                   # Physical, emotional, social, temporal, environment
  simulation/              # SimulationWorld, Runner, batch, analysis, POM, explanation
  rendering/               # Scripture loader, narrator
  io/                      # Loader, trajectory dataset

content/                   # Biography packs (7 total)
  peter/                   # FaithJourneyState + behavior_profile
  judas/                   # BetrayalPsychologyState + behavior_profile
  caiaphas/                # PoliticalCalculationState + behavior_profile
  crowd/                   # CrowdDynamicsState + behavior_profile
  vangogh/                 # CreativeDriveState + behavior_profile + triggers
  gauguin/                 # ArtisticEgoState + behavior_profile
  theo/                    # PatronState + behavior_profile
  shared/                  # Cross-agent triggers, scripture

tests/                     # 588 tests total (fast 457 / slow / archived 33)
```

## v0.7 trace pipeline (render-ready)

```python
from engine.rendering.trace_narrator import narrate_result

result = SimulationWorld(config, engine, behavior_profiles=profiles).run(seed=0)
narrative = narrate_result(result, player_id="peter", skip_repeats=True)
```

Or step-by-step (collect, filter, render):

```python
from engine.rendering.trace_emitter import collect_trace_events
from engine.rendering.player_view import PlayerViewFilterConfig, filter_for_player
from engine.rendering.trace_narrator import render_trace_timeline

events = collect_trace_events(result)                          # §2 all entry types
visible = filter_for_player(events, PlayerViewFilterConfig("peter"))  # §3.1 filter
narrative = render_trace_timeline(visible, skip_repeats=True)  # v2.0 preview
```

The narrator renders one line per entry in chronological order.
Sample output (Peter's view, seed=0):

```
[tick    1] peter가 follow_closely을(를) 수행했다.
[tick    1] judas가 follow을(를) 수행했다.
[tick    2] judas가 question을(를) 수행했다.
[tick    7] *** 분기점: tick 6~8 구간에서 경로가 갈라지기 시작한다. ***
```

The line for an action uses `visible_signal` from the content pack if set;
otherwise a generic `agent가 action을 수행했다` fallback.
LLM is not used at any stage (ABSOLUTE RULE #4).

### Information asymmetry (TRACE_SCHEMA §3.1)

Each `AgentAction` in `behavior_profile.json` may declare `observable_from`:

```json
{
  "action_id": "inform_authorities",
  "visible_signal": "유다가 밤중에 어디론가 사라졌다.",
  "observable_from": ["caiaphas"]
}
```

- Empty `observable_from` (default): the action is public — every player view sees it.
- Non-empty list: only the listed agents' views see the action.
  Other players see nothing, so the witness stays in the dark.

Example (Peter's view vs. Caiaphas's view, same seed):
Peter does not see Judas's `inform_authorities`; Caiaphas does.
This is how the simulator preserves the witness identity: the player only learns
what the chosen character could plausibly observe.

Full working example: `python demo_v07.py`

## Adding a new person

1. Create `content/[name]/` with:
   - `initial_state.json` -- starting parameters
   - `domain_[name].py` -- domain-specific state (extends DomainState)
   - `behavior_profile.json` -- voluntary actions with weight formulas
   - `hazard_events.json` -- events with hazard functions (optional)
   - `checkpoints.json` -- ground truth observations (optional)

2. For multi-agent, also create:
   - Supporting agent content packs
   - `triggers.json` -- cross-agent interaction triggers

3. Register domain types and run:
   ```python
   register_domain_type("your_domain", YourDomainState)
   ```

No engine code modification needed.

## Tech stack

Python 3.11+ / Pydantic / pytest / SALib / UMAP / sklearn HDBSCAN / shapiq / pyABC / EMA Workbench

## Documents

| File | Role |
|------|------|
| `CLAUDE.md` | Behavior rules (absolute, project identity, conventions) |
| `DESIGN.md` | v0.7 architecture and roadmap (v1.0 → v2.0) |
| `DESIGN_LATENT_DRIVE.md` | v1.0 Latent Drive model design |
| `TRACE_SCHEMA.md` | Trace entry types and player-view filter rules |
| `ITERATION_CLASSIFICATION.md` | 34 exploratory analyses tiered for paper / archive |
| `PAPER_OUTLINE_V05.md` | v0.6 paper outline (bullet-level) |
| `PAPER_DRAFT_V06.md` | v0.6 paper working draft (prose, unreviewed) |
| `RESEARCH.md` | Research findings summary (consolidated) |
| `SCENARIO_TEMPLATE.md` | Guide for adding a third scenario |
| `progress.md` | Session memory / status board |
