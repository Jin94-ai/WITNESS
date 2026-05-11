# WITNESS v3.0 Rubric Design Review

## 0. 결론

현재 `4-Axis Discovery Evaluator` 설계 방향은 적합하다.

다만 지금 상태에서 이 모듈을 **Discovery Evaluator**라고 부르면 다소 과장될 수 있다.  
더 정직한 명칭은 다음에 가깝다.

> **Discovery Candidate Triage Tool**  
> 또는  
> **Discovery Candidate Classifier**

즉, 이 evaluator는 “이 결과가 진짜 발견이다”를 증명하는 도구가 아니라, 생성된 trajectory가 다음 조건을 어느 정도 만족하는지 분류하는 도구다.

1. 정경 hard constraint를 위반하지 않는가
2. 상태 변화와 행동이 인과적으로 설명 가능한가
3. 사전 정의한 character trait signature와 맞는가
4. 단순 정경 복사도 아니고 무작위 noise도 아닌가

따라서 최종 label은 truth claim이 아니라 **candidate class**로 해석해야 한다.

---

## 1. 유지해야 할 좋은 설계

### 1.1 4축 독립 critic 구조

현재 4축 구성은 적절하다.

| 축 | Critic | 역할 |
|---|---|---|
| Character Consistency | `character_critic.py` | 인물 trait signature 정합성 |
| Canon Compatibility | `canon_critic.py` | 정경 hard/soft constraint 위반 여부 |
| Causal Coherence | `causal_critic.py` | 상태 변화와 행동의 인과 설명 가능성 |
| Novelty under Constraint | `novelty_critic.py` | 복사/의미 있는 차이/noise 구분 |

이 구조는 WITNESS의 핵심 주장과 맞다.

> “하나의 점수로 서사를 평가하지 않고, 서로 다른 성질의 판단을 독립적으로 보존한다.”

---

### 1.2 Scalar 합산 금지 유지

다음과 같은 방식은 금지하는 것이 맞다.

```text
discovery_score = character * 0.3 + canon * 0.3 + causal * 0.2 + novelty * 0.2
```

이 방식은 설명은 쉬우나, 실제로는 서로 다른 판단 축을 하나의 숫자로 뭉개므로 WITNESS의 정직성을 훼손한다.

현재처럼 `RubricReport`가 4개 sub-report를 별도 필드로 보존하는 방향은 유지해야 한다.

```python
RubricReport:
    character: CharacterReport
    canon: CanonReport
    causal: CausalReport
    novelty: NoveltyReport
    discovery_class: DiscoveryClass
```

---

### 1.3 Rule #14 준수 유지

Rubric은 학습 loss로 사용하면 안 된다.

금지:

```python
loss = rubric_score
loss.backward()
```

이유:

- 모델이 좋은 narrative를 배우는 것이 아니라 rubric의 허점을 공략하게 된다.
- WITNESS는 “발견처럼 보이는 결과”가 아니라 “감사 가능한 결과”를 목표로 한다.
- Rubric은 training layer가 아니라 audit/classification layer여야 한다.

따라서 다음 조건은 계속 유지한다.

- critic 반환 타입은 dataclass report
- `torch.Tensor` 없음
- `.backward()` 없음
- `loss` 사용 없음
- neural trainer가 rubric을 import하지 않음

---

## 2. 핵심 보완점

## 2.1 최종 label에 `CANDIDATE`를 붙일 것

현재 최종 label이 다음처럼 되어 있으면 과장으로 보일 수 있다.

```text
CHARACTER_CONSISTENT_NOVEL
```

추천:

```text
CHARACTER_CONSISTENT_NOVEL_CANDIDATE
```

이유:

- evaluator가 신학적/문학적 진실을 증명하지는 않는다.
- 현재 critic은 휴리스틱 기반이다.
- threshold도 Phase 5+ 실측 보정 전이다.
- 따라서 “발견 확정”이 아니라 “발견 후보”로 표현하는 것이 맞다.

추천 label set:

```text
NOT_DISCOVERY_HARDCODED
INVALID_CANON_VIOLATION
NOT_DISCOVERY_INCOHERENT
CANONICAL_REPRODUCTION
NOT_DISCOVERY_NOISE
CANON_COMPATIBLE_CHARACTER_DRIFT
CHARACTER_CONSISTENT_NOVEL_CANDIDATE
```

---

## 2.2 RubricEvaluator flowchart 수정

현재 flow:

```text
Step 1: is_all_hardcoded?        → NOT_DISCOVERY_HARDCODED
Step 2: hard violation?          → INVALID
Step 3: drift ≤ reproduction_threshold? → CANONICAL_REPRODUCTION
Step 4: drift > noise_threshold? → NOT_DISCOVERY_NOISE
Step 5: drift in meaningful band + character < threshold → CANON_COMPATIBLE_ALTERNATIVE
Step 6: drift in meaningful band + character ≥ threshold → CHARACTER_CONSISTENT_NOVEL
```

수정 추천:

```text
Step 1: is_all_hardcoded?
    → NOT_DISCOVERY_HARDCODED

Step 2: hard canon violation?
    → INVALID_CANON_VIOLATION

Step 3: causal coherence below minimum?
    → NOT_DISCOVERY_INCOHERENT

Step 4: drift ≤ copy_threshold?
    → CANONICAL_REPRODUCTION

Step 5: drift > noise_threshold?
    → NOT_DISCOVERY_NOISE

Step 6: meaningful drift + character below threshold
    → CANON_COMPATIBLE_CHARACTER_DRIFT

Step 7: meaningful drift + character pass + causal pass
    → CHARACTER_CONSISTENT_NOVEL_CANDIDATE
```

변경 이유:

1. Causal coherence는 discovery 판정의 핵심 gate이므로 앞쪽에 있어야 한다.
2. Character threshold 미달을 `CANON_COMPATIBLE_ALTERNATIVE`라고 부르면 너무 긍정적으로 보인다.
3. 최종 결과는 discovery 확정이 아니라 candidate로 표현해야 한다.

---

## 2.3 Character Critic 명칭과 구조 수정

### 문제

현재 Character Critic은 다음 3요소 평균으로 composite을 계산한다.

1. Impulsivity
2. Relationship coherence
3. Fear-courage oscillation

이 조합은 “베드로다움” 전체를 측정하기에는 약하다.

문제점:

- 베드로 고유성이 아니라 “즉각반응형 인물” 일반성을 측정할 가능성이 있다.
- 다른 충동적/관계반응형 인물도 높은 점수를 받을 수 있다.
- 단순 평균은 특정 축의 실패를 다른 축의 성공으로 덮어버린다.

예:

```text
impulsivity = 1.0
relationship_coherence = 0.1
oscillation = 1.0
average = 0.7
```

평균은 높지만, relationship coherence가 낮다면 Peter-like signature라고 보기 어렵다.

---

### 명칭 수정 추천

현재:

```text
Character Consistency
```

추천:

```text
Trait Signature Consistency
```

또는:

```text
Character Trait Consistency
```

공식 문서에서는 “베드로다움”이라는 표현을 줄이고 다음처럼 명시한다.

```text
This critic measures Peter-like trait signature match, not full theological or literary identity.
```

한국어:

```text
이 critic은 베드로라는 인물 전체의 고유성을 판정하는 것이 아니라, 사전에 정의한 Peter-like trait signature와의 정합성을 측정한다.
```

---

### 구조 수정 추천

단순 평균 대신 minimum gate를 추가한다.

```python
@dataclass
class CharacterReport:
    impulsivity_score: float
    relationship_coherence_score: float
    oscillation_score: float
    passed_minimum_signature: bool
    weak_axes: list[str]
    composite_score: float  # display only, not decision source
```

판정 예시:

```python
passed_minimum_signature = (
    impulsivity_score >= 0.4
    and relationship_coherence_score >= 0.5
    and oscillation_score >= 0.3
)
```

핵심 원칙:

- composite score는 표시용이다.
- 최종 decision은 minimum gate를 우선한다.
- 약한 축은 `weak_axes`에 명시한다.

---

## 2.4 Novelty Critic을 drift 하나로 보지 말 것

### 문제

현재 novelty는 `copy_threshold`, `noise_threshold` 중심이다.

| Threshold | 의미 |
|---|---|
| `copy_threshold` | drift 이하면 canon copy |
| `noise_threshold` | drift 초과면 random deviation |

이 구조 자체는 유용하지만, drift 하나만으로는 다음 둘을 구분하기 어렵다.

```text
A. 정경과 다르지만 의미 있는 대안
B. 그냥 상태값이 흔들려서 이상해진 결과
```

새롭다는 것은 canon에서 멀어진 것이 아니라, **설명 가능한 방향으로 다르게 간 것**이다.

---

### 수정 추천

Novelty는 최소한 두 축으로 분리한다.

```text
1. distance_from_canon
2. structuredness_of_difference
```

추천 report:

```python
@dataclass
class NoveltyReport:
    canon_drift: float
    copy_like: bool
    noise_like: bool
    structured_difference_score: float
    changed_axes: list[str]
    interpretation: str
```

해석 원칙:

```text
low drift + low structuredness  → CANONICAL_REPRODUCTION
medium drift + high structuredness → meaningful alternative candidate
high drift + low structuredness → NOT_DISCOVERY_NOISE
high drift + high structuredness → requires manual review
```

Novelty는 Causal Coherence와 연결되어야 한다.

> 의미 있는 다름은 반드시 인과적으로 설명 가능해야 한다.

---

## 2.5 Causal Critic을 가장 강하게 보강할 것

4축 중 포트폴리오 설득력을 가장 크게 좌우하는 것은 `causal_critic.py`다.

WITNESS의 핵심 주장은 다음이다.

> “작가가 임의로 만든 줄거리가 아니라, 상태 변화와 사건 압력에서 결과가 나왔다.”

따라서 causal critic은 단순 보조 축이 아니라 discovery candidate 판정의 핵심 gate가 되어야 한다.

---

### 최소 측정 항목

`causal_critic.py`는 최소한 다음을 봐야 한다.

```text
1. 상태 변화 전후 delta가 존재하는가?
2. delta를 유발할 event/pressure가 직전 window 안에 있는가?
3. action이 해당 state/pressure 조합에서 설명 가능한가?
4. 설명 불가능한 jump가 몇 개인가?
5. pressure와 action 방향이 정렬되는가?
```

추천 report:

```python
@dataclass
class CausalReport:
    explained_transition_ratio: float
    unexplained_jumps: list[TransitionIssue]
    pressure_action_alignment: float
    temporal_gap_violations: list[TemporalGapViolation]
    causal_chain_length_avg: float
    passed_causal_gate: bool
```

추천 gate:

```python
passed_causal_gate = (
    explained_transition_ratio >= 0.7
    and pressure_action_alignment >= 0.6
    and len(unexplained_jumps) <= max_allowed_jumps
)
```

수치는 placeholder이며 Phase 5+에서 calibration 필요.

---

## 2.6 Canon Critic은 hard/soft 분리를 유지할 것

Canon critic이 너무 보수적으로 설계되면 discovery가 불가능해진다.

잘못된 방향:

```text
정경과 조금만 다르면 invalid
```

올바른 방향:

```text
Hard constraint 위반만 invalid.
Soft deviation은 report에 남기되 discovery 가능성을 막지 않는다.
```

추천 구조:

```python
@dataclass
class CanonReport:
    hard_violations: list[CanonViolation]
    soft_deviations: list[CanonDeviation]
    hard_pass: bool
    soft_compatibility_score: float
```

분류 기준:

| 구분 | 예시 | 처리 |
|---|---|---|
| Hard constraint | 핵심 사건 발생 여부, 생존/사망, 명시적 사건 순서 | 위반 시 INVALID |
| Soft constraint | 정서 방향성, 관계 긴장도, 행동 가능 범위, 분위기 | report에 기록 |

---

## 2.7 Threshold는 `uncalibrated`로 명시할 것

현재 값:

```text
copy_threshold = 1.5
noise_threshold = 15.0
```

이 값들은 출발점으로는 가능하지만, 확정값처럼 보이면 위험하다.

추천 표현:

```text
initial placeholder threshold
```

또는:

```text
calibration_required_default
```

추천 config:

```yaml
rubric:
  novelty:
    copy_threshold: 1.5
    noise_threshold: 15.0
    calibration_status: "uncalibrated_phase3_placeholder"
  character:
    impulsivity_min: 0.4
    relationship_coherence_min: 0.5
    oscillation_min: 0.3
    calibration_status: "uncalibrated_phase3_placeholder"
  causal:
    explained_transition_min: 0.7
    pressure_action_alignment_min: 0.6
    calibration_status: "uncalibrated_phase3_placeholder"
```

Report에도 calibration status를 포함한다.

```json
{
  "calibration_status": "uncalibrated_phase3_placeholder"
}
```

---

## 3. 추가해야 할 Non-Claims 섹션

계획서에 반드시 아래 섹션을 추가하는 것을 추천한다.

```md
## Non-Claims

This evaluator does not prove theological correctness.
This evaluator does not prove literary quality.
This evaluator does not discover meaning by itself.

This evaluator only classifies whether a generated trajectory is:

1. canon-compatible,
2. causally explainable,
3. trait-consistent,
4. non-copy and non-noise.

Therefore final labels should be interpreted as candidate classes, not final truth claims.
```

한국어 버전:

```md
## Non-Claims

이 evaluator는 신학적 정답을 증명하지 않는다.
이 evaluator는 문학적 완성도를 증명하지 않는다.
이 evaluator는 의미를 스스로 발견하지 않는다.

이 evaluator가 하는 일은 생성된 trajectory가 다음 조건을 만족하는지 분류하는 것이다.

1. 정경 hard constraint를 위반하지 않는가
2. 상태 변화와 행동이 인과적으로 설명 가능한가
3. 사전 정의한 character trait signature와 맞는가
4. 단순 복사도 아니고 무작위 noise도 아닌가

따라서 최종 label은 truth claim이 아니라 discovery candidate class로 해석해야 한다.
```

---

## 4. 수정 후 추천 문서 구조

기존 계획서를 다음 순서로 정리하는 것을 추천한다.

```text
1. Purpose
2. Non-Claims
3. 4-Axis Critic Overview
4. RubricEvaluator Flowchart
5. Character / Trait Signature Critic
6. Canon Compatibility Critic
7. Causal Coherence Critic
8. Novelty under Constraint Critic
9. Rule #14 Compliance
10. No Scalar Aggregation Rule
11. Threshold Calibration Status
12. Acceptance Criteria
```

---

## 5. Acceptance Criteria 수정안

기존 acceptance에 아래 항목을 추가한다.

```text
- Final discovery labels use CANDIDATE where appropriate.
- Causal coherence gate runs before novelty classification.
- Character critic uses minimum-axis gates, not only average composite.
- Novelty critic separates canon drift from structured difference.
- Threshold config includes calibration_status.
- Report includes weak_axes / violations / unexplained_jumps.
- Non-Claims section is present in the design doc.
- Rubric is not imported by neural trainer.
- No scalar total discovery score is produced.
```

---

## 6. 우선순위

바로 고칠 우선순위는 다음이다.

```text
P0. 최종 label에 CANDIDATE 붙이기
P0. causal coherence gate를 Step 3으로 올리기
P0. Rule #14 / no scalar aggregation 유지 확인

P1. character composite 평균 대신 minimum gate 추가
P1. novelty를 drift + structuredness로 분리
P1. threshold에 uncalibrated 표시 추가

P2. Canon hard/soft report 구조 정리
P2. Non-Claims 섹션 추가
P2. acceptance criteria 업데이트
```

---

## 7. 최종 평가

| 항목 | 평가 |
|---|---:|
| 구조 적합성 | 8 / 10 |
| 정직성 | 8.5 / 10 |
| 포트폴리오 설득력 | 7 / 10 |
| Critic 강도 | 5.5 / 10 |
| Phase 3 적용 가능성 | 8 / 10 |

최종 판단:

> 설계 방향은 맞다.  
> 다만 지금은 “발견 평가기”가 아니라 “발견 후보 분류기”로 낮춰 부르는 것이 맞다.  
> Character, Novelty, Causal critic은 gate 중심으로 강화해야 한다.

---

## 8. Claude Code Directive Draft

아래 directive를 Claude Code에 전달하면 된다.

```text
WITNESS v3.0 Rubric Design Hardening Directive

Goal:
Refine the 4-Axis Discovery Evaluator into a Discovery Candidate Classifier.
Do not present rubric output as final truth or proven discovery.

Constraints:
- Do not use rubric as training loss.
- Do not import rubric from neural trainer.
- Do not produce a single scalar discovery score.
- Keep 4 critic reports independent.
- Mark all thresholds as uncalibrated Phase 3 placeholders.

Required changes:
1. Rename final novel label to CHARACTER_CONSISTENT_NOVEL_CANDIDATE.
2. Update RubricEvaluator flow:
   - hardcoded check
   - hard canon violation check
   - causal coherence gate
   - canonical reproduction check
   - noise check
   - character drift check
   - novel candidate check
3. Add causal gate before novelty classification.
4. Modify CharacterReport:
   - keep component scores
   - add passed_minimum_signature
   - add weak_axes
   - keep composite_score as display-only
5. Modify NoveltyReport:
   - separate canon_drift and structured_difference_score
   - add copy_like, noise_like, changed_axes, interpretation
6. Modify CanonReport:
   - separate hard_violations and soft_deviations
   - only hard violations invalidate output
7. Add calibration_status to config and reports.
8. Add Non-Claims section to the design doc.
9. Update tests to confirm:
   - no scalar total score
   - no trainer imports rubric
   - hard violation invalidates
   - causal failure returns NOT_DISCOVERY_INCOHERENT
   - meaningful drift + character pass returns CHARACTER_CONSISTENT_NOVEL_CANDIDATE

Acceptance:
- All existing tests pass.
- New tests cover all revised decision branches.
- Rubric output clearly states candidate status.
- Thresholds are marked uncalibrated.
- No raw theological/literary truth claim is made by evaluator.
```
