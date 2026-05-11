"""Episode Outline — Story Assembly Layer.

Per `WITNESS_PORTFOLIO_DEMO_PIPELINE_PLAN` 후속 directive (Story Assembly).

여러 StorySeedCard / StoryCandidate를 *하나의 에피소드 개요*로 조립한다.

규칙:
    - S01 (강한 후보) = Main Arc
    - S02-Sn = Supporting Arcs (역할 라벨은 데이터로 추출)
    - Act 1/2/3은 PressureSummary 3 phase + main arc turning points 매핑
    - 일반인용 한국어
    - 없는 사건 / 대사 / 구체 행동 추가 금지
"""
from __future__ import annotations

from dataclasses import dataclass, field

from engine.observer.pressure_summary import PressureSummary
from engine.observer.story_candidate import StoryCandidate
from engine.observer.story_seed_card import StorySeedCard
from engine.observer.data_narrative import (
    NarrativeEvidence,
    evidence_to_act_summary,
    evidence_to_how_changes_story,
    evidence_to_logline,
    evidence_to_one_line_story,
    evidence_to_three_part_outline_phase3,
    evidence_to_what_pressures_story,
    evidence_to_why,
)


# ---------------------------------------------------------------------------
# Supporting arc role inference (data-driven, not hardcoded per character)
# ---------------------------------------------------------------------------

def _infer_supporting_role(
    sup_candidate: StoryCandidate,
    main_candidate: StoryCandidate,
    total_ticks: int,
) -> str:
    """Supporting arc의 *역할 라벨*을 데이터로부터 추출.

    Heuristic:
      - main과 *같은 그룹 라벨*을 supporting list에 공유하면 "{main}을(를) 지켜보는 목격자"
      - 후반(60%+)에 turning point가 집중되면 "늦게 반응하는 인물"
      - 그 외 / 다른 그룹: "결정을 미루는 사람"
    """
    # supporting_characters_or_groups는 agent name + group label 혼합 tuple.
    # 두 candidate의 supporting set 교집합에서 *agent 이름이 아닌 항목*이
    # 있으면 같은 그룹으로 간주 (group labels은 identity_map에서 온 한국어).
    main_supporting = set(main_candidate.supporting_characters_or_groups)
    sup_supporting = set(sup_candidate.supporting_characters_or_groups)
    shared = main_supporting & sup_supporting
    # main의 main agent name은 sup에 자기 자신으로 들어갈 수 없으므로 제외 단계 불필요.
    # group label은 일반적으로 cluster / 무리 / 그룹 단어 포함하거나 ID 형태.
    # 가장 안전: shared가 있으면 같은 컨텍스트로 봄.
    main_name = main_candidate.main_characters[0] if main_candidate.main_characters else "main"

    if shared:
        return f"{main_name}을(를) 지켜보는 목격자"

    # 후반 turning point 집중 → 늦게 반응
    if sup_candidate.key_turning_points and total_ticks > 0:
        late_threshold = total_ticks * 0.6
        late_ticks = [
            tp for tp in sup_candidate.key_turning_points
            if tp.tick >= late_threshold
        ]
        if len(late_ticks) >= 1 and len(late_ticks) >= len(sup_candidate.key_turning_points) / 2:
            return "늦게 반응하는 인물"

    return "결정을 미루는 사람"


# ---------------------------------------------------------------------------
# Title selection
# ---------------------------------------------------------------------------

# Main conflict별 에피소드 제목. seed card title보다 *조금 더 추상적*.
_EPISODE_TITLE_BY_CONFLICT: dict[str, str] = {
    "loyalty_vs_survival":             "침묵으로 변해가는 밤",
    "uncertainty_vs_commitment":       "결정 없이 흐르는 시간",
    "control_vs_exposure":             "조여드는 시선의 시간",
    "collective_fear_vs_scapegoating": "두려움이 향하는 곳",
    "identity_vs_failure":             "이름이 흔들리는 자리",
    "atmosphere_vs_action":            "움직이지 않는 방",
    "trust_vs_self_protection":        "거리를 두기 시작한 사람들",
    "unknown":                         "정리되지 않은 변화",
}


# ---------------------------------------------------------------------------
# Display-name overlay (general-audience surface).
#
# 이름 매핑 dict는 *content layer* 책임. engine module은 content-agnostic
# 유지 — `display_name_overrides` 인자로 build_episode_outline / 헬퍼에
# 전달받는다.
# ---------------------------------------------------------------------------


