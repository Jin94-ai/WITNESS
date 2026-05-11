# WITNESS docs/ — Master Index

**Date**: 2026-05-10
**Purpose**: 현재 살아있는 docs 한눈에 보기. *archive 자료*는 §10에서 별도 정리.

> **2026-05-11 갱신** (Phase 3.0 v1.1 + Phase 3.1 prep): Phase 2.5 + 2.75 + 2.8 + 2.9 + **Phase 3.0 v1.1 Mode A 파이프라인** (7 스크립트) + **Phase 3.1 prep** (No-ML weighted score baseline + demo).
>
> **메인 portfolio asset**: [docs/portfolio/demo_genre_comparison/index.html](portfolio/demo_genre_comparison/index.html)
> — 같은 universal skeleton이 두 장르 (한국 막장 / 일본 정적)로 다르게 변환되는 모습 side-by-side.
>
> **포트폴리오 reading order**: [docs/portfolio/README.md](portfolio/README.md) (Main → Evidence → Appendix).

---

## 0. Portfolio 메인 (먼저 보세요)

| 위치 | 역할 |
|---|---|
| [docs/portfolio/README.md](portfolio/README.md) | **Reading order** — 메인 / evidence / appendix |
| [docs/portfolio/demo_genre_comparison/index.html](portfolio/demo_genre_comparison/index.html) | **메인 portfolio asset** — cross-genre comparison (self-contained HTML) |
| [docs/portfolio/demo_flesh_baseline/index.html](portfolio/demo_flesh_baseline/index.html) | **Phase 3.1 prep asset (seed × profile fit, Target A)** — No-ML weighted score baseline (seed별 genre fit, 설명 가능) |
| [docs/portfolio/demo_adaptation_recommendation/index.html](portfolio/demo_adaptation_recommendation/index.html) | **Phase 3.1 prep asset (seed → ranked top-K genres, Target C)** — §22.3 Adaptation Recommendation HTML demo. ranked card view + 1순위 분포 bar. Generators: `run_adaptation_recommendation.py` → `build_adaptation_recommendation_demo.py`. Non-Claims + uncalibrated + Rule #14. |
| [docs/portfolio/demo_episode_intensity/index.html](portfolio/demo_episode_intensity/index.html) | **Phase 3.1 prep asset (episode × genre intensity, Target B, fixture-only)** — §22.2 Episode Intensity HTML demo. 10 records × 2 genres arc bar chart + per-record feature contributions. *Fictional fixture-only* banner (cycle 40) — `tests/fixtures/annotation_public_safe/` 기반. Operating Guide §9 deploy 카테고리: `fixture-only`. |
| [docs/portfolio/FLESH_BASELINE_DEMO.md](portfolio/FLESH_BASELINE_DEMO.md) | Phase 3.1 baseline cover doc — 사용법 / score 공식 / Acceptance |
| `scripts/annotation/build_episode_intensity_demo.py` | **Phase 3.1 cycle 10 (episode × profile intensity)** — Plan §22.2 Target B demo HTML 생성기. title × genre arc bar chart + per-record feature contributions. 사용자 데이터로 Operating Guide Step 13b에서 deploy. |
| [docs/portfolio/demo_rubric/README.md](portfolio/demo_rubric/README.md) | **Rubric directive 결과물 (Phase 3.05, 15 cycle)** — 4-Axis Discovery Candidate Classifier 8-step flowchart 모든 endpoint + Result-7~11 ensemble layer (real e2e / multi-seed §H8 / multi-agent / cross-scenario / HTML viz). CLI: `scripts/rubric/run_rubric.py`. Non-Claims + uncalibrated_phase3_placeholder. |
| [docs/portfolio/demo_rubric/ensemble_visualization.html](portfolio/demo_rubric/ensemble_visualization.html) | **Result-11 visual asset** — 3 ensembles (cross_scenario 19/20 + multi_agent 14/15 + multi_seed 4/5) 통합 HTML (self-contained, 10.9KB). discovery_class 색상 분포 / per-context table / axis means / Non-Claims + Rule #14. Generator: `scripts/rubric/build_ensemble_html.py`. |
| [docs/portfolio/demo_genre_comparison/comparison.json](portfolio/demo_genre_comparison/comparison.json) | machine-readable comparison output (`genre_comparison_output_v1`) |
| [data/narrative/genre_comparison_output.json](../data/narrative/genre_comparison_output.json) | 위 동상 mirror (data/ 영역) |
| [docs/portfolio/GENRE_ADAPTER_DEMO.md](portfolio/GENRE_ADAPTER_DEMO.md) | Genre Adapter 사용법 / 신뢰성 검증 / 시연 절차 |
| [docs/specs/NARRATIVE_SCHEMA_VERSION_MAP.md](specs/NARRATIVE_SCHEMA_VERSION_MAP.md) | schema_version 관계 (skeleton_output_v1 + universal_story_seed_v1_1 + genre_adapted_output_v1_1 + genre_comparison_output_v1) |

---

## 0. 30분 안에 프로젝트 이해 (필독 5)

| 파일 | 역할 |
|---|---|
| [README.md](../README.md) | 프로젝트 소개 + 빠른 실행 |
| [CLAUDE.md](../CLAUDE.md) | AI 작업 행동 강령 + HARNESS H1-H8 |
| [DESIGN.md](../DESIGN.md) | 4-layer 아키텍처 + v0.7 설계 + Visual Layer §11 |
| [docs/SUMMARY_PHASES_1_TO_7.md](SUMMARY_PHASES_1_TO_7.md) | **Lee plan.md 7-phase 누적 결과 종합** |
| [docs/CANONICAL_MANIFEST.md](CANONICAL_MANIFEST.md) | 무엇을 먼저 봐야 하는지 |

---

## 1. 현재 활성 directive

