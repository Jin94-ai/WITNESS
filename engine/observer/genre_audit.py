"""Genre Audit — GenreAdaptedOutput 검증 (Phase 2.75 §11).

Per `docs/WITNESS_PHASE_2_75_GENRE_ADAPTER_MVP_PLAN.md` §11:
    1. Forbidden event audit
    2. Dialogue audit
    3. Evidence preservation audit
    4. Overreach audit (cross-check: 출력 본문이 rulebook의 forbidden_transformations
       ㅡ 출생의 비밀 등 ㅡ을 *추가*하지 않았는지)
    5. Source imitation audit
"""
from __future__ import annotations

from dataclasses import dataclass, field

from engine.observer.genre_adapter import GenreAdaptedOutput, GenreAdaptedSeed
from engine.observer.genre_rulebook import GenreAuditBlocklist


@dataclass(frozen=True)
class GenreAuditResult:
    schema_version: str
    genre_id: str
    overall: str                              # "pass" / "fail"
    forbidden_event_violations: tuple[str, ...]
    dialogue_violations: tuple[str, ...]
    source_imitation_violations: tuple[str, ...]
    evidence_violations: tuple[str, ...]
    quality_warnings: tuple[str, ...] = ()    # Phase 2.8: soft (warning, not fail)
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "genre_id": self.genre_id,
            "overall": self.overall,
            "forbidden_event_violations": list(self.forbidden_event_violations),
            "dialogue_violations": list(self.dialogue_violations),
            "source_imitation_violations": list(self.source_imitation_violations),
            "evidence_violations": list(self.evidence_violations),
            "quality_warnings": list(self.quality_warnings),
            "notes": list(self.notes),
        }


GENRE_AUDIT_VERSION = "genre_audit_result_v1_1"

# Phase 2.8 Issue 5: soft quality checks
_AWKWARD_JOSA_PATTERNS = ("이(가)", "을(를)", "은(는)", "에(에서)")


def _collect_output_text(out: GenreAdaptedOutput) -> list[tuple[str, str]]:
    """(location, text) 쌍 — audit가 검사해야 할 출력 본문 모음."""
    pairs: list[tuple[str, str]] = []
    for s in out.adapted_seeds:
        pairs.append((f"seed[{s.source_seed_id}].adapted_title_ko", s.adapted_title_ko))
        pairs.append((f"seed[{s.source_seed_id}].adapted_premise_ko", s.adapted_premise_ko))
        pairs.append((f"seed[{s.source_seed_id}].adapted_function_ko", s.adapted_function_ko))
        pairs.append((f"seed[{s.source_seed_id}].cliffhanger_ko", s.cliffhanger_ko))
    flow = out.adapted_flow
    pairs.append(("flow.title_ko", flow.title_ko))
    pairs.append(("flow.premise_ko", flow.premise_ko))
    pairs.append(("flow.cliffhanger_ko", flow.cliffhanger_ko))
    pairs.append(("flow.genre_lens_ko", flow.genre_lens_ko))
    for i, line in enumerate(flow.adapted_outline_ko):
        pairs.append((f"flow.adapted_outline_ko[{i}]", line))
    # Phase 2.8: structured outline lines (audit는 두 경로 모두 검사)
    for i, step in enumerate(flow.adapted_outline_steps):
        pairs.append((f"flow.adapted_outline_steps[{i}].line_ko", step.line_ko))
    return pairs


def _check_forbidden_events(
    pairs: list[tuple[str, str]], blocklist: GenreAuditBlocklist,
) -> list[str]:
    out: list[str] = []
    for loc, text in pairs:
        for token in blocklist.forbidden_event_tokens:
            if token and token in text:
                out.append(f"{loc}: forbidden event token {token!r}")
    return out


def _check_dialogue(
    pairs: list[tuple[str, str]], blocklist: GenreAuditBlocklist,
) -> list[str]:
    out: list[str] = []
    for loc, text in pairs:
        for marker in blocklist.forbidden_dialogue_markers:
            if marker and marker in text:
                out.append(f"{loc}: dialogue marker {marker!r}")
    return out


def _check_source_imitation(
    pairs: list[tuple[str, str]], blocklist: GenreAuditBlocklist,
) -> list[str]:
    out: list[str] = []
    for loc, text in pairs:
        for token in blocklist.forbidden_source_imitation:
            if token and token in text:
                out.append(f"{loc}: source imitation suspect {token!r}")
    return out


