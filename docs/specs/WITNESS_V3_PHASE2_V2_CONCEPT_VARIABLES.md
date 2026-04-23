# WITNESS v3.0 — Phase 2 v2: 개념 변수 시스템 (ChatGPT 권고 반영)

**생성 배경:**
WITNESS_V3_PHASE2_CONCEPT_VARIABLES.md (v1) 에 대한 ChatGPT 외부 자문 결과,
**철학 방향은 정확하나 5가지 구조적 미해결 문제**가 지적됨. 이를 전면 반영한 v2.

**ChatGPT 핵심 평가:**
> *"방향 전환은 맞다. 다만 바로 구현 문서로 쓰기 전에 아래 5개를 먼저 고쳐야 한다.
> 1. 외부 변수 3층 분리 (primitive / event / derived pressure)
> 2. 변수 등급 분류 (candidate / active / derived)
> 3. 정경 근거 등급화 (A 직접 / B 강한 추론 / C 해석적)
> 4. 관계 변수 target 구조 명시 (love, loyalty, trust, belonging)
> 5. 행동을 통한 world update 허용 (action → event → external update)"*

> *"철학은 이전보다 훨씬 정확해졌고, 지금부터 필요한 건 '개념 사전'을 
> '실행 가능한 상태공간'으로 압축하는 규칙이다."*

**선행 조건:**
- WITNESS_V3_PHASE2_CONCEPT_VARIABLES.md (v1) — 철학 문서로 보존, 구현 문서로는 폐기
- WITNESS_V3_REDESIGN.md Phase 1 (발견 정의) 완료 또는 진행 중
- 기존 1176+ tests green

**v1 → v2 변경 요약:**
- 외부 변수를 단일 카테고리 → **3층 분리** (Primitive / Event / Pressure)
- 변수를 단순 목록 → **3등급 분류** (Candidate / Active / Derived)
- 정경 근거를 binary → **3등급** (A / B / C)
- 관계 변수 (love, loyalty, trust 등) → **target slot 구조** 명시
- "인물 → 외부 변수 금지" → **"action → event → world update 허용"** 으로 완화

---

## 0. 핵심 원칙 (v1에서 유지 + 강화)

### 0.1 v1 핵심 4원칙 유지

```
1. 변수 = 명명 가능한 개념 그 자체 (잘게 쪼개지 말 것)
2. 맥락은 상호작용으로 발생 (별도 변수 만들지 말 것)
3. 인물 변수 + 외부 변수 둘 다 등록
4. 베드로 생애 정경에서 bottom-up 추출
```

### 0.2 v2 추가 원칙 (ChatGPT 권고)

```
5. 외부 변수는 3층으로 분리 (Primitive / Event / Pressure)
6. 변수는 3등급으로 분류 (Candidate / Active / Derived)
7. 정경 근거는 3등급으로 표시 (Level A / B / C)
8. 관계성 개념은 target-aware 구조 (love[target], loyalty[target] ...)
9. 인물 행동의 세계 폐루프 허용 (action → event → external update)
```

### 0.3 ChatGPT 핵심 한 줄

> *"모든 추출 변수는 ontology 후보일 뿐이며, 실제 시뮬레이션 활성 변수는 
> 별도로 선별한다."*

이 한 줄이 v2의 가장 중요한 추가 원칙. **추출 ≠ 활성화.**

---

## 1. 변수의 3등급 분류 (ChatGPT 권고 #2)

### 1.1 등급 정의

```
Candidate (후보 변수)
    정경에서 추출되었으나 시뮬레이션에 아직 사용 안 함
    Reserve / dormant 상태로 보관
    필요 시 Active로 승격 가능
    예상 수: 50-60개

    ↓ 승격 (engineer 판단 + Lee 승인)

Active (활성 변수)
    실제 시뮬레이션 엔진의 상태로 작동
    AgentState에 필드로 존재
    행동 결정에 직접 영향
    예상 수: 20-30개

    ↑ 도출 (계산식으로 자동 생성)

Derived (도출 변수)
    Active 변수들의 함수로 자동 계산
    독립 상태 아님, 별도 저장 안 함
    예: stress = fear + fatigue + uncertainty
    예상 수: 10-20개
```

### 1.2 승격 기준 (Candidate → Active)

