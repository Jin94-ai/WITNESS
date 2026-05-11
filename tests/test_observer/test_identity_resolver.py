"""Tests for IdentityResolver (Stage 5.1-5.3 — Phase A)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.observer.identity_resolver import (
    AgentIdentity,
    GroupIdentity,
    IdentityResolver,
    translate_pressure,
)

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data" / "visual" / "dot_observer_data.json"
SOURCE_VG = ROOT / "data" / "visual" / "dot_observer_data_vangogh.json"


# ============ pressure translation ============

def test_pressure_translate_rise_known():
    assert translate_pressure("fear", "rise") == "fear intensifies"
    assert translate_pressure("authority_vigilance", "rise") == "authority pressure closes in"


def test_pressure_translate_fall_known():
    assert translate_pressure("fear", "fall") == "fear eases"


def test_pressure_translate_unknown_returns_raw():
    assert translate_pressure("unknown_field", "rise") == "unknown_field"


# ============ explicit identity_map.json (peter_scarcity_baseline) ============

def test_resolver_loads_explicit_map_for_peter():
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    res = IdentityResolver.from_observer(obs)
    # identity_map.json says agent_03 = "Peter"
    assert res.agent_label("agent_03") == "Peter"
    assert res.group_label("L1") == "core disciples"


def test_resolver_returns_full_identity():
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    res = IdentityResolver.from_observer(obs)
    ident = res.agent_identity("agent_03")
    assert ident.display_name == "Peter"
    assert ident.archetype == "loyal_under_pressure"
    assert ident.role == "disciple"


# ============ archetype fallback (vangogh has no identity_map.json) ============

def test_resolver_falls_back_to_archetype_when_no_map():
    obs = json.loads(SOURCE_VG.read_text(encoding="utf-8"))
    res = IdentityResolver.from_observer(obs)
    # Should NOT be "Peter" or any explicit name — there is no map for vangogh
    label = res.agent_label("agent_01")
    # Either raw id or "{id} ({archetype})"
    assert label.startswith("agent_01")


def test_resolver_archetype_is_one_of_known():
    obs = json.loads(SOURCE_VG.read_text(encoding="utf-8"))
    res = IdentityResolver.from_observer(obs)
    valid = {
        "loyal_presence", "strained_presence", "low_hope_actor",
        "burdened_actor", "background_presence", "loyal_under_pressure",
        "peripheral_disciple", "skeptic_witness", "unknown",
    }
    for aid in ["agent_01", "agent_02", "agent_03"]:
        ident = res.agent_identity(aid)
        assert ident.archetype in valid, (
            f"unexpected archetype {ident.archetype!r} for {aid}"
        )


# ============ pass-through for unknown IDs ============

def test_resolver_returns_id_for_unknown_agent():
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    res = IdentityResolver.from_observer(obs)
    assert res.agent_label("agent_999") == "agent_999"


def test_resolver_returns_id_for_unknown_group():
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    res = IdentityResolver.from_observer(obs)
    assert res.group_label("L99") == "L99"


# ============ no plot hardcoding (rule #1) ============

def test_identity_resolver_module_has_no_hardcoded_hero():
    """The resolver module must not embed agent IDs in its source.

    Names live in content/, not in code.
    """
    src = (ROOT / "engine" / "observer" / "identity_resolver.py").read_text(encoding="utf-8")
    for forbidden in ("peter", "Peter", "베드로", "vangogh", "VanGogh", "talleyrand"):
        assert forbidden not in src, f"forbidden hero '{forbidden}' in resolver source"


# ============ to_dict serialization ============

def test_resolver_to_dict_shape():
    obs = json.loads(SOURCE.read_text(encoding="utf-8"))
    res = IdentityResolver.from_observer(obs)
    d = res.to_dict()
    assert d["anchor_id"] == "peter_scarcity_baseline"
    assert "agent_03" in d["agents"]
    assert d["agents"]["agent_03"]["display_name"] == "Peter"
    assert "L1" in d["groups"]


def test_agent_identity_dataclass_serialization_roundtrip():
    a = AgentIdentity(
        agent_id="agent_99",
        display_name="Test",
        archetype="x",
        role="y",
    )
    d = a.to_dict()
    assert d["agent_id"] == "agent_99"
    assert d["display_name"] == "Test"
    # Construction back from dict (defensive — no from_dict but should not crash)
    json.dumps(d)
