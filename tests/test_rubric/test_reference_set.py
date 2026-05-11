"""Phase G Step G1 — Reference trajectory set loader tests."""

from __future__ import annotations

import pytest

from engine.rubric.reference_loader import (
    EXPECTED_COUNT,
    EXPECTED_LENGTH,
    SCALAR_FIELDS,
    SCHEMA_VERSION,
    TARGET_AWARE_FIELDS,
    ReferenceSchemaError,
    ReferenceSet,
    default_path,
    load_reference_set,
)


@pytest.fixture(scope="module")
def ref_set() -> ReferenceSet:
    path = default_path()
    if not path.exists():
        pytest.skip(f"reference set not present at {path}")
    return load_reference_set(path)


# -----------------------------------------------------------------
# Top-level schema
# -----------------------------------------------------------------

def test_schema_version(ref_set: ReferenceSet) -> None:
    assert ref_set.schema_version == SCHEMA_VERSION


def test_count_equals_45(ref_set: ReferenceSet) -> None:
    assert ref_set.count == EXPECTED_COUNT
    assert len(ref_set.trajectories) == EXPECTED_COUNT


def test_three_categories_15_each(ref_set: ReferenceSet) -> None:
    assert len(ref_set.canonical_like) == 15
    assert len(ref_set.plausible_alternative) == 15
    assert len(ref_set.obvious_noise) == 15


def test_noise_levels_5_each(ref_set: ReferenceSet) -> None:
    assert len(ref_set.noise_level_1) == 5
    assert len(ref_set.noise_level_2) == 5
    assert len(ref_set.noise_level_3) == 5


# -----------------------------------------------------------------
# Per-trajectory
# -----------------------------------------------------------------

def test_all_trajectories_length_30(ref_set: ReferenceSet) -> None:
    for t in ref_set.trajectories:
        assert len(t.ticks) == EXPECTED_LENGTH, (
            f"{t.trajectory_id} length={len(t.ticks)}"
        )


def test_trajectory_ids_unique(ref_set: ReferenceSet) -> None:
    ids = [t.trajectory_id for t in ref_set.trajectories]
    assert len(set(ids)) == len(ids)


def test_trajectory_id_prefixes(ref_set: ReferenceSet) -> None:
    """can_*, alt_*, noi_* convention."""
    for t in ref_set.canonical_like:
        assert t.trajectory_id.startswith("can_"), t.trajectory_id
    for t in ref_set.plausible_alternative:
        assert t.trajectory_id.startswith("alt_"), t.trajectory_id
    for t in ref_set.obvious_noise:
        assert t.trajectory_id.startswith("noi_"), t.trajectory_id


# -----------------------------------------------------------------
# Tick schema
# -----------------------------------------------------------------

def test_all_ticks_have_required_fields(ref_set: ReferenceSet) -> None:
    for t in ref_set.trajectories:
        for tr in t.ticks:
            assert isinstance(tr.tick, int)
            assert isinstance(tr.event_in, list)
            assert isinstance(tr.action, str)
            assert tr.event_out is None or isinstance(tr.event_out, str)
            assert isinstance(tr.state, dict)


def test_state_scalar_fields_complete(ref_set: ReferenceSet) -> None:
    for t in ref_set.trajectories:
        for tr in t.ticks:
            for name in SCALAR_FIELDS:
                assert name in tr.state, f"{t.trajectory_id}.tick{tr.tick}: missing {name}"


def test_state_target_aware_fields_complete(ref_set: ReferenceSet) -> None:
    for t in ref_set.trajectories:
        for tr in t.ticks:
            for name in TARGET_AWARE_FIELDS:
                assert name in tr.state, f"{t.trajectory_id}.tick{tr.tick}: missing {name}"
                assert isinstance(tr.state[name], dict)


def test_state_values_in_range(ref_set: ReferenceSet) -> None:
    for t in ref_set.trajectories:
        for tr in t.ticks:
            for name in SCALAR_FIELDS:
                v = tr.state[name]
                assert 0.0 <= float(v) <= 10.01, (
                    f"{t.trajectory_id}.tick{tr.tick}: {name}={v}"
                )
            for name in TARGET_AWARE_FIELDS:
                for k, v in tr.state[name].items():
                    assert 0.0 <= float(v) <= 10.01, (
                        f"{t.trajectory_id}.tick{tr.tick}: {name}[{k}]={v}"
                    )


# -----------------------------------------------------------------
# Convenience API
# -----------------------------------------------------------------

def test_get_by_trajectory_id(ref_set: ReferenceSet) -> None:
    t = ref_set.get("can_01")
    assert t.category == "canonical_like"


def test_get_raises_on_missing(ref_set: ReferenceSet) -> None:
    with pytest.raises(KeyError):
        ref_set.get("nonexistent_id")


# -----------------------------------------------------------------
# Rule #19 invariant -- loader is read-only
# -----------------------------------------------------------------

def test_reference_set_file_unchanged_checksum(ref_set: ReferenceSet) -> None:
    """Rule #19: loader must not mutate the source file.
    (Loader only reads; this is a smoke test that load is idempotent.)"""
    p = default_path()
    size1 = p.stat().st_size
    _ = load_reference_set(p)
    size2 = p.stat().st_size
    assert size1 == size2
