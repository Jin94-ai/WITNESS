# Lee Gate — Branch C 1차 Evidence Status (post-cross-seed walkback)

**Date:** 2026-04-28
**Status:** Saturation reached, autonomous progression complete. Lee directive needed.
**Source:** 26 LOOPs of autonomous Branch C work (LOOP 51-76).

---

## 1. What's done

### Branch C PREP (LOOP 51-58)
- Tasks 1-4 complete: scope/criteria, world-side observables (7), acceptance test (6+5 questions), design draft (6 first-slice candidates).

### Branch C 1차 EVIDENCE (LOOP 59-69)
- 4 mechanical execution slices: S5 placement / S4 cast / S3 event density / S2 scarcity depth.
- 48 validated annotated probes (12 baseline + 36 new).
- v4 spec adds Top blame target (Q3b interpersonal axis surfacing).
- Generator-only changes; engine touch = 0; pytest 1500 PASS.

### Hypothesis cycle (LOOP 70-72)
- S2 nonmonotonic finding: triple→RECOVERY (seed=0).
- 3 hypotheses (A/B/C) tested + rejected.
- Hypothesis D proposed (oscillation enables confession).
- D' generalization test → REJECTED (scenario-specific dynamics).

### Cross-seed walkback (LOOP 73-76) — CRITICAL self-falsification
- HARNESS H1 self-audit: all evidence used seed=0 only.
- 5-seed ensemble re-test of all 4 slices (180 runs total).
- Findings: per-dimension sensitivity ratios shifted ±33pp from seed=0 estimates.

---

## 2. What's robust (claims surviving cross-seed test)

