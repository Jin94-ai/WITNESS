# WITNESS — 이야기가 나오기까지의 구현 단계 계획서

> 목적: 현재 WITNESS의 `Moment → StoryThread → NarrativeOpportunity` 파이프라인을 기반으로, 실제 창작자가 이해하고 선택할 수 있는 “이야기 후보”가 나오기까지 필요한 단계를 구현 가능한 단위로 정리한다.
>
> 핵심 원칙: **세계가 먼저 구동되고, 이야기는 나중에 채굴된다.**  
> 한 인물의 하드코딩된 플롯을 뽑는 것이 아니라, 세계 전체에서 발생한 여러 변화 흐름 중 창작 가능한 서사 후보를 선별한다.

---

## 0. 현재 위치

현재 WITNESS는 다음 단계까지 구현된 상태로 본다.

```text
Simulation dump
→ Moment
→ MomentLink
→ StoryThread
→ NarrativeOpportunity
→ Static Mining Console
```

현재 결과물은 “완성된 이야기”가 아니라 **이야기 가능성 카드**다.

현재 강점:

- 세계 상태 변화 감지 가능
- 에이전트 상태 변화 감지 가능
- 집단 압력 변화 감지 가능
- 여러 Moment를 Thread로 연결 가능
- StoryThread별 conflict / arc / score 추론 가능
- provenance class로 근거 추적 가능

현재 약점:

- `agent_03` 같은 익명 ID라 감정적으로 이해하기 어렵다.
- tick과 수치 중심이라 장면성이 약하다.
- conflict label과 logline이 템플릿 기반이라 반복적이다.
- 관계 변화가 충분히 서사적으로 표현되지 않는다.
- “이야기 후보”와 “실제 이야기 소재” 사이에 한 단계가 더 필요하다.

---

## 1. 최종 목표

WITNESS의 최종 출력은 소설 본문이나 시나리오 본문이 아니다.

최종 목표는 다음과 같다.

```text
세계 시뮬레이션을 돌린다.
→ 여러 인물과 집단의 압력, 선택, 관계 변화가 쌓인다.
→ 그중 서사로 발전 가능한 흐름을 찾는다.
→ 창작자가 방송, 소설, 영화, 게임에 쓸 수 있는 이야기 후보 카드로 본다.
```

즉 최종 산출물은 **Story Candidate Pack**이다.

예상 출력:

```text
Story Candidate S01
Title: Loyalty Under Survival Pressure
Main characters: Peter, Guard Group, Crowd
Core conflict: Loyalty vs Survival
Arc: Loyal presence → fear → withdrawal → shame
Key relationship: Peter ↔ Disciple Group
Usable formats: film scene, novel chapter, game quest branch
Why it matters: A clear internal conflict accumulates across multiple pressure events.
Evidence: 21 linked moments, 3 pressure types, 1 unresolved thread
```

---

## 2. 전체 단계

이야기가 나오기까지의 단계는 7단계로 나눈다.

```text
Stage 1. World Run
Stage 2. Moment Extraction
Stage 3. Moment Linking
Stage 4. Story Thread Mining
Stage 5. Context Enrichment
Stage 6. Story Candidate Formation
Stage 7. Creative Output Packaging
```

현재 Stage 1~4는 기본 구현되어 있다.  
앞으로 중요한 것은 Stage 5~7이다.

---

# Stage 1. World Run

## 목적

압력 기반 세계를 구동해 raw simulation dump를 만든다.

## 입력

```text
scenario config
seed
agent profiles
world rules
hazard functions
trigger rules
```

## 출력

```text
200 ticks × N agents × state snapshots
triggered events
world snapshots
group snapshots
agent snapshots
```

## 핵심 데이터

```text
agent.fear
agent.hope
agent.shame_self
agent.dominant_state
group.tension
group.dominant_mode
world.public_suspicion
world.authority_vigilance
world.blame_concentration
world.crowd_mood
active_events
```

## 구현 상태

이미 존재한다고 본다.

## 추가 작업

없음. 단, 이후 단계에서 쓰기 위해 dump schema가 안정적이어야 한다.

---

# Stage 2. Moment Extraction

## 목적

