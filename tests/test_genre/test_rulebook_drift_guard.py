"""Tests for *generic* rulebook drift guard + multi-genre abstraction.

Per Phase 2.5 §F drift guard pattern, applied to genre layer:
    - rulebook schema_version freeze
    - audit_blocklist schema_version freeze
    - core required keys
    - rulebook abstraction이 1개 장르에 hardcoded이 아님 (japanese_quiet_drama
      추가로 확인)
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
GENRES_DIR = ROOT / "content" / "genres"


def _list_genre_dirs() -> list[Path]:
    return sorted(p for p in GENRES_DIR.iterdir() if p.is_dir())


# ---------------------------------------------------------------------------
# 1. Drift guard — 모든 장르 rulebook가 schema 따라야
# ---------------------------------------------------------------------------

EXPECTED_RULEBOOK_KEYS = (
    "schema_version", "genre_id", "display_name_ko", "description_ko",
    "conflict_amplifiers", "role_mappings", "pressure_mappings",
    "episode_rhythm", "cliffhanger_patterns",
    "allowed_transformations", "forbidden_transformations",
)

EXPECTED_BLOCKLIST_KEYS = (
    "schema_version", "genre_id",
    "forbidden_event_tokens", "forbidden_dialogue_markers",
    "forbidden_source_imitation",
)


def test_at_least_two_genres_exist():
    """rulebook 추상화가 1개에 hardcoded인지 검증 — 최소 2 장르 필요."""
    genres = _list_genre_dirs()
    assert len(genres) >= 2, (
        f"need ≥2 genre rulebooks to validate abstraction; got {[g.name for g in genres]}"
    )


def test_all_rulebooks_use_v1_schema():
    for gdir in _list_genre_dirs():
        rb_path = gdir / "rulebook.json"
        if not rb_path.exists():
            continue
        d = json.loads(rb_path.read_text(encoding="utf-8"))
        assert d.get("schema_version") == "genre_rulebook_v1", (
            f"{gdir.name}/rulebook.json schema_version drifted: {d.get('schema_version')!r}"
        )


def test_all_audit_blocklists_use_v1_schema():
    for gdir in _list_genre_dirs():
        bl_path = gdir / "audit_blocklist.json"
        if not bl_path.exists():
            continue
        d = json.loads(bl_path.read_text(encoding="utf-8"))
        assert d.get("schema_version") == "genre_audit_blocklist_v1", (
            f"{gdir.name}/audit_blocklist.json schema_version drifted"
        )


def test_all_rulebooks_have_required_keys():
    for gdir in _list_genre_dirs():
        rb_path = gdir / "rulebook.json"
        if not rb_path.exists():
            continue
        d = json.loads(rb_path.read_text(encoding="utf-8"))
        for key in EXPECTED_RULEBOOK_KEYS:
            assert key in d, f"{gdir.name}/rulebook.json missing key: {key!r}"


def test_all_blocklists_have_required_keys():
    for gdir in _list_genre_dirs():
        bl_path = gdir / "audit_blocklist.json"
        if not bl_path.exists():
            continue
        d = json.loads(bl_path.read_text(encoding="utf-8"))
        for key in EXPECTED_BLOCKLIST_KEYS:
            assert key in d, f"{gdir.name}/audit_blocklist.json missing key: {key!r}"


def test_all_rulebooks_genre_id_matches_dir_name():
    for gdir in _list_genre_dirs():
        rb_path = gdir / "rulebook.json"
        if not rb_path.exists():
            continue
        d = json.loads(rb_path.read_text(encoding="utf-8"))
        assert d.get("genre_id") == gdir.name, (
            f"genre_id mismatch: dir={gdir.name} rulebook says {d.get('genre_id')!r}"
        )


def test_all_rulebooks_have_episode_rhythm():
    """장르마다 자체 episode_rhythm을 정의해야 (parametric 증명)."""
    for gdir in _list_genre_dirs():
        rb_path = gdir / "rulebook.json"
        if not rb_path.exists():
            continue
        d = json.loads(rb_path.read_text(encoding="utf-8"))
        rhythm = d.get("episode_rhythm", [])
        assert len(rhythm) >= 4, (
            f"{gdir.name}: episode_rhythm too short ({len(rhythm)}, need ≥4)"
        )


def test_all_rulebooks_have_fallback_cliffhanger():
    """우선순위 fallback 없으면 select_cliffhanger가 깨질 수 있음."""
    for gdir in _list_genre_dirs():
        rb_path = gdir / "rulebook.json"
        if not rb_path.exists():
            continue
        d = json.loads(rb_path.read_text(encoding="utf-8"))
        cliffs = d.get("cliffhanger_patterns", [])
        has_fallback = any(c.get("fallback") for c in cliffs)
        assert has_fallback, (
            f"{gdir.name}: no cliffhanger pattern with fallback=true"
        )


def test_all_rulebooks_role_mappings_cover_core_roles():
    """모든 장르는 protagonist / supporting_actor / witness / delayed_actor 매핑 필수."""
    core_roles = ("protagonist", "supporting_actor", "witness", "delayed_actor")
    for gdir in _list_genre_dirs():
        rb_path = gdir / "rulebook.json"
        if not rb_path.exists():
            continue
        d = json.loads(rb_path.read_text(encoding="utf-8"))
        role_mappings = d.get("role_mappings", {})
        for role in core_roles:
            assert role in role_mappings, (
                f"{gdir.name}: role_mappings missing {role!r}"
            )


# ---------------------------------------------------------------------------
# 2. Cross-genre abstraction — japanese_quiet_drama로 검증
# ---------------------------------------------------------------------------

def test_load_japanese_quiet_drama_rulebook():
    """new genre가 generic loader로 로딩되는지."""
    from engine.observer.genre_rulebook import load_rulebook
    rb = load_rulebook("japanese_quiet_drama")
    assert rb.schema_version == "genre_rulebook_v1"
    assert rb.genre_id == "japanese_quiet_drama"
    assert "정적" in rb.display_name_ko or "조용" in rb.description_ko


def test_japanese_quiet_drama_has_distinct_amplifiers():
    """japanese_quiet_drama amplifier가 korean_morning_melodrama와 다름 (parametric 증명)."""
    from engine.observer.genre_rulebook import load_rulebook
    jp = load_rulebook("japanese_quiet_drama")
    kr = load_rulebook("korean_morning_melodrama")
    jp_ids = {a.id for a in jp.conflict_amplifiers}
    kr_ids = {a.id for a in kr.conflict_amplifiers}
    # 두 set이 정확히 같으면 abstraction이 작동 안 함
    assert jp_ids != kr_ids, "amplifiers must differ between genres"


def test_japanese_quiet_drama_has_distinct_cliffhanger_patterns():
    from engine.observer.genre_rulebook import load_rulebook
    jp = load_rulebook("japanese_quiet_drama")
    kr = load_rulebook("korean_morning_melodrama")
    jp_ids = {c.id for c in jp.cliffhanger_patterns}
    kr_ids = {c.id for c in kr.cliffhanger_patterns}
    assert jp_ids != kr_ids


def test_japanese_quiet_drama_adapter_pipeline():
    """SkeletonOutput → japanese_quiet_drama → audit pass."""
    from engine.observer.genre_adapter import adapt_skeleton_to_genre
    from engine.observer.genre_audit import audit_genre_output
    from engine.observer.genre_rulebook import load_audit_blocklist, load_rulebook

    from tests.test_genre.test_genre_adapter import _make_clean_skeleton

    rb = load_rulebook("japanese_quiet_drama")
    bl = load_audit_blocklist("japanese_quiet_drama")
    sk = _make_clean_skeleton()

    out = adapt_skeleton_to_genre(sk, rb)
    assert out.genre_id == "japanese_quiet_drama"
    assert len(out.adapted_seeds) == 4

    audit = audit_genre_output(out, bl)
    assert audit.overall == "pass", (
        f"japanese_quiet_drama audit failed: {audit.to_dict()}"
    )


def test_two_genres_produce_different_adapted_output():
    """같은 SkeletonOutput을 두 다른 장르로 변환하면 결과가 *달라야* 한다.

    이게 통과해야 rulebook abstraction이 의미 있다.
    """
    from engine.observer.genre_adapter import adapt_skeleton_to_genre
    from engine.observer.genre_rulebook import load_rulebook

    from tests.test_genre.test_genre_adapter import _make_clean_skeleton
    sk = _make_clean_skeleton()

    rb_kr = load_rulebook("korean_morning_melodrama")
    rb_jp = load_rulebook("japanese_quiet_drama")
    out_kr = adapt_skeleton_to_genre(sk, rb_kr)
    out_jp = adapt_skeleton_to_genre(sk, rb_jp)

    # 장르 id 다름
    assert out_kr.genre_id != out_jp.genre_id

    # adapted_premise_ko가 동일하지 않음 (같으면 변환이 작동 안 함)
    kr_premises = [s.adapted_premise_ko for s in out_kr.adapted_seeds]
    jp_premises = [s.adapted_premise_ko for s in out_jp.adapted_seeds]
    assert kr_premises != jp_premises, (
        "two genres produced identical premises — abstraction broken"
    )

    # cliffhanger도 다름 (또는 적어도 한 seed는 다름)
    kr_cliffs = [s.cliffhanger_ko for s in out_kr.adapted_seeds]
    jp_cliffs = [s.cliffhanger_ko for s in out_jp.adapted_seeds]
    assert kr_cliffs != jp_cliffs, (
        "two genres produced identical cliffhangers"
    )

    # 그러나 source_seed_id / source_conflict_axis_id는 *동일* (보존 증명)
    for kr_seed, jp_seed in zip(out_kr.adapted_seeds, out_jp.adapted_seeds):
        assert kr_seed.source_seed_id == jp_seed.source_seed_id
        assert kr_seed.source_conflict_axis_id == jp_seed.source_conflict_axis_id
        assert kr_seed.source_pressures == jp_seed.source_pressures
        assert kr_seed.source_desires == jp_seed.source_desires


def test_two_genres_produce_different_arc_phrases():
    """Phase 2.75 cycle 5: 같은 arc_direction을 두 장르가 다르게 phrasing."""
    from engine.observer.genre_rulebook import (
        load_rulebook, map_arc_direction_to_phrase,
    )
    rb_kr = load_rulebook("korean_morning_melodrama")
    rb_jp = load_rulebook("japanese_quiet_drama")
    # 두 rulebook 모두 visibility_to_silence를 phrase로 가짐
    kr_phrase = map_arc_direction_to_phrase(rb_kr, "visibility_to_silence")
    jp_phrase = map_arc_direction_to_phrase(rb_jp, "visibility_to_silence")
    assert kr_phrase
    assert jp_phrase
    assert kr_phrase != jp_phrase, (
        "two genres must phrase visibility_to_silence differently — "
        "abstraction broken if same"
    )


def test_two_genres_produce_different_flow_role_functions():
    from engine.observer.genre_rulebook import (
        load_rulebook, map_flow_role_to_function,
    )
    rb_kr = load_rulebook("korean_morning_melodrama")
    rb_jp = load_rulebook("japanese_quiet_drama")
    kr_func = map_flow_role_to_function(rb_kr, "main_arc")
    jp_func = map_flow_role_to_function(rb_jp, "main_arc")
    assert kr_func != jp_func, (
        "two genres must phrase main_arc function differently"
    )


def test_arc_direction_phrase_falls_back_for_unknown():
    """rulebook에 없는 arc_direction은 generic fallback."""
    from engine.observer.genre_rulebook import (
        load_rulebook, map_arc_direction_to_phrase,
    )
    rb = load_rulebook("korean_morning_melodrama")
    phrase = map_arc_direction_to_phrase(rb, "completely_made_up_direction")
    # generic fallback이 emit되어야 (구체적 장르 표현 X)
    assert phrase
    # "겉으로는 곁에" 같은 KR-specific phrase는 안 들어가야
    assert "겉으로는 곁에" not in phrase


def test_flow_role_function_falls_back_for_unknown():
    from engine.observer.genre_rulebook import (
        load_rulebook, map_flow_role_to_function,
    )
    rb = load_rulebook("japanese_quiet_drama")
    func = map_flow_role_to_function(rb, "made_up_flow_role")
    assert func
    # JP-specific phrase가 들어가면 안 됨
    assert "정적은 다음 회차로" not in func


def test_adapted_premises_differ_due_to_arc_phrasing():
    """Phase 2.75 cycle 5 회귀 방지: 두 장르 변환 결과의 premise가 *arc phrasing
    이유로* 달라야 한다."""
    from engine.observer.genre_adapter import adapt_skeleton_to_genre
    from engine.observer.genre_rulebook import load_rulebook

    from tests.test_genre.test_genre_adapter import _make_clean_skeleton
    sk = _make_clean_skeleton()
    rb_kr = load_rulebook("korean_morning_melodrama")
    rb_jp = load_rulebook("japanese_quiet_drama")
    out_kr = adapt_skeleton_to_genre(sk, rb_kr)
    out_jp = adapt_skeleton_to_genre(sk, rb_jp)
    # S01 premise — visibility_to_silence arc 사용
    s01_kr = next(s for s in out_kr.adapted_seeds if s.source_seed_id == "S01")
    s01_jp = next(s for s in out_jp.adapted_seeds if s.source_seed_id == "S01")
    assert s01_kr.adapted_premise_ko != s01_jp.adapted_premise_ko
    # 각 장르의 arc 표현이 들어 있어야
    assert "겉으로는 곁에 남지만" in s01_kr.adapted_premise_ko
    assert "곁에 머물지만 말은" in s01_jp.adapted_premise_ko


def test_rulebook_arc_phrases_field_exists():
    from engine.observer.genre_rulebook import load_rulebook
    for gid in ("korean_morning_melodrama", "japanese_quiet_drama"):
        rb = load_rulebook(gid)
        assert isinstance(rb.arc_direction_phrases, dict)
        assert "visibility_to_silence" in rb.arc_direction_phrases
        assert isinstance(rb.flow_role_function_phrases, dict)
        assert "main_arc" in rb.flow_role_function_phrases


def test_run_genre_demo_works_with_japanese_quiet_drama(tmp_path):
    """CLI가 japanese_quiet_drama로도 demo 생성 가능."""
    import subprocess
    import sys
    DEMO_SCRIPT = ROOT / "scripts/narrative/run_genre_demo.py"
    DEPLOYED = ROOT / "docs/portfolio/demo/skeleton_output.json"
    if not DEPLOYED.exists():
        pytest.skip()
    out_dir = tmp_path / "demo_jp"
    rc = subprocess.run(
        [sys.executable, str(DEMO_SCRIPT),
         "--skeleton", str(DEPLOYED),
         "--genre", "japanese_quiet_drama",
         "--output", str(out_dir)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )
    assert rc.returncode == 0, rc.stderr
    assert (out_dir / "index.html").exists()
    html = (out_dir / "index.html").read_text(encoding="utf-8")
    assert "japanese_quiet_drama" in html
    # 일본 드라마 톤 단어가 들어 있어야 (rulebook의 display_name_ko)
    assert "정적" in html or "조용" in html
