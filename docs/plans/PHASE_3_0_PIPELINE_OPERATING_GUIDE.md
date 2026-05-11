# Phase 3.0 v1.1 Pipeline Operating Guide

> Per `docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md` §10 + §17.

이 문서는 **Phase 3.0 Data & Annotation Pilot의 Mode A (수동 입력) 파이프라인**을
실제로 어떻게 운영하는지 정리한다. 2026-05-11 시점 (cycle 8):
- **Phase 3.0 7 스크립트 + Phase 3.1 5 산출 모두 작동 (fast suite 2,524 pass)**
- **§4의 Step 1-9 = Phase 3.0 운영 / Step 10-13 = Phase 3.1 baseline + demo (사용자 승인 후 즉시 가능)**
- **외부 fetch / LLM API / 원문 저장 0** — 사용자 승인 5+2건 후에만 실제 실행

---

## 1. 역할 분리 (v1.1 §2.1)

| Layer | 담당 | 이번 cycle 산출 |
|---|---|---|
| Claude Code = 데이터 공장 | 7 pipeline 스크립트 | ✅ 완료 |
| LLM = 라벨러 | annotation_inputs 받아 응답 | 사용자 승인 후 |
| User = 승인권자 | source / fetch / API / 비용 / 저장 / 공개 정책 | PHASE_3_0_APPROVAL_CHECKLIST.md |

---

## 2. 스크립트 인덱스 (외부 의존 0)

### Phase 3.0 (Mode A 데이터 파이프라인)

