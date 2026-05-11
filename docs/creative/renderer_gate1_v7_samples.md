# Renderer Gate 1 v7 — Cycle 6 sample diff (Cycle 5 → Cycle 6)

**Date**: 2026-04-29
**Source**: Cycle 6 (Patch J) applied to `scripts/story/generate_trilogy_view.py`
**Cycle 5 baseline**: `renderer_gate1_v6_samples.md`
**Trigger**: Lee v2 약점 "Trilogy Act I/II SAT 톤 차이를 더 벌려야" — Cycle 3 Patch F는 SAT outcome line 분리만 처리, *escalation 의미*는 미구현.

---

## 0. Cycle 6 변경 요약

| Patch | 내용 | 효과 |
|---|---|---|
| J | Trilogy modal view에 Act II 전용 escalation envelope (preamble + echo) 추가. `generate_trilogy_view.py`만 수정, render_story_ko.py 무수정. | Act II narrative 본문 *전후*에 *escalation 의미* 명시 |

### 0.1 Patch J 위치

```
Act II epigraph: "이미 한 번 떨어진 비난은, 잊혀지기 전에 두 번째가 따라왔다."
↓ NEW preamble: "(첫 비난의 굳음이 풀리지 않은 채, 두 번째 비난이 그 자리에 떨어졌다. 사람들의 자세는 한 번이 아니라 두 번 멈춰 섰다.)"
Act II narrative 본문 (변경 없음)
↓ NEW echo: "(같은 거리, 같은 자세, 그러나 두 번의 비난이 동시에 머물렀다. 굳음은 한 결로 끝나지 않았다.)"
```

Act I + Act III는 envelope 없음. Trilogy 자체의 *escalation arc* (1→2→3)에서 Act II가 *깊어지는 굳음*이라는 정체성을 본문 *밖에서* 표시.

---

## 1. Sample — Trilogy Act II (전후 비교)

### Cycle 5 (이전)
```
### Act II — 두 번의 비난, 깊어지는 굳음
  (modal: SATURATION_DOMINATED, seed=0)

> 이미 한 번 떨어진 비난은, 잊혀지기 전에 두 번째가 따라왔다.

가뭄의 기색은 처음에는 시장의 끝자락에서 시작되었다. ... [narrative 본문]
... [SAT scarcity outcome line]
... [authority + shame residue]
```

### Cycle 6 (현재)
```
### Act II — 두 번의 비난, 깊어지는 굳음
  (modal: SATURATION_DOMINATED, seed=0)

> 이미 한 번 떨어진 비난은, 잊혀지기 전에 두 번째가 따라왔다.

(첫 비난의 굳음이 풀리지 않은 채, 두 번째 비난이 그 자리에 떨어졌다. 사람들의 자세는 한 번이 아니라 두 번 멈춰 섰다.)  ← NEW preamble

가뭄의 기색은 처음에는 시장의 끝자락에서 시작되었다. ... [narrative 본문 — 변경 없음]
... [SAT scarcity outcome line]
... [authority + shame residue]

(같은 거리, 같은 자세, 그러나 두 번의 비난이 동시에 머물렀다. 굳음은 한 결로 끝나지 않았다.)  ← NEW echo
```

### 변화점
- Act II *진입 시* preamble = "이미 한 번 + 두 번째" 명시 → Act I 대비 *escalation* 표시
- Act II *종료 시* echo = "두 번의 비난이 동시에 머물렀다" → Act III (3번째)와 다른 *accumulation* 의미
- Act II 본문 자체는 *변경 없음* — 회귀 위험 zero
- Act I + Act III에는 envelope 없음 — escalation은 Act II 정체성으로만 표시

---

## 2. Lee v2 약점 처리 (재인용)

> "Trilogy modal 3-act: 구조 자체가 강하다. **Act I/II의 SAT 톤 차이는 더 벌려야 한다**."

| Cycle | 처리 |
|---|---|
| Cycle 3 (Patch F) | SAT scarcity pool 3 → 5 line 확장 → Act I/II가 다른 outcome line 사용 (sample line 분리) |
| **Cycle 6 (Patch J)** | **Act II *envelope*로 escalation 의미 명시 (sample line 분리 외에 *meta context* 추가)** |

