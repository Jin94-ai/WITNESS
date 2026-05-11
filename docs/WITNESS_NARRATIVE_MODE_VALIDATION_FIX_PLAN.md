# WITNESS Narrative Mode Refactor — Validation Fix Plan

> 목적: 2026-05-09 검증 보고서의 결함을 바탕으로, Phase 3 ML/Flesh Engine 진입 전에 **SkeletonOutput의 의미 보존성, taxonomy 일관성, annotation 가능성, contract drift guard**를 보강한다.

---

## 0. 핵심 결론

현재 WITNESS Narrative Mode Refactor는 구조적으로는 잘 진행되었다.

```text
Skeleton Engine
→ UniversalStorySeed
→ SkeletonOutput v1
→ Anchor Binding
→ Annotation Infra
→ Future Flesh Engine
```

하지만 검증 보고서에서 확인된 핵심 문제는 다음이다.

> 인프라는 작동하지만, adapter 단계에서 의미 정보가 누수되고 있다.

즉, 현재 문제는 “코드가 안 돈다”가 아니다. 문제는 **코드는 통과하지만 UniversalStorySeed가 충분히 의미 있는 narrative skeleton을 보존하지 못한다는 것**이다.

이번 수정의 목표는 기능 추가가 아니라:

```text
형식적 통과
→ 의미적 통과
```

로 올리는 것이다.

---

## 1. 현재 상태 요약

검증 보고서 기준 현재 상태:

```text
Fast suite: 2,304 passed, 14 skipped
Skeleton tests: 100 신규
Phase 0: Contract & Skeleton Cleanup 완료
Phase 1: Data Infra 완료
Phase 2: Multi-AI Annotation Prep 완료
Phase 3-5: ML 학습 미진입
Phase 6: Portfolio integration partial
```

주요 성공:

```text
- SkeletonOutput v1 FROZEN contract
- Universal pressure / desire / conflict taxonomy
- Anchor binding 외부화
- LLM annotation prompt template
- hallucination quote validator
- inter-annotator Pearson r 도구
- RFC governance
```

주요 결함:

```text
- Adapter가 main_archetype을 잃음
- dominant_pressures가 다수 seed에서 비어 있음
- supporting_roles가 placeholder로만 남음
- main_role / main_archetype 책임이 불명확함
- 일부 annotation feature가 회차 단위로 측정 불가능함
- taxonomy 자기 일관성 구멍
- drift guard가 필드 이름만 검사함
```

---

## 2. 이번 수정의 범위

### 2.1 한다

```text
1. Annotation feature 정의 수정
2. Taxonomy 명세 보강
3. UniversalStorySeed contract 책임 명확화
4. Adapter lossless 보강
5. SkeletonOutput 재생성
6. Drift guard 강화
7. Validation report 갱신
8. Tests 추가/수정
```

### 2.2 하지 않는다

```text
- Phase 3 ML 학습 시작
- 실제 LLM API 호출
- 실제 방송 대본/줄거리 fetch
- 새 anchor 추가
- engine simulation core 수정
- visual track 수정
- 외부 asset 도입
- 긴 소설/대사/장면 본문 생성
```

---

## 3. 최우선 원칙

### 3.1 Lossless Adapter 원칙

Universal 변환 후에도 다음 정보가 사라지면 안 된다.

```text
- seed_id
- conflict_axis_id
- main_archetype
- main_role
- dominant_pressures
- dominant_desires
- supporting_roles
- evidence_count
- audit_status
- source anchor metadata
```

### 3.2 Empty Field 정책

다음 필드는 빈 값이면 실패로 본다.

```text
UniversalStorySeed.main_archetype
UniversalStorySeed.main_role
UniversalStorySeed.dominant_desires
UniversalStorySeed.conflict_axis_id
```

다음 필드는 빈 값이 가능하지만 반드시 이유를 audit에 기록해야 한다.

```text
dominant_pressures
supporting_roles
```

### 3.3 Placeholder 금지

아래 값은 최종 SkeletonOutput에서 금지한다.

```text
main
supporting_1
supporting_2
unknown
""
```

단, `unknown`은 validator의 명시적 fallback mode에서만 허용하고 audit에 기록한다.

---

# Phase A — Annotation Feature Definition Fix

