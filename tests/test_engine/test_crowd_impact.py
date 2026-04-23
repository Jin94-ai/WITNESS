"""군중 영향 분���: 3-agent vs 4-agent 비교.

군중 추가가 체포 시점, Peter 행동, 전체 경로에 미치는 영향을 정량화.
"""

import statistics
from collections import Counter
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
N_SEEDS = 15


def _engine() -> RuleEngine:
    return RuleEngine([FearResponseRule(), GriefRule(), HopeRule(), HomeostasisRule()])


def _run_3agent(n_seeds=N_SEEDS):
    peter = load_agent_state(CONTENT_DIR / "peter" / "initial_state.json")
    judas = load_agent_state(CONTENT_DIR / "judas" / "initial_state.json")
    caiaphas = load_agent_state(CONTENT_DIR / "caiaphas" / "initial_state.json")
    triggers = load_triggers(CONTENT_DIR / "shared" / "triggers.json")
    hazards = load_hazard_events(CONTENT_DIR / "peter" / "hazard_events.json")
    interventions = load_interventions(CONTENT_DIR / "peter" / "canonical_events.json")
    profiles = {
        "peter": load_behavior_profile(CONTENT_DIR / "peter" / "behavior_profile.json"),
        "judas": load_behavior_profile(CONTENT_DIR / "judas" / "behavior_profile.json"),
        "caiaphas": load_behavior_profile(CONTENT_DIR / "caiaphas" / "behavior_profile.json"),
    }
    config = SimulationConfig(
        max_tick=500, initial_state=peter,
        initial_states=[peter, judas, caiaphas],
        hazard_events=hazards, interventions=interventions,
        triggers=triggers, state_noise_scale=0.05,
    )
    results = []
    for seed in range(n_seeds):
        results.append(SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=seed))
    return results


def _run_4agent(n_seeds=N_SEEDS):
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
    results = []
    for seed in range(n_seeds):
        results.append(SimulationWorld(config, _engine(), behavior_profiles=profiles).run(seed=seed))
    return results


@pytest.mark.slow
class TestCrowdImpact:
    def test_crowd_effect_on_peter_behavior(self):
        """군중 유무에 따른 Peter 행동 분포 ���교."""
        r3 = _run_3agent()
        r4 = _run_4agent()

        def _peter_action_dist(results):
            counts = Counter()
            for r in results:
                for a in r.action_histories.get("peter", []):
                    counts[a.chosen_action] += 1
            total = sum(counts.values())
            return {k: v / total for k, v in counts.items()} if total > 0 else {}

        dist_3 = _peter_action_dist(r3)
        dist_4 = _peter_action_dist(r4)

        print("\n=== Peter Action Distribution ===")
        all_actions = sorted(set(list(dist_3.keys()) + list(dist_4.keys())))
        print(f"{'action':>25} | {'3-agent':>8} | {'4-agent':>8} | {'delta':>8}")
        print("-" * 55)
        for a in all_actions:
            v3 = dist_3.get(a, 0)
            v4 = dist_4.get(a, 0)
            delta = v4 - v3
            print(f"{a:>25} | {v3:>7.1%} | {v4:>7.1%} | {delta:>+7.1%}")

        # 군중이 있으면 withdraw_in_fear 비율이 높아져야 함
        w3 = dist_3.get("withdraw_in_fear", 0)
        w4 = dist_4.get("withdraw_in_fear", 0)
        print(f"\nwithdraw_in_fear: 3-agent={w3:.1%}, 4-agent={w4:.1%}")

    def test_crowd_effect_on_arrest_timing(self):
        """군중 유무에 따른 체포 시점 비교."""
        r3 = _run_3agent()
        r4 = _run_4agent()

        def _arrest_ticks(results):
            ticks = []
            for r in results:
                arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
                if arrests and arrests[0]["tick"] < 400:
                    ticks.append(arrests[0]["tick"])
            return ticks

        t3 = _arrest_ticks(r3)
        t4 = _arrest_ticks(r4)

        m3 = statistics.mean(t3) if t3 else 0
        m4 = statistics.mean(t4) if t4 else 0

        print("\n=== Arrest Timing ===")
        print(f"3-agent: mean={m3:.0f}, n={len(t3)}/{N_SEEDS}")
        print(f"4-agent: mean={m4:.0f}, n={len(t4)}/{N_SEEDS}")
        print(f"Delta: {m4 - m3:+.0f} ticks")
