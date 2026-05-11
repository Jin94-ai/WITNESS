"""Rubric Runner CLI — 4-Axis Discovery Candidate Classifier 실행 (Phase 3.05).

Per `docs/witness_rubric_design.md` + `docs/WITNESS_V3_RUBRIC_DESIGN_REVIEW.md`.

목표:
    Trajectory records JSON → RubricReport (discovery_class + 6 sub-reports).
    `--md-report` 옵션으로 사람이 읽기 좋은 markdown 보고서도 생성.

원칙:
    - Rule #14: rubric은 evaluation-only — 학습 loss 사용 0
    - scalar 합산 0 (4 critic report independent 유지)
    - threshold는 uncalibrated_phase3_placeholder
    - 최종 label은 *truth claim*이 아니라 *discovery candidate class*로 해석

사용:
    python scripts/rubric/run_rubric.py \\
        --records data/trace_example.json \\
        --canonical-sequence "[[1, \\"pray\\"], [2, \\"follow_closely\\"]]" \\
        --vocabulary "pray follow_closely deny weep" \\
        --output rubric_report.json \\
        --md-report rubric_report.md

Exit:
    0 — 정상 (discovery_class와 무관)
    1 — runtime error
    2 — 입력 누락 / 형식 오류
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.constraint.hard_constraints import HardConstraintChecker  # noqa: E402
from engine.constraint.soft_constraints import SoftConstraintScorer  # noqa: E402
from engine.rubric import (  # noqa: E402
    CanonCritic,
    CausalCritic,
    CharacterCritic,
    ContextBreakCritic,
    DiscoveryClass,
    NoveltyCritic,
    RubricEvaluator,
    SceneResponseCritic,
)


def _force_utf8_stdout() -> None:
    if hasattr(sys.stdout, "buffer"):
        try:
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace",
            )
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, encoding="utf-8", errors="replace",
            )
        except Exception:
            pass


def load_records(path: Path) -> list[dict]:
    """JSON 파일에서 records list 로드."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and "records" in raw:
        return raw["records"]
    if isinstance(raw, list):
        return raw
    raise ValueError(
        f"records JSON 형식 오류: list 또는 {{records: [...]}} 필요, got {type(raw).__name__}",
    )


def build_evaluator(
    *,
    canonical_sequence: list[tuple[int, str]] | None = None,
    vocabulary: set[str] | None = None,
    reproduction_threshold: float = 2.0,
    action_pressure_map: dict[str, list[str]] | None = None,
) -> RubricEvaluator:
    """Phase 3.05 review §2.7 — uncalibrated placeholder thresholds로 평가기 생성.

    Phase 3.05 review §2.5 P1 extended (cycle 16+20): action_pressure_map 전달 시
    CausalCritic이 pressure-action alignment를 측정하고 gate에 반영.
    """
    hard = HardConstraintChecker(action_vocabulary=vocabulary or set())
    soft = SoftConstraintScorer(canonical_sequence=canonical_sequence or [])
    causal_kwargs: dict = {}
    if action_pressure_map:
        causal_kwargs["action_pressure_map"] = action_pressure_map
    return RubricEvaluator(
        character=CharacterCritic(),
        scene_response=SceneResponseCritic(),
        context_break=ContextBreakCritic(),
        canon=CanonCritic(
            hard=hard, soft=soft, reproduction_threshold=reproduction_threshold,
        ),
        causal=CausalCritic(**causal_kwargs),
        novelty=NoveltyCritic(),
    )


def report_to_dict(rep) -> dict:
    """RubricReport → dict (JSON 직렬화용).

    Phase 3.05 review §2.4 / §2.6 (cycle 27/28): sub-report dataclass의 *모든*
    @property alias 필드 (`copy_like` / `noise_like` / `structured_difference_score` /
    `hard_pass` / 등)를 자동 surface. `__dict__` 만 사용하면 properties가 skip되어
    deployed report에 review alias가 누락되는 stranded 패턴 (L84) 해소.

    cycle 28 generalization: 명시 list 없이 @property descriptor를 *generic*하게 walk —
    향후 추가되는 @property aliases도 자동 surface (L85 detector pattern).
    """
    # Generic walker — instance __dict__ + class @property descriptors 둘 다 포함.
    def _to_dict(obj):
        if isinstance(obj, DiscoveryClass):
            return obj.value
        if isinstance(obj, (list, tuple)):
            return [_to_dict(x) for x in obj]
        if isinstance(obj, dict):
            return {k: _to_dict(v) for k, v in obj.items()}
        if hasattr(obj, "__dict__"):
            result = {k: _to_dict(v) for k, v in obj.__dict__.items()}
            # Surface @property descriptors (review alias 필드 자동 포함).
            cls = type(obj)
            for name in dir(cls):
                if name.startswith("_") or name in result:
                    continue
                descriptor = getattr(cls, name, None)
                if isinstance(descriptor, property):
                    try:
                        val = getattr(obj, name)
                    except Exception:
                        continue
                    result[name] = _to_dict(val)
            return result
        return obj

    return {
        "discovery_class": rep.discovery_class.value,
        "character": _to_dict(rep.character),
        "scene_response": _to_dict(rep.scene_response),
        "context_break": _to_dict(rep.context_break),
        "canon": _to_dict(rep.canon),
        "causal": _to_dict(rep.causal),
        "novelty": _to_dict(rep.novelty),
        "justification": list(rep.justification),
    }


