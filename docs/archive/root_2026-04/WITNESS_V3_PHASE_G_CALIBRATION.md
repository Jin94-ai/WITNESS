# WITNESS v3.0 — Phase G: Reference Set Calibration

**생성 배경:**
Phase 2 v2 Dynamics + B2 retune + D1-D4 확장 완료 후 여전히 DiscoveryClass 
10/10 noise. 두 외부 LLM (Gemini, ChatGPT) 공통 진단:

> *"현재는 자가 기준으로 자가 판정하는 상태. 의미 있는 엄격성인지 알 수 없다.
> Threshold 재정의가 아니라 먼저 reference trajectory set 구축이 필요하다."*

**이 Phase의 본질:**
GPT가 생성한 외부 reference set (45 trajectories)을 활용하여:
1. 현재 Rubric의 threshold가 **적절히 calibrated 되어 있는지** 검증
2. 분포 기반 threshold 재설정
3. Recovery profile 변수별 분리 (현재 너무 깨끗)

**입력 자산:**
- `witness_trajectories_45.json` (1.67MB, 65243 lines, GPT 생성)
  - 15 Canonical-like (`can_01` ~ `can_15`)
  - 15 Plausible alternative (`alt_01` ~ `alt_15`)
  - 15 Obvious noise (`noi_01` ~ `noi_15`)
    - Level 1 (subtle): 5개
    - Level 2 (context drift): 5개
    - Level 3 (character break): 5개

**외부성 보장 (자가참조 회피):**
- 생성자: GPT (외부 모델)
- 평가자: Claude Code (Witness RubricEvaluator)
- 감독자: Opus (이 대화)
- 판정자: Lee (sanity check)

네 역할이 완전 분리되어 ChatGPT가 경고한 *"자가 기준으로 자가 판정"* 문제 회피.

**선행 조건:**
- Phase 2 v2 Dynamics + B2 + Cat F 완료 상태
- 1446+ tests green
- `engine/rubric/rubric_evaluator.py` 정상 작동
- GPT 생성 JSON 파일 `data/reference/witness_trajectories_45.json` 배치

---

## 0. 작업 방식

### 0.1 Lee 개입 최소화 (이전 지시 유지)

Step G1-G5 전부 Claude Code 자율. Lee 개입은:
- **Step G6** (sanity check, 9개 trajectory만)
- **Step G7** (Phase G 종료 후 다음 방향 결정)

### 0.2 금지 사항

- **Reference set 내용 수정 금지** (외부성 유지)
- **Threshold를 "느낌대로" 조정 금지** (분포 기반만)
- **Judas policy retune 금지** (ChatGPT 강한 경고, ABSOLUTE 영구 유지)
- **Neural policy 도입 금지** (Phase 5 영역, 지금 아님)
- **새 Phase 진입 금지** (Phase G 완료 후 Lee 결정)

### 0.3 ABSOLUTE RULES 추가

**Rule #19 신설:**
> Reference set (외부 생성)의 내용은 Claude Code가 수정 불가.
> Schema 검증만 허용. 품질 판정은 Lee sanity check만.

**Rule #20 신설:**
> Threshold calibration은 reference set의 실측 분포만 근거.
> 경험적 수동 조정 / "느낌으로 약간 낮춤" 금지.

**Rule #21 신설 (영구):**
> Contrast bench scenario (Judas, 3번째 시나리오 등)는 튜닝 대상 아님.
> Peter 스타일 boost/attenuation 금지. Policy/edges 실패는 
> **일반화 실패의 진단 자료** 로만 사용.

---

## 1. Step G1 — Reference Set 로딩 + Schema 검증

### 1.1 작업

```python
# 위치: data/reference/witness_trajectories_45.json
# 복사: /mnt/user-data/uploads/witness_trajectories_45.json
```

### 1.2 로더 구현

```
engine/rubric/reference_loader.py (신규)

class ReferenceTrajectory:
    metadata: dict
    ticks: list[TickRecord]
    
class ReferenceSet:
    canonical_like: list[ReferenceTrajectory]
    plausible_alternative: list[ReferenceTrajectory]
    obvious_noise: list[ReferenceTrajectory]
    
    # Noise level subdivision
    noise_level_1: list
    noise_level_2: list
    noise_level_3: list
```

