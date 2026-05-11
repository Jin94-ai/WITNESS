# WITNESS Narrative Schema Version Map

> Per `docs/WITNESS_PHASE_2_9_PORTFOLIO_FINALIZATION_AND_PHASE_3_PREP_PLAN.md` §4 Issue 2.

이 문서는 WITNESS 산출물에 등장하는 **schema_version 문자열**의 관계를 정리한다.
한 산출물이 여러 schema_version을 가지는 이유와, *Phase 3 consumer*가 어떤
필드를 읽어야 하는지가 한눈에 보이도록 한다.

---

## 1. 한눈에 보는 schema 계보

```text
[Skeleton Layer]
  SkeletonOutput container         skeleton_output_v1            (frozen container)
    ├── seeds: UniversalStorySeed   universal_story_seed_v1_1     (RFC-0001, additive)
    ├── flow:  LifeStoryFlow         life_story_flow_v1_1          (additive)
    ├── evidence_ledger              evidence_ledger_v1
    ├── audit_trail                  audit_trail_v1_1              (additive)
    └── anchor_metadata              (anchor binding info, no version)

[Genre Adapter Layer — Phase 2.75 + 2.8]
  GenreAdaptedOutput               genre_adapted_output_v1_1     (Phase 2.8 polish)
    ├── adapted_seeds                (GenreAdaptedSeed, inline)
    └── adapted_flow                 genre_adapted_flow_v1_1
          └── adapted_outline_steps  (GenreAdaptedOutlineStep, inline)
  GenreAuditResult                  genre_audit_result_v1_1      (quality_warnings 필드)
  GenreRulebook (rulebook.json)     genre_rulebook_v1            (Phase 2.8 fields additive)
  GenreAuditBlocklist               genre_audit_blocklist_v1

[Cross-Genre Wrapper — Phase 2.8]
  GenreComparisonOutput             genre_comparison_output_v1   (multi-genre wrapper)

[Universal Taxonomy — Phase 2.5]
  pressure_taxonomy / desire_taxonomy / conflict_axes
                                    universal_taxonomy_v1_1

[Phase 3.0 Mode A Data Pipeline]
  EpisodeSynopsisRecord            normalized_synopsis_v1        (inline JSONL)
  AnnotationInput task             annotate_episode_synopsis_v1  (Plan §12)
  AnnotationOutput (LLM 응답)      episode_annotation_v1         (Plan §13)
  Hallucination report             hallucination_report_v1       (Phase 3.05 3 layer 분리)
    ├── valid_files_only_summary   (threshold 기준)
    ├── all_files_summary          (비교용)
    └── invalid_files              (parse fail + schema fail)
  Reliability report               reliability_report_v1         (summary.keep/revise/drop)
  Feature matrix                   feature_matrix_v1             (long-form CSV)
  Public-safe dataset              public_safe_dataset_v1        (synopsis_text 제거)

[Phase 3.1 No-ML Baseline — Two layers]
  GenreProfile                     genre_profile_v1              (KEEP feature weights)
  GenreProfiles index              genre_profiles_index_v1
  FleshBaselineOutput              flesh_baseline_output_v1      (seed × profile fit)
    └── recommendations[]
          └── score_breakdown      (Phase 3.05 — 항상 채워짐, mode 명시)
                ├── axis_match
                ├── pressure_overlap
                ├── compatibility_score
                ├── annotation_score (rulebook_only=None)
                ├── annotation_components
                ├── final_score
                └── mode (rulebook_only | annotation_blended)
  EpisodeIntensityOutput           episode_intensity_v1          (episode × profile intensity, Plan §22.2 Target B)
```

---

## 2. 컨테이너 vs. 내부 contract — 분리 이유

```text
SkeletonOutput container = skeleton_output_v1 (frozen)
UniversalStorySeed       = universal_story_seed_v1_1 (additive bump, RFC-0001)
```

**왜 SkeletonOutput v1을 유지했는가**:
- Phase 2.5에서 UniversalStorySeed는 의미 보존 강화로 v1.1로 bump
- 그러나 *컨테이너 자체*의 필드 set은 변경 없음 (seeds / flow / evidence_ledger /
  audit_trail / anchor_metadata 5개)
