# RFC-0001 — UniversalStorySeed v1.1

```
RFC ID:        RFC-0001
Title:         UniversalStorySeed v1 → v1.1 (semantic-preservation upgrade)
Author:        WITNESS team
Status:        approved
Created:       2026-05-09
Affected:      UniversalStorySeed, SkeletonOutput consumers, universal_seed_adapter
```

---

## 1. 동기 (Why)

`docs/WITNESS_NARRATIVE_MODE_VALIDATION_FIX_PLAN.md` §C 매핑.

검증 보고서에서 다음 결함이 확인됨:

```
- main_role과 main_archetype의 책임 경계가 불분명
- supporting_roles에 placeholder ("supporting_1") 누수
- pressure_pattern 안의 primary_pressure / primary_desire가 dominant_pressures /
  dominant_desires와 중복
- flow_role / change_pattern / arc_direction이 contract 외부에 머물러
  flesh engine에서 참조 불가
- turning_points_count가 pressure_pattern 안에 묻혀 있음
```

이는 SkeletonOutput consumer (flesh engine, renderer)가 *서사적 결정*을
내릴 때 필요한 정보가 contract에 없다는 뜻. Phase 3 ML 진입 전에
contract를 *의미 보존*까지 끌어올려야 한다.

내부 refactor가 아니라 *외부 요구사항 (의미 보존성)*을 충족하기 위한 변경.

## 2. 제안 (What)

### 2.1 변경 범위

```python
# Before (v1)
@dataclass(frozen=True)
class UniversalStorySeed:
    seed_id: str
    conflict_axis_id: str
    main_role: str                           # 책임 모호: archetype과 혼용
    main_archetype: str = ""
    dominant_pressures: tuple[str, ...] = ()
    dominant_desires: tuple[str, ...] = ()
    supporting_roles: tuple[str, ...] = ()   # placeholder 누수
    pressure_pattern: dict[str, Any] = ...   # primary_* / change_pattern
                                              # / turning_points_count 혼재
    confidence_label: str = ""
    audit_status: str = "pass"
    evidence_count: int = 0
    notes: tuple[str, ...] = ()

# After (v1.1)
@dataclass(frozen=True)
class UniversalStorySeed:
    seed_id: str
    conflict_axis_id: str

    main_archetype: str                       # 인물 유형 (loyal_under_pressure 등)
    main_role: str                            # 서사 기능 (protagonist / witness 등)

    dominant_pressures: tuple[str, ...] = ()
    dominant_desires: tuple[str, ...] = ()

    supporting_archetypes: tuple[str, ...] = ()   # 신규
    supporting_roles: tuple[str, ...] = ()

    change_pattern: str = ""                  # 신규: pressure_pattern.change_pattern 승격
    arc_direction: str = ""                   # 신규: visibility_to_silence 등
    relationship_function: str = ""           # 신규: contrast_to_main 등
    flow_role: str = ""                       # 신규: main_arc / witness_arc 등

    turning_points_count: int = 0             # 신규: pressure_pattern에서 승격

    pressure_pattern: dict[str, Any] = ...    # 호환용으로 유지 (deprecated)

    confidence_label: str = ""
    audit_status: str = "pass"
    evidence_count: int = 0
    notes: tuple[str, ...] = ()
```

### 2.2 책임 분리

```
main_archetype:
  인물이 어떤 *유형*인가
  e.g. loyal_under_pressure, uncertain_actor, watcher, late_responder

main_role:
  이 seed/flow 안에서 어떤 *서사 기능*을 하는가
  e.g. protagonist, supporting_actor, witness, delayed_actor, pressure_source

flow_role:
  LifeStoryFlow 안에서 어떤 *위치*인가
  e.g. main_arc, supporting_arc, contrast_arc, echo_arc
```

### 2.3 schema_version 변경

`universal_story_seed_v1` → `universal_story_seed_v1_1`

```
[x] 추가만 — 기존 v1 consumer는 default value로 호환 가능
[ ] 필드 제거 / 타입 변경 — pressure_pattern dict는 *유지*
```

기존 *필드 제거 없음*. 따라서 v1 consumer는 default 값으로 v1.1 seed를 읽을 수
있고, v1.1 consumer는 v1 seed를 신규 필드 default로 읽을 수 있다 (마이그레이션
부담 최소).

