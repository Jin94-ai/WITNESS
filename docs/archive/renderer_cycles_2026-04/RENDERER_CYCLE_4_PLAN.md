# Renderer Cycle 4 Plan — accusation REC sharpness + PARTIAL × scenario

**Date**: 2026-04-29
**Source**: Cycle 3 미해결 약점 + 대칭성 회복 (renderer_gate1_v4_samples.md §8 우선순위 1 + 4)
**Predecessor**: `RENDERER_CYCLE_3_PLAN.md` (Patch D/E/F — scenario × outcome SAT/MIXED + opening/pool expansion)
**Target weakness**:
- Lee v2 약점 #4 미해결: P10 REC accusation flat — accusation 날카로움 약함
- Cycle 3 대칭성 누락: PARTIAL × scenario pool 미적용 (REC/SAT/MIXED만 있음)

---

## 0. Cycle 4 motivation

### 0.1 Lee v2 약점 추적 (verbatim)

> "P10 REC accusation: 읽히지만 accusation만의 날카로움이 약하다. scarcity/sacred recovery와 같은 톤으로 수렴한다."

Cycle 3 Patch D/E/F가 SAT/MIXED는 처리했지만 *REC accusation의 sharpness*는 미해결. P_CV_01 (MIXED accusation)에서 효과 보였지만 P10 (REC accusation)은 그대로 일반 REC tone.

### 0.2 현재 SCENARIO_RECOVERY_POOLS["accusation"] (Cycle 1 + 3)

```python
"accusation": [
    "비난이 닿았던 자리에서도 사람들은 다시 일어섰다. 손가락질의 끝은 어딘가에서 풀려났다.",
    "광장과 안마당의 공기는 여전히 무거웠지만, 그 무거움은 누구의 어깨도 더는 누르지 않았다.",
    "거리의 시선은 여전히 한 방향으로 모였지만, 그 방향에서 더 이상 무엇도 떨어지지 않았다.",
    "한 번 입에 올랐던 이름이 천천히 거리에서 흩어졌다. 그 이름은 누구의 것도 아닌 것으로 돌아갔다.",
    "관청 안마당의 그림자가 옅어지고, 광장의 발걸음은 다시 평소의 결을 찾아갔다.",
],
```

5개 모두 "풀려나는 / 옅어지는 / 흩어지는" tone — Lee가 지적한 "scarcity/sacred recovery와 수렴" 정확히 그 패턴.

### 0.3 Lee 의도 재해석

"accusation 날카로움이 *살아 있는* recovery" — 풀림은 풀림이지만 *손가락질의 잔재가 visible*하게. 즉:
- 회복은 분명히 발생했지만 *그 회복 안에 accusation의 그림자*가 남음
- "손가락이 거두어졌다" → "거두어졌지만 그 손가락 끝의 잔영은 남아 있었다"
- "이름이 흩어졌다" → "흩어졌지만 그 이름이 떨어진 자리는 한 박자 더 무거운 결을 지녔다"

= **Recovery + Sharpness coexistence pattern**.

### 0.4 PARTIAL × scenario 누락 분석

Cycle 3에서 SCENARIO_*_POOLS 추가 시:
- ✅ SCENARIO_RECOVERY_POOLS (Cycle 1 + Cycle 3 확장)
- ✅ SCENARIO_SATURATION_POOLS (Cycle 3 신설)
- ✅ SCENARIO_MIXED_POOLS (Cycle 3 신설)
- ❌ **SCENARIO_PARTIAL_POOLS 누락**

PARTIAL은 outcome cell의 ~20%를 차지 (P6 MIXED는 PARTIAL과 인접 boundary). 대칭성 회복이 marginal하지만 작업 단가 작음.

---

## 1. Patch G — accusation REC sharpness deepening

### 1.1 전략

**기존 5개 보존 + sharpness-living 5개 추가 = 10개 pool**.

이유:
- 기존 line은 *일반적 REC tone* — 회복이 명확한 경우에 적합
- 신규 line은 *날카로움 살린 REC tone* — accusation 잔재가 남는 경우
- variant_pick(probe_id, slot, pool) hash 분산 → 일부 probe (P10 포함)가 신규 line으로 옮겨감

### 1.2 신규 5개 — Sharpness coexistence pool

