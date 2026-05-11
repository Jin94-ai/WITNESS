"""Demo: Observer → Story Candidate Pipeline.

Per `docs/observer/OBSERVER_TO_STORY_PIPELINE.md` Phase P4 +
`docs/observer/CANDIDATE_CURATION_PLAN.md` Phase Q1-Q4.

Usage:
    python examples/demo_observer_story.py                            # default = list-candidates
    python examples/demo_observer_story.py --list-candidates          # raw candidates (P1-P5)
    python examples/demo_observer_story.py --curated                  # curated 3 buckets (Q1-Q4)
    python examples/demo_observer_story.py --packet <candidate_id>    # single packet
    python examples/demo_observer_story.py --render-story <candidate_id>  # render result
    python examples/demo_observer_story.py --compare-lenses <candidate_id>  # 3 lens compare

Default input: peter_scarcity_baseline canonical run (Lee directive §10).

원칙: Observer가 잡은 흐름 → story candidate 추천 + 정리. *판정* 안 함.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Force UTF-8 stdout
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, OSError):
        pass

from engine.observer.candidate import (  # noqa: E402
    StoryCandidate,
    extract_event_candidates,
    extract_person_candidates,
    extract_story_candidates,
    extract_world_candidates,
)
from engine.observer.candidate_curation import curate_candidates  # noqa: E402
from examples.demo_observer import build_real_stream_from_anchor  # noqa: E402
from scripts.observer.candidate_packet import (  # noqa: E402
    build_curated_packet,
    build_packet,
    format_packet_compact,
    format_packet_text,
)
from scripts.observer.render_candidate_story import (  # noqa: E402
    compare_lenses,
    render_candidate_story,
)

# ============================================================
# Default canonical run cache
# ============================================================

_OBSERVER_CACHE = None


def _get_observer():
    """Lazy-build canonical Observer (peter_scarcity_baseline seed=0, 200 ticks)."""
    global _OBSERVER_CACHE
    if _OBSERVER_CACHE is None:
        _OBSERVER_CACHE = build_real_stream_from_anchor(
            anchor_id="peter_scarcity_baseline", seed=0, n_ticks=200
        )
    return _OBSERVER_CACHE


def _get_all_candidates(observer) -> list[StoryCandidate]:
    """Collect candidates from all 4 categories."""
    source_run = "peter_scarcity_baseline_seed0"
    candidates = []
    candidates.extend(extract_story_candidates(observer, source_run, top_k=5))
    candidates.extend(extract_world_candidates(observer, source_run, top_k=3))
    candidates.extend(extract_person_candidates(observer, source_run, top_k=3))
    candidates.extend(extract_event_candidates(observer, source_run, top_k=3))
    return candidates


def _find_candidate(candidates: list[StoryCandidate], candidate_id: str) -> StoryCandidate | None:
    for c in candidates:
        if c.candidate_id == candidate_id:
            return c
    return None


# ============================================================
# Commands
# ============================================================


def cmd_list_candidates() -> int:
    """List candidates from all 4 categories — top 5/3/3/3."""
    print("=" * 70)
    print("Observer → Story Candidate Pipeline — Candidate List")
    print("Source: peter_scarcity_baseline (seed=0, 200 ticks)")
    print("=" * 70)
    print()

    observer = _get_observer()
    source_run = "peter_scarcity_baseline_seed0"

    print("[Top 5 salient candidates]")
    for c in extract_story_candidates(observer, source_run, top_k=5):
        packet = build_packet(c, observer)
        print("  " + format_packet_compact(packet))
    print()

    print("[Top 3 world-heavy candidates]")
    for c in extract_world_candidates(observer, source_run, top_k=3):
        packet = build_packet(c, observer)
        print("  " + format_packet_compact(packet))
    print()

    print("[Top 3 person-arc candidates]")
    for c in extract_person_candidates(observer, source_run, top_k=3):
        packet = build_packet(c, observer)
        print("  " + format_packet_compact(packet))
    print()

    print("[Top 3 event-ripple candidates]")
    for c in extract_event_candidates(observer, source_run, top_k=3):
        packet = build_packet(c, observer)
        print("  " + format_packet_compact(packet))
    print()

    print("(Candidate = 추천만, 판정 아님. --packet <id>로 단일 packet 보기.)")
    return 0


def cmd_packet(candidate_id: str) -> int:
    """Single candidate packet (full text)."""
    observer = _get_observer()
    candidates = _get_all_candidates(observer)
    candidate = _find_candidate(candidates, candidate_id)
    if candidate is None:
        print(f"Candidate '{candidate_id}' not found.")
        print("Available IDs:")
        for c in candidates[:10]:
            print(f"  {c.candidate_id}")
        return 2
    packet = build_packet(candidate, observer)
    print(format_packet_text(packet))
    return 0


def cmd_render_story(candidate_id: str) -> int:
    """Render candidate as story-ready text in recommended lens."""
    observer = _get_observer()
    candidates = _get_all_candidates(observer)
    candidate = _find_candidate(candidates, candidate_id)
    if candidate is None:
        print(f"Candidate '{candidate_id}' not found.")
        return 2
    packet = build_packet(candidate, observer)
    lens = packet.render_lens or "world"
    print(render_candidate_story(candidate, observer, lens=lens, detail=True))
    return 0


def cmd_compare_lenses(candidate_id: str) -> int:
    """Compare 3 lenses for a single candidate."""
    observer = _get_observer()
    candidates = _get_all_candidates(observer)
    candidate = _find_candidate(candidates, candidate_id)
    if candidate is None:
        print(f"Candidate '{candidate_id}' not found.")
        return 2
    print(compare_lenses(candidate, observer))
    return 0


def cmd_curated() -> int:
    """List curated candidates — 3 buckets per Phase Q1-Q4."""
    print("=" * 70)
    print("Observer → Story Candidate Pipeline — Curated 3-Bucket View")
    print("Source: peter_scarcity_baseline (seed=0, 200 ticks)")
    print("=" * 70)
    print()

    observer = _get_observer()
    candidates = _get_all_candidates(observer)
    curated = curate_candidates(candidates, observer)

    def _print_bucket(label: str, items: list, hint: str) -> None:
        print(f"[{label}] ({len(items)})")
        if not items:
            print("  (none)")
        else:
            for cc in items:
                packet = build_curated_packet(cc, observer)
                print("  " + format_packet_compact(packet))
        print(f"  → {hint}")
        print()

    _print_bucket(
        "Story-ready",
        curated.story_ready,
        "render로 넘겨볼 만한 후보 (강한 신호 + lens 실체)",
    )
    _print_bucket(
        "Observation-only",
        curated.observation_only,
        "읽을 가치 있지만 바로 story 가면 약한 후보",
    )
    _print_bucket(
        "Low-activity hold",
        curated.low_activity_hold,
        "지금은 약하지만 tension seed (탐색 보류)",
    )

    print(
        "(Curation = 분류만, 판정 아님. "
        "near-duplicate는 'related' 필드로 접힘.)"
    )
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        return cmd_list_candidates()

    arg = sys.argv[1]
    if arg == "--list-candidates":
        return cmd_list_candidates()
    if arg == "--curated":
        return cmd_curated()
    if arg == "--packet":
        if len(sys.argv) < 3:
            print("Usage: --packet <candidate_id>")
            return 2
        return cmd_packet(sys.argv[2])
    if arg == "--render-story":
        if len(sys.argv) < 3:
            print("Usage: --render-story <candidate_id>")
            return 2
        return cmd_render_story(sys.argv[2])
    if arg == "--compare-lenses":
        if len(sys.argv) < 3:
            print("Usage: --compare-lenses <candidate_id>")
            return 2
        return cmd_compare_lenses(sys.argv[2])

    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
