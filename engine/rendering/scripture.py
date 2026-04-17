"""정경 말씀 로더.

content/shared/scripture/의 JSON 파일에서 성경 본문을 로드한다.
scripture_ref (예: "요 21:15")로 원문을 정확히 반환.

절대 원칙: LLM이 이 텍스트에 관여하지 않는다. 원문 그대로만.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# 책 이름 매핑 (한글 약어 → 파일명)
_BOOK_MAP: dict[str, str] = {
    "마": "matthew",
    "마태": "matthew",
    "막": "mark",
    "마가": "mark",
    "눅": "luke",
    "누가": "luke",
    "요": "john",
    "요한": "john",
    "행": "acts",
    "사도행전": "acts",
}

# 캐시: 로드된 성경 데이터
_scripture_cache: dict[str, list[dict[str, Any]]] = {}


def _load_book(book_key: str, scripture_dir: Path) -> list[dict[str, Any]]:
    """성경 책 한 권의 데이터를 로드한다."""
    if book_key in _scripture_cache:
        return _scripture_cache[book_key]

    file_name = _BOOK_MAP.get(book_key, book_key)

    # chapter별 파일 (john_21.json) 또는 전체 파일 (john.json) 탐색
    # 우선 전체 파일
    full_path = scripture_dir / f"{file_name}.json"
    if full_path.exists():
        data = json.loads(full_path.read_text(encoding="utf-8"))
        verses: list[dict[str, Any]] = data.get("verses", [])
        _scripture_cache[book_key] = verses
        return verses

    # chapter별 파일들을 모아서 반환
    all_verses: list[dict[str, Any]] = []
    for p in sorted(scripture_dir.glob(f"{file_name}_*.json")):
        data = json.loads(p.read_text(encoding="utf-8"))
        chapter = data.get("chapter", 0)
        for v in data.get("verses", []):
            all_verses.append({**v, "chapter": chapter})
    _scripture_cache[book_key] = all_verses
    return all_verses


def parse_scripture_ref(ref: str) -> tuple[str, int, int, int | None]:
    """scripture_ref를 파싱한다.

    Args:
        ref: "요 21:15" 또는 "요 21:15-17" 형식

    Returns:
        (book_key, chapter, verse_start, verse_end)
        verse_end는 범위가 없으면 None.
    """
    ref = ref.strip()
    parts = ref.split()
    if len(parts) != 2:
        raise ValueError(f"Invalid scripture_ref format: '{ref}'. Expected '책 장:절'")

    book_key = parts[0].lower()
    chapter_verse = parts[1]

    if ":" not in chapter_verse:
        raise ValueError(f"Invalid chapter:verse format: '{chapter_verse}'")

    chapter_str, verse_str = chapter_verse.split(":", 1)
    chapter = int(chapter_str)

    if "-" in verse_str:
        start_str, end_str = verse_str.split("-", 1)
        return book_key, chapter, int(start_str), int(end_str)

    return book_key, chapter, int(verse_str), None


def load_scripture(
    ref: str,
    scripture_dir: Path | None = None,
) -> str:
    """scripture_ref로 성경 원문을 로드한다.

    Args:
        ref: "요 21:15" 또는 "요 21:15-17"
        scripture_dir: scripture JSON 파일이 있는 디렉토리.
                       None이면 기본 경로(content/shared/scripture/).

    Returns:
        성경 원문 텍스트. 여러 절이면 줄바꿈으로 연결.

    Raises:
        ValueError: ref 형식이 올바르지 않거나, 해당 절을 찾을 수 없을 때.
    """
    if scripture_dir is None:
        scripture_dir = Path("content/shared/scripture")

    book_key, chapter, verse_start, verse_end = parse_scripture_ref(ref)
    verses = _load_book(book_key, scripture_dir)

    if verse_end is None:
        verse_end = verse_start

    # 해당 절 필터
    matching = []
    for v in verses:
        v_chapter = v.get("chapter", chapter)  # chapter 필드가 없으면 파일 기본값 사용
        v_num = v.get("verse", 0)
        if v_chapter == chapter and verse_start <= v_num <= verse_end:
            matching.append(v)

    if not matching:
        raise ValueError(
            f"Scripture not found: {ref} "
            f"(book={book_key}, ch={chapter}, vv={verse_start}-{verse_end})"
        )

    # 절 번호순 정렬 후 텍스트 연결
    matching.sort(key=lambda v: v.get("verse", 0))
    return "\n".join(v.get("text", "") for v in matching)


def clear_cache() -> None:
    """캐시를 비운다."""
    _scripture_cache.clear()