## A.1 문제

검증 보고서에서 두 annotation feature가 회차 단위 측정에 부적합하다고 판단되었다.

```text
P1-A: conflict_amplification_rate 정의 모호
P1-B: resolution_to_dangling_ratio 회차 단위 측정 불가능
```

## A.2 수정 방향

### 기존 `conflict_amplification_rate`

문제:

```text
회차 시작 대비 끝의 갈등 강도 비율
```

이는 줄거리 텍스트만 보고 “시작 강도”를 추정해야 해서 annotation variance가 커진다.

### 수정 후

```text
conflict_intensity_peak
```

정의:

```text
해당 회차 줄거리 안에서 관측되는 갈등 누적/폭발의 최대 강도.
```

Scale:

```text
0 = 갈등 거의 없음
1 = 약한 긴장 또는 암시
2 = 명확한 갈등 존재
3 = 갈등이 여러 인물/관계로 확산
4 = 공개 충돌, 폭로, 관계 파탄 직전
5 = 회차의 중심이 강한 충돌/폭로/파국으로 구성됨
```

### 기존 `resolution_to_dangling_ratio`

문제:

```text
던진 떡밥이 언제 회수되는지 단일 회차만 보고 측정 불가능.
```

### 수정 후

권장 feature:

```text
dangling_thread_generation
```

정의:

```text
해당 회차에서 새롭게 남겨진 미해결 질문, 의심, 비밀, 오해, 다음 회차로 넘어가는 갈등의 수와 강도.
```

Scale:

```text
0 = 미해결 질문 없음
1 = 약한 암시 1개
2 = 분명한 미해결 질문 1개
3 = 미해결 갈등 2개 이상
4 = 주요 관계/비밀이 다음 회차로 강하게 넘어감
5 = 회차 말미가 거의 클리프행어 중심
```

보조 feature로 필요하면 별도:

```text
resolved_prior_thread_count
```

MVP에서는 `dangling_thread_generation`만 사용한다.

## A.3 수정 대상

```text
docs/annotation/ANNOTATION_GUIDE.md
scripts/annotation/prompt_templates.py
tests/test_skeleton/test_phase2_prep.py
tests/test_skeleton/test_inter_annotator_correlation.py
```

## A.4 Acceptance

```text
[ ] conflict_amplification_rate 명칭 제거 또는 deprecated 표시
[ ] conflict_intensity_peak 정의 추가
[ ] resolution_to_dangling_ratio 명칭 제거 또는 deprecated 표시
[ ] dangling_thread_generation 정의 추가
[ ] prompt template의 7 features가 새 정의와 일치
[ ] 테스트에서 두 feature의 회차 단위 측정 가능성을 검증
```

---

# Phase B — Taxonomy Consistency Fix

## B.1 `natural_collisions` 의미 분리

### 문제

`desire_taxonomy.json`의 `natural_collisions`에는 desire와 pressure가 섞여 있다.

예:

```json
"survival": {
  "natural_collisions": ["loyalty", "love", "shame_self"]
}
```

여기서 `loyalty`, `love`는 desire이고 `shame_self`는 pressure다.

### 수정

`natural_collisions`를 폐기하거나 deprecated하고 다음으로 분리한다.

```json
"survival": {
  "colliding_desires": ["loyalty", "love"],
  "colliding_pressures": ["shame_self"]
}
```

### Acceptance

```text
[ ] 모든 desire entry가 colliding_desires / colliding_pressures를 가진다.
[ ] 모든 colliding_desires id는 desire_taxonomy에 존재한다.
[ ] 모든 colliding_pressures id는 pressure_taxonomy에 존재한다.
[ ] 기존 natural_collisions는 제거하거나 deprecated로 명시한다.
```

---

## B.2 `unknown` conflict axis 의도 결정

### 문제

`unknown`이 fallback인지 정상 axis인지 불분명하다.

### 결정

이번 계획에서는 `unknown`을 **fallback only**로 정의한다.

정책:

```text
- 정상 SkeletonOutput에서는 unknown 금지
- 어쩔 수 없이 unknown이 나오는 경우 audit_trail에 unknown_axis_count 기록
- Phase 3 학습 데이터에는 unknown seed를 기본 제외
```

### 수정

