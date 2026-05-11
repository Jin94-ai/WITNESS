# Branch C — D' Generalization Test Results

**Date:** 2026-04-28
**Source:** `BRANCH_C_S2_NONMONOTONIC_ANALYSIS.md` §4 D' refined hypothesis
**Test script:** `scripts/b_direction/test_d_prime_generalization.py`
**Status:** D' REJECTED — nonmonotonicity is scenario-specific.

---

## 1. Question

Does the 3-regime spacing pattern observed in scarcity (LOOP 70) generalize to accusation + sacred scenarios?

**Scarcity reference (LOOP 70)**:
- spread (t=5,40,100) → RECOVERY
- mild-cluster (t=5,7,10) → SATURATION
- very-cluster (t=5,6,7) → PARTIAL
- late-spread (t=100,140,180) → strongest RECOVERY

**D' (mechanism-level claim)**: oscillation-driven confession enables recovery. If true, should observe in accusation + sacred too.

**D' (scenario-specific null)**: scarcity has unique cohort/role structure that produces this pattern; other scenarios won't.

---

## 2. Test setup

- 4 spacing variants (spread / mild-cluster / very-cluster / late-spread)
- 2 scenarios tested (accusation, sacred)
- 8 probes total
- Same ticks as scarcity reference: spread=t5,40,100 / mild=t5,7,10 / very=t5,6,7 / late=t100,140,180
- For accusation: events are public_accusation against disciple_follower
- For sacred: events are miracle_witnessed (with 1 baseline accusation @ t50)

## 3. Results

### Accusation (4 spacings)

| Spacing | Outcome | n_conf | n_forg | final_mean |
|---|---|---:|---:|---:|
| spread       | SATURATION_DOMINATED | 63 | 31 | 1.99 |
| mild-cluster | PARTIAL              | 94 | 41 | 1.21 |
| very-cluster | SATURATION_DOMINATED | 57 | 30 | 2.34 |
| late-spread  | MIXED                | 59 | 28 | 3.60 |

→ **Accusation nonmonotonic in different way**: SAT/PARTIAL/SAT/MIXED. Spread → SAT (opposite of scarcity).

### Sacred (4 spacings)

| Spacing | Outcome | n_conf | n_forg | final_mean |
|---|---|---:|---:|---:|
| spread       | RECOVERY_DOMINATED | 35 | 27 | 0.10 |
| mild-cluster | RECOVERY_DOMINATED | 59 | 46 | 0.85 |
| very-cluster | RECOVERY_DOMINATED | 68 | 46 | 1.26 |
| late-spread  | PARTIAL            | 27 | 19 | 0.00 |

→ **Sacred is pressure-resistant**: 3/4 RECOVERY regardless of spacing. Miracle events drive awe, not shame, so scenario is tilted toward recovery.

## 4. Match comparison (vs scarcity baseline)

| Spacing | Scarcity | Accusation | Sacred | Match scarcity? |
|---|---|---|---|---|
| spread       | RECOVERY | **SATURATION** | RECOVERY | sacred ✓ / accusation ✗ |
| mild-cluster | SATURATION | PARTIAL | **RECOVERY** | both ✗ |
| very-cluster | PARTIAL | **SATURATION** | **RECOVERY** | both ✗ |
| late-spread  | RECOVERY | **MIXED** | **PARTIAL** | both ✗ |

**Scoreboard**: accusation 0/4 match, sacred 1/4 match. **D' REJECTED**.

---

## 5. Key findings

### Finding 1: Each scenario has its own spacing-outcome map

| Scenario | Spread bias | Saturation tendency | Comments |
|---|---|---|---|
| Scarcity | RECOVERY at spread/late-spread | mild-cluster only | 3-regime nonmonotonic |
| Accusation | SATURATION at spread/very-cluster | dominant | recovery breaks only at mild-cluster |
| Sacred | RECOVERY across most | very rare | high-awe protection |

→ **Spacing affects outcome differently per scenario**. No universal mechanism.

### Finding 2: Accusation has reverse-spread pattern

In scarcity, well-spread accusations enable recovery (via oscillation valleys).
In accusation, well-spread accusations cumulate (target=disciple_follower, location=priest_courtyard) → SATURATION.

**Why the difference?** In accusation scenario, the accusation events route blame to a *single target role* in a *single location* (priest_courtyard). Spread accusations let blame accumulate without dispersion. In scarcity, accusations target merchant in marketplace BUT with low-density crowd, blame dissipates between events.

→ **Accusation lacks the dissipation mechanism scarcity has at low density**.

### Finding 3: Sacred is pressure-resistant

Sacred scenario (with miracle events instead of accusations) recovers in 3/4 spacings. Only late-spread gives PARTIAL — and even then final_mean=0.00 (recovery from cap perspective).

**Why?** Miracle events drive awe (not shame), and awe + sacred environment + 1 baseline accusation @ t50 produces strong recovery dynamics. The scenario is tilted toward RECOVERY by construction.

### Finding 4: Mechanism is configuration-dependent at the scenario level

