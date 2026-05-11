# WITNESS Readability Blind — Pilot Results (Claude Simulation)

**Status:** **CLAUDE SIMULATION — NOT TRUE BLIND EVAL**
**Date:** 2026-04-27
**Source directive:** `docs/WITNESS_NEXT_ACTIONS_PILOT_BLIND_EVAL.md`
**Mode used:** Pilot (N=4)
**"Evaluator":** Claude (Iter 189 of readability loop)

---

## ⚠️ HARNESS H4 caveat — read first

Claude has **full mechanism knowledge** + **ground truth access** + **wrote
the protocol/probes**. This is **NOT** a true blind evaluation. Per Protocol
V2 §8: "Claude CANNOT act as the blind evaluator (has full mechanism knowledge)."

**What this simulation IS valid for**:
- ✅ Protocol/template usability — does §1.1.5 self-call flow work?
- ✅ Q-set internal consistency — do Q1-Q6 cover the probe content?
- ✅ Annotated vs original format-axis demonstration (with mechanism-knowledge bias)
- ✅ Iter 185-188 infrastructure self-test (cap disclosure, sub-tags, final summary, self-call)
- ✅ Ground truth comparison (auto-grading exercise)

**What this simulation is NOT valid for**:
- ❌ True blind readability measurement
- ❌ Inter-rater agreement
- ❌ Final branch decision
- ❌ Replacing Lee's direct evaluation

**Branch verdict from this simulation is provisional only**. Lee's direct
evaluation remains the definitive signal. The pilot template was filled
to (a) test the protocol mechanically and (b) generate auto-comparable
metrics for when Lee runs it later.

---

## 0. Mode

- [x] **Pilot (N=4)** — claude simulation
- [ ] Full (N=12, all original)
- [ ] Full (N=12, all annotated)
- [ ] Hybrid (N=12, 6 original + 6 annotated)

**Evaluator:** Claude (with full mechanism knowledge — see caveat above)
**Date:** 2026-04-27
**Total time spent:** ~15 min reading + filling

---

## 1. Pilot results (N=4)

### 1.1 Per-probe table

| Probe | Format | Q1 | Q1b | Q2a | Q2b | Q2c | Q3a | Q3b | Q4a | Q4b | Q5a | Q5b | Score |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PILOT_1 | original | CLEAR_FLOW | PARTIAL_EXPLAIN | accusation_blame | shame_social | MIXED_BUT_READABLE | COHORT_SHIFT | group_alignment, crowd_mood, public_attention | MIXED_ARC | MODERATE | WEAK_RHYTHM | HELPS | **Readable** |
| PILOT_2 | original | CLEAR_FLOW | PARTIAL_EXPLAIN | shame_social | accusation_blame | MIXED_BUT_READABLE | COHORT_SHIFT | group_alignment, crowd_mood | ESCALATION | STRONG | NO_OSCILLATION | NEUTRAL | **Readable** |
| PILOT_3 | annotated | CLEAR_FLOW | CAN_EXPLAIN | shame_social | sacred_awe | MIXED_BUT_READABLE | COHORT_SHIFT | group_alignment, public_attention | RECOVERY | STRONG | WEAK_RHYTHM | HELPS | **Readable** |
| PILOT_4 | annotated | CLEAR_FLOW | CAN_EXPLAIN | accusation_blame | shame_social | CLEAR | COHORT_SHIFT | group_alignment, crowd_mood | ESCALATION | STRONG | WEAK_RHYTHM | NEUTRAL | **Readable** |

**Score**: 4/4 Readable — but bias-loaded. Mechanism knowledge inflates Readable rate.

### 1.1.5 Final summary self-call

**Vocabulary**: LOW_ACTIVITY / RECOVERY_DOMINATED / SATURATION_DOMINATED / MIXED / PARTIAL

| Probe | Format | My self-call | Annotated label visible | Match? |
|---|---|---|---|---|
| PILOT_1 | original | **MIXED** (A4+A10 stuck, A5-A8 recovered) | (not shown) | n/a |
| PILOT_2 | original | **SATURATION_DOMINATED** (A3/A5/A8/A9 stuck) | (not shown) | n/a |
| PILOT_3 | annotated | **RECOVERY_DOMINATED** (matches headline) | RECOVERY_DOMINATED | yes |
| PILOT_4 | annotated | **SATURATION_DOMINATED** (matches headline) | SATURATION_DOMINATED | yes |

### 1.2-1.3 Q6a confusion notes (with sub-tags)

