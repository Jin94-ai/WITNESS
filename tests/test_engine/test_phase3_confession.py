"""Phase 3 가이사랴 빌립보 고백 + 변화산 content 검증 (v1.2 Iter 13)."""

import json
from pathlib import Path

PHASE3_DIR = Path(__file__).resolve().parent.parent.parent / "content" / "peter" / "phases" / "03_confession"


class TestPhase3Files:
    def test_config_exists(self):
        assert (PHASE3_DIR / "phase_config.json").exists()

    def test_events_exists(self):
        assert (PHASE3_DIR / "canonical_events.json").exists()

    def test_handoff_exists(self):
        assert (PHASE3_DIR / "handoff_to_04.json").exists()


class TestPhase3Config:
    def test_structure(self):
        data = json.loads(
            (PHASE3_DIR / "phase_config.json").read_text(encoding="utf-8"),
        )
        assert data["phase_id"] == "03_confession"
        # 전환점 phase는 dense 2h/tick
        assert data["tick_scale_hours"] == 2.0
        # Phase 1 (84) + Phase 2 (540) = 624
        assert data["tick_offset_from_life_start"] == 624
        assert data["max_tick"] == 150


class TestPhase3CanonicalEvents:
    def test_event_count(self):
        data = json.loads(
            (PHASE3_DIR / "canonical_events.json").read_text(encoding="utf-8"),
        )
        # 고백/변화산 핵심 사건 + 수난 예고 = 최소 10개
        assert len(data["events"]) >= 10

    def test_confession_event_present(self):
        """핵심: Peter의 고백."""
        data = json.loads(
            (PHASE3_DIR / "canonical_events.json").read_text(encoding="utf-8"),
        )
        event_ids = [ev["event_id"] for ev in data["events"]]
        assert any("confession" in eid.lower() or "peters_confession" in eid for eid in event_ids)

    def test_satan_rebuke_present(self):
        """반석 선언 직후 사탄 책망 (동일 tick 근처)."""
        data = json.loads(
            (PHASE3_DIR / "canonical_events.json").read_text(encoding="utf-8"),
        )
        event_ids = [ev["event_id"] for ev in data["events"]]
        assert any("satan" in eid or "rebuke" in eid for eid in event_ids)

    def test_transfiguration_present(self):
        data = json.loads(
            (PHASE3_DIR / "canonical_events.json").read_text(encoding="utf-8"),
        )
        event_ids = [ev["event_id"] for ev in data["events"]]
        assert any("transfiguration" in eid or "three_tents" in eid for eid in event_ids)

    def test_two_passion_predictions(self):
        """1, 2차 수난 예고 모두 포함 → 베드로가 받아들이지 못하는 충격."""
        data = json.loads(
            (PHASE3_DIR / "canonical_events.json").read_text(encoding="utf-8"),
        )
        event_ids = [ev["event_id"] for ev in data["events"]]
        passion_events = [eid for eid in event_ids if "passion" in eid]
        assert len(passion_events) >= 2

    def test_identity_shift_from_rebuke(self):
        """사탄 책망 이벤트에 slow_state.identity_shift 영향이 있어야 함."""
        data = json.loads(
            (PHASE3_DIR / "canonical_events.json").read_text(encoding="utf-8"),
        )
        rebuke_event = next(
            (ev for ev in data["events"] if "satan" in ev["event_id"] or "rebuke" in ev["event_id"]),
            None,
        )
        assert rebuke_event is not None
        field_paths = [e["field_path"] for e in rebuke_event["effects"]]
        assert any("identity_shift" in fp or "moral_injury" in fp for fp in field_paths)


class TestPhase3HandoffSpec:
    def test_structure(self):
        data = json.loads(
            (PHASE3_DIR / "handoff_to_04.json").read_text(encoding="utf-8"),
        )
        assert data["phase_from"] == "03_confession"
        assert data["phase_to"] == "04_journey_to_jerusalem"

    def test_theological_carry(self):
        """고백 phase 종료 시 confusion 높음 → Phase 4로 carry (신학적 긴장 유지)."""
        data = json.loads(
            (PHASE3_DIR / "handoff_to_04.json").read_text(encoding="utf-8"),
        )
        mapped = {m["source_field_path"] for m in data["mappings"]}
        assert "emotions.confusion" in mapped
        assert "emotions.awe" in mapped


class TestScriptureCoverage:
    def test_confession_source_refs_multiple(self):
        """공관복음 3 저자 모두 고백 기록 — 교차 참조."""
        data = json.loads(
            (PHASE3_DIR / "phase_config.json").read_text(encoding="utf-8"),
        )
        refs = data["scripture_refs"]
        # 마 / 막 / 눅 중 최소 2개
        gospels = sum(1 for r in refs if any(g in r for g in ["마 16", "막 8", "눅 9"]))
        assert gospels >= 2
