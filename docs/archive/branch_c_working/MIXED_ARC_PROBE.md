# WITNESS B-Direction — Mixed-Arc Minimal Probe

**Freeze date:** 2026-04-25
**Step E of post-loop audit** (`WITNESS_POST_LOOP_FREEZE_AND_NEXT_STEPS.md`)

---

## 0. Purpose

Test whether the frozen kernel:
- Holds structural findings under mixed-pressure conditions
- Produces arc-like flow under overlap, or collapses to single loop
- Has cross-pressure dynamics (relation / world memory interaction)

Per work directive §3, minimum 2 probes:
1. **accusation + sacred overlap**
2. **scarcity + private grief overlap**

---

## 1. Method

Per probe, 3 conditions:
- **A baseline**: scenario unmixed (reference)
- **B mixed**: scenario + overlay injection
- **C mixed + P2a off**: mixed + ablation (does P1 hold under mixing?)

5 seeds × 200 ticks each. PYHASH=0 pinned. Script:
`scripts/b_direction/run_mixed_arc_probe.py`.

Mixing mechanisms chosen per Iter 77-80 filter-layer analysis:
- Use KNOWN-COUPLED mechanisms (direct state injection into motif-read fields)
- Avoid dormant events (sacred seeds) and decoupled state (awe) as
  PRIMARY mixing — but include for completeness

---

## 2. Probe 1 — Accusation + Sacred Overlay

### 2.1 Mixing design

- **awe injection**: agent_01 + agent_02 (upper_room disciples) get
  `state["awe"] = 6.0` at t=0
- **crowd dominant_emotion**: priest_courtyard crowd gets
  `dominant_emotion = "awe"` at init

Both mechanisms known decoupled from cycle machinery (Iter 78, 89).
Used as PROBE rather than expected to produce effect.

### 2.2 Results (N=5 × 200 tk)

| Condition | rev_all | rev_inj | rev_oth | final | confess/seed | grieve/seed |
|---|---:|---:|---:|---:|---:|---:|
| A baseline | 3.17 | 0.00 | 3.17 | 5.96 | 36.6 | 13.8 |
| B mixed | **3.17** | 0.00 | 3.17 | **5.96** | **36.6** | **13.8** |
| C mixed + P2a off | 0.00 | 0.00 | 0.00 | 10.00 | 88.6 | 72.6 |

### 2.3 Finding — A and B BIT-IDENTICAL

Sacred overlay produces **zero effect** on any measured variable:
- rev/agent: identical
- final shame: identical
- grieve motif firing: identical
- confess events: identical

**This empirically confirms Iter 77-78 architectural finding**: sacred
state fields (awe) and sacred crowd emotion are completely decoupled
from the cycle mechanism. "Sacred overlay on accusation" produces no
mixed-arc — sacred elements are pure narrative decoration.

### 2.4 P1 holds under this "mixing"

C condition (P2a off + mixed): rev_all → 0, final → 10. Standard
P1 ablation pattern. Mixed overlay doesn't change ablation response.

### 2.5 Probe 1 verdict

**Probe 1 does NOT produce real mixed-arc**. Sacred overlay is
architecturally inert. Collapsed to single (accusation) loop.

This is a REPLICATION of Iter 77/78 findings in the freeze audit.
Confirms the decoupling architectural claim at probe level.

### 2.6 Readability implication

If human evaluator reads a Probe 1 B output, it should be
indistinguishable from Probe 1 A. This becomes a test of
**dominant-pressure perception** (Q2): if evaluator senses
sacred-flavored pressure in B but not A, that would be a spurious
perception (data is identical).

---

## 3. Probe 2 — Scarcity + Private Grief Overlay

### 3.1 Mixing design

- **Guilt + grief injection** (Iter 57 coupling-verified method):
  agent_03 + agent_04 + agent_05 (fisher_laborer cohort) get
  `guilt.self=6.0`, `guilt.primary_focus=4.2`, `grief=3.0` at t=0

These fields ARE motif-read (confess, grieve, weep motifs).