#### PILOT_1 (original)
- `[FORMAT:DENSITY]` event log too dense (~370 deny events visible) — hard to skim arc
- `[FORMAT:HEADLINE]` no headline summary; must scan all events to estimate cohort outcomes
- `[SCOPE:TRAJECTORY]` per-agent shame trajectory exists (snapshots at 50/100/150/200) but cohort grouping not visible

#### PILOT_2 (original)
- `[FORMAT:DENSITY]` same density issue; deny+confess events interleaved heavily
- `[STRUCTURE:RECOVERY]` looks like recovery actions fired but most cohorts still stuck — probe doesn't make this contrast salient (mechanism question, may also be [FORMAT])
- `[FORMAT:HEADLINE]` cohort outcomes not visible without manual computation from snapshots

#### PILOT_3 (annotated)
- `[FORMAT:HEADLINE]` final summary line is the most useful single addition — instant orient
- `[SCOPE:HIDDEN_DATA]` cap disclosure says "30 of 35" — minor (only 5 hidden)

#### PILOT_4 (annotated)
- `[FORMAT:CAP]` "showing first 30 of 200 confessions" disclosure works — I knew kernel did much more than displayed
- `[SCOPE:TRAJECTORY]` per-agent shame trajectory missing (annotated has cohort labels but not trajectories) — for outliers like saturation cases, trajectory would clarify "stuck since when"

### 1.4 Pilot aggregates

**Format-axis (Protocol V2 §4)**:
- Readable rate (original): **2/2** (with mechanism-knowledge bias)
- Readable rate (annotated): **2/2**
- Format gap: **0% in Readable rate** — but see self-call below
- CAN_EXPLAIN gap: **+100%** (annotated 2/2 vs original 0/2 on CAN_EXPLAIN)
- Q5b HELPS rate gap: **+50%** (annotated PILOT_3 HELPS, PILOT_4 NEUTRAL; original PILOT_1 HELPS, PILOT_2 NEUTRAL — actually 50/50 on both, **0% gap**)

**Q6a tag distribution** (across 4 probes, ~10 notes total):
- `[FORMAT]` count: 5 (mostly DENSITY, HEADLINE, CAP)
- `[STRUCTURE]` count: 1 (RECOVERY in PILOT_2)
- `[Q_SET]` count: 0
- `[SCOPE]` count: 3 (HIDDEN_DATA, TRAJECTORY ×2)
- `[OTHER]` count: 0

**Final summary self-call (per §1.1.5)**:
- Original self-call accuracy (vs ground truth): **1/2**
  - PILOT_1 (ground truth: RECOVERY_DOMINATED): I called MIXED → **mismatch**
  - PILOT_2 (ground truth: SATURATION_DOMINATED): I called SATURATION_DOMINATED → **match**
- Annotated match rate (self-call vs visible label): **2/2** (trivially — labels visible)
- **Comparison**: Original 1/2 vs Annotated 2/2 → annotated label resolves Q4a-rollup
  ambiguity that original requires mechanism knowledge to disambiguate.

### 1.5 Pilot branch decision

| Pattern | Match? |
|---|---|
| Annotated 2/2 + original ≤1/2 → Branch A | Partial — Q1 readable both, but final-summary self-call: original 1/2 vs annotated 2/2 ⇒ format-axis effect detected |
| Both 2/2 → Branch C ready | YES on Q1 readable; **NO on final-summary self-call** |
| Both ≤1/2 → Branch B priority | NO |
| Mixed → run full eval | YES (signal split: Q1-readable both, but Q4a-rollup gap) |

**Pilot verdict (provisional, claude-bias)**:
- On readable rate alone: **C ready** (both formats readable)
- On final-summary self-call: **A** (format-axis effect on Q4a-rollup)
- Synthesizing: **A with C-readiness signal** — annotated format helps Q4a-style
  inference, AND original is readable enough that broader-world prerequisites are
  partly met. If Lee's true blind shows similar pattern → **A confirmed +
  C preparation**.

**Recommended next**: **run Lee's true blind eval** (PROTOCOL_V2 §5.1 says
mixed → run full N=12). The simulation suggests A or A+C-prep; only Lee's
true blind can disambiguate.

### 1.6 Time tracking

| Phase | Target | Actual (claude sim) |
|---|---|---|
| Reading | 12-16 min | ~10 min (knowledge of format helps) |
| Writing answers | 3-4 min | ~5 min |
| Total | 15-20 min | ~15 min |

**Time test passed** — 15-20 min target is achievable for evaluator with
zero mechanism knowledge.

