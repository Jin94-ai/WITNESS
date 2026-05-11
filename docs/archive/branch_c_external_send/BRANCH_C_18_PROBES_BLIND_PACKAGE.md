# Branch C — 18 New Probes Blind Eval Package (GPT-5.5)

**Date:** 2026-04-28
**Source:** Branch C 1차 evidence (S5+S4 18 probes)
**Status:** Send-ready (post LOOP-update with cross-seed disclosure + 3 external questions + anonymization note)
**Companion:**
- `BRANCH_C_S5_RESULTS.md` (placement variation)
- `BRANCH_C_S4_RESULTS.md` (cast composition)
- `BRANCH_C_FIRST_EVIDENCE_SUMMARY.md` v4.4 (combined + cross-seed walkback)
- **`BRANCH_C_GPT55_SEND_CHECKLIST.md`** (this package send 점검)
- **paper `PAPER_DRAFT_V06.md` §6.9 + §7.4 + Appendix G** (full ensemble characterization)

---

## 0. CRITICAL DISCLOSURE — Read before evaluating

**Seed=0 conditioning**: All 18 probes were generated at `PYTHONHASHSEED=0`. Post-generation cross-seed re-test (Branch C v4.4, paper §7.4) revealed that per-dimension configuration-sensitivity ratios are biased ±33pp by single-seed conditioning:

| Slice | seed=0 (this package) | 5-seed ensemble | Δ |
|---|---:|---:|---:|
| S5 placement | 67% | 44% | -23pp |
| S4 cast composition | 67% | 56% | -11pp |
| (S3 event density, S2 scarcity depth not in this package) | | | |

→ **The 18 probes here represent a single-seed snapshot**. The configuration-sensitivity claim is paper-validated at *modal level* across 5 seeds (Appendix G), but individual probe outcomes within (scenario, configuration) cells vary across seeds.

**External-question implication**: GPT-5.5 should be able to detect *that* configuration matters. The *exact magnitude* of sensitivity (67%, 44%, etc.) is bias-prone to seed=0 — that magnitude is not the eval target.

---

## 1. Why this blind eval

Per `BRANCH_C_FIRST_EVIDENCE_SUMMARY.md` §7 option (c): blind validation of the configuration sensitivity claim by external evaluator (GPT-5.5).

Claim under test: "WITNESS dynamics are configuration-dependent — final-summary outcome depends on (cast × placement × scenario × events)."

If true, GPT-5.5 should:
1. Read 18 new probes (without knowing they are config variants)
2. Find that **same scenario** (e.g., all 6 accusation probes) produces **different final-summary outcomes**
3. Note the configuration as a likely cause

If GPT-5.5 misses this and treats all probes as same scenario type, the claim is undermined.

### 1.1 Three external questions (the ones we want answered)

Beyond the structured Q-set per probe, please answer these three at the end:

**Q-EXT 1.** Reading these 18 probes blind, *do you detect that configuration variation* (cast composition, spatial placement, etc.) is producing the outcome differences within the same scenario type? If yes, which dimension is most explanatory? If no, what alternate mechanism (random noise, measurement artifact, scenario misidentification) better explains the variation?

**Q-EXT 2.** For the 6 accusation probes (or 6 scarcity probes, or 6 sacred probes — whichever is largest in your inferred grouping), are there ≥2 distinct final-summary outcomes within the group? If yes, this supports the project's "configuration-dependent dynamics" claim.

**Q-EXT 3.** Methodological feedback: the project notes that single-seed snapshots can bias per-dimension sensitivity ratios by ±33pp (paper §7.4 / cross-seed walkback). Given you're reading a single-seed snapshot here, do you have any concern that the apparent variation is *seed artifact* rather than configuration effect? (We have separate cross-seed evidence; this question is about whether the 18-probe sample alone is convincing.)

---

## 2. Evaluator instructions (paste as system message)

```
You are an external readability evaluator for the WITNESS project. Your task
is to read 18 simulation probes (all annotated v3 format) and answer a
structured Q-set per probe, then produce aggregates.

Hidden context: Each probe is one 50-tick (or 200-tick, see header) slice of
a multi-agent simulation. The scenario type, cast composition, and spatial
placement are hidden — you must infer them from the data.

Rules:
1. Treat this as blind: do not search prior context.
2. For each probe, fill all 12 columns of the Q-set table.
3. The "Final summary" headline is visible at top of each probe — DO NOT
   copy it as your self-call until you've inferred from cohort outcomes
   first. Treat self-call as label-intuition check, not pure blind.
4. Q6a confusion notes: tag each with [FORMAT] / [STRUCTURE] / [Q_SET] /
   [SCOPE] / [OTHER] before free text.
5. After all 18 probes, group by inferred scenario type (e.g., "accusation
   probes", "scarcity probes", "sacred probes") and report:
   - How many distinct final-summary outcomes within each scenario group?
   - Which probes diverge from the group's modal outcome?
   - Hypothesis for what drives within-scenario divergence (cast / placement
     / events / horizon)

Q-set + score rule: see PROTOCOL section below.
```

