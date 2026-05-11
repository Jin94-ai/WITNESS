# WITNESS — 다음 진행 계획서 (Renderer Freeze + Branch C External Eval 기준)

## 0. 문서 목적

이 문서는 현재 WITNESS 프로젝트의 최신 판단을 반영해,  
다음 단계에서 무엇을 해야 하는지 명확히 정리한 실행 계획서다.

이번 판단의 핵심은 다음과 같다.

> **Branch C external eval은 진행한다.  
> Renderer는 Cycle 7에서 멈춘다.  
> 지금부터 Renderer는 추가 patch 단계가 아니라 선별·편집·패키징 준비 단계다.  
> Branch C external eval이 4/5 PASS 이상일 때만 creative asset pack v1로 간다.**

즉, 다음 단계의 방향은:
- 더 만드는 것 아님
- **외부 검증 + curated selection 준비**
이다.

---

## 1. 현재 상태 고정

### 1.1 Branch C
- `BRANCH_C_18_PROBES_SEND_BUNDLE(3).md`는 **그대로 진행 가능**
- §A = GPT-5.5로 보낼 본문
- §B = Lee 개인 노트 / ground truth / validation criteria
- 단일 seed bias도 미리 공개되어 있음
- 평가 기준도 5개로 기계적 판정 가능

### 결론
**Branch C external eval = GO**

---

### 1.2 Renderer
- Cycle 1~7까지 누적 개선 진행
- Lee v2에서 잡힌 약점 5/5는 사실상 처리
- Sample 기준:
  - 좋은 것 2
  - 애매한 것 2
  - bad 탈출 1
- Cycle 8 후보들은 현재 기준으로 과공학 위험이 큼

### 결론
**Renderer Cycle 8 = 중지**
**Renderer = Freeze**

---

### 1.3 Creative Asset Pack
현재 renderer는 “더 patch”할 단계가 아니라
**좋은 출력 선별 + 편집 + 패키징 준비**
단계로 들어갔다.

단, 이 단계는 아직 바로 public demo로 가는 게 아니라,
**Branch C external eval과 결합된 후 curated internal/demo pack**으로 먼저 가야 한다.

---

## 2. 이번 판단의 핵심 요약

### 2.1 Branch C에 대한 판단
- 외부 평가로 바로 보내도 됨
- 구조상 bundle 문제 없음
- 운영 원칙만 지키면 됨

### 반드시 지킬 5가지
1. 새 GPT-5.5 채팅에서 시작
2. §A만 paste
3. §B는 절대 paste하지 않음
4. “내 프로젝트야” 같은 사전 설명 금지
5. 응답 raw text를 `BRANCH_C_GPT55_RESPONSE_RAW.md`에 저장

---

### 2.2 Renderer에 대한 판단
- Cycle 1~7 누적 효과는 분명히 있음
- 하지만 Cycle 8부터는 개선보다 **과공학 가능성**이 큼
- 특히 남은 문제는 engine/renderer patch보다
  **curation / editing / packaging 문제**에 가까움

### 결론
- Renderer는 Cycle 7에서 freeze
- 추가 patch 금지
- 다음 단계는 **curated pack 준비**

---

### 2.3 최신 판단 source
`RENDERER_GATE1_V3_RESULTS.md`는 Cycle 2 시점 기준 구버전이다.

### 처리 원칙
- `RENDERER_GATE1_V3_RESULTS.md`
  → **superseded / reference only**
- 최신 판단 source
  → **`RENDERER_GATE1_V3_BUNDLE_CYCLE7(1).md` 기준**

이 정리를 명확히 하지 않으면 문서 체계가 꼬인다.

---

## 3. Lee 최종 평가 요약 반영

### 3.1 Renderer sample별 판단
| # | Sample | 판단 |
|---|---|---|
| 1 | P6 MIXED scarcity | asset 후보 가능 |
| 2 | Trilogy modal 3-act | demo / explainer asset 성격 |
| 3 | P9 SAT scarcity | 개선됨, 다만 설명문 냄새 일부 잔존 |
| 4 | P10 REC accusation | asset 후보 가능 |
| 5 | P_PV_09 LOW_ACTIVITY | bad 탈출, 하지만 hook 약함 |
| 6 | P_CV_01 MIXED accusation | good에 가깝지만 템플릿 냄새 약간 |

### 3.2 Cycle 평가
- 가장 좋은 Cycle 변화: **Cycle 3**
  - scenario × outcome SAT/MIXED differentiation
- 가장 약한 Cycle 변화: **Cycle 7**
  - motif closing line, 반복 리스크 있음

### 3.3 종합 판단
> **v2에서 잡힌 약점은 대부분 해결되었다.  
> 다만 Cycle 5~7 이후부터는 개선과 과공학의 경계에 들어왔으므로,  
> renderer cycle은 여기서 멈추는 게 맞다.**

---

## 4. 다음 진행 원칙

## 원칙 1 — Branch C external eval 먼저
다음 단계의 첫 행동은 Branch C external eval 실행이다.

이유:
- Branch C는 구조 검증
- Renderer는 전달 검증
- 둘 중 하나만 통과해도 부족함
- 따라서 지금 먼저 해야 할 것은 **구조 검증의 외부 판독 확보**

