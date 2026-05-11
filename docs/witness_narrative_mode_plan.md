# WITNESS Narrative Mode Refactor Plan

> 목표: WITNESS를 **베드로 특화 narrative demo**에서  
> **결정론적 서사 시뮬레이션 엔진(뼈대) + ML로 학습된 Narrative Mode 변환기(살)**의 이중 구조로 개편한다.

---

## 0. 한 줄 방향

```text
보편 서사 시뮬레이션(뼈대)
  → ML로 학습된 Narrative Mode(살)
  → 같은 시드를 다양한 전개 양식으로 변환
```

WITNESS는 이야기를 처음부터 지어내지 않는다.  
인간 삶의 압력과 관계 변화를 결정론적으로 시뮬레이션하고(뼈대),  
그 결과 위에 회차별 줄거리 코퍼스로 학습된 전개 동역학(살)을 입혀,  
같은 서사 시드를 다양한 Narrative Mode로 변환한다.

---

## 1. 프로젝트의 정체성 재정의

### 1.1 이 프로젝트가 풀려는 문제

기존 WITNESS는 다음 한계를 가진다.

```text
- Peter anchor 의존도가 높다.
- Story Seed가 인물명/정경 사건에 묶여 있다.
- 장르 변환 layer가 없다.
- "이야기 개요" 수준에 머물러 있다.
- rule/template 기반이라 하드코딩 의심을 받을 수 있다.
- ML이 적용되지 않은 순수 결정론적 시스템이다.
```

이번 개편은 위 한계를 다음 두 축으로 해결한다.

```text
축 1: 뼈대 엔진의 최소 범용화
  - 기존 시뮬레이션 자산을 거의 보존한다.
  - Peter 의존도만 떼어내어 anchor-agnostic하게 만든다.

축 2: 살 엔진의 ML 도입
  - 결정론적 변환 룰북이 아니라 학습된 모델을 사용한다.
  - 회차별 줄거리 코퍼스로부터 Narrative Mode를 학습한다.
  - 이를 통해 프로젝트에 실제 ML 적용 트랙을 만든다.
```

### 1.2 이 프로젝트가 포트폴리오에서 갖는 위치

```text
- 너의 multi-AI orchestration 패턴을 ML 어노테이션 파이프라인으로 활용한다.
- 너의 RTX 2070 SUPER / 4050 환경에 맞는 (b) Mid ML 규모로 설계한다.
- 결정론적 엔지니어링 자산 + ML 학습 파이프라인을 동시에 보여준다.
- 데이터 거버넌스, 어노테이션 설계, 평가 설계까지 포함된 end-to-end ML 프로젝트다.
```

---

## 2. 핵심 개념: Narrative Mode

### 2.1 왜 "장르"가 아니라 "Narrative Mode"인가

전통적 장르 라벨(로맨스/스릴러/가족극)은 **소재**에 대한 라벨이다.  
그러나 막장 드라마의 정체는 소재가 아니라 **전개 방식**이다.

```text
막장 드라마 = 평범한 소재(가족/연애/일상) + 극단적 전개(증폭/우연/폭로/극단화)
```

뼈대 엔진은 이미 압력·관계·선택의 동역학을 다루므로,  
그 위에 입혀야 할 것은 "어떤 소재인가"가 아니라 "어떻게 전개되는가"이다.

따라서 이 프로젝트에서는 "장르" 대신 **Narrative Mode**라는 용어를 사용한다.

```text
Narrative Mode = 서사가 어떻게 전개되는지를 결정하는 동역학적 양식
```

같은 시드에 다른 모드를 입히면, 같은 가족 상황도 잔잔한 일상극이 되거나 막장이 된다.

### 2.2 Narrative Mode의 3개 층위

학습 대상이 될 수 있는 층위는 셋이지만, MVP에서는 첫 두 층위만 다룬다.

| 층위 | 정체 | MVP 포함 |
|---|---|---|
| **전개 동역학** | 갈등 증폭률, 폭로 밀도, 우연 빈도, 극단화 패턴 | ✅ |
| **서사 문법** | 인물 역할 매핑, 장면 리듬, 클리프행어 구조 | ✅ |
| **문체** | 어휘, 문장 리듬, 톤 | ❌ (Phase 2 이후) |

문체는 (c) Heavy ML 영역(small LM fine-tuning)이라 MVP에서 제외한다.

