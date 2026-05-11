# WITNESS 로드맵 — B 방향(생성 가능한 원리 구축) 기준 상세 실행 계획

## 문서 목적

이 문서는 WITNESS 프로젝트를 **특정 인물/특정 서사를 잘 맞추는 방향(A)** 이 아니라,
**그런 인물과 서사가 발생할 수 있는 생성 원리와 세계 구조를 만드는 방향(B)** 으로
전환하고 실행하기 위한 상세 로드맵이다.

이 문서는 다음 전제를 따른다.

- 목표는 "좋은 이야기 1편"이 아니라 **여러 이야기들이 발생할 수 있는 세계**다.
- Peter/Judas 작업은 최종 목적지가 아니라 **공통 엔진 추출용 프로토타입**이다.
- 앞으로의 핵심은 handcrafted patch 증가가 아니라,
  **shared engine + persona profile + world process + scenario binding** 구조로 가는 것이다.
- 구현의 기준은 개별 인물 fidelity보다 **생성 원리의 범용성**을 우선한다.

---

# 0. 방향 선언

## 0.1 프로젝트 방향

WITNESS의 장기 방향은 다음이다.

> 특정 인물의 장면을 정교하게 재현하는 시뮬레이터가 아니라,
> 인물·집단·제도·정보·공간·시간이 상호작용하면서
> 다양한 trajectory와 story-like flow를 낳는 world engine을 구축한다.

## 0.2 현재까지 작업의 의미 재정의

현재까지의 Peter/Judas 작업은 다음 의미로만 유지한다.

- 인간 반응 구조 추출
- pressure와 state의 연결 방식 검증
- motif 후보 탐색
- relation / target 구조 점검
- rubric의 한계 드러내기
- world-person interface 실험

즉, 지금까지의 작업은 **prototype extraction lab**으로 해석한다.

## 0.3 절대 금지

다음은 장기 방향과 충돌하므로 금지한다.

1. 특정 인물 전용 action boost를 계속 누적하는 것
2. 인물마다 별도 변수 세트를 만드는 것
3. 시나리오마다 새 규칙 뭉치를 만드는 것
4. world를 인물 장면의 배경판처럼 쓰는 것
5. story fidelity 향상을 generative principle 진전으로 착각하는 것

---

# 1. 최종 비전 — 세계는 어떻게 굴러가야 하는가

B 방향에서 세계는 다음 흐름으로 작동해야 한다.

1. **느린 세계 구조**가 존재한다
   - 제도, 자원, 절기, 공간 제약, 정보 비대칭, 집단 긴장
2. 그 구조가 **사건 가능성 지형**을 만든다
   - 어떤 일이 "생기기 쉬운가"를 결정
3. 사건과 환경이 인물에게 **pressure**로 전달된다
4. 인물은 pressure를 profile과 관계망에 따라 다르게 해석한다
5. 해석은 직접 action이 아니라 우선 **response motif**를 만든다
6. motif가 action으로 실현된다
7. action은 다시 event / information / relation / institution / crowd에 영향을 준다
8. 세계는 이 결과를 축적하고, 다음 tick의 가능성 지형이 바뀐다
9. 이 축적을 통해 story-like flow가 emergent하게 생긴다

즉 세계는 “정해진 사건 목록”이 아니라,
**가능성 지형이 계속 바뀌는 process system**이어야 한다.

---

# 2. 전체 단계 개요

이 로드맵은 7개 단계로 나뉜다.

- Phase 1. Prototype 정리
- Phase 2. Persona Engine 고정
- Phase 3. World Process Engine 고도화
- Phase 4. Population Grammar 구축
- Phase 5. Micro-world 생성
- Phase 6. Story Probe 루프 확립
- Phase 7. Neural / Learning 연결 검토

각 단계는 "만들 것", "검증할 것", "넘어가지 말아야 할 선"을 포함한다.

---

# 3. Phase 1 — Prototype 정리

## 3.1 목표

Peter/Judas 작업을 더 정교하게 만드는 것이 아니라,
**무엇이 generic이고 무엇이 scenario-specific인지 명확히 분리**하는 단계다.

## 3.2 핵심 질문

- 현재 구조 중 어느 부분이 shared engine인가?
- 어느 부분이 Peter/Judas patch인가?
- 어떤 변수는 유지할 가치가 있고, 어떤 것은 narrative leakage인가?
- 어떤 direct boost는 motif layer로 올려야 하는가?

## 3.3 작업 항목

### A. generic vs specific 분리 문서화

분류 대상:
- state variables
- pressure formulas
- event list
- action gates
- policy boosts
- recovery edges
- target names
- evaluation heuristics

