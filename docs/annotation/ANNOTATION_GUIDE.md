# Multi-AI Narrative Mode Annotation Guide (Phase 2)

> Per `docs/witness_narrative_mode_plan.md` §5.3 + §5.4.
>
> 이 문서는 회차 줄거리에서 *Narrative Mode 정량 특성 벡터*를 추출하는
> 어노테이션 가이드. 어노테이터(LLM 또는 사람)는 이 가이드를 따라
> 일관된 결과를 산출해야 한다.

---

## 1. 어노테이션 대상

각 회차 줄거리(`data/raw/{cat}/{title}/episodes/{NN}.json`)에 대해 다음
**7개 정량 특성**을 매긴다 (Plan §2.3 참조).

```
1. conflict_intensity_peak       (갈등 강도 정점)         [0~5 레벨 / 5로 정규화]
2. revelation_density            (폭로 밀도)
3. coincidence_frequency         (우연 빈도)
4. relationship_polarization     (관계 극단화)
5. new_conflict_introduction_rate (새 갈등 도입률)
6. dangling_thread_generation    (미해결 생성률)         [0~5 레벨 / 5로 정규화]
7. cliffhanger_intensity         (클리프행어 강도)
```

각 특성은 **0.0 ~ 1.0** 범위의 숫자로 매긴다 (보간 가능).
1·6은 0~5 정수 레벨에서 어노테이트 후 `level/5`로 정규화한다.

> Phase 2.5 변경 (2026-05-09): `conflict_amplification_rate` →
> `conflict_intensity_peak` / `resolution_to_dangling_ratio` →
> `dangling_thread_generation`. 두 feature는 *회차 단위 측정 가능*하도록
> 재정의되었다. 마이그레이션 매핑은 `prompt_templates.DEPRECATED_FEATURE_RENAMES` 참조.

---

## 2. 특성별 측정 가이드

### 2.1 conflict_intensity_peak (0~5 레벨 / 5로 정규화)

**정의**: 해당 회차 줄거리 안에서 관측되는 갈등 누적/폭발의 *최대 강도*.

```
0  → 0.0  : 갈등 거의 없음
1  → 0.2  : 약한 긴장 또는 암시
2  → 0.4  : 명확한 갈등 존재
3  → 0.6  : 갈등이 여러 인물/관계로 확산
4  → 0.8  : 공개 충돌, 폭로, 관계 파탄 직전
5  → 1.0  : 회차의 중심이 강한 충돌·폭로·파국으로 구성됨
```

**측정 방법**: 회차 *전체* 줄거리에서 가장 강한 갈등 장면을 기준으로 한 번만
판단한다. *시작 대비 끝* 비교가 아니다 (Phase 2.5 변경).

> Deprecated: `conflict_amplification_rate` (시작/끝 비율은 회차 단위
> 텍스트만 보고 측정 시 variance가 컸음). 마이그레이션 시 자동 rename.

### 2.2 revelation_density (0.0 ~ 1.0)

**정의**: 회차당 새로 드러나는 *숨겨진 사실*의 수.

```
0.0  : 폭로 0건
0.2  : 1건의 작은 사실 폭로
0.5  : 1건의 큰 폭로 또는 2-3건의 중간 폭로
0.8  : 2건 이상의 큰 폭로 (출생의 비밀, 외도 발각, 살인 자백 등)
1.0  : 3건 이상의 큰 폭로 (정보 폭주)
```

**측정 방법**: 줄거리에서 "사실 X가 알려진다" / "Y가 발각된다" / "Z의
정체가 드러난다" 같은 표현을 카운트.

### 2.3 coincidence_frequency (0.0 ~ 1.0)

**정의**: 우연한 마주침/발견이 *결정타*가 되는 횟수.

```
0.0  : 우연 0건
0.3  : 1건의 작은 우연 (배경적)
0.5  : 1건의 결정적 우연 (회차의 turning point)
0.8  : 2건 이상의 결정적 우연
1.0  : 3건 이상의 결정적 우연 (회차 거의 모든 turning point가 우연 기반)
```

