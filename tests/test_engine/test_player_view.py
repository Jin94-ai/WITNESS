"""Player view filter 테스트 (TRACE_SCHEMA §3.1).

플레이어 시점 필터링 + 내부 정보 제거 검증.
"""

from engine.rendering.player_view import (
    PlayerViewFilterConfig,
    filter_for_player,
    is_observable,
    strip_internals,
)
from engine.rendering.trace_emitter import TraceEvent


def _cfg(player: str = "peter") -> PlayerViewFilterConfig:
    return PlayerViewFilterConfig(player_id=player)


class TestObservability:
    def test_bifurcation_included(self):
        ev = TraceEvent(tick=100, type="bifurcation_point", payload={})
        assert is_observable(ev, _cfg()) is True

    def test_trigger_fired_included(self):
        ev = TraceEvent(tick=150, type="trigger_fired", payload={"trigger_id": "arrest"})
        assert is_observable(ev, _cfg()) is True

    def test_canonical_match_excluded(self):
        ev = TraceEvent(
            tick=0, type="canonical_match",
            payload={"checkpoint_id": "deny_3", "passed": True},
        )
        assert is_observable(ev, _cfg()) is False

    def test_action_self_always_visible(self):
        ev = TraceEvent(
            tick=5, type="action_taken",
            payload={"agent": "peter", "action": "pray", "observable_from": []},
        )
        assert is_observable(ev, _cfg("peter")) is True

    def test_action_public_visible(self):
        """observable_from empty → 공적 행동, 누구나 관찰."""
        ev = TraceEvent(
            tick=5, type="action_taken",
            payload={"agent": "judas", "action": "follow", "observable_from": []},
        )
        assert is_observable(ev, _cfg("peter")) is True

    def test_action_restricted_not_player(self):
        ev = TraceEvent(
            tick=5, type="action_taken",
            payload={"agent": "judas", "action": "secret",
                     "observable_from": ["caiaphas"]},
        )
        assert is_observable(ev, _cfg("peter")) is False

    def test_action_restricted_to_player(self):
        ev = TraceEvent(
            tick=5, type="action_taken",
            payload={"agent": "judas", "action": "whisper",
                     "observable_from": ["peter"]},
        )
        assert is_observable(ev, _cfg("peter")) is True

    def test_unknown_type_default_false(self):
        ev = TraceEvent(tick=0, type="future_entry_type", payload={})
        assert is_observable(ev, _cfg()) is False


class TestInternalsStripping:
    def test_other_agent_internals_stripped(self):
        ev = TraceEvent(
            tick=5, type="action_taken",
            payload={
                "agent": "judas",
                "action": "withdraw",
                "weights": {"withdraw": 1.2, "follow": 0.8},
                "latent_drive": [0.9, 0.3],
                "observable_from": [],
            },
        )
        stripped = strip_internals(ev, _cfg("peter"))
        assert "weights" not in stripped.payload
        assert "latent_drive" not in stripped.payload
        # 허용된 필드는 보존
        assert stripped.payload["agent"] == "judas"
        assert stripped.payload["action"] == "withdraw"

    def test_self_internals_preserved(self):
        """플레이어 자신의 event는 내부 정보 보존 (1인칭 내레이션용)."""
        ev = TraceEvent(
            tick=5, type="action_taken",
            payload={
                "agent": "peter",
                "action": "pray",
                "weights": {"pray": 1.5},
                "internal_state_change": {"emotions.fear": "+1.0"},
            },
        )
        cfg = PlayerViewFilterConfig(player_id="peter", include_self_internals=True)
        stripped = strip_internals(ev, cfg)
        assert "weights" in stripped.payload
        assert "internal_state_change" in stripped.payload

    def test_self_internals_optional_off(self):
        """include_self_internals=False 면 자기 것도 제거."""
        ev = TraceEvent(
            tick=5, type="action_taken",
            payload={
                "agent": "peter",
                "action": "pray",
                "weights": {"pray": 1.5},
            },
        )
        cfg = PlayerViewFilterConfig(player_id="peter", include_self_internals=False)
        stripped = strip_internals(ev, cfg)
        assert "weights" not in stripped.payload


class TestFilterPipeline:
    def test_filter_for_player_end_to_end(self):
        events = [
            # Peter 자기 행동
            TraceEvent(tick=1, type="action_taken", payload={
                "agent": "peter", "action": "follow", "observable_from": [],
                "weights": {"follow": 1.0},
            }),
            # Judas 공적 행동
            TraceEvent(tick=2, type="action_taken", payload={
                "agent": "judas", "action": "walk", "observable_from": [],
                "weights": {"walk": 1.0},
            }),
            # Caiaphas 비밀 행동 (Peter에게 안 보임)
            TraceEvent(tick=3, type="action_taken", payload={
                "agent": "caiaphas", "action": "plot",
                "observable_from": ["priests"],
            }),
            # Trigger
            TraceEvent(tick=10, type="trigger_fired", payload={
                "trigger_id": "arrest_trigger"
            }),
            # Canonical match (렌더 제외)
            TraceEvent(tick=0, type="canonical_match", payload={
                "checkpoint_id": "deny_3", "passed": True
            }),
        ]
        filtered = filter_for_player(events, _cfg("peter"))
        types_and_agents = [(e.type, e.payload.get("agent")) for e in filtered]

        # canonical_match 제외됨
        assert ("canonical_match", None) not in types_and_agents
        # caiaphas 비밀 행동 제외됨
        assert ("action_taken", "caiaphas") not in types_and_agents
        # Peter 자기 행동 포함, weights 보존
        peter_ev = [e for e in filtered if e.payload.get("agent") == "peter"][0]
        assert "weights" in peter_ev.payload
        # Judas 공적 행동 포함, weights 제거
        judas_ev = [e for e in filtered if e.payload.get("agent") == "judas"][0]
        assert "weights" not in judas_ev.payload
        # Trigger 포함
        assert ("trigger_fired", None) in types_and_agents
