"""Persona Engine (Steps C+E+F) smoke tests."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from engine.persona import (
    DEFAULT_PROFILE,
    MOTIF_NAMES,
    MotifTendency,
    PersonaProfile,
    activate_motifs,
    load_profile,
    select_action,
)

# -----------------------------------------------------------------
# Profile basics
# -----------------------------------------------------------------

def test_default_profile_validates() -> None:
    issues = DEFAULT_PROFILE.validate()
    assert issues == []


def test_motif_tendency_get() -> None:
    t = MotifTendency()
    assert t.get("conceal") == 1.0
    assert t.get("nonexistent") == 1.0  # default


def test_motif_names_count() -> None:
    assert len(MOTIF_NAMES) == 8


# -----------------------------------------------------------------
# Motif activation behavior
# -----------------------------------------------------------------

def test_conceal_rises_with_shame_and_threat() -> None:
    state = {"fear": 5.0}
    pressures_low = {"shame_exposure": 0.0, "social_threat": 0.0}
    pressures_high = {"shame_exposure": 8.0, "social_threat": 7.0}
    a_low = activate_motifs(state, pressures_low, {}, DEFAULT_PROFILE)
    a_high = activate_motifs(state, pressures_high, {}, DEFAULT_PROFILE)
    assert a_high.activations["conceal"] > a_low.activations["conceal"]


def test_grieve_rises_with_grief_and_eye_contact() -> None:
    state_no = {"grief": 0.0, "guilt": {"primary_focus": 0.0}}
    state_yes = {"grief": 5.0, "guilt": {"primary_focus": 4.0}}
    a_no = activate_motifs(state_no, {}, {}, DEFAULT_PROFILE)
    a_yes = activate_motifs(state_yes, {}, {"eye_contact": 1}, DEFAULT_PROFILE)
    assert a_yes.activations["grieve"] > a_no.activations["grieve"]


def test_seek_repair_rises_with_guilt_hope_trust() -> None:
    state_base = {"hope": 1.0, "trust": {"primary_focus": 2.0},
                  "guilt": {"primary_focus": 1.0}}
    state_repair = {"hope": 8.0, "trust": {"primary_focus": 8.0},
                    "guilt": {"primary_focus": 6.0}}
    events = {"forgiveness_offered": 1}
    a_no = activate_motifs(state_base, {}, {}, DEFAULT_PROFILE)
    a_yes = activate_motifs(state_repair, {}, events, DEFAULT_PROFILE)
    assert a_yes.activations["seek_repair"] > a_no.activations["seek_repair"]


def test_profile_tendency_amplifies_motif() -> None:
    state = {"grief": 5.0, "guilt": {"primary_focus": 3.0}}
    profile_low = PersonaProfile(
        name="low_grieve",
        motif_tendency=MotifTendency(grieve=0.5),
        motif_action_priors=DEFAULT_PROFILE.motif_action_priors,
    )
    profile_high = PersonaProfile(
        name="high_grieve",
        motif_tendency=MotifTendency(grieve=1.8),
        motif_action_priors=DEFAULT_PROFILE.motif_action_priors,
    )
    a_low = activate_motifs(state, {}, {}, profile_low)
    a_high = activate_motifs(state, {}, {}, profile_high)
    assert a_high.activations["grieve"] > a_low.activations["grieve"]


# -----------------------------------------------------------------
# Action selection
# -----------------------------------------------------------------

def test_select_action_returns_motif_family_action() -> None:
    state = {"grief": 6.0, "guilt": {"primary_focus": 5.0}}
    motif_result = activate_motifs(state, {}, {"eye_contact": 1}, DEFAULT_PROFILE)
    # Force grieve as primary (it should be with this state)
    assert "weep" in DEFAULT_PROFILE.motif_action_priors["grieve"]
    sel = select_action(motif_result, DEFAULT_PROFILE)
    # Chosen action should be in one of the top-2 motif's families
    m_a, m_b = motif_result.top_two
    possible = (
        set(DEFAULT_PROFILE.motif_action_priors.get(m_a, {}))
        | set(DEFAULT_PROFILE.motif_action_priors.get(m_b, {}))
    )
    assert sel.action in possible


def test_select_action_availability_filter_blocks() -> None:
    state = {"shame": {"crowd": 7.0}, "fear": 6.0}
    pressures = {"social_threat": 8.0, "shame_exposure": 7.0}
    motif_result = activate_motifs(state, pressures, {}, DEFAULT_PROFILE)

    def no_deny(action: str) -> bool:
        return action != "deny"

    sel = select_action(motif_result, DEFAULT_PROFILE, availability_filter=no_deny)
    assert sel.action != "deny"


# -----------------------------------------------------------------
# Persona content loading
# -----------------------------------------------------------------

def test_load_peter_profile() -> None:
    path = Path(__file__).resolve().parents[2] / "content" / "peter" / "v3" / "profile.json"
    if not path.exists():
        pytest.skip("peter profile.json not present")
    profile = load_profile(path)
    assert profile.name == "peter_passion"
    issues = profile.validate()
    assert issues == [], f"Peter profile issues: {issues}"


def test_load_judas_profile() -> None:
    path = Path(__file__).resolve().parents[2] / "content" / "judas" / "v3" / "profile.json"
    if not path.exists():
        pytest.skip("judas profile.json not present")
    profile = load_profile(path)
    assert profile.name == "judas_passion"
    issues = profile.validate()
    assert issues == [], f"Judas profile issues: {issues}"


def test_peter_has_higher_seek_repair_tendency_than_judas() -> None:
    peter_path = Path(__file__).resolve().parents[2] / "content" / "peter" / "v3" / "profile.json"
    judas_path = Path(__file__).resolve().parents[2] / "content" / "judas" / "v3" / "profile.json"
    if not peter_path.exists() or not judas_path.exists():
        pytest.skip("profiles missing")
    peter = load_profile(peter_path)
    judas = load_profile(judas_path)
    assert peter.motif_tendency.seek_repair > judas.motif_tendency.seek_repair
    assert peter.motif_tendency.confess > judas.motif_tendency.confess
    assert peter.relation_bias.primary_focus_attachment_strength > \
           judas.relation_bias.primary_focus_attachment_strength


# -----------------------------------------------------------------
# Rule #1 on engine/persona/
# -----------------------------------------------------------------

def test_persona_engine_no_person_hardcoding() -> None:
    banned = ["peter", "jesus", "judas", "caiaphas", "pilate"]
    root = Path(__file__).resolve().parents[2]
    for py in (root / "engine" / "persona").glob("*.py"):
        src = py.read_text(encoding="utf-8").lower()
        for b in banned:
            if re.search(rf"\b{b}\b", src):
                raise AssertionError(f"{py.name} contains '{b}' -- Rule #1")