---

## 3. Q-set + score rule (verbatim from PROTOCOL_V2)

| Q | Topic | Options |
|---|---|---|
| Q1 | Flow vs noise | RANDOM / FLOW_HINT / CLEAR_FLOW |
| Q1b | Readability confidence | CAN_EXPLAIN / PARTIAL_EXPLAIN / CANNOT_EXPLAIN |
| Q2a | Primary pressure | shame / fear / sacred / scarcity / accusation / grief / none |
| Q2b | Secondary pressure | (same as Q2a) / none_secondary |
| Q2c | Pressure clarity | CLEAR / MIXED_BUT_READABLE / VAGUE / UNREADABLE |
| Q3a | Relation/group level | NONE / LOCAL_SHIFT / COHORT_SHIFT / RESTRUCTURE |
| Q3b | What changed most (multi) | interpersonal / group_alignment / crowd_mood / authority / public_attention |
| Q4a | Primary arc | NO_ARC / FLAT / ESCALATION / RECOVERY / MIXED / CYCLIC |
| Q4b | Arc strength | WEAK / MODERATE / STRONG |
| Q5a | Oscillation type | NO_OSC / MEANINGLESS_NOISE / WEAK_RHYTHM / CLEAR_CYCLE |
| Q5b | Narrative contribution | HELPS / NEUTRAL / HURTS |

**Score**:
- **Readable**: Q1=CLEAR_FLOW AND Q1b ∈ {CAN_EXPLAIN, PARTIAL_EXPLAIN} AND Q4a ≠ NO_ARC AND Q2c ∈ {CLEAR, MIXED_BUT_READABLE}
- **Partially readable**: Q1=FLOW_HINT OR (Q1=CLEAR_FLOW AND Q1b=CANNOT_EXPLAIN) OR Q2c=VAGUE
- **Unreadable**: Q1=RANDOM OR Q4a=NO_ARC OR Q2c=UNREADABLE

---

## 4. Materials (18 probes, in suggested reading order)

### S5 placement variation (9 probes)

```
docs/b_direction/readability_probes_placement/P_PV_01.txt  (accusation/original)
docs/b_direction/readability_probes_placement/P_PV_02.txt  (accusation/inverted)
docs/b_direction/readability_probes_placement/P_PV_03.txt  (accusation/clustered)
docs/b_direction/readability_probes_placement/P_PV_04.txt  (scarcity/original)
docs/b_direction/readability_probes_placement/P_PV_05.txt  (scarcity/inverted)
docs/b_direction/readability_probes_placement/P_PV_06.txt  (scarcity/clustered)
docs/b_direction/readability_probes_placement/P_PV_07.txt  (sacred/original)
docs/b_direction/readability_probes_placement/P_PV_08.txt  (sacred/inverted)
docs/b_direction/readability_probes_placement/P_PV_09.txt  (sacred/clustered)
```

### S4 cast composition variation (9 probes)

```
docs/b_direction/readability_probes_cast/P_CV_01.txt  (accusation/full)
docs/b_direction/readability_probes_cast/P_CV_02.txt  (accusation/no_authority)
docs/b_direction/readability_probes_cast/P_CV_03.txt  (accusation/no_outsider)
docs/b_direction/readability_probes_cast/P_CV_04.txt  (scarcity/full)
docs/b_direction/readability_probes_cast/P_CV_05.txt  (scarcity/no_authority)
docs/b_direction/readability_probes_cast/P_CV_06.txt  (scarcity/no_outsider)
docs/b_direction/readability_probes_cast/P_CV_07.txt  (sacred/full)
docs/b_direction/readability_probes_cast/P_CV_08.txt  (sacred/no_authority)
docs/b_direction/readability_probes_cast/P_CV_09.txt  (sacred/no_outsider)
```

**Note for evaluator (anonymization)**: Probe filenames (`P_PV_NN`, `P_CV_NN`) directly encode variant type (PV = placement variant, CV = cast variant). For strictly blind eval, **treat the IDs as anonymous P_NEW_01..P_NEW_18 in the order listed above** — do not derive variant type from the filename, infer it from the probe content. Lee can also rename files before sending if preferred; both options yield equivalent eval.

---

## 5. Answer template (paste as response format)

