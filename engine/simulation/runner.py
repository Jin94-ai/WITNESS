"""시뮬레이션 러너.

Hazard-driven 모드: 이벤트가 상태 기반 위험도로 확률적 발생.
Legacy 모드: tick 고정 이벤트 (하위 호환).

핵심 루프:
  tick 순회 -> 정경 개입 -> hazard 평가 -> 이벤트 발동 -> 행동 결정
  -> 노이즈 주입 -> 규칙 적용 -> 상태 기록
"""

from __future__ import annotations

import copy
import random

from pydantic import BaseModel, Field

from engine.core.event import (
    ActionOption,
    ExternalEvent,
    StateEffect,
    WeightFormula,
)
from engine.core.hazard import HazardEngine, HazardEvent
from engine.core.state import AgentState, clamp, set_nested_value
from engine.core.world import SimulationConfig
from engine.rules.base import RuleContext, RuleEngine
from engine.simulation.checkpoint import (
    ActionRecord,
    Checkpoint,
    CheckpointResult,
    compute_match_rate,
    evaluate_checkpoint,
)
from engine.rules.environment import EnvironmentDynamicsRule
from engine.simulation.decision import decide_action
from engine.simulation.event_scheduler import EventScheduler
from engine.simulation.resolution import ResolutionConfig, ResolutionEngine, ResolutionTier


class SimulationResult(BaseModel):
    """단일 시뮬레이션 실행 결과."""

    seed: int | None = None
    final_state: AgentState
    state_snapshots: dict[int, AgentState] = Field(
        default_factory=dict, description="이벤트 tick의 상태 스냅샷"
    )
    action_history: list[ActionRecord] = Field(default_factory=list)
    checkpoint_results: list[CheckpointResult] = Field(default_factory=list)
    canonical_match_rate: float = 0.0
    fired_events: list[dict] = Field(
        default_factory=list,
        description="발동된 hazard 이벤트 기록 [{event_id, tick}]",
    )
    resolution_tiers: dict[int, str] = Field(
        default_factory=dict,
        description="tick별 해상도 등급 기록 (이벤트 tick만)",
    )


