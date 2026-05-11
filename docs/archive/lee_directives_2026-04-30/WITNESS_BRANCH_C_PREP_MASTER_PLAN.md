# WITNESS — Branch C Prep 총정리 및 다음 진행 지시서

## 0. 문서 목적

이 문서는 현재 WITNESS 프로젝트의 상태를 종합해,  
**Branch C PREP 단계로 다음 진행을 할 수 있도록** 범위, 정의, 완료 기준, 보류 원칙, 즉시 실행 작업을 한 문서에 정리한 것이다.

이 문서의 목적은 다음 다섯 가지다.

1. 현재 branch 상태를 명확히 고정
2. Branch C의 첫 use case를 정의
3. “broader world”가 무엇인지 현재 프로젝트 문맥에서 정의
4. Branch C를 언제 “완료”라고 부를지 target-based criterion 제시
5. Claude Code와 Lee가 바로 다음 작업을 시작할 수 있게 실행 큐 제공

---

## 1. 현재 상태 요약

현재 WITNESS는 다음 상태에 있다.

- Branch A (readability-facing)는 사실상 검증되었다
- Full N=12 TRUE COMBINED 결과로 **P-C-ready** verdict가 나왔다
- 단, 현재 상태는 **Branch C PREP allowed, EXECUTION gated**
- 즉, broader world 방향으로 **설계/표현/관측 가능성 준비는 가능**
- 그러나 engine 변경, world refactor, broader world execution은 아직 금지

핵심 요약:

> **우리는 “사람이 읽을 수 있는 세계 출력”까지는 도달했고,  
> 이제부터는 “더 넓은 세계를 무엇으로 정의하고 어디까지를 이번 Branch C로 볼 것인가”를 먼저 고정해야 한다.**

---

## 2. Branch 상태 고정

### 2.1 현재 branch 판정
- **Branch A: confirmed**
- **Branch B: de-prioritized but debt cleanup 유지**
- **Branch C: PREP allowed**
- **Branch C execution: gated**

### 2.2 이 말의 의미
현재부터는:
- readability infra는 유지/개선 가능
- world-side observables 정의 가능
- Branch C 설계 문서화 가능
- annotated output acceptance 기준 정의 가능

하지만 아직:
- engine behavior 변경
- new world mechanics 추가
- broader world execution
- world/ legacy refactor
는 하지 않는다.

---

## 3. 첫 Branch C use case

## 결론
**첫 Branch C use case는 “4th scenario 추가”가 아니라,  
현재 3개 scenario(accusation / scarcity / sacred) 안에서 world-side observables와 population variation을 더 깊게 드러내는 수직 확장”으로 정의한다.**

### 왜 이렇게 가는가

현재 상태를 보면:
- readability는 이미 통과했다
- world-side readability도 crowd_mood / authority / public_attention이 일정 수준 surface되었다
- 하지만 kernel gap 문서상 여전히 placement template, authority autonomy, sole-channel recovery 같은 구조적 ceiling이 존재한다
- 이런 상황에서 4th scenario를 추가하면 “더 넓은 세계”가 아니라 “scenario 수만 늘어난 상태”가 될 위험이 있다

따라서 첫 Branch C use case는:
- 새로운 시나리오 개수를 늘리는 것보다
- 현재 시나리오에서 **더 많은 world-side 신호를 읽히게 만들고**
- **cast composition / location placement / authority observability**를 정교하게 다루는 것이 더 적절하다

### 첫 Branch C use case 정의
다음 중 하나 또는 둘의 결합으로 본다.

1. **현 scenario depth 확장**
   - accusation / scarcity / sacred 각각에서 world-side observables를 더 분명히 surface
   - authority / public attention / blame concentration / crowd mood가 더 선명히 읽히도록 설계

2. **population variation within current scenarios**
   - 동일 scenario에서 cast composition variation
   - location placement variation
   - cohort split 가시화
   - world memory trace 가시화

즉, Branch C의 첫 use case는 **“현재 세계를 더 세계답게 만드는 확장”**이다.

---

## 4. “broader world” 정의

## 결론
현재 WITNESS에서 **broader world**는 수평 확장보다 **수직 확장**으로 정의한다.

