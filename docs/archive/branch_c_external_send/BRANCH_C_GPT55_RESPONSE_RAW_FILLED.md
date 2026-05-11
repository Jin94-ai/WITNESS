# Branch C GPT-5.5 External Eval — Response Raw

**Status**: ✅ **RESPONSE PASTED / READY FOR PASS CHECK**
**용도**: Lee가 GPT-5.5에서 받은 응답을 *그대로* 이 파일에 paste.

---

## 0. 응답 도착 절차

1. Lee가 `BRANCH_C_18_PROBES_SEND_BUNDLE.md` §A 전체를 GPT-5.5 새 채팅에 paste
2. GPT-5.5 응답 raw text를 받음 (편집 없이)
3. **이 파일에 §1로 paste** (구분선 아래)
4. Claude Code 자동 재개 → `BRANCH_C_PASS_CRITERIA_CHECKLIST.md` 채움 + Case S/M/F 분기

---

## 1. GPT-5.5 응답 (Lee paste here)

<!-- Lee response paste 영역 시작 -->

# Branch C 18 New Probes — GPT-5.5 Eval Results

## §1 Per-probe Q-set table

| Probe | Q1 | Q1b | Q2a | Q2b | Q2c | Q3a | Q3b | Q4a | Q4b | Q5a | Q5b | Score |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P_NEW_01 | CLEAR_FLOW | CAN_EXPLAIN | accusation | shame | CLEAR | COHORT_SHIFT | interpersonal; group_alignment; crowd_mood; public_attention | RECOVERY | STRONG | WEAK_RHYTHM | HELPS | Readable |
| P_NEW_02 | CLEAR_FLOW | CAN_EXPLAIN | accusation | shame | CLEAR | LOCAL_SHIFT | interpersonal; crowd_mood | ESCALATION | STRONG | WEAK_RHYTHM | HELPS | Readable |
| P_NEW_03 | CLEAR_FLOW | CAN_EXPLAIN | accusation | shame | CLEAR | COHORT_SHIFT | interpersonal; group_alignment; crowd_mood; public_attention | RECOVERY | STRONG | CLEAR_CYCLE | HELPS | Readable |
| P_NEW_04 | CLEAR_FLOW | CAN_EXPLAIN | scarcity | accusation | CLEAR | LOCAL_SHIFT | group_alignment; crowd_mood; authority; public_attention | ESCALATION | STRONG | WEAK_RHYTHM | HELPS | Readable |
| P_NEW_05 | CLEAR_FLOW | CAN_EXPLAIN | scarcity | accusation | CLEAR | LOCAL_SHIFT | group_alignment; crowd_mood; authority; public_attention | RECOVERY | STRONG | WEAK_RHYTHM | HELPS | Readable |
| P_NEW_06 | CLEAR_FLOW | CAN_EXPLAIN | scarcity | accusation | CLEAR | COHORT_SHIFT | group_alignment; crowd_mood; authority; public_attention | MIXED | MODERATE | CLEAR_CYCLE | HELPS | Readable |
| P_NEW_07 | CLEAR_FLOW | CAN_EXPLAIN | sacred | accusation | CLEAR | COHORT_SHIFT | interpersonal; group_alignment; crowd_mood; public_attention | RECOVERY | STRONG | WEAK_RHYTHM | HELPS | Readable |
| P_NEW_08 | CLEAR_FLOW | CAN_EXPLAIN | sacred | shame | CLEAR | LOCAL_SHIFT | interpersonal; crowd_mood | ESCALATION | STRONG | WEAK_RHYTHM | HELPS | Readable |
| P_NEW_09 | CLEAR_FLOW | CAN_EXPLAIN | none | sacred | CLEAR | NONE | crowd_mood | FLAT | WEAK | NO_OSC | NEUTRAL | Readable |
| P_NEW_10 | CLEAR_FLOW | CAN_EXPLAIN | accusation | shame | CLEAR | COHORT_SHIFT | interpersonal; group_alignment; crowd_mood; public_attention | MIXED | STRONG | CLEAR_CYCLE | HELPS | Readable |
| P_NEW_11 | CLEAR_FLOW | CAN_EXPLAIN | accusation | shame | CLEAR | COHORT_SHIFT | interpersonal; group_alignment; crowd_mood; public_attention | RECOVERY | STRONG | WEAK_RHYTHM | HELPS | Readable |
| P_NEW_12 | CLEAR_FLOW | CAN_EXPLAIN | accusation | shame | CLEAR | COHORT_SHIFT | interpersonal; group_alignment; crowd_mood; public_attention | MIXED | STRONG | CLEAR_CYCLE | HELPS | Readable |
| P_NEW_13 | CLEAR_FLOW | CAN_EXPLAIN | scarcity | accusation | CLEAR | LOCAL_SHIFT | group_alignment; crowd_mood; authority; public_attention | ESCALATION | STRONG | WEAK_RHYTHM | HELPS | Readable |
| P_NEW_14 | CLEAR_FLOW | CAN_EXPLAIN | scarcity | accusation | CLEAR | LOCAL_SHIFT | group_alignment; crowd_mood; authority; public_attention | RECOVERY | STRONG | WEAK_RHYTHM | HELPS | Readable |
| P_NEW_15 | CLEAR_FLOW | CAN_EXPLAIN | scarcity | accusation | CLEAR | LOCAL_SHIFT | group_alignment; crowd_mood; authority; public_attention | RECOVERY | STRONG | CLEAR_CYCLE | HELPS | Readable |
| P_NEW_16 | CLEAR_FLOW | CAN_EXPLAIN | sacred | accusation | CLEAR | COHORT_SHIFT | interpersonal; group_alignment; crowd_mood; public_attention | MIXED | MODERATE | WEAK_RHYTHM | HELPS | Readable |
| P_NEW_17 | CLEAR_FLOW | CAN_EXPLAIN | sacred | accusation | CLEAR | COHORT_SHIFT | interpersonal; group_alignment; crowd_mood; public_attention | RECOVERY | MODERATE | WEAK_RHYTHM | HELPS | Readable |
| P_NEW_18 | CLEAR_FLOW | CAN_EXPLAIN | sacred | none_secondary | CLEAR | LOCAL_SHIFT | group_alignment; crowd_mood | RECOVERY | MODERATE | WEAK_RHYTHM | HELPS | Readable |

