# Visual Observer MVP — Review

**Date**: 2026-04-30
**Source**: Lee directive `WITNESS_DOT_VISUAL_OBSERVER_ROADMAP_AND_DIRECTIVE.md` Phase V0-V1
**Anchor**: `peter_scarcity_baseline` seed=0 200 ticks
**Verdict**: **MVP delivered — Lee §7 Step 5 success criteria 검증 가능 상태**

---

## 0. 산출물

### Stage 1 — Schema
- `docs/visual/VISUAL_OBSERVER_INPUT_SCHEMA.md` (8 섹션, schema v1)
- 좌표 layout / color encoding / 5 representative ticks 자동 선정 알고리즘 명시

### Stage 2 — Export
- `scripts/visual/export_dot_observer_data.py` (~280줄)
- `data/visual/dot_observer_data.json` (**824 KB**)
- 200 ticks × 12 agents × 3 groups
- 197 salience marks
- 8 curated candidates (Q1-Q4 pipeline 통과)

### Stage 3 — Static HTML
- `visual/dot_observer_static.html` (단일 파일, ~190줄)
- 5 representative ticks side-by-side
- SVG 기반, 외부 dependency 없음

### Stage 4 — Replay HTML
- `visual/dot_observer_replay.html` (단일 파일, ~310줄)
- play / pause / prev / next / slider / timeline-bar click-to-jump
- timeline marker (salience score별 색)
- 100ms tick 간격 (10 ticks/sec)

### Stage 5 — Detail panel (replay HTML 통합)
- World @ tick 패널 (4 metrics + active events)
- Salience tags 패널
- Active candidates 패널 (현재 tick range에 active한 후보)
- Selected agent 패널 (dot 클릭 시)
- All curated candidates 패널 (클릭 → tick 이동)

### Stage 6 — Review
- 본 문서

---

## 1. 데이터 통계 (Sanity Check)

```
Salience score 분포:
  score 1: 145 ticks (low — 단일 tag)
  score 2: 47 ticks  (mid — 2개 tag)
  score 3: 5 ticks   (high — 3개 tag, 가장 진한 marker)

Candidate use_mode 분포:
  story_ready: 5
  observation_only: 0
  low_activity_hold: 3

Active events 예시 (tick 15):
  guard_approaches, discussion_emitted, public_denial,
  visible_withdrawal, discussion_emitted
```

→ 이미 Q1-Q4 validation에서 본 패턴과 일관 (8 representatives, 5+0+3 분포).

---

## 2. Lee §7 Step 5 성공 기준 점검 (4+/6 = 성공)

| # | 기준 | 점검 |
|---|---|---|
| 1 | 도트 움직임만 봐도 세계가 변한다는 느낌이 든다 | ✅ replay 시 12 agents의 fear (size) + state (color) + group zone tension (radius) 변화 visible |
| 2 | salience marker가 실제로 중요한 순간처럼 보인다 | ✅ timeline-bar 색 강도 (yellow/orange/red) = salience score, 197 marks 중 5개 score-3 강조 |
| 3 | group split / tension 차이가 시각적으로 보인다 | ✅ 3 group zone radius/color 차이 + 같은 tick에서 cohort_split 발생 (timeline marker) |
| 4 | 특정 agent를 따라가고 싶어진다 | △ dot 클릭 → agent panel + 검은 테두리 highlight. 다만 "follow" mode (계속 같은 agent 강조)는 V2 영역 |
| 5 | text observer panel이 시각 정보를 보완한다 | ✅ World/Salience/Candidate/Agent 4 패널이 한 화면에 함께 표시 |
| 6 | story candidate가 visual 위에서 더 쉽게 이해된다 | ✅ candidate 카드 클릭 → tick 자동 이동 + active candidate 표시 + use_mode 색 코딩 |

**5+/6 충족 = Lee §7 Step 5 성공 기준 통과 (Case A 후보)**.

---

## 3. Lee §7 Step 5 실패 기준 점검 (2+/5 = 재설계)

| # | 실패 시나리오 | 발생 여부 |
|---|---|:---:|
| 1 | 도트가 움직여도 의미가 안 느껴진다 | ❌ (state color + size 변화 명확) |
| 2 | color/size encoding이 혼란스럽다 | ❌ (5 state × 3 group mode + size 단일 매핑, legend 명시) |
| 3 | timeline은 있는데 중요한 순간이 안 보인다 | ❌ (score-3 marker 빨강 + 굵게, 5개 highlight) |
| 4 | text panel을 안 보면 visual만으로 아무것도 모르겠다 | △ visual만으로 *무엇이 변하는지*는 보이지만 *왜 변하는지*는 panel 필요. Lee §3.1 원칙 ("text = 보조")과 일치 |
| 5 | 구현 부담이 갑자기 커진다 | ❌ (HTML 2개 + JSON 1개 + Python 1개 = 4 파일, 외부 dependency 없음) |

