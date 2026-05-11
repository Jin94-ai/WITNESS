# WITNESS — pytest 운영 개선안

## 0. 문서 목적

이 문서는 현재 WITNESS 프로젝트에서  
**코드 변경 때마다 1500개 이상의 pytest가 반복 실행되는 문제**를 완화하기 위해 작성한다.

목표는 두 가지다.

1. **전체 테스트 안전망은 유지**
2. **작은 수정의 피드백 속도는 훨씬 빠르게**

즉, 방향은 “full pytest를 없애는 것”이 아니라  
**테스트를 계층화해서 언제 무엇을 돌릴지 분리하는 것**이다.

---

## 1. 현재 문제 정의

현재 상태의 문제는 pytest가 많다는 것 자체가 아니다.  
문제는 **모든 변경에 대해 너무 거친 단위로 검증이 걸리는 것**이다.

예를 들어:

- `render_story_ko.py` 문장 템플릿 수정
- `extract_story_features.py` 정규식 수정
- `build_narrative_ir.py` 임계값 조정
- `docs/story/` 문서 수정

같은 변경에도  
`tests/test_world/`, `tests/test_vangogh/`, `tests/test_talleyrand/`, `tests/test_person/`, `tests/test_rubric/`까지  
전체를 매번 다 돌리면 피드백 루프가 지나치게 느려진다.

즉 지금 구조는:

- 안전성은 높다
- 하지만 수정 속도와 실험 속도는 느리다
- 특히 story output 구현 단계에선 **과검증**일 수 있다

---

## 2. 기본 원칙

### 원칙 1
**Full suite는 유지한다.**
없애지 않는다.

### 원칙 2
**작은 수정에는 작은 테스트를 쓴다.**
관련 없는 도메인 전체를 매번 돌리지 않는다.

### 원칙 3
**테스트를 3층으로 나눈다.**
- Fast local
- Domain
- Full suite

### 원칙 4
**이번 story output 단계에 맞는 fast path를 새로 만든다.**
현재 WITNESS에는 story renderer 관련 빠른 테스트 레이어가 따로 필요하다.

---

## 3. 새로운 테스트 계층 구조

## Layer 1 — Fast Local Tests
### 목적
가장 빠른 피드백.
작은 수정 직후 바로 확인.

### 실행 시점
- 함수/스크립트 수정 직후
- 5~10분 단위 반복 작업 중
- template / regex / threshold 조정 직후

### 포함 대상
Story output 구현과 직접 관련된 테스트만 포함한다.

예:
- annotated probe 파싱 테스트
- story feature extraction 테스트
- Narrative IR mapping 테스트
- renderer smoke test
- josa / role plural helper 테스트
- representative probe golden output 비교

### 목표 시간
- **수초 ~ 30초 이내**

### 추천 명령 예시
```bash
pytest tests/test_story/ -q
```

---

## Layer 2 — Domain Tests
### 목적
관련 도메인 단위 검증.
현재 작업과 인접한 영역만 본다.

### 실행 시점
- 한 작업 블록이 끝났을 때
- renderer 1차 개선 후
- extraction / IR / rendering이 함께 바뀌었을 때
- 세션 중간 체크포인트

### 포함 대상
현재 변경과 직접 관련된 영역만 묶는다.

story 단계 예시:
- `tests/test_story/`
- `tests/test_engine/` 중 story extraction과 붙는 부분
- `tests/test_world_process/` 중 observable surface 관련
- 필요 시 `tests/test_rendering/` (추가 가능)

### 목표 시간
- **수십초 ~ 몇 분**

### 추천 명령 예시
```bash
pytest tests/test_story tests/test_world_process tests/test_engine -q
```

---

## Layer 3 — Full Suite
### 목적
프로젝트 전체 무결성 보장.
회귀 탐지.
legacy/비직접 영역 영향 확인.

### 실행 시점
- 세션 마감 전
- milestone 마감 전
- PR/merge 전
- engine touch 전후
- 큰 refactor 후
- canonical 결과물 생성 전

### 포함 대상
현재 전체 pytest suite

### 목표 시간
- 느려도 괜찮다
- 하지만 **항상 매 수정마다 돌릴 필요는 없다**

### 추천 명령 예시
```bash
pytest
```

---

## 4. Story Output 단계 전용 개선안

현재 WITNESS는 story output MVP 구현 단계에 들어갔다.  
따라서 **story 전용 테스트 레이어**를 먼저 세워야 한다.

## 4.1 새 테스트 디렉토리 제안
```text
tests/test_story/
├── test_extract_story_features.py
├── test_build_narrative_ir.py
├── test_render_story_ko.py
├── test_story_helpers.py
└── test_story_golden_outputs.py
```

---

## 4.2 각 테스트의 역할

### `test_extract_story_features.py`
검증 내용:
- annotated probe에서 required fields가 정확히 추출되는가
- final_summary / primary_pressure / counts / world metrics가 누락되지 않는가
- 정규식 변경이 기존 probe를 깨지 않는가

### `test_build_narrative_ir.py`
검증 내용:
- saturation probe가 saturation narrative key로 가는가
- recovery / mixed / partial 분류가 맞는가
- blame strong / suspicion strong / confession volume band가 맞는가
- threshold 조정이 의도한 분류를 만드는가

