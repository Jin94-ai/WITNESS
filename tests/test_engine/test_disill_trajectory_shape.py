"""Judas Disillusionment Trajectory Shape.

평균 Judas disill 궤적이 linear / exponential / sigmoid 중 어떤 shape?

방법:
- 시드별 궤적 집계 → 평균 곡선
- 세 가지 모델 fit (least squares)
- R² 비교

시그모이드 fit이 좋으면: 비선형 regime switch (accumulation then jump)
Linear이면: steady growth
Exponential이면: positive feedback
"""

import math
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


def _r_squared(y_true: list[float], y_pred: list[float]) -> float:
    mean_y = sum(y_true) / len(y_true)
    ss_res = sum((y_true[i] - y_pred[i]) ** 2 for i in range(len(y_true)))
    ss_tot = sum((y - mean_y) ** 2 for y in y_true)
    if ss_tot == 0:
        return 0.0
    return 1 - ss_res / ss_tot


def _fit_linear(xs: list[float], ys: list[float]) -> tuple[float, float]:
    """OLS y = a*x + b."""
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    den = sum((x - mx) ** 2 for x in xs)
    a = num / den if den > 0 else 0
    b = my - a * mx
    return a, b


@pytest.mark.slow
class TestDisillTrajectoryShape:
    def test_trajectory_shape_fit(self):
        """평균 Judas disill 궤적의 linear/exp/sigmoid fit 비교."""
        n_seeds = 15
        sample_ticks = list(range(0, 200, 10))

        # Collect disill at each tick, for each seed
        trajectories: list[list[float]] = []
        for seed in range(n_seeds):
            r = _run(seed)
            snaps = r.state_snapshots.get("judas", {})
            traj = []
            for t in sample_ticks:
                candidates = [tk for tk in snaps if tk <= t]
                if candidates:
                    traj.append(snaps[max(candidates)].domain_state.disillusionment)
                else:
                    traj.append(0)
            trajectories.append(traj)

        # Average trajectory
        mean_traj = [
            statistics.mean(trajectories[s][i] for s in range(len(trajectories)))
            for i in range(len(sample_ticks))
        ]

        print(f"\n=== Average Judas disill trajectory (n={n_seeds}) ===")
        for i, t in enumerate(sample_ticks):
            bar = "#" * int(mean_traj[i] * 3)
            print(f"  tick {t:>3}: {mean_traj[i]:.2f} {bar}")

        xs = [float(t) for t in sample_ticks]

        # 1. Linear fit
        a_lin, b_lin = _fit_linear(xs, mean_traj)
        y_lin = [a_lin * x + b_lin for x in xs]
        r2_lin = _r_squared(mean_traj, y_lin)

        # 2. Exponential fit: y = a * (1 - exp(-k*x)) + y0
        # Simplified: fit y - y0 to log-linearized form after subtracting baseline
        # y_max ~ 10.0, baseline ~ 3.0
        y_max = max(mean_traj) + 1
        y_baseline = min(mean_traj)
        # Transform: log((y_max - y) / (y_max - y_baseline)) = -k*x
        valid = [
            (xs[i], math.log((y_max - mean_traj[i]) / (y_max - y_baseline)))
            for i in range(len(xs))
            if y_max > mean_traj[i] and y_max - y_baseline > 0
        ]
        if valid:
            vx = [v[0] for v in valid]
            vy = [v[1] for v in valid]
            k, _ = _fit_linear(vx, vy)
            k = -k  # slope should be negative in transformed space
            y_exp = [
                y_baseline + (y_max - y_baseline) * (1 - math.exp(-k * x))
                for x in xs
            ]
            r2_exp = _r_squared(mean_traj, y_exp)
        else:
            r2_exp = 0.0

        # 3. Sigmoid fit: y = L / (1 + exp(-k*(x-x0))) + y0
        # Fit parameters L, k, x0, y0 using simple grid search
        best_r2_sig = -1
        best_params = None
        y0 = y_baseline
        L = y_max - y_baseline
        for x0 in [50, 75, 100, 125, 150]:
            for k in [0.01, 0.02, 0.03, 0.05, 0.08, 0.1]:
                y_sig = [y0 + L / (1 + math.exp(-k * (x - x0))) for x in xs]
                r2 = _r_squared(mean_traj, y_sig)
                if r2 > best_r2_sig:
                    best_r2_sig = r2
                    best_params = (x0, k)

        print("\nFit comparison (R²):")
        print(f"  Linear:      {r2_lin:.4f}")
        print(f"  Exponential: {r2_exp:.4f}")
        print(f"  Sigmoid (x0={best_params[0]}, k={best_params[1]}): {best_r2_sig:.4f}")

        # 어느 shape이 가장 잘 맞는가
        if best_r2_sig > r2_exp and best_r2_sig > r2_lin:
            print("\n**Best fit: Sigmoid** (non-linear regime switch)")
            print(f"  Transition point x0 = {best_params[0]}, steepness k = {best_params[1]}")
        elif r2_exp > r2_lin:
            print("\n**Best fit: Exponential** (positive feedback/saturation)")
        else:
            print("\n**Best fit: Linear** (steady growth)")

        # Linear fit R² < 0.98 정도면 non-linear dynamic 존재
        if r2_lin < 0.98:
            nonlinear_advantage = max(r2_exp, best_r2_sig) - r2_lin
            print(f"Nonlinear advantage over linear: {nonlinear_advantage:.4f}")

        assert r2_lin > 0.8, "Trajectory should be at least monotone (linear-ish)"
        # 실측: linear이 best fit (R²=0.998 > sigmoid 0.966 > exp 0.784)
        # 4차 LLM 리뷰 교정: global shape는 LINEAR, 이산성은 trigger에서 발생
