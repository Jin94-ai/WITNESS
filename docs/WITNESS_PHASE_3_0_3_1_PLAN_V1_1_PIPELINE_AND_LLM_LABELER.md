# WITNESS Phase 3.0–3.1 Plan v1.1  
## Data Pipeline + LLM Annotation Pilot → Flesh Baseline

> 기준일: 2026-05-11  
> 목적: Phase 2.9까지 완성된 **SkeletonOutput + Rule-based Genre Adapter** 구조를  
> 실제 장르 줄거리 데이터와 annotation reliability 검증을 통해 **데이터 기반 Flesh Engine**으로 확장한다.  
>
> v1.1 보강 핵심: **Claude Code는 데이터 파이프라인, LLM은 라벨러, 사용자는 승인권자**로 역할을 분리한다.

---

## 0. 현재 위치

현재 WITNESS는 아래 단계까지 완료되었다.

```text
Phase 0    Skeleton Cleanup              DONE
Phase 1    Data Infra                    INFRA READY
Phase 2    Annotation Prep               PREP READY
Phase 2.5  Validation Fix                DONE
Phase 2.75 Genre Adapter MVP             DONE
Phase 2.8  Genre Adapter Polish          DONE
Phase 2.9  Portfolio Finalization        DONE
Phase 3.0  Data & Annotation Pilot       NEXT
Phase 3.1  ML / Flesh Baseline           AFTER 3.0 PASS
```

현재 확인 가능한 결과물:

```text
SkeletonOutput v1.1
→ Rule-based Genre Adapter
→ GenreComparisonOutput
→ demo_genre_comparison/index.html
```

즉, 현재는 **Rule-based Flesh**가 붙은 상태다.  
Phase 3부터는 실제 장르 데이터 기반으로 **Data-validated Flesh** 가능성을 검증한다.

---

## 1. 전체 목표

Phase 3.0–3.1의 최종 목표는 다음이다.

```text
실제 장르 줄거리 데이터
→ Claude Code 데이터 파이프라인
→ LLM annotation
→ quote / schema / reliability 검증
→ 신뢰 가능한 feature만 선별
→ 작은 Flesh Baseline
→ SkeletonOutput을 genre flesh decision에 연결
```

큰 방향:

```text
SkeletonOutput
→ Universal Story Skeleton
→ Genre Rulebook
→ Annotation Dataset
→ Genre Profile
→ Flesh Baseline
→ Genre Adaptation Recommendation
```

---

## 2. 핵심 운영 원칙

## 2.1 역할 분리

이번 단계부터 역할을 명확히 분리한다.

```text
Claude Code = 데이터 공장
LLM = 라벨러
User = 승인권자
```

### Claude Code가 담당할 것

```text
1. 데이터 source 후보 관리
2. ToS / robots.txt 검토 결과 기록
3. fetch 또는 수동 입력 데이터 저장
4. raw/private 경로 분리
5. public-safe metadata 생성
6. schema validation
7. 중복 제거
8. episode 단위 정렬
9. annotation input 생성
10. LLM annotation output 검증
11. evidence quote validation
12. feature_matrix.csv 생성
13. inter-annotator reliability 계산
14. report / data card 생성
```

### LLM이 담당할 것

```text
1. episode synopsis 읽기
2. feature score 부여
3. evidence quote 선택
4. confidence 부여
5. warning / ambiguity flag 작성
```

### 사용자가 결정할 것

```text
1. 어떤 source를 사용할지
2. 실제 fetch 승인 여부
3. LLM API 사용 여부
4. 비용 상한
5. raw synopsis 저장 위치
6. 공개 repo 정책
7. KEEP / REVISE / DROP 최종 판단
```

---

## 2.2 금지 원칙

아래 방식은 금지하거나 후순위로 둔다.

```text
- LLM에게 원문을 통째로 주고 “ML용 데이터로 정리해줘”라고 맡기기
- LLM이 data cleaning / schema / 저장 구조를 결정하게 하기
- mini pilot 검증 전 API 자동화부터 구현하기
- raw synopsis를 공개 repo에 저장하기
- 비용 상한 없이 LLM annotation 실행하기
- reliability 검증 없이 ML 학습 시작하기
```

이유:

```text
LLM에게 데이터 정제를 통째로 맡기면 재현성이 약하고,
같은 원문도 세션마다 다른 데이터셋으로 바뀔 수 있다.
ML용 데이터는 재실행 가능해야 하므로,
수집 / 정제 / 검증은 코드 파이프라인이 담당해야 한다.
```

---

## 2.3 API 없는 수동 annotation fallback

초기 10-episode pilot은 API 자동화 없이도 가능해야 한다.

파이프라인:

```text
raw/private synopsis
→ Claude Code가 annotation_inputs/*.json 생성
→ 사용자가 LLM에 수동으로 붙여넣기
→ LLM 응답을 annotation_outputs/*.json으로 저장
→ Claude Code가 schema / quote / reliability 검증
```

권장 디렉터리:

```text
data/annotation/phase3_pilot/annotation_inputs/
data/annotation/phase3_pilot/annotation_outputs/
data/annotation/phase3_pilot/validated/
data/annotation/phase3_pilot/reports/
```

장점:

```text
- API 비용 없이 pilot 가능
- 프롬프트 / 스키마 / feature 정의를 먼저 검증 가능
- 실패해도 비용 손실이 적음
- LLM API 자동화 전 품질 확인 가능
```

---

## 2.4 API 자동화는 후순위

LLM API 자동화는 다음 조건을 만족한 뒤에만 구현한다.

```text
[ ] 10-episode manual or semi-manual pilot 완료
[ ] annotation schema 안정
[ ] evidence quote hallucination rate < 5%
[ ] 최소 4개 feature에서 r >= 0.7
[ ] prompt template 수정 필요성이 낮음
[ ] 비용 상한 확정
```

그 이후에만 아래를 구현한다.

```text
scripts/annotation/run_llm_annotation.py
```

---

# PART A. Phase 3.0 — Data & Annotation Pilot

---

## 3. Phase 3.0 목표

Phase 3.0은 “많이 수집하는 단계”가 아니다.  
목표는 작게 검증하는 것이다.

```text
1. 실제 장르 synopsis를 안전하게 수집할 수 있는가
2. Claude Code 데이터 파이프라인이 재현 가능하게 작동하는가
3. annotation guide가 실제 줄거리에서 작동하는가
4. LLM annotator 간 일치도가 충분한가
5. evidence quote hallucination이 낮은가
6. 어떤 feature를 ML/Flesh Baseline에 넣을 수 있는가
```

---

## 4. Phase 3.0 승인 항목

Phase 3.0을 시작하기 전에 사용자 승인이 필요하다.

## 4.1 필수 승인 5건

```text
[ ] 실제 줄거리 데이터 fetch 승인
[ ] 출처별 ToS / robots.txt 검토 승인
[ ] LLM API 사용 승인 또는 수동 annotation 방식 승인
[ ] 비용 상한 승인
[ ] 저장 위치 / 공개 가능성 결정
```

## 4.2 보조 승인 2건

```text
[ ] 공개 repo 정책 승인
[ ] 10-episode mini pilot 범위 승인
```

승인 전 금지:

```text
- 실제 외부 fetch
- LLM API 호출
- 원문 synopsis 저장
- 모델 학습
- 공개 repo에 raw text 추가
```

---

## 5. Phase 3.0 Mini Pilot 범위

초기 pilot은 작게 잡는다.

```text
1 genre
2 titles
5 episodes per title
총 10 episode synopses
```

권장 장르:

```text
korean_morning_melodrama
```

이유:

```text
- 현재 rulebook이 가장 구체적이다.
- 장르 문법이 뚜렷하다.
- conflict / cliffhanger / dangling thread feature 검증에 적합하다.
```

확장 조건:

```text
10개 pilot에서 reliability 통과
→ 20개로 확장
→ 40개 cross-genre pilot
```

---

## 6. Phase 3.0 작업 모드

Phase 3.0은 세 가지 모드를 지원한다.

---

### Mode A — Manual Input Mode

외부 fetch 없이 사용자가 synopsis를 직접 넣는다.

```text
사용자 수동 수집
→ data/external_private/synopsis_raw/*.json 저장
→ Claude Code가 normalize / validate
```

장점:

```text
- ToS / robots 리스크 낮음
- 구현 빠름
- 10개 pilot에 적합
```

