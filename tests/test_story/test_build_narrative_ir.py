"""Test Narrative IR builder (build_narrative_ir.py)."""

import pytest

from scripts.story.build_narrative_ir import (
    build_group_response,
    build_initial_tension,
    build_ir,
    build_pressure_arc,
    build_world_aftereffect,
)


def make_features(**overrides):
    """Build a minimal features dict for testing."""
    base = {
        "probe_id": "P_TEST",
        "final_summary": "RECOVERY_DOMINATED",
        "primary_pressure": "scarcity",
        "failure_mode": None,
        "cohort_outcomes": [
            {"location": "L1", "agents_count": 4, "arc": "recovery", "peak": 8.0, "final": 2.0}
        ],
        "accusations_count": 1,
        "accusation_targets": ["merchant"],
        "confessions_count": 50,
        "forgiveness_count": 30,
        "crowd_blame_peak": 1.0,
        "crowd_blame_final": 0.5,
        "public_suspicion_peak": 0.3,
        "public_suspicion_final": 0.2,
        "authority_vigilance_peak": 0.2,
        "authority_vigilance_final": 0.15,
        "top_blame_target_role": "fisher_laborer",
        "top_blame_target_peak": 0.8,
        "roles_present": ["merchant", "laborer"],
        "locations_present": ["L1"],
    }
    base.update(overrides)
    return base


class TestPressureArcBlameBand:
    """B-1: blame_band 4-tier classification."""

    def test_absent(self):
        arc = build_pressure_arc(make_features(crowd_blame_peak=0.3))
        assert arc["blame_band"] == "absent"

    def test_weak(self):
        arc = build_pressure_arc(make_features(crowd_blame_peak=1.0))
        assert arc["blame_band"] == "weak"

    def test_strong(self):
        arc = build_pressure_arc(make_features(crowd_blame_peak=2.0))
        assert arc["blame_band"] == "strong"

    def test_dominant(self):
        arc = build_pressure_arc(make_features(crowd_blame_peak=4.0))
        assert arc["blame_band"] == "dominant"


class TestPressureArcConfessionVolume:
    """B-2: scenario-normalized confession volume."""

    def test_scarcity_high_threshold(self):
        # scarcity uses 100/30 thresholds
        arc = build_pressure_arc(make_features(primary_pressure="scarcity", confessions_count=150))
        assert arc["confession_volume"] == "high"

    def test_sacred_low_threshold(self):
        # sacred uses 60/20 thresholds (sacred has fewer confessions in general)
        arc = build_pressure_arc(make_features(primary_pressure="sacred", confessions_count=70))
        assert arc["confession_volume"] == "high"  # Above sacred 'high' (60+)

    def test_low(self):
        arc = build_pressure_arc(make_features(confessions_count=10))
        assert arc["confession_volume"] == "low"


class TestPressureArcAuthorityPattern:
    """D-2: authority_pattern (decayed/loosened/sustained)."""

    def test_sustained(self):
        # peak 0.3 → final 0.28 (0.93 of peak, ≥0.85)
        arc = build_pressure_arc(make_features(
            authority_vigilance_peak=0.3, authority_vigilance_final=0.28,
        ))
        assert arc["authority_pattern"] == "sustained"

    def test_decayed(self):
        # peak 0.3 → final 0.1 (0.33 of peak, <0.5)
        arc = build_pressure_arc(make_features(
            authority_vigilance_peak=0.3, authority_vigilance_final=0.1,
        ))
        assert arc["authority_pattern"] == "decayed"

    def test_absent(self):
        arc = build_pressure_arc(make_features(authority_vigilance_peak=0.1))
        assert arc["authority_pattern"] == "absent"


class TestInitialTensionDispatch:
    """initial_tension chooses correct key by primary_pressure."""

    def test_scarcity(self):
        t = build_initial_tension(make_features(primary_pressure="scarcity"))
        assert t["key"] == "tension_scarcity_accusation"

    def test_accusation(self):
        t = build_initial_tension(make_features(primary_pressure="accusation"))
        assert t["key"] == "tension_direct_accusation"

    def test_sacred(self):
        t = build_initial_tension(make_features(primary_pressure="sacred"))
        assert t["key"] == "tension_sacred_event"

    def test_low_activity(self):
        t = build_initial_tension(make_features(
            final_summary="LOW_ACTIVITY", primary_pressure="none_clear",
        ))
        assert t["key"] == "tension_none"


class TestGroupResponseSplit:
    """split flag: True iff both recovery and saturation cohorts exist."""

    def test_split_true(self):
        cohorts = [
            {"location": "L1", "agents_count": 3, "arc": "recovery", "peak": 8, "final": 2},
            {"location": "L2", "agents_count": 3, "arc": "saturation", "peak": 10, "final": 9},
        ]
        resp = build_group_response(make_features(cohort_outcomes=cohorts))
        assert resp["split"] is True

    def test_split_false_all_recovery(self):
        cohorts = [
            {"location": "L1", "agents_count": 3, "arc": "recovery", "peak": 8, "final": 2},
            {"location": "L2", "agents_count": 3, "arc": "recovery", "peak": 7, "final": 1},
        ]
        resp = build_group_response(make_features(cohort_outcomes=cohorts))
        assert resp["split"] is False


class TestWorldAftereffect:
    def test_strong_residue(self):
        af = build_world_aftereffect(make_features(public_suspicion_final=0.5))
        assert af["suspicion_strong_residue"] is True

    def test_no_residue(self):
        af = build_world_aftereffect(make_features(public_suspicion_final=0.05))
        assert af["suspicion_residue"] is False


class TestBuildIRDominantMode:
    """final_summary → dominant_mode mapping."""

    @pytest.mark.parametrize("fs,expected", [
        ("RECOVERY_DOMINATED", "recovery_dominated"),
        ("SATURATION_DOMINATED", "saturation_dominated"),
        ("MIXED", "mixed"),
        ("PARTIAL", "partial"),
        ("LOW_ACTIVITY", "low_activity"),
    ])
    def test_dominant_mode(self, fs, expected):
        ir = build_ir(make_features(final_summary=fs))
        assert ir["dominant_mode"] == expected


class TestLocationSemanticMapping:
    """D-1: scenario-specific location names."""

    def test_scarcity_locations(self):
        cohorts = [
            {"location": "L1", "agents_count": 3, "arc": "recovery", "peak": 8, "final": 2},
            {"location": "L2", "agents_count": 3, "arc": "saturation", "peak": 10, "final": 9},
        ]
        f = make_features(primary_pressure="scarcity", cohort_outcomes=cohorts,
                          locations_present=["L1", "L2", "L3"])
        resp = build_group_response(f)
        # 첫 cohort = L1 in scarcity 매핑은 "곡물 창고"
        assert resp["cohorts_detail"][0]["location_name"] == "곡물 창고"
        # 두 번째 cohort = L2 in scarcity 매핑은 "빈민가"
        assert resp["cohorts_detail"][1]["location_name"] == "빈민가"