| 파일 | 역할 |
|---|---|
| [docs/WITNESS_PHASE_3_05_PREP_INTEGRITY_AND_VALIDATOR_HARDENING_PLAN.md](WITNESS_PHASE_3_05_PREP_INTEGRITY_AND_VALIDATOR_HARDENING_PLAN.md) | **현재 메인 directive (Phase 3.05)** (2026-05-11). Cycle 7-12 prep 검수 후 정직성/검증성 보강. Step 1-6 모두 ✅ |
| [docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md](WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md) | 모 directive (Phase 3.0/3.1 prep 전체). v1.1 Phase 3.0 Mode A pipeline ✅ + Phase 3.1 No-ML baseline ✅ (외부 의존 0). 사용자 승인 후 즉시 운영 가능 |
| [docs/plans/PHASE_3_0_PIPELINE_OPERATING_GUIDE.md](plans/PHASE_3_0_PIPELINE_OPERATING_GUIDE.md) | Phase 3.0 v1.1 Mode A 9 step + Phase 3.1 baseline 4 step (Step 10-13: profiles / flesh / episode_intensity / demo 13a+13b) — 총 13 step + **§9 Deploy Status Matrix (Phase 3.05)** 운영 절차 |
| [docs/plans/PHASE_3_0_DATA_CARD.md](plans/PHASE_3_0_DATA_CARD.md) | pilot 종료 후 사용자 작성 data card template |
| [docs/plans/PHASE_3_0_DATA_PILOT_REPORT.md](plans/PHASE_3_0_DATA_PILOT_REPORT.md) | pilot 최종 검증 보고서 template (12/12 Acceptance + Phase 3.1 GO/NO-GO) |
| [docs/WITNESS_PHASE_2_9_PORTFOLIO_FINALIZATION_AND_PHASE_3_PREP_PLAN.md](WITNESS_PHASE_2_9_PORTFOLIO_FINALIZATION_AND_PHASE_3_PREP_PLAN.md) | 직전 directive (2026-05-10). Phase 2.9 (✅ 완료) |
| [docs/plans/PHASE_3_0_DATA_PILOT_PREP.md](plans/PHASE_3_0_DATA_PILOT_PREP.md) | Phase 3.0 진입 준비 문서 — 범위 / 파일럿 크기 / 저장 정책 / 신뢰도 기준 |
| [docs/plans/DATA_SOURCE_CANDIDATE_REVIEW.md](plans/DATA_SOURCE_CANDIDATE_REVIEW.md) | Phase 3.0 후보 데이터 소스 검토 표 (실제 fetch 전 robots.txt + ToS 검토용) |
| [docs/plans/PHASE_3_0_APPROVAL_CHECKLIST.md](plans/PHASE_3_0_APPROVAL_CHECKLIST.md) | Phase 3.0 시작 전 사용자 승인 체크리스트 (5+2 항목) |
| [docs/WITNESS_PHASE_2_8_GENRE_ADAPTER_POLISH_AND_PHASE_3_PILOT_PLAN.md](WITNESS_PHASE_2_8_GENRE_ADAPTER_POLISH_AND_PHASE_3_PILOT_PLAN.md) | 직전 directive (2026-05-10). Phase 2.8 Polish (✅ 완료) |
| [docs/WITNESS_PHASE_2_75_GENRE_ADAPTER_MVP_PLAN.md](WITNESS_PHASE_2_75_GENRE_ADAPTER_MVP_PLAN.md) | 직전 directive (2026-05-10). Rule-based Genre Adapter MVP. ✅ 완료 |
| [docs/WITNESS_NARRATIVE_MODE_VALIDATION_FIX_PLAN.md](WITNESS_NARRATIVE_MODE_VALIDATION_FIX_PLAN.md) | 더 이전 (2026-05-09). Phase 2.5 Validation Fix — 의미 보존성 보강. ✅ 완료 |
| [docs/witness_narrative_mode_plan.md](witness_narrative_mode_plan.md) | 모ㅏplan (2026-05-09). Skeleton (결정론적) + Flesh (ML) 이중 구조 개편. Phase 0/1/2 prep 완료 |
| [docs/plans/RFC_TEMPLATE.md](plans/RFC_TEMPLATE.md) | SkeletonOutput / UniversalStorySeed / taxonomy 변경 시 의무 RFC 양식 |
| [docs/plans/RFC_UNIVERSAL_STORY_SEED_V1_1.md](plans/RFC_UNIVERSAL_STORY_SEED_V1_1.md) | RFC-0001 (approved) — UniversalStorySeed v1 → v1.1 (semantic-preservation upgrade) |
| [docs/plans/VALIDATION_REPORT_2026_05_09_FIXES.md](plans/VALIDATION_REPORT_2026_05_09_FIXES.md) | Phase 2.5 검증 보고서 — 8 필수 + 5 권고 대응표 + Phase 3 Go 판정 |
| [docs/plans/GENRE_ADAPTER_MVP_AUDIT.md](plans/GENRE_ADAPTER_MVP_AUDIT.md) | Phase 2.75 검증 보고서 — Acceptance 11/11 met + Phase 3 GO 판정 |
| [docs/plans/GENRE_ADAPTER_POLISH_AUDIT.md](plans/GENRE_ADAPTER_POLISH_AUDIT.md) | Phase 2.8 검증 보고서 — 6 issue 대응 + Acceptance 12/12 met + No-Go 0건 |
| [docs/data/SELECTION_CRITERIA.md](data/SELECTION_CRITERIA.md) | Phase 1 — 막장/비교군 작품 선정 기준 + ToS 안전선 |
| [docs/data/DATA_CARD_TEMPLATE.md](data/DATA_CARD_TEMPLATE.md) | Phase 1 — 데이터 카드 템플릿 |
| [docs/annotation/ANNOTATION_GUIDE.md](annotation/ANNOTATION_GUIDE.md) | Phase 2 — 7 정량 features (v1.1: conflict_intensity_peak / dangling_thread_generation 0-5 레벨) |
| [docs/WITNESS_STORY_EMERGENCE_IMPLEMENTATION_PLAN.md](WITNESS_STORY_EMERGENCE_IMPLEMENTATION_PLAN.md) | 이전 directive (2026-05-06). Story Candidate Pack — Stage 5-7. 현재 Skeleton 자산으로 흡수됨 |
| [docs/WITNESS_NARRATIVE_MINING_PLAN.md](WITNESS_NARRATIVE_MINING_PLAN.md) | 이전 plan — narrative mining engine 전환. Stage 1-4 (Moment/Link/Thread/Opportunity) 구현 |
| [docs/WITNESS_PROJECT_RESET_AND_TEXT_FIRST_PLAN.md](WITNESS_PROJECT_RESET_AND_TEXT_FIRST_PLAN.md) | 더 이전 — text-first pivot |
| [docs/plan.md](plan.md) | 가장 이전 long-range plan (참조용) |

### 1.0a Skeleton-Flesh 분리 산출물 (2026-05-09 → 2026-05-10 갱신)

| 파일 | 역할 |
|---|---|
| [content/universal/pressure_taxonomy.json](../content/universal/pressure_taxonomy.json) | 12 universal pressures (v1.1: crowd_tension 추가, crowd_mood = environmental_state) |
| [content/universal/desire_taxonomy.json](../content/universal/desire_taxonomy.json) | 8 universal desires (v1.1: colliding_desires + colliding_pressures 분리) |
| [content/universal/conflict_axes.json](../content/universal/conflict_axes.json) | 8 conflict axes (v1.1: unknown.status="fallback_only") |
| [engine/observer/universal_story_seed.py](../engine/observer/universal_story_seed.py) | UniversalStorySeed v1.1 (anchor-clean, RFC-0001 — main_archetype/main_role/supporting_archetypes/change_pattern/arc_direction/relationship_function/flow_role/turning_points_count) |
| [engine/observer/skeleton_output.py](../engine/observer/skeleton_output.py) | **FROZEN** SkeletonOutput contract v1 (sub-types: LifeStoryFlow v1.1 + AuditTrail v1.1) |
| [engine/observer/universal_seed_adapter.py](../engine/observer/universal_seed_adapter.py) | Lossless adapter (4-tier pressure fallback / archetype/role/flow_role default maps / strict_axis 게이트 / validate_skeleton_semantic + is_skeleton_phase3_ready) |
| [engine/anchor/anchor_registry.py](../engine/anchor/anchor_registry.py) | AnchorRegistry + AnchorBinding |
| [engine/anchor/universal_seed_renderer.py](../engine/anchor/universal_seed_renderer.py) | UniversalStorySeed + AnchorBinding → 한국어 surface (v1.1 fields 노출) |
| [content/anchors/peter_scarcity_baseline/binding.json](../content/anchors/peter_scarcity_baseline/binding.json) | 영어→한국어 매핑 |
| [scripts/data/synopsis_schema.py](../scripts/data/synopsis_schema.py) | Phase 1 — episode synopsis schema + validators (network IO 0) |
| [scripts/data/collect_synopsis.py](../scripts/data/collect_synopsis.py) | Phase 1 — CLI orchestrator skeleton (validate / list-candidates) |
| [scripts/annotation/prompt_templates.py](../scripts/annotation/prompt_templates.py) | Phase 2 v1.1 — LLM 프롬프트 + multi-AI 합성 + leveled validation + migrate_deprecated_annotation |
| [scripts/annotation/synthesize_annotations.py](../scripts/annotation/synthesize_annotations.py) | Phase 2 — synthesize CLI (`--migrate-deprecated` v1→v1.1) |
| [scripts/annotation/annotate_with_llm.py](../scripts/annotation/annotate_with_llm.py) | Phase 2 — fixture mode CLI (`--migrate-deprecated`) |
| [scripts/skeleton/validate_skeleton_phase3.py](../scripts/skeleton/validate_skeleton_phase3.py) | Phase 2.5 cycle 5 — Phase 3 Go gate CLI (exit 0/1/2 + `--lenient`/`--json`) |
| [tests/test_skeleton/](../tests/test_skeleton/) | 169 tests (taxonomy / contract drift / sub-dataclass drift / leveled validation / phase 3 ready / RFC) |

