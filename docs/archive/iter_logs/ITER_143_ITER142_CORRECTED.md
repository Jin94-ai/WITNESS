# Iter 143 -- Iter 142 Self-Correction (No-Shame Mistaken For Recovery)

**Date:** 2026-04-26
**Iteration:** Iter 143
**Severity:** HIGH -- corrects Iter 142 direction

---

## 0. Summary

Per-agent audit of Iter 142 V1 (scarcity, all agents at poor_quarter,
"100% recovery"). **Self-correction**: ALL 12 agents had peak shame
= 1.0 (below 1.5 cycling threshold). They never experienced shame.

| Audit category | Count |
|---|---:|
| No shame ever (peak < 1.5) | **12 / 12** |
| Real recovery (peak ≥ 1.5 then final < 4) | 0 |
| Saturated | 0 |

The "100% recovery" was a measurement artifact: my filter excluded
all 12 agents (none cycled), returning empty list, defaulting mean
to 0.0, which then counted as "recovery" because 0.0 < 4.0.

---

## 1. The actual mechanism

When all 12 agents are placed at poor_quarter:
- The public_accusation event at marketplace fires
- Marketplace crowd receives blame
- BUT agents are at poor_quarter, not marketplace
- Agents don't experience direct event-induced shame
- Only rumor propagation through social network produces minor shame
- Net: peak shame = 1.0 (below cycling threshold)

This is **not recovery**. It's **non-impact**.

---

## 2. Iter 142 conclusion direction-corrected

### Pre-Iter-143 framing (Iter 142)
"Location placement universally rescues from saturation."

### Post-Iter-143 framing
"Placing all agents at the low-pressure location DIFFERENT from
where pressure events fire prevents shame accumulation. This isn't
recovery -- it's avoidance."

### Iter 130 monostable claim partially restored
Iter 130 said scarcity is monostable-HIGH. Iter 142 claimed this
was a placement artifact. Iter 143 reveals: at default placement,
scarcity DOES saturate (Iter 130 correct). At all-at-poor-quarter,
shame doesn't accumulate (avoidance, not rescue).

The "monostable vs bistable" classification might actually depend
on whether agents are EXPOSED to pressure events. Avoidance ≠
recovery.

---

## 3. Lessons

### 3.1 Active filter assumption
My recovery measurement script assumes "active cycling" means
peak ≥ 1.5. When agents never reach this threshold, the filter
excludes them, and the empty-list edge case defaults to 0.0,
which is then misinterpreted as "recovery".

This is a script bug, not a kernel issue. Should fix the
classification to:
- ag_finals empty → "no agents cycled" (not recovery)
- ag_finals all > threshold → "recovery"
- ag_finals mixed → "partial recovery"

### 3.2 Self-correction discipline
Iter 142 felt like a major finding. Iter 143 with one targeted
audit showed it was wrong direction. The H4 caveat I noted in
Iter 142 ("agents may have never experienced shame") was the
critical alarm I should have probed before claiming finding.

This is the third major self-correction in the arc:
- Iter 134 mechanism wrong (Iter 135 corrected)
- Iter 119 "8/8 predictions" overconfident (Iter 127 corrected)
- Iter 142 "universal rescue" wrong direction (Iter 143 corrected)

Self-correction is part of honest engineering. The arc has
embedded this discipline.

### 3.3 The Iter 140-141 finding still stands
Iter 140-141 tested individual agent (a04, a05, a10) location
changes within a scenario where OTHER agents AT the high-pressure
location were still being affected by events. The relocated
agent's recovery was a real recovery from real shame.

Iter 142 went too far: relocating ALL agents away from event
location creates avoidance, not recovery.

---

## 4. Refined model

The location-placement mechanism is real BUT:
- It works because location-pressure modulates ambient impact
- Moving an individual agent changes their exposure
- Moving all agents away from pressure-event source = avoidance
  (they don't even encounter the pressure)

Refined description:
> Per-agent location placement determines an agent's exposure to
> pressure-event impact AT that location. High-pressure locations
> compound shame; low-pressure locations buffer.
>
> If agents are placed AWAY from where events fire entirely, they
> don't experience the events directly -- this is avoidance, not
> recovery.

For meaningful Branch C scenario design, agents need to BE EXPOSED
to events for recovery dynamics to matter. Putting all agents at
"safe" locations far from event sources prevents the kernel's
recovery channel from firing at all.

---

## 5. What survives

### From Iter 140-141 (still valid)
- Per-agent location placement modulates recovery within a scenario
- 0% ↔ 100% flip at single-agent level for accusation scenario
- Mechanism is role-agnostic (priest, soldier, outsider all flip
  identically)

### From Iter 142 (corrected)
- Cross-scenario "universal mechanism" claim was overstated
- Scarcity scenario with all-at-poor-quarter = no shame, not recovery
- The kernel's bistability requires PRESSURE EXPOSURE; without
  exposure, dynamics don't fire

---

## 6. What could still be wrong (H4)

- N=3 audit; could be missing edge cases at higher N
- "Peak < 1.5 = no shame" threshold is arbitrary; some shame
  accumulation might still be meaningful at peak 1.0
- The kernel might have OTHER pathways for shame accumulation
  besides location-pressure (e.g., social network propagation
  reaches all agents). The 1.0 peak suggests rumor-mediated minor
  shame, which is non-zero.
- "Avoidance vs recovery" framing is my interpretation; could be
  framed differently.

---

## 7. What I did NOT try (H2)

- Mixed placements (some at marketplace, some at poor_quarter)
- N=15 verification of audit
- Track per-tick shame trajectory (not just peak/final) to see
  what produces the 1.0 plateau
- Disable rumor and check if peak drops to 0 (test rumor-mediated
  hypothesis)

---

## 8. Conclusion

**Iter 142's "universal rescue" finding was wrong direction**.
Per-agent audit (Iter 143) reveals all 12 agents at poor_quarter
never experienced shame; the "100% recovery" was a measurement
artifact (empty filter → 0.0 default → counted as recovery).

**Iter 130's monostable scarcity finding mostly stands**: scarcity
at default placement does saturate. Avoidance (all at low-pressure)
prevents shame accumulation but isn't recovery.

**The Iter 140-141 per-agent location finding still holds** within
its proper scope: when an individual agent is relocated WHILE OTHER
agents experience pressure events, the relocated agent's shame
trajectory differs.

**Self-correction discipline embedded**: 3 major corrections in
the arc (134/135, 119/127, 142/143). Following H4 self-checks
catches errors before they propagate.

**The recovery model still requires**:
1. Agents EXPOSED to pressure events (otherwise nothing to recover from)
2. Cast representation ≥2 per accused role (Iter 119)
3. Forgiveness rumor cascade (Phase 2a)
4. Time horizon sufficient for cascade (>500t typically)

**No engine changes** required. Just script-side filter logic could
be refined to distinguish "no shame ever" from "recovery from shame".
