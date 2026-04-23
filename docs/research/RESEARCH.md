# Witness: 연구 발견 정리

> 2026-04-19 기준 (v0.7), 572 fast tests / 97% coverage
> Multi-agent, trigger-mediated, hazard-driven historical simulator

---

## 1. 프로젝트 정의

**"한 사람의 삶에서, 무엇이 갈라지는 순간이었는가?"**

역사적 인물을 에이전트로 모델링하여 수천 번 시뮬레이션하고, 결과 **분포**를 관측한다. 개별 결과가 아니라 파라미터 공간의 지형도, 경로 유형 클러스터, 분기점(bifurcation)을 탐지.

---

## 2. 핵심 아키텍처

- **Multi-agent simulation**: SimulationWorld가 여러 에이전트를 동시 실행
- **Hazard-driven events**: `P(event) = 1 - exp(-h*dt)` (Poisson process)
- **Trigger system**: 에이전트 상태/행동 조건 충족 → 이벤트 동적 생성 (tick 하드코딩 대신)
- **Fast/slow state 분리**: 감정은 항상성 복귀, SlowState는 비가역 누적
- **Engine/content 분리**: engine/에 인물 하드코딩 0건

**두 완성 시나리오**: Peter (4-agent, 500 tick) + Van Gogh (3-agent, 150 tick)

---

## 3. 검증된 핵심 발견

### 3.1 창발적 사건 발생

| 지표 | 값 | 해석 |
|------|-----|------|
| 체포 spontaneous rate (n=100) | **100%** [96.3%, 100%] | tick 하드코딩 없이 자연 발생 |
| Arrest tick mean (n=100) | **199.0, std=42.5, median=196** | 95% CI 좁음 |
| Arrest tick range (n=100) | **[116, 287]** | unimodal, 결정론적 아님 |
| Bimodality coefficient (n=60) | Sarle BC = **0.395** (<0.555 threshold) | **Unimodal** (KDE 1 peak at tick 203) |
| Phase transition | disillusionment ~1.0 임계점 | 낮으면 deadline 의존, 높으면 spontaneous |

**결론**: 체포는 **시스템 내부에서 emergent하게 발생**. 외부 타이머 불필요.
**n=100 replication**: 초기 n=50 결과 (mean 191.4, 100% rate)가 그대로 재현됨 → robust.

### 3.2 인과성 검증

| 검증 | 결과 |
|------|------|
| **Calibration leakage** | Trigger(원인 측)와 POM(결과 측)이 구조적으로 독립 (overlap 0건) |
| **Counterfactual: Judas 제거** | Spontaneous arrest **0%** (필수 원인) |
| **Counterfactual: cross-agent 제거** | Spontaneous arrest **0%** (상호작용 필수) |
| **Explanation faithfulness** | Causal chain이 지목한 에이전트 제거 시 결과 변화 (10/10 runs) |
| **Causal chain frequency** | inform→surveillance→betray→arrest: **100%** |
| **Bottleneck** | surveillance→betray **63 ± 30 ticks** |
| **Judas effect size** | Cohen's d = **-6.87 (large)**, 평균 차이 208 ticks |
| **Permutation test (arrest tick, B=1000)** | p-value **< 0.001** (비모수 유의) |
| **Permutation test (spontaneous rate)** | p-value **< 0.001** (100% vs 0%) |
| **Cross-agent coupling (Judas disill ↔ Peter fear)** | Pearson r = **0.756** (15/15 positive) |
| **Cross-agent coupling (Judas disill ↔ Caiaphas threat)** | Pearson r = **0.894** (15/15 positive) |
| **Lagged correlation peak** | lag=-30, r=0.792 (Peter fear leads Judas disill by ~30 tick) |

### 3.3 예측력

| 검증 | 결과 |
|------|------|
| **Forecasting holdout (n=20, tick 200)** | Witness 80% [63%, 90%] vs random 20% |
| **Forecasting holdout (n=100, tick 200)** | **86% [77.9%, 91.5%]**, Close±1: **100%** |
| **Baseline comparison** | Witness 80% vs majority/fixed/naive 57% (유의미) |
| **Multivariate vs univariate (tick 200, saturated)** | Univariate **80%** > Multivariate **63%** |
| **Multivariate vs univariate (tick 150, pre-saturation)** | Univariate **79%** ≈ Multivariate **83%** |

