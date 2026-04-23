"""JSON-only 데이터 주도 Peter arc 구성 (v1.2 Iter 45).

Iter 43 `load_handoff_spec` + Iter 44 `load_phase`가 조합되어 content/ 의
JSON 파일들만으로 Peter 5-phase 아크를 구성하고 `PhasedSimulationWorld`로
실행 가능함을 증명. 테스트 코드에 tick_scale / max_tick 같은 숫자 하드코딩
없이 전적으로 content-driven.

ABSOLUTE RULE #1 (engine 인물 비종속)과 호환되는 데이터 driven 경로 확립:
engine/ 은 Peter를 모르고, 이 테스트도 orchestration (agents_active + 로드
순서)만 담당하며 수치는 content 파일에서 가져옴.
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
    load_handoff_spec,
    load_phase,
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

PHASE_FILES = [
    ("01_calling", "handoff_to_02.json", ["peter"]),
    ("02_galilean", "handoff_to_03.json", ["peter", "judas"]),
    ("03_confession", "handoff_to_04.json", ["peter", "judas"]),
    ("04_journey_to_jerusalem", "handoff_to_05.json", ["peter", "judas"]),
    ("05_passion", None, ["peter", "judas", "caiaphas", "crowd"]),
]


@pytest.fixture(scope="module")
def _setup_domain():
    for t, c in [
        ("faith_journey", FaithJourneyState),
        ("betrayal_psychology", BetrayalPsychologyState),
        ("political_calculation", PoliticalCalculationState),
        ("crowd_dynamics", CrowdDynamicsState),
    ]:
        register_domain_type(t, c)
    return None


def _rules() -> RuleEngine:
    return RuleEngine([
        FearResponseRule(), HopeRule(), GriefRule(),
        ConfusionRule(), LoveRule(),
        HomeostasisRule(),
    ])


def _load_arc_from_json() -> list:
    """PHASE_FILES를 기반으로 phases list를 load_phase + load_handoff_spec만 사용."""
    phases = []
    for phase_dir, handoff_name, agents in PHASE_FILES:
        phase_dir_path = CONTENT / "peter" / "phases" / phase_dir
        cfg_path = phase_dir_path / "phase_config.json"
        handoff = None
        if handoff_name:
            handoff_path = phase_dir_path / handoff_name
            if handoff_path.exists():
                handoff = load_handoff_spec(handoff_path)
        phase = load_phase(
            cfg_path,
            agents_active=agents,
            handoff_to_next=handoff,
        )
        phases.append(phase)
    return phases


class TestJsonDrivenArcLoad:
    def test_all_phases_load(self, _setup_domain):
        phases = _load_arc_from_json()
        assert len(phases) == 5
        assert [p.phase_id for p in phases] == [
            "01_calling", "02_galilean", "03_confession",
            "04_journey_to_jerusalem", "05_passion",
        ]

    def test_tick_scales_from_json(self, _setup_domain):
        """phase_config.json의 tick_scale_hours가 올바르게 로드됨."""
        phases = _load_arc_from_json()
        scales = [p.tick_scale_hours for p in phases]
        # Phase 1/3/5 dense (2h), Phase 2/4 sparse (24h)
        assert scales == [2.0, 24.0, 2.0, 24.0, 2.0]

    def test_handoffs_loaded(self, _setup_domain):
        """Phase 1-4는 handoff_to_next가 있고, Phase 5는 없음."""
        phases = _load_arc_from_json()
        for i, p in enumerate(phases[:-1]):
            assert p.handoff_to_next is not None, f"Phase {i} missing handoff"
        assert phases[-1].handoff_to_next is None


class TestJsonDrivenArcExecution:
    def test_runs_through_phased_world(self, _setup_domain):
        """JSON만으로 구성된 arc가 실행 가능."""
        phases = _load_arc_from_json()
        peter = load_agent_state(CONTENT / "peter" / "initial_state_calling.json")
        judas = load_agent_state(CONTENT / "judas" / "initial_state.json")
        cai = load_agent_state(CONTENT / "caiaphas" / "initial_state.json")
        crowd = load_agent_state(CONTENT / "crowd" / "initial_state.json")
        config = SimulationConfig(
            initial_state=peter,
            initial_states=[peter, judas, cai, crowd],
            max_tick=5000, state_noise_scale=0.0,
            phases=phases,
        )
        result = PhasedSimulationWorld(config, _rules()).run(seed=0)
        assert isinstance(result, PhasedMultiAgentResult)
        assert len(result.per_phase_results) == 5


class TestContentAuthorWorkflow:
    """Content 저자 관점: JSON 파일만 수정하면 scenario 재구성 가능."""

    def test_adding_new_phase_by_json_only(self, _setup_domain, tmp_path):
        """임시 phase_config.json을 작성해서 arc에 끼워넣어도 동작."""
        # 임시 phase
        (tmp_path / "extra_phase.json").write_text(
            '{"phase_id":"extra","tick_scale_hours":2.0,"max_tick":5}',
            encoding="utf-8",
        )
        extra_phase = load_phase(
            tmp_path / "extra_phase.json",
            agents_active=["peter"],
        )
        peter = load_agent_state(CONTENT / "peter" / "initial_state_calling.json")
        config = SimulationConfig(
            initial_state=peter,
            initial_states=[peter],
            max_tick=1000, state_noise_scale=0.0,
            phases=[extra_phase],
        )
        result = PhasedSimulationWorld(config, _rules()).run(seed=0)
        assert isinstance(result, PhasedMultiAgentResult)
        assert "extra" in result.per_phase_results
