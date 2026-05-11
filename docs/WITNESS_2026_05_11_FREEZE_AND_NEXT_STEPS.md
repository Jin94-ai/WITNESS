# WITNESS 2026-05-11 진행상황 점검 및 다음 단계 제안

## 1. 현재 상태 요약

현재 WITNESS 프로젝트는 **Phase 3.05 / Phase 3.1 frontier가 사실상 닫힌 상태**다.

```text
상태: Phase 3.05 / 3.1 frontier closed
품질: 안정적
테스트: 2,648 fast tests pass / 0 regression
주요 병목: 코드 구조가 아니라 실제 데이터 투입
위험 요소: 174 uncommitted changes
다음 유효 단계: Phase 3.0 Actual Mini Pilot
```

현재까지 완료된 영역은 다음과 같다.

- 4-Axis Discovery Candidate Classifier 구현
- Rubric engine / CLI / fixture / portfolio reports 구축
- Phase 3.1 Target A/B/C portfolio asset 확보
- doc-currency 대량 갱신
- doc-reality automation 구축
- Lessons L82-L88 정리 및 saturation curve 검증
- 5회 연속 saturation pause 발생

따라서 지금은 더 구현할 단계가 아니라, **커밋 / 동결 / 실데이터 투입 판단 단계**다.

---

## 2. 핵심 판단

현재 프로젝트의 병목은 더 이상 구조 개발이 아니다.

병목은 다음이다.

```text
실제 synopsis 10개가 아직 들어오지 않음
→ annotation 없음
→ feature_matrix 없음
→ reliability report 없음
→ actual pilot demo 없음
```

따라서 다음 실질 진전은 다음 흐름에서 나온다.

```text
실제 줄거리 10개 투입
→ manual annotation
→ strict validation
→ feature matrix
→ reliability report
→ flesh baseline
→ episode intensity
→ actual pilot demo
```

---

## 3. 지금 가장 큰 리스크

## 3.1 174 uncommitted changes

현재 174개의 uncommitted change가 있다는 점이 가장 위험하다.

이 상태에서 Phase 3.0 actual pilot을 시작하면 다음 문제가 생긴다.

```text
- 어떤 변화가 어떤 결과를 만든 것인지 추적하기 어려움
- regression 발생 시 rollback 범위가 커짐
- prep / fixture / actual 결과물이 섞일 수 있음
- portfolio asset과 docs의 상태가 혼재될 수 있음
- 실제 pilot 결과의 신뢰성이 낮아질 수 있음
```

따라서 다음 작업은 새 기능 구현이 아니라 **변경사항 분류와 freeze**여야 한다.

---

## 4. 권장 커밋 분할

174개 변경을 하나의 커밋으로 묶으면 나중에 리뷰와 복구가 어렵다.

권장 커밋 단위는 다음과 같다.

```text
commit 1: rubric engine + tests
commit 2: rubric CLI + fixtures + demo reports
commit 3: Phase 3.1 Target A/B/C assets
commit 4: doc-currency updates
commit 5: doc-reality automation
commit 6: lessons L82-L88 / meta docs
```

최소 4개, 가능하면 6개 커밋으로 나누는 것이 좋다.

---

## 5. Rubric 명명 주의

현재 Rubric은 **Discovery Evaluator**가 아니라 **Discovery Candidate Classifier**로 유지해야 한다.

사용해도 되는 표현:

```text
Discovery Candidate Classifier
candidate classifier
triage layer
audit rubric
non-training evaluator
```

피해야 할 표현:

```text
Discovery Evaluator
Discovery Validator
Discovery Judge
Meaning Discovery Score
final discovery proof
```

이유:

현재 rubric은 진짜 discovery를 증명하는 장치가 아니라, 생성된 trajectory가 discovery candidate로 볼 수 있는지 분류하는 감사 계층에 가깝다.

---

## 6. Portfolio / Demo 문구 리스크

Rubric ensemble HTML 결과는 수치가 좋아 보일 수 있다.

예:

```text
cross_scenario 19/20
multi_agent 14/15
multi_seed 4/5
```

하지만 이것이 fixture / synthetic 기반이라면 actual data 검증처럼 보이면 안 된다.

따라서 HTML 상단이나 README에 다음과 같은 문구가 필요하다.

```text
This is a rubric stress-test surface using controlled fixtures, not a claim of validated real-world discovery.
```

한국어 표현:

```text
이 데모는 통제 fixture 기반 rubric stress-test이며, 실제 데이터 기반 discovery 검증 결과가 아니다.
```

---

## 7. 지금 추가하면 좋은 최소 보완

새 기능 구현은 권장하지 않는다.

대신 다음 3개만 추가하면 좋다.

