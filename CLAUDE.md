# CLAUDE.md — Witness

> **Witness (v2 refactor 진행중)**: *결정론적 서사 시뮬레이션 엔진(뼈대) + Rule-based Flesh MVP / ML 학습 Narrative Mode 변환기(살)* 의 이중 구조.
>
> 뼈대 = anchor-agnostic universal seed 출력 (`engine/observer/skeleton_output.py` SkeletonOutput v1 — **FROZEN** + UniversalStorySeed v1.1 / RFC-0001).
> 살 = ① **Rule-based Flesh MVP** (Phase 2.75, ✅ 구현 — `engine/observer/genre_adapter.py`) + ② **ML 학습 Narrative Mode** (Phase 3-5, 미구현).
> Anchor-specific 표현 (인물명 / 정경 사건 / 시대)은 `engine/anchor/` 와 `content/anchors/{id}/binding.json` 에서 분리 보관.

| 참조 | 역할 |
|---|---|
| [docs/witness_rubric_design.md](docs/witness_rubric_design.md) + [docs/WITNESS_V3_RUBRIC_DESIGN_REVIEW.md](docs/WITNESS_V3_RUBRIC_DESIGN_REVIEW.md) | **Rubric directive (2026-05-11, 29 cycle 완료)** — 4-Axis Discovery **Candidate Classifier**. cycle 1-15 (P0/P1/P2 + Result-1~11 ensemble) + cycle 16-29 (review §2.5 alignment / §5 discrimination empirical / generic walker / Phase 3.1 §29 verifier). Acceptance §7 17+/17+ ✅ + review §2.1/§2.2/§2.3/§2.4/§2.5/§2.6/§3/§5/§H8 all validated ✅. 123+ rubric tests. |
| [docs/WITNESS_PHASE_3_05_PREP_INTEGRITY_AND_VALIDATOR_HARDENING_PLAN.md](docs/WITNESS_PHASE_3_05_PREP_INTEGRITY_AND_VALIDATOR_HARDENING_PLAN.md) | **현재 메인 directive** (2026-05-11 Phase 3.05). Cycle 7-12 prep 검수 결과 — prep 산출물 정직성·검증성 강화. Step 1+2 (score_breakdown 정직성) ✅ / Step 3+4 (validator strict + report 3 layer) ✅ / Step 5+6 (deploy status matrix + docs sync) ✅ |
| [docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md](docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md) | 모 directive (Phase 3.0/3.1 prep 전체). v1.1 핵심 = "Claude Code = 데이터 공장 / LLM = 라벨러 / User = 승인권자". Phase 3.0 Mode A 파이프라인 ✅ + Phase 3.1 No-ML baseline ✅ (외부 의존 0) |
| [docs/plans/PHASE_3_0_PIPELINE_OPERATING_GUIDE.md](docs/plans/PHASE_3_0_PIPELINE_OPERATING_GUIDE.md) | Phase 3.0 Mode A 9 step + **Phase 3.1 baseline 4 step (Step 10-13: profiles / flesh / episode_intensity / demo 13a+13b)** 운영 절차 + Acceptance 매핑 + **Deploy Status Matrix (§9, Phase 3.05 Step 5)** |
| [docs/WITNESS_PHASE_2_9_PORTFOLIO_FINALIZATION_AND_PHASE_3_PREP_PLAN.md](docs/WITNESS_PHASE_2_9_PORTFOLIO_FINALIZATION_AND_PHASE_3_PREP_PLAN.md) | 직전 (2026-05-10). Phase 2.9 Portfolio Finalization (✅ 완료) |
| [docs/plans/PHASE_3_0_APPROVAL_CHECKLIST.md](docs/plans/PHASE_3_0_APPROVAL_CHECKLIST.md) | Phase 3.0 시작 전 사용자 승인 5+2건 체크리스트 (단계별 12 step) |
| [docs/WITNESS_PHASE_2_8_GENRE_ADAPTER_POLISH_AND_PHASE_3_PILOT_PLAN.md](docs/WITNESS_PHASE_2_8_GENRE_ADAPTER_POLISH_AND_PHASE_3_PILOT_PLAN.md) | 직전 (2026-05-10). Phase 2.8 Polish (✅ 완료) |
| [docs/WITNESS_PHASE_2_75_GENRE_ADAPTER_MVP_PLAN.md](docs/WITNESS_PHASE_2_75_GENRE_ADAPTER_MVP_PLAN.md) | 더 이전 (2026-05-10). Rule-based Genre Adapter MVP (✅ 완료) |
| [docs/WITNESS_NARRATIVE_MODE_VALIDATION_FIX_PLAN.md](docs/WITNESS_NARRATIVE_MODE_VALIDATION_FIX_PLAN.md) | 더 이전 (2026-05-09). Phase 2.5 Validation Fix — UniversalStorySeed v1.1 / 의미 보존 강제 (✅ 완료) |
| [docs/witness_narrative_mode_plan.md](docs/witness_narrative_mode_plan.md) | 모 plan (2026-05-09). Skeleton-Flesh 전체 |
| [docs/plans/RFC_TEMPLATE.md](docs/plans/RFC_TEMPLATE.md) + [RFC_UNIVERSAL_STORY_SEED_V1_1.md](docs/plans/RFC_UNIVERSAL_STORY_SEED_V1_1.md) | RFC governance + RFC-0001 (approved) |
| [DESIGN.md](DESIGN.md) | 아키텍처 / 4층 엔진 / 로드맵 (2026-05-10 갱신: 두 갈래 Flesh) |
| [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) | 디렉토리 트리 + 파일별 역할 |
| [docs/HARNESS.md](docs/HARNESS.md) | H1-H8 상세 + 자가감사 8항목 |
| [progress.md](progress.md) · [lessons.md](lessons.md) | 세션 메모리 / 크로스 세션 학습 |

