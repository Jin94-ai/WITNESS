# WITNESS Demo v1 — Known Limitations

**Date**: 2026-04-30
**Source**: `docs/plan.md` Phase 6 + 누적 review (Phase 1-5)
**Audience**: 시연자(Lee) + 데모 청중 (질문 시 핸들링용)

---

## 0. 핵심 disclaimer

> **이 데모는 internal diagnostic tool입니다. Public product가 아닙니다.**

본 doc은 *알려진 한계 명시 + 청중 질문 핸들링 가이드*. 한계 자체가 *데모를 막지는 않음* — 시연자가 *정직하게 답변*하면 됨.

---

## 1. 8 Known Limitations

### 1.1 Single-seed bias

**현상**:
- `peter_scarcity_baseline` 데이터: seed=0 only
- `vangogh_sacred_baseline` 데이터: seed=0 only
- 즉 두 anchor는 *각각 1번의 simulation snapshot*만 visual에 반영됨

**영향**:
- *"이게 일반적 패턴인가요?"* 질문에 답할 근거 부족
- 다른 seed에서 다른 결과 나올 수 있음

**완화**:
- `peter_scarcity_triple`은 5 seeds cross-seed 수행 (화면 2에서 시연)
- HARNESS H8 (single-seed conditioning warns) 일관

**시연자 답변**:
> "맞아요, 그건 single-seed snapshot입니다. 화면 2에서 5 seeds로 *변동성*을 보여드린 게 그래서예요. 더 robust한 evidence는 별도 paper-grade 자료에 있습니다."

---

### 1.2 Sacred encoding 약함

**현상**:
- vangogh_sacred_baseline에서 score-2/3 marker **0개** (148개 모두 score-1)
- candidate 6개 모두 low_activity_hold (story_ready 0)
- group mode 변화 1회만 (peter는 12회)

**원인**:
- 8 tag salience system이 *외부 충격* 위주로 설계됨 (cohort_split / saturation_lock 등)
- Sacred dynamics는 *내부적 변화* — score-2/3 trigger 못 함

**영향**:
- vangogh 화면이 *visual 정보 밀도 낮음*
- 청중이 *"실패 같다"*고 오해 가능

**완화** (이미 적용):
- 데모 script에서 *"실패가 아닌 다른 dynamics"* 명시
- Browsing pack §C.3 caveat 명시

**시연자 답변**:
> "vangogh가 *조용한 흐름*인 건 정확합니다. WITNESS는 좋은 이야기/나쁜 이야기를 자동 판정하지 않습니다 — 시스템이 *이건 보류 후보다*라고 알려주는 거고, 사용자가 판단합니다. 그게 *관찰기 ≠ 평가기* 원칙."

---

### 1.3 Story panel placeholder

**현상**:
- Explorer의 "Story / lens text" panel이 항상 placeholder
- *"별도 story text는 본 v0에 통합 안 됨 — story renderer 재개 금지 조항"* 메시지

**원인**:
- Lee directive 명시 *story renderer 재개 금지*
- v0/v0.1/v0.2 모두 일관

**영향**:
- 청중이 *"text가 없어서 의미를 모르겠다"* 가능

**완화**:
- Packet panel이 candidate metadata로 대체 (rationale + signals + classification)
- 별도 CLI 도구로 호출 가능 (`render_candidate_story.py`)

**시연자 답변**:
> "Story text는 v0.1에서 *선택*입니다. Visual + packet으로 *세계 흐름*과 *후보 식별*까지는 충분합니다. 후보의 *서사 흐름*이 필요하면 별도 CLI 도구가 있어요. Phase 5 평가에서 이게 데모 병목이 아니라고 결론 났습니다."

---

### 1.4 Person candidate vangogh 0

**현상**:
- vangogh_sacred에서 person candidate 0개
- peter_baseline은 5개 (story_ready 모두 person)

**원인**:
- vangogh는 8 agents 중 1명만 dynamic (≥3 distinct states)
- Anchor 자체 특성 — agent-driven dynamics 약함

**영향**:
- V2-2 selected agent follow가 vangogh에서 *의미 약함*
- "인물 따라가기" 경험 vangogh에서 부재

**완화 (가능 옵션, 본 v1에서는 미수행)**:
- v0.2 backlog: relation / interaction candidate
- Phase 7 fork decision 대상

**시연자 답변**:
> "맞습니다. 그건 anchor 특성입니다 — sacred dynamics는 *집단/사건 중심*이지 *개인 중심*이 아니에요. peter scarcity는 12명 중 4명이 dynamic이라 *agent follow*가 의미 있고, vangogh는 그 lens가 약합니다. 다른 lens (event / world)가 우세."

---

### 1.5 Cross-seed 단일 anchor

**현상**:
- 5 seeds cross-seed = `peter_scarcity_triple`만
- baseline / vangogh는 *single-seed only*

**원인**:
- Lee directive *"cross-seed 대확장 금지"*
- Phase 3에서 1 anchor만 추가, Phase 6에서도 추가 0

**영향**:
- "cross-seed가 *모든 anchor*에서 작동하나?" 질문에 답할 근거 부족
- baseline / vangogh 운명 분포는 별도 자료 필요

**완화**:
- 화면 2에서 *peter_triple* 시연으로 *concept* 입증
- "다른 anchor도 cross-seed 가능, scope 외" 답변

**시연자 답변**:
> "지금은 1개 anchor만 cross-seed 됐습니다 — `peter_scarcity_triple`. 이건 *configuration sensitivity 시연*이지 일반화 증명이 아니에요. 다른 anchor cross-seed는 별도 단계."

---

### 1.6 Relation / Interaction candidate 부재

**현상**:
- 현재 candidate type = person / event / world / mixed (4개)
- *relation / interaction candidate type 없음*
- *agent-pair lens / 관계 narration 부재*

