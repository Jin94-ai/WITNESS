# WITNESS Narrative Mining Engine 작업 계획서

## 0. 목적

기존 WITNESS는 압력 기반 세계 시뮬레이션, Observer, Candidate 추출, Markdown Brief, Provenance Ledger까지 갖춘 구조다. 하지만 현재 산출물은 주로 “긴장이 튄 순간” 또는 “사건 후보”를 잡는 데 집중되어 있다.

이 계획의 목표는 WITNESS를 단순 보고서 생성기나 단일 인물 서사 생성기가 아니라, **세계 전체를 구동한 뒤 그 안에서 쌓이는 여러 이야기 후보를 채굴하는 Narrative Mining Engine**으로 확장하는 것이다.

핵심 방향:

```text
World Simulation
→ Moment Detection
→ Moment Linking
→ Story Thread Mining
→ Narrative Opportunity Ranking
→ Creative Use Case Export
```

---

## 1. 최종 포지션

### 1.1 프로젝트 정의

**WITNESS = World-first Narrative Mining Engine**

한 줄 정의:

> WITNESS는 압력 기반 세계 시뮬레이션을 구동한 뒤, 그 안에서 발생하는 인물 변화, 관계 변화, 집단 긴장, 갈등 누적을 연결해 여러 개의 서사 후보를 채굴하는 시스템이다.

### 1.2 하지 말아야 할 포지션

```text
- 한 인물의 이야기를 하드코딩해서 뽑는 엔진
- 정해진 플롯을 재생하는 스토리 렌더러
- AI가 소설을 자동으로 써주는 도구
- 단순 사건 감지기
- 픽셀 월드나 컷신 중심의 시각화 프로젝트
```

### 1.3 해야 할 포지션

```text
- 세계 전체를 먼저 구동한다.
- 여러 인물과 집단의 압력 변화가 쌓인다.
- 반복 선택, 관계 변화, 미해결 갈등을 관찰한다.
- 그중 이야기로 발전 가능한 흐름을 Story Thread로 묶는다.
- 창작자는 여러 이야기 후보 중 사용할 것을 고른다.
```

---

## 2. 현재 구조와 확장 방향

### 2.1 현재 강점

기존 WITNESS에는 이미 다음 기반이 있다.

```text
- 다중 에이전트 시뮬레이션
- 압력 기반 세계 구동
- deterministic seed 실행
- AgentState / WorldSnapshot / GroupSnapshot / AgentSnapshot
- Observer 4-lens 구조: World / Person / Group / Event
- StoryCandidate 추출
- Curation bucket: story_ready / observation_only / hold
- Provenance class: source_derived / source_inferred / not_used
- Markdown Brief 자동 생성
- Provenance Ledger 자동 생성
```

### 2.2 현재 한계

현재 Candidate는 주로 이런 질문에 답한다.

```text
어느 순간 긴장이 튀었는가?
어느 tick이 관찰할 만한가?
어떤 signal이 감지됐는가?
```

하지만 우리가 원하는 질문은 다르다.

```text
이 세계 안에서 어떤 이야기가 쌓이고 있는가?
어떤 인물/관계/집단 축이 서사로 발전 가능한가?
반복되는 갈등은 무엇인가?
시작과 끝 사이에 의미 있는 변화가 있었는가?
창작자가 가져다 쓸 만한 이야기 씨앗은 무엇인가?
```

### 2.3 확장 방향

기존 `StoryCandidate`를 폐기하지 않는다. 대신 그 위에 새로운 계층을 추가한다.

```text
Snapshot
→ Moment
→ MomentLink
→ StoryThread
→ NarrativeOpportunity
→ CreativeExport
```

---

## 3. 핵심 개념 정의

## 3.1 Moment

Moment는 단일 tick 또는 짧은 tick range에서 관찰된 의미 있는 변화다.

기존 Candidate보다 더 넓은 개념이다. Candidate가 “눈에 띄는 사건 후보”라면, Moment는 “서사적으로 연결될 수 있는 변화 단위”다.

### Moment 예시

