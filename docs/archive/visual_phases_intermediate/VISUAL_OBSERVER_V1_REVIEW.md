# Visual Observer V1 Review — 사용성 점검

**Date**: 2026-04-30
**Source**: Lee directive (V1 Review + V2 plan), 구현보다 review/plan 중심
**Target**: `visual/dot_observer_replay.html` (V1 MVP — Phase V0-V1 산출물)
**Verdict**: **Case A 후보** — V1 충분, V2 minimal interaction으로 진행 권고

---

## 0. Review 방식

이 문서는 **실제 사용 관점 점검**이다. 코드 정합성 검증이 아니라 *사람이 이 화면 앞에 앉아서 잘 쓸 수 있는가*에 초점.

분석 자료:
- `data/visual/dot_observer_data.json` 824 KB (200 ticks, 12 agents, 3 groups)
- `visual/dot_observer_replay.html` (~310줄, 외부 dependency 0)
- 197 salience marks + 8 curated candidates

---

## 1. 5개 사용 관점 질문 점검 (Lee §1)

### Q1. tick 이동이 직관적인가
**△ 부분 YES**.

**5가지 이동 방법 제공**:
- ▶ Play / Pause (100ms 간격, 10 ticks/sec)
- ◀ / ▶ 단일 tick
- Slider drag (0-199)
- Timeline-bar click (positional)
- Candidate card click (jump to candidate.tick)

**강점**:
- Slider가 200 ticks 범위에서 충분히 정밀 (200 px 가까이)
- Timeline-bar click이 marker와 함께 "중요한 곳에 닿기"가 자연스러움

**약점**:
- Play 속도 100ms 고정 — 200 ticks = 20초. 더 느리게/빠르게 옵션 없음
- 키보드 단축키 없음 (←/→ 화살표로 prev/next 미지원)
- "특정 tick으로 직접 입력" 입력란 없음 (slider만)

---

### Q2. salience marker를 보고 중요한 순간을 찾을 수 있는가
**△ 부분 YES — score-3은 보이지만 score-1 noise가 강함**.

**데이터 현실**:
- 197 / 200 ticks (98.5%)에 salience mark 존재
- Score 분포: **1점 145개 (74%) / 2점 47개 (24%) / 3점 5개 (2.5%)**
- Score-3 ticks: **15, 25, 142, 146, 147** (curated story_ready와 정확히 매칭)

**강점**:
- Score-3 (빨간 굵은 marker)는 5개 → 즉시 시각적 식별 가능
- Score 색 분리 (yellow/orange/red) 의도 명확

**약점 (큰 것)**:
- 145개 yellow marker가 거의 전 timeline을 덮음 → **timeline이 yellow 띠처럼 보임**
- "중요한 순간"을 찾기 위해 강조해야 할 score-3가 yellow noise 사이에 묻힘
- score-1이 너무 흔해서 "salience"라는 단어 자체의 의미가 희석됨

**근본 원인**:
- `detect_salience_tags`가 너무 관대 — agent_state_shift가 거의 매 tick 1개씩 발생
- 임계값 조정이 데이터 layer 작업 (visual layer 책임 아님)

**시각적 mitigation 가능 (V2 영역)**:
- score-1 marker를 더 흐리게 (opacity 0.3~)
- score-1 marker를 hover 시에만 표시
- 또는 timeline-bar에 score>=2만 표시 (cleaner)

---

### Q3. group split/tension이 눈에 들어오는가
**△ 부분 YES — L1 위주로 변화, L2/L3 정적**.

**데이터 현실**:
- 200 ticks 동안 group dominant_mode 변화 = **12회**
- L1만 활발히 변화: low_activity → partial → saturation → partial → recovery → partial → ...
- L2, L3는 거의 항상 `low_activity` (peter_scarcity_baseline anchor 특성)
- Tension range: 0.00 ~ 1.00 (full range 사용 — 좋음)

**강점**:
- Zone radius 변화 (80~110) + color 변화가 L1에서 명확히 보임
- Mode 변화 12회 = 200 ticks에서 적당한 빈도 (지루하지 않고 과하지 않음)

**약점**:
- "split" 느낌이 약함 — 한 group만 움직이고 둘은 정지 → 분할 아닌 *국지적 활성*
- L1 zone 위에 attention 집중되어 L2/L3는 시각적 dead space
- 다른 anchor (예: peter_scarcity_triple)에서는 다를 가능성 있음 — 검증 미실행

---

### Q4. text panel이 너무 길거나 짧지 않은가
**✅ 적절**.

**현재 5개 panel**:

| Panel | 내용 | 크기 |
|---|---|---|
| World @ tick | mood + 3 metrics + active_events | 4-6줄 |
| Salience tags | 0~3 tags | 0-2줄 |
| Active candidates | 0~2 카드 | 가변 |
| Selected agent | dot 클릭 시 | 3줄 |
| All curated candidates | 8 카드 | 8 카드 (스크롤 없이 가능) |

**강점**:
- World panel = 한눈에 4 metric + events
- Active candidates (현재 tick range에 active)가 *맥락*을 줌
- All candidates 8개 = 스크롤 없이 표시 (3-bucket 색 코딩)

**약점 (작은 것)**:
- Salience tags panel은 World panel과 합칠 수 있음 (둘 다 tick 정보)
- Selected agent panel이 hidden→visible 전환 시 layout shift 발생 가능

---

### Q5. candidate panel이 실제로 탐색에 도움이 되는가
**✅ YES — candidate 카드 클릭 → tick jump이 핵심 가치**.

