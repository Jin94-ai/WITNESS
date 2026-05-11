"""Trace JSONL → Rubric records JSON adapter (Phase 3.05).

demo_v07.py 등 simulation tools가 출력하는 trace JSONL을 rubric runner의
records JSON 형식으로 변환한다.

Source format (demo_v07 / TraceEvent):
    {"tick": N, "type": "action_taken", "payload": {"agent": "peter",
     "action": "follow_closely", "event_id": "voluntary", ...}}

Target format (rubric records):
    {"tick": N, "action_id": "follow_closely", "scene_id": "...",
     "state": {...}, "event_in": [...], "event_triggered": bool}

사용:
    python scripts/rubric/trace_to_records.py \\
        --trace output/peter_trace.jsonl \\
        --agent peter \\
        --output output/peter_records.json

설계:
    - agent filter: 특정 agent (예: peter)의 events만 추출
    - tick-aligned: 같은 tick의 action만 1건 → action_id (마지막 action_taken 우선)
    - event_in: 같은 tick의 다른 event types (예: scene_changed, event_fired)에서 추출
    - state: 가능하면 추출, 없으면 빈 dict (rubric은 default 0 사용)
    - scene_id: trace에 scene 정보 있으면 추출, 없으면 빈 문자열

원칙: data 변환만 — 새 정보 생성 0 (truth claim 회피).
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


def load_trace_jsonl(path: Path) -> list[dict]:
    """JSONL → list of dicts."""
    events = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        events.append(json.loads(line))
    return events


def convert(
    events: list[dict],
    *,
    agent: str,
) -> list[dict]:
    """trace events → rubric records.

    각 tick에 대해:
    - target agent의 마지막 `action_taken` event를 action_id로
    - 같은 tick의 다른 event types를 event_in에 추가
    - state는 trace에 있으면 추출 (현재 demo_v07는 state 누락 — 빈 dict)
    """
    # 1. 모든 event를 tick으로 그룹핑
    by_tick: dict[int, list[dict]] = {}
    for ev in events:
        tick = ev.get("tick")
        if tick is None:
            continue
        by_tick.setdefault(tick, []).append(ev)

    records: list[dict] = []
    for tick in sorted(by_tick.keys()):
        tick_events = by_tick[tick]
        # action_taken with target agent
        agent_actions = [
            e for e in tick_events
            if e.get("type") == "action_taken"
            and e.get("payload", {}).get("agent") == agent
        ]
        if not agent_actions:
            continue  # target agent가 이 tick에 action 없으면 skip
        action_id = agent_actions[-1].get("payload", {}).get("action")
        if not action_id:
            continue

        # event_in: 다른 event types
        event_in: list[str] = []
        for e in tick_events:
            etype = e.get("type", "")
            if etype == "action_taken":
                continue
            # event_id가 있으면 추가, 없으면 type
            ev_id = e.get("payload", {}).get("event_id") or etype
            if ev_id and ev_id not in event_in:
                event_in.append(ev_id)

        records.append({
            "tick": tick,
            "action_id": action_id,
            "scene_id": "",
            "state": {},
            "event_in": event_in,
            "event_triggered": len(event_in) > 0,
        })
    return records


def main(argv: list[str] | None = None) -> int:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--trace", required=True, type=Path,
                     help="trace JSONL input (demo_v07 형식)")
    ap.add_argument("--agent", required=True, type=str,
                     help="filter target agent (예: peter)")
    ap.add_argument("--output", required=True, type=Path,
                     help="records JSON output")
    ap.add_argument("--wrap-meta", action="store_true",
                     help="`{meta: ..., records: [...]}` wrapper로 저장")
    args = ap.parse_args(argv)

    if not args.trace.exists():
        print(f"ERROR: trace 파일 미존재: {args.trace}", file=sys.stderr)
        return 2

    events = load_trace_jsonl(args.trace)
    records = convert(events, agent=args.agent)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.wrap_meta:
        payload = {
            "meta": {
                "source_trace": str(args.trace),
                "agent": args.agent,
                "n_events_total": len(events),
                "n_records": len(records),
                "note": "demo_v07 trace → rubric records 변환 (정보 생성 0).",
            },
            "records": records,
        }
        args.output.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    else:
        args.output.write_text(
            json.dumps(records, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    print(f"OK: {len(records)} records from {len(events)} trace events → {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
