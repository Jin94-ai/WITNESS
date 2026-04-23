# WITNESS v3.0 — Phase 2 v2 Dynamics: 상태 동역학 채우기

**생성 배경:**
Phase 2 v2 구조(Active 20 + Candidate 10 + Derived 8 + 3 Layer + Rubric)는 완성.
첫 실측(1 seed × 30 tick) 결과 `run_to_tomb` 7회 / `grief` 0.5 stuck / drift 28.5 
발생. 두 외부 LLM 검증 결과 **공통 진단**:

> *"Ontology가 아니라 동역학(dynamics)이 비어 있다.
> 27 direct edges 중 10개만 구현, state transition이 장면에 반응 못 함.
> policy tuning / threshold 보정 / multi-seed 이전에 동역학부터."*

**이 지시의 범위:**
상태 동역학을 채우는 한 묶음. 개별 결정이 아니라 **8개 결정이 상호 연결**되어 
한 번에 진행.

**이 지시가 안 하는 것:**
- Ontology 재설계 (Active 20 대부분 유지)
- Threshold 재보정 (동역학 완료 후)
- Multi-seed ensemble (동역학 완료 후)
- BC 재학습 (동역학 완료 후)
- Scene template 도입 (1차 구현 후 판단)

**선행 조건:**
- Phase 2 v2 구현 완료 (277 tests green)
- 첫 실측 결과 존재 (`docs/person/v3_measurement/peter_v3_seed0_ticks30.json`)
- 두 외부 LLM 검증 완료

---

## 0. 작업 방식 (핵심)

### 0.1 Lee 승인 대기 최소화

Lee 지시: *"전문적인 영역에서 방향을 정하는 건 너가 해줘. 내 승인을 
기다리는 작업들이 너무 많아서 작업 진행이 잘 안 되는 거 같아."*

이 지시를 따라:
- Claude Code는 **아래 결정 1-8을 Lee 재승인 없이 그대로 실행**
- 각 결정의 구체 수치, 공식, 우선순위는 Claude Code 자율
- Lee 개입 시점: **방향이 틀렸다고 Lee가 명시적으로 말할 때만**

### 0.2 Phase 내 자율 실행 흐름

```
Step 1 → Step 2 → Step 3 → ... → Step 8
각 Step 완료 후 실측 한 번 + 다음 Step 자동 진입 (Lee 승인 대기 없음)
단, Step 8 완료 후에만 Lee 검토
```

### 0.3 보고 vs 실행

**보고만 (대기 없이 계속 실행):**
- 각 Step 완료 (간략히 한 줄)
- 중간 실측 수치

**멈추고 Lee 판단 필요 (드문 경우):**
- 277 tests 중 5개 이상 깨지는데 원인 구조적
- ABSOLUTE RULES 위반 가능성 발견
- 결정 1-8과 명백히 충돌하는 예기치 못한 상황
- Active 변수 또는 3 Layer 구조 변경 필요성

---

## 1. 결정 요약 (8개, 순차 실행)

| # | 결정 | 영향 | Step 순서 |
|---|---|---|---|
| 1 | Dynamics first | 작업 범위 | (prerequisite) |
| 2 | faith_stage → Derived 강등 | Active 20 → 19 | Step 1 |
| 3 | Pressure 공식 가중합+clip 전환 | Layer C 전면 | Step 2 |
| 4 | Availability gate 2단 구조 | Action selection | Step 3 |
| 5 | Direct edges 20개 우선 구현 | State transition | Step 4 |
| 6 | Scene template 보류 | (skip) | - |
| 7 | guilt/shame semantics 분리 | 문서 정정 | Step 5 |
| 8 | Threshold/Multi-seed/BC 후순위 | (skip) | - |

각 Step 상세는 §3 이하.

---

## 2. ABSOLUTE RULES 준수

기존 Rule #1-18 전부 유지. 이번 지시로 추가되는 Rule 없음.

