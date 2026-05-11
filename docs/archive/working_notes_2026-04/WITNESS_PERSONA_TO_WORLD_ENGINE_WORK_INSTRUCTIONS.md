# WITNESS 작업지시서
## Peter 중심 프로토타입에서 Persona Engine, Population Engine, World Engine으로 전환

**문서 목적:**
이 문서는 지금까지의 Peter/Judas 기반 실험, persona engine 논의, motif layer 논의, target-role ontology 논의, world 6-layer 논의를 하나의 실행 지시서로 통합한 것이다. 목표는 더 이상 개별 인물을 handcraft하는 방식에 머물지 않고, **공통 엔진 + 인물 프로파일 + 역할(role) + 세계 맥락(world context)** 기반으로 확장 가능한 구조로 전환하는 것이다.

**핵심 결론:**
- Peter v3 작업은 **최종 제품**이 아니라 **공통 구조 추출용 프로토타입**이다.
- 앞으로의 핵심은 **Peter를 더 잘 맞추는 것**이 아니라, Peter에서 **일반화 가능한 인간 반응 구조**를 추출하는 것이다.
- 인물은 장기적으로 **문서 1개**가 아니라 **config 1개** 수준으로 세팅 가능해야 한다.
- 세계는 사람만으로 돌아가지 않으므로, **비인간적 동학(agent-independent dynamics)** 과 **cross-layer coupling** 이 포함되어야 한다.
- 레이어 수보다 중요한 것은 각 레이어가 **정적 카테고리**가 아니라 **독립 동학(process)** 과 **다른 레이어와의 결합 규칙**을 가지는가이다.

---

# 0. 이번 전환의 최상위 목표

## 0.1 목표 재정의
기존의 암묵적 목표는 다음과 같았다.

- Peter를 canonical하게 잘 움직이게 만들기
- Judas도 동일한 엔진에서 돌아가게 만들기
- rubric으로 canonical / alternative / noise를 구분하기

이 목표는 중간 단계로는 유효했지만, 최종 목표인 **세계 구축**에는 직접 연결되지 않는다.

이번 전환 이후의 목표는 다음과 같다.

> **"공통 persona engine 위에 persona profile, social role, relation template, world context를 얹어서 다양한 agent를 생성할 수 있게 한다."**

그리고 장기적으로는:

> **"사람 하나하나를 설계하는 대신, population grammar와 world process를 통해 다양한 agent population과 trajectory를 생성한다."**

---

# 1. 핵심 원칙

## 원칙 1 — 개별 인물 전용 패치 누적 금지
다음 유형은 더 이상 최종 구조로 확대하지 않는다.

- `accusation_fresh -> deny +8.0`
- `eye_contact_fresh -> weep +6.0`
- `restoration_fresh -> confess +6.0`
- 특정 canonical tick에 맞춘 direct action boost
- 특정 인물의 서사에만 맞는 hardcoded response bias

이런 항목은 **임시 patch** 로 남길 수는 있지만, 전부 **교체 대상**으로 분류한다.

## 원칙 2 — 공통 엔진 + 인물 프로파일 구조로 전환
앞으로 인물은 새 변수 세트와 새 규칙 세트로 정의하지 않는다.

인물은 다음 4개로 정의한다.

1. shared persona engine
2. persona profile schema
3. social role binding
4. world-context instantiation

## 원칙 3 — Peter/Judas는 prototype extraction 대상으로 취급
Peter/Judas 작업의 목적은:
- 더 정밀한 canonical fit
- 더 많은 direct tuning

이 아니라:
- 어떤 pressure가 중요한가
- 어떤 response motif가 필요한가
- 어떤 profile parameter가 인물 차이를 설명하는가
- 어떤 target-role ontology가 충분한가

를 추출하는 것이다.

## 원칙 4 — 변수 ontology는 유지, 움직임 규칙은 리팩토링
현재 19개 변수 세트는 일단 유지한다. 문제는 변수 이름 자체보다:
- pressure -> state edges
- state -> action 연결 방식
- target semantics
- action 후폭풍 계산
- recovery / decay 구조

에 있다.

## 원칙 5 — 세계는 사람만으로 돌아가지 않는다
world engine은 사람의 행동만으로 움직이는 배경판이 되면 안 된다.
반드시 다음 세 종류의 동학을 포함해야 한다.

