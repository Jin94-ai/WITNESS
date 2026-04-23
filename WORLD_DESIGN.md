# WORLD_DESIGN.md — Witness 세계 시뮬레이션 설계서

*Witness: 살아있는 세계 위의 인과 시뮬레이터*

---

## 1. 프로젝트 정체성

### 1.1 한 줄 정의

> **Witness는 역사적 세계를 자체 동역학으로 구축하고, 그 안에서 인물들의 서사가 창발하며, 변수 조정을 통해 "만약 ~이었다면?"을 실험할 수 있는 인과 시뮬레이션 엔진이다.**

### 1.2 핵심 철학

> *"세상엔 인과관계가 있고 서사가 쌓여 역사가 생기고 스토리가 생기고 내가 존재하는거야."*
> — 프로젝트 설계자 Lee, 최초 구상

이 문장이 Witness의 모든 설계 결정의 근원이다.

### 1.3 이전 단계와의 관계

```
[v0.1~v1.2] 전기 시뮬레이터 (Biography Simulator)
  "한 사람의 생애를 시뮬레이션한다"
  - 세계 = 배경 (고정된 무대)
  - 인물 = 중심 (시뮬레이션 대상)
  - 성과: 엔진 5,800줄, 3 시나리오, 1003 테스트, POM 검증
        ↓
[v2.0] 세계 시뮬레이션 (World Simulation) ← 지금 시작
  "세계가 살아있고, 인물은 그 안의 일부다"
  - 세계 = 살아있는 시스템 (자체 동역학)
  - 인물 = 세계의 참여자 (세계가 인물 없이도 돌아감)
  - 목표: 변수 조정으로 반사실 실험 가능
```

**v1.2의 모든 코드와 테스트는 보존된다.** 세계는 기존 엔진 *위에* 쌓는다.

### 1.4 최종 비전

세계가 구축되면 이런 실험이 가능해진다:

- *"예수가 존재하지 않았다면 예루살렘은 어떻게 됐는가?"*
- *"베드로가 특별히 불행했다면 여전히 제자가 되었는가?"*
- *"빌라도가 관대했다면 십자가가 아닌 다른 결과가 나왔는가?"*
- *"유월절이 한 달 늦었다면 체포 타이밍이 달라졌는가?"*
- *"열심당이 더 강했다면 예수 운동이 흡수되었는가?"*

각 실험은 **"이 변수가 역사에 어떤 인과적 영향을 미쳤는가"**를 정량적으로 측정한다. 이것이 Witness의 궁극적 가치다.

---

## 2. 전기 시뮬레이터 vs 세계 시뮬레이션

### 2.1 근본적 차이

| | v1.2 전기 시뮬레이터 | v2.0 세계 시뮬레이션 |
|---|---|---|
| **중심** | 한 인물 | 세계 자체 |
| **다른 인물** | 주인공에게 영향 주는 도구 | 각자 독립적 생애 |
| **환경** | 고정 파라미터 | 자체 동역학 (경제, 정치, 기후) |
| **사건** | 인물에게 일어남 | 세계에서 일어남 (인물과 무관하게도) |
| **인과** | 내면 → 행동 (1차원) | 개인↔사회↔제도↔환경 (다층) |
| **시간** | 인물의 생애 범위 | 세대를 넘어갈 수 있음 |
| **제거 테스트** | 인물 제거 = 시뮬레이션 없음 | 인물 제거해도 세계 계속 돌아감 |
| **반사실** | "유다 없으면?" 수준 | "로마가 관대했다면?" 수준 |

### 2.2 핵심 전환

**세계가 먼저고, 인물은 그 안의 일부다.**

시뮬레이션을 시작하면 베드로가 없어도 예루살렘이 돌아간다. 유월절이 오고, 순례자가 몰려오고, 물가가 오르고, 로마가 긴장하고, 가야바가 움직인다. 베드로는 이 세계의 15만 명 중 한 명이다.

---

## 3. 세계의 층위 구조

### 3.1 6-Layer 아키텍처

