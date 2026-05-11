# WITNESS — Lee plan.md Phase 1-7 누적 결과 요약

**Date**: 2026-04-30
**Source**: `docs/plan.md` 7-phase 단계적 로드맵 완료 후 통합 요약
**Verdict**: **v0.1 Freeze + Visual Explorer 중심으로 v0.2 진행 (Case F-A)**
**용도**: Phase 1-7 결과를 한 doc에서 보기 — 중간 plan/review 분산되어 있던 것을 종합

---

## 0. 한 줄 요약

> **WITNESS = world simulation explorer. Phase 1-7 누적 검증 모두 success. 도트 기반 Visual Explorer가 핵심 entry, Visual + Packet + Story 3 layer 역할 정의됨, 5분 internal demo package 가능, fork decision = Visual Explorer 중심 v0.2.**

---

## 1. 7-Phase 결과 종합표

| Phase | 목표 | Case | 핵심 산출물 |
|---|---|---|---|
| 1 | v0.1 운영 정리 | (성공) | OPERATING_GUIDE + SMOKE_TEST 8/8 |
| 2 | v0.2 minimal connection | (성공) | 4 features (marker noise / agent follow / filter / range overlay) |
| 3 | Multi-anchor 최소 확장 | A3-A | vangogh_sacred 추가 |
| 4 | Browsing Pack v1 | BP-A | 3 anchor 통합 가이드 (10-12분) |
| 5 | Text/Visual 역할 재평가 | TV-A | Visual+Packet 충분, Story 선택 |
| 6 | Internal Demo Package v1 | D-A | 5분 / 3 화면 / 5 doc |
| 7 | Long-term Fork Decision | **F-A** | **Visual Explorer 중심 v0.2** |

---

## 2. 핵심 결론 정리

### 2.1 Visual / Packet / Story 3 layer 역할 (Phase 5 TV-A)

```
Visual: 세계 흐름을 먼저 보여줌 (어디를 볼지)
Packet: 왜 이 후보인지 설명 (rationale + signals + classification)
Story:  선택 출력, v0.1 필수 아님 (시연자 CLI 백업 도구)
```

→ Visual + Packet으로 *대부분 충분*. Story renderer 재개 불필요.

### 2.2 3 Entry Points (Visual Layer 역할 분리)

| Entry HTML | 역할 |
|---|---|
| `visual/explorer.html` | **Broad navigation entry** — anchor selector + view toggle + candidate panel + packet |
| `visual/dot_observer_replay.html` | **Single-run deep view** — 200-tick replay + V2 5 panel |
| `visual/dot_observer_cross_seed.html` | **Cross-seed deep view** — 5 seeds small multiples |

기존 deep view 보존 — explorer는 *기능 superset*이 아닌 *navigation superset*.

### 2.3 3 Anchor 통합 (Phase 3 A3-A)

| Anchor | 특징 | story_ready | score-3 |
|---|---|---|---|
| peter_scarcity_baseline | 격동 (1 accusation) | 5 | 5 |
| peter_scarcity_triple | 운명 분기 (3 accusations, REC 3/PARTIAL 1/SAT 1) | seed별 2-5 | seed별 5/5/1/1/4 |
| vangogh_sacred_baseline | 조용한 dynamics (sacred) | **0** | **0** |

→ 3 anchor가 *각자 다른 dynamics family*를 visual로 표현.

### 2.4 5분 데모 흐름 (Phase 6 D-A)

```
0:00-0:30  도입 (한 줄 메시지: "world simulation explorer")
0:30-2:00  화면 1 — peter_baseline (격동, 5 score-3 marker → 5 story_ready)
2:00-3:30  화면 2 — peter_triple cross-seed (REC 3 / PARTIAL 1 / SAT 1)
3:30-4:40  화면 3 — vangogh (yellow only, 다른 dynamics)
4:40-5:00  마무리 (Visual / Packet / Story 3 layer)
```

핵심 메시지 (반드시 전달):
> *"WITNESS는 텍스트 이야기 생성기가 아니라, 움직이는 세계를 도트 기반으로 관찰하고, 그 안에서 이야기 후보를 발견하는 world simulation explorer다."*

---

## 3. Case F-A 결정 (Phase 7) — Visual Explorer 중심 v0.2

### 4 Fork Option 비교 결과

| 옵션 | 자산 활용도 | 2주 선명도 | Q1-Q4 evidence |
|---|:---:|:---:|---|
| **1. Visual Explorer** | **최고** | **높음** | **4/4 압도** |
| 2. Story/IP Asset | 중 | 낮음 | 부분 |
| 3. Simulation Research | 중 | 낮음 (months) | 부분 |
| 4. Playable Prototype | **최저** | **매우 낮음** | 0 |

### 우선순위 결정 (evidence-driven)
1. **Visual Explorer 중심** — 추천 (Case F-A)
2. Simulation Research 보조 (보존, paper draft 활용)
3. Story/IP Asset 보류 (asset pack v1 보존, renderer 재개는 별도 directive)
4. Playable Prototype 장기 보류 (현재 evidence 0)