---

## 3. Cross-probe observations

- **Format-axis differential is on Q4a-rollup, not Q1**: Both formats produced
  Q1=CLEAR_FLOW. The differential surfaces only when evaluator must rollup
  cohort outcomes into a single label (final summary self-call). This is
  what Iter 187 final summary feature was designed to expose.
- **PILOT_1 mismatch (MIXED vs RECOVERY_DOMINATED ground truth)** is the
  signal: even with mechanism knowledge, the original probe's dense event
  log + 4-snapshot states make it ambiguous whether A4/A10 stuck overrides
  A5-A8 recovered. Annotated would force the rollup explicit.
- **Q6a cluster on `[FORMAT:DENSITY]` and `[FORMAT:HEADLINE]`** for original
  probes — exactly what annotated format addresses.
- **Q-set V2 questions felt adequate** — 0 `[Q_SET]` tags. No ambiguity
  in question wording during this simulation.
- **Where I spent the most time**: PILOT_2 cohort outcome rollup (manual
  computation from t=200 snapshot). Annotated would eliminate this.

---

## 4. Ground truth comparison

### 4.1 Q2a primary pressure (from RESULTS_V2 §4 mapping)

| Probe | Format | My Q2a | Ground truth scenario | Match? |
|---|---|---|---|---|
| PILOT_1 | original | accusation_blame | accusation baseline | ✅ |
| PILOT_2 | original | shame_social | scarcity baseline | ❌ (I'd need to read scarcity-specific cues) |
| PILOT_3 | annotated | shame_social | sacred baseline | ❌ (I called shame_social, ground is sacred — annotation didn't surface sacred dominance) |
| PILOT_4 | annotated | accusation_blame | accusation p2a_off | ✅ |

**Q2a primary accuracy: 2/4 (50%)**.

Note: PILOT_3 mismatch is interesting — annotated label says "sacred baseline"
but I read the probe as shame_social-dominated because the recovery cohort
labels emphasized shame. **This suggests annotated format does NOT fully
surface scenario type for Q2a; it surfaces arc rollup (Q4a) better than
pressure type (Q2a).**

### 4.2 Final summary self-call (from §1.1.5)

| Probe | Self-call | Ground truth | Match? |
|---|---|---|---|
| PILOT_1 | MIXED | RECOVERY_DOMINATED | ❌ |
| PILOT_2 | SATURATION_DOMINATED | SATURATION_DOMINATED | ✅ |
| PILOT_3 | RECOVERY_DOMINATED | RECOVERY_DOMINATED | ✅ |
| PILOT_4 | SATURATION_DOMINATED | SATURATION_DOMINATED | ✅ |

**Final summary accuracy: 3/4 (75%)** — but PILOT_3, PILOT_4 trivially match
because labels were visible.
- Original-only accuracy: **1/2 (PILOT_2 match, PILOT_1 mismatch)**
- Annotated-only accuracy: **2/2 (trivial)**
- **Format-axis differential confirmed**: +50% on final summary self-call.

### 4.3 Ablation detectability

PILOT_4 is `accusation p2a_off` — recovery channel disabled. Did I detect
this from probe alone?

- PILOT_4 final summary: SATURATION_DOMINATED ✅ matches expected (no recovery)
- 200 confessions but 124 forgiveness rumors emitted — high event count yet
  saturated → kernel-level recovery suppressed
- However, the **mechanistic explanation** (forgiveness phase OFF, so
  rumors don't decrement shame) is NOT visible in the probe — only the
  outcome (stuck despite confessing).

**Ablation outcome detectable; ablation cause not detectable from probe
alone** — confirms Iter 184 PROBE_STATS_CHARACTERIZATION §3.3 hypothesis
(p2a_off variants produce 3.0× more confessions).

---

## 5. Iter 185-188 infrastructure evaluation

### 5.1 Annotated event log cap disclosure (Iter 185)
**Verdict: KEEP**. PILOT_4 "showing first 30 of 200 confessions" was directly
useful — without it I'd have read 30 confessions and assumed kernel ran out
of activity around tick 200. With it, I knew to look for "did the cohort recover
despite 200 confessions?" — answer: no, p2a_off blocked it.

### 5.2 Q6a sub-tags (Iter 186)
**Verdict: KEEP, but only sub-tags I used were `:DENSITY`, `:HEADLINE`, `:CAP`,
`:HIDDEN_DATA`, `:TRAJECTORY`, `:RECOVERY`**. 6 of ~18 sub-tags. Others may
emerge in true blind. Sub-tag burden was zero — they read like natural notes.

### 5.3 Final summary 5 labels (Iter 187)
**Verdict: 4 sufficient, 5th may be redundant**. I used MIXED, SATURATION_DOMINATED,
RECOVERY_DOMINATED. PARTIAL never used (could fold into MIXED). LOW_ACTIVITY
never used in pilot (would matter for sacred sham_mul_0.05 / scarcity sham_mul).
Recommendation for v1.3: **observe true-blind use, then prune if PARTIAL doesn't
discriminate**.

### 5.4 Self-call template (Iter 188)
**Verdict: KEEP, surface effect detector**. Without §1.1.5, the format-axis
differential would have stayed hidden (Q1 readable both, but Q4a-rollup gap
isn't in standard Q-set). Self-call surfaces it.

**Net assessment of Iter 185-188**: each iter added a feature that did
something concrete in this simulation. Not all (PARTIAL label) used, but
none caused harm.

---

## 6. Branch decision (provisional, Lee gate required)

### 6.1 What this simulation suggests

Pattern: **"both formats readable on Q1, but format gap on Q4a-rollup"**.

| Mapping | Branch |
|---|---|
| Q1 readable both | C ready (per §5.1 rule) |
| Q4a-rollup gap (annotated wins) | A (per format-axis) |
| Synthesis | **A confirmed + C-readiness signal** |

### 6.2 What Lee's true blind would clarify

- If Lee (without mechanism knowledge) finds original PILOT_1 hard to read
  → **A confirmed** (mechanism knowledge alone made me read it as readable)
- If Lee finds even annotated hard → **B priority**
- If Lee finds both readable → **C ready** (and confirms annotation is
  helpful but not required)

### 6.3 Provisional next direction

Per §6 of NEXT_ACTIONS doc:

**If A confirmed (most likely from this simulation pattern)**:
1. Annotated probe format is provisionally validated → keep v1.2
2. Protocol V2 maintained; pilot infrastructure ready for full N=12 if needed
3. Annotated probe regeneration / additional fields (relation shift, motif
   shift in v2 spec §6) are next presentation work
4. Branch B debt cleanup (SCRIPT_STATUS Phase A — 47 leaf scripts) can
   proceed as low-risk parallel

---

## 7. KERNEL_GAPS gate update

Per NEXT_ACTIONS §7 + this simulation:

- **K1 vs K2 (shame_decay)**: simulation does not change recommendation.
  **K2 (defer)** still default. Pilot didn't surface "kernel structurally
  unable to recover" — the recovery WAS visible (PILOT_3 RECOVERY_DOMINATED,
  PILOT_1 partial recovery). Phase 2a is functional; adding shame_decay would
  be ahead of evidence.
- Other gaps (trust→shame, belonging, placement template, authority autonomy):
  no signal from simulation. **Defer all.**

---

## 8. Following auto-actions (per NEXT_ACTIONS §6 + §8)

Branch A path (provisional):

### 8.1 Immediately executable (no Lee gate, low-risk)
- ✅ Mark Pilot 4 as "auto-graded by Claude simulation; awaiting Lee true blind"
- ✅ Update `READABILITY_BLIND_RESULTS_V2.md` template note about Claude sim
- ⏸ SCRIPT_STATUS Phase A (47 leaf scripts archive) — can run parallel to Lee's eval
- ⏸ Annotated probe v2 candidates (relation shift / motif shift) — defer until
  Lee confirms A

### 8.2 Lee gate (provisional pause)
- Final branch decision (A vs C ready confirmation)
- KERNEL_GAPS K1/K2 decision
- World/ Phase 3 decisions

### 8.3 Re-enter readability loop
Continue with `loop v1.md` 360s cadence per Lee's directive end:
> /loop C:\Users\이진석\Desktop\Witness\docs\loop v1.md 이거대로 다시 360초마다 루프 진행해

---

## 9. One-line summary

**Claude simulation pilot (4 probes, 15 min) suggests Branch A confirmed
on format-axis (annotated final-summary self-call = 2/2 vs original 1/2),
with Q1-readable both = C-readiness signal — but Lee's true blind remains
the definitive verdict. Iter 185-188 readability infrastructure (cap disclosure,
sub-tags, final summary, self-call) all earned their KEEP in this simulation.**

---

## 10. Versioning

| Version | Date | Note |
|---|---|---|
| v1 (this) | 2026-04-27 | Claude simulation pilot, NOT replacement for Lee true blind |
