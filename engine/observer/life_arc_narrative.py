"""Life Arc Narrative — time-windowed narrative from PhasedMultiAgentResult.

Per user directive (2026-05-08): "이야기의 흐름을 특정한 시간대로 두고
확인할 수 있도록. {display_name}의 인생 / 예수님의 공생애 3년 이런식으로."

이 모듈은 phased simulation 결과 (action_histories + canonical events +
emotion trajectory)에서 *시간대별 narrative timeline*을 합성한다.

원칙 (Plan §10/§14.4 유지):
    - 없는 사건 추가 금지 — events는 *반드시* canonical_events.json에서 옴
    - 대사 / 구체적 장면 묘사 금지 — agent의 chosen_action만 인용
    - 감정 과잉 표현 금지 — 수치 (emotion delta)만 인용
    - 한국어 plain language

데이터 흐름:
    PhasedMultiAgentResult
      ├── per_phase_results[phase_id].action_histories[agent_id]
      │     → fired event_id + chosen_action (engine 출력)
      ├── extract_absolute_trajectory(agent_id, "emotions.X")
      │     → emotion timeline (engine 출력)
      └── phase_boundaries (절대 hours)

      + content/{agent_id}/phases/{phase_id}/canonical_events.json
        → canonical event descriptions + scripture refs (정경 inline)

      → TimeWindowSummary list
        → render_life_arc_md(): 한국어 timeline markdown
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Plain-language emotion / action dictionaries
# ---------------------------------------------------------------------------

_PLAIN_EMOTION: dict[str, str] = {
    "awe":          "경외",
    "hope":         "희망",
    "fear":         "두려움",
    "grief":        "슬픔",
    "confusion":    "혼란",
    "love":         "사랑",
    "shame_self":   "수치심",
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CanonicalEventRecord:
    """One canonical event + simulation-chosen action."""
    phase_id: str
    local_tick: int
    absolute_hours: float
    absolute_days: float
    event_id: str
    description: str                       # 한국어 (canonical_events.json에서)
    scripture_ref: str                     # e.g., "눅 5:1-3"
    chosen_action: str                     # engine 출력 (action_histories에서)
    chosen_action_description: str = ""    # JSON action_options.description (한국어)


@dataclass(frozen=True)
class EmotionDelta:
    """One emotion's start/end value over a time window."""
    emotion: str               # 'awe' / 'fear' ...
    plain_emotion: str         # '경외' ...
    start_value: float
    end_value: float
    delta: float               # end - start


@dataclass(frozen=True)
class TimeWindow:
    """One time bracket within the life arc."""
    label: str                 # e.g., "01_calling" (internal)
    plain_label: str           # e.g., "1주차: 갈릴리 호숫가의 부르심"
    start_hours: float
    end_hours: float


@dataclass(frozen=True)
class UnfiredCanonicalEvent:
    """Canonical event defined in JSON but not fired by engine in this run.

    Useful for showing the full intended timeline; the simulation may have
    skipped these because trigger conditions did not match.
    """
    phase_id: str
    local_tick: int
    absolute_hours: float
    absolute_days: float
    event_id: str
    description: str
    scripture_ref: str


@dataclass(frozen=True)
class TimeWindowSummary:
    """Engine-derived narrative summary for one time window."""
    window: TimeWindow
    canonical_events: tuple[CanonicalEventRecord, ...]
    unfired_events: tuple[UnfiredCanonicalEvent, ...]
    emotion_deltas: tuple[EmotionDelta, ...]
    plain_narrative: str       # 한국어 단락

    def to_dict(self) -> dict:
        # JSON 측에도 josa 후처리 적용해 미해결 marker 누설 방지
        from engine.observer.episode_outline import resolve_korean_josa as _j
        return {
            "label": self.window.label,
            "plain_label": self.window.plain_label,
            "start_hours": self.window.start_hours,
            "end_hours": self.window.end_hours,
            "duration_days": (self.window.end_hours - self.window.start_hours) / 24.0,
            "canonical_events": [
                {
                    "phase_id": e.phase_id,
                    "local_tick": e.local_tick,
                    "absolute_hours": e.absolute_hours,
                    "absolute_days": e.absolute_days,
                    "event_id": e.event_id,
                    "description": e.description,
                    "scripture_ref": e.scripture_ref,
                    "chosen_action": e.chosen_action,
                    "chosen_action_description": e.chosen_action_description,
                }
                for e in self.canonical_events
            ],
            "unfired_events": [
                {
                    "phase_id": e.phase_id,
                    "local_tick": e.local_tick,
                    "absolute_hours": e.absolute_hours,
                    "absolute_days": e.absolute_days,
                    "event_id": e.event_id,
                    "description": e.description,
                    "scripture_ref": e.scripture_ref,
                }
                for e in self.unfired_events
            ],
            "emotion_deltas": [
                {
                    "emotion": d.emotion,
                    "plain_emotion": d.plain_emotion,
                    "start_value": d.start_value,
                    "end_value": d.end_value,
                    "delta": d.delta,
                }
                for d in self.emotion_deltas
            ],
            "plain_narrative": _j(self.plain_narrative),
        }


