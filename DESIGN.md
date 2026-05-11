# Witness 설계도 v1.2 (+ Narrative Mode Refactor v2 — 2026-05-10)

> **v2 개편 (2026-05-09 시작 → 2026-05-10 Genre Adapter MVP 추가)**: 결정론적 시뮬레이션 엔진(뼈대) + ML로 학습된 Narrative Mode 변환기(살)의
> 이중 구조. 뼈대는 anchor-agnostic universal seed 출력, 살은 회차별 줄거리 코퍼스 학습 기반 변환.
> Phase 2.75에서 *rule-based Flesh MVP* (Genre Adapter)가 추가되어 ML 진입 전 contract 검증 layer 역할.
> Plans: [docs/witness_narrative_mode_plan.md](docs/witness_narrative_mode_plan.md) +
> [docs/WITNESS_NARRATIVE_MODE_VALIDATION_FIX_PLAN.md](docs/WITNESS_NARRATIVE_MODE_VALIDATION_FIX_PLAN.md) +
> [docs/WITNESS_PHASE_2_75_GENRE_ADAPTER_MVP_PLAN.md](docs/WITNESS_PHASE_2_75_GENRE_ADAPTER_MVP_PLAN.md).
>
> 역사적 인물의 생애를 hazard-driven, multi-agent ensemble simulation으로 수천 회 돌리고
> 결과 분포를 관측하여 "무엇이 갈라지는 순간이었는가"를 발견하는 시스템.
> **궁극 비전**: 플레이어가 역사적 인물의 삶을 체험하며 목격자가 되는 서사 시뮬레이터.

---

## v2 — Skeleton + Flesh 이중 구조 (2026-05-09 ~ 2026-05-10)

```
[Skeleton Engine — 결정론적]
  Layer 1. Engine Core (압력 / 다중 에이전트 / deterministic seed)
  Layer 2. Universal Human Model (pressure / desire / conflict_axes taxonomy)
  Layer 3. Story Seed Mining → UniversalStorySeed v1.1 + EvidenceLedger

       ↓ SkeletonOutput contract (FROZEN v1, RFC-0001 v1.1) ↓

[Flesh Engine — 두 갈래]
  ① Rule-based Flesh MVP (Phase 2.75)
     Layer 4a. GenreRulebook (parametric — JSON 정의)
     Layer 4b. GenreAdapter (structure-only 변환)
     Layer 4c. GenreAudit (forbidden event / dialogue / source imitation)
     → SkeletonOutput v1.1 → GenreAdaptedOutput v1
     → 외부 의존 0, ML 진입 전 contract 검증 layer

  ② ML 학습 (Phase 3-5, 미진입)
     Layer 5a. Narrative Mode Models (Classifier α / Evaluator γ / Transformer β)
     Layer 5b. Mode Application (학습된 mode → 모드화 출력)
     → 외부 의존 (LLM API / 데이터 fetch / GPU)

       ↓

[Portfolio Surface]
  - Universal Skeleton 미리보기 (docs/portfolio/demo/index.html)
  - Genre Adapter 데모 (docs/portfolio/demo_genre/, demo_genre_japanese/)
  - Cross-genre 비교 (docs/portfolio/demo_genre_comparison/)
```

**현재 진행 (2026-05-10)**:
- **Phase 0** (Contract & Skeleton Cleanup): ✅ DONE — `engine/observer/skeleton_output.py::SkeletonOutput` v1 FROZEN, `engine/observer/universal_story_seed.py` v1.1 (RFC-0001), `engine/anchor/` 분리
- **Phase 1** (Data Infra): ✅ INFRA — `docs/data/SELECTION_CRITERIA.md` + `scripts/data/synopsis_schema.py`. 실제 fetch는 ToS 검토 후
- **Phase 2** (Annotation prep): ✅ PREP — `docs/annotation/ANNOTATION_GUIDE.md` v1.1 + `scripts/annotation/prompt_templates.py` (leveled features 0-5 / migrate_deprecated_annotation)
- **Phase 2.5** (Validation Fix): ✅ DONE — UniversalStorySeed v1.1 + lossless adapter (4-tier pressure fallback) + LifeStoryFlow v1.1 (flow_roles auto-build) + AuditTrail v1.1 + `validate_skeleton_phase3.py` CLI / `is_skeleton_phase3_ready` Python helper / `assemble_skeleton_output(strict_axis=True)`. RFC-0001 + [VALIDATION_REPORT_2026_05_09_FIXES.md](docs/plans/VALIDATION_REPORT_2026_05_09_FIXES.md)
- **Phase 2.75** (Genre Adapter MVP): ✅ DONE — `engine/observer/genre_rulebook.py` + `genre_adapter.py` + `genre_audit.py` + `content/genres/{korean_morning_melodrama, japanese_quiet_drama}/` rulebooks. 외부 의존 0. [GENRE_ADAPTER_MVP_AUDIT.md](docs/plans/GENRE_ADAPTER_MVP_AUDIT.md): Phase 3 GO 판정.
- **Phase 2.8** (Genre Adapter Polish): ✅ DONE — structured outline + `genre_lens_ko` + soft `quality_warnings` + `genre_comparison_output_v1` + HTML 정보 위계 개선. 94 신규 genre tests. [GENRE_ADAPTER_POLISH_AUDIT.md](docs/plans/GENRE_ADAPTER_POLISH_AUDIT.md).
- **Phase 2.9** (Portfolio Finalization): ✅ DONE — `demo_genre_comparison`을 portfolio main 확정 / README 정정 (rule-based 현재 / ML Phase 3 후) / [NARRATIVE_SCHEMA_VERSION_MAP.md](docs/specs/NARRATIVE_SCHEMA_VERSION_MAP.md) / [portfolio/README.md](docs/portfolio/README.md) (Main/Evidence/Appendix) / Phase 3.0 prep 3 docs ([PILOT_PREP](docs/plans/PHASE_3_0_DATA_PILOT_PREP.md) + [SOURCE_REVIEW](docs/plans/DATA_SOURCE_CANDIDATE_REVIEW.md) + [APPROVAL_CHECKLIST](docs/plans/PHASE_3_0_APPROVAL_CHECKLIST.md)) / .gitignore에 `data/external_private/` preempt. [PHASE_2_9_PORTFOLIO_FINALIZATION_PLAN.md](docs/plans/PHASE_2_9_PORTFOLIO_FINALIZATION_PLAN.md).
- **Phase 3.0 v1.1** (Data Pipeline + LLM Labeler): ✅ Mode A 코드 파이프라인 + templates + fixture e2e (2 titles × 5 ep, 77 quotes, hallucination 0) — *외부 의존 0으로 작성 완료*. 7 신규 스크립트 (normalize / validate_dataset / build_inputs / build_public_safe / validate_outputs / build_feature_matrix / build_reliability_report) + Operating Guide ([PHASE_3_0_PIPELINE_OPERATING_GUIDE.md](docs/plans/PHASE_3_0_PIPELINE_OPERATING_GUIDE.md)). `instructions_ko` 12 feature 정의 inline. 사용자 승인 5+2건 후 운영 시작.
- **Phase 3.1 prep** (No-ML weighted score, 두 layer baseline): ✅ 모두 학습 0 / fine-tuning 0 / raw text 0:
  - **seed × profile fit** (`engine/observer/flesh_baseline.py` / flesh_baseline_output_v1): compatibility (50%) + annotation (50%) blend. SkeletonOutput seed가 어떤 장르 flesh와 잘 맞는지. demo: [docs/portfolio/demo_flesh_baseline/index.html](docs/portfolio/demo_flesh_baseline/index.html).
  - **episode × profile intensity** (`engine/observer/episode_intensity.py` / episode_intensity_v1, Plan §22.2 Target B): annotator 평균 → KEEP feature × profile.feature_weights 선형 결합. 각 *에피소드*가 장르 시그니처에 부합하는 정도. demo HTML 스크립트 `scripts/annotation/build_episode_intensity_demo.py` (title × genre arc bar chart + per-record feature contribution mini-bars).
  - 5 산출 (build_genre_profiles + run_flesh_baseline + build_flesh_baseline_demo + run_episode_intensity + build_episode_intensity_demo) + 35 tests. 모든 score 설명 가능 (reason_features + feature_contributions breakdown).