**핵심**: 
- tick 200의 **Judas disillusionment 단일 변수**만으로 arrest 카테고리 **86% 예측** (n=100)
- 추가 변수(greed, caiaphas.threat)는 tick 200에서 이미 saturate되어 redundant
- tick 150에서는 saturation 전이라 multivariate가 약간 나음 (+4pp), 하지만 CI 겹침
- **"유다의 환멸이 유일한 robust predictive signal"** — saturation 유무와 독립
- n=100 replication에서 accuracy **상승** (80→86%), CI 현저히 좁아짐 → sampling error 아닌 robust signal

**Initial parameter importance ranking** (±2 sweep, n=5):

| 순위 | 파라미터 | baseline | Sensitivity (tick) | Slope |
|------|---------|---------|-------------------|-------|
| 1 | **judas.disillusionment** | 3.0 | **180** | -45/unit |
| 2 | judas.greed | 4.0 | 23 | +5/unit |
| 3 | peter.hope | 7.0 | 17 | - |
| 4 | peter.fear | 2.0 | 3 | - |
| 5 | judas.messiah_expectation | 7.0 | **0** | 0 |
| 5 | caiaphas.threat_assessment | 4.0 | **0** | 0 |

- Disill이 **180 tick 변화** 유발, greed는 **23 tick**만 (8배 격차)
- Peter 전체 파라미터 합 **21 tick** (Judas disill 단일의 1/9) → 비대칭 인과
- threat/messiah_exp 초기값은 **완전 무관**: 시스템이 임계치까지 자연 성장 → saturation
- **Disill × Greed 2x2 factorial**: main_disill -123t, main_greed -4.7t, interaction +8.6t (ratio 0.07, near-additive)
- 이는 forecast 분석과 일관: **"disill이 유일하게 독립적 signal"**, 다른 변수는 상태 dynamics에 흡수됨

**Peter 초기값 영향 asymmetry**:
- Arrest tick 영향: **21 tick** (near zero)
- sword_drawn POM 영향: fear=3 → 70%, fear=5~7 → 80% (Peter state는 자기 POM에만 영향)
- 결론: Peter는 **event의 목격자**, 원인 에이전트 아님

**Judas 행동 시간분포 (phase-by-phase, n=25)**:

| Action | Early (0-100) | Mid (100-200) | Late (200+) |
|--------|--------------|---------------|-------------|
| follow | **65.7%** | 47.1% | 28.2% |
| question | 25.6% | 29.2% | 27.5% |
| inform_authorities | 0.3% | 11.8% | **22.1%** |
| withdraw | 8.5% | 9.5% | 11.4% |
| **betray** | **0%** | 2.3% | **10.9%** |

- **Betray 0건 in early phase, 93% concentrated in late** → 인과 순서 완벽 보존
- Action entropy 증가: early 1.23 → mid 1.84 → late **2.21 bits** (행동 다양성 시간 증가)
- 첫 Judas 행동이 betray인 경우 **0/20 run** (state 누적 없이는 불가능)
- 주 전이: follow↔question 루프 + follow→inform (12%) + inform→follow (31%): 관찰-보고 oscillation

**Peter 행동 arc (arrest-relative, n=20)**:

| Action | Pre-arrest (early) | Pre-arrest (late) | Post-arrest |
|--------|---------------------|--------------------|-------------|
| follow_closely | **69.5%** | 54.8% | 48.3% |
| discuss_with_disciples | 12.5% | 17.8% | 19.3% |
| pray | 11.1% | 11.5% | **16.7%** |
| withdraw_in_fear | 1.6% | 7.0% | **7.9%** |
| **deny** | 0.6% | **2.2%** (76% of all) | 0.0% |
| weep | 0.2% | 2.3% | **4.1%** |

- **follow_closely 감소** 69.5%→48.3% (체포 후 예수 부재)
- **deny peaks in pre_arrest_late** (체포 시점 부근 집중) → POM `triple_denial` 패턴 자연 발생
- **Peter deny count distribution**: mean **3.0**, median 3.0, **97%가 3회 이상** (POM p3 기준 자연 충족)
- **withdraw_in_fear 5배, weep 20배 증가** post-arrest (체포 후 감정 반응)
- 성서와 일관: "3회 부인" + "통곡" 정경 기록이 emergent behavior로 재현

**Peter 감정 궤적 (arrest-relative, n=20)**:

| Offset | Fear | Grief | Hope |
|--------|------|-------|------|
| -100 | 6.29 | 3.00 | 5.20 |
| -50 | 9.57 | 6.28 | 3.60 |
| **0** (arrest) | 8.45 | 9.20 | **2.02** ← hope trough |
| **+25** | 9.77 | **9.41** ← grief peak | 3.21 |
| **+75** | **9.87** ← fear peak | 8.47 | 5.50 |
| +100 | 9.78 | 8.50 | 6.05 |

- **Hope trough at arrest (0)**: 가장 낮은 희망이 정확히 체포 시점
- **Grief peak at +25**: 부인 직후 peak (통곡)
- **Fear peak at +75**: 체포 후 75 tick, 지속 공포
- **Peak grief distribution**: mean 9.98, **100% reach ≥ 8.0** (POM grief_peak 자연 충족)
- **Hope recovery**: min **0.41** → final **7.53** (+7.11, canonical intervention 효과)
- **20/20 final hope ≥ 3.0** (POM eventual_hope 자연 충족)

**VG 감정 궤적 (departure-relative, n=20)**:

| Offset | Fear | Grief | Hope |
|--------|------|-------|------|
| -30 | 6.81 | 4.76 | 9.48 |
| -10 | 9.09 | 7.82 | 9.33 |
| **0** (dep) | 9.47 | 8.97 | **1.29** ← hope trough |
| **+20** | 9.58 | **9.92** ← grief peak | 2.43 |
| **+30** | **9.68** ← fear peak | 9.91 | 2.92 |

- **같은 순서**: hope trough (0) → grief peak (+20) → fear peak (+30) (Peter와 동일)
- **VG hope crash**: 9.33 → 1.29 in 10 tick (slope -0.8/tick). Peter (slope -0.06/tick) 대비 **13배 급격**
- VG peak grief: mean **9.98**, 100% reach ≥7.0 (POM grief_peak 자연 충족, Peter 수치 정확히 동일)
- **Cross-scenario emotional isomorphism**: peak ORDER 완벽 일치, dynamics만 다름

### 3.4 Forecast Horizon: 언제부터 예측 가능한가?

**Peter** (max_tick=500, arrest ~191):

| Horizon | Accuracy | Mean disill |
|---------|----------|-------------|
| tick 50 | 40% | 4.2 |
| tick 100 | **20%** (최저) | 5.6 |
| tick 150 | 44% | 7.1 |
| tick 200 | 62% | 8.4 |

**Van Gogh** (max_tick=150, departure ~77):

| Horizon | Accuracy | Mean frust | n_valid |
|---------|----------|------------|---------|
| tick 20 | 60% | 4.3 | 20 |
| tick 40 | 60% | 5.7 | 20 |
| tick 60 | **79%** | 7.1 | 19 |
| tick 80 | 71% | 8.5 | **7** (sample depletion) |

**핵심 차이**: Peter는 horizon 늦을수록 정확도 단조 증가, VG는 60에서 peak 후 하락.
- Peter arrest 분포(~200) + max=500 → horizon 200에서도 여유
- VG departure 분포(60-102) + max=150 → horizon 80에서 대부분 완료 + survivor bias
- **함의**: Forecast horizon-accuracy 곡선은 **scenario-specific surface pattern** (분포-horizon 상대 위치가 결정). Deep structure와 구별되는 층위.

**Decision window 발견** (tick 정밀 분석):
- Peter: **75-100 구간이 decision window** (growth rate std 0.69, 최대)
- 125-175는 **separation plateau** (갈래 완전히 벌어짐)
- tick 100 부근에서 경로가 갈라짐 → low disill(<5) 평균 arrest 224 vs high(≥5) 182

**Non-parametric validation (Spearman rho)**:

| Horizon | ρ (disill@h vs arrest_tick) | 강도 |
|---------|----------------------------|-----|
| tick 50 | -0.570 | moderate-strong |
| tick 100 | -0.733 | strong |
| tick 150 | -0.785 | strong |
| tick 200 | **-0.876** | **very strong** |

tick 200 bootstrap 95% CI: **[-0.987, -0.594]** (분포 가정 없이 음의 상관 유의).
Horizon 늦어질수록 |ρ| 단조 증가 → accuracy와 동일 방향, 순위 기반에서도 확인.

