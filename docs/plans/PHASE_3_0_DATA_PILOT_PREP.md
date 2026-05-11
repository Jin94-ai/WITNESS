# Phase 3.0 Data & Annotation Pilot — Prep

> Per `docs/WITNESS_PHASE_2_9_PORTFOLIO_FINALIZATION_AND_PHASE_3_PREP_PLAN.md` §6+§7.1.

이 문서는 Phase 3.0 (외부 데이터 사용 첫 단계)에 진입하기 *전*에 필요한 준비를
정리한다. 실제 fetch / LLM API / 저장 / 학습은 사용자 승인이 떨어진 후에만 시작한다.

---

## 1. 목적

```text
Phase 2.5 / 2.75 / 2.8까지의 contract와 어댑터는 외부 의존 0으로 작동을 증명했다.
Phase 3.0은 그 contract가 *실제 외부 데이터*에서도 견디는지를 작은 pilot으로 검증한다.
```

검증 대상:
- annotation feature definition의 회차 단위 측정 가능성
- LLM annotator의 신뢰도 (hallucination rate / inter-annotator r)
- evidence_quote의 출처 보존성
- skeleton output → annotation feature 매핑의 일관성

---

## 2. 범위

### 2.1 한다

```text
- 작은 양의 회차 줄거리 수집 (10 episodes, 1 genre, 2 titles)
- 2-3개 LLM 모델 multi-AI annotation
- evidence_quote hallucination 검사
- inter-annotator Pearson r 계산
- feature reliability grade
- 사람 5% 이상 spot-check
- data card 작성
```

### 2.2 하지 않는다

```text
- 처음부터 40+ episodes 대규모 수집
- 원문 synopsis를 공개 repo에 commit
- 대사 / 본문 인용을 길게 사용
- 특정 작품명을 portfolio HTML에 노출
- ML 학습 시작
- Phase 3.1 진입 (Phase 3.0 통과 후)
```

---

## 3. 승인 필요 항목

`PHASE_3_0_APPROVAL_CHECKLIST.md` 참조 — 5+2 승인.

---

## 4. 데이터 소스 후보

`DATA_SOURCE_CANDIDATE_REVIEW.md` 참조 — 후보 검토 표.

---

## 5. Pilot 크기

### 5.1 1차 (보수적)

```text
1 genre  (예: 한국 아침 막장 드라마 또는 일본 정적 드라마)
2 titles
5 episodes each
total: 10 episode synopses
```

### 5.2 2차 (1차 통과 후 확장)

```text
2 genres
2 titles each
10 episodes each
total: 40 episode synopses
```

### 5.3 정지 조건

1차에서 다음 중 하나라도 발생하면 2차로 확장하지 않는다:

```text
- hallucination quote rate ≥ 5%
- inter-annotator r < 0.7 (5+ features)
- evidence_quote가 원문 substring 매칭 < 95%
- ToS / robots.txt 위반 발견
- 원문 인용 과다 (LLM 응답이 본문 길게 quote)
```

---

## 6. 저장 정책

### 6.1 디렉토리 구조

```text
data/external_private/synopsis_raw/
  └── {genre}/{title}/{episode}.json
      (원문 synopsis — 비공개, .gitignore)

data/annotation/phase3_pilot/
  └── per_annotator/{annotator}/{title}/{episode}.json
  └── synthesized/{title}/{episode}.json   (multi-AI 합성)
  └── features/{title}_features.csv         (feature vector 추출)
  └── reports/reliability_report.md
```

### 6.2 공개 repo 정책

```text
원문 synopsis_raw/         → 비공개 (.gitignore)
per_annotator raw/         → 비공개 (.gitignore)
synthesized features/      → 공개 가능 (수치만)
reliability reports/       → 공개 가능
short evidence quotes      → 내부 audit용 우선; portfolio 노출 시 ≤ 30자
portfolio HTML 본문        → 원문 본문 노출 금지
```

### 6.3 .gitignore 추가 항목

```text
data/external_private/
data/annotation/phase3_pilot/per_annotator/
data/annotation/phase3_pilot/synopsis_cache/
```

---

## 7. Annotation 계획