### 2.3 Narrative Mode를 정량화하는 특성 벡터

학습의 입력/출력이 될 정량적 특성을 회차 단위로 정의한다.

```text
- 갈등 증폭률 (conflict_amplification_rate)
  : 회차 시작 대비 끝의 갈등 강도 비율

- 폭로 밀도 (revelation_density)
  : 회차당 새로 드러나는 숨겨진 사실의 수

- 우연 빈도 (coincidence_frequency)
  : 우연한 마주침/발견이 결정타가 되는 횟수

- 관계 극단화 (relationship_polarization)
  : 인물 관계가 중간 지대 없이 극과 극으로 가는 정도

- 새 갈등 도입률 (new_conflict_introduction_rate)
  : 회차당 새로 시작되는 갈등의 수

- 회수/방치 비율 (resolution_to_dangling_ratio)
  : 떡밥이 회수되는 비율 vs 방치되는 비율

- 클리프행어 강도 (cliffhanger_intensity)
  : 회차 말미 미해결 긴장의 강도
```

이 벡터가 Narrative Mode의 정량적 정의가 된다.

---

## 3. 아키텍처: 뼈대 엔진 + 살 엔진

### 3.1 분할의 근거

뼈대-살 분할은 단순한 코드 정리가 아니라, **두 엔진의 작동 원리가 근본적으로 다르기 때문에** 강제되는 분할이다.

| 측면 | 뼈대 엔진 | 살 엔진 |
|---|---|---|
| 패러다임 | 결정론적 | 비결정론적 (학습 기반) |
| 구현 방식 | Rule-based | ML-based |
| 의사결정 근거 | Evidence | Learned pattern |
| 출력 보장 | seed 동일 → 결과 동일 | 확률적 분포 |
| 검증 방식 | 단위 테스트 | 평가 지표 + 사람 검증 |

이 둘이 같은 코드베이스에 섞이면 검증 전략이 충돌하므로, 강하게 분리한다.

### 3.2 전체 구조

```text
[뼈대 엔진 — Skeleton Engine]
  Layer 1. Engine Core
    - 압력 기반 상태 변화
    - 다중 에이전트 루프
    - deterministic seed
  
  Layer 2. Universal Human Model
    - Pressure Taxonomy
    - Desire Model
    - Conflict Axis
  
  Layer 3. Story Seed Mining
    - UniversalStorySeed
    - EvidenceLedger
    - Anchor metadata는 별도 레지스트리로 분리

         ↓ SkeletonOutput contract ↓

[살 엔진 — Flesh Engine (ML)]
  Layer 4. Narrative Mode Models
    - Mode Classifier (회차 → 모드 점수)
    - Mode Transformer (시드 → 모드화된 시드)
    - Mode Evaluator (변환 결과 평가)
  
  Layer 5. Mode Application
    - 뼈대 시드 + 학습된 모드 → 모드화된 출력

         ↓

[Portfolio Surface]
  - 뼈대 결과
  - 모드 변환 결과
  - 학습 곡선 / 모델 카드
  - Evidence / Audit
```

### 3.3 두 엔진 사이의 Contract

뼈대-살 분할이 작동하려면 인터페이스를 먼저 동결해야 한다.

```python
@dataclass(frozen=True)
class SkeletonOutput:
    seeds: tuple[UniversalStorySeed, ...]
    flow: LifeStoryFlow | None
    evidence_ledger: EvidenceLedger
    anchor_metadata: AnchorMetadata | None  # anchor-specific 표현 (선택)
    audit_trail: AuditTrail
```

이 구조가 동결된 후에야 살 엔진 작업을 시작한다.

### 3.4 Life Story Flow의 소속

`LifeStoryFlow`는 뼈대 엔진에 둔다. 단, 정렬 규칙은 다음으로 한정한다.

```text
허용:
  - 압력 누적순
  - 관계 거리 변화순
  - 시뮬레이션 시간순
  - evidence-derived ordering

금지:
  - 장르적 리듬에 맞춘 재배치 (이건 살 엔진의 일)
  - 클리프행어를 위한 의도적 재배열
```

장르적 재배치가 필요하면 살 엔진이 다시 한다.

### 3.5 Anchor Metadata의 위치

뼈대 엔진은 universal seed만 출력한다. Peter / Vangogh / Talleyrand 같은 anchor-specific 표현은 별도 `AnchorRegistry`가 보관한다.