def _to_display_name(
    name: str, overrides: dict[str, str] | None,
) -> str:
    """영어 raw name → display name. overrides 없거나 매핑 없으면 그대로."""
    if not overrides:
        return name
    return overrides.get(name, name)


def _name_substitute_in_text(
    text: str, overrides: dict[str, str] | None,
) -> str:
    """텍스트 내 모든 raw name을 display name으로 치환."""
    if not text or not overrides:
        return text
    for raw, display in overrides.items():
        text = text.replace(raw, display)
    return text


def _persistence_qualifier_safe(sustained: int, total: int) -> str:
    """수치 0인 정성 지속 표현 — supporting one-line용.

    Returns "오래" / "꾸준히" / "잠시" / "" (signal 없으면 빈 문자열).
    """
    if total <= 0 or sustained <= 0:
        return ""
    ratio = sustained / total
    if ratio >= 0.30:
        return "오래"
    if ratio >= 0.15:
        return "꾸준히"
    if ratio >= 0.05:
        return "잠시"
    return ""


# ---------------------------------------------------------------------------
# Story-tone fields (for general-audience main display).
#
# Per directive 2026-05-08: 메인 화면은 *수치 없이* 인물의 욕망/압박/변화 방향을
# 보여줘야 한다. evidence_to_logline (수치 인용)은 Evidence 영역으로 분리.
# ---------------------------------------------------------------------------

_ONE_LINE_STORY_BY_CONFLICT: dict[str, str] = {
    "loyalty_vs_survival": (
        "{main}은(는) 끝까지 곁에 남고 싶지만, 두려움과 사람들의 시선이 "
        "커질수록 점점 말하지 않는 쪽으로 밀려난다."
    ),
    "uncertainty_vs_commitment": (
        "{main}은(는) 결정을 내리지 않은 채 머물지만, 주변의 변화는 "
        "그를 대신 움직인다."
    ),
    "control_vs_exposure": (
        "권위는 시선을 좁히고, 사람들의 의심은 퍼진다. {main}은(는) "
        "그 사이에서 자기 자리를 지키려 한다."
    ),
    "collective_fear_vs_scapegoating": (
        "그룹의 두려움이 한 방향으로 모이는 동안, 누가 표적이 될지는 "
        "아무도 명시적으로 결정하지 않는다."
    ),
    "identity_vs_failure": (
        "{main}은(는) 자신이 약속한 사람으로 남고 싶지만, 작은 실패들이 "
        "그 이름을 천천히 흐리게 만든다."
    ),
    "atmosphere_vs_action": (
        "분위기는 이미 무거워졌지만, 누구도 의자에서 일어서지 않는다."
    ),
    "trust_vs_self_protection": (
        "{main}은(는) 관계를 지키고 싶지만, 자신을 보호하는 거리만 "
        "조용히 늘어난다."
    ),
    "unknown": (
        "{main}은(는) 압력 속에서 변화한다. 그 방향은 아직 분명하지 않지만, "
        "예전과 같은 자리는 아니다."
    ),
}


_WHAT_WANTS_BY_CONFLICT: dict[str, str] = {
    "loyalty_vs_survival":             "끝까지 곁에 남고 싶다.",
    "uncertainty_vs_commitment":       "결정을 내리지 않은 채 머물고 싶다.",
    "control_vs_exposure":             "들키지 않고 자기 자리를 지키고 싶다.",
    "collective_fear_vs_scapegoating": "그룹의 안전을 지키고 싶다.",
    "identity_vs_failure":             "자신이 약속한 사람으로 남고 싶다.",
    "atmosphere_vs_action":            "분위기 안에서 안정을 지키고 싶다.",
    "trust_vs_self_protection":        "관계를 지키면서도 자신을 보호하고 싶다.",
    "unknown":                         "지금의 자리를 지키고 싶다.",
}


_WHAT_PRESSURES_BY_CONFLICT: dict[str, str] = {
    "loyalty_vs_survival":             "사람들의 의심, 권위자의 압박, 자기 안의 두려움.",
    "uncertainty_vs_commitment":       "주변의 결정 압박과 자기 안의 망설임.",
    "control_vs_exposure":             "권위자의 시선과 사람들의 의심이 동시에 좁혀온다.",
    "collective_fear_vs_scapegoating": "집단의 두려움과 비난이 한 방향으로 모인다.",
    "identity_vs_failure":             "흔들리는 희망과 누적되는 수치심.",
    "atmosphere_vs_action":            "이미 변한 분위기가 계속 무겁게 머문다.",
    "trust_vs_self_protection":        "신뢰의 책임과 스스로를 지키려는 본능 사이의 긴장.",
    "unknown":                         "여러 압력이 같은 시간대에 함께 누적된다.",
}