특히 주의:
- **Rule #12:** 월드는 행동 결정 금지. Availability gate는 인물 측 로직이지 
  월드가 행동 결정하는 게 아님. gate 조건에 월드 상태를 참조하는 건 OK.
- **Rule #15:** Active 변수 수. faith_stage 제거 시 Active 19개. 새 변수 추가 
  안 하면 문제 없음. 만약 hesitation 추가가 필요하다고 판단되면 Lee 보고 후 
  결정 (Active 20 유지를 위해).
- **Rule #17:** Level C 자동 Active 금지. 이번 작업은 기존 Active만 다룸.

---

## 3. Step 1 — faith_stage 강등

### 3.1 작업

`faith_stage` 를 Active 등록에서 제거. Derived 계산으로 이동.

### 3.2 이유

ChatGPT 지적:
> *"faith_stage = none/follower/tested/failed/restored/shepherd/foundation은 
> 상태 변수가 아니라 서사 압축 레이블이다. 관찰자의 사후 태그. Active에 두면 
> 시스템이 우리가 발견하려는 것을 이미 상태에 넣어버리는 leakage가 발생한다."*

### 3.3 구현

**삭제:**
```
engine/person/state_v3.py
  ActiveState.faith_stage 필드 제거
```

**이동:**
```
engine/person/state_derived.py
  faith_stage_tag 계산 함수 추가
  입력: love[jesus], guilt[jesus], trust[jesus], shame, hope
  출력: 7개 Literal 중 하나
```

**계산 규칙 (Claude Code 자율 결정):**

대략 방향:
- love[jesus] 높음 + guilt[jesus] 없음 + trust[jesus] 높음 → follower 또는 shepherd
- guilt[jesus] 매우 높음 + love[jesus] 유지 → failed
- shame 높음 → tested
- ... etc

정확한 threshold는 Claude Code가 기존 initial_state/targets 참고하여 결정.

### 3.4 Rubric 처리

Rubric의 character_critic에서 faith_stage를 직접 참조하던 부분 있으면:
- Active state가 아니라 derived 계산 결과를 참조하도록 변경
- Rubric 보조 feature로 계속 사용 가능 (leakage 아님)

### 3.5 테스트

- `test_state_v3.py` 에서 faith_stage 관련 테스트 수정
- `test_derived.py` 에 faith_stage_tag 계산 테스트 추가
- Active 개수 테스트: `assert active_count == 19` (20에서 19로)

### 3.6 Step 1 완료 조건

- [ ] faith_stage가 ActiveState에 없음
- [ ] faith_stage_tag가 Derived에서 계산됨
- [ ] 277 tests green 유지 (수정 반영 후)

---

## 4. Step 2 — Pressure 공식 가중합+clip 전환

### 4.1 작업

Layer C의 8 Pressure 전체를 곱셈 → 가중합+clip 으로 전환.

### 4.2 이유

두 LLM 공통 지적:
- Gemini: *"곱셈은 All-or-Nothing. 한 인수가 0이면 전체 0."*
- ChatGPT: *"AND 구조는 실제 사회적 압력과 안 맞음. 주효과 먼저."*

### 4.3 전환 규칙

각 Pressure마다:

**현재 (예):**
```python
social_threat = 10 * crowd_density * accusation_visibility * authority_presence
```

**전환 후 (예):**
```python
social_threat = clip(
    5 * accusation_visibility + 3 * crowd_density + 2 * authority_presence,
    min=0, max=10
)
```

### 4.4 가중치 결정 원칙

Claude Code 자율 결정. 기본 원칙:
- **주효과(main effect)가 큰 변수에 더 큰 가중치**
- 가중치 합은 대략 10 (clip 범위에 맞춤)
- 변수 3개면 대략 5+3+2 또는 4+4+2
- 변수 2개면 6+4 또는 5+5

### 4.5 특별 케이스: sacred_salience

ChatGPT 지적:
> *"sacred_salience = religious_context × hope/10 은 거의 hope에만 좌우됨. 
> 실제로는 event + memory 기반이어야 함."*