1. **human-driven dynamics**
2. **structure-driven dynamics**
3. **environment-driven dynamics**

## 원칙 6 — 레이어는 주제 분류가 아니라 process 엔진이어야 한다
정치/경제/문화/군중/공간/개입 같은 폴더 구조만으로는 세계가 살아나지 않는다.
각 레이어는 다음을 가져야 한다.

- state
- process
- shock
- slow variable
- decay / accumulation
- coupling rule

## 원칙 7 — population-level generation을 목표로 한다
장기 목표는 "다음 인물 한 명을 어떻게 설계할까"가 아니다.
장기 목표는:

> **"어떤 role cluster와 persona profile prior를 통해 agent population을 자동 생성할까"**

이다.

---

# 2. 현재 기반으로 인정하는 것

## 2.1 유지할 수 있는 기존 구조
현재까지 만든 구조 중 유지 가치가 높은 것:

- world -> primitive -> pressure -> person state -> action -> event 폐루프
- availability gate 구조
- target-aware relation 구조
- decay / recovery 구조
- action -> event feedback 구조
- rubric / evaluator 분리
- Active 19 state ontology

## 2.2 현재 Active 19 변수 (유지)

### Scalar 13
- fear
- hope
- grief
- confusion
- joy
- anger
- awe
- fatigue
- hunger
- vitality
- doubt
- resolve
- trauma

### Target-aware 6
- love[target]
- loyalty[target]
- trust[target]
- belonging[target]
- guilt[target]
- shame[target]

이 세트는 **최종 완성**은 아니더라도 **공통 엔진의 초기 상태공간**으로 유지 가능하다.

---

# 3. 이번 작업의 최종 산출물

이번 전환 작업의 최종 산출물은 아래 9개다.

1. `PETER_SPECIFIC_VS_GENERIC.md`
2. `RESPONSE_MOTIFS.md`
3. `POLICY_REFACTOR_PLAN.md`
4. `TARGET_ROLE_ONTOLOGY.md`
5. `PERSONA_PROFILE_SCHEMA.md`
6. `TRACE_PROVENANCE_EXTENSION.md`
7. `PETER_JUDAS_CONTRAST.md`
8. `WORLD_ENGINE_REFRAMED_6_LAYER.md`
9. `POPULATION_GENERATION_GRAMMAR.md`

---

# 4. 전체 작업 흐름

전체 작업은 세 축으로 진행한다.

## 축 A — Persona Engine 정리
Peter/Judas prototype에서 공통 인간 반응 구조를 추출

## 축 B — Population/Role 구조 설계
개별 인물 대신 role cluster와 profile prior로 agent population 생성 가능하게 설계

## 축 C — World Engine 재정의
6-layer world를 정적 분류가 아니라 process engine으로 재정의하고, 사람 없이도 돌아가는 비인간 동학을 명확히 함

---

# 5. Step A — Peter-specific와 Generic 구조 분리

## 목적
현재 구현에서 어떤 부분이 shared engine이고, 어떤 부분이 Peter patch인지 분리한다.

## 작업
현재 person loop, state transition, policy retune, action selection, target naming, recovery edges를 전수 점검하여 아래 3분류를 만든다.

### A-1. Generic
모든 인물에 공통으로 남길 수 있는 구조

예:
- pressure 계산 인터페이스
- availability gate 인터페이스
- action -> event feedback 인터페이스
- target-aware variable 구조
- decay / recovery 인터페이스

### A-2. Peter-specific
Peter canonical sequence에 직접 맞춘 patch

예:
- accusation_fresh -> deny boost
- eye_contact_fresh -> weep boost
- restoration_fresh -> confess boost
- disciples / followers 등 특정 타겟 명칭
- Peter canonical tick에 맞춘 특수 attenuation

### A-3. Ambiguous
지금은 generic처럼 보이지만 사실 Peter 편향일 수도 있는 것

예:
- 특정 recovery edge 강도
- guilt/shame semantics 일부
- denial 이후 guilt delta의 크기

## 산출물
`docs/persona_engine/PETER_SPECIFIC_VS_GENERIC.md`

## 완료 기준
- 최소 30개 이상의 규칙/구조 항목을 점검했다.
- 각 항목이 Generic / Peter-specific / Ambiguous 중 하나로 분류됐다.
- Peter-specific 항목마다 **교체 우선순위**가 붙었다.

---

