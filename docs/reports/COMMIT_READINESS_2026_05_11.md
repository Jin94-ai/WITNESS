# WITNESS Commit Readiness Report — 2026-05-11

> **Status**: Phase 3.05 / Phase 3.1 frontier closed. 174 uncommitted changes accumulated across ~70 autonomous-mode cycles (2026-05-11 session). This report categorizes all changes, identifies should-not-commit items, recommends a commit split, and lists remaining blockers before Phase 3.0 Actual Mini Pilot entry.
>
> **Per directive** [WITNESS_2026_05_11_FREEZE_AND_NEXT_STEPS.md](../WITNESS_2026_05_11_FREEZE_AND_NEXT_STEPS.md): this freeze precedes Phase 3.0 Actual Mini Pilot. No new feature work.

---

## 1. Summary

| Metric | Value |
|---|---|
| Total uncommitted entries | **174** (M=33 / D=23 / ??=118) |
| Fast test suite | **2,648 pass / 14 skipped / 0 regression** |
| Lessons added this session | **L82–L88** (7 new) |
| Rubric directive cycles | **29** (P0/P1/P2 + Result-1~11 + cycle 16-29) |
| Doc-currency cycles | **45-51, 53, 55, 60** (within meta-arc 44-61) |
| Pause-fresh-review meta-arc | **cycle 44-61** (L88 empirically validated 2x) |
| Total session cycles | **~70** (cycle 1-69 + this freeze cycle) |

---

## 2. Major Assets Added

### 2.1 Rubric Engine (Phase 3.05, cycle 1-29)
- `engine/rubric/` — 6 critic modules + `rubric_evaluator.py` (8-step flowchart)
- 4-Axis Discovery **Candidate Classifier** (NOT "Evaluator" — see §5 naming guard)
- All thresholds marked `uncalibrated_phase3_placeholder`
- Rule #14 enforced (rubric not imported by neural trainer)
- No scalar aggregation (4 independent sub-reports preserved)

### 2.2 Rubric CLI / fixtures / demo reports (cycle 17-28)
- `scripts/rubric/run_rubric.py` (records → RubricReport JSON + markdown)
- `scripts/rubric/trace_to_records.py` (trace JSONL → records adapter)
- `scripts/rubric/build_ensemble_html.py` (3 ensembles → visualization HTML)
- 14 fixtures in `tests/fixtures/rubric_demo/`
- 22+ portfolio reports in `docs/portfolio/demo_rubric/`

### 2.3 Phase 3.1 Target A/B/C (cycle 17-19, 25, 29-31, 40)
- **Target A** (`flesh_baseline.py`) — seed × profile fit
- **Target B** (`episode_intensity.py`) — episode × profile intensity (fixture-only deploy cycle 40)
- **Target C** (`adaptation_recommendation.py`, cycle 17-19) — seed → ranked top-K genres
- **Plan §24 Step 2 bridge** (`apply_top_recommendation.py`, cycle 25)
- **Plan §29 verifier** (`verify_phase3_1_acceptance.py`, cycle 29-31)

### 2.4 Doc-currency updates (cycle 32-51, 53, 55, 60)
- CLAUDE.md / DESIGN.md / README.md / PROJECT_STRUCTURE.md updated
- Operating Guide §2 + §4.6 + §9 Deploy Status Matrix
- 9 portfolio docs updated (resume / cover letter / interview / demo guide / 등)

### 2.5 Doc-reality automation (cycle 33-38, 41-42, 47)
- `_DOC_REALITY_REGISTRY` in `tests/test_skeleton/test_phase3_1_baseline.py`
- 7 doc-reality registry entries
- Multi-doc regex link checker (`test_all_markdown_internal_links_resolve`)
- 130 internal markdown links auto-verified across `docs/portfolio/` + `docs/plans/`, 0 broken

