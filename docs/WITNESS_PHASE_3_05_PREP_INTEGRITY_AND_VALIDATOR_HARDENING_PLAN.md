# WITNESS Phase 3.05 — Prep Integrity & Validator Hardening Plan

> 기준일: 2026-05-11  
> 목적: Cycle 7–12에서 구현된 Phase 3.0/3.1 prep 산출물을 검수한 결과를 바탕으로, **prep 결과물이 실제 데이터 기반 추천처럼 보이지 않도록 정직성·검증성·운영 명확성을 보강한다.**

---

## 0. 현재 상태 판단

Cycle 7–12 진행은 전반적으로 정상이다.

현재 구현된 것은 다음이다.

```text
Phase 3.0 Mode A pipeline prep
- 수동 입력 기반 데이터 파이프라인
- annotation_inputs 생성
- annotation_outputs 검증
- quote hallucination 검사
- feature quote coverage 검사
- feature_matrix / reliability report 준비

Phase 3.1 No-ML baseline prep
- seed × genre profile fit
- episode × genre profile intensity
- flesh_baseline demo
- episode_intensity script / demo builder
```

다만 중요한 구분이 있다.

```text
현재 deploy된 것:
- data/narrative/phase3_1_demo/flesh_baseline_output.json
- data/narrative/phase3_1_demo/genre_profiles.json
- docs/portfolio/demo_flesh_baseline/index.html
- docs/portfolio/demo_flesh_baseline/baseline.md

현재 deploy 안 된 것:
- data/annotation/phase3_pilot/
- episode_intensity_output.json
- docs/portfolio/demo_episode_intensity/index.html
```

이 구분은 정상이다. `episode_intensity`는 구현되어 있지만 실제 Phase 3.0 데이터가 없으므로, fixture 기반 demo를 공개 deploy하지 않은 판단은 타당하다.

---

## 1. 핵심 결론

현재 상태는 정상이다. 하지만 다음 문제가 있다.

```text
flesh_baseline_output.json은 rulebook_only prep 결과인데,
모든 seed × genre score가 1.0 / strong_fit으로 표시된다.

이 상태를 그대로 보여주면 실제 annotation 기반 추천처럼 오해될 수 있다.
```

따라서 다음 작업은 새 기능 추가가 아니라:

```text
prep 결과물 정직성 보강
validator strict safety 보강
deploy 상태 문서화
```

이다.

---

## 2. 검수 요약

### 2.1 잘된 점

#### Operating Guide 구조가 좋다

`PHASE_3_0_PIPELINE_OPERATING_GUIDE.md`는 Step 1–9와 Step 10–13을 명확히 구분한다.

```text
Step 1–9   = Phase 3.0 데이터 / annotation 운영
Step 10–13 = Phase 3.1 baseline + demo
```

또한 다음 두 layer를 잘 구분한다.

```text
seed × profile fit
episode × profile intensity
```

이 구분은 계속 유지해야 한다.

#### 수동 LLM annotation flow가 현실적이다

현재 Mode A 흐름은 타당하다.

```text
raw synopsis
→ normalize
→ validate
→ annotation_inputs 생성
→ 사용자가 LLM에 붙여넣기
→ annotation_outputs 저장
→ validate_annotation_outputs.py
→ feature_matrix
→ reliability report
```

이 방식은 API 비용 없이 pilot을 검증할 수 있다.

#### quote hallucination + feature coverage 검사가 좋다

기존 quote hallucination check는 다음을 본다.

```text
LLM이 제시한 evidence quote가 원문에 실제 존재하는가?
```

Cycle 12에서 추가된 feature quote coverage는 다음을 본다.

```text
각 expected feature가 충분한 evidence quote를 받았는가?
```

즉, 이제 두 층이 생겼다.

```text
거짓 quote 방지
+
근거 없는 점수 방지
```

#### episode_intensity 구현 방향은 좋다

`episode_intensity_v1`은 long-form feature matrix를 record별 평균으로 모으고, GenreProfile의 feature weight를 적용해 0–1 intensity score를 만든다.

