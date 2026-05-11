# WITNESS — Readability Blind 질문 개선안 + 프로젝트 개선 + 다음 진행방향

## 0. 문서 목적

이 문서는 현재 WITNESS B-direction 진행 상태를 바탕으로 다음 세 가지를 함께 정리한다.

1. **READABILITY_BLIND_PROTOCOL 질문 개선안**
2. **현재 프로젝트 개선 포인트**
3. **다음 진행방향 및 branch 판단 기준**

이 문서의 목적은 단순히 질문을 고치는 것이 아니라,  
현재 WITNESS가 **engine-internal mechanism 단계**에서 **readable world 단계**로 넘어가기 위해  
무엇을 바꾸고 무엇을 확인해야 하는지를 한 번에 정리하는 것이다.

---

## 1. 현재 상태에 대한 핵심 판단

현재 WITNESS는 다음 상태에 있다.

- world flow kernel은 상당 부분 확인됨
- role priors, Phase 2a, rumor/memory, cast support, mixed dynamics 일부까지 구조적으로 밝혀짐
- 그러나 아직 외부 인간 독자가 이것을 **“세계의 흐름”**으로 읽을 수 있는지는 확인되지 않음
- 따라서 지금 가장 중요한 단계는 **Readability Blind**이며, 이것이 Branch A/B/C를 가르는 인간 게이트다

즉 지금은 더 많은 mechanism drilling보다  
**“이 엔진이 실제로 읽히는가?”**를 검증하는 것이 더 중요하다.

---

## 2. 현재 Readability Blind Protocol의 좋은 점

현재 프로토콜의 장점은 유지해야 한다.

### 유지할 핵심
- evaluator가 scenario / seed / ablation / metric을 모른 상태에서 읽는다
- 읽고 나서 답한다
- internal mechanism knowledge가 없는 인간 판독을 gate로 둔다
- 결과를 바로 branch decision에 연결한다

이 네 가지는 매우 좋다.  
따라서 질문 개선은 **이 구조를 바꾸지 않고**, 외부 판독의 질을 높이는 방향으로만 해야 한다.

---

## 3. 질문(Q1-Q5) 개선안

---

### Q1 — Flow vs noise

#### 현재
> 이 probe는 랜덤 로그처럼 보이나, 어떤 흐름이 느껴지나?

Options:
- RANDOM
- FLOW_HINT
- CLEAR_FLOW

#### 문제
현재 Q1은 나쁘지 않지만, 판독자가 “흐름이 있다”와 “읽을 만하다”를 혼동할 수 있다.  
어떤 probe는 흐름은 느껴지지만 여전히 이해하기 어렵다.

#### 개선안
Q1은 그대로 유지하되, 아래 보조 구분을 추가한다.

### Q1b — Readability confidence
> 지금 느낀 흐름을 내가 설명할 수 있는가?

Options:
- `CAN_EXPLAIN` — 어떤 흐름인지 말로 설명 가능
- `PARTIAL_EXPLAIN` — 대략 느낌은 있으나 설명은 불완전
- `CANNOT_EXPLAIN` — 뭔가 있지만 설명 어려움

#### 이유
WITNESS의 다음 단계는 단순 flow detection이 아니라 **readable world**이기 때문이다.  
Q1만으로는 “느낌은 있는데 설명 못함”과 “명확히 이해됨”이 섞인다.

---

### Q2 — Dominant perceived pressure

#### 현재
primary 하나 선택 + free-text

#### 문제
현재 mixed-arc나 복합 dynamics를 보기엔 pressure를 하나만 고르는 건 너무 거칠다.  
특히 accusation + shame, scarcity + grief, sacred + blame 같이 섞이는 경우가 있다.

#### 개선안

### Q2a — Primary perceived pressure
기존 그대로 유지:
- `shame_social`
- `fear_physical`
- `sacred_awe`
- `scarcity_material`
- `accusation_blame`
- `grief_loss`
- `none_discernible`

### Q2b — Secondary perceived pressure
같은 목록에서 하나 더 선택 가능:
- `none_secondary`
- `shame_social`
- `fear_physical`
- `sacred_awe`
- `scarcity_material`
- `accusation_blame`
- `grief_loss`

### Q2c — Pressure clarity
> 이 압력이 뚜렷하게 읽히는가?

Options:
- `CLEAR`
- `MIXED_BUT_READABLE`
- `VAGUE`
- `UNREADABLE`