- **Phase 3.05 prep 정직성 보강** (2026-05-11): ✅ Step 1+2 (`flesh_baseline.recommend_seed` *항상* score_breakdown 채움 — rulebook_only도 `axis_match/pressure_overlap/compatibility_score/annotation_score=None/mode`; demo HTML+MD에 "Prep mode (rulebook-only)" banner + fit_label 병기) + Step 3+4 (validator `--strict + --synopsis` 강제 exit 2; hallucination report 3 layer 분리 `valid_files_only_summary`/`all_files_summary`/`invalid_files` — threshold = valid 기준) + Step 5+6 (Operating Guide §9 **Deploy Status Matrix** 5 분류 + 5 architectural docs sync). 모든 prep 산출물 *실제 데이터 기반 추천처럼 보이지 않도록* 정직성 강화. 13 신규 phase3 tests / 2,543 fast.
- **Rubric directive (Phase 3.05, 29 cycle)** ✅ 2026-05-11. 4-Axis Discovery **Candidate Classifier** ([docs/witness_rubric_design.md](docs/witness_rubric_design.md) + [WITNESS_V3_RUBRIC_DESIGN_REVIEW.md](docs/WITNESS_V3_RUBRIC_DESIGN_REVIEW.md)). 8-step flowchart (hardcoded → canon hard → **causal gate** → context_break → novelty noise → canonical_reproduction → character_consistent_novel_CANDIDATE / canon_compatible_character_DRIFT). 5 critic 모듈 (`engine/rubric/{character,canon,causal,novelty,context_break,scene_response}_critic.py` + `rubric_evaluator.py`). 3 scripts (`scripts/rubric/{run_rubric,trace_to_records,build_ensemble_html}.py`). 14 fixtures + 12+ portfolio reports (8 trajectory variants + alignment + axis-isolated + ensemble HTML). review §2.1/§2.2/§2.3/§2.4/§2.5/§2.6/§3/§5/§H8 모두 entire validation ✅. 124+ rubric tests. Rule #14 (학습 loss 0) + scalar 합산 0 + 모든 threshold `calibration_status="uncalibrated_phase3_placeholder"` 명시. **review §2.5 P1 extended** (cycle 16/20/22): CausalCritic `action_pressure_map` (optional, engine person-agnostic) → `pressure_action_alignment`. **review §5 discrimination empirical** (cycle 23/26): Phase H 재설계 CharacterCritic 3 axis (relation_stability/identity_retention/recovery_plausibility + minimum gate) — anti-signature fixture로 양방향 + axis-isolated N-case로 *각 axis 독립 trigger* 입증. **L84 generic detector** (cycle 28): `report_to_dict()` walker가 `__dict__` + `@property` 모두 walk — 향후 @property aliases 자동 surface.
- **Phase 3.1 §22.3 Target C — Adaptation Recommendation** ✅ 2026-05-11 cycle 17-19. `engine/observer/adaptation_recommendation.py` (schema `adaptation_recommendation_v1`) + `scripts/narrative/{run_adaptation_recommendation,build_adaptation_recommendation_demo}.py` + portfolio demo `docs/portfolio/demo_adaptation_recommendation/index.html`. Target A의 flat list를 *seed별 grouped + score 내림차순 + top_k*로 재구성. **Plan §24 Step 2 bridge** (cycle 25): `scripts/narrative/apply_top_recommendation.py` — modal genre 자동 선택 + `--genre` override + `apply_genre_adapter.py`에 delegate → SkeletonOutput → recommendation → modal_genre → GenreAdaptedOutput chain 완결. Cross-target invariant (cycle 21): Target A top-1 = Target C 1순위 (동일 `recommend_seed()` 호출).
- **Phase 3.1 §29 Acceptance verifier** ✅ 2026-05-11 cycle 29-31. `scripts/data/verify_phase3_1_acceptance.py` (9 항목 자동: §29.1 PENDING Phase 3.0 dep / §29.2-8 AUTO / §29.9 HEURISTIC) + `--md-report` flag + Operating Guide §4.6 dedicated section. Phase 3.0 verifier 대칭.
- **Target B fixture-only portfolio deploy** ✅ 2026-05-11 cycle 40. `docs/portfolio/demo_episode_intensity/index.html` (10 episodes × 2 genres, `tests/fixtures/annotation_public_safe/` 기반). `--fixture-only` flag → prominent "Fictional fixture-only" banner (HTML CSS + MD blockquote + fixture path 노출). Operating Guide §9 deploy 카테고리: **fixture-only**. Phase 3.0 pilot 진입 후 실제 데이터로 교체 path 명시. → **Target A/B/C 모두 portfolio asset 보유** — Phase 3.1 baseline 시연 완결성.
- **doc-reality automation** (cycle 33-38, 41-42): registry-driven invariant + multi-doc regex link checker. CLAUDE.md / FLESH_BASELINE_DEMO / portfolio README / Operating Guide 4개 doc 모두 자동 검증. 130 internal links across docs/portfolio + docs/plans 0 broken. lessons L86+L87 (doc statements as machine-checkable + registry/regex dual).
- **Phase 3.0 actual run / Phase 3.1 학습**: ⏳ 사용자 승인 5+2건 대기. APPROVAL_CHECKLIST §2.1 12 step 단계별 절차.
- **Phase 6** (통합 데모): ✅ PARTIAL — main `index.html`에 skeleton output 미리보기 + universal_seed_renderer + Phase 2.75 portfolio demo

