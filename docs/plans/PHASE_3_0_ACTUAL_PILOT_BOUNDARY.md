# Phase 3.0 Actual Mini Pilot — Boundary Document

> **Per directive** [WITNESS_2026_05_11_FREEZE_AND_NEXT_STEPS.md](../WITNESS_2026_05_11_FREEZE_AND_NEXT_STEPS.md) §7.2.
>
> 이 문서는 **Phase 3.0 Actual Mini Pilot**의 *범위와 금지사항*을 명시한다. prep / fixture / actual 결과물이 섞이지 않게 하기 위한 경계 정의.

---

## 1. Scope Definition

Phase 3.0 Actual Mini Pilot은 **10개의 실제 회차 줄거리 (synopses)**를 Mode A (manual LLM annotation)로 처리하는 *단일 통과 실험*이다.

```text
입력:  10 episode synopsis (Lee 제공, private, gitignored)
처리:  manual LLM annotation → strict validation → feature matrix → reliability report
출력:  reliability.json + feature_matrix.csv + flesh_baseline_output.json (data-driven mode)
판정:  Phase 3.1 GO / NO-GO (≥4 KEEP feature)
```

---

## 2. Allowed Activities

### 2.1 Data ingestion (Lee 직접 수동)
- ✅ 10 episode synopsis (TitleA × 5 + TitleB × 5 = 10)
- ✅ Private file path: `data/external_private/synopsis_raw/`
- ✅ Lee 본인이 직접 type / paste / load — *자동 fetch 0*

### 2.2 Annotation (Mode A — manual LLM)
- ✅ `scripts/data/build_annotation_inputs.py` 로 task JSON 생성
- ✅ Lee 본인이 외부 LLM에 *수동 prompt → 응답 복사 → JSON 저장*
- ✅ Per-annotator output: `data/annotation/phase3_pilot/annotation_outputs/` (gitignored)
- ✅ 최소 2명 annotator 권장 (reliability r 계산용)

### 2.3 Validation (strict)
- ✅ `scripts/annotation/validate_annotation_outputs.py --strict --synopsis <raw>`
- ✅ Hallucination quote check < 5% (실패 시 STOP)
- ✅ Schema validation (`episode_annotation_v1`)

### 2.4 Feature matrix + reliability
- ✅ `scripts/annotation/build_feature_matrix.py` (long-form CSV)
- ✅ `scripts/annotation/build_reliability_report.py` (Pearson r per feature → KEEP/REVISE/DROP/NEEDS_MORE_DATA)
- ✅ Phase 3.1 GO 임계: summary.keep ≥ 4

### 2.5 Baseline regeneration (Phase 3.1 data-driven mode)
- ✅ `scripts/narrative/build_genre_profiles.py --reliability <rel.json>` (KEEP feature 기반)
- ✅ `scripts/narrative/run_flesh_baseline.py` (annotation_blended mode 발동)
- ✅ `scripts/annotation/run_episode_intensity.py` (실제 데이터로)
- ✅ `scripts/data/verify_phase3_1_acceptance.py --reliability-report <rel.json>` (§29.1 PASS 검증)

### 2.6 Documentation
- ✅ `docs/plans/PHASE_3_0_DATA_PILOT_REPORT.md` 작성 (pilot 종료 후)
- ✅ `docs/plans/PHASE_3_0_FEATURE_RELIABILITY_REPORT.md` 작성
- ✅ `docs/plans/PHASE_3_0_DATA_CARD.md` 갱신
- ✅ Portfolio demos를 *data-driven mode*로 재생성 (cycle 40 fixture-only → actual)

---

## 3. Forbidden Activities

### 3.1 External fetch (절대 금지)
- ❌ HTTP / HTTPS fetch
- ❌ web scraping
- ❌ `requests.get` / `urllib.request.urlopen`
- ❌ Wikipedia / TVN / Netflix / 등 외부 source 자동 다운로드

이유: Plan §7.2 ToS / robots.txt review 미완료 시점에서 외부 fetch는 *법적 / 라이선스 위험*. Mode A는 *Lee 직접 수동*이 핵심.