#### 이유
이렇게 해야 later analysis에서
- 단일 pressure probe
- mixed pressure probe
- 잘못 읽히는 probe
를 나눌 수 있다.

---

### Q3 — Relation / group dynamics

#### 현재
- NONE
- SURFACE
- SHIFT
- RESTRUCTURE

#### 문제
지금 구조는 개인/집단/군중/권위가 섞여 있어서,  
“조금 움직임”과 “집단 단위 재편”을 구분하기 어렵다.

#### 개선안

### Q3a — Relation/group change level
- `NONE`
- `LOCAL_SHIFT` — 일부 agent 수준 변화만 감지
- `COHORT_SHIFT` — 집단/코호트 수준 변화 감지
- `RESTRUCTURE` — 관계/집단 재편으로 느껴짐

### Q3b — What changed most?
복수 선택 가능:
- `interpersonal_relation`
- `group_alignment`
- `crowd_mood`
- `authority_presence`
- `public_attention`
- `not_discernible`

#### 이유
WITNESS가 world 쪽으로 가려면 “사람 사이 관계”만이 아니라  
**군중, 권위, public attention**도 읽혀야 한다.

---

### Q4 — Arc perception

#### 현재
- NO_ARC
- FLAT
- ESCALATION
- RECOVERY
- MIXED_ARC

#### 문제
기본적으로 괜찮다.  
다만 지금 WITNESS는 oscillation / cycle / partial recovery가 있으므로  
단순 recovery / escalation만으론 부족할 수 있다.

#### 개선안

### Q4a — Primary arc type
- `NO_ARC`
- `FLAT`
- `ESCALATION`
- `RECOVERY`
- `MIXED_ARC`
- `CYCLIC_ARC`

### Q4b — Arc strength
- `WEAK`
- `MODERATE`
- `STRONG`

#### 이유
지금 limit cycle / oscillation이 의미 있는 dynamics인지 보려면  
“mixed”와 “cyclic”을 구분하는 것이 좋다.

---

### Q5 — Oscillation character

#### 현재
- NO_OSCILLATION
- MEANINGLESS_NOISE
- WEAK_RHYTHM
- CLEAR_CYCLE

#### 문제
좋지만, oscillation이 “의미 있는 반복”인지 “그냥 왔다 갔다 함”인지에 더해  
**그 반복이 narrative sense를 만드는가**가 필요하다.

#### 개선안

### Q5a — Oscillation type
- `NO_OSCILLATION`
- `MEANINGLESS_NOISE`
- `WEAK_RHYTHM`
- `CLEAR_CYCLE`

### Q5b — Narrative contribution
> oscillation이 이해를 돕나, 방해하나?

Options:
- `HELPS_READABILITY`
- `NEUTRAL`
- `HURTS_READABILITY`

#### 이유
WITNESS는 cycle을 발견했지만, 좋은 발견인지 artifact인지 아직 모른다.  
이 질문이 그 차이를 인간 쪽에서 잡아준다.

---

### Q6 — Confusion notes (optional → semi-required)

#### 현재
Optional free text

#### 문제
지금 단계에선 “왜 unreadable한가”가 훨씬 중요하다.  
optional이면 가장 중요한 진단 데이터가 비어버릴 수 있다.

#### 개선안
다음 형식으로 **반필수** 처리한다.

### Q6a — 가장 이해 안 된 점 1개 이상
예:
- pressure가 안 드러남
- agent가 너무 많아 구분 안 됨
- relation shift가 안 보임
- oscillation이 의미 없는 반복처럼 보임
- 사건이 왜 이어지는지 모르겠음
- world-side 변화보다 개인 로그만 보임

### Q6b — readable하게 만들려면 무엇이 더 필요했는가
예:
- 요약 문장
- relation delta 강조
- dominant pressure 표기
- cohort-level summary
- key event grouping

#### 이유
이건 단순 평가가 아니라 **Branch A/B 판단용 설계 피드백**이다.

---

## 4. 개선된 질문 세트 제안 (최종형)

### Q1 — Flow vs noise
- RANDOM
- FLOW_HINT
- CLEAR_FLOW

### Q1b — Readability confidence
- CAN_EXPLAIN
- PARTIAL_EXPLAIN
- CANNOT_EXPLAIN

