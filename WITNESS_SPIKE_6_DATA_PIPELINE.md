# WITNESS v2.0 — Spike 6 연장: 데이터 파이프라인 재설계

**생성 배경:**
Spike 6에서 Peter neural policy 인프라는 완성됐지만, 학습 결과가 majority
baseline(val_acc=68%)에 고정. 외부 리뷰 3종(Gemini, ChatGPT, 내부 분석)이
공통으로 지적한 근본 원인 — 샘플 수(108)가 아니라 **데이터 생성 파이프라인
자체가 다양한 데이터를 못 만드는 구조**.

**이전의 함정 (피할 것):**
- ❌ "그냥 seed 10 → 1000으로 늘리기" → ChatGPT 명시 배제 (*"majority만 더 많아짐"*)
- ❌ "LLM으로 데이터 품질 검사" → ChatGPT 명시 배제 (*"distribution 깨짐"*)
- ❌ 현재 Peter neural policy를 "살아 움직인다"고 해석 → noisy sampler일 뿐

**선행 조건:**
- Spike 6 완료 (engine/policies/, NeuralDecisionPolicy, Protocol, 3 callsite 통합)
- 1176+ fast tests green
- Rule #11 (dual-path fallback) 준수 상태

**폐기:**
- Spike 7/8/9+ 이전 계획은 이 파이프라인 재설계가 끝난 뒤 재수립

---

## 0. 이 Spike의 본질 재정의

### 0.1 "좋은 데이터"란 무엇인가

Lee가 원하는 "천변만화" 를 가능케 하려면 데이터가:

1. **상태 공간을 넓게 커버해야 한다** — canonical 궤적 근처만이 아니라
2. **Rare action이 학습 가능한 support를 가져야 한다** — 최소 200개/class
3. **Decision boundary 근처 샘플이 있어야 한다** — 같은 state에서 다른 action
4. **Environment 다양성을 반영해야 한다** — 같은 Peter라도 다른 예루살렘에서

현재 108 샘플은 위 4개 중 **하나도 충족하지 못한다.**

### 0.2 이 Spike가 안 하는 것

❌ Neural model 아키텍처 변경 (ResNet / LSTM 등)
❌ Feature 확장 (domain_state, environment를 feature에 추가)
❌ Loss function 변경 (FocalLoss / Weighted CE)
❌ 새로운 agent 추가 (Judas, Jesus 등)
❌ Active Learning (모델이 majority 고정인 상태에서 의미 없음)
❌ LLM denoising (distribution 왜곡)

**이 Spike는 오직 "데이터를 어떻게 만드는가" 파이프라인에 집중.**

위 제외 항목들은 **파이프라인이 완성된 후 Phase 3에서 재검토.** 지금 건드리면
변경 원인이 어디인지 판단 불가능해짐.

### 0.3 왜 파이프라인 먼저인가

ChatGPT 정확한 지적:

> *"좋은 데이터는 '많이 돌려서' 생기는 게 아니라 '의도적으로 분포를 깨서' 만든다."*

파이프라인이 bad면:
- 모델 아무리 키워도 학습 안 됨
- Feature 아무리 추가해도 같은 분포만 학습
- Loss 아무리 바꿔도 majority 여전히 dominant

파이프라인이 good이면:
- 작은 모델로도 의미 있는 학습
- Feature 확장 효과가 비로소 드러남
- Class imbalance 자연 해소

**순서가 중요하다. 파이프라인 → 그 다음 모델/feature/loss.**

---

## 1. ABSOLUTE RULES 상태

기존 Rule #1-11 전부 유지. 신규 rule 없음.

특히 중요:
- **Rule #6** (engine/ public interface 수정 금지) — 파이프라인 추가는 `engine/policies/` 하위 또는 신규 `scripts/` 에서
- **Rule #8** (기존 테스트 보존) — 1176+ tests 전부 green 유지
- **Rule #11** (dual-path fallback 유지) — 데이터 생성 중 규칙 기반 엔진 손대지 말 것

---

## 2. Phase 1 — 진단 (선행 필수)

### 2.1 의도

파이프라인을 설계하기 전에 **현재 변수 공간과 엔진 capability**를 실측한다.
이걸 모르면 또 추측으로 설계하게 됨.

