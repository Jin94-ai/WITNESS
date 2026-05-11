"""Tests for genre_rulebook loader (Phase 2.75 §4 + §5)."""
from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def test_load_rulebook_korean_morning_melodrama():
    from engine.observer.genre_rulebook import load_rulebook
    rb = load_rulebook("korean_morning_melodrama")
    assert rb.schema_version == "genre_rulebook_v1"
    assert rb.genre_id == "korean_morning_melodrama"
    assert rb.display_name_ko
    assert len(rb.conflict_amplifiers) >= 3
    assert len(rb.episode_rhythm) == 6
    assert len(rb.cliffhanger_patterns) >= 4


def test_rulebook_role_mappings_cover_required_roles():
    """Plan §5.2: protagonist / supporting_actor / witness / delayed_actor."""
    from engine.observer.genre_rulebook import load_rulebook
    rb = load_rulebook("korean_morning_melodrama")
    for role in ("protagonist", "supporting_actor", "witness", "delayed_actor"):
        assert role in rb.role_mappings, f"missing role mapping: {role}"
        assert len(rb.role_mappings[role]) >= 1


def test_rulebook_pressure_mappings_cover_taxonomy():
    """rulebook의 pressure_mappings가 universal pressure_taxonomy의 핵심을 커버해야."""
    from engine.observer.genre_rulebook import load_rulebook
    rb = load_rulebook("korean_morning_melodrama")
    for pid in ("fear", "confusion", "authority_vigilance",
                 "public_suspicion", "group_tension", "crowd_tension"):
        assert pid in rb.pressure_mappings, f"missing pressure mapping: {pid}"


def test_load_audit_blocklist():
    from engine.observer.genre_rulebook import load_audit_blocklist
    bl = load_audit_blocklist("korean_morning_melodrama")
    assert bl.schema_version == "genre_audit_blocklist_v1"
    assert bl.genre_id == "korean_morning_melodrama"
    # 핵심 막장 토큰
    for token in ("출생의 비밀", "불륜", "살인", "납치"):
        assert token in bl.forbidden_event_tokens


def test_audit_blocklist_dialogue_markers():
    from engine.observer.genre_rulebook import load_audit_blocklist
    bl = load_audit_blocklist("korean_morning_melodrama")
    assert "라고 말했다" in bl.forbidden_dialogue_markers
    # 양쪽 따옴표 (한국어 큰따옴표 + ASCII)
    assert "“" in bl.forbidden_dialogue_markers


def test_load_rulebook_unknown_genre_raises():
    from engine.observer.genre_rulebook import load_rulebook
    with pytest.raises(FileNotFoundError):
        load_rulebook("nonexistent_genre_xyz")


def test_select_amplifier_by_conflict_axis():
    from engine.observer.genre_rulebook import load_rulebook, select_amplifier
    rb = load_rulebook("korean_morning_melodrama")
    amp = select_amplifier(rb, "loyalty_vs_survival")
    assert amp is not None
    # silence_to_misunderstanding이 loyalty_vs_survival에 적용
    assert amp.id in ("silence_to_misunderstanding", "family_gaze_pressure")


def test_select_amplifier_returns_none_for_unmatched():
    from engine.observer.genre_rulebook import load_rulebook, select_amplifier
    rb = load_rulebook("korean_morning_melodrama")
    amp = select_amplifier(rb, "completely_made_up_axis")
    assert amp is None


def test_select_cliffhanger_priority_order():
    """우선순위: loyalty_vs_survival → silence_read_as_betrayal (priority 1)."""
    from engine.observer.genre_rulebook import load_rulebook, select_cliffhanger
    rb = load_rulebook("korean_morning_melodrama")
    cliff = select_cliffhanger(
        rb,
        conflict_axis_ids=("loyalty_vs_survival",),
        main_roles=("protagonist",),
    )
    assert cliff.id == "silence_read_as_betrayal"


def test_select_cliffhanger_witness_role():
    """witness role이 있으면 witness_notices_gap (loyalty 매칭 없을 때)."""
    from engine.observer.genre_rulebook import load_rulebook, select_cliffhanger
    rb = load_rulebook("korean_morning_melodrama")
    cliff = select_cliffhanger(
        rb,
        conflict_axis_ids=("trust_vs_self_protection",),
        main_roles=("witness",),
    )
    # silence_read_as_betrayal (priority 1, requires loyalty_vs_survival) is skipped
    # witness_notices_gap (priority 2, requires_role=witness) wins
    assert cliff.id == "witness_notices_gap"


def test_select_cliffhanger_fallback():
    """매칭 없으면 fallback (unresolved_question_to_next_episode)."""
    from engine.observer.genre_rulebook import load_rulebook, select_cliffhanger
    rb = load_rulebook("korean_morning_melodrama")
    cliff = select_cliffhanger(
        rb,
        conflict_axis_ids=("nonexistent_axis",),
        main_roles=("nonexistent_role",),
    )
    assert cliff.fallback or cliff.priority >= 99


def test_map_pressure_to_genre():
    from engine.observer.genre_rulebook import load_rulebook, map_pressure_to_genre
    rb = load_rulebook("korean_morning_melodrama")
    assert map_pressure_to_genre(rb, "authority_vigilance") == "가족/권위자의 시선"
    # unknown pressure → passthrough
    assert map_pressure_to_genre(rb, "unknown_pressure_xyz") == "unknown_pressure_xyz"


def test_map_role_to_genre():
    from engine.observer.genre_rulebook import load_rulebook, map_role_to_genre
    rb = load_rulebook("korean_morning_melodrama")
    label = map_role_to_genre(rb, "protagonist")
    assert label in ("버티는 사람", "숨기는 사람")
    # unknown role → passthrough
    assert map_role_to_genre(rb, "made_up_role") == "made_up_role"
