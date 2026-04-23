# WITNESS v2.0 — Spike 6 연장 2회차: 학습 가능한 데이터 생성

**생성 배경:**
Spike 6 1회차 연장(데이터 파이프라인)으로 샘플 63×, action vocab 3× 확대,
val_acc majority +28.9%p 개선 달성. 그러나 외부 리뷰 2종이 공통 지적:

> *"이 파이프라인은 '데이터를 많이 만드는 시스템'은 완성됐다.
> 근데 '배울 수 있는 데이터'를 만드는 단계는 아직 아니다."* (ChatGPT)
>
> *"양적 팽창의 한계점. 1,500 시드를 더 돌려도 F1=0 클래스는 해결 안 됨."* (Gemini)

이번 Spike는 **"양"이 아니라 "학습 가능성"** 에 집중.

**남은 근본 병목 4가지:**
1. Baseline trajectory 편중 (89%) → teacher forcing 수준
2. Rare action sampling 실패 (rollout 몇 tick 후 follow_closely attractor로 흡수)
3. 4개 action F1=0 고정 (weep, fall_asleep, follow_at_distance, run_to_tomb)
4. 12-feature로는 event-driven action 분리 불가 (aliasing)

**선행 조건:**
- Spike 6 1회차 연장 완료
- `data/person/pipeline_v1/` 의 6,821 balanced samples 존재
- `content/peter/trained/peter_bc_v2.pt` 재학습 모델 존재
- 1176+ tests green

---

## 0. 핵심 원칙 (ChatGPT 정확한 지적)

### 0.1 학습 가능성의 본질

```
같은 상태에서 다른 행동이 나오면 → 학습 불가능 (noise)
다른 상태에서 다른 행동이 나오면 → 학습 가능 (decision boundary)
```

**현재 데이터 상태:**
```
state S → follow / withdraw / deny (뒤섞임)
→ 모델 입장: noise
```

**목표 데이터 상태:**
```
state S1 → follow_closely
state S2 → withdraw_in_fear
state S3 → deny
→ 경계 학습 가능
```

### 0.2 이번 Spike가 안 하는 것

❌ 샘플 수 추가 증가 (현재 6,821로 충분)
❌ 모델 아키텍처 변경 (1637 파라미터 MLP 유지)
❌ Loss function 변경 (Phase 4 이후)
❌ Class-weighted loss (Phase 4 이후)
❌ Active learning (모델 안정화 후)

**이번은 오직 "데이터 생성 방식 근본 전환" 에 집중.**

### 0.3 Rule 상태

- Rule #1-11 전부 유지
- **Rule #6 해석 명확화**: engine 수정 금지이지만 `scripts/` 에서 SimulationWorld
  state를 직접 patching하는 것은 허용. 이전 파이프라인에서 이를 회피해서
  initial-state로 근사한 결과 rare action 실패. **이번에는 허용되는 범위 내에서
  "난폭한 확충" (Gemini 지적) 가능.**

---

## 1. 작업 구조 (ChatGPT 우선순위 + Gemini 보강)

### 우선순위

| 순위 | 작업 | 출처 |
|---|---|---|
| 1 | Forced action sampling 구현 | ChatGPT 지침 #1, #4 |
| 2 | Event context feature 추가 | ChatGPT 지침 #3, Gemini "temporal context" |
| 3 | Baseline 비율 제한 | ChatGPT 지침 #5 |
| 4 | Separability test (학습 전 검증) | ChatGPT 지침 #8 |
| 5 | Boundary-focused noise | ChatGPT 지침 #7 |

**Class-weighted loss, Correlated noise, NLL 중심 평가 등은 Phase 4로 유보.**
먼저 데이터가 학습 가능해져야 loss 변경의 효과를 측정할 수 있음.

---

## 2. Phase A — Forced Action Sampling

### 2.1 핵심 전환

**이전 (1회차):**
```python
for initial_state in perturbed_states:
    rollout_result = simulation.run(initial_state, length=40)
    samples.append(rollout_result)
# → rollout 중 follow_closely attractor로 흡수됨
```

