"""Demo: annotated probe → 한국어 이야기 출력 (3-stage pipeline).

Usage:
    python examples/demo_story.py P9             # baseline P9
    python examples/demo_story.py P_S2_08        # Branch C scarcity depth (nonmonotonic)
    python examples/demo_story.py P_PV_09        # Branch C LOW_ACTIVITY (rare)
    python examples/demo_story.py --highlights   # 6 핵심 케이스 한 번에

This script chains extract → IR → render in one call. Output goes to
docs/story/generated/ and is also printed to stdout.

Per docs/story/STORY_OUTPUT_SPEC.md and docs/research/PAPER_DRAFT_V06.md
Appendix H. No engine, content pack, or annotated probe spec touched.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.story.build_narrative_ir import process as build_ir  # noqa: E402
from scripts.story.extract_story_features import process_probe as extract  # noqa: E402
from scripts.story.render_story_ko import process as render  # noqa: E402

HIGHLIGHTS = [
    ("P6",     "MIXED scarcity (가장 풍부, cohort split)"),
    ("P_PV_09", "LOW_ACTIVITY (rare 1/48, sacred clustered)"),
    ("P_PV_01", "RECOVERY accusation (placement reversal - pair with P_PV_02)"),
    ("P_PV_02", "SATURATION accusation (placement reversal - pair with P_PV_01)"),
    ("P_S2_05", "SATURATION scarcity (nonmonotonic - pair with P_S2_08)"),
    ("P_S2_08", "RECOVERY scarcity triple (nonmonotonic - pair with P_S2_05)"),
]


def run_pipeline(probe_id: str) -> tuple[str, str]:
    """Run extract → IR → render for one probe."""
    extract(probe_id)
    build_ir(probe_id)
    summary, narrative = render(probe_id)
    return summary, narrative


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2

    if sys.argv[1] == "--highlights":
        print("=== 6 Story Highlights (curated) ===\n")
        for probe_id, label in HIGHLIGHTS:
            print(f"\n{'='*70}")
            print(f"{probe_id} - {label}")
            print(f"{'='*70}\n")
            try:
                summary, narrative = run_pipeline(probe_id)
                print("[Summary form]\n")
                print(summary)
                print("\n[Narrative form]\n")
                print(narrative)
            except FileNotFoundError as e:
                print(f"  skipped ({e})")
        print("\n\nAll generated files in: docs/story/generated/")
        return 0

    probe_id = sys.argv[1]
    try:
        summary, narrative = run_pipeline(probe_id)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("\nAvailable probe IDs:")
        print("  Baseline: P1..P12")
        print("  Branch C placement: P_PV_01..P_PV_09")
        print("  Branch C cast:      P_CV_01..P_CV_09")
        print("  Branch C density:   P_ED_01..P_ED_09")
        print("  Branch C scarcity:  P_S2_01..P_S2_09")
        return 1

    print(f"=== {probe_id} ===\n")
    print("[Summary form (400-800자)]\n")
    print(summary)
    print(f"\n({len(summary)}자)\n")
    print("\n[Narrative form (1000-1800자 target)]\n")
    print(narrative)
    print(f"\n({len(narrative)}자)\n")
    print("\nFiles written:")
    print(f"  docs/story/generated/{probe_id}_summary_ko.txt")
    print(f"  docs/story/generated/{probe_id}_narrative_ko.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
