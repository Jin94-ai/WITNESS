# Branch C — S2 Scarcity Depth Results

**Date:** 2026-04-28
**Slice:** S2 scarcity depth expansion (per `BRANCH_C_DESIGN_DRAFT.md` §3, executed per `BRANCH_C_S2_DESIGN_PLAN.md`)
**Generator:** `scripts/b_direction/generate_scarcity_depth_variations.py`
**Probes:** 9 (3 event counts × 3 crowd densities)
**Engine touch:** NO (generator-level seed_events list + CrowdState density variation only)

---

## 1. Hypothesis under test

Does scarcity SATURATION outcome depend on (event count × crowd density), with each dimension independently flipping outcome?

→ Test S2 dimension orthogonal to S3/S4/S5: same scenario (scarcity), same cast (n=12), same placement (S5 original baseline), only event count + crowd density vary.

## 2. Variants

| Probe | Events | marketplace density | poor_quarter density |
|---|---|---:|---:|
| P_S2_01 | 1 accusation (t5)         | 0.3 | 0.2 |
| P_S2_02 | 1 accusation (t5)         | 0.7 | 0.5 (baseline) |
| P_S2_03 | 1 accusation (t5)         | 0.9 | 0.8 |
| P_S2_04 | 2 accusations (t5, t40)   | 0.3 | 0.2 |
| P_S2_05 | 2 accusations (t5, t40)   | 0.7 | 0.5 |
| P_S2_06 | 2 accusations (t5, t40)   | 0.9 | 0.8 |
| P_S2_07 | 3 accusations (t5, t40, t100) | 0.3 | 0.2 |
| P_S2_08 | 3 accusations (t5, t40, t100) | 0.7 | 0.5 |
| P_S2_09 | 3 accusations (t5, t40, t100) | 0.9 | 0.8 |

All include guard_approaches @ t15 + 1 misdeed rumor.

## 3. Results

| Probe | Events | Density | Final summary | Failure mode |
|---|---|---|---|---|
| P_S2_01 | single | low      | RECOVERY_DOMINATED | - |
| P_S2_02 | single | baseline | SATURATION_DOMINATED | shame_cap |
| P_S2_03 | single | high     | SATURATION_DOMINATED | shame_cap |
| P_S2_04 | double | low      | SATURATION_DOMINATED | shame_cap |
| P_S2_05 | double | baseline | SATURATION_DOMINATED | shame_cap |
| P_S2_06 | double | high     | SATURATION_DOMINATED | shame_cap |
| P_S2_07 | triple | low      | RECOVERY_DOMINATED | - |
| P_S2_08 | triple | baseline | RECOVERY_DOMINATED | - |
| P_S2_09 | triple | high     | RECOVERY_DOMINATED | - |

**Configuration sensitivity vs baseline (single/baseline = SATURATION)**: 4/9 = **44% flip rate**.

## 4. Pattern (nonmonotonic — UNEXPECTED)

| Events | low | baseline | high |
|---|---|---|---|
| single | RECOVERY | SATURATION | SATURATION |
| double | SATURATION | SATURATION | SATURATION |
| **triple** | **RECOVERY** | **RECOVERY** | **RECOVERY** |

**Striking finding**: more accusations does NOT lead to deeper saturation. Instead, **triple accusations → RECOVERY across all densities**. This is *nonmonotonic* — single causes saturation, double sustains it, triple **breaks out of saturation**.

Predicted outcome was: more events → deeper saturation. **Prediction broken**.

## 5. Hypothesis for nonmonotonicity (HARNESS H1 — falsification candidate)

**Trivial explanation A**: Each `public_accusation` event triggers a delayed `forgiveness_emitted` cascade. With 1 accusation, only 1 cascade — partial response. With 3 accusations spread across 100 ticks (last at t=100), the cascade has 100 more ticks to drive shame decay, exceeding saturation.

**Trivial explanation B**: Triple accusations exceed a "moral fatigue" threshold where cohorts stop responding to accusations entirely → shame stops accumulating → final_mean drops below 4 → RECOVERY classification.

