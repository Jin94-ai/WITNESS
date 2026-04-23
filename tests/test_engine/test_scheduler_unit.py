"""AgentScheduler 단위 테스트."""

import random

from engine.simulation.scheduler import AgentScheduler


class TestAgentScheduler:
    def test_sequential_order_preserved(self):
        s = AgentScheduler(["a", "b", "c"], mode="sequential")
        order = s.get_activation_order(random.Random(0))
        assert order == ["a", "b", "c"]

    def test_simultaneous_order_preserved(self):
        s = AgentScheduler(["a", "b", "c"], mode="simultaneous")
        order = s.get_activation_order(random.Random(0))
        assert order == ["a", "b", "c"]

    def test_random_mode_shuffles(self):
        """random 모드는 seed에 따라 순서 변동."""
        s = AgentScheduler(["a", "b", "c", "d", "e", "f"], mode="random")
        orders = [tuple(s.get_activation_order(random.Random(i))) for i in range(10)]
        # 서로 다른 순열이 최소 2개 이상
        assert len(set(orders)) > 1

    def test_mode_property(self):
        """mode property 접근 (line 36)."""
        s = AgentScheduler(["a"], mode="simultaneous")
        assert s.mode == "simultaneous"

    def test_agent_ids_property_returns_copy(self):
        s = AgentScheduler(["a", "b"])
        ids = s.agent_ids
        ids.append("x")
        # 내부 상태는 불변
        assert "x" not in s.agent_ids

    def test_add_agent_idempotent(self):
        s = AgentScheduler(["a"])
        s.add_agent("a")
        assert s.agent_ids == ["a"]
        s.add_agent("b")
        assert s.agent_ids == ["a", "b"]

    def test_remove_agent(self):
        s = AgentScheduler(["a", "b", "c"])
        s.remove_agent("b")
        assert s.agent_ids == ["a", "c"]
        # no-op for unknown
        s.remove_agent("x")
        assert s.agent_ids == ["a", "c"]