**Contract governance**: SkeletonOutput / UniversalStorySeed / universal taxonomy 변경 시
[docs/plans/RFC_TEMPLATE.md](docs/plans/RFC_TEMPLATE.md) 따라 RFC 의무 (RFC-0001이 첫 사례). drift guard
test가 `tests/test_skeleton/test_phase2_prep.py`에서 field 이름 + type annotation + default
value + frozen 상태 + tuple/list mutability + schema_version까지 즉시 fail.

**Phase 3 Go Gate** (3 layer 강제):
- 코드: `engine.observer.universal_seed_adapter.is_skeleton_phase3_ready(out) → (bool, errors)`
- CLI: `python scripts/skeleton/validate_skeleton_phase3.py docs/portfolio/demo/skeleton_output.json` (exit 0/1/2)
- 쓰기 시점: `assemble_skeleton_output(..., strict_axis=True)` — unknown axis fail-fast

**Genre Adapter governance**: 새 장르 추가 = `content/genres/{genre_id}/rulebook.json` + `audit_blocklist.json` 작성. engine 변경 0. `tests/test_genre/test_rulebook_drift_guard.py`가 모든 장르 rulebook의 schema 강제.

---

---

## ⚠️ Surface 전환 알림 (2026-05-06~)

이 문서는 *engine + simulation 설계*의 정합한 기록으로 유지된다. **현재 portfolio
메인 산출물은 Narrative Mining Engine 출력** — `Story Thread` + `Narrative Opportunity`
+ HTML 콘솔 — 이다. Visual은 frozen, Text-first Observer Brief는 Narrative Mining의
*입력 layer*로 통합됐다.

| 항목 | 상태 |
|---|---|
| Engine + Observer + Curation 계층 | **active** — 본 문서가 정확한 설계서 |
| **Narrative Mining Layer (신규 메인, Phase 1-5)** | [engine/observer/moment.py](engine/observer/moment.py) / [thread.py](engine/observer/thread.py) / [narrative_opportunity.py](engine/observer/narrative_opportunity.py) → [docs/portfolio/NARRATIVE_OPPORTUNITIES.md](docs/portfolio/NARRATIVE_OPPORTUNITIES.md) + [console.html](docs/portfolio/narrative_mining_console.html) |
| Reporting Layer (Phase 11-12, 입력 surface) | [scripts/report/](scripts/report/) → brief + provenance table (narrative mining 입력에도 사용) |
| Story Output Layer (v1.3 한국어 narrative) | active in code, *non-main-artifact* (story renderer 회귀 금지) |
| Visual Layer (PSD / PEP / WFO) | **전체 freeze** ([VISUAL_TRACK_FREEZE_DECISION.md](docs/visual/VISUAL_TRACK_FREEZE_DECISION.md)) |

전환 사유:
1. PEP cutscene playback 27.9% staged-only / WFO Polished Viewer 5초 테스트 fail → visual freeze
2. 단일 brief는 *후보 감지*에 강하지만 *서사 축적*을 못 보여줌 → Narrative Mining 추가
3. Audit 방법론(`source_derived` / `source_inferred` / `not_used`)은 visual track에서 발명되어 brief, provenance table, narrative mining의 모든 layer에 transfer

> **현 active plan**: [WITNESS_NARRATIVE_MINING_PLAN.md](docs/WITNESS_NARRATIVE_MINING_PLAN.md)
> **이전 plan (보존)**: [WITNESS_PROJECT_RESET_AND_TEXT_FIRST_PLAN.md](docs/WITNESS_PROJECT_RESET_AND_TEXT_FIRST_PLAN.md)
> **Lessons cluster**: L46–L55 (visual track 회고), L56 (narrative mining 도입)

본 문서의 §1–§N 엔진 설계 내용은 무수정으로 보존한다. Visual layer 관련 기획(§11 등)은 *appendix-only*로 읽어야 한다 — 새 산출물 트리거가 아님.

---

## 0. 문서 이력

- v0.1: 일반 역사 인물 시뮬레이터의 추상 설계
- v0.2.1: 베드로 MVP 구체 설계 (선형 내러티브 리더 전제)
- v0.3: hazard-driven ensemble simulator로 전환
- v0.4: EnvironmentState 통합 + ablation 검증
- v0.5: POM/PRIM/pyABC Model Selection/shapiq 4단계 검증 완료
- v0.6: M1-Multi 다중 에이전트 시뮬레이션 완료
- **v0.7: 5차 LLM 리뷰 기반 로드맵 재정립** (이 문서) — v1.0 학습 엔진 전환 경로 수립

---

## 0.5. v0.7 → v1.0+ 로드맵 (5차 리뷰 통합)

### 버전 단계

| 버전 | 핵심 변화 | 기간 |
|------|----------|------|
| v0.5 | Rule-based symbolic simulator + 검증 프레임워크 | 완료 (봉인) |
| v0.7 | Trace pipeline + player view + drive hooks + content-driven narrative | 완료 |
| **v1.2 (현재)** | **Phase-linked continuous life architecture (베드로 공생애 3년)** | **5 Phase E2E + phase별 canonical events + absolute time + slow recovery rule** |
| **Branch C 1차** | **World-layer configuration sensitivity (S2/S3/S4/S5 + cross-seed walkback)** | **완료 — 36 probes + 240 runs, paper §6.9 + Appendix G** |
| **Story Output MVP** | **annotated probe → 한국어 narrative renderer (3-stage pipeline)** | **완료 — 6/6 PASS, 48 stories, paper §6.10 + Appendix H** |
| **J-Alpha (Creative IP 1차 증명)** | **같은 anchor 5 seeds → 다른 한국어 이야기 5편 가설 검증** | **부분 성공 — Peter 5/6 PASS, Van Gogh→sacred 1/6 FAIL.** Gate 2 = A (PASS) 응답 → J-Beta 진행 |
| **J-Beta (Creative IP 확장)** | **Selector queryable library + Scarcity Trilogy + Cross-scenario REC differentiation** | **진행 중 — 5 anchors, scarcity trilogy nonmonotonic IP narrative beat (1/2/3 accusations → SAT/SAT/REC), Gate 1 자율 cycle 1+2+3 완료** |
| v0.6/v1.0 paper | 논문 마감본 — 34 iteration → 핵심 narrative 축약 + 용어 교정 | 1-2개월 |
| v1.0 Stage 2 | Predictive Latent Drive Bottleneck — PyTorch encoder 실제 구현 | 3-4개월 |
| v1.1 | Relational Graph Extension (node drive + edge tension) | 2-3개월 |
| v1.3 | Weak Preference Inference (classical IRL 아닌 mixture) | 2-3개월 |
| v2.0 | Narrative Witness Layer (Story Output MVP → 인터랙티브 player view) | 지속 |