@dataclass(frozen=True)
class LifeArcNarrative:
    """Top-level narrative: ordered list of time windows."""
    agent_id: str
    agent_label: str           # 한국어 표시 이름 (e.g., "{display_name}")
    seed: int
    total_hours: float
    total_days: float
    windows: tuple[TimeWindowSummary, ...]

    def to_dict(self) -> dict:
        return {
            "schema_version": "life_arc_narrative_v1",
            "agent_id": self.agent_id,
            "agent_label": self.agent_label,
            "seed": self.seed,
            "total_hours": self.total_hours,
            "total_days": self.total_days,
            "windows": [w.to_dict() for w in self.windows],
        }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_phase_canonical_events(
    phase_id: str,
    agent_id: str,
    content_root: Path,
    explicit_path: str | None = None,
) -> dict[str, dict[str, Any]]:
    """Return mapping event_id → event dict from canonical_events.json.

    Path resolution order:
        1. `explicit_path` (from Phase config) if given
        2. content_root/{agent_id}/phases/{phase_id}/canonical_events.json
        3. content_root/{agent_id}/canonical_events.json (fallback for non-
           phase-specific events such as the passion arc which loads from
           the agent root).
    """
    candidates: list[Path] = []
    if explicit_path:
        candidates.append(Path(explicit_path))
    candidates.append(content_root / agent_id / "phases" / phase_id / "canonical_events.json")
    candidates.append(content_root / agent_id / "canonical_events.json")

    for p in candidates:
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            out: dict[str, dict[str, Any]] = {}
            for e in data.get("events", []):
                eid = e.get("event_id")
                if eid:
                    out[eid] = e
            return out
    return {}


def _phase_boundary_for(phase_id: str, boundaries: list[dict[str, Any]]) -> dict[str, Any] | None:
    for b in boundaries:
        if b.get("phase_id") == phase_id:
            return b
    return None


def _absolute_hours_for(
    phase_id: str,
    local_tick: int,
    boundaries: list[dict[str, Any]],
) -> float:
    b = _phase_boundary_for(phase_id, boundaries)
    if not b:
        return 0.0
    start_hours = float(b.get("start_hours", 0.0))
    scale = float(b.get("tick_scale_hours", 1.0))
    return start_hours + local_tick * scale


def _gather_canonical_events(
    result,
    agent_id: str,
    content_root: Path,
    phase_event_paths: dict[str, str] | None = None,
) -> tuple[list[CanonicalEventRecord], list[UnfiredCanonicalEvent]]:
    """Match action_histories events to canonical_events.json.

    Returns:
        (fired_events, unfired_events) — the latter are canonical events
        defined in JSON but the engine did not fire (e.g. trigger condition
        mismatch or phase max_tick truncation).
    """
    fired: list[CanonicalEventRecord] = []
    unfired: list[UnfiredCanonicalEvent] = []
    boundaries = result.phase_hours_table()  # adds start_hours / end_hours / tick_scale_hours
    phase_event_paths = phase_event_paths or {}
    for phase_id, phase_result in result.per_phase_results.items():
        explicit = phase_event_paths.get(phase_id)
        canonical_map = _load_phase_canonical_events(
            phase_id, agent_id, content_root, explicit_path=explicit,
        )
        actions = phase_result.action_histories.get(agent_id, [])
        fired_event_ids: set[str] = set()
        for a in actions:
            eid = getattr(a, "event_id", None) or (a.get("event_id") if isinstance(a, dict) else None)
            local_tick = getattr(a, "tick", None) or (a.get("tick") if isinstance(a, dict) else None)
            chosen = (
                getattr(a, "chosen_action", None)
                or (a.get("chosen_action") if isinstance(a, dict) else None)
                or "(no action)"
            )
            if eid is None or local_tick is None:
                continue
            cev = canonical_map.get(eid)
            if not cev:
                continue
            abs_hours = _absolute_hours_for(phase_id, int(local_tick), boundaries)
            # 선택된 action_id에 대응하는 한국어 description 찾기
            chosen_desc = ""
            for opt in cev.get("action_options", []) or []:
                if opt.get("action_id") == chosen:
                    chosen_desc = str(opt.get("description", ""))
                    break
            fired.append(CanonicalEventRecord(
                phase_id=phase_id,
                local_tick=int(local_tick),
                absolute_hours=abs_hours,
                absolute_days=abs_hours / 24.0,
                event_id=eid,
                description=str(cev.get("description", "")),
                scripture_ref=str(cev.get("scripture_ref", cev.get("source_ref", ""))),
                chosen_action=str(chosen),
                chosen_action_description=chosen_desc,
            ))
            fired_event_ids.add(eid)

        # phase의 실제 진행 ticks (MVP 단축이 적용된 max_tick 반영)
        b = _phase_boundary_for(phase_id, boundaries)
        if b is not None:
            phase_max_local_tick = int(b.get("end_tick", 0)) - int(b.get("start_tick", 0))
        else:
            phase_max_local_tick = 0

        # 정의되었으나 발화되지 않은 정경 사건들 (phase의 실행 범위 내만)
        for eid, cev in canonical_map.items():
            if eid in fired_event_ids:
                continue
            local_tick_def = cev.get("tick")
            if local_tick_def is None:
                continue
            ltd = int(local_tick_def)
            # MVP 단축으로 phase max_tick 외에 정의된 이벤트는 narrative
            # 산출에서 제외 (이 시뮬레이션 run에서는 도달 불가)
            if phase_max_local_tick and ltd > phase_max_local_tick:
                continue
            abs_hours = _absolute_hours_for(phase_id, ltd, boundaries)
            unfired.append(UnfiredCanonicalEvent(
                phase_id=phase_id,
                local_tick=ltd,
                absolute_hours=abs_hours,
                absolute_days=abs_hours / 24.0,
                event_id=eid,
                description=str(cev.get("description", "")),
                scripture_ref=str(cev.get("scripture_ref", cev.get("source_ref", ""))),
            ))

    fired.sort(key=lambda r: r.absolute_hours)
    unfired.sort(key=lambda r: r.absolute_hours)
    return fired, unfired


