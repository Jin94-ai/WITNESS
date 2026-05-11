"""GenreRulebook loader + dataclasses (Phase 2.75 §4 + §5).

Per `docs/WITNESS_PHASE_2_75_GENRE_ADAPTER_MVP_PLAN.md`:
    rule-based Flesh MVP. SkeletonOutput v1.1을 받아 *구조* 수준에서
    장르 문법으로 해석. 외부 의존 0.

이 모듈은 rulebook JSON + audit blocklist JSON을 읽어 dataclass로 변환.
실제 변환 로직은 engine/observer/genre_adapter.py가 담당.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


_GENRE_ROOT = Path(__file__).resolve().parents[2] / "content" / "genres"


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ConflictAmplifier:
    id: str
    description_ko: str
    applies_to: tuple[str, ...]


@dataclass(frozen=True)
class CliffhangerPattern:
    id: str
    description_ko: str
    priority: int
    requires: tuple[str, ...] = ()      # conflict axis ids
    requires_role: str = ""               # main_role or supporting role
    fallback: bool = False


@dataclass(frozen=True)
class GenreRulebook:
    schema_version: str
    genre_id: str
    display_name_ko: str
    description_ko: str
    conflict_amplifiers: tuple[ConflictAmplifier, ...]
    role_mappings: dict[str, tuple[str, ...]]      # role_id → (label_ko ...)
    pressure_mappings: dict[str, str]              # pressure_id → label_ko
    episode_rhythm: tuple[str, ...]
    cliffhanger_patterns: tuple[CliffhangerPattern, ...]
    allowed_transformations: tuple[str, ...]
    forbidden_transformations: tuple[str, ...]
    # Phase 2.75 cycle 5: per-genre phrasing (parametric over hardcoded fallback)
    arc_direction_phrases: dict[str, str] = field(default_factory=dict)
    flow_role_function_phrases: dict[str, str] = field(default_factory=dict)
    # Phase 2.8: structured outline templates (Issue 1+6)
    genre_lens_ko: str = ""
    outline_templates: dict[str, dict[str, str]] = field(default_factory=dict)
                                                         # role → phase ("early"/"middle"/"late") → template
    outline_step_mapping: dict[str, str] = field(default_factory=dict)
                                                         # episode_rhythm step → phase
    outline_role_assignment_priority: tuple[str, ...] = ()
                                                         # 각 step에 어떤 role을 할당할지
    outline_final_step_uses_cliffhanger: bool = False
                                                         # True면 마지막 step은 outline template 대신 cliffhanger 문장


@dataclass(frozen=True)
class GenreAuditBlocklist:
    schema_version: str
    genre_id: str
    forbidden_event_tokens: tuple[str, ...]
    forbidden_dialogue_markers: tuple[str, ...]
    forbidden_source_imitation: tuple[str, ...]


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_rulebook(genre_id: str, *, root: Path | None = None) -> GenreRulebook:
    """Load `content/genres/{genre_id}/rulebook.json`."""
    base = (root or _GENRE_ROOT) / genre_id
    p = base / "rulebook.json"
    if not p.exists():
        raise FileNotFoundError(f"rulebook not found: {p}")
    raw = json.loads(p.read_text(encoding="utf-8"))

    if raw.get("schema_version") != "genre_rulebook_v1":
        raise ValueError(
            f"unsupported rulebook schema_version: {raw.get('schema_version')!r}"
        )
    if raw.get("genre_id") != genre_id:
        raise ValueError(
            f"genre_id mismatch: rulebook says {raw.get('genre_id')!r}, "
            f"requested {genre_id!r}"
        )

    amplifiers = tuple(
        ConflictAmplifier(
            id=a["id"],
            description_ko=a["description_ko"],
            applies_to=tuple(a.get("applies_to", [])),
        )
        for a in raw.get("conflict_amplifiers", [])
    )

    cliffs = tuple(
        CliffhangerPattern(
            id=c["id"],
            description_ko=c["description_ko"],
            priority=int(c.get("priority", 99)),
            requires=tuple(c.get("requires", [])),
            requires_role=c.get("requires_role", ""),
            fallback=bool(c.get("fallback", False)),
        )
        for c in raw.get("cliffhanger_patterns", [])
    )

    role_mappings = {
        k: tuple(v) for k, v in raw.get("role_mappings", {}).items()
    }
    pressure_mappings = dict(raw.get("pressure_mappings", {}))

    return GenreRulebook(
        schema_version=raw["schema_version"],
        genre_id=raw["genre_id"],
        display_name_ko=raw.get("display_name_ko", genre_id),
        description_ko=raw.get("description_ko", ""),
        conflict_amplifiers=amplifiers,
        role_mappings=role_mappings,
        pressure_mappings=pressure_mappings,
        episode_rhythm=tuple(raw.get("episode_rhythm", [])),
        cliffhanger_patterns=cliffs,
        allowed_transformations=tuple(raw.get("allowed_transformations", [])),
        forbidden_transformations=tuple(raw.get("forbidden_transformations", [])),
        arc_direction_phrases=dict(raw.get("arc_direction_phrases", {})),
        flow_role_function_phrases=dict(raw.get("flow_role_function_phrases", {})),
        genre_lens_ko=raw.get("genre_lens_ko", ""),
        outline_templates={
            role: dict(phase_map)
            for role, phase_map in raw.get("outline_templates", {}).items()
        },
        outline_step_mapping=dict(raw.get("outline_step_mapping", {})),
        outline_role_assignment_priority=tuple(
            raw.get("outline_role_assignment_priority", [])
        ),
        outline_final_step_uses_cliffhanger=bool(
            raw.get("outline_final_step_uses_cliffhanger", False)
        ),
    )


def load_audit_blocklist(
    genre_id: str, *, root: Path | None = None,
) -> GenreAuditBlocklist:
    """Load `content/genres/{genre_id}/audit_blocklist.json`."""
    base = (root or _GENRE_ROOT) / genre_id
    p = base / "audit_blocklist.json"
    if not p.exists():
        raise FileNotFoundError(f"audit_blocklist not found: {p}")
    raw = json.loads(p.read_text(encoding="utf-8"))

    if raw.get("schema_version") != "genre_audit_blocklist_v1":
        raise ValueError(
            f"unsupported blocklist schema_version: {raw.get('schema_version')!r}"
        )
    if raw.get("genre_id") != genre_id:
        raise ValueError(
            f"genre_id mismatch: blocklist says {raw.get('genre_id')!r}, "
            f"requested {genre_id!r}"
        )

    return GenreAuditBlocklist(
        schema_version=raw["schema_version"],
        genre_id=raw["genre_id"],
        forbidden_event_tokens=tuple(raw.get("forbidden_event_tokens", [])),
        forbidden_dialogue_markers=tuple(raw.get("forbidden_dialogue_markers", [])),
        forbidden_source_imitation=tuple(raw.get("forbidden_source_imitation", [])),
    )


# ---------------------------------------------------------------------------
# Helpers (rulebook lookup)
# ---------------------------------------------------------------------------

def select_amplifier(
    rulebook: GenreRulebook, conflict_axis_id: str,
) -> ConflictAmplifier | None:
    """conflict_axis_id에 적용 가능한 첫 번째 amplifier 반환 (rulebook 순서대로)."""
    for amp in rulebook.conflict_amplifiers:
        if conflict_axis_id in amp.applies_to:
            return amp
    return None


def select_cliffhanger(
    rulebook: GenreRulebook,
    *,
    conflict_axis_ids: tuple[str, ...],
    main_roles: tuple[str, ...],
) -> CliffhangerPattern:
    """우선순위 기반 cliffhanger 선택 (Plan §7.3).

    1. requires가 conflict_axis_ids와 매칭
    2. requires_role이 main_roles와 매칭
    3. fallback
    """
    candidates = list(rulebook.cliffhanger_patterns)
    candidates.sort(key=lambda c: c.priority)
    fallback: CliffhangerPattern | None = None
    for c in candidates:
        if c.fallback:
            if fallback is None or c.priority < fallback.priority:
                fallback = c
            continue
        if c.requires:
            if any(axis in conflict_axis_ids for axis in c.requires):
                return c
        if c.requires_role:
            if c.requires_role in main_roles:
                return c
    if fallback is not None:
        return fallback
    # Truly nothing — synthetic fallback (rulebook lacks fallback declaration)
    return CliffhangerPattern(
        id="unresolved_question_to_next_episode",
        description_ko="정리되지 않은 질문이 다음 회차로 넘어간다.",
        priority=999,
        fallback=True,
    )


def map_pressure_to_genre(
    rulebook: GenreRulebook, pressure_id: str,
) -> str:
    """pressure_id → 장르 표현 (rulebook.pressure_mappings)."""
    return rulebook.pressure_mappings.get(pressure_id, pressure_id)


def map_role_to_genre(
    rulebook: GenreRulebook, role_id: str,
) -> str:
    """role_id → 장르 역할 라벨 (rulebook.role_mappings, 첫 번째 라벨)."""
    labels = rulebook.role_mappings.get(role_id, ())
    if labels:
        return labels[0]
    return role_id


# Phase 2.75 cycle 5: parametric phrasing
_DEFAULT_ARC_DIRECTION_PHRASE = "변화가 천천히 누적된다"
_DEFAULT_FLOW_ROLE_FUNCTION = "이 흐름이 다음 회차로 넘어가며 긴장이 쌓인다."


def map_arc_direction_to_phrase(
    rulebook: GenreRulebook, arc_direction: str,
) -> str:
    """arc_direction id → 장르별 phrasing.

    rulebook의 `arc_direction_phrases`에 있으면 그 phrasing 사용.
    없으면 generic fallback 한 줄.
    """
    if not arc_direction:
        return _DEFAULT_ARC_DIRECTION_PHRASE
    return rulebook.arc_direction_phrases.get(arc_direction, _DEFAULT_ARC_DIRECTION_PHRASE)


def map_flow_role_to_function(
    rulebook: GenreRulebook, flow_role: str,
) -> str:
    """flow_role id → 장르별 기능 phrasing."""
    if not flow_role:
        return _DEFAULT_FLOW_ROLE_FUNCTION
    return rulebook.flow_role_function_phrases.get(flow_role, _DEFAULT_FLOW_ROLE_FUNCTION)


# Phase 2.8 Issue 2: plain-label resolution for internal IDs
# (taxonomy 기반 label은 universal_story_seed.load_*에서 직접 로딩)
_ARCHETYPE_PLAIN_KO = {
    "loyal_under_pressure": "압력 속에서도 남으려는 사람",
    "uncertain_actor": "결정을 미루는 사람",
    "uncertain_disciple": "결정을 미루는 사람",
    "watcher": "지켜보지만 말하지 않는 사람",
    "late_responder": "뒤늦게 반응하는 사람",
}

_FLOW_ROLE_PLAIN_KO = {
    "main_arc": "중심 흐름",
    "witness_arc": "지켜보는 흐름",
    "supporting_uncertainty": "망설이는 보조 흐름",
    "delayed_response_arc": "뒤늦은 반응 흐름",
}


def archetype_plain_ko(archetype_id: str) -> str:
    """archetype 내부 ID → 일반인용 한국어 label. Phase 2.8 Issue 2."""
    return _ARCHETYPE_PLAIN_KO.get(archetype_id, archetype_id)


def flow_role_plain_ko(flow_role_id: str) -> str:
    return _FLOW_ROLE_PLAIN_KO.get(flow_role_id, flow_role_id)
