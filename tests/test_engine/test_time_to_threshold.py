"""Time-to-Threshold Analysis.

Judas disillusionment이 특정 임계값을 언제 최초로 넘는가?
- threshold 5.0: "환멸 활성화" (중간 수준)
- threshold 7.0: "심각한 환멸"
- threshold 8.0: "arrest_trigger state 조건"
- threshold 9.0: "극한 환멸"

검증:
1. 각 임계값에 도달하는 tick의 분포 (mean, CI, range)
2. 임계값-도달tick의 correlation과 arrest_tick의 관계
3. "속도 패턴": 7→8 단계가 가장 결정적인가?

의의:
- 기존 forecast 분석은 "tick 200에서 disill이 얼마인가?"
- 이 분석은 "disill이 얼마일 때 몇 tick인가?" (역의 관점)
- 두 관점이 일관된 insight 주면 robust.
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
from engine.simulation.statistics import confidence_interval
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


def _first_crossing(r, threshold: float) -> int | None:
    """Judas disillusionment이 threshold를 처음 넘는 tick."""
    snapshots = r.state_snapshots.get("judas", {})
    if not snapshots:
        return None
    for tick in sorted(snapshots.keys()):
        if snapshots[tick].domain_state.disillusionment >= threshold:
            return tick
    return None


@pytest.mark.slow
class TestTimeToThreshold:
    def test_threshold_crossings(self):
        """각 임계값 도달 tick의 분포 측정."""
        n_seeds = 30
        thresholds = [5.0, 6.0, 7.0, 8.0, 9.0]

        data = {t: [] for t in thresholds}
        arrest_ticks = []

        for seed in range(n_seeds):
            r = _run(seed)
            for t in thresholds:
                tk = _first_crossing(r, t)
                if tk is not None:
                    data[t].append(tk)
            arrests = [x for x in r.fired_triggers if x["trigger_id"] == "arrest_trigger"]
            if arrests:
                arrest_ticks.append(arrests[0]["tick"])

        print(f"\n=== Time-to-Threshold (n={n_seeds}) ===")
        print(f"{'threshold':>10} | {'mean tick':>10} | {'95% CI':>18} | "
              f"{'median':>7} | {'n_reached':>10}")
        print("-" * 68)
        for t in thresholds:
            ticks = data[t]
            if ticks:
                ci = confidence_interval(ticks)
                med = statistics.median(ticks)
                print(f"{t:>10.1f} | {ci.mean:>10.1f} | "
                      f"[{ci.lower:>5.1f}, {ci.upper:>5.1f}] | "
                      f"{med:>7.0f} | {len(ticks):>3}/{n_seeds:>3}")

        arrest_ci = confidence_interval(arrest_ticks)
        print(
            f"\nArrest tick: {arrest_ci.mean:.1f} "
            f"[{arrest_ci.lower:.1f}, {arrest_ci.upper:.1f}] "
            f"(n={len(arrest_ticks)})"
        )

        # 검증 1: 임계값 올라갈수록 도달 tick이 늦어진다 (단조)
        means = [statistics.mean(data[t]) for t in thresholds if data[t]]
        for i in range(1, len(means)):
            assert means[i] >= means[i - 1] - 3, \
                f"threshold={thresholds[i]} mean tick {means[i]:.1f} < "\
                f"threshold={thresholds[i-1]} mean tick {means[i-1]:.1f}"

        # 검증 2: 각 임계값이 arrest_tick보다 먼저 도달 (인과 순서)
        # arrest_trigger 조건은 disill >= 8.0이므로, threshold 8.0 도달 tick <= arrest_tick
        if data[8.0] and arrest_ticks:
            # pairwise 확인은 seed 일치가 필요하므로 mean으로 근사
            assert statistics.mean(data[8.0]) <= statistics.mean(arrest_ticks) + 5, \
                f"disill->=8 mean {statistics.mean(data[8.0]):.1f} "\
                f">= arrest mean {statistics.mean(arrest_ticks):.1f}"

        # 검증 3: 7->8 구간의 속도가 5->6, 6->7보다 상당히 다름 (decision window)
        # 간단화: 임계값 간 평균 tick 차이 계산
        if all(data[t] for t in thresholds):
            gaps = {}
            for i in range(1, len(thresholds)):
                prev = statistics.mean(data[thresholds[i-1]])
                cur = statistics.mean(data[thresholds[i]])
                gaps[f"{thresholds[i-1]}->{thresholds[i]}"] = cur - prev
            print("\nGap (tick) between thresholds:")
            for k, v in gaps.items():
                print(f"  {k}: {v:.1f}")

    def test_threshold_crossing_predicts_arrest(self):
        """Threshold 도달 tick과 arrest tick의 pairwise 상관."""
        n_seeds = 30
        threshold = 7.0  # 중간 수준 임계

        pairs = []
        for seed in range(n_seeds):
            r = _run(seed)
            tk = _first_crossing(r, threshold)
            arrests = [x for x in r.fired_triggers if x["trigger_id"] == "arrest_trigger"]
            if tk is not None and arrests:
                pairs.append((tk, arrests[0]["tick"]))

        if len(pairs) < 10:
            pytest.skip("Not enough pairs")

        # Pearson correlation
        xs = [p[0] for p in pairs]
        ys = [p[1] for p in pairs]
        mx = statistics.mean(xs)
        my = statistics.mean(ys)
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        dx = sum((x - mx) ** 2 for x in xs) ** 0.5
        dy = sum((y - my) ** 2 for y in ys) ** 0.5
        r_corr = num / (dx * dy) if dx > 0 and dy > 0 else 0

        print(f"\n=== Threshold {threshold} Reach Tick vs Arrest Tick ===")
        print(f"n={len(pairs)}")
        print(f"Pearson r: {r_corr:.3f}")
        print(f"Mean reach tick: {mx:.1f}")
        print(f"Mean arrest tick: {my:.1f}")
        print(f"Mean gap: {my - mx:.1f} ticks")

        # 양의 상관: 늦게 threshold 도달 -> 늦게 arrest
        assert r_corr > 0.3, \
            f"Expected positive correlation between threshold crossing and arrest, got {r_corr:.3f}"
