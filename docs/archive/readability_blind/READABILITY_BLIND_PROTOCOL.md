# WITNESS B-Direction — Readability Blind Evaluation Protocol

**Freeze date:** 2026-04-25
**Doc purpose:** Protocol for external (human) blind reading of engine
output, per `WITNESS_POST_LOOP_FREEZE_AND_NEXT_STEPS.md` Step C.

---

## 1. Why readability blind

89 iterations confirmed engine mechanism at internal metric level. But:
- No external validation that engine output "reads like a world"
- Mechanism-level success does not imply narrative-level success
- Criterion 6 of Updated Loop remains outstanding (human-gated)

This evaluation is the gate before deciding:
- Branch A (readability-facing expansion)
- Branch B (simplification — if unreadable)
- Branch C (broader world — if readable + robust)

---

## 2. Blind evaluator role

Evaluator (Lee or external reader) reads probe outputs **without**:
- Scenario label (accusation / scarcity / sacred)
- Seed number
- Phase 2a toggle state
- Internal metrics (rev/agent, grieve_frac, etc.)
- Mechanism explanations

Evaluator has access to:
- A compact narrative log of the probe (agents, events, actions, key
  state transitions)
- The question set below

Order: **read probe → answer questions → then optionally read ground
truth + metrics**.

---

## 3. Question set (per probe) -- v2 (Iter 161)

Updated per `docs/WITNESS_READABILITY_Q_IMPROVEMENTS_AND_NEXT_DIRECTION.md`.
The improved set distinguishes **flow detection** from **readability**,
allows **mixed pressure** observation, and elevates **confusion notes**
from optional to semi-required.

### Q1 — Flow vs noise
> 이 probe는 랜덤 로그처럼 보이나, 어떤 흐름이 느껴지나?

Options:
- `RANDOM` — 랜덤 로그로 보임
- `FLOW_HINT` — 흐름이 어렴풋이 느껴짐
- `CLEAR_FLOW` — 명확한 흐름 있음

### Q1b — Readability confidence
> 지금 느낀 흐름을 내가 설명할 수 있는가?

Options:
- `CAN_EXPLAIN` — 어떤 흐름인지 말로 설명 가능
- `PARTIAL_EXPLAIN` — 대략 느낌은 있으나 설명은 불완전
- `CANNOT_EXPLAIN` — 뭔가 있지만 설명 어려움

### Q2a — Primary perceived pressure
> 어떤 압력이 가장 중심처럼 보이나?

Options:
- `shame_social`
- `fear_physical`
- `sacred_awe`
- `scarcity_material`
- `accusation_blame`
- `grief_loss`
- `none_discernible`

### Q2b — Secondary perceived pressure
> 부차적으로 같이 느껴지는 압력이 있나?

Options:
- `none_secondary`
- `shame_social`
- `fear_physical`
- `sacred_awe`
- `scarcity_material`
- `accusation_blame`
- `grief_loss`

### Q2c — Pressure clarity
> 이 압력이 뚜렷하게 읽히는가?

Options:
- `CLEAR`
- `MIXED_BUT_READABLE`
- `VAGUE`
- `UNREADABLE`

### Q3a — Relation/group change level
> 관계나 집단 변화가 어느 수준에서 느껴지나?

Options:
- `NONE`
- `LOCAL_SHIFT` — 일부 agent 수준 변화만 감지
- `COHORT_SHIFT` — 집단/코호트 수준 변화 감지
- `RESTRUCTURE` — 관계/집단 재편으로 느껴짐

### Q3b — What changed most?
> 가장 두드러진 변화는 무엇이었나? (복수 선택 가능)

Options:
- `interpersonal_relation`
- `group_alignment`
- `crowd_mood`
- `authority_presence`
- `public_attention`
- `not_discernible`

### Q4a — Primary arc type
> recovery / escalation / cyclic 중 어떤 arc가 보이나?

Options:
- `NO_ARC` — 흐름 없음
- `FLAT` — 변화 없음
- `ESCALATION` — 악화만
- `RECOVERY` — 회복만
- `MIXED_ARC` — 진폭 있는 복합 흐름
- `CYCLIC_ARC` — 의미 있는 반복 cycle

### Q4b — Arc strength
> arc가 얼마나 강하게 느껴지나?

Options:
- `WEAK`
- `MODERATE`
- `STRONG`

### Q5a — Oscillation type
> oscillation이 어떤 종류로 보이나?

Options:
- `NO_OSCILLATION`
- `MEANINGLESS_NOISE` — 의미 없는 흔들림
- `WEAK_RHYTHM` — 약한 반복
- `CLEAR_CYCLE` — 의미 있는 반복