**Time-to-threshold 분석** (Peter disill, n=30):

| Threshold | Mean reach tick | 95% CI | Gap from prev |
|-----------|----------------|--------|---------------|
| 5.0 | 86.2 | [75.3, 97.1] | - |
| 6.0 | 125.3 | [113.7, 136.9] | **39.1** |
| 7.0 | 160.0 | [146.0, 173.9] | 34.7 |
| 8.0 | 184.9 | [170.5, 199.3] | **24.9** (가속) |
| 9.0 | 212.7 | [199.3, 226.1] | 27.8 |

- **Arrest tick mean 191.4** ≈ threshold 8.0 도달 tick 184.9 + 7 tick
- **7→8 gap 최소 (24.9)**: trigger 임계(8.0) 근처에서 가속
- **Pearson r(threshold 7.0 도달, arrest_tick) = 0.938**: 거의 완벽 상관, mean gap **31.5 tick**
- 역의 관점 일관성: "disill이 얼마일 때 몇 tick" = "tick에서 얼마의 disill" 양방향 일치

**VG Time-to-threshold** (Gauguin frustration, n=30):

| Threshold | Mean reach tick | 95% CI | Gap from prev |
|-----------|----------------|--------|---------------|
| 5.0 | 32.2 | [29.0, 35.4] | - |
| 6.0 | 44.5 | [41.0, 47.9] | 12.3 |
| 7.0 | 61.1 | [57.7, 64.5] | 16.6 |
| 8.0 | 74.0 | [69.7, 78.4] | **12.9** |
| 9.0 | 92.0 | [87.4, 96.6] | 18.0 |

- **Departure tick mean 76.6** ≈ threshold 8.0 도달 tick 74.0 + 2.6 tick (Peter 대비 타이트)
- **7→8 gap 12.9**: 전체 평균(15.0)보다 짧음 (약한 가속), Peter 패턴 완화판
- **Pearson r(threshold 6.0 도달, departure_tick) = 0.766**, mean gap **32.1 tick**
- Peter와 VG 모두 "임계 도달 → 이벤트 발생" 30 tick 선행 패턴 동일 (surface timing 차이 불구)

### 3.5 강건성 (Robustness)

| 검증 | 결과 |
|------|------|
| Trigger threshold +20% | 체포 44 tick 지연 (파괴 아님) |
| Trigger threshold -20% | 차이 거의 없음 |
| Rule-family ablation (n=30, CI) | 모든 ablation CI가 baseline과 겹침 → **POM이 특정 규칙에 과적합되지 않음** |
| Seed sensitivity | CV = **21.4%** (moderately stochastic) |
| Noise scale 역설 | noise 증가 시 std 감소 (regression to mean) |
| **Initial perturbation smoothness** | disill init 1→5 스윕 시 arrest 313→125, diffs [74,41,46,26] (bifurcation 없음) |
| **Attractor stability** | Small perturbation (±0.5) effect **38.1 tick** < seed std **42.8 tick** |
| **Sample size convergence** | CI width n=80/n=20 = **0.49** (이론 0.50), sqrt(n) scaling 준수 |
| **Adequate n for spontaneous rate** | n=40 lower bound 91.2%, n=80 lower bound 95.4% |

**주요 stochasticity 원천**: state_noise가 아니라 **AgentScheduler의 random activation order**.

**Attractor 해석**: 초기 조건 small perturbation 효과가 내부 stochasticity보다 작음 → 
시스템은 **stable attractor 주변**에 있음 (결정론적 chaos 아님). 
역사적 함의: "유다가 조금 더 환멸했더라면?" 같은 micro-counterfactual은 체포 시점에 작은 shift만 유발.

### 3.6 Negative Controls (금지된 결과 억제)

| 검증 | 결과 |
|------|------|
| Arrest before Last Supper (tick<100) | 0/20 (완전 억제) |
| Restoration without prior breakdown | 0/20 (인과 질서) |
| Peter performing betrayer actions | 0건 |
| Self-harm frequency | 15% (역사적 희귀성 유지) |
| No impossible paths | 0건 |

시뮬레이터는 **조건에 맞는 사건만 발생**시키고, 불가능한 경로를 만들지 않는다.

### 3.7 Cross-Scenario Structural Isomorphism

