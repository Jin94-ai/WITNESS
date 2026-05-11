# Iter 166 -- Annotated Probe Set Complete (12/12)

**Date:** 2026-04-26
**Iteration:** Iter 166
**Severity:** LOW -- presentation infrastructure deliverable

---

## 0. Summary

Per directive `WITNESS_READABILITY_Q_IMPROVEMENTS_AND_NEXT_DIRECTION.md`
§6 improvement 5 (readability-facing representation), extended Iter 163
prototype to all 12 probes.

**Deliverables**:
- Original 12: `P1.txt` - `P12.txt` (preserved for blind eval)
- Annotated 12: `P1_ANNOTATED.txt` - `P12_ANNOTATED.txt` (supplementary)

Both sets stored in `docs/b_direction/readability_probes/`.

---

## 1. Annotated probe structure

Each annotated probe has 3 sections:

### 1.1 Headline summary
- Per-cohort outcomes (location-grouped agents):
  - "recovery", "saturation", "partial", or "no shame accumulation"
  - peak shame + final shame summary per cohort
- Pressure events + recovery actions counts
- World-level blame trajectory (peak + final)

### 1.2 Agents/locations header
Same as original probes (anonymized roles + L1/L2/L3 locations)

### 1.3 Event log grouped by 50-tick windows
Events organized into Tick 0-49, 50-99, 100-149, 150-199 sections
for navigation by phase rather than flat timeline.

---

## 2. Use cases

### Option A: Hybrid blind eval (per Iter 163 Option B)
Run blind eval on 6 original + 6 annotated. Compare:
- Did annotation help evaluator answer Q1/Q1b correctly?
- Did Q3b world-side categories appear more in annotated?

This isolates "structure detection" from "structure presentation".

### Option B: Annotated as supplementary reference (per Iter 163 Option C)
Lee uses annotated probes to:
- Train evaluators on what kernel produces
- Verify ground truth scenarios after blind eval
- Onboard external reviewers without full mechanism knowledge

### Option C: Pre-eval comparison
Lee reads annotated first to understand kernel behavior, then runs
blind eval on originals to test their own detection ability.

---

## 3. Connection to Iter 163-165 cumulative findings

Iter 163-165 trio established:
- **Iter 163**: probe presentation matters (annotated vs flat)
- **Iter 164**: kernel has rich autonomous activity (4/4 signals)
- **Iter 165**: meso fields strongly cross-coupled (7/10 pairs)

Combined insight: **the kernel produces rich, coupled, autonomous
dynamics** -- but original probes don't surface this clearly.
Annotated probes (Iter 163, 166) directly address the gap.

---

## 4. Implementation cost

This iter: ~150 lines new script (`generate_annotated_probes_all.py`)
that imports the existing `generate_readability_probes.py` ground
truth + build_world. Generates 12 annotated probes in ~30 seconds.

If Lee approves, the original `generate_readability_probes.py`
could be modified to add a `--annotated` flag. Currently the two
scripts are separate.

---

## 5. What could still be wrong (H4)

- Anonymization: the L1/L2/L3 mapping is dict-insertion-order
  dependent. Different scenarios may map locations differently
  in annotated vs original -- could be confusing for evaluator
  comparison.
- Cohort summary uses my judgment thresholds (peak < 1.5 = no shame,
  final < 4 + peak >= 5 = recovery, etc.). Different thresholds
  could change labels.
- Confession listing capped at 30 per probe; some probes have 70+
  confessions, so some get truncated.
- Annotated probes might LEAK ground-truth (cohort outcomes are
  named; evaluator could deduce scenario from cohort distribution).
  Should be used for non-blind purposes only.

---

## 6. What I did NOT try (H2)

- Generate annotated probes with multiple horizon windows (only 50t)
- Add visual ASCII chart of shame trajectory
- Color/format markup
- A/B test annotated vs original with mock evaluator
- Modify generate_readability_probes.py to add --annotated flag

---

## 7. Conclusion

**12 annotated probes generated** as supplement to original 12 blind
eval probes. Decision pending: Lee chooses whether to use as
supplementary reference (Option B), hybrid eval (Option A), or
pre-eval comparison (Option C).

**Per directive instruction "결과를 회고하고 프로젝트 자체를 더 나은
방향으로 개선"**:

The cumulative Iter 161-166 work has produced a clear project-direction
insight: **investing in presentation/representation is now higher
leverage than kernel mechanism work**.

Specifically:
- Mechanism work (Iter 161 spatial disengagement) hits structural
  ceilings without new kernel rules
- Cleanup work (Iter 162 inert audit) confirms 5 RESERVE candidates
  but no production gain
- Autonomy work (Iter 164) shows kernel is already autonomous
- Coupling work (Iter 165) shows meso fields already cross-correlated
- **Presentation work (Iter 163, 166) directly addresses the visibility
  gap**

**Project improvement recommendation**: invest in Branch A-style
presentation work (annotated probes, headline summaries, cohort
breakdowns) rather than Branch B-style kernel additions or new
mechanisms. The kernel is rich; readers need help seeing it.

This is consistent with the directive's emphasis on Step C readability
as the primary blocker.