```json
{
  "moment_id": "M_t072_peter_fear_rise",
  "tick": 72,
  "tick_range": [68, 76],
  "moment_type": "agent_state_shift",
  "agents": ["peter"],
  "groups": ["L1"],
  "pressures": ["fear", "authority_vigilance"],
  "signals": ["agent_state_shift", "authority_vigilance_spike"],
  "summary": "Peter's fear rises while authority pressure increases.",
  "provenance": "source_derived"
}
```

### Moment 유형

```text
agent_state_shift       인물 상태 변화
relationship_drift      관계 변화
group_tension_shift     집단 긴장 변화
world_pressure_shift    세계 압력 변화
choice_pattern          반복 선택 또는 행동 경향
conflict_marker         갈등 축이 드러나는 순간
event_ripple            사건 이후 여파
unresolved_thread       미해결 상태가 지속되는 구간
```

---

## 3.2 Story Thread

Story Thread는 여러 Moment가 같은 갈등 축으로 연결된 서사 후보이다.

단일 사건이 아니라, 시간에 따른 변화 묶음이어야 한다.

### Story Thread 예시

```json
{
  "thread_id": "T04_fear_loyalty_silence",
  "title": "Fear Turns Loyalty into Silence",
  "main_agents": ["peter"],
  "supporting_agents": ["group_L1"],
  "core_conflict": "loyalty_vs_survival",
  "arc_direction": "loyal_presence_to_avoidant_isolation",
  "moments": ["M_t034", "M_t058", "M_t072", "M_t091"],
  "start_tick": 34,
  "end_tick": 91,
  "pressure_history": ["fear", "authority_vigilance", "shame_self"],
  "relationship_drift": ["distance_up", "trust_down"],
  "unresolved_question": "Will Peter confess loyalty or continue hiding?",
  "story_potential_score": 0.82,
  "usable_as": ["film_scene", "short_story", "game_quest_branch"]
}
```

---

## 3.3 Narrative Opportunity

Narrative Opportunity는 Story Thread를 창작자가 바로 이해하고 선택할 수 있게 정리한 결과물이다.

Story Thread가 데이터 구조라면, Narrative Opportunity는 창작용 요약 카드다.

### Narrative Opportunity 예시

```text
Title: Fear Turns Loyalty into Silence

Core Conflict:
A loyal follower wants to remain faithful, but rising public danger makes silence feel safer than truth.

Arc:
Presence → hesitation → withdrawal → shame

Why it works:
The thread has repeated pressure, visible emotional drift, relationship distance, and an unresolved moral question.

Usable as:
- Film: betrayal-before-betrayal scene
- Novel: internal collapse chapter
- Game: loyalty choice branch
- Drama: group suspicion episode
```

---

## 4. 데이터 설계

새 파일을 추가한다.

```text
engine/observer/moment.py
engine/observer/thread.py
engine/observer/narrative_opportunity.py
scripts/narrative/build_story_threads.py
scripts/narrative/export_narrative_opportunities.py
```

기존 engine core는 수정하지 않는다. 모든 작업은 additive 원칙을 지킨다.

---

## 4.1 Moment 모델

파일: `engine/observer/moment.py`

```python
from dataclasses import dataclass, field
from typing import Literal

MomentType = Literal[
    "agent_state_shift",
    "relationship_drift",
    "group_tension_shift",
    "world_pressure_shift",
    "choice_pattern",
    "conflict_marker",
    "event_ripple",
    "unresolved_thread",
]

ProvenanceClass = Literal[
    "source_derived",
    "source_inferred",
    "not_used",
]

@dataclass(frozen=True)
class Moment:
    moment_id: str
    tick: int
    tick_range: tuple[int, int]
    moment_type: MomentType
    agents: list[str] = field(default_factory=list)
    groups: list[str] = field(default_factory=list)
    events: list[str] = field(default_factory=list)
    pressures: list[str] = field(default_factory=list)
    signals: list[str] = field(default_factory=list)
    summary: str = ""
    salience_score: float = 0.0
    provenance: ProvenanceClass = "source_derived"
```

---

## 4.2 Moment 추출기

파일: `engine/observer/moment_extractor.py`

### 입력

```text
SnapshotStream 또는 observer dump JSON
```

### 출력

```text
list[Moment]
```

### 추출 기준

#### A. Agent State Shift