### 1.0b Phase 2.75 Genre Adapter MVP 산출물 (2026-05-10 신규)

| 파일 | 역할 |
|---|---|
| [content/genres/korean_morning_melodrama/rulebook.json](../content/genres/korean_morning_melodrama/rulebook.json) | 한국 아침 막장 드라마 rulebook (Phase 2.8: + genre_lens_ko / outline_templates × phase / outline_step_mapping / outline_role_assignment_priority) |
| [content/genres/korean_morning_melodrama/audit_blocklist.json](../content/genres/korean_morning_melodrama/audit_blocklist.json) | forbidden_event_tokens / dialogue markers / source imitation |
| [content/genres/japanese_quiet_drama/rulebook.json](../content/genres/japanese_quiet_drama/rulebook.json) | 일본 정적 드라마 rulebook (반대 톤 — 절제 / 가라앉힘 / atmosphere over plot) |
| [content/genres/japanese_quiet_drama/audit_blocklist.json](../content/genres/japanese_quiet_drama/audit_blocklist.json) | 일본 드라마 audit blocklist |
| [engine/observer/genre_rulebook.py](../engine/observer/genre_rulebook.py) | GenreRulebook + GenreAuditBlocklist + select_amplifier / select_cliffhanger / map_arc_direction_to_phrase / map_flow_role_to_function |
| [engine/observer/genre_adapter.py](../engine/observer/genre_adapter.py) | GenreAdaptedSeed/Flow/Output dataclass + adapt_skeleton_to_genre (structure_only, 입력 게이트) |
| [engine/observer/genre_audit.py](../engine/observer/genre_audit.py) | 4 영역 audit (forbidden_event / dialogue / source_imitation / evidence_preservation) |
| [scripts/narrative/apply_genre_adapter.py](../scripts/narrative/apply_genre_adapter.py) | CLI: skeleton + genre → GenreAdaptedOutput JSON |
| [scripts/narrative/run_genre_demo.py](../scripts/narrative/run_genre_demo.py) | CLI: 단일 장르 portfolio demo (HTML / md / audit md / json) |
| [scripts/narrative/run_genre_comparison.py](../scripts/narrative/run_genre_comparison.py) | CLI: N개 장르 side-by-side 비교 demo (Phase 2.8: comparison_summary + 새 HTML hierarchy) |
| [docs/portfolio/demo_genre/index.html](portfolio/demo_genre/index.html) | korean_morning_melodrama 단일 장르 데모 (self-contained) |
| [docs/portfolio/demo_genre_japanese/index.html](portfolio/demo_genre_japanese/index.html) | japanese_quiet_drama 단일 장르 데모 |
| [docs/portfolio/demo_genre_comparison/index.html](portfolio/demo_genre_comparison/index.html) | **메인 portfolio asset** — 두 장르 side-by-side 비교 (Plan §14.2 메인 흐름) |
| [docs/portfolio/GENRE_ADAPTER_DEMO.md](portfolio/GENRE_ADAPTER_DEMO.md) | Genre Adapter portfolio cover doc |
| [tests/test_genre/](../tests/test_genre/) | 94 tests (rulebook / adapter / audit / demo CLI / comparison / drift guard / abstraction proof / Phase 2.8 polish) |

### 1.0 Portfolio Demo + Story Assembly — Active Main (2026-05-08)

**일반인용 한국어 데모 v2 (Episode-centric)** — 명령어 한 번으로 self-contained HTML + Episode Outline + 4 seed cards + 6단계 파이프라인 진행.

- 메인: [docs/portfolio/demo/index.html](portfolio/demo/index.html) — Episode 중심 7-section
- **Episode Outline**: [docs/portfolio/demo/episode_outline.md](portfolio/demo/episode_outline.md) (한국어, 한 편)
- Seed Cards (보조): [docs/portfolio/demo/story_seed_cards.md](portfolio/demo/story_seed_cards.md)
- Run Log: [docs/portfolio/demo/run_log.md](portfolio/demo/run_log.md) (6단계 + duration)
- 검증 리포트: [docs/portfolio/demo/evidence_report.md](portfolio/demo/evidence_report.md)
- 데모 폴더 README: [docs/portfolio/demo/README.md](portfolio/demo/README.md)
- Plan: [docs/WITNESS_PORTFOLIO_DEMO_PIPELINE_PLAN.md](WITNESS_PORTFOLIO_DEMO_PIPELINE_PLAN.md) + Story Assembly directive
- Orchestrator: `python scripts/narrative/run_portfolio_demo.py` (~0.25s, 8 outputs, fresh engine simulation per run)
- 모듈: `engine/observer/data_narrative.py` (synthesizer 2026-05-08) + `pressure_summary.py` + `story_seed_card.py` + `episode_outline.py` + `run_log.py`
- 테스트: 86+ (13 data_narrative + 22 episode_outline (incl. 4 evidence-integration) + 9 run_log + 16 portfolio_demo_episode + 18 portfolio_demo + 8 기존)
- **Data-driven body** (2026-05-08): seed가 다르면 logline / acts / supporting one-lines가 *실제 수치*까지 다름 (예: "39단계 동안 가라앉지 않는다" vs "29단계 동안 ...")

### 1.0 Life Arc Narrative — 시간대 기반 timeline (2026-05-08)

**베드로 공생애 142일 timeline** — engine PhasedSimulationWorld 시뮬레이션 결과를 시간대별로 narrative로 변환.

- 메인 (5 phases): [.md](portfolio/demo/life_arc_demo.md) / [.html](portfolio/demo/life_arc_demo.html) / [.json](portfolio/demo/life_arc_demo.json)
- 주별 세밀 (21 weeks): [.md](portfolio/demo/life_arc_demo_by_week.md) / [.html](portfolio/demo/life_arc_demo_by_week.html) / [.json](portfolio/demo/life_arc_demo_by_week.json)
- Seed 비교: [docs/portfolio/demo/life_arc_seed_diversity.md](portfolio/demo/life_arc_seed_diversity.md) — 3 seeds, 정경 사건별 선택 차이 표 (~73% events differ)
- Orchestrators:
  - `python scripts/narrative/run_life_arc_demo.py [--full-passion] [--seed N] [--window by_phase|by_week]`
  - `python scripts/narrative/demo_life_arc_seed_diversity.py [--seeds 0,7,11]`
- 모듈: `engine/observer/life_arc_narrative.py` (5 dataclass + by_phase/by_week + render_md/_html)
- 테스트: 32 (26 life_arc + 6 seed diversity)
- HTML: self-contained (외부 자산 0, ~30 KB), silent run 압축 적용
- **Engine-driven**: 정경 사건 description은 `content/peter/phases/*/canonical_events.json`에서 verbatim 인용. 사건마다 *시뮬레이션 베드로의 선택*은 engine action_histories에서. seed가 다르면 같은 사건에 대해 다른 선택.

