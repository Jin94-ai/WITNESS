# Readability Pilot -- 4-Probe Subset (Original vs Annotated)

**Date:** 2026-04-26
**Status:** Pilot blind eval (per Step A2 directive)
**Purpose:** Lower the threshold for human evaluation from 1-2 hours to 15-20 minutes,
and isolate the **format axis** (original vs annotated) before committing to a
full 12-probe blind eval.

**Verbatim from directive (Lee, 2026-04-26)**:
> "Step C를 12개 full run 전, 4개 pilot blind로 축소 실행 가능한 형태로 준비"
> "원본 vs annotated readability 차이를 작게라도 검증할 수 있게 만들기"
> "인간이 1~2시간 대신 15~20분 안에 반응할 수 있도록 문턱 낮추기"

---

## 0. Quick start (for evaluator)

1. Read `docs/b_direction/READABILITY_BLIND_PROTOCOL.md` (or v2 when ready)
   for the Q1-Q6 question set.
2. Open the 4 pilot files in order:
   - `readability_pilot/PILOT_1_original.txt`
   - `readability_pilot/PILOT_2_original.txt`
   - `readability_pilot/PILOT_3_annotated.txt`
   - `readability_pilot/PILOT_4_annotated.txt`
3. For each, answer Q1-Q6. Aim for 3-5 minutes per probe (15-20 min total).
4. Record answers in `readability_pilot/PILOT_RESULTS_template.md` (see §4).
5. Send results back; do NOT view §3 (ground truth) until after answering.

---

## 1. Why 4 probes (not 12)?

The full 12-probe blind eval has been blocked because it requires 1-2 hours of
focused human reading. This pilot reduces that to ~15-20 minutes by:

- **4 probes instead of 12**: still covers 3 scenarios + 1 structural variant
- **Mixed format**: 2 original + 2 annotated (lets us see if format helps)
- **Same protocol**: Q1-Q6 unchanged

If pilot signal is clear (e.g., annotated probes get higher Q1 readable rate),
the full 12-probe eval can be skipped or repurposed. If signal is ambiguous,
the full eval is still needed.

---

## 2. Selection rationale

| Pilot file | Source | Scenario | Variant | Format | Why selected |
|---|---|---|---|---|---|
| PILOT_1_original.txt | P10 | accusation | baseline (seed=0) | original | Most-studied scenario, baseline kernel state |
| PILOT_2_original.txt | P9 | scarcity | baseline (seed=0) | original | Different domain, baseline kernel state |
| PILOT_3_annotated.txt | P4 | sacred | baseline (seed=0) | annotated | Third scenario domain, annotated to test format |
| PILOT_4_annotated.txt | P3 | accusation | p2a_off (seed=0) | annotated | Recovery-blocked variant, annotated |

### Coverage analysis
- **Scenarios**: 3 (accusation x2, scarcity x1, sacred x1) -- all 3 covered
- **Variants**: 3 baselines + 1 p2a_off (recovery-blocked) -- structural axis tested
- **Seeds**: all seed=0 -- intentional (cleanest comparison; seed variance not the
  axis of this pilot)
- **Format split**: 2 original + 2 annotated

### Cross-axis comparisons enabled
- **Format on accusation**: PILOT_1 (original baseline) vs PILOT_4 (annotated p2a_off)
- **Format across scenarios**: PILOT_1+2 (originals: accusation, scarcity) vs
  PILOT_3+4 (annotated: sacred, accusation)
- **Mechanism axis (within annotated)**: PILOT_3 (sacred baseline) vs PILOT_4
  (accusation p2a_off) — does annotation help reader detect mechanism difference?

### What this pilot does NOT cover
- **Within-scenario format comparison**: no probe pair from the same
  (scenario, seed, variant) shown in both original and annotated form. This
  was avoided because seeing the same data twice in different formats would
  contaminate the second read. If needed, expand to 6-probe pilot.
- **Seed variance**: only seed=0. Probes P11 (accusation seed=3) and P2
  (scarcity seed=2) are excluded.
- **Sham_mul variants**: P1 (scarcity sham_mul_0.8), P7 (sacred sham_mul_0.05)
  excluded.

---

## 3. Ground truth (DO NOT READ until after answering)

<details>
<summary>Click to reveal (only after answering Q1-Q6 for all 4 probes)</summary>

