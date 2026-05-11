# WITNESS — 다음 진행 지시서 (자율 가능 작업 소진 이후)

## 0. 문서 목적

이 문서는 이번 세션 진행 결과를 바탕으로,  
**지금 어디까지 왔는지 요약하고 다음으로 무엇을 해야 하는지**를 정리한 실행 지시서다.

중요한 점은 하나다.

> **이번 회차에서 자율적으로 할 수 있고 가치 있는 작업은 사실상 거의 소진되었다.  
> 따라서 다음 단계는 “더 돌릴 것 찾기”가 아니라, 남은 갈림길 중 무엇을 선택할지 잠그는 일이다.**

이 문서는 그 선택을 대신 내려서,
Claude Code가 다음 지시 없이도 불필요한 정체 없이 움직일 수 있게 만드는 것을 목표로 한다.

---

## 1. 현재 상태 요약

이번 회차까지의 성과는 아래처럼 정리된다.

### 1.1 Story Output MVP
- 3-stage pipeline 완성
- 48 stories 생성 완료
  - baseline 12
  - Branch C 36
- Phase 2 acceptance 6/6 PASS
- story output MVP는 이제 “있다” 수준이 아니라 **검증된 결과물 층**으로 봐도 된다

### 1.2 Branch C 1차 evidence
- 36 probes
- cross-seed walkback 완료
- paper §6.9 / Appendix G 반영
- `LEE_GATE_2026-04-28_BRANCH_C.md` 5 options 대기

### 1.3 Paper synchronization
- §6 findings 8 → 10
- §7.4 single-seed inadequacy 추가
- Appendix G + H 추가
- Abstract 7 findings 반영

### 1.4 Pytest 운영 개선
- `tests/test_story/` 신설
- 119 tests / 0.23초
- fast layer가 실제로 작동하는 상태

### 1.5 J-Alpha / J-Beta
- selector
- 5-variation demo
- scarcity_high_density 발견
- variation review / anchor comparison 완료
- queryable library 4 API
- 5 anchors 확보
- Scarcity Trilogy nonmonotonic IP narrative beat 확보

### 1.6 Cleanup
- visible files 226 → 133 (-41%)
- archive 7 subdir
- README / CLAUDE / DESIGN / lessons / auto-memory index 정리

---

## 2. 현재 국면 진단

현재 국면은 다음처럼 판단한다.

### 결론
**지금은 “자율 작업 지속” 국면이 아니라 “선택해야 하는 국면”이다.**

즉,
- 더 돌리면 무언가 나오긴 하겠지만
- 큰 가치 없이 marginal work만 늘어날 확률이 높다
- 의미 있는 다음 진전은 남은 결정 몇 개를 잠그는 데서 나온다

따라서 지금부터는 무작정 자율 루프를 더 돌리지 않는다.

---

## 3. 내가 내리는 판단

사용자가 직접 판단해야 한다고 적힌 항목들 중, 지금 기준으로 아래처럼 결정한다.

---

## 3.1 결정 1 — density-aware sentence pool
### 판단: **지금 하지 않음**
보류가 맞다.

### 이유
- 구현 비용이 의외로 크다
  - annotated header 변경
  - IR atom 수정
  - generator 영향
- 그런데 현재 얻는 가치는 “같은 outcome 내부의 미세 cell 차이 표현 강화” 수준이다
- 지금 이 프로젝트의 병목은 거기까지의 미세한 문장 차별화가 아니다
- 현재는 이미 story output MVP가 통과했으므로, 이건 2차 미세 개선에 가깝다

### 상태
- `J-Beta phase 2 backlog`로 이동
- 지금 사이클에서는 실행 금지

---

## 3.2 결정 2 — Lee Gate 1 v2 (renderer diagnosis 직접 평가)
### 판단: **다음 최우선**
이게 다음 1순위다.

### 이유
지금 creative track에서 가장 실제적인 병목은
- selector가 있냐
- story가 나오냐
가 아니라