조건:

```text
fear / hope / shame_self / dominant_state 중 하나가 일정 threshold 이상 변화
```

예시:

```python
if abs(agent_now.fear - agent_prev.fear) >= 1.5:
    create Moment(type="agent_state_shift")
```

#### B. Group Tension Shift

조건:

```text
group.tension이 threshold 이상 상승
또는 dominant_mode가 low_activity → split / saturated로 변경
```

#### C. World Pressure Shift

조건:

```text
crowd_mood 변화
blame_concentration 상승
public_suspicion 상승
authority_vigilance 상승
```

#### D. Conflict Marker

조건:

```text
한 agent의 fear 상승 + hope 하락
또는 group tension 상승 + agent withdrawal
또는 authority_vigilance 상승 + public_suspicion 상승
```

#### E. Unresolved Thread Marker

조건:

```text
같은 압력 또는 상태가 N tick 이상 유지됨
예: fear > 7.0이 10 tick 이상 지속
```

---

## 4.3 MomentLink 모델

파일: `engine/observer/thread.py`

```python
from dataclasses import dataclass
from typing import Literal

LinkType = Literal[
    "same_agent",
    "same_group",
    "same_relationship",
    "same_pressure",
    "same_conflict_axis",
    "causal_order",
    "temporal_continuity",
]

@dataclass(frozen=True)
class MomentLink:
    source_moment_id: str
    target_moment_id: str
    link_type: LinkType
    weight: float
    rationale: str
```

---

## 4.4 StoryThread 모델

파일: `engine/observer/thread.py`

```python
from dataclasses import dataclass, field
from typing import Literal

ArcDirection = Literal[
    "stability_to_breakdown",
    "fear_to_withdrawal",
    "trust_to_distance",
    "loyalty_to_betrayal_risk",
    "confusion_to_commitment",
    "isolation_to_dependence",
    "tension_to_collective_action",
    "unknown",
]

@dataclass(frozen=True)
class StoryThread:
    thread_id: str
    title: str
    main_agents: list[str]
    supporting_agents: list[str] = field(default_factory=list)
    groups: list[str] = field(default_factory=list)
    core_conflict: str = "unknown"
    arc_direction: ArcDirection = "unknown"
    moment_ids: list[str] = field(default_factory=list)
    start_tick: int = 0
    end_tick: int = 0
    pressure_history: list[str] = field(default_factory=list)
    relationship_drift: list[str] = field(default_factory=list)
    unresolved_question: str = ""
    story_potential_score: float = 0.0
    usable_as: list[str] = field(default_factory=list)
    provenance: str = "source_inferred"
```

---

## 5. 이야기 후보 생성 알고리즘

## 5.1 전체 파이프라인

```text
1. observer dump 로드
2. Snapshot 기반 Moment 추출
3. Moment 간 link 생성
4. link graph 생성
5. graph에서 connected component 또는 path 후보 추출
6. 각 path를 StoryThread 후보로 변환
7. story_potential_score 계산
8. threshold 이상만 Narrative Opportunity로 export
```

---

## 5.2 Moment 추출

입력:

```text
data/visual/dot_observer_data.json
```

출력:

```text
data/narrative/moments.json
```

명령:

```bash
python scripts/narrative/build_moments.py \
  --input data/visual/dot_observer_data.json \
  --output data/narrative/moments.json
```

---

## 5.3 Moment 연결 기준

Moment A와 Moment B가 다음 중 하나 이상을 공유하면 연결한다.

```text
same_agent              같은 인물이 포함됨
same_group              같은 집단이 포함됨
same_pressure           같은 압력 축이 반복됨
same_conflict_axis      같은 갈등 유형으로 해석 가능
temporal_continuity     tick 간격이 너무 멀지 않음
causal_order            A의 변화가 B의 조건을 강화함
```

### 기본 시간 간격

```text
max_gap = 30 ticks
```

단, unresolved_thread는 더 긴 간격 허용 가능.

```text
max_gap_for_unresolved = 60 ticks
```

---

## 5.4 Story Thread 승격 조건

Moment 묶음이 Story Thread가 되려면 최소 조건을 만족해야 한다.

