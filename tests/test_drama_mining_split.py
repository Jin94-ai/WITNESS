"""Leakage validation tests for WITNESS Drama Mining split.

Per directive §4 + 보완 §1: fixture sample zip 기반 검증.
실제 split (data/splits/v1/) 검증은 CLI + 수동.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import pytest

from drama_mining.data.loader import stream_aihub_023
from drama_mining.data.preprocess import preprocess_stream
from drama_mining.data.split import split_by_origin_base, write_split

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_ZIP = ROOT / "tests" / "fixtures" / "aihub_023_sample.zip"

# 실제 v1 split (선택적)
SPLITS_V1_DIR = ROOT / "data" / "splits" / "v1"


@pytest.fixture(scope="module")
def sample_entries() -> list[dict]:
    if not SAMPLE_ZIP.exists():
        pytest.skip(f"sample fixture not found: {SAMPLE_ZIP}")
    return list(preprocess_stream(stream_aihub_023(SAMPLE_ZIP)))


# ---------- core split behavior (fixture-based) ----------


def test_split_returns_4_tuple(sample_entries):
    train, val, test, meta = split_by_origin_base(sample_entries, seed=42)
    assert isinstance(train, list)
    assert isinstance(val, list)
    assert isinstance(test, list)
    assert isinstance(meta, dict)


def test_split_no_empty_partition(sample_entries):
    """샘플이 너무 작아 일부 split이 비어있을 수 있지만, train만큼은 비어있으면 안 됨."""
    train, val, test, _ = split_by_origin_base(sample_entries, seed=42)
    assert len(train) > 0, "train empty"


def test_split_filters_to_categories(sample_entries):
    train, val, test, _ = split_by_origin_base(
        sample_entries, seed=42, categories=("fm_drama", "fs_drama")
    )
    all_entries = train + val + test
    assert all_entries, "no entries"
    types = {e["doc_type"] for e in all_entries}
    assert types <= {"fm_drama", "fs_drama"}


def test_split_no_origin_overlap(sample_entries):
    """cycle 86 §3 핵심: doc_origin_base overlap = 0."""
    train, val, test, meta = split_by_origin_base(sample_entries, seed=42)
    train_origins = {e["doc_origin_base"] for e in train}
    val_origins = {e["doc_origin_base"] for e in val}
    test_origins = {e["doc_origin_base"] for e in test}
    assert train_origins.isdisjoint(val_origins), train_origins & val_origins
    assert train_origins.isdisjoint(test_origins), train_origins & test_origins
    assert val_origins.isdisjoint(test_origins), val_origins & test_origins
    # metadata도 같은 값
    lc = meta["leakage_check"]
    assert lc["origin_overlap_train_val"] == 0
    assert lc["origin_overlap_train_test"] == 0
    assert lc["origin_overlap_val_test"] == 0


def test_split_is_deterministic(sample_entries):
    """같은 seed 두 번 → 같은 결과 (passage_id 기준)."""
    a = split_by_origin_base(sample_entries, seed=42)
    b = split_by_origin_base(sample_entries, seed=42)
    a_ids = [tuple(e["passage_id"] for e in part) for part in a[:3]]
    b_ids = [tuple(e["passage_id"] for e in part) for part in b[:3]]
    assert a_ids == b_ids


def test_split_seed_changes_output(sample_entries):
    """다른 seed → 결과 다름 (작품 수 ≥ 3일 때 거의 항상)."""
    a = split_by_origin_base(sample_entries, seed=42)
    c = split_by_origin_base(sample_entries, seed=99)
    a_train_origins = {e["doc_origin_base"] for e in a[0]}
    c_train_origins = {e["doc_origin_base"] for e in c[0]}
    # 동일하지 않거나 (가능성 매우 높음) — 작품 수 적으면 같을 수도. 정도만 확인.
    # 작품 수 < 3이면 skip
    if len(a_train_origins | c_train_origins) < 3:
        pytest.skip("too few origins to test seed sensitivity")
    assert a_train_origins != c_train_origins


def test_split_metadata_schema(sample_entries):
    _, _, _, meta = split_by_origin_base(sample_entries, seed=42)
    assert meta["schema_version"] == "split_metadata_v1"
    for k in ("created_at_iso", "seed", "ratios", "categories", "totals",
              "class_distribution", "year_distribution", "leakage_check",
              "passage_length_avg"):
        assert k in meta, f"missing meta key: {k}"


def test_split_ratios_invalid_sum_raises(sample_entries):
    with pytest.raises(ValueError):
        split_by_origin_base(
            sample_entries, train_ratio=0.5, val_ratio=0.3, test_ratio=0.3,
        )


def test_split_write_creates_files(sample_entries, tmp_path):
    train, val, test, meta = split_by_origin_base(sample_entries, seed=42)
    write_split(tmp_path / "out", train, val, test, meta)
    out = tmp_path / "out"
    assert (out / "train_ids.json").exists()
    assert (out / "val_ids.json").exists()
    assert (out / "test_ids.json").exists()
    assert (out / "split_metadata.json").exists()

    # raw passage가 저장되지 않음 (cycle 86 §4 data_card 정책)
    train_ids = json.loads((out / "train_ids.json").read_text(encoding="utf-8"))
    assert isinstance(train_ids, list)
    assert all(isinstance(x, str) for x in train_ids)
    # train_ids의 각 항목이 dict가 아니어야 — passage 같은 raw 텍스트 X
    for x in train_ids:
        assert "passage" not in x.lower() or "passage_id" in x  # only passage_id allowed


# ---------- 실제 v1 split (선택 검증) ----------


def _doc_origin_base(origin: str) -> str:
    return re.sub(r"\d+$", "", origin).strip()


def _splits_v1_ready() -> bool:
    return all(
        (SPLITS_V1_DIR / fname).exists()
        for fname in ("train_ids.json", "val_ids.json", "test_ids.json", "split_metadata.json")
    )


def test_v1_split_metadata_leakage_zero():
    if not _splits_v1_ready():
        pytest.skip("data/splits/v1/ not generated yet (CLI 수동)")
    meta = json.loads((SPLITS_V1_DIR / "split_metadata.json").read_text(encoding="utf-8"))
    lc = meta["leakage_check"]
    assert lc["origin_overlap_train_val"] == 0
    assert lc["origin_overlap_train_test"] == 0
    assert lc["origin_overlap_val_test"] == 0


def test_v1_split_ratios_within_tolerance():
    if not _splits_v1_ready():
        pytest.skip("data/splits/v1/ not generated yet")
    meta = json.loads((SPLITS_V1_DIR / "split_metadata.json").read_text(encoding="utf-8"))
    t = meta["totals"]
    total = t["train_passages"] + t["val_passages"] + t["test_passages"]
    assert 0.60 <= t["train_passages"] / total <= 0.80, t
    assert 0.05 <= t["val_passages"] / total <= 0.25, t
    assert 0.05 <= t["test_passages"] / total <= 0.25, t


def test_v1_split_class_balance():
    """각 split에서 minority class ≥ 30%."""
    if not _splits_v1_ready():
        pytest.skip("data/splits/v1/ not generated yet")
    meta = json.loads((SPLITS_V1_DIR / "split_metadata.json").read_text(encoding="utf-8"))
    for split_name, dist in meta["class_distribution"].items():
        total = sum(dist.values())
        if total == 0:
            continue
        minority = min(dist.values()) / total
        assert minority >= 0.30, f"{split_name} minority {minority:.2%}: {dist}"