raw tick stream에서 의미 있는 변화 단위를 뽑는다.

Moment는 아직 이야기가 아니다.  
Moment는 “서사 재료가 될 수 있는 변화”다.

## Moment 유형

```text
agent_state_shift
relationship_drift
group_tension_shift
world_pressure_shift
choice_pattern
conflict_marker
event_ripple
unresolved_thread
```

## 추출 기준 예시

### 2.1 Agent State Shift

```text
fear가 threshold 이상 상승
hope가 threshold 이상 하락
shame_self가 누적 상승
dominant_state가 calm → tense → fragmenting으로 변화
```

### 2.2 Group Tension Shift

```text
group.tension이 급상승
group.dominant_mode가 partial → split으로 변화
member_count 변화와 tension 변화가 동시에 발생
```

### 2.3 World Pressure Shift

```text
authority_vigilance 상승
public_suspicion 상승
blame_concentration 상승
crowd_mood가 calm → agitated → tense로 변화
```

### 2.4 Conflict Marker

```text
agent fear 상승 + authority_vigilance 상승
hope 하락 + shame 상승
group tension 상승 + blame concentration 상승
```

### 2.5 Unresolved Thread

```text
특정 pressure가 일정 tick 이상 유지됨
fear > 7.0이 10 ticks 이상 지속
relationship distance가 회복되지 않음
world suspicion이 낮아지지 않음
```

## 출력 예시

```json
{
  "moment_id": "M_t072_agent_03_fear",
  "tick": 72,
  "tick_range": [70, 74],
  "moment_type": "agent_state_shift",
  "agents": ["agent_03"],
  "groups": ["L1"],
  "pressures": ["fear"],
  "delta": 1.6,
  "salience_score": 0.72,
  "provenance": "source_derived"
}
```

## 구현 상태

기본 구현 완료.

## 보강 작업

- relationship_drift moment가 약하면 추가 구현한다.
- choice_pattern moment가 없다면 행동 로그 기반으로 추가한다.
- unresolved_thread 기준을 명확히 문서화한다.

---

# Stage 3. Moment Linking

## 목적

개별 Moment들을 연결해 변화 흐름을 만든다.

하나의 Moment는 사건 조각이다.  
여러 Moment가 연결되어야 이야기 가능성이 생긴다.

## 링크 유형

```text
same_agent
same_group
same_relationship
same_pressure
same_conflict_axis
temporal_continuity
causal_suggestion
```

## 연결 기준

### 3.1 same_agent

같은 agent가 반복적으로 등장하면 연결한다.

```text
agent_03 fear rise
→ agent_03 shame rise
→ agent_03 withdrawal state
```

### 3.2 same_group

같은 group에서 긴장 변화가 반복되면 연결한다.

```text
L1 tension rise
→ L1 split mode
→ L1 member salient persistence
```

### 3.3 same_pressure

같은 압력이 여러 위치에서 반복되면 연결한다.

```text
authority_vigilance rise
→ agent fear rise
→ public_suspicion rise
```

### 3.4 same_conflict_axis

같은 갈등 축에 속하는 Moment들을 연결한다.

```text
fear + authority → loyalty_vs_survival
shame + hope_down → identity_vs_failure
blame + group_tension → scapegoating
```

### 3.5 temporal_continuity

시간상 가까운 Moment를 연결한다.  
단, 이 링크는 너무 많이 생기면 전체가 mega-thread로 합쳐질 수 있으므로 thread mining에서는 낮은 가중치로 사용한다.

## 출력 예시

```json
{
  "link_id": "L_M001_M008_same_agent",
  "source_moment_id": "M_t034_agent_03_fear",
  "target_moment_id": "M_t058_agent_03_shame",
  "link_type": "same_agent",
  "weight": 0.85,
  "reason": "same agent appears across pressure shifts"
}
```

## 구현 상태

기본 구현 완료.

## 보강 작업

- `same_relationship` 링크 추가 또는 강화
- `causal_suggestion`은 보수적으로 구현
- temporal link는 thread 생성 시 가중치 제한

---

# Stage 4. Story Thread Mining

## 목적

연결된 Moment 묶음 중 서사 가능성이 있는 흐름을 StoryThread로 승격한다.