---

## 7.1 Commit Readiness Report

추천 파일:

```text
docs/reports/COMMIT_READINESS_2026_05_11.md
```

포함할 내용:

```text
- changed files summary
- test count
- major assets added
- known non-claims
- not-yet-done items
- recommended commit split
- files that should not be committed
```

목적:

Phase 3.0 actual pilot에 들어가기 전에 현재 repository 상태를 추적 가능한 형태로 남긴다.

---

## 7.2 Phase 3.0 Actual Pilot Boundary 문서

추천 파일:

```text
docs/plans/PHASE_3_0_ACTUAL_PILOT_BOUNDARY.md
```

포함할 내용:

```text
Allowed:
- 10 manually provided synopses
- private/gitignored raw text
- manual LLM annotation
- strict validation
- feature matrix
- reliability report

Forbidden:
- external fetch
- LLM API
- ML training
- public raw synopsis
- more than 10 episodes
- fixture result presented as actual
```

목적:

Phase 3.0 actual pilot의 범위와 금지사항을 명확히 해서 prep / fixture / actual 결과물이 섞이지 않게 한다.

---

## 7.3 Uncommitted Risk Note

174개 변경이 있는 상태에서는 단순 `git status`만으로 부족하다.

최소한 다음 항목을 정리해야 한다.

```text
- why this branch is safe to commit
- which files are generated
- which files are source
- which files are portfolio artifacts
- which files should not be committed
- whether private raw synopsis paths are gitignored
```

---

## 8. 다음 진행 우선순위

추천 우선순위는 다음이다.

```text
1순위: commit split + freeze
2순위: Phase 3.0 Actual Mini Pilot
3순위: calibration phase
```

Calibration은 아직 이르다.

이유:

```text
실측 trajectory가 없음
→ threshold 보정 근거 없음
→ 지금 calibration을 하면 가짜 정밀도가 됨
```

따라서 현재 기준 판단은 다음과 같다.

```text
Phase 5 calibration: 아직 아님
Phase 3.0 mini pilot: 지금 맞음
```

---

## 9. 다음 Claude Code Directive

아래 directive를 다음 작업에 바로 사용할 수 있다.

```md
# WITNESS Commit Freeze + Phase 3.0 Boundary Directive

Current state:
- Rubric / Phase 3.1 / doc-currency / doc-reality frontier appears closed.
- Fast tests: 2,648 pass, 0 regression.
- There are 174 uncommitted changes.
- Do not start new feature work yet.

Goal:
Prepare the repository for a safe freeze before Phase 3.0 Actual Mini Pilot.

Tasks:
1. Inspect git status and categorize all uncommitted changes into:
   - rubric engine/tests
   - rubric CLI/demo/fixtures
   - Phase 3.1 assets
   - docs/doc-currency
   - doc-reality automation
   - lessons/meta docs
   - generated artifacts
   - should-not-commit items

2. Create a commit readiness report:
   docs/reports/COMMIT_READINESS_2026_05_11.md

3. Create a Phase 3.0 Actual Pilot boundary document:
   docs/plans/PHASE_3_0_ACTUAL_PILOT_BOUNDARY.md

4. Verify:
   - no raw synopsis is committed
   - private/gitignored path exists or is documented
   - all portfolio demos clearly label prep/fixture/actual status
   - rubric outputs are labeled as candidate classification, not final discovery proof

5. Run fast tests once.

6. Output:
   - recommended commit split
   - files that should not be committed
   - remaining blockers before Phase 3.0 mini pilot

Constraints:
- Do not implement new rubric logic.
- Do not add new portfolio demos.
- Do not run external fetch.
- Do not call LLM API.
- Do not start ML training.
- Do not exceed repository cleanup scope.
```

---

## 10. 최종 판단

현재 개선보완점은 기능 추가가 아니라 **동결 품질 관리**다.

지금 바로 다음으로 가려면 순서는 다음이 맞다.

```text
1. 174 uncommitted changes 정리
2. commit readiness report 작성
3. Phase 3.0 boundary 문서 작성
4. freeze
5. 실제 synopsis 10개 투입
```

이 상태에서 새 기능을 더 만드는 것은 권장하지 않는다.

다음 실질 진전은 **실제 줄거리 10개를 넣어 Phase 3.0 Actual Mini Pilot을 실행하는 것**이다.

---

## 11. 한 줄 결론

WITNESS는 현재 구조 개발 구간을 넘어섰다.

이제 필요한 것은 추가 구현이 아니라:

```text
commit freeze
→ actual pilot boundary 고정
→ 실제 데이터 10개 투입
→ reliability / feature / demo 결과 확인
```

이다.