**“이 렌더러 출력이 창작물로서 어디가 약한가를 인간 기준으로 정확히 잡는 것”**
이다.

Claude bias 기반 진단은 이미 1차로 충분히 했다.  
이제 남은 건 **실제 사람 눈으로 renderer의 약점을 찍는 것**이다.

### 효과
이걸 하면:
- style profile 확장 방향이 잡히고
- J-Beta 이후 renderer cycle이 방향을 얻고
- density-aware 같은 미세 작업이 진짜 필요한지도 판별된다

즉 지금 가장 생산적인 다음 단계는 Gate 1 v2다.

---

## 3.3 결정 3 — Branch C 5 options
### 판단: **지금은 GPT-5.5 send가 우선, engine touch는 보류**
선택은 **(B) 중에서 “GPT-5.5 send” 쪽으로 간다.**

### 이유
- Branch C 1차 evidence는 이미 충분히 정리됐다
- engine touch(S6 authority autonomy)는 kernel change라 너무 무겁다
- S1 accusation depth는 지금 가치가 작다
- 지금 phase에서는 더 파는 것보다 **외부 판독/외부 반응**이 낫다

즉 Branch C는 지금:
- 더 실험하는 것보다
- **외부 검증 / 외부 읽힘 테스트**를 먼저 받는 게 맞다

### 상태
- Branch C immediate recommendation = **GPT-5.5 send with proper disclosure**
- S6 engine touch = deferred
- S1 = skip
- research deepening = hold

---

## 3.4 결정 4 — 70+ trajectory labeling
### 판단: **지금 당장 하지 않음**
자동 진행 금지.

### 이유
- schema 자체가 설계 결정이다
- labeling을 돌리기 시작하면 다시 체계 구축 작업이 커진다
- 현재는 이미 creative output / variation demo / selector library가 돌아가므로
- 70+ labeling은 “좋은 다음 단계”일 수 있어도 “지금 가장 좋은 다음 단계”는 아니다

### 상태
- J-Beta 확장 후보로 유지
- renderer diagnosis 이후 다시 판단

---

## 3.5 결정 5 — style profile 확장
### 판단: **renderer diagnosis 이후에만**
바로 하지 않는다.

### 이유
- 소설 톤 / 웹소설 톤 분기는 취향 문제가 아니라 출력 가치 문제다
- 그런데 현재는 인간 기준의 강약점 맵이 먼저다
- 진단 없이 style만 확장하면 다시 문체 실험 루프에 빠질 가능성이 높다

### 상태
- Gate 1 v2 이후 진행
- 지금은 보류

---

## 3.6 결정 6 — IP mode 확장 (drama / webtoon / game)
### 판단: **금지 유지**
지금 하지 않는다.

### 이유
- 이미 문서에도 후순위로 적혀 있다
- 지금 소설/웹소설 1차도 아직 renderer ground truth가 약하다
- mode 확장은 결과물 확장이 아니라 복잡도 확장이다

---

## 3.7 결정 7 — Van Gogh real annotated probe generator
### 판단: **지금 보류**
바로 하지 않는다.

### 이유
- 새 generator 작업은 새 트랙을 연다
- 현재는 Peter / Branch C / variation demo / story MVP를 막 통과한 상태
- Van Gogh real generator는 지금 꼭 필요한 다음 스텝이 아니다
- renderer diagnosis 이후 creative quality 기준이 잡히면 그때 하는 게 맞다

---

## 4. 따라서 다음 우선순위

## 최우선 1 — Renderer Human Diagnosis (Gate 1 v2)
이게 다음 1순위다.

### 해야 할 것
- 현재 renderer 출력 샘플 5개 선정
  - 좋은 것 2
  - 애매한 것 2
  - 나쁜 것 1
- Lee가 직접 읽고
  - 어디가 좋고
  - 어디가 약하고
  - creative output으로서 무엇이 어색한지
  표시