| Pilot file | Source P-index | Scenario | Seed | Variant | p2a status |
|---|---|---|---|---|---|
| PILOT_1_original.txt | P10 | accusation | 0 | baseline | enabled |
| PILOT_2_original.txt | P9 | scarcity | 0 | baseline | enabled |
| PILOT_3_annotated.txt | P4 | sacred | 0 | baseline | enabled |
| PILOT_4_annotated.txt | P3 | accusation | 0 | p2a_off | **disabled** |

### Expected dynamics (from prior internal analysis)
- **PILOT_1 (accusation baseline)**: forgiveness rumor recovery active; partial
  recovery on accused cohort, no shame on outsider cohort
- **PILOT_2 (scarcity baseline)**: scarcity-driven shame accumulation, recovery
  via forgiveness rumor; mixed cohort outcomes
- **PILOT_3 (sacred baseline)**: sacred-tagged events; lower shame velocity;
  decorative-suspect (per pending B3 work)
- **PILOT_4 (accusation p2a_off)**: forgiveness rumor disabled → recovery
  channel blocked → expected saturation in accused cohort

</details>

---

## 4. Results template (for evaluator to fill out)

Save to `readability_pilot/PILOT_RESULTS.md`:

```markdown
# Readability Pilot Results

**Evaluator:** [name]
**Date:** [yyyy-mm-dd]
**Time spent:** [minutes]

## Per-probe answers

### PILOT_1 (original format)
- Q1 (readable?): [yes/partial/no]
- Q1b (confidence 1-5):
- Q2 (dominant pressure):
- Q3 (cohort/group dynamics):
- Q4 (arc type):
- Q5 (oscillation):
- Q6 (confusion notes):

### PILOT_2 (original format)
[same template]

### PILOT_3 (annotated format)
[same template]

### PILOT_4 (annotated format)
[same template]

## Cross-probe observations

- Did annotated probes feel easier to read? Yes/No/Mixed:
- Format vs scenario: did format change your answers?:
- Where did you spend the most time?:
- Q-set issues: any question unclear or missing?:

## Time budget actual vs target

| Phase | Target | Actual |
|---|---|---|
| Reading | 12-16 min | |
| Writing answers | 3-4 min | |
| Total | 15-20 min | |
```

---

## 5. Branch decision rule (per Step C result mapping)

Per directive §8, after pilot results:

| Outcome | Action |
|---|---|
| Annotated readability >> original (e.g., 3-4 / 4 readable on annotated, ≤1 / 4 on original) | **Branch A confirmed**, full 12-probe eval optional. Strengthen presentation. |
| Annotated ≈ original (similar readable rate) | Format does not help; **structure is the bottleneck**. Branch B simplification gains priority. |
| Both formats unreadable | **Branch B strong**, kernel may need restructure or recovery diversification (post-shame_decay decision K1). |
| Both formats readable | **Branch C ready**, world-side process is externally legible. |

These thresholds use 4-probe granularity (≤1, 2-3, ≥4) so 1 probe shift can
change the verdict. Treat pilot as **noisy hint**, not final answer.

---

## 6. What this pilot does NOT decide (H4)

- **Final branch decision**: pilot is a hint with N=4. Statistical confidence
  is low. Full 12-probe eval may still be needed even with strong pilot signal.
- **Q-set adequacy**: if Q1-Q6 are themselves wrong, no probe set fixes that.
  V2 Q-set (Step A3, next iter) addresses this separately.
- **Multiple-evaluator variance**: pilot is presumably 1 evaluator. Different
  evaluators may give different answers; pilot doesn't measure inter-rater
  agreement.
- **Probe selection bias**: I (assistant) chose the 4 probes. Different
  selection might yield different signal. The §2 selection rationale is
  defensible but not unique.

---

## 7. Files

```
docs/b_direction/READABILITY_PILOT_4.md           ← this doc
docs/b_direction/readability_pilot/
  PILOT_1_original.txt    (P10: accusation baseline)
  PILOT_2_original.txt    (P9: scarcity baseline)
  PILOT_3_annotated.txt   (P4: sacred baseline)
  PILOT_4_annotated.txt   (P3: accusation p2a_off)
```

---

## 8. Next steps (after pilot results)

1. Lee runs pilot in 15-20 min, fills `PILOT_RESULTS.md`
2. Compare to ground truth (§3)
3. Apply §5 branch decision rule
4. Decide:
   - Run full 12-probe eval? (skip if pilot signal is strong + clear)
   - Revise Q-set? (if multiple Q6 confusion notes converge on protocol issue)
   - Revise annotated format? (if PILOT_3+4 annotation does not help)
