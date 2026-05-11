# Visual Observer V2 — Minimal Improvement Plan

**Date**: 2026-04-30
**Source**: Lee directive (V1 Review + V2 plan, "구현보다 review/plan 중심")
**Prerequisite**: `docs/visual/VISUAL_OBSERVER_V1_REVIEW.md` (Case A 판정)
**Status**: Plan only — 별도 directive 없을 시 *대기*. 새 코드 작성 안 함.

---

## 0. 핵심 원칙

> **새 기능 대확장 금지. V1의 6개 약점 (W1-W6) 중 minimal subset만 보강.**

V2 = polish, not expansion.
- ❌ 새 lens 추가
- ❌ 새 panel 추가
- ❌ 새 visualization metaphor
- ✅ 기존 element의 *사용성 향상*

---

## 1. V1 약점 → V2 후보 매핑

V1 review §2의 6개 약점 (W1-W6) → Lee §3 5개 후보로 매핑:

| V1 약점 | V2 후보 | Lee §3 매핑 |
|---|---|---|
| W1: score-1 marker noise | (없음 — 별도 추가 후보로 검토) | (Lee §3 외) |
| W2: marker tooltip native | salience marker hover tooltip | Lee §3 후보 4 |
| W3: agent follow 없음 | selected agent follow | Lee §3 후보 1 |
| W4: candidate range 미시각화 | click candidate → tick range highlight | Lee §3 후보 3 |
| W5: candidate filter 없음 | candidate filter (3-bucket) | Lee §3 후보 5 |
| W6: agent panel stale | (W3와 함께 처리) | (Lee §3 후보 1 부속) |
| (Lee §3 후보 2) | click agent → person panel 강화 | Lee §3 후보 2 (W6 확장) |

→ Lee §3 5개 후보 + W1 1개 = **총 6 candidate features**.

---

## 2. 우선순위 (V1 Review §3 권고 기준)

### Tier 1 — 가장 효과적 (구현 우선)
1. **score-1 marker noise 완화** (W1 → 가장 큰 약점)
2. **selected agent follow** (W3+W6 → V1의 단절감 해소)

### Tier 2 — 탐색 효율 향상
3. **candidate filter** (W5 → 8개 list 필터링)
4. **click candidate → tick range highlight** (W4 → tick_range 시각화)

### Tier 3 — Polish
5. **click agent → person panel 강화** (W6 → 시간 변화 mini chart)
6. **salience marker hover tooltip** (W2 → native → custom)

**Tier 1만 구현해도 V2 minimal로 충분**. Tier 2/3은 단가 작은 추가 작업.

---

## 3. 후보별 상세

### V2-1. Score-1 marker noise 완화 (W1)
**문제**: 145개 yellow marker가 timeline을 덮어 score-3 (5개)이 묻힘.

**옵션 A — opacity 차등** (권장, 단가 5분):
```css
.timeline-mark        { opacity: 0.25; }  /* score-1 */
.timeline-mark.score-2 { opacity: 0.7; }
.timeline-mark.score-3 { opacity: 1.0; }
```

**옵션 B — score-1 hide on default + toggle**:
- "show low salience" 체크박스 추가
- 기본 = score>=2만 표시

**옵션 C — width 차등 (이미 부분 적용됨)**:
- 현재 score-3만 `width: 3px`, 나머지 `2px`
- 1px / 2px / 4px로 더 강한 대비

**권장**: 옵션 A + 옵션 C 조합 (CSS만 수정, JS 로직 변화 없음).

---

### V2-2. Selected agent follow (W3 + W6)
**문제**: agent dot 클릭 후 tick 이동하면 highlight는 유지되지만 panel content는 stale.

**구현 방향**:
- 현재 `SELECTED_AGENT` 변수가 `agent_id`로 유지됨 (재렌더 시 강조)
- `renderAgentPanel(agent)`을 `jumpToTick`에서도 호출 → 매 tick 자동 갱신
- 변경 범위: `jumpToTick` 함수 마지막에 `if (SELECTED_AGENT) refreshAgentPanel()` 추가

**예상 효과**:
- 1 agent 따라가기 가능 → 12-agent 중 *focal agent* 선택 후 200 ticks를 그 시점에서 봄
- "특정 agent를 따라가고 싶어진다" (Lee §7 Step 5 기준 4번) 충족

**단가**: ~10줄 JS 변경.

---

### V2-3. Click candidate → tick range highlight (W4)
**문제**: candidate 클릭 시 `tick`으로만 jump, `tick_range`는 timeline에 표시 안 됨.

**구현 방향**:
- Timeline-bar에 candidate.tick_range를 *반투명 overlay*로 표시
- candidate 선택 해제 시 overlay 제거
- 여러 candidate 동시 선택은 V2 범위 외 — 한 번에 1개만

**Visual**:
```
[==============================]  <- timeline 200 ticks
       ▒▒▒▒▒                      <- selected candidate.tick_range overlay
        ▼                          <- selected candidate.tick cursor
```

**단가**: ~15줄 JS + ~5줄 CSS.

---

### V2-4. Candidate filter (W5)
**문제**: 8 candidates list에 use_mode 색만 있음, 분리 보기 불가.

**구현 방향**:
- Candidate panel 상단에 3 toggle button:
  - `[story_ready] [observation_only] [low_activity_hold]`
- 모두 ON = 현재 동작 (8개 표시)
- 일부 OFF = 해당 bucket 숨김
- toggle 상태는 client-side state (no localStorage)