### 산출물
- `docs/creative/RENDERER_DIAGNOSIS_GATE1_V2.md`

### 목적
- renderer 약점 ground truth 확보
- style/profile/표현 개선의 실제 기준 확보

---

## 최우선 2 — Branch C GPT-5.5 Send
이게 2순위다.

### 해야 할 것
- 현재 Branch C package를 다시 점검
- disclosure 문제 없는지 확인
- send용 package 정리
- GPT-5.5로 보내 external reading 받기

### 산출물
- `docs/b_direction/BRANCH_C_GPT55_SEND_PACKAGE.md`
- 또는 기존 blind package 갱신

### 목적
- Branch C를 더 파는 대신 외부 반응 확보
- engine touch 전 외부 판독을 먼저 받음

---

## 3순위 — Renderer 2차 cycle
단, Gate 1 v2 이후.

### 해야 할 것
- renderer weakness 3개 추출
- 우선순위 2개만 고르기
- 개선 후 before/after 비교

### 산출물
- `docs/creative/RENDERER_CYCLE_2_PLAN.md`

---

## 4순위 — J-Beta 확장 항목 재평가
이건 위 1~3이 끝난 뒤.

재평가 대상:
- 70+ labeling
- style profile 분기
- density-aware
- Van Gogh real generator

즉 지금은 여기까지 가지 않는다.

---

## 5. Claude Code 다음 작업 지시

Claude Code는 다음 순서로 진행한다.

### Step 1
`docs/creative/RENDERER_DIAGNOSIS_GATE1_V2.md` 템플릿 문서 작성

포함:
- 샘플 5개 목록
- good / bad / awkward / flat / report-like 분류 칸
- 한 줄 총평
- 다음 cycle에서 반드시 고칠 3개 항목 체크란

### Step 2
renderer 샘플 5개 선정 + 정리
- 좋은 것 2
- 애매한 것 2
- 나쁜 것 1

### Step 3
Branch C send package 점검 문서 작성
- disclosure
- current claim
- external question
- package completeness 확인

추천 파일:
- `docs/b_direction/BRANCH_C_GPT55_SEND_CHECKLIST.md`

### Step 4
Gate 1 v2와 GPT-5.5 send 준비가 끝나면 멈춤
이후는 새 directive 또는 결과 입력을 기다림

---

## 6. 지금 하지 말아야 할 것

- density-aware sentence pool 구현
- 70+ trajectory labeling 시작
- style profile 확장 시작
- drama/webtoon/game 확장
- Van Gogh real generator 시작
- Branch C engine touch
- Branch C 새 slice 실험
- paper 추가 확장

지금은 **새로운 제작보다 진단과 외부 판독이 우선**이다.

---

## 7. 다음 단계 이후 예상 흐름

### 경우 A — Gate 1 v2 결과가 명확함
→ renderer cycle 2 진행  
→ style profile 확장 여부 판단

### 경우 B — GPT-5.5 send 결과가 강하게 긍정적
→ Branch C evidence 잠금  
→ creative track 쪽 story selector / variation demo 자산화 강화

### 경우 C — GPT-5.5 send 결과가 애매함
→ Branch C는 유지하되 research deepening은 하지 않고  
creative output 중심으로만 계속

### 경우 D — renderer 평가가 매우 부정적
→ style expansion 전에 renderer core 수정 먼저

---

## 8. 최종 한 줄 요약

**현재 자율적으로 할 수 있고 가치 있는 작업은 거의 소진되었다.  
따라서 다음 단계는 “더 만들기”가 아니라,  
(1) renderer human diagnosis를 통해 creative ground truth를 확보하고  
(2) Branch C를 GPT-5.5에 보내 외부 판독을 받는 것이다.  
그 전까지 density-aware, 70+ labeling, style 분기, 새 generator 같은 확장 작업은 하지 않는다.**
