# WITNESS Cleanup Report — 2026-05-15

> Lee 지시: "필요없는 문서/파일/폴더 정리, 통합 가능한 문서 합치기, 버려진 코드는 기록만 남기고 삭제, 엔진→Flesh까지 깔끔하게."

---

## 1. 결과 요약

| Metric | Before | After | Δ |
|---|---:|---:|---:|
| **Fast tests pass** | 2,693 | **2,095** | -598 (archived tests 포함) |
| **Fast tests fail** | 0 | **0** | 회귀 0 |
| docs/*.md (top-level) | 79 | **29** | -50 |
| docs/plans/ | 15 | **3** | -12 |
| docs subdir 갯수 | 22 | 19 | -3 (visual, annotation, reports 삭제) |
| scripts/ root .py | 17+ | 0 | -17 (legacy 이동) |
| __pycache__/ | 76 dirs | 0 | -76 |
| output/ files | 54 | 0 | -54 |
| Archive 폴더 | 5 | 9 | +4 (frozen_flesh_adapter, frozen_rubric, frozen_visual, legacy_scripts, track_a_directives) |

---

## 2. 이동된 트랙 (Lee 결정 4개 모두 "Archive로 이동")

### 2.1 Genre Adapter Track (Flesh ① Rule-based MVP)
→ [archive/frozen_flesh_adapter_2026_05_15/](../archive/frozen_flesh_adapter_2026_05_15/) ([README](../archive/frozen_flesh_adapter_2026_05_15/README.md))

- engine/observer/{genre_*, flesh_baseline, episode_intensity, adaptation_recommendation}.py (7)
- content/genres/ (2 장르)
- scripts/{narrative (9 Genre Adapter 한정), annotation (10)}
- tests/test_genre/ (7) + tests/test_skeleton/test_phase3_* / test_phase1_* / test_phase2_* / test_annotate_with_llm 등 (9)
- tests/test_world/test_jesus_agent.py (content/jesus 의존)
- docs/portfolio/demo_{flesh_baseline, adaptation_recommendation, episode_intensity, genre, genre_comparison, genre_japanese}/ (6 dirs)
- docs/WITNESS_PHASE_{2_75, 2_8, 2_9, 3_0_3_1, 3_05}_*.md (5)
- docs/plans/PHASE_3_0_* + GENRE_ADAPTER_* + DATA_SOURCE_* (12)
- docs/{NARRATIVE_MODE_VALIDATION_FIX_PLAN, witness_narrative_mode_plan, witness_manual_annotation_plan}.md (3)

### 2.2 Rubric Track (Discovery Candidate Classifier)
→ [archive/frozen_rubric_2026_05_15/](../archive/frozen_rubric_2026_05_15/) ([README](../archive/frozen_rubric_2026_05_15/README.md))

- engine/rubric/ (11 .py)
- scripts/rubric/ (3 scripts)
- tests/test_rubric/ (5 files, 124+ test functions)
- tests/fixtures/rubric_demo/ (14 fixtures)
- docs/portfolio/demo_rubric/ (39 files, 22+ reports + ensemble_visualization.html)
- docs/{witness_rubric_design, WITNESS_V3_RUBRIC_DESIGN_REVIEW}.md

### 2.3 Visual Track
→ [archive/frozen_visual_2026_05_15/](../archive/frozen_visual_2026_05_15/) ([README](../archive/frozen_visual_2026_05_15/README.md))

- visual/ (8 HTML)
- scripts/visual/ + scripts/narrative/{demo_seed_diversity, run_portfolio_demo}
- tests/test_visual/ (3) + tests/test_narrative/{test_demo_seed_diversity, test_general_audience_output, test_portfolio_demo, test_portfolio_demo_episode} (4)
- docs/visual/ (22 docs)
- docs/WITNESS_PEP_*, PIXEL_*, WORLD_TO_VISUAL, ENGINE_EVENT_LOG_ADAPTER plans (5)
- docs/portfolio/{WITNESS_5MIN_DEMO_SCRIPT_TEXT_FIRST, WITNESS_CASE_STUDY_TEXT_FIRST, WITNESS_OBSERVER_BRIEF_SAMPLE, WITNESS_VISUAL_EXPERIMENT_APPENDIX}.md

### 2.4 Legacy scripts (v0.5/v0.7 paper era)
→ [archive/legacy_scripts_2026_05_15/](../archive/legacy_scripts_2026_05_15/) ([README](../archive/legacy_scripts_2026_05_15/README.md))

- scripts/{counterfactual_*, baseline_*, paper_*, world_*, hazard_scaling, chain_detection_v2, svm_comparison, audit_report, demo_spike*, demo_world_*}.py (17)
- tests/test_world/test_world_numbers_scripts.py

### 2.5 Track A directives (16 docs)
→ [archive/track_a_directives_2026_05_15/](../archive/track_a_directives_2026_05_15/)

- docs/witness_{drama_mining_plan, dm_day2_directive, data_audit_directive, gemma_labeling_directive, train_directive_{1,2}, finalize_directive{,_2}, session_handoff{,_v2}}.md
- docs/{WITNESS_DATA_AUDIT_REVISED_DIRECTIVE, WITNESS_GEMMA_LABELING_{REVIEW_TEMPLATE,STAGE1_5_DIRECTIVE}, WITNESS_GEMMA_WEAK_LABEL_DATASET_CLEANING_PLAN, taxonomy_review_prompt, CLEANUP_PLAN_2026_05_15}.md

---

## 3. 즉시 삭제 (Phase 1)

| 항목 | 갯수 |
|---|---:|
| `__pycache__/` 디렉토리 | 76 |
| `output/` 시뮬레이션 결과 캐시 | 54 파일 |
| `content/jesus/` (0 imports) | 2 파일 |
| `docs/results/_ai_hub_023_schema_stats_tmp.json` | 1 |

---

## 4. 살아남은 active 구조

```
Witness/
├── engine/                       # Skeleton + 시뮬레이션 코어 (17 modules)
│   ├── core/ rules/ simulation/ rendering/
│   ├── observer/ anchor/         # taxonomy + skeleton_output + Story Emergence
│   ├── person/ persona/ population/ world/
│   ├── action/ policies/ constraint/ io/
│
├── world/                        # World root module (engine 외부)
│
├── content/                      # Anchor + 인물별 콘텐츠 (genres archived)
│   └── universal/ anchors/ shared/
│   └── peter/ judas/ caiaphas/ crowd/ vangogh/ gauguin/ theo/ talleyrand/
│   (※ jesus/ 삭제, genres/ archived)
│
├── drama_mining/                 # Track A — AI-Hub 023
│
├── scripts/                      # Active utilities only
│   ├── labeling/                 # Track A 라벨링
│   ├── witness_train/            # Track A 학습
│   ├── narrative/                # Story Emergence + Narrative Mining
│   ├── observer/ story/ report/ skeleton/ b_direction/ data/ v3_measurement/
│   ├── data_pipeline/ audit/
│
├── tests/                        # 2,095 pass / 0 fail
├── examples/                     # 7 demo scripts
├── docs/
│   ├── CLAUDE.md DESIGN.md INDEX.md PROJECT_STRUCTURE.md HARNESS.md
│   ├── README.md ARCHIVE_POLICY.md
│   ├── DEPRECATED_TRACKS.md      # archive 4 폴더 인덱스
│   ├── CLEANUP_REPORT_2026_05_15.md (이 파일)
│   ├── results/witness_final/    # 11 정리 파일 (Track A 최종)
│   ├── plans/                    # RFC_TEMPLATE + RFC_UNIVERSAL_STORY_SEED_V1_1 + VALIDATION_REPORT_2026_05_09_FIXES
│   └── portfolio/                # 25 active portfolio docs
│
├── data/                         # gitignored (AI-Hub + processed)
├── models/                       # gitignored (KoBART/Qwen checkpoints)
└── archive/                      # legacy + 4 신규 frozen + 1 directives
```

---

## 5. 갱신된 핵심 docs

| 문서 | 변경 |
|---|---|
| [CLAUDE.md](../CLAUDE.md) | "post-cleanup 2026-05-15" 헤더 + archive 트랙 표시 + 살아남은 active 트랙 정의 |
| [docs/DEPRECATED_TRACKS.md](DEPRECATED_TRACKS.md) | 정책 변경 ("원위치 유지" → "archive 이동 완료") + 4 archive 폴더 + active 트랙 정의 |
| [docs/results/witness_final/](results/witness_final/) | Track A 최종 정리 11 파일 (변경 없음, 보존) |

---

## 6. 검증

```bash
python -m pytest -m "not slow and not archived" -q --tb=no
# 2,095 passed, 1 skipped, 133 deselected in ~90s
```

**회귀 0건**. 살아남은 코드의 동작 변경 0.

---

## 7. 남은 정리 후보 (사용자 추가 요청 시)

- `docs/story/` (100 files) — Story track 전 시대 디자인 docs
- `docs/creative/` (24 files) — variation + creative pack
- `docs/specs/` (18 files) — 다양한 spec
- `docs/persona_engine/`, `docs/world_engine/`, `docs/observer/` — engine 디자인 docs
- `data/raw_v1_archive/`, `data/external_private/` 외 `data/{annotated, labeled, b_direction, world}/` 등
- examples/demo_creative.py, examples/demo_story.py 등 (2-4 refs)

위 영역은 *broken link 다수*라 정리 시 INDEX.md 등 광범위 link rewrite 필요. **본 cleanup 범위 외**.

---

## 8. 한 줄

```
4 트랙 (Genre Adapter / Rubric / Visual / Legacy) archive 이동 완료.
docs 50% 감소 (79→29). 2,095 fast pass / 0 fail / 0 regression.
살아남은 active: Skeleton (taxonomy + universal_seed + Story Emergence) + Track A (drama mining).
```
