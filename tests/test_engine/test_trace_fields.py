"""Trace Schema 필드 backward compat + 기본 사용 테스트.

TRACE_SCHEMA.md 에 정의된 observable_from / visible_signal 필드 검증.
v1.0 render-ready trace의 첫 단계.
"""

from engine.simulation.checkpoint import ActionRecord


class TestActionRecordTraceFields:
    def test_default_observable_from_empty(self):
        """observable_from 기본값은 empty list."""
        rec = ActionRecord(tick=0, event_id="x", chosen_action="follow")
        assert rec.observable_from == []

    def test_default_visible_signal_none(self):
        """visible_signal 기본값 None."""
        rec = ActionRecord(tick=0, event_id="x", chosen_action="follow")
        assert rec.visible_signal is None

    def test_can_set_observable_from(self):
        """특정 agent들만 관찰 가능하게 지정."""
        rec = ActionRecord(
            tick=100,
            event_id="voluntary",
            chosen_action="withdraw",
            observable_from=["peter", "caiaphas"],
        )
        assert "peter" in rec.observable_from
        assert "caiaphas" in rec.observable_from
        assert len(rec.observable_from) == 2

    def test_can_set_visible_signal(self):
        """렌더러용 서술 설정."""
        rec = ActionRecord(
            tick=150,
            event_id="voluntary",
            chosen_action="withdraw",
            visible_signal="유다가 말없이 자리를 뜬다",
        )
        assert rec.visible_signal == "유다가 말없이 자리를 뜬다"

    def test_weights_field_still_works(self):
        """기존 weights 필드 유지 (backward compat)."""
        rec = ActionRecord(
            tick=0,
            event_id="x",
            chosen_action="follow",
            weights={"follow": 1.2, "flee": 0.3},
        )
        assert rec.weights["follow"] == 1.2


class TestRenderReadyFiltering:
    """TRACE_SCHEMA.md §3.1 플레이어 시점 필터 시뮬레이션.

    렌더러가 trace 읽을 때 player_id가 observable_from에 있는
    action만 렌더.
    """

    def test_empty_observable_means_visible_to_all(self):
        """observable_from이 empty면 모든 시점에 보임 (default)."""
        rec = ActionRecord(tick=0, event_id="x", chosen_action="public_act")

        def is_visible(record: ActionRecord, player_id: str) -> bool:
            if not record.observable_from:
                return True  # empty = 모두에게 보임
            return player_id in record.observable_from

        assert is_visible(rec, "peter") is True
        assert is_visible(rec, "judas") is True

    def test_restricted_observable(self):
        """observable_from에 명시된 agent만 렌더 대상."""
        rec = ActionRecord(
            tick=0,
            event_id="x",
            chosen_action="secret",
            observable_from=["peter"],
        )

        def is_visible(record: ActionRecord, player_id: str) -> bool:
            if not record.observable_from:
                return True
            return player_id in record.observable_from

        assert is_visible(rec, "peter") is True
        assert is_visible(rec, "judas") is False
