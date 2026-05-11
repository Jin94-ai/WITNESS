"""Unit tests for world_flow_events_v1 adapter + audit.

Locks in:
  - schema validity
  - actor reference integrity
  - tick non-decreasing per window
  - provenance required on every visual_action
  - source-backed ratio computation
  - WFO-A/B/C decision matches Lee §17 thresholds
  - persistent actor state continuity (actors exist across all windows)
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "visual"))


def _load(module_name: str, file_name: str):
    spec = importlib.util.spec_from_file_location(
        module_name, ROOT / "scripts" / "visual" / file_name
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bwf = _load("build_world_flow_events", "build_world_flow_events.py")
auditor = _load("audit_world_flow_traceability", "audit_world_flow_traceability.py")

SOURCE_FILE = ROOT / "data" / "visual" / "dot_observer_data.json"


def _build_to_tmp(tmp_path):
    out_path = tmp_path / "world_flow_events.json"
    bwf.main(str(SOURCE_FILE), str(out_path))
    return json.loads(out_path.read_text(encoding="utf-8"))


# ============ schema + structural integrity ============

def test_schema_version(tmp_path):
    data = _build_to_tmp(tmp_path)
    assert data["meta"]["schema_version"] == "world_flow_events_v1"


def test_three_windows_generated(tmp_path):
    data = _build_to_tmp(tmp_path)
    assert len(data["windows"]) == 3
    cids = [w["candidate_id"] for w in data["windows"]]
    assert cids == ["C01_t15", "C02_t25", "C03_t142"]


def test_actors_unique(tmp_path):
    data = _build_to_tmp(tmp_path)
    ids = [a["id"] for a in data["actors"]]
    assert len(ids) == len(set(ids))


def test_engine_agents_count(tmp_path):
    data = _build_to_tmp(tmp_path)
    engine_agents = [a for a in data["actors"] if a["source_kind"] == "engine_agent"]
    assert len(engine_agents) == 12, "expected 12 engine_agent actors (peter_scarcity_baseline)"


def test_synthetic_guard_present_when_guard_event(tmp_path):
    data = _build_to_tmp(tmp_path)
    synthetic = [a for a in data["actors"] if a["source_kind"] == "synthetic_authority"]
    # C01_t15 has guard_approaches in events_involved; should produce 1 synthetic
    assert len(synthetic) == 1
    assert synthetic[0]["id"] == "guard"


def test_window_tick_ranges_correct(tmp_path):
    data = _build_to_tmp(tmp_path)
    expected = {
        "C01_t15": [13, 17],
        "C02_t25": [23, 27],
        "C03_t142": [140, 144],
    }
    for w in data["windows"]:
        assert w["tick_range"] == expected[w["candidate_id"]]


def test_ticks_non_decreasing_per_window(tmp_path):
    data = _build_to_tmp(tmp_path)
    for w in data["windows"]:
        ticks = [t["tick"] for t in w["ticks"]]
        assert ticks == sorted(ticks), f"{w['window_id']} ticks not sorted: {ticks}"


# ============ provenance integrity ============

VALID_CLASSES = {"source_derived", "source_inferred", "staged_only"}
VALID_CONFIDENCE = {"high", "medium", "low"}


def test_every_visual_action_has_provenance(tmp_path):
    data = _build_to_tmp(tmp_path)
    for w in data["windows"]:
        for tk in w["ticks"]:
            for va in tk["visual_actions"]:
                assert "provenance" in va, (
                    f"window {w['window_id']} tick {tk['tick']} "
                    f"action type={va.get('type')} missing provenance"
                )


def test_provenance_class_valid(tmp_path):
    data = _build_to_tmp(tmp_path)
    for w in data["windows"]:
        for tk in w["ticks"]:
            for va in tk["visual_actions"]:
                cls = va["provenance"].get("class")
                assert cls in VALID_CLASSES, f"invalid class '{cls}'"


def test_provenance_confidence_valid(tmp_path):
    data = _build_to_tmp(tmp_path)
    for w in data["windows"]:
        for tk in w["ticks"]:
            for va in tk["visual_actions"]:
                conf = va["provenance"].get("confidence")
                assert conf in VALID_CONFIDENCE, f"invalid confidence '{conf}'"


def test_provenance_mapping_present(tmp_path):
    data = _build_to_tmp(tmp_path)
    for w in data["windows"]:
        for tk in w["ticks"]:
            for va in tk["visual_actions"]:
                mapping = va["provenance"].get("mapping")
                assert isinstance(mapping, str) and mapping, "provenance.mapping missing or empty"


def test_actor_references_resolve(tmp_path):
    data = _build_to_tmp(tmp_path)
    actor_ids = {a["id"] for a in data["actors"]}
    for w in data["windows"]:
        for tk in w["ticks"]:
            for va in tk["visual_actions"]:
                actor = va.get("actor")
                # null actor allowed for world-level events
                if actor is not None:
                    assert actor in actor_ids, (
                        f"window {w['window_id']} tick {tk['tick']} action references "
                        f"undefined actor '{actor}'"
                    )


# ============ summary correctness ============

def test_summary_counts_match_actions(tmp_path):
    data = _build_to_tmp(tmp_path)
    expected = {"source_derived": 0, "source_inferred": 0, "staged_only": 0}
    for w in data["windows"]:
        for tk in w["ticks"]:
            for va in tk["visual_actions"]:
                cls = va["provenance"]["class"]
                expected[cls] += 1
    summary = data["summary"]
    assert summary["source_derived"] == expected["source_derived"]
    assert summary["source_inferred"] == expected["source_inferred"]
    assert summary["staged_only"] == expected["staged_only"]


def test_total_visual_actions_matches(tmp_path):
    data = _build_to_tmp(tmp_path)
    actual_total = 0
    for w in data["windows"]:
        for tk in w["ticks"]:
            actual_total += len(tk["visual_actions"])
    assert data["summary"]["total_visual_actions"] == actual_total


def test_source_backed_ratio_computed(tmp_path):
    data = _build_to_tmp(tmp_path)
    s = data["summary"]
    expected_ratio = (s["source_derived"] + s["source_inferred"]) / s["total_visual_actions"]
    assert abs(s["source_backed_ratio"] - round(expected_ratio, 3)) < 0.001


# ============ WFO case decision ============

def test_wfo_case_a_or_b_for_current_data(tmp_path):
    """Current adapter should achieve WFO-A or strong WFO-B (Lee §17 target)."""
    data = _build_to_tmp(tmp_path)
    case = data["summary"]["wfo_case_estimate"]
    assert case in ("WFO-A", "WFO-B"), f"Adapter produced {case}, below acceptable threshold"


def test_audit_decide_case_logic():
    """Audit threshold logic — pure function test."""
    assert auditor.decide_case(0.95, 0.05) == "WFO-A"
    assert auditor.decide_case(0.80, 0.20) == "WFO-A"
    assert auditor.decide_case(0.79, 0.21) == "WFO-B"
    assert auditor.decide_case(0.65, 0.30) == "WFO-B"
    assert auditor.decide_case(0.55, 0.40) == "WFO-C"
    assert auditor.decide_case(0.30, 0.10) == "WFO-C"


# ============ persistent actor state ============

def test_all_engine_agents_appear_in_first_window_spawn(tmp_path):
    """All 12 source agents must spawn at the first window's first tick."""
    data = _build_to_tmp(tmp_path)
    first_window = data["windows"][0]
    first_tick = first_window["ticks"][0]
    spawn_actors = {
        va["actor"] for va in first_tick["visual_actions"]
        if va["type"] == "spawn" and va.get("actor")
    }
    engine_ids = {a["id"] for a in data["actors"] if a["source_kind"] == "engine_agent"}
    assert engine_ids.issubset(spawn_actors), (
        f"missing spawn actions for engine agents: {engine_ids - spawn_actors}"
    )