### 1.1 Story Viability Validation + Human Pick — Predecessor (2026-05-08)

**Stage E (Human Pick Test) 운영 추가**:
- 외부 의뢰 패키지: [docs/portfolio/HUMAN_PICK_TEST_PACK.md](portfolio/HUMAN_PICK_TEST_PACK.md) (single-file, email-friendly)
- 응답 템플릿: [data/narrative/human_pick_responses_template.json](../data/narrative/human_pick_responses_template.json)
- Aggregator: `scripts/narrative/aggregate_human_pick.py` → `docs/portfolio/HUMAN_PICK_RESULT.md` + JSON
- 사용 가이드: [docs/STORY_VIABILITY_USER_GUIDE.md](STORY_VIABILITY_USER_GUIDE.md) §2.5
- 테스트: 10 (`tests/test_narrative/test_human_pick_aggregator.py`)
- 현재 baseline: 1 reviewer self-eval — S01 Peter PASS, S02-S04 fail (selection rate 0)

**Stage A-D + F (자동 검증)**:

- 메인 산출물: [docs/portfolio/STORY_VIABILITY_REPORT.md](portfolio/STORY_VIABILITY_REPORT.md) — 4 candidates / 1 strong + 3 viable / 0 audit_fail / **SHIP** 등급
- Scene Briefs: [docs/portfolio/SCENE_BRIEFS.md](portfolio/SCENE_BRIEFS.md) (6-section structured per candidate)
- 1-page Treatments: [docs/portfolio/ONE_PAGE_TREATMENTS.md](portfolio/ONE_PAGE_TREATMENTS.md) (3-act + adaptation notes)
- 사용자 가이드: [docs/STORY_VIABILITY_USER_GUIDE.md](STORY_VIABILITY_USER_GUIDE.md) (Stage E Human Pick Test 운영)
- Plan: [docs/WITNESS_STORY_VIABILITY_VALIDATION_PLAN.md](WITNESS_STORY_VIABILITY_VALIDATION_PLAN.md)
- 모듈: `engine/observer/scene_brief.py` + `treatment.py` + `story_viability.py` + `story_audit.py`
- 빌더: `scripts/narrative/build_story_viability_report.py` (단일 명령으로 5 출력 모두 생성)
- Anchor blocklist: `content/anchors/peter_scarcity_baseline/audit_blocklist.json`
- 테스트: 19 (`tests/test_narrative/test_story_viability.py`)

### 1.1 Story Emergence — Predecessor (2026-05-06)

**Phase A+B+C (Identity + StoryCandidate + TurningPoint)**:
- 메인 산출물: [docs/portfolio/STORY_CANDIDATES.md](portfolio/STORY_CANDIDATES.md) (4 cards: Peter / Andrew / James / John)
- Machine-readable: [data/narrative/story_candidates.json](../data/narrative/story_candidates.json) (`story_candidates_v1`)
- 모듈: [engine/observer/identity_resolver.py](../engine/observer/identity_resolver.py) + [story_candidate.py](../engine/observer/story_candidate.py) + [story_candidate_builder.py](../engine/observer/story_candidate_builder.py)
- 매핑: [content/anchors/peter_scarcity_baseline/identity_map.json](../content/anchors/peter_scarcity_baseline/identity_map.json)
- 테스트: 26 (10 identity_resolver + 16 story_candidate_builder)

**Phase D+E+F (Relationships + Cross-seed + Console)**:
- Cross-seed report: [docs/portfolio/CROSS_SEED_STORY_PATTERNS.md](portfolio/CROSS_SEED_STORY_PATTERNS.md) — 5 seeds, 6/6 robust patterns
- Cross-seed JSON: [data/narrative/cross_seed_story_patterns.json](../data/narrative/cross_seed_story_patterns.json) (`cross_seed_story_patterns_v1`)
- Story Candidate Console (정적 HTML): [docs/portfolio/story_candidate_console.html](portfolio/story_candidate_console.html) (23KB self-contained)
- Aggregator: [engine/observer/cross_seed_pattern.py](../engine/observer/cross_seed_pattern.py)
- 빌더: `scripts/narrative/build_cross_seed_patterns.py`, `scripts/narrative/build_story_candidate_console.py`, `scripts/narrative/build_story_candidates.py`
- 5-seed dumps: `data/visual/dot_observer_data_seed{0..4}.json`
- 테스트 추가: 7 (cross_seed_pattern)

### 1.0 Phase 1-5 — Narrative Mining Engine (Active Main)

- 메인 산출물 (creator-facing): [docs/portfolio/NARRATIVE_OPPORTUNITIES.md](portfolio/NARRATIVE_OPPORTUNITIES.md) (4 threads, 1 strong)
- 정적 HTML 콘솔: [docs/portfolio/narrative_mining_console.html](portfolio/narrative_mining_console.html) (self-contained, 105 moments + 4 threads embedded)
- 메인 데이터: [data/narrative/](../data/narrative/) — `moments.json`, `moment_links.json`, `story_threads.json`, `narrative_opportunities.json`
- 모듈: [engine/observer/moment.py](../engine/observer/moment.py), [thread.py](../engine/observer/thread.py), [thread_builder.py](../engine/observer/thread_builder.py), [narrative_opportunity.py](../engine/observer/narrative_opportunity.py), [moment_extractor.py](../engine/observer/moment_extractor.py)
- 빌더: [scripts/narrative/](../scripts/narrative/) — `build_moments.py`, `build_story_threads.py`, `export_narrative_opportunities.py`, `build_mining_console.py`
- 테스트: `tests/test_observer/test_moment_extractor.py` (18) + `test_moment_linking.py` (15) + `test_story_thread_builder.py` (18) + `tests/test_narrative/` (18) = **69 tests**

### 1.1 Phase 11-12 — Text-first Observer Brief + Provenance Table (Active)

**Phase 11 (브리핑)**:
- 메인 산출물: [docs/demo/WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md](demo/WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md)
- Builder: [scripts/report/build_observer_brief.py](../scripts/report/build_observer_brief.py)
- 5분 데모: [docs/demo/WITNESS_TEXT_FIRST_DEMO_SCRIPT.md](demo/WITNESS_TEXT_FIRST_DEMO_SCRIPT.md)
- 케이스 스터디: [docs/portfolio/WITNESS_CASE_STUDY_TEXT_FIRST.md](portfolio/WITNESS_CASE_STUDY_TEXT_FIRST.md)
- Visual freeze 결정: [docs/visual/VISUAL_TRACK_FREEZE_DECISION.md](visual/VISUAL_TRACK_FREEZE_DECISION.md)
- 테스트: `tests/test_report/test_observer_brief.py` (10 tests)

**Phase 12 (필드 단위 provenance)**:
- 메인 산출물: [docs/demo/WITNESS_PROVENANCE_TABLE_PETER_SCARCITY.md](demo/WITNESS_PROVENANCE_TABLE_PETER_SCARCITY.md) (160 field rows)
- Builder: [scripts/report/build_provenance_table.py](../scripts/report/build_provenance_table.py)
- Machine-readable: [data/report/provenance_table.json](../data/report/provenance_table.json) (`provenance_table_v1` schema)
- 테스트: `tests/test_report/test_provenance_table.py` (8 tests)
- 집계: 59.4% source_derived / 25.0% source_inferred / 15.6% not_used (visual 명시 제외)

