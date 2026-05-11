# WITNESS

**결정론적 서사 시뮬레이션 엔진(뼈대) + 장르 변환기(살)** 의 이중 구조 포트폴리오.

WITNESS는 먼저 다중 에이전트 세계를 결정론적으로 시뮬레이션합니다 (뼈대).
그다음 인물의 두려움, 주변 압력, 행동 변화 흐름을 관찰해 anchor-clean한
**UniversalStorySeed v1.1**과 **SkeletonOutput v1**으로 추출합니다.

현재 버전은 그 universal seed를 **rule-based Genre Adapter**로 *서로 다른 장르
문법*으로 변환합니다. 같은 universal skeleton이 한국 아침 막장 드라마와
일본 정적 드라마로 서로 다르게 펼쳐지는 모습을 side-by-side로 보여줍니다.

> **메인 portfolio asset**: [docs/portfolio/demo_genre_comparison/index.html](docs/portfolio/demo_genre_comparison/index.html)
> — 같은 universal skeleton → 두 장르 변환 비교.

ML 기반 Flesh Engine은 **Phase 3.0 Data & Annotation Pilot** 통과 후
진행 예정입니다 (현재 사용자 승인 5건 대기 중).

> WITNESS currently demonstrates a rule-based genre adaptation layer.
> The ML-based Flesh Engine is planned after the Phase 3.0 data and annotation pilot.

> 전체 개편 plan: [docs/witness_narrative_mode_plan.md](docs/witness_narrative_mode_plan.md).
> 현재 진행 (2026-05-11):
> - Phase 0 (skeleton contract 동결), Phase 1 (data infra), Phase 2 prep (annotation guide v1.1) ✅
> - **Phase 2.5** Validation Fix (UniversalStorySeed v1.1 / RFC-0001 / 의미 보존 강제) ✅
> - **Phase 2.75** Rule-based Genre Adapter MVP ✅
> - **Phase 2.8** Genre Adapter Polish (structured outline + genre_lens + soft quality audit) ✅
> - **Phase 2.9** Portfolio Finalization (메인 demo 확정 + Phase 3.0 prep 3 docs) ✅
> - **Phase 3.0 v1.1** Mode A 데이터 파이프라인 7 스크립트 + 2 titles × 5 ep fixture (77 quotes / hallucination 0) + instructions_ko (12 feature 정의 inline) ✅ (외부 fetch 0)
> - **Phase 3.1 prep** No-ML weighted score baseline ✅ (학습 0). **Target A/B/C 모두 결과물 (portfolio asset) 보유**:
>   - **Target A** *seed × profile fit* (flesh_baseline.py + demo HTML)
>   - **Target B** *episode × profile intensity* (episode_intensity.py + demo HTML, fixture-only, Plan §22.2)
>   - **Target C** *seed → ranked top-K genres* (adaptation_recommendation.py + demo HTML, Plan §22.3)
>   - Plan §24 Step 2 bridge: `apply_top_recommendation.py` (Target C → genre_adapter chain 완결)
>   - Plan §29 verifier: `verify_phase3_1_acceptance.py` (9 항목 자동, Phase 3.0 verifier 대칭)
> - **Phase 3.05 prep 정직성 보강** ✅ — rulebook_only score_breakdown 항상 채움 (axis/pressure/compatibility/annotation_score=None/mode) + demo "Prep mode (rulebook-only)" banner + validator `--strict + --synopsis` 강제 + hallucination report 3 layer 분리 (valid/all/invalid) + Operating Guide Deploy Status Matrix
> - **Rubric directive (29 cycle)** ✅ — 4-Axis Discovery *Candidate Classifier* ([docs/witness_rubric_design.md](docs/witness_rubric_design.md) + [WITNESS_V3_RUBRIC_DESIGN_REVIEW.md](docs/WITNESS_V3_RUBRIC_DESIGN_REVIEW.md)). 8-step flowchart (hardcoded → canon hard → **causal gate** → context_break → novelty noise → canonical_reproduction → character_consistent_novel_CANDIDATE / canon_compatible_character_DRIFT). 12+ portfolio reports (8 trajectory variants + alignment + axis-isolated + ensemble HTML). review §2.1-§2.6/§3/§5/§H8 all validated. Rule #14 (학습 loss 0) + scalar 합산 0 + uncalibrated_phase3_placeholder 명시.
> - Phase 3.0 actual run / Phase 3.1 학습 — 외부 의존성 사용자 승인 5+2건 대기
>
> **포트폴리오 메인 데모 (2026-05-10)**: [docs/portfolio/demo_genre_comparison/index.html](docs/portfolio/demo_genre_comparison/index.html)
> — 같은 universal skeleton을 *한국 아침 막장 드라마* vs *일본 정적 드라마*로 변환한 결과 side-by-side.
>
> **FROZEN contract**: [`engine/observer/skeleton_output.py::SkeletonOutput`](engine/observer/skeleton_output.py)
> + [`UniversalStorySeed v1.1`](engine/observer/universal_story_seed.py) (RFC-0001).
> 변경 시 [docs/plans/RFC_TEMPLATE.md](docs/plans/RFC_TEMPLATE.md) 따라 RFC 작성 의무.
> Phase 3 Go gate: `python scripts/skeleton/validate_skeleton_phase3.py docs/portfolio/demo/skeleton_output.json`.

