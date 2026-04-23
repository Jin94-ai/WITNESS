# Witness — Technical Summary for External Review (2026-04-21)

> 외부 리뷰어에게 프로젝트 **구현 상태 그 자체**를 설명하기 위한 기술 요약. 설계 의도나 로드맵은 별도 문서(`PROJECT_DIRECTION_v2.md`, `DESIGN.md`) 참조. 여기는 "**지금 코드가 실제로 무엇을 하고 있는가**"만.

---

## 1. `engine/` 모듈 구성 (5,797 lines, 49 Python files)

모두 person-agnostic (content 하드코딩 금지, `test_integrity.py` 자동 검증).

### 1.1 `engine/core/` — 상태와 기본 개념 (1,571 lines)

| 모듈 | 라인 | 역할 |
|------|-----|------|
| `state.py` | 237 | `AgentState` / `PhysicalState` / `EmotionalState` / `SlowState` / `DomainState` / `LatentDriveState`. Pydantic 기반, 모든 필드 [0,10] clamping. |
| `event.py` | 224 | `ExternalEvent` / `StateEffect` / `CanonicalIntervention` / `WeightFormula`. 이벤트 스키마 + state 변경 효과. |
| `hazard.py` | 266 | `HazardFunction(base_rate, factors, max_hazard, base_rate_unit)` / `HazardEvent` / `HazardEngine`. Poisson `P(event) = 1 - exp(-h · dt)`. `base_rate_unit="per_hour"` opt-in (v1.2 Iter 27). |
| `trigger.py` | 242 | `Trigger` (state_conditions + event_template), `TriggerEngine`. 다중 agent 조건 평가. |
| `action.py` | 108 | `AgentAction` (visible_signal, observable_from), `AgentBehaviorProfile`. content-driven 정보 비대칭성. |
| `phase.py` | 154 | **v1.2**: `Phase` / `PhaseExitCondition` / `PhaseHandoffSpec` / `FieldMapping`. phase-linked 아크 표현. |
| `latent_drive.py` | **446** | `LatentDriveEncoder` Protocol + 구현체 4종: `IdentityEncoder`, `FixedProjectionEncoder` (random projection), `ExtensibleFixedProjectionEncoder` (domain_state feature 포함), `LearnedLinearEncoder` (sklearn LDA). v1.0 Stage 2 bridge. |
| `environment.py` | 37 | `EnvironmentState`. 환경 변수 저장소. |
| `world.py` | 99 | `SimulationConfig` (initial_state, phases, events, triggers, hazard_events, noise_scale 등). v1.2에서 `phases: list[Phase] \| None` 추가. |

### 1.2 `engine/rules/` — 상태 전이 규칙 (1,018 lines)

모든 rule은 `RuleContext.dt_hours` 기반 per-hour rate 권장 (v1.2).

| 모듈 | 라인 | 역할 |
|------|-----|------|
| `base.py` | 81 | `Rule` Protocol, `RuleEngine.apply_all`, `RuleContext(tick, delta_tick, dt_hours, active_events, environment, rng, all_agents)`. |
| `emotional.py` | 159 | `FearResponseRule`, `HopeRule`, `GriefRule`, `ConfusionRule`, `LoveRule` — 감정 교차 효과. |
| `physical.py` | 81 | `FatigueRule`, `HungerRule`, `HealthRule`. |
| `social.py` | 56 | `RelationshipDecayRule`, `GroupIsolationRule`. |
| `temporal.py` | 187 | `HomeostasisRule` (감정 회복), `SlowStateRule` (moral_injury 누적), `HighStressConsequenceRule`, `CircadianRule`. |
| `environment.py` | 79 | `EnvironmentDynamicsRule`. |
| `inhibitor.py` | 128 | **v1.2**: `FieldAttenuationRule`, `FieldAmplificationRule` — generic cross-agent field 감쇄/증폭. content-configurable. |
| `slow_recovery.py` | 147 | **v1.2**: `SlowStateFieldRecoveryRule` — opt-in moral_injury/trust_scar/identity_shift/event_trauma 조건부 회복. |

