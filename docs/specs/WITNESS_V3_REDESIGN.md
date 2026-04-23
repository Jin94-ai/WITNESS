# WITNESS v3.0 — 구조적 재설계: Pressure-Based World + Constrained Generation

**생성 배경:**
Spike 6 (Behavior Cloning)에서 반복 확인된 근본 한계 — *"신경망이 잘 학습할수록
규칙 엔진의 사본, 못 학습하면 noise, emergent vs 오류 구분 불가"* — 을 해결하기 위해
프로젝트 구조를 재설계한다.

**이 설계는 ChatGPT 외부 자문(982줄 상세 답변)의 전면 수용이다.**

**핵심 전환:**
- 신경망을 "중심 엔진"에서 "규칙 세계 위의 반응 해석기"로 강등
- 월드 엔진을 "사건 생성기"에서 "압력 생성기"로 재정의
- Reward 논쟁을 폐기하고 "학습 reward + 평가 rubric 분리"로 재프레이밍
- 변수 50-80 확장 계획 폐기, 20-30개 핵심 + 희소 상호작용으로 축소

**선행 조건:**
- Spike 1-6 완료 (1176+ tests green, Person/World engine 동작)
- Spike 6 BC 모델 2개 (peter_bc_v2, v3) 존재 — 이후 단계에서 역할 재배정

**폐기 / 아카이브:**
- Spike 6의 BC 중심 로드맵
- Spike 7/8 이전 계획 (Discovery Target, remove_jesus 등)
- 변수 50-80개 확장 계획

---

## 0. 이 재설계의 본질

### 0.1 핵심 문장 (ChatGPT 원문)

> *"세계는 행동을 만들지 말고, 행동이 어려워지는 조건을 만들라."*

> *"신경망을 버리는 게 아니라, '세계를 만드는 역할'에서 빼고 '세계 안에서 반응을
> 해석하는 역할'로 축소하는 게 맞다."*

> *"reward는 선택사항이고, evaluation rubric은 필수사항이다."*

### 0.2 왜 이 재설계가 필요한가

지금까지의 구조는 다음 세 가지가 얽혀 있었다:

```
(1) 세계가 행동까지 결정 → 인물이 규칙 반사체가 됨
(2) 신경망이 규칙 엔진을 모방 → 사본 생성 또는 noise
(3) "발견" 정의 부재 → 재생을 발견으로 착각
```

ChatGPT 재설계는 이 셋을 분리한다:

```
(1) 세계는 압력만 생성, 행동은 인물이 결정
(2) 신경망은 압력→행동 분포의 해석기, 세계 시뮬레이션과 분리
(3) "발견"을 3종으로 분할, 평가 rubric 4축으로 측정
```

### 0.3 이 재설계가 안 건드리는 것