단점:

```text
- 반복 수집에는 비효율적
```

---

### Mode B — Approved Fetch Mode

사용자 승인 + ToS / robots 검토 후 fetch한다.

```text
source review
→ approved source
→ collect_synopsis CLI
→ raw private storage
→ public-safe metadata
```

장점:

```text
- 재현 가능
- 확장 가능
```

단점:

```text
- legal / ToS 검토 필요
- source별 구현 필요
```

---

### Mode C — API Annotation Mode

annotation input을 LLM API에 자동으로 보낸다.

```text
annotation_inputs/*.json
→ LLM API
→ annotation_outputs/*.json
→ validation
```

조건:

```text
manual/semi-manual pilot 통과 후에만
```

---

## 7. 데이터 소스 후보 검토

## 7.1 우선순위

```text
1. 공식 방송사 회차 소개
2. 공식 스트리밍 플랫폼 공개 synopsis
3. 위키 / 팬덤 요약
4. 개인 블로그 / 리뷰
```

권장:

```text
공식 방송사 / 공식 플랫폼 우선.
개인 블로그 / 리뷰는 저작권·품질·노이즈 문제로 비추천.
```

## 7.2 후보 검토표

문서:

```text
docs/plans/DATA_SOURCE_CANDIDATE_REVIEW.md
```

필드:

```text
source_name
title
genre
official_or_unofficial
url
robots_txt_status
tos_status
copyright_risk
fetch_method
fetch_difficulty
public_repo_allowed
recommended_use
notes
```

## 7.3 판정 등급

```text
APPROVED_FOR_PILOT
REVIEW_REQUIRED
DO_NOT_USE
```

---

## 8. 저장 정책

외부 원문은 공개 repo에 바로 넣지 않는다.

## 8.1 권장 디렉터리

```text
data/external_private/synopsis_raw/
data/annotation/phase3_pilot/
data/annotation/phase3_pilot/annotation_inputs/
data/annotation/phase3_pilot/annotation_outputs/
data/annotation/phase3_pilot/per_annotator/
data/annotation/phase3_pilot/features/
data/annotation/phase3_pilot/reports/
```

## 8.2 .gitignore 보호

아래는 반드시 gitignore에 있어야 한다.

```text
data/external_private/
data/annotation/phase3_pilot/per_annotator/
data/annotation/phase3_pilot/synopsis_cache/
data/llm_keys/
data/llm_call_logs/
```

권장 추가:

```text
data/annotation/phase3_pilot/annotation_inputs/
data/annotation/phase3_pilot/annotation_outputs/
```

단, public-safe fixture가 필요하면 별도 경로를 사용한다.

```text
tests/fixtures/annotation_public_safe/
```

## 8.3 공개 가능성

```text
Raw synopsis:
- 기본 비공개 / local-only
- 공개 repo 금지 권장

Annotation feature vector:
- 공개 가능성 있음
- 원문 재현 불가능한 numeric / categorical feature 중심

Derived metrics:
- 공개 가능

Evidence quote:
- 짧은 quote만 내부 audit용
- 공개 repo 노출은 별도 검토
```

---

## 9. 데이터 스키마

## 9.1 EpisodeSynopsisRecord

```json
{
  "record_id": "km_001_ep001",
  "genre_id": "korean_morning_melodrama",
  "title_id": "title_a",
  "episode_number": 1,
  "source_name": "official_broadcaster",
  "source_url": "",
  "source_license_note": "",
  "fetched_at": "2026-05-11",
  "raw_text_storage": "private",
  "synopsis_text": "",
  "public_safe_summary": "",
  "notes": ""
}
```

## 9.2 Public-safe version

공개용에는 raw synopsis를 넣지 않는다.

```json
{
  "record_id": "km_001_ep001",
  "genre_id": "korean_morning_melodrama",
  "title_id": "title_a",
  "episode_number": 1,
  "source_name": "official_broadcaster",
  "public_safe_summary": "redacted",
  "annotation_available": true
}
```

---

## 10. Claude Code 데이터 파이프라인

## 10.1 신규/보강 스크립트

