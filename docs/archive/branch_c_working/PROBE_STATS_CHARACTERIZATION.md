# Probe Statistics Characterization (12 Readability Probes)

**Date:** 2026-04-26
**Iteration:** Iter 184 (post-cycle small experiment)
**Status:** Post-hoc analysis of existing probe outputs (no new mechanism)
**Source:** `docs/b_direction/readability_probes/P{1-12}.txt`

---

## 0. Purpose

Cross-probe objective stats baseline. Helps:
- Evaluator anticipate what variance to expect across the 12 probes
- Identify outlier probes (e.g., very long event logs, atypical action mixes)
- Inform future v2 annotated probe format (e.g., line caps that scale with event density)
- Provide quantitative anchor for §6 Q-set V3 trigger-condition decisions

**This is pure post-hoc analysis** — no new mechanism, no new scenario, no
Phase 2a drilling. Reads existing P1.txt-P12.txt files only.

---

## 1. Per-probe stats table

Counts derived from `grep -c` over event log lines.

| P | Scenario | Variant | Lines | Acc | Confess | Forgive | Deny | Guard | Prayer | Miracle |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| P1 | scarcity | sham_mul_0.8 | 453 | 1 | 106 | 106 | 60 | 1 | 0 | 0 |
| P2 | scarcity | baseline s=2 | 523 | 1 | 117 | 117 | 93 | 1 | 0 | 0 |
| P3 | accusation | p2a_off | 825 | 2 | 124 | 124 | **370** | 1 | 0 | 0 |
| P4 | sacred | baseline s=0 | **209** | 1 | **31** | **31** | 77 | 0 | 1 | 1 |
| P5 | sacred | baseline s=1 | **199** | 1 | **30** | **30** | 65 | 0 | 1 | 1 |
| P6 | scarcity | p2a_off | **979** | 1 | 142 | 142 | **447** | 1 | 0 | 0 |
| P7 | sacred | sham_mul_0.05 | 368 | 1 | 82 | 82 | 114 | 0 | 1 | 1 |
| P8 | accusation | sham_mul_0.8 | 415 | 2 | 38 | 38 | 248 | 1 | 0 | 0 |
| P9 | scarcity | baseline s=0 | 469 | 1 | 52 | 52 | 183 | 1 | 0 | 0 |
| P10 | accusation | baseline s=0 | 434 | 2 | 41 | 41 | 266 | 1 | 0 | 0 |
| P11 | accusation | baseline s=3 | 424 | 2 | 32 | 32 | 269 | 1 | 0 | 0 |
| P12 | sacred | p2a_off | 665 | 1 | 155 | 155 | 218 | 0 | 1 | 1 |

---

## 2. Cross-probe patterns (objective)

### 2.1 Accusation count = scenario fingerprint
- **Accusation scenarios**: 2 accusations (multi-target)
- **Scarcity / Sacred scenarios**: 1 accusation each

This is structural (per scenario builders) and gives Q2a a deterministic
hint if the evaluator counts accusations.

### 2.2 Sacred event signature
- **Sacred only**: prayer=1, miracle=1, guard=0
- **Non-sacred**: prayer=0, miracle=0, guard=1

A 3-event signature uniquely identifies sacred. **Annotated probe format
should preserve this** (currently does — accusations + sacred events all
appear in event log).

### 2.3 Confess == Forgive (always 1:1)
Every public_confession spawns one forgiveness_emitted event. Structural.
This is informative for evaluator: count one, get the other.

### 2.4 p2a_off variants produce MORE confessions, not fewer
| Probe | Variant | Confess count |
|---|---|---:|
| P3 (accusation p2a_off) | p2a OFF | 124 |
| P10 (accusation baseline) | p2a ON | 41 |
| P6 (scarcity p2a_off) | p2a OFF | 142 |
| P9 (scarcity baseline) | p2a ON | 52 |
| P12 (sacred p2a_off) | p2a OFF | 155 |
| P4 (sacred baseline) | p2a ON | 31 |

**3.0× more confessions** when Phase 2a is disabled. Mechanism: without
forgiveness-rumor-driven shame decay, agents stay in high-shame state and
keep confessing. Recovery never resolves.

This is a **strong cross-probe pattern** that pilot/full eval can detect
if evaluator is looking for "did it stop confessing?" signal.

### 2.5 sham_mul_0.8 dampens denials in scarcity
- P1 (scarcity sham_mul_0.8): 60 denies
- P2 (scarcity baseline s=2): 93 denies
- P9 (scarcity baseline s=0): 183 denies

sham_mul=0.8 (0.8× shame applied to forgiveness-targeted agents) reduces
agent shame → fewer agents in deny motif → fewer public_denial events.
But sample is small; could be seed variance.

### 2.6 Sacred baseline = quietest probes
- P4 (sacred s=0): 209 lines, 31 confess
- P5 (sacred s=1): 199 lines, 30 confess

Less than half the event count of the median probe. Sacred baseline
produces less crisis. Q-set evaluator may rate these as "FLAT" or "WEAK"
arc.

### 2.7 Sacred p2a_off vs sacred baseline
- P12 (sacred p2a_off): 665 lines, 155 confess
- P4/P5 (sacred baseline): ~200 lines, ~30 confess

