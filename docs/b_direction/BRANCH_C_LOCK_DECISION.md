# Branch C — Lock Decision

**Date**: 2026-04-30
**Source**: `BRANCH_C_GPT55_RESPONSE_RAW_FILLED.md` + `BRANCH_C_PASS_CRITERIA_CHECKLIST_FILLED.md`
**Trigger**: GPT-5.5 external eval = **5/5 PASS** → Case S
**Renderer status**: Cycle 7 freeze 유지 (Cycle 8 안 함)

---

## 0. Decision

> **Branch C는 외부 readability eval에서 5/5 PASS로 통과했다. 따라서 configuration-dependent dynamics claim을 *external validation 받은 상태*로 lock한다. 단, single-seed 한정 caveat은 그대로 유지한다.**

---

## 1. PASS 결과 (verbatim from checklist)

| Criterion | Result | PASS? |
|---|---|:---:|
| Within-scenario divergence | 3/3 groups show ≥3 distinct outcomes | ✅ |
| Configuration sensitivity verdict | STRONG | ✅ |
| Q2a typing accuracy | 17/18 또는 18/18 (P_NEW_09 sacred vs none) | ✅ |
| Final summary self-call | 18/18 | ✅ |
| Q3b world-side axes | 4/5 majority (interpersonal 10 / group_alignment 14 / crowd_mood 18 / public_attention 14) | ✅ |

**5/5 PASS** = Case S = strong positive.

---

## 2. Locked claim (paper / public framing)

### 2.1 Approved claim

> "single-seed external readability eval supports configuration-sensitive outcome divergence; magnitude requires cross-seed confirmation."

### 2.2 Locked specifics

- **Within-scenario divergence**: 3/3 scenario groups (accusation / scarcity / sacred) show ≥3 distinct final-summary outcomes
- **Most explanatory dimension**: placement / cohort routing (primary), cast composition (secondary)
- **All 18 self-calls match headline labels**: 18/18 (perfect agreement on outcome class)
- **GPT-5.5 readability**: 18/18 readable, 18/18 CLEAR_FLOW, 18/18 CAN_EXPLAIN

### 2.3 NOT locked (existence vs magnitude separation)

- 67% sensitivity ratio (single-seed bias possible ±33pp per paper §7.4)
- Specific per-dimension ratios (S5 placement / S4 cast)
- Cross-seed modal stability (별도 5-seed ensemble로 측정 필요)

---

## 3. Public framing rules

### 3.1 Use

- "WITNESS는 configuration-sensitive narrative dynamics를 보이는 generative simulator다"
- "같은 scenario pressure가 cohort 배치 / cast 구성에 따라 다른 outcome class로 갈라진다"
- "external readability eval (GPT-5.5)이 within-scenario divergence를 detect함"

### 3.2 Avoid (CLAUDE.md ABSOLUTE Rule #5 + Lee directive §6 public framing)

- "predicts human behavior"
- "proves moral causality"
- "simulates real society"
- "AI sociology engine"
- "67% sensitivity" (single-seed magnitude)

---

## 4. Forbidden (Type E directive 유지)

- Renderer Cycle 8+
- Renderer 자율 rollback (별도 directive 필요)
- Branch C 새 slice / engine touch (현재 evidence 충분)
- Single-seed magnitude claim (cross-seed 없이)

---

## 5. Next actions (Case S 분기)

1. ✅ Branch C lock 명시 (이 doc)
2. **CREATIVE_ASSET_PACK_V1_PLAN.md** finalize → `docs/creative/`로 이동
3. **Observer real-run validation** 진행 (Lee directive `WITNESS_NEXT_STEP_OBSERVER_REAL_RUN_VALIDATION.md`)
4. Asset pack v1 candidate cleanup:
   - P6 MIXED scarcity (flagship)
   - P10 REC accusation
   - P_CV_01 MIXED accusation
   - Scarcity Trilogy (demo asset)
5. P9 SAT scarcity / P_PV_09 LOW_ACTIVITY = internal hold (manual edit only)

---

## 6. Caveat retained (verbatim from checklist §4)

> The external eval explicitly accepts the single-seed limitation:
> - It supports configuration dependence as existence evidence
> - It should not be used to claim the exact sensitivity magnitude
> - Any public or paper-facing claim should phrase this as:
>   **"single-seed external readability eval supports configuration-sensitive outcome divergence; magnitude requires cross-seed confirmation."**

---

## 7. Versioning

| Version | Date | Note |
|---|---|---|
| **v1 (this lock)** | **2026-04-30** | **Branch C external validation 5/5 PASS = Case S → lock + asset pack 진행** |