# 6. Step B — Response Motif Layer 설계

## 목적
현재 direct action boost 구조를 없애고, 중간층으로 **response motif** 를 도입한다.

## 배경
현재 구조:
- scene cue -> specific action boost

문제:
- 시나리오 편향이 큼
- 다른 인물로 일반화하기 어려움
- 하드코딩 느낌이 강함

바꿀 구조:
- scene cue / pressure / state
- -> response motif activation
- -> action selection

## 최소 motif 세트
초기 motif 후보는 아래 8개로 제한한다.

1. conceal
2. confess
3. withdraw
4. remain_present
5. confront
6. grieve
7. seek_repair
8. observe_wait

처음부터 12개 이상으로 늘리지 말 것.

## 각 motif에 대해 정의할 것
- motif 정의
- 활성화 조건
- 억제 조건
- 관련 pressure
- 관련 state
- 대표 action 후보
- Peter/Judas에서의 발현 차이
- alternative/noise 구분에서의 의미

## 예시
### conceal
- accusation, shame_exposure, social_threat 상승 시 활성화
- action 후보: deny, stay_hiding, follow_at_distance

### grieve
- guilt, grief, loss cue, eye_contact, restoration failure 등에서 활성화
- action 후보: weep, withdraw, silence-like action

### seek_repair
- guilt 높고 hope / trust / belonging이 완전히 무너지지 않았을 때 활성화
- action 후보: confess, return_token, reconcile-like action

## 산출물
`docs/persona_engine/RESPONSE_MOTIFS.md`

## 완료 기준
- motif 8개가 모두 정의되었다.
- 각 motif에 action 후보가 최소 2개 이상 연결되었다.
- Peter-specific direct boost를 motif boost로 치환할 수 있는 매핑이 최소 5개 제시되었다.

---

# 7. Step C — Policy를 motif mediation 구조로 리팩토링

## 목적
직접 action 선택을 scene patch로 조정하는 구조를 버리고,
**scene recognizer -> motif activator -> action selector** 3단 구조로 리팩토링한다.

## 새 구조
### C-1. Scene recognizer
현재 장면을 인식한다.
예:
- accusation scene
- eye_contact scene
- restoration scene
- crowd pressure scene
- betrayal/remorse scene
- fatigue/vigil scene

### C-2. Motif activator
scene + pressure + state + profile 기반으로 motif activation score를 만든다.

### C-3. Action selector
활성화된 motif 안에서 availability gate를 통과한 action 중 하나를 선택한다.

## 금지
- scene cue에서 action으로 바로 꽂는 direct boost를 계속 늘리지 말 것

## 산출물
- 코드 리팩토링
- `docs/persona_engine/POLICY_REFACTOR_PLAN.md`

## 완료 기준
- direct action boost 50% 이상이 motif boost로 대체되었다.
- Peter와 Judas가 동일한 motif vocabulary를 공유한다.
- action score 계산에서 motif layer가 명시적으로 드러난다.

---

# 8. Step D — Generic target-role ontology 설계

## 목적
현재 Peter 친화 target 명칭을 generic social-role로 재정의한다.

## 배경
현재 일부 target는 특정 시나리오에 너무 가까움.
예:
- twelve_disciples
- broader_followers
- primary_figure

이 구조는 Peter/Judas에선 편하지만 world-level 확장엔 불리하다.

## 새 generic role 후보
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
- sacred_focus
- patron

## 작업
현재 target-aware 변수 6개에 대해, 어떤 target role들이 실제로 필요한지 재정의한다.

### 예시
- love[intimate_other]
- trust[authority_group]
- shame[public_group]
- guilt[primary_focus]
- belonging[in_group]

## content binding 규칙
구체 인물/집단 이름은 engine에 넣지 않는다.
반드시 scenario content에서 binding 한다.

예:
Peter scenario:
- `primary_focus = Jesus`
- `peer_group = disciples`
- `public_group = courtyard crowd`

Judas scenario:
- `primary_focus = Jesus`
- `authority_group = priests`
- `peer_group = disciples`

## 산출물
`docs/persona_engine/TARGET_ROLE_ONTOLOGY.md`

## 완료 기준
- 기존 target 이름 중 scenario-specific 용어가 generic role로 치환되었다.
- target role의 최소/최대 세트가 정의되었다.
- content binding 예시가 Peter/Judas 두 시나리오에 대해 작성되었다.