### 2.6 Lessons L82-L88
- **L82**: 결과물 진화 4단계 (engine → CLI → demo → N-case)
- **L83**: ensemble 5단계 확장
- **L84**: engine-only stranded pattern
- **L85**: 3 instances → systemic, generic detector
- **L86**: doc statements as machine-checkable invariants
- **L87**: registry + regex dual approach
- **L88**: pause→fresh-review pattern + saturation curve

---

## 3. Known Non-Claims

The session work explicitly avoids the following claims:

- **No "Discovery proof"** — Rubric is a *Candidate Classifier* / triage tool. See §5 naming guard.
- **No "data-validated" claims for rubric ensemble HTML** — fixture/synthetic based. Add stress-test banner per §6.
- **No "real-world discovery validation"** — only Phase 3.0 pilot can claim that.
- **No threshold calibration** — all thresholds are `uncalibrated_phase3_placeholder`.
- **No ML training** — Rule #14 enforced via test.
- **No external fetch / LLM API** — all current work is local + reproducible.

---

## 4. Not-Yet-Done Items

- Phase 3.0 Mini Pilot (10 real synopses) — *gated on user approval 5+2건*
- Calibration phase (Phase 5+) — *requires real trajectory ensemble*
- LLM annotation Mode B/C — Mode A (manual) only currently
- Visual track polish — *frozen since 2026-05-06* (intentional)

---

## 5. Rubric Naming Guard (per directive §5)

**Allowed terms** in commit messages + future docs:
- Discovery Candidate Classifier
- candidate classifier
- triage layer
- audit rubric
- non-training evaluator

**Forbidden terms**:
- Discovery Evaluator
- Discovery Validator
- Discovery Judge
- Meaning Discovery Score
- final discovery proof

**Reason**: rubric is *audit / classification layer*, not a discovery proof apparatus.

---

## 6. Portfolio Stress-Test Disclaimer

Rubric ensemble HTML shows promising numbers:
- cross_scenario 19/20
- multi_agent 14/15
- multi_seed 4/5

But these are **fixture/synthetic-based**, not actual data validation. Banner to add in `docs/portfolio/demo_rubric/README.md` + `ensemble_visualization.html`:

```text
This is a rubric stress-test surface using controlled fixtures,
not a claim of validated real-world discovery.
```

```text
이 데모는 통제 fixture 기반 rubric stress-test이며,
실제 데이터 기반 discovery 검증 결과가 아니다.
```

---

## 7. Recommended Commit Split

Per directive §4 (4 minimum, 6 recommended):

### Commit 1 — Rubric engine + tests
```text
engine/rubric/ (all files, including new context_break / population / reference_loader / scene_response / world critics)
tests/test_rubric/ (new + modified)
tests/test_skeleton/test_phase3_1_baseline.py (rubric-related sections)
```
Message theme: "feat(rubric): 4-Axis Discovery Candidate Classifier + 6 critic modules + 124+ tests"

### Commit 2 — Rubric CLI + fixtures + demo reports
```text
scripts/rubric/ (all files)
tests/fixtures/rubric_demo/ (14 fixtures)
docs/portfolio/demo_rubric/ (22+ reports including ensemble_visualization.html)
```
Message theme: "feat(rubric): CLI runner + ensemble HTML + 14 fixtures + 22 portfolio reports"

### Commit 3 — Phase 3.1 Target A/B/C assets
```text
engine/observer/{flesh_baseline,episode_intensity,adaptation_recommendation,genre_profile}.py
scripts/narrative/{run_,build_}* for Target A/C
scripts/annotation/{run_,build_}* for Target B
scripts/narrative/apply_top_recommendation.py (Plan §24 bridge)
scripts/data/verify_phase3_1_acceptance.py (Plan §29 verifier)
docs/portfolio/demo_flesh_baseline/
docs/portfolio/demo_adaptation_recommendation/
docs/portfolio/demo_episode_intensity/ (fixture-only deploy)
```
Message theme: "feat(phase-3.1): Target A/B/C portfolio assets + §24 bridge + §29 verifier"