이 구조는 다음 원칙에 맞다.

```text
학습 0
fine-tuning 0
raw text 사용 0
annotation feature score만 사용
```

따라서 Phase 3.1 §22.2 Target B의 구현 방향은 타당하다.

---

## 3. 주요 문제점과 수정 방향

---

# Issue 1 — flesh_baseline_output이 실제 추천처럼 보일 위험

## 현재 상태

`flesh_baseline_output.json`은 `rulebook_only` prep 결과다.

현재 특징:

```text
data_source: rulebook_only
score: 1.0
fit_label: strong_fit
score_breakdown: {}
```

모든 seed × genre가 1.0으로 나온다.

이건 실제 annotation 기반 추천이 아니다. 정확한 의미는 다음에 가깝다.

```text
이 skeleton seed는 현재 rulebook과 구조적으로 호환된다.
```

하지만 현재 표면 표현은 다음처럼 보일 수 있다.

```text
이 장르가 이 seed에 매우 잘 맞는다고 모델이 판단했다.
```

이건 과장이다.

## 수정 방향

prep mode에서는 점수 의미를 바꿔 보여줘야 한다.

기존 표현:

```text
score
strong_fit
recommendation
```

권장 표현:

```text
rulebook_compatibility_score
compatibility_match
rulebook-only prep
```

기존 schema를 크게 깨지 않으려면 `score`는 유지하되 `score_breakdown`을 채운다.

```json
"score_breakdown": {
  "compatibility_score": 1.0,
  "axis_match": 0.5,
  "pressure_overlap": 0.5,
  "annotation_score": null,
  "final_score": 1.0,
  "mode": "rulebook_only"
}
```

HTML에서는 다음처럼 표시한다.

```text
strong_fit (rulebook-only)
```

또는:

```text
compatibility match
```

## Acceptance

```text
[ ] score_breakdown 빈 dict 0건
[ ] compatibility_score / annotation_score / final_score 구분
[ ] rulebook_only mode 명시
[ ] HTML에서 1.000 strong_fit이 실제 annotation 기반 추천처럼 보이지 않음
[ ] baseline.md에도 같은 설명 반영
```

---

# Issue 2 — score_breakdown이 비어 있음

## 문제

`score_breakdown: {}`는 설명 가능성을 약하게 만든다.

현재 HTML에는 “weighted score”처럼 보이지만, 실제 JSON에는 breakdown이 비어 있다.

이건 다음 불일치를 만든다.

```text
HTML: 설명 가능한 weighted score처럼 보임
JSON: score_breakdown 없음
실제 상태: rulebook_only compatibility
```

## 수정 방향

`run_flesh_baseline.py` 또는 `engine/observer/flesh_baseline.py`에서 `rulebook_only`일 때도 최소 breakdown을 생성한다.

권장 breakdown:

```json
{
  "axis_match": 0.5,
  "pressure_overlap": 0.5,
  "annotation_component": null,
  "compatibility_score": 1.0,
  "final_score": 1.0,
  "mode": "rulebook_only"
}
```

장르별 차별화가 아직 없다면 `score`는 유지하되, 명시적으로 한계를 표시한다.

```text
현재 점수는 rulebook의 compatible_conflict_axes / compatible_pressures와의 단순 호환성만 나타낸다.
Phase 3.0 annotation 데이터가 들어오면 annotation component가 추가된다.
```

## Acceptance

```text
[ ] 모든 recommendation이 non-empty score_breakdown 보유
[ ] axis_match / pressure_overlap 산출
[ ] annotation_component는 rulebook_only에서 null
[ ] demo와 JSON의 설명이 일치
```

---

# Issue 3 — fit_label이 prep mode에서 너무 확정적임

## 문제

`strong_fit`은 실제 데이터 기반 scoring이면 괜찮다. 하지만 `rulebook_only`에서 `strong_fit`은 너무 강하게 보인다.

## 수정 방향

두 가지 중 하나를 택한다.