### 2.2 진단 항목

다음 6개를 실측하고 보고한다:

#### 2.2.1 기존 108 샘플 분포 측정

```
- 각 12 feature의 min/max/mean/std/histogram
- 각 action별 state 분포 (어떤 state에서 어떤 action이 나왔는가)
- Tick별 state 궤적 (얼마나 좁은 범위를 돌고 있는가)
```

산출물: `docs/person/diagnostics/existing_sample_distribution.md`

**이게 "현재 얼마나 좁은 공간에서 돌고 있는가"의 base rate.**

#### 2.2.2 Peter engine의 초기 상태 허용 범위

```
- AgentState 초기값을 extreme으로 설정했을 때 engine이 crash하는 경계
- 어떤 조합이 "비현실적"인지 (fear=10 + hope=10 같은)
- Engine의 자동 clipping / validation 로직이 있는지
```

산출물: `docs/person/diagnostics/initial_state_bounds.md`

**방법:**
- fear를 0, 2, 4, 6, 8, 10으로 sweep
- 각 값에서 다른 변수 extreme 조합 시도
- Engine crash / unreasonable behavior 기록

#### 2.2.3 Tick 수 확장 가능성

```
- 현재 seed당 10 tick → 50 tick, 100 tick, 500 tick 돌려봤을 때
  engine이 안정적인가
- 긴 궤적에서 state가 어디로 수렴하는가 (attractor 존재?)
- Canonical_events 없을 때 Peter가 "이상한 상태"로 가는가
```

산출물: `docs/person/diagnostics/tick_extension_test.md`

#### 2.2.4 Environment intervention 가능성

```
- World engine의 InterventionSpec (Spike 4)을 Person Engine에서 호출 가능한가
- Peter의 behavior가 environment 변수에 실제로 반응하는가
  (현재 reward / weight formula가 environment를 참조하는가)
- 혹시 Person Engine이 environment를 무시하고 있지는 않은가
```

산출물: `docs/person/diagnostics/environment_responsiveness.md`

**이 결과에 따라 Phase 2 Environment 다양화 가능 여부가 결정된다.**

#### 2.2.5 Forced action 가능성

```
- engine/core/action.py::select_action이 강제 action을 받을 수 있는가
- 현재 구조에서 "이 tick에 이 action을 강제로 실행" 가능한가
- Forced action 이후 state transition이 정상 계산되는가
```

산출물: `docs/person/diagnostics/forced_action_feasibility.md`

**가능하면 ChatGPT의 "forced action rollouts" 전략 사용 가능.
불가능하면 engine 수정이 필요하거나 다른 전략으로 전환.**

#### 2.2.6 Counterfactual branching 가능성

```
- 특정 tick의 state를 복제해서 여러 branch rollout 가능한가
- State의 deep copy가 engine 구조에서 지원되는가
- Branch 간 RNG 분기가 가능한가 (determinism 유지)
```

산출물: `docs/person/diagnostics/counterfactual_branching.md`

### 2.3 Phase 1 완료 기준

- [ ] 6개 진단 보고서 모두 작성
- [ ] Lee가 보고서를 확인하고 Phase 2 설계에 사용 가능
- [ ] 기존 1176+ tests green 유지 (진단은 read-only, 코드 수정 금지)
- [ ] ruff/mypy clean 유지

### 2.4 Phase 1 진행 중 막혔을 때

1. Engine이 예상외 방식으로 crash → Lee에게 보고, 수정 여부 Lee 판단
2. 진단 중 Rule #6 위반 유혹 (engine/ 수정해야 할 것 같음) → 진행 중단, Lee 판단
3. Environment intervention이 구조적으로 불가능 → Phase 2 설계 변경 필요, Lee 보고
4. 진단 결과가 서로 모순 → Lee와 해석 상의

**Phase 1 완료 없이 Phase 2 진입 금지. Lee가 진단 결과를 본 후 다음 지시사항 발급.**

---

## 3. Phase 2 — 데이터 파이프라인 구축 (Phase 1 완료 후)

### 3.1 설계 철학

ChatGPT의 추천 pipeline (Step 1-6)을 뼈대로, Gemini의 Stress Injection과
Environment 다양화를 보강한다.

