# Branch C — First Evidence Summary (S5 + S4 + S3 + S2 + D', v4)

**Date:** 2026-04-28
**Source slices:**
- `BRANCH_C_S5_RESULTS.md` (placement variation, 9 probes — LOOP 59)
- `BRANCH_C_S4_RESULTS.md` (cast composition, 9 probes — LOOP 60)
- `BRANCH_C_S3_RESULTS.md` (sacred event density, 9 probes — LOOP 67)
- `BRANCH_C_S2_RESULTS.md` (scarcity depth, 9 probes — LOOP 69)
- `BRANCH_C_S2_NONMONOTONIC_ANALYSIS.md` (hypothesis D test — LOOP 70)
- `BRANCH_C_D_PRIME_GENERALIZATION_RESULTS.md` (D' rejection — LOOP 72)
- `ANNOTATED_V4_TOP_BLAME_FINDINGS.md` (v4 interpersonal axis — LOOP 64)
**Status:** Provisional. Lee directive needed for (a) stop + lock / (b) continue S1 / (c) external eval / (d) S6 engine touch.

---

## 1. What Branch C 1차 evidence claims (v4.2 — refined)

> **WITNESS dynamics are configuration-dependent at two levels: (a) within-scenario seed-modulated outcome distributions and (b) cross-scenario distributional signatures. Same spacing input produces different modal outcomes per scenario (D' REJECTED at modal level, LOOP 72+74), but seed variance within (scenario, spacing) cells is non-negligible.**

This is a *more nuanced* claim than v3-v4.1 had. Master plan §4 ("broader world = more world-side observability") is empirically supported with two distinct evidence types:

1. **Within-scenario configuration sensitivity** (S5/S4/S3/S2): per-dimension 67%/67%/22%/44% **at seed=0**. Cross-seed: ±20-30% variability.
2. **Cross-scenario dynamics-rule heterogeneity** (D' cross-seed): scenarios have distinct **modal outcome distributions** under same spacing input. 2/12 cells unanimous (5/5 seeds agree), 10/12 cells modal 2-4/5.

→ Cannot reduce world dynamics to a single universal mechanism. Each scenario carries its own **distributional signature**, but individual runs are seed-modulated.

---

## 2. Combined results (36 new probes)

### 2.1 Final-summary distribution

| Source | RECOVERY | SATURATION | MIXED | PARTIAL | LOW_ACTIVITY |
|---|---:|---:|---:|---:|---:|
| Baseline P1-P12 | 4 | 4 | 3 | 1 | 0 |
| S5 placement (9) | 3 | 3 | 1 | 1 | 1 |
| S4 cast (9) | 6 | 1 | 2 | 1 | 0 |
| S3 event density (9) | 4 | 0 | 0 | 5 | 0 |
| S2 scarcity depth (9) | 4 | 5 | 0 | 0 | 0 |
| **Combined 36 new** | **17** | **9** | **3** | **7** | **1** |

→ All 5 final-summary labels appear in 36-probe set. RECOVERY most common (17/36 = 47%).

### 2.2 Configuration sensitivity ratio (per dimension)

**Seed=0-only (legacy claim, v3-v4.2)**:
| Slice | Probes flipping baseline outcome | Ratio (seed=0) |
|---|---:|---|
| S5 placement | 6/9 | 67% |
| S4 cast composition | 6/9 | 67% |
| S3 event density | 2/9 | 22% |
| S2 scarcity depth | 4/9 | 44% |
| Combined 36 | 18/36 | 50% |

**Cross-seed ensemble (v4.4 measured claim, LOOP 75-76)**:
| Slice | Modal flips vs baseline | Ratio (5-seed ensemble) | Delta vs seed=0 |
|---|---:|---:|---:|
| S5 placement | 4/9 | 44.4% | -22.6pp |
| S4 cast composition | 5/9 | 55.6% | -11.4pp |
| S3 event density | 4/9 | 44.4% | **+22.4pp (INCREASE)** |
| S2 scarcity depth | 1/9 | 11.1% | **-32.9pp (HUGE DROP)** |
| **Mean** | | **38.9%** | -11.1pp |

→ Per-dimension ranking changes dramatically under ensemble:
- **Cast (S4)** stays moderate-high (56%) — most ensemble-robust
- **Placement (S5)** moderate (44%) — placement effects partially seed-conditional
- **Event density (S3)** moderate (44%) — INCREASED, seed=0 underestimated
- **Scarcity depth (S2)** very low (11%) — nonmonotonicity nearly disappears under ensemble

→ **S2 nonmonotonicity (LOOP 69 finding) is largely a seed=0 artifact**. Single/density variation modal: SAT 2/5 / SAT 2/5 / REC 4/5. Triple modal: REC 4/5 (low) / REC 3/5 / REC 3/5. Most flips are at single/low only.

→ **S3 has 4/9 unanimous cells** (most stable). Sacred/high-density cells consistently PARTIAL across seeds.

### 2.3 Detection robustness (v2.1)

| Slice | Q2a-typing | Match GT |
|---|---:|---|
| Baseline 12 | 12/12 | 100% |
| S5 (9) | 9/9 | 100% |
| S4 (9) | 9/9 | 100% |
| S3 (9) | 9/9 | 100% |
| S2 (9) | 9/9 | 100% |
| **Combined 36 new** | **36/36** | **100%** |

→ v2.1 detection is **configuration-invariant across all 4 dimensions**.

### 2.4 World-side observability (v3 + v4)

All 48 probes (12 baseline + 36 new) surface 4 v3/v4 fields:
- Crowd blame total (Q3b crowd_mood)
- Public suspicion (Q3b public_attention) — v3
- Authority vigilance (Q3b authority) — v3
- Top blame target (Q3b interpersonal) — v4

Validation: `validate_annotated_v4.py` 48/48 PASS.

---

## 3. Specific findings to lock as canonical

### 3.1 Authority is the strongest single saturation driver (S4 evidence)

drop authority → RECOVERY 3/3 across scenarios (accusation MIXED→RECOVERY, scarcity SATURATION→RECOVERY, sacred PARTIAL→RECOVERY).

### 3.2 Placement reverses dynamics (S5 evidence)

3/3 reversals via placement inversion: accusation/scarcity/sacred all flip RECOVERY ↔ SATURATION when locations swap.

### 3.3 LOW_ACTIVITY only via sacred placement clustering (S5 evidence)

1/48 = 2.1% rate. Real but rare discriminator.

### 3.4 Event density saturates outcome at high count (S3 evidence)

high (5 miracles) → all PARTIAL regardless of spacing.
low/med + edge-spacing → RECOVERY. even-spacing → PARTIAL.

### 3.5 Top blame target deterministic per scenario (v4 evidence)

scarcity = fisher_laborer 100%. accusation = crowd_participant 82%. sacred = disciple_follower 70%.

### 3.6 Scarcity event count is **nonmonotonic** (S2 evidence — NEW)

This is the most striking finding of LOOP 67-70:

| Event count | Outcome | Confessions |
|---|---|---:|
| single (1, t5) | density-modulated SAT/REC | 69-116 |
| double (2, t5,40) | SATURATION 3/3 | 71 |
| **triple (3, t5,40,100)** | **RECOVERY 3/3** | **115** |

**Interpretation**: scarcity SATURATION is not an "event count escalation" effect. Instead, **3-regime spacing dynamics**:

- mild-cluster (gap 2-5): SATURATION (cap-stuck, fewer confession opportunities)
- very-cluster (gap 1, consecutive): PARTIAL (all-at-once trigger, unison confession)
- spread (gap ≥30): RECOVERY (oscillation-driven confession)
- late-spread (events 100+ ticks in): STRONGEST RECOVERY (215 conf)

Validates KERNEL_GAPS Gap 4 refinement: forgiveness uptake threshold has **dynamic dependence on shame oscillation pattern**, not just raw event count.

---

## 4. Branch C activation predicate (per master plan §10)

| Predicate condition | Status |
|---|---|
| Configuration sensitivity demonstrated | ✓ 18/36 = 50% across 4 dimensions |
| Q2a-typing 36/36 maintained | ✓ |
| World-side observables (Q3b) intact | ✓ all 36 surface v3+v4, 4/5 axes covered |
| Engine touch | ✗ (NO across S2/S3/S4/S5) |
| Forbidden_now violations | ✗ (NONE) |
| Nonmonotonic dynamics surfaced | ✓ NEW — S2 reveals 3-regime spacing |

→ **Branch C 1차 evidence sufficient + extended with mechanism-level finding**.

---

## 5. What this evidence does NOT prove (HARNESS H4)

- **NOT** proven: S2 nonmonotonicity generalizes to accusation/sacred — only scarcity tested
- **NOT** proven: external evaluator (GPT-5.5) reads same way — Claude generated, no blind eval yet
- **NOT** proven: 200-tick horizon is sufficient — long-horizon (>200) coupling unknown
- **NOT** proven: hypothesis D' (oscillation-driven confession) is the *only* mechanism — alternates not tested
- **NOT** proven: configuration sensitivity holds for cross-product variants — only single-dimension slices tested

### 5.1 What I did NOT try

- **Cross-product variants**: cast × placement × density × event_count combined
- **Other scenarios under S2 design**: only scarcity tested for nonmonotonicity
- **Seed variation**: all probes use seed=0 (Q2a-robust per S5/S4 but seed=0 may have specific path-dependence)
- **Longer horizons**: 500/1000 tick probes
- **S1 (accusation depth)** — last remaining mechanical slice; per master plan would test cast composition variation N=15 in accusation only
- **S6 (engine touch — authority autonomy)**: forbidden without Lee directive

### 5.2 Alternate interpretations

- **50% combined sensitivity dilutes per-dimension signal**: per-dimension reporting is more informative (67%/67%/22%/44%)
- **Nonmonotonicity could be sample-size artifact**: 9 probes per slice is small. Larger N could reveal it as 2-regime not 3-regime.
- **High-density PARTIAL bias in S3 might be ceiling artifact**: 5 miracles = awe ceiling reached → cohorts converge; needs `overflow_awe` field for full rejection.

---

## 6. Recommended next step (Claude bias, autonomous-mode)

| Option | What | When to take |
|---|---|---|
| **(a)** Stop, lock 1차 at 36 probes | Mark this v3 as canonical | If Lee considers 36 probes sufficient |
| **(b)** Continue S1 (accusation depth) | Last remaining mechanical slice | If Lee wants 5-dimension coverage |
| **(c)** External eval on 36 probes | Update blind package, send to GPT-5.5 | If Lee wants blind validation |
| **(d)** S6 (engine touch — authority autonomy) | Requires Lee directive | Forbidden in autonomous mode |
| **(e)** Test D' generalization in accusation/sacred | Run analogous nonmonotonic test on other scenarios | If Lee wants mechanism-level confirmation |

**Claude bias** (revised after S2 nonmonotonicity finding): **(a) lock at 36** OR **(e) test D' in accusation**.

Reasons:
- 36 probes covers 4 orthogonal dimensions, 5 distinct outcomes, surfaces nonmonotonic mechanism.
- (b) S1 would mostly overlap with S4 (cast variation in accusation).
- (e) tests whether nonmonotonicity is scarcity-specific or general.
- (c) requires Lee to send to GPT-5.5 (HUMAN_GATE).

---

## 7. Open questions for Lee

> **Branch C 1차 evidence 36 probes 충분한가? 다음 단계?**
> (a) 1차 lock → Branch C EXECUTION 다음 directive 대기
> (b) S1 accusation depth 추가 → 45 probes 5-dimension coverage
> (c) GPT-5.5 blind eval (36-probe extended package update 필요)
> (d) S6 engine touch — Lee 명시 directive 필요
> (e) Test D' (oscillation hypothesis) in accusation/sacred

---

## 8. Versioning

| Version | Date | Note |
|---|---|---|
| v1 | 2026-04-28 | First evidence summary post S5+S4 18 probes. Configuration sensitivity 67%. |
| v2 | 2026-04-28 | Extended to 27 probes (added S3 event density + v4 top_blame_target). Per-dimension 67%/67%/22%. |
| v3 | 2026-04-28 | Extended to 36 probes (added S2 scarcity depth + nonmonotonicity analysis). Per-dimension 67%/67%/22%/44%. NEW: 3-regime spacing finding. |
| v4 | 2026-04-28 | Added D' generalization test (8 probes accusation+sacred). D' REJECTED — accusation 0/4, sacred 1/4 match scarcity baseline. NEW canonical claim: scenario-specific dynamics-rules. |
| v4.1 | 2026-04-28 | CRITICAL CAVEAT (LOOP 73): all findings used seed=0 only. Triple→RECOVERY is 3/5 across seeds, not 3/3. Per-dimension sensitivity 67%/67%/22%/44% is seed=0-conditional. |
| v4.2 | 2026-04-28 | D' cross-seed re-test (LOOP 74): 60 runs. D' rejection ROBUST at modal level. Refined claim: distributional signatures, not deterministic outcomes. |
| v4.3 | 2026-04-28 | S5 cross-seed re-test (LOOP 75): 45 runs. S5 sensitivity drops 67% → 44%. |
| v4.4 (this) | 2026-04-28 | **All-slices cross-seed re-test (LOOP 76)**: 135 runs across S4/S3/S2. **Surprising findings**: S4 67%→55.6% (-11pp), S3 **22%→44.4% (+22pp INCREASE)**, S2 44%→11.1% (-33pp HUGE drop). Mean ensemble 39% (vs seed=0 mean 50%). Per-dimension cross-seed: 44%/56%/44%/11% (S5/S4/S3/S2). S2 nonmonotonicity nearly disappears under ensemble (single→SAT for 4/5 high-density seeds, triple→REC 3/5 — borderline). S3 has 4/9 unanimous cells (most ensemble-stable). |
