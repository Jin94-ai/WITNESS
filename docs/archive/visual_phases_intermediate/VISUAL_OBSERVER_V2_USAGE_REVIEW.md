# Visual Observer V2 — Usage Review (3 시나리오 검증)

**Date**: 2026-04-30
**Source**: `VISUAL_OBSERVER_V2_USAGE_SCENARIOS.md` 시나리오별 검증
**Verdict**: **Case A — V2 충분** → Anchor 2 visual validation으로 이동

---

## 0. 검증 방법

각 시나리오는 6 질문으로 점검:
1. 성공 여부
2. 막히는 지점
3. text panel 충분성
4. visual 단독 이해도
5. story candidate 탐색 도움
6. 다음에 고쳐야 할 것 1개

데이터 근거: `data/visual/dot_observer_data.json` (824 KB, 200 ticks × 12 agents × 3 groups). 5 score-3 marker, 8 candidates, 4 dynamic agents.

---

## 시나리오 A — World-first browsing

### 1. 성공 여부
**✅ 성공**.
- timeline-bar에서 score-3 marker (5개) 즉시 시각적 식별
- 클릭 → tick jump 즉시 작동
- 4 panel (World / Salience / Active candidates / canvas)이 같은 tick의 *세 측면* 동시 제공

### 2. 막히는 지점
**△ 1지점**: score-3 cluster (142-146-147) 3개가 4-tick window에 몰려 *서로 다른 사건처럼 보이는데 거의 같은 신호*(`cohort_split, saturation_lock, agent_state_shift`).
- 사용자가 "이 3개가 정말 다른 건가?" 의문 가능
- Active candidates panel에서 `+1 related`, `+2 related`로 표시되지만 timeline marker 자체는 동일하게 빨간 marker 3개

### 3. text panel 충분성
**✅ 충분**.
- World panel = mood + 4 metrics (한눈에)
- Salience tags = 어떤 신호인지 (3 tag chip)
- Active candidates = candidate ID + use_mode + lens (어디로 향할지)
- 3 panel을 한 화면에서 동시 읽으면 *왜 score-3인지* 이해됨

### 4. visual 단독 이해도
**△ 부분**.
- 도트 색 변화 + zone 색 변화는 보임 (L1 zone partial → saturation)
- 하지만 *왜* 변하는지 panel 없이는 모름 (예: "blame_concentration 0.32"는 panel 봐야 함)
- score-3 marker의 *어떤 신호*인지도 panel 없이는 모름
- → Lee §9 verbatim "visual = 어디를 볼지, text = 왜 중요한지" 원칙과 일관

### 5. story candidate 탐색 도움
**✅ 강한 도움**.
- 5 score-3 marker → 5 candidate (정확히 매칭)
- 사용자가 4번 클릭으로 *모든 강한 순간* 순회 가능
- 데이터 근거: 시나리오 A의 5 marker는 모두 story_ready bucket의 후보와 1:1 매칭

### 6. 다음에 고쳐야 할 것 1개
> **score-3 cluster (142/146/147)의 시각적 grouping** — timeline marker 위에 *cluster bracket* (예: ⌐⌐⌐) 또는 first-of-cluster marker만 굵게 + 나머지는 thin.

---

## 시나리오 B — Agent-follow browsing

### 1. 성공 여부
**△ 부분 성공**.
- V2-2 panel auto-refresh는 작동 (tick 이동 시 fear/hope/shame 갱신)
- BUT *interesting agent* 클릭 시에만 의미 있음
- 12 agents 중 4명만 dynamic (agent_03/05/08/09), 나머지 8명은 200 ticks 전부 calm/fear=2.42 → 0.0 → 0.0...
- 사용자가 boring agent를 클릭하면 follow 자체가 무의미

### 2. 막히는 지점
**❌ 큰 막힘**: "어느 dot이 dynamic한지" 미리 알리는 표시 부재.
- salient stroke은 *현재 tick* 상태 변화만 알림
- 200 ticks 전체 *trajectory*가 dynamic한 agent를 사전에 식별 불가
- 첫 클릭 확률 67% (8/12)로 boring agent → 사용자 "follow가 별로 안 움직이네" 결론 가능