분류 결과:
- generic core
- scenario binding
- temporary patch
- delete candidate

### B. 현재 prototype의 산출물 보존

Peter/Judas는 삭제하지 말고,
앞으로 generic structure를 검증하는 **contrast benchmark**로 유지한다.

### C. leakage 제거

다음은 적극 제거 또는 강등 대상이다.
- faith_stage 같은 narrative compression variable
- 특정 canonical tick 전용 action shortcut
- scenario 고유명 target

## 3.4 산출물

- `PETER_SPECIFIC_VS_GENERIC.md`
- `JUDAS_SPECIFIC_VS_GENERIC.md`
- `GENERIC_CORE_CANDIDATES.md`

## 3.5 완료 기준

- 현재 시스템의 generic core를 명시적으로 설명할 수 있다
- Peter/Judas 차이를 규칙 뭉치가 아니라 profile / binding 관점으로 재서술할 수 있다

---

# 4. Phase 2 — Persona Engine 고정

## 4.1 목표

“인물 하나 = 규칙 세트” 구조를 버리고,
**공통 persona engine + 인물 profile parameter** 구조로 고정한다.

## 4.2 Persona Engine의 필수 구성

### 1) Shared state ontology

현재 19개 변수는 출발점으로 유지 가능하다.

- scalar 13
  - fear, hope, grief, confusion, joy, anger, awe
  - fatigue, hunger, vitality
  - doubt, resolve, trauma
- target-aware 6
  - love, loyalty, trust, belonging, guilt, shame

단, 이 ontology는 **고정 진리**가 아니라 최소 실행 세트다.
향후 sensitivity 기준으로 줄이거나 바꿀 수 있다.

### 2) Response motif layer

직접 action boost를 금지하고,
scene/state/pressure는 반드시 motif를 경유하게 만든다.

최소 motif 후보:
- conceal
- confess
- withdraw
- remain_present
- confront
- grieve
- seek_repair
- observe_wait

추가 후보:
- protect
- exploit
- attach
- detach

### 3) Generic target-role ontology

고유명 target 제거.

예시 role:
- self
- primary_focus
- intimate_other
- peer_group
- in_group
- out_group
- public_group
- authority_group
- family
- rival
- protected_other

### 4) Persona profile schema

profile은 새 규칙 묶음이 아니라 **parameter vector**다.

필수 축:
- pressure sensitivities
- motif priors
- relation biases
- recovery / decay biases
- ambiguity tolerance
- impulsivity / latency
- authority reactivity
- exposure sensitivity

## 4.3 핵심 질문

- 어떤 차이는 profile에 남기고, 어떤 차이는 world position에서 나오게 할 것인가?
- profile 축은 몇 개까지 허용할 것인가?
- motif는 1-hot인가, mixture인가?
- relation은 scalar만으로 충분한가, 일부는 history summary가 필요한가?

## 4.4 작업 항목

### A. motif 설계
각 motif에 대해 정의:
- 어떤 pressure/state 조합에서 상승하는가
- 어떤 action family로 내려가는가
- 얼마나 지속되는가
- motif 전환 비용이 있는가

### B. policy 3층 분리
정책은 최소한 아래 3단 구조여야 한다.
1. scene recognizer
2. motif activator
3. action selector

### C. profile schema 정의
Peter/Judas는 같은 schema 위에 parameter만 다르게 얹는다.

### D. provenance 추가
각 tick에 기록:
- dominant pressure source
- selected motif
- blocked actions
- winning action reason
- guilt/shame source

## 4.5 산출물

- `RESPONSE_MOTIFS.md`
- `PERSONA_PROFILE_SCHEMA.md`
- `TARGET_ROLE_ONTOLOGY.md`
- `TRACE_PROVENANCE_EXTENSION.md`
- `POLICY_REFACTOR_PLAN.md`

## 4.6 완료 기준

- direct action boost가 motif mediation으로 대체되었다
- Peter/Judas가 같은 schema로 설명된다
- target role이 generic role로 바뀌었다
- 새 인물 추가 시 “새 규칙 세트”가 아니라 “profile + binding”만 요구된다

---

# 5. Phase 3 — World Process Engine 고도화

## 5.1 목표

세계가 인물의 배경판이 아니라,
**사람 없이도 자기 시간으로 굴러가는 process system**이 되게 만든다.

## 5.2 세계 6레이어 재정의

기존 6레이어는 단순 폴더 구성이 아니라,
다음 6축으로 재해석하는 것이 좋다.

### Layer A. Material
- 자원
- 식량
- 건강 환경
- 이동성
- 물류
- 기후/자연 조건