### Commit 4 — Doc-currency updates
```text
CLAUDE.md / DESIGN.md / README.md / docs/PROJECT_STRUCTURE.md (modified)
docs/INDEX.md / ARCHIVE_POLICY.md / CANONICAL_MANIFEST.md / etc (new)
docs/plans/PHASE_3_0_PIPELINE_OPERATING_GUIDE.md (matrix updates)
docs/portfolio/README.md + FLESH_BASELINE_DEMO.md + GENRE_ADAPTER_DEMO.md (etc)
docs/portfolio/APPLICATION_RESUME_BULLETS.md / COVER_LETTER_SNIPPETS.md / INTERVIEW_STORY_BANK.md / DEMO_GUIDE_FOR_PORTFOLIO.md / VERBAL_DEMO_SCRIPT_5MIN.md
docs/portfolio/PORTFOLIO_README_DRAFT.md / TARGET_ROLES_AND_POSITIONING.md / PORTFOLIO_REPACK_PLAN.md / PORTFOLIO_ASSET_CHECKLIST.md / PORTFOLIO_PUBLIC_RELEASE_RISK_MEMO.md / ARCHITECTURE_FOR_PORTFOLIO.md
```
Message theme: "docs: phase 3.05 / 3.1 doc-currency sync (15 docs across CLAUDE/DESIGN/README/portfolio)"

### Commit 5 — Doc-reality automation
```text
tests/test_skeleton/test_phase3_1_baseline.py (registry + multi-doc link checker tests)
tests/test_skeleton/test_phase6_renderer.py (CLAUDE.md framing test, if separately needed)
```
Message theme: "test: doc-reality registry (7 docs) + multi-doc broken-link checker (130 links 0 broken)"

### Commit 6 — Lessons L82-L88 + meta docs
```text
lessons.md (L82-L88 entries + saturation curve refinement)
progress.md (cycle entries — though this gets touched in many commits; may need to split)
memory/* (project_witness_rubric_directive.md + MEMORY.md, if tracked)
docs/witness_rubric_design.md (Phase 3.05 design doc)
docs/WITNESS_V3_RUBRIC_DESIGN_REVIEW.md (rubric review doc)
docs/WITNESS_2026_05_11_FREEZE_AND_NEXT_STEPS.md (this directive)
```
Message theme: "docs(meta): L82-L88 lessons + rubric design + review + freeze directive"

### Optional commit 7 — Deleted obsolete docs
```text
docs/person/DATA_PIPELINE_v*.md (15 files deleted)
docs/world/SPIKE_*.md (6 files deleted, frozen visual track)
docs/session-prompts.md
docs/witness_previous_experiments_reevaluation.md
```
Message theme: "chore: remove obsolete person/world spike docs (visual track frozen, person v3 archived)"

---

## 8. Files That Should NOT Be Committed

Per `.gitignore` + sensitivity check:

### 8.1 Already gitignored (no action needed)
- `archive/*` (line 102) — local-only legacy
- `data/*` (line 84) — reproducible generated data, except whitelisted public-safe files
- `data/external_private/` (line 110) — private raw synopsis
- `data/annotation/phase3_pilot/per_annotator/` (line 111)
- `data/annotation/phase3_pilot/synopsis_cache/` (line 112)
- `data/annotation/phase3_pilot/annotation_inputs/` (line 114)
- `data/annotation/phase3_pilot/annotation_outputs/` (line 115)
- `data/annotation/phase3_pilot/validated/` (line 116)
- `data/annotation/phase3_pilot/normalized_synopsis.jsonl` (line 118)
- `data/llm_keys/` (line 124)
- `data/llm_call_logs/` (line 125)
- `models/` (gitignored via `data/*` if under data/, or no model files present)
- `visual/` (5 HTML visual demos, frozen — appear untracked but visual track is frozen per CLAUDE.md, no need to commit)