---

# 9. Step E — Persona Profile Schema 설계

## 목적
인물 차이를 새 변수/새 규칙이 아니라 **공통 엔진 위의 파라미터 벡터**로 표현한다.

## 구조
### E-1. Pressure sensitivity
- social_threat_sensitivity
- shame_exposure_sensitivity
- loyalty_pull_sensitivity
- uncertainty_sensitivity
- isolation_pressure_sensitivity
- sacred_salience_sensitivity

### E-2. Motif prior / action tendency
- conceal_tendency
- confess_tendency
- confront_tendency
- withdraw_tendency
- grief_expression_tendency
- repair_tendency
- observe_wait_tendency
- presence_tendency

### E-3. Recovery / decay bias
- fear_recovery_rate
- guilt_decay_rate
- grief_tail_strength
- confusion_decay_rate
- trust_restoration_bias
- shame_persistence
- trauma_reactivation_bias

### E-4. Relation bias
- primary_focus_attachment_strength
- peer_dependence
- public_exposure_sensitivity
- authority_reactivity
- belonging_need
- status_concern

### E-5. Tempo / style
- impulsivity
- deliberation_bias
- ambiguity_tolerance
- volatility
- persistence

## 작업
Peter와 Judas를 같은 schema 위에 올려 profile 초안을 작성한다.
필요 시 archetype-like intermediate abstraction도 작성한다.

## 산출물
`docs/persona_engine/PERSONA_PROFILE_SCHEMA.md`

## 완료 기준
- profile 파라미터가 최소 20개 축으로 정리되었다.
- Peter/Judas profile이 같은 schema 위에 기술되었다.
- 새 인물 추가 시 새 규칙이 아니라 profile initialization으로 시작할 수 있는 형태가 되었다.

---

# 10. Step F — Trace provenance 기록 확장

## 목적
변수 수를 늘리지 않고 해석 가능성을 높인다.

## 작업
각 tick에 아래 provenance를 기록한다.

- dominant_pressure_source
- secondary_pressure_source
- dominant_state_shift_reason
- guilt_source
- shame_source
- selected_scene
- selected_motif
- blocked_actions
- winning_action_reason
- recovery_source

## 예시
- `dominant_pressure_source = accusation`
- `guilt_source = betrayal`
- `shame_source = public_exposure`
- `selected_scene = accusation_scene`
- `selected_motif = conceal`
- `blocked_actions = [run_to_tomb, jump_into_sea]`
- `winning_action_reason = conceal high + deny available`

## 산출물
- trace schema 확장
- `docs/persona_engine/TRACE_PROVENANCE_EXTENSION.md`

## 완료 기준
- 새로운 trace fields가 추가되었다.
- 최소 5개 trajectory에 대해 provenance가 사람 읽기 가능한 수준으로 출력된다.
- misclassification 분석 시 provenance만으로 1차 진단이 가능해진다.

---

# 11. Step G — Peter/Judas contrast bench 분석

## 목적
Judas를 retune 대상이 아니라, policy 일반화 실패를 드러내는 contrast bench로 사용한다.

## 작업
Peter와 Judas에 대해 아래 비교표를 만든다.

- 공통 motif
- Peter 우세 motif
- Judas 우세 motif
- 공통 pressure reaction
- profile 차이
- 현재 엔진이 못 설명하는 차이
- direct patch가 개입하는 구간
- generic schema로 흡수 가능한 차이
- scenario-specific content로 남겨야 할 차이

## 산출물
`docs/persona_engine/PETER_JUDAS_CONTRAST.md`

## 완료 기준
- Peter/Judas의 차이가 변수셋 차이가 아니라 profile/motif 차이로 설명된다.
- Judas retune 없이도 무엇이 부족한지 구조적으로 설명 가능해진다.

---

# 12. Step H — Population Grammar 설계

## 목적
개별 인물 handcraft를 중단하고, population-level agent generation 규칙으로 넘어간다.

## 핵심 질문
"다음 인물을 어떻게 설계할까?"가 아니라,

> **"어떤 role cluster와 persona prior를 통해 세계 안의 agent population을 생성할까?"**

## 작업
role cluster를 정의한다.

### 예시 role cluster
- fisher / laborer
- disciple / follower
- priest / authority
- merchant
- outsider
- family anchor
- crowd participant
- soldier / enforcer
- elite strategist

