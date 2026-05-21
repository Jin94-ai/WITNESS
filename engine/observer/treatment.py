"""1-page Treatment — Stage C (Story Viability Validation).

Per `docs/WITNESS_STORY_VIABILITY_VALIDATION_PLAN.md` §7.

Expands a SceneBrief into a 3-act 1-page treatment + adaptation notes.
Forbidden by plan §7: new events / new characters / dialogue / specific
actions / scriptural-historical details / over-narration. Allowed:
sequencing pressure changes, sharpening the scene question, mapping
turning points to acts, using unresolved_question as the hook.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.observer.scene_brief import SceneBrief
from engine.observer.story_candidate import StoryCandidate


@dataclass(frozen=True)
class Treatment:
    candidate_id: str
    premise: str
    act_1_setup: str
    act_2_pressure_build: str
    act_3_turn_consequence: str
    end_hook: str
    adaptation_notes: dict[str, str]   # film / novel / game → 1-line note
    treatment_completeness: str        # "complete" / "treatment_incomplete"
    missing_acts: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "candidate_id": self.candidate_id,
            "premise": self.premise,
            "act_1_setup": self.act_1_setup,
            "act_2_pressure_build": self.act_2_pressure_build,
            "act_3_turn_consequence": self.act_3_turn_consequence,
            "end_hook": self.end_hook,
            "adaptation_notes": dict(self.adaptation_notes),
            "treatment_completeness": self.treatment_completeness,
            "missing_acts": list(self.missing_acts),
        }


def _act_1_setup(c: StoryCandidate, brief: SceneBrief) -> str:
    main = brief.main_character
    group_label = c.supporting_characters_or_groups[-1] if c.supporting_characters_or_groups else "the surrounding group"
    return (
        f"{main} starts within {group_label}, "
        f"under the initial state described by the candidate ({brief.starting_state}). "
        f"The base pressures are present but not yet pivotal: "
        f"{', '.join(brief.internal_pressure) or '(no internal pressure flagged)'}."
    )


def _act_2_pressure_build(c: StoryCandidate, brief: SceneBrief) -> str:
    main = brief.main_character
    ext = ", ".join(brief.external_pressure) or "(no external pressure flagged)"
    relationships = "; ".join(c.relationship_dynamics) or "no directional relationship signal beyond group co-presence"
    return (
        f"External pressure builds across the run — {ext}. "
        f"Group-level context: {relationships}. "
        f"This is the accumulation phase: pressure layers, but {main} has not yet pivoted."
    )


def _act_3_turn_consequence(c: StoryCandidate, brief: SceneBrief) -> str:
    if not c.key_turning_points:
        return (
            "No categorized turning point in the source data; "
            "act 3 is the unresolved tension itself rather than a discrete shift."
        )
    # Pick strongest turning point (already prioritized in scene brief)
    return (
        f"Turning point: {brief.turning_point}. "
        f"After this moment, the candidate's arc resolves to: "
        f"{c.arc_summary.split('→')[-1].strip() if '→' in c.arc_summary else 'the final pressure state'}. "
        f"The shift is *visible in pressure data* but not necessarily in agent action — the engine "
        f"does not emit per-agent micro-action; the consequence is read from state fields."
    )


def _end_hook(c: StoryCandidate, brief: SceneBrief) -> str:
    return (
        f"Unresolved question — {c.unresolved_question} The run does not "
        f"answer this; the next scene / episode / branch begins here."
    )


def _adaptation_notes(c: StoryCandidate) -> dict[str, str]:
    """Re-use the candidate's existing adaptation_hooks and add format-aware caveats."""
    notes: dict[str, str] = {}
    hooks = c.adaptation_hooks or {}
    for fmt in ("film_scene", "novel_chapter", "game_quest_branch", "drama_episode",
                "documentary_segment", "short_story", "game_branch"):
        if fmt in hooks:
            label = {
                "film_scene": "Film",
                "novel_chapter": "Novel",
                "game_quest_branch": "Game",
                "drama_episode": "Drama",
                "documentary_segment": "Documentary",
                "short_story": "Short story",
                "game_branch": "Game",
            }[fmt]
            notes[label] = hooks[fmt]
    return notes


def build_treatment(c: StoryCandidate, brief: SceneBrief) -> Treatment:
    premise = c.one_line_premise
    act1 = _act_1_setup(c, brief)
    act2 = _act_2_pressure_build(c, brief)
    act3 = _act_3_turn_consequence(c, brief)
    hook = _end_hook(c, brief)
    notes = _adaptation_notes(c)

    missing: list[str] = []
    if not premise:
        missing.append("premise")
    if not act1:
        missing.append("act_1")
    if not act2:
        missing.append("act_2")
    if not act3:
        missing.append("act_3")
    if not hook:
        missing.append("end_hook")
    completeness = "treatment_incomplete" if missing else "complete"

    return Treatment(
        candidate_id=c.story_candidate_id,
        premise=premise,
        act_1_setup=act1,
        act_2_pressure_build=act2,
        act_3_turn_consequence=act3,
        end_hook=hook,
        adaptation_notes=notes,
        treatment_completeness=completeness,
        missing_acts=tuple(missing),
    )