```
┌─────────────────────────────────────────────┐
│  Layer 6: 개인 (Individuals)                │
│  베드로, 유다, 가야바, 빌라도, 군중 속 개인들   │
│  ← 기존 engine/ 이 담당 (Agent, Rule, Hazard) │
├─────────────────────────────────────────────┤
│  Layer 5: 사회 동역학 (Social Dynamics)       │
│  소문 전파, 군중 심리, 메시아 기대              │
├─────────────────────────────────────────────┤
│  Layer 4: 종교/사상 세력 (Factions)           │
│  바리새파, 사두개파, 에세네파, 열심당, 예수 운동  │
├─────────────────────────────────────────────┤
│  Layer 3: 정치 구조 (Political Structure)     │
│  로마 총독, 대제사장, 산헤드린, 헤롯 안티파스     │
├─────────────────────────────────────────────┤
│  Layer 2: 경제 (Economy)                     │
│  물가, 세금, 성전 수입, 교역, 빈부격차           │
├─────────────────────────────────────────────┤
│  Layer 1: 자연환경 (Environment)              │
│  계절, 기후, 달력, 절기, 농업 주기               │
└─────────────────────────────────────────────┘
```

**각 Layer는 자체 동역학으로 독립적으로 돌아간다.** 동시에 Layer 간 상호작용이 있다:

- Layer 1 → 2: 가뭄 → 곡물 가격 상승
- Layer 2 → 5: 물가 상승 → 빈민 불만 → 군중 불안
- Layer 5 → 4: 메시아 기대 고조 → 열심당 세력 확장
- Layer 4 → 3: 열심당 위협 → 로마 감시 강화
- Layer 3 → 6: 로마 감시 → 개인의 공포 증가
- Layer 6 → 5: 개인의 행동 (성전 정화) → 소문 전파 → 사회 동요

### 3.2 각 Layer 상세

#### Layer 1: 자연환경

```python
class EnvironmentLayer:
    calendar: JewishCalendar
    # - 현재 날짜 (유대력)
    # - 절기 상태: 유월절/초막절/오순절/안식일/평일
    # - 절기 → 순례자 유입 트리거

    climate: Climate
    # - 계절 (건기/우기)
    # - 일일 기온
    # - 일출/일몰 시각

    agriculture: AgricultureCycle
    # - 파종/성장/수확 주기
    # - 곡물 산출량 → Layer 2 경제에 영향
```

자체 동역학: 달력은 자동 진행, 계절은 주기적 변화, 절기는 달력에 의해 트리거.

#### Layer 2: 경제

```python
class EconomyLayer:
    grain_price: float      # 곡물 가격 (기본 생존 지표)
    temple_revenue: float   # 성전 수입 (환전 + 제물 판매)
    tax_burden: float       # 로마 세금 부담
    trade_activity: float   # 교역 활성도
    poverty_rate: float     # 빈곤율

    # 동역학:
    # - 절기 → 순례자 유입 → 성전 수입 증가 + 물가 상승
    # - 가뭄 → 곡물 가격 상승 → 빈곤율 증가
    # - 세금 인상 → 불만 증가 → Layer 5에 영향
```

#### Layer 3: 정치 구조

```python
class PoliticalLayer:
    roman_governor: GovernorState
    # - alertness: 경계 수준 (0-10)
    # - policy: 강경/유화
    # - location: 가이사랴/예루살렘 (절기에 이동)
    # - garrison_deployment: 병력 배치 수준

    high_priest: HighPriestState
    # - threat_perception: 위협 인식 수준
    # - roman_cooperation: 로마 협력도
    # - priority: 질서유지/교리수호/권력유지

    sanhedrin: SanhedrinState
    # - unity: 내부 결속도
    # - dominant_faction: 사두개/바리새 중 우세
    # - pending_cases: 계류 중인 재판
```

자체 동역학: 빌라도는 절기에 예루살렘으로 이동, 가야바는 위협 수준에 따라 행동, 산헤드린은 내부 정치.

#### Layer 4: 종교/사상 세력

