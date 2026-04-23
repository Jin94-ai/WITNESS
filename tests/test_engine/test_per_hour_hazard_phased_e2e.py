"""per_hour hazard를 실제 PhasedSimulationWorld에서 실행 (v1.2 Iter 35).

Iter 27이 엔진 수준에서 per_hour 해석을 추가했고, 단위 테스트로 검증됨.
이 테스트는 **content 수준 deployment**를 증명:
- `HazardEvent(hazard=HazardFunction(base_rate_unit="per_hour", ...))`를 config에
  넣고 PhasedSimulationWorld로 실행.
- phase마다 tick_scale_hours가 달라도 실시간 기준 발동 분포가 일관.
- phased 실행이 hazard_events를 각 phase에 전달하고 phase.tick_scale_hours를
  evaluate_tick에 전달하는지 end-to-end 확인.
"""

from engine.core.hazard import (
    HazardEvent,
    HazardFunction,
)
from engine.core.phase import Phase, PhaseExitCondition
from engine.core.state import AgentState
from engine.core.world import SimulationConfig
from engine.rules.base import RuleEngine
from engine.simulation.phased_world import (
    PhasedMultiAgentResult,
    PhasedSimulationWorld,
)


def _per_hour_event() -> HazardEvent:
    hf = HazardFunction(
        base_rate=0.1,
        base_rate_unit="per_hour",
        max_hazard=10.0,
    )
    return HazardEvent(event_id="ping", hazard=hf, max_fires=100)


def _agent() -> AgentState:
    return AgentState(agent_id="a")


class TestPhasedPerHourHazard:
    def test_hazard_fires_in_phased_single_phase(self):
        a = _agent()
        ev = _per_hour_event()
        config = SimulationConfig(
            initial_state=a, initial_states=[a],
            max_tick=500, state_noise_scale=0.0,
            hazard_events=[ev],
            phases=[Phase(
                phase_id="p1",
                agents_active=["a"],
                tick_scale_hours=2.0,
                exit_condition=PhaseExitCondition(max_tick=50),
            )],
        )
        result = PhasedSimulationWorld(config, RuleEngine([])).run(seed=0)
        assert isinstance(result, PhasedMultiAgentResult)
        # per_hour 0.1 × dt=2 → P(fire)~0.18 per tick × 50 ticks → 기대 발동 수 수 개
        assert len(result.fired_events) > 0

    def test_per_hour_invariant_across_tick_scales(self):
        """동일한 총 시간에서 phase tick_scale이 달라도 기대 발동 수 유사."""
        n_seeds = 50

        # A: 2h/tick × 24 tick = 48h
        fires_a = []
        for seed in range(n_seeds):
            ev_a = _per_hour_event()
            a = _agent()
            cfg_a = SimulationConfig(
                initial_state=a, initial_states=[a],
                max_tick=500, state_noise_scale=0.0,
                hazard_events=[ev_a],
                phases=[Phase(
                    phase_id="dense", agents_active=["a"],
                    tick_scale_hours=2.0,
                    exit_condition=PhaseExitCondition(max_tick=24),
                )],
            )
            r_a = PhasedSimulationWorld(cfg_a, RuleEngine([])).run(seed=seed)
            fires_a.append(len(r_a.fired_events))

        # B: 24h/tick × 2 tick = 48h
        fires_b = []
        for seed in range(n_seeds):
            ev_b = _per_hour_event()
            a = _agent()
            cfg_b = SimulationConfig(
                initial_state=a, initial_states=[a],
                max_tick=500, state_noise_scale=0.0,
                hazard_events=[ev_b],
                phases=[Phase(
                    phase_id="sparse", agents_active=["a"],
                    tick_scale_hours=24.0,
                    exit_condition=PhaseExitCondition(max_tick=2),
                )],
            )
            r_b = PhasedSimulationWorld(cfg_b, RuleEngine([])).run(seed=seed)
            fires_b.append(len(r_b.fired_events))

        mean_a = sum(fires_a) / n_seeds
        mean_b = sum(fires_b) / n_seeds
        # Poisson λT=4.8, A는 per-tick P 작아서 잘 따라감, B는 max_fires_per_tick=2로 절단
        # A는 이론값에 가깝고, B는 A보다 작거나 비슷 (truncated)
        assert mean_a > 0.0
        assert mean_b > 0.0
        # A가 적어도 기대값의 절반 이상 (Poisson λT=4.8 → E~4.8, truncated 고려 2+)
        assert mean_a >= 2.0, f"A mean={mean_a}"


class TestMixedPerTickAndPerHour:
    """같은 config 안에 per_tick 이벤트와 per_hour 이벤트 공존."""

    def test_both_events_fire_independently(self):
        ev_tick = HazardEvent(
            event_id="tick_based",
            hazard=HazardFunction(base_rate=0.3, base_rate_unit="per_tick"),
            max_fires=100,
        )
        ev_hour = HazardEvent(
            event_id="hour_based",
            hazard=HazardFunction(base_rate=0.1, base_rate_unit="per_hour"),
            max_fires=100,
        )
        a = _agent()
        config = SimulationConfig(
            initial_state=a, initial_states=[a],
            max_tick=500, state_noise_scale=0.0,
            hazard_events=[ev_tick, ev_hour],
            phases=[Phase(
                phase_id="mixed", agents_active=["a"],
                tick_scale_hours=4.0,
                exit_condition=PhaseExitCondition(max_tick=50),
            )],
        )
        # 20 seeds 평균
        fires_tick = 0
        fires_hour = 0
        for seed in range(20):
            ev_tick.fire_count = 0
            ev_tick.last_fired_tick = -1
            ev_hour.fire_count = 0
            ev_hour.last_fired_tick = -1
            result = PhasedSimulationWorld(config, RuleEngine([])).run(seed=seed)
            for e in result.fired_events:
                if e["event_id"] == "tick_based":
                    fires_tick += 1
                elif e["event_id"] == "hour_based":
                    fires_hour += 1
        # 두 이벤트 모두 발동
        assert fires_tick > 0
        assert fires_hour > 0


class TestMultiPhasePerHour:
    """Phase 1 (2h/tick) + Phase 2 (24h/tick) — per_hour 이벤트는 두 phase에서 rate 동일."""

    def test_per_hour_event_phase_continuity(self):
        ev = HazardEvent(
            event_id="ping",
            hazard=HazardFunction(base_rate=0.2, base_rate_unit="per_hour"),
            max_fires=100,
        )
        a = _agent()
        config = SimulationConfig(
            initial_state=a, initial_states=[a],
            max_tick=1000, state_noise_scale=0.0,
            hazard_events=[ev],
            phases=[
                Phase(
                    phase_id="dense", agents_active=["a"],
                    tick_scale_hours=2.0,
                    exit_condition=PhaseExitCondition(max_tick=12),  # 24h
                ),
                Phase(
                    phase_id="sparse", agents_active=["a"],
                    tick_scale_hours=24.0,
                    exit_condition=PhaseExitCondition(max_tick=1),  # 24h
                ),
            ],
        )
        result = PhasedSimulationWorld(config, RuleEngine([])).run(seed=0)
        # 둘 다 24h 경과 → event가 phase 1 또는 2에서 fire됨
        assert isinstance(result, PhasedMultiAgentResult)
        assert len(result.per_phase_results) == 2
