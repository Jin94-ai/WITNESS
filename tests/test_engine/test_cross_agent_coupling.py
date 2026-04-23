"""Cross-Agent State Coupling Analysis.

"에이전트 A의 상태가 에이전트 B의 상태와 어떻게 연관되는가?"

측정:
- Judas disillusionment vs Peter fear (tick별 시계열 상관)
- Judas disillusionment vs Caiaphas threat_assessment
- Peter fear vs Crowd hostility

검증:
- 정방향 coupling이 존재하는가?
- Lagged correlation: A의 변화가 얼마나 지연되어 B에 반영되는가?
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


def _collect_timeseries(r, agent: str, field_path: str, ticks: list[int]) -> list[float]:
    """특정 tick마다 agent의 상태 값 추출. field_path는 'domain_state.disillusionment' 형태."""
    snaps = r.state_snapshots.get(agent, {})
    result = []
    for t in ticks:
        candidates = [tk for tk in snaps if tk <= t]
        if not candidates:
            result.append(0.0)
            continue
        s = snaps[max(candidates)]
        # field_path 해석
        parts = field_path.split(".")
        obj = s
        for p in parts:
            obj = getattr(obj, p)
        result.append(float(obj))
    return result


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
class TestCrossAgentCoupling:
    def test_judas_disill_vs_peter_fear(self):
        """Judas disill과 Peter fear의 시계열 상관."""
        n_seeds = 15
        sample_ticks = list(range(50, 250, 10))

        correlations = []
        for seed in range(n_seeds):
            r = _run(seed)
            judas_disill = _collect_timeseries(r, "judas", "domain_state.disillusionment", sample_ticks)
            peter_fear = _collect_timeseries(r, "peter", "emotions.fear", sample_ticks)
            rho = _pearson_r(judas_disill, peter_fear)
            correlations.append(rho)

        import statistics
        mean_r = statistics.mean(correlations)
        std_r = statistics.stdev(correlations)
        pos_count = sum(1 for r in correlations if r > 0)

        print(f"\n=== Judas disill vs Peter fear (n={n_seeds}) ===")
        print(f"Mean Pearson r: {mean_r:.3f}")
        print(f"Std Pearson r: {std_r:.3f}")
        print(f"Positive correlations: {pos_count}/{n_seeds}")

        # 양의 상관 지배 (Judas 환멸 상승 시 Peter 공포 상승)
        assert pos_count >= n_seeds * 0.7, \
            f"Only {pos_count}/{n_seeds} positive (expected >= 70%)"
        assert mean_r > 0.3, f"Mean r {mean_r:.3f} too weak"

    def test_judas_disill_vs_caiaphas_threat(self):
        """Judas disill과 Caiaphas threat_assessment의 상관."""
        n_seeds = 15
        sample_ticks = list(range(50, 250, 10))

        correlations = []
        for seed in range(n_seeds):
            r = _run(seed)
            judas_d = _collect_timeseries(
                r, "judas", "domain_state.disillusionment", sample_ticks
            )
            caia_t = _collect_timeseries(
                r, "caiaphas", "domain_state.threat_assessment", sample_ticks
            )
            rho = _pearson_r(judas_d, caia_t)
            correlations.append(rho)

        import statistics
        mean_r = statistics.mean(correlations)
        pos_count = sum(1 for r in correlations if r > 0)

        print(f"\n=== Judas disill vs Caiaphas threat (n={n_seeds}) ===")
        print(f"Mean Pearson r: {mean_r:.3f}")
        print(f"Positive correlations: {pos_count}/{n_seeds}")

        # Judas → Caiaphas 경로 존재: inform_authorities -> surveillance
        # 강한 양의 상관 기대
        assert mean_r > 0.5, \
            f"Judas disill-Caiaphas threat coupling weak (r={mean_r:.3f})"

    def test_lagged_cross_correlation(self):
        """Lagged cross-correlation: Judas disill leads Peter fear?

        r(lag=k): Judas(t) vs Peter(t+k).
        최대 상관 lag가 양수이면 Judas가 leading indicator.
        """
        n_seeds = 10
        sample_ticks = list(range(50, 250, 5))

        lags = [-30, -20, -10, 0, 10, 20, 30]
        lag_correlations = {lag: [] for lag in lags}

        for seed in range(n_seeds):
            r = _run(seed)
            for lag in lags:
                shifted_judas_ticks = [t for t in sample_ticks if 50 <= t + lag <= 250]
                peter_ticks_at_shift = [t + lag for t in shifted_judas_ticks]
                j = _collect_timeseries(
                    r, "judas", "domain_state.disillusionment", shifted_judas_ticks
                )
                p = _collect_timeseries(r, "peter", "emotions.fear", peter_ticks_at_shift)
                if len(j) == len(p) and len(j) > 2:
                    rho = _pearson_r(j, p)
                    lag_correlations[lag].append(rho)

        import statistics

        print(f"\n=== Lagged Cross-Correlation Judas→Peter fear (n={n_seeds}) ===")
        print(f"{'lag':>6} | {'mean r':>8}")
        print("-" * 20)
        mean_by_lag = {}
        for lag in lags:
            vals = lag_correlations[lag]
            if vals:
                m = statistics.mean(vals)
                mean_by_lag[lag] = m
                print(f"{lag:>+6} | {m:>8.3f}")

        # Best lag
        if mean_by_lag:
            best_lag = max(mean_by_lag.keys(), key=lambda k: mean_by_lag[k])
            print(f"\nBest lag: {best_lag:+} (r={mean_by_lag[best_lag]:.3f})")
            print("양수 lag: Judas가 leading indicator (earlier change in Judas "
                  "precedes Peter change)")
