"""에이전트 행동 프로파일 테스트."""

import random

from engine.core.action import AgentAction, AgentBehaviorProfile
from engine.core.event import WeightFormula
from engine.core.state import AgentState, EmotionalState


def _agent(fear: float = 5.0, hope: float = 5.0) -> AgentState:
    return AgentState(
        agent_id="test",
        emotions=EmotionalState(fear=fear, hope=hope),
    )


def _action(action_id: str, base_weight: float = 1.0, cooldown: int = 0) -> AgentAction:
    return AgentAction(
        action_id=action_id,
        weight_formula=WeightFormula(base_weight=base_weight),
        cooldown=cooldown,
    )


class TestAgentAction:
    def test_available_by_default(self):
        action = _action("follow")
        assert action.is_available(0, _agent()) is True

    def test_cooldown_blocks(self):
        action = _action("follow", cooldown=3)
        action.record_perform(10)
        assert action.is_available(11, _agent()) is False
        assert action.is_available(13, _agent()) is True

    def test_record_perform(self):
        action = _action("follow")
        action.record_perform(5)
        assert action.last_performed_tick == 5

    def test_visible_signal_default_none(self):
        action = _action("follow")
        assert action.visible_signal is None

    def test_visible_signal_set(self):
        action = AgentAction(
            action_id="withdraw",
            weight_formula=WeightFormula(base_weight=1.0),
            visible_signal="agent가 조용히 물러났다.",
        )
        assert action.visible_signal == "agent가 조용히 물러났다."

    def test_observable_from_default_empty(self):
        """기본값: 비어있음 (공개). Player view가 모두에게 보여줌."""
        action = _action("follow")
        assert action.observable_from == []

    def test_observable_from_restricts_to_list(self):
        action = AgentAction(
            action_id="secret_meeting",
            weight_formula=WeightFormula(base_weight=1.0),
            observable_from=["caiaphas"],
        )
        assert action.observable_from == ["caiaphas"]

    def test_observable_from_serializable(self):
        """Pydantic round-trip 유지 (content pack JSON 호환성)."""
        import json
        action = AgentAction(
            action_id="x",
            weight_formula=WeightFormula(base_weight=1.0),
            observable_from=["a", "b"],
            visible_signal="signal",
        )
        data = json.loads(action.model_dump_json())
        restored = AgentAction.model_validate(data)
        assert restored.observable_from == ["a", "b"]
        assert restored.visible_signal == "signal"


class TestAgentBehaviorProfile:
    def test_get_available(self):
        profile = AgentBehaviorProfile(
            agent_id="peter",
            actions=[_action("follow"), _action("pray")],
        )
        available = profile.get_available_actions(0, _agent())
        assert len(available) == 2

    def test_select_action_deterministic(self):
        """높은 가중치 행동이 선택될 확률이 높다."""
        profile = AgentBehaviorProfile(
            agent_id="peter",
            actions=[
                _action("follow", base_weight=100.0),
                _action("hide", base_weight=0.01),
            ],
        )
        rng = random.Random(42)
        counts = {"follow": 0, "hide": 0}
        for _ in range(100):
            action = profile.select_action(0, _agent(), rng)
            assert action is not None
            counts[action.action_id] += 1
        assert counts["follow"] > 90

    def test_select_action_no_available(self):
        profile = AgentBehaviorProfile(
            agent_id="peter",
            actions=[],
        )
        rng = random.Random(42)
        assert profile.select_action(0, _agent(), rng) is None

    def test_cooldown_filters(self):
        action = _action("follow", cooldown=10)
        action.record_perform(0)
        profile = AgentBehaviorProfile(
            agent_id="peter",
            actions=[action],
        )
        available = profile.get_available_actions(5, _agent())
        assert len(available) == 0

    def test_select_action_floating_point_safeguard(self):
        """부동소수점 안전장치 (line 108): 매우 많은 options에서 안정성."""
        profile = AgentBehaviorProfile(
            agent_id="peter",
            actions=[_action(f"a{i}", base_weight=1.0) for i in range(50)],
        )
        rng = random.Random(0)
        for _ in range(20):
            result = profile.select_action(0, _agent(), rng)
            assert result is not None
