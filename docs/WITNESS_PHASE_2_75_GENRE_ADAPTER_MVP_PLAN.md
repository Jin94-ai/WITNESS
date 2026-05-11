# WITNESS Next Plan — Rule-based Flesh / Genre Adapter MVP

> 목표: Phase 3 ML/Flesh Engine 학습으로 바로 넘어가기 전에,  
> 현재 완성된 `SkeletonOutput v1.1`이 실제 장르 변환에 쓸 수 있는지  
> **Rule-based Genre Adapter MVP**로 검증한다.

---

## 0. 현재 상태 판단

현재 WITNESS Narrative Mode Refactor는 다음 단계까지 완료되었다.

```text
Phase 0 — Skeleton Cleanup
Phase 1 — Data Infra
Phase 2 — Multi-AI Annotation Prep
Phase 2.5 — Validation Fix
Phase 6 partial — Portfolio skeleton integration
```

핵심 개선:

```text
UniversalStorySeed v1.1
SkeletonOutput contract
Anchor binding 분리
Phase 3 Go Gate
Validation fix report
Annotation guide v1.1
```

이전 결함이었던 아래 항목들은 해결되었다.

```text
main_archetype empty
main_role == "main"
supporting_1 / supporting_2 placeholder
dominant_pressures empty
flow == null
unknown axis ambiguity
drift guard weak typing
```

현재 `SkeletonOutput`은 다음 정보를 충분히 가진다.

```text
- seed_id
- conflict_axis_id
- main_archetype
- main_role
- dominant_pressures
- dominant_desires
- supporting_archetypes
- supporting_roles
- change_pattern
- arc_direction
- relationship_function
- flow_role
- turning_points_count
- evidence_count
- audit_status
- LifeStoryFlow ordering
```

따라서 다음 단계는 바로 ML 학습이 아니라:

> 이 뼈대가 실제 장르 변환에 쓸 수 있는지 작은 rule-based Flesh Engine으로 증명하는 것

이다.

---

## 1. 왜 바로 Phase 3 ML로 가지 않는가

Phase 3는 외부 의존성이 크다.

```text
- 실제 줄거리 데이터 fetch
- 출처별 ToS / robots.txt 검토
- LLM API 비용
- multi-AI annotation
- human review sampling
- model training
- GPU / storage / experiment tracking
```

반면 Rule-based Genre Adapter MVP는 외부 의존 없이 가능하다.

```text
SkeletonOutput v1.1
→ Genre Rulebook
→ Genre-adapted Treatment
→ Evidence / Audit
→ Portfolio Demo
```

이 단계에서 다음을 먼저 확인해야 한다.

```text
1. SkeletonOutput이 장르 변환에 충분한 정보를 담고 있는가
2. Universal seed가 특정 장르 문법으로 변환 가능한가
3. 변환 과정에서 원본 conflict / desire / pressure가 보존되는가
4. 장르 어댑터가 없는 사건을 추가하지 않는가
5. 포트폴리오에서 “활용 가능성”이 명확하게 보이는가
```

---

## 2. 이번 Phase 이름

```text
Phase 2.75 — Rule-based Genre Adapter MVP
```

또는:

```text
Phase 2.75 — Structure-only Genre Adaptation
```

권장 이름:

```text
Phase 2.75 — Rule-based Genre Adapter MVP
```

---

## 3. 목표 산출물

이번 단계의 최종 산출물은 아래다.

```text
content/genres/korean_morning_melodrama/rulebook.json
content/genres/korean_morning_melodrama/audit_blocklist.json

engine/observer/genre_rulebook.py
engine/observer/genre_adapter.py
engine/observer/genre_audit.py

scripts/narrative/apply_genre_adapter.py
scripts/narrative/run_genre_demo.py

data/narrative/genre_adapted_output.json
docs/portfolio/demo_genre/index.html
docs/portfolio/GENRE_ADAPTER_DEMO.md
docs/plans/GENRE_ADAPTER_MVP_AUDIT.md
```

---

## 4. 핵심 설계

### 4.1 입력

```text
docs/portfolio/demo/skeleton_output.json
```

필수 조건:

```text
- schema_version: skeleton_output_v1 또는 skeleton_output_v1_1
- seed schema: universal_story_seed_v1_1
- flow != null
- audit_trail.unknown_axis_count == 0
- audit_trail.forbidden_event_additions == 0
- audit_trail.forbidden_dialogue_generation == 0
```

