# Iter 141 -- Location-Pressure Effect is Role-Agnostic

**Date:** 2026-04-26
**Iteration:** Iter 141
**Severity:** LOW -- generalization of Iter 140 finding

---

## 0. Summary

Iter 140 found agents 04 (authority_priest) and 05 (soldier_enforcer)
flip 0%→100% recovery via location change. Iter 141 tests if this
generalizes to outsider role.

**Result: identical flip pattern**.

| agent_10 location | Recovery rate |
|---|---:|
| priest_courtyard (max pressure) | **0/15 (0%)** |
| city_street (medium) | 14/15 (93%) |
| upper_room (min pressure) | **15/15 (100%)** |

The location-pressure mechanism is **role-agnostic**: same dramatic
effect across authority_priest, soldier_enforcer, AND outsider roles.

---

## 1. Cross-role comparison (Iter 140 + Iter 141)

| Role | priest_courtyard | upper_room |
|---|---:|---:|
| authority_priest (a04) | 0% | 100% |
| soldier_enforcer (a05) | 0% | 100% |
| outsider (a10) | 0% | 100% |

Identical pattern across 3 different roles. **Location dominates role**
in determining per-agent recovery propensity.

---

## 2. Implications

### 2.1 Branch C scenario design simplification
Per-agent placement is THE key per-agent lever. It works the same
regardless of role:
- Place agent at low-pressure location → high recovery propensity
- Place agent at high-pressure location → guaranteed saturation

### 2.2 Predictive model further refined

> P(role r forgiven) ≈ P(role r forgiven | cast count) ×
>                      Π_{a ∈ role-r agents} placement_factor(a's location)

Where placement_factor:
- ~1.0 for low-pressure locations (upper_room)
- ~0.0 for high-pressure locations (priest_courtyard)

This explains why even "well-cast" scenarios can fail: if all role-r
agents are placed at high-pressure locations, P(role r forgiven) ≈ 0.

### 2.3 Iter 138 framing fully resolved
The priest_cohort saturation in Iter 138 wasn't:
- Affordance restriction (Iter 139)
- Role-specific (Iter 141 -- outsider behaves same way)

It IS:
- Location pressure ceiling effect, applied uniformly to any role
  placed at high-pressure location

---

## 3. What could still be wrong (H4)

- Tested only 1 outsider (agent_10) at varied locations. Outsiders
  07 and 08 stayed at city_street. Multi-outsider relocation might
  show different patterns.
- The "generalization across 3 roles" claim is based on 3 specific
  agents. Other roles (family, crowd) untested.
- Same scenario (2 acc diff roles, augmented cast). Cross-scenario
  generalization untested.
- The "0%" and "100%" extremes might shift with N=30 (binomial CI
  considerations).

---

## 4. What I did NOT try (H2)

- N=30 verification
- All 3 outsiders at upper_room (combined effect)
- Other roles (family, crowd) at high/low pressure
- Cross-scenario (sacred + relocated agents)
- Mixed locations (some agents high, some low)
- Beyond 3 location types (mid-tier locations untested)

---

## 5. Conclusion

**Location-pressure mechanism generalizes across roles**. Outsider,
authority_priest, and soldier_enforcer all flip 0%→100% recovery
identically when moved between high-pressure and low-pressure
locations.

**Per-agent placement is THE per-agent lever**, role-agnostic.

**Branch C 7-lever framework intact** (Iter 140 lever 7: per-agent
location placement).

**No code changes**, no architectural retractions. Pure generalization
verification of Iter 140 finding.
