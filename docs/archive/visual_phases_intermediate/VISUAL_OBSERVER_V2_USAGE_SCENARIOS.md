# Visual Observer V2 — 실제 사용 시나리오 3개

**Date**: 2026-04-30
**Source**: Lee directive (V2 사용 검증, 코드 수정 금지)
**Target**: `visual/dot_observer_replay.html` (V2 minimal 적용판)
**Anchor**: `peter_scarcity_baseline` seed=0 200 ticks
**용도**: V2가 *기능 모음*이 아니라 *세계 관찰 + candidate 탐색 도구*로 작동하는지 검증할 정형 시나리오 정의.

---

## 0. 시나리오 사용 전제

각 시나리오는 동일한 시작점:
1. `python scripts/visual/export_dot_observer_data.py` (data/visual/dot_observer_data.json 생성)
2. `python -m http.server 8000`
3. 브라우저에서 `http://localhost:8000/visual/dot_observer_replay.html`
4. 화면: SVG 도트 + timeline-bar + 5 panel (World @ tick 0, Salience tags, Active candidates, Agent — hidden, All curated candidates with filter row)

**현재 데이터 statistics**:
- 197 salience marks (score-1: 145개 / score-2: 47개 / score-3: 5개)
- 8 curated candidates (5 story_ready + 0 observation_only + 3 low_activity_hold)
- 12 agents 중 4명만 dynamic (agent_03/05/08/09) — 나머지 8명은 200 ticks 내내 `calm` 단일 state

---

## 시나리오 A — World-first browsing (top-down)

> *"세계가 어디서 흔들렸나?"*

### 흐름
1. **시작**: tick 0 표시. 도트 12개 모두 회색(calm), zone 모두 light-gray(low_activity).
2. **timeline-bar 살피기**: 200 ticks 가로 띠. score-1 yellow(opacity 0.18 — 거의 안 보임) / score-2 orange(0.7) / score-3 red(width 3px, opacity 1.0).
3. **score-3 marker 찾기**: 5개 빨간 굵은 marker가 즉시 식별.
   - 위치: tick 15, 25, 142, 146, 147 (앞쪽 클러스터 1 + 뒤쪽 클러스터 1)
4. **첫 번째 marker (tick 15) 클릭** → tick jump.
5. **검토 사항 (4 panel 순회)**:
   - **World @ tick 15**: mood=tense, blame_concentration=0.32, suspicion=0.20+, vigilance=0.45+
   - **Salience tags**: `authority_vigilance_spike`, `cohort_split`, `agent_state_shift`
   - **Active candidates**: `C01_t15` 카드 (story_ready / lens=person)
   - **(canvas)**: L1 zone 색이 partial / saturation으로 변함. 일부 dot이 주황/빨강.
6. **다음 marker로 이동**: timeline-bar의 다음 score-3 클릭 → tick 25, 142, ... 순회.
7. **결과**: "어디가 강한 신호인가"를 visual 한 곳에서 확인 + 각 위치의 *왜* 를 5 panel로 이해.

### 기대 효과
- score-1 noise가 V2-1로 가라앉아 score-3가 timeline에서 *튀어나옴*
- 5 score-3 → 5 candidate (정확히 매칭) → 사용자가 *4번 클릭으로 모든 강한 순간* 순회 가능
- World panel + Salience + Active candidates 3 panel이 같은 tick의 *세 측면* 동시 표시

### 핵심 V2 기능
- **V2-1 marker noise 완화** (이 시나리오의 진입점 자체가 score-3 marker 식별)
- 기존 K1 timeline-bar click + K6 candidate-jump

### 시나리오 막힐 수 있는 지점
- score-3 5개가 *클러스터링*되어 있음 (15-25 / 142-147). 사용자가 142, 146, 147을 *서로 다른 사건*으로 오해할 수 있음 → near-duplicate 표시 필요할까?
- (이미 Active candidates panel에서 `+1 related`, `+2 related` 표시되지만 visual marker 자체는 같아 보임)

---

## 시나리오 B — Agent-follow browsing (bottom-up)

> *"한 사람의 시간이 어떻게 흘렀나?"*

### 흐름
1. **시작**: tick 0. 도트 12개 표시.
2. **agent 후보 식별**: V1 review §1 Q3에서 발견된 약점 — 12 agents 중 4명만 *dynamic* (03/05/08/09). 사용자가 dot 위치만 보고는 어느 게 dynamic인지 불명.
3. **추측으로 클릭**: tick 15 위치로 이동 후 (시나리오 A의 첫 marker), 검은 stroke(salient)이 있는 dot 클릭.
   - 데이터 기준 tick 15 시점에 `agent.delta` 있는 agent들이 salient mark됨 → V1 schema 따라.
4. **agent 클릭** (예: `agent_03` — dynamic 후보 중 1):
   - Selected agent panel 표시: `agent_03 (group L1) · follow @ tick 15`, state=fragmenting, fear=10.00, hope=2.x, shame_self=4.x.
5. **tick slider 또는 play**:
   - V2-2 덕에 panel content가 tick 이동마다 자동 갱신.
   - tick 0: fear=2.42, state=calm
   - tick 18: fear=10.00, state=fragmenting (peak)
   - tick 50+: fear=다시 낮아지고 state 변화
   - tick 200: 끝
6. **결과**: 한 agent의 *시간 trajectory*를 panel 갱신으로 추적.

### 기대 효과
- V2-2가 V1의 stale panel 문제를 해결 → tick 이동마다 follow agent 상태 갱신
- 같은 agent를 *시간 축으로* 봄 → 1 agent 200 ticks 단편 200개 합쳐 한 줄거리

### 핵심 V2 기능
- **V2-2 selected agent follow** (이 시나리오의 핵심)
- 기존 K1 dot click + K5 agent panel

