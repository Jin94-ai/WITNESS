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

    def test_full_file_path(self, tmp_path):
        """chapter별 파일 대신 전체 파일 (john.json 형식)로도 로드."""
        # scripture.py _BOOK_MAP: "요" → "john"
        full_file = tmp_path / "john.json"
        import json
        full_file.write_text(
            json.dumps({
                "verses": [
                    {"chapter": 3, "verse": 16, "text": "하나님이 세상을 이처럼 사랑하사"},
                ]
            }),
            encoding="utf-8",
        )
        text = load_scripture("요 3:16", tmp_path)
        assert "하나님이" in text

    def test_default_scripture_dir(self):
        """scripture_dir 미지정 → 기본 경로에서 로드."""
        # 기본 경로 content/shared/scripture가 존재. 실제 존재하는 절 사용
        # 존재하지 않으면 ValueError → 테스트 skip
        try:
            text = load_scripture("요 21:15")
            assert isinstance(text, str)
        except (ValueError, FileNotFoundError):
            import pytest as _pytest
            _pytest.skip("default scripture path not present in test env")

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
