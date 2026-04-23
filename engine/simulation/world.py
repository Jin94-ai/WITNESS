"""다중 에이전트 시뮬레이션 월드.

Mesa의 Model 역할. 여러 에이전트를 관리하고, 트리거 시스템으로
에이전트 간 상호작용에서 이벤트를 발생시킨다.

핵심 루프 (매 tick):
  1. 에이전트 활성화 순서 결정
  2. 각 에이전트: 자발적 행동 선택 + 규칙 적용
  3. 트리거 평가: 에이전트 상태/행동 조건 충족 -> 이벤트 주입
  4. Hazard 이벤트 평가 (에이전트별)
  5. 환경 동적 규칙 적용
  6. 상태 스냅샷

단일 에이전트 시: 기존 SimulationRunner 위임.
"""

from __future__ import annotations

import random
from typing import Any, Literal

from pydantic import BaseModel, Field

from engine.core.action import AgentBehaviorProfile
from engine.core.event import ActionOption, StateEffect
from engine.core.hazard import HazardEngine
from engine.core.state import AgentState, clamp, set_nested_value
from engine.core.trigger import TriggerEngine
from engine.core.world import SimulationConfig
from engine.rules.base import RuleContext, RuleEngine
from engine.rules.environment import EnvironmentDynamicsRule
from engine.simulation.checkpoint import (
    ActionRecord,
    Checkpoint,
    CheckpointResult,
    compute_match_rate,
    evaluate_checkpoint,
)
from engine.simulation.decision import decide_action
from engine.simulation.event_scheduler import EventScheduler
from engine.simulation.scheduler import AgentScheduler


class MultiAgentResult(BaseModel):
    """다중 에이전트 시뮬레이션 결과."""

    seed: int | None = None
    final_states: dict[str, AgentState] = Field(
        default_factory=dict, description="에이전트별 최종 상태"
    )
    state_snapshots: dict[str, dict[int, AgentState]] = Field(
        default_factory=dict, description="에이전트별 tick별 상태 스냅샷"
    )
    action_histories: dict[str, list[ActionRecord]] = Field(
        default_factory=dict, description="에이전트별 행동 이력"
    )
    checkpoint_results: dict[str, list[CheckpointResult]] = Field(
        default_factory=dict, description="에이전트별 체크포인트 결과"
    )
    canonical_match_rates: dict[str, float] = Field(
        default_factory=dict, description="에이전트별 정경 일치율"
    )
    fired_triggers: list[dict[str, Any]] = Field(
        default_factory=list, description="발동된 트리거 기록"
    )
    fired_events: list[dict[str, Any]] = Field(
        default_factory=list, description="발동된 hazard 이벤트 기록"
    )

    def extract_agent_result(self, agent_id: str) -> Any:
        """특정 에이전트의 결과를 SimulationResult 형태로 추출한다.

        기존 POM scorecard, 분석 파이프라인과의 호환성을 위한 어댑터.

        Returns:
            SimulationResult 인스턴스 (순환 import 방지를 위해 Any 타입)
        """
        from engine.simulation.runner import SimulationResult

        return SimulationResult(
            seed=self.seed,
            final_state=self.final_states[agent_id],
            state_snapshots=self.state_snapshots.get(agent_id, {}),
            action_history=self.action_histories.get(agent_id, []),
            checkpoint_results=self.checkpoint_results.get(agent_id, []),
            canonical_match_rate=self.canonical_match_rates.get(agent_id, 0.0),
            fired_events=self.fired_events,
        )