```markdown
# Branch C 18 New Probes — GPT-5.5 Eval Results

## §1 Per-probe Q-set table

| Probe | Q1 | Q1b | Q2a | Q2b | Q2c | Q3a | Q3b | Q4a | Q4b | Q5a | Q5b | Score |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P_PV_01 | ? | ... |
| ...18 rows...

## §2 Final summary self-call (with headline label visible)

| Probe | Self-call (before peeking) | Headline label | Match? |
|---|---|---|---|
| P_PV_01 | ? | ? | ? |
| ...18 rows...

## §3 Within-scenario divergence analysis

After grouping probes by inferred Q2a (scenario type):

### Group A: probes inferred as "accusation" (Q2a = accusation)
- Probes: [list]
- Final summary outcomes: [list]
- Distinct outcomes: N
- Modal: [most common]
- Divergent: [probes that differ from modal]
- Hypothesis for divergence: [free text]

### Group B: probes inferred as "scarcity"
... (same format)

### Group C: probes inferred as "sacred"
... (same format)

## §4 Aggregates

- Readable rate (18): N/18
- Q1=CLEAR_FLOW: N/18
- Q1b=CAN_EXPLAIN: N/18
- Q2a primary pressure distribution: shame X / scarcity X / sacred X / accusation X / ...
- Q3b world-side axes selected (multi-select sums):
  - interpersonal: N
  - group_alignment: N
  - crowd_mood: N
  - authority: N
  - public_attention: N

## §5 Configuration sensitivity verdict

Did within-scenario divergence (§3) suggest configuration-dependent dynamics?
- [ ] STRONG — multiple distinct outcomes within each scenario group
- [ ] MODERATE — some scenario groups show divergence, others not
- [ ] WEAK — most probes within group share modal outcome
- [ ] NONE — all probes within group share single outcome

If STRONG or MODERATE: which configuration dimension (cast vs placement vs
something else) seems most explanatory?

## §6 Cross-probe observations (free text)
```

---

## 6. Ground truth (DO NOT share with GPT-5.5)

For post-eval comparison only.

| Probe | Source slice | Scenario | Variant | Final summary GT |
|---|---|---|---|---|
| P_PV_01 | S5 | accusation | original | RECOVERY_DOMINATED |
| P_PV_02 | S5 | accusation | inverted | SATURATION_DOMINATED |
| P_PV_03 | S5 | accusation | clustered | RECOVERY_DOMINATED |
| P_PV_04 | S5 | scarcity | original | SATURATION_DOMINATED |
| P_PV_05 | S5 | scarcity | inverted | RECOVERY_DOMINATED |
| P_PV_06 | S5 | scarcity | clustered | PARTIAL |
| P_PV_07 | S5 | sacred | original | RECOVERY_DOMINATED |
| P_PV_08 | S5 | sacred | inverted | SATURATION_DOMINATED |
| P_PV_09 | S5 | sacred | clustered | LOW_ACTIVITY |
| P_CV_01 | S4 | accusation | full (n=10) | MIXED |
| P_CV_02 | S4 | accusation | no_authority (n=8) | RECOVERY_DOMINATED |
| P_CV_03 | S4 | accusation | no_outsider (n=9) | MIXED |
| P_CV_04 | S4 | scarcity | full (n=12) | SATURATION_DOMINATED |
| P_CV_05 | S4 | scarcity | no_authority (n=9) | RECOVERY_DOMINATED |
| P_CV_06 | S4 | scarcity | no_outsider (n=10) | RECOVERY_DOMINATED |
| P_CV_07 | S4 | sacred | full (n=8) | PARTIAL |
| P_CV_08 | S4 | sacred | no_authority (n=7) | RECOVERY_DOMINATED |
| P_CV_09 | S4 | sacred | no_outsider (n=7) | RECOVERY_DOMINATED |

**Configuration sensitivity ratio**: 12/18 probes diverge from baseline (67%).

---

## 7. Post-eval validation criteria

GPT-5.5 returns answers → check:

| Criterion | PASS condition |
|---|---|
| Within-scenario divergence detected | §3 reports ≥2 distinct outcomes in ≥2 of 3 scenario groups |
| Configuration sensitivity verdict | §5 = STRONG or MODERATE |
| Q2a-typing accuracy vs GT | ≥15/18 (≥83%) |
| Final summary self-call vs GT | ≥12/18 (≥67%, lower threshold since variants make it harder) |
| Q3b world-side axes positive | ≥3 of 5 axes selected on majority of probes |

→ If 4/5 PASS, configuration sensitivity claim **externally validated**.

---

## 8. Versioning

| Version | Date | Note |
|---|---|---|
| v1 (this) | 2026-04-28 | Package ready post Branch C 1차 evidence (S5+S4). |