### 7.1 입력

```text
- episode synopsis (synopsis_v1)
- genre label
- title metadata
- episode number
```

### 7.2 도구 (이미 구현)

```text
scripts/annotation/prompt_templates.py:
  - SYSTEM_PROMPT_KO
  - build_user_prompt_ko(synopsis_text_ko, episode_no, title_ko)
  - validate_annotation_dict(d, strict_levels=True)
  - validate_evidence_quotes(annotation, synopsis_text)
  - hallucination_rate(annotation, synopsis_text)
  - synthesize_annotations(annotations)
  - inter_annotator_correlation(annotations_per_episode)
  - reliability_grade(correlation)
  - migrate_deprecated_annotation(d)  # v1 → v1.1

scripts/annotation/annotate_with_llm.py:
  - dry-run mode  (build prompt, no network)
  - fixture mode  (validate + save real LLM response)
  - --migrate-deprecated  (v1 → v1.1 자동 변환)

scripts/annotation/synthesize_annotations.py:
  - --inputs  (multi-annotator JSONs)
  - --per-annotator-dir  (디렉토리 모드)
  - --migrate-deprecated

scripts/annotation/sample_for_human_review.py:
  - low_confidence / random_stratified
```

### 7.3 LLM 구성

```text
1차: 2-model pilot (예: Claude + GPT)
2차: 3-model (Claude + GPT + Gemini)
```

비용 상한 승인 후 결정.

### 7.4 출력

```text
data/annotation/phase3_pilot/synthesized/{title}/{episode}.json
data/annotation/phase3_pilot/features/features.csv
data/annotation/phase3_pilot/reports/reliability_report.md
```

---

## 8. 신뢰도 기준

### 8.1 통과 기준

```text
[ ] hallucination quote rate < 5%
[ ] inter-annotator Pearson r ≥ 0.7 for ≥ 4-5 features
[ ] evidence_quote substring 매칭 ≥ 95%
[ ] 사람 spot-check 5% 이상 일치
[ ] data card 완성 (출처 / 라이선스 / 어노테이션 / 분할 / 편향)
```

### 8.2 부분 통과 (feature drop)

```text
- r < 0.7인 feature는 제외하되 reason 명시
- prompt template 수정 후 재시도 가능
```

### 8.3 전체 fail

다음 중 하나가 발생하면 Phase 3.0 1차 fail, source 또는 prompt 재검토:

```text
- hallucination quote rate ≥ 10%
- 5개 미만 feature가 r ≥ 0.7
- ToS / robots.txt 위반
- 원문 인용 과다로 저작권 위험
```

---

## 9. 중단 조건

다음 시점에 즉시 중단:

```text
- 사용자 승인 5건 중 미승인 항목 발견
- 데이터 소스가 robots.txt를 disallow
- 데이터 소스가 ToS로 scrape 금지
- LLM API 비용이 상한 초과
- 원문 본문이 portfolio HTML에 노출됨
- 사용자가 직접 stop 요청
```

---

## 10. 산출물 (Phase 3.0 pilot 후)

```text
docs/plans/PHASE_3_0_RELIABILITY_REPORT.md
data/annotation/phase3_pilot/reports/reliability_report.md
data/annotation/phase3_pilot/features/features.csv
docs/portfolio/PHASE_3_0_DATA_CARD.md (또는 docs/data/{title}_data_card.md)
```

---

## 11. Phase 3.1 진입 조건

Phase 3.0 1차 + 2차 통과 후 Phase 3.1 ML/Flesh Engine 진입 가능:

```text
- hallucination < 5%
- inter-annotator r ≥ 0.7 for ≥ 5 features
- 40-episode dataset 확보
- data card 완성
- train/val split 결정
- baseline target 결정 (mode classification / genre intensity / adaptation recommendation)
- 사용자 ML 학습 비용 별도 승인
```

---

## 12. 한 줄 요약

```text
Phase 3.0은 "처음 외부 데이터를 만지는 단계"다.
큰 학습이 아니라 *작은 pilot*으로 신뢰도를 검증하는 것이 목표.
승인 후에야 실제 fetch가 시작된다.
```