class SimulationWorld:
    """다중 에이전트 시뮬레이션 월드.

    Args:
        config: 시뮬레이션 설정 (initial_states에 여러 에이전트)
        rule_engine: 규칙 엔진 (모든 에이전트에 공유)
        behavior_profiles: 에이전트별 행동 프로파일
        checkpoints: 검증 체크포인트 (optional)
    """

    def __init__(
        self,
        config: SimulationConfig,
        rule_engine: RuleEngine,
        behavior_profiles: dict[str, AgentBehaviorProfile] | None = None,
        checkpoints: dict[str, list[Checkpoint]] | None = None,
        scheduler_mode: Literal["sequential", "random", "simultaneous"] = "random",
        drive_model: Any = None,
        policies: dict[str, Any] | None = None,
    ) -> None:
        """SimulationWorld initializer.

        Args:
            drive_model: v1.0+ LatentDriveModel (optional). is_active() True이면
                매 tick 규칙 적용 후 agent.drive_state를 encode로 갱신.
                None이면 v0.x 모드 (symbolic only).
            policies: Spike 6 optional DecisionPolicy per agent_id. Unset or None →
                기존 규칙 기반 동작 그대로 (backward compat).
        """
        self._config = config
        self._rule_engine = rule_engine
        self._behavior_profiles = behavior_profiles or {}
        self._checkpoints = checkpoints or {}
        self._scheduler_mode = scheduler_mode
        self._drive_model = drive_model
        self._policies = policies or {}

    def run(self, seed: int | None = None) -> MultiAgentResult:
        """다중 에이전트 시뮬레이션을 실행한다."""
        effective_seed = seed if seed is not None else self._config.seed
        rng = random.Random(effective_seed)

        # 초기 상태 설정
        all_initial = self._config.get_all_initial_states()
        states: dict[str, AgentState] = {}
        for agent_state in all_initial:
            states[agent_state.agent_id] = self._apply_overrides(agent_state)

        agent_ids = list(states.keys())
        scheduler = AgentScheduler(agent_ids, self._scheduler_mode)

        # behavior_profiles deep copy (cooldown 상태 격리)
        profiles = {
            aid: p.model_copy(deep=True) for aid, p in self._behavior_profiles.items()
        }

        # 환경
        environment = self._config.environment.model_copy(deep=True)

        # Hazard 엔진 (모든 에이전트 공유)
        hazard_events = [e.model_copy(deep=True) for e in self._config.hazard_events]
        hazard_engine = HazardEngine(hazard_events)

        # 트리거 엔진
        triggers = [t.model_copy(deep=True) for t in self._config.triggers]
        trigger_engine = TriggerEngine(triggers)

        # Legacy 스케줄러 (canonical_timeline 이벤트용)
        event_scheduler = EventScheduler(
            self._config.events, self._config.interventions,
        )

        # 결과 수집
        snapshots: dict[str, dict[int, AgentState]] = {
            aid: {0: s} for aid, s in states.items()
        }
        action_histories: dict[str, list[ActionRecord]] = {
            aid: [] for aid in agent_ids
        }
        fired_triggers: list[dict[str, Any]] = []
        fired_events: list[dict[str, Any]] = []

        for tick in range(1, self._config.max_tick + 1):
            # tick 갱신
            for aid in agent_ids:
                states[aid] = states[aid].model_copy(update={"tick": tick})

            # 1a. 정경 개입 (모든 에이전트에 적용)
            for intervention in event_scheduler.get_interventions_for_tick(tick):
                for aid in agent_ids:
                    states[aid] = intervention.apply(states[aid])

            # 1b. External events (tick 고정, v1.2 phase-linked에서 활용)
            # effects는 primary agent(initial_state)에 적용, action_options는 행동 선택지에.
            primary_id_for_events = agent_ids[0] if agent_ids else None
            for event in event_scheduler.get_events_for_tick(tick):
                if primary_id_for_events is None:
                    continue
                # preconditions 평가
                if not all(
                    p.evaluate(states[primary_id_for_events])
                    for p in event.preconditions
                ):
                    continue
                # effects 적용 (primary agent)
                for effect in event.effects:
                    target = effect.target_agent_id or primary_id_for_events
                    if target in states:
                        states[target] = effect.apply(states[target])
                # action_options가 있으면 확률적 선택
                if event.action_options:
                    chosen = decide_action(
                        states[primary_id_for_events],
                        list(event.action_options),
                        rng,
                        environment,
                        policy=self._policies.get(primary_id_for_events),
                    )
                    if chosen is not None:
                        action_histories[primary_id_for_events].append(ActionRecord(
                            tick=tick, event_id=event.event_id,
                            chosen_action=chosen.action_id, weights={},
                        ))
                        for effect in chosen.effects:
                            target = effect.target_agent_id or primary_id_for_events
                            if target in states:
                                states[target] = effect.apply(states[target])
                fired_events.append({"event_id": event.event_id, "tick": tick})

            # 2. 에이전트별 자발적 행동
            recent_actions: dict[str, list[str]] = {aid: [] for aid in agent_ids}
            activation_order = scheduler.get_activation_order(rng)

            for aid in activation_order:
                profile = profiles.get(aid)
                if profile is None:
                    continue
                action = profile.select_action(
                    tick, states[aid], rng, environment,
                    policy=self._policies.get(aid),
                )
                if action is not None:
                    action.record_perform(tick)
                    recent_actions[aid].append(action.action_id)
                    # 행동 효과 적용
                    for effect in action.effects:
                        if effect.target_agent_id and effect.target_agent_id in states:
                            states[effect.target_agent_id] = effect.apply(
                                states[effect.target_agent_id]
                            )
                        else:
                            states[aid] = effect.apply(states[aid])
                    # TRACE_SCHEMA §2.2: weight breakdown 기록 (선택된 action)
                    try:
                        breakdown = action.weight_formula.compute_weight_breakdown(
                            states[aid], environment,
                        )
                    except Exception:
                        breakdown = None
                    action_histories[aid].append(ActionRecord(
                        tick=tick, event_id="voluntary",
                        chosen_action=action.action_id, weights={},
                        weight_breakdown=breakdown,
                        visible_signal=action.visible_signal,
                        observable_from=list(action.observable_from),
                    ))

            # 3. 트리거 평가
            fired_trigs = trigger_engine.evaluate_tick(tick, states, recent_actions)
            for trig in fired_trigs:
                # TRACE_SCHEMA §2.1: state_conditions_satisfied 스냅샷
                try:
                    conditions_snapshot = trig.snapshot_conditions(
                        states, recent_actions,
                    )
                except Exception:
                    conditions_snapshot = []
                fired_triggers.append({
                    "trigger_id": trig.trigger_id, "tick": tick,
                    "event_template_id": trig.event_template_id,
                    "state_conditions_satisfied": conditions_snapshot,
                })
                # 트리거 효과 적용
                for effect_data in trig.effects_on_fire:
                    effect = StateEffect.model_validate(effect_data)
                    target = effect.target_agent_id
                    if target and target in states:
                        states[target] = effect.apply(states[target])

            # 4. Hazard 이벤트 평가 (첫 에이전트 기준 -- 향후 에이전트별 확장)
            # v1.2: per-event base_rate_unit=per_hour일 경우 tick_scale_hours 전달
            primary_id = agent_ids[0]
            fired = hazard_engine.evaluate_tick(
                tick, states[primary_id], rng, environment=environment,
                tick_scale_hours=self._config.tick_scale_hours,
            )
            for hazard_ev in fired:
                fired_events.append({"event_id": hazard_ev.event_id, "tick": tick})

                # 행동 결정 (primary agent)
                if hazard_ev.action_options_on_fire:
                    options = [
                        ActionOption.model_validate(o)
                        for o in hazard_ev.action_options_on_fire
                    ]
                    chosen = decide_action(
                        states[primary_id], options, rng, environment,
                        policy=self._policies.get(primary_id),
                    )
                    if chosen:
                        action_histories[primary_id].append(ActionRecord(
                            tick=tick, event_id=hazard_ev.event_id,
                            chosen_action=chosen.action_id, weights={},
                        ))
                        for effect in chosen.effects:
                            states[primary_id] = effect.apply(states[primary_id])

                # 이벤트 효과 적용
                for effect_data in hazard_ev.effects_on_fire:
                    effect = StateEffect.model_validate(effect_data)
                    if effect.field_path.startswith("env."):
                        env_field = effect.field_path[4:]
                        current = getattr(environment, env_field, None)
                        if current is not None and isinstance(current, (int, float)):
                            if effect.operation == "set":
                                setattr(environment, env_field, effect.value)
                            elif effect.operation == "add":
                                setattr(environment, env_field,
                                        clamp(current + float(effect.value)))
                    else:
                        target = effect.target_agent_id or primary_id
                        if target in states:
                            states[target] = effect.apply(states[target])

            # 5. 노이즈 주입 + 규칙 적용 (에이전트별)
            for aid in agent_ids:
                if self._config.state_noise_scale > 0:
                    states[aid] = self._apply_noise(states[aid], rng)

                context = RuleContext(
                    tick=tick, delta_tick=1, rng=rng,
                    dt_hours=self._config.tick_scale_hours,
                    all_agents=states,
                )
                states[aid] = self._rule_engine.apply_all(states[aid], context)

            # 5b. [v1.0] Latent drive encoding (drive_model 있을 때만)
            if self._drive_model is not None and getattr(
                self._drive_model, "is_active", lambda: False
            )():
                for aid in agent_ids:
                    drive = self._drive_model.encode_safe(
                        states[aid],
                        history=action_histories.get(aid, [])[-10:],
                    )
                    if drive is not None:
                        states[aid] = states[aid].model_copy(
                            update={"drive_state": drive}
                        )

            # 6. 환경 동적 규칙
            env_rule = EnvironmentDynamicsRule()
            environment = env_rule.apply(environment, tick)

            # 7. 스냅샷 (이벤트 tick 또는 주기적)
            tick_had_event = bool(fired_trigs) or bool(fired)
            for aid in agent_ids:
                if tick_had_event or tick % 10 == 0:
                    snapshots[aid][tick] = states[aid]

        # 최종 스냅샷
        for aid in agent_ids:
            snapshots[aid][self._config.max_tick] = states[aid]

        # 에이전트별 체크포인트 평가
        checkpoint_results: dict[str, list[CheckpointResult]] = {}
        match_rates: dict[str, float] = {}
        for aid in agent_ids:
            agent_cps = self._checkpoints.get(aid, [])
            if agent_cps:
                cp_results = [
                    evaluate_checkpoint(cp, snapshots[aid], action_histories.get(aid, []))
                    for cp in agent_cps
                ]
                checkpoint_results[aid] = cp_results
                match_rates[aid] = compute_match_rate(cp_results, agent_cps)

        return MultiAgentResult(
            seed=effective_seed,
            final_states=states,
            state_snapshots=snapshots,
            action_histories=action_histories,
            checkpoint_results=checkpoint_results,
            canonical_match_rates=match_rates,
            fired_triggers=fired_triggers,
            fired_events=fired_events,
        )

    def _apply_noise(self, state: AgentState, rng: random.Random) -> AgentState:
        """감정 상태에 가우시안 노이즈 주입."""
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
