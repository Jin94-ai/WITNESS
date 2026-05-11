# WITNESS Readability Blind Results V2

**Status:** EMPTY TEMPLATE (awaiting Lee's true blind evaluation)
**Protocol:** `READABILITY_BLIND_PROTOCOL_V2.md`
**Q-set:** v2 (Q1, Q1b, Q2a-c, Q3a-b, Q4a-b, Q5a-b, Q6a-b)

> **NOTE (2026-04-27)**: A Claude-simulation auto-grading run was performed
> per `WITNESS_NEXT_ACTIONS_PILOT_BLIND_EVAL.md`. Results are in
> `READABILITY_BLIND_RESULTS_V2_CLAUDE_SIM.md`. **That simulation does NOT
> replace Lee's true blind eval** — Claude has full mechanism knowledge.
> The simulation provisionally suggests Branch A (annotated format helps
> Q4a-rollup) but Lee's blind remains the gate.

---

## 0. Mode used (fill before starting)

- [ ] Pilot (N=4)
- [ ] Full (N=12, all original)
- [ ] Full (N=12, all annotated)
- [ ] Hybrid (N=12, 6 original + 6 annotated)

**Evaluator:** [name]
**Date:** [yyyy-mm-dd]
**Total time spent:** [minutes]

---

## 1. Pilot results (N=4)

Skip this section if doing full mode.

### 1.0 Quick-fill cheat sheet (NEW v2.6, friction reduction; v2.7 options aligned to PROTOCOL §2; v2.8 quick rules verbatim from PROTOCOL §3; v2.9 v2 annotated fields added)

**Annotated v2/v2.1/v3 fields (visible only on annotated probes; LOOP 28-34)**:

| Field | Options | Note |
|---|---|---|
| `Primary pressure` | `accusation` / `sacred` / `scarcity` / `shame` / `fear` / `awe` / `grief` / `mixed` / `none_clear` | Empirically detected (NOT scenario name). Address Q2a-typing gap. v2.1 = 12/12 = 100% accuracy via cast/location signature. |
| `Failure mode` | `shame_cap` / `repeat_retrigger` / `no_forgiveness_uptake` / `crowd_blame_persists` / `shame_decay_absent` | Only shown on SATURATION_DOMINATED. Resolves PILOT_4 confusion (200 confessions + saturation = shame ceiling). |
| `Public suspicion` (v3) | numeric peak/final or `negligible (peak<0.05)` | CrowdState ACTIVE memory. Q3b `public_attention` axis evidence. |
| `Authority vigilance` (v3) | numeric peak/final or `negligible (peak<0.05)` | CrowdState DEAD memory (logged-only). Q3b `authority_presence` axis evidence. v3 finding: only scarcity scenarios show authority_vigilance > 0 (guard_approaches event accumulation). |



**옵션을 protocol 다시 열지 않고 여기서 보고 채우세요.** 셀에는 옵션 ID 한 단어만 적으면 됩니다. **Single source of truth: `READABILITY_BLIND_PROTOCOL_V2.md` §2.**

| Q | 무엇을 묻는가 | 답 옵션 (cell에 한 단어만) |
|---|---|---|
| **Q1** | Flow vs noise | `RANDOM` / `FLOW_HINT` / `CLEAR_FLOW` |
| **Q1b** | Readability confidence | `CAN_EXPLAIN` / `PARTIAL_EXPLAIN` / `CANNOT_EXPLAIN` |
| **Q2a** | Primary pressure | `shame` / `fear` / `sacred` / `scarcity` / `accusation` / `grief` / `none` |
| **Q2b** | Secondary pressure | (same as Q2a) / `none_secondary` |
| **Q2c** | Pressure clarity | `CLEAR` / `MIXED_BUT_READABLE` / `VAGUE` / `UNREADABLE` |
| **Q3a** | Relation/group level | `NONE` / `LOCAL_SHIFT` / `COHORT_SHIFT` / `RESTRUCTURE` |
| **Q3b** | What changed most (multi) | `interpersonal` / `group_alignment` / `crowd_mood` / `authority` / `public_attention` |
| **Q4a** | Primary arc | `NO_ARC` / `FLAT` / `ESCALATION` / `RECOVERY` / `MIXED` / `CYCLIC` |
| **Q4b** | Arc strength | `WEAK` / `MODERATE` / `STRONG` |
| **Q5a** | Oscillation type | `NO_OSC` / `MEANINGLESS_NOISE` / `WEAK_RHYTHM` / `CLEAR_CYCLE` |
| **Q5b** | Narrative contribution | `HELPS` / `NEUTRAL` / `HURTS` |
| **Score** | 종합 (Protocol §3) | `Readable` / `Partial` / `Unreadable` |

**Quick rules** (verbatim from `READABILITY_BLIND_PROTOCOL_V2.md` §3):
- **Readable**: `Q1=CLEAR_FLOW AND Q1b ∈ {CAN_EXPLAIN, PARTIAL_EXPLAIN} AND Q4a ≠ NO_ARC AND Q2c ∈ {CLEAR, MIXED_BUT_READABLE}`
- **Partially readable**: `Q1=FLOW_HINT OR (Q1=CLEAR_FLOW AND Q1b=CANNOT_EXPLAIN) OR Q2c=VAGUE`
- **Unreadable**: `Q1=RANDOM OR Q4a=NO_ARC OR Q2c=UNREADABLE`

### 1.1 Per-probe table

| Probe | Format | Q1 | Q1b | Q2a | Q2b | Q2c | Q3a | Q3b | Q4a | Q4b | Q5a | Q5b | Score |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PILOT_1 | original | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? |
| PILOT_2 | original | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? |
| PILOT_3 | annotated | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? |
| PILOT_4 | annotated | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? |

**Score column**: Readable / Partial / Unreadable per Protocol V2 §3 (or §1.0 quick rules above).

### 1.1.5 Final summary self-call (NEW v2.1)

After answering Q1-Q6, BEFORE looking at any annotated label, write your
own one-line final summary using the same 5-label vocabulary:

| Probe | Format | Your final summary | Annotated label (visible only on PILOT_3, PILOT_4) | Match? |
|---|---|---|---|---|
| PILOT_1 | original | ? | (not shown — original) | n/a |
| PILOT_2 | original | ? | (not shown — original) | n/a |
| PILOT_3 | annotated | ? | RECOVERY_DOMINATED | yes/no |
| PILOT_4 | annotated | ? | SATURATION_DOMINATED | yes/no |

**Vocabulary** (Protocol V2 §1.2.0 / ANNOTATED_PROBE_FORMAT v1.2):
- `LOW_ACTIVITY` — kernel almost silent, no shame accumulation across cohorts
- `RECOVERY_DOMINATED` — at least one cohort recovered, no saturation
- `SATURATION_DOMINATED` — at least one cohort stuck at high shame, no recovery
- `MIXED` — both recovery and saturation cohorts present (divergence)
- `PARTIAL` — neither pole dominant; mostly partial cohorts

**Why two columns for annotated probes**:
- Original probes: evaluator's self-call is the only signal → tests whether
  kernel structure is legible without help
- Annotated probes: evaluator may be anchored by visible label. Match rate
  shows whether label is intuitive given the probe data; mismatch (rare)
  suggests label rule needs revision OR evaluator misread label

**Branch implication**:
- If original self-call accuracy < annotated match rate → **format helps
  Q4a-style inference** (Branch A signal for presentation work)
- If both low → **structure unclear regardless of format** (Branch B signal)
- If original self-call high → kernel is legible without label

### 1.2 Q6a (confusion notes, structured + free)

#### PILOT_1 (original)
- [TAG] note 1
- [TAG] note 2
- (free text if needed)

#### PILOT_2 (original)
- ...

#### PILOT_3 (annotated)
- ...

#### PILOT_4 (annotated)
- ...

**Tag legend** (per Protocol V2 §2.1):
- `[FORMAT]` — probe formatting/presentation issue → Branch A signal
- `[STRUCTURE]` — kernel mechanism not detectable → Branch B signal
- `[Q_SET]` — question itself unclear
- `[SCOPE]` — probe lacks needed information
- `[OTHER]` — doesn't fit above

**Optional sub-tags** (Protocol V2 §2.1.1, v2.1):
- `[FORMAT:LENGTH/DENSITY/ANONYMIZATION/GROUPING/HEADLINE/CAP]`
- `[STRUCTURE:MECHANISM/AGENCY/CAUSALITY/WORLD_SIDE/RECOVERY]`
- `[Q_SET:AMBIGUOUS/MISSING_OPTION/OVERLAP/WRONG_LEVEL]`
- `[SCOPE:HIDDEN_DATA/TRAJECTORY/RELATION/TIMING]`

### 1.3 Q6b (design feedback, free text)

What would have made each probe more readable?

- PILOT_1: 
- PILOT_2: 
- PILOT_3: 
- PILOT_4: 

### 1.4 Pilot aggregates

**Format-axis (Protocol V2 §4)**:
- Readable rate (original): [count] / 2
- Readable rate (annotated): [count] / 2
- Format gap: [+/- %]
- CAN_EXPLAIN gap: [+/- %]
- Q5b HELPS rate gap: [+/- %]

**Q6a tag distribution**:
- [FORMAT] count: 
- [STRUCTURE] count: 
- [Q_SET] count: 
- [SCOPE] count: 
- [OTHER] count: 

**Final summary self-call (per §1.1.5, NEW v2.1)**:
- Original self-call accuracy (vs ground truth in §4.1): [N] / 2
- Annotated match rate (self-call vs visible label): [N] / 2
- Comparison: original-self-call vs annotated-match → indicates whether
  format helps Q4a-style inference

**Format-axis metrics v2.2 (per Protocol V2 §4 extension)**:
- **Q4a-rollup gap**: (annotated match rate) - (original self-call accuracy) = ?
  - >0: annotation helps arc rollup
  - ≈0: annotation does NOT help arc rollup
- **Q2a-typing gap**: (Q2a correct on annotated) / N - (on original) / N = ?
  - Computed after §4 ground truth comparison
  - >0: annotation helps scenario detection
  - ≈0: orthogonal — annotation does not surface scenario type

**Format-axis metric v2.3 (Branch C signal)**:
- **Q3b world-side gap**: count of `{crowd_mood, authority_presence, public_attention}` selected
  - Annotated count: ?
  - Original count: ?
  - Gap (annotated - original): ?
  - Per axis breakdown (which world-side option surfaced):
    - crowd_mood gap: ?
    - authority_presence gap: ?
    - public_attention gap: ?
  - Branch C ready: Q3b world-side gap >0 AND Q1 readable rate high on both

### 1.5 Pilot branch decision (per Protocol V2 §5.1)

| Pattern | Match? |
|---|---|
| Annotated 2/2 + original ≤1/2 → Branch A | yes/no |
| Both 2/2 → Branch C ready | yes/no |
| Both ≤1/2 → Branch B priority | yes/no |
| Mixed → run full eval | yes/no |

**Pilot verdict**: [A / B / C / A+B / inconclusive — run full]

### 1.6 Pilot time tracking

| Phase | Target | Actual |
|---|---|---|
| Reading | 12-16 min | |
| Writing answers | 3-4 min | |
| Total | 15-20 min | |

---

## 2. Full results (N=12)

Skip this section if pilot was sufficient.

### 2.1 Per-probe table — Q1, Q1b, Q2

| Probe | Format | Q1 | Q1b | Q2a | Q2b | Q2c |
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

### 2.2 Per-probe table — Q3, Q4, Q5, Score

| Probe | Q3a | Q3b | Q4a | Q4b | Q5a | Q5b | Score |
|---|---|---|---|---|---|---|---|
| P1 | ? | ? | ? | ? | ? | ? | ? |
| P2 | ? | ? | ? | ? | ? | ? | ? |
| P3 | ? | ? | ? | ? | ? | ? | ? |
| P4 | ? | ? | ? | ? | ? | ? | ? |
| P5 | ? | ? | ? | ? | ? | ? | ? |
| P6 | ? | ? | ? | ? | ? | ? | ? |
| P7 | ? | ? | ? | ? | ? | ? | ? |
| P8 | ? | ? | ? | ? | ? | ? | ? |
| P9 | ? | ? | ? | ? | ? | ? | ? |
| P10 | ? | ? | ? | ? | ? | ? | ? |
| P11 | ? | ? | ? | ? | ? | ? | ? |
| P12 | ? | ? | ? | ? | ? | ? | ? |

### 2.3 Per-probe Q6a (confusion notes, tagged)

#### P1
- [TAG] ...

(repeat P2-P12)

### 2.4 Per-probe Q6b (free text design feedback)

#### P1
- 

(repeat P2-P12)

### 2.5 Full-mode aggregates

**Counts**:
- Readable: [N] / 12
- Partially readable: [N] / 12
- Unreadable: [N] / 12

**Q1b confidence**:
- CAN_EXPLAIN: [N] / 12
- PARTIAL_EXPLAIN: [N] / 12
- CANNOT_EXPLAIN: [N] / 12

**Q2a primary pressure accuracy** (after revealing ground truth):
- Correct: [N] / 12
- Off-by-related: [N] / 12 (e.g., grief instead of shame)
- Wrong category: [N] / 12

**Q2c clarity distribution**:
- CLEAR: [N]
- MIXED_BUT_READABLE: [N]
- VAGUE: [N]
- UNREADABLE: [N]

**Q3b world-side perception count** (multi-select):
- crowd_mood: [N]
- authority_presence: [N]
- public_attention: [N]
- group_alignment: [N]
- interpersonal_relation: [N]

**Q4a arc distribution**:
- NO_ARC: [N]
- FLAT: [N]
- ESCALATION: [N]
- RECOVERY: [N]
- MIXED_ARC: [N]
- CYCLIC_ARC: [N]

**Q5b oscillation contribution**:
- HELPS_READABILITY: [N]
- NEUTRAL: [N]
- HURTS_READABILITY: [N]

**Q6a tag distribution**:
- [FORMAT]: [N]
- [STRUCTURE]: [N]
- [Q_SET]: [N]
- [SCOPE]: [N]
- [OTHER]: [N]

**Ablation detectability** (after revealing ground truth):
- p2a_off probes correctly identified as different: [N] / [3 p2a_off probes]

### 2.6 If hybrid mode (N=12, 6+6)

**Format-axis breakdown**:
- Readable rate (originals): [N] / 6
- Readable rate (annotated): [N] / 6
- Format gap: [+/- %]
- CAN_EXPLAIN gap: [+/- %]

### 2.7 Full branch decision (per Protocol V2 §5.2)

Apply each rule and tick conditions met:

#### Branch A — Readability-facing
- [ ] Readable ≥ 8/12
- [ ] CAN_EXPLAIN majority
- [ ] Q2/Q3/Q4/Q5 reasonably consistent across probes
- [ ] Q6a [FORMAT] dominates

#### Branch B — Simplification
- [ ] Readable ≤ 3/12
- [ ] Q1=RANDOM frequent
- [ ] Q2c VAGUE/UNREADABLE majority
- [ ] Q5b HURTS_READABILITY frequent
- [ ] Q6a [STRUCTURE] dominates

#### Branch A+B
- [ ] Readable 4-7/12
- [ ] Q6a mixed FORMAT/STRUCTURE

#### Branch C
- [ ] Readable high
- [ ] Q3b world-side picked frequently (crowd_mood / authority / public_attention)
- [ ] Mixed-arc maintained
- [ ] Simplification need low

**Full verdict**: [A / B / A+B / C]

---

## 3. Cross-probe observations (free text)

After completing all probes:

- Did any pattern emerge across probes? (e.g., scenarios always readable, variants never)
- Did the format axis affect your answers in unexpected ways?
- Did Q-set V2 questions feel adequate? Where did Q6a [Q_SET] tags cluster?
- Where did you spend the most time? Why?

[free text]

---

## 4. Ground truth comparison (only AFTER finishing eval)

Open `READABILITY_BLIND_GROUND_TRUTH.md` and compare:

| Probe | Your Q2a (primary) | Ground truth scenario | Match? |
|---|---|---|---|
| P1 | ? | scarcity sham_mul_0.8 | ? |
| P2 | ? | scarcity baseline | ? |
| P3 | ? | accusation p2a_off | ? |
| P4 | ? | sacred baseline | ? |
| P5 | ? | sacred baseline | ? |
| P6 | ? | scarcity p2a_off | ? |
| P7 | ? | sacred sham_mul_0.05 | ? |
| P8 | ? | accusation sham_mul_0.8 | ? |
| P9 | ? | scarcity baseline | ? |
| P10 | ? | accusation baseline | ? |
| P11 | ? | accusation baseline | ? |
| P12 | ? | sacred p2a_off | ? |

(Or for pilot: only PILOT_1-4 mapped to P10 / P9 / P4 / P3.)

### 4.1 Final summary ground truth (NEW v2.1, for §1.1.5 self-call check)

Computed from annotated probe headlines (Iter 187 v1.2):

| Probe | Source | Final summary (ground truth) |
|---|---|---|
| P1 | scarcity sham_mul_0.8 | PARTIAL |
| P2 | scarcity baseline s=2 | SATURATION_DOMINATED |
| P3 | accusation p2a_off | SATURATION_DOMINATED |
| P4 | sacred baseline s=0 | RECOVERY_DOMINATED |
| P5 | sacred baseline s=1 | RECOVERY_DOMINATED |
| P6 | scarcity p2a_off | MIXED |
| P7 | sacred sham_mul_0.05 | PARTIAL |
| P8 | accusation sham_mul_0.8 | MIXED |
| P9 | scarcity baseline s=0 | SATURATION_DOMINATED |
| P10 | accusation baseline | RECOVERY_DOMINATED |
| P11 | accusation baseline s=3 | MIXED |
| P12 | sacred p2a_off | SATURATION_DOMINATED |

For pilot mapping:
- PILOT_1 (P10): RECOVERY_DOMINATED
- PILOT_2 (P9): SATURATION_DOMINATED
- PILOT_3 (P4): RECOVERY_DOMINATED
- PILOT_4 (P3): SATURATION_DOMINATED

---

## 5. Notes for V3 protocol revision (post-eval)

If Q6a [Q_SET] tags clustered on specific questions, list them:

- [Q_SET] cluster around: [Q1 / Q1b / Q2a / ...]
- Suggested revision: [free text]

These will inform Protocol V3 if needed.

---

## 6. Versioning

| Version | Date | Change |
|---|---|---|
| v2.0 | 2026-04-22 | initial Q-set V2 template |
| v2.1 | 2026-04-25 | + §1.1.5 final summary self-call (NEW), + §4.1 ground truth |
| v2.2-2.5 | 2026-04-26~27 | format-axis metrics + V2.4 matrix + V2.5 precedence-ordered algorithm (Protocol V2 cross-link) |
| v2.6 | 2026-04-28 | §1.0 quick-fill cheat sheet (friction reduction). Lee가 Protocol V2를 다시 열지 않고 Q1-Q5b 옵션 + Score quick rules를 한 곳에서 볼 수 있음. Per continuous-execution directive §5 우선순위 1. |
| v2.7 | 2026-04-28 | §1.0 cheat sheet 옵션을 PROTOCOL_V2 §2와 정확히 align (autonomous-mode LOOP 18 self-check 발견 후 즉시 수정). 이전 v2.6은 옵션을 자체 추정해 4개 Q에 불일치 발생. |
| v2.8 | 2026-04-28 | §1.0 quick rules도 PROTOCOL_V2 §3과 verbatim 일치. |
| v2.9 | 2026-04-28 | §1.0 cheat sheet에 v2 annotated fields (Primary pressure + Failure mode). v2 first cycle scarcity 0/4 limitation. |
| v2.10 | 2026-04-28 | LOOP 32 v2.1 scarcity detection 100% (cast/location multi-signal). Limitation resolved. |
| **v2.11 (this)** | **2026-04-28** | **LOOP 34 v3 world-side fields (Public suspicion + Authority vigilance) annotated에 surface. Q3b world-side gap address. Both fields traceable from CrowdState — public_suspicion ACTIVE memory, authority_vigilance DEAD/logged-only. evaluator는 이 두 axes 추가로 Q3b 답할 수 있음.** |