ChatGPT 추가 체크리스트 #4:

> *"이 변수가 바뀌어도 policy output이 거의 안 바뀌면 제거한다."*

승격 4개 조건:
1. 정경에서 명시 또는 명백히 추론 가능 (Level A 또는 B)
2. 다른 Active 변수의 단순 합/차로 표현 불가
3. 행동 결정에 영향
4. **시뮬레이션 감도 (sensitivity) 가 있음** — 이 변수 변경 시 policy output 변화

**4 조건 모두 만족해야 Active 승격.** 셋만 만족하면 Candidate에 보류.

### 1.3 v1과의 차이

v1: 추출 즉시 모두 변수로 등록 → 50-60개 변수 모두 활성
v2: 추출은 50-60개 가능, **활성은 20-30개로 제한**, 나머지는 reserve

이 차이는 결정적. v1대로 가면 *"개념 사전"* 이 *"엔진 상태"* 와 섞여서 폭발.

---

## 2. 외부 변수의 3층 분리 (ChatGPT 권고 #1)

### 2.1 ChatGPT 지적 (v1의 문제)

v1의 외부 변수 후보:
```
crowd_density, public_visibility, accusation, sacred_presence, 
social_threat, authority_presence
```

ChatGPT 지적: *"이건 사실 한 층이 아니다. 서로 성격이 다르다."*

### 2.2 v2의 3층 구조

```
Layer A: World Primitives (지속 상태)
    crowd_density, roman_presence, authority_presence, group_cohesion,
    time_of_day, location, group_presence, ...
    → 환경의 기본 입력값. 시뮬레이션 외부에서 주어짐.

Layer B: Events (짧은 사건)
    accusation, eye_contact, betrayal_witnessed, prayer_invitation,
    miracle_witnessed, ally_arrival, ally_departure, ...
    → 특정 시점에 발생. 짧은 수명. World Primitive를 갱신할 수 있음.

Layer C: Derived Pressures (계산되는 압력)
    social_threat, shame_exposure, urgency, isolation_pressure, 
    loyalty_pull, sacred_salience, uncertainty, physical_threat, ...
    → A + B로부터 자동 계산. 별도 입력 아님.
    → 인물 변수에 작용하는 매개체.
```

### 2.3 계산 예시

```
social_threat = crowd_density × accusation_visibility × authority_presence

shame_exposure = public_visibility × prior_failure_salience 
                + (recent_event: accusation) × 1.5

isolation_pressure = (1 - group_cohesion) × (1 - ally_proximity)
```

### 2.4 v1 결정 사항 갱신

v1 §6 Pressure Layer 처리 옵션 A/B/C 중:

**옵션 C (Pressure는 외부 변수 조합으로 자동 도출) 가 최종 채택.**

이건 Pressure가 **Derived 등급**으로 분류된다는 뜻. 별도 저장하지 않고 매 tick
계산. ChatGPT가 명시적으로 권장:

> *"Pressure는 별도 '정의된 기본 변수'가 아니라, 외부 primitive들로부터 계산되는 
> derived layer로 두는 게 맞다."*

### 2.5 작업 시 분류 작업

추출된 외부 개념을 등록할 때 **반드시 어느 Layer 인지 명시**:

```yaml
crowd_density:
  layer: A (Primitive)
  type: world_state
  
public_accusation:
  layer: B (Event)
  type: social_event
  duration: 1 tick
  
shame_exposure:
  layer: C (Derived)
  computed_from: [public_visibility, prior_failure_salience, recent_accusation]
  formula: "see witness_pressure_calculations.md"
```

---

## 3. 정경 근거 3등급 (ChatGPT 권고 #3)

### 3.1 ChatGPT 지적

v1의 *"본문에서 직접 명시 또는 명백히 추론"* 기준이 모호.
*"명백히"* 라는 단어가 신학 해석과 심리 소설화를 섞을 위험.

### 3.2 v2의 3등급 분류