def test_transitions_between_windows_present(tmp_path):
    data = _build_to_tmp(tmp_path)
    assert "transitions" in data
    assert len(data["transitions"]) == 2  # 3 windows -> 2 transitions
    for t in data["transitions"]:
        assert "agent_summary" in t
        assert "world_mood_summary" in t
        assert t["from_tick"] < t["to_tick"]


def test_transition_agent_summary_covers_all_engine_agents(tmp_path):
    data = _build_to_tmp(tmp_path)
    engine_ids = {a["id"] for a in data["actors"] if a["source_kind"] == "engine_agent"}
    for t in data["transitions"]:
        summary_ids = set(t["agent_summary"].keys())
        assert engine_ids.issubset(summary_ids), (
            f"transition missing summary for: {engine_ids - summary_ids}"
        )


# ============ no staged_only by default (Lee §6.4 / §8.4) ============

def test_no_staged_only_actions(tmp_path):
    """WFO v0 design goal: zero staged_only. Every action is source-backed."""
    data = _build_to_tmp(tmp_path)
    staged_actions = []
    for w in data["windows"]:
        for tk in w["ticks"]:
            for va in tk["visual_actions"]:
                if va["provenance"]["class"] == "staged_only":
                    staged_actions.append((w["window_id"], tk["tick"], va["type"]))
    assert not staged_actions, f"staged_only actions found: {staged_actions}"


