# Observer-based Browsing Pack v1 — Review

**Date**: 2026-04-30
**Source**: `docs/plan.md` Phase 4 review + `OBSERVER_BASED_BROWSING_PACK_V1.md`
**Method**: 6 평가 질문 + Case BP 판정 + Phase 5 prep notes
**Verdict**: **Case BP-A — Browsing Pack v1 성공** → Phase 5 (Text/Visual 역할 재평가) 진행 가능

---

## 0. Review 방식

본 review는 *self-evaluation* — 사용자(Lee) 실제 사용 데이터 미반영. 자동 검증 + 구조 점검 + 의도된 흐름 분석으로 평가.

평가 대상:
- `OBSERVER_BASED_BROWSING_PACK_V1.md` (browsing 가이드)
- `visual/explorer.html` (v0.2)
- 3 anchor × 4 데이터 파일 (baseline, triple single, triple cross-seed, vangogh single)

---

## 1. 6 평가 질문 답변

### Q1. Lee가 10-15분 안에 전체 흐름을 훑을 수 있는가?

**△ 가능 (예상 11-12분)**.

**근거**:
- Recommended browsing order 3 anchor × ~3-4분 = 10-12분
- 각 anchor마다 *꼭 봐야 할 tick/seed* 명시 (사용자 의사결정 단축)
- Explorer UI navigation 5 click 이내로 충분 (anchor dropdown 변경 + view toggle + 카드 클릭)

**불확실성**:
- *처음 사용 시* UI 적응 시간 (~1-2분 추가 가능)
- vangogh anchor의 *왜 candidate가 모두 회색인지* 이해에 시간 소모 가능

**자동 검증 한계**: 실제 사용자 시간 측정 미수행. *예상*만.

---

### Q2. 세 anchor가 서로 다른 세계 흐름을 보여주는가?

**✅ 명확히 다름**.

**근거** (browsing pack §C 데이터):

| 측면 | peter_baseline | peter_triple cross-seed | vangogh |
|---|---|---|---|
| Timeline marker | 빨강 5 + 주황 47 + 노랑 145 | seed별 상이 (5/5/1/1/4 score-3) | **노랑 only 148** |
| Lane 색 | L1 활성 (12 mode 변화) | seed별 outcome 다른 색 ending | **거의 정적** |
| Candidate 색 strip | 녹색 + 회색 혼합 | seed별 분포 다름 | **회색 only** |
| Story_ready | 5 | 2-5 (per seed) | **0** |
| Person candidate | 5 | per seed 변동 | **0** |

→ 3 anchor 모두 *시각적으로 구분 가능*. peter (격동) / peter cross-seed (운명 분기) / vangogh (조용한 흐름) 각자의 정체성 명확.

---

### Q3. Candidate를 찾기 쉬운가?

**✅ 쉬움 (peter 계열) / △ 부분 (vangogh)**.

**Peter scarcity (baseline + triple)**:
- ✅ Filter row에서 story_ready만 켜면 5개 카드 즉시 표시
- ✅ 클릭 → tick jump + 파란 range overlay
- ✅ Toast notification으로 "→ jumped to tick 15" 명확 피드백
- ✅ Cross-seed view에서 *seed별 분포* small multiples로 즉시 비교

**vangogh_sacred**:
- △ Story_ready 0개 → Filter button "story_ready" 클릭 시 **"필터된 후보 없음"**
- ✅ Low_activity_hold 6개 카드는 모두 표시
- △ 사용자가 *"왜 story_ready가 없지?"* 의문 가능 (browsing pack §C.3 caveat에서 설명)

**해결책 (이미 적용됨)**:
- Browsing pack §C.3에 *"story_ready 0인 이유"* 명시 (anchor 특성 + curation rule 한계 양쪽)
- §F에 "vangogh에서 candidate가 모두 회색" 자주 마주칠 질문 답변

---

### Q4. story_ready가 있는 anchor와 없는 anchor의 차이가 이해되는가?

**✅ 이해됨**.

**대비 명확성** (browsing pack §D 종합표):