```text
AnchorRegistry
  - Peter: 이름, 갈릴리, 닭 울음 등
  - Vangogh: ...
  - Talleyrand: ...

뼈대 엔진은 universal seed만 뱉음.
포트폴리오 표면이 universal seed + AnchorRegistry를 결합해 anchor 버전을 렌더링.
```

이로써 뼈대는 anchor-clean 상태를 유지한다.

---

## 4. 살 엔진의 ML 설계

### 4.1 ML 규모: (b) Mid ML

세 가지 가능한 ML 깊이 중 (b)를 선택한다.

```text
(a) Light ML  : LLM prompt + few-shot. ML 프로젝트로서 약함.
(b) Mid ML    : 작은 분류기/추출기 직접 학습. RTX 2070/4050으로 가능. ★ 선택
(c) Heavy ML  : small LM fine-tuning. 욕심 과함, 검증 어려움.
```

### 4.2 학습할 모델의 종류

세 가지 모델을 단계적으로 만든다.

#### 4.2.1 Mode Classifier (α)

```text
입력: 회차 줄거리 (또는 회차 특성 벡터)
출력: Narrative Mode 분류 또는 점수
구현: gradient boosting, 작은 transformer
용도: 모드의 정량적 정의 + 다른 모델의 평가 도구
```

#### 4.2.2 Mode Evaluator (γ)

```text
입력: 뼈대 시드 + 변환된 출력
출력: "이 변환이 해당 모드답게 되었는가" 점수
구현: α를 활용 + 추가 휴리스틱
용도: β를 학습/검증할 때의 reward 또는 평가 지표
```

#### 4.2.3 Mode Transformer (β)

```text
입력: UniversalStorySeed (뼈대 출력)
출력: Mode-applied seed (살 출력)
구현: 시퀀스 변환 모델 또는 구조화 출력 LLM + 학습된 후처리
용도: 실제 모드 적용
```

### 4.3 학습 순서

```text
1. α (Classifier) 먼저
   - 정량적 모드 정의 확보
   - 데이터 어노테이션의 검증 도구

2. γ (Evaluator) 다음
   - α를 도구로 활용
   - β의 출력 품질을 평가할 척도 마련

3. β (Transformer) 마지막
   - α, γ가 평가 인프라로 작동
   - β부터 시작하면 평가 기준 없이 헤맴
```

이 순서가 핵심이다. β부터 시작하면 "이게 막장스러운가?"를 판단할 도구가 없어 검증이 불가능하다.

---

## 5. 데이터 수집 전략

### 5.1 핵심 원칙

```text
- 원문 시나리오/대본은 학습하지 않는다.
- 회차별 줄거리, 학술 분석, 위키 구조 분석을 주력으로 한다.
- multi-AI 어노테이션으로 정량 특성을 추출한다.
- 데이터 카드를 작성하여 출처와 라이선스를 명시한다.
```

### 5.2 데이터 소스별 평가

| 소스 | 적합도 | 저작권 | 용도 |
|---|---|---|---|
| 회차별 줄거리 (위키, EPG, 공식 사이트) | ★★★★★ | 사실 정보, 안전 | 주력 학습 데이터 |
| 학술 분석 / 비평 (KCI, 미디어 연구 논문) | ★★★★★ | 인용 범위, 안전 | 정량 패턴 참조 |
| 위키/팬덤 구조 분석 (나무위키 클리셰 섹션, TV Tropes) | ★★★★☆ | 라이선스 확인 필요 | 패턴 카탈로그 |
| 시청자 리뷰 / 실시간 반응 | ★★★☆☆ | 단편, 보통 안전 | 보조 신호 |
| 실제 대본 / 스크립트 | ★☆☆☆☆ | 위험 | 사용 안 함 |

### 5.3 수집 파이프라인