## 각 role cluster마다 정의할 것
- 기본 profile prior
- relation template
- likely pressures
- common affordances
- info access level
- resource constraints
- sanction exposure

## 산출물
`docs/world_engine/POPULATION_GENERATION_GRAMMAR.md`

## 완료 기준
- 최소 6개 이상의 role cluster가 정의되었다.
- 각 role cluster가 profile prior와 relation template를 가진다.
- 새 agent를 "role + profile perturbation + world context" 로 instantiate할 수 있다.

---

# 13. Step I — World Engine 6-layer 재정의

## 목적
기존 6-layer 구조를 단순 카테고리가 아니라 **독립 동학 + cross-layer coupling** 구조로 재정의한다.

## 핵심 입장
6레이어는 숫자상 부족하다고 단정할 수는 없지만,
단순한 폴더 분류 수준이면 세계의 다양함을 표현하기에 부족하다.

따라서 6-layer는 다음과 같이 **process-oriented** 로 재정의한다.

## 제안 6-layer
### Layer 1. Material layer
- 자원
- 생산/소비
- 이동성
- 환경 제약
- 질병/기후

### Layer 2. Institutional layer
- 법
- 권력
- 종교 제도
- 처벌 기대
- 제도 관성

### Layer 3. Social layer
- 가족
- 파벌
- 공동체
- 평판
- 군중 구조

### Layer 4. Informational layer
- 소문
- 비밀
- 왜곡
- 신뢰도
- 정보 지연

### Layer 5. Symbolic layer
- 명예
- 수치
- 신성
- 정체성
- 규범
- 금기

### Layer 6. Temporal-dynamic layer
- 누적
- decay
- seasonal rhythm
- event residue
- tipping point
- path dependence

## 각 layer마다 반드시 정의할 것
- stored state
- update process
- shock input
- slow variable
- decay / accumulation rule
- 타 레이어와의 coupling
- human-independent update 가능 여부

## 산출물
`docs/world_engine/WORLD_ENGINE_REFRAMED_6_LAYER.md`

## 완료 기준
- 각 레이어가 단순 데이터 저장소가 아니라 process를 가진다.
- 각 레이어가 사람 없이도 일정 부분 world state를 바꿀 수 있다.
- 각 레이어가 2개 이상의 다른 레이어와 coupling rule을 가진다.

---

# 14. Step J — Cross-layer coupling 표준화

## 목적
레이어 수보다 더 중요한 cross-layer coupling을 명시한다.

## 작업
최소 20개 coupling rule을 정의한다.

### 예시
- economy pressure -> family tension 상승
- public rumor intensity -> accusation probability 상승
- institutional fear -> public denial likelihood 간접 상승
- crowd density -> information diffusion acceleration
- sacred calendar period -> sacred_salience baseline 상승
- resource scarcity -> group cohesion 저하
- authority presence -> action affordance 축소
- space bottleneck -> public visibility 상승
- public humiliation -> shame residue 장기화

## 산출물
`docs/world_engine/CROSS_LAYER_COUPLINGS.md`

## 완료 기준
- coupling 20개 이상
- human-driven / structure-driven / environment-driven 분류 포함
- coupling마다 source layer, target layer, expected effect가 기록됨

---

# 15. Step K — Agent initialization recipe 설계

## 목적
새 인물 하나를 handcraft 문서 없이 world에 꽂을 수 있는 최소 입력 템플릿을 만든다.

## 최소 입력 예시
1. persona profile
2. role cluster
3. relation seeds
4. initial state seed
5. recent history summary
6. faction / institution affiliation
7. information access level

## 출력
- agent config JSON schema
- scenario binding example

## 산출물
`docs/world_engine/AGENT_INITIALIZATION_RECIPE.md`

## 완료 기준
- Peter/Judas 외의 임의 agent 3명을 손으로 문서 작성 없이 config 수준으로 초기화할 수 있다.

---

# 16. Step L — Rubric 재설계 방향 연결

## 목적
reference set 평가에서 드러난 문제를 persona/world 전환 구조와 연결한다.

## 현재 문제 요약
- canonical의 character_composite가 가장 낮음
- alternative와 noise drift 분리 실패
- causal smoothness 구분력 약함
- novelty critic 독립성 없음

## 방향
rubric은 distance 중심에서 벗어나 아래 축을 강화해야 한다.