**Phase 13 (Portfolio Package v1, 2026-05-06)**:
- Case study: [docs/portfolio/WITNESS_CASE_STUDY_TEXT_FIRST.md](portfolio/WITNESS_CASE_STUDY_TEXT_FIRST.md)
- Brief sample: [docs/portfolio/WITNESS_OBSERVER_BRIEF_SAMPLE.md](portfolio/WITNESS_OBSERVER_BRIEF_SAMPLE.md) (외부용 abridged)
- Visual appendix: [docs/portfolio/WITNESS_VISUAL_EXPERIMENT_APPENDIX.md](portfolio/WITNESS_VISUAL_EXPERIMENT_APPENDIX.md)
- 5분 데모 (portfolio 변형): [docs/portfolio/WITNESS_5MIN_DEMO_SCRIPT_TEXT_FIRST.md](portfolio/WITNESS_5MIN_DEMO_SCRIPT_TEXT_FIRST.md)
- Resume bullets (final): [docs/portfolio/WITNESS_RESUME_BULLETS_FINAL.md](portfolio/WITNESS_RESUME_BULLETS_FINAL.md)

**Phase 14 (deferred — design-only)**:
- Visual 재도전 prerequisite 4개의 *설계만*: [docs/visual/ENGINE_EVENT_LOG_ADAPTER_DESIGN_NOTES.md](visual/ENGINE_EVENT_LOG_ADAPTER_DESIGN_NOTES.md)
- 구현 0, visual freeze 유지. 미래 cycle이 visual 재개를 *제안*할 때 design space를 미리 제약하는 가드레일 문서.

**Iter 2-3 자체 cycle (유지보수)**:
- Iter 2 (2026-05-06): brief builder generalization lock-in (alt anchor에도 작동) + cross-doc drift patch (1,897/1,913 → 1,922 numbers, 18→19 report tests)
- Iter 3 (2026-05-06): README/DESIGN text-first banner + Phase 14 design notes + lessons L46-L55 cluster summary

---

## 2. 메서드 / 원칙

| 파일 | 역할 |
|---|---|
| [docs/HARNESS.md](HARNESS.md) | H1-H8 anti-bias engineering |
| [docs/ODD_PROTOCOL.md](ODD_PROTOCOL.md) | Overview-Design-Details 방법론 |
| [docs/ARCHIVE_POLICY.md](ARCHIVE_POLICY.md) | 작업 영역 vs archive 운영 규칙 |
| [docs/REPORT_TEMPLATE.md](REPORT_TEMPLATE.md) | 보고서 템플릿 |

---

## 3. Visual Layer (전체 freeze, 2026-05-06)

> **Freeze 결정**: [docs/visual/VISUAL_TRACK_FREEZE_DECISION.md](visual/VISUAL_TRACK_FREEZE_DECISION.md)
> Visual track 5 sub-tracks 모두 frozen — experiment record로 보존, 메인 산출물 아님.
> 메인 산출물은 §1.1 Text-first Observer Brief.



### 3.1 운영 + 검증
- [docs/visual/VISUAL_EXPLORER_V0_1_OPERATING_GUIDE.md](visual/VISUAL_EXPLORER_V0_1_OPERATING_GUIDE.md) — **운영 매뉴얼** (필독)
- [docs/visual/VISUAL_EXPLORER_V0_1_SMOKE_TEST.md](visual/VISUAL_EXPLORER_V0_1_SMOKE_TEST.md) — 자동 검증 8/8 PASS

### 3.2 종합 review
- [docs/visual/VISUAL_TRACK_SYNTHESIS_REVIEW.md](visual/VISUAL_TRACK_SYNTHESIS_REVIEW.md) — 4 단계 누적 종합 (Case V-A)

### 3.3 검증 레코드 (anchor / cross-seed)
- [docs/visual/CROSS_SEED_VISUAL_VALIDATION.md](visual/CROSS_SEED_VISUAL_VALIDATION.md) — Case CS-A (REC 3 / PARTIAL 1 / SAT 1)
- [docs/visual/ANCHOR_3_VISUAL_VALIDATION.md](visual/ANCHOR_3_VISUAL_VALIDATION.md) — vangogh sacred (Case A3-A)

### 3.4 Browsing 가이드
- [docs/visual/OBSERVER_BASED_BROWSING_PACK_V1.md](visual/OBSERVER_BASED_BROWSING_PACK_V1.md) — 3 anchor 통합 browsing

### 3.5 Schema
- [docs/visual/VISUAL_OBSERVER_INPUT_SCHEMA.md](visual/VISUAL_OBSERVER_INPUT_SCHEMA.md) — JSON schema v1

### 3.6 Pixel visual track (2026-05-02 현재)

> **Pixel track 진화**: World map (PW-S1-B → PW-S2-C) 실패 → Scene Director Static (PW-SC-B freeze) → **Pixel Event Playback (PEP) MVP** (현 active 트랙). *정적 → 짧은 사건 재생*.

**WFO v0 진입점 (WFO-A 확정, 100% source-backed) — 신규 트랙**:
- [docs/visual/WORLD_FLOW_TRACEABILITY_AUDIT.md](visual/WORLD_FLOW_TRACEABILITY_AUDIT.md) — **WFO 감사 결과: WFO-A** (100% source-backed, 0 staged)
- [data/visual/world_flow_traceability_report.json](../data/visual/world_flow_traceability_report.json) — `world_flow_traceability_report_v1`
- [data/visual/world_flow_events.json](../data/visual/world_flow_events.json) — `world_flow_events_v1` IR, **windows mode** (13 actors / 3 windows / 146 visual_actions)
- [data/visual/world_flow_events_long.json](../data/visual/world_flow_events_long.json) — `world_flow_events_v1` IR, **long-form mode** (13 actors / 1 window / 200 ticks / 768 visual_actions, WFO-A)
- builder: `scripts/visual/build_world_flow_events.py` (Engine Event Log Adapter, `--mode windows|long_form`)
- audit: `scripts/visual/audit_world_flow_traceability.py`
- spec: [docs/visual/WORLD_FLOW_OBSERVER_SPEC.md](visual/WORLD_FLOW_OBSERVER_SPEC.md)
- inventory: [docs/visual/WORLD_FLOW_SOURCE_INVENTORY.md](visual/WORLD_FLOW_SOURCE_INVENTORY.md)
- tests: `tests/test_visual/test_world_flow_events.py` (29 tests = 23 windows + 6 long-form)
- spec history: [WITNESS_ENGINE_EVENT_LOG_ADAPTER_PLAN.md](WITNESS_ENGINE_EVENT_LOG_ADAPTER_PLAN.md) (Lee directive)

**WFO Polished Viewer (2026-05-06, last-mile presentation)**:
- 실행: [visual/world_flow_observer.html](../visual/world_flow_observer.html) — Canvas 800×500, 200-tick long-form, 60 s default playback
- spec: [docs/visual/WORLD_FLOW_OBSERVER_VIEWER_SPEC.md](visual/WORLD_FLOW_OBSERVER_VIEWER_SPEC.md) — visual grammar / event vocabulary / anti-pattern guarantees
- 8-event glyph vocabulary (× ! ▼ ○ 〜 ↘ ✦ ·) + state cross-fade + group breathing + mood tint
- *No metadata in field of view* — designed for 5-second "this simulation runs" test, not for debugging

> **WFO-A 의미**: WFO v0는 source-backed 100% (PEP의 72.1%보다 +27.9pp). 모든 visual_action이 observer per-tick deltas (source_derived 41.1%) 또는 signal-based 추론 규칙 (source_inferred 58.9%)으로 derive됨. staged_only 0개. 이는 *visual layer = engine/observer translation* claim을 정직하게 뒷받침.