보존할 자산:
- Person Engine 기본 구조 (AgentState, FaithJourneyState)
- World Engine의 Layer 1 (Calendar, Crowd, Economy, Politics 등 기존 6 layer)
- DecisionPolicy Protocol, dual-path fallback (Rule #11)
- 기존 1176+ tests
- Spike 4 counterfactual framework (Judas, Pilate 등)

재배치할 자산:
- BC 모델 peter_bc_v2/v3 → "후보 평가기(scorer)" 역할로 전환 가능성 검토
- Spike 6 데이터 파이프라인 → 새 평가 체계의 trajectory 생성원

---

## 1. ABSOLUTE RULES 업데이트

### 1.1 기존 Rule #1-11 유지

단, 해석 명확화:

- **Rule #6 (engine public API 수정 금지):** 신규 `engine/pressure/`, `engine/rubric/` 
  등 **새 모듈 추가는 허용**. 기존 모듈 수정만 금지.
- **Rule #11 (dual-path):** BC 모델을 scorer로 전환해도 규칙 기반 fallback 유지.

### 1.2 Rule #12 신설

> **월드 레이어는 행동을 결정하지 않는다.**
> 월드는 압력 벡터(pressure field)를 생성할 뿐이며, 행동은 인물 모듈의 책임이다.
> 월드 규칙에 `agent.action = X` 같은 직접 할당이 발견되면 Rule #12 위반.

### 1.3 Rule #13 신설

> **"발견(discovery)"은 3종으로 분할하여 명시한다.**
> 
> - Canonical reproduction (정경 재생)
> - Canon-compatible alternative (정경과 양립 가능한 대안)
> - Character-consistent novel trajectory (캐릭터 일관성 있는 새 경로)
> 
> 모든 실험 보고서는 결과가 위 3종 중 어느 것인지 명시해야 한다.
> "발견" 이라는 단어를 분류 없이 사용 금지.

### 1.4 Rule #14 신설

> **학습 reward와 평가 rubric을 분리한다.**
> 
> 학습 단계에서 reward 사용은 선택사항이며, 정경을 reward로 직접 쓰지 않는다.
> 평가 단계에서 rubric 4축(Character / Canon / Causal / Novelty)은 필수다.
> Reward 없는 학습 + rubric 기반 평가가 기본 구조.

---

## 2. 재설계의 4 Phase 구조

이 재설계는 단일 작업이 아니라 **4개 독립 Phase**로 나뉜다. 각 Phase는 **선행
Phase 완료 후에만** 진행한다.

```
Phase 1: 발견 정의 문서화           (문서 작업, 코드 0)
   ↓
Phase 2: 핵심 변수 24개 재설계      (Person 재설계)
   ↓
Phase 3: Pressure Field 월드 구축   (World 재설계)
   ↓
Phase 4: 4축 Rubric 평가 시스템     (평가 체계 구축)
```

**각 Phase 완료 후 Lee 확인 대기. 자동 다음 Phase 진입 금지.**

---

## 3. Phase 1 — 발견 정의 문서화

### 3.1 의도

ChatGPT 지적:
> *"이 3개를 분리해서 써야 합니다. 이 셋을 구분 못 하면 이후 실험이 전부 흐려집니다."*

이 Phase는 **코드 작업이 아니라 철학 문서화**. 모든 후속 Phase의 기준점.

### 3.2 작성할 문서

```
docs/witness_discovery_definitions.md
```

**최소 섹션:**

1. **Canonical reproduction** — 정경 재생
   - 정의
   - 측정 방법
   - 예시 (베드로 부인 사건이 정경대로 발생)

2. **Canon-compatible alternative** — 정경 양립 대안
   - 정의 (정경과 모순되지 않지만 정경에 명시되지 않은 행동)
   - 측정 방법 (canon critic으로 hard constraint 통과)
   - 예시 (정경에 없는 화요일 오후의 plausible 베드로 행동)

3. **Character-consistent novel trajectory** — 캐릭터 일관성 있는 새 경로
   - 정의
   - 측정 방법 (character critic + causal critic 통과)
   - 예시 (베드로답지만 정경 어느 장면에도 없는 trajectory)

4. **혼동 방지 — "발견"으로 오해되는 것들**
   - 규칙 보간 (interpolation) — 발견 아님
   - Noise / random variation — 발견 아님
   - 하드코딩된 사건의 실행 — 발견 아님

### 3.3 Phase 1 완료 기준

- [ ] `docs/witness_discovery_definitions.md` 작성 완료
- [ ] 3종 발견 각각에 **측정 방법** 명시 (추상적 서술 금지)
- [ ] Lee가 문서를 읽고 "앞으로 실험 결과를 이 3종으로 분류 가능" 판단
- [ ] 코드 변경 0 (이 Phase는 순수 문서 작업)
- [ ] 기존 tests green 유지

### 3.4 Phase 1 금지 사항

- 코드 변경 금지
- 새 실험 실행 금지
- Phase 2 코드 미리 작성 금지

### 3.5 Phase 1 막혔을 때

1. 3종 경계가 모호한 경우 → Lee 판단 필요
2. 측정 방법이 현 도구로 불가능한 경우 → 구현 가능한 측정 방법 Lee와 상의
3. 정경 양립 여부 판정이 신학적으로 논쟁적인 경우 → Lee 판단 필요

---

## 4. Phase 2 — 핵심 변수 24개 재설계

### 4.1 의도

ChatGPT 지적:
> *"80개는 최종 ontology 후보일 수는 있어도 다음 단계 구현 타깃으로는 과합니다."*
> *"변수 수보다 더 무서운 건 상호작용 수. 각 변수는 최대 3개만 직접 연결."*

Lee의 원안(50-80 원자 변수)을 축소. **20-30개 핵심 변수 + 희소 상호작용 그래프**.

### 4.2 3계층 변수 구조 (ChatGPT 권장)

```
Core state (행동 직접 결정 변수, 20-30개)
    ↓
Latent bundle (아직 분해 애매한 추상 변수, 유지)
    ↓
Derived features (규칙이 계산하는 보조 피처)
```

### 4.3 Core state 24개 후보 (ChatGPT 초안)

**Lee가 검증/수정 필요. 아래는 출발점.**

**범주 1 — Threat (4개)**
- `fear_death` — 생명 위협
- `fear_pain` — 고통 위협
- `fear_isolation` — 사회적 배제 위협
- `fear_identity_loss` — 정체성 상실 위협

**범주 2 — Attachment (3개)**
- `loyalty_to_jesus` — 예수에 대한 충성
- `bond_to_disciples` — 동료 제자들과의 유대
- `attachment_to_family` — 가족에 대한 애착

**범주 3 — Conviction (3개)**
- `conviction_calling` — 부르심에 대한 확신
- `conviction_identity` — 자기 정체성 확신
- `conviction_truth` — 가르침의 진실성 확신

**범주 4 — Shame/Guilt (3개)**
- `shame_exposure` — 공개 수치
- `guilt_betrayal` — 배신 죄책감
- `regret_inaction` — 행동하지 못한 후회

**범주 5 — State (3개)**
- `fatigue` — 피로
- `exhaustion_emotional` — 감정 소진
- `hunger` — 배고픔

**범주 6 — Social (3개)**
- `public_visibility` — 공개 노출도
- `role_expectation` — 역할 기대 압박
- `perceived_forgiveness` — 용서받았다는 감각

**범주 7 — Memory (3개)**
- `memory_of_jesus_teaching` — 가르침 기억
- `memory_of_own_failure` — 자기 실패 기억
- `memory_of_miracles` — 기적 목격 기억

**범주 8 — Faith trajectory (2개)**
- `faith_stage` — 신앙 단계 (categorical)
- `understanding_level` — 이해 수준

총 24개 (범주별 2-4개).

### 4.4 상호작용 규칙

**원칙:** 각 변수는 최대 3개 upstream + 3개 downstream 연결.

**새 변수 추가 시 체크리스트 (ChatGPT 원문):**

1. 이 변수는 기존 변수들의 선형/비선형 조합으로 대체 가능한가?
2. 이 변수가 바뀌면 실제로 action distribution이 바뀌는가?
3. 이 변수를 관찰하지 않으면 설명 불가능한 현상이 있는가?

**셋 중 둘 이상 해당 안 되면 변수 추가 금지.**

### 4.5 기존 AgentState와의 관계

기존:
```
emotions: fear, hope, grief, confusion, love  (5)
physical: fatigue, hunger, health             (3)
slow_state: moral_injury, identity_shift, 
            event_trauma, trust_scar          (4)
FaithJourneyState: jesus_understanding, 
            obedience_maturity, fear_layers, 
            communal_role                     (4)
```
**총 16개**

신규 24개는 기존과 **완전 대체 아닌 매핑 관계**로 설계:

- 기존 `fear` → 신규 `fear_death/pain/isolation/identity_loss` 4개로 분해
- 기존 `moral_injury` → 신규 `guilt_betrayal + regret_inaction + shame_exposure`로 분해
- 기존 `jesus_understanding` → 신규 `understanding_level + conviction_truth`로 분해
- 기존 `love` → 신규 `loyalty_to_jesus + bond_to_disciples`로 분해

**매핑 테이블 필수 작성.** 기존 코드가 깨지지 않도록.

### 4.6 Phase 2 완료 기준

- [ ] 24개 핵심 변수 확정 (Lee 승인)
- [ ] 범주별 정의 문서 (`docs/witness_core_variables_v2.md`)
- [ ] 기존 16개 ↔ 신규 24개 매핑 테이블
- [ ] 상호작용 그래프 (각 변수 최대 3 connection)
- [ ] 기존 AgentState와 backward compatible한 migration path
- [ ] 기존 1176+ tests green 유지 (migration 후)

### 4.7 Phase 2 금지 사항

- 24개 초과 변수 추가 금지 (변수 폭증 방지)
- 완전 연결 그래프 설계 금지 (희소성 유지)
- 기존 코드 전면 재작성 금지 (migration path로 점진)
- Phase 3 월드 작업 병행 금지

### 4.8 Phase 2 막혔을 때

1. 24개로 표현 불가능한 행동이 발견 → 변수 추가 여부 Lee 판단
2. 기존 코드와 충돌 → backward compat 우선
3. 범주 간 경계 모호 → Lee와 재분류
4. Lee가 검증한 24개가 원안과 크게 다름 → ChatGPT 권장 범주 무시하고 Lee 안 우선

---

## 5. Phase 3 — Pressure Field 월드 구축

### 5.1 의도

ChatGPT 지적:
> *"세계를 '무엇이 일어났는가'의 목록으로 만들지 말고, '그 일이 인물에게 어떤 
> 압력을 가했는가'의 구조로 만들어라."*

기존 월드 엔진 6 layer는 유지하되, **Pressure Field Layer를 신설**하여 월드와
인물 사이의 중간 층으로 배치.

### 5.2 4층 월드 구조 (ChatGPT 원안)

```
Layer A: World Facts  (기존 Spike 1-5 layer 재분류)
    - time_of_day, location, crowd_density,
      roman_presence, temple_tension, group_cohesion,
      recent_public_events, resource_scarcity

Layer B: Event Objects  (짧은 수명 사건)
    - event_type, participants, visibility,
      urgency, threat_level, sacred_salience,
      social_exposure

Layer C: Pressure Field  ← 신규 핵심
    - 8 압력 변수 (§5.3)

Layer D: Constraint  (헌법)
    - 역사적 모순 금지, 정경 충돌 금지,
      시대착오 금지, 신성모독 금지,
      특정 인물 지식 범위 제한
```

### 5.3 8개 Pressure 변수 (ChatGPT 원안, Lee 검증 필요)

```
social_threat       ← crowd_density × accusation_visibility
physical_threat     ← roman_presence × volatility
shame_exposure      ← public_visibility × prior_failure_salience
loyalty_pull        ← memory_of_jesus × proximity_of_suffering
uncertainty         ← information_gap × stakes
urgency             ← time_pressure × decision_criticality
isolation_pressure  ← (group_absence) × (perceived_abandonment)
sacred_salience     ← religious_context × personal_faith_activation
```

### 5.4 Event Table (ChatGPT 예시)

```
Event                 | social_threat | physical_threat | shame_exposure | loyalty_pull
---------------------|---------------|-----------------|----------------|-------------
public accusation    | +3            | +1              | +4             | 0
jesus eye contact    | 0             | 0               | +3             | +5
crowd mockery        | +4            | +1              | +5             | -1
ally nearby          | -2            | 0               | -1             | +2
```

**각 이벤트의 압력 영향을 테이블화.** 이게 월드의 디버깅 포인트.

### 5.5 압력 잔향(Duration)

ChatGPT 지적:
> *"중요한 건 이벤트 발생 그 순간보다, 그게 몇 턴 동안 잔향을 남기느냐다."*

각 압력마다 **decay 시간** 정의:

```
accusation (event): 1 turn only
shame_exposure (pressure): 5 turn decay
sacred_salience (pressure): 장면 후 장기 지속
```

### 5.6 기존 Spike 1-5 월드와의 통합

**충돌 회피 원칙:**
- 기존 6 layer (Calendar, Crowd, Economy, Politics, Factions, Rumours)는 
  Layer A (World Facts) 하위로 재분류
- 새 Pressure Field Layer (C)는 **기존 위에 올라가는 새 층**
- 기존 tests 전부 green 유지

### 5.7 Phase 3 완료 기준

- [ ] 8개 Pressure 변수 확정
- [ ] Event Table 작성 (최소 20개 이벤트)
- [ ] Pressure 계산 엔진 (`engine/pressure/calculator.py`)
- [ ] Constraint Layer 초안 (hard constraints 명시)
- [ ] 기존 1176+ tests green 유지
- [ ] Rule #12 준수 (월드가 행동 결정 금지)

### 5.8 Phase 3 금지 사항

- 월드가 행동 직접 할당 금지 (Rule #12)
- 세계 엔진에 복잡한 agent 로직 주입 금지
- 8개 초과 압력 변수 추가 금지 (검증 전)
- 기존 6 layer 삭제/재작성 금지

### 5.9 Phase 3 막혔을 때

1. 기존 6 layer와 Pressure Field의 경계 모호 → Lee 판단
2. Constraint Layer가 너무 엄격해서 대안 trajectory 차단 → 완화 Lee 판단
3. 압력 계산이 너무 무거워짐 → 8개에서 축소 Lee 판단
4. 기존 tests 깨짐 → migration 재설계

---

## 6. Phase 4 — 4축 Rubric 평가 시스템

### 6.1 의도

ChatGPT 지적:
> *"reward는 선택사항이고, evaluation rubric은 필수사항입니다."*

Reward를 학습에서 빼고, 대신 **4축 평가 rubric**을 구축. 이 rubric이 모든 후속
실험의 "발견 vs 재생 vs noise" 판정 도구.

### 6.2 4축 Rubric (ChatGPT 원안)

**축 1: Character Consistency**
- 베드로다움 유지 여부
- 측정: 
  - 충동성 패턴 (베드로 특유의 즉각 반응)
  - 관계 반응 (예수/동료/적대자에 대한 베드로식 반응)
  - 두려움-용기 전환 (베드로의 전형적 왕복)

**축 2: Canon Compatibility**
- 정경과 모순 여부
- 측정:
  - Hard constraint 침범 (시대착오, 신성모독, 직접 모순)
  - Soft constraint (canonical attractor에서의 편차)

**축 3: Causal Coherence**
- 상태 변화와 행동의 인과 설명 가능 여부
- 측정:
  - 상태 전이가 이유를 가지는가
  - 뜬금없는 점프가 없는가
  - 시간 경과가 자연스러운가

**축 4: Novelty under Constraint**
- 정경 복사본이 아닌가
- 측정:
  - 정경 trajectory와의 거리 (너무 가까우면 복사)
  - 무작위 일탈 여부 (너무 멀면 noise)
  - "의미 있는 다름" 지표

### 6.3 Critic 구현 방식

각 축마다 **독립 critic**:

```
engine/rubric/
  __init__.py
  character_critic.py   (축 1)
  canon_critic.py       (축 2)
  causal_critic.py      (축 3)
  novelty_critic.py     (축 4)
  rubric_evaluator.py   (4 critic 통합)
```

**중요:** critic은 학습 loss로 쓰지 않는다. **사후 평가용**만.

### 6.4 BC 모델 재배치

기존 peter_bc_v2/v3 BC 모델을 **canon critic 구현에 활용 가능성 검토**:

- 규칙 기반 엔진 행동 = BC 모델이 예측하는 행동 → canon-compatible
- BC 모델 예측과 크게 다름 → canon deviation 신호

이건 ChatGPT의 "구조 B (Rule World + Neural Scorer)" 의 적용.

### 6.5 Phase 4 완료 기준

- [ ] 4 critic 모두 구현
- [ ] Rubric evaluator 통합
- [ ] 기존 trajectory (Spike 1-6 실험 결과)에 rubric 적용 가능 확인
- [ ] **이전 "발견" 주장들을 rubric으로 재평가**
  - Judas 제거 실험 → Rule #13의 어느 종류인가?
  - Spike 6 BC 결과 → 어느 종류인가?
- [ ] Rule #13, #14 준수
- [ ] 기존 1176+ tests green 유지

### 6.6 Phase 4 금지 사항

- Rubric을 학습 loss로 사용 금지 (Rule #14 위반)
- 정경을 dense reward로 사용 금지 (constraint로만)
- 단일 scalar로 합산 금지 (4축 독립 유지)

### 6.7 Phase 4 막혔을 때

1. Character critic의 "베드로다움" 정의 불가 → Lee와 함께 정의
2. Novelty critic의 "의미 있는 다름" 판정 어려움 → 정량 지표 Lee와 설계
3. 기존 실험 결과가 rubric 통과 실패 → Lee 판단 (그 자체가 중요한 정보)

---

## 7. 4 Phase의 관계와 병행 금지

```
Phase 1 (문서) ────────────────┐
                               │
Phase 2 (변수) ←───────────────┤ (Phase 1 발견 정의 참조)
                               │
Phase 3 (월드) ←───────────────┤ (Phase 2 변수 참조)
                               │
Phase 4 (평가) ←───────────────┤ (Phase 1-3 모두 참조)
```

**엄격한 순서. 병행 금지.**

이유:
- Phase 1 없이 Phase 2-4는 기준점 없음
- Phase 2 없이 Phase 3은 인물 반응 대상 불명
- Phase 3 없이 Phase 4는 평가 대상 trajectory 없음

**각 Phase 완료 후 Lee 확인 대기.** Claude Code가 자동 진입 금지.

---

## 8. 신경망의 위치 — 미래 Phase 5+ 예고

이 재설계(Phase 1-4)에서는 **신경망 학습 작업 없음.**

Phase 5+ (추후 별도 지시)에서 신경망 재도입:

**ChatGPT 구조 B (권장, 보수적):**
```
Rule engine proposes candidate actions
    ↓
Neural scorer ranks them  ← 기존 BC 모델 전환
    ↓
Top action selected
    ↓
Rubric critic filters
    ↓
Final action
```

**또는 ChatGPT 구조 A (균형):**
```
world state + event + pressure vector + person state
    ↓
Neural policy  ← 신규 학습 필요
    ↓
Action distribution
    ↓
Rule-based constraint filter / critic
    ↓
Final action
```

**구조 C (월드도 신경망):** ChatGPT 명시 금지 — *"현재 자원, 데이터, 검증 체계로는
너무 이르다."*

Phase 5 진입 여부는 **Phase 4 rubric 결과**를 보고 Lee가 결정.

---

## 9. 자율 vs 보고 구분

### Claude Code 자율 결정 영역

**Phase 1:**
- 문서 구조, 예시 선택

**Phase 2:**
- 변수 구현 세부 (dataclass, validation 로직)
- Migration 전략 세부
- 범주 내 변수 이름 선택 (Lee 승인 후)

**Phase 3:**
- Pressure 계산 수식 세부
- Event Table 구체 값 (Lee 방향 승인 후)
- Decay 함수 형태

**Phase 4:**
- Critic 구현 아키텍처
- 지표 계산 방식
- Rubric 통합 방식

### Lee 판단 필수 영역

**Phase 1:**
- "발견" 3종의 경계 정의
- 측정 방법 실현 가능성

**Phase 2:**
- **24개 핵심 변수 최종 확정** (ChatGPT 초안은 출발점일 뿐)
- 범주 체계 승인
- 기존-신규 매핑 최종 승인

**Phase 3:**
- **8개 Pressure 변수 최종 확정**
- Event Table 주요 이벤트 목록
- Constraint 범위 (너무 엄격하면 다양성 차단)

**Phase 4:**
- "베드로다움"의 정의
- "의미 있는 다름"의 정의
- 이전 실험 재평가 시 판단

### Claude Code 절대 단독 결정 금지

- 각 Phase 완료 판정 (Lee 확인 대기)
- 다음 Phase 자동 진입
- Rule #12, #13, #14 해석 변경
- BC 모델 폐기 여부
- 신경망 재도입 시점

---

## 10. 산출물 구조

```
docs/
  witness_discovery_definitions.md         (Phase 1)
  witness_core_variables_v2.md             (Phase 2)
  witness_core_variables_migration.md      (Phase 2)
  witness_pressure_field_design.md         (Phase 3)
  witness_event_pressure_table.md          (Phase 3)
  witness_rubric_design.md                 (Phase 4)
  witness_previous_experiments_reevaluation.md  (Phase 4)

engine/
  core/                                    (기존 유지)
  person/
    state_v2.py                            (Phase 2, 24 변수)
    migration.py                           (Phase 2, 기존→신규)
  pressure/                                (Phase 3, 신규 디렉토리)
    __init__.py
    pressure_field.py
    event_pressure_map.py
    decay.py
  constraint/                              (Phase 3, 신규)
    __init__.py
    hard_constraints.py
    soft_constraints.py
  rubric/                                  (Phase 4, 신규)
    __init__.py
    character_critic.py
    canon_critic.py
    causal_critic.py
    novelty_critic.py
    rubric_evaluator.py

tests/
  test_person/test_state_v2.py             (Phase 2)
  test_pressure/                           (Phase 3)
  test_rubric/                             (Phase 4)
```

---

## 11. 세션 권장

| Phase | 예상 세션 | 비고 |
|---|---|---|
| Phase 1 (문서) | 1 세션 | 순수 문서 작업 |
| Phase 2 (변수) | 2-3 세션 | 설계 + migration + test |
| Phase 3 (월드) | 3-4 세션 | Pressure + Event + Constraint |
| Phase 4 (평가) | 2-3 세션 | 4 critic + 통합 + 재평가 |

**총 8-11 세션.** 각 Phase 완료 후 Lee 확인, 새 세션에서 다음 Phase.

**한 세션에 여러 Phase 시도 금지.**

---

## 12. 이번 재설계의 정신

### 12.1 버리는 것

- "신경망 중심" 가정
- "변수 50-80 확장" 계획
- "정경 reward" 아이디어
- "발견" 의 모호한 사용
- 월드가 행동 결정

### 12.2 얻는 것

- 해석 가능한 구조
- 검증 가능한 "발견" 판정
- 1인 프로젝트 규모에 맞는 scope
- 신경망 재도입 시 명확한 역할 (scorer / critic)
- 정경 제약과 다양성의 균형

### 12.3 Lee의 원래 비전과의 관계

Lee의 원 비전:
> *"신경망 학습을 통해 천변만화하는 세상을 시뮬레이터로 구축"*

재설계 후 해석:
> *"규칙 기반 압력장 위에서, 신경망이 해석기/평가자로 기여하며, 
> 발견 rubric으로 검증 가능한 천변만화 생성"*

핵심은 *"천변만화"* 의 정의가 명확해졌다는 것:
- Canonical reproduction (정확한 재생)
- Canon-compatible alternative (정경 양립 대안)
- Character-consistent novel trajectory (캐릭터 일관성 있는 새 경로)

이 셋이 각각 다른 빈도로 나타나는 시스템 = 천변만화.

---

## 13. 한 줄 요약

**"세계는 행동을 만들지 말고 행동을 어렵게 하라. 신경망은 세계를 만드는 
자리에서 내려 세계 안에서 반응을 해석하는 자리로. Reward 없이 학습하고, 
rubric으로 평가하며, 발견을 3종으로 분할해 측정하라."**

---

## 14. 부록 — ChatGPT 원문에서 특히 중요한 인용

```
"변수 원자화는 '학습 품질 개선 장치'지, '발견 생성 장치'가 아닙니다."

"reward는 선택사항이고, evaluation rubric은 필수사항입니다."

"알파고 비유는 절반은 유효, 절반은 틀렸다."

"세계는 행동을 만들지 말고, 행동이 어려워지는 조건을 만들라."

"신경망을 버리는 게 아니라, '세계를 만드는 역할'에서 빼고 
 '세계 안에서 반응을 해석하는 역할'로 축소하는 게 맞다."

"허용된 우주 안에서 분기하는 것이 목적이다."
```

이 6개 문장이 재설계의 뼈대.