_HOW_CHANGES_BY_CONFLICT: dict[str, str] = {
    "loyalty_vs_survival": (
        "처음에는 남아 있으려 하지만, 시간이 지날수록 행동보다 침묵이 앞서기 시작한다."
    ),
    "uncertainty_vs_commitment": (
        "머무는 동안 결정의 순간을 미루고, 시간이 그를 대신 움직인다."
    ),
    "control_vs_exposure": (
        "감시는 점점 좁혀지고 의심은 퍼진다. 그 사이의 거리가 사라진다."
    ),
    "collective_fear_vs_scapegoating": (
        "두려움이 표적을 향해 모이는 동안, 누구도 그 방향을 선언하지 않는다."
    ),
    "identity_vs_failure": (
        "희망은 흔들리고 수치심이 쌓인다. 자신이 누구라고 불릴지가 조용히 바뀐다."
    ),
    "atmosphere_vs_action": (
        "분위기는 더 무거워지지만, 행동은 따라오지 않는다."
    ),
    "trust_vs_self_protection": (
        "한 발자국 물러서기 시작한다. 시선은 같은 사람을 보지만 거리는 달라진다."
    ),
    "unknown": (
        "압력은 누적되고, 인물의 자리는 천천히 다른 모양이 된다."
    ),
}


_THREE_PART_OUTLINE_BY_CONFLICT: dict[str, tuple[str, str, str]] = {
    "loyalty_vs_survival": (
        "{main}은(는) 아직 자리에 남아 있다.",
        "사람들의 시선과 압박이 커지고, 주변 인물들도 결정을 미룬다.",
        "그는 떠나지 않지만, 더 이상 앞에 나서지도 않는다.",
    ),
    "uncertainty_vs_commitment": (
        "{main}은(는) 그룹 옆에 머물고 있다.",
        "주변의 변화가 빨라지지만 그는 여전히 결정하지 않는다.",
        "결정의 순간을 미룬 결과, 그의 자리는 이미 다른 의미가 된다.",
    ),
    "control_vs_exposure": (
        "권위는 시선을 좁히기 시작한다.",
        "사람들의 의심도 함께 커진다. {main}은(는) 그 사이에 있다.",
        "감시와 의심이 만나고, 자기 자리를 지키는 일이 점점 어려워진다.",
    ),
    "collective_fear_vs_scapegoating": (
        "그룹의 두려움이 시작된다.",
        "두려움이 한 방향으로 모이고, 표적이 천천히 그려진다.",
        "결정은 명시적이지 않지만, 표적은 이미 정해져 있다.",
    ),
    "identity_vs_failure": (
        "{main}은(는) 자신의 약속을 기억한다.",
        "작은 실패들이 쌓이고, 희망은 흔들린다.",
        "이 자리 이후 그가 어떤 이름으로 불릴지가 분명하지 않게 된다.",
    ),
    "atmosphere_vs_action": (
        "분위기가 이미 무거워져 있다.",
        "압력은 계속 쌓이지만, 의자에서 일어서는 사람은 없다.",
        "분위기만 바뀌고 행동은 그대로 남는다.",
    ),
    "trust_vs_self_protection": (
        "{main}은(는) 가까이 있다.",
        "위험이 가까워질수록 자신을 보호하려는 거리가 생긴다.",
        "신뢰는 남아 있지만, 거리는 이미 달라졌다.",
    ),
    "unknown": (
        "{main}은(는) 변화가 시작되는 자리에 있다.",
        "여러 압력이 같은 시간대에 함께 누적된다.",
        "그의 자리는 이전과 다르지만, 어디로 향할지는 아직 보이지 않는다.",
    ),
}


_WHY_USABLE_GENERIC = (
    "이 개요는 단편 영화, 소설 챕터, 게임 선택지로 확장할 수 있다. "
    "중심 갈등이 단순하고, 장면의 질문이 분명하다."
)


# ---------------------------------------------------------------------------
# Logline generation (data-cited, evidence-driven; for Evidence section)
# ---------------------------------------------------------------------------