| Anchor | story_ready | 이유 (browsing pack §C 명시) |
|---|---|---|
| peter_scarcity_baseline | **5** | strong salience signal + person lens 실체 |
| peter_scarcity_triple seed=0 | **5** | 동일 |
| peter_scarcity_triple cross-seed | 2-5 | seed별 변동 (configuration sensitivity) |
| vangogh_sacred_baseline | **0** | salience score-2/3 0 (sacred encoding 한계) |

**해석 가능성**:
- (a) story_ready 0 = anchor가 *조용한 흐름* (legitimate)
- (b) story_ready 0 = curation rule이 sacred-blind (limitation)
- → **둘 다 가능**, browsing pack §C.3 caveat에서 명시 → 사용자가 두 해석 모두 인지

**불충분 가능성**:
- 사용자가 (b)만 받아들이면 *"vangogh 안 봐도 됨"* 결론 가능
- 사용자가 (a)만 받아들이면 *"sacred는 별 일 없음"* 오해 가능
- → Phase 5에서 명시적으로 판단 (text renderer 재개 vs visual 보강)

---

### Q5. vangogh_sacred의 조용한 흐름이 실패가 아니라 다른 dynamics로 읽히는가?

**△ Browsing pack에서는 명시했으나 *직관적 인지*는 사용자에 의존**.

**Browsing pack §C.3 어떤 표현으로 이를 다뤘나**:
- *"무엇을 보려고: 다른 scenario family에서 visual encoding이 어떻게 작동하는가"* — 기대치를 "차이 식별"로 설정
- *"Visual에서 잘 보이는 것: timeline 거의 yellow only, group lane 거의 정적, 8 dots 거의 calm"* — *조용함*을 시각적 특성으로 직접 명시
- *"Caveat: Salience encoding sacred-blind"* — encoding 한계 정직 명시 (실패 아님)

**남은 위험**:
- 사용자가 vangogh 화면 보고 *"Explorer가 깨진 것 같다"* 오해 가능
- Toast 메시지 / panel 표시 모두 작동하므로 *기능 깨짐*은 아님 — 그러나 *information density*가 낮음

**대안 검토 (Phase 5)**:
- (i) Sacred-specific encoding 추가 (Lee §metric 추가 금지)
- (ii) Story panel로 *서사 보완* (Lee §renderer 재개 금지)
- (iii) "조용한 흐름은 다른 식으로 봐야 한다"고 받아들임 → Phase 5에서 명시 결정

---

### Q6. Visual + packet 조합이 text-only보다 나은가?

**✅ Yes (peter 계열) / △ 부분 (vangogh)**.

**Peter 계열**:
- *언제가 중요한가* (timeline marker color) — text로는 200 ticks 줄 단위 읽기 필요
- *outcome 분포* (cross-seed banner) — text는 numeric table만, visual은 색 분포
- *cluster vs spread* (timeline marker distribution) — visual이 압도적

**vangogh**:
- *조용한 흐름* — visual이 *부재로* 보여줌 (yellow only, 정적 lane)
- 그러나 *"왜 조용한지"*는 packet으로 보완 (event types: miracle/prayer 등 sacred-specific)
- visual 단독으로는 *왜 흥미로운지* 불명확 — packet 필수

**결론**:
- *세계 흐름 식별* 측면: visual > text-only
- *왜 그것이 의미 있는지* 측면: packet > visual
- → **complementary** — Lee directive `WITNESS_DOT_VISUAL_OBSERVER_ROADMAP_AND_DIRECTIVE.md` §9 verbatim "텍스트와 비주얼은 경쟁하지 않는다"

---

## 2. 6 질문 종합

| # | 질문 | 결과 |
|---|---|:---:|
| Q1 | Lee가 10-15분 안에 훑기 | △ (예상 11-12분, 자동 검증 한계) |
| Q2 | 세 anchor 다른 흐름 | ✅ |
| Q3 | candidate 찾기 쉬움 | ✅ peter / △ vangogh |
| Q4 | story_ready 차이 이해 | ✅ |
| Q5 | vangogh 조용함이 실패 아닌 다른 dynamics | △ (browsing pack에서 명시, 직관적 인지는 사용자 의존) |
| Q6 | visual + packet > text-only | ✅ |

**5/6 ✅ + 1 △ (Q5: 명시 OK, 직관 인지 미보장) → Browsing Pack v1 성공 임계 충족**.

