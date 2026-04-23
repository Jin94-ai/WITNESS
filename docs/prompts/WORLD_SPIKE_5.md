# WORLD_SPIKE_5.md — Jesus Agent + "remove_jesus_movement" experiment

> Draft (2026-04-22, end of Spike 4 autonomous session).
> Target session: after external LLM review of SPIKE_1/2/3/4_REVIEW.md.
> This prompt assumes the reviewer did NOT veto Jesus-as-agent under the
> v1.1 amendment to ABSOLUTE RULE #3. If they did, pivot to §3 alternate.

---

## §0. Background

Spike 1→4 complete and external-review-ready. Key context:

- 6-layer World Engine (calendar / crowd / economy / politics / rumours /
  factions) + Person×World Sync Layer + variable-intervention framework
- `InterventionSpec` primitives already include `agent_remove` —
  "remove Jesus" would be one line once a Jesus Agent exists
- ABSOLUTE RULE #3 v1.1 (WORLD_DESIGN_v1.1_amendments §1.1): Jesus
  may be implemented as Agent, but:
  1. 정경 말씀은 개역개정 본문 그대로 (scripture verbatim)
  2. 예수의 내면을 "신성의 시뮬레이션"으로 과대 해석하지 않는다
  3. influence bias를 일반 Tier 1 Agent보다 크게 허용, 그러나 절대 우위 아님

Spike 4 SPIKE_4_REVIEW.md Q7 asked the reviewer to choose between
(a) `content/jesus/` (this prompt) and (b) second world
(`arles_1888`, §3 alternate below). Default assumption: (a).

---

## §1. Absolute rules (carry forward)

1. engine/ public interface 수정 금지
2. 기존 content/ 파일 수정 금지 (jesus/ 는 신규)
3. 정경 말씀 verbatim 보존 (개역개정) — Jesus Agent의 모든 visible_signal 에 scripture reference
4. Jesus Agent의 interior state를 신성 시뮬레이션으로 해석하지 말 것 — 단지 relational influence scalar
5. Jesus Agent는 Tier 1 agent의 influence cap을 넘지 않음 (saturation 가드레일)
6. 기존 1137 fast tests + 4 review packets의 주장 유지
7. ABSOLUTE RULE #9 (same-tick feedback 금지) 유지

---

## §2. Spike 5 scope

### 5-A: content/jesus/ skeleton

```
content/jesus/
├── initial_state.json          # agent_id="jesus", faith_journey domain state
├── behavior_profile.json       # 5-7 actions, each cite scripture
└── README.md                   # 신학적 가드레일 + reviewer quote
```

- `initial_state.json`: `agent_id = "jesus"`, domain_state = **faith_journey** (재사용, 별도 도메인 만들지 않음 — 예수의 identity는 영적 여정이 아니라 시뮬레이션 관점에서 특별한 agent이므로 단순 reuse + 초기값으로 차별화). 초기 `jesus_understanding = "son_of_god"` (starting commitment).

- `behavior_profile.json`: 5-7 action. 모든 action의 `visible_signal`은 개역개정 인용 포함. 예:
  - `teach` (publicly visible, observable_from=[], visible_signal 포함 Matt 5:3 인용)
  - `heal` (visible, observable_from=[])
  - `rebuke` (visible, 특정 faction threat_perception 증가 trigger)
  - `temple_cleanse` (rare action, publicity_shock max)
  - `withdraw_to_pray` (invisible, no visible_signal)
  - `proclaim_kingdom` (visible, rumour_seed 강하게 emit)