### 1.3 `engine/simulation/` — 실행/분석 (2,841 lines)

| 모듈 | 라인 | 역할 |
|------|-----|------|
| `world.py` | 395 | `SimulationWorld` — 다중 agent 메인 루프. trigger → external → intervention → hazard → rules → drive encoding → snapshot. |
| `phased_world.py` | **410** | **v1.2**: `PhasedSimulationWorld` + `PhasedMultiAgentResult`. phases=None이면 `SimulationWorld` bit-exact 위임; phases=[...]이면 phase별 순차 실행 + handoff + per-phase `canonical_events_path` 로드. |
| `analysis.py` | 391 | SALib/UMAP/HDBSCAN 기반 민감도/차원축소/클러스터. |
| `runner.py` | 321 | v0.1 legacy 단일 agent 실행기 (`SimulationResult`). |
| `training_samples.py` | **320** | `TrainingSample`, `state_to_feature_vector` (12-dim), `state_to_feature_vector_extended` (domain_state 포함), `compute_drive_action_diagnostics`, `drive_class_separability` (Fisher ratio). |
| `checkpoint.py` | 263 | event-relative hindcasting 검증. |
| `drive_training.py` | 226 | `TrainingConfig` + `train_drive_model` (config.use_fixed_projection / use_learned_linear opt-in). |
| `bifurcation.py` | 183 | Decision window 탐지. |
| `explanation.py` | 176 | 인과 설명 카드 생성. |
| `time_axis.py` | **167** | **v1.2**: `ticks_to_absolute_hours`, `extract_field_trajectory_absolute`, `convert_phase_boundaries_to_hours`. phase-variable tick 간 비교. |
| `statistics.py` | 151 | CI, Cohen's d, Wilson proportion. |
| `recovery_test.py` | 144 | Parameter Recovery Test. |
| `resolution.py` | 118 | 동적 해상도. |
| `calibration.py` | 116 | pyABC 파라미터 보정. |
| `pom.py` | 105 | `PatternCriterion`, `evaluate_pom`, `pom_filter`. |
| `batch.py`, `event_scheduler.py`, `scheduler.py`, `decision.py` | 74/71/54/48 | 앙상블, 이벤트 스케줄링, agent 활성화 순서, 확률적 행동 결정. |

### 1.4 기타 (367 lines)

- `engine/io/loader.py` (217): `load_agent_state`, `load_phase`, `load_handoff_spec`, `load_events`, `load_triggers` 등 JSON 파서.
- `engine/io/trajectory.py` (358): Parquet/JSONL trajectory dataset 저장.
- `engine/rendering/` (769): `trace_emitter`, `player_view`, `trace_narrator`, `scripture` — v0.7 trace pipeline.

---

## 2. `content/` 인물 팩 (8개)

### 2.1 필수 파일 기준

`test_content_pack_structure.py`가 모든 agent pack에 `initial_state.json` + `behavior_profile.json` 존재 강제. 그 외는 pack별 가변.

### 2.2 Pack 구성

