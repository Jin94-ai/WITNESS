"""StorySeedCard — Stage 6 (일반인용 이야기 씨앗 카드).

Per `docs/WITNESS_PORTFOLIO_DEMO_PIPELINE_PLAN.md` §6.

StoryCandidate (검증자용) → StorySeedCard (일반인용) 변환기.

핵심 규칙 (plan §9):
    - 한국어 plain language (tick / source / co-occurrence 사용 금지)
    - conflict label → 일반 제목 lookup
    - pressure name → 일반 단어 lookup
    - 한 카드 200~350자
    - 없는 사건 / 대사 / 감정 과잉 표현 금지

Forbidden expressions (plan §9.1) 유지 — story_audit 활용 가능.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.observer.scene_brief import SceneBrief
from engine.observer.story_candidate import StoryCandidate
from engine.observer.story_viability import ViabilityScore

# ---------------------------------------------------------------------------
# Plain-language lookups (plan §6.X + §9.2)
# ---------------------------------------------------------------------------

_PLAIN_TITLE_BY_CONFLICT: dict[str, str] = {
    "loyalty_vs_survival":             "침묵으로 변해가는 충성",
    "uncertainty_vs_commitment":       "결정을 미루는 사람",
    "control_vs_exposure":             "드러날수록 조여오는 통제",
    "collective_fear_vs_scapegoating": "두려움이 누군가를 가리킬 때",
    "identity_vs_failure":             "무너진 자리에서 남는 이름",
    "atmosphere_vs_action":            "아무도 움직이지 않는 방",
    "trust_vs_self_protection":        "거리를 두기 시작하는 마음",
    "unknown":                         "정리되지 않은 긴장",
}


_PLAIN_PREMISE_BY_CONFLICT: dict[str, str] = {
    "loyalty_vs_survival": (
        "{main}은(는) 끝까지 곁에 남고 싶다. 하지만 사람들의 시선과 권위자의 "
        "압박이 커질수록, 점점 말하지 않는 쪽을 선택하게 된다."
    ),
    "uncertainty_vs_commitment": (
        "{main}은(는) 그룹 옆에 머물지만, 주변의 압력이 올라가는 동안 "
        "어떤 결정도 내리지 못한 채 표류한다."
    ),
    "control_vs_exposure": (
        "{main}을(를) 둘러싼 통제는 점점 강해지지만, 동시에 사람들의 의심도 "
        "퍼진다. 누가 먼저 무너질지 보이지 않는다."
    ),
    "collective_fear_vs_scapegoating": (
        "그룹 안의 두려움이 한 방향으로 모인다. 누군가가 표적이 되어가지만, "
        "아무도 그 결정을 명시적으로 내리지 않는다."
    ),
    "identity_vs_failure": (
        "{main}의 희망은 흔들리고 수치심이 쌓인다. 자신이 누구라고 불릴지가 "
        "조용히 바뀌어간다."
    ),
    "atmosphere_vs_action": (
        "분위기는 이미 변했지만, 누구도 움직이지 않는다. 결정 없는 시간이 "
        "이어진다."
    ),
    "trust_vs_self_protection": (
        "{main}은(는) 거리를 두기 시작한다. 신뢰가 무너진 건 아니지만, "
        "지키려는 것이 달라진다."
    ),
    "unknown": (
        "{main}은(는) 압력 속에서 변화한다. 그 변화가 어디로 가는지는 아직 "
        "분명하지 않다."
    ),
}


_PLAIN_WHY_INTERESTING: dict[str, str] = {
    "loyalty_vs_survival": (
        "그는 배신자가 되고 싶지 않다. 그런데 살아남으려는 마음이 충성을 "
        "조금씩 침묵으로 바꾼다. 그 변화가 누구에게나 익숙한 형태로 쌓인다."
    ),
    "uncertainty_vs_commitment": (
        "결정하지 않는 것도 결정이다. 머무는 동안 시간은 그를 대신 움직인다."
    ),
    "control_vs_exposure": (
        "감시와 의심은 거울이다. 한쪽이 강해지면 다른 쪽도 비틀려간다."
    ),
    "collective_fear_vs_scapegoating": (
        "두려움은 표적을 찾는다. 누가 결정한 것인지 모를 때 가장 빨리 움직인다."
    ),
    "identity_vs_failure": (
        "이름은 한 번에 잃지 않는다. 작은 실패들이 천천히 그 자리를 갉아먹는다."
    ),
    "atmosphere_vs_action": (
        "분위기만 바뀌는 방이 있다. 행동이 따라오지 않는 시간을 견디는 인물이 "
        "있다."
    ),
    "trust_vs_self_protection": (
        "지키려는 것이 달라지는 순간, 관계는 이미 다른 모양이 된다."
    ),
    "unknown": (
        "결정되지 않은 긴장은 어디로든 발전할 수 있다. 그 분기점이 이 후보의 "
        "씨앗이다."
    ),
}


_PLAIN_SCENE_IMAGE: dict[str, str] = {
    "loyalty_vs_survival": (
        "사람들이 수군거리는 방 안. {main}은(는) 아직 그 자리에 있지만, "
        "더 이상 앞에 나서지 않는다."
    ),
    "uncertainty_vs_commitment": (
        "그룹의 가장자리. {main}은(는) 떠나지도 다가서지도 않은 채 "
        "주변의 변화를 본다."
    ),
    "control_vs_exposure": (
        "한쪽에서는 권위자가 시선을 좁히고, 다른 쪽에서는 사람들이 서로를 "
        "본다. {main}은(는) 그 사이에 있다."
    ),
    "collective_fear_vs_scapegoating": (
        "그룹 전체의 시선이 천천히 한 쪽으로 모인다. 어느 누구도 그 방향을 "
        "선언하지 않는다."
    ),
    "identity_vs_failure": (
        "{main}이(가) 자신이 했던 약속을 떠올리려 한다. 무엇이 남아 있는지가 "
        "분명하지 않다."
    ),
    "atmosphere_vs_action": (
        "분위기는 이미 무거워졌지만, 의자에서 일어서는 사람은 없다."
    ),
    "trust_vs_self_protection": (
        "{main}은(는) 한 발자국 물러선다. 시선은 여전히 같은 사람을 보지만 "
        "거리는 달라졌다."
    ),
    "unknown": (
        "{main}은(는) 변화가 일어나는 자리에 있다. 어느 방향으로 갈지는 "
        "아직 보이지 않는다."
    ),
}


_PLAIN_UNRESOLVED_BY_CONFLICT: dict[str, str] = {
    "loyalty_vs_survival":             "침묵도 충성일까, 아니면 이미 물러선 것일까?",
    "uncertainty_vs_commitment":       "결정의 순간이 올까, 아니면 표류가 계속될까?",
    "control_vs_exposure":             "감시와 의심 중 어느 쪽이 먼저 무너질까?",
    "collective_fear_vs_scapegoating": "두려움이 다음에 누구를 가리킬까?",
    "identity_vs_failure":             "이 자리 이후, 어떤 이름이 남을까?",
    "atmosphere_vs_action":            "분위기 변화가 행동으로 이어질까?",
    "trust_vs_self_protection":        "거리를 두면서도 신뢰는 남을 수 있을까?",
    "unknown":                         "이 변화는 무엇을 향해 가고 있을까?",
}


# Confidence label (Plan §6 — strong_viable / viable_with_gaps / weak / not_viable)
_PLAIN_CONFIDENCE: dict[str, str] = {
    "strong_viable":     "바로 발전 가능한 씨앗",
    "viable_with_gaps":  "보완이 필요한 씨앗",
    "weak_seed":         "아이디어 씨앗",
    "not_viable":        "현 단계에서 부적합",
}


_PLAIN_USABLE_FOR: dict[str, str] = {
    "film_scene":        "단편 영화 장면",
    "novel_chapter":     "소설 챕터",
    "game_quest_branch": "게임 선택지",
    "drama_episode":     "드라마 에피소드",
    "documentary_segment": "다큐 단편",
    "short_story":       "단편 소설",
    "game_branch":       "게임 분기",
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EvidenceSummary:
    source_thread_id: str
    evidence_count: int
    strongest_signals: tuple[str, ...]   # 일반인용 단어로 변환된 신호
    audit_status: str                    # "통과" / "주의" / "실패"
    technical_link: str | None = None    # debug folder 등으로의 링크

    def to_dict(self) -> dict:
        return {
            "source_thread_id": self.source_thread_id,
            "evidence_count": self.evidence_count,
            "strongest_signals": list(self.strongest_signals),
            "audit_status": self.audit_status,
            "technical_link": self.technical_link,
        }


@dataclass(frozen=True)
class StorySeedCard:
    """일반인용 이야기 씨앗 카드.

    Plan §6.0 model. Forbidden expressions (plan §9.1) 자동 검증 가능.
    """
    seed_id: str                         # "S01"
    title: str                           # "침묵으로 변해가는 충성"
    subtitle: str                        # 한국어 한 줄 부제 (예: "{name} - 한 줄 라벨")
    main_character: str                  # display name from identity_map
    plain_premise: str                   # 한국어 2-3 문장
    why_interesting: str                 # 한국어 2-3 문장
    scene_image: str                     # 한국어 1-2 문장 (장면 이미지)
    unresolved_question: str             # 한국어 한 문장
    usable_for: tuple[str, ...]          # 한국어 매체 라벨
    confidence_label: str                # "바로 발전 가능한 씨앗" 등
    evidence_summary: EvidenceSummary
    risk_note: str                       # "없는 사건을 추가하지 않음" 등

    def to_dict(self) -> dict:
        # 한국어 josa 후처리 일괄 적용 (engine/observer/episode_outline.resolve_korean_josa 활용)
        from engine.observer.episode_outline import resolve_korean_josa as _j
        return {
            "seed_id": self.seed_id,
            "title": _j(self.title),
            "subtitle": _j(self.subtitle),
            "main_character": self.main_character,
            "plain_premise": _j(self.plain_premise),
            "why_interesting": _j(self.why_interesting),
            "scene_image": _j(self.scene_image),
            "unresolved_question": _j(self.unresolved_question),
            "usable_for": list(self.usable_for),
            "confidence_label": self.confidence_label,
            "evidence_summary": self.evidence_summary.to_dict(),
            "risk_note": _j(self.risk_note),
        }


# ---------------------------------------------------------------------------
# Pressure name translation (plan §3 + §9.2 부분)
# ---------------------------------------------------------------------------

_PLAIN_PRESSURE: dict[str, str] = {
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


_PHRASE_TO_PRESSURE: dict[str, str] = {
    "fear intensifies":             "fear",
    "fear eases":                   "fear",
    "hope steadies":                "hope",
    "resolve weakens":              "hope",
    "shame accumulates":            "shame_self",
    "shame relaxes":                "shame_self",
    "authority pressure closes in": "authority_vigilance",
    "authority pressure recedes":   "authority_vigilance",
    "public suspicion rises":       "public_suspicion",
    "public suspicion settles":     "public_suspicion",
    "blame begins to concentrate":  "blame_concentration",
    "blame disperses":              "blame_concentration",
    "group tension sharpens":       "group_tension",
    "group tension softens":        "group_tension",
    "crowd mood shifts":            "crowd_mood",
}


def _translate_signals_to_korean(c: StoryCandidate) -> tuple[str, ...]:
    """world_pressure_context phrases + turning point labels을 한국어 단어로 변환."""
    out: list[str] = []
    # world_pressure_context는 영어 phrase ("fear intensifies" 등)
    for phrase in c.world_pressure_context:
        pressure_key = _PHRASE_TO_PRESSURE.get(phrase)
        if pressure_key:
            translated = _PLAIN_PRESSURE.get(pressure_key)
            if translated and translated not in out:
                out.append(translated)
    # turning point label도 의미있는 시그널로 추가
    if any(tp.label == "sustained pressure begins" for tp in c.key_turning_points):
        if "지속되는 압력" not in out:
            out.append("지속되는 압력")
    if any(tp.label == "co-occurring pressure" for tp in c.key_turning_points):
        if "동시에 겹친 변화" not in out:
            out.append("동시에 겹친 변화")
    if any(tp.moment_ids and "unresolved" in str(tp.summary).lower()
           for tp in c.key_turning_points):
        if "풀리지 않은 긴장" not in out:
            out.append("풀리지 않은 긴장")
    return tuple(out[:5])  # 최대 5개


def _translate_usable_formats(c: StoryCandidate) -> tuple[str, ...]:
    out: list[str] = []
    for fmt in c.usable_formats:
        plain = _PLAIN_USABLE_FOR.get(fmt)
        if plain and plain not in out:
            out.append(plain)
    return tuple(out)


# ---------------------------------------------------------------------------
# Subtitle generation (one short line)
# ---------------------------------------------------------------------------

_SUBTITLE_BY_CONFLICT: dict[str, str] = {
    "loyalty_vs_survival":             "{main} — 충성과 생존 사이",
    "uncertainty_vs_commitment":       "{main} — 결정 없는 시간",
    "control_vs_exposure":             "{main} — 감시와 의심 사이",
    "collective_fear_vs_scapegoating": "그룹 — 두려움이 향하는 곳",
    "identity_vs_failure":             "{main} — 잃어가는 이름",
    "atmosphere_vs_action":            "분위기만 바뀌는 시간",
    "trust_vs_self_protection":        "{main} — 거리를 두는 마음",
    "unknown":                         "{main} — 정리되지 않은 변화",
}


# ---------------------------------------------------------------------------
# Audit-status translation
# ---------------------------------------------------------------------------

_AUDIT_STATUS_PLAIN: dict[str, str] = {
    "pass":        "통과",
    "risky":       "주의",
    "audit_fail":  "실패",
}


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

def build_seed_card(
    candidate: StoryCandidate,
    brief: SceneBrief,
    score: ViabilityScore,
    audit_overall_status: str = "pass",
    evidence=None,
) -> StorySeedCard:
    """Build StorySeedCard from internal artifacts.

    If `evidence` (NarrativeEvidence) is provided, plain_premise / why_interesting
    / scene_image are produced from observer data, so different seeds yield
    different body text. Without evidence the older lookup-based templates
    are used as fallback.
    """
    main = candidate.main_characters[0] if candidate.main_characters else "(인물 미상)"
    conflict = candidate.core_conflict or "unknown"

    title = _PLAIN_TITLE_BY_CONFLICT.get(conflict, _PLAIN_TITLE_BY_CONFLICT["unknown"])
    subtitle = _SUBTITLE_BY_CONFLICT.get(conflict,
                                          _SUBTITLE_BY_CONFLICT["unknown"]
                                         ).format(main=main)

    if evidence is not None:
        from engine.observer.data_narrative import (
            evidence_to_premise,
            evidence_to_scene_image,
            evidence_to_why_interesting,
        )
        premise = evidence_to_premise(evidence)
        why = evidence_to_why_interesting(evidence)
        scene = evidence_to_scene_image(evidence)
    else:
        premise = _PLAIN_PREMISE_BY_CONFLICT.get(
            conflict, _PLAIN_PREMISE_BY_CONFLICT["unknown"]
        ).format(main=main)
        why = _PLAIN_WHY_INTERESTING.get(
            conflict, _PLAIN_WHY_INTERESTING["unknown"]
        )
        scene = _PLAIN_SCENE_IMAGE.get(
            conflict, _PLAIN_SCENE_IMAGE["unknown"]
        ).format(main=main)
    unresolved = _PLAIN_UNRESOLVED_BY_CONFLICT.get(
        conflict, _PLAIN_UNRESOLVED_BY_CONFLICT["unknown"]
    )

    confidence = _PLAIN_CONFIDENCE.get(score.grade, score.grade)
    usable = _translate_usable_formats(candidate)

    evidence = EvidenceSummary(
        source_thread_id=candidate.source_thread_id,
        evidence_count=sum(candidate.provenance_summary.values()),
        strongest_signals=_translate_signals_to_korean(candidate),
        audit_status=_AUDIT_STATUS_PLAIN.get(audit_overall_status, audit_overall_status),
    )

    risk_note = "없는 사건을 추가하지 않음. 대사를 만들지 않음."

    return StorySeedCard(
        seed_id=candidate.story_candidate_id,
        title=title,
        subtitle=subtitle,
        main_character=main,
        plain_premise=premise,
        why_interesting=why,
        scene_image=scene,
        unresolved_question=unresolved,
        usable_for=usable,
        confidence_label=confidence,
        evidence_summary=evidence,
        risk_note=risk_note,
    )