def _emotion_deltas_in_window(
    result,
    agent_id: str,
    start_hours: float,
    end_hours: float,
    emotions: tuple[str, ...] = ("awe", "hope", "fear", "grief", "confusion", "love"),
) -> list[EmotionDelta]:
    """Compute (start, end) values for each emotion within the window."""
    out: list[EmotionDelta] = []
    for em in emotions:
        traj = result.extract_absolute_trajectory(agent_id, f"emotions.{em}")
        if not traj:
            continue
        # find points just inside / nearest to window edges
        in_window = [p for p in traj if start_hours <= p.hours <= end_hours]
        if not in_window:
            # fall back: nearest-before / nearest-after
            before = [p for p in traj if p.hours <= start_hours]
            after = [p for p in traj if p.hours >= end_hours]
            if not before or not after:
                continue
            start_v = before[-1].value
            end_v = after[0].value
        else:
            start_v = in_window[0].value
            end_v = in_window[-1].value
        if abs(end_v - start_v) < 0.01 and abs(start_v) < 0.01:
            continue  # all-zero emotion → skip noise
        out.append(EmotionDelta(
            emotion=em,
            plain_emotion=_PLAIN_EMOTION.get(em, em),
            start_value=round(float(start_v), 2),
            end_value=round(float(end_v), 2),
            delta=round(float(end_v - start_v), 2),
        ))
    return out


# ---------------------------------------------------------------------------
# Time window strategies
# ---------------------------------------------------------------------------

def _windows_by_phase(
    result,
    plain_phase_labels: dict[str, str] | None = None,
) -> list[TimeWindow]:
    """One TimeWindow per phase boundary."""
    plain_phase_labels = plain_phase_labels or {}
    out: list[TimeWindow] = []
    for b in result.phase_hours_table():
        pid = b["phase_id"]
        out.append(TimeWindow(
            label=pid,
            plain_label=plain_phase_labels.get(pid, _generic_phase_label(pid)),
            start_hours=float(b["start_hours"]),
            end_hours=float(b["end_hours"]),
        ))
    return out


def _windows_by_week(result) -> list[TimeWindow]:
    """One TimeWindow per 7-day bracket, spanning the full simulation.

    Empty windows (no canonical events fired and minimal emotion change) are
    still listed so the timeline shows the full passage of time.
    """
    boundaries = result.phase_hours_table()
    if not boundaries:
        return []
    total_hours = float(boundaries[-1]["end_hours"])
    week_hours = 7 * 24.0
    out: list[TimeWindow] = []
    week_idx = 1
    cursor = 0.0
    while cursor < total_hours:
        end = min(cursor + week_hours, total_hours)
        start_day = cursor / 24.0
        end_day = end / 24.0
        out.append(TimeWindow(
            label=f"week_{week_idx:02d}",
            plain_label=f"{week_idx}주차 ({start_day:.0f}–{end_day:.0f}일)",
            start_hours=cursor,
            end_hours=end,
        ))
        cursor = end
        week_idx += 1
    return out


