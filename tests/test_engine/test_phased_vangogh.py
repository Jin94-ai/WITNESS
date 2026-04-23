"""Van Gogh scenario through PhasedSimulationWorld — engine neutrality proof (Iter 34).

ABSOLUTE RULE #1 (인물 비종속) 검증: v1.2 phase-linked 머신이 Peter뿐 아니라
Van Gogh (전혀 다른 domain, 다른 agents, 다른 rule set)에서도 작동하는가?

검증 포인트:
1. VG 3-agent config을 Phase 1개로 감싸 실행 — 정상 완주.
2. VG hazard events는 per_tick 기본값 — legacy 동작 보존.
3. phases=None 직접 실행과 Phase 1개 감싼 실행 결과 동일 (delegate 검증).
4. time_axis 편의 method (extract_absolute_trajectory)가 VG에서도 작동.
"""

from pathlib import Path

import pytest

from content.gauguin.domain_artistic_ego import ArtisticEgoState
from content.theo.domain_patron import PatronState
from content.vangogh.domain_creative import CreativeDriveState
from engine.core.phase import Phase, PhaseExitCondition
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
from engine.simulation.phased_world import (
    PhasedMultiAgentResult,
    PhasedSimulationWorld,
)
from engine.simulation.world import SimulationWorld

CONTENT = Path(__file__).resolve().parent.parent.parent / "content"


@pytest.fixture(scope="module")
def _setup_domain():
    register_domain_type("creative_drive", CreativeDriveState)
    register_domain_type("artistic_ego", ArtisticEgoState)
    register_domain_type("patron", PatronState)
    return None


def _rules() -> RuleEngine:
    return RuleEngine([
        FearResponseRule(), GriefRule(), HopeRule(), HomeostasisRule(),
    ])


def _build_vg_config(with_phase: bool, max_tick: int = 100):
    vg = load_agent_state(CONTENT / "vangogh" / "initial_state.json")
    gauguin = load_agent_state(CONTENT / "gauguin" / "initial_state.json")
    theo = load_agent_state(CONTENT / "theo" / "initial_state.json")
    triggers = load_triggers(CONTENT / "vangogh" / "triggers.json")
    hazards = load_hazard_events(CONTENT / "vangogh" / "hazard_events.json")
    kwargs = dict(
        max_tick=max_tick,
        initial_state=vg,
        initial_states=[vg, gauguin, theo],
        triggers=triggers,
        hazard_events=hazards,
        state_noise_scale=0.0,
    )
    if with_phase:
        kwargs["phases"] = [
            Phase(
                phase_id="arles",
                agents_active=["vangogh", "gauguin", "theo"],
                tick_scale_hours=2.0,
                exit_condition=PhaseExitCondition(max_tick=max_tick),
            ),
        ]
    return SimulationConfig(**kwargs)


def _profiles():
    return {
        "vangogh": load_behavior_profile(CONTENT / "vangogh" / "behavior_profile.json"),
        "gauguin": load_behavior_profile(CONTENT / "gauguin" / "behavior_profile.json"),
        "theo": load_behavior_profile(CONTENT / "theo" / "behavior_profile.json"),
    }


class TestVanGoghSinglePhase:
    def test_runs_with_phased_world(self, _setup_domain):
        config = _build_vg_config(with_phase=True, max_tick=50)
        world = PhasedSimulationWorld(
            config, _rules(), behavior_profiles=_profiles(),
        )
        result = world.run(seed=42)
        assert isinstance(result, PhasedMultiAgentResult)
        assert "vangogh" in result.final_states
        assert "gauguin" in result.final_states
        assert "theo" in result.final_states

    def test_phased_single_phase_matches_legacy(self, _setup_domain):
        """phase 1개 감싼 실행과 phases=None 실행이 동일 수치."""
        cfg_legacy = _build_vg_config(with_phase=False, max_tick=50)
        cfg_phased = _build_vg_config(with_phase=True, max_tick=50)

        legacy = SimulationWorld(
            cfg_legacy, _rules(), behavior_profiles=_profiles(),
        ).run(seed=42)
        phased = PhasedSimulationWorld(
            cfg_phased, _rules(), behavior_profiles=_profiles(),
        ).run(seed=42)

        # fear 동일 (seed=42, noise=0)
        assert (
            legacy.final_states["vangogh"].emotions.fear
            == phased.final_states["vangogh"].emotions.fear
        )
        # tick 도달 동일
        assert (
            legacy.final_states["vangogh"].tick
            == phased.final_states["vangogh"].tick
        )


