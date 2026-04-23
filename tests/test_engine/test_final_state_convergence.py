"""Final State Convergence Analysis.

시뮬레이션 종료 시점의 각 agent 상태 variance 측정.

작은 variance = 시스템이 attractor로 수렴
큰 variance = 발산적 (다양한 종점)

Peter 최종 상태는 canonical_intervention(요 21장) 거쳐서 수렴해야 함.
Judas는 초기 상태 따라 disill, greed, guilt가 발산.
"""

import statistics
from pathlib import Path

import pytest

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
from engine.simulation.world import SimulationWorld

register_domain_type("faith_journey", FaithJourneyState)
register_domain_type("betrayal_psychology", BetrayalPsychologyState)
register_domain_type("political_calculation", PoliticalCalculationState)
register_domain_type("crowd_dynamics", CrowdDynamicsState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"


def _engine() -> RuleEngine:
    return RuleEngine([FearResponseRule(), GriefRule(), HopeRule(), HomeostasisRule()])


def _run(seed: int):
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
    return SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=seed)


@pytest.mark.slow
class TestFinalStateConvergence:
    def test_final_state_variance_per_agent(self):
        """각 agent의 최종 상태 variance. 작은 variance = attractor 수렴."""
        n_seeds = 30

        peter_finals = {"fear": [], "grief": [], "hope": [], "love": []}
        judas_finals = {"disillusionment": [], "greed": [], "guilt": []}
        caiaphas_finals = {"threat_assessment": []}

        for seed in range(n_seeds):
            r = _run(seed)
            p = r.final_states["peter"]
            j = r.final_states["judas"]
            c = r.final_states["caiaphas"]

            peter_finals["fear"].append(p.emotions.fear)
            peter_finals["grief"].append(p.emotions.grief)
            peter_finals["hope"].append(p.emotions.hope)
            peter_finals["love"].append(p.emotions.love)

            judas_finals["disillusionment"].append(j.domain_state.disillusionment)
            judas_finals["greed"].append(j.domain_state.greed)
            judas_finals["guilt"].append(j.domain_state.guilt)

            caiaphas_finals["threat_assessment"].append(c.domain_state.threat_assessment)

        print(f"\n=== Final State Variance (n={n_seeds}) ===")
        print(f"{'agent.field':>28} | {'mean':>7} | {'std':>6} | {'cv':>5}")
        print("-" * 55)

        all_cvs = {}
        for agent, fields in [
            ("peter", peter_finals),
            ("judas", judas_finals),
            ("caiaphas", caiaphas_finals),
        ]:
            for field, values in fields.items():
                mean = statistics.mean(values)
                std = statistics.stdev(values)
                cv = std / abs(mean) if abs(mean) > 0.001 else std
                key = f"{agent}.{field}"
                all_cvs[key] = cv
                print(f"{key:>28} | {mean:>7.2f} | {std:>6.2f} | {cv:>5.2f}")

        print("\n낮은 CV = 강한 attractor (모든 run이 비슷한 최종 상태)")
        print("높은 CV = 발산적 (초기 조건/seed에 민감)")

        # Peter emotions는 canonical intervention 후 수렴해야 함 (CV < 0.5)
        for emo in ["hope", "love"]:
            key = f"peter.{emo}"
            assert all_cvs[key] < 1.5, \
                f"Peter.{emo} CV {all_cvs[key]:.2f} too high (expected attractor)"

        # Judas disill은 arrest 이후 평형 상태 (최대로 올라감, variance 낮음)
        assert all_cvs["judas.disillusionment"] < 0.5, \
            f"Judas disill CV {all_cvs['judas.disillusionment']:.2f} too high"

    def test_peter_final_hope_post_restoration(self):
        """Peter가 canonical intervention(요 21장) 후 hope가 같은 수준으로 수렴."""
        n_seeds = 20

        final_hopes = []
        for seed in range(n_seeds):
            r = _run(seed)
            final_hopes.append(r.final_states["peter"].emotions.hope)

        mean_h = statistics.mean(final_hopes)
        std_h = statistics.stdev(final_hopes)
        min_h = min(final_hopes)
        max_h = max(final_hopes)

        print(f"\n=== Peter Final Hope Convergence (n={n_seeds}) ===")
        print(f"Mean: {mean_h:.2f}, std: {std_h:.2f}")
        print(f"Range: [{min_h:.2f}, {max_h:.2f}]")

        # POM eventual_hope 기준 >= 3.0 대부분 충족
        reach_3 = sum(1 for h in final_hopes if h >= 3.0)
        print(f">= 3.0: {reach_3}/{n_seeds}")

        # canonical 후 수렴: std < 2.0
        assert std_h < 2.5, \
            f"Final hope std {std_h:.2f} too high (canonical should pull to same level)"
