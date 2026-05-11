# WITNESS — 세계구축 완성을 위한 핵심 요소, 자가판단 척도, 다음 진행 작업지시서

## 0. 문서 목적

이 문서는 지금까지의 WITNESS B-direction 진행 결과와 대화에서 정리된 설계 원칙을 바탕으로,  
WITNESS가 **“인물 재현 프로젝트”를 넘어 “세계구축 프로젝트”로 완성되기 위해 필요한 요소들**을 정리하고,  
앞으로 프로젝트 내부에서 스스로 **“우리가 진짜 세계구축 방향으로 가고 있는가?”**를 판단할 수 있는 척도를 제시하기 위해 작성한다.

이 문서는 세 가지를 동시에 다룬다.

1. **세계구축 완성에 필요한 요소**
2. **세계구축 진행 여부를 자가판단할 수 있는 척도**
3. **지금 다음으로 해야 할 일**

---

## 1. 현재 프로젝트 위치 요약

현재 WITNESS는 다음 단계까지 왔다.

- Peter 중심 story replay 단계는 이미 지남
- persona/world interface는 상당 부분 구축됨
- world flow kernel은 발견되었고, 루프를 통해 구조적 병목도 상당 부분 드러남
- conditional invariance, role-conditioned priors, agent-level emergent framing, cycle / recovery channel 등 engine-level 동역학은 많이 해부됨
- 그러나 아직 완성된 “세계”라기보다 **세계가 흐르기 시작하는 커널**을 발견하고 정리하는 단계에 있음
- external readability, broader world-side autonomy, mixed-arc richness, world-side process diversity는 아직 미완

즉 현재는 **“세계구축 100% 완성”이 아니라, 세계구축의 커널을 확보하고 다음 확장 방향을 고르는 단계**다.

---

## 2. 세계구축으로 완성되기 위해 반드시 필요한 요소

세계는 사람만으로 돌아가지 않는다.  
좋은 세계는 인물의 감정이나 행동만이 아니라, 인물 바깥의 구조와 힘들이 독립적으로 움직이면서  
다시 인물을 흔드는 구조를 가져야 한다.

아래 요소들은 WITNESS가 “인물 엔진”을 넘어 “세계 엔진”으로 가기 위해 필요한 핵심 구성요소들이다.

---

### 요소 A — Shared Human Engine

모든 인물이 공유하는 공통 엔진.

포함 요소:
- 공통 state ontology
- pressure 처리 방식
- motif 구조
- action selection 구조
- recovery / decay 구조
- relation slot 구조
- evaluation interface

이건 이미 상당 부분 구축되어 있다.  
다만 앞으로 더 중요한 건 이 엔진을 늘리는 것이 아니라, **어디까지가 shared engine이고 어디서부터가 content / profile / world binding인지 명확히 유지하는 것**이다.

핵심 질문:
- 이 메커니즘은 특정 인물 전용인가?
- 아니면 어떤 인물에도 공통으로 적용되는가?

---

### 요소 B — Persona Profile Schema

인물별 차이를 “새 변수 세트”가 아니라 **공통 엔진 위의 profile parameter**로 표현하는 구조.

포함 가능 예:
- shame sensitivity
- threat reactivity
- repair tendency
- conceal tendency
- authority reactivity
- attachment strength
- recovery speed
- peer dependence
- sacred susceptibility

핵심 원칙:
- 인물 하나 = 규칙 묶음이 아님
- 인물 하나 = shared engine 위의 profile config

주의:
- profile 차원이 끝없이 늘어나면 다시 handcrafted가 된다
- profile은 “행동 분기를 실제로 바꾸는 최소 축”만 남겨야 한다

---

### 요소 C — Generic Target-Role Ontology

target-aware relation을 특정 인물명이나 고유 집단이 아니라 **generic social role**로 바꾸는 구조.

예:
- self
- primary_focus
- intimate_other
- peer_group
- in_group
- public_group
- authority_group
- family
- rival
- protected_other

핵심 효과:
- Peter, Judas, Van Gogh 등 서로 다른 시나리오에 같은 relation engine을 재사용 가능
- content layer에서 binding만 바꿔도 됨

---

### 요소 D — World-side Independent Processes

가장 중요한 요소 중 하나.  
세계를 세계답게 만드는 건 사람 바깥에서 독립적으로 돌아가는 process들이다.

최소한 필요한 process 후보:
- rumor propagation
- crowd attention / suspicion / blame concentration
- authority vigilance / response
- scarcity / resource pressure
- sacred / ritual timing
- information delay / distortion

핵심 원칙:
- 사람이 없어도 일정 부분 world state가 변해야 한다
- 사람 행동은 그 process를 증폭/변형할 수 있어야 한다

즉 세계는 단순 배경이 아니라 **자기 시간을 가진 시스템**이어야 한다.