_LOGLINE_BY_CONFLICT: dict[str, str] = {
    "loyalty_vs_survival": (
        "{main}은(는) 끝까지 곁에 남고 싶지만, 두려움과 사람들의 시선이 "
        "커질수록 충성은 점점 침묵으로 바뀐다."
    ),
    "uncertainty_vs_commitment": (
        "{main}은(는) 압력이 올라가는 동안 결정 없이 그 자리를 지킨다. "
        "주변의 변화는 멈추지 않는다."
    ),
    "control_vs_exposure": (
        "권위는 시선을 좁히고, 사람들의 의심은 퍼진다. 그 사이에 "
        "{main}이(가) 있다."
    ),
    "collective_fear_vs_scapegoating": (
        "그룹의 두려움이 한 방향으로 모인다. 누가 결정한 것인지 모를 때 "
        "표적은 가장 빨리 정해진다."
    ),
    "identity_vs_failure": (
        "{main}의 희망이 흔들리고 수치심이 쌓인다. 어떤 이름이 남을지 "
        "조용히 바뀌어간다."
    ),
    "atmosphere_vs_action": (
        "분위기는 이미 무거워졌지만, 누구도 의자에서 일어서지 않는다."
    ),
    "trust_vs_self_protection": (
        "{main}은(는) 거리를 두기 시작한다. 신뢰가 무너진 건 아니지만, "
        "지키려는 것이 달라진다."
    ),
    "unknown": (
        "{main}은(는) 압력 속에서 변화한다. 그 방향은 아직 분명하지 않다."
    ),
}


# ---------------------------------------------------------------------------
# Korean postposition helper
# ---------------------------------------------------------------------------

def _has_final_consonant(word: str) -> bool:
    """마지막 한글 음절의 받침 유무를 검사."""
    if not word:
        return False
    last = word[-1]
    code = ord(last)
    if 0xAC00 <= code <= 0xD7A3:  # 한글 음절 영역
        return ((code - 0xAC00) % 28) != 0
    return False  # 영어 / 숫자 등은 받침 없음으로 처리


def pick_postposition(word: str, with_consonant: str, without: str) -> str:
    """word + 적절한 조사 (예: ('Hero', '은', '는') → 'Hero는')."""
    return word + (with_consonant if _has_final_consonant(word) else without)


def _natural_subject(name: str) -> str:
    """주격 조사 — 받침 검사. Hero는 / Andrew는 / 김(받침)은."""
    return pick_postposition(name, "은", "는")


# ---------------------------------------------------------------------------
# Public helper: resolve Korean josa placeholders in any text
# ---------------------------------------------------------------------------

import re

# 패턴: '단어' 뒤에 '은(는)', '이(가)', '을(를)', '과(와)', '으로(로)' 형태가 오면
# 이전 단어의 받침 유무에 따라 단일 조사로 치환.
_JOSA_TABLE: tuple[tuple[str, str, str], ...] = (
    # (regex_after_word, with_consonant, without)
    (r"은\(는\)", "은", "는"),
    (r"는\(은\)", "는", "은"),
    (r"이\(가\)", "이", "가"),
    (r"가\(이\)", "가", "이"),
    (r"을\(를\)", "을", "를"),
    (r"를\(을\)", "를", "을"),
    (r"과\(와\)", "과", "와"),
    (r"와\(과\)", "와", "과"),
    (r"으로\(로\)", "으로", "로"),
    (r"로\(으로\)", "로", "으로"),
)


def resolve_korean_josa(text: str) -> str:
    """문자열에서 '단어은(는)' / '단어이(가)' 등을 받침에 맞게 단일 조사로 치환.

    Pressure Summary / Story Seed Card / Episode Outline의 모든 한국어 출력에
    공통 적용. 템플릿에서 '은(는)' 표기를 그대로 둘 수 있게 함.
    """
    for pattern, with_c, without in _JOSA_TABLE:
        # (\S) — 직전 비-공백 한 글자, 그 뒤 패턴
        full_re = re.compile(r"(\S)" + pattern)

        def repl(m: re.Match) -> str:
            prev = m.group(1)
            return prev + (with_c if _has_final_consonant(prev) else without)
        text = full_re.sub(repl, text)
    return text


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SupportingArc:
    seed_id: str
    name: str
    role_label: str        # "목격자" / "결정을 미루는 사람" / "늦게 반응하는 인물"
    one_line: str          # 한국어 한 줄

    def to_dict(self) -> dict:
        return {
            "seed_id": self.seed_id,
            "name": self.name,
            "role_label": self.role_label,
            "one_line": self.one_line,
        }