**새 공식 (Claude Code 구체화):**
```python
sacred_salience = clip(
    a * religious_context
    + b * recent_event_weight(sacred_meal | prayer_invitation | miracle_witnessed)
    + c * primary_figure_presence
    + d * loyalty[primary_figure] / 10
    + e * awe / 10,
    min=0, max=10
)
```

가중치 a-e는 Claude Code가 결정. hope 의존성 명시적으로 제거 (또는 매우 낮은 
가중치만).

### 4.6 recent_event_weight 구현

Layer B 이벤트 중 sacred 관련 이벤트가 최근 발생했을 때의 영향:
- event 발생 시점: 1.0
- 이후 exponential decay (half-life ~5 tick)
- 여러 event 동시 활성화 시 max 또는 sum (Claude Code 결정)

### 4.7 테스트

- `test_pressure_computation.py` 의 8 pressure 테스트 전면 재작성
- 경계값 테스트: 변수 하나가 0이어도 pressure가 0 아님 확인
- sanity check: 모든 입력 최대치일 때 10에 근접

### 4.8 Step 2 완료 조건

- [ ] 8 Pressure 모두 가중합+clip 공식
- [ ] sacred_salience는 hope 의존성 제거됨
- [ ] recent_event_weight 함수 구현
- [ ] Pressure 테스트 전부 green
- [ ] 277 tests green 유지

---

## 5. Step 3 — Availability Gate (2단 구조)

### 5.1 작업

행동 선택을 2단계로 분리. `run_to_tomb` 과 같은 맥락 강한 행동에 gate 적용.

### 5.2 이유

ChatGPT 지적:
> *"run_to_tomb 7회는 availability gating 부재 문제. 정책이 이런 행동을 상시 
> 옵션으로 취급. gate가 강해야 튀지 않음."*

### 5.3 구조

```python
# 기존 (단일 단계)
def select_action(state, world, policy):
    candidates = ALL_ACTIONS  # 21개 전부
    scores = policy.score(state, world, candidates)
    return argmax(scores)

# 신규 (2단 구조)
def select_action(state, world, policy):
    # Step A: Availability gate
    available = [a for a in ALL_ACTIONS if availability_gate(a, state, world)]
    if not available:
        available = DEFAULT_FALLBACK  # e.g., [follow_closely, stay_hiding]
    
    # Step B: Score
    scores = policy.score(state, world, available)
    return argmax(scores)
```

### 5.4 Availability Gate 정의

각 action마다 `available` 조건 정의. Claude Code 자율 결정.

**예시 (Claude Code가 구체화):**

```python
AVAILABILITY = {
    "run_to_tomb": lambda state, world: (
        world.recent_event("resurrection_news") within 3 ticks
        and world.location_reachable("tomb")
    ),
    
    "draw_sword": lambda state, world: (
        world.recent_event("guard_approaches") or 
        world.recent_event("arrest_warrant") within 2 ticks
        and state.anger > 5
    ),
    
    "deny": lambda state, world: (
        world.recent_event("public_accusation") within 1 tick
    ),
    
    "fall_asleep": lambda state, world: (
        state.fatigue > 6
        and world.recent_event("prayer_invitation") within 5 ticks
    ),
    
    "confess": lambda state, world: (
        world.recent_event("forgiveness_offered") within 3 ticks
        or state.guilt[any_target] > 7
    ),
    
    # 일반 행동은 항상 available
    "follow_closely": lambda state, world: True,
    "discuss_with_disciples": lambda state, world: True,
    # ...
}
```

**중요:** 맥락 강한 행동만 gate. 일반 행동은 `True` 유지.

### 5.5 Gate 조건의 엄격도

Claude Code 자율 결정. 원칙:
- Canonical하게 특정 맥락에서만 일어나는 행동 → 엄격한 gate
- 일상적으로 가능한 행동 → 느슨한 gate 또는 no gate

