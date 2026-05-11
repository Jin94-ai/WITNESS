"""Tests for cross-seed pattern aggregator (Phase E)."""
from __future__ import annotations

from engine.observer.cross_seed_pattern import (
    CrossSeedPattern,
    SeedRecord,
    _classify_robustness,
    aggregate_character_patterns,
    aggregate_conflict_patterns,
    build_cross_seed_report,
)


def _candidate(cid: str, conflict: str, mains: list[str]) -> dict:
    return {
        "story_candidate_id": cid,
        "core_conflict": conflict,
        "main_characters": mains,
    }


def _seed(s: int, *cands: dict) -> SeedRecord:
    return SeedRecord(seed=s, run_label=f"test_seed{s}",
                       candidates=list(cands))


# ============ Robustness classification ============

def test_classify_robustness_thresholds():
    assert _classify_robustness(5, 5) == "robust"
    assert _classify_robustness(4, 5) == "robust"   # 80%
    assert _classify_robustness(2, 5) == "moderate"  # 40%
    assert _classify_robustness(1, 5) == "anomaly"
    assert _classify_robustness(0, 0) == "anomaly"


# ============ Conflict aggregation ============

def test_aggregate_conflict_basic():
    seeds = [
        _seed(0, _candidate("S01", "loyalty_vs_survival", ["Peter"])),
        _seed(1, _candidate("S01", "loyalty_vs_survival", ["Peter"])),
        _seed(2, _candidate("S01", "loyalty_vs_survival", ["Peter"])),
        _seed(3, _candidate("S01", "loyalty_vs_survival", ["Peter"])),
        _seed(4, _candidate("S01", "uncertainty_vs_commitment", ["Andrew"])),
    ]
    patterns = aggregate_conflict_patterns(seeds)
    by_value = {p.pattern_value: p for p in patterns}
    assert by_value["loyalty_vs_survival"].seed_count == 4
    assert by_value["loyalty_vs_survival"].robustness == "robust"
    assert by_value["uncertainty_vs_commitment"].seed_count == 1
    assert by_value["uncertainty_vs_commitment"].robustness == "anomaly"


def test_aggregate_conflict_dedup_within_seed():
    """A conflict that appears in multiple candidates of the same seed
    counts once for that seed (frequency is *seed coverage*, not raw count)."""
    seeds = [
        _seed(0,
              _candidate("S01", "loyalty_vs_survival", ["Peter"]),
              _candidate("S02", "loyalty_vs_survival", ["John"])),
        _seed(1, _candidate("S01", "loyalty_vs_survival", ["Peter"])),
    ]
    patterns = aggregate_conflict_patterns(seeds)
    p = patterns[0]
    assert p.seed_count == 2  # NOT 3 (despite 3 occurrences total)
    # both candidate IDs preserved
    assert len(p.candidate_ids) == 3


# ============ Character aggregation ============

def test_aggregate_character_recurrence():
    seeds = [
        _seed(0, _candidate("S01", "x", ["Peter", "John"])),
        _seed(1, _candidate("S01", "x", ["Peter"])),
        _seed(2, _candidate("S01", "x", ["John"])),
    ]
    patterns = aggregate_character_patterns(seeds)
    by_value = {p.pattern_value: p for p in patterns}
    assert by_value["Peter"].seed_count == 2
    assert by_value["John"].seed_count == 2


# ============ Report ============

def test_build_cross_seed_report_summary():
    seeds = [
        _seed(0, _candidate("S01", "loyalty_vs_survival", ["Peter"])),
        _seed(1, _candidate("S01", "loyalty_vs_survival", ["Peter"])),
    ]
    rep = build_cross_seed_report(seeds, anchor_id="test_anchor")
    d = rep.to_dict()
    assert d["anchor_id"] == "test_anchor"
    assert d["seeds"] == [0, 1]
    assert d["candidate_counts"] == {"0": 1, "1": 1}
    assert d["schema_version"] == "cross_seed_story_patterns_v1"
    assert d["summary"]["total_patterns"] >= 2  # 1 conflict + 1 character


def test_pattern_to_dict_includes_frequency():
    p = CrossSeedPattern(
        pattern_kind="conflict", pattern_value="x",
        seed_count=4, total_seeds=5, seeds_present=(0, 1, 2, 3),
        candidate_ids=("0:S01",), robustness="robust",
    )
    d = p.to_dict()
    assert d["frequency"] == 0.8
    assert d["robustness"] == "robust"


def test_aggregator_no_hardcoded_hero():
    from pathlib import Path
    src = (Path(__file__).resolve().parents[2]
           / "engine" / "observer" / "cross_seed_pattern.py").read_text(encoding="utf-8")
    for forbidden in ("peter", "Peter", "베드로", "vangogh", "VanGogh", "talleyrand"):
        assert forbidden not in src, f"forbidden '{forbidden}' in cross_seed_pattern source"