→ 두 cycle이 함께 Act I/II 차별화의 *두 측면* 처리:
- Cycle 3 = *문장 level 분리* (다른 image)
- Cycle 6 = *meta level 차별화* (Act II 정체성 명시)

---

## 3. 종합 비교 (Cycle 1 → Cycle 6 누적)

### 3.1 Lee v2 약점 처리 누적

| Lee v2 약점 | 처리 |
|---|---|
| 반복 stock phrase | ✅ Cycle 2 Patch A |
| outcome rhythm 미구분 | ✅ Cycle 2 Patch B + Cycle 3 D/E + Cycle 4 H |
| LOW_ACTIVITY branch | ✅ Cycle 2 Patch C |
| Trilogy Act I/II 톤 차이 | ✅ **Cycle 3 Patch F (line 분리) + Cycle 6 Patch J (escalation envelope)** |
| accusation 날카로움 | ✅ Cycle 4 Patch G (sharpness coexistence) |
| scene-level local action | ✅ Cycle 5 Patch I (Stage 2.5) |

→ Lee v2 약점 + Cycle 4/5 후보 모두 처리 완료. Cycle 6는 Trilogy 약점 *심화 처리*.

### 3.2 변경 통계 (Cycle 6 완료)

- `scripts/story/render_story_ko.py`: Cycle 1-5 변경 그대로 (Cycle 6 무수정)
- `scripts/story/generate_trilogy_view.py`: Cycle 6 Patch J 추가 (ACT_II_PREAMBLE/ECHO + modal_lines 삽입 로직 ~10 lines)
- 96 narrative 변경 없음 (render_story_ko.py 무수정)
- Trilogy modal_lines: 95 → ~99 lines (+4 for Act II envelope)
- test_story: 119 PASS 유지
- forbidden audit: 96/96 clean (envelope은 outputs/, generated/ 무관)

### 3.3 Pool 통계 (Cycle 6 완료)

| Pool | Cycle 5 | Cycle 6 |
|---|---|---|
| 모든 SCENARIO_*_POOLS (12 outcome × scenario) | 65 lines | (그대로) |
| LOW_ACTIVITY pools | 18 lines | (그대로) |
| OPENING_POOLS | 21 lines | (그대로) |
| SCENARIO_MICRO_ACTION_POOLS | 15 lines | (그대로) |
| **ACT_II envelope (NEW)** | 0 | **2 strings (preamble + echo)** |
| **총** | ~119 | **~121** (envelope은 sample-specific) |

---

## 4. Cycle 7 후보 (Cycle 6 후 미해결)

| 우선순위 | 항목 | 이유 |
|---|---|---|
| 1 | named motif continuity (도시/거리/광장 추적) | 가장 큰 coherence 효과, dict 확장 + coordinated selection |
| 2 | narrator distance control | 추상적 — 명확한 patch 매핑 어려움 |
| 3 | LOW_ACTIVITY × scenario | "부재의 긴장" 의도 충돌 가능 |
| 4 | full omniscient → micro 전환 | architecture 변경 (Cycle 5에서 부분 처리) |

→ Cycle 7는 *named motif continuity* — 큰 작업이지만 *coordinated pool selection* 패턴이 새 architecture 시도.

---

## 5. Versioning

| Version | Date | Note |
|---|---|---|
| Cycle 1 | 2026-04-28 | scarcity opening + cross-scenario REC + anchor signature |
| Cycle 2 | 2026-04-29 | Patch A/B/C — phrase de-template + outcome rhythm + LOW_ACTIVITY |
| Cycle 3 | 2026-04-29 | Patch D/E/F — scenario × outcome SAT/MIXED + opening/pool expansion |
| Cycle 4 | 2026-04-29 | Patch G/H — accusation REC sharpness + PARTIAL × scenario |
| Cycle 5 | 2026-04-29 | Patch I — scene-level micro-action beat (Stage 2.5) |
| **Cycle 6 (이 plan)** | **2026-04-29** | **Patch J — Trilogy Act II escalation envelope (sample-specific meta context)** |
| Cycle 7 후보 | TBD | named motif continuity / narrator distance |