**골격:**
```
baseline 100 seeds run
   → trajectory 저장
각 trajectory에서:
   → decision point 추출 (slicing)
각 state에서:
   → counterfactual perturbation (3-5 branch)
   → forced action rollout (Phase 1에서 feasible 판정 시)
Parameter sweep:
   → 희귀 영역 집중 (rare action state)
Stress injection:
   → fear=9.5 같은 극단 상태 강제 주입
Environment 다양화:
   → InterventionSpec으로 100가지 예루살렘 (Phase 1에서 feasible 판정 시)
Balanced sampling:
   → dataset 구성 시 각 action 최소 수 보장
Noise injection:
   → state에 N(0, 0.5) noise 추가 (마지막 단계)
```

### 3.2 Phase 2A — baseline trajectory harvesting

#### 3.2.1 목표

ChatGPT의 Step 1-3. Decision point와 negative samples 포함한 풍부한 trajectory
수집.

#### 3.2.2 요구사항

**기존 코드 변경 최소화:**
- 기존 `build_behavior_cloning_dataset` 는 그대로 유지
- 신규 `build_enriched_dataset` 를 `engine/policies/neural/dataset.py` 에 추가
  또는 `scripts/data_pipeline/` 에 별도 모듈

**수집 대상:**

```python
@dataclass
class EnrichedSample:
    state: AgentState
    available_actions: list[ActionOption]  # 이 tick에 선택 가능했던 것 전부
    selected_action: str                    # 실제 선택
    action_weights: dict[str, float]        # rule-based가 계산한 weights
    next_state: AgentState                  # 상태 전이
    tick: int
    seed: int
    scenario_id: str
```

기존 dataset은 `(state, action)` 만 저장. Enriched는 **ranking learning**과
**transition learning** 둘 다 가능한 형태.

#### 3.2.3 목표 수량

- 100 seeds × 평균 100 tick (Phase 1 결과 따라 조정)
- 예상: 약 10,000 enriched samples

### 3.3 Phase 2B — counterfactual perturbation

#### 3.3.1 목표

ChatGPT 전략 2. 같은 state에서 다른 action 경로 생성 → decision boundary 학습.

#### 3.3.2 구현 방식

```python
# baseline trajectory의 특정 tick에서 분기
for trajectory in baseline_trajectories:
    for branch_tick in [25, 50, 75, 100]:  # 몇 tick에서 분기할지
        base_state = trajectory[branch_tick]
        for perturbation in perturbations:
            # perturbation 예시:
            # {"fear": +2}, {"hope": -2}, {"fatigue": +3}
            branched_state = apply_perturbation(base_state, perturbation)
            rollout_samples = run_rollout(branched_state, length=20)
            collect(rollout_samples)
```

**Perturbation 범위:** Phase 1 진단 결과에 따라 결정
- "안전 범위"가 좁으면 ±1-2 수준
- 넓으면 ±3-5까지 가능

### 3.4 Phase 2C — parameter sweep (rare action 중심)

#### 3.4.1 목표

ChatGPT 전략 1 + Gemini 전략 1. 희귀 action이 나오는 state 영역을 체계적으로
방문.

#### 3.4.2 구현 방식

**1단계: rare action 유발 state 분석**

기존 108 샘플에서 rare action (withdraw_in_fear, assert_loyalty, pray)이
나왔을 때 state가 어땠는지 분석. 공통 패턴 추출.

예:
- withdraw_in_fear: fear > 8, fatigue > 6, moral_injury > 5 근처에서 나옴
- assert_loyalty: hope > 7, love > 8, confusion < 3 근처에서 나옴

**2단계: 해당 영역 집중 sweep**

```python
# withdraw_in_fear 영역
for fear in np.linspace(7, 10, 10):
    for fatigue in np.linspace(6, 10, 8):
        for moral_injury in np.linspace(5, 10, 6):
            # 다른 변수는 기본값 또는 random
            state = build_state(fear=fear, fatigue=fatigue, moral_injury=moral_injury)
            rollout = run_short_rollout(state, length=10)
            collect(rollout)
```

각 rare action에 최소 200개 샘플 목표.

### 3.5 Phase 2D — stress injection (Gemini 전략 2)

#### 3.5.1 목표

