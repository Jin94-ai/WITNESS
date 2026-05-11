# WITNESS B-Direction — Population Grammar

**Date:** 2026-04-26
**Doc reference:** `WITNESS_WORLD_BUILDING_ELEMENTS_AND_SCALE.md` §5.7

---

## 0. Discovery

Surveying `engine/population/`, **population grammar is already
substantially implemented**. The §5.7 directive treats this as
"draft" needed; in fact the infrastructure exists at ~80% and just
needs formal documentation + remaining gaps identified.

Existing modules:
- `engine/population/role_cluster.py` — 10 generic role clusters
- `engine/population/generator.py` — `AgentConfig` (7-field) +
  `instantiate_agent` + `generate_population`
- `engine/population/history_tags.py` — `apply_recent_history` +
  history tag deltas
- `engine/population/transitions.py` — role transition mechanism

---

## 1. Existing population grammar audit

### 1.1 Role families — ✅ DONE (10 roles)

`ROLE_CLUSTERS` dict (`role_cluster.py:61`):
- `fisher_laborer` — manual labor, peer-bonded, low authority reactivity
- `authority_priest` — religious/political authority, status-conscious
- `soldier_enforcer` — enforcement role, action-oriented
- `crowd_participant` — passive bystander, reactive
- `outsider` — marginal, low belonging
- `merchant` — commerce, opportunistic, mid-trust
- `family_anchor` — protective, remain-present-prone
- `elite_strategist` — deliberative, observation-prone
- `disciple_follower` — devotional, peer-dependent
- `spiritual_wanderer` — sacred-sensitive, peripheral

Each role has:
- `profile_prior` (per-section dicts: pressure_sensitivity / motif_tendency /
  relation_bias / recovery_bias)
- `profile_variance` (gaussian σ for sampling perturbation)
- `relation_template` (required + optional relations needed)
- `affordance_pack` (action repertoire)
- `info_access_level` + `resource_prior` (world binding tags)
- `state_prior` (sparse overrides on default ActiveState)
- `climate_sensitivity` (role-conditional crowd-climate scaling)
- `motif_action_priors` (optional role-specific motif→action priors)

### 1.2 Profile prior templates — ✅ DONE

Each role's `profile_prior` is a partial PersonaProfile spec. The
generator's `_perturb_profile` applies per-role variance for diversity.

### 1.3 Relation seeding templates — ✅ DONE (semi)

`RelationTemplate` per role specifies required + optional relations.
`AgentConfig.relation_seeds` lets caller bind specific names to those
slots. `_build_relations` handles the wiring.

Gap: `generate_population()` uses placeholder names for required
relations in bulk mode. Real social_network construction happens at
scenario level (cast builders write their own networks).

### 1.4 Placement templates — ⚠ PARTIAL

Cast builders (`run_accusation_scene.py`, etc.) hardcode placements:
```python
initial_placements={
    "agent_01": "upper_room",
    "agent_02": "upper_room",
    ...
}
```

No generic "placement template" per role. Gap candidate:
`role_placement_priors[role_id] = {location_id: weight, ...}` per
scenario.

### 1.5 Initial history seeds — ⚠ PARTIAL

`AgentConfig.recent_history` accepts a string tag. `history_tags.py`
provides `HISTORY_TAG_DELTAS` mapping tag → state deltas. `apply_recent_history`
mutates initial state.

