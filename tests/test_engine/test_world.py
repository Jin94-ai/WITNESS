"""다중 에이전트 SimulationWorld 테스트."""

import random

from engine.core.action import AgentAction, AgentBehaviorProfile
from engine.core.event import StateEffect, WeightFormula
from engine.core.state import AgentState, EmotionalState
from engine.core.trigger import Trigger, TriggerCondition
from engine.core.world import SimulationConfig
from engine.rules.base import RuleEngine
from engine.rules.emotional import FearResponseRule, HopeRule
from engine.rules.temporal import HomeostasisRule
from engine.simulation.scheduler import AgentScheduler
from engine.simulation.world import MultiAgentResult, SimulationWorld


def _agent(agent_id: str, fear: float = 5.0, hope: float = 5.0) -> AgentState:
    return AgentState(
        agent_id=agent_id,
        emotions=EmotionalState(fear=fear, hope=hope),
    )


def _rule_engine() -> RuleEngine:
    return RuleEngine([FearResponseRule(), HopeRule(), HomeostasisRule()])


class TestAgentScheduler:
    def test_sequential_order(self):
        scheduler = AgentScheduler(["a", "b", "c"], mode="sequential")
        rng = random.Random(42)
        order = scheduler.get_activation_order(rng)
        assert order == ["a", "b", "c"]

    def test_random_order_varies(self):
        scheduler = AgentScheduler(["a", "b", "c"], mode="random")
        orders = set()
        for seed in range(20):
            rng = random.Random(seed)
            order = tuple(scheduler.get_activation_order(rng))
            orders.add(order)
        assert len(orders) > 1  # 적어도 2가지 이상의 순서

    def test_add_remove_agent(self):
        scheduler = AgentScheduler(["a", "b"])
        scheduler.add_agent("c")
        assert "c" in scheduler.agent_ids
        scheduler.remove_agent("a")
        assert "a" not in scheduler.agent_ids


class TestSimulationWorldBasic:
    def test_two_agent_runs(self):
        """2-에이전트 시뮬레이션이 완주한다."""
        peter = _agent("peter", fear=6.0, hope=4.0)
        judas = _agent("judas", fear=3.0, hope=2.0)

        config = SimulationConfig(
            max_tick=50,
            initial_state=peter,
            initial_states=[peter, judas],
            state_noise_scale=0.05,
        )
        world = SimulationWorld(config, _rule_engine())
        result = world.run(seed=42)

        assert isinstance(result, MultiAgentResult)
        assert "peter" in result.final_states
        assert "judas" in result.final_states
        assert result.final_states["peter"].tick == 50
        assert result.final_states["judas"].tick == 50

    def test_single_agent_compat(self):
        """단일 에이전트도 SimulationWorld로 실행 가능."""
        peter = _agent("peter")
        config = SimulationConfig(
            max_tick=30,
            initial_state=peter,
            state_noise_scale=0.01,
        )
        world = SimulationWorld(config, _rule_engine())
        result = world.run(seed=1)

        assert len(result.final_states) == 1
        assert "peter" in result.final_states

    def test_seed_reproducibility(self):
        """같은 시드면 같은 결과."""
        peter = _agent("peter", fear=7.0)
        judas = _agent("judas", fear=3.0)
        config = SimulationConfig(
            max_tick=30,
            initial_state=peter,
            initial_states=[peter, judas],
            state_noise_scale=0.05,
        )
        engine = _rule_engine()
        r1 = SimulationWorld(config, engine).run(seed=99)
        r2 = SimulationWorld(config, engine).run(seed=99)
        assert r1.final_states["peter"].emotions.fear == r2.final_states["peter"].emotions.fear
        assert r1.final_states["judas"].emotions.fear == r2.final_states["judas"].emotions.fear

    def test_parameter_overrides_applied_to_initial_states(self):
        """parameter_overrides는 모든 initial state에 적용됨 (world.py:355)."""
        peter = _agent("peter", fear=3.0)
        judas = _agent("judas", fear=3.0)
        config = SimulationConfig(
            max_tick=5,
            initial_state=peter,
            initial_states=[peter, judas],
            state_noise_scale=0.0,
            parameter_overrides={"emotions.fear": 8.5},
        )
        world = SimulationWorld(config, _rule_engine())
        result = world.run(seed=0)
        # 모든 agent의 fear가 override 값으로 시작 (tick 0 snapshot 확인)
        for aid in ["peter", "judas"]:
            snap0 = result.state_snapshots[aid].get(0)
            assert snap0 is not None
            assert snap0.emotions.fear == 8.5, \
                f"{aid} fear should be override 8.5, got {snap0.emotions.fear}"