### L-1. scene_response_fit
장면에 적합한 반응군인가

### L-2. character_consistency
관계/반응/회복 패턴이 일관적인가

### L-3. context_break_score
물리적/맥락적/사회적 affordance 위반이 있는가

### L-4. structured_novelty
그 차이가 무작위가 아니라 의미 있는 branching인가

## 산출물
`docs/rubric/RUBRIC_PHASE_H_REDIRECTION.md`

## 완료 기준
- persona/world 리팩토링이 rubric 재설계 방향과 연결된다.
- 평가 기준이 scene-fit / character-fit / context-break 쪽으로 이동한다.

---

# 17. 하지 말아야 할 것

## 금지 1 — Peter direct patch 추가 금지
canonical fit 향상을 위해 direct action boost를 더 추가하지 말 것.

## 금지 2 — 인물마다 새 변수 세트 정의 금지
Peter 변수, Judas 변수, Van Gogh 변수 따로 정의하지 말 것.

## 금지 3 — target 이름에 고유명 고착 금지
`jesus`, `disciples`, `courtyard crowd` 같은 이름을 engine ontology로 올리지 말 것.

## 금지 4 — 더 맞는 결과 = 더 좋은 구조로 착각 금지
Peter 점수가 올라가도 genericity가 깨졌으면 후퇴다.

## 금지 5 — neural policy로 조기 도피 금지
motif layer, target-role ontology, persona profile schema 없이 neural로 가면 현재 patch 구조를 부드럽게 근사하는 데 그칠 위험이 크다.

## 금지 6 — population 단계 전에 다시 인물 handcraft 확장 금지
새 인물을 추가할 때 문서 분량이 Peter급으로 늘어나는 방식은 중단한다.

---

# 18. 자율 결정 가능 / Lee 승인 필요 / 절대 단독 결정 금지

## 18.1 자율 결정 가능
- motif 이름 초안
- profile parameter 축 초안
- generic target-role naming 초안
- role cluster 초안
- provenance field naming
- cross-layer coupling 후보 수집

## 18.2 Lee 승인 필요
- Peter-specific patch 제거 우선순위
- motif vocabulary 확정
- target-role ontology 최종 naming
- persona profile schema 최종 축
- world 6-layer 재정의 최종 버전
- role cluster 최종 목록
- rubric redesign의 평가 철학

## 18.3 절대 단독 결정 금지
- 신학 해석이 개입되는 canonical semantics 변경
- Rule #13 의미 변경
- threshold 철학 변경
- universality 주장
- world layer의 존재론적 축 최종 확정
- 대규모 neural transition 시작 선언

---

# 19. 우선순위

## 1순위
- Step A Peter-specific vs Generic 분리
- Step B Response Motif Layer 설계
- Step C Policy motif mediation 리팩토링

## 2순위
- Step D Generic target-role ontology
- Step E Persona profile schema
- Step F Provenance 기록 확장

## 3순위
- Step G Peter/Judas contrast bench 분석
- Step H Population grammar 설계

## 4순위
- Step I 6-layer world 재정의
- Step J cross-layer coupling 표준화
- Step K agent initialization recipe

## 5순위
- Step L rubric redesign 연결

---

# 20. 완료 기준

이번 전환 작업의 완료는 다음 조건을 만족할 때로 본다.

## 완료 조건 1
direct action boost 중심 구조가 motif mediation 구조로 대체되었다.

## 완료 조건 2
target-aware 관계 구조가 generic social-role ontology 위에 올라갔다.

## 완료 조건 3
Peter와 Judas가 동일한 persona profile schema로 설명된다.

## 완료 조건 4
새 agent 추가 시 필요한 것은 새 규칙 하드코딩이 아니라:
- role selection
- profile initialization
- relation seed
- world context binding

정도로 줄어들었다.

## 완료 조건 5
world engine 6-layer가 정적 카테고리가 아니라 process-oriented structure로 재정의되었다.

## 완료 조건 6
population grammar를 통해 handcraft 없이도 복수 agent 초기화가 가능해졌다.

---

# 21. 한 줄 요약

> **앞으로의 목표는 Peter를 더 잘 흉내 내는 것이 아니라, Peter에서 인간 일반의 반응 구조를 추출해 shared persona engine을 만들고, 그 위에 role, profile, world context를 얹어 population과 world dynamics를 생성하는 것이다.**