| 진행도 (normalized) | Peter (Judas disill/8) | VG (Gauguin frust/8) | Cohen's d |
|-------|----------------------|---------------------|-----------|
| 50% | 68% | 70% | -0.30 (small) |
| 75% | 84% | 85% | -0.24 |
| 90% | **94%** | **96%** | **-0.47 (small)** |

**구조적 동형 확인**: 인물은 달라도 임계점 접근 패턴이 유사.

**Counterfactual 역할 구조 isomorphism**:

| 시나리오 | 필수 원인 (제거 시 spontaneous 0%) | 버퍼 (제거 시 감정만 악화) |
|---------|---------------------------------|-----------------------|
| Peter | Judas (d=-6.87 on arrest) | Crowd/Caiaphas (완화/가속) |
| VG | Gauguin (필수, w/o → 10/10 deadline) | Theo (d=9.07 on confidence) |

**공통 구조**: 각 시나리오마다 "central driver + emotional buffer" 패턴.
- Gauguin 제거: 10/10 deadline-assisted (spontaneous 0건)
- Theo 제거: VG confidence 8.17 → **-8.22** (d=9.07 huge effect), departure tick 영향 없음 (d=-0.17)

### 3.8 Cross-Scenario Difference (Decision Window)

| Segment | Peter std | VG std |
|---------|-----------|--------|
| 20-40% | **0.63** ← Peter peak | 0.34 |
| 60-80% | 0.55 | **0.44** ← VG peak |

**Kolmogorov-Smirnov test** (normalized event tick 분포 비교, n=30 each):

| 지표 | 값 |
|------|-----|
| Peter normalized mean | 0.383 (range [0.23, 0.57]) |
| VG normalized mean | 0.510 (range [0.40, 0.70]) |
| **KS statistic D** | **0.567** |
| D_crit (α=0.01) | 0.421 |
| **Significance** | **α=0.01 유의** |

- 정규화해도 분포가 통계적으로 다름 → **surface timing 진짜로 다름** (단순 scaling 차이 아님)
- Peter는 시나리오 전반부(0.38)에서, VG는 후반부(0.51)에서 임계 도달
- **Dual-layer 가설 KS 증거**: 표면(분포) 다름 + 심층(acceleration, POM 구조) 동형

**표면 차이**: Decision window 위치가 다름.
- Peter: 초반형 (20-40%에서 경로 결정)
- VG: 후반형 (60-80%에서 경로 결정)

**심층 공통**: 80-100%에서 growth 가속 (둘 다).

### 3.9 Narrative Anomaly Analysis

Forecast exact match 아닌 경로(20%) 분석:
- **늦은 체포 (≥230 tick)**: 평균 disill@200 = 6.7
- **빠른 체포 (<170 tick)**: 평균 disill@200 = 9.5
- 편차가 **random noise 아닌 개연성 있는 대체 역사**
- 내적 일관성: 20/20 (모든 run에서 grief 누적 유지)

### 3.10 Stochasticity Architecture (Hazard Poisson Check)

**Dual-layer stochasticity 검증** (n=213 intervals, 20 runs):

| 층위 | 지표 | 해석 |
|------|-----|------|
| Background hazard | Inter-arrival CV = **0.85** | Poisson-like (CV=1.0 기준) |
| Hazard chi-square | **26.64** > 11.35 (α=0.01) | 정확한 exponential 아님 (mixture) |
| Trigger (arrest) | CV = **0.21** | state-driven 수렴 |

- Hazard 층은 거의 Poisson, trigger 층은 state-driven 집중
- **이중 구조**: "Poisson 배경 위에 결정론적 수렴" 설계 정당성 입증

### 3.11 Terminal Attractor (Final State Convergence)

**Final state variance** (n=30):

| Agent.field | Mean | Std | CV |
|-------------|------|-----|-----|
| judas.disillusionment | **10.0** | 0.00 | **0.00** |
| judas.greed | 10.0 | 0.00 | 0.00 |
| judas.guilt | 10.0 | 0.00 | 0.00 |
| caiaphas.threat | 10.0 | 0.00 | 0.00 |
| peter.fear | 9.80 | 0.17 | **0.02** |
| peter.hope | 7.52 | 0.72 | 0.10 |
| peter.love | 8.29 | 0.57 | 0.07 |
| peter.grief | 3.79 | 1.02 | 0.27 |

