# Renderer Cycle 2 Plan — phrase de-template + outcome rhythm + LOW_ACTIVITY branch

**Date**: 2026-04-29
**Source**: Lee Gate 1 v2 결과 (`docs/LEE_RENDERER_GATE1_V2_FILLED_RESPONSE.md`)
**Long-range directive**: `docs/WITNESS_LONG_RANGE_NEXT_ACTIONS_2026-04-29.md` §2.2 + §3.1

---

## 0. Lee 평가 요약 (v2 통과 부분 + 약점)

### 0.1 Lee verdict (verbatim, H5)

> "**2/5는 creative output으로 쓸 만하고, 2/5는 salvage 가능하지만 아직 템플릿 냄새가 강하며, 1/5는 creative output으로는 탈락이다.**"
>
> "Renderer Gate 1 v2는 부분 통과다. ... 다음 작업은 Branch C 자체가 아니라 renderer cycle 2다."

### 0.2 Lee 평가 5 sample

| # | Sample | Lee 분류 | 핵심 약점 |
|---|---|---|---|
| 1 | P6 MIXED scarcity | **good** | (반복 문장 일부 줄여야) |
| 2 | Trilogy modal | **good** | Act I/II SAT 톤 차이 더 벌려야 |
| 3 | P9 SAT scarcity | flat + report-like | saturation 압박이 문장 리듬으로 안 옴 |
| 4 | P10 REC accusation | flat | accusation만의 날카로움 약함, scarcity/sacred recovery로 수렴 |
| 5 | P_PV_09 LOW_ACTIVITY | **bad** | "아무 일 없음"을 문학적으로 처리 못 함 |

### 0.3 Lee 우선 개선 3

1. **반복 결말문 / stock phrase 제거** — 같은 위치 같은 기능으로 반복되는 문장
2. **outcome별 tension curve 차별화** — SAT/REC/MIXED/PARTIAL/LOW_ACTIVITY 문장 리듬 분리
3. **LOW_ACTIVITY 전용 renderer 분기 신설** — "사건 안 됨"을 장면으로

---

## 1. 작업 범위 (Cycle 2 = 3 Patches)

```
Patch A — phrase de-template
Patch B — outcome rhythm control
Patch C — LOW_ACTIVITY renderer branch
```

### 1.1 Out of scope (Cycle 2 명시 제외)

- style profile 확장 (drama / webtoon / game IP) — forbidden_now §3
- density-aware sentence pool — forbidden_now §3
- Van Gogh annotated probe 신규 — forbidden_now §3
- 70+ trajectory labeling — forbidden_now §3
- engine/ 수정 — Rule #1 (인물 비종속 + ABSOLUTE)
- Branch C engine touch — forbidden_now §3

→ **Cycle 2는 `scripts/story/render_story_ko.py`만 수정. engine/ 무수정.**

---

## 2. Patch A — phrase de-template

### 2.1 Lee 식별 stock phrase 3개 (verbatim)

```
1. "그리고 그 모든 결은 결국 한 모양으로 굳어 갔다."  (TRANSITION_TO_OUTCOME[2])
2. "며칠이 지난 뒤, 사건이 끝난 자리에는 무언가가 남아 있었다."  (TRANSITION_TO_AFTEREFFECT[0])
3. "권위의 시선도 거두어지지 않았다."  (_aftereffect authority_residue)
```

### 2.2 분기 방향 (Lee verbatim)

| Outcome / 톤 | 결말 이미지 |
|---|---|
| scarcity SAT | 물성/식량/손끝/창고 |
| accusation REC | 시선/이름/소문/공적 공간 |
| sacred REC/PARTIAL | 기도/기적/침묵/믿음의 잔상 |
| LOW_ACTIVITY | "없음" 자체를 긴장으로 만드는 정적 이미지 |

### 2.3 구현

**A1**: `TRANSITION_TO_OUTCOME` flat list → `TRANSITION_TO_OUTCOME_BY_FS` dict (final_summary 별 분리). MIXED-specific만 "한 모양으로 굳어" 류 사용. SAT은 "굳어" 회피, REC는 "갈라" 회피.

**A2**: `TRANSITION_TO_AFTEREFFECT` flat list → `TRANSITION_TO_AFTEREFFECT_BY_FS` dict. SAT은 잔류감, REC은 회복의 잔향, MIXED는 두 결의 시간, PARTIAL은 미완 감, LOW_ACTIVITY는 부재의 여운.

**A3**: `_aftereffect`의 `authority_residue` 라인을 단일 문장 → outcome × pressure_type 조합별 pool로 변환. variant_pick으로 선택.

**A4**: `OUTCOME_POOLS` 확장 — scenario × outcome 조합별 이미지 시그너처 (Patch A2.2 표 기반).

---

## 3. Patch B — outcome rhythm control

### 3.1 Lee 의도 (verbatim)

