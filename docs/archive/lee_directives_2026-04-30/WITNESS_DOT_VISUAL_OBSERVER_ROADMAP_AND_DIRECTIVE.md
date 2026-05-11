# WITNESS — Dot Visual Observer 로드맵 및 다음 작업 지시서

## 0. 문서 목적

이 문서는 WITNESS 프로젝트의 현재 방향성을 재정렬하고,  
최종 목표까지의 로드맵과 지금 당장 해야 할 작업을 정리한 실행 지시서다.

핵심 판단은 다음과 같다.

> **WITNESS의 최종 목표는 “텍스트 이야기 생성기”가 아니라,  
> 실시간으로 흐르는 세계를 관찰하고, 필요하면 특정 인물/사건/집단/세계 흐름으로 줌인할 수 있는 세계 관찰·탐색 시스템이다.**

텍스트 출력은 최종 목적지가 아니다.  
텍스트는 지금까지 세계가 실제로 이야기성을 갖고 흐르는지 검증하기 위한 **저비용 관찰 레이어**였다.

이제 Observer Layer와 Candidate Pipeline이 어느 정도 성립했으므로,  
다음 단계는 고퀄리티 비주얼이 아니라 **도트 기반 Visual Observer MVP**로 넘어가는 것이다.

---

## 1. 현재 프로젝트 위치

현재 WITNESS는 아래 단계까지 도달했다.

### 1.1 World / Person Engine
- 인물 상태 변화
- 세계 압력
- 사건 전파
- group / cohort 분기
- Branch C configuration sensitivity

이 축은 이미 충분히 검증되었다.

### 1.2 Story Output Layer
- 한글 story renderer 존재
- Renderer Cycle 7에서 freeze
- creative asset pack v1 존재
- story output은 가능함

다만 이 레이어는 최종 목적지가 아니라  
**세계 흐름을 사람이 이해하기 위한 텍스트 관찰 방식**이다.

### 1.3 Observer Layer
- Snapshot
- World View
- Person View
- Event View
- Compare View
- Replay / Jump
- Candidate extraction
- Candidate curation

여기까지 구축되었다.

### 1.4 현재 상태의 의미
지금 프로젝트는 더 이상  
“세계가 흐르는지 모르겠다” 단계가 아니다.

현재 질문은:

> **이제 그 흐르는 세계를 어떻게 더 직관적으로 볼 것인가?**

이다.

---

## 2. 최종 목표 정의

## 최종 목표
WITNESS는 장기적으로 다음 형태를 지향한다.

> **도트 기반으로 흐르는 세계를 실시간/리플레이로 관찰하고,  
> 인물·집단·사건·세계 흐름을 자유롭게 줌인/줌아웃하며,  
> 그 안에서 이야기 후보를 발견하고, 필요하면 텍스트 story로 확인할 수 있는 시스템.**

즉 최종 구조는 다음과 같다.

```text
World Simulation
    ↓
World Snapshot Stream
    ↓
Observer Layer
    ↓
Dot Visual Observer
    ├─ World View
    ├─ Group View
    ├─ Person View
    ├─ Event View
    ├─ Salience Markers
    ├─ Candidate Highlight
    └─ Text Story / Packet Panel
```

이 시스템은 게임이 아니다.  
처음 목표는 **관찰 가능한 움직이는 세계**다.

---

## 3. 텍스트 레이어에 대한 현재 판단

## 3.1 텍스트는 계속 개선해야 하는가?
현재 판단은:

> **대규모 텍스트 개선은 중지.  
> 텍스트는 freeze 상태로 두고, 관찰·선별·보조 설명 용도로 사용한다.**

### 이유
- renderer는 이미 Cycle 7까지 개선됨
- 더 고치면 과공학 가능성 큼
- 현재 병목은 문장 품질이 아니라 세계를 직관적으로 보는 방식
- 텍스트 story는 visual observer의 side panel / candidate detail로도 충분히 가치 있음

### 허용되는 텍스트 작업
- 오탈자 / 명백한 어색함 수정
- packet wording 소폭 개선
- story candidate 설명 간결화
- visual observer에 들어갈 짧은 summary 생성

### 금지되는 텍스트 작업
- Renderer Cycle 8
- 문체 profile 대확장
- 웹소설 톤 / 문학 톤 분기
- narrative summary template 대량 추가
- 텍스트 story를 최종 산출물처럼 계속 polish

즉 텍스트는 이제 **주연이 아니라 관찰 보조 패널**이다.

---

## 4. 비주얼 방향성

## 4.1 지금 비주얼은 “도트”로 충분하다
고퀄리티 캐릭터, 3D, 애니메이션, 웹툰식 장면은 아직 필요 없다.

초기 Visual Observer는 아래 정도면 충분하다.

- agent dot
- group zone
- color / size / opacity로 상태 표현
- timeline scrubber
- salience marker
- selected tick info panel
- selected agent/event detail panel