### 2.4 마이그레이션 plan

```
1. UniversalStorySeed dataclass에 신규 필드 추가 (default 값 포함)
2. to_dict / from_dict가 신규 필드 emit / accept
3. universal_seed_adapter에 archetype map / role map / flow_role map 추가
   (Phase D 작업)
4. 기존 산출 SkeletonOutput JSON 재생성
5. drift guard 갱신 (Phase F)
```

## 3. 영향 (Impact)

### 3.1 affected modules

```
- engine/observer/universal_story_seed.py (dataclass)
- engine/observer/universal_seed_adapter.py (Phase D 변경)
- engine/observer/skeleton_output.py (schema_version bump 검토)
- engine/anchor/universal_seed_renderer.py (신규 필드 렌더링)
- tests/test_skeleton/test_phase2_prep.py (EXPECTED_UNIVERSAL_SEED_FIELDS)
- tests/test_skeleton/test_universal_taxonomy.py (roundtrip 갱신)
```

### 3.2 acceptance test 갱신

```
- 신규: test_universal_seed_v1_1_has_change_pattern
- 신규: test_universal_seed_v1_1_has_flow_role
- 신규: test_supporting_archetypes_distinct_from_supporting_roles
- 갱신: EXPECTED_UNIVERSAL_SEED_FIELDS in test_phase2_prep.py
```

### 3.3 flesh engine 영향

Phase 3 ML이 아직 시작되지 않았으므로 학습된 모델 재학습 불필요. 단, ML
입력 schema 정의에 신규 필드 명시.

## 4. 대안 (Alternatives Considered)

### 4.1 대안 A: pressure_pattern dict 그대로 유지

신규 필드 (change_pattern, arc_direction, flow_role, turning_points_count)를
pressure_pattern dict 안에 string key로 추가.

*왜 채택하지 않았는가*: dataclass field 수준의 type safety / drift guard 적용
불가. flesh engine이 dict key 존재 여부를 매번 검사해야 함. 검증 보고서가
지적한 *책임 불명확* 문제 해결 안 됨.

### 4.2 대안 B: 새 dataclass UniversalStorySeedV2

UniversalStorySeed v1을 동결하고 별도 V2 클래스를 신설.

*왜 채택하지 않았는가*: 기존 SkeletonOutput v1 consumer가 즉시 깨진다.
산출 파일 마이그레이션 비용 큼. 추가 필드는 default 값으로 호환 가능하므로
별도 클래스 불필요.

### 4.3 대안 C: 신규 필드를 anchor_metadata로 이동

main_archetype / flow_role 등을 UniversalStorySeed가 아니라 SkeletonOutput.
anchor_metadata에 모음.

*왜 채택하지 않았는가*: anchor_metadata는 anchor-specific 정보 (peter, judas 등)
이고 신규 필드는 *universal*이다. 경계 위반.

## 5. 리스크

```
- 기존 SkeletonOutput JSON 산출은 신규 필드 누락 → 재생성 필요
- universal_seed_adapter가 신규 필드를 채울 수 있어야 함 (Phase D 의존)
- flesh engine 미시작이므로 학습 데이터 호환성 문제 없음
- pressure_pattern dict 유지로 deprecated 누수 가능 — 향후 RFC-0002에서 제거
```

## 6. 승인 체크리스트

```
[x] 동기가 외부 요구사항 (Validation Fix Plan §C) 에 명시 매핑됨
[x] 대안 최소 2개 검토됨 (총 3개)
[x] schema_version bump 결정 명시됨 (v1 → v1_1, additive)
[x] 영향 받는 모든 모듈 list 작성됨
[x] acceptance test 갱신 plan 명시됨
[x] flesh engine 영향 검토됨 (미시작이므로 영향 없음)
[x] 마이그레이션 plan 작성됨 (additive이므로 default 값으로 호환)
```

## 7. 변경 이력

| 일시 | 변경 |
|---|---|
| 2026-05-09 | initial draft + approved (Validation Fix Plan Phase C 일부) |

---

*RFC-0001 채택. 후속 RFC가 이 결정을 reverse하지 않는 한 v1.1 contract 동결.*
