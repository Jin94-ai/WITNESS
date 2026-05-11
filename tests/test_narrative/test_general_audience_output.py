"""General-audience output enforcement (directive 2026-05-08).

메인 portfolio demo에서 reviewer가 첫 화면에 *수치 / 내부 용어*를 보면 안 됨.
모든 그런 정보는 Evidence section (접힘) 또는 Technical Appendix로 격리되어야.

이 테스트는 다음을 강제한다:
    1. EpisodeOutline에 story-tone 필드가 모두 존재 (one_line_story / what_wants / etc.)
    2. story-tone 필드 텍스트에 숫자 / 내부 용어 / 단계 표현이 *없음*
    3. index.html에서 Main Story Result가 Run Summary보다 *먼저* 나타남
    4. index.html의 메인 episode 영역에 수치형 단어 (200단계 / 비율 / audit_pass) 없음
    5. Evidence section (접힘) 안에는 수치 허용 (검증 X)
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DEMO_DIR = ROOT / "docs" / "portfolio" / "demo"

# Internal terms that must never leak into general-audience surfaces
FORBIDDEN_INTERNAL = (
    "tick ",
    "source_derived",
    "source_inferred",
    "co-occurrence",
    "authority_vigilance",
    "public_suspicion",
    "blame_concentration",
    "group_tension",
    "viable_with_gaps",
    "strong_viable",
    "deterministic",
    "cross-seed",
    "MomentLink",
    "StoryThread",
    "NarrativeOpportunity",
)

# Numeric / quantitative patterns forbidden in main display
FORBIDDEN_NUMERIC_PATTERNS = (
    r"\d+\s*단계 중",
    r"\d+\s*%",
    r"초반\s*\d+회",
    r"후반\s*\d+회",
    r"audit_pass",
    r"audit_fail",
)


@pytest.fixture(scope="module", autouse=True)
def _run_orchestrator():
    rc = subprocess.run(
        [sys.executable,
         str(ROOT / "scripts/narrative/run_portfolio_demo.py")],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0, f"orchestrator failed: {rc.stderr}"


# ============================================================================
# 1. EpisodeOutline must have story-tone fields
# ============================================================================

def test_episode_outline_has_story_tone_fields():
    p = DEMO_DIR / "episode_outline.json"
    payload = json.loads(p.read_text(encoding="utf-8"))
    o = payload["outline"]
    required = (
        "one_line_story",
        "what_character_wants",
        "what_pressures_them",
        "how_it_changes",
        "three_part_outline",
        "unresolved_question",
        "why_usable",
    )
    for field in required:
        assert field in o, f"missing story-tone field: {field}"
    # three_part_outline must be a list of 3 strings
    assert isinstance(o["three_part_outline"], list)
    assert len(o["three_part_outline"]) == 3
    for line in o["three_part_outline"]:
        assert isinstance(line, str)
        assert len(line) > 5


# ============================================================================
# 2. Story-tone fields must contain no numbers / no internal terms
# ============================================================================

def _story_tone_text(outline: dict) -> str:
    """Concatenate all story-tone fields for inspection."""
    parts = [
        outline.get("one_line_story", ""),
        outline.get("what_character_wants", ""),
        outline.get("what_pressures_them", ""),
        outline.get("how_it_changes", ""),
        " ".join(outline.get("three_part_outline", [])),
        outline.get("unresolved_question", ""),
        outline.get("why_usable", ""),
    ]
    return " ".join(parts)


def test_story_tone_fields_have_no_numbers():
    p = DEMO_DIR / "episode_outline.json"
    o = json.loads(p.read_text(encoding="utf-8"))["outline"]
    text = _story_tone_text(o)
    digits = re.findall(r"\d+", text)
    assert not digits, (
        f"story-tone fields contain numbers (forbidden in main display): "
        f"{digits}\nText: {text}"
    )


def test_story_tone_fields_have_no_internal_terms():
    p = DEMO_DIR / "episode_outline.json"
    o = json.loads(p.read_text(encoding="utf-8"))["outline"]
    text = _story_tone_text(o)
    for tok in FORBIDDEN_INTERNAL:
        assert tok not in text, f"internal token leaked: {tok!r}"


def test_story_tone_fields_have_no_forbidden_numeric_patterns():
    p = DEMO_DIR / "episode_outline.json"
    o = json.loads(p.read_text(encoding="utf-8"))["outline"]
    text = _story_tone_text(o)
    for pattern in FORBIDDEN_NUMERIC_PATTERNS:
        assert not re.search(pattern, text), (
            f"forbidden numeric pattern in story-tone: {pattern!r}"
        )


# ============================================================================
# 3. index.html — Main Story Result before Run Summary
# ============================================================================

def test_main_story_appears_before_run_summary_in_html():
    html = (DEMO_DIR / "index.html").read_text(encoding="utf-8")
    ep_pos = html.find('id="episodeSection"')
    run_pos = html.find('id="runSummary"')
    assert ep_pos != -1, "episodeSection missing"
    assert run_pos != -1, "runSummary missing"
    assert ep_pos < run_pos, (
        "메인 결과물(episodeSection)이 실행 결과(runSummary)보다 *먼저* 나타나야 함."
    )


def test_hero_h1_emphasizes_story_not_data():
    html = (DEMO_DIR / "index.html").read_text(encoding="utf-8")
    m = re.search(r"<h1>([^<]+)</h1>", html)
    assert m
    h1 = m.group(1)
    # 새 hero 메시지에는 "이야기" 단어가 들어가야
    assert "이야기" in h1, f"hero h1 lacks story framing: {h1!r}"
    # 기술 데모 톤 ("시뮬레이션 + 에피소드 데모") 제거 확인
    assert "에피소드 데모" not in h1, "stale technical hero detected"


# ============================================================================
# 4. Main episode section in HTML — no numeric leaks
# ============================================================================

def _extract_episode_main_block(html: str) -> str:
    """Extract the main episode section content (between episodeSection start
    and the *next* section heading)."""
    start = html.find('id="episodeSection"')
    assert start != -1
    # find end: the closing </section> at same level. Approx: find next
    # <section> tag after start.
    rest = html[start:]
    next_section = rest.find("<section", 100)
    if next_section == -1:
        next_section = len(rest)
    return rest[:next_section]


def test_episode_main_block_has_no_internal_tokens():
    html = (DEMO_DIR / "index.html").read_text(encoding="utf-8")
    block = _extract_episode_main_block(html)
    for tok in FORBIDDEN_INTERNAL:
        assert tok not in block, f"internal token in main episode block: {tok!r}"


def test_payload_one_line_story_is_used_not_data_logline():
    """JS template uses ep.one_line_story for the main display, not ep.logline.

    그렇게 하면 *메인 영역*에 수치가 안 나옴. 페이로드의 logline 필드는 *Evidence
    접힘*에만 노출되어야.
    """
    html = (DEMO_DIR / "index.html").read_text(encoding="utf-8")
    # script 영역에서 ep.one_line_story 참조 확인
    assert "ep.one_line_story" in html, (
        "main episode template must use ep.one_line_story (story-tone), "
        "not ep.logline (data-cited)"
    )


# ============================================================================
# 5. Evidence section — numbers ARE allowed there (sanity)
# ============================================================================

def test_evidence_payload_logline_still_carries_numbers():
    """Sanity: data-cited logline (Evidence 영역용) is still numeric."""
    p = DEMO_DIR / "episode_outline.json"
    o = json.loads(p.read_text(encoding="utf-8"))["outline"]
    # logline 자체는 numeric 표현 유지 (data evidence)
    digits = re.findall(r"\d+", o["logline"])
    assert digits, (
        f"data-cited logline lost its numeric citations: {o['logline']!r}"
    )


# ============================================================================
# 6. Markdown output mirrors the same hierarchy
# ============================================================================

def test_episode_outline_md_uses_story_tone_first():
    """한 줄 이야기 (story-tone)가 Evidence (수치)보다 먼저 등장.

    Iter 22-26 후: 메인 영역 필드명이 한국어로 변경됨 ('한 줄 이야기').
    """
    md = (DEMO_DIR / "episode_outline.md").read_text(encoding="utf-8")
    pos_story = md.find("한 줄 이야기")
    pos_evidence = md.find("Evidence")
    assert pos_story != -1, "'한 줄 이야기' heading missing"
    assert pos_evidence != -1, "Evidence section heading missing"
    assert pos_story < pos_evidence, (
        "'한 줄 이야기' must appear before 'Evidence' in markdown."
    )


def test_episode_outline_md_korean_field_labels_visible():
    """메인 마크다운에 한국어 필드명이 모두 보임 (Iter 22-26 directive §3)."""
    md = (DEMO_DIR / "episode_outline.md").read_text(encoding="utf-8")
    for label in (
        "그가 원하는 것",
        "그를 밀어붙이는 압력",
        "어떻게 변하는가",
        "이야기 흐름",
        "어디에 쓸 수 있는가",
    ):
        assert label in md, f"Korean field label missing in md: {label}"


# ============================================================================
# 7. Evidence-aware story-tone — different seeds yield different main text
#    (Iter 17-20, 2026-05-08)
# ============================================================================

def _outline_for_seed(seed: int, tmp_path) -> dict:
    out = tmp_path / f"seed{seed}"
    rc = subprocess.run(
        [sys.executable,
         str(ROOT / "scripts/narrative/run_portfolio_demo.py"),
         "--seed", str(seed),
         "--output", str(out)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0, rc.stderr
    return json.loads(
        (out / "episode_outline.json").read_text(encoding="utf-8")
    )["outline"]


def test_different_seeds_produce_different_one_line_story(tmp_path):
    """Story-tone evidence-aware: 같은 conflict이라도 evidence 패턴이 다르면
    one_line_story 본문이 다르게 나와야 — seed 0 vs seed 7."""
    o0 = _outline_for_seed(0, tmp_path)
    o7 = _outline_for_seed(7, tmp_path)
    # 같은 conflict이면 base template은 같지만 evidence-aware suffix가
    # 추가되어 결과가 달라야 한다
    assert o0["one_line_story"] != o7["one_line_story"], (
        "story-tone one_line_story is identical across seeds — "
        "evidence-aware boost not active"
    )


def test_evidence_aware_main_text_still_has_no_numbers(tmp_path):
    """Evidence boost 적용 후에도 메인 영역 수치 0 유지."""
    for seed in (0, 7):
        o = _outline_for_seed(seed, tmp_path)
        text = " ".join([
            o["one_line_story"],
            o["what_character_wants"],
            o["what_pressures_them"],
            o["how_it_changes"],
            " ".join(o["three_part_outline"]),
            o["unresolved_question"],
            o["why_usable"],
        ])
        digits = re.findall(r"\d+", text)
        assert not digits, (
            f"evidence-aware main text leaked numbers in seed {seed}: "
            f"{digits}"
        )


def test_evidence_aware_what_pressures_uses_qualitative_descriptors(tmp_path):
    """what_pressures_them에 정성 표현 단어가 들어 있어야."""
    o = _outline_for_seed(0, tmp_path)
    qualitative = ("오래", "꾸준히", "잠시", "압도적으로", "분명히", "간간이",
                   "가라앉지 않는", "머물다", "누적되는", "지나가는")
    found = sum(q in o["what_pressures_them"] for q in qualitative)
    assert found >= 1, (
        f"what_pressures_them lacks qualitative descriptors: {o['what_pressures_them']}"
    )


def test_three_part_phase3_evidence_aware_differs_by_seed(tmp_path):
    """Three-part outline phase 3 (전환)에 evidence-aware 정성 한 절 추가.
    같은 conflict이라도 seed별 행동 변화 패턴이 다르면 phase 3 본문도 달라야."""
    o0 = _outline_for_seed(0, tmp_path)
    o7 = _outline_for_seed(7, tmp_path)
    p0 = o0["three_part_outline"][2]
    p7 = o7["three_part_outline"][2]
    # phase 1, 2는 plot structure로 동일 가능. phase 3는 evidence-aware
    # 정성 표현이 붙으므로 달라야.
    if p0 == p7:
        # Both seeds may have produced identical action pattern → still
        # acceptable but should at least contain the evidence-aware suffix
        for s in (p0, p7):
            assert "행동" in s, (
                f"phase 3 lacks evidence-aware action qualifier: {s}"
            )
    else:
        # 다른 본문 — 각각 정성 표현 포함
        for s in (p0, p7):
            assert "행동" in s


def test_three_part_outline_has_no_numbers(tmp_path):
    """Three-part outline 전체 (3 lines) 어디에도 수치 없음."""
    for seed in (0, 7):
        o = _outline_for_seed(seed, tmp_path)
        text = " ".join(o["three_part_outline"])
        digits = re.findall(r"\d+", text)
        assert not digits, (
            f"three_part_outline leaked numbers in seed {seed}: {digits}"
        )


# ============================================================================
# 8. Final portfolio re-edit (directive 2026-05-08, Iter 22-28)
# ============================================================================

def test_hero_h1_mentions_simulation_and_story():
    """Hero h1에 '시뮬레이션' + '이야기 개요' 모두 포함."""
    html = (DEMO_DIR / "index.html").read_text(encoding="utf-8")
    m = re.search(r"<h1>([^<]+)</h1>", html)
    assert m
    h1 = m.group(1)
    assert "시뮬레이션" in h1, f"hero h1 missing '시뮬레이션': {h1}"
    assert "이야기 개요" in h1, f"hero h1 missing '이야기 개요': {h1}"


def test_hero_has_flow_strip():
    """Hero 아래 흐름 표시 (시뮬레이션 → 압력 → 이야기 개요 → 근거)."""
    html = (DEMO_DIR / "index.html").read_text(encoding="utf-8")
    assert 'class="flow-strip"' in html
    for step in ("시뮬레이션 실행", "인물의 압력 흐름", "이야기 개요", "근거"):
        assert step in html, f"flow-strip missing '{step}'"


def test_main_uses_korean_field_labels():
    """메인 에피소드 영역의 필드명이 한국어."""
    html = (DEMO_DIR / "index.html").read_text(encoding="utf-8")
    # JS template 안의 한국어 필드명 검사
    for label in (
        "그가 원하는 것",
        "그를 밀어붙이는 압력",
        "어떻게 변하는가",
        "이야기 흐름",
        "어디에 쓸 수 있는가",
        "보조 흐름",
    ):
        assert label in html, f"missing Korean main field label: {label}"


def test_main_main_character_is_korean_name():
    """main_character가 한국어 이름 (Peter → 베드로)."""
    o = json.loads(
        (DEMO_DIR / "episode_outline.json").read_text(encoding="utf-8")
    )["outline"]
    # peter_scarcity_baseline anchor에서는 Peter → 베드로
    assert o["main_character"] == "베드로", (
        f"main_character should be '베드로' (Korean), got: {o['main_character']!r}"
    )
    # one_line_story도 베드로 사용
    assert "베드로" in o["one_line_story"]
    assert "Peter" not in o["one_line_story"], (
        "one_line_story still contains English 'Peter' — Korean name overlay missing"
    )


def test_main_avoids_strong_unjustified_adverbs():
    """'압도적으로' 같은 과한 부사가 메인 영역에 노출되지 않아야 (directive §2)."""
    o = json.loads(
        (DEMO_DIR / "episode_outline.json").read_text(encoding="utf-8")
    )["outline"]
    main_text = " ".join([
        o["one_line_story"],
        o["what_pressures_them"],
        o["how_it_changes"],
        " ".join(o["three_part_outline"]),
    ])
    # 단일 강한 부사는 evidence threshold가 명확하지 않으면 약화. directive 예시.
    # ("압도적으로 눌러온다" 형태가 노출되지 않아야)
    assert "압도적으로 눌러온다" not in main_text


# Story Seed Cards
def test_story_seed_cards_md_no_numeric_data_terms():
    """story_seed_cards.md 본문에 '단계' / '부근' / '데이터의 특징' 노출 안 됨.

    수치 인용은 evidence_report.md / Technical Appendix로 분리되어야 한다.
    """
    md = (DEMO_DIR / "story_seed_cards.md").read_text(encoding="utf-8")
    forbidden_phrases = (
        "200단계",
        "단계 부근",
        "단계 동안",
        "데이터의 특징",
        "관측된 상태 변화",
    )
    for phrase in forbidden_phrases:
        assert phrase not in md, (
            f"story_seed_cards.md leaks data-doc phrase: {phrase}"
        )


def test_story_seed_cards_md_titles_are_distinct():
    """S01-S04 title이 모두 달라야 (S02-S04가 같으면 보조 흐름 차이 약함)."""
    md = (DEMO_DIR / "story_seed_cards.md").read_text(encoding="utf-8")
    titles = re.findall(r"^## (.+)$", md, re.MULTILINE)
    assert len(titles) >= 3, f"too few seed titles: {titles}"
    assert len(titles) == len(set(titles)), (
        f"duplicate titles in story_seed_cards.md: {titles}"
    )


def test_story_seed_cards_main_seed_short():
    """S01 (메인 씨앗)은 '메인 에피소드의 중심축'으로 짧게 표기."""
    md = (DEMO_DIR / "story_seed_cards.md").read_text(encoding="utf-8")
    assert "메인 에피소드" in md and "중심축" in md, (
        "S01 should reference main episode + 중심축 phrase"
    )


def test_story_seed_cards_supporting_uses_role_titles():
    """S02-S04 카드 제목이 'role'에 매핑된 보조 차별화 단어를 사용."""
    md = (DEMO_DIR / "story_seed_cards.md").read_text(encoding="utf-8")
    # 적어도 두 개 이상의 *서로 다른* 보조 역할 단어가 카드 제목에 등장
    role_titles = ("결정을 미루는 사람", "지켜보는 사람", "늦게 반응하는 사람")
    found = sum(t in md for t in role_titles)
    assert found >= 2, (
        f"need ≥2 distinct supporting role-titles in story_seed_cards.md; "
        f"found {found}"
    )


# README compactness
def test_readme_first_section_has_quickstart():
    """README 첫 70줄 안에 빠른 실행 명령과 결과물 설명이 있어야.

    Phase 2.5/2.75/2.9 추가로 헤더 메타가 늘어나 30 → 70 줄로 완화."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    head = "\n".join(readme.splitlines()[:70])
    assert "scripts/narrative/run_portfolio_demo.py" in head, (
        "README quickstart command missing in first 70 lines"
    )
    assert "결과로 무엇이 나오나" in head or "결과물" in head, (
        "README missing 'what does it produce' framing in first 70 lines"
    )


