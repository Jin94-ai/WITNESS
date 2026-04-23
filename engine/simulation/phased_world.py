"""Phase-linked continuous life architecture (v1.2 MVP — Iteration 4).

여러 phase를 순차 실행하고, 각 phase 종료 시 PhaseHandoffSpec에 따라
state를 다음 phase의 초기값으로 전달. 단일 phase 케이스는 기존
SimulationWorld에 위임 (backward compat).

reviewer 피드백 반영:
- 표면은 단일 연속 시뮬레이터로 보이지만 내부는 stitched
- 각 phase는 phase-local MultiAgentResult를 생성, 이후 합침
- phase 경계에서 state는 handoff mapping에 따라 선별적으로 전달
  (slow_state는 irreversible이므로 기본 carry, fast state는 reset)
- canonical intervention은 phase 내부에서만 적용 (reparameterization
  shock; 완전 회복 아님)

참조: frolicking-sleeping-whistle.md §2.2-2.7
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Literal

from engine.core.action import AgentBehaviorProfile
from engine.core.phase import Phase, PhaseHandoffSpec
from engine.core.state import AgentState, get_nested_value, set_nested_value
from engine.core.world import SimulationConfig
from engine.rules.base import RuleEngine
from engine.simulation.checkpoint import Checkpoint
from engine.simulation.world import MultiAgentResult, SimulationWorld


class PhasedMultiAgentResult(MultiAgentResult):
    """Phase-linked 실행의 결과.

    단일 MultiAgentResult의 확장: 각 phase별 부분 결과 목록 + 전체 요약.
    기존 MultiAgentResult API와 호환되도록 action_histories 등은 전체 merged.

    Attributes:
        per_phase_results: phase_id → 해당 phase의 MultiAgentResult
        phase_boundaries: list[(phase_id, start_tick_global, end_tick_global)]
    """

    per_phase_results: dict[str, MultiAgentResult] = {}  # noqa: RUF012
    phase_boundaries: list[dict[str, Any]] = []  # noqa: RUF012

    def extract_absolute_trajectory(
        self,
        agent_id: str,
        field_path: str,
    ) -> list[Any]:
        """phase-variable tick을 arc 시작 이후 hours 좌표계로 변환한 시계열.

        reviewer 지적 대응: 장기 분석은 tick이 아닌 absolute hours 기준이어야 함.
        내부적으로 `engine.simulation.time_axis.extract_field_trajectory_absolute`
        위임.

        Args:
            agent_id: 추적할 agent id.
            field_path: dot-separated 필드 경로 (e.g., "emotions.awe",
                "domain_state.obedience_maturity").

        Returns:
            hours 오름차순으로 정렬된 `TimePoint` list.
        """
        from engine.simulation.time_axis import extract_field_trajectory_absolute

        per_phase_snapshots = {
            phase_id: result.state_snapshots
            for phase_id, result in self.per_phase_results.items()
        }
        return extract_field_trajectory_absolute(
            per_phase_snapshots,
            self.phase_boundaries,
            agent_id,
            field_path,
        )

    def phase_hours_table(self) -> list[dict[str, Any]]:
        """phase_boundaries를 absolute hours 좌표계로 확장한 표.

        `convert_phase_boundaries_to_hours` 위임. 각 phase가
        `start_hours`, `end_hours`, `duration_hours`를 포함하여 반환.
        장기 분석/시각화에 편리.

        Returns:
            각 원소가 원본 phase_boundary에 start_hours/end_hours/
            duration_hours 추가된 dict.
        """
        from engine.simulation.time_axis import convert_phase_boundaries_to_hours

        return convert_phase_boundaries_to_hours(self.phase_boundaries)


def apply_handoff(
    prev_final_states: dict[str, AgentState],
    next_initial_states: dict[str, AgentState],
    spec: PhaseHandoffSpec | None,
) -> dict[str, AgentState]:
    """Phase N 종료 상태로 Phase N+1 초기 상태를 갱신.

    Args:
        prev_final_states: Phase N의 final_states.
        next_initial_states: Phase N+1의 config 기본 initial_states (아직 handoff 전).
        spec: 전달 규칙. None이면 변경 없이 next_initial_states 반환.

    Returns:
        handoff 적용된 새 dict[agent_id -> AgentState].

    규칙:
    - spec.carry_all_slow_state=True면 prev의 모든 agent slow_state를 next에 주입.
    - spec.mappings의 각 FieldMapping은 원본 field_path 값을 target으로 복사.
      source가 None이면 default_if_missing 사용, 그것도 None이면 skip.
    - next에 없는 agent_id는 prev에서 그대로 복제 (persistent agents).
    """
    if spec is None:
        return next_initial_states

    # 시작점: next의 깊은 복사
    result: dict[str, AgentState] = {
        aid: s.model_copy(deep=True) for aid, s in next_initial_states.items()
    }

    # prev에 있지만 next에 없는 agent는 그대로 복제 (life arc 연속성)
    for aid, state in prev_final_states.items():
        if aid not in result:
            result[aid] = state.model_copy(deep=True)

    # 1. slow_state carry-all (irreversible field 기본 전달)
    if spec.carry_all_slow_state:
        for aid, prev_state in prev_final_states.items():
            if aid not in result:
                continue
            # Pydantic model deep copy via model_copy(update=...)
            result[aid] = result[aid].model_copy(
                update={"slow_state": prev_state.slow_state.model_copy(deep=True)},
            )

    # 2. 개별 field mapping
    for mapping in spec.mappings:
        src = prev_final_states.get(mapping.source_agent_id)
        if src is None:
            continue
        value = get_nested_value(src, mapping.source_field_path)
        if value is None:
            value = mapping.default_if_missing
        if value is None:
            continue

        tgt = result.get(mapping.target_agent_id)
        if tgt is None:
            continue
        result[mapping.target_agent_id] = set_nested_value(
            tgt, mapping.target_field_path, value,
        )

    return result


def _merge_phase_result(
    merged: PhasedMultiAgentResult,
    phase_result: MultiAgentResult,
    phase: Phase,
    global_tick_offset: int,
) -> None:
    """단일 phase 결과를 전체 merged result에 추가.

    phase의 local tick에 global_tick_offset을 더해 global tick으로 변환.
    per_phase_results에는 원본 phase-local 결과를 저장.
    """
    merged.per_phase_results[phase.phase_id] = phase_result

    # final_states: 항상 마지막 phase의 값으로 덮어씀
    merged.final_states.update(phase_result.final_states)

    # state_snapshots: tick을 global로 변환해 merge
    for aid, snaps in phase_result.state_snapshots.items():
        if aid not in merged.state_snapshots:
            merged.state_snapshots[aid] = {}
        for local_tick, state in snaps.items():
            merged.state_snapshots[aid][local_tick + global_tick_offset] = state

    # action_histories: global tick으로 변환
    for aid, records in phase_result.action_histories.items():
        if aid not in merged.action_histories:
            merged.action_histories[aid] = []
        for rec in records:
            # model_copy with updated tick
            new_rec = rec.model_copy(update={"tick": rec.tick + global_tick_offset})
            merged.action_histories[aid].append(new_rec)

    # fired_triggers: global tick
    for t in phase_result.fired_triggers:
        t_copy = dict(t)
        t_copy["tick"] = t.get("tick", 0) + global_tick_offset
        t_copy["phase_id"] = phase.phase_id
        merged.fired_triggers.append(t_copy)

    # fired_events: global tick
    for e in phase_result.fired_events:
        e_copy = dict(e)
        e_copy["tick"] = e.get("tick", 0) + global_tick_offset
        e_copy["phase_id"] = phase.phase_id
        merged.fired_events.append(e_copy)

    # checkpoint_results: 그대로 append (phase-local 의미 유지)
    for aid, cps in phase_result.checkpoint_results.items():
        if aid not in merged.checkpoint_results:
            merged.checkpoint_results[aid] = []
        merged.checkpoint_results[aid].extend(cps)


class PhasedSimulationWorld:
    """Phase-linked continuous life architecture.

    단일 phase (config.phases=None or empty): 기존 SimulationWorld에 위임.
    다중 phase: 순차 실행 + handoff.

    reviewer 피드백: 표면은 연속, 내부는 stitched local simulators.

    Args:
        config: SimulationConfig. phases가 None이면 단일 phase 모드.
        rule_engine: 공유 RuleEngine.
        behavior_profiles: agent별 behavior profile.
        checkpoints: optional checkpoint 정의.
        scheduler_mode: 에이전트 스케줄 모드.
        drive_model: v1.0+ LatentDriveModel (optional).
    """

    def __init__(
        self,
        config: SimulationConfig,
        rule_engine: RuleEngine,
        behavior_profiles: dict[str, AgentBehaviorProfile] | None = None,
        checkpoints: dict[str, list[Checkpoint]] | None = None,
        scheduler_mode: Literal["sequential", "random", "simultaneous"] = "random",
        drive_model: Any = None,
    ) -> None:
        self._config = config
        self._rule_engine = rule_engine
        self._behavior_profiles = behavior_profiles or {}
        self._checkpoints = checkpoints or {}
        self._scheduler_mode = scheduler_mode
        self._drive_model = drive_model

    def run(self, seed: int | None = None) -> MultiAgentResult:
        """실행. 단일 phase면 기존 동작, 다중 phase면 stitched life arc."""
        if not self._config.is_phase_linked:
            # backward compat: 기존 SimulationWorld 단일 phase
            world = SimulationWorld(
                self._config, self._rule_engine,
                behavior_profiles=self._behavior_profiles,
                checkpoints=self._checkpoints,
                scheduler_mode=self._scheduler_mode,
                drive_model=self._drive_model,
            )
            return world.run(seed=seed)

        # phase-linked 실행
        return self._run_phase_linked(seed)

    def _run_phase_linked(self, seed: int | None) -> PhasedMultiAgentResult:
        """다중 phase 순차 실행."""
        phases = self._config.phases or []
        merged = PhasedMultiAgentResult(seed=seed)
        global_offset = 0

        # 첫 phase의 initial_states는 config에서
        current_states: dict[str, AgentState] = {
            s.agent_id: s.model_copy(deep=True)
            for s in self._config.get_all_initial_states()
        }

        for i, phase in enumerate(phases):
            # phase-local config 생성
            phase_config = self._build_phase_config(phase, current_states)

            # phase 실행 (기존 SimulationWorld)
            phase_world = SimulationWorld(
                phase_config, self._rule_engine,
                behavior_profiles=self._behavior_profiles,
                checkpoints=self._checkpoints,
                scheduler_mode=self._scheduler_mode,
                drive_model=self._drive_model,
            )
            phase_result = phase_world.run(seed=seed)

            # merge into global result
            _merge_phase_result(merged, phase_result, phase, global_offset)
            merged.phase_boundaries.append({
                "phase_id": phase.phase_id,
                "start_tick": global_offset,
                "end_tick": global_offset + phase_config.max_tick,
                "tick_scale_hours": phase.tick_scale_hours,
            })
            global_offset += phase_config.max_tick

            # handoff: phase.handoff_to_next를 사용해 다음 phase 초기값 준비.
            # next_defaults 계산 시 *Phase N의 final_states*를 기준으로 사용 —
            # current_states에는 Phase N에 활성화되지 않았던 agent가 남아있을 수 있음.
            if i + 1 < len(phases):
                next_phase = phases[i + 1]
                next_defaults = self._phase_initial_defaults(
                    next_phase, phase_result.final_states,
                )
                current_states = apply_handoff(
                    phase_result.final_states,
                    next_defaults,
                    phase.handoff_to_next,
                )
            else:
                # 마지막 phase: final_states 그대로
                current_states = phase_result.final_states

        return merged

    def _build_phase_config(
        self,
        phase: Phase,
        current_states: dict[str, AgentState],
    ) -> SimulationConfig:
        """phase 별 SimulationConfig 생성.

        - initial_states: current_states (handoff 이후 값)
        - max_tick: phase.exit_condition.max_tick (없으면 config.max_tick)
        - tick_scale_hours: phase.tick_scale_hours
        - events: phase.canonical_events_path 있으면 로드, 없으면 config.events
        - phases: None (재귀 방지, phase 내부는 단일 phase 모드)
        """
        max_tick = (
            phase.exit_condition.max_tick
            if phase.exit_condition.max_tick is not None
            else self._config.max_tick
        )

        # 활성 agents 필터링
        active_ids = (
            phase.agents_active
            if phase.agents_active is not None
            else list(current_states.keys())
        )
        active_states = [
            current_states[aid] for aid in active_ids if aid in current_states
        ]

        if not active_states:
            # fallback: 전체 유지 (안전 장치)
            active_states = list(current_states.values())

        # v1.2 Iter 20: phase-specific canonical events 로드
        # canonical_events_path가 설정되면 해당 파일에서 events 로드 → config.events override
        phase_events = deepcopy(self._config.events)
        if phase.canonical_events_path is not None:
            try:
                from pathlib import Path

                from engine.io.loader import load_events
                phase_events = load_events(Path(phase.canonical_events_path))
            except (FileNotFoundError, ValueError, OSError):
                # 로드 실패 시 상위 config.events fallback
                pass

        # 재귀 방지를 위해 phases=None, tick_scale_hours=phase 값
        return SimulationConfig(
            seed=self._config.seed,
            max_tick=max_tick,
            initial_state=active_states[0],
            initial_states=active_states,
            triggers=deepcopy(self._config.triggers),
            events=phase_events,
            interventions=deepcopy(self._config.interventions),
            hazard_events=deepcopy(self._config.hazard_events),
            environment=self._config.environment.model_copy(deep=True),
            state_noise_scale=self._config.state_noise_scale,
            parameter_overrides=dict(self._config.parameter_overrides),
            tick_scale_hours=phase.tick_scale_hours,
            phases=None,  # 재귀 방지
        )

    def _phase_initial_defaults(
        self,
        next_phase: Phase,
        current_states: dict[str, AgentState],
    ) -> dict[str, AgentState]:
        """다음 phase 기본 initial_states (handoff 적용 전).

        v1.2 Iter 17: Phase boundary agent 소개 지원.
        - next_phase.agents_active가 None이면 current_states 그대로
        - 있으면 filter + current에 없는 agent는 SimulationConfig.initial_states에서 로드

        예: 특정 phase의 agents_active=["<a>", "<b>"]이고
        current_states에 <b> 없으면, config.initial_states에서 <b> 원본 꺼내 추가.
        이로써 시나리오 중간 phase에서 새 agent 등장 가능.
        """
        if next_phase.agents_active is None:
            return {aid: s.model_copy(deep=True) for aid, s in current_states.items()}

        result: dict[str, AgentState] = {}
        # config 전체 initial_states에서 fallback용 맵
        config_initial_map = {
            s.agent_id: s for s in self._config.get_all_initial_states()
        }
        for aid in next_phase.agents_active:
            if aid in current_states:
                # 이전 phase에서 carry-forward
                result[aid] = current_states[aid].model_copy(deep=True)
            elif aid in config_initial_map:
                # phase boundary에서 새로 소개되는 agent
                result[aid] = config_initial_map[aid].model_copy(deep=True)
            # 둘 다 아니면 skip (경고 없이 무시)
        return result