# Phase label generator — data-agnostic. Specific human-readable labels for
# a given anchor live in the *content* layer (e.g., the orchestrator script
# constructs them), not in this engine module. The orchestrator passes them
# to build_life_arc_narrative() via `plain_phase_labels`.
def _generic_phase_label(phase_id: str) -> str:
    """Fallback label: '01_calling' → '1막: calling' style. Content-layer
    Korean labels override this via `plain_phase_labels` parameter."""
    parts = phase_id.split("_", 1)
    if len(parts) == 2 and parts[0].isdigit():
        n = int(parts[0])
        return f"{n}막: {parts[1]}"
    return phase_id


# ---------------------------------------------------------------------------
# Plain narrative renderer (per window)
# ---------------------------------------------------------------------------

def _strip_trailing_scripture_paren(description: str, scripture_ref: str) -> str:
    """canonical_events.json 의 description은 종종 '... (눅 5:3)' 형태로
    scripture를 이미 포함한다. 그런 경우 scripture_ref와 중복이라 description
    끝의 () 부분을 한 번만 제거 (없으면 그대로)."""
    if not description or not scripture_ref:
        return description
    s = description.rstrip()
    if s.endswith(")") and scripture_ref in s:
        # '... (눅 5:3)' or '... (마 16:16). 신학적 최고점.' 같은 형태 모두 처리.
        # 가장 단순: scripture_ref이 description에 이미 있으면 — render 단계에서
        # *추가* 인용을 생략 (description은 그대로 유지).
        pass
    return description


def _format_event_ref(description: str, scripture_ref: str) -> str:
    """Render description; append scripture_ref only if not already in description."""
    desc = description.strip()
    if scripture_ref and f"({scripture_ref})" in desc:
        return desc
    if scripture_ref:
        return f"{desc} *({scripture_ref})*"
    return desc


def _render_window_narrative(
    window: TimeWindow,
    events: list[CanonicalEventRecord],
    unfired: list[UnfiredCanonicalEvent],
    deltas: list[EmotionDelta],
    agent_label: str,
) -> str:
    """Engine-derived 한국어 markdown 블록 — 사건 + 선택 + 감정 변화.

    구조: header(이미 상위에서) → 인트로 한 줄 → bulleted event list →
    (선택) 미발화 정경 사건 list → 감정 흐름 한 줄.
    """
    lines: list[str] = []
    duration_days = (window.end_hours - window.start_hours) / 24.0
    lines.append(
        f"이 시간대는 약 {duration_days:.1f}일에 해당한다 "
        f"({window.start_hours:.0f}–{window.end_hours:.0f} 시각)."
    )
    lines.append("")

    if not events:
        if unfired:
            lines.append(
                f"이 구간에서 *시뮬레이션 {agent_label}*이(가) 응답한 정경 사건은 "
                f"0건이다 (trigger 조건 미일치). 정의된 정경 사건은 {len(unfired)}건."
            )
        else:
            lines.append(
                "이 구간에는 정경 사건이 발화되지 않았다 "
                "(시뮬레이션 trigger 조건 미일치). 감정 흐름만 관측된다."
            )
    else:
        lines.append(f"**발화된 정경 사건 {len(events)}건**:")
        lines.append("")
        for e in events:
            lines.append(
                f"- **약 {e.absolute_days:.1f}일째** — "
                f"{_format_event_ref(e.description, e.scripture_ref)}"
            )
            if e.chosen_action_description:
                lines.append(
                    f"  - 시뮬레이션 {agent_label}의 선택: "
                    f"**{e.chosen_action_description}** *(`{e.chosen_action}`)*"
                )
            else:
                lines.append(
                    f"  - 시뮬레이션 {agent_label}의 선택: `{e.chosen_action}`"
                )

    lines.append("")

    if unfired:
        lines.append(
            f"**미발화 정경 사건 {len(unfired)}건** *(JSON 정의되었으나 "
            f"시뮬레이션 trigger 미일치)*:"
        )
        lines.append("")
        for u in unfired:
            lines.append(
                f"- 약 {u.absolute_days:.1f}일째 — "
                f"{_format_event_ref(u.description, u.scripture_ref)}"
            )
        lines.append("")

    if deltas:
        delta_phrases: list[str] = []
        for d in deltas:
            if abs(d.delta) < 0.5:
                continue
            direction = "↑" if d.delta > 0 else "↓"
            delta_phrases.append(
                f"{d.plain_emotion} {d.start_value:.1f} → {d.end_value:.1f} {direction}"
            )
        if delta_phrases:
            lines.append("**감정 흐름**: " + ", ".join(delta_phrases))

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Top-level builder
# ---------------------------------------------------------------------------