@dataclass(frozen=True)
class EpisodeAct:
    label: str             # "Act 1 — Setup" 등
    plain_label: str       # "1막 — 시작" 한국어
    summary: str           # 한국어 2-3 문장

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "plain_label": self.plain_label,
            "summary": self.summary,
        }


@dataclass(frozen=True)
class EpisodeOutline:
    """Story Assembly Layer — main result for portfolio demo.

    *Story-tone fields* (general-audience main display, no numbers):
        - one_line_story: 메인 logline (수치 없음, 인물 욕망/압박/변화 방향)
        - what_character_wants
        - what_pressures_them
        - how_it_changes
        - three_part_outline: tuple of 3 plain-Korean lines
        - unresolved_question (= end_hook)
        - why_usable

    *Data-cited fields* (Evidence section, numbers allowed):
        - logline (evidence_to_logline 또는 conflict template)
        - act_1/2/3 summaries (evidence-driven 수치 인용)
        - why_this_feels_like_a_story (evidence_to_why)
        - evidence_summary
    """
    title: str
    # === Story-tone (메인 화면용) ===
    one_line_story: str
    main_character: str
    what_character_wants: str
    what_pressures_them: str
    how_it_changes: str
    three_part_outline: tuple[str, str, str]
    unresolved_question: str
    why_usable: str
    # === 데이터 인용 (Evidence section용) ===
    logline: str                    # 수치 인용 logline (Iter 1-6 기존)
    main_arc: str
    supporting_arcs: tuple[SupportingArc, ...]
    act_1: EpisodeAct
    act_2: EpisodeAct
    act_3: EpisodeAct
    end_hook: str                   # = unresolved_question (legacy)
    why_this_feels_like_a_story: str
    evidence_summary: str
    risk_notes: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "title": resolve_korean_josa(self.title),
            # Story-tone fields
            "one_line_story": resolve_korean_josa(self.one_line_story),
            "main_character": self.main_character,
            "what_character_wants": resolve_korean_josa(self.what_character_wants),
            "what_pressures_them": resolve_korean_josa(self.what_pressures_them),
            "how_it_changes": resolve_korean_josa(self.how_it_changes),
            "three_part_outline": [
                resolve_korean_josa(s) for s in self.three_part_outline
            ],
            "unresolved_question": resolve_korean_josa(self.unresolved_question),
            "why_usable": resolve_korean_josa(self.why_usable),
            # Data-cited fields (Evidence section)
            "logline": resolve_korean_josa(self.logline),
            "main_arc": resolve_korean_josa(self.main_arc),
            "supporting_arcs": [
                {**s.to_dict(),
                 "one_line": resolve_korean_josa(s.one_line),
                 "role_label": resolve_korean_josa(s.role_label)}
                for s in self.supporting_arcs
            ],
            "act_1": {**self.act_1.to_dict(),
                       "summary": resolve_korean_josa(self.act_1.summary)},
            "act_2": {**self.act_2.to_dict(),
                       "summary": resolve_korean_josa(self.act_2.summary)},
            "act_3": {**self.act_3.to_dict(),
                       "summary": resolve_korean_josa(self.act_3.summary)},
            "end_hook": resolve_korean_josa(self.end_hook),
            "why_this_feels_like_a_story": resolve_korean_josa(
                self.why_this_feels_like_a_story
            ),
            "evidence_summary": resolve_korean_josa(self.evidence_summary),
            "risk_notes": [resolve_korean_josa(r) for r in self.risk_notes],
        }


# ---------------------------------------------------------------------------
# Act builders
# ---------------------------------------------------------------------------

def _act_1(
    pressure: PressureSummary,
    main: StoryCandidate,
    evidence: NarrativeEvidence | None = None,
    overrides: dict[str, str] | None = None,
) -> EpisodeAct:
    if evidence is not None:
        return EpisodeAct(
            label="Act 1 — Setup",
            plain_label="1막 — 시작",
            summary=_name_substitute_in_text(
                evidence_to_act_summary(evidence, 0), overrides,
            ),
        )
    # Fallback (no evidence given)
    phase1 = pressure.pressure_phases[0] if pressure.pressure_phases else None
    phase_text = phase1.summary if phase1 else "초반에는 변화가 시작된다."
    return EpisodeAct(
        label="Act 1 — Setup",
        plain_label="1막 — 시작",
        summary=(
            f"{phase_text} "
            f"몇몇 인물은 자리에 남지만 압력은 이미 오래 지속되고 있다."
        ),
    )


