"""Phase 2A — baseline trajectory harvesting.

Spec §3.2: 100 seeds × 200 tick canonical Peter runs.
- diag 3 confirmed 500 tick stable, so 200 tick is safe
- Outputs EnrichedSample-like dict per (agent, tick) with state features + selected
  action + available action weights (for future ranking / KL metrics)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.simulation.training_samples import (  # noqa: E402
    extract_samples,
    state_to_feature_vector,
)
from scripts.data_pipeline._common import (  # noqa: E402
    register_domain_types,
    run_peter,
)


def harvest_baseline(
    n_seeds: int = 100, max_tick: int = 200, agent_id: str = "peter",
) -> dict[str, Any]:
    """Return structured harvest: X (N,12), y_actions (N,), metadata."""
    all_X: list[list[float]] = []
    all_actions: list[str] = []
    all_seeds: list[int] = []
    all_ticks: list[int] = []

    for seed in range(n_seeds):
        result = run_peter(seed, max_tick=max_tick)
        samples = extract_samples(result)
        peter_samples = [s for s in samples if s.agent_id == agent_id and s.action is not None]
        for s in peter_samples:
            all_X.append(state_to_feature_vector(s.state))
            all_actions.append(s.action)
            all_seeds.append(seed)
            all_ticks.append(s.tick)

    X = np.asarray(all_X, dtype=np.float32) if all_X else np.zeros((0, 12), dtype=np.float32)
    return {
        "X": X,
        "actions": all_actions,
        "seeds": all_seeds,
        "ticks": all_ticks,
        "source": "baseline",
    }


def save_harvest(harvest: dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    np.save(out_dir / "X.npy", harvest["X"])
    (out_dir / "meta.json").write_text(
        json.dumps(
            {
                "source": harvest["source"],
                "actions": harvest["actions"],
                "seeds": harvest["seeds"],
                "ticks": harvest["ticks"],
                "n_samples": int(harvest["X"].shape[0]),
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def main() -> int:
    register_domain_types()
    out = ROOT / "data" / "person" / "pipeline_v1" / "baseline"
    n_seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    max_tick = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    print(f"[2A] Harvesting {n_seeds} seeds × {max_tick} tick...")
    harvest = harvest_baseline(n_seeds=n_seeds, max_tick=max_tick)
    save_harvest(harvest, out)
    from collections import Counter
    cnt = Counter(harvest["actions"])
    print(f"  samples: {harvest['X'].shape[0]}")
    print(f"  distribution: {dict(cnt)}")
    print(f"  saved to: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
