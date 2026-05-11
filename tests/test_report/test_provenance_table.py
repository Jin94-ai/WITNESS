"""Unit tests for the Provenance Table builder (Phase 12)."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(
        name, ROOT / "scripts" / "report" / file
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# load brief first so provenance table can import it
_load("build_observer_brief", "build_observer_brief.py")
bpt = _load("build_provenance_table", "build_provenance_table.py")

SOURCE = ROOT / "data" / "visual" / "dot_observer_data.json"


def _build(tmp_path, include_holds=False, with_json=False):
    out_md = tmp_path / "ptab.md"
    out_json = (tmp_path / "ptab.json") if with_json else None
    bpt.main(str(SOURCE), str(out_md),
             run_label="peter_scarcity_baseline",
             include_holds=include_holds,
             out_json=str(out_json) if out_json else None)
    md = out_md.read_text(encoding="utf-8")
    payload = json.loads(out_json.read_text(encoding="utf-8")) if out_json else None
    return md, payload


def test_table_renders(tmp_path):
    md, _ = _build(tmp_path)
    assert "# WITNESS Provenance Table" in md
    assert "provenance_table_v1" in md


def test_table_lists_all_story_ready_candidates_as_sections(tmp_path):
    md, _ = _build(tmp_path)
    for cid in ("C01_t15", "C02_t25", "C03_t142", "C05_t147", "P03_t66_agent_08"):
        assert f"## {cid} —" in md, f"section for {cid} missing"


def test_each_section_lists_each_field_spec(tmp_path):
    md, _ = _build(tmp_path)
    # candidate-level fields
    for f in ("candidate_id", "tick", "tick_range", "agents_involved",
              "events_involved", "rationale", "signals", "use_mode"):
        assert f"`{f}`" in md
    # tick-level fields
    for f in ("world.crowd_mood", "world.authority_vigilance",
              "groups[].dominant_mode", "agents[].dominant_state",
              "agents[].fear", "agents[].salient"):
        assert f"`{f}`" in md
    # not_used fields
    for f in ("synthetic_guard_movement", "walking_frame_timeline",
              "speech_bubble_staging", "tile_grid_position",
              "hand_authored_cutscene_cues"):
        assert f"`{f}`" in md


def test_aggregate_dominated_by_source_derived(tmp_path):
    _, payload = _build(tmp_path, with_json=True)
    agg = payload["aggregate"]["by_class"]
    total = payload["aggregate"]["total_rows"]
    # source_derived should be > 50% of rows for a properly text-honest brief
    assert agg["source_derived"] / total > 0.5
    # not_used must be present (otherwise the brief silently omits visual fields)
    assert agg["not_used"] > 0


def test_class_values_are_valid(tmp_path):
    _, payload = _build(tmp_path, with_json=True)
    valid = {"source_derived", "source_inferred", "not_used"}
    for cand in payload["candidates"]:
        for row in cand["rows"]:
            assert row["class"] in valid, f"invalid class: {row['class']}"
            assert row["confidence"] in {"high", "medium", "low"}


def test_off_by_one_world_value_matches_tick(tmp_path):
    """world.* values in the C01_t15 section must come from tick 15, not 14 or 16."""
    md, _ = _build(tmp_path)
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    tick15 = next(t for t in obs["ticks"] if t["tick"] == 15)
    expected_av = f"{tick15['world']['authority_vigilance']:.3f}"
    section = md.split("## C01_t15")[1].split("## C")[0]
    assert expected_av in section


def test_include_holds_adds_hold_sections(tmp_path):
    md, _ = _build(tmp_path, include_holds=True)
    assert "## W03_t20" in md or "## E02_t102_public_denial" in md


def test_machine_readable_json_payload_shape(tmp_path):
    _, payload = _build(tmp_path, with_json=True)
    assert payload["schema_version"] == "provenance_table_v1"
    assert payload["run_label"] == "peter_scarcity_baseline"
    assert isinstance(payload["candidates"], list)
    for cand in payload["candidates"]:
        assert "candidate_id" in cand
        assert "rows" in cand
        for row in cand["rows"]:
            for k in ("field", "class", "confidence", "source", "value", "note"):
                assert k in row, f"row missing key {k}: {row}"
