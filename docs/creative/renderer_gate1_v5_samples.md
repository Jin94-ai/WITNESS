# Renderer Gate 1 v5 — Cycle 4 sample diff (Cycle 3 → Cycle 4)

**Date**: 2026-04-29
**Source**: Cycle 4 (Patch G + H) applied to `scripts/story/render_story_ko.py`
**Cycle 3 baseline**: `renderer_gate1_v4_samples.md`
**Trigger**: Cycle 3 미해결 약점 #1 (Lee v2: P10 accusation 날카로움) + 대칭성 회복 (PARTIAL × scenario)

---

## 0. Cycle 4 변경 요약

| Patch | 내용 | 효과 |
|---|---|---|
| G | SCENARIO_RECOVERY_POOLS["accusation"] 5 → 10 (sharpness coexistence 5개 추가) | P10 REC accusation에서 "회복 명시 + 잔재 명시" 한 문장 구조 |
| H | SCENARIO_PARTIAL_POOLS 신설 + _outcome() PARTIAL 분기 | scarcity/accusation/sacred PARTIAL tone 분기 (대칭성 회복) |

---

## 1. Sample 1 — P10 REC accusation (Lee v2 약점 #4 직접 대응)

### Cycle 3 (이전)
> 어느 순간, 무거움이 더 이상 자라지 않았다. 거리는 천천히 다시 숨을 쉬기 시작했다. **거리의 시선은 여전히 한 방향으로 모였지만, 그 방향에서 더 이상 무엇도 떨어지지 않았다.**

### Cycle 4 (현재)
> 어느 순간, 무거움이 더 이상 자라지 않았다. 거리는 천천히 다시 숨을 쉬기 시작했다. **비난의 무게는 풀렸지만, 그 무게가 닿았던 어깨에는 옅은 자국이 남았다.**

### 변화점
- 일반 REC tone ("시선이 모였지만 떨어지지 않았다") → **sharpness coexistence** ("무게는 풀렸지만 자국이 남았다")
- 회복 명시 + 잔재 명시가 **한 문장 안**에 동시 표현
- accusation의 sharpness가 *recovery 안에 살아있음* — Lee 의도 정확히 반영

### Lee v2 verbatim 매핑
> "accusation만의 날카로움이 약하다. scarcity/sacred recovery와 같은 톤으로 수렴한다."

→ Patch G의 sharpness coexistence pool이 *날카로움 + 회복* 둘 다 표현하는 line 5개 추가. P10이 hash 분산으로 신규 line 매핑됨.

---

## 2. Sample 2 — P_PV_06 PARTIAL scarcity (Patch H 효과)

### Cycle 3 (이전)
> 흔들림은 그치지 않았지만, 더 깊이 가라앉지도 않았다. 어중간한 자리에서 사람들은 멈췄다. **어떤 자리는 며칠이 지난 뒤에야 미세하게 움직였다.** 분명한 끝이 오지 않은 채 시간은 한 걸음씩 흘렀다.

### Cycle 4 (현재)
> 흔들림은 그치지 않았지만, 더 깊이 가라앉지도 않았다. 어중간한 자리에서 사람들은 멈췄다. **곡식의 무게는 일부 풀렸고, 일부는 그대로였다. 자루의 한 끝은 가벼워졌지만 다른 끝은 여전히 무거웠다.** 분명한 끝이 오지 않은 채 시간은 한 걸음씩 흘렀다.

### 변화점
- 일반 PARTIAL tone ("미세하게 움직였다") → **scarcity-specific PARTIAL** (자루 일부 풀림 / 한 끝 가벼움 / 다른 끝 무거움)
- 물성 이미지 (자루 / 한 끝 vs 다른 끝)로 PARTIAL의 *어중간함*을 구체화

---

## 3. Sample 3 — P_CV_07 PARTIAL sacred (Patch H 효과)

### Cycle 3 (이전)
> 어떤 자리는 며칠이 지난 뒤에야 미세하게 움직였다.

### Cycle 4 (현재)
> 기도는 끝났지만 그 자리의 침묵은 풀리지 않았다. 사람들의 자세는 어중간한 결로 머물렀다.
> *(또는 hash에 따라 다른 sacred PARTIAL line)*

