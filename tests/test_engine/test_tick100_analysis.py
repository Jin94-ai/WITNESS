"""Tick 100 Uncertainty Peak - 정밀 분석.

이전 발견: tick 100에서 예측 정확도 최저점 (20%).
여기서 정확히 무슨 일이 일어나는가?

가설:
1. Disillusionment 변곡점: 이 시점에 기울기가 급변
2. 경로 분기: 시드별로 disillusionment가 다른 방향으로 갈림
3. Trigger 접근: 임계값(8.0)에 접근하는 run과 아닌 run의 분리
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


def _get_disill_at(result, target_tick: int) -> float | None:
    judas_snaps = result.state_snapshots.get("judas", {})
    candidates = [t for t in judas_snaps if t <= target_tick]
    if not candidates:
        return None
    return judas_snaps[max(candidates)].domain_state.disillusionment


@pytest.mark.slow
class TestTick100Analysis:
    def test_disillusionment_spread_by_tick(self):
        """여러 tick에서 disillusionment 분산(std) 측정.

        예상: disill std가 어느 tick에서 최대인가?
        - 초기: 모두 같은 초기값 -> std 작음
        - 중간: 경로 갈라짐 -> std 큼
        - 후기: 트리거 발동 후 saturate -> std 작음
        """
        n_seeds = 25
        check_ticks = [25, 50, 75, 100, 125, 150, 175, 200, 250]

        disill_by_tick: dict[int, list[float]] = {t: [] for t in check_ticks}

        for seed in range(n_seeds):
            r = _run(seed)
            for t in check_ticks:
                v = _get_disill_at(r, t)
                if v is not None:
                    disill_by_tick[t].append(v)

        print(f"\n=== Disillusionment Spread by Tick (n={n_seeds}) ===")
        print(f"{'tick':>5} | {'mean':>5} | {'std':>5} | {'min':>5} | {'max':>5}")
        print("-" * 40)

        for t in check_ticks:
            vals = disill_by_tick[t]
            if len(vals) > 1:
                mean = statistics.mean(vals)
                std = statistics.stdev(vals)
                print(f"{t:>5} | {mean:>5.1f} | {std:>5.2f} | {min(vals):>5.1f} | {max(vals):>5.1f}")

        # std가 어느 tick에서 최대인지
        stds = {t: statistics.stdev(vals) if len(vals) > 1 else 0 for t, vals in disill_by_tick.items()}
        peak_tick = max(stds, key=stds.get)
        print(f"\nMaximum spread at tick {peak_tick} (std={stds[peak_tick]:.2f})")

    def test_path_divergence_near_tick100(self):
        """tick 100 부근에서 경로가 여러 그룹으로 갈라지는지 확인.

        가설: 이 시점에 disill이 'quickly accumulating' vs 'stagnant' 그룹으로 분기.
        """
        n_seeds = 25
        tick_100_disill = []
        for seed in range(n_seeds):
            r = _run(seed)
            v = _get_disill_at(r, 100)
            arrests = [t for t in r.fired_triggers if t["trigger_id"] == "arrest_trigger"]
            arrest_tick = arrests[0]["tick"] if arrests else 500
            if v is not None:
                tick_100_disill.append((v, arrest_tick))

        # tick 100 disill 히스토그램
        print("\n=== Tick 100 Disillusionment Distribution ===")
        bins = [(0, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 10)]
        for lo, hi in bins:
            count = sum(1 for v, _ in tick_100_disill if lo <= v < hi)
            bar = "#" * count
            print(f"  [{lo:.0f}-{hi:.0f}): {bar} ({count})")

        # disill이 "낮음"(<5)인 그룹과 "높음"(>=5)인 그룹의 arrest tick 비교
        low_group = [at for v, at in tick_100_disill if v < 5]
        high_group = [at for v, at in tick_100_disill if v >= 5]

        print(f"\nLow disill at tick 100 (<5): n={len(low_group)}")
        if low_group:
            print(f"  Mean arrest tick: {statistics.mean(low_group):.0f}")
        print(f"High disill at tick 100 (>=5): n={len(high_group)}")
        if high_group:
            print(f"  Mean arrest tick: {statistics.mean(high_group):.0f}")

        # 두 그룹이 실제로 다른 결과를 보이는지
        if low_group and high_group and len(low_group) > 1 and len(high_group) > 1:
            low_mean = statistics.mean(low_group)
            high_mean = statistics.mean(high_group)
            # high disill 그룹은 더 이른 arrest
            assert high_mean < low_mean, "High disill at tick 100 should yield earlier arrest"

    def test_growth_rate_around_tick100(self):
        """tick 75-125 구간의 disillusionment 증가율 측정.

        이 구간이 peak 증가율이면 "확률적 분기가 가장 활발한 구간" 가설 지지.
        """
        n_seeds = 20
        segments = [(25, 50), (50, 75), (75, 100), (100, 125), (125, 150), (150, 175)]

        segment_growths: dict[tuple[int, int], list[float]] = {s: [] for s in segments}

        for seed in range(n_seeds):
            r = _run(seed)
            for start, end in segments:
                v_start = _get_disill_at(r, start)
                v_end = _get_disill_at(r, end)
                if v_start is not None and v_end is not None:
                    segment_growths[(start, end)].append(v_end - v_start)

        print("\n=== Disillusionment Growth Rate by Segment ===")
        print(f"{'segment':>15} | {'mean growth':>12} | {'std':>5}")
        print("-" * 45)

        for seg, growths in segment_growths.items():
            if len(growths) > 1:
                mean_g = statistics.mean(growths)
                std_g = statistics.stdev(growths)
                print(f"{f'{seg[0]}-{seg[1]}':>15} | {mean_g:>11.2f}  | {std_g:>5.2f}")
