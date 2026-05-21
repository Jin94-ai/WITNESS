"""Adapter: existing StorySeedCard / StoryCandidate → UniversalStorySeed.

Per `docs/witness_narrative_mode_plan.md` Phase 0
+ `docs/WITNESS_NARRATIVE_MODE_VALIDATION_FIX_PLAN.md` Phase D (lossless).

이 어댑터는 기존 anchor-bound seed (인물명 / 정경 사건 포함)에서
*anchor-clean* 추상을 추출해 UniversalStorySeed로 만든다.

원칙 (Phase 2.5 lossless):
    - archetype_by_seed는 *필수*. 없으면 ValueError.
    - main_role / supporting_roles는 archetype에서 lookup. placeholder 금지.
    - dominant_pressures는 4-tier fallback:
        1. phrase mapping
        2. conflict_axis pole에서 pressure
        3. archetype default vulnerabilities
        4. silent empty 금지 — audit_trail에 기록
    - unmapped pressure phrase는 audit_trail.unmapped_pressure_phrases에 누적
    - flow_role / change_pattern / arc_direction / relationship_function /
      supporting_archetypes 모두 채움 (UniversalStorySeed v1.1)
"""
from __future__ import annotations

from typing import Any

from engine.observer.skeleton_output import (
    AnchorMetadata,
    AuditTrail,
    EvidenceLedger,
    LifeStoryFlow,
    SkeletonOutput,
)
from engine.observer.universal_story_seed import (
    UniversalStorySeed,
    load_conflict_axes,
)

# ---------------------------------------------------------------------------
# Phase 2.5 §D.2: Default archetype / role / flow maps (Peter baseline MVP)
# ---------------------------------------------------------------------------

DEFAULT_ARCHETYPE_BY_SEED: dict[str, str] = {
    "S01": "loyal_under_pressure",
    "S02": "uncertain_actor",
    "S03": "watcher",
    "S04": "late_responder",
}

MAIN_ROLE_BY_ARCHETYPE: dict[str, str] = {
    "loyal_under_pressure": "protagonist",
    "uncertain_actor":      "supporting_actor",
    "uncertain_disciple":   "supporting_actor",  # legacy alias
    "watcher":              "witness",
    "late_responder":       "delayed_actor",
}

FLOW_ROLE_BY_SEED: dict[str, str] = {
    "S01": "main_arc",
    "S02": "supporting_uncertainty",
    "S03": "witness_arc",
    "S04": "delayed_response_arc",
}

DEFAULT_SUPPORTING_ARCHETYPES_BY_SEED: dict[str, tuple[str, ...]] = {
    "S01": ("uncertain_actor", "watcher"),
    "S02": ("watcher",),
    "S03": ("loyal_under_pressure",),
    "S04": ("uncertain_actor",),
}

CHANGE_PATTERN_BY_ARCHETYPE: dict[str, str] = {
    "loyal_under_pressure": "stay_present_then_withdraw",
    "uncertain_actor":      "delay_under_pressure",
    "uncertain_disciple":   "delay_under_pressure",
    "watcher":              "observe_without_intervening",
    "late_responder":       "delayed_action",
}

ARC_DIRECTION_BY_ARCHETYPE: dict[str, str] = {
    "loyal_under_pressure": "visibility_to_silence",
    "uncertain_actor":      "uncertainty_to_withdrawal",
    "uncertain_disciple":   "uncertainty_to_withdrawal",
    "watcher":              "presence_to_distance",
    "late_responder":       "silence_to_response",
}

RELATIONSHIP_FUNCTION_BY_ARCHETYPE: dict[str, str] = {
    "loyal_under_pressure": "group_presence_without_action",
    "uncertain_actor":      "contrast_to_main_arc",
    "uncertain_disciple":   "contrast_to_main_arc",
    "watcher":              "witness_function",
    "late_responder":       "delayed_echo",
}

DEFAULT_PRESSURES_BY_ARCHETYPE: dict[str, tuple[str, ...]] = {
    "loyal_under_pressure": ("authority_vigilance", "public_suspicion", "fear"),
    "uncertain_actor":      ("confusion", "fear"),
    "uncertain_disciple":   ("confusion", "fear"),
    "watcher":              ("public_suspicion",),
    "late_responder":       ("confusion",),
}

# Flow ordering priority (Plan §E.3)
_FLOW_ROLE_ORDER: tuple[str, ...] = (
    "main_arc",
    "witness_arc",
    "supporting_uncertainty",
    "delayed_response_arc",
)


