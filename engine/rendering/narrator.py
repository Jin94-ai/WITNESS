"""기초 내러티브 렌더러.

시뮬레이션 결과를 사람이 읽을 수 있는 내러티브 텍스트로 변환한다.
비전 A(내러티브 체험)의 기초 인프라.

원칙: LLM이 이 텍스트를 생성하지 않는다. 템플릿 기반으로 구조화된 텍스트를 생성.
"""

from __future__ import annotations

from engine.simulation.explanation import generate_explanation
from engine.simulation.world import MultiAgentResult


def _append_scripture_section(
    sections: list[str],
    result: MultiAgentResult,
    scripture_dir: str = "content/shared/scripture",
) -> None:
    """정경 말씀이 있으면 섹션에 추가한다."""
    from pathlib import Path

    from engine.rendering.scripture import load_scripture

    # config에서 interventions의 scripture_ref를 찾을 수 없으므로
    # 기본 디렉토리에서 시도
    sd = Path(scripture_dir)
    if not sd.exists():
        return

    # "요 21:15-17" -- 회복의 말씀 (가장 중요한 정경 개입)
    try:
        text = load_scripture("요 21:15-17", sd)
        if text:
            sections.append("[Scripture -- 요 21:15-17]")
            for line in text.split("\n"):
                sections.append(f"  {line}")
            sections.append("")
    except (ValueError, FileNotFoundError):
        pass


def render_narrative(result: MultiAgentResult, agent_id: str = "") -> str:
    """특정 에이전트의 관점에서 시뮬레이션 내러티브를 생성한다.

    Args:
        result: 다중 에이전트 시뮬레이션 결과
        agent_id: 관점 에이전트 ID. 빈 문자열이면 첫 번째 에이전트.

    Returns:
        구조화된 내러티브 텍스트
    """
    if not agent_id and result.final_states:
        agent_id = next(iter(result.final_states))
    card = generate_explanation(result)
    causal_chain = card["causal_chain"]

    sections: list[str] = []

    # 제목
    sections.append(f"--- Narrative: {agent_id} (seed={result.seed}) ---")
    sections.append("")

    # 프롤로그: 초기 상태
    if agent_id in result.final_states:
        initial_snaps = result.state_snapshots.get(agent_id, {})
        if 0 in initial_snaps:
            s0 = initial_snaps[0]
            sections.append("[Prologue]")
            sections.append(
                f"  Fear: {s0.emotions.fear:.1f}, Hope: {s0.emotions.hope:.1f}, "
                f"Love: {s0.emotions.love:.1f}"
            )
            sections.append("")

    # 주요 행동 시퀀스
    history = result.action_histories.get(agent_id, [])
    if history:
        sections.append("[Actions]")
        # 행동 전환점 추출 (이전과 다른 행동이 나온 시점)
        prev_action = None
        transitions = []
        for a in history:
            if a.chosen_action != prev_action:
                transitions.append((a.tick, a.chosen_action, a.event_id))
                prev_action = a.chosen_action

        for tick, action, event in transitions[:15]:  # 최대 15개 전환점
            source = f"({event})" if event != "voluntary" else ""
            sections.append(f"  tick {tick:>4}: {action} {source}")
        sections.append("")

    # 핵심 이벤트
    if causal_chain:
        sections.append("[Key Moments]")
        for step in causal_chain:
            sections.append(f"  tick {step['tick']:>4}: {step['event']}")
        sections.append("")

    # 정경 말씀 (scripture_ref가 있는 intervention이 있으면)
    _append_scripture_section(sections, result)

    # 에필로그: 최종 상태
    if agent_id in result.final_states:
        final = result.final_states[agent_id]
        sections.append("[Epilogue]")
        sections.append(
            f"  Fear: {final.emotions.fear:.1f}, Hope: {final.emotions.hope:.1f}, "
            f"Grief: {final.emotions.grief:.1f}"
        )
        sections.append(
            f"  Moral injury: {final.slow_state.moral_injury:.1f}, "
            f"Identity: {final.slow_state.identity_shift:.1f}"
        )
        sections.append("")

    # 결과
    sections.append(f"[Outcome] {card['outcome_summary']}")

    return "\n".join(sections)


def render_ensemble_summary(
    results: list[MultiAgentResult],
    agent_id: str = "",
) -> str:
    """앙상블 결과의 내러티브 요약을 생성한다.

    Args:
        results: 다중 에이전트 시뮬레이션 결과 목록
        agent_id: 관점 에이전트 ID

    Returns:
        앙상블 요약 텍스트
    """
    import statistics
    from collections import Counter

    n = len(results)
    if n == 0:
        return "No results to summarize."

    if not agent_id and results[0].final_states:
        agent_id = next(iter(results[0].final_states))

    # 에이전트 행동 분포
    action_counts: Counter[str] = Counter()
    for r in results:
        for a in r.action_histories.get(agent_id, []):
            action_counts[a.chosen_action] += 1

    total_actions = sum(action_counts.values())

    # 최종 상태 통계
    fears = [r.final_states[agent_id].emotions.fear for r in results if agent_id in r.final_states]
    hopes = [r.final_states[agent_id].emotions.hope for r in results if agent_id in r.final_states]
    injuries = [r.final_states[agent_id].slow_state.moral_injury for r in results if agent_id in r.final_states]

    lines = [
        f"--- Ensemble Summary: {agent_id} ({n} runs) ---",
        "",
        "[Action Distribution]",
    ]

    for action, count in action_counts.most_common(10):
        pct = count / total_actions if total_actions > 0 else 0
        lines.append(f"  {action:>25}: {count:>5} ({pct:.1%})")

    lines.append("")
    lines.append("[Final State Statistics]")
    def _fmt(values: list[float], label: str) -> str:
        m = statistics.mean(values)
        s = statistics.stdev(values) if len(values) > 1 else 0
        return f"  {label}: {m:.1f} +/- {s:.1f}"

    if fears:
        lines.append(_fmt(fears, "Fear"))
    if hopes:
        lines.append(_fmt(hopes, "Hope"))
    if injuries:
        lines.append(_fmt(injuries, "Moral injury"))

    return "\n".join(lines)
