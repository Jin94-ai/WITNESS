# Appendix — Method Caveat

**Date**: 2026-04-30
**Source**: Branch C lock decision § 6 (verbatim) + paper §7.4 (single-seed bias)
**용도**: Asset pack v1 모든 narrative의 method limitation 명시

---

## 0. 핵심 caveat (verbatim from BRANCH_C_LOCK_DECISION.md §6)

> The external eval explicitly accepts the single-seed limitation:
> - It supports configuration dependence as **existence evidence**.
> - It should **not** be used to claim the **exact sensitivity magnitude**.
> - Any public or paper-facing claim should phrase this as:
>   **"single-seed external readability eval supports configuration-sensitive outcome divergence; magnitude requires cross-seed confirmation."**

---

## 1. Locked claims (asset pack에서 사용 가능)

### 1.1 Existence claims

✅ Configuration이 outcome class에 영향 미친다 (within-scenario divergence existence).

✅ 같은 scenario pressure가 cohort 배치 / cast 구성에 따라 다른 outcome class로 갈라질 수 있다.

✅ External readability eval (GPT-5.5)이 within-scenario divergence를 detect함.

### 1.2 Specifics that are locked

- 3/3 scenario groups (accusation / scarcity / sacred) show ≥3 distinct final-summary outcomes
- Most explanatory dimension: placement / cohort routing (primary), cast composition (secondary)
- All 18 self-calls match headline labels (18/18)
- GPT-5.5 readability: 18/18 readable, 18/18 CLEAR_FLOW, 18/18 CAN_EXPLAIN

---

## 2. NOT locked (asset pack에서 사용 금지)

### 2.1 Magnitude claims

❌ "67% sensitivity" — single-seed bias 가능 ±33pp (paper §7.4).

❌ "S5 placement는 44%, S4 cast는 56% 변동" — single-seed에서만 측정.

❌ "특정 dimension이 정확히 X% 영향" — cross-seed ensemble 필요.

### 2.2 Behavioral / predictive claims

❌ "predicts human behavior"
❌ "proves moral causality"
❌ "simulates real society"
❌ "AI sociology engine"
❌ "deterministic moral simulator"

이는 CLAUDE.md ABSOLUTE Rule #5 (terminology 과장 금지) 일관.

---

## 3. Cross-seed evidence 부재

### 3.1 현재 evidence 종류

| Evidence type | 출처 | 적합한 claim |
|---|---|---|
| Single-seed snapshot | 18 probes (P_NEW_01-18) | within-scenario divergence existence |
| 5-seed modal | scarcity Trilogy (3 anchors) | nonmonotonic dynamics existence |
| External readability eval | GPT-5.5 18 probes | configuration sensitivity readability |

### 3.2 필요하지만 부재한 evidence

| Required for | Evidence not yet collected |
|---|---|
| Magnitude claim | 5-seed cross-seed ensemble per dimension |
| Determinism claim | Multi-run modal stability |
| Predictive claim | External validation against human ground truth |

→ 이러한 evidence 부재 시 *existence claim*만 사용.

---

## 4. Per-asset method note

### Asset 01 (P6 MIXED scarcity)

- Single-seed snapshot at peter_scarcity_baseline configuration
- 같은 anchor 다른 seed에서 다른 outcome class (RECOVERY / SATURATION 등)도 나옴 (paper §6.9 cross-seed 측정)
- 이 narrative는 *existence example*: "이런 cohort split outcome이 가능하다"

### Asset 02 (P10 REC accusation)

- Single-seed snapshot at S5 placement variation
- *Recovery outcome 발생 가능성* 보여줌 (deterministic 아님)
- 같은 configuration 다른 seed에서 SATURATION 또는 MIXED 가능

### Asset 03 (P_CV_01 MIXED accusation)

- Single-seed snapshot at S4 cast variation (full n=10)
- P10과 *same scenario / different configuration* contrast
- *Configuration-dependence existence evidence*

### Asset 04 (Scarcity Trilogy modal)

- 5-seed modal across 3 anchors (1/2/3 accusations)
- *modal seed pattern* — 각 anchor의 가장 흔한 결말 1개 표시
- *Nonmonotonic dynamics existence*: 비난 횟수 증가가 단조 증가 결과로 이어지지 않음
- 5-seed distribution 표는 §5-seed 분포에서 visible (asset 04 본문 마지막)

---

## 5. Public framing rules

### 5.1 Use phrases

- "narrative dynamics experiment"
- "configuration-sensitive narrative dynamics"
- "generative simulator"
- "scenario pressure × cohort routing → outcome class divergence"
- "existence evidence (single-seed)"
- "nonmonotonic dynamics demo (modal across 3 anchors)"

### 5.2 Avoid phrases

- "predicts" / "proves" / "deterministic"
- "AI sociology engine"
- "67% sensitivity" 또는 specific magnitude
- "real society simulation"

---

## 6. Asset pack v1 boundary

이 v1 pack은 **internal curated bundle**이다. 다음 조건이 모두 충족되어야 *public release* 가능:

1. 5-seed cross-seed validation completed (currently absent)
2. Lee 검토 + approval
3. Caveat strengthening (영문 mirror 등)
4. Renderer Cycle 7 freeze 유지 (no Cycle 8)

→ 현재 상태 = *internal curated only*.

---

## 7. Versioning

| Version | Date | Note |
|---|---|---|
| **v1 (this caveat)** | **2026-04-30** | **Branch C lock decision + paper §7.4 single-seed bias 통합 caveat** |
