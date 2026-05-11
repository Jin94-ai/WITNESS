# V3 Phase G — Complete (Case β 판정 + Phase H 계획)

**작성:** 2026-04-23
**판정:** **Case β (Rubric 자체 재설계 필요)** — Lee 2026-04-23 확정.

---

## 0. Lee 원문 verbatim (H5)

> *"지금 이상한 수치들은 대부분 threshold 문제라기보다 rubric 구조 문제로 보는 게 맞습니다. (...) canonical / alternative / noise를 나누는 기준을 'distance' 중심에서 'scene-fit + character-fit + context-break' 중심으로 재설계해야 한다."*

(전체 분석은 세션 로그 참조.)

---

## 1. Phase G 결과 요약 (Step G1-G6)

| Step | 결과 |
|---|---|
| G1 | `engine/rubric/reference_loader.py` + 14 schema tests green |
| G2 | 45 trajectories 평가. Default threshold로 **45/45 NOT_DISCOVERY_NOISE** |
| G3 | 분포 리포트. Canonical/noise drift **NO OVERLAP**. Character backwards. |
| G4 | Percentile calibration. rep=28.30 / noise=29.00 / char=0.843 / copy=23.50. Canonical 87% ✓, Alt 33% ✗, Noise 33% ✗ |
| G5 | Variable-specific recovery profile. grief HL=13 floor=0.15, guilt HL=11 floor=0.10 (long tail 확보) |
| G6 | 9 trajectory Lee 검토 완료 |

**Tests:** 348 v3-local green (+14 reference + 8 calibration).

---

## 2. Lee 진단 4 핵심 신호 (verbatim 해석)

### 2.1 canonical의 character_composite가 최저 (0.67)

**원인:** Character critic이 **"베드로다움"이 아니라 "부드럽고 안정적 trajectory"를 보상** 중.
- canonical은 deny→weep→withdraw→confess 급격한 전환 많음 → impulsivity 높음 → 점수 손해
- 매끈한 alternative가 점수 유리

**의미:** Character critic 방향이 반대.

### 2.2 alternative ↔ noise drift 겹침 (median 29.5 vs 29.0)

**원인:** drift는 canonical vs non-canonical 분리에는 쓸만하나, **alternative vs noise 분리 못 함**. 둘 다 canon_valid=100% 이므로 hard filter 무효.

**의미:** drift 기반 threshold는 이 구분 축으로 부적합.

### 2.3 causal smoothness 구분력 없음 (0.85-0.88 세 category 모두)

**원인:** synthetic reference가 서사 형식 시퀀스이므로 숫자적 연속성은 대부분 유사. Smoothness는 **"숫자가 매끈한가"** 이지 **"장면에 맞는 이유-반응 구조인가"** 가 아님.

**의미:** Causal critic이 wrong question에 답하는 중.

### 2.4 novelty가 canon_drift 재사용 (novelty_drift == canon_soft_drift)

**원인:** Novelty critic이 별도 feature 없이 drift 값만 재활용.

**의미:** 4축 중 실질 3축. "맥락 이탈 / 물리적 부적합 / 동기-행동 불일치" 포착 못함. `jump_into_sea` L3 noise가 alternative로 흘러가는 근원.

---

## 3. 판정

### 3.1 Case β 확정

`Phase G spec §4.4` + `§7.1`:
> *"분포가 너무 겹쳐서 threshold로 해결 안 되면: rubric 자체 재설계 필요."*

- Alternative/noise gap 0.7 — threshold 이동 overfit 위험
- Character critic 방향성 문제 — threshold 조정으로 안 됨
- Novelty 중복 — 구조적 문제
- Causal smoothness 구분력 없음 — feature 재설계 필요

**→ Phase H (Rubric 재설계) 진입 필요.**

### 3.2 현재 상태의 재해석 (H1 null hypothesis)

지금까지 Peter v3 10-seed ensemble에서 **10/10 NOT_DISCOVERY_NOISE** 판정은:
- "엔진이 낮은 품질" 신호 **아님**
- "Rubric이 엔진 출력과 canonical 사이의 차이를 discriminative feature로 못 잡음" 신호

즉 **Rule #13 범주의 "0 discovery" 주장 자체가 현 rubric 하에서만 유효**. Phase H 후 같은 trajectory가 다른 class로 분류될 수 있음.

---

## 4. Lee의 Misclassification 재해석 (4개 경계 샘플)

| trajectory | 현재 판정 | Lee 해석 | 구분 |
|---|---|---|---|
| `alt_07` (drift 27.0) | canonical_reproduction | "실제로 canonical-like에 더 가까울 수 있음" | **Label 품질** |
| `alt_13` (drift 34.0) | not_discovery_noise | "alternative로 보기 어려울 수 있음" | **Label 품질** |
| `noi_03` (L1, drift 29.0) | canon_compatible_alternative | "맥락 위반 / affordance 위반 미포착" | **Rubric 결함** |
| `noi_13` (L3, drift 29.0) | canon_compatible_alternative | "jump_into_sea 장면/캐릭터 불가능 미포착" | **Rubric 결함** |

