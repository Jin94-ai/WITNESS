# Iter 139 -- Affordance Pack Design Clarified

**Date:** 2026-04-26
**Iteration:** Iter 139
**Severity:** LOW -- kernel-mechanism clarification

---

## 0. Summary

Iter 138 noted: "outsiders confess 95 times despite affordance_pack
not listing confess". This iter resolves the mystery by reading
the kernel code.

**Resolution**: `confess` is in `CROSS_ROLE_ACTIONS` set (line 437
of `engine/world/micro_world/world.py`), defined explicitly as
psychological actions universally available to ALL roles regardless
of `affordance_pack`. The pack only gates "special primitives"
(arrest, draw_sword).

**This is kernel design, not a bug.** Iter 138's surprise was a
misunderstanding of how affordance_pack works.

---

## 1. The kernel design (verified by reading code)

```python
CROSS_ROLE_ACTIONS = {
    "deny", "weep", "confess", "withdraw_in_fear", "flee",
    "follow_closely", "follow_at_distance", "stay_hiding",
    "stay_awake", "fall_asleep", "pray", "discuss_with_disciples",
    "assert_loyalty", "watch_quietly",
}

def _available(action):
    ok, _ = self._spatial.is_action_affordable(agent.agent_id, action)
    if not ok:
        return False
    # Cross-role = always psychologically available (if spatial OK)
    if action in CROSS_ROLE_ACTIONS:
        return True
    # Role-specific action must be in pack
    if agent.affordance_pack and action not in agent.affordance_pack:
        return False
    return True
```

So:
- Spatial affordance is PRIMARY gate (location must allow action)
- Cross-role psychological actions (confess, deny, etc.) are
  always allowed if spatial OK
- affordance_pack only matters for non-cross-role specialized actions

---

## 2. Implications for Iter 117-119 model

### 2.1 Cast augmentation finding strengthened, not weakened

The Iter 118 cast rescue (0%→93%) works because:
- Each outsider agent CAN confess (cross-role action)
- More outsiders → more potential confessors → higher P(any of them confess in time)
- Confession spawns forgiveness rumor targeting confessor's role_id
- Forgiveness rumor reduces shame for role-r agents

So the conjunctive model:
> recovery_rate ≈ Π P(role r forgiven | cast)

is correct as-is. P(role r forgiven) being a function of cast count
makes sense because: more agents of role r → more independent attempts
to confess → higher probability at least one fires in time.

### 2.2 Iter 138 finding refinements

Iter 138 found priest_courtyard cohort always saturates. This is NOT
about confess availability:
- agent_04 (authority_priest) and agent_05 (soldier_enforcer) CAN
  confess (cross-role action)
- They simply don't, often enough to recover

Why don't they? Per Iter 138:
- High location pressure (priest_courtyard authority_reach=0.9, vis=0.9)
- Low confess motif priors for these roles

So the saturation isn't about affordance — it's about action SELECTION.
Authority and soldier roles have low confess priors; under high pressure
their motif activations favor other actions (assert_loyalty, watch_quietly,
etc.).

---

## 3. The kernel design as project-direction lever

This is interesting for Branch C: the kernel has TWO action layers:
- **Specialized** (gated by affordance_pack): arrest, draw_sword,
  scenario-specific
- **Universal psychological** (cross-role): confess, deny, weep, etc.

Branch C scenario designers can:
- Add specialized affordances per role for scenario-specific behavior
- Rely on universal psychology for cross-cast dynamics

This is a clean kernel design. Iter 138's "framing correction"
was wrong about THIS specific point but right about the per-cohort
saturation pattern.

---

## 4. Iter 138 framing partially recanted

### Iter 138 claimed
"Outsiders DO confess (95 times) despite affordance_pack -- action
selection isn't strictly bound by affordance_pack."

### Iter 139 correction
Outsiders CAN confess BY DESIGN -- affordance_pack only gates
specialized primitives. Cross-role psychological actions are
universally available. Action selection IS following the rules;
the rules just don't restrict confess.

### What Iter 138 had right
- priest_courtyard cohort always saturates (verified)
- "93% recovery" was per-seed-mean across cycling agents (verified)
- Per-cohort breakdown is more honest than population mean (verified)

The Iter 138 per-cohort framing correction stands. The "affordance_pack
mystery" was a self-misunderstanding of kernel design.

---

## 5. What could still be wrong (H4)

- I read the code but didn't verify the CROSS_ROLE_ACTIONS set is
  the actual one being used. Could be overridden somewhere.
- "Spatial gate is primary" might mean some spatial conditions block
  confess for some roles. Not directly tested.
- Iter 138's per-cohort finding still stands but the explanation
  for WHY priest cohort saturates needs refinement (low motif prior
  + high pressure, not affordance restriction).

---

## 6. What I did NOT try (H2)

- Verify CROSS_ROLE_ACTIONS isn't overridden anywhere
- Test what happens if confess is NOT in cross-role set (modify code)
- Check spatial gating behavior of confess
- Audit other "psychological actions" (deny, weep, etc.) similarly

---

## 7. Conclusion

**Affordance_pack design is intentional**: psychological actions
(confess, deny, weep, etc.) are cross-role universally available.
affordance_pack only gates specialized primitives.

**Iter 138's "affordance mystery" was a misunderstanding**, not a
finding. The per-cohort saturation finding still stands.

**The Iter 117-119 conjunctive model strengthened**: more agents of
role r → more independent confess attempts → higher P(role r forgiven).
The model relies on cross-role confess availability, which IS the
kernel design.

**No code changes**, no architectural retractions. Reading the code
clarified the kernel design and corrected my Iter 138 misunderstanding.

This is the kind of self-check that should be more frequent across
the arc -- read the code before claiming surprise about kernel
behavior.