class TestSimulationWorldTrigger:
    def test_trigger_fires(self):
        """트리거 조건 충족 시 발동한다."""
        peter = _agent("peter", fear=5.0)
        judas = _agent("judas", fear=9.0)  # 높은 fear -> 트리거 조건

        trigger = Trigger(
            trigger_id="arrest",
            state_conditions=[
                TriggerCondition(
                    agent_id="judas", field_path="emotions.fear",
                    operator="gte", value=8.0,
                ),
            ],
            event_template_id="arrest_event",
        )

        config = SimulationConfig(
            max_tick=10,
            initial_state=peter,
            initial_states=[peter, judas],
            triggers=[trigger],
        )
        result = SimulationWorld(config, _rule_engine()).run(seed=42)

        # judas.fear=9.0 >= 8.0이므로 트리거 발동
        assert len(result.fired_triggers) > 0
        assert result.fired_triggers[0]["trigger_id"] == "arrest"

    def test_trigger_deadline(self):
        """트리거 조건 미충족이어도 deadline에 강제 발동."""
        peter = _agent("peter")
        judas = _agent("judas", fear=1.0)  # 조건 미충족

        trigger = Trigger(
            trigger_id="arrest",
            state_conditions=[
                TriggerCondition(
                    agent_id="judas", field_path="emotions.fear",
                    operator="gte", value=99.0,  # 불가능한 조건
                ),
            ],
            event_template_id="arrest_event",
            deadline_tick=5,
        )

        config = SimulationConfig(
            max_tick=10,
            initial_state=peter,
            initial_states=[peter, judas],
            triggers=[trigger],
        )
        result = SimulationWorld(config, _rule_engine()).run(seed=42)

        assert len(result.fired_triggers) == 1
        assert result.fired_triggers[0]["tick"] == 5  # deadline 강제


class TestSimulationWorldBehaviorProfile:
    def test_voluntary_actions(self):
        """에이전트 자발적 행동이 기록된다."""
        peter = _agent("peter", fear=5.0)
        judas = _agent("judas", fear=5.0)

        profiles = {
            "judas": AgentBehaviorProfile(
                agent_id="judas",
                actions=[
                    AgentAction(
                        action_id="inform",
                        weight_formula=WeightFormula(base_weight=10.0),
                    ),
                ],
            ),
        }

        config = SimulationConfig(
            max_tick=5,
            initial_state=peter,
            initial_states=[peter, judas],
        )
        result = SimulationWorld(
            config, _rule_engine(), behavior_profiles=profiles,
        ).run(seed=42)

        # judas는 매 tick "inform" 행동을 수행해야 함
        judas_actions = result.action_histories.get("judas", [])
        assert len(judas_actions) == 5  # 5 ticks
        assert all(a.chosen_action == "inform" for a in judas_actions)

    def test_action_with_cross_agent_effect(self):
        """에이전트 행동이 다른 에이전트에 영향."""
        peter = _agent("peter", fear=3.0)
        judas = _agent("judas", fear=5.0)

        profiles = {
            "judas": AgentBehaviorProfile(
                agent_id="judas",
                actions=[
                    AgentAction(
                        action_id="betray",
                        weight_formula=WeightFormula(base_weight=10.0),
                        effects=[
                            StateEffect(
                                field_path="emotions.fear",
                                operation="add", value=2.0,
                                target_agent_id="peter",
                            ),
                        ],
                    ),
                ],
            ),
        }

        config = SimulationConfig(
            max_tick=1,
            initial_state=peter,
            initial_states=[peter, judas],
        )
        result = SimulationWorld(
            config, _rule_engine(), behavior_profiles=profiles,
        ).run(seed=42)

        # peter의 fear가 judas의 betray로 상승해야 함
        # 초기 3.0 + 2.0 = 5.0 (규칙 적용 전)
        peter_final = result.final_states["peter"]
        assert peter_final.emotions.fear > 3.0


