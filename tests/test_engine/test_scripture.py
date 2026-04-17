"""Scripture 로더 테스트."""

from pathlib import Path

import pytest

from engine.rendering.scripture import clear_cache, load_scripture, parse_scripture_ref

SCRIPTURE_DIR = Path(__file__).resolve().parent.parent.parent / "content" / "shared" / "scripture"


class TestParseScriptureRef:
    def test_single_verse(self):
        book, ch, v_start, v_end = parse_scripture_ref("요 21:15")
        assert book == "요"
        assert ch == 21
        assert v_start == 15
        assert v_end is None

    def test_verse_range(self):
        book, ch, v_start, v_end = parse_scripture_ref("요 21:15-17")
        assert book == "요"
        assert ch == 21
        assert v_start == 15
        assert v_end == 17

    def test_invalid_format(self):
        with pytest.raises(ValueError):
            parse_scripture_ref("invalid")

    def test_missing_colon(self):
        with pytest.raises(ValueError):
            parse_scripture_ref("요 21")


class TestLoadScripture:
    def setup_method(self):
        clear_cache()

    def test_single_verse(self):
        """요 21:15 로드."""
        text = load_scripture("요 21:15", SCRIPTURE_DIR)
        assert "요한의 아들 시몬아" in text
        assert "사랑하느냐" in text

    def test_verse_range(self):
        """요 21:15-17 로드 (3절)."""
        text = load_scripture("요 21:15-17", SCRIPTURE_DIR)
        lines = text.strip().split("\n")
        assert len(lines) == 3

    def test_verse_17_exact(self):
        """요 21:17 -- '내 양을 먹이라' 포함."""
        text = load_scripture("요 21:17", SCRIPTURE_DIR)
        assert "내 양을 먹이라" in text

    def test_verse_7_peter_jumps(self):
        """요 21:7 -- 베드로가 바다로 뛰어내림."""
        text = load_scripture("요 21:7", SCRIPTURE_DIR)
        assert "바다로 뛰어 내리더라" in text

    def test_not_found(self):
        """존재하지 않는 절은 ValueError."""
        with pytest.raises(ValueError):
            load_scripture("요 21:99", SCRIPTURE_DIR)

    def test_cache_works(self):
        """두 번 로드해도 같은 결과."""
        text1 = load_scripture("요 21:15", SCRIPTURE_DIR)
        text2 = load_scripture("요 21:15", SCRIPTURE_DIR)
        assert text1 == text2

    def test_book_mapping(self):
        """'요한' 으로도 로드 가능."""
        text = load_scripture("요한 21:15", SCRIPTURE_DIR)
        assert "사랑하느냐" in text
