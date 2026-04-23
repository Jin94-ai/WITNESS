"""Phase 2 갈릴리 사역 content + Phase 1→2 real handoff E2E (v1.2 Iter 9-10)."""

import json
from pathlib import Path

from content.peter.domain_faith import FaithJourneyState
from engine.core.phase import (
    FieldMapping,
    Phase,
    PhaseExitCondition,
    PhaseHandoffSpec,
)
from engine.core.world import SimulationConfig
from engine.io.loader import (
    load_agent_state,
    load_events,
    register_domain_type,
)
from engine.rules.base import RuleEngine
from engine.rules.emotional import (
    ConfusionRule,
    FearResponseRule,
    GriefRule,
    HopeRule,
    LoveRule,
)
from engine.rules.temporal import HomeostasisRule
from engine.simulation.phased_world import (
    PhasedMultiAgentResult,
    PhasedSimulationWorld,
)

CONTENT = Path(__file__).resolve().parent.parent.parent / "content"
PHASE2_DIR = CONTENT / "peter" / "phases" / "02_galilean"


def _rules() -> RuleEngine:
    return RuleEngine([
        FearResponseRule(), HopeRule(), GriefRule(),
        ConfusionRule(), LoveRule(),
        HomeostasisRule(),
    ])


class TestPhase2Files:
    def test_config_exists(self):
        assert (PHASE2_DIR / "phase_config.json").exists()

    def test_canonical_events_exists(self):
        assert (PHASE2_DIR / "canonical_events.json").exists()

    def test_handoff_to_03_exists(self):
        assert (PHASE2_DIR / "handoff_to_03.json").exists()


class TestPhase2Config:
    def test_structure(self):
        data = json.loads(
            (PHASE2_DIR / "phase_config.json").read_text(encoding="utf-8"),
        )
        assert data["phase_id"] == "02_galilean"
        assert data["tick_scale_hours"] == 24.0  # sparse 1일/tick
        assert data["max_tick"] == 540  # ~18개월
        assert data["tick_offset_from_life_start"] == 84  # Phase 1 이후

    def test_scripture_refs_multiple_gospels(self):
        """공관복음 병행 기록을 source로."""
        data = json.loads(
            (PHASE2_DIR / "phase_config.json").read_text(encoding="utf-8"),
        )
        refs = data["scripture_refs"]
        # 최소 3개 이상 복음서 참조
        assert len(refs) >= 3


class TestPhase2CanonicalEvents:
    def test_event_count(self):
        data = json.loads(
            (PHASE2_DIR / "canonical_events.json").read_text(encoding="utf-8"),
        )
        # 최소 7개 주요 사건
        assert len(data["events"]) >= 7

    def test_events_tick_ordered_and_in_range(self):
        data = json.loads(
            (PHASE2_DIR / "canonical_events.json").read_text(encoding="utf-8"),
        )
        ticks = [ev["tick"] for ev in data["events"]]
        assert ticks == sorted(ticks)
        assert all(0 <= t <= 540 for t in ticks)

    def test_walking_on_water_present(self):
        """핵심 사건: 물 위 걸음 포함."""
        data = json.loads(
            (PHASE2_DIR / "canonical_events.json").read_text(encoding="utf-8"),
        )
        event_ids = [ev["event_id"] for ev in data["events"]]
        assert any("walking_on_water" in eid or "walk" in eid for eid in event_ids)

    def test_feeding_5000_present(self):
        data = json.loads(
            (PHASE2_DIR / "canonical_events.json").read_text(encoding="utf-8"),
        )
        event_ids = [ev["event_id"] for ev in data["events"]]
        assert any("feeding_5000" in eid or "5000" in eid for eid in event_ids)

    def test_dense_window_via_adjacent_ticks(self):
        """reviewer 지적 반영: 주요 사건은 연속 tick으로 dense 표현.
        오병이어(230) → 물 위 걸음 storm(232) → 베드로 시도(233) → 구출(234) 등.
        """
        data = json.loads(
            (PHASE2_DIR / "canonical_events.json").read_text(encoding="utf-8"),
        )
        ticks = [ev["tick"] for ev in data["events"]]
        # 인접한 tick 쌍이 최소 1개 (연속 tick dense 표현)
        has_adjacent = any(
            abs(ticks[i + 1] - ticks[i]) <= 2 for i in range(len(ticks) - 1)
        )
        assert has_adjacent


class TestPhase2HandoffSpec:
    def test_structure(self):
        data = json.loads(
            (PHASE2_DIR / "handoff_to_03.json").read_text(encoding="utf-8"),
        )
        assert data["phase_from"] == "02_galilean"
        assert data["phase_to"] == "03_confession"
        assert data["carry_all_slow_state"] is True

    def test_obedience_and_awe_carried(self):
        data = json.loads(
            (PHASE2_DIR / "handoff_to_03.json").read_text(encoding="utf-8"),
        )
        mapped_paths = {m["source_field_path"] for m in data["mappings"]}
        assert "domain_state.obedience_maturity" in mapped_paths
        assert "emotions.awe" in mapped_paths