### `test_render_story_ko.py`
검증 내용:
- renderer가 예외 없이 문자열을 반환하는가
- 필수 문단이 빠지지 않는가
- world-side 문장이 특정 조건에서 포함되는가
- saturation / recovery ending 문장이 혼동되지 않는가

### `test_story_helpers.py`
검증 내용:
- 조사 자동 선택
- role plural 처리
- 중복 문장 제거 helper
- scenario-specific 문장 suppress rule

### `test_story_golden_outputs.py`
검증 내용:
- 대표 probe 2~4개에 대해 핵심 phrase가 유지되는가
- renderer 개선이 story 의미를 망치지 않는가
- 완전 일치가 아니라 “핵심 의미 키/문장 조각” 기준으로 검증

---

## 5. 추천 실행 규칙

## 규칙 A — 작은 수정 직후
다음만 돌린다:
```bash
pytest tests/test_story/ -q
```

사용 예:
- template 문장 수정
- 정규식 수정
- threshold band 수정
- helper 함수 수정

---

## 규칙 B — story 파이프라인이 여러 단계 바뀐 경우
다음을 돌린다:
```bash
pytest tests/test_story tests/test_world_process tests/test_engine -q
```

사용 예:
- extraction + IR + renderer 동시 변경
- observable surface가 story에 연결되는 구조 수정
- annotated field 추가/삭제

---

## 규칙 C — milestone / 세션 마감
전체를 돌린다:
```bash
pytest
```

사용 예:
- baseline 12개 전부 생성 완료 후
- renderer 1차 개선 완료 후
- Story MVP acceptance 문서 작성 전
- canonical 반영 전

---

## 6. 지금 당장 만들어야 할 것

현재 가장 필요한 건 아래 4개다.

### 6.1 `tests/test_story/` 신설
최우선.
story output 단계의 빠른 피드백을 위해 반드시 필요하다.

### 6.2 representative golden probes 선정
추천:
- saturation 대표 1개
- recovery 대표 1개
- mixed 대표 1개
- sacred / scarcity / accusation 중 최소 2종 포함

예:
- P9 (saturation/scarcity)
- P6 (mixed)
- P4 or P5 (sacred baseline)
- P10 or P11 (accusation)

### 6.3 pytest marker / 실행 alias 정리
가능하면 아래 별칭을 둔다.

- `pytest tests/test_story -q` → fast
- `pytest tests/test_story tests/test_world_process tests/test_engine -q` → domain
- `pytest` → full

필요하면 Makefile / script / README shortcut 추가.

### 6.4 Story 단계 운영 규칙 문서화
팀/Claude Code/미래 세션을 위해  
“언제 fast/domain/full을 돌리는가”를 문서에 남긴다.

---

## 7. Golden test 설계 원칙

중요: story output은 문장 하나 바뀌었다고 테스트를 깨면 안 된다.  
그래서 **완전 일치 비교**보다 **핵심 의미 단위 비교**가 맞다.

### 좋은 golden test
- final_summary에 맞는 ending 의미가 있는가
- pressure type이 opening에 반영되는가
- world-side 문장이 최소 1개는 나오는가
- saturation이면 stuck / residue 계열 표현이 있는가
- recovery면 easing / loosen / 풀림 계열 표현이 있는가

### 나쁜 golden test
- 전체 문장 완전 일치
- 띄어쓰기 하나 차이로 실패
- 문체 바뀌면 무조건 실패

즉 story 테스트는 **semantic golden**이 맞다.

---

## 8. Claude Code용 운영 지침

Claude Code는 story output 단계에서 다음 규칙을 따른다.

### 기본
- 작은 수정에는 full pytest 금지
- 먼저 `tests/test_story/`만 돌린다
- domain 영향이 있을 때만 domain tests
- milestone에서만 full suite

### 세부
1. `extract_story_features.py` 수정
   → `tests/test_story/test_extract_story_features.py`

2. `build_narrative_ir.py` 수정
   → `tests/test_story/test_build_narrative_ir.py`

3. `render_story_ko.py` 수정
   → `tests/test_story/test_render_story_ko.py`
   + 필요 시 golden test

4. baseline 12개 story 재생성 직전
   → story tests + domain tests

5. baseline review / MVP acceptance 직전
   → full pytest

---

## 9. 하지 말아야 할 것

- 작은 텍스트 수정마다 전체 1500개 실행
- story renderer를 수정하면서 unrelated suite까지 강제로 돌리기
- full suite를 없애기
- golden test를 완전 문자열 일치로 만들기
- marker만 만들고 실제 story 테스트를 안 만드는 것

지금 가장 중요한 건  
**full suite 제거가 아니라, fast local story test layer 신설**이다.

---

## 10. 단계별 적용 로드맵

### Phase 1
`tests/test_story/` 생성

### Phase 2
story helpers / extraction / IR / renderer smoke tests 작성

### Phase 3
representative golden tests 추가

### Phase 4
README 또는 docs에 fast/domain/full 실행 규칙 기록

### Phase 5
Story Output MVP 루프에서 실제로 사용

---

## 11. 최종 한 줄 요약

**1500개 pytest 전체는 계속 필요하지만,  
지금 story output 단계에서는 매 수정마다 전체를 돌리는 대신  
`tests/test_story/` 중심의 fast local layer를 새로 만들고,  
domain tests와 full suite를 단계별로 분리해서 운영하는 것이 맞다.**