```text
scripts/data/collect_synopsis.py
scripts/data/normalize_synopsis.py
scripts/data/validate_synopsis_dataset.py
scripts/data/build_annotation_inputs.py
scripts/data/build_public_safe_dataset.py
scripts/annotation/validate_annotation_outputs.py
scripts/annotation/build_feature_matrix.py
scripts/annotation/build_reliability_report.py
```

## 10.2 실행 흐름

```bash
# 1. raw synopsis 정규화
python scripts/data/normalize_synopsis.py \
  --input data/external_private/synopsis_raw \
  --output data/annotation/phase3_pilot/normalized_synopsis.jsonl

# 2. dataset validation
python scripts/data/validate_synopsis_dataset.py \
  --input data/annotation/phase3_pilot/normalized_synopsis.jsonl

# 3. annotation input 생성
python scripts/data/build_annotation_inputs.py \
  --input data/annotation/phase3_pilot/normalized_synopsis.jsonl \
  --output data/annotation/phase3_pilot/annotation_inputs

# 4. 수동 또는 API annotation 후 output 검증
python scripts/annotation/validate_annotation_outputs.py \
  --input data/annotation/phase3_pilot/annotation_outputs \
  --synopsis data/annotation/phase3_pilot/normalized_synopsis.jsonl

# 5. feature matrix 생성
python scripts/annotation/build_feature_matrix.py \
  --input data/annotation/phase3_pilot/annotation_outputs \
  --output data/annotation/phase3_pilot/features/feature_matrix.csv

# 6. reliability report 생성
python scripts/annotation/build_reliability_report.py \
  --features data/annotation/phase3_pilot/features/feature_matrix.csv \
  --output data/annotation/phase3_pilot/reports/reliability.json
```

---

## 11. Annotation Feature Set v1.1

Phase 2에서 준비한 feature set을 사용한다.  
단, Phase 3.0에서 reliability가 낮으면 drop한다.

필수 최소:

```text
1. conflict_intensity_peak
2. dangling_thread_generation
3. cliffhanger_strength
4. relationship_pressure
5. hidden_information_pressure
6. silence_or_avoidance
7. emotional_suppression
```

추가 후보:

```text
8. role_reversal_signal
9. public_suspicion_pressure
10. resolution_signal
```

---

## 12. Annotation Input Schema

Claude Code가 LLM에게 넘길 입력은 고정한다.

```json
{
  "task": "annotate_episode_synopsis_v1",
  "record_id": "km_001_ep001",
  "genre_id": "korean_morning_melodrama",
  "title_id": "title_a",
  "episode_number": 1,
  "synopsis_text": "...",
  "features_to_score": [
    "conflict_intensity_peak",
    "dangling_thread_generation",
    "cliffhanger_strength",
    "relationship_pressure",
    "hidden_information_pressure",
    "silence_or_avoidance",
    "emotional_suppression"
  ],
  "output_schema": "episode_annotation_v1"
}
```

---

## 13. Annotation Output Schema

```json
{
  "annotation_id": "ann_modelA_km_001_ep001",
  "record_id": "km_001_ep001",
  "annotator_id": "modelA",
  "genre_id": "korean_morning_melodrama",
  "features": {
    "conflict_intensity_peak": 4,
    "dangling_thread_generation": 5,
    "cliffhanger_strength": 4,
    "relationship_pressure": 3,
    "hidden_information_pressure": 2,
    "silence_or_avoidance": 4,
    "emotional_suppression": 3
  },
  "evidence_quotes": {
    "conflict_intensity_peak": ["..."],
    "dangling_thread_generation": ["..."]
  },
  "confidence": {
    "overall": 0.78
  },
  "warnings": []
}
```

---

## 14. Annotation 실행 방식

## 14.1 수동 LLM Annotation

초기 권장 방식.

```text
annotation_inputs/*.json
→ 사용자가 ChatGPT / Claude / 기타 LLM에 붙여넣기
→ 결과 JSON 저장
→ validate_annotation_outputs.py 실행
```

장점:

```text
- API 비용 없음
- 프롬프트 품질 수동 확인 가능
- 실패 시 빠른 수정 가능
```

## 14.2 API Annotation

후순위.

조건:

```text
manual pilot 통과 후
비용 상한 확정 후
```

실행 후보:

```text
scripts/annotation/run_llm_annotation.py
```

---

## 15. Annotator 구성

초기 권장:

```text
2-model pilot
```