```python
class FactionLayer:
    factions: Dict[str, Faction]
    # pharisees: 바리새파 (회당 영향력, 민중 교육)
    # sadducees: 사두개파 (성전 귀족, 로마 협력)
    # essenes: 에세네파 (쿰란, 묵시 사상)
    # zealots: 열심당 (무장 저항, 지하 조직)
    # jesus_movement: 예수 운동 (갈릴리 기반, 성장 중)
    # baptist_remnant: 세례 요한 잔여 세력

    # 각 faction:
    class Faction:
        influence: float     # 사회적 영향력 (0-10)
        membership: int      # 추종자 수 (추정)
        militancy: float     # 무장 성향
        roman_stance: str    # 협력/중립/저항
        growth_rate: float   # 성장/쇠퇴 속도
```

자체 동역학: 각 세력이 독립적으로 성장/쇠퇴, 서로 경쟁/협력, 외부 사건에 반응.

#### Layer 5: 사회 동역학

```python
class SocialLayer:
    crowd_density: float       # 군중 밀도 (순례자 유입에 따라)
    public_mood: float         # 대중 분위기 (-10 절망 ~ +10 흥분)
    messianic_expectation: float  # 메시아 기대 수준
    rumor_network: RumorGraph  # 소문 전파 네트워크

    class RumorGraph:
        active_rumors: List[Rumor]
        # 각 소문: 내용, 출처, 확산 범위, 신뢰도, 나이
        # 소문은 시장/회당/우물가에서 전파
        # 시간이 지나면 왜곡되거나 소멸
```

자체 동역학: 군중 밀도는 절기에 따라 변화, 소문은 자체 전파 규칙, 메시아 기대는 사건에 반응.

#### Layer 6: 개인

**기존 engine/의 Agent 시스템 그대로.** 추가되는 것:

- 각 agent가 **Layer 1-5의 정보를 부분적으로만 인식** (정보 비대칭)
- agent의 행동이 **Layer 1-5에 영향을 줄 수 있음** (상향 인과)
- Layer 1-5의 변화가 **agent의 상태에 영향** (하향 인과)

---

## 4. 시스템 아키텍처

### 4.1 폴더 구조

```
witness/                          (프로젝트 루트, 기존 유지)
│
├── engine/                       (기존 그대로, 수정 금지)
│   ├── core/                     (Agent, Hazard, Trigger, Phase 등)
│   ├── rules/                    (감정, 물리, 사회 규칙)
│   ├── simulation/               (SimulationWorld, PhasedWorld 등)
│   ├── rendering/                (trace, narrator)
│   └── io/                       (loader)
│
├── world/                        (신규 — 세계 Layer)
│   ├── __init__.py
│   ├── core/
│   │   ├── world_state.py        # WorldState: 모든 Layer의 통합 상태
│   │   ├── world_config.py       # WorldConfig: 세계 초기 설정
│   │   └── layer.py              # Layer 프로토콜 (공통 인터페이스)
│   ├── environment/
│   │   ├── calendar.py           # 유대 달력 + 절기
│   │   ├── climate.py            # 기후/계절
│   │   └── agriculture.py        # 농업 주기
│   ├── economy/
│   │   └── economy.py            # 물가, 세금, 성전 수입
│   ├── politics/
│   │   ├── roman_admin.py        # 총독, 군대
│   │   └── temple_authority.py   # 대제사장, 산헤드린
│   ├── factions/
│   │   └── faction_system.py     # 종파 세력 동역학
│   ├── social/
│   │   ├── crowd.py              # 군중 밀도/심리
│   │   └── rumors.py             # 소문 전파
│   ├── simulation/
│   │   ├── world_tick.py         # 세계 전체 1틱 진행
│   │   ├── layer_sync.py         # Layer 간 상호작용
│   │   ├── world_runner.py       # 세계 실행기 (다중 seed 앙상블)
│   │   └── observer.py           # 특정 agent 시점으로 관찰
│   └── intervention/
│       └── variable_control.py   # 변수 주입/제거/조정 (미래 구현)
│
├── content/                      (기존 + 확장)
│   ├── peter/                    (기존 그대로)
│   ├── judas/                    (기존 그대로)
│   ├── caiaphas/                 (기존 그대로)
│   ├── crowd/                    (기존 그대로)
│   ├── vangogh/                  (기존 그대로)
│   ├── gauguin/                  (기존 그대로)
│   ├── theo/                     (기존 그대로)
│   ├── talleyrand/               (기존 그대로)
│   ├── shared/                   (기존 그대로)
│   └── worlds/                   (신규 — 세계 데이터)
│       └── jerusalem_ad30/
│           ├── world_config.json      # 세계 기본 설정
│           ├── calendar.json          # 유대 달력 데이터
│           ├── economy_initial.json   # 경제 초기 상태
│           ├── factions_initial.json  # 종파 초기 세력
│           ├── politics_initial.json  # 정치 구조 초기 상태
│           ├── geography.json         # 지형/구역/거리
│           └── agents.json            # 이 세계에 존재하는 agent 목록
│
├── tests/                        (기존 + 세계 테스트)
│   ├── test_engine/              (기존 1003개 그대로)
│   ├── test_peter/               (기존 그대로)
│   └── test_world/               (신규)
│       ├── test_calendar.py
│       ├── test_economy.py
│       ├── test_politics.py
│       ├── test_world_tick.py
│       └── test_layer_sync.py
│
├── scripts/                      (기존 + 세계 데모)
│   ├── paper_numbers.py          (기존 유지)
│   ├── baseline_comparison.py    (기존 유지)
│   └── demo_world.py             (신규 — 세계 실행 진입점)
│
├── docs/
│   ├── paper_data/               (기존 유지)
│   └── world/                    (신규 — 세계 설계 문서)
│
├── DESIGN.md                     (기존 유지)
├── PROJECT_DIRECTION_v2.md       (기존 유지)
├── WORLD_DESIGN.md               (이 문서)
└── README.md
```

