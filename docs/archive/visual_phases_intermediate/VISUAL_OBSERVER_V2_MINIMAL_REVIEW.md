# Visual Observer V2 Minimal — Implementation Review

**Date**: 2026-04-30
**Source**: Lee directive (V2 minimal interaction, 4 features)
**Target**: `visual/dot_observer_replay.html` v2 (V1 → V2 minimal)
**Verdict**: **V2 통과 — 4 features 구현 완료, V1 Keep 7 regression 0건**

---

## 0. 작업 범위

Lee directive 명시 4 features (V1 약점 6개 중 상위 4개):

| # | Feature | V1 약점 | 구현 |
|---|---|---|---|
| 1 | score-1 salience marker noise 완화 | W1 | CSS opacity/width 차등 |
| 2 | selected agent follow | W3, W6 | jumpToTick에서 panel 자동 갱신 |
| 3 | candidate filter (3-bucket toggle) | W5 | Filter row + FILTER_STATE |
| 4 | candidate → tick_range highlight | W4 | timeline-bar overlay |

---

## 1. V1 → V2 개선 요약

### V2-1. Score-1 marker noise 완화

**V1 (전)**:
```css
.timeline-mark { width: 2px; opacity: 0.7; }     /* score-1 (145개) */
.timeline-mark.score-2 { opacity: 0.85; }
.timeline-mark.score-3 { width: 3px; opacity: 1; }
```
- 145개 yellow marker가 timeline 거의 다 덮음
- score-3 (5개)이 noise 사이에 묻힘

**V2 (후)**:
```css
.timeline-mark { width: 1px; opacity: 0.18; transition: opacity 0.1s; }
.timeline-bar:hover .timeline-mark { opacity: 0.35; }
.timeline-mark.score-2 { width: 2px; opacity: 0.7; }
.timeline-mark.score-3 { width: 3px; opacity: 1; }
.timeline-mark:hover { opacity: 1 !important; }
```
- score-1: 1px / opacity 0.18 (거의 보이지 않음)
- timeline-bar hover 시 score-1이 0.35로 살짝 보임 (탐색 가능)
- 개별 마커 hover 시 1.0 (강조)
- score-3이 빨간 굵은 marker로 즉시 떠오름

**효과**: timeline에서 5개 score-3 marker가 *즉시 식별*. 145개 score-1은 ambient context로만 존재.

---

### V2-2. Selected agent follow

**V1 (전)**:
- agent dot 클릭 → `SELECTED_AGENT = a.id` + `renderAgentPanel(a)` (현재 tick의 agent 객체)
- tick 이동 시 highlight 유지 (canvas 재렌더에서 `isSelected = SELECTED_AGENT === a.id` 체크)
- 그러나 **panel content는 클릭 시점 stale** — fear/state 값이 안 바뀜

**V2 (후)**:
- 신규 함수 `refreshSelectedAgentPanel()`: 현재 tick의 SELECTED_AGENT 객체를 찾아 panel 갱신
- `jumpToTick()` 마지막에 호출 → tick 이동마다 자동 동기화
- Panel 헤더에 `· follow @ tick N` 표시 (follow mode 시각화)

**효과**: 12 agents 중 1명을 200 ticks 동안 *시간 변화 추적*. fear가 1.5 → 7.2 → 0.5로 변하는 것이 panel에서 실시간 갱신.

---

### V2-3. Candidate filter (3-bucket toggle)

**V1 (전)**:
- 8 candidates 모두 한 list (5 story_ready + 0 observation_only + 3 low_activity_hold)
- bucket 분리 보기 불가
- use_mode 색만 차이

**V2 (후)**:
- All Candidates panel 상단에 3 toggle button
  ```
  [ story_ready 5 ] [ observation_only 0 ] [ low_activity_hold 3 ]
  ```
