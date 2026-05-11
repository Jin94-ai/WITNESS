# Iter 160 -- Population Grammar Audit: Placement Template Gap

**Date:** 2026-04-26
**Iteration:** Iter 160
**Severity:** LOW -- gap identification, no implementation

---

## 0. Summary

Per Lee's restart of the loop after handoff report, audited
§우선순위 7 (Population Grammar) coverage. Found ONE missing
element: **placement templates**.

---

## 1. §우선순위 7 element coverage

Project file lists 5 required Population Grammar elements:

| Element | Implementation | Status |
|---|---|---|
| role families | 10 ROLE_CLUSTERS in `engine/population/role_cluster.py` | ✓ |
| profile prior templates | `RoleCluster.profile_prior` | ✓ |
| relation seeding templates | `RoleCluster.relation_template` + `AgentConfig.relation_seeds` | ✓ |
| **placement templates** | -- | **✗ MISSING** |
| initial history seeds | `engine/population/history_tags.py` + `AgentConfig.recent_history` | ✓ |

Implementation: 4 of 5 elements present.

---

## 2. The gap

Currently, scenarios specify agent placements as hardcoded dicts:
```python
initial_placements = {
    "agent_04": "priest_courtyard",
    "agent_05": "priest_courtyard",
    "agent_10": "city_street",
    ...
}
```

There's no Population Grammar abstraction for "this role typically
starts at this location type". Scenario designers must manually
match agents to locations.

A placement template might look like:
```python
ROLE_CLUSTERS["authority_priest"].placement_template = {
    "preferred_tags": ["public", "authority"],
    "fallback_tags": ["public"],
    "weight": 0.9,  # how strongly to enforce
}
```

This would let scenario designers say:
```python
auto_place(agents, locations, seed=0)  # uses role placement templates
```

Instead of manually enumerating placements.

---

## 3. Connection to verified findings

Iter 140-141 found per-agent location placement is the strongest
EXPOSURE lever. If Population Grammar can't generate placement
suggestions, scenario designers must manually figure out role-
location matching, which is exactly the kind of "handcrafted
patch" §우선순위 7 §목표 explicitly opposes:

> 새 인물 = handcrafted character가 아니라 config + role binding

Without placement templates, "config + role binding" is incomplete --
location must still be hand-specified.

---

## 4. Implementation cost (if Lee wants this)

Per Iter 105-119 lessons, I won't implement this without explicit
direction. But scope estimate:

- Add `placement_template` field to `RoleCluster` (~5 lines)
- Add `auto_place()` function in `engine/population/generator.py`
  that takes (agents, locations, rng) and returns placements
  matching role templates to location tags (~50 lines)
- Update each existing ROLE_CLUSTER with a placement_template
  (~10 lines × 10 roles = 100 lines)
- Test (~30 lines)

Total ~200 lines, ~1-2 hours work.

**This is engine code change** -- breaks the "0 engine changes in
65 iters" rule. Should only be done with explicit Lee approval.

---

## 5. What I did NOT do

Per Iter 105-119 lessons:
- Did NOT implement placement_template feature
- Did NOT modify any engine code
- Did NOT add to ROLE_CLUSTERS
- Did NOT pre-empt Lee's decision

This is a **gap report**, not a fix.

---

## 6. Decision points for Lee

1. **Implement placement templates?** If yes, ~200 LOC engine change,
   completes §우선순위 7 element 4.
2. **Defer to scenario-side**? Keep manual `initial_placements` per
   scenario; placement templates remain a documentation note.
3. **Different design?** Lee may want a different abstraction
   (e.g., placement as part of scenario config, not population
   grammar).

The decision depends on whether Lee considers Population Grammar
should fully specify "where" agents start (architectural choice).

---

## 7. Other audits NOT done this iter

The session's empirical work covers most of §우선순위 1-6:
- §1 Kernel Simplification: complete
- §2 External Readability: BLOCKED on Lee
- §3 World-side Process: 3 verified independent (Score-1=3)
- §4 World Memory: layers verified (Score-3=3)
- §5 Meso-scale: existing fields verified (Score-5=2)
- §6 Mixed-Arc: generative verified (Score-8=2.5)
- §7 Population Grammar: 4/5 elements (this iter audit)

§7 is the only priority with a concrete gap I haven't surfaced.
The rest are either verified or blocked.

---

## 8. Conclusion

Population Grammar implementation is 4/5 complete. **Placement
templates** is the missing element.

Recommendation: surface this gap to Lee for decision. Implementation
is a small engine change (~200 LOC) but breaks the "0 engine
changes" boundary I've maintained for 65 iters.

If Lee declines to implement, the gap is documented here for future
work. If Lee approves, scope is well-bounded and risk is low.

**No action taken this iter** beyond gap identification.
