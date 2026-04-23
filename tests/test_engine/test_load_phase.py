"""load_phase JSON loader 검증 (v1.2 Iter 44).

content/peter/phases/*/phase_config.json → `Phase` dataclass 변환.
agents_active / handoff_to_next는 caller가 주입.
"""

from pathlib import Path

from engine.core.phase import (
    FieldMapping,
    Phase,
    PhaseHandoffSpec,
)
from engine.io.loader import load_phase

CONTENT = Path(__file__).resolve().parent.parent.parent / "content"


class TestLoadPhase:
    def test_loads_peter_01_calling(self):
        phase = load_phase(
            CONTENT / "peter" / "phases" / "01_calling" / "phase_config.json",
        )
        assert isinstance(phase, Phase)
        assert phase.phase_id == "01_calling"
        assert phase.tick_scale_hours == 2.0
        assert phase.exit_condition.max_tick == 84
        assert phase.canonical_events_path is not None

    def test_loads_peter_02_galilean_tick_scale(self):
        phase = load_phase(
            CONTENT / "peter" / "phases" / "02_galilean" / "phase_config.json",
        )
        # Galilean은 sparse 1일/tick
        assert phase.tick_scale_hours == 24.0

    def test_exit_condition_triggered_by(self):
        phase = load_phase(
            CONTENT / "peter" / "phases" / "01_calling" / "phase_config.json",
        )
        assert phase.exit_condition.triggered_by == "calling_accepted"

    def test_agents_active_defaults_none(self):
        phase = load_phase(
            CONTENT / "peter" / "phases" / "01_calling" / "phase_config.json",
        )
        assert phase.agents_active is None

    def test_agents_active_injected(self):
        phase = load_phase(
            CONTENT / "peter" / "phases" / "01_calling" / "phase_config.json",
            agents_active=["peter"],
        )
        assert phase.agents_active == ["peter"]

    def test_handoff_injected(self):
        handoff = PhaseHandoffSpec(
            mappings=[FieldMapping("a", "b", "a", "b")],
        )
        phase = load_phase(
            CONTENT / "peter" / "phases" / "01_calling" / "phase_config.json",
            handoff_to_next=handoff,
        )
        assert phase.handoff_to_next is handoff

    def test_tick_offset_from_life_start(self):
        phase = load_phase(
            CONTENT / "peter" / "phases" / "02_galilean" / "phase_config.json",
        )
        # Phase 2는 Phase 1 이후: offset > 0
        assert phase.tick_offset > 0

    def test_loads_all_peter_phases(self):
        """모든 Peter phase JSON이 Phase 객체로 로드 가능."""
        phase_dirs = [
            "01_calling",
            "02_galilean",
            "03_confession",
            "04_journey_to_jerusalem",
            "05_passion",
        ]
        for pd in phase_dirs:
            cfg = CONTENT / "peter" / "phases" / pd / "phase_config.json"
            if not cfg.exists():
                continue
            phase = load_phase(cfg)
            assert isinstance(phase, Phase)
            assert phase.phase_id.startswith(pd[:2])  # 01 / 02 etc.


class TestMinimalPhaseJson:
    def test_minimal_phase_json(self, tmp_path):
        p = tmp_path / "minimal.json"
        p.write_text(
            '{"phase_id":"test","tick_scale_hours":2.0,"max_tick":10}',
            encoding="utf-8",
        )
        phase = load_phase(p)
        assert phase.phase_id == "test"
        assert phase.exit_condition.max_tick == 10
        assert phase.exit_condition.triggered_by is None

    def test_max_tick_fallback_wins_over_max_tick(self, tmp_path):
        """exit_condition.max_tick_fallback이 있으면 max_tick보다 우선."""
        p = tmp_path / "override.json"
        p.write_text(
            '{"phase_id":"t","tick_scale_hours":2.0,"max_tick":999,'
            '"exit_condition":{"max_tick_fallback":20}}',
            encoding="utf-8",
        )
        phase = load_phase(p)
        assert phase.exit_condition.max_tick == 20

    def test_invalid_tick_scale_raises(self, tmp_path):
        import pytest
        p = tmp_path / "invalid.json"
        p.write_text(
            '{"phase_id":"t","tick_scale_hours":0,"max_tick":10}',
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="tick_scale_hours"):
            load_phase(p)
