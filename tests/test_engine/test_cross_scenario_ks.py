"""Cross-Scenario Distribution Comparison (Kolmogorov-Smirnov Test).

두 시나리오의 정규화된 event tick 분포를 비교:
- Peter: arrest_tick / 500 (normalized 0~1)
- VG: departure_tick / 150 (normalized 0~1)

H0: 두 분포가 같음 (같은 모양의 곡선)
H1: 다름

KS 통계량 D = max |F_Peter(x) - F_VG(x)|
유의 경계 D_crit(α=0.05) = 1.36 * sqrt((n1+n2)/(n1*n2))

만약 D > D_crit: surface timing 분포 유의 차이 (dual-layer 가설 지지)
만약 D <= D_crit: 분포 유사 (deep universal pattern)
"""

from pathlib import Path

import pytest

from content.caiaphas.domain_politics import PoliticalCalculationState
from content.crowd.domain_crowd import CrowdDynamicsState
from content.gauguin.domain_artistic_ego import ArtisticEgoState
from content.judas.domain_betrayal import BetrayalPsychologyState
from content.peter.domain_faith import FaithJourneyState
from content.theo.domain_patron import PatronState
from content.vangogh.domain_creative import CreativeDriveState
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
register_domain_type("creative_drive", CreativeDriveState)
register_domain_type("artistic_ego", ArtisticEgoState)
register_domain_type("patron", PatronState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"


def _engine() -> RuleEngine:
    return RuleEngine([FearResponseRule(), GriefRule(), HopeRule(), HomeostasisRule()])


def _run_peter(seed: int):
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


def _run_vg(seed: int):
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


def _ks_statistic(xs: list[float], ys: list[float]) -> float:
    """Two-sample KS statistic D = max |F_x - F_y|."""
    combined = sorted(set(xs + ys))
    n_x, n_y = len(xs), len(ys)
    max_d = 0.0
    for v in combined:
        f_x = sum(1 for x in xs if x <= v) / n_x
        f_y = sum(1 for y in ys if y <= v) / n_y
        max_d = max(max_d, abs(f_x - f_y))
    return max_d


def _ks_critical(n1: int, n2: int, alpha: float = 0.05) -> float:
    """Two-sample KS critical value (asymptotic)."""
    c_alpha = {0.1: 1.22, 0.05: 1.36, 0.01: 1.63}[alpha]
    return c_alpha * ((n1 + n2) / (n1 * n2)) ** 0.5


@pytest.mark.slow
class TestCrossScenarioKS:
    def test_normalized_event_tick_distribution(self):
        """Peter arrest_tick/500 vs VG departure_tick/150 분포 KS 비교."""
        n_seeds = 30

        peter_normalized = []
        for seed in range(n_seeds):
            r = _run_peter(seed)
            arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            if arrests:
                peter_normalized.append(arrests[0]["tick"] / 500.0)

        vg_normalized = []
        for seed in range(n_seeds):
            r = _run_vg(seed)
            deps = [t for t in r.fired_triggers if t["trigger_id"] == "gauguin_departure"]
            if deps:
                vg_normalized.append(deps[0]["tick"] / 150.0)

        peter_normalized.sort()
        vg_normalized.sort()

        print(f"\n=== Cross-Scenario KS Test (n_peter={len(peter_normalized)}, "
              f"n_vg={len(vg_normalized)}) ===")
        print(f"Peter normalized: mean {sum(peter_normalized)/len(peter_normalized):.3f}, "
              f"range [{peter_normalized[0]:.3f}, {peter_normalized[-1]:.3f}]")
        print(f"VG normalized:    mean {sum(vg_normalized)/len(vg_normalized):.3f}, "
              f"range [{vg_normalized[0]:.3f}, {vg_normalized[-1]:.3f}]")

        d = _ks_statistic(peter_normalized, vg_normalized)
        d_crit_05 = _ks_critical(len(peter_normalized), len(vg_normalized), 0.05)
        d_crit_01 = _ks_critical(len(peter_normalized), len(vg_normalized), 0.01)

        print(f"\nKS statistic D: {d:.3f}")
        print(f"D_crit (α=0.05): {d_crit_05:.3f}")
        print(f"D_crit (α=0.01): {d_crit_01:.3f}")

        significant_05 = d > d_crit_05
        significant_01 = d > d_crit_01
        print(f"Significant at α=0.05: {'YES' if significant_05 else 'NO'}")
        print(f"Significant at α=0.01: {'YES' if significant_01 else 'NO'}")

        if significant_01:
            print("\n강력한 통계 증거: 두 시나리오의 정규화 timing 분포는 다름")
            print("→ Dual-layer 가설 지지 (surface timing differs)")
        elif significant_05:
            print("\n약한 증거: 분포 차이 있음")
        else:
            print("\n분포가 통계적으로 구별 불가 → surface timing도 유사")

        # 두 분포 상위 quartile 위치
        p75_peter = peter_normalized[int(0.75 * len(peter_normalized))]
        p75_vg = vg_normalized[int(0.75 * len(vg_normalized))]
        print(f"\n75% percentile: Peter {p75_peter:.3f}, VG {p75_vg:.3f}")

        # 최소 검증: D는 > 0 (완전 동일 아니고)
        assert d > 0.05, \
            f"KS stat {d:.3f} suspiciously low"