The "spacing → outcome" relationship is itself **scenario-specific**. This is a stronger claim than Branch C 1차 evidence: configuration sensitivity exists not just within scenarios (cast/placement/density variations), but **the dynamics-rule itself varies by scenario**.

→ This is consistent with master plan §4 ("broader world = more world-side observability"). The world layer has scenario-specific dynamics, not a single universal kernel.

---

## 6. Implications

### For KERNEL_GAPS Gap 4 (forgiveness uptake threshold)

Gap 4 was hypothesized to have a single threshold. Now revealed: threshold dynamics are scenario-specific. Cannot fix Gap 4 by adding a single rule — needs scenario-aware tuning.

### For Branch C activation predicate

Branch C 1차 evidence v3 should be updated:
- Configuration sensitivity exists across **5+ orthogonal dimensions** (cast × placement × density × event_count × scenario_dynamics)
- Scenario_dynamics is a **cross-scenario** dimension itself

### For external eval

GPT-5.5 blind eval would now have richer evidence: 36 probes (S2/S3/S4/S5) + 8 D' generalization probes = 44 total. But D' results are post-hoc analytical (not generated as standardized probes).

---

## 7. What this evidence does NOT prove (HARNESS H4)

- **NOT** proven: every scenario has unique dynamics — only 3 tested
- **NOT** proven: D' is scenario-specific *because* of scenario content — could be cast-density-content interaction
- **NOT** proven: "spread→SATURATION" in accusation generalizes to other accusation cast variants — only baseline cast tested

### What I did NOT try

- Test with N=4 spacings × 3 cast variants × 3 scenarios = 36 probes for full crossing
- Test with 4 accusations or 5 accusations (count-extension instead of just spacing)
- Test in cross-scenario hybrid (accusation + scarcity events mixed)

---

## 8. Falsification status

| Hypothesis | Status |
|---|---|
| A (forgiveness scales with events) | REJECTED (LOOP 70) |
| B (moral fatigue) | REJECTED (LOOP 70) |
| C (cohort propagation) | REJECTED (LOOP 70) |
| D (oscillation enables confession, scarcity-only) | SUPPORTED for scarcity (LOOP 70) |
| **D' (D generalizes to accusation+sacred)** | **REJECTED (this LOOP 72 test)** |

→ Status: scarcity has unique 3-regime spacing dynamics. Accusation and sacred have their own scenario-specific patterns.

## 9. New canonical claim

> **Branch C 1차 evidence reveals: scenario-specific dynamics-rules.** Same spacing input produces different outcomes per scenario. This is a stronger configuration-dependence claim than 1차 v2/v3 had: not just "outcomes vary per cast/placement", but "the cast/placement/spacing → outcome mapping itself varies per scenario".

This is consistent with the WITNESS hypothesis (cf. CLAUDE.md ABSOLUTE rule #5 "용어 과장 금지"): we can claim **structural isomorphism in engine** + **scenario-specific dynamics in content+world** without overclaiming universality.

---

## 10. Cross-seed re-test (LOOP 74) — D' rejection HOLDS at modal level

Per HARNESS H1 + LOOP 73 caveat: re-tested all 12 (scenario, spacing) cells with seeds 0-4. **60 total runs**.

### Modal outcomes (5-seed mode per cell)

| Spacing | Scarcity | Accusation | Sacred |
|---|---|---|---|
| spread       | RECOVERY (3/5) | **SATURATION (5/5)** | PARTIAL (4/5) |
| mild-cluster | SATURATION (3/5) | PARTIAL (2/5) | RECOVERY (4/5) |
| very-cluster | SATURATION (2/5) | SATURATION (2/5) | **RECOVERY (5/5)** |
| late-spread  | RECOVERY (3/5) | MIXED (3/5) | PARTIAL (4/5) |

### Key findings

1. **D' rejection HOLDS at modal level**: 3/4 spacings show 3 distinct modals across scenarios (only very-cluster has scarcity=accusation modal match, both at 2/5 weak modals). The scenario-specific dynamics claim survives.
2. **Scenario-locked patterns** (5/5 unanimous):
   - accusation/spread → SATURATION (5/5)
   - sacred/very-cluster → RECOVERY (5/5)
3. **Within-scenario seed variance is high**: most cells show 2-3/5 modal agreement. Only 2/12 cells are 5/5 unanimous. **Scarcity is most seed-sensitive** (3/5 modal in 3 cells, 2/5 in 1 cell). **Sacred is most seed-stable** (4/5 or 5/5 agreement in 3/4 cells).
4. **D' (mechanism-level claim) still REJECTED**: same spacing → different scenarios → different modals. Universal-mechanism hypothesis remains falsified.

### Revised verdict

**D' rejection: ROBUST at scenario-level**. Scenario-specific dynamics survive cross-seed test.

**Within-scenario seed-stability: WEAK**. Scarcity especially. This is a new HARNESS H4 caveat: "modal outcome ≠ deterministic outcome per (scenario, spacing)".

→ Canonical claim refinement: scenarios have **distinct distributional signatures**, not deterministic outcomes. Ensemble (5+ seed) characterization is required for reliable per-(scenario, spacing) claims.