StoryThread는 아직 완성된 이야기가 아니다.  
StoryThread는 “이야기로 발전 가능한 변화 흐름”이다.

## Thread 생성 방식

단순 connected component는 금지한다.  
temporal_continuity 때문에 모든 Moment가 하나의 mega-thread로 합쳐질 위험이 있다.

권장 방식:

```text
agent-centric mining
+ conflict-axis grouping
+ pressure bridge
+ group context attachment
```

## Thread 최소 조건

StoryThread로 인정하려면 아래 조건 중 다수를 만족해야 한다.

```text
- 3개 이상의 Moment 포함
- 시작 상태와 끝 상태가 다름
- 같은 agent 또는 group이 반복 등장
- 같은 conflict axis가 반복됨
- pressure가 누적 또는 반전됨
- relationship drift 또는 group tension이 포함됨
- unresolved question이 남음
```

## Thread score 요소

```text
change_score          상태 변화 강도
continuity_score      시간적 연결성
conflict_score        갈등 축 명확성
relationship_score    관계/집단 변화 포함 여부
pressure_score        압력 종류와 누적성
resolution_gap_score  미해결성
multi_agent_score     다중 인물성
creative_use_score    활용 가능성
```

## 출력 예시

```json
{
  "thread_id": "T01",
  "title": "Loyalty Strained by Survival Pressure",
  "rank": "strong",
  "score": 0.802,
  "core_conflict": "loyalty_vs_survival",
  "arc_direction": "fear_to_withdrawal",
  "main_agents": ["agent_03"],
  "groups": ["L1"],
  "tick_span": [2, 197],
  "moment_ids": ["M_t002_agent_03_fear", "M_t015_conflict_authority_fear"],
  "pressure_history": ["fear", "authority_vigilance", "shame_self"],
  "unresolved_question": "Will the central agent stay in place or withdraw under pressure?"
}
```

## 구현 상태

기본 구현 완료.

## 보강 작업

- weak thread와 strong thread의 기준 명확화
- relationship 기반 thread를 별도 mining 가능하게 추가
- group-centric thread도 agent-centric과 병렬로 생성

---

# Stage 5. Context Enrichment

## 목적

StoryThread를 사람이 이해할 수 있게 만든다.

현재 약점은 `agent_03`, `L1`, `tick 72`, `fear rises` 같은 내부 데이터 표현이다.  
이 단계에서는 내부 ID를 창작자가 이해 가능한 맥락으로 변환한다.

## 5.1 Agent Identity Mapping

### 목적

익명 agent ID를 실제 인물 이름 / 역할 / 기능으로 매핑한다.

### 입력

```text
content/{anchor}/profile.json
content/{anchor}/characters.json
observer dump agent metadata
```

### 출력 예시

```json
{
  "agent_03": {
    "display_name": "Peter",
    "role": "disciple",
    "dramatic_function": "loyal follower under fear",
    "initial_desire": "remain loyal",
    "core_vulnerability": "fear of exposure"
  }
}
```

### 구현 우선순위

최우선.  
비용 대비 효과가 가장 크다.

---

## 5.2 Group Identity Mapping

### 목적

`L1`, `L2`, `L3`를 창작자가 이해할 수 있는 집단으로 변환한다.

### 출력 예시

```json
{
  "L1": {
    "display_name": "disciple cluster",
    "function": "loyalty group",
    "risk": "fragmentation under authority pressure"
  },
  "L2": {
    "display_name": "crowd cluster",
    "function": "public mood amplifier",
    "risk": "scapegoating"
  }
}
```

---

## 5.3 Pressure Translation

### 목적

수치 압력을 서사적 언어로 변환한다.

```text
fear rise → fear intensifies
hope down → resolve weakens
authority_vigilance rise → authority pressure closes in
blame_concentration rise → blame begins to concentrate
```

### 주의

이 단계는 소설 문장을 쓰는 것이 아니다.  
수치 변화를 사람이 읽을 수 있는 중립적 문장으로 바꾸는 것이다.

---

## 5.4 Event Context Attachment

### 목적