### 4.1 수평 확장 (이번 Branch C 기본 정의 아님)
- 4th scenario 추가
- 완전히 새로운 상황군 추가
- 세계 종류를 늘리는 방식

이 방식은 아직 시기상조다.  
이유는 현재 gap이 “시나리오 부족”보다 “현재 세계의 자율성과 관측 가능성 한계”에 가깝기 때문이다.

### 4.2 수직 확장 (현재 Branch C 정의)
- 현재 시나리오 안에서 world-side process를 더 깊게 surface
- crowd / authority / public attention / blame / memory를 더 잘 보이게 함
- 같은 사건이라도 cast composition과 placement에 따라 다른 world dynamics가 나오는지 확인
- 사람 내부 arc를 넘어서 **세계 차원의 observables**가 읽히게 만듦

### 4.3 현재 프로젝트 문맥에서의 broader world 정의
현재 Branch C에서 broader world는 다음으로 정의한다.

> **현재 3개 scenario 안에서,  
> 사람의 내적 변화뿐 아니라 crowd / authority / public attention / blame concentration / memory residue 같은  
> world-side observables가 독립적인 축으로 읽히고 비교될 수 있는 상태.**

즉 broader world는 “더 많은 이야기”가 아니라  
**“더 많은 세계 차원의 관측 가능성”**이다.

---

## 5. Branch C 완료 기준 (1차)

## 결론
Branch C는 open-ended branch로 두지 않는다.  
이번 Branch C PREP/1차 완료 기준은 **target-based**로 명시한다.

### 5.1 완료 기준 A — World-side observables 명시 완료
다음 항목이 문서로 고정되어야 한다.

- crowd mood
- authority vigilance / presence
- public attention
- blame concentration
- public suspicion
- world memory residue
- cohort split signal

즉, “우리가 세계에서 무엇을 보려는가”가 분명해야 한다.

---

### 5.2 완료 기준 B — Annotated output acceptance 기준 정의
annotated output이 Branch C에서도 계속 유효한지 판단하기 위한 acceptance 기준이 있어야 한다.

최소 질문:
- 어떤 필드가 필수인가
- 어떤 필드는 optional인가
- readability를 해치지 않는 선에서 world-side signal을 얼마나 surface할 것인가
- arc readability와 world readability를 동시에 유지할 수 있는가

---

### 5.3 완료 기준 C — 첫 use case 범위 고정
아래 중 무엇을 이번 Branch C prep의 실행 단위로 볼지 문서화되어야 한다.

- accusation depth expansion
- scarcity depth expansion
- sacred depth expansion
- cast composition variation
- placement variation
- authority observability pass

즉, **이번에 실제로 무엇을 시도할 것인가**가 잘려 있어야 한다.

---

### 5.4 완료 기준 D — 금지선 명시
아래가 여전히 금지라는 점이 문서화되어야 한다.

- engine code 변경
- shame_decay 구현
- authority autonomy 구현
- belonging field 추가
- broader world execution
- world/ legacy refactor

이 금지선이 없으면 Branch C prep가 engine tinkering으로 흐를 수 있다.

---

### 5.5 완료 기준 E — Branch C spec 문서 1개 고정
최소 한 문서에서 아래를 모두 다뤄야 한다.

- broader world 정의
- 첫 use case
- observables 목록
- acceptance 기준
- completion criterion
- forbidden_now
- world/ legacy 처리 원칙

이 문서가 곧 Branch C 준비 단계의 canonical entry point가 된다.

---

## 6. world/ legacy 재검토 여부

## 결론
**현재는 재검토하지 않는다. Freeze 유지가 맞다.**

### 이유
- `world/`는 별도 spike / legacy 축이다
- current canonical world 흐름은 `engine/world/` + readability infra + current scenario 체계 위에서 정의되고 있다
- 지금 Branch C prep는 canonical current branch를 기준으로 해야 한다
- `world/`를 다시 열면 canonical / legacy 구분이 흐려진다
- tests / imports 의존성도 남아 있어 건드리는 비용이 지금 이득보다 크다

### 운영 원칙
- `world/`, `docs/world/`, `pipeline_v2`, `abc_snapshots`는 계속 freeze
- Branch C prep 문서에서도 explicitly “out of scope”로 적는다
- 별도 directive 없이는 손대지 않는다