## 빠른 실행

```bash
# 1) Universal skeleton 데모 (engine 시뮬레이션 + skeleton output)
python scripts/narrative/run_portfolio_demo.py
open docs/portfolio/demo/index.html

# 2) Genre Adapter — 같은 skeleton을 한국 아침 막장 드라마 문법으로 변환
python scripts/narrative/run_genre_demo.py \
    --skeleton docs/portfolio/demo/skeleton_output.json \
    --genre korean_morning_melodrama \
    --output docs/portfolio/demo_genre
open docs/portfolio/demo_genre/index.html

# 3) 두 장르 side-by-side 비교 (메인 portfolio asset)
python scripts/narrative/run_genre_comparison.py \
    --skeleton docs/portfolio/demo/skeleton_output.json \
    --genres korean_morning_melodrama japanese_quiet_drama \
    --output docs/portfolio/demo_genre_comparison
open docs/portfolio/demo_genre_comparison/index.html

# 4) Phase 3 Go gate (deployed skeleton이 ML 진입 조건 만족하는지)
python scripts/skeleton/validate_skeleton_phase3.py docs/portfolio/demo/skeleton_output.json
```

## 결과로 무엇이 나오나

- 하나의 메인 에피소드 개요 (제목 / 한 줄 이야기 / 욕망 / 압박 / 변화 / 3단계 흐름 / 남는 질문 / 활용 가능성)
- 보조 이야기 씨앗 카드 (역할별로 차별화)
- 시뮬레이션 실행 로그 / 압력 흐름 (접힘)
- 근거 / 감사 리포트
- 확장 데모: 베드로 life arc timeline (5막 / 주별 / seed 비교)

---

<details>
<summary>상세: 메인 산출물 / 기술 스택 (펼침)</summary>

> **메인 산출물 (2026-05-06~)**:
> - [docs/portfolio/STORY_CANDIDATES.md](docs/portfolio/STORY_CANDIDATES.md) — **Story Candidate 카드** (4 distinct: Peter / Andrew / James / John, named characters, conflict-tuned premises)
> - [docs/portfolio/CROSS_SEED_STORY_PATTERNS.md](docs/portfolio/CROSS_SEED_STORY_PATTERNS.md) — **Cross-seed robustness** (5 seeds, 6/6 robust patterns, 0 anomaly)
> - [docs/portfolio/story_candidate_console.html](docs/portfolio/story_candidate_console.html) — 정적 HTML 콘솔 (23KB self-contained, candidate list + arc + turning points + creative-use 탭 + cross-seed badges)
> - 입력 layer: [docs/portfolio/NARRATIVE_OPPORTUNITIES.md](docs/portfolio/NARRATIVE_OPPORTUNITIES.md) (4 threads) / [WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md](docs/demo/WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md) (5 candidate cards)
>
> **Plan**: [docs/WITNESS_STORY_EMERGENCE_IMPLEMENTATION_PLAN.md](docs/WITNESS_STORY_EMERGENCE_IMPLEMENTATION_PLAN.md)
> **Visual track**: 전체 frozen ([VISUAL_TRACK_FREEZE_DECISION.md](docs/visual/VISUAL_TRACK_FREEZE_DECISION.md)).

