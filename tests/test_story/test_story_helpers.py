"""Story renderer helper tests (josa, role plural, variant_pick)."""

from scripts.story.render_story_ko import (
    _has_batchim,
    josa,
    role_ko,
    role_plural_ko,
    variant_pick,
)


class TestBatchim:
    def test_batchim_present(self):
        assert _has_batchim("학생") is True   # 생 has 받침
        assert _has_batchim("상인") is True   # 인 has 받침

    def test_no_batchim(self):
        assert _has_batchim("제자") is False  # 자 no 받침
        assert _has_batchim("노동자") is False

    def test_non_hangul(self):
        assert _has_batchim("") is False
        assert _has_batchim("abc") is False


class TestJosa:
    def test_eul_reul(self):
        assert josa("학생", "을", "를") == "을"
        assert josa("제자", "을", "를") == "를"

    def test_i_ga(self):
        assert josa("선생", "이", "가") == "이"
        assert josa("자리", "이", "가") == "가"


class TestRolePlural:
    def test_basic_role(self):
        assert role_plural_ko("merchant") == "상인들"

    def test_already_plural_no_double(self):
        # crowd_participant 매핑이 이미 "거리의 사람들"임
        result = role_plural_ko("crowd_participant")
        assert result == "거리의 사람들"
        assert "사람들들" not in result   # 핵심: 중복 방지

    def test_unknown_role_default(self):
        assert role_plural_ko("nonexistent_role") == "그 사람들"


class TestRoleKo:
    def test_known_role(self):
        assert role_ko("merchant") == "상인"
        assert role_ko("disciple_follower") == "제자"

    def test_unknown_role(self):
        assert role_ko("nonexistent") == "그 사람"


class TestVariantPick:
    def test_deterministic(self):
        pool = ["A", "B", "C"]
        # 같은 input → 같은 output
        assert variant_pick("P1", "slot1", pool) == variant_pick("P1", "slot1", pool)

    def test_different_probe_id_can_differ(self):
        pool = ["A", "B", "C", "D", "E"]
        # 5 pool variants에서 P1, P2, P3가 모두 같을 확률 매우 낮음
        results = {variant_pick(pid, "slot1", pool) for pid in ["P1", "P2", "P3", "P4", "P5"]}
        assert len(results) >= 2  # 최소 2개 다른 variant 선택

    def test_empty_pool_returns_empty(self):
        assert variant_pick("P1", "slot1", []) == ""
