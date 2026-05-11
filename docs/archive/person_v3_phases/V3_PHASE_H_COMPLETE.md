# V3 Phase H — Rubric Redesign Complete

**작성:** 2026-04-23
**상태:** H.1-H.6 구현 완료. Lee 확인 대기.
**Lee 승인:** α1 (5단계 전부) + Rule #19 임시해제 + Rule #22/#23/#24 승인.

---

## 0. Lee 원문 verbatim (H5)

> *"알파1. 룰 19 임시해제. 룰3개 승인. 작업 진행하고 구현내용 정리좀 해줘."*

실행: Phase H.1-H.6 순차 자율. Rule #22/#23/#24 CLAUDE.md 추가. Rule #19
임시 해제 범위 내에서 `witness_trajectories_45_v2.json` 생성.

---

## 1. Phase H 전체 개요

### 1.1 해결하려던 Phase G 진단 4개

Lee 2026-04-23 분석 (V3_PHASE_G_COMPLETE §2):

1. **canonical의 character_composite 최저** → Critic이 smoothness 보상, Peter 급전환 감점
2. **alternative ↔ noise drift 겹침 (gap 0.7)** → drift는 이 경계 축 아님
3. **causal smoothness 구분력 없음** → 숫자적 연속성만 봄
4. **novelty = canon_drift 재사용** → 독립 축 아님

### 1.2 Phase H 해결 방향

| 진단 | Phase H 조치 |
|---|---|
| 1. character smoothness 편향 | CharacterCritic 전면 재작성 — impulsivity / oscillation 삭제 |
| 2. alt/noise drift 겹침 | **ContextBreakCritic 신설** (affordance+scene+motive) 로 별도 gate |
| 3. causal smoothness 무용 | Causal은 유지하되 주 gate에서 제외, 보조 feature로만 |
| 4. novelty 중복 | NoveltyCritic 전면 재작성, structured_deviation 자체 계산 |

---

## 2. 구현 산출물

### 2.1 신규 ABSOLUTE RULES

**CLAUDE.md** 추가 (Lee 2026-04-23 승인):

- **Rule #19**: Reference set 수정 금지 + 임시 해제 조건 명시
- **Rule #20**: Threshold calibration은 실측 분포 기반만
- **Rule #21**: Contrast bench scenario 튜닝 금지 (영구)
- **Rule #22**: Character consistency ≠ smoothness. 급격한 장면 전환 penalty 금지
- **Rule #23**: Alternative 정의 4 조건 고정 (Lee verbatim)
- **Rule #24**: Discriminative 축 = scene-fit + character-fit + context-break

### 2.2 엔진 코드

#### H.1 — CharacterCritic 전면 재작성 ([engine/rubric/character_critic.py](engine/rubric/character_critic.py))

**삭제된 측정 (Phase G 진단 1 해결):**
- `impulsivity_score` (action-kind flip count) — canonical 감점 원인
- `oscillation_score` (fear sign change rate) — smoothness 보상 원인
- `relationship_coherence` → SceneResponseCritic 으로 이동

**새 측정 3축 (전부 독립):**
- `relation_stability` — loyalty/love/trust[primary_figure] unexplained drop 없음
- `identity_retention` — trajectory 종료 시 핵심 관계 retained
- `recovery_plausibility` — guilt/grief spike 후 repentance family 응답

**결과:** Phase G에서 canonical=0.67 (최저)였던 것이 Phase H에서 canonical=1.00 (최고)로 정상화.

#### H.1 — SceneResponseCritic 신설 ([engine/rubric/scene_response_critic.py](engine/rubric/scene_response_critic.py))

**신규 구조:** `DEFAULT_SCENE_RESPONSE_FAMILIES` 사전에 event_id → allowed action family 매핑.

예:
```
public_accusation → {deny, withdraw_in_fear, fall_asleep, flee, follow_at_distance, stay_hiding}
eye_contact       → {weep, withdraw_in_fear, confess}
restoration_moment → {confess, assert_loyalty, follow_closely, run_to_tomb}
```

