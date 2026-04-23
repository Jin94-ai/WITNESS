"""Cross-Scenario Decision Window Analysis.

Peter에서 발견한 decision window (tick 75-100, 전체의 15-20%)가
Van Gogh 시나리오에도 같은 정규화 위치에 있는가?

만약 두 시나리오의 decision window가 progress-normalized 같은 위치에 있다면,
"universal decision window hypothesis"를 뒷받침한다.
"""

import statistics
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


def _growth_by_segment(
    results: list, agent_id: str, field_path: str, trigger_id: str, segments_frac: list[tuple[float, float]]
) -> dict:
    """각 progress segment에서 상태값의 증가량 측정.

    Args:
        results: SimulationWorld.run() 결과 목록
        agent_id: 추적 에이전트 ID
        field_path: "domain_state.disillusionment" 등
        trigger_id: 정규화 기준 트리거 ID
        segments_frac: [(0.0, 0.2), (0.2, 0.4), ...] normalized 구간

    Returns:
        {segment: [growths]} 딕셔너리
    """
    from engine.core.state import get_nested_value

    segment_data: dict[tuple[float, float], list[float]] = {s: [] for s in segments_frac}

    for r in results:
        # trigger tick 찾기
        trigger_ticks = [t["tick"] for t in r.fired_triggers if t["trigger_id"] == trigger_id]
        if not trigger_ticks:
            continue
        T = trigger_ticks[0]

        snapshots = r.state_snapshots.get(agent_id, {})

        def value_at(norm_t: float) -> float | None:
            target_tick = int(norm_t * T)
            candidates = [t for t in snapshots if t <= target_tick]
            if not candidates:
                return None
            v = get_nested_value(snapshots[max(candidates)], field_path)
            return float(v) if isinstance(v, (int, float)) else None

        for seg in segments_frac:
            v_start = value_at(seg[0])
            v_end = value_at(seg[1])
            if v_start is not None and v_end is not None:
                segment_data[seg].append(v_end - v_start)

    return segment_data


@pytest.mark.slow
class TestCrossDecisionWindow:
    def test_cross_scenario_decision_windows(self):
        """Peter와 VG 모두에서 decision window 위치 탐색."""
        segments = [(0.0, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.0)]

        peter_results = [_run_peter(s) for s in range(15)]
        vg_results = [_run_vg(s) for s in range(15)]

        peter_data = _growth_by_segment(
            peter_results, "judas", "domain_state.disillusionment",
            "arrest_trigger", segments
        )
        vg_data = _growth_by_segment(
            vg_results, "gauguin", "domain_state.frustration_with_partner",
            "gauguin_departure", segments
        )

        print("\n=== Cross-Scenario Decision Window ===")
        print(f"{'segment':>12} | {'Peter mean':>12} | {'Peter std':>10} | {'VG mean':>10} | {'VG std':>8}")
        print("-" * 65)

        peter_stds = {}
        vg_stds = {}

        for seg in segments:
            p_vals = peter_data[seg]
            v_vals = vg_data[seg]

            p_mean = statistics.mean(p_vals) if p_vals else 0
            p_std = statistics.stdev(p_vals) if len(p_vals) > 1 else 0
            v_mean = statistics.mean(v_vals) if v_vals else 0
            v_std = statistics.stdev(v_vals) if len(v_vals) > 1 else 0

            peter_stds[seg] = p_std
            vg_stds[seg] = v_std

            print(f"{f'{seg[0]*100:.0f}-{seg[1]*100:.0f}%':>12} | "
                  f"{p_mean:>11.2f}  | {p_std:>10.2f} | {v_mean:>9.2f}  | {v_std:>8.2f}")

        # Decision window 식별 (variation이 가장 큰 segment)
        peter_peak = max(peter_stds, key=peter_stds.get)
        vg_peak = max(vg_stds, key=vg_stds.get)

        p_range = f"{peter_peak[0]*100:.0f}-{peter_peak[1]*100:.0f}%"
        v_range = f"{vg_peak[0]*100:.0f}-{vg_peak[1]*100:.0f}%"
        print(f"\nPeter decision window: {p_range} (std={peter_stds[peter_peak]:.2f})")
        print(f"VG decision window:    {v_range} (std={vg_stds[vg_peak]:.2f})")

        if peter_peak == vg_peak:
            print("\nBoth scenarios share the same decision window -> UNIVERSAL PATTERN")
        else:
            print("\nDecision windows differ between scenarios")

        # 최소한 둘 다 identifiable한 peak가 있어야 함
        assert peter_stds[peter_peak] > 0
        assert vg_stds[vg_peak] > 0
