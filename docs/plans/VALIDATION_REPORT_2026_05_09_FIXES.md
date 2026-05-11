# Validation Report — Phase 2.5 Fixes (2026-05-09)

> Per `docs/WITNESS_NARRATIVE_MODE_VALIDATION_FIX_PLAN.md` Phase G.

이 보고서는 검증 보고서에서 식별된 결함을 Phase 2.5 fix 사이클로 어떻게
해소했는지 정리한다. 출처는 코드 + 테스트 + RFC-0001.

---

## 1. 8개 필수 수정 대응표

| # | 결함 | 대응 | 코드 위치 | 테스트 |
|---|------|------|----------|--------|
| P1-A | conflict_amplification_rate 정의 모호 | conflict_intensity_peak (회차 단위 최대 강도, 0~5 레벨) | `scripts/annotation/prompt_templates.py` `ANNOTATION_FEATURES` | `tests/test_skeleton/test_phase2_prep.py::test_prompt_features_match_annotation_guide` |
| P1-B | resolution_to_dangling_ratio 단일 회차 측정 불가 | dangling_thread_generation (회차 내 신규 미해결, 0~5 레벨) | 동상 | 동상 |
| P2-A | natural_collisions에 desire/pressure 혼재 | colliding_desires + colliding_pressures 분리 (natural_collisions는 deprecated 호환용으로만 잔존) | `content/universal/desire_taxonomy.json` | `test_universal_taxonomy.py::test_desire_taxonomy_split_collisions_into_desires_and_pressures` |
| P2-B | unknown axis 의도 불분명 | unknown.status="fallback_only", valid_for_training=false | `content/universal/conflict_axes.json` | `test_unknown_axis_is_fallback_only` |
| P2-C | crowd_mood가 pressure로 오인 | crowd_mood.kind="environmental_pressure_state" + deprecated_as_pressure=true; 신규 crowd_tension은 aversive pressure | `content/universal/pressure_taxonomy.json` | `test_crowd_mood_marked_as_environmental_state`, `test_crowd_tension_added_as_aversive_pressure` |
| P3-A | UniversalStorySeed의 main_role/main_archetype 책임 불명확 | RFC-0001 + v1.1 dataclass: main_archetype(인물 유형) vs main_role(서사 기능) 분리; supporting_archetypes/change_pattern/arc_direction/relationship_function/flow_role/turning_points_count 신규 | `engine/observer/universal_story_seed.py`, `docs/plans/RFC_UNIVERSAL_STORY_SEED_V1_1.md` | `test_universal_seed_v1_1_*` (4 tests) |
| P3-B | adapter가 archetype/role/pressure/supporting role 손실 | `archetype_by_seed` 필수화, MAIN_ROLE_BY_ARCHETYPE / FLOW_ROLE_BY_SEED / SUPPORTING_ARCHETYPES_BY_SEED / 4-tier pressure fallback 도입 | `engine/observer/universal_seed_adapter.py` | `test_adapter_*` (8 tests) |
| P3-C | SkeletonOutput.flow=null | LifeStoryFlow v1.1: flow_roles dict 추가, assemble_skeleton_output에서 자동 채움 | `engine/observer/skeleton_output.py`, adapter | `test_skeleton_flow_*` (4 tests) |

## 2. 5개 권고 수정 대응표

| # | 권고 | 대응 |
|---|------|------|
| R1 | drift guard에 type/default/frozen/mutability 검사 | `test_phase2_prep.py` 9 신규 drift guard 테스트 |
| R2 | adapter unmapped phrase는 audit에 누적 | `audit_trail.unmapped_pressure_phrases`, AuditTrail v1.1 |
| R3 | unknown axis 카운트는 audit_trail에 기록 | `audit_trail.unknown_axis_count` |
| R4 | empty pressure seed audit | `audit_trail.missing_pressure_seeds` |
| R5 | RFC governance 적용 | RFC-0001 작성, schema_version bump 추적 |

---

## 3. SkeletonOutput Before / After diff

### Before (v1)

```json
{
  "seed_id": "S02",
  "conflict_axis_id": "uncertainty_vs_commitment",
  "main_role": "main",
  "main_archetype": "",
  "dominant_pressures": [],
  "dominant_desires": ["commitment"],
  "supporting_roles": ["supporting_1", "supporting_2"],
  "pressure_pattern": {}
}
```

### After (v1.1)