```text
1단계: 회차 줄거리 코퍼스 구축
  - 막장 드라마 10~20개 선정
  - 각 작품의 회차별 줄거리 수집
  - 결과: (작품ID, 회차번호, 줄거리텍스트, 메타데이터) 형태

2단계: 비교군 코퍼스 구축
  - "막장이 아닌" 드라마/소설의 회차 줄거리도 같은 방식으로 수집
  - 잔잔한 가족극, 정통 사극 등
  - 막장 모드를 학습하려면 "막장이 아닌 것"의 데이터가 반드시 필요

3단계: multi-AI 어노테이션
  - 각 회차 줄거리를 LLM(Claude/GPT/Gemini)에 입력
  - 정량 특성 벡터 추출:
    - 폭로 건수, 새 갈등 수, 우연 횟수, 극단화 정도 등
  - 여러 LLM 결과를 합성하여 신뢰도 확보 (multi-AI orchestration)

4단계: 사람 검증 샘플
  - 어노테이션 결과 일부를 직접 검토
  - LLM 어노테이션의 신뢰도 측정
  - 불일치 사례를 통해 어노테이션 가이드 개선

5단계: 학습 데이터셋 구축
  - 어노테이션된 회차 데이터를 학습 셋/검증 셋/테스트 셋으로 분할
  - 작품 단위로 분할하여 데이터 누수 방지
```

### 5.4 작품 선정 기준

```text
막장 드라마 분류:
  - 학술 논문/언론 기사에서 "막장"으로 명시적 분류된 작품만 사용
  - 위키 분류 카테고리 활용
  - 모호한 작품은 일단 제외

비교군 분류:
  - 같은 시기, 같은 채널, 같은 시간대의 "막장 아님" 작품 선택
  - 시대/플랫폼 편향 최소화
```

### 5.5 자동화의 안전선

```text
- robots.txt 준수
- 사이트 ToS 확인 (특히 나무위키, 위키피디아)
- 가능하면 공식 API/덤프 사용 (위키피디아는 공식 덤프 존재)
- 요청 간격 제한
- 수집 로그 보관
```

### 5.6 데이터 카드

각 데이터셋에 대해 다음을 문서화한다.

```text
- 출처 URL 및 수집 시점
- 라이선스
- 작품 선정 기준
- 어노테이션 방법 및 어노테이터 (LLM 모델 버전 포함)
- 사람 검증 비율
- 알려진 편향
- 사용 제약
```

이 데이터 카드 자체가 포트폴리오의 한 자료가 된다.

---

## 6. Implementation Phases

### Phase 0 — Contract & Skeleton Cleanup

**목표**: 뼈대-살 contract를 동결하고 뼈대 엔진을 최소 범용화한다.

```text
작업:
  - Pressure / Desire / Conflict Axis 보편 taxonomy JSON 작성
  - UniversalStorySeed 스키마 정의
  - SkeletonOutput contract 정의 및 동결
  - 기존 Peter seed → UniversalStorySeed 변환
  - AnchorRegistry 분리

산출물:
  - content/universal/pressure_taxonomy.json
  - content/universal/desire_taxonomy.json
  - content/universal/conflict_axes.json
  - engine/observer/universal_story_seed.py
  - engine/observer/skeleton_output.py
  - engine/anchor/anchor_registry.py

Acceptance:
  [ ] Peter 이름 없이도 universal seed가 의미를 유지한다.
  [ ] SkeletonOutput contract가 동결되었다 (이후 변경 시 별도 RFC 필요).
  [ ] Anchor 정보가 별도 레지스트리로 분리되었다.
  [ ] 기존 audit/evidence 규율이 유지된다.
```

### Phase 1 — 데이터 수집 인프라

**목표**: Narrative Mode 학습용 데이터 수집 파이프라인을 구축한다.

```text
작업:
  - 작품 선정 기준 문서 작성
  - 막장/비교군 작품 리스트 확정 (각 10~20개)
  - 회차 줄거리 수집 스크립트 작성
  - 데이터 저장 스키마 정의
  - 데이터 카드 템플릿 작성

산출물:
  - data/raw/melodrama/
  - data/raw/control/
  - scripts/data/collect_synopsis.py
  - docs/data/SELECTION_CRITERIA.md
  - docs/data/DATA_CARD_TEMPLATE.md

Acceptance:
  [ ] 막장 작품 10개 이상의 회차 줄거리가 수집되었다.
  [ ] 비교군 작품 10개 이상의 회차 줄거리가 수집되었다.
  [ ] 수집 출처와 라이선스가 명확히 기록되었다.
  [ ] robots.txt와 ToS가 준수되었다.
```

### Phase 2 — Multi-AI 어노테이션 파이프라인

**목표**: 회차 줄거리에서 정량 특성 벡터를 추출하는 어노테이션 파이프라인을 만든다.