</details>

> **Ultimate vision**: A narrative simulator where the player experiences a historical figure's life as a witness.
> Multi-agent + trigger-mediated + hazard-driven. Learn from simulation to construct life trajectories.
> Ask: **"What was the moment that made the difference?"**

> 📂 **Project navigation**: [docs/INDEX.md](docs/INDEX.md) — master index | [docs/SUMMARY_PHASES_1_TO_7.md](docs/SUMMARY_PHASES_1_TO_7.md) — 누적 결과 종합

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
| v1.3 | World Observer Layer (관찰 계층, 4 lens + salience + replay) | **MVP complete (2026-04-30)** |
| v2.0 | Narrative Witness renderer (player experience) | Planned |

See `DESIGN.md` for full roadmap; `docs/specs/DESIGN_LATENT_DRIVE.md` for v1.0 architecture.

## Quick start

```bash
python -m venv venv && source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt

# Peter multi-agent (4 agents, 100 runs)
python main.py --multi

# Van Gogh multi-agent (3 agents)
python main.py --multi --person vangogh --runs 50

# v0.7 trace pipeline demo (sim → trace → player view → JSONL → narrative)
python examples/demo_v07.py --scenario peter
python examples/demo_v07.py --scenario vangogh --seed 0

# v1.2 phase-linked arc demo (Peter 공생애, absolute-time output)
python examples/demo_phased.py --seed 0                 # 4-phase (~101 days, 2 agents)
python examples/demo_phased.py --seed 0 --full-passion  # 5-phase + legacy 500-tick passion (~143 days, 4 agents)
python examples/demo_phased.py --with-recovery          # opt-in slow state recovery rule
python examples/demo_phased.py --show-drive --encoder learned  # v1.0 Stage 2 LDA encoder + drive trajectory

# Legacy comprehensive demo
python examples/demo.py --quick

# Single-agent mode (legacy)
python main.py --person peter
python main.py --person vangogh --runs 50

# Portfolio demo (one-command, self-contained HTML, data-driven body 2026-05-08)
python scripts/narrative/run_portfolio_demo.py                 # default seed 0
python scripts/narrative/run_portfolio_demo.py --seed 7        # different seed → different body text
# → docs/portfolio/demo/index.html (self-contained, ~16 KB)

# Life Arc Narrative (engine phased simulation → 시간대별 베드로 공생애 timeline, 2026-05-08)
python scripts/narrative/run_life_arc_demo.py --full-passion                     # 5 phase, 142일, 15 정경 사건
python scripts/narrative/run_life_arc_demo.py --seed 7 --full-passion            # 다른 seed → 다른 선택
python scripts/narrative/run_life_arc_demo.py --full-passion --window by_week    # 21 weekly windows
python scripts/narrative/demo_life_arc_seed_diversity.py --seeds 0,7,11          # 3 seeds 비교
# → docs/portfolio/demo/life_arc_demo.{md,html,json} (self-contained HTML 포함)

# Tests
pytest -m "not slow and not archived"  # 2,130 fast tests (~75s)
pytest tests/test_observer/            # observer + moment + linking + thread tests
pytest tests/test_narrative/           # 18 narrative export + console tests (Phase 4-5)
pytest tests/test_report/              # 19 brief / provenance-table tests
pytest tests/test_visual/              # 72 visual regression tests (track frozen)
pytest -m archived                     # Tier 3 archived tests
```

## Narrative mining quickstart (메인 트랙)