**단가**: ~25줄 JS + ~10줄 CSS.

---

### V2-5. Click agent → person panel 강화 (Lee §3 후보 2)
**문제**: 현재 agent panel = fear/hope/shame 단일 tick 값만.

**구현 방향**:
- Mini timeline chart: 200 ticks의 fear/hope/shame 라인 (32px 높이 SVG)
- Hover하면 해당 tick 값 표시
- Selected agent의 *시간 변화*를 한눈에

**Visual**:
```
[Selected agent: agent_01 (group L2)]
state = agitated · salient
fear ━━━━━━━━━━━━━━━━━━━━━━━ (line chart 0~10)
hope ━━━━━━━━━━━━━━━━━━━━━━━
shame_self ━━━━━━━━━━━━━━━━━
```

**주의**: 200 tick 라인은 좁음 → SVG path로 single line 시각화 (컬러 매핑 안 함, 단순 monotone).

**단가**: ~40줄 JS + ~15줄 CSS. Tier 2 후보 — V2 minimal에서 *선택적*.

---

### V2-6. Salience marker hover tooltip (W2)
**문제**: 현재 `<title>` 속성으로 native browser tooltip → 디자인 안 됨, 지연 있음.

**구현 방향**:
- Custom HTML tooltip (position: absolute)
- 마커 hover 시 `tick: 15 / tags: [authority_vigilance_spike, cohort_split, agent_state_shift] / score: 3`
- mouseleave 시 hide

**단가**: ~30줄 JS + ~15줄 CSS. Tier 3 후보 — V2 polish 후반.

---

## 4. V2에서 하지 말아야 할 것 (Lee §4 verbatim)

| 금지 항목 | V2 영향 |
|---|---|
| 3D | 모든 visualization은 2D SVG 유지 |
| React 대시보드 | Vanilla JS만, 외부 framework 미사용 |
| 캐릭터 일러스트 | dot circles만 |
| story renderer 재개 | 텍스트 출력 freeze 유지 |
| new scenario | peter_scarcity_baseline 1개 only (V4 영역) |
| player intervention | 관찰자 모드만, 개입 기능 0 (V6 영역) |
| complex UI | 단순 panel + click + toggle만, 복잡한 layout 금지 |

**추가 금지 (V1 review 기반)**:
- 새 lens 추가 (person/event/world 외)
- 새 metric 추가 (4 world metric 외)
- 새 candidate 분류 추가 (3 bucket 외)
- candidate sorting alg 추가 (filter만)

---

## 5. V2 작업 단가 견적

| Tier | 후보 | 단가 |
|---|---|---|
| **Tier 1** | V2-1 marker opacity (CSS 5분) | 5분 |
| **Tier 1** | V2-2 agent follow (JS 10줄) | ~15분 |
| **Tier 2** | V2-3 candidate range highlight | ~30분 |
| **Tier 2** | V2-4 candidate filter | ~30분 |
| **Tier 3** | V2-5 person panel 강화 | ~50분 |
| **Tier 3** | V2-6 marker tooltip | ~30분 |

**V2 minimum** (Tier 1 only) = ~20분
**V2 standard** (Tier 1+2) = ~80분
**V2 full** (Tier 1+2+3) = ~160분

---

## 6. 검증 계획 (V2 implementation 시)

### V2 success criteria (Lee §1 기준 재해석)
1. ✅ Score-3 marker가 score-1 noise에서 분명히 떠 있다
2. ✅ Agent follow가 작동해서 12 agents 중 1명을 200 ticks 따라가기 가능
3. ✅ Candidate filter로 story_ready 5개만 보기 가능
4. ✅ Candidate 클릭 시 tick_range가 timeline에 보인다
5. ✅ V2 추가 기능이 V1 작동을 깨지 않음 (regression 0)

### V2 failure criteria
1. ❌ Tier 1 변경 후에도 score-1 noise 여전
2. ❌ Agent follow 시 panel content가 여전히 stale
3. ❌ Filter toggle 시 candidate list가 깨짐
4. ❌ V1의 5가지 tick 이동이 작동 안 함

**4/5 success / 0 failure 시 V2 minimal 성공**.

---

## 7. 다음 분기 (V2 implementation 후)

### Case A (V2 minimal 성공)
→ Phase V3 Observer + Story Panel 통합 (Lee directive §10 V3 영역) 검토

### Case B (V2 일부만 성공)
→ Tier 2/3 일부 polish 추가, 핵심 기능 유지

### Case C (V2 실패)
→ V1으로 회귀, encoding 자체 재설계 검토 (Lee Case B/C)

---

## 8. ABSOLUTE 원칙

- Rule #1: visual 코드에 person hardcoding 없음 유지
- Rule #6: 기존 candidate.py / curation.py / packet.py API 무수정 (visual layer 외부)
- 관찰기 ≠ 평가기: V2도 *분류/filter*만, *quality verdict* 안 함

---

## 9. 한 줄 요약

> **V2 minimal = V1의 6개 약점 중 Tier 1 (W1 marker noise + W3 agent follow) 우선 보강. 새 panel/lens/metric/scenario 추가 금지. CSS + JS 추가만, 기존 element 사용성 향상에 집중. Tier 1만 ~20분, full Tier 1+2+3은 ~160분 단가.**

---

**Versioning**: v1 (this plan) — 2026-04-30 V2 minimal plan 작성. Implementation은 별도 directive 시 진행.