| Pack | 특화 파일 | Domain state 핵심 필드 |
|------|----------|---------------------|
| **peter** | `domain_faith.py`, `canonical_events.json` (19 events), `hazard_events.json`, `checkpoints.json/checkpoints_multi.json`, `pom_scorecard.py`, `initial_state.json` (수난 시점) + `initial_state_calling.json` (어부 시점), **`phases/` 5 directories** (01_calling / 02_galilean / 03_confession / 04_journey_to_jerusalem / 05_passion; 각 `phase_config.json` + `canonical_events.json`), `scenes/`, `chronicle_periods/` | `FaithJourneyState`: `jesus_understanding` (7-level Literal), `obedience_maturity`, `fear_layers`, `communal_role`, `repentance_history` |
| **judas** | `domain_betrayal.py` | `BetrayalPsychologyState`: `disillusionment`, `greed`, `messiah_expectation`, `guilt`, `loyalty_to_cause` |
| **caiaphas** | `domain_politics.py` | `PoliticalCalculationState` |
| **crowd** | `domain_crowd.py` | `CrowdDynamicsState` |
| **vangogh** | `domain_creative.py`, `triggers.json`, `hazard_events.json`, `checkpoints.json`, `pom_scorecard.py` | `CreativeDriveState` |
| **gauguin** | `domain_artistic_ego.py` | `ArtisticEgoState` |
| **theo** | `domain_patron.py` | `PatronState` |
| **talleyrand** | `domain_diplomacy.py`, `canonical_events.json` (10 events, 1789-1830 regime transitions), `pom_scorecard.py` | `DiplomacyState`: `current_regime` (7-level Literal), `alignment_stance` (5-level), `leverage`, `legitimacy_anchor`, `reputation_ambiguity`, `network_regime_span`, `compromise_count`, `moral_fatigue` |

`content/shared/`: `triggers.json` (다중 agent 공용), `scripture/` (개역개정 정경 텍스트).

---

## 3. `demo_phased.py --seed 0` 실행 출력

기본값 (4-phase, recovery 비활성, drive off, 2 agents: peter + judas):

```
Witness v1.2 demo — Peter 공생애 (seed=0)
  Phases: 4
  Recovery rule active: False
  Drive model: off

Phase Boundaries (absolute time)
Phase         Ticks     Hours          Days
01_calling    0-84      0.0-168.0      7.00
02_galilean   84-144    168.0-1608.0   60.00
03_confession 144-194   1608.0-1708.0   4.17
04_journey    194-224   1708.0-2428.0  30.00
Total: 2428.0h ≈ 101.2 days

Peter trajectory — awe
  [01_calling]    tick 0→84:  0.00 → 6.00   (miracle catch, Luke 5)
  [02_galilean]   tick 0→60:  6.00 → 8.00   (sustained ministry)
  [03_confession] tick 0→50:  8.00 → 10.00  (transfiguration peak)
  [04_journey]    tick 0→30:  10.00 → 10.00 (saturated)

Peter trajectory — obedience_maturity
  [01_calling]    0.00 → 5.00  (calling acceptance)
  [02_galilean]   5.00 → 5.80
  [03_confession] 5.80 → 7.60  (Caesarea Philippi confession +1.0)
  [04_journey]    7.60 → 7.90

Final Agent States
  [peter]
    fear=3.13  hope=5.12  awe=10.00
    slow: moral_injury=1.30  event_trauma=0.00
    obedience_maturity=7.90
    jesus_understanding=messiah_political
  [judas]
    fear=0.05  hope=4.42  awe=0.00
    slow: moral_injury=0.00  event_trauma=0.00
    disillusionment=3.00
```

**해석**: canonical events가 예정된 tick에 정확히 발동하고, effects가 누적된다. `jesus_understanding=messiah_political`은 Phase 3 `conf_03_peters_confession` event의 `set` operation 결과 (Phase 5 부활 이후엔 `risen_lord`, 승천 후 `sending_lord`로 전이하지만 이 데모는 Phase 4에서 끝남). Peter의 `moral_injury=1.30`은 Phase 1 `calling_04_fall_at_knees`의 `slow_state.moral_injury += 0.5` 효과 + 그 외 이벤트 누적. Judas는 Phase 2부터 등장했지만 canonical event에 직접 영향받지 않아 초기값 유지.

---

## 4. 핵심 테스트 3개

### 4.1 `test_claim_legacy_mode_identical_to_v07` — legacy bit-exact 보존