---

## 원칙 2 — Renderer는 patch가 아니라 curation
Renderer는 더 늘리거나 뜯는 단계가 아니다.

이제 해야 할 일:
- 좋은 것 선별
- 애매한 것 편집 필요 여부 표시
- bad/weak sample은 보류
- curated pack 기준 정리

즉 이제 Renderer 쪽의 핵심은
**“어떻게 더 만들까”가 아니라 “무엇을 살릴까”**다.

---

## 원칙 3 — public demo는 아직 아님
Renderer만 통과했다고 외부 공개하면 안 된다.

### 이유
- Branch C external eval 결과가 아직 없음
- 구조 검증과 전달 검증이 둘 다 필요함

따라서:
- 지금은 internal curated pack 준비 가능
- public-facing demo / asset pack 공개는 아직 아님

---

## 5. 다음 진행 순서

## Step 1 — Branch C External Eval 실행
### 해야 할 일
- `BRANCH_C_18_PROBES_SEND_BUNDLE(3).md`에서 §A만 복사
- GPT-5.5 새 채팅에 paste
- 응답 raw 저장

### 저장 파일
- `docs/b_direction/BRANCH_C_GPT55_RESPONSE_RAW.md`

### 완료 조건
- raw response 저장 완료
- 5개 PASS 기준 적용 준비 완료

---

## Step 2 — Branch C 결과 판정
### 기준
5개 기준 중 **4/5 PASS 이상**이면 통과로 본다.

### 분기
- **4/5 이상 PASS**
  → Branch C lock 가능
  → creative asset pack v1 단계로 이동
- **4/5 미만**
  → Branch C lock 보류
  → renderer 공개 / pack 진행도 함께 보류

---

## Step 3 — Renderer 문서 정리
### 해야 할 일
1. `RENDERER_GATE1_V3_RESULTS.md`
   - superseded / reference only 처리
2. 최신 판단 source를
   - `RENDERER_GATE1_V3_BUNDLE_CYCLE7(1).md`
   로 명시
3. Cycle 7 freeze 상태 공식화 문서 갱신

### 목적
- decision source 혼선 제거
- 이후 creative pack에서 어떤 문서를 기준으로 삼을지 명확화

---

## Step 4 — Curated Internal Pack 초안 준비
단, Step 2 통과 시에만 진행.

### 포함 후보
**강한 후보**
- P6 MIXED scarcity
- P10 REC accusation
- P_CV_01 MIXED accusation

**demo / explainer**
- Scarcity Trilogy

**보류 / 편집 필요**
- P9 SAT scarcity
- LOW_ACTIVITY

### 산출물
- `docs/creative/CREATIVE_ASSET_PACK_V1_PLAN.md`

### 포함 항목
- 포함 작품
- 제외 작품
- 편집 필요 여부
- demo용 / asset용 분리

---

## 6. 지금 하지 말아야 할 것

- Renderer Cycle 8
- narrator distance control
- omniscient ↔ micro 전환
- LOW_ACTIVITY × scenario 추가 cycle
- motif closing 추가 patch
- density-aware sentence pool
- style profile 확장
- public demo 오픈
- Branch C external eval 전 creative asset pack 공개

즉 지금은 **추가 창작/추가 개선 금지** 상태다.

---

## 7. Claude Code용 작업 지시

Claude Code는 다음 순서로 움직인다.

### Stage 1
1. Branch C external eval 실행 지원
2. response raw 저장 구조 준비
3. PASS 5 criteria 점검표 준비

### Stage 2
4. Renderer 문서 체계 정리
   - `RENDERER_GATE1_V3_RESULTS.md` → superseded
   - Cycle 7 bundle → latest decision source

### Stage 3
5. Branch C 결과가 4/5 PASS 이상이면
   - `CREATIVE_ASSET_PACK_V1_PLAN.md` 작성
   - curated internal/demo pack 준비

### Stage 4
6. Branch C 결과가 4/5 미만이면
   - creative asset pack 진행 중지
   - renderer 공개도 중지
   - 다음 directive 대기

---

## 8. 최종 결정문

지금 기준으로 최종 결정은 아래와 같다.

> **Branch C 18-probe external eval은 그대로 진행한다.  
> Renderer는 Cycle 7에서 멈춘다. Cycle 8은 하지 않는다.  
> 현재 renderer는 더 고칠 단계가 아니라 선별·편집·패키징 단계다.  
> `RENDERER_GATE1_V3_RESULTS.md`는 Cycle 2 기준 구버전이므로 reference only로 내리고,  
> 최신 판단은 Cycle 7 bundle 기준으로 한다.  
> Branch C external eval이 4/5 PASS 이상이면 creative asset pack v1로 간다.  
> PASS가 아니면 Branch C lock은 보류하고, renderer 공개도 같이 보류한다.**

---

## 9. 한 줄 요약

**지금부터의 핵심은 더 만드는 것이 아니라,  
Branch C external eval을 보내 구조 검증을 끝내고,  
Renderer는 Cycle 7에서 멈춘 채 좋은 결과만 선별할 준비를 하는 것이다.  
그리고 두 검증이 모두 맞을 때만 creative asset pack v1로 이동한다.**