### 4.2 출력

```json
{
  "schema_version": "genre_adapted_output_v1",
  "source_skeleton_schema": "skeleton_output_v1",
  "genre_id": "korean_morning_melodrama",
  "source_seed_ids": ["S01", "S03", "S02", "S04"],
  "original_universal_flow": {},
  "genre_adapted_flow": {},
  "adapted_treatments": [],
  "audit": {}
}
```

### 4.3 변환 원칙

장르 어댑터는 다음을 한다.

```text
- conflict를 장르 문법으로 해석한다.
- role을 장르 역할로 매핑한다.
- pressure를 장르적 압력 장치로 변환한다.
- flow를 장르 episode rhythm으로 재배열한다.
- unresolved question을 cliffhanger로 바꾼다.
```

장르 어댑터는 다음을 하지 않는다.

```text
- 원본에 없는 사건을 확정하지 않는다.
- 대사를 만들지 않는다.
- 인물 관계를 임의로 추가하지 않는다.
- 출생의 비밀, 불륜, 살인 같은 막장 요소를 자동 삽입하지 않는다.
- 특정 드라마 문장/장면/대사를 모방하지 않는다.
```

---

## 5. 첫 번째 장르: Korean Morning Melodrama

### 5.1 장르 정의

이번 MVP의 첫 장르는:

```text
korean_morning_melodrama
```

목표는 “막장 드라마 말투 흉내”가 아니다.

목표:

```text
한국 아침드라마/막장드라마에서 자주 보이는
갈등 증폭 구조, 역할 배치, 회차 리듬, 클리프행어 문법을
rulebook으로 모델링한다.
```

---

### 5.2 Rulebook 구조

파일:

```text
content/genres/korean_morning_melodrama/rulebook.json
```

예시:

```json
{
  "schema_version": "genre_rulebook_v1",
  "genre_id": "korean_morning_melodrama",
  "display_name_ko": "한국 아침 막장 드라마",
  "description_ko": "가족, 비밀, 오해, 침묵, 폭로, 관계 파탄을 중심으로 갈등을 증폭하는 장르 문법.",
  "conflict_amplifiers": [
    {
      "id": "silence_to_misunderstanding",
      "description_ko": "침묵이 오해를 키운다.",
      "applies_to": ["loyalty_vs_survival", "trust_vs_self_protection"]
    },
    {
      "id": "hidden_truth_pressure",
      "description_ko": "숨긴 진실이 관계를 흔든다.",
      "applies_to": ["control_vs_exposure", "identity_vs_failure"]
    },
    {
      "id": "family_gaze_pressure",
      "description_ko": "가족 또는 집단의 시선이 인물을 압박한다.",
      "applies_to": ["loyalty_vs_survival", "uncertainty_vs_commitment"]
    }
  ],
  "role_mappings": {
    "protagonist": ["버티는 사람", "숨기는 사람"],
    "supporting_actor": ["망설이는 사람"],
    "witness": ["알아차리지만 말하지 않는 사람"],
    "delayed_actor": ["뒤늦게 반응하는 사람"]
  },
  "pressure_mappings": {
    "fear": "말하지 못하게 만드는 두려움",
    "confusion": "결정을 미루게 만드는 혼란",
    "authority_vigilance": "가족/권위자의 시선",
    "public_suspicion": "주변 사람들의 의심",
    "group_tension": "집안 또는 조직 내부의 긴장",
    "crowd_tension": "집단 전체의 불안"
  },
  "episode_rhythm": [
    "평온한 표면",
    "작은 균열",
    "의심의 확산",
    "침묵 또는 회피",
    "관계 충돌",
    "마지막 질문"
  ],
  "cliffhanger_patterns": [
    {
      "id": "silence_read_as_betrayal",
      "description_ko": "누군가 침묵을 배신으로 해석하기 시작한다.",
      "requires": ["loyalty_vs_survival"]
    },
    {
      "id": "witness_notices_gap",
      "description_ko": "지켜보던 인물이 말하지 않은 사실을 알아차린다.",
      "requires_role": "witness"
    },
    {
      "id": "delayed_response_arrives_late",
      "description_ko": "뒤늦은 반응이 이미 커진 오해와 부딪힌다.",
      "requires_role": "delayed_actor"
    }
  ],
  "allowed_transformations": [
    "침묵을 오해 가능성으로 변환",
    "주변 시선을 가족/집단의 시선으로 변환",
    "미해결 질문을 클리프행어로 변환",
    "보조 seed를 장르적 보조 역할로 변환"
  ],
  "forbidden_transformations": [
    "출생의 비밀 임의 추가",
    "불륜 임의 추가",
    "살인 임의 추가",
    "폭로 확정",
    "대사 생성",
    "작품 특정 장면 모방"
  ]
}
```