### Option A — schema 유지, UI에서 보정

JSON:

```json
"fit_label": "strong_fit"
```

HTML:

```text
strong_fit (rulebook-only)
```

또는:

```text
compatibility match
```

### Option B — prep 전용 label 추가

JSON:

```json
"fit_label": "rulebook_compatible"
```

단, 이 경우 기존 enum / tests 수정이 필요할 수 있다.

권장:

```text
Option A
```

이유:

```text
schema 변경 최소화
기존 fit_label consumer 유지
UI와 docs에서 의미 보정
```

## Acceptance

```text
[ ] prep mode UI에서 strong_fit 단독 표시 없음
[ ] rulebook-only임이 카드와 matrix 양쪽에 표시됨
[ ] 실제 annotation 기반 score와 혼동되지 않음
```

---

# Issue 4 — validate_annotation_outputs.py strict safety 보강 필요

## 현재 상태

`validate_annotation_outputs.py`는 다음을 검사한다.

```text
schema
feature score
evidence quote substring match
record_id ↔ normalized_synopsis 일치
confidence
feature quote coverage
```

좋은 구조다.

하지만 strict mode에서 `--synopsis`가 없으면 quote validation이 의미 없어질 수 있다.

## 문제

quote validation은 원문 synopsis가 있어야 의미가 있다.

따라서 다음 실행은 위험하다.

```bash
python scripts/annotation/validate_annotation_outputs.py   --input data/annotation/phase3_pilot/annotation_outputs   --strict
```

이 경우 원문 비교 없이 hallucination check가 약해질 수 있다.

## 수정 방향

strict mode에서 synopsis가 없으면 실패하게 한다.

권장:

```text
--strict 상태에서 --synopsis 미지정이면 exit 2
```

또는 명시 옵션 추가:

```text
--require-synopsis-for-quotes
```

권장:

```text
strict mode 기본 동작으로 강제
```

## Acceptance

```text
[ ] --strict + --synopsis 없음 → exit 2
[ ] error message가 명확함
[ ] strict mode에서 quote hallucination 검사가 항상 원문 기반으로 수행됨
```

---

# Issue 5 — invalid file과 hallucination 통계 분리 필요

## 현재 가능 문제

schema error가 있는 annotation 파일이 hallucination aggregate에 섞이면 보고서 해석이 꼬일 수 있다.

현재 구조에서 schema invalid 파일도 per-file stats에 들어갈 가능성이 있다.

## 수정 방향

hallucination summary를 두 층으로 분리한다.

```json
{
  "all_files_summary": {},
  "valid_files_only_summary": {},
  "invalid_files": []
}
```

판정 기준:

```text
- threshold pass/fail은 valid_files_only 기준
- invalid file은 별도 fail로 처리
```

feature quote coverage도 valid files 기준으로 계산한다.

## Acceptance

```text
[ ] hallucination report에 valid_files_only_summary 존재
[ ] invalid_files 목록 존재
[ ] threshold 판정은 valid files only 기준
[ ] invalid files가 있으면 strict mode fail
[ ] feature coverage도 valid files 기준
```

---

# Issue 6 — episode_intensity는 deploy하지 않는 판단 유지

## 현재 상태

`episode_intensity.py`, `run_episode_intensity.py`, `build_episode_intensity_demo.py`는 구현되어 있다.

하지만 실제 `episode_intensity_output.json`과 `demo_episode_intensity/index.html`은 deploy되지 않았다.

이 판단은 타당하다.

이유:

```text
현재 episode intensity는 fixture 기반 prep으로만 가능하다.
실제 Phase 3.0 data가 없으므로 포트폴리오에 노출하면 실제 데이터 기반 분석처럼 보일 위험이 있다.
```

## 정책

```text
episode_intensity script: 유지
episode_intensity fixture tests: 유지
episode_intensity deploy output: 생성하지 않음
demo_episode_intensity: 실제 Phase 3.0 데이터 이후 생성
```

단, 사용자가 fixture demo를 원하면 다음 조건으로만 생성한다.