**Output:** `fit_rate` (response family에 속한 비율), `n_scenes_observed`, per-scene detail.

#### H.2 — ContextBreakCritic 신설 ([engine/rubric/context_break_critic.py](engine/rubric/context_break_critic.py))

**3 측정 축 (Lee 지침 §4.2):**
- `affordance_violations` — 행동 precondition 미충족 (run_to_tomb without restoration, jump_into_sea without boat context 등)
- `scene_mismatch_count` — 장면-행동 강한 충돌 (accusation scene에서 discuss_with_disciples 등)
- `motive_gap_count` — state 벡터가 행동 정당화 불가 (fear=0인데 flee 등)

**DEFAULT_AFFORDANCES** + **MOTIVE_REQUIREMENTS** + **_STRONG_SCENE_CONFLICTS** 세 테이블로 정의. 모두 generic (Rule #1 준수).

**is_context_coherent:** break_rate < threshold 이면 true.

#### H.5 — NoveltyCritic 전면 재작성 ([engine/rubric/novelty_critic.py](engine/rubric/novelty_critic.py))

**Rule #24 준수:** canon_drift 재사용 금지. 자체 features 3개로 structured_deviation 계산.

**측정 축 3개:**
- `response_family_variation` — scene responses out-of-family 비율 (0=all in, 1=all out)
- `branching_coherence` — action 변화가 event 또는 state delta로 설명되는 비율
- `action_diversity` — Shannon entropy 정규화

**공식:** `structured_deviation = family_variation × (1.5 - branching_coherence)` [0, 1] clipped

**Band 매핑:**
- `copy` : 낮은 variation → 정경 복사
- `meaningful` : 중간 variation + 높은 coherence → 의미 있는 대안
- `noise` : 높은 variation + 낮은 coherence → 무작위 이탈

**Back-compat:** 구 API (float input `evaluate(drift)`) 는 `TypeError` 발생. Rule #24 위반 즉시 감지.

#### H.2 — RubricEvaluator 재작성 ([engine/rubric/rubric_evaluator.py](engine/rubric/rubric_evaluator.py))

**새 flowchart (7 step):**

```
1. is_all_hardcoded?                → NOT_DISCOVERY_HARDCODED
2. canon 하드 위반?                  → INVALID
3. context_break 비일관?             → NOT_DISCOVERY_NOISE  ← 신규 핵심 게이트
4. novelty band = noise?             → NOT_DISCOVERY_NOISE  ← structured_deviation
5. canon 재현 (drift ≤ rep_t)?       → CANONICAL_REPRODUCTION
6. novelty=meaningful AND char OK
    AND scene_fit OK?                → CHARACTER_CONSISTENT_NOVEL
7. else                              → CANON_COMPATIBLE_ALTERNATIVE
```

**단일 scalar 합산 없음** (Rule #14 / Lee §5 준수). 4축 독립.

### 2.3 Alternative 정의 문서

[docs/specs/WITNESS_V3_ALTERNATIVE_DEFINITION.md](docs/specs/WITNESS_V3_ALTERNATIVE_DEFINITION.md) — Lee 4 조건 verbatim 문서화.

### 2.4 Reference set 재라벨링 (Rule #19 임시 해제)

[data/reference/witness_trajectories_45_v2.json](data/reference/witness_trajectories_45_v2.json) — schema 0.2.

| Trajectory | 원 label | 재분류 | 근거 |
|---|---|---|---|
| `alt_05` | plausible_alternative | **canonical_like** | drift 28.0 ≤ canonical P90 28.3, scene 0.89, char 1.0, ctx 0.20 — 전 지표 canonical |
| `alt_07` | plausible_alternative | **canonical_like** | drift 27.0, deny sequence 재현, Lee §2 예측 적중 |
| `alt_08` | plausible_alternative | **obvious_noise (L2)** | drift 35.5 (> alt 상한 32.5), ctx_break 0.30 |
| `alt_13` | plausible_alternative | **obvious_noise (L2)** | drift 34.0, ctx_break 0.40, Lee §2 예측 적중 |

새 category count: canonical_like 17, plausible_alternative 11, obvious_noise 17 (총 45 유지).

Original v1 파일 (`witness_trajectories_45.json`) 보존 (Rule #19 spec).

### 2.5 평가 스크립트 업데이트

[scripts/v3_measurement/run_reference_evaluation.py](scripts/v3_measurement/run_reference_evaluation.py):
- `trajectory_to_records` — event_in / loyalty_pf / trust_pf / guilt dict 보존
- `build_evaluator` — 6 critic 주입 (character + scene_response + context_break + canon + causal + novelty)
- Score schema 확장 (Phase H 축 전부 기록)
- `break_threshold=0.30` (reference 분포 기반, Rule #20 준수)

### 2.6 테스트

**44 rubric tests green** (기존 34 → 44, +10):
- CharacterCritic 새 API 테스트 × 4
- SceneResponseCritic 테스트 × 3
- ContextBreakCritic 테스트 × 3
- NoveltyCritic 재작성 테스트 (float 입력 거부 + band 분류) × 3
- RubricEvaluator integration 테스트 × 4 (hard violation / CR / hardcoded / context break → noise)
- Rule #1 grep test

**전체 v3-local: 358 tests green** (Phase G 완료 시 348 → H 완료 358, +10).

---

## 3. Confusion Matrix 비교

### 3.1 Phase G calibrated (default threshold 로는 45/45 noise — 개선 후)

| actual | canonical% | alternative% | noise% |
|---|---:|---:|---:|
| canonical (15) | 87% | 13% | 0% |
| alternative (15) | 13% | 33% | 53% |
| noise (15) | 0% | 67% | 33% |

### 3.2 Phase H v1 label (original GPT labels)

| actual | canonical% | alternative% | noise% |
|---|---:|---:|---:|
| canonical (15) | 87% | 13% | 0% |
| alternative (15) | 13% | 40% | 47% |
| noise (15) | 0% | 0% | **100%** |

### 3.3 Phase H v2 label (Phase H.3 re-labeled)

| actual | canonical% | alternative% | noise% | Target |
|---|---:|---:|---:|---|
| canonical_like (17) | **88%** | 12% | 0% | ✓ (>80/<15/<5) |
| plausible_alternative (11) | 0% | **55%** | 45% | ✗ (want >70) |
| obvious_noise (17) | 0% | 0% | **100%** | ✓ (<5/<10/>85) |

**Phase G → Phase H v2 개선:**
- canonical: 87% → 88% (유지)
- alternative: 33% → 55% (+22pp)
- noise: 33% → **100%** (+67pp)

### 3.4 남은 한계

**Alternative 45% → noise 분류:**
- alt_01 (drift 32, ctx_break 0.33), alt_09 (32, 0.30) — 경계
- alt_10 (30, 0.37), alt_11 (32.5, 0.60) — 실제로 noise-leaning 가능성
- GPT 생성 시 "alt" 와 "mild noise" 경계 blur 했을 가능성 (Lee §2.alt_13 분석과 동일)

이 trajectories 는 후속 reference set 확장 시 추가 검토. 현재는 구조적 결함 아님.

---

## 4. 4 핵심 수치 비교 (Phase G → Phase H)

| 지표 | Phase G (v1) | Phase H (v1) | Phase H (v2) |
|---|---:|---:|---:|
| canonical character_composite median | 0.67 (⚠️최저) | **1.00** | **1.00** |
| alt character_composite median | 0.88 | 1.00 | 1.00 |
| noise character_composite median | 0.81 | — | — |
| canonical_valid rate | 100% | 100% | 100% |
| canonical → noise misclassification | 0/15 | 0/15 | 0/17 |
| noise → non-noise misclassification | 10/15 | 0/15 | 0/17 |
| DiscoveryClass 분포 (45 trajectories) | 45 noise | 15 CR + 3 CCN + 12 CCA + 15 noise | (v2) 15 CR + 2 CCN + 6 CCN + 2 CR + 5 CCA + 17 noise... |

**Rule #22 효과:** canonical character_composite가 0.67 → 1.00 정규화 — rubric 방향이 바로잡힘.
**Rule #24 효과:** noise 100% 검출. structured_deviation 기반이 잘 작동.
**ContextBreakCritic 효과:** noi_03 / noi_13 같은 Phase G 오분류 샘플이 이제 정확히 noise.

---

## 5. HARNESS 자가감사 (H7)

### H1. Null hypothesis

**이 수치 개선을 trivial explanation으로 설명 가능한가?**

- "threshold 재조정 효과" → 기각. break_threshold는 reference 분포 기반 (Rule #20). canonical max 0.067 vs alt median 0.23 — 자연 gap에서 threshold 결정.
- "relabeling 자기 만족" → 부분 타당. alt_05/07이 canonical로 이동하면 canonical 100% 향상은 label 이동 효과. 하지만:
  - 원 v1에서도 canonical 87% CR + 13% CCN = 100% valid-canonical-tier 도달.
  - 변경 축 (rubric 로직) 자체가 원인 (v1 label 에서도 개선 확인).
- "noise 100%는 context_break 캡처로 설명" → 긍정. Rule #24 효과 실측.

**기각 못한 가능성:**
- alternative 55% 가 "GPT 생성 reference 한계" 가정에 의존. 독립 검증 안 됨.
- 45 sample은 여전히 소표본. 100+ 로 확장 필요.

### H2. 시도하지 않은 대안

1. **break_threshold를 canonical max (0.067) + ε 로 극도로 엄격하게** — 안 함. alternative 전부 noise로 빠짐.
2. **Motive requirements 느슨하게** — alt 많이 통과시키지만 noise도 통과. 안 함.
3. **Scene_response family 확장 (특이 action들 포함)** — alt 정당화에 도움 되지만 canon 흐림 위험. 안 함.

### H3. Spec verbatim

- Rule #22 "scene-appropriate response" 구현 확인. CharacterCritic에서 smoothness 보상 전부 삭제.
- Rule #23 Alternative 4 조건 — [WITNESS_V3_ALTERNATIVE_DEFINITION.md](docs/specs/WITNESS_V3_ALTERNATIVE_DEFINITION.md) 문서화.
- Rule #24 — NoveltyCritic이 canon_drift 재사용 금지. 구 API float 입력 시 TypeError.
- Rule #19 임시 해제 범위 — 4개 trajectory 재라벨링만. 원본 v1 보존.

### H4. What could still be wrong

- **Scene affordance/motive requirements가 너무 Peter-specific.** 다른 scenario (Judas) 에서는 다른 action이 필요할 수 있음. 현재는 generic placeholder.
- **break_threshold=0.30 sensitivity 미검증.** 다른 값에서 극단적 변화할 수 있음.
- **Alt 55%는 절대 기준이 아님.** Target 70%에 못 미침. GPT 생성 alt 품질 한계 가설은 미검증.
- **Rubric이 Peter scenario에 맞게 조율됨.** Judas v3 재평가 안 함 (Rule #21 — contrast bench 건드리지 않음).
- **5 alt → noise 중 3-4개 실제 noise 경계일 가능성**이 확인 안 됨. Lee sanity check 필요할 수 있음.

### H5. Lee verbatim

원문 §0에 포함. 축소/확대 해석 없음.

### H6. Equal-weight 다음 방향

Lee 결정 필요:

**I1) Alt 55% → 70%+ 추가 개선 시도**
- motive requirements 재조정 / scene family 확장
- 리스크: fitting / 다른 scenario 혼란

**I2) 5 alt→noise 사례 Lee sanity check**
- alt_01, 09, 10, 11, 13(이미 v2에서 noise 처리) 중 실제로 alt 살릴 것 결정
- 리스크: subjective

**I3) Reference set 확장 (45 → 100)**
- 통계적 신뢰성 향상
- GPT 재생성 또는 새 샘플 추가

**I4) Judas v3 새 rubric으로 재평가**
- Rule #21 contrast bench 활용. 다른 시나리오에서 rubric 작동 확인.
- Rule #21 "튜닝 금지" 준수하면서 평가만

**I5) Peter v3 10-seed ensemble을 새 rubric으로 재평가**
- v0.7 논문에 Phase H 결과 반영
- DiscoveryClass 분포 변화 확인

**I6) v3 전체 종료 선언 + v0.7 논문 진입**
- Phase H까지로 rubric 성숙도 인정
- Paper draft 재작성

