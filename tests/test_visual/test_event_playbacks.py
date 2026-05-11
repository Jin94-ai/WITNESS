"""Unit tests for event_playback_v1 generation + validation.

Locks in:
  - build_event_playbacks.py output passes validate_event_playbacks.py
  - 5-second readability rule (KEY reaction event ≤ 5000ms per playback)
  - Schema invariants (uniqueness, t-ordering, bounds, types)
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


bep = _load("build_event_playbacks", "build_event_playbacks.py")
vep = _load("validate_event_playbacks", "validate_event_playbacks.py")


# ============ build → validate roundtrip ============

def test_validator_passes_on_committed_playbacks(tmp_path):
    """The committed event_playbacks.json must pass validation."""
    in_path = ROOT / "data" / "visual" / "dot_observer_data.json"
    out_path = tmp_path / "event_playbacks.json"
    bep.main(str(in_path), str(out_path))
    rc = vep.main(str(out_path))
    assert rc == 0, "validate_event_playbacks rejected build output"


def test_three_target_playbacks_generated(tmp_path):
    in_path = ROOT / "data" / "visual" / "dot_observer_data.json"
    out_path = tmp_path / "event_playbacks.json"
    bep.main(str(in_path), str(out_path))
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["meta"]["schema_version"] == "event_playback_v1"
    assert data["meta"]["playback_count"] == 3
    ids = [p["candidate_id"] for p in data["playbacks"]]
    assert ids == ["C01_t15", "C02_t25", "C03_t142"]


# ============ 5-second readability rule (Lee Wide Plan §4.1) ============

def _key_reaction_t(playback: dict) -> int | None:
    for ev in playback.get("timeline", []):
        if ev.get("type") in vep.KEY_REACTION_EVENTS:
            return ev.get("t", 0)
    return None


def test_all_playbacks_have_key_reaction_within_5s(tmp_path):
    """Each playback's first emote/pose_change must occur within 5000ms.

    This is the core rule of PEP timing cleanup — if violated, the 5-second
    test fails even when the full cutscene is internally coherent.
    """
    in_path = ROOT / "data" / "visual" / "dot_observer_data.json"
    out_path = tmp_path / "event_playbacks.json"
    bep.main(str(in_path), str(out_path))
    data = json.loads(out_path.read_text(encoding="utf-8"))
    for pb in data["playbacks"]:
        t = _key_reaction_t(pb)
        assert t is not None, f"{pb['playback_id']} has no key reaction event"
        assert t <= vep.KEY_REACTION_DEADLINE_MS, (
            f"{pb['playback_id']} key reaction at {t}ms exceeds 5000ms"
        )


def test_speech_appears_within_2_5s(tmp_path):
    """Speech events should start by 2.5s for trigger readability.

    Per Lee Wide Plan §4.1: speech 1.2-2.2s recommended; 2500ms is the soft cap.
    """
    in_path = ROOT / "data" / "visual" / "dot_observer_data.json"
    out_path = tmp_path / "event_playbacks.json"
    bep.main(str(in_path), str(out_path))
    data = json.loads(out_path.read_text(encoding="utf-8"))
    for pb in data["playbacks"]:
        speech_events = [e for e in pb["timeline"] if e.get("type") == "speech"]
        if not speech_events:
            continue
        first_speech = speech_events[0]
        assert first_speech["t"] <= 2500, (
            f"{pb['playback_id']} first speech at {first_speech['t']}ms "
            "exceeds 2500ms — trigger signal too late for 5-sec readability"
        )


# ============ schema invariants ============

def test_actor_ids_unique_per_playback(tmp_path):
    in_path = ROOT / "data" / "visual" / "dot_observer_data.json"
    out_path = tmp_path / "event_playbacks.json"
    bep.main(str(in_path), str(out_path))
    data = json.loads(out_path.read_text(encoding="utf-8"))
    for pb in data["playbacks"]:
        ids = [a["id"] for a in pb["actors"]]
        assert len(ids) == len(set(ids)), f"{pb['playback_id']} has duplicate actor ids"


def test_timeline_t_non_decreasing(tmp_path):
    in_path = ROOT / "data" / "visual" / "dot_observer_data.json"
    out_path = tmp_path / "event_playbacks.json"
    bep.main(str(in_path), str(out_path))
    data = json.loads(out_path.read_text(encoding="utf-8"))
    for pb in data["playbacks"]:
        last = -1
        for ev in pb["timeline"]:
            t = ev.get("t", 0)
            assert t >= last, f"{pb['playback_id']} t={t} regresses from {last}"
            last = t


def test_actor_refs_resolve(tmp_path):
    in_path = ROOT / "data" / "visual" / "dot_observer_data.json"
    out_path = tmp_path / "event_playbacks.json"
    bep.main(str(in_path), str(out_path))
    data = json.loads(out_path.read_text(encoding="utf-8"))
    for pb in data["playbacks"]:
        actor_ids = {a["id"] for a in pb["actors"]}
        for ev in pb["timeline"]:
            if "actor" in ev and not ev["actor"].startswith("__"):
                assert ev["actor"] in actor_ids, (
                    f"{pb['playback_id']} event refers to undefined actor '{ev['actor']}'"
                )
            if ev.get("type") == "crowd_react":
                for cid in ev.get("actors", []):
                    assert cid in actor_ids, (
                        f"{pb['playback_id']} crowd_react actor '{cid}' undefined"
                    )


def test_move_targets_within_stage(tmp_path):
    in_path = ROOT / "data" / "visual" / "dot_observer_data.json"
    out_path = tmp_path / "event_playbacks.json"
    bep.main(str(in_path), str(out_path))
    data = json.loads(out_path.read_text(encoding="utf-8"))
    for pb in data["playbacks"]:
        w = pb["map"]["width_tiles"]
        h = pb["map"]["height_tiles"]
        for ev in pb["timeline"]:
            if ev.get("type") == "move":
                tx, ty = ev["to"]["x"], ev["to"]["y"]
                assert 0 <= tx < w and 0 <= ty < h, (
                    f"{pb['playback_id']} move target ({tx},{ty}) out of bounds {w}x{h}"
                )


def test_only_supported_event_types(tmp_path):
    in_path = ROOT / "data" / "visual" / "dot_observer_data.json"
    out_path = tmp_path / "event_playbacks.json"
    bep.main(str(in_path), str(out_path))
    data = json.loads(out_path.read_text(encoding="utf-8"))
    for pb in data["playbacks"]:
        for ev in pb["timeline"]:
            assert ev.get("type") in vep.SUPPORTED_EVENT_TYPES, (
                f"{pb['playback_id']} unsupported event type '{ev.get('type')}'"
            )


def test_events_within_duration(tmp_path):
    in_path = ROOT / "data" / "visual" / "dot_observer_data.json"
    out_path = tmp_path / "event_playbacks.json"
    bep.main(str(in_path), str(out_path))
    data = json.loads(out_path.read_text(encoding="utf-8"))
    for pb in data["playbacks"]:
        dur = pb["duration_ms"]
        for ev in pb["timeline"]:
            assert ev.get("t", 0) <= dur, (
                f"{pb['playback_id']} event t={ev['t']} exceeds duration {dur}"
            )


# ============ Lee Wide Directive §5.5: Scene-specific staging tests ============

def _load_playbacks(tmp_path):
    in_path = ROOT / "data" / "visual" / "dot_observer_data.json"
    out_path = tmp_path / "event_playbacks.json"
    bep.main(str(in_path), str(out_path))
    return json.loads(out_path.read_text(encoding="utf-8"))


def _pb_by_id(data, candidate_id):
    return next(p for p in data["playbacks"] if p["candidate_id"] == candidate_id)


def test_scene_01_has_authority_move_before_focal_retreat(tmp_path):
    """C01: guard must move BEFORE focal step_back (causal order)."""
    data = _load_playbacks(tmp_path)
    pb = _pb_by_id(data, "C01_t15")
    auth_move_t = None
    focal_step_t = None
    for ev in pb["timeline"]:
        if ev.get("type") == "move" and ev.get("actor") == "guard" and auth_move_t is None:
            auth_move_t = ev["t"]
        if ev.get("type") == "step_back" and ev.get("actor", "").startswith("agent_") and focal_step_t is None:
            focal_step_t = ev["t"]
    assert auth_move_t is not None, "C01 missing guard move event"
    assert focal_step_t is not None, "C01 missing focal step_back event"
    assert auth_move_t < focal_step_t, (
        f"C01 guard move ({auth_move_t}ms) must precede focal step_back ({focal_step_t}ms) "
        "for causal order"
    )
    assert focal_step_t <= 4500, (
        f"C01 focal step_back at {focal_step_t}ms exceeds 4500ms (Lee §5.4 #6)"
    )


def test_scene_02_has_speaker_then_grief_then_right_group_withdrawal(tmp_path):
    """C02: agent_03 speech → agent_05 grief → right witnesses retreat (causal chain)."""
    data = _load_playbacks(tmp_path)
    pb = _pb_by_id(data, "C02_t25")
    speech_t = None
    grief_t = None
    right_retreat_t = None
    right_actors = {"agent_02", "agent_08"}
    for ev in pb["timeline"]:
        if ev.get("type") == "speech" and ev.get("actor") == "agent_03" and speech_t is None:
            speech_t = ev["t"]
        if ev.get("type") == "emote" and ev.get("emote") == "grief" and grief_t is None:
            grief_t = ev["t"]
        if ev.get("type") == "move" and ev.get("actor") in right_actors and right_retreat_t is None:
            right_retreat_t = ev["t"]
    assert speech_t is not None, "C02 missing agent_03 speech"
    assert grief_t is not None, "C02 missing grief emote"
    assert right_retreat_t is not None, "C02 missing right group withdrawal"
    assert speech_t < grief_t, (
        f"C02 speech ({speech_t}ms) must precede grief ({grief_t}ms)"
    )
    assert grief_t < right_retreat_t, (
        f"C02 grief ({grief_t}ms) must precede right group retreat ({right_retreat_t}ms)"
    )
    assert right_retreat_t <= 5000, (
        f"C02 right group retreat at {right_retreat_t}ms exceeds 5000ms"
    )


def test_scene_03_has_speech_crowd_react_kneel_supporter_inward_within_5s(tmp_path):
    """C03: speech → crowd_react → kneel → supporter inward, all within 5s."""
    data = _load_playbacks(tmp_path)
    pb = _pb_by_id(data, "C03_t142")
    speech_t = None
    crowd_t = None
    kneel_t = None
    supporter_inward_t = None
    supporter_actors = {"agent_06", "agent_12"}
    for ev in pb["timeline"]:
        if ev.get("type") == "speech" and speech_t is None:
            speech_t = ev["t"]
        if ev.get("type") == "crowd_react" and crowd_t is None:
            crowd_t = ev["t"]
        if ev.get("type") == "pose_change" and ev.get("pose") == "kneeling" and kneel_t is None:
            kneel_t = ev["t"]
        if ev.get("type") == "move" and ev.get("actor") in supporter_actors and supporter_inward_t is None:
            supporter_inward_t = ev["t"]
    assert speech_t is not None and speech_t <= 2500, f"C03 speech missing or > 2500ms: {speech_t}"
    assert crowd_t is not None and crowd_t <= 4000, f"C03 crowd_react missing or > 4000ms: {crowd_t}"
    assert kneel_t is not None and kneel_t <= 4000, f"C03 kneel missing or > 4000ms: {kneel_t}"
    assert supporter_inward_t is not None and supporter_inward_t <= 5000, (
        f"C03 supporter inward missing or > 5000ms: {supporter_inward_t}"
    )
    # causal order
    assert speech_t < crowd_t < kneel_t, (
        f"C03 order broken: speech={speech_t}, crowd_react={crowd_t}, kneel={kneel_t}"
    )


def test_no_new_event_types_introduced(tmp_path):
    """Ensure no event type is added beyond the supported 8+1 set."""
    data = _load_playbacks(tmp_path)
    seen_types = set()
    for pb in data["playbacks"]:
        for ev in pb["timeline"]:
            seen_types.add(ev.get("type"))
    extra = seen_types - vep.SUPPORTED_EVENT_TYPES
    assert not extra, (
        f"New event types introduced: {extra}. PEP grammar locked at "
        f"{sorted(vep.SUPPORTED_EVENT_TYPES)}."
    )


def test_no_relation_line_or_overlay_events(tmp_path):
    """Ensure no relation_line / wave / aura / rift overlay events leak in.

    Lee Wide Directive §9 absolute prohibition.
    """
    data = _load_playbacks(tmp_path)
    forbidden_substrings = ("relation", "wave", "aura", "rift", "overlay", "diagram")
    for pb in data["playbacks"]:
        for ev in pb["timeline"]:
            ev_type = ev.get("type", "")
            for word in forbidden_substrings:
                assert word not in ev_type.lower(), (
                    f"{pb['playback_id']} event_type '{ev_type}' contains forbidden '{word}' "
                    f"(Lee §9 prohibition)"
                )


def test_all_playbacks_have_visible_motion_before_4s(tmp_path):
    """Each playback must have at least one move/step_back event before 4000ms.

    Lee §5.4 #3: visible motion event < 4s for liveness.
    """
    data = _load_playbacks(tmp_path)
    for pb in data["playbacks"]:
        has_motion = any(
            ev.get("type") in ("move", "step_back") and ev.get("t", 0) < 4000
            for ev in pb["timeline"]
        )
        assert has_motion, (
            f"{pb['playback_id']} no motion event (move/step_back) before 4000ms — "
            f"actors must visibly move for liveness"
        )


# ============ WVT (World-to-Visual Traceability) tests — Lee §8.4 ============

def test_every_playback_has_source_trace(tmp_path):
    data = _load_playbacks(tmp_path)
    for pb in data["playbacks"]:
        assert "source_trace" in pb, f"{pb['playback_id']} missing source_trace (WVT §6.1)"
        st = pb["source_trace"]
        for f in ("anchor_id", "candidate_id", "tick", "source_events", "source_signals", "mapping_mode", "traceability_note"):
            assert f in st, f"{pb['playback_id']} source_trace missing field '{f}'"
        assert st["anchor_id"] == "peter_scarcity_baseline"
        assert st["candidate_id"] == pb["candidate_id"]


def test_every_event_has_source(tmp_path):
    data = _load_playbacks(tmp_path)
    for pb in data["playbacks"]:
        for i, ev in enumerate(pb["timeline"]):
            assert "source" in ev, (
                f"{pb['playback_id']} event[{i}] type={ev.get('type')} missing 'source' "
                f"(WVT §6.2)"
            )


def test_source_class_is_valid(tmp_path):
    data = _load_playbacks(tmp_path)
    for pb in data["playbacks"]:
        for i, ev in enumerate(pb["timeline"]):
            cls = ev["source"].get("class")
            assert cls in vep.SOURCE_CLASSES, (
                f"{pb['playback_id']} event[{i}] source.class='{cls}' not in {vep.SOURCE_CLASSES}"
            )


def test_source_confidence_is_valid(tmp_path):
    data = _load_playbacks(tmp_path)
    for pb in data["playbacks"]:
        for i, ev in enumerate(pb["timeline"]):
            conf = ev["source"].get("confidence")
            assert conf in vep.CONFIDENCE_LEVELS, (
                f"{pb['playback_id']} event[{i}] source.confidence='{conf}' not in {vep.CONFIDENCE_LEVELS}"
            )


def test_source_kind_is_valid(tmp_path):
    data = _load_playbacks(tmp_path)
    for pb in data["playbacks"]:
        for i, ev in enumerate(pb["timeline"]):
            kind = ev["source"].get("kind")
            assert kind in vep.SOURCE_KINDS, (
                f"{pb['playback_id']} event[{i}] source.kind='{kind}' not in {vep.SOURCE_KINDS}"
            )


def test_source_mapping_string_present(tmp_path):
    data = _load_playbacks(tmp_path)
    for pb in data["playbacks"]:
        for i, ev in enumerate(pb["timeline"]):
            mapping = ev["source"].get("mapping")
            assert isinstance(mapping, str) and mapping, (
                f"{pb['playback_id']} event[{i}] source.mapping missing or empty"
            )


def test_staged_only_ratio_below_vt_b_max(tmp_path):
    """Staged-only ratio must be ≤ 45% (VT-B max). Higher means VT-C territory."""
    data = _load_playbacks(tmp_path)
    counts = {"source_derived": 0, "source_inferred": 0, "staged_only": 0}
    for pb in data["playbacks"]:
        for ev in pb["timeline"]:
            cls = ev["source"].get("class")
            if cls in counts:
                counts[cls] += 1
    total = sum(counts.values())
    staged_ratio = counts["staged_only"] / total if total else 1.0
    assert staged_ratio <= vep.VT_B_STAGED_MAX, (
        f"staged_only ratio {staged_ratio:.2%} exceeds VT-B max {vep.VT_B_STAGED_MAX:.0%} "
        f"({counts['staged_only']}/{total} events) — visual mostly hand-authored"
    )


def test_source_derived_events_reference_known_source(tmp_path):
    """source_derived events must reference an event/signal/state present in source data."""
    data = _load_playbacks(tmp_path)
    for pb in data["playbacks"]:
        st = pb["source_trace"]
        known_events = set(st.get("source_events", []) + st.get("source_active_events_at_tick", []))
        known_signals = set(st.get("source_signals", []))
        for i, ev in enumerate(pb["timeline"]):
            s = ev["source"]
            if s["class"] != "source_derived":
                continue
            mapping = s.get("source", "")
            kind = s.get("kind")
            if kind == "observer_event":
                # mapping should reference at least one source event
                assert any(e in mapping for e in known_events), (
                    f"{pb['playback_id']} event[{i}] source_derived mapping does not "
                    f"reference any known source event. mapping='{mapping[:80]}', "
                    f"known={list(known_events)[:5]}"
                )
            elif kind == "candidate_signal":
                assert any(sig in mapping for sig in known_signals), (
                    f"{pb['playback_id']} event[{i}] source_derived mapping does not "
                    f"reference any known signal. mapping='{mapping[:80]}'"
                )


def test_compute_vt_case_returns_b_or_better(tmp_path):
    """Current PEP should compute as VT-B or VT-A (not VT-C)."""
    data = _load_playbacks(tmp_path)
    case, summary = vep.compute_vt_case(data["playbacks"])
    assert case in ("VT-A", "VT-B"), (
        f"VT case {case} indicates inadequate traceability. Summary: {summary}"
    )