```bash
# 1. Run a simulation → observer dump (already in the repo for peter_scarcity_baseline)
#    data/visual/dot_observer_data.json  ← 824 KB / 200 ticks / 12 agents

# 2. Mine moments → story threads → narrative opportunities (4 sequential CLI stages)
python scripts/narrative/build_moments.py
# → Wrote data/narrative/moments.json: 105 moments (50 agent_state_shift,
#   12 group_tension_shift, 36 world_pressure_shift, 6 unresolved_thread, 1 conflict_marker)

python scripts/narrative/build_story_threads.py
# → Wrote data/narrative/moment_links.json: 1,727 links {same_agent: 128,
#   same_group: 276, same_pressure: 415, same_conflict_axis: 274, temporal_continuity: 634}
# → Wrote data/narrative/story_threads.json: 4 threads (strong=1, usable=0, weak=3)

python scripts/narrative/export_narrative_opportunities.py
# → Wrote docs/portfolio/NARRATIVE_OPPORTUNITIES.md (12 KB, 4 thread cards)
# → Wrote data/narrative/narrative_opportunities.json (machine-readable)

python scripts/narrative/build_mining_console.py
# → Wrote docs/portfolio/narrative_mining_console.html (56 KB self-contained)

# 3. Open the thread console in any browser
python -m http.server 8000
# → http://localhost:8000/docs/portfolio/narrative_mining_console.html

# 4. Story Emergence Phase A-F (one layer up — named characters, cross-seed)
python scripts/narrative/build_story_candidates.py
# → docs/portfolio/STORY_CANDIDATES.md  (Peter / Andrew / James / John)
# → data/narrative/story_candidates.json

python scripts/visual/export_dot_observer_data.py --seed 1 --output data/visual/dot_observer_data_seed1.json
python scripts/visual/export_dot_observer_data.py --seed 2 --output data/visual/dot_observer_data_seed2.json
python scripts/visual/export_dot_observer_data.py --seed 3 --output data/visual/dot_observer_data_seed3.json
python scripts/visual/export_dot_observer_data.py --seed 4 --output data/visual/dot_observer_data_seed4.json
# (seed 0 is already at data/visual/dot_observer_data_seed0.json)

python scripts/narrative/build_cross_seed_patterns.py
# → docs/portfolio/CROSS_SEED_STORY_PATTERNS.md  (5 seeds aggregated)
# → 6/6 robust patterns / 0 anomaly for peter_scarcity_baseline

python scripts/narrative/build_story_candidate_console.py
# → docs/portfolio/story_candidate_console.html  (23KB self-contained)
# Open in browser → http://localhost:8000/docs/portfolio/story_candidate_console.html

# Pipeline runs against any observer dump. Verified on:
#   data/visual/dot_observer_data.json          (peter_scarcity_baseline)
#   data/visual/dot_observer_data_triple.json   (peter_scarcity_triple)
#   data/visual/dot_observer_data_vangogh.json  (vangogh_sacred_baseline)
# Use --input on each script to switch anchors.
```

## Text-first reporting layer (기반 surface — narrative mining에 입력 데이터 제공)

```bash
# Observer Brief (candidate cards with provenance class)
python scripts/report/build_observer_brief.py
# → docs/demo/WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md

# Per-field Provenance Table
python scripts/report/build_provenance_table.py --json data/report/provenance_table.json
# → docs/demo/WITNESS_PROVENANCE_TABLE_PETER_SCARCITY.md
```

이 두 산출물은 *narrative mining의 입력 layer*이자 자체 portfolio 자료다. The
brief is schema-agnostic across observer dumps (`peter_scarcity_baseline`,
`peter_scarcity_triple`, `vangogh_sacred_baseline` all verified by
`tests/test_report/test_observer_brief.py`).

---

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

tests/                     # 1978 tests total (fast 1845 / slow + archived 133)
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

