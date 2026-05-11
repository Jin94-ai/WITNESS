# WITNESS — World Flow 실험-검증 반복 루프 작업지시서

## 0. 문서 목적

이 문서는 WITNESS 프로젝트의 다음 핵심 개발 방법론을 고정하기 위한 작업지시서다.

핵심 방법론은 다음 한 문장으로 요약된다.

> **설계 → 세계가 흐르나 실험 → 잘 흐르나 검증 → 구조 수정**

이 루프를 반복하면서, 개별 인물 handcrafted 중심 개발에서 벗어나 **구조가 이야기를 낳는 세계 엔진**으로 전환한다.

이 문서는 단발성 계획이 아니라, 앞으로의 주요 개발 루프를 정의하는 기준 문서다.

---

## 1. 왜 이 루프가 필요한가

WITNESS의 목표는 특정 인물의 서사를 정교하게 재현하는 것이 아니라,

- 세계가 먼저 움직이고
- 그 안의 인물들이 서로 다른 압력과 위치 속에서 반응하며
- 결과적으로 이야기 같은 흐름이 생겨나는 구조

를 만드는 것이다.

따라서 다음과 같은 방식은 장기 목표와 맞지 않는다.

- 개별 인물 patch 누적
- 개별 action boost 누적
- 특정 canonical scene에 맞춘 수동 튜닝 반복
- “좋은 이야기 하나”를 직접 쓰는 방식

대신 필요한 것은:

1. **세계가 실제로 흐르는가**를 먼저 확인하고
2. 그 흐름이 **좋은 흐름인지 검증**하고
3. 그 결과를 바탕으로 구조를 다시 수정하는

반복 루프다.

---

## 2. 이 루프의 핵심 질문

이 문서가 다루는 핵심 질문은 두 개다.

### 질문 A — 세계가 흐르나?
아래 중 최소 일부가 발생해야 한다.

- 사람 없이도 world state가 변화한다
- 사건이 다른 레이어로 번진다
- 행동이 다시 world를 흔든다
- 이전 사건의 잔향이 남아 다음 가능성 지형을 바꾼다

### 질문 B — 잘 흐르나?
흐름이 있다는 것과 좋은 흐름이라는 것은 다르다.

잘 흐른다는 것은 최소한 다음을 만족해야 한다.

- propagation이 있다
- persistence가 있다
- restructuring이 있다
- divergence가 있다
- boundedness가 있다
- readability가 있다

즉, world가 단순 반응기가 아니라 **구조적 arc를 낳는 시스템**이어야 한다.

---

## 3. 반복 루프의 전체 구조

WITNESS의 world-engine 개발은 아래 5단 루프로 운영한다.

### Loop 1 — Build
구조 수정 및 최소 보강

예:
- world kernel 수정
- coupling 추가/삭제
- motif 구조 조정
- relation memory 조정
- process 엔진 추가
- role-conditioned initialization 정리

### Loop 2 — Run
작은 세계 실행

예:
- micro-world 실행
- seed 여러 개 실행
- trace / provenance 기록
- story probe 생성

### Loop 3 — Detect
흐름 존재 여부 및 유형 판정

예:
- static / reactive / propagating / narrative-generative 분류
- dominant layer 확인
- dead layer 확인
- over-dominant layer 확인

### Loop 4 — Evaluate
흐름 품질 검증

예:
- propagation 점검
- memory 점검
- restructuring 점검
- readability 점검
- patch dependence 점검
- random churn 여부 점검

### Loop 5 — Refine
결과 기반 수정

예:
- coupling 강화/완화
- dead layer process화
- motif 재구성
- role ontology 정리
- memory persistence 조정
- action primitive 재조정

이후 다시 Build로 돌아간다.

---

## 4. 운영 원칙

### 원칙 1 — 큰 구조 추가보다 최소 실행 구조 우선
지금 단계에서는 “더 많은 레이어 / 변수 / 인물 / 시스템”보다, 현재 구조를 작동 가능한 최소 단위로 압축하는 것이 우선이다.

### 원칙 2 — micro-world 실험을 기본 단위로 사용
처음부터 큰 세계를 돌리지 않는다.

기본 단위는 다음 정도를 권장한다.

