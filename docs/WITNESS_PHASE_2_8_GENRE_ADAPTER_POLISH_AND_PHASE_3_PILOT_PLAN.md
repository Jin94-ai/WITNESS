# WITNESS Next Plan — Genre Adapter Polish + Phase 3.0 Data/Annotation Pilot

> 기준일: 2026-05-10  
> 목적: Phase 2.75 Genre Adapter MVP 산출물을 검수한 결과를 바탕으로,  
> **장르 어댑터 결과물의 표현 품질을 개선**하고, 이후 **Phase 3.0 Data/Annotation Pilot**으로 안전하게 진입한다.

---

## 0. 현재 판단

Phase 2.75는 성공으로 본다.

현재 WITNESS는 다음 흐름을 실제 코드와 산출물로 보여준다.

```text
SkeletonOutput v1.1
→ Genre Rulebook
→ Genre Adapter
→ GenreAdaptedOutput v1
→ Cross-genre Portfolio Demo
→ Evidence / Audit
```

특히 좋은 점은 다음이다.

```text
1. 같은 universal skeleton을 두 장르로 변환했다.
2. 한국 아침 막장 드라마와 일본 정적 드라마가 서로 다른 톤으로 나온다.
3. source_seed_id / conflict_axis / pressures / desires가 보존된다.
4. transformation_level == structure_only가 유지된다.
5. forbidden event / dialogue / source imitation audit가 있다.
6. 외부 LLM / 데이터 fetch / 학습 없이 작동한다.
7. rulebook JSON만 바꿔 장르를 추가할 수 있음을 보였다.
```

따라서 구조 증명은 성공했다.

다만 아직 포트폴리오 메인 결과물로 쓰기에는 표현 품질에서 몇 가지 수정이 필요하다.

---

## 1. 파일 검수 요약

검토 대상:

```text
docs/portfolio/demo_genre_comparison/index.html
docs/plans/GENRE_ADAPTER_MVP_AUDIT.md
docs/portfolio/GENRE_ADAPTER_DEMO.md
data/narrative/genre_adapted_output.json
content/genres/korean_morning_melodrama/rulebook.json
content/genres/japanese_quiet_drama/rulebook.json
engine/observer/genre_adapter.py
engine/observer/genre_audit.py
```

확인된 상태:

```text
- demo_genre_comparison/index.html은 self-contained HTML 구조.
- 두 장르 side-by-side 비교가 가능.
- skeleton summary가 먼저 나오고, 장르 column이 이어짐.
- GenreAdaptedOutput은 source_seed_id, source_conflict_axis_id, source_pressures, source_desires를 보존.
- Audit 문서는 Phase 2.75 acceptance 11개 통과와 No-Go 0건을 기록.
- 한국 막장 rulebook과 일본 정적 드라마 rulebook은 의도적으로 반대 톤으로 설계됨.
- genre_adapter.py는 rulebook 기반 mapping, flow interleave, cliffhanger priority를 사용.
- genre_audit.py는 forbidden event, dialogue, source imitation, evidence preservation을 검사.
```

---

## 2. 종합 평가

```text
구조 완성도: 8.5 / 10
Audit 안정성: 8 / 10
Rulebook abstraction: 8 / 10
Cross-genre 설득력: 7.5 / 10
표면 문장 품질: 6 / 10
Portfolio 첫인상: 7 / 10
Phase 3 준비도: 7.5 / 10
```

한 줄 평가:

> Phase 2.75는 “뼈대-살 분리 작동 증명”에는 성공했다.  
> 그러나 포트폴리오 메인으로 쓰기 전, 장르 변환 문장의 반복성과 기계적 표현을 다듬어야 한다.

---

## 3. 주요 개선 필요점

---

# Issue 1 — 회차 흐름 문장이 기계적으로 반복됨

## 문제

현재 `adapted_outline_ko`는 episode rhythm과 adapted seed를 라운드로빈으로 결합한다.

예:

```text
1. 평온한 표면 — 버티는 사람이(가) 이 인물의 침묵이 다음 회차의 오해를 만든다.
2. 작은 균열 — 알아차리지만 말하지 않는 사람이(가) 지켜보는 시선이 미세한 변화를 알아차린다.
3. 의심의 확산 — 망설이는 사람이(가) 망설이는 시간이 길어질수록 주변의 의심이 자란다.
4. 침묵 또는 회피 — 뒤늦게 반응하는 사람이(가) 뒤늦은 반응이 이미 커진 오해와 부딪힌다.
5. 관계 충돌 — 버티는 사람이(가) 이 인물의 침묵이 다음 회차의 오해를 만든다.
6. 마지막 질문 — 알아차리지만 말하지 않는 사람이(가) 지켜보는 시선이 미세한 변화를 알아차린다.
```

문제점:

```text
- “사람이(가)” 조사가 어색하다.
- 1번과 5번, 2번과 6번이 사실상 반복된다.
- episode rhythm의 의미와 seed function이 자연스럽게 결합되지 않는다.
- 회차 흐름이라기보다 mapping 결과 나열처럼 보인다.
```

## 수정 방향

`_interleave_outline()`을 단순 라운드로빈에서 rulebook 기반 `outline_templates`로 바꾼다.

### rulebook에 추가

```json
"outline_templates": {
  "main_arc": {
    "early": "{role}은 아직 자리를 지키지만, {pressure}은 이미 주변을 누르고 있다.",
    "middle": "{role}의 침묵은 갈등을 줄이지 못하고 오해의 여지를 남긴다.",
    "late": "{role}은 끝내 말하지 못한 채 다음 질문을 남긴다."
  },
  "witness_arc": {
    "early": "{role}은 변화를 알아차리지만 아직 말하지 않는다.",
    "middle": "{role}의 시선은 중심 인물의 침묵을 더 선명하게 만든다.",
    "late": "{role}은 알고도 말하지 않는 위치에 남는다."
  },
  "supporting_uncertainty": {
    "middle": "{role}의 망설임은 주변의 의심을 키운다."
  },
  "delayed_response_arc": {
    "late": "{role}의 반응은 너무 늦게 도착한다."
  }
}
```

### 기대 출력

```text
1. 평온한 표면
   버티는 사람은 아직 자리를 지키지만, 가족/권위자의 시선은 이미 주변을 누르고 있다.

2. 작은 균열
   알아차리지만 말하지 않는 사람은 변화를 눈치채지만 아직 말하지 않는다.

3. 의심의 확산
   망설이는 사람의 유예가 길어질수록 주변의 의심은 커진다.

4. 침묵 또는 회피
   버티는 사람의 침묵은 갈등을 줄이지 못하고 오해의 여지를 남긴다.

5. 관계 충돌
   뒤늦게 반응하는 사람의 반응은 이미 커진 오해와 부딪힌다.

6. 마지막 질문
   누군가 그 침묵을 배신으로 해석하기 시작한다.
```

## Acceptance

```text
[ ] adapted_outline_ko에 “사람이(가)” 표현이 없어야 한다.
[ ] 같은 seed function이 2회 이상 반복되지 않아야 한다.
[ ] 각 episode rhythm 단계가 독립적인 문장으로 읽혀야 한다.
[ ] outline이 mapping table이 아니라 회차 흐름처럼 읽혀야 한다.
```

---

# Issue 2 — Skeleton Summary가 내부 용어 중심

## 문제

현재 HTML 상단 skeleton summary는 다음 내부 ID를 그대로 보여준다.

```text
loyalty_vs_survival
authority_vigilance
uncertainty_vs_commitment
loyal_under_pressure
```

이건 개발자에게는 좋지만, 포트폴리오 첫 화면에서는 장벽이다.

## 수정 방향

표에는 내부 ID와 함께 plain Korean label을 병기하거나, 기본 표시는 한국어로 바꾼다.

예:

```text
loyalty_vs_survival → 충성 vs 생존
authority_vigilance → 권위자의 압박
uncertainty_vs_commitment → 불확실함 vs 결단
loyal_under_pressure → 압력 속에서도 남으려는 사람
```

## 구현

taxonomy loader를 활용해 HTML render 단계에서 plain label을 사용한다.

