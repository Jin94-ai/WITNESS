# Iter 161 -- Recovery Diversification: Spatial Disengagement Negative + Kernel Gap Identified

**Date:** 2026-04-26
**Iteration:** Iter 161
**Severity:** MEDIUM -- negative result + structural insight

---

## 0. Summary

Per `WITNESS_READABILITY_Q_IMPROVEMENTS_AND_NEXT_DIRECTION.md`
priority 4 + improvement point 2: explored **spatial disengagement
recovery** as a candidate recovery family beyond Phase 2a.

**Result: NEGATIVE**. Mid-sim relocation from high-pressure to
low-pressure location does NOT reduce already-accumulated shame.

| Variant | Pre-saturation peak | Post-relocation final | Recovery |
|---|---|---|---|
| V0 control (no relocate) | 10.0 | 10.0 | 0/5 |
| V1 relocate at t=80 | 10.0 | **10.0** | **0/5** |

---

## 1. Why this matters: kernel gap revealed

The spatial disengagement experiment revealed a fundamental
structural property: **shame has no passive decay rule**. Once it
reaches saturation (10.0), it stays there indefinitely unless an
ACTIVE mechanism reduces it (currently only Phase 2a forgiveness
rumor).

This explains why all of Lee's directive priority 4 candidates
would face similar issues:

| Candidate | Mechanism needed | Currently exists? |
|---|---|---|
| trust-driven stabilization | trust state + decay coupling to shame | NO (no trust→shame coupling) |
| belonging-driven calming | belonging state + decay coupling | NO |
| authority withdrawal de-escalation | authority_reach decay + shame coupling | partial (auth_reach exists; no decay-shame coupling) |
| spatial disengagement (this iter) | shame decay when away from event | **NO** (verified) |
| scarcity easing recovery | scarcity state + decay coupling | NO |
| ritual / sacred grounding | already exists for awe-baseline cast (Iter 95, 113) | YES (conditionally) |

**5 of 6 candidates require shame_decay or coupling rule that
doesn't exist in current kernel**.

---

## 2. The structural insight

The directive proposes "recovery diversity" but the kernel currently
has only ONE active reduction mechanism (Phase 2a forgiveness rumor).
Adding new recovery families requires either:

### Option A: Add passive shame_decay rule
```python
# Pseudocode
if agent at low-pressure location AND away from blame_concentration:
    shame *= 0.95  # gentle decay
```

This is a kernel mechanism addition. Risk per Iter 105-119 lessons:
could become decorative if not carefully verified.

### Option B: Add coupled active reductions
e.g., "trust > threshold → shame -= 0.1/tick" or "belonging
high → shame -= small_amount". Each is a new mechanism couple.

### Option C: Accept Phase 2a as sole channel
Lee's directive notes "Phase 2a 외 보조 recovery path 최소
1~2개 탐색해야 한다" -- but the empirical work (Iter 105-119)
showed aux mechanisms become decorative without strong driver.
Current state may be the practical limit.

---

## 3. Recommendation for project improvement

The directive's improvement point 2 (recovery diversity) is
genuine but requires **kernel decision**, not just probe work.
Three paths:

### Path 1: Implement shame_decay (small kernel addition)
Add ~10 lines to MicroWorld step: if agent at low-pressure location
AND no recent shame-source event AND shame > 0, decay shame slowly.

This would unlock multiple recovery family experiments:
- spatial disengagement (verified by repeating Iter 161 experiment)
- belonging-driven (with belonging state coupled to decay rate)
- authority withdrawal (with authority_reach modulating decay rate)

### Path 2: Defer to scenario-side
Accept that single-channel recovery is the kernel's current
property. Mark improvement point 2 as "kernel-extension-blocked".

### Path 3: Probe whether existing mechanisms could be repurposed
e.g., does forgiveness rumor at one location affect shame at another?
(Iter 145 found cross-location effect for crowd_participants -- 
similar mechanism might be repurposable for "spatial disengagement
via cross-location forgiveness diffusion")

---

## 4. Implementation cost (if Lee wants Path 1)

Adding `shame_decay` rule to MicroWorld step:
- ~10 lines code in `engine/world/micro_world/world.py`
- Configurable via `MicroWorldConfig.shame_decay_enabled` toggle
- Default OFF to preserve existing behavior
- New probe to verify it works (~50 lines)
- Per Iter 105-119 discipline: verify with N=15 + per-agent peak/final audit

**This breaks the "0 engine changes in 65+ iters" boundary**, but
it's a small targeted addition with explicit empirical motivation
(Iter 161 showed the gap).

Per CLAUDE.md HARNESS H6: I'm not the one to decide. This is
flagged for Lee's review.

---

## 5. Connection to Q-set improvement (Iter 161)

The Q-set update (READABILITY_BLIND_PROTOCOL.md v2) added Q5b
(narrative contribution of oscillation: HELPS / NEUTRAL / HURTS).

If oscillation is judged HURTS_READABILITY by evaluators, that's
evidence that Phase 2a's cycling pattern is artifact-prone, NOT
narrative-meaningful. In that case, adding recovery diversity
becomes more important (provides clean recovery arcs without
oscillation).

So Q5b indirectly informs the recovery-diversity priority.

---

## 6. What could still be wrong (H4)

- Tested only one relocation timing (t=80). Earlier relocation
  (e.g., t=15 before saturation) might allow shame to decay before
  ceiling. But shame still has no decay rule.
- N=5; N=15 might reveal seed-specific edge cases
- Spatial disengagement could work via interaction with crowd
  state changes (e.g., reduced ambient pressure at city_street
  after agents leave). Untested.
- "Shame has no decay" claim based on observation; haven't
  exhaustively searched code for such a rule
- The 10.0 ceiling persistence might be due to ongoing rumor
  effects (threat_to_authority rumor still active even after
  relocation). Without rumor, shame might drift.

---

## 7. What I did NOT try (H2)

- N=15 verification
- Earlier relocation (before saturation)
- Combined: relocate + remove rumor + add prayer/miracle to upper_room
- Code search for any existing shame_decay rule
- Test if relocation helps when shame is mid-range (not saturated)

---

## 8. Conclusion

**Spatial disengagement recovery candidate FAILS in current kernel**.
Once shame saturates, location change doesn't help.

**Kernel gap identified**: no passive shame_decay rule. This is the
underlying reason Lee's priority 4 candidates can't be implemented
with current kernel.

**Branch decision input** for Lee's project-improvement
prioritization:
- If recovery diversity is a key goal → kernel needs shame_decay
- If simplification (Branch B) wins → accept single-channel limit
- Q5b answers in upcoming Step C eval will inform whether
  oscillation is artifact (favoring decay addition) or feature
  (current single channel is enough)

**Per directive instruction "실험이 끝날때마다 결과를 회고하고
프로젝트 자체를 더 나은 방향으로 개선한다"**: this experiment's
retrospection produces a clean architectural insight (shame decay
gap) that informs project direction more than any individual
finding.

**No engine changes** this iter; gap is documented for Lee's
review.