### 3. text panel 충분성
**△ 부분**.
- Agent panel은 *현재 tick* 단일 값 (fear=10.00, state=fragmenting)
- *시간 변화 trajectory*는 panel에서 볼 수 없음 (사용자가 tick slide하며 panel 변화로 추적)
- V2 plan Tier 3 V2-5 (mini chart)가 이 문제 해결안 — V2 minimal에서는 미구현

### 4. visual 단독 이해도
**△ 부분**.
- dot size (fear) + color (state) + stroke (salient) 변화는 visible
- 하지만 *어떤 agent가 어떤 group에 속하나*는 group_id 보지 않으면 모름
- panel 봐야 정확한 fear 값 알 수 있음

### 5. story candidate 탐색 도움
**△ 약함**.
- agent-driven으로 candidate 발견은 어려움
- candidate panel은 agent와 직접 연결 안 됨 (`agents_involved`만 데이터에 존재, visual에 표시 안 됨)
- 시나리오 B는 *story candidate 탐색*보다 *agent 시간 trajectory 이해*에 가까움

### 6. 다음에 고쳐야 할 것 1개
> **dot에 *trajectory dynamism* hint 추가** — 200 ticks 전체에서 distinct state 수가 많은 agent (예: agent_03/05/08/09)에 영구 "dynamic" badge 또는 별도 색 ring. (이는 export script 단계에서 계산 가능.) 또는 agent panel에 V2-5 mini chart 추가.

---

## 시나리오 C — Candidate-first browsing

### 1. 성공 여부
**✅ 성공**.
- V2-3 filter button 클릭 → 즉시 5개 story_ready만 표시
- V2-4 range overlay가 timeline에 파란 반투명 직사각형으로 즉시 표시
- 5 카드 순회 30초 미만 가능

### 2. 막히는 지점
**△ 1지점**: cluster 안 navigation (C03_t142 vs C05_t147 — 5 tick gap, 같은 signals).
- 두 candidate 사이를 비교하려면 매번 panel scroll → 카드 클릭 → 또 scroll
- "다음 candidate" / "이전 candidate" 버튼 없음
- candidate 카드끼리 keyboard 화살표 navigation 없음

### 3. text panel 충분성
**✅ 충분**.
- candidate 카드 자체에 ID + tick + range + use_mode + lens + related 모두 표시
- World @ tick + Active candidates 같이 보면 candidate의 *맥락* 이해 충분

### 4. visual 단독 이해도
**✅ 강함** (3 시나리오 중 가장 visual 강함).
- range overlay가 timeline에 직접 표시 → "이 candidate는 13-17 범위"가 panel 없이도 인지
- filter button color (story_ready 녹색 / observation_only 노랑 / low_activity_hold 회색)이 곧 candidate 카드의 use_mode 색과 매칭 → 일관

### 5. story candidate 탐색 도움
**✅ 강한 도움** (3 시나리오 중 핵심).
- *시스템이 추천한 후보만* 좁혀서 보기 가능
- Each candidate가 *이미 큐레이션 통과* (Q1-Q4 pipeline) → 탐색 효율 ↑
- 5 카드 클릭 = 5 후보 검토 = 시스템의 핵심 추천 일순

### 6. 다음에 고쳐야 할 것 1개
> **candidate panel에 keyboard navigation** (↓/↑) 또는 panel 상단에 "Prev / Next candidate" 버튼. 카드 list 길어질 때 순회 효율 향상. cluster 안에서 특히 유용.

---

## 4. 종합 검증

### 3 시나리오 합계 점수

| 시나리오 | 성공 | 막힘 | text 충분 | visual 단독 | candidate 탐색 도움 |
|---|:---:|---|:---:|:---:|:---:|
| A. World-first | ✅ | △ 1지점 | ✅ | △ | ✅ 강함 |
| B. Agent-follow | △ 부분 | ❌ 큰 막힘 | △ | △ | △ 약함 |
| C. Candidate-first | ✅ | △ 1지점 | ✅ | ✅ 강함 | ✅ 강함 (핵심) |

### V2 4 features 검증

| Feature | 시나리오 사용 | 검증 |
|---|---|---|
| V2-1 marker noise 완화 | A 진입점 | ✅ score-3 5개 즉시 식별 |
| V2-2 agent follow | B 핵심 | △ 작동하지만 boring agent 비율 67%로 의미 약함 |
| V2-3 candidate filter | C 진입점 | ✅ 5개 story_ready만 보기 즉시 |
| V2-4 range overlay | C visual 핵심 | ✅ tick_range가 timeline에 직접 표시 |

