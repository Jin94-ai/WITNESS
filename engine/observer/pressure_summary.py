"""Pressure Summary — Stage 3 (세계가 어떻게 움직였는가).

Per `docs/WITNESS_PORTFOLIO_DEMO_PIPELINE_PLAN.md` §3.

압력 timeline을 *3 phase로 압축*하여 일반인이 한눈에 이해 가능한 요약을 만든다.

규칙:
    - 한국어 plain language
    - tick / source / co-occurrence 같은 내부 용어 사용 금지
    - phase는 정확히 3개 (초반 / 중반 / 후반)
    - 각 phase에 dominant pressure가 있음
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AgentPressureSummary:
    """한 agent의 두드러지는 압력 변화 요약 (이름 + 한 줄)."""
    agent_name: str
    summary: str    # 한국어, 한 문장

    def to_dict(self) -> dict:
        return {"agent_name": self.agent_name, "summary": self.summary}


@dataclass(frozen=True)
class PressurePhase:
    start_tick: int
    end_tick: int
    label: str            # 영어 (내부)
    plain_label: str      # 한국어 (UI)
    summary: str          # 한국어 한 문장

    def to_dict(self) -> dict:
        return {
            "start_tick": self.start_tick,
            "end_tick": self.end_tick,
            "label": self.label,
            "plain_label": self.plain_label,
            "summary": self.summary,
        }


@dataclass(frozen=True)
class PressureSummary:
    total_ticks: int
    dominant_world_pressure: str         # 한국어 라벨
    peak_pressure_tick: int
    pressure_phases: tuple[PressurePhase, ...]    # 정확히 3개
    top_agent_pressures: tuple[AgentPressureSummary, ...]
    plain_language_summary: str          # 한국어 3문장 요약

    def to_dict(self) -> dict:
        from engine.observer.episode_outline import resolve_korean_josa as _j
        return {
            "total_ticks": self.total_ticks,
            "dominant_world_pressure": self.dominant_world_pressure,
            "peak_pressure_tick": self.peak_pressure_tick,
            "pressure_phases": [
                {**p.to_dict(), "summary": _j(p.summary)}
                for p in self.pressure_phases
            ],
            "top_agent_pressures": [
                {**a.to_dict(), "summary": _j(a.summary)}
                for a in self.top_agent_pressures
            ],
            "plain_language_summary": _j(self.plain_language_summary),
        }


# ---------------------------------------------------------------------------
# Plain-language pressure dictionary (shared with story_seed_card)
# ---------------------------------------------------------------------------

_PLAIN_PRESSURE = {
    "fear":                  "두려움",
    "hope":                  "희망",
    "shame_self":            "수치심",
    "authority_vigilance":   "권위자의 압박",
    "public_suspicion":      "사람들의 의심",
    "blame_concentration":   "비난이 한쪽으로 몰림",
    "group_tension":         "집단의 긴장",
    "crowd_mood":            "분위기",
    "confusion":             "혼란",
    "grief":                 "슬픔",
}


# ---------------------------------------------------------------------------
# Phase labels (deterministic — early / mid / late)
# ---------------------------------------------------------------------------

_PHASE_LABELS = (
    ("early_pressure_buildup",  "초반"),
    ("mid_pressure_peak",       "중반"),
    ("late_unresolved_drift",   "후반"),
)


# ---------------------------------------------------------------------------
# Phase classification heuristic
# ---------------------------------------------------------------------------

def _split_into_thirds(total_ticks: int) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]]:
    """200 ticks → (1, 67), (68, 134), (135, 200) 등 3등분 (1-indexed inclusive)."""
    if total_ticks <= 0:
        return ((0, 0), (0, 0), (0, 0))
    third = total_ticks // 3
    a = (1, third)
    b = (third + 1, 2 * third)
    c = (2 * third + 1, total_ticks)
    return (a, b, c)


def _dominant_pressure_in_window(
    ticks: list[dict[str, Any]],
    lo: int, hi: int,
) -> str:
    """Return the world pressure that has the highest *peak value* in [lo, hi]."""
    fields = ("authority_vigilance", "public_suspicion",
              "blame_concentration", "crowd_mood")
    peaks: dict[str, float] = {f: 0.0 for f in fields if f != "crowd_mood"}
    mood_peak: str = "calm"
    for t in ticks:
        if not (lo <= t.get("tick", 0) <= hi):
            continue
        w = t.get("world", {})
        for f in peaks:
            v = float(w.get(f, 0.0))
            if v > peaks[f]:
                peaks[f] = v
        m = w.get("crowd_mood", "calm")
        if m in ("agitated", "tense"):
            mood_peak = m

    # Add agent-level fear peak (count of agents with fear ≥ 7.0)
    fear_above_7 = 0
    for t in ticks:
        if not (lo <= t.get("tick", 0) <= hi):
            continue
        for a in t.get("agents", []):
            if float(a.get("fear", 0.0)) >= 7.0:
                fear_above_7 += 1
    # Normalize fear count to 0..1 for comparison (rough)
    fear_score = min(1.0, fear_above_7 / max(1, len(ticks) * 3))

    candidates: dict[str, float] = {
        "fear": fear_score,
        **peaks,
    }
    if mood_peak == "tense":
        candidates["crowd_mood"] = 0.7
    elif mood_peak == "agitated":
        candidates["crowd_mood"] = 0.5

    if not any(v > 0 for v in candidates.values()):
        return "fear"  # default
    return max(candidates.items(), key=lambda kv: kv[1])[0]


def _phase_summary(phase_idx: int, dominant: str, plain_dominant: str) -> str:
    """3 phase별 한국어 요약. josa 후처리는 to_dict / render에서 일괄."""
    if phase_idx == 0:  # early
        return f"초반에는 {plain_dominant}이(가) 빠르게 올라갑니다."
    elif phase_idx == 1:  # mid
        return f"중반에는 {plain_dominant}을(를) 중심으로 여러 압력이 함께 쌓입니다."
    else:  # late
        if dominant in ("fear", "shame_self"):
            return f"후반에는 {plain_dominant}이(가) 가라앉지 않은 채 남습니다."
        return "후반에는 결정되지 않은 긴장이 지속됩니다."


# ---------------------------------------------------------------------------
# Top agent extraction
# ---------------------------------------------------------------------------

def _top_agents(
    ticks: list[dict[str, Any]],
    identity_resolver=None,
    n: int = 3,
) -> list[AgentPressureSummary]:
    """Find agents whose fear/shame stayed elevated longest."""
    elevated_count: dict[str, int] = {}
    for t in ticks:
        for a in t.get("agents", []):
            aid = a["id"]
            if float(a.get("fear", 0.0)) >= 6.0 or \
               float(a.get("shame_self", 0.0)) >= 4.0:
                elevated_count[aid] = elevated_count.get(aid, 0) + 1

    ranked = sorted(elevated_count.items(), key=lambda kv: -kv[1])[:n]
    out: list[AgentPressureSummary] = []
    for aid, count in ranked:
        name = aid
        if identity_resolver is not None:
            name = identity_resolver.agent_label(aid)
        out.append(AgentPressureSummary(
            agent_name=name,
            summary=f"{name}은(는) 약 {count}단계 동안 두려움이나 수치심이 높게 유지되었습니다.",
        ))
    return out


# ---------------------------------------------------------------------------
# Top-level builder
# ---------------------------------------------------------------------------

def build_pressure_summary(
    observer: dict[str, Any],
    identity_resolver=None,
) -> PressureSummary:
    ticks = observer.get("ticks", [])
    total_ticks = len(ticks)
    if total_ticks == 0:
        return PressureSummary(
            total_ticks=0,
            dominant_world_pressure="(데이터 없음)",
            peak_pressure_tick=0,
            pressure_phases=(),
            top_agent_pressures=(),
            plain_language_summary="(시뮬레이션 데이터가 없습니다)",
        )

    thirds = _split_into_thirds(total_ticks)
    phases: list[PressurePhase] = []
    for i, (lo, hi) in enumerate(thirds):
        dom = _dominant_pressure_in_window(ticks, lo, hi)
        plain_dom = _PLAIN_PRESSURE.get(dom, dom)
        label_eng, plain_label = _PHASE_LABELS[i]
        phases.append(PressurePhase(
            start_tick=lo,
            end_tick=hi,
            label=label_eng,
            plain_label=plain_label,
            summary=_phase_summary(i, dom, plain_dom),
        ))

    # overall dominant: max peak of authority_vigilance across run as proxy
    peak_av = 0.0
    peak_tick = 0
    for t in ticks:
        v = float(t.get("world", {}).get("authority_vigilance", 0.0))
        if v > peak_av:
            peak_av = v
            peak_tick = t.get("tick", 0)
    dominant = _dominant_pressure_in_window(ticks, 1, total_ticks)

    top_agents = _top_agents(ticks, identity_resolver=identity_resolver, n=3)

    plain_summary = " ".join(p.summary for p in phases)

    return PressureSummary(
        total_ticks=total_ticks,
        dominant_world_pressure=_PLAIN_PRESSURE.get(dominant, dominant),
        peak_pressure_tick=peak_tick,
        pressure_phases=tuple(phases),
        top_agent_pressures=tuple(top_agents),
        plain_language_summary=plain_summary,
    )