### v1.2 Phase-linked Life Architecture (2026-04-19, GPT+Gemini 리뷰 반영)

**범위**: 베드로 공생애 3년 — 소명(Luke 5) → 갈릴리 사역 → 고백+변화산 → 예루살렘 여정 → 수난(기존 500 tick legacy).

**5 Phase 구조**:
| Phase | 기간 | tick scale | 핵심 이벤트 |
|-------|------|-----------|-------------|
| 01 소명 (Call) | ~1주 (84 tick) | 2h/tick (dense) | Luke 5 기적 어획 → 소명 수락 |
| 02 갈릴리 사역 (Galilean) | ~18개월 (540 tick) | 24h/tick (sparse, dense subwindow) | 12 사도, 오병이어, 물 위 걸음(dense 230-234), 사천명 |
| 03 고백+변화산 (Confession) | ~1.5주 (150 tick) | 2h/tick (dense) | 가이사랴 빌립보 고백 → 사탄 책망 → 변화산 → 수난예고 |
| 04 예루살렘 여정 (Journey) | ~3개월 (90 tick) | 24h/tick | 3차 수난예고, 지위 논쟁, 유다 공모, 베다니 향유 |
| 05 수난 (Passion) | 42일 (500 tick) | 2h/tick | 기존 v0.7 scenario (legacy mode 유지) |

**아키텍처 구성요소**:
- `engine/core/phase.py`: `Phase`, `PhaseExitCondition`, `PhaseHandoffSpec`, `FieldMapping`
- `engine/simulation/phased_world.py`: `PhasedSimulationWorld`, `apply_handoff`, `PhasedMultiAgentResult` — Phase별 `canonical_events_path` 자동 로드 (Iter 20)
- `engine/simulation/time_axis.py` (Iter 22): `ticks_to_absolute_hours`, `extract_field_trajectory_absolute`, `convert_phase_boundaries_to_hours` — phase-variable tick을 "arc 시작 후 hours" 좌표계로 재표현.
- `engine/rules/base.py`: `RuleContext.dt_hours` (phase-variable 호환)
- `engine/rules/inhibitor.py`: `FieldAttenuationRule`, `FieldAmplificationRule` (generic, content-configurable)
- `engine/rules/slow_recovery.py` (Iter 23): `SlowStateFieldRecoveryRule` — field별 opt-in 회복 (moral_injury + trust_scar + identity_shift; event_trauma는 PTSD 원칙으로 자연 회복 없음). 기본 rate=0 zero-effect.
- `engine/core/world.py`: `SimulationConfig.phases` + `tick_scale_hours`
- `engine/core/state.py`: `EmotionalState.awe` 필드 추가

**Content**:
- `content/peter/phases/{01_calling, 02_galilean, 03_confession, 04_journey_to_jerusalem}/` 각각 `phase_config.json` + `canonical_events.json` + `handoff_to_next.json`
- `content/shared/scripture/luke_5.json` (개역개정 소명 본문)
- `content/peter/initial_state_calling.json` (어부 시점 초기값)

**reviewer 피드백 반영**:
- "단일 연속 시뮬레이터"가 아닌 **"phase-linked continuous life architecture"** (표면 연속, 내부 stitched)
- 모든 rule dt-aware (hazard만이 아닌 RuleContext 전체)
- Legacy mode 완전 보존 (phases=None = 기존 v0.7 동작, arrest tick 152-211 유지)
- slow_state irreversible carry-forward + explicit field mapping
- canonical intervention = reparameterization shock (완전 회복 아님)
- Phase 2 "국지적 dense window" (물 위 걸음 등 연속 tick dense 표현)
- Inhibitor Rule 스켈레톤 (Gemini 지적: 유다 조기 배반 방지 기전)

**v1.2 완성 체크리스트** (Iter 20-37 이후):
- [x] Phase-linked life architecture (Phase dataclass + handoff + PhasedSimulationWorld, Iter 1-18).
- [x] Slow state field-specific recovery (`SlowStateFieldRecoveryRule`, Iter 23, opt-in zero-default).
- [x] 전체 아크 E2E run (Iter 18, 5 phase + Iter 32 Phase 5 linked-life).
- [x] Absolute time 기반 분석 메트릭 재정의 (`time_axis.py`, Iter 22).
- [x] Phase-aware 분석 demo script (`examples/demo_phased.py`, Iter 28).
- [x] 외부 리뷰어 질문 6개 최종 응답 (`REVIEW_RESPONSE_V1_2.md`, Iter 29).
- [x] Inhibitor Rule content-level deployment (Iter 31, Judas disillusionment 감쇄 6 tests).
- [x] Hazard `base_rate_unit` per_hour 옵션 (Iter 27, legacy-safe opt-in).
- [x] Engine-neutrality 증명 (Iter 34, Van Gogh through PhasedSimulationWorld).
- [x] POM-style ensemble emergent 패턴 검증 (Iter 30, 10 seed × 4 phase).
- [x] time_axis + inhibitor 100% coverage (Iter 36), phased_world 97%+ (Iter 37).

**여전히 가능한 확장**:
- Phase 4 → Phase 5 handoff가 legacy 수치를 override하는 linked-life full-length (500 tick) 실제 검증.
- v0.6 paper 섹션에 v1.2 스트럭처 추가 (필요 시).

### v0.7 완료 사항 (current as of 2026-04-19)

- Trace Schema §2 entry 5종 end-to-end (action_taken, trigger_fired, belief_update, bifurcation_point, canonical_match)
- `engine/rendering/trace_emitter.py` + `player_view.py` + `trace_narrator.py`
- `narrate_result()` one-call helper
- `AgentAction.visible_signal` + `observable_from` content-driven 정보 비대칭성 (전 7 content pack 22 actions)
- `engine/simulation/bifurcation.py` (smoothing + significance + top_k)
- `engine/simulation/training_samples.py` + `drive_training.py` (Stage 2 skeleton + SampleStatistics diagnostic)
- `engine/core/latent_drive.py` (4 Protocol + Identity impls)
- CI workflow (ruff + mypy + pytest + coverage artifact) + benchmark script (Peter 1001 tick/s, VG 1267 tick/s baseline)
- `examples/demo_v07.py --scenario peter|vangogh` — end-to-end pipeline 데모
- **1845 fast tests / archived / 97%+ coverage** (time_axis / slow_recovery / inhibitor 100%)
- v0.6 paper working draft (`docs/research/PAPER_DRAFT_V06.md`, 319 lines, §1–§9 + Appendix A/B/C + References)

