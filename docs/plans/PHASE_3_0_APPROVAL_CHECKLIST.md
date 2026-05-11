# Phase 3.0 Approval Checklist

> Per `docs/WITNESS_PHASE_2_9_PORTFOLIO_FINALIZATION_AND_PHASE_3_PREP_PLAN.md` §6.1+§7.3.

이 문서는 **Phase 3.0 Data & Annotation Pilot**을 시작하기 전 사용자 승인이
필요한 항목들을 목록으로 정리한다. 각 항목이 체크되어야 *실제 작업*이 시작될
수 있다.

> **Note (cycle 70+, per [PHASE_3_0_ACTUAL_PILOT_BOUNDARY.md](PHASE_3_0_ACTUAL_PILOT_BOUNDARY.md))**:
> *Phase 3.0 **Actual Mini Pilot**은 Mode A (수동 LLM annotation) 한정*. 따라서
> 본 체크리스트 중:
> - **필수 (Mode A pilot 진입)**: #1 (manual input 형태로 변경 가능) / #2 (출처 ToS — Mode A에서는 Lee가 직접 ingest이므로 source 외부 fetch 아님 — *선택* 가능) / #5 (저장 정책) / #7 (10-episode 범위)
> - **deferred (Mode C — Actual Mini Pilot에서 사용 금지)**: #3 (LLM API) / #4 (비용 상한)
> - #6 (공개 repo 정책)은 Mode 무관 항상 필수.
>
> Mode C 활성화는 *Actual Mini Pilot 통과 후 별도 directive* 필요. Boundary §3.2가 강제.

---

## 1. 5+2 핵심 승인 항목

### ☐ 1. 실제 줄거리 데이터 fetch 승인

```text
승인 내용:
- 외부 사이트에서 회차 줄거리(synopsis_text_ko)를 자동으로 가져오는 작업 시작
- robots.txt + ToS 사전 확인 후
- rate limit 준수 (예: 1 req/sec 이하)
- user-agent 명시 ("WITNESS-Phase3.0-Pilot/0.1 (research)")

승인 효과:
- scripts/data/fetch_synopsis.py 같은 fetcher 작성/실행 가능
- data/external_private/synopsis_raw/ 에 저장 (.gitignore)
```

승인 시 사용자가 다음에 답해야 함:
- [ ] 어느 source부터 시작? (DATA_SOURCE_CANDIDATE_REVIEW.md 표 참조)
- [ ] rate limit 상한 (req/sec)?
- [ ] user-agent 문자열 OK?

---

### ☐ 2. 출처별 ToS / robots.txt 검토 승인

```text
승인 내용:
- 각 source의 robots.txt + ToS를 직접 읽고 사용자에게 보고
- "이 사이트는 OK / 보류 / 제외" 결정 사용자에게 위임
- 모호한 경우 안전 측 (제외)

승인 효과:
- 검토 결과를 DATA_SOURCE_CANDIDATE_REVIEW.md 표에 기록
- 통과한 source만 #1 fetch 대상에 포함
```

승인 시 답할 항목:
- [ ] 검토 결과 모호한 source는 제외하는 보수 정책 OK?
- [ ] 출처 메타에 robots.txt + ToS 상태 기록 OK?

---

### ☐ 3. LLM API 사용 승인

```text
승인 내용:
- Claude / GPT / Gemini 등 외부 LLM API 호출
- annotation prompt를 LLM에 전송
- LLM 응답(JSON)을 받아 디스크에 저장

승인 효과:
- scripts/annotation/annotate_with_llm.py 의 *real LLM call mode* 활성화
  (현재는 dry-run + fixture mode만 작동)
- API key 설정 + 호출 로깅
```

승인 시 답할 항목:
- [ ] 어느 LLM부터? (Claude / GPT / Gemini 중 1차 2개)
- [ ] API key 보관 방법? (.env / OS keyring)
- [ ] 호출 로그 저장 위치?

---

### ☐ 4. 비용 상한 승인

```text
승인 내용:
- LLM API 호출 누적 비용 상한 (예: $X)
- 상한 초과 시 즉시 중단

승인 효과:
- 1차 10 episodes × 2-3 LLM = ~20-30 calls
- 예상 비용: 수$ ~ 수십$ (모델별)
```

승인 시 답할 항목:
- [ ] 1차 pilot 비용 상한? ($)
- [ ] 누적 vs 일일 상한?
- [ ] 상한 초과 시 알림 vs 자동 중단?

