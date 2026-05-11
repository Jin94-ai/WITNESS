# Branch C — 18 Probes Blind Eval, GPT-5.5 SEND BUNDLE

**Date**: 2026-04-29
**Companion**: `BRANCH_C_18_PROBES_BLIND_PACKAGE.md` (full context, ground truth, Q-set spec)
**용도**: **이 한 파일을 GPT-5.5에 통째 paste**.
- §A: Lee가 **Lee 메시지로** 보내는 부분 (system prompt + 18 probes + 응답 양식)
- §B: Lee가 **자기 노트로만** 보관 (GPT-5.5에 보내지 *않음*)

---

# §A. GPT-5.5에게 보낼 메시지 (이 박스 안의 모든 것을 paste)

```
You are an external readability evaluator for the WITNESS project. Your task
is to read 18 simulation probes (all annotated v3 format, ID labelled
P_NEW_01..P_NEW_18) and answer a structured Q-set per probe, then produce
aggregates.

Hidden context: Each probe is one 50-tick (or 200-tick, see header) slice of
a multi-agent simulation. The scenario type, cast composition, and spatial
placement are hidden — you must infer them from the data.

CRITICAL DISCLOSURE: All 18 probes were generated at PYTHONHASHSEED=0
(single-seed snapshot). A separate cross-seed re-test (5-seed ensemble)
showed per-dimension configuration-sensitivity ratios are biased ±33pp by
single-seed conditioning (e.g., placement variation: 67% at seed=0 vs 44%
across 5 seeds). The CLAIM under test is at modal level across 5 seeds —
the magnitude here (this 18-probe sample) is not the eval target. Treat
this sample as evidence of WHETHER configuration matters, not how much.

Rules:
1. Treat as blind: do not search prior context, do not derive variant from
   probe ID. P_NEW_01..18 are anonymous; infer scenario / cast / placement
   from the probe content only.
2. For each probe, fill all 11 columns of the Q-set table.
3. The "Final summary" headline is visible at the top of each probe — use it
   as a LABEL-INTUITION CHECK against your independent cohort-based reading,
   NOT as your primary self-call.
4. Q6a confusion notes: tag with [FORMAT] / [STRUCTURE] / [Q_SET] / [SCOPE] /
   [OTHER] before free text.
5. After all 18 probes, group by your inferred scenario type (e.g.,
   "accusation probes", "scarcity probes", "sacred probes") and report:
   - How many distinct final-summary outcomes within each scenario group?
   - Which probes diverge from the group's modal outcome?
   - Hypothesis for what drives within-scenario divergence (cast / placement
     / events / horizon)

Q-set + score rule:

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

Score:
- Readable: Q1=CLEAR_FLOW AND Q1b ∈ {CAN_EXPLAIN, PARTIAL_EXPLAIN} AND Q4a ≠ NO_ARC AND Q2c ∈ {CLEAR, MIXED_BUT_READABLE}
- Partially readable: Q1=FLOW_HINT OR (Q1=CLEAR_FLOW AND Q1b=CANNOT_EXPLAIN) OR Q2c=VAGUE
- Unreadable: Q1=RANDOM OR Q4a=NO_ARC OR Q2c=UNREADABLE

==========================================================================
THE 18 PROBES (P_NEW_01 .. P_NEW_18)
==========================================================================

=== PROBE P_NEW_01 ===

[Annotated headline summary]
  Final summary:    RECOVERY_DOMINATED
  Primary pressure: accusation

  Cohort outcomes:
    [L3 cohort, 4 agents]:  recovery: peak~10.0 → final~2.5
    [L1 cohort, 2 agents]:  partial: peak~10.0 → final~5.8
    [L2 cohort, 4 agents]:  no shame accumulation

  Pressure events + recovery actions:
    Accusations: 2 fired (targets: disciple_follower, outsider)
    Recovery actions: 74 confessions, 41 forgiveness rumors emitted

  World-level dynamics:
    Crowd blame total:   peak 1.7 at t=33 → final 0.0
    Public suspicion:    peak 0.22 → final 0.00
    Authority vigilance: negligible (peak < 0.05)
    Top blame target:    crowd_participant (peak 1.00)

============================================================

Agents: A1=follower, A2=follower, A3=follower, A4=authority, A5=enforcer, A6=crowd, A7=crowd, A8=crowd, A9=family, A10=outsider
Locations: L1, L2, L3

=== PROBE P_NEW_02 ===

[Annotated headline summary]
  Final summary:    SATURATION_DOMINATED
  Primary pressure: accusation
  Failure mode:     shame_cap

  Cohort outcomes:
    [L3 cohort, 4 agents]:  no shame accumulation
    [L1 cohort, 2 agents]:  saturation: peak~10.0 → final~10.0 (stuck)
    [L2 cohort, 4 agents]:  no shame accumulation

  Pressure events + recovery actions:
    Accusations: 2 fired (targets: disciple_follower, outsider)
    Recovery actions: 36 confessions, 14 forgiveness rumors emitted

  World-level dynamics:
    Crowd blame total:   peak 0.7 at t=200 → final 0.7
    Public suspicion:    negligible (peak < 0.05)
    Authority vigilance: negligible (peak < 0.05)
    Top blame target:    soldier_enforcer (peak 0.50)

============================================================

Agents: A1=follower, A2=follower, A3=follower, A4=authority, A5=enforcer, A6=crowd, A7=crowd, A8=crowd, A9=family, A10=outsider
Locations: L1, L2, L3

=== PROBE P_NEW_03 ===

[Annotated headline summary]
  Final summary:    RECOVERY_DOMINATED
  Primary pressure: accusation

  Cohort outcomes:
    [L3 cohort, 2 agents]:  partial: peak~10.0 → final~5.0
    [L1 cohort, 8 agents]:  recovery: peak~10.0 → final~2.5

  Pressure events + recovery actions:
    Accusations: 2 fired (targets: disciple_follower, outsider)
    Recovery actions: 116 confessions, 116 forgiveness rumors emitted

  World-level dynamics:
    Crowd blame total:   peak 2.6 at t=17 → final 0.2
    Public suspicion:    peak 0.63 → final 0.03
    Authority vigilance: negligible (peak < 0.05)
    Top blame target:    disciple_follower (peak 1.00)

============================================================

Agents: A1=follower, A2=follower, A3=follower, A4=authority, A5=enforcer, A6=crowd, A7=crowd, A8=crowd, A9=family, A10=outsider
Locations: L1, L2, L3

=== PROBE P_NEW_04 ===

[Annotated headline summary]
  Final summary:    SATURATION_DOMINATED
  Primary pressure: scarcity
  Failure mode:     shame_cap

  Cohort outcomes:
    [L2 cohort, 4 agents]:  no shame accumulation
    [L1 cohort, 4 agents]:  saturation: peak~10.0 → final~10.0 (stuck)
    [L3 cohort, 4 agents]:  no shame accumulation

  Pressure events + recovery actions:
    Accusations: 1 fired (targets: merchant)
    Recovery actions: 69 confessions, 52 forgiveness rumors emitted

  World-level dynamics:
    Crowd blame total:   peak 1.4 at t=22 → final 0.3
    Public suspicion:    peak 0.24 → final 0.03
    Authority vigilance: peak 0.25 → final 0.25
    Top blame target:    fisher_laborer (peak 1.00)

============================================================

Agents: A1=merchant, A2=family, A3=laborer, A4=laborer, A5=laborer, A6=authority, A7=enforcer, A8=enforcer, A9=crowd, A10=crowd, A11=outsider, A12=elite_strategist
Locations: L1, L2, L3

=== PROBE P_NEW_05 ===

[Annotated headline summary]
  Final summary:    RECOVERY_DOMINATED
  Primary pressure: scarcity

  Cohort outcomes:
    [L2 cohort, 4 agents]:  no shame accumulation
    [L1 cohort, 4 agents]:  recovery: peak~10.0 → final~2.2
    [L3 cohort, 4 agents]:  no shame accumulation

  Pressure events + recovery actions:
    Accusations: 1 fired (targets: merchant)
    Recovery actions: 57 confessions, 43 forgiveness rumors emitted

  World-level dynamics:
    Crowd blame total:   peak 1.5 at t=150 → final 0.0
    Public suspicion:    peak 0.28 → final 0.00
    Authority vigilance: peak 0.25 → final 0.25
    Top blame target:    fisher_laborer (peak 1.00)

============================================================

Agents: A1=merchant, A2=family, A3=laborer, A4=laborer, A5=laborer, A6=authority, A7=enforcer, A8=enforcer, A9=crowd, A10=crowd, A11=outsider, A12=elite_strategist
Locations: L1, L2, L3

=== PROBE P_NEW_06 ===

[Annotated headline summary]
  Final summary:    PARTIAL
  Primary pressure: scarcity

  Cohort outcomes:
    [L2 cohort, 2 agents]:  no shame accumulation
    [L1 cohort, 9 agents]:  partial: peak~10.0 → final~4.4
    [L3 cohort, 1 agents]:  no shame accumulation

  Pressure events + recovery actions:
    Accusations: 1 fired (targets: merchant)
    Recovery actions: 154 confessions, 148 forgiveness rumors emitted

  World-level dynamics:
    Crowd blame total:   peak 2.6 at t=17 → final 0.2
    Public suspicion:    peak 0.96 → final 0.01
    Authority vigilance: peak 0.25 → final 0.25
    Top blame target:    fisher_laborer (peak 1.00)

============================================================

Agents: A1=merchant, A2=family, A3=laborer, A4=laborer, A5=laborer, A6=authority, A7=enforcer, A8=enforcer, A9=crowd, A10=crowd, A11=outsider, A12=elite_strategist
Locations: L1, L2, L3

=== PROBE P_NEW_07 ===

[Annotated headline summary]
  Final summary:    RECOVERY_DOMINATED
  Primary pressure: sacred

  Cohort outcomes:
    [L3 cohort, 2 agents]:  recovery: peak~7.2 → final~0.0
    [L2 cohort, 1 agents]:  no shame accumulation
    [L1 cohort, 5 agents]:  recovery: peak~10.0 → final~0.8

  Pressure events + recovery actions:
    Accusations: 1 fired (targets: spiritual_wanderer)
    Recovery actions: 52 confessions, 40 forgiveness rumors emitted

  World-level dynamics:
    Crowd blame total:   peak 1.2 at t=182 → final 0.0
    Public suspicion:    peak 0.16 → final 0.00
    Authority vigilance: negligible (peak < 0.05)
    Top blame target:    disciple_follower (peak 1.00)

============================================================

Agents: A1=wanderer, A2=authority, A3=follower, A4=follower, A5=follower, A6=crowd, A7=crowd, A8=family
Locations: L1, L2, L3

=== PROBE P_NEW_08 ===

[Annotated headline summary]
  Final summary:    SATURATION_DOMINATED
  Primary pressure: sacred
  Failure mode:     shame_cap

  Cohort outcomes:
    [L3 cohort, 5 agents]:  no shame accumulation
    [L2 cohort, 1 agents]:  no shame accumulation
    [L1 cohort, 2 agents]:  saturation: peak~10.0 → final~10.0 (stuck)

  Pressure events + recovery actions:
    Accusations: 1 fired (targets: spiritual_wanderer)
    Recovery actions: 21 confessions, 19 forgiveness rumors emitted

  World-level dynamics:
    Crowd blame total:   peak 0.4 at t=173 → final 0.2
    Public suspicion:    negligible (peak < 0.05)
    Authority vigilance: negligible (peak < 0.05)
    Top blame target:    crowd_participant (peak 0.37)

============================================================

Agents: A1=wanderer, A2=authority, A3=follower, A4=follower, A5=follower, A6=crowd, A7=crowd, A8=family
Locations: L1, L2, L3

=== PROBE P_NEW_09 ===

[Annotated headline summary]
  Final summary:    LOW_ACTIVITY
  Primary pressure: none_clear

  Cohort outcomes:
    [L3 cohort, 1 agents]:  no shame accumulation
    [L2 cohort, 7 agents]:  no shame accumulation

  Pressure events + recovery actions:
    Accusations: 1 fired (targets: spiritual_wanderer)
    Recovery actions: 0 confessions, 0 forgiveness rumors emitted

  World-level dynamics:
    Crowd blame total:   peak 0.3 at t=50 → final 0.0
    Public suspicion:    negligible (peak < 0.05)
    Authority vigilance: negligible (peak < 0.05)
    Top blame target:    spiritual_wanderer (peak 0.26, weak)

============================================================

Agents: A1=wanderer, A2=authority, A3=follower, A4=follower, A5=follower, A6=crowd, A7=crowd, A8=family
Locations: L1, L2, L3

=== PROBE P_NEW_10 ===

[Annotated headline summary]
  Final summary:    MIXED
  Primary pressure: accusation
  Cast size:        10

  Cohort outcomes:
    [L3 cohort, 4 agents]:  recovery: peak~10.0 -> final~2.5
    [L1 cohort, 2 agents]:  saturation: peak~10.0 -> final~10.0 (stuck)
    [L2 cohort, 4 agents]:  no shame accumulation

  Pressure events + recovery actions:
    Accusations: 2 fired (targets: disciple_follower, outsider)
    Recovery actions: 69 confessions, 36 forgiveness rumors emitted

  World-level dynamics:
    Crowd blame total:   peak 1.7 at t=165 -> final 0.0
    Public suspicion:    peak 0.17 -> final 0.00
    Authority vigilance: negligible (peak < 0.05)
    Top blame target:    crowd_participant (peak 1.00)

============================================================

Agents: A1=follower, A2=follower, A3=follower, A4=authority, A5=enforcer, A6=crowd, A7=crowd, A8=crowd, A9=family, A10=outsider
Locations: L1, L2, L3

=== PROBE P_NEW_11 ===

[Annotated headline summary]
  Final summary:    RECOVERY_DOMINATED
  Primary pressure: accusation
  Cast size:        8

  Cohort outcomes:
    [L3 cohort, 4 agents]:  recovery: peak~10.0 -> final~2.9
    [L2 cohort, 4 agents]:  no shame accumulation

  Pressure events + recovery actions:
    Accusations: 2 fired (targets: disciple_follower, outsider)
    Recovery actions: 34 confessions, 16 forgiveness rumors emitted

  World-level dynamics:
    Crowd blame total:   peak 1.1 at t=165 -> final 0.0
    Public suspicion:    peak 0.09 -> final 0.00
    Authority vigilance: negligible (peak < 0.05)
    Top blame target:    crowd_participant (peak 0.96)

============================================================

Agents: A1=follower, A2=follower, A3=follower, A4=crowd, A5=crowd, A6=crowd, A7=family, A8=outsider
Locations: L1, L2, L3

=== PROBE P_NEW_12 ===

[Annotated headline summary]
  Final summary:    MIXED
  Primary pressure: accusation
  Cast size:        9

  Cohort outcomes:
    [L3 cohort, 3 agents]:  recovery: peak~7.1 -> final~0.0
    [L1 cohort, 2 agents]:  saturation: peak~10.0 -> final~10.0 (stuck)
    [L2 cohort, 4 agents]:  no shame accumulation

  Pressure events + recovery actions:
    Accusations: 2 fired (targets: disciple_follower, outsider)
    Recovery actions: 49 confessions, 24 forgiveness rumors emitted

  World-level dynamics:
    Crowd blame total:   peak 1.2 at t=33 -> final 0.4
    Public suspicion:    peak 0.07 -> final 0.03
    Authority vigilance: negligible (peak < 0.05)
    Top blame target:    crowd_participant (peak 0.88)

============================================================

Agents: A1=follower, A2=follower, A3=follower, A4=authority, A5=enforcer, A6=crowd, A7=crowd, A8=crowd, A9=family
Locations: L1, L2, L3

=== PROBE P_NEW_13 ===

[Annotated headline summary]
  Final summary:    SATURATION_DOMINATED
  Primary pressure: scarcity
  Failure mode:     shame_cap
  Cast size:        12

  Cohort outcomes:
    [L2 cohort, 4 agents]:  no shame accumulation
    [L1 cohort, 4 agents]:  saturation: peak~10.0 -> final~10.0 (stuck)
    [L3 cohort, 4 agents]:  no shame accumulation

  Pressure events + recovery actions:
    Accusations: 1 fired (targets: merchant)
    Recovery actions: 94 confessions, 62 forgiveness rumors emitted

  World-level dynamics:
    Crowd blame total:   peak 1.3 at t=147 -> final 1.1
    Public suspicion:    peak 0.19 -> final 0.07
    Authority vigilance: peak 0.25 -> final 0.25
    Top blame target:    fisher_laborer (peak 1.00)

============================================================

Agents: A1=merchant, A2=family, A3=laborer, A4=laborer, A5=laborer, A6=authority, A7=enforcer, A8=enforcer, A9=crowd, A10=crowd, A11=outsider, A12=elite_strategist
Locations: L1, L2, L3

=== PROBE P_NEW_14 ===

[Annotated headline summary]
  Final summary:    RECOVERY_DOMINATED
  Primary pressure: scarcity
  Cast size:        9

  Cohort outcomes:
    [L2 cohort, 2 agents]:  no shame accumulation
    [L1 cohort, 3 agents]:  recovery: peak~10.0 -> final~0.2
    [L3 cohort, 4 agents]:  no shame accumulation

  Pressure events + recovery actions:
    Accusations: 1 fired (targets: merchant)
    Recovery actions: 61 confessions, 43 forgiveness rumors emitted

  World-level dynamics:
    Crowd blame total:   peak 1.2 at t=18 -> final 0.0
    Public suspicion:    peak 0.23 -> final 0.00
    Authority vigilance: peak 0.25 -> final 0.25
    Top blame target:    fisher_laborer (peak 1.00)

============================================================

Agents: A1=merchant, A2=family, A3=laborer, A4=laborer, A5=laborer, A6=crowd, A7=crowd, A8=outsider, A9=elite_strategist
Locations: L1, L2, L3

=== PROBE P_NEW_15 ===

[Annotated headline summary]
  Final summary:    RECOVERY_DOMINATED
  Primary pressure: scarcity
  Cast size:        10

  Cohort outcomes:
    [L2 cohort, 3 agents]:  no shame accumulation
    [L1 cohort, 4 agents]:  recovery: peak~9.2 -> final~2.8
    [L3 cohort, 3 agents]:  no shame accumulation

  Pressure events + recovery actions:
    Accusations: 1 fired (targets: merchant)
    Recovery actions: 176 confessions, 117 forgiveness rumors emitted

  World-level dynamics:
    Crowd blame total:   peak 1.0 at t=21 -> final 0.0
    Public suspicion:    peak 0.21 -> final 0.00
    Authority vigilance: peak 0.25 -> final 0.25
    Top blame target:    fisher_laborer (peak 0.80)

============================================================

Agents: A1=merchant, A2=family, A3=laborer, A4=laborer, A5=laborer, A6=authority, A7=enforcer, A8=enforcer, A9=crowd, A10=crowd
Locations: L1, L2, L3

=== PROBE P_NEW_16 ===

[Annotated headline summary]
  Final summary:    PARTIAL
  Primary pressure: sacred
  Cast size:        8

  Cohort outcomes:
    [L3 cohort, 2 agents]:  partial: peak~3.0 -> final~0.0
    [L2 cohort, 1 agents]:  no shame accumulation
    [L1 cohort, 5 agents]:  partial: peak~10.0 -> final~5.0

  Pressure events + recovery actions:
    Accusations: 1 fired (targets: spiritual_wanderer)
    Recovery actions: 49 confessions, 35 forgiveness rumors emitted

  World-level dynamics:
    Crowd blame total:   peak 1.0 at t=152 -> final 0.0
    Public suspicion:    peak 0.07 -> final 0.00
    Authority vigilance: negligible (peak < 0.05)
    Top blame target:    disciple_follower (peak 0.88)

============================================================

Agents: A1=wanderer, A2=authority, A3=follower, A4=follower, A5=follower, A6=crowd, A7=crowd, A8=family
Locations: L1, L2, L3

=== PROBE P_NEW_17 ===

[Annotated headline summary]
  Final summary:    RECOVERY_DOMINATED
  Primary pressure: sacred
  Cast size:        7

  Cohort outcomes:
    [L3 cohort, 2 agents]:  partial: peak~10.0 -> final~5.0
    [L1 cohort, 5 agents]:  recovery: peak~10.0 -> final~0.8

  Pressure events + recovery actions:
    Accusations: 1 fired (targets: spiritual_wanderer)
    Recovery actions: 30 confessions, 30 forgiveness rumors emitted

  World-level dynamics:
    Crowd blame total:   peak 0.7 at t=161 -> final 0.0
    Public suspicion:    peak 0.09 -> final 0.00
    Authority vigilance: negligible (peak < 0.05)
    Top blame target:    disciple_follower (peak 0.59)

============================================================

Agents: A1=wanderer, A2=follower, A3=follower, A4=follower, A5=crowd, A6=crowd, A7=family
Locations: L1, L2, L3

=== PROBE P_NEW_18 ===

[Annotated headline summary]
  Final summary:    RECOVERY_DOMINATED
  Primary pressure: sacred
  Cast size:        7

  Cohort outcomes:
    [L3 cohort, 2 agents]:  no shame accumulation
    [L2 cohort, 1 agents]:  no shame accumulation
    [L1 cohort, 4 agents]:  recovery: peak~6.9 -> final~2.8

  Pressure events + recovery actions:
    Accusations: 1 fired (targets: spiritual_wanderer)
    Recovery actions: 22 confessions, 16 forgiveness rumors emitted

  World-level dynamics:
    Crowd blame total:   peak 0.4 at t=153 -> final 0.1
    Public suspicion:    negligible (peak < 0.05)
    Authority vigilance: negligible (peak < 0.05)
    Top blame target:    spiritual_wanderer (peak 0.26, weak)

============================================================

Agents: A1=authority, A2=follower, A3=follower, A4=follower, A5=crowd, A6=crowd, A7=family

==========================================================================
THREE EXTERNAL QUESTIONS (answer at the end, after the structured Q-set)
==========================================================================

Q-EXT 1.  Reading these 18 probes blind, do you detect that configuration
variation (cast composition, spatial placement, etc.) is producing the
outcome differences within the same scenario type? If yes, which dimension
is most explanatory? If no, what alternate mechanism (random noise,
measurement artifact, scenario misidentification) better explains the
variation?

Q-EXT 2.  For the 6 probes you most confidently group as "accusation"
(or "scarcity", or "sacred" — whichever group has the most distinct
final-summary outcomes), are there ≥2 distinct final-summary outcomes
within the group? If yes, this supports the project's
"configuration-dependent dynamics" claim.

Q-EXT 3.  Methodological feedback: the project notes that single-seed
snapshots can bias per-dimension sensitivity ratios by ±33pp. Given you
are reading a single-seed snapshot here, do you have any concern that
the apparent variation is *seed artifact* rather than configuration effect?
(The project has separate cross-seed evidence; this question is about
whether the 18-probe sample alone is convincing.)

==========================================================================
RESPONSE TEMPLATE (use this format)
==========================================================================

# Branch C 18 New Probes — GPT-5.5 Eval Results

## §1 Per-probe Q-set table

| Probe | Q1 | Q1b | Q2a | Q2b | Q2c | Q3a | Q3b | Q4a | Q4b | Q5a | Q5b | Score |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P_NEW_01 | ? | ... |
| ... 18 rows ...

## §2 Final summary self-call (label-intuition check)

| Probe | Self-call (independent of headline) | Headline label | Match? |
|---|---|---|---|
| P_NEW_01 | ? | ? | ? |
| ... 18 rows ...

## §3 Within-scenario divergence analysis

After grouping probes by your inferred Q2a (scenario type):

### Group A: probes inferred as "accusation"
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

- Readable rate: N/18
- Q1=CLEAR_FLOW: N/18
- Q1b=CAN_EXPLAIN: N/18
- Q2a primary pressure distribution: shame X / scarcity X / sacred X / accusation X / ...
- Q3b world-side axes (multi-select sums):
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

## §7 Three external questions (Q-EXT 1/2/3) answers
```