Full working example: `python examples/demo_v07.py`

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
| `docs/specs/DESIGN_LATENT_DRIVE.md` | v1.0 Latent Drive model design |
| `docs/specs/TRACE_SCHEMA.md` | Trace entry types and player-view filter rules |
| `docs/specs/WITNESS_V3_REDESIGN.md` | v3 Phase 2 v2 redesign + redesign phases |
| `docs/specs/WITNESS_V3_PHASE2_V2_*.md` | v3 concept variables + Dynamics spec |
| `docs/specs/WORLD_DESIGN*.md` | v2.0 World Engine design |
| `docs/specs/WORLD_SPIKE_*.md` + `WITNESS_SPIKE_*.md` | Spike-level specs |
| `docs/specs/SCENARIO_TEMPLATE.md` | Guide for adding a third scenario |
| `docs/research/RESEARCH.md` | Research findings summary (consolidated) |
| `docs/research/ITERATION_CLASSIFICATION.md` | 34 exploratory analyses tiered for paper / archive |
| `docs/research/PAPER_OUTLINE_V05.md` | v0.6 paper outline (bullet-level) |
| `docs/research/PAPER_DRAFT_V06.md` | v0.6 paper working draft (prose, unreviewed) |
| `docs/research/PROJECT_DIRECTION_v2.md` | v2 direction notes |
| `docs/person/` | v3 session artifacts (per-phase reports) |
| `docs/world/` | World Engine Spike review docs |
| `docs/sessions/` | Dated session dumps |
| `docs/story/` | **Story Output MVP** — annotated probe → 한국어 서사 텍스트 (3-stage pipeline) |
| `docs/SESSION_SUMMARY_2026-04-28_BRANCH_C_AUTONOMOUS.md` | Branch C autonomous session 종합 정리 |
| `examples/` | Runnable demos (demo.py, demo_v07.py, demo_phased.py) |
| `progress.md` | Session memory / status board |
| `lessons.md` | Cross-session learnings |

## World Observer Layer (NEW — 2026-04-30)

Person Engine 위에 추가된 *흐르는 세계 관찰 계층*. 시뮬레이션 결과를 다양한 렌즈 (Person / Group / Event / World) + zoom level + salience detector로 조회. **관찰기 ≠ 평가기** — story quality 자동 판정 안 함, *탐색 가능성*에 집중.

```
Pressure/Event Input
    ↓
Simulation Engine (existing)
    ↓
World Snapshot Stream
    ↓
World Observer Layer
    ├─ Person View / Group View / Event View / World View
    ├─ Salience Detector (8 tag types)
    ├─ ReplayCursor (jump / bookmark / window)
    └─ Multi-stream Compare (anchor seed comparison)
```

**Status (2026-04-30)**: MVP complete (Phase O1-O7) + Story Pipeline (Phase P1-P5). 179 tests PASS (130 base + 35 candidate/packet/render + 14 adapter). ABSOLUTE Rule #1 (no person hardcoding) + Rule #6 (engine API preservation) 준수.

**Quick start**:
```bash
# 통합 demo (4 modes + default full)
python examples/demo_observer.py                # full demo
python examples/demo_observer.py --status       # MVP 상태
python examples/demo_observer.py --views        # 4 lens texts
python examples/demo_observer.py --replay       # ReplayCursor + auto bookmark
python examples/demo_observer.py --compare      # 3 seeds 측면 비교
```

**핵심 components**:
- `engine/observer/` — snapshot_schema / recorder / core (4 lens) / salience / replay / adapter
- `scripts/observer/` — observer_report (text) / compare_views (multi-stream)
- `docs/observer/WORLD_OBSERVER_LAYER_SPEC.md` (canonical spec)

**Adapter usage** (post-hoc on existing simulation):
```python
from engine.simulation.world import SimulationWorld
from engine.observer.adapter import result_to_observer

world = SimulationWorld(config, ...)
result = world.run()
observer = result_to_observer(result, role_map={"agent_001": "follower"})
```

## Observer → Story Candidate Pipeline (NEW — 2026-04-30)

Observer Layer가 잡은 salient moment를 *story candidate*로 변환하고 사람이 빠르게 검토할 수 있는 packet으로 출력. 2 단계: P1-P5 capability + Q1-Q4 curation. *추천 + 분류*만, *판정* 안 함 (관찰기 ≠ 평가기).