`conflict_axes.json`의 unknown entry에 명시한다.

```json
"unknown": {
  "id": "unknown",
  "status": "fallback_only",
  "valid_for_training": false
}
```

Validator:

```text
- strict mode: unknown이면 fail
- lenient mode: unknown 허용하되 audit 기록
```

### Acceptance

```text
[ ] unknown axis가 fallback_only로 명시된다.
[ ] strict validator에서 unknown seed는 실패한다.
[ ] lenient validator에서 unknown은 audit_trail에 기록된다.
[ ] SkeletonOutput 기본 생성은 strict mode를 사용한다.
```

---

## B.3 `crowd_mood` 재분류

### 문제

`crowd_mood`는 pressure라기보다 environmental state에 가깝다.

### 결정

MVP에서는 breaking change를 줄이기 위해 다음 방식으로 처리한다.

```text
crowd_mood 유지
단, pressure가 아니라 environmental_pressure_state로 명시
polarity: neutral 유지 가능
```

추가로 실제 압력으로 쓰고 싶을 때는:

```text
crowd_tension
```

을 새 pressure로 추가한다.

```json
"crowd_tension": {
  "id": "crowd_tension",
  "plain_label_ko": "군중의 긴장",
  "polarity": "aversive",
  "axis_hint": "external_social"
}
```

### Acceptance

```text
[ ] crowd_mood는 environmental_state임이 명시된다.
[ ] crowd_tension을 aversive pressure로 추가한다.
[ ] adapter가 crowd_mood만 있을 때는 pressure로 오인하지 않는다.
[ ] tension이 명확할 때 crowd_tension으로 매핑 가능하다.
```

---

# Phase C — UniversalStorySeed Contract RFC

## C.1 문제

`main_role`과 `main_archetype`의 책임이 불명확하다.

## C.2 권장 결정

RFC를 작성하고 다음 의미로 고정한다.

```text
main_archetype:
- 인물이 어떤 유형인가
- 예: loyal_under_pressure, uncertain_actor, watcher, late_responder

main_role:
- 이 seed/flow 안에서 어떤 서사 기능을 하는가
- 예: protagonist, witness, delayed_actor, pressure_source, supporting_actor

flow_role:
- LifeStoryFlow 안에서 어떤 위치인가
- 예: main_arc, supporting_arc, contrast_arc, echo_arc
```

## C.3 UniversalStorySeed v1.1 제안

```python
@dataclass(frozen=True)
class UniversalStorySeed:
    seed_id: str
    conflict_axis_id: str

    main_archetype: str
    main_role: str

    dominant_pressures: tuple[str, ...]
    dominant_desires: tuple[str, ...]

    supporting_archetypes: tuple[str, ...] = ()
    supporting_roles: tuple[str, ...] = ()

    change_pattern: str = ""
    arc_direction: str = ""
    relationship_function: str = ""
    flow_role: str = ""

    turning_points_count: int = 0

    confidence_label: str = ""
    audit_status: str = "pass"
    evidence_count: int = 0
    notes: tuple[str, ...] = ()
```

## C.4 `pressure_pattern` 처리

현재 `pressure_pattern`은 중복 정보가 많다.

수정:

```text
pressure_pattern.primary_pressure 제거
pressure_pattern.primary_desire 제거
turning_points_count를 top-level로 승격
change_pattern / arc_direction / relationship_function 추가
```

## C.5 RFC 산출물

```text
docs/plans/RFC_UNIVERSAL_STORY_SEED_V1_1.md
```

필수 포함:

```text
- 변경 동기
- 기존 contract 문제
- 대안 2개 이상
- 선택안
- 마이그레이션 계획
- flesh engine 영향
- 테스트 계획
```

## C.6 Acceptance

```text
[ ] RFC 문서 작성
[ ] UniversalStorySeed v1.1 구현
[ ] 기존 v1 산출물 migration 또는 adapter fallback 구현
[ ] drift guard expected fields 갱신
[ ] tests 통과
```

---

# Phase D — Adapter Lossless Fix

## D.1 핵심 문제

현재 adapter는 다음 의미 정보를 잃는다.

```text
main_archetype
main_role
dominant_pressures
supporting_roles
```

## D.2 수정 정책

### D.2.1 archetype map 필수화