Tick 100에서 극단 상태 강제 주입 후 관찰. Parameter sweep과 다른 점:
**자연 궤적 중에 기습적으로 극단 상태를 만든다.**

#### 3.5.2 구현 방식

```python
for seed in range(100):
    simulation = create_simulation(seed)
    for tick in range(200):
        simulation.step()
        if tick == 100:  # 극단 주입 시점
            simulation.agent('peter').state.emotions.fear = 9.5
            simulation.agent('peter').state.physical.fatigue = 8.0
        if tick >= 100 and tick < 120:
            collect_sample(simulation)  # 주입 후 20 tick 관측
```

### 3.6 Phase 2E — environment 다양화 (Phase 1 feasible 판정 시)

#### 3.6.1 목표

Gemini 전략 3. World engine InterventionSpec으로 다양한 예루살렘 생성.

#### 3.6.2 구현 방식 (Phase 1 결과에 따라)

**Option A — Phase 1에서 environment 반응 확인됨:**
```python
environments = [
    {"staple_price": 2.0, "roman_alertness": 0.1, "crowd_density": 0.2},  # 평화기
    {"staple_price": 5.0, "roman_alertness": 0.8, "crowd_density": 0.9},  # 긴장기
    # ... 100가지
]
for env in environments:
    for seed in range(20):
        run_with_environment(env, seed)
```

**Option B — Phase 1에서 environment 반응 미확인:**
Phase 2E 건너뜀. Feature 확장 후 재검토 (Phase 3).

### 3.7 Phase 2F — balanced sampling + noise injection

#### 3.7.1 Balanced sampling

```python
target_per_action = 1000  # 각 action 목표
final_dataset = []

for action in action_vocab:
    candidates = [s for s in all_samples if s.selected_action == action]
    if len(candidates) >= target_per_action:
        final_dataset.extend(random.sample(candidates, target_per_action))
    else:
        # 부족하면 전부 포함 + oversampling 보고
        final_dataset.extend(candidates)
        log_warning(f"{action}: only {len(candidates)} samples")
```

**주의:** balanced sampling은 **학습용 dataset** 에만 적용. 분포 분석용
원본 데이터는 별도 보존.

#### 3.7.2 Noise injection (마지막 단계)

```python
for sample in final_dataset:
    sample.state.emotions.fear += np.random.normal(0, 0.3)
    sample.state.emotions.hope += np.random.normal(0, 0.3)
    # 모든 feature에 약한 noise
    # clip to [0, 10]
```

**주의:** noise는 **학습 전 마지막 단계**. Counterfactual perturbation보다
훨씬 작은 scale (0.3 vs 2-3).

### 3.8 Phase 2 완료 기준

- [ ] Phase 2A-F 모두 완료 (2E는 Phase 1 결과에 따라 skip 가능)
- [ ] 최종 dataset: 최소 5,000 / 각 action 최소 200
- [ ] 분포 분석 보고서 (`docs/person/diagnostics/pipeline_output_analysis.md`)
- [ ] 기존 `build_behavior_cloning_dataset` 호환성 유지
- [ ] 기존 1176+ tests green 유지
- [ ] ruff/mypy clean 유지

### 3.9 Phase 2 진행 중 막혔을 때

1. Phase 1 진단과 모순되는 상황 발견 → Lee 판단 필요
2. Balanced sampling에서 특정 action이 여전히 50개 미만 → 전략 변경 보고
3. Counterfactual branching에서 engine state 손상 → 복구 후 Lee 보고
4. 데이터 생성 시간이 예상의 5배 초과 → 범위 축소 여부 Lee 판단
5. 생성된 데이터의 분포가 여전히 편향 (majority > 50%) → 파이프라인 재설계 필요

---

## 4. Phase 3 — 학습 재시도 + 평가 (Phase 2 완료 후)

### 4.1 의도

파이프라인이 만들어낸 데이터로 **기존 모델 재학습**. 모델 구조는 건드리지
않는다. 데이터만 바꿨을 때 학습 품질이 얼마나 개선되는지 측정.

### 4.2 평가 지표 (ChatGPT 지적 수용)

**Accuracy 외에 다음을 반드시 측정:**