- **모든 Judas/Caiaphas domain states가 천장 saturate** (zero variance)
- Peter emotions CV 0.02~0.27 (강한 수렴)
- Peter final hope 20/20 ≥ 3.0 (POM eventual_hope 보편적 충족)
- **해석 (교정된 버전)**: 스토캐스틱 프로세스에도 불구하고 **현 규칙계에서 강한 terminal attractor 형성**. 이는 [0,10] 스케일의 천장 saturation + 현 rule 구조의 결과이지 역사적 필연성 증거는 아님.

### 3.12 Checkpoint Bottleneck Analysis

**Per-checkpoint match rate** (event-relative, n=30):

| Checkpoint | Pass rate | Phi |
|------------|-----------|-----|
| grief_peak | 100% | 0.000 |
| moral_injury | 100% | 0.000 |
| deny_3 | 96.7% | 0.186 |
| restoration | 73.3% | 0.603 |
| sword_at_arrest | 43.3% | 0.605 |
| **follow_after_arrest** | **23.3%** | 0.079 |

- 이중 병목: **sword_at_arrest** (action 선택) + **follow_after_arrest** (좁은 시간 창)
- Overall match ≥ 50%: **100%** (모든 run 과반 통과)
- 향상 여지: follow_after_arrest의 `relative_offset` 조정

### 3.13 External Validity — Train/Test Split Generalization

**LLM 리뷰 4차 지적 대응**: 지금까지 forecast 검증은 in-sample. 진짜 generalization 검증 추가.

**Train/Test split** (seeds 0-29 train, seeds 30-59 test):

| Feature | Train acc | Test acc | Overfit gap |
|---------|-----------|----------|-------------|
| withdraw rate @ tick 100 | 83.3% | **73.3%** | +10.0% |
| disill @ tick 150 | 83.3% | **88.9%** | -5.6% |

- **Disill signal은 overfit gap negative** (test > train): 완전 robust
- **Withdraw signal은 10pp overfit**: 약간 seed-specific threshold fitting

**5-fold CV (withdraw @ tick 100)**: mean **72%** [60%, 80%], std 8.4%
- 5 folds 모두 threshold ~0.08 근처로 수렴 → rule 자체는 안정

**의의**: 첫 external validity 증거. 기존 in-sample 결과가 심한 overfit이 아님을 확인.
**한계**: 같은 distribution에서 train/test. 완전한 "외부 데이터" 검증은 여전히 미흡.

### 3.14 Behavioral Rate Signals (Action Regression)

Action count regression에 **time confound** 존재 (모든 r > 0): 
시간 지날수록 행동 횟수 증가 → 모든 행동이 arrest_tick과 양의 상관.

해법: **rate (count / pre_arrest_tick)로 정규화**:

| Action | Count r | Rate r | 해석 |
|--------|---------|--------|------|
| judas.withdraw | +0.221 | **-0.942** | confound 제거 시 강력 negative 등장 |
| peter.weep | +0.879 | +0.796 | late-arrest pattern (방향 보존) |
| peter.follow_closely | +0.966 | -0.599 | 방향 반전 |
| judas.inform_authorities | +0.704 | +0.415 | 약화 |

**Behavioral forecast** (tick 100 withdraw rate, 2-class):
- Best threshold: 0.08/tick, accuracy **83.3%** [66.4%, 92.7%]
- State-based forecast reference: disill@200 86%
- **behavioral signal이 state보다 먼저 발현**: withdraw rate@100 (73%) > disill@100 (63%)

**함의**: 에이전트의 "결정 궤적"이 state 변화보다 먼저 행동에 나타남.
Judas의 withdraw는 의식적 disengagement의 조기 지표.

**Cross-scenario behavioral signal isomorphism** (n=25 each, rate regression):

| 시나리오 | Driver 행동 | Rate r (vs event tick) |
|---------|----------|---------------------|
| Peter | judas.withdraw | **-0.942** |
| VG | gauguin.critique | **-0.922** |

- **구조 동형**: 양쪽 시나리오 모두 **driver 에이전트의 "공격적" 행동 rate**가 가장 강한 negative 시그널
- Judas의 withdraw = 감정적 철회, Gauguin의 critique = 언어적 비판
- 공격 빈도 높을수록 event 빠름 → "아가 상대를 밀어내는 행동이 임계 가속"

---

## 4. 방법론적 기여

### 4.1 Trigger-mediated emergent event generation