def _act_2(
    pressure: PressureSummary,
    main: StoryCandidate,
    supporting: list[SupportingArc],
    evidence: NarrativeEvidence | None = None,
    overrides: dict[str, str] | None = None,
) -> EpisodeAct:
    main_name = _to_display_name(
        main.main_characters[0] if main.main_characters else "중심 인물",
        overrides,
    )
    if evidence is not None:
        body = _name_substitute_in_text(
            evidence_to_act_summary(evidence, 1), overrides,
        )
        sup_descriptions: list[str] = []
        for s in supporting[:3]:
            sup_descriptions.append(f"{s.name}은(는) {s.role_label} 위치에 있다")
        sup_text = ". ".join(sup_descriptions) + "." if sup_descriptions else ""
        summary = f"{body} {sup_text}".strip()
        return EpisodeAct(
            label="Act 2 — Pressure Build",
            plain_label="2막 — 압력 누적",
            summary=summary,
        )
    phase2 = pressure.pressure_phases[1] if len(pressure.pressure_phases) >= 2 else None
    phase_text = phase2.summary if phase2 else "중반에는 압력이 누적된다."
    sup_descriptions = []
    for s in supporting[:3]:
        sup_descriptions.append(f"{s.name}은(는) {s.role_label} 위치에 있다")
    sup_text = ". ".join(sup_descriptions) + "." if sup_descriptions else ""
    return EpisodeAct(
        label="Act 2 — Pressure Build",
        plain_label="2막 — 압력 누적",
        summary=(
            f"{phase_text} "
            f"{main_name}은(는) 자리에 남아 있지만 점점 앞에 나서지 않는다. "
            f"{sup_text}"
        ).strip(),
    )


def _act_3(
    pressure: PressureSummary,
    main: StoryCandidate,
    main_seed: StorySeedCard,
    evidence: NarrativeEvidence | None = None,
    overrides: dict[str, str] | None = None,
) -> EpisodeAct:
    if evidence is not None:
        return EpisodeAct(
            label="Act 3 — Turn / Consequence",
            plain_label="3막 — 전환 / 결과",
            summary=_name_substitute_in_text(
                evidence_to_act_summary(evidence, 2), overrides,
            ),
        )
    phase3 = pressure.pressure_phases[2] if len(pressure.pressure_phases) >= 3 else None
    phase_text = phase3.summary if phase3 else "후반에는 결정되지 않은 긴장이 남는다."
    return EpisodeAct(
        label="Act 3 — Turn / Consequence",
        plain_label="3막 — 전환 / 결과",
        summary=(
            f"{phase_text} 결정되지 않은 긴장이 남는다."
        ),
    )


# ---------------------------------------------------------------------------
# Top-level builder
# ---------------------------------------------------------------------------

