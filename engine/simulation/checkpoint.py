"""체크포인트 시스템 (Hindcasting).

시뮬레이션 결과를 정경 관측 데이터와 대조하여 일치율을 측정한다.
기후 모델의 Hindcasting과 동일한 역할.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from engine.core.state import AgentState, get_nested_value


class CheckpointCondition(BaseModel):
    """체크포인트 조건. 시뮬레이션 결과가 정경과 일치하는지 판별."""

    condition_type: Literal["action_taken", "state_range", "state_comparison"] = Field(
        description="조건 유형"
    )
    params: dict[str, Any] = Field(description="조건 파라미터")


class Checkpoint(BaseModel):
    """정경 체크포인트. 성경 기록에서 확인 가능한 관측 사실."""

    checkpoint_id: str = Field(description="체크포인트 ID")
    tick: int = Field(ge=0, description="해당 tick")
    description: str = Field(default="", description="설명")
    conditions: list[CheckpointCondition] = Field(description="충족 조건 목록")
    weight: float = Field(default=1.0, ge=0.0, description="중요도 가중치")


class ActionRecord(BaseModel):
    """시뮬레이션 중 기록된 행동.

    v1.0+ Trace Schema (TRACE_SCHEMA.md) 확장 필드:
    - observable_from: 이 행동을 관찰 가능한 다른 agent IDs (목격자 시점 필터)
    - visible_signal: 외부에서 관찰되는 행동 서술 (v2.0 렌더러 전용)

    두 필드 모두 default이며 기존 코드 backward compatible.
    """

    tick: int = Field(ge=0)
    event_id: str
    chosen_action: str
    weights: dict[str, float] = Field(default_factory=dict)
    observable_from: list[str] = Field(
        default_factory=list,
        description="이 행동을 관찰 가능한 agent IDs (비어있으면 모두에게 관찰 가능)",
    )
    visible_signal: str | None = Field(
        default=None,
        description="외부에서 관찰되는 행동 서술 (v2.0 렌더러 전용)",
    )
    weight_breakdown: dict[str, float] | None = Field(
        default=None,
        description="선택된 action의 weight 구성 요소 분해 (TRACE_SCHEMA §2.2). "
                    "base + state_mult.<field> contributions + final. "
                    "v1.0 latent drive 도입 시 drive.<axis> 기여 추가 예정.",
    )


class CheckpointResult(BaseModel):
    """체크포인트 평가 결과."""

    checkpoint_id: str
    passed: bool
    details: str = ""


def evaluate_checkpoint(
    checkpoint: Checkpoint,
    state_history: dict[int, AgentState],
    action_history: list[ActionRecord],
) -> CheckpointResult:
    """체크포인트를 평가한다.

    Args:
        checkpoint: 평가할 체크포인트
        state_history: tick -> AgentState 매핑
        action_history: 시뮬레이션 중 기록된 행동 목록

    Returns:
        CheckpointResult
    """
    all_passed = True
    details_parts: list[str] = []

    for cond in checkpoint.conditions:
        passed, detail = _evaluate_condition(
            cond, checkpoint.tick, state_history, action_history
        )
        if not passed:
            all_passed = False
        details_parts.append(detail)

    return CheckpointResult(
        checkpoint_id=checkpoint.checkpoint_id,
        passed=all_passed,
        details="; ".join(details_parts),
    )


def _evaluate_condition(
    cond: CheckpointCondition,
    tick: int,
    state_history: dict[int, AgentState],
    action_history: list[ActionRecord],
) -> tuple[bool, str]:
    """개별 조건을 평가한다."""
    ct = cond.condition_type
    params = cond.params

    if ct == "action_taken":
        return _check_action_taken(params, action_history)
    if ct == "state_range":
        return _check_state_range(params, tick, state_history)
    if ct == "state_comparison":
        return _check_state_comparison(params, tick, state_history)

    return False, f"unknown condition_type: {ct}"


def _check_action_taken(
    params: dict[str, Any],
    action_history: list[ActionRecord],
) -> tuple[bool, str]:
    """특정 행동이 수행되었는지 확인한다.

    파라미터:
        action_id: 검사할 행동 ID
        min_count: 최소 발생 횟수 (기본 1)
        at_tick_range: [min, max] 절대 tick 범위 (optional)
        relative_to_event: 기준 이벤트 ID (optional) -- 이벤트 발생 tick 기준으로 상대 범위 계산
        relative_offset: [before, after] 기준 이벤트 tick 전후 범위 (기본 [0, 10])
    """
    action_id = params.get("action_id", "")
    min_count = params.get("min_count", 1)
    tick_range = params.get("at_tick_range")

    # 이벤트-상대적 범위: relative_to_event가 있으면 at_tick_range 대신 동적 계산
    rel_event = params.get("relative_to_event")
    if rel_event is not None and tick_range is None:
        offset = params.get("relative_offset", [0, 10])
        # 기준 이벤트의 tick을 action_history에서 찾기
        ref_tick = next(
            (a.tick for a in action_history if a.event_id == rel_event), None
        )
        if ref_tick is not None:
            tick_range = [ref_tick - offset[0], ref_tick + offset[1]]

    matching = [
        a for a in action_history
        if a.chosen_action == action_id
        and (tick_range is None or tick_range[0] <= a.tick <= tick_range[1])
    ]

    count = len(matching)
    passed = count >= min_count
    detail = f"action '{action_id}': {count}/{min_count} occurrences"
    return passed, detail


def _check_state_range(
    params: dict[str, Any],
    tick: int,
    state_history: dict[int, AgentState],
) -> tuple[bool, str]:
    """특정 tick에서 상태 값이 범위 내인지 확인한다."""
    field_path = params.get("field_path", "")
    min_val = params.get("min")
    max_val = params.get("max")

    # 정확한 tick이 없으면 가장 가까운 이전 tick 사용
    state = _get_closest_state(tick, state_history)
    if state is None:
        return False, f"no state at tick {tick}"

    actual = get_nested_value(state, field_path)
    if actual is None:
        return False, f"field '{field_path}' not found"

    passed = True
    if min_val is not None and actual < min_val:
        passed = False
    if max_val is not None and actual > max_val:
        passed = False

    detail = f"'{field_path}'={actual:.1f} (min={min_val}, max={max_val})"
    return passed, detail


def _check_state_comparison(
    params: dict[str, Any],
    tick: int,
    state_history: dict[int, AgentState],
) -> tuple[bool, str]:
    """두 상태 필드를 비교한다."""
    field_a = params.get("field_a", "")
    field_b = params.get("field_b", "")
    operator = params.get("operator", "gt")

    state = _get_closest_state(tick, state_history)
    if state is None:
        return False, f"no state at tick {tick}"

    val_a = get_nested_value(state, field_a)
    val_b = get_nested_value(state, field_b)

    if val_a is None or val_b is None:
        return False, f"field not found: {field_a} or {field_b}"

    if not isinstance(val_a, (int, float)) or not isinstance(val_b, (int, float)):
        return False, f"non-numeric comparison: {field_a}={val_a}, {field_b}={val_b}"

    if operator == "gt":
        passed = val_a > val_b
    elif operator == "lt":
        passed = val_a < val_b
    else:
        passed = val_a == val_b

    detail = f"'{field_a}'={val_a:.1f} {operator} '{field_b}'={val_b:.1f}"
    return passed, detail


def _get_closest_state(tick: int, state_history: dict[int, AgentState]) -> AgentState | None:
    """해당 tick 또는 가장 가까운 이전 tick의 상태를 반환한다."""
    if tick in state_history:
        return state_history[tick]
    # 이전 tick 중 가장 가까운 것
    earlier = [t for t in state_history if t <= tick]
    if earlier:
        return state_history[max(earlier)]
    return None


def compute_match_rate(
    results: list[CheckpointResult],
    checkpoints: list[Checkpoint],
) -> float:
    """가중 정경 일치율을 계산한다.

    Returns:
        0.0~1.0 범위의 일치율
    """
    if not results or not checkpoints:
        return 0.0

    cp_map = {cp.checkpoint_id: cp for cp in checkpoints}
    total_weight = 0.0
    passed_weight = 0.0

    for r in results:
        cp = cp_map.get(r.checkpoint_id)
        w = cp.weight if cp else 1.0
        total_weight += w
        if r.passed:
            passed_weight += w

    return passed_weight / total_weight if total_weight > 0 else 0.0
