# Witness — ODD Protocol (Overview, Design concepts, Details)

> Grimm et al. (2020) ODD Protocol v2에 따른 모델 기술.

---

## 1. Purpose and patterns

### Purpose
한 사람의 생애를 수천 번 시뮬레이션하고 결과 분포를 관측하여 "무엇이 갈라지는 순간이었는가"를 발견한다.

### Patterns
모델이 재현해야 하는 관측 패턴 (POM scorecard):

**베드로 (7개 패턴):**
1. 체포 시 도주 안 함
2. 칼을 뽑음
3. 3회 부인
4. 극한 슬픔 경험 (grief >= 8)
5. 도덕적 상처 누적 (moral_injury >= 3)
6. 정체성 손상 (identity_shift < -1)
7. 최종 희망 회복 (hope >= 3)

**반 고흐 (5개 패턴):**
1. 창작 폭발
2. 고갱 갈등 2회+
3. 극한 슬픔
4. 자해/위기
5. 정체성 손상

---

## 2. Entities, state variables, and scales

### Entities
- **Agent**: 시뮬레이션의 주체. AgentState로 표현.
- **Environment**: 에이전트 외부 압력. EnvironmentState로 표현.

### State variables

**AgentState:**
- physical: fatigue, hunger, health, location (각 0~10)
- emotions (fast state): fear, hope, grief, confusion, love (각 0~10)
- slow_state: moral_injury, breach_count, event_trauma, identity_shift, trust_scar
- relationships: target_id별 trust, love, awe, understanding
- domain_state: 인물별 확장 (FaithJourneyState, CreativeDriveState 등)

**EnvironmentState:**
- crowd_pressure, surveillance, threat_level, time_pressure, isolation_degree (각 0~10)

### Scales
- 시간: tick (베드로: ~2시간/tick, 500 tick = 50일. 반 고흐: ~1일/tick, 150 tick = 15주)
- 공간: location 문자열 (이산적)

---

## 3. Process overview and scheduling

### 매 tick 순서:
1. CanonicalIntervention 적용 (정경 개입)
2. Legacy tick 고정 이벤트 (하위 호환)
3. Hazard 기반 이벤트 평가 (competing risks, hazard 내림차순)
   - 행동 결정 (WeightFormula + 확률적 선택)
   - 이벤트 효과 적용 (행동 결정 후)
4. Langevin 노이즈 주입
5. 규칙 엔진 적용 (physical → emotional → social → temporal)
6. 환경 동적 규칙 적용
7. 동적 해상도 판정 + 스냅샷

---

## 4. Design concepts

### Basic principles
- Hazard-driven events: 이벤트가 고정 시점이 아니라 상태 기반 위험도로 확률적 발생.
- Fast/slow state: emotions는 항상성으로 중앙 수렴, slow_state는 비가역적 누적.
- Pattern-Oriented Modeling: 여러 패턴을 동시에 맞추는 필터로 규칙 구조 검증.

### Emergence
- 경로 유형 (도주형, 부인형 등)이 규칙에서 하드코딩되지 않고 자연 출현.
- fear x love 상호작용이 부인의 가장 큰 단일 동인 (shapiq 검증).

### Adaptation
- 에이전트 행동은 WeightFormula로 상태 기반 확률적 결정.
- 학습/적응 메커니즘은 없음 (slow_state는 누적이지 학습이 아님).

### Objectives
- 에이전트에 명시적 objective 없음. 행동은 상태 기반 확률.

### Sensing
- 에이전트는 자신의 상태 + 환경을 완전히 감지.

### Interaction
- 현재: 에이전트-환경 상호작용만. 에이전트 간 직접 상호작용 없음 (향후 확장).

### Stochasticity
- Hazard event timing (Poisson process)
- Action selection (weighted random choice)
- Langevin noise on emotions
- Seed-based reproducibility

### Observation
- 매 배치: POM scorecard, 경로 클러스터링 (UMAP+HDBSCAN), 민감도 분석 (Sobol, Morris, shapiq), 분기면 탐색 (PRIM, Decision Tree), 파라미터 보정 (pyABC).

---

## 5. Initialization

- 초기 상태: content/[인물]/initial_state.json
- 환경 초기 상태: SimulationConfig.environment
- 파라미터 오버라이드: parameter_overrides로 배치 실행 시 변동

---

## 6. Input data

- 정경 이벤트: content/[인물]/hazard_events.json
- 정경 개입: content/[인물]/canonical_events.json (interventions)
- 체크포인트: content/[인물]/checkpoints.json

---

## 7. Submodels

### 규칙 (engine/rules/)
- FatigueRule, HungerRule, HealthRule (physical)
- FearResponseRule (피로-공포 교차 증폭), ConfusionRule (fatigue>7 AND fear>6), HopeRule, GriefRule, LoveRule (emotional)
- RelationshipDecayRule, GroupIsolationRule (social)
- HomeostasisRule (조건부, 감정별 차등), SlowStateRule, HighStressConsequenceRule, CircadianRule (temporal)
- EnvironmentDynamicsRule (환경 자체 변동)

### 검증 결과
- POM: current 규칙 38.6% 7/7 통과 (fear-only 1.2%, uniform 0%)
- pyABC Model Selection: current = 100%
- shapiq: fear x love 상호작용 = 1위 (0.123)
- Parameter Recovery: PASS (true params in recovered box)
- 194개 테스트 전체 통과