### 핵심 설계 원칙 (v1.0+)

1. **기존 symbolic event engine 유지**: trigger/hazard/rule은 버리지 않음
2. **학습층은 그 위에 얹음**: latent drive state가 action weight + trigger susceptibility 조절
3. **3~8차원 latent drive**: attachment, self-preservation, shame, calling, resentment 등 (이름은 학습 후 해석)
4. **Render-ready trace schema 지금부터**: render 자체는 v2.0이지만 로그 구조는 v1.0부터
5. **전 생애 = phase-linked local simulators**: 단일 50년 agent 아님
6. **세계 = 3층 구조**: principal agents + role nodes + structural fields (agent count 아님)

### 즉각 원칙 (용어/해석 교정 — 4차 리뷰 반영)

- "phase transition" → "threshold-triggered regime switch" (궤적은 linear, 이산성은 trigger)
- "terminal convergence = 역사 필연성" → "현 규칙계 saturation attractor" (model artifact)
- "behavioral > state signal" → "this model에서 leading indicator"
- "universality" 주장 (v1.2 Iter 57 업데이트): **"engine universality"** 주장 가능 — 3번째 이질적 시나리오(Talleyrand, Type A 협상형)가 동일 엔진에서 실행되고 `test_cross_scenario_pom_asymmetry.py`에서 POM 교차 적용 비대칭성 증명됨. 하지만 **"empirical generalization"**(수치 claim의 범인물 일반화)은 여전히 금기. 권장 표현: "the engine is scenario-agnostic; the patterns are scenario-specific."

---

## 1. 프로젝트 정체성

### 1.1 한 줄 정의

> **Multi-agent, hazard-driven, ensemble historical simulator.**
> 여러 인물의 상호작용을 수천 번 시뮬레이션하고 결과 분포를 관측한다.

### 1.2 근본 질문

> "이 사람의 삶에서, 무엇이 갈라지는 순간이었는가?"

### 1.3 방법론

개별 결과가 아니라 **분포를 관측**:
- 파라미터 공간 지형도 (어떤 조건에서 어떤 경로)
- 경로 유형 클러스터링 (도주형, 부인형, 순교형)
- 분기점(bifurcation) 탐지 (변수를 조금 바꾸면 결과가 뒤집히는 임계점)
- 역사적 경로의 위치 (필연이었는가, 우연이었는가)

### 1.4 두 비전

- **비전 B (베이스)**: 인과 시뮬레이션. 시스템이 수천 번 돌리고 분포를 관측.
- **비전 A (나중)**: 내러티브 체험. 발견된 경로를 1인칭으로 체험.

---

## 2. 엔진 4층 구조

```
Layer 1: Universal Engine (인물/시대 비종속)
  ├── AgentState (물리/감정/관계/도메인)
  ├── HazardEngine (상태 기반 확률적 이벤트 발생)
  ├── TriggerEngine (다중 에이전트 조건 -> 이벤트 동적 생성)
  ├── RuleEngine (상태 전이 규칙)
  ├── AgentScheduler (에이전트 활성화 순서 관리)
  ├── SimulationWorld (다중 에이전트 루프)
  ├── SimulationRunner (단일 에이전트 hazard-driven 루프, 하위 호환)
  ├── ResolutionEngine (동적 해상도)
  └── Analysis Pipeline (SALib, UMAP, HDBSCAN, pyABC)

Layer 2: Domain Module (인물의 전문 분야)
  - 베드로: FaithJourneyState (신앙 여정)
  - 유다: BetrayalPsychologyState (배반 심리)
  - 가야바: PoliticalCalculationState (정치적 계산)
  - 반 고흐: CreativeDriveState (창작 의지)

Layer 3: Era Module (시대 환경)
  - 1세기 팔레스타인

Layer 4: Biography Pack (인물 고유 데이터)
  - 초기 상태, hazard 이벤트, behavior_profile, 체크포인트(ground truth)
  - 다중 에이전트: shared/triggers.json (에이전트 간 상호작용 트리거)
```

---

## 3. Hazard-Driven 이벤트 시스템

v0.2.1의 tick 고정 이벤트를 대체. 핵심 전환:

```
기존: if tick == 152: 체포()
신규: hazard = f(fear, fatigue, confusion, ...) -> Poisson draw -> 체포()
```

### 3.1 HazardFunction

매 tick 상태에 따라 발생 확률 계산:
- `base_rate`: 상태 무관 기본률
- `factors`: 상태 기반 인자 목록 (field_path, weight, transform)
- `firing_probability = 1 - exp(-hazard * dt)` (Poisson process)

### 3.2 HazardEvent

- `preconditions`: 활성화 전제조건
- `anchor_window`: 발생 가능 tick 범위 (bounded stochasticity)
- `deadline_tick`: 미발생 시 강제 발동 (하위 호환)
- `cooldown`, `max_fires`: 발산 방지
- `effects_on_fire`, `action_options_on_fire`: 발동 시 효과

### 3.3 Competing Risks

eligible 이벤트들을 hazard 내림차순 정렬, 순차 발동 시도.
`max_fires_per_tick`으로 한 tick 과부하 방지.

### 3.4 Langevin 노이즈

매 tick 감정 상태에 가우시안 노이즈 주입 (`state_noise_scale`).
같은 상황에서도 미세한 심리적 요동으로 결과가 달라짐.

### 3.5 다중 에이전트 시스템 (M1-Multi)

핵심 전환: tick 하드코딩 이벤트 -> 에이전트 간 상호작용에서 이벤트 발생.

```
기존: tick 152에 체포 발생 (하드코딩)
신규: 유다 환멸 누적 -> 배반 행동 -> 가야바 위협 판단 -> 체포 (emergent)
```

#### SimulationWorld

다중 에이전트 루프 (매 tick):
1. 에이전트 활성화 순서 결정 (AgentScheduler)
2. 각 에이전트: AgentBehaviorProfile에서 자발적 행동 선택
3. 행동 효과 적용 (cross-agent 가능: target_agent_id)
4. TriggerEngine: 에이전트 상태/행동 조건 평가 -> 이벤트 동적 생성
5. HazardEngine: 확률적 이벤트 평가
6. 환경 동적 규칙 적용

