"""Phase 3.1 — KEEP features (reliability report) + rulebooks → genre_profiles.json.

Per `docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md` §28.

입력:
    1. reliability.json (Phase 3.0 §16.3 출력) — KEEP feature list
    2. genre rulebook (content/genres/{genre_id}/rulebook.json) — compatibility 추론

출력:
    data/annotation/phase3_pilot/genre_profiles.json (genre_profiles_index_v1)

원칙:
    - KEEP feature가 4개 미만이면 경고 (Phase 3.1 진입 조건 미충족)
    - feature_weights는 reliability r 기반 (큰 r = 큰 weight) 또는 uniform
    - rulebook.conflict_amplifiers + pressure_mappings에서 compatibility

사용:
    python scripts/narrative/build_genre_profiles.py \\
        --reliability data/annotation/phase3_pilot/reports/reliability.json \\
        --genres korean_morning_melodrama \\
        --output data/annotation/phase3_pilot/genre_profiles.json
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


from engine.observer.genre_profile import (  # noqa: E402
    GenreProfile,
    build_profile_from_rulebook,
    save_profiles,
)
from engine.observer.genre_rulebook import load_rulebook  # noqa: E402


def extract_keep_with_weights(reliability_json: dict) -> tuple[list[str], dict[str, float]]:
    """reliability report → KEEP feature list + r-based weights."""
    keep = list(reliability_json.get("summary", {}).get("keep", []))
    feat_rel = reliability_json.get("feature_reliability", {})
    weights: dict[str, float] = {}
    for f in keep:
        info = feat_rel.get(f, {})
        r = info.get("mean_r", 0.0)
        # Use max(r, 0) so negative r features (which shouldn't be KEEP anyway) don't sneak in
        weights[f] = max(0.0, float(r))
    return keep, weights


def main(argv: list[str] | None = None) -> int:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--reliability", type=Path, default=None,
                     help="reliability.json (Phase 3.0 output). 없으면 rulebook-only mode")
    ap.add_argument("--genres", required=True, nargs="+",
                     help="genre_id list (1+ rulebooks)")
    ap.add_argument("--output", required=True, type=Path,
                     help="genre_profiles.json output path")
    ap.add_argument("--require-min-keep", type=int, default=4,
                     help="≥ N KEEP features 미만이면 fail (default 4 = Phase 3.1 진입 조건)")
    ap.add_argument("--allow-rulebook-only", action="store_true",
                     help="reliability 없을 때 rulebook-only profile 생성 허용 (기본 fail)")
    args = ap.parse_args(argv)

    rel: dict | None = None
    if args.reliability and args.reliability.exists():
        rel = json.loads(args.reliability.read_text(encoding="utf-8"))

    if rel:
        keep, weights = extract_keep_with_weights(rel)
        n_records = int(rel.get("n_records", 0))
        data_source = "phase3_pilot"
        print(f"reliability loaded: {len(keep)} KEEP features (n_records={n_records})")
        if len(keep) < args.require_min_keep:
            print(
                f"WARNING: only {len(keep)} KEEP features (< {args.require_min_keep}); "
                "Phase 3.1 진입 조건 미충족",
                file=sys.stderr,
            )
            if not args.allow_rulebook_only:
                print(
                    "Use --allow-rulebook-only to proceed with low-data profile",
                    file=sys.stderr,
                )
                return 1
    else:
        if not args.allow_rulebook_only:
            print(
                "ERROR: --reliability not provided. Use --allow-rulebook-only "
                "to build profile from rulebook only (no data backing)",
                file=sys.stderr,
            )
            return 1
        keep = []
        weights = {}
        n_records = 0
        data_source = "rulebook_only"

    profiles: list[GenreProfile] = []
    for gid in args.genres:
        try:
            rb = load_rulebook(gid)
        except FileNotFoundError as e:
            print(f"ERROR: rulebook not found for {gid}: {e}", file=sys.stderr)
            return 2
        # If no KEEP features, fall back to "all features uniformly" using
        # rulebook's outline_step_mapping or pressure_mappings? — Use Phase 3.0 §11
        # default features as fallback when allow_rulebook_only.
        if not keep:
            keep_for_genre = [
                "conflict_intensity_peak",
                "dangling_thread_generation",
                "cliffhanger_strength",
                "relationship_pressure",
                "hidden_information_pressure",
            ]
            print(
                f"  rulebook-only fallback: using §11 default features for {gid}",
                file=sys.stderr,
            )
        else:
            keep_for_genre = list(keep)

        profile = build_profile_from_rulebook(
            genre_id=gid,
            rulebook=rb,
            keep_features=keep_for_genre,
            feature_weights=weights or None,
            n_records_basis=n_records,
            data_source=data_source,
        )
        profiles.append(profile)
        print(
            f"  {gid}: {len(profile.feature_weights)} weights, "
            f"{len(profile.compatible_conflict_axes)} axes, "
            f"{len(profile.compatible_pressures)} pressures"
        )

    save_profiles(profiles, args.output)
    print(f"OK: {len(profiles)} profile(s) → {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
