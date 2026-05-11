"""Phase 3.1 §22.3 Target C — Adaptation Recommendation CLI.

Per `docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md` §22.3.

입력:
    - SkeletonOutput JSON (예: docs/portfolio/demo/skeleton_output.json)
    - genre_profiles.json (build_genre_profiles.py 출력)

출력:
    - data/narrative/adaptation_recommendation.json
      schema_version: adaptation_recommendation_v1

목적:
    seed 별로 *어떤 genre로 각색할지* ranked top-K 추천. Plan §22.3 출력 spec
    그대로. ML 0 / 외부 fetch 0 / raw text 사용 0.

Target A/B/C 관계:
    - Target A (`run_flesh_baseline.py`): (seed × profile) flat fit list
    - Target B (`run_episode_intensity.py`): (episode × profile) intensity
    - Target C (이 스크립트): seed → ranked top-K genres (grouping + ranking)

사용:
    python scripts/narrative/run_adaptation_recommendation.py \\
        --skeleton docs/portfolio/demo/skeleton_output.json \\
        --profiles data/annotation/phase3_pilot/genre_profiles.json \\
        --output data/narrative/adaptation_recommendation.json \\
        --top-k 3
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
                sys.stdout.buffer, encoding="utf-8", errors="replace",
            )
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, encoding="utf-8", errors="replace",
            )
        except Exception:
            pass


from engine.observer.adaptation_recommendation import (  # noqa: E402
    run_adaptation_recommendation,
)
from engine.observer.genre_profile import load_profiles  # noqa: E402
from scripts.narrative.apply_genre_adapter import _load_skeleton_output  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--skeleton", required=True, type=Path,
                     help="SkeletonOutput JSON (예: docs/portfolio/demo/skeleton_output.json)")
    ap.add_argument("--profiles", required=True, type=Path,
                     help="genre_profiles.json")
    ap.add_argument("--output", required=True, type=Path,
                     help="adaptation_recommendation.json")
    ap.add_argument("--top-k", type=int, default=3,
                     help="seed당 추천 모드 수 (default 3)")
    ap.add_argument("--min-score", type=float, default=0.0,
                     help="이 score 이하 모드 제외 (default 0.0 — 모두 포함)")
    args = ap.parse_args(argv)

    if not args.skeleton.exists():
        print(f"ERROR: skeleton not found: {args.skeleton}", file=sys.stderr)
        return 2
    if not args.profiles.exists():
        print(f"ERROR: profiles not found: {args.profiles}", file=sys.stderr)
        return 2
    if args.top_k < 1:
        print(f"ERROR: --top-k must be >= 1 (got {args.top_k})", file=sys.stderr)
        return 2

    skeleton = _load_skeleton_output(args.skeleton)
    profiles = load_profiles(args.profiles)
    if not profiles:
        print(f"ERROR: no profiles loaded from {args.profiles}", file=sys.stderr)
        return 2

    out = run_adaptation_recommendation(
        skeleton, profiles,
        top_k=args.top_k,
        min_score=args.min_score,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(out.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"OK: adaptation recommendation → {args.output}")
    print(f"  source skeleton: {out.source_skeleton_id} ({out.source_skeleton_version})")
    print(f"  profiles used:   {', '.join(out.genre_profiles_used)}")
    print(f"  top_k:           {out.top_k}")
    print(f"  calibration:     {out.calibration_status}")
    print()
    print("Per-seed top recommendations:")
    for rec in out.recommendations:
        if not rec.recommended_modes:
            print(f"  {rec.source_seed_id}: (no modes >= min_score)")
            continue
        top = rec.recommended_modes[0]
        print(
            f"  {rec.source_seed_id} → {top.genre_id} "
            f"(score {top.score:.3f} / {top.fit_label})",
        )
        for alt in rec.recommended_modes[1:]:
            print(
                f"      alt: {alt.genre_id} "
                f"(score {alt.score:.3f} / {alt.fit_label})",
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
