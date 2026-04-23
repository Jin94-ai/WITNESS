"""Hazard 기반 이벤트 발생 시스템.

tick 고정 이벤트를 대체한다. 각 이벤트는 "위험도 함수(hazard function)"를 가지며,
매 tick 현재 상태에 따라 발생 확률이 계산되고, 확률적으로 발생한다.

핵심 전환:
  기존: if tick == 152: 체포()
  신규: hazard = f(상태들...) -> if rng.random() < 1 - exp(-hazard * dt): 체포()

Competing risks: 같은 tick에 여러 이벤트가 경쟁. 가장 높은 hazard가 우선.
Bounded stochasticity: precondition, cooldown, anchor window로 발산 방지.
"""

from __future__ import annotations

import math
import random
from typing import Any, Literal

from pydantic import BaseModel, Field

from engine.core.state import AgentState, get_nested_value


class HazardFactor(BaseModel):
    """Hazard 계산에 사용되는 인자. 에이전트 상태 또는 환경에서 값을 읽는다."""

    field_path: str = Field(description="점 구분 필드 경로 (AgentState 또는 EnvironmentState)")
    weight: float = Field(default=1.0, description="이 인자의 가중치")
    transform: str = Field(
        default="linear",
        description="변환 방식: linear, inverse, threshold",
    )
    threshold: float = Field(default=5.0, description="threshold 변환 시 기준값")
    source: str = Field(
        default="agent",
        description="값의 출처: 'agent' 또는 'environment'",
    )

    def compute(self, state: AgentState, environment: Any = None) -> float:
        """현재 상태/환경에서 인자 값을 계산한다."""
        if self.source == "environment" and environment is not None:
            raw = getattr(environment, self.field_path, None)
        else:
            raw = get_nested_value(state, self.field_path)

        if not isinstance(raw, (int, float)):
            return 0.0
        val = float(raw) / 10.0  # 0~1로 정규화

        if self.transform == "linear":
            return val * self.weight
        if self.transform == "inverse":
            return (1.0 - val) * self.weight
        if self.transform == "threshold":
            return self.weight if float(raw) >= self.threshold else 0.0
        return 0.0


class HazardFunction(BaseModel):
    """이벤트의 위험도 함수. 매 tick 발생 확률을 계산한다."""

    base_rate: float = Field(
        default=0.0, ge=0.0, description="기본 발생률 (상태 무관 부분)"
    )
    base_rate_unit: Literal["per_tick", "per_hour"] = Field(
        default="per_tick",
        description=(
            "base_rate와 factors 합산 hazard의 시간 단위. "
            "'per_tick' (기본): dt=1.0 — 기존 v0.5~v0.7 legacy calibration 호환. "
            "'per_hour': caller가 dt=tick_scale_hours를 전달해야 (v1.2 phase-linked "
            "scenario에서 장기 아크 실시간 기준 rate 해석)."
        ),
    )
    factors: list[HazardFactor] = Field(
        default_factory=list, description="상태/환경 기반 인자 목록"
    )
    max_hazard: float = Field(
        default=1.0, gt=0.0, description="hazard 상한 (발산 방지)"
    )

    def compute_hazard(self, state: AgentState, environment: Any = None) -> float:
        """현재 상태/환경에서 hazard 값을 계산한다 (0 이상)."""
        h = self.base_rate
        for factor in self.factors:
            h += factor.compute(state, environment)
        return min(max(h, 0.0), self.max_hazard)

    def firing_probability(self, state: AgentState, dt: float = 1.0, environment: Any = None) -> float:
        """현재 상태에서 이 tick에 이벤트가 발생할 확률.

        Poisson process: P(event) = 1 - exp(-hazard * dt)
        """
        h = self.compute_hazard(state, environment)
        if h <= 0:
            return 0.0
        return 1.0 - math.exp(-h * dt)


class HazardPrecondition(BaseModel):
    """Hazard 활성화 전제조건. 충족되지 않으면 hazard = 0."""

    field_path: str = Field(description="AgentState의 점 구분 필드 경로")
    operator: str = Field(description="비교 연산자: gt, lt, gte, lte, eq, in")
    value: Any = Field(description="비교 대상 값")

    def evaluate(self, state: AgentState) -> bool:
        """전제조건 충족 여부."""
        actual = get_nested_value(state, self.field_path)
        if actual is None:
            return False
        if self.operator == "gt":
            return bool(actual > self.value)
        if self.operator == "lt":
            return bool(actual < self.value)
        if self.operator == "gte":
            return bool(actual >= self.value)
        if self.operator == "lte":
            return bool(actual <= self.value)
        if self.operator == "eq":
            return bool(actual == self.value)
        if self.operator == "in":
            return bool(actual in self.value)
        return False