# ---------------------------------------------------------------------------
# Pressure phrase → taxonomy id mapping
# ---------------------------------------------------------------------------

_PHRASE_TO_PRESSURE: dict[str, str] = {
    "fear intensifies":             "fear",
    "fear eases":                   "fear",
    "hope steadies":                "hope",
    "resolve weakens":              "hope",
    "shame accumulates":            "shame_self",
    "shame relaxes":                "shame_self",
    "authority pressure closes in": "authority_vigilance",
    "authority pressure recedes":   "authority_vigilance",
    "public suspicion rises":       "public_suspicion",
    "public suspicion settles":     "public_suspicion",
    "blame begins to concentrate":  "blame_concentration",
    "blame disperses":              "blame_concentration",
    "group tension sharpens":       "group_tension",
    "group tension softens":        "group_tension",
    # crowd_mood는 pressure가 아니라 environmental_state. 명백한 압력 표현이
    # 있을 때만 crowd_tension으로 매핑.
    "crowd hostility rises":        "crowd_tension",
    "crowd turns aggressive":       "crowd_tension",
}


def map_pressure_phrases(
    phrases: tuple[str, ...] | list[str],
) -> tuple[list[str], list[str]]:
    """Phase 2.5 §D.4: silent failure 방지. (mapped, unmapped) 둘 다 반환."""
    mapped: list[str] = []
    unmapped: list[str] = []
    for p in phrases:
        pid = _PHRASE_TO_PRESSURE.get(p)
        if pid:
            if pid not in mapped:
                mapped.append(pid)
        else:
            unmapped.append(p)
    return mapped, unmapped


def _phrases_to_pressure_ids(phrases: tuple[str, ...] | list[str]) -> list[str]:
    """Backward-compat helper. 새 코드는 map_pressure_phrases 사용."""
    mapped, _ = map_pressure_phrases(phrases)
    return mapped


# ---------------------------------------------------------------------------
# Conflict axis → pressures + desires
# ---------------------------------------------------------------------------

def _desires_for_conflict(conflict_axis_id: str) -> list[str]:
    axes = load_conflict_axes()
    axis = axes.get(conflict_axis_id)
    if not axis:
        return []
    out: list[str] = []
    for pole_key in ("pole_a", "pole_b"):
        pole = axis.get(pole_key)
        if pole and pole.get("kind") == "desire":
            out.append(pole["id"])
    return out


def _pressures_from_conflict_axis(conflict_axis_id: str) -> list[str]:
    """Phase 2.5 §D.3 tier 2: conflict axis pole에서 pressure 추출."""
    axes = load_conflict_axes()
    axis = axes.get(conflict_axis_id)
    if not axis:
        return []
    out: list[str] = []
    for pole_key in ("pole_a", "pole_b"):
        pole = axis.get(pole_key)
        if pole and pole.get("kind") == "pressure":
            out.append(pole["id"])
    return out


def _default_pressures_for_archetype(archetype: str) -> list[str]:
    """Phase 2.5 §D.3 tier 3: archetype별 기본 pressure."""
    return list(DEFAULT_PRESSURES_BY_ARCHETYPE.get(archetype, ()))


def infer_pressures(
    candidate_phrases: tuple[str, ...] | list[str],
    conflict_axis_id: str,
    archetype: str,
) -> tuple[list[str], list[str], str]:
    """Phase 2.5 §D.3: 4-tier pressure fallback.

    Returns:
        (pressures, unmapped_phrases, fallback_tier_used)
        fallback_tier_used: "phrase" | "conflict_axis" | "archetype_default" |
                            "audit_empty"
    """
    mapped, unmapped = map_pressure_phrases(candidate_phrases)
    if mapped:
        return mapped, unmapped, "phrase"

    axis_pressures = _pressures_from_conflict_axis(conflict_axis_id)
    if axis_pressures:
        return axis_pressures, unmapped, "conflict_axis"

    arch_default = _default_pressures_for_archetype(archetype)
    if arch_default:
        return arch_default, unmapped, "archetype_default"

    return [], unmapped, "audit_empty"


# ---------------------------------------------------------------------------
# Adapter (per-seed conversion)
# ---------------------------------------------------------------------------

