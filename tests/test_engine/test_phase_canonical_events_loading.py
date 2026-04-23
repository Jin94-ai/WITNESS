"""Phase.canonical_events_path 자동 로드 테스트 (v1.2 Iter 20).

각 phase의 canonical_events_path 파일이 PhasedSimulationWorld에서
자동 로드되어 해당 phase 내부에서만 fire되는지 검증.
"""

from pathlib import Path

import pytest

from content.peter.domain_faith import FaithJourneyState
from engine.core.phase import Phase, PhaseExitCondition, PhaseHandoffSpec
from engine.core.world import SimulationConfig
from engine.io.loader import load_agent_state, register_domain_type
from engine.rules.base import RuleEngine
from engine.rules.emotional import (
    ConfusionRule,
    FearResponseRule,
    GriefRule,
    HopeRule,
    LoveRule,
)
from engine.rules.temporal import HomeostasisRule
from engine.simulation.phased_world import (
    PhasedMultiAgentResult,
    PhasedSimulationWorld,
)

CONTENT = Path(__file__).resolve().parent.parent.parent / "content"


def _rules() -> RuleEngine:
    return RuleEngine([
        FearResponseRule(), HopeRule(), GriefRule(),
        ConfusionRule(), LoveRule(),
        HomeostasisRule(),
    ])


@pytest.fixture(scope="module")
def _setup():
    register_domain_type("faith_journey", FaithJourneyState)
    return None


class TestPhaseSpecificEventsLoading:
    def test_phase_loads_own_canonical_events(self, _setup):
        """Phase 1(소명)이 자체 canonical_events_path에서 events 로드."""
        peter = load_agent_state(CONTENT / "peter" / "initial_state_calling.json")
        config = SimulationConfig(
            initial_state=peter,
            initial_states=[peter],
            max_tick=200,
            state_noise_scale=0.0,
            events=[],  # 상위는 비어있음
            phases=[
                Phase(
                    phase_id="01_calling",
                    agents_active=["peter"],
                    tick_scale_hours=2.0,
                    exit_condition=PhaseExitCondition(max_tick=84),
                    canonical_events_path=str(
                        CONTENT / "peter" / "phases" / "01_calling" / "canonical_events.json"
                    ),
                ),
            ],
        )
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)
        assert isinstance(result, PhasedMultiAgentResult)
        # Phase 1 실행 후 events가 fire되었는지 확인
        p1 = result.per_phase_results["01_calling"]
        # 소명 phase 5 events 중 일부 fire
        assert len(p1.fired_events) >= 3
        # awe 급상승 확인 (기적 어획 event 효과)
        assert p1.final_states["peter"].emotions.awe >= 3.0
        # obedience_maturity 누적
        assert p1.final_states["peter"].domain_state.obedience_maturity > 0.0

    def test_two_phases_load_different_events(self, _setup):
        """Phase 1과 Phase 3가 각자 다른 canonical_events 로드."""
        peter = load_agent_state(CONTENT / "peter" / "initial_state_calling.json")
        config = SimulationConfig(
            initial_state=peter,
            initial_states=[peter],
            max_tick=500,
            state_noise_scale=0.0,
            events=[],
            phases=[
                Phase(
                    phase_id="01_calling",
                    agents_active=["peter"],
                    tick_scale_hours=2.0,
                    exit_condition=PhaseExitCondition(max_tick=84),
                    canonical_events_path=str(
                        CONTENT / "peter" / "phases" / "01_calling" / "canonical_events.json"
                    ),
                    handoff_to_next=PhaseHandoffSpec(),
                ),
                Phase(
                    phase_id="03_confession",
                    agents_active=["peter"],
                    tick_scale_hours=2.0,
                    exit_condition=PhaseExitCondition(max_tick=150),
                    canonical_events_path=str(
                        CONTENT / "peter" / "phases" / "03_confession" / "canonical_events.json"
                    ),
                ),
            ],
        )
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)

        p1 = result.per_phase_results["01_calling"]
        p3 = result.per_phase_results["03_confession"]
        # 두 phase 모두 events fire됨
        assert len(p1.fired_events) >= 3
        assert len(p3.fired_events) >= 3

        # Phase 1 events id vs Phase 3 events id 다름
        p1_ids = {e["event_id"] for e in p1.fired_events}
        p3_ids = {e["event_id"] for e in p3.fired_events}
        assert p1_ids.isdisjoint(p3_ids)  # 교집합 없음
        # Phase 1은 calling_ prefix
        assert any(eid.startswith("calling_") for eid in p1_ids)
        # Phase 3은 conf_ prefix
        assert any(eid.startswith("conf_") for eid in p3_ids)

    def test_missing_events_file_fallback(self, _setup):
        """canonical_events_path 파일 없으면 config.events fallback, 에러 없음."""
        peter = load_agent_state(CONTENT / "peter" / "initial_state_calling.json")
        config = SimulationConfig(
            initial_state=peter,
            initial_states=[peter],
            max_tick=100,
            state_noise_scale=0.0,
            events=[],  # fallback 비어있음
            phases=[
                Phase(
                    phase_id="test",
                    tick_scale_hours=2.0,
                    exit_condition=PhaseExitCondition(max_tick=10),
                    canonical_events_path="nonexistent/path.json",
                ),
            ],
        )
        world = PhasedSimulationWorld(config, _rules())
        # 에러 없이 완주
        result = world.run(seed=0)
        p = result.per_phase_results["test"]
        assert p.final_states["peter"].tick == 10
        # events 안 fire됨 (파일 없음 + fallback 빈 리스트)
        assert len(p.fired_events) == 0

    def test_canonical_path_none_uses_config_events(self, _setup):
        """canonical_events_path=None이면 상위 config.events 그대로."""
        from engine.io.loader import load_events
        peter = load_agent_state(CONTENT / "peter" / "initial_state_calling.json")
        global_events = load_events(
            CONTENT / "peter" / "phases" / "01_calling" / "canonical_events.json",
        )
        config = SimulationConfig(
            initial_state=peter,
            initial_states=[peter],
            max_tick=200,
            state_noise_scale=0.0,
            events=global_events,  # 상위에 events 있음
            phases=[
                Phase(
                    phase_id="uses_global",
                    tick_scale_hours=2.0,
                    exit_condition=PhaseExitCondition(max_tick=84),
                    # canonical_events_path=None → 상위 events 사용
                ),
            ],
        )
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)
        p = result.per_phase_results["uses_global"]
        # 상위 events가 fire됨
        assert len(p.fired_events) >= 3


class TestBackwardCompatCanonicalPath:
    def test_legacy_scenario_still_works(self, _setup):
        """기존 v0.7 scenario (phases=None, events via config)."""
        legacy_peter = load_agent_state(CONTENT / "peter" / "initial_state.json")
        config = SimulationConfig(
            initial_state=legacy_peter,
            initial_states=[legacy_peter],
            max_tick=50,
            state_noise_scale=0.05,
        )
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)
        # PhasedMultiAgentResult가 아닌 MultiAgentResult
        from engine.simulation.world import MultiAgentResult
        assert isinstance(result, MultiAgentResult)
        assert not isinstance(result, PhasedMultiAgentResult)