현재:

```python
archetype_by_seed: dict[str, str] | None = None
```

수정:

```python
archetype_by_seed: dict[str, str]
supporting_archetypes_by_seed: dict[str, tuple[str, ...]]
```

기본 빈 dict 금지.

```python
if not archetype_by_seed:
    raise ValueError("archetype_by_seed is required for lossless conversion")
```

## D.2.2 기본 archetype map

Peter baseline MVP:

```python
ARCHETYPE_BY_SEED = {
    "S01": "loyal_under_pressure",
    "S02": "uncertain_actor",
    "S03": "watcher",
    "S04": "late_responder",
}
```

지원 역할:

```python
MAIN_ROLE_BY_ARCHETYPE = {
    "loyal_under_pressure": "protagonist",
    "uncertain_actor": "supporting_actor",
    "watcher": "witness",
    "late_responder": "delayed_actor",
}
```

flow role:

```python
FLOW_ROLE_BY_SEED = {
    "S01": "main_arc",
    "S02": "supporting_uncertainty",
    "S03": "witness_arc",
    "S04": "delayed_response_arc",
}
```

## D.2.3 supporting role map

기존 `supporting_1` 금지.

예:

```python
SUPPORTING_ARCHETYPES_BY_SEED = {
    "S01": ("uncertain_actor", "watcher"),
    "S02": ("watcher",),
    "S03": ("loyal_under_pressure",),
    "S04": ("uncertain_actor",),
}
```

결과:

```json
"supporting_archetypes": ["uncertain_actor", "watcher"],
"supporting_roles": ["supporting_actor", "witness"]
```

## D.3 Pressure fallback 강화

### 문제

S02~S04의 dominant_pressures가 비어 있다.

### 수정

1차: candidate phrase mapping 시도  
2차: conflict_axis pole에서 pressure fallback  
3차: archetype default vulnerabilities fallback  
4차: 그래도 없으면 audit 기록

예:

```python
def infer_pressures(candidate, conflict_axis_id, archetype):
    pressures = map_phrases(candidate.world_pressure_context)
    if pressures:
        return pressures

    pressures = pressure_poles_from_conflict_axis(conflict_axis_id)
    if pressures:
        return pressures

    pressures = default_pressures_for_archetype(archetype)
    if pressures:
        return pressures

    audit_missing_pressure(seed_id)
    return ()
```

`uncertainty_vs_commitment`의 pole_a는 `confusion` pressure이므로 S02~S04는 최소 `confusion`을 가져야 한다.

## D.4 Phrase mapping 실패를 silent failure로 두지 않기

현재 `_phrases_to_pressure_ids`는 실패 phrase를 그냥 버린다.

수정:

```python
mapped, unmapped = map_pressure_phrases(...)
if unmapped:
    audit_trail.unmapped_pressure_phrases += unmapped
```

## D.5 Acceptance

```text
[ ] skeleton_output.json의 모든 seed에 main_archetype 존재
[ ] 모든 seed의 main_role이 "main"이 아님
[ ] S02-S04 dominant_pressures가 비어 있지 않음
[ ] supporting_roles에 supporting_1/supporting_2 없음
[ ] unmapped pressure phrase는 audit에 기록됨
[ ] adapter lossless test 추가
```

---

# Phase E — SkeletonOutput Flow 채우기

## E.1 문제

현재 `flow: null`.

이는 “여러 seed가 하나의 흐름으로 연결된다”는 목표와 맞지 않는다.

## E.2 MVP Flow

SkeletonOutput에 최소 flow를 채운다.

```json
"flow": {
  "schema_version": "life_story_flow_v1",
  "ordering": "evidence_derived",
  "ordered_seed_ids": ["S01", "S03", "S02", "S04"],
  "flow_roles": {
    "S01": "main_arc",
    "S03": "witness_arc",
    "S02": "supporting_uncertainty",
    "S04": "delayed_response_arc"
  }
}
```

## E.3 정렬 기준

MVP에서는 다음 우선순위로 정렬한다.

```text
1. main_arc 먼저
2. witness_arc
3. supporting_uncertainty
4. delayed_response_arc
5. 나머지는 evidence_count 내림차순
```

## E.4 Acceptance

