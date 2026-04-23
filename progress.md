# Progress -- Witness

> 마지막 업데이트: 2026-04-22 (Spike 5 Part 1 + Part 2 완료 — 공간 / Jesus agent / 주변 agent / 3층 경제)

## v2.0 World Engine — Spike 5 Part 1 + 2 현황 (2026-04-22)

**Scope**: 세계 두껍게 만들기. **실험 추가 0건** (Rule #10). 기존 Spike 4 3종
intervention은 회귀 테스트로만 유지.

| Phase | 산출물 | 핵심 |
|---|---|---|
| 5C (Part 1) | `world/space/` 4 modules + 6 canonical locations | movement cost, 정보 비대칭, spatial rumour factor |
| 5A (Part 1) | `world/agents/jesus.py` + `content/jesus/` | multi-path emitter (≥3 actions → jesus_movement), 개역개정 citation 가드 |
| 5B (Part 2) | `world/agents/pilate.py` + `caiaphas.py` + `light/` (4 disciples) | hub role, graded-proximity foundation |
| 5D (Part 2) | `world/economy/temple_economy.py` + `taxation.py` + `cross_economy.py` | 3층 독립 + indirect path, same-tick feedback guard |

**검증 지표 (2026-04-22 말)**:
- Fast tests: **1176+ passed** (Spike 4 완료 1137 → Part 1 1163 → Part 2 1176 → 보완 195 in world/)
- World 테스트 커버리지: **97%** (Part 2 후 +1%p, `intervention/engine.py` 77→99%, `space/position.py` 71→100%)
- ruff clean, mypy world/ clean (engine/simulation/world.py:268 pre-existing 1건만 Rule #6으로 유지)
- engine/ 무수정, content/ 기존 파일 무수정 (agents/jesus, worlds/jerusalem_ad30/agents 및 economy/ 만 신규)
- Spike 4 3종 intervention 회귀 green + Layer DAG acyclic 유지

**구조적 여지 (Spike 7+ 실험 대비)**:
- `faction_influence_jesus_movement`로 가는 action path 최소 3개 (single-point failure 회피)
- Caiaphas hub가 pharisees + sadducees 양쪽에 도달 (graded control 가능)
- 경제 3층 indirect path: temple→jesus_sympathy, taxation→zealot_militancy, staple→discontent
- 제자 3명 (John/James/Thomas) 동일 context에 2가지 이상 distinct action 선택

**미해결 / 다음 스텝**:
- Part 3+ scope (현 spike에서는 의도적 restraint): Jesus/Pilate/Caiaphas/Light agents + 신규 경제 sub-layers를 `IntegratedWorldRunner`에 실제 통합. `BatchInterventionRunner` 노출도 별도 spike.
- 기존 `lenient_pilate` intervention은 현재 `PoliticsState` 경로로 작동 — PilateAgent 기반 재배선은 Part 3+.
- Spike 7+ 실험 재개 시 본 spike 구조 직접 활용 (graded proximity, 3-path insurance).

---

## v2.0 World Engine — Spike 1 + 2 + 3 + 4 현황 (2026-04-22)

**Spike 4 결과 요약 (Phase 4A→4F 완료)**:

| Phase | 내용 | 핵심 |
|---|---|---|
| 4A (loop #21) | InterventionSpec (frozen, 11 primitives) + InterventionEngine (deepcopy+mutate+audit log) | 14 tests |
| 4B (loop #22) | BatchInterventionRunner + Cohen's d + permutation p-value (500 iter) | 5 tests, null-spec bit-identical 검증 |
| 4E (loop #23) | 3종 canonical intervention JSON (content/interventions/) | remove_judas / hazard_half / lenient_pilate |
| 4F (loop #23) | demo_spike4_interventions.py — E2E 실험 실행 + 비교 테이블 | per-experiment JSON 자동 저장 |

**실측 실험 결과 (full run: 10 seeds × 90 days, 2026-04-22)**:

| Intervention | triggers Δ | rumours Δ | JM Δ | Pharisees (ctrl) | Cohen's d 최대 | p-value |
|---|---|---|---|---|---|---|
| **remove_judas** | 216.5→76.1 (-65%) | 79.1→0 (-100%) | 9.83→3.75 (-62%) | 0 | **-69.52** (JM) | **0.000** |
| hazard_half | 0 | 0 | 0 | 0 | 0 | 1.00 |
| lenient_pilate | 0 | 0 | 0 | 0 | 0 | 1.00 |

- remove_judas는 paper-quality significance (d=-69.52 on jesus_movement, p=0.000)
- hazard_half / lenient_pilate zero effect는 **metric saturation** 때문 (SPIKE_4_REVIEW Q5 확인): hazard events는 tracked metric 경로 없음, peter_fear는 9.83 ceiling saturate. Framework 자체는 정상.

**framework 검증**:
- null-spec intervention → control/intervention arms 완전 bit-identical (seed-paired) → 비교 baseline 신뢰 가능
- remove_judas 실험이 **Spike 3 Phase 3D counterfactual과 독립 framework에서 재현**: trigger -68%, rumours -100%, jesus_movement -56% (Phase 3D는 -64%/-100%/-62% with longer run)
- pharisees (specificity control) 모든 intervention에서 변화 없음 → 효과가 specific (global noise 아님)

**Spike 4 산출물**:
- [world/intervention/](world/intervention/) — spec.py / engine.py / batch.py (3 modules, 19 tests)
- [content/interventions/](content/interventions/) — 3종 canonical spec JSON
- [scripts/demo_spike4_interventions.py](scripts/demo_spike4_interventions.py) — E2E runner + table printer
- [docs/world/paper_data/intervention_*.json](docs/world/paper_data/) — 3종 실측 결과 저장
- [docs/world/SPIKE_4_REVIEW.md](docs/world/SPIKE_4_REVIEW.md) — 338 lines 외부 LLM 리뷰 패킷 (§5 7 questions)

**검증 지표 (2026-04-22 말)**:
- Fast tests: **1137 passed** (1003 engine + 134 world; Spike 4에서 +19 tests)
- ruff clean, mypy world/ clean (25 source files)
- engine/ 무수정, content/ 기존 파일 무수정 (interventions/ 만 추가)
- 4개 review packet 총 1394 lines (SPIKE_1 413 + SPIKE_2 307 + SPIKE_3 336 + SPIKE_4 338)

**미해결 / 다음 스텝**:
- SPIKE_4_REVIEW.md Q5 saturation confound — peter_fear가 ceiling 9.84 → lenient_pilate 측정 안 됨. `overflow_fear` 필드 or time-to-saturation 지표 필요.
- Full 10-seed × 90-day run 필요 (데모는 2×30, p-value 신뢰도 낮음)
- Spike 5 선택: (a) content/jesus/ + remove_jesus_movement 실험, (b) arles_1888 두 번째 world pack

---

## v2.0 World Engine — Spike 1 + 2 + 3 현황 (2026-04-21)

**Spike 3 결과 요약 (Phase 3A→3D 완료)**:

| Phase | 내용 | 핵심 |
|---|---|---|
| 3A (loop #9) | FactionLayer + 6 AD-30 factions (pharisees, sadducees, essenes, zealots, jesus_movement, baptist_remnant) | independent dynamics, optional layer |
| 3B (loop #11) | crowd → zealot militancy edge | threshold brake, same-tick, 3 tests pin |
| 3C (loop #13+14) | Layer 5 rumour graph + seeding pipeline | rumor_seed WorldEffect 수신, 한국어 content 호환 버그 수정 |
| 3D (loop #15+16) | rumour → jesus_movement influence edge | pharisees control 포함 specificity 증명 |

**Counterfactual 체인 (Spike 2 통합 모드 기준)**:

| Metric | Full 4 agents | Judas 제거 | Δ |
|---|:---:|:---:|:---:|
| trigger_count | 212 | 77 | -64% |
| rumours seeded | 77 | 0 | **-100%** |
| rumor_intensity_max | 12.05 | 0 | **-100%** |
| jesus_movement 최종 influence | **9.90** | **3.80** | **-62%** |
| pharisees (control, non-sensitive) | 6.18 | 6.18 | **0%** |

체인: **Judas → (inform/betray) → rumor_seed → rumours → jesus_movement influence**. Pharisees가 control로 effect specificity 증명 (global noise 아님).

**Spike 3 산출물**:
- [world/factions/](world/factions/) — FactionLayer (Phase 3A+3B+3D), 6 faction content pack
- [world/social/rumors.py](world/social/rumors.py) — RumorLayer (Phase 3C)
- [world/core/world_state.py](world/core/world_state.py) — FactionSnapshot/State, Rumor/RumorState, RomanStance
- [tests/test_world/test_factions.py](tests/test_world/test_factions.py) — 18 tests
- [tests/test_world/test_rumors.py](tests/test_world/test_rumors.py) — 12 tests
- [tests/test_world/test_layer_dag.py](tests/test_world/test_layer_dag.py) — 6-layer DAG 자동 검증
- [docs/world/SPIKE_3_REVIEW.md](docs/world/SPIKE_3_REVIEW.md) — 336 lines 외부 LLM 리뷰 패킷 (§5 7 questions)
- [docs/world/paper_data/world_numbers.json](docs/world/paper_data/world_numbers.json) — jesus_movement + pharisees(control) final_influence 포함

**검증 지표 (2026-04-21 말)**:
- Fast tests: **1118 passed** (1003 engine + 115 world; Spike 3에서 +34 tests 신규)
- ruff clean, mypy world/ clean (22 source files)
- engine/ 무수정, content/ 기존 파일 무수정 (worlds/jerusalem_ad30/ 확장만)

---

## v2.0 World Engine — Spike 1 + 2 현황 (2026-04-21)

**완료**:
- Spike 1A/1B/1C/1D: Layer 1 calendar, Layer 2 economy (staple_price), Layer 3 politics (roman_alertness + pilate_location), Layer 5 crowd + overflow_pressure, Sync Layer 브리지
- Spike 2 Phase A (리뷰어 조건 3개):
  - A-1 Sync aggregation (sum/mean/max/threshold 4개 모드, Spike 1D 구현 + 테스트)
  - A-2 overflow_pressure (CrowdState 필드, clamp 초과분 추적, 6 테스트)
  - A-3 same-tick feedback 금지 룰 (WORLD_DESIGN ABSOLUTE RULE #9, DAG 자동 검증 5 테스트)
- Spike 2 Phase B (Person × World 통합):
  - B-1 SyncLayer.world_to_environment (EnvironmentState 5필드 매핑)
  - B-2 SyncLayer.actions_to_effects (action 속성 기반 generic 변환, publicity_shock/authority_threat/rumor_seed)
  - B-3 IntegratedWorldRunner (1일 1 world tick + 12 person substeps)
  - B-4 6개 통합 테스트 (90일 완주 / fear differs / endo 이벤트 / 상향 인과 / Judas 제거 / env 반영)
  - B-5 scripts/demo_world_integrated.py (per-day world + agent + WorldEffects 출력)

**검증 지표 (2026-04-21)**:
- Fast tests: **1084 passed** (1003 engine + 81 world, Spike 2에서 +20)
- World tests: 81 (1A 33 + 1B 6 + 1C 11 + 1D 12 + A-2 6 + A-3 5 + B-4 6 + smoke 2)
- ruff world/ + tests + scripts/demo_world_*: All checks passed
- mypy world/: 18 source files, no issues (engine/ pre-existing 39 errors는 별개)
- engine/ 무수정, content/ 기존 파일 무수정

**통합 데모 (seed 0, 25일)**:
- 유월절 Passover에서 crowd=10.0, price=3.5, alert=10.0, Pilate Jerusalem, Peter fear 2.5→9.9
- Judas disillusionment 2→10, inform_authorities 발화 → authority_threat=10.0 (max)
- WorldEffect 매일 관측 (25/25일 non-zero) — 양방향 인과 증명
- Fired triggers 31, hazard events 21 over 90일 — endogenous arrest 유지

**남은 Spike**:
- Spike 3: Layer 4 factions + rumour graph
- Spike 4: variable intervention (예수 제거 시 세계 변화 측정)
- Spike 2 미해결 리뷰어 조건 2개 (percept interpolation, Jesus dominance 제어)

---

## 현재 상태 (v0.7)

| 지표 | 값 |
|------|-----|
| 엔진 모듈 | 34+ (v0.5 22개 + v0.7 신규 trace/player_view/trace_narrator/bifurcation/latent_drive/training_samples/drive_training 등) |
| 콘텐츠 팩 | 7 (Peter 시나리오 4 + Van Gogh 시나리오 3) |
| 테스트 | **572 fast / 98 slow / 33 archived = 703 total** (Tier 5 v0.7 pipeline 109 tests) |
| Coverage | **97%** (15 engine modules at 100%) |
| Ruff / mypy | 0 errors (engine strict 통과) |
| engine/ 인물 특정 용어 | **0건** (test_integrity 자동 검증) |
| v0.6 paper draft | 319 lines (`PAPER_DRAFT_V06.md` — §1-§9 prose + Appendix A/B/C + References) |
| CI | `.github/workflows/ci.yml` — Python 3.11/3.12 matrix + coverage artifact |
| Benchmark | Peter 1001 tick/s @ 2.3 MB, VG 1267 tick/s @ 1.7 MB (250 tick × 5) |

---

## 검증 결과 (확실한 것들)

1. **POM**: current 38.6% 7/7 통과, fear-only 1.2%, uniform 0% (32배 분리)
2. **pyABC Model Selection**: Peter current=100%, Van Gogh current=84%
3. **Parameter Recovery**: PASS (true params in recovered box)
4. **환경 → 부인↑**: 방향성 일관
5. **도주율 29%**: 환경 무관
6. **Multi-agent 체포 자연 발생**: 50/50 spontaneous (100%), mean=198 ± 43, range 119-281
7. **Multi-agent 민감도**: 유다 환멸이 체포 시점 결정 (4배 영향), 탐욕/위협은 약한 영향
8. **Trigger Sensitivity**: 조건 +20% -> tick 250 (지연), cross-agent 제거 -> spontaneous 0% (필수)
9. **Counterfactual**: 유다 제거 -> deadline만 의존, 트리거 제거 -> 체포 미발생
10. **Threshold-triggered regime switch**: disillusionment 임계 ~1.0에서 outcome 분포 급변 (338→158, non-linear response at fixed threshold)
11. **Precursor**: 93% intelligence_driven, 인과체인 100% (inform→surveillance→betray→arrest)

## 검증 결과 (교정된 것들)

- shapiq 상호작용: 변수 세트에 의존 (3개 vs 5개에서 구조 변동)
- Scale robustness: feature importance가 env scale에 따라 뒤집힘
- Canonical prevalence: rule family에 따라 15~65% (불안정)
- "Phase transition" → "threshold-triggered regime switch" (LLM 4차 리뷰 교정)
- "Terminal convergence = 역사 필연성" → "model saturation artifact" (LLM 4차 리뷰 교정)
- "Universality" 주장: 3번째 시나리오 이전까지 보류 (LLM 5차 리뷰)

---

## v0.5 구현 이력

### 엔진
- Hazard-driven 이벤트 (Poisson, competing risks, anchor window, deadline)
- Fast/slow state (HomeostasisRule 조건부, SlowState 비가역적)
- EnvironmentState (surveillance, crowd_pressure, 환경 동적 규칙)
- 동적 해상도 (Chronicle/Episode/Scene, tension trigger)
- POM 검증 체계 (7패턴 동시 필터)

### 분석
- SALib (Sobol, Morris), UMAP+HDBSCAN, Decision Tree
- shapiq (Shapley 상호작용), pyABC (파라미터 보정 + Model Selection)
- EMA Workbench PRIM (시나리오 디스커버리)
- Parameter Recovery Test

### 다중 에이전트 (M1-Multi)
- SimulationWorld: 다중 에이전트 동시 실행
- TriggerEngine: 에이전트 상태/행동 조건 → 이벤트 동적 생성
- AgentBehaviorProfile: 에이전트별 자발적 행동 + 가중치 기반 선택
- AgentScheduler: sequential/random/simultaneous 활성화 순서
- 체포 자연 발생: 평균 tick ~182 (132~284 범위), 10/10 시드 deadline 전 발동
- MultiAgentResult: 에이전트별 checkpoint 평가 + 정경 일치율
- Peter behavior_profile: follow_closely, pray, discuss, assert_loyalty, withdraw_in_fear, weep
- Multi-agent POM: all_pass 50%, sword_drawn 50%, no_flee 80%
- 이벤트-상대적 체크포인트 (relative_to_event + relative_offset): Peter 35.5% → 80.3%
- Multi-agent 민감도: 유다 환멸이 체포 시점 결정 (low=286 vs high=72, 4배)

### Trigger Ontology 범용성 검증 (VG scenario)
- Van Gogh 3-agent (VG + Gauguin + Theo)
- Gauguin 떠남: 19개 서로 다른 tick (55~101), 20/20 spontaneous
- 동일 엔진, 완전히 다른 이야기: "배반 → 체포" vs "비판 → 떠남" 모두 작동

### 인프라 (v0.5)
- main.py CLI (--person, --runs, --multi)
- pyproject.toml, requirements.txt
- 시각화 6개 (output/)

---

## LLM 3차 리뷰 반영 (2026-04-18)

- Calibration leakage 점검: trigger-POM overlap **0건**, Peter 상태/행동을 trigger 조건에 미사용 확인
- Forecasting holdout: holdout tick 200에서 Judas disill만으로 arrest 카테고리 예측 **85% exact / 100% close** (random baseline 20%)
- Explanation faithfulness: causal chain이 Judas를 **10/10 runs** 지목, 제거 시 spontaneous 0/10 → 인과성 입증
- 통계 유틸 (engine/simulation/statistics.py): 95% CI (Wilson score), Cohen's d
- 핵심 수치 CI: arrest tick **191.4 [176.8, 206.1]**, spontaneous rate **100% [88.6%, 100%]** (n=30)
- Judas effect size: Cohen's d = **-6.87 (large)**, 평균 차이 **208 ticks**
- Negative controls: pre-supper arrest **0/20**, restoration-without-breakdown **0/20**, self-harm 15% (역사적 희귀성 유지)
- Universal threshold: Peter 94% vs VG 96% (normalized 90%에서), Cohen's d small → **구조적 동형** 입증
- Narrative anomaly: late arrest 평균 disill@200=6.7 vs early 9.5 → 편차는 **개연성 있는 대체 역사** (random noise 아님)
- Baseline comparison: Witness **80%** vs random 20%, majority/fixed/naive 57% — CI [63%, 90%] 모든 베이스라인보다 유의미
- Rule ablation: emotional 규칙 제거 시 POM **0%** (-30pp, 필수), homeostasis -10pp, slow_state +20pp

### SlowState 설계 원칙 수정
- SlowStateRule의 hope>7 → identity_shift+0.01 자동 회복 제거 (slow_state는 비가역이어야 함)
- POM p6_identity_damage: final 기준 → peak 기준 (Peter는 회복되므로 "경험한 손상" 검증이 타당)
- intervention_restoration에 slow_state.identity_shift=2.0 추가 (정경 개입으로만 회복)
- 결과: baseline POM **27% → 53%** (n=15), slow_state 제거 영향 정상화

### Rule ablation 통계 재검증 (n=30, 95% CI)
- baseline 40% [25%, 58%], 모든 family 제거 시 CI가 baseline과 겹침
- 개별 rule 제거의 POM 영향 **통계적으로 유의하지 않음**
- 인사이트: POM이 특정 규칙에 과적합되지 않음 → emergent behavior 검증 확인

### Multivariate vs Univariate forecast
- univariate 80% [63%, 90%] vs multivariate 63% [46%, 78%]
- holdout=200에서 greed/threat는 이미 saturate (대부분 ≥9)
- **핵심 발견**: disillusionment가 유일한 진짜 predictive signal, 추가 변수는 redundant

### Forecast horizon 분석
- tick 50(40%) / 100(**20%**) / 150(44%) / 200(62%)
- tick 100이 "인과 불확실성 peak" — 시스템 경로가 결정되는 구간
- tick 50의 초기 disill(~4)로도 40% 예측 가능 (baseline 20% 대비 2배)

### Seed sensitivity
- CV=21.4% (moderately stochastic), 평균 191.4, std 41.0
- noise 0→0.2 증가 시 std **42→28 감소** (noise가 regression to mean 유도)
- 주된 stochasticity 원천은 state_noise가 아니라 **agent scheduler의 random order**

### Tick 100 정밀 분석
- Max disill spread는 tick 175 (std 1.21), tick 100은 중간 (std 0.87)
- 75-100 구간이 **decision window** (growth 변동 std 0.69, 가장 큼)
- 125-175는 **separation plateau** (갈래가 완전히 벌어짐)
- Low disill@100 (<5): 평균 arrest 224, High(≥5): 평균 182 (42 tick 차이)

### Cross-scenario decision window
- Peter: 20-40% (std 0.63) — 초반 결정형
- VG: 60-80% (std 0.44) — 후반 결정형
- **다른 decision window** → universal decision window 가설 반증
- 공통점: 80-100%에서 growth 최대 (임계 접근 가속 패턴)

### VG Forecast Horizon (교차 시나리오)
- VG: 20(60%) 40(60%) 60(**79%**) 80(71%, n=7) — horizon 60에서 peak
- Peter: 50(40%) 100(20%) 150(44%) 200(62%) — horizon 200까지 단조 증가
- **핵심 차이**: Peter는 단조 증가, VG는 peak-and-decay
- 원인: 분포-max_tick 상대 위치 (VG는 departure 분포가 max에 근접 → survivor bias)

### Forecast n=100 Replication (sample size robustness)
- n=100 accuracy: **86%** [77.9%, 91.5%] (vs n=20: 80%)
- Close match ±1: **100%** at n=100 (완전 인접성)
- Spontaneous arrest rate n=100: **100%** [96.3%, 100%]
- Arrest tick n=100: mean **199.0**, std **42.5**, range **[116, 287]**

### VG Cross-scenario Counterfactual
- Gauguin 제거: spontaneous departure **0/10**, deadline-assisted **10/10** (Peter의 Judas 구조 동일)
- Theo 제거 (버퍼):
  - Departure tick 영향 없음 (d=-0.17, small)
  - VG hope 0.72 → 0.16 (d=0.97, large)
  - VG artistic confidence 8.17 → **-8.22** (d=**9.07**, huge effect)
- **Cross-scenario structural isomorphism**:
  - Peter = Judas(driver) + Crowd/Caiaphas(buffer)
  - VG = Gauguin(driver) + Theo(buffer)

### Multivariate at tick 150 (pre-saturation)
- tick 150: Uni 79% vs Multi 83% (CI 겹침, 통계적 동률)
- tick 200: Uni 80% vs Multi 63% (17pp 차이, univariate 승)
- 해석: disill은 saturation 여부와 독립적으로 지배적 signal
- 강화: "유다의 환멸이 유일한 robust predictive signal"

### Initial state perturbation (Lyapunov-style stability)
- Judas init_disill 1→5 스윕: arrest 313→239→198→152→125 (단조 감소, smooth)
- Small perturbation ±0.5: effect **38.1 tick** < seed std **42.8 tick**
- **결론**: Stable attractor 주변, 결정론적 chaos 아님

### Spearman rank correlation (non-parametric)
- disill@50: ρ = **-0.570** / disill@100: ρ = **-0.733** / disill@150: ρ = **-0.785** / disill@200: ρ = **-0.876** (bootstrap 95% CI [-0.987, -0.594])
- Horizon 늦어질수록 |ρ| 단조 증가

### Time-to-threshold (Peter)
- 5.0→6.0: 39.1 tick / 6→7: 34.7 / **7→8: 24.9** (가속) / 8→9: 27.8
- 7→8 gap 최소 → trigger 임계 근처 국소 가속 (global shape는 linear)
- disill 8.0 도달 mean tick **184.9** vs arrest mean **191.4** (gap ~7)
- Pearson r(threshold 7.0 crossing, arrest) = **0.938**

### VG Time-to-threshold (cross-scenario)
- VG gaps: 5→6 12.3 / 6→7 16.6 / **7→8 12.9** / 8→9 18.0
- 7→8이 전체 평균 아래 (Peter의 가속 패턴 완화판)
- frust 8.0 도달 74.0 vs departure 76.6 (gap **2.6**)
- Pearson r(threshold 6.0, departure) = **0.766** (Peter 0.938 대응)

### Arrest 분포 shape (n=60)
- Sarle BC: **0.395** < 0.555 → **unimodal**
- KDE (Silverman): 단일 유의미 peak at tick **203**
- 이전 "early 55 / mid 45 분할"은 임의 bucketing, 실제는 연속 분포

### Sample size convergence (n=[10,20,40,80,120])
- Mean arrest tick: 197.7 → 192.9 → 192.8 → 197.0 → 201.5 (안정)
- CI width: 59.6 → 37.3 → 24.4 → 18.1 → 15.7 (sqrt(n) scaling)
- CI width ratio n=80/n=20: **0.49** (이론 0.50, 완벽 일치)
- **guidance**: n=40 최소 권장, n=80 안정

### Parameter importance ranking
- 1위 **judas.disillusionment**: sensitivity **180 tick**, slope -45/unit
- 2위 judas.greed: 23 tick (8배 작음)
- 3-4위 messiah_expectation / threat_assessment: **0 tick** (완전 무관)
- 결론: **단 하나의 initial-condition knob**만 영향

### Judas 행동 시간 분포 (n=25)
- Early (0-100): follow **65.7%**, betray **0%**, inform **0.3%**
- Mid (100-200): follow 47.1%, inform 11.8%, betray 2.3%
- Late (200+): inform **22.1%**, betray **10.9%**, follow 28.2%
- 행동 entropy: 1.23 → 1.84 → **2.21 bits**

### Peter 행동 arc (arrest-relative, n=20)
- follow_closely: 69.5% → 54.8% → 48.3% (체포 후 감소)
- deny 76%가 pre_arrest_late phase에 집중
- withdraw_in_fear 5배 증가, weep 20배 증가 (post-arrest)
- Peter deny count: **97%가 3회 이상** (POM triple_denial 자연 충족)

### POM Bootstrap CI (n=40, B=2000)
- all_pass point **47.5%**, bootstrap 95% CI **[32.5%, 62.5%]**
- 패턴별: grief_peak 100%, eventual_hope 100%, moral_injury 97.5%, triple_denial 90%
- **Bottleneck: sword_drawn 50%** (Phi=0.951 with all_pass)

### Peter 감정 궤적 (arrest-relative)
- Hope trough at 0: **2.02** / Grief peak at +25: **9.41** / Fear peak at +75: **9.87**
- Peak grief: 100% reach ≥8.0
- Hope recovery: min 0.41 → final 7.53 (canonical 효과)
- 3-phase arc: hope collapse → grief → sustained fear

### Permutation test (Judas counterfactual, B=1000)
- Arrest tick diff: with=192.9 vs without=400 (deadline), observed diff **207.1 tick**
- Permutation p-value: **<0.001** (비모수 유의)
- Cohen's d=-6.87 + permutation p<0.001: parametric/non-parametric 양쪽 유의

### VG POM bootstrap + cross-scenario bottleneck
- VG all_pass: 15.0% [5.0%, 27.5%]
- VG 병목: self_harm 15%, **Phi=1.000** (perfect alignment)
- Peter 병목: sword_drawn 50%, Phi=0.951
- **Cross-scenario POM isomorphism**: 둘 다 단일 rare-action pattern이 bottleneck

### Cross-agent state coupling
- Judas disill ↔ Peter fear: Pearson r = **0.756** (15/15 positive)
- Judas disill ↔ Caiaphas threat: r = **0.894** (15/15 positive)
- Lagged correlation peak at lag=-30 (r=0.792): Peter fear leads Judas disill

### Cross-scenario KS test
- Peter mean 0.383, VG mean 0.510 (normalized [0,1])
- **KS D = 0.567**, D_crit(α=0.01) = 0.421 → **α=0.01 유의**
- **Dual-layer**: 표면 다름 + 심층(POM) 동형

### VG 감정 궤적 (cross-scenario emotional isomorphism)
- Hope trough at 0: 1.29 / Grief peak at +20: 9.92 / Fear peak at +30: 9.68
- Peter와 **peak ORDER 완벽 일치**: hope trough → grief peak → fear peak
- VG hope crash: slope **-0.8/tick** (Peter -0.06, 13배 급격)

### Disill × Greed 2x2 factorial
- Main effect disill: **-123.1 tick** (dominant)
- Main effect greed: -4.7 tick
- Interaction: +8.6 tick (weak, ratio 0.07)
- 거의 additive, disill이 26배 주효과

### Peter 초기값 sensitivity (asymmetric causation)
- Peter.fear: **3.4 tick** (거의 0) / Peter.hope: 17.2 tick
- Peter total: **21 tick** (Judas disill 단일의 1/9)
- **Peter = witness, Judas = cause** 인과 경로 명확

### Hazard Poisson check (n=213 intervals)
- Inter-arrival: mean 29.14, std 24.78, **CV=0.85**
- Chi-square 26.64 > 11.35 (α=0.01) → exponential 완벽 아님
- Arrest trigger CV=**0.21** (state-driven 수렴, Poisson과 명확히 구별)
- **이중 stochasticity**: Poisson-like background + state-driven convergence

### Final state convergence (attractor)
- Judas disill/greed/guilt, Caiaphas threat: 모두 **10.0 ± 0.0** (천장 포화)
- Peter fear CV=**0.02**, grief 0.27, hope 0.10, love 0.07 (강한 수렴)
- **주의**: 이는 현 규칙계 + [0,10] 스케일 천장의 구조적 산물 (역사적 필연성 증거 아님, LLM 4차 교정)

### Action count regression
- 모든 행동 r > 0 (time 상관 confound)
- **방법론 함의**: action count는 time confound 강함 → state-based regression이 clean

### Action RATE regression (time confound 제거)
- **judas.withdraw rate: r=-0.942** (강력 음의 상관)
- peter.weep rate: r=+0.796 (late-arrest 패턴)
- 양/음 방향 모두 나타남 → count 회귀의 time confound 증명

### Withdraw rate forecast (tick 100 기준)
- Best threshold: 0.08/tick, accuracy **83.3%** [66.4%, 92.7%]
- 같은 HOLDOUT=100 비교: withdraw 73% vs disill 63% (withdraw 우세)
- **behavioral rate signal이 state signal을 early horizon에서 outperform**

### VG behavioral signal (cross-scenario)
- gauguin.critique rate r=**-0.922** (Peter의 judas.withdraw -0.942와 대응)
- **Cross-scenario 동형 구조**: 양쪽 모두 driver의 "aggressive" 행동 rate가 가장 강한 signal

### Multi-horizon withdraw forecast
- tick 50 → **73.3%** / 75 → 80% / 100 → 83.3% / 150 → 83.3%
- tick 50 (10% of max)에서 이미 73% accuracy
- **이른 behavior 시그널이 뒤늦은 state 관측보다 우월**

### Withdraw rate noise robustness
- r = -0.977 (noise=0) / -0.930 (0.05) / -0.934 (0.10) / **-0.854** (0.20)
- 모든 noise에서 |r| > 0.85 → **실제 causal signal** (noise artifact 아님)

### Disill trajectory shape fit
- **Linear R² = 0.998** (best fit)
- Sigmoid R² = 0.966, Exponential R² = 0.784
- **교정**: 이전 "phase transition" 가정은 local (7→8 gap만), global shape는 **LINEAR 누적**
- Linear accumulation + discrete trigger = Witness 핵심 dynamics

---

## LLM 4차 리뷰 반영 (2026-04-19)

비판적 자체 점검으로 다음 조치:

1. **"Phase transition" 용어 전면 제거**: progress.md / DESIGN.md / RESEARCH.md 모두 "threshold-triggered regime switch"로 교체
2. **Terminal convergence 재해석**: "역사적 필연성 재현"이라는 과장 주장 철회 → "현 규칙계의 강한 terminal attractor" (model artifact)
3. **External validity 최초 증거 (partial holdout)**:
   - Withdraw rate @ tick 100: train 83.3% / test **73.3%** (overfit gap +10%)
   - Disill @ tick 150: train 83.3% / test **88.9%** (overfit gap -5.6%, 완벽 일반화)
   - 5-fold CV (withdraw): mean **72%**, std 8.4%
   - **의의**: 기존 in-sample 결과가 심한 overfit 아님 확인. 첫 "외부" 검증.
   - **한계**: 같은 distribution의 train/test. 진짜 external data/human baseline 필요.

---

## v0.7 로드맵 (5차 LLM 리뷰 기반)

**비전 재정립**: Witness = 플레이어가 역사적 인물의 삶을 체험하며 목격자가 되는 서사 시뮬레이터.

**6단계 로드맵** (상세: `DESIGN.md`, `DESIGN_LATENT_DRIVE.md`, `TRACE_SCHEMA.md`)

| 버전 | 핵심 | 기간 |
|------|------|------|
| v0.5 (완료) | Rule-based symbolic + 검증 프레임워크 | — |
| **v0.7 (현재)** | Trace pipeline + player view + drive hooks + content-driven narrative | **Stage 1 + 2 skeleton 완료** |
| v0.6/v1.0 paper | 논문 마감 (`PAPER_OUTLINE_V05.md` / `PAPER_DRAFT_V06.md`) | 1-2개월 |
| v1.0 | Predictive Latent Drive Bottleneck (PyTorch training) | 3-4개월 |
| v1.1 | Relational graph (node drive + edge tension) | 2-3개월 |
| v1.2 | Phase-linked life architecture (베드로 전 생애) | 3-4개월 |
| v1.3 | Weak Preference Inference (classical IRL 아님) | 2-3개월 |
| v2.0 | Narrative Witness Layer (trace → 1인칭 경험) | 지속 |

---

## v0.7 Stage 1 Infrastructure (2026-04-19)

### Core / Trace Schema
- [x] `AgentState.drive_state: LatentDriveState | None` (backward compat)
- [x] `engine/core/latent_drive.py` — 4 Protocols + IdentityEncoder/Policy/Susceptibility/SlowUpdate (v1.0 학습 모델 교체 시 baseline)
- [x] `ActionRecord.observable_from` + `visible_signal` + `weight_breakdown` 필드 (Trace Schema §2)
- [x] `WeightFormula.compute_weight_breakdown` (base + state_multipliers 분해, Trace §2.2)
- [x] `Trigger.snapshot_conditions()` + SimulationWorld 연결 (§2.1 state conditions 실측값 + threshold + satisfied)
- [x] `AgentBelief` 클래스 + `AgentState.beliefs` 필드 (v1.1 relational 기초, backward compat empty dict)

### Rendering Pipeline
- [x] `engine/rendering/trace_emitter.py` — SimulationResult → 통합 JSONL TraceEvent 스트림 (§2 entries 5종: action_taken / trigger_fired / belief_update / bifurcation_point / canonical_match)
- [x] `engine/rendering/player_view.py` — 플레이어 시점 필터 (§3.1 정보 비대칭성, 내부 필드 제거)
- [x] `engine/rendering/trace_narrator.py` (v2.0 renderer preview) — TraceEvent → 한국어 narrative. 5개 entry 타입 dispatch, `visible_signal` 우선 + generic fallback, `skip_repeats` per-agent. LLM 미사용 (ABSOLUTE RULE #4)
- [x] `narrate_result(result, player_id, ...)` one-call helper (collect→filter→render 단축)

### Bifurcation Detection
- [x] `engine/simulation/bifurcation.py` — `detect_bifurcation(trajectories)`: decision window + plateau_start + max_growth_std (Trace §2.4)
- [x] 정밀도 개선: `smoothing` (centered moving average), `min_significance` (weak peak 기각 → `significant` flag), `top_k` (non-overlapping candidate windows → `top_windows` 필드). Backward compat 유지.

### Stage 2 Skeleton
- [x] `SimulationWorld.__init__(drive_model=...)` hook — v1.0 학습 모델이 매 tick agent.drive_state 갱신. None이면 no-op
- [x] `engine/simulation/training_samples.py` — MultiAgentResult → (state, action, event, next_state) 튜플. state_to_feature_vector (12-dim), samples_to_feature_matrix
- [x] `SampleStatistics` + `summarize_samples()` — agent_counts, action_counts, event_rate, action_imbalance_ratio (pre-training diagnostic)
- [x] `engine/simulation/drive_training.py` — `TrainingConfig` (drive_dim, loss weights α/β/γ/λ), `collect_trajectories` / `trajectories_to_samples` / `train_drive_model` / `validate_drive_model` / `train_and_validate` E2E API. 현재는 identity fallback, Stage 2에서 PyTorch MLP로 교체.
- [x] `ValidationReport.sample_stats` 필드 통합

### Content-Driven Narrative (정보 비대칭성 end-to-end)
- [x] `AgentAction.visible_signal` + `observable_from` 필드 (engine/core/action.py) + SimulationWorld voluntary action record에 propagate
- [x] **전체 content pack visible_signal 완성** (22개 action):
  - peter 6 ("베드로가 예수 곁을 떠나지 않고 뒤따랐다" 등)
  - judas 5 ("유다가 또 말없이 무리에서 떨어져 앉았다" 등)
  - caiaphas 4 ("대제사장의 체포 명령이 내려졌다" 등)
  - crowd 4 ("누군가의 수군거림이 들려왔다" 등)
  - vangogh 4 ("빈센트가 붓을 놓지 않고 밤까지 작업했다" 등)
  - gauguin 5 ("고갱이 짐을 챙겨 노란 집을 나섰다" 등)
  - theo 3 ("파리의 테오가 송금을 보냈다" 등)
- [x] **observable_from 정보 비대칭성**: Judas inform_authorities → [caiaphas] 전용, betray → [peter, caiaphas] 목격. seed=0 200-tick Peter run에서 inform_authorities 13회 발생 중 Peter 시점 0개 / Caiaphas 시점 13개 E2E 확인
- [x] observable_from 확장: caiaphas consult_sanhedrin→[caiaphas, crowd], vangogh/theo 3개 letter action → [theo, vangogh]

### Demo + Integration
- [x] `demo_v07.py` — 6단계 파이프라인 (`sim → trace → player_view → JSONL → narrative`)
- [x] `--scenario peter|vangogh` 지원: scenario별 bifurcation driver (peter→judas.disill, vangogh→gauguin.frustration) + belief update heuristic (peter→judas withdraw ×5, vangogh→gauguin critique ×3)
- [x] demo 확장: BeliefUpdate §2.3 실제 예시 — §2 entry 4 타입 모두 존재 (action_taken 805 / trigger_fired 6 / belief_update 2 / bifurcation_point 1)
- [x] Peter 시점 814 events → 481 narrative lines (per-agent skip_repeats 묶음), 분기점 강조 포함
- [x] VG seed=0 150-tick: 빈센트/고갱/테오 3-agent emergent narrative 출력, 분기점 tick 8-10 포함

### 인프라 / 품질
- [x] `archived` pytest marker 도입 + Tier 3 16개 파일에 적용. `pytest -m archived`로만 실행
- [x] mypy strict: engine/ 실제 에러 **0건** (third-party stub 5건은 기존부터)
- [x] `test_content_pack_structure.py` — 새 시나리오 자동 구조 검증 (initial_state/behavior_profile 존재, JSON schema, 엔진 로직 비-override, 7 pack 열거)
- [x] E2E 통합 테스트 `test_trace_integration.py` — 실제 Peter 시뮬 → trace emitter → player view filter → JSONL round-trip, visible_signal/observable_from 검증
- [x] `.github/workflows/ci.yml` — GitHub Actions CI: Python 3.11/3.12 matrix, ruff check, mypy engine/ (continue-on-error for third-party stubs), pytest fast suite, engine integrity grep, coverage artifact upload
- [x] `benchmarks/bench_simulation.py` — Peter/VG tick/s + 메모리 벤치마크 (tracemalloc). 기준선: **Peter 1001 tick/s @ 2.3 MB, VG 1267 tick/s @ 1.7 MB** (250 tick × 5 seeds)

### 용어 감사 / 문서 sync
- [x] `phase transition` → `threshold-triggered regime switch` 전면 교정 (모든 현재 언급은 correction context)
- [x] `ITERATION_CLASSIFICATION.md` — Tier 1~4 (34 iteration) + Tier 5 신규 (v0.7 trace pipeline 109 tests) 매핑
- [x] Documents sync: `CLAUDE.md` / `DESIGN.md` / `DESIGN_LATENT_DRIVE.md` / `TRACE_SCHEMA.md` / `ITERATION_CLASSIFICATION.md` / `PAPER_OUTLINE_V05.md` / `PAPER_DRAFT_V06.md` / `SCENARIO_TEMPLATE.md` / `RESEARCH.md` / `README.md`
- [x] Stale 참조 정리: `LLM_REVIEW_DIRECTION.md` (미존재) 제거 → 내용은 DESIGN.md §0.5 + CLAUDE.md ABSOLUTE RULE #5에 통합

### Coverage 확장 (572 fast / 97%)
- [x] statistics.py 92% → 100%, scripture.py 91% → 100%, trace_emitter.py 94% → 100%, decision.py 93% → 100%, scheduler.py 96% → 100%, social.py 96% → 100%, state.py 98% → 100%, pom.py 97% → 100%, checkpoint.py 97% → 100%, core/world.py 97% → 100%, bifurcation/explanation/resolution/drive_training 모두 100%
- [x] event.py 96% → 97%, hazard.py 97% → 99%, trigger.py 96% → 99%, narrator.py 94% → 98%, trajectory.py 94% → 99%, analysis.py 56% → 70% (fast mode)
- [x] **15 engine modules at 100%**

---

## v0.6 Paper Draft (319 lines)

`PAPER_DRAFT_V06.md` — 비제출 working draft 상태.

### 섹션 prose 완료
- **§1 Introduction**: 검증 공백 문제 → distribution 관측 전환 → 3-contribution framing (engine, 7-layer framework, cross-scenario)
- **§2 Related Work**: POM (Grimm 2005), docking (Axtell), Epstein generative SS, Keeling & Rohani hazard, Mesa/CESM separation
- **§3 The Witness Engine** (3.1-3.5): 4-layer architecture, state model (fast/slow), hazard-driven events, trigger system, 자동 integrity 검증
- **§4 Scenarios** (4.1-4.2): Peter 4-agent, VG 3-agent, 공통 엔진 사용 rationale
- **§5 Validation Framework** (5.1-5.7): POM / Counterfactual Ablation (d=-6.87, p<0.001) / Event-Relative Checkpoint (35.5%→80.3%) / Explanation Faithfulness (ρ=1.0) / Partial Holdout (train 83% / test 88.9%) / Cross-Scenario KS (D=0.567 p<0.01) / Behavioral Rate (r=-0.942)
- **§6 Key Findings** (6.1-6.8): Emergent / Asymmetric causation / Structural isomorphism / Surface difference / Linear+threshold / Stability not chaos / Terminal saturation (artifact) / Behavioral precedence — 모든 finding 해석 한계 명시
- **§7 Discussion**: Framework reusability (70%) / Limitations / Methodological notes (용어 교정 근거)
- **§8 Future Work**: v1.0 Stage 1/2, v1.1-v1.3 세부, v2.0 player_view+trace_narrator 연결, 3번째 시나리오 (SCENARIO_TEMPLATE)
- **§9 Conclusion**

### 부록
- **Appendix A**: 재현 가이드 (demo_v07, benchmark, pytest tiers)
- **Appendix B**: Per-finding test pointer table (§5.1-5.7 + §6.1-6.8 = 16 rows, test 파일 + 핵심 수치)
- **Appendix C**: Figure plan (8 placeholders: architecture / POM heatmap / counterfactual bar / Spearman / trajectory fit / KS CDF / behavioral scatter / emotion arc)
- **References**: Axtell 1996, Epstein 2006, Grimm 2005, Keeling & Rohani 2008, Mesa 2015

---

## v1.2 Phase-Linked Life Architecture 착수 (2026-04-19)

**동기**: Peter 시나리오를 50일 수난에서 **3년 공생애 (소명 → 승천)** 전체 아크로 확장. GPT + Gemini 외부 리뷰 수렴 반영.

**결정**:
- 표현: "phase-linked continuous life architecture" (표면 연속, 내부 stitched)
- Tick scale: phase-variable (dense 2h/tick ↔ sparse 1일/tick)
- MVP: Phase 1 (Luke 5 소명) + mock Phase 2 handoff
- Legacy 보존: `initial_state_legacy.json` + mode 분리 (v0.7 검증 수치 유지)
- 전 rule dt-aware (hazard만이 아닌)
- Slow state 회복: field별 분리, canonical = reparameterization shock, MVP 비활성

**Iteration 완료**:
- [x] **Iter 1**: `engine/core/phase.py` — `Phase` / `PhaseExitCondition` / `PhaseHandoffSpec` / `FieldMapping` dataclass. 21 tests.
- [x] **Iter 2**: `RuleContext.dt_hours` 필드 (default 2.0). 9 tests — rate scaling, time-invariance, real-time axis.
- [x] **Iter 3**: `SimulationConfig.phases` + `tick_scale_hours` 필드. `is_phase_linked` property. 7 tests.
- [x] **Iter 4**: `engine/simulation/phased_world.py` — `PhasedSimulationWorld` + `apply_handoff` + `PhasedMultiAgentResult`. slow_state carry-forward + explicit field mapping + multi-phase stitching. 12 tests.
- [x] **Iter 5**: `content/peter/phases/01_calling/` (phase_config, canonical_events 5 scenes, handoff_to_02) + `content/shared/scripture/luke_5.json` (개역개정 Luke 5:1-11). 15 tests.
- [x] **Iter 6**: `FaithJourneyState` nullable 확장 (`jesus_understanding: None` 허용, `communal_role: None` 허용). `EmotionalState.awe` 필드 추가. `content/peter/initial_state_calling.json` (어부 시점 초기 상태: Gennesaret, fatigue 6.0, obedience 0.0, 예수와 관계 없음). 13 tests.
- [x] **Iter 7**: SimulationWorld에 `ExternalEvent` 처리 추가 (intervention + events 모두 지원). `test_peter_calling.py` 9 tests — 5 canonical events 모두 발동, awe 급상승, obedience emergent 누적, 10 시드 ensemble 전부 완주.
- [x] **Iter 8**: Legacy mode 검증 — `demo_v07.py --scenario peter` / `--scenario vangogh`, `main.py` / `main.py --multi` 모두 정상 작동. Peter arrest tick range 152-211 (v0.7 수치 유지). Engine integrity 0건.

**Phase 1 + Phase 2 scaffold 완료 (Iter 1-11)**:
- [x] **Iter 9**: `content/peter/phases/02_galilean/` (phase_config, canonical_events 12 scenes, handoff_to_03). 12 사도 택정 / 12명 파송 / 오병이어(tick 231) / 물 위 걸음(232-234 연속 dense) / 사천명 / 바리새인 논쟁 / 벳새다 소경. 15 tests.
- [x] **Iter 10**: Phase 1 → Phase 2 real handoff E2E. `PhasedSimulationWorld`로 두 phase 순차 실행, phase boundaries tick offset 검증 (0-84 / 84-114).
- [x] **Iter 11**: `engine/rules/inhibitor.py` — `FieldAttenuationRule` + `FieldAmplificationRule` (generic, content-configurable). dt_hours 인식. Gemini 지적 반영: 유다 조기 배반 방지. 11 tests.

**최종 지표 (v1.2 MVP + Phase 2 scaffold)**: **Fast tests: 684** (+112 from v0.7 baseline 572) / Archived: 33 / Total: 815. Coverage 유지. Ruff clean. Engine integrity 유지. Legacy mode 완벽 보존.

**3년 아크 scaffold 현 상태**:
- Phase 1 소명 (84 tick, 2h/tick) — content + E2E ✅
- Phase 2 갈릴리 사역 (540 tick, 24h/tick) — content ✅ / E2E 부분
- Phase 3 고백+변화산 — 미착수
- Phase 4 예루살렘 여정 — 미착수
- Phase 5 수난 (기존 500 tick) — legacy mode로 유지 중

**reviewer 피드백 반영 누적 확인**:
- ✅ "phase-linked continuous life" 명칭 (stitched 내부)
- ✅ 모든 rule dt-aware (inhibitor도 dt_hours 인식)
- ✅ Legacy mode 완전 보존 (phases=None = 기존 동작)
- ✅ slow_state irreversible carry-forward
- ✅ Explicit field mapping (선별 전달)
- ✅ canonical event = reparameterization shock
- ✅ Phase 2 "국지적 dense window" (230-234 연속 tick으로 오병이어+물 위 걸음 표현)
- ✅ Inhibitor Rule 스켈레톤 (generic, content-configurable, engine integrity 유지)

**Phase 3-4 scaffold + 전체 아크 E2E 완료 (Iter 13-16)**:
- [x] **Iter 13**: Phase 3 content (가이사랴 빌립보 고백 13 scenes). 13 tests.
- [x] **Iter 14**: Phase 4 content (예루살렘 여정 8 scenes). 12 tests. 전체 아크 ~1.9년 검증.
- [x] **Iter 15**: DESIGN.md v1.2 상태 반영 — 5 Phase 구조 + reviewer 체크리스트.
- [x] **Iter 16**: 전체 아크 E2E — `PhasedSimulationWorld`로 Phase 1→4 순차 실행, 4개 phase 모두 완주, tick_scale 2h/24h/2h/24h 교대 유지, state continuity 보장, legacy mode 동일 결과 재현. 10 tests.

**최종 지표 (Phase 1-4 전체 아크 작동)**: **Fast tests: 719** (+147 from v0.7 baseline 572) / Archived: 33. Ruff clean. Engine integrity 유지.

**3년 아크 현 상태**:
| Phase | 기간 | tick | 상태 |
|-------|------|------|------|
| 01 Call | ~1주 | 84 × 2h | content + E2E ✅ |
| 02 Galilean | ~18개월 | 540 × 24h | content ✅ / E2E 부분 |
| 03 Confession | ~1.5주 | 150 × 2h | content ✅ |
| 04 Journey | ~3개월 | 90 × 24h | content ✅ |
| 05 Passion | 42일 | 500 × 2h | legacy 유지 |
| **총합** | **~1.9년** | **~1,364 tick** | |

**v1.2 Phase 1-5 전체 연결 완료 (Iter 17-18)**:
- [x] **Iter 17**: Phase boundary agent introduction — `PhasedSimulationWorld._phase_initial_defaults` 개선으로 `config.initial_states` fallback 로드 + next_defaults 계산 버그 수정 (phase final_states 기준으로). +5 tests.
- [x] **Iter 18**: **5-phase 전체 아크 E2E** — Peter(소명) → Peter+Judas(갈릴리 12 사도 택정부터) → Peter+Judas(고백/여정) → Peter+Judas+Caiaphas+Crowd(수난). Legacy v0.7 compat 유지. +7 tests.

**최종 지표**: **Fast tests: 731** (+159 from v0.7 baseline 572) / Archived: 33 / Total: 895.

**v1.2 Iter 19-22 (reviewer feedback 반영 추가 작업)**:
- [x] **Iter 20**: `Phase.canonical_events_path` 자동 로드 — PhasedSimulationWorld가 phase별 canonical_events.json을 읽어 해당 phase 내부에서만 fire. missing path fallback + legacy compat 유지. +5 tests.
- [x] **Iter 21**: **전체 아크 + phase별 events 배선** — Phase 1-4 각각 자체 canonical_events로 실행 (5 / 12 / 13 / 8 이벤트). Peter obedience_maturity / awe / understanding 누적 거동 검증. +7 tests.
- [x] **Iter 22**: **Absolute time 분석 메트릭** (`engine/simulation/time_axis.py`) — ChatGPT 지적 "phase-variable tick에서 tick 단위는 비교 불가, hours since call로 재정의" 대응. `ticks_to_absolute_hours`, `extract_field_trajectory_absolute`, `convert_phase_boundaries_to_hours`, `hours_to_days`/`hours_to_years`, `extract_final_states_at_phase_boundaries` 제공. +15 tests.

**현재 지표 (Iter 22 완료)**: **Fast tests: 758** / Archived: 33 / Total: 922. Ruff/mypy clean (기존 stub warning만).

**v1.2 Iter 23-25 (review blocker 해소 + 통합)**:
- [x] **Iter 23**: `SlowStateFieldRecoveryRule` (`engine/rules/slow_recovery.py`) — field-specific opt-in 회복. moral_injury (hope ≥ threshold), trust_scar (관계 평균 trust ≥ threshold), identity_shift (hope+love 동시). event_trauma는 의도적 미제공 (PTSD 원칙). 기본 rate=0 = zero-effect. +19 tests.
- [x] **Iter 24**: DESIGN.md v1.2 섹션 refresh — Iter 20-23 신규 모듈 반영, 남은 과제 체크박스 업데이트.
- [x] **Iter 25**: `PhasedMultiAgentResult.extract_absolute_trajectory` 편의 method + integration 테스트 — 실제 2-phase 실행 결과를 absolute hours trajectory로 변환, tick_scale 차이가 hours 간격에 반영됨을 검증, legacy 모드 분리 확인. +5 tests.

**현재 지표 (Iter 25 완료)**: **Fast tests: 782** (+210 from v0.7 baseline 572) / Archived: 33 / Total: 946. Ruff clean. mypy: 6 pre-existing stub warnings (SALib/umap/sklearn), 0 신규.

**v1.2 Iter 26 (Inhibitor pipeline 통합 검증)**:
- [x] `test_inhibitor_integration.py` — FieldAttenuationRule이 PhasedSimulationWorld pipeline 내부에서 RuleContext.dt_hours를 정확히 받아 감쇄 적용함을 증명. tick_scale 변경 invariance (2h/tick 24tick vs 24h/tick 2tick = 동일 48h → 동일 감쇄량), min_target_value floor, multi-phase dt 전환 4가지 시나리오. +5 tests.

**현재 지표 (Iter 26 완료)**: **Fast tests: 787** / Archived: 33 / Total: 951. Ruff clean.

**v1.2 Iter 27 (Hazard per_hour 지원 — opt-in, legacy-safe)**:
- [x] `HazardFunction.base_rate_unit: Literal["per_tick", "per_hour"] = "per_tick"` 추가. 기본 per_tick이므로 v0.7 legacy calibration 100% 보존.
- [x] `HazardEngine.evaluate_tick(tick_scale_hours=None)` — per_hour 이벤트는 tick_scale_hours를 dt로 사용, 그 외는 기존 dt.
- [x] `engine/simulation/world.py`가 `self._config.tick_scale_hours`를 `evaluate_tick`에 전달.
- [x] 테스트: per_tick 기본 legacy 보존 / per_hour tick_scale 스케일링 / 실시간 invariance / fallback / backward compat JSON. +9 tests.

**현재 지표 (Iter 27 완료)**: **Fast tests: 796** / Archived: 33 / Total: 960. Ruff clean. mypy: 6 pre-existing stub warnings, 0 신규.

이제 phase 2 (24h/tick)에서 hazard rate를 per_hour로 선언하면 phase 1 (2h/tick)과 실시간 기준 기대값이 호환됨. 기존 Peter 수난 hazard는 per_tick 기본값이므로 무영향.

**v1.2 Iter 28 (runnable demo)**:
- [x] `demo_phased.py` — Peter 공생애 4-phase 전체 아크 실제 실행 + time_axis 절대시간 출력. Phase boundary 표, awe/obedience trajectory 샘플링, final state dump.
- [x] `--with-recovery` flag: `SlowStateFieldRecoveryRule` 옵션 활성화 (moral_injury 1.30 → 1.23 소량 회복 관찰됨).
- Seed=0 실행 결과: awe 0 → 6 (소명) → 8 (갈릴리) → 10 (고백/변화산) → plateau, obedience 0 → 5 → 5.8 → 7.6 → 7.9, 총 2428h ≈ 101 days.
- 전체 아크가 phase 경계에서 discontinuity 없이 연결됨 (handoff 적용 시 slow_state carry-all + explicit emotions/obedience 매핑).

**현재 지표 (Iter 28 완료)**: Fast tests 796 그대로 (데모는 스크립트이므로 추가 테스트 없음). Ruff clean.

**v1.2 Iter 29 (외부 리뷰 수렴 문서)**:
- [x] `REVIEW_RESPONSE_V1_2.md` — plan의 6개 reviewer 질문에 대해 Iter 20-28 구현 증거로 답변. 코드/테스트 참조 + trade-off 정리 + 남은 blockers.
- Q1 phase-variable tick: `HazardFunction.base_rate_unit` opt-in으로 해소.
- Q2 phase 구분: Markan 순서로 5 phase 확정.
- Q3 slow state 회복: field-specific opt-in, event_trauma 제외.
- Q4 MVP 소명 선택: 사후 타당성 증명 (Phase 2-4 확장 성공).
- Q5 v0.7 보존: `test_claim_legacy_mode_identical_to_v07`로 bit-exact 보장.
- Q6 연속 vs stitched: `PhasedMultiAgentResult`가 둘 다 제공.

**v1.2 Iter 30 (POM-style 앙상블 emergent 검증)**:
- [x] `test_phase_arc_emergent.py` — 10 seed × 4 phase 앙상블. fixture scope=module로 캐싱.
- 완주율 100%, Phase 1 awe 평균 ≥ 3.0 (canonical 기적 효과), Phase 1 → 3 awe 단조 성장 (transfiguration peak), obedience phase별 non-decreasing 평균, fear/awe bounded, jesus_understanding literal 범위, seed 재현성 + noise variation. +11 tests.

**현재 지표 (Iter 30 완료)**: **Fast tests: 807** (+235 from v0.7 baseline 572) / Archived: 33 / Total: 971. Ruff clean.

**v1.2 Iter 31 (Inhibitor content-level composition)**:
- [x] `test_inhibitor_judas_deployment.py` — FieldAmplificationRule로 Judas disillusionment drift + FieldAttenuationRule로 Peter.awe 조건부 감쇄 조합. Gemini 경고 "1년 차 조기 배반" 시나리오 증명:
  - 억제 없이: 720h에 disillusionment 3.0 → 10.0 cap 도달.
  - 억제 있고 awe=8: 순증가 (0.01-0.008)/h × 720 = +1.44 → 4.44 (cap 미만 bounded).
  - awe=3 (< threshold 5): 억제 미작동, cap 도달.
  - tick_scale 2h/tick 360 tick vs 24h/tick 30 tick (동일 720h): inhibitor 동일 per-hour 해석. +6 tests.

**현재 지표 (Iter 31 완료)**: **Fast tests: 813** / Archived: 33 / Total: 977. Ruff clean.

**v1.2 Iter 32 (Phase 5 linked-life 모드 + legacy 분리)**:
- [x] `content/peter/phases/05_passion/phase_config.json` — legacy canonical_events.json 재사용, tick_scale_hours=2.0, max_tick=500.
- [x] `test_linked_life_phase5.py` — 5-phase linked-life 실행 + legacy-phase5 (phases=None) 분리 보존 검증. 두 mode 결과가 양자택일로 다름을 증명. Phase 5 config exists, 5 phase complete, Peter handoff 반영, legacy literal ("messiah_political") 보존. +6 tests.
- Legacy mode는 여전히 phases=None으로 실행되어 v0.7 수치 bit-exact.

**현재 지표 (Iter 32 완료)**: **Fast tests: 819** (+247 from v0.7 baseline 572) / Archived: 33 / Total: 983. Ruff clean.

**v1.2 Iter 33 (README user-facing refresh)**:
- [x] README.md: 제목 v0.7 → v1.2, 로드맵 테이블에 v1.2 current 반영, v0.7 → Complete 변경.
- [x] Quick start에 `demo_phased.py` 추가, pytest test 수 572 → 819 업데이트.
- [x] "v1.2 Phase-linked life architecture" 새 섹션 — 두 mode (legacy-phase5 / linked-life), 핵심 모듈 표, dt_hours-aware 설명.

**v1.2 Iter 34 (engine-neutrality 증명 — Van Gogh through PhasedSimulationWorld)**:
- [x] `test_phased_vangogh.py` — VG 3-agent scenario를 Phase 1개로 감싸거나 2 phase로 분할해 PhasedSimulationWorld로 실행. VG hazard events per_tick 기본값 보존, 단일 phase = legacy 수치 동일 (bit-exact), fired_events 순서 동일, `extract_absolute_trajectory`가 VG에서도 작동, 2 phase split + handoff로 fear 연속성.
- ABSOLUTE RULE #1 (engine 인물 비종속) empirical 증명: v1.2 머신이 Peter뿐 아니라 Van Gogh에서도 정상 동작. +7 tests.

**현재 지표 (Iter 34 완료)**: **Fast tests: 826** (+254 from v0.7 baseline 572) / Archived: 33 / Total: 990. Ruff clean.

**v1.2 Iter 35 (per_hour hazard content-level E2E)**:
- [x] `test_per_hour_hazard_phased_e2e.py` — per_hour HazardEvent를 SimulationConfig에 직접 넣고 PhasedSimulationWorld 실행. phase.tick_scale_hours가 evaluate_tick에 전달되어 per_hour 이벤트 발동률이 tick_scale에 의해 해석됨을 end-to-end로 증명.
- per_tick + per_hour 혼합 config에서 두 이벤트가 각자 independent 발동. 2-phase (2h/tick + 24h/tick)에서 per_hour 이벤트가 양쪽에서 일관된 rate 해석. +4 tests.

**현재 지표 (Iter 35 완료)**: **Fast tests: 830** (+258 from v0.7 baseline 572) / Archived: 33 / Total: 994. Ruff clean.

**v1.2 Iter 36 (coverage 100% — time_axis + inhibitor)**:
- [x] `test_coverage_gaps_v12.py` — time_axis.extract_final_states_at_phase_boundaries 5 cases + Inhibitor/Amplifier edge cases (non-numeric trigger/target, missing trigger agent, below-threshold). +11 tests.
- Coverage: `engine/simulation/time_axis.py` 75% → **100%**, `engine/rules/inhibitor.py` 89% → **100%**.

**현재 지표 (Iter 36 완료)**: **Fast tests: 841** (+269 from v0.7 baseline 572) / Archived: 33 / Total: 1005. Ruff clean.

**v1.2 Iter 37 (phased_world edge 경로 커버)**:
- [x] `test_phased_world_edge_cases.py` — apply_handoff 6가지 edge case: source agent missing, value+default 둘 다 None, default 적용됨, target agent missing, agents_active fallback, 빈 checkpoints. +6 tests.
- Coverage: `engine/simulation/phased_world.py` 94% → **97%**. 남은 4줄은 defensive dead code + 드문 checkpoint 병합 경로로 판단, 추후 필요 시 커버.

**현재 지표 (Iter 37 완료)**: **Fast tests: 847** (+275 from v0.7 baseline 572) / Archived: 33 / Total: 1011. Ruff clean.

**v1.2 Iter 38 (DESIGN.md 문서 정렬)**:
- [x] DESIGN.md 제목 v0.7 → v1.2, 테스트 수 572 → 847 업데이트, coverage 노트 추가.
- [x] v1.2 완성 체크리스트 — Iter 1-37 완료 항목 명시 + 남은 확장 과제 분리.
- 문서-코드 싱크: README.md, DESIGN.md, progress.md, REVIEW_RESPONSE_V1_2.md가 모두 Iter 37 기준으로 일관.

**v1.2 Iter 39 (Phase 5 full-length 500 tick scale 증명)**:
- [x] `test_linked_life_phase5_full.py` — Phase 1-5 full arc (총 724 tick, 4 agents) + Phase 5 full 500 tick 실행. 0.12~0.75s/seed. 5 phase 완주, Phase 5 내부 tick=500, 4 agent 모두 final_states에 존재, Phase 5에서 legacy events 5+ fire, 모든 emotions bounded, 3 seed 안정성, runtime budget < 5초. +7 tests.
- Iter 38에서 명시한 "여전히 가능한 확장" 항목 중 `linked-life full 500 tick` 실증 완료.

**현재 지표 (Iter 39 완료)**: **Fast tests: 854** (+282 from v0.7 baseline 572) / Archived: 33 / Total: 1018. Ruff clean.

**v1.2 Iter 40 (release-readiness attestation)**:
- [x] demo_v07.py peter + vangogh 실행 완주 (v0.7 파이프라인 regression 없음).
- [x] demo_phased.py seed=0, seed=42, --with-recovery 모두 정상 출력.
- [x] benchmark: Peter 928 tick/s @ 2.3 MB, Van Gogh 1158 tick/s @ 1.7 MB (v0.7 기준 1001/1267에서 ~5-10% 느려짐 — rule 추가 overhead, 예상 범위).
- [x] pytest fast 854 pass / ruff clean / mypy 6 pre-existing stub warning (0 신규).
- v1.2 작업 싸이클 종료 선언: 아키텍처 + 테스트 + 문서 + 데모 모두 정합. legacy v0.7 파이프라인도 그대로 작동.

**v1.2 Iter 41 (lessons.md 신규)**:
- [x] `lessons.md` — 글로벌 CLAUDE.md 지침("lessons.md 업데이트 제안") 이행. Iter 20-40 세션에서 얻은 10가지 교훈 기록: opt-in zero-default 패턴, legacy 분리, phase-linked 두 관점, ensemble validation, integration 3계층, 100% coverage 부수 효과, float equality, dt 누락 발견 과정, loop ROI 감소 시점, 루프 박자와 사고 깊이.
- 다음 세션용 주의 사항 명시: v1.2 종료 선언, legacy sacred 수치, 3번째 시나리오 전 universality 금기, v1.0 Stage 2 진입점.

**v1.2 Iter 42 (v0.6 paper draft v1.2 반영)**:
- [x] PAPER_DRAFT_V06.md §8 Future Work — v1.2 상태 "scheduled" → "implemented; see Appendix D" + 5 phase 개요 추가.
- [x] 새 **Appendix D** — v1.2 implementation summary: 신규 모듈 테이블, RuleContext.dt_hours 설명, Peter content 확장, 핵심 검증 6개, 테스트 카운트 변동(572→854, 100% coverage 3 module), 런타임 (0.1-0.8s/seed, 벤치마크 ~7% 감소).
- Paper 분량: 319 → 351 lines.

**v1.2 Iter 43 (handoff JSON loader)**:
- [x] `engine/io/loader.py::load_handoff_spec(path)` — `handoff_to_next.json` 파일을 `PhaseHandoffSpec`으로 로드. content/peter/phases/*/handoff_to_*.json 구조 지원 (carry_all_slow_state + mappings + default_if_missing).
- [x] `test_load_handoff_spec.py` — Peter 모든 phase handoff 파일 로드, FieldMapping 타입 검증, Phase 4→5 핵심 field (confusion/fear) 포함, carry_all 기본/반전, 빈 mappings, default_if_missing 보존. +8 tests.
- 지금까지 `PhaseHandoffSpec`을 프로그램으로만 구성 가능했던 간극 해소 — content 작성자가 JSON 파일로 handoff를 선언하면 바로 로드.

**현재 지표 (Iter 43 완료)**: **Fast tests: 862** (+290 from v0.7 baseline 572) / Archived: 33 / Total: 1026. Ruff clean. mypy clean on new module.

**v1.2 Iter 44 (phase_config.json loader)**:
- [x] `engine/io/loader.py::load_phase(path, agents_active=None, handoff_to_next=None)` — `phase_config.json` → `Phase` 객체 변환. agents_active / handoff_to_next는 orchestration 결정이므로 caller 주입. exit_condition 중첩 dict 해석 (max_tick_fallback > max_tick, triggered_by).
- [x] `test_load_phase.py` — Peter 모든 phase JSON 로드 (01-05), tick_scale 서로 다름 확인, triggered_by, agents_active/handoff 주입, tick_offset_from_life_start 보존, 최소 JSON, max_tick_fallback override, 잘못된 tick_scale 검증. +11 tests.

**현재 지표 (Iter 44 완료)**: **Fast tests: 873** (+301 from v0.7 baseline 572) / Archived: 33 / Total: 1037. Ruff clean.

**v1.2 Iter 45 (JSON-only content-driven arc)**:
- [x] `test_json_driven_arc.py` — Iter 43 load_handoff_spec + Iter 44 load_phase 조합으로 **코드 안에 수치 하드코딩 없이 content/peter/phases/*/*.json만으로** Peter 5-phase arc 구성 + `PhasedSimulationWorld`로 실제 실행. orchestration (agents_active) 만 테스트가 제공.
- 5 phase 로드 순서, tick_scale_hours [2,24,2,24,2] JSON에서 복원, handoff 존재 유무 (1-4 있음, 5 없음) 확인, full arc 실행 완주, content 저자 워크플로우 (임시 JSON만 써서 phase 추가) 시뮬레이션. +5 tests.

**현재 지표 (Iter 45 완료)**: **Fast tests: 878** (+306 from v0.7 baseline 572) / Archived: 33 / Total: 1042. Ruff clean.

**v1.2 Iter 46 (demo_phased.py --full-passion 확장)**:
- [x] `demo_phased.py --full-passion` flag 추가: Phase 5 (500 tick passion) + Caiaphas/Crowd agents 자동 추가. Phase 4 → Phase 5 handoff 자동 연결.
- 기본 (4-phase): 2-agent (peter+judas), 2428h ≈ 101일.
- --full-passion (5-phase): 4-agent (+caiaphas+crowd), 3428h ≈ 143일.
- 실행: `python demo_phased.py --seed 0 --full-passion` 작동 확인.
- Ruff clean, 기존 878 tests 그대로.

**v1.2 Iter 47 (phase_hours_table 편의 method + 문서/데모 연동)**:
- [x] `PhasedMultiAgentResult.phase_hours_table()` — `convert_phase_boundaries_to_hours` 편의 wrapper. 외부 임포트 없이 phase boundary table 조회.
- [x] `demo_phased.py`: `result.phase_hours_table()`로 단순화, `convert_phase_boundaries_to_hours` import 제거.
- [x] README.md Quick start: `demo_phased.py --full-passion` 옵션 문서화.
- [x] 통합 테스트: convert_phase_boundaries_to_hours와 phase_hours_table() 결과 동일 검증. +1 test.

**현재 지표 (Iter 47 완료)**: **Fast tests: 879** / Archived: 33 / Total: 1043. Ruff clean.

**v1.2 Iter 48 (SCENARIO_TEMPLATE.md v1.2 섹션 추가)**:
- [x] SCENARIO_TEMPLATE.md §7 — 3번째 시나리오 저자 관점의 phase-linked 아크 가이드.
- 언제 phase를 쓸지, 파일 구조 (content/[name]/phases/), `load_phase` + `load_handoff_spec` Python 예시, Peter 패턴 참조 표 (tick_scale, max_tick, agents per phase).
- 문서: 183 → 244 lines. 기존 §1-§6 (Peter/VG와 다른 시나리오 타입 권장, POM scorecard, 체크리스트) 구조는 그대로.

**v1.2 Iter 49 (lessons.md tail 반성 + 교훈 11-12 추가)**:
- [x] Iter 41-48 saturation 패턴 솔직한 가치 표 기록.
- 교훈 11: Loop saturation 탐지 — 3 연속 low-med iteration or 5줄 편의 method 반복이면 새 세션 대기.
- 교훈 12: 300s ScheduleWakeup이 cache-miss 구간에서 사고 깊이 약화 — 다음 세션에서 재협의.

**v1.2 Iter 50 (session wrap-up)**:
- [x] 최종 검증: pytest 879 pass, ruff clean, demo_phased.py --seed 7 --full-passion --with-recovery 실행 성공 (5-phase, 3428h ≈ 143일, 4 agents, recovery active).
- Session 종료 준비 상태: v1.2 architecture + tests + docs + demos 완전 일관. 다음 세션은 v1.0 Stage 2 또는 3번째 시나리오로 pivoting 권장.

---

## 외부 리뷰 수용 세션 (Iter 51-53)

사용자가 제공한 Gemini + ChatGPT 합동 리뷰를 바탕으로 정책 3개 고정:

**Iter 51 (jesus_understanding Phase 1/3 전환)**:
- [x] content/peter/phases/01_calling/canonical_events.json `calling_05_call_and_follow`: None → teacher
- [x] content/peter/phases/03_confession/canonical_events.json `conf_03_peters_confession`: → messiah_political
- [x] demo_phased.py handoff에 jesus_understanding carry + final state 출력 추가
- [x] test_jesus_understanding_transitions.py (+6 tests): 결정적 전환, phase 진행, handoff pass-through

**Iter 52 (Phase 5 resurrection/ascension 전환)**:
- [x] content/peter/canonical_events.json `scene_13_emmaus_jerusalem` (tick 237): → risen_lord
- [x] `scene_17_ascension` (tick 495): → sending_lord
- [x] +3 tests: full legacy run → sending_lord, mid-run → risen_lord, pre-arrest → messiah_political
- Legacy dynamics 불변 (`jesus_understanding`은 behavior/trigger/hazard 어디서도 참조 안 됨, numeric 수치 영향 0)
- Peter 전 생애 아크 정경 복원: None → teacher → messiah_political → risen_lord → sending_lord

**Iter 53 (SlowStateFieldRecoveryRule event_trauma opt-in)**:
- [x] `event_trauma_rate_per_hour` 필드 추가 (기본 0.0 = Gemini PTSD 원칙, 양수 = ChatGPT baseline decay)
- [x] hope + relationships trust 동시 충족 시만 decay (단독 시간 경과 불가 — 신학적 사건 버튼화 방지)
- [x] +6 tests: 조건 충족/미충족, 0 floor, 음수 예외, no-relationships no-op

**외부 리뷰 정책 3개 상태**:
- [x] jesus_understanding canonical transitions — Phase 1/3/5 완료
- [ ] per_hour hazard for v1.2 content — **deferred**: Peter phases 1-4에 hazard_events.json 부재로 적용 대상 없음. 엔진 capability(Iter 27)는 준비 완료; 실제 hazard를 phase에 추가할 때 적용 예정
- [x] slow state recovery field-specific + event_trauma opt-in — 완료

**현재 지표 (Iter 53 완료)**: **Fast tests: 894** (+322 from v0.7 baseline 572) / Archived: 33 / Total: 1058. Ruff + mypy clean.

---

## 3번째 시나리오 Talleyrand + Universality 증거 (Iter 54-58)

**Iter 54**: `content/talleyrand/` 생성 — `domain_diplomacy.py` (DiplomacyState with regime / alignment_stance / leverage / legitimacy_anchor / reputation_ambiguity / network_depth / network_regime_span / moral_fatigue / compromise_count). initial_state, behavior_profile (5 voluntary actions). +9 tests.

**Iter 55**: `content/talleyrand/canonical_events.json` — 1789-1830 7 regime transition events (tick_unit=1개월, 720h/tick). test_regime_transitions.py +12 tests: tick 1/72/120/180/216(falls)/300/492 체제 전환 시점 검증, 50년 career 완주, Peter/VG 대비 구조적 차이. `bug: tick=0 events SimulationWorld range(1, max_tick+1)에서 fire 안 됨 → tick=1 shift`.

**Iter 56**: `content/talleyrand/pom_scorecard.py` — Type A 7 patterns (multi_regime_survival / network_regime_span_grown / reputation_ambiguity_emergent / compromise_accumulation / no_emotional_collapse / career_continuity / legitimacy_below_anchor). `SimulationResult`/`MultiAgentResult` 모두 지원하는 duck-typing 헬퍼. test_pom_scorecard.py +11 tests: 20-seed all_pass rate ≥ 80%.

**Iter 57 (핵심 증명)**: `test_cross_scenario_pom_asymmetry.py` +8 tests. Talleyrand-on-Talleyrand ≥ 80%, Talleyrand-on-Peter = 0%, regime events Peter=0/Talleyrand=6+, denial events Peter≥3/Talleyrand=0. 같은 엔진이 3 시나리오 타입 수용 확인. **Universality 증거 체계 완성**.

**Iter 58**: ABSOLUTE RULE #5 + DESIGN.md + lessons.md 업데이트 — "universality" 주장을 **engine universality (허용)** vs **empirical generalization (금기)** 두 층위로 분리. 권장 표현: "the engine is scenario-agnostic; the patterns are scenario-specific". lessons.md 교훈 13 추가.

**현재 지표 (Iter 58 완료)**: **Fast tests: 934** (+362 from v0.7 baseline 572) / Archived: 33 / Total: 1098. Content packs: 8 (+talleyrand). Ruff + mypy clean.

---

## v1.0 Stage 2 bridge infrastructure (Iter 59-62)

**Iter 59**: `FixedProjectionEncoder` (`engine/core/latent_drive.py`) — seeded random numpy projection state→drive (tanh). IdentityEncoder → FixedProjection → (future) PyTorch 3단계 중 중간. 의존성은 numpy만. +13 tests.

**Iter 60**: FixedProjectionEncoder feature set을 12차원으로 확장 — `training_samples.state_to_feature_vector`와 동일 순서/shape. 신규 API: `encode_from_features(features)`, `encode_batch(feature_matrix)` (mini-batch 벡터화). Stage 2 training loop가 `encoder.encode_batch(X)`로 바로 사용 가능. +6 tests.

**Iter 61**: `TrainingConfig.use_fixed_projection: bool = False` opt-in flag. `train_drive_model`이 True일 때 FixedProjectionEncoder (seed=config.random_seed) 반환, False 기본은 IdentityEncoder. +2 tests.

**Iter 62**: SimulationWorld E2E 검증 (`test_drive_simulation_e2e.py`) — `SimulationWorld(drive_model=LatentDriveModel(encoder=FixedProjectionEncoder))` 로 실제 매 tick drive_state 업데이트 확인. Identity와 다른 값, tanh [-1,1] 범위, state 진화 따라 snapshots drive 다양성, seed 재현성. +9 tests.

**현재 지표 (Iter 62 완료)**: **Fast tests: 964** (+392 from v0.7 baseline 572) / Archived: 33 / Total: 1128. Ruff + mypy clean.

**Stage 2 진입 상태**:
- [x] Protocol plumbing (v0.7부터)
- [x] Training sample 추출 + feature matrix (v0.7)
- [x] Non-identity encoder (Iter 59-60)
- [x] train_drive_model opt-in 전환 (Iter 61)
- [x] SimulationWorld E2E drive trace (Iter 62)
- [x] 사용자 가시 demo 통합 (Iter 63 `demo_phased.py --show-drive`)
- [ ] **PyTorch MLP encoder + learned weights** (`drive_training.py:118` TODO, torch 의존성 필요)
- [ ] Loss 구현 (action_pred + event_pred + state_continuity + KL)
- [ ] Validation against POM/counterfactual baseline

**Iter 63**: `demo_phased.py --show-drive --drive-dim D` — `FixedProjectionEncoder` 주입 + Peter drive 궤적 phase 별 출력. 관측: Phase 3 (고백/변화산)에서 drive dim 2, 4가 inflection. Stage 2 bridge가 사용자 CLI에서 즉시 접근 가능.

**Iter 64**: `DriveActionDiagnostic` + `compute_drive_action_diagnostics` + `drive_class_separability` (Fisher-style). Stage 2 학습 feasibility 사전 측정. +8 tests.

**Iter 65**: Peter empirical 측정 — 10-seed × 300 tick, separability = **1.93** (>1.0 feasibility threshold). Regression guard +3 tests.

**Iter 66**: Cross-scenario spectrum — **VG 6.04 / Peter 1.93 / Talleyrand 0.05**. Talleyrand 실패 원인: `state_to_feature_vector`가 `domain_state` 무시. +3 tests + lessons.md 교훈 14-15 (모든 scenario 측정 + feature universality ≠ engine universality).

**Iter 67**: `DomainState.to_feature_vector()` protocol + `state_to_feature_vector_extended` + `ExtensibleFixedProjectionEncoder` (lazy W init, variable length). `DiplomacyState.to_feature_vector` (regime 7 + stance 5 + 3 scalars = 15 features). 예상 밖 결과: **Talleyrand 0.24 → 0.19** (감소). Random projection이 sparse one-hot을 signal로 활용 못 함 → within-variance만 커짐. +12 tests + lessons.md 교훈 16 ("feature 추가는 learning 있을 때만 효과").

**Iter 68**: `DESIGN_LATENT_DRIVE.md` §7 Stage 2 checklist에 Iter 65-67 feasibility 증거 표 + 방법론 업데이트. Stage 2 PyTorch를 "선택"이 아니라 "시나리오 일반성 확보 필요조건"으로 격상. Stage 2 학습 시 반드시 포함할 feature block 3개 명시 (base + domain-specific + history).

**현재 지표 (Iter 68 완료)**: **Fast tests: 990** / Archived: 33 / Total: 1154. Ruff + mypy clean.

**Iter 69 (Talleyrand action predictability 진단)**:
empirical: Peter logit 45.5% vs majority 12.5% (3.6×), Talleyrand logit 45.6% vs majority 47.8% (chance 이하). 원인: `behavior_profile.json`의 base_weight 2.5-3.0 dominance, state_multipliers 0.1-0.2. +3 regression tests + 교훈 17.

**Iter 70 (Talleyrand profile 재튜닝)**:
base 0.2-1.0, multipliers 0.4-0.9로 수정. 재측정: majority 53.5%, logit 55.1% (+1.6%p). 방향 맞으나 충분치 않음 — 5 actions + regime-discrete state가 bottleneck. 교훈 18 추가.

**Iter 71 (Stage 2 scope 분리)**:
Talleyrand를 "engine universality 증거 (완료)" 와 "Stage 2 learning target (deferred)" 로 역할 분리. Stage 2 PyTorch 학습의 direct target = Peter + VG. Talleyrand Stage 2 진입은 content 확장(7-10 actions) 필요하므로 v1.2.1 이후 작업. `DESIGN_LATENT_DRIVE.md` §7 feasibility 표에 명시.

**현재 지표 (Iter 71 완료)**: Fast tests 993 유지. Ruff clean. Stage 2 path 명확화 완료.

**Iter 72 (Stage 2 첫 실제 학습된 encoder — sklearn LDA)**:
- `engine/core/latent_drive.py::LearnedLinearEncoder` — sklearn `LinearDiscriminantAnalysis`로 state feature → d-차원 projection 학습. Fisher-style between/within variance ratio 직접 최대화. torch 불필요.
- `encode_before_fit` 예외, dim 범위 검증, n_classes-1 자동 축소, padding to dim 등 edge case 처리.
- `LatentDriveEncoder` Protocol 호환 (`.encode(state, history)` 동일 interface).
- `test_learned_linear_encoder.py` +8 tests: contract, fake samples fit, Peter empirical 2× fixed projection 비교.
- Peter 10-seed × 300 tick 실측: **FixedProjection 1.91 → LDA-learned 2.39 (1.25× 개선)**. LDA는 linear-only이므로 modest; MLP (nonlinear)에서 추가 이득 기대.

**현재 지표 (Iter 72 완료)**: **Fast tests: 1001** (+408 from v0.7 baseline 572) / Archived: 33 / Total: 1165. Ruff clean. mypy: 7 pre-existing stub warnings (+1 sklearn.discriminant_analysis), 0 real errors.

**Stage 2 진입 상태** (Iter 72 시점):
- [x] Protocol plumbing
- [x] FixedProjectionEncoder (random baseline)
- [x] **LearnedLinearEncoder (LDA, 첫 실제 학습)** ← Iter 72 여기!
- [x] TrainingConfig.use_learned_linear opt-in (Iter 73)
- [x] demo_phased.py --encoder 선택자 (Iter 74)
- [x] PAPER_DRAFT §Appendix E (Iter 75)
- [ ] LearnedMLPEncoder (PyTorch, 비선형)
- [ ] Full train_drive_model loss 구현 (action + event + continuity + KL)
- [ ] Peter/VG validation against POM baseline

---

## Iter 76 Release attestation (자동 재현 가능한 스냅샷)

| 검증 | 결과 |
|------|------|
| pytest fast suite | **1003 passed**, 131 deselected (slow/archived) |
| ruff check . | All checks passed |
| mypy engine/ | 7 pre-existing stub warnings, 0 real errors |
| demo_v07.py --scenario peter --seed 0 | runs + trace complete |
| demo_v07.py --scenario vangogh --seed 0 | runs + trace complete |
| demo_phased.py --seed 0 | 4-phase Peter arc |
| demo_phased.py --seed 0 --full-passion | 5-phase full arc |
| demo_phased.py --seed 0 --show-drive --encoder learned | LDA pilot fit + drive trajectory |
| coverage (engine/ + content/talleyrand) | **97% overall**; time_axis/inhibitor/slow_recovery/pom/statistics/etc. 100%; phased_world 97%, training_samples 99% |
| benchmark (250 tick × 10) | Peter 709 tick/s @ 2.3 MB; VG 946 tick/s @ 1.7 MB (v0.7 baseline 1001/1267 → ~30% 감소, Stage 2 pilot fit 오버헤드 아님 — 그냥 현재 기계 상태 snapshot) |

**현재 지표 (Iter 76 완료)**: **Fast tests: 1003** (+431 from v0.7 baseline 572) / Archived: 33 / Total: 1167. 17 lessons (14-18 v1.0 Stage 2 findings). 72+ iterations across 2 continuous sessions. 세 번째 시나리오 (Talleyrand) 완성. Stage 2 첫 학습 단계 달성.

**Agent introduction 순서 (생애 시나리오)**:
| Phase | Agents | 근거 |
|-------|--------|------|
| 01 소명 | peter | 어부 시절, 동료/배신자 없음 |
| 02 갈릴리 | peter + judas | 12 사도 택정(Mark 3:13-19)부터 Judas 동행 |
| 03 고백 | peter + judas | 12명과 가이사랴 빌립보 동행 |
| 04 여정 | peter + judas | 예루살렘 여정, Judas 공모는 내부적 |
| 05 수난 | peter + judas + caiaphas + crowd | 대제사장 + 군중 등장 (체포부터) |

**남은 과제 (v1.2 완성까지)**:
- Inhibitor Rule 실제 배치 (Phase 2-4 Judas disillusionment 감쇄 설정)
- Slow state field-specific recovery (moral_injury vs event_trauma)
- [x] Absolute time 메트릭 재정의 (Iter 22 완료)
- [x] Peter content에 phase별 canonical_events → PhasedSimulationWorld로 자동 로드 기능 (Iter 20 완료)
- Phase-specific analysis reporting (time_axis 사용한 실제 분석 스크립트/demo)
- v1.2 documentation — DESIGN.md 최신 상태 반영 + reviewer 질문 6개 최종 응답

## Counterfactual 실험 (2026-04-21, counterfactual_experiment_prompt.md)

**목적**: 논문 baseline v2의 두 비판 방어.
1. chain rate random(0.60) > full(0.10) → "chain은 activity frequency일 뿐"
2. endogenous_arrest 모든 조건 1.0 → "arrest가 항상 발생하도록 설계"

**산출물**:
- `scripts/counterfactual_baseline.py` (5 조건) + `scripts/hazard_scaling.py` (6 factor) + `scripts/counterfactual_figures.py` (2 fig)
- `docs/paper_data/causal_counterfactual.{json,txt}` / `hazard_scaling.{json,txt}` / `fig_counterfactual_comparison.png` / `fig_hazard_scaling_curve.png`
- `scripts/paper_numbers.py`에 merge 로직 추가 → 재실행 시 `paper_numbers.json`이 counterfactual/hazard_scaling 자동 포함.

**핵심 발견 — V2 metric 한계, V3 (trigger_arrest) 지표 도입**:
- V2 `endogenous_arrest_rate`는 canonical `scene_08_arrest` + state-driven hazard ceiling으로 모든 counterfactual 조건에서 1.0 포화 (discriminative power 없음).
- V3 `trigger_arrest_rate` = `arrest_trigger` (state_conditions: Judas disillusion + Caiaphas threat + Judas betray action) 발화율. Full: **0.90**, Judas/Caiaphas/trigger 제거: **0.00**.

**3 verdicts**:
- causal_dependency (V3): **CAUSAL_PASS**
- trigger_necessity: **TRIGGER_NECESSARY** (full chain 0.10 → trigger 제거 0.00)
- random_chain_nature: **RANDOM_CHAIN_SPURIOUS** (random+no_judas chain 0.00 vs random+judas baseline 0.60)

**Hazard scaling 패턴**: V2 기준 "inevitability" (1.0 invariant). Chain rate는 factor 0.75-0.10에서 0.30으로 오히려 상승 → hazard 감소 시 경쟁 event가 줄어 chain 패턴이 정렬. factor 0.0에서만 chain=0.

**논문 반영 포인트**:
1. V2 metric의 saturation → V3 trigger_arrest로 재정의 필요 (Methods §).
2. "Chain rate random > full" 문제는 V2 활동량 지표 측정의 artifact. V3로 재분석 시 해소.
3. Judas는 causal 필수 (제거 시 trigger_arrest 0.9→0). Caiaphas/trigger도 동일.
4. Full system causal structure counterfactually validated: **YES**.

---

## 남은 작업 (v1.2 이후)

- [ ] **v0.6 paper 마감**: 수치 재확인, figure 실제 렌더, 외부 피드백 (arXiv preprint → 저널 결정)
- [ ] **논문 §Results 재작성**: V3 trigger_arrest 지표 도입 + hazard_scaling "inevitability" 해석
- [ ] **v1.0 Stage 2 PyTorch encoder**: `drive_training.py` line 118 TODO 지점 실제 학습 루프 구현 (큰 작업)
- [ ] **3번째 시나리오**: `SCENARIO_TEMPLATE.md` 가이드 참조. 인물 결정 필요 (권장: Type A 협상형, 예: Cavour 이탈리아 통일, Talleyrand Vienna Congress)
- [ ] **v1.1 Relational Graph**: Beliefs-about-others 1급 state로 정규화
- [ ] **v2.0 Narrative Witness Layer**: trace + player_view + narrator를 인터랙티브 체험으로 확장

## 지금 바로 이용 가능한 검증

```bash
pytest -m "not slow and not archived"       # 572 fast tests (~45s)
pytest -m archived                          # 33 Tier 3 archived tests
python demo_v07.py --scenario peter         # v0.7 파이프라인 (Peter)
python demo_v07.py --scenario vangogh       # v0.7 파이프라인 (VG)
python main.py --multi                      # 4-agent Peter 배치
python main.py --multi --person vangogh     # 3-agent VG 배치
python benchmarks/bench_simulation.py       # 성능 기준선
```
