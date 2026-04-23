# 34 Iteration 재분류 — v1.0 학습 엔진 전환용

> ChatGPT 5차 리뷰 기반. 각 iteration을 v1.0 Latent Drive Bottleneck 전환 관점에서 재사용/재해석/폐기 분류.

---

## A. 재사용 (High Value — 학습 엔진에도 그대로 이식)

### 검증 프레임워크 (가장 큰 자산)

| # | 분석/테스트 | v1.0 역할 |
|---|------------|----------|
| 1 | POM 7-pattern (Peter), 5-pattern (VG) | 학습 모델 출력의 pattern 적합성 검증 |
| 2 | Event-relative checkpoint (80.3%) | Latent drive 모델이 emergent timing 준수하는지 |
| 3 | Counterfactual ablation (Judas d=-6.87) | Drive 제거 실험의 기준 |
| 4 | Causal chain faithfulness (ρ=1.0, n=30) | Drive-based action이 설명 충실성 유지하는지 |
| 5 | Permutation test (p<0.001) | 비모수 유의성 검증 프로토콜 |
| 6 | Partial holdout train/test (CI=0.49) | Out-of-sample validation 프로토콜 |
| 7 | Spearman rank correlation | 학습 모델 예측력 재검증 |
| 8 | Sample size convergence (sqrt(n) scaling) | 학습 평가 시 최소 n 기준 |
| 9 | Proportion CI (Wilson score) | 학습 모델 성공률 CI |
| 10 | Bootstrap CI | 안정성 측정 |

### 인프라/아키텍처

| # | 요소 | v1.0 역할 |
|---|------|----------|
| 11 | Engine/content 분리 (0 hardcoding) | Drive 모델도 content에 분리 |
| 12 | Trigger system (symbolic) | **유지** — latent drive가 trigger susceptibility 조절만 |
| 13 | Hazard Poisson framework | 배경 event 생성 유지 |
| 14 | AgentScheduler | 그대로 |
| 15 | State/slow_state 분리 | drive는 slow_state와 동일 층위 |
| 16 | Canonical intervention 메커니즘 | 유지 |
| 17 | MultiAgentResult/checkpoint | 로그 구조 유지 |

### 발견 (v1.0 설계 가이드)

| # | 발견 | v1.0 활용 |
|---|------|----------|
| 18 | Judas disill 180t sensitivity / 그 외 0-23t | 어떤 드라이브가 실제 sensitivity를 만드는지 학습 목표 |
| 19 | Withdraw rate r=-0.94 (behavioral leading indicator) | 행동 → 상태 → 사건의 학습 순서 |
| 20 | Peter emotional arc (hope trough → grief peak +25 → fear peak +75) | 학습 모델이 이 순서 재현해야 |
| 21 | Cross-scenario POM bottleneck isomorphism (sword_drawn ↔ self_harm Phi=0.95+) | Drive 공간에서 일반화되는 rare-action 구조 |
| 22 | Peter deny count 97% ≥ 3 (POM triple_denial 자연 발생) | 학습 후에도 보존되어야 할 emergent pattern |
| 23 | Linear disill trajectory (R²=0.998) | 학습 모델 regularization 기준 |
| 24 | Cross-agent coupling (Judas↔Peter r=0.76, Judas↔Caiaphas r=0.89) | Relational layer(v1.1)의 기초 |

---

## B. 재해석 (Middle Value — 학습 레이어 위에서 의미 재정의)

| # | 기존 해석 | v1.0 재해석 |
|---|----------|------------|
| B1 | Feature importance (현재 state-based) | Drive axis importance로 재표현 |
| B2 | Rule-family comparison (homeostasis, emotional 등) | Symbolic rule + learned drive의 역할 분담 |
| B3 | Handcrafted state importance (fear/grief/hope 개별 효과) | Latent drive가 이들을 projection으로 재구성 |
| B4 | Univariate vs Multivariate forecast | Latent drive single-dim이 multi-state를 대체 가능한지 |
| B5 | Terminal attractor (Judas 10.0 saturation) | Drive saturation으로 재해석 ("자기파괴 drive 극한") |
| B6 | Decision window (tick 75-100 std peak) | Drive gradient가 최대인 구간 |
| B7 | Action rate regression (time-confound 없는 판) | Drive-action mapping 학습 타겟 |
| B8 | Trigger sensitivity audit (±20% → 44t shift) | Drive-trigger coupling strength 학습 |

