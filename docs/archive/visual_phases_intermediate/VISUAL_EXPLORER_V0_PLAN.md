# Visual Explorer v0 — Plan

**Date**: 2026-04-30
**Source**: `VISUAL_TRACK_SYNTHESIS_REVIEW.md` Case V-A 판정 + Lee directive (plan 작성, 구현 금지)
**Status**: Plan only — *별도 directive 시까지 대기*. 새 코드 0.
**Goal**: V0-V2 + Cross-seed 4 단계 통합 → *통합 도구* (run/anchor selector + replay + cross-seed + candidate panel + story panel side-by-side).

---

## 0. 핵심 원칙

> **v0 = 통합. 새 capability 추가 아님.**

- 새 lens / metric / bucket / scenario 추가 금지
- React / framework 도입 금지
- visual polish 금지
- player intervention 금지
- 기존 4 단계 자료 (V0-V1 / V2 / Anchor 2 / Cross-seed) *그대로 사용*
- v0 = *navigation + selector + integration* layer 추가

---

## 1. v0 구성 요소

### 1.1 단일 entry HTML
- `visual/explorer.html` (신규) — 단일 진입점
- 외부 dependency 0 (vanilla JS + SVG only)
- 4 view를 single page에서 전환 (탭 또는 sidebar nav)

### 1.2 4 view 통합

| View | Source | 역할 |
|---|---|---|
| **Single-run replay** | 기존 `dot_observer_replay.html` 로직 import | 한 세계 200 ticks 추적 |
| **Cross-seed comparison** | 기존 `dot_observer_cross_seed.html` 로직 import | 5 seeds 비교 |
| **Candidate panel** | Q1-Q4 curated 8 카드 (use_mode 색 코딩) | Curation 결과 검토 |
| **Text packet/story side panel** | `scripts/observer/candidate_packet.py` 출력을 *static* JSON으로 export | candidate 클릭 → packet 표시 |

### 1.3 Run/anchor selector (UI 상단)
```
[ Anchor: peter_scarcity_baseline ▼ ]  [ View: Single-run / Cross-seed ]
```
- Anchor dropdown:
  - peter_scarcity_baseline (default)
  - peter_scarcity_triple
  - peter_scarcity_double (옵션)
  - peter_scarcity_high_density (옵션)
  - vangogh_sacred_baseline (옵션 — cross-scenario family)
- View toggle: Single-run / Cross-seed
- (Cross-seed 선택 시) Seed selector로 deep-dive 가능

### 1.4 Story panel side-by-side
- Candidate 클릭 시 우측 panel에 *render_candidate_story* 결과 표시
- 3-lens 토글 (person / event / world)
- packet 형식 표시 (6-field) — 기존 `format_packet_text` 출력
- 텍스트는 export 단계에서 *pre-rendered* (HTML이 동적 fetch 안 함, performance + offline 작동)

---

## 2. v0 통합 layout (예상)

```
┌─────────────────────────────────────────────────────────────────┐
│ [Anchor: peter_scarcity_baseline ▼] [View: Single ●  Cross ○]  │
├──────────────────────────────────────────────┬──────────────────┤
│                                              │                  │
│   Main canvas                                │  Side panel      │
│   (single-run dots OR cross-seed rows)       │                  │
│                                              │  Candidate list  │
│                                              │   (filterable)   │
│                                              │                  │
│   Timeline-bar (single-run only)             │  Selected:       │
│                                              │   - World stats  │
│                                              │   - Salience tags│
│                                              │   - Packet       │
│                                              │   - Story (3 lens│
│                                              │     toggle)      │
│                                              │                  │
└──────────────────────────────────────────────┴──────────────────┘
```

---

## 3. 데이터 dependencies

### 3.1 기존 활용 (별도 export 신규 불필요)
- `data/visual/dot_observer_data.json` (V0-V1 baseline)
- `data/visual/dot_observer_data_triple.json` (Anchor 2)
- `data/visual/dot_observer_cross_seed_triple.json` (Cross-seed)

### 3.2 신규 export 필요 (별도 script — 작은 단가)
- 각 anchor × seed별 *pre-rendered packet/story text* JSON
- 예: `data/visual/packets_baseline_seed0.json`, `packets_triple_seed0.json` 등
- 출력: candidate_id → {packet_text, person_lens, event_lens, world_lens}
- 신규 script: `scripts/visual/export_packets_for_visual.py` (~80줄 예상)

### 3.3 Schema 무수정 원칙
- `cross_seed_v1` schema 무수정
- v1 schema 무수정
- 신규 packet schema는 *별도* (`packets_v0`) — 기존 schema에 영향 없음

---

## 4. 최소 사용 흐름 3개 (Lee §4 verbatim)

### 흐름 1 — 한 세계를 replay로 관찰
1. 진입: `explorer.html`
2. Anchor selector default = `peter_scarcity_baseline`
3. View toggle default = Single-run
4. Main canvas = V2 dot replay (timeline + dots + 5 panel)
5. Side panel = candidate list + selected candidate detail
6. 사용자가 timeline-bar / candidate card / dot click으로 자유 이동
7. **결과**: 200 ticks를 5가지 navigation으로 추적, candidate 8개 검토

### 흐름 2 — seed 5개를 비교
1. View toggle → Cross-seed
2. Anchor selector default = `peter_scarcity_triple` (cross-seed 데이터 있음)
3. Main canvas = 5 seed small multiples (lane + markers + range overlay)
4. Side panel = outcome distribution banner + selected seed detail
5. Seed row 클릭 → side panel 갱신 (candidates, salience, final modes)
6. **결과**: 5 seeds 한 화면에서 outcome 분포 + per-seed detail