```json
{
  "schema_version": "universal_story_seed_v1_1",
  "seed_id": "S02",
  "conflict_axis_id": "uncertainty_vs_commitment",
  "main_role": "supporting_actor",
  "main_archetype": "uncertain_actor",
  "dominant_pressures": ["confusion"],
  "dominant_desires": ["commitment"],
  "supporting_archetypes": ["watcher"],
  "supporting_roles": ["witness"],
  "pressure_pattern": {
    "turning_points_count": 2,
    "primary_pressure": "confusion",
    "primary_desire": "commitment",
    "pressure_fallback_tier": "conflict_axis"
  },
  "change_pattern": "delay_under_pressure",
  "arc_direction": "uncertainty_to_withdrawal",
  "relationship_function": "contrast_to_main_arc",
  "flow_role": "supporting_uncertainty",
  "turning_points_count": 2
}
```

flow:

```json
{
  "schema_version": "life_story_flow_v1_1",
  "ordering": "evidence_derived",
  "ordered_seed_ids": ["S01", "S03", "S02", "S04"],
  "flow_roles": {
    "S01": "main_arc",
    "S02": "supporting_uncertainty",
    "S03": "witness_arc",
    "S04": "delayed_response_arc"
  }
}
```

audit_trail:

```json
{
  "schema_version": "audit_trail_v1_1",
  "unmapped_pressure_phrases": [],
  "missing_pressure_seeds": [],
  "unknown_axis_count": 0
}
```

## 4. Fast Suite 결과

```text
2,327 passed, 14 skipped, 133 deselected (94 sec)
회귀 0건. Phase 2.5 추가 테스트 23개 (skeleton 110 → 132).
```

세부:
- skeleton 132 tests
- Phase A (rename): 0 회귀
- Phase B (taxonomy): 5 신규 (collision split + unknown + crowd_*)
- Phase C (RFC + v1.1 dataclass): 5 신규 (change_pattern/flow_role/turning_points/supporting_archetypes/RFC doc)
- Phase D (adapter lossless): 8 신규 (archetype required/no placeholder/main_role/main_archetype/4-tier fallback ×2/unmapped/supporting/audit)
- Phase E (flow): 4 신규 (not null/main first/coverage/disable)
- Phase F (drift guard): 9 신규 (frozen/type/default/factory/schema_version/audit/flow)

## 5. 남은 위험

```
- pressure_pattern dict는 deprecated v1 호환용으로 유지. 후속 RFC-0002에서 제거.
- desire_taxonomy.natural_collisions 필드도 deprecated 유지 (compat).
- 아직 *실제 LLM API 호출 / 실제 줄거리 fetch* 미수행 — Phase 3 ML 시작 시 별도 acceptance.
- archetype_by_seed default가 Peter baseline에 hardcoded. 다른 anchor 추가 시 anchor별 default map 분리 필요.
- `crowd_tension`은 phrase mapping이 2개뿐 (`crowd hostility rises`, `crowd turns aggressive`). real data로 phrase 카탈로그 확장 필요.
```

## 6. Phase 3 Go / No-Go 판정

### Go 조건 (Plan §7) 검증

| 조건 | 상태 |
|------|------|
| Adapter lossless tests 통과 | ✅ 8/8 |
| SkeletonOutput v1.1 생성 성공 | ✅ |
| unknown axis 0건 또는 audit 명시 | ✅ (Peter baseline 0건, audit_trail.unknown_axis_count=0) |
| dominant_pressures empty 0건 또는 audit 명시 | ✅ (4-tier fallback으로 0건; 잔존 시 missing_pressure_seeds) |
| supporting placeholder 0건 | ✅ |
| feature definition reliability risk 해소 | ✅ (회차 단위 측정 가능 anchor + 0-5 레벨) |
| fast suite 회귀 0 | ✅ (2,327 pass) |

### No-Go 조건 검증

| 조건 | 상태 |
|------|------|
| main_archetype 빈 seed 존재 | ✅ 0건 |
| main_role == "main" seed 존재 | ✅ 0건 |
| supporting_1/supporting_2 존재 | ✅ 0건 |
| dominant_pressures silent empty 존재 | ✅ 0건 (audit-aware fallback) |
| unknown axis가 정상 seed로 통과 | ✅ 0건 |
| drift guard가 타입 변경 못 잡음 | ✅ 9 drift guard tests |

### 판정

```
Phase 3 (ML / Flesh Engine) 진입 GO.
```

단, *외부 의존성 (LLM API / fetch)* 를 동반하는 단계는 별도 ToS / robots.txt /
사용량 budget 검토 후 시작.

---

## 7. 변경 이력

| 일시 | 변경 |
|---|---|
| 2026-05-09 | initial — Phase 2.5 fix cycle (Phase A-G 일괄 처리, 23 신규 skeleton tests, RFC-0001) |
