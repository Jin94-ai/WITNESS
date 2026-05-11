"""Test annotated probe parsing (extract_story_features.py)."""

import pytest
from scripts.story.extract_story_features import parse_probe, process_probe


# Representative annotated probe text snippets for unit testing
SAMPLE_PROBE = """=== PROBE P6_ANNOTATED (annotated supplement, v4) ===

[Annotated headline summary]
  Final summary:    MIXED
  Primary pressure: scarcity

  Cohort outcomes:
    [L2 cohort, 4 agents]:  recovery: peak~10.0 → final~3.2
    [L1 cohort, 4 agents]:  saturation: peak~10.0 → final~10.0 (stuck)
    [L3 cohort, 4 agents]:  saturation: peak~10.0 → final~10.0 (stuck)

  Pressure events + recovery actions:
    Accusations: 1 fired (targets: merchant)
    Recovery actions: 207 confessions, 142 forgiveness rumors emitted

  World-level dynamics:
    Crowd blame total:   peak 1.9 at t=127 → final 1.3
    Top blame target:    fisher_laborer (peak 1.29)
    Public suspicion:    peak 0.43 → final 0.31
    Authority vigilance: peak 0.25 → final 0.25

============================================================

Agents: A1=merchant, A2=family, A3=laborer, A4=laborer
Locations: L1, L2, L3
"""


class TestParseProbeBasicFields:
    def test_probe_id(self):
        f = parse_probe(SAMPLE_PROBE)
        assert f["probe_id"] == "P6"

    def test_final_summary(self):
        f = parse_probe(SAMPLE_PROBE)
        assert f["final_summary"] == "MIXED"

    def test_primary_pressure(self):
        f = parse_probe(SAMPLE_PROBE)
        assert f["primary_pressure"] == "scarcity"


class TestParseCohorts:
    def test_cohort_count(self):
        f = parse_probe(SAMPLE_PROBE)
        assert len(f["cohort_outcomes"]) == 3

    def test_cohort_arc_types(self):
        f = parse_probe(SAMPLE_PROBE)
        arcs = [c["arc"] for c in f["cohort_outcomes"]]
        assert arcs.count("recovery") == 1
        assert arcs.count("saturation") == 2

    def test_cohort_peak_final(self):
        f = parse_probe(SAMPLE_PROBE)
        recovery_cohort = next(c for c in f["cohort_outcomes"] if c["arc"] == "recovery")
        assert recovery_cohort["peak"] == 10.0
        assert recovery_cohort["final"] == 3.2


class TestParseEventCounts:
    def test_accusations(self):
        f = parse_probe(SAMPLE_PROBE)
        assert f["accusations_count"] == 1
        assert "merchant" in f["accusation_targets"]

    def test_confessions(self):
        f = parse_probe(SAMPLE_PROBE)
        assert f["confessions_count"] == 207

    def test_forgiveness(self):
        f = parse_probe(SAMPLE_PROBE)
        assert f["forgiveness_count"] == 142


class TestParseWorldDynamics:
    def test_crowd_blame(self):
        f = parse_probe(SAMPLE_PROBE)
        assert f["crowd_blame_peak"] == 1.9
        assert f["crowd_blame_final"] == 1.3

    def test_top_blame_target(self):
        f = parse_probe(SAMPLE_PROBE)
        assert f["top_blame_target_role"] == "fisher_laborer"
        assert f["top_blame_target_peak"] == 1.29

    def test_public_suspicion(self):
        f = parse_probe(SAMPLE_PROBE)
        assert f["public_suspicion_peak"] == 0.43

    def test_authority_vigilance(self):
        f = parse_probe(SAMPLE_PROBE)
        assert f["authority_vigilance_peak"] == 0.25


class TestParseRolesLocations:
    def test_roles_extracted(self):
        f = parse_probe(SAMPLE_PROBE)
        assert "merchant" in f["roles_present"]
        assert "laborer" in f["roles_present"]

    def test_locations_extracted(self):
        f = parse_probe(SAMPLE_PROBE)
        assert "L1" in f["locations_present"]
        assert len(f["locations_present"]) == 3


class TestRealProbeProcessing:
    """Integration: actual P{1-12} probes parse without error."""

    @pytest.mark.parametrize("probe_id", ["P1", "P6", "P9", "P12"])
    def test_baseline_probe_parses(self, probe_id):
        f = process_probe(probe_id)
        assert f["probe_id"] == probe_id
        assert f["final_summary"] in {
            "RECOVERY_DOMINATED", "SATURATION_DOMINATED",
            "MIXED", "PARTIAL", "LOW_ACTIVITY",
        }

    @pytest.mark.parametrize("probe_id", ["P_PV_09", "P_S2_08"])
    def test_branch_c_probe_parses(self, probe_id):
        f = process_probe(probe_id)
        assert f["probe_id"] == probe_id
