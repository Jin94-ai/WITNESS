# Branch C PASS Criteria Checklist — 5 기준 자동 점검표

**Date**: 2026-04-30
**Source**: Lee directive `WITNESS_NEXT_PLAN_AFTER_RENDERER_FREEZE_AND_BRANCHC_GO.md` §5 Step 2
**Companion**: `BRANCH_C_18_PROBES_BLIND_PACKAGE.md` §7 + `BRANCH_C_18_PROBES_SEND_BUNDLE.md` §B.3
**용도**: Branch C GPT-5.5 응답 도착 시 *자동 PASS/FAIL 판정*. 4/5 PASS 이상 = Case S, 2-3/5 = Case M, 0-1/5 = Case F.

---

## 0. 사용 방법

1. Lee가 GPT-5.5에 `BRANCH_C_18_PROBES_SEND_BUNDLE.md` §A를 paste 후 응답 받음
2. 응답 raw text를 `BRANCH_C_GPT55_RESPONSE_RAW.md`에 저장
3. 응답을 §1-§5 5 기준에 매핑 (PASS / PARTIAL / FAIL)
4. §6 종합 판정으로 Case S/M/F 결정
5. 결정 결과에 따라 `RENDERER_FREEZE_DECISION.md` §3 분기 자동 재개

---

## 1. Criterion 1 — Within-scenario divergence detected

**기준**: 응답 §3 (Within-scenario divergence analysis)에서 **≥2 distinct final-summary outcomes in ≥2 of 3 scenario groups**

**점검 방법**:
- GPT-5.5 응답 §3에서 그룹 분석 확인
- "accusation group", "scarcity group", "sacred group" (또는 GPT가 inferred한 group label) 각각의 distinct outcomes 수 카운트
- *2개 이상의 그룹*에서 *2개 이상의 distinct outcomes*가 보고되었는지

**판정**:
- ☐ **PASS** — 2 of 3 (또는 3 of 3) groups가 ≥2 distinct outcomes
- ☐ **PARTIAL** — 1 of 3 group만 ≥2 distinct
- ☐ **FAIL** — 모든 group이 unique outcome 1개 (within-scenario divergence 미감지)

**Lee verdict**:

---

## 2. Criterion 2 — Configuration sensitivity verdict

**기준**: 응답 §5 (Configuration sensitivity verdict) checkbox에서 **STRONG or MODERATE**

**점검 방법**:
- GPT-5.5 응답 §5의 4 checkbox (STRONG / MODERATE / WEAK / NONE) 중 어느 것이 표시됐는지

**판정**:
- ☐ **PASS** — STRONG 또는 MODERATE
- ☐ **FAIL** — WEAK 또는 NONE
- (PARTIAL 없음 — binary)

**Lee verdict**:

---

## 3. Criterion 3 — Q2a typing accuracy vs Ground Truth

**기준**: 응답 §1 Q-set table의 Q2a (primary pressure) 컬럼 vs `BRANCH_C_18_PROBES_SEND_BUNDLE.md` §B.2 Ground Truth Scenario column

**점검 방법**:
- 18 probe 각각의 Q2a 응답값 (shame / fear / sacred / scarcity / accusation / grief / none) 수집
- Ground truth (accusation / scarcity / sacred 9개씩 ≈ 6+6+6) 와 비교
- 정답 개수 카운트

**판정**:
- ☐ **PASS** — ≥15/18 (≥83%)
- ☐ **PARTIAL** — 12-14/18 (66-82%)
- ☐ **FAIL** — ≤11/18 (≤61%)

**정답 수**: ___/18
**Lee verdict**:

### 3.1 Probe별 Q2a 매핑 (작성 시 사용)

| Probe (anonymized) | Ground Truth | GPT-5.5 Q2a | Match? |
|---|---|---|---|
| P_NEW_01 | accusation | | |
| P_NEW_02 | accusation | | |
| P_NEW_03 | accusation | | |
| P_NEW_04 | scarcity | | |
| P_NEW_05 | scarcity | | |
| P_NEW_06 | scarcity | | |
| P_NEW_07 | sacred | | |
| P_NEW_08 | sacred | | |
| P_NEW_09 | sacred | | |
| P_NEW_10 | accusation | | |
| P_NEW_11 | accusation | | |
| P_NEW_12 | accusation | | |
| P_NEW_13 | scarcity | | |
| P_NEW_14 | scarcity | | |
| P_NEW_15 | scarcity | | |
| P_NEW_16 | sacred | | |
| P_NEW_17 | sacred | | |
| P_NEW_18 | sacred | | |

---

## 4. Criterion 4 — Final summary self-call accuracy

**기준**: 응답 §2 self-call (label-intuition check) vs Ground Truth final summary

**점검 방법**:
- 18 probe 각각의 self-call (응답 §2 컬럼) vs ground truth final summary
- 정답 개수 카운트