```text
- moment가 최소 3개 이상이어야 함
- start_tick과 end_tick 사이에 의미 있는 상태 변화가 있어야 함
- 같은 agent/group/pressure 중 하나가 반복되어야 함
- core_conflict를 추론할 수 있어야 함
- unresolved_question이 생성 가능해야 함
```

권장 조건:

```text
- 관계 변화가 포함되면 가산점
- 반복 선택 패턴이 있으면 가산점
- 시작과 끝의 dominant_state가 달라지면 가산점
- world pressure와 agent pressure가 동시에 엮이면 가산점
```

---

## 6. Story Potential Score

Story Thread의 점수는 단순 salience가 아니라 “이야기로 쓸 수 있는 가능성”이다.

### 6.1 점수 요소

```text
change_score             시작과 끝의 변화량
continuity_score         moment들이 시간적으로 연결되는 정도
conflict_score           명확한 갈등 축 존재 여부
relationship_score       관계 변화 포함 여부
pressure_score           압력 누적 정도
resolution_gap_score     미해결 질문의 강도
multi_agent_score        여러 인물/집단이 얽혔는지
creative_use_score       영화/소설/게임 등 활용 가능성
```

### 6.2 기본 계산식

```python
story_potential_score = (
    change_score * 0.20 +
    continuity_score * 0.15 +
    conflict_score * 0.20 +
    relationship_score * 0.15 +
    pressure_score * 0.10 +
    resolution_gap_score * 0.10 +
    multi_agent_score * 0.05 +
    creative_use_score * 0.05
)
```

### 6.3 점수 해석

```text
0.80 이상  strong narrative opportunity
0.60 이상  usable thread
0.40 이상  weak but inspectable
0.40 미만  hold
```

---

## 7. Core Conflict 추론 규칙

LLM 없이 deterministic rule로 먼저 구현한다.

### 7.1 예시 규칙

```text
fear 상승 + loyalty 관련 agent 지속 등장
→ loyalty_vs_survival

trust 하락 + distance 상승
→ trust_vs_self_protection

group tension 상승 + blame_concentration 상승
→ collective_fear_vs_scapegoating

authority_vigilance 상승 + public_suspicion 상승
→ control_vs_exposure

hope 하락 + shame 상승
→ identity_vs_failure

confusion 상승 + repeated avoidance
→ uncertainty_vs_commitment
```

### 7.2 출력 conflict label

```text
loyalty_vs_survival
trust_vs_self_protection
collective_fear_vs_scapegoating
control_vs_exposure
identity_vs_failure
uncertainty_vs_commitment
belonging_vs_isolation
unknown
```

---

## 8. Arc Direction 추론 규칙

### 8.1 예시

```text
fear 상승 + group distance 상승
→ fear_to_withdrawal

trust 하락 + tension 상승
→ trust_to_distance

hope 하락 + shame 상승
→ stability_to_breakdown

confusion 하락 + commitment 행동 증가
→ confusion_to_commitment

isolation 상승 + dependency 상승
→ isolation_to_dependence

group tension 상승 + collective event 발생
→ tension_to_collective_action
```

### 8.2 주의

Arc Direction은 창작적 해석이므로 `source_inferred`로 표시한다.

---

## 9. Narrative Opportunity Export

파일: `scripts/narrative/export_narrative_opportunities.py`

### 입력

```text
data/narrative/story_threads.json
```

### 출력

```text
docs/portfolio/NARRATIVE_OPPORTUNITIES.md
data/narrative/narrative_opportunities.json
```

### Markdown 출력 형식

```md
# WITNESS Narrative Opportunities

## Run Context

- Scenario: peter_scarcity_baseline
- Seed: 0
- Ticks: 200
- Threads found: 12
- Strong opportunities: 4

---

## T04 — Fear Turns Loyalty into Silence

### Core Conflict

Loyalty vs survival.

### Arc

Presence → hesitation → withdrawal → shame.

### Key Moments

| Tick | Moment | Evidence |
|---:|---|---|
| 34 | Fear begins rising | source_derived |
| 58 | Group tension crosses threshold | source_derived |
| 72 | Peter withdraws from group pressure | source_inferred |
| 91 | Shame rises while hope falls | source_derived |

### Why This Is Usable

This thread contains repeated pressure, visible internal drift, relationship distance, and an unresolved moral question.

### Creative Uses

- Film: betrayal-before-betrayal scene
- Novel: internal collapse chapter
- Game: loyalty choice branch
- Drama: suspicion episode

### Unresolved Question

Will the character confess loyalty or continue hiding?
```