---

### 5.3 Audit blocklist

파일:

```text
content/genres/korean_morning_melodrama/audit_blocklist.json
```

예시:

```json
{
  "schema_version": "genre_audit_blocklist_v1",
  "genre_id": "korean_morning_melodrama",
  "forbidden_event_tokens": [
    "출생의 비밀",
    "불륜",
    "살인",
    "납치",
    "유전자 검사",
    "친자 확인",
    "복수극을 시작한다"
  ],
  "forbidden_dialogue_markers": [
    "“",
    "”",
    "\\\"",
    "라고 말했다",
    "라고 외쳤다"
  ],
  "forbidden_source_imitation": [
    "특정 드라마 제목",
    "특정 등장인물명",
    "실제 방송 대사"
  ]
}
```

주의:

```text
막장 드라마 rulebook이라고 해서 “출생의 비밀” 같은 것을 자동으로 넣으면 안 된다.
이번 MVP는 structure-only adaptation이다.
```

---

## 6. 데이터 모델

### 6.1 GenreAdaptedSeed

```python
@dataclass(frozen=True)
class GenreAdaptedSeed:
    adaptation_id: str
    source_seed_id: str
    genre_id: str

    source_conflict_axis_id: str
    source_desires: tuple[str, ...]
    source_pressures: tuple[str, ...]

    genre_role: str
    genre_pressure: tuple[str, ...]
    genre_conflict_amplifier: str

    adapted_title_ko: str
    adapted_premise_ko: str
    adapted_function_ko: str
    cliffhanger_ko: str | None

    transformation_level: str  # "structure_only"
    evidence_preserved: bool
    forbidden_added: bool
```

### 6.2 GenreAdaptedFlow

```python
@dataclass(frozen=True)
class GenreAdaptedFlow:
    adaptation_id: str
    genre_id: str
    source_ordered_seed_ids: tuple[str, ...]

    title_ko: str
    premise_ko: str
    role_map: dict[str, str]
    episode_rhythm: tuple[str, ...]
    adapted_outline_ko: tuple[str, ...]
    cliffhanger_ko: str

    evidence_summary: dict
    audit_status: str
```

### 6.3 GenreAdaptedOutput

```python
@dataclass(frozen=True)
class GenreAdaptedOutput:
    schema_version: str
    genre_id: str
    source_skeleton_version: str
    adapted_seeds: tuple[GenreAdaptedSeed, ...]
    adapted_flow: GenreAdaptedFlow
    audit: GenreAuditResult
```

---

## 7. 변환 규칙

### 7.1 Seed 변환

입력:

```json
{
  "seed_id": "S01",
  "conflict_axis_id": "loyalty_vs_survival",
  "main_archetype": "loyal_under_pressure",
  "main_role": "protagonist",
  "dominant_pressures": ["authority_vigilance"],
  "dominant_desires": ["loyalty", "survival"],
  "change_pattern": "stay_present_then_withdraw",
  "arc_direction": "visibility_to_silence",
  "flow_role": "main_arc"
}
```

출력 예:

```text
원본 Universal Seed:
한 사람은 끝까지 남고 싶지만, 압력이 커질수록 침묵으로 밀려난다.

Genre Adapted:
가족 또는 집단의 시선 속에서 끝까지 남으려는 인물이,
말하지 못한 침묵 때문에 오해를 키운다.
```

### 7.2 Flow 변환

입력 flow:

```text
S01 main_arc
S03 witness_arc
S02 supporting_uncertainty
S04 delayed_response_arc
```

Genre flow:

```text
1. 평온한 표면 — 인물은 아직 곁에 남아 있다.
2. 작은 균열 — 지켜보는 사람이 변화를 알아차린다.
3. 의심의 확산 — 결정하지 못한 시간이 길어진다.
4. 침묵 또는 회피 — 중심 인물은 말하지 않는다.
5. 마지막 질문 — 뒤늦은 반응이 이미 커진 오해와 부딪힌다.
```

### 7.3 Cliffhanger 선택

우선순위:

```text
1. main seed가 loyalty_vs_survival이면 silence_read_as_betrayal
2. witness role이 있으면 witness_notices_gap
3. delayed_actor가 있으면 delayed_response_arrives_late
4. fallback: unresolved_question_to_next_episode
```

---

## 8. 구현 파일 계획

### 8.1 신규 코드

```text
engine/observer/genre_rulebook.py
engine/observer/genre_adapter.py
engine/observer/genre_audit.py
```

### 8.2 신규 스크립트

```text
scripts/narrative/apply_genre_adapter.py
scripts/narrative/run_genre_demo.py
```

### 8.3 신규 테스트

```text
tests/test_genre/test_genre_rulebook.py
tests/test_genre/test_genre_adapter.py
tests/test_genre/test_genre_audit.py
tests/test_genre/test_genre_demo.py
```

### 8.4 신규 문서

```text
docs/genres/KOREAN_MORNING_MELODRAMA_RULEBOOK.md
docs/portfolio/GENRE_ADAPTER_DEMO.md
docs/plans/GENRE_ADAPTER_MVP_AUDIT.md
```

### 8.5 신규 산출물

```text
data/narrative/genre_adapted_output.json
docs/portfolio/demo_genre/index.html
docs/portfolio/demo_genre/genre_adapted_output.md
docs/portfolio/demo_genre/evidence_audit.md
```

---

## 9. CLI 설계

### 9.1 apply_genre_adapter.py

```bash
python scripts/narrative/apply_genre_adapter.py \
  --input docs/portfolio/demo/skeleton_output.json \
  --genre korean_morning_melodrama \
  --output data/narrative/genre_adapted_output.json
```

### 9.2 run_genre_demo.py

```bash
python scripts/narrative/run_genre_demo.py \
  --skeleton docs/portfolio/demo/skeleton_output.json \
  --genre korean_morning_melodrama \
  --output docs/portfolio/demo_genre
```

생성:

```text
docs/portfolio/demo_genre/index.html
docs/portfolio/demo_genre/genre_adapted_output.md
docs/portfolio/demo_genre/evidence_audit.md
data/narrative/genre_adapted_output.json
```

---

## 10. Portfolio Demo 구성

파일:

```text
docs/portfolio/demo_genre/index.html
```

화면 구성:

```text
1. Hero
2. Original Skeleton
3. Genre Adapter
4. Original Seed vs Genre Adapted Result
5. Adapted Episode Flow
6. Evidence / Audit
7. Technical Appendix
```

### 10.1 Hero

```text
WITNESS · 장르 어댑터 데모

세계 시뮬레이션에서 나온 보편 이야기 뼈대를
한국 아침 막장 드라마의 구조 문법으로 변환합니다.
```

### 10.2 Original Skeleton

```text
원본 뼈대:
- 중심 갈등: 곁에 남기 vs 살아남기
- 중심 인물 유형: 압력 속에서도 곁에 남으려는 사람
- 압력: 권위자의 압박
- 흐름: 남아 있음 → 침묵 → 물러섬
```

### 10.3 Genre Adapted Result

```text
장르 변환 결과:

가족 또는 집단의 시선 속에서 끝까지 남으려는 인물이,
말하지 못한 침묵 때문에 오해를 키운다.

이야기 기능:
침묵이 갈등을 줄이는 것이 아니라,
오히려 다음 회차의 오해와 의심을 만든다.
```

### 10.4 Adapted Episode Flow

```text
1. 평온한 표면
   겉으로는 관계가 유지되는 것처럼 보인다.

2. 작은 균열
   지켜보는 사람이 침묵의 변화를 알아차린다.

3. 의심의 확산
   결정하지 못한 시간이 길어지고 주변의 시선이 무거워진다.

4. 침묵 또는 회피
   중심 인물은 떠나지 않지만 말하지도 않는다.

5. 마지막 질문
   뒤늦은 반응이 이미 커진 오해와 부딪힌다.
```

### 10.5 Evidence / Audit

접힘 영역:

```text
- source seed ids: S01, S03, S02, S04
- original conflict preserved: yes
- original desires preserved: yes
- original pressures preserved: yes
- transformation level: structure_only
- forbidden event added: no
- dialogue generated: no
```

---

## 11. Audit 규칙

### 11.1 Forbidden event audit

다음이 출력에 있으면 fail.

```text
출생의 비밀
불륜
살인
납치
친자 확인
유전자 검사
복수극 시작
```