**Refactor 작업 원칙** (2026-05-10 갱신):
- engine 시뮬레이션 로직 변경 금지 (skeleton 보존)
- 새 anchor / scenario / engine metric 도입 금지
- 실제 대본/스크립트 학습 금지 (회차 줄거리만)
- ML 규모는 (b) Mid ML로 한정
- Evaluator γ 없이 Transformer β 먼저 만들지 않기
- SkeletonOutput / UniversalStorySeed contract 변경 시 RFC_TEMPLATE.md 따라 RFC 의무
- **Genre Adapter (Phase 2.75 + 2.8)**: structure_only 변환만, 없는 사건 추가 0, 대사 생성 0, 특정 작품/대사 모방 0. 새 장르 = `content/genres/{genre_id}/rulebook.json` + `audit_blocklist.json` 작성으로 끝 (engine 변경 0). audit (`engine/observer/genre_audit.py`)이 hard 위반 + soft `quality_warnings` (조사 placeholder / duplicate / repeated function / empty lens) 모두 검사. Phase 2.8 polish 산출: `genre_lens_ko` (장르 렌즈 한 줄) / `outline_templates` (rhythm × phase × role) / structured `adapted_outline_steps` (seed link 보존).
- **Phase 3 Go gate**: ML/외부 의존성 작업 시작 전 `python scripts/skeleton/validate_skeleton_phase3.py`로 deployed skeleton 검증 또는 `is_skeleton_phase3_ready(out)` 호출.
- **Phase 3.0 Data Pilot (v1.1)**: 코드 파이프라인 + Phase 3.1 prep 모두 *외부 의존 0*으로 작성됨. 사용자 승인 5+2건 후 즉시 운영 가능 — Mode A (수동 LLM annotation) → Mode B (승인 fetch) → Mode C (API). 절차: `docs/plans/PHASE_3_0_APPROVAL_CHECKLIST.md` (12 step). 운영 가이드: `docs/plans/PHASE_3_0_PIPELINE_OPERATING_GUIDE.md`. 미승인 시 *외부 fetch / LLM API / 원문 저장 / 학습* 0건 — `.gitignore` preempt 완료.
- **Phase 3.1 prep (No-ML)**: `engine/observer/{genre_profile,flesh_baseline,episode_intensity,adaptation_recommendation}.py` + `scripts/narrative/{build_genre_profiles,run_flesh_baseline,build_flesh_baseline_demo,run_adaptation_recommendation,build_adaptation_recommendation_demo,apply_top_recommendation}.py` + `scripts/annotation/{run_episode_intensity,build_episode_intensity_demo}.py` + `scripts/data/verify_phase3_1_acceptance.py`. 세 layer baseline:
  - **Target A — seed × profile fit** (`flesh_baseline.py` / `flesh_baseline_output_v1`): weighted rule score (compatibility 50% + annotation 50%) — SkeletonOutput seed가 어떤 장르 flesh와 잘 맞는지.
  - **Target B — episode × profile intensity** (`episode_intensity.py` / `episode_intensity_v1`, Plan §22.2): annotator 평균 후 GenreProfile.feature_weights 선형 결합 — 각 *에피소드*가 장르 시그니처에 얼마나 부합하는지. 데모: `docs/portfolio/demo_episode_intensity/index.html` (cycle 40, **fixture-only** — `tests/fixtures/annotation_public_safe/` 기반, banner 강제).
  - **Target C — seed → ranked top-K genres** (`adaptation_recommendation.py` / `adaptation_recommendation_v1`, Plan §22.3, cycle 17-19): Target A의 flat list를 *seed별 grouped + score 내림차순 + top_k*로 재구성. 데모: `docs/portfolio/demo_adaptation_recommendation/index.html`.
  - **Plan §24 Step 2 bridge** (`apply_top_recommendation.py`, cycle 25): adaptation_recommendation → genre_adapter delegate. modal genre 자동 + `--genre` override + `calibration_status` / `mode` 노출. SkeletonOutput → Target C → modal_genre → GenreAdaptedOutput chain 완결.
  - **Plan §29 verifier** (`verify_phase3_1_acceptance.py`, cycle 29-31): 9 항목 자동 점검 (AUTO 7 + PENDING 1 + HEURISTIC 1) — Phase 3.0 verifier 대칭. `--md-report` flag + Operating Guide §4.6.
  학습 0 / fine-tuning 0 / raw text 0. 데모: `docs/portfolio/demo_flesh_baseline/index.html` + `docs/portfolio/demo_adaptation_recommendation/index.html`. ablation baseline으로 ML 진입 시 그대로 사용 가능.
