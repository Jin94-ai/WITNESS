"""Trace → Narrative 번역기 (v2.0 Narrative Witness Layer preview).

PlayerView가 필터링한 TraceEvent 스트림을 chronological narrative 텍스트로 변환.
v2.0 렌더러가 교체할 자리 — 현재는 템플릿 기반 basic 렌더.

원칙 (TRACE_SCHEMA.md §3):
- visible_signal이 있으면 그대로 사용
- 없으면 generic fallback (agent + action verb)
- bifurcation_point는 긴장 강조
- canonical_match는 서사 앵커
- LLM 미사용 (ABSOLUTE RULE #4)
"""

from __future__ import annotations

from typing import Any

from engine.rendering.player_view import PlayerViewFilterConfig, filter_for_player
from engine.rendering.trace_emitter import TraceEvent, collect_trace_events


def _signal_for_action(payload: dict) -> str:
    """Action entry → 한 줄 서술.

    visible_signal 우선, 없으면 "agent가 action" generic.
    """
    vs = payload.get("visible_signal")
    if vs:
        return str(vs)
    agent = payload.get("agent", "?")
    action = payload.get("action", "?")
    return f"{agent}가 {action}을(를) 수행했다."


def _signal_for_trigger(payload: dict) -> str:
    trigger_id = payload.get("trigger_id") or payload.get("event_template_id") or "event"
    return f"[{trigger_id}] 사건이 발생했다."


def _signal_for_bifurcation(payload: dict) -> str:
    window = payload.get("decision_window") or [0, 0]
    return (
        f"*** 분기점: tick {window[0]}~{window[1]} 구간에서 경로가 갈라지기 시작한다. ***"
    )


def _signal_for_belief(payload: dict) -> str:
    observer = payload.get("observer", "?")
    target = payload.get("target", "?")
    trigger = payload.get("trigger", "")
    return f"{observer}의 {target}에 대한 인식이 변했다. ({trigger})"


def _signal_for_canonical(payload: dict) -> str:
    cid = payload.get("checkpoint_id", "?")
    passed = payload.get("passed", False)
    mark = "일치" if passed else "불일치"
    return f"[정경 체크] {cid}: {mark}"


_DISPATCH = {
    "action_taken": _signal_for_action,
    "trigger_fired": _signal_for_trigger,
    "bifurcation_point": _signal_for_bifurcation,
    "belief_update": _signal_for_belief,
    "canonical_match": _signal_for_canonical,
}


def render_event_line(event: TraceEvent) -> str:
    """단일 TraceEvent → `[tick NNN] <서술>` 한 줄."""
    fn = _DISPATCH.get(event.type)
    if fn is None:
        return f"[tick {event.tick:>4}] ({event.type})"
    return f"[tick {event.tick:>4}] {fn(event.payload)}"


def narrate_result(
    result: Any,
    player_id: str,
    *,
    skip_repeats: bool = True,
    bifurcation_reports: list[Any] | None = None,
    belief_updates: list[dict] | None = None,
) -> str:
    """One-call helper: SimulationResult → player-view narrative.

    collect_trace_events → filter_for_player → render_trace_timeline 단축.

    Args:
        result: SimulationResult (또는 MultiAgentResult 호환 객체).
        player_id: 시점 agent ID.
        skip_repeats: 같은 agent의 연속 같은 action 묶기.
        bifurcation_reports: (옵션) detect_bifurcation() 결과.
        belief_updates: (옵션) v1.1 belief update dicts.

    Returns:
        Player-perspective narrative 텍스트.
    """
    events = collect_trace_events(
        result,
        bifurcation_reports=bifurcation_reports,
        belief_updates=belief_updates,
    )
    cfg = PlayerViewFilterConfig(player_id=player_id)
    filtered = filter_for_player(events, cfg)
    return render_trace_timeline(filtered, skip_repeats=skip_repeats)


def render_trace_timeline(
    events: list[TraceEvent],
    *,
    skip_repeats: bool = True,
) -> str:
    """TraceEvent 목록 → chronological narrative.

    Args:
        events: (이미 player_view 필터된) tick 오름차순 TraceEvent 목록.
        skip_repeats: 같은 agent의 연속 같은 action 묶기 (tick만 갱신).
            타 agent action 사이에 끼어있어도 per-agent로 추적.

    Returns:
        여러 줄 narrative 텍스트.
    """
    lines: list[str] = []
    last_action_per_agent: dict[str, str] = {}

    for ev in events:
        if skip_repeats and ev.type == "action_taken":
            agent = str(ev.payload.get("agent", ""))
            action = str(ev.payload.get("action", ""))
            if last_action_per_agent.get(agent) == action:
                continue
            last_action_per_agent[agent] = action
        elif ev.type == "action_taken":
            pass  # skip_repeats False: render all
        else:
            # 비-action event는 per-agent 추적 초기화 안 함
            # (bifurcation/trigger 이후에도 같은 action 연속이면 계속 묶음)
            pass
        lines.append(render_event_line(ev))
    return "\n".join(lines)