### 변화점
- 일반 PARTIAL → **sacred-specific PARTIAL** (기도 끝남 + 침묵 남음 / 자세 어중간 결)
- 종교적 모티프 (기도 / 침묵 / 자세)로 PARTIAL의 *어중간함*을 구체화

---

## 4. Sample 4-6 — 변경 없음

- P6 MIXED scarcity → Cycle 3 변경 그대로
- Trilogy modal → Cycle 3 변경 그대로 (Act III REC accusation은 SCENARIO_RECOVERY_POOLS["accusation"] hash에 따라 신규 line 가능)
- P9 SAT scarcity → Cycle 3 변경 그대로
- P_PV_09 LOW_ACTIVITY → Cycle 2 Patch C 그대로
- P_CV_01 MIXED accusation → Cycle 3 변경 그대로

---

## 5. 종합 비교 (Lee v2 약점 누적 처리)

| Lee v2 약점 | Cycle 2 | Cycle 3 | Cycle 4 |
|---|---|---|---|
| 반복 stock phrase | ✅ outcome-conditional | ✅ 유지 | ✅ 유지 |
| outcome rhythm 미구분 | ⚠️ 부분 | ✅ scenario × outcome 추가 | ✅ + PARTIAL × scenario (대칭성) |
| LOW_ACTIVITY branch | ✅ Patch C | ✅ 유지 | ✅ 유지 |
| Trilogy Act I/II 톤 차이 | ⚠️ Act II authority | ✅ Patch F SAT line 분리 | ✅ 유지 |
| **accusation 날카로움** | ❌ 미해결 | ⚠️ MIXED만 | ✅ **Patch G sharpness coexistence (REC P10 직접 대응)** |

→ Lee v2 약점 5개 모두 처리 (Trilogy Act I/II는 partial하지만 sample line 분리 달성).

### 5.1 정량 (96 narrative scan)

| 지표 | Cycle 3 | Cycle 4 |
|---|---|---|
| accusation REC pool size | 5 | **10** |
| PARTIAL × scenario coverage | 0 | **3 scenarios × 5 lines** |
| accusation REC hash collision | 1/5 = 20% | **1/10 = 10%** |
| test_story PASS | 119/119 | **119/119 유지** |
| forbidden audit | 96/96 clean | **96/96 clean** |

### 5.2 회귀 보장

- Cycle 1/2/3 변경 모두 보존 (additive only)
- 96 narrative 재생성 후 forbidden phrase 검증 통과
- 119 test_story 유지

---

## 6. Cycle 5 후보 (Cycle 4까지 미해결)

| 우선순위 | 항목 | 이유 |
|---|---|---|
| 1 | scene-level local action beats (omniscient → micro) | Cycle 3 plan §4 Cycle 4 후보로 미뤘음, 가장 큰 구조적 변경 |
| 2 | named motif continuity (도시/거리/광장 추적) | narrative depth 강화 |
| 3 | LOW_ACTIVITY × scenario 분기 (현재 단일 branch) | 대칭성 |
| 4 | narrator distance control | observer perspective 다양화 |
| 5 | Trilogy Act II 강조 mechanism (probe-aware) | "두 번째 비난의 깊이" 표현 |

Cycle 5는 *구조적 변경*이 필요한 작업 (단순 dict 확장이 아님). 가장 큰 변경 — Cycle 4까지 dict 확장 패턴이 마무리되었기에, 다음은 *새 architecture*.

---

## 7. Versioning

| Version | Date | Note |
|---|---|---|
| Cycle 1 | 2026-04-28 | scarcity opening 3→5 + cross-scenario REC + anchor signature |
| Cycle 2 | 2026-04-29 | Patch A/B/C — phrase de-template + outcome rhythm + LOW_ACTIVITY |
| Cycle 3 | 2026-04-29 | Patch D/E/F — scenario × outcome SAT/MIXED + opening/pool expansion |
| **Cycle 4 (이 plan)** | **2026-04-29** | **Patch G/H — accusation REC sharpness + PARTIAL × scenario (대칭성)** |
| Cycle 5 후보 | TBD | scene-level / named motif / narrator distance (구조적 변경) |
