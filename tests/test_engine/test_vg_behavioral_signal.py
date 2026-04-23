"""VG Behavioral Rate Signal Analysis (Cross-Scenario Test of Peter Finding).

Peter 결과: Judas withdraw rate vs arrest_tick r=-0.942.
VG 시나리오에서도 행동 비율이 departure_tick 예측에 쓸 수 있는가?

VG 후보 행동:
- Gauguin: withdraw_to_studio, threaten_departure, critique
- VG: despair, paint_feverishly, seek_connection
"""

import statistics
from pathlib import Path

import pytest

from content.gauguin.domain_artistic_ego import ArtisticEgoState
from content.theo.domain_patron import PatronState
from content.vangogh.domain_creative import CreativeDriveState
from engine.core.world import SimulationConfig
from engine.io.loader import (
    load_agent_state,
    load_behavior_profile,
    load_hazard_events,
    load_triggers,
    register_domain_type,
)
from engine.rules.base import RuleEngine
from engine.rules.emotional import FearResponseRule, GriefRule, HopeRule
from engine.rules.temporal import HomeostasisRule
from engine.simulation.world import SimulationWorld

pytestmark = pytest.mark.archived  # Tier 3 archived (ITERATION_CLASSIFICATION.md)

register_domain_type("creative_drive", CreativeDriveState)
register_domain_type("artistic_ego", ArtisticEgoState)
register_domain_type("patron", PatronState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"


def _engine() -> RuleEngine:
    return RuleEngine([FearResponseRule(), GriefRule(), HopeRule(), HomeostasisRule()])


def _run(seed: int):
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
        hazard_events=hazards, triggers=triggers, state_noise_scale=0.05,
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
class TestVGBehavioralSignal:
    def test_vg_action_rates_vs_departure(self):
        """VG action rates vs departure_tick correlation."""
        n_seeds = 25
        action_rates: list[dict[str, float]] = []
        dep_ticks: list[int] = []

        for seed in range(n_seeds):
            r = _run(seed)
            deps = [t for t in r.fired_triggers if t["trigger_id"] == "gauguin_departure"]
            if not deps:
                continue
            dt = deps[0]["tick"]
            dep_ticks.append(dt)

            counts: dict[str, int] = {}
            for agent in ["vangogh", "gauguin", "theo"]:
                for rec in r.action_histories.get(agent, []):
                    if rec.tick >= dt:
                        continue
                    key = f"{agent}.{rec.chosen_action}"
                    counts[key] = counts.get(key, 0) + 1

            total = max(dt, 1)
            rates = {k: v / total for k, v in counts.items()}
            action_rates.append(rates)

        # common actions
        all_keys: dict[str, int] = {}
        for rates in action_rates:
            for k in rates:
                all_keys[k] = all_keys.get(k, 0) + 1
        common = [k for k, c in all_keys.items() if c >= len(dep_ticks) * 0.5]

        print(f"\n=== VG Action Rate vs Departure Tick (n={len(dep_ticks)}) ===")
        print(f"{'action':>36} | {'r':>7} | {'mean rate':>11}")
        print("-" * 61)

        correlations = []
        for act in common:
            rates_vec = [r.get(act, 0.0) for r in action_rates]
            r_val = _pearson_r(rates_vec, [float(t) for t in dep_ticks])
            mean_r = statistics.mean(rates_vec)
            correlations.append((act, r_val, mean_r))

        correlations.sort(key=lambda x: -abs(x[1]))
        for act, r_val, mean_r in correlations[:12]:
            print(f"{act:>36} | {r_val:>+7.3f} | {mean_r:>11.4f}")

        # Peter 참조 결과
        print("\nPeter 참조: judas.withdraw rate r=-0.942 (early-warning)")
        print("VG의 등가 행동은?")

        # Strongest negative correlate (early-warning signal)
        neg_candidates = [(a, r) for a, r, _ in correlations if r < -0.3]
        if neg_candidates:
            top_neg = min(neg_candidates, key=lambda x: x[1])
            print(f"VG top negative: {top_neg[0]} (r={top_neg[1]:+.3f})")
        pos_candidates = [(a, r) for a, r, _ in correlations if r > 0.3]
        if pos_candidates:
            top_pos = max(pos_candidates, key=lambda x: x[1])
            print(f"VG top positive: {top_pos[0]} (r={top_pos[1]:+.3f})")

        # 최소 한 방향이라도 |r| > 0.4
        max_r = max(abs(r) for _, r, _ in correlations)
        assert max_r > 0.4, f"No VG action with strong correlation (max|r|={max_r:.2f})"