목록 (Claude Code가 분류):
- 엄격: run_to_tomb, draw_sword, deny, confess, jump_into_sea
- 중간: weep, withdraw_in_fear, pray, assert_loyalty
- 느슨: follow_closely, discuss_with_disciples, stay_awake, stay_hiding, 
  follow_at_distance, fall_asleep, flee, accept_washing, resist_washing, 
  watch_quietly, stay_on_boat

### 5.6 Fallback

모든 행동이 gate에서 막힌 경우 fallback. Claude Code 결정:
- 기본 fallback: `[follow_closely, stay_awake, watch_quietly]`
- 또는 상황에 따라 (`state.fatigue` 높으면 `stay_awake` 제외 등)

### 5.7 테스트

- `test_action_selection.py` 신규 또는 확장
- 각 맥락 강한 action에 대해:
  - 조건 만족 시 available 확인
  - 조건 불만족 시 blocked 확인
- Fallback 동작 확인

### 5.8 Step 3 완료 조건

- [ ] 2단 구조 구현
- [ ] 최소 10개 action에 availability gate 정의
- [ ] Fallback 동작
- [ ] 관련 테스트 green
- [ ] 277 + 신규 tests green

---

## 6. Step 4 — Direct Edges 20개 구현 (핵심)

### 6.1 작업

State transition rules 27 direct edges 중 **우선순위 20개를 1차 구현**. 나머지 7개는 후순위.

### 6.2 이유

두 LLM 공통:
- Gemini: *"27 엣지가 MCTS 기본 물리 법칙"*
- ChatGPT: *"이게 먼저. 상태가 장면에 반응해야 함."*

### 6.3 우선순위 5 카테고리 (ChatGPT 권고)

**Category A — 외부 이벤트 → 내부 상태 (가장 중요)**
```
accusation_visibility 증가 → fear +, shame +, confusion +
public_exposure → shame +, fear +
guard_approaches → fear ++, anger +
arrest_warrant → fear ++, confusion +
```

**Category B — 가시적 고통/상실 → 정서**
```
primary_figure_suffering_visible → grief ++, awe +, loyalty[primary_figure] +
peer_failure → grief +, shame[self] +
ally_departure → belonging -, fear +
```

**Category C — 내부 상태 간 전이**
```
guilt[target] high → withdrawal tendency, grief +, doubt +
shame high → withdrawal tendency +, hesitation (없으면 resolve -)
fear high + guilt high → confusion +
```

**Category D — 관계/소속 → 감정**
```
ally_proximity high → belonging +, fear -
group_cohesion high → belonging +, isolation -
primary_figure_presence → awe +, loyalty[primary_figure] 유지
```

**Category E — 신성 이벤트 → 정서**
```
sacred_meal → awe +, peace 관련 (derived)
prayer_invitation → awe +, hope +
miracle_witnessed → awe ++, trust[primary_figure] +, hope +
```

각 카테고리 4 edges × 5 = **20 edges**.

### 6.4 Edge 강도 결정

Claude Code 자율 결정:
- `+` = +0.3~0.5 per event
- `++` = +0.5~1.0 per event
- `-` = -0.3~0.5 per event
- `--` = -0.5~1.0 per event

지속성:
- Event 발생 시 즉시 효과
- 이후 매 tick small decay (자연 감소)

### 6.5 State 상한

모든 state는 [0, 10] 유지. clip 필수.

### 6.6 grief 증가 경로 (특별 주의)

ChatGPT 지적:
> *"grief는 최소 3 경로가 있어야 한다.
> 1) event-induced: loss cue, failure cue, suffering visible
> 2) state-induced: guilt high + helplessness high
> 3) action-induced expression: weep, withdraw, silence"*

위 20 edges 중 Category B와 C에서 grief 증가 경로 3개 이상 확보되는지 확인.

### 6.7 구현 위치

```
engine/person/state_transitions.py  (신규)

class StateTransitionEngine:
    def apply(self, state, events_this_tick, action_last_tick):
        # Category A: event → state
        # Category B: event → state (loss)
        # Category C: state → state
        # Category D: relational
        # Category E: sacred
        ...
```