---

### 요소 E — World Memory

세계는 매 tick 새로 시작하지 않는다.  
좋은 세계는 이전 사건의 잔향이 다음 사건 가능성을 바꾼다.

필요한 memory 예:
- shame_climate
- rumor_residue
- authority_vigilance residue
- unresolved_group_tension
- public_attention trail
- forgiveness_trace
- scarcity persistence

핵심 효과:
- 과거가 현재를 바꿈
- state change보다 possibility landscape change가 중요해짐

---

### 요소 F — Meso-scale Dynamics (Crowd / Group / Faction)

개인과 거시 세계 사이를 연결하는 중간 규모 구조.

필요한 이유:
- crowd는 단순히 개인 100명의 평균이 아님
- group mood, faction stance, public suspicion, collective attention 같은 상태는 독립 동학을 가짐

최소 요소:
- crowd node
- group cohesion
- faction mood
- public suspicion
- local trust climate
- collective blame / fear

세계가 진짜로 흐르려면 개인과 macro-state 사이의 이 층이 필요하다.

---

### 요소 G — Institution / Constraint Layer

사람은 감정만으로 안 움직인다.  
제도와 규범은 action space 자체를 바꾼다.

필요한 요소:
- punishment expectation
- rule enforcement
- stigma cost
- authority reach
- role-based affordance
- taboo / sacred constraint

핵심 효과:
- 어떤 행동은 사실상 금지
- 어떤 행동은 role마다 비용이 다름
- 어떤 말과 행위는 공개/비공개에 따라 의미가 달라짐

---

### 요소 H — Space as Affordance

공간은 단순 location label이 아니라, 행동 가능성과 비용 구조를 결정하는 요소다.

예:
- visibility
- concealability
- reachability
- crowdability
- authority reach
- sacred proximity
- escape routes

좋은 세계에서 공간은 scenery가 아니라 **interaction geometry**다.

---

### 요소 I — Time as Rhythm

tick만 있다고 시간이 되는 건 아니다.  
세계에는 리듬이 필요하다.

예:
- 낮/밤
- fatigue accumulation
- ritual calendar
- delayed consequences
- long-tail recovery
- decay half-life differences
- anticipation / waiting structures

이게 있어야 같은 사건도 다른 타이밍에 다른 의미를 가진다.

---

### 요소 J — Population Grammar

세계를 위해선 named character를 하나씩 만드는 게 아니라,  
“어떤 세계에 어떤 종류의 사람들이 기본적으로 존재하는가”를 정의해야 한다.

예:
- peer-dependent role
- authority-aligned role
- conceal-prone role
- public-facing role
- high-repair role
- shame-sensitive role
- opportunistic role
- stabilizer role

핵심 원칙:
- agent 1명 = handcrafted character가 아니라
- role cluster + profile priors + relation seed + world placement

---

### 요소 K — Story Probe Layer

구조를 먼저 만들되, 구조가 실제로 어떤 흐름을 낳는지 계속 짧게 확인할 수 있어야 한다.

story probe는:
- 완성된 문학 작품이 아니라
- 구조가 낳은 흐름 샘플이다

좋은 story probe가 보여줘야 하는 것:
- dominant pressure
- relation shift
- key events
- motif sequence
- world memory effect
- readable arc hint

이 층이 있어야 구조가 “읽히는 세계”로 넘어갈 수 있다.

---

## 3. 프로젝트가 세계구축 쪽으로 가고 있는지 판단하는 자가판단 척도

이 섹션은 앞으로 프로젝트 내부에서 스스로 질문할 수 있는 기준이다.

판정은 4단계로 구분한다.

- **Level 0 — 인물 재현 단계**
- **Level 1 — 인물-세계 인터페이스 단계**
- **Level 2 — 세계 흐름 커널 단계**
- **Level 3 — 읽히는 세계 단계**
- **Level 4 — 확장 가능한 세계 단계**

---

### 척도 1 — World-side Autonomy

질문:
- 사람이 아무 행동도 안 해도 world state가 변하는가?
- rumor, authority, crowd, scarcity 중 하나라도 독립 process로 돌아가는가?

판정:
- 0점: world가 완전 배경
- 1점: 이벤트가 있으면만 반응
- 2점: 일부 process가 독립적으로 움직임
- 3점: 여러 process가 서로 영향을 주며 독립적으로 움직임

현재 예상 위치:
- 1~2 사이

---

### 척도 2 — Cross-layer Propagation

질문:
- 한 사건이 최소 2개 이상의 다른 레이어로 퍼지는가?
- action → rumor → crowd → authority 같은 연쇄가 실제로 있는가?

판정:
- 0점: 한 레이어 안에서만 반응
- 1점: 2 layers
- 2점: 3 layers
- 3점: 4+ layers + memory residue

