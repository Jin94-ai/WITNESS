# Phase 3.0 Data Pilot Report (Template)

> Per `docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md` §17.2 + §18 + §32.

이 문서는 **Phase 3.0 mini pilot이 종료된 후** 사용자/Claude가 작성하는 *최종
검증 보고서*다. 이 보고서가 **Phase 3.1 ML / Flesh Baseline 진입 여부**를 결정한다.

---

## 0. 작성 시기

```text
Phase 3.0 §32 step 1-12를 완료한 직후:
  - 사용자 승인 5+2건 ✓
  - source review / ToS / robots ✓
  - 10 synopsis 수집/입력 ✓
  - annotation_inputs 생성 ✓
  - annotation_outputs 확보 (수동 또는 API) ✓
  - schema validation ✓
  - hallucination check ✓
  - reliability report ✓
  - KEEP/REVISE/DROP 결정 ✓
  - Data Card 작성 ✓ (PHASE_3_0_DATA_CARD.md)
이 시점에 이 보고서를 작성한다.
```

---

## 1. Pilot 요약

```text
실행 일시:      {{ started_at }} ~ {{ ended_at }}
genre_id:       {{ genre_id }}                    (e.g. korean_morning_melodrama)
mode:           Mode A (수동) | Mode B (fetch) | Mode C (API)
n_titles:       {{ n_titles }}                    (목표 2)
n_episodes:     {{ n_episodes }}                  (목표 10)
n_annotators:   {{ n_annotators }}                (권장 ≥ 2)
LLM 모델 사용: {{ llm_models }}                   (or "manual paste")
비용:           {{ cost_usd }} USD                (Mode C인 경우, 상한 ${{ budget_limit }})
```

---

## 2. 사용자 승인 체크리스트

`docs/plans/PHASE_3_0_APPROVAL_CHECKLIST.md` 5+2 항목:

```text
[x] 1. 실제 줄거리 데이터 fetch 승인 (또는 manual input mode 승인)
[x] 2. 출처별 ToS / robots.txt 검토 승인
[x] 3. LLM API 사용 승인 (또는 수동 annotation)
[x] 4. 비용 상한 승인         ${{ budget }} USD
[x] 5. 저장 위치 / 공개 가능성 결정
[x] 6. 공개 repo 정책 승인
[x] 7. 10-episode mini pilot 범위 승인
```

승인 일시 / 메모: {{ approval_notes }}

---

## 3. 산출물 위치

| 항목 | 경로 |
|---|---|
| 원본 synopsis (private) | `data/external_private/synopsis_raw/` |
| Normalized JSONL | `data/annotation/phase3_pilot/normalized_synopsis.jsonl` |
| Annotation inputs | `data/annotation/phase3_pilot/annotation_inputs/` |
| Annotation outputs | `data/annotation/phase3_pilot/annotation_outputs/` |
| Validated outputs | `data/annotation/phase3_pilot/validated/` |
| Public-safe dataset | `data/annotation/phase3_pilot/public_safe_dataset.jsonl` |
| Feature matrix CSV | `data/annotation/phase3_pilot/features/feature_matrix.csv` |
| Hallucination report | `data/annotation/phase3_pilot/reports/hallucination_report.json` |
| Reliability report | `data/annotation/phase3_pilot/reports/reliability.json` |
| Data Card | `docs/plans/PHASE_3_0_DATA_CARD.md` |

---

## 4. Acceptance Criteria 검증 (§18)

