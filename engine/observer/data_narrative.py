"""Data Narrative — Stage 7 (data-driven 합성기).

Per `WITNESS_PORTFOLIO_DEMO_PIPELINE_PLAN.md` 후속 directive (data-driven
synthesizer). 기존 episode_outline / story_seed_card는 *conflict 라벨 lookup*
으로 본문을 만들어 seed가 달라져도 동일한 텍스트가 나오는 한계가 있었다.

이 모듈은 observer dump (실제 시뮬레이션 산출물)에서 *그 run에서 일어난 일*을
숫자로 뽑아 NarrativeEvidence로 만들고, 자연어 한국어 문장으로 변환한다.

원칙:
    - 없는 사건 / 대사 / 구체 행동 추가 금지 (Plan §10/§14.4 유지)
    - 모든 본문은 observer 수치에서 직접 유도되어야 함
    - 한국어 plain language (tick / pressure / co-occurrence 사용 금지)
    - identity_resolver를 통해 agent_id → 한국어 이름 변환
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# ---------------------------------------------------------------------------
# Plain-language pressure / event dictionaries
# ---------------------------------------------------------------------------

_PLAIN_PRESSURE: dict[str, str] = {
    "fear":                  "두려움",
    "hope":                  "희망",
    "shame_self":            "수치심",
    "authority_vigilance":   "권위자의 압박",
    "public_suspicion":      "사람들의 의심",
    "blame_concentration":   "비난이 한쪽으로 몰리는 흐름",
    "crowd_mood":            "분위기",
    "group_tension":         "집단의 긴장",
}


_PLAIN_STATE: dict[str, str] = {
    "calm":         "평정",
    "tense":        "긴장",
    "fragmenting":  "흔들림",
    "anxious":      "불안",
    "desperate":    "절박함",
    "withdrawn":    "물러섬",
    "agitated":     "동요",
}


_PLAIN_EVENT: dict[str, str] = {
    "discussion_emitted":   "토론이 일어남",
    "public_denial":        "공개적 부인",
    "public_confession":    "공개적 고백",
    "public_accusation":    "공개적 비난",
    "visible_grief":        "겉으로 드러나는 슬픔",
    "visible_withdrawal":   "사람들 앞에서 물러섬",
    "guard_approaches":     "권위자가 다가옴",
    "forgiveness_emitted":  "용서를 표현함",
}


# ---------------------------------------------------------------------------
# NarrativeEvidence dataclass
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PressurePeak:
    """One agent or world-level pressure peak observation."""
    pressure: str               # 'fear' / 'authority_vigilance' / ...
    plain_pressure: str         # '두려움' / '권위자의 압박' / ...
    peak_value: float
    sustained_ticks: int        # 임계치 이상 유지 단계 수
    peak_tick: int              # peak가 일어난 단계


@dataclass(frozen=True)
class CoOccurrence:
    """Two pressures elevated at the same tick."""
    tick: int
    pressure_a: str
    pressure_b: str
    plain_a: str
    plain_b: str


@dataclass(frozen=True)
class StateTransition:
    """One agent's dominant_state change observation."""
    agent_id: str
    agent_name: str
    from_state: str
    to_state: str
    plain_from: str
    plain_to: str
    transition_tick: int