class TestPhase2SingleRun:
    """Phase 2만 단독 실행 (Phase 1 없이, 기본 소명 이후 상태로)."""

    def setup_method(self):
        register_domain_type("faith_journey", FaithJourneyState)

    def test_phase2_runs_with_events(self):
        """Phase 2 events가 실제로 fire되는지."""
        # 소명 phase 이후 상태를 가정한 초기값 (obedience≈2, awe≈3 등)
        peter = load_agent_state(CONTENT / "peter" / "initial_state_calling.json")
        # 소명 이후 상태 시뮬레이션 (수동 override)
        peter = peter.model_copy(update={
            "domain_state": peter.domain_state.model_copy(update={
                "jesus_understanding": "teacher",
                "obedience_maturity": 2.0,
                "communal_role": "disciple",
            }),
        })

        events = load_events(PHASE2_DIR / "canonical_events.json")
        config = SimulationConfig(
            initial_state=peter, initial_states=[peter],
            max_tick=540,
            events=events,
            state_noise_scale=0.01,
            tick_scale_hours=24.0,
        )
        from engine.simulation.world import SimulationWorld
        world = SimulationWorld(config, _rules())
        result = world.run(seed=0)
        assert result.final_states["peter"].tick == 540
        # 최소 몇 개 이벤트 fire
        assert len(result.fired_events) >= 5


class TestPhase1ToPhase2RealHandoff:
    """PhasedSimulationWorld로 Phase 1 → Phase 2 전체 실행 (mock 아님)."""

    def setup_method(self):
        register_domain_type("faith_journey", FaithJourneyState)

    def test_real_handoff_preserves_obedience(self):
        """Phase 1에서 누적된 obedience가 Phase 2 시작 시점에 carry-forward."""
        peter = load_agent_state(CONTENT / "peter" / "initial_state_calling.json")

        phase1_events = load_events(
            CONTENT / "peter" / "phases" / "01_calling" / "canonical_events.json",
        )
        _ = phase1_events  # (events는 SimulationConfig.events로 전달)

        # Phase 1 config — 소명 events 포함
        # Phase 2 config — 갈릴리 events 포함
        # 단일 SimulationConfig.events에 둘 다 넣기는 어색하므로
        # 각 phase마다 독립 config 준비 필요. MVP는 phase.canonical_events_path
        # 를 engine에서 로드하는 로직이 없음 → 여기서는 global events 사용.

        # 현실적 MVP 테스트: 단일 config.events로 합치고 phases만 분리
        from engine.io.loader import load_events as _le
        p1_events = _le(
            CONTENT / "peter" / "phases" / "01_calling" / "canonical_events.json",
        )
        # (p2_events는 현 MVP에서 미사용 — Phase 2는 handoff carry 검증에 집중)

        # 두 phase를 PhasedSimulationWorld로 실행 — 각 phase 내부는 단일 SimulationWorld
        # phase-local events는 각 phase config에 넣어야 하는데, 현 구조는
        # 상위 config.events를 모든 phase가 공유. MVP 단순화:
        # Phase 1만 events 사용, Phase 2는 events 없이 handoff 검증에 집중

        handoff_spec = PhaseHandoffSpec(
            mappings=[
                FieldMapping(
                    "peter", "domain_state.obedience_maturity",
                    "peter", "domain_state.obedience_maturity",
                ),
                FieldMapping(
                    "peter", "emotions.awe",
                    "peter", "emotions.awe",
                ),
            ],
        )

        config = SimulationConfig(
            initial_state=peter, initial_states=[peter],
            max_tick=700,  # upper bound
            events=p1_events,  # Phase 1 events (Phase 2는 events 없이 state evolve)
            state_noise_scale=0.01,
            phases=[
                Phase(
                    phase_id="01_calling",
                    tick_scale_hours=2.0,
                    exit_condition=PhaseExitCondition(max_tick=84),
                    handoff_to_next=handoff_spec,
                ),
                Phase(
                    phase_id="02_galilean",
                    tick_scale_hours=24.0,
                    exit_condition=PhaseExitCondition(max_tick=30),  # MVP 단축
                ),
            ],
        )
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)
        assert isinstance(result, PhasedMultiAgentResult)
        assert "01_calling" in result.per_phase_results
        assert "02_galilean" in result.per_phase_results

        # Phase 1에서 축적된 obedience가 0보다 큼
        p1_final = result.per_phase_results["01_calling"].final_states["peter"]
        assert p1_final.domain_state.obedience_maturity > 0.0

        # Phase 2 시작 시점(handoff 직후)은 직접 관측 어려움 — 대신
        # Phase 2 final state에서 Phase 1 obedience가 carry되어 있는지 확인
        # (Phase 2 events 없고 homeostasis만 작동하므로 obedience는 rule로 변하지 않음)
        p2_final = result.per_phase_results["02_galilean"].final_states["peter"]
        # Phase 1 종료시 obedience가 Phase 2로 전달되어야
        assert p2_final.domain_state.obedience_maturity >= p1_final.domain_state.obedience_maturity - 0.5

    def test_phase_boundaries_tick_offsets(self):
        peter = load_agent_state(CONTENT / "peter" / "initial_state_calling.json")
        config = SimulationConfig(
            initial_state=peter, initial_states=[peter],
            max_tick=700, state_noise_scale=0.01,
            phases=[
                Phase(
                    phase_id="01_calling",
                    tick_scale_hours=2.0,
                    exit_condition=PhaseExitCondition(max_tick=84),
                    handoff_to_next=PhaseHandoffSpec(),
                ),
                Phase(
                    phase_id="02_galilean",
                    tick_scale_hours=24.0,
                    exit_condition=PhaseExitCondition(max_tick=30),
                ),
            ],
        )
        world = PhasedSimulationWorld(config, _rules())
        result = world.run(seed=0)
        assert len(result.phase_boundaries) == 2
        b0 = result.phase_boundaries[0]
        b1 = result.phase_boundaries[1]
        assert b0["start_tick"] == 0
        assert b0["end_tick"] == 84
        assert b1["start_tick"] == 84
        assert b1["end_tick"] == 84 + 30
        assert b0["tick_scale_hours"] == 2.0
        assert b1["tick_scale_hours"] == 24.0
