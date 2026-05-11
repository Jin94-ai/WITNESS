# WITNESS Story Viability Validation Plan

> 목적: WITNESS가 생성한 `StoryCandidate`가 실제 창작에 쓸 수 있는 **Scene Brief**와 **1-page Treatment**로 변환 가능한지 검증한다.  
> 핵심 질문: “이 후보는 데이터 카드에 머무는가, 아니면 장면/에피소드/퀘스트로 발전 가능한가?”

---

## 0. 현재 전제

WITNESS는 현재 다음 단계까지 구현되어 있다.

```text
Simulation dump
→ Moment
→ MomentLink
→ StoryThread
→ NarrativeOpportunity
→ StoryCandidate
→ Cross-seed Story Pattern
→ Story Candidate Console
```

현재 강점:

- 압력 기반 세계 구동
- 여러 인물/집단에서 서사 후보 채굴
- named character 적용
- conflict-tuned premise 생성
- turning point 분류
- cross-seed robustness 확인
- provenance 유지

현재 한계:

- 완성된 이야기 본문은 아님
- 장면 묘사 없음
- 대사 없음
- 구체적 장소감 약함
- 극적 전환의 강도는 아직 검증 필요
- 창작자가 “쓸 수 있다”고 느끼는지 미검증

따라서 다음 단계는 **생성 고도화**가 아니라 **변환 가능성 검증**이다.

---

## 1. 검증 목표

### 1.1 검증할 것

각 `StoryCandidate`가 아래 산출물로 변환 가능한지 확인한다.

```text
StoryCandidate
→ Scene Brief
→ 1-page Treatment
→ Viability Score
→ Human Pick Result
```

### 1.2 검증하지 않을 것

이번 단계에서 하지 않는다.

```text
완성 소설 생성
시나리오 본문 생성
대사 생성
감정 과잉 문장 생성
시네마틱 컷신 생성
새 사건 임의 추가
```

이번 검증은 “이야기 자체를 쓰는 것”이 아니라,  
**이야기로 확장 가능한 구조가 있는지 확인하는 것**이다.

---

## 2. 핵심 판정 기준

StoryCandidate가 실제 이야기로 발전 가능하려면 최소 5개 조건을 만족해야 한다.

| 기준 | 설명 | 최소 통과 조건 |
|---|---|---|
| Character Clarity | 중심 인물이 분명한가 | named character 1명 이상 |
| Conflict Clarity | 원하는 것과 두려워하는 것이 충돌하는가 | conflict label + pressure evidence 존재 |
| Pressure Accumulation | 압력이 누적되는가 | 3개 이상 linked moment |
| Turning Point Strength | 변화의 전환점이 있는가 | categorized turning point 1개 이상 |
| Unresolved Hook | 다음 장면을 부르는 질문이 있는가 | unresolved question 또는 lingering tension 존재 |

추가 가산 기준:

| 기준 | 설명 |
|---|---|
| Relationship Context | 인물 간 관계 변화 또는 병렬 압력이 보이는가 |
| Cross-seed Robustness | 여러 seed에서 반복되는가 |
| Adaptation Range | film / novel / game 중 2개 이상으로 변환 가능한가 |
| Provenance Integrity | source_derived / source_inferred 구분이 유지되는가 |

---

## 3. 입력 데이터

### 3.1 필수 입력

```text
data/narrative/story_candidates.json
docs/portfolio/STORY_CANDIDATES.md
docs/portfolio/CROSS_SEED_STORY_PATTERNS.md
```

### 3.2 선택 입력

```text
data/narrative/story_threads.json
data/narrative/moments.json
data/narrative/moment_links.json
content/anchors/{anchor_id}/identity_map.json
```

### 3.3 입력 단위

검증 대상은 개별 `StoryCandidate`다.

예:

```json
{
  "candidate_id": "S01",
  "title": "Loyalty Strained by Survival Pressure",
  "main_character": "Peter",
  "core_conflict": "loyalty_vs_survival",
  "premise": "Peter tries to stay present as fear and public pressure slowly turn loyalty into silence.",
  "turning_points": [...],
  "relationship_dynamics": [...],
  "adaptation_hooks": [...],
  "evidence": {...},
  "risk_notes": [...]
}
```