---

### ☐ 5. 저장 위치 / 공개 가능성 결정

```text
승인 내용:
- 원문 synopsis: 비공개 (data/external_private/, .gitignore)
- per-annotator raw: 비공개
- annotation feature vector (수치): 공개 가능
- short evidence quote (≤ 30자): 내부 audit용 우선
- portfolio HTML 본문: 원문 노출 금지

승인 효과:
- 위 정책에 맞춰 .gitignore 추가
- portfolio HTML에 본문 인용 0
```

승인 시 답할 항목:
- [ ] 원문 비공개 OK?
- [ ] feature vector 공개 가능?
- [ ] short evidence quote 길이 상한? (≤ 30자)

---

### ☐ 6. (보조) 공개 repo 정책 승인

```text
승인 내용:
- portfolio repo가 public인 경우, data/external_private/는 .gitignore
- annotation feature CSV는 공개 OK (저작권 위험 없음)
- reliability report는 공개 OK
- HTML demo는 본문 인용 0
```

승인 시 답할 항목:
- [ ] repo가 public? private?
- [ ] feature CSV 공개 OK?

---

### ☐ 7. (보조) 10-episode mini pilot 승인

```text
승인 내용:
- 1차 pilot 범위 = 1 genre × 2 titles × 5 episodes = 10 synopses
- 1차 통과 후 사용자 재승인 받아 2차 (40 synopses) 진행

승인 효과:
- 작은 단위 시작 → 위험 통제
- 1차 reliability report 기반 2차 결정
```

승인 시 답할 항목:
- [ ] 1차 10 episodes 우선 OK?
- [ ] 어느 genre? (한국 막장 우선?)
- [ ] 어느 2 titles? (또는 사용자가 선정?)

---

## 2. 승인 절차

### 2.1 단계별 승인

각 항목을 한 번에 모두 받지 않고, *순서대로* 한 단계씩 승인:

```text
Step 1. 데이터 소스 후보 검토 (사용자가 DATA_SOURCE_CANDIDATE_REVIEW.md 검토)
   ↓
Step 2. 1-2개 source 선정 (사용자가 표에 OK 표시)
   ↓
Step 3. robots.txt + ToS 검토 (claude가 보고 → 사용자 승인)
   ↓
Step 4. fetch 승인 (#1)
   ↓
Step 5. 1 episode 샘플 fetch + 사용자 검토
   ↓
Step 6. 나머지 9 episodes fetch
   ↓
Step 7. LLM API 승인 (#3) + 비용 상한 (#4)
   ↓
Step 8. 1 episode annotation 샘플 → 사용자 검토
   ↓
Step 9. 나머지 9 episodes annotation
   ↓
Step 10. reliability report 작성
   ↓
Step 11. 1차 통과 / fail 판정
   ↓
Step 12. 2차 확장 여부 결정 (사용자 추가 승인)
```

### 2.2 중단 권한

사용자는 어느 단계에서든 즉시 중단 가능. 중단 시 진행 중인 fetch / API call 즉시 정지.

---

## 3. 미승인 시 안전 행동

승인이 떨어지지 않은 상태에서 claude는 다음을 *절대* 하지 않는다:

```text
- 외부 사이트 fetch (robots.txt 확인 포함)
- LLM API 호출 (Claude / GPT / Gemini)
- 원문 synopsis 저장
- 학습 코드 실행
- 비용 발생 행동
```

대신 다음만 가능:

```text
- 후보 source 문서 정리 (DATA_SOURCE_CANDIDATE_REVIEW.md)
- prompt template 검토 (network 0)
- mock fixture 기반 dry-run
- 도구 코드 점검 (validate / synthesize / hallucination_rate / inter_annotator)
- 문서 작성 / 정리
```

---

## 4. 한 줄 결론

```text
이 체크리스트의 모든 항목이 ☑ 표시되기 전까지 Phase 3.0의 *실제* 작업은 0건.
승인은 단계별로 받고, 각 단계마다 사용자에게 보고한다.
```

---

## 5. 변경 이력

| 일시 | 변경 |
|---|---|
| 2026-05-10 | initial — Phase 2.9 §6.1 매핑 |
| 2026-05-11 (cycle 78) | Mode A 한정 진입 명시 — ACTUAL_PILOT_BOUNDARY와 정합. #3-4 (Mode C) deferred 명시 |