**이번 (2회차):**
```python
for state in target_states:
    for action in available_actions_at(state):
        # rollout 없이, 이 state에서 이 action을 했다면의 결과만 기록
        next_state = engine.compute_transition(state, action)
        samples.append((state, action, next_state))
# → 각 state에서 모든 action을 체계적으로 확보
```

### 2.2 구현 요구사항

#### 2.2.1 Target state 생성 (ChatGPT 지침 #1 + #2)

각 action의 "결정 경계 영역"을 명시적으로 정의:

```
withdraw_in_fear: fear > 7 AND hope < 3
pray: fatigue > 6 AND hope > 5 AND confusion > 4
assert_loyalty: love > 7 AND hope > 7 AND confusion < 3
deny: fear > 8 AND moral_injury > 5
weep: grief > 7 AND moral_injury > 5
...
```

각 action의 경계 영역을 **기존 108 샘플 + Phase 1 진단에서 추출**. 이 경계 영역
내에서 grid sampling으로 target_states 생성.

#### 2.2.2 Forced transition 계산

- `engine/core/action.py::select_action` 의 weight 계산 우회
- 주어진 (state, action) 쌍에 대해 state transition만 호출
- 이것이 scripts/ 수준에서 가능한지 먼저 확인 (Phase 1 진단에서 "forced action 가능" 판정됨)

#### 2.2.3 목표 수량 (ChatGPT 지침 #2)

각 action마다 **최소 200~300 샘플 강제 생성**. 자연 발생 기다리지 말 것.

현재 분포 (1회차 결과):
- follow_closely: 10,606 (과잉)
- run_to_tomb: 14 (부족)
- confess: 45 (부족)
- follow_at_distance: 81 (부족)
- fall_asleep: 166 (부족)

→ 부족한 action부터 강제 채움:
```python
for action in action_vocab:
    current_count = count_samples(action)
    while current_count < 300:
        target_state = sample_boundary_state(action)
        transition = forced_sample(target_state, action)
        save(transition)
        current_count += 1
```

### 2.3 Phase A 완료 기준

- [ ] Forced action sampling 모듈 (`scripts/data_pipeline/forced_sampling.py`) 구현
- [ ] 각 15 action에 최소 200 샘플 확보
- [ ] `data/person/pipeline_v2/forced/` 저장 완료
- [ ] 기존 1176+ tests green 유지

---

## 3. Phase B — Event Context Feature 추가

### 3.1 배경 (ChatGPT 지침 #3, Gemini 공통)

**현재 F1=0인 4개 class의 원인:**

| Action | 현재 support | 원인 |
|---|---|---|
| weep | 127 | grief 높음 + moral_injury 높음이라는 state는 pray와 겹침 |
| fall_asleep | 33 | event-triggered (게세마네), state만으로 구분 불가 |
| follow_at_distance | 81 | 체포 직후라는 맥락 없으면 follow_closely와 구분 불가 |
| run_to_tomb | 14 | 부활 주일 고유, 시간 정보 없으면 설명 불가 |

**공통 원인:** 12-feature에 **시간/event 정보가 없음**.

### 3.2 추가할 Feature (최소 구현)

```python
extended_features = [
    # 기존 12 feature
    fear, hope, grief, confusion, love,
    fatigue, hunger, health,
    moral_injury, identity_shift, event_trauma, trust_scar,
    # 신규 3-5 feature
    recent_event_id,       # 최근 발생 event의 categorical ID
    time_since_event,      # 최근 event로부터 경과 tick
    hazard_proximity,      # 가까운 hazard까지 거리 (optional)
]
```

### 3.3 구현 요구사항

#### 3.3.1 Event ID 추출

- Person Engine이 이미 event를 track하는지 확인 (Phase 1 진단에서 확인됨)
- Event ID를 integer로 indexing
- Unknown / no_event는 0

#### 3.3.2 Feature vector 확장

