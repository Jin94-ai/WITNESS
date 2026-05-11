# Iter 144 -- Iter 140-141 Cascade-Corrected (Same No-Shame Artifact)

**Date:** 2026-04-26
**Iteration:** Iter 144
**Severity:** HIGH -- corrects Iter 140 finding too

---

## 0. Summary

Applied Iter 143's audit lens to Iter 140 V1 (agents 04 priest and
05 soldier relocated to upper_room, claimed 100% recovery).

**Result: same no-shame artifact**. agents 04, 05 had peak shame
= 0.5 (well below 1.5 cycling threshold). Never experienced
meaningful shame. The "100% recovery" was the empty-filter default.

| Audit category | Iter 140 V1 |
|---|---:|
| No shame ever (peak < 1.5) | 6 / 10 (incl. agents 04, 05) |
| Real recovery | 0 |
| Saturated | 4 (city_street agents) |

---

## 1. The cascade

| Iter | Original framing | Audit reality |
|---|---|---|
| 142 | "Universal cross-scenario rescue" | All-poor-quarter = no-shame avoidance |
| 140 | "Per-agent location flips 0%↔100% recovery" | Same -- low-pressure agents avoid shame, never recover |
| 141 | "Mechanism is role-agnostic" | Same artifact, role-agnostic in the "no-shame" sense |

**All three iters reported framings that were wrong direction**. The
kernel does NOT have a mechanism that reduces high shame to low shame
based on location alone.

---

## 2. The actual location mechanism

Location parameters modulate **shame accumulation rate**:
- High visibility + low concealment → shame_exposure boost when events fire
- High authority_reach → physical_threat pressure
- These compound shame from accusation events at the location

So:
- Agents at high-pressure locations + accusation events → shame accumulates
  rapidly, exceeds threshold, gets stuck (without cast-supported recovery)
- Agents at low-pressure locations OR away from event sites → shame
  barely accumulates (peak < 1.5)

The "location flips recovery" was reading "low shame from no
accumulation" as "low shame from recovery". Both have low final shame
but only the latter involves the recovery mechanism.

---

## 3. What's actually true (post Iter 144)

### Cast threshold (Iter 119): VALID
With agents EXPOSED to pressure events:
- n=1 cast: P(role r forgiven) ≈ 0, can't escape saturation
- n=2 cast: P(role r forgiven) ≈ 1, escapes via cascade

This was tested with proper exposure (Iter 118 had 2-acc-diff-roles
firing AT the agents' locations). Recovery was real.

### Location parameters (Iter 133): MOSTLY VALID
Single-parameter changes (low authority_reach in weak_accusation)
still valid -- those changes were applied to a location with active
events, modulating shame accumulation rate, agents still received
shame.

### Iter 140-142 per-agent placement: WRONG DIRECTION
Moving agents AWAY from event locations isn't "rescue from
saturation" -- it's "avoiding events entirely, never accumulating
shame".

---

## 4. Refined per-agent location framework

A more honest description:

> Location placement determines whether an agent is EXPOSED to
> pressure events at that location:
> - Same location as event: experiences event-induced shame
> - Different location: largely insulated from event impact
>
> This is NOT a "recovery mechanism". It's an exposure determination.
>
> Recovery (high shame → low shame transition) requires:
> - Agent EXPOSED to pressure
> - Agent cast representation at n≥2 for accused role
> - Time horizon for forgiveness rumor cascade

---

## 5. Three cascading self-corrections

In Iter 140-144 (5 iters), three findings have been corrected:
1. Iter 140: per-agent location 0%↔100% flip → no-shame artifact
2. Iter 141: role-agnostic generalization → applies to no-shame
   pattern, not real recovery
3. Iter 142: cross-scenario universal rescue → same no-shame artifact

The pattern: I applied the same flawed measurement technique
(empty-filter → 0.0 default → counted as recovery) across multiple
iters before catching it via Iter 143 audit.

This is exactly the discipline the arc benefits from. Once the
audit lens was applied (Iter 143), the cascade of corrections
followed.

---

## 6. Lessons

### 6.1 Active filter requires exposure verification
The recovery_rate calculation should report:
- Real recovery: peak ≥ threshold AND final < threshold
- Saturation: peak ≥ threshold AND final ≥ threshold
- No-shame: peak < threshold (excluded from recovery numerator)

Empty filter results should NOT default to "recovery".

### 6.2 H4 self-checks must be probed
Iter 140 already noted: "tested only this specific seed range".
Iter 142 already noted: "the 0.0 mean shame may indicate no shame
ever accumulated -- need to check max shame trajectory". The H4
caveat WAS the correct alarm; I should have probed it before
claiming finding.

Iter 143-144 are the probes that should have been Iter 140.5 and
142.5.

### 6.3 The arc has embedded honest discipline
Despite the false starts, finding and correcting these errors is
itself the value. A loop without self-correction would have
propagated these as confident claims.

---

## 7. Updated Branch C design framework

7-lever framework (refined):

1. Cast composition (n≥2 sweet spot per accused role)
2. Pressure events (where they fire, what they target)
3. Time horizon
4. Memory layers (rumor decay)
5. Location parameters (modulate accumulation rate when exposed)
6. Event timing (relative to memory state)
7. **Per-agent location placement (determines exposure, NOT recovery)**

Lever 7 reframed: it's an EXPOSURE lever, not a recovery lever.
Designers can use it to choose which agents are exposed to which
event sites, but it doesn't constitute a recovery mechanism on
its own.

---

## 8. What could still be wrong (H4)

- N=5 audit; could miss edge cases at higher N
- "peak < 1.5 = no shame" threshold is engine-defined cycling
  threshold; the 0.5 / 1.0 peaks observed are likely rumor-mediated
  minor accumulation, not zero accumulation
- The cascading corrections might themselves be wrong direction;
  need to re-audit Iter 144 with another lens
- "Empty filter defaults to 0.0" might not be the only artifact;
  other measurement bugs may exist

---

## 9. What I did NOT try (H2)

- N=15 verification of Iter 140 V1 audit
- Mixed placements (a04 at upper_room, a05 at city_street)
- Direct accusation at upper_room (test if agents there CAN
  experience shame)
- Force agent_04 into shame state at upper_room and observe recovery
- Check trajectory in detail (not just peak/final) to see what
  produces the 0.5 plateau

---

## 10. Conclusion

**Iter 140-142 location-recovery findings cascade-corrected**.
Per-agent location placement modulates EXPOSURE to events, not
RECOVERY from shame. The "100% recovery" reports were no-shame
artifacts of the recovery_rate filter logic.

**Real recovery mechanism remains**: cast threshold (n=2 per
accused role) + Phase 2a forgiveness rumor cascade, requiring
agents to be EXPOSED to pressure events first.

**The 7-lever framework still holds** but lever 7 (per-agent
placement) is reframed as an exposure lever.

**Three consecutive self-corrections** in 5 iters (140-144). The
arc has produced significant value through this discipline, even
when the immediate claims were wrong. The MEASUREMENT CORRECTION
process is itself a finding about how to evaluate kernel behavior
honestly.

**No engine changes**. Just probe-script-side filter logic should
better distinguish "no shame ever" from "recovery from shame".
