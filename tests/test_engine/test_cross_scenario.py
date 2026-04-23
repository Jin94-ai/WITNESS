"""Cross-Scenario Ensemble Comparison.

동일 엔진이 완전히 다른 역사적 시나리오에서 구조적으로 유사한
창발적 행동을 생성하는지 비교한다.

Peter 시나리오: 유다 환멸 -> 배반 -> 체포
Van Gogh 시나리오: 고갱 좌절 -> 떠남 -> 위기

두 시나리오의 공통 구조:
- 핵심 에이전트의 내부 상태 누적 -> 임계점 도달 -> 트리거 발동
- spontaneous 발생률, tick 분산, 인과 체인 구조
"""

import statistics
from pathlib import Path

import pytest

from content.caiaphas.domain_politics import PoliticalCalculationState
from content.crowd.domain_crowd import CrowdDynamicsState
from content.gauguin.domain_artistic_ego import ArtisticEgoState
from content.judas.domain_betrayal import BetrayalPsychologyState
from content.peter.domain_faith import FaithJourneyState
from content.theo.domain_patron import PatronState
from content.vangogh.domain_creative import CreativeDriveState
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
from engine.simulation.world import SimulationWorld

register_domain_type("faith_journey", FaithJourneyState)
register_domain_type("betrayal_psychology", BetrayalPsychologyState)
register_domain_type("political_calculation", PoliticalCalculationState)
register_domain_type("crowd_dynamics", CrowdDynamicsState)
register_domain_type("creative_drive", CreativeDriveState)
register_domain_type("artistic_ego", ArtisticEgoState)
register_domain_type("patron", PatronState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"
N_SEEDS = 15


def _engine() -> RuleEngine:
    return RuleEngine([FearResponseRule(), GriefRule(), HopeRule(), HomeostasisRule()])


def _run_peter_ensemble():
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
    config = SimulationConfig(
        max_tick=500, initial_state=peter,
        initial_states=[peter, judas, caiaphas, crowd],
        hazard_events=hazards, interventions=interventions,
        triggers=triggers, state_noise_scale=0.05,
    )
    return [SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=s) for s in range(N_SEEDS)]


def _run_vangogh_ensemble():
    vg = load_agent_state(CONTENT_DIR / "vangogh" / "initial_state.json")
    g = load_agent_state(CONTENT_DIR / "gauguin" / "initial_state.json")
    t = load_agent_state(CONTENT_DIR / "theo" / "initial_state.json")
    triggers = load_triggers(CONTENT_DIR / "vangogh" / "triggers.json")
    hazards = load_hazard_events(CONTENT_DIR / "vangogh" / "hazard_events.json")
    profiles = {
        "vangogh": load_behavior_profile(CONTENT_DIR / "vangogh" / "behavior_profile.json"),
        "gauguin": load_behavior_profile(CONTENT_DIR / "gauguin" / "behavior_profile.json"),
        "theo": load_behavior_profile(CONTENT_DIR / "theo" / "behavior_profile.json"),
    }
    config = SimulationConfig(
        max_tick=150, initial_state=vg,
        initial_states=[vg, g, t],
        hazard_events=hazards,
        triggers=triggers, state_noise_scale=0.05,
    )
    return [SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=s) for s in range(N_SEEDS)]


class TestCrossScenarioComparison:
    @pytest.mark.slow
    def test_structural_similarity(self):
        """두 시나리오의 구조적 유사성을 비교한다."""
        peter_results = _run_peter_ensemble()
        vg_results = _run_vangogh_ensemble()

        # Peter: arrest 시점
        peter_ticks = []
        for r in peter_results:
            arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            if arrests and arrests[0]["tick"] < 400:
                peter_ticks.append(arrests[0]["tick"])

        # VG: departure 시점
        vg_ticks = []
        for r in vg_results:
            deps = [t for t in r.fired_triggers if t["trigger_id"] == "gauguin_departure"]
            if deps and deps[0]["tick"] < 120:
                vg_ticks.append(deps[0]["tick"])

        peter_sp_rate = len(peter_ticks) / N_SEEDS
        vg_sp_rate = len(vg_ticks) / N_SEEDS

        print("\n=== Cross-Scenario Structural Comparison ===")
        print(f"{'':>20} | {'Peter':>12} | {'Van Gogh':>12}")
        print("-" * 50)
        print(f"{'Spontaneous rate':>20} | {peter_sp_rate:>11.0%} | {vg_sp_rate:>11.0%}")

        if peter_ticks:
            pm = statistics.mean(peter_ticks)
            ps = statistics.stdev(peter_ticks) if len(peter_ticks) > 1 else 0
            print(f"{'Mean event tick':>20} | {pm:>11.0f} | ", end="")
        if vg_ticks:
            vm = statistics.mean(vg_ticks)
            vs = statistics.stdev(vg_ticks) if len(vg_ticks) > 1 else 0
            print(f"{vm:>11.0f}")
            print(f"{'Std dev':>20} | {ps:>11.0f} | {vs:>11.0f}")
            print(f"{'Unique ticks':>20} | {len(set(peter_ticks)):>11} | {len(set(vg_ticks)):>11}")

        # 둘 다 spontaneous rate >= 80%
        assert peter_sp_rate >= 0.8
        assert vg_sp_rate >= 0.8

    def test_both_scenarios_use_same_engine(self):
        """두 시나리오가 동일한 engine/ 코드를 사용한다 (content만 다르다)."""
        e1 = _engine()
        e2 = _engine()
        assert isinstance(e1, type(e2))
        assert len(e1.rules) == len(e2.rules)

    @pytest.mark.slow
    def test_pom_both_scenarios(self):
        """두 시나리오 모두 POM이 작동한다."""
        from content.peter.pom_scorecard import make_peter_scorecard
        from content.vangogh.pom_scorecard import make_vangogh_scorecard
        from engine.simulation.pom import pom_filter

        peter_results = _run_peter_ensemble()
        vg_results = _run_vangogh_ensemble()

        peter_sim_results = [r.extract_agent_result("peter") for r in peter_results]
        vg_sim_results = [r.extract_agent_result("vangogh") for r in vg_results]

        peter_pom = pom_filter(peter_sim_results, make_peter_scorecard())
        vg_pom = pom_filter(vg_sim_results, make_vangogh_scorecard())

        print("\n=== Cross-Scenario POM ===")
        print(f"Peter all_pass: {peter_pom['all_pass_rate']:.1%}")
        print(f"VG all_pass: {vg_pom['all_pass_rate']:.1%}")

        # 두 시나리오 모두 POM이 0%가 아니어야 함
        assert peter_pom["all_pass_rate"] > 0
        assert vg_pom["all_pass_rate"] > 0