즉 목표는 예쁜 그래픽이 아니라:

> **세계가 움직인다는 것을 직관적으로 보는 것**

이다.

---

## 4.2 도트 시각화의 장점
도트 기반 MVP는 현재 프로젝트와 잘 맞는다.

### 장점
1. 구현 비용이 낮다
2. 인물 12명 / 그룹 3개 정도를 쉽게 표현 가능
3. pressure / mood / tension을 색과 크기로 표현 가능
4. tick replay와 잘 맞음
5. observer snapshot과 직접 연결 가능
6. story보다 먼저 “세계 흐름”이 보임

### 중요한 점
비주얼은 story를 대체하는 게 아니라,
**story 이전의 세계 관찰 도구**다.

---

## 5. 최종 로드맵

## Phase V0 — Text / Observer Freeze 정리
### 목표
현재 텍스트/observer 상태를 고정하고 Visual MVP로 넘어갈 준비.

### 해야 할 일
- renderer freeze 상태 유지
- observer/candidate pipeline 상태 문서화
- Visual Observer가 사용할 snapshot fields 확정

### 산출물
- `docs/visual/VISUAL_OBSERVER_INPUT_SCHEMA.md`

---

## Phase V1 — Dot Visual Observer MVP
### 목표
하나의 canonical run을 도트 기반으로 리플레이해서 볼 수 있게 한다.

### 입력
- `peter_scarcity_baseline`
- 200 ticks
- 12 agents
- 3 groups

### 화면 구성
1. **Timeline**
   - tick 이동
   - salience marker 표시

2. **World Panel**
   - crowd mood
   - blame concentration
   - public suspicion
   - authority vigilance

3. **Dot World View**
   - agent dots
   - group zones
   - color = dominant state 또는 mode
   - size/opacity = tension or salience

4. **Detail Panel**
   - selected agent / event / tick 정보
   - observer text summary
   - candidate link

### 산출물
- `visual/dot_observer.html` 또는 `examples/visual_dot_observer.py`
- `docs/visual/VISUAL_OBSERVER_MVP_REVIEW.md`

---

## Phase V2 — Interaction MVP
### 목표
도트를 클릭하거나 tick를 이동하며 관찰 가능하게 한다.

### 기능
- click agent → Person View
- click event marker → Event View
- click group → Group View
- tick scrubber
- candidate highlight
- selected candidate → story packet 보기

### 산출물
- `visual/dot_observer_interactive.html`
- `docs/visual/VISUAL_OBSERVER_INTERACTION_REVIEW.md`

---

## Phase V3 — Observer + Story Panel 통합
### 목표
visual observer에서 선택한 후보를 텍스트 story / packet으로 확인한다.

### 기능
- candidate list panel
- candidate click → packet 표시
- render story button or pre-rendered story panel
- person/event/world lens toggle

### 산출물
- `docs/visual/VISUAL_OBSERVER_STORY_PANEL_PLAN.md`
- demo output

---

## Phase V4 — Multi-anchor Expansion
### 목표
한 anchor 전용이 아닌지 확인한다.

### 대상
1. Peter scarcity
2. accusation canonical
3. 필요 시 Branch C selected run

### 검증 질문
- 같은 visual observer가 다른 pressure에서도 작동하는가?
- event-heavy run에서도 잘 보이는가?
- world-heavy run과 person-heavy run이 구분되는가?

---

## Phase V5 — Explorer Prototype
### 목표
visual observer를 단일 demo가 아니라 내부 탐색 도구로 만든다.

### 기능
- run selector
- candidate filter
- pressure filter
- outcome filter
- person/event/world lens 전환
- saved interesting moments

### 주의
아직 public product가 아니라 internal explorer다.

---

## Phase V6 — Playable / Intervention Prototype
### 목표
관찰자에서 개입자로 확장한다.

### 기능 후보
- 특정 압력 투입
- 특정 event trigger
- agent focus follow
- “what if” replay
- intervention comparison

### 이 단계는 매우 나중이다.
현재는 하지 않는다.

---

## 6. 지금 당장 해야 할 일

## 결론
**지금은 텍스트 개선이 아니라 Dot Visual Observer MVP로 넘어간다.**

### 이유
- 텍스트 renderer는 이미 freeze
- observer/candidate pipeline은 작동
- 이제 최종 목표에 가까운 “움직이는 세계 보기”를 작게 검증할 타이밍
- 도트 기반이면 구현 부담이 낮고 현재 snapshot 구조와 잘 맞음

---

## 7. 다음 작업 지시

## Step 1 — Visual Input Schema 확정
### 해야 할 일
Observer snapshot에서 visual에 필요한 최소 필드를 정의한다.

### 최소 필드
- tick
- agents
  - id
  - group_id
  - x / y or layout slot
  - dominant_state
  - fear / shame / hope 등 최소 2~3개 상태
  - salience flag
- groups
  - id
  - dominant_mode
  - tension