Moment 주변의 active_events를 붙여 “무슨 상황에서 변화가 생겼는지” 보여준다.

예시:

```text
Before:
agent_03 fear rises (+1.60)

After:
Peter's fear rises while authority pressure increases and guard_approaches is active.
```

### 구현 방식

각 Moment tick 기준으로:

```text
active_events_at_tick
world snapshot
group snapshot
nearby candidate
```

을 attach한다.

---

## Stage 5 출력 예시

```json
{
  "thread_id": "T01",
  "main_characters": ["Peter"],
  "supporting_groups": ["disciple cluster", "authority presence"],
  "translated_pressures": [
    "fear intensifies",
    "authority pressure closes in",
    "shame accumulates"
  ],
  "context_summary": "Peter remains near the group while authority pressure rises and fear persists across the run."
}
```

---

# Stage 6. Story Candidate Formation

## 목적

StoryThread를 창작자가 실제로 고를 수 있는 Story Candidate로 변환한다.

StoryThread는 데이터 구조다.  
StoryCandidate는 창작용 카드다.

## Story Candidate 필드

```text
story_candidate_id
title
one_line_premise
main_characters
supporting_characters_or_groups
core_conflict
arc_summary
key_turning_points
relationship_dynamics
world_pressure_context
unresolved_question
usable_formats
adaptation_hooks
evidence_summary
provenance_summary
risk_notes
```

---

## 6.1 One-line Premise 생성

### 목적

창작자가 5초 안에 이해할 수 있는 한 줄을 만든다.

### 나쁜 예

```text
agent_03 fear rises under authority_vigilance.
```

### 좋은 예

```text
A loyal follower tries to stay present as fear and public pressure slowly turn loyalty into silence.
```

### 구현 원칙

- 완성된 소설 문장 금지
- 과장된 감정 서술 금지
- 데이터 근거 없는 사건 추가 금지
- conflict + character role + pressure + arc를 포함

---

## 6.2 Arc Summary 생성

### 목적

이야기의 변화 방향을 압축한다.

예시:

```text
loyal presence → rising fear → social distance → shame accumulation → unresolved withdrawal
```

### 구현 방식

Moment sequence를 시간순으로 정렬하고, 주요 state transition만 남긴다.

---

## 6.3 Key Turning Points 생성

### 목적

Story Candidate 안에서 장면 후보가 될 수 있는 tick을 고른다.

선별 기준:

```text
salience 높은 Moment
conflict_marker
unresolved_thread 시작점
world pressure spike
relationship drift point
group split point
```

출력 예시:

```text
1. tick 15 — authority pressure rises while fear spikes.
2. tick 72 — group tension sharpens around the agent.
3. tick 142 — fear returns after a temporary drop.
4. tick 197 — unresolved fear remains near the end of the run.
```

---

## 6.4 Relationship Dynamics 생성

### 목적

이야기성을 강화하기 위해 관계 변화를 별도로 보여준다.

출력 예시:

```text
Peter ↔ Disciple Cluster:
The character remains tied to the group, but fear and shame increasingly isolate him from the group pressure field.
```

필요 데이터:

```text
same_group moments
relationship_drift moments
group tension shifts
agent dominant_state changes
```

---

## 6.5 Adaptation Hooks 생성

### 목적

방송, 소설, 영화, 게임에서 어떻게 쓸 수 있는지 제안한다.

출력 예시:

```text
Film scene:
A quiet scene where the character stays physically present but emotionally withdraws as authority pressure enters the room.

Novel chapter:
A chapter tracking the slow conversion of loyalty into fear-driven silence.

Game quest branch:
The player must choose whether to confess, hide, or stay silent as public suspicion rises.
```

주의:

- 이 단계는 창작 아이디어 제안이다.
- 실제 대사, 시나리오, 소설 본문 생성은 별도 directive가 있을 때만 한다.

---

## Stage 6 출력 예시