### 6.8 테스트

- 각 카테고리 sanity test (최소 1개씩)
- 특히 grief 3 경로 테스트
- clip 경계 테스트

### 6.9 Step 4 완료 조건

- [ ] 20 edges 구현
- [ ] grief 최소 3 경로
- [ ] State transition 테스트 green
- [ ] 277 + 신규 tests green
- [ ] **실측 1 seed × 30 tick 재실행**
- [ ] run_to_tomb 발생 횟수 < 3 (availability gate 효과)
- [ ] grief 값이 tick마다 변화 (stuck 해소)

---

## 7. Step 5 — guilt/shame Semantics 문서

### 7.1 작업

`witness_concept_variables_v2.md` 에 guilt/shame semantics 정정.

### 7.2 이유

ChatGPT 지적:
> *"shame[before_whom]은 맞음. guilt[target]은 부분적으로만 맞음. guilt는 
> 'toward_whom' + 'self' 둘 다. 같은 dict 구조면 구현은 편하지만 의미 뭉개짐."*

### 7.3 정정 내용

**문서 수정:**
```yaml
shame:
  structure: target-aware
  target_semantics: "before_whom (수치를 느끼는 상대)"
  default_targets: [crowd, peers, self]
  
guilt:
  structure: target-aware
  target_semantics: "toward_whom + self (누구에게 잘못했는가 + 자기 판단)"
  default_targets: [primary_figure, self]
  note: "'toward' semantics와 'self-judgment' semantics 모두 포함. 
         구현상 dict 구조는 동일하지만 해석 시 target 별 의미가 다름."
```

### 7.4 코드 변경

구조 자체는 유지 (dict[str, float]). **문서와 테스트의 target 의미만 명확히.**

테스트 예:
```python
def test_shame_semantics():
    state.shame["crowd"] = 7  # crowd 앞에서의 수치
    state.shame["self"] = 5   # 자기 앞에서의 수치 (자기 혐오)

def test_guilt_semantics():
    state.guilt["primary_figure"] = 8  # 예수에게 잘못한 죄책감
    state.guilt["self"] = 6            # 자기 판단상의 죄책감
```

### 7.5 Step 5 완료 조건

- [ ] 문서 정정 반영
- [ ] Semantics 테스트 추가
- [ ] 277 + 신규 tests green

---

## 8. Step 6 — 2차 실측 + Rubric 재평가

### 8.1 작업

Step 1-5 완료 후 첫 실측과 동일 조건으로 재측정.

### 8.2 조건

```
content: content/peter/v3/{initial_state,targets,canonical_events}.json
seed: 0
ticks: 30
policy: rule-based (Step 3 availability gate 포함)
```

### 8.3 비교 대상

첫 실측 (`peter_v3_seed0_ticks30.json`) vs 2차 실측.

### 8.4 검증할 것

**동역학 개선:**
- [ ] run_to_tomb 횟수 < 3 (1회가 canonical)
- [ ] grief 값 변화 (stuck 해소)
- [ ] denial이 accusation event 근처에서 발생 (예: tick 17-19)
- [ ] action 분포 다양화

**Rubric 변화:**
- [ ] Canon hard violation 없음 (기존에도 없었음, 유지)
- [ ] Canon soft_drift 감소 (28.5 → ?)
- [ ] Character composite 유지 또는 증가
- [ ] DiscoveryClass 재평가

### 8.5 해석 원칙

**주의:** drift가 줄어도 여전히 noise로 분류될 수 있음. Threshold 자체가 임의값 
(noise_threshold=20.0) 이므로 판정보다는 **절대 drift 변화폭**에 주목.

예:
- 첫 실측 drift 28.5 → 2차 drift 15.0 이면 **동역학 개선 성공** (여전히 noise 
  분류여도)
- 2차 drift 가 18-28.5 수준이면 동역학 부분 개선
- 2차 drift 가 28.5 이상이면 동역학 변경이 효과 없음 (원인 재분석 필요)