- 인물 수: 5~12
- 공간 수: 2~4
- role 종류: 3~5
- 주요 process: 3개 내외
- tick 길이: 30~50

### 원칙 3 — 실험과 검증을 분리
- “흐르는가”는 생성 능력 평가
- “잘 흐르는가”는 품질 평가

둘을 섞지 않는다.

### 원칙 4 — 한 번에 하나씩 바꾼다
한 번의 루프에서 구조 변경은 가능한 한 1개 범주만 바꾼다.

예:
- rumor process만 바꿈
- crowd coupling만 바꿈
- motif selection만 바꿈
- recovery persistence만 바꿈

한 번에 5개를 바꾸면 원인 추적이 불가능해진다.

### 원칙 5 — 세계는 사람 없이도 일정 부분 움직여야 한다
agent-independent process가 최소 일부 포함되어야 한다.

예:
- rumor diffusion
- authority vigilance drift
- ritual time pressure
- scarcity accumulation
- public visibility decay

### 원칙 6 — world는 기억을 가져야 한다
실험에서 다음이 없으면 “흐름”으로 보지 않는다.

- 관계 잔향
- shame climate
- authority memory
- rumor residue
- unresolved conflict tail

---

## 5. 흐름 판정 체계

실험 후 현재 world 상태를 아래 4분류 중 하나로 판정한다.

### A. Static world
특징:
- state는 바뀌지만 체감상 세계가 안 움직임
- 사람 로그만 있고 world의 독자적 변형이 약함
- 사건이 누적되지 않음

해석:
- 아직 world engine이 아니라 scene replay 수준

### B. Reactive world
특징:
- 사건이 생기면 반응은 있음
- 하지만 영향이 다음 장면 구조를 거의 못 바꿈
- memory와 propagation이 약함

해석:
- 반응형 무대 수준

### C. Propagating world
특징:
- 한 사건이 다른 레이어로 번짐
- relation / rumor / authority / crowd / pressure가 연결됨
- 잔향이 남고 다음 장면 가능성을 바꿈

해석:
- 최소한 world가 흐른다고 볼 수 있는 상태

### D. Narrative-generative world
특징:
- 전개가 emergent하게 휨
- 구조적 arc가 보임
- 특정 인물 중심이 아니어도 이야기처럼 읽힘
- 반복 실험에서 arc family가 나타남

해석:
- 장기적으로 목표하는 방향

현재 단계 목표는 최소 **C**, 궁극 목표는 **D**다.

---

## 6. “잘 흐름”의 품질 기준

world flow 품질 검증 시 다음 6축을 본다.

### 6.1 Propagation
한 사건이 다른 레이어로 전파되는가

예:
- accusation → shame climate → crowd attention → authority vigilance
- rumor → public exposure → relation damage → later concealment

### 6.2 Persistence
영향이 남는가

예:
- 관계 손상 유지
- unresolved guilt tail
- rumor residue
- public shame climate 유지

### 6.3 Restructuring
세계 지형을 다시 그리는가

예:
- trust network 재배열
- belonging 변화
- group cohesion 변화
- visibility landscape 변화

### 6.4 Divergence
같은 초기 구조에서도 seed에 따라 다른 arc가 가능한가

예:
- conceal cascade
- repair attempt
- relation fracture
- authority clampdown

### 6.5 Boundedness
완전 랜덤이 아니라 구조적 제약 안에서 움직이는가

즉:
- 물리적 불가능이 적다
- social affordance 위반이 낮다
- patch 없이도 plausibility가 유지된다

### 6.6 Readability
나중에 봤을 때 왜 이런 흐름이 생겼는지 설명 가능한가

즉:
- provenance가 기록됨
- dominant process가 식별됨
- key turning point가 설명 가능함

---

## 7. 실험 단위 고정

루프가 누적되려면 매번 비교 가능한 단위를 유지해야 한다.

### 7.1 Micro-world spec 고정
실험 템플릿 예시:

- 인물 수: 8
- role cluster: 4종
- 공간: 3곳
- world process: rumor / authority / crowd
- tick 수: 40
- scenario shock: 1~2개

### 7.2 Story probe format 고정
모든 실험에서 같은 형식으로 출력한다.

필수 항목:
- initial world state summary
- key agents & roles
- dominant pressures by phase
- motif sequence by key agent
- key events
- relation deltas
- world memory summary
- final arc summary