**판정**:
- ☐ **PASS** — ≥12/18 (≥67%)
- ☐ **PARTIAL** — 9-11/18 (50-66%)
- ☐ **FAIL** — ≤8/18 (≤49%)

**정답 수**: ___/18
**Lee verdict**:

### 4.1 Probe별 final summary 매핑 (작성 시 사용)

| Probe | Ground Truth Final | GPT-5.5 Self-call | Match? |
|---|---|---|---|
| P_NEW_01 | RECOVERY_DOMINATED | | |
| P_NEW_02 | SATURATION_DOMINATED | | |
| P_NEW_03 | RECOVERY_DOMINATED | | |
| P_NEW_04 | SATURATION_DOMINATED | | |
| P_NEW_05 | RECOVERY_DOMINATED | | |
| P_NEW_06 | PARTIAL | | |
| P_NEW_07 | RECOVERY_DOMINATED | | |
| P_NEW_08 | SATURATION_DOMINATED | | |
| P_NEW_09 | LOW_ACTIVITY | | |
| P_NEW_10 | MIXED | | |
| P_NEW_11 | RECOVERY_DOMINATED | | |
| P_NEW_12 | MIXED | | |
| P_NEW_13 | SATURATION_DOMINATED | | |
| P_NEW_14 | RECOVERY_DOMINATED | | |
| P_NEW_15 | RECOVERY_DOMINATED | | |
| P_NEW_16 | PARTIAL | | |
| P_NEW_17 | RECOVERY_DOMINATED | | |
| P_NEW_18 | RECOVERY_DOMINATED | | |

---

## 5. Criterion 5 — Q3b world-side axes positive

**기준**: 응답 §4 (Aggregates) Q3b world-side axes 분포에서 **≥3 of 5 axes selected on majority of probes**

**점검 방법**:
- 응답 §4의 Q3b multi-select sums 확인
- 5 axes (interpersonal / group_alignment / crowd_mood / authority / public_attention) 중 *각 axis가 majority (≥10/18) 응답*에서 선택된 axis 수 카운트

**판정**:
- ☐ **PASS** — 3 axes 이상이 majority (≥10/18 probes)에서 선택
- ☐ **PARTIAL** — 2 axes만 majority
- ☐ **FAIL** — 1 axis 이하만 majority

**Lee verdict**:

### 5.1 Axis별 응답 분포

| Axis | Sum (out of 18) | Majority (≥10)? |
|---|---|:---:|
| interpersonal | | |
| group_alignment | | |
| crowd_mood | | |
| authority | | |
| public_attention | | |

---

## 6. 종합 판정

| Criterion | Status |
|---|---|
| 1. Within-scenario divergence | ☐ PASS / ☐ PARTIAL / ☐ FAIL |
| 2. Configuration sensitivity verdict | ☐ PASS / ☐ FAIL |
| 3. Q2a typing accuracy | ☐ PASS / ☐ PARTIAL / ☐ FAIL |
| 4. Final summary self-call | ☐ PASS / ☐ PARTIAL / ☐ FAIL |
| 5. Q3b world-side axes | ☐ PASS / ☐ PARTIAL / ☐ FAIL |

**PASS count**: ___/5

### 6.1 Case 분기 (자동)

| PASS count | Case | 다음 행동 |
|---|---|---|
| **5/5** | **Case S (strong)** | creative asset pack v1 plan + Branch C lock decision |
| **4/5** | **Case S (PASS)** | (위와 동일) |
| **3/5** | **Case M (moderate)** | 내부 데모만, Branch C lock 보류, retest plan |
| **2/5** | **Case M (moderate-low)** | (위와 동일) |
| **1/5** | **Case F (weak)** | renderer 작업 중단, 구조/평가 재검토 |
| **0/5** | **Case F (fail)** | (위와 동일) |

**최종 Case 판정**: ☐ Case S / ☐ Case M / ☐ Case F

### 6.2 자동 재개 next step

판정 후 `RENDERER_FREEZE_DECISION.md` §3에 따라 자동 재개:

- **Case S** → `docs/creative/CREATIVE_ASSET_PACK_V1_PLAN.md` 작성
- **Case M** → `docs/b_direction/BRANCH_C_HOLD_AND_RETEST_PLAN.md` 작성
- **Case F** → `docs/b_direction/BRANCH_C_NEGATIVE_RESULT_REVIEW.md` 작성

---

## 7. 응답 처리 timeline

1. **Lee paste** → GPT-5.5 새 채팅에 §A 송부
2. **Lee 응답 받음** → raw text를 `BRANCH_C_GPT55_RESPONSE_RAW.md`에 저장
3. **Claude Code 자동 재개** → 이 점검표 §1-5 채움 (raw response 분석)
4. **종합 판정** → §6 자동
5. **Case 분기 실행** → §6.2 next step plan doc 작성

---

## 8. Versioning

| Version | Date | Note |
|---|---|---|
| **v1 (이 doc)** | **2026-04-30** | **Branch C external eval 응답 도착 시 자동 점검표** |
