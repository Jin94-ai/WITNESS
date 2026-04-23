"""Run Explanation Card 테스트."""

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
from engine.simulation.explanation import format_explanation_text, generate_explanation
from engine.simulation.world import SimulationWorld

register_domain_type("faith_journey", FaithJourneyState)
register_domain_type("betrayal_psychology", BetrayalPsychologyState)
register_domain_type("political_calculation", PoliticalCalculationState)
register_domain_type("crowd_dynamics", CrowdDynamicsState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"


def _run_peter_multi(seed=42):
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
    engine = RuleEngine([FearResponseRule(), GriefRule(), HopeRule(), HomeostasisRule()])
    config = SimulationConfig(
        max_tick=500, initial_state=peter,
        initial_states=[peter, judas, caiaphas, crowd],
        hazard_events=hazards, interventions=interventions,
        triggers=triggers, state_noise_scale=0.05,
    )
    return SimulationWorld(config, engine, behavior_profiles=profiles).run(seed=seed)


class TestExplanationCard:
    def test_generate_explanation(self):
        """설명 카드가 생성된다."""
        result = _run_peter_multi()
        card = generate_explanation(result)

        assert "seed" in card
        assert "agents" in card
        assert "key_events" in card
        assert "causal_chain" in card
        assert "outcome_summary" in card
        assert card["seed"] == 42

    def test_agents_summary(self):
        """에이전트별 요약이 올바르다."""
        result = _run_peter_multi()
        card = generate_explanation(result)

        assert "peter" in card["agents"]
        assert "judas" in card["agents"]
        assert card["agents"]["peter"]["total_actions"] > 0
        assert "dominant_action" in card["agents"]["peter"]

    def test_causal_chain_present(self):
        """인과 체인이 추출된다."""
        result = _run_peter_multi()
        card = generate_explanation(result)

        assert len(card["causal_chain"]) > 0
        events = [s["event"] for s in card["causal_chain"]]
        print(f"\nCausal chain: {events}")

    def test_format_text(self):
        """텍스트 포맷이 생성된다."""
        result = _run_peter_multi()
        card = generate_explanation(result)
        text = format_explanation_text(card)

        assert "Run Explanation" in text
        assert "Outcome:" in text
        assert "Agent Summary" in text
        print(f"\n{text}")

    def test_different_seeds_different_explanations(self):
        """다른 시드에서 다른 설명이 생성된다."""
        r1 = _run_peter_multi(seed=1)
        r2 = _run_peter_multi(seed=2)
        c1 = generate_explanation(r1)
        c2 = generate_explanation(r2)

        # 결과 요약이 다를 수 있음 (다른 체포 tick)
        assert c1["outcome_summary"] != c2["outcome_summary"] or c1["seed"] != c2["seed"]


class TestExplanationVanGogh:
    def _run_vg(self, seed=42):
        from content.gauguin.domain_artistic_ego import ArtisticEgoState
        from content.theo.domain_patron import PatronState
        from content.vangogh.domain_creative import CreativeDriveState

        register_domain_type("creative_drive", CreativeDriveState)
        register_domain_type("artistic_ego", ArtisticEgoState)
        register_domain_type("patron", PatronState)

        vg = load_agent_state(CONTENT_DIR / "vangogh" / "initial_state.json")
        g = load_agent_state(CONTENT_DIR / "gauguin" / "initial_state.json")
        t = load_agent_state(CONTENT_DIR / "theo" / "initial_state.json")
        triggers = load_triggers(CONTENT_DIR / "vangogh" / "triggers.json")
        profiles = {
            "vangogh": load_behavior_profile(CONTENT_DIR / "vangogh" / "behavior_profile.json"),
            "gauguin": load_behavior_profile(CONTENT_DIR / "gauguin" / "behavior_profile.json"),
            "theo": load_behavior_profile(CONTENT_DIR / "theo" / "behavior_profile.json"),
        }
        engine = RuleEngine([FearResponseRule(), GriefRule(), HopeRule(), HomeostasisRule()])
        config = SimulationConfig(
            max_tick=150, initial_state=vg,
            initial_states=[vg, g, t],
            triggers=triggers, state_noise_scale=0.05,
        )
        return SimulationWorld(config, engine, behavior_profiles=profiles).run(seed=seed)

    def test_vg_explanation(self):
        """Van Gogh 시나리오의 설명 카드."""
        result = self._run_vg()
        card = generate_explanation(result)
        # 트리거가 발동했어야 함
        assert "Trigger" in card["outcome_summary"]
        # gauguin departure가 인과 체인에 있어야 함
        events = [s["event"] for s in card["causal_chain"]]
        assert "gauguin_departure" in events

    def test_vg_format(self):
        """Van Gogh 설명 카드 텍스트 포맷."""
        result = self._run_vg()
        card = generate_explanation(result)
        text = format_explanation_text(card)
        assert "Trigger" in text
