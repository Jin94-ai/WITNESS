# Project Structure

> Witness 디렉토리 상세 트리. 파일별 역할 주석 포함. CLAUDE.md에서 분리 (2026-05-02) — *원칙은 CLAUDE.md, 구조 참조는 여기*.
>
> 간략 버전은 [README.md](../README.md#project-structure)에 있다.

```
Witness/
├── engine/                      # Universal Engine (인물 비종속)
│   ├── core/
│   │   ├── state.py             # AgentState (drive_state v1.0, beliefs v1.1)
│   │   ├── event.py             # ExternalEvent, StateEffect, WeightFormula (+breakdown)
│   │   ├── hazard.py            # HazardFunction, HazardEngine
│   │   ├── trigger.py           # TriggerEngine (+snapshot_conditions for §2.1)
│   │   ├── action.py            # AgentAction, AgentBehaviorProfile
│   │   ├── environment.py       # EnvironmentState
│   │   ├── latent_drive.py      # v1.0 LatentDriveModel + 4 Protocol (identity impls)
│   │   └── world.py             # SimulationConfig
│   ├── rules/                   # 상태 전이 규칙
│   │   ├── base.py              # Rule Protocol, RuleEngine, RuleContext
│   │   ├── physical.py          # 피로, 배고픔, 건강
│   │   ├── emotional.py         # 감정 교차 효과
│   │   ├── social.py            # 관계, 고립
│   │   ├── temporal.py          # 항상성, 일주기
│   │   └── environment.py       # 환경 동적 규칙
│   ├── simulation/
│   │   ├── world.py             # SimulationWorld (다중 에이전트 루프)
│   │   ├── runner.py            # SimulationRunner (단일 에이전트 하위 호환)
│   │   ├── scheduler.py         # AgentScheduler (활성화 순서 관리)
│   │   ├── event_scheduler.py   # 외부/hazard 이벤트 주입
│   │   ├── decision.py          # 확률적 행동 결정
│   │   ├── checkpoint.py        # Hindcasting 검증 (+ActionRecord v0.7 필드)
│   │   ├── batch.py             # N회 앙상블 실행
│   │   ├── analysis.py          # 분포 분석, 민감도
│   │   ├── statistics.py        # CI, Cohen's d, Wilson proportion
│   │   ├── pom.py               # Pattern-Oriented Modeling
│   │   ├── calibration.py       # pyABC 파라미터 보정
│   │   ├── recovery_test.py     # Parameter Recovery Test
│   │   ├── explanation.py       # 인과 설명 카드 생성
│   │   ├── bifurcation.py       # Decision window 탐지 (+smoothing/sig/top_k)
│   │   ├── training_samples.py  # v1.0 Stage 2 학습 샘플 + SampleStatistics
│   │   ├── drive_training.py    # v1.0 Stage 2 학습 파이프라인 (skeleton)
│   │   └── resolution.py        # 동적 해상도
│   ├── rendering/
│   │   ├── scripture.py         # 정경 말씀 로더
│   │   ├── narrator.py          # MultiAgentResult → 내러티브 (v0.5)
│   │   ├── trace_emitter.py     # v0.7 TraceEvent JSONL stream (§2 entries)
│   │   ├── player_view.py       # v0.7 플레이어 시점 필터 (§3.1 정보 비대칭성)
│   │   └── trace_narrator.py    # v0.7 TraceEvent → narrative + narrate_result()
│   ├── observer/                # World Observer Layer (2026-04-30)
│   │   ├── snapshot_schema.py   # 4 Pydantic 모델 (Snapshot/World/Group/Agent)
│   │   ├── recorder.py          # record_snapshot() + SnapshotStream
│   │   ├── core.py              # Observer 클래스 (4 lens API: World/Person/Group/Event)
│   │   ├── salience.py          # 8 tag types + top-N moments/agents
│   │   ├── replay.py            # ReplayCursor + auto_bookmark + window helpers
│   │   ├── adapter.py           # MultiAgentResult → Observer (post-hoc 변환)
│   │   ├── candidate.py         # P1: StoryCandidate + 4 extractor (story/world/person/event)
│   │   └── candidate_curation.py # Q1: 3-bucket (story_ready/observation_only/low_activity_hold) + temporal diversity + near-dup
│   └── io/
│       ├── loader.py            # JSON 로더 (behavior_profile, triggers 포함)
│       └── trajectory.py        # Run-level 경로 데이터셋 저장
│
├── content/
│   ├── universal/               # (v2 2026-05-09) Anchor-agnostic taxonomy
│   │   ├── pressure_taxonomy.json   # 11 pressures (id, plain_label_ko, polarity)
│   │   ├── desire_taxonomy.json     # 8 desires + natural_collisions
│   │   └── conflict_axes.json       # 8 axes + tension_question_ko
│   ├── anchors/                 # (v2) Anchor-specific bindings
│   │   └── peter_scarcity_baseline/
│   │       ├── identity_map.json    # agent_id → archetype + display_name
│   │       ├── binding.json         # raw English → 한국어 (베드로 등) display
│   │       └── audit_blocklist.json # forbidden tokens for this anchor
│   ├── peter/                   # Biography Pack: 베드로
│   ├── judas/                   # Biography Pack: 유다
│   ├── caiaphas/                # Biography Pack: 가야바
│   ├── vangogh/                 # Biography Pack: 반 고흐
│   └── shared/
│       ├── triggers.json        # 다중 에이전트 트리거 정의
│       └── scripture/           # 정경 말씀 JSON
│
├── engine/anchor/               # (v2 2026-05-09) Anchor-specific surface (skeleton 외부)
│   ├── anchor_registry.py       # AnchorRegistry + AnchorBinding (binding.json 로더)
│   └── universal_seed_renderer.py  # UniversalStorySeed + AnchorBinding → 한국어
│
├── engine/observer/             # (v2 추가)
│   ├── universal_story_seed.py  # UniversalStorySeed (anchor-clean dataclass)
│   ├── skeleton_output.py       # FROZEN SkeletonOutput contract v1
│   ├── universal_seed_adapter.py    # (StoryCandidate, StorySeedCard) → UniversalStorySeed
│   ├── genre_rulebook.py + genre_adapter.py + genre_audit.py  # (v2.75/2.8) Rule-based Flesh
│   ├── genre_profile.py + flesh_baseline.py    # (v3.1) seed × profile fit (No-ML weighted score)
│   │                                            # (v3.05) recommend_seed 항상 score_breakdown 채움
│   │                                            #   — axis_match/pressure_overlap/compatibility_score/
│   │                                            #     annotation_score(None for rulebook_only)/mode
│   ├── episode_intensity.py     # (v3.1 cycle 8) episode × profile intensity (Plan §22.2 Target B)
│   ├── adaptation_recommendation.py  # (v3.1 cycle 17) seed → ranked top-K genres (Plan §22.3 Target C, schema adaptation_recommendation_v1)
│   └── ... (기존 모듈들)
│
├── tests/                       # 1845 fast tests / 0 fail (2026-04-30). 3-tier 실행 (README 참조)
│   ├── test_engine/             # 엔진 unit + integration
│   ├── test_peter/              # 베드로 시나리오 (POM, ablation, KS)
│   ├── test_vangogh/            # 반 고흐 시나리오
│   ├── test_talleyrand/         # 3rd scenario (engine universality)
│   ├── test_world/              # World Engine v2.0 Spike 1-5
│   ├── test_world_process/      # Process layers (calendar/economy/politics)
│   ├── test_action/, test_persona/, test_population/, test_rubric/
│   ├── test_story/              # Story Output Layer (119 tests, 2026-04-29)
│   │   ├── test_story_helpers.py        # josa / role plural / variant_pick
│   │   ├── test_extract_story_features.py
│   │   ├── test_build_narrative_ir.py
│   │   ├── test_render_story_ko.py
│   │   └── test_story_golden_outputs.py # semantic golden (P9/P4/P6/P10 representative)
│   └── test_observer/           # World Observer Layer + Pipeline + Curation (212 tests, 2026-04-30)
│       ├── test_snapshot_schema.py
│       ├── test_recorder.py
│       ├── test_core.py             # Observer 4 lens
│       ├── test_salience.py         # 8 tag types
│       ├── test_observer_report.py
│       ├── test_replay.py           # ReplayCursor
│       ├── test_compare_views.py    # multi-stream
│       ├── test_adapter.py          # MultiAgentResult → Observer
│       ├── test_candidate.py        # P1: 4 extractor + StoryCandidate (12 tests)
│       ├── test_candidate_packet.py # P2: 6-field packet + 3 format (13 tests)
│       ├── test_render_candidate_story.py # P3: 3-lens narration (10 tests)
│       ├── test_candidate_curation.py     # Q1: 3-bucket + temporal diversity + near-dup (22 tests)
│       └── test_candidate_packet_v2.py    # Q3: use_mode/strongest_lens/related fields (11 tests)
│
├── data/                        # (v2 2026-05-09 expanded)
│   ├── raw/
│   │   ├── melodrama/           # Phase 1 — 막장 작품 회차 줄거리 코퍼스 (ToS 후 fetch)
│   │   │   └── _selection_log.json
│   │   └── control/             # Phase 1 — 비교군 (잔잔한 가족극 등)
│   │       └── _selection_log.json
│   └── annotated/               # Phase 2 — 정량 특성 벡터 (LLM 합성 후)
│
├── models/                      # (v2 2026-05-09) Phase 3-5 학습 모델 (현재 비어있음)
│   └── .gitkeep                 # mode_classifier_v1 / mode_transformer_v1 등이 들어갈 자리
│
├── scripts/data/                # (v2) Phase 1 — 회차 줄거리 수집 인프라
│   ├── synopsis_schema.py       # EpisodeSynopsis dataclass + validators (network IO 0)
│   └── collect_synopsis.py      # CLI orchestrator (validate / list-candidates)
├── scripts/annotation/          # (v2) Phase 2 — multi-AI 어노테이션
│   ├── prompt_templates.py      # SYSTEM_PROMPT_KO + build_user_prompt_ko + synthesize
│   │                            #   + leveled validation + migrate_deprecated_annotation (v2.5)
│   ├── synthesize_annotations.py    # CLI: N annotations → 단일 합성 벡터 (--migrate-deprecated)
│   ├── annotate_with_llm.py     # CLI: dry-run + fixture mode (--migrate-deprecated)
│   └── sample_for_human_review.py   # CLI: 5% 샘플링 (low_confidence | random_stratified)
├── scripts/skeleton/            # (v2.5) Phase 3 Go gate CLI
│   └── validate_skeleton_phase3.py  # deployed skeleton_output.json → exit 0/1/2 + --lenient/--json
├── scripts/narrative/           # (v2.75 + v3.1) Genre adapter + Flesh Baseline CLIs
│   ├── apply_genre_adapter.py       # SkeletonOutput + genre → GenreAdaptedOutput JSON
│   ├── run_genre_demo.py            # 단일 장르 portfolio demo (HTML / md / audit / json)
│   ├── run_genre_comparison.py      # N개 장르 side-by-side 비교 demo
│   ├── build_genre_profiles.py      # (v3.1) reliability + rulebook → genre_profiles.json
│   ├── run_flesh_baseline.py        # (v3.1) Skeleton + profiles → flesh_baseline_output.json (seed × profile)
│   └── build_flesh_baseline_demo.py # (v3.1) baseline JSON → portfolio HTML/MD demo
├── scripts/data/                # (v3.0 v1.1 신규)
│   ├── normalize_synopsis.py        # raw private → normalized JSONL
│   ├── validate_synopsis_dataset.py # schema + 중복 / 정렬 / 길이 / private 강제
│   ├── build_annotation_inputs.py   # → annotate_episode_synopsis_v1 task (Mode A, instructions_ko 12 feature 정의 inline)
│   └── build_public_safe_dataset.py # synopsis_text 제거 / source_url 제거
├── scripts/annotation/          # (v3.0 v1.1 + v3.1 cycle 8/10)
│   ├── validate_annotation_outputs.py # schema + hallucination check (< 5%)
│   ├── build_feature_matrix.py        # annotation outputs → long-form CSV
│   ├── build_reliability_report.py    # → KEEP/REVISE/DROP 판정 (≥4 KEEP = Phase 3.1 GO)
│   ├── run_episode_intensity.py       # (v3.1 cycle 8) feature_matrix + profiles → episode_intensity_v1 (episode × profile, Plan §22.2 Target B)
│   └── build_episode_intensity_demo.py # (v3.1 cycle 10) intensity → portfolio HTML; --fixture-only flag (cycle 40) → "Fictional fixture-only" banner

├── scripts/narrative/              # (v3.1 cycle 17-19 + cycle 25) Target C + bridge
│   ├── run_adaptation_recommendation.py  # (cycle 18) SkeletonOutput + profiles → adaptation_recommendation_v1 (seed → ranked top-K)
│   ├── build_adaptation_recommendation_demo.py  # (cycle 19) → portfolio HTML/MD (ranked card view + 1순위 분포 bar)
│   └── apply_top_recommendation.py # (cycle 25, Plan §24 Step 2 bridge) modal genre 자동 선택 + apply_genre_adapter delegate

├── scripts/data/                   # (v3.1 cycle 29-31) Phase 3.1 verifier
│   └── verify_phase3_1_acceptance.py # (Plan §29 9 항목 자동 + --md-report, Phase 3.0 verifier 대칭)

├── engine/rubric/                  # (Phase 3.05, 29 cycle) 4-Axis Discovery Candidate Classifier
│   ├── rubric_evaluator.py         # 8-step flowchart (review §2.2 P0: causal gate at Step 3)
│   ├── character_critic.py + canon_critic.py + causal_critic.py + novelty_critic.py + context_break_critic.py + scene_response_critic.py
│   │                                # review §2.3/§2.4/§2.5/§2.6 minimum gate + alignment + soft hard 분리
│   └── 모든 threshold uncalibrated_phase3_placeholder (Phase 5+ 실측 보정 전)

├── scripts/rubric/                 # (Phase 3.05) CLI + adapter + visualization
│   ├── run_rubric.py               # records → RubricReport JSON + markdown (--action-pressure-map flag, --is-all-hardcoded)
│   ├── trace_to_records.py         # demo_v07 trace JSONL → rubric records adapter
│   └── build_ensemble_html.py      # 3 ensembles → portfolio HTML (cross_scenario + multi_agent + multi_seed)
│
├── content/genres/              # (v2.75) Phase 2.75 — Rule-based Flesh MVP rulebooks
│   ├── korean_morning_melodrama/
│   │   ├── rulebook.json        # 한국 아침 막장 드라마 (5 amplifiers / 5 cliffhangers / arc_phrases / flow_role_function_phrases)
│   │   └── audit_blocklist.json # forbidden_event_tokens / dialogue / source imitation
│   └── japanese_quiet_drama/    # 일본 정적 드라마 (반대 톤 — abstraction 증명)
│       ├── rulebook.json
│       └── audit_blocklist.json
│
├── docs/data/                   # (v2)
│   ├── SELECTION_CRITERIA.md    # Phase 1 — 작품 선정 기준 + ToS 안전선
│   └── DATA_CARD_TEMPLATE.md    # 데이터셋 카드 템플릿
├── docs/annotation/             # (v2)
│   └── ANNOTATION_GUIDE.md      # Phase 2 — 7 features (v1.1: leveled 0~5) + multi-AI 합성
├── docs/genres/                 # (v2.75 — TBD; rulebook은 content/genres/, 외부 documentation은 추후)
├── docs/plans/                  # (v2 / v2.5 / v2.75 / v2.8 / v2.9 / v3.0 / v3.1)
│   ├── RFC_TEMPLATE.md          # SkeletonOutput / UniversalStorySeed 변경 시 RFC 양식
│   ├── RFC_UNIVERSAL_STORY_SEED_V1_1.md  # RFC-0001 (approved) — v1 → v1.1
│   ├── VALIDATION_REPORT_2026_05_09_FIXES.md  # Phase 2.5 검증 보고서 (Phase 3 GO)
│   ├── GENRE_ADAPTER_MVP_AUDIT.md     # Phase 2.75 검증 보고서 (Phase 3 GO)
│   ├── GENRE_ADAPTER_POLISH_AUDIT.md  # Phase 2.8 검증 보고서 (6 issue + 12/12 acceptance)
│   ├── PHASE_2_9_PORTFOLIO_FINALIZATION_PLAN.md   # Phase 2.9 audit (5 issue + 11/11 acceptance)
│   ├── PHASE_3_0_DATA_PILOT_PREP.md         # Phase 3.0 진입 준비
│   ├── DATA_SOURCE_CANDIDATE_REVIEW.md       # 후보 source 표 (robots.txt + ToS)
│   ├── PHASE_3_0_APPROVAL_CHECKLIST.md       # 5+2 사용자 승인 체크리스트
│   ├── PHASE_3_0_PIPELINE_OPERATING_GUIDE.md # (v3.0 v1.1) Mode A 9 step 운영 절차
│   ├── PHASE_3_0_DATA_CARD.md                # (v3.0 v1.1) pilot 종료 후 작성 template
│   └── PHASE_3_0_DATA_PILOT_REPORT.md        # (v3.0 v1.1) 최종 검증 보고서 template
├── docs/specs/                  # (v2.9)
│   └── NARRATIVE_SCHEMA_VERSION_MAP.md       # schema_version 관계 (frozen container vs 내부 contract)
├── docs/portfolio/README.md     # (v2.9) Reading order — Main / Evidence / Appendix
├── docs/portfolio/demo_genre/             # (v2.75) korean_morning_melodrama 단일 장르 데모
├── docs/portfolio/demo_genre_japanese/    # (v2.75) japanese_quiet_drama 단일 장르 데모
├── docs/portfolio/demo_genre_comparison/  # (v2.75) 메인 portfolio asset — side-by-side 비교
│
├── tests/test_skeleton/         # (v2 + v3.0/3.1 prep) 217 tests — taxonomy / contract drift / phase1+2 / Phase 3.0 pipeline (22) / Phase 3.1 baseline (26)
├── tests/test_genre/            # (v2.75 + v2.8) 94 tests — rulebook / adapter / audit / demo CLI / comparison / drift / abstraction / Phase 2.8 polish
├── tests/fixtures/annotation_public_safe/  # (v3.0) Mode A fictional fixture — 5 raw + 10 outputs + README
│
├── benchmarks/
│   └── bench_simulation.py      # Peter/VG tick/s + memory 벤치마크
├── .github/workflows/
│   └── ci.yml                   # GitHub Actions (ruff + mypy + pytest fast)
├── CLAUDE.md                    # 행동 강령 (원칙 + HARNESS 요약)
├── DESIGN.md                    # v0.7 설계도 + 6단계 로드맵
├── README.md
├── progress.md                  # 세션 메모리
├── lessons.md                   # 크로스 세션 학습
├── docs/
│   ├── HARNESS.md               # H1-H8 반편향 engineering 상세 + H7 자가감사 8항목
│   ├── PROJECT_STRUCTURE.md     # 이 파일
│   ├── specs/                   # 설계 스펙
│   │   ├── DESIGN_LATENT_DRIVE.md         # v1.0 Latent Drive 설계
│   │   ├── TRACE_SCHEMA.md                # v0.7 trace pipeline 규격
│   │   ├── WITNESS_V3_REDESIGN.md         # v3 재설계
│   │   ├── WITNESS_V3_PHASE2_V2_*.md      # v3 Phase 2 v2 개념/동역학
│   │   ├── WORLD_DESIGN*.md               # v2.0 World Engine 설계
│   │   ├── WORLD_SPIKE_*.md               # Spike 단위 상세
│   │   ├── WITNESS_SPIKE_6_*.md           # Spike 6 (신경망 전환)
│   │   └── SCENARIO_TEMPLATE.md           # 3번째 시나리오 추가 가이드
│   ├── research/                # 연구 궤적
│   │   ├── RESEARCH.md                    # 발견 요약 (통합)
│   │   ├── ITERATION_CLASSIFICATION.md    # 34 iteration Tier 분류
│   │   ├── PAPER_OUTLINE_V05.md           # v0.6 논문 outline
│   │   ├── PAPER_DRAFT_V06.md             # v0.6 논문 draft
│   │   └── PROJECT_DIRECTION_v2.md        # v2 방향
│   ├── person/                  # Peter v3 세션 아티팩트
│   ├── world/                   # World Engine Spike 리뷰
│   ├── sessions/                # 일자별 세션 덤프
│   ├── story/                   # Story Output Layer (한국어 narrative MVP, 2026-04-28)
│   │   ├── STORY_OUTPUT_SPEC.md            # 사양 + forbidden phrases
│   │   ├── STORY_MVP_ACCEPTANCE_v2.md      # 6/6 PASS verdict
│   │   ├── STORY_BRANCH_C_INTEGRATION.md   # Branch C × Story 연결
│   │   ├── STORY_HIGHLIGHTS.md             # 6 큐레이션 케이스
│   │   └── generated/                      # 96 .txt files (12 baseline + 36 Branch C × 2 forms)
│   ├── observer/                # Observer Pipeline + Curation specs (2026-04-30)
│   │   ├── OBSERVER_TO_STORY_PIPELINE.md         # P1-P5 spec
│   │   ├── OBSERVER_TO_STORY_VALIDATION.md       # P5 real-run record
│   │   ├── OBSERVER_TO_STORY_REVIEW.md           # P5 Keep/Weak/Missing
│   │   ├── CANDIDATE_CURATION_PLAN.md            # Q1-Q4 spec
│   │   ├── CANDIDATE_CURATION_VALIDATION.md      # Q4 Case A verdict
│   │   ├── ANCHOR_2_EXPANSION_PLAN.md            # Step 1 next plan
│   │   └── WORLD_OBSERVER_LAYER_SPEC.md          # O1-O7 base spec
│   └── visual/                  # Dot Visual Observer specs + reviews (2026-04-30 V0-V2 + Cross-seed + Explorer v0/v0.1)
│       ├── VISUAL_OBSERVER_INPUT_SCHEMA.md       # Stage 1: JSON schema v1
│       ├── VISUAL_OBSERVER_MVP_REVIEW.md         # V0-V1 5+/6 success
│       ├── VISUAL_OBSERVER_V1_REVIEW.md          # Keep 7 / Weak 6 / Remove 0
│       ├── VISUAL_OBSERVER_V2_MINIMAL_PLAN.md    # 6 후보 (Tier 1-3)
│       ├── VISUAL_OBSERVER_V2_MINIMAL_REVIEW.md  # 4/4 success, regression 0
│       ├── VISUAL_OBSERVER_V2_USAGE_SCENARIOS.md # 3 시나리오 (World/Agent/Candidate-first)
│       ├── VISUAL_OBSERVER_V2_USAGE_REVIEW.md    # Case A 판정
│       ├── ANCHOR_2_VISUAL_VALIDATION_PLAN.md    # peter_scarcity_triple plan
│       ├── ANCHOR_2_VISUAL_VALIDATION.md         # Case A-2 (single-seed limitation)
│       ├── CROSS_SEED_VISUAL_VALIDATION.md       # Case CS-A (REC 3/PARTIAL 1/SAT 1)
│       ├── VISUAL_TRACK_SYNTHESIS_REVIEW.md      # 4 단계 종합 + Case V-A
│       ├── VISUAL_EXPLORER_V0_PLAN.md            # Explorer v0 plan
│       ├── VISUAL_EXPLORER_V0_REVIEW.md          # Explorer v0 (Case EX-A)
│       ├── VISUAL_EXPLORER_V0_1_OPERATING_GUIDE.md # v0.1 operating guide (Phase 1)
│       └── VISUAL_EXPLORER_V0_1_SMOKE_TEST.md    # v0.1 smoke test 8/8 PASS
├── scripts/
│   ├── story/                   # Story output 3-stage pipeline + selector
│   │   ├── extract_story_features.py       # annotated probe → JSON
│   │   ├── build_narrative_ir.py           # JSON → semantic IR
│   │   ├── render_story_ko.py              # IR → 한국어 텍스트
│   │   ├── selector.py                     # J-Alpha+J-Beta anchor library (2026-04-30 moved from engine/story/ for Rule #1)
│   │   ├── generate_anchor_variations.py
│   │   └── generate_trilogy_view.py
│   ├── observer/                # World Observer Layer scripts (2026-04-30)
│   │   ├── observer_report.py              # 4 lens text reports
│   │   ├── compare_views.py                # multi-stream + multi-lens compare
│   │   ├── narrative_summary.py            # narrate_person_arc / event_ripple / world_arc
│   │   ├── candidate_packet.py             # P2: 6-field packet + Q3 v2 (use_mode/strongest_lens/related)
│   │   └── render_candidate_story.py       # P3: 3-lens narration + compare_lenses
│   ├── visual/                  # Dot Visual Observer scripts (2026-04-30 V0-V2 + Cross-seed)
│   │   ├── export_dot_observer_data.py         # V0-V1: Observer snapshot → visual JSON v1 (--anchor / --output)
│   │   └── export_cross_seed_visual_data.py    # Cross-seed: 5 seeds → cross_seed_v1 JSON (별도 schema)
│   └── audit_report.py          # HARNESS H4-H8 자동 검증 + --stories 모드
├── visual/                      # Dot Visual Observer HTML (2026-04-30 V0-V2 + Cross-seed + Explorer v0)
│   ├── explorer.html                       # **Broad navigation entry** (v0): anchor selector + view toggle + candidate panel + packet (Case EX-A)
│   ├── dot_observer_static.html            # 5 representative ticks side-by-side
│   ├── dot_observer_replay.html            # **Single-run deep view**: 200-tick replay + 4 V2 features + ?data= query param
│   └── dot_observer_cross_seed.html        # **Cross-seed deep view**: 5 seeds small multiples (Case CS-A)
├── data/
│   ├── story/                   # Story intermediate JSONs
│   │   ├── story_features/                 # 48 extracted feature files
│   │   └── narrative_ir/                   # 48 IR files
│   └── visual/                  # Visual Observer data (gitignore 권장 — generated)
│       ├── dot_observer_data.json              # V1 canonical run (peter_scarcity_baseline, ~824 KB)
│       ├── dot_observer_data_triple.json       # Anchor 2 (peter_scarcity_triple seed=0, ~824 KB)
│       └── dot_observer_cross_seed_triple.json # Cross-seed (5 seeds × 200 ticks, ~275 KB)
└── examples/                    # Runnable demo entry points
    ├── demo.py                  # v0.5 기본 실행 예시
    ├── demo_v07.py              # v0.7 trace pipeline 데모 (peter/vangogh)
    ├── demo_phased.py           # v1.2 phase-linked arc demo
    ├── demo_story.py            # Story output 단일 entry point (P9 / --highlights)
    ├── demo_creative.py         # Creative IP track J-Alpha+J-Beta (--status / --trilogy / --all-anchors)
    ├── demo_observer.py         # World Observer Layer (--status / --views / --replay / --compare / --narrate / --real)
    └── demo_observer_story.py   # P1-P5 Pipeline + Q1-Q4 Curation (default list / --curated / --packet / --render-story / --compare-lenses)
```

## 파일 의존 관계

```
CLAUDE.md (행동 강령 — 원칙)
    ↓
DESIGN.md (설계도 — 아키텍처, 방법론, 스키마)
    ↓
progress.md (세션 메모리)
    ↓
실제 작업
```
