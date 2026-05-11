"""CLI: SkeletonOutput JSON이 Phase 3 ML 진입 조건을 만족하는지 검증.

Per `docs/WITNESS_NARRATIVE_MODE_VALIDATION_FIX_PLAN.md` §7 Phase 3 Go/No-Go.
+ `engine/observer/universal_seed_adapter.py::validate_skeleton_semantic`.

사용:
    python scripts/skeleton/validate_skeleton_phase3.py docs/portfolio/demo/skeleton_output.json
    python scripts/skeleton/validate_skeleton_phase3.py path/to/skeleton.json --lenient
    python scripts/skeleton/validate_skeleton_phase3.py path/to/skeleton.json --json

종료 코드:
    0 = pass (Phase 3 ready)
    1 = fail (semantic violations)
    2 = file/parsing error

이 CLI는 *deployed* skeleton_output.json (예: docs/portfolio/demo/skeleton_output.json)
이 contract를 의미적으로 보존하는지 검증한다. CI 또는 PR 게이트로 사용 가능.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

# Ensure project root is importable when run as a script
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _force_utf8_stdout() -> None:
    """Windows cp949 환경에서도 한국어 / em-dash 출력 가능하게."""
    if hasattr(sys.stdout, "buffer"):
        try:
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace"
            )
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, encoding="utf-8", errors="replace"
            )
        except Exception:
            pass

from engine.observer.skeleton_output import (  # noqa: E402
    AnchorMetadata, AuditTrail, EvidenceLedger, LifeStoryFlow, SkeletonOutput,
)
from engine.observer.universal_seed_adapter import (  # noqa: E402
    validate_skeleton_semantic,
)
from engine.observer.universal_story_seed import UniversalStorySeed  # noqa: E402


def _load_skeleton_output(path: Path) -> SkeletonOutput:
    """deployed skeleton_output.json → SkeletonOutput dataclass."""
    raw = json.loads(path.read_text(encoding="utf-8"))

    seeds = tuple(UniversalStorySeed.from_dict(s) for s in raw.get("seeds", []))

    flow_d = raw.get("flow")
    flow: LifeStoryFlow | None = None
    if flow_d is not None:
        flow = LifeStoryFlow(
            schema_version=flow_d.get("schema_version", "life_story_flow_v1_1"),
            ordering=flow_d.get("ordering", "evidence_derived"),
            ordered_seed_ids=tuple(flow_d.get("ordered_seed_ids", [])),
            flow_roles=dict(flow_d.get("flow_roles", {})),
        )

    el_d = raw.get("evidence_ledger", {})
    ledger = EvidenceLedger(
        schema_version=el_d.get("schema_version", "evidence_ledger_v1"),
        total_signals=int(el_d.get("total_signals", 0)),
        signals_per_seed=dict(el_d.get("signals_per_seed", {})),
        audit_pass_count=int(el_d.get("audit_pass_count", 0)),
        audit_fail_count=int(el_d.get("audit_fail_count", 0)),
        audit_risky_count=int(el_d.get("audit_risky_count", 0)),
        forbidden_token_violations=int(el_d.get("forbidden_token_violations", 0)),
        notes=tuple(el_d.get("notes", [])),
    )

    at_d = raw.get("audit_trail", {})
    audit = AuditTrail(
        schema_version=at_d.get("schema_version", "audit_trail_v1_1"),
        stages_passed=tuple(at_d.get("stages_passed", [])),
        forbidden_event_additions=int(at_d.get("forbidden_event_additions", 0)),
        forbidden_dialogue_generation=int(at_d.get("forbidden_dialogue_generation", 0)),
        forbidden_slugline_use=int(at_d.get("forbidden_slugline_use", 0)),
        unmapped_pressure_phrases=tuple(at_d.get("unmapped_pressure_phrases", [])),
        missing_pressure_seeds=tuple(at_d.get("missing_pressure_seeds", [])),
        unknown_axis_count=int(at_d.get("unknown_axis_count", 0)),
        notes=tuple(at_d.get("notes", [])),
    )

    am_d = raw.get("anchor_metadata")
    anchor: AnchorMetadata | None = None
    if am_d is not None:
        anchor = AnchorMetadata(
            anchor_id=am_d.get("anchor_id", ""),
            display_name_overrides=dict(am_d.get("display_name_overrides", {})),
            role_label_overrides=dict(am_d.get("role_label_overrides", {})),
            description_ko=am_d.get("description_ko", ""),
        )

    return SkeletonOutput(
        schema_version=raw.get("schema_version", "skeleton_output_v1"),
        seeds=seeds,
        flow=flow,
        evidence_ledger=ledger,
        anchor_metadata=anchor,
        audit_trail=audit,
    )


def main(argv: list[str] | None = None) -> int:
    _force_utf8_stdout()
    parser = argparse.ArgumentParser(
        description="Validate SkeletonOutput JSON against Phase 3 Go criteria.",
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Path to skeleton_output.json (e.g. docs/portfolio/demo/skeleton_output.json)",
    )
    parser.add_argument(
        "--lenient",
        action="store_true",
        help="Lenient mode: unknown axes are allowed if recorded in audit_trail.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON output instead of human prose.",
    )
    args = parser.parse_args(argv)

    if not args.path.exists():
        print(f"ERROR: file not found: {args.path}", file=sys.stderr)
        return 2
    try:
        out = _load_skeleton_output(args.path)
    except Exception as e:
        print(f"ERROR: failed to parse {args.path}: {e}", file=sys.stderr)
        return 2

    errors = validate_skeleton_semantic(out, strict=not args.lenient)
    mode = "lenient" if args.lenient else "strict"
    summary = {
        "path": str(args.path),
        "mode": mode,
        "ready": not errors,
        "error_count": len(errors),
        "errors": errors,
        "schema_version": out.schema_version,
        "seed_count": len(out.seeds),
        "flow_present": out.flow is not None,
        "audit_trail": {
            "unmapped_pressure_phrases":
                list(out.audit_trail.unmapped_pressure_phrases),
            "missing_pressure_seeds":
                list(out.audit_trail.missing_pressure_seeds),
            "unknown_axis_count": out.audit_trail.unknown_axis_count,
        },
    }

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"Skeleton: {args.path}")
        print(f"Mode:     {mode}")
        print(f"Schema:   {out.schema_version}")
        print(f"Seeds:    {len(out.seeds)}")
        print(f"Flow:     {'present' if out.flow else 'NONE'}")
        print(f"Audit:    "
              f"unmapped={len(out.audit_trail.unmapped_pressure_phrases)} "
              f"missing_pressures={len(out.audit_trail.missing_pressure_seeds)} "
              f"unknown_axes={out.audit_trail.unknown_axis_count}")
        print()
        if errors:
            print(f"FAIL — {len(errors)} semantic violation(s):")
            for e in errors:
                print(f"  - {e}")
            print()
            print("Phase 3 진입 차단. validation report 갱신 필요.")
        else:
            print("PASS — Phase 3 진입 조건 충족.")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