def render_markdown(report_dict: dict, *, n_records: int) -> str:
    """RubricReport → markdown 보고서.

    Phase 3.05 review §3: candidate class로 표현. truth claim 회피.
    """
    lines = []
    lines.append("# WITNESS Rubric Evaluation Report (Phase 3.05)")
    lines.append("")
    lines.append(f"> Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"> Tool: `scripts/rubric/run_rubric.py`")
    lines.append(f"> Trajectory length: {n_records} records")
    lines.append("")
    lines.append("## Non-Claims")
    lines.append("")
    lines.append("이 보고서는 신학적/문학적 *진실*을 증명하지 않는다. ")
    lines.append("생성된 trajectory가 (1) canon-compatible, (2) causally explainable, ")
    lines.append("(3) trait-consistent, (4) non-copy/non-noise인지 *분류*한다.")
    lines.append("최종 label은 **discovery candidate class**로 해석.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Discovery Classification")
    lines.append("")
    lines.append(f"**discovery_class**: `{report_dict['discovery_class']}`")
    lines.append("")
    lines.append("### Justification")
    lines.append("")
    for j in report_dict.get("justification", []):
        lines.append(f"- {j}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 6 Sub-Reports (axis별 독립)")
    lines.append("")

    # Character
    char = report_dict.get("character", {})
    lines.append("### Character (review §2.3 minimum gate)")
    lines.append(f"- relation_stability: {char.get('relation_stability', 0):.3f}")
    lines.append(f"- identity_retention: {char.get('identity_retention', 0):.3f}")
    lines.append(f"- recovery_plausibility: {char.get('recovery_plausibility', 0):.3f}")
    lines.append(f"- composite (display only): {char.get('composite', 0):.3f}")
    lines.append(f"- **passed_minimum_signature**: `{char.get('passed_minimum_signature', '?')}`")
    weak = char.get("weak_axes", [])
    lines.append(f"- weak_axes: {list(weak) if weak else '없음'}")
    lines.append("")

    # Causal
    causal = report_dict.get("causal", {})
    lines.append("### Causal (review §2.5 gate)")
    lines.append(f"- explained_transition_ratio: {causal.get('explained_transition_ratio', 0):.3f}")
    lines.append(f"- unexplained_jumps: {causal.get('unexplained_jumps', 0)}")
    lines.append(f"- smoothness_score: {causal.get('smoothness_score', 0):.3f}")
    lines.append(f"- **passed_causal_gate**: `{causal.get('passed_causal_gate', '?')}`")
    lines.append("")

    # Novelty
    novelty = report_dict.get("novelty", {})
    lines.append("### Novelty (review §2.4 structured difference)")
    lines.append(f"- novelty_band: `{novelty.get('novelty_band', '?')}`")
    lines.append(f"- structured_deviation: {novelty.get('structured_deviation', 0):.3f}")
    changed = novelty.get("changed_axes", [])
    lines.append(f"- changed_axes: {list(changed) if changed else '없음'}")
    if novelty.get("interpretation"):
        lines.append(f"- interpretation: {novelty['interpretation']}")
    lines.append("")

    # Canon
    canon = report_dict.get("canon", {})
    lines.append("### Canon (review §2.6 hard/soft 분리)")
    lines.append(f"- is_canon_valid (hard_pass): `{canon.get('is_canon_valid', '?')}`")
    lines.append(f"- hard_violations: {len(canon.get('hard_violations', []))}건")
    lines.append(f"- soft_drift: {canon.get('soft_drift', 0):.3f}")
    lines.append(f"- soft_compatibility_score: {canon.get('soft_compatibility_score', 0):.3f}")
    lines.append(f"- is_canon_reproducing: `{canon.get('is_canon_reproducing', '?')}`")
    lines.append("")

    # Scene + Context (보조)
    scene = report_dict.get("scene_response", {})
    ctx = report_dict.get("context_break", {})
    lines.append("### Scene Response")
    lines.append(f"- fit_rate: {scene.get('fit_rate', 0):.3f}")
    lines.append("")
    lines.append("### Context Break")
    lines.append(f"- break_rate: {ctx.get('break_rate', 0):.3f}")
    lines.append(f"- is_context_coherent: `{ctx.get('is_context_coherent', '?')}`")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Calibration Status")
    lines.append("")
    lines.append("모든 critic threshold는 **uncalibrated_phase3_placeholder** — Phase 5+ 실측 trajectory로 보정 필요.")
    lines.append("")
    lines.append("## Rule #14 Compliance")
    lines.append("")
    lines.append("- Rubric은 evaluation-only (학습 loss 사용 0)")
    lines.append("- scalar 합산 0 (4 critic report independent 유지)")
    lines.append("- final label은 candidate class — truth claim 아님")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--records", required=True, type=Path,
                     help="trajectory records JSON 경로")
    ap.add_argument("--output", required=True, type=Path,
                     help="RubricReport JSON output 경로")
    ap.add_argument("--md-report", type=Path, default=None,
                     help="markdown 보고서 output 경로 (옵션)")
    ap.add_argument("--canonical-sequence", type=str, default="[]",
                     help='canonical sequence JSON ([[tick, action], ...]). default: 빈 list')
    ap.add_argument("--vocabulary", type=str, default="",
                     help="hard constraint action vocabulary (space-separated). default: 빈 set (모두 허용)")
    ap.add_argument("--reproduction-threshold", type=float, default=2.0,
                     help="canon reproduction threshold (uncalibrated, default 2.0)")
    ap.add_argument("--is-all-hardcoded", action="store_true",
                     help="모든 event가 hardcoded firing이면 → NOT_DISCOVERY_HARDCODED")
    ap.add_argument("--action-pressure-map", type=Path, default=None,
                     help="action→[pressure_field,...] JSON 매핑 (cycle 16, review §2.5 alignment). "
                          "제공 시 CausalCritic이 pressure-action alignment를 측정하고 gate에 반영")
    args = ap.parse_args(argv)

    if not args.records.exists():
        print(f"ERROR: records 파일 미존재: {args.records}", file=sys.stderr)
        return 2

    try:
        records = load_records(args.records)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"ERROR: records 로드 실패: {e}", file=sys.stderr)
        return 2

    # canonical_sequence 파싱
    try:
        canon_raw = json.loads(args.canonical_sequence)
        if not isinstance(canon_raw, list):
            raise ValueError("canonical-sequence는 list여야 함")
        canon_seq = [(int(t), str(a)) for t, a in canon_raw]
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        print(f"ERROR: canonical-sequence 파싱 실패: {e}", file=sys.stderr)
        return 2

    vocab = set(args.vocabulary.split()) if args.vocabulary else set()

    action_pressure_map: dict[str, list[str]] = {}
    if args.action_pressure_map:
        if not args.action_pressure_map.exists():
            print(
                f"ERROR: --action-pressure-map 파일 미존재: {args.action_pressure_map}",
                file=sys.stderr,
            )
            return 2
        try:
            raw_map = json.loads(args.action_pressure_map.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"ERROR: --action-pressure-map JSON 파싱 실패: {e}", file=sys.stderr)
            return 2
        if not isinstance(raw_map, dict):
            print(
                "ERROR: --action-pressure-map JSON은 {action_id: [pressure_field,...]} dict여야 함",
                file=sys.stderr,
            )
            return 2
        for action_id, fields in raw_map.items():
            # Underscore-prefixed keys (e.g. "_meta", "_comment") are treated as
            # metadata and skipped — convention for inline JSON documentation.
            if str(action_id).startswith("_"):
                continue
            if not isinstance(fields, list) or not all(isinstance(f, str) for f in fields):
                print(
                    f"ERROR: --action-pressure-map: '{action_id}' 항목이 list[str]이 아님",
                    file=sys.stderr,
                )
                return 2
            action_pressure_map[str(action_id)] = list(fields)

    evaluator = build_evaluator(
        canonical_sequence=canon_seq,
        vocabulary=vocab,
        reproduction_threshold=args.reproduction_threshold,
        action_pressure_map=action_pressure_map or None,
    )

    try:
        report = evaluator.evaluate(records, is_all_hardcoded=args.is_all_hardcoded)
    except Exception as e:
        print(f"ERROR: rubric evaluate 실패: {e}", file=sys.stderr)
        return 1

    rep_dict = report_to_dict(report)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(rep_dict, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"discovery_class: {report.discovery_class.value}")
    print(f"records: {len(records)}")
    print(f"canon_valid: {report.canon.is_canon_valid}")
    print(f"causal_gate: {getattr(report.causal, 'passed_causal_gate', '?')}")
    print(f"character_signature: {getattr(report.character, 'passed_minimum_signature', '?')}")
    if getattr(report.causal, "alignment_evaluated", False):
        print(
            f"pressure_action_alignment: {report.causal.pressure_action_alignment:.3f} "
            f"(aligned={report.causal.aligned_actions}, "
            f"misaligned={report.causal.misaligned_actions}, "
            f"unmapped={report.causal.unmapped_actions})",
        )
    print(f"\nJSON report → {args.output}")

    if args.md_report:
        args.md_report.parent.mkdir(parents=True, exist_ok=True)
        args.md_report.write_text(
            render_markdown(rep_dict, n_records=len(records)),
            encoding="utf-8",
        )
        print(f"Markdown report → {args.md_report}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