```python
# Cycle 4 Patch G additions to SCENARIO_RECOVERY_POOLS["accusation"]:
"손가락질의 끝은 거두어졌지만, 그 끝에서 떨어진 잔영은 거리 위에 잠시 머물렀다.",
"이름이 거리에서 흩어졌어도, 그 이름이 처음 떨어진 자리는 한 박자 더 무거운 결을 지녔다.",
"광장의 시선은 다시 흩어졌다. 그러나 어떤 시선은 처음 향했던 자리에서 한 번 더 멈췄다가 풀렸다.",
"비난의 무게는 풀렸지만, 그 무게가 닿았던 어깨에는 옅은 자국이 남았다.",
"손가락이 거두어진 후에도 그 손가락이 향했던 방향은 거리 위에 한동안 그대로였다.",
```

각 line의 구조: **회복 명시 + 잔재 명시** (둘 다 한 문장 안에).

### 1.3 효과 측정

- 5 → 10 pool: hash collision 1/5 = 20% → 1/10 = 10%
- accusation REC probe (P10, P_PV_01, P_PV_03 등)의 sharpness 표현 가능성 ↑
- P10이 신규 5개 중 하나로 매핑되면 v3에서 v5로 sharper

---

## 2. Patch H — SCENARIO_PARTIAL_POOLS 신설

### 2.1 의도

PARTIAL = "흔들림은 그치지 않았지만 더 깊이 가라앉지도 않았다" — *어중간한 결*.

scenario별 PARTIAL 표현:
- **scarcity PARTIAL**: 곡식이 일부 풀리고 일부 그대로 (어떤 자루는 비어 있고 어떤 자루는 채워짐)
- **accusation PARTIAL**: 시선이 거두어졌으나 이름은 남음 (손가락은 거두어졌지만 그림자가 머문 채)
- **sacred PARTIAL**: 기도가 끝났지만 침묵이 남음 (모임은 흩어졌지만 그 자리의 결은 그대로)

### 2.2 구현

```python
SCENARIO_PARTIAL_POOLS = {
    "scarcity": [
        "곡식의 무게는 일부 풀렸고, 일부는 그대로였다. 자루의 한 끝은 가벼워졌지만 다른 끝은 여전히 무거웠다.",
        "시장의 가격은 한 박자 흔들리다 멈췄다. 분명한 끝도, 분명한 시작도 없는 시간이 흘렀다.",
        "곡물 창고의 문은 한 번 열렸다가 다시 닫혔다. 그 사이에 무엇이 옮겨졌는지는 분명하지 않았다.",
        "빈손에 무엇인가 채워지는 듯하다가 다시 비워졌다. 어느 쪽도 분명한 결을 잡지 못했다.",
        "거리의 자루들은 일부만 풀렸다. 나머지는 그 자리에서 여전히 같은 무게로 머물렀다.",
    ],
    "accusation": [
        "손가락은 거두어졌지만, 그 손가락이 향했던 방향은 그대로였다. 어느 쪽도 분명한 결을 잡지 못했다.",
        "이름은 천천히 흩어지다 한 자리에서 멈췄다. 그 이름이 완전히 사라지지도, 완전히 굳지도 않은 채였다.",
        "광장의 시선은 일부 풀렸고, 일부는 그대로였다. 어떤 자리는 다시 평소의 결을 찾았고 어떤 자리는 한 박자 멈춘 채였다.",
        "비난의 무게는 한 번 가벼워졌다가 다시 무거워졌다. 분명한 회복도 분명한 굳음도 아닌 시간이 흘렀다.",
        "관청 안마당의 그림자는 옅어지다 다시 짙어졌다. 어느 쪽으로도 분명한 끝이 오지 않았다.",
    ],
    "sacred": [
        "기도는 끝났지만 그 자리의 침묵은 풀리지 않았다. 사람들의 자세는 어중간한 결로 머물렀다.",
        "성전 바깥뜰의 모임은 일부 흩어졌고, 일부는 그대로였다. 어느 쪽도 분명한 결을 잡지 못했다.",
        "성전 안의 침묵이 거리까지 흘러나왔다가 한 자리에서 멈췄다. 그 침묵이 풀리는 신호도, 더 깊어지는 신호도 오지 않았다.",
        "기도 소리는 한 번 거두어졌다가 다시 시작되었다. 그 사이에 사람들의 결은 어느 쪽으로도 분명히 기울지 않았다.",
        "성전 쪽으로 향한 시선은 일부 거두어졌고, 일부는 그대로였다. 두 결이 같은 거리 위에 머물렀다.",
    ],
}
```