```python
# engine/simulation/training_samples.py 수정 또는
# engine/policies/neural/dataset.py 에 extended_feature_vector 함수 추가

def state_to_extended_feature_vector(state, context):
    base = state_to_feature_vector(state)  # 기존 12
    extended = [
        context.recent_event_id,
        context.time_since_event,
        context.hazard_proximity,
    ]
    return base + extended  # 15-dim
```

**주의:** 기존 `state_to_feature_vector` 는 **유지**. 신규 함수를 병행 제공하여
기존 학습 코드 호환성 확보.

#### 3.3.3 모델 입력 차원 변경

- 기존: `BehaviorCloningMLP(in_dim=12, n_actions=5)`
- 신규: `BehaviorCloningMLP(in_dim=15, n_actions=15)` (또는 현재 15 action 유지)

### 3.4 Phase B 완료 기준

- [ ] Extended feature vector 함수 구현
- [ ] 기존 12-feature 함수 유지 (backward compatible)
- [ ] Dataset builder가 extended feature 옵션 지원
- [ ] Phase A에서 생성한 forced samples에 extended feature 추출 가능 확인
- [ ] 1176+ tests green 유지

---

## 4. Phase C — Baseline 비율 제한

### 4.1 배경 (ChatGPT 지침 #5)

현재 데이터 구성:
- baseline (Phase 2A): 22,756 (89%)
- rare sweep (2C): 2,259 (9%)
- perturbation (2B): 110 (0.4%)
- stress (2D): 122 (0.5%)

모델이 **baseline policy의 softened version만 학습**. "다양한 상황" 학습 아님.

### 4.2 목표 비율

```
baseline: ≤ 50%
forced sampling (Phase A): ≥ 50%
```

### 4.3 구현 방식

최종 dataset 구성 시:

```python
# 샘플링 가중치
if sample.source == 'baseline':
    sample.include_prob = 0.3
elif sample.source in ['forced', 'boundary']:
    sample.include_prob = 1.0
elif sample.source in ['rare_sweep', 'perturbation']:
    sample.include_prob = 0.8

final_dataset = stratified_sample(all_sources, weights=include_prob)
```

### 4.4 Dual dataset 유지 (ChatGPT 지침 #6 보강)

**학습용과 분포 보존용을 분리:**

```
data/person/pipeline_v2/
  balanced_for_training/    ← baseline ≤ 50%, 학습에 사용
  raw_natural/              ← 원본 분포 보존, calibration용
```

학습된 모델이 실제 분포에서 얼마나 벗어나는지 측정할 때 raw_natural 사용.

---

## 5. Phase D — Separability Test (학습 전 검증)

### 5.1 배경 (ChatGPT 지침 #8)

현재 데이터를 신경망에 던지기 전에, **linear classifier로 먼저 분리 가능한지
확인**. 이게 안 되면 데이터 문제지 모델 문제가 아님.

### 5.2 검증 테스트 3종

#### 5.2.1 Linear Separability Test

```python
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

lr = LogisticRegression(max_iter=1000)
scores = cross_val_score(lr, X, y, cv=5)
print(f"Linear classifier accuracy: {scores.mean():.3f}")

# 기준: 0.6 이상이면 "학습 가능한 데이터"
#       0.6 미만이면 "데이터에 분리 가능한 구조 없음"
```

#### 5.2.2 Consistency Test

```python
# 같은 state에서 같은 action이 얼마나 일관되게 나오는가
for state_cluster in kmeans(X, k=50):
    actions_in_cluster = y[state_cluster]
    dominant_action = mode(actions_in_cluster)
    consistency = count(actions_in_cluster == dominant_action) / len(actions_in_cluster)

# 기준: 평균 consistency > 0.7 이면 학습 가능
```

#### 5.2.3 Feature Importance (ChatGPT 지침 #8-3)

```python
from sklearn.ensemble import RandomForestClassifier
rf = RandomForestClassifier(n_estimators=100)
rf.fit(X, y)

# 각 action별로 중요한 feature가 뚜렷한가?
for action in action_vocab:
    mask = y == action_vocab.index(action)
    importance = rf.feature_importances_
    # 기준: 각 action마다 top-3 feature가 뚜렷하면 학습 가능
```