### 시나리오 막힐 수 있는 지점
- **(가장 큰 문제)**: 12 agents 중 8명이 *boring follow target* (200 ticks 내내 calm, fear=2.42→0.0→0.0...). 사용자가 처음 클릭한 agent가 boring agent일 확률 67%.
- 시각적 hint 부재: "어느 dot이 dynamic한지" 미리 알리는 표시가 없음. salient stroke은 *현재 tick* 변화만 알림 — *전체 trajectory dynamic*은 별개.
- agent panel은 *현재 tick* 단일 값 — *시간 변화 trajectory*를 한눈에 보기 어려움 (V2 plan Tier 3 V2-5 mini chart가 이 문제 해결안).

---

## 시나리오 C — Candidate-first browsing (filter)

> *"시스템이 추천한 후보만 빠르게 순회"*

### 흐름
1. **시작**: All curated candidates panel에 8개 카드. Filter row 3 button (story_ready 5 / observation_only 0 / low_activity_hold 3) 모두 active.
2. **filter 좁히기**: `observation_only` button 클릭 → 비활성. `low_activity_hold` button 클릭 → 비활성.
3. **결과**: story_ready 5개만 panel에 남음.
   - C01_t15 (range 13-17, lens=person)
   - C02_t25 (range 23-27, lens=person)
   - P03_t66_agent_08 (range 64-68, lens=person, +2 related)
   - C03_t142 (range 140-144, lens=person)
   - C05_t147 (range 145-149, lens=person, +1 related)
4. **첫 카드 클릭 (C01_t15)**: tick 15로 jump + range overlay (timeline-bar에 13-17 파란 반투명).
5. **검토 사항**:
   - **(canvas)**: tick 15 시점 도트 상태 — L1 zone에 변화 있음
   - **World @ tick 15**: 시나리오 A와 동일
   - **Active candidates**: C01_t15 카드 (선택됨 — 파란 테두리)
   - **timeline-bar**: tick 15 black cursor + range 13-17 파란 overlay
6. **다음 카드 클릭 (C02_t25)**:
   - tick 25 jump + range 23-27 새 overlay (이전 overlay 사라짐)
7. **순회 진행**: 5개 카드 모두 클릭 → 5 candidate 모두 빠르게 검토.

### 기대 효과
- V2-3 filter가 *bucket 분리* 가능 → 사용자가 "시스템이 가장 확신하는 5개만"으로 좁힘
- V2-4 range overlay가 *candidate가 단일 시점이 아닌 구간*임을 visualize → 13-17 범위에 무엇이 있나
- 5 카드 클릭 시간 ≤ 30초 (timeline jump 즉시)

### 핵심 V2 기능
- **V2-3 candidate filter** (시나리오 진입)
- **V2-4 range overlay** (시나리오의 핵심 visual hint)
- 기존 K6 candidate click → jump

### 시나리오 막힐 수 있는 지점
- 5 카드 중 4개가 cluster (142-147)에 있어 *range overlay*가 인접하게 겹침 (140-144 / 145-149는 단지 1 tick 차이) → 시각적 구분 어려움
- "다음 candidate" / "이전 candidate" navigation 버튼 없음 → 매번 panel scroll/click 필요. cluster 안에서 빠른 순회 시 답답.
- C03_t142와 C05_t147은 *3-tick gap*만 있고 둘 다 같은 lens (person), 같은 signals — 사용자가 "둘이 정말 다른가?" 의문 가능 (+1 related로 표시되지만 visual은 같아 보임).

---

## 4. 3 시나리오 종합

| 시나리오 | 진입 | 핵심 V2 기능 | 핵심 약점 |
|---|---|---|---|
| A. World-first | timeline score-3 marker | V2-1 noise 완화 | score-3 cluster (142-147)의 visual 구분 약함 |
| B. Agent-follow | dot click | V2-2 follow + auto-refresh | dynamic agent 식별 hint 부재 (8/12 boring) |
| C. Candidate-first | filter + card click | V2-3 filter + V2-4 range overlay | next/prev navigation 부재 |

### 공통 패턴
- **3 시나리오 모두 *4 panel 동시 표시*에 의존**: World + Salience + Active + (Agent or All curated). 한 개 panel만 보고는 candidate의 의미 파악 어려움.
- **3 시나리오 모두 timeline-bar가 핵심 navigation tool**: marker / cursor / range overlay 모두 timeline-bar 위에 layer됨.
- **3 시나리오 모두 *visual + text complementary*** (Lee directive §9 verbatim): visual = 어디로 갈지 안내, text = 왜 중요한지 설명.

---

## 5. 시나리오별 검증 질문 (다음 doc에서 답변)

각 시나리오마다:
1. *성공 여부*: 의도한 흐름이 막힘 없이 진행되는가?
2. *막히는 지점*: 사용자가 "다음에 뭘 해야 하지?" 멈추는 지점이 있는가?
3. *text panel 충분성*: 4 panel 정보로 candidate 의미 이해 가능한가?
4. *visual 단독 이해*: panel 안 보고 visual만으로 어디까지 이해 가능한가?
5. *story candidate 탐색 도움*: 결과적으로 *story 후보*로 이어질 가치 있는 후보를 식별 가능한가?
6. *다음에 고쳐야 할 것 1개만*: focus.

---

## 6. 한 줄 요약

> **3 시나리오 = (A) timeline-driven world-first / (B) dot-driven agent-follow / (C) filter-driven candidate-first. 각 시나리오가 V2의 4 features (marker noise + agent follow + filter + range overlay) 중 다른 조합을 사용. 다음 doc에서 시나리오별 막힘/도움 정량 검증.**

---

**Versioning**: v1 (this doc) — 2026-04-30 V2 사용 시나리오 정형화.