### 4.2 핵심 원칙

**원칙 1: engine/ 수정 금지**
기존 engine/ 코드는 한 줄도 수정하지 않는다. world/가 engine/을 import해서 사용한다. 기존 1003 테스트가 항상 통과해야 한다.

**원칙 2: world/는 engine/의 상위 계층**
world/world_tick.py가 매 틱마다 Layer 1-5를 업데이트한 후, engine/의 Agent/Rule 시스템으로 Layer 6(개인)을 업데이트한다. engine/은 자신이 세계 안에서 돌아가는지 모른다.

**원칙 3: Content/World 분리**
세계의 구조(world/)와 특정 세계의 데이터(content/worlds/jerusalem_ad30/)는 분리. 나중에 다른 세계(예: content/worlds/arles_1888/)를 추가할 수 있다.

**원칙 4: 각 Layer는 독립 테스트 가능**
달력만 따로, 경제만 따로, 정치만 따로 테스트할 수 있어야 한다. Layer 간 의존성은 명시적 인터페이스로만.

**원칙 5: 변수 조정은 나중에**
v2.0 첫 단계에서는 세계 구축에 집중. 변수 주입/제거/조정 실험은 세계가 안정적으로 돌아간 후에. world/intervention/은 빈 디렉토리로 자리만 잡아둔다.

### 4.3 세계 틱 구조

```python
class WorldTick:
    """세계 전체의 1틱 진행"""

    def tick(self, world_state: WorldState, agents: List[AgentState]) -> WorldState:
        # 1. Layer 1: 환경 업데이트
        #    - 달력 1일 진행
        #    - 계절/기후 변화
        #    - 절기 확인 → 절기 이벤트 발생 여부
        world_state.environment = self.environment_layer.tick(world_state.environment)

        # 2. Layer 2: 경제 업데이트
        #    - 환경(계절, 절기) 반영
        #    - 물가/세금/교역 계산
        world_state.economy = self.economy_layer.tick(
            world_state.economy, world_state.environment
        )

        # 3. Layer 3: 정치 업데이트
        #    - 경제 상황 반영 (빈민 불만 → 총독 경계)
        #    - 독립적 정치 동역학 (가야바의 판단, 빌라도의 이동)
        world_state.politics = self.politics_layer.tick(
            world_state.politics, world_state.economy, world_state.social
        )

        # 4. Layer 4: 종파 업데이트
        #    - 정치/경제 반영
        #    - 세력 간 경쟁/성장/쇠퇴
        world_state.factions = self.faction_layer.tick(
            world_state.factions, world_state.politics, world_state.social
        )

        # 5. Layer 5: 사회 업데이트
        #    - 군중 밀도 (절기 + 순례자)
        #    - 소문 전파
        #    - 대중 분위기
        world_state.social = self.social_layer.tick(
            world_state.social, world_state.environment, world_state.factions
        )

        # 6. Layer 6: 개인 업데이트 (기존 engine 사용)
        #    - 세계 상태를 agent의 환경으로 주입
        #    - engine의 Rule/Hazard/Trigger 시스템으로 agent 업데이트
        #    - agent 행동이 세계에 영향 (상향 인과)
        agent_env = self.world_to_agent_env(world_state)
        updated_agents = self.engine_tick(agents, agent_env)
        world_state = self.agent_effects_to_world(updated_agents, world_state)

        return world_state
```

