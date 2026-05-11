"""Synthesize multi-AI annotations into a single vector (Phase 2).

Per `docs/witness_narrative_mode_plan.md` §6 Phase 2 산출물:
    scripts/annotation/synthesize_annotations.py

이 스크립트는 *네트워크 호출 0*. 입력은 이미 LLM이 생성하고 디스크에 기록된
어노테이션 JSON들 — 여러 어노테이터의 결과를 하나의 합성 벡터로 만들어
정규 위치에 저장한다.

흐름:
    data/annotated/_per_annotator/{annotator_id}/{title}/{episode_no:02d}.json
        × N annotators
        ↓ synthesize_annotations() (mean + spread-based confidence)
    data/annotated/{title}/{episode_no:02d}.json
        (단일 합성 결과)

Usage:
    python scripts/annotation/synthesize_annotations.py \\
        --inputs path/to/a1.json path/to/a2.json path/to/a3.json \\
        --output path/to/synthesized.json

    # 또는 디렉토리 모드
    python scripts/annotation/synthesize_annotations.py \\
        --per-annotator-dir data/annotated/_per_annotator \\
        --title-id mydrama --episode 5 \\
        --output data/annotated/mydrama/05.json
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _ensure_utf8_stdout() -> None:
    if sys.platform == "win32":
        try:
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace",
            )
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, encoding="utf-8", errors="replace",
            )
        except Exception:
            pass


_ensure_utf8_stdout()

from scripts.annotation.prompt_templates import (  # noqa: E402
    SynthesizedAnnotation,
    migrate_deprecated_annotation,
    synthesize_annotations,
    validate_annotation_dict,
)


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_inputs_from_paths(
    paths: list[Path], *, migrate: bool = False,
) -> list[dict]:
    out: list[dict] = []
    for p in paths:
        if not p.exists():
            print(f"ERROR: input not found: {p}", file=sys.stderr)
            sys.exit(1)
        d = json.loads(p.read_text(encoding="utf-8"))
        if migrate:
            d = migrate_deprecated_annotation(d)
        errs = validate_annotation_dict(d)
        if errs:
            print(f"ERROR: {p} invalid:", file=sys.stderr)
            for e in errs:
                print(f"  - {e}", file=sys.stderr)
            if any("missing feature" in e for e in errs) and not migrate:
                print(
                    "  HINT: --migrate-deprecated 로 v1 → v1.1 자동 변환 시도 "
                    "(conflict_amplification_rate / resolution_to_dangling_ratio 매핑)",
                    file=sys.stderr,
                )
            sys.exit(1)
        out.append(d)
    return out


def load_inputs_from_dir(
    base: Path, title_id: str, episode_no: int,
    *, migrate: bool = False,
) -> list[dict]:
    """Walk per-annotator dir for matching (title, episode)."""
    out: list[dict] = []
    if not base.exists():
        return out
    for annotator_dir in sorted(base.iterdir()):
        if not annotator_dir.is_dir():
            continue
        candidate = (
            annotator_dir / title_id / f"{episode_no:02d}.json"
        )
        if candidate.exists():
            d = json.loads(candidate.read_text(encoding="utf-8"))
            if migrate:
                d = migrate_deprecated_annotation(d)
            errs = validate_annotation_dict(d)
            if errs:
                print(f"WARNING: {candidate} invalid; skipping", file=sys.stderr)
                continue
            out.append(d)
    return out


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def synthesized_to_dict(s: SynthesizedAnnotation) -> dict:
    return {
        "schema_version": "synthesized_annotation_v1",
        "title_id": s.title_id,
        "episode_no": s.episode_no,
        "features": dict(s.features),
        "confidence": s.confidence,
        "contributing_annotators": list(s.contributing_annotators),
        "evidence_quotes": list(s.evidence_quotes),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cli() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument(
        "--inputs", nargs="+", type=Path,
        help="N annotation JSON paths (이미 LLM이 생성한 결과)",
    )
    src.add_argument(
        "--per-annotator-dir", type=Path,
        help="data/annotated/_per_annotator 같은 base dir",
    )
    ap.add_argument("--title-id", help="(--per-annotator-dir 모드) title id")
    ap.add_argument(
        "--episode", type=int,
        help="(--per-annotator-dir 모드) 회차 번호",
    )
    ap.add_argument(
        "--output", type=Path,
        help="합성 결과를 저장할 JSON 경로 (생략 시 stdout)",
    )
    ap.add_argument(
        "--migrate-deprecated", action="store_true",
        help=(
            "Phase 2.5: 기존 v1 어노테이션의 conflict_amplification_rate / "
            "resolution_to_dangling_ratio 필드를 v1.1 이름으로 자동 변환 후 처리. "
            "기존 어노테이션 재 어노테이션 없이 합성 가능."
        ),
    )
    args = ap.parse_args()

    if args.inputs:
        annotations = load_inputs_from_paths(
            args.inputs, migrate=args.migrate_deprecated,
        )
    else:
        if args.title_id is None or args.episode is None:
            print("ERROR: --per-annotator-dir requires --title-id and --episode",
                   file=sys.stderr)
            return 1
        annotations = load_inputs_from_dir(
            args.per_annotator_dir, args.title_id, args.episode,
            migrate=args.migrate_deprecated,
        )
        if not annotations:
            print(
                f"ERROR: no annotations found at "
                f"{args.per_annotator_dir}/<annotator>/{args.title_id}/"
                f"{args.episode:02d}.json",
                file=sys.stderr,
            )
            return 1

    if len(annotations) < 2:
        print(
            f"WARNING: only {len(annotations)} annotation(s) — confidence "
            f"signal may be 0 (multi-AI synthesis needs ≥2 annotators)",
            file=sys.stderr,
        )

    syn = synthesize_annotations(annotations)
    out_dict = synthesized_to_dict(syn)
    text = json.dumps(out_dict, ensure_ascii=False, indent=2)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"OK: written {args.output}")
        print(f"  contributing annotators: {len(syn.contributing_annotators)}")
        print(f"  confidence: {syn.confidence:.3f}")
    else:
        print(text)

    return 0


if __name__ == "__main__":
    sys.exit(cli())