### 1.3 검증 테스트

```
tests/test_rubric/test_reference_set.py

- schema_version == "witness.v3.trajectory-set.0.1"
- count == 45
- 3 categories × 15 each
- Noise: 5 × 3 levels
- 모든 trajectory length == 30
- Action vocab 준수 (21 actions)
- State field 완전성:
    scalar (13): fear, hope, grief, confusion, joy, anger, awe,
                 fatigue, hunger, vitality, doubt, resolve, trauma
    target_aware (6): love, loyalty, trust, belonging, guilt, shame
- Value range: 0 <= v <= 10.01
```

### 1.4 완료 조건

- [ ] Loader 구현
- [ ] 45 trajectories 전체 로딩 성공
- [ ] Schema 검증 0 error
- [ ] 1446+ tests + 신규 tests green

---

## 2. Step G2 — Rubric Evaluator 적용

### 2.1 작업

`engine/rubric/rubric_evaluator.py` 의 4 critic을 45 trajectories에 전부 적용.

### 2.2 출력 형식

```python
# scripts/v3_measurement/run_reference_evaluation.py (신규)

각 trajectory 결과:
{
    "trajectory_id": "can_01",
    "category": "canonical_like",
    "noise_level": None,
    "scores": {
        "character_composite": float,
        "canon_valid": bool,
        "canon_soft_drift": float,
        "causal_smoothness": float,
        "novelty_band": "copy" | "meaningful" | "noise",
        "novelty_drift": float,
    },
    "discovery_class": "CANONICAL_REPRODUCTION" | ...
}

저장: data/reference/evaluation_results.json
```

### 2.3 분포 분석

```python
# scripts/v3_measurement/analyze_reference_distribution.py (신규)

각 category 별 각 score axis의 분포:
- min / q1 / median / q3 / max
- mean ± stdev
- histogram (10 bins)

저장: data/reference/distribution_analysis.json
```

### 2.4 완료 조건

- [ ] 45 trajectories 전부 rubric 점수 계산
- [ ] 분포 JSON 저장
- [ ] 현재 threshold 기준 DiscoveryClass 분포 기록

---

## 3. Step G3 — 분포 시각화 + 해석

### 3.1 작업

3 category × 4 score axis 분포를 텍스트 리포트로.

### 3.2 리포트 형식

```
docs/person/V3_REFERENCE_DISTRIBUTION_REPORT.md

Section 1: Distribution table
    |               | canonical_like | alternative | noise (L1) | noise (L2) | noise (L3) |
    | drift med     |                |             |            |            |            |
    | drift q1-q3   |                |             |            |            |            |
    | character med |                |             |            |            |            |
    | ...

Section 2: Category separation
    - canonical_like의 drift 분포가 obvious_noise 분포와 얼마나 겹치는가?
    - 겹치면 분류 불가능 — rubric 설계 재검토 신호
    - 분리되면 threshold calibration 가능

Section 3: Current threshold 판정
    - noise_threshold=20.0, reproduction_threshold=2.0 등이 실측 분포와 
      얼마나 정렬되는지
    - misclassification 케이스 목록 (e.g., canonical인데 noise로 판정된 것)
```

### 3.3 관찰 항목 (Claude Code 자율 해석)

- Canonical_like의 character_composite가 높은 편인가?
- Noise Level 3의 canon_valid가 false인가?
- Alternative과 Noise L1의 경계가 명확한가?
- 각 축에서 어느 category 구분이 가장 뚜렷한가?

### 3.4 완료 조건

- [ ] 분포 리포트 작성
- [ ] 각 축의 category separation 정량화
- [ ] 현재 threshold의 misclassification 기록

---

## 4. Step G4 — Threshold Calibration (분포 기반만)

### 4.1 원칙

**Rule #20 엄수.** "느낌대로" 금지. 아래 공식만.

### 4.2 Calibration 공식

```
# ChatGPT 권고 원문 (spec §6.2)

reproduction_threshold 
  = canonical_like 의 canon_soft_drift 90th percentile
  (= canonical의 90%가 이 이하로 들어와야 함)

noise_threshold 
  = obvious_noise 의 canon_soft_drift 10th percentile
  (= noise의 90%가 이 이상으로 나와야 함)

character_min_composite 
  = plausible_alternative 의 character_composite 25th percentile
  (= alternative의 75%가 이 이상으로 들어와야 함)

copy_threshold
  = canonical_like 의 novelty_drift 10th percentile
  (= canonical의 90%가 이 이하로 들어와야 copy로 분류)
```

