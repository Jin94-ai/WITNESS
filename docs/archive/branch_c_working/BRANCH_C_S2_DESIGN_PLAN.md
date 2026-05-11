# Branch C — S2 Scarcity Depth Design Plan

**Date:** 2026-04-28
**Source:** `BRANCH_C_DESIGN_DRAFT.md` §3 S2 (scarcity depth expansion)
**Prep for LOOP 69 fast execution.**

---

## 1. Hypothesis under test

Per master plan §3 S2: "scarcity에서 location placement variation + authority_vigilance 추적 강화".

**Refined hypothesis** (after S5 already covered scarcity placement): Does the scarcity SATURATION outcome depend on (event count × crowd density), with authority_vigilance as a measurable mediator?

**Why this is informative**:
- S5 showed scarcity inverted (granary↔poor_quarter swap) flips SATURATION→RECOVERY
- S4 showed scarcity no_authority → RECOVERY
- Open: does **event count alone** flip outcome, holding cast + placement at baseline?
- Open: does **crowd density alone** flip outcome?

## 2. Variants (9 probes)

Fixed: scarcity scenario, baseline cast (n=12), baseline placement (S5 original), seed=0, 200 ticks.

3 event counts × 3 crowd densities:

| Probe | Events | Crowd density (marketplace, poor_quarter) |
|---|---|---|
| P_S2_01 | 1 accusation only        | low (0.3, 0.2) |
| P_S2_02 | 1 accusation only        | baseline (0.7, 0.5) |
| P_S2_03 | 1 accusation only        | high (0.9, 0.8) |
| P_S2_04 | 2 accusations (t5, t40)  | low |
| P_S2_05 | 2 accusations (t5, t40)  | baseline |
| P_S2_06 | 2 accusations (t5, t40)  | high |
| P_S2_07 | 3 accusations (t5, t40, t100) | low |
| P_S2_08 | 3 accusations (t5, t40, t100) | baseline |
| P_S2_09 | 3 accusations (t5, t40, t100) | high |

All include: 1 guard_approaches @ t15, 1 misdeed rumor.

## 3. Predicted outcomes (Claude bias)

- **Density-dominated**: low density → RECOVERY 3/3 (insufficient crowd for blame propagation)
- **Event count + density interaction**: high density × 3 accusations → SATURATION strongest
- **Authority vigilance**: should track event count (more accusations = more vigilance peaks)

If predictions match: validates "scarcity SATURATION is event-density-mediated, not just present-or-absent".
If predictions break: reveals hidden coupling.

## 4. Configuration sensitivity expectation

Branch C 1차 has 67%/67%/22% per dimension. S2 expectation:
- If event count and crowd density are *both* strong (cf. cast/placement): ~50-67%
- If one is dominant, other weak: ~33-44%
- If neither flips outcome: <22% — surprising, would suggest scarcity SATURATION is **scenario-locked**

## 5. Implementation plan (next LOOP)

```
1. Copy template: scripts/b_direction/generate_event_density_variations.py (S3 generator)
2. Modify for scarcity:
   - scenario fixed = scarcity
   - cast = baseline (build_scarcity_cast)
   - placement = S5 original
   - vary seed_events list (1/2/3 accusations)
   - vary crowd density (low/baseline/high)
3. Output: docs/b_direction/readability_probes_scarcity_depth/P_S2_{01-09}.txt
4. Validate: extend validate_annotated_v4.py
5. Document: BRANCH_C_S2_RESULTS.md
6. Update FIRST_EVIDENCE_SUMMARY to v3 (36 probes)
```

Estimated: 1 LOOP (360s) — code clone + regen + validate + doc.

## 6. Forbidden_now check

| Action | Engine touch | Status |
|---|---|---|
| Vary seed_events list | NO | safe |
| Vary CrowdState density param | NO (state init only) | safe |
| Use existing `build_scarcity_cast` | NO | safe |
| Reuse v4 surfacing logic | NO | safe |

→ S2 fully autonomous-mode safe per master plan §8.