#### TriggerEngine

- TriggerCondition: 특정 에이전트의 상태 필드 조건
- ActionTriggerCondition: 특정 에이전트의 행동 감지
- deadline_tick: 조건 미충족 시 강제 발동 (정경 호환 폴백)

#### 검증 결과

- 체포 자연 발생: 50/50 runs 100% spontaneous, mean=198 +/- 43
- 체포 tick 분산: 17개 서로 다른 값 (111~283)
- 유다 행동 진행: follow -> question -> withdraw -> inform -> betray

#### 분석 심화

- **Trigger Sensitivity**: 조건 +20% -> 44 tick 지연, cross-agent 제거 -> spontaneous 0%
- **Counterfactual**: 유다 제거 -> deadline only, 트리거 제거 -> 미발생
- **Threshold-triggered regime switch**: disillusionment ~1.0 임계, 0->4에서 arrest tick 급변 (338->158). Dynamics는 linear (R²=0.998), 이산성은 trigger에서 발생.
- **Precursor**: 93% intelligence_driven, 인과 체인 100%
- **Causal Lag**: bottleneck = surveillance->betray (63 +/- 30 ticks)
- **Crowd Effect**: 군중 추가 시 체포 24 tick 앞당김, Peter fear +0.62
- **Cross-Scenario**: Peter vs Van Gogh 동일 엔진 동형 구조 (100% sp 양쪽)

---

## 4. 상태 전이 규칙

### 4.1 물리 규칙
- FatigueRule, HungerRule, HealthRule

### 4.2 감정 규칙 (핵심: 교차 효과)
- FearResponseRule: 피로-공포 교차 증폭
- ConfusionRule: fatigue>7 AND fear>6 -> confusion 급등
- HopeRule, GriefRule, LoveRule

### 4.3 사회 규칙
- RelationshipDecayRule, GroupIsolationRule

### 4.4 시간 규칙
- HomeostasisRule (극단 -> 중앙 복귀), CircadianRule (일주기)

---

## 5. 동적 해상도

### 5.1 3-Tier

| Tier | 시간 단위 | 용도 |
|------|----------|------|
| Chronicle | 일~주 | 대부분의 생애 |
| Episode | 시간~일 | 이벤트 밀도 높은 구간 |
| Scene | 분~시간 | 분기점, 극한 긴장 |

### 5.2 전환 기준

1. **anchor_window**: 미리 지정된 고해상도 구간
2. **tension_trigger**: 긴장도(fear + confusion + fatigue + 감정 갈등)가 임계값 초과
3. **event_density**: 최근 N tick 내 이벤트 빈도가 임계 초과

---

## 6. 분석 파이프라인

### 6.1 전역 민감도 (SALib)
- **Morris 스크리닝**: 초기 탐색. 어떤 파라미터가 중요한지 빠르게 식별.
- **Sobol 분석**: 상호작용까지 보는 정밀 분석.

### 6.2 경로 클러스터링 (UMAP + HDBSCAN)
- Trajectory를 feature matrix로 변환
- UMAP 2D 임베딩
- HDBSCAN 밀도 기반 클러스터링
- "도주형", "부인형" 등 경로 유형 자연 출현 관측

### 6.3 분기점 탐지
- 파라미터 스윕 → 결과 분산 급증 지점 탐색
- 평균 기울기 급변 + 표준편차 급등 = bifurcation 후보

### 6.4 파라미터 보정 (pyABC)
- Approximate Bayesian Computation
- 역사 경로에 가장 가까운 파라미터 posterior 추정
- likelihood-free (시뮬레이터 내부를 모르는 상태에서 보정)

### 6.5 Trajectory 데이터셋
- 각 run을 JSONL 레코드로 저장
- seed, params, event_sequence, state_series, checkpoint_results, fired_events
- run-level 데이터가 모든 분석의 원본

---

## 7. 첫 인물: 베드로

### 7.1 범위
예수의 마지막 50일 (수난주간 + 부활 40일). 약 500 tick.

### 7.2 Ground Truth
성경 기록 = 체크포인트:
- 체포 시 칼을 뽑음 (요 18:10)
- 멀리서 따라감 (눅 22:54)
- 3회 부인 (마 26:69-75)
- 통곡 (마 26:75)
- 빈 무덤에 달려감 (눅 24:12)
- 디베랴에서 바다에 뛰어듦 (요 21:7)
- 회복 (요 21:15-17)

### 7.3 신학적 원칙
- 예수는 에이전트가 아님 (정경 타임라인 = 고정 외부 입력)
- 정경 말씀은 개역개정 그대로 (재작성 금지)
- 고통을 영성 자원으로 삼지 않음
- 베드로의 부인은 인간 조건의 이해로

### 7.4 관측 결과 (2000+ 회 hazard-driven, 파라미터 공간 탐색)

**경로 유형 분포:**
- 정경 경로 (따라감 + 3회 부인): 46.6%
- 도주형: ~29%
- 기타 (부분 부인, 고백 등): ~24%

**정경 경로의 분포 내 위치:**
- UMAP 중심에서 43rd percentile -- 극단이 아니라 자연스러운 위치
- "베드로의 경로는 특수한 조건의 희귀 결과가 아니라, 인간 조건의 자연스러운 귀결"

**Sobol 전역 민감도 (outcome: 부인 횟수):**

| 파라미터 | S1 (직접) | ST (전체) | 상호작용 |
|---------|-----------|-----------|---------|
| fear | 0.460 | 0.553 | 0.093 |
| love | 0.186 | 0.554 | 0.367 |
| hope | 0.101 | 0.511 | 0.409 |
| confusion | 0.104 | 0.466 | 0.362 |
| fatigue | 0.001 | 0.085 | 0.084 |

**핵심 발견 (v0.4 -- 환경 통합 + ablation 검증 후):**

1. **체포 분기 (도주 vs 따라감)**: love(31.8%) > hope(26.5%) > fear(22.9%) > surveillance(13.0%)
   - love <= 3.27 → 대부분 도주
   - love > 3.27 AND fear <= 4.76 → surveillance에 따라 follow/flee 갈림
2. **부인 분기 (deny3 vs 기타)**: hope(34.3%) = love(34.1%) = crowd_pressure(31.6%) -- fear/surveillance = 0%
   - "부인은 공포가 아니라, 희망/사랑의 부재 + 군중 압력의 결합"