표기 방식:

```text
충성 vs 생존
<small>loyalty_vs_survival</small>
```

## Acceptance

```text
[ ] demo_genre_comparison 첫 화면에서 내부 ID만 단독으로 보이지 않는다.
[ ] 일반인용 label이 먼저 보인다.
[ ] technical appendix에는 내부 ID를 유지한다.
```

---

# Issue 3 — 장르 차이는 보이지만, “왜 다르게 나왔는지” 설명이 부족함

## 문제

두 장르 column은 다른 결과를 보여주지만, 사용자가 바로 이해할 설명이 부족하다.

현재 사용자는 이렇게 볼 수 있다.

```text
한국 장르: 침묵 → 오해
일본 장르: 침묵 → 정적
```

하지만 왜 그렇게 갈라졌는지 rulebook 근거가 메인에서 충분히 보이지 않는다.

## 수정 방향

각 column 상단에 `Genre Lens` 섹션을 추가한다.

### 한국 막장 드라마

```text
장르 렌즈:
침묵은 갈등을 줄이지 않는다.
오히려 주변의 의심과 오해를 키운다.
```

### 일본 정적 드라마

```text
장르 렌즈:
침묵은 폭발하지 않는다.
정적으로 남아 인물 사이의 거리를 조금씩 바꾼다.
```

## Acceptance

```text
[ ] 각 genre column 상단에 Genre Lens가 있다.
[ ] 사용자가 장르 차이를 5초 안에 이해할 수 있다.
[ ] Lens 문장은 rulebook description 또는 conflict amplifier에서 생성된다.
```

---

# Issue 4 — `genre_adapted_output.json`은 한국 장르 단일 파일

## 문제

현재 `genre_adapted_output.json`은 `korean_morning_melodrama` 단일 출력이다.

하지만 메인 포트폴리오 후보는 cross-genre comparison이다.

## 수정 방향

비교용 machine-readable output을 별도 생성한다.

```text
data/narrative/genre_comparison_output.json
docs/portfolio/demo_genre_comparison/genre_comparison_output.json
```

구조:

```json
{
  "schema_version": "genre_comparison_output_v1",
  "source_skeleton_version": "skeleton_output_v1",
  "source_seed_ids": ["S01", "S02", "S03", "S04"],
  "genres": {
    "korean_morning_melodrama": {},
    "japanese_quiet_drama": {}
  },
  "comparison_summary": {
    "shared_conflict_axes": ["loyalty_vs_survival", "uncertainty_vs_commitment"],
    "difference": [
      {
        "source_seed_id": "S01",
        "korean": "침묵이 오해를 만든다",
        "japanese": "침묵이 정적으로 이어진다"
      }
    ],
    "audit_overall": "pass"
  }
}
```

## Acceptance

```text
[ ] comparison output JSON이 생성된다.
[ ] HTML이 comparison output에서 렌더링 가능하다.
[ ] 두 장르 audit 결과가 모두 포함된다.
```

---

# Issue 5 — Audit는 좋지만 “표현 품질”은 검증하지 않음

## 문제

현재 audit는 주로 안전성/보존성 중심이다.

```text
forbidden event
dialogue
source imitation
evidence preservation
```

하지만 아래는 잡지 못한다.

```text
- 어색한 조사
- 반복 문장
- mapping 결과처럼 보이는 문장
- 장르 column 간 차이가 약한 경우
```

## 수정 방향

`genre_quality_audit.py` 또는 기존 `genre_audit.py`에 soft quality checks를 추가한다.

Soft audit 항목:

```text
- awkward_josa_patterns: ["이(가)", "을(를)", "은(는)"]
- repeated_outline_function_count
- duplicate_outline_lines
- empty_genre_lens
- all_genres_same_premise
```

결과:

```json
"quality_warnings": [
  "outline contains awkward josa pattern: 사람이(가)",
  "same adapted_function repeated in outline twice"
]
```

주의:

```text
quality warning은 fail이 아니라 warning.
단, portfolio polish gate에서는 warning 0을 목표로 한다.
```

## Acceptance

