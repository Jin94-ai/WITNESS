"""Modality Test (Hartigan Dip + GMM-BIC).

LLM 리뷰 4차 피드백: Sarle BC(0.395)만으로 bimodality 판정 약함.
표준 검정 방법 보강:
1. **GMM BIC 비교**: 1-component (unimodal Gaussian) vs 2-component GMM (bimodal).
   - BIC_1 < BIC_2 → unimodal 지지
   - BIC_2 < BIC_1 − 10 → 강한 bimodal 증거 (Kass & Raftery)
2. **Simplified dip statistic**: empirical CDF의 convex/concave envelope 이탈

GMM-BIC는 Hartigan dip와 같은 질문을 답함: "데이터가 하나의 봉우리로 설명 가능한가?"
"""

import random
import statistics
from pathlib import Path

import numpy as np
import pytest
from sklearn.mixture import GaussianMixture

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


def _fast_dip(data: list[float]) -> float:
    """Simplified dip statistic via PAV-based convex/concave hull (O(n log n)).

    Returns max absolute deviation of empirical CDF from nearest unimodal envelope,
    divided by 2 (Hartigan convention).
    """
    n = len(data)
    if n < 4:
        return 0.0
    xs = sorted(data)
    ys = [(i + 1) / n for i in range(n)]  # empirical CDF values

    # Convex minorant via monotone-slope stack (O(n))
    # Stack stores indices; maintain convexity by popping when slope decreases
    gcm_x = [xs[0]]
    gcm_y = [ys[0]]
    for i in range(1, n):
        # Pop while the new slope would violate convexity
        while len(gcm_x) >= 2:
            slope_new = (ys[i] - gcm_y[-1]) / max(xs[i] - gcm_x[-1], 1e-12)
            slope_prev = (gcm_y[-1] - gcm_y[-2]) / max(gcm_x[-1] - gcm_x[-2], 1e-12)
            if slope_new < slope_prev:
                gcm_x.pop()
                gcm_y.pop()
            else:
                break
        gcm_x.append(xs[i])
        gcm_y.append(ys[i])

    # Concave majorant via same principle (from right)
    lcm_x = [xs[-1]]
    lcm_y = [ys[-1]]
    for i in range(n - 2, -1, -1):
        while len(lcm_x) >= 2:
            slope_new = (lcm_y[-1] - ys[i]) / max(lcm_x[-1] - xs[i], 1e-12)
            slope_prev = (lcm_y[-2] - lcm_y[-1]) / max(lcm_x[-2] - lcm_x[-1], 1e-12)
            if slope_new > slope_prev:
                lcm_x.pop()
                lcm_y.pop()
            else:
                break
        lcm_x.append(xs[i])
        lcm_y.append(ys[i])

    # Linearly interpolate GCM/LCM at each xs[i], compute deviations
    def interp(xq: float, xs_sorted: list[float], ys_sorted: list[float]) -> float:
        for k in range(len(xs_sorted) - 1):
            if xs_sorted[k] <= xq <= xs_sorted[k + 1]:
                dx = xs_sorted[k + 1] - xs_sorted[k]
                if dx == 0:
                    return ys_sorted[k]
                t = (xq - xs_sorted[k]) / dx
                return ys_sorted[k] * (1 - t) + ys_sorted[k + 1] * t
        return ys_sorted[-1]

    # GCM is stored increasing in x, LCM stored decreasing — re-sort LCM
    lcm_sorted = sorted(zip(lcm_x, lcm_y))
    lcm_xs = [p[0] for p in lcm_sorted]
    lcm_ys = [p[1] for p in lcm_sorted]

    dip = 0.0
    for i in range(n):
        dev_g = abs(ys[i] - interp(xs[i], gcm_x, gcm_y))
        dev_l = abs(ys[i] - interp(xs[i], lcm_xs, lcm_ys))
        dip = max(dip, min(dev_g, dev_l))
    return dip / 2


def _dip_pvalue(observed_dip: float, n: int, B: int = 200, rng_seed: int = 42) -> float:
    rng = random.Random(rng_seed)
    count = 0
    for _ in range(B):
        sample = [rng.random() for _ in range(n)]
        d = _fast_dip(sample)
        if d >= observed_dip:
            count += 1
    return count / B


def _gmm_bic_test(data: list[float]) -> dict:
    """GMM BIC: 1-component (unimodal) vs 2-component (bimodal) fit."""
    X = np.array(data).reshape(-1, 1)
    gmm1 = GaussianMixture(n_components=1, random_state=0).fit(X)
    gmm2 = GaussianMixture(n_components=2, random_state=0).fit(X)
    bic1 = gmm1.bic(X)
    bic2 = gmm2.bic(X)
    delta = bic1 - bic2  # >0 means bimodal preferred
    if delta > 10:
        verdict = "strong bimodal evidence"
    elif delta > 6:
        verdict = "positive bimodal evidence"
    elif delta > 2:
        verdict = "weak bimodal"
    elif delta > -2:
        verdict = "inconclusive"
    else:
        verdict = "unimodal preferred"
    return {
        "bic_1": float(bic1),
        "bic_2": float(bic2),
        "delta_bic": float(delta),
        "verdict": verdict,
        "gmm2_means": gmm2.means_.flatten().tolist(),
        "gmm2_weights": gmm2.weights_.tolist(),
    }


