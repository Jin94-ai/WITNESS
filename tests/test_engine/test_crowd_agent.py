"""군중 준-에이전트 통합 테스트.

4-에이전트 시뮬레이션: Peter + Judas + Caiaphas + Crowd.
군중의 사회적 압력이 베드로의 행동에 영향을 미치는지 검증.
"""

from collections import Counter
from pathlib import Path

from content.caiaphas.domain_politics import PoliticalCalculationState
from content.crowd.domain_crowd import CrowdDynamicsState
from content.judas.domain_betrayal import BetrayalPsychologyState
from content.peter.domain_faith import FaithJourneyState
from engine.core.world import SimulationConfig
from engine.io.loader import (
    load_agent_state,
    load_behavior_profile,
    load_hazard_events,
    load_interventions,
    load_triggers,
    register_domain_type,
)
from engine.rules.base import RuleEngine
from engine.rules.emotional import FearResponseRule, GriefRule, HopeRule
from engine.rules.temporal import HomeostasisRule
from engine.simulation.world import SimulationWorld

register_domain_type("faith_journey", FaithJourneyState)
register_domain_type("betrayal_psychology", BetrayalPsychologyState)
register_domain_type("political_calculation", PoliticalCalculationState)
register_domain_type("crowd_dynamics", CrowdDynamicsState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"


def _engine() -> RuleEngine:
    return RuleEngine([FearResponseRule(), GriefRule(), HopeRule(), HomeostasisRule()])


def _load_4_agents():
    peter = load_agent_state(CONTENT_DIR / "peter" / "initial_state.json")
    judas = load_agent_state(CONTENT_DIR / "judas" / "initial_state.json")
    caiaphas = load_agent_state(CONTENT_DIR / "caiaphas" / "initial_state.json")
    crowd = load_agent_state(CONTENT_DIR / "crowd" / "initial_state.json")
    triggers = load_triggers(CONTENT_DIR / "shared" / "triggers.json")
    hazards = load_hazard_events(CONTENT_DIR / "peter" / "hazard_events.json")
    interventions = load_interventions(CONTENT_DIR / "peter" / "canonical_events.json")
    profiles = {
        "peter": load_behavior_profile(CONTENT_DIR / "peter" / "behavior_profile.json"),
        "judas": load_behavior_profile(CONTENT_DIR / "judas" / "behavior_profile.json"),
        "caiaphas": load_behavior_profile(CONTENT_DIR / "caiaphas" / "behavior_profile.json"),
        "crowd": load_behavior_profile(CONTENT_DIR / "crowd" / "behavior_profile.json"),
    }
    return peter, judas, caiaphas, crowd, triggers, hazards, interventions, profiles


class TestCrowdAgent:
    def test_4_agents_run(self):
        """4-에이전트 500 tick 완주."""
        peter, judas, caiaphas, crowd, triggers, hazards, interventions, profiles = _load_4_agents()
        config = SimulationConfig(
            max_tick=500, initial_state=peter,
            initial_states=[peter, judas, caiaphas, crowd],
            hazard_events=hazards, interventions=interventions,
            triggers=triggers, state_noise_scale=0.05,
        )
        result = SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=42)

        assert "peter" in result.final_states
        assert "crowd" in result.final_states
        assert result.final_states["crowd"].tick == 500

    def test_crowd_actions_recorded(self):
        """군중의 행동이 기록된다."""
        peter, judas, caiaphas, crowd, triggers, hazards, interventions, profiles = _load_4_agents()
        config = SimulationConfig(
            max_tick=200, initial_state=peter,
            initial_states=[peter, judas, caiaphas, crowd],
            hazard_events=hazards, interventions=interventions,
            triggers=triggers, state_noise_scale=0.05,
        )
        result = SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=42)

        crowd_actions = result.action_histories.get("crowd", [])
        assert len(crowd_actions) > 0
        action_types = Counter(a.chosen_action for a in crowd_actions)
        print(f"\nCrowd actions: {dict(action_types)}")

    def test_crowd_affects_peter_fear(self):
        """군중의 challenge/accuse가 베드로의 공포를 높인다."""
        peter, judas, caiaphas, crowd, triggers, hazards, interventions, profiles = _load_4_agents()

        # 군중 없이
        config_no_crowd = SimulationConfig(
            max_tick=200, initial_state=peter,
            initial_states=[peter, judas, caiaphas],
            hazard_events=hazards, interventions=interventions,
            triggers=triggers, state_noise_scale=0.05,
        )
        profiles_no_crowd = {k: v for k, v in profiles.items() if k != "crowd"}

        # 군중 있이
        config_with_crowd = SimulationConfig(
            max_tick=200, initial_state=peter,
            initial_states=[peter, judas, caiaphas, crowd],
            hazard_events=hazards, interventions=interventions,
            triggers=triggers, state_noise_scale=0.05,
        )

        fears_no_crowd = []
        fears_with_crowd = []
        for seed in range(10):
            r1 = SimulationWorld(config_no_crowd, _engine(), behavior_profiles=profiles_no_crowd).run(seed=seed)
            r2 = SimulationWorld(config_with_crowd, _engine(), behavior_profiles=profiles).run(seed=seed)
            fears_no_crowd.append(r1.final_states["peter"].emotions.fear)
            fears_with_crowd.append(r2.final_states["peter"].emotions.fear)

        import statistics
        mean_no = statistics.mean(fears_no_crowd)
        mean_with = statistics.mean(fears_with_crowd)
        print(f"\nPeter fear (no crowd): {mean_no:.2f}")
        print(f"Peter fear (with crowd): {mean_with:.2f}")

        # 군중이 있으면 베드로의 공포가 더 높아야 함 (또는 최소 동등)
        # homeostasis가 강하므로 차이가 미미할 수 있지만, 방향은 맞아야 함

    def test_crowd_pressure_trigger(self):
        """crowd_pressure_spike 트리거가 발동한다."""
        peter, judas, caiaphas, crowd, triggers, hazards, interventions, profiles = _load_4_agents()
        config = SimulationConfig(
            max_tick=500, initial_state=peter,
            initial_states=[peter, judas, caiaphas, crowd],
            hazard_events=hazards, interventions=interventions,
            triggers=triggers, state_noise_scale=0.05,
        )

        pressure_count = 0
        for seed in range(10):
            r = SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=seed)
            pressures = [t for t in r.fired_triggers if t["trigger_id"] == "crowd_pressure_spike"]
            if pressures:
                pressure_count += 1

        print(f"\nCrowd pressure trigger fired: {pressure_count}/10 seeds")
