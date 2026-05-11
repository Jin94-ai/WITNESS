# Branch C — S2 Nonmonotonicity Analysis

**Date:** 2026-04-28
**Source:** `BRANCH_C_S2_RESULTS.md` §5 + §9 — investigate triple->RECOVERY nonmonotonicity.

## 1. Per-probe metrics

| Events | Density | n_acc | n_conf | n_confessors | cohorts_w_conf | n_forg | shame_peak | final_mean |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| single | low | 1 | 116 | 11 | 3/3 | 79 | 10.00 | 0.64 |
| single | baseline | 1 | 69 | 10 | 3/3 | 52 | 10.00 | 3.58 |
| single | high | 1 | 69 | 10 | 3/3 | 52 | 10.00 | 3.58 |
| double | low | 2 | 71 | 10 | 3/3 | 52 | 10.00 | 3.58 |
| double | baseline | 2 | 71 | 10 | 3/3 | 52 | 10.00 | 3.58 |
| double | high | 2 | 71 | 10 | 3/3 | 52 | 10.00 | 3.58 |
| triple | low | 3 | 115 | 11 | 3/3 | 81 | 10.00 | 1.37 |
| triple | baseline | 3 | 115 | 11 | 3/3 | 81 | 10.00 | 1.37 |
| triple | high | 3 | 115 | 11 | 3/3 | 81 | 10.00 | 1.37 |

## 2. Aggregate by event count (averaged across densities)

| Events | mean n_conf | mean n_forg | mean cohorts_w_conf | mean final_shame |
|---|---:|---:|---:|---:|
| single | 84.7 | 61.0 | 3.0 | 2.60 |
| double | 71.0 | 52.0 | 3.0 | 3.58 |
| triple | 115.0 | 81.0 | 3.0 | 1.37 |

## 3. Hypothesis test (HARNESS H1 — falsification)

### Hypothesis A: forgiveness cascade scales with event count

**Prediction**: n_forgiveness monotonic in event count (1 < 2 < 3).

**If A true**: triple has more forgiveness emissions, drives recovery.
**If A false**: forgiveness flat or peaks at 2 -> hypothesis rejected.

### Hypothesis B: moral fatigue

**Prediction**: confession count plateaus or decreases at triple (cohorts stop responding).

**If B true**: triple has fewer confessions than double.
**If B false**: confessions increase or stay similar -> hypothesis rejected.

### Hypothesis C: cohort propagation

**Prediction**: cohorts_with_confessions monotonic in event count.

**If C true**: triple has more cohorts with confessions than double.
**If C false**: cohorts plateau -> hypothesis rejected.

## 4. Verdict

### Hypothesis A — REJECTED in linear form, MODIFIED form survives

n_forgiveness across event counts:
- single mean: 61 (with single/low at 79, single/baseline+high at 52)
- double mean: 52
- triple mean: 81

→ **Not monotonic in event count**. Double has FEWER forgiveness than single. Triple jumps to highest.

But: at single/low density (LOW crowd density), forgiveness=79 — same level as triple. So "single can also reach high forgiveness if density permits".

### Hypothesis B — REJECTED

n_confessions:
- single mean: 84.7
- double: 71.0
- triple: 115.0

→ Triple has MOST confessions (not fewer). Moral fatigue at triple is **falsified**.

### Hypothesis C — REJECTED

cohorts_with_confessions = 3/3 in **every probe**. No variation; does not explain outcome difference.

### NEW Hypothesis D (emerges from data) — Shame oscillation enables confession

Pattern observed:
| Probe class | n_conf | n_forg | final_mean | Outcome |
|---|---:|---:|---:|---|
| single/low (low density)        | 116 | 79 | 0.64 | RECOVERY |
| single/baseline+high            |  69 | 52 | 3.58 | SATURATION |
| double/all                      |  71 | 52 | 3.58 | SATURATION |
| triple/all                      | 115 | 81 | 1.37 | RECOVERY |

**Recovery threshold appears to be**: n_conf ≥ 80 AND n_forg ≥ 60.

**Mechanism (D)**: Confessions fire most efficiently when shame OSCILLATES (rising/falling) rather than saturated at cap.

- Single accusation @ t=5 + baseline/high density: shame spikes to cap (10) and stays stuck — 195 ticks of cap-state → only ~69 confessions.
- Single + low density: lower density means slower propagation, so shame stays oscillating longer → 116 confessions.
- Double @ t=5, t=40 (close-spaced): two spikes too close, no recovery valley between → 71 conf (same as single/baseline).
- Triple @ t=5, t=40, t=100 (well-spaced t=100 gap): 3 oscillation cycles in 200 ticks → 115 conf.

**Implication**: scarcity SATURATION is **spacing-dependent, not just count-dependent**. Three accusations close together would NOT trigger triple's recovery effect.

