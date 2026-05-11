"""Render UniversalStorySeed + AnchorBinding → 한국어 surface.

Per `docs/witness_narrative_mode_plan.md` §3.5:
    뼈대 엔진은 universal seed만 출력한다.
    포트폴리오 표면이 universal seed + AnchorRegistry를 결합해
    anchor 버전을 렌더링한다.

이 모듈은 그 *결합 layer*. flesh engine 또는 portfolio surface가 사용한다.
skeleton engine은 이 모듈을 import하지 않는다.

핵심 함수:
    render_universal_seed_to_korean(seed, binding, taxonomy_data) → str
        UniversalStorySeed → 한국어 한 단락 (수치 0, story-tone)
"""
from __future__ import annotations

from typing import Any

from engine.anchor.anchor_registry import AnchorBinding
from engine.observer.universal_story_seed import (
    UniversalStorySeed,
    load_conflict_axes,
    load_desire_taxonomy,
    load_pressure_taxonomy,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve_main_display(
    seed: UniversalStorySeed, binding: AnchorBinding | None,
) -> str:
    """Universal main_role / archetype → display name (Korean if binding)."""
    if binding is not None:
        # Try role mapping first
        if seed.main_role and seed.main_role in binding.role_to_display_name_ko:
            return binding.role_to_display_name_ko[seed.main_role]
        # Then archetype
        if seed.main_archetype and seed.main_archetype in binding.archetype_to_display_name_ko:
            return binding.archetype_to_display_name_ko[seed.main_archetype]
    # Fallback: archetype label or generic
    return seed.main_archetype or seed.main_role or "중심 인물"


def _pressures_to_plain_ko(
    pressure_ids: tuple[str, ...],
    pressures_taxonomy: dict[str, dict[str, Any]] | None = None,
) -> list[str]:
    if pressures_taxonomy is None:
        pressures_taxonomy = load_pressure_taxonomy()
    out: list[str] = []
    for pid in pressure_ids:
        entry = pressures_taxonomy.get(pid)
        if entry:
            label = entry.get("plain_label_ko") or pid
            if label not in out:
                out.append(label)
    return out


def _desires_to_plain_ko(
    desire_ids: tuple[str, ...],
    desires_taxonomy: dict[str, dict[str, Any]] | None = None,
) -> list[str]:
    if desires_taxonomy is None:
        desires_taxonomy = load_desire_taxonomy()
    out: list[str] = []
    for did in desire_ids:
        entry = desires_taxonomy.get(did)
        if entry:
            label = entry.get("plain_label_ko") or did
            if label not in out:
                out.append(label)
    return out


def _conflict_axis_label_ko(
    axis_id: str,
    axes_taxonomy: dict[str, dict[str, Any]] | None = None,
) -> str:
    if axes_taxonomy is None:
        axes_taxonomy = load_conflict_axes()
    entry = axes_taxonomy.get(axis_id)
    if entry:
        return entry.get("plain_label_ko") or axis_id
    return axis_id


def _conflict_axis_question_ko(
    axis_id: str,
    axes_taxonomy: dict[str, dict[str, Any]] | None = None,
) -> str:
    if axes_taxonomy is None:
        axes_taxonomy = load_conflict_axes()
    entry = axes_taxonomy.get(axis_id)
    if entry:
        return entry.get("tension_question_ko") or ""
    return ""


# ---------------------------------------------------------------------------
# Top-level renderers
# ---------------------------------------------------------------------------

def render_universal_seed_to_korean(
    seed: UniversalStorySeed,
    binding: AnchorBinding | None = None,
) -> str:
    """UniversalStorySeed + (optional) AnchorBinding → 한국어 단락.

    수치 0 — story-tone. 메인 인물 이름 (display) + 갈등 축 + 압박 + 욕망.
    """
    pressures_taxonomy = load_pressure_taxonomy()
    desires_taxonomy = load_desire_taxonomy()
    axes_taxonomy = load_conflict_axes()

    main_display = _resolve_main_display(seed, binding)
    axis_label = _conflict_axis_label_ko(seed.conflict_axis_id, axes_taxonomy)
    axis_question = _conflict_axis_question_ko(seed.conflict_axis_id, axes_taxonomy)
    pressures_ko = _pressures_to_plain_ko(seed.dominant_pressures, pressures_taxonomy)
    desires_ko = _desires_to_plain_ko(seed.dominant_desires, desires_taxonomy)

    parts: list[str] = []
    parts.append(f"**{main_display}** — {axis_label}")
    if axis_question:
        parts.append(f"질문: {axis_question}")
    if desires_ko:
        parts.append(f"이루고 싶은 것: {', '.join(desires_ko)}")
    if pressures_ko:
        parts.append(f"받는 압력: {', '.join(pressures_ko)}")
    return "\n".join(parts)


def render_universal_seed_to_dict(
    seed: UniversalStorySeed,
    binding: AnchorBinding | None = None,
) -> dict:
    """UniversalStorySeed + binding → flat dict for HTML / JSON UIs.

    Phase 2.5 v1.1: change_pattern / arc_direction / relationship_function /
    flow_role / supporting_archetypes / turning_points_count 모두 노출.
    """
    pressures_taxonomy = load_pressure_taxonomy()
    desires_taxonomy = load_desire_taxonomy()
    axes_taxonomy = load_conflict_axes()
    return {
        "seed_id": seed.seed_id,
        "main_display": _resolve_main_display(seed, binding),
        "main_archetype": seed.main_archetype,
        "main_role": seed.main_role,
        "conflict_axis_id": seed.conflict_axis_id,
        "conflict_axis_label_ko": _conflict_axis_label_ko(seed.conflict_axis_id, axes_taxonomy),
        "conflict_axis_question_ko": _conflict_axis_question_ko(seed.conflict_axis_id, axes_taxonomy),
        "pressures_ko": _pressures_to_plain_ko(seed.dominant_pressures, pressures_taxonomy),
        "desires_ko": _desires_to_plain_ko(seed.dominant_desires, desires_taxonomy),
        "supporting_archetypes": list(seed.supporting_archetypes),
        "supporting_role_ids": list(seed.supporting_roles),
        "change_pattern": seed.change_pattern,
        "arc_direction": seed.arc_direction,
        "relationship_function": seed.relationship_function,
        "flow_role": seed.flow_role,
        "turning_points_count": seed.turning_points_count,
        "confidence_label": seed.confidence_label,
        "audit_status": seed.audit_status,
    }