| 스크립트 | 역할 |
|---|---|
| [scripts/data/normalize_synopsis.py](../../scripts/data/normalize_synopsis.py) | raw private synopsis (.json / .txt) → normalized JSONL |
| [scripts/data/validate_synopsis_dataset.py](../../scripts/data/validate_synopsis_dataset.py) | normalized JSONL schema + 중복 / 정렬 / 길이 검증 |
| [scripts/data/build_annotation_inputs.py](../../scripts/data/build_annotation_inputs.py) | normalized → annotation_inputs/*.json (LLM 붙여넣기용, instructions_ko 포함) |
| [scripts/data/build_public_safe_dataset.py](../../scripts/data/build_public_safe_dataset.py) | normalized → public_safe (synopsis_text 제거) |
| [scripts/annotation/validate_annotation_outputs.py](../../scripts/annotation/validate_annotation_outputs.py) | LLM 응답 schema + evidence_quote hallucination 검사 |
| [scripts/annotation/build_feature_matrix.py](../../scripts/annotation/build_feature_matrix.py) | annotation_outputs → long-form CSV |
| [scripts/annotation/build_reliability_report.py](../../scripts/annotation/build_reliability_report.py) | feature_matrix → 각 feature별 Pearson r + KEEP/REVISE/DROP/NEEDS_MORE_DATA 판정 |

### Phase 3.1 (baseline 산출)

| 스크립트 | 역할 |
|---|---|
| [scripts/narrative/build_genre_profiles.py](../../scripts/narrative/build_genre_profiles.py) | reliability + rulebook → GenreProfile (genre_profile_v1) |
| [scripts/narrative/run_flesh_baseline.py](../../scripts/narrative/run_flesh_baseline.py) | SkeletonOutput + profiles → flesh_baseline_output_v1 (*seed × profile* fit, Plan §22.1 Target A) |
| [scripts/annotation/run_episode_intensity.py](../../scripts/annotation/run_episode_intensity.py) | feature_matrix + profiles → episode_intensity_v1 (*episode × profile* intensity, Plan §22.2 Target B) |
| `engine/observer/adaptation_recommendation.py` | SkeletonOutput + profiles → adaptation_recommendation_v1 (*seed → ranked top-K genres*, Plan §22.3 Target C, No-ML library) |
| [scripts/narrative/run_adaptation_recommendation.py](../../scripts/narrative/run_adaptation_recommendation.py) | adaptation_recommendation 모듈 CLI wrapper — `--skeleton` + `--profiles` + `--top-k` + `--min-score`, deploy artifact: `data/narrative/phase3_1_demo/adaptation_recommendation.json` |
| [scripts/narrative/build_adaptation_recommendation_demo.py](../../scripts/narrative/build_adaptation_recommendation_demo.py) | adaptation_recommendation.json → portfolio HTML+MD demo (`docs/portfolio/demo_adaptation_recommendation/`), self-contained, Non-Claims + Rule #14 + Phase 3.05 정직성 4 layer |
| [scripts/narrative/apply_top_recommendation.py](../../scripts/narrative/apply_top_recommendation.py) | **Plan §24 Step 2 bridge** — adaptation_recommendation → genre_adapter. modal 1순위 genre 자동 선택 (tie-break: alphabetical) + `--genre` override. delegates to `apply_genre_adapter.py`. recommendation의 `calibration_status` / `mode` 노출 |
| [scripts/data/verify_phase3_1_acceptance.py](../../scripts/data/verify_phase3_1_acceptance.py) | **Plan §29 자동 검증 CLI** — 9개 acceptance 항목 자동 점검 (AUTO 7 + PENDING 1 + HEURISTIC 1). reliability.json 미존재 시 §29.1 PENDING (Phase 3.0 dep). exit 0 (AUTO all pass) / 1 (AUTO fail) / 2 (사용 오류) |
| [scripts/narrative/build_flesh_baseline_demo.py](../../scripts/narrative/build_flesh_baseline_demo.py) | flesh_baseline output → portfolio HTML/MD/JSON demo (*seed × profile* view) |
| [scripts/annotation/build_episode_intensity_demo.py](../../scripts/annotation/build_episode_intensity_demo.py) | episode_intensity output → portfolio HTML/MD/JSON demo (*episode × profile* arc view, title 별 그룹) |

---

## 3. 디렉토리 구조 (Phase 3.0 v1.1 §8)

```text
data/external_private/                            ← .gitignore (사용자 승인 후 사용)
  └── synopsis_raw/
       └── {title}_ep{NN}.json or .txt

data/annotation/phase3_pilot/
  ├── normalized_synopsis.jsonl                   ← .gitignore (synopsis_text 포함)
  ├── annotation_inputs/                          ← .gitignore
  │    └── {record_id}.json
  ├── annotation_outputs/                         ← .gitignore (사용자 응답)
  │    └── {record_id}_{annotator}.json
  ├── per_annotator/                              ← .gitignore (raw multi-annotator)
  ├── synopsis_cache/                             ← .gitignore (LLM 응답 cache)
  ├── validated/                                  ← .gitignore
  ├── public_safe_dataset.jsonl                   ← 추적 (synopsis_text 제거)
  ├── features/
  │    └── feature_matrix.csv                     ← 추적 (수치만)
  └── reports/
        ├── reliability.json                       ← 추적
        └── hallucination_report.json              ← 추적

data/llm_keys/                                    ← .gitignore
data/llm_call_logs/                               ← .gitignore
```

`.gitignore`는 [.gitignore](../../.gitignore) Phase 3.0 섹션 참조.

---

## 4. 운영 절차 (Mode A — 수동 LLM annotation)

승인 5+2건이 완료된 후:

### Step 1. Raw synopsis 수동 입력

사용자가 직접 작성/입력:

```text
data/external_private/synopsis_raw/titleA_ep01.json
data/external_private/synopsis_raw/titleA_ep02.json
...
data/external_private/synopsis_raw/titleA_ep05.json
data/external_private/synopsis_raw/titleB_ep01.json
... (총 10 episodes)
```

각 .json 형식:

```json
{
  "genre_id": "korean_morning_melodrama",
  "title_id": "titleA",
  "episode_number": 1,
  "synopsis_text": "회차 줄거리 전문...",
  "source_name": "official_broadcaster",
  "source_url": "https://...",
  "source_license_note": "...",
  "fetched_at": "2026-05-11",
  "public_safe_summary": "한 줄 요약 (≤ 100자)"
}
```

또는 `.txt` 형식 (`{title_id}_ep{NN}.txt`):

```
title_id_ep01.txt → synopsis_text 본문만
```

### Step 2. Normalize

```bash
python scripts/data/normalize_synopsis.py \
    --input data/external_private/synopsis_raw \
    --output data/annotation/phase3_pilot/normalized_synopsis.jsonl \
    --default-genre korean_morning_melodrama
```

### Step 3. Validate dataset

```bash
python scripts/data/validate_synopsis_dataset.py \
    --input data/annotation/phase3_pilot/normalized_synopsis.jsonl \
    --strict-min-records 10
```

### Step 4. Build annotation inputs

```bash
python scripts/data/build_annotation_inputs.py \
    --input data/annotation/phase3_pilot/normalized_synopsis.jsonl \
    --output data/annotation/phase3_pilot/annotation_inputs
```

10개의 `{record_id}.json` 파일 생성됨. 각 파일은 LLM에 *그대로* 붙여넣을 수 있는
task (annotate_episode_synopsis_v1).

### Step 5. (수동) LLM에 붙여넣기

각 파일을 ChatGPT / Claude / Gemini 등에 붙여넣고, `episode_annotation_v1`
schema 응답을 받아 저장:

```text
data/annotation/phase3_pilot/annotation_outputs/
  ├── km_titleA_ep001_modelA.json
  ├── km_titleA_ep001_modelB.json
  ├── ...
  └── km_titleB_ep005_modelB.json
```

(2-model pilot이면 10 × 2 = 20 outputs, 3-model이면 30 outputs)

### Step 6. Validate outputs + hallucination check + feature coverage

```bash
python scripts/annotation/validate_annotation_outputs.py \
    --input data/annotation/phase3_pilot/annotation_outputs \
    --synopsis data/annotation/phase3_pilot/normalized_synopsis.jsonl \
    --validated-dir data/annotation/phase3_pilot/validated \
    --hallucination-report data/annotation/phase3_pilot/reports/hallucination_report.json
```

성공 기준 (§16.1): `hallucination_rate < 0.05`. ≥ 0.10이면 No-Go.

추가 검증 (cycle 12) — feature가 일관되게 quote를 받는지:
- `--expected-features` 미지정 시 Phase 3.0 §11 7 features default 사용.
- hallucination_report에 추가 필드: `per_feature_quote_count` / `per_feature_annotation_coverage` / `expected_features_coverage_ratio` / `expected_features_with_zero_coverage` / `min_coverage_feature` / `min_coverage_ratio`.
- LLM annotator가 *어떤 feature는 quote 없이 score만 줬는지* 즉시 발견 가능 — annotation 품질 control.

선택적으로 strict mode + 최소 coverage threshold 강제:

```bash
python scripts/annotation/validate_annotation_outputs.py \
    --input ... --synopsis ... \
    --hallucination-report ... \
    --quote-coverage-min 0.5 --strict
# coverage 0.5 미만 feature가 있으면 exit 1
```

### Step 7. Build feature matrix

```bash
python scripts/annotation/build_feature_matrix.py \
    --input data/annotation/phase3_pilot/validated \
    --output data/annotation/phase3_pilot/features/feature_matrix.csv
```

### Step 8. Reliability report

```bash
python scripts/annotation/build_reliability_report.py \
    --features data/annotation/phase3_pilot/features/feature_matrix.csv \
    --output data/annotation/phase3_pilot/reports/reliability.json
```

성공 기준 (§16.2 + §20): `summary.keep ≥ 4` features.

### Step 9. Public-safe dataset (선택)

```bash
python scripts/data/build_public_safe_dataset.py \
    --input data/annotation/phase3_pilot/normalized_synopsis.jsonl \
    --output data/annotation/phase3_pilot/public_safe_dataset.jsonl \
    --max-summary-length 100 \
    --annotation-index data/annotation/phase3_pilot/validated
```

이 파일은 공개 가능 (synopsis_text 제거, source_url 제거).

### Step 10. Genre Profile 빌드 (Phase 3.1 §26)

reliability + rulebook → 검증된 weight를 가진 GenreProfile.

```bash
python scripts/narrative/build_genre_profiles.py \
    --reliability data/annotation/phase3_pilot/reports/reliability.json \
    --genres korean_morning_melodrama \
    --output data/annotation/phase3_pilot/genre_profiles.json
```

성공 기준: `data_source="phase3_pilot"`, `feature_weights` ≥ 4 (KEEP 통과).

### Step 11. Flesh Baseline (Phase 3.1 §27 — seed × profile)

SkeletonOutput seed가 어떤 장르 flesh에 잘 맞는지 *seed × profile* 점수.

```bash
python scripts/narrative/run_flesh_baseline.py \
    --skeleton docs/portfolio/demo/skeleton_output.json \
    --profiles data/annotation/phase3_pilot/genre_profiles.json \
    --output data/annotation/phase3_pilot/flesh_baseline_output.json
```

각 seed × profile 조합당 `score` 0-1 + `fit_label` (strong/moderate/weak/no_fit).

### Step 12. Episode Intensity (Phase 3.1 §22.2 — episode × profile)

각 *에피소드*가 장르 시그니처에 얼마나 부합하는지 weighted intensity score.

```bash
python scripts/annotation/run_episode_intensity.py \
    --feature-matrix data/annotation/phase3_pilot/features/feature_matrix.csv \
    --profiles data/annotation/phase3_pilot/genre_profiles.json \
    --reliability data/annotation/phase3_pilot/reports/reliability.json \
    --output data/annotation/phase3_pilot/episode_intensity.json \
    --strict-min-records 10
```

각 record × profile 당 `intensity_score` (0-1) + per-feature `feature_contributions`.

`flesh_baseline_output.json` (Step 11)이 *seed → genre fit* 답변이라면, `episode_intensity.json` (Step 12)은 *episode → genre intensity* 답변. 두 layer는 다른 질문에 답하므로 둘 다 산출 권장.

### Step 13. Demo HTML (Phase 3.1 §28) — 두 layer 모두

**13a. Seed × profile fit demo** (`flesh_baseline_output.json`):

```bash
python scripts/narrative/build_flesh_baseline_demo.py \
    --skeleton docs/portfolio/demo/skeleton_output.json \
    --baseline data/annotation/phase3_pilot/flesh_baseline_output.json \
    --output docs/portfolio/demo_flesh_baseline
```

**13b. Episode × profile intensity demo** (`episode_intensity.json`, Plan §22.2):

```bash
python scripts/annotation/build_episode_intensity_demo.py \
    --intensity data/annotation/phase3_pilot/episode_intensity.json \
    --output docs/portfolio/demo_episode_intensity
```

둘 다 self-contained HTML + MD + JSON. raw text 노출 0 검증 자동. 두 demo는 각각 다른 질문에 답한다 — *seed → genre fit* (어떤 시뮬레이션 seed가 장르에 적합) vs *episode → genre intensity* (어떤 실제 에피소드가 장르 시그니처가 강한가).

---

## 4.5. Acceptance 자동 검증 (Phase 3.05 cycle 5, 보강 cycle 7)

Step 1-13 완료 후, Plan §18의 12개 acceptance 항목을 한 명령으로 자동 점검:

```bash
python scripts/data/verify_phase3_0_acceptance.py \
    --pilot-dir data/annotation/phase3_pilot \
    --output data/annotation/phase3_pilot/reports/acceptance_check.json \
    --md-report data/annotation/phase3_pilot/reports/acceptance_check.md
```

산출 (cycle 11 보강):
- **stdout 보고서** — 12 항목별 status 표시 (`[O]` PASS / `[X]` FAIL / `[~]` PENDING / `[?]` MANUAL)
- **JSON report** (`--output`) — `checks[]` (item_id / name / status / category / detail / evidence) + `summary`
- **Markdown report** (`--md-report`, cycle 11 신규) — 사람이 읽기 좋은 보고서 (Summary 섹션 + 12 항목 표 + Status/Category legend + timestamp). pilot 종료 후 *공식 acceptance 문서*로 첨부 가능.
- **exit code** — 0 (모든 AUTO PASS 또는 PENDING) / 1 (1+ AUTO FAIL) / 2 (입력 오류)

분류 (cycle 7 보강):
- **AUTO** (§18.3-10 + 보강된 §18.1-2): 산출물 / 수치 자동 체크. exit code에 반영. **`PHASE_3_0_APPROVAL_CHECKLIST.md` 파싱**으로 §18.1+2도 AUTO에 합류 — 체크박스 `### ☐/☑ N. ...` 헤더 인식.
- **HEURISTIC** (§18.11-12): Data Card / Pilot Report 작성 추정 (template marker 검사). exit code에 영향 0 (warning만).
- **MANUAL** (§18.1-2 fallback): approval checklist doc 없으면 MANUAL fallback. 사용자 환경 차이 대비.

Status 의미:
- **`[O]` PASS**: 모든 조건 통과.
- **`[X]` FAIL**: 필수 조건 미충족 (exit 1 트리거 — AUTO인 경우만).
- **`[~]` PENDING**: 사용자 승인 *진행 중* (FAIL 아님, exit code 영향 0). 예: 체크리스트 4/7 체크.
- **`[?]` MANUAL**: 자동 검증 불가, 사용자 외부 확인 필요.

`--strict` mode 없이도 안전하게 실행 가능 — pilot 미운영 상태에서도 정상 동작 (모든 AUTO FAIL/PENDING로 표시).

진행 패턴 (cycle 7):
```text
pre-approval: §18.1 [~] PENDING (0/7 체크) + §18.2 [~] PENDING
사용자 ☐→☑ 마킹 진행 → §18.1 [~] PENDING (4/7 체크, 미체크: ...)
모든 ☑ 완료    → §18.1 [O] PASS (AUTO) + §18.2 [O] PASS
```

---

## 4.6. Phase 3.1 Acceptance 자동 검증 (cycle 29-31)

Phase 3.1 baseline deploy 후, Plan §29의 9개 acceptance 항목을 한 명령으로 자동 점검 (Phase 3.0 verifier 대칭):

```bash
python scripts/data/verify_phase3_1_acceptance.py \
    --baseline-output data/narrative/phase3_1_demo/flesh_baseline_output.json \
    --profiles data/narrative/phase3_1_demo/genre_profiles.json \
    --demo-dir docs/portfolio/demo_flesh_baseline \
    --baseline-cover-doc docs/portfolio/FLESH_BASELINE_DEMO.md \
    --output data/narrative/phase3_1_demo/acceptance_check.json \
    --md-report data/narrative/phase3_1_demo/acceptance_check.md
```

Phase 3.0 의존 항목 (§29.1) 검증을 활성화하려면 `--reliability-report`도 전달:

```bash
    --reliability-report data/annotation/phase3_pilot/reports/reliability.json
```

산출 (Phase 3.0 verifier 패턴 transplant):
- **stdout 보고서** — 9 항목별 status 표시 (`[O]` PASS / `[X]` FAIL / `[~]` PENDING).
- **JSON report** (`--output`) — `checks[]` + `summary` (Phase 3.0과 동일 schema).
- **Markdown report** (`--md-report`, cycle 31) — Summary 섹션 + 9 항목 표 + Status/Category legend + timestamp.
- **exit code** — 0 (AUTO PASS 또는 PENDING) / 1 (1+ AUTO FAIL) / 2 (입력 오류).

분류:
- **AUTO** (§29.2-8): 산출물 / 필드 자동 체크 — exit code에 반영.
- **PENDING** (§29.1): Phase 3.0 reliability 의존. reliability.json 미존재 시 PENDING (exit 0 유지). 존재 + summary.keep ≥ 4 시 PASS.
- **HEURISTIC** (§29.9): cover doc 길이 ≥ 500 chars 약한 검사. exit code 영향 0.

운영 시점:
- Phase 3.1 baseline deploy 직후 (`run_flesh_baseline.py` + `build_flesh_baseline_demo.py` 완료 후)
- Phase 3.2 진입 결정 전 *모든 AUTO PASS* 확인 필수

자동 검증: `tests/test_skeleton/test_phase3_1_baseline.py::test_verify_phase3_1_*`

---

## 5. Phase 3.0 Acceptance 매핑 (§18)

| Acceptance 항목 | 관련 산출물 |
|---|---|
| 사용자 승인 5+2건 완료 | PHASE_3_0_APPROVAL_CHECKLIST.md |
| source 후보 ToS 검토 완료 | DATA_SOURCE_CANDIDATE_REVIEW.md |
| 10 episode synopsis 확보 | `synopsis_raw/` (private) |
| raw synopsis가 공개 repo 밖 | .gitignore + `external_private/` |
| annotation_inputs/*.json 생성 | `build_annotation_inputs.py` |
| annotation_outputs/*.json 확보 | 수동 LLM 응답 |
| schema validation 통과 | `validate_annotation_outputs.py` |
| hallucination rate < 5% | `hallucination_report.json` |
| 최소 4 feature r ≥ 0.7 | `reliability.json::summary.keep` |
| KEEP/REVISE/DROP 판정 | `reliability.json` |
| Data Card | (작성 후 docs/plans/PHASE_3_0_DATA_CARD.md) |
| Phase 3.1 Go/No-Go | (작성 후 docs/plans/PHASE_3_0_DATA_PILOT_REPORT.md) |

---

## 6. No-Go 시 행동 (§19)

```text
hallucination_rate ≥ 10%   → prompt template 수정 + 재 annotation
KEEP feature < 3            → feature definition 수정 또는 제거
ToS 위반 발견               → 즉시 fetch 중단 + source 제거
원문 본문 노출              → public_safe_dataset 사용 + portfolio HTML 검토
LLM에게 데이터 정제 위임    → 코드 파이프라인으로 회귀
```

---

## 7. Phase 3.1 진입 조건 (§20)

```text
[ ] Phase 3.0 pilot report 완료
[ ] reliability.json::summary.keep ≥ 4
[ ] hallucination_rate < 0.05
[ ] feature_matrix.csv 생성
[ ] data card 완료
[ ] train/val split 결정
[ ] baseline target 결정 (genre intensity score 권장)
```

---

## 8. 검증 (누적 산출)

- **Phase 3.0 pipeline**: 7 신규 스크립트 + 22 tests (`tests/test_skeleton/test_phase3_pipeline.py`)
- **Phase 3.1 baseline**: 5 신규 산출 (GenreProfile + FleshBaseline + EpisodeIntensity + demo + reliability) + 35 tests (`tests/test_skeleton/test_phase3_1_baseline.py`)
- Mode A → Phase 3.1 *13 step* 전체 e2e fixture test (`test_full_pipeline_e2e_fixture_to_baseline`) 포함
- 누적 **2,524 fast tests pass / 0 회귀**
- 외부 fetch / LLM API / 학습 0 — 사용자 승인 5+2건 전 *모든 산출* 결정론적 코드 + fixture로 검증됨

---

## 9. Deploy Status Matrix (Phase 3.05 Step 5)

산출물별 *현재 상태 / 생성 조건 / 공개 정책*. 사용자/agent가 파일 요청 시 이 표를 기준으로 삼는다 (요청 전 status 확인).

### 분류

| 상태 | 의미 |
|---|---|
| **deployed-prep** | 이미 생성됨, rulebook_only 또는 fixture 기반 prep mode |
| **deployed-data** | 이미 생성됨, 실제 Phase 3.0 pilot 데이터 기반 (현재는 0건, 사용자 승인 후) |
| **script-only** | 스크립트는 구현됨, output은 deploy되지 않음 (운영 시 자동 생성) |
| **fixture-only** | tests/fixtures/에서만 존재, public-safe fictional 데이터 |
| **generated-after-approval** | 사용자 승인 5+2건 + Mode A 운영 후 자동 생성 |

### Phase 3.0 산출물

| 산출물 | 상태 | 생성 조건 | 공개 가능? | 비고 |
|---|---|---|---|---|
| `data/external_private/synopsis_raw/*.json` | generated-after-approval | 사용자가 raw synopsis 수동 입력 | ❌ 공개 금지 | `.gitignore` 보호 |
| `data/annotation/phase3_pilot/normalized_synopsis.jsonl` | generated-after-approval | Step 2 normalize 후 | ❌ synopsis_text 포함 | `.gitignore` 보호 |
| `data/annotation/phase3_pilot/annotation_inputs/*.json` | generated-after-approval | Step 4 build_annotation_inputs 후 | ❌ synopsis_text 포함 | `.gitignore` 보호 |
| `data/annotation/phase3_pilot/annotation_outputs/*.json` | generated-after-approval | 수동 LLM 응답 저장 (Step 5) | ❌ raw quote 포함 | `.gitignore` 보호 |
| `data/annotation/phase3_pilot/validated/*.json` | generated-after-approval | Step 6 validation 통과분 | ❌ 동상 | `.gitignore` 보호 |
| `data/annotation/phase3_pilot/features/feature_matrix.csv` | generated-after-approval | Step 7 | ✅ 수치만 | 추적 가능 |
| `data/annotation/phase3_pilot/reports/reliability.json` | generated-after-approval | Step 8 | ✅ 수치만 | 추적 가능 |
| `data/annotation/phase3_pilot/reports/hallucination_report.json` | generated-after-approval | Step 6 | ✅ 수치만 | 추적 가능 |
| `data/annotation/phase3_pilot/public_safe_dataset.jsonl` | generated-after-approval | Step 9 (선택) | ✅ synopsis_text 제거됨 | 추적 가능 |
| `tests/fixtures/annotation_public_safe/` | **fixture-only** | 이미 존재 (cycle 2 + 7) | ✅ fictional | titleA + titleB × 5 ep (10 raw / 20 outputs) — 운영용 데이터 아님 |

### Phase 3.1 산출물

| 산출물 | 상태 | 생성 조건 | 공개 가능? | 비고 |
|---|---|---|---|---|
| `data/narrative/phase3_1_demo/genre_profiles.json` | **deployed-prep** | rulebook_only fallback (cycle 3) | ✅ 공개 | `data_source: rulebook_only` 명시 |
| `data/narrative/phase3_1_demo/flesh_baseline_output.json` | **deployed-prep** | rulebook_only fallback (cycle 3, Phase 3.05 cycle 1 갱신) | ✅ 공개 | 모든 8 rec에 `score_breakdown.mode=rulebook_only`, `annotation_score=None` |
| `docs/portfolio/demo_flesh_baseline/index.html` | **deployed-prep** | cycle 4 + Phase 3.05 cycle 1 | ✅ 공개 | "Prep mode (rulebook-only)" banner / `strong_fit (rulebook-only)` 병기 |
| `docs/portfolio/demo_flesh_baseline/baseline.md` | **deployed-prep** | 동상 | ✅ 공개 | 동상 |
| `docs/portfolio/demo_flesh_baseline/flesh_baseline_output.json` | **deployed-prep** | mirror | ✅ 공개 | data layer와 동일 |
| `data/annotation/phase3_pilot/episode_intensity.json` | **script-only** | Operating Guide Step 12 (사용자 데이터로) | ✅ raw 제외 공개 | `scripts/annotation/run_episode_intensity.py` 구현됨, real-data output deploy 0 |
| `docs/portfolio/demo_episode_intensity/index.html` | **fixture-only** (cycle 40) | Step 13b — `tests/fixtures/annotation_public_safe/` 기반 e2e 실행 deploy | ✅ "Fictional fixture-only" banner 강제 | `build_episode_intensity_demo.py --fixture-only` 사용 / Target B 1번째 portfolio asset / Phase 3.0 pilot 진입 후 실제 데이터 deploy로 교체 가능 |
| `data/narrative/phase3_1_demo/adaptation_recommendation.json` | **deployed-prep** | cycle 18 — Target C `run_adaptation_recommendation.py` 출력 | ✅ 공개 | rulebook_only mode + `calibration_status: uncalibrated_phase3_placeholder` 명시 / 4 seeds × 2 genres = 8 ranked modes |
| `docs/portfolio/demo_adaptation_recommendation/index.html` | **deployed-prep** | cycle 19 — Target C HTML demo | ✅ 공개 | Non-Claims + Prep-mode (rulebook-only) + Calibration banner / 1순위 분포 bar + seed별 ranked card view |
| `data/narrative/phase3_1_demo/top_recommendation_adapted.json` | **deployed-prep** | cycle 25 — Plan §24 Step 2 bridge 결과 | ✅ 공개 | `apply_top_recommendation.py` modal-genre 선택 + `apply_genre_adapter` delegate 결과 / 선택 근거 (modal_count / tied / mode) stdout 노출 |
| `docs/portfolio/demo_rubric/*` | **deployed-prep** | Phase 3.05 Rubric directive cycle 19/22/23/26/27/28 등 | ✅ 공개 | Non-Claims + uncalibrated 명시 / 8 trajectory variants + 3 alignment + 4 character + 3 ensemble JSON + 1 HTML viz / `from engine.rubric` import는 neural trainer 외부만 (Rule #14) |

### 정책

- **공개 vs git-tracked 구분 (cycle 60 명시)**: 표의 "✅ 공개" column은 *외부 공개 가능 여부 (privacy/license 안전)*를 뜻하며, *git-tracked 여부와 다르다*. `data/` 영역은 `.gitignore` line 84 `data/*` 로 대용량 생성 데이터 reproducible 정책에 따라 미추적 (필요 시 `scripts/` 로 재생성). `docs/portfolio/` 영역은 git-tracked. 즉 `data/narrative/phase3_1_demo/*.json` 같은 deployed-prep artifacts는 *공개 가능*하지만 *reproducible이라 repo 미포함* — 사용자가 직접 재생성 후 외부 공유 가능.
- **deployed-prep**: 공개 가능. 단 prep banner + `data_source: rulebook_only` 명시 강제.
- **deployed-data**: 사용자 승인 후 Phase 3.0 pilot 운영 결과로만 생성.
- **script-only**: 사용자 요청 시 fixture 기반 prep deploy 가능하나 "fictional fixture" banner + portfolio main 노출 금지 (appendix만).
- **fixture-only**: test 용도만. portfolio에 포함하지 않음.
- **generated-after-approval**: 사용자 승인 5+2건 (PHASE_3_0_APPROVAL_CHECKLIST.md) 통과 전 *어떤 외부 fetch / LLM API / 학습도 0건*.

### 파일 요청 원칙 (사용자/agent 공통)

```text
요청 우선순위:
1. deployed artifact 먼저 (이미 존재)
2. script-only output은 존재 여부 확인 후 (Operating Guide Step 10-13 실행 필요)
3. generated-after-approval 파일은 승인 전 요청하지 않음
4. fixture-only는 test 용도로만 사용, portfolio main에 노출 금지
```

이 표는 cycle 별로 갱신된다. 마지막 갱신: Phase 3.05 cycle 3 (2026-05-11).

---

## 10. 한 줄 요약

```text
"Claude Code = 데이터 공장 / LLM = 라벨러 / User = 승인권자"의 분리를
실제 7 스크립트로 구현. fetch 없이도 Mode A로 10-episode pilot 가능.
Phase 3.05 — prep 산출물 정직성 보강 (rulebook_only score_breakdown / 3 layer report / strict synopsis 강제 / deploy status matrix).
```