def build_life_arc_narrative(
    result,
    agent_id: str,
    agent_label: str,
    seed: int,
    content_root: Path | None = None,
    window_strategy: str = "by_phase",
    plain_phase_labels: dict[str, str] | None = None,
    phase_event_paths: dict[str, str] | None = None,
) -> LifeArcNarrative:
    """Assemble a LifeArcNarrative from a PhasedMultiAgentResult.

    Args:
        result: PhasedMultiAgentResult (from PhasedSimulationWorld.run()).
        agent_id: which agent's life arc.
        agent_label: 한국어 표시 이름 (display name).
        seed: simulation seed (for reproducibility tag in output).
        content_root: where canonical_events.json lives. Default: <repo>/content
        window_strategy: only "by_phase" supported for v1.
        plain_phase_labels: mapping phase_id → 한국어 라벨.

    Returns:
        LifeArcNarrative with one TimeWindowSummary per phase.
    """
    if content_root is None:
        # default: repository content/ folder
        # (engine/observer/life_arc_narrative.py → ../../content)
        content_root = Path(__file__).resolve().parents[2] / "content"

    plain_phase_labels = plain_phase_labels or {}

    boundaries = result.phase_hours_table()
    if not boundaries:
        return LifeArcNarrative(
            agent_id=agent_id, agent_label=agent_label, seed=seed,
            total_hours=0.0, total_days=0.0, windows=(),
        )
    total_hours = float(boundaries[-1]["end_hours"])

    fired_events, unfired_events = _gather_canonical_events(
        result, agent_id, content_root, phase_event_paths=phase_event_paths,
    )

    if window_strategy == "by_phase":
        windows = _windows_by_phase(result, plain_phase_labels=plain_phase_labels)
    elif window_strategy == "by_week":
        windows = _windows_by_week(result)
    else:
        raise ValueError(f"unsupported window_strategy: {window_strategy}")

    summaries: list[TimeWindowSummary] = []
    n_windows = len(windows)
    for i, w in enumerate(windows):
        # Half-open interval [start, end) for all but the last window;
        # the last window is closed [start, end] so the final tick is captured.
        if i == n_windows - 1:
            in_window = lambda h, lo=w.start_hours, hi=w.end_hours: lo <= h <= hi
        else:
            in_window = lambda h, lo=w.start_hours, hi=w.end_hours: lo <= h < hi
        evs = [e for e in fired_events if in_window(e.absolute_hours)]
        unf = [u for u in unfired_events if in_window(u.absolute_hours)]
        deltas = _emotion_deltas_in_window(
            result, agent_id, w.start_hours, w.end_hours,
        )
        narrative = _render_window_narrative(w, evs, unf, deltas, agent_label)
        summaries.append(TimeWindowSummary(
            window=w,
            canonical_events=tuple(evs),
            unfired_events=tuple(unf),
            emotion_deltas=tuple(deltas),
            plain_narrative=narrative,
        ))

    return LifeArcNarrative(
        agent_id=agent_id,
        agent_label=agent_label,
        seed=seed,
        total_hours=total_hours,
        total_days=total_hours / 24.0,
        windows=tuple(summaries),
    )


# ---------------------------------------------------------------------------
# Markdown renderer
# ---------------------------------------------------------------------------

def _is_window_silent(w: TimeWindowSummary) -> bool:
    """Window has no fired AND no unfired canonical events."""
    return len(w.canonical_events) == 0 and len(w.unfired_events) == 0


def _group_silent_runs(
    windows: tuple[TimeWindowSummary, ...],
) -> list[tuple[str, list[TimeWindowSummary]]]:
    """Group consecutive silent windows.

    Returns list of (kind, [windows]) where kind is 'silent' or 'active'.
    Adjacent windows with the same kind are merged.
    """
    out: list[tuple[str, list[TimeWindowSummary]]] = []
    for w in windows:
        kind = "silent" if _is_window_silent(w) else "active"
        if out and out[-1][0] == kind:
            out[-1][1].append(w)
        else:
            out.append((kind, [w]))
    return out


