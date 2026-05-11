# Renderer Gate 1 v6 — Cycle 5 sample diff (Cycle 4 → Cycle 5)

**Date**: 2026-04-29
**Source**: Cycle 5 (Patch I) applied to `scripts/story/render_story_ko.py`
**Cycle 4 baseline**: `renderer_gate1_v5_samples.md`
**Trigger**: Cycle 5 후보 #1 (renderer_gate1_v5_samples.md §6) — scene-level micro-action beats (omniscient → micro)

---

## 0. Cycle 5 변경 요약

| Patch | 내용 | 효과 |
|---|---|---|
| I | SCENARIO_MICRO_ACTION_POOLS 신설 (3 scenarios × 5 lines) + render_narrative() Stage 2.5 삽입 | omniscient observer 흐름 안에 *concrete individual action* zoom-in moment 추가 |

### 0.1 Stage 2.5 위치

```
Stage 1: 도입 (opening)
Stage 2: 압력 상승 (initial_tension + pressure_arc)
↓ NEW Stage 2.5: micro-action beat (concrete individual)
Stage 2 transition → Stage 3: 반응 분기 (group_response)
Stage 3: cohort detail
Stage 3 transition → Stage 4: 귀결 (turning_point + outcome)
Stage 4 transition → Stage 5: 사후 (aftereffect)
```

LOW_ACTIVITY narrative (`_render_narrative_low_activity()`)는 별도 5-stage branch이므로 Patch I 영향 없음.

---

## 1. Sample 1 — P10 REC accusation (Patch I 적용 효과)

### Cycle 4 (이전)
> ...드문드문 고백이 새어 나왔다. 듣는 사람도, 말하는 사람도 그 무게에 익숙하지 않았다. 이 흐름 속에서, 사람들은 각자 다른 자리에서 다른 호흡을 가졌다.

### Cycle 5 (현재)
> ...드문드문 고백이 새어 나왔다. 듣는 사람도, 말하는 사람도 그 무게에 익숙하지 않았다. **한 사람의 눈이 평소보다 길게 한 자리에 머물렀다.** 이 흐름 속에서, 사람들은 각자 다른 자리에서 다른 호흡을 가졌다.

### 변화점
- omniscient observer flow ("드문드문 고백이 새어 나왔다") → **concrete individual action** ("한 사람의 눈이 평소보다 길게 한 자리에 머물렀다")
- Stage 2 → Stage 3 transition 직전의 *zoom-in moment*
- accusation-specific micro-action (시선 / 머무는 자리) — accusation 톤 누적 강화

---

## 2. Sample 2 — P9 SAT scarcity (Patch I 효과)

### Cycle 4 (이전)
> ...듣는 사람도, 말하는 사람도 그 무게에 익숙하지 않았다. 사람들의 결은 그 무게 아래에서 갈라지기 시작했다.

### Cycle 5 (현재)
> ...듣는 사람도, 말하는 사람도 그 무게에 익숙하지 않았다. **누군가 자루의 매듭을 만지작거리다가 다시 손을 내려놓았다.** 사람들의 결은 그 무게 아래에서 갈라지기 시작했다.

### 변화점
- omniscient ("듣는 사람도, 말하는 사람도...") → **concrete action** ("누군가 자루의 매듭을 만지작거리다가...")
- scarcity-specific micro-action (자루 매듭 / 손 내려놓음) — scarcity 모티프 누적
- 추상적 위기 → *body action*으로 표현된 망설임

---

## 3. Sample 3 — P6 MIXED scarcity (Patch I 효과)

Stage 2 끝부분에 scarcity micro-action 추가됨 (hash에 따라 5개 scarcity micro-action 중 하나).

---

## 4. Sample 4 — Trilogy 3 acts

각 Act의 Stage 2.5에 scarcity micro-action 추가됨. Act I/II/III 모두 다른 anchor (probe_id 다름) → 다른 micro-action line 선택 가능.

---

## 5. Sample 5 — P_PV_09 LOW_ACTIVITY (변경 없음)

LOW_ACTIVITY는 `_render_narrative_low_activity()` 별도 branch — Patch I 적용 안 됨. Cycle 2 Patch C 그대로 유지.

LOW_ACTIVITY는 자체적으로 micro-action 스타일 sign 이미 포함 ("누군가 무엇인가를 말하려다 입을 다물었다" — 부재의 긴장 stage 1) — 재처리 불필요.