def _check_evidence_preservation(out: GenreAdaptedOutput) -> list[str]:
    """Plan §11.3: source_seed_id / source_conflict_axis_id / source_desires /
    source_pressures / source_flow_role 모두 보존되어야 한다."""
    violations: list[str] = []
    for s in out.adapted_seeds:
        if not s.source_seed_id:
            violations.append(f"adapted seed missing source_seed_id (adaptation_id={s.adaptation_id})")
        if not s.source_conflict_axis_id:
            violations.append(f"seed[{s.source_seed_id}]: empty source_conflict_axis_id")
        # transformation_level 강제
        if s.transformation_level != "structure_only":
            violations.append(
                f"seed[{s.source_seed_id}]: transformation_level "
                f"{s.transformation_level!r} != 'structure_only'"
            )
        if not s.evidence_preserved:
            violations.append(f"seed[{s.source_seed_id}]: evidence_preserved=False")
        if s.forbidden_added:
            violations.append(f"seed[{s.source_seed_id}]: forbidden_added=True")
    # flow의 source_ordered_seed_ids가 adapted_seeds와 동일 set이어야
    flow_ids = set(out.adapted_flow.source_ordered_seed_ids)
    seed_ids = {s.source_seed_id for s in out.adapted_seeds}
    if flow_ids != seed_ids:
        violations.append(
            f"flow.source_ordered_seed_ids != adapted seeds: "
            f"flow={sorted(flow_ids)}, seeds={sorted(seed_ids)}"
        )
    return violations


def _check_quality_warnings(out: GenreAdaptedOutput) -> list[str]:
    """Phase 2.8 Issue 5: soft warnings — fail 아니지만 polish 게이트 신호.

    체크:
        - awkward_josa_patterns (이(가) / 을(를) / 은(는)) 출력 본문 등장
        - duplicate outline lines (같은 line_ko 2회 이상)
        - repeated adapted_function in outline (같은 source_seed_id+function 반복)
        - empty genre lens
    """
    warnings: list[str] = []
    flow = out.adapted_flow

    # 1. awkward josa
    pairs = _collect_output_text(out)
    for loc, text in pairs:
        for pat in _AWKWARD_JOSA_PATTERNS:
            if pat in text:
                warnings.append(
                    f"{loc}: awkward josa placeholder {pat!r} (use proper "
                    "particle resolution)"
                )

    # 2. duplicate outline lines
    if flow.adapted_outline_steps:
        seen_lines: dict[str, int] = {}
        for step in flow.adapted_outline_steps:
            seen_lines[step.line_ko] = seen_lines.get(step.line_ko, 0) + 1
        for line, count in seen_lines.items():
            if count > 1:
                warnings.append(
                    f"adapted_outline_steps: line repeated {count}x: "
                    f"{line[:40]!r}..."
                )

    # 3. repeated adapted_function (legacy adapted_outline_ko)
    if flow.adapted_outline_ko:
        seen_func: dict[str, int] = {}
        for line in flow.adapted_outline_ko:
            seen_func[line] = seen_func.get(line, 0) + 1
        for line, count in seen_func.items():
            if count > 1:
                warnings.append(
                    f"adapted_outline_ko: identical line repeated {count}x"
                )

    # 4. empty genre lens
    if not flow.genre_lens_ko:
        warnings.append(
            "flow.genre_lens_ko is empty (Phase 2.8 Issue 3: rulebook should "
            "define genre_lens_ko for portfolio polish)"
        )

    return warnings


def audit_genre_output(
    out: GenreAdaptedOutput, blocklist: GenreAuditBlocklist,
) -> GenreAuditResult:
    """Phase 2.75 §11 모든 hard audit + Phase 2.8 soft quality_warnings.

    overall = pass / fail 은 *hard audit*만 결정. quality_warnings는 별도.
    """
    if out.genre_id != blocklist.genre_id:
        return GenreAuditResult(
            schema_version=GENRE_AUDIT_VERSION,
            genre_id=out.genre_id,
            overall="fail",
            forbidden_event_violations=(),
            dialogue_violations=(),
            source_imitation_violations=(),
            evidence_violations=(
                f"genre_id mismatch: output={out.genre_id} blocklist={blocklist.genre_id}",
            ),
            quality_warnings=(),
        )

    pairs = _collect_output_text(out)
    forbidden = _check_forbidden_events(pairs, blocklist)
    dialogue = _check_dialogue(pairs, blocklist)
    source = _check_source_imitation(pairs, blocklist)
    evidence = _check_evidence_preservation(out)
    quality = _check_quality_warnings(out)

    overall = "pass" if not (forbidden or dialogue or source or evidence) else "fail"

    return GenreAuditResult(
        schema_version=GENRE_AUDIT_VERSION,
        genre_id=out.genre_id,
        overall=overall,
        forbidden_event_violations=tuple(forbidden),
        dialogue_violations=tuple(dialogue),
        source_imitation_violations=tuple(source),
        evidence_violations=tuple(evidence),
        quality_warnings=tuple(quality),
    )
