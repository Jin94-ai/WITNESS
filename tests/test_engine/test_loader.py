"""engine/io/loader.py 단위 테스트."""

from pathlib import Path

from content.peter.domain_faith import FaithJourneyState
from engine.io.loader import (
    load_agent_state,
    register_domain_type,
    resolve_domain_state,
)

# FaithJourneyState를 레지스트리에 등록
register_domain_type("faith_journey", FaithJourneyState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content" / "peter"


class TestResolveDomainState:
    def test_none(self):
        assert resolve_domain_state(None) is None

    def test_base_type(self):
        result = resolve_domain_state({"type": "base"})
        assert result is not None
        assert result.type == "base"

    def test_faith_journey(self):
        result = resolve_domain_state({
            "type": "faith_journey",
            "jesus_understanding": "teacher",
            "communal_role": "disciple",
        })
        assert isinstance(result, FaithJourneyState)
        assert result.jesus_understanding == "teacher"

    def test_unknown_type_falls_back(self):
        result = resolve_domain_state({"type": "unknown_type"})
        assert result is not None
        assert result.type == "unknown_type"


class TestLoadAgentState:
    def test_load_peter_initial(self):
        path = CONTENT_DIR / "initial_state.json"
        state = load_agent_state(path)
        assert state.agent_id == "peter"
        assert state.physical.location == "bethany"
        assert state.emotions.hope == 7.0
        assert state.relationships["jesus"].trust == 8.0
        assert state.domain_state is not None
        assert isinstance(state.domain_state, FaithJourneyState)
        assert state.domain_state.jesus_understanding == "messiah_political"
        assert state.domain_state.communal_role == "inner_circle"