### Q2a — Primary perceived pressure
- shame_social
- fear_physical
- sacred_awe
- scarcity_material
- accusation_blame
- grief_loss
- none_discernible

### Q2b — Secondary perceived pressure
- none_secondary
- shame_social
- fear_physical
- sacred_awe
- scarcity_material
- accusation_blame
- grief_loss

### Q2c — Pressure clarity
- CLEAR
- MIXED_BUT_READABLE
- VAGUE
- UNREADABLE

### Q3a — Relation/group change level
- NONE
- LOCAL_SHIFT
- COHORT_SHIFT
- RESTRUCTURE

### Q3b — What changed most?
- interpersonal_relation
- group_alignment
- crowd_mood
- authority_presence
- public_attention
- not_discernible

### Q4a — Primary arc type
- NO_ARC
- FLAT
- ESCALATION
- RECOVERY
- MIXED_ARC
- CYCLIC_ARC

### Q4b — Arc strength
- WEAK
- MODERATE
- STRONG

### Q5a — Oscillation type
- NO_OSCILLATION
- MEANINGLESS_NOISE
- WEAK_RHYTHM
- CLEAR_CYCLE

### Q5b — Narrative contribution
- HELPS_READABILITY
- NEUTRAL
- HURTS_READABILITY

### Q6a — 가장 이해 안 된 점
(free text, 최소 1개)

### Q6b — readable하게 만들려면 필요한 것
(free text)

---

## 5. 이 질문 개선이 프로젝트에 주는 의미

이 질문 개선은 단순 UX 개선이 아니다.  
이건 프로젝트 방향을 더 정확히 판단하기 위한 장치다.

### 개선 후 더 잘 알 수 있는 것
1. 흐름은 있는데 설명이 안 되는지
2. mixed dynamics가 실제로 읽히는지
3. oscillation이 artifact처럼 보이는지, meaningful cycle처럼 보이는지
4. relation/group/world-side 변화가 인간 눈에 드러나는지
5. 현재 unreadability가 구조 문제인지, probe presentation 문제인지

즉 이 질문 개선은  
**Branch A(가독성 확장) vs Branch B(단순화) vs Branch C(넓은 세계)**를 더 정교하게 결정하게 해준다.

---

## 6. 현재 프로젝트 개선 포인트

지금 WITNESS의 개선 포인트는 크게 5개다.

---

### 개선 포인트 1 — Decorative / decoupled world 요소 정리

지금 sacred 계열 일부와 narrative field 일부는 실제 동학에 거의 안 들어갈 가능성이 높다.  
즉 “이름은 있는데 구조에 안 연결된 장식층”이 있다.

해야 할 일:
- sacred_awe 관련 실제 consumer/propagation 재점검
- narrative field 6개의 reserve/remove 확정
- component ledger 정식화

핵심 목표:
- 세계를 풍부하게 보이게 하는 이름표가 아니라, 실제로 world state를 바꾸는 요소만 남기기

---

### 개선 포인트 2 — Recovery diversity 확보

현재 recovery는 너무 Phase 2a + forgiveness rumor channel에 몰려 있다.  
이건 kernel 발견으로는 좋지만, 완성된 세계로는 부족하다.

필요한 추가 recovery family 후보:
- trust-driven stabilization
- belonging-driven calming
- authority withdrawal de-escalation
- scarcity easing recovery
- spatial disengagement recovery
- ritual / sacred grounding recovery (진짜로 wired될 경우)

핵심 목표:
- “회복이 있다”가 아니라
- “회복이 여러 방식으로 존재한다”

---

### 개선 포인트 3 — World-side autonomy 강화

지금 world flow는 있지만, 아직은 일부 process가 인물 쪽 사건에 많이 기대고 있다.

다음에 살릴 process 우선순위:
1. rumor propagation
2. crowd attention / blame concentration
3. authority response
4. scarcity persistence
5. sacred / ritual timing (단, decorative가 아닌 실제 wired 버전)

핵심 목표:
- 사람이 없어도 world state가 조금은 움직일 것
- 사람 행동은 그 움직임을 증폭/변형할 것

---

### 개선 포인트 4 — Meso-scale 강화

개인과 거시 세계 사이에 meso-scale이 더 필요하다.

강화 대상:
- cohort mood
- crowd suspicion
- blame concentration
- public attention
- local trust climate
- faction / group alignment