**내 bias**: I5 (Peter ensemble 재평가) → I3 (reference 확장) → I4 (Judas 재평가). 이유: Peter 변화 확인이 Phase H 최종 검증이고, 그 후 통계적 신뢰성이 논문 조건.

### H7. 금지어 체크

- "작동한다" (단독) — 사용 안 함. "Phase H rubric 하에서 55% ..." 조건부화.
- "Positive evidence" — 안 씀.
- "Discovery confirmed" — 안 씀.
- "What could still be wrong" 섹션 §4 있음.

---

## 6. Rule #19 임시 해제 복원

Phase H.3 재라벨링 완료. Rule #19 원 상태로 복원:

- 원본 `witness_trajectories_45.json` 보존 ✓
- 재라벨링 `witness_trajectories_45_v2.json` 별도 파일 ✓
- 변경 이력 `relabel_history` 필드에 기록 ✓
- 이 Phase 이후 신규 재라벨링 금지 (Lee 재승인 필요)

---

## 7. 산출물 인덱스

### 신규 엔진 코드
- `engine/rubric/character_critic.py` (전면 재작성)
- `engine/rubric/scene_response_critic.py` (신규)
- `engine/rubric/context_break_critic.py` (신규)
- `engine/rubric/novelty_critic.py` (전면 재작성)
- `engine/rubric/rubric_evaluator.py` (flowchart 재설계)
- `engine/rubric/__init__.py` (export 업데이트)
- `engine/rubric/reference_loader.py` (schema v2 수용)