class SimulationRunner:
    """시뮬레이션 실행기. Hazard-driven과 legacy 모드를 모두 지원."""

    def __init__(
        self,
        config: SimulationConfig,
        rule_engine: RuleEngine,
        checkpoints: list[Checkpoint] | None = None,
        resolution_config: ResolutionConfig | None = None,
    ) -> None:
        self._config = config
        self._rule_engine = rule_engine
        self._checkpoints = checkpoints or []
        self._resolution_config = resolution_config

    def run_single(self, seed: int | None = None) -> SimulationResult:
        """단일 시뮬레이션을 실행한다."""
        if self._config.is_hazard_driven:
            return self._run_hazard_driven(seed)
        return self._run_legacy(seed)

    def _run_hazard_driven(self, seed: int | None = None) -> SimulationResult:
        """Hazard-driven 시뮬레이션."""
        effective_seed = seed if seed is not None else self._config.seed
        rng = random.Random(effective_seed)

        state = self._apply_overrides(self._config.initial_state)

        # 환경 상태 (매 run마다 독립 복사)
        environment = self._config.environment.model_copy(deep=True)

        # Hazard 엔진 (매 run마다 독립 복사)
        hazard_events = [e.model_copy(deep=True) for e in self._config.hazard_events]
        hazard_engine = HazardEngine(hazard_events)

        # Legacy 스케줄러 (canonical_timeline 이벤트용)
        scheduler = EventScheduler(
            self._config.events,
            self._config.interventions,
        )

        state_snapshots: dict[int, AgentState] = {0: state}
        action_history: list[ActionRecord] = []
        fired_events: list[dict] = []
        resolution_tiers: dict[int, str] = {}
        tick_had_event = False

        # 동적 해상도 엔진 (설정이 있으면)
        res_engine = (
            ResolutionEngine(self._resolution_config)
            if self._resolution_config else None
        )

        for tick in range(1, self._config.max_tick + 1):
            state = state.model_copy(update={"tick": tick})
            tick_had_event = False

            # 1. 정경 개입 (canonical_timeline)
            for intervention in scheduler.get_interventions_for_tick(tick):
                state = intervention.apply(state)
                tick_had_event = True

            # 2. Legacy tick 고정 이벤트 (하위 호환)
            legacy_events = scheduler.get_events_for_tick(tick)
            for event in legacy_events:
                if not all(p.evaluate(state) for p in event.preconditions):
                    continue
                for effect in event.effects:
                    state = effect.apply(state)
                if event.action_options:
                    state, action_history = self._process_actions(
                        state, event.event_id, event.action_options,
                        tick, action_history, rng,
                    )
                tick_had_event = True

            # 3. Hazard 기반 이벤트 평가
            fired = hazard_engine.evaluate_tick(tick, state, rng, environment=environment)
            for hazard_ev in fired:
                fired_events.append({"event_id": hazard_ev.event_id, "tick": tick})
                tick_had_event = True

                # 행동 결정을 이벤트 효과 적용 전에 수행
                # (체포 시 fear SET이 행동 결정 직전 상태를 균일화하는 것을 방지)
                if hazard_ev.action_options_on_fire:
                    options = [
                        ActionOption.model_validate(o)
                        for o in hazard_ev.action_options_on_fire
                    ]
                    state, action_history = self._process_actions(
                        state, hazard_ev.event_id, options,
                        tick, action_history, rng, environment,
                    )

                # 이벤트 효과 적용 (행동 결정 후)
                for effect_data in hazard_ev.effects_on_fire:
                    effect = StateEffect.model_validate(effect_data)
                    # "env." 접두사면 환경에 적용, 아니면 에이전트에 적용
                    if effect.field_path.startswith("env."):
                        env_field = effect.field_path[4:]  # "env." 제거
                        current = getattr(environment, env_field, None)
                        if current is not None and isinstance(current, (int, float)):
                            if effect.operation == "set":
                                setattr(environment, env_field, effect.value)
                            elif effect.operation == "add":
                                setattr(environment, env_field, clamp(current + float(effect.value)))
                    else:
                        state = effect.apply(state)

            # 4. 상태 노이즈 주입 (Langevin)
            if self._config.state_noise_scale > 0:
                state = self._apply_noise(state, rng)

            # 5. 규칙 엔진 적용
            active_events = legacy_events + [
                ExternalEvent(event_id=fe["event_id"], tick=tick)
                for fe in fired_events if fe["tick"] == tick
            ]
            context = RuleContext(
                tick=tick, delta_tick=1, active_events=active_events, rng=rng,
            )
            state = self._rule_engine.apply_all(state, context)

            # 5.5. 환경 동적 규칙 적용
            env_rule = EnvironmentDynamicsRule()
            environment = env_rule.apply(environment, tick)

            # 6. 동적 해상도 판정 + 스냅샷
            if res_engine:
                if tick_had_event:
                    res_engine.record_event(tick)
                tier = res_engine.determine_tier(tick, state)
                if tier != ResolutionTier.CHRONICLE:
                    resolution_tiers[tick] = tier.value
                # Scene/Episode면 항상 스냅샷, Chronicle이면 매 50tick
                if res_engine.should_snapshot(tier) or tick_had_event or tick % 50 == 0:
                    state_snapshots[tick] = state
            else:
                if tick_had_event or tick % 10 == 0:
                    state_snapshots[tick] = state

        state_snapshots[self._config.max_tick] = state

        cp_results = [
            evaluate_checkpoint(cp, state_snapshots, action_history)
            for cp in self._checkpoints
        ]
        match_rate = compute_match_rate(cp_results, self._checkpoints)

        return SimulationResult(
            seed=effective_seed,
            final_state=state,
            state_snapshots=state_snapshots,
            action_history=action_history,
            checkpoint_results=cp_results,
            canonical_match_rate=match_rate,
            fired_events=fired_events,
            resolution_tiers=resolution_tiers,
        )

    def _run_legacy(self, seed: int | None = None) -> SimulationResult:
        """기존 tick 고정 모드 (하위 호환)."""
        effective_seed = seed if seed is not None else self._config.seed
        rng = random.Random(effective_seed)

        state = self._apply_overrides(self._config.initial_state)
        scheduler = EventScheduler(self._config.events, self._config.interventions)

        state_snapshots: dict[int, AgentState] = {0: state}
        action_history: list[ActionRecord] = []

        for tick in range(1, self._config.max_tick + 1):
            state = state.model_copy(update={"tick": tick})

            for intervention in scheduler.get_interventions_for_tick(tick):
                state = intervention.apply(state)

            events = scheduler.get_events_for_tick(tick)
            for event in events:
                if not all(p.evaluate(state) for p in event.preconditions):
                    continue
                for effect in event.effects:
                    state = effect.apply(state)
                if event.action_options:
                    state, action_history = self._process_actions(
                        state, event.event_id, event.action_options,
                        tick, action_history, rng,
                    )

            context = RuleContext(
                tick=tick, delta_tick=1, active_events=events, rng=rng,
            )
            state = self._rule_engine.apply_all(state, context)

            if events:
                state_snapshots[tick] = state

        state_snapshots[self._config.max_tick] = state

        cp_results = [
            evaluate_checkpoint(cp, state_snapshots, action_history)
            for cp in self._checkpoints
        ]
        match_rate = compute_match_rate(cp_results, self._checkpoints)

        return SimulationResult(
            seed=effective_seed,
            final_state=state,
            state_snapshots=state_snapshots,
            action_history=action_history,
            checkpoint_results=cp_results,
            canonical_match_rate=match_rate,
        )

    def _process_actions(
        self,
        state: AgentState,
        event_id: str,
        options: list[ActionOption],
        tick: int,
        action_history: list[ActionRecord],
        rng: random.Random,
        environment: object | None = None,
    ) -> tuple[AgentState, list[ActionRecord]]:
        """행동 결정 + 효과 적용 + slow_state 갱신 + 기록."""
        chosen = decide_action(state, options, rng, environment)
        if chosen:
            weights = {
                opt.action_id: opt.weight_formula.compute_weight(state, environment)
                for opt in options
            }
            action_history.append(
                ActionRecord(
                    tick=tick,
                    event_id=event_id,
                    chosen_action=chosen.action_id,
                    weights=weights,
                )
            )
            for effect in chosen.effects:
                state = effect.apply(state)

        return state, action_history

    def _apply_noise(self, state: AgentState, rng: random.Random) -> AgentState:
        """감정 상태에 가우시안 노이즈 주입 (Langevin equation)."""
        scale = self._config.state_noise_scale
        emotions = state.emotions
        updates: dict[str, float] = {}
        for field in ("fear", "hope", "grief", "confusion", "love"):
            current = getattr(emotions, field)
            noise = rng.gauss(0, scale)
            updates[field] = clamp(current + noise)
        new_emotions = emotions.model_copy(update=updates)
        return state.model_copy(update={"emotions": new_emotions})

    def _apply_overrides(self, state: AgentState) -> AgentState:
        """파라미터 오버라이드를 초기 상태에 적용한다."""
        result = state
        for path, value in self._config.parameter_overrides.items():
            result = set_nested_value(result, path, value)
        return result