### 4.3 Validation

Calibrated threshold로 45 trajectories 재평가:

```
목표 confusion matrix:

               | predicted
               | canonical | alternative | noise
------+--------+-----------+-------------+-------
actual| can    |   >80%    |   <15%      |  <5%
      | alt    |   <10%    |   >70%      |  <20%
      | noise  |   <5%     |   <10%      |  >85%
```

### 4.4 불가능한 경우

분포가 겹쳐서 위 목표 달성 불가능이면:
- **Threshold 이동으로 해결 불가능** = rubric 자체 재설계 필요
- 이 경우 Lee 판단 요청 (Step G6에서)

### 4.5 완료 조건

- [ ] 분포 기반 새 threshold 계산
- [ ] Validation 완료 (confusion matrix)
- [ ] 목표 confusion 달성 또는 rubric 재설계 필요 판정
- [ ] `data/reference/calibrated_thresholds.json` 저장

---

## 5. Step G5 — Recovery Profile 분리

### 5.1 작업

ChatGPT 지적:
> *"fear 9.9 → 0, confusion 9.92 → 0, grief 10.0 → 0 은 너무 완전하다.
> Recovery edge가 합성되어 과보정됐을 가능성."*

### 5.2 변수별 감쇠 프로파일 (ChatGPT 권고)

```
현재: 모든 변수 half-life 8 일괄 decay

변경안:
  fear:      fast spike / fast decay   (half-life 4-6)
  confusion: medium spike / medium decay (half-life 6-8)
  grief:     slow decay + memory echo   (half-life 12-15, floor 0.1)
  guilt:     slow decay + rebound on reminder events (half-life 10, rebound trigger)
  shame:     context-dependent decay    (presence of target가 있으면 decay 느림)
  anger:     medium decay               (half-life 6)
  awe:       slow decay                 (half-life 10)
```

### 5.3 구현 위치

```
engine/person/state_transitions.py
  RecoveryProfile 클래스 신설
  각 변수별 decay_fn(state, world, elapsed_ticks)
```

### 5.4 Reference set 활용

Canonical_like 15개의 tick 1-30 구간에서 각 변수의 실제 궤적 참고하여 decay rate 
조정. (단, 하드코딩 금지 — 일반 원칙만.)

### 5.5 재검증

Recovery profile 변경 후:
- Peter v3 100-tick 장기 실측 재실행
- tick 100에 완전 0 수렴하는지 여부 관찰
- grief가 long tail 가지는지
- 10-seed ensemble로 dynamics 안정성 확인

### 5.6 완료 조건

- [ ] 변수별 decay profile 구현
- [ ] 100-tick 장기 실측 재실행
- [ ] grief long tail 확인
- [ ] 기존 1446+ tests green 유지

---

## 6. Step G6 — Lee Sanity Check

### 6.1 작업

Lee가 9개 trajectory만 직접 검토. 그 이상 안 보임.

### 6.2 Lee가 볼 것

- **3개 canonical_like** 중 random: `can_03`, `can_08`, `can_12`
- **3개 alternative** 중 random: `alt_02`, `alt_07`, `alt_13`
- **3개 noise (각 level 하나씩)**: `noi_03` (L1), `noi_08` (L2), `noi_13` (L3)

각 trajectory에 대해 **Claude Code가 요약 리포트 작성**:

```
Trajectory: can_03
Category: canonical_like
Rubric score:
  character_composite: 0.92
  canon_valid: True
  canon_soft_drift: 1.8
  novelty_band: copy
  discovery_class: CANONICAL_REPRODUCTION
  
Action summary at key ticks:
  T17: deny    T19: deny    T20: deny    T21: weep    T28: confess
  
Trajectory-level reading:
  정경 3회 부인 재현 충실. tick 21-22 통곡 후 tick 28에 복귀.
  drift 1.8 → 거의 그대로 재현.
```