> "SATURATION은 갇힘, RECOVERY는 풀림, MIXED는 분열이 핵심인데 현재는 셋 다 '거리의 공기 변화'로 귀결된다."

| Outcome | 문장 리듬 |
|---|---|
| RECOVERY_DOMINATED | 점점 열리는 호흡, 문장 길이 증가 |
| SATURATION_DOMINATED | 짧고 닫히는 문장, 제자리 반복 |
| MIXED | 두 공간/두 집단 대비, 교차 구조 |
| PARTIAL | 회복과 잔류의 불완전한 균형 |
| LOW_ACTIVITY | 부재의 긴장, 미발화된 사건 |

### 3.2 구현

**B1** `_outcome()` 직후 → `_outcome_rhythm()` 후처리 추가:
- SAT: 짧은 문장 강제 (마침표 빈도 ↑), "멈춘 / 굳은 / 그대로" 류 정적 동사 풀
- REC: 호흡 점층 — 짧은 한 문장 + 긴 한 문장 + 긴 문장 (반복)
- MIXED: 두 공간 대비를 명시적으로 한 문장 안에 (이미 _group_response에서 일부 됨)
- PARTIAL: "그치지 않았지만 / 더 자라지도" 류 양가 표현
- LOW_ACTIVITY: Patch C로 이전

**B2** `_pressure_arc()` 마지막 부분에 outcome-aware modifier:
- SAT 진행 중: "그 무게는 풀리지 않았다" 류 닫힘 신호
- REC 진행 중: "그러나 누군가의 입에서 작은 빛이 새어 나왔다" 류 열림 신호
- (현재는 모든 outcome에서 동일 confession_volume 처리 → 분기)

**B3** `_aftereffect()` 마지막 마무리 문장을 outcome별 분기:
- SAT: "그 침묵이 며칠을 이어졌다" 강화
- REC: 잔향 + 다시 일어선 거리
- MIXED: 갈림이 남은 자리
- PARTIAL: 어중간한 결이 남은 자리
- LOW_ACTIVITY: Patch C

---

## 4. Patch C — LOW_ACTIVITY 전용 renderer branch

### 4.1 Lee 의도 (verbatim)

> "LOW_ACTIVITY는 '아무 일 없음'이 아니라 '무언가 일어날 수 있었지만 끝내 일어나지 않음'으로 처리한다."

5 요소:
1. 작은 징후 2~3개
2. 확산되지 않는 rumor
3. 반응하지 않는 crowd
4. 무심한 authority
5. 끝내 사건이 되지 못한 tension

### 4.2 구현

**C1** `render_narrative()` 진입부에 분기:
```python
if ir["outcome"]["final_summary"] == "LOW_ACTIVITY":
    return _render_narrative_low_activity(ir)
```

**C2** `_render_narrative_low_activity()` 새 함수:
- Stage 1 (도입): 평소 같은 거리 + 작은 징후 2-3개 (predicted variant_pick pool)
- Stage 2 (확산 안 되는 rumor): "한 사람이 말했지만 그 말은 두 번째 사람에게 닿지 않았다"
- Stage 3 (반응 안 하는 crowd): "사람들의 발걸음은 평소처럼 흘렀다"
- Stage 4 (무심한 authority): "권위의 시선은 닿지 않은 곳에 머물렀다"
- Stage 5 (사건이 되지 못한 tension): "그것은 끝내 사건이 되지 못했다. 그러나 그렇기 때문에 더 무거운 자리가 있었다"

**C3** `render_summary()`도 동일 분기 — `_render_summary_low_activity()` (짧은 버전).

### 4.3 5 요소별 sentence pool

```
징후 (signs):
- "한 사람이 잠시 발을 멈췄다가 다시 걸어갔다"
- "어떤 자리에서는 평소보다 길게 머무는 사람들이 있었다"
- "거리 한쪽 끝에서 작은 술렁임이 있었지만 곧 가라앉았다"
- "누군가 무엇인가를 말하려다 입을 다물었다"

확산 안 되는 rumor:
- "한 사람이 말을 시작했지만, 두 번째 사람에게는 닿지 않았다"
- "소문은 한 자리에서만 머물렀고, 거리 끝까지 가지 못했다"
- "누군가의 말이 공기 중에 잠시 떠올랐다가 그대로 흩어졌다"

반응 안 하는 crowd:
- "사람들의 발걸음은 평소처럼 흘렀다. 누구도 그 작은 술렁임을 향해 고개를 돌리지 않았다"
- "거리는 평소의 결을 유지했고, 누구도 그것을 깨려 하지 않았다"
- "사람들은 모두 자기 자리에 있었지만, 어디에도 모이지 않았다"

무심한 authority:
- "권위의 시선은 다른 곳에 있었다. 거리 위의 작은 흔들림은 그 시선에 닿지 않았다"
- "권위는 거기 있었지만, 보아야 할 것을 보지 않았다"
- "권위의 자리는 비어 있는 듯도 했고, 채워져 있는 듯도 했다. 분명한 것은 어떤 시선도 그곳에서 내려오지 않았다는 것이다"

사건 못 됨 (tension):
- "그것은 끝내 사건이 되지 못했다. 그러나 그렇기 때문에 거리에는 다른 종류의 무게가 깔렸다"
- "무엇이 시작될 수 있었는지는 누구도 분명히 말하지 못했다. 다만 그것이 시작되지 않았다는 사실만이 남았다"
- "사건은 자라기 직전에 멈췄고, 그 멈춤은 그 자체로 한 종류의 흔적을 남겼다"
```