### 8.6 산출물

```
docs/person/v3_measurement/peter_v3_seed0_ticks30_v2.json
docs/person/V3_DYNAMICS_COMPARISON.md
```

### 8.7 Step 6 완료 조건

- [ ] 2차 실측 완료
- [ ] 비교 문서 작성
- [ ] **이 시점에서 Lee 검토 대기**

---

## 9. Step 7 — Lee 검토 후 판단

### 9.1 가능한 결과 3가지

**Case A: 동역학 개선 성공**
- drift 크게 감소, run_to_tomb/grief 문제 해소
- 다음: Step 8 (나머지 7 direct edges 추가) 또는 Phase 2 종료 판단

**Case B: 부분 개선**
- drift 중간 정도 감소, 일부 문제만 해소
- 다음: 원인 분석, 추가 edge 또는 gate 보강

**Case C: 개선 없음**
- drift 변화 미미
- 다음: 더 큰 구조적 문제. Lee와 원인 분석.

### 9.2 Lee 개입 지점

**유일한 Lee 필수 개입:** Step 7.

이 시점 이전까지는 Lee 개입 없이 Claude Code가 결정 1-8을 자율 실행.

---

## 10. Step 8 — 나머지 7 Direct Edges (Case A 시)

### 10.1 조건부 진행

Step 7에서 Lee가 *"동역학 1차 성공"* 판정한 경우에만.

### 10.2 작업

나머지 7 edges 추가. Claude Code가 우선순위 자율 결정.

### 10.3 후속 작업 준비

Phase 2 v2 Dynamics 완료 후 가능한 다음 작업 (별도 지시):
- Scene template 도입 검토
- Threshold 보정 (분포 기반)
- Multi-seed ensemble
- BC 재학습 검토

---

## 11. 산출물 구조

```
engine/person/
  state_v3.py                        (수정, faith_stage 제거)
  state_derived.py                   (수정, faith_stage_tag 추가)
  state_transitions.py               (신규, Step 4)

engine/action/
  availability_gate.py               (신규, Step 3)
  action_selector.py                 (수정, 2단 구조)

engine/world/
  pressure.py                        (수정, 가중합+clip)

tests/
  test_person/
    test_state_v3.py                 (수정)
    test_state_transitions.py        (신규)
    test_derived_faith_stage.py      (신규)
  test_action/
    test_availability_gate.py        (신규)
    test_action_selection_2stage.py  (신규)
  test_world/
    test_pressure_computation.py     (수정)

docs/
  witness_concept_variables_v2.md    (수정, guilt/shame semantics)

docs/person/
  v3_measurement/
    peter_v3_seed0_ticks30.json      (기존)
    peter_v3_seed0_ticks30_v2.json   (신규, 2차 실측)
  V3_DYNAMICS_COMPARISON.md          (신규)
  V3_PHASE2_V2_DYNAMICS_COMPLETE.md  (완료 보고)
```

---

## 12. 세션 권장

| Step | 예상 세션 | 비고 |
|---|---|---|
| Step 1 (faith_stage 강등) | 0.5 세션 | 단순 작업 |
| Step 2 (Pressure 공식) | 1 세션 | 8 공식 전환 + sacred 재설계 |
| Step 3 (Availability gate) | 1-2 세션 | 가장 큰 작업 중 하나 |
| Step 4 (Direct edges 20) | 2 세션 | 가장 큰 작업 |
| Step 5 (semantics 문서) | 0.3 세션 | |
| Step 6 (2차 실측) | 0.5 세션 | |

**총 5-6 세션.** Step 7 Lee 검토 후 Step 8 추가.

**Step 1-6은 한 번에 이어서 실행 가능** (Lee 승인 대기 없음).

---

## 13. 금지 사항

