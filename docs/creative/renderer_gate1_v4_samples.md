# Renderer Gate 1 v4 — Cycle 3 sample diff (Cycle 2 → Cycle 3)

**Date**: 2026-04-29
**Source**: Cycle 3 (Patch D + E + F) applied to `scripts/story/render_story_ko.py`
**Cycle 2 baseline**: `renderer_gate1_v3_samples.md`
**Trigger**: Lee directive "Saturation에 도달해도 계속해서 Renderer 개선해" (saturation override)

---

## 0. Cycle 3 변경 요약

| Patch | 내용 | 효과 |
|---|---|---|
| D | SCENARIO_SATURATION_POOLS 신설 + _outcome() SAT 분기 | scarcity/accusation/sacred SAT tone 구분 (Lee 의도 §2.2) |
| E | SCENARIO_MIXED_POOLS 신설 + _outcome() MIXED 분기 | cohort split scenario별 차별화 |
| F | OPENING accusation/sacred 3→6, scenario×outcome pools 3→5 | hash collision 33% → 17% (Trilogy Act I/II 차별화) |

---

## 1. Sample 1 — P6 MIXED scarcity (cohort split tone 강화)

### Cycle 2 (이전)
> 갈라진 자리는 좁혀지지 않았다. 누구의 잘못도 분명히 가려지지 않은 채, 사람들은 서로 다른 결로 굳었다. 같은 사건 아래에서도 사람들의 결은 둘로 갈렸다. 한 자리는 다시 숨을 쉬었고, 다른 자리는 굳어 있었다.

### Cycle 3 (현재)
> 갈라진 자리는 좁혀지지 않았다. 누구의 잘못도 분명히 가려지지 않은 채, 사람들은 서로 다른 결로 굳었다. **곡식의 무게가 한쪽에서는 풀리고, 다른 쪽에서는 더 깊게 가라앉았다. 같은 거리에 두 결의 시간이 흘렀다.** 어느 쪽이 옳았는지는 끝내 분명해지지 않았다.

### 변화점
- 일반 MIXED tone → **scarcity-specific MIXED** (곡식 무게가 한쪽에서 풀리고 다른 쪽에서 가라앉음)
- 빈민가 vs 곡물 창고 cohort split이 *물성 이미지*로 더 선명하게 표현

---

## 2. Sample 2 — Scarcity Trilogy modal (Act I/II 차별화)

### Cycle 2 (이전, Act I/II SAT scarcity)
- Act I: "회복의 길은 끝내 열리지 않았다. 사람들은 자리에 머물렀다. 어떤 자리는 시간이 흘러도 풀리지 않았다."
- Act II: "회복의 길은 끝내 열리지 않았다. 사람들은 자리에 머물렀다. 어떤 자리는 시간이 흘러도 풀리지 않았다." *(같은 line, hash collision)*

### Cycle 3 (현재, Act I/II 다른 line)
- Act I: "회복의 길은 끝내 열리지 않았다. **곡물 창고의 문은 닫힌 채였다. 그 문을 여는 결정은 누구의 자리에서도 내려오지 않았다.**"
- Act II: "회복의 길은 끝내 열리지 않았다. **시장의 가격은 멈춘 채로 며칠을 흘렀고, 빈 자루는 점점 더 무거워 보였다.**"

### 변화점
- Act I → 창고/문/결정 이미지 (정지된 결정)
- Act II → 시장/가격/빈 자루 이미지 (연속된 정체)
- 둘 다 SAT scarcity tone 유지하되 micro-image 분리
- Lee v2 약점 "Act I/II SAT 톤 차이를 더 벌려야" 직접 대응

---

## 3. Sample 3 — P9 SAT scarcity (보고서 톤 → 물성 이미지)

### Cycle 2 (이전)
> 더 이상 올라갈 수 없는 곳까지 무거움이 차올랐다. 사람들은 그 자리에 갇혔다. 사람들은 자리에 머물렀다. 어떤 자리는 시간이 흘러도 풀리지 않았다.

### Cycle 3 (현재)
> 더 이상 올라갈 수 없는 곳까지 무거움이 차올랐다. 사람들은 그 자리에 갇혔다. **곡식 자루는 같은 자리에 그대로였다. 그 무게를 옮길 수 있는 손은 어디에도 없었다.**

### 변화점
- 일반 SAT 표현 → **scarcity-specific SAT** (곡식 자루 그대로 / 무게 옮길 손 없음)
- "사람들은 자리에 머물렀다" 추상적 → "곡식 자루는 같은 자리에 그대로" 구체적 물성
- Lee v2 약점 "saturation 압박이 문장 리듬으로 안 옴" 부분 대응 — 추상 → 물성 변환

---

## 4. Sample 4 — P10 REC accusation (변경 적음, Cycle 1 SCENARIO_RECOVERY_POOLS["accusation"]가 이미 적용됨)

### Cycle 2 (이전)
> 어느 순간, 무거움이 더 이상 자라지 않았다. 거리는 천천히 다시 숨을 쉬기 시작했다. **거리의 시선은 여전히 한 방향으로 모였지만, 그 방향에서 더 이상 무엇도 떨어지지 않았다.**

### Cycle 3 (현재)
변경 없음 — accusation REC pool은 Cycle 1에서 이미 추가됨. P10은 동일.

### 미해결
- Lee v2 약점 "accusation 날카로움 약함, recovery 톤으로 수렴" — Cycle 3에서 OPENING accusation 3→6 확장 + accusation × MIXED pool 추가했지만 P10은 REC outcome이라 영향 적음
- accusation REC pool 자체를 Cycle 4에서 더 sharper-edged image로 확장 검토 필요
- **Cycle 4 후보**