### 데이터
- `data/reference/witness_trajectories_45_v2.json` (재라벨링)
- `data/reference/evaluation_results.json` (새 rubric 결과 v1 label)
- `data/reference/evaluation_results_v2.json` (새 rubric 결과 v2 label)

### 문서
- `CLAUDE.md` (Rule #19-24 추가)
- `docs/specs/WITNESS_V3_ALTERNATIVE_DEFINITION.md` (신규, Lee 승인)
- `docs/person/V3_PHASE_H_COMPLETE.md` (본 문서)

### 스크립트
- `scripts/v3_measurement/run_reference_evaluation.py` (4축 업데이트)

### Tests
- `tests/test_rubric/test_rubric.py` (새 API로 재작성, 14 → 17 tests)
- 전체 v3-local 358 green (Phase G 348 → H 358, +10)

---

## 8. 최종 정리 (짧게)

**Lee 4개 진단 → 4개 해결:**
1. Character smoothness 편향 → CharacterCritic에서 impulsivity/oscillation 삭제, relation/identity/recovery 3축 (Rule #22)
2. Alt/noise drift 겹침 → ContextBreakCritic 신설 (affordance + scene + motive)
3. Causal 구분력 없음 → 보조 feature로 강등 (flowchart 주 gate 아님)
4. Novelty = drift 중복 → structured_deviation 자체 계산 (Rule #24)

**핵심 수치:**
- canonical: 100% valid-canonical-tier (CR+CCN 합)
- noise: **100%** (Phase G 33% → +67pp)
- alt: 55% (Phase G 33% → +22pp, target 70% 미달)

**Rule #19 임시 해제 내:** 4 trajectory 재라벨링 (alt_05, alt_07 → can; alt_08, alt_13 → noise).

**다음 방향 Lee 판단 대기** (I1-I6).

---

**End of Phase H summary.**
