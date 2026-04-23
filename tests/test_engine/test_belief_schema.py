"""AgentBelief + belief_update entry 테스트 (§2.3, v1.1 기초).

v1.1 relational extension 전이라도 스키마와 파이프라인이 작동하는지 검증.
"""

from engine.core.state import AgentBelief, AgentState
from engine.rendering.player_view import PlayerViewFilterConfig, filter_for_player
from engine.rendering.trace_emitter import (
    TraceEvent,
    collect_trace_events,
    emit_belief_updates,
)


class TestAgentBeliefSchema:
    def test_default_belief(self):
        b = AgentBelief(target_id="judas")
        assert b.target_id == "judas"
        assert b.estimated_state == {}
        assert b.confidence == 0.0
        assert b.observation_count == 0

    def test_belief_fields(self):
        b = AgentBelief(
            target_id="judas",
            estimated_state={"emotions.fear": 6.5, "domain_state.disillusionment": 7.2},
            confidence=0.4,
            observation_count=12,
        )
        assert b.estimated_state["domain_state.disillusionment"] == 7.2
        assert b.confidence == 0.4
        assert b.observation_count == 12


class TestAgentStateBeliefs:
    def test_beliefs_empty_by_default(self):
        """v0.x에서는 beliefs dict가 비어있음."""
        state = AgentState(agent_id="peter")
        assert state.beliefs == {}

    def test_beliefs_assignable(self):
        state = AgentState(
            agent_id="peter",
            beliefs={
                "judas": AgentBelief(target_id="judas", confidence=0.3),
            },
        )
        assert "judas" in state.beliefs
        assert state.beliefs["judas"].confidence == 0.3


class TestBeliefEmitter:
    def test_emit_belief_event(self):
        updates = [
            {
                "tick": 150,
                "observer": "peter",
                "target": "judas",
                "trigger": "observed withdraw x3",
                "belief_change": {
                    "estimated_drive[loyalty]": "0.7 → 0.4",
                    "trust": "4.0 → 3.2",
                },
            },
        ]
        events = list(emit_belief_updates(updates))
        assert len(events) == 1
        ev = events[0]
        assert ev.type == "belief_update"
        assert ev.payload["observer"] == "peter"
        assert ev.payload["target"] == "judas"
        assert "belief_change" in ev.payload

    def test_collect_trace_with_beliefs(self):
        """collect_trace_events가 belief_updates를 받아 통합."""
        from types import SimpleNamespace

        result = SimpleNamespace(
            action_histories={},
            fired_triggers=[],
            checkpoint_results={},
        )
        belief_updates = [
            {"tick": 50, "observer": "peter", "target": "judas",
             "trigger": "saw withdraw", "belief_change": {"trust": "5 → 4"}},
        ]
        events = collect_trace_events(result, belief_updates=belief_updates)
        belief_events = [e for e in events if e.type == "belief_update"]
        assert len(belief_events) == 1


class TestBeliefPlayerView:
    def test_own_belief_visible(self):
        """Peter가 observer일 때 Peter 시점에서 관찰 가능."""
        ev = TraceEvent(
            tick=100, type="belief_update",
            payload={"observer": "peter", "target": "judas", "trigger": "x",
                     "belief_change": {}},
        )
        cfg = PlayerViewFilterConfig(player_id="peter")
        filtered = filter_for_player([ev], cfg)
        assert len(filtered) == 1

    def test_other_belief_hidden(self):
        """Caiaphas의 belief update는 Peter 시점에서 가려짐."""
        ev = TraceEvent(
            tick=100, type="belief_update",
            payload={"observer": "caiaphas", "target": "judas", "trigger": "x",
                     "belief_change": {}},
        )
        cfg = PlayerViewFilterConfig(player_id="peter")
        filtered = filter_for_player([ev], cfg)
        assert filtered == []
