"""Action Count Regression: predicting arrest tick from action frequencies.

각 run의 Peter/Judas 행동 빈도를 feature로, arrest_tick을 target으로 회귀.
어떤 행동 빈도가 arrest_tick을 가장 잘 예측하는가?

간단 linear regression (closed-form OLS) 사용.
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

pytestmark = pytest.mark.archived  # Tier 3 archived (ITERATION_CLASSIFICATION.md)

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


def _pearson_r(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    if n < 2:
        return 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    dx = sum((x - mx) ** 2 for x in xs) ** 0.5
    dy = sum((y - my) ** 2 for y in ys) ** 0.5
    if dx == 0 or dy == 0:
        return 0.0
    return num / (dx * dy)


@pytest.mark.slow
class TestActionRegression:
    def test_action_counts_vs_arrest(self):
        """각 run의 행동 빈도와 arrest tick의 Pearson 상관."""
        n_seeds = 25

        # Action counts per run before arrest
        action_counts: list[dict[str, int]] = []
        arrest_ticks: list[int] = []

        for seed in range(n_seeds):
            r = _run(seed)
            arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            if not arrests:
                continue
            at = arrests[0]["tick"]
            arrest_ticks.append(at)

            # Count actions BEFORE arrest for both Peter and Judas
            counts: dict[str, int] = {}
            for agent in ["peter", "judas"]:
                for rec in r.action_histories.get(agent, []):
                    if rec.tick >= at:
                        continue
                    key = f"{agent}.{rec.chosen_action}"
                    counts[key] = counts.get(key, 0) + 1
            action_counts.append(counts)

        # Collect all actions that appear in at least 50% of runs
        all_actions: dict[str, int] = {}
        for counts in action_counts:
            for k in counts:
                all_actions[k] = all_actions.get(k, 0) + 1

        common_actions = [a for a, c in all_actions.items() if c >= len(arrest_ticks) * 0.5]

        print(f"\n=== Action Count → Arrest Tick Pearson (n={len(arrest_ticks)}) ===")
        print(f"{'action':>35} | {'r':>7} | {'mean count':>12}")
        print("-" * 62)

        correlations = []
        for act in common_actions:
            counts = [c.get(act, 0) for c in action_counts]
            r_val = _pearson_r([float(c) for c in counts], [float(t) for t in arrest_ticks])
            mean_c = statistics.mean(counts)
            correlations.append((act, r_val, mean_c))

        # Sort by |r|
        correlations.sort(key=lambda x: -abs(x[1]))
        for act, r_val, mean_c in correlations[:12]:
            print(f"{act:>35} | {r_val:>+7.3f} | {mean_c:>12.1f}")

        # 양의 상관: 해당 행동 많이 할수록 arrest 늦음
        # 음의 상관: 해당 행동 많이 할수록 arrest 이름
        top = correlations[0]
        print(f"\nTop correlate: {top[0]} (r={top[1]:+.3f})")

        if top[1] > 0:
            print("→ 이 행동 많이 할수록 arrest 늦음 (late arrest와 연관)")
        else:
            print("→ 이 행동 많이 할수록 arrest 이름 (early arrest와 연관)")

        # 최소 한 action에서 |r| > 0.4
        assert abs(correlations[0][1]) > 0.4, \
            f"Top correlation {correlations[0][1]:.3f} too weak"

    def test_judas_inform_vs_arrest(self):
        """Judas inform_authorities 횟수와 arrest 시점 특히 측정."""
        n_seeds = 25

        inform_counts = []
        arrest_ticks = []
        for seed in range(n_seeds):
            r = _run(seed)
            arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            if not arrests:
                continue
            at = arrests[0]["tick"]
            arrest_ticks.append(at)

            n_inform = sum(
                1 for rec in r.action_histories.get("judas", [])
                if rec.chosen_action == "inform_authorities" and rec.tick < at
            )
            inform_counts.append(n_inform)

        r_val = _pearson_r(
            [float(c) for c in inform_counts],
            [float(t) for t in arrest_ticks],
        )
        mean_inform = statistics.mean(inform_counts)

        print("\n=== Judas inform_authorities count (pre-arrest) ===")
        print(f"n={len(arrest_ticks)}, mean count: {mean_inform:.1f}")
        print(f"Pearson r vs arrest_tick: {r_val:+.3f}")
        if r_val > 0:
            print("양의 상관: 더 많이 inform할수록 arrest 늦음")
            print("(inform 자체보다 betray가 결정적 - inform은 feeder 행동)")
        else:
            print("음의 상관: inform이 많을수록 arrest 빠름 (inform→surveillance→arrest)")