---

## 7. 지금 바로 진행할 작업 (즉시 실행 가능)

아래 작업은 **engine 변경 없이**, 그리고 **Lee 추가 지시 없이도** Claude Code가 진행 가능하다.

---

### Task 1 — Branch C scope 문서 작성
추천 파일명:
- `docs/b_direction/BRANCH_C_SCOPE_AND_CRITERIA.md`

포함할 내용:
- first use case
- broader world 정의
- completion criterion
- forbidden_now
- world/ legacy freeze
- immediate next actions

이 문서가 이번 정리의 핵심 산출물이다.

---

### Task 2 — World-side observables 문서 작성
추천 파일명:
- `docs/b_direction/WORLD_SIDE_OBSERVABLES.md`

최소 항목:
- observable name
- source field / source layer
- why it matters
- where it appears now
- how it should appear in annotated outputs
- target readability signal

추천 observable:
- crowd_mood
- authority_vigilance
- public_attention
- public_suspicion
- blame_concentration
- world_memory_residue
- cohort_divergence

---

### Task 3 — Annotated output acceptance test 정의
추천 파일명:
- `docs/b_direction/ANNOTATED_OUTPUT_ACCEPTANCE_TEST.md`

질문 예시:
- final summary는 유지되는가
- primary pressure가 실제로 scenario typing에 도움 되는가
- failure mode가 saturation 이해를 돕는가
- authority / public_attention / crowd_mood가 동시에 surface되어도 과부하가 아닌가
- readability를 해치지 않으면서 world-side observables가 드러나는가

---

### Task 4 — Branch C design scope draft
추천 파일명:
- `docs/b_direction/BRANCH_C_DESIGN_DRAFT.md`

포함할 것:
- 이번 C prep에서 할 것
- 하지 않을 것
- target outputs
- validation questions
- prep 완료 시점
- execution gate 조건

---

## 8. 지금 하면 안 되는 것

아래는 여전히 금지다.

- engine code 변경
- shame_decay 구현
- trust→shame coupling 구현
- belonging field 추가
- authority autonomy 구현
- broader world execution
- new scenario 추가
- world/ legacy refactor
- Branch C 완료 선언

즉 지금은 **문서화 / 관측 가능성 정의 / acceptance 기준 정리 단계**다.

---

## 9. Claude Code 운영 원칙 (다음 라운드용)

Claude Code는 다음 원칙으로 Branch C prep를 진행한다.

1. **기본 branch는 A+C prep**
2. 하지만 C execution으로 넘어가지 않는다
3. 한 루프당 목표는 하나만
4. engine behavior 변경은 하지 않는다
5. 모든 출력은 “준비”인지 “실행”인지 명확히 표시한다
6. human gate가 없어도 계속 가능한 low-risk 문서 작업은 계속한다
7. diminishing returns 구간에 들어가면 새 문서 생성보다 기존 canonical 문서 통합/정렬을 우선한다

---

## 10. Branch C prep 완료 후 다음 질문

이번 prep가 끝나면 다음 질문으로 넘어간다.

1. 첫 execution slice는 무엇인가?
   - accusation depth?
   - scarcity depth?
   - sacred depth?
   - cast composition variation?
   - authority observability pass?

2. 그 slice의 validation은 무엇인가?
   - readability 유지?
   - world-side observables 증가?
   - cohort split 더 명확?
   - public attention / authority signal 분리?

3. execution에 필요한 최소 engine touch가 생기는가?
   - 그렇다면 별도 Lee directive 요청

---

## 11. 최종 한 줄 요약

**현재 WITNESS는 Branch A를 통과했고, Branch C는 준비 단계에 들어갈 수 있다.  
첫 Branch C는 4th scenario를 늘리는 수평 확장이 아니라,  
현재 3개 scenario 안에서 world-side observables와 population variation을 더 깊게 드러내는 수직 확장으로 정의하는 것이 맞다.  
지금 바로 해야 할 일은 engine 변경이 아니라,  
Branch C scope / world-side observables / annotated acceptance 기준을 문서로 고정하는 것이다.**
