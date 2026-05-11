# WITNESS — 개선안 및 개선 적용 루프 정리

기준 문서:
- WORLD_FLOW_LOOP 결과 요약 (Iter 1-50)
- 약점 분석 및 개선 제안

작성 목적:
- 현재 Iter 1-50 결과를 바탕으로 **잘 안 된 점**을 중심으로 정리한다.
- 그 약점을 해결하기 위한 **구체적 개선안**을 명시한다.
- 개선안이 반영된 상태에서 다음 반복을 어떻게 운영할지 **업데이트된 루프**로 고정한다.

---

## 0. 현재 상태 한 줄 요약

현재 엔진은 다음 수준까지 도달했다.

- 단일 시나리오 replay에서 벗어나 4 scenario, agent-level emergent dynamics, long-horizon limit cycle까지 확인
- C_propagating flow 도달 및 유지 확인
- role priors, rumor amplification, autonomous recovery cascade 등 핵심 구조 요소 발견

하지만 동시에 아래 문제가 남아 있다.

- 개념 프레임이 여러 차례 뒤집힘
- 일부 breakthrough가 구조적 문제처럼 보였으나 실제로는 contract/naming mismatch였음
- role priors finding의 범위가 아직 조건부인지 보편적인지 불명확함
- scenario diversity가 이름 수준인지 topology 수준인지 아직 충분히 분리되지 않음
- external readability 검증이 없음
- limit cycle이 구조적으로 의미 있는 현상인지 artifact인지 아직 불명확함

따라서 다음 단계는 “더 많은 구조 추가”가 아니라:

**해석 안정화 → 핵심 finding 고정 → topology 다양성 검증 → readability 검증 → mixed-arc 검증**

순으로 진행한다.

---

## 1. 현재 잘 안 된 점 정리

### 1.1 해석 레벨 혼동

현재까지의 retraction 중 상당수는 아래 레벨들이 섞여 해석된 결과일 가능성이 크다.

- engine-level dynamics
- agent-level motif / reversal / recovery
- scenario-level aggregate label

예:
- scenario topology로 보던 것이 agent-level emergent로 재해석됨
- arc label을 전체 시나리오 법칙처럼 읽었다가 majority/minority 구성으로 수정됨
- 단일 rise-then-fall로 보던 것이 long-horizon limit cycle로 수정됨

문제:
- 수정이 실제 구조 변화인지, 분석 단위 착각인지 구분이 흐려짐
- 결과 해석의 안정성이 낮아짐

---

### 1.2 schema / event contract 관리 약함

Iter 34의 핵심 breakthrough가 `forgiveness_offered` vs `forgiveness_emitted` mismatch 한 줄 수정에서 나왔다.

문제:
- 30 iter 동안 “구조적으로 어려운 문제”로 오인되었음
- naming mismatch가 emergent path를 가리고 있었음
- 설계 논의가 wiring bug에 의해 오염될 수 있음

---

### 1.3 role priors finding의 과해석 위험

현재 핵심 문장:

> Role identity는 motif_action_priors에 산다 — motif_tendency가 아니다.

이 문장은 중요한 발견 후보이지만, 현재는 여전히 **조건부 설계 법칙 후보**로 봐야 한다.

문제:
- transition scenarios에서는 강하지만 standalone/general case에선 범위가 좁아진 전례가 있음
- priors가 실제 병목인지, pressure / cast / memory와의 상호작용 결과인지 완전히 분리되지 않음

---

### 1.4 scenario diversity의 구조적 증명 부족

현재 4 scenario가 존재하지만, 이미 “3 scenarios → 2 topologies”로 scope narrowing이 일어났다.

문제:
- narrative label은 달라도 실제 state-space topology는 유사할 수 있음
- accusation / scarcity / sacred가 모두 crisis variants일 가능성이 있음
- diversity claim이 topology 수준에서 충분히 잠기지 않음

---

### 1.5 readability 검증 부재

현재 엔진은 통계적/구조적 지표는 강해졌지만, 외부 사람이 읽었을 때:

- arc가 보이는지
- 흐름이 읽히는지
- oscillation이 노이즈처럼 보이지 않는지

에 대한 검증이 없다.

문제:
- “잘 도는 동역학”과 “읽히는 세계”를 혼동할 수 있음

---

### 1.6 limit cycle의 의미 불명확

200-tick에서 3-6 reversals/agent 수준의 limit cycle이 확인되었다.

문제:
- robust한 dynamical regime인지
- 특정 parameter 조합의 artifact인지
- narrative quality를 해치는지
- cycle source가 어디인지

아직 모른다.

---

### 1.7 inert / low-effect component 정리가 미완

일부 coupling / gate / decay는 제거되었지만, 아직도 완전 inert인지 애매한 component가 남아 있다.

예:
- authority_vigilance field 완전 삭제 여부 미결정
- climate_sensitivity는 low-effect로 분류됐다가 support로 재분류됨

문제:
- component ledger가 없으면 불활성 구조가 다시 부활할 수 있음
- kernel / support / inert 경계가 흔들림

---

### 1.8 mixed-arc 검증 부재