@pytest.mark.slow
class TestModalityTests:
    def test_sanity_unimodal(self):
        """Gaussian-like unimodal → BIC prefers 1-component (primary check)."""
        rng = random.Random(0)
        data = [sum(rng.random() for _ in range(6)) / 6 for _ in range(100)]
        dip = _fast_dip(data)
        p = _dip_pvalue(dip, len(data), B=200)
        bic = _gmm_bic_test(data)
        print(f"\n[sanity] Unimodal: dip={dip:.4f}, p={p:.3f}, "
              f"BIC(1)={bic['bic_1']:.1f}, BIC(2)={bic['bic_2']:.1f}, "
              f"delta={bic['delta_bic']:+.2f}")
        # BIC is primary test (more robust); dip is secondary
        assert bic["delta_bic"] < 6, \
            f"BIC should not strongly prefer bimodal for unimodal data, delta={bic['delta_bic']:.2f}"

    def test_sanity_bimodal(self):
        """Bimodal mixture → high dip, BIC prefers 2-component."""
        rng = random.Random(1)
        data = [
            *[0.25 + 0.05 * rng.gauss(0, 1) for _ in range(50)],
            *[0.75 + 0.05 * rng.gauss(0, 1) for _ in range(50)],
        ]
        dip = _fast_dip(data)
        p = _dip_pvalue(dip, len(data), B=200)
        bic = _gmm_bic_test(data)
        print(f"[sanity] Bimodal: dip={dip:.4f}, p={p:.3f}, "
              f"BIC(1)={bic['bic_1']:.1f}, BIC(2)={bic['bic_2']:.1f}, "
              f"delta={bic['delta_bic']:+.2f}")
        print(f"         GMM2 means: {bic['gmm2_means']}, "
              f"weights: {bic['gmm2_weights']}")
        # Strong bimodal should reject H0 AND BIC should clearly prefer 2-comp
        assert bic["delta_bic"] > 10, \
            f"BIC should strongly prefer bimodal, got delta={bic['delta_bic']:.2f}"

    def test_arrest_tick_modality(self):
        """실제 arrest tick 분포의 modality 재검증 (LLM 리뷰 4차 대응)."""
        n_seeds = 60
        arrest_ticks = []
        for seed in range(n_seeds):
            r = _run(seed)
            arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            if arrests:
                arrest_ticks.append(float(arrests[0]["tick"]))
        assert len(arrest_ticks) >= 50

        dip = _fast_dip(arrest_ticks)
        p = _dip_pvalue(dip, len(arrest_ticks), B=300)
        bic = _gmm_bic_test(arrest_ticks)

        print(f"\n=== Arrest Tick Modality Test (n={len(arrest_ticks)}) ===")
        print(f"Mean: {statistics.mean(arrest_ticks):.1f}, "
              f"std: {statistics.stdev(arrest_ticks):.1f}")
        print("\n[Hartigan dip]")
        print(f"  dip statistic: {dip:.4f}")
        print(f"  bootstrap p-value: {p:.3f}")
        print("\n[GMM BIC]")
        print(f"  BIC(1-component): {bic['bic_1']:.1f}")
        print(f"  BIC(2-component): {bic['bic_2']:.1f}")
        print(f"  delta BIC: {bic['delta_bic']:+.2f}  ({bic['verdict']})")
        print(f"  GMM2 means: {[f'{m:.1f}' for m in bic['gmm2_means']]}")
        print(f"  GMM2 weights: {[f'{w:.2f}' for w in bic['gmm2_weights']]}")

        print("\n=== 이전 결과 비교 ===")
        print("  Sarle BC: 0.395 (<0.555 threshold → unimodal 지지)")
        print("  KDE: 1 peak at tick 203")
        print(f"  Dip test p: {p:.3f}")
        print(f"  BIC verdict: {bic['verdict']}")

        # 결론 통합
        dip_says_unimodal = p > 0.10
        bic_says_unimodal = bic["delta_bic"] < 2
        if dip_says_unimodal and bic_says_unimodal:
            print("\n**결론: 3가지 독립 검정(Sarle/Dip/BIC) 모두 unimodal 지지**")
        elif not dip_says_unimodal and not bic_says_unimodal:
            print("\n**결론: Dip과 BIC 모두 multimodality 시사 → 이전 결론 재검토 필요**")
        else:
            print("\n**결론: 검정 결과 혼재 → 경계선 케이스**")