class TestExtractAgentResult:
    def test_extract_produces_simulation_result(self):
        """extract_agent_result가 SimulationResult를 반환한다."""
        from engine.simulation.runner import SimulationResult

        peter = _agent("peter", fear=5.0)
        judas = _agent("judas", fear=3.0)
        config = SimulationConfig(
            max_tick=10,
            initial_state=peter,
            initial_states=[peter, judas],
            state_noise_scale=0.01,
        )
        multi = SimulationWorld(config, _rule_engine()).run(seed=42)
        peter_r = multi.extract_agent_result("peter")

        assert isinstance(peter_r, SimulationResult)
        assert peter_r.final_state.agent_id == "peter"
        assert peter_r.seed == 42


class TestSimulationWorldWithHazard:
    def test_hazard_events_fire(self):
        """SimulationWorld에서 hazard 이벤트가 발동한다."""
        from engine.core.hazard import HazardEvent, HazardFunction

        peter = _agent("peter", fear=7.0)
        judas = _agent("judas", fear=3.0)

        hazard_event = HazardEvent(
            event_id="test_hazard",
            hazard=HazardFunction(base_rate=0.5),
            anchor_window=(1, 20),
            effects_on_fire=[
                {"field_path": "emotions.fear", "operation": "add", "value": 1.0}
            ],
        )

        config = SimulationConfig(
            max_tick=20,
            initial_state=peter,
            initial_states=[peter, judas],
            hazard_events=[hazard_event],
            state_noise_scale=0.05,
        )
        result = SimulationWorld(config, _rule_engine()).run(seed=42)

        assert len(result.fired_events) > 0
        assert result.fired_events[0]["event_id"] == "test_hazard"

    def test_hazard_with_action_options(self):
        """Hazard 이벤트에 행동 선택지가 있으면 primary agent가 선택한다."""
        from engine.core.hazard import HazardEvent, HazardFunction

        peter = _agent("peter", fear=5.0)

        hazard_event = HazardEvent(
            event_id="crisis",
            hazard=HazardFunction(base_rate=1.0),
            anchor_window=(1, 5),
            action_options_on_fire=[
                {
                    "action_id": "flee",
                    "weight_formula": {"base_weight": 5.0},
                    "effects": [{"field_path": "emotions.fear", "operation": "add", "value": -2.0}],
                },
                {
                    "action_id": "stand",
                    "weight_formula": {"base_weight": 1.0},
                },
            ],
        )

        config = SimulationConfig(
            max_tick=5,
            initial_state=peter,
            hazard_events=[hazard_event],
        )
        result = SimulationWorld(config, _rule_engine()).run(seed=42)

        peter_actions = result.action_histories.get("peter", [])
        assert len(peter_actions) > 0

    def test_hazard_env_effect(self):
        """Hazard 이벤트가 환경에 효과를 적용한다."""
        from engine.core.hazard import HazardEvent, HazardFunction

        peter = _agent("peter", fear=5.0)

        hazard_event = HazardEvent(
            event_id="env_event",
            hazard=HazardFunction(base_rate=1.0),
            anchor_window=(1, 3),
            effects_on_fire=[
                {"field_path": "env.surveillance", "operation": "add", "value": 2.0}
            ],
        )

        config = SimulationConfig(
            max_tick=5,
            initial_state=peter,
            hazard_events=[hazard_event],
            state_noise_scale=0.01,
        )
        # Should run without error
        result = SimulationWorld(config, _rule_engine()).run(seed=42)
        assert len(result.fired_events) > 0


class TestEventSchedulerInject:
    def test_inject_event(self):
        """동적 이벤트 주입이 작동한다."""
        from engine.core.event import ExternalEvent
        from engine.simulation.event_scheduler import EventScheduler

        scheduler = EventScheduler([])
        event = ExternalEvent(event_id="dynamic", tick=5, description="injected")
        scheduler.inject_event(event)

        # tick 5에서 조회 가능해야 함
        events = scheduler.get_events_for_tick(5)
        assert len(events) == 1
        assert events[0].event_id == "dynamic"

    def test_inject_preserves_order(self):
        """주입된 이벤트가 기존 이벤트 순서를 유지한다."""
        from engine.core.event import ExternalEvent
        from engine.simulation.event_scheduler import EventScheduler

        existing = [ExternalEvent(event_id="e1", tick=3), ExternalEvent(event_id="e3", tick=7)]
        scheduler = EventScheduler(existing)
        scheduler.inject_event(ExternalEvent(event_id="e2", tick=5))

        e3 = scheduler.get_events_for_tick(3)
        assert len(e3) == 1

        e5 = scheduler.get_events_for_tick(5)
        assert len(e5) == 1
        assert e5[0].event_id == "e2"
