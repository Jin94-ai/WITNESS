# WITNESS Creative Asset Pack v1

**Date**: 2026-04-30
**Status**: Internal curated pack (Branch C Case S 후 first asset bundling)
**Source**: `docs/creative/CREATIVE_ASSET_PACK_V1_PLAN.md` (Lee directive 후속)
**Renderer**: Cycle 7 freeze 유지

---

## 0. 무엇인가

WITNESS는 *narrative dynamics experiment*다. 같은 사회적/도덕적 압력이 *configuration* (cohort 배치 + cast 구성)에 따라 다른 outcome class로 갈라지는지 실험한다.

이 pack은 그 *configuration-sensitive divergence*를 한국어 narrative 형태로 보여주는 *first curated bundle*이다.

---

## 1. 무엇이 *아닌가*

다음과 같은 주장은 **하지 않는다**:
- "predicts human behavior"
- "proves moral causality"
- "simulates real society"
- "AI sociology engine"

이는 CLAUDE.md ABSOLUTE Rule #5 (terminology 과장 금지) 일관.

---

## 2. 검증 근거

### 2.1 External eval (GPT-5.5)

`docs/b_direction/BRANCH_C_GPT55_RESPONSE_RAW_FILLED.md`:
- 18 probes blind eval — 18/18 readable, 18/18 self-call match
- Within-scenario divergence: 3/3 groups show ≥3 distinct outcomes
- Configuration sensitivity verdict: STRONG
- Most explanatory dimension: placement / cohort routing (primary), cast composition (secondary)

### 2.2 Internal real-run validation

`docs/observer/REAL_RUN_VALIDATION.md`:
- peter_scarcity_baseline canonical (200 ticks, 12 agents, 3 groups)
- 3 seeds compare → 2 distinct final moods (seed_1: calm / seed_0,2: tense)
- Lee directive §6 success criteria 6/6 충족

### 2.3 Locked claim

> "single-seed external readability eval supports configuration-sensitive outcome divergence; magnitude requires cross-seed confirmation."

NOT locked: 67% sensitivity ratio, per-dimension specific magnitudes (single-seed bias possible ±33pp).

---

## 3. Pack 구조

| File | Role |
|---|---|
| `00_README.md` | 이 doc — pack 전체 소개 |
| `01_flagship_mixed_scarcity.md` | P6 — flagship narrative (cohort split) |
| `02_recovery_accusation.md` | P10 — recovery contrast |
| `03_mixed_accusation_configuration.md` | P_CV_01 — configuration-dependence explainer |
| `04_scarcity_trilogy_modal.md` | Trilogy 3-act — nonmonotonic dynamics |
| `appendix_method_caveat.md` | Single-seed limitation 상세 |
| `internal_hold/` | Public 아님, internal reference |
| ├── `p9_sat_scarcity_needs_manual_edit.md` | Manual edit 후보 |
| └── `p_pv_09_low_activity_reference.md` | LOW_ACTIVITY 참조 |

---

## 4. 읽기 순서

### 4.1 처음 보는 사람
1. 이 README (소개 + 검증 근거)
2. `01_flagship_mixed_scarcity.md` (P6 — 가장 강한 split outcome)
3. `04_scarcity_trilogy_modal.md` (Trilogy — high-level dynamics 설명)
4. `appendix_method_caveat.md` (한계 명시)

### 4.2 Configuration sensitivity 직접 보고 싶을 때
1. `02_recovery_accusation.md` (P10 — accusation 후 recovery)
2. `03_mixed_accusation_configuration.md` (P_CV_01 — same accusation pressure but different cohort outcome)

비교 시 핵심 질문: *같은 "accusation" pressure인데 왜 outcome이 다른가*?

### 4.3 한계 + 향후
1. `appendix_method_caveat.md`
2. `internal_hold/` (개선 검토 자료)

---

## 5. 사용 시 framing 권장

### 5.1 Use phrases

- "narrative dynamics experiment"
- "configuration-sensitive narrative dynamics"
- "generative simulator"
- "scenario pressure × cohort routing → outcome class divergence"

### 5.2 Avoid phrases

- "predicts" / "proves" / "simulates real society"
- "AI sociology engine"
- "67% sensitivity" (single-seed magnitude)

---

## 6. 다음 단계

이 v1 pack은 *internal curated*. Public release 여부는 Lee 검토 후 결정.

가능한 다음 단계:
- (Lee 검토) public-facing 버전 (caveat 강화 + 영문 mirror)
- 5-seed cross-seed validation으로 sensitivity magnitude 확정
- 추가 anchor (다른 scenario) 포함한 v2 pack

---

## 7. Versioning

| Version | Date | Note |
|---|---|---|
| **v1 (this pack)** | **2026-04-30** | **Branch C Case S 후 first internal curated bundle** |
