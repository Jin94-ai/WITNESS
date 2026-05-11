"""Recent-history free-text → state delta (Step K).

Lee §15: "recent_history 자유 텍스트" 입력 처리.
단순 substring 매칭. LLM 사용 금지 (Rule #4).
"""

from __future__ import annotations

# Tag → state field deltas. 다수 태그가 매칭되면 누적. 범위 [0, 10] clip.
HISTORY_TAG_DELTAS: dict[str, dict[str, float]] = {
    # Positive events
    "witnessed miracle":    {"awe": 2.0, "hope": 1.0},
    "good catch":           {"hope": 1.0, "vitality": 0.5},
    "good harvest":         {"hope": 1.0, "vitality": 0.5},
    "successful trade":     {"hope": 1.0, "resolve": 0.5},
    "family gathering":     {"joy": 1.5, "hope": 0.5},
    "spiritual encounter":  {"awe": 2.0, "sacred_salience": 2.0},

    # Loss / grief
    "family illness":       {"grief": 1.5, "fear": 1.0},
    "bereavement":          {"grief": 3.0, "fatigue": 1.0},
    "death in family":      {"grief": 3.0, "fatigue": 1.0},
    "property loss":        {"anger": 1.5, "fear": 1.0, "hope": -1.0},

    # Threat / injustice
    "tax increase":         {"fear": 0.5, "anger": 1.0, "resolve": 0.5},
    "arrest of relative":   {"anger": 2.0, "grief": 1.0, "fear": 1.5},
    "brother arrested":     {"anger": 2.0, "grief": 1.0, "fear": 1.0},
    "public humiliation":   {"shame": 3.0, "fear": 1.5, "resolve": -0.5},
    "false accusation":     {"anger": 2.0, "fear": 1.5, "resolve": 0.5},

    # Transition
    "conversion":           {"awe": 2.0, "hope": 2.0, "doubt": -1.5},
    "disillusionment":      {"doubt": 2.0, "hope": -1.5, "resolve": -0.5},
    "exile":                {"isolation_pressure_exposure": 2.0,
                             "grief": 1.0, "fear": 1.0},

    # Relational
    "reconciliation":       {"hope": 1.5, "grief": -1.0, "resolve": 0.5},
    "betrayal by friend":   {"doubt": 2.0, "anger": 1.5, "grief": 1.0},
    "parental approval":    {"hope": 1.5, "resolve": 1.0},
    "marriage":             {"joy": 2.0, "hope": 1.5},

    # Physical
    "chronic illness":      {"vitality": -2.0, "fatigue": 2.0, "hope": -1.0},
    "recovery":             {"vitality": 2.0, "hope": 1.0},
    "exhaustion":           {"fatigue": 2.0, "vitality": -0.5},
}


def apply_recent_history(
    state: dict,
    recent_history_text: str,
) -> dict:
    """Apply substring tag matches. Returns new dict (clipped 0-10).

    state: mutable state dict (fear/hope/grief/...). Target-aware fields
        (love/loyalty/...) not affected by this simple tagger.
    recent_history_text: free text, lower-cased for matching.
    """
    if not recent_history_text:
        return state
    text = recent_history_text.lower()
    for tag, delta in HISTORY_TAG_DELTAS.items():
        if tag in text:
            for field_name, amount in delta.items():
                if field_name in state:
                    cur = float(state[field_name])
                    state[field_name] = max(0.0, min(10.0, cur + amount))
    return state