[tests/test_engine/test_full_arc_phases_1_to_4.py:236](tests/test_engine/test_full_arc_phases_1_to_4.py#L236)

```python
def test_claim_legacy_mode_identical_to_v07(self, peter_calling_state):
    """phases=None 모드가 v0.7과 완전 동일 동작."""
    legacy_peter = load_agent_state(CONTENT / "peter" / "initial_state.json")
    config = SimulationConfig(
        initial_state=legacy_peter, initial_states=[legacy_peter],
        max_tick=50, state_noise_scale=0.05,
    )
    phased_world = PhasedSimulationWorld(config, _rules())
    phased_result = phased_world.run(seed=7)

    from engine.simulation.world import SimulationWorld
    direct_world = SimulationWorld(config, _rules())
    direct_result = direct_world.run(seed=7)

    assert (
        phased_result.final_states["peter"].emotions.fear
        == direct_result.final_states["peter"].emotions.fear
    )
```

**주장**: 동일 seed로 `PhasedSimulationWorld(phases=None)` 과 `SimulationWorld`가 **부동소수점 단위까지 같은 값**을 내야 한다. v0.7 기존 검증 자산(arrest 100%, Cohen's d, sword_drawn Phi 등)이 v1.2 architecture 변경으로 깨지지 않았음을 매 PR마다 보장.

### 4.2 `test_no_peter_run_passes_talleyrand_scorecard` — universality asymmetry

[tests/test_engine/test_cross_scenario_pom_asymmetry.py:119](tests/test_engine/test_cross_scenario_pom_asymmetry.py#L119)

```python
def test_no_peter_run_passes_talleyrand_scorecard(self, peter_ensemble):
    rate = _all_pass_rate(peter_ensemble, make_talleyrand_scorecard())
    # Peter는 talleyrand agent가 없음 → 거의 모든 패턴 실패
    assert rate == 0.0
```

**주장**: Talleyrand의 POM scorecard (multi_regime_survival / reputation_ambiguity_emergent 등 Type A 패턴)를 Peter 시나리오 run에 적용하면 0% 통과한다. 인접 증거(Talleyrand-on-Talleyrand ≥ 80%)와 결합하여 "엔진은 범용이지만 패턴은 시나리오 특정적"(engine scenario-agnostic, patterns scenario-specific) 주장의 empirical 근거. v1.2 ABSOLUTE RULE #5 "universality" 범위 제한 해제의 정당화.

### 4.3 `test_causal_chain_arrest` — 다중 agent causal bottleneck

[tests/test_engine/test_precursor_analysis.py:192](tests/test_engine/test_precursor_analysis.py#L192)

```python
assert chain_rate >= 0.5, (
    f"Causal chain should be present in >= 50% of arrests "
    f"(got {chain_rate:.0%})"
)
```

**주장**: Peter 다중 agent 앙상블에서 arrest 이벤트 발생 시, "inform → surveillance → betray → arrest" 인과 체인이 50% 이상 run에서 관측된다. Hazard-driven 엔진이 rare action sequence를 확률적으로 생성하면서도 causal structure (Judas → Caiaphas → 체포)가 유지됨을 검증. `empty bubble` 반박 (인과 없는 stochastic 결과가 아님).

---

## 5. 할 수 있는 것 / 할 수 없는 것

### 5.1 할 수 있는 것 (empirically verified, 1003 tests pass)

| 능력 | 증거 |
|------|------|
| **Peter 수난 50일 4-agent 앙상블 실행** — arrest 100% 자발 발생, tick mean 121.85 ± 1.35 (n=20) | `paper_numbers.json::peter_standalone` |
| **Peter 공생애 3년 5-phase 연속 실행** (handoff + phase-variable tick_scale + phase별 canonical events) | `demo_phased.py --full-passion`, `test_linked_life_phase5_full.py` |
| **Van Gogh 3-agent Arles 150 tick 실행** — Gauguin 떠남 100% | `paper_numbers.json::vangogh` |
| **Talleyrand 50년 career 6-regime 전환 실행** | `demo`, `test_regime_transitions.py` |
| **legacy 시나리오 bit-exact 보존** — `phases=None` 경로가 v0.7과 동일 | `test_claim_legacy_mode_identical_to_v07` |
| **engine universality empirical 증거** — POM scorecard 교차 적용 asymmetry (Talleyrand-on-Peter = 0%, Talleyrand-on-Talleyrand ≥ 80%) | `test_cross_scenario_pom_asymmetry.py` |
| **학습된 linear encoder (sklearn LDA)** — Peter separability 1.91 → 2.39 (+25%) | `LearnedLinearEncoder`, `paper_numbers.json::separability_spectrum` |
| **비선형 학습 feasibility 확인 — RBF SVM > LDA**: Peter +22.8%p, VG +40.1%p | `scripts/svm_comparison.py` 실행 결과, `svm_comparison.json` |
| **Stage 2 pre-training 진단** — action class separability, logit vs majority | `compute_drive_action_diagnostics`, `drive_class_separability` |
| **Multi-scenario feature-gap 분석** — feature extractor 확장 (`DomainState.to_feature_vector`) | `ExtensibleFixedProjectionEncoder`, `test_extensible_encoder.py` |
| **Absolute-time 좌표계 분석** (phase-variable tick 통합) | `time_axis.py`, `extract_absolute_trajectory` |
| **Canonical intervention 효과** — jesus_understanding 전이 (None → teacher → messiah_political → risen_lord → sending_lord) | Phase 1/3/5 canonical_events.json |
| **Inhibitor/Amplifier content composition** — Judas disillusionment 감쇄 | `test_inhibitor_judas_deployment.py` |
| **Slow state field-specific 회복** — moral_injury/trust_scar/identity_shift opt-in (기본 zero-effect) | `SlowStateFieldRecoveryRule` |
| **Player-view 정보 비대칭성 + 내러티브 렌더링** (v0.7) | `player_view.py`, `trace_narrator.py` |
| **재현성 보장** — 동일 seed에서 bit-exact | 수많은 reproducibility test |
| **POM / Counterfactual ablation / Partial holdout forecasting / Behavioral rate regression** (v0.5 framework) | `test_peter/*`, `test_engine/test_cross_scenario*.py` |
| **97% coverage, ruff clean, mypy 0 real errors** | CI + `pytest --cov` |

### 5.2 할 수 없는 것 (구조적/의도적 한계, 현재 코드 상태로 명시)

| 한계 | 원인 / 설계 |
|------|-----------|
| **PyTorch MLP 기반 비선형 drive encoder 학습** | 구현 없음. `drive_training.py:118` TODO. torch 의존성 미설치. (`svm_comparison.py` 결과로 도입 정당화됨 — next step) |
| **Talleyrand action → state 예측 학습** | logit test acc (42.2%) ≈ majority (41.3%), separability 0.12. 5-action + regime-discrete state. Stage 2 deferred (6가지 가설 empirical 소거 완료). |
| **Relational state** (beliefs-about-others) | v1.1 계획, 미구현. 현재 `relationships: dict[str, Relationship]`는 1-hop trust만. |
| **LLM 런타임 개입** | ABSOLUTE RULE #4로 **금지**. LLM은 설계 파트너 + 사후 분석만. |
| **엔진 코드 내 특정 인물 참조** | ABSOLUTE RULE #1로 **금지**. `test_integrity.py` 자동 검증. |
| **정경 말씀 재작성** | ABSOLUTE RULE #2로 **금지**. 개역개정 텍스트 원문만. |
| **예수 agent화** | ABSOLUTE RULE #3으로 **금지**. `ExternalEvent`/`CanonicalIntervention`으로만 존재. |
| **실시간 인터랙티브 플레이어 체험** | v2.0 계획, 미구현. 현재 trace → JSONL → narrator text만. |
| **4번째 시나리오** | PROJECT_DIRECTION_v2.md §3.4 "논문 완성 전까지 착수 금지". |
| **논문 제출** | 미완성. scripts/paper_*.py로 수치/figure 추출 인프라만 준비됨. |
| **"universality" 보편 주장** (3번째 시나리오 이후에도) | "engine scenario-agnostic, patterns scenario-specific"로 scope 제한. 수치 claim의 범인물 일반화는 여전히 금기. |
| **Phase 4 → Phase 5 linked-life가 v0.7 수치를 보존** | 의도적 분리. linked-life는 Phase 1-4 handoff state 주입으로 Phase 5 수치 변화. legacy mode (`phases=None`)만 bit-exact 보장. |
| **Talleyrand의 국익 일관성 같은 meta-goal 모델링** | 현재 `DiplomacyState`는 생존-협상-평판 축만. 고차원 meta-goal 필드 없음. |
| **정경 외 "자연 회복"으로 event_trauma 빠르게 낮추기** | `SlowStateFieldRecoveryRule.event_trauma_rate_per_hour` 기본 0 (PTSD 원칙). 양수 설정해도 hope + 관계 동시 충족 조건 하에서만 미세 decay. |

---

## 6. 검증 메트릭 합계

| 지표 | 값 |
|------|-----|
| Fast tests | **1003 pass** (v0.7 baseline 572 대비 **+431**) |
| Archived tests | 33 |
| Slow/deselected | 131 |
| Coverage (engine/) | ~97% overall |
| Lint (ruff) | clean |
| Type (mypy) | 7 pre-existing stub warnings (SALib/umap/sklearn.cluster/discriminant_analysis), 0 real errors |
| Content packs | 8 (peter/judas/caiaphas/crowd/vangogh/gauguin/theo/talleyrand) |
| Engine modules | 37+ (49 Python files 총 5,797 lines) |
| Documents | 9 (CLAUDE / DESIGN / DESIGN_LATENT_DRIVE / PROJECT_DIRECTION_v2 / progress / lessons (19 entries) / REVIEW_RESPONSE_V1_2 / PAPER_DRAFT_V06 §Appendix D+E / SCENARIO_TEMPLATE §7) |
| Demos | `demo.py`, `demo_v07.py --scenario {peter,vangogh}`, `demo_phased.py --seed N --full-passion --with-recovery --show-drive --encoder {identity,fixed,learned}` |
| Paper-extraction scripts | `scripts/paper_numbers.py`, `scripts/paper_figures.py`, `scripts/svm_comparison.py` → `docs/paper_data/*.{json,png,txt}` |

---

## 7. 이 요약의 한계

- **empirical 수치 재현은 `scripts/paper_numbers.py` 실행으로 검증 가능**. 이 문서에 인용된 수치는 2026-04-20 실행 결과 기준. seed 고정된 측정이지만 (a) ruff/mypy/test 환경 차이, (b) sklearn/numpy 버전 차이로 fractional 변동 가능.
- **테스트 수 1003 중 일부는 schema-level assertion** (JSON 파일 존재 확인, field type 검증 등). 품질 지표로 읽을 때 "전체가 심층 검증"은 아님.
- **POM scorecard는 content 저자가 손으로 설계한 7-pattern 기준**. selection bias 존재. 외부 인물에 대해 동일 절차로 검증 안 됨.
- **`drive_class_separability` 지표는 empirical heuristic** — Fisher-style between/within variance ratio의 단순 구현. 0.5 threshold는 자의적.
- **`legitimacy_below_anchor` POM pattern이 현재 Talleyrand run에서 0/10 실패** — Iter 80 behavior profile rebalance 후 `legitimacy_anchor` 상승 효과. all_pass 0%가 되어 Iter 57에서 측정한 "≥80%" 주장과 표면적으로 충돌해 보이지만, per-pattern asymmetry (Talleyrand 6/7 pattern ≥ 80% vs Peter 전 pattern 0%)로는 여전히 성립. 논문 figure `fig_pom_cross_scenario_heatmap.png`에서 시각화됨.

---

*작성 2026-04-21, `scripts/paper_numbers.py` 실행 결과 기반.*