### 흐름 3 — candidate를 골라 packet/story 확인
1. (흐름 1 또는 2 진행 중) candidate 카드 클릭
2. Side panel에 packet 6-field 표시 + 3-lens story toggle
3. 사용자가 person/event/world toggle 해서 lens 비교
4. (선택) 다음 candidate 카드 클릭으로 순회
5. **결과**: candidate → packet → story가 *같은 화면*에서 검토 가능

---

## 5. 작업 단가 견적

| Phase | 작업 | 단가 |
|---|---|---|
| **v0-A** | `explorer.html` 통합 layout (single + cross + side panel) | ~90분 |
| **v0-B** | Anchor selector + view toggle (UI + URL routing) | ~30분 |
| **v0-C** | `export_packets_for_visual.py` 신규 (~80줄) | ~40분 |
| **v0-D** | Story side panel (3-lens toggle + packet format) | ~40분 |
| **v0-E** | 사용 흐름 3개 검증 + review doc | ~30분 |

**총합**: 약 230분 (~4시간).

**v0 minimum** (단일 흐름만 = v0-A + v0-B): ~120분
**v0 standard** (3 흐름 모두): ~230분

---

## 6. 출력 산출물 (v0 구현 시)

| 산출물 | 용도 |
|---|---|
| `visual/explorer.html` | 단일 entry (4 view 통합) |
| `scripts/visual/export_packets_for_visual.py` | packet/story pre-render export |
| `data/visual/packets_<anchor>_seed<n>.json` | pre-rendered text JSON |
| `docs/visual/VISUAL_EXPLORER_V0_REVIEW.md` | v0 검증 + 사용 흐름 3개 결과 |

기존 자료 *모두 무수정*:
- `dot_observer_static.html` / `dot_observer_replay.html` / `dot_observer_cross_seed.html` 보존
- `dot_observer_data*.json` 모두 보존
- 기존 export script 2개 모두 보존

---

## 7. v0 검증 기준 (구현 후 사용)

### 성공 기준 4+/6
1. ✅ 단일 entry HTML로 4 view 모두 도달 가능
2. ✅ Anchor selector로 다른 anchor 즉시 전환
3. ✅ Single-run / Cross-seed view 토글 작동
4. ✅ Candidate 클릭 → packet/story 같은 화면에 표시
5. ✅ 3 사용 흐름 모두 막힘 없이 진행
6. ✅ 기존 V0-V2 + Cross-seed 자료 깨지지 않음

### 실패 기준 2+/5
1. ❌ Single-run view가 V2 대비 regression
2. ❌ Cross-seed view가 기존 dot_observer_cross_seed.html 대비 regression
3. ❌ Anchor 전환 시 stale state (panel content 미갱신)
4. ❌ Story panel이 비어있거나 잘못된 candidate에 매칭
5. ❌ 외부 dependency 추가 (React 등)

---

## 8. v0 *후속* 분기 (구현 후, 별도 directive 시)

### Case Vex-A (v0 잘 작동)
- v0 freeze
- 다음 단계 (별도 directive 시):
  - Multi-anchor cross-seed (trilogy view)
  - Cross-scenario validation (vangogh)
  - Phase V3 — Observer + Story Panel 더 깊은 통합

### Case Vex-B (v0 부분 약함)
- 약점 수정 (encoding 또는 UI 흐름)
- 새 기능 추가 금지

### Case Vex-C (v0 통합이 사용성 떨어짐)
- 4 view 분리 모드로 회귀
- visual track 자체 freeze 후 text 중심 회귀 검토

---

## 9. v0 *하지 말아야 할 것* (Lee directive 일관)

| 금지 항목 | v0 상태 |
|---|:---:|
| React dashboard | ❌ vanilla JS only |
| 3D / 캐릭터 / animation | ❌ 2D SVG only |
| player intervention | ❌ observer-only |
| story renderer 재개 | ❌ 기존 render_candidate_story 결과 *static export*만 |
| new scenario | ❌ peter family + vangogh 등 selector library 안 |
| multi-anchor 대규모 확장 | ❌ 1 anchor at a time (UI selector) |
| visual polish | ❌ MVP 수준 통합만 |
| V3 기능 구현 | ❌ V3 (intervention prototype 등)는 별도 phase |
| 새 lens / metric / bucket | ❌ 기존 자료 그대로 활용 |

---

## 10. ABSOLUTE 원칙

- Rule #1: visual 코드에 person hardcoding 없음 (anchor_id parameter only)
- Rule #6: engine/observer/* 모두 무수정 (v0는 visual layer 안에서만 작동)
- 관찰기 ≠ 평가기: v0도 *분류 + 탐색*만, *quality verdict* 안 함

---

## 11. 다음 단계

**본 plan은 plan만**. Lee 명시 directive 시 v0 구현 진행:
1. v0-A `explorer.html` 통합 layout 작성
2. v0-B Anchor selector + view toggle
3. v0-C packet export script
4. v0-D Story side panel
5. v0-E 검증 + `VISUAL_EXPLORER_V0_REVIEW.md`

별도 directive 없을 시 *대기*. 새 코드 0.

---

## 12. 한 줄 요약

> **Visual Explorer v0 = V0-V1 + V2 + Anchor 2 + Cross-seed 4 단계 자료를 *통합 entry HTML로 재구성*. 새 capability 0, 통합 layer만 추가. Anchor selector + view toggle + candidate-to-packet/story side panel. 3 사용 흐름 (replay 관찰 / seeds 비교 / candidate→story). 작업 단가 ~120-230분. 본 doc은 plan만 — 구현은 별도 directive 시.**

---

**Versioning**: v1 (this plan) — 2026-04-30 Visual Explorer v0 plan 대기.