### Layer B. Institutional
- 법
- 제재
- 종교 규범
- 권력 도달 범위
- 행정/군사 질서

### Layer C. Social
- 관계망
- 집단 응집
- 파벌
- 평판
- 군중 clustering

### Layer D. Informational
- rumor
- secrecy
- testimony
- misinterpretation
- propagation delay
- credibility

### Layer E. Symbolic
- sacred salience
- honor/shame climate
- taboo
- identity boundary
- ideological meaning

### Layer F. Temporal-Dynamic
- decay
- accumulation
- delayed effect
- rhythm (day/night, ritual, season)
- path dependence
- tipping point

## 5.3 핵심 질문

- 각 레이어는 state 저장소인가, process engine인가?
- 사람 없이도 state를 갱신하는가?
- action space / information access / cost structure를 바꾸는가?
- time asymmetry를 만드는가?
- 다른 레이어와 강하게 결합하는가?

## 5.4 우선 강화 대상

### A. crowd를 독립 meso-layer로 다루기
군중은 개인의 합이 아니라 phase transition을 가지는 집단 동학이다.

필요 항목:
- crowd density
- emotional contagion
- alignment / fragmentation
- accusation amplification
- blame concentration

### B. rumor / information propagation
필요 항목:
- spread speed
- distortion
- credibility decay
- local clustering
- authority suppression

### C. institution as action-space shaper
제도는 단순 tension 값이 아니라:
- 어떤 action이 위험한가
- 어떤 정보가 차단되는가
- 처벌 기대치가 얼마나 되는가
를 바꿔야 한다.

### D. space as affordance
공간은 좌표가 아니라:
- visibility
- reachability
- escape routes
- crowdability
- authority reach
- sacred proximity
를 제공해야 한다.

### E. time as rhythm
시간은 tick index가 아니라:
- 낮/밤
- fatigue accumulation
- ritual timing
- event afterglow
- punishment latency
- memory decay
를 만들어야 한다.

## 5.5 cross-layer coupling 설계

최소 coupling 예시:
- scarcity -> fatigue / trust erosion / group tension
- rumor -> crowd attention / accusation probability / institutional response
- sacred season -> symbolic pressure / action cost reweighting
- political tension -> authority sensitivity / public accusation likelihood
- spatial density -> information spread / shame exposure

## 5.6 산출물

- `WORLD_LAYER_REDEFINITION.md`
- `WORLD_PROCESSES.md`
- `CROWD_DYNAMICS.md`
- `RUMOR_PROPAGATION.md`
- `SPACE_AS_AFFORDANCE.md`
- `TEMPORAL_RHYTHMS.md`
- `CROSS_LAYER_COUPLINGS.md`

## 5.7 완료 기준

- world는 사람 없이도 일정 부분 굴러간다
- crowd / rumor / institution / space / time 중 최소 3개가 독립 process로 작동한다
- cross-layer coupling으로 world state가 비선형적으로 변한다

---

# 6. Phase 4 — Population Grammar 구축

## 6.1 목표

인물을 한 명씩 설계하지 않고,
**role-conditioned population generation**으로 agent를 생성한다.

## 6.2 핵심 발상

인물은 문서 한 편이 아니라 config 한 개가 되어야 한다.

생성 입력 예시:
- persona profile
- social role
- relation seeds
- initial state
- recent history summary
- world position

## 6.3 Population Grammar 구성

### A. role ontology
예:
- disciple
- fisherman
- priest
- ruler
- outsider
- artisan
- merchant
- soldier
- follower
- crowd member

### B. role priors
각 role에 대한 기본 profile prior를 둔다.

예:
- fisherman: peer dependence 높음, authority distrust 중간 이상
- priest: status preservation 높음, public shame sensitivity 낮음
- follower: belonging need 높음, information uncertainty 높음

### C. archetype library
role과 별개로 reaction archetype을 둔다.

예:
- impulsive
- avoidant
- calculating
- devoted
- shame-sensitive
- authority-sensitive
- repair-oriented
- opportunistic

### D. population initialization recipe
population 생성 시 최소 입력:
- number of agents
- role distribution
- archetype mixture
- initial tension map
- relation density
- initial rumor seeds
- resource conditions

## 6.4 핵심 질문

- role과 archetype은 어떻게 분리할 것인가?
- 어떤 차이는 role에서 오고, 어떤 차이는 archetype에서 오는가?
- 개별 인물 고유성은 어디에서 생기는가?
- 몇 명부터 world-like dynamics가 보이기 시작하는가?

## 6.5 첫 population 규모 권장

처음부터 100명으로 가지 말 것.

