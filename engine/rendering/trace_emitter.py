"""Trace Event Emitter (TRACE_SCHEMA.md §2 통합).

SimulationResult의 개별 구조 (fired_triggers, fired_events, action_histories,
checkpoint_results) 를 JSONL render-ready trace entry 스트림으로 변환.

v2.0 Narrative Witness Layer가 읽을 최종 포맷.

참조:
- TRACE_SCHEMA.md §2 (entry types)
- TRACE_SCHEMA.md §3 (render filter rules)
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable


@dataclass
class TraceEvent:
    """단일 trace entry (TRACE_SCHEMA.md §2).

    type field로 entry 종류 구분:
    - "action_taken"      (§2.2)
    - "trigger_fired"     (§2.1)
    - "belief_update"     (§2.3, v1.1 예정)
    - "bifurcation_point" (§2.4)
    - "canonical_match"   (§2.5)
    """

    tick: int
    type: str
    payload: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        """JSONL 한 줄."""
        d = asdict(self)
        return json.dumps(d, ensure_ascii=False)


def emit_action_events(
    action_histories: dict[str, list],
) -> Iterable[TraceEvent]:
    """ActionRecord 기록을 action_taken TraceEvent로 변환 (§2.2)."""
    for agent, records in action_histories.items():
        for rec in records:
            payload: dict[str, Any] = {
                "agent": agent,
                "action": rec.chosen_action,
                "event_id": rec.event_id,
                "weights": rec.weights,
                "observable_from": list(rec.observable_from),
                "visible_signal": rec.visible_signal,
            }
            # weight_breakdown은 None 아닐 때만 포함 (§2.2 선택 필드)
            if rec.weight_breakdown is not None:
                payload["weight_breakdown"] = dict(rec.weight_breakdown)
            yield TraceEvent(
                tick=rec.tick,
                type="action_taken",
                payload=payload,
            )


def emit_trigger_events(
    fired_triggers: list[dict],
) -> Iterable[TraceEvent]:
    """발동된 trigger를 trigger_fired TraceEvent로 변환 (§2.1).

    cause.state_conditions_satisfied 는 내부 수치 정보이지만
    trigger 발동은 공적 event (결과가 드러나므로) — state 값은 노출하되,
    내부 drive snapshot은 제외. Player view filter가 타 agent 내부만 스트립.
    """
    for t in fired_triggers:
        payload: dict[str, Any] = {
            "trigger_id": t.get("trigger_id"),
            "event_id": t.get("event_id"),
            "event_template_id": t.get("event_template_id"),
        }
        conditions = t.get("state_conditions_satisfied")
        if conditions:
            # cause 하위로 중첩 (§2.1 구조)
            payload["cause"] = {
                "state_conditions_satisfied": list(conditions),
            }
        yield TraceEvent(
            tick=t.get("tick", 0),
            type="trigger_fired",
            payload=payload,
        )


def emit_canonical_matches(
    checkpoint_results: dict[str, list],
) -> Iterable[TraceEvent]:
    """Checkpoint 결과를 canonical_match TraceEvent로 변환 (§2.5)."""
    for agent, checkpoints in checkpoint_results.items():
        for cp in checkpoints:
            yield TraceEvent(
                tick=0,  # checkpoint는 run 전체를 요약 (tick 정보 개별 필요 시 확장)
                type="canonical_match",
                payload={
                    "agent": agent,
                    "checkpoint_id": cp.checkpoint_id,
                    "passed": cp.passed,
                    "details": cp.details,
                },
            )


def emit_belief_updates(
    belief_updates: list[dict],
) -> Iterable[TraceEvent]:
    """Belief update 기록을 belief_update TraceEvent로 (§2.3, v1.1).

    Args:
        belief_updates: [{tick, observer, target, trigger, belief_change}, ...]
            - belief_change: {"field": "prev → new", ...}
    """
    for bu in belief_updates:
        yield TraceEvent(
            tick=bu.get("tick", 0),
            type="belief_update",
            payload={
                "observer": bu.get("observer"),
                "target": bu.get("target"),
                "trigger": bu.get("trigger"),
                "belief_change": bu.get("belief_change", {}),
            },
        )


def emit_bifurcation_events(
    bifurcation_reports: list,
) -> Iterable[TraceEvent]:
    """Bifurcation 탐지 결과를 bifurcation_point TraceEvent로 변환 (§2.4)."""
    for report in bifurcation_reports:
        lo, hi = report.decision_window
        yield TraceEvent(
            tick=report.max_growth_std_tick,
            type="bifurcation_point",
            payload={
                "decision_window": [lo, hi],
                "plateau_start": report.plateau_start,
                "max_growth_std": report.max_growth_std_value,
            },
        )


def collect_trace_events(
    result: Any,
    bifurcation_reports: list[Any] | None = None,
    belief_updates: list[dict[str, Any]] | None = None,
) -> list[TraceEvent]:
    """SimulationResult → tick 순 정렬된 TraceEvent 목록.

    Args:
        result: MultiAgentResult 또는 단일 SimulationResult (action_histories, etc.)
        bifurcation_reports: (옵션) 외부 계산된 bifurcation 결과 (§2.4)
        belief_updates: (옵션, v1.1+) agent belief 갱신 기록 (§2.3)

    Returns:
        tick 오름차순 TraceEvent 목록.
    """
    events: list[TraceEvent] = []

    # action_histories: dict (multi) or list (single)
    actions = getattr(result, "action_histories", None)
    if isinstance(actions, dict):
        events.extend(emit_action_events(actions))
    elif isinstance(actions, list):
        # 단일 에이전트 경로: agent_id 미상이면 "_"
        agent_id = getattr(result, "agent_id", None) or "_"
        events.extend(emit_action_events({agent_id: actions}))

    fired_triggers = getattr(result, "fired_triggers", [])
    events.extend(emit_trigger_events(fired_triggers))

    checkpoints = getattr(result, "checkpoint_results", {})
    if isinstance(checkpoints, dict):
        events.extend(emit_canonical_matches(checkpoints))

    if bifurcation_reports:
        events.extend(emit_bifurcation_events(bifurcation_reports))

    if belief_updates:
        events.extend(emit_belief_updates(belief_updates))

    events.sort(key=lambda e: (e.tick, e.type))
    return events


def write_trace_jsonl(events: Iterable[TraceEvent], path: str) -> int:
    """JSONL 파일로 기록. 반환: 기록된 줄 수."""
    count = 0
    with open(path, "w", encoding="utf-8") as f:
        for ev in events:
            f.write(ev.to_json() + "\n")
            count += 1
    return count
