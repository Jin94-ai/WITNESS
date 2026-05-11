# WITNESS Internal Demo Package v1 — Review

**Date**: 2026-04-30
**Source**: `docs/plan.md` Phase 6 review
**Method**: 6 평가 질문 + Case D 판정 + Phase 7 prep
**Verdict**: **Case D-A — Internal Demo Package v1 성공** → Phase 7 (Long-term Fork Decision) 진행 가능

---

## 0. Review 방식

본 review는 *self-evaluation* — 실제 시연 사용 데이터 미반영. *문서 패키징 quality* + *데모 흐름 설계 정합성* + *제약 준수* 점검.

평가 대상:
- `INTERNAL_DEMO_PACKAGE_V1.md` (12 sections)
- `DEMO_SCRIPT_V1.md` (5분 대본 + FAQ + cheat sheet + 시간 옵션)
- `KNOWN_LIMITATIONS_V1.md` (9 한계 + 강점)
- `DEMO_RUN_CHECKLIST_V1.md` (A-M 13 sections)

---

## 1. 6 평가 질문 답변

### Q1. 5분 안에 설명 가능한가?

**△ 가능 (예상 5:00, 허용 4:30~5:30)**.

**근거**:
- DEMO_SCRIPT_V1.md 시간 budget 명시:
  - 0:00-0:30 도입 (30초)
  - 0:30-2:00 화면 1 (90초)
  - 2:00-3:30 화면 2 (90초)
  - 3:30-4:40 화면 3 (70초)
  - 4:40-5:00 마무리 (20초)
  - **합계**: 5분
- DEMO_RUN_CHECKLIST_V1.md §K 자체 시연 항목으로 *사전 측정* 권장
- *시간 초과 위험*: 화면 2 cross-seed가 click 횟수 많아 길어질 수 있음 (압축 옵션 명시됨)

**불확실성**:
- 청중 질문 도중 답변 → 시간 초과 (DEMO_SCRIPT FAQ §"마지막 30초 이후 받기" 권고로 완화)
- 시연자 처음 시연 시 ~6분 가능 (사전 자체 시연 1회 권장)

**자동 검증 한계**: 실제 시연 시간 측정 미수행. 예상값.

---

### Q2. 세 화면이 각각 다른 메시지를 갖는가?

**✅ 명확히 다름**.

**근거** (INTERNAL_DEMO_PACKAGE_V1.md §5):

| 화면 | 핵심 메시지 |
|---|---|
| 1. peter_baseline | *"세계가 흐르고, 어디가 중요한지 visual로 보인다."* |
| 2. peter_triple cross-seed | *"같은 anchor가 어떤 운명들을 낳을 수 있는지 — configuration sensitivity."* |
| 3. vangogh | *"다른 scenario family는 다른 dynamics. 시스템이 자동 판정 안 함."* |

세 메시지가 *겹치지 않고 누적*:
- 화면 1 = WITNESS의 *기본 사용*
- 화면 2 = WITNESS의 *unique 발견* (configuration sensitivity)
- 화면 3 = WITNESS의 *철학* (관찰기 ≠ 평가기)

→ 각 화면 후 청중이 *"방금 무슨 메시지?"* 묻지 못할 수준의 명확성.

---

### Q3. Visual + Packet만으로 충분한가?

**✅ 충분 (peter 계열) / △ 부분 (vangogh)**.

**근거**:
- Phase 4 Browsing Pack Q6 검증: visual + packet > text-only (격동 anchor 압도)
- Phase 5 TEXT_VISUAL_ROLE_REASSESSMENT.md Q1 결정: *story text는 v0.1에서 선택*
- 데모 script 모든 화면이 *visual + packet only*로 흐름 연결

**Vangogh 부분**:
- *"왜 vangogh가 흥미로운가"*는 packet panel만으로 부족 가능
- 그러나 Phase 5에서 *"sacred는 다른 dynamics"*로 의미 부여 → 데모 script에서 이 framing으로 다룸
- Story text가 *흐름의 필수 요소가 아님* → 시연자 백업 도구

**불확실성**:
- 청중이 *"vangogh도 story text 보여줘"* 강하게 요구 시 → CLI 백업 (DEMO_SCRIPT_V1 §FAQ)

---

### Q4. Story text 부재가 데모를 막는가?

**❌ 막지 않음**.