### 2.4 relationship_polarization (0.0 ~ 1.0)

**정의**: 인물 관계가 *중간 지대 없이* 극과 극으로 가는 정도.

```
0.0  : 모든 관계가 그라데이션 (애매한 거리, 미묘한 감정)
0.3  : 일부 관계만 극단적
0.5  : 절반 이상의 관계가 극단적
0.8  : 거의 모든 관계가 극단적 (완전한 사랑 vs 완전한 증오)
1.0  : 모든 주요 관계가 극단적, 중간 지대 0
```

### 2.5 new_conflict_introduction_rate (0.0 ~ 1.0)

**정의**: 회차당 *새로 시작되는* 갈등의 수.

```
0.0  : 새 갈등 도입 0건
0.3  : 새 갈등 1건
0.5  : 새 갈등 2건
0.8  : 새 갈등 3건 이상
1.0  : 새 갈등 4건 이상 (정보 폭주에 가까움)
```

### 2.6 dangling_thread_generation (0~5 레벨 / 5로 정규화)

**정의**: 해당 회차에서 *새롭게 남겨진* 미해결 질문/의심/비밀/오해/다음 회차로
넘어가는 갈등의 수와 강도.

```
0  → 0.0  : 미해결 질문 없음
1  → 0.2  : 약한 암시 1개
2  → 0.4  : 분명한 미해결 질문 1건
3  → 0.6  : 미해결 갈등 2건 이상
4  → 0.8  : 주요 관계/비밀이 다음 회차로 강하게 넘어감
5  → 1.0  : 회차 말미가 거의 클리프행어 중심
```

**측정 방법**: 회차 *내부에서 새롭게 생성된* 미해결 thread만 카운트.
이전 회차의 회수 비율은 대상 아니다 (단일 회차 단위 측정 가능성 보장).

> Deprecated: `resolution_to_dangling_ratio` (이전 회차 떡밥 회수 시점은
> 단일 회차 텍스트만으로 측정 불가능). 보조 feature가 필요하면 향후
> `resolved_prior_thread_count`를 별도 도입한다.
> (주의: 막장 모드는 *높은* dangling_thread_generation을 보이는 경향)

### 2.7 cliffhanger_intensity (0.0 ~ 1.0)

**정의**: 회차 *말미*의 미해결 긴장 강도.

```
0.0  : 회차가 깔끔하게 끝남 (cliffhanger 없음)
0.3  : 약한 미해결 (다음 회차로 자연스럽게 이어짐)
0.5  : 중간 정도 cliffhanger (한 사건 미해결)
0.8  : 강한 cliffhanger (여러 사건 미해결, 충격적 마지막 장면)
1.0  : 극단적 cliffhanger (정체 폭로 직전 컷 등)
```

---

## 3. 어노테이션 절차

### 3.1 입력 형식

각 회차 JSON 하나당 한 어노테이션 결과. 입력은 `synopsis_text_ko`만 본다.
원본 시나리오 / 대본은 보지 않는다.

### 3.2 출력 형식

```json
{
  "schema_version": "annotation_v1",
  "title_id": "string",
  "episode_no": 5,
  "annotator_id": "claude-3.5-sonnet | gpt-4 | gemini-2 | human:이름",
  "annotated_at_iso": "2026-05-09T...",
  "features": {
    "conflict_intensity_peak": 0.0,
    "revelation_density": 0.0,
    "coincidence_frequency": 0.0,
    "relationship_polarization": 0.0,
    "new_conflict_introduction_rate": 0.0,
    "dangling_thread_generation": 0.0,
    "cliffhanger_intensity": 0.0
  },
  "evidence_quotes": [
    {"feature": "revelation_density", "quote_ko": "줄거리에서 인용한 짧은 문장"}
  ],
  "confidence": 0.0,
  "notes": []
}
```

`evidence_quotes`는 **각 특성을 매긴 근거**를 줄거리에서 직접 인용한 짧은
문장. 어노테이션 검증 시 사람이 이를 보고 합리성 판단.

### 3.3 LLM 프롬프트 가이드

LLM 어노테이터에게 줄 때 다음을 지킨다:

1. *영어가 아닌 한국어 줄거리*임을 명시
2. 0.0 ~ 1.0 스케일과 anchor 점수를 가이드 §2의 정의 그대로 전달
3. evidence_quote는 줄거리 *원문에서* 인용 (LLM이 새로 만들어내면 안 됨)
4. confidence는 *어노테이터의 자기 평가* — 줄거리가 모호하면 낮춤
5. JSON only — 자유 텍스트 답변 금지

### 3.4 사람 검증 샘플링

전체의 최소 5%를 사람이 직접 어노테이션 → LLM 결과와 비교. 일치도 측정 시
Cohen's kappa 또는 Pearson correlation 사용 (각 특성별 별도 측정).

기준:
- kappa ≥ 0.6 또는 r ≥ 0.7 → 신뢰 가능
- 그 미만 → 가이드 개선 또는 해당 특성 제외

### 3.5 multi-AI 합성

여러 LLM (Claude / GPT / Gemini) 어노테이션을 합성할 때:

```
1. 각 어노테이터의 features 평균 (산술 평균 또는 중앙값)
2. confidence는 어노테이터 *간 일치도*로 계산 (분산이 작을수록 높음)
3. evidence_quotes는 union (모든 어노테이터의 인용 모음)
4. 최종 합성 결과를 별도 JSON으로 저장
```

---

## 4. 어노테이션 결과 저장 위치

```
data/annotated/{title_id}/{episode_no:02d}.json
   - 합성된 최종 어노테이션 (각 회차별 1개 파일)

data/annotated/_per_annotator/{annotator_id}/{title_id}/{episode_no:02d}.json
   - 어노테이터별 raw 결과 (감사 보존)
```

---

## 5. Phase 2 acceptance 매핑

Plan §6 Phase 2 acceptance 항목과 매핑:

| 항목 | 본 가이드 §섹션 |
|---|---|
| 모든 회차에 정량 특성 벡터 추출 | §2 (7 features 정의) + §3 (절차) |
| 사람 검증 샘플 (최소 5%)에서 LLM 어노테이션 합리적 | §3.4 |
| 어노테이션 가이드 따라 재현 가능 | §2 + §3 (전체 가이드) |
| 어노테이션 신뢰도 지표 기록 | §3.4 (kappa / Pearson) |

---

## 6. Phase 3.0 v1.1 § 11 — 신규 narrative pressure features (additive, 2026-05-11)

> Per `docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md` §11.
>
> Phase 3.0 mini pilot에서 사용할 *narrative pressure 중심* feature 4개를
> 추가한다. 기존 §1-§5의 v1.1 set은 backward-compat용으로 유지하되, Phase 3.0
> annotation_inputs (`scripts/data/build_annotation_inputs.py`)는 이 v1.2 set을
> 기본 사용한다.
>
> 모두 0-5 정수 레벨로 평가하고 `level/5`로 정규화한다.

### 6.1 cliffhanger_strength (0~5 레벨, v1.1 cliffhanger_intensity 대체)

**정의**: 회차 *말미*의 미해결 긴장이 다음 회차 진입을 견인하는 강도.

```
0 → 0.0 : 깔끔히 끝남 (cliffhanger 없음)
1 → 0.2 : 약한 미해결 (자연 연결)
2 → 0.4 : 한 사건 미해결
3 → 0.6 : 여러 사건 미해결
4 → 0.8 : 강한 cliffhanger (충격적 마지막 장면)
5 → 1.0 : 극단적 cliffhanger (정체 폭로 직전 cut 등)
```

> 명칭 변경 사유: Phase 3.0 §11이 `cliffhanger_strength` 명시. v1.1
> `cliffhanger_intensity`와 *의미는 동일*. annotation_outputs schema는 둘 다
> 허용.

### 6.2 relationship_pressure (0~5 레벨)

**정의**: 인물 간 *관계*에서 발생하는 압력의 강도 (가족/연인/직장 등).