---

## C. 폐기 또는 hard demotion (Low Value for v1.0)

| # | 항목 | 이유 |
|---|------|------|
| C1 | "Phase transition" 용어 전체 | 4차 리뷰에서 기각. Linear + threshold로 교정 완료 |
| C2 | "Historical inevitability" 주장 | 4차 리뷰에서 기각. Model saturation으로 교정 |
| C3 | 특정 rule 내부 parameter 미세 tuning | 학습층 도입 시 쓸모 없어짐 |
| C4 | Hardcoded threshold (disill=8, threat=7 등) | Learned susceptibility로 대체 |
| C5 | behavior_profile.json weights 고정값 | Latent drive → action weight 산출로 대체 |
| C6 | "Universality 주장" 현재 사용처 | 3번째 시나리오 전까지 미사용 |
| C7 | 중복 상관 분석들 (여러 방식의 같은 점 검증) | 핵심 2-3개만 남기고 제거 |
| C8 | 일부 rare test (raw histogram peak count) | 신뢰성 낮은 검정 제거 |

---

## 요약 수치

- **재사용**: 24 항목 (검증 프레임워크 10 + 인프라 7 + 발견 7)
- **재해석**: 8 항목
- **폐기**: 8 항목

**결론**: 절대 다수가 재사용 가능. 폐기는 주로 용어 과장과 hardcoded 세부사항. **34 iteration은 v1.0의 기초로 대부분 살아남는다.**

---

## 구체적 테스트 파일 매핑 (v0.5 논문 narrative 선별용)

### Tier 1 — 논문 핵심 narrative (8개 선정)

| 테스트 파일 | 섹션 | 발견 |
|------------|------|------|
| `test_emergent_arrest.py` | §6.1 | 100% 자발 체포 발생 |
| `test_permutation_judas.py` | §6.2 | Judas counterfactual p<0.001 |
| `test_pom_bootstrap.py` | §6.3 | POM bottleneck sword_drawn Phi=0.95 |
| `test_vg_pom_bootstrap.py` | §6.3 | VG POM bottleneck self_harm Phi=1.0 (isomorphism) |
| `test_partial_holdout_generalization.py` | §5.5 | 첫 external validity (disill train 83% / test 88.9%) |
| `test_cross_scenario_ks.py` | §6.4 | KS D=0.567 (dual-layer surface differ) |
| `test_disill_trajectory_shape.py` | §6.5 | Linear R²=0.998 (not phase transition) |
| `test_action_rate_regression.py` | §6.8 | Time-confound 제거 → withdraw r=-0.94 |

### Tier 2 — 보조 figure/appendix

| 테스트 파일 | 역할 |
|------------|------|
| `test_forecast_n100_replication.py` | n=100 replication (sample robust) |
| `test_hartigan_dip.py` | Modality 검정 3종 합의 |
| `test_explanation_faithfulness_extended.py` | Faithfulness ρ=1.0 |
| `test_cross_agent_coupling.py` | Judas↔Peter r=0.76 |
| `test_peter_emotion_arc.py` | Peter 감정 arc |
| `test_negative_controls.py` | 금지 결과 억제 |
| `test_phase_transition.py` | Threshold response (이름 유지, 본문 교정됨) |
| `test_sample_convergence.py` | sqrt(n) scaling |

### Tier 3 — Archived (paper 제외, repo 유지)

중복/시간-confound/재해석-필요 분석들. v0.5 paper narrative에서 빠지지만 repo에는 역사적 기록으로 유지.