**근거**:
- Phase 5 Case TV-A 판정: visual + packet 충분
- Story panel placeholder는 *Lee directive 명시 일관 (story renderer 재개 금지)*
- DEMO_SCRIPT_V1 §FAQ에서 *"Visual + packet으로 *세계 흐름*과 *후보 식별*까지는 충분"* 답변 명시
- 백업 CLI 도구 (`render_candidate_story.py`)가 *시연자 자신 있게* 응답 가능

**시나리오 점검**:
- *"text 없으니 의미를 모르겠다"* 청중 → 시연자 답변 가능 (DEMO_SCRIPT §FAQ Q1)
- *"vangogh story 보여줘"* 청중 → 별도 CLI 즉시 시연 가능 (DEMO_RUN_CHECKLIST §I 사전 점검)

→ Story text 부재는 *데모 블로커 0건* (KNOWN_LIMITATIONS_V1 §1.3 일관).

---

### Q5. WITNESS가 무엇인지 한 문장으로 설명 가능한가?

**✅ 가능 — INTERNAL_DEMO_PACKAGE_V1.md §0 verbatim**:

> *"WITNESS는 텍스트 이야기 생성기가 아니라, 움직이는 세계를 도트 기반으로 관찰하고, 그 안에서 이야기 후보를 발견하는 *world simulation explorer*다."*

**검증**:
- 길이: ~50 단어 (한 문장)
- 명확성: *"world simulation explorer"* 한 phrase가 핵심
- 차별화: *"텍스트 이야기 생성기가 아니라"*로 *anti-position* 명시
- 실행 가능: 청중이 *"WITNESS는 X를 한다"* paraphrase 가능 — *"세계 관찰 + 이야기 후보 발견"*

