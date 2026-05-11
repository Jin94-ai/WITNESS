# Iter 165 -- Meso-Scale Cross-Coupling: Already Rich

**Date:** 2026-04-26
**Iteration:** Iter 165
**Severity:** MEDIUM -- positive structural finding

---

## 0. Summary

Per directive `WITNESS_READABILITY_Q_IMPROVEMENTS_AND_NEXT_DIRECTION.md`
§6 improvement point 4 (Meso-scale 강화), tested whether existing
meso fields cross-couple.

**Finding: 7 of 10 pairs show |r| > 0.3** -- meso-scale dynamics
are already richly coupled via indirect path.

| Pair | Pearson r |
|---|---:|
| blame_total ↔ public_susp | **+0.684** |
| blame_total ↔ shame_climate | **+0.650** |
| alignment ↔ blame_total | +0.571 |
| alignment ↔ public_susp | +0.557 |
| alignment ↔ density | +0.474 |
| public_susp ↔ shame_climate | +0.408 |
| alignment ↔ shame_climate | +0.382 |

---

## 1. Direct vs indirect coupling

### `step_crowd` per-tick rules (DIRECT couplings)
- `alignment_strength < 0.2` → `dominant_emotion = "indifferent"`
- `alignment_strength > 0.4` + density + contagion → alignment
  positive feedback
- All other fields decay independently (no cross-field rules)

### Empirical correlations (INDIRECT couplings via cascade)

The 7+ correlated pairs emerge through indirect paths:
- accusation event spawns: simultaneously updates blame_concentration
  + shame_climate + alignment
- forgiveness rumor reduces: blame + alignment + shame_climate +
  public_suspicion (per Iter 145 cross-location effects)
- agent state → action selection → spawned events → meso updates
- shame_climate → agent shame_exposure pressure → agent decisions
  → events → all meso fields

Net result: meso fields move together because they share event
sources and propagation paths.

---

## 2. Implication for directive improvement 4

Directive says "meso-scale 강화" with goal:
> 세계를 "개인 로그의 합"이 아니라 "집단적 흐름을 가진 구조"로 바꾸기

Iter 165 finding: **the kernel already has 집단적 흐름 (collective
flow) at meso scale**. The 7 strong correlations indicate fields
move as a coupled system.

So "strengthening" may not need new mechanisms. Three options:

### Option 1: Add direct cross-field rules
e.g., shame_climate += 0.05 * public_suspicion per tick. Would
make couplings stronger and more deterministic.

Risk per Iter 105-119 lessons: could create phantoms if not
carefully verified.

### Option 2: Expose existing coupling in probes
Iter 163 annotated probe added "Crowd blame total: peak X at tY → final Z".
Could similarly expose the COUPLING by showing parallel trajectories
of multiple fields.

This is presentation work, no kernel changes.

### Option 3: Accept current state
Score-5 (Meso-scale Reality) at 2 may be appropriate. Iter 165
shows the meso system is internally rich; whether external
evaluators perceive the coupling depends on Step C results.

---

## 3. Connection to Q-set update (Iter 161)

The Q-set added Q3b (multi-select for what changed):
- interpersonal_relation
- group_alignment
- crowd_mood
- authority_presence
- public_attention
- not_discernible

If evaluators correctly identify multiple Q3b categories per probe
(reflecting the coupled meso fields), the kernel's coupling IS
externally readable.

If only `not_discernible` or `interpersonal_relation` is picked
(individual-level only), the coupling is internal but not exposed.

This makes Q3b a key signal for whether to do Option 1 (add direct
rules), Option 2 (expose in probes), or Option 3 (accept).

---

## 4. Surprising specific findings

### blame_total ↔ public_susp r=+0.684 (strongest)
These two fields are NOT directly coupled in step_crowd. Yet
they show the strongest correlation. Mechanism:
- accusation events feed BOTH simultaneously
- forgiveness rumors reduce BOTH simultaneously
- They effectively share a common driver (accusation/forgiveness
  event flow)

### density ↔ alignment r=+0.474
This is a step_crowd direct coupling: alignment positive feedback
is gated by density. Empirical correlation matches expectation.

### shame_climate ↔ public_susp r=+0.408 (weakest of "strong")
Independent decay rules but correlated via shared event sources.

---

## 5. What could still be wrong (H4)

- N=5 × 200t = 1000 samples. Modest. Higher N might give different
  correlations.
- Tested only priest_courtyard. Other locations might show
  different coupling patterns.
- Pearson correlation captures linear relationships; nonlinear
  couplings might be missed.
- Lag effects untested (does shame_climate at t lead public_susp
  at t+5?).
- Default scenario (accusation events). Different scenarios might
  show different coupling.

---

## 6. What I did NOT try (H2)

- N=15 verification
- Cross-location coupling matrix
- Lag analysis (cross-correlation function)
- Compare with V1 (no events) coupling -- might be much weaker
- Test sacred / scarcity scenario coupling

---

## 7. Conclusion

**Meso-scale dynamics are richly coupled at empirical level**: 7 of
10 pairs show |r| > 0.3 despite step_crowd treating fields as
independent decay processes.

**The coupling is INDIRECT** (via shared event sources + agent
feedback), not built into kernel rules.

**Directive improvement 4 framing**: "strengthen meso-scale" could
mean adding direct rules, exposing coupling in probes, or accepting
the rich indirect coupling as sufficient. Lee should choose based
on Step C readability results -- if Q3b shows evaluators detect
multiple meso categories, current state is sufficient.

**Per directive instruction "결과를 회고"**: this iter shows that
"empirical kernel state" can be richer than "kernel rule structure"
suggests. Meso fields don't have direct couplings in step_crowd
but become coupled through dynamics. This is consistent with the
project's "world that flows" thesis -- emergence, not just
mechanism.

**No engine changes**, no new mechanisms. Pure observational probe
that supports current state.