- **Phase 3.05 정직성 보강** (2026-05-11): cycle 7-12 prep 검수 후 rulebook_only score가 *실제 데이터 기반 추천처럼 보일 위험* 발견. 보강:
  - `flesh_baseline.recommend_seed`가 *항상* score_breakdown 채움 — `{axis_match, pressure_overlap, compatibility_score, annotation_score (rulebook_only=None), annotation_components, final_score, mode}`. 빈 dict 0건.
  - demo HTML/MD: "Prep mode (rulebook-only)" banner + `fit_label (rulebook-only)` 병기 + breakdown 명시 표시.
  - validator strict: `--strict + --synopsis 없음 → exit 2` (quote validation 강제). hallucination report 3 layer 분리 (`valid_files_only_summary` / `all_files_summary` / `invalid_files`). threshold = valid 기준.
  - Operating Guide §9 **Deploy Status Matrix** — 5 분류 (deployed-prep / deployed-data / script-only / fixture-only / generated-after-approval) + 파일 요청 원칙.
- **Rubric directive (2026-05-11, 29 cycle 누적)**: 4-Axis Discovery **Candidate Classifier** (review에 따라 *Evaluator* → *Candidate Classifier* 명칭 격상). `engine/rubric/{character_critic,canon_critic,causal_critic,novelty_critic,context_break_critic,scene_response_critic,rubric_evaluator}.py` + `scripts/rubric/{run_rubric,trace_to_records,build_ensemble_html}.py`. 핵심:
  - **8-step flowchart** (review §2.2 P0): hardcoded → canon hard violation → **causal gate** → context-break → novelty noise → canonical reproduction → character_consistent_novel_CANDIDATE / canon_compatible_character_DRIFT.
  - **review §2.5 P1 extended** (cycle 16/20/22): CausalCritic에 *optional* `action_pressure_map` 인자 + `pressure_action_alignment` 측정. engine은 person-agnostic 유지 (map 비어 있으면 alignment_evaluated=False, gate 영향 0). CLI `--action-pressure-map` flag 노출.
  - **review §5 discrimination empirical 입증** (cycle 23/26): Phase H 재설계된 CharacterCritic 3 axis (relation_stability / identity_retention / recovery_plausibility + minimum gate) — anti-signature fixture로 *양방향 discriminate* + axis-isolated N-case ensemble로 *각 axis 독립 trigger* 입증.
  - **L84/L85 generic detector** (cycle 28): `report_to_dict()` walker가 `__dict__` + `@property` descriptor *모두* walk — 향후 @property aliases 자동 surface. meta-test invariant로 stranded 패턴 차단.
  - **Rule #14 + scalar 합산 금지**: rubric은 학습 loss 0건 (test로 강제). 4 critic report independent 유지.
  - **모든 threshold** `calibration_status: "uncalibrated_phase3_placeholder"` 명시 (Phase 5+ 실측 보정 전).