---

## 10. 데이터 출력 구조

## 10.1 `moments.json`

```json
{
  "run_label": "peter_scarcity_baseline",
  "moments": [
    {
      "moment_id": "M_t034_peter_fear_rise",
      "tick": 34,
      "tick_range": [30, 38],
      "moment_type": "agent_state_shift",
      "agents": ["peter"],
      "groups": ["L1"],
      "pressures": ["fear"],
      "signals": ["agent_state_shift"],
      "summary": "Peter's fear begins to rise.",
      "salience_score": 0.64,
      "provenance": "source_derived"
    }
  ]
}
```

## 10.2 `story_threads.json`

```json
{
  "run_label": "peter_scarcity_baseline",
  "threads": [
    {
      "thread_id": "T04_fear_loyalty_silence",
      "title": "Fear Turns Loyalty into Silence",
      "main_agents": ["peter"],
      "supporting_agents": ["group_L1"],
      "groups": ["L1"],
      "core_conflict": "loyalty_vs_survival",
      "arc_direction": "fear_to_withdrawal",
      "moment_ids": ["M_t034", "M_t058", "M_t072", "M_t091"],
      "start_tick": 34,
      "end_tick": 91,
      "pressure_history": ["fear", "authority_vigilance", "shame_self"],
      "relationship_drift": ["distance_up"],
      "unresolved_question": "Will Peter confess loyalty or continue hiding?",
      "story_potential_score": 0.82,
      "usable_as": ["film_scene", "short_story", "game_quest_branch"],
      "provenance": "source_inferred"
    }
  ]
}
```

## 10.3 `narrative_opportunities.json`

```json
{
  "run_label": "peter_scarcity_baseline",
  "summary": {
    "threads_total": 12,
    "strong_opportunities": 4,
    "usable_threads": 6,
    "hold_threads": 2
  },
  "opportunities": [
    {
      "thread_id": "T04_fear_loyalty_silence",
      "title": "Fear Turns Loyalty into Silence",
      "logline": "A loyal character slowly retreats into silence as public danger makes truth feel unsafe.",
      "creative_uses": ["film", "novel", "game"],
      "score": 0.82
    }
  ]
}
```

---

## 11. UI 방향: Narrative Mining Console

보고서만 만들지 말고 정적 HTML 콘솔을 만든다.

파일:

```text
docs/portfolio/narrative_mining_console.html
```

### 화면 구성

```text
┌──────────────────────────────────────────────┐
│ WITNESS Narrative Mining Console             │
│ Scenario / Seed / Ticks / Threads Found       │
├──────────────────────────────────────────────┤
│ World Pressure Timeline                       │
│ candidate pins + thread spans                 │
├─────────────────┬────────────────────────────┤
│ Story Threads   │ Thread Detail               │
│ T01             │ title / conflict / arc       │
│ T02             │ moments / pressure history   │
│ T03             │ unresolved question          │
├─────────────────┴────────────────────────────┤
│ Creative Use Cases                            │
│ Film / Novel / Game / Drama                   │
└──────────────────────────────────────────────┘
```

### 필수 UI 요소

```text
- thread list
- story_potential_score
- core_conflict badge
- arc_direction badge
- timeline span
- key moments table
- pressure history chips
- creative use tags
- evidence toggle
```

### 하지 말 것

```text
- 캐릭터 애니메이션
- 픽셀 컷신
- staged visual
- 복잡한 live simulation UI
- 외부 asset 의존
```

---

## 12. 구현 단계

## Phase 1 — Moment Layer 추가

목표:

```text
Snapshot stream에서 Moment를 추출한다.
```

작업:

```text
1. engine/observer/moment.py 추가
2. engine/observer/moment_extractor.py 추가
3. scripts/narrative/build_moments.py 추가
4. data/narrative/moments.json 생성
5. tests/test_observer/test_moment_extractor.py 추가
```