권장:
- 5명: 최소 관계 실험
- 8~12명: micro-world 추천
- 20명: 집단 동학 초기 관찰
- 50명+: 나중 단계

## 6.6 산출물

- `ROLE_ONTOLOGY.md`
- `ARCHETYPE_LIBRARY.md`
- `POPULATION_GRAMMAR.md`
- `AGENT_INITIALIZATION_RECIPE.md`

## 6.7 완료 기준

- 새 agent를 “새 규칙 추가” 없이 생성할 수 있다
- 8~12명 micro-world를 자동 초기화할 수 있다
- role + archetype + world position만으로 agent 간 차이가 생긴다

---

# 7. Phase 5 — Micro-world 생성

## 7.1 목표

shared engine과 population grammar가 실제로 world-like flow를 낳는지 확인하기 위해,
**작은 세계를 먼저 만든다.**

## 7.2 권장 micro-world 구성

인원: 8~12명

구성 예시:
- central focus 1
- close followers 2~3
- uncertain followers 2
- authority-side actors 1~2
- crowd-like agents 2~4

world setting 포함:
- sacred event pressure
- authority tension
- rumor seeds
- crowd density variation
- limited movement space
- public vs private zones

## 7.3 목적

이 단계의 목적은 “좋은 story”가 아니다.

목적은 다음이 자연스럽게 나타나는지 확인하는 것이다.
- information flow
- relation reconfiguration
- pressure propagation
- crowd response
- institutional reaction
- alternative trajectories

## 7.4 봐야 할 emergent patterns

- rumor -> crowd -> authority reaction
- public shame -> relation realignment
- scarcity -> concealment increase
- sacred salience -> costly confession or presence
- repeated exposure -> withdrawal / collapse / repair divergence

## 7.5 산출물

- micro-world scenario specs 2~3개
- trajectory logs
- world-state evolution report
- relation-network evolution snapshots

## 7.6 완료 기준

- 주인공 한 명을 직접 몰아가지 않아도 흐름이 생긴다
- 한 agent를 빼도 world process가 유지된다
- world state가 action의 단순 배경이 아니라 실제 driver로 보인다

---

# 8. Phase 6 — Story Probe 루프 확립

## 8.1 목표

구조 우선 개발이 추상 설계로만 끝나지 않게,
**짧은 story probe를 반복적으로 뽑아 구조를 검증**한다.

## 8.2 Story Probe란

story probe는 완성 서사가 아니다.
구조가 어떤 흐름을 낳는지 보기 위한 짧은 trajectory 샘플이다.

예:
- 20~40 tick
- 1개 장면 or 짧은 국면
- 주요 pressure / motif / relation 변화 관찰

## 8.3 Story Probe 점검 기준

### A. 구조적 기준
- 사건이 가능성 지형에서 자연 발생했는가?
- world process가 실제로 영향을 줬는가?
- action이 다시 world를 바꿨는가?

### B. 인물 기준
- profile 차이가 반응 차이로 나타나는가?
- 같은 장면에서 서로 다른 motif가 나오는가?
- handcrafted patch 없이 그럴듯한가?

### C. 서사 기준
- 흐름이 너무 평평하지 않은가?
- 너무 랜덤하지 않은가?
- 작은 전환점이 있는가?
- 결과적으로 story-like pattern이 읽히는가?

## 8.4 운영 방식

개발 루프는 다음을 반복한다.

1. 구조 수정
2. 3~10개 story probe 생성
3. probe 검토
4. 구조 재조정
5. 다시 probe 생성

즉 “구조 우선 + 이야기로 검증” 방식으로 간다.

## 8.5 산출물

- `STORY_PROBE_PROTOCOL.md`
- probe batch examples
- probe evaluation checklist

## 8.6 완료 기준

- 구조 수정이 probe 결과에 어떤 차이를 만드는지 읽을 수 있다
- probe를 통해 random log와 meaningful flow를 구분할 수 있다

---

# 9. Phase 7 — Rubric 재설계

## 9.1 목표

기존 rubric이 canonical / alternative / noise를 제대로 못 가르는 문제를 해결하고,
나중엔 population/world-level 평가까지 확장 가능한 구조를 만든다.

## 9.2 현재 문제 요약

- canonical-like의 character composite가 가장 낮음
- alternative와 noise가 drift로 분리 안 됨
- causal smoothness가 구분력 없음
- novelty가 canon_drift 재사용이라 독립성 없음

## 9.3 재설계 방향

### A. character critic 분리
- character consistency
- scene response fit

### B. context-break critic 신설
- affordance violation
- motive-action mismatch
- physical implausibility
- scene mismatch

