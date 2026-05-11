"""CLI: SkeletonOutput JSON에 장르 어댑터를 적용해 GenreAdaptedOutput JSON 생성.

Per `docs/WITNESS_PHASE_2_75_GENRE_ADAPTER_MVP_PLAN.md` §9.1.

사용:
    python scripts/narrative/apply_genre_adapter.py \\
        --input docs/portfolio/demo/skeleton_output.json \\
        --genre korean_morning_melodrama \\
        --output data/narrative/genre_adapted_output.json

선택:
    --strict-audit  audit 결과가 fail이면 exit 1 (default: 경고만)
    --json          stdout에 결과 JSON 출력 (--output 생략 시)
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _force_utf8_stdout() -> None:
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


from engine.observer.genre_adapter import (  # noqa: E402
    GenreAdaptedOutput, adapt_skeleton_to_genre,
)
from engine.observer.genre_audit import audit_genre_output  # noqa: E402
from engine.observer.genre_rulebook import (  # noqa: E402
    load_audit_blocklist, load_rulebook,
)
from engine.observer.skeleton_output import (  # noqa: E402
    AnchorMetadata, AuditTrail, EvidenceLedger, LifeStoryFlow, SkeletonOutput,
)
from engine.observer.universal_story_seed import UniversalStorySeed  # noqa: E402


def _load_skeleton_output(path: Path) -> SkeletonOutput:
    """Phase 2.5 cycle 5의 validate_skeleton_phase3.py loader와 동일."""
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
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, type=Path,
                     help="SkeletonOutput JSON path")
    ap.add_argument("--genre", required=True,
                     help="genre_id (e.g. korean_morning_melodrama)")
    ap.add_argument("--output", type=Path,
                     help="GenreAdaptedOutput JSON 저장 경로 (생략 시 stdout)")
    ap.add_argument("--strict-audit", action="store_true",
                     help="audit fail 시 exit 1 (default: 경고만)")
    ap.add_argument("--json", action="store_true",
                     help="stdout에 결과 JSON 출력 (--output 없을 때만 의미)")
    args = ap.parse_args(argv)

    if not args.input.exists():
        print(f"ERROR: input not found: {args.input}", file=sys.stderr)
        return 2

    try:
        skeleton = _load_skeleton_output(args.input)
    except Exception as e:
        print(f"ERROR: failed to parse skeleton: {e}", file=sys.stderr)
        return 2

    try:
        rulebook = load_rulebook(args.genre)
        blocklist = load_audit_blocklist(args.genre)
    except Exception as e:
        print(f"ERROR: failed to load genre {args.genre!r}: {e}", file=sys.stderr)
        return 2

    try:
        adapted = adapt_skeleton_to_genre(skeleton, rulebook)
    except ValueError as e:
        print(f"ERROR: skeleton fails Phase 2.75 §4.1 input gate: {e}",
               file=sys.stderr)
        return 1

    audit_result = audit_genre_output(adapted, blocklist)
    out_dict = adapted.to_dict()
    out_dict["audit"] = audit_result.to_dict()

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(out_dict, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"OK: genre_adapted_output saved → {args.output}")
        print(f"  source seeds: {len(adapted.adapted_seeds)}")
        print(f"  genre: {adapted.genre_id}")
        print(f"  audit: {audit_result.overall}")
        if audit_result.overall == "fail":
            print("  violations:")
            for cat, items in (
                ("forbidden_event", audit_result.forbidden_event_violations),
                ("dialogue", audit_result.dialogue_violations),
                ("source_imitation", audit_result.source_imitation_violations),
                ("evidence", audit_result.evidence_violations),
            ):
                for v in items:
                    print(f"    [{cat}] {v}")
    elif args.json:
        print(json.dumps(out_dict, ensure_ascii=False, indent=2))
    else:
        print(f"genre: {adapted.genre_id}")
        print(f"adapted seeds: {len(adapted.adapted_seeds)}")
        print(f"audit: {audit_result.overall}")

    if args.strict_audit and audit_result.overall == "fail":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