```json
{
  "story_candidate_id": "S01",
  "title": "Loyalty Under Survival Pressure",
  "one_line_premise": "A loyal follower tries to stay present as fear and public pressure slowly turn loyalty into silence.",
  "main_characters": ["Peter"],
  "supporting_characters_or_groups": ["disciple cluster", "authority presence"],
  "core_conflict": "loyalty_vs_survival",
  "arc_summary": "loyal presence → rising fear → withdrawal pressure → shame accumulation → unresolved silence",
  "key_turning_points": [
    {
      "tick": 15,
      "summary": "Authority pressure rises while fear spikes."
    },
    {
      "tick": 142,
      "summary": "Fear returns after temporary relief."
    }
  ],
  "relationship_dynamics": [
    "The character remains near the group but becomes increasingly isolated by fear."
  ],
  "world_pressure_context": [
    "authority pressure rises",
    "public suspicion remains active"
  ],
  "unresolved_question": "Will loyalty survive when silence becomes safer than presence?",
  "usable_formats": ["film_scene", "novel_chapter", "game_quest_branch"],
  "evidence_summary": "Built from 21 linked moments across fear, authority_vigilance, and shame_self.",
  "provenance_summary": {
    "source_derived": 18,
    "source_inferred": 3,
    "not_used": 0
  },
  "risk_notes": [
    "No dialogue generated.",
    "No unstated event added.",
    "Premise is inferred from pressure pattern, not directly authored by the engine."
  ]
}
```

---

# Stage 7. Creative Output Packaging

## 목적

Story Candidate를 포트폴리오와 창작 실무에서 볼 수 있는 형태로 출력한다.

출력은 세 가지가 필요하다.

```text
JSON ledger
Markdown cards
Static HTML console
```

---

## 7.1 JSON Ledger

기계가 다시 읽을 수 있는 원본 출력.

경로 예시:

```text
data/narrative/story_candidates.json
```

용도:

- 테스트
- 콘솔 렌더링
- cross-seed 비교
- 외부 도구 연결

---

## 7.2 Markdown Cards

사람이 읽는 리뷰용 문서.

경로 예시:

```text
docs/portfolio/STORY_CANDIDATES.md
```

구성:

```text
Executive Summary
Candidate Ranking
Story Candidate Cards
Evidence Summary
Limitations
Next Steps
```

---

## 7.3 Static HTML Console

포트폴리오 메인 surface.

경로 예시:

```text
docs/portfolio/story_candidate_console.html
```

화면 구성:

```text
[Run Summary]
[Story Candidate List]
[Selected Candidate Detail]
[Arc Timeline]
[Key Turning Points]
[Relationship Dynamics]
[Evidence / Provenance Toggle]
[Creative Use Tabs: Film / Novel / Game]
```

---

# 8. 구현 순서

## Phase A. Readability Fix

목표: 지금 산출물을 사람이 읽을 수 있게 만든다.

작업:

```text
A1. agent_id → display_name 매핑
A2. group_id → display_name 매핑
A3. pressure name → human-readable phrase 매핑
A4. active_events context attach
A5. 기존 NarrativeOpportunity 카드에 표시
```

예상 효과:

```text
agent_03 fear rises
→ Peter's fear intensifies as authority pressure rises.
```

우선순위: 최상

---

## Phase B. Story Candidate Model 추가

목표: StoryThread와 NarrativeOpportunity 사이에 창작용 모델을 추가한다.

신규 파일 후보:

```text
engine/observer/story_candidate.py
engine/observer/story_candidate_builder.py
scripts/narrative/build_story_candidates.py
```

핵심 dataclass:

```python
@dataclass(frozen=True)
class StoryCandidate:
    story_candidate_id: str
    source_thread_id: str
    title: str
    one_line_premise: str
    main_characters: tuple[str, ...]
    supporting_characters_or_groups: tuple[str, ...]
    core_conflict: str
    arc_summary: str
    key_turning_points: tuple[TurningPoint, ...]
    relationship_dynamics: tuple[str, ...]
    world_pressure_context: tuple[str, ...]
    unresolved_question: str
    usable_formats: tuple[str, ...]
    adaptation_hooks: dict[str, str]
    evidence_summary: str
    provenance_summary: dict[str, int]
    risk_notes: tuple[str, ...]
```

우선순위: 높음

---

## Phase C. Turning Point Selector

목표: thread 안에서 장면 후보가 될 핵심 moment를 선별한다.

선별 규칙:

```text
conflict_marker 우선
salience_score 상위
unresolved_thread 시작점
world pressure spike
group tension shift
agent dominant_state transition
```

출력:

```python
@dataclass(frozen=True)
class TurningPoint:
    tick: int
    moment_ids: tuple[str, ...]
    label: str
    summary: str
    provenance: ProvenanceClass
```

우선순위: 높음

---

## Phase D. Relationship Dynamics Builder

목표: thread가 단순 개인 감정선으로 보이지 않게 관계 축을 만든다.

입력:

```text
same_group links
relationship_drift moments
group_tension_shift moments
agent state changes
```

출력 예시:

```text
Peter remains connected to the disciple cluster, but rising fear and shame weaken his effective participation.
```

주의:

- 실제 relationship score가 없으면 “관계 변화”라고 과장하지 말 것.
- group co-presence와 group pressure만 있으면 “relationship context”로 낮춰 표현할 것.

우선순위: 중간

---

## Phase E. Cross-seed Story Pattern Mining

목표: 단일 실행에서 나온 후보가 우연인지, 세계 구조가 반복적으로 낳는 패턴인지 확인한다.

입력:

```text
seed 0~4 또는 0~9
각 seed의 StoryCandidate JSON
```

출력:

```text
conflict_family frequency
arc_direction frequency
recurring character involvement
robust story candidates
seed-specific anomalies
```

예시:

```text
loyalty_vs_survival appeared in 4/5 seeds.
control_vs_exposure appeared in 2/5 seeds.
identity_vs_failure appeared in 1/5 seeds.
```

우선순위: 중간~높음

포트폴리오 효과가 큼.

---

## Phase F. Console Upgrade

목표: Narrative Mining Console을 Story Candidate Console로 바꾼다.

필수 UI:

```text
Candidate ranking
Arc timeline
Turning point list
Character / group context
Creative use tabs
Evidence toggle
Seed robustness badge, if Phase E exists
```

금지:

```text
픽셀 캐릭터 애니메이션
컷신
스토리 렌더러
대사 자동 생성
근거 없는 장면 연출
```

우선순위: 중간

---

# 9. 검증 기준

## 9.1 Unit Tests

필수 테스트:

```text
test_agent_identity_mapping.py
test_group_identity_mapping.py
test_story_candidate_builder.py
test_turning_point_selector.py
test_story_candidate_provenance.py
test_no_unbacked_story_claims.py
test_cross_seed_pattern_summary.py
```

---

## 9.2 Regression Tests

기존 테스트는 유지한다.

```text
Moment extraction count가 의도 없이 급변하지 않는지
Thread count가 mega-thread로 붕괴하지 않는지
StoryCandidate가 source 없는 claim을 만들지 않는지
Visual staged data가 story candidate에 섞이지 않는지
```

---

## 9.3 Human Review Checklist

각 StoryCandidate는 아래 질문에 답해야 한다.

```text
1. 5초 안에 무슨 이야기 후보인지 이해되는가?
2. 주인공 또는 중심 집단이 보이는가?
3. 갈등 축이 명확한가?
4. 시작과 끝의 변화가 있는가?
5. 최소 2~3개의 turning point가 있는가?
6. 창작자가 film / novel / game 중 하나로 가져갈 수 있는가?
7. 근거 없는 사건이나 감정 서술이 추가되지 않았는가?
8. 데이터 카드가 아니라 이야기 가능성 카드처럼 보이는가?
```

---

# 10. 금지 사항

## 10.1 하드코딩 금지

금지:

```text
Peter는 반드시 배신한다
Judas는 반드시 죄책감을 느낀다
이 시점에서는 반드시 체포가 일어난다
특정 인물 중심으로만 story candidate 생성
```

허용:

```text
Peter에게 fear와 shame이 누적되어 loyalty_vs_survival thread가 형성됨
특정 seed에서 Peter 중심 thread가 strong으로 분류됨
다른 seed나 anchor에서는 다른 thread가 나올 수 있음
```

---

## 10.2 Story Renderer 회귀 금지

금지:

```text
완성된 소설 본문 생성
대사 생성
영화 시나리오 생성
감정 과잉 문장 생성
근거 없는 장면 묘사
```