| # | 조건 | 상태 | 증거 |
|---|------|------|------|
| 1 | 사용자 승인 5+2건 완료 | ☐ | §2 |
| 2 | source 후보 ToS / robots 검토 완료 | ☐ | DATA_SOURCE_CANDIDATE_REVIEW.md |
| 3 | 10 episode synopsis 확보 | ☐ | normalized_synopsis.jsonl 행 수 |
| 4 | raw synopsis 공개 repo 밖 또는 .gitignore 보호 | ☐ | .gitignore 확인 |
| 5 | annotation_inputs/*.json 생성 | ☐ | dir count |
| 6 | annotation_outputs/*.json 확보 | ☐ | dir count |
| 7 | annotation output schema 통과 | ☐ | validate_annotation_outputs.py 실행 결과 |
| 8 | hallucination quote rate < 5% | ☐ | hallucination_report.json::hallucination_rate |
| 9 | 최소 4 feature r ≥ 0.7 | ☐ | reliability.json::summary.keep |
| 10 | KEEP/REVISE/DROP 판정 완료 | ☐ | reliability.json::summary |
| 11 | Data Card 작성 | ☐ | PHASE_3_0_DATA_CARD.md filled |
| 12 | Phase 3.1 Go/No-Go 판정 | ☐ | §7 |

---

## 5. 핵심 결과

### 5.1 Hallucination Quote Check

```text
total_quotes:        {{ total_quotes }}
verified:            {{ verified }}
hallucinated:        {{ hallucinated }}
hallucination_rate:  {{ rate }}        (PASS if < 0.05, NO-GO if ≥ 0.10)
status:              {{ halluc_status }}    PASS | WARN | NO-GO
```

문제 quote (hallucinated) 예시:

```text
- record {{ rid }}, feature {{ f }}: "{{ quote }}"
  → 원문 매칭 실패 (annotator: {{ ann_id }})
- ...
```

### 5.2 Inter-annotator Reliability

| feature | n_pairs | mean_r | median_r | decision |
|---|---|---|---|---|
| conflict_intensity_peak    | {{ n }} | {{ r }} | {{ med }} | {{ d }} |
| dangling_thread_generation | {{ n }} | {{ r }} | {{ med }} | {{ d }} |
| cliffhanger_strength       | {{ n }} | {{ r }} | {{ med }} | {{ d }} |
| relationship_pressure      | {{ n }} | {{ r }} | {{ med }} | {{ d }} |
| hidden_information_pressure| {{ n }} | {{ r }} | {{ med }} | {{ d }} |
| silence_or_avoidance       | {{ n }} | {{ r }} | {{ med }} | {{ d }} |
| emotional_suppression      | {{ n }} | {{ r }} | {{ med }} | {{ d }} |

```text
KEEP            count: {{ n_keep }}        threshold: ≥ 4
REVISE          count: {{ n_revise }}
DROP            count: {{ n_drop }}
NEEDS_MORE_DATA count: {{ n_needs }}
```

### 5.3 사람 spot-check

```text
spot-check 비율:    {{ pct }} % (n={{ n_spot }})
일치:               {{ n_match }}
일부 불일치:        {{ n_partial }}
큰 불일치:          {{ n_major }}
주요 발견:
  - {{ finding_1 }}
  - {{ finding_2 }}
```

---

## 6. Feature 별 분석

### 6.1 KEEP feature (Phase 3.1에서 사용)

```text
{{ keep_feature_1 }}:
  mean_r:   {{ r }}
  reason:   annotator 간 score scale + 방향 일치
  next:     Phase 3.1 weighted score baseline에 weight 부여

{{ keep_feature_2 }}: ...
```

### 6.2 REVISE feature (정의 수정 후 재시도)

```text
{{ revise_feature_1 }}:
  mean_r:    {{ r }}
  주요 불일치 패턴: {{ pattern }}
  proposed revision:
    - "{{ current_def }}" → "{{ revised_def }}"
  next:      ANNOTATION_GUIDE.md 갱신 후 다음 pilot에서 재측정
```

### 6.3 DROP feature

```text
{{ drop_feature_1 }}:
  mean_r:    {{ r }}
  사유:      {{ reason }}
  next:      feature set v1.2에서 제거 검토
```

### 6.4 NEEDS_MORE_DATA

```text
{{ needs_feature_1 }}:
  n_pairs:  {{ n }}
  사유:     표본 부족 — Phase 3.0 2차 (40-episode)에서 재평가
```

---

## 7. Phase 3.1 Go / No-Go 판정

§19 No-Go 조건:

```text
[ ] hallucination_rate ≥ 10%             {{ check_1 }}
[ ] r ≥ 0.7 feature가 3개 미만           {{ check_2 }}
[ ] feature definition이 대량으로 흔들림   {{ check_3 }}
[ ] data card 미작성                      {{ check_4 }}
```

§20 Phase 3.1 진입 조건:

```text
[ ] Phase 3.0 pilot report 완료           {{ check_5 }}
[ ] KEEP feature 최소 4개                 {{ check_6 }}
[ ] hallucination_rate < 5%               {{ check_7 }}
[ ] feature_matrix.csv 생성               {{ check_8 }}
[ ] train/val split 가능                  {{ check_9 }}
[ ] baseline target 정의                  {{ check_10 }}
```

### 판정

```text
{{ verdict }}    GO | NO-GO | CONDITIONAL_GO
```

이유 / 다음 단계:

```text
GO인 경우:
  → Phase 3.1 시작 가능. KEEP feature {{ list }}로 weighted score baseline 구축.

NO-GO인 경우:
  → Phase 3.0 2차 시작. 다음 작업:
     - feature definition 수정 ({{ specific_features }})
     - prompt template 개선
     - LLM 모델 조합 변경 (시도)
     - 또는 데이터 source 교체

CONDITIONAL_GO인 경우:
  → Phase 3.1 시작하되 KEEP feature를 expand 가능 (pilot 2차와 병행).
     - 1차 KEEP: {{ list }}
     - 2차 시작 동시에 baseline 구축
```

---

## 8. 부록 — 주요 명령어 로그

(재현성 보장. 실제 실행한 commands 기록.)

```bash
# Step 1. Normalize
python scripts/data/normalize_synopsis.py \
    --input data/external_private/synopsis_raw \
    --output data/annotation/phase3_pilot/normalized_synopsis.jsonl

# Step 2. Validate
python scripts/data/validate_synopsis_dataset.py \
    --input data/annotation/phase3_pilot/normalized_synopsis.jsonl \
    --strict-min-records 10

# Step 3. Build inputs
python scripts/data/build_annotation_inputs.py \
    --input data/annotation/phase3_pilot/normalized_synopsis.jsonl \
    --output data/annotation/phase3_pilot/annotation_inputs

# Step 4-5. (Manual) LLM annotation → annotation_outputs/

# Step 6. Validate outputs
python scripts/annotation/validate_annotation_outputs.py \
    --input data/annotation/phase3_pilot/annotation_outputs \
    --synopsis data/annotation/phase3_pilot/normalized_synopsis.jsonl \
    --validated-dir data/annotation/phase3_pilot/validated \
    --hallucination-report data/annotation/phase3_pilot/reports/hallucination_report.json

# Step 7. Feature matrix
python scripts/annotation/build_feature_matrix.py \
    --input data/annotation/phase3_pilot/validated \
    --output data/annotation/phase3_pilot/features/feature_matrix.csv

# Step 8. Reliability
python scripts/annotation/build_reliability_report.py \
    --features data/annotation/phase3_pilot/features/feature_matrix.csv \
    --output data/annotation/phase3_pilot/reports/reliability.json

# Step 9. Public-safe (선택)
python scripts/data/build_public_safe_dataset.py \
    --input data/annotation/phase3_pilot/normalized_synopsis.jsonl \
    --output data/annotation/phase3_pilot/public_safe_dataset.jsonl \
    --max-summary-length 100 \
    --annotation-index data/annotation/phase3_pilot/validated
```

---

## 9. 변경 이력

| 버전 | 날짜 | 변경 |
|---|---|---|
| v0.1 | {{ created_at }} | Phase 3.0 mini pilot initial report |

---

*이 보고서가 Phase 3.1 진입 여부를 결정한다. NO-GO인 경우 무리하게 ML 시작
금지 — 신뢰도 안 잡힌 데이터로 학습하면 모델은 장르 문법이 아니라 noise를 학습한다.*
