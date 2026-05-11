# Branch C — GPT-5.5 Send Checklist

**Date**: 2026-04-28
**Phase**: NEXT_STEPS_AFTER_AUTONOMOUS_ROUND.md §4 최우선 2 / §5 Step 3
**Source directive**: `docs/WITNESS_NEXT_STEPS_AFTER_AUTONOMOUS_ROUND.md` §3.3 — Branch C immediate recommendation = GPT-5.5 send with proper disclosure
**Predecessor**: `BRANCH_C_18_PROBES_BLIND_PACKAGE.md` (LOOP 63, 18 probes)

---

## 0. 결정 명시 (Lee directive §3.3)

| Branch C 5 options | 결정 |
|---|---|
| (a) Lock 1차 evidence | bundled into "send"  |
| (b) S1 accusation depth | **SKIP** |
| **(c) GPT-5.5 send** | **PRIORITY 1** |
| (d) S6 engine touch | **DEFER** |
| (e) S2 mechanism | **HOLD** |

→ 이 checklist는 **(c) 진행**.

---

## 1. Send 전 점검 5 항목

### 1.1 Disclosure — seed=0 conditioning 명시 ☐
- [ ] Package 본문에 "all 18 probes generated at seed=0" 명시
- [ ] Cross-seed sensitivity가 ±33pp 변동 가능하다는 caveat (§7.4 paper 참조)
- [ ] Per-dimension 측정 ratio 67%/67%/22%/44%는 seed=0 conditional이라는 표시

**현재 상태**: `BRANCH_C_18_PROBES_BLIND_PACKAGE.md` 작성 시 (LOOP 63) cross-seed 측정 전 — disclosure 없음.

**필요 변경**: package 상단에 disclosure block 추가.

### 1.2 Current claim — paper §6.9 / §7.4 정합성 ☐
- [ ] Branch C 1차 evidence claim (paper §6.9)이 18 probes blind eval 가설과 일치
- [ ] §7.4 single-seed inadequacy 방법론 기여 명시
- [ ] Appendix G referenced (full ensemble characterization)

**현재 상태**: paper §6.9 + Appendix G가 본문 동기화됨 (LOOP 78). 18 probes는 *cross-seed walkback 전* 데이터. *최신* paper 기준으로 send 가능.

**필요 변경**: package에 "paper §6.9 + Appendix G + §7.4 참조" link 명시.

### 1.3 External question 명확화 ☐
GPT-5.5에게 *정확히 무엇을 묻고 싶은가*?

**핵심 question**:
1. 18 probes를 같은 scenario 구분 없이 읽었을 때, *configuration variation*이 outcome 차이를 만든다고 인지하는가?
2. 인지한다면, 어떤 configuration dimension (cast / placement / event count)이 가장 설명적인가?
3. 인지 못 한다면, GPT-5.5가 outcome 차이를 *다른* 메커니즘 (랜덤 / 측정 오류 등)으로 해석하는가?

**필요 변경**: package에 위 3 question 명시 + Q-set과 별도로.

### 1.4 Package completeness — 36 probes vs 18 probes ☐
**현재 옵션**:
- (A) 기존 18 probes (S5 + S4) 그대로 send — minimal, GPT-5.5에게 부담 적음
- (B) 36 probes (S5 + S4 + S3 + S2) full Branch C 1차 evidence — paper §6.9와 일치하지만 부담 큼
- (C) 18 probes + cross-seed ensemble disclosure — middle ground

**Claude bias**: **(C) 권장**. 18 probes는 GPT-5.5 부담 작고, ensemble disclosure로 limitation 명시.

### 1.5 Anonymization — probe filename hint 제거 ☐
**현재 LOOP 63 package §4 note**: "For strictly blind eval, Lee can rename to anonymous P_NEW_01-P_NEW_18 before sending."

- [ ] Lee가 send 전 P_PV_NN / P_CV_NN → P_NEW_NN으로 rename 작업
- [ ] 또는 package 본문에 명시 ("filenames hint variant; for strictly blind eval, treat ID as anonymous")

**Claude bias**: rename은 manual task. package 본문 명시가 더 efficient.

---

## 2. Send 흐름 권장

### 2.1 Pre-send (이번 LOOP에서 자동 진행 가능)
- ☐ 1.1 disclosure block 작성 → package 상단 추가
- ☐ 1.2 paper reference 추가
- ☐ 1.3 3 question block 추가
- ☐ 1.5 anonymization 명시 추가

### 2.2 Send (Lee 직접)
- Lee가 package + GPT-5.5 chat 열어서 paste
- 결과 기다림

### 2.3 Post-send (응답 도착 후)
- ☐ GPT-5.5 응답 → `BRANCH_C_GPT55_RESPONSE_2026-04-XX.md` 작성
- ☐ Validation criteria check (LOOP 63 §7)
- ☐ Branch C lock 또는 추가 cycle 결정

---

## 3. Predicted GPT-5.5 outcomes (자체 판단)

### 3.1 PASS scenario (configuration sensitivity 인지)
- §3 within-scenario divergence 발견
- ≥2/3 scenario groups에서 distinct outcomes 발견
- §5 verdict = STRONG or MODERATE

→ Branch C externally validated. paper §6.9 강화.

### 3.2 PARTIAL scenario (일부만 인지)
- 1 scenario group에서만 divergence 발견
- §5 verdict = WEAK

→ paper §7.2 limitations에 추가.

### 3.3 FAIL scenario (인지 못 함)
- 모든 outcome을 same scenario noise로 해석
- §5 verdict = NONE

→ Branch C claim 외부 invalidated. paper §6.9 약화 또는 retraction.

→ NEXT_STEPS_AFTER_AUTONOMOUS_ROUND.md §7 경우 C: "research deepening 안 함, creative output 중심으로만 계속".

---

## 4. 자율 진행 가능 작업 (이번 LOOP)

§2.1 pre-send 작업이 자율 가능 — package 본문 갱신:

### 4.1 Disclosure block (§1.1)
package 상단 §0 or §1에 추가 가능.

### 4.2 Paper reference link (§1.2)
"Companion: paper §6.9 + Appendix G + §7.4" 추가.

### 4.3 3 external question block (§1.3)
package §2 evaluator instructions에 추가 가능.

### 4.4 Anonymization 명시 (§1.5)
package §4 note 강화.

→ **자율 가능**. 진행하면 send-ready.

---

## 5. Versioning

| Version | Date | Note |
|---|---|---|
| v1 (this) | 2026-04-28 | Lee directive §5 Step 3 — checklist 작성. send-ready 만들기 위한 자율 작업 가능. |
| (post-send) | TBD | GPT-5.5 응답 도착 후 |
