"""Smoke tests for Korean renderer (render_story_ko.py)."""

import pytest
from scripts.story.build_narrative_ir import process as build_ir
from scripts.story.render_story_ko import render_summary, render_narrative, process


class TestRenderSmoke:
    """No exceptions, returns string, basic invariants."""

    @pytest.mark.parametrize("probe_id", ["P1", "P6", "P9", "P12"])
    def test_baseline_render_no_error(self, probe_id):
        ir = build_ir(probe_id)
        summary = render_summary(ir)
        narrative = render_narrative(ir)
        assert isinstance(summary, str) and len(summary) > 0
        assert isinstance(narrative, str) and len(narrative) > 0

    @pytest.mark.parametrize("probe_id", ["P_PV_09", "P_S2_05", "P_S2_08"])
    def test_branch_c_render_no_error(self, probe_id):
        ir = build_ir(probe_id)
        summary = render_summary(ir)
        narrative = render_narrative(ir)
        assert isinstance(summary, str) and len(summary) > 0
        assert isinstance(narrative, str) and len(narrative) > 0


class TestForbiddenPhrases:
    """Spec §6: raw IDs, numbers, meta phrases must NOT appear."""

    @pytest.mark.parametrize("probe_id", ["P6", "P9", "P_PV_09", "P_S2_08"])
    def test_no_raw_probe_id(self, probe_id):
        s, n = process(probe_id)
        # probe_id 자체가 출력에 누출되면 안 됨
        assert probe_id not in s
        assert probe_id not in n

    @pytest.mark.parametrize("probe_id", ["P6", "P9"])
    def test_no_meta_phrases(self, probe_id):
        s, n = process(probe_id)
        forbidden = ["trajectory", "probe", "annotated", "이 시뮬레이션", "데이터에 따르면"]
        for phrase in forbidden:
            assert phrase not in s, f"summary contains '{phrase}'"
            assert phrase not in n, f"narrative contains '{phrase}'"

    @pytest.mark.parametrize("probe_id", ["P6", "P9", "P_PV_09"])
    def test_no_raw_numbers(self, probe_id):
        s, n = process(probe_id)
        # peak X.YY, t=N, agent_NN 같은 raw 수치 0건
        import re
        bad_pattern = re.compile(r"(peak|final|t=)\s*[\d.]+", re.IGNORECASE)
        assert not bad_pattern.search(s), f"summary leaks raw number"
        assert not bad_pattern.search(n), f"narrative leaks raw number"


class TestOutcomeToneDifferentiation:
    """C2: recovery vs saturation vs mixed → tonally different."""

    def test_recovery_tone_keywords(self):
        # P4 = sacred RECOVERY
        ir = build_ir("P4")
        narrative = render_narrative(ir)
        # Recovery 결말 톤: "다시 일어섰다 / 가라앉았다 / 풀렸다 / 되찾았다" 중 하나 이상
        recovery_words = ["다시", "가라앉", "풀렸", "되찾", "가벼워"]
        assert any(w in narrative for w in recovery_words), \
            f"P4 narrative missing recovery tone: {narrative[-200:]}"

    def test_saturation_tone_keywords(self):
        # P9 = scarcity SATURATION
        ir = build_ir("P9")
        narrative = render_narrative(ir)
        # Saturation 결말 톤
        sat_words = ["굳", "머물렀다", "멈춘", "갇혔", "비켜"]
        assert any(w in narrative for w in sat_words), \
            f"P9 narrative missing saturation tone: {narrative[-200:]}"

    def test_mixed_tone_keywords(self):
        # P6 = MIXED
        ir = build_ir("P6")
        narrative = render_narrative(ir)
        # MIXED 결말 톤
        mixed_words = ["갈라", "한쪽", "다른", "결로 굳", "다른 모양"]
        assert any(w in narrative for w in mixed_words), \
            f"P6 narrative missing mixed tone: {narrative[-200:]}"


class TestFiveStageStructure:
    """Narrative output has 5 paragraphs (5-stage structure)."""

    @pytest.mark.parametrize("probe_id", ["P6", "P9", "P_PV_01"])
    def test_narrative_has_multiple_paragraphs(self, probe_id):
        ir = build_ir(probe_id)
        narrative = render_narrative(ir)
        paragraphs = [p for p in narrative.split("\n\n") if p.strip()]
        assert len(paragraphs) >= 4, f"{probe_id} has only {len(paragraphs)} paragraphs"


class TestVariationByProbeId:
    """C-3: same-IR probes (e.g. P4 vs P5) produce different text."""

    def test_p4_p5_differ(self):
        # P4 and P5 are both sacred RECOVERY with identical cohort structure
        # → same IR, should differ via probe_id hash
        s4, _ = process("P4")
        s5, _ = process("P5")
        # Summaries 100% 동일하면 안 됨 (probe-hash variation 작동 검증)
        assert s4 != s5, "P4 and P5 produced identical text — variation broken"
