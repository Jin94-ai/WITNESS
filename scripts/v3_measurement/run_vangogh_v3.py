"""v3 Persona Engine — Van Gogh scenario 실측 (3번째 scenario).

Rule #5: 3번째 이질 scenario가 같은 engine에서 작동 확인. Rule #21: Judas와
동일하게 contrast bench — 튜닝 대상 아님.

Run:
    python scripts/v3_measurement/run_vangogh_v3.py [seed=0] [ticks=30]
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.person.loop import PersonV3Loop, TrajectoryRecord  # noqa: E402
from engine.persona import load_profile  # noqa: E402

CONTENT = ROOT / "content" / "vangogh" / "v3"


def main() -> int:
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    n_ticks = int(sys.argv[2]) if len(sys.argv) > 2 else 30

    profile = load_profile(CONTENT / "profile.json")
    print(f"[v3 VG] {profile.name} | seed={seed} ticks={n_ticks}")

    loop = PersonV3Loop(
        initial_state_path=CONTENT / "initial_state.json",
        canonical_events_path=CONTENT / "canonical_events.json",
        persona_profile=profile,
        seed=seed,
    )
    records = loop.run(n_ticks)

    print("\n  tick | action                  | motif         | events")
    print("  " + "-" * 78)
    for r in records:
        motif = r.selected_motif or "-"
        evs = ",".join(r.fired_events[:2])[:24]
        print(f"  {r.tick:>4} | {r.action_id:<23} | {motif:<13} | {evs}")

    motif_counts = Counter(r.selected_motif for r in records if r.selected_motif)
    action_counts = Counter(r.action_id for r in records)
    print(f"\n  motif: {dict(motif_counts.most_common())}")
    print(f"  action: {dict(action_counts.most_common())}")

    final = records[-1]
    print(f"\n  final state: fear={final.state.get('fear'):.2f} "
          f"grief={final.state.get('grief'):.2f} "
          f"awe={final.state.get('awe'):.2f}")

    # Save artifact
    out_dir = ROOT / "docs" / "person" / "v3_measurement"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / f"vangogh_v3_seed{seed}_ticks{n_ticks}.json"
    payload = {
        "seed": seed,
        "n_ticks": n_ticks,
        "profile_name": profile.name,
        "motif_distribution": dict(motif_counts),
        "action_distribution": dict(action_counts),
        "trajectory_summary": [
            {"tick": r.tick, "action": r.action_id,
             "motif": r.selected_motif, "events": r.fired_events}
            for r in records
        ],
    }
    out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                        encoding="utf-8")
    print(f"\n  saved: {out_json.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
