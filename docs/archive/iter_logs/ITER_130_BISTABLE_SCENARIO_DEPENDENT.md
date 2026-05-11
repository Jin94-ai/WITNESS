# Iter 130 -- Bistability is Scenario-Dependent, Not Universal

**Date:** 2026-04-26
**Iteration:** Iter 130
**Severity:** MEDIUM -- generalization finding (refines Iter 129 claim)

---

## 0. Summary

Tested whether Iter 129's bistable kernel finding generalizes to
sacred and scarcity scenarios. **Result: bistability is scenario-
dependent, not universal**.

| Scenario | Equilibrium structure | Finals at 1000t |
|---|---|---|
| Accusation (Iter 129) | **BISTABLE** | high (10.0) or low (3.33) cluster |
| Sacred standalone | **BISTABLE** | [10.0, 0.16, 10.0, 2.52, 0.48] |
| Scarcity | **MONOSTABLE-HIGH** | [10.0, 10.0, 10.0, 10.0, 10.0] |

This **refines Iter 129's claim**: the kernel has bistable structure
in accusation and sacred scenarios but monostable (single high
equilibrium) in scarcity.

---

## 1. Per-scenario interpretation

### 1.1 Sacred (BISTABLE confirmed)
3 seeds recover to <3, 2 seeds saturate to 10.0. The bistable
structure visible in Iter 107-119 holds at 1000t. Recovery is
seed-dependent (which equilibrium is reached), not gradually
modulated.

### 1.2 Scarcity (MONOSTABLE-HIGH)
ALL 5 seeds saturate to 10.0. No recovery basin reached at 1000t.
This matches Iter 112's finding (scarcity 0% recovery rate at 500t)
and extends it: even at 2x horizon, recovery is unattainable.

Why scarcity is monostable:
- scarcity_pressure event continuously generates blame (per Iter 123:
  blame_total active 87% of horizon)
- public_suspicion accumulates (63% nonzero in scarcity per Iter 123)
- Forgiveness rumor activity exists (19% of horizon) but is dwarfed
  by ongoing pressure
- Net: blame generation > forgiveness reduction → permanent saturation

This is consistent with the Iter 117-119 conjunctive model breaking
down here: P(recovery) is determined not just by role coverage but
also by net pressure-vs-recovery balance, which scarcity tilts
toward saturation.

### 1.3 Accusation (BISTABLE per Iter 129)
Cast composition determines basin: ≥2 agents per accused role →
forgiveness floor; <2 agents → saturation.

---

## 2. Refined kernel-structure claim

Pre-Iter-130 (per Iter 129):
> The kernel is bistable.

Post-Iter-130:
> The kernel is bistable in accusation/sacred contexts and monostable
> in scarcity. Bistability requires balance between pressure
> generation and forgiveness reduction; scarcity tilts toward
> ongoing pressure that overwhelms the recovery channel.

This is a real structural property of the kernel: **scenario topology
varies**.

---

## 3. Implications for Branch C scenario design

### Three scenario classes (from Iter 130 + earlier work)
1. **Bistable scenarios** (accusation, sacred): seed-dependent or
   cast-dependent basin selection produces dichotomous outcomes
2. **Monostable scenarios** (scarcity): deterministic saturation;
   no recovery achievable in current parameters

### Implication
Branch C scenario library will have at least 2 topology types.
Designers should know which they're producing:
- Bistable: useful for narrative -- different seed produces
  different arc (recovery vs saturation)
- Monostable: useful for endpoint scenarios where saturation
  is the intended dynamic

### Honest acknowledgment
The "world that flows" thesis works in bistable contexts but
becomes "world that saturates" in scarcity. This isn't a kernel
flaw -- it's reflecting the scenario design (scarcity has no
recovery mechanism by design).

---

## 4. What could still be wrong (H4)

- N=5 seeds × 1 condition per scenario. Could be small-N artifact.
  N=15 verification would tighten classification.
- Tested only specific scenario implementations. Different sacred
  configs (no late miracle) might be monostable too.
- Scarcity might have bistable behavior at much longer horizon
  (5000t+) or with different parameters.
- "Bistable" classification used heuristic (high>7 AND low<5,
  no mid). Edge cases might be missed.
- Single-seed per condition lacks within-condition variance check.

---

## 5. What I did NOT try (H2)

- N=15 verification of sacred bistability
- Scarcity at 5000t (extreme horizon)
- Mixed scenarios at 1000t (their topology untested)
- Parameter sweeps to find scarcity bistability threshold
- Augmented-cast scarcity (does increasing cast help?)
- Forgiveness rumor strength in scarcity (could amplifying
  forgiveness rescue scarcity from monostability?)

---

## 6. Connection to project direction

WORLD_BUILDING_ELEMENTS §4 stages: criteria for Stage B included
"여러 process가 서로 영향을 주며 독립적으로 움직임" and Stage C
adds readability + memory residue.

Iter 130 finding: the kernel produces qualitatively different
scenario topologies (bistable vs monostable). This is a DEEPER
property of "world flow" than my earlier framing suggested:
- Some scenarios have multiple stable end-states (bistable)
- Some scenarios have single forced end-state (monostable)
- Designers can choose which to produce

This is consistent with Lee's bifurcation theme: bistable scenarios
are the bifurcation-ready ones.

---

## 7. Conclusion

**Bistability is scenario-dependent**. Accusation and sacred have
bistable kernel structure; scarcity has monostable-high (saturation)
structure.

**Iter 129's "kernel is bistable" claim refined**: it's bistable
where pressure-recovery balance allows; monostable where pressure
dominates.

**Branch C scenario design has TWO topology classes** to choose
from. This is itself a design lever -- choosing scenario type
determines whether outcomes are dichotomous or deterministic.

**No code changes**, no architectural retractions. Pure structural
refinement of the kernel's behavioral repertoire.

---

## 8. Note on probe limits

After 26 iterations of empirical work (Iter 105-130), I'm reaching
diminishing returns on new findings. Each iter produces incremental
refinements but the core picture (predictive recovery model,
bistability where pressure permits, scenario-dependent dynamics)
is now stable.

Further probes would mostly verify-or-refine existing claims at
N=15 (instead of N=5) or extend horizons (to 5000t etc). These
would strengthen confidence but not produce qualitatively new
findings.

The empirical investigation has reached natural saturation.