| Claim | Evidence | Robustness |
|---|---|---|
| WITNESS dynamics are configuration-dependent | 4 within-scenario slices, 3 dimensions show ≥44% ensemble sensitivity | STRONG |
| Scenarios have distinct distributional signatures (D' rejected) | 12-cell × 5-seed test, 3/4 spacings distinct modals | STRONG |
| Cast variation is most ensemble-robust dimension | S4 56% sensitivity (smallest seed-delta) | STRONG |
| Sacred/clustered → LOW_ACTIVITY 5/5 unanimous | LOOP 75 | STRONG |
| Accusation/spread → SATURATION 5/5 unanimous | LOOP 74 | STRONG |
| Sacred/very-cluster → RECOVERY 5/5 unanimous | LOOP 74 | STRONG |
| Top blame target deterministic per scenario (scarcity 100% fisher_laborer) | LOOP 64 | STRONG |
| Q2a-typing 100% across 36 probes | configuration-invariant | STRONG |

## 3. What's been walked back

| Original claim | Cross-seed reality | Delta |
|---|---|---:|
| Per-dim sensitivity 67%/67%/22%/44% | Cross-seed 44%/56%/44%/11% | mean -11pp |
| Mean configuration sensitivity 50% | Mean 39% | -11pp |
| S2 nonmonotonicity (triple→RECOVERY 3/3) | 3/5 across seeds — seed-modulated | weak |
| S2 scarcity depth as 44%-sensitive dimension | 11% — least sensitive | -33pp |
| 36 probes give "configuration-dependent" claim deterministically | All snapshots are seed=0; ensemble shows distributional signatures only | qualitative |

## 4. Open gates for Lee decision

### (a) Lock 1차 evidence with v4.4 (cross-seed ensemble) claim?

Updated canonical claim:
> "WITNESS dynamics show scenario-specific distributional signatures over outcome space, with per-dimension configuration sensitivity averaging ~39% (S4 56%, S5 44%, S3 44%, S2 11%) under 5-seed ensemble. Modal outcomes are scenario-discriminative for 2/12 (scenario, spacing) cells (5/5 unanimous), with most cells showing 2-3 distinct outcomes per 5 seeds."

**Pros**: Empirically grounded, ensemble-validated. Conservative. Aligns with HARNESS H1.
**Cons**: Less rhetorically strong than v3 (50% sensitivity vs 39%). May be insufficient for "Branch C activation" claim if rhetoric was the goal.

### (b) Continue S1 (5th mechanical slice — accusation depth)?

Master plan §3 lists S1 = accusation cast variation N=15. Per current findings, this is likely incremental (S4 already covered cast variation cross-scenario). **Claude bias: skip — overlapping with S4**.

### (c) Send 36 probes to GPT-5.5 with **explicit seed=0 disclosure**?

The original BLIND_PACKAGE (LOOP 63) was prepared as 18 probes. Now have 36 + cross-seed ensemble data. Need:
- Update package: 36 probes + ensemble disclaimer + cross-seed table
- Or: send 18 probes with note "additional 18 since added"

**Risk**: If GPT-5.5 reads "configuration sensitivity 67%" without ensemble caveat, will reach overstrong conclusion.

### (d) S6 engine touch (authority autonomy KERNEL_GAPS Gap 6)?

Forbidden in autonomous mode. Master plan §4 listed as engine kernel change.

If pursued: implement authority decay in `engine/world/factions.py` or similar to make authority autonomous (per Iter 38 ablation). Predict effect on saturation rate.

### (e) Investigate S2 seed-artifact reduction mechanism?

S2 dropped 44% → 11% under ensemble. Why? Most likely cause: scarcity scenario has high cohort-density-driven shame variance, where small seed differences cascade into different cohort outcomes. Mechanism investigation could identify a "seed-stable" S2 protocol (e.g., averaging shame cap thresholds across cohorts).

**Value**: Would convert S2 from 11%-sensitive (noisy) to 30-40%-sensitive (controllable). High research value, but requires generator changes.

---

## 5. Recommended Lee decision pattern

Given autonomous saturation, the **strongest lever Lee has** is one of:

1. **Lock + send to GPT-5.5 with full disclosure** (option c). Generates external validation.
2. **Authorize S6 engine touch** (option d). Highest research value but irreversible engine change.
3. **Stop Branch C, return to v0.6 paper draft**. Fold cross-seed findings into paper.

Other options ((a) lock alone, (b) S1, (e) S2 mechanism) are incremental.

## 6. Files for Lee review

| Doc | Purpose |
|---|---|
| `BRANCH_C_FIRST_EVIDENCE_SUMMARY.md` (v4.4) | Top-level summary, ensemble-corrected |
| `BRANCH_C_CROSS_SEED_ENSEMBLE_RESULTS.md` | Per-cell modal outcomes, 180 runs |
| `BRANCH_C_D_PRIME_GENERALIZATION_RESULTS.md` (with §10 cross-seed) | Scenario-specific dynamics evidence |
| `BRANCH_C_S2_NONMONOTONIC_ANALYSIS.md` (with §8 caveat) | Hypothesis cycle, seed-robustness caveat |
| `LEE_GATE_2026-04-28_BRANCH_C.md` (this) | Decision package |

## 7. Bias disclosure (HARNESS H6)

I bias toward (1) lock + send to GPT-5.5 with disclosure. Reasons:
- Cross-seed walkback is the most important methodological finding of this Branch C cycle.
- External validation against the *corrected* claim is more valuable than against the seed=0 inflated claim.
- Lee can assess whether GPT-5.5's reading aligns with ensemble-corrected expectations.

But options (2) and (3) are equally valid — all 3 are strong moves. (4) and (5) are smaller-scope follow-ups.

## 8. Next autonomous action (default if no Lee directive)

Per lessons L26 (consolidation trap): autonomous mode should now **stop adding probes / re-running tests / refining docs**. Saturation reached.

Possible autonomous-safe non-saturating work:
- Update v0.6 paper draft with Branch C findings (Methods §, Results §)
- Refine HARNESS docs based on L13 (seed=0 conditioning lesson)
- Cleanup orphan analysis scripts in `scripts/b_direction/`

If LOOP 78+ continues without Lee gate, will pivot to v0.6 paper draft update.