```
Level A: 본문 직접 명시
    정경 본문에 해당 단어 또는 명시적 표현 존재
    예: "두려워하여" → fear
        "사랑하여" → love
        "통곡하니라" → grief
    → Active 승격 우선 후보

Level B: 행동/맥락상 강한 추론
    행동의 패턴이나 사건 직후 반응에서 강하게 추론 가능
    심리 해석은 최소
    예: 부인 후 "심히 통곡" → guilt + shame 강한 추론
        체포 직전 도망 → fear 강한 추론
    → Active 승격 가능, 신중 검토

Level C: 신학적/서사적 해석 필요
    정경 본문 + 신학적 전통 + 문학적 해석이 필요
    개인 해석이 갈릴 수 있음
    예: forgiveness_perception (디베랴 호숫가 후)
        identity_restoration (3회 사랑 고백 후)
    → Reserve 보관, 필요 시 Lee 승인 후 Active
```

### 3.3 활성화 우선순위

**Active 승격 시 우선순위:**
- Level A: 자유롭게 Active
- Level B: 다른 조건 (§1.2의 4조건) 모두 통과 시 Active
- Level C: 기본적으로 Reserve 상태 유지. Lee 명시적 승인만 Active.

ChatGPT 권고:
> *"active state에 들어가는 변수는 우선 A/B 위주로 시작. C는 reserve candidate로 
> 두는 게 안전하다."*

### 3.4 등급 표기 예시

```yaml
fear:
  evidence_level: A
  scripture_basis:
    - reference: "마태복음 14:30"
      level: A
      text: "두려워 빠져 들어가게 되었을 때"
    - reference: "마가복음 14:50"
      level: B
      text: "다 예수를 버리고 도망하니라"  # 도망 → fear 강한 추론

forgiveness_perception:
  evidence_level: C
  scripture_basis:
    - reference: "요한복음 21:15-17"
      level: C
      text: "세 번 사랑 고백 장면"
      interpretation_note: "신학적 회복 모티프, 베드로 내면은 명시 안 됨"
  status: reserve  # Active 아님
```

---

## 4. 관계 변수 Target 구조 (ChatGPT 권고 #4)

### 4.1 ChatGPT 지적

v1은 *"loyalty_to_jesus 같은 인물+target 결합 변수 금지, loyalty 일반 + 
인스턴스화"* 라고 했지만 **구체 구현 방법이 모호.**

ChatGPT 권고:
> *"일부 변수는 단일 scalar가 아니라 relation slot를 가져야 한다."*

### 4.2 v2 분류: Scalar vs Target-aware

**Scalar 변수 (target 없음)**
```
fear, fatigue, hunger, confusion, vitality, pain, 
hope, joy, sadness, anger, awe, peace, ...
```

이런 건 *"누구를"* 이 무의미한 내적 상태. 단일 float 값.

**Target-aware 변수 (target slot 필수)**
```
love[target]
loyalty[target]
trust[target]
belonging[group]
isolation[from_group]
guilt[wronged_party]    # 누구를 배신/실망시킨 것에 대한 죄책감
shame[before_whom]       # 누구 앞에서의 수치
attachment[target]
```

### 4.3 구현 방식

```python
# Scalar
state.fear = 0.7

# Target-aware
state.love = {
    "jesus": 0.9,
    "andrew": 0.8,      # 형제
    "wife": 0.7,
    "disciples_general": 0.6
}

state.guilt = {
    "jesus": 0.8,        # 부인 후
    "self": 0.6
}

state.belonging = {
    "twelve_disciples": 0.9,
    "jewish_community": 0.5
}
```

### 4.4 베드로 시나리오에서의 target 목록

```
인물 target:
  jesus, andrew (형제), wife, mother_in_law,
  john, james, judas (이전), thomas, ...
  caiaphas, pilate (적대자),
  
그룹 target:
  twelve_disciples, broader_followers, jewish_community,
  roman_authority, jerusalem_citizens, ...
```

### 4.5 작업 시 표기

추출 시 변수가 target-aware 인지 명시:

```yaml
love:
  type: person_concept
  category: emotion
  structure: target-aware
  default_targets: [jesus, peers, family]
  evidence_level: A
  
fatigue:
  type: person_concept
  category: physical
  structure: scalar
  evidence_level: A
```

---

## 5. 행동 → 세계 폐루프 (ChatGPT 권고 #5)

### 5.1 ChatGPT 지적 (v1 §3.3 수정)

v1: *"인물 변수 → 외부 변수: 금지"*

ChatGPT: *"이 원칙을 강하게 고정하면 세계가 죽는다. 시뮬레이션에서 중요한 건 
상호작용의 폐루프이다."*