### 3.2 Results (N=5 × 200 tk)

| Condition | rev_all | rev_inj | rev_oth | final | confess/seed | grieve/seed |
|---|---:|---:|---:|---:|---:|---:|
| A baseline | 3.90 | 3.80 | 4.00 | 3.28 | 99.8 | 99.8 |
| B mixed | **1.17** | 1.00 | 1.30 | **2.50** | **225.0** | **251.6** |
| C mixed + P2a off | 0.00 | 0.00 | 0.00 | 10.00 | 301.0 | 80.2 |

### 3.3 Finding — real mixed dynamics

Under grief injection (B vs A):
- **rev_all drops 3.9 → 1.17** (−2.73, −70%)
- **grieve firing increases 99.8 → 251.6** (+152%, 2.5×)
- **confess firing increases 99.8 → 225.0** (+125%)
- Final shame drops slightly (3.28 → 2.50, deeper recovery)

**Interpretation**: Grief injection displaces cycling behavior with
motif-firing activity. Agents spend more ticks in grieve + confess
motifs (higher counts) but reversal-based cycling drops (fewer
peak-trough oscillations on shame trace). This is the first clean
demonstration of an arc-like behavior shift under mixing.

### 3.4 Cohort separation (inj vs oth)

Under B mixed:
- rev_inj = 1.00 (3 injected fishers)
- rev_oth = 1.30 (9 non-injected)

Both cohorts drop similarly from baseline (baseline inj=3.80,
oth=4.00 → mixed inj=1.00, oth=1.30). Mixing effect is **cohort-wide**,
not just injected — likely via events_recent propagation (high confess
events from injected cohort affect everyone's confess motif activation).

### 3.5 P1 holds under mixing

C condition (P2a off + mixed): rev → 0, final → 10. Iter 66 P1
replicated even under grief-overlay mixing. Structural finding
robust.

### 3.6 Probe 2 verdict

**Probe 2 produces genuine mixed-arc dynamics**:
- Cycle count suppressed (real effect)
- Motif composition shifts (grieve + confess dominate)
- Final recovery is deeper (2.5 vs 3.3)
- Cohort-wide propagation (not local to injected agents)

This is a NEW finding during the audit: grief injection into scarcity
base doesn't just add cycling — it REDUCES cycling while increasing
motif activity. Agents engage with grief processing instead of
crisis oscillation.

Whether this is a "richer narrative arc" or "a different single loop"
requires readability blind evaluation (Step C).

---

## 4. Cross-probe comparison

| Question | Probe 1 (acc+sacred) | Probe 2 (scar+grief) |
|---|:-:|:-:|
| Mixing produced any state delta? | **No** (bit-identical) | **Yes** (ΔMany metrics) |
| Single-loop collapse? | **Yes** (same as A) | **No** (different dynamic regime) |
| P1 ablation holds? | **Yes** | **Yes** |
| Cohort differentiation? | No (identical) | **Cohort-wide effect** (not just inj) |
| Relation / world restructuring? | No | Visible (grieve firing +152%) |
| Readability impact (predicted)? | Same as A | Different trajectory, possibly richer |

---

## 5. Does one pressure family dominate?

**Probe 1**: Sacred pressure does NOT dominate accusation —
sacred is architecturally decoupled, so accusation pressure
completely dominates.

**Probe 2**: Grief injection does NOT kill scarcity cycling —
scarcity's accumulation pressure persists. Instead, grief ADDS a
parallel motif track (grieve + weep firing more often). Neither
dominates; they coexist with shifted emphasis.

### 5.1 Implication for kernel robustness

- Kernel shows **brittle response to sacred overlay** (no response)
- Kernel shows **responsive behavior to grief overlay** (modified dynamics,
  P1 still holds)

This asymmetry reflects the architectural separation identified in
Iter 77-78-89: only motif-coupled state fields change dynamics.

---

## 6. Readability hypothesis for Step C

Based on Probe 1 + 2 results:

- **Probe 1 B (acc + sacred)**: expected to read identically to Probe 1 A.
  Evaluator should NOT be able to perceive "sacred overlay" if
  working blind on the compact log.
- **Probe 2 B (scarcity + grief)**: expected to read as grief-heavy,
  less cycling, more weeping. Evaluator may perceive this as Arc D
  (grief) emerging over scarcity base.

If readability evaluation confirms these predictions, that validates
the decoupling/coupling architectural claim at the human-perceived
level.

---

## 7. Branch decision implications

### Inputs this probe gives to branch decision

1. **"Does one pressure family kill another?"** — NO. Both probes
   preserve structural findings (P1 holds).

2. **"Mixed arc or single-loop collapse?"** —
   - Probe 1: single-loop collapse (sacred decoupled)
   - Probe 2: modified dynamics, NOT pure single loop

3. **"Relation / world memory cross-reaction?"** —
   - Probe 1: none (sacred ignored)
   - Probe 2: cohort-wide propagation via events_recent (new finding)

4. **"Readability under mixing — better or worse?"** —
   Unknown without Step C human eval.

### Branch implications

- **Pro Branch A (readability)**: Probe 2 produces visually richer
  output (more motif variety, deeper recovery) that evaluators might
  perceive as "more narrative." Worth testing readability on Probe 2 B.

- **Pro Branch B (simplification)**: Probe 1's null (sacred completely
  decoupled despite being a "scenario element") argues for either
  WIRING sacred events OR REMOVING them. Current state is worst-case
  (appears wired, is dormant).