### Q5b — Narrative contribution
> oscillation이 이해를 돕나, 방해하나?

Options:
- `HELPS_READABILITY`
- `NEUTRAL`
- `HURTS_READABILITY`

### Q6a — 가장 이해 안 된 점 (semi-required, 최소 1개)
> 이 probe에서 가장 unreadable했던 부분 1-3개. 예시:

- pressure가 안 드러남
- agent가 너무 많아 구분 안 됨
- relation shift가 안 보임
- oscillation이 의미 없는 반복처럼 보임
- 사건이 왜 이어지는지 모르겠음
- world-side 변화보다 개인 로그만 보임
- (자유 기술)

### Q6b — readable하게 만들려면 무엇이 더 필요했는가 (free text)
> Branch A vs B 판단 위한 설계 피드백. 예시:

- 요약 문장
- relation delta 강조
- dominant pressure 표기
- cohort-level summary
- key event grouping
- (자유 기술)

---

## 4. Probe selection (12-20 target)

### 4.1 Coverage strategy
- 4 probes per scenario × 3 scenarios = 12 core
- 4 additional variants (Phase 2a off / mul variant / mixed injection) = 16 total

### 4.2 Probe list (proposed 12)

| # | Scenario | Variant | PYHASH | Seed | Horizon | Intent |
|:-:|---|---|:-:|:-:|:-:|---|
| P1 | accusation | baseline | 0 | 0 | 200 tk | Clean baseline |
| P2 | accusation | baseline | 0 | 3 | 200 tk | Seed variation |
| P3 | accusation | Phase 2a OFF | 0 | 0 | 200 tk | Ablation variant |
| P4 | accusation | shame mul 0.8 | 0 | 0 | 200 tk | Secondary-rise regime |
| P5 | scarcity | baseline | 0 | 0 | 200 tk | Scarcity clean |
| P6 | scarcity | baseline | 0 | 2 | 200 tk | Seed variation |
| P7 | scarcity | Phase 2a OFF | 0 | 0 | 200 tk | Ablation variant |
| P8 | scarcity | shame mul 0.8 | 0 | 0 | 200 tk | Regime variation |
| P9 | sacred | baseline | 0 | 0 | 200 tk | Sacred clean |
| P10 | sacred | baseline | 0 | 1 | 200 tk | Seed variation |
| P11 | sacred | Phase 2a OFF | 0 | 0 | 200 tk | Ablation variant |
| P12 | sacred | shame mul 0.05 | 0 | 0 | 200 tk | Low-mul sacred |

Probe IDs are assigned randomly before presenting to evaluator to prevent
ordering bias. Ground truth table held separately.

---

## 5. Probe format (what the evaluator sees)

Per probe, a compact text log:

```
[PROBE 7 / 12]   (scenario+seed hidden)

Agents: 10 named A1..A10 with role cluster labels
Locations: 3 named L1, L2, L3

Event log (tick : actor : event):
  t=3   L2  :  accusation fires against agent in L2 cohort
  t=5   A4  :  conceal
  t=5   A7  :  remain_present
  t=7   L3  :  accusation fires against agent in L3 cohort
  t=12  L1  :  guard presence
  ...
  (agent actions, spawned events, motif changes per significant tick)

State snapshots (tick 50, tick 100, tick 150):
  A4: shame=4.2, fear=3.1, motif=conceal
  A6: shame=8.8, guilt=6.4, motif=confess
  ...
  Crowd: blame_concentration={"disciple_follower": 3.2}, shame_climate=2.1

Final state (tick 200):
  (similar snapshot)
```

No scenario names, no PYHASH info, no ablation info, no metrics.

---

## 6. Aggregation + verdict (v2)

### 6.1 Per-probe scoring (using improved Q-set)

Each probe gets Q1, Q1b, Q2a-c, Q3a-b, Q4a-b, Q5a-b, Q6a-b answers. Classification:

- **Readable**: Q1=CLEAR_FLOW AND Q1b ∈ {CAN_EXPLAIN, PARTIAL_EXPLAIN}
  AND Q4a ≠ NO_ARC AND Q2c ∈ {CLEAR, MIXED_BUT_READABLE}
- **Partially readable**: Q1=FLOW_HINT OR (Q1=CLEAR_FLOW AND Q1b=CANNOT_EXPLAIN)
  OR Q2c=VAGUE
- **Unreadable**: Q1=RANDOM OR Q4a=NO_ARC OR Q2c=UNREADABLE

The Q1b axis (readability confidence) was added in Iter 161 because
flow detection alone was conflating "feels like something" with
"can explain". Branch A requires the latter.

### 6.2 Cross-probe patterns

