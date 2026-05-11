"""Genre Adapter — SkeletonOutput v1.1 → GenreAdaptedOutput (Phase 2.75).

Per `docs/WITNESS_PHASE_2_75_GENRE_ADAPTER_MVP_PLAN.md` §6 + §7:
    rule-based, structure-only 변환. 외부 의존 0.

원칙:
    - 원본 conflict_axis / dominant_pressures / dominant_desires 보존
    - role을 장르 역할로 매핑 (rulebook.role_mappings)
    - pressure를 장르 표현으로 변환 (rulebook.pressure_mappings)
    - flow를 episode_rhythm으로 정렬
    - cliffhanger 우선순위 기반 선택
    - transformation_level == "structure_only"
    - 없는 사건 추가 0, 대사 생성 0
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from engine.observer.genre_rulebook import (
    GenreRulebook,
    map_arc_direction_to_phrase,
    map_flow_role_to_function,
    map_pressure_to_genre,
    map_role_to_genre,
    select_amplifier,
    select_cliffhanger,
)
from engine.observer.skeleton_output import SkeletonOutput
from engine.observer.universal_story_seed import UniversalStorySeed


GENRE_ADAPTED_OUTPUT_VERSION = "genre_adapted_output_v1_1"
GENRE_ADAPTED_FLOW_VERSION = "genre_adapted_flow_v1_1"


# ---------------------------------------------------------------------------
# Dataclasses (Plan §6)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class GenreAdaptedSeed:
    adaptation_id: str
    source_seed_id: str
    genre_id: str

    source_conflict_axis_id: str
    source_desires: tuple[str, ...]
    source_pressures: tuple[str, ...]
    source_flow_role: str

    genre_role: str
    genre_pressure: tuple[str, ...]
    genre_conflict_amplifier: str

    adapted_title_ko: str
    adapted_premise_ko: str
    adapted_function_ko: str
    cliffhanger_ko: str

    transformation_level: str = "structure_only"
    evidence_preserved: bool = True
    forbidden_added: bool = False

    def to_dict(self) -> dict:
        return {
            "adaptation_id": self.adaptation_id,
            "source_seed_id": self.source_seed_id,
            "genre_id": self.genre_id,
            "source_conflict_axis_id": self.source_conflict_axis_id,
            "source_desires": list(self.source_desires),
            "source_pressures": list(self.source_pressures),
            "source_flow_role": self.source_flow_role,
            "genre_role": self.genre_role,
            "genre_pressure": list(self.genre_pressure),
            "genre_conflict_amplifier": self.genre_conflict_amplifier,
            "adapted_title_ko": self.adapted_title_ko,
            "adapted_premise_ko": self.adapted_premise_ko,
            "adapted_function_ko": self.adapted_function_ko,
            "cliffhanger_ko": self.cliffhanger_ko,
            "transformation_level": self.transformation_level,
            "evidence_preserved": self.evidence_preserved,
            "forbidden_added": self.forbidden_added,
        }


@dataclass(frozen=True)
class GenreAdaptedOutlineStep:
    """Phase 2.8 Issue 6: structured outline — rhythm step + seed link + Korean line."""
    step: str
    source_seed_id: str
    source_flow_role: str
    line_ko: str

    def to_dict(self) -> dict:
        return {
            "step": self.step,
            "source_seed_id": self.source_seed_id,
            "source_flow_role": self.source_flow_role,
            "line_ko": self.line_ko,
        }


@dataclass(frozen=True)
class GenreAdaptedFlow:
    schema_version: str
    adaptation_id: str
    genre_id: str
    source_ordered_seed_ids: tuple[str, ...]

    title_ko: str
    premise_ko: str
    genre_lens_ko: str                         # Phase 2.8 Issue 3: 장르 렌즈
    role_map: dict[str, str]                   # source_seed_id → genre_role
    episode_rhythm: tuple[str, ...]
    adapted_outline_ko: tuple[str, ...]        # backward-compat (free-form)
    adapted_outline_steps: tuple[GenreAdaptedOutlineStep, ...]
                                                # Phase 2.8 v1.1: structured
    cliffhanger_ko: str

    evidence_summary: dict = field(default_factory=dict)
    audit_status: str = "pass"

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "adaptation_id": self.adaptation_id,
            "genre_id": self.genre_id,
            "source_ordered_seed_ids": list(self.source_ordered_seed_ids),
            "title_ko": self.title_ko,
            "premise_ko": self.premise_ko,
            "genre_lens_ko": self.genre_lens_ko,
            "role_map": dict(self.role_map),
            "episode_rhythm": list(self.episode_rhythm),
            "adapted_outline_ko": list(self.adapted_outline_ko),
            "adapted_outline_steps": [s.to_dict() for s in self.adapted_outline_steps],
            "cliffhanger_ko": self.cliffhanger_ko,
            "evidence_summary": dict(self.evidence_summary),
            "audit_status": self.audit_status,
        }


@dataclass(frozen=True)
class GenreAdaptedOutput:
    schema_version: str
    genre_id: str
    source_skeleton_version: str
    source_seed_ids: tuple[str, ...]
    adapted_seeds: tuple[GenreAdaptedSeed, ...]
    adapted_flow: GenreAdaptedFlow
    audit: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "genre_id": self.genre_id,
            "source_skeleton_version": self.source_skeleton_version,
            "source_seed_ids": list(self.source_seed_ids),
            "adapted_seeds": [s.to_dict() for s in self.adapted_seeds],
            "adapted_flow": self.adapted_flow.to_dict(),
            "audit": dict(self.audit),
        }


# ---------------------------------------------------------------------------
# Per-seed transformation (§7.1)
# ---------------------------------------------------------------------------

def _adapt_seed(
    seed: UniversalStorySeed, rulebook: GenreRulebook,
) -> GenreAdaptedSeed:
    amplifier = select_amplifier(rulebook, seed.conflict_axis_id)
    amp_id = amplifier.id if amplifier else "no_amplifier"
    amp_desc = amplifier.description_ko if amplifier else "장르 매칭 없음"

    genre_role = map_role_to_genre(rulebook, seed.main_role)
    genre_pressure = tuple(
        map_pressure_to_genre(rulebook, p) for p in seed.dominant_pressures
    )

    # adapted_title_ko: archetype + amplifier 결합 (작품-specific 텍스트 0)
    adapted_title_ko = f"{genre_role} — {amp_desc}"

    # adapted_premise_ko: 원본 arc_direction을 보존하며 장르 압력 표현
    pressure_phrase = (
        ", ".join(genre_pressure) if genre_pressure else "내부 압력"
    )
    arc_phrase = map_arc_direction_to_phrase(rulebook, seed.arc_direction)
    adapted_premise_ko = (
        f"{genre_role}이 {pressure_phrase} 속에서 "
        f"{arc_phrase}."
    )

    # adapted_function_ko: 장르적 기능 (변환 결과가 다음 회차에 어떻게 작용하는가)
    adapted_function_ko = _function_phrase(seed, amplifier, rulebook)

    # 개별 cliffhanger (per-seed 보조)
    cliff = select_cliffhanger(
        rulebook,
        conflict_axis_ids=(seed.conflict_axis_id,),
        main_roles=(seed.main_role,),
    )

    return GenreAdaptedSeed(
        adaptation_id=f"{seed.seed_id}__{rulebook.genre_id}",
        source_seed_id=seed.seed_id,
        genre_id=rulebook.genre_id,
        source_conflict_axis_id=seed.conflict_axis_id,
        source_desires=tuple(seed.dominant_desires),
        source_pressures=tuple(seed.dominant_pressures),
        source_flow_role=seed.flow_role,
        genre_role=genre_role,
        genre_pressure=genre_pressure,
        genre_conflict_amplifier=amp_id,
        adapted_title_ko=adapted_title_ko,
        adapted_premise_ko=adapted_premise_ko,
        adapted_function_ko=adapted_function_ko,
        cliffhanger_ko=cliff.description_ko,
    )


def _function_phrase(
    seed: UniversalStorySeed, amplifier, rulebook: GenreRulebook,
) -> str:
    """flow_role → 장르별 기능 phrasing.

    Phase 2.75 cycle 5: rulebook.flow_role_function_phrases가 우선. 그 다음
    amplifier.description_ko (있으면). 마지막은 generic fallback.
    """
    if seed.flow_role and seed.flow_role in rulebook.flow_role_function_phrases:
        return rulebook.flow_role_function_phrases[seed.flow_role]
    if amplifier:
        return amplifier.description_ko
    return map_flow_role_to_function(rulebook, seed.flow_role)


# ---------------------------------------------------------------------------
# Flow transformation (§7.2)
# ---------------------------------------------------------------------------

def _build_flow(
    skeleton: SkeletonOutput,
    rulebook: GenreRulebook,
    adapted_seeds: tuple[GenreAdaptedSeed, ...],
) -> GenreAdaptedFlow:
    if skeleton.flow is None:
        # SkeletonOutput.flow가 null이면 어댑터가 만들 수 없음 (Phase 2.5 §E 위배)
        raise ValueError(
            "GenreAdapter requires SkeletonOutput.flow != None. "
            "Re-assemble skeleton with fill_flow_default=True."
        )

    ordered_ids = tuple(skeleton.flow.ordered_seed_ids)
    by_id = {s.source_seed_id: s for s in adapted_seeds}
    role_map = {sid: by_id[sid].genre_role for sid in ordered_ids if sid in by_id}

    # main seed 기준 cliffhanger (전체 flow의 끝)
    main_seeds = [
        s for s in skeleton.seeds if s.flow_role == "main_arc"
    ] or list(skeleton.seeds)
    conflict_ids = tuple(s.conflict_axis_id for s in main_seeds)
    main_roles = tuple(s.main_role for s in main_seeds)
    cliff = select_cliffhanger(
        rulebook, conflict_axis_ids=conflict_ids, main_roles=main_roles,
    )

    # Phase 2.8 Issue 1+6: structured outline (rhythm × role × phase template)
    rhythm = rulebook.episode_rhythm
    outline_steps = _build_structured_outline(
        rhythm, ordered_ids, by_id, rulebook, cliff.description_ko,
    )
    # backward-compat: free-form list[str]
    outline_lines = tuple(
        f"{i+1}. {step.step} — {step.line_ko}"
        for i, step in enumerate(outline_steps)
    )

    # title / premise: 장르 + 메인 갈등 표현 (작품 0)
    main_seed = main_seeds[0] if main_seeds else None
    if main_seed:
        title_ko = (
            f"{rulebook.display_name_ko}: "
            f"{by_id.get(main_seed.seed_id).genre_role if main_seed.seed_id in by_id else main_seed.main_role} 이야기"
        )
        premise_ko = (
            by_id.get(main_seed.seed_id).adapted_premise_ko
            if main_seed.seed_id in by_id
            else "장르 어댑터 결과"
        )
    else:
        title_ko = rulebook.display_name_ko
        premise_ko = ""

    evidence_summary = {
        "source_seed_count": len(skeleton.seeds),
        "preserved_conflict_axes": sorted({s.conflict_axis_id for s in skeleton.seeds}),
        "preserved_pressures": sorted({
            p for s in skeleton.seeds for p in s.dominant_pressures
        }),
        "preserved_desires": sorted({
            d for s in skeleton.seeds for d in s.dominant_desires
        }),
    }

    return GenreAdaptedFlow(
        schema_version=GENRE_ADAPTED_FLOW_VERSION,
        adaptation_id=f"flow__{rulebook.genre_id}",
        genre_id=rulebook.genre_id,
        source_ordered_seed_ids=ordered_ids,
        title_ko=title_ko,
        premise_ko=premise_ko,
        genre_lens_ko=rulebook.genre_lens_ko,
        role_map=role_map,
        episode_rhythm=rhythm,
        adapted_outline_ko=outline_lines,
        adapted_outline_steps=outline_steps,
        cliffhanger_ko=cliff.description_ko,
        evidence_summary=evidence_summary,
    )


def _select_seed_for_role(
    role: str,
    ordered_ids: tuple[str, ...],
    by_id: dict[str, GenreAdaptedSeed],
) -> GenreAdaptedSeed | None:
    """ordered_ids 에서 source_flow_role == role 인 첫 seed."""
    for sid in ordered_ids:
        seed = by_id.get(sid)
        if seed is not None and seed.source_flow_role == role:
            return seed
    return None


def _build_structured_outline(
    rhythm: tuple[str, ...],
    ordered_ids: tuple[str, ...],
    by_id: dict[str, GenreAdaptedSeed],
    rulebook: GenreRulebook,
    cliffhanger_ko: str,
) -> tuple[GenreAdaptedOutlineStep, ...]:
    """Phase 2.8 Issue 1+6: structured outline.

    각 rhythm step에 대해:
        - outline_step_mapping → phase ("early"/"middle"/"late")
        - outline_role_assignment_priority[i] → 어떤 source_flow_role을 쓸지
        - outline_templates[role][phase] → template string
        - {role}/{pressure} 치환 → 한 줄
    마지막 step은 outline_final_step_uses_cliffhanger=True면 cliffhanger 문장.
    """
    if not rhythm:
        return ()

    steps: list[GenreAdaptedOutlineStep] = []
    n_rhythm = len(rhythm)
    role_priority = rulebook.outline_role_assignment_priority

    for i, step in enumerate(rhythm):
        # 마지막 step + cliffhanger fallback
        is_last = (i == n_rhythm - 1)
        if is_last and rulebook.outline_final_step_uses_cliffhanger and cliffhanger_ko:
            # fallback seed: main_arc 또는 첫 seed
            seed = (_select_seed_for_role("main_arc", ordered_ids, by_id)
                    or (by_id.get(ordered_ids[0]) if ordered_ids else None))
            if seed is not None:
                steps.append(GenreAdaptedOutlineStep(
                    step=step,
                    source_seed_id=seed.source_seed_id,
                    source_flow_role=seed.source_flow_role,
                    line_ko=cliffhanger_ko,
                ))
                continue

        # role assignment
        target_role = (
            role_priority[i] if i < len(role_priority) else "main_arc"
        )
        seed = _select_seed_for_role(target_role, ordered_ids, by_id)
        # Fallback: 첫 seed
        if seed is None and ordered_ids:
            seed = by_id.get(ordered_ids[0])
        if seed is None:
            steps.append(GenreAdaptedOutlineStep(
                step=step, source_seed_id="", source_flow_role="",
                line_ko=step,
            ))
            continue

        # phase
        phase = rulebook.outline_step_mapping.get(step, "middle")
        templates = rulebook.outline_templates.get(seed.source_flow_role, {})
        template = templates.get(phase) or templates.get("middle") or ""
        if not template:
            # Fallback: 기존 function phrasing
            line = seed.adapted_function_ko or step
        else:
            pressure_phrase = (
                seed.genre_pressure[0] if seed.genre_pressure else "내부 압력"
            )
            line = template.format(
                role=seed.genre_role,
                pressure=pressure_phrase,
            )

        steps.append(GenreAdaptedOutlineStep(
            step=step,
            source_seed_id=seed.source_seed_id,
            source_flow_role=seed.source_flow_role,
            line_ko=line,
        ))

    return tuple(steps)


# ---------------------------------------------------------------------------
# Top-level adapter
# ---------------------------------------------------------------------------

def adapt_skeleton_to_genre(
    skeleton: SkeletonOutput,
    rulebook: GenreRulebook,
) -> GenreAdaptedOutput:
    """SkeletonOutput v1.1 + rulebook → GenreAdaptedOutput.

    Plan §4.1 입력 조건:
        - flow != null
        - audit_trail.unknown_axis_count == 0
        - audit_trail.forbidden_event_additions == 0
        - audit_trail.forbidden_dialogue_generation == 0
    """
    # 입력 게이트
    if skeleton.flow is None:
        raise ValueError("input skeleton.flow is None (Phase 2.75 §4.1 violation)")
    at = skeleton.audit_trail
    if at.unknown_axis_count > 0:
        raise ValueError(
            f"input skeleton has unknown_axis_count={at.unknown_axis_count}"
            " (Phase 2.75 §4.1 violation; re-assemble with strict_axis=True)"
        )
    if at.forbidden_event_additions > 0:
        raise ValueError("input skeleton has forbidden_event_additions > 0")
    if at.forbidden_dialogue_generation > 0:
        raise ValueError("input skeleton has forbidden_dialogue_generation > 0")

    adapted_seeds = tuple(_adapt_seed(s, rulebook) for s in skeleton.seeds)
    adapted_flow = _build_flow(skeleton, rulebook, adapted_seeds)

    return GenreAdaptedOutput(
        schema_version=GENRE_ADAPTED_OUTPUT_VERSION,
        genre_id=rulebook.genre_id,
        source_skeleton_version=skeleton.schema_version,
        source_seed_ids=tuple(s.seed_id for s in skeleton.seeds),
        adapted_seeds=adapted_seeds,
        adapted_flow=adapted_flow,
    )
