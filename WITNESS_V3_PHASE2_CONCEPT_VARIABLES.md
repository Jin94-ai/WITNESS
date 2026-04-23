# WITNESS v3.0 — Phase 2 재설계: 개념 변수 시스템

**생성 배경:**
WITNESS_V3_REDESIGN.md Phase 2 (24 변수 재설계) 결과물이 Lee 의도와 어긋남.
Claude Code가 *"원자 변수 = 잘게 쪼갬"* 으로 해석하여 `fear → fear_death/fear_pain/
fear_isolation/fear_identity_loss` 식으로 분해. Lee의 진짜 의도는 정반대.

**Lee 정정:**
> *"fear라면 공포 그 자체잖아. fear 자체가 개념적이라는 거지. 이제 이 fear가 
> 상황에 따라서 조금씩 바뀌는 거고. 그래서 상황에 따라 다른 변수들과 섞여서 
> 다른 의미가 될 수 있지만 fear, love 등등 이렇게 개념 자체가 변수가 되어야 한다."*

> *"인물과 관련된 개념이 있고, 변화를 촉발할 다양한 개념들이 있을 거야.
> 이런 것들을 가능하면 다 변수로 지정하고 싶은데, 일단은 베드로의 생애에 
> 관련된 것들로 집중해보자."*

**선행 조건:**
- WITNESS_V3_REDESIGN.md Phase 1 (발견 정의 문서) 완료 또는 진행 중
- 기존 1176+ tests green
- 24 변수 작업물 (Phase 2 첫 시도) 존재 — 이 지시로 폐기 대체

**폐기:**
- Phase 2 첫 시도의 24 변수 (`witness_core_variables_v2.md`) 전면 폐기
- 16 → 24 migration 계수 13개 폐기
- 24 변수 간 20 edges 폐기
- 8 범주 체계 (Threat / Attachment / Conviction / ...) 폐기

