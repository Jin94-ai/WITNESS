# Data Card — {{ corpus_name }}

> Per `docs/witness_narrative_mode_plan.md` §5.6.
>
> 이 카드 자체가 포트폴리오의 한 자료다. 데이터셋 변경 시 갱신.

---

## 1. 기본 정보

```
이름:                {{ corpus_name }}
버전:                {{ version }}
생성일:              {{ created_at }}
유지자:              {{ maintainer }}
의도된 용도:         {{ intended_use }}
의도하지 않은 용도:  {{ explicitly_excluded_use }}
```

## 2. 출처 (Sources)

```
- 출처 1: {{ source_name }} ({{ source_url }})
  - 라이선스: {{ license }}
  - 수집 시점: {{ fetched_at }}
  - 수집 방법: {{ fetch_method }}  e.g. official wiki dump / API / scraping
- 출처 2: ...
```

원문 시나리오 / 대본은 *포함하지 않는다*. 회차 줄거리 / 학술 분석 / 위키
구조만 사용.

## 3. 작품 선정 기준

`docs/data/SELECTION_CRITERIA.md` 참조. 본 코퍼스의 선정 결과:

```
- 멜로드라마: {{ n_melodrama }}개 작품, 총 {{ n_melodrama_episodes }}개 회차
- 비교군:    {{ n_control }}개 작품, 총 {{ n_control_episodes }}개 회차
- 선정 사유 evidence:  {{ evidence_summary }}
- 거절된 후보 수:        {{ n_rejected }}
```

## 4. 어노테이션 방법

```
어노테이터 종류:    {{ annotators }}  e.g. Claude-3.5 + GPT-4 + Gemini-2 합성
어노테이션 가이드:  docs/annotation/ANNOTATION_GUIDE.md
사람 검증 비율:     {{ human_validation_pct }} %
일치도 지표:        {{ agreement_metric }}  e.g. Cohen's kappa = 0.78
```

## 5. 데이터 분할

```
훈련:  {{ n_train }} 회차 / {{ n_train_titles }} 작품
검증:  {{ n_val }} 회차 / {{ n_val_titles }} 작품
테스트: {{ n_test }} 회차 / {{ n_test_titles }} 작품

분할 단위: 작품 (회차 단위 분할 X — 누수 방지)
seed:    {{ split_seed }}
```

## 6. 알려진 편향

```
- 시대 편향:       {{ era_bias }}  e.g. 2010-2020 한국 드라마 중심
- 채널 편향:       {{ channel_bias }}
- 장르 편향:       {{ genre_bias }}
- 어노테이터 편향: {{ annotator_bias }}  e.g. LLM 프롬프트의 한국어 emphasis
```

## 7. 사용 제약

```
- 학술 / 포트폴리오 용도로만 사용
- 재배포 금지 (출처 사이트 ToS 별도 확인)
- 원문 시나리오를 본 코퍼스로부터 *역추론하려는 시도 금지*
```

## 8. 변경 이력

| 버전 | 날짜 | 변경 |
|---|---|---|
| {{ version }} | {{ created_at }} | initial |

---

*이 카드는 데이터셋의 모든 변경에 동기화 갱신되어야 한다.*