**Test of D**: re-run triple with accusations clustered at t=5,7,10 → predict SATURATION (because no spacing for oscillation).

### Falsification path for D

If clustered-triple → SATURATION (not RECOVERY), D is supported.
If clustered-triple → RECOVERY, D is rejected; some other event-count mechanism dominates.

### D test results (LOOP 70 followup, `test_hypothesis_d_clustered_triple.py`)

| Variant | Ticks | n_conf | n_forg | final_mean | Outcome |
|---|---|---:|---:|---:|---|
| spread       | t=5, 40, 100  | 115 | 81  | 1.37 | RECOVERY |
| clustered    | t=5, 7, 10    | 63  | 39  | 3.58 | **SATURATION** |
| very-clustered | t=5, 6, 7   | 106 | 74  | 1.84 | PARTIAL |
| late-spread  | t=100, 140, 180 | 215 | 156 | 0.97 | RECOVERY (strongest) |

**D PARTIALLY supported, with refinement**:

- **mild-cluster (gap 2-5 ticks) → SATURATION** (matches D prediction)
- **very-cluster (gap 1 tick) → PARTIAL, not SATURATION** (D refinement needed)
- **wide-spread → RECOVERY** (matches D)
- **late-spread → STRONGEST recovery** (215 conf — even more than spread baseline)

→ **Spacing has 3 regimes, not 2**. Very-tight clustering (consecutive ticks) gets *more* confessions than mild clustering — possibly because all agents flip simultaneously and confess in unison later. Mild clustering spreads the trigger over too few agents per tick.

→ Late-spread (events 100+ ticks into 200-tick horizon) gives strongest recovery — the system has time after the last event for recovery dynamics to dominate.

**Refined hypothesis D'**: scarcity recovery depends on **time-after-last-event** AND **spacing of triggers**. Cap-stuck saturation occurs only in narrow "mild-clustered" regime. Both very-tight and well-spread clustering allow recovery via different mechanisms.

## 5. Implication for KERNEL_GAPS Gap 4

Gap 4 (forgiveness uptake threshold): this analysis reveals the threshold is **shame-state-dependent**, not raw-count-dependent. Specifically, confessions fire most when shame is **above threshold but below cap**.

→ Update KERNEL_GAPS Gap 4 with: "uptake threshold has dynamic dependence on shame oscillation pattern; cap-stuck states suppress uptake."

## 6. What this analysis does NOT prove (HARNESS H4)

- D not yet directly tested — needs clustered-triple variant
- "shame oscillation enables confession" is post-hoc — could be other dynamics (recovery cooldown, social cascade timing) producing same pattern
- Other scenarios (accusation, sacred) not tested for same nonmonotonicity

### What I did NOT try

- Time-series plot of shame trajectory per probe (would directly show oscillation pattern)
- Per-cohort confession timing
- Different timing patterns at triple count (clustered vs evenly-spread)
- Re-test in accusation/sacred scenarios

## 7. Action items

1. (autonomous, next LOOP) Run clustered-triple variant to test hypothesis D
2. (autonomous) Document hypothesis D in KERNEL_GAPS as Gap 4 refinement
3. (Lee gate) Decide whether to pursue Gap 4 further or move to S1/lock 1차

---

## 8. Seed robustness check (LOOP 73 followup) — CRITICAL UPDATE

Per HARNESS H1 + H4: "seed=0 only" was a known untested limitation. Testing seeds 0-4 reveals:

| Event count | RECOVERY | SATURATION | other |
|---|---:|---:|---:|
| single   | 2/5 | 2/5 | 1/5 (PARTIAL) |
| double   | 2/5 | 3/5 | 0/5 |
| **triple** | **3/5** | **2/5** | **0/5** |

→ Triple→RECOVERY is **NOT 3/3**. It's 3/5 across seeds. **D is only partially seed-robust.**

**Implications**:

1. **The S2 finding "triple → RECOVERY 3/3" was a seed=0 artifact masked as a 3/3 pattern**. Real rate is 3/5 = 60% (still nonmonotonic but weaker).
2. **D hypothesis is partially weakened**: oscillation-driven recovery happens in 60% of triple cases, not 100%.
3. **D' rejection (LOOP 72)** also seed=0-only — needs cross-seed re-test to confirm scenario-specific dynamics.

### Revised D verdict

D = **PARTIALLY SUPPORTED, seed-modulated**. Spread events trigger recovery in majority of seeds (3/5 = 60%) but a saturated path exists (2/5 = 40%). The mechanism (oscillation-enabled confession) is real but not deterministic.

### What I did NOT try (continuing H4)

- Seed 5-9 (10-seed test instead of 5)
- Cross-seed variance for accusation/sacred D' generalization
- Statistical test (binomial: 3/5 vs null 2.5/5 — not significant at any reasonable α)