현재 예상 위치:
- 2 이상 (이미 5 layers 전파 경험 있음)

---

### 척도 3 — World Memory

질문:
- 과거 사건이 다음 행동 가능성을 바꾸는가?
- memory가 state change가 아니라 possibility landscape를 바꾸는가?

판정:
- 0점: 매 tick 새로 시작
- 1점: 일시 잔향
- 2점: 의미 있는 잔향과 재노출 효과
- 3점: 여러 memory channel이 동시에 작동

현재 예상 위치:
- 1~2

---

### 척도 4 — Recovery Diversity

질문:
- 회복이 단일 회로(예: Phase 2a + shame) 외에도 가능한가?
- trust / belonging / authority withdrawal / scarcity easing 같은 다른 path가 있는가?

판정:
- 0점: recovery 없음
- 1점: recovery 하나만 있음
- 2점: 2~3개 recovery family
- 3점: scenario 따라 다른 recovery family가 작동

현재 예상 위치:
- 1

---

### 척도 5 — Meso-scale Reality

질문:
- 군중, 집단, faction이 단순 aggregate가 아니라 자체 상태를 가지는가?

판정:
- 0점: 개인만 있고 meso 없음
- 1점: crowd proxy 존재
- 2점: group / crowd node가 작동
- 3점: faction / public mood / blame concentration까지 존재

현재 예상 위치:
- 1

---

### 척도 6 — Information Topology

질문:
- 정보가 누구에게 어떻게 퍼지는지 구조가 있는가?
- rumor와 사실이 다른 경로를 갖는가?

판정:
- 0점: 정보 구조 없음
- 1점: rumor만 존재
- 2점: 정보 비대칭 / delay / distortion 일부 존재
- 3점: 정보 topology가 세계 동학의 핵심 축으로 작동

현재 예상 위치:
- 1

---

### 척도 7 — Institution / Constraint Reality

질문:
- 권위, 제도, 비용, 규범이 action space를 실제로 자르는가?

판정:
- 0점: 심리 엔진
- 1점: constraint 일부 존재
- 2점: role / public exposure / authority reach가 행동 가능성에 영향
- 3점: institution이 독립적으로 world state를 흔듦

현재 예상 위치:
- 1~2

---

### 척도 8 — Mixed-Arc Richness

질문:
- 두 pressure family가 동시에 걸렸을 때 한쪽이 완전히 죽지 않고, 섞인 흐름이 나오는가?

판정:
- 0점: 하나만 강함
- 1점: mixed probe 일부 가능
- 2점: 혼합 조건에서도 새로운 arc family 발생
- 3점: mixed arc가 일반적이고 읽힘

현재 예상 위치:
- 1 (probe는 했지만 아직 충분히 rich하지 않음)

---

### 척도 9 — Readability

질문:
- 외부 독자가 읽었을 때 “그냥 로그”가 아니라 “흐름”으로 느껴지는가?

판정:
- 0점: unreadable
- 1점: partially readable
- 2점: 일부 probe readable
- 3점: 다수 probe에서 arc / pressure / relation shift가 읽힘

현재 예상 위치:
- 미측정 (중요 blocker)

---

### 척도 10 — Expansion Readiness

질문:
- 새 인물/새 scenario 추가 시 필요한 것이 handcrafted patch인가, 아니면 profile + binding + placement인가?

판정:
- 0점: 매번 새 규칙 세트 필요
- 1점: 일부 shared kernel
- 2점: profile + binding 위주
- 3점: population grammar로 샘플링 가능

현재 예상 위치:
- 1~2

---

## 4. 자가판단 종합 규칙

### 세계구축 진행 수준 판정

#### 단계 A — 아직 인물 엔진 중심
다음 중 5개 이상이면 여기에 해당:
- World-side autonomy ≤1
- Recovery diversity =1
- Information topology ≤1
- Meso-scale ≤1
- Readability 미측정 또는 0
- Expansion readiness ≤1

#### 단계 B — 세계 흐름 커널 확보
다음 중 다수가 해당:
- Cross-layer propagation ≥2
- World memory ≥1
- Mixed-arc probe 일부 존재
- Shared kernel 존재
- role cluster / prior 구조 존재
- Readability는 아직 미완

#### 단계 C — 읽히는 세계 입구
다음이 필요:
- Readability blind에서 최소 일부 probe readable
- mixed-arc가 무너지지 않음
- 세계 memory와 meso-scale이 외부에서 감지 가능
- recovery가 단일 회로에서 약간 벗어남

#### 단계 D — 확장 가능한 세계
다음이 필요:
- profile + binding 기반 인물 instantiate 가능
- role cluster sampling 가능
- world-side process 3개 이상 독립 가동
- broader world / cast combinatorics에서도 유지
- external readability가 안정적

