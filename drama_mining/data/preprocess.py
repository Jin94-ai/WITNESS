"""Normalize loader output into ML-ready entries.

Per docs/witness_dm_day2_directive.md §3.

기본 사용:
    from drama_mining.data.loader import stream_aihub_023
    from drama_mining.data.preprocess import preprocess_stream
    for entry in preprocess_stream(stream_aihub_023(zip_path)):
        if entry["is_valid"]:
            ...
"""

from __future__ import annotations

import re
import unicodedata
from typing import Iterator

# 회차 번호 추출 정규식 (directive §3.4)
# 작품명 끝의 1~3자리 숫자 (zero-padded 포함). 작품명 base는 최소 2자.
_ORIGIN_EPISODE_RE = re.compile(r"^(.+?)(\d{1,3})$")

# 작품명에 *내재된* 숫자 (회차 아님) — 학습 중 발견되면 추가
KNOWN_NUMBER_IN_NAME: set[str] = {
    "1박2일",
    "1번가의기적",
    "1번가의 기적",
    "전설의고향2",
    "전설의 고향 2",
}

# Passage 길이 최소 기준
DEFAULT_MIN_PASSAGE_LENGTH = 50

# Control character (0x00-0x1F except \t \n) 제거용
_CONTROL_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")
# 연속 공백 (개행 포함) → 단일 space
_WHITESPACE_RE = re.compile(r"\s+")


def normalize_passage(text: str) -> str:
    """Passage 텍스트 정규화.

    - Unicode NFC 정규화
    - 제어문자 제거
    - 연속 whitespace (개행 포함) → 단일 space
    - 앞뒤 strip
    """
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    text = _CONTROL_RE.sub("", text)
    text = _WHITESPACE_RE.sub(" ", text)
    return text.strip()


def extract_origin_base(doc_origin: str) -> str:
    """doc_origin에서 끝 회차 번호 제거.

    Examples:
        "장밋빛인생024" → "장밋빛인생"
        "결혼해주세요31" → "결혼해주세요"
        "당신옆이좋아" → "당신옆이좋아"  (회차 통합형)
        "복희누나004" → "복희누나"
        "1박2일" → "1박2일"  (KNOWN_NUMBER_IN_NAME)
    """
    if not doc_origin:
        return doc_origin
    if doc_origin in KNOWN_NUMBER_IN_NAME:
        return doc_origin
    m = _ORIGIN_EPISODE_RE.match(doc_origin)
    if m:
        base, _num = m.groups()
        # 작품명 base는 최소 2자 (한국어 1글자 + α) — 너무 짧으면 회차 아님
        if len(base) >= 2:
            return base
    return doc_origin


def validate_entry(
    entry: dict,
    *,
    min_passage_length: int = DEFAULT_MIN_PASSAGE_LENGTH,
    require_summary: bool = True,
) -> tuple[bool, str]:
    """학습 가능 entry인지 검증.

    Returns (is_valid, reason_if_invalid). reason은 invalid면 비어있지 않음.
    """
    passage = (entry.get("passage") or "").strip()
    if not passage:
        return False, "empty_passage"
    if len(passage) < min_passage_length:
        return False, f"passage_too_short_{len(passage)}"
    if not (entry.get("doc_origin") or "").strip():
        return False, "empty_doc_origin"
    if require_summary:
        s1 = (entry.get("summary_1") or "").strip()
        s3 = (entry.get("summary_3") or "").strip()
        if not s1 and not s3:
            return False, "no_summary"
    return True, ""


def _parse_year(year_raw) -> int | str:
    if year_raw in ("", None):
        return ""
    try:
        return int(str(year_raw)[:4])
    except (ValueError, TypeError):
        return str(year_raw)


def preprocess_entry(raw: dict, *, min_passage_length: int = DEFAULT_MIN_PASSAGE_LENGTH) -> dict:
    """단일 raw entry → preprocessed entry."""
    passage = normalize_passage(raw.get("passage", ""))
    summary_1 = normalize_passage(raw.get("summary_1", ""))
    summary_3 = normalize_passage(raw.get("summary_3", ""))
    doc_origin_raw = raw.get("doc_origin", "") or ""
    doc_origin_base = extract_origin_base(doc_origin_raw)

    out = {
        "doc_id": raw.get("doc_id", ""),
        "doc_type": raw.get("doc_type", ""),
        "doc_origin_raw": doc_origin_raw,
        "doc_origin_base": doc_origin_base,
        "passage_id": raw.get("passage_id", ""),
        "passage": passage,
        "passage_length": len(passage),
        "summary_1": summary_1,
        "summary_1_length": len(summary_1),
        "summary_3": summary_3,
        "summary_3_length": len(summary_3),
        "published_year": _parse_year(raw.get("published_year", "")),
        "summary_mode": raw.get("summary_mode", ""),
    }

    # validation uses the normalized values
    is_valid, reason = validate_entry(
        {
            "passage": passage,
            "doc_origin": doc_origin_base,
            "summary_1": summary_1,
            "summary_3": summary_3,
        },
        min_passage_length=min_passage_length,
    )
    out["is_valid"] = is_valid
    out["invalid_reason"] = reason
    return out


def preprocess_stream(
    raw_iter: Iterator[dict],
    *,
    min_passage_length: int = DEFAULT_MIN_PASSAGE_LENGTH,
) -> Iterator[dict]:
    """Stream of raw entries → stream of preprocessed entries.

    Invalid entries는 is_valid=False로 표시하고 그대로 yield (집계용).
    """
    for raw in raw_iter:
        yield preprocess_entry(raw, min_passage_length=min_passage_length)