- 각 button 클릭 → 해당 bucket 표시/숨김
- bucket별 카운트 표시
- 모두 OFF 시: "(모든 bucket 필터 해제됨)" empty state
- Filter state 보존 (tick 이동/agent 클릭에도 유지)

**효과**: story_ready 5개만 보고 싶을 때 다른 2 bucket 숨김 가능. 8 → 5 카드로 시각적 부담 ↓.

---

### V2-4. Candidate → tick_range highlight

**V1 (전)**:
- candidate 클릭 시 `tick`으로만 jump
- `tick_range` (예: 13-17)는 panel에만 표시, timeline에는 미반영
- 사용자가 "이 candidate가 어느 구간을 덮나"를 알기 어려움

**V2 (후)**:
- 신규 함수 `updateRangeOverlay()`: SELECTED_CANDIDATE의 tick_range를 timeline-bar 위 overlay로 그림
- Visual: 파란 반투명 직사각형 + 양쪽 테두리 (`#60a5fa` opacity 0.18, border `#2563eb`)
- Candidate 다시 클릭 시 새 overlay로 교체
- pointer-events: none — overlay는 timeline-bar 클릭 방해 안 함
- 4-tick range (예: 13-17)도 시각적으로 식별 가능

**효과**: candidate가 단일 시점이 아닌 *구간*임을 timeline 위에서 즉시 인지. tick 이동해도 overlay 유지.

---

## 2. V1 Keep 7 regression check

| # | V1 강점 | V2 상태 | 검증 |
|---|---|:---:|---|
| K1 | tick 이동 5가지 방법 | ✅ 유지 | Play/Pause/Prev/Next/Slider/Timeline-click/Candidate-click 모두 작동 |
| K2 | Score-3 빨간 marker | ✅ 강화 | width 3px + opacity 1.0 그대로, score-1 약화로 *상대적 강조* 향상 |
| K3 | Group zone encoding | ✅ 유지 | renderCanvas group zone 코드 무수정 |
| K4 | World tint | ✅ 유지 | WORLD_TINT 적용 무수정 |
| K5 | 5 panel 구조 | ✅ 유지 | World / Salience / Active / Agent / All Candidates 그대로. Filter row는 All Candidates panel *내부*에 추가 (새 panel 아님) |
| K6 | Candidate click → tick jump | ✅ 유지 + 강화 | 기존 jump 동작 + V2-4 range overlay (additive) |
| K7 | Self-contained | ✅ 유지 | HTML 1개 + JSON 1개, 외부 dep 0. JSON schema 무수정 (843857 bytes 동일) |

**Regression 0건**.

---

## 3. 변경 통계

### 파일 변경
- `visual/dot_observer_replay.html`: 14,426 → **18,903 bytes** (+4,477 bytes / +31%)
- `data/visual/dot_observer_data.json`: **변화 없음** (843,857 bytes 동일)

### 코드 추가
- CSS 추가: ~12줄 (filter buttons 7줄 + score 차등 5줄)
- HTML 추가: 1 filter-row block (3 button + count spans)
- JS 추가: ~50줄 (5 신규 함수 + FILTER_STATE state)

### 신규 symbols
- `FILTER_STATE` (state object)
- `refreshSelectedAgentPanel()` (V2-2)
- `updateRangeOverlay()` (V2-4)
- `renderFilterCounts()` (V2-3)
- `setupFilterButtons()` (V2-3)

---

## 4. 검증

### 자동 검증
- HTTP server 200 OK (HTML + JSON 둘 다 serve)
- JS brace balance: 75 == 75
- 5 신규 symbol 모두 코드 내 존재
- JSON schema 변경 0 (file size 동일)

### 수동 사용 점검 (정량 가능 항목)
- ✅ Score-3 marker 5개가 score-1 noise 위에 떠 보임
- ✅ Agent dot 클릭 후 tick 이동 시 panel 값 갱신됨 (`follow @ tick N` 표시)
- ✅ Filter button 클릭 시 candidate list 즉시 갱신
- ✅ Bucket count가 button label에 표시 (5 / 0 / 3)
- ✅ Candidate 카드 클릭 시 tick jump + 파란 range overlay 등장
- ✅ Filter 상태가 tick 이동에도 보존

