# WITNESS B-Direction — Readability Blind Results (v2 -- Iter 161 Q-set)

**Status:** EMPTY TEMPLATE (awaiting human evaluation)

Q-set updated per `docs/WITNESS_READABILITY_Q_IMPROVEMENTS_AND_NEXT_DIRECTION.md`.

---

## 1. Evaluation instructions

1. Read protocol: `docs/b_direction/READABILITY_BLIND_PROTOCOL.md`
2. Open each probe in `docs/b_direction/readability_probes/P1.txt` … `P12.txt`
3. For each probe, answer Q1, Q1b, Q2a-c, Q3a-b, Q4a-b, Q5a-b, Q6a-b
   BEFORE reading ground truth
4. Do NOT consult `READABILITY_BLIND_GROUND_TRUTH.md` until all 12 are done
5. Fill in tables below

---

## 2. Per-probe answers (categorical)

### Table 2.1: Q1, Q1b, Q2 (flow + pressure)

| Probe | Q1 (flow) | Q1b (explain?) | Q2a (primary) | Q2b (secondary) | Q2c (clarity) |
|---|---|---|---|---|---|
| P1 | ? | ? | ? | ? | ? |
| P2 | ? | ? | ? | ? | ? |
| P3 | ? | ? | ? | ? | ? |
| P4 | ? | ? | ? | ? | ? |
| P5 | ? | ? | ? | ? | ? |
| P6 | ? | ? | ? | ? | ? |
| P7 | ? | ? | ? | ? | ? |
| P8 | ? | ? | ? | ? | ? |
| P9 | ? | ? | ? | ? | ? |
| P10 | ? | ? | ? | ? | ? |
| P11 | ? | ? | ? | ? | ? |
| P12 | ? | ? | ? | ? | ? |

### Table 2.2: Q3, Q4, Q5 (relations / arcs / oscillation)

| Probe | Q3a (level) | Q3b (what) | Q4a (arc) | Q4b (strength) | Q5a (osc) | Q5b (narrative) |
|---|---|---|---|---|---|---|
| P1 | ? | ? | ? | ? | ? | ? |
| P2 | ? | ? | ? | ? | ? | ? |
| P3 | ? | ? | ? | ? | ? | ? |
| P4 | ? | ? | ? | ? | ? | ? |
| P5 | ? | ? | ? | ? | ? | ? |
| P6 | ? | ? | ? | ? | ? | ? |
| P7 | ? | ? | ? | ? | ? | ? |
| P8 | ? | ? | ? | ? | ? | ? |
| P9 | ? | ? | ? | ? | ? | ? |
| P10 | ? | ? | ? | ? | ? | ? |
| P11 | ? | ? | ? | ? | ? | ? |
| P12 | ? | ? | ? | ? | ? | ? |

**Q1 options**: RANDOM / FLOW_HINT / CLEAR_FLOW
**Q1b options**: CAN_EXPLAIN / PARTIAL_EXPLAIN / CANNOT_EXPLAIN
**Q2a/Q2b options**: shame_social / fear_physical / sacred_awe / scarcity_material / accusation_blame / grief_loss / none_discernible (or none_secondary for Q2b)
**Q2c options**: CLEAR / MIXED_BUT_READABLE / VAGUE / UNREADABLE
**Q3a options**: NONE / LOCAL_SHIFT / COHORT_SHIFT / RESTRUCTURE
**Q3b options** (multi-select): interpersonal_relation / group_alignment / crowd_mood / authority_presence / public_attention / not_discernible
**Q4a options**: NO_ARC / FLAT / ESCALATION / RECOVERY / MIXED_ARC / CYCLIC_ARC
**Q4b options**: WEAK / MODERATE / STRONG
**Q5a options**: NO_OSCILLATION / MEANINGLESS_NOISE / WEAK_RHYTHM / CLEAR_CYCLE
**Q5b options**: HELPS_READABILITY / NEUTRAL / HURTS_READABILITY

---

## 3. Per-probe Q6 (confusion + design feedback)

For each probe, answer Q6a (semi-required, ≥1 item) + Q6b (free text):

### P1
- Q6a: 
- Q6b: 

### P2
- Q6a: 
- Q6b: 

### P3
- Q6a: 
- Q6b: 

### P4
- Q6a: 
- Q6b: 

### P5
- Q6a: 
- Q6b: 

### P6
- Q6a: 
- Q6b: 

### P7
- Q6a: 
- Q6b: 

### P8
- Q6a: 
- Q6b: 

### P9
- Q6a: 
- Q6b: 

### P10
- Q6a: 
- Q6b: 

### P11
- Q6a: 
- Q6b: 

### P12
- Q6a: 
- Q6b: 

---