#### 4.2.1 Per-class metrics
- Precision / Recall / F1 per action
- Rare action에서 모델이 실제로 학습했는지 확인

#### 4.2.2 Behavior fidelity metric (ChatGPT 핵심 지적)
- **Per-state KL divergence** between rule-based and neural weights
- "같은 state에서 두 policy가 얼마나 다른가" 정량화
- **"살아 움직인다"의 정확한 측정법**

#### 4.2.3 Sequence-level divergence (Gemini 지적)
- Neural policy로 full trajectory rollout
- Rule-based trajectory와의 divergence
- 현재의 20-34% divergence가 **학습의 결과인지 noise인지** 판정

#### 4.2.4 Log-likelihood
- Validation set에 대한 NLL
- Accuracy보다 더 신뢰할 수 있는 지표

### 4.3 Phase 3 완료 기준

- [ ] 기존 모델로 새 dataset 재학습
- [ ] Val accuracy > majority baseline (68%) 최소 10%p 이상 초과
- [ ] 각 rare action에서 F1 > 0.3 이상
- [ ] Behavior fidelity metric 계산 완료
- [ ] Lee가 결과 확인: "이제 모델이 실제로 학습한 것으로 보이는가?"
- [ ] 위 기준 미달 시 Phase 4 (feature 확장 등)로 진행 여부 Lee 판단

### 4.4 Phase 3 진행 중 막혔을 때

1. **여전히 majority baseline에 고정** → 파이프라인 문제 (Phase 2로 back) or
   feature 문제 (Phase 4로 forward) Lee 판단
2. **Accuracy는 좋은데 behavior fidelity 나쁨** → Lee 해석 필요 (정상일 수도)
3. **Rare action F1이 0** → 해당 action의 샘플 질 재검토
4. **Training loss는 떨어지는데 validation은 그대로** → overfit, 정상적 현상

---

## 5. 이번 대화에서 확인된 함정 (피할 것)

### 5.1 "단순 seed 증가"의 유혹

ChatGPT 명시 배제. 절대 *"일단 1000번 돌려보자"* 로 시작하지 말 것.
Parameter sweep + stress injection이 먼저.

### 5.2 LLM denoising

Gemini 전략 4는 ChatGPT 전략과 충돌 — distribution 왜곡.
**사용 금지.** 데이터 품질 검사에 LLM 쓰지 말 것.

### 5.3 "살아 움직인다"는 환상적 해석

현재 `STAGE2_PETER_PROGRESS.md`에 기록된 *"20-34% divergence는 살아 움직이는가의
원천"* 은 **잘못된 해석**. 이번 Spike 진행 중 해당 문장을 다음으로 수정:

> *"20-34% divergence는 학습 품질 부족으로 인한 noise. 'behavior fidelity'
> metric으로 측정하기 전까지 '학습된 다양성'이라고 해석하지 않음."*

### 5.4 파이프라인 완성 전 다른 개선 시도

Feature 확장, loss 변경, 모델 아키텍처 변경은 **파이프라인 완성 후**에
검토. 지금 건드리면 변화 원인 판단 불가.

### 5.5 Active Learning

Gemini 전략 5. 현재 모델이 majority baseline에 고정된 상태라 "모델 불확실성"이
의미 없음. Phase 3 이후 모델이 실제로 학습된 후에 검토.

---

## 6. 자율 vs 보고 구분

### Claude Code 자율 결정 영역

- Parameter sweep의 구체적 grid 해상도 (10? 20? 50?)
- Counterfactual branching의 branch 수 (3? 5? 10?)
- Noise injection의 std (0.1? 0.3? 0.5?)
- Tick 길이 (50? 100? 200?)
- Seed 수 (50? 100? 200?)
- 데이터 저장 포맷 (numpy? parquet? json?)
- 진단 보고서의 구체적 figure 디자인

### Lee 판단 필수 영역

