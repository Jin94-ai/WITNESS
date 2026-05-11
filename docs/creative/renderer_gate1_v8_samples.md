# Renderer Gate 1 v8 — Cycle 7 sample diff (Cycle 6 → Cycle 7)

**Date**: 2026-04-29
**Source**: Cycle 7 (Patch K) applied to `scripts/story/render_story_ko.py`
**Cycle 6 baseline**: `renderer_gate1_v7_samples.md`
**Trigger**: Lee directive Type D 지속, Cycle 7 named motif (Lee 미명시 영역, over-engineering 위험 명시 후 진행).

---

## 0. Cycle 7 변경 요약

| Patch | 내용 | 효과 |
|---|---|---|
| K | SCENARIO_MOTIF_CLOSING_POOLS 신설 (3 scenarios × 5 lines) + render_narrative() 마지막 stage 추가 | narrative 끝에 *primary motif closing line* 추가 — coherence ring |

### 0.1 Patch K 위치 (Stage 6)

```
Stage 1: 도입 (opening)
Stage 2: 압력 상승
Stage 2.5: micro-action zoom-in (Cycle 5)
Stage 3: 반응 분기
Stage 4: 귀결
Stage 5: 사후 세계
↓ NEW Stage 6: motif coherence ring closing line
```

LOW_ACTIVITY는 별도 branch — Patch K skip ("부재의 긴장" 의도와 충돌).

---

## 1. Sample 1 — P10 REC accusation (motif closing 효과)

### Cycle 6 (이전) — 마지막 paragraph
> 거리는 천천히 다시 평소의 모양으로 돌아갔다. 그 흔적이 어딘가에 남았더라도, 사람들의 눈에는 잘 보이지 않았다.

### Cycle 7 (현재) — 마지막 2 paragraphs
> 거리는 천천히 다시 평소의 모양으로 돌아갔다. 그 흔적이 어딘가에 남았더라도, 사람들의 눈에는 잘 보이지 않았다.
>
> **손가락이 향했던 방향의 결은 다음 시각까지 옅게라도 남았다.**

### 변화점
- Stage 5 (aftereffect) 마지막 → 일반화 ("거리는 평소의 모양으로 돌아갔다")
- **Stage 6 (NEW motif closing)** → accusation-specific ("손가락이 향했던 방향의 결")
- *coherence ring*: 손가락 motif (Stage 2 손가락질 → Stage 2.5 시선 → Stage 4 어깨 자국 → **Stage 6 손가락 방향**)
- narrative 전체에 걸친 *accusation motif*가 마지막에 명시적으로 닫힘

---

## 2. Sample 2 — P9 SAT scarcity (motif closing 효과)

### Cycle 6 (이전)
> ...같은 침묵이 며칠을 이어졌다.

### Cycle 7 (현재)
> ...같은 침묵이 며칠을 이어졌다.
>
> **시장의 결은 다음 시각으로 천천히 옮겨 갔지만, 그 결의 흔적은 옅게라도 남았다.**

### 변화점
- scarcity-specific motif (시장의 결)
- *coherence ring*: 시장/곡식/창고 motif (Stage 1-5 전반에 걸쳐 등장 → Stage 6에서 마지막 closing)

---

## 3. Sample 3 — P6 MIXED scarcity (motif closing 효과)

### Cycle 6 (이전)
> ...두 자리가 같은 거리에 머물렀지만, 같은 결의 시간을 살지 않았다.

### Cycle 7 (현재)
> ...두 자리가 같은 거리에 머물렀지만, 같은 결의 시간을 살지 않았다.
>
> **빈손과 찬손 사이의 결은 다음 며칠을 천천히 흘러갔다.**

### 변화점
- scarcity-specific motif but *MIXED-resonant* (빈손 vs 찬손 = 두 결 split)
- variant_pick hash로 P9의 "시장의 결"과 다른 line 선택 (probe별 다양성)

---

## 4. Sample 4 — P_PV_09 LOW_ACTIVITY (변경 없음)

LOW_ACTIVITY는 `_render_narrative_low_activity()` 별도 branch — Patch K 적용 안 됨. "부재의 긴장" 의도 보존.

---

