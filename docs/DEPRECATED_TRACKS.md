# Archived Tracks (2026-05-15 cleanup)

> **2026-05-15 update**: 이전 정책 "원위치 유지" → **archive로 물리적 이동 완료**.
> Lee 결정 (2026-05-15): "필요없는 문서/파일/폴더 정리, 버려진 코드는 기록만 남기고 삭제, 엔진→Flesh까지 깔끔하게."

---

## 1. Archived 폴더 (4개)

| 폴더 | 사유 | README |
|---|---|---|
| `archive/frozen_flesh_adapter_2026_05_15/` | Genre Adapter Track (Flesh ① Rule-based MVP) — Phase 2.75/2.8/2.9/3.0/3.05/3.1 | [README](../archive/frozen_flesh_adapter_2026_05_15/README.md) |
| `archive/frozen_rubric_2026_05_15/` | Discovery Candidate Classifier — 4-Axis 8-step flowchart, 124+ tests, 22+ portfolio reports | [README](../archive/frozen_rubric_2026_05_15/README.md) |
| `archive/frozen_visual_2026_05_15/` | Visual Track (PSD / PEP / WFO 등 5 sub-track) — 2026-05-06 freeze | [README](../archive/frozen_visual_2026_05_15/README.md) |
| `archive/legacy_scripts_2026_05_15/` | v0.5 / v0.7 paper era scripts (17 .py) | [README](../archive/legacy_scripts_2026_05_15/README.md) |

기존 archived (그대로):
- `archive/data_legacy/` — 42MB legacy data
- `archive/b_direction_legacy/` — Branch B/C era
- `archive/output_legacy/` + `archive/outputs_legacy/` — 시뮬레이션 결과
- `archive/track_a_pivot_2026_05_12/` — Track A pivot 시 archived

---

## 2. Active (보존)

### 2.1 Engine core (foundation)

```
engine/core/           # AgentState, HazardFunction, TriggerEngine, world
engine/rules/          # 5 rule modules
engine/simulation/     # SimulationWorld, BatchRunner, POM, statistics
engine/rendering/      # narrator, trace_emitter, player_view, trace_narrator
engine/observer/       # taxonomy + skeleton output + universal_seed (※ genre_*/flesh_baseline/episode_intensity/adaptation_recommendation archived)
engine/anchor/         # AnchorRegistry + universal_seed_renderer
engine/person/         # 7 persona modules
engine/persona/        # 4 modules
engine/population/     # 5 modules
engine/world/          # 5 modules
engine/action/         # 3 modules
engine/policies/       # 2 modules
engine/constraint/     # 3 modules
engine/io/             # 3 modules
```

### 2.2 World root (engine 외부)

```
world/                 # 10 subdirs (agents, core, economy, environment,
                       #             factions, intervention, politics,
                       #             simulation, social, space)
```

### 2.3 Track A — Drama Mining

```
drama_mining/          # AI-Hub 023 loader + preprocess + split
scripts/labeling/      # Stage 1-3 Gemma labeling + repair + taxonomy_review
scripts/witness_train/ # Stage 1/2 KoBART + Qwen LoRA + eval
data/processed/witness_v{1,2}/  # gitignored
models/                # gitignored (KoBART checkpoints + Qwen LoRA adapter)
docs/results/witness_final/     # 11 정리 파일
docs/results/witness_train_v{1,2}/  # eval reports
docs/results/gemma_labeling_poc/    # stage summaries
docs/results/taxonomy_review/       # 6 항목 + SUMMARY
data/external_private/gemma_review/ # gitignored (private jsonl)
```

### 2.4 Story Emergence + Narrative Mining

```
engine/observer/{moment, thread, narrative_opportunity, ...}.py
scripts/narrative/{aggregate_human_pick, build_cross_seed_patterns,
                   build_mining_console, build_moments, build_story_*,
                   demo_life_arc_seed_diversity, export_narrative_opportunities,
                   run_life_arc_demo}.py
scripts/observer/ scripts/story/ scripts/report/ scripts/skeleton/
tests/test_narrative/ tests/test_observer/ tests/test_story/
content/{universal, anchors, peter, judas, caiaphas, crowd, vangogh,
         gauguin, theo, talleyrand, shared}
```

### 2.5 Governance

```
docs/plans/RFC_TEMPLATE.md + RFC_UNIVERSAL_STORY_SEED_V1_1.md
docs/plans/VALIDATION_REPORT_2026_05_09_FIXES.md
docs/HARNESS.md (H1-H8)
lessons.md (L1-L88)
```

---

## 3. 정책 (변경됨)

```
2026-05-12 (old): "원위치 유지 + import path 변경 금지"
2026-05-15 (new): "archive로 물리 이동 + tests 같이 이동 + import 끊김 수용"
```

**사유**: Track A 종결 후 *"엔진→Flesh까지 깔끔하게 이어질 수 있도록"* 정리. 살아남은 engine은 Skeleton (taxonomy + universal_seed + anchor)과 Story Emergence + Drama Mining (Track A) 두 갈래만.

---

## 4. 테스트 상태

| 시점 | fast pass | 비고 |
|---|---:|---|
| 2026-05-11 freeze (cycle 79) | 2,648 | 174 uncommitted commit split |
| Track A stage 2.2 후 | 2,693 | +45 (drama_mining tests) |
| **2026-05-15 cleanup 후** | **2,095** | -598 (archived tests 포함) |

---

## 5. 한 줄

```
Genre Adapter / Rubric / Visual / Legacy scripts 4 트랙 archive 이동 완료.
살아남은 active: Skeleton (taxonomy + universal_seed) + Story Emergence + Track A drama mining.
2,095 fast pass / 0 fail / 0 regression.
```