---

## 4. 출력 산출물

이번 검증의 최종 산출물은 4개다.

```text
docs/portfolio/STORY_VIABILITY_REPORT.md
data/narrative/story_viability_scores.json
docs/portfolio/SCENE_BRIEFS.md
docs/portfolio/ONE_PAGE_TREATMENTS.md
```

선택 산출물:

```text
docs/portfolio/story_viability_console.html
```

---

## 5. Stage A — StoryCandidate 정규화

### 목적

각 StoryCandidate를 검증 가능한 구조로 정규화한다.

### 작업

1. `story_candidates.json` 로드
2. 후보별 필수 필드 확인
3. 누락 필드 기록
4. 검증용 내부 모델로 변환

### 내부 모델 예시

```python
@dataclass(frozen=True)
class ViabilityInput:
    candidate_id: str
    title: str
    main_character: str
    supporting_characters: tuple[str, ...]
    core_conflict: str
    premise: str
    arc_summary: str
    turning_points: tuple[TurningPoint, ...]
    relationship_dynamics: tuple[str, ...]
    adaptation_hooks: dict[str, str]
    evidence_counts: dict[str, int]
    cross_seed_frequency: int | None = None
    risk_notes: tuple[str, ...] = ()
```

### 통과 조건

- candidate_id 있음
- main_character 있음
- core_conflict 있음
- premise 있음
- turning_points 1개 이상
- evidence_counts 있음

### 실패 처리

필수 필드가 없으면 해당 candidate는 `invalid_input`으로 표시한다.

---

## 6. Stage B — Scene Brief 변환

### 목적

StoryCandidate가 장면 기획서로 바뀔 수 있는지 확인한다.

### Scene Brief 출력 포맷

```markdown
## Scene Brief — S01

### Core
- Main character:
- Supporting/context:
- Core conflict:
- Scene question:

### Situation
- External pressure:
- Internal pressure:
- Group/world context:

### Progression
1. Starting state:
2. Pressure enters:
3. Turning point:
4. Ending state:

### Creative Constraint
- Do not add:
- Must preserve:

### Evidence
- Source-derived:
- Source-inferred:
```

### 변환 규칙

#### 1. Scene Question 생성

`core_conflict` 기준 deterministic template 사용.

```python
SCENE_QUESTION_BY_CONFLICT = {
    "loyalty_vs_survival": "Will {main} stay loyal when survival pressure rises?",
    "uncertainty_vs_commitment": "Will {main} commit despite uncertainty?",
    "control_vs_exposure": "Will control hold as exposure risk increases?",
    "collective_fear_vs_scapegoating": "Who becomes the target when fear concentrates?",
    "identity_vs_failure": "Can {main} preserve identity under visible failure?",
}
```

#### 2. External Pressure

world / group pressure에서 추출.

예:

```text
authority_vigilance
public_suspicion
blame_concentration
group_tension
```

#### 3. Internal Pressure

agent pressure에서 추출.

예:

```text
fear
shame_self
hope
confusion
grief
```

#### 4. Progression

turning point 순서에 따라 구성.

```text
first moment → pressure enters → strongest turn → final unresolved state
```

### 통과 조건

Scene Brief는 아래 6개를 모두 채워야 한다.

```text
main character
scene question
internal pressure
external pressure
turning point
ending state
```

하나라도 비면 `scene_brief_incomplete`.

---

## 7. Stage C — 1-page Treatment 변환

### 목적

Scene Brief가 짧은 에피소드 구조로 확장 가능한지 확인한다.

### Treatment 출력 포맷

```markdown
## Treatment — S01

### Premise
...

### Act 1 — Setup
...

### Act 2 — Pressure Build
...

### Act 3 — Turn / Consequence
...

### End Hook
...

### Adaptation Notes
- Film:
- Novel:
- Game:
```