```text
작업:
  - 어노테이션 가이드 작성 (어떤 특성을 어떻게 측정할지)
  - LLM 프롬프트 템플릿 설계 (Claude/GPT/Gemini용)
  - 합성 로직 구현 (여러 LLM 결과 → 단일 벡터)
  - 사람 검증 샘플링 도구
  - 어노테이션 신뢰도 측정 (Cohen's kappa 등)

산출물:
  - scripts/annotation/annotate_with_llm.py
  - scripts/annotation/synthesize_annotations.py
  - scripts/annotation/sample_for_human_review.py
  - docs/annotation/ANNOTATION_GUIDE.md

Acceptance:
  [ ] 모든 수집된 회차에 대해 정량 특성 벡터가 추출되었다.
  [ ] 사람 검증 샘플 (최소 5%)에서 LLM 어노테이션이 합리적인 수준이다.
  [ ] 어노테이션 가이드에 따라 재현 가능하다.
  [ ] 어노테이션의 신뢰도 지표가 기록되었다.
```

### Phase 3 — Mode Classifier (α) 학습

**목표**: 회차 줄거리/특성 벡터를 입력받아 Narrative Mode를 분류하는 모델을 학습한다.

```text
작업:
  - 학습/검증/테스트 셋 분할 (작품 단위)
  - 베이스라인 모델 학습 (gradient boosting)
  - 작은 transformer 모델 학습 (선택)
  - 평가 지표 정의 (정확도, F1, AUC)
  - 혼동 행렬 분석

산출물:
  - models/mode_classifier_v1/
  - notebooks/classifier_training.ipynb
  - reports/classifier_evaluation.md
  - 모델 카드

Acceptance:
  [ ] 분류기가 막장/비교군을 베이스라인 이상으로 구분한다.
  [ ] 검증 셋 / 테스트 셋 성능이 기록되었다.
  [ ] 어떤 특성이 가장 영향력 있는지 분석되었다.
  [ ] 모델 카드가 작성되었다.
```

### Phase 4 — Mode Evaluator (γ) 구축

**목표**: Mode 변환 결과의 품질을 평가하는 도구를 만든다.

```text
작업:
  - α를 활용한 평가 함수 정의
  - 추가 휴리스틱 평가 (전개 동역학 일관성, evidence 보존 등)
  - 평가 리포트 템플릿
  - 사람 평가와의 상관 측정

산출물:
  - engine/flesh/mode_evaluator.py
  - notebooks/evaluator_validation.ipynb
  - docs/evaluation/EVALUATION_PROTOCOL.md

Acceptance:
  [ ] Evaluator가 임의의 (시드, 변환결과) 쌍에 점수를 매길 수 있다.
  [ ] Evaluator 점수가 사람 평가와 상관성을 가진다.
  [ ] 평가 프로토콜이 문서화되었다.
```

### Phase 5 — Mode Transformer (β) 학습

**목표**: 뼈대 시드를 받아 Narrative Mode가 적용된 시드로 변환하는 모델을 만든다.

```text
작업:
  - 변환 입출력 스키마 정의
  - 학습 데이터 구축 (universal seed ↔ mode-applied seed 쌍)
  - 변환 모델 학습 (구조화 출력 LLM + 학습된 후처리, 또는 시퀀스 모델)
  - γ를 사용한 출력 평가
  - audit 적용 (없는 사건 추가 금지 등)

산출물:
  - models/mode_transformer_v1/
  - engine/flesh/mode_transformer.py
  - reports/transformer_evaluation.md

Acceptance:
  [ ] Transformer 출력이 원본 seed의 desire/conflict_axis를 보존한다.
  [ ] γ 평가에서 변환 후 모드 점수가 유의미하게 상승한다.
  [ ] audit에서 금지된 사건 추가가 없다.
  [ ] 검증 셋에서의 성능이 기록되었다.
```

### Phase 6 — 통합 및 포트폴리오 데모

**목표**: 뼈대 + 살 통합 데모를 포트폴리오 표면에 노출한다.

```text
작업:
  - 뼈대 엔진 출력 → 살 엔진 변환 → 결과 비교 데모
  - 학습 곡선, 모델 카드, 데이터 카드 노출
  - "원본 시드 vs 모드 적용 시드" 비교 UI
  - evidence/audit 토글 유지

산출물:
  - docs/portfolio/demo_skeleton/
  - docs/portfolio/demo_mode/
  - docs/portfolio/demo_comparison/

Acceptance:
  [ ] Peter 없이도 의미 있는 universal seed가 표시된다.
  [ ] Mode 변환 결과가 원본 seed를 보존한다.
  [ ] 학습 과정과 모델 성능이 투명하게 노출된다.
  [ ] evidence/audit 토글이 유지된다.
```