```
Observer (snapshot stream)
    ↓ engine/observer/candidate.py — 4 extractor (story/world/person/event)
StoryCandidate × N (raw)
    ↓ engine/observer/candidate_curation.py — 3 bucket + temporal diversity + near-dup
CuratedSet (story_ready / observation_only / low_activity_hold)
    ↓ scripts/observer/candidate_packet.py — 6-field packet + curation block
CandidatePacket (Basic / Why / Lens summaries / Story potential / Render link / Human check / Curation)
    ↓ scripts/observer/render_candidate_story.py — 3-lens narration
Story-ready text (per lens)
```

**Status (2026-04-30)**:
- P1-P5 capability: 35 tests PASS (12 candidate + 13 packet + 10 render)
- Q1-Q4 curation: 33 tests PASS (22 curation + 11 packet v2)
- Real-run: 14 raw → 8 curated (5 story_ready + 0 observation_only + 3 low_activity_hold), 42% near-dup reduction
- Lee directives: P1-P5 §11 6/6 ✅, Q1-Q4 §7 4+/6 ✅ (Case A both)

**Quick start**:
```bash
python examples/demo_observer_story.py                       # default: raw list (P1-P5)
python examples/demo_observer_story.py --curated             # 3-bucket curated view (Q1-Q4)
python examples/demo_observer_story.py --packet <id>         # single packet (full text)
python examples/demo_observer_story.py --render-story <id>   # render in recommended lens
python examples/demo_observer_story.py --compare-lenses <id> # 3-lens comparison
```

**핵심 docs**:
- `docs/observer/OBSERVER_TO_STORY_PIPELINE.md` (P1-P5 spec)
- `docs/observer/CANDIDATE_CURATION_PLAN.md` (Q1-Q4 spec)
- `docs/observer/OBSERVER_TO_STORY_VALIDATION.md` + `CANDIDATE_CURATION_VALIDATION.md` (real-run records)
- `docs/observer/ANCHOR_2_EXPANSION_PLAN.md` (next step plan)

## Visual Observer Layer (NEW — 2026-04-30)

도트 기반 visual track. Observer snapshot → 도트 시각화 → Explorer 통합 entry. 4 단계 (V0-V1 + V2 + Anchor 2 + Cross-seed) + Visual Explorer v0 통합.

**3 entry points (역할 분리)**:

| HTML | 역할 | 사용 시점 |
|---|---|---|
| **`visual/explorer.html`** | **Broad navigation entry** | 전체 탐색의 default entry. anchor + view + candidate + packet 통합 |
| `visual/dot_observer_replay.html` | Single-run **deep view** | 한 run의 V2 5-panel + agent dot click + range overlay 등 풀 기능 |
| `visual/dot_observer_cross_seed.html` | Cross-seed **deep view** | 5 seeds small multiples + per-seed detail full panels |

**Status (2026-04-30)**:
- V0-V1 MVP: Lee §7 5+/6 success
- V2 minimal: 4 features (marker noise / agent follow / filter / range overlay)
- Anchor 2 single-seed: Case A-2 (V2 generalize ✅, 데이터 발산 미미)
- Cross-seed: Case CS-A (REC 3 / PARTIAL 1 / SAT 1 nonmonotonic visible)
- Visual Explorer v0: Case EX-A (단일 entry 통합 + 기존 deep view 보존)

**Quick start**:
```bash
# 1. 데이터 export (1회)
python scripts/visual/export_dot_observer_data.py
python scripts/visual/export_dot_observer_data.py \
    --anchor peter_scarcity_triple --output data/visual/dot_observer_data_triple.json
python scripts/visual/export_cross_seed_visual_data.py \
    --anchor peter_scarcity_triple --seeds 0 1 2 3 4 \
    --output data/visual/dot_observer_cross_seed_triple.json

# 2. HTTP server + 브라우저
python -m http.server 8000
# Default broad navigation:
#   http://localhost:8000/visual/explorer.html
# Deep view (V2 5-panel + dot click):
#   http://localhost:8000/visual/dot_observer_replay.html
# Deep view (cross-seed full panels):
#   http://localhost:8000/visual/dot_observer_cross_seed.html
```