- Active 변수 20 → 19 이외의 수 변경 금지 (Lee 승인 없이)
- 새 변수 추가 금지 (hesitation 포함)
- Rubric 구조 변경 금지
- ABSOLUTE RULES #1-18 해석 변경 금지
- Threshold 보정 작업 금지 (후순위)
- Multi-seed 작업 금지 (후순위)
- BC 재학습 작업 금지 (후순위)
- Scene template 도입 금지 (1차 완료 후 판단)

---

## 14. 자율 실행 범위 (확장)

Lee 지시 *"내 승인을 기다리는 작업들이 너무 많아서"* 에 따라 **자율 범위 확장**:

### Claude Code 자율 결정 (Lee 재승인 불필요)

- Step 1-6의 모든 구현 세부
- 공식의 구체 수치 (가중치, threshold, decay)
- Edge 강도 (+0.3 vs +0.5 vs +1.0)
- Availability gate 조건의 구체성
- Gate의 엄격/느슨 분류
- Grief 3 경로의 구체 정의
- Fallback action 선정
- 테스트 케이스 선정

### Lee 개입 필요 (여전히 보고)

1. 277 tests 중 5개 이상이 깨지는데 원인이 구조적
2. Active 변수 수 변경 필요 (20 → 19 외)
3. ABSOLUTE RULES 위반 가능성
4. 결정 1-8과 명백히 충돌하는 상황
5. **Step 7 (2차 실측 Lee 검토)**

### Claude Code 절대 단독 결정 금지

- 새 Phase 진입 (Phase 3 등)
- BC 모델 변경
- Content 파일 수정 (정경 근거 변경)
- 새 ABSOLUTE RULES 추가

---

## 15. 진행 보고 형식

각 Step 완료 후 한 줄 보고:

```
Step 1 ✓ faith_stage → Derived 이동. Active 19. Tests green.
Step 2 ✓ 8 Pressure 가중합+clip. sacred_salience event-based 재계산.
Step 3 ✓ Availability gate 10 actions. Fallback 동작.
Step 4 ✓ 20 edges (5 categories × 4). grief 3 경로 확보.
Step 5 ✓ guilt/shame semantics 문서 정정.
Step 6 ✓ 2차 실측 완료. drift 28.5 → X. run_to_tomb X회. 
         ← Lee 검토 요청.
```

중간에 막히면:
```
[BLOCKED at Step N] 이유: ... 
Lee 판단 필요: (a) ... (b) ...
```

---

## 16. 이 지시의 정신

**Lee가 신뢰를 준 영역:**

> *"전문적인 영역에서 방향을 정하는 건 너가 해줘."*

이 신뢰를 받은 만큼:
- Claude Code는 **주저 없이 결정**
- 막히면 **솔직히 보고**
- 성공하면 **자기 자랑 없이 다음 Step**
- 실패하면 **원인 분석**

**Lee가 신뢰를 거둘 경우:**

결정 1-8 중 *"이건 틀렸다"* 싶으면 Lee가 말함. 그 때만 멈춤.

---

## 17. 한 줄 요약

**"8개 결정을 5-6 세션에 자율 실행. Step 1-6 Lee 승인 대기 없음. 
Step 7 (2차 실측 비교) 시점에만 Lee 검토. 동역학 1차 성공 시 Step 8, 
실패 시 원인 재분석."**

---

## 부록 A — 결정 1-8 원본 (Lee 승인 완료)

Lee 명시 승인 (대화에서): *"좋아. 너가 결정한 대로 진행하자."*

| # | 결정 | Lee 승인 |
|---|---|---|
| 1 | Dynamics first (동역학 채우기 먼저) | ✓ |
| 2 | faith_stage → Derived 강등 | ✓ |
| 3 | Pressure 공식 가중합+clip 전환 | ✓ |
| 4 | Availability gate 2단 구조 | ✓ |
| 5 | Direct edges 20개 우선 구현 | ✓ |
| 6 | Scene template 보류 | ✓ |
| 7 | guilt/shame semantics 분리 | ✓ |
| 8 | Threshold/Multi-seed/BC 후순위 | ✓ |

이 8개는 Claude Code가 재확인 없이 진행.