기존 ABM들: 에이전트 간 상호작용 (network)  
Witness 기여: **Trigger가 구조화된 사건 생성** (agent-agent negotiation과 외부 사건 시스템의 중간)

### 4.2 Event-relative checkpointing

Tick-bound 검증은 emergent timing과 충돌 (체포 tick 분산 119-283).
해법: `relative_to_event` + `relative_offset` 파라미터.
- 효과: Peter multi-agent match rate **35.5% → 80.3%** (+44.8pp)

### 4.3 POM (Pattern-Oriented Modeling) 다층 검증

단일 지표가 아니라 7패턴 동시 만족 + event-relative + counterfactual ablation.
- Current rules: 47.5% all_pass (n=40, bootstrap CI [32.5%, 62.5%])
- Parametric CI [32.9%, 62.5%] — bootstrap과 거의 일치 (width diff 0.4%)
- Rule ablation CI 겹침 → rule-specific overfitting 없음

**Peter 패턴별 통과율 + Phi(pattern→all_pass)** (n=40):

| Pattern | Pass rate | Phi |
|---------|-----------|-----|
| grief_peak | 100% | 0.000 (universal) |
| eventual_hope | 100% | 0.000 (universal) |
| moral_injury | 97.5% | 0.152 |
| identity_damage | 97.5% | 0.152 |
| triple_denial | 90.0% | 0.317 |
| no_flee | 75.0% | 0.549 |
| **sword_drawn** | **50.0%** | **0.951** |

- `sword_drawn`이 **single bottleneck**: P(all_pass | sword_drawn 실패) = **0%**

**VG 패턴별** (n=40, all_pass 15%, bootstrap CI [5%, 27.5%]):

| Pattern | Pass rate | Phi |
|---------|-----------|-----|
| creative_output | 100% | 0.000 |
| gauguin_conflict | 100% | 0.000 |
| grief_peak | 100% | 0.000 |
| identity_damage | 100% | 0.000 |
| **self_harm** | **15%** | **1.000** |

**Cross-scenario POM bottleneck isomorphism**:
- Peter 병목: `sword_drawn` (50%, Phi 0.951) — 드문 저항 행동
- VG 병목: `self_harm` (15%, Phi **1.000**) — 드문 위기 행동
- 둘 다 **단일 rare-action pattern**이 POM 통과율 상한 결정
- **공통 구조**: "4-6개 상시 충족 패턴 + 1개 희귀 행동 bottleneck" (구조 동형)

### 4.4 Dual-layer Universal Pattern

**심층 구조**: 모든 시나리오에서 공통 (threshold accumulation, 가속 곡선)  
**표면 타이밍**: 시나리오별 다름 (decision window 위치)

---

## 5. 한계 및 미래 작업

### 5.1 알려진 한계

- **Gauguin post-departure activity**: 에이전트 "떠남" 이후에도 행동 계속 (엔진 한계)
- **Saturation at holdout 200**: greed/threat가 포화되어 multivariate 이득 없음
- **Sample size**: 대부분 n=20~30, n=100+에서 재검증 필요 항목 있음

### 5.2 다음 가능한 방향

1. **Agent retirement mechanism**: depart/die 후 에이전트 비활성화
2. **Earlier holdout analysis**: tick 150 부근에서 multivariate가 정보 더 주는지
3. **Third content pack**: 동역학 유형 다른 인물 (정치가, 협상형)
4. **Human baseline comparison**: 전문가/비전문가 예측과 비교
5. **Expert validation**: 역사 전공자 검증

---

## 6. 한 줄 요약

**Witness는 multi-agent 시뮬레이터로 역사적 사건의 창발적 발생을 재현하고,
그 인과 구조를 통계적/반사실적으로 검증했으며,
두 시나리오(Peter, Van Gogh)에서 "심층 구조는 공통, 표면 타이밍은 다름"의
dual-layer universal pattern을 발견했다.**

---

## 7. 검증 가능성 (Reproducibility)

- 416 tests (fast 358 / slow 58), 96% coverage
- Ruff + mypy strict clean
- 시드 재현성: PASS
- Engine/content 분리: 0 hardcoding
- 모든 발견은 pytest로 재검증 가능

```bash
python demo.py --quick           # 모든 핵심 결과 10초 내
pytest -m "not slow"             # 빠른 검증 (358 tests, ~45s)
pytest                           # 전체 (416 tests, ~4분)
```
