"""Phase 3.1 §24 Step 2 — Bridge: adaptation_recommendation → genre_adapter.

Per `docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md` §24 Step 2
("score와 rulebook adapter 연결").

목적:
    Target C (`adaptation_recommendation.json`)의 top-1 추천을 *실제로* genre adapter에
    연결한다. 기존 chain은 SkeletonOutput → Target C 추천 → (gap) → 사용자가 수동으로
    `apply_genre_adapter.py --genre <id>` 호출 → GenreAdaptedOutput. 이 wrapper가
    중간 gap을 메운다.

전략:
    recommendation.json의 *seed별 1순위 genre 빈도*를 집계해 가장 흔한 1순위 genre를
    선택 (modal genre). 동률 시 사전순 첫 번째. 사용자가 `--genre` override 가능.

입력:
    - SkeletonOutput JSON (apply_genre_adapter input과 동일)
    - adaptation_recommendation JSON (run_adaptation_recommendation 출력)

출력:
    - GenreAdaptedOutput JSON (apply_genre_adapter와 동일 schema)
    - stdout에 선택 근거 (modal genre / 빈도 / tie-break) 명시

원칙 (Phase 3.05 정직성):
    - recommendation의 `calibration_status` 와 `mode` (rulebook_only / annotation_blended)를
      선택 근거에 노출 — 사용자가 "score 신뢰도"를 알도록.
    - raw text 사용 0, 학습 0, 외부 fetch 0.

사용:
    python scripts/narrative/apply_top_recommendation.py \\
        --skeleton docs/portfolio/demo/skeleton_output.json \\
        --recommendation data/narrative/phase3_1_demo/adaptation_recommendation.json \\
        --output data/narrative/phase3_1_demo/top_recommendation_adapted.json
"""
from __future__ import annotations

import argparse
import io
import json
import subprocess
import sys
from collections import Counter
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


def select_modal_top_genre(recommendation: dict) -> tuple[str | None, dict]:
    """recommendation.json → modal 1순위 genre + 선택 근거 dict.

    Returns:
        (genre_id, info_dict). genre_id is None if no recommendations.
    """
    counter: Counter = Counter()
    modes_seen: set[str] = set()
    for rec in recommendation.get("recommendations", []):
        modes = rec.get("recommended_modes", [])
        if modes:
            top = modes[0]
            counter[top["genre_id"]] += 1
            modes_seen.add(top.get("mode", "rulebook_only"))
    if not counter:
        return None, {"reason": "no recommendations in input"}
    # modal genre (highest count, alphabetical tiebreak)
    top_count = max(counter.values())
    candidates = sorted([g for g, c in counter.items() if c == top_count])
    chosen = candidates[0]
    return chosen, {
        "modal_genre": chosen,
        "modal_count": top_count,
        "total_seeds_with_modes": sum(counter.values()),
        "tie_break_applied": len(candidates) > 1,
        "tied_candidates": candidates if len(candidates) > 1 else [],
        "all_counts": dict(counter),
        "recommendation_modes_seen": sorted(modes_seen),
        "calibration_status": recommendation.get("calibration_status", "?"),
    }


def main(argv: list[str] | None = None) -> int:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--skeleton", required=True, type=Path,
                     help="SkeletonOutput JSON 경로")
    ap.add_argument("--recommendation", required=True, type=Path,
                     help="adaptation_recommendation.json (run_adaptation_recommendation 출력)")
    ap.add_argument("--output", type=Path, default=None,
                     help="GenreAdaptedOutput JSON 출력 (없으면 stdout)")
    ap.add_argument("--genre", default=None,
                     help="modal 자동 선택을 override (사용자가 명시적으로 장르 지정)")
    ap.add_argument("--strict-audit", action="store_true",
                     help="adapter audit fail 시 exit 1 (default: 경고만)")
    args = ap.parse_args(argv)

    if not args.skeleton.exists():
        print(f"ERROR: skeleton not found: {args.skeleton}", file=sys.stderr)
        return 2
    if not args.recommendation.exists():
        print(f"ERROR: recommendation not found: {args.recommendation}",
              file=sys.stderr)
        return 2

    try:
        rec_data = json.loads(args.recommendation.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"ERROR: recommendation JSON parse: {e}", file=sys.stderr)
        return 2

    expected_schema = "adaptation_recommendation_v1"
    if rec_data.get("schema_version") != expected_schema:
        print(
            f"WARNING: recommendation schema_version "
            f"'{rec_data.get('schema_version')}' != '{expected_schema}'",
            file=sys.stderr,
        )

    if args.genre:
        chosen = args.genre
        info: dict = {
            "modal_genre": chosen,
            "override": True,
            "reason": "user-supplied --genre",
            "calibration_status": rec_data.get("calibration_status", "?"),
        }
    else:
        chosen, info = select_modal_top_genre(rec_data)
        if chosen is None:
            print(f"ERROR: no top-1 recommendations to bridge from", file=sys.stderr)
            return 2
        info["override"] = False

    print(f"Selected genre: {chosen}")
    print(f"  Selection info: {json.dumps(info, ensure_ascii=False)}")

    # Delegate to apply_genre_adapter.py
    cmd = [
        sys.executable,
        str(ROOT / "scripts/narrative/apply_genre_adapter.py"),
        "--input", str(args.skeleton),
        "--genre", chosen,
    ]
    if args.output:
        cmd += ["--output", str(args.output)]
    else:
        cmd += ["--json"]
    if args.strict_audit:
        cmd += ["--strict-audit"]

    print(f"Delegating to apply_genre_adapter.py …")
    rc = subprocess.run(cmd, capture_output=False)
    if rc.returncode != 0:
        return rc.returncode

    return 0


if __name__ == "__main__":
    sys.exit(main())
