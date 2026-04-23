"""Action RATE Regression (time-confound free).

이전 action count regression은 모든 r이 positive (time confound).
해법: count 대신 rate (count / total_ticks)로 정규화.

어떤 행동의 RATE(비율)가 arrest_tick을 예측하는가?
- Positive rate correlation: 해당 행동 비율이 높을수록 arrest 늦음 (late-pattern 행동)
- Negative rate correlation: 해당 행동 비율이 높을수록 arrest 이름 (early-trigger 행동)
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
class TestActionRateRegression:
    def test_action_rates_vs_arrest(self):
        """각 run의 행동 비율(count/pre_arrest_ticks)과 arrest tick의 Pearson."""
        n_seeds = 25

        action_rates: list[dict[str, float]] = []
        arrest_ticks: list[int] = []

        for seed in range(n_seeds):
            r = _run(seed)
            arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            if not arrests:
                continue
            at = arrests[0]["tick"]
            arrest_ticks.append(at)

            # Count actions BEFORE arrest + normalize by pre-arrest ticks
            counts: dict[str, int] = {}
            for agent in ["peter", "judas"]:
                for rec in r.action_histories.get(agent, []):
                    if rec.tick >= at:
                        continue
                    key = f"{agent}.{rec.chosen_action}"
                    counts[key] = counts.get(key, 0) + 1

            total_ticks = max(at, 1)  # pre-arrest tick count
            rates = {k: v / total_ticks for k, v in counts.items()}
            action_rates.append(rates)

        # Filter to common actions (>= 50% of runs)
        all_keys: dict[str, int] = {}
        for rates in action_rates:
            for k in rates:
                all_keys[k] = all_keys.get(k, 0) + 1
        common = [k for k, c in all_keys.items() if c >= len(arrest_ticks) * 0.5]

        print(f"\n=== Action Rate → Arrest Tick Pearson (n={len(arrest_ticks)}) ===")
        print(f"{'action':>35} | {'r':>7} | {'mean rate':>11}")
        print("-" * 60)

        correlations = []
        for act in common:
            rates_vec = [r.get(act, 0.0) for r in action_rates]
            r_val = _pearson_r(rates_vec, [float(t) for t in arrest_ticks])
            mean_r = statistics.mean(rates_vec)
            correlations.append((act, r_val, mean_r))

        correlations.sort(key=lambda x: -abs(x[1]))
        for act, r_val, mean_r in correlations[:12]:
            print(f"{act:>35} | {r_val:>+7.3f} | {mean_r:>11.4f}")

        # Separate positive (late-pattern) vs negative (early-trigger)
        pos_actions = [(a, r) for a, r, _ in correlations if r > 0.3]
        neg_actions = [(a, r) for a, r, _ in correlations if r < -0.3]

        print(f"\nPositive rate (late-arrest pattern): {len(pos_actions)}")
        for a, r in pos_actions[:5]:
            print(f"  {a}: r={r:+.3f}")
        print(f"\nNegative rate (early-trigger): {len(neg_actions)}")
        for a, r in neg_actions[:5]:
            print(f"  {a}: r={r:+.3f}")

        # 이제 양/음 두 방향 모두 나타나야 함 (time confound 제거)
        assert len(correlations) > 5, "Need enough actions"

    def test_judas_inform_rate_inversion(self):
        """Judas inform_authorities rate: count 분석에서 r=+0.704였음.
        Rate로 바꾸면 방향 전환?
        """
        n_seeds = 25

        rates = []
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
            rates.append(n_inform / max(at, 1))

        r_val = _pearson_r(rates, [float(t) for t in arrest_ticks])
        mean_rate = statistics.mean(rates)

        print("\n=== Judas inform_authorities RATE (pre-arrest) ===")
        print(f"n={len(arrest_ticks)}, mean rate: {mean_rate:.4f} per tick")
        print(f"Pearson r vs arrest_tick: {r_val:+.3f}")
        print("Count 분석 참조값: r=+0.704 (time confound)")

        if r_val < 0:
            print("→ Rate 분석 후 음의 상관: inform 비율 높을수록 arrest 이름 (인과 방향 드러남)")
        else:
            print("→ Rate 분석도 양의 상관 (inform은 count와 rate 모두 late과 연관)")