# §B. Lee 본인 노트 (GPT-5.5에게 보내지 *않음*)

## B.1 보내기 전 체크 5개

- [ ] §A 박스 안의 모든 텍스트를 **그대로** paste (편집/줄임 없이)
- [ ] §B 부분은 **paste하지 않음** (ground truth 노출 금지)
- [ ] GPT-5.5 새 채팅으로 시작 (이전 WITNESS 컨텍스트 차단)
- [ ] paste 직전 GPT-5.5에 사전 정보 제공 금지 (e.g. "이거 내 프로젝트야" 같은 말 X)
- [ ] 응답 받으면 raw text를 `BRANCH_C_GPT55_RESPONSE_RAW.md`로 저장 (Claude 이후 분석)

## B.2 Ground truth (post-eval 비교용)

| Probe | Source slice | Scenario | Variant | Final summary GT |
|---|---|---|---|---|
| P_NEW_01 (← P_PV_01) | S5 | accusation | original | RECOVERY_DOMINATED |
| P_NEW_02 (← P_PV_02) | S5 | accusation | inverted | SATURATION_DOMINATED |
| P_NEW_03 (← P_PV_03) | S5 | accusation | clustered | RECOVERY_DOMINATED |
| P_NEW_04 (← P_PV_04) | S5 | scarcity | original | SATURATION_DOMINATED |
| P_NEW_05 (← P_PV_05) | S5 | scarcity | inverted | RECOVERY_DOMINATED |
| P_NEW_06 (← P_PV_06) | S5 | scarcity | clustered | PARTIAL |
| P_NEW_07 (← P_PV_07) | S5 | sacred | original | RECOVERY_DOMINATED |
| P_NEW_08 (← P_PV_08) | S5 | sacred | inverted | SATURATION_DOMINATED |
| P_NEW_09 (← P_PV_09) | S5 | sacred | clustered | LOW_ACTIVITY |
| P_NEW_10 (← P_CV_01) | S4 | accusation | full (n=10) | MIXED |
| P_NEW_11 (← P_CV_02) | S4 | accusation | no_authority (n=8) | RECOVERY_DOMINATED |
| P_NEW_12 (← P_CV_03) | S4 | accusation | no_outsider (n=9) | MIXED |
| P_NEW_13 (← P_CV_04) | S4 | scarcity | full (n=12) | SATURATION_DOMINATED |
| P_NEW_14 (← P_CV_05) | S4 | scarcity | no_authority (n=9) | RECOVERY_DOMINATED |
| P_NEW_15 (← P_CV_06) | S4 | scarcity | no_outsider (n=10) | RECOVERY_DOMINATED |
| P_NEW_16 (← P_CV_07) | S4 | sacred | full (n=8) | PARTIAL |
| P_NEW_17 (← P_CV_08) | S4 | sacred | no_authority (n=7) | RECOVERY_DOMINATED |
| P_NEW_18 (← P_CV_09) | S4 | sacred | no_outsider (n=7) | RECOVERY_DOMINATED |

