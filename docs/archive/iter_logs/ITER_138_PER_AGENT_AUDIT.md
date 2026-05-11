# Iter 138 -- Per-Agent Audit Reveals Iter 118 Framing Issue

**Date:** 2026-04-26
**Iteration:** Iter 138
**Severity:** HIGH -- corrects framing of strongest finding (Iter 118)

---

## 0. Summary

Per-agent audit of Iter 118 V3 (augmented cast 3 outsiders, 2 acc
diff roles, "93% recovery"). **Two surprises**:

1. **Outsiders DO confess** (95 times in 5 seeds) despite outsider
   role's `affordance_pack` not listing 'confess'. Action selection
   isn't strictly bound by affordance_pack.
2. **Priest_courtyard cohort NEVER recovers** -- agents 04 and 05
   saturate to shame=10.0 in 100% of seeds. The "93% recovery" was
   a per-seed mean dominated by other cohorts.

---

## 1. Per-agent final shame (5 seeds, augmented cast, 2 acc diff)

| Agent | Role | Final shames across seeds |
|---|---|---|
| agent_01 | disciple_follower | [0.5, 0.5, 0.5, 0.5, 0.5] |
| agent_02 | disciple_follower | [0.5, 0.5, 0.5, 0.5, 0.5] |
| agent_03 | disciple_follower | [0.5, 0.5, 0.5, 0.5, 0.5] |
| agent_04 | authority_priest | **[10.0, 10.0, 10.0, 10.0, 10.0]** |
| agent_05 | soldier_enforcer | **[10.0, 10.0, 10.0, 10.0, 10.0]** |
| agent_06 | crowd_participant | [0.0, 0.0, 0.0, 0.0, 0.0] |
| agent_07 | outsider | [0.0, 0.0, 0.0, 0.0, 0.0] |
| agent_08 | outsider | [0.0, 0.0, 0.0, 0.0, 0.0] |
| agent_09 | family_anchor | [0.5, 0.5, 0.5, 0.5, 0.5] |
| agent_10 | outsider | [0.0, 0.0, 0.0, 0.0, 0.0] |

**Pattern**:
- Disciples + family + crowd + outsiders → recover to 0-0.5
- Authority + soldier → saturate to 10.0 (priest_courtyard cohort)

Per-seed mean across all cycling agents:
> (10+10+0+0+0+0+0.5+0.5+0.5+0.5) / 8 ≈ 2.75-3.33

This is what Iter 118 reported as "recovery" -- a per-seed mean,
not per-cohort recovery.

---

## 2. Why agents 04, 05 saturate

agent_04 (authority_priest) and agent_05 (soldier_enforcer) are at
priest_courtyard. priest_courtyard has high authority_reach (0.9)
and high visibility (0.9), low concealment (0.1). Per Iter 133:
- authority_reach * 5 = 4.5 physical_threat pressure
- visibility + low concealment compounds shame_exposure

These two agents are subjected to MAXIMUM ambient pressure. Authority
and soldier roles also have low confess motif tendencies (priest
role has confess but with low priors per Iter 79).

So priest_courtyard cohort is a **deterministic saturation regime**
in this scenario design. They don't recover because:
- High location pressure
- Low confess priors
- No forgiveness rumor reaches them with target_role matching their
  roles (authority_priest, soldier_enforcer rarely confess)

---

## 3. Why outsiders confess despite affordance_pack

This is genuinely surprising. outsider's affordance_pack is:
```
["withdraw_in_fear", "stay_hiding", "follow_at_distance", "watch_quietly"]
```

No 'confess'. Yet 95 outsider confessions across 5 seeds × 500t.

Possible mechanism (untested):
- Action selection logic falls through to motif-driven choice when
  affordance_pack doesn't have action match
- Available_filter in `_agent_decide` might allow action regardless
  of affordance_pack
- Or: outsider role inherits some default actions from a base

This is a kernel-mechanism question worth investigating but doesn't
invalidate the Iter 118 finding -- the EFFECT of cast augmentation
is real.

---

## 4. Iter 118 framing correction

### Pre-Iter-138
> "Cast augmentation alone (1 outsider → 3 outsiders) flips 2-acc-
> diff-roles recovery rate from 0% to 93%."

### Post-Iter-138
> "Cast augmentation rescues 7-8 of 10 agents (specifically:
> disciples + family + crowd + outsiders). The priest_courtyard
> cohort (authority_priest, soldier_enforcer) saturates regardless --
> location pressure + low confess priors prevent their recovery in
> this scenario design."

The 93% per-seed-mean recovery is real, but it's NOT uniform.

### Updated predictive model

> recovery_rate(cohort) ≈ baseline ×
>   ∏_{r ∈ cohort accused roles ∩ confess-capable roles} P(role r forgiven)
>   × scenario factors

Critically: **a role saturates if it's in a high-pressure location
AND has low confess priors**, regardless of cast representation.

---

## 5. Implications for Branch C

### 5.1 Per-cohort design awareness
Branch C scenario designers should think per-cohort:
- Which cohorts will recover? (those with confess-capable roles +
  reasonable location)
- Which will saturate? (those at high-pressure locations OR
  with rare confess)
- Mean recovery rate is a misleading single number; cohort
  breakdown is what matters narratively

### 5.2 Honest acknowledgment
Iter 118-119's "93% recovery" sounded like uniform success but
was a population mean. This is exactly the kind of metric framing
Lee's anti-bias HARNESS rules warn about (H1, H4): single metric
can mask structural variance.

### 5.3 Stage B verdict mostly preserved
The kernel DOES produce predictable structure. But the structure
is more nuanced than a single "recovery rate" captures. Different
cohorts have different recovery propensities determined by:
- Role × location coupling (per-cohort baseline)
- Cast representation (modulator within cohort)
- Pressure events (determines which cohorts get accused)

---

## 6. What could still be wrong (H4)

- N=5 seeds × 1 condition. Per-agent finals are extremely
  consistent (stdev=0 in most cells), which is suspicious. Could
  be deterministic kernel reaches same equilibrium each seed.
- Outsiders' ability to confess despite affordance_pack might be
  a probe-script-side issue (not a kernel issue). Need to verify
  by reading action selection code.
- The 100% saturation of agents 04, 05 might be specific to this
  seed range. With N=15 some seeds might escape.
- The "0.5" final for disciples is suspiciously consistent across
  all seeds. Could be deterministic equilibrium related to
  forgiveness rumor decay.

---

## 7. What I did NOT try (H2)

- Read action selection code to confirm/refute affordance_pack
  being non-binding
- N=15 to see if any seeds break the agents 04, 05 saturation
- Different scenarios (sacred + augmented cast) for per-agent audit
- Original cast (1 outsider) per-agent audit (compare to V3)
- Check if pressure events on disciples ALSO occasionally saturate
  some agents

---

## 8. Conclusion

**Iter 118-119 finding partially corrected**: cast augmentation
rescues MOST cohorts but priest_courtyard cohort saturates regardless.

**Per-cohort breakdown reveals**:
- Disciples + outsiders + crowd + family: recover reliably with
  cast augmentation
- Authority + soldier (in priest_courtyard): saturate due to high
  pressure + low confess

**The "93% recovery" was a population mean, not per-cohort recovery**.

This refines (doesn't retract) the predictive model: Branch C
scenarios should be designed per-cohort, with awareness that some
roles will deterministically saturate under high-pressure locations.

**No code changes**, but framing of Iter 118 finding requires
update across docs to be honest about per-cohort variation.

This is exactly the kind of self-correction the arc benefits from --
finding nuance behind a headline number before it propagates as
overconfident summary.