### 5.2 v2 수정 원칙

**금지:** `person_state → external_state` 직접 연결
- 베드로의 fear 값이 직접 crowd_density를 바꾸는 건 금지
- 텔레파시처럼 인물 변수가 세계를 갱신하는 건 금지

**허용:** `action → event → external update`
- 베드로가 "큰 소리로 부인" 행동 → "public_outburst" 이벤트 발생 → 
  crowd_attention 증가
- 베드로가 "물러남" 행동 → "withdrawal" 이벤트 → isolation 증가
- 베드로가 "고백" 행동 → "public_declaration" 이벤트 → authority_attention 증가

### 5.3 데이터 흐름

```
Person State (변수)
       ↓
   [decision]
       ↓
Person Action
       ↓
   [action → event 매핑]
       ↓
World Event (Layer B)
       ↓
   [event → primitive update]
       ↓
World Primitives (Layer A) 갱신
       ↓
   [next tick]
       ↓
Pressure 재계산 → 다음 Person decision
```

### 5.4 새 산출물 필요

```
docs/witness_action_to_event_mapping.md
```

베드로의 가능한 행동 목록 (기존 BC 모델 학습 데이터에서 추출 가능: 
follow_closely, deny, weep, pray, withdraw_in_fear, ...) 각각이 어떤 이벤트를
유발하는지 매핑.

```yaml
deny:
  triggers_event: public_denial
  event_effects:
    - target: crowd_attention
      delta: +0.3
    - target: ally_proximity
      delta: -0.2
    
weep:
  triggers_event: visible_distress
  event_effects:
    - target: ally_attention
      delta: +0.4
    - target: public_visibility
      delta: -0.1   # 숨어서 우는 경우
```

---

## 6. 상호작용 그래프 — v1 수정 (ChatGPT 권고)

### 6.1 v1의 "최대 3개" 규칙 완화

ChatGPT 지적:
> *"각 변수 최대 3개"는 너무 기계적. 연결 유형별 제한이 더 정확하다."*

### 6.2 v2 새 규칙

**Strong direct edges:** 변수당 2-4개 (상한 5)
- 실제로 강한 직접 인과 관계
- 부호 (+/-) 와 강도 (weak/medium/strong) 명시

**Mediated connections:** 제한 없음
- Pressure 또는 latent mediator를 통한 간접 연결
- 직접 edge가 아니라 계산식으로 표현

### 6.3 예시

```
직접 연결 (Strong):
  fear → hesitation (strong, +)
  fear → confusion (medium, +)
  fear → hope (medium, -)
  fear → resolve (medium, -)

매개 연결 (Mediated):
  public_accusation → shame_exposure → shame → hesitation
                     (Layer B → Layer C → Person → Person)
  
  여기서 public_accusation은 fear와 직접 연결 안 함.
  shame_exposure (Pressure) 가 매개.
```

### 6.4 표기 방식

```yaml
fear:
  direct_edges:
    - target: hesitation
      sign: positive
      strength: strong
    - target: confusion
      sign: positive
      strength: medium
    - target: hope
      sign: negative
      strength: medium
    - target: resolve
      sign: negative
      strength: medium
```

---

## 7. 산출물 구조 (v1에서 갱신)

```
docs/
  witness_concept_variables_v2.md       (이 문서의 핵심 산출)
    Section 1: Person Variables (인물 변수, target-aware 구조 포함)
    Section 2: External Variables Layer A (Primitives)
    Section 3: External Variables Layer B (Events)
    Section 4: External Variables Layer C (Derived Pressures)
    Section 5: 각 변수의 정경 근거 + Level (A/B/C)
    Section 6: Active / Candidate / Derived 분류
  
  witness_pressure_calculations.md      (v2 신규)
    Layer C 압력의 계산식
    예: social_threat = crowd_density × accusation_visibility × ...
  
  witness_action_to_event_mapping.md    (v2 신규)
    행동 → 이벤트 → 외부 변수 갱신 매핑
  
  witness_concept_interactions.md       (v1에서 갱신)
    Strong direct edges + Mediated paths 분리

engine/
  person/
    state_v3.py                         (Active 변수만, target-aware 포함)
    state_candidates.py                 (Candidate 변수 보관)
    state_derived.py                    (Derived 변수 계산 함수)
    
  world/
    primitives.py                       (Layer A)
    events.py                           (Layer B)  
    pressure.py                         (Layer C 계산)
  
  action/
    action_event_mapper.py              (행동 → 이벤트 변환)

tests/
  test_person/
    test_state_v3.py
    test_target_aware_variables.py
  test_world/
    test_3layer_separation.py
    test_pressure_computation.py
  test_action/
    test_action_to_event_loop.py
```

