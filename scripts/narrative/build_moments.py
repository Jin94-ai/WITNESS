"""Build Moments — Narrative Mining Layer Phase 1 entry point.

Per `docs/WITNESS_NARRATIVE_MINING_PLAN.md` §5.2.

Reads an observer dump (e.g. `data/visual/dot_observer_data.json`) and writes
`data/narrative/moments.json` with a deterministic moment list + summary.

Usage:
    python scripts/narrative/build_moments.py
    python scripts/narrative/build_moments.py \\
        --input data/visual/dot_observer_data_triple.json \\
        --output data/narrative/moments_triple.json \\
        --run-label peter_scarcity_triple
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Repo root on sys.path so engine.observer.moment_extractor imports cleanly.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.observer.moment_extractor import extract_moments, serialize_moments  # noqa: E402


def main(in_path: str, out_path: str, run_label: str) -> None:
    observer = json.loads(Path(in_path).read_text(encoding="utf-8"))
    moments = extract_moments(observer)
    payload = serialize_moments(moments, run_label=run_label)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    s = payload["summary"]
    print(
        f"Wrote {out_path}: {s['total']} moments  "
        f"(by_type: {s['by_type']}, by_provenance: {s['by_provenance']})"
    )


def cli() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--input", default="data/visual/dot_observer_data.json")
    ap.add_argument("--output", default="data/narrative/moments.json")
    ap.add_argument("--run-label", default="peter_scarcity_baseline")
    ns = ap.parse_args()
    main(ns.input, ns.output, ns.run_label)


if __name__ == "__main__":
    cli()
