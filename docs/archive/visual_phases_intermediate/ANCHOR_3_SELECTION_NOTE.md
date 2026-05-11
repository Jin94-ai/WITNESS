# Anchor 3 Selection Note

**Date**: 2026-04-30
**Source**: `docs/plan.md` Phase 3 (Multi-anchor 최소 확장)
**Selected anchor**: **`vangogh_sacred_baseline`** (1순위, fallback 미사용)
**Status**: Selection 완료, export 검증됨

---

## 0. 선택 결과

> **vangogh_sacred_baseline** — 1순위 선택, fallback (accusation canonical) 사용 안 함.

선택 시점에 즉시 export 검증 완료:
- `python scripts/visual/export_dot_observer_data.py --anchor vangogh_sacred_baseline --output data/visual/dot_observer_data_vangogh.json`
- 결과: 595.6 KB, 200 ticks × 8 agents × 3 groups, 148 salience marks, 6 curated candidates

기존 export script 무수정. Schema v1 그대로.

---

## 1. 왜 vangogh_sacred를 선택했나

### Lee directive 1순위 조건 (Phase 3 §우선 anchor 선택)
- ✅ **기존 anchor와 world dynamics가 다를 것**: sacred pressure는 scarcity와 다른 metric system
- ✅ **event-heavy 또는 sacred/world-heavy 성격**: sacred = world-heavy (miracle / prayer 중심)
- ✅ **기존 exporter로 비교적 쉽게 생성 가능할 것**: 기존 selector library (`scripts/story/selector.py`)에 등록 + 기존 `build_real_stream_from_anchor` 작동 확인

### 1차 검증 결과 (export 시점)
```
Building Observer (vangogh_sacred_baseline seed=0 200 ticks)...
Wrote dot_observer_data_vangogh.json (595.6 KB)
Meta: 200 ticks × 8 agents × 3 groups
Salience marks: 148
Curated candidates: 6
```

→ **즉시 작동**. fallback (accusation canonical) 검토 불필요.

---

## 2. peter_scarcity 계열과 어떤 차이를 기대하는가

### 2.1 사전 분석 (export 후 데이터 비교)

| 측정 | peter_scarcity_baseline | vangogh_sacred_baseline | 차이 |
|---|---|---|---|
| Agent count | 12 | 8 | -33% |
| Salience marks (total) | 197 | 148 | -25% |
| Score-1 / score-2 / score-3 | 145 / 47 / 5 | **148 / 0 / 0** | score-2/3 모두 사라짐 |
| Candidate count | 8 | 6 | -25% |
| Candidate use_mode | story_ready 5 / low_activity_hold 3 | **모두 low_activity_hold (6)** | story_ready 0! |
| Candidate types | person 5 / world 1 / event 2 | **world 2 / event 4** (person 0) | type 분포 역전 |
| Active event types | 8 (accusation/denial/withdrawal 등) | 9 (**miracle_witnessed / prayer_invitation** 등 sacred-specific) | 사건 구성 다름 |
| Group mode changes | 12 | **1** | 거의 정적 |
| Avg tension | 0.183 | **0.004** | 극히 낮음 |
| Max blame_concentration | 0.457 | 0.19 | -58% |
| Max authority_vigilance | 0.25 | **0.0** | sacred는 authority 신호 없음 |
| Dynamic agents (≥3 distinct states) | 4/12 (33%) | **1/8 (12.5%)** | 더 정적 |

### 2.2 dynamics 차이 정성 정리
- **scarcity**: accusation → blame → denial → withdrawal 사슬 (dramatic)
- **sacred**: miracle / prayer / discussion 위주 (contemplative)
- **scarcity**가 *external pressure-driven*이라면 **sacred**는 *internal-state-driven* — visual에서 "부드러운 흐름"으로 표현됨

---

## 3. 검증 질문 5개 (Lee §검증 질문)

### Q1. 기존 scarcity 계열과 다른 visual pattern이 보이는가?
**기대**: 명확히 다른 pattern.
- timeline에 score-2/3 marker 거의 없음 → **yellow noise 위주의 차분한 timeline**
- group lane 거의 정적 (mode change 1회) → **단조로운 배경**
- candidate 모두 low_activity_hold → **회색 candidate strip**

→ "조용한 흐름" vs peter의 "격동" 시각적 식별 가능.

### Q2. world / event / person 중 어떤 lens가 가장 강한가?
**기대**: **event lens** > world lens > person lens.
- candidate types: event 4 / world 2 / person 0 → event lens 우세
- person dynamics 약함 (1/8 agent만 dynamic) → person lens 약함
- world lens: blame/suspicion 낮지만 sacred-specific events (miracle/prayer)는 world-level