# ============ key event types present ============

def test_state_change_actions_present_when_deltas_exist(tmp_path):
    """When agent state changes occur in source, state_change actions must be emitted."""
    data = _build_to_tmp(tmp_path)
    state_changes = []
    for w in data["windows"]:
        for tk in w["ticks"]:
            for va in tk["visual_actions"]:
                if va["type"] == "state_change":
                    state_changes.append(va)
    # There should be at least some state changes across the 3 windows
    # (fragmenting transitions etc)
    assert len(state_changes) > 0, "no state_change actions emitted — adapter not detecting deltas?"


def test_emote_event_attributed_when_active_event_exists(tmp_path):
    data = _build_to_tmp(tmp_path)
    # Each active_events entry should produce one emote_event (when actor attributed)
    for w in data["windows"]:
        for tk in w["ticks"]:
            attributed_count = sum(
                1 for ev in tk.get("active_events", [])
                if ev.get("attributed_actor")
            )
            emote_count = sum(
                1 for va in tk["visual_actions"] if va["type"] == "emote_event"
            )
            assert emote_count == attributed_count, (
                f"window {w['window_id']} tick {tk['tick']}: "
                f"attributed events={attributed_count} but emote_event actions={emote_count}"
            )


# ============ long-form mode coverage (200-tick viewer) ============

def _build_long_form(tmp_path):
    out_path = tmp_path / "world_flow_events_long.json"
    bwf.main(str(SOURCE_FILE), str(out_path), mode="long_form")
    return json.loads(out_path.read_text(encoding="utf-8"))


def test_long_form_single_window(tmp_path):
    data = _build_long_form(tmp_path)
    assert len(data["windows"]) == 1
    w = data["windows"][0]
    # full simulation range
    assert w["tick_range"] == [0, 199]
    assert len(w["ticks"]) == 200


def test_long_form_meta_carries_canvas(tmp_path):
    data = _build_long_form(tmp_path)
    meta = data["meta"]
    assert meta.get("canvas_width") == 800
    assert meta.get("canvas_height") == 500
    assert "L1" in meta.get("group_centers", {})
    assert "L2" in meta.get("group_centers", {})
    assert "L3" in meta.get("group_centers", {})


def test_long_form_no_staged_actions(tmp_path):
    data = _build_long_form(tmp_path)
    staged = 0
    total = 0
    for w in data["windows"]:
        for tk in w["ticks"]:
            for va in tk.get("visual_actions", []):
                total += 1
                if va.get("provenance", {}).get("class") == "staged_only":
                    staged += 1
    assert total > 0
    assert staged == 0, (
        f"long-form must remain WFO-A (0 staged actions); got {staged}/{total}"
    )


def test_long_form_actors_include_engine_twelve(tmp_path):
    data = _build_long_form(tmp_path)
    ids = [a["id"] for a in data["actors"]]
    for i in range(1, 13):
        assert f"agent_{i:02d}" in ids, f"agent_{i:02d} missing from long-form actors"


def test_long_form_emote_glyph_coverage(tmp_path):
    """Each event_name fired in observer.active_events should be representable
    by an emote_event in long-form (so the viewer's glyph vocabulary stays bounded)."""
    obs = json.loads(SOURCE_FILE.read_text(encoding="utf-8"))
    seen_in_observer = set()
    for tk in obs["ticks"]:
        for ev in tk.get("active_events", []):
            name = ev if isinstance(ev, str) else ev.get("name")
            if name:
                seen_in_observer.add(name)

    data = _build_long_form(tmp_path)
    seen_in_emotes = set()
    for w in data["windows"]:
        for tk in w["ticks"]:
            for va in tk.get("visual_actions", []):
                if va.get("type") == "emote_event":
                    seen_in_emotes.add(va["params"].get("event_name"))

    missing = seen_in_observer - seen_in_emotes
    assert not missing, f"long-form missed event_names: {sorted(missing)}"


def test_long_form_tick_indices_complete_and_ordered(tmp_path):
    data = _build_long_form(tmp_path)
    w = data["windows"][0]
    ticks = [tk["tick"] for tk in w["ticks"]]
    assert ticks == list(range(200))