**핵심 docs**:
- `docs/visual/VISUAL_EXPLORER_V0_1_OPERATING_GUIDE.md` (운영 매뉴얼)
- `docs/visual/VISUAL_EXPLORER_V0_1_SMOKE_TEST.md` (8/8 PASS)
- `docs/visual/VISUAL_TRACK_SYNTHESIS_REVIEW.md` (4 단계 종합)
- `docs/visual/VISUAL_EXPLORER_V0_REVIEW.md` (Case EX-A)
- `docs/visual/CROSS_SEED_VISUAL_VALIDATION.md` (Case CS-A)
- `docs/observer/OBSERVER_TO_STORY_VALIDATION.md` + `CANDIDATE_CURATION_VALIDATION.md` (real-run records)
- `docs/observer/ANCHOR_2_EXPANSION_PLAN.md` (next step plan)

## Story Output Layer (NEW — 2026-04-28)

Annotated probe를 입력 받아 한국어 이야기 텍스트를 생성하는 3-stage pipeline. v2.0 Narrative Witness Layer의 entry point.

```
annotated probe (.txt)
    ↓ scripts/story/extract_story_features.py
data/story/story_features/{probe_id}.json (수치/구조 추출)
    ↓ scripts/story/build_narrative_ir.py
data/story/narrative_ir/{probe_id}.json (의미 atom 변환)
    ↓ scripts/story/render_story_ko.py
docs/story/generated/{probe_id}_{summary,narrative}_ko.txt (한국어 텍스트)
```

**Status (2026-04-28)**: MVP Phase 2 통과 (6/6 acceptance, P4≠P5 variation 확인). 48 stories 생성됨 (12 baseline + 36 Branch C). Configuration sensitivity가 이야기 톤에서 surface (LOW_ACTIVITY / nonmonotonic / placement reversal 모두 글에서 식별 가능).

**Quick start**:
```bash
# 12 baseline stories
python scripts/story/extract_story_features.py --all
python scripts/story/build_narrative_ir.py --all
python scripts/story/render_story_ko.py --all

# Branch C 36 stories
python scripts/story/extract_story_features.py --branch-c
python scripts/story/build_narrative_ir.py --branch-c
python scripts/story/render_story_ko.py --branch-c

# J-Alpha + J-Beta Creative IP demo
python examples/demo_story.py --highlights      # 6 curated cases
python scripts/story/generate_anchor_variations.py    # 5 anchors x 5 seeds = 25 stories
python scripts/story/generate_trilogy_view.py         # scarcity trilogy 3-act narrative
```

**핵심 docs**:
- `docs/story/STORY_OUTPUT_SPEC.md` (사양)
- `docs/story/STORY_MVP_ACCEPTANCE_v2.md` (6/6 PASS verdict)
- `docs/story/STORY_HIGHLIGHTS.md` (48 stories 큐레이션 — Lee 직접 평가용)
- `docs/story/STORY_BRANCH_C_INTEGRATION.md` (Branch C × Story 연결)
- `docs/archive/lee_directives_2026-04-30/WITNESS_STORY_OUTPUT_MVP_PLAN.md` + `..._NEXT_STEPS.md` (원래 directive, archive)

## Creative IP Track — J-Alpha + J-Beta (NEW — 2026-04-28)

Story Output Layer 위에 *anchor variation IP 자산*을 만드는 트랙. Lee directive `docs/archive/lee_directives_2026-04-30/WITNESS_CREATIVE_IP_TRACK_IMPROVED_DIRECTIVE.md` (archive).

### J-Alpha (1차 증명, PASS 5/6)
**핵심 가설**: "같은 anchor의 5 seed가 실제로 서로 다른 한국어 이야기로 읽히는가?"
- ✅ Peter scarcity baseline → 3 distinct outcomes (SAT 2 / REC 2 / PARTIAL 1)
- ✗ Van Gogh→sacred substitute → 5/5 PARTIAL (anchor 선택 문제, transparency 보존)
- 자율 follow-up 발견: peter_scarcity_high_density (3 distinct, READY)