@dataclass(frozen=True)
class NarrativeEvidence:
    """Structured evidence extracted from one observer dump.

    Different seeds → different numbers → different narrative content.
    """
    total_ticks: int
    main_agent_id: str
    main_agent_name: str

    main_agent_pressure_peaks: tuple[PressurePeak, ...]   # 주인공의 압력 peaks
    main_agent_state_transitions: tuple[StateTransition, ...]
    main_agent_action_count_early: int   # 초반 1/3 동안 active_events 등장 횟수
    main_agent_action_count_late: int    # 후반 1/3 동안 active_events 등장 횟수

    world_co_occurrences: tuple[CoOccurrence, ...]   # 세계 레벨 동시 압력
    dominant_world_pressure: str              # 'fear' / 'authority_vigilance' ...
    dominant_world_pressure_plain: str
    dominant_pressure_phase: int              # 0 = 초반, 1 = 중반, 2 = 후반
    crowd_tense_ticks: int                    # 분위기가 tense / agitated인 단계 수

    salient_event_summary: tuple[tuple[str, int], ...]   # [('public_denial', 4), ...]
                                                          # main_agent 한정

    def to_dict(self) -> dict:
        return {
            "total_ticks": self.total_ticks,
            "main_agent_id": self.main_agent_id,
            "main_agent_name": self.main_agent_name,
            "main_agent_pressure_peaks": [
                {
                    "pressure": p.pressure,
                    "plain_pressure": p.plain_pressure,
                    "peak_value": p.peak_value,
                    "sustained_ticks": p.sustained_ticks,
                    "peak_tick": p.peak_tick,
                }
                for p in self.main_agent_pressure_peaks
            ],
            "main_agent_state_transitions": [
                {
                    "agent_id": s.agent_id,
                    "agent_name": s.agent_name,
                    "from_state": s.from_state,
                    "to_state": s.to_state,
                    "plain_from": s.plain_from,
                    "plain_to": s.plain_to,
                    "transition_tick": s.transition_tick,
                }
                for s in self.main_agent_state_transitions
            ],
            "main_agent_action_count_early": self.main_agent_action_count_early,
            "main_agent_action_count_late": self.main_agent_action_count_late,
            "world_co_occurrences": [
                {
                    "tick": c.tick, "pressure_a": c.pressure_a,
                    "pressure_b": c.pressure_b,
                    "plain_a": c.plain_a, "plain_b": c.plain_b,
                }
                for c in self.world_co_occurrences
            ],
            "dominant_world_pressure": self.dominant_world_pressure,
            "dominant_world_pressure_plain": self.dominant_world_pressure_plain,
            "dominant_pressure_phase": self.dominant_pressure_phase,
            "crowd_tense_ticks": self.crowd_tense_ticks,
            "salient_event_summary": list(self.salient_event_summary),
        }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

# 주인공 후보의 ID를 식별. main_characters[0]은 표시 이름이라 직접 매칭이 안 될 수
# 있어서, identity_resolver로 *역참조*하거나 agent fear/shame이 가장 높은
# agent를 main으로 본다 (관측 기반 fallback).
def _resolve_main_agent_id(
    candidate_main_name: str,
    ticks: list[dict[str, Any]],
    identity_resolver,
) -> str:
    if identity_resolver is not None:
        # forward lookup: 모든 agent_id를 돌려서 label이 candidate_main_name과
        # 일치하는 첫 항목을 찾는다.
        agent_ids = set()
        for t in ticks[:5]:
            for a in t.get("agents", []):
                agent_ids.add(a["id"])
        for aid in agent_ids:
            if identity_resolver.agent_label(aid) == candidate_main_name:
                return aid
    # Fallback: 두려움 / 수치심 누적이 가장 큰 agent
    cum: dict[str, float] = {}
    for t in ticks:
        for a in t.get("agents", []):
            cum[a["id"]] = cum.get(a["id"], 0.0) + \
                float(a.get("fear", 0.0)) + float(a.get("shame_self", 0.0))
    if not cum:
        return "agent_01"
    return max(cum.items(), key=lambda kv: kv[1])[0]


def _extract_main_agent_pressure_peaks(
    ticks: list[dict[str, Any]],
    main_id: str,
) -> list[PressurePeak]:
    """주인공의 fear / shame_self / hope 약화 peaks 추출."""
    fear_series: list[tuple[int, float]] = []
    shame_series: list[tuple[int, float]] = []
    hope_series: list[tuple[int, float]] = []
    for t in ticks:
        for a in t.get("agents", []):
            if a["id"] != main_id:
                continue
            tick_n = t.get("tick", 0)
            fear_series.append((tick_n, float(a.get("fear", 0.0))))
            shame_series.append((tick_n, float(a.get("shame_self", 0.0))))
            hope_series.append((tick_n, float(a.get("hope", 0.0))))

    peaks: list[PressurePeak] = []

    def _summarize(series: list[tuple[int, float]],
                    name: str, threshold: float) -> PressurePeak | None:
        if not series:
            return None
        peak_tick, peak_val = max(series, key=lambda kv: kv[1])
        if peak_val < threshold:
            return None
        sustained = sum(1 for _, v in series if v >= threshold)
        return PressurePeak(
            pressure=name,
            plain_pressure=_PLAIN_PRESSURE.get(name, name),
            peak_value=round(peak_val, 2),
            sustained_ticks=sustained,
            peak_tick=peak_tick,
        )

    fp = _summarize(fear_series, "fear", 5.0)
    if fp:
        peaks.append(fp)
    sp = _summarize(shame_series, "shame_self", 3.0)
    if sp:
        peaks.append(sp)

    # hope의 *약화*: peak 대비 가장 낮은 값
    if hope_series:
        max_hope = max(v for _, v in hope_series)
        min_hope = min(v for _, v in hope_series)
        if max_hope - min_hope >= 2.0:
            min_tick = next(
                (k for k, v in hope_series if v == min_hope), 0
            )
            low_count = sum(1 for _, v in hope_series if v <= min_hope + 1.0)
            peaks.append(PressurePeak(
                pressure="hope",
                plain_pressure="희망의 약화",
                peak_value=round(max_hope - min_hope, 2),
                sustained_ticks=low_count,
                peak_tick=min_tick,
            ))

    return peaks