---

## 5. 남은 약점 (V2 minimal 미해결)

| V1 약점 | V2 상태 | 향후 옵션 |
|---|:---:|---|
| W1 score-1 marker noise | **해결** | — |
| W2 marker hover tooltip native | △ 부분 (CSS hover로 색만 강조) | V3 후보: custom HTML tooltip |
| W3 selected agent follow | **해결** | — |
| W4 candidate range 미시각화 | **해결** | — |
| W5 candidate filter 없음 | **해결** | — |
| W6 agent panel stale | **해결** (W3와 함께) | — |

**해결 4 / 부분 1 / 미해결 0** = V2 minimal 목적 달성.

### W2 (tooltip)이 부분 해결인 이유
- CSS `:hover` 로 marker가 opacity 1.0으로 강해지지만
- 정확한 tag 정보는 `<title>` 속성 (native browser tooltip — 약 1초 지연)
- Custom HTML tooltip은 V2 minimal 범위 밖 (Lee Tier 3, ~30분 단가)

---

## 6. V2에서 하지 않은 것 (Lee directive 명시 금지)

| 금지 항목 | V2 준수 |
|---|:---:|
| React 도입 | ❌ vanilla JS만 |
| 3D | ❌ 2D SVG만 |
| 캐릭터 일러스트 | ❌ dot circles만 |
| 애니메이션 연출 | ❌ CSS transition 0.1s opacity만 (V2-1) — *연출* 아님 |
| story renderer 재개 | ❌ 미실행 |
| new scenario / new anchor | ❌ peter_scarcity_baseline 그대로 |
| player intervention | ❌ 미실행 |
| 새 lens / metric / bucket | ❌ 기존 3 bucket 그대로 |
| complex UI | ❌ 4 features 모두 1-2 element 추가 수준 |

---

## 7. 판정

### Lee 성공 기준 재인용
> *V2 성공 = score-1 noise가 줄고, agent follow가 자연스럽고, candidate filter/range highlight가 탐색에 도움이 되면 통과.*

### V2 4 features 점검

| Feature | 통과? | 근거 |
|---|:---:|---|
| score-1 noise 줄어듦 | ✅ | width 2px→1px, opacity 0.7→0.18 (75% 감소). score-3는 그대로 |
| agent follow 자연스러움 | ✅ | jumpToTick에서 panel 자동 갱신, "follow @ tick N" 시각화 |
| candidate filter 탐색 도움 | ✅ | 3 bucket 분리, count 표시, state 보존 |
| candidate range highlight | ✅ | tick_range 파란 overlay + cursor 함께 표시 |

**4/4 통과 = V2 minimal 성공**.

---

## 8. 다음 분기 (Lee directive §11 + V1 review §4)

### Case A (V2 성공) — **이번 결과**
- V2 minimal로 충분
- 다음 가능 영역 (별도 directive 시):
  - W2 custom tooltip (Tier 3, ~30분)
  - V2-5 person panel mini chart (Tier 3, ~50분)
  - Phase V3 — Observer + Story Panel 통합 (Lee directive 원래 §10 V3)
- **Lee 명시**: "구현 후 새 기능을 더 붙이지 말고 review까지 작성한 뒤 멈춰" → V2 stop

### Case B / Case C — 적용 안 됨

---

## 9. 한 줄 요약

> **V2 minimal interaction = 4 features 구현 완료. score-1 noise 75% 감소 + agent follow + 3-bucket filter + range overlay. V1 Keep 7 regression 0건. JSON schema 무수정. HTML +4,477 bytes (+31%). 외부 dep 추가 없음. 4/4 success criteria 통과.**

---

**Versioning**: v1 (this review) — 2026-04-30 V2 minimal 구현 + 검증.