허용:

```text
one-line premise
arc summary
turning point summary
adaptation hook
creative use suggestion
```

---

## 10.3 Visual Cutscene 회귀 금지

금지:

```text
픽셀 월드 재개
캐릭터 애니메이션
hand-staged scene
speech bubble staging
```

허용:

```text
arc timeline
pressure chart
relationship map
evidence toggle
candidate card UI
```

---

# 11. 성공 기준

최소 성공 기준:

```text
각 strong StoryThread에서 StoryCandidate가 생성된다.
StoryCandidate는 이름, 갈등, arc, turning point, 활용처를 포함한다.
각 문장은 source_derived 또는 source_inferred 근거를 가진다.
agent_03 같은 익명 ID가 메인 출력에 그대로 노출되지 않는다.
창작자가 5초 안에 후보의 방향을 이해할 수 있다.
```

좋은 성공 기준:

```text
한 run에서 3~5개의 서로 다른 StoryCandidate가 나온다.
각 후보가 서로 다른 conflict axis를 가진다.
film / novel / game 활용 hook이 다르게 제시된다.
cross-seed에서 반복적으로 나타나는 story pattern을 보여준다.
HTML console에서 arc와 evidence를 동시에 확인할 수 있다.
```

최종 성공 기준:

```text
WITNESS를 본 사람이 “이 세계에서 여러 이야기 후보가 자연스럽게 나왔고, 나는 그중 하나를 골라 발전시킬 수 있겠다”고 느낀다.
```

---

# 12. 권장 구현 우선순위

```text
1. Agent / Group identity mapping
2. StoryCandidate dataclass + builder
3. TurningPoint selector
4. StoryCandidate Markdown export
5. StoryCandidate JSON ledger
6. Existing console upgrade
7. Cross-seed pattern summary
8. Controlled natural-language enrichment
```

---

# 13. 최종 포지셔닝 문장

영문:

```text
WITNESS is a world-first narrative mining engine. It runs a pressure-driven multi-agent world, connects accumulated changes into story threads, and surfaces multiple story candidates that creators can adapt for film, fiction, broadcast, or games.
```

한국어:

```text
WITNESS는 세계 우선 서사 채굴 엔진이다. 압력 기반 다중 에이전트 세계를 구동하고, 그 안에서 누적된 변화를 서사 스레드로 연결한 뒤, 창작자가 골라 쓸 수 있는 여러 이야기 후보를 제시한다.
```

---

# 14. 에이전트 작업 지시 요약

에이전트는 다음 순서대로 작업한다.

```text
[1] 기존 NarrativeOpportunity 출력 확인
[2] agent_id / group_id 매핑 데이터 위치 확인
[3] Context Enrichment 모듈 추가
[4] StoryCandidate dataclass 추가
[5] StoryCandidate builder 구현
[6] TurningPoint selector 구현
[7] Markdown export 구현
[8] JSON ledger export 구현
[9] 기존 console에 StoryCandidate view 추가
[10] 테스트 추가
[11] 기존 report / visual / engine layer는 수정하지 않음
```

절대 하지 말 것:

```text
engine core 수정
visual track 재개
story_renderer 재개
대사 / 소설 / 시나리오 본문 생성
특정 인물 플롯 하드코딩
```

---

# 15. 결론

현재 WITNESS는 “이야기 가능성 채굴”까지 도달했다.  
다음 단계는 더 많은 엔진을 만드는 것이 아니라, 이미 채굴된 thread를 창작자가 이해할 수 있는 **Story Candidate**로 승격하는 것이다.

핵심 전환은 다음 한 줄이다.

```text
StoryThread는 데이터 구조다.
StoryCandidate는 창작자가 고를 수 있는 이야기 재료다.
```

따라서 다음 구현은 Stage 5~7에 집중한다.

```text
Context Enrichment
→ Story Candidate Formation
→ Creative Output Packaging
```

이 세 단계를 완료하면 WITNESS는 단순한 시뮬레이션 보고서나 사건 감지기를 넘어, 실제 창작 파이프라인에 넣을 수 있는 Narrative Mining Engine으로 보일 수 있다.