완료 기준:

```text
- agent_state_shift Moment 추출 가능
- group_tension_shift Moment 추출 가능
- world_pressure_shift Moment 추출 가능
- deterministic output
- 기존 테스트 영향 없음
```

---

## Phase 2 — Moment Linking 추가

목표:

```text
Moment들을 같은 agent/group/pressure/conflict 기준으로 연결한다.
```

작업:

```text
1. MomentLink 모델 추가
2. link_moments(moments) 함수 구현
3. same_agent / same_group / same_pressure link 구현
4. temporal_continuity link 구현
5. tests/test_observer/test_moment_linking.py 추가
```

완료 기준:

```text
- Moment graph 생성 가능
- tick 순서 보존
- max_gap 적용
- link rationale 생성
```

---

## Phase 3 — Story Thread Mining

목표:

```text
연결된 Moment 묶음을 StoryThread로 승격한다.
```

작업:

```text
1. StoryThread 모델 추가
2. build_story_threads(moments, links) 구현
3. connected component 또는 path 기반 thread 생성
4. core_conflict 추론 규칙 구현
5. arc_direction 추론 규칙 구현
6. story_potential_score 계산
7. scripts/narrative/build_story_threads.py 추가
8. data/narrative/story_threads.json 생성
```

완료 기준:

```text
- 최소 3 moment 이상 묶음만 thread로 승격
- start/end 변화량 계산
- core_conflict 생성
- unresolved_question 생성
- score 산출
```

---

## Phase 4 — Narrative Opportunity Export

목표:

```text
StoryThread를 창작자가 이해 가능한 카드 형태로 변환한다.
```

작업:

```text
1. narrative_opportunity.py 추가
2. export_narrative_opportunities.py 추가
3. Markdown export 구현
4. JSON export 구현
5. creative use mapping 구현
```

완료 기준:

```text
- docs/portfolio/NARRATIVE_OPPORTUNITIES.md 생성
- data/narrative/narrative_opportunities.json 생성
- strong / usable / hold 분류
```

---

## Phase 5 — Narrative Mining Console

목표:

```text
정적 HTML로 Story Thread를 직관적으로 보여준다.
```

작업:

```text
1. docs/portfolio/narrative_mining_console.html 생성
2. story_threads.json 로드
3. thread list 렌더
4. thread detail 렌더
5. timeline span 렌더
6. evidence toggle 구현
```

완료 기준:

```text
- 브라우저에서 열면 바로 확인 가능
- 외부 라이브러리 없이 작동
- 하나의 HTML 파일로 포트폴리오 공유 가능
```

---

## 13. 테스트 계획

### 13.1 Moment Extractor Tests

```text
- fear 상승 시 agent_state_shift Moment 생성
- group tension 상승 시 group_tension_shift Moment 생성
- authority_vigilance 상승 시 world_pressure_shift Moment 생성
- threshold 미만 변화는 Moment 생성하지 않음
- output deterministic
```

### 13.2 Moment Linking Tests

```text
- 같은 agent를 공유하면 same_agent link 생성
- 같은 pressure를 공유하면 same_pressure link 생성
- max_gap 초과 시 link 생성하지 않음
- link weight가 0~1 범위 유지
```

### 13.3 Story Thread Tests

```text
- moment 2개 이하는 thread 승격 불가
- moment 3개 이상 + 같은 conflict axis면 thread 생성
- start_tick < end_tick 보장
- story_potential_score 0~1 범위
- provenance는 source_inferred
```

### 13.4 Export Tests

```text
- Markdown 파일 생성
- JSON 파일 생성
- strong / usable / hold 분류 정확성
- thread_id 중복 없음
```

---

## 14. 설계 원칙

### 14.1 Additive 원칙

기존 engine core를 수정하지 않는다.

```text
engine/core/* 수정 금지
engine/simulation/* 수정 최소화
engine/observer/* 에 additive module 추가
scripts/narrative/* 신규 추가
```

### 14.2 Provenance 원칙

모든 출력은 source class를 가져야 한다.

```text
source_derived   실제 snapshot / observer field에서 직접 온 값
source_inferred  규칙 기반 추론 결과
not_used         시각 연출 또는 제외된 값
```

