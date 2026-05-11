"""Unit tests for the Observer Brief builder (Phase 11)."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load_builder():
    spec = importlib.util.spec_from_file_location(
        "build_observer_brief",
        ROOT / "scripts" / "report" / "build_observer_brief.py",
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["build_observer_brief"] = mod
    spec.loader.exec_module(mod)
    return mod


bob = _load_builder()
SOURCE = ROOT / "data" / "visual" / "dot_observer_data.json"


def _build_to_tmp(tmp_path):
    out = tmp_path / "brief.md"
    bob.main(str(SOURCE), str(out), run_label="peter_scarcity_baseline")
    return out.read_text(encoding="utf-8")


def test_brief_renders(tmp_path):
    md = _build_to_tmp(tmp_path)
    assert "# WITNESS Observer Brief" in md
    assert "peter_scarcity_baseline" in md


def test_brief_lists_story_ready_candidates(tmp_path):
    md = _build_to_tmp(tmp_path)
    # all five story_ready candidates present in dot_observer_data.json
    for cid in ("C01_t15", "C02_t25", "C03_t142", "C05_t147", "P03_t66_agent_08"):
        assert cid in md, f"{cid} missing from brief"


def test_brief_excludes_low_activity_holds_by_default(tmp_path):
    md = _build_to_tmp(tmp_path)
    # default mode list is story_ready only — these should NOT appear in card section
    # (we still allow the executive summary to mention counts)
    for cid in ("W03_t20", "E02_t102_public_denial", "E03_t112_visible_grief"):
        # they should not appear as candidate-card headers
        assert f"### {cid} —" not in md, f"hold candidate {cid} leaked into card section"


def test_brief_provenance_block_per_card(tmp_path):
    md = _build_to_tmp(tmp_path)
    # each story_ready candidate gets its own Provenance block
    assert md.count("**Provenance**") == 5


def test_brief_run_context_lists_seed_and_n_ticks(tmp_path):
    md = _build_to_tmp(tmp_path)
    assert "n_ticks | 200" in md
    assert "seed | 0" in md
    assert "agent_count | 12" in md


def test_brief_no_narrative_renderer_leakage(tmp_path):
    """Phase 11 explicitly forbids story-renderer-style prose. Make sure none
    of the disallowed framings reappeared."""
    md = _build_to_tmp(tmp_path)
    forbidden = [
        "once upon a time",
        "his heart",  # third-person psychological narration
        "in the silence",
        "the prophet",
        "the disciple",
    ]
    for f in forbidden:
        assert f.lower() not in md.lower(), (
            f"forbidden narrative phrase '{f}' appeared in brief"
        )


def test_brief_includes_provenance_table_columns(tmp_path):
    md = _build_to_tmp(tmp_path)
    assert "Source-derived" in md
    assert "Source-inferred" in md
    assert "Use mode" in md


def test_brief_world_snapshot_uses_correct_tick(tmp_path):
    """C01_t15 should report the world snapshot AT tick 15, not tick 16.
    This guards the off-by-one fix in get_tick()."""
    md = _build_to_tmp(tmp_path)
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    # find tick 15's world readings
    tick15 = next(t for t in obs["ticks"] if t["tick"] == 15)
    expected_av = f"{tick15['world']['authority_vigilance']:.3f}"
    # locate C01_t15 card and check the authority_vigilance line is from tick 15
    c01 = md.split("### C01_t15")[1].split("### ")[0]
    assert f"authority_vigilance: {expected_av}" in c01


def test_brief_includes_holds_when_flag_set(tmp_path):
    out = tmp_path / "brief_full.md"
    bob.main(str(SOURCE), str(out), run_label="peter_scarcity_baseline",
             include_holds=True)
    md = out.read_text(encoding="utf-8")
    # at least one hold candidate is now in the card section
    has_hold_card = any(
        f"### {cid} —" in md
        for cid in ("W03_t20", "E02_t102_public_denial", "E03_t112_visible_grief")
    )
    assert has_hold_card


def test_filter_candidates_returns_only_requested_modes():
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    only_ready = bob.filter_candidates(obs, ("story_ready",))
    assert all(c["use_mode"] == "story_ready" for c in only_ready)
    only_holds = bob.filter_candidates(obs, ("low_activity_hold",))
    assert all(c["use_mode"] == "low_activity_hold" for c in only_holds)


# ============ generalization across other anchors (lock-in) ============

ALT_DUMPS = [
    (ROOT / "data" / "visual" / "dot_observer_data_triple.json",
     "peter_scarcity_triple", False, True),   # has story_ready candidates
    (ROOT / "data" / "visual" / "dot_observer_data_vangogh.json",
     "vangogh_sacred_baseline", True, True),  # 0 story_ready, hold-only
]


def test_brief_builder_generalizes_to_alt_anchors(tmp_path):
    """Same brief builder must run on any observer dump matching the schema.
    This locks the data-source-agnostic shape of the builder."""
    for src, label, include_holds, expect_card in ALT_DUMPS:
        if not src.exists():
            continue  # tolerate missing alt dumps in trimmed checkouts
        out = tmp_path / f"brief_{label}.md"
        bob.main(str(src), str(out), run_label=label, include_holds=include_holds)
        md = out.read_text(encoding="utf-8")
        assert label in md, f"label {label} missing from header"
        assert "# WITNESS Observer Brief" in md
        if expect_card:
            assert "Provenance" in md, f"no Provenance block in {label} brief"