---

## 7. 평가 및 검증 전략

### 7.1 뼈대 엔진 검증 (기존 유지)

```text
- Hardcoding audit (grep 기반)
- Seed sensitivity (같은 evidence → 같은 결과)
- Anchor 독립성 (Peter 이름 없이도 작동)
- Evidence 보존
```

### 7.2 살 엔진 검증 (신규)

```text
- 어노테이션 신뢰도 (LLM 간 일치도, 사람과의 일치도)
- 분류기 성능 (정확도, F1, AUC, 혼동 행렬)
- 변환 품질 (γ 점수, 사람 평가)
- Mode preservation (변환 후에도 원본 desire/conflict_axis 유지)
- Mode overreach audit (없는 사건 추가 여부)
```

### 7.3 통합 검증

```text
- 같은 universal seed에 다른 mode 적용 → 다른 결과
- 같은 universal seed에 같은 mode 재적용 → 안정적 결과
- 학습 데이터 누수 검사
```

---

## 8. MVP 범위

### 8.1 포함

```text
- 뼈대 엔진 최소 범용화 (Phase 0)
- 막장 모드 데이터 수집 (Phase 1)
- multi-AI 어노테이션 파이프라인 (Phase 2)
- Mode Classifier α (Phase 3)
- Mode Evaluator γ (Phase 4)
- 간소한 Mode Transformer β v1 (Phase 5)
- 통합 데모 (Phase 6)
```

### 8.2 제외

```text
- 문체 학습 (small LM fine-tuning)
- 실제 대본/스크립트 학습
- 복수 모드 동시 학습 (막장 외 모드는 비교군 역할만)
- 대사 생성
- 긴 소설 draft 생성
- 웹앱/GUI
- RAG corpus 구축
```

### 8.3 향후 확장

```text
- 두 번째 Narrative Mode 학습 (예: 잔잔한 일상극, 웹소설 등)
- 모드 간 비교 평가
- 문체 층위 학습 (Phase 2 프로젝트로 분리)
- 사용자 평가 수집 시스템
```

---

## 9. 리스크와 대응

### 9.1 데이터 부족

```text
리스크: 회차 줄거리만으로 충분한 신호가 안 나올 수 있음.
대응:
  - 학술 분석 / 위키 구조 카탈로그를 보조 데이터로 활용
  - 어노테이션 특성을 줄이고 핵심 몇 개에 집중
  - Few-shot 평가로 데이터 효율 확인
```

### 9.2 어노테이션 일관성 문제

```text
리스크: LLM 어노테이션이 흔들려서 학습 신호가 노이즈에 묻힘.
대응:
  - multi-AI 합성으로 신뢰도 향상
  - 어노테이션 가이드를 충분히 구체화
  - 사람 검증 비율 늘리기
  - 일치도 낮은 특성은 제거
```

### 9.3 저작권 / 라이선스 문제

```text
리스크: 데이터 수집 과정에서 의도치 않은 ToS 위반.
대응:
  - 사용 전 출처별 ToS 확인
  - 수집 로그와 라이선스 기록 의무화
  - 가능하면 공식 API/덤프 사용
  - 의심스러운 출처는 제외
```

### 9.4 ML 검증의 어려움

```text
리스크: "막장스러움"이 주관적이라 모델 평가가 흔들림.
대응:
  - 정량 특성 벡터로 객관화
  - 사람 평가는 다중 평가자로 수집 (가능한 범위에서)
  - 평가 프로토콜을 사전 동결
  - 분류기 성능을 평가의 1차 척도로 활용
```

### 9.5 뼈대 엔진의 침범

```text
리스크: 살 엔진 작업 중 뼈대 contract를 자꾸 건드리게 됨.
대응:
  - SkeletonOutput contract를 Phase 0에서 명시적으로 동결
  - 변경 시 RFC 문서 작성 의무화
  - 살 엔진은 contract 외부에 의존하지 않음
```

### 9.6 프로젝트 비대화

```text
리스크: ML 욕심이 커져서 (c) Heavy ML로 표류.
대응:
  - MVP 범위를 (b) Mid ML로 못 박음
  - 문체 학습은 별도 프로젝트로 분리
  - 매 Phase 끝에 범위 점검
```