def build_episode_outline(
    candidates: list[StoryCandidate],
    seed_cards: list[StorySeedCard],
    pressure: PressureSummary,
    audit_pass_count: int = 0,
    audit_fail_count: int = 0,
    evidence: NarrativeEvidence | None = None,
    supporting_evidence: dict[str, NarrativeEvidence] | None = None,
    display_name_overrides: dict[str, str] | None = None,
) -> EpisodeOutline:
    """Assemble an EpisodeOutline from S01 (main) + Sn (supporting).

    If `evidence` is provided, Logline / Acts / Why are produced from observer
    data via the data-driven synthesizer (data_narrative). Without evidence
    the older lookup-based fallback is used.
    """
    if not candidates or not seed_cards:
        raise ValueError("candidates and seed_cards must be non-empty")

    main_candidate = candidates[0]
    main_seed = seed_cards[0]

    # Local closures so each rendering helper picks up display-name overrides
    # without polluting the engine module with content-specific names.
    def _disp(name: str) -> str:
        return _to_display_name(name, display_name_overrides)

    def _sub(text: str) -> str:
        return _name_substitute_in_text(text, display_name_overrides)

    raw_main_name = (
        main_candidate.main_characters[0]
        if main_candidate.main_characters else "중심 인물"
    )
    main_name = _disp(raw_main_name)

    conflict = main_candidate.core_conflict or "unknown"

    # Title from main conflict
    title = _EPISODE_TITLE_BY_CONFLICT.get(
        conflict, _EPISODE_TITLE_BY_CONFLICT["unknown"]
    )

    # === Story-tone fields (main display, no numbers) ===
    # conflict label lookup이 base. evidence가 있으면 *수치 없는* qualitative
    # descriptor로 보강 — 같은 conflict이라도 seed별로 다른 본문이 나오게.
    one_line_template = _ONE_LINE_STORY_BY_CONFLICT.get(
        conflict, _ONE_LINE_STORY_BY_CONFLICT["unknown"]
    ).format(main=main_name)
    what_wants_base = _WHAT_WANTS_BY_CONFLICT.get(
        conflict, _WHAT_WANTS_BY_CONFLICT["unknown"]
    )
    what_pressures_base = _WHAT_PRESSURES_BY_CONFLICT.get(
        conflict, _WHAT_PRESSURES_BY_CONFLICT["unknown"]
    )
    how_changes_base = _HOW_CHANGES_BY_CONFLICT.get(
        conflict, _HOW_CHANGES_BY_CONFLICT["unknown"]
    )
    three_part_template = _THREE_PART_OUTLINE_BY_CONFLICT.get(
        conflict, _THREE_PART_OUTLINE_BY_CONFLICT["unknown"]
    )
    three_part_base = tuple(
        s.format(main=main_name) for s in three_part_template
    )
    why_usable = _WHY_USABLE_GENERIC

    if evidence is not None:
        # Evidence-aware boost (수치 0 유지, 정성 표현만)
        # evidence-derived text는 영어 ev.main_agent_name을 박아 넣으므로
        # _korean_name_substitute로 후처리해 한국어 surface 일관성 유지.
        ev_pressures = _sub(
            evidence_to_what_pressures_story(evidence)
        )
        ev_how = _sub(
            evidence_to_how_changes_story(evidence)
        )
        one_line_story = _sub(
            evidence_to_one_line_story(evidence, one_line_template)
        )
        what_pressures = (
            f"{what_pressures_base} {ev_pressures}".strip()
            if ev_pressures else what_pressures_base
        )
        how_changes = ev_how if ev_how else how_changes_base
        # Three-part phase 3 (전환)에 evidence-aware 정성 한 절 추가
        three_part_outline = (
            three_part_base[0],
            three_part_base[1],
            _sub(
                evidence_to_three_part_outline_phase3(evidence, three_part_base[2])
            ),
        )
    else:
        one_line_story = one_line_template
        what_pressures = what_pressures_base
        how_changes = how_changes_base
        three_part_outline = three_part_base
    what_wants = what_wants_base

    # === Data-cited logline (Evidence section) — 한국어 surface도 동일 매핑 ===
    if evidence is not None:
        logline = _sub(evidence_to_logline(evidence))
    else:
        logline_template = _LOGLINE_BY_CONFLICT.get(
            conflict, _LOGLINE_BY_CONFLICT["unknown"]
        )
        logline = logline_template.format(main=main_name)

    # Main Arc one-liner
    main_arc = f"{main_name} — {main_seed.subtitle.split('—', 1)[-1].strip() if '—' in main_seed.subtitle else main_seed.title}"

    # Supporting arcs — 한국어 이름 + 역할 라벨. 메인 화면용 one-line은 수치
    # 없는 정성 표현. 수치 인용 본문은 별도 (Evidence 영역).
    supporting: list[SupportingArc] = []
    for cand, card in zip(candidates[1:], seed_cards[1:]):
        sup_name_ko = _disp(card.main_character)
        role = _sub(
            _infer_supporting_role(cand, main_candidate, pressure.total_ticks)
        )
        sup_ev = None
        if supporting_evidence is not None:
            sup_ev = supporting_evidence.get(cand.story_candidate_id)
        if sup_ev is not None and sup_ev.main_agent_pressure_peaks:
            p = sup_ev.main_agent_pressure_peaks[0]
            persistence = _persistence_qualifier_safe(p.sustained_ticks, sup_ev.total_ticks)
            if persistence:
                one_line = f"{sup_name_ko}의 {p.plain_pressure}은(는) {persistence} 유지된다."
            else:
                one_line = f"{sup_name_ko}은(는) 같은 압력 안에서 다른 속도로 흔들린다."
        else:
            one_line = card.plain_premise.split(".")[0] + "."
            one_line = _sub(one_line)
        supporting.append(SupportingArc(
            seed_id=card.seed_id,
            name=sup_name_ko,
            role_label=role,
            one_line=one_line,
        ))

    # Acts (evidence-driven when given)
    a1 = _act_1(pressure, main_candidate, evidence=evidence,
                overrides=display_name_overrides)
    a2 = _act_2(pressure, main_candidate, supporting, evidence=evidence,
                overrides=display_name_overrides)
    a3 = _act_3(pressure, main_candidate, main_seed, evidence=evidence,
                overrides=display_name_overrides)

    end_hook = main_seed.unresolved_question

    if evidence is not None:
        why = _sub(evidence_to_why(evidence))
    else:
        why = (
            f"이 개요는 시뮬레이션이 발견한 {len(candidates)}개의 변화 흐름을 "
            f"{main_name} 중심으로 묶은 결과이다. "
            f"개별 인물의 작은 변화가 압력 누적과 함께 *하나의 분위기*로 모이는 것을 "
            f"보여준다. 사건이 만들어진 것이 아니라, 데이터에 이미 있던 흐름들이 "
            f"같은 시간대에서 겹친다."
        )

    evidence = (
        f"이 개요는 {len(seed_cards)}개의 이야기 씨앗에서 조립되었다. "
        f"감사 통과: {audit_pass_count}, 실패: {audit_fail_count}. "
        f"근거 없는 사건이나 대사는 추가되지 않았다."
    )

    risk_notes = (
        "없는 사건을 추가하지 않았다.",
        "대사를 만들지 않았다.",
        "구체적 장면 묘사는 창작자의 영역으로 남겼다.",
        f"개요는 {main_name}을(를) 중심으로 했지만, 동일 데이터로 다른 인물 중심의 "
        f"대안 개요도 가능하다.",
    )

    return EpisodeOutline(
        title=title,
        # Story-tone (main display)
        one_line_story=one_line_story,
        main_character=main_name,
        what_character_wants=what_wants,
        what_pressures_them=what_pressures,
        how_it_changes=how_changes,
        three_part_outline=three_part_outline,
        unresolved_question=end_hook,
        why_usable=why_usable,
        # Data-cited (Evidence section)
        logline=logline,
        main_arc=main_arc,
        supporting_arcs=tuple(supporting),
        act_1=a1,
        act_2=a2,
        act_3=a3,
        end_hook=end_hook,
        why_this_feels_like_a_story=why,
        evidence_summary=evidence,
        risk_notes=risk_notes,
    )