- 컨테이너 schema bump = 모든 consumer가 깨짐 → 비용 큼
- 내부 dataclass는 default value로 호환 (additive change만 허용)

**Drift guard**:
- `tests/test_skeleton/test_phase2_prep.py::test_skeleton_output_field_set_matches_frozen_contract`
  — 컨테이너 필드 set 변경 시 fail (RFC 트리거)
- 동일 test for UniversalStorySeed — 필드 set + type annotation + default + frozen 검사

---

## 3. Phase 별 산출물 schema

### 3.1 Phase 0/1/2 (skeleton + annotation)

| 산출물 | schema_version | 위치 |
|---|---|---|
| SkeletonOutput container | `skeleton_output_v1` | `engine/observer/skeleton_output.py` |
| UniversalStorySeed | `universal_story_seed_v1_1` | `engine/observer/universal_story_seed.py` |
| EvidenceLedger | `evidence_ledger_v1` | 위 동상 sub-dataclass |
| AuditTrail | `audit_trail_v1_1` | 위 동상 sub-dataclass |
| LifeStoryFlow | `life_story_flow_v1_1` | 위 동상 sub-dataclass |
| pressure_taxonomy | `universal_taxonomy_v1_1` | `content/universal/pressure_taxonomy.json` |
| desire_taxonomy | `universal_taxonomy_v1_1` | `content/universal/desire_taxonomy.json` |
| conflict_axes | `universal_taxonomy_v1_1` | `content/universal/conflict_axes.json` |
| EpisodeSynopsis (annotation 입력) | `synopsis_v1` | `scripts/data/synopsis_schema.py` |
| Annotation result | `annotation_v1` | `scripts/annotation/prompt_templates.py` |

### 3.2 Phase 2.75 + 2.8 (genre adapter)

| 산출물 | schema_version | 위치 |
|---|---|---|
| GenreRulebook | `genre_rulebook_v1` (Phase 2.8 fields additive) | `content/genres/{id}/rulebook.json` |
| GenreAuditBlocklist | `genre_audit_blocklist_v1` | `content/genres/{id}/audit_blocklist.json` |
| GenreAdaptedOutput | `genre_adapted_output_v1_1` (Phase 2.8 structured outline) | `engine/observer/genre_adapter.py` |
| GenreAdaptedFlow | `genre_adapted_flow_v1_1` | inline in adapter |
| GenreAuditResult | `genre_audit_result_v1_1` (quality_warnings 필드) | `engine/observer/genre_audit.py` |
| GenreComparisonOutput | `genre_comparison_output_v1` (cross-genre wrapper) | `scripts/narrative/run_genre_comparison.py` |

### 3.3 Phase 3.0 v1.1 (Mode A 데이터 파이프라인)

| 산출물 | schema_version | 위치 |
|---|---|---|
| EpisodeSynopsisRecord (normalized) | `normalized_synopsis_v1` (inline JSONL) | `scripts/data/normalize_synopsis.py` |
| AnnotationInput task | `annotate_episode_synopsis_v1` | `scripts/data/build_annotation_inputs.py` (Plan §12) |
| AnnotationOutput (LLM 응답) | `episode_annotation_v1` | `scripts/annotation/validate_annotation_outputs.py` (Plan §13) |
| Feature matrix CSV | `feature_matrix_v1` (long-form) | `scripts/annotation/build_feature_matrix.py` |
| Reliability report | `reliability_report_v1` (with `summary.keep/revise/drop` + `phase3_threshold_pass`) | `scripts/annotation/build_reliability_report.py` |
| Hallucination report | `hallucination_report_v1` (Phase 3.05 — 3 layer: `valid_files_only_summary`/`all_files_summary`/`invalid_files`) | `scripts/annotation/validate_annotation_outputs.py` |
| Public-safe dataset (synopsis_text 제거) | `public_safe_dataset_v1` (JSONL) | `scripts/data/build_public_safe_dataset.py` |
| Acceptance check report | inline (12 항목 `checks[]` + `summary`) | `scripts/data/verify_phase3_0_acceptance.py` |

### 3.4 Phase 3.1 prep (No-ML weighted score baseline)

