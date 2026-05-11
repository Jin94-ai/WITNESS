"""Build StoryThread — Narrative Mining Phase 3 entry point.

Per `docs/WITNESS_NARRATIVE_MINING_PLAN.md` §5.1, §5.4, §6.

Reads `data/narrative/moments.json` (Phase 1 output) and produces:
  - data/narrative/story_threads.json
  - data/narrative/moment_links.json (intermediate, for inspection)

Usage:
    python scripts/narrative/build_story_threads.py
    python scripts/narrative/build_story_threads.py \\
        --moments data/narrative/moments_triple.json \\
        --threads data/narrative/story_threads_triple.json \\
        --run-label peter_scarcity_triple
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.observer.moment import Moment  # noqa: E402
from engine.observer.thread_builder import (  # noqa: E402
    build_story_threads,
    link_moments,
    serialize_links,
    serialize_threads,
)


def main(in_moments: str, out_links: str, out_threads: str, run_label: str) -> None:
    payload = json.loads(Path(in_moments).read_text(encoding="utf-8"))
    moments = [Moment.from_dict(d) for d in payload["moments"]]

    links = link_moments(moments)
    Path(out_links).parent.mkdir(parents=True, exist_ok=True)
    Path(out_links).write_text(
        json.dumps(serialize_links(links), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    threads = build_story_threads(moments, links)
    Path(out_threads).write_text(
        json.dumps(
            serialize_threads(threads, run_label=run_label),
            ensure_ascii=False, indent=2,
        ),
        encoding="utf-8",
    )

    s_link = serialize_links(links)["summary"]
    s_thread = serialize_threads(threads, run_label=run_label)["summary"]
    print(
        f"Wrote {out_links}: {s_link['total']} links {s_link['by_type']}\n"
        f"Wrote {out_threads}: {s_thread['total']} threads "
        f"(strong={s_thread['strong']}, usable={s_thread['usable']}, weak={s_thread['weak']})"
    )


def cli() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--moments", default="data/narrative/moments.json")
    ap.add_argument("--links", default="data/narrative/moment_links.json")
    ap.add_argument("--threads", default="data/narrative/story_threads.json")
    ap.add_argument("--run-label", default="peter_scarcity_baseline")
    ns = ap.parse_args()
    main(ns.moments, ns.links, ns.threads, ns.run_label)


if __name__ == "__main__":
    cli()
