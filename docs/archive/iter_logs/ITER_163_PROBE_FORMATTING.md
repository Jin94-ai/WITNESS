# Iter 163 -- Annotated Probe Formatting Prototype

**Date:** 2026-04-26
**Iteration:** Iter 163
**Severity:** LOW -- readability infrastructure improvement

---

## 0. Summary

Per directive `WITNESS_READABILITY_Q_IMPROVEMENTS_AND_NEXT_DIRECTION.md`
§6 improvement point 5 (Readability-facing representation),
prototyped an enhanced probe formatter with **headline summary**
+ **cohort breakdown** + **event grouping**.

Generated ONE example: `docs/b_direction/readability_probes/P_ANNOTATED_DEMO.txt`

If Lee approves the format, it can be applied to all 12 probes
via update to `generate_readability_probes.py`.

---

## 1. The 4 enhancements (per directive §6 point 5)

### 1.1 Dominant pressure summary
Top of probe shows:
- Number of accusations + targets
- Number of confessions + forgiveness rumors
- Crowd blame trajectory

### 1.2 Cohort delta highlighting
Per-location cohort arc summary:
```
[L1 cohort]:  saturation: peak~10.0 → final~9.8 (stuck)
[L2 cohort]:  recovery: peak~10.0 at t=28 → final~2.7
[L3 cohort]:  no shame accumulation
```

This directly addresses Iter 138's per-cohort framing finding
(population mean masks cohort variance).

### 1.3 Event grouping
Events grouped by 50-tick windows instead of flat timeline:
```
--- Tick 0-49 ---
  t=  3  accusation against disciple_follower
  t=  7  accusation against outsider
  t= 23  confession by A5 (enforcer)
  ...
--- Tick 50-99 ---
  ...
```

Reader can navigate by phase, not scan endless tick lines.

### 1.4 Compact summary of key shifts
Crowd-level dynamics summarized:
```
Crowd blame total:   peak 1.2 at t=22 → final 0.2
```

Shows world-side process trajectory without listing every blame_concentration update.

---

## 2. Comparison: original vs annotated

### Original probe (P10.txt, Iter 120 anonymization)
- ~415 lines per probe
- Flat event log (every tick with significant event)
- State snapshots at 50-tick intervals
- No cohort summary
- No per-cohort arc classification
- Reader must mentally compute trajectories

### Annotated probe (P_ANNOTATED_DEMO.txt, Iter 163)
- ~80 lines (much more compact)
- Headline summary (10 lines) gives whole probe in 30 seconds
- Cohort arc classification done for evaluator
- Event grouping by phase
- Reader can verify headline against detailed log if needed

---

## 3. Connection to Step C readability eval

The directive's readability protocol is BLOCKED on Lee's blind eval.
Annotated probes might:
- Make 1-2 hour eval easier (faster reading)
- Give clearer signal on Q1 (flow detection) and Q1b (explanation)
- Help with Q3b (world-side perception) by surfacing crowd_blame_total
- Help with Q4a (arc type) by classifying cohort arcs explicitly

But CAUTION: annotated probes might LEAK information about kernel
dynamics that the original probes intentionally hide. The original
12 probes were designed to test if evaluators DETECT structure
without help. Annotated probes test if evaluators CAN UNDERSTAND
when structure is presented.

These are DIFFERENT tests:
- Original: "does the kernel produce externally readable flow?"
- Annotated: "given the kernel produces flow, is it presentable to evaluators?"

Both useful but distinct. Lee should decide which to use for which
purpose.

---

## 4. Recommended next step for Lee

Three options:

### Option A: Use annotated format for blind eval
Replace 12 probes with annotated versions. Faster eval, clearer
signal. But risks evaluator getting "obvious answers" from headline
summaries (defeats blind purpose).

### Option B: Hybrid -- annotated for one half, original for other
Run blind eval on 6 original + 6 annotated probes. Compare:
- Did evaluator correctly classify scenario in original vs annotated?
- Did Q1/Q1b answers differ?
- This isolates "structure detection" vs "structure presentation".

### Option C: Keep original 12, use annotated as separate "case study"
Original 12 = blind eval (current plan). Annotated demos = teaching
material to show what the kernel produces when explained.

I lean toward **Option C** -- preserves blind eval integrity,
adds annotated probes as supplementary documentation. Lee decides.

---

## 5. Implementation cost (if Lee approves)

If Option A or B is chosen, modify `generate_readability_probes.py`:
- Add `make_annotated_probe()` function (~80 lines, mostly already
  prototyped in `generate_annotated_probe.py`)
- Add CLI flag `--annotated` to choose format
- Regenerate probes with annotated format

If Option C, the prototype script `generate_annotated_probe.py`
already exists. Optionally generate annotated versions for all 12
scenarios (12 files × ~80 lines each = ~10 min compute).

---

## 6. What could still be wrong (H4)

- Headline summary uses my judgment for "saturation" / "recovery"
  / "partial" classification. Different thresholds could change
  labels.
- Cohort grouping is by location_id; might miss cross-location
  cohort dynamics.
- Tick-window grouping (50-tick) is arbitrary; events at boundaries
  might span windows awkwardly.
- The peak/final classification is from the same logic that produced
  Iter 142 no-shame artifact. Need to verify peak >= 1.5 threshold
  in annotated headline before claiming "saturation" vs "no shame".
- This is ONE example (accusation seed=0). Other scenarios might
  need different cohort grouping.

---

## 7. What I did NOT try (H2)

- Generate annotated versions for all 12 probes (waiting Lee approval)
- Modify generate_readability_probes.py directly (would invalidate
  existing P1-P12)
- Test annotated probe with mock evaluator
- Add Q3b-relevant fields explicitly (group_alignment, public_attention)
- Compare with original P10.txt side-by-side

---

## 8. Conclusion

**Annotated probe formatting prototype demonstrates** all 4
enhancements requested by directive §6 point 5:
- dominant pressure summary
- cohort delta highlighting
- event grouping
- compact summary of key shifts

**Output**: 80-line annotated probe vs 415-line original. ~5x
more compact while preserving detail.

**Decision pending**: Lee should choose how/whether to apply this
format -- blind eval (loses some blindness), hybrid (mixes
blind/annotated), or supplementary (preserves original 12).

**Per directive instruction "실험이 끝날때마다 결과를 회고"**:
this experiment shows that probe presentation IS a separate
dimension from kernel mechanism. The kernel produces complex
dynamics; how those dynamics are presented to evaluators
significantly affects readability. Iter 163 prototype shows
the kernel IS presentable -- the question is whether to use
this for blind eval or only for explanation.

**No engine changes**, no architectural changes. Pure presentation
prototype.