**Trivial explanation C**: Cohort dynamics: with 3 accusations, more cohorts get exposed → more confessions emitted → more forgiveness rumors → propagation reaches saturated cohorts.

**Falsification check**: confessions + forgiveness counts per probe should distinguish A/B/C.

→ **What I did NOT try (yet)**: extract raw confession count + forgiveness count per probe and compare. Quick follow-up possible.

## 6. Cross-density signal (single accusation case)

For single accusation (3 probes):
- low (0.3, 0.2) → RECOVERY
- baseline (0.7, 0.5) → SATURATION
- high (0.9, 0.8) → SATURATION

**Density matters at single-accusation regime**: 0.3-density crowds don't propagate blame/shame strongly enough to reach saturation. ≥0.7 density → saturation.

For double + triple, density doesn't matter (3/3 saturation in double, 3/3 recovery in triple). **Density signal is masked by event count**.

## 7. Interpretation

S2 reveals: **scarcity dynamics are nonmonotonic in event count**. Two distinct regimes:

1. **Low-event regime (1-2 accusations)**: density-modulated saturation. Low density → recovery, high density → saturation.
2. **High-event regime (3+ accusations)**: density-independent recovery. The system "saturates and recovers" — possibly because the forgiveness response cascades exceed shame accumulation.

This is consistent with KERNEL_GAPS Gap 4 ("forgiveness mechanism uptake threshold"): forgiveness has uptake-modulating thresholds that may fire only after sufficient repeat triggers.

**Important**: this nonmonotonic pattern was NOT predicted by S5/S4 — only S2's event-count variation could surface it.

## 8. Combined Branch C 1차 evidence (4 slices, 36 probes)

| Slice | N | Distinct outcomes | Configuration sensitivity |
|---|---:|---:|---:|
| S5 placement | 9 | 4 | 6/9 = 67% |
| S4 cast      | 9 | 4 | 6/9 = 67% |
| S3 density   | 9 | 2 | 2/9 = 22% |
| S2 scarcity depth | 9 | 2 | 4/9 = 44% |
| **Combined 36** | **36** | **5 distinct** | **18/36 = 50%** |

→ Per-dimension sensitivity: 67% / 67% / 22% / 44%. **Mean: 50%**.

→ Branch C activation predicate met across **4 orthogonal dimensions**.

## 9. What this evidence does NOT prove (HARNESS H4)

- **NOT** proven: nonmonotonic event-count effect generalizes to accusation/sacred scenarios — only scarcity tested
- **NOT** proven: nonmonotonicity is forgiveness-cascade-driven (3 candidate explanations, none ruled out)
- **NOT** proven: density signal masking is real (could be P_S2_04 outlier)
- **NOT** proven: "triple → RECOVERY" holds with different accusation timings (only t5,t40,t100 tested)

### 9.1 What I did NOT try

- **Quad accusations** (4+) — would reveal if monotonicity returns at higher counts
- **Extract confession + forgiveness counts** per probe to distinguish hypotheses A/B/C in §5
- **Repeat with sacred or accusation scenario** for nonmonotonicity generalization
- **Vary timing** (e.g., 3 accusations clustered at t5,10,15 vs spread t5,100,180)

## 10. Files

- `scripts/b_direction/generate_scarcity_depth_variations.py` — generator
- `scripts/b_direction/validate_annotated_v4.py` — needs S2 extension
- `docs/b_direction/readability_probes_scarcity_depth/P_S2_{01-09}.txt` — 9 probes
- `BRANCH_C_S2_DESIGN_PLAN.md` — pre-execution plan

## 11. Next decisions

1. **Extend validate_annotated_v4 to cover S2** (mechanical, autonomous)
2. **Investigate nonmonotonicity** — extract confession/forgiveness counts → test hypotheses A/B/C
3. **Update FIRST_EVIDENCE_SUMMARY** to v3 (36 probes)
4. **Lee gate**: lock 1차 OR continue S1 (accusation depth)