**PEP 진입점 (frozen as VT-B)**:
- [docs/visual/VISUAL_TRACEABILITY_AUDIT.md](visual/VISUAL_TRACEABILITY_AUDIT.md) — **WVT 감사 결과: VT-B** (72.1% source-backed / 27.9% staged)
- [data/visual/visual_traceability_report.json](../data/visual/visual_traceability_report.json) — machine-readable report (`visual_traceability_report_v1`)
- 실행: [visual/pixel_event_playback.html](../visual/pixel_event_playback.html) — **Korean Observer Mode + Trace Mode** (1105 lines)
- 데이터: `data/visual/event_playbacks.json` (`event_playback_v1` + `source_trace` + per-event `source`)
- builder: `scripts/visual/build_event_playbacks.py` (`make_source_trace`, `src_derived/inferred/staged` helpers)
- validator: `scripts/visual/validate_event_playbacks.py` (KEY ≤ 4500ms + source class/conf/kind/mapping + `compute_vt_case`)
- **audit**: `scripts/visual/audit_visual_traceability.py` (JSON + Markdown report generator)
- grammar: [docs/visual/PIXEL_EVENT_PLAYBACK_GRAMMAR.md](visual/PIXEL_EVENT_PLAYBACK_GRAMMAR.md) §1-§14
- tests: `tests/test_visual/test_event_playbacks.py` (25 tests, 0.31s — 16 timing/grammar + 9 WVT)
- spec history: [WITNESS_PIXEL_EVENT_PLAYBACK_PLAN.md](WITNESS_PIXEL_EVENT_PLAYBACK_PLAN.md) → [WITNESS_PEP_WIDE_NEXT_WORK_PLAN.md](WITNESS_PEP_WIDE_NEXT_WORK_PLAN.md) → [WITNESS_PEP_NEXT_WIDE_DIRECTIVE.md](WITNESS_PEP_NEXT_WIDE_DIRECTIVE.md) → [WITNESS_WORLD_TO_VISUAL_TRACEABILITY_PLAN.md](WITNESS_WORLD_TO_VISUAL_TRACEABILITY_PLAN.md) (현 directive)

**VT-B 의미**: PEP는 partially-traceable. 핵심 사건(confession/forgiveness/fear/kneel)은 source_derived, salient agents source_derived. 단, 27.9%는 staged_only (crowd 위치, 일부 movement). PEP는 *staged prototype*으로 freeze. 다음은 **Engine Event Log Adapter → World Flow Timeline → Persistent Actor State → Pixel World Flow Observer** 설계 (별도 directive 시).

**Frozen (보존, 수정 금지)**:
- [docs/visual/PIXEL_SCENE_DIRECTOR_REVIEW.md](visual/PIXEL_SCENE_DIRECTOR_REVIEW.md) §12 — PW-SC-B freeze + 실패 이유 ("static image cannot communicate interaction/flow clearly enough")
- `visual/pixel_scene.html` (PSD-LC1, "static summary artifact"로 보존)
- `scripts/visual/build_scene_beats.py`, `data/visual/scene_beats.json`
- `tests/test_visual/test_scene_director.py` (18 unit tests)

**진화 history (시간순)**:
- [PIXEL_WORLD_OBSERVER_REDIRECTION.md](visual/PIXEL_WORLD_OBSERVER_REDIRECTION.md) — Pixel track 시작 (도트 → 8-bit world map)
- [PIXEL_WORLD_ASSET_DECISION.md](visual/PIXEL_WORLD_ASSET_DECISION.md) — Inline Canvas primitive 선택
- [PIXEL_WORLD_5_SECOND_TEST.md](visual/PIXEL_WORLD_5_SECOND_TEST.md) — S1 verdict (PW-S1-B)
- [PIXEL_WORLD_STATIC_PATCH_REVIEW.md](visual/PIXEL_WORLD_STATIC_PATCH_REVIEW.md) — S2 patch + verdict (**PW-S2-C**)
- [PIXEL_SCENE_DIRECTOR_REDIRECTION.md](visual/PIXEL_SCENE_DIRECTOR_REDIRECTION.md) — 어휘 patch 포기, 구성 차원 재정의
- [PIXEL_SCENE_DIRECTOR_REVIEW.md](visual/PIXEL_SCENE_DIRECTOR_REVIEW.md) — PSD MVP + LC1 + **PW-SC-B freeze**
- [WITNESS_PIXEL_EVENT_PLAYBACK_PLAN.md](WITNESS_PIXEL_EVENT_PLAYBACK_PLAN.md) — *medium pivot* (정적 → 사건 재생)
- [PIXEL_EVENT_PLAYBACK_REVIEW.md](visual/PIXEL_EVENT_PLAYBACK_REVIEW.md) — **현 active 진입점**

**보류 상태**:
- `visual/pixel_world_static.html` (PW-S2-C 후 보류, world map 어휘 자체 실패)

**관련 lessons**:
- L46-L48 [lessons.md](../lessons.md): 어휘 patch ≠ 구성 fix / 직역 → dashboard 번역 → scene / cue는 결과의 그림자

→ Phase 1-7 *중간 plan / intermediate review*는 [archive/visual_phases_intermediate/](archive/visual_phases_intermediate/) 참조.

---

## 4. Demo Package (5분 시연)

| 파일 | 역할 |
|---|---|
| [docs/demo/INTERNAL_DEMO_PACKAGE_V1.md](demo/INTERNAL_DEMO_PACKAGE_V1.md) | 12 sections — 목적/대상/실행/3 화면 |
| [docs/demo/DEMO_SCRIPT_V1.md](demo/DEMO_SCRIPT_V1.md) | 5분 대본 + FAQ + cheat sheet |
| [docs/demo/DEMO_RUN_CHECKLIST_V1.md](demo/DEMO_RUN_CHECKLIST_V1.md) | 시연 5-10분 전 점검 |
| [docs/demo/KNOWN_LIMITATIONS_V1.md](demo/KNOWN_LIMITATIONS_V1.md) | 9 한계 + 강점 |
| [docs/demo/INTERNAL_DEMO_PACKAGE_REVIEW.md](demo/INTERNAL_DEMO_PACKAGE_REVIEW.md) | Phase 6 review (Case D-A) |

---

## 5. Observer Layer (Pipeline + Curation)

### 5.1 Spec
- [docs/observer/WORLD_OBSERVER_LAYER_SPEC.md](observer/WORLD_OBSERVER_LAYER_SPEC.md) — O1-O7 base
- [docs/observer/OBSERVER_TO_STORY_PIPELINE.md](observer/OBSERVER_TO_STORY_PIPELINE.md) — P1-P5
- [docs/observer/CANDIDATE_CURATION_PLAN.md](observer/CANDIDATE_CURATION_PLAN.md) — Q1-Q4

### 5.2 Validation
- [docs/observer/CANDIDATE_CURATION_VALIDATION.md](observer/CANDIDATE_CURATION_VALIDATION.md) — Case A
- [docs/observer/OBSERVER_TO_STORY_VALIDATION.md](observer/OBSERVER_TO_STORY_VALIDATION.md) — Case A
- [docs/observer/OBSERVER_TO_STORY_REVIEW.md](observer/OBSERVER_TO_STORY_REVIEW.md) — Keep/Weak/Missing
- [docs/observer/REAL_RUN_VALIDATION.md](observer/REAL_RUN_VALIDATION.md) + [REVIEW_SUMMARY.md](observer/REAL_RUN_REVIEW_SUMMARY.md)