### 현재 프로젝트 위치 판단
현재 WITNESS는 **단계 B: 세계 흐름 커널 확보**에 있다.  
단, 단계 C(읽히는 세계 입구)로 넘어가기 직전의 정리 국면이다.

---

## 5. 지금 다음으로 진행해야 할 것

우선순위를 매우 명확하게 적는다.

---

### 우선순위 1 — Kernel Simplification 마무리

현재 Branch B가 우선이다.

해야 할 것:
- decorative sacred 정리
- inert / reserve state-field 정리
- component ledger 공식화
- single-loop recovery dependence 명시
- unwired / dormant / doc-only 컴포넌트 표기

목표:
- 현재 kernel을 더 단단한 최소 커널로 압축

---

### 우선순위 2 — External Readability Blind 실행

이건 지금 가장 중요한 human gate다.

해야 할 것:
- 이미 생성된 readability probes 12개 사용
- blind로 읽기
- Q1-Q5 답변 수집
- readable / partially readable / unreadable 판정
- dominant perceived pressure / arc / relation shift 기록

목표:
- 지금 구조가 내부 metric을 넘어 외부에서도 “흐름”으로 읽히는지 확인

이 결과는 다음 branch 선택에 직접 사용한다.

---

### 우선순위 3 — World-side Process 3개 정식 승격

이제부터 사람 바깥의 세계 process를 명확하게 살려야 한다.

첫 승격 후보 3개:
1. rumor propagation
2. crowd attention / blame concentration
3. authority response

목표:
- 사람 없이도 world state가 움직임
- 사람 행동이 world-level 변화를 남김
- world가 다음 사건 가능성 지형을 바꿈

---

### 우선순위 4 — World Memory 정식 계층화

현재 존재하는 memory를 정식 layer로 만든다.

우선 후보:
- shame_climate
- rumor_residue
- authority_vigilance residue
- unresolved_group_tension
- forgiveness_trace

해야 할 것:
- 각 memory의 생성 조건
- 유지 / decay
- action space / pressure / event spawn에 주는 영향
명시

---

### 우선순위 5 — Meso-scale 추가

crowd / group / public mood를 중간 계층으로 승격한다.

우선 추가할 상태:
- public suspicion
- blame concentration
- group cohesion
- local trust climate
- crowd attention lock

목표:
- 개인 ↔ macro world 사이를 메우기
- social flow를 개별 인물 평균이 아니라 meso dynamics로 다루기

---

### 우선순위 6 — Mixed-Arc 강화

이미 mixed probe는 시작됐다.  
다음에는 mixed condition이 truly generative한지 더 봐야 한다.

추천 실험:
- accusation + sacred overlap
- scarcity + grief
- authority + rumor
- public shame + low belonging

봐야 할 것:
- single-loop collapse 여부
- mixed motif composition
- relation / memory / crowd의 교차 변화
- readability 개선 여부

---

### 우선순위 7 — Population Grammar 초안

Named character를 늘리는 대신 role cluster 기반 instantiate 구조를 만든다.

필요 요소:
- role families
- profile prior templates
- relation seeding templates
- placement templates
- initial history seeds

목표:
- 새 인물 = handcrafted character가 아니라 config + role binding

---

## 6. 지금 하지 말아야 할 것

### 금지
- neural policy 바로 도입
- Phase 2a 추가 drilling
- shame multiplier 미세 스윕
- 새 변수 대량 추가
- 새 named scenario 대량 추가
- universality 주장
- single-seed 기반 결론
- external readability 평가 없이 “읽히는 세계” 주장

---

## 7. 다음 단계 분기 규칙

### A로 갈 조건 — Readability-facing Phase
다음이 만족되면:
- readability blind에서 ≥8/12 readable
- mixed-arc에서도 arc-like 흐름 감지
- world-side process가 일부 외부에서 읽힘

→ 다음은 readability-facing phase

### B 유지 조건 — Kernel Simplification 계속
다음이 만족되면:
- readability 낮음
- mixed-arc collapse 잦음
- inert 구조 다수
- recovery diversity 낮음

→ Branch B 유지

### C로 갈 조건 — Broader World Phase
다음이 만족되면:
- readability 일정 수준 확보
- world-side process 3개 이상 독립 가동
- meso-scale 작동
- mixed-arc 유지
- expansion readiness ≥2

→ Broader world phase 진입

---

## 8. 한 줄 요약

**지금 WITNESS는 “세계를 낳는 커널”은 잡았지만, 아직 “완성된 세계”는 아니다.  
앞으로 필요한 것은 사람 내부를 더 파는 것이 아니라,  
사람 바깥에서 독립적으로 움직이는 process, 그 memory, 그리고 개인과 세계 사이를 메우는 meso-scale을 붙이는 것이다.  
이와 동시에 external readability를 통해 지금 구조가 실제로 ‘세계처럼 읽히는지’ 확인해야 한다.**