### 7.3 Validation sheet 고정
모든 실험에서 동일한 체크리스트를 사용한다.

필수 항목:
- flow type
- propagation score
- persistence score
- restructuring score
- readability score
- patch dependence warning
- dead layer warning
- over-dominant layer warning

---

## 8. 추천 micro-world 실험 구성

### 8.1 초기 실험 크기
처음 실험은 5~12명 수준의 닫힌 작은 세계로 제한한다.

권장 이유:
- 관계망이 생긴다
- crowd/rumor/authority 같은 meso dynamics가 보인다
- 디버깅 가능하다
- handcraft를 벗어나기 시작한다

### 8.2 구성 예시
- 핵심 agent 2~3명
- peer group 2~4명
- authority 측 1~2명
- crowd proxy 또는 meso-node 1개
- 공간 2~4개
- rumor channel 1개
- authority pressure channel 1개

### 8.3 목표
이 micro-world는 “특정 이야기 재현”이 아니라,

> 작은 사회적 압력과 사건이 관계/정보/권력 지형을 실제로 흔드는가

를 보는 실험장이다.

---

## 9. 실험 종류

처음 반복 루프에서 우선적으로 돌릴 실험은 아래 3종이다.

### Experiment A — Pressure propagation
질문:
같은 world shock가 서로 다른 role / profile에 어떻게 다르게 번역되는가?

예:
- accusation shock
- rumor shock
- authority arrival
- scarcity spike
- sacred signal

관찰 포인트:
- 어떤 pressure가 지배적인가
- 어떤 agent가 어떤 motif로 반응하는가
- world state에 어떤 2차 효과가 생기는가

### Experiment B — Relation restructuring
질문:
한 사건이 관계망을 어떻게 바꾸는가?

예:
- trust 하락
- belonging 변화
- loyalty tension
- peer split
- repair attempt

관찰 포인트:
- relation delta가 다음 tick 행동에 반영되는가
- relation change가 world event 가능성을 바꾸는가

### Experiment C — World memory
질문:
초기 사건이 몇 tick 뒤에도 세계 가능성 지형을 바꾸는가?

예:
- shame climate 지속
- authority vigilance 누적
- rumor residue 유지
- unresolved guilt tail
- public visibility 흔적

관찰 포인트:
- memory가 실제 후속 행동/사건에 영향을 주는가
- 즉시 반응으로 끝나지 않는가

---

## 10. 실험 이후 해야 할 진단

실험 후에는 아래 4종 분석을 반드시 수행한다.

### 10.1 Dominant process 분석
무엇이 흐름을 실제로 만들었는가?

예:
- rumor process 주도
- authority vigilance 주도
- relation fracture 주도
- shame climate 주도

### 10.2 Dead layer 분석
이름은 있으나 실제 영향이 거의 없는 layer/process를 찾는다.

예:
- politics layer 이름만 존재
- space layer 위치 라벨만 존재
- crowd layer가 배경 노드 수준

### 10.3 Over-dominant layer 분석
너무 강해서 나머지를 죽이는 layer/process를 찾는다.

예:
- rumor 하나가 전부 지배
- person emotion만 과도하게 강함
- authority rule이 모든 branching 차단

### 10.4 Arc extraction
story probe 중 arc처럼 보이는 흐름을 3~5개 뽑는다.

예:
- rumor → accusation → conceal → relation split
- shame exposure → withdrawal → belonging collapse → repair failure
- sacred signal → remain_present → public cost → later restoration

이 arc가 어떤 process 조합에서 생겼는지 기록한다.

---

## 11. 수정 방향 결정 규칙

실험과 진단 뒤에는 아래 셋 중 하나만 선택한다.

### Keep
현재 구조를 유지하고 다음 실험으로 넘어간다.

선택 조건:
- propagation이 분명하다
- dead layer가 적다
- patch dependence가 낮다
- readability가 확보된다

### Rollback
이번 구조 변경을 되돌린다.

선택 조건:
- random churn이 심해짐
- readability 악화
- 특정 process가 과도하게 지배
- memory가 망가짐

### Refine
구조 전체는 유지하되 coupling이나 persistence를 조정한다.