**5x more events when sacred recovery is disabled.** The Iter 113 finding
(late miracle = -26.7%) is consistent: sacred events DO have causal effect
on recovery. Disabling p2a removes the recovery, leaving agents to keep
confessing.

---

## 3. Implications for evaluator (Q-set anchor points)

### 3.1 Q1 (Flow vs noise) anchor
Lines / event count strongly correlates with "noisiness":
- **Quiet** (P4, P5): ~200 lines → easier to feel a flow
- **Noisy** (P3, P6, P12): 600-1000 lines → harder to detect arc

Evaluator confusion on Q1 may correlate with line count (post-eval check).

### 3.2 Q2a (primary pressure) hints
- 2 accusations = accusation scenario
- prayer + miracle = sacred scenario
- 1 accusation + no sacred events = scarcity scenario

If evaluator misses these structural cues, Q2a accuracy will drop.

### 3.3 Q4a (arc type) anchor
- p2a OFF variants: confess count high but final shame high → "saturation"
  arc (escalation without resolution)
- p2a ON baseline: confess count low and final shame mixed → "recovery"
  or "partial" arc

Cross-checking confess count to Q4a answer gives objective sanity.

### 3.4 Q5a (oscillation) hint
Probes with **multiple deny → confess transitions** (e.g., P10, P11
accusation baseline) show oscillation pattern. Probes with sustained
single motif (P3, P6 saturated) show less oscillation.

---

## 4. Outlier probes flagged

### P3 (accusation p2a_off, 825 lines)
- 2nd-longest probe
- 370 denies (highest deny count among accusation variants)
- Annotated version (P3_ANNOTATED) caps confessions at 30 in event log
  → annotation hides 94 confessions from view
- **Recommendation**: pilot eval may show evaluator confusion on this probe;
  cap-aware revision in v2 annotated format could help

### P6 (scarcity p2a_off, 979 lines)
- **Longest probe by far** (979 lines)
- 447 denies (highest deny count)
- Annotated version caps at 30 → hides 112 confessions
- **Recommendation**: same as P3; consider longer cap or summary stats
  in annotated format

### P4, P5 (sacred baseline, ~200 lines)
- **Shortest probes**
- Annotated version may feel "too sparse" — evaluator could mistake
  sparseness for "FLAT" arc
- **Recommendation**: monitor Q4a answers for these probes; if "FLAT"
  dominates, investigate whether annotated format should include
  proportional content density

---

## 5. What I did NOT compute (H2)

- **Per-agent shame trajectory variance**: requires reading state snapshots
  (already in original probes but not aggregated)
- **Cross-tick confession rate**: requires tick-bucketed parsing
- **Cohort recovery rate from probe data**: annotated probes already provide
  cohort outcome labels
- **Inter-probe entropy / information content**: would need text-based
  Shannon entropy computation
- **Cross-correlation between event types**: requires more sophisticated
  parsing

These are deferred. Step B4 forbidden list does NOT prohibit deeper analysis
but each adds complexity for marginal gain at this stage.

---

## 6. What could still be wrong (H4)

### 6.1 grep count accuracy
Counts use `grep -c "event_id"` which counts lines containing the string.
If a line contains the string in description (not as event ID), count is
inflated. Spot-check shows event log lines have format `t=N event_id` so
substring match should be accurate, but not formally validated.

### 6.2 Single-seed observations
sham_mul_0.8 dampening (§2.5) is N=1 per scenario. Could be seed variance.

### 6.3 Outlier identification is qualitative
"Longest", "shortest" outlier flagging uses no formal threshold. Could pick
2-stdev cutoff for rigor.

### 6.4 Anchor predictions are speculative
§3 anchor predictions ("evaluator confusion may correlate with line count")
are hypotheses, not validated claims. Pilot results will test them.

### 6.5 Confess-forgive 1:1 might break in edge cases
Claim is structural (every confess → forgiveness_emitted). If a future
content config disables this coupling (currently only Phase 2a-related toggles
exist), the 1:1 invariant breaks. Static code grep would confirm; not done
this iter.

---

## 7. Directive compliance check

§6 forbidden items respected:
- [x] No Phase 2a drilling (post-hoc count, not new ablation)
- [x] No shame multiplier sweep (just observation of existing variants)
- [x] No shame_decay implementation
- [x] No neural probe
- [x] No new variables added
- [x] No new named scenario extension
- [x] No universality claims (cross-probe pattern is structural, not universal)
- [x] No Branch C entry

---

## 8. Decision

**Provisional value: medium**. This characterization gives evaluator
objective anchors for Q-set answers and flags 4 outlier probes for v2
annotated format consideration.

**Permanence: low**. As pilot/full eval results arrive, this baseline gets
superseded by actual evaluator data. Treat as scaffolding, not load-bearing.

---

## 9. References

- `docs/b_direction/readability_probes/P{1-12}.txt` — source files
- `docs/b_direction/READABILITY_BLIND_GROUND_TRUTH.md` — P-to-scenario mapping
- `scripts/b_direction/generate_readability_probes.py` — `PROBES_GROUND_TRUTH`
- `docs/b_direction/ANNOTATED_PROBE_FORMAT.md` §6 — fields not yet in
  annotated format (this characterization could inform that list)
- `docs/b_direction/READABILITY_BLIND_PROTOCOL_V2.md` §5 branch decision
  rules — pilot-mode and full-mode thresholds
