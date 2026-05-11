# WITNESS — World Observer Layer 설계안

## 0. 문서 목적

이 문서는 WITNESS 프로젝트를  
현재의 **“압력 → 시뮬레이션 → 스토리 출력” 구조**에서 한 단계 확장하여,

> **실시간으로 흐르는 세계를 전지적 관찰자 시점에서 살펴보고,  
> 필요하면 인물 중심 / 사건 중심 / 집단 중심 / 세계 전체 흐름으로 자유롭게 전환해서 볼 수 있게 하는 관찰 계층**
을 설계하기 위한 문서다.

이 문서의 목적은 다음 네 가지다.

1. World Observer Layer의 역할 정의
2. 필요한 기능을 계층별로 분해
3. MVP 범위와 장기 확장 범위를 구분
4. Claude Code가 실제로 구현 가능한 작업 순서 제시

---

## 1. 왜 이 레이어가 필요한가

현재 WITNESS는 기본적으로 다음 구조에 가깝다.

- 특정 압력 / 사건 입력
- 시뮬레이션 실행
- 결과 trajectory / probe 생성
- story renderer가 한글 이야기 출력

이 구조는 **사후 렌더링(post-hoc rendering)** 에 강하다.  
즉, 이미 끝난 결과를 이야기로 읽는 데는 적합하다.

하지만 Lee가 원하는 것은 그보다 한 단계 위다.

### 원하는 것
- 세계가 실시간으로 흐르는 걸 본다
- 필요하면 한 인물에 붙는다
- 필요하면 군중/권위/전체 흐름을 본다
- 중요한 순간만 추려서 본다
- 하나의 이야기뿐 아니라 다양한 시점/거리에서 살펴본다

즉 현재는 “결과물 생성기”라면,
앞으로는 **“흐르는 세계를 관찰하는 층”** 이 필요하다.

---

## 2. 핵심 정의

## World Observer Layer란?

World Observer Layer는  
**시뮬레이션이 생성하는 상태 변화를 실시간 혹은 리플레이 가능한 관찰 단위로 구조화하고,  
그것을 다양한 관찰 렌즈(Person / Group / Event / World)로 조회하게 해주는 계층**이다.

### 이 레이어가 하는 일
- 세계 상태를 tick 단위로 기록
- 중요한 변화(salience)를 추출
- 특정 인물/사건/집단/세계 전체 관점에서 재구성
- 필요한 구간만 잘라서 보여줌
- 이후 story renderer가 이 관찰 결과를 바탕으로 이야기로 바꿀 수도 있게 함

### 이 레이어가 하지 않는 일
- “좋은 이야기”라고 판정하지 않음
- 창작적 가치 평가를 자동화하지 않음
- 특정 해석을 정답으로 고정하지 않음

즉 이 레이어는 **판정기**가 아니라 **관찰기 / 탐색기**다.

---

## 3. 상위 아키텍처

현재 구조:
```text
Pressure/Event Input
    ↓
Simulation Engine
    ↓
Trajectory / Probe
    ↓
Story Renderer
```

확장 구조:
```text
Pressure/Event Input
    ↓
Simulation Engine
    ↓
World Snapshot Stream
    ↓
World Observer Layer
    ├─ Person View
    ├─ Group View
    ├─ Event View
    ├─ World View
    ├─ Salience List
    └─ Replay / Filter / Zoom
    ↓
(선택) Story Framer / Story Renderer
```

핵심 변화는:
- Story는 이제 유일한 출력이 아님
- 먼저 **세계를 보는 층**이 생기고
- Story는 그 위의 한 출력 방식으로 내려감

---

## 4. 필요한 핵심 기능 6가지

## 4.1 World Snapshot Recorder
먼저 세계를 “볼 수 있게” 기록해야 한다.

### 기능
매 tick 또는 일정 간격마다 세계 상태를 공통 schema로 저장한다.

### 최소 저장 대상
- tick / time
- active events
- 인물별 주요 상태 변화량
- crowd mood
- blame concentration
- public suspicion
- authority vigilance
- resource pressure (scarcity 등)
- 지역별/코호트별 긴장도
- top target / top tension / top divergence

### 목적
- 리플레이 가능성 확보
- 다양한 렌즈의 공통 입력 확보
- post-hoc story뿐 아니라 real-time observation 가능

---

## 4.2 Multi-view Observer
같은 세계를 여러 시점으로 볼 수 있어야 한다.

### A. Person View
특정 인물 중심으로 보는 시점

예:
- 현재 fear / shame / loyalty / trust 흐름
- 최근 어떤 사건을 겪었는가
- 어떤 turning point가 있었는가
- 이 인물 arc는 recovery / saturation / mixed 중 어디로 가는가