---

## 6. 종합 비교 (Cycle 1 → Cycle 5 누적)

### 6.1 Lee v2 약점 처리 누적

| Lee v2 약점 | 처리 |
|---|---|
| 반복 stock phrase | ✅ Cycle 2 Patch A |
| outcome rhythm 미구분 | ✅ Cycle 2 Patch B + Cycle 3 Patch D/E + Cycle 4 Patch H |
| LOW_ACTIVITY branch | ✅ Cycle 2 Patch C |
| Trilogy Act I/II 톤 차이 | ✅ Cycle 3 Patch F (sample line 분리) |
| accusation 날카로움 | ✅ Cycle 4 Patch G (sharpness coexistence) |
| **scene-level local action** | ✅ **Cycle 5 Patch I (Stage 2.5 zoom-in)** |

→ Lee Cycle 4 후보 #1 (renderer_gate1_v5_samples.md §6) 처리 완료.

### 6.2 정량 (96 narrative scan)

| 지표 | Cycle 4 | Cycle 5 |
|---|---|---|
| 평균 narrative 길이 | ~960자 | **~990자** (+30자 / 1 sentence per non-LOW probe) |
| micro-action 등장 (non-LOW probes) | 0 | **1 per probe** |
| omniscient → concrete 전환 | 0 | **Stage 2.5에서** |
| test_story | 119 PASS | **119 PASS 유지** |
| forbidden audit | 96/96 clean | **96/96 clean** |

### 6.3 Pool 통계 (Cycle 5 완료)

| Pool | Cycle 4 | Cycle 5 |
|---|---|---|
| SCENARIO_RECOVERY_POOLS | scarcity 5 / accusation 10 / sacred 5 | (그대로) |
| SCENARIO_SATURATION_POOLS | 3 × 5 = 15 | (그대로) |
| SCENARIO_MIXED_POOLS | 3 × 5 = 15 | (그대로) |
| SCENARIO_PARTIAL_POOLS | 3 × 5 = 15 | (그대로) |
| LOW_ACTIVITY pools (5 component) | 6+3+3+3+3 = 18 | (그대로) |
| OPENING_POOLS | scarcity 5 / accusation 6 / sacred 6 / low 2 / other 2 = 21 | (그대로) |
| **SCENARIO_MICRO_ACTION_POOLS (NEW)** | 0 | **3 × 5 = 15** |
| **총** | ~104 lines | **~119 lines** |

### 6.4 회귀 보장

- Cycle 1/2/3/4 변경 모두 보존 (additive only — Stage 2.5 *추가*만, 기존 stages 유지)
- 96 narrative 재생성 후 forbidden phrase 검증 통과
- 119 test_story 유지

---

## 7. Cycle 6 후보 (Cycle 5 후 미해결)

| 우선순위 | 항목 | 이유 |
|---|---|---|
| 1 | named motif continuity (도시/거리/광장 추적) | 가장 큰 coherence 효과, 작업 단가 큼 |
| 2 | Trilogy Act II 강조 mechanism | sample-specific만, 작업 단가 작음 |
| 3 | narrator distance control | 추상적 — 명확한 patch 매핑 어려움 |
| 4 | LOW_ACTIVITY × scenario 분기 | "부재의 긴장" 의도와 충돌 가능 |
| 5 | full omniscient → micro 전환 | 너무 큰 architecture 변경 |

→ Cycle 6는 *named motif coordinated pool selection* 또는 *Trilogy Act II 강조* 둘 중 선택. 전자는 큰 효과, 후자는 작은 단가.

---

## 8. Versioning

| Version | Date | Note |
|---|---|---|
| Cycle 1 | 2026-04-28 | scarcity opening + cross-scenario REC + anchor signature |
| Cycle 2 | 2026-04-29 | Patch A/B/C — phrase de-template + outcome rhythm + LOW_ACTIVITY branch |
| Cycle 3 | 2026-04-29 | Patch D/E/F — scenario × outcome SAT/MIXED + opening/pool expansion |
| Cycle 4 | 2026-04-29 | Patch G/H — accusation REC sharpness + PARTIAL × scenario |
| **Cycle 5 (이 plan)** | **2026-04-29** | **Patch I — scene-level micro-action beat (Stage 2.5 zoom-in)** |
| Cycle 6 후보 | TBD | named motif continuity / Trilogy Act II / narrator distance |