### 4.4 세계 ↔ 개인 인터페이스

**하향 인과 (세계 → 개인)**:
세계 상태가 agent의 `EnvironmentState`로 변환되어 주입.

```python
def world_to_agent_env(self, world: WorldState) -> EnvironmentState:
    """세계 상태를 기존 engine의 EnvironmentState로 변환"""
    return EnvironmentState(
        surveillance=world.politics.roman_governor.garrison_deployment,
        crowd_pressure=world.social.crowd_density,
        time_pressure=world.environment.calendar.days_until_passover,
        # ... 기존 engine이 이해하는 필드로 매핑
    )
```

**상향 인과 (개인 → 세계)**:
agent의 행동이 세계 상태를 변경.

```python
def agent_effects_to_world(self, agents, world: WorldState) -> WorldState:
    """agent 행동이 세계에 미치는 영향"""
    for agent in agents:
        for action in agent.recent_actions:
            if action == "temple_cleansing":
                world.social.active_rumors.append(
                    Rumor(content="갈릴리 랍비가 성전을 뒤엎었다", spread=0.3)
                )
                world.politics.high_priest.threat_perception += 2.0
            if action == "public_teaching":
                world.factions["jesus_movement"].influence += 0.1
                world.social.messianic_expectation += 0.05
    return world
```

---

## 5. 첫 세계: 예루살렘 AD 30

### 5.1 범위

- **시간**: AD 30년 니산월 (유월절 한 달 전) ~ 유월절 후 50일 (오순절)
- **공간**: 예루살렘 + 근교 (베다니, 겟세마네, 골고다)
- **인구**: 상주 ~4만, 유월절 유입 ~15만 (집단 변수로 처리)
- **개별 agent**: 베드로, 유다, 가야바 + 신규 (빌라도, 바라바 등)

### 5.2 세계의 자체 동역학 (agent 없이도 돌아가는 것)

1. 달력이 진행된다 → 유월절이 다가온다
2. 순례자가 유입된다 → 인구 밀도가 높아진다
3. 물가가 오른다 → 빈민 압박이 커진다
4. 빌라도가 가이사랴에서 올라온다 → 로마 감시가 강화된다
5. 가야바가 산헤드린을 소집한다 → "소요가 없어야 한다"
6. 바리새파가 회당에서 가르친다 → 메시아 기대가 오르락내리락한다
7. 열심당이 지하에서 움직인다 → 긴장이 쌓인다

**이 7가지가 베드로 없이도 매 틱 돌아간다.** 이게 "살아있는 세계"의 최소 조건이다.

### 5.3 베드로가 세계에 참여하면

위의 자체 동역학에 추가로:
- 예수 운동(Layer 4)이 예루살렘에 도착한다
- 성전 정화가 일어난다 → 소문 폭발 (Layer 5)
- 가야바의 위협 인식 급상승 (Layer 3)
- 유다의 내면이 변화한다 (Layer 6, 기존 엔진)
- 체포-재판-십자가로 이어지는 인과 체인

**핵심: 이 인과 체인이 세계의 자체 동역학과 얽혀 있다.** 유월절이 아니었으면 순례자가 없고, 순례자가 없으면 성전 정화의 관중이 없고, 관중이 없으면 소문이 안 퍼지고, 소문이 안 퍼지면 가야바가 덜 위협 느끼고... 세계의 리듬이 사건의 타이밍을 결정한다.

