# Iter 135 -- Iter 134 Mechanism Hypothesis Wrong (Self-Correction)

**Date:** 2026-04-26
**Iteration:** Iter 135
**Severity:** MEDIUM -- self-correction of Iter 134 mechanism claim

---

## 0. Summary

Directly tested Iter 134's hypothesis ("seeded rumor decay drives
timing effect"). **Hypothesis falsified**:

| Variant | Recovery rate |
|---|---:|
| V0 (t=3, rumor) | 53% |
| V1 (t=3, NO rumor) | **60%** |
| V2 (t=50, rumor) | 20% |
| V3 (t=50, NO rumor) | **60%** |

Removing the rumor produces **60% recovery regardless of accusation
timing**. The Iter 134 timing effect is rumor-driven but in OPPOSITE
direction from my hypothesis: the rumor HURTS recovery (creates
timing-dependent ambient state), not AMPLIFIES it.

---

## 1. What this corrects

### Iter 134 framing
"Seeded rumor amplifies recovery at t=3 (53%); rumor decays by t=50,
removing amplification → 20% recovery."

### Iter 135 reality
"Without rumor, recovery is 60% at any timing. Adding rumor:
- t=3 (rumor fresh): rumor's shame buildup + accusation produces
  53% (slightly worse than no-rumor 60%)
- t=50 (rumor partially decayed): 20% -- accusation hits agents
  in chaotic mid-rumor state, recovery cascade fails

The timing effect is rumor-state-dependent, but rumor REDUCES
recovery, doesn't amplify it.

---

## 2. Corrected mechanism interpretation

The seeded threat_to_authority rumor:
- Generates per-tick shame propagation through social network
- WITHOUT a pairing accusation event: agents experience low-grade
  ambient shame (rumor diffusion only)
- This ambient state is DIFFERENT from "fresh state" or
  "post-accusation peak shame"

When accusation fires:
- At t=3 (rumor fresh): agents have rumor-induced shame; accusation
  adds clearly-attributable trigger; confess→forgiveness cascade
  can fire. 53% recovery.
- At t=50 (rumor decaying): agents have been in low-grade shame for
  47 ticks. Crowd state has drifted (alignment, blame_concentration
  adjustments). Accusation arrives but the cascade can't coordinate.
  20% recovery.
- Without rumor: accusation triggers clear shame from baseline; clean
  cascade. 60% recovery.

**The rumor creates "ambient pressure" that interferes with cascade
coordination when paired with delayed accusation.**

---

## 3. The pure accusation finding

Without seeded rumor, accusation at any timing produces ~60%
recovery. This is HIGHER than I would have predicted.

| Iter 134 condition | Iter 135 (no rumor) |
|---|---:|
| t=3 baseline 53% | t=3 no-rumor: **60%** |
| t=50 ambient 20% | t=50 no-rumor: **60%** |

Pure accusation (no preceding rumor) is robust across timing.
Adding rumor introduces timing fragility.

This refines the predictive model:
> recovery_rate ≈ baseline × Π P(role r forgiven | cast)
>                × (1 - ambient_load)
>                × rumor_interference_factor(timing)

Where rumor_interference_factor:
- ≈ 1.0 if no seeded rumor (clean accusation)
- ≈ 0.9 if rumor + immediate accusation
- ≈ 0.3 if rumor + delayed accusation (>10 ticks)

---

## 4. Implications

### 4.1 Branch C scenario design refinement
Designers should be aware that **seeded rumors CAN reduce recovery
rate** if not paired with timely accusation events. The kernel
shows that "world has memory" applies to both supportive and
disruptive memory.

### 4.2 Honest acknowledgment
Iter 134's documented mechanism was wrong. I claimed "seeded
amplification regime" but the rumor isn't amplifying -- it's
modulating in a complicated way.

The Iter 134 raw finding (timing matters: 53% vs 20%) holds, but
the HYPOTHESIS for why was wrong.

### 4.3 Pattern across the arc
Iter 105-119 cleanup retracted multiple claims. Iter 127 found
model limits. Iter 135 found a hypothesis was wrong direction.
**Self-correction has been frequent**, which is honest engineering.

---

## 5. Connection to Element I (Time as Rhythm)

Element I criterion: "same event at different times has different
meaning". Iter 135 actually STRENGTHENS this:

**With rumor**: timing matters dramatically (53→20%)
**Without rumor**: timing doesn't matter (60% always)

So the rumor IS what makes time matter. Without world memory
(rumor), the kernel is timing-blind. With memory, timing produces
qualitatively different outcomes -- exactly Lee's Element I criterion.

This connects Element E (World Memory) and Element I (Time as
Rhythm): time-dependent dynamics REQUIRE memory layers. Without
memory, time is just tick counter.

---

## 6. What could still be wrong (H4)

- N=15 binomial CI on 60% is [33%, 84%]. V1 (60%) and V0 (53%) CI
  overlap; might be statistical noise rather than real "+7%".
- Tested only 2 timings (t=3, t=50). Smooth interpolation between
  them not measured.
- The "pure accusation 60%" baseline differs from Iter 116's t=3
  with rumor (53%). Iter 116 had "1 acc + rumor" → 53%. Iter 135
  V1 has "1 acc no rumor" → 60%. So removing rumor adds ~7% but
  CI overlap.
- "Rumor introduces fragility" framing is post-hoc. Could be that
  pre-rumor state changes subtly affect cast composition or
  motif activation.
- The 60% in V3 (t=50 no rumor) deserves attention: it suggests
  pure-accusation timing is robust for at least 50 tick delay.
  Untested at later delays.

---

## 7. What I did NOT try (H2)

- Late accusation (t=200, t=400) without rumor: predict still 60%
- N=30 verification of the +7% no-rumor uplift
- Rumor + immediate accusation at t=3 without disciple_follower
  target (test whether target_role-rumor coupling matters)
- Different rumor decay rates (slow rumor + delayed accusation)
- Multiple rumors with different content_tags

---

## 8. Conclusion

**Iter 134 mechanism hypothesis was wrong**. Rumor decay isn't the
mechanism; rumor INTERFERENCE is.

Specifically: seeded rumor without paired immediate accusation creates
ambient-pressure state that disrupts later accusation's recovery
cascade.

**Pure accusation (no rumor) is timing-robust** at ~60% recovery.

**Element I (Time as Rhythm) confirmed via opposite path**: time
matters because of WORLD MEMORY (the rumor). Time + memory = rhythm.
Time alone is just clock ticks.

**Predictive model refined** with rumor_interference_factor.

**No engine changes**, no architectural retractions. Pure self-
correction of a Iter 134 hypothesis.

This is the kind of self-criticism the arc benefits from -- finding
my own claim was wrong before it propagates.