def render_life_arc_md(arc: LifeArcNarrative) -> str:
    """LifeArcNarrative → Korean markdown timeline document.

    Korean josa markers ('은(는)' / '이(가)' / etc.) used in templates are
    resolved by post-processing through resolve_korean_josa.

    For weekly windows, runs of consecutive silent windows (no events of
    any kind) are compressed into a single heading to keep the timeline
    scannable. Active (event-bearing) windows are rendered in full.
    """
    from engine.observer.episode_outline import resolve_korean_josa as _j

    out_lines: list[str] = []
    out_lines.append(f"# {arc.agent_label}의 생애 — 시뮬레이션 narrative")
    out_lines.append("")
    out_lines.append(
        f"> *seed: {arc.seed}, 총 {arc.total_days:.1f}일 ({arc.total_hours:.0f}시간), "
        f"{len(arc.windows)}개 시간대*"
    )
    out_lines.append("")
    out_lines.append(
        "이 timeline은 *engine 시뮬레이션 출력*에서 자동 합성되었다. "
        "정경 사건은 `content/{agent}/phases/*/canonical_events.json`에서 인용되며, "
        "각 사건의 *선택*은 시뮬레이션 결과(action_histories)이다. "
        "다른 seed로 돌리면 같은 사건에 대해 다른 선택이 나올 수 있다."
    )
    out_lines.append("")

    total_fired = sum(len(w.canonical_events) for w in arc.windows)
    total_unfired = sum(len(w.unfired_events) for w in arc.windows)
    out_lines.append(
        f"정경 사건: 발화 {total_fired}건 / 정의 "
        f"{total_fired + total_unfired}건. 없는 사건은 추가되지 않았다."
    )
    out_lines.append("")
    out_lines.append("---")
    out_lines.append("")

    runs = _group_silent_runs(arc.windows)
    for kind, ws in runs:
        if kind == "silent" and len(ws) >= 2:
            # Compress consecutive silent windows into one compact section
            first, last = ws[0], ws[-1]
            start_day = first.window.start_hours / 24.0
            end_day = last.window.end_hours / 24.0
            count = len(ws)
            # Pick the first and last labels and join (e.g. "2주차 → 9주차")
            first_label = first.window.plain_label.split(" ", 1)[0]
            last_label = last.window.plain_label.split(" ", 1)[0]
            heading = (
                f"{first_label}–{last_label}"
                if first_label != last_label else first_label
            )
            out_lines.append(f"## {heading} *(연속 {count}개 시간대 압축)*")
            out_lines.append("")
            out_lines.append(
                f"> *{first.window.start_hours:.0f}–"
                f"{last.window.end_hours:.0f} 시각 "
                f"(약 {start_day:.0f}–{end_day:.0f}일), "
                f"정경 사건 발화 0건 / 정의 0건*"
            )
            out_lines.append("")
            out_lines.append(
                "이 구간은 시뮬레이션에서 정경 사건이 발화되지 않은 "
                f"연속 {count}개 시간대이다 (감정 흐름만 진행)."
            )
            out_lines.append("")
            continue

        for w in ws:
            duration_days = (w.window.end_hours - w.window.start_hours) / 24.0
            out_lines.append(f"## {w.window.plain_label}")
            out_lines.append("")
            if w.unfired_events:
                out_lines.append(
                    f"> *{w.window.start_hours:.0f}–{w.window.end_hours:.0f} 시각 "
                    f"(약 {duration_days:.1f}일), "
                    f"정경 사건 발화 {len(w.canonical_events)}건 / "
                    f"정의 {len(w.canonical_events) + len(w.unfired_events)}건*"
                )
            else:
                out_lines.append(
                    f"> *{w.window.start_hours:.0f}–{w.window.end_hours:.0f} 시각 "
                    f"(약 {duration_days:.1f}일), "
                    f"정경 사건 {len(w.canonical_events)}건 발화*"
                )
            out_lines.append("")
            out_lines.append(w.plain_narrative)
            out_lines.append("")

    out_lines.append("---")
    out_lines.append("")
    out_lines.append(
        "*이 문서는 `engine/observer/life_arc_narrative.py`에서 자동 생성되었다. "
        "사건과 성서 레퍼런스는 `content/.../canonical_events.json`에서, "
        "선택과 감정 흐름은 engine simulation 출력에서 직접 인용된다.*"
    )
    return _j("\n".join(out_lines))


# ---------------------------------------------------------------------------
# HTML renderer (self-contained portfolio asset)
# ---------------------------------------------------------------------------

def _html_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
    )