def _extract_main_agent_state_transitions(
    ticks: list[dict[str, Any]],
    main_id: str,
    identity_resolver,
) -> list[StateTransition]:
    """주인공의 dominant_state 변화 시점 (consecutive change만, 첫 N개)."""
    last_state: str | None = None
    transitions: list[StateTransition] = []
    name = identity_resolver.agent_label(main_id) if identity_resolver else main_id
    for t in ticks:
        for a in t.get("agents", []):
            if a["id"] != main_id:
                continue
            cur = a.get("dominant_state", "calm")
            if last_state is not None and cur != last_state:
                transitions.append(StateTransition(
                    agent_id=main_id,
                    agent_name=name,
                    from_state=last_state,
                    to_state=cur,
                    plain_from=_PLAIN_STATE.get(last_state, last_state),
                    plain_to=_PLAIN_STATE.get(cur, cur),
                    transition_tick=t.get("tick", 0),
                ))
            last_state = cur
            break
    return transitions


def _count_main_agent_events(
    ticks: list[dict[str, Any]],
    main_id: str,
    lo: int, hi: int,
) -> int:
    """주인공이 *salient* 표시된 단계 수 (제한된 직접 개입 척도)."""
    count = 0
    for t in ticks:
        if not (lo <= t.get("tick", 0) <= hi):
            continue
        for a in t.get("agents", []):
            if a["id"] == main_id and a.get("salient"):
                count += 1
                break
    return count