## 5. Sample 5 — Trilogy 3 acts (motif closing 추가됨)

각 Act 끝에 scarcity motif closing line 추가. Act II는 Cycle 6 envelope (echo)와 함께 *이중 closing* 효과:
```
Act II body (변경 없음)
↓ Cycle 6 ECHO: "(같은 거리, 같은 자세, 그러나 두 번의 비난이...)"
↓ Cycle 7 MOTIF CLOSING: "곡물 창고를 향한 시선이 거두어진 후에도..."
↓ "-" * 70
```

Act II의 closing 강화 — *meta envelope* + *motif ring* 둘 다.

---

## 6. 종합 비교 (Cycle 1 → Cycle 7 누적)

### 6.1 Lee v2 약점 + 자율 식별 후보 처리

| 항목 | Cycle | Status |
|---|---|---|
| #1 stock phrase | Cycle 2 A | ✅ Lee 명시 |
| #2 outcome rhythm | Cycle 2 B + 3 D/E + 4 H | ✅ Lee 명시 |
| #3 LOW_ACTIVITY | Cycle 2 C | ✅ Lee 명시 |
| #4 Trilogy Act I/II | Cycle 3 F + 6 J | ✅ Lee 명시 |
| #5 accusation 날카로움 | Cycle 4 G | ✅ Lee 명시 |
| #6 scene-level micro action | Cycle 5 I | ✅ 자율 (Cycle 4 후보) |
| **#7 named motif continuity** | **Cycle 7 K** | ✅ **자율 (Cycle 5 후보, over-engineering 위험 인지 후)** |

### 6.2 Pool 통계 (Cycle 7 완료)

| Pool | Cycle 6 | Cycle 7 |
|---|---|---|
| 모든 SCENARIO outcome × scenario pools | 65 lines | (그대로) |
| LOW_ACTIVITY pools | 18 | (그대로) |
| OPENING_POOLS | 21 | (그대로) |
| SCENARIO_MICRO_ACTION_POOLS | 15 | (그대로) |
| ACT_II envelope (Trilogy) | 2 strings | (그대로) |
| **SCENARIO_MOTIF_CLOSING_POOLS (NEW)** | 0 | **15 (3 × 5)** |
| **총** | ~121 | **~136** (+15) |

### 6.3 회귀 보장

- pytest tests/test_story → 119/119 PASS (Cycle 6 = Cycle 7)
- 96/96 forbidden audit clean
- Cycle 1-6 변경 모두 보존 (additive only)
- narrative 평균 길이 ~990자 → ~1030자 (+40자 / 1 sentence)

---

## 7. Rollback path

Lee가 "motif closing 부조화"라고 평가 시 즉시 rollback 가능:
1. `SCENARIO_MOTIF_CLOSING_POOLS` 정의 제거
2. `_motif_closing()` 함수 제거
3. `render_narrative()` 마지막 paragraph append 제거
4. 96 narrative 재생성 → Cycle 6 상태 복원

회귀 위험 ZERO (additive only).

---

## 8. Cycle 8 후보

| 우선순위 | 항목 | 작업 단가 | Lee 명시? |
|---|---|---|---|
| 1 | narrator distance control | 큼 (architecture) | ❌ 자율 |
| 2 | full omniscient → micro 전환 | 매우 큼 | ❌ 자율 |
| 3 | LOW_ACTIVITY × scenario | 작음 | ❌ 자율, 의도 충돌 가능 |
| 4 | Cycle 7 motif closing 효과 측정 후 (Lee 평가 필요) | — | — |

→ Cycle 8는 Cycle 7 효과 측정 후 결정. *over-engineering risk-cap* 인지.

---

## 9. Versioning

| Version | Date | Note |
|---|---|---|
| Cycle 1-6 | 2026-04-28~29 | Lee 명시 약점 5/5 + Cycle 4/5 후보 처리 |
| Retrospective | 2026-04-29 | Cycles 1-6 통합 review |
| **Cycle 7 (이 plan)** | **2026-04-29** | **Patch K — primary motif closing line (coherence ring, Lee 미명시 자율 영역, over-engineering risk-cap 명시)** |
| Cycle 8 후보 | TBD | narrator distance / Lee 평가 후 결정 |