### 5.3 Plan
- [docs/observer/ANCHOR_2_EXPANSION_PLAN.md](observer/ANCHOR_2_EXPANSION_PLAN.md) — Step 1 next plan

---

## 6. Roadmap / Decision

| 파일 | 역할 |
|---|---|
| [docs/roadmap/WITNESS_FORK_DECISION.md](roadmap/WITNESS_FORK_DECISION.md) | **Phase 7 — Case F-A** (Visual Explorer 중심 v0.2) |

---

## 7. Creative / Story track (currently freeze)

### 7.1 Renderer 결과 (Cycle 1-7 종합)
- [docs/creative/RENDERER_CYCLES_1_TO_6_RETROSPECTIVE.md](creative/RENDERER_CYCLES_1_TO_6_RETROSPECTIVE.md) — Cycle 1-6 종합
- [docs/creative/RENDERER_FREEZE_DECISION.md](creative/RENDERER_FREEZE_DECISION.md) — Cycle 7 freeze 결정

### 7.2 Asset Pack v1
- [docs/creative/CREATIVE_ASSET_PACK_V1_PLAN.md](creative/CREATIVE_ASSET_PACK_V1_PLAN.md) — plan
- [docs/creative/asset_pack_v1/](creative/asset_pack_v1/) — 4 narratives + caveat appendix

### 7.3 Anchor library
- [docs/creative/CURATED_ANCHOR_SET_ALPHA.md](creative/CURATED_ANCHOR_SET_ALPHA.md)
- [docs/creative/J_BETA_PROGRESS.md](creative/J_BETA_PROGRESS.md)
- [docs/creative/PETER_5_VARIATION_COMPARISON.md](creative/PETER_5_VARIATION_COMPARISON.md)
- [docs/creative/PETER_TWO_ANCHOR_COMPARISON.md](creative/PETER_TWO_ANCHOR_COMPARISON.md)
- [docs/creative/NOVEL_TONE_GUIDE_ALPHA.md](creative/NOVEL_TONE_GUIDE_ALPHA.md)
- [docs/creative/VARIATION_READING_REVIEW.md](creative/VARIATION_READING_REVIEW.md)

### 7.4 Decision
- [docs/creative/TEXT_VISUAL_ROLE_REASSESSMENT.md](creative/TEXT_VISUAL_ROLE_REASSESSMENT.md) — **Phase 5 (Case TV-A)**

→ Renderer Cycle 2-7 plans + intermediate diagnostics는 [archive/renderer_cycles_2026-04/](archive/renderer_cycles_2026-04/).

### 7.5 Sample outputs
- [docs/creative/renderer_gate1_v3_samples.md](creative/renderer_gate1_v3_samples.md) ~ v8
- [docs/creative/renderer_gate1_v4_samples.md](creative/renderer_gate1_v4_samples.md)

---

## 8. Story Output Layer (template-guided narrative MVP)

| 파일 | 역할 |
|---|---|
| [docs/story/STORY_OUTPUT_SPEC.md](story/STORY_OUTPUT_SPEC.md) | 사양 + forbidden phrases |
| [docs/story/STORY_MVP_ACCEPTANCE_v2.md](story/STORY_MVP_ACCEPTANCE_v2.md) | 6/6 PASS verdict |
| [docs/story/STORY_BRANCH_C_INTEGRATION.md](story/STORY_BRANCH_C_INTEGRATION.md) | Branch C × Story 연결 |
| [docs/story/STORY_HIGHLIGHTS.md](story/STORY_HIGHLIGHTS.md) | 6 큐레이션 케이스 |
| [docs/story/generated/](story/generated/) | 96 .txt files (12 baseline + 36 Branch C × 2 forms) |

---

## 9. 컨셉 설계 (저레벨 reference)

| 파일 | 역할 |
|---|---|
| [docs/witness_concept_variables_v2.md](witness_concept_variables_v2.md) | Concept variable 정의 |
| [docs/witness_concept_interactions.md](witness_concept_interactions.md) | 변수 상호작용 |
| [docs/witness_action_to_event_mapping.md](witness_action_to_event_mapping.md) | Action ↔ Event 매핑 |
| [docs/witness_discovery_definitions.md](witness_discovery_definitions.md) | 발견 정의 |
| [docs/witness_event_pressure_table.md](witness_event_pressure_table.md) | Event-pressure table |
| [docs/witness_pressure_calculations.md](witness_pressure_calculations.md) | Pressure 계산 |
| [docs/witness_pressure_field_design.md](witness_pressure_field_design.md) | Pressure field 설계 |
| [docs/witness_migration_v3.md](witness_migration_v3.md) | v3 migration 노트 |
| [docs/witness_rubric_design.md](witness_rubric_design.md) | Rubric 설계 |

---

## 10. Spec / Research 폴더 (v0.7+)

### 10.1 Specs
- [docs/specs/](specs/) — 17 specs (DESIGN_LATENT_DRIVE, TRACE_SCHEMA, V3_REDESIGN, V3_PHASE2_V2_*, WORLD_DESIGN*, WORLD_SPIKE_*, SPIKE_6_*)

### 10.2 Research
- [docs/research/RESEARCH.md](research/RESEARCH.md) — 발견 요약
- [docs/research/PAPER_OUTLINE_V05.md](research/PAPER_OUTLINE_V05.md)
- [docs/research/PAPER_DRAFT_V06.md](research/PAPER_DRAFT_V06.md) — paper working draft
- [docs/research/PROJECT_DIRECTION_v2.md](research/PROJECT_DIRECTION_v2.md)
- [docs/research/ITERATION_CLASSIFICATION.md](research/ITERATION_CLASSIFICATION.md)

### 10.3 Branch direction (Branch C — 1차 evidence)
- [docs/b_direction/BRANCH_C_LOCK_DECISION.md](b_direction/BRANCH_C_LOCK_DECISION.md) — Branch C lock + locked claim
- [docs/b_direction/BRANCH_C_FIRST_EVIDENCE_SUMMARY.md](b_direction/BRANCH_C_FIRST_EVIDENCE_SUMMARY.md) — paper §6.9 evidence
- [docs/b_direction/BRANCH_C_CROSS_SEED_ENSEMBLE_RESULTS.md](b_direction/BRANCH_C_CROSS_SEED_ENSEMBLE_RESULTS.md) — cross-seed evidence
- [docs/b_direction/CLAIM_STATUS_MATRIX.md](b_direction/CLAIM_STATUS_MATRIX.md) — claim 상태 표
- [docs/b_direction/FREEZE_COMPONENTS.md](b_direction/FREEZE_COMPONENTS.md) + `FREEZE_STATE.md` — freeze 결정
- [docs/b_direction/](b_direction/) — 30 .md (concept reference — KERNEL_GAPS / RUBRIC_REDESIGN / WORLD_MEMORY / ARCHETYPE_LIBRARY 등). External send 자료는 archive로 이동.

### 10.4 Person / World 폴더
- [docs/person/](person/) — Peter v3 README + 측정 데이터 (paper_data/v3_measurement/diagnostics/JSON files; V3 phase docs는 archive)
- [docs/world/](world/) — World Engine README + paper_data (Spike 1-5 reviews는 archive)

---

## 11. Archive (역사적 기록)

다음 자료는 *현재 작업 영역 외부*. 의미는 *각 카테고리 representative doc*에 보존됨.

### 11.1 Lee directive files (`archive/lee_directives_2026-04-30/`, 19 files)
**의미 보존**: `docs/SUMMARY_PHASES_1_TO_7.md` + 각 Phase review