3. **환경 효과**: surveillance 0→10에서 deny3 비율 88%→95%
4. **Rule ablation 결과**:
   - current(love+env): deny3=94%
   - identity/shame: deny3=78%
   - env_only: deny3=82%
   - uniform(baseline): deny3=14%
   - 모든 상태 기반 규칙이 baseline보다 5~7배 높음. 구조 차이가 크지만 방향은 일관.
5. **정경 경로**: 46.6% 출현, UMAP 중심 (outlier 아님)
6. **Sobol (환경 없이)**: fear 직접효과 크지만, love/hope 상호작용이 큼
7. **Morris (환경 포함)**: 부인에서 surveillance/crowd_pressure가 공동 1위, fear는 최하위
   - "외부 압력 모델이 없을 때 내부 상태가 과대평가되고 있었다" (ChatGPT 예측 적중)
8. **pyABC 보정**: 정경 조건 = fear=6.0, love=5.6, hope=2.0

### 7.5 검증 결과 (v0.5 -- POM/PRIM/Model Selection/shapiq)

**POM (Pattern-Oriented Modeling):**
- 7개 관측 패턴 동시 필터. current 규칙: 38.6% 통과. fear-only: 1.2%. uniform: 0%.
- POM이 규칙군을 32배 차이로 분리 (deny3 단독은 2배 차이).

**PRIM:**
- POM 통과 영역: love [1.4, 8.7], crowd [1.1, 7.2]. fear/hope 제한 없음.

**pyABC Model Selection:**
- current=100%, fear-only=0%, identity=0%. 유일한 유효 구조.

**shapiq (Shapley Interaction) -- 교정됨:**
- 3개 변수(fear/love/hope)에서: fear x love = 0.123 (1위)
- 5개 변수(+surveillance/crowd)에서: fear 단독 = 0.026, surveillance = 0.025 (공동 상위). fear x love = 0.014로 급락.
- **결론: shapiq 결과는 변수 세트에 의존. 특정 상호작용을 "핵심 동인"으로 확정하기 어려움.**
- **안정적인 것**: POM이 규칙군을 분리 (38.6% vs 1.2%)하는 것은 변수 세트 무관.

**Cross-Persona (베드로 vs 반 고흐):**
- 베드로: fear x love 상호작용이 핵심 (관계적 위기)
- 반 고흐: fear 단독이 핵심 (내적 위기)
- 공통: fear와 love가 상위 2개 변수. 인물을 넘어서는 핵심.

---

## 8. 기술 스택

- Python 3.11+
- Pydantic (스키마)
- pytest (테스트)
- SALib (민감도 분석)
- UMAP + sklearn HDBSCAN (클러스터링)
- pyABC (파라미터 보정)
- NumPy, pandas, scipy

---

## 9. 프로젝트 구조

```
Witness/
├── engine/
│   ├── core/
│   │   ├── state.py          # AgentState
│   │   ├── event.py          # ExternalEvent, StateEffect
│   │   ├── hazard.py         # HazardFunction, HazardEvent, HazardEngine
│   │   ├── environment.py    # EnvironmentState (외부 압력)
│   │   └── world.py          # SimulationConfig
│   ├── rules/
│   │   ├── base.py           # Rule Protocol, RuleEngine
│   │   ├── physical.py, emotional.py, social.py, temporal.py
│   ├── simulation/
│   │   ├── runner.py          # SimulationRunner (hazard-driven + legacy)
│   │   ├── decision.py        # 확률적 행동 결정
│   │   ├── checkpoint.py      # Hindcasting
│   │   ├── batch.py           # 앙상블 실행
│   │   ├── analysis.py        # SALib, UMAP, HDBSCAN, 분기점 탐지
│   │   ├── resolution.py      # 동적 해상도
│   │   └── calibration.py     # pyABC 파라미터 보정
│   └── io/
│       ├── loader.py          # JSON 로더
│       └── trajectory.py      # 경로 데이터셋 저장/로드
│
├── content/peter/             # Biography Pack: 베드로
│   ├── initial_state.json
│   ├── hazard_events.json
│   ├── canonical_events.json  # (legacy + interventions)
│   ├── checkpoints.json
│   └── domain_faith.py
│
├── tests/ (1845 fast tests, 0 fail, 2026-04-30 기준 — Observer Layer 212 tests: 130 base + 35 Pipeline + 33 Curation + 14 adapter)
│
├── scripts/story/                # Story Output Layer (2026-04-28 NEW)
│   ├── extract_story_features.py    # annotated probe → JSON
│   ├── build_narrative_ir.py        # JSON → semantic IR (atoms)
│   ├── render_story_ko.py           # IR → 한국어 텍스트 (template-guided)
│   ├── selector.py                  # J-Alpha+J-Beta anchor library (2026-04-30 moved here for Rule #1)
│   ├── generate_anchor_variations.py
│   └── generate_trilogy_view.py
├── engine/observer/              # World Observer Layer (2026-04-30 NEW, v1.3)
│   ├── snapshot_schema.py        # 4 Pydantic models (Snapshot/World/Group/Agent)
│   ├── recorder.py               # record_snapshot() + SnapshotStream
│   ├── core.py                   # Observer (4 lens API: World/Person/Group/Event)
│   ├── salience.py               # 8 tag types + top-N moments/agents
│   ├── replay.py                 # ReplayCursor + auto_bookmark + window helpers
│   └── adapter.py                # MultiAgentResult → Observer (post-hoc)
├── scripts/observer/             # World Observer scripts (2026-04-30)
│   ├── observer_report.py        # 11 text format functions
│   └── compare_views.py          # multi-stream + multi-lens compare
├── scripts/audit_report.py        # HARNESS H4-H8 자동 검증 + --stories 모드
├── data/story/                   # Story intermediate JSONs (48 features + 48 IRs)
├── docs/story/                   # 4 canonical + generated/ (96 .txt)
├── docs/observer/                # World Observer canonical spec
│
├── examples/demo_story.py         # Story 단일 entry point (P9 또는 --highlights)
├── examples/demo_observer.py      # Observer 단일 entry point (4 modes)
├── examples/demo_creative.py      # Creative IP track (J-Alpha + J-Beta)
├── CLAUDE.md, DESIGN.md, README.md, progress.md
└── requirements.txt
```

---

## 10. World Observer Layer (v1.3, 2026-04-30 NEW)

### 10.1 정의

Person Engine 위에 추가된 *흐르는 세계 관찰 계층*. 시뮬레이션이 생성하는 상태 변화를 tick 단위 snapshot stream으로 구조화하고, 다양한 렌즈 (Person / Group / Event / World) + zoom level + salience detector로 조회 가능하게 함.

핵심 원칙: **관찰기 ≠ 평가기**. story quality 자동 판정 안 함, *탐색 가능성*에 집중.

