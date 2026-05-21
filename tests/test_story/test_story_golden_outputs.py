"""Semantic golden tests — representative probes 4종.

Per WITNESS_PYTEST_IMPROVEMENT_PLAN.md §6.2:
- P6 (MIXED scarcity)
- P9 (SATURATION scarcity)
- P4 (RECOVERY sacred)
- P10 (RECOVERY accusation)

Per §7: 의미 단위 비교, 완전 일치 X.
"""

import pytest

from scripts.story.render_story_ko import process as render


class TestP9_SaturationScarcity:
    """P9 = SATURATION_DOMINATED, scarcity. 굳음 톤이 surface해야."""

    @classmethod
    def setup_class(cls):
        cls.summary, cls.narrative = render("P9")
        cls.text = cls.summary + "\n\n" + cls.narrative

    def test_scarcity_opening_present(self):
        scarcity_keywords = ["곡식", "곡물", "시장", "빈민가"]
        assert any(k in self.text for k in scarcity_keywords)

    def test_saturation_ending(self):
        sat_keywords = ["굳", "자리에 머물렀다", "비켜", "멈춘", "갇혔"]
        assert any(k in self.text for k in sat_keywords)

    def test_no_recovery_dominant_tone(self):
        # SATURATION에 "흔들림은 가라앉았다 / 어깨에서 무게가 풀렸다" 같은
        # recovery 핵심 결말 표현은 없어야 함 (P9 끝부분 검사)
        recovery_endings = ["흔들림은 가라앉았다", "어깨에서 무게가 풀렸다", "다시 숨을 쉬"]
        last_para = self.text.split("\n\n")[-2:]  # 마지막 2 문단
        last_text = "\n".join(last_para)
        assert not any(e in last_text for e in recovery_endings), \
            "P9 (SATURATION) leaked recovery tone in ending"


class TestP4_RecoverySacred:
    """P4 = RECOVERY_DOMINATED, sacred."""

    @classmethod
    def setup_class(cls):
        cls.summary, cls.narrative = render("P4")
        cls.text = cls.summary + "\n\n" + cls.narrative

    def test_sacred_opening_present(self):
        sacred_keywords = ["성전", "기도", "바깥뜰"]
        assert any(k in self.text for k in sacred_keywords)

    def test_recovery_ending(self):
        rec_keywords = ["다시", "가라앉", "풀렸", "되찾"]
        assert any(k in self.text for k in rec_keywords)


class TestP6_MixedScarcity:
    """P6 = MIXED, scarcity. cohort split 명시 surface."""

    @classmethod
    def setup_class(cls):
        cls.summary, cls.narrative = render("P6")
        cls.text = cls.summary + "\n\n" + cls.narrative

    def test_scarcity_opening(self):
        assert any(k in self.text for k in ["곡식", "곡물", "빈민가", "시장"])

    def test_split_keywords_present(self):
        # MIXED는 분기/갈림 묘사가 핵심
        split_keywords = ["갈라", "한쪽", "다른 자리", "두 자리", "결로 굳"]
        assert any(k in self.text for k in split_keywords)

    def test_location_semantic_in_text(self):
        # D-1: location semantic이 텍스트에 surface
        loc_keywords = ["곡물 창고", "빈민가", "시장"]
        assert any(k in self.text for k in loc_keywords)


class TestP10_RecoveryAccusation:
    """P10 = RECOVERY_DOMINATED, accusation."""

    @classmethod
    def setup_class(cls):
        cls.summary, cls.narrative = render("P10")
        cls.text = cls.summary + "\n\n" + cls.narrative

    def test_accusation_opening_or_targeting(self):
        # accusation 시나리오 표지: 손가락질, 가리켰다, 광장, 안마당
        acc_keywords = ["가리켰다", "손가락질", "광장", "관청", "비난"]
        assert any(k in self.text for k in acc_keywords)

    def test_recovery_ending(self):
        rec_keywords = ["다시", "가라앉", "풀렸", "회복"]
        assert any(k in self.text for k in rec_keywords)


class TestCrossOutcomeDifferentiation:
    """SATURATION vs RECOVERY ending should not collide."""

    def test_p9_p4_endings_differ(self):
        _, p9_narr = render("P9")  # SATURATION
        _, p4_narr = render("P4")  # RECOVERY
        # Last paragraphs must differ in tone
        p9_end = p9_narr.split("\n\n")[-1]
        p4_end = p4_narr.split("\n\n")[-1]
        assert p9_end != p4_end


class TestWorldSideAxesPresent:
    """C3: at least 2 of crowd/authority/suspicion/blame surfaced."""

    @pytest.mark.parametrize("probe_id", ["P6", "P9", "P_PV_01"])
    def test_world_side_minimum_two_axes(self, probe_id):
        _, narrative = render(probe_id)
        axes_keywords = {
            "blame": ["비난", "비난은"],
            "authority": ["권위", "시선"],
            "suspicion": ["의심"],
            "crowd": ["사람들의 눈"],
        }
        present = sum(
            1 for axis_kws in axes_keywords.values()
            if any(kw in narrative for kw in axis_kws)
        )
        assert present >= 2, f"{probe_id}: only {present} world-side axes surfaced"