def render_episode_outline_md(outline: EpisodeOutline, run_label: str) -> str:
    """일반인용 메인 마크다운 — *수치 없는* story-tone fields 우선.

    수치 인용은 'Evidence (접힘)' 섹션에 별도 보존.
    """
    three_part = "\n".join(
        f"{i+1}. {resolve_korean_josa(line)}"
        for i, line in enumerate(outline.three_part_outline)
    )
    sup_block = "\n".join(
        f"- **{s.name}** — {resolve_korean_josa(s.role_label)}"
        for s in outline.supporting_arcs
    ) or "_(보조 인물 없음)_"
    risks = "\n".join(f"- {resolve_korean_josa(r)}" for r in outline.risk_notes)

    body = f"""# {outline.title}

> *시나리오: `{run_label}`*

## 한 줄 이야기

{outline.one_line_story}

## 중심 인물

**{outline.main_character}**

## 그가 원하는 것

{outline.what_character_wants}

## 그를 밀어붙이는 압력

{outline.what_pressures_them}

## 어떻게 변하는가

{outline.how_it_changes}

## 이야기 흐름

{three_part}

## 남는 질문

> {outline.unresolved_question}

## 어디에 쓸 수 있는가

{outline.why_usable}

## 보조 흐름

{sup_block}

---

<details>
<summary>Evidence — 데이터 근거 (접힘, 영어 필드명 보존)</summary>

### 데이터 인용 logline

{outline.logline}

### {outline.act_1.plain_label}

{outline.act_1.summary}

### {outline.act_2.plain_label}

{outline.act_2.summary}

### {outline.act_3.plain_label}

{outline.act_3.summary}

### 왜 하나의 이야기처럼 읽히는가

{outline.why_this_feels_like_a_story}

### 근거 요약

{outline.evidence_summary}

### 위험 노트

{risks}

</details>

---

*이 개요는 시뮬레이션 데이터에서 자동 조립되었다. 없는 사건이나 대사는 추가되지 않았다.*
"""
    return resolve_korean_josa(body)