단, rulebook의 forbidden list 안에 있는 경우는 출력물이 아니라 config이므로 제외.

### 11.2 Dialogue audit

다음이 있으면 fail.

```text
“...”
"..."
라고 말했다
라고 외쳤다
대사:
```

### 11.3 Evidence preservation audit

다음이 보존되어야 한다.

```text
source_seed_id
source_conflict_axis_id
source_desires
source_pressures
source_flow_role
```

### 11.4 Overreach audit

허용:

```text
침묵 → 오해 가능성
주변 시선 → 가족/집단의 시선
미해결 질문 → 클리프행어
```

금지:

```text
침묵 → 실제 배신 확정
시선 → 출생의 비밀 폭로
혼란 → 불륜 의심 확정
```

---

## 12. Acceptance Criteria

Phase 2.75가 끝나면 다음을 만족해야 한다.

```text
[ ] genre rulebook JSON이 존재한다.
[ ] audit blocklist JSON이 존재한다.
[ ] SkeletonOutput v1.1을 읽을 수 있다.
[ ] GenreAdaptedOutput JSON을 생성한다.
[ ] Original seed와 adapted seed가 source_seed_id로 연결된다.
[ ] conflict_axis / desires / pressures가 보존된다.
[ ] transformation_level == "structure_only"로 표시된다.
[ ] forbidden event 추가 0건.
[ ] dialogue 생성 0건.
[ ] demo_genre/index.html이 self-contained로 생성된다.
[ ] 기존 fast suite 회귀 0.
```

---

## 13. No-Go Criteria

아래 중 하나라도 발생하면 Phase 2.75 실패다.

```text
- adapted output이 원본 conflict_axis를 잃음
- adapted output이 source_seed_id를 잃음
- forbidden event가 출력 본문에 등장
- 대사 생성
- 특정 드라마/작품명/실제 대사 모방
- skeleton_output 없이 genre output 생성
- audit 결과를 숨김
```

---

## 14. 다음 단계와의 연결

Phase 2.75가 성공하면 두 갈래가 열린다.

### 14.1 Phase 3 ML/Flesh Engine

```text
Rule-based adapter의 feature와 출력 구조를 supervised target으로 사용 가능.
```

ML 입력:

```text
SkeletonOutput v1.1
+ annotation features
+ genre rulebook features
```

ML 출력 후보:

```text
mode classification
genre intensity score
adaptation recommendation
```

### 14.2 Product / Portfolio Demo

```text
Universal Skeleton
→ Genre Adapter
→ Genre Treatment
```

이 흐름이 포트폴리오에서 가장 설득력 있는 메인 구조가 될 수 있다.

---

## 15. 다음 에이전트 Directive

```text
WITNESS Phase 2.75 — Rule-based Genre Adapter MVP directive

목표:
Phase 3 ML/Flesh Engine 진입 전에, SkeletonOutput v1.1이 실제 장르 변환에 쓸 수 있는지 rule-based genre adapter로 검증한다.

제약:
- engine simulation core 수정 금지
- visual track 수정 금지
- 외부 LLM API 호출 금지
- 실제 데이터 fetch 금지
- 실제 방송 대본 학습 금지
- 특정 드라마 문장/장면/대사 모방 금지
- 대사 생성 금지
- 없는 사건 추가 금지
- 기존 Phase 3 Go Gate 유지

구현:
1. korean_morning_melodrama rulebook.json 작성
2. audit_blocklist.json 작성
3. genre_rulebook.py 구현
4. genre_adapter.py 구현
5. genre_audit.py 구현
6. apply_genre_adapter.py CLI 구현
7. run_genre_demo.py 구현
8. demo_genre/index.html 생성
9. tests 추가
10. GENRE_ADAPTER_MVP_AUDIT.md 작성

Acceptance:
- SkeletonOutput v1.1을 입력으로 받는다.
- adapted output이 source_seed_id / conflict_axis / desires / pressures를 보존한다.
- transformation_level은 structure_only다.
- forbidden event 추가 0.
- 대사 생성 0.
- demo_genre/index.html 하나로 Original Skeleton → Genre Adapted Result → Evidence/Audit 흐름이 보인다.
- fast suite 회귀 0.
```

---

## 16. 한 줄 결론

이제 뼈대는 충분히 단단하다.  
다음은 ML이 아니라, **그 뼈대가 실제 장르 변환에 쓸 수 있음을 rule-based Flesh MVP로 증명하는 단계**다.

---

*End of plan.*