### B. Group View
코호트 / 지역 / 역할군 단위로 보는 시점

예:
- 어느 집단이 갈라지고 있는가
- 누가 회복 / 고착으로 가는가
- group-level blame / tension / cohesion은 어떤가

### C. Event View
한 사건 중심으로 보는 시점

예:
- accusation 하나가 어디로 퍼졌는가
- sacred sign이 누구에게 영향을 줬는가
- event effect가 언제 사라졌는가

### D. World View
세계 전체 흐름 시점

예:
- 군중 분위기 변화
- 권위 시선 증감
- 비난 집중
- 의심 잔존
- 세계 phase 전이

---

## 4.3 Zoom / Distance Control
전지적 관찰자라면 가까이도 보고 멀리도 봐야 한다.

### Zoom 1 — Macro
- 세계 전체 phase
- 주요 압력선
- 큰 전환점
- dominant forces

### Zoom 2 — Meso
- 집단 / 지역 / 코호트
- split / divergence / local saturation
- event propagation

### Zoom 3 — Micro
- 특정 인물
- 특정 interaction
- 특정 장면
- 특정 tick window

### 목적
- 정보 과부하 방지
- 같은 데이터도 거리만 바꿔서 다르게 보게 함

---

## 4.4 Salience Detector
실시간 세계는 너무 많은 정보가 흐르므로,  
무엇이 중요한지 자동으로 표시해야 한다.

### 감지 후보
- pressure spike
- blame target shift
- authority vigilance spike
- public suspicion jump
- cohort split 발생
- recovery turning point
- saturation lock
- low-activity but meaningful tension
- 특정 인물 state 급변
- event ripple 확대

### 출력 형태
- top 5 salient moments
- top 3 unstable agents
- top 3 emerging world tensions
- current strongest event ripple

### 목적
- “지금 뭘 봐야 하는가”를 알려줌
- 관찰자가 막연히 로그를 다 뒤지지 않게 함

---

## 4.5 Replay / Jump / Bookmark
실시간으로만 보면 중요한 걸 놓친다.

### 기능
- 특정 tick로 이동
- 특정 event 시작점으로 점프
- turning point bookmark
- 특정 인물 arc의 결정적 순간 모아보기
- 최근 N ticks replay
- before / after 비교

### 예시
- “tick 17 accusation 발생 지점으로 이동”
- “베드로 arc turning point 3개만 보기”
- “world phase transition 구간만 보기”

---

## 4.6 Filter / Search / Compare
관찰이 쉬워지려면 해석기를 더 넣는 게 아니라, 찾기 쉬워야 한다.

### 필터 예시
- by person
- by event
- by location
- by pressure type
- by outcome type (recovery / saturation / mixed / low activity)
- by world-heavy moments
- by split-heavy moments
- by low-activity but high-potential moments

### 비교 예시
- same anchor, different seeds
- same scenario, different outcomes
- person view vs world view
- accusation vs scarcity vs sacred

---

## 5. 핵심 데이터 구조

## 5.1 Snapshot Schema (MVP)
```json
{
  "tick": 17,
  "active_events": ["public_accusation"],
  "world": {
    "crowd_mood": "tense",
    "blame_concentration": 0.82,
    "public_suspicion": 0.71,
    "authority_vigilance": 0.43,
    "scarcity_pressure": 0.20
  },
  "groups": [
    {"id": "L1", "dominant_mode": "saturation", "tension": 0.88},
    {"id": "L2", "dominant_mode": "mixed", "tension": 0.64}
  ],
  "agents": [
    {"id": "peter", "fear": 7.2, "shame_self": 6.1, "delta": ["fear_up", "resolve_down"]},
    {"id": "crowd_01", "anger": 4.8}
  ],
  "salience_hints": ["blame_target_shift", "accusation_spike"]
}
```

---

## 5.2 View Query Examples
```python
observer.get_world_view(tick=120)
observer.get_person_view(agent_id="peter", tick=120)
observer.get_group_view(group_id="L2", tick=120)
observer.get_event_view(event_id="public_accusation")
observer.get_salience_window(tick_from=100, tick_to=140)
observer.compare_anchor_seeds(anchor="peter_scarcity_baseline")
```

---

## 5.3 Observer Output Examples
### World View Output (텍스트)
- 현재 세계는 accusation 이후 비난이 한 대상에 집중되고 있다.
- 의심은 아직 내려가지 않았고, 권위의 시선도 느슨해지지 않았다.
- L1은 고착, L2는 분기, L3는 회복 직전이다.

### Person View Output (텍스트)
- 베드로는 최근 8 ticks 동안 fear가 급상승했고 resolve가 흔들렸다.
- accusation 직후 shame_self가 상승했고, 이후 loyalty가 흔들리는 징후가 있다.
- 현재 arc는 saturation에 가까워지고 있다.