---

## 8. 16 → 신규 마이그레이션 (v1에서 갱신)

### 8.1 ChatGPT 권고 적용

v1의 매핑은 *"방향만 있고 기준이 부족"* 했음. v2는 명확한 분류로 처리.

### 8.2 마이그레이션 분류

**유지 (Active 등급, Level A, Scalar)**
```
fear, hope, love (target-aware로 변환), grief, confusion,
fatigue, hunger, health (vitality로 명칭 변경 검토)
```

**재정의 필요 (분해 또는 재명명)**
```
moral_injury → 분해: shame[target] + guilt[wronged_party]
identity_shift → 재정의: doubt + confusion 조합으로 충분한지 검토
event_trauma → trauma 단일 변수로 유지 검토
trust_scar → trust[target] 의 음수 상태로 처리
```

**거의 폐기 후보 (Candidate 또는 Reserve)**
```
fear_layers — Lee 의도 어긋남, 폐기
obedience_maturity — "일상 명명 가능 개념" 기준 미달, 폐기
communal_role — 외부 변수 (group_role) 로 이동 검토
```

### 8.3 마이그레이션 작업 원칙

ChatGPT 핵심 지적:
> *"마이그레이션은 단순 rename이 아니라 관찰 가능한 개념으로의 환원 원칙이 
> 더 분명해야 한다."*

각 기존 변수마다 **이 변수가 일상적으로 명명 가능한 개념인가?** 질문.
- Yes → 신규 변수로 매핑
- No → 분해하거나 폐기

---

## 9. 작업 순서 (v1에서 갱신)

### Step A — 정경 정독 + 개념 추출 (v1과 동일)

베드로 등장 모든 장면 정독, 추출.

**산출:** Raw 추출 목록

### Step B — 개념 정규화 + Layer 분류

v2 추가 작업: 외부 변수를 Layer A/B/C로 분류.

**산출:** `witness_concept_variables_v2.md` v0.1

### Step C — 정경 근거 + Level 등급화

각 변수에 Level A/B/C 부여. **C 등급은 자동 Reserve.**

**산출:** v0.2 (근거 + 등급)

### Step D — Active / Candidate / Derived 분류

§1.2 4조건 적용. Active 20-30개 선정. 나머지 Candidate.
Pressure는 자동 Derived.

**산출:** v0.3 (등급 분류)

### Step E — Target-aware 구조 결정

§4 분류. 각 Active 변수가 scalar인지 target-aware인지 결정.

**산출:** v0.4 (구조 명시)

### Step F — 상호작용 그래프

Strong direct edges + Mediated paths 분리.

**산출:** `witness_concept_interactions.md`

### Step G — Pressure 계산식 작성

Layer C 변수들의 계산식 정의.

**산출:** `witness_pressure_calculations.md`

### Step H — Action → Event 매핑

행동 → 이벤트 → 외부 변수 갱신 매핑.

**산출:** `witness_action_to_event_mapping.md`

### Step I — 16 → 신규 마이그레이션

§8 분류 적용한 매핑 테이블.

**산출:** `witness_migration_v3.md`

### Step J — 코드 구현

state_v3.py + state_candidates.py + state_derived.py + 
3 layer world + action_event_mapper

**산출:** 코드 + tests

### Step K — Lee 검토

각 Step 완료 후 Lee 확인. 핵심 분기점:
- Step C 후 (정경 근거 + Level)
- Step D 후 (Active 선정)
- Step I 후 (마이그레이션 확정)

---

## 10. ABSOLUTE RULES 갱신

### 10.1 기존 Rule #1-14 유지

WITNESS_V3_REDESIGN.md의 Rule #12-14 모두 유지.

### 10.2 Rule #12 해석 갱신 (ChatGPT 권고 #5)

기존 Rule #12: *"월드 레이어는 행동 결정 금지."*