### 8.2 Should remain untracked (manual decision)
- `docs/archive/*` (Phase 2.x legacy moved to archive subdir, gitignored intentionally)
- `models/` (no current model artifacts — safe to leave untracked)
- `visual/` (frozen sub-tracks: pixel_event_playback.html / world_flow_observer.html / etc — frozen per CLAUDE.md line "Visual track: frozen 2026-05-06". If commit needed, document freeze status explicitly first)

### 8.3 Should be verified before commit
- **All `?? docs/*.md` plan files**: confirm none contain private synopsis text or external content
- **`content/peter/v3/profile.json` + `content/judas/v3/profile.json` + `content/vangogh/v3/`**: confirm no copyrighted source material
- **`docs/person/v3_measurement/peter_v3_ensemble_N10.json` (modified) + `docs/person/v3_measurement/vangogh_v3_seed0_ticks30.json` (untracked)**: large measurement data — verify size + content

---

## 9. Repository Safety Checklist

Before any commit:

- [ ] No raw synopsis in tracked files (grep `synopsis_text` across staged area)
- [ ] No LLM API keys or tokens in any file
- [ ] No private email / personal data
- [ ] All portfolio demos prominently labeled with current status (prep / fixture-only / actual)
- [ ] Rubric outputs labeled as candidate classification (not "discovery proof")
- [ ] `audit.raw_text_used = False` in all flesh_baseline / adaptation_recommendation / episode_intensity outputs
- [ ] `model.trained = False` everywhere in current state

---

## 10. Remaining Blockers Before Phase 3.0 Actual Mini Pilot

Per directive §10, before pilot start:

1. ☐ This commit readiness report reviewed by Lee
2. ☑ Commit split executed (4-6 commits per §7) — *cycle 79 완료* (7 commits + `git status` clean / 2,648 fast pass / 0 regression; 상세 §12)
3. ☑ Phase 3.0 Actual Pilot Boundary doc created ([PHASE_3_0_ACTUAL_PILOT_BOUNDARY.md](../plans/PHASE_3_0_ACTUAL_PILOT_BOUNDARY.md)) — *cycle 70 완료*
4. ☐ All 12 approval items checked off in [PHASE_3_0_APPROVAL_CHECKLIST.md](../plans/PHASE_3_0_APPROVAL_CHECKLIST.md)
5. ☐ 10 real synopses provided by Lee (private path under `data/external_private/`)
6. ☐ ToS / robots.txt review complete for any source candidates
7. ☑ Rubric portfolio HTML banner added (fixture stress-test disclaimer, §6 of this doc) — *cycle 71 완료* ([demo_rubric/README.md](../portfolio/demo_rubric/README.md) top + [ensemble_visualization.html](../portfolio/demo_rubric/ensemble_visualization.html) Non-Claims 위)

Until items 1, 4 (Lee-action items) are done, **no Phase 3.0 actual work proceeds**. Items 5-6 are Phase 3.0 pilot 진입 직전 별도 단계. *Push to origin/main은 Lee 별도 결정 (`git push` 미실행).*

---

## 11. Test Suite State

```bash
$ python -m pytest -m "not slow and not archived" -q --tb=no
2,648 passed, 14 skipped, 133 deselected in ~122s
```

Skipped 14 = `tests/test_rubric/test_reference_set.py` (waits for external `data/reference/witness_trajectories_45.json`, Phase G Step G1 — intentional).

---

## 11.1 Uncommitted Risk Note (per directive §7.3)

본 branch가 안전한 commit 후보임을 6 axis 로 보증:

### 11.1.1 Why this branch is safe to commit
- All 174 changes 추적 가능 (M/D/?? 명확)
- 2,648 fast tests pass / 0 regression (clean baseline)
- Doc-reality registry로 *향후 stale 자동 차단* (130 internal links 0 broken)
- Rubric "Candidate Classifier" 명명 일관 (no "Evaluator" / "Validator" / "Judge" 누설)
- Fixture stress-test disclaimer 추가 (cycle 71, demo_rubric README + ensemble_visualization.html)
- 모든 portfolio demo가 `data_source` 명시 (rulebook_only / phase3_pilot / fixture-only)