**→ Rubric 결함과 Reference label 품질이 섞여 있음.** Phase H 작업은 둘 다 다뤄야.

---

## 5. Phase H 실행 계획 (Lee 5 우선순위)

### H.1 Character critic 분해 (1순위)

**현재:** `CharacterCritic.composite` = impulsivity × relationship × oscillation → smoothness 편향.

**재설계:**
- **A. `character_consistency`**: target-aware relation 일관성 + 감정/의지 장기 연속성 + recovery plausibility + 핵심 장면 후 붕괴 여부
- **B. `scene_response_fit`**: accusation → conceal/deny/confess/freeze family / eye_contact → weep/withdraw/grief / restoration → repair/confess/resolve family

두 개로 분리, 각 독립 점수. Composite 만들지 않음 (Lee 지시 "4축 독립 유지").

**파일:**
- `engine/rubric/character_critic.py` 분해
- `engine/rubric/scene_response_critic.py` 신규

### H.2 Noise 전용 critic 신설 (2순위)

**새 critic:** `ContextBreakCritic` 또는 `SceneFitCritic`.

**측정 축 4종:**
1. **affordance violation** — 해당 장면/장소에서 그 행동 가능한가 (scene_affordances table 필요)
2. **scene mismatch** — accusation scene에서 discuss / jump_into_sea 등
3. **motive gap** — 현재 state ↔ action 단절 (state vector 거리와 expected action profile)
4. **physical implausibility** — 공간/상황상 불가능

**파일:**
- `engine/rubric/context_break_critic.py` 신규
- `content/peter/v3/scene_affordances.json` 신규 (장면별 허용 action group)

### H.3 45 reference trajectories 재라벨링 (3순위)

**대상:** alt_07 / alt_13 / noi_03 / noi_13 등 경계 샘플 + alt/noise 구분 기준 문서.

**방법:** Lee의 세부 기준 (§3.2) 에 맞춰 재검토. 경우에 따라 일부 재분류.

**Rule #19 영향:** "reference set 내용 수정 금지" 조항과 충돌.
- 명시적 label 이동은 Rule #19 violation
- **Lee 승인 필수** 또는 별도 reference_set_v2 파일 생성 (v1 보존)

**제안:** `witness_trajectories_45_v2.json` 신규 + 변경 사유 명시.

### H.4 Alternative 정의 문서화 (4순위)

**Lee 정의 채택:**
> *"alternative = canonical과 다르지만, 장면 적합성 + 캐릭터 일관성 + 인과 정합성을 유지하는 trajectory"*

요건 4개:
1. hard canon 위반 없음
2. 주요 장면에서 response family plausibly adjacent
3. drift canonical > noise 구간 (bounded)
4. motive/action 연결 설명 가능

**파일:**
- `docs/specs/WITNESS_V3_ALTERNATIVE_DEFINITION.md` 신규

### H.5 Novelty critic 재설계 (5순위)

**현재:** novelty_drift == canon_soft_drift — 독립 축 아님.

**재설계:**
- distance 사용 금지
- **structured deviation score**: response family variation + plausibly branching vs random / 동일 state에서 novel action의 motive consistency
- canon과의 거리가 아니라 "변이의 구조성" 측정

**파일:**
- `engine/rubric/novelty_critic.py` 전면 재작성

---

## 6. Phase H 작업 범위 추정

| 작업 | 예상 세션 | 영향 |
|---|---|---|
| H.1 Character 분해 | 1 | 기존 character_critic test 재작성 |
| H.2 Context-break critic | 2 | scene_affordances content 작성 |
| H.3 Re-labeling | 1 | reference_set_v2 (Lee 승인 필수) |
| H.4 Alt 정의 문서 | 0.3 | 문서만 |
| H.5 Novelty 재설계 | 1 | test 전면 교체 |
| 전체 validation + 45 trajectories 재평가 | 1 | confusion matrix 재확인 |

**총 6-7 세션.**

---

## 7. Rule 후보 (Lee 승인 대기)

Phase H 진입 시 ABSOLUTE RULES 확장 제안:

- **Rule #22 후보** (character critic 방향): "Character consistency는 smoothness가 아니라 scene-appropriate response. Fear/anger oscillation 자체를 impulsivity penalty로 쓰지 말 것. Canonical의 급격한 장면 전환은 오히려 character-consistent 증거."
- **Rule #23 후보** (alternative 정의 고정): Lee §3.2 정의 4 조건 verbatim 채택. 임의 label 금지.
- **Rule #24 후보** (context-break 독립 축): "Discriminative feature는 distance 아니라 scene-fit + character-fit + context-break 3축 조합."