- 핵심 주의: action_id 중 `cleanse`, `teach`, `proclaim` 은 기존 rumour-keyword 매칭 (Spike 3 Phase 3C loop #14 bug fix 후)과 자동 매치 → Jesus가 자연스럽게 rumour 생성자.

### 5-B: content/worlds/jerusalem_ad30/ 변경

- `factions_config.factions.jesus_movement.target_influence`: 현재 3.0 → Jesus Agent 존재 시 자동으로 더 높이는 메커니즘 필요:
  - 옵션 1: JSON에 `jesus_movement_target_when_jesus_present` 추가 (engine 확장 필요)
  - 옵션 2: Jesus Agent의 action이 직접 jesus_movement faction influence를 증가 (agent → world WorldEffect에 신규 channel `faction_influence_boost` 추가)
  
  **권장 옵션 2**: primitive 기반, Phase 3D architecture 재사용.

### 5-C: content/interventions/remove_jesus_movement.json

이미 framework 있음. agent_remove + faction_remove 복합:

```json
{
  "intervention_id": "remove_jesus_movement",
  "description": "예수 Agent + jesus_movement faction 모두 제거. 세계 역사에서 예수 운동이 존재하지 않았다면?",
  "agent_remove": ["jesus"],
  "faction_remove": ["jesus_movement"]
}
```

그러나 이걸 검증하려면 먼저 Jesus Agent가 실제로 jesus_movement에 영향을 주는 체인을 구축해야.

### 5-D: Sync Layer 확장 — `faction_influence_boost` channel

기존 WorldEffect channel: `publicity_shock`, `authority_threat`, `rumor_seed`.  
신규: `faction_influence_boost` (target_faction별 SUM, per world day).

- `SyncLayer.actions_to_effects`: Jesus Agent의 `proclaim_kingdom` action → emit `{channel_id: "faction_influence_boost", value: 1.0, target_faction: "jesus_movement"}` (channel이 target을 필드로 가져야 해서 WorldEffect 구조 변경 필요).
  - 또는 simpler: channel_id를 `"faction_influence_jesus_movement"` 같은 per-faction으로 분리.
- FactionLayer.tick: `ctx.aggregated_effects.get("faction_influence_jesus_movement", 0.0)` 를 jesus_movement influence drift에 더함.

**주의**: 이 새 cross-layer edge는 Phase 3D와 같은 방식 (same-tick, threshold/saturation brake). DAG 자동 검증 유지.

### 5-E: 통합 실험 실행

```bash
# Before 5-E (null jesus test): Jesus Agent 없을 때 jesus_movement baseline
python scripts/demo_spike4_interventions.py --intervention remove_judas  # 기존 재검증

# With Jesus Agent:
# 1. Control arm = Jesus 포함 4 agents (peter, judas, caiaphas, crowd, jesus)
# 2. remove_jesus_movement: Jesus Agent + jesus_movement faction 모두 제거
# 3. Expected: 
#    - Full: jesus_movement 훨씬 높은 final influence (예: 8-9)
#    - remove: 0 (faction 자체가 없음)
#    - Peter fear trajectory 다를 것 (Jesus가 제공하는 hope source 제거)

# 측정: peter fear, peter hope, rumours, pharisees/zealots response
```

---

## §3. Alternate — `content/worlds/arles_1888/` (if §2 blocked)

두 번째 world pack, Van Gogh scenario.

- content/worlds/arles_1888/world_config.json — 프랑스 지방 도시 AD 1888
- Layer 1 calendar: Gregorian, 별도 feast system 없음, 기후 변동 (mistral)
- Layer 2 economy: 그림 판매 / 물감 가격 / 후원자 지불
- Layer 3 politics: 시장 권위 / mental asylum 관련 제도
- Layer 4 factions: 인상주의 / 후기인상주의 / 파리 아카데미
- Layer 5 crowd: 지방 도시 관광객 파동 (여름 peak)
- Agent: vangogh (기존 content 재사용), gauguin (기존)

SPIKE_4_REVIEW.md Q7 "engine universality" — arles_1888가 AD-30 world
와 완전히 다른 layer parameter로 같은 엔진에서 돌면 **v2.0 engine universality** claim 가능.

---

## §4. 테스트 전략

1. **Jesus Agent contents 단위 테스트**: `test_content_pack_structure.py`가 `jesus/` 에 initial_state + behavior_profile 찾고 schema 통과.
2. **정경 보존 테스트**: Jesus behavior_profile의 모든 visible_signal 에 개역개정 인용 포함 (string match "개역개정" 또는 scripture book:chapter reference).
3. **influence ceiling guardrail**: Jesus agent의 어떤 weight * baseline도 10 (Tier 1 agent cap) 초과 불가.
4. **faction_influence_boost 채널 작동 테스트**: Jesus의 proclaim 4회 → jesus_movement target_influence_mean 증가 pin.
5. **remove_jesus_movement 실험**: BatchRunner로 control (Jesus 포함) vs remove arm 실행 → jesus_movement influence Δ >= 80% 감소 + peter hope trajectory 다름.

예상 신규 test 10-15개.

---

## §5. 성공 기준

1. content/jesus/ 5-7 action behavior_profile 로드 성공
2. 모든 Jesus action visible_signal이 개역개정 인용 포함 (test_canonical_preservation)
3. Jesus Agent 포함 통합 시뮬레이션 90일 완주, rumour seed 대폭 증가 (기존 77 → 150+)
4. jesus_movement final influence 현재 9.9 → Jesus Agent 추가 시 훨씬 낮아지지 말 것 (신규 agent가 기존 growth 대체하는지 검증)
5. remove_jesus_movement counterfactual: jesus_movement 8-9 → 0, Peter hope Δ measurable, Cohen's d > 1.0 on hope
6. 기존 1137 tests green 유지
7. 4번째 external review packet (SPIKE_5_REVIEW.md) 준비

---

## §6. 하지 않을 것

- LLM 기반 설교 생성 (정경 verbatim만)
- Jesus의 "내면 상태" 분석 (단순 influence scalar)
- 예수 신성 시뮬레이션 (cap 10 강제)
- 무제한 influence 성장 메커니즘
- 기존 content 수정 (shared/scripture/ 는 readonly 참조만)

---

## §7. 자율 진행 규칙

- Phase 5A → 5B → 5C → 5D → 5E 순서
- 각 단계 pytest + ruff 검증
- 정경 인용 검증은 별도 test file (`test_canonical_preservation_jesus.py`)
- 실패 시 3회 재시도
- 완료 후 SPIKE_5_REVIEW.md 패킷 자동 작성

---

**이 문서는 draft.** 실제 실행 전에:
- 외부 LLM 4번째 review (SPIKE_4_REVIEW.md Q7 응답) 필요
- content/jesus/behavior_profile.json 의 5-7 action + 정확한 정경 인용은 사용자 신학 감수 필요
- Q7에서 arles_1888 선택 시 본 문서 §3 alternate 확장