---

## 6. 개발 로드맵

### 6.1 Spike 1: 세계가 돌아간다 (4-6주)

**목표**: *"agent 없이 예루살렘이 자체적으로 돌아간다"*

구현:
- [ ] world/core/ 기본 구조 (WorldState, WorldConfig, Layer 프로토콜)
- [ ] Layer 1: 유대 달력 + 절기 주기 + 기본 기후
- [ ] Layer 2: 물가 + 순례자 유입에 따른 변동
- [ ] Layer 3: 빌라도 이동 + 가야바 위협 인식 (단순 규칙)
- [ ] Layer 5: 군중 밀도 (절기에 따른 사이클)
- [ ] world/simulation/world_tick.py: Layer 1-3, 5 순차 업데이트
- [ ] content/worlds/jerusalem_ad30/ 초기 데이터
- [ ] scripts/demo_world.py: 90일간 세계 실행, Layer별 상태 출력
- [ ] tests/test_world/: 각 Layer 단위 테스트

**검증**: 90일 돌렸을 때 유월절 전후로 군중 밀도, 물가, 로마 경계가 자연스럽게 오르내리는가?

**하지 않을 것**: Layer 4 (종파), Layer 6 (개인 agent), 소문 전파, 변수 조정

### 6.2 Spike 2: 개인이 세계 안으로 (3-4주)

**목표**: *"기존 agent(베드로, 유다, 가야바)가 세계 안에서 돌아간다"*

구현:
- [ ] world_to_agent_env(): 세계 상태 → 기존 EnvironmentState 매핑
- [ ] agent_effects_to_world(): agent 행동 → 세계 영향
- [ ] 기존 engine의 SimulationWorld를 world_tick의 Layer 6으로 통합
- [ ] 세계 모드에서 arrest가 여전히 자발 발생하는가 검증

**검증**: 세계 모드의 결과가 전기 모드(기존)와 *유사하되 동일하지는 않아야* 한다. 세계의 맥락이 agent에 영향을 주므로 수치가 달라질 수 있지만, 구조(인과 체인)는 유지.

### 6.3 Spike 3: 종파와 소문 (3-4주)

**목표**: *"예수 운동이 세계 안의 한 세력으로 존재한다"*

구현:
- [ ] Layer 4: 종파 시스템 (5-6개 종파, 세력 변동)
- [ ] Layer 5 확장: 소문 전파 네트워크
- [ ] 예수 운동의 성장이 가야바의 위협 인식에 영향
- [ ] 소문("갈릴리 랍비가 성전을 뒤엎었다")이 Layer 5에서 전파

**검증**: 예수 운동의 influence가 높아질수록 가야바의 threat_perception이 올라가고, 체포 타이밍이 앞당겨지는가?

### 6.4 Spike 4: 변수 조정 실험 (2-3주)

**목표**: *"예수를 제거했을 때 세계가 어떻게 달라지는가?"*

구현:
- [ ] world/intervention/variable_control.py
- [ ] 첫 실험: 예수 운동 제거 → 세계 90일 실행 → 비교
- [ ] 두 번째 실험: 빌라도 관대도 변경 → 비교
- [ ] 세 번째 실험: 경제 호황 → 비교

**검증**: 변수 제거/변경 시 *측정 가능한 차이*가 발생하는가?

### 6.5 이후 (장기)

- 더 많은 agent (니고데모, 아리마대 요셉, 바라바, 막달라 마리아)
- 더 풍부한 경제 모델
- 갈릴리 확장 (예루살렘 외 지역)
- 다른 세계 (content/worlds/arles_1888/ 등)
- 인과 발견 (방식 4): 시뮬레이션 데이터에서 자동으로 인과 관계 추출
- 인터랙티브: 사용자가 세계에 개입

---

## 7. 기존 프로젝트와의 관계 정리

### 7.1 보존하는 것