Lee 승인 시 CLAUDE.md에 추가.

---

## 8. HARNESS 자가감사 (H7)

### H1 null hypothesis
"현재 수치는 trivial explanation (rubric이 우연히 이렇게 나옴)으로 설명 가능한가?" → 기각. Lee 분석에서 4개 신호가 한 방향으로 정렬 (critic 방향, drift gap, smoothness 구분력, novelty 중복).

### H2 시도하지 않은 대안
- **"현재 rubric에서 threshold만 조정"** — 실행했음 (G4), canonical 87% / alt+noise 실패. 한계 확인.
- **"reference set 100개로 확장"** — 안 함. Lee 권고 없음.
- **"Threshold를 soft boundary로 변경"** — 안 함. 구조 문제라 의미 없음.

### H3 spec verbatim
- spec §4.4 "threshold로 해결 안 되면 rubric 재설계" 충족.
- spec §7.1 Case β 정의: "분포 겹침 → rubric 재설계 + Phase H" 충족.
- Rule #19 "reference set 수정 금지" — H.3 재라벨링은 이 조항 저촉. **Lee 명시 승인 없이 진행 금지**.

### H4 What could still be wrong
- Lee 분석 중 "Character critic 방향이 반대"는 강한 가설이지만 검증 안 됨. Phase H.1 실제 구현 후 재평가 필요.
- Reference set label 품질이 불확실 — GPT 생성의 품질 상한 있음.
- "scene-fit" 측정이 Rule #1 (engine person-agnostic) 와 충돌 가능 — scenario-specific scene_affordances 를 content/로 빼야 함.
- 45개 샘플은 통계적 신뢰성 낮음 (3 categories × 15 = 소표본). P25/P75 추정 불확실성.

### H5 Lee 원문 verbatim
§0에 Lee 결론 문장 포함. 5 우선순위 spec §5에 대응. 축소 해석 없음.

### H6 Equal-weight 선택지 (Lee 결정용)

**H-start 방향:**
- **α1) Phase H 5단계 전부 순차 실행** (6-7 세션)
- **α2) Phase H 1+2 핵심만 (Character 분해 + Context-break critic)** — 구조 변화 가장 크므로 우선 검증
- **α3) Phase H 3 (재라벨링) 먼저** — label 품질 불확실성 해소 후 rubric 재설계
- **α4) Phase H 진입 전 reference set 확장 (45→100)** — 통계적 신뢰성 우선
- **α5) Phase G에서 정지, v0.7 논문 방향 재검토** — 분류 불가능 상태에서 "Rule #13 0 discovery" 주장 자체 재평가

**내 bias**: **α2 (Character 분해 + Context-break critic)**. 이유: Lee가 명시한 4개 원인 중 2개가 즉시 해결. H.3 재라벨링은 H.1+H.2 결과로 자연스레 재정렬될 것.

**Lee가 다른 bias (H4 경고: 내 bias는 잘못될 수 있음) 를 가지면 그 경로 따름.**

### H7 금지어 체크
- "positive 증거" / "작동한다" / "발견" — 사용 안 함
- "구조 문제 확정" — Lee verbatim 인용 조건부화

---

## 9. 산출물 인덱스 (Phase G)

### 코드
- `engine/rubric/reference_loader.py`
- `engine/person/recovery_profile.py`
- `engine/person/state_transitions.py` (수정)

### 스크립트
- `scripts/v3_measurement/run_reference_evaluation.py`
- `scripts/v3_measurement/analyze_reference_distribution.py`
- `scripts/v3_measurement/calibrate_thresholds.py`
- `scripts/v3_measurement/generate_sanity_check.py`

### 데이터
- `data/reference/witness_trajectories_45.json` (GPT 생성, Rule #19)
- `data/reference/evaluation_results.json`
- `data/reference/evaluation_results_calibrated.json`
- `data/reference/distribution_analysis.json`
- `data/reference/calibrated_thresholds.json`

### 문서
- `docs/person/V3_REFERENCE_DISTRIBUTION_REPORT.md`
- `docs/person/V3_SANITY_CHECK_SUMMARIES.md`
- `docs/person/V3_PHASE_G_COMPLETE.md` (본 문서)

### 테스트 (22 신규, 전체 348 green)
- `tests/test_rubric/test_reference_set.py` (14)
- `tests/test_rubric/test_calibration.py` (8)

---

## 10. Lee 결정 요청

**질문 1:** Phase H α1/α2/α3/α4/α5 중 선택?
**질문 2:** H.3 재라벨링 시 Rule #19 임시 해제 (또는 reference_set_v2 생성 경로)?
**질문 3:** Rule #22/#23/#24 후보 승인 여부?

**답 받는 대로 Phase H 착수.**

---

**End of Phase G.**