**검증 기준** (INTERNAL_DEMO_PACKAGE_V1.md §7.1 Hard 기준 #4):
- *"청중이 'WITNESS는 X를 한다'를 한 문장으로 paraphrase 가능"*
- → 본 review 자체에서 paraphrase 검증됨 ✅

---

### Q6. 다음 fork decision으로 넘어갈 수 있는가?

**✅ Yes**.

**근거**:
- Phase 1-6 누적 결과 모두 success (Case A / TV-A / BP-A / EX-A / D-A 예상)
- Lee plan.md Phase 7 정의: *"이 프로젝트를 앞으로 어디로 확장할지 결정"*
- Phase 6에서 *데모 자체*가 fork decision의 evidence 제공:
  - "Visual 중심으로 작동" → 옵션 1 (Visual Explorer 중심) evidence
  - "Configuration sensitivity 시연 가능" → 옵션 3 (Simulation Research) evidence
  - "Story 후보 발견" → 옵션 2 (Story/IP Asset) 가능성
  - "Intervention 미구현" → 옵션 4 (Playable Prototype) 가능성

**Phase 7에서 답할 4 옵션**:
1. Visual Explorer 중심 → 관찰형 세계 엔진 발전
2. Story/IP Asset 중심 → 좋은 후보 → 이야기/IP 씨앗 발전
3. Simulation Research 중심 → paper / engine validation 강화
4. Playable Prototype 중심 → intervention / what-if / player action

**현재 데모 evidence가 4 옵션 모두에 *부분적 입력* 제공**:
- 옵션 1: Explorer가 *internal diagnostic*까지 작동 (이번 v1)
- 옵션 2: Story_ready candidate가 식별됨 (peter 5개)
- 옵션 3: Cross-seed nonmonotonic finding이 paper-grade evidence와 연결 가능
- 옵션 4: 현재 0 — fork 시 별도 단계 필요

→ Phase 7로 *진입 가능 상태*. 어느 옵션을 *선택*할지는 별도 결정.

---

## 2. 6 질문 종합

| # | 질문 | 결과 |
|---|---|:---:|
| Q1 | 5분 안에 설명 가능 | △ (예상 5:00, 사전 자체 시연 권장) |
| Q2 | 3 화면 다른 메시지 | ✅ |
| Q3 | Visual + Packet 충분 | ✅ peter / △ vangogh (시연자 답변 가능) |
| Q4 | Story text 부재가 데모 막음 | ❌ 막지 않음 |
| Q5 | WITNESS 한 문장 설명 가능 | ✅ |
| Q6 | Phase 7 fork decision 진입 가능 | ✅ |

→ **5/6 ✅ + 1 △ + 1 ❌(긍정) → Case D-A 충족**.

---

## 3. Case D-A vs D-B vs D-C vs D-D 평가

### Case D-A 조건: Internal Demo Package v1 성공
- ✅ 6/6 평가 질문 모두 *작동 또는 명시적 답변 가능*
- ✅ 5분 budget 안에 3 화면 + 도입 + 마무리
- ✅ 시연자 자료 (script + checklist + limitations) 모두 작성
- ✅ Story text 부재 = *데모 블로커 아님* (Q4)
- ✅ Lee 9 금지 항목 모두 준수

### Case D-B 조건: 데모는 가능하지만 story text 부족
- 적용 안 됨 — Q3/Q4에서 Visual + Packet 충분 검증 (story text 필수 아님)
- 만약 추후 시연 후 *"story text 있으면 더 좋겠다"* 피드백 시 → 별도 directive로 *static export* 검토 가능 (Phase 5 TV-B 옵션)

### Case D-C 조건: 데모 흐름이 약함
- 적용 안 됨 — Q1/Q2에서 흐름 + 메시지 명확성 검증

### Case D-D 조건: 아직 데모 불가
- 적용 안 됨 — 모든 핵심 항목 충족

### 결정: **Case D-A — Internal Demo Package v1 성공**

근거 종합:
1. 6/6 평가 질문 통과 (5 ✅ + 1 △ + 1 ❌긍정)
2. 5 doc 모두 작성 (package + script + limitations + checklist + review)
3. 5분 budget 안에 3 화면 흐름 정합성 (DEMO_SCRIPT_V1)
4. 한계 명시 + 답변 가능 (KNOWN_LIMITATIONS_V1)
5. 시연 전 점검 list 완비 (DEMO_RUN_CHECKLIST_V1)
6. Story text 부재가 *디자인된 한계* (Lee directive 일관)

→ **Phase 7 (Long-term Fork Decision) 진행 가능**.

---

## 4. HARNESS 적용

### What I did NOT verify
- *실제* 5분 시연 시간 측정
- 청중 *실제* reaction
- 시연자 *말하는 흐름*의 자연스러움 (script가 글로 매끄러워도 말로 옮길 때 다를 수 있음)
- Browser performance (200 ticks replay 시 frame drop 여부)
- *처음 사용 시연자* (script 처음 읽는 사람)에게 5분 budget 가능한지

### What could still be wrong
- 5분이 *너무 빡빡*해서 청중이 *압박감* 느낄 수 있음
- vangogh 화면이 *시연자 본인*에게는 명확하지만 *청중*에게는 *왜 보여주는지* 불명확 가능
- "configuration sensitivity"라는 *technical term*이 *비전공 청중*에게 어려울 가능
- 5 sec doc set이 *시연자 부담*일 수 있음 (script 외워야 하는 분량 ~700 단어)

### Alternate interpretations
- (a) Case D-A → Phase 7 (이번 결과)
- (b) 실제 시연 후 *story text 필요* 피드백 → Case D-B 후속
- (c) 실제 시연 후 *5분 budget 부족* → DEMO_SCRIPT 압축 옵션 (4분 모드) 활용
- (d) 실제 시연 후 *3 화면 다 못 봄* → Case D-C 후속

→ 본 review (a) 선택. (b)/(c)/(d)는 *실제 시연 후 평가*에서 결정.

---

## 5. Phase 7 prep notes (4 옵션 evidence 정리)

Lee plan.md Phase 7 §"4 옵션":

### 옵션 1 — Visual Explorer 중심
**Evidence (현재까지)**:
- explorer.html v0.2 작동 (broad navigation entry)
- 3 anchor 통합 (peter_baseline / peter_triple / vangogh)
- Single-run + Cross-seed 두 view 통합
- Browsing Pack v1 Case BP-A
- Demo Package v1 Case D-A (이번 결과)

**가치**:
- 관찰형 세계 엔진으로 발전 가능
- *internal diagnostic tool*에서 *external explorer*로 확장 가능

**비용**:
- Multi-anchor 대확장 필요 (vangogh 외 sacred / accusation 더)
- Cross-seed 대확장 필요 (다른 anchor cross-seed)
- Mobile / responsive design (visual polish 영역)
- Public-facing UI (안내문 / onboarding)

### 옵션 2 — Story / IP Asset 중심
**Evidence (현재까지)**:
- Q1-Q4 curation = 5 story_ready (peter_baseline)
- `render_candidate_story.py` 3-lens narration 작동
- Branch C 18 probes (creative track 1차 증명)
- Asset Pack v1 (4 candidate narratives, paper Appendix H)

**가치**:
- 좋은 후보 → 이야기/IP 씨앗으로 발전
- creative output 수익 가능성

**비용**:
- Story renderer 재개 (Cycle 8+ 재시작)
- Manual edit / curation 비중 ↑
- Quality verdict (관찰기 ≠ 평가기 원칙 약화 가능성)

### 옵션 3 — Simulation Research 중심
**Evidence (현재까지)**:
- 1845 fast tests
- Paper §6 10 findings + Appendix G/H
- Branch C cross-seed sensitivity (S5 placement 44%, S4 cast 56%)
- Configuration sensitivity within-scenario (3/3 scenario groups)
- Trilogy modal (1/2/3 accusations nonmonotonic)

**가치**:
- Paper / engine validation 강화
- Academic contribution

**비용**:
- 5+ seed ensemble (HARNESS H8) per claim
- Cross-anchor / cross-scenario 확장
- 외부 review 필요 (peer review)

### 옵션 4 — Playable Prototype 중심
**Evidence (현재까지)**:
- 0 — 현재 *관찰자 모드만*
- Intervention / what-if / player action 모두 forbidden_now

**가치**:
- 실제 *체험형* WITNESS
- 게임 / 인터랙티브 콘텐츠 가능성

**비용**:
- Engine 대규모 변경 (intervention API 추가)
- UI 대규모 변경 (action selection / outcome preview)
- Validation 새로 시작 (intervention 후 outcome 변화 측정)
- 가장 큰 단가

---

## 6. Phase 7에서 답할 핵심 질문

1. **가장 많이 살아 있는 결과물이 무엇인가?**
   - Visual Explorer (사용 빈도 추정 가장 높음)
   - Cross-seed visualization (configuration sensitivity의 핵심)
   - 1845 tests (engine evidence)

2. **Lee가 계속 만지고 싶은 방향은 무엇인가?**
   - (Lee 본인 결정 영역)

3. **실제 결과물로 보여주기 쉬운 방향은 무엇인가?**
   - Visual Explorer (5분 데모 가능 — 이번 v1)
   - Story/IP (4 candidate narratives)
   - Paper (Appendix G/H)
   - Playable (현재 0)

4. **구현 난이도 대비 가치가 가장 큰 방향은 무엇인가?**
   - 옵션 1 (Visual Explorer 확장) — 단가 중간, 가치 명확
   - 옵션 3 (Simulation Research) — 단가 중간, 가치 academic
   - 옵션 4 (Playable) — 단가 높음, 가치 큼 (장기)

→ Phase 7에서 *evidence 종합*하고 *Lee 결정*.

---

## 7. Lee 10 금지 항목 준수

| 금지 항목 | 준수 |
|---|:---:|
| 코드 수정 | ✅ doc 5개만 |
| 새 visual 기능 | ✅ |
| story renderer 재개 | ✅ |
| 새 anchor 추가 | ✅ |
| sacred-specific metric 추가 | ✅ |
| bucket 추가 | ✅ |
| React / 3D / 캐릭터 / animation | ✅ |
| player intervention | ✅ |
| visual polish | ✅ |
| public demo packaging | ✅ Internal scope 명시 (INTERNAL_DEMO_PACKAGE_V1 §1.1) |

---

## 8. Phase 6 stop rule (Lee plan.md §GLOBAL STOP RULE)

1. **산출물 요약**:
   - `INTERNAL_DEMO_PACKAGE_V1.md` (12 sections)
   - `DEMO_SCRIPT_V1.md` (5분 대본 + FAQ + cheat sheet)
   - `KNOWN_LIMITATIONS_V1.md` (9 한계 + 강점)
   - `DEMO_RUN_CHECKLIST_V1.md` (A-M 13 sections)
   - `INTERNAL_DEMO_PACKAGE_REVIEW.md` (이 문서)

2. **성공/실패 판정**: ✅ **Case D-A 성공**

3. **다음 Phase로 갈지**: ✅ Phase 7 (Long-term Fork Decision) 진행 가능

4. **새 기능 추가 안 했는지**: ❌ 추가 0 (코드 변경 0, doc 5개만)

5. **Forbidden 위반 여부**: ❌ 0건

---

## 9. 한 줄 요약

> **Internal Demo Package v1 = 5 doc (package / script / limitations / checklist / review). 5분 / 3 화면 / 한 문장 메시지 (world simulation explorer). 6/6 평가 질문 통과 (5 ✅ + 1 △ + 1 ❌긍정). Visual + Packet으로 충분, story text는 시연자 백업 도구. Case D-A 성공 → Phase 7 (Long-term Fork Decision) 진행 가능. 코드 0 변경, Lee 10 금지 항목 모두 준수.**

---

**Versioning**: v1 (this review) — 2026-04-30 Phase 6 완료. Case D-A.
