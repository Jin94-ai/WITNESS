"""DiplomacyState (Talleyrand 스켈레톤) 검증 (Iter 54).

ChatGPT 권장: 3번째 시나리오는 엔진의 약점(협상/점진적 체제 전환)을 시험.
이 테스트는 domain state 스켈레톤이 Peter/VG와 구조적으로 구별되는지 확인.
"""

from content.talleyrand.domain_diplomacy import DiplomacyState
from engine.core.state import AgentState, DomainState
from engine.io.loader import register_domain_type


class TestDiplomacyStateSchema:
    def test_inherits_domain_state(self):
        assert issubclass(DiplomacyState, DomainState)

    def test_default_instantiation(self):
        s = DiplomacyState()
        assert s.type == "diplomacy"
        assert s.current_regime == "ancien_regime"
        assert s.alignment_stance == "pragmatic_serve"
        assert 0.0 <= s.leverage <= 10.0
        assert 0.0 <= s.legitimacy_anchor <= 10.0

    def test_bounded_fields(self):
        """모든 float field는 [0, 10] 범위."""
        s = DiplomacyState()
        for name in [
            "leverage", "legitimacy_anchor", "reputation_ambiguity",
            "network_depth", "moral_fatigue",
        ]:
            v = getattr(s, name)
            assert 0.0 <= v <= 10.0, f"{name} out of [0,10]: {v}"

    def test_regime_literal_enforcement(self):
        """current_regime은 Literal이므로 무효 값 거부."""
        import pytest
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            DiplomacyState(current_regime="monarchy_of_france")  # not in Literal

    def test_alignment_stance_literal(self):
        import pytest
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            DiplomacyState(alignment_stance="traitor")  # not in Literal


class TestRegistryIntegration:
    """DomainState registry에 등록 가능 + AgentState 안에 들어감."""

    def test_registers_and_loads(self):
        register_domain_type("diplomacy", DiplomacyState)
        agent = AgentState(
            agent_id="talleyrand",
            domain_state=DiplomacyState(
                current_regime="empire",
                alignment_stance="covert_maneuver",
                leverage=8.0,
                legitimacy_anchor=2.0,
                reputation_ambiguity=8.5,
                network_depth=9.0,
                network_regime_span=4,
            ),
        )
        assert agent.domain_state.type == "diplomacy"
        assert agent.domain_state.current_regime == "empire"


class TestStructuralDistinctionFromPeterVG:
    """Peter (bottleneck), VG (isolation), Talleyrand (ambiguity) — 축이 다름."""

    def test_has_ambiguity_as_resource(self):
        """Talleyrand는 reputation_ambiguity가 자원 (Peter/VG엔 없음)."""
        s = DiplomacyState(reputation_ambiguity=9.0)
        assert s.reputation_ambiguity >= 7.0  # 높은 ambiguity = 생존 자원

    def test_compromise_count_monotonic_counter(self):
        """compromise_count는 accumulation 변수 (Peter obedience와 대응되지만 의미 반대)."""
        s = DiplomacyState(compromise_count=15)
        assert s.compromise_count >= 0

    def test_moral_fatigue_distinct_from_moral_injury(self):
        """moral_fatigue는 '원칙 부재' 피로 — Peter의 moral_injury와 다른 semantic."""
        s = DiplomacyState(moral_fatigue=5.5)
        assert 0.0 <= s.moral_fatigue <= 10.0