**해석 명확화:**
- 월드는 **압력만 생성**, 행동 결정 금지 (그대로)
- 단, **인물 행동의 결과로 월드가 갱신되는 것은 허용**
- `person_state → external_state` 직접 연결만 금지
- `action → event → external update` 는 정상 폐루프

### 10.3 Rule #15 신설

> **변수는 3등급으로 분류한다 (Candidate / Active / Derived).**
> 
> 추출된 모든 변수가 시뮬레이션에 활성화되는 것이 아니다. Active 등급은
> §1.2 4조건을 모두 만족해야 하며, 활성 변수 수는 20-30개로 제한한다.
> Candidate는 reserve로 보관, Derived는 Active 변수의 계산식.

### 10.4 Rule #16 신설

> **외부 변수는 3 Layer로 분리한다 (Primitive / Event / Derived Pressure).**
> 
> Primitive는 환경 입력값, Event는 짧은 사건, Pressure는 둘로부터 계산되는
> 도출값이다. 같은 등급에 섞어서 등록 금지.

### 10.5 Rule #17 신설

> **정경 근거는 Level A/B/C로 등급화한다.**
> 
> Level A (본문 직접 명시) 와 Level B (강한 추론) 만 Active 승격 가능.
> Level C (해석적) 는 Lee 명시적 승인 시에만 Active.

### 10.6 Rule #18 신설

> **관계성 개념은 target-aware 구조로 구현한다.**
> 
> love, loyalty, trust, belonging, guilt[wronged_party], shame[before_whom] 
> 등은 단일 scalar가 아니라 dict[target, value] 구조로 저장.

---

## 11. 자율 vs 보고 구분 (v1에서 갱신)

### Claude Code 자율 결정 영역

- 변수 명칭 후보
- 정경 정독 순서
- 코드 구현 세부 (dict 구조, validator 로직)
- Mediated path 설계

### Lee 판단 필수 영역

1. **Active 승격 최종 승인** (각 변수)
2. **Candidate vs Active 경계** (애매한 경우)
3. **Level B vs C 경계** (해석 정도)
4. **Target 목록 결정** (관계 변수의 target 후보들)
5. **Direct edge vs Mediated 결정** (어느 게 직접인가)
6. **Pressure 계산식 검증** (수식이 합리적인가)
7. **Action → Event 매핑 검증** (행동의 결과가 합리적인가)
8. **마이그레이션 폐기 변수** (기존 16에서 무엇을 버릴지)

### Claude Code 절대 단독 결정 금지

