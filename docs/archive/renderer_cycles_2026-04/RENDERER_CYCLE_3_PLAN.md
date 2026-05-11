# Renderer Cycle 3 Plan — scenario × outcome 톤 분기 + opening expansion

**Date**: 2026-04-29
**Source**: Lee directive "Saturation에 도달해도 계속해서 Renderer 개선해" (saturation override)
**Predecessor**: `RENDERER_CYCLE_2_PLAN.md` (Patch A/B/C — phrase de-template + outcome rhythm + LOW_ACTIVITY branch)
**Target weakness**: Cycle 2가 *부분 처리*한 두 가지 — (a) Lee v2 평가 "P10 REC accusation = flat, accusation 날카로움 약함" + (b) "Trilogy Act I/II 톤 차이 부족"

---

## 0. Cycle 3 motivation

### 0.1 Cycle 2 한계 (renderer_gate1_v3_samples.md §6.1 미해결 항목)

| Lee v2 약점 | Cycle 2 처리 | Cycle 3 대상 |
|---|---|---|
| 반복 stock phrase 5/5 | ✅ MIXED 1/5만 유지 | (완료) |
| outcome별 tension curve 미구분 | ⚠️ 부분 (transition + authority + shame outcome-conditional) | (완료, ratio 측정 미정) |
| LOW_ACTIVITY 전용 branch 부재 | ✅ Patch C 신설 | (완료) |
| **Trilogy Act I/II 톤 차이 부족** | ⚠️ Act II authority 잔향만 차별화, opening 동일 | **Patch F 대상** |
| **accusation 날카로움 부족** | ❌ 미해결 | **Patch D + E 대상** |

### 0.2 Lee directive 변화

기존 (Type B-2 §8): "saturation 시 정지, 외부 입력 대기"
**새 directive**: "Saturation에 도달해도 계속해서 Renderer 개선해"

→ **Cycle 3는 외부 입력 도착 *전*에 자율 진행**. Gate 1 v3 평가 양식은 그대로 두고, Cycle 3 patches가 적용된 상태로 평가받게 됨 (Cycle 3 효과를 Cycle 2 효과와 함께 측정).

### 0.3 Scope — 작은 changes, 큰 효과

Cycle 3는 *기존 pool 확장*만 — 새 함수/branch 신설 없음. Cycle 2의 outcome-conditional dict 패턴을 *scenario × outcome*까지 확장.

---

## 1. Patch D — scenario × outcome SAT pools

### 1.1 Lee 분기 의도 (verbatim, RENDERER_CYCLE_2_PLAN.md §2.2)

| Outcome / 톤 | 결말 이미지 |
|---|---|
| scarcity SAT | 물성/식량/손끝/창고 |
| accusation REC | 시선/이름/소문/공적 공간 |
| sacred REC/PARTIAL | 기도/기적/침묵/믿음의 잔상 |

### 1.2 현재 상태