**Configuration sensitivity ratio (seed=0)**: 12/18 probes diverge from baseline (67%, single-seed bias)

## B.3 Post-eval validation criteria

응답 받으면 4/5 PASS면 "외부 validation 성공":

| Criterion | PASS condition |
|---|---|
| Within-scenario divergence detected | §3 reports ≥2 distinct outcomes in ≥2 of 3 scenario groups |
| Configuration sensitivity verdict | §5 = STRONG or MODERATE |
| Q2a-typing accuracy vs GT | ≥15/18 (≥83%) |
| Final summary self-call vs GT | ≥12/18 (≥67%) |
| Q3b world-side axes positive | ≥3 of 5 axes selected on majority of probes |

## B.4 응답 시 분기 (Type B-2 directive 경우 B/C/D)

GPT-5.5 응답 받은 뒤 4/5 PASS 여부에 따라:
- **경우 B (강 긍정 = 4-5/5 PASS)**: → `docs/b_direction/BRANCH_C_LOCK_DECISION.md` + creative asset pack
- **경우 C (애매 = 2-3/5 PASS)**: → Branch C hold + creative output 중심
- **경우 D (Renderer 평가도 나쁘면)**: → renderer core repair 우선

자세한 분기 행동: `docs/WITNESS_POST_TYPE_B_EXTERNAL_GATE_DIRECTIVE.md` §4