가능하면:

```text
3-model pilot
```

주의:

```text
모델 이름은 실제 사용 승인 후 결정.
비용 상한 전에는 API 호출 금지.
```

실행 단위:

```text
10 episodes × 2 models = 20 annotation outputs
또는
10 episodes × 3 models = 30 annotation outputs
```

Human spot check:

```text
10 episodes 중 2개
또는 전체 annotation의 5–10%
```

---

## 16. Quality Checks

## 16.1 Hallucination quote check

조건:

```text
evidence quote가 원문에 실제 존재해야 함.
```

성공 기준:

```text
hallucination quote rate < 5%
```

No-Go:

```text
hallucination quote rate >= 10%
```

---

## 16.2 Inter-annotator reliability

측정:

```text
Pearson r
Spearman rho optional
feature-wise agreement
```

성공 기준:

```text
최소 4–5개 feature에서 r >= 0.7
```

주의:

```text
10개 pilot은 표본이 작으므로 r은 불안정하다.
그래도 feature별 방향성 확인용으로 사용한다.
```

---

## 16.3 Feature decision

각 feature를 아래로 분류한다.

```text
KEEP
REVISE
DROP
NEEDS_MORE_DATA
```

기준:

```text
KEEP:
- r >= 0.7
- hallucination low
- human spot check 통과

REVISE:
- r 0.4–0.7
- 정의가 애매한 경우

DROP:
- r < 0.4
- quote hallucination 많음
- annotator 간 해석 불일치

NEEDS_MORE_DATA:
- 표본 부족으로 판단 보류
```

---

## 17. Phase 3.0 산출물

## 17.1 코드 / 스크립트

```text
scripts/data/normalize_synopsis.py
scripts/data/validate_synopsis_dataset.py
scripts/data/build_annotation_inputs.py
scripts/data/build_public_safe_dataset.py
scripts/annotation/validate_annotation_outputs.py
scripts/annotation/build_feature_matrix.py
scripts/annotation/build_reliability_report.py
```

선택적 후순위:

```text
scripts/annotation/run_llm_annotation.py
```

---

## 17.2 문서

```text
docs/plans/PHASE_3_0_DATA_PILOT_REPORT.md
docs/plans/PHASE_3_0_FEATURE_RELIABILITY_REPORT.md
docs/plans/PHASE_3_0_DATA_CARD.md
docs/plans/PHASE_3_0_PIPELINE_OPERATING_GUIDE.md
```

---

## 17.3 데이터

```text
data/annotation/phase3_pilot/normalized_synopsis.jsonl
data/annotation/phase3_pilot/annotation_inputs/
data/annotation/phase3_pilot/annotation_outputs/
data/annotation/phase3_pilot/features/feature_matrix.csv
data/annotation/phase3_pilot/reports/reliability.json
data/annotation/phase3_pilot/reports/hallucination_report.json
```

---

## 17.4 공개용 산출물

```text
docs/portfolio/PHASE_3_0_PILOT_SUMMARY.md
```

주의:

```text
원문 synopsis는 공개하지 않는다.
```

---

## 18. Phase 3.0 Acceptance Criteria

```text
[ ] 사용자 승인 5+2건 완료
[ ] source 후보 ToS / robots.txt 검토 완료
[ ] 10 episode synopsis 확보
[ ] raw synopsis 저장 위치가 공개 repo 밖이거나 gitignore 보호됨
[ ] annotation_inputs/*.json 생성
[ ] 수동 또는 API annotation_outputs/*.json 확보
[ ] annotation output schema validation 통과
[ ] evidence quote hallucination rate < 5%
[ ] 최소 4개 feature에서 inter-annotator r >= 0.7
[ ] feature KEEP / REVISE / DROP 판정 완료
[ ] Data Card 작성
[ ] Phase 3.1 Go / No-Go 판정 작성
```

---

## 19. Phase 3.0 No-Go Criteria

```text
- ToS / robots.txt 검토 없이 fetch
- 원문 synopsis 공개 repo 저장
- 비용 상한 없이 LLM API 호출
- LLM에게 데이터 정제 전체 위임
- annotation input/output schema 없이 수동 라벨링 진행
- hallucination quote rate >= 10%
- r >= 0.7 feature가 3개 미만
- feature definition이 대량으로 흔들림
- data card 미작성
```