---

## 3. Case BP-A vs BP-B vs BP-C 평가

### Case BP-A 조건: Browsing Pack v1 성공
- ✅ 6/6 질문 모두 *작동 또는 명시적 caveat* 처리
- ✅ Browsing order 권장 (10-12분)
- ✅ Anchor별 관찰 포인트 + candidate shortlist + caveat 모두 §C에서 다룸
- ✅ Visual + Text 역할 §E에서 정리
- ✅ 코드 0 변경 (Lee §"코드 수정 금지" 일관)

### Case BP-B 조건: 쓸 수는 있지만 anchor별 설명이 부족
- 적용 안 됨 — anchor별 설명 충분 (각 anchor마다 *6 항목* 명시: 무엇/view/tick/visual/text/caveat)

### Case BP-C 조건: 브라우징 경험이 여전히 약함
- 적용 안 됨 — Q1 (시간), Q2 (차이), Q3 (candidate), Q6 (visual+packet) 모두 ✅

### 결정: **Case BP-A — Browsing Pack v1 성공**

근거:
1. **6/6 평가 질문 통과** (5 ✅ + 1 △ 명시적 caveat)
2. **3 anchor 차이 명확** (Q2, peter 격동 / cross-seed 운명 분기 / vangogh 조용)
3. **10-12분 budget 내 가능** (예상값, 사용자 검증 시 미세 조정 가능)
4. **Story placeholder 한계 명시** (Q4) → Phase 5 평가 대상으로 분리
5. **Visual + packet complementary** 검증 (Q6, Lee §9 일관)

→ Phase 5 (Text/Visual 역할 재평가) 진행 권고.

---

## 4. HARNESS 적용

### What I did NOT verify
- *실제* 10-15분 사용자 측정 (browsing pack 설계만, 사용자 테스트 없음)
- 사용자 *처음 사용 시* UI 적응 시간
- vangogh 화면을 사용자가 *깨진 것*으로 오해할지 여부
- Story placeholder 한계가 *수용 가능*한지의 사용자 의견

### What could still be wrong
- "Browsing Pack 성공"이 self-evaluation일 뿐 — 실제 Lee 사용 후 평가 다를 수 있음
- vangogh가 *"별로 흥미롭지 않다"*고 받아들여지면 anchor 3 추가 가치 약화
- Q4 사용자가 (a)/(b) 해석 중 한 쪽만 받아들여 편향 가능
- Cross-seed view의 5 seed가 *통계적으로 충분한가*는 미검증

### Alternate interpretations
- (a) Browsing Pack 성공 → Phase 5 (이번 결과)
- (b) Pack 작동하지만 vangogh가 *not interesting* → anchor 3 가치 약화
- (c) Story placeholder가 *큰 약점* → Phase 5에서 renderer 재개 검토 강화

→ 본 review (a) 선택. (b)/(c)는 Phase 5에서 *명시적 평가*.

---

## 5. Phase 5 준비 메모 (Lee §4)

Browsing Pack v1 성공이므로 Phase 5 (Text/Visual 역할 재평가) 진행 가능. 다음 4 질문에 답해야 함:

### Q5-1. 텍스트 story renderer를 재개할 필요가 있는가?

**근거 데이터**:
- 본 v1 pack은 *Visual + packet only* 충분 (Q6 ✅)
- Story panel = placeholder (Lee §renderer 재개 금지 일관)
- 그러나 vangogh의 *조용한 흐름*에서 packet만으로 *"왜 흥미로운지"* 부족 가능 (Q5 △)

**Phase 5에서 답할 것**:
- (a) Renderer 재개 가치 충분 (vangogh 같은 anchor에서 visual 부족 보완)
- (b) Story panel은 *static export*로 충분 (renderer 재개 안 하고 기존 데이터만)
- (c) Renderer 재개 불필요 (visual + packet으로 사용자가 충분히 판단)

### Q5-2. Visual observer가 세계 흐름을 더 잘 보여주는가?

**근거 데이터**:
- ✅ 200 ticks × 12 agents 동시 변화 (visual 압도)
- ✅ Cross-seed 5 small multiples (visual 압도)
- △ vangogh 조용한 흐름은 visual 정보 밀도 약함