### 5.3 Separability Test가 실패하면?

**이 경우 Phase A/B/C로 되돌아감.** 신경망 학습 금지.

실패 유형별 조치:

| 실패 | 원인 추정 | 조치 |
|---|---|---|
| Linear acc < 0.6 | 데이터에 구조 없음 | Phase A 재실행, target state 재설계 |
| Consistency < 0.7 | 같은 state에 여러 action | Phase B (event context feature) 강화 |
| Feature importance 평탄 | Feature가 action 구분 못 함 | Phase B 확장 (추가 feature) |

### 5.4 Phase D 완료 기준

- [ ] 3종 separability test 실행
- [ ] 모든 기준 통과 또는 Phase A/B/C 재실행
- [ ] 결과 보고서 `docs/person/diagnostics/separability_v2.md`
- [ ] Lee 확인: **"데이터가 학습 가능한 상태인가"** 감각 판단

---

## 6. Phase E — Boundary-Focused Noise (선택적)

### 6.1 배경 (ChatGPT 지침 #7)

1회차의 균일 Gaussian noise (σ=0.3) 는:
- 전체 blur 효과
- Decision boundary는 여전히 모호
- Gemini 지적: "상관관계 유지 안 된 noise"

### 6.2 개선 방식

```python
def add_boundary_noise(state, action):
    if is_near_decision_boundary(state, action):
        # 경계 근처에서만 강한 noise
        return state + np.random.normal(0, 0.8, size=state.shape)
    else:
        # 경계에서 먼 영역은 약한 noise
        return state + np.random.normal(0, 0.2, size=state.shape)
```

**Decision boundary 판정 방법:**
- 해당 action의 canonical condition(Phase A 2.2.1)에서 거리 측정
- 거리 < threshold 이면 boundary 근처

### 6.3 선택적 이유

Phase A-D만으로 separability test 통과 시 Phase E 생략 가능. **과도하게 noise
추가하면 오히려 학습 방해**. Lee 판단으로 진행 여부 결정.

---

## 7. Phase F — 재학습 + 평가 (모든 Phase 완료 후)

### 7.1 학습

기존 `engine/policies/neural/trainer.py` 그대로 사용. 단 in_dim=15 (extended feature).

```python
train_behavior_cloning(
    train_ds, val_ds,
    epochs=50, batch_size=64, lr=1e-3,
    seed=0,
)
```

### 7.2 평가 지표 (ChatGPT + Gemini 공통)

#### 7.2.1 기본 지표
- Val accuracy
- Per-class precision / recall / F1
- Macro F1 (모든 class 평등 가중)

#### 7.2.2 Behavior fidelity (1회차와 비교)
- Per-state KL divergence
- 1회차 KL 1.44 대비 개선 여부

#### 7.2.3 Rare action 구제 확인
- F1=0이었던 4개 action (weep, fall_asleep, follow_at_distance, run_to_tomb)이
  F1 > 0 으로 바뀌었는가
- 특히 Phase B (event context) 효과 직접 측정

### 7.3 Phase F 완료 기준 (Lee 감각 판단)

수치 기준이 아닌 Lee의 판단:

- [ ] **"이제 모델이 실제로 학습했다"** 고 느끼는가
- [ ] **"Peter가 이전과 다르게 반응한다"** 고 느끼는가
- [ ] F1=0 class 중 최소 1-2개 구제됨
- [ ] 기존 5개 F1 ≥ 0.5 class가 여전히 유지됨

---

## 8. 최종 체크리스트 (ChatGPT 지침 #10 수용)

파이프라인 v2 완료 시점에 다음이 전부 체크되어야 함:

- [ ] 각 action ≥ 200 샘플
- [ ] baseline ≤ 50%
- [ ] Forced sampling 포함
- [ ] Event context feature 포함
- [ ] 동일 state → action consistency > 0.7
- [ ] Linear separability acc > 0.6
- [ ] Feature importance 뚜렷

