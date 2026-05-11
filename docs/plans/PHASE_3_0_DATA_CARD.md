# Phase 3.0 Data Card (Template)

> Per `docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md` §17.2 + §18.

이 문서는 **Phase 3.0 mini pilot이 종료된 후** 사용자가 작성하는 data card
*template*이다. v1.1 §18 acceptance §"Data Card 작성"에 매핑.

---

## 0. Template 사용법

```text
1. Phase 3.0 mini pilot (10 episodes) 완료 후 이 파일을 복사.
2. 모든 {{ ... }} placeholder를 실제 값으로 교체.
3. PHASE_3_0_DATA_PILOT_REPORT.md와 함께 검토.
4. 완성본은 docs/plans/PHASE_3_0_DATA_CARD_FILLED.md (또는 비슷한 이름)로 저장.
```

---

## 1. Pilot 메타

```text
이름:        Phase 3.0 Mini Pilot ({{ genre_id }})
버전:        v0.1
생성일:      {{ created_at }}
유지자:      {{ maintainer }}
의도된 용도:  Phase 3.1 weighted score baseline 입력
파일럿 모드: Mode A (수동 LLM annotation) | Mode B (승인 fetch) | Mode C (API)
의도하지 않은 용도:
  - 외부 배포 / 재공개
  - 원문 synopsis 재구성 (역추론 금지)
  - 학술 외 상업적 이용
```

---

## 2. 데이터 출처

| # | source_name | url | license_note | fetched_at | fetch_method | n_episodes |
|---|---|---|---|---|---|---|
| 1 | {{ source_1_name }} | {{ source_1_url }} | {{ source_1_license }} | {{ source_1_date }} | manual_input \| approved_fetch | {{ n }} |
| 2 | {{ source_2_name }} | ... | ... | ... | ... | ... |

**ToS / robots.txt 검토 결과** (DATA_SOURCE_CANDIDATE_REVIEW.md 표 인용):

```text
- {{ source_1_name }}: APPROVED_FOR_PILOT — robots.txt allow / ToS allows research use
- {{ source_2_name }}: ...
```

**원문 저장 정책**:

```text
- raw text storage: data/external_private/synopsis_raw/  (.gitignore 보호)
- public_safe_summary 길이 상한: 100자
- portfolio HTML 본문 인용: 0 (public_safe_dataset.jsonl에서 synopsis_text 제거)
```

---

## 3. 작품 / 회차 선정

```text
genre_id:           {{ genre_id }}        (e.g. korean_morning_melodrama)
titles:             {{ n_titles }}        (권장 1차: 2개)
episodes per title: {{ n_episodes_per_title }}  (권장 1차: 5개)
total episodes:     {{ n_total_episodes }}      (권장 1차: 10)
```

선정 사유:

```text
- {{ title_1_name }}: 장르 문법 대표성 / 회차별 독립성 / 갈등 변화 명확
- {{ title_2_name }}: ...
```

거절된 후보 (있을 시):

```text
- {{ rejected_title }}: 사유 (ToS 위반 / 저작권 위험 / 편향 등)
```

---

## 4. 어노테이션 방법

### 4.1 LLM 구성

```text
방식:           Mode A 수동 / Mode C API
어노테이터:     {{ annotator_list }}    (e.g. Claude-3.5-Sonnet + GPT-4o)
어노테이터 수:  {{ n_annotators }}      (권장 ≥ 2, 가능하면 3)
프롬프트:       scripts/data/build_annotation_inputs.py 가 생성
output schema:  episode_annotation_v1
features:       7 (Phase 3.0 §11)
              - conflict_intensity_peak
              - dangling_thread_generation
              - cliffhanger_strength
              - relationship_pressure
              - hidden_information_pressure
              - silence_or_avoidance
              - emotional_suppression
```

### 4.2 사람 spot-check

```text
spot-check 비율: {{ spot_check_pct }} %     (권장 ≥ 5%)
spot-check 결과:
  - 전체 일치: {{ n_match }}/{{ n_total }}
  - 일부 불일치: {{ n_partial }}/{{ n_total }}
  - 큰 불일치: {{ n_major }}/{{ n_total }}
```

---

## 5. Reliability 결과

### 5.1 Hallucination Quote Check (§16.1)

```text
total_quotes:        {{ total_quotes }}
verified:            {{ verified }}
hallucinated:        {{ hallucinated }}
hallucination_rate:  {{ hallucination_rate }}    (PASS if < 0.05, NO-GO if ≥ 0.10)
```