---

# PART B. Phase 3.1 — ML / Flesh Baseline

---

## 20. Phase 3.1 진입 조건

Phase 3.1은 Phase 3.0이 통과된 뒤에만 시작한다.

진입 조건:

```text
[ ] Phase 3.0 pilot report 완료
[ ] KEEP feature 최소 4개 이상
[ ] hallucination quote rate < 5%
[ ] raw data 공개/비공개 정책 확정
[ ] feature_matrix.csv 생성
[ ] train/validation split 가능
[ ] baseline target 정의
```

---

## 21. Phase 3.1 목표

Phase 3.1의 목표는 대형 모델이 아니다.  
작은 baseline으로 “학습 가능한 신호가 있는지” 보는 것이다.

목표:

```text
1. annotation feature로 genre mode를 분류할 수 있는가
2. 특정 skeleton이 어떤 genre flesh에 잘 맞는지 점수화할 수 있는가
3. rulebook adapter와 score를 결합할 수 있는가
4. 향후 Flesh Engine의 최소 target을 정의할 수 있는가
```

---

## 22. Phase 3.1 Model Targets

## 22.1 Target A — Genre Mode Classification

입력:

```text
annotation feature vector
```

출력:

```text
genre_id
```

MVP에서는 1 genre pilot이면 불가능하다.  
이 경우 Phase 3.1A는 보류한다.

---

## 22.2 Target B — Genre Intensity Score

입력:

```text
annotation feature vector
```

출력:

```text
genre_intensity_score
```

예:

```text
korean_melodrama_intensity: 0.0–1.0
quiet_drama_intensity: 0.0–1.0
```

10개 pilot에서도 간단한 rule/linear score 가능.

---

## 22.3 Target C — Adaptation Recommendation

입력:

```text
SkeletonOutput features
+ annotation-derived genre profile
```

출력:

```text
recommended_genre_modes
```

예:

```json
{
  "source_seed_id": "S01",
  "recommended_modes": [
    {
      "genre_id": "korean_morning_melodrama",
      "score": 0.78,
      "reason": "silence_or_avoidance + relationship_pressure high"
    }
  ]
}
```

---

## 23. Phase 3.1 모델 후보

## 23.1 No-ML Baseline

먼저 만든다.

```text
weighted rule score
```

예:

```text
melodrama_score =
  0.25 * conflict_intensity_peak
+ 0.25 * dangling_thread_generation
+ 0.20 * relationship_pressure
+ 0.15 * hidden_information_pressure
+ 0.15 * cliffhanger_strength
```

장점:

```text
- 데이터 적어도 가능
- 설명 가능
- rulebook과 연결 쉬움
```

---

## 23.2 Linear Baseline

```text
Logistic Regression
Ridge Regression
Linear SVM
```

조건:

```text
데이터가 최소 40개 이상일 때 추천.
10개 pilot에서는 과적합 위험 큼.
```

---

## 23.3 Tree Baseline

```text
Decision Tree
RandomForest
GradientBoosting
```

조건:

```text
데이터 100개 이상 전까지는 보류.
```

---

## 23.4 Neural Model

```text
MLP
Transformer
Fine-tuning
```

조건:

```text
Phase 3.1에서는 금지.
Phase 4 이후 검토.
```

---

## 24. Phase 3.1 추천 순서

```text
Step 1. No-ML weighted score
Step 2. score와 rulebook adapter 연결
Step 3. small linear baseline, 데이터가 충분할 때만
Step 4. error analysis
Step 5. Phase 3.2 여부 결정
```

---

## 25. Feature Engineering

입력 feature 후보:

```text
conflict_intensity_peak
dangling_thread_generation
cliffhanger_strength
relationship_pressure
hidden_information_pressure
silence_or_avoidance
emotional_suppression
```

Skeleton-derived feature:

```text
conflict_axis_id
dominant_pressures
dominant_desires
flow_role
arc_direction
relationship_function
turning_points_count
```

결합 feature:

```text
skeleton_pressure_overlap_with_genre_profile
skeleton_conflict_axis_compatibility
flow_role_to_genre_role_fit
cliffhanger_compatibility
```

---

## 26. Genre Profile v1