이 리포트를 받고 Lee가:
- (a) "이건 정말 canonical처럼 보인다" → OK
- (b) "이건 어색하다 / 이게 왜 canonical이냐" → Flag
- (c) "noise인데 noise 같지 않다" → Flag

### 6.3 Flag 처리

Lee가 flag한 trajectory는:
- GPT 생성 품질 문제 → 해당 trajectory 제외 (Rule #19 내 허용 범위)
- Rubric 판정 문제 → Step G4 재조정

### 6.4 완료 조건

- [ ] 9개 trajectory 요약 리포트 작성
- [ ] Lee 검토 결과 수신
- [ ] Flag 처리 완료

---

## 7. Step G7 — Phase G 종료 + 다음 방향 판정

### 7.1 판정 항목

Phase G 종료 시점에 다음 3가지 결과 가능:

**Case α — Threshold calibration 성공**
- 새 threshold로 confusion matrix 목표 달성
- Recovery profile 합리적으로 분리됨
- → Peter v3 10-seed 재실행 → DiscoveryClass 변화 관찰
- → 변화 있으면 Rule #13 "발견" 개념 재평가 가능

**Case β — Rubric 자체 재설계 필요**
- 분포가 너무 겹쳐서 threshold로 해결 안 됨
- → 4 critic 중 어느 것을 강화/교체할지 판단
- → Phase H (Rubric redesign) 로 진행

**Case γ — Reference set 재생성 필요**
- Lee sanity check에서 다수 flag
- → GPT 재생성 요청 또는 기준 변경

### 7.2 보고

```
docs/person/V3_PHASE_G_COMPLETE.md

- Step G1-G6 결과 요약
- Calibrated threshold 최종값
- Recovery profile 최종값
- Case α/β/γ 판정
- Lee 결정 요청 사항 (다음 Phase)
```

### 7.3 Lee 결정 사항

Step G7에서 Lee는:
- 다음 Phase 방향 결정 (H 또는 다른 방향)
- Case β인 경우 rubric 재설계 범위
- Case γ인 경우 reference set 재생성 여부

---

## 8. 산출물 구조

```
data/reference/                                    (신규)
  witness_trajectories_45.json                     (GPT 생성, 외부)
  evaluation_results.json                          (Step G2)
  distribution_analysis.json                       (Step G2)
  calibrated_thresholds.json                       (Step G4)

engine/rubric/
  reference_loader.py                              (Step G1 신규)
  
engine/person/
  state_transitions.py                             (Step G5 수정)
  recovery_profile.py                              (Step G5 신규)

scripts/v3_measurement/
  run_reference_evaluation.py                      (Step G2 신규)
  analyze_reference_distribution.py                (Step G2 신규)

tests/test_rubric/
  test_reference_set.py                            (Step G1 신규)
  test_calibration.py                              (Step G4 신규)

docs/person/
  V3_REFERENCE_DISTRIBUTION_REPORT.md              (Step G3 신규)
  V3_SANITY_CHECK_SUMMARIES.md                     (Step G6 신규)
  V3_PHASE_G_COMPLETE.md                           (Step G7 신규)
```

---

## 9. 세션 권장

| Step | 예상 세션 | 비고 |
|---|---|---|
| G1 (로더) | 0.5 세션 | Schema 검증 |
| G2 (rubric 적용) | 0.5 세션 | 45 trajectories 평가 |
| G3 (분포 분석) | 1 세션 | 리포트 작성 |
| G4 (calibration) | 1 세션 | 분포 기반 |
| G5 (recovery profile) | 1-2 세션 | 가장 큰 작업 |
| G6 (sanity check) | 0.5 세션 | Claude Code는 요약 작성만 |
| G7 (종료 판정) | 0.5 세션 | 문서 작성 |

**총 5-6 세션.** Step G1-G5는 Lee 개입 없이 진행.

---

## 10. 진행 보고 형식

```
Step G1 ✓ Loader 구현. 45 trajectories 로딩. Schema 0 error.
Step G2 ✓ Rubric 45 trajectory 평가 완료. 분포 JSON 저장.
Step G3 ✓ 분포 리포트 작성. Canonical/noise separation {명확/부분/불명확}.
Step G4 ✓ Calibrated thresholds: {reproduction_t}, {noise_t}, {character_min}.
          Confusion matrix: canonical {X}% / alt {Y}% / noise {Z}%.
Step G5 ✓ Recovery profile 분리. 100-tick grief long tail 확인.
Step G6 ⏸ Lee sanity check 요청 (9 trajectories).
```

막혔을 때:
```
[BLOCKED at Step N]
이유: [구체]
가능 원인: (a) ... (b) ... (c) ...
Lee 판단 필요.
```

---

## 11. 이전 경고 재확인 (ChatGPT + Gemini)

반드시 피할 것:

### 경고 1 — "구조 완성" 착각
Phase G 완료는 "구조 완성"이 아니라 "평가 프레임 calibration 완료"일 뿐.
그 다음 단계는 여전히 많이 남음.

### 경고 2 — Judas retune
Phase G는 Peter 시나리오만 사용. Judas는 **contrast bench** 로만 
(Rule #21 영구). 이번 Phase에서 Judas 건드리지 않음.

### 경고 3 — Recovery 과보정
현재 recovery가 *"너무 깨끗"* (fear/grief/confusion이 tick 100에 0). 
Step G5에서 **변수별 분리**. grief는 long tail 유지 (0 수렴 X).

### 경고 4 — 분포 기반 엄수
"느낌으로 약간 조정" 절대 금지. Rule #20 엄수. 오직 percentile 공식.

---

## 12. 이 Phase의 의미

Lee의 원래 문제 제기:
> *"하드코딩된 결과를 발견이라고 칭하는 부분이 좀 있는 거 같아."*

지금까지 해결된 것:
- Rule #13: 발견 3종 분할 ✓
- Rule #14: 학습 reward ≠ 평가 rubric ✓
- Spike 6 BC retrospectively "NOT_DISCOVERY_INTERPOLATION" 철회 ✓

**Phase G가 해결하는 것:**
- Rubric 자체의 엄격성이 "진짜"인지 검증 (외부 reference set으로)
- Threshold의 arbitrary 성격 제거 (분포 기반)
- 자기참조 평가 구조 탈피

Phase G 완료 후에야 *"Rule #13 범주의 진짜 발견이 0건"* 이라는 현재 상태의 
**신뢰성** 을 말할 수 있음.

---

## 13. 한 줄 요약

**"외부 생성 reference set 45개로 Rubric threshold를 분포 기반 calibrate.
생성-평가-감독-판정 4역할 완전 분리. Step G1-G5 자율, G6에서 Lee 9개 
sanity check, G7에서 Case α/β/γ 판정."**

---

## 부록 A — Lee 승인 완료 항목 (재확인)

이 Phase 전에 Lee가 이미 승인한 것:

| 항목 | Lee 승인 |
|---|---|
| Reference set 구축 필요성 (ChatGPT 1순위) | ✓ |
| Reference set 외부 생성 (Opus/GPT) | ✓ |
| GPT가 생성 (최종 선택) | ✓ |
| 45 trajectories (15 × 3) | ✓ (GPT 제출) |
| Judas retune 영구 금지 | ✓ (이전 지시 유지) |
| Neural policy 지금 아님 | ✓ (이전 지시 유지) |

이 6개는 Claude Code가 재확인 없이 진행.

---

## 부록 B — Reference Set 품질 검증 (Opus 확인 완료)

GPT 생성 `witness_trajectories_45.json` (1.67MB, 65243 lines)에 대해 Opus가 
spot check 완료:

**Schema 준수:** 45 × 30 × 19 변수 = 에러 0건
**카테고리 분포:** 15/15/15, noise level 5/5/5
**Canonical 품질:** can_01~05의 tick 17/19/20 전부 deny, tick 21 weep, 
                 tick 28 confess — 정경 완전 재현
**Alternative 품질:** alt_01~05에서 회피/위임/자백 등 다양한 패턴, 
                   부인 없거나 1회만, 정경 모순 없음
**Noise Level 1:** 고발 상황에서 discuss_with_disciples 등 맥락 이탈
**Noise Level 3:** 고발 상황에서 jump_into_sea, draw_sword 등 캐릭터 완전 붕괴
**State dynamism:** can_01 guilt 0→1.7→3.3→4.95→7.1 (부인 누적), 
                   tick 21 weep에서 grief 0→3.0 점프 — 정확한 심리 흐름

**판정:** 즉시 사용 가능.