---

## 5. before / after 비교 기준

### 5.1 정량 (참고용)

| 지표 | Cycle 1 (현재) | Cycle 2 목표 |
|---|---|---|
| 5 sample 평균 길이 | ~900자 | ~1000자 (LOW_ACTIVITY ↑) |
| stock phrase (3 phrase) 등장 횟수 | 5/5 (모두) | ≤2/5 (MIXED만 허용) |
| LOW_ACTIVITY 길이 | 529자 | ≥800자 |

### 5.2 정성 (Lee 평가용)

5 sample × 평가 5 카테고리:

| Sample | Cycle 1 분류 | Cycle 2 목표 |
|---|---|---|
| P6 MIXED | good | good (유지) |
| Trilogy | good | good (Act I/II 차별화) |
| P9 SAT | flat + report-like | good 또는 awkward (report-like 탈출) |
| P10 REC accusation | flat | good 또는 awkward (scenario tone 확보) |
| P_PV_09 LOW_ACTIVITY | bad | 최소 awkward (bad 탈출) |

**Cycle 2 PASS 조건** (Lee 정의):
- 최소 3/5 good
- LOW_ACTIVITY가 bad 탈출
- P9가 report-like 탈출
- P10이 scenario tone 가짐

---

## 6. 작업 순서

1. **Patch A** 구현 — phrase de-template
2. **Patch B** 구현 — outcome rhythm
3. **Patch C** 구현 — LOW_ACTIVITY branch
4. 5 sample 재생성: `python scripts/story/render_story_ko.py P6 P_PV_09 P9 P10` + Trilogy regen
5. before/after diff `docs/creative/renderer_gate1_v3_samples.md`
6. Gate 1 v3 양식 `docs/creative/RENDERER_GATE1_V3_RESULTS.md` 빈 양식 생성
7. pytest engine fast + test_story (~1500 tests) 회귀 확인
8. Lee 평가 대기

---

## 7. 위험 + 보존

### 7.1 회귀 위험

- 기존 12 baseline (P1-P12) + 36 Branch C (S5/S4/S3/S2 × 9) narrative 변화 → 96 file 재생성 필요
- test_story (95 tests) 중 golden output 깨질 가능성 → semantic golden만 확인, 정확 string 매칭은 없음 (이미 verified)

### 7.2 보존 (Cycle 2가 건드리지 *않는* 것)

- IR schema (build_narrative_ir.py): 변경 없음
- Feature extraction (extract_story_features.py): 변경 없음
- Selector queryable library (engine/story/selector.py): 변경 없음
- Anchor library (5 anchors): 변경 없음
- engine/ 전체: 변경 없음

---

## 8. HARNESS 자가감사 (H7)

- [x] **H1** 수치는 Lee 평가 기준 (good/bad), trivial explanation 가능 — falsifiable by Lee Gate 1 v3
- [x] **H2** 시도 안 한 대안: (a) LLM rewriting (rule #4 위반), (b) sentence template 전체 교체 (Cycle 3급 작업), (c) drama profile (forbidden_now)
- [x] **H3** Rule #1 verbatim: `engine/` 인물 하드코딩 금지 — Cycle 2는 `scripts/story/`만 수정 → 위반 아님
- [x] **H4** What could still be wrong: outcome rhythm patch가 자연스러운 Korean prose가 아니라 mechanical 분기로 읽힐 수 있음 → Gate 1 v3가 falsification path
- [x] **H5** Lee verbatim §0.1 보존
- [x] **H6** 이 plan은 frame-neutral — Lee가 "구현 안 함" 결정도 가능 (단 directive가 GO 명시)
- [x] **H7** 이 doc 자체 — H7 자가감사 명시
- [x] **H8** sensitivity claim 없음 (5 sample illustration)

---

## 9. Versioning

| Version | Date | Note |
|---|---|---|
| v1 (자율 cycle) | 2026-04-28 | 3 우선 개선 (scarcity opening 3→5 / cross-scenario REC / anchor signature) — 자율 fill |
| **v2 (Cycle 2)** | **2026-04-29** | **이 plan — Lee Gate 1 v2 결과 반영. Patch A/B/C.** |
| v3 (post-Gate 1 v3) | TBD | Lee Gate 1 v3 결과 후 후속 plan |