```text
[ ] quality_warnings 필드가 audit에 포함된다.
[ ] 사람이(가) 같은 placeholder 조사 표현을 잡는다.
[ ] adapted_outline 반복을 잡는다.
[ ] hard audit pass와 soft warning을 분리한다.
```

---

# Issue 6 — 장르 어댑터가 아직 “회차 흐름”보다 “역할 함수 나열”에 가까움

## 문제

현재 flow builder는 다음 방식이다.

```text
episode_rhythm × adapted_seed function
```

이건 MVP로는 좋지만, 진짜 회차 개요로 보이려면 rhythm 단계마다 기능이 달라져야 한다.

## 수정 방향

`adapted_outline_ko`를 2층으로 나눈다.

```text
1. rhythm_step
2. narrative_line
```

JSON 구조:

```json
"adapted_outline": [
  {
    "step": "평온한 표면",
    "source_seed_id": "S01",
    "source_flow_role": "main_arc",
    "line_ko": "버티는 사람은 아직 자리를 지키지만, 가족/권위자의 시선은 이미 주변을 누르고 있다."
  }
]
```

HTML은 `line_ko`를 보여주고, technical appendix에서 source_seed_id를 보여준다.

## Acceptance

```text
[ ] adapted_outline_ko list[str]를 유지하되, v1.1에서 structured outline도 추가한다.
[ ] HTML은 structured outline을 우선 사용한다.
[ ] 각 line이 source_seed_id를 보존한다.
```

---

## 4. 다음 작업 Phase 정의

## Phase 2.8 — Genre Adapter Polish

목표:

```text
Phase 2.75에서 작동을 증명한 Genre Adapter를
포트폴리오 메인으로 보여줄 수 있을 만큼 polish한다.
```

범위:

```text
- output 문장 품질 개선
- cross-genre comparison output 명시화
- genre lens 추가
- quality audit 추가
- HTML 정보 위계 개선
```

하지 않을 것:

```text
- 실제 데이터 fetch
- LLM API 호출
- ML 학습
- 새 장르 3개 이상 추가
- 소설 본문 생성
- 대사 생성
```

---

## 5. Phase 2.8 구현 계획

### Step 1 — Rulebook outline templates 추가

수정 파일:

```text
content/genres/korean_morning_melodrama/rulebook.json
content/genres/japanese_quiet_drama/rulebook.json
```

추가 필드:

```text
genre_lens_ko
outline_templates
outline_step_mapping
```

예:

```json
"genre_lens_ko": "침묵은 갈등을 줄이지 않는다. 오히려 주변의 의심과 오해를 키운다."
```

---

### Step 2 — Genre Adapter flow builder 개선

수정 파일:

```text
engine/observer/genre_adapter.py
```

변경:

```text
_interleave_outline()
→ build_structured_outline()
```

출력:

```python
@dataclass(frozen=True)
class GenreAdaptedOutlineStep:
    step: str
    source_seed_id: str
    source_flow_role: str
    line_ko: str
```

`GenreAdaptedFlow`에 추가:

```python
adapted_outline_steps: tuple[GenreAdaptedOutlineStep, ...]
```

기존 `adapted_outline_ko`는 backward compatibility로 유지.

---

### Step 3 — Quality Audit 추가

수정 파일:

```text
engine/observer/genre_audit.py
```

추가:

```python
quality_warnings: tuple[str, ...]
```

체크:

```text
- "이(가)" / "을(를)" / "은(는)" placeholder pattern
- duplicate outline lines
- repeated adapted_function in outline
- empty genre lens
- identical premise across genres
```

---

### Step 4 — Cross-genre comparison output 생성

신규 또는 수정:

```text
engine/observer/genre_comparison.py
scripts/narrative/run_genre_comparison_demo.py
```

출력:

```text
data/narrative/genre_comparison_output.json
docs/portfolio/demo_genre_comparison/genre_comparison_output.json
```

---

### Step 5 — HTML 정보 위계 개선

수정:

```text
docs/portfolio/demo_genre_comparison/index.html generator
```

새 구조:

```text
1. Hero
2. One Skeleton, Two Genre Lenses
3. Universal Skeleton Summary
4. Side-by-side Genre Results
5. Why They Differ
6. Evidence Preservation
7. Audit & Technical Appendix
```

Hero 문구:

```text
같은 이야기 뼈대가 장르 문법에 따라 다르게 살아나는 과정을 보여줍니다.
```

---

### Step 6 — Audit 문서 갱신

수정/신규:

```text
docs/plans/GENRE_ADAPTER_POLISH_AUDIT.md
docs/portfolio/GENRE_ADAPTER_DEMO.md
```

포함:

```text
- Phase 2.75 → 2.8 변경점
- hard audit 결과
- soft quality warning 결과
- cross-genre output summary
- remaining risks
```

---

## 6. Phase 2.8 Acceptance Criteria

```text
[ ] genre_lens_ko가 두 rulebook에 존재한다.
[ ] outline_templates가 두 rulebook에 존재한다.
[ ] adapted_outline_steps가 source_seed_id를 보존한다.
[ ] HTML에 “One Skeleton, Two Genre Lenses” 섹션이 있다.
[ ] 한국/일본 장르 차이가 5초 안에 이해된다.
[ ] “사람이(가)” 같은 placeholder 조사 표현이 없다.
[ ] outline line 중복이 없다.
[ ] quality_warnings가 audit 결과에 포함된다.
[ ] hard audit overall == pass.
[ ] soft quality warning == 0 또는 명시적으로 documented.
[ ] comparison output JSON이 생성된다.
[ ] fast suite 회귀 0.
```

---

## 7. Phase 2.8 No-Go Criteria

```text
- 장르 결과물이 원본 conflict_axis를 잃음
- source_seed_id 연결이 끊김
- forbidden event가 출력 본문에 등장
- 대사 생성
- 특정 작품명/실제 대사 모방
- hard audit fail
- side-by-side 결과가 거의 동일하게 보임
- HTML 첫 화면에서 무엇을 비교하는지 불명확
```

---

## 8. Phase 3.0 — Data & Annotation Pilot 준비

Phase 2.8이 끝나면 Phase 3 전체 학습으로 바로 가지 말고, 작은 pilot으로 진입한다.

### 8.1 목표

```text
실제 장르 줄거리 데이터를 소량 수집해
annotation guide와 prompt template의 신뢰도를 검증한다.
```

### 8.2 Pilot 범위

권장 최소:

```text
2 genres
각 2 titles
각 title 10 episodes
총 40 episode synopses
```

보수적 시작:

```text
1 genre
2 titles
각 10 episodes
총 20 episode synopses
```

### 8.3 필수 승인

Phase 3.0 시작 전 사용자 승인 필요:

```text
1. 실제 줄거리 데이터 fetch 승인
2. 출처별 ToS / robots.txt 검토 승인
3. LLM API 사용 승인
4. 비용 상한 승인
5. 저장 위치 / 공개 가능성 결정
```

---

## 9. Phase 3.0 데이터 수집 원칙

### 9.1 데이터 소스 원칙

우선순위:

```text
1. 공식 방송사 회차 소개
2. 공식 스트리밍 플랫폼 공개 synopsis
3. 위키/팬덤 요약은 보조적 참고만
4. 블로그/리뷰는 저작권/품질 문제로 비추천
```

### 9.2 수집 전 체크

각 source마다:

```text
- robots.txt 확인
- Terms of Service 확인
- rate limit
- 저작권 고지
- 공개 포트폴리오 노출 가능 여부
```

### 9.3 저장 정책

```text
data/raw_external/...
```

공개 repo에 올릴지 여부는 별도 결정.

권장:

```text
- 원문 synopsis는 비공개 또는 sample만 공개
- annotation feature vector / derived metrics는 공개 가능
- evidence_quote는 저작권 위험이 있으므로 짧게, 내부 audit용 우선
```

---

## 10. Phase 3.0 Annotation Pilot

### 10.1 Annotation 실행

각 회차에 대해:

```text
- LLM A
- LLM B
- LLM C
```

가능하면 3개 모델. 비용 때문에 2개부터 시작 가능.