### 10.2 아키텍처

```
Pressure/Event Input
    ↓
Simulation Engine (existing — SimulationWorld)
    ↓ MultiAgentResult
World Snapshot Stream  ← engine/observer/recorder.py 또는 adapter.py
    ↓
World Observer Layer
    ├─ Person View (engine/observer/core.py)
    ├─ Group View
    ├─ Event View
    ├─ World View
    ├─ Salience Detector (engine/observer/salience.py)
    ├─ ReplayCursor (engine/observer/replay.py)
    └─ Multi-stream Compare (scripts/observer/compare_views.py)
    ↓
Text Reports (scripts/observer/observer_report.py)
```

### 10.3 Snapshot Schema

```python
class Snapshot(BaseModel):
    tick: int
    active_events: list[str]
    world: WorldSnapshot       # crowd_mood / blame / suspicion / authority / scarcity
    groups: list[GroupSnapshot]  # cohort/location: dominant_mode + tension
    agents: list[AgentSnapshot]  # light view: fear/hope/shame_self + delta tags
    salience_hints: list[str]    # 8+ tag types
```

`AgentSnapshot`은 `engine.core.state.AgentState`의 *light view subset* (fear/hope/shame_self만). caller가 `role_map`으로 generic role tag 제공 (no person hardcoding).

### 10.4 ABSOLUTE Rules 준수

- **Rule #1** (no person hardcoding in engine/): Observer schema는 *generic role tag* (follower/crowd/authority). Caller가 `role_map` 제공.
- **Rule #6** (engine API preservation): SimulationWorld 무수정. `result_to_observer()` adapter가 외부에서 *post-hoc* 변환.

### 10.5 9 Salience tag types

| Tag | 감지 |
|---|---|
| `pressure_spike` | world.scarcity_pressure tick-over-tick delta > 0.2 |
| `authority_vigilance_spike` | world.authority_vigilance jump |
| `public_suspicion_jump` | world.public_suspicion jump |
| `blame_concentration_spike` | world.blame_concentration jump |
| `cohort_split` | 2+ groups in different dominant_modes |
| `recovery_turning_point` | group mode shift saturation→recovery |
| `saturation_lock` | group mode "saturation" 5+ ticks 연속 |
| `low_activity_tension` | crowd_mood "tense" + active_events 0 |
| `agent_state_shift` | agent delta non-empty |

### 10.6 MVP scope (Lee directive)

**포함**:
- Snapshot Recorder (post-hoc + adapter for SimulationWorld)
- 4 lens (World/Person/Group/Event)
- Salience top 5 / top unstable agents
- Jump/Replay/Bookmark
- Multi-stream comparison (anchor seed level)
- Text reports (한국어 categorical tag 매핑)

**제외**:
- Full GUI / live interactive dashboard (text-based MVP)
- Story quality scoring (관찰기 ≠ 평가기 원칙)
- Public-facing browser
- Real-time callback hook (post-hoc 변환만 — 추가 phase 시 directive 필요)

### 10.7 검증

- 212 tests in `tests/test_observer/` (130 base + 35 Pipeline + 33 Curation + 14 adapter)
- Engine integrity: 0 violations (Rule #1 + Rule #6 준수)
- Ruff + mypy clean

### 10.8 Demo entry

```bash
python examples/demo_observer.py            # full demo
python examples/demo_observer.py --status   # MVP 상태
python examples/demo_observer.py --views    # 4 lens text
python examples/demo_observer.py --replay   # ReplayCursor + auto bookmark
python examples/demo_observer.py --compare  # 3 seeds 측면 비교
```

### 10.9 Canonical spec

`docs/observer/WORLD_OBSERVER_LAYER_SPEC.md` (12 sections, MVP scope + phase plan).

---

## 11. Visual Observer Layer (v0-v0.1, 2026-04-30 NEW)

### 11.1 정의

도트 기반 visual track. Observer snapshot stream을 도트/zone/timeline으로 시각화하여 *세계 흐름의 직관적 관찰* 제공. Lee directive `docs/archive/lee_directives_2026-04-30/WITNESS_DOT_VISUAL_OBSERVER_ROADMAP_AND_DIRECTIVE.md` §0 verbatim — *"도트 기반 흐르는 세계 관찰 + 줌인/줌아웃 + 이야기 후보 발견"*.

### 11.2 아키텍처 (3 entry points, 역할 분리)

| Entry HTML | 역할 |
|---|---|
| **`visual/explorer.html`** | **Broad navigation entry** (v0/v0.1) — anchor selector + view toggle (single/cross) + candidate panel + packet side panel |
| `visual/dot_observer_replay.html` | **Single-run deep view** (V2) — 200-tick replay + 5 panel + agent dot click + range overlay |
| `visual/dot_observer_cross_seed.html` | **Cross-seed deep view** — 5 seeds small multiples + per-seed full detail |

기존 deep view 보존 — explorer.html이 *기능 superset*이 아닌 *navigation superset*.

### 11.3 4 단계 누적 검증 (모두 success)

| 단계 | Case |
|---|---|
| V0-V1 MVP | A (5+/6) |
| V2 minimal interaction | A (4/4) |
| Anchor 2 single-seed | A-2 |
| Cross-seed | CS-A |
| Visual Explorer v0 통합 | EX-A |

### 11.4 ABSOLUTE Rules 준수

- Rule #1: visual 코드에 person hardcoding 없음 (anchor_id parameter only)
- Rule #6: engine/observer/* 무수정
- 관찰기 ≠ 평가기: visual은 *분류 + 탐색*만, *quality verdict* 안 함

### 11.5 Tech stack

- Vanilla JS + SVG (외부 dependency 0)
- HTTP server (`python -m http.server`)
- 데이터: schema v1 (single-run) + cross_seed_v1 (multi-seed)

### 11.6 Demo entry

```bash
# 데이터 export (1회)
python scripts/visual/export_dot_observer_data.py
python scripts/visual/export_dot_observer_data.py \
    --anchor peter_scarcity_triple --output data/visual/dot_observer_data_triple.json
python scripts/visual/export_cross_seed_visual_data.py \
    --anchor peter_scarcity_triple --seeds 0 1 2 3 4 \
    --output data/visual/dot_observer_cross_seed_triple.json

# HTTP server + 브라우저
python -m http.server 8000
# 단일 entry (default):
http://localhost:8000/visual/explorer.html
```

### 11.7 Canonical spec

`docs/visual/VISUAL_EXPLORER_V0_1_OPERATING_GUIDE.md` (운영 매뉴얼).
`docs/visual/VISUAL_TRACK_SYNTHESIS_REVIEW.md` (4 단계 종합).