---

## 5. Sample 5 — P_PV_09 LOW_ACTIVITY (변경 없음, Patch C 적용 그대로)

Cycle 3는 LOW_ACTIVITY branch 미수정. 5 stage 부재의 긴장 그대로 유지.

---

## 6. Sample 6 — P_CV_01 MIXED accusation (Cycle 3 신규 효과 가장 잘 보이는 sample)

### Cycle 2 (이전)
> Opening: "거리는 평소처럼 흐르지 않았다. 광장과 관청 안마당 사이를 오가는 발걸음이 지나치게 조심스러웠고..."
> Outcome: "사람들은 서로 다른 결로 굳었다. 같은 사건 아래에서도 사람들의 결은 둘로 갈렸다. 한 자리는 다시 숨을 쉬었고, 다른 자리는 굳어 있었다."

### Cycle 3 (현재)
> Opening: "**광장 한쪽 끝에서 누군가의 이름이 작게 입에 올랐다. 그 이름이 거리 끝까지 닿기 전에, 발걸음의 결이 한 박자 어긋났다.**" (Patch F 신규 accusation opening)
> Outcome: "사람들은 서로 다른 결로 굳었다. **한쪽에서는 손가락이 거두어졌고, 다른 쪽에서는 그 손가락의 그림자가 그대로 남았다.** 어느 쪽이 옳았는지는 끝내 분명해지지 않았다. **두 결의 시간이 한 거리 위에서 천천히 다른 결로 멀어져 갔다.**"

### 변화점
- Opening → accusation-specific (이름 / 발걸음 결 / 거리 끝)
- Outcome → accusation MIXED tone (손가락 / 그림자 / 두 결의 시간)
- accusation 날카로움이 *outcome*에서 표현됨 (P10 REC에서 미해결이지만 P_CV_01 MIXED에서는 효과 보임)

---

## 7. 종합 비교

### 7.1 정량 (96 narrative scan)

| 지표 | Cycle 1 | Cycle 2 | Cycle 3 |
|---|---|---|---|
| "한 모양으로 굳어 갔다" 등장 | 5/5 (sample) → 96/96 (전체) | 2/96 | **2/96** (MIXED only, intentional) |
| "권위의 시선도 거두어지지 않았다" 등장 | 5/5 (sample) → 96/96 (전체) | 1/96 | **1/96** (SAT, intentional) |
| "며칠이 지난 뒤..." 등장 | flat | 4/96 (SAT only) | **4/96** (SAT only, intentional) |
| Trilogy Act I/II SAT outcome line 동일 | 동일 (1/3 collision) | 동일 (1/3 collision) | **다름 (1/5 collision)** |
| OPENING pool size accusation/sacred | 3/3 | 3/3 | **6/6** |
| scenario × outcome pool coverage | REC만 | REC만 | **REC + SAT + MIXED** (PARTIAL 미적용) |
| 96/96 forbidden audit | clean | clean | **clean** |

### 7.2 정성 (Lee v2 약점 처리 추적)

| Lee v2 약점 | Cycle 2 | Cycle 3 |
|---|---|---|
| 반복 stock phrase | ✅ outcome-conditional | ✅ 유지 |
| outcome rhythm 미구분 | ⚠️ 부분 (transition + authority + shame) | ✅ scenario × outcome 추가 분기 |
| LOW_ACTIVITY 전용 branch | ✅ Patch C | ✅ 유지 |
| **Trilogy Act I/II 톤 차이** | ⚠️ Act II authority만 | ✅ **Patch F로 SAT outcome line 분리** |
| **accusation 날카로움** | ❌ 미해결 | ⚠️ MIXED (P_CV_01)에서 효과, REC (P10)은 Cycle 4 |

### 7.3 회귀 보장

- pytest tests/test_story → 119/119 PASS (Cycle 2 = Cycle 3, 회귀 없음)
- 96/96 forbidden phrase audit clean (Cycle 2 = Cycle 3)
- Cycle 2 patches는 그대로 보존 (additive only)

---

## 8. Cycle 4 후보 (미해결 약점 + 새 기회)

| 우선순위 | 항목 | 이유 |
|---|---|---|
| 1 | accusation REC tone deepening (P10 직접 대응) | Lee v2 약점 #4 미해결 |
| 2 | scene-level local action beats (omniscient → micro) | Cycle 3 plan §4 Cycle 4 후보 |
| 3 | named motif continuity (도시/거리/광장 추적) | Cycle 3 plan §4 Cycle 4 후보 |
| 4 | PARTIAL × scenario pools (현재 미적용) | 대칭성 — REC/SAT/MIXED는 적용, PARTIAL만 미적용 |
| 5 | narrator distance control | Cycle 3 plan §4 Cycle 4 후보 |

---

## 9. Versioning

| Version | Date | Note |
|---|---|---|
| Cycle 1 (자율) | 2026-04-28 | scarcity opening 3→5 / cross-scenario REC / anchor signature |
| Cycle 2 (Lee Gate 1 v2 후) | 2026-04-29 | Patch A/B/C — phrase de-template + outcome rhythm + LOW_ACTIVITY |
| **Cycle 3 (saturation override)** | **2026-04-29** | **Patch D/E/F — scenario × outcome SAT/MIXED + opening 3→6 / pools 3→5** |
| Cycle 4 후보 | TBD | accusation REC deepening / scene-level / named motif / narrator distance |