```text
[ ] SkeletonOutput.flow가 null이 아님
[ ] ordered_seed_ids가 seeds와 일치
[ ] flow_roles가 모든 seed_id를 포함
[ ] flow ordering이 deterministic
[ ] renderer에서 flow summary를 출력 가능
```

---

# Phase F — Contract Drift Guard 강화

## F.1 문제

현재 drift guard는 필드 이름만 검사한다.

## F.2 강화 항목

다음까지 검사한다.

```text
- field name
- type annotation
- default value
- default_factory 여부
- frozen dataclass 여부
- tuple/list mutability
- schema_version 값
```

## F.3 테스트 예시

```python
def test_universal_story_seed_contract_types_frozen():
    hints = get_type_hints(UniversalStorySeed)
    assert hints["dominant_pressures"] == tuple[str, ...]
    assert hints["dominant_desires"] == tuple[str, ...]
    assert hints["supporting_roles"] == tuple[str, ...]
```

```python
def test_skeleton_output_dataclass_is_frozen():
    assert SkeletonOutput.__dataclass_params__.frozen is True
```

## F.4 Acceptance

```text
[ ] field name drift 감지
[ ] type drift 감지
[ ] list/tuple mutability drift 감지
[ ] schema_version drift 감지
[ ] frozen 해제 감지
```

---

# Phase G — Validation Report Regeneration

## G.1 목표

수정 전/후 차이를 검증 보고서로 남긴다.

## 산출물

```text
docs/plans/VALIDATION_REPORT_2026_05_09_FIXES.md
```

## 포함 내용

```text
1. 기존 결함 P1-A~P3-A 대응표
2. 수정 여부
3. 남은 위험
4. 재생성 skeleton_output.json diff
5. fast suite 결과
6. Phase 3 진입 가능 여부
```

## Acceptance

```text
[ ] 8개 필수 수정 상태가 명시됨
[ ] 5개 권고 수정 상태가 명시됨
[ ] Phase 3 go/no-go 판정 포함
```

---

## 4. 수정 후 기대되는 SkeletonOutput 예시

```json
{
  "schema_version": "skeleton_output_v1_1",
  "seeds": [
    {
      "seed_id": "S01",
      "conflict_axis_id": "loyalty_vs_survival",
      "main_archetype": "loyal_under_pressure",
      "main_role": "protagonist",
      "dominant_pressures": ["authority_vigilance", "public_suspicion", "fear"],
      "dominant_desires": ["loyalty", "survival"],
      "supporting_archetypes": ["uncertain_actor", "watcher"],
      "supporting_roles": ["supporting_actor", "witness"],
      "change_pattern": "stay_present_then_withdraw",
      "arc_direction": "visibility_to_silence",
      "relationship_function": "group_presence_without_action",
      "flow_role": "main_arc",
      "turning_points_count": 3,
      "confidence_label": "바로 발전 가능한 씨앗",
      "audit_status": "통과",
      "evidence_count": 21
    },
    {
      "seed_id": "S02",
      "conflict_axis_id": "uncertainty_vs_commitment",
      "main_archetype": "uncertain_actor",
      "main_role": "supporting_actor",
      "dominant_pressures": ["confusion", "fear"],
      "dominant_desires": ["commitment"],
      "supporting_archetypes": ["watcher"],
      "supporting_roles": ["witness"],
      "change_pattern": "delay_under_pressure",
      "arc_direction": "uncertainty_to_withdrawal",
      "relationship_function": "contrast_to_main_arc",
      "flow_role": "supporting_uncertainty",
      "turning_points_count": 2,
      "confidence_label": "보완이 필요한 씨앗",
      "audit_status": "통과",
      "evidence_count": 9
    }
  ],
  "flow": {
    "schema_version": "life_story_flow_v1_1",
    "ordering": "evidence_derived",
    "ordered_seed_ids": ["S01", "S03", "S02", "S04"],
    "flow_roles": {
      "S01": "main_arc",
      "S03": "witness_arc",
      "S02": "supporting_uncertainty",
      "S04": "delayed_response_arc"
    }
  }
}
```

---

## 5. 수정 순서

```text
Step 1 — Feature definition patch
Step 2 — Taxonomy patch
Step 3 — RFC 작성
Step 4 — Contract 구현
Step 5 — Adapter lossless 수정
Step 6 — SkeletonOutput 재생성
Step 7 — Drift guard 강화
Step 8 — Validation report 갱신
```