### 14.3 No Hardcoded Hero 원칙

특정 인물을 주인공으로 고정하지 않는다.

금지:

```text
main_agent = "peter" 고정
Peter 전용 story rule
특정 anchor 전용 thread title
```

허용:

```text
run 결과에서 salience 높은 agent를 main_agents로 선택
agent id는 데이터에서 읽기
conflict는 상태 변화와 관계 변화로 추론
```

### 14.4 No Story Writing 원칙

초기 버전에서는 완성된 소설/대본을 생성하지 않는다.

생성할 것:

```text
- thread title
- core conflict
- arc direction
- key moments
- unresolved question
- creative use tags
```

생성하지 말 것:

```text
- 완성된 장면 대사
- 소설 본문
- 영화 시나리오
- 감정 과잉 서술
```

---

## 15. 최종 산출물 목록

```text
engine/observer/moment.py
engine/observer/moment_extractor.py
engine/observer/thread.py
engine/observer/thread_builder.py
engine/observer/narrative_opportunity.py

scripts/narrative/build_moments.py
scripts/narrative/build_story_threads.py
scripts/narrative/export_narrative_opportunities.py

data/narrative/moments.json
data/narrative/story_threads.json
data/narrative/narrative_opportunities.json

docs/portfolio/NARRATIVE_OPPORTUNITIES.md
docs/portfolio/narrative_mining_console.html

tests/test_observer/test_moment_extractor.py
tests/test_observer/test_moment_linking.py
tests/test_observer/test_story_thread_builder.py
tests/test_narrative/test_narrative_export.py
```

---

## 16. README용 최종 문구

```md
# WITNESS

WITNESS is a world-first narrative mining engine.

It runs a pressure-driven multi-agent simulation, observes changes across agents, groups, and world-level pressures, then mines multiple emergent story threads from the simulation trace.

Unlike a scripted story generator, WITNESS does not start with a fixed protagonist or plot. It simulates the world first, then extracts usable narrative opportunities such as character arcs, relationship fractures, conflict seeds, and episode candidates.
```

한국어 버전:

```md
# WITNESS

WITNESS는 세계 우선형 서사 채굴 엔진입니다.

압력 기반 다중 에이전트 시뮬레이션을 구동한 뒤, 인물·집단·세계 압력의 변화를 관찰하고, 그 안에서 발생한 여러 서사 스레드 후보를 추출합니다.

WITNESS는 고정된 주인공이나 플롯에서 시작하지 않습니다. 먼저 세계를 구동하고, 그 결과로 쌓인 인물 변화, 관계 균열, 갈등 씨앗, 에피소드 후보를 창작자가 선택할 수 있는 형태로 정리합니다.
```

---

## 17. 성공 기준

이 작업이 성공했는지는 다음 질문으로 판단한다.

```text
1. 세계를 구동한 결과 여러 개의 Story Thread가 나오는가?
2. 특정 인물 하나에 하드코딩되어 있지 않은가?
3. 각 Thread가 최소 3개 이상의 Moment로 구성되는가?
4. 시작과 끝 사이에 상태 변화가 있는가?
5. 관계 변화나 갈등 누적이 보이는가?
6. 창작자가 영화/소설/게임/방송 중 어디에 쓸 수 있을지 판단 가능한가?
7. 각 판단의 근거가 source_derived / source_inferred로 구분되는가?
8. 정적 HTML 콘솔에서 직관적으로 확인 가능한가?
```

---

## 18. 최종 요약

현재 WITNESS는 사건 후보 감지에는 강하지만, 이야기의 축적을 보여주기에는 부족하다.

따라서 다음 단계는 Visual 재개나 Report 강화가 아니라, **Moment를 연결해 Story Thread를 채굴하는 Narrative Mining Layer**를 추가하는 것이다.

핵심 전환:

```text
Before:
무슨 사건이 감지됐는가?

After:
이 세계 안에서 어떤 이야기가 자라고 있는가?
```

최종 목표:

```text
세계를 구동한다.
변화가 쌓인다.
여러 서사 후보가 나온다.
창작자는 그중 쓸 만한 것을 고른다.
```