Phase 3.1에서 만들 핵심 산출물:

```json
{
  "genre_id": "korean_morning_melodrama",
  "profile_version": "genre_profile_v1",
  "feature_weights": {
    "conflict_intensity_peak": 0.25,
    "dangling_thread_generation": 0.25,
    "relationship_pressure": 0.20,
    "hidden_information_pressure": 0.15,
    "cliffhanger_strength": 0.15
  },
  "compatible_conflict_axes": [
    "loyalty_vs_survival",
    "uncertainty_vs_commitment",
    "trust_vs_self_protection"
  ],
  "compatible_pressures": [
    "public_suspicion",
    "authority_vigilance",
    "confusion",
    "shame_self"
  ]
}
```

---

## 27. Phase 3.1 Output Schema

```json
{
  "schema_version": "flesh_baseline_output_v1",
  "source_skeleton_id": "peter_scarcity_baseline",
  "genre_profiles_used": ["korean_morning_melodrama"],
  "recommendations": [
    {
      "source_seed_id": "S01",
      "genre_id": "korean_morning_melodrama",
      "score": 0.78,
      "fit_label": "strong_fit",
      "reason_features": [
        "authority_vigilance",
        "loyalty_vs_survival",
        "silence_or_avoidance"
      ],
      "recommended_adapter": "rulebook_v2_8"
    }
  ],
  "model": {
    "type": "weighted_rule_score",
    "trained": false,
    "data_source": "phase3_pilot"
  },
  "audit": {
    "raw_text_used": false,
    "evidence_preserved": true
  }
}
```

---

## 28. Phase 3.1 산출물

코드:

```text
engine/observer/flesh_baseline.py
engine/observer/genre_profile.py
scripts/narrative/build_genre_profiles.py
scripts/narrative/run_flesh_baseline.py
```

데이터:

```text
data/annotation/phase3_pilot/genre_profiles.json
data/narrative/flesh_baseline_output.json
```

문서:

```text
docs/plans/PHASE_3_1_FLESH_BASELINE_REPORT.md
docs/portfolio/FLESH_BASELINE_DEMO.md
```

데모:

```text
docs/portfolio/demo_flesh_baseline/index.html
```

---

## 29. Phase 3.1 Acceptance Criteria

```text
[ ] Phase 3.0 reliability report 통과
[ ] GenreProfile v1 생성
[ ] weighted score baseline 생성
[ ] SkeletonOutput seed별 genre fit score 생성
[ ] reason_features가 설명 가능
[ ] raw synopsis를 출력에 포함하지 않음
[ ] rule-based adapter와 연결 가능
[ ] demo_flesh_baseline/index.html 생성
[ ] baseline report 작성
```

---

## 30. Phase 3.1 No-Go Criteria

```text
- Phase 3.0 통과 전 학습 시작
- raw synopsis가 public output에 노출
- r 낮은 feature를 그대로 사용
- score reason이 설명 불가능
- 데이터 10개 이하로 복잡한 ML 모델 학습
- neural model 도입
- model card 없음
```

---

## 31. Phase 3.1에서 하지 않을 것

```text
- 대형 모델 학습
- fine-tuning
- full prose generation
- 대사 생성
- 장면 본문 생성
- 실제 작품 스타일 모방
- 장르별 완성 시나리오 생성
```

Phase 3.1은 **추천 / 점수 / 프로파일링**까지만 한다.

---

## 32. Phase 3.0–3.1 전체 실행 순서

```text
1. 사용자 승인 5+2건 받기
2. source candidate review 확정
3. ToS / robots.txt 검토
4. 10-episode synopsis 수집 또는 manual input
5. private raw storage
6. annotation_inputs 생성
7. manual or API annotation_outputs 확보
8. schema validation
9. evidence quote validation
10. inter-annotator reliability report
11. KEEP / REVISE / DROP feature 결정
12. Phase 3.0 Go / No-Go
13. GenreProfile v1 생성
14. weighted score baseline 작성
15. SkeletonOutput seed별 genre fit score 계산
16. demo_flesh_baseline 생성
17. Phase 3.1 report 작성
```

---

## 33. Phase 3.0 Agent Directive

