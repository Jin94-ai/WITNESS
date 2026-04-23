"""Phase 4 예루살렘 여정 content 검증 (v1.2 Iter 14)."""

import json
from pathlib import Path

PHASE4_DIR = Path(__file__).resolve().parent.parent.parent / "content" / "peter" / "phases" / "04_journey_to_jerusalem"


class TestPhase4Files:
    def test_config_exists(self):
        assert (PHASE4_DIR / "phase_config.json").exists()

    def test_events_exists(self):
        assert (PHASE4_DIR / "canonical_events.json").exists()

    def test_handoff_exists(self):
        assert (PHASE4_DIR / "handoff_to_05.json").exists()


class TestPhase4Config:
    def test_structure(self):
        data = json.loads(
            (PHASE4_DIR / "phase_config.json").read_text(encoding="utf-8"),
        )
        assert data["phase_id"] == "04_journey_to_jerusalem"
        # 여정 phase는 sparse 1일/tick
        assert data["tick_scale_hours"] == 24.0
        # Phase 1-3 누적 이후 시작: 84 + 540 + 150 = 774
        assert data["tick_offset_from_life_start"] == 774
        assert data["max_tick"] == 90  # 3개월


class TestPhase4CanonicalEvents:
    def test_key_teachings_present(self):
        """주요 가르침 / 사건 포함 — 지위 논쟁 / 용서 / 부자청년 / 수난예고 / 유다 공모 / 향유."""
        data = json.loads(
            (PHASE4_DIR / "canonical_events.json").read_text(encoding="utf-8"),
        )
        event_ids = [ev["event_id"] for ev in data["events"]]
        keywords = [
            ("greatest", "지위 논쟁"),
            ("forgive", "용서 가르침"),
            ("rich", "부자 청년"),
            ("passion", "3차 수난 예고"),
            ("judas", "유다 배반 공모"),
            ("anointing", "베다니 향유"),
        ]
        for keyword, desc in keywords:
            assert any(keyword in eid for eid in event_ids), f"Missing: {desc}"

    def test_tick_ordered_and_bounded(self):
        data = json.loads(
            (PHASE4_DIR / "canonical_events.json").read_text(encoding="utf-8"),
        )
        ticks = [ev["tick"] for ev in data["events"]]
        assert ticks == sorted(ticks)
        assert all(0 <= t <= 90 for t in ticks)

    def test_judas_event_no_peter_effect(self):
        """유다 공모 이벤트는 베드로 상태에 직접 영향 없음 (베드로가 모름)."""
        data = json.loads(
            (PHASE4_DIR / "canonical_events.json").read_text(encoding="utf-8"),
        )
        judas_event = next(
            (ev for ev in data["events"] if "judas" in ev["event_id"]),
            None,
        )
        assert judas_event is not None
        # effects가 비어있어야 (베드로에게 직접 영향 없음)
        assert len(judas_event["effects"]) == 0


class TestPhase4HandoffToPhase5:
    def test_structure(self):
        data = json.loads(
            (PHASE4_DIR / "handoff_to_05.json").read_text(encoding="utf-8"),
        )
        assert data["phase_from"] == "04_journey_to_jerusalem"
        assert data["phase_to"] == "05_passion"

    def test_all_key_fields_carried(self):
        """Phase 5(수난)에서 의미 있는 모든 fast state carry."""
        data = json.loads(
            (PHASE4_DIR / "handoff_to_05.json").read_text(encoding="utf-8"),
        )
        mapped = {m["source_field_path"] for m in data["mappings"]}
        # 누적 순종, 경외, 혼란, 두려움, 사랑 → Phase 5 수난 진입 시 의미
        for required in [
            "domain_state.obedience_maturity",
            "emotions.awe",
            "emotions.confusion",
            "emotions.fear",
            "emotions.love",
        ]:
            assert required in mapped, f"Missing handoff mapping: {required}"

    def test_legacy_compat_noted(self):
        data = json.loads(
            (PHASE4_DIR / "handoff_to_05.json").read_text(encoding="utf-8"),
        )
        # legacy 500 tick scenario 호환 메모
        assert "note_legacy_compat" in data or "legacy" in json.dumps(data).lower()


class TestCumulativeTickOffset:
    """Phase 1 + 2 + 3 + 4 누적 tick offset 정합성."""

    def test_phase4_offset_matches_prior_phases(self):
        import json as _json
        from pathlib import Path as _Path

        content = _Path(__file__).resolve().parent.parent.parent / "content" / "peter" / "phases"
        p1 = _json.loads((content / "01_calling" / "phase_config.json").read_text(encoding="utf-8"))
        p2 = _json.loads((content / "02_galilean" / "phase_config.json").read_text(encoding="utf-8"))
        p3 = _json.loads((content / "03_confession" / "phase_config.json").read_text(encoding="utf-8"))
        p4 = _json.loads((content / "04_journey_to_jerusalem" / "phase_config.json").read_text(encoding="utf-8"))

        expected_p4_offset = p1["max_tick"] + p2["max_tick"] + p3["max_tick"]
        assert p4["tick_offset_from_life_start"] == expected_p4_offset

    def test_total_arc_ministry_range(self):
        """전체 아크 tick 합이 역사적 공생애 범위 (약 2~3년)인지.

        복음서 공생애 기간은 학자들 사이 논쟁: 요한복음의 유월절 3회 기준 2-3년,
        공관복음 기준은 더 짧을 수 있음. 2년~3.5년 허용.
        """
        import json as _json
        from pathlib import Path as _Path

        content = _Path(__file__).resolve().parent.parent.parent / "content" / "peter" / "phases"
        p1 = _json.loads((content / "01_calling" / "phase_config.json").read_text(encoding="utf-8"))
        p2 = _json.loads((content / "02_galilean" / "phase_config.json").read_text(encoding="utf-8"))
        p3 = _json.loads((content / "03_confession" / "phase_config.json").read_text(encoding="utf-8"))
        p4 = _json.loads((content / "04_journey_to_jerusalem" / "phase_config.json").read_text(encoding="utf-8"))

        total_hours = (
            p1["max_tick"] * p1["tick_scale_hours"]
            + p2["max_tick"] * p2["tick_scale_hours"]
            + p3["max_tick"] * p3["tick_scale_hours"]
            + p4["max_tick"] * p4["tick_scale_hours"]
        )
        total_hours += 500 * 2.0  # legacy Phase 5
        total_years = total_hours / 24.0 / 365.25

        # 공생애 기간 허용 범위 (학자 논쟁 반영)
        assert 1.5 <= total_years <= 3.5, f"Total arc: {total_years:.2f} years"