class TestVanGoghLegacyHazardUnaffected:
    """VG hazard events는 per_tick 기본값 — Iter 27 변경에 영향 없음."""

    def test_hazard_events_default_per_tick(self, _setup_domain):
        hazards = load_hazard_events(CONTENT / "vangogh" / "hazard_events.json")
        assert len(hazards) > 0
        for ev in hazards:
            # 명시 안 하면 per_tick
            assert ev.hazard.base_rate_unit == "per_tick"

    def test_phased_world_preserves_vg_hazard_behavior(self, _setup_domain):
        """PhasedSimulationWorld에서도 VG hazard가 per_tick으로 동작."""
        # phased single-phase 실행, seed 동일 → legacy와 동일 event 발동 패턴
        cfg_legacy = _build_vg_config(with_phase=False, max_tick=100)
        cfg_phased = _build_vg_config(with_phase=True, max_tick=100)

        legacy = SimulationWorld(
            cfg_legacy, _rules(), behavior_profiles=_profiles(),
        ).run(seed=0)
        phased = PhasedSimulationWorld(
            cfg_phased, _rules(), behavior_profiles=_profiles(),
        ).run(seed=0)

        legacy_events = [e["event_id"] for e in legacy.fired_events]
        phased_events = [e["event_id"] for e in phased.fired_events]
        assert legacy_events == phased_events


class TestVanGoghAbsoluteTrajectoryAPI:
    """time_axis 편의 method가 VG에서도 작동 — 인물 비종속."""

    def test_extract_absolute_trajectory_works(self, _setup_domain):
        config = _build_vg_config(with_phase=True, max_tick=30)
        result = PhasedSimulationWorld(
            config, _rules(), behavior_profiles=_profiles(),
        ).run(seed=0)
        traj = result.extract_absolute_trajectory("vangogh", "emotions.fear")
        # 30 tick × 2h/tick 범위
        assert len(traj) > 0
        for p in traj:
            assert 0.0 <= p.hours <= 60.0

    def test_multiple_agents_extractable(self, _setup_domain):
        config = _build_vg_config(with_phase=True, max_tick=30)
        result = PhasedSimulationWorld(
            config, _rules(), behavior_profiles=_profiles(),
        ).run(seed=0)
        vg_traj = result.extract_absolute_trajectory("vangogh", "emotions.fear")
        gauguin_traj = result.extract_absolute_trajectory("gauguin", "emotions.fear")
        theo_traj = result.extract_absolute_trajectory("theo", "emotions.fear")
        assert len(vg_traj) > 0
        assert len(gauguin_traj) > 0
        assert len(theo_traj) > 0


class TestVanGoghTwoPhases:
    """VG를 2 phase로 분할 실행 가능 — handoff 검증."""

    def test_two_phase_split(self, _setup_domain):
        from engine.core.phase import FieldMapping, PhaseHandoffSpec

        vg = load_agent_state(CONTENT / "vangogh" / "initial_state.json")
        gauguin = load_agent_state(CONTENT / "gauguin" / "initial_state.json")
        theo = load_agent_state(CONTENT / "theo" / "initial_state.json")
        handoff = PhaseHandoffSpec(
            mappings=[
                FieldMapping("vangogh", "emotions.fear", "vangogh", "emotions.fear"),
                FieldMapping("vangogh", "emotions.hope", "vangogh", "emotions.hope"),
                FieldMapping("vangogh", "emotions.grief", "vangogh", "emotions.grief"),
            ],
        )
        config = SimulationConfig(
            initial_state=vg,
            initial_states=[vg, gauguin, theo],
            max_tick=5000, state_noise_scale=0.0,
            phases=[
                Phase(
                    phase_id="arles_early",
                    agents_active=["vangogh", "gauguin", "theo"],
                    tick_scale_hours=2.0,
                    exit_condition=PhaseExitCondition(max_tick=20),
                    handoff_to_next=handoff,
                ),
                Phase(
                    phase_id="arles_late",
                    agents_active=["vangogh", "gauguin", "theo"],
                    tick_scale_hours=2.0,
                    exit_condition=PhaseExitCondition(max_tick=20),
                ),
            ],
        )
        result = PhasedSimulationWorld(
            config, _rules(), behavior_profiles=_profiles(),
        ).run(seed=0)

        assert len(result.per_phase_results) == 2
        # handoff로 fear 연속 — early 끝 값 = late 시작에 가까운 값
        early_end = result.per_phase_results["arles_early"].final_states["vangogh"].emotions.fear
        # late 시작 state를 직접 조회할 수는 없지만, per_phase snapshot이 있으면 간접 확인 가능
        late_snapshots = result.per_phase_results["arles_late"].state_snapshots.get("vangogh", {})
        if 0 in late_snapshots:
            late_start = late_snapshots[0].emotions.fear
            # state_noise=0이므로 동일값
            assert abs(early_end - late_start) < 1e-6