### 10.2 검증

기존 도구 사용:

```text
validate_annotation_dict()
validate_evidence_quotes()
hallucination_rate()
inter_annotator_correlation()
reliability_grade()
```

### 10.3 성공 기준

```text
[ ] evidence quote hallucination rate < 5%
[ ] 최소 5개 feature에서 inter-annotator r ≥ 0.7
[ ] 나머지 feature는 marginal 이상 또는 guide 수정 대상
[ ] 사람 검증 샘플 5% 이상
[ ] data card 작성
```

### 10.4 실패 시

```text
- feature 정의 수정
- prompt template 수정
- low reliability feature 제거
- LLM 모델 조합 변경
- 데이터 소스 교체
```

---

## 11. Phase 3.1 ML/Flesh Engine은 아직 보류

Phase 3.0 Pilot이 통과하기 전까지는 ML 학습 금지.

이유:

```text
annotation reliability가 검증되지 않은 데이터로 학습하면
모델은 장르 문법이 아니라 annotation noise를 학습한다.
```

Phase 3.1 진입 조건:

```text
- pilot dataset 20~40 episodes 확보
- feature reliability report 작성
- 사용할 feature set 확정
- train/val split 결정
- baseline classifier / regressor target 결정
```

---

## 12. 다음 에이전트 Directive

```text
WITNESS Phase 2.8 — Genre Adapter Polish directive

목표:
Phase 2.75에서 작동을 증명한 rule-based Genre Adapter를 포트폴리오 메인으로 쓸 수 있도록 polish한다. 기능 확장이 아니라 출력 품질과 비교 명확성을 개선한다.

제약:
- engine simulation core 수정 금지
- external LLM API 호출 금지
- 실제 데이터 fetch 금지
- ML 학습 금지
- 대사 생성 금지
- 없는 사건 추가 금지
- 특정 작품/대사 모방 금지
- source_seed_id / conflict_axis / pressures / desires 보존

작업:
1. 두 genre rulebook에 genre_lens_ko, outline_templates, outline_step_mapping 추가
2. genre_adapter.py의 _interleave_outline을 structured outline builder로 교체
3. GenreAdaptedOutlineStep dataclass 추가
4. adapted_outline_steps를 GenreAdaptedFlow에 추가하고 기존 adapted_outline_ko는 호환용 유지
5. genre_audit.py에 quality_warnings 추가
6. 사람이(가), 을(를), 은(는) 같은 placeholder 조사 패턴 검사 추가
7. duplicate outline line / repeated function warning 추가
8. genre_comparison_output.json 생성
9. demo_genre_comparison/index.html 정보 위계 개선
10. GENRE_ADAPTER_POLISH_AUDIT.md 작성
11. tests 추가 및 fast suite 통과

Acceptance:
- side-by-side demo에서 장르 차이가 5초 안에 이해된다.
- outline 문장이 mapping 나열이 아니라 회차 흐름처럼 읽힌다.
- placeholder 조사 표현이 없다.
- source_seed_id / conflict_axis / pressures / desires 보존.
- hard audit pass.
- soft quality warning 0 또는 명시적 documented.
- fast suite 회귀 0.
```

---

## 13. 최종 진행 순서

```text
1. Phase 2.8 Genre Adapter Polish
2. demo_genre_comparison 최종 검수
3. Phase 3.0 Data & Annotation Pilot 승인 여부 결정
4. ToS / robots.txt 검토
5. 20~40 episode pilot dataset 구축
6. multi-AI annotation
7. reliability report
8. Phase 3.1 ML/Flesh Engine 여부 결정
```

---

## 14. 한 줄 결론

Phase 2.75는 성공했다.  
다만 지금 결과물은 “작동 증명”이고, 포트폴리오 메인으로 쓰려면 **표현 품질과 비교 명확성**을 한 번 더 다듬어야 한다.

> 다음은 ML이 아니라 Phase 2.8 Genre Adapter Polish다.  
> 그 다음에야 실제 데이터/LLM/API를 쓰는 Phase 3.0 Annotation Pilot로 넘어간다.

---

*End of plan.*