def candidate_to_universal_seed(
    candidate,                   # StoryCandidate
    seed_card,                   # StorySeedCard
    archetype: str,              # 필수 (Phase 2.5 §D.2.1)
    *,
    role: str = "",
    supporting_archetypes: tuple[str, ...] = (),
    flow_role: str = "",
    audit_collector: dict | None = None,  # 누적 audit 정보 받음
) -> UniversalStorySeed:
    """Convert a (StoryCandidate, StorySeedCard) pair into a UniversalStorySeed v1.1.

    Phase 2.5 §D: lossless conversion.
    """
    if not archetype:
        raise ValueError(
            "candidate_to_universal_seed: archetype is required for lossless "
            "conversion (Phase 2.5 §D.2.1)"
        )

    conflict = candidate.core_conflict or "unknown"

    # 4-tier pressure fallback
    pressures, unmapped, tier = infer_pressures(
        candidate.world_pressure_context, conflict, archetype,
    )
    desires = _desires_for_conflict(conflict)

    # supporting_roles: archetype lookup, no placeholder
    supporting_roles = tuple(
        MAIN_ROLE_BY_ARCHETYPE.get(a, a) for a in supporting_archetypes
    )

    # main_role lookup
    main_role = role or MAIN_ROLE_BY_ARCHETYPE.get(archetype, archetype)

    # change_pattern / arc_direction / relationship_function lookup
    change_pattern = CHANGE_PATTERN_BY_ARCHETYPE.get(archetype, "")
    arc_direction = ARC_DIRECTION_BY_ARCHETYPE.get(archetype, "")
    relationship_function = RELATIONSHIP_FUNCTION_BY_ARCHETYPE.get(archetype, "")

    # turning_points_count
    tp_count = 0
    if hasattr(candidate, "key_turning_points") and candidate.key_turning_points:
        tp_count = len(candidate.key_turning_points)

    # qualitative pressure_pattern (deprecated v1 호환용)
    pattern: dict[str, Any] = {}
    if tp_count:
        pattern["turning_points_count"] = tp_count
    if pressures:
        pattern["primary_pressure"] = pressures[0]
    if desires:
        pattern["primary_desire"] = desires[0]
    if tier != "phrase":
        pattern["pressure_fallback_tier"] = tier

    # Audit collector (caller가 dict 제공하면 누적)
    if audit_collector is not None:
        if unmapped:
            audit_collector.setdefault("unmapped_pressure_phrases", []).extend(unmapped)
        if tier == "audit_empty":
            audit_collector.setdefault("missing_pressure_seeds", []).append(seed_card.seed_id)
        if conflict == "unknown":
            audit_collector["unknown_axis_count"] = (
                audit_collector.get("unknown_axis_count", 0) + 1
            )

    return UniversalStorySeed(
        seed_id=seed_card.seed_id,
        conflict_axis_id=conflict,
        main_role=main_role,
        main_archetype=archetype,
        dominant_pressures=tuple(pressures),
        dominant_desires=tuple(desires),
        supporting_archetypes=supporting_archetypes,
        supporting_roles=supporting_roles,
        pressure_pattern=pattern,
        change_pattern=change_pattern,
        arc_direction=arc_direction,
        relationship_function=relationship_function,
        flow_role=flow_role,
        turning_points_count=tp_count,
        confidence_label=getattr(seed_card, "confidence_label", ""),
        audit_status=getattr(seed_card.evidence_summary, "audit_status", "pass"),
        evidence_count=getattr(seed_card.evidence_summary, "evidence_count", 0),
        notes=(),
    )


# ---------------------------------------------------------------------------
# Skeleton output assembly (Phase 2.5 lossless + auto-flow)
# ---------------------------------------------------------------------------

def _resolve_archetype_map(
    seed_ids: list[str],
    archetype_by_seed: dict[str, str] | None,
) -> dict[str, str]:
    """Phase 2.5 §D.2.1: archetype_by_seed는 필수. None 또는 빈 dict면 default.
    그래도 모든 seed가 매핑돼야 — 누락 시 ValueError."""
    resolved = dict(archetype_by_seed or {})
    # default fill for known seed_ids
    for sid in seed_ids:
        if sid not in resolved and sid in DEFAULT_ARCHETYPE_BY_SEED:
            resolved[sid] = DEFAULT_ARCHETYPE_BY_SEED[sid]
    # validate full coverage
    missing = [sid for sid in seed_ids if sid not in resolved or not resolved[sid]]
    if missing:
        raise ValueError(
            f"archetype_by_seed missing entries for: {missing}. "
            "Phase 2.5 §D.2.1: archetype_by_seed is required for lossless conversion."
        )
    return resolved