| 테스트 파일 | 이유 |
|------------|------|
| `test_action_regression.py` | Time-confound (rate 버전이 대체) |
| `test_peter_weep_forecast.py` | Downstream indicator 확인용 (causal 기여 약함) |
| `test_multi_horizon_withdraw.py` | 5 horizon 세부분석 (요약값만 paper에) |
| `test_vg_behavioral_signal.py` | Cross-scenario 확인 (action rate가 대표) |
| `test_vg_emotion_arc.py` | Peter emotion arc와 유사 |
| `test_vg_time_to_threshold.py` | Peter 판과 유사 |
| `test_tick100_analysis.py` | Decision window 세부 (summary만) |
| `test_narrative_anomaly.py` | Anomaly run 분석 (부차적) |
| `test_seed_sensitivity.py` | CV 분석 (summary로) |
| `test_multi_sensitivity.py` | Sensitivity audit (partial holdout으로 대체) |
| `test_peter_param_importance.py` | Peter-side parameter (Judas asymmetry 확인용) |
| `test_initial_perturbation.py` | Stability (summary로 편입) |
| `test_arrest_distribution.py` | Sarle BC (Hartigan dip이 대체) |
| `test_judas_action_sequence.py` | Markov 분석 (보조) |
| `test_disill_greed_interaction.py` | 2x2 factorial (param importance로 편입) |
| `test_withdraw_noise_robustness.py` | Noise 견고성 (summary로) |

### Tier 4 — 엔진/인프라 테스트 (논문 무관, 필수 유지)

`test_integrity.py`, `test_rules.py`, `test_event.py`, `test_hazard.py`, `test_loader.py`,
`test_checkpoint.py`, `test_trigger.py`, `test_world.py`, `test_scripture.py`, 기타 30+.

**이들은 논문 narrative가 아니라 엔진 correctness 보장용. 전부 유지.**

### Tier 5 — v0.7 trace pipeline 테스트 (신규, 2026-04-19 추가)

v0.7 Stage 1 인프라 검증용 테스트 (counts 2026-04-19 기준):
- `test_trace_emitter.py` — §2 entry emitters (10 tests)
- `test_trace_narrator.py` — TraceEvent → narrative (17 tests)
- `test_trace_integration.py` — 실제 Peter 시뮬 E2E (10 tests, visible_signal/observable_from 검증 포함)
- `test_trace_fields.py` — ActionRecord 필드 확장 (7 tests)
- `test_bifurcation.py` — decision window 탐지 (13 tests, smoothing/significance/top_k 포함)
- `test_player_view.py` — 정보 비대칭성 필터 (§3.1) (12 tests)
- `test_training_samples.py` — Stage 2 sample extraction (12 tests, SampleStatistics 포함)
- `test_drive_training_pipeline.py` — Stage 2 skeleton (11 tests)
- `test_latent_drive.py` — 4 Protocol + Identity impls (8 tests)
- `test_content_pack_structure.py` — 7 pack 구조 검증 (9 tests)

Tier 5 총 **109 tests** (fast-suite 포함). v0.7 본체와 함께 유지. v1.0 Stage 2 PyTorch 구현 시 훈련 loss 계산 테스트 추가 예정.

---

## Paper 선별 원칙

- **Tier 1**: 논문 main body figure + 섹션 narrative. 8개.
- **Tier 2**: Appendix / supplementary figure. 8개.
- **Tier 3**: Archived (repo 유지, paper 언급만 혹은 제외). 16개.
- **Tier 4**: 엔진 테스트 (논문 외, 유지 필수).
- **Tier 5**: v0.7 trace pipeline 테스트 (2026-04-19+ 신규).

**총계**: 논문에 주로 등장하는 분석 = Tier 1+2 = **16개** (34 중).
**결론**: ChatGPT 지적 "8-10 핵심 + 보조 선별" 기준 만족.

## v0.7 완료 기록 (2026-04-19)

- Stage 1 infrastructure 완료: latent_drive 4 Protocol + Identity impls, bifurcation detector (smoothing/significance/top_k), trace_emitter (§2 entries 5종), player_view (§3.1 filter), trace_narrator (v2.0 preview).
- Content-driven narrative: `AgentAction.visible_signal` + `observable_from` 필드, 전 7 content pack 22 actions에 한국어 서사 + 정보 비대칭성 설정.
- Stage 2 skeleton: training_samples (SampleStatistics diagnostic), drive_training (identity fallback + 학습 파이프라인 API), samples_to_feature_matrix.
- 인프라: `.github/workflows/ci.yml`, `benchmarks/bench_simulation.py` (Peter 1001 tick/s, VG 1267 tick/s baseline).
- **Fast tests: 530** / Archived: 33 / Total: 661. **Coverage: 96%**. mypy strict clean.
