# Iter 140 -- Location Pressure Dominates Per-Agent Recovery

**Date:** 2026-04-26
**Iteration:** Iter 140
**Severity:** MEDIUM -- mechanism confirmation, strongest per-agent
finding of the arc

---

## 0. Summary

Tested whether priest_cohort saturation (Iter 138) is driven by
location pressure. **Confirmed dramatically**: relocating agents 04
and 05 from priest_courtyard to upper_room flips their recovery
from 0% to 100%.

| Variant | agent_04 (priest) | agent_05 (soldier) |
|---|---:|---:|
| V0 priest_courtyard | 0/15 (0%) | 0/15 (0%) |
| V1 upper_room | **15/15 (100%)** | **15/15 (100%)** |
| V2 city_street | 3/15 (20%) | 4/15 (27%) |

**Same agent, same role, same scenario events -- only initial
location differs.** Recovery rate ranges from 0% to 100%.

---

## 1. Location property comparison

| Location | visibility | concealment | authority_reach | Pressure level |
|---|---:|---:|---:|---|
| priest_courtyard | 0.9 | 0.1 | 0.9 | MAX |
| city_street | 0.6 | 0.3 | 0.4 | MEDIUM |
| upper_room | 0.2 | 0.7 | 0.1 | MIN |

Per Iter 133 mechanism findings:
- `authority_reach * 5 = physical_threat pressure`
- `visibility + low concealment → shame_exposure boost`

priest_courtyard: physical_threat = 4.5, shame_exposure boost = +2.7
upper_room: physical_threat = 0.5, no shame_exposure boost
(visibility too low)

Difference is dramatic enough to flip recovery 0%↔100%.

---

## 2. Implications

### 2.1 Per-agent recovery is location-determined within scenario
Same role + same accusation = different outcomes by location.
This is the strongest per-agent design lever measured.

### 2.2 Iter 138 mechanism CONFIRMED
priest_cohort saturation isn't:
- Affordance restriction (Iter 139 showed confess is universally available)
- Role-specific (other roles in same location would saturate too)

It IS:
- Location pressure ceiling effect

### 2.3 Branch C scenario design has 2 levers per agent
1. Role (which affordances, motif tendencies)
2. Initial location (which pressure environment they enter)

Designers can:
- Same character in different starting location → different arc
- Same scenario with different placements → different cohort outcomes

### 2.4 Updated predictive model

Pre-Iter-140:
> recovery_rate ≈ Π P(role r forgiven | cast)

Pre-Iter-140 with Iter 138 correction:
> recovery rate is per-cohort, not uniform

Post-Iter-140:
> P(role r forgiven) = function(cast count, ROLE TYPE × LOCATION PRESSURE)
>
> A role at high-pressure location saturates regardless of cast
> A role at low-pressure location recovers reliably

---

## 3. The 7-lever framework (post Iter 140)

1. Cast composition (Iter 100/118-119/136)
2. Pressure events (Iter 116-117)
3. Time horizon (Iter 129-130)
4. Memory layers (Iter 122-123)
5. Location parameters (Iter 133)
6. Event timing relative to memory state (Iter 134-135)
7. **Per-agent location placement** (Iter 140, NEW)

Lever 7 is per-agent (not per-scenario). It interacts with role
and accusation patterns.

---

## 4. What could still be wrong (H4)

- N=15 binomial CI on 100% is [78%, 100%]. Could be slightly less
  with N=30; unlikely given stdev=0 pattern.
- Tested only 3 location combinations. Other locations might give
  different results.
- Co-locating both agents in same location may reinforce dynamics
  not present when split. Untested.
- The accusation events still target "disciple_follower" and
  "outsider" roles -- agents 04 (priest) and 05 (soldier) aren't
  directly accused. Their recovery measures ambient response, not
  conjunctive condition. Different dynamics may apply if they were
  the accused role.

---

## 5. What I did NOT try (H2)

- Mixed placements (a04 at upper_room, a05 at city_street)
- N=30 verification
- Direct accusation of agent_04's role (authority_priest) at
  upper_room vs priest_courtyard
- Rebuild test cast where agent_04 IS at low-pressure default
- Cross-scenario relocation test (sacred + upper_room agents)

---

## 6. Cumulative arc summary (Iter 105-140)

| Iter group | Output |
|---|---|
| 105-110 | PYHASH cleanup + 6 retractions |
| 111-119 | Predictive model + cast threshold (n=2 sweet spot) |
| 120-126 | Step C prep + memory verification |
| 127-130 | Model limits + scenario topology (bistable vs monostable) |
| 133-138 | New dimensions probed: space (133), time (134), corrections (135-138) |
| 139-140 | Code-reading + per-agent location mechanism |

The arc has produced:
- Robust predictive framework
- 7 design levers
- Multiple self-corrections
- Clean per-agent and per-cohort understanding
- Step C readability materials prepared

---

## 7. Conclusion

**Location pressure is the strongest per-agent design lever**:
0% to 100% recovery flip via location change alone. This validates
Iter 138's per-cohort saturation finding mechanistically.

**Branch C scenario design has 7 levers** including the new
per-agent location placement.

**No engine changes**, no architectural retractions. Pure mechanism
verification of an Iter 138 hypothesis.
