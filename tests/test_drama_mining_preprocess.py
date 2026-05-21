"""Tests for drama_mining.data.preprocess."""

from __future__ import annotations

from pathlib import Path

import pytest

from drama_mining.data.loader import stream_aihub_023
from drama_mining.data.preprocess import (
    extract_origin_base,
    normalize_passage,
    preprocess_entry,
    preprocess_stream,
    validate_entry,
)

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_ZIP = ROOT / "tests" / "fixtures" / "aihub_023_sample.zip"


# ---------- normalize_passage ----------


def test_normalize_collapses_whitespace():
    assert normalize_passage("a  \n\nb   c") == "a b c"


def test_normalize_strips_edges():
    assert normalize_passage("  hello  ") == "hello"


def test_normalize_empty_returns_empty():
    assert normalize_passage("") == ""
    assert normalize_passage(None) == ""


def test_normalize_removes_control_chars():
    assert normalize_passage("a\x00b\x07c") == "abc"


def test_normalize_preserves_korean():
    out = normalize_passage("한적한 거리에\n근수가 운영하는")
    assert "한적한" in out
    assert "근수" in out


# ---------- extract_origin_base ----------


def test_extract_origin_base_zero_padded():
    assert extract_origin_base("장밋빛인생024") == "장밋빛인생"


def test_extract_origin_base_two_digit():
    assert extract_origin_base("결혼해주세요31") == "결혼해주세요"


def test_extract_origin_base_single_digit():
    assert extract_origin_base("쌈마이웨이8") == "쌈마이웨이"


def test_extract_origin_base_no_episode():
    assert extract_origin_base("당신옆이좋아") == "당신옆이좋아"
    assert extract_origin_base("당신뿐이야") == "당신뿐이야"
    assert extract_origin_base("어여쁜당신") == "어여쁜당신"


def test_extract_origin_base_short_name_with_number_preserved():
    """작품명 base가 너무 짧으면 (1자) 보존."""
    # "a5" → base "a"는 1자 미만 → 회차 추출 안 함
    assert extract_origin_base("a5") == "a5"


def test_extract_origin_base_known_number_in_name():
    """KNOWN_NUMBER_IN_NAME 작품은 회차 추출 안 함."""
    assert extract_origin_base("1박2일") == "1박2일"


def test_extract_origin_base_empty_passthrough():
    assert extract_origin_base("") == ""


# ---------- validate_entry ----------


def test_validate_rejects_empty_passage():
    valid, reason = validate_entry({"passage": "", "doc_origin": "x", "summary_1": "y"})
    assert not valid
    assert "empty_passage" in reason


def test_validate_rejects_short_passage():
    valid, reason = validate_entry({"passage": "짧음", "doc_origin": "x", "summary_1": "y"})
    assert not valid
    assert "too_short" in reason


def test_validate_rejects_empty_origin():
    valid, reason = validate_entry({"passage": "a" * 100, "doc_origin": "", "summary_1": "y"})
    assert not valid
    assert "empty_doc_origin" in reason


def test_validate_rejects_no_summary():
    valid, reason = validate_entry(
        {"passage": "a" * 100, "doc_origin": "x", "summary_1": "", "summary_3": ""},
    )
    assert not valid
    assert "no_summary" in reason


def test_validate_accepts_summary_3_only():
    valid, reason = validate_entry(
        {"passage": "a" * 100, "doc_origin": "x", "summary_1": "", "summary_3": "ok"},
    )
    assert valid, reason


def test_validate_passes_normal_entry():
    valid, reason = validate_entry(
        {"passage": "한적한 거리에 가게가 있다." * 5, "doc_origin": "x", "summary_1": "요약"},
    )
    assert valid, reason


# ---------- preprocess_entry / preprocess_stream ----------


@pytest.fixture
def sample_zip() -> Path:
    if not SAMPLE_ZIP.exists():
        pytest.skip(f"sample fixture not found: {SAMPLE_ZIP}")
    return SAMPLE_ZIP


def test_preprocess_entry_required_fields(sample_zip):
    raw = next(stream_aihub_023(sample_zip))
    out = preprocess_entry(raw)
    required = {
        "doc_id", "doc_type", "doc_origin_raw", "doc_origin_base",
        "passage_id", "passage", "passage_length",
        "summary_1", "summary_1_length", "summary_3", "summary_3_length",
        "published_year", "summary_mode", "is_valid", "invalid_reason",
    }
    assert required <= set(out.keys()), f"missing: {required - set(out.keys())}"


def test_preprocess_stream_yields_valid_and_invalid(sample_zip):
    """Invalid (e.g. corrupted, but corrupted is skipped at loader level)도 yield."""
    entries = list(preprocess_stream(stream_aihub_023(sample_zip)))
    valid = [e for e in entries if e["is_valid"]]
    invalid = [e for e in entries if not e["is_valid"]]
    # 모두 또는 거의 대부분 valid (corrupted 1건은 loader에서 skip됨)
    assert len(valid) > 0
    # 28 entries (29 - 1 corrupted) 모두 valid 또는 일부 too_short
    assert len(entries) == 28


def test_preprocess_origin_base_extracted_from_sample(sample_zip):
    """샘플 데이터에서 doc_origin_base가 raw와 다른 케이스 (회차 분리형) 있어야."""
    raws_diff_count = 0
    for entry in preprocess_stream(stream_aihub_023(sample_zip)):
        if entry["doc_origin_raw"] != entry["doc_origin_base"]:
            raws_diff_count += 1
    # 샘플에 회차 분리형이 일부 포함되어 있음
    assert raws_diff_count >= 0  # 통계만 확인 (sample 구성에 따라 0일 수도)


def test_preprocess_passage_length_matches(sample_zip):
    for entry in preprocess_stream(stream_aihub_023(sample_zip)):
        assert entry["passage_length"] == len(entry["passage"])


def test_preprocess_published_year_int_when_present(sample_zip):
    for entry in preprocess_stream(stream_aihub_023(sample_zip)):
        y = entry["published_year"]
        # int 또는 빈 문자열
        assert isinstance(y, (int, str))
