"""Tests for scripts/skeleton/validate_skeleton_phase3.py CLI.

Phase 2.5 cycle 5: Phase 3 Go gate를 CLI로 호출 가능하게 함. CI / PR 게이트
용도. exit 0 = pass, exit 1 = semantic violation, exit 2 = file/parse error.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/skeleton/validate_skeleton_phase3.py"
DEPLOYED = ROOT / "docs/portfolio/demo/skeleton_output.json"


def _make_minimal_skeleton(**overrides) -> dict:
    seed = {
        "schema_version": "universal_story_seed_v1_1",
        "seed_id": "S01",
        "conflict_axis_id": "loyalty_vs_survival",
        "main_role": "protagonist",
        "main_archetype": "loyal_under_pressure",
        "dominant_pressures": ["fear"],
        "dominant_desires": ["loyalty"],
        "supporting_archetypes": [],
        "supporting_roles": [],
        "pressure_pattern": {},
        "change_pattern": "stay_present_then_withdraw",
        "arc_direction": "visibility_to_silence",
        "relationship_function": "group_presence_without_action",
        "flow_role": "main_arc",
        "turning_points_count": 1,
        "confidence_label": "",
        "audit_status": "pass",
        "evidence_count": 1,
        "notes": [],
    }
    base = {
        "schema_version": "skeleton_output_v1",
        "seeds": [seed],
        "flow": {
            "schema_version": "life_story_flow_v1_1",
            "ordering": "evidence_derived",
            "ordered_seed_ids": ["S01"],
            "flow_roles": {"S01": "main_arc"},
        },
        "evidence_ledger": {
            "schema_version": "evidence_ledger_v1",
            "total_signals": 1,
            "signals_per_seed": {"S01": 1},
            "audit_pass_count": 1, "audit_fail_count": 0,
            "audit_risky_count": 0, "forbidden_token_violations": 0,
            "notes": [],
        },
        "anchor_metadata": {
            "anchor_id": "test", "display_name_overrides": {},
            "role_label_overrides": {}, "description_ko": "",
        },
        "audit_trail": {
            "schema_version": "audit_trail_v1_1",
            "stages_passed": ["moments"],
            "forbidden_event_additions": 0, "forbidden_dialogue_generation": 0,
            "forbidden_slugline_use": 0,
            "unmapped_pressure_phrases": [],
            "missing_pressure_seeds": [],
            "unknown_axis_count": 0,
            "notes": [],
        },
    }
    base.update(overrides)
    return base


def test_cli_help_runs():
    rc = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0


def test_cli_validates_deployed_skeleton_output():
    """deployed docs/portfolio/demo/skeleton_output.json은 Phase 3 ready여야."""
    if not DEPLOYED.exists():
        import pytest
        pytest.skip("deployed skeleton_output.json missing")
    rc = subprocess.run(
        [sys.executable, str(SCRIPT), str(DEPLOYED)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0, (
        f"deployed skeleton failed Phase 3 gate. stdout:\n{rc.stdout}\n"
        f"stderr:\n{rc.stderr}"
    )
    assert "PASS" in rc.stdout


def test_cli_emits_json_mode(tmp_path):
    p = tmp_path / "ok.json"
    p.write_text(json.dumps(_make_minimal_skeleton()), encoding="utf-8")
    rc = subprocess.run(
        [sys.executable, str(SCRIPT), str(p), "--json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0, rc.stderr
    d = json.loads(rc.stdout)
    assert d["ready"] is True
    assert d["error_count"] == 0
    assert d["seed_count"] == 1
    assert d["flow_present"] is True


def test_cli_fails_on_main_role_placeholder(tmp_path):
    bad = _make_minimal_skeleton()
    bad["seeds"][0]["main_role"] = "main"   # placeholder
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(bad), encoding="utf-8")
    rc = subprocess.run(
        [sys.executable, str(SCRIPT), str(p)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 1
    assert "main_role placeholder" in rc.stdout


def test_cli_fails_on_missing_flow(tmp_path):
    bad = _make_minimal_skeleton(flow=None)
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(bad), encoding="utf-8")
    rc = subprocess.run(
        [sys.executable, str(SCRIPT), str(p)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 1
    assert "flow is None" in rc.stdout


def test_cli_lenient_passes_unknown_axis(tmp_path):
    """unknown axis는 strict fail / lenient pass."""
    bad = _make_minimal_skeleton()
    bad["seeds"][0]["conflict_axis_id"] = "unknown"
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(bad), encoding="utf-8")

    rc_strict = subprocess.run(
        [sys.executable, str(SCRIPT), str(p)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc_strict.returncode == 1
    assert "unknown axis" in rc_strict.stdout

    rc_lenient = subprocess.run(
        [sys.executable, str(SCRIPT), str(p), "--lenient"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc_lenient.returncode == 0


def test_cli_exit_2_on_missing_file(tmp_path):
    rc = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path / "does_not_exist.json")],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 2


def test_cli_exit_2_on_malformed_json(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("not valid json {{{", encoding="utf-8")
    rc = subprocess.run(
        [sys.executable, str(SCRIPT), str(p)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 2