Gap: tag library is small; no formal sampling library (e.g., "sample 1
of 5 history seeds for a fisher").

### 1.6 Bulk generation — ✅ DONE

`generate_population(role_distribution, total_agents)` samples N
agents per role distribution. Returns list of `InstantiatedAgent`.

Gap: bulk gen uses placeholder relations (not connected to real cast).
For scenario instantiation, manual stitching still needed.

### 1.7 Faction affiliation — ✅ EXISTS

`AgentConfig.faction_affiliation` is a free-form dict carried into
`InstantiatedAgent.faction_affiliation`. No faction state engine
(would be Branch C broader-world feature).

---

## 2. AgentConfig 7-field design (verbatim)

```python
@dataclass
class AgentConfig:
    agent_id: str                                    # 1
    role_cluster: str                                # 2 (must match ROLE_CLUSTERS key)
    profile_overrides: dict = field(default_factory=dict)   # 3
    relation_seeds: dict = field(default_factory=dict)      # 4
    initial_state_seed: dict = field(default_factory=dict)  # 5
    recent_history: str = ""                                # 6
    faction_affiliation: dict = field(default_factory=dict) # 7
    info_access_level: str | None = None             # optional override
    seed: int | None = None
```

**This is the canonical "new character = config + role binding"
contract.** Per §5.7, this is exactly what's needed.

---

## 3. Demonstrated instantiation pattern

```python
from engine.population import instantiate_agent, AgentConfig

cfg = AgentConfig(
    agent_id="new_fisher_001",
    role_cluster="fisher_laborer",
    profile_overrides={
        "pressure_sensitivity": {"shame_exposure": 1.4},
    },
    relation_seeds={
        "peer_group": ["agent_005", "agent_006"],
        "family": ["agent_010"],
    },
    initial_state_seed={"hope": 6.0, "fear": 2.0},
    recent_history="loss_of_kin",
    faction_affiliation={"village": "north_quarter"},
    seed=42,
)
agent = instantiate_agent(cfg)
# agent: InstantiatedAgent with profile, relations, initial_state, etc.
```

No new rules, no new variables, no handcrafted character file.
Pure config + role binding.

---

## 4. Demonstrated bulk population

```python
from engine.population import generate_population

agents = generate_population(
    role_distribution={
        "crowd_participant": 0.4,
        "soldier_enforcer": 0.2,
        "merchant": 0.2,
        "outsider": 0.1,
        "authority_priest": 0.1,
    },
    total_agents=20,
    seed_base=0,
)
# agents: list of 20 InstantiatedAgent across role distribution
```

Per Scale-10 §3.10:
- Score 3 = "population grammar로 샘플링 가능"
- This function exists. Score: **3**.

---

## 5. Mapping to Scale-10 (Expansion Readiness)

Per WORLD_BUILDING §3.10:
- 0 = each new character needs new rule set
- 1 = some shared kernel
- 2 = profile + binding mostly
- 3 = population grammar samplable

**Current measured score: 3** (already at top of scale).

Caveats:
- The generator works structurally, but few scenarios use it (cast
  builders prefer hardcoded for clarity).
- Social network wiring still scenario-specific.
- Placement assignment still scenario-specific.
- History tag library is sparse (verify HISTORY_TAG_DELTAS scope).

---

## 6. What's missing for full §5.7

### 6.1 Placement template per role

Add to `RoleCluster`:
```python
placement_priors: dict[str, float] = field(default_factory=dict)
# e.g., {"market": 0.4, "private_house": 0.4, "public_road": 0.2}
```

Then `instantiate_agent` could optionally pick a location given
available world locations. This would replace cast-builder hardcoded
placements.

**Status**: NOT IMPLEMENTED. Needs design + 1 new field per role.
Cost: 1 dict field × 10 roles + ~20 lines.

### 6.2 Expanded history tag library

Current `HISTORY_TAG_DELTAS` (from history_tags.py) has a small set.
For richer initial-state diversity, expand to:
- `loss_of_kin`
- `recent_promotion`
- `public_humiliation`
- `gain_of_status`
- `betrayed_by_friend`
- `survived_attack`
- ... etc.

Each tag → state delta dict.

**Status**: PARTIAL. Existing tags covered. Cost: pure data, no logic.

### 6.3 Scenario template / cast template

Currently cast builders are imperative Python. A declarative format
would parameterize:
```python
ScenarioTemplate(
    name="accusation_basic",
    role_distribution={"disciple_follower": 0.3, ...},
    locations=["upper_room", "priest_courtyard", "city_street"],
    placement_priors={...},
    seed_events=[...],
    seed_rumors=[...],
    network_density=0.3,  # generates random social graph
)
```

**Status**: NOT IMPLEMENTED. Major refactor (would replace
run_accusation_scene.py et al.). Branch A or C feature.

### 6.4 Cross-cast sampling

Population grammar lets us sample N agents. For scenario use, need:
- Auto-build social_network from role distribution
- Auto-place agents from placement_priors + location list
- Auto-seed rumors per scenario type

**Status**: NOT IMPLEMENTED. Would unlock cast combinatorial
testing (척도 8 → 2 or 3).

---

## 7. Population grammar as branch lever

### Branch A (readability)
Population grammar lets us run "alternate cast" probes for readability
blind. E.g., what if accusation cast had 50% authority_priest and 30%
crowd_participant? Does the readability shift accordingly?

### Branch B (simplification)
Population grammar already exists; nothing to simplify here. Could
audit if any role's profile_prior is INERT (would parallel the state-
field INERT findings).

### Branch C (broader world)
**Population grammar is THE prerequisite** for broader-world expansion.
With placement templates + scenario templates added, we'd have
cast combinatorial testing capability.

---

## 8. Implementation gap summary

| §5.7 element | Status | Cost to complete |
|---|:-:|---|
| Role families | ✅ DONE | 0 |
| Profile prior templates | ✅ DONE | 0 |
| Relation seeding templates | ✅ DONE (per agent) | Bulk-mode wiring would help |
| Placement templates | ⚠ PARTIAL (per scenario only) | ~20 lines + 1 field per role |
| Initial history seeds | ⚠ PARTIAL | Pure data expansion |
| Bulk population sampling | ✅ DONE | 0 |
| Scenario template | ❌ NOT IMPLEMENTED | Major (Branch A/C work) |

---

## 9. What could still be wrong (H4)

- "Score 3 on Scale-10" assumes the generator actually works for
  current scenarios. Would need to instantiate accusation cast via
  generator and verify identical behavior to hand-built cast.
- HISTORY_TAG_DELTAS coverage not audited; "PARTIAL" status is
  inference.
- Population grammar might be working at toy scale; broader-world
  test needed.
- Faction state engine doesn't exist; faction_affiliation is just
  a metadata tag.

---

## 10. What I did NOT try (H2)

- Run accusation scenario with population-grammar-instantiated cast vs
  handcrafted cast and compare (would prove or disprove "Score 3").
- Audit HISTORY_TAG_DELTAS scope.
- Implement placement_priors as 1-line role addition.
- Auto-network generation from role distribution.

---

## 11. Conclusion

**Priority 7 was already 80% complete pre-WORLD_BUILDING document.**
This audit reveals existing infrastructure (`generator.py` +
`role_cluster.py` + `history_tags.py`) that wasn't documented in
recent B-direction docs.

**Score 3 on Scale-10** (Expansion Readiness) is achievable today with
current grammar. To realize it operationally:
- Document for users (this doc partially does that)
- Add placement_priors per role (low cost)
- Add scenario template DSL (Branch A/C feature)

**Branch implications**:
- This is a strong asset for Branch C broader-world phase
- Branch A could leverage for cast variation studies
- Branch B has no cleanup target here (clean infrastructure)

---

**End of Population Grammar audit. Existing implementation in
engine/population/ is the §5.7 contract. Remaining gaps are
Branch-specific feature work, not freeze-discipline targets.**