`SCENARIO_RECOVERY_POOLS` dict — REC만 scenario별 분기 (Cycle 1 자율 cycle #2):
- scarcity REC (3 lines) ✅
- accusation REC (3 lines) ✅
- sacred REC (3 lines) ✅

**누락**: SAT × scenario / MIXED × scenario / PARTIAL × scenario

### 1.3 Patch D 구현

`SCENARIO_SATURATION_POOLS` 신설:

```python
SCENARIO_SATURATION_POOLS = {
    "scarcity": [
        # 물성/식량/손끝/창고 이미지
        "곡식 자루는 같은 자리에 그대로였다. 그 무게를 옮길 수 있는 손은 어디에도 없었다.",
        "시장의 가격은 멈춘 채로 며칠을 흘렀고, 빈 자루는 점점 더 무거워 보였다.",
        "곡물 창고의 문은 닫힌 채였다. 그 문을 여는 결정은 누구의 자리에서도 내려오지 않았다.",
    ],
    "accusation": [
        # 시선/이름/소문/공적 공간 이미지 — 날카로움 강조
        "한 번 입에 오른 이름은 거두어지지 않았다. 그 이름 위에 다른 시선들이 계속 쌓여 갔다.",
        "광장의 한 자리에 손가락질의 잔상이 남아 있었다. 시선이 그 자리를 비켜 가는 동안에도, 이름은 그곳에 머물렀다.",
        "소문은 자기 결로 굳었다. 한 번 형태를 잡은 후로는 누구의 손도 그것을 풀지 못했다.",
    ],
    "sacred": [
        # 기도/기적/침묵/믿음의 잔상 이미지
        "성전 안의 침묵은 거리의 침묵으로 이어졌다. 그 두 침묵이 한 자리에서 만난 후로 어느 쪽도 다시 흩어지지 않았다.",
        "기도의 끝에서도 사람들은 같은 자세로 머물렀다. 무엇이 일어났는지, 무엇이 일어나지 않았는지 누구도 분명히 옮기지 못한 채였다.",
        "사람들의 시선은 성전 쪽을 향한 채 멈춰 있었다. 그 시선이 거두어지는 신호는 어디에서도 오지 않았다.",
    ],
}
```

### 1.4 _outcome() 호출 분기 변경

기존 (Cycle 2):
```python
if fs == "RECOVERY_DOMINATED" and pressure_type in SCENARIO_RECOVERY_POOLS:
    pool = SCENARIO_RECOVERY_POOLS[pressure_type]
```

새로 (Cycle 3):
```python
if fs == "RECOVERY_DOMINATED" and pressure_type in SCENARIO_RECOVERY_POOLS:
    pool = SCENARIO_RECOVERY_POOLS[pressure_type]
elif fs == "SATURATION_DOMINATED" and pressure_type in SCENARIO_SATURATION_POOLS:
    pool = SCENARIO_SATURATION_POOLS[pressure_type]
```

---

## 2. Patch E — scenario × outcome MIXED pools

### 2.1 의도

MIXED는 cohort split이 핵심 — scenario별로 *어느 자리들이 갈라지는지*가 다름.

### 2.2 Patch E 구현

`SCENARIO_MIXED_POOLS` 신설:

```python
SCENARIO_MIXED_POOLS = {
    "scarcity": [
        # 빈민가 vs 곡물 창고 vs 시장 분열
        "곡식의 무게가 한쪽에서는 풀리고, 다른 쪽에서는 더 깊게 가라앉았다. 같은 거리에 두 결의 시간이 흘렀다.",
        "빈민가의 손은 다시 펴졌고, 곡물 창고의 어깨는 그대로였다. 한 사건이 두 자리에 다른 결을 남겼다.",
        "시장의 가격은 한쪽 끝에서는 흔들리지 않았고, 다른 쪽에서는 여전히 가벼워지지 않았다.",
    ],
    "accusation": [
        # 가리킨 자 vs 가리킴 받은 자 vs 지켜본 자 분열
        "한쪽에서는 손가락이 거두어졌고, 다른 쪽에서는 그 손가락의 그림자가 그대로 남았다.",
        "이름이 풀려난 자리와 이름이 굳은 자리가 같은 거리 안에 있었다. 시선은 두 자리를 다르게 비추었다.",
        "광장의 한 끝에서는 사람들이 다시 모였고, 다른 끝에서는 손가락질의 잔상이 그대로였다.",
    ],
    "sacred": [
        # 성전 안 vs 바깥 vs 거리 분열
        "성전 안의 침묵과 바깥의 술렁임이 한 자리에서 갈라졌다. 같은 사건 아래에서도 두 결의 호흡이 흘렀다.",
        "기도가 닿은 자리와 기도가 닿지 않은 자리가 같은 거리 위에 머물렀다.",
        "성전 쪽으로 향한 어떤 시선은 다시 거두어졌고, 다른 시선은 그대로 그곳에 남았다.",
    ],
}
```

### 2.3 _outcome() 호출 분기 추가

```python
elif fs == "MIXED" and pressure_type in SCENARIO_MIXED_POOLS:
    pool = SCENARIO_MIXED_POOLS[pressure_type]
```

---

## 3. Patch F — accusation/sacred OPENING_POOLS 확장

### 3.1 현재 상태

`OPENING_POOLS`:
- scarcity: 5 lines (Cycle 1 자율 cycle에서 3 → 5 확장)
- accusation: 3 lines
- sacred: 3 lines
- low: 2 lines
- other: 2 lines

### 3.2 Trilogy hash collision 분석

`variant_pick(probe_id, slot, pool)` deterministic by md5 hash. Pool 3 → 33% 충돌. Pool 5 → 20% 충돌 — Trilogy Act I/II/III 같은 SAT outcome인 경우 collision 확률 낮춤.

### 3.3 Patch F 구현

accusation OPENING_POOLS 3 → 6:
```python
"accusation": [
    # 기존 3
    "공기는 이미 무거웠다. 광장과 관청 안마당과 좁은 거리 사이로 의심이 흐르고 있었고, ...",
    "그 자리에 서 있던 사람들은 알고 있었다. 무언가가 곧 시작될 것이라는 것을. ...",
    "거리는 평소처럼 흐르지 않았다. 광장과 관청 안마당 사이를 오가는 발걸음이 ...",
    # Cycle 3 신규 3
    "광장 한쪽 끝에서 누군가의 이름이 작게 입에 올랐다. 그 이름이 거리 끝까지 닿기 전에, 발걸음의 결이 한 박자 어긋났다.",
    "관청 안마당의 그림자가 평소보다 길게 거리 위로 떨어졌다. 그 그림자 안에서 사람들의 시선은 서로를 비껴 갔다.",
    "거리에는 평소와 같은 인사가 오갔다. 그러나 그 인사 끝에 매번 한 박자 더 머무르는 시선이 있었다.",
],
```

sacred OPENING_POOLS 3 → 6:
```python
"sacred": [
    # 기존 3
    "성전 바깥뜰에 사람들이 모여 있었다. ...",
    "성전을 향한 발걸음은 평소보다 많았다. ...",
    "성전 안에서는 기도가 이어졌고, 바깥에서는 그 기도를 듣는 사람들이 늘어 갔다. ...",
    # Cycle 3 신규 3
    "성전의 첫 빛이 안마당에 닿기 전부터 사람들이 모이고 있었다. 그 모임의 결은 평소의 모임과 한 박자 달랐다.",
    "성전 바깥 계단 위로 한 사람이 천천히 걸어 올라갔다. 그 한 걸음마다 거리의 호흡이 한 박자씩 늦어졌다.",
    "기도 소리는 들리지 않았지만, 사람들은 그 소리가 시작될 자리에 모여 있었다. 그 기다림 자체가 한 종류의 사건이었다.",
],
```

---

## 4. Out of scope (Cycle 4 후보)

- scene-level agency (omniscient observer → micro-action)
- named motif continuity (도시/거리/광장 모티프 추적)
- narrator distance control
- 70+ trajectory labeling — forbidden_now (해제 미적용 시)
- style profile 확장 — forbidden_now
- engine/ 수정 — Rule #1
- Van Gogh annotated probe 신규 — forbidden_now

---

## 5. 검증 + Cycle 3 PASS 기준

### 5.1 정량

| 지표 | Cycle 2 | Cycle 3 목표 |
|---|---|---|
| 5 sample 평균 길이 | ~1000자 | ~1100자 (scenario tone 추가로 증가 예상) |
| accusation outcome × scenario tone present | REC만 | REC + SAT + MIXED |
| Opening pool size (accusation/sacred) | 3 | 6 |
| Trilogy Act I/II opening 동일 hash 충돌 | 1/3 = 33% | 1/6 ≈ 17% |

### 5.2 정성

| Sample | Cycle 2 | Cycle 3 목표 |
|---|---|---|
| P9 SAT scarcity | SAT-specific 시간 정지 | + 곡식/창고 이미지 |
| P10 REC accusation | REC-specific (Cycle 1) | (변경 없음 — Lee 평가 대기) |
| **P_CV_01 MIXED accusation** | MIXED 일반 | + 손가락질/이름 이미지 |
| **P_CV_04 SAT scarcity** | SAT 일반 | + 곡식/창고 이미지 |
| Trilogy Act I vs II opening | 같은 line | 다른 line (hash collision 17%) |

### 5.3 회귀 보장

- pytest tests/test_story → 119/119 PASS 유지
- 96/96 forbidden phrase audit clean 유지
- Cycle 2 변경된 phrases는 그대로 보존 (additive only)

---

## 6. HARNESS 자가감사 (H7)

- [x] **H1** Lee 평가 기준 (good/bad) trivial explanation 가능
- [x] **H2** 시도 안 한 대안: (a) LLM rewriting (Rule #4), (b) scene-level agency (Cycle 4), (c) named motif (Cycle 4)
- [x] **H3** Rule #1 verbatim — Cycle 3는 `scripts/story/`만 수정 → 위반 아님
- [x] **H4** What could still be wrong: (i) accusation tone images 자연스러운 한국어 prose가 아닐 수 있음, (ii) opening pool 확장만으로 Trilogy 차별화 부족할 수 있음 (probe_id가 같으면 여전히 같은 hash) — Lee Gate 1 v3 평가가 falsification path
- [x] **H5** Lee verbatim: directive "Saturation에 도달해도 계속해서 Renderer 개선해" — saturation override 명시 보존
- [x] **H6** Lee가 후속 directive에서 "Cycle 3 멈춤" 가능 — 이 plan 자체는 frame-neutral
- [x] **H7** 이 doc — H7 자가감사 명시
- [x] **H8** sensitivity claim 없음 (5 sample illustration)

---

## 7. 작업 순서

1. Patch D (SCENARIO_SATURATION_POOLS) 추가 + _outcome() 분기 확장
2. Patch E (SCENARIO_MIXED_POOLS) 추가 + _outcome() 분기 확장
3. Patch F (accusation/sacred OPENING_POOLS 3 → 6 확장)
4. 5 sample 재생성 (P6/P9/P10/P_PV_09 + Trilogy)
5. 96 narrative 전체 재생성 (--all + --branch-c) + anchor variations + Trilogy
6. Stock phrase 차단 검증 + 96/96 forbidden audit
7. before/after Cycle 2 → Cycle 3 diff doc 작성 (`renderer_gate1_v4_samples.md`)
8. pytest test_story 119 PASS
9. progress.md + lessons L25

---

## 8. Versioning

| Version | Date | Note |
|---|---|---|
| Cycle 1 (자율) | 2026-04-28 | scarcity opening 3→5 / cross-scenario REC / anchor signature |
| Cycle 2 (Lee Gate 1 v2 후) | 2026-04-29 | Patch A/B/C (phrase de-template + outcome rhythm + LOW_ACTIVITY) |
| **Cycle 3 (이 plan)** | **2026-04-29** | **Patch D/E/F (scenario × outcome SAT/MIXED + opening expansion)** |
| Cycle 4 후보 | TBD | scene-level agency / named motif / narrator distance |