### 생성 원칙

허용:

```text
압력 변화의 순서화
장면 질문의 명확화
turning point를 act 구조에 배치
unresolved question을 hook으로 사용
```

금지:

```text
새 사건 추가
새 인물 추가
대사 추가
구체적 행동을 임의로 단정
성경/역사적 세부를 임의 보강
감정 과잉 산문
```

### Act 배치 규칙

```text
Act 1:
- 초기 상태
- 중심 인물의 위치
- 기본 압력

Act 2:
- 압력 누적
- 관계 또는 집단 맥락
- conflict intensification

Act 3:
- turning point
- 변화된 상태
- unresolved hook
```

### 통과 조건

Treatment는 아래 조건을 만족해야 한다.

| 항목 | 조건 |
|---|---|
| Premise | StoryCandidate premise를 보존 |
| Act 1 | starting state 포함 |
| Act 2 | pressure build 포함 |
| Act 3 | turning point 또는 consequence 포함 |
| End Hook | unresolved question 포함 |
| Evidence Discipline | 없는 사건을 추가하지 않음 |

---

## 8. Stage D — Viability Scoring

### 목적

각 후보가 실제 창작용 이야기로 발전 가능한지 점수화한다.

### 점수 모델

총점 100점.

```python
score = (
    20 * character_clarity
  + 20 * conflict_clarity
  + 15 * pressure_accumulation
  + 15 * turning_point_strength
  + 10 * relationship_context
  + 10 * unresolved_hook
  + 5  * cross_seed_robustness
  + 5  * adaptation_range
  - 10 * missing_context_penalty
  - 10 * over_inference_penalty
)
```

각 항목은 0.0~1.0으로 계산한다.

### 항목별 계산 기준

#### character_clarity

```text
1.0 = named main character 있음
0.5 = archetype fallback만 있음
0.0 = 익명 agent only
```

#### conflict_clarity

```text
1.0 = core_conflict + internal/external pressure 모두 있음
0.5 = conflict label만 있음
0.0 = unknown conflict
```

#### pressure_accumulation

```text
1.0 = linked moments 10개 이상
0.7 = linked moments 5~9개
0.4 = linked moments 3~4개
0.0 = linked moments 2개 이하
```

#### turning_point_strength

```text
1.0 = sustained pressure + co-occurring pressure + world/group shift 중 2개 이상
0.6 = categorized turning point 1개
0.0 = turning point 없음
```

#### relationship_context

```text
1.0 = named relationship dynamics 있음
0.6 = group context 있음
0.0 = 관계/집단 맥락 없음
```

#### unresolved_hook

```text
1.0 = explicit unresolved question 있음
0.5 = lingering tension 있음
0.0 = 없음
```

#### cross_seed_robustness

```text
1.0 = 5/5 seeds
0.8 = 4/5 seeds
0.6 = 3/5 seeds
0.0 = 2/5 이하 또는 데이터 없음
```

#### adaptation_range

```text
1.0 = film + novel + game 모두 있음
0.7 = 2개 있음
0.3 = 1개 있음
0.0 = 없음
```

#### missing_context_penalty

```text
1.0 = 장면 위치/관계/행동 모두 불명확
0.5 = 일부만 불명확
0.0 = 충분히 명확
```

#### over_inference_penalty

```text
1.0 = 근거 없는 사건/감정/행동을 추가함
0.5 = 표현이 다소 강함
0.0 = evidence 범위 내 표현
```

### 등급

| 점수 | 등급 | 의미 |
|---:|---|---|
| 80~100 | strong_viable | 장면/에피소드로 바로 개발 가능 |
| 65~79 | viable_with_gaps | 가능하지만 맥락 보강 필요 |
| 50~64 | weak_seed | 아이디어 씨앗 수준 |
| 0~49 | not_viable | 이야기 후보로 부적합 |

---

## 9. Stage E — Human Pick Test

### 목적

시스템 점수와 실제 창작자 직관이 맞는지 확인한다.

### 대상

최소 3명.

가능한 리뷰어:

```text
소설/에세이 쓰는 사람
영상/영화 관심자
게임 기획 관심자
일반 독자
```

### 테스트 자료

각 후보마다 다음 3개만 보여준다.

```text
StoryCandidate card
Scene Brief
1-page Treatment
```

원본 telemetry 전체는 숨긴다.  
단, 요청하면 Evidence section을 열람 가능하게 한다.

### 질문

각 리뷰어에게 아래 질문을 묻는다.

```text
1. 이 후보로 장면/에피소드/퀘스트를 만들 수 있다고 느끼는가? (1~5)
2. 가장 쓰고 싶은 후보는 무엇인가?
3. 왜 그 후보를 골랐는가?
4. 부족한 정보는 무엇인가?
5. 데이터처럼 느껴지는 문장은 어디인가?
6. 억지로 이야기화한 느낌이 드는 부분은 어디인가?
7. 이 후보가 적합한 매체는 무엇인가? film / novel / game / none
```

### Human Pick Score

```python
human_pick_score = average(question_1_score) / 5
selection_rate = selected_count / reviewer_count
```

### 통과 기준

후보 하나가 아래 조건을 만족하면 실제 이야기 가능성 있음.

```text
human_pick_score >= 0.70
selection_rate >= 0.33
major over-inference complaint 없음
```

---

## 10. Stage F — Evidence Discipline Audit

### 목적

Scene Brief와 Treatment가 원본 데이터 범위를 넘지 않았는지 검사한다.

### 금지 위반

아래가 있으면 `audit_fail`.

```text
없는 사건 추가
없는 인물 추가
없는 관계 단정
대사 생성
장소/시간을 근거 없이 구체화
감정 상태를 수치 이상으로 과장
역사/성경 맥락을 근거 없이 삽입
```

### 허용 변환

아래는 허용.

```text
fear rises → fear pressure increases
authority_vigilance rises → authority pressure closes in
unresolved_thread → unresolved tension remains
group_tension_shift → group context becomes unstable
```

### Audit 출력

```json
{
  "candidate_id": "S01",
  "scene_brief_audit": "pass",
  "treatment_audit": "pass",
  "violations": [],
  "risky_phrases": [
    {
      "phrase": "emotionally withdraws",
      "risk": "medium",
      "reason": "derived from fear/shame pattern, not direct action"
    }
  ]
}
```

---

## 11. 최종 Report 구조

`STORY_VIABILITY_REPORT.md`는 아래 구조로 작성한다.

```markdown
# WITNESS Story Viability Report

## 1. Summary

| Candidate | Score | Grade | Human Pick | Audit |
|---|---:|---|---:|---|

## 2. Strongest Candidate

## 3. Candidate-by-Candidate Review

### S01 — ...
- Viability score:
- Grade:
- What works:
- What is missing:
- Risk:
- Recommended use:

## 4. Human Pick Test Result

## 5. Evidence Audit Result

## 6. Decision

### Ship / Improve / Drop

## 7. Next Implementation Recommendation
```

---

## 12. Implementation Files

### New module files

```text
engine/observer/story_viability.py
engine/observer/scene_brief.py
engine/observer/treatment.py
engine/observer/story_audit.py
```

### New scripts

```text
scripts/narrative/build_scene_briefs.py
scripts/narrative/build_treatments.py
scripts/narrative/score_story_viability.py
scripts/narrative/audit_story_viability.py
scripts/narrative/build_story_viability_report.py
```

### New tests

```text
tests/test_narrative/test_scene_brief.py
tests/test_narrative/test_treatment.py
tests/test_narrative/test_story_viability.py
tests/test_narrative/test_story_audit.py
tests/test_narrative/test_story_viability_report.py
```

---

## 13. Acceptance Criteria

이번 검증 phase는 아래 조건을 만족하면 완료한다.

### Functional

```text
[ ] StoryCandidate JSON을 읽는다.
[ ] Scene Brief를 생성한다.
[ ] 1-page Treatment를 생성한다.
[ ] Viability Score를 계산한다.
[ ] Evidence Audit을 수행한다.
[ ] Markdown report를 생성한다.
```