def _build_default_flow(
    seeds: list[UniversalStorySeed],
) -> LifeStoryFlow:
    """Phase 2.5 §E: SkeletonOutput.flow는 null이 아니어야 함.

    정렬 우선순위 (§E.3):
        1. main_arc 먼저
        2. witness_arc
        3. supporting_uncertainty
        4. delayed_response_arc
        5. 나머지는 evidence_count 내림차순
    """
    role_priority = {role: i for i, role in enumerate(_FLOW_ROLE_ORDER)}
    fallback_priority = len(_FLOW_ROLE_ORDER)

    def sort_key(seed: UniversalStorySeed) -> tuple:
        prio = role_priority.get(seed.flow_role, fallback_priority)
        # secondary: evidence_count desc → use negative
        return (prio, -seed.evidence_count, seed.seed_id)

    ordered = sorted(seeds, key=sort_key)
    flow_roles = {
        s.seed_id: s.flow_role or FLOW_ROLE_BY_SEED.get(s.seed_id, "unspecified_arc")
        for s in seeds
    }

    return LifeStoryFlow(
        ordering="evidence_derived",
        ordered_seed_ids=tuple(s.seed_id for s in ordered),
        flow_roles=flow_roles,
    )


def assemble_skeleton_output(
    candidates: list,            # list[StoryCandidate]
    seed_cards: list,            # list[StorySeedCard]
    anchor_id: str,
    *,
    audits: list | None = None,
    archetype_by_seed: dict[str, str] | None = None,
    supporting_archetypes_by_seed: dict[str, tuple[str, ...]] | None = None,
    flow_role_by_seed: dict[str, str] | None = None,
    flow: LifeStoryFlow | None = None,
    fill_flow_default: bool = True,   # Phase 2.5 §E: default flow 생성
    strict_axis: bool = False,        # Phase 2.5 cycle 8 §B.2: assembly 시점 strict
) -> SkeletonOutput:
    """Pack candidates + seed_cards + audits into a frozen SkeletonOutput v1.1.

    Phase 2.5 §D + §E:
    - archetype_by_seed 필수 (None이면 DEFAULT_ARCHETYPE_BY_SEED + 누락 검증)
    - flow가 None이고 fill_flow_default=True면 자동 flow 생성
    - audit_trail에 unmapped phrase / missing pressure / unknown axis 누적
    - strict_axis=True (cycle 8): 입력 candidate에 unknown axis가 하나라도 있으면
      ValueError로 즉시 거부. plan §B.2의 "정상 SkeletonOutput에서는 unknown 금지"
      정책을 *assembly layer*에서 강제 (validate_skeleton_semantic은 *읽기* 시점
      검증, 이건 *쓰기* 시점 게이트).
    """
    seed_ids = [card.seed_id for card in seed_cards]
    resolved_archetypes = _resolve_archetype_map(seed_ids, archetype_by_seed)
    supporting_archetypes_by_seed = (
        supporting_archetypes_by_seed
        if supporting_archetypes_by_seed is not None
        else DEFAULT_SUPPORTING_ARCHETYPES_BY_SEED
    )
    flow_role_by_seed = flow_role_by_seed or FLOW_ROLE_BY_SEED

    audit_collector: dict[str, Any] = {}
    universal_seeds: list[UniversalStorySeed] = []
    unknown_axis_seeds: list[str] = []
    for cand, card in zip(candidates, seed_cards):
        archetype = resolved_archetypes[card.seed_id]
        supp = supporting_archetypes_by_seed.get(card.seed_id, ())
        flow_role = flow_role_by_seed.get(card.seed_id, "")
        seed = candidate_to_universal_seed(
            cand, card,
            archetype=archetype,
            supporting_archetypes=supp,
            flow_role=flow_role,
            audit_collector=audit_collector,
        )
        if seed.conflict_axis_id == "unknown":
            unknown_axis_seeds.append(seed.seed_id)
        universal_seeds.append(seed)

    if strict_axis and unknown_axis_seeds:
        raise ValueError(
            f"strict_axis=True: seeds with 'unknown' conflict axis are forbidden "
            f"in normal SkeletonOutput (Plan §B.2). Offenders: {unknown_axis_seeds}. "
            "Set strict_axis=False to allow with audit_trail.unknown_axis_count record."
        )

    # Evidence ledger
    audits = audits or []
    audit_pass = sum(1 for a in audits if getattr(a, "overall", "") == "pass")
    audit_risky = sum(1 for a in audits if getattr(a, "overall", "") == "risky")
    audit_fail = sum(1 for a in audits if getattr(a, "overall", "") == "audit_fail")
    signals_per_seed = {
        card.seed_id: card.evidence_summary.evidence_count
        for card in seed_cards
    }
    total_signals = sum(signals_per_seed.values())

    ledger = EvidenceLedger(
        total_signals=total_signals,
        signals_per_seed=signals_per_seed,
        audit_pass_count=audit_pass,
        audit_risky_count=audit_risky,
        audit_fail_count=audit_fail,
    )

    audit_trail = AuditTrail(
        stages_passed=("moments", "threads", "candidates", "seed_cards",
                        "scene_brief", "treatment", "viability", "audit"),
        unmapped_pressure_phrases=tuple(
            audit_collector.get("unmapped_pressure_phrases", [])
        ),
        missing_pressure_seeds=tuple(
            audit_collector.get("missing_pressure_seeds", [])
        ),
        unknown_axis_count=audit_collector.get("unknown_axis_count", 0),
    )

    metadata = AnchorMetadata(
        anchor_id=anchor_id,
    )

    if flow is None and fill_flow_default:
        flow = _build_default_flow(universal_seeds)

    return SkeletonOutput(
        seeds=tuple(universal_seeds),
        flow=flow,
        evidence_ledger=ledger,
        anchor_metadata=metadata,
        audit_trail=audit_trail,
    )