source: `data/annotation/phase3_pilot/reports/hallucination_report.json`

### 5.2 Inter-annotator Reliability (§16.2)

```text
n_records:    {{ n_records }}
n_annotators: {{ n_annotators }}
features:     {{ n_features }}

per-feature mean Pearson r:
  conflict_intensity_peak:        {{ r1 }}    {{ decision1 }}
  dangling_thread_generation:     {{ r2 }}    {{ decision2 }}
  cliffhanger_strength:           {{ r3 }}    {{ decision3 }}
  relationship_pressure:          {{ r4 }}    {{ decision4 }}
  hidden_information_pressure:    {{ r5 }}    {{ decision5 }}
  silence_or_avoidance:           {{ r6 }}    {{ decision6 }}
  emotional_suppression:          {{ r7 }}    {{ decision7 }}
```

source: `data/annotation/phase3_pilot/reports/reliability.json`

### 5.3 KEEP / REVISE / DROP 결정 (§16.3)

```text
KEEP:             {{ keep_features }}        (r ≥ 0.7)
REVISE:           {{ revise_features }}      (0.4 ≤ r < 0.7)
DROP:             {{ drop_features }}        (r < 0.4)
NEEDS_MORE_DATA:  {{ needs_more_features }}  (sample 부족)

Phase 3.1 진입 조건 (≥ 4 KEEP): {{ phase3_1_pass }}     PASS | NOT YET
```

---

## 6. 분할 (Phase 3.1 학습용)

10개 pilot은 분할이 어려울 수 있다. 현재 권장:

```text
훈련:  N/A (pilot 단계, 학습 안 함)
검증:  N/A
테스트: 10 (모두)

이후 40+ episodes 확장 시:
  훈련:  ~70%
  검증:  ~15%
  테스트: ~15%
  분할 단위: 작품 (회차 단위 분할 X — 누수 방지)
  seed:   {{ split_seed }}
```

---

## 7. 알려진 편향

```text
- 시대 편향:       {{ era_bias }}        (e.g. 2015-2020 한국 드라마)
- 채널 편향:       {{ channel_bias }}    (e.g. KBS / MBC / SBS 분포)
- 장르 편향:       1 genre pilot — cross-genre 일반화 불가
- title 편향:      2 titles pilot — title 내부 회차 간 상관 가능성
- 어노테이터 편향: LLM 한국어 능력 / 프롬프트 wording 영향
- 인물 편향:       특정 작품 인물군에 대한 LLM 사전 지식
```

---

## 8. 위험 / 한계

```text
- 표본 크기 (10 episodes) → r 추정치 불안정
- 1 genre 한정 → 다른 장르 일반화 X
- 수동 입력 mode면 사용자 입력 일관성에 의존
- evidence_quote 30자 미만이면 hallucination 검사 false negative 위험
- LLM 모델 버전 변경 시 재현성 저하 가능
```

---

## 9. 사용 제약

```text
- 학술 / 포트폴리오 용도로만 사용
- 재배포 금지 (외부 source ToS 별도 확인)
- 원문 시나리오 / 대사 본문 노출 금지
- portfolio HTML / 외부 send 시 public_safe_dataset.jsonl만 사용
- evidence_quote는 ≤ 30자, 내부 audit용 우선
```

---

## 10. 산출물 인덱스

```text
private (.gitignore):
  data/external_private/synopsis_raw/                            (raw input)
  data/annotation/phase3_pilot/normalized_synopsis.jsonl
  data/annotation/phase3_pilot/annotation_inputs/
  data/annotation/phase3_pilot/annotation_outputs/
  data/annotation/phase3_pilot/validated/

public (tracked):
  data/annotation/phase3_pilot/public_safe_dataset.jsonl
  data/annotation/phase3_pilot/features/feature_matrix.csv
  data/annotation/phase3_pilot/reports/reliability.json
  data/annotation/phase3_pilot/reports/hallucination_report.json
  docs/plans/PHASE_3_0_DATA_CARD.md                              (이 파일의 fill-in 사본)
  docs/plans/PHASE_3_0_DATA_PILOT_REPORT.md                      (pilot 보고서)
```

---

## 11. 변경 이력

| 버전 | 날짜 | 변경 |
|---|---|---|
| v0.1 | {{ created_at }} | Phase 3.0 mini pilot initial |

---

*이 카드는 데이터셋 변경 시마다 갱신한다. 변경 사유 + 영향 분석을 변경 이력에 기록.*