## 4. Per-probe classification

Per protocol §6.1 v2:
- **Readable** = Q1=CLEAR_FLOW AND Q1b ∈ {CAN_EXPLAIN, PARTIAL_EXPLAIN}
  AND Q4a ≠ NO_ARC AND Q2c ∈ {CLEAR, MIXED_BUT_READABLE}
- **Partial** = Q1=FLOW_HINT OR (Q1=CLEAR_FLOW AND Q1b=CANNOT_EXPLAIN)
  OR Q2c=VAGUE
- **Unreadable** = Q1=RANDOM OR Q4a=NO_ARC OR Q2c=UNREADABLE

| Probe | Classification |
|---|---|
| P1 | ? |
| P2 | ? |
| P3 | ? |
| P4 | ? |
| P5 | ? |
| P6 | ? |
| P7 | ? |
| P8 | ? |
| P9 | ? |
| P10 | ? |
| P11 | ? |
| P12 | ? |

---

## 5. Aggregate verdict

(Fill after table 4 complete)

- Readable count: ? / 12
- Partial count: ? / 12
- Unreadable count: ? / 12

### 5.1 Readability confidence (Q1b distribution)

| Q1b | Count |
|---|---|
| CAN_EXPLAIN | ? |
| PARTIAL_EXPLAIN | ? |
| CANNOT_EXPLAIN | ? |

### 5.2 Pressure clarity (Q2c distribution)

| Q2c | Count |
|---|---|
| CLEAR | ? |
| MIXED_BUT_READABLE | ? |
| VAGUE | ? |
| UNREADABLE | ? |

### 5.3 Dominant-pressure accuracy

Compare Q2a (and Q2b) vs ground truth scenario:
- accusation scenario → expected: accusation_blame / shame_social
- scarcity scenario → expected: scarcity_material / accusation_blame
- sacred scenario → expected: sacred_awe / shame_social

| Scenario | Correct Q2a count | Total | Accuracy |
|---|---|---|---|
| accusation | ? | 4 | ? |
| scarcity | ? | 4 | ? |
| sacred | ? | 4 | ? |

### 5.4 Q3b world-side perception

How often did evaluator pick world-side categories?

| Category | Count |
|---|---|
| interpersonal_relation | ? |
| group_alignment | ? |
| crowd_mood | ? |
| authority_presence | ? |
| public_attention | ? |
| not_discernible | ? |

High counts on crowd_mood / authority_presence / public_attention =
world-side dynamics are externally readable.

### 5.5 Arc type distribution (Q4a)

| Arc | Count |
|---|---|
| NO_ARC | ? |
| FLAT | ? |
| ESCALATION | ? |
| RECOVERY | ? |
| MIXED_ARC | ? |
| CYCLIC_ARC | ? |

### 5.6 Oscillation narrative contribution (Q5b)

| Q5b | Count |
|---|---|
| HELPS_READABILITY | ? |
| NEUTRAL | ? |
| HURTS_READABILITY | ? |

If HURTS frequent → oscillation might be artifact, not narrative

### 5.7 Ablation detectability

Phase 2a OFF probes: P3 (accusation), P7 (scarcity), P11 (sacred).
Expected signature: ceiling saturation, monotonic rise, no resolution.

Did evaluator notice these differ from baselines?
- P3 vs P1/P2 (accusation baseline): differ? ?
- P7 vs P5/P6 (scarcity baseline): differ? ?
- P11 vs P9/P10 (sacred baseline): differ? ?

---

## 6. Q6 confusion notes thematic clustering

Cluster Q6a/Q6b answers across all 12 probes:

### Probe-formatting level confusions
(things a better probe representation would fix)

- (fill from Q6 answers)

### Structural / kernel-level confusions
(things suggesting kernel needs simplification)

- (fill from Q6 answers)

**Ratio**: probe-formatting count vs structural count is the
KEY signal for Branch A vs Branch B.

---

## 7. Branch decision (per protocol §10 v2)

Apply the decision rules in §10:

- [ ] Branch A criteria met? (≥8/12 readable, CAN_EXPLAIN majority, Q6 mostly probe-formatting)
- [ ] Branch B criteria met? (≤3/12 readable, RANDOM frequent, Q6 mostly structural)
- [ ] Branch A+B 병행? (4-7/12 readable, explanation unstable)
- [ ] Branch C ready? (high readability + world-side externally readable + mixed-arc maintained)

**Final verdict**: (fill after evaluation)

---

## 8. Improvement notes for next iteration

(Lee fills in after evaluation)

- What worked well in the Q-set:
- What was awkward:
- What probes need redesign:
- What kernel changes are indicated:

---

**End of v2 template (Iter 161 Q-set update).**
