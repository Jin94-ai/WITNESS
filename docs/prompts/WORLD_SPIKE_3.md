# WORLD_SPIKE_3.md — Layer 4 factions + Layer 5 rumour graph

> Draft skeleton (2026-04-21). Not yet handed to Claude Code. Review before
> execution; fill in open parameters based on Spike 2 external-LLM review.

## 배경

Spike 1 (세계 자체 동역학) + Spike 2 (Person × World 연결) 완료. 그 결과:

- Calendar / Crowd / Economy / Politics + Sync Layer가 정상 작동
- Agent가 World에 영향 (publicity_shock / authority_threat / rumor_seed 채널)
- World가 Agent에 영향 (EnvironmentState 5 필드 일일 업데이트)

Spike 3 목표: *"종파 세력과 소문이 세계 안의 독립 동역학으로 존재"*.

---

## 절대 규칙 (유지)

1. engine/ public interface 수정 금지 (generic 확장만 허용)
2. content/ 기존 파일 수정 금지
3. 기존 1084 fast tests 전부 green
4. ABSOLUTE RULE #9 (same-tick feedback 금지) 유지 — 새 Layer들은 DAG 자동 검증 통과해야 함

---

## Spike 3 범위

### 3-A: Layer 4 Factions

```python
class FactionLayer:
    """Organised groups with influence, militancy, roman_stance."""
    factions: dict[str, Faction]  # pharisees / sadducees / zealots / jesus_movement / baptist_remnant
```

각 Faction 상태:
- `influence` (0..10) — 사회적 영향력
- `militancy` (0..10) — 무장 성향
- `roman_stance` ∈ {cooperative, neutral, resistant}
- `growth_rate` — 누적 변화율 시간 상수

동역학:
- `influence` ← 느린 decay + rumour_intensity bonus + Roman_alertness drag
- Faction 간 경쟁: 한 Faction influence ↑ → 다른 Faction influence ↓ (zero-sum 단 상한 내에서)
- 예수 운동은 agent Jesus가 등장할 때만 non-zero (Spike 4 예비)

**Brake**: 3일 IIR on rumour intensity + saturation + faction-간 자기억제.

### 3-B: Layer 5 Rumour Graph

```python
class RumorGraph:
    active_rumors: list[Rumor]
    # content, source_agent, spread (0..1), credibility (0..1), age_days
    # 소문은 spread rate per day + decay per day + credibility drift
```

Rumour dynamics:
- 새 rumour seed: Agent → `rumor_seed` channel (Spike 2 aggregation 이미 있음)
- Spread: `spread(t+1) = clamp(spread(t) + crowd_density * 0.05 - 0.02, 0, 1)`
- Credibility: `credibility(t+1) = credibility(t) - 0.02 * (1 - active_feast?)` (시간 지나면 신뢰도 감소)
- Age cap: 30일 넘으면 자동 삭제

**인과 연결**:
- `rumor_seed` from Spike 2 → Rumour 생성
- Rumour `spread` → faction influence bonus
- Rumour `credibility` × `spread` → agent percept의 `heard_rumors` 리스트 (Spike 2 percept 확장)

### 3-C: Jesus as Agent (v1.1 ABSOLUTE RULE #3 변경)

`content/jesus/` 신규 패키지:
- `initial_state.json`: faith_journey state? 또는 새 `divine_authority` domain?
- `behavior_profile.json`: 5-8개 action (teach / heal / rebuke / withdraw / temple_cleanse)
- 정경 말씀은 개역개정 원문 보존 — visible_signal에 scripture reference 포함

**설계 주의**:
- Jesus agent 제거 가능 (Spike 4 counterfactual 지원)
- behavior_profile의 `influence` bias를 일반 Tier 1 Agent보다 크게 (그러나 절대 우위 아님)
- action이 Jesus Movement faction influence 증가 + rumor_seed 강력 emit

---

## 테스트 전략

1. FactionLayer 단위 테스트 (5-6 factions)
2. RumorGraph 단위 테스트 (spread / decay / age)
3. DAG 자동 검증 (Spike 2 A-3 테스트 확장): faction ↔ rumour 순환이 `@prev_tick`으로 표기되는지
4. 통합: IntegratedWorldRunner에 factions + rumours 추가했을 때 기존 Spike 2 integration 6 tests 유지
5. Jesus 제거 counterfactual: 예수 포함 시 vs 제거 시 factions["jesus_movement"].influence 궤적 차이
6. 성공 기준: Passover 전후 rumour count > 3, Jesus movement influence > 1.0 in 90-day run

---

## 자율 진행 규칙

- Phase 3A → 3B → 3C 순서로 실행
- 각 Phase 완료 후 pytest + ruff 검증
- 실패 시 디버그 + 재시도 (최대 3번), 4번째 fail은 설계 재검토
- 완료 후 보고: 생성 파일, 테스트 결과, 리뷰 조건 대응, Spike 4 진입 가능 여부

---

## 관련 외부 리뷰

[../world/SPIKE_1_REVIEW.md](../world/SPIKE_1_REVIEW.md) Q1 (같은 tick 안 feedback), Q2 (overflow), Q6 (percept cadence), Q7 (Jesus dominance) 중 Spike 2에서 Q2/Q1 해결 완료. Spike 3에서 Q6, Q7 해결.

---

**이 문서는 draft.** 실제 실행 전에:
- Gemini / ChatGPT 에 review 받을 것 (SPIKE_2 결과 + 이 draft 동시 제공)
- Faction growth 방정식과 rumour decay 상수를 현실적 값으로 조정
- Jesus agent의 action 5-8개를 정확한 정경 인용으로 설계