### Quality

```text
[ ] 없는 사건을 추가하지 않는다.
[ ] 대사를 생성하지 않는다.
[ ] 소설 본문처럼 쓰지 않는다.
[ ] source_derived / source_inferred 구분을 유지한다.
[ ] weak candidate도 억지로 strong으로 올리지 않는다.
[ ] risk notes가 비어 있으면 안 된다.
```

### Portfolio

```text
[ ] 최소 1개 후보가 strong_viable 또는 viable_with_gaps 등급을 받는다.
[ ] 가장 강한 후보의 Scene Brief가 사람이 읽고 이해 가능하다.
[ ] 가장 강한 후보의 Treatment가 장면/에피소드로 확장 가능하다.
[ ] Human Pick Test에서 최소 1개 후보가 선택된다.
```

---

## 14. Recommended Workflow

### Step 1

```bash
python scripts/narrative/build_scene_briefs.py \
  --input data/narrative/story_candidates.json \
  --output docs/portfolio/SCENE_BRIEFS.md
```

### Step 2

```bash
python scripts/narrative/build_treatments.py \
  --input data/narrative/story_candidates.json \
  --scene-briefs docs/portfolio/SCENE_BRIEFS.md \
  --output docs/portfolio/ONE_PAGE_TREATMENTS.md
```

### Step 3

```bash
python scripts/narrative/score_story_viability.py \
  --input data/narrative/story_candidates.json \
  --output data/narrative/story_viability_scores.json
```

### Step 4

```bash
python scripts/narrative/audit_story_viability.py \
  --scene-briefs docs/portfolio/SCENE_BRIEFS.md \
  --treatments docs/portfolio/ONE_PAGE_TREATMENTS.md \
  --output data/narrative/story_viability_audit.json
```

### Step 5

```bash
python scripts/narrative/build_story_viability_report.py \
  --scores data/narrative/story_viability_scores.json \
  --audit data/narrative/story_viability_audit.json \
  --output docs/portfolio/STORY_VIABILITY_REPORT.md
```

---

## 15. Decision Rules

### Ship

아래 조건이면 현재 방향을 포트폴리오에 사용한다.

```text
최소 1개 strong_viable
또는
2개 이상 viable_with_gaps
그리고 audit_fail 0개
```

### Improve

아래 조건이면 StoryCandidate enrichment를 보강한다.

```text
대부분 weak_seed
또는
Human Pick Test에서 아무도 선택하지 않음
또는
missing_context_penalty가 반복적으로 높음
```

### Drop / Reframe

아래 조건이면 “이야기 후보” claim을 낮춘다.

```text
모든 후보 not_viable
또는
Scene Brief 변환이 반복적으로 실패
또는
Treatment 생성 시 over-inference가 필수적으로 발생
```

이 경우 포지셔닝을 다음으로 낮춘다.

```text
Narrative Mining Engine
→ Simulation Pattern Mining Tool
```

---

## 16. Important Guardrails

이 phase에서 가장 중요한 것은 **이야기처럼 보이게 만드는 것**이 아니다.  
중요한 것은 **원본 시뮬레이션 데이터로부터 이야기화가 가능한 최소 구조가 실제로 존재하는지 검증하는 것**이다.

따라서:

```text
멋진 문장보다 정확한 변환
강한 주장보다 약점 표시
창작보다 검증
완성본보다 가능성 판정
```

을 우선한다.

---

## 17. Final Success Definition

이번 검증의 성공 정의:

> WITNESS가 생성한 StoryCandidate 중 최소 하나가, 원본 데이터를 벗어나지 않고도 Scene Brief와 1-page Treatment로 변환 가능하며, 사람이 실제 창작 후보로 선택할 수 있음을 확인한다.

실패 정의:

> StoryCandidate가 수치와 라벨의 묶음에 머물고, 장면 질문·전환점·미해결 훅으로 변환되지 못한다.

---

*End of plan.*
