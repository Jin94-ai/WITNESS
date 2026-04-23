"""내러티브 렌더러 테스트."""

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
from engine.rendering.narrator import render_ensemble_summary, render_narrative
from engine.rules.base import RuleEngine
from engine.rules.emotional import FearResponseRule, GriefRule, HopeRule
from engine.rules.temporal import HomeostasisRule
from engine.simulation.world import SimulationWorld

register_domain_type("faith_journey", FaithJourneyState)
register_domain_type("betrayal_psychology", BetrayalPsychologyState)
register_domain_type("political_calculation", PoliticalCalculationState)
register_domain_type("crowd_dynamics", CrowdDynamicsState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"


def _run(seed=42):
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


class TestNarrator:
    def test_render_narrative(self):
        """Peter 관점 내러티브가 생성된다."""
        result = _run()
        text = render_narrative(result, "peter")

        assert "Narrative: peter" in text
        assert "[Prologue]" in text
        assert "[Actions]" in text
        assert "[Epilogue]" in text
        assert "[Outcome]" in text
        print(f"\n{text}")

    def test_render_judas_narrative(self):
        """Judas 관점 내러티브가 생성된다."""
        result = _run()
        text = render_narrative(result, "judas")

        assert "Narrative: judas" in text
        assert "[Actions]" in text

    def test_ensemble_summary(self):
        """앙상블 요약이 생성된다."""
        results = [_run(seed=s) for s in range(5)]
        text = render_ensemble_summary(results, "peter")

        assert "Ensemble Summary" in text
        assert "[Action Distribution]" in text
        assert "[Final State Statistics]" in text
        print(f"\n{text}")


class TestNarratorEdgeBranches:
    def test_render_narrative_default_agent(self):
        """agent_id=\"\" → final_states의 첫 번째 agent 자동 선택."""
        result = _run()
        text = render_narrative(result, agent_id="")
        assert "Narrative:" in text
        # default로 선택된 agent가 final_states의 첫 번째
        assert next(iter(result.final_states)) in text

    def test_render_narrative_missing_scripture_dir(self, tmp_path, monkeypatch):
        """scripture_dir가 존재하지 않으면 Scripture 섹션 생략."""
        # narrator가 기본 "content/shared/scripture"를 사용하므로
        # cwd를 tmp로 바꿔 해당 경로가 없게 만듦
        monkeypatch.chdir(tmp_path)
        result = _run()
        text = render_narrative(result, "peter")
        assert "Narrative: peter" in text
        assert "[Scripture" not in text

    def test_render_ensemble_summary_empty(self):
        """빈 results → 'No results to summarize.'"""
        text = render_ensemble_summary([], "peter")
        assert text == "No results to summarize."

    def test_render_ensemble_summary_default_agent(self):
        """agent_id=\"\" → results[0].final_states의 첫 agent 자동."""
        results = [_run(seed=s) for s in range(2)]
        text = render_ensemble_summary(results, agent_id="")
        assert "Ensemble Summary" in text
