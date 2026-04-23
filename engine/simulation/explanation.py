"""Run Explanation Card.

개별 시뮬레이션 결과를 사람이 읽을 수 있는 인과 요약으로 변환한다.
"왜 이 경로가 나왔는가?"에 대한 구조화된 답변.

비전 A(내러티브 체험)의 전 단계 -- 분석 해석 레이어.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from engine.simulation.world import MultiAgentResult


def generate_explanation(result: MultiAgentResult) -> dict[str, Any]:
    """MultiAgentResult에서 인과 요약 카드를 생성한다.

    Returns:
        {
            "seed": int,
            "agents": {agent_id: {...agent summary...}},
            "key_events": [...],
            "causal_chain": [...],
            "outcome_summary": str,
        }
    """
    # 에이전트별 행동 요약
    agents: dict[str, dict[str, Any]] = {}
    for aid, history in result.action_histories.items():
        action_counts = Counter(a.chosen_action for a in history)
        top_action = action_counts.most_common(1)[0][0] if action_counts else "none"
        agents[aid] = {
            "total_actions": len(history),
            "action_distribution": dict(action_counts.most_common()),
            "dominant_action": top_action,
        }

    # 핵심 이벤트 타임라인
    key_events: list[dict[str, Any]] = []

    # 트리거 이벤트
    for t in result.fired_triggers:
        key_events.append({
            "tick": t["tick"],
            "type": "trigger",
            "id": t["trigger_id"],
        })

    # Hazard 이벤트
    for e in result.fired_events:
        key_events.append({
            "tick": e["tick"],
            "type": "hazard",
            "id": e["event_id"],
        })

    key_events.sort(key=lambda x: x["tick"])

    # 인과 체인 추출
    causal_chain = _extract_causal_chain(result)

    # 결과 요약
    outcome = _summarize_outcome(result, key_events)

    return {
        "seed": result.seed,
        "agents": agents,
        "key_events": key_events,
        "causal_chain": causal_chain,
        "outcome_summary": outcome,
    }


def _extract_causal_chain(result: MultiAgentResult) -> list[dict[str, Any]]:
    """인과 체인을 추출한다. 인물 비종속: 트리거 + 희귀 행동 기반.

    포함 대상:
    1. 발동된 트리거 (시스템 이벤트, 발생 순서)
    2. 에이전트별 첫 번째 "희귀 행동" (해당 에이전트의 전체 행동 중 하위 30% 미만 빈도)
       - 희귀 행동 = 결과에 기여한 개별적 선택 (예: judas의 betray, gauguin의 depart)
    """
    from collections import Counter

    chain: list[dict[str, Any]] = []

    # 트리거 이벤트
    seen_triggers: set[str] = set()
    for t in result.fired_triggers:
        tid = t["trigger_id"]
        if tid not in seen_triggers:
            chain.append({"tick": t["tick"], "event": tid, "agent": "system"})
            seen_triggers.add(tid)

    # 에이전트별 희귀 행동: 행동 분포에서 평균 빈도의 50% 미만인 것
    for aid, history in result.action_histories.items():
        if not history:
            continue
        action_counts = Counter(a.chosen_action for a in history)
        if len(action_counts) < 2:
            continue
        total = sum(action_counts.values())
        mean_freq = total / len(action_counts)
        threshold = mean_freq * 0.5
        rare_actions = {
            action for action, count in action_counts.items() if count < threshold
        }
        # 첫 번째 희귀 행동
        for a in history:
            if a.chosen_action in rare_actions:
                chain.append({
                    "tick": a.tick,
                    "event": f"{aid}_{a.chosen_action}",
                    "agent": aid,
                })
                break

    chain.sort(key=lambda x: x["tick"])
    return chain


def _summarize_outcome(result: MultiAgentResult, key_events: list[dict]) -> str:
    """결과를 한 문장으로 요약한다. 인물 비종속."""
    trigger_ids = [e["id"] for e in key_events if e["type"] == "trigger"]

    if not trigger_ids:
        return "Simulation completed without trigger events."

    # 첫 번째 트리거를 핵심 이벤트로 사용
    first_trigger_id = trigger_ids[0]
    first_tick = next(e["tick"] for e in key_events if e["id"] == first_trigger_id)

    # 에이전트별 총 행동 수 요약
    agent_summaries = []
    for aid, history in result.action_histories.items():
        n = len(history)
        if n > 0:
            agent_summaries.append(f"{aid}({n})")

    agents_str = ", ".join(agent_summaries[:4])
    return (
        f"Trigger '{first_trigger_id}' at tick {first_tick}. "
        f"Agents: {agents_str}. "
        f"{len(result.fired_triggers)} triggers, {len(result.fired_events)} hazard events."
    )


def format_explanation_text(card: dict[str, Any]) -> str:
    """설명 카드를 사람이 읽을 수 있는 텍스트로 포맷한다."""
    lines = [
        f"=== Run Explanation (seed={card['seed']}) ===",
        "",
        f"Outcome: {card['outcome_summary']}",
        "",
        "-- Agent Summary --",
    ]

    for aid, info in card["agents"].items():
        top3 = list(info["action_distribution"].items())[:3]
        top3_str = ", ".join(f"{a}({c})" for a, c in top3)
        lines.append(f"  {aid}: {info['total_actions']} actions. Top: {top3_str}")

    if card["causal_chain"]:
        lines.append("")
        lines.append("-- Causal Chain --")
        for step in card["causal_chain"]:
            lines.append(f"  tick {step['tick']:>4}: [{step['agent']}] {step['event']}")

    if card["key_events"]:
        lines.append("")
        lines.append(f"-- Key Events ({len(card['key_events'])} total) --")
        for e in card["key_events"][:10]:  # 최대 10개
            lines.append(f"  tick {e['tick']:>4}: [{e['type']}] {e['id']}")

    return "\n".join(lines)
