"""Arrest Tick Distribution Shape Analysis.

N=100 replication에서 관찰된 카테고리 분포: very_early 0, early 55, mid 45, late 0.
이것이 진짜 bimodal (두 개의 구별되는 modes)인가, 아니면 단일 peak with spread인가?

검증 방법:
1. Bimodality coefficient (Sarle's formula)
2. Histogram-based peak detection
3. Early (<200) vs Mid (>=200) 평균의 Cohen's d
4. Hartigan's dip test 간이 버전 (gap 기반)
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
from engine.simulation.statistics import cohens_d
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


def _bimodality_coefficient(data: list[float]) -> float:
    """Sarle's BC = (skew^2 + 1) / (kurtosis + 3*(n-1)^2 / ((n-2)*(n-3))).
    BC > 0.555: bimodal suggested.
    BC < 0.555: unimodal.
    """
    n = len(data)
    if n < 4:
        return 0.0
    mean = statistics.mean(data)
    sd = statistics.stdev(data)
    if sd == 0:
        return 0.0
    # Skewness (Fisher-Pearson)
    m3 = sum((x - mean) ** 3 for x in data) / n
    skew = m3 / (sd ** 3)
    # Excess kurtosis
    m4 = sum((x - mean) ** 4 for x in data) / n
    kurt = m4 / (sd ** 4) - 3
    correction = 3 * (n - 1) ** 2 / ((n - 2) * (n - 3))
    bc = (skew ** 2 + 1) / (kurt + correction)
    return bc


def _histogram(data: list[float], n_bins: int = 20) -> list[int]:
    if not data:
        return []
    mn, mx = min(data), max(data)
    if mn == mx:
        return [len(data)]
    bins = [0] * n_bins
    bin_width = (mx - mn) / n_bins
    for v in data:
        idx = min(int((v - mn) / bin_width), n_bins - 1)
        bins[idx] += 1
    return bins


def _count_peaks(hist: list[int], min_prominence: int = 2) -> int:
    """간단한 peak counting: local maxima with min separation."""
    peaks = 0
    for i in range(1, len(hist) - 1):
        if hist[i] > hist[i - 1] and hist[i] > hist[i + 1] and hist[i] >= min_prominence:
            peaks += 1
    return peaks


@pytest.mark.slow
class TestArrestDistribution:
    def test_bimodality_analysis(self):
        """Arrest tick 분포가 bimodal인가?"""
        n_seeds = 60
        arrest_ticks = []
        for seed in range(n_seeds):
            r = _run(seed)
            arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            if arrests:
                arrest_ticks.append(arrests[0]["tick"])

        assert len(arrest_ticks) >= 50, "Need enough samples"

        mean = statistics.mean(arrest_ticks)
        sd = statistics.stdev(arrest_ticks)
        bc = _bimodality_coefficient([float(t) for t in arrest_ticks])

        print(f"\n=== Arrest Tick Distribution Analysis (n={len(arrest_ticks)}) ===")
        print(f"Mean: {mean:.1f}, std: {sd:.1f}")
        print(f"Range: [{min(arrest_ticks)}, {max(arrest_ticks)}]")
        print(f"Bimodality coefficient (Sarle): {bc:.3f}")
        print("Threshold for bimodality: > 0.555")
        print(f"Interpretation: {'BIMODAL' if bc > 0.555 else 'unimodal'} suggested")

        # Histogram-based peak detection
        hist = _histogram([float(t) for t in arrest_ticks], n_bins=15)
        print(f"\nHistogram (15 bins): {hist}")
        n_peaks = _count_peaks(hist, min_prominence=3)
        print(f"Detected peaks: {n_peaks}")

        # Early vs Mid split analysis (based on n=100 earlier finding)
        early = [t for t in arrest_ticks if t < 200]
        mid = [t for t in arrest_ticks if t >= 200]
        print(f"\nEarly (<200): n={len(early)}, mean={statistics.mean(early) if early else 0:.1f}")
        print(f"Mid  (>=200): n={len(mid)}, mean={statistics.mean(mid) if mid else 0:.1f}")

        if early and mid:
            d = cohens_d(early, mid).cohens_d
            gap = statistics.mean(mid) - statistics.mean(early)
            print(f"Mean gap: {gap:.1f} ticks")
            print(f"Cohen's d (early vs mid): {d:.2f}")

        # Unimodality vs bimodality decision
        if bc > 0.555:
            print("\nCONCLUSION: Bimodal distribution suggested.")
            print("이는 시스템이 두 개의 구별되는 attractor(빠른/중간 arrest)를 생성함을 의미.")
        else:
            print("\nCONCLUSION: Unimodal (single attractor with spread).")
            print("Arrest timing은 연속 분포, 인위적 category 구분은 편의상.")

        # 최소 검증: std가 적절 (완전 deterministic 아님)
        assert sd > 10, f"Std {sd:.1f} too low (expected stochastic variation)"
        # 최소 검증: mean이 합리적 범위
        assert 150 < mean < 250, f"Mean arrest tick {mean:.1f} outside expected range"

    def test_arrest_kde_estimate(self):
        """간이 kernel density로 peak 개수 확인."""
        n_seeds = 50
        arrest_ticks = []
        for seed in range(n_seeds):
            r = _run(seed)
            arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            if arrests:
                arrest_ticks.append(float(arrests[0]["tick"]))

        if len(arrest_ticks) < 20:
            pytest.skip("not enough samples")

        # Gaussian KDE
        sd = statistics.stdev(arrest_ticks)
        n = len(arrest_ticks)
        # Silverman's bandwidth
        bw = 1.06 * sd * (n ** (-1 / 5))

        # Evaluate KDE at grid points
        mn, mx = min(arrest_ticks), max(arrest_ticks)
        n_grid = 50
        step = (mx - mn) / (n_grid - 1)
        grid = [mn + i * step for i in range(n_grid)]

        def kde_at(x: float) -> float:
            # Gaussian kernel sum
            norm = 1 / (n * bw * (2 * math.pi) ** 0.5)
            return norm * sum(math.exp(-0.5 * ((x - xi) / bw) ** 2) for xi in arrest_ticks)

        densities = [kde_at(g) for g in grid]
        # Find peaks in density
        peaks = []
        for i in range(1, len(densities) - 1):
            if densities[i] > densities[i - 1] and densities[i] > densities[i + 1]:
                if densities[i] > max(densities) * 0.3:  # significant height
                    peaks.append((grid[i], densities[i]))

        print(f"\n=== KDE Peak Analysis (n={n}, bw={bw:.1f}) ===")
        print(f"Range: [{mn:.0f}, {mx:.0f}]")
        print(f"Significant peaks (density > 30% of max): {len(peaks)}")
        for p_tick, p_dens in peaks:
            print(f"  Peak at tick {p_tick:.0f}, density {p_dens:.5f}")

        # 최소 하나의 peak 존재
        assert len(peaks) >= 1
