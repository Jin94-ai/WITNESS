"""Test selector (scripts/story/selector.py) — J-Alpha + J-Beta query API."""

import pytest

from scripts.story.selector import (
    AnchorBundle,
    get_anchor_by_id,
    get_curated_anchors,
    get_top_arcs,
    get_variations,
    get_variations_by_anchor_id,
    pick_most_readable_anchor,
    query_anchors,
)


class TestCuratedAnchors:
    def test_curated_set_size_jbeta(self):
        # J-Alpha 3 + J-Beta 2 (scarcity_double, scarcity_triple) = 5
        anchors = get_curated_anchors()
        assert len(anchors) == 5

    def test_anchor_ids(self):
        anchors = get_curated_anchors()
        ids = {a.anchor_id for a in anchors}
        # J-Alpha
        assert "peter_scarcity_baseline" in ids
        assert "vangogh_sacred_baseline" in ids
        assert "peter_scarcity_high_density" in ids
        # J-Beta
        assert "peter_scarcity_double" in ids
        assert "peter_scarcity_triple" in ids

    def test_each_anchor_has_5_seeds(self):
        for a in get_curated_anchors():
            assert a.seed_count == 5


class TestGetVariations:
    def test_returns_5_seed_world_pairs(self):
        anchor = get_curated_anchors()[0]
        pairs = get_variations(anchor, max_seeds=5)
        assert len(pairs) == 5
        seeds = [p[0] for p in pairs]
        assert seeds == [0, 1, 2, 3, 4]

    def test_max_seeds_under_5(self):
        anchor = get_curated_anchors()[0]
        pairs = get_variations(anchor, max_seeds=3)
        assert len(pairs) == 3

    def test_each_world_is_microworld(self):
        from engine.world.micro_world import MicroWorld
        anchor = get_curated_anchors()[0]
        pairs = get_variations(anchor, max_seeds=2)
        for seed, world in pairs:
            assert isinstance(world, MicroWorld)


class TestPickMostReadableAnchor:
    def test_returns_anchor(self):
        anchor = pick_most_readable_anchor()
        assert isinstance(anchor, AnchorBundle)

    def test_picks_highest_diversity(self):
        # Peter scarcity expected_outcome_diversity=3 vs Van Gogh sacred=2
        anchor = pick_most_readable_anchor()
        assert anchor.anchor_id == "peter_scarcity_baseline"

    def test_explicit_anchor_list(self):
        custom = [
            AnchorBundle(anchor_id="a", scenario="x", seed_count=5,
                         builder=lambda s: None, expected_outcome_diversity=1),
            AnchorBundle(anchor_id="b", scenario="y", seed_count=5,
                         builder=lambda s: None, expected_outcome_diversity=4),
        ]
        anchor = pick_most_readable_anchor(custom)
        assert anchor.anchor_id == "b"


class TestAnchorBundleSemantics:
    def test_peter_anchor_scenario(self):
        anchors = get_curated_anchors()
        peter = next(a for a in anchors if a.anchor_id == "peter_scarcity_baseline")
        assert peter.scenario == "scarcity"

    def test_vangogh_anchor_scenario(self):
        anchors = get_curated_anchors()
        vg = next(a for a in anchors if a.anchor_id == "vangogh_sacred_baseline")
        assert vg.scenario == "sacred"


class TestQueryAPI:
    """J-Beta query API extension."""

    def test_get_anchor_by_id(self):
        anchor = get_anchor_by_id("peter_scarcity_baseline")
        assert anchor is not None
        assert anchor.scenario == "scarcity"

    def test_get_anchor_by_id_not_found(self):
        assert get_anchor_by_id("nonexistent") is None

    def test_get_variations_by_anchor_id(self):
        pairs = get_variations_by_anchor_id("peter_scarcity_baseline", max_seeds=2)
        assert len(pairs) == 2

    def test_get_variations_by_anchor_id_invalid(self):
        with pytest.raises(ValueError):
            get_variations_by_anchor_id("nonexistent")

    def test_query_by_scenario(self):
        scarcity_anchors = query_anchors(scenario="scarcity")
        # baseline + high_density + double + triple = 4 scarcity anchors
        assert len(scarcity_anchors) == 4

    def test_query_by_min_diversity(self):
        ready_anchors = query_anchors(min_diversity=3)
        # Only diversity≥3 = peter_scarcity_baseline + peter_scarcity_high_density
        assert len(ready_anchors) == 2

    def test_query_combined(self):
        ready_scarcity = query_anchors(scenario="scarcity", min_diversity=3)
        assert len(ready_scarcity) == 2  # excludes vangogh, double, triple

    def test_query_no_filter(self):
        all_anchors = query_anchors()
        assert len(all_anchors) == 5


class TestTopArcs:
    """J-Beta arc-type query."""

    def test_recovery_anchors(self):
        anchors = get_top_arcs("recovery")
        # sacred scenario only
        assert all(a.scenario == "sacred" for a in anchors)

    def test_saturation_anchors(self):
        anchors = get_top_arcs("saturation")
        # scarcity scenario
        assert all(a.scenario == "scarcity" for a in anchors)

    def test_low_activity_anchors(self):
        anchors = get_top_arcs("low_activity")
        # sacred only (LOW_ACTIVITY only via sacred clustered)
        assert all(a.scenario == "sacred" for a in anchors)

    def test_mixed_anchors_empty(self):
        # MIXED는 cell-specific, no scenario hint
        assert get_top_arcs("mixed") == []

    def test_unknown_arc_type(self):
        assert get_top_arcs("nonsense") == []