이동된 directive (모두 *수행 완료* 상태):
- WITNESS_DOT_VISUAL_OBSERVER_ROADMAP_AND_DIRECTIVE.md
- WITNESS_OBSERVER_TO_STORY_PIPELINE_DIRECTIVE.md
- WITNESS_CANDIDATE_CURATION_AND_NEXT_STEPS.md
- WITNESS_NEXT_STEP_OBSERVER_REAL_RUN_VALIDATION.md
- WITNESS_BRANCH_C_PREP_MASTER_PLAN.md
- WITNESS_CLAUDE_CODE_CONTINUOUS_EXECUTION_DIRECTIVE.md
- WITNESS_CREATIVE_IP_TRACK_IMPROVED_DIRECTIVE.md
- WITNESS_LONG_RANGE_NEXT_ACTIONS_2026-04-29.md
- WITNESS_NEXT_PLAN_AFTER_RENDERER_FREEZE_AND_BRANCHC_GO.md
- WITNESS_NEXT_STEPS_AFTER_AUTONOMOUS_ROUND.md
- WITNESS_POST_TYPE_B_EXTERNAL_GATE_DIRECTIVE.md
- WITNESS_PROJECT_STATUS_2026-04-29.md
- WITNESS_PYTEST_IMPROVEMENT_PLAN.md
- WITNESS_STORY_OUTPUT_MVP_PLAN.md
- WITNESS_STORY_OUTPUT_NEXT_STEPS.md
- WITNESS_WORLD_OBSERVER_LAYER_SPEC.md
- LEE_RENDERER_GATE1_V2_FILLED_RESPONSE.md
- SESSION_SUMMARY_2026-04-28_BRANCH_C_AUTONOMOUS.md
- CREATIVE_TRACK_TRANSITION.md

### 11.2 Visual phase intermediate (`archive/visual_phases_intermediate/`, 13 files)
**의미 보존**: `docs/visual/VISUAL_TRACK_SYNTHESIS_REVIEW.md` + `docs/SUMMARY_PHASES_1_TO_7.md`

이동된 plan / intermediate review:
- VISUAL_OBSERVER_MVP_REVIEW.md (V0-V1)
- VISUAL_OBSERVER_V1_REVIEW.md
- VISUAL_OBSERVER_V2_MINIMAL_PLAN.md / _REVIEW.md
- VISUAL_OBSERVER_V2_USAGE_SCENARIOS.md / _REVIEW.md
- VISUAL_EXPLORER_V0_PLAN.md / _REVIEW.md / _V0_2_REVIEW.md
- ANCHOR_2_VISUAL_VALIDATION_PLAN.md / VALIDATION.md
- ANCHOR_3_SELECTION_NOTE.md
- OBSERVER_BASED_BROWSING_PACK_REVIEW.md

### 11.3 Renderer Cycle plans (`archive/renderer_cycles_2026-04/`, 11 files)
**의미 보존**: `docs/creative/RENDERER_CYCLES_1_TO_6_RETROSPECTIVE.md` + `RENDERER_FREEZE_DECISION.md`

이동된 cycle plans (Cycle 7 freeze 후 historical):
- RENDERER_CYCLE_2_PLAN.md ~ RENDERER_CYCLE_7_PLAN.md (6 cycles)
- RENDERER_DIAGNOSIS_ALPHA.md
- RENDERER_DIAGNOSIS_GATE1_V2.md / _BUNDLE.md
- RENDERER_GATE1_V3_BUNDLE_CYCLE7.md / _RESULTS.md

### 11.4 Person V3 phases (`archive/person_v3_phases/`, 19 files)
**의미 보존**: `engine/person/loop.py` (PersonV3Loop) — Phase 1-H 작업이 코드로 흡수됨

이동된 V3 phase docs (Apr 21-24):
- DATA_PIPELINE_v1.md ~ v2_*.md (6 files — pipeline development)
- V3_PHASE_1_COMPLETE.md ~ V3_PHASE_H_COMPLETE.md (8 files)
- V3_PHASES_1_TO_4_COMPLETE.md / V3_PHASE2_V2_*.md / V3_PHASE5_MEASUREMENT_FIRST.md
- STAGE2_PETER_PROGRESS.md / V3_B2_POLICY_RETUNE.md / V3_DYNAMICS_COMPARISON.md
- V3_REFERENCE_DISTRIBUTION_REPORT.md / V3_RETROSPECTIVE_DISCOVERY_CLASSIFICATION.md / V3_SANITY_CHECK_SUMMARIES.md

### 11.5 World Spike phases (`archive/world_spike_phases/`, 6 files)
**의미 보존**: `engine/world/` — Spike 1-5 작업이 코드로 흡수됨

이동된 spike reviews:
- SPIKE_1_REVIEW.md ~ SPIKE_4_REVIEW.md
- WORLD_SPIKE_5_PART1_PROGRESS.md / PART2_PROGRESS.md

### 11.6 Branch C external send (`archive/branch_c_external_send/`, 10 files)
**의미 보존**: `docs/b_direction/BRANCH_C_LOCK_DECISION.md` (locked claim) + `BRANCH_C_FIRST_EVIDENCE_SUMMARY.md`

이동된 external send 자료 (외부 검증 완료, 결과는 LOCK_DECISION에 흡수):
- BRANCH_C_18_PROBES_BLIND_PACKAGE.md / SEND_BUNDLE.md
- BRANCH_C_GPT55_RESPONSE_RAW.md / RAW_FILLED.md / SEND_CHECKLIST.md
- BRANCH_C_PASS_CRITERIA_CHECKLIST.md / FILLED.md
- CREATIVE_ASSET_PACK_V1_PLAN_DRAFT.md (finalized: docs/creative/CREATIVE_ASSET_PACK_V1_PLAN.md)
- LEE_GATE_2026-04-28_BRANCH_C.md
- SCRIPT_STATUS.md (working note)

### 11.7 기타 archive (이전부터 존재)
- `archive/branch_c_working/` — Branch C 작업 자료
- `archive/full_eval_n12/` — n=12 전체 평가
- `archive/iter_logs/` — Iter 1-184 logs (이미 archive됨)
- `archive/readability_blind/` — readability 1차 자료
- `archive/root_2026-04/` — 4월 다이어트 시점
- `archive/story_progressive_2026-04/` — story track 자료
- `archive/working_notes_2026-04/` — 작업 노트

---

## 12. Recent History (Phase 1-7)

빠른 timeline:

```
2026-04-30 — Phase 1: v0.1 운영 정리 → 성공
2026-04-30 — Phase 2: v0.2 minimal interaction → 성공 (4 features)
2026-04-30 — Phase 3: Multi-anchor → A3-A (vangogh)
2026-04-30 — Phase 4: Browsing Pack v1 → BP-A
2026-04-30 — Phase 5: Text/Visual 역할 → TV-A
2026-04-30 — Phase 6: Internal Demo Package v1 → D-A
2026-04-30 — Phase 7: Long-term Fork Decision → F-A (Visual Explorer 중심 v0.2)
2026-04-30 — 폴더 정리: 43 docs → archive (lee_directives + visual_intermediate + renderer_cycles)
```

세부 내용은 `progress.md` 또는 `docs/SUMMARY_PHASES_1_TO_7.md` 참조.

---

## 13. 한 줄 요약

> **WITNESS docs/ master index — 30분 안에 프로젝트 이해 5 doc, 현재 active layer (Visual + Demo + Observer + Roadmap), 컨셉 reference (witness_*.md), spec / research, archive 명시. 213 .md 파일 → 170 (43 archived) 정리 완료.**

---

**Versioning**: v1 (this index) — 2026-04-30 폴더 정리 후 master index.