def _extract_co_occurrences(
    ticks: list[dict[str, Any]],
    threshold_av: float = 0.3,
    threshold_ps: float = 0.3,
    threshold_bc: float = 0.3,
) -> list[CoOccurrence]:
    """세계 레벨 압력 두 개가 동시에 임계 이상인 단계."""
    out: list[CoOccurrence] = []
    seen_pair_ticks: set[tuple[int, str, str]] = set()
    for t in ticks:
        w = t.get("world", {})
        elevated: list[str] = []
        if float(w.get("authority_vigilance", 0.0)) >= threshold_av:
            elevated.append("authority_vigilance")
        if float(w.get("public_suspicion", 0.0)) >= threshold_ps:
            elevated.append("public_suspicion")
        if float(w.get("blame_concentration", 0.0)) >= threshold_bc:
            elevated.append("blame_concentration")
        if w.get("crowd_mood") in ("tense", "agitated"):
            elevated.append("crowd_mood")
        # pair만 (3개 이상은 강한 신호이므로 첫 페어로 대표)
        if len(elevated) >= 2:
            a, b = sorted(elevated)[:2]
            key = (t.get("tick", 0) // 10, a, b)  # 10단계 묶음으로 중복 제거
            if key in seen_pair_ticks:
                continue
            seen_pair_ticks.add(key)
            out.append(CoOccurrence(
                tick=t.get("tick", 0),
                pressure_a=a, pressure_b=b,
                plain_a=_PLAIN_PRESSURE.get(a, a),
                plain_b=_PLAIN_PRESSURE.get(b, b),
            ))
    return out


def _dominant_world_pressure(ticks: list[dict[str, Any]]) -> tuple[str, int]:
    """전체 run에서 가장 *peak가 큰* 세계 압력. (key, peak_tick) 반환."""
    fields = ("authority_vigilance", "public_suspicion", "blame_concentration")
    peaks: dict[str, tuple[float, int]] = {f: (0.0, 0) for f in fields}
    tense_count = 0
    for t in ticks:
        w = t.get("world", {})
        for f in fields:
            v = float(w.get(f, 0.0))
            if v > peaks[f][0]:
                peaks[f] = (v, t.get("tick", 0))
        if w.get("crowd_mood") in ("tense", "agitated"):
            tense_count += 1
    # tense_count가 많으면 crowd_mood를 우선 후보로
    candidates = list(peaks.items())
    candidates.sort(key=lambda kv: -kv[1][0])
    if candidates and candidates[0][1][0] > 0.0:
        return candidates[0][0], candidates[0][1][1]
    return "crowd_mood", 0


def _crowd_tense_ticks(ticks: list[dict[str, Any]]) -> int:
    return sum(
        1 for t in ticks
        if t.get("world", {}).get("crowd_mood") in ("tense", "agitated")
    )


def _phase_of_tick(tick: int, total: int) -> int:
    if total <= 0:
        return 0
    third = total / 3.0
    if tick <= third:
        return 0
    if tick <= 2 * third:
        return 1
    return 2


def _salient_events_for_main(
    ticks: list[dict[str, Any]],
    main_id: str,
) -> list[tuple[str, int]]:
    """Main agent가 salient한 단계의 active_events 카운트."""
    from collections import Counter
    cnt: Counter[str] = Counter()
    for t in ticks:
        is_main_salient = any(
            a["id"] == main_id and a.get("salient")
            for a in t.get("agents", [])
        )
        if not is_main_salient:
            continue
        for ev in t.get("active_events", []):
            cnt[ev] += 1
    return cnt.most_common(5)


# ---------------------------------------------------------------------------
# Top-level extractor
# ---------------------------------------------------------------------------

def extract_narrative_evidence(
    observer: dict[str, Any],
    main_character_name: str,
    identity_resolver=None,
) -> NarrativeEvidence:
    """Observer dump → NarrativeEvidence (data-driven 본문 합성용 입력).

    Different seeds with different observer outputs will produce different
    NarrativeEvidence values, which the natural-language renderers below
    convert into different Korean body text.
    """
    ticks = observer.get("ticks", [])
    total = len(ticks)
    main_id = _resolve_main_agent_id(main_character_name, ticks, identity_resolver)

    peaks = _extract_main_agent_pressure_peaks(ticks, main_id)
    transitions = _extract_main_agent_state_transitions(
        ticks, main_id, identity_resolver
    )

    early_lo, early_hi = 1, max(1, total // 3)
    late_lo, late_hi = max(1, 2 * total // 3 + 1), total
    early_acts = _count_main_agent_events(ticks, main_id, early_lo, early_hi)
    late_acts = _count_main_agent_events(ticks, main_id, late_lo, late_hi)

    cooc = _extract_co_occurrences(ticks)
    dom_pressure, dom_tick = _dominant_world_pressure(ticks)
    dom_phase = _phase_of_tick(dom_tick, total)

    return NarrativeEvidence(
        total_ticks=total,
        main_agent_id=main_id,
        main_agent_name=main_character_name,
        main_agent_pressure_peaks=tuple(peaks),
        main_agent_state_transitions=tuple(transitions[:8]),
        main_agent_action_count_early=early_acts,
        main_agent_action_count_late=late_acts,
        world_co_occurrences=tuple(cooc[:6]),
        dominant_world_pressure=dom_pressure,
        dominant_world_pressure_plain=_PLAIN_PRESSURE.get(dom_pressure, dom_pressure),
        dominant_pressure_phase=dom_phase,
        crowd_tense_ticks=_crowd_tense_ticks(ticks),
        salient_event_summary=tuple(_salient_events_for_main(ticks, main_id)),
    )


# ---------------------------------------------------------------------------
# Natural-language renderers (한국어 plain language)
# ---------------------------------------------------------------------------

def _phase_plain(phase_idx: int) -> str:
    return {0: "초반", 1: "중반", 2: "후반"}.get(phase_idx, "")


def evidence_to_logline(ev: NarrativeEvidence) -> str:
    """NarrativeEvidence → 한 줄 logline (한국어).

    핵심 압력 + 주인공 + 가장 두드러진 변화. josa는 후처리에서 해결.
    """
    name = ev.main_agent_name
    parts: list[str] = []

    # 1) 주인공의 가장 두드러진 압력
    if ev.main_agent_pressure_peaks:
        p = ev.main_agent_pressure_peaks[0]
        parts.append(
            f"{name}의 {p.plain_pressure}이(가) "
            f"{ev.total_ticks}단계 중 약 {p.sustained_ticks}단계 동안 가라앉지 않는다"
        )
    else:
        parts.append(f"{name}은(는) 압력이 누적되는 자리에 있다")

    # 2) 세계의 dominant pressure
    if ev.dominant_world_pressure_plain:
        phase = _phase_plain(ev.dominant_pressure_phase)
        if phase:
            parts.append(
                f"같은 시간 동안 {ev.dominant_world_pressure_plain}이(가) "
                f"{phase}에 가장 강해진다"
            )

    return ". ".join(parts) + "."


def evidence_to_act_summary(ev: NarrativeEvidence, phase_idx: int) -> str:
    """phase_idx (0/1/2) → 그 phase에서 데이터가 보여준 사실 한국어 문장.

    Act 1 / 2 / 3 builder에서 호출.
    """
    phase_name = _phase_plain(phase_idx)
    name = ev.main_agent_name

    # 그 phase에 일어난 transitions
    if ev.total_ticks > 0:
        third = ev.total_ticks / 3.0
        lo = phase_idx * third
        hi = (phase_idx + 1) * third
        phase_transitions = [
            t for t in ev.main_agent_state_transitions
            if lo < t.transition_tick <= hi
        ]
    else:
        phase_transitions = []

    parts: list[str] = []

    if phase_idx == 0:
        # 초반: 주인공의 *시작 상태* + 첫 변화
        parts.append(f"{phase_name}에는 {name}이(가) 그룹 안에 머물러 있다")
        if phase_transitions:
            t0 = phase_transitions[0]
            parts.append(
                f"{t0.transition_tick}단계 부근에서 {t0.plain_from}에서 "
                f"{t0.plain_to}으로(로) 첫 변화가 일어난다"
            )
        if ev.main_agent_action_count_early > 0:
            parts.append(
                f"이 단계 동안 {name}이(가) 두드러지게 보인 단계는 "
                f"{ev.main_agent_action_count_early}회이다"
            )
    elif phase_idx == 1:
        # 중반: 압력 누적
        if ev.world_co_occurrences:
            cooc = ev.world_co_occurrences[len(ev.world_co_occurrences) // 2]
            parts.append(
                f"{phase_name}에는 {cooc.plain_a}과(와) {cooc.plain_b}이(가) "
                f"같은 시간대에 함께 올라간다"
            )
        else:
            parts.append(
                f"{phase_name}에는 {ev.dominant_world_pressure_plain}이(가) 누적된다"
            )
        if phase_transitions:
            t0 = phase_transitions[0]
            parts.append(
                f"{name}의 상태는 {t0.plain_from}에서 {t0.plain_to}으로(로) 바뀐다"
            )
    else:
        # 후반: 가라앉지 않은 긴장
        if ev.main_agent_pressure_peaks:
            p = ev.main_agent_pressure_peaks[0]
            parts.append(
                f"{phase_name}에는 {name}의 {p.plain_pressure}이(가) "
                f"가라앉지 않은 채 남는다"
            )
        if ev.main_agent_action_count_late < ev.main_agent_action_count_early:
            parts.append(
                f"{name}이(가) 두드러지는 단계 수는 초반 "
                f"{ev.main_agent_action_count_early}회에서 "
                f"{ev.main_agent_action_count_late}회로 줄어든다"
            )
        elif ev.main_agent_action_count_late > 0:
            parts.append(
                f"{name}이(가) 두드러지게 보인 단계는 후반에 "
                f"{ev.main_agent_action_count_late}회이다"
            )

    return ". ".join(parts) + "." if parts else (
        f"{phase_name}에는 결정되지 않은 흐름이 이어진다."
    )


def evidence_to_why(ev: NarrativeEvidence) -> str:
    """NarrativeEvidence → '왜 하나의 이야기처럼 읽히는가' 한국어 단락.

    실제 데이터에 있는 *수치*를 인용해서 만든다.
    """
    name = ev.main_agent_name
    bits: list[str] = []

    # 1) 주인공 압력
    if ev.main_agent_pressure_peaks:
        p = ev.main_agent_pressure_peaks[0]
        bits.append(
            f"{name}의 {p.plain_pressure}이(가) {ev.total_ticks}단계 중 "
            f"약 {p.sustained_ticks}단계 동안 높게 유지된다"
        )

    # 2) co-occurrence
    if ev.world_co_occurrences:
        cooc = ev.world_co_occurrences[0]
        bits.append(
            f"{cooc.plain_a}과(와) {cooc.plain_b}이(가) 같은 시간대에 "
            f"함께 올라가는 단계가 관측된다"
        )

    # 3) action 변화
    if ev.main_agent_action_count_late < ev.main_agent_action_count_early and \
       ev.main_agent_action_count_early > 0:
        bits.append(
            f"{name}이(가) 두드러지는 단계 수가 초반 "
            f"{ev.main_agent_action_count_early}회에서 후반 "
            f"{ev.main_agent_action_count_late}회로 줄어든다"
        )

    # 4) crowd_mood 누적
    if ev.crowd_tense_ticks > 0 and ev.total_ticks > 0:
        ratio = ev.crowd_tense_ticks * 100 // max(1, ev.total_ticks)
        bits.append(
            f"전체 단계의 약 {ratio}%에서 분위기가 긴장 또는 동요로 표시된다"
        )

    if not bits:
        return (
            f"이 데이터에서 {name} 중심으로 의미 있는 변화 신호가 약하게만 나타난다. "
            f"창작자가 더 발전시킬 여지가 있다."
        )

    body = "; ".join(bits)
    closer = (
        ". 이 흐름은 한 사건이 아니라 여러 신호가 같은 시간대에 겹쳐서 만들어진 "
        "것이다. 그 점이 단편적인 인상을 *하나의 이야기*로 묶는다."
    )
    return body + closer


def evidence_to_premise(ev: NarrativeEvidence) -> str:
    """씨앗 카드 plain_premise — 데이터 근거의 두 문장."""
    name = ev.main_agent_name
    sentences: list[str] = []

    if ev.main_agent_pressure_peaks:
        p = ev.main_agent_pressure_peaks[0]
        sentences.append(
            f"{name}의 {p.plain_pressure}은(는) {ev.total_ticks}단계 중 "
            f"약 {p.sustained_ticks}단계 동안 높게 유지된다"
        )
    else:
        sentences.append(
            f"{name}은(는) 압력이 누적되는 자리에 있지만 강한 변화는 약하다"
        )

    if ev.main_agent_action_count_late < ev.main_agent_action_count_early and \
       ev.main_agent_action_count_early > 0:
        sentences.append(
            "같은 사람이 두드러지게 보이는 단계는 후반으로 갈수록 줄어든다"
        )
    elif ev.main_agent_state_transitions:
        last = ev.main_agent_state_transitions[-1]
        sentences.append(
            f"마지막에 관측된 상태 변화는 {last.plain_from}에서 "
            f"{last.plain_to}으로(로)이다"
        )
    else:
        sentences.append(
            f"같은 시간 동안 {ev.dominant_world_pressure_plain}이(가) 세계 전체에서 "
            f"가장 강하게 표시된다"
        )

    return ". ".join(sentences) + "."


def evidence_to_scene_image(ev: NarrativeEvidence) -> str:
    """씨앗 카드 scene_image — 데이터에서 보이는 단순 이미지 1-2 문장.

    구체적 장면 묘사가 아니라 *데이터에 표시된 자리*를 가리킴.
    """
    name = ev.main_agent_name

    if ev.main_agent_state_transitions:
        last = ev.main_agent_state_transitions[-1]
        return (
            f"같은 그룹 안에 {name}이(가) 머물러 있는 자리. "
            f"{last.transition_tick}단계 부근에서 그의 상태는 "
            f"{last.plain_from}에서 {last.plain_to}으로(로) 바뀌어 있다."
        )

    if ev.main_agent_pressure_peaks:
        p = ev.main_agent_pressure_peaks[0]
        return (
            f"{name}의 {p.plain_pressure}이(가) 가장 강하게 표시된 "
            f"{p.peak_tick}단계 부근의 자리. 주변 그룹은 함께 움직이지 않는다."
        )

    return (
        f"{name}이(가) 그룹 안에 남아 있는 자리. "
        f"세계 전체에서는 {ev.dominant_world_pressure_plain}이(가) 가장 강하게 "
        f"표시되어 있다."
    )


def evidence_to_why_interesting(ev: NarrativeEvidence) -> str:
    """씨앗 카드 why_interesting — 데이터의 *흥미로운 점* 한 두 문장."""
    name = ev.main_agent_name

    if ev.main_agent_pressure_peaks and \
       ev.main_agent_action_count_late < ev.main_agent_action_count_early:
        p = ev.main_agent_pressure_peaks[0]
        return (
            f"{name}의 {p.plain_pressure}은(는) 줄어들지 않지만, "
            f"같은 사람이 두드러지게 보이는 단계 수는 후반으로 갈수록 줄어든다. "
            f"내적 압력과 외적 행동이 같은 방향으로 가지 않는다는 점이 특이하다."
        )

    if ev.world_co_occurrences:
        cooc = ev.world_co_occurrences[0]
        return (
            f"{cooc.plain_a}과(와) {cooc.plain_b}이(가) 같은 시간대에 함께 "
            f"올라간다. 두 압력이 따로 움직이지 않는다는 점이 이 데이터의 특징이다."
        )

    return (
        f"이 후보는 단일 사건이 아니라 {ev.total_ticks}단계에 걸친 "
        f"누적 흐름이다. 한 시점이 아닌 시간의 폭이 의미를 만든다."
    )


# ---------------------------------------------------------------------------
# Qualitative descriptors (NUMBER-FREE — for general-audience main display)
#
# Per directive 2026-05-08: 메인 영역에는 수치가 들어가면 안 되지만, *질적
# evidence 인용*은 OK ("두려움이 일정 기간 높게 유지됨"). 이 함수들은 같은
# evidence에서 *seed별 패턴*을 정성 표현으로 매핑해, conflict label만으로는
# 만들 수 없는 본문 다양성을 제공한다.
# ---------------------------------------------------------------------------

def _persistence_qualifier(sustained: int, total: int) -> str:
    """압력의 지속 정도를 정성어로 매핑. 수치 노출 0."""
    if total <= 0:
        return ""
    ratio = sustained / total
    if ratio >= 0.30:
        return "오래"
    if ratio >= 0.15:
        return "꾸준히"
    if ratio >= 0.05:
        return "잠시"
    return "거의"


def _action_change_qualifier(early: int, late: int) -> str:
    """초반→후반 행동 빈도 변화를 정성어로 매핑."""
    if early == 0 and late == 0:
        return "거의 드러나지 않는다"
    if late == 0 and early > 0:
        return "후반으로 갈수록 사라진다"
    if early > 0 and late < early / 2:
        return "후반으로 갈수록 눈에 띄게 줄어든다"
    if early > 0 and late < early:
        return "후반으로 갈수록 조금씩 줄어든다"
    if late > early:
        return "후반으로 갈수록 늘어난다"
    return "꾸준히 유지된다"


def _crowd_intensity_qualifier(tense_ticks: int, total: int) -> str:
    """분위기 긴장 비율을 정성어로 매핑."""
    if total <= 0:
        return ""
    ratio = tense_ticks / total
    if ratio >= 0.5:
        return "압도적으로"
    if ratio >= 0.25:
        return "분명히"
    if ratio >= 0.10:
        return "간간이"
    return "거의 없이"


def evidence_to_qualitative_descriptors(ev: NarrativeEvidence) -> dict[str, str]:
    """수치 0인 정성 표현 dict — story-tone fields 보강용.

    Returns 7 fields:
        - main_pressure_plain: 주인공 주된 압력 (한국어)
        - main_pressure_persistence: "오래" / "꾸준히" / "잠시" / "거의"
        - dominant_world_pressure_plain: 세계 dominant pressure
        - crowd_intensity: "압도적으로" / "분명히" / "간간이" / "거의 없이"
        - action_change_phrase: "후반으로 갈수록 사라진다" 등
        - first_state_transition_plain: 첫 상태 변화 ("평정 → 긴장") (수치 X)
        - last_state_transition_plain: 마지막 상태 변화 (수치 X)
    """
    out: dict[str, str] = {}

    # 주인공 main pressure
    if ev.main_agent_pressure_peaks:
        p = ev.main_agent_pressure_peaks[0]
        out["main_pressure_plain"] = p.plain_pressure
        out["main_pressure_persistence"] = _persistence_qualifier(
            p.sustained_ticks, ev.total_ticks
        )
    else:
        out["main_pressure_plain"] = ""
        out["main_pressure_persistence"] = ""

    # 세계 dominant
    out["dominant_world_pressure_plain"] = ev.dominant_world_pressure_plain or ""
    out["crowd_intensity"] = _crowd_intensity_qualifier(
        ev.crowd_tense_ticks, ev.total_ticks
    )

    # 행동 변화
    out["action_change_phrase"] = _action_change_qualifier(
        ev.main_agent_action_count_early, ev.main_agent_action_count_late
    )

    # 상태 변화 (수치 없이 from/to만)
    if ev.main_agent_state_transitions:
        first = ev.main_agent_state_transitions[0]
        out["first_state_transition_plain"] = f"{first.plain_from} → {first.plain_to}"
        last = ev.main_agent_state_transitions[-1]
        out["last_state_transition_plain"] = f"{last.plain_from} → {last.plain_to}"
    else:
        out["first_state_transition_plain"] = ""
        out["last_state_transition_plain"] = ""

    return out


def evidence_to_what_pressures_story(ev: NarrativeEvidence) -> str:
    """주인공이 받는 압박을 *수치 없이* 정성 표현. story-tone 메인용.

    예시:
    - main_pressure 두려움 (오래 유지) + 분위기 압도적: "오래 가라앉지 않는 두려움 위로 무거운 분위기가 압도적으로 눌러온다."
    - 두려움 (잠시) + 분위기 간간이: "두려움은 잠시 지나가지만, 분위기는 간간이 무겁게 머문다."
    """
    desc = evidence_to_qualitative_descriptors(ev)
    main_p = desc["main_pressure_plain"]
    persistence = desc["main_pressure_persistence"]
    crowd = desc["crowd_intensity"]
    dom = desc["dominant_world_pressure_plain"]

    if not main_p:
        return ""

    parts: list[str] = []
    if persistence == "오래":
        parts.append(f"오래 가라앉지 않는 {main_p}")
    elif persistence == "꾸준히":
        parts.append(f"꾸준히 누적되는 {main_p}")
    elif persistence == "잠시":
        parts.append(f"잠시 머물다 가라앉는 {main_p}")
    elif persistence == "거의":
        parts.append(f"잠시 지나가는 {main_p}")
    else:
        parts.append(main_p)

    # crowd intensity는 정성 표현 — 과한 부사 ("압도적으로 눌러온다")는
    # 사용자 directive 후속 (2026-05-08) 따라 약화.
    if crowd == "압도적으로":
        parts.append("그 사이 분위기가 무겁게 이어진다")
    elif crowd == "분명히":
        parts.append(f"{dom or '주변'}이 함께 누적된다")
    elif crowd == "간간이":
        parts.append(f"{dom or '주변'}은 간간이 무겁게 머문다")

    if len(parts) == 1:
        return parts[0] + "이 그를 누른다."
    return parts[0] + ", " + parts[1] + "."


def evidence_to_how_changes_story(ev: NarrativeEvidence) -> str:
    """변화의 방향을 *수치 없이* story-tone으로 표현.

    예시:
    - action 줄어듦 + transition o: "처음에는 자리에 남아 있지만, 평정에서 긴장으로 바뀐 뒤 행동이 후반으로 갈수록 줄어든다."
    - action 사라짐: "처음에는 자리에 남아 있지만, 후반에는 행동이 사라진다."
    """
    desc = evidence_to_qualitative_descriptors(ev)
    action_change = desc["action_change_phrase"]
    first_trans = desc["first_state_transition_plain"]
    last_trans = desc["last_state_transition_plain"]

    parts: list[str] = ["처음에는 자리에 남아 있다"]

    if first_trans:
        parts.append(f"이후 {first_trans}으로(로) 첫 변화가 일어난다")

    if last_trans and last_trans != first_trans:
        parts.append(f"마지막에는 {last_trans}으로(로) 모인다")

    if action_change:
        parts.append(f"행동은 {action_change}")

    return ". ".join(parts) + "."


def evidence_to_three_part_outline_phase3(
    ev: NarrativeEvidence, base_phase3: str,
) -> str:
    """Three-part outline의 phase 3 (전환)에 evidence-aware *정성* 표현 추가.

    Plot 구조 문장 (base_phase3)은 그대로 두고, 행동 변화 정성 표현만 한 절
    덧붙임 — 같은 conflict이라도 seed별 evidence 패턴이 다르면 phase 3 본문도
    살짝 다르게 끝난다. 수치 0 유지.

    Examples (loyalty_vs_survival 기본 phase 3 = "그는 떠나지 않지만, 더 이상
    앞에 나서지도 않는다.")
    - seed 0 (action 8→6 줄어듦): "...앞에 나서지도 않는다. 행동은 후반으로
      갈수록 조금씩 줄어든다."
    - seed 7 (action 8→0 사라짐): "...앞에 나서지도 않는다. 행동은 후반으로
      갈수록 사라진다."
    """
    if ev.main_agent_action_count_early <= 0 and ev.main_agent_action_count_late <= 0:
        # 행동 데이터 없음 → 정성 표현 추가 skip
        return base_phase3
    qualifier = _action_change_qualifier(
        ev.main_agent_action_count_early, ev.main_agent_action_count_late,
    )
    base = base_phase3.rstrip()
    if not base.endswith((".", "?", "!")):
        base = base + "."
    return f"{base} 행동은 {qualifier}."


def evidence_to_one_line_story(ev: NarrativeEvidence, conflict_template: str) -> str:
    """conflict 기반 템플릿에 evidence-aware qualifier를 *수치 없이* 삽입.

    Args:
        ev: NarrativeEvidence
        conflict_template: 기존 _ONE_LINE_STORY_BY_CONFLICT 템플릿 (이미
            {main} 치환된 상태). evidence-aware version은 *템플릿을 수정하지 않고*
            추가 한 문장으로 보강한다 (메인 영역은 두 문장 max).

    Returns:
        original template + evidence-aware *qualifier* sentence.

    예시 (loyalty_vs_survival, seed 0 vs seed 7):
    - seed 0 (오래 + 압도적): "...밀려난다. 두려움이 오래 가라앉지 않고, 무거운 분위기가 압도적으로 눌러온다."
    - seed 7 (잠시 + 간간이): "...밀려난다. 두려움은 잠시 지나가지만, 분위기는 간간이 무겁게 머문다."
    """
    pressures_phrase = evidence_to_what_pressures_story(ev)
    if not pressures_phrase:
        return conflict_template

    # 템플릿 마침표 보장 (이미 . 끝이면 추가 X)
    base = conflict_template.rstrip()
    if not base.endswith((".", "?", "!")):
        base = base + "."

    return f"{base} {pressures_phrase}"