```text
- fictional fixture banner 필수
- prep-only 명시
- portfolio main에 노출 금지
- docs/portfolio/appendix 또는 scratch 위치
```

## Acceptance

```text
[ ] episode_intensity fixture demo를 메인 포트폴리오에 deploy하지 않음
[ ] Operating Guide에 deploy 조건 명시
[ ] 실제 Phase 3.0 데이터 후 생성하는 경로 명시
```

---

# Issue 7 — deploy 상태 문서화 필요

## 문제

이번 대화에서 혼란이 있었다.

```text
일부 요청 파일은 아직 deploy되지 않은 산출물이었다.
Claude Code는 이를 정상적으로 구분했다.
```

앞으로 같은 혼란을 막으려면 문서에 산출물 상태표가 있어야 한다.

## 수정 방향

`PHASE_3_0_PIPELINE_OPERATING_GUIDE.md`에 deploy 상태표 추가.

표:

```text
산출물 | 현재 상태 | 생성 조건 | 공개 가능 여부 | 비고
```

예:

```text
flesh_baseline_output.json
- 상태: deployed prep
- 생성 조건: rulebook_only prep
- 공개 가능: 가능
- 비고: prep banner 필수

demo_flesh_baseline/index.html
- 상태: deployed prep
- 생성 조건: rulebook_only prep
- 공개 가능: 가능
- 비고: 실제 annotation 기반 아님

episode_intensity.json
- 상태: not deployed
- 생성 조건: Phase 3.0 annotation data 생성 후
- 공개 가능: 실제 데이터면 가능, raw text 제외

demo_episode_intensity/index.html
- 상태: not deployed
- 생성 조건: Phase 3.0 data 후
- 공개 가능: 가능, fixture면 비추천

data/annotation/phase3_pilot/
- 상태: not generated
- 생성 조건: 사용자 승인 5+2건 후 Mode A 운영
- 공개 가능: raw 제외
```

## Acceptance

```text
[ ] Operating Guide에 deploy status table 존재
[ ] deployed prep / fixture-only / generated-after-approval 구분
[ ] 사용자와 agent가 요청 가능한 파일 범위를 알 수 있음
```

---

## 4. 다음 Phase 이름

권장 이름:

```text
Phase 3.05 — Prep Integrity & Validator Hardening
```

이 단계는 Phase 3.0 실제 운영 전 안전장치다.

---

## 5. 구현 계획

---

## Step 1 — Flesh Baseline score_breakdown 보강

수정 후보:

```text
engine/observer/flesh_baseline.py
scripts/narrative/run_flesh_baseline.py
```

작업:

```text
1. rulebook_only mode에서 score_breakdown 생성
2. axis_match / pressure_overlap / compatibility_score 추가
3. annotation_score는 null
4. final_score는 현재 score와 동일
5. mode: rulebook_only 명시
```

예상 output:

```json
"score_breakdown": {
  "axis_match": 0.5,
  "pressure_overlap": 0.5,
  "compatibility_score": 1.0,
  "annotation_score": null,
  "final_score": 1.0,
  "mode": "rulebook_only"
}
```

Tests:

```text
[ ] test_flesh_baseline_rulebook_only_has_score_breakdown
[ ] test_flesh_baseline_rulebook_only_annotation_score_is_null
[ ] test_score_breakdown_not_empty_for_all_recommendations
```

---

## Step 2 — Flesh Baseline demo 문구 수정

수정 후보:

```text
scripts/narrative/build_flesh_baseline_demo.py
docs/portfolio/demo_flesh_baseline/index.html
docs/portfolio/demo_flesh_baseline/baseline.md
```

작업:

```text
1. Prep banner 강화
2. score label을 compatibility 중심으로 수정
3. strong_fit 단독 노출 방지
4. score_breakdown 표시
5. annotation_score 없음 표시
```

권장 문구:

```text
Prep mode — 현재 점수는 실제 annotation 기반 추천이 아니라 rulebook compatibility입니다.
Phase 3.0 pilot 데이터가 들어오면 annotation component가 추가됩니다.
```