### 시나리오별 핵심 fix 1개씩 (총 3개)

1. **A**: score-3 cluster (142-147)의 visual grouping 표시
2. **B**: agent에 trajectory dynamism hint (4/12 dynamic 식별)
3. **C**: candidate panel keyboard/button navigation

---

## 5. 분기 판단

### Case A vs B vs C 평가

**Case A 조건**: V2가 실제 사용에서 *세계 관찰 + candidate 탐색에 도움이 되는가*?
- 시나리오 A: ✅ (강한 도움)
- 시나리오 B: △ (약함 — boring agent 비율 문제, V2 자체 설계 아닌 anchor 특성)
- 시나리오 C: ✅ (강한 도움 — V2의 핵심 가치)

**Case B 조건**: encoding 보정으로 살아남나?
- color/opacity/size 자체는 V2-1로 이미 보강됨
- 추가 encoding 조정으로 시나리오 B의 boring agent 문제 해결 안 됨 (anchor 특성)
- → Case B는 적합 안 함

**Case C 조건**: visual이 실제 탐색에 약한가?
- 시나리오 A + C에서 강한 도움 확인됨
- → Case C는 적합 안 함

### 결정: **Case A — V2 충분**

근거:
1. 시나리오 A + C가 V2의 핵심 사용 흐름이고 둘 다 강한 도움
2. 시나리오 B의 약점은 *V2 설계 결함*이 아니라 *anchor 자체 특성* (peter_scarcity_baseline에서 12명 중 4명만 dynamic) — 다른 anchor에서는 다를 수 있음
3. V2-3 filter + V2-4 range overlay가 candidate 탐색의 핵심 가치를 검증
4. 3개 핵심 fix가 모두 *추가 polish* 수준 (V3 영역, V2 stop 후 별도 directive 시 검토)

---

## 6. 다음 단계 (Lee §4)

### Case A → Anchor 2 visual validation
- 작성 대상: `docs/visual/ANCHOR_2_VISUAL_VALIDATION_PLAN.md`
- 대상 anchor: accusation canonical run (실제 후보 = `peter_scarcity_triple` — selector library 확인됨, 3 accusations 포함)
- 목표:
  - **scarcity에서 작동한 V2가 event-heavy/accusation 시나리오에서도 작동하는가?**
  - boring agent 비율이 다른가? (시나리오 B 약점 검증)
  - candidate distribution이 다른가? (3-bucket 분포 변화)
  - timeline marker 분포가 다른가? (score-3 cluster 패턴)

---

## 7. 한 줄 요약

> **3 시나리오 검증 결과: A/C 강한 도움, B 약함 (anchor 특성 — 4/12 dynamic). V2 4 features 모두 작동. Case A 판정 → Anchor 2 visual validation 진행 권고. peter_scarcity_triple 추천 (selector library 등록됨).**

---

## 8. 검증 방법론 (HARNESS H4 적용)

### What could still be wrong
- 시나리오는 *정형*만 검증, 실제 사용자가 다른 흐름 (예: 무작위 클릭) 시 V2가 어떻게 작동하는지 미검증
- 5 score-3 marker가 *peter_scarcity_baseline* 한정 — 다른 anchor에서 거의 없을 수도, 너무 많을 수도

### What I did NOT try
- 실제 비-개발자 사용자 테스트 (이번 directive 범위 밖)
- 모바일/태블릿 viewport
- score-1 marker를 fully hide하는 강한 옵션 (V2-1 partial mitigation)
- candidate filter를 OR 대신 AND로 (현재 OR — 모두 ON 시 전부 표시, 일부 OFF 시 일부 숨김)

### Alternate interpretations
- 시나리오 B 약점이 V2 설계 결함이라면 → encoding 추가 조정 필요 (V2-5 mini chart 등)
- 시나리오 B 약점이 anchor 특성이라면 → Anchor 2 검증으로 가설 falsify 가능 → 본 review의 가정

→ Anchor 2 검증이 가설을 falsifying할 *명시적 path* (HARNESS H8 single-seed conditioning과 일관 — 1 anchor 결과를 다른 anchor에서 재확인).

---

**Versioning**: v1 (this review) — 2026-04-30 V2 사용성 검증 완료. Case A 판정.
