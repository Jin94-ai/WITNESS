# Iter 137 -- Cast Threshold Dominates Other Levers

**Date:** 2026-04-26
**Iteration:** Iter 137
**Severity:** LOW -- model validation finding

---

## 0. Summary

Tested whether space-affordance modulation (Iter 133 lever) can
rescue cast-threshold failure (Iter 117 V3, 0% recovery). **Result:
no meaningful rescue**. Cast threshold dominates other levers when
acting as a hard conjunctive bottleneck.

| Variant | Recovery rate |
|---|---:|
| V0 default (orig cast + 2 acc diff) | 0/15 (0%) |
| V1 low authority_reach (priest only) | 0/15 |
| V2 low authority_reach (both locations) | 1/15 (7%) |
| V3 high concealment (both) | 0/15 |
| V4 combined (low auth + high conceal) | 1/15 (7%) |

The 7% rescue in V2/V4 is within binomial CI noise [0%, 22%].

---

## 1. Mechanism

The predictive recovery model:
> recovery_rate ≈ baseline × ∏_{r ∈ accused_roles} P(role r forgiven)
>                × (1 - ambient_load) × space_modulation

When any P(role r forgiven) ≈ 0 (because cast < n=2 threshold), the
**∏ product is ≈ 0**. Other multiplicative factors can't rescue
this -- multiplying by anything against ~0 gives ~0.

In the orig cast (1 outsider), P(outsider forgiven) ≈ 0 because
single agent rarely confesses in time. Space modulation reduces
ambient pressure but doesn't change agent-level confess probability.

This is consistent with the structural model: **cast composition is
the conjunctive bottleneck**; other levers are modulators ON TOP of
that.

---

## 2. Implications

### 2.1 Lever hierarchy
The 6 design levers don't operate as equal modulators. There's a
hierarchy:
1. **Conjunctive (must satisfy)**: cast composition (n≥2 per accused role)
2. **Modulators (scale within conjunctive)**: pressure events,
   timing, space, memory layers, time horizon

If conjunctive condition fails → recovery ~0% regardless of modulators.
If conjunctive satisfied → modulators shift recovery rate within ~0-100%.

### 2.2 Branch C scenario design rule
**First**: ensure cast representation ≥2 per accused role.
**Then**: tune modulators (location, timing, etc.).

Reversing this order produces scenarios that look "designed for
recovery" but fail because conjunctive condition isn't met.

### 2.3 Updated predictive model (clarified)

> recovery_rate ≈ I[cast satisfies conjunctive] ×
>                 baseline × (1 - ambient_load) × space × time × memory
>
> Where I[...] is indicator function: 1 if all accused roles have
> ≥2 cast members, 0 (effectively) otherwise.

This is mathematically equivalent to the previous model but makes
the dominance structure explicit.

---

## 3. What could still be wrong (H4)

- N=15 binomial CI on 7% is [0%, 32%]; could be larger rescue with
  more seeds. Probably not, since 14/15 still saturate.
- Tested 4 location parameter combinations. Other combinations
  (cooperative location pairings, threshold parameters) might have
  different effect.
- The "rescue not possible" finding is conditional on:
  - Default cast (1 outsider)
  - 2-acc-diff-roles scenario
  - 500t horizon
- Different scenarios (sacred or scarcity) might show different
  cast × space interaction.
- 1/15 rescue is a real seed (not pure noise) -- there's some path
  by which space helps in 1 case. Could be amplified with the right
  combination.

---

## 4. What I did NOT try (H2)

- N=30 verification of 7% rescue
- Other rescue attempts (very low authority_reach 0.0,
  visibility=0.0, etc.) -- extreme parameter values
- Combine cast slight-augmentation (n=1.5 -- not physical) with
  space modulation
- Other lever combinations (timing × space, memory × space)
- Cross-scenario test of cast dominance

---

## 5. Connection to project direction

Lee's "world that flows" thesis is supported by this finding:
- The kernel produces a **structured dependency**: cast first,
  modulators second
- This is a real architectural property, not arbitrary
- Branch C designers can predict scenario behavior using the
  hierarchy

Score-tier impact: none. This iter validates existing model rather
than producing new tier estimates.

---

## 6. Conclusion

**Cast threshold dominates other levers**. When P(role r forgiven)
falls to ~0 (n=1 cast representation), other modulators can't
rescue meaningfully.

**6-lever framework refined into hierarchy**:
- Conjunctive: cast composition (must satisfy)
- Modulators: pressure, timing, space, memory, horizon (tune within)

**No code changes**, no architectural retractions. This iter
provides clean confirmation of the predictive model's mathematical
structure.

---

## 7. Note on diminishing returns

This iter's finding is "validate-existing", not "discover-new".
Previous productive iters (133, 134, 136) found new dimensions or
new mechanisms. Iter 137 confirms a logical implication of the
existing model.

The Iter 105-137 arc has now:
- Cleaned up measurement infrastructure (Iter 105-110)
- Built predictive model (Iter 111-119)
- Verified verification work (Iter 120-126)
- Found model limits (Iter 127, 130, 135)
- Probed unaddressed elements (Iter 133, 134)
- Self-corrected one mechanism (Iter 135)
- Refined model with new findings (Iter 136-137)

The investigation is reaching genuine saturation -- new probes mostly
verify existing claims rather than reveal new structure.