### 2.3 _outcome() 분기 확장

```python
elif fs == "PARTIAL" and pressure_type in SCENARIO_PARTIAL_POOLS:
    pool = SCENARIO_PARTIAL_POOLS[pressure_type]
```

---

## 3. Out of scope (Cycle 5+ 후보)

- scene-level local action beats (omniscient → micro)
- named motif continuity (도시/거리/광장 추적)
- narrator distance control
- LOW_ACTIVITY × scenario 분기 (현재 단일 LOW_ACTIVITY branch)
- Trilogy Act II "두 번째 비난" 강조 (현재 Act I와 outcome 같음)

---

## 4. 검증

### 4.1 정량

| 지표 | Cycle 3 | Cycle 4 목표 |
|---|---|---|
| accusation REC pool size | 5 | **10** |
| PARTIAL × scenario coverage | 0 | **3 scenarios × 5 lines** |
| accusation REC outcome × scenario × probe collision | 1/5 = 20% | **1/10 = 10%** |
| test_story | 119 PASS | 119 PASS 유지 |
| forbidden audit | 96/96 clean | 96/96 clean 유지 |

### 4.2 정성

| Sample | Cycle 3 | Cycle 4 목표 |
|---|---|---|
| P10 REC accusation | 일반 REC tone | sharpness coexistence (변경 가능, hash 의존) |
| P_PV_06 PARTIAL scarcity | 일반 PARTIAL | scarcity-specific PARTIAL (자루 일부 풀림) |
| P_CV_07 PARTIAL sacred | 일반 PARTIAL | sacred-specific PARTIAL (기도 끝났지만 침묵 남음) |

---

## 5. HARNESS 자가감사 (H7)

- [x] **H1** Lee 평가 기준 (good/bad) trivial explanation 가능
- [x] **H2** 시도 안 한 대안: (a) accusation REC pool *교체* (보존 원칙 위반 가능), (b) scene-level rendering (Cycle 5), (c) LLM rewriting (Rule #4)
- [x] **H3** Rule #1 verbatim — Cycle 4는 `scripts/story/`만 수정 → 위반 아님
- [x] **H4** What could still be wrong: (i) sharpness coexistence tone이 자연스러운 한국어 prose가 아닐 수 있음 (어색한 대비 구조), (ii) 10 pool 확장이 hash 분산이지만 P10이 여전히 일반 line에 매핑될 수 있음 — Lee Gate 1 v3 / v5 평가가 falsification path
- [x] **H5** Lee verbatim §0.1 보존
- [x] **H6** Lee가 "Cycle 4 멈춤" 가능 — 이 plan frame-neutral
- [x] **H7** 이 doc — H7 자가감사 명시
- [x] **H8** sensitivity claim 없음 (5-6 sample illustration)

---

## 6. 작업 순서

1. Patch G — SCENARIO_RECOVERY_POOLS["accusation"] 5 → 10 확장
2. Patch H — SCENARIO_PARTIAL_POOLS 신설 + _outcome() PARTIAL 분기
3. 5 sample + 추가 PARTIAL sample 재생성
4. 96 narrative 전체 재생성 (--all + --branch-c) + Trilogy
5. forbidden audit 96/96 clean
6. before/after Cycle 3 → Cycle 4 diff doc (`renderer_gate1_v5_samples.md`)
7. pytest test_story 119 PASS
8. progress.md + lessons L26

---

## 7. Versioning

| Version | Date | Note |
|---|---|---|
| Cycle 1 | 2026-04-28 | scarcity opening 3→5 + cross-scenario REC + anchor signature |
| Cycle 2 | 2026-04-29 | Patch A/B/C — phrase de-template + outcome rhythm + LOW_ACTIVITY |
| Cycle 3 | 2026-04-29 | Patch D/E/F — scenario × outcome SAT/MIXED + opening/pool expansion |
| **Cycle 4 (이 plan)** | **2026-04-29** | **Patch G/H — accusation REC sharpness + PARTIAL × scenario** |
| Cycle 5 후보 | TBD | scene-level / named motif / narrator distance |