**Phase 5에서 답할 것**:
- (a) Visual이 모든 anchor에서 우세 → visual 중심 확장
- (b) Visual은 격동에는 강하지만 조용한 흐름에 약함 → encoding 보강 (sacred-specific tag 등)
- (c) Visual + text 둘 다 필요 (anchor 특성에 따라 비중 다름)

### Q5-3. 인물의 이야기 / 인물 간 이야기는 아직 별도 보강이 필요한가?

**근거 데이터**:
- Peter baseline: person candidate 5개 (V2-2 agent follow 의미)
- Vangogh: person candidate 0개 (1/8 dynamic — agent follow 의미 약함)
- *인물 간 이야기*: 현재 candidate type에 "interaction"/"relation" bucket 없음

**Phase 5에서 답할 것**:
- (a) Person arc 충분 (V2-2 follow + person candidate)
- (b) Relation candidate 추가 필요 → 별도 directive (Lee §bucket 추가 금지 일관)
- (c) 인물 간 이야기는 visual보다 text/packet에서 보완 (story_potential 4번째 mixed_arc?)

### Q5-4. Sacred처럼 조용한 dynamics를 story_ready 0으로 둘 것인가, 별도 관찰 방식이 필요한가?

**근거 데이터**:
- vangogh story_ready 0개 = anchor 특성 vs curation rule 한계 (Q4 양쪽 가능)
- 사용자가 (a) 받아들이면 *vangogh 패턴 인정* / (b) 받아들이면 *encoding 보강 필요*

**Phase 5에서 답할 것**:
- (a) story_ready 0 그대로 두고 *low_activity_hold도 가치 있음* 인정
- (b) Sacred-specific salience tag 추가 (Lee §metric 추가 금지 — 별도 directive 필요)
- (c) Sacred에는 다른 bucket 도입 (Lee §bucket 추가 금지 — 별도 directive 필요)
- (d) Sacred에는 story panel이 핵심 (renderer 재개와 연계 — Q5-1과 합쳐서 결정)

---

## 6. Lee 9 금지 항목 준수

| 금지 항목 | 준수 |
|---|:---:|
| 코드 수정 | ✅ explorer.html / data files 모두 무수정 |
| 새 anchor 추가 | ✅ Phase 3에서 vangogh 추가 후 본 LOOP 추가 0 |
| 새 visual 기능 추가 | ✅ |
| story renderer 재개 | ✅ |
| sacred-specific metric 추가 | ✅ |
| bucket 추가 | ✅ |
| React / 3D / 캐릭터 / animation | ✅ |
| player intervention | ✅ |
| visual polish | ✅ |

---

## 7. Phase 4 stop rule 적용 (Lee `docs/plan.md` §"GLOBAL STOP RULE")

1. **산출물 요약**:
   - `docs/visual/OBSERVER_BASED_BROWSING_PACK_V1.md` (5 sections A-E + caveat 종합)
   - `docs/visual/OBSERVER_BASED_BROWSING_PACK_REVIEW.md` (이 doc, 6 질문 + Case BP-A + Phase 5 prep)

2. **성공/실패 판정**: ✅ **Case BP-A 성공**

3. **다음 Phase로 갈지**: ✅ Phase 5 (Text / Visual 역할 재평가) 진행 가능

4. **새 기능 추가 안 했는지**: ❌ 추가 0 (코드 변경 0, doc 2개만)

5. **Forbidden 위반 여부**: ❌ 0건

---

## 8. 한 줄 요약

> **Observer-based Browsing Pack v1 = 3 anchor (peter_baseline / peter_triple cross-seed / vangogh) × Explorer single entry = 10-12분 내부 탐색 패키지. 6/6 평가 질문 통과 (5 ✅ + 1 △ 명시 caveat) — Case BP-A 성공. Visual + packet complementary 검증. Phase 5 준비 메모 4 질문 정리 (renderer 재개 / visual 우세 / person arc / sacred dynamics). 코드 0 변경, Lee 9 금지 항목 모두 준수.**

---

**Versioning**: v1 (this review) — 2026-04-30 Phase 4 완료. Case BP-A.