HTML 표시:

```text
Compatibility score: 1.000
Annotation score: not available yet
Label: strong_fit (rulebook-only)
```

Tests:

```text
[ ] test_flesh_baseline_demo_mentions_rulebook_only
[ ] test_flesh_baseline_demo_does_not_claim_trained_model
[ ] test_flesh_baseline_demo_displays_score_breakdown
```

---

## Step 3 — Validator strict safety 보강

수정 후보:

```text
scripts/annotation/validate_annotation_outputs.py
```

작업:

```text
1. --strict + --synopsis 없음 → exit 2
2. error message 명확화
3. strict mode에서 quote validation source 필요
```

Tests:

```text
[ ] test_validate_annotation_strict_requires_synopsis
[ ] test_validate_annotation_non_strict_can_run_without_synopsis
```

---

## Step 4 — Hallucination report 분리

수정 후보:

```text
scripts/annotation/validate_annotation_outputs.py
```

작업:

```text
1. all_files_summary 생성
2. valid_files_only_summary 생성
3. invalid_files 목록 생성
4. threshold 판정은 valid_files_only 기준
5. feature coverage도 valid files 기준으로 계산
```

Output 예:

```json
{
  "all_files_summary": {
    "n_files": 20,
    "hallucination_rate": 0.02
  },
  "valid_files_only_summary": {
    "n_files": 19,
    "hallucination_rate": 0.0,
    "phase3_threshold_pass": true
  },
  "invalid_files": [
    {
      "path": "bad_output.json",
      "errors": ["missing field: features"]
    }
  ]
}
```

Tests:

```text
[ ] test_hallucination_report_has_valid_files_only_summary
[ ] test_invalid_files_do_not_pollute_valid_summary
[ ] test_strict_fails_when_invalid_files_exist
```

---

## Step 5 — Operating Guide deploy status table 추가

수정 후보:

```text
docs/plans/PHASE_3_0_PIPELINE_OPERATING_GUIDE.md
```

작업:

```text
1. 산출물 deploy status table 추가
2. deployed prep / not deployed / generated after approval 구분
3. fixture demo 정책 명시
4. 앞으로 파일 요청 시 이 표를 기준으로 삼도록 명시
```

추가 섹션 제목:

```text
## Deploy Status Matrix
```

Tests:

```text
[ ] test_operating_guide_has_deploy_status_matrix
[ ] test_operating_guide_marks_episode_intensity_not_deployed
[ ] test_operating_guide_marks_flesh_baseline_as_deployed_prep
```

---

## Step 6 — Docs sync

수정 후보:

```text
README.md
CLAUDE.md
DESIGN.md
INDEX.md
PROJECT_STRUCTURE.md
lessons.md
memory/project_witness_*.md
```

반영 내용:

```text
- rulebook_only prep score 의미
- episode_intensity script는 implemented, output은 not deployed
- deploy status matrix
- validator strict safety
```

---

## 6. Acceptance Criteria

```text
[ ] flesh_baseline_output.json의 모든 recommendation에 score_breakdown 존재
[ ] score_breakdown에 compatibility_score / annotation_score / mode 존재
[ ] rulebook_only일 때 annotation_score == null
[ ] demo_flesh_baseline이 실제 annotation 기반 추천처럼 보이지 않음
[ ] strong_fit 단독 노출 없음 또는 rulebook-only 병기
[ ] validate_annotation_outputs.py strict 모드에서 --synopsis 없으면 exit 2
[ ] hallucination report가 all_files_summary / valid_files_only_summary를 구분
[ ] invalid files가 threshold 계산을 오염시키지 않음
[ ] Operating Guide에 deploy status matrix 존재
[ ] episode_intensity fixture demo는 deploy하지 않음
[ ] 실제 fetch / LLM API / ML 학습 0건
[ ] fast suite 회귀 0
```

---

## 7. No-Go Criteria

아래 중 하나라도 있으면 이번 fix 실패다.