### 3.2 LLM API call (절대 금지)
- ❌ OpenAI API / Anthropic API / Google API 호출
- ❌ `import openai` / `import anthropic` / 등
- ❌ HTTP POST to LLM endpoint

이유: 비용 발생 + Plan §14.2 *Mode C는 후순위* 명시. Mode A에서는 Lee가 수동으로 LLM과 대화 후 응답을 *복사하여 저장*.

### 3.3 ML training (절대 금지)
- ❌ PyTorch / TensorFlow training loop
- ❌ `model.fit()` / `optimizer.step()` / 등
- ❌ Fine-tuning
- ❌ Gradient computation on rubric outputs (**Rule #14 강제**)

이유: Phase 3.1 prep은 *No-ML weighted score baseline*. Phase 3.2+ 에서 ML 진입 결정.

### 3.4 Public exposure of raw synopsis (절대 금지)
- ❌ git commit raw synopsis text
- ❌ public portfolio HTML에 synopsis_text 노출
- ❌ `data/annotation/phase3_pilot/normalized_synopsis.jsonl` git tracked

이유: 저작권 / 라이선스 위험. `.gitignore` line 110-118 강제. `audit.raw_text_used = False` invariant 유지.

### 3.5 Scope expansion (제한)
- ❌ 10 episode 초과 — *Mini* pilot은 정확히 10개
- ❌ Fixture 결과를 actual 결과로 표시 — 명시적 banner 필수
- ❌ Phase 3.0 actual 결과를 prep 결과처럼 banner 표시 (혹은 그 역)

이유: prep / fixture / actual 결과물 *분류 혼동 방지*. Operating Guide §9 Deploy Status Matrix 5 카테고리 (deployed-prep / deployed-data / script-only / fixture-only / generated-after-approval) 일관 적용.

### 3.6 Calibration (yet)
- ❌ Threshold 보정 (Phase 5+ 대기)
- ❌ `uncalibrated_phase3_placeholder` 제거 / 변경

이유: Phase 5 calibration은 *실측 trajectory ensemble 수집 후*. 현재는 *fake precision* 위험.

---

## 4. Pilot 진입 사전 조건

다음 모두 ✅ 되어야 pilot 시작:

1. ✅ [COMMIT_READINESS_2026_05_11.md](../reports/COMMIT_READINESS_2026_05_11.md) 검토 완료
2. ✅ 174 uncommitted → 6 commit split 완료
3. ✅ [PHASE_3_0_APPROVAL_CHECKLIST.md](PHASE_3_0_APPROVAL_CHECKLIST.md) 12 step 모두 ☑
4. ✅ 10 synopsis 준비 완료 (Lee, private path)
5. ✅ ToS / robots.txt review 완료 (관련 source 사용 시)
6. ✅ Rubric portfolio HTML "stress-test fixture" banner 추가

---

## 5. Pilot 진행 시 9-Step Operating Guide

[PHASE_3_0_PIPELINE_OPERATING_GUIDE.md](PHASE_3_0_PIPELINE_OPERATING_GUIDE.md) §4 Mode A 9-step 그대로 적용:

1. Step 1 — raw synopsis ingest (Lee 수동, private path)
2. Step 2 — `normalize_synopsis.py` → normalized JSONL
3. Step 3 — `validate_synopsis_dataset.py` schema check
4. Step 4 — `build_annotation_inputs.py` → LLM task JSON
5. Step 5 — Manual annotation (Lee → 외부 LLM → 응답 저장)
6. Step 6 — `validate_annotation_outputs.py --strict --synopsis <raw>` (hallucination check)
7. Step 7 — `build_feature_matrix.py` → CSV
8. Step 8 — `build_reliability_report.py` → r per feature
9. Step 9 — Phase 3.1 GO/NO-GO 판정 (summary.keep ≥ 4?)

---

## 6. Pilot 종료 후 Phase 3.1 갱신

Pilot 통과 (summary.keep ≥ 4) 시:

```bash
# 1. Profiles 재생성 (KEEP feature 기반)
python scripts/narrative/build_genre_profiles.py \
    --reliability data/annotation/phase3_pilot/reports/reliability.json \
    --genres korean_morning_melodrama japanese_quiet_drama \
    --output data/narrative/phase3_1_pilot/genre_profiles.json

# 2. Flesh baseline (annotation_blended mode)
python scripts/narrative/run_flesh_baseline.py \
    --skeleton docs/portfolio/demo/skeleton_output.json \
    --profiles data/narrative/phase3_1_pilot/genre_profiles.json \
    --output data/narrative/phase3_1_pilot/flesh_baseline_output.json

# 3. Adaptation recommendation
python scripts/narrative/run_adaptation_recommendation.py \
    --skeleton docs/portfolio/demo/skeleton_output.json \
    --profiles data/narrative/phase3_1_pilot/genre_profiles.json \
    --output data/narrative/phase3_1_pilot/adaptation_recommendation.json

# 4. Episode intensity (실제 데이터)
python scripts/annotation/run_episode_intensity.py \
    --feature-matrix data/annotation/phase3_pilot/features/feature_matrix.csv \
    --profiles data/narrative/phase3_1_pilot/genre_profiles.json \
    --reliability data/annotation/phase3_pilot/reports/reliability.json \
    --output data/annotation/phase3_pilot/episode_intensity.json

# 5. Portfolio demos 재생성 (actual data mode)
python scripts/narrative/build_flesh_baseline_demo.py \
    --skeleton docs/portfolio/demo/skeleton_output.json \
    --baseline data/narrative/phase3_1_pilot/flesh_baseline_output.json \
    --output docs/portfolio/demo_flesh_baseline_actual/

python scripts/narrative/build_adaptation_recommendation_demo.py \
    --recommendation data/narrative/phase3_1_pilot/adaptation_recommendation.json \
    --output docs/portfolio/demo_adaptation_recommendation_actual/

python scripts/annotation/build_episode_intensity_demo.py \
    --intensity data/annotation/phase3_pilot/episode_intensity.json \
    --output docs/portfolio/demo_episode_intensity_actual/
# (NOT --fixture-only — actual data deployment)

# 6. Verifier final pass
python scripts/data/verify_phase3_1_acceptance.py \
    --baseline-output data/narrative/phase3_1_pilot/flesh_baseline_output.json \
    --profiles data/narrative/phase3_1_pilot/genre_profiles.json \
    --demo-dir docs/portfolio/demo_flesh_baseline_actual \
    --baseline-cover-doc docs/portfolio/FLESH_BASELINE_DEMO.md \
    --reliability-report data/annotation/phase3_pilot/reports/reliability.json \
    --output data/annotation/phase3_pilot/reports/phase3_1_acceptance_actual.json \
    --md-report data/annotation/phase3_pilot/reports/phase3_1_acceptance_actual.md
# 기대: §29.1 PASS (Phase 3.0 reliability ≥ 4 KEEP)
```

→ `actual` deploy directory는 별도 (`*_actual`) — 기존 prep / fixture-only deploys와 *명시적 분리*.

---

## 7. NO-GO 시 행동

`summary.keep < 4` 인 경우:

```text
1. STOP — Phase 3.1 진입 보류
2. Reliability report 분석 — 어느 feature가 r 낮은지 확인
3. Annotation guide 수정 (PHASE_3_0_DATA_PILOT_REPORT.md에 작성)
4. Annotator 재훈련 또는 feature 정의 조정 후 *동일 10 synopsis*로 재시도
5. 재시도 3회 후도 ≥4 KEEP 못 만들면 Phase 3.0 v1.2 재설계 검토
```

---

## 8. Boundary 위반 시 행동

만약 본 문서의 "Forbidden" §3 항목 위반이 발생:

1. 즉시 STOP — 현재 작업 보류
2. 변경 사항 rollback (git reset 또는 manual revert)
3. CLAUDE.md / lessons.md 에 incident 기록
4. Lee 보고 + 재발 방지 대책 합의 후 재개

---

## 9. 한 줄 결론

```text
10 synopsis × Mode A manual annotation × strict validation
→ ≥4 KEEP feature → Phase 3.1 data-driven baseline → actual portfolio assets
→ Phase 3.1 acceptance §29.1 PASS
→ Phase 3.2 (or beyond) decision
```

본 boundary는 *prep / fixture / actual 결과물 혼동 0건* 보장이 핵심이다.