**Tradeoff**: 이 규칙은 속도보다 정직성·검증을 우선한다. 단순 작업은 판단으로 우회 가능.

---

## 1. Think Before Coding

**가정하지 마라. 혼란을 숨기지 마라. 트레이드오프를 표면화하라.**

- 불확실하면 멈춘다. 무엇이 불분명한지 명시하고 묻는다.
- 다중 해석이 있으면 `[A][B][C]`로 제시한다. **조용히 고르지 않는다.**
- 수정 요청은 **Patch / Refactor / Rebuild** 중 어디인지 먼저 판단한다.
- 구현 요청은 **Probe (검증) / Stitch (통합)** 중 어느 단계인지 선언한다.

## 2. Surgical Changes

**요청된 것만 수정한다. 인접 코드는 건드리지 않는다.**

- 변경된 모든 줄은 사용자 요청으로 직접 추적되어야 한다.
- 내 변경이 만든 orphan만 제거한다. 기존 dead code는 언급만 — 삭제 금지.
- 추가보다 삭제 우선. 200줄 작성 후 50줄로 가능하면 다시 쓴다.
- 임시방편 패치 금지. 근본 원인을 고친다.

## 3. Goal-Driven Verification

**검증 기준 없이 "완료" 선언 금지.**

- 테스트 통과 / 로그 / 실행 결과 등 작동 증거를 제시한다.
- 멀티스텝은 `1. 단계 → verify: 체크` 형식으로 계획한다.
- 동일 에러 2회 실패 시 접근 방식 자체를 재검토한다.
- Probe 완료 시 Recipe Card로 증류 후 실험 코드 삭제 제안.

## 4. HARNESS — 보고 정직성 (자기 편향 차단)

> Spike 6의 7 반복 패턴에서 도출. 보고 직전 [자가감사 8항목](docs/HARNESS.md#자가감사-8항목-보고-직전-강제-응답--h7-통합-체크) 강제 응답. 패턴별 trigger word + 자기질문 상세는 [docs/HARNESS.md](docs/HARNESS.md).

- **H1** — 수치 보고 시 trivial explanation + falsification criterion 명시
- **H2** — 실패를 외부 탓으로 돌리기 전 "시도하지 않은 대안 3개" 명시
- **H3** — spec/rule 인용은 **verbatim**. 방패로 사용 금지
- **H4** — 보고서 필수: *What could still be wrong / What I did NOT try / Alternate interpretations*
- **H5** — Lee의 원래 지시는 verbatim 보존. 축소 해석 시 사유 + 재확인 요청
- **H6** — 결정 요청 시 선택지를 equal weight로, 내 bias 명시
- **H7** — 보고 직전 자가감사 8항목 응답 (HARNESS.md 참조)
- **H8** — sensitivity ratio가 headline claim이면 **5+ seed ensemble 필수**, single-seed는 illustration 한정

**금지어** (경고 없이 사용 불가): "설계의 승리", "핵심 원천", "positive 증거", "준수 완료", "살아 움직인다", "작동한다"(단독 — "조건 X 하에서"로 조건부화)

자동 검증: `python scripts/audit_report.py <report.md>`

## 5. 프로젝트 경계

**엔진/콘텐츠 분리** — `grep -r "peter\|Peter\|베드로" engine/` 결과는 항상 0건이어야 한다.

**신학적 기준** (베드로 편)
- 예수의 신성을 에이전트화하지 않는다.
- 고통을 영성 자원으로 삼지 않는다.
- 베드로의 죄는 도덕적 비난이 아닌 인간 조건의 이해로.
- 교파적 편향 최소화.

**스타일** — 이모지 금지. 간결. 객관적·중립적 톤. 기술적 정확성 우선.

---

**Commands**: `pytest` · `pytest --cov=engine` · `ruff check . && mypy engine/`
