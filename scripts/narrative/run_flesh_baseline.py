"""Phase 3.1 — SkeletonOutput + GenreProfiles → flesh_baseline_output.json.

Per `docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md` §27 + §28.

입력:
    - SkeletonOutput JSON (예: docs/portfolio/demo/skeleton_output.json)
    - genre_profiles.json (build_genre_profiles.py 출력)
    - (선택) feature_matrix.csv — annotation feature를 skeleton seed에 매핑할 때

출력:
    - data/narrative/flesh_baseline_output.json
    - (선택) docs/portfolio/demo_flesh_baseline/index.html

원칙:
    - raw text 사용 0 (annotation feature 수치만)
    - 대사 / 본문 생성 0
    - 모든 score는 설명 가능 (reason_features + score_breakdown)

사용:
    python scripts/narrative/run_flesh_baseline.py \\
        --skeleton docs/portfolio/demo/skeleton_output.json \\
        --profiles data/annotation/phase3_pilot/genre_profiles.json \\
        --output data/narrative/flesh_baseline_output.json
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


from engine.observer.flesh_baseline import run_flesh_baseline  # noqa: E402
from engine.observer.genre_profile import load_profiles  # noqa: E402
from scripts.narrative.apply_genre_adapter import _load_skeleton_output  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--skeleton", required=True, type=Path)
    ap.add_argument("--profiles", required=True, type=Path,
                     help="genre_profiles.json")
    ap.add_argument("--output", required=True, type=Path,
                     help="flesh_baseline_output.json")
    ap.add_argument("--annotation-features", type=Path, default=None,
                     help="(선택) feature_matrix.csv — skeleton seed별 annotation score 사용")
    args = ap.parse_args(argv)

    if not args.skeleton.exists():
        print(f"ERROR: skeleton not found: {args.skeleton}", file=sys.stderr)
        return 2
    if not args.profiles.exists():
        print(f"ERROR: profiles not found: {args.profiles}", file=sys.stderr)
        return 2

    skeleton = _load_skeleton_output(args.skeleton)
    profiles = load_profiles(args.profiles)
    if not profiles:
        print(f"ERROR: no profiles loaded from {args.profiles}", file=sys.stderr)
        return 2

    annotation_features_by_seed: dict[str, dict[str, float]] = {}
    if args.annotation_features and args.annotation_features.exists():
        # Mean per-feature score per skeleton seed (간단한 매핑 — 실제 phase 3.1
        # iteration에서는 더 정교한 mapping 필요)
        # 현재 구조: feature_matrix는 record_id 단위, skeleton seed_id와 직접
        # 매핑은 caller가 결정. 1차는 skip.
        print(
            "NOTE: annotation_features mapping은 Phase 3.1 iteration 2에서 정교화. "
            "1차는 compatibility-only score.",
            file=sys.stderr,
        )

    out = run_flesh_baseline(
        skeleton, profiles,
        annotation_features_by_seed=annotation_features_by_seed,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(out.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"OK: flesh_baseline output → {args.output}")
    print(f"  source skeleton: {out.source_skeleton_id} ({out.source_skeleton_version})")
    print(f"  profiles used:   {', '.join(out.genre_profiles_used)}")
    print(f"  recommendations: {len(out.recommendations)}")
    if out.recommendations:
        # Top recommendation per seed
        seen = set()
        top: list = []
        for rec in sorted(out.recommendations, key=lambda r: -r.score):
            if rec.source_seed_id not in seen:
                seen.add(rec.source_seed_id)
                top.append(rec)
        for rec in sorted(top, key=lambda r: r.source_seed_id):
            print(
                f"    {rec.source_seed_id} → {rec.genre_id} "
                f"(score {rec.score:.3f} / {rec.fit_label})"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
