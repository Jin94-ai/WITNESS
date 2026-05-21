"""Tests for drama_mining.data.loader.

Per directive §2.5 + 보완 §1: pytest 기본 suite는 small fixture만 사용.
실제 TL1.zip 검증은 CLI (`python -m drama_mining.data.loader --count`).
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from drama_mining.data.loader import (
    KNOWN_CATEGORIES,
    count_by_category,
    count_by_category_and_mode,
    stream_aihub_023,
)

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_ZIP = ROOT / "tests" / "fixtures" / "aihub_023_sample.zip"


@pytest.fixture
def sample_zip() -> Path:
    if not SAMPLE_ZIP.exists():
        pytest.skip(f"sample fixture not found: {SAMPLE_ZIP}")
    return SAMPLE_ZIP


# ---------- stream_aihub_023 ----------


def test_stream_returns_iterator(sample_zip):
    it = stream_aihub_023(sample_zip)
    first = next(iter(it))
    assert isinstance(first, dict)


def test_stream_yields_required_fields(sample_zip):
    required = {
        "doc_id", "doc_type", "doc_origin", "passage_id", "passage",
        "summary_1", "summary_3", "published_year", "summary_mode",
    }
    n = 0
    for entry in stream_aihub_023(sample_zip):
        assert required <= set(entry.keys()), f"missing: {required - set(entry.keys())}"
        n += 1
    assert n > 0


def test_stream_filters_categories(sample_zip):
    entries = list(stream_aihub_023(sample_zip, categories=["fm_drama"]))
    assert entries, "fm_drama filter empty"
    assert all(e["doc_type"] == "fm_drama" for e in entries)
    # 다른 카테고리 entry는 안 나와야
    other = list(stream_aihub_023(sample_zip, categories=["fs_drama"]))
    assert all(e["doc_type"] == "fs_drama" for e in other)


def test_stream_skips_corrupted_json(sample_zip):
    """fixture에 corrupted entry 1건 (fm_drama/20per/SCRIPT-corrupted-...). skip되어야."""
    skipped: list[tuple[str, str]] = []
    entries = list(stream_aihub_023(
        sample_zip,
        categories=["fm_drama"],
        skip_logger=lambda reason, path: skipped.append((reason, path)),
    ))
    # fm_drama 11 - 1 corrupted = 10
    assert len(entries) == 10, f"expected 10 valid fm_drama, got {len(entries)}"
    assert len(skipped) == 1
    assert "corrupted" in skipped[0][1]


def test_stream_extracts_summary_mode(sample_zip):
    modes = {e["summary_mode"] for e in stream_aihub_023(sample_zip)}
    # fixture에 20per + 3sent 둘 다 있음
    assert "20per" in modes
    assert "3sent" in modes


def test_stream_raises_on_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        list(stream_aihub_023(tmp_path / "nope.zip"))


def test_stream_handles_utf8_korean(sample_zip):
    for e in stream_aihub_023(sample_zip, categories=["fm_drama"]):
        assert isinstance(e["passage"], str)
        # Korean (Hangul) syllables 포함 OK
        if e["passage"]:
            break
    else:
        pytest.fail("no passage with Korean characters found in fm_drama sample")


# ---------- count_by_category ----------


def test_count_by_category_returns_dict(sample_zip):
    counts = count_by_category(sample_zip)
    assert isinstance(counts, dict)
    assert all(isinstance(v, int) for v in counts.values())


def test_count_by_category_known_cats(sample_zip):
    counts = count_by_category(sample_zip)
    # corrupted 1건 제외하면 28 entries
    total = sum(counts.values())
    assert total == 28, f"expected 28 valid (29-1 corrupted), got {total}"
    # 6 카테고리 모두 fixture에 포함
    for cat in ("fm_drama", "fs_drama", "enter", "c_event", "history", "culture"):
        assert cat in counts, f"missing category: {cat}"


def test_count_by_category_and_mode(sample_zip):
    counts = count_by_category_and_mode(sample_zip)
    assert isinstance(counts, dict)
    # fm_drama/20per + fm_drama/3sent 둘 다 존재
    assert ("fm_drama", "20per") in counts
    assert ("fm_drama", "3sent") in counts


# ---------- known constants ----------


def test_known_categories_six():
    assert len(KNOWN_CATEGORIES) == 6
    assert "fm_drama" in KNOWN_CATEGORIES
    assert "fs_drama" in KNOWN_CATEGORIES