---

## 9. Phase별 세션 권장

| Phase | 세션 | 예상 소요 |
|---|---|---|
| Phase A (Forced sampling) | 1-2 세션 | 구현 + 데이터 생성 |
| Phase B (Event feature) | 1 세션 | 함수 추가 + 기존 호환 |
| Phase C (Baseline 제한) | 0.5 세션 | 기존 파이프라인 확장 |
| Phase D (Separability) | 0.5 세션 | 검증 + 보고서 |
| Phase E (Boundary noise) | 0.5 세션 (선택) | Lee 판단 |
| Phase F (재학습 + 평가) | 1 세션 | 실험 + Lee 검토 |

**한 세션에 Phase A-F 전부 시도 금지.**

---

## 10. 각 Phase 진행 중 막혔을 때

### Phase A (Forced sampling)
1. Engine state transition이 scripts/ 에서 호출 불가능 → Lee 판단 (engine 수정 필요 여부)
2. 특정 action의 boundary 정의 불가능 → Lee와 조건 상의
3. Forced transition이 engine crash 유발 → 경계 영역 축소

### Phase B (Event feature)
1. Event ID tracking이 Person Engine에 없음 → Lee 판단 (engine 수정 허용 여부)
2. Event vocabulary가 너무 많음 → 주요 event만 선택, Lee 상의
3. Time since event 계산이 모호 → 정의 Lee 상의

### Phase C (Baseline 제한)
1. 50% 제한 시 총 샘플 수가 급감 → Phase A에서 forced sampling 추가 생성
2. 특정 action이 baseline에만 존재 → Phase A에서 해당 action 집중 생성

### Phase D (Separability)
1. Linear acc < 0.6 → **Phase A/B로 rollback**, 재설계
2. Consistency < 0.7 → **Phase B 강화** 후 재시도
3. 특정 action만 분리 불가 → 해당 action의 target state 재정의

### Phase E-F
Phase A-D가 성공하면 이 두 Phase는 기술적 이슈 거의 없음.

---

## 11. 산출물 구조

```
scripts/data_pipeline/                            (신규 추가)
  forced_sampling.py                              (Phase A)
  extended_features.py                            (Phase B)
  baseline_limiter.py                             (Phase C)
  separability_check.py                           (Phase D)
  boundary_noise.py                               (Phase E, 선택)
  build_final_dataset_v2.py                       (통합)

engine/policies/neural/
  dataset.py                                      (기존 + extended 옵션)

data/person/pipeline_v2/                          (신규 디렉토리)
  forced/
  extended_features/
  balanced_for_training/
  raw_natural/
  final/
    dataset.npz                                   (학습용)
    meta.json                                     (vocab + source distribution)

content/peter/trained/
  peter_bc_v3.pt                                  (Phase F 결과)
  peter_bc_v3.feature_config.json

docs/person/
  STAGE2_PETER_PROGRESS.md                        (업데이트)
  diagnostics/
    separability_v2.md                            (Phase D 결과)
  DATA_PIPELINE_v2.md                             (최종 문서)
```

---

## 12. 이번 Spike의 정신

**Lee의 원래 비전 재확인:**
> *"신경망 학습을 통해 천변만화하는 세상을 시뮬레이터로써 구축"*

**1회차 연장의 한계:**
- 데이터 많이 만들기는 달성
- 배울 수 있는 데이터 만들기는 미달성

**이번 2회차의 목표:**
- 모델이 **왜 이 행동인지** 설명할 수 있는 데이터
- 각 action마다 **distinct region** 존재
- **Decision boundary가 학습 가능한** 구조

---

## 13. 한 줄 요약

**"좋은 데이터는 '많은 데이터'가 아니라 '행동이 왜 갈리는지 드러나는
데이터'다. Forced sampling으로 경계를 만들고, Event context로 feature를
해상하고, Baseline 편중을 제한하고, 학습 전 separability로 검증한다."**
