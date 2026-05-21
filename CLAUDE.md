# CLAUDE.md — Witness

> **Witness (post-cleanup 2026-05-15)**: *결정론적 서사 시뮬레이션 엔진 (뼈대)* + Track A 드라마 마이닝 (ML MVP 인정 후 마무리).
>
> Skeleton = anchor-agnostic universal seed 출력 (`engine/observer/skeleton_output.py` SkeletonOutput v1 — **FROZEN** + UniversalStorySeed v1.1 / RFC-0001).
> Anchor binding (인물명 / 정경 사건 / 시대)은 `engine/anchor/` + `content/anchors/{id}/binding.json`.
>
> Flesh ① (Rule-based Genre Adapter) / Rubric (Discovery Candidate Classifier) / Visual track → **archive로 이동** (2026-05-15). [docs/DEPRECATED_TRACKS.md](docs/DEPRECATED_TRACKS.md) 참조.

---

## 핵심 참조

| 항목 | 역할 |
|---|---|
| [DESIGN.md](DESIGN.md) | 아키텍처 + 4층 엔진 + Skeleton-Flesh 이분 (post-cleanup) |
| [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) | 디렉토리 트리 (post-cleanup) |
| [docs/DEPRECATED_TRACKS.md](docs/DEPRECATED_TRACKS.md) | Archive 4 폴더 + active 보존 |
| [docs/HARNESS.md](docs/HARNESS.md) | H1-H8 자가감사 8항목 |
| [docs/results/witness_final/](docs/results/witness_final/) | Track A 최종 정리 11 파일 (inventory / metrics / trajectory / data_spec / model_spec / env / taxonomy_summary / labeling_track_summary / learning_inputs_summary / qualitative_summary / discrepancies) |
| [docs/plans/RFC_TEMPLATE.md](docs/plans/RFC_TEMPLATE.md) + [RFC_UNIVERSAL_STORY_SEED_V1_1.md](docs/plans/RFC_UNIVERSAL_STORY_SEED_V1_1.md) | RFC governance |
| [progress.md](progress.md) · [lessons.md](lessons.md) | 세션 메모리 (L1-L88) |

---

## 살아남은 active 트랙

### Skeleton (foundation)
- `engine/{core, rules, simulation, rendering}/` — 결정론적 시뮬레이션
- `engine/observer/` — taxonomy + skeleton_output + universal_story_seed + Story Emergence (moment/thread/narrative_opportunity 등)
- `engine/anchor/` — AnchorRegistry + 한국어 binding
- `engine/{person, persona, population, world, action, policies, constraint, io}/` — 시뮬레이션 코어
- `world/` (root) — world dynamics root module
- `content/{universal, anchors, shared, peter, judas, caiaphas, crowd, vangogh, gauguin, theo, talleyrand}/`

### Track A — Drama Mining
- `drama_mining/` — AI-Hub 023 loader/preprocess/split
- `scripts/labeling/` — Stage 1-3 Gemma + repair + taxonomy_review
- `scripts/witness_train/` — Stage 1/2 KoBART + Qwen LoRA + eval
- `data/processed/witness_v{1,2}/` (gitignored) + `models/` (gitignored)
- `docs/results/{witness_final, witness_train_v{1,2}, gemma_labeling_poc, taxonomy_review}/`

### Story Emergence + Narrative Mining (active)
- `scripts/narrative/` — moment / thread / story_candidate / mining_console / life_arc
- `scripts/{observer, story, report, skeleton}/`
- `tests/test_{engine, narrative, observer, story, person, persona, peter, population, talleyrand, vangogh, world, world_process, action, report, skeleton, drama_mining_*}/`

---

## Archive (2026-05-15 이동)

| 폴더 | 트랙 |
|---|---|
| `archive/frozen_flesh_adapter_2026_05_15/` | Genre Adapter (Flesh ①) — Phase 2.75/2.8/2.9/3.0/3.05/3.1 |
| `archive/frozen_rubric_2026_05_15/` | Discovery Candidate Classifier (8-step, 124+ tests) |
| `archive/frozen_visual_2026_05_15/` | Pixel World / PSD / PEP / WFO 5 sub-track |
| `archive/legacy_scripts_2026_05_15/` | v0.5/v0.7 paper era 17 scripts |
| `archive/track_a_directives_2026_05_15/` | Track A directives 16개 (drama_mining/Gemma/train/finalize) |
| `archive/track_a_pivot_2026_05_12/` | Track B v2 crawl 결과 |
| `archive/{data_legacy, b_direction_legacy, output_legacy, outputs_legacy}/` | 이전 archives |

---

## 작업 원칙 (2026-05-15)

- **Skeleton engine 시뮬레이션 로직 변경 금지** (FROZEN SkeletonOutput contract)
- **새 anchor / scenario / engine metric 도입 금지** — Track A 종결 후 안정 상태 유지
- **archive로 옮긴 자산 복귀 금지** — Lee 별도 결정 시에만
- **SkeletonOutput / UniversalStorySeed contract 변경 시 RFC 의무** ([docs/plans/RFC_TEMPLATE.md](docs/plans/RFC_TEMPLATE.md))
- **Track A 재진입 시 ML 학습은 별도 디렉티브로** — 본 directive 자동 진입 금지 (witness_finalize_directive_2 종결)

**현재 상태**: **2,095 fast tests / 1 skipped / 0 fail / 0 regression** (post-cleanup baseline).

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

## 4. HARNESS — 보고 정직성

> [docs/HARNESS.md](docs/HARNESS.md) 자가감사 8항목 (H1-H8) 보고 직전 강제 응답.

- **H1** — 수치 보고 시 trivial explanation + falsification criterion 명시
- **H2** — 실패를 외부 탓으로 돌리기 전 "시도하지 않은 대안 3개" 명시
- **H3** — spec/rule 인용은 **verbatim**
- **H4** — 보고서 필수: *What could still be wrong / What I did NOT try / Alternate interpretations*
- **H5** — Lee의 원래 지시는 verbatim 보존. 축소 해석 시 사유 + 재확인 요청
- **H6** — 결정 요청 시 선택지를 equal weight로, 내 bias 명시
- **H7** — 보고 직전 자가감사 8항목 응답
- **H8** — sensitivity ratio가 headline claim이면 **5+ seed ensemble 필수**

**금지어**: "설계의 승리", "핵심 원천", "positive 증거", "준수 완료", "살아 움직인다", "작동한다"(단독 — "조건 X 하에서"로 조건부화)

## 5. 프로젝트 경계

**엔진/콘텐츠 분리** — `grep -r "peter\|Peter\|베드로" engine/` 결과는 항상 0건이어야 한다.

**신학적 기준** (베드로 편)
- 예수의 신성을 에이전트화하지 않는다.
- 고통을 영성 자원으로 삼지 않는다.
- 베드로의 죄는 도덕적 비난이 아닌 인간 조건의 이해로.
- 교파적 편향 최소화.

**스타일** — 이모지 금지. 간결. 객관적·중립적 톤. 기술적 정확성 우선.

---

**Commands**: `pytest -m "not slow and not archived" -q` · `ruff check . && mypy engine/`