현재 발견된 구조는 비교적 “깨끗한” 시나리오 위에서 확인된 경우가 많다.

문제:
- accusation + sacred
- scarcity + private grief
- blame + repair overlap

같은 혼합 압력장에서 기존 발견이 유지되는지 검증되지 않았다.

---

## 2. 개선안

---

### 개선안 A — 분석 단위 분리 고정

#### 목표
해석 레벨 혼동 제거.

#### 조치
모든 분석/보고는 아래 3단 분리 형식을 강제한다.

1. **engine-level**
   - attractor / cycle / equilibrium / propagation depth
2. **agent-level**
   - dominant motif, reversals, recovery, pressure exposure
3. **scenario-level**
   - aggregate label, cast composition, majority/minority dynamics

#### 산출물
- 보고서 템플릿 개정
- 각 실험 결과에 engine/agent/scenario 3분리 섹션 강제

#### 완료 기준
- 향후 summary 문서에서 세 수준을 한 문단에 섞어 해석하지 않음

---

### 개선안 B — event contract linting 도입

#### 목표
naming mismatch / wiring bug를 구조적 한계로 오해하지 않도록 방지.

#### 조치
다음 검사 추가:

- produced but never consumed events
- consumed but never produced events
- alias / near-duplicate event names
- event registry 단일화
- producer-consumer contract test

#### 산출물
- `engine/world/event_registry.py` 또는 동등 기능
- lint script
- contract tests

#### 완료 기준
- event mismatch류가 실험 이후가 아니라 실험 전 lint에서 잡힘

---

### 개선안 C — role priors finding을 ablation으로 잠그기

#### 목표
“role identity는 motif_action_priors에 산다”를 조건부/구조적 finding으로 검증.

#### 조치
최소 4조건 비교:

- no role priors
- weak priors
- current priors
- strong priors

각 조건에서 측정:

- action_JS
- motif occupancy shift
- conditional invariance score
- C_propagating 도달률
- readability proxy

추가로 아래 3축 interaction sweep 수행:

- blame pressure low/med/high
- scarcity pressure low/med/high
- sacred pressure low/med/high

#### 완료 기준
- prior strength에 따른 변화가 계층 병목으로 설명 가능한지 확인
- “priors 단독”이 아니라 “priors × world pressure” 상호작용 그림 확보

---

### 개선안 D — scenario topology fingerprint 비교

#### 목표
scenario diversity를 narrative label이 아니라 구조적 fingerprint로 증명.

#### 조치
각 scenario에 대해 아래 벡터를 계산/비교:

- dominant pressure signature over time
- motif occupancy distribution
- event family composition
- reversal density
- memory tail length
- relation restructuring magnitude

#### 완료 기준
- 4 scenario가 실제로 몇 개 topology로 묶이는지 다시 정의
- “4 scenarios”가 아니라 “N topologies”로 명시 가능

---

### 개선안 E — readability blind evaluation 도입

#### 목표
통계적으로 좋은 흐름이 실제로 읽히는 세계인지 검증.

#### 조치
story probe 12~20개 생성 후, 아래 정보는 숨김:

- scenario label
- seed
- internal metric

외부 평가 질문:

1. 이 로그는 랜덤하게 보이는가, 흐름이 보이는가?
2. 핵심 압력은 무엇으로 읽히는가?
3. 관계/집단 재배열이 느껴지는가?
4. oscillation이 의미 있는 반복처럼 보이는가, 노이즈처럼 보이는가?
5. arc가 있다면 어떤 arc로 읽히는가?

#### 완료 기준
- 내부 metric과 외부 readability 평가 간 상관 또는 불일치 패턴 확보

---

### 개선안 F — limit cycle source 분석

#### 목표
limit cycle이 진짜 regime인지 artifact인지 분리.

#### 조치
측정:

- cycle count per agent
- period distribution
- amplitude stability
- cast perturbation sensitivity
- memory ablation 시 cycle 유지 여부
- prior ablation 시 cycle 유지 여부

가능하면 간단한 phase portrait / recurrence 시각화 추가.

#### 완료 기준
- cycle의 source 후보를 최소 1-2개로 좁힘
- “cycle 있음”이 아니라 “왜 cycle이 생기는가” 설명 가능

---

### 개선안 G — component ledger 작성

#### 목표
kernel / support / inert 구조를 고정하고 drift를 막음.

#### 조치
모든 component를 아래로 분류:

- kernel
- support
- contextual
- inert
- deprecated

각 항목마다 기록:

- 유지 근거
- 주요 기여 scenario
- 제거 시 손실
- 현재 불확실성

#### 완료 기준
- authority_vigilance, climate_sensitivity 같은 구조가 ledger 없이 재해석되지 않음

---

### 개선안 H — mixed-arc scenario 검증

#### 목표
깨끗한 시나리오에서 찾은 발견이 혼합 압력장에서도 유지되는지 확인.

#### 추천 mixed scenarios
1. accusation + sacred overlap
2. scarcity + private grief overlap
3. blame + repair overlap