**보존 / 진행 계속:**
- Phase 1 발견 정의 문서 (Rule #13)
- Phase 3 Pressure Field 월드 설계 (영향 일부 있음, §6 참조)
- Phase 4 Rubric 평가 시스템

---

## 0. 핵심 원칙 (반드시 먼저 읽을 것)

### 0.1 변수 = 명명 가능한 개념 그 자체

```
✅ 좋은 변수: fear, love, hope, fatigue, hunger
❌ 나쁜 변수: fear_death, fear_pain, fear_isolation
              (fear의 "맥락별 표현"이지 별도 변수 아님)
```

**원칙:** 일상적으로 명명되는 인간 경험의 단위가 변수.
잘게 쪼개지 말 것. 추상적 동기로 거슬러 올라가지도 말 것.

### 0.2 맥락은 상호작용으로 발생

`fear` 가 단일 변수라도 다양한 행동으로 표현 가능:

```
fear × roman_presence(높음)         → "죽음 공포처럼" 행동
fear × public_visibility(높음)      → "사회적 공포처럼" 행동
fear × isolation_pressure(높음)     → "고립 공포처럼" 행동
fear × identity_threat(높음)        → "정체성 공포처럼" 행동
```

**같은 fear 변수, 다른 상황 변수 → 자동으로 다른 의미 발생.**

별도 변수 만들 필요 없음. 이건 ChatGPT가 말한 *"세계는 압력만 만들고 인물이 
해석한다"* 의 정확한 구현.

### 0.3 두 종류의 개념 변수

Lee 정의:

**A. 인물 관련 개념 (인물 내부 상태)**
- 감정: fear, love, hope, joy, anger, sadness, grief, ...
- 신체: fatigue, hunger, pain, vitality, ...
- 인지: confusion, certainty, awareness, doubt, ...
- 의지: determination, hesitation, resolve, ...
- 관계 감각: belonging, isolation, intimacy, ...

**B. 변화 촉발 개념 (인물 외부에서 작용)**
- 환경: crowd_density, public_visibility, time_pressure, ...
- 사건: accusation, eye_contact, betrayal_witnessed, ...
- 사회: social_threat, group_cohesion, authority_presence, ...
- 신성: sacred_presence, sacred_call, ...

**둘 다 변수로 명시.** 인물 변수 ↔ 외부 변수 상호작용에서 행동 발생.

### 0.4 베드로 생애로 집중

이번 작업은 **베드로 생애에 등장하는 개념들로 한정.**

> Lee: *"가능하면 다 변수로 지정하고 싶은데, 일단은 베드로의 생애에 관련된 
> 것들로 집중해보자."*

확장 가능한 구조로 설계하되, 첫 구현은 베드로 범위. 빌라도, 막달라 마리아 등
다른 인물은 후속 작업.

---

## 1. 변수 선정 작업 — 두 단계

### Step 1 — 베드로 생애 정경 정독 + 개념 추출

**작업:**
정경에서 베드로가 등장하는 모든 장면을 정독하고, 다음 둘을 추출:

**A. 베드로 내부에 일어난 개념** (인물 변수 후보)
- 본문에서 직접 명명된 것: "두려워하여" → fear, "사랑하여" → love
- 행동에서 명백히 추론되는 것: 부인 → shame, guilt
- 정경 내러티브가 함의하는 것: 회복 장면 → forgiveness_perception

**B. 베드로에게 작용한 외부 개념** (외부 변수 후보)
- 사건: "여종이 바라보고 말하되" → accusation, public_exposure
- 환경: "불을 쬐고 있더니" → physical_setting, group_presence
- 사회: "무리가" → crowd_presence, social_pressure

### Step 2 — 중복 제거 + 명명 정규화

추출된 개념 중:
- 같은 의미 다른 표현 → 단일 명칭으로 통일
- 너무 협소한 표현 (특정 사건에만 쓰임) → 범용 개념으로 일반화
- 개념이 분명하지 않은 것 → 보류 또는 제거

**작업 산출물:**

```
docs/witness_concept_variables.md
```

내용:
- A 인물 변수 목록 (각 변수: 명칭, 정의, 정경 근거 장면)
- B 외부 변수 목록 (각 변수: 명칭, 정의, 정경 근거 장면)
- 추출 과정 메모 (어떤 장면에서 어떤 개념을 추출했는가)

---

## 2. 변수 수의 가이드

### 2.1 인물 변수 (A 목록)

**예상 범위: 15-25개**

기존 5개 (fear, hope, grief, confusion, love)에서 출발해 정경 정독으로 자연
추가될 만한 것들:
- 가능 추가: shame, guilt, joy, anger, doubt, peace, longing, awe, 
  fatigue, hunger, vitality, determination, hesitation, isolation, 
  belonging, ...

**상한 없음. Lee 의도대로 *"가능한 한 다"* 추가.** 단, 아래 조건:

**변수 추가 체크리스트 (각 변수마다):**
1. 정경 본문에서 명시적으로 등장하거나 명백히 추론되는가?
2. 다른 변수들의 단순 합/차로 표현 불가능한가?
3. 베드로의 행동 결정에 영향을 미치는가?

**셋 다 yes여야 변수 추가.**

### 2.2 외부 변수 (B 목록)

**예상 범위: 20-40개**

베드로 생애의 외부 자극이 더 다양함. 정경에 등장하는 사건/환경/사회 요소를
모두 변수화.

**여기는 제한 더 느슨. *"가능한 한 다"* 의 의미가 강함.**

다만:
- 너무 일회성인 것 (특정 한 장면에만 등장) → 일반화 가능한지 검토
- 시뮬레이션 시각에서 의미 있는 단위인가?

### 2.3 합산: 35-65 변수

이 범위가 ChatGPT의 *"24 권장"* 보다 큼. 의도적.

**왜 ChatGPT 권장보다 많아도 OK인가:**
- ChatGPT 권장 24개는 *"분자 변수 24개"* (각 변수가 여러 의미 묶음) 가정
- Lee 방식은 *"개념 자체 변수"* 라 의미 명확
- 의미 명확한 변수 50개가 의미 모호한 변수 24개보다 학습에 좋을 수 있음
- 단, 상호작용은 여전히 희소해야 함 (§3)

---

## 3. 상호작용 그래프 — 희소 유지

ChatGPT 권고 유지:

> *"각 변수는 최대 3개만 직접 연결. 완전 연결망이 아니라 sparse causal graph로."*

### 3.1 인물 변수 ↔ 인물 변수

**최대 3 + 3 = 6개 직접 연결.**

예:
```
fear → shame (양), hope (음), determination (음)
shame ← fear (양), public_visibility (양), prior_failure (양)
```

각 연결마다 **부호(+/-) 명시.** 가중치는 일단 1.0 통일 (나중에 보정).

### 3.2 외부 변수 → 인물 변수

각 외부 변수가 영향 미치는 인물 변수도 **최대 3개.**

예:
```
public_accusation → fear (+), shame (+), confusion (+)
sacred_presence → awe (+), peace (+), determination (+)
ally_nearby → isolation (-), belonging (+), fear (-)
```

### 3.3 인물 변수 → 외부 변수: 금지

인물이 외부 환경을 바꾸는 직접 영향은 모델링하지 않음 (적어도 이번에는).
이건 Rule #12 (월드는 행동 결정 금지)의 역방향: 인물도 월드 직접 결정 안 함.

베드로의 행동이 다른 사람의 행동을 통해 환경을 바꾸는 건 행동 → 사건 → 외부 변수
간접 경로로만.

### 3.4 상호작용 수 상한

대략적 가이드:
- 인물 변수 20개 × 평균 4 connection = 80 edges
- 외부 변수 30개 × 평균 2 connection (인물 영향) = 60 edges
- 합 140 edges 정도

**완전 연결 (50 + 30) × (50 + 30) / 2 = 3,200 대비 4.4%.** 충분히 희소.

---

## 4. 정경 근거 작업 (가장 중요)

각 변수마다 **정경 근거** 명시 필수.

```yaml
fear:
  type: person_concept
  category: emotion
  definition: "위협 인지 시의 회피 정서"
  scripture_basis:
    - "마태복음 14:30 (베드로가 풍랑을 보고 두려워하여 빠져 들어가게 되었을 때)"
    - "마가복음 14:50 (제자들이 다 예수를 버리고 도망하니라)"
    - "누가복음 22:54-62 (부인 장면 전반)"
  
public_accusation:
  type: external_concept
  category: social_event
  definition: "공개적으로 정체나 행위가 지목됨"
  scripture_basis:
    - "마태복음 26:69-72 (대제사장의 집 뜰 사건)"
    - "마가복음 14:66-72 (동일 장면)"
```

**근거 없는 변수 추가 금지.** ABSOLUTE RULE #2 (정경 재작성 금지) 의 정신을 
변수 설계로 확장: *"정경에 근거 없는 베드로 모델링 금지"*.

---

## 5. 명명 규칙

**원칙: 단순, 일상적, 영어 단어 하나로.**

```
✅ fear, love, hope, shame, fatigue
✅ accusation, isolation, sacred_presence (필요 시 두 단어)

❌ fear_death (잘게 쪼갬)
❌ avoidance_motivation (학술 추상화)
❌ peter_specific_loyalty_to_jesus (인물 종속 + 길음)
```

베드로 특화 변수는 만들지 않음. 만약 *"예수에 대한 충성"* 을 모델링하고 싶다면:
- 변수: `loyalty` (일반 개념)
- 베드로 인스턴스에서 활성화: loyalty.target = jesus, loyalty.intensity = 0.8
- 다른 인물은 다른 target 가능

이게 미래 다른 인물 확장 시 필수 구조. (단, 이번 구현은 베드로만 작동하면 OK.)

---

## 6. Phase 3 (Pressure Field) 와의 관계

WITNESS_V3_REDESIGN.md Phase 3에서 8개 Pressure 변수 정의했음:
```
social_threat, physical_threat, shame_exposure, loyalty_pull,
uncertainty, urgency, isolation_pressure, sacred_salience
```

**이 8개를 어떻게 처리?**

선택지:

**옵션 A — Pressure 8개를 외부 변수로 흡수**
8개 Pressure가 사실 *"외부 변수"* B 목록의 일부. 별도 Layer 만들지 말고 
B 목록에 흡수.

**옵션 B — Pressure는 별도 Layer 유지**
8개 Pressure는 *"외부 사건이 만드는 압력"* 이라는 중간 추상화. 외부 변수와 
구별해서 유지.

**옵션 C — Pressure 자체를 도출 변수로**
외부 변수들의 조합으로 Pressure가 자동 계산되도록. 별도 정의 안 함.

**Lee 결정 필요.** 단, 옵션 C가 Lee 의도(*"개념 자체가 변수"*)와 가장 일관됨.
*"social_threat"* 도 결국 *"crowd_density × accusation_visibility"* 의 함수라면, 
별도 변수가 아니라 도출값.

---

## 7. 기존 16 변수 → 신규 변수 마이그레이션

기존 AgentState (16):
```
emotions: fear, hope, grief, confusion, love
physical: fatigue, hunger, health
slow_state: moral_injury, identity_shift, event_trauma, trust_scar
FaithJourneyState: jesus_understanding, obedience_maturity, fear_layers, 
                   communal_role
```

### 매핑 원칙

**대부분 1:1 매핑 또는 명칭만 변경.**

```
fear (기존)            → fear (신규, 그대로)
hope (기존)            → hope (신규, 그대로)
love (기존)            → love (신규, 그대로) — 단 target 분리 가능성
grief (기존)           → grief (신규, 그대로) 또는 sadness로 통합
confusion (기존)       → confusion (신규, 그대로)
fatigue (기존)         → fatigue (신규, 그대로)
hunger (기존)          → hunger (신규, 그대로)
health (기존)          → vitality 또는 health (그대로)
```

**모호한 분자 변수는 분해 또는 명확화:**

```
moral_injury (기존, 분자) 
  → 분해 또는 폐기
  → guilt (신규, 단일 개념) + shame (신규) — Lee 의도에 맞춤
  → 단, "fear_pain 같은 잘게 쪼갬" 과 다름. guilt와 shame은 일상적으로 명명 가능

identity_shift (기존)
  → 신규 변수 추가? 또는 기존 doubt + confusion으로 충분?

event_trauma (기존, 분자)
  → trauma 단일 변수로 유지? 또는 폐기?

trust_scar (기존, 분자)
  → trust 단일 변수의 음수 표현으로 처리?

jesus_understanding (기존)
  → understanding (단일 개념) + 외부 변수와 결합

obedience_maturity (기존)
  → obedience? 또는 폐기 (일상 개념 아님)

fear_layers (기존, Literal)
  → 폐기 (Lee 의도 어긋남)

communal_role (기존, Literal)
  → 폐기 또는 외부 변수로 이동
```

이 매핑은 **출발점 제안**이지 확정 아님. Step 1 (정경 정독) 결과에 따라 조정.

---

## 8. 작업 순서

### 8.1 Step A — 정경 정독 + 개념 추출 (가장 큰 작업)

베드로 등장 모든 장면 정독.
- 사복음서: 마태/마가/누가/요한
- 사도행전 1-15장 (베드로 주요 등장)
- 베드로전서/후서 (저자로서)
- 갈라디아서 1-2장 (바울이 언급)

**산출:** 추출된 개념 raw 목록 (정리 전)

### 8.2 Step B — 개념 정규화

- 중복 제거
- 명명 통일 (영어 단어 1-2개)
- 인물 변수(A) vs 외부 변수(B) 분류

**산출:** `docs/witness_concept_variables.md` v0.1 (정리됨)

### 8.3 Step C — 정경 근거 명시

각 변수마다 정경 구절 매핑 (§4).

**산출:** `docs/witness_concept_variables.md` v0.2 (근거 추가)

### 8.4 Step D — 상호작용 그래프 설계

§3 규칙 따라 sparse graph 설계.

**산출:** `docs/witness_concept_interactions.md`

### 8.5 Step E — 16 → 신규 마이그레이션

§7 매핑 확정, 기존 코드와 backward compatible 경로.

**산출:** `docs/witness_migration_v3.md` + 코드 변경

### 8.6 Step F — Lee 검토

각 Step 완료 후 Lee 확인. 특히 Step C 후 (정경 근거 검증) 와 Step E 후 
(매핑 확정) 가 핵심 분기점.

---

## 9. 자율 vs 보고 구분

### Claude Code 자율 결정 영역

- 변수 명칭 후보 (영어 단어 선택)
- 정경 정독 순서
- 추출 작업의 도구/방법
- 마이그레이션 코드 구현 세부

### Lee 판단 필수 영역

1. **변수 추가/제거 최종 승인**
   - 특히 모호한 분자 변수 (moral_injury, identity_shift) 처리 방향
2. **정경 근거의 신학적 적절성**
   - 정경 해석이 갈리는 부분
3. **인물 변수 vs 외부 변수 경계 모호한 케이스**
4. **Pressure Layer 처리 (옵션 A/B/C)**
5. **상호작용 graph의 부호 (+/-) 결정**
6. **베드로 특화 처리 vs 일반화 결정**

### Claude Code 절대 단독 결정 금지

- 정경 본문 수정 (Rule #2)
- 인물 행동까지 결정하는 변수 추가 (Rule #12)
- 학습 데이터 생성 (이번 Phase 범위 밖)
- BC 모델 재학습 (이번 Phase 범위 밖)

---

## 10. 산출물 구조

```
docs/
  witness_concept_variables.md          (Step A-C)
    Section 1: 인물 변수 (A 목록)
    Section 2: 외부 변수 (B 목록)
    Section 3: 각 변수의 정경 근거
  
  witness_concept_interactions.md       (Step D)
    Section 1: 인물 변수 ↔ 인물 변수
    Section 2: 외부 변수 → 인물 변수
    Section 3: 부호 (+/-) 표
  
  witness_migration_v3.md               (Step E)
    Section 1: 16 → 신규 매핑 테이블
    Section 2: Backward compat 전략
    Section 3: 폐기되는 기존 변수

engine/
  person/
    state_v3.py                         (Step E, 신규 AgentState)
    migration_v2_to_v3.py               (Step E, 변환 함수)

tests/
  test_person/
    test_state_v3.py
    test_migration_v2_to_v3.py
```

---

## 11. 금지 사항

- **잘게 쪼개기 금지** (`fear_death`, `fear_pain` 같은 변수 만들지 말 것)
- **추상 동기화 금지** (`avoidance_motivation`, `affect_valence` 같은 학술 변수)
- **인물 특화 변수 금지** (`loyalty_to_jesus`, `peter_calling` — 일반 변수 + 인스턴스화)
- **정경 근거 없는 변수 금지**
- **상호작용 폭발 금지** (각 변수 최대 3+3 connection)
- **Phase 3 Pressure / Phase 4 Rubric 작업 동시 진행 금지** — 이번은 변수만
- **신경망 학습 작업 금지** — Phase 5+ 영역

---

## 12. 세션 권장

| Step | 예상 세션 | 비고 |
|---|---|---|
| Step A (정경 정독) | 2-3 세션 | 가장 큰 작업, 인내 필요 |
| Step B (정규화) | 1 세션 | A 완료 후 |
| Step C (근거 명시) | 1-2 세션 | 신학적 신중함 필요 |
| Step D (그래프) | 1 세션 | C 완료 후 |
| Step E (마이그레이션) | 2 세션 | 코드 + test |

**총 7-9 세션.** 각 Step 완료 후 Lee 확인.

**한 세션에 여러 Step 시도 금지.** 특히 Step A (정경 정독)는 깊이 필요.

---

## 13. 진행 중 막혔을 때

### Step A (정경 정독)
1. 동일 장면을 사복음서가 다르게 기록 → 모두 기록 후 통합 시 Lee 판단
2. 베드로 행동의 동기가 명시 안 됨 → 추론 vs 보류 Lee 판단
3. 신학적 해석이 갈리는 장면 (예: 부활 후 디베랴 호숫가) → Lee 판단

### Step B (정규화)
1. 두 개념이 비슷한데 합칠지 분리할지 → Lee 판단
2. 명칭이 어색함 → 후보 제시 후 Lee 선택

### Step C (근거 명시)
1. 정경 인용이 약함 → 변수 폐기 vs 유지 Lee 판단
2. 인용은 있지만 해석 불일치 → Lee 판단

### Step D (그래프)
1. 부호 (+/-)가 모호 → Lee 판단
2. 한 변수에 4개 이상 연결 필요 → 우선순위 Lee 판단

### Step E (마이그레이션)
1. 기존 코드가 모호한 분자 변수에 강하게 의존 → 단계적 폐기 Lee 판단
2. Backward compat 불가능한 변경 → Lee 판단

---

## 14. 한 줄 요약

**"개념 자체가 변수다. fear는 fear, love는 love. 베드로의 생애 정경에서 
나타나는 모든 인물 개념과 외부 개념을 변수로 등록하되, 각 변수는 단순 
명료하고 정경 근거가 있어야 하며, 상호작용은 희소하게."**

---

## 15. 부록 — 이전 시도와의 차이 정리

| 항목 | Phase 2 첫 시도 (폐기) | 이번 재설계 |
|---|---|---|
| 변수 정의 | 잘게 쪼갬 (fear → 4개) | 개념 자체 (fear는 fear) |
| 변수 수 | 24개 | 35-65개 |
| 명명 | 길고 구체적 (`fear_isolation`) | 짧고 일상적 (`fear`, `isolation`) |
| 인물 vs 외부 | 인물 변수만 | 인물 + 외부 둘 다 |
| Peter 종속 | 베드로 특화 변수 다수 | 일반 개념 + 인스턴스화 |
| 근거 | ChatGPT 초안 | 정경 정독 |
| 상호작용 | 20 edges | 100-150 edges (희소 유지) |
| 출발점 | 추상적 분류 | 정경 본문 |

근본 차이: **Top-down (분류 체계 → 변수)** vs **Bottom-up (정경 → 개념 → 변수)**.
이번은 bottom-up.

---

## 16. Claude Code에게 — 특별 주의

이번 작업에서 다음 함정 조심:

### 함정 1 — 학술 분류 체계 끌어오기
"감정 분류 체계 (Plutchik, Ekman)" 같은 거 끌어와서 *"이 6개가 보편 감정"* 
선언하지 말 것. Lee 의도는 정경에서 직접 추출.

### 함정 2 — 변수 수 자기 제한
"24개로 줄여야 한다" 강박 갖지 말 것. Lee 의도는 *"가능한 한 다"*. 
50-60개도 OK.

### 함정 3 — 잘게 쪼개기 본능
이전 시도에서 한 실수. *"이걸 더 분해할 수 있나?"* 가 아니라 *"이게 일상적으로 
명명 가능한 단위인가?"* 가 기준.

### 함정 4 — Peter 종속 변수 만들기
*"loyalty_to_jesus"* 같은 인물+target 결합 변수 만들지 말 것. 일반 개념 
(`loyalty`) + 인스턴스 데이터 (target=jesus) 분리.

### 함정 5 — 자기 격려
"이번엔 잘 만든 것 같다" 같은 자기 평가 금지. Lee 검토만이 평가.

### 함정 6 — 220 임의값 다시 만들기
이전 시도의 220개 임의 scalar (migration 계수, threshold 등) 반복 금지. 
이번은 변수 정의에 집중. 수치는 Lee 검토 후.

---

## 17. 마지막 — 무엇이 *"적용"* 인가

Lee 지시:
> *"이 내용 적용해서 진행해보자"*

여기서 *"적용"* 은:
1. Phase 2 첫 시도(24 변수) **폐기**
2. 새 작업 = 정경 정독 → 개념 추출 → 변수 등록
3. 인물 + 외부 둘 다 변수화
4. 베드로 범위로 한정
5. 잘게 쪼개기 vs 개념 자체의 차이 명확히 인식

코드 작성 전에 **§0과 §1을 먼저 정독하고, 그 정신을 이해한 후 Step A 시작.**