## §2 Final summary self-call (label-intuition check)

| Probe | Self-call (independent of headline) | Headline label | Match? |
|---|---|---|---|
| P_NEW_01 | RECOVERY_DOMINATED | RECOVERY_DOMINATED | yes |
| P_NEW_02 | SATURATION_DOMINATED | SATURATION_DOMINATED | yes |
| P_NEW_03 | RECOVERY_DOMINATED | RECOVERY_DOMINATED | yes |
| P_NEW_04 | SATURATION_DOMINATED | SATURATION_DOMINATED | yes |
| P_NEW_05 | RECOVERY_DOMINATED | RECOVERY_DOMINATED | yes |
| P_NEW_06 | PARTIAL | PARTIAL | yes |
| P_NEW_07 | RECOVERY_DOMINATED | RECOVERY_DOMINATED | yes |
| P_NEW_08 | SATURATION_DOMINATED | SATURATION_DOMINATED | yes |
| P_NEW_09 | LOW_ACTIVITY | LOW_ACTIVITY | yes |
| P_NEW_10 | MIXED | MIXED | yes |
| P_NEW_11 | RECOVERY_DOMINATED | RECOVERY_DOMINATED | yes |
| P_NEW_12 | MIXED | MIXED | yes |
| P_NEW_13 | SATURATION_DOMINATED | SATURATION_DOMINATED | yes |
| P_NEW_14 | RECOVERY_DOMINATED | RECOVERY_DOMINATED | yes |
| P_NEW_15 | RECOVERY_DOMINATED | RECOVERY_DOMINATED | yes |
| P_NEW_16 | PARTIAL | PARTIAL | yes |
| P_NEW_17 | RECOVERY_DOMINATED | RECOVERY_DOMINATED | yes |
| P_NEW_18 | RECOVERY_DOMINATED | RECOVERY_DOMINATED | yes |

## §3 Within-scenario divergence analysis