- world
  - crowd_mood
  - blame_concentration
  - public_suspicion
  - authority_vigilance
- events
  - active_events
  - event markers
- candidates
  - candidate_id
  - tick_range
  - use_mode
  - strongest_lens

### 산출물
- `docs/visual/VISUAL_OBSERVER_INPUT_SCHEMA.md`

---

## Step 2 — Static Dot Timeline Prototype
### 해야 할 일
처음부터 인터랙티브로 가지 않는다.

먼저 5개 tick snapshot을 정적 dot view로 출력한다.

추천 tick:
- start
- first salience
- middle
- major split / lock
- end

### 산출물
- `docs/visual/static_snapshots/`
- 또는 `visual/dot_observer_static.html`

### 목표
도트로 세계 변화가 직관적으로 보이는지 확인.

---

## Step 3 — Replay MVP
### 해야 할 일
tick 단위로 dot 상태가 바뀌는 replay 구현.

### 기능
- play / pause
- previous / next tick
- timeline slider
- salience marker

### 산출물
- `visual/dot_observer_replay.html`

---

## Step 4 — Detail Panel 연결
### 해야 할 일
선택한 tick의 observer summary를 옆에 표시한다.

### 표시 정보
- world summary
- active events
- top salience
- top candidate
- selected agent summary

### 산출물
- replay demo 갱신
- `docs/visual/VISUAL_OBSERVER_MVP_REVIEW.md`

---

## Step 5 — MVP 판정
### 성공 기준
다음 중 4개 이상 만족하면 Visual Observer MVP 성공.

1. 도트 움직임만 봐도 세계가 변한다는 느낌이 든다
2. salience marker가 실제로 중요한 순간처럼 보인다
3. group split / tension 차이가 시각적으로 보인다
4. 특정 agent를 따라가고 싶어진다
5. text observer panel이 시각 정보를 보완한다
6. story candidate가 visual 위에서 더 쉽게 이해된다

### 실패 기준
다음 중 2개 이상이면 재설계.

1. 도트가 움직여도 의미가 안 느껴진다
2. color/size encoding이 혼란스럽다
3. timeline은 있는데 중요한 순간이 안 보인다
4. text panel을 안 보면 visual만으로 아무것도 모르겠다
5. 구현 부담이 갑자기 커진다

---

## 8. 지금 하지 말아야 할 것

아래는 현재 단계에서 금지한다.

- 3D
- 캐릭터 일러스트
- 애니메이션 연출
- 웹툰/영상 생성
- full game UI
- 플레이어 개입 기능
- 복잡한 React dashboard
- story renderer 재개
- new anchor 대확장
- PyTorch encoder
- Talleyrand scenario

지금은 **도트 기반 세계 관찰 MVP**만 한다.

---

## 9. 텍스트와 비주얼의 역할 정리

### 텍스트의 역할
- observer summary
- candidate packet
- selected story detail
- lens explanation

### 비주얼의 역할
- 세계 흐름을 직관적으로 보여줌
- 시간 변화 / 압력 / 분기 / 집중을 한눈에 보여줌
- 어디를 읽어야 할지 알려줌

### 핵심 원칙
텍스트와 비주얼은 경쟁하지 않는다.

```text
Visual = 세계를 먼저 보게 함
Text = 선택한 순간을 이해하게 함
Story = 선택한 후보를 서사로 읽게 함
```

---

## 10. Claude Code용 작업 순서

### Stage 1
`docs/visual/VISUAL_OBSERVER_INPUT_SCHEMA.md` 작성

### Stage 2
Observer snapshot을 visual-friendly JSON으로 export하는 script 작성

추천:
- `scripts/visual/export_dot_observer_data.py`

### Stage 3
정적 dot snapshot HTML 생성

추천:
- `visual/dot_observer_static.html`

### Stage 4
Replay HTML MVP 생성

추천:
- `visual/dot_observer_replay.html`

### Stage 5
observer text panel 연결

### Stage 6
`docs/visual/VISUAL_OBSERVER_MVP_REVIEW.md` 작성

---

## 11. 다음 분기

### 경우 A — Dot MVP가 잘 작동
- interaction MVP로 이동
- click agent / click event / candidate panel 추가

### 경우 B — Dot MVP가 의미는 있지만 약함
- encoding 조정
- color/size/state mapping 개선
- tick selection 보강

### 경우 C — Dot MVP가 약함
- visual 확장 중단
- text observer / candidate browser 중심으로 회귀
- 비주얼은 chart/graph 수준으로 축소

---

## 12. 최종 한 줄 요약

**WITNESS의 최종 목표는 텍스트 이야기 생성기가 아니라,  
움직이는 세계를 관찰하고 필요하면 그 안의 이야기를 읽을 수 있는 시스템이다.  
텍스트는 그 검증을 위한 중간 레이어였고, 이제는 도트 기반 Visual Observer MVP로 넘어가  
실제로 세계가 움직이는 감각을 눈으로 확인할 단계다.**