### 11.1.2 Which files are *generated* (script output / can be reproduced)
- `data/narrative/phase3_1_demo/*.json` (run_flesh_baseline + run_adaptation_recommendation + apply_top_recommendation 출력)
- `docs/portfolio/demo_flesh_baseline/*` (build_flesh_baseline_demo 출력)
- `docs/portfolio/demo_adaptation_recommendation/*` (build_adaptation_recommendation_demo 출력)
- `docs/portfolio/demo_episode_intensity/*` (build_episode_intensity_demo --fixture-only 출력)
- `docs/portfolio/demo_rubric/*.{json,md}` (run_rubric.py 출력 across 8 fixtures + alignment + axis-isolated + ensembles)
- `docs/portfolio/demo_rubric/ensemble_visualization.html` (build_ensemble_html.py 출력)

→ 모두 *script 재실행*으로 재생성 가능. commit 후에도 reproducibility 보장.

### 11.1.3 Which files are *source* (engine logic, schema, tests)
- `engine/rubric/*.py` (6 critic + rubric_evaluator + __init__)
- `engine/observer/adaptation_recommendation.py`
- `engine/observer/{flesh_baseline,episode_intensity,genre_profile}.py` (modified)
- `engine/{action,core,person,rules,world}/*.py` (modified — cycle 16 CausalCritic 외 minor changes)
- `tests/test_rubric/*.py` (new + modified)
- `tests/test_skeleton/test_phase3_1_baseline.py` (registry test + L86 patterns)
- `scripts/rubric/*.py` + `scripts/narrative/*.py` (new) + `scripts/annotation/*.py` (new) + `scripts/data/verify_phase3_1_acceptance.py` (new)

### 11.1.4 Which files are *portfolio artifacts* (reviewer-facing deploys)
- `docs/portfolio/demo_rubric/` (cycle 19/22/23/26/27/28 산출)
- `docs/portfolio/demo_adaptation_recommendation/` (cycle 19)
- `docs/portfolio/demo_episode_intensity/` (cycle 40 fixture-only)
- `docs/portfolio/demo_flesh_baseline/` (existing, updated)
- `docs/portfolio/README.md` + `FLESH_BASELINE_DEMO.md` + `INTERVIEW_STORY_BANK.md` + 등 (recruiter-facing, cycle 48/50/51)

### 11.1.5 Which files should NOT be committed
→ §8 참조. 요약:
- `archive/` (gitignored)
- `data/external_private/` (gitignored, pre-emptive)
- `data/annotation/phase3_pilot/per_annotator/` + `annotation_inputs/` + `outputs/` + `validated/` + `normalized_synopsis.jsonl` (gitignored)
- `data/llm_keys/` + `data/llm_call_logs/` (gitignored)
- `models/` (no model artifacts, safe to leave untracked)
- `visual/` (frozen 2026-05-06, 5 HTML files — *Lee 결정* 필요 if commit)

### 11.1.6 Private raw synopsis paths — gitignored 확인
- ✅ `.gitignore` line 110 `data/external_private/` — confirmed pre-emptive (path 미존재이지만 보호됨)
- ✅ `.gitignore` line 114-118 `data/annotation/phase3_pilot/{annotation_inputs,annotation_outputs,validated,normalized_synopsis.jsonl}` — synopsis_text 포함 가능 영역 모두 gitignored
- ✅ `audit.raw_text_used = False` 모든 deployed-prep / fixture-only output에 검증됨
- ✅ Test `test_deployed_episode_intensity_demo_has_fixture_only_banner`이 `synopsis_text not in html` 강제

→ **현재 working tree에 raw synopsis text 0건** 확인. Phase 3.0 actual pilot 시작 시 *Lee 본인이 수동 입력*하는 데이터는 `data/external_private/` 또는 `data/annotation/phase3_pilot/annotation_outputs/`로 흘러가며 gitignored 보호.

