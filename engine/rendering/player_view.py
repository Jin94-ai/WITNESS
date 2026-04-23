"""Player View Filter (TRACE_SCHEMA.md §3.1).

플레이어가 목격자가 되는 경험 구현의 핵심: 정보 비대칭성 적용.

규칙:
1. observable_from이 비어있으면 모두 관찰 가능 (공적 행동)
2. observable_from에 player_id 있으면 관찰 가능
3. 없으면 필터링 (플레이어는 이 행동을 못 봄)
4. internal_state_change / weights / latent_drive 등 내부 정보는 렌더 금지
   (플레이어 본인이 체험하는 agent 자신의 정보는 예외로 허용)
"""

from __future__ import annotations

from dataclasses import dataclass

from engine.rendering.trace_emitter import TraceEvent

# 플레이어에게 노출되면 안 되는 내부 필드 (타 에이전트 경우)
# weight_breakdown은 §2.2에서 드러내는 base/state_mult contribution — 내부 상태 노출
# cause 는 trigger의 condition 수치 묶음 (§2.1) — renderer가 선택적으로 활용
_INTERNAL_FIELDS = {
    "weights",
    "weight_breakdown",
    "latent_drive",
    "drive_attribution",
    "internal_state_change",
    "state_conditions_satisfied",  # top-level 버전
    "cause",  # 중첩 cause 블록
}


@dataclass
class PlayerViewFilterConfig:
    """필터 동작 설정.

    player_id: 플레이어가 체험 중인 agent ID.
    include_self_internals: 플레이어 자신의 내부 상태는 1인칭 내레이션으로 렌더 허용.
    include_bifurcation: bifurcation_point entry는 항상 포함 (서사 긴장감 유발).
    include_trigger_fired: trigger_fired entry 포함 (public event).
    """

    player_id: str
    include_self_internals: bool = True
    include_bifurcation: bool = True
    include_trigger_fired: bool = True


def is_observable(event: TraceEvent, cfg: PlayerViewFilterConfig) -> bool:
    """플레이어 시점에서 이 event가 보이는가."""
    if event.type == "bifurcation_point":
        return cfg.include_bifurcation

    if event.type == "trigger_fired":
        return cfg.include_trigger_fired  # 공적 event

    if event.type == "canonical_match":
        return False  # meta-level; 렌더 대상 아님 (validation용)

    if event.type == "action_taken":
        agent = event.payload.get("agent")
        observable_from = event.payload.get("observable_from") or []
        if agent == cfg.player_id:
            return True  # 자기 행동은 당연히 관찰 가능
        if not observable_from:
            return True  # 공적 (anyone observes)
        return cfg.player_id in observable_from

    if event.type == "belief_update":
        # 플레이어 자신의 belief update만 관찰 가능 (내면 추적)
        return event.payload.get("observer") == cfg.player_id

    # Unknown type: 기본 보류 (conservative)
    return False


def strip_internals(
    event: TraceEvent,
    cfg: PlayerViewFilterConfig,
) -> TraceEvent:
    """타 에이전트의 내부 필드 제거 (렌더 전용).

    플레이어 자신의 event라면 _INTERNAL_FIELDS도 보존 (자기 내면은 1인칭 내레이션).
    """
    agent = event.payload.get("agent")
    is_self = agent == cfg.player_id
    if is_self and cfg.include_self_internals:
        return event

    filtered = {
        k: v for k, v in event.payload.items() if k not in _INTERNAL_FIELDS
    }
    return TraceEvent(tick=event.tick, type=event.type, payload=filtered)


def filter_for_player(
    events: list[TraceEvent],
    cfg: PlayerViewFilterConfig,
) -> list[TraceEvent]:
    """시점별 필터링 + 내부 정보 제거된 trace.

    Renderer가 이 결과를 읽어서 서사 문장을 생성한다.
    """
    visible = [ev for ev in events if is_observable(ev, cfg)]
    return [strip_internals(ev, cfg) for ev in visible]