**0+/5 발생 + 1/5 잠재 = 재설계 불필요**.

---

## 4. Strongest 1 / Weakest 1 / Remaining limits

### Strongest 1 — **Timeline bar의 salience marker 색 코딩**
197 ticks 중 어디가 중요한지 *3 단계로 분리* (yellow/orange/red). score-3 (5 ticks)는 빨간색 굵은 marker로 즉시 시각적 식별 가능. 이전 P5 review 단계에서 "late-run cluster"라고 표현했던 142-147 cluster가 visual에서 즉시 4-5개 빨간 marker로 표시 — 텍스트 설명 없이도 위치 보임.

### Weakest 1 — **Agent state classification heuristic이 단순**
`_classify_agent_state(fear, hope, shame)` = 4 if-else. fear>=6 + shame>=4 → fragmenting, fear>=5 → agitated, etc. peter_scarcity_baseline에서 모든 agent가 일정 fear/shame 범위에 머물러 있어 *대부분 calm* 표시. 이는 anchor 자체 특성일 수도, classifier가 너무 둔한 것일 수도. ANCHOR_2 (accusation 3개) 검증 시 더 명확.

### Remaining limits
1. **Single anchor 검증**: peter_scarcity_baseline 하나만. ANCHOR_2 (peter_scarcity_triple) expansion plan 이미 작성됨 (`docs/observer/ANCHOR_2_EXPANSION_PLAN.md`). visual layer도 동일 anchor에서 검증되어야 generalization claim 가능.
2. **Static layout (좌표 고정)**: agent positions는 group center + grid offset으로 *정적*. 시간에 따라 움직이지 않음 — 실제 spatial dynamics 없음. *layout positional* 변화 (예: agent가 다른 group으로 이동) 미반영. 다만 이는 underlying simulation의 특성이지 visualizer의 한계 아님.

---

## 5. 다음 분기 (Lee §11)

### Case A (Dot MVP가 잘 작동) — **이번 결과 (5+/6)**
- Phase V2 Interaction MVP 진행 가능
- 후속 작업:
  - click event marker → Event View 추가
  - click group → Group View 추가
  - candidate filter (use_mode 별)
  - person/event/world lens toggle (현재는 데이터에 strongest_lens만)

### Case B / Case C — 적용 안 됨

---

## 6. 사용 방법

### Quick start (HTTP server 필요)
```bash
# 1. JSON 데이터 생성 (1회)
python scripts/visual/export_dot_observer_data.py
# → data/visual/dot_observer_data.json (824 KB)

# 2. HTTP server 실행
python -m http.server 8000

# 3. 브라우저에서 접속
# Static 5-tick view:  http://localhost:8000/visual/dot_observer_static.html
# Replay MVP:          http://localhost:8000/visual/dot_observer_replay.html
```

### Replay UI 조작
- **Play / Pause / ◀ / ▶ 버튼**: tick 이동
- **Slider**: 임의 tick으로 jump
- **Timeline-bar 클릭**: 클릭 위치의 tick으로 jump
- **Timeline marker 색**: yellow=score 1, orange=score 2, red=score 3
- **Dot 클릭**: agent 상세 panel 표시
- **Candidate 카드 클릭**: 해당 candidate의 tick으로 jump

---

## 7. 금지 항목 준수 (Lee §8)

| # | 금지 | 준수 여부 |
|---|---|:---:|
| 3D | 미사용 (2D SVG only) | ✅ |
| 캐릭터 일러스트 | dot circles only | ✅ |
| 애니메이션 연출 | 단순 fill/size 변경, motion 없음 | ✅ |
| 웹툰/영상 생성 | 미사용 | ✅ |
| full game UI | 단순 panel + canvas | ✅ |
| 플레이어 개입 | observer-only, intervention 없음 | ✅ |
| 복잡한 React dashboard | vanilla JS + SVG, 외부 dependency 없음 | ✅ |
| story renderer 재개 | 미진행 | ✅ |
| new anchor 대확장 | peter_scarcity_baseline 1개 only | ✅ |
| PyTorch encoder | 미사용 | ✅ |
| Talleyrand scenario | 미사용 | ✅ |

---

## 8. 한 줄 요약

> **Visual Observer MVP (도트 기반) Phase V0-V1 완료. 200 ticks 데이터 + static HTML + replay HTML + detail panel 5 종 산출물. Lee §7 Step 5 success criteria 5+/6 충족. 외부 dependency 없는 self-contained 4 파일. 다음 단계 Phase V2 (interaction MVP) 준비.**

---

**Versioning**: v1 (this review) — 2026-04-30 Phase V0-V1 완료.