선택 조건:
- 흐름은 생기지만 너무 약함
- 흐름은 있는데 산만함
- 특정 process만 약간 조정하면 좋아질 가능성 있음

주의:
**실험 후 반드시 keep / rollback / refine 중 하나를 명시적으로 고를 것.**

---

## 12. 지금 추가해도 되는 것 vs 미뤄야 하는 것

### 12.1 지금 추가 가능
실험을 가능하게 하거나 흐름 검증에 직접 필요한 것만 추가한다.

허용:
- motif mediation
- rumor process
- crowd proxy / meso-node
- authority vigilance process
- world memory / residue tracking
- role-conditioned initialization
- provenance trace
- generic action primitive 정리

### 12.2 지금 미뤄야 하는 것
다음은 아직 이르다.

보류:
- neural policy
- 대규모 population
- 정교한 경제 전체 모형
- full institutional simulation
- universality 주장
- 발견 선언
- 변수/레이어 과도한 추가
- 인물별 patch 누적

---

## 13. 금지 사항

### 금지 1
흐름이 조금 생겼다고 바로 더 큰 세계로 확장하지 말 것.

### 금지 2
실험 없이 구조 문서만 계속 늘리지 말 것.

### 금지 3
story probe가 그럴듯하다고 곧바로 성공으로 판정하지 말 것.

### 금지 4
validation rubric 점수만 잘 나오게 구조를 과적합하지 말 것.

### 금지 5
micro-world에서만 잘 되는 구조를 곧바로 범용 구조라고 부르지 말 것.

### 금지 6
개별 agent fidelity 개선을 위해 direct patch를 계속 추가하지 말 것.

---

## 14. 산출물 규격

한 번의 루프마다 아래 산출물을 남긴다.

### 14.1 실험 명세
- micro-world spec
- active process 목록
- changed coupling 목록
- 실행 seed 목록

### 14.2 story probe
- 3~5개 대표 probe
- key event chain
- key motif chain
- relation 변화 요약
- world memory 변화 요약

### 14.3 flow diagnosis
- flow type 판정
- dominant / dead / over-dominant layer
- patch dependence 여부

### 14.4 refinement decision
- keep / rollback / refine
- 근거
- 다음 루프에서 바꿀 한 가지 요소

---

## 15. 완료 기준 (현재 단계)

현재 단계 완료는 아래 조건을 충족할 때로 본다.

### 완료 조건 1
최소 1개의 micro-world에서 flow type이 **Propagating world(C)** 이상으로 판정된다.

### 완료 조건 2
사건이 relation / rumor / authority / crowd / pressure 중 최소 2개 이상 레이어에 전파된다.

### 완료 조건 3
world memory가 실제 후속 가능성 지형을 바꾸는 사례가 반복적으로 관찰된다.

### 완료 조건 4
story probe에서 arc-like flow 3종 이상이 식별된다.

### 완료 조건 5
dominant/dead/over-dominant layer 분석이 가능하며, 그 결과로 구조 수정이 추적 가능하다.

### 완료 조건 6
실험-검증-수정 루프가 최소 3회 이상 반복되어, 한 번의 lucky output이 아니라 개발 방법론으로 정착한다.

---

## 16. 중기 목표

현재 단계의 다음 목표는 단순 확장이 아니다.

중기 목표는 다음 순서로 간다.

1. world flow confirmation
2. flow diagnosis
3. coupling refinement
4. arc reproducibility 확인
5. 5~12명 → 12~20명 수준 micro-population 확장
6. 다른 시나리오 context에서 transfer 실험

즉:

> **확인 → 진단 → 정제 → 반복 → 확장**

이 순서를 지킨다.

---

## 17. 한 줄 요약

**WITNESS의 B 방향 세계 구축은, “설계 → 세계가 흐르나 실험 → 잘 흐르나 검증 → 구조 수정” 루프를 계속 반복하면서 세계 동학을 발견하고 정제하는 방식으로 발전시킨다.**

조금 더 압축하면:

> **다음 단계는 큰 구조 추가가 아니라, 현재 구조를 world kernel로 압축해 micro-world 실험을 돌리고, 그 흐름을 읽고, 진단하고, 다시 다듬는 반복 루프를 개발 방법론으로 고정하는 것이다.**