---

## 10. 디렉토리 구조 (제안)

```text
witness/
├── engine/
│   ├── core/               # (기존) 시뮬레이션 코어
│   ├── observer/           # (기존) Moment, Thread, Candidate
│   ├── universal/          # (신규) Universal taxonomy
│   ├── anchor/             # (신규) AnchorRegistry
│   └── flesh/              # (신규) ML-based mode 변환
│       ├── classifier.py
│       ├── evaluator.py
│       └── transformer.py
├── content/
│   ├── universal/          # 보편 taxonomy JSON
│   └── anchors/            # anchor-specific 표현
├── data/
│   ├── raw/
│   │   ├── melodrama/
│   │   └── control/
│   ├── annotated/
│   └── splits/
├── models/
│   ├── mode_classifier_v1/
│   └── mode_transformer_v1/
├── scripts/
│   ├── data/
│   ├── annotation/
│   └── narrative/
├── notebooks/
├── tests/
├── docs/
│   ├── plans/
│   ├── data/
│   ├── annotation/
│   ├── evaluation/
│   └── portfolio/
└── README.md
```

---

## 11. 포트폴리오 메시지

### 11.1 한 줄 설명

```text
WITNESS는 결정론적 서사 시뮬레이션 엔진(뼈대) 위에,
회차별 줄거리 코퍼스로 학습된 Narrative Mode 모델(살)을 얹어,
같은 시드를 다양한 전개 양식으로 변환하는 시스템이다.
```

영문:

```text
WITNESS combines a deterministic narrative simulation engine (skeleton)
with ML-trained Narrative Mode models (flesh), enabling the same story seed
to be transformed into different storytelling modalities.
```

### 11.2 강조할 기술 요소

```text
- 결정론적 시뮬레이션 + ML 학습의 하이브리드 아키텍처
- multi-AI orchestration을 활용한 어노테이션 파이프라인
- 데이터 거버넌스 (선정 기준, 데이터 카드, 어노테이션 가이드)
- 평가 인프라를 먼저 구축한 후 변환 모델을 학습한 설계 순서
- end-to-end ML 프로젝트 (데이터 수집 → 어노테이션 → 학습 → 평가 → 통합)
```

### 11.3 대학원 트랙에서의 의미

```text
- AGI / world model 관심사와 연결: 시뮬레이션 + 학습된 변환의 이중 구조
- ML 실전 적용 경험: 단순 응용이 아니라 데이터셋 구축부터 평가까지
- 아키텍처 설계 능력: 두 패러다임의 분리와 contract 설계
- 연구적 자세: 평가 도구를 먼저 만들고 모델을 학습하는 순서
```

---

## 12. 다음 실행 directive

```text
WITNESS Narrative Mode refactor directive:

1차 목표는 Phase 0과 Phase 1을 동시에 시작하는 것.
- Phase 0: 뼈대 엔진의 SkeletonOutput contract 동결 + Peter seed의 universal 변환
- Phase 1: 막장 / 비교군 회차 줄거리 수집 시작 (작품 선정 기준 확정 먼저)

제약:
- 뼈대 엔진의 시뮬레이션 로직은 변경하지 않는다.
- 실제 대본/스크립트는 학습 데이터에서 제외한다.
- ML 규모는 (b) Mid ML로 한정한다.
- 문체 학습은 이번 MVP에서 다루지 않는다.
- 평가 도구(α, γ) 없이 변환 모델(β)을 먼저 만들지 않는다.

Acceptance:
- Phase 0 완료 후 Peter 없이도 universal seed가 의미를 유지한다.
- Phase 1 완료 후 데이터 카드와 함께 raw 코퍼스가 존재한다.
- 두 phase 모두 audit/evidence 규율을 유지한다.
```

---

## 13. 결론

이번 개편의 본질은 다음 세 줄로 요약된다.

```text
1. 뼈대 엔진은 거의 그대로, anchor 의존성만 떼어낸다.
2. 살 엔진은 ML로 새로 짠다 — 학습된 Narrative Mode가 핵심.
3. "장르"는 소재가 아니라 전개 동역학(Narrative Mode)으로 재정의한다.
```

이 방향은 WITNESS를 단순 narrative demo가 아닌  
**결정론적 시뮬레이션과 ML 학습이 결합된 end-to-end 프로젝트**로 격상시킨다.

---

*End of plan.*