# ---------------------------------------------------------------------------
# Phase 2.5 §7: Semantic validator (Phase 3 Go gate)
# ---------------------------------------------------------------------------

import re as _re_validator

_SUPPORTING_PLACEHOLDER = _re_validator.compile(r"^supporting_\d+$")


def validate_skeleton_semantic(
    output: SkeletonOutput,
    *,
    strict: bool = True,
) -> list[str]:
    """Phase 2.5 §7 Phase 3 Go gate를 *코드*로 강제하는 validator.

    Returns:
        list of error messages. empty == 의미적 통과.

    strict=True 일 때 다음을 fail로 본다:
        - main_archetype 빈 seed
        - main_role == "main"
        - supporting_roles에 numeric placeholder
        - dominant_pressures 빈 채로 audit 기록 없음
        - unknown axis가 정상 seed로 통과
        - flow == None
        - flow_roles가 모든 seed 커버 안 함

    strict=False (lenient)일 때는 unknown axis와 missing pressure를 fail 대신
    note로 기록하고 통과시킨다.
    """
    errors: list[str] = []
    seeds = output.seeds
    audit = output.audit_trail
    missing_pressure_seeds = set(audit.missing_pressure_seeds or ())

    # Per-seed checks
    for seed in seeds:
        sid = seed.seed_id
        if not seed.main_archetype:
            errors.append(f"seed {sid}: empty main_archetype")
        if seed.main_role == "main":
            errors.append(f"seed {sid}: main_role placeholder ('main')")
        if not seed.main_role:
            errors.append(f"seed {sid}: empty main_role")
        for role in seed.supporting_roles:
            if _SUPPORTING_PLACEHOLDER.match(role):
                errors.append(
                    f"seed {sid}: supporting_roles contains numeric placeholder ({role!r})"
                )
        if not seed.dominant_pressures and sid not in missing_pressure_seeds:
            errors.append(
                f"seed {sid}: dominant_pressures empty without audit record "
                "(silent empty forbidden)"
            )
        if seed.conflict_axis_id == "unknown" and strict:
            errors.append(f"seed {sid}: unknown axis on normal seed (strict mode)")

    # Flow checks
    if output.flow is None:
        errors.append("SkeletonOutput.flow is None (Phase 2.5 §E)")
    else:
        seed_ids = {s.seed_id for s in seeds}
        flow_role_keys = set(output.flow.flow_roles.keys())
        missing = seed_ids - flow_role_keys
        if missing:
            errors.append(
                f"flow.flow_roles missing seeds: {sorted(missing)}"
            )

    return errors


def is_skeleton_phase3_ready(output: SkeletonOutput) -> tuple[bool, list[str]]:
    """Phase 3 ML 진입 가능 여부를 코드로 판정.

    Returns: (ready, errors). errors가 비어있으면 ready=True.
    """
    errors = validate_skeleton_semantic(output, strict=True)
    return (not errors), errors
