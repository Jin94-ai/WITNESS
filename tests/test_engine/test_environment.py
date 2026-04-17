"""EnvironmentState 통합 테스트."""

from engine.core.environment import EnvironmentState
from engine.core.hazard import HazardEngine, HazardEvent, HazardFactor, HazardFunction
from engine.core.state import AgentState, EmotionalState
from engine.core.world import SimulationConfig
from engine.rules.base import RuleEngine
from engine.rules.temporal import HomeostasisRule
from engine.simulation.runner import SimulationRunner


def _agent() -> AgentState:
    return AgentState(agent_id="test", emotions=EmotionalState(fear=5.0, love=7.0))


class TestEnvironmentState:
    def test_defaults(self):
        env = EnvironmentState()
        assert env.crowd_pressure == 3.0
        assert env.surveillance == 3.0

    def test_custom(self):
        env = EnvironmentState(surveillance=9.0, crowd_pressure=8.0)
        assert env.surveillance == 9.0


class TestHazardWithEnvironment:
    def test_env_factor_increases_hazard(self):
        hf = HazardFunction(
            base_rate=0.1,
            factors=[
                HazardFactor(field_path="surveillance", weight=0.5, source="environment"),
            ],
        )
        agent = _agent()
        low_env = EnvironmentState(surveillance=2.0)
        high_env = EnvironmentState(surveillance=9.0)
        h_low = hf.compute_hazard(agent, low_env)
        h_high = hf.compute_hazard(agent, high_env)
        assert h_high > h_low

    def test_env_factor_with_agent_factor(self):
        """환경 + 에이전트 factor가 동시에 작동."""
        hf = HazardFunction(
            base_rate=0.1,
            factors=[
                HazardFactor(field_path="emotions.fear", weight=0.3),
                HazardFactor(field_path="surveillance", weight=0.3, source="environment"),
            ],
        )
        agent = _agent()
        env = EnvironmentState(surveillance=7.0)
        h = hf.compute_hazard(agent, env)
        assert h > 0.1  # base_rate 이상


class TestRunnerWithEnvironment:
    def test_environment_in_config(self):
        env = EnvironmentState(surveillance=8.0, crowd_pressure=7.0)
        config = SimulationConfig(
            max_tick=20,
            initial_state=_agent(),
            environment=env,
            hazard_events=[
                HazardEvent(
                    event_id="test",
                    hazard=HazardFunction(base_rate=0.5),
                    max_fires=1,
                    effects_on_fire=[
                        {"field_path": "env.surveillance", "operation": "add", "value": 2.0},
                    ],
                    action_options_on_fire=[],
                ),
            ],
        )
        result = SimulationRunner(config, RuleEngine([HomeostasisRule()])).run_single(seed=42)
        assert result.final_state.tick == 20

    def test_different_env_different_results(self):
        """다른 환경 -> 다른 결과."""
        base_event = HazardEvent(
            event_id="challenge",
            hazard=HazardFunction(
                base_rate=0.3,
                factors=[HazardFactor(field_path="surveillance", weight=0.5, source="environment")],
            ),
            max_fires=3,
            cooldown=2,
            effects_on_fire=[],
            action_options_on_fire=[
                {
                    "action_id": "deny",
                    "weight_formula": {"base_weight": 0.3, "state_multipliers": [
                        {"field_path": "surveillance", "factor_type": "linear",
                         "params": {"scale": 0.5}, "source": "environment"},
                    ]},
                    "effects": [{"field_path": "emotions.grief", "operation": "add", "value": 1.0}],
                },
                {
                    "action_id": "confess",
                    "weight_formula": {"base_weight": 0.5},
                    "effects": [],
                },
            ],
        )

        low_config = SimulationConfig(
            max_tick=30, initial_state=_agent(),
            hazard_events=[base_event],
            environment=EnvironmentState(surveillance=1.0),
        )
        high_config = SimulationConfig(
            max_tick=30, initial_state=_agent(),
            hazard_events=[base_event],
            environment=EnvironmentState(surveillance=9.0),
        )

        engine = RuleEngine([HomeostasisRule()])
        # 100회 돌려서 deny 비율 비교
        low_denials = 0
        high_denials = 0
        for seed in range(100):
            r_low = SimulationRunner(low_config, engine).run_single(seed=seed)
            r_high = SimulationRunner(high_config, engine).run_single(seed=seed)
            low_denials += sum(1 for a in r_low.action_history if a.chosen_action == "deny")
            high_denials += sum(1 for a in r_high.action_history if a.chosen_action == "deny")

        # 높은 surveillance에서 deny가 더 많아야 함
        assert high_denials > low_denials