_HTML_CSS = """
:root {
  --bg: #fafaf7;
  --fg: #222;
  --muted: #777;
  --border: #ddd;
  --accent: #5a7fb8;
  --fired: #2d6a4f;
  --unfired: #b78c2e;
  --silent: #aaa;
  --code-bg: #f0eee9;
}
html, body { margin: 0; padding: 0; background: var(--bg); color: var(--fg);
  font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', sans-serif;
  font-size: 15px; line-height: 1.6; }
.wrap { max-width: 820px; margin: 0 auto; padding: 32px 24px 64px; }
header { margin-bottom: 32px; border-bottom: 1px solid var(--border); padding-bottom: 16px; }
header h1 { margin: 0 0 8px; font-size: 28px; }
.meta { color: var(--muted); font-size: 13px; }
.intro { color: var(--fg); font-size: 14px; margin: 16px 0 24px; }
.summary { background: var(--code-bg); border-left: 3px solid var(--accent); padding: 12px 16px; font-size: 14px; margin-bottom: 32px; }
section.window { margin: 28px 0; padding: 0; }
section.window h2 { font-size: 18px; margin: 0 0 6px; padding: 0; }
section.window .window-meta { color: var(--muted); font-size: 12px; margin-bottom: 12px; }
section.silent { padding: 12px 16px; background: #f3f3ee; border-left: 3px solid var(--silent); border-radius: 3px; }
section.silent h2 { color: var(--silent); }
ul.events { list-style: none; padding-left: 0; margin: 0 0 12px; }
ul.events li { margin: 12px 0; padding-left: 12px; border-left: 2px solid var(--border); }
ul.events li.fired { border-left-color: var(--fired); }
ul.events li.unfired { border-left-color: var(--unfired); }
.day-tag { display: inline-block; min-width: 56px; color: var(--accent); font-weight: 600; font-size: 13px; }
.scripture { color: var(--muted); font-style: italic; font-size: 13px; }
.choice { margin-top: 4px; padding: 4px 0 0 0; font-size: 14px; }
.choice .ko { font-weight: 600; color: var(--fired); }
.choice .id { color: var(--muted); font-family: SFMono-Regular, Menlo, monospace; font-size: 12px; }
.deltas { margin-top: 8px; color: var(--muted); font-size: 13px; }
.deltas .up { color: #b04848; }
.deltas .dn { color: #4a7aa8; }
footer { margin-top: 48px; padding-top: 16px; border-top: 1px solid var(--border); color: var(--muted); font-size: 12px; }
"""


def _render_emotion_deltas_html(deltas: tuple[EmotionDelta, ...]) -> str:
    if not deltas:
        return ""
    parts = []
    for d in deltas:
        if abs(d.delta) < 0.5:
            continue
        cls = "up" if d.delta > 0 else "dn"
        arrow = "↑" if d.delta > 0 else "↓"
        parts.append(
            f'<span class="{cls}">{_html_escape(d.plain_emotion)} '
            f'{d.start_value:.1f}→{d.end_value:.1f} {arrow}</span>'
        )
    if not parts:
        return ""
    return f'<div class="deltas">감정: {" · ".join(parts)}</div>'


def _render_event_li_html(
    e: CanonicalEventRecord, agent_label: str,
) -> str:
    desc = _html_escape(e.description.strip())
    if e.scripture_ref and f"({e.scripture_ref})" not in e.description:
        scripture = (
            f'<span class="scripture"> ({_html_escape(e.scripture_ref)})</span>'
        )
    else:
        scripture = ""

    if e.chosen_action_description:
        choice = (
            f'<div class="choice">'
            f'<span class="ko">{_html_escape(e.chosen_action_description)}</span> '
            f'<span class="id">`{_html_escape(e.chosen_action)}`</span>'
            f'</div>'
        )
    else:
        choice = (
            f'<div class="choice">'
            f'<span class="id">`{_html_escape(e.chosen_action)}`</span>'
            f'</div>'
        )
    return (
        f'<li class="fired">'
        f'<span class="day-tag">{e.absolute_days:.1f}일</span> '
        f'{desc}{scripture}'
        f'{choice}'
        f'</li>'
    )


def _render_unfired_li_html(u: UnfiredCanonicalEvent) -> str:
    desc = _html_escape(u.description.strip())
    if u.scripture_ref and f"({u.scripture_ref})" not in u.description:
        scripture = (
            f'<span class="scripture"> ({_html_escape(u.scripture_ref)})</span>'
        )
    else:
        scripture = ""
    return (
        f'<li class="unfired">'
        f'<span class="day-tag">{u.absolute_days:.1f}일</span> '
        f'{desc}{scripture} '
        f'<span class="scripture">— 미발화</span>'
        f'</li>'
    )