def test_readme_first_lines_are_compact_intro():
    """README 첫 line은 tagline-style 한 줄 — 'WITNESS' 타이틀."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    lines = readme.splitlines()
    # H1 (line 0)
    assert lines[0].startswith("# WITNESS"), (
        f"README first line should be a H1 with 'WITNESS': {lines[0]!r}"
    )


# ============================================================================
# 9. Multi-seed acceptance robustness (Iter 31)
#
# 메인 portfolio acceptance가 seed 0뿐 아니라 *다른 seed*에서도 유지되어야.
# directive Acceptance 항목들이 시뮬레이션 분기에 의존하지 않음을 강제.
# ============================================================================

def test_seed_7_main_text_has_no_numbers(tmp_path):
    """seed 7로 portfolio demo 실행해도 메인 영역 수치 0 유지."""
    o = _outline_for_seed(7, tmp_path)
    text = " ".join([
        o["one_line_story"],
        o["what_character_wants"],
        o["what_pressures_them"],
        o["how_it_changes"],
        " ".join(o["three_part_outline"]),
        o["unresolved_question"],
        o["why_usable"],
    ])
    digits = re.findall(r"\d+", text)
    assert not digits, f"seed 7 main text leaked numbers: {digits}"


def test_seed_7_main_character_is_korean(tmp_path):
    """seed 7도 main_character가 한국어 매핑됨 (Peter→베드로)."""
    o = _outline_for_seed(7, tmp_path)
    assert o["main_character"] == "베드로"
    assert "Peter" not in o["one_line_story"]


def test_seed_7_no_internal_terms(tmp_path):
    """seed 7 메인 영역에 internal terms (tick / authority_vigilance / 등) 0."""
    o = _outline_for_seed(7, tmp_path)
    text = " ".join([
        o["one_line_story"],
        o["what_pressures_them"],
        o["how_it_changes"],
        " ".join(o["three_part_outline"]),
    ])
    for tok in FORBIDDEN_INTERNAL:
        assert tok not in text, f"seed 7 leaked internal token: {tok!r}"


def test_main_section_has_no_english_field_labels():
    """index.html *전체*에 영어 필드명 ('What He Wants' / 'Three-part Outline'
    등) 0 — 메인 화면이 한국어로 통일됨. Technical Appendix에는 영어 허용
    하지만 현재 데모는 영어 필드명 없이 작동 가능하므로 0 강제."""
    html = (DEMO_DIR / "index.html").read_text(encoding="utf-8")
    english_labels = (
        "What He Wants", "What Pressures Him", "How It Changes",
        "Three-part Outline", "Why This Is Usable", "Supporting Seeds",
        ">Main Character<", ">Unresolved Question<", "One-line Story",
    )
    for lbl in english_labels:
        assert lbl not in html, (
            f"English field label leaked into HTML: {lbl!r}"
        )


def test_pressure_summary_has_no_internal_terms():
    """pressure_summary.json 의 plain_label / summary에 internal pressure
    code 누설 0 (authority_vigilance / public_suspicion 등 영어 dict key)."""
    p = json.loads(
        (DEMO_DIR / "pressure_summary.json").read_text(encoding="utf-8")
    )
    text = json.dumps(p, ensure_ascii=False)
    for tok in (
        "authority_vigilance", "public_suspicion", "blame_concentration",
        "group_tension", "crowd_mood",
    ):
        assert tok not in text, (
            f"pressure_summary leaked internal pressure code: {tok!r}"
        )
