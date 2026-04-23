"""Van Gogh Time-to-Threshold Analysis (Peter 대응).

Peter에서: disill 5→6 39.1t, 6→7 34.7t, **7→8 24.9t** (가속), 8→9 27.8t.
VG에서 같은 패턴이 보이는가?
- Gauguin frustration 5→6, 6→7, 7→8 (trigger threshold), 8→9 gap 측정
- 7→8 구간이 다른 구간보다 짧으면 **cross-scenario 가속 패턴 공통**

이는 "surface timing은 다르지만 deep pattern은 동일" dual-layer 가설 강화.
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
from engine.simulation.statistics import confidence_interval
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


def _first_crossing_frust(r, threshold: float) -> int | None:
    snapshots = r.state_snapshots.get("gauguin", {})
    if not snapshots:
        return None
    for tick in sorted(snapshots.keys()):
        if snapshots[tick].domain_state.frustration_with_partner >= threshold:
            return tick
    return None


@pytest.mark.slow
class TestVGTimeToThreshold:
    def test_vg_threshold_gap_pattern(self):
        """VG에서 7→8 구간이 가속하는가 (Peter 대응 검증)."""
        n_seeds = 30
        thresholds = [5.0, 6.0, 7.0, 8.0, 9.0]

        data: dict[float, list[int]] = {t: [] for t in thresholds}
        dep_ticks = []

        for seed in range(n_seeds):
            r = _run(seed)
            for th in thresholds:
                tk = _first_crossing_frust(r, th)
                if tk is not None:
                    data[th].append(tk)
            deps = [x for x in r.fired_triggers if x["trigger_id"] == "gauguin_departure"]
            if deps:
                dep_ticks.append(deps[0]["tick"])

        print(f"\n=== VG Time-to-Threshold (n={n_seeds}) ===")
        print(f"{'threshold':>10} | {'mean tick':>10} | {'95% CI':>18} | "
              f"{'median':>7} | {'n_reached':>10}")
        print("-" * 68)
        means = {}
        for th in thresholds:
            ticks = data[th]
            if ticks:
                ci = confidence_interval(ticks)
                med = statistics.median(ticks)
                means[th] = ci.mean
                print(f"{th:>10.1f} | {ci.mean:>10.1f} | "
                      f"[{ci.lower:>5.1f}, {ci.upper:>5.1f}] | "
                      f"{med:>7.0f} | {len(ticks):>3}/{n_seeds:>3}")

        if dep_ticks:
            dep_ci = confidence_interval(dep_ticks)
            print(
                f"\nDeparture tick: {dep_ci.mean:.1f} "
                f"[{dep_ci.lower:.1f}, {dep_ci.upper:.1f}] (n={len(dep_ticks)})"
            )

        # Gap 분석
        if all(t in means for t in thresholds):
            gaps = {}
            for i in range(1, len(thresholds)):
                gap = means[thresholds[i]] - means[thresholds[i - 1]]
                gaps[f"{thresholds[i-1]}->{thresholds[i]}"] = gap
            print("\nGap between thresholds (tick):")
            for k, v in gaps.items():
                print(f"  {k}: {v:.1f}")

            # 7→8 gap이 5→6 또는 6→7 gap보다 작거나 비슷
            g_56 = gaps["5.0->6.0"]
            g_67 = gaps["6.0->7.0"]
            g_78 = gaps["7.0->8.0"]
            print("\nPeter reference: 5→6=39.1, 6→7=34.7, 7→8=24.9 (가속)")
            print(f"VG actual:       5→6={g_56:.1f}, 6→7={g_67:.1f}, 7→8={g_78:.1f}")

            if g_78 <= min(g_56, g_67):
                print("\nVG에서도 7→8 구간 가속 확인 -> Cross-scenario 공통 패턴")
            else:
                print("\nVG에서는 다른 가속 패턴. Peter와 다른 표면 dynamics.")

        # 단조성 검증
        sorted_means = [means[t] for t in thresholds if t in means]
        for i in range(1, len(sorted_means)):
            assert sorted_means[i] >= sorted_means[i - 1] - 3, \
                f"Threshold means should be monotone: {sorted_means}"

    def test_vg_threshold_predicts_departure(self):
        """VG threshold 도달 tick과 departure tick의 상관."""
        n_seeds = 30
        threshold = 6.0  # VG는 스케일이 다르므로 mid-value

        pairs = []
        for seed in range(n_seeds):
            r = _run(seed)
            tk = _first_crossing_frust(r, threshold)
            deps = [x for x in r.fired_triggers if x["trigger_id"] == "gauguin_departure"]
            if tk is not None and deps:
                pairs.append((tk, deps[0]["tick"]))

        if len(pairs) < 10:
            pytest.skip("Not enough pairs")

        xs = [p[0] for p in pairs]
        ys = [p[1] for p in pairs]
        mx = statistics.mean(xs)
        my = statistics.mean(ys)
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        dx = sum((x - mx) ** 2 for x in xs) ** 0.5
        dy = sum((y - my) ** 2 for y in ys) ** 0.5
        r_corr = num / (dx * dy) if dx > 0 and dy > 0 else 0

        print(f"\n=== VG Threshold {threshold} Reach vs Departure ===")
        print(f"n={len(pairs)}")
        print(f"Pearson r: {r_corr:.3f}")
        print(f"Mean reach tick: {mx:.1f}")
        print(f"Mean departure tick: {my:.1f}")
        print(f"Mean gap: {my - mx:.1f} ticks")
        print("Peter reference (threshold 7.0 -> arrest): r=0.938, gap=31.5")

        assert r_corr > 0.3, \
            f"Expected positive correlation, got {r_corr:.3f}"