| 산출물 | schema_version | 위치 |
|---|---|---|
| GenreProfile | `genre_profile_v1` (feature_weights + compatible_axes/pressures + data_source) | `engine/observer/genre_profile.py` |
| GenreProfiles index | `genre_profiles_index_v1` (profiles[] container) | 위 동상 `save_profiles` |
| FleshBaselineOutput | `flesh_baseline_output_v1` (recommendations[] + model + audit, Phase 3.05 — `score_breakdown` 항상 채움) | `engine/observer/flesh_baseline.py` |
| FleshRecommendation `score_breakdown` (Phase 3.05) | `{axis_match, pressure_overlap, compatibility_score, annotation_score (None for rulebook_only), annotation_components, final_score, mode}` | 위 동상 dataclass |
| EpisodeIntensityOutput (Plan §22.2 Target B) | `episode_intensity_v1` (intensity_records[] + kept_features_used + model + audit) | `engine/observer/episode_intensity.py` |

---

## 4. Phase 3 Consumer 가이드

### 4.1 ML/Flesh Engine 입력 후보

Phase 3.1 ML 입력으로 사용할 *primary contract*:

```text
SkeletonOutput v1
  ├── seeds: list[UniversalStorySeed v1.1]
  │   ├── seed_id, conflict_axis_id (anchor-clean)
  │   ├── main_archetype, main_role, supporting_archetypes / supporting_roles
  │   ├── dominant_pressures, dominant_desires
  │   ├── change_pattern, arc_direction, relationship_function
  │   ├── flow_role, turning_points_count
  │   ├── confidence_label, audit_status, evidence_count
  │   └── pressure_pattern (deprecated v1 호환)
  ├── flow: LifeStoryFlow v1.1
  │   ├── ordering, ordered_seed_ids
  │   └── flow_roles (Phase 2.5 신규)
  ├── evidence_ledger v1
  ├── audit_trail v1.1 (unmapped_pressure_phrases / missing_pressure_seeds /
  │                     unknown_axis_count)
  └── anchor_metadata
```

### 4.2 Genre Adapter 입력 게이트

Phase 2.75 §4.1 + Phase 2.5 strict_axis 게이트:

```text
adapt_skeleton_to_genre()는 다음 입력을 강제:
  - flow != None
  - audit_trail.unknown_axis_count == 0
  - audit_trail.forbidden_event_additions == 0
  - audit_trail.forbidden_dialogue_generation == 0
  - rulebook은 genre_rulebook_v1
```

### 4.3 ML Target 후보

Phase 2.75 + 2.8 출력을 supervised target으로 사용 가능:

```text
GenreAdaptedOutput v1.1 → ML이 학습할 *전환 결과*
  - adapted_outline_steps (rhythm × seed × phase template)
  - genre_role / genre_pressure (rulebook mapping)
  - cliffhanger (rulebook priority)
  - audit + quality_warnings (정확성 신호)
```

---

## 5. RFC 거버넌스

### 5.1 RFC가 *필요한* 변경

```text
- SkeletonOutput container 필드 추가/제거/타입 변경
- UniversalStorySeed 필드 추가/제거/타입 변경
- universal taxonomy schema_version bump
- frozen=True → frozen=False 변경
```

### 5.2 RFC가 *불필요한* 변경 (additive)

```text
- 새 anchor 추가 (content/anchors/{id}/binding.json)
- 새 장르 추가 (content/genres/{id}/rulebook.json)
- rulebook 안 새 필드 추가 (Phase 2.8: genre_lens_ko 등)
- Audit 안 quality_warnings 같은 soft 필드
```

### 5.3 작성된 RFCs

| RFC ID | 제목 | 상태 |
|---|---|---|
| RFC-0001 | UniversalStorySeed v1 → v1.1 | approved |

문서: [docs/plans/RFC_TEMPLATE.md](../plans/RFC_TEMPLATE.md) +
[RFC_UNIVERSAL_STORY_SEED_V1_1.md](../plans/RFC_UNIVERSAL_STORY_SEED_V1_1.md)

---

## 6. 검증 — drift guard 매핑