- engine/ 전체 (5,800줄, 수정 금지)
- content/peter, judas, caiaphas, crowd, vangogh, gauguin, theo, talleyrand (전부 유지)
- tests/ 기존 1003개 (항상 green)
- scripts/ 기존 (paper_numbers 등)
- docs/paper_data/ (실험 결과 보존)

### 7.2 추가하는 것

- world/ (신규 디렉토리)
- content/worlds/ (세계 데이터)
- tests/test_world/ (세계 테스트)
- scripts/demo_world.py (세계 데모)
- WORLD_DESIGN.md (이 문서)

### 7.3 논문 상태

PAPER_DRAFT_V06.md (413줄)은 보존한다. 세계 구축을 진행하면서 자연스럽게 논문의 추가 소재가 생길 것이다. 논문 마감은 Lee가 원할 때 한다. 강제하지 않는다.

---

## 8. 절대 규칙 (ABSOLUTE RULES) 확장

기존 5개 규칙을 유지하고, 세계 시뮬레이션용 규칙을 추가한다.

### 기존 유지

1. engine/ 코드 내 특정 인물 참조 금지
2. 정경 말씀 재작성 금지
3. 예수 비에이전트화 (ExternalEvent/CanonicalIntervention으로만)
4. LLM 런타임 배제
5. 용어 과장 금지 ("engine universality"만 허용)

### 신규 추가

6. **engine/ 수정 금지**: world/는 engine/을 import만 한다. engine/ public interface를 깨지 않는 generic 확장은 허용 (v1.1 amendment §2.6).
7. **Layer 독립성**: 각 Layer는 단독으로 테스트 가능해야 한다. Layer 간 의존은 명시적 인터페이스만.
8. **기존 테스트 보존**: 1003개 기존 테스트가 항상 통과해야 한다. 세계 추가로 깨지면 안 된다.
9. **Same-tick feedback 금지** (Spike 2 A-3): 같은 world tick 안에서 Layer A → Layer B → Layer A 순환 금지. 순환 의존이 필요한 경우 반드시 1-tick delay를 삽입하고, 의존 문자열에 `@prev_tick` 접미사를 붙여 `describe_dynamics()`에 기록한다. 자동 검증: `tests/test_world/test_layer_dag.py::test_tick_order_is_a_dag`.

---

## 9. Claude Code 첫 세션 프롬프트

```
WORLD_DESIGN.md를 읽어라. 이 문서가 세계 시뮬레이션의 최상위 설계서다.
PROJECT_DIRECTION_v2.md와 DESIGN.md도 참조하되, 충돌 시 WORLD_DESIGN.md가 우선.

오늘 세션 목표: Spike 1의 첫 단계 — 세계 기본 구조 + Layer 1 (달력/절기).

절대 규칙:
1. engine/ 기존 코드 수정 금지
2. 기존 1003 테스트가 깨지면 안 됨
3. world/ 아래에만 새 코드 작성
4. 각 Layer는 단독 테스트 가능해야 함

작업 순서:
1. world/ 폴더 구조 생성 (WORLD_DESIGN.md §4.1 참조)
2. world/core/layer.py — Layer 프로토콜 정의
3. world/core/world_state.py — WorldState 기본 스키마
4. world/core/world_config.py — WorldConfig
5. world/environment/calendar.py — 유대 달력 (니산월~시반월, 90일)
   - 유월절(니산 14일), 무교절, 초실절, 안식일 자동 계산
   - tick 1일 = 달력 1일 진행
6. content/worlds/jerusalem_ad30/calendar.json — 달력 초기 데이터
7. tests/test_world/test_calendar.py — 달력 단위 테스트
   - 90일 돌렸을 때 유월절이 정확한 날에 오는가
   - 안식일이 7일마다 오는가
   - 절기 이벤트가 올바르게 트리거되는가

오늘 Layer 2-5는 구현하지 않는다.
달력이 정확하게 돌아가는 것을 먼저 확인한다.

자율 진행. 완료 후 보고.
시작해라.
```

---

*WORLD_DESIGN.md v1.0 끝*
*작성: Lee + Claude (claude.ai 설계 파트너)*
*일시: 2026-04-21*
*다음 갱신: Spike 1 완료 후*