- Level C 변수의 Active 승격
- 정경 본문 수정 (Rule #2)
- ABSOLUTE RULES #12-18 해석 변경
- Active 변수 30개 초과 시 추가 (Lee 승인 필수)

---

## 12. 금지 사항 (v1에서 갱신)

- 잘게 쪼개기 금지 (`fear_death`, `fear_pain`)
- 추상 동기화 금지 (`avoidance_motivation`)
- 인물 특화 변수 금지 (`loyalty_to_jesus`)
- 정경 근거 없는 변수 금지
- 같은 등급에 다른 Layer 섞기 금지 (Layer A/B/C 혼동)
- Active 30개 초과 자동 진행 금지
- Level C 자동 Active 승격 금지
- `person_state → external_state` 직접 연결 금지 (Rule #12)
- 단일 scalar로 관계 변수 모델링 금지 (Rule #18)
- Phase 3 Pressure / Phase 4 Rubric 작업 동시 진행 금지
- 신경망 학습 작업 금지

---

## 13. 세션 권장

| Step | 예상 세션 | 비고 |
|---|---|---|
| Step A (정경 정독) | 2-3 세션 | 가장 큰 작업 |
| Step B (Layer 분류) | 1 세션 | A/B/C 분리 |
| Step C (Level 등급화) | 1-2 세션 | 신학적 신중함 |
| Step D (Active 선정) | 1 세션 | Lee 검토 핵심 |
| Step E (Target 구조) | 0.5 세션 | 관계 변수만 |
| Step F (상호작용 그래프) | 1 세션 | |
| Step G (Pressure 계산식) | 1 세션 | |
| Step H (Action → Event) | 1 세션 | |
| Step I (마이그레이션) | 1 세션 | Lee 승인 핵심 |
| Step J (코드 구현) | 2-3 세션 | |

**총 11-15 세션.** 각 Step 완료 후 Lee 확인.

---

## 14. v1과 v2의 차이 정리표

| 항목 | v1 | v2 |
|---|---|---|
| 외부 변수 구조 | 단일 카테고리 | 3 Layer (Primitive/Event/Pressure) |
| 변수 등급 | 없음 (모두 활성) | 3등급 (Candidate/Active/Derived) |
| 변수 수 가이드 | 35-65 모두 활성 | 50-60 추출, 20-30 활성 |
| 정경 근거 | binary (있음/없음) | 3등급 (Level A/B/C) |
| 관계 변수 | "loyalty + 인스턴스" 모호 | target-aware dict 구조 명시 |
| 인물→세계 영향 | 금지 | action → event 폐루프 허용 |
| 상호작용 제한 | 변수당 최대 3 | 변수당 2-4 strong + 매개 연결 무제한 |
| Pressure 처리 | 옵션 결정 안 함 | 옵션 C 확정 (Derived 등급) |
| Phase 3 관계 | 모호 | Pressure 계산이 Phase 2의 일부로 통합 |

---

## 15. ChatGPT가 강조한 원리들 (재확인)

```
"모든 추출 변수는 ontology 후보일 뿐이며, 실제 시뮬레이션 활성 변수는 
 별도로 선별한다."

"개념 사전을 실행 가능한 상태공간으로 압축하는 규칙이 핵심이다."

"외부 변수에 primitive / event / pressure가 섞여 있다."

"관계 변수는 target-aware 구조가 필요하다."

"인물→세계 폐루프를 너무 막아놨다."

"명백한 추론 기준이 아직 약하다."

"ontology와 runtime state를 분리하지 않았다."
```

이 7개 문장이 v2의 뼈대.

---

## 16. Claude Code에게 — 함정 경고 (v1 + v2 추가)

v1 6 함정 유지 + v2 추가:

### 함정 7 — 추출과 활성화를 혼동
"50개 추출했으니 50개 다 코드에 넣자" 함정. 추출 ≠ Active.
**Active 20-30 제한 엄수.** 나머지는 Candidate에 보관.

### 함정 8 — Layer 분류 게으름
모든 외부 변수를 단일 카테고리에 박지 말 것.
**3 Layer (Primitive/Event/Pressure) 분류 필수.**

### 함정 9 — Level B와 C 경계 회피
"애매하면 그냥 B로" 하지 말 것.
**Level C는 Reserve로 가는 게 안전.**

### 함정 10 — Target slot 누락
love, loyalty 같은 거 단일 float로 만들지 말 것.
**dict[target, value] 강제.**

### 함정 11 — Pressure 별도 등록
Pressure를 Active 변수로 등록하지 말 것.
**Derived 등급, 계산식만 정의.**

---

## 17. 한 줄 요약

**"개념을 추출하되 활성화는 신중하게. 외부 변수는 Layer로 분리하고, 
정경 근거는 Level로 등급화하고, 관계는 target으로 구체화하고, 
인물의 행동은 세계를 갱신할 수 있게 하라. 추출 ≠ 활성화."**

---

## 부록 A — Lee가 결정해야 할 것들 (정리)

이 v2 지시사항이 Claude Code에게 전달되기 전에 Lee가 미리 답하면 좋은 것:

**결정 1 — Active 변수 상한**
- (a) 20개 (보수적)
- (b) 25개 (중간)
- (c) 30개 (느슨)
- (d) 30 초과 시마다 Lee 승인

**결정 2 — Level C 처리**
- (a) 자동 Reserve, Lee 승인 시에만 Active
- (b) 신학적으로 명백한 것은 자동 Active
- (c) 모두 Reserve, 추후 일괄 검토

**결정 3 — Target 목록 범위**
- (a) 베드로 가까운 인물 5-10명 + 그룹 5개
- (b) 정경 등장 모든 인물 + 그룹
- (c) Lee가 직접 정의

**결정 4 — Action 목록 출처**
- (a) 기존 BC 모델의 15 actions 그대로 사용
- (b) 정경에서 새로 추출
- (c) 둘 다 비교 후 통합

이 4개 답하시면 Claude Code 작업 시작 시 혼란 줄어듭니다.