class HazardEvent(BaseModel):
    """Hazard 기반 이벤트 정의.

    tick 고정이 아니라, 매 tick hazard를 계산하여 확률적으로 발생.
    anchor_window: 발생 가능한 tick 범위 (bounded stochasticity).
    """

    event_id: str = Field(description="이벤트 고유 ID")
    description: str = Field(default="")
    hazard: HazardFunction = Field(description="위험도 함수")
    preconditions: list[HazardPrecondition] = Field(
        default_factory=list, description="활성화 전제조건"
    )
    anchor_window: tuple[int, int] | None = Field(
        default=None, description="발생 가능 tick 범위 [min, max]. None이면 항시 가능."
    )
    deadline_tick: int | None = Field(
        default=None, description="이 tick까지 미발생 시 강제 발동. None이면 강제 없음."
    )
    cooldown: int = Field(default=0, ge=0, description="발동 후 재발동까지 대기 tick")
    max_fires: int = Field(default=1, ge=1, description="최대 발동 횟수")
    fire_count: int = Field(default=0, ge=0, description="현재까지 발동 횟수")
    last_fired_tick: int = Field(default=-1, description="마지막 발동 tick")
    source_ref: str = Field(default="", description="출처 참조")

    # 발동 시 적용할 효과와 행동 선택지는 ExternalEvent에서 가져옴
    # HazardEvent가 firing되면 연결된 ExternalEvent를 생성
    effects_on_fire: list[dict] = Field(
        default_factory=list, description="발동 시 StateEffect 데이터"
    )
    action_options_on_fire: list[dict] = Field(
        default_factory=list, description="발동 시 ActionOption 데이터"
    )

    def is_eligible(self, tick: int, state: AgentState) -> bool:
        """이 tick에서 이 이벤트가 발동 가능한지."""
        if self.fire_count >= self.max_fires:
            return False
        if self.cooldown > 0 and self.last_fired_tick >= 0:
            if tick - self.last_fired_tick < self.cooldown:
                return False
        if self.anchor_window is not None:
            if tick < self.anchor_window[0] or tick > self.anchor_window[1]:
                return False
        return all(p.evaluate(state) for p in self.preconditions)

    def is_deadline(self, tick: int) -> bool:
        """deadline에 도달했는지."""
        if self.deadline_tick is None:
            return False
        return tick >= self.deadline_tick and self.fire_count < self.max_fires

    def record_fire(self, tick: int) -> None:
        """발동을 기록한다."""
        self.fire_count += 1
        self.last_fired_tick = tick


class HazardEngine:
    """Hazard 기반 이벤트 발생 엔진.

    매 tick:
    1. eligible한 이벤트 필터
    2. 각 이벤트의 firing probability 계산
    3. competing risks: 확률적으로 발동할 이벤트 결정
    4. deadline 도달 시 강제 발동
    """

    def __init__(self, hazard_events: list[HazardEvent]) -> None:
        self._events = hazard_events

    @property
    def events(self) -> list[HazardEvent]:
        return list(self._events)

    def evaluate_tick(
        self,
        tick: int,
        state: AgentState,
        rng: random.Random,
        dt: float = 1.0,
        max_fires_per_tick: int = 2,
        environment: Any = None,
        tick_scale_hours: float | None = None,
    ) -> list[HazardEvent]:
        """이 tick에서 발동하는 이벤트 목록을 반환한다.

        Competing risks: eligible 이벤트들의 hazard를 계산하고,
        가장 높은 hazard부터 발동을 시도한다. max_fires_per_tick으로
        한 tick에 너무 많은 이벤트가 터지는 것을 방지 (bounded stochasticity).

        v1.2: per-event `base_rate_unit` 해석.
        - 'per_tick': `dt` 그대로 사용 (legacy, default).
        - 'per_hour': `tick_scale_hours`가 주어지면 그것을 dt로 사용,
          아니면 `dt` fallback.

        Returns:
            발동된 HazardEvent 목록. 빈 리스트일 수 있음.
        """
        fired: list[HazardEvent] = []

        # 1. deadline 강제 발동
        for event in self._events:
            if event.is_deadline(tick) and event.fire_count < event.max_fires:
                event.record_fire(tick)
                fired.append(event)

        fired_ids = {e.event_id for e in fired}

        # 2. Competing risks: hazard 순으로 정렬 후 순차 시도
        eligible = [
            e for e in self._events
            if e.is_eligible(tick, state) and e.event_id not in fired_ids
        ]

        # hazard 내림차순 정렬 (가장 위험한 이벤트 우선)
        eligible.sort(
            key=lambda e: e.hazard.compute_hazard(state, environment), reverse=True
        )

        for event in eligible:
            if len(fired) >= max_fires_per_tick:
                break
            # per-event dt 해석
            if event.hazard.base_rate_unit == "per_hour" and tick_scale_hours is not None:
                effective_dt = tick_scale_hours
            else:
                effective_dt = dt
            prob = event.hazard.firing_probability(state, effective_dt, environment)
            if rng.random() < prob:
                event.record_fire(tick)
                fired.append(event)

        return fired

    def reset(self) -> None:
        """모든 이벤트의 발동 상태를 초기화한다."""
        for event in self._events:
            event.fire_count = 0
            event.last_fired_tick = -1