def render_life_arc_html(arc: LifeArcNarrative) -> str:
    """LifeArcNarrative → self-contained HTML timeline document.

    Mirrors render_life_arc_md structure (compressed silent runs + active
    sections with bulleted events). No external assets — CSS inline, JSON
    payload embedded for downstream tools.
    """
    from engine.observer.episode_outline import resolve_korean_josa as _j

    title = f"{arc.agent_label}의 생애 — 시뮬레이션 narrative"
    total_fired = sum(len(w.canonical_events) for w in arc.windows)
    total_unfired = sum(len(w.unfired_events) for w in arc.windows)

    body_lines: list[str] = []
    body_lines.append('<header>')
    body_lines.append(f'<h1>{_html_escape(title)}</h1>')
    body_lines.append(
        f'<div class="meta">seed: {arc.seed} · 총 '
        f'{arc.total_days:.1f}일 ({arc.total_hours:.0f}시간) · '
        f'{len(arc.windows)}개 시간대</div>'
    )
    body_lines.append('</header>')
    body_lines.append(
        '<div class="intro">이 timeline은 <em>engine 시뮬레이션 출력</em>에서 '
        '자동 합성되었다. 정경 사건은 <code>canonical_events.json</code>에서 '
        '인용되며, 각 사건의 선택은 시뮬레이션 결과(action_histories)이다.</div>'
    )
    body_lines.append(
        f'<div class="summary">정경 사건: 발화 {total_fired}건 / '
        f'정의 {total_fired + total_unfired}건. 없는 사건은 추가되지 않았다.</div>'
    )

    runs = _group_silent_runs(arc.windows)
    for kind, ws in runs:
        if kind == "silent" and len(ws) >= 2:
            first, last = ws[0], ws[-1]
            start_day = first.window.start_hours / 24.0
            end_day = last.window.end_hours / 24.0
            count = len(ws)
            first_label = first.window.plain_label.split(" ", 1)[0]
            last_label = last.window.plain_label.split(" ", 1)[0]
            heading = (
                f"{first_label}–{last_label}"
                if first_label != last_label else first_label
            )
            body_lines.append('<section class="window silent">')
            body_lines.append(
                f'<h2>{_html_escape(heading)} '
                f'<span class="meta">(연속 {count}개 시간대 압축)</span></h2>'
            )
            body_lines.append(
                f'<div class="window-meta">{start_day:.0f}–{end_day:.0f}일 '
                f'· 정경 사건 0건</div>'
            )
            body_lines.append(
                f'<p>이 구간은 시뮬레이션에서 정경 사건이 발화되지 않은 '
                f'연속 {count}개 시간대이다 (감정 흐름만 진행).</p>'
            )
            body_lines.append('</section>')
            continue

        for w in ws:
            duration_days = (w.window.end_hours - w.window.start_hours) / 24.0
            silent_class = " silent" if _is_window_silent(w) else ""
            body_lines.append(f'<section class="window{silent_class}">')
            body_lines.append(
                f'<h2>{_html_escape(w.window.plain_label)}</h2>'
            )
            body_lines.append(
                f'<div class="window-meta">{w.window.start_hours:.0f}–'
                f'{w.window.end_hours:.0f} 시각 (약 {duration_days:.1f}일) · '
                f'발화 {len(w.canonical_events)}건 / 정의 '
                f'{len(w.canonical_events) + len(w.unfired_events)}건</div>'
            )
            if w.canonical_events:
                body_lines.append('<ul class="events">')
                for e in w.canonical_events:
                    body_lines.append(
                        _render_event_li_html(e, arc.agent_label)
                    )
                body_lines.append('</ul>')
            if w.unfired_events:
                body_lines.append(
                    '<div class="window-meta" style="margin:6px 0 4px">'
                    '미발화 (JSON 정의되었으나 simulation trigger 미일치):'
                    '</div>'
                )
                body_lines.append('<ul class="events">')
                for u in w.unfired_events:
                    body_lines.append(_render_unfired_li_html(u))
                body_lines.append('</ul>')
            if not w.canonical_events and not w.unfired_events:
                body_lines.append(
                    '<p style="color:var(--silent)">이 구간에는 정경 사건이 '
                    '발화되지 않았다. 감정 흐름만 관측된다.</p>'
                )
            body_lines.append(_render_emotion_deltas_html(w.emotion_deltas))
            body_lines.append('</section>')

    body_lines.append(
        '<footer>이 문서는 '
        '<code>engine/observer/life_arc_narrative.py</code>에서 자동 생성되었다. '
        '사건과 성서 레퍼런스는 <code>canonical_events.json</code>에서, '
        '선택과 감정 흐름은 engine simulation 출력에서 직접 인용된다. '
        'self-contained — 외부 자산 0.</footer>'
    )

    # JSON payload for downstream tools
    payload_json = json.dumps(arc.to_dict(), ensure_ascii=False)

    html = (
        '<!DOCTYPE html>\n<html lang="ko">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        f'<title>{_html_escape(title)}</title>\n'
        f'<style>{_HTML_CSS}</style>\n'
        '</head>\n<body>\n'
        '<div class="wrap">\n'
        + "\n".join(body_lines)
        + '\n</div>\n'
        f'<script type="application/json" id="life-arc-payload">{payload_json}</script>\n'
        '</body>\n</html>'
    )
    return _j(html)