### C. novelty 재정의
canon에서 얼마나 먼지가 아니라,
**structured deviation**인지 본다.

### D. world-level 평가 예비 설계
향후 평가 축:
- character-level
- scene-level
- trajectory-level
- population-level
- world-level

## 9.4 reference set 운영

reference trajectories는 calibration용이며,
gold truth로 절대화하지 않는다.

필요한 세트:
- canonical-like
- plausible alternative
- obvious noise

그리고 각 세트 내부 품질도 human sanity check를 거친다.

## 9.5 산출물

- `RUBRIC_REDESIGN.md`
- `REFERENCE_SET_POLICY.md`
- `WORLD_LEVEL_EVALUATION_SKETCH.md`

## 9.6 완료 기준

- canonical / alternative / noise가 threshold 이동만으로가 아니라 critic 구조로 분리된다
- world-level evaluation 확장 방향이 문서화된다

---

# 10. Phase 8 — Neural / Learning 연결 (후순위)

## 10.1 목표

neural component를 붙이더라도,
현재 rule-based fallback과 generic structure를 유지한 채 제한적으로 연결한다.

## 10.2 원칙

neural을 policy 전체 대체로 먼저 쓰지 말 것.

우선순위:
1. motif arbitration
2. profile inference
3. pressure combination smoothing
4. action selection 보조

즉 neural은 먼저 **중간층 보조기**로 들어와야 한다.

## 10.3 금지

- 현재 handcrafted patch를 black-box가 그냥 근사하는 방향
- direct action imitation을 곧바로 목표로 삼는 것
- fallback 없는 full neural 전환

## 10.4 완료 기준

- neural이 구조를 덮어쓰지 않고 보조한다
- rule-based fallback이 유지된다
- 해석 가능성이 크게 깨지지 않는다

---

# 11. 단계별 의사결정 우선순위

## 11.1 가장 먼저 결정할 것

1. 무엇이 profile에 남고 무엇이 world-generated difference가 될 것인가
2. motif를 어떤 구조로 둘 것인가
3. target-role ontology를 generic하게 어떻게 잡을 것인가
4. action vocabulary를 primitive와 realized action으로 나눌 것인가
5. world 6-layer 중 어떤 것부터 process engine으로 승격할 것인가

## 11.2 나중에 결정할 것

- neural policy 연결 시점
- 대규모 population scale
- 고급 world-level 평가 자동화

---

# 12. 하지 말아야 할 것

1. Peter fidelity가 오른다고 generic progress라고 판단하지 말 것
2. Judas를 Peter처럼 retune하지 말 것
3. world layer를 카테고리 저장소로만 두지 말 것
4. relation을 값만 늘려서 해결하려 하지 말 것
5. profile 축을 무한정 늘리지 말 것
6. story probe 없이 추상 구조만 계속 설계하지 말 것
7. reference trajectories를 절대 기준으로 오해하지 말 것

---

# 13. 권장 실행 순서 (실전 버전)

## Step 1
Phase 1 완료
- generic vs specific 문서화

## Step 2
Phase 2 시작
- motif layer
- generic target roles
- persona profile schema
- provenance

## Step 3
Phase 3 중 우선 3개만 강화
- rumor
- crowd
- space affordance

## Step 4
8~12명 micro-world 생성 가능하게 population grammar 구축

## Step 5
story probe 루프 돌리기
- 좋은 story를 뽑으려 하지 말고
- 구조가 어떤 흐름을 낳는지 보기

## Step 6
rubric 재설계
- alternative / noise 분리 축 보강

## Step 7
그 다음에만 neural 보조 검토

---

# 14. 최종 완료 조건

이 로드맵의 장기 완료 조건은 아래와 같다.

1. 인물 하나를 새 규칙 세트 없이 생성할 수 있다
2. 세계는 사람 없이도 일정 부분 굴러간다
3. crowd / rumor / institution / space / time 중 최소 4개가 독립 동학을 가진다
4. story probe에서 story-like flow가 반복적으로 나온다
5. 특정 인물 없이도 micro-world가 의미 있는 dynamics를 보인다
6. Peter/Judas는 handcrafted exemplar가 아니라 generated agent의 검증 기준으로 남는다
7. evaluation이 character-level을 넘어 population/world-level까지 확장된다

---

# 15. 한 줄 요약

> WITNESS의 다음 단계는 특정 인물을 더 정교하게 맞추는 것이 아니라,
> shared persona engine, world process engine, population grammar, story probe loop를 구축하여
> 이야기들이 발생할 수 있는 생성 가능한 세계를 만드는 것이다.