After all 12 probes scored:
- Readable count / 12 → threshold
- CAN_EXPLAIN count / 12 → readability-confidence threshold
- Dominant-pressure accuracy: Q2a (and optionally Q2b) vs ground-truth scenario
- Pressure clarity distribution: Q2c counts (CLEAR / MIXED_BUT_READABLE / VAGUE / UNREADABLE)
- Arc-type distribution: Q4a counts
- Q5b distribution: HELPS_READABILITY vs HURTS_READABILITY (key for oscillation finding)
- Ablation detectability: can evaluator distinguish Phase 2a OFF probes from ON?
- Q6 confusion notes thematic clustering (probe-formatting issues vs
  structural issues): KEY for Branch A vs Branch B decision

### 6.3 Decision thresholds (v2 per Iter 161 directive §8)

#### Branch A — Readability-facing
Conditions (all):
- Readable ≥ 8/12
- Q1b CAN_EXPLAIN majority
- Q2/Q3/Q4/Q5 reasonably consistent across probes
- Q6 confusion notes are mostly **probe-formatting level** (not structural)

#### Branch B — Simplification 계속
Conditions:
- Readable ≤ 3/12
- Q1=RANDOM ratio high
- Q2c VAGUE/UNREADABLE majority
- Q5b HURTS_READABILITY frequent
- Q6 confusion notes point at **structural debt**

#### Branch A+B 병행
Conditions:
- Readable 4~7/12
- Flow detected but Q1b explanation unstable
- Mixed dynamics present but external reading wobbles

#### Branch C — Broader World
Conditions:
- Readable high
- World-side process partly readable externally (Q3b crowd_mood / authority_presence / public_attention picked frequently)
- Mixed-arc maintained without collapse
- Simplification need is low

---

## 7. Who runs this

This protocol is **human-gated**. Claude can:
- Generate probe text logs (see companion script `scripts/b_direction/generate_readability_probes.py`)
- Pre-populate ground truth table (held separately)
- Aggregate answers into verdict after evaluator returns

Claude CANNOT:
- Act as the blind evaluator (has full mechanism knowledge)
- Interpret Q1-Q5 answers without human input
- Generate acceptable probes that prevent label leak (manual review
  recommended)

---

## 8. Ground truth (held for post-eval)

The scenario / seed / variant assignments above are held in:
`docs/b_direction/READABILITY_BLIND_GROUND_TRUTH.md` (internal, not shared
with evaluator).

Evaluator sees only scrambled P1-P12 IDs.

---

## 9. Output of evaluation (v2)

After evaluator completes all probes, results compiled into
`docs/b_direction/READABILITY_BLIND_RESULTS.md`:

```
| Probe | Q1 | Q1b | Q2a | Q2b | Q2c | Q3a | Q3b | Q4a | Q4b | Q5a | Q5b | Score |
| P1 | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |
```

Plus:
- Aggregate readable count / 12
- CAN_EXPLAIN count / 12 (readability-confidence)
- Q2c clarity distribution
- Perceived-pressure (Q2a + Q2b) vs ground-truth accuracy
- Q3b world-side perception counts (crowd_mood, authority_presence, public_attention)
- Q5b narrative contribution distribution
- Q6a confusion notes (semi-required)
- Q6b design feedback (free text)
- Ablation detectability

---

## 10. Post-evaluation branch decision input (v2)

Per Iter 161 directive §8 (improved branch criteria):

### Branch A — Readability-facing
- Readable ≥ 8/12 AND
- CAN_EXPLAIN majority AND
- Q2/Q3/Q4/Q5 consistent AND
- Q6 confusion = probe-formatting level

→ Move to readability-facing phase (probes can be enhanced;
  scenarios can be designed for readability)

### Branch B — Simplification
- Readable ≤ 3/12 AND
- Q1=RANDOM frequent AND
- Q2c VAGUE/UNREADABLE majority AND
- Q5b HURTS_READABILITY frequent AND
- Q6 confusion = structural debt

→ Continue Branch B simplification work (kernel reduction,
  decorative element removal, component ledger formalization)

### Branch A+B 병행 (parallel A and B)
- Readable 4-7/12 AND
- Flow detected but explanation unstable
- → Both paths: improve readability presentation AND simplify
  decorative elements

### Branch C — Broader World
- Readable high AND
- Q3b shows world-side perception (crowd/authority/public_attention) AND
- Mixed-arc maintained AND
- Simplification need low

→ Move to broader-world phase (cast composition variation,
  population grammar, additional scenarios)

---

**End of Readability Blind Protocol v2 (Iter 161). Companion files:
`READABILITY_BLIND_GROUND_TRUTH.md`, `generate_readability_probes.py`,
`READABILITY_BLIND_RESULTS.md` template.**
