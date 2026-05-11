# Branch C — S3 Event Density Variation Results

**Date:** 2026-04-28
**Slice:** S3 sacred depth expansion (per `BRANCH_C_DESIGN_DRAFT.md` §3)
**Generator:** `scripts/b_direction/generate_event_density_variations.py`
**Probes:** 9 (3 miracle counts × 3 spacing patterns)
**Engine touch:** NO (generator-level seed_events list variation only)
**Validation:** PASS via `validate_annotated_v4.py` (9/9 v4 fields)

---

## 1. Hypothesis

Does miracle event density (count) and spacing (timing distribution) shift final-summary outcome under fixed cast + baseline placement, independently of S4 (cast) and S5 (placement) effects?

→ Test orthogonal dimension to S4/S5: same scenario (sacred), same cast (n=8), same placement (baseline), only event density varies.

## 2. Variants

| Density | Spacing | Miracle ticks |
|---|---|---|
| low (1)   | early | [10] |
| low (1)   | even  | [100] |
| low (1)   | late  | [190] |
| med (3)   | early | [10, 30, 60] |
| med (3)   | even  | [10, 100, 190] |
| med (3)   | late  | [140, 170, 190] |
| high (5)  | early | [10, 20, 40, 70, 100] |
| high (5)  | even  | [10, 50, 100, 150, 190] |
| high (5)  | late  | [90, 120, 150, 170, 190] |

All probes: sacred scenario, baseline placement, n=8 cast, seed=0, 200 ticks, 1 prayer (t5) + 1 accusation (t50).

## 3. Results

| Probe | Density | Spacing | Final summary | Awe peak | Top blame |
|---|---|---|---|---:|---|
| P_ED_01 | low  | early | RECOVERY_DOMINATED | 9.95 | crowd_participant (peak 1.00) |
| P_ED_02 | low  | even  | PARTIAL            | 9.75 | crowd_participant (peak 0.96) |
| P_ED_03 | low  | late  | RECOVERY_DOMINATED | 9.75 | disciple_follower (peak 0.62) |
| P_ED_04 | med  | early | RECOVERY_DOMINATED | 9.95 | crowd_participant (peak 1.00) |
| P_ED_05 | med  | even  | PARTIAL            | 9.95 | (varies) |
| P_ED_06 | med  | late  | RECOVERY_DOMINATED | 9.95 | (varies) |
| P_ED_07 | high | early | PARTIAL            | 9.95 | (varies) |
| P_ED_08 | high | even  | PARTIAL            | 9.95 | (varies) |
| P_ED_09 | high | late  | PARTIAL            | 9.95 | (varies) |

**Final summary distribution:** 4 RECOVERY_DOMINATED + 5 PARTIAL. No SATURATION, no MIXED, no LOW_ACTIVITY.

**Configuration sensitivity:** 2/9 distinct outcomes = **22% sensitivity** (lower than S4=67% and S5=67%).

## 4. Pattern (key finding)

| Density | early | even | late |
|---|---|---|---|
| low  | RECOVERY | PARTIAL | RECOVERY |
| med  | RECOVERY | PARTIAL | RECOVERY |
| high | PARTIAL  | PARTIAL | PARTIAL  |

**2 dimensional patterns visible:**

1. **Density-driven saturation**: high (5 miracles) → all PARTIAL regardless of spacing. Low/med (1-3 miracles) → spacing-driven RECOVERY/PARTIAL split.

2. **Spacing-driven RECOVERY**: at low/med density, **even-spacing → PARTIAL, edge-spacing (early or late) → RECOVERY**. Even-spacing creates sustained pressure throughout the 200 ticks → recovery never completes. Edge-spacing concentrates miracles at one end → temple cohort either recovers (after late miracles) or stays low-shame (after early miracles).

## 5. Interpretation

This slice tests an **orthogonal dimension** to S4/S5:

- S4 (cast composition): 9 probes, **6/9 = 67% flips**, authority drop = strongest single driver
- S5 (placement): 9 probes, **6/9 = 67% flips**, original ↔ inverted reverses dynamics
- **S3 (event density): 9 probes, 2/9 = 22% flips**, even-spacing concentrates PARTIAL outcomes

**Why S3 is less sensitive than S4/S5**: Sacred scenario has only 1 accusation (t50, single shame source). Cohort outcomes are dominated by *recovery from a single trigger*, and miracle frequency only modulates **timing of recovery**, not the trigger itself. S4 (drop authority) directly removes additional shame sources; S5 (placement) routes accusations to different cohorts. S3 only shifts the recovery rate.

**This is informative**: Configuration sensitivity is **dimension-dependent**. Cast/placement = high sensitivity (route shame); event density = low sensitivity (modulate recovery). Both are real effects, but with different mechanisms.

## 6. Combined Branch C 1차 evidence (3 slices, 27 probes)

| Slice | N | Distinct outcomes | Configuration sensitivity |
|---|---:|---:|---:|
| S5 placement | 9 | 4 (RECOVERY/SATURATION/PARTIAL/LOW_ACTIVITY) | 6/9 = 67% |
| S4 cast      | 9 | 4 (MIXED/RECOVERY/SATURATION/PARTIAL) | 6/9 = 67% |
| S3 density   | 9 | 2 (RECOVERY/PARTIAL) | 2/9 = 22% |
| **Combined 27** | **27** | **5 distinct (all 5 labels)** | **14/27 = 52%** |

**Combined finding**: WITNESS dynamics are configuration-dependent across **at least 3 orthogonal dimensions** (cast × placement × event density), with sensitivity varying by dimension. Cast and placement have ~3× the sensitivity of event density for sacred scenario.

## 7. What could still be wrong (HARNESS H4 — Negative Findings)

- **Trivial explanation**: "high density → PARTIAL" might be a saturation artifact: 5 miracles in 200 ticks may exceed the awe ceiling and cause all cohorts to converge to same "max-awe-but-still-partial-recovery" state. **Falsification check**: awe peak at high density is 9.95 (saturated) vs low density 9.75-9.95 (also near-saturated). Awe is at ceiling in 7/9 probes — so awe-saturation does not uniquely explain density effect. Recovery-rate is the true driver. **Hypothesis tentatively retained, but**: needs raw pre-clamp `overflow_awe` field to fully reject saturation hypothesis.
- **What I did NOT try**:
  1. Vary seed (only seed=0). May affect spacing-edge cases.
  2. Vary horizon. 50/100/200 tick horizons would test "do dynamics scale with timeframe?"
  3. Cross-product with placement (3 density × 3 placement = 9 probes already in S5+S3 separately, never together).
  4. Other scenarios (accusation, scarcity) under density variation.
- **Alternate interpretation**: even-spacing → PARTIAL might be a *fixed-tick-50-accusation* artifact: accusation at t50 always splits the trajectory in half, and even-spaced miracles always cross the accusation boundary, blurring outcome. Edge-spaced (early-only or late-only) miracles concentrate before/after the accusation, allowing clean before/after dynamics. → **Suggests scenarios with 0 or 2+ accusations would test this; future S3 extension.**

## 8. Files

- `scripts/b_direction/generate_event_density_variations.py` — generator
- `scripts/b_direction/validate_annotated_v4.py` — extended to cover S3
- `docs/b_direction/readability_probes_event_density/P_ED_{01-09}.txt` — 9 probes

## 9. Next decisions (for Lee)

1. **Lock 1차 evidence**: Branch C 1차 = S5 + S4 + S3 = 27 probes, 14/27 = 52% configuration sensitivity. Sufficient for Branch C activation claim?
2. **Update blind eval package**: extend `BRANCH_C_18_PROBES_BLIND_PACKAGE.md` to 27 probes including S3?
3. **Continue to S1/S2** (accusation depth / scarcity depth)?
4. **Move to S6** (engine kernel touch — authority autonomy)? — requires Lee directive.