1. Phase 1 진단 보고서 6개 전부 완료 후 → Phase 2 진입 허가
2. Phase 2F (balanced sampling) 에서 특정 action이 100개 미만일 때
3. Phase 3 결과가 여전히 majority baseline에 가까울 때
4. Environment intervention이 불가능하다고 Phase 1에서 확인된 경우
5. Forced action이 불가능하다고 확인되어 Step 5 전략 변경 필요 시
6. Engine 수정 필요성이 제기될 때 (Rule #6 관련)
7. 데이터 생성 시간이 예상보다 크게 길어져 범위 조정 필요 시

---

## 7. 산출물 구조

```
docs/person/diagnostics/              (Phase 1)
  existing_sample_distribution.md
  initial_state_bounds.md
  tick_extension_test.md
  environment_responsiveness.md
  forced_action_feasibility.md
  counterfactual_branching.md

scripts/data_pipeline/                (Phase 2, 신규 디렉토리)
  baseline_harvest.py                 (Phase 2A)
  counterfactual_branch.py            (Phase 2B)
  rare_action_sweep.py                (Phase 2C)
  stress_injection.py                 (Phase 2D)
  environment_variation.py            (Phase 2E, feasible 시)
  balance_and_noise.py                (Phase 2F)
  build_final_dataset.py              (통합)

engine/policies/neural/
  dataset.py                          (기존 + EnrichedSample 확장)

content/peter/trained/                (Phase 3)
  peter_bc_v2.pt                      (재학습 결과)
  peter_bc_v2.feature_config.json

docs/person/
  STAGE2_PETER_PROGRESS.md            (업데이트, 환상적 해석 수정 포함)
  DATA_PIPELINE_v1.md                 (최종 파이프라인 문서)
```

---

## 8. 세션 관리

### Phase 1 (진단)
- 1-2 세션
- 각 진단 항목은 독립적, 병렬 수행 가능
- 완료 후 Lee 확인 대기 (자동 Phase 2 진입 금지)

### Phase 2 (파이프라인 구축)
- Phase 2A-F를 세션 분리 권장
- Phase 2A + 2B는 한 세션, 2C + 2D는 한 세션, 2E + 2F는 한 세션
- 데이터 생성 자체가 시간 걸리므로 overnight 실행 고려

### Phase 3 (재학습 + 평가)
- 1-2 세션
- 재학습은 분 단위, 평가가 대부분 시간

### 세션 간 context 유지
- 매 세션 `DATA_PIPELINE_v1.md` 업데이트
- 진단 결과는 `docs/person/diagnostics/` 에 축적
- 실패한 시도도 기록 (성공만 기록 금지)

---

## 9. 목표 수치 (ChatGPT 권장)

| 항목 | 현재 | 목표 |
|---|---|---|
| 총 샘플 수 | 108 | 5,000~20,000 |
| 각 action 최소 | 1 (withdraw_in_fear) | 200+ |
| State 공간 커버리지 | ~5% 추정 | 30%+ (Phase 1 측정 후 목표 재조정) |
| Rare action F1 | 0에 가까움 | 0.3+ |
| Val accuracy | 68% (= majority) | 78%+ |

**주의:** 이 수치는 기준선이지 하드 목표 아님. Lee가 Phase 3 결과를 보고
*"의미 있는 학습이 일어났다"* 고 판단하는 것이 최종 기준.

---

## 10. 한 줄 요약

**"파이프라인이 bad면 모델/feature/loss를 아무리 바꿔도 소용없다.
진단(Phase 1) → 파이프라인 구축(Phase 2) → 재학습(Phase 3) 순서로,
단순 seed 증가와 LLM denoising 함정을 피해 의도적으로 분포를 깨는
데이터를 만든다."**

---

## 부록 — Lee에게

이 파일은 이전 대화에서 반복된 실수(지엽적 목록 → 하드코딩 최적화)를
피하기 위해 **"진단 먼저"** 를 맨 앞에 박았다. Phase 1 진단 없이 Phase 2로
넘어가면 또 추측 기반 설계가 반복된다.

파이프라인이 완성된 후에야 "Feature 확장", "모델 아키텍처", "Loss 변경"
같은 ChatGPT/Gemini의 다른 지적들이 의미를 가진다. 지금은 그 지적들을
의도적으로 무시하고 파이프라인만 본다.

Rule #11 (dual-path)을 엄격하게 유지하는 이유: Phase 2/3 진행 중 데이터
파이프라인이 실패해도 **기존 규칙 기반 엔진은 영향받지 않아야 한다.**
신경망 전환의 안전장치는 계속 유지.
