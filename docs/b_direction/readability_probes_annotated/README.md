# Annotated Readability Probes (Provisional Standard)

This directory contains 12 annotated supplement probes (P1_ANNOTATED.txt -
P12_ANNOTATED.txt) that pre-compute cohort outcomes, pressure events,
crowd-blame trajectory, and 50-tick-window event grouping for the
WITNESS readability blind eval set.

**Format spec:** `../ANNOTATED_PROBE_FORMAT.md`
**Generator:** `scripts/b_direction/generate_annotated_probes_all.py`
**Originals (blind-eval set):** `../readability_probes/P1.txt` - `P12.txt`

## Use cases

1. **Hybrid eval** -- mix originals + annotated, compare reader Q1/Q1b
   detection rates (per Iter 163 Option B).
2. **Pilot eval** -- run a 4-probe pilot (per Step A2 directive) before
   committing to full 12-probe blind.
3. **Reference / training** -- show evaluator what the kernel produces
   before they read originals.

## Caution

These files may LEAK ground truth (cohort labels + arc classification
hint at scenario). Do NOT use as primary blind-eval material; use only
as supplementary or post-eval comparison.

## Probe-to-scenario mapping

Same as originals (deterministic shuffle: `random.Random(42)`). See
`PROBES_GROUND_TRUTH` in `scripts/b_direction/generate_readability_probes.py`
for the canonical mapping.
