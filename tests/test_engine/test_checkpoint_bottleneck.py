"""Per-Checkpoint Match Rate Analysis.

진행도: event-relative checkpoint 35.5% → 80.3% match rate 달성.
어떤 checkpoint가 여전히 병목인가?

각 checkpoint의 pass rate + phi(checkpoint→overall_match) 측정.
"""

import json
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
from engine.rules.emotional import FearResponseRule, GriefRule, HopeRule, LoveRule
from engine.rules.physical import FatigueRule, HungerRule
from engine.rules.temporal import HomeostasisRule
from engine.simulation.checkpoint import Checkpoint
from engine.simulation.world import SimulationWorld

register_domain_type("faith_journey", FaithJourneyState)
register_domain_type("betrayal_psychology", BetrayalPsychologyState)
register_domain_type("political_calculation", PoliticalCalculationState)
register_domain_type("crowd_dynamics", CrowdDynamicsState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"


def _engine() -> RuleEngine:
    return RuleEngine([
        FatigueRule(), HungerRule(),
        FearResponseRule(), HopeRule(), GriefRule(), LoveRule(),
        HomeostasisRule(),
    ])


def _run(seed: int):
    peter = load_agent_state(CONTENT_DIR / "peter" / "initial_state.json")
    judas = load_agent_state(CONTENT_DIR / "judas" / "initial_state.json")
    caiaphas = load_agent_state(CONTENT_DIR / "caiaphas" / "initial_state.json")
    crowd = load_agent_state(CONTENT_DIR / "crowd" / "initial_state.json")
    triggers = load_triggers(CONTENT_DIR / "shared" / "triggers.json")
    hazards = load_hazard_events(CONTENT_DIR / "peter" / "hazard_events.json")
    interventions = load_interventions(CONTENT_DIR / "peter" / "canonical_events.json")
    cp_data = json.loads(
        (CONTENT_DIR / "peter" / "checkpoints_multi.json").read_text(encoding="utf-8")
    )
    peter_cps = [Checkpoint.model_validate(cp) for cp in cp_data["checkpoints"]]

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
    return SimulationWorld(
        config, _engine(),
        behavior_profiles=profiles,
        checkpoints={"peter": peter_cps},
    ).run(seed=seed)


@pytest.mark.slow
class TestCheckpointBottleneck:
    def test_per_checkpoint_match_rate(self):
        """각 checkpoint의 match rate + 전체 match rate와 상관."""
        from engine.simulation.statistics import proportion_ci
        n_seeds = 30

        # Run and collect checkpoint results
        per_run: list[dict[str, bool]] = []
        for seed in range(n_seeds):
            r = _run(seed)
            cps = r.checkpoint_results.get("peter", [])
            d = {cp.checkpoint_id: cp.passed for cp in cps}
            per_run.append(d)

        if not per_run or not per_run[0]:
            pytest.skip("no checkpoints")

        cp_ids = list(per_run[0].keys())

        print(f"\n=== Per-Checkpoint Match Rate (n={n_seeds}) ===")
        print(f"{'checkpoint':>28} | {'pass rate':>10} | {'95% CI':>18} | {'phi':>7}")
        print("-" * 75)

        # Overall match rate per run = fraction of passed
        overall_match = [sum(r.values()) / len(r) for r in per_run]

        results = []
        for cp_id in cp_ids:
            passes = sum(1 for r in per_run if r[cp_id])
            ci = proportion_ci(passes, n_seeds)

            # Phi with "this run >= median match rate"
            import statistics
            median_match = statistics.median(overall_match)
            high_match = [overall_match[i] >= median_match for i in range(n_seeds)]

            a = sum(1 for i in range(n_seeds) if per_run[i][cp_id] and high_match[i])
            b = sum(1 for i in range(n_seeds) if per_run[i][cp_id] and not high_match[i])
            c = sum(1 for i in range(n_seeds) if not per_run[i][cp_id] and high_match[i])
            d = sum(1 for i in range(n_seeds) if not per_run[i][cp_id] and not high_match[i])

            denom = ((a + b) * (c + d) * (a + c) * (b + d)) ** 0.5
            phi = (a * d - b * c) / denom if denom > 0 else 0

            results.append((cp_id, ci, phi))
            print(f"{cp_id:>28} | {ci.mean:>10.1%} | "
                  f"[{ci.lower:>5.1%}, {ci.upper:>5.1%}] | {phi:>6.3f}")

        # Overall stats
        overall_ci = proportion_ci(
            sum(1 for m in overall_match if m >= 0.5), n_seeds
        )
        print(f"\nOverall match >= 50%: {overall_ci.mean:.0%}")

        # 가장 낮은 pass rate 찾기
        bottleneck = min(results, key=lambda x: x[1].mean)
        print(f"\nBottleneck checkpoint: {bottleneck[0]} ({bottleneck[1].mean:.1%})")
        # 가장 높은 pass rate
        best = max(results, key=lambda x: x[1].mean)
        print(f"Best (universal): {best[0]} ({best[1].mean:.1%})")

        # 각 checkpoint 최소 5% 이상 통과
        for cp_id, ci, _ in results:
            assert ci.mean > 0.05, \
                f"Checkpoint {cp_id} pass rate {ci.mean:.0%} too low"
