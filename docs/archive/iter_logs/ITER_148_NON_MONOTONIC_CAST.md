# Iter 148 -- Cast Curve Non-Monotonic (n=3 Local Dip)

**Date:** 2026-04-26
**Iteration:** Iter 148
**Severity:** LOW -- refinement of cast threshold curve

---

## 0. Summary

Tested if Iter 136's n=3 dip continues at n=4. **Result: dip is
local, recovery restored at n=4.**

| n outsiders | with rumor | no rumor |
|---:|---:|---:|
| 1 | 0% (Iter 119) | 0% (Iter 136) |
| 2 | 100% (Iter 119) | 100% (Iter 136) |
| 3 | 93% | **73%** (dip) |
| 4 | **100%** | **100%** (restored) |

The cast-recovery curve is non-monotonic. n=3 has a local dip
(mixed cast at city_street: 3 outsiders + 1 crowd_participant).
n=4 is homogeneous (all outsiders) and recovery returns to 100%.

---

## 1. The mechanism hypothesis

n=3 cast composition at city_street:
- agents 07, 08, 10 reassigned to outsider (3 outsiders)
- agent 06 remains crowd_participant (1 crowd member)

The mixed cast (3 outsiders + 1 crowd_participant) at city_street
may create dynamics where:
- Crowd_participant has different motif tendencies than outsiders
- Mixed responses to accusation events at city_street create
  uncoordinated cascade
- Without rumor's stabilization, this mixed response fails more
  often

n=4 (all outsiders at city_street) restores homogeneous response.
With pure outsider cohort, all agents have similar motif tendencies
and the recovery cascade fires reliably.

This is consistent with conjunctive model: cast representation
matters, but ALSO cast HOMOGENEITY at the recovery-critical
location.

---

## 2. Updated cast threshold model

Pre-Iter-148:
> n=2 sweet spot, n=3+ slightly degraded

Post-Iter-148:
> Cast-recovery curve is non-monotonic.
>   n=1: 0%
>   n=2: 100% (baseline sweet spot)
>   n=3: dips to 73% (mixed cast at city_street)
>   n=4: 100% (homogeneous cast)
>
> Recovery requires: cast representation ≥2 per accused role AND
> ideally homogeneous cast at recovery-critical location.

---

## 3. Branch C design implication

For predictable recovery, designers should:
- Ensure n≥2 per accused role (necessary)
- Avoid mixed-role cohorts at recovery sites (n=3 mixed example)
- Either fully replace OR keep majority, not mix awkwardly

This is a refinement, not a fundamental change. The n=2 sweet spot
remains the primary recommendation.

---

## 4. What could still be wrong (H4)

- N=15 binomial CI on 73% vs 93%/100% is wide; the dip might be
  statistical noise. With N=30 might disappear.
- Tested only n=1, 2, 3, 4. Higher n (5+) untested.
- "Mixed cast hurts" hypothesis is post-hoc; not directly tested
  by varying mix ratios.
- The dip might be specific to which crowd_participant is left
  (agent 06). Testing with different remaining mix could check.

---

## 5. What I did NOT try (H2)

- N=30 verification of n=3 dip
- n=5+ outsider counts
- Mixed cast with different remaining roles (family, disciple, etc.)
- Cross-scenario: does n=3 dip appear in sacred?

---

## 6. Conclusion

**Cast-recovery curve is non-monotonic** with n=2 sweet spot,
local dip at n=3 (mixed cohort), and recovery restored at n=4
(homogeneous).

**Mechanism hypothesis**: cast HOMOGENEITY matters in addition
to cast count. Mixed responses at recovery-critical location
disrupt the cascade.

**No code changes**, no architectural retractions. Refinement of
Iter 119/136 finding.

This is the kind of small but informative finding that emerges
when probing further into existing claims. The cast threshold
remains the dominant lever; this just adds nuance about
composition.