**강점 (큰 것)**:
- 8 candidates 클릭하면 즉시 해당 tick으로 이동 → *순회 탐색* 가능
- use_mode 색 코딩 (story_ready 녹색 / observation_only 노랑 / low_activity_hold 회색)
- related_candidate_ids 표시 (`+2 related`) — Q1-Q4 near-dup 정보 활용
- Tick distribution: 15, 20, 25, 66, 102, 112, 142, 147 — *시간적으로 분산* (다양성 ✅)

**약점**:
- **Filter 없음**: story_ready만 보고 싶을 때 분리 불가
- **정렬 옵션 없음**: 항상 입력 순서 (tick 순서 아님)
- 클릭하면 tick으로 jump하지만 *tick range 강조*는 안 됨 → tick_range가 candidate의 의미인데 시각화 부재

---

## 2. V1 분류 — Keep / Weak / Remove

### Keep (강점, 유지)

#### K1. Tick 이동 5가지 방법
- Play/Pause/단일/Slider/Timeline-bar/Candidate-click 모두 자연스러움
- 사용자 의도에 따라 적절한 도구 선택 가능

#### K2. Score-3 빨간 marker
- 5 ticks (15, 25, 142, 146, 147)이 즉시 식별
- curated story_ready 후보와 1:1 매칭 (의도된 설계)

#### K3. Group zone radius/color encoding
- L1의 saturation/partial/recovery 전환이 시각적으로 보임
- Tension full range (0~1) 활용

#### K4. World tint
- crowd_mood 변화가 배경색으로 미세하게 들어옴 → ambient 정보

#### K5. 5 panel 구조
- 명확한 separation: World / Salience / Active candidate / Agent / All candidate
- 용도가 겹치지 않음

#### K6. Candidate card click → tick jump
- 8개 candidate를 빠르게 순회 → 핵심 탐색 가치

#### K7. Self-contained
- HTML 1개 + JSON 1개 = 4파일 시스템
- 외부 dependency 0 (vanilla JS + SVG)
- HTTP server만 있으면 작동

---

### Weak (약점, V2에서 보강 후보)

#### W1. Score-1 marker noise (가장 큰 약점)
- 145개 yellow marker가 timeline을 덮음
- "중요한 순간"이 묻힘
- **V2 후보**: score-1을 흐리게 / hide / opacity 0.3

#### W2. Timeline marker tooltip이 native title
- Hover 시 ~1초 지연 + 디자인 안 됨
- **V2 후보**: custom hover tooltip (Lee §3 후보 4)

#### W3. Selected agent follow 없음
- Agent 클릭 후 tick 이동하면 동일 agent_id로 highlight 유지되지만 panel 내용은 stale
- **V2 후보**: selected agent follow (Lee §3 후보 1)

#### W4. Click candidate → tick range highlight 없음
- candidate.tick으로 jump만 됨, tick_range는 미시각화
- **V2 후보**: timeline-bar에 candidate range overlay (Lee §3 후보 3)

#### W5. Candidate filter/sort 없음
- 8개 모두 한 list — bucket 별 분리 보기 불가
- **V2 후보**: bucket toggle filter (Lee §3 후보 5)

#### W6. Selected agent panel content가 stale
- Click 시 정보, tick 변화 시 갱신 안 됨
- **V2 후보**: agent follow 시 자동 갱신 (W3와 함께)

---

### Remove (제거 후보)

**없음.** 모든 panel/encoding이 의미 있게 사용됨.

검토했지만 제거하지 않음:
- Salience tags panel: World panel과 합칠 수 있지만 *시각적 분리*가 정보 구조에 도움
- All candidates panel: 적당한 크기, 제거하면 탐색 불가
- World tint: 미세하지만 ambient 가치

**가능한 합치기 (V2에서 검토 가능)**:
- Salience + World → "Tick state" 단일 panel (안 합쳐도 무방)

---

## 3. 종합 평가

### V1 충분/약함/실패 판정

| 기준 | 결과 |
|---|---|
| 도트 움직임만 봐도 세계 변화 보임 | ✅ |
| Salience marker가 중요한 순간처럼 보임 | △ (score-3 OK, score-1 noise) |
| Group split/tension 차이 visible | △ (L1 위주, L2/L3 정적) |
| Agent follow 욕구 | △ (V2 영역) |
| Text panel이 visual 보완 | ✅ |
| Candidate가 visual 위에서 더 이해됨 | ✅ |

**결과**: 명확 충족 3 / 부분 충족 3 / 실패 0 → **Case A (V1 충분)**

### V1 핵심 가치 (한 줄)
> *200 ticks 데이터를 5가지 방법으로 순회 가능하고, 8 curated candidates 클릭으로 중요 tick 즉시 jump, 5 panel이 visual 보완.*

### V1의 결정적 약점 (한 줄)
> *score-1 marker 145개가 yellow noise처럼 timeline을 덮어 score-3이 살짝 묻힘.*

---

## 4. 다음 분기 (Lee §11 + 본 review 결론)

### Case A (V1 충분) — **이번 결과**
- **권고**: V2 minimal interaction 진행
- 후속 plan: `docs/visual/VISUAL_OBSERVER_V2_MINIMAL_PLAN.md`
- 우선순위: W1 (score-1 noise) > W3 (agent follow) > W5 (candidate filter) > W4 (range highlight) > W2 (tooltip)

### Case B (V1 약함) — 적용 안 됨
- 만약 발생 시: encoding 조정 (score 임계값 / color mapping / dot size 공식)

### Case C (V1 실패) — 적용 안 됨
- 만약 발생 시: visual 확장 중단 + text observer 회귀

---

## 5. 한 줄 요약

> **V1 = Case A 후보 (5+/6 success). 강점 7 + 약점 6 + 제거 0. score-1 marker noise가 가장 큰 약점이지만 score-3은 살아있음. V2 minimal interaction 진행 권고.**

---

**Versioning**: v1 — 2026-04-30 V1 사용성 review.
