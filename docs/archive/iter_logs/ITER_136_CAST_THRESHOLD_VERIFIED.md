# Iter 136 -- Cast Threshold Verified Without Rumor + Sweet Spot Refinement

**Date:** 2026-04-26
**Iteration:** Iter 136
**Severity:** MEDIUM -- main finding verified + refinement

---

## 0. Summary

Tested whether Iter 117-119 cast threshold finding (n=1: 0%, n=2:
100% recovery) was rumor-confounded. **Result: primary finding
robust without rumor**. But n=3 no-rumor reveals **sweet spot
behavior**: more outsiders past n=2 paradoxically reduces reliability.

| n outsiders | With rumor | No rumor |
|---:|---:|---:|
| 1 | 0% | 0% |
| 2 | **100%** | **100%** |
| 3 | 93% | 73% |

---

## 1. Iter 119 finding survives N=15 + no-rumor verification

The dominant claim "n=1: ~0%, n=2: ~100% recovery" holds in BOTH
rumor and no-rumor conditions. Cast threshold mechanism is
**rumor-independent at the threshold itself**.

This is the strongest empirical anchor of the entire arc, now
confirmed via removal of one possible confound.

---

## 2. New finding: n=2 sweet spot, not "n≥2 plateau"

At n=3:
- With rumor: 93% (close to n=2's 100%)
- Without rumor: 73% (substantially below n=2)

This is a sweet-spot pattern. Pre-Iter-136 framing assumed
P(role r forgiven) → 1 for n≥2. Iter 136 shows degradation past
n=2:
- n=2: maximally reliable (100%)
- n=3 with rumor: rumor compensates for over-representation
- n=3 without rumor: 4/15 seeds fail

### Why n=3 might be less reliable

Cast at n=3 outsiders: agents 10, 07, 08 are outsiders. Agents 01-03
are disciples (3). The remaining cast: agent_06 is the ONLY
crowd_participant (08 was reassigned to outsider).

Compared to n=2 cast: 2 outsiders (10, 07), 2 crowd_participants (06, 08).

Hypothesis: crowd_participants serve a stabilizing role:
- They populate city_street crowd
- Reassigning them to outsider concentrates outsider-targeted shame
- This may distort the natural recovery pattern

Without rumor's pre-staging of disciple-side dynamics, the n=3
imbalance produces failure in some seeds.

---

## 3. Refined predictive model

Pre-Iter-136 (Iter 119):
> P(role r forgiven) ≈ 1 if cast has ≥2 role-r agents

Post-Iter-136:
> P(role r forgiven) function:
>   - n=1: ≈ 0 (single agent unreliable)
>   - n=2: ≈ 1 (optimal)
>   - n=3+: ≈ 0.7-1 (slightly degraded; rumor stabilizes)
>   - Trade-off: more role-r agents means fewer of OTHER roles,
>     which may matter for stability

The model is non-monotonic in n, with peak at n=2.

This is a small refinement. Lee's Branch C scenario design
implication: **don't over-represent any single role**. Match cast
size to scenario role coverage with minimal margin.

---

## 4. The rumor's role (refined again)

Iter 134 framing: rumor amplifies recovery (later corrected Iter 135).
Iter 135 framing: rumor INTERFERES with cascade.
Iter 136 finding: rumor STABILIZES n=3 cast (93% with vs 73% without).

So rumor is multi-faceted:
- In standard cast: rumor + delayed accusation HURTS recovery (Iter 134-135)
- In over-represented cast (n=3): rumor STABILIZES recovery (Iter 136)
- In standard cast + early accusation: rumor slightly HURTS (Iter 135 V0 53% vs V1 60%)

Rumor effect direction depends on cast composition × event timing.
Not a simple amplifier or interferer.

---

## 5. Updated 6 design levers (post Iter 134-136)

1. Cast composition (Iter 100/118-119/136 -- n=2 sweet spot)
2. Pressure events
3. Time horizon
4. Memory layers including rumor (Iter 122-123, 135-136 -- multi-effect)
5. Location parameters (Iter 133)
6. Event timing relative to memory state (Iter 134, 135 corrected)

---

## 6. What could still be wrong (H4)

- N=15 binomial CI on 73% is [44%, 92%]; on 93% is [70%, 99%]. CI
  partial overlap; the 20% drop might be smaller (10-12%) or larger
  (25-30%) under tighter measurement.
- Tested only n=1, 2, 3. Smooth interpolation might show different
  shape (e.g., n=2.5 not testable but maybe peak is between 2 and 3).
- The n=3 cast modification reduces crowd_participants from 3 to 1.
  This conflates "outsider count" with "crowd_participant count".
  Pure outsider-count effect not isolated.
- Hypothesis "crowd_participants stabilize" is post-hoc; not directly
  tested by ablating crowd_participants while keeping outsider count.
- "Rumor multi-effect" framing is post-hoc rationalization of three
  different observations. Could be that rumor has a single mechanism
  that produces different surface effects depending on context.

---

## 7. What I did NOT try (H2)

- N=30 verification of n=3 no-rumor 73%
- n=4, n=5 outsider counts (test if degradation continues)
- Total cast size variation (8 agents vs 12 vs 15)
- Pure crowd_participant ablation while keeping outsider count
- Cross-scenario (sacred + 2-acc) at varied cast
- Direct probe of crowd_participant role function

---

## 8. Conclusion

**The Iter 119 cast threshold finding survives no-rumor
verification at the n=1→n=2 transition** (0%→100% in both
rumor and no-rumor conditions).

**New finding**: cast representation has a sweet spot at n=2,
not a plateau. n=3 with reduced crowd_participants is less
reliable without rumor's stabilizing effect.

**Updated model**: P(role r forgiven) is non-monotonic in cast
representation, peaking at n=2.

**Branch C design implication**: minimal-sufficient role
representation is optimal. Over-representing any single role can
reduce overall recovery reliability.

**No engine changes**, no architectural retractions. Pure
refinement of an established finding via direct verification.