```text
- rulebook_only prep score가 실제 data-backed recommendation처럼 보임
- score_breakdown이 여전히 빈 dict
- demo에서 model trained처럼 보임
- strict validator가 synopsis 없이 hallucination check를 통과시킴
- invalid annotation이 hallucination pass 통계에 섞임
- episode_intensity fixture demo를 main portfolio에 deploy
- 외부 fetch 발생
- LLM API 호출 발생
- ML 학습 발생
```

---

## 8. 다음 에이전트 Directive

```text
WITNESS Phase 3.05 — Prep Integrity & Validator Hardening directive

Cycle 7–12 산출물 검수 결과, Phase 3.0/3.1 prep은 정상으로 본다.
다만 prep 결과물이 실제 데이터 기반 추천처럼 보이지 않도록 정직성 보강을 수행한다.

제약:
- 실제 fetch 금지
- LLM API 호출 금지
- ML 학습 금지
- episode_intensity fixture demo deploy 금지
- 새 baseline 추가 금지
- raw synopsis public 저장 금지

작업:
1. flesh_baseline_output.json의 score_breakdown을 채운다.
   - compatibility_score
   - axis_match
   - pressure_overlap
   - annotation_score: null
   - final_score
   - mode: rulebook_only

2. demo_flesh_baseline/index.html과 baseline.md 문구를 수정한다.
   - 1.000 strong_fit이 실제 annotation 기반 추천이 아니라 rulebook compatibility임을 명시한다.
   - Prep mode banner를 강화한다.
   - label은 strong_fit 단독이 아니라 strong_fit (rulebook-only) 또는 compatibility match로 표시한다.

3. validate_annotation_outputs.py strict safety를 보강한다.
   - --strict에서 --synopsis 없으면 exit 2.
   - hallucination summary를 valid_files_only 기준으로 산출한다.
   - invalid files는 별도 fail로 분리한다.

4. PHASE_3_0_PIPELINE_OPERATING_GUIDE.md에 deploy status matrix를 추가한다.
   - deployed prep
   - not deployed until user approval
   - fixture-only
   - generated after Phase 3.0

5. 관련 tests와 docs를 갱신한다.

Acceptance:
- score_breakdown 빈 dict 0건
- prep demo가 실제 데이터 기반 추천처럼 보이지 않음
- strict validator에서 synopsis 누락 방지
- invalid files가 hallucination pass 통계를 오염시키지 않음
- deploy 상태가 문서에 명확
- fast suite 회귀 0
```

---

## 9. Phase 3.05 이후 진행 순서

Phase 3.05가 끝나면 다음 순서로 간다.

```text
1. 사용자 승인 5+2건 재확인
2. Mode A 또는 Approved Fetch Mode 선택
3. 10 episode synopsis 준비
4. annotation_inputs 생성
5. 수동 LLM annotation 또는 API annotation 선택
6. validate_annotation_outputs.py strict mode 실행
7. feature_matrix 생성
8. reliability report 생성
9. Phase 3.0 Go / No-Go
10. Phase 3.1 real data baseline 생성
```

---

## 10. 파일 요청 원칙

앞으로 파일 요청 시 반드시 먼저 상태를 구분한다.

```text
1. deployed artifact
2. prep artifact
3. fixture-only artifact
4. script exists but output not deployed
5. generated after user approval
```

요청 우선순위:

```text
- deployed artifact 먼저 요청
- script-only output은 존재 여부 확인 후 요청
- generated-after-approval 파일은 승인 전 요청하지 않음
- fixture-only demo는 포트폴리오 산출물처럼 요구하지 않음
```

---

## 11. 한 줄 결론

현재 Phase 3.0/3.1 prep은 정상이다.  
다음은 기능 추가가 아니라, **prep 산출물이 실제 데이터 기반 결과처럼 보이지 않도록 정직성·검증성을 강화하는 단계**다.

> 다음 단계는 Phase 3.05 Prep Integrity & Validator Hardening이다.

---

*End of plan.*