**원인**:
- Lee directive *"bucket 추가 금지"*
- Phase 5에서 v0.2 backlog로 분리 결정

**영향**:
- "인물 간 이야기"가 *암시적*으로만 (cohort_split 등)
- 직접 visualize 안 됨

**완화**:
- `candidate.agents_involved` 필드에 *동시 발생 agents* 목록 보존 (방안)
- Phase 7 fork decision 대상 (옵션 4 — interaction layer 추가 검토)

**시연자 답변**:
> "현재는 4 candidate type만 있습니다. *인물 간 관계* candidate는 v0.2 backlog로 분리되어 있어요. Phase 7 fork decision에서 *interaction layer 추가*가 검토될 예정. 지금 데모에는 포함 안 됐습니다."

---

### 1.7 5 seeds 통계 한계

**현상**:
- Cross-seed view는 5 seeds (peter_triple) 사용
- 5 seeds = 통계적으로 *충분하지 않음*

**원인**:
- 한 화면 안에서 *대조 가능한 최대치*
- 더 많은 seeds (10+) 추가 시 visual clutter + export cost ↑

**영향**:
- "REC 3 / SAT 1 / PARTIAL 1 = nonmonotonic 확정?"이라고 물으면 *no*
- Statistical confidence interval 없음

**완화**:
- 데모 script에서 *"통계 증명이 아니라 시연"* 명시
- Paper-grade evidence는 별도 자료

**시연자 답변**:
> "5 seeds로 *통계 증명*하는 게 아니에요. **시연**입니다 — '같은 anchor가 어떤 운명들을 낳을 수 있는가'를 *대조*로 보여줍니다. Statistical confidence가 필요하면 paper-grade 별도 자료가 있어요."

---

### 1.8 Mobile / tablet viewport 미검증

**현상**:
- explorer.html이 desktop 1280×800+ 가정
- canvas 800×500 SVG fixed
- Mobile / tablet 화면에서 layout 깨짐 가능

**원인**:
- v0/v0.1/v0.2 모두 desktop 우선
- *visual polish 금지* directive와도 일관 (responsive design = polish 영역)

**영향**:
- 청중이 *모바일로 시연 시도*하면 깨짐
- 데모 환경 고정 (시연자 desktop)

**완화**:
- 데모 환경 권장사항 명시 (`INTERNAL_DEMO_PACKAGE_V1.md` §3.4)
- 시연 시 *반드시 시연자 desktop 사용*

**시연자 답변**:
> "이건 desktop 전용입니다. 모바일은 v1 scope 외예요. responsive design은 *visual polish* 영역이라 v0.x에서는 일부러 안 했습니다."

---

### 1.9 (보너스) Visual은 internal diagnostic tool

**현상**:
- Explorer / browsing pack / demo package 모두 *internal scope*
- Public product 아님

**원인**:
- Lee directive 명시 *"public-facing product packaging 금지"*
- *"public demo packaging 금지"* (Phase 6)
- 데모 v1 = internal scope

**영향**:
- 청중이 "이걸 사이트에 올려서 보여주면 되겠네"라고 오해 가능
- UI / 안내문 / 사용자 onboarding 부족

**완화**:
- INTERNAL_DEMO_PACKAGE_V1.md §1.1 / §2.3 명시
- 데모 마무리에서 *"internal tool" 다시 강조*

**시연자 답변**:
> "이건 *internal* tool입니다. UI도 *최소* 수준이라 사용자 onboarding 거의 없죠. Public product로 가려면 *완전히 다른 작업*이 필요합니다 — 그건 fork decision에서 결정될 예정."

---

## 2. 한계 종합표

| # | 한계 | 데모 영향 | 청중 질문 시 답변 가능? |
|---|---|:---:|:---:|
| 1 | Single-seed bias (peter baseline / vangogh) | 약 | ✅ |
| 2 | Sacred encoding 약함 (vangogh score-2/3 0) | 중 | ✅ |
| 3 | Story panel placeholder | 약 | ✅ |
| 4 | Person candidate vangogh 0 | 약 | ✅ |
| 5 | Cross-seed 단일 anchor | 약 | ✅ |
| 6 | Relation / Interaction candidate 부재 | 약 | ✅ |
| 7 | 5 seeds 통계 한계 | 중 | ✅ |
| 8 | Mobile / tablet 미검증 | 무 | ✅ |
| 9 | Internal scope only | 무 | ✅ |

→ **9개 한계 모두 *답변 가능* 상태**. 데모 *블로커 0건*.

---

## 3. 한계 *없는* 영역 (강점)

비교 균형을 위해 명시:
- ✅ **Engine integrity**: ABSOLUTE Rule #1/#6 모두 준수, 1845 fast tests pass
- ✅ **Visual stability**: V0-V1 + V2 + Anchor 2 + Cross-seed + Explorer v0/v0.1/v0.2 누적 검증, regression 0건
- ✅ **Schema consistency**: schema v1 + cross_seed_v1 무수정 계속 유지
- ✅ **External dependency 0**: vanilla JS + SVG, install 단순
- ✅ **3 anchor support**: peter_baseline / peter_triple / vangogh — scenario family generalize 검증
- ✅ **Documentation**: docs/visual/ + docs/demo/ + docs/observer/ 등 상세

---

## 4. 한 줄 요약

> **9 known limitations 모두 청중 질문 시 *자신 있게 답변 가능*. 한계 자체가 *데모 블로커 아님*. WITNESS 강점도 함께 명시 (engine integrity / visual stability / schema consistency / 0 external dep / 3 anchor / docs).**

---

**Versioning**: v1 (this limitations) — 2026-04-30 Phase 6 한계 명시.
