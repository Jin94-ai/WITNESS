"""Phase 1 소명 content 파일 구조 검증 (v1.2 Iteration 5).

content/peter/phases/01_calling/ 및 content/shared/scripture/luke_5.json 의
구조가 엔진 로더와 호환되는지 검증.
"""

import json
from pathlib import Path

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"
PHASE1_DIR = CONTENT_DIR / "peter" / "phases" / "01_calling"


class TestPhase1FilesExist:
    def test_phase_config_exists(self):
        assert (PHASE1_DIR / "phase_config.json").exists()

    def test_canonical_events_exists(self):
        assert (PHASE1_DIR / "canonical_events.json").exists()

    def test_handoff_exists(self):
        assert (PHASE1_DIR / "handoff_to_02.json").exists()

    def test_luke_5_scripture_exists(self):
        assert (CONTENT_DIR / "shared" / "scripture" / "luke_5.json").exists()


class TestPhaseConfig:
    def test_structure(self):
        data = json.loads(
            (PHASE1_DIR / "phase_config.json").read_text(encoding="utf-8"),
        )
        assert data["phase_id"] == "01_calling"
        assert data["tick_scale_hours"] == 2.0  # dense
        assert data["max_tick"] == 84  # 7일 × 12 tick
        assert "눅 5" in data["scripture_refs"][0]


class TestCanonicalEvents:
    def test_structure(self):
        data = json.loads(
            (PHASE1_DIR / "canonical_events.json").read_text(encoding="utf-8"),
        )
        assert data["meta"]["phase_id"] == "01_calling"
        assert data["meta"]["total_ticks"] == 84
        assert len(data["events"]) >= 4  # 최소 4개 scene

    def test_events_within_phase_tick_range(self):
        """모든 이벤트의 tick이 phase max_tick 내."""
        data = json.loads(
            (PHASE1_DIR / "canonical_events.json").read_text(encoding="utf-8"),
        )
        max_tick = data["meta"]["total_ticks"]
        for ev in data["events"]:
            assert 0 <= ev["tick"] <= max_tick, f"{ev['event_id']}: tick {ev['tick']} out of range"

    def test_events_tick_ordered(self):
        data = json.loads(
            (PHASE1_DIR / "canonical_events.json").read_text(encoding="utf-8"),
        )
        ticks = [ev["tick"] for ev in data["events"]]
        assert ticks == sorted(ticks), "events should be tick-ordered"

    def test_each_event_has_scripture_ref(self):
        data = json.loads(
            (PHASE1_DIR / "canonical_events.json").read_text(encoding="utf-8"),
        )
        for ev in data["events"]:
            assert "scripture_ref" in ev or "source_ref" in ev
            assert "눅 5" in ev.get("scripture_ref", "") or "눅 5" in ev.get("source_ref", "")

    def test_final_event_triggers_calling_accepted(self):
        """마지막 사건(소명 수락)에 leave_everything_follow 행동 포함."""
        data = json.loads(
            (PHASE1_DIR / "canonical_events.json").read_text(encoding="utf-8"),
        )
        final = data["events"][-1]
        action_ids = [a["action_id"] for a in final.get("action_options", [])]
        assert "leave_everything_follow" in action_ids


class TestHandoffSpec:
    def test_structure(self):
        data = json.loads(
            (PHASE1_DIR / "handoff_to_02.json").read_text(encoding="utf-8"),
        )
        assert data["phase_from"] == "01_calling"
        assert data["phase_to"] == "02_galilean"
        assert data["carry_all_slow_state"] is True

    def test_mappings_expected_fields(self):
        data = json.loads(
            (PHASE1_DIR / "handoff_to_02.json").read_text(encoding="utf-8"),
        )
        mapped_paths = {
            m["source_field_path"] for m in data["mappings"]
        }
        assert "domain_state.obedience_maturity" in mapped_paths
        assert "emotions.awe" in mapped_paths


class TestLuke5Scripture:
    def test_structure(self):
        data = json.loads(
            (CONTENT_DIR / "shared" / "scripture" / "luke_5.json").read_text(encoding="utf-8"),
        )
        assert data["book"] == "luke"
        assert data["chapter"] == 5
        assert data["version"] == "개역개정"

    def test_verses_1_to_11_present(self):
        """소명 본문 Luke 5:1-11 완비."""
        data = json.loads(
            (CONTENT_DIR / "shared" / "scripture" / "luke_5.json").read_text(encoding="utf-8"),
        )
        verse_nums = {v["verse"] for v in data["verses"]}
        for n in range(1, 12):
            assert n in verse_nums, f"Missing Luke 5:{n}"

    def test_key_phrases_preserved(self):
        """핵심 대사가 개역개정 원문 그대로 보존 (ABSOLUTE RULE #2)."""
        data = json.loads(
            (CONTENT_DIR / "shared" / "scripture" / "luke_5.json").read_text(encoding="utf-8"),
        )
        verses = {v["verse"]: v["text"] for v in data["verses"]}
        # 핵심 대사
        assert "깊은 데로 가서 그물을 내려" in verses[4]
        assert "말씀에 의지하여" in verses[5]
        assert "나를 떠나소서 나는 죄인이로소이다" in verses[8]
        assert "사람을 취하리라" in verses[10]
        assert "모든 것을 버려 두고 예수를 따르니라" in verses[11]