### Q3. salience marker 분포가 달라지는가?
**기대**: **score-2/3 marker 0개**.
- score-1 148개 (전체 ticks 148/200 = 74%)
- score-2 = 0
- score-3 = 0
- → vangogh_sacred에서 *visual 강조점 없음*. salience system이 sacred dynamics를 *3-tier 분류*로 못 잡음.

### Q4. candidate bucket 분포가 달라지는가?
**기대**: **모두 low_activity_hold (6/6)**.
- story_ready 0 — 즉 시스템이 *render로 넘길 가치 있는 후보 0개*로 판정
- observation_only 0
- low_activity_hold 6 — *탐색용*으로만 분류

→ 현재 Q1-Q4 curation rule이 sacred dynamics를 "story-ready"로 판정하지 못함. 이는 *anchor 특성*인가 *curation rule 한계*인가 — **검증 필요**.

### Q5. Explorer UI가 새 anchor에서도 깨지지 않는가?
**기대**: ✅ 깨지지 않음.
- schema v1 그대로 (export script 무수정 + 기존 ANCHOR_DATA 패턴 따름)
- explorer.html은 anchor_id parameter로만 작동 → person hardcoding 없음 (ABSOLUTE Rule #1)
- UI 자동 갱신 (loadAnchor 함수가 모든 state reset)

---

## 4. Fallback 조건 (사용 안 함)

다음 조건 시 fallback 발동 예정이었음:
1. selector library에서 vangogh_sacred_baseline 미발견
2. anchor.builder(seed=0) 호출 실패
3. build_real_stream_from_anchor 호출 시 schema-incompatible 에러
4. export script가 person hardcoding 의존성으로 fail

**실제**: 위 4 조건 모두 발생 안 함. vangogh_sacred 즉시 작동.

Fallback 후보였던 *accusation canonical*은:
- selector library에 *standalone "accusation" anchor* 부재
- peter_scarcity_double / triple이 가까운 후보였으나 둘 다 scarcity scenario
- → vangogh_sacred가 *진정한 cross-scenario family* generalization 검증에 적합

---

## 5. 작업 단가 (실제 측정)

| 작업 | 시간 |
|---|---|
| selector library 확인 | < 1분 |
| build_real_stream_from_anchor 사전 검증 | 1분 |
| export 실행 (`--anchor vangogh_sacred_baseline`) | 30초 (200 ticks × 8 agents) |
| 비교 분석 (peter vs vangogh) | 5분 |
| 본 doc 작성 | 25분 |

**총합**: ~30분 (Phase 3 §1+§2 단계).

남은 작업:
- explorer.html에 anchor option 추가 (~5분)
- validation doc 작성 (~30분)

---

## 6. 다음 단계

### Phase 3 §3 — Explorer anchor option 추가
- `ANCHOR_DATA` 상수에 `vangogh_sacred_baseline` entry 1줄 추가:
  ```js
  vangogh_sacred_baseline: {
    single: "../data/visual/dot_observer_data_vangogh.json",
    cross: null,  // cross-seed export 안 함 (Phase 3 cross-seed 대확장 금지)
  }
  ```
- Anchor dropdown `<select>`에 `<option>` 1줄 추가
- 기존 anchor 동작 무영향

### Phase 3 §4 — Validation doc
- 검증 질문 5개 답변
- single-run view 작동 여부
- candidate panel 작동 여부
- 기존 scarcity 계열과 차이 정량
- 한계와 caveat
- Case A3-A / A3-B / A3-C 판정

---

## 7. ABSOLUTE 원칙 + Lee directive 준수

| 원칙 | 준수 |
|---|:---:|
| Rule #1 (no person hardcoding) | ✅ anchor_id parameter only |
| Rule #6 (engine API preservation) | ✅ engine 무수정 |
| Lee §"기존 schema 유지" | ✅ schema v1 그대로 |
| Lee §"새 schema 금지" | ✅ 미수행 |
| Lee §"기존 engine 수정 금지" | ✅ 미수행 |
| Lee §"새 scenario 생성 금지" | ✅ vangogh_sacred는 *기존 selector library* anchor |
| Lee §"기존 anchor/export 경로로 가능한 경우만 진행" | ✅ build_real_stream_from_anchor 그대로 |
| Lee §"cross-seed는 하지 말고 single-run만" | ✅ cross-seed export 미수행 |

---

## 8. 한 줄 요약

> **Anchor 3 = vangogh_sacred_baseline (1순위, fallback 미사용). 즉시 export 성공 (595.6 KB / 8 agents / 148 marks / 6 candidates). peter와 극명한 차이: score-2/3 marker 0개 / 모두 low_activity_hold / event lens 우세 / mode change 1회 / tension avg 0.004. 기존 scarcity의 격동 vs sacred의 차분한 흐름이 visual에서 직접 보일 것 — Phase 3 §3-§4 진행.**

---

**Versioning**: v1 (this note) — 2026-04-30 Anchor 3 selection 완료.