---

## 6. 최종 Acceptance Criteria

이번 Phase 2.5 Fix가 끝나면 다음을 만족해야 한다.

```text
[ ] ANNOTATION_GUIDE의 7 features가 회차 단위로 측정 가능하다.
[ ] desire taxonomy의 collision schema가 명확하다.
[ ] unknown axis의 역할이 fallback only로 명시된다.
[ ] crowd_mood / crowd_tension 구분이 명확하다.
[ ] UniversalStorySeed v1.1 RFC가 존재한다.
[ ] main_archetype / main_role 책임이 명확하다.
[ ] skeleton_output.json 모든 seed에 main_archetype이 존재한다.
[ ] skeleton_output.json 모든 seed의 main_role이 의미 있는 role이다.
[ ] dominant_pressures가 비어 있는 seed가 없거나 audit에 명시된다.
[ ] supporting_roles가 placeholder가 아니다.
[ ] flow가 null이 아니다.
[ ] drift guard가 type / mutability / frozen 변경을 잡는다.
[ ] fast suite 통과.
[ ] validation fix report가 생성된다.
```

---

## 7. Phase 3 Go / No-Go 기준

### Go

아래 조건을 모두 만족하면 Phase 3 ML/Flesh Engine으로 진입한다.

```text
- Adapter lossless tests 통과
- SkeletonOutput v1.1 생성 성공
- unknown axis 0건 또는 audit 명시
- dominant_pressures empty 0건 또는 audit 명시
- supporting placeholder 0건
- feature definition reliability risk 해소
- fast suite 회귀 0
```

### No-Go

아래 중 하나라도 있으면 Phase 3 진입 금지.

```text
- main_archetype 빈 seed 존재
- main_role == "main" seed 존재
- supporting_1/supporting_2 존재
- dominant_pressures silent empty 존재
- unknown axis가 정상 seed로 통과
- drift guard가 타입 변경을 못 잡음
```

---

## 8. 다음 에이전트 Directive

```text
WITNESS Narrative Mode — Phase 2.5 Validation Fix directive

검증 보고서 기반으로 Phase 3 진입 전 필수 결함을 수정한다.

목표:
SkeletonOutput이 형식적으로만 통과하는 것이 아니라, 의미 정보를 보존하는 narrative skeleton이 되도록 만든다.

제약:
- engine simulation core 수정 금지
- visual track 수정 금지
- 외부 의존 0
- LLM API 호출 금지
- 실제 데이터 fetch 금지
- SkeletonOutput / UniversalStorySeed contract 변경 시 RFC 작성 필수
- 기존 fast suite 회귀 0

수정:
1. Annotation feature 두 개를 회차 단위로 측정 가능하게 수정한다.
2. desire taxonomy collision schema를 분리한다.
3. unknown axis를 fallback only로 정의하고 validator 동작을 명확히 한다.
4. crowd_mood와 crowd_tension을 분리한다.
5. UniversalStorySeed v1.1 RFC를 작성한다.
6. main_archetype / main_role 책임을 분리한다.
7. adapter가 archetype / role / pressure / supporting role을 lossless하게 보존하도록 수정한다.
8. pressure fallback과 unmapped phrase audit을 추가한다.
9. SkeletonOutput.flow를 null이 아니게 채운다.
10. drift guard를 field name뿐 아니라 type/default/frozen까지 검사하도록 강화한다.
11. skeleton_output.json을 재생성하고 before/after validation report를 작성한다.

Acceptance:
- 모든 seed에 main_archetype 존재
- main_role == "main" 없음
- supporting_1/supporting_2 없음
- dominant_pressures silent empty 없음
- flow != null
- unknown axis는 fallback only로 audit됨
- fast suite 통과
- validation fix report 생성
```

---

## 9. 한 줄 결론

지금 필요한 것은 새 기능이 아니다.

> **SkeletonOutput이 ML/Flesh Engine에 넘겨도 될 만큼 의미 정보를 보존하는지 보장하는 것.**

이 수정이 끝나야 장르 어댑터나 ML 학습으로 넘어갈 수 있다.

---

*End of plan.*