### J-Beta (확장, 진행 중)
**Selector queryable library**: 5 anchors (J-Alpha 3 + J-Beta 2 trilogy)
- `engine/story/selector.py`: `query_anchors(scenario=, min_diversity=)` / `get_top_arcs(arc_type)` / `get_anchor_by_id` / `get_variations_by_anchor_id`

**Scarcity Trilogy** (1/2/3 accusations, **nonmonotonic IP narrative beat**):
- Act I (1 acc): SAT modal — "한 번의 비난이 어떤 자리를 굳히고"
- Act II (2 acc): SAT modal — "두 번의 비난이 그 굳음을 깊게 했다"
- Act III (3 acc): **REC modal** — "세 번째 비난이 닿았을 때, 무언가가 풀려났다"

→ "더 많은 무게가 어느 순간 짐을 덜어 줄 수 있다"는 **counterintuitive narrative paradox** — IP 자산 가치 큼.

**Cross-scenario REC differentiation** (Gate 1 자율 cycle):
- sacred REC: "기도가 끝난 자리에서…"
- accusation REC: "거리의 시선은 여전히 한 방향으로 모였지만, 그 방향에서 더 이상 무엇도 떨어지지 않았다…"
- scarcity REC: "곡식이 채워지지는 않았지만, 사람들은 다시 손을 마주잡았다…"

### Creative IP 산출 (`outputs/creative_demo/`)
- `peter_scarcity_baseline_5_variations_ko.txt` (5 stories — J-Alpha PASS evidence)
- `peter_scarcity_high_density_5_variations_ko.txt` (자율 발견)
- `peter_scarcity_double_5_variations_ko.txt` + `peter_scarcity_triple_5_variations_ko.txt` (J-Beta trilogy)
- `vangogh_sacred_baseline_5_variations_ko.txt` (FAIL transparency)
- **`scarcity_trilogy_modal.txt`** (3-act narrative — IP 직접 가치)
- **`scarcity_trilogy_full.txt`** (15-story cross-seed)

### 핵심 docs
- `docs/CREATIVE_TRACK_TRANSITION.md` (트랙 전환 공식)
- `docs/creative/CURATED_ANCHOR_SET_ALPHA.md` (anchor 선정)
- `docs/creative/VARIATION_READING_REVIEW.md` (J-Alpha verdict)
- `docs/creative/PETER_5_VARIATION_COMPARISON.md` (Lee Gate 2 보조)
- `docs/creative/PETER_TWO_ANCHOR_COMPARISON.md` (cell 비교)
- `docs/creative/J_BETA_PROGRESS.md` (J-Beta 진행)
- `docs/creative/RENDERER_DIAGNOSIS_ALPHA.md` (Gate 1 자율 진단)
- `docs/creative/NOVEL_TONE_GUIDE_ALPHA.md` (renderer 개선 가이드)

## Pytest 실행 layer 가이드 (3-tier, 2026-04-28)

`docs/archive/lee_directives_2026-04-30/WITNESS_PYTEST_IMPROVEMENT_PLAN.md` 기반. 변경 단위에 맞는 layer 선택:

### Fast Local (~0.5초, 119 tests)
**언제**: 작은 수정 직후 — template, regex, threshold, helper 변경
```bash
pytest tests/test_story/ -q
```

### Domain (수십초)
**언제**: 한 작업 블록 끝, extraction+IR+renderer 동시 변경, observable surface 수정
```bash
pytest tests/test_story tests/test_engine tests/test_world_process -q
```

### Full Suite (~13min, 1845 fast tests + 14 skipped, 0 failures)
**언제**: 세션 마감 전, milestone 완료 직전, engine touch 전후, canonical 결과물 생성 전
```bash
pytest -m "not slow and not archived"
```

### 운영 규칙 (Claude Code용)
- `extract_story_features.py` 수정 → `pytest tests/test_story/test_extract_story_features.py`
- `build_narrative_ir.py` 수정 → `pytest tests/test_story/test_build_narrative_ir.py`
- `render_story_ko.py` 수정 → `pytest tests/test_story/test_render_story_ko.py` + golden test
- baseline 12개 재생성 직전 → story tests + domain tests
- MVP acceptance 직전 / engine touch 후 → full suite