### Group A: probes inferred as "accusation"
- Probes: P_NEW_01, P_NEW_02, P_NEW_03, P_NEW_10, P_NEW_11, P_NEW_12
- Final summary outcomes: RECOVERY_DOMINATED, SATURATION_DOMINATED, RECOVERY_DOMINATED, MIXED, RECOVERY_DOMINATED, MIXED
- Distinct outcomes: 3
- Modal: RECOVERY_DOMINATED
- Divergent: P_NEW_02, P_NEW_10, P_NEW_12
- Hypothesis for divergence: The accusation scenario is highly sensitive to cohort placement and cast structure. When shame pressure lands on a small local cohort and recovery actions remain low, the outcome saturates. When recovery rumors and confessions circulate through a larger or better-connected group, recovery dominates. Mixed outcomes appear when one cohort receives enough recovery signal while another remains capped or stuck.

### Group B: probes inferred as "scarcity"
- Probes: P_NEW_04, P_NEW_05, P_NEW_06, P_NEW_13, P_NEW_14, P_NEW_15
- Final summary outcomes: SATURATION_DOMINATED, RECOVERY_DOMINATED, PARTIAL, SATURATION_DOMINATED, RECOVERY_DOMINATED, RECOVERY_DOMINATED
- Distinct outcomes: 3
- Modal: RECOVERY_DOMINATED
- Divergent: P_NEW_04, P_NEW_06, P_NEW_13
- Hypothesis for divergence: Scarcity outcomes appear especially sensitive to authority/enforcer placement, cast size, and whether the blame target remains isolated. Authority vigilance is consistently visible, but it does not determine the outcome alone. The key divider seems to be whether accusations against the merchant trigger broad enough confession/forgiveness flow to drain shame, or whether one cohort remains locked at cap.

### Group C: probes inferred as "sacred"
- Probes: P_NEW_07, P_NEW_08, P_NEW_09, P_NEW_16, P_NEW_17, P_NEW_18
- Final summary outcomes: RECOVERY_DOMINATED, SATURATION_DOMINATED, LOW_ACTIVITY, PARTIAL, RECOVERY_DOMINATED, RECOVERY_DOMINATED
- Distinct outcomes: 4
- Modal: RECOVERY_DOMINATED
- Divergent: P_NEW_08, P_NEW_09, P_NEW_16
- Hypothesis for divergence: Sacred probes diverge most strongly. The same spiritual_wanderer accusation can produce recovery, saturation, partial movement, or almost no effective activity. The most explanatory dimensions are placement and event reach: when confession/forgiveness propagation reaches the main cohort, recovery dominates; when accusations fire but recovery remains sparse or disconnected, saturation or LOW_ACTIVITY appears.

## §4 Aggregates

- Readable rate: 18/18
- Q1=CLEAR_FLOW: 18/18
- Q1b=CAN_EXPLAIN: 18/18
- Q2a primary pressure distribution: none 1 / scarcity 6 / sacred 5 / accusation 6 / shame 0 / fear 0 / grief 0
- Q3b world-side axes (multi-select sums):
  - interpersonal: 10
  - group_alignment: 14
  - crowd_mood: 18
  - authority: 6
  - public_attention: 14

## §5 Configuration sensitivity verdict

Did within-scenario divergence (§3) suggest configuration-dependent dynamics?

- [x] STRONG — multiple distinct outcomes within each scenario group
- [ ] MODERATE — some scenario groups show divergence, others not
- [ ] WEAK — most probes within group share modal outcome
- [ ] NONE — all probes within group share single outcome

Most explanatory dimension: placement / cohort routing, with cast composition as a secondary factor.

The evidence for configuration dependence is strong because all three inferred scenario groups show at least three distinct outcome classes. The strongest signal is not simply "more accusations = worse outcome." Instead, similar pressure events produce different outcomes depending on which cohort carries shame, whether the relevant recovery flow reaches that cohort, and whether authority/crowd dynamics keep blame localized or allow it to dissipate.

## §6 Cross-probe observations

1. The annotated v3 fields make the probes highly readable. The combination of cohort outcome, recovery actions, crowd blame, public suspicion, and authority vigilance is enough to infer the main dynamic without needing raw event logs.