```
0 → 0.0 : 관계 압력 거의 없음
1 → 0.2 : 약한 거리감 / 미세한 긴장
2 → 0.4 : 명확한 관계 긴장 (한 관계)
3 → 0.6 : 관계 긴장이 여러 인물로 확산
4 → 0.8 : 공개 충돌 직전 / 관계 파탄 임박
5 → 1.0 : 회차의 중심이 관계 파탄/충돌
```

### 6.3 hidden_information_pressure (0~5 레벨)

**정의**: 숨긴 진실/비밀이 인물에게 가하는 압력의 강도. 비밀 *내용*이 아닌
*존재 자체*가 만드는 압력.

```
0 → 0.0 : 숨긴 정보 없음
1 → 0.2 : 약한 비밀 (사소한 미공개)
2 → 0.4 : 분명한 비밀 1건
3 → 0.6 : 비밀 2건 이상 + 압박
4 → 0.8 : 주요 비밀이 여러 인물 사이에 작용
5 → 1.0 : 비밀이 회차 전체를 지배
```

### 6.4 silence_or_avoidance (0~5 레벨)

**정의**: 인물이 *말하지 않음 / 자리 피함 / 결정 미룸*의 강도.

```
0 → 0.0 : 인물이 모두 행동/말함
1 → 0.2 : 약한 회피 (한 순간 침묵)
2 → 0.4 : 명확한 회피 (한 인물의 침묵)
3 → 0.6 : 여러 인물의 회피
4 → 0.8 : 중심 인물의 지속적 침묵
5 → 1.0 : 침묵/회피가 회차의 중심 사건
```

### 6.5 emotional_suppression (0~5 레벨)

**정의**: 인물이 감정을 *눌러두는* 강도. 표면은 평온하지만 안에서 누적되는 정도.

```
0 → 0.0 : 감정 표현 자유롭음
1 → 0.2 : 약한 억제 (한 장면)
2 → 0.4 : 명확한 억제 (한 인물)
3 → 0.6 : 여러 인물의 억제
4 → 0.8 : 중심 인물의 지속적 억제
5 → 1.0 : 억제가 회차의 중심
```

### 6.6 사용 (Phase 3.0 §11 7-feature set)

`scripts/data/build_annotation_inputs.py`의 `DEFAULT_FEATURES_TO_SCORE`:

```python
(
    "conflict_intensity_peak",         # §2.1 (v1.1 유지)
    "dangling_thread_generation",      # §2.6 (v1.1 유지)
    "cliffhanger_strength",            # §6.1 (v1.2 신규, v1.1 cliffhanger_intensity 대체)
    "relationship_pressure",           # §6.2 (v1.2 신규)
    "hidden_information_pressure",     # §6.3 (v1.2 신규)
    "silence_or_avoidance",            # §6.4 (v1.2 신규)
    "emotional_suppression",           # §6.5 (v1.2 신규)
)
```

v1.1 features (`revelation_density / coincidence_frequency /
relationship_polarization / new_conflict_introduction_rate`)은 *legacy
compat*용으로 `scripts/annotation/prompt_templates.py::ANNOTATION_FEATURES`
에 유지. 기존 Phase 2 prep 코드는 v1.1 set 그대로 작동.

---

## 7. 변경 이력

| 버전 | 날짜 | 변경 |
|---|---|---|
| v1 | 2026-05-09 | initial — 7 features + multi-AI 합성 절차 |
| v1.1 | 2026-05-09 | Phase 2.5: conflict_amplification_rate → conflict_intensity_peak (회차 단위 최대 강도, 0~5 레벨); resolution_to_dangling_ratio → dangling_thread_generation (회차 내 신규 미해결, 0~5 레벨) |
| v1.2 | 2026-05-11 | Phase 3.0 §11 — narrative pressure 4 features 추가 (relationship_pressure / hidden_information_pressure / silence_or_avoidance / emotional_suppression) + cliffhanger_strength로 명칭 정비 (additive, v1.1 features는 legacy compat 유지) |

---

*가이드 변경 시 기존 어노테이션 무효 가능. 변경 시 RFC 문서 작성 의무 (additive
feature는 RFC 불요, breaking change만 RFC).*