핵심 목표:
- 세계를 “개인 로그의 합”이 아니라
- “집단적 흐름을 가진 구조”로 바꾸기

---

### 개선 포인트 5 — Readability-facing representation

지금 많은 동학이 내부에서는 보이는데, 인간에게는 아직 직접 읽히지 않을 수 있다.

가능한 보완:
- probe에 dominant pressure summary 추가 여부 검토
- cohort delta / relation delta를 더 잘 드러내는 probe formatting
- event grouping (쓸모없는 나열 방지)
- key shifts를 묶어서 보여주는 compact summary

핵심 목표:
- world dynamics를 설명 없이도 어느 정도 느낄 수 있게 만들기

---

## 7. 다음 진행방향

이제 다음 방향은 분명하다.

---

### 1순위 — Readability Blind 실행 (최우선)
이미 준비는 끝났다.  
지금 가장 중요한 건 인간 판독이다.

해야 할 것:
- P1~P12 blind reading
- 개선된 Q 세트로 평가
- readable / partially readable / unreadable 판정
- confusion notes 수집

왜 최우선인가:
- 지금은 내부 metric보다 외부 readability가 branch 결정의 blocker이기 때문

---

### 2순위 — Branch B 정리 계속 (단순화)
Readability 전/후와 무관하게 일부는 지금 해도 된다.

저위험 작업:
- breach_count annotation
- unwired field docstring 정리
- component ledger 업데이트
- reserve/remove 후보 확정

왜 필요한가:
- 설계 부채를 줄이지 않으면 다음 단계도 불필요한 층 위에서 흔들린다

---

### 3순위 — World-side process 승격
Readability 결과가 나쁘지 않다면 바로 붙일 다음 요소는 world-side process다.

우선순위:
1. rumor propagation 정식화
2. crowd attention / blame concentration 정식화
3. authority response 정식화

왜 이 3개인가:
- 사람 밖의 세계가 스스로 움직이는 느낌을 가장 빨리 만들기 때문

---

### 4순위 — Recovery diversification 실험
Phase 2a 외 recovery channel을 최소 1~2개 추가/탐색해야 한다.

추천 실험:
- trust high + low authority pressure에서 calming
- belonging high cohort에서 de-escalation
- spatial relocation이 실제 recovery channel이 될 수 있는지
- scarcity 완화 시 recovery slope 변화

---

### 5순위 — Meso-scale / population grammar 초안
지금부터는 named character를 늘리기보다,  
role cluster / cohort / public node 쪽으로 이동해야 한다.

해야 할 것:
- role families 정리
- profile priors template
- group seeding template
- world placement template

---

## 8. Branch 판단 기준 (개선안 반영)

### Branch A — Readability-facing
조건:
- readable ≥ 8/12
- Q1b에서 CAN_EXPLAIN이 다수
- Q2/Q3/Q4/Q5가 일정 정도 일관됨
- confusion notes가 probe formatting 수준 문제 위주

### Branch B — Simplification 계속
조건:
- readable ≤ 3/12
- Q1=RANDOM 비율 높음
- pressure clarity가 VAGUE/UNREADABLE 다수
- oscillation이 HURTS_READABILITY로 많이 판정됨
- confusion notes가 구조 부채를 지적함

### Branch A+B 병행
조건:
- readable 4~7/12
- 흐름은 느껴지지만 설명/판독이 불안정
- mixed dynamics는 있으나 external reading이 흔들림

### Branch C — Broader World
조건:
- readable 높음
- world-side process 일부가 외부에서도 읽힘
- mixed-arc가 collapse 없이 유지
- simplification 필요성이 낮음

---

## 9. 지금 하지 말아야 할 것

- neural policy 도입
- Phase 2a 추가 drilling
- shame multiplier 미세 스윕
- 새 변수 대량 추가
- 새 scenario 대량 추가
- universality 주장
- single-seed 결론
- readability blind 없이 “이제 읽히는 세계” 선언

---

## 10. 한 줄 요약

**다음 핵심은 질문 세트를 더 정교하게 만들어 blind readability를 제대로 수행하고,  
그 결과를 바탕으로 decorative 구조를 줄이고 world-side process와 meso-scale을 강화하는 것이다.  
즉 이제는 mechanism을 더 깊게 파는 것보다, 이 엔진이 인간에게도 ‘세계처럼’ 읽히도록 만드는 쪽으로 넘어가야 한다.**