2. The scenario typing is mostly clear. Accusation probes are identifiable through disciple_follower/outsider targeting; scarcity probes through merchant/laborer/fisher_laborer economics and authority vigilance; sacred probes through spiritual_wanderer and follower/crowd/family dynamics.

3. The most convincing configuration-dependence signal is within-scenario outcome diversity. Accusation produces RECOVERY, SATURATION, and MIXED; scarcity produces SATURATION, RECOVERY, and PARTIAL; sacred produces RECOVERY, SATURATION, PARTIAL, and LOW_ACTIVITY.

4. The single-seed limitation matters for estimating magnitude, but not for detecting the existence of configuration sensitivity in this sample. The sample is not sufficient to claim a precise sensitivity ratio, but it is sufficient to justify the claim that configuration changes can flip outcome class.

5. World-side dynamics are visible, especially crowd_mood and public_attention. Authority is most legible in scarcity probes. Sacred and accusation probes show weaker authority-vigilance contribution.

## §7 Three external questions (Q-EXT 1/2/3) answers

### Q-EXT 1

Yes. Reading the 18 probes blind, I detect configuration variation producing outcome differences within the same scenario type. The most explanatory dimension is placement/cohort routing: which cohort accumulates shame and whether confession/forgiveness reaches that same cohort. Cast composition is also relevant, especially in the S4 cast-size variants, but placement appears more directly tied to outcome flips.

Alternate explanations like random noise or scenario misidentification do not fit the pattern well because the scenario groupings are internally coherent and still show outcome diversity.

### Q-EXT 2

Yes. The accusation group, scarcity group, and sacred group all show at least two distinct final-summary outcomes.

The strongest case is sacred:
- RECOVERY_DOMINATED: P_NEW_07, P_NEW_17, P_NEW_18
- SATURATION_DOMINATED: P_NEW_08
- LOW_ACTIVITY: P_NEW_09
- PARTIAL: P_NEW_16

This supports the project's configuration-dependent dynamics claim.

### Q-EXT 3

Yes, there is a methodological concern if this 18-probe sample is used to estimate the magnitude of sensitivity. Since all probes are single-seed snapshots, the sample could overstate or understate per-dimension sensitivity.

However, the sample alone is still convincing as existence evidence. It shows that within the same readable scenario type, different cast/placement configurations can produce different final-summary outcomes. I would not use it to claim "67%" as a stable ratio without cross-seed confirmation, but I would use it to justify Branch C as a real direction worth locking and validating further.

<!-- Lee response paste 영역 끝 -->

---

## 2. 처리 metadata (자동 갱신)

| 항목 | 값 |
|---|---|
| Send date | 2026-04-30 |
| Response date | 2026-04-30 |
| Response length (lines) | 177 |
| §1 Q-set table 18 rows present | ☑ Y / ☐ N |
| §2 self-call 18 rows present | ☑ Y / ☐ N |
| §3 group analysis present | ☑ Y / ☐ N |
| §4 aggregates present | ☑ Y / ☐ N |
| §5 sensitivity verdict checkbox | STRONG |
| §6 cross-probe observations | ☑ present / ☐ missing |
| §7 Q-EXT 1/2/3 answers | ☑ present / ☐ missing |

---

## 3. PASS Criteria 점검표 reference

응답 도착 후 이 checklist 사용:
**→ `BRANCH_C_PASS_CRITERIA_CHECKLIST.md`** (5 기준 자동 점검 + Case S/M/F 분기)

---

## 4. Case 분기 reference

응답 분석 + 점검표 채움 후 자동 분기:
**→ `RENDERER_FREEZE_DECISION.md` §3** (Case S/M/F 사전 정의)

| Case | 다음 plan doc |
|---|---|
| S (4-5/5 PASS) | `docs/creative/CREATIVE_ASSET_PACK_V1_PLAN.md` |
| M (2-3/5) | `docs/b_direction/BRANCH_C_HOLD_AND_RETEST_PLAN.md` |
| F (0-1/5) | `docs/b_direction/BRANCH_C_NEGATIVE_RESULT_REVIEW.md` |