- **Con Branch C (broader world)**: Current kernel has only one real
  mixing axis (guilt/grief into existing cohort). Sacred can't mix
  without feature work. This suggests broader-world ambition is
  premature without first either wiring sacred or simplifying it.

---

## 8. What could still be wrong (H4)

- 2 probes only. Other mixing combinations (accusation + private_crisis,
  sacred + scarcity) untested.
- Single PYHASH (0). Noise floor for probe-2 metrics not measured.
- 200 tick horizon. Longer runs could reveal delayed mixing effects.
- Probe 2 grief injection is Iter 57 method — grief + guilt BOTH injected;
  cannot separate grief-alone effect from guilt-alone.
- "Arc-like flow" vs "single loop collapse" is subjective without
  human eval.
- Cohort-wide propagation (Probe 2) not traced to confirm events_recent
  is the propagation channel — could be crowd-level.

---

## 9. What I did NOT try (H2)

- Scarcity + sacred (sacred decoupled, expected null).
- Accusation + private grief (symmetric to Probe 2 but different base
  scenario).
- Longer horizon (500 tk).
- Empirical activate_motifs instrumentation under mixed condition
  (would confirm motif-ranking shifts).
- Temporal analysis (when does grief injection stop producing cycling
  reduction?).

---

## 10. Step E conclusion

**Probe 1 (accusation + sacred)**: confirms architectural decoupling
of sacred layer. Null mixing. P1 ablation replicates.

**Probe 2 (scarcity + grief)**: produces genuine mixed-arc dynamics
at cohort-wide scale. Cycling suppressed, motif diversity increased,
recovery deeper. P1 ablation still holds.

**Criterion 7 substantively advanced**: Kernel is robust to mixing
(P1 holds) but responds differentially based on architectural
coupling. This is the expected behavior for a kernel that has
narrative decoration separated from mechanism.

---

## 11. Completion checklist per work directive §3 Step E

- [x] accusation + sacred overlap — probed (Probe 1)
- [x] scarcity + private grief overlap — probed (Probe 2)
- [x] "Does one pressure family kill another?" — answered NO
- [x] "Mixed arc vs single-loop collapse?" — answered (both patterns observed)
- [x] "Relation / world memory cross-reaction?" — observed in Probe 2
- [ ] "Readability better or worse under mixing?" — requires Step C human eval

5 of 6 checklist items complete; item 6 awaits readability blind.

---

**End of Mixed-Arc Minimal Probe. Combined with Step C readability
results, provides full input to branch decision.**