---

## 12. Conclusion

WITNESS 프로젝트는 **구조 개발 단계를 넘어섰다**. Phase 3.05 정직성 + Phase 3.1 baseline + Rubric directive 모두 *coded + tested + documented + portfolio-deployed*. doc-reality automation으로 *향후 stale 자동 방지*. lessons L82-L88로 *프로세스 자체*를 자동화 가능한 패턴으로 정리.

다음 단계는 **추가 구현이 아니라 commit freeze → Phase 3.0 Actual Mini Pilot 진입**.

이 보고서가 Phase 3.0 진입 전 *마지막 audit 단계*다.

---

## 12.1 Commit Split Execution Record (cycle 79, 2026-05-11)

Lee 명시 승인 후 7 commits 실행 (`git log --oneline -7`):

```
ede3677  chore: remove obsolete person v3 / world spike / session-prompt docs
cfa25cb  docs(meta): L82-L88 lessons + plan / directive docs + .gitignore safety
d4baa80  docs: phase 3.05/3.1 doc-currency sync + portfolio + reference docs
3082e21  feat(engine): persona / population / world extras + v3 dynamics + examples + scripts
3bae241  feat(phase-3.1): Target A/B/C baselines + Genre Adapter + supporting infra
bca24eb  feat(rubric): CLI runner + ensemble HTML + 14 fixtures + 22+ portfolio reports
246bee3  feat(rubric): 4-Axis Discovery Candidate Classifier engine + 124+ tests
```

| Commit | 변경 규모 | 종류 | 비고 |
|---|---|---|---|
| 1 | 16 files / +4274 -258 | rubric engine + 124+ tests | §7 Commit 1 |
| 2 | 55 files | rubric CLI + 14 fixtures + 22+ portfolio reports | §7 Commit 2 |
| 3 | 168 files | Phase 3.1 Target A/B/C + Genre Adapter + engine/observer/ + scripts/{narrative,annotation,data,skeleton}/ + content/{anchors,genres,universal}/ + portfolio demos | §7 Commit 3 |
| 4 | 145 files | engine {anchor,persona,population,world/*}/ + content/{peter,judas,vangogh}/v3/ + examples + scripts {observer,story,report,b_direction,visual,v3_measurement}/ + tests {persona,population,report,story,visual,world_process}/ | §7 미정의 — 보강 commit |
| 5 | 633 files | doc-currency (CLAUDE.md / DESIGN.md / README.md / docs/INDEX.md / portfolio package 20+ + reference + spec + layer docs + docs/archive/) | §7 Commit 4 |
| 6 | 71 files | lessons L82-L88 + plan/directive docs + .gitignore safety (models/+visual/) + tests/fixtures/annotation_public_safe/ + archive/README.md | §7 Commit 5+6 통합 |
| 7 | 23 deletes | obsolete person v3 / world spike / session-prompts | §7 Optional Commit 7 |

검증:
- ✅ `git status`: working tree clean (commit 직후)
- ✅ `git log --oneline`: 7 commits ahead of origin/main
- ✅ `pytest -m "not slow and not archived" -q --tb=no`: **2,648 passed / 14 skipped / 0 regression** (166s)
- ✅ models/, visual/, archive/*, data/external_private/*, data/llm_keys/, data/llm_call_logs/ → 미커밋 확인
- ✅ raw synopsis text 노출 0 / LLM API key 노출 0 / 작품명 익명화 (title_a/title_b) 유지

**Note**: §7 권장 6 commits는 *narrow* 분류였으나 실제 174 top-level 변경 외 engine/observer/, content/, scripts/, tests/ 등의 broader infrastructure도 untracked였음 — Commit 4 (engine misc + content + scripts misc)로 추가 분리. Lee directive *"4-6 commit"* 정신 유지 (7 = 6 + optional delete).

Push to origin/main은 **Lee 별도 결정**. Claude 자동 push 0.