---

## 6. 하드코딩 위험을 피하는 원칙

이 레이어는 해석기처럼 보일 수 있으므로, 다음 원칙이 중요하다.

### 원칙 1
시스템은 **관측 태그**까지만 만든다.

허용:
- accusation_spike
- blame_target_shift
- recovery_turning_point
- saturation_lock
- split_detected

비허용:
- “이건 훌륭한 회복 서사다”
- “이건 asset 가치가 높다”
- “이건 좋은 이야기다”

### 원칙 2
여러 렌즈를 제공하되, 하나를 정답으로 고정하지 않는다.

### 원칙 3
해석보다 **탐색 가능성**을 높인다.
즉:
- 필터
- 정렬
- 비교
- 점프
가 더 중요하다.

---

## 7. MVP 범위

처음부터 UI까지 다 만들 필요 없다.  
MVP는 **텍스트 기반 World Observer**로 충분하다.

## MVP 포함
1. Snapshot Recorder
2. World View
3. Person View
4. Event View
5. Salience Top 5
6. Jump / Replay (기본)
7. Anchor seed comparison (최소)

## MVP 제외
- full GUI
- live interactive dashboard
- fine-grained aesthetics
- evaluator automation
- story quality scoring
- public-facing polished browser

---

## 8. 추천 구현 순서

## Phase O1 — Snapshot Recorder
### 산출물
- `engine/observer/snapshot_schema.py`
- `engine/observer/recorder.py`

### 목표
시뮬레이션 tick 상태를 observer-friendly schema로 저장

---

## Phase O2 — Observer Core API
### 산출물
- `engine/observer/core.py`

### 최소 API
- `get_world_view`
- `get_person_view`
- `get_event_view`
- `get_salience_list`

---

## Phase O3 — Text Observer Reports
### 산출물
- `scripts/observer/observer_report.py`

### 지원 출력
- 현재 세계 요약
- 특정 인물 요약
- 최근 salient moment 요약
- 특정 event ripple 요약

---

## Phase O4 — Replay / Jump
### 산출물
- `engine/observer/replay.py`

### 기능
- tick jump
- event jump
- turning point bookmarks
- recent window replay

---

## Phase O5 — Multi-lens Compare
### 산출물
- `scripts/observer/compare_views.py`

### 기능
- same tick: world vs person vs event
- same anchor: seed 5개 비교

---

## 9. Claude Code용 구현 지시

### Step 1
`docs/observer/WORLD_OBSERVER_LAYER_SPEC.md` 작성  
(이 문서를 canonical spec으로 옮기기)

### Step 2
snapshot schema 정의

### Step 3
observer core API 최소 구현

### Step 4
텍스트 기반 observer report 생성기 구현

### Step 5
salience detector 최소 구현

### Step 6
jump / replay 최소 구현

### Step 7
anchor seed comparison 텍스트 출력 구현

---

## 10. 지금 하지 말아야 할 것

- world observer를 곧바로 public UI로 만들기
- story evaluator처럼 해석 결과를 고정하기
- “좋은 이야기/나쁜 이야기” 자동 판정 넣기
- branch C / renderer 문제와 observer 레이어를 한 번에 같이 풀기
- GUI부터 만들기

지금은 **관찰 계층의 기능적 MVP**가 먼저다.

---

## 11. 이 레이어가 프로젝트에 주는 가치

### 11.1 Story 이전의 관찰 가능성
이제는 결과 story만 보지 않고,  
**이야기가 자라는 세계 자체**를 볼 수 있게 된다.

### 11.2 디버깅 강화
왜 어떤 variation이 약한지,  
왜 world-side가 안 보이는지,  
왜 특정 인물 arc가 죽는지 더 잘 보인다.

### 11.3 Lee의 판독 효율 향상
고정 해석문 없이도:
- 인물 중심
- 사건 중심
- 세계 중심
- 시간 구간 중심
으로 쉽게 훑어볼 수 있게 된다.

### 11.4 장기적으로 Narrative Witness Layer 기반
향후 v2.0의 interactive 체험 계층으로 자연스럽게 이어질 수 있다.

---

## 12. 최종 한 줄 요약

**World Observer Layer는 지금의 ‘압력 → story’ 구조 위에,  
흐르는 세계를 전지적 관찰자 시점에서 실시간/리플레이 방식으로 살펴볼 수 있게 하는 관찰 계층이다.  
핵심은 story quality를 자동 평가하는 것이 아니라,  
인물/사건/집단/세계 시점과 줌 레벨을 바꿔가며 같은 세계를 자유롭게 들여다볼 수 있게 만드는 것이다.**
