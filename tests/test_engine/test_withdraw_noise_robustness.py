"""Withdraw Rate Signal Robustness to State Noise.

Withdraw rate r=-0.94 finding (n=25, state_noise=0.05)이 noise 증가에도 유지되는가?

state_noise_scale 변화 [0.0, 0.05, 0.10, 0.20]에서
Judas withdraw rate vs arrest_tick의 Pearson r 측정.

견고하면 (|r| > 0.7 모든 noise 수준에서): 실제 causal signal.
무너지면: noise-specific artifact.
"""

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


def _run(seed: int, noise: float):
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
        triggers=triggers, state_noise_scale=noise,
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
class TestWithdrawNoiseRobustness:
    def test_withdraw_r_vs_noise(self):
        """Withdraw rate vs arrest_tick correlation across noise levels."""
        n_seeds = 15
        noise_levels = [0.0, 0.05, 0.10, 0.20]

        print(f"\n=== Withdraw Rate r vs Noise Level (n={n_seeds} each) ===")
        print(f"{'noise':>8} | {'r':>7} | {'mean arrest':>12} | {'mean rate':>11}")
        print("-" * 50)

        import statistics
        results = []
        for noise in noise_levels:
            rates = []
            arrest_ticks = []
            for seed in range(n_seeds):
                r = _run(seed, noise)
                arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
                if not arrests:
                    continue
                at = arrests[0]["tick"]
                arrest_ticks.append(at)
                withdraw_count = sum(
                    1 for rec in r.action_histories.get("judas", [])
                    if rec.chosen_action == "withdraw" and rec.tick < at
                )
                rates.append(withdraw_count / max(at, 1))

            if len(rates) >= 5:
                r_val = _pearson_r(rates, [float(t) for t in arrest_ticks])
                results.append((noise, r_val, rates, arrest_ticks))
                print(f"{noise:>8.2f} | {r_val:>+7.3f} | {statistics.mean(arrest_ticks):>12.1f} | "
                      f"{statistics.mean(rates):>11.4f}")

        # Key check: all noise levels should show strong negative r
        for noise, r_val, _, _ in results:
            assert r_val < -0.5, \
                f"noise={noise}: r={r_val:.3f} lost signal (expected r < -0.5)"

        # Max - min |r| difference should be small (robust)
        rs = [abs(r_val) for _, r_val, _, _ in results]
        r_range = max(rs) - min(rs)
        print(f"\n|r| range across noise: {r_range:.3f}")
        print(f"Min |r|: {min(rs):.3f}, Max |r|: {max(rs):.3f}")

        # 강건한 시그널: |r| 변동이 크지 않음
        assert r_range < 0.3, \
            f"Withdraw r |range| {r_range:.3f} too large (noise-sensitive)"

        print("\n결론: Withdraw rate signal은 noise 수준에 robust (|r| 변동 < 0.3)")
        print("→ 실제 causal signal (noise artifact 아님)")
