# Iter 164 -- World-Side Autonomy: Agent-Driven Activity Without Seed Events

**Date:** 2026-04-26
**Iteration:** Iter 164
**Severity:** MEDIUM -- positive structural finding

---

## 0. Summary

Per directive `WITNESS_READABILITY_Q_IMPROVEMENTS_AND_NEXT_DIRECTION.md`
§6 improvement point 3 (World-side autonomy 강화), tested whether
the kernel produces world activity WITHOUT seed events.

**Result: 4/4 autonomy signals present**. Even with zero seed
events and zero seed rumors, the world produces ~88% of full-scenario
activity through agent-driven dynamics.

| Metric | V0 full | V1 no events, no rumor | Ratio |
|---|---:|---:|---:|
| shame_climate peak | 1.0 | **1.0** | 100% |
| public_susp peak | 0.17 | 0.15 | 88% |
| blame_total peak | 1.41 | **1.21** | 86% |
| rumor count peak | 39 | **35** | 90% |
| spawned events | 3246 | **2872** | 88% |
| action diversity | 13 | 12.6 | 97% |

---

## 1. The mechanism

The kernel has **agent-driven autonomy**:
- Agents have motif activation system (decision logic)
- Even without external pressure events, agents take actions
  (confess, deny, withdraw, etc.)
- Agent actions SPAWN events (public_confession spawns
  forgiveness_emitted)
- Spawned events update world state (rumor registry, crowd state)
- World state feeds back into agent state (shame_climate → shame
  pressure)

This is a self-driven loop. The kernel doesn't need player input
to produce structured dynamics.

---

## 2. Connection to Lee's Score-1 (World Autonomy) criterion

Lee's directive criterion: "사람이 없어도 world state가 조금은 움직일 것".

Strict interpretation: "without people/agents". This iter doesn't
test that (we have agents). With no agents, kernel would just
have decay → zero state.

Pragmatic interpretation: "without player events". This iter
strongly affirms: 4/4 autonomy signals present.

**Score-1 (World Autonomy) = 3 confirmed**. Kernel produces
multiple processes operating independently, each generating activity
even without external stimulus.

---

## 3. Implication for "world process formalization" (priority 3)

Directive priority 3 lists "world-side process 정식화":
1. rumor propagation
2. crowd attention / blame concentration
3. authority response

Iter 164 shows all 3 ARE active without seed events:
- Rumor propagation: 35 rumors at peak (all forgiveness from
  agent confessions, then propagating)
- Crowd attention / blame: blame_concentration reaches 1.21
- Authority response: ... actually NOT active without
  guard_approaches event. authority_reach is location property,
  not a process.

So 2 of 3 priority-3 processes are autonomous. Authority response
remains event-triggered.

---

## 4. Surprise: V2 (no events, with rumor) is LOWER than V1

V1 (no events, no rumor): blame peak 1.21
V2 (no events, with rumor): blame peak 1.10

Adding the seeded threat_to_authority rumor REDUCED blame
accumulation. This is unexpected -- typically rumor amplifies
blame.

Possible mechanism: the seeded rumor reaches agents who would
otherwise have moved more autonomously toward confess (which
generates forgiveness rumor → reduces blame). With seeded threat
rumor, agents may take different actions (deny, conceal) that
don't produce forgiveness rumors.

This connects to Iter 134-135 finding (rumor INTERFERES with
cascade). Iter 164 shows rumor's interference is observable
even without external accusation events.

---

## 5. Implication for directive improvement point 1 (decorative cleanup)

Iter 162 confirmed 5 fields INERT under accusation. Iter 164 shows
same fields likely INERT in V1 (no events, no rumor) too -- but
not directly tested. The autonomy signals (shame_climate,
blame_total, public_susp, rumors) ARE LOAD-BEARING in V1.

So the kernel's load-bearing components (memory layers + Phase 2a)
work autonomously. The INERT fields (moral_injury, identity_shift,
trust_scar, event_trauma, breach_count) remain RESERVE.

---

## 6. What could still be wrong (H4)

- N=5 seeds, modest. N=15 might give tighter bounds.
- "Autonomy" is observed at ~88% of full-scenario level. May be
  artifact of agent action distributions in default cast.
- Different cast compositions might show different autonomy levels
  (e.g., all-priest cast might be more or less active).
- 200t horizon. Long-horizon autonomy untested.
- The "V2 lower than V1" finding has small magnitude (0.11 blame),
  could be noise.

---

## 7. What I did NOT try (H2)

- N=15 verification
- Test with ZERO agents (just crowd state) -- degenerate case
- Long horizon (500t) autonomy
- Different cast compositions
- Direct trace of which agent actions drive autonomy

---

## 8. Conclusion

**The kernel has substantive agent-driven autonomy** (4/4 signals,
~88% of full-scenario activity without seed events).

**Score-1 (World Autonomy) confirmed at 3** -- multiple processes
running independently.

**Priority 3 partial coverage**: rumor propagation + crowd
attention/blame are autonomous. Authority response is still
event-triggered (would need engine work to make autonomous).

**Surprising finding**: seeded rumors REDUCE world activity
(slightly), consistent with Iter 134-135 rumor-interference
mechanism.

**Per directive instruction "결과를 회고"**: this iter shows
the kernel is more autonomous than the existing 60-iter framing
suggested. Most empirical work focused on event-driven scenarios;
the kernel's BEHAVIOR WITHOUT events is also rich. Future
investigations could explore "ambient kernel dynamics" as a
separate research line.

**Project improvement input**: directive's priority 3 (world-side
process formalization) is mostly already satisfied for rumor +
crowd. Authority autonomy would require a kernel addition
(autonomous authority event spawning based on blame_concentration
threshold).

**No engine changes** this iter. Pure observational probe.