```text
WITNESS Phase 3.0 — Data & Annotation Pilot directive

목표:
실제 장르 줄거리 데이터를 소규모로 수집하거나 수동 입력하고, Claude Code 데이터 파이프라인 + LLM labeler 구조로 annotation guide / feature reliability를 검증한다.

사전 승인:
- 실제 fetch 승인 또는 manual input mode 승인
- ToS / robots.txt 검토 승인
- LLM API 사용 또는 수동 annotation 방식 승인
- 비용 상한 승인
- 저장 위치 / 공개 가능성 승인
- 공개 repo 정책 승인
- 10-episode mini pilot 승인

제약:
- 승인 없는 fetch 금지
- 승인 없는 LLM API 호출 금지
- raw synopsis 공개 repo 저장 금지
- ML 학습 금지
- 10 episode를 넘는 수집 금지
- 저작권 있는 원문을 포트폴리오 HTML에 노출 금지
- LLM에게 데이터 정제 전체 위임 금지

작업:
1. DATA_SOURCE_CANDIDATE_REVIEW.md를 기준으로 source 또는 manual input mode를 선택한다.
2. robots.txt / ToS 검토 결과를 기록한다.
3. 2 titles × 5 episodes = 10 synopses를 수집 또는 수동 입력한다.
4. raw text는 private / gitignored 경로에 저장한다.
5. normalized_synopsis.jsonl을 생성한다.
6. annotation_inputs/*.json을 생성한다.
7. 수동 또는 API 방식으로 annotation_outputs/*.json을 확보한다.
8. annotation output schema를 검증한다.
9. evidence quote hallucination을 검사한다.
10. inter-annotator reliability를 계산한다.
11. feature별 KEEP / REVISE / DROP 판정을 한다.
12. PHASE_3_0_DATA_PILOT_REPORT.md를 작성한다.

Acceptance:
- hallucination quote rate < 5%
- r >= 0.7 feature 최소 4개
- data card 존재
- raw synopsis public output 노출 0
- Phase 3.1 Go / No-Go 판정 존재
```

---

## 34. Phase 3.1 Agent Directive

```text
WITNESS Phase 3.1 — ML / Flesh Baseline directive

목표:
Phase 3.0에서 검증된 annotation feature만 사용하여, SkeletonOutput seed가 어떤 genre flesh와 잘 맞는지 점수화하는 baseline을 만든다.

제약:
- Phase 3.0 Go 전 시작 금지
- neural model 금지
- fine-tuning 금지
- raw synopsis public output 노출 금지
- r 낮은 feature 사용 금지
- 대사 / 장면 본문 생성 금지

작업:
1. KEEP feature set을 로드한다.
2. genre_profile_v1을 생성한다.
3. weighted rule score baseline을 만든다.
4. SkeletonOutput seed별 genre fit score를 계산한다.
5. reason_features를 함께 출력한다.
6. flesh_baseline_output.json을 생성한다.
7. demo_flesh_baseline/index.html을 생성한다.
8. PHASE_3_1_FLESH_BASELINE_REPORT.md를 작성한다.

Acceptance:
- genre fit score 생성
- reason_features 설명 가능
- raw text 노출 0
- rule-based adapter와 연결 가능
- baseline report 존재
```

---

## 35. 최종 성공 정의

Phase 3.0–3.1이 성공하면 WITNESS는 이렇게 말할 수 있다.

```text
WITNESS는 시뮬레이션에서 이야기 뼈대를 뽑고,
장르 rulebook으로 1차 변환한 뒤,
실제 장르 데이터에서 검증된 feature profile을 사용해
어떤 장르적 살이 잘 맞는지 점수화한다.
```

이 시점부터 WITNESS는 단순 rule-based demo를 넘어:

```text
Data-validated Narrative Flesh Baseline
```

에 진입한다.

---

## 36. 한 줄 결론

Phase 3.0은 “데이터를 많이 모으는 단계”가 아니다.  
**Claude Code 데이터 파이프라인과 LLM labeler 구조가 실제로 작동하는지 확인하는 단계**다.

Phase 3.1은 “큰 ML 모델”이 아니다.  
**검증된 feature로 genre flesh fit을 점수화하는 작은 baseline**이다.

이 두 단계를 통과해야 비로소 본격적인 ML / Flesh Engine으로 넘어갈 수 있다.

---

*End of plan.*