### 다음 2주 로드맵 (Lee directive §5 verbatim)

| Week | 작업 |
|---|---|
| 1 | (1) Explorer v0.2 안정화 (2) Demo guide 정리 (3) 1 anchor 추가 검토 (4) Portfolio README 초안 |
| 2 | (1) v0.2 package (2) Demo GIF/screenshot (3) Portfolio docs 정리 (4) v0.2 roadmap |

총 ~10-12시간 분산, 새 코드 ~0.

---

## 4. 강점 (확정)

- ✅ Engine integrity (1845 fast tests, ABSOLUTE Rule #1/#6 준수)
- ✅ 4 layer stack (Person + World + Story Output + Observer + Visual, additive)
- ✅ 3 anchor support (peter_baseline / peter_triple / vangogh)
- ✅ Cross-seed visualization (configuration sensitivity 시연)
- ✅ Visual + Packet complementary 검증
- ✅ Self-contained (외부 dependency 0, vanilla JS + SVG)
- ✅ Schema 무수정 7-phase 누적 (v1 + cross_seed_v1)

---

## 5. 한계 (인정)

- ⚠️ Single-seed bias (peter_baseline / vangogh seed=0 only)
- ⚠️ Sacred encoding 약함 (vangogh score-2/3 marker 0)
- ⚠️ Story panel placeholder (renderer 재개 금지 일관)
- ⚠️ Cross-seed 단일 anchor (peter_triple만)
- ⚠️ Relation/interaction candidate 부재 (v0.2 backlog)
- ⚠️ Mobile / responsive 미검증

→ 한계는 *데모 블로커 아님* (Phase 6 KNOWN_LIMITATIONS_V1 검증).

---

## 6. 동행 문서 (currently referenced)

### 6.1 Visual layer (실제 사용)
- `docs/visual/VISUAL_EXPLORER_V0_1_OPERATING_GUIDE.md` (운영 매뉴얼)
- `docs/visual/VISUAL_EXPLORER_V0_1_SMOKE_TEST.md` (자동 검증)
- `docs/visual/VISUAL_TRACK_SYNTHESIS_REVIEW.md` (4 단계 종합)
- `docs/visual/CROSS_SEED_VISUAL_VALIDATION.md` (configuration sensitivity)
- `docs/visual/ANCHOR_3_VISUAL_VALIDATION.md` (vangogh)
- `docs/visual/OBSERVER_BASED_BROWSING_PACK_V1.md` (browsing 가이드)
- `docs/visual/VISUAL_OBSERVER_INPUT_SCHEMA.md` (data schema)

### 6.2 Demo package (Phase 6)
- `docs/demo/INTERNAL_DEMO_PACKAGE_V1.md` (12 sections)
- `docs/demo/DEMO_SCRIPT_V1.md` (5분 대본 + FAQ + cheat sheet)
- `docs/demo/DEMO_RUN_CHECKLIST_V1.md` (시연 전 점검)
- `docs/demo/KNOWN_LIMITATIONS_V1.md` (9 한계)

### 6.3 Observer layer specs
- `docs/observer/WORLD_OBSERVER_LAYER_SPEC.md` (O1-O7 base)
- `docs/observer/OBSERVER_TO_STORY_PIPELINE.md` (P1-P5)
- `docs/observer/CANDIDATE_CURATION_PLAN.md` (Q1-Q4)
- `docs/observer/CANDIDATE_CURATION_VALIDATION.md` (Case A)

### 6.4 Decision / strategy
- `docs/roadmap/WITNESS_FORK_DECISION.md` (Case F-A — Phase 7)
- `docs/creative/TEXT_VISUAL_ROLE_REASSESSMENT.md` (Case TV-A — Phase 5)

### 6.5 Project meta
- `README.md` / `CLAUDE.md` / `DESIGN.md` (root)
- `docs/HARNESS.md` (H1-H8 anti-bias engineering)
- `docs/ODD_PROTOCOL.md` (Overview-Design-Details)
- `docs/CANONICAL_MANIFEST.md` (navigation)
- `docs/INDEX.md` (current docs nav)

---

## 7. Archive (historical reference, 옮겨진 자료)

다음 자료는 *작업 결과가 본 SUMMARY 또는 phase reviews에 흡수*되어 archive로 이동됨.

### 7.1 Lee directive files (root)
**위치**: `docs/archive/lee_directives_2026-04-30/`
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
- WITNESS_OBSERVER_TO_STORY_PIPELINE_DIRECTIVE.md
- WITNESS_POST_TYPE_B_EXTERNAL_GATE_DIRECTIVE.md
- WITNESS_PROJECT_STATUS_2026-04-29.md
- WITNESS_PYTEST_IMPROVEMENT_PLAN.md
- WITNESS_STORY_OUTPUT_MVP_PLAN.md
- WITNESS_STORY_OUTPUT_NEXT_STEPS.md
- WITNESS_WORLD_OBSERVER_LAYER_SPEC.md

### 7.2 Visual phase intermediate (plan / 중간 review)
**위치**: `docs/archive/visual_phases_intermediate/`
- VISUAL_EXPLORER_V0_PLAN.md (Phase 7 전 plan, V0_REVIEW에 결과)
- VISUAL_OBSERVER_V2_MINIMAL_PLAN.md (V2_MINIMAL_REVIEW에 결과)
- ANCHOR_2_VISUAL_VALIDATION_PLAN.md (ANCHOR_2_VALIDATION에 결과)
- ANCHOR_3_SELECTION_NOTE.md (ANCHOR_3_VALIDATION에 결과 포함)
- VISUAL_OBSERVER_V2_USAGE_SCENARIOS.md (USAGE_REVIEW에 답변 포함)

### 7.3 Renderer Cycle plans (Cycle 7 freeze 후 historical)
**위치**: `docs/archive/renderer_cycles_2026-04/`
- RENDERER_CYCLE_2_PLAN.md ~ RENDERER_CYCLE_7_PLAN.md (6 cycles)
- RENDERER_DIAGNOSIS_*.md / RENDERER_GATE1_V*.md (intermediate diagnostics)

→ 모든 Cycle 결과는 `docs/creative/RENDERER_CYCLES_1_TO_6_RETROSPECTIVE.md` 와 `RENDERER_FREEZE_DECISION.md`에 종합됨.

---

## 8. 전체 layer 진화 chain

```
Engine (Person + World)
    ↓ (1845 tests, ABSOLUTE Rule #1/#6)
Story Output Layer (template-guided narrative)
    ↓ (119 tests, render_story_ko)
Observer Layer Phase O1-O7 (snapshot / lens / replay / compare)
    ↓ (212 tests, 4 lens)
Pipeline Phase P1-P5 (candidate extraction)
    ↓ (35 tests, 4 extractor)
Curation Phase Q1-Q4 (3 bucket + temporal diversity + near-dup)
    ↓ (33 tests, story_ready / observation_only / low_activity_hold)
Visual Phase V0-V2 (도트 기반 single-anchor + 4 V2 features)
    ↓ (4 self-contained HTML, schema v1)
Cross-seed (multi-seed small multiples — single-seed conditioning 극복)
    ↓ (cross_seed_v1 schema, 5 seeds)
Visual Explorer v0/v0.1/v0.2 (broad navigation entry)
    ↓ (anchor selector + view toggle + candidate panel + packet)
Browsing Pack v1 (3 anchor 통합)
    ↓
Internal Demo Package v1 (5분 / 3 화면)
    ↓
Long-term Fork Decision (Case F-A — Visual Explorer 중심 v0.2)
```

각 layer freeze 가능 + additive (이전 layer 깨지 않음).

---

## 9. Lee 7-phase 모든 plan.md 금지 항목 누적 준수

전체 7 phase 동안 *추가 0건* 금지:

- ❌ React dashboard / 3D / 캐릭터 / animation / player intervention
- ❌ Story renderer 재개 (Cycle 7 freeze 유지)
- ❌ New scenario / Talleyrand scenario
- ❌ Sacred-specific metric / new bucket
- ❌ Multi-anchor 대규모 확장
- ❌ Public-facing product packaging
- ❌ Visual polish
- ❌ Complex UI refactor
- ❌ 기존 안정 파일 대규모 리팩터

---

## 10. Phase 1-7 stop rule 누적

각 phase별 stop rule (Lee plan.md §GLOBAL STOP RULE) 준수:
1. ✅ 산출물 요약 (각 phase doc에 명시)
2. ✅ 성공/실패 판정 (Case A / TV-A / BP-A / EX-A / D-A / F-A)
3. ✅ 다음 phase 진입 결정
4. ✅ 새 기능 추가 0
5. ✅ Forbidden 위반 0

---

## 11. v0.1 → v0.2 전환점

**v0.1** (현재 freeze): 7-phase 누적 결과
- Visual Explorer working
- Browsing Pack v1 working
- Internal Demo Package v1 working
- Fork decision Case F-A

**v0.2** (다음, Lee directive 시 진행):
- Week 1-2 작업 (위 §3 표)
- Visual Explorer 안정화 + portfolio 초안 + GIF/screenshot
- 새 기능 0, *기존 자산 packaging* 위주

---

## 12. 한 줄 요약 (재)

> **Phase 1-7 누적 모든 success. v0.1 Freeze + Visual Explorer 중심 v0.2 (Case F-A). Visual + Packet 충분, Story 선택. 5분 internal demo 가능, 3 anchor 통합, configuration sensitivity 시연. 코드 0 변경 (Lee 모든 금지 일관).**

---

**Versioning**: v1 (this summary) — 2026-04-30 Phase 1-7 완료 종합.