| schema | drift guard test |
|---|---|
| skeleton_output_v1 (필드 set) | `test_phase2_prep.py::test_skeleton_output_field_set_matches_frozen_contract` |
| universal_story_seed_v1_1 (field name + type + default + frozen) | `test_phase2_prep.py::test_universal_story_seed_*` (9 tests) |
| audit_trail_v1_1 (필드 set + tuple typing) | `test_phase2_prep.py::test_audit_trail_field_set_matches_contract` 등 |
| life_story_flow_v1_1 | 동상 |
| evidence_ledger_v1 | 동상 |
| anchor_metadata | 동상 |
| universal_taxonomy_v1_1 family | `test_phase2_prep.py::test_taxonomy_schema_versions_are_v1_family` |
| genre_rulebook_v1 + Phase 2.8 fields | `test_rulebook_drift_guard.py` (15+ tests) |
| genre_audit_result_v1_1 | `test_phase2_8_polish.py` |
| genre_comparison_output_v1 | `test_phase2_8_polish.py::test_comparison_json_has_comparison_summary` |
| episode_annotation_v1 (Phase 3.0 §13 schema) | `test_phase3_pipeline.py::test_validate_outputs_*` (8 tests) |
| hallucination_report_v1 3 layer (Phase 3.05) | `test_phase3_pipeline.py::test_validate_outputs_report_has_valid_only_summary` 등 (4 tests) |
| feature_matrix_v1 long-form CSV | `test_phase3_pipeline.py::test_build_feature_matrix` |
| reliability_report_v1 (summary.keep/revise/drop) | `test_phase3_pipeline.py::test_build_reliability_report_*` |
| feature coverage (Phase 3.0/3.1 cycle 12) | `test_phase3_pipeline.py::test_validate_outputs_feature_coverage_*` (4 tests) |
| genre_profile_v1 | `test_phase3_1_baseline.py::test_genre_profile_roundtrip` 등 |
| flesh_baseline_output_v1 + score_breakdown (Phase 3.05) | `test_phase3_1_baseline.py::test_recommend_seed_rulebook_only_score_breakdown` 등 (7 tests) |
| episode_intensity_v1 (Plan §22.2) | `test_phase3_1_baseline.py::test_episode_intensity_*` (8 tests) |
| Phase 3.05 4 layer 통합 e2e | `test_phase3_1_baseline.py::test_phase3_05_integrity_e2e_*` (3 tests) |
| Plan §18 acceptance checker | `test_phase3_pipeline.py::test_verify_acceptance_*` (6 tests) |

---

## 7. 한 줄 결론

```text
SkeletonOutput container는 v1을 유지.
내부 contract는 additive bump (UniversalStorySeed v1.1, audit_trail v1.1, flow v1.1).
Genre Adapter는 v1.1 polish 적용.
Cross-genre wrapper는 v1으로 출발.
Phase 3.0/3.1 schema 11종 추가 (Mode A pipeline 7 + No-ML baseline 4).
Phase 3.05 정직성 보강 — score_breakdown 항상 채움 + hallucination report 3 layer.
모든 변경은 drift guard tests로 강제.
```

---

## 8. 변경 이력

| 일시 | 변경 |
|---|---|
| 2026-05-10 | initial — Phase 2.9 §4 Issue 2 매핑 |
| 2026-05-11 | Phase 3.0 v1.1 + Phase 3.1 prep schemas 추가 (§3.3 + §3.4): normalized_synopsis_v1 / annotate_episode_synopsis_v1 / episode_annotation_v1 / hallucination_report_v1 (Phase 3.05 3 layer) / reliability_report_v1 / feature_matrix_v1 / public_safe_dataset_v1 / genre_profile_v1 / flesh_baseline_output_v1 / episode_intensity_v1 |
| 2026-05-11 | Phase 3.05 정직성 보강 반영 — flesh_baseline_output_v1 `score_breakdown` 항상 채움 (axis_match / pressure_overlap / compatibility_score / annotation_score [rulebook_only=None] / annotation_components / final_score / mode). hallucination_report_v1 3 layer 분리 (valid_files_only / all_files / invalid_files). §6 drift guard 매핑에 Phase 3 tests 13행 추가 |
