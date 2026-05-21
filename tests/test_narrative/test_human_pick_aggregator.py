"""Tests for Stage E Human Pick aggregator."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load():
    spec = importlib.util.spec_from_file_location(
        "aggregate_human_pick",
        ROOT / "scripts" / "narrative" / "aggregate_human_pick.py",
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["aggregate_human_pick"] = mod
    spec.loader.exec_module(mod)
    return mod


agg = _load()


def _reviewer(rid: str, top_pick: str, scores: dict[str, int],
              q6: dict[str, str] | None = None,
              media: dict[str, str] | None = None) -> dict:
    q6 = q6 or {}
    media = media or {}
    return {
        "id": rid,
        "responses": {
            cid: {
                "q1": scores.get(cid),
                "q4": "",
                "q5": "",
                "q6": q6.get(cid, ""),
                "q7": media.get(cid),
            }
            for cid in scores
        },
        "q2_top_pick": top_pick,
        "q3_pick_reason": "",
    }


def test_three_reviewers_all_pick_s01_passes():
    payload = {
        "_meta": {"anchor_id": "test"},
        "reviewers": [
            _reviewer("R1", "S01", {"S01": 5, "S02": 3, "S03": 2, "S04": 3},
                      media={"S01": "film"}),
            _reviewer("R2", "S01", {"S01": 4, "S02": 3, "S03": 3, "S04": 2},
                      media={"S01": "novel"}),
            _reviewer("R3", "S01", {"S01": 5, "S02": 2, "S03": 3, "S04": 3},
                      media={"S01": "game"}),
        ],
    }
    result = agg.aggregate(payload)
    assert result["candidates"]["S01"]["overall_pass"] is True
    assert result["candidates"]["S01"]["selection_rate"] == 1.0
    assert result["candidates"]["S02"]["overall_pass"] is False  # avg 2.67 < 3.5


def test_low_q1_fails_pass_criterion():
    payload = {
        "_meta": {"anchor_id": "test"},
        "reviewers": [
            _reviewer("R1", "S02", {"S01": 2}),
            _reviewer("R2", "S02", {"S01": 2}),
            _reviewer("R3", "S02", {"S01": 2}),
        ],
    }
    result = agg.aggregate(payload)
    assert result["candidates"]["S01"]["passes_q1"] is False
    assert result["candidates"]["S01"]["overall_pass"] is False


def test_low_pick_rate_fails():
    payload = {
        "_meta": {"anchor_id": "test"},
        "reviewers": [
            _reviewer("R1", "S02", {"S01": 5}),
            _reviewer("R2", "S03", {"S01": 5}),
            _reviewer("R3", "S04", {"S01": 5}),
        ],
    }
    result = agg.aggregate(payload)
    assert result["candidates"]["S01"]["passes_q1"] is True
    assert result["candidates"]["S01"]["passes_pick_rate"] is False
    assert result["candidates"]["S01"]["overall_pass"] is False


def test_repeated_q6_complaint_fails_pass():
    payload = {
        "_meta": {"anchor_id": "test"},
        "reviewers": [
            _reviewer("R1", "S01", {"S01": 5},
                      q6={"S01": "feels too generic and templated"}),
            _reviewer("R2", "S01", {"S01": 5},
                      q6={"S01": "the premise feels generic"}),
            _reviewer("R3", "S01", {"S01": 5},
                      q6={"S01": "way too generic"}),
        ],
    }
    result = agg.aggregate(payload)
    # 3 reviewers all use word "generic" — should be flagged
    assert "generic" in result["candidates"]["S01"]["repeat_complaints"]
    assert result["candidates"]["S01"]["passes_complaint_check"] is False
    assert result["candidates"]["S01"]["overall_pass"] is False


def test_single_reviewer_does_not_trigger_complaint_repeat():
    payload = {
        "_meta": {"anchor_id": "test"},
        "reviewers": [
            _reviewer("R1", "S01", {"S01": 5},
                      q6={"S01": "feels too generic"}),
        ],
    }
    result = agg.aggregate(payload)
    assert result["candidates"]["S01"]["repeat_complaints"] == []
    # Pass rate alone fails (1/1 = 100% pick, q1 5/5 ok, no complaints) — should pass
    assert result["candidates"]["S01"]["overall_pass"] is True


def test_medium_distribution_aggregated():
    payload = {
        "_meta": {"anchor_id": "test"},
        "reviewers": [
            _reviewer("R1", "S01", {"S01": 5}, media={"S01": "film"}),
            _reviewer("R2", "S01", {"S01": 4}, media={"S01": "film"}),
            _reviewer("R3", "S01", {"S01": 5}, media={"S01": "novel"}),
        ],
    }
    result = agg.aggregate(payload)
    dist = result["candidates"]["S01"]["medium_distribution"]
    assert dist == {"film": 2, "novel": 1}


def test_template_only_responses_filtered_in_main(tmp_path):
    """If reviewers have null q1 across the board (template only), main()
    must error out gracefully rather than aggregate empty data."""
    template_path = tmp_path / "responses.json"
    template_path.write_text(json.dumps({
        "_meta": {"anchor_id": "test"},
        "reviewers": [
            {
                "id": "R1",
                "responses": {
                    "S01": {"q1": None, "q4": "", "q5": "", "q6": "", "q7": None},
                },
                "q2_top_pick": None, "q3_pick_reason": "",
            },
        ],
    }), encoding="utf-8")
    out_md = tmp_path / "out.md"
    out_json = tmp_path / "out.json"
    rc = agg.main(str(template_path), str(out_md), str(out_json))
    assert rc == 1


def test_renders_markdown_summary_table():
    payload = {
        "_meta": {"anchor_id": "test_anchor"},
        "reviewers": [
            _reviewer("R1", "S01", {"S01": 5, "S02": 3}),
            _reviewer("R2", "S01", {"S01": 4, "S02": 2}),
            _reviewer("R3", "S01", {"S01": 5, "S02": 3}),
        ],
    }
    result = agg.aggregate(payload)
    md = agg.render_md(result, payload)
    assert "Human Pick Test Result" in md
    assert "test_anchor" in md
    assert "S01" in md and "S02" in md
    # Decision section
    assert "Decision" in md


def test_template_file_exists():
    template_path = ROOT / "data" / "narrative" / "human_pick_responses_template.json"
    assert template_path.exists()
    payload = json.loads(template_path.read_text(encoding="utf-8"))
    assert payload["_meta"]["schema_version"] == "human_pick_responses_v1"
    # Three R-stub reviewers
    assert len(payload["reviewers"]) >= 3
    # All q1 are null in template
    for r in payload["reviewers"]:
        for cid, resp in r["responses"].items():
            assert resp["q1"] is None, f"template should have null q1, got {resp['q1']}"


def test_test_pack_lists_all_four_candidates():
    pack_path = ROOT / "docs" / "portfolio" / "HUMAN_PICK_TEST_PACK.md"
    assert pack_path.exists()
    text = pack_path.read_text(encoding="utf-8")
    for cid in ("S01", "S02", "S03", "S04"):
        assert cid in text, f"{cid} missing from HUMAN_PICK_TEST_PACK.md"
    # Required sections
    assert "응답 양식" in text
    assert "Q1" in text and "Q2" in text and "Q7" in text
