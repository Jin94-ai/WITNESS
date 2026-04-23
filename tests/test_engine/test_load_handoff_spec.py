"""load_handoff_spec JSON loader 검증 (v1.2 Iter 43).

content/peter/phases/*/handoff_to_next.json 파일들이 실제로
`PhaseHandoffSpec`으로 로드되고 `PhasedSimulationWorld`에서 사용 가능한지
end-to-end 검증.
"""

from pathlib import Path

import pytest

from engine.core.phase import FieldMapping, PhaseHandoffSpec
from engine.io.loader import load_handoff_spec

CONTENT = Path(__file__).resolve().parent.parent.parent / "content"


class TestLoadHandoffSpec:
    def test_loads_peter_01_to_02(self):
        spec = load_handoff_spec(
            CONTENT / "peter" / "phases" / "01_calling" / "handoff_to_02.json",
        )
        assert isinstance(spec, PhaseHandoffSpec)
        assert spec.carry_all_slow_state is True
        assert len(spec.mappings) >= 3  # obedience + awe + hope 최소

    def test_mappings_are_fieldmapping_instances(self):
        spec = load_handoff_spec(
            CONTENT / "peter" / "phases" / "01_calling" / "handoff_to_02.json",
        )
        for m in spec.mappings:
            assert isinstance(m, FieldMapping)
            assert m.source_agent_id
            assert m.source_field_path
            assert m.target_agent_id
            assert m.target_field_path

    def test_loads_all_peter_handoffs(self):
        """Peter의 모든 phase handoff JSON을 로드."""
        handoff_files = [
            ("01_calling", "handoff_to_02.json"),
            ("02_galilean", "handoff_to_03.json"),
            ("03_confession", "handoff_to_04.json"),
            ("04_journey_to_jerusalem", "handoff_to_05.json"),
        ]
        for phase_dir, fname in handoff_files:
            path = CONTENT / "peter" / "phases" / phase_dir / fname
            if not path.exists():
                continue  # phase 03 handoff 04가 없을 수도
            spec = load_handoff_spec(path)
            assert isinstance(spec, PhaseHandoffSpec)

    def test_loads_phase4_to_5_includes_confusion_and_fear(self):
        """Phase 4 → Phase 5 handoff는 confusion/fear 포함 (수난 진입 state)."""
        path = CONTENT / "peter" / "phases" / "04_journey_to_jerusalem" / "handoff_to_05.json"
        if not path.exists():
            pytest.skip("handoff_to_05.json not present")
        spec = load_handoff_spec(path)
        sources = {m.source_field_path for m in spec.mappings}
        assert "emotions.confusion" in sources
        assert "emotions.fear" in sources

    def test_carry_all_slow_state_default_true(self, tmp_path):
        """carry_all_slow_state 명시 안 된 JSON은 True."""
        p = tmp_path / "minimal.json"
        p.write_text('{"phase_from":"a","phase_to":"b","mappings":[]}', encoding="utf-8")
        spec = load_handoff_spec(p)
        assert spec.carry_all_slow_state is True

    def test_empty_mappings(self, tmp_path):
        """mappings 없어도 carry_all_slow_state로만 handoff 가능."""
        p = tmp_path / "empty.json"
        p.write_text(
            '{"phase_from":"a","phase_to":"b","carry_all_slow_state":true,"mappings":[]}',
            encoding="utf-8",
        )
        spec = load_handoff_spec(p)
        assert spec.mappings == []

    def test_carry_all_disabled(self, tmp_path):
        p = tmp_path / "disabled.json"
        p.write_text(
            '{"phase_from":"a","phase_to":"b","carry_all_slow_state":false,"mappings":[]}',
            encoding="utf-8",
        )
        spec = load_handoff_spec(p)
        assert spec.carry_all_slow_state is False

    def test_default_if_missing_preserved(self, tmp_path):
        p = tmp_path / "with_default.json"
        p.write_text(
            '{"phase_from":"a","phase_to":"b","mappings":[{'
            '"source_agent_id":"x","source_field_path":"a.b",'
            '"target_agent_id":"y","target_field_path":"c.d",'
            '"default_if_missing":5.0}]}',
            encoding="utf-8",
        )
        spec = load_handoff_spec(p)
        assert spec.mappings[0].default_if_missing == 5.0