#### 평가 포인트
- 기존 motif classes 유지 여부
- role priors effect 유지 여부
- propagation depth 변화
- readability 악화/개선 여부

#### 완료 기준
- clean scenario finding이 혼합 상황에서도 일부 유지되는지 확인
- 혼합 상황 전용 failure mode 파악

---

## 3. 개선안이 반영된 업데이트 루프

기존 WORLD_FLOW_LOOP를 아래와 같이 수정한다.

---

### Phase 0 — Pre-Run Structural Audit

실험 전에 반드시 수행.

#### 체크리스트
- event contract lint 통과
- component ledger 최신화
- scenario fingerprint 정의 여부 확인
- 분석 단위(engine/agent/scenario) 분리 템플릿 준비

**이 단계 실패 시 Run 금지.**

---

### Phase 1 — Build

#### 허용되는 수정
- prior strength 조정
- pressure coupling 조정
- memory 구조 조정
- event spawn / feedback 조정
- mixed-arc scenario 추가
- readability probe exporter 추가

#### 금지
- 새 finding을 확인하기 전에 새 레이어 대량 추가
- neural policy 도입
- universality claim
- 사람이 읽기 좋은 story를 위해 metric 없는 patch 추가

---

### Phase 2 — Run

각 iteration batch는 아래 4종을 포함한다.

1. baseline scenario set
2. ablation scenario set
3. long-horizon run (cycle 확인용)
4. readability probe export

최소 실행 단위:
- n seeds 고정
- 동일 cast / variant cast 둘 다
- 30-50 tick short horizon + 200 tick long horizon

---

### Phase 3 — Detect

#### 먼저 판정할 것
현재 변화가 어느 수준에서 나타났는가?

- engine-level change
- agent-level change
- scenario-level change
- none / noise-level

#### flow class 판정
- Static
- Reactive
- Propagating
- Narrative-generative candidate
- Limit-cycle / equilibrium subtype

---

### Phase 4 — Evaluate

평가는 아래 6축으로 한다.

1. **Propagation**
   - 사건이 몇 레이어까지 번졌는가
2. **Persistence**
   - memory tail이 남는가
3. **Restructuring**
   - relation / pressure / event landscape가 재구성되는가
4. **Conditional invariance**
   - role identity와 pressure response가 적절히 공존하는가
5. **Readability**
   - 외부 사람이 흐름을 읽는가
6. **Robustness**
   - seed/cast/ablation 변화에서 finding이 버티는가

추가 진단:
- dead layer
- over-dominant layer
- inert support
- patch dependence

---

### Phase 5 — Decide

각 iteration 또는 batch 끝에서 아래 중 하나만 선택한다.

#### Keep
조건:
- effect가 noise-level 아님
- 해석 레벨이 분리되어 있음
- ablation 또는 fingerprint에서 구조적으로 설명 가능

#### Refine
조건:
- 효과는 있으나 범위/해석이 불명확
- readability 또는 robustness가 부족
- mixed-arc에서 깨짐

#### Rollback
조건:
- 효과가 wiring bug/measurement artifact로 확인됨
- component ledger상 inert 또는 harmful
- external readability를 악화시킴

---

## 4. 다음 진행 우선순위

### 1순위 — 구조 해석 안정화
- 분석 단위 분리
- event contract linting
- component ledger 작성

### 2순위 — prior finding 고정
- prior strength ablation
- pressure interaction sweep
- cast sensitivity test

### 3순위 — topology diversity 재검증
- fingerprint 비교
- 4 scenario → N topologies 재정의

### 4순위 — limit cycle source 분석
- long horizon + ablation
- cycle source 후보 좁히기

### 5순위 — readability blind evaluation
- 외부 독자 or Lee blind check

### 6순위 — mixed-arc scenario
- overlap pressure 환경 실험

---

## 5. 이번 단계에서 하지 말아야 할 것

- universality claim 확대
- finding을 “세계 법칙” 수준으로 말하기
- new variable / new layer 대량 추가
- readability를 맞추려고 임의 patch 누적
- neural policy probe를 현재 약점 정리 전에 본격화

---

## 6. 이번 단계 완료 기준

아래가 충족되면 이번 개선 단계는 완료로 본다.

1. event mismatch류가 lint 단계에서 잡힌다
2. 분석 단위(engine/agent/scenario)가 문서/실험에서 분리된다
3. role priors finding이 ablation 및 interaction 관점에서 조건부 범위까지 명시된다
4. scenario diversity를 topology fingerprint로 다시 정의했다
5. limit cycle의 source 후보가 최소 1-2개로 좁혀졌다
6. external readability blind check 결과가 있다
7. mixed-arc scenario에서 기존 finding이 어디까지 유지되는지 파악했다
8. component ledger가 작성되고 kernel/support/inert가 고정되었다

---

## 7. 한 줄 요약

다음 단계의 핵심은 **새 구조를 더 추가하는 것**이 아니다.

핵심은:

**지금까지 얻은 finding을 해석 안정성, contract 안정성, topology 다양성, readability, robustness 관점에서 다시 잠가서 “진짜 구조적 발견”과 “조건부/국지적 효과”를 분리하는 것**이다.

