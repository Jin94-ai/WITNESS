# Branch C Preparation Spec

**Date:** 2026-04-28
**Status:** **PREP ONLY** — execution gated by separate Lee directive
**Trigger:** Full N=12 TRUE COMBINED → P-C-ready verdict (Lee approved PREP 2026-04-28)
**Companion:** `BRANCH_DECISION_2026-04-28.md`, `FULL_EVAL_N12_POSTCHECK.md`

---

## 0. What "Branch C" means

**Branch C = "broader world readability"** — extending WITNESS beyond the current 3 scenarios (accusation/sacred/scarcity) and beyond cohort-shame focus toward world-process-level dynamics that an external reader can interpret without scenario-specific priors.

Three claimed Branch C dimensions (per `BRANCH_B_C_SUMMARY.md` historical):
1. **Cross-scenario population variation** — different cast compositions, location structures
2. **World-side process visibility** — crowd_mood, authority, public_attention as first-class observables (not hidden under per-agent shame)
3. **Long-horizon coupling** — meso-scale memory (shame_climate, public_suspicion) traceable across event boundaries

**Status of each per Full N=12**:

| Dimension | Status | Source |
|---|---|---|
| 1. Cross-scenario population | partial — 3 scenarios tested, all readable; expansion blocked | NEXT_ACTIONS §3 |
| 2. World-side process | **partially achieved** — v3 fields (public_suspicion, authority_vigilance) surfaced; crowd_mood + public_attention 12/12, authority 8/12 | RESULTS_V2_FILLED §5 |
| 3. Long-horizon coupling | meso-scale memory exposed but not traced across multiple events | not yet measured |

---

## 1. World-side observables — current state

### 1.1 What's already in CrowdState (verified LOOP 34)

| Field | Status | Coupling | Visible in v3 annotated? |
|---|---|---|---|
| `dominant_emotion` | ACTIVE | crowd→agent emotional contagion | Indirectly via cohort outcome |
| `density` | ACTIVE | runtime read | No (rarely informative on probe scale) |
| `alignment_strength` | ACTIVE | runtime | No |
| `blame_concentration` | ACTIVE (per-target) | runtime | ✓ (Crowd blame total) |
| `rumor_intensity` | ACTIVE | shame coupling | No |
| `accusation_amplification` | ACTIVE | runtime | No |
| `shame_climate` | ACTIVE meso memory | shame_exposure pressure | No (could be added v4) |
| `public_suspicion` | ACTIVE meso memory | social_threat pressure | ✓ (v3) |
| `authority_vigilance` | DEAD/logged-only | (no downstream coupling) | ✓ (v3) |
| `false_belief_ratio` | ACTIVE | runtime | No |

### 1.2 Q3b Q-set option mapping

| Q3b option | Currently surfaced | Gap |
|---|---|---|
| `interpersonal` | per-agent relationship state (latent) | No annotated representation; v4 candidate |
| `group_alignment` | cohort outcome rollup | ✓ (via cohort split visibility) |
| `crowd_mood` | dominant_emotion (implicit) + public_suspicion proxy | ✓ (v3 surfaced) |
| `authority` | authority_vigilance | ✓ (v3 surfaced, but DEAD memory — note caveat) |
| `public_attention` | public_suspicion | ✓ (v3 surfaced) |

### 1.3 v4 candidate fields (NOT implementing now)

These are *spec only*, NOT for autonomous implementation:

- **shame_climate trace** — meso memory, currently ACTIVE in coupling but not surfaced. v4: add `Shame climate: peak X → final Y` line.
- **rumor_intensity trace** — to distinguish accusation-rumor vs scarcity-rumor cases
- **dominant_emotion timeseries** — show transitions (anger → fear → calm) across 50 ticks
- **interpersonal-shift** — per-agent relation state changes (would need per-tick relationship trace)

**Why deferred**: Without empirical evidence (full N=12 with v4 fields) that these resolve a *measured* gap, adding them is "ahead of evidence" (lessons L7).

---

## 2. Acceptance criteria for current annotated output

For Branch C prep verification, annotated v3 fields must satisfy:

### 2.1 Field presence (LOOP 50 verified)

✓ All 12 P{1-12}_ANNOTATED.txt files contain:
- `Final summary: {LABEL}` (5 labels per §1.2.0)
- `Primary pressure: {label}` (v2.1 detection 12/12)
- `Failure mode: {label}` (v2, only on SATURATION_DOMINATED — surfaced on P2/P3/P9/P12)
- `Crowd blame total: {peak/final | negligible}`
- `Public suspicion: {peak/final | negligible}` (v3)
- `Authority vigilance: {peak/final | negligible}` (v3)

### 2.2 Detection accuracy thresholds

| Detection | Required | Actual (v2.1/v3) | Met? |
|---|---|---|---|
| Primary pressure | ≥80% | 12/12 = 100% | ✓ |
| Final summary | ≥80% (computed) | 12/12 (rule-based) | ✓ |
| Failure mode (saturation only) | non-empty | 4/4 saturated probes | ✓ |
| Public suspicion (non-zero where applicable) | discriminative | 8 probes show non-negligible | ✓ |
| Authority vigilance (non-zero where applicable) | discriminative | 4 probes (scarcity scenarios) show non-negligible | ✓ |

### 2.3 Test plan (acceptance test stub)

Standalone validation script (NOT pytest, since it requires PYTHONHASHSEED=0):

```python
# scripts/b_direction/validate_annotated_v3.py (stub for Branch C prep)
"""Verify all 12 P_ANNOTATED files contain required v3 fields + correct detection."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PROBES = ROOT / "docs" / "b_direction" / "readability_probes"

REQUIRED_PATTERNS = {
    "final_summary": r"Final summary:\s+(LOW_ACTIVITY|RECOVERY_DOMINATED|SATURATION_DOMINATED|MIXED|PARTIAL)",
    "primary_pressure": r"Primary pressure:\s+(\w+)",
    "crowd_blame": r"Crowd blame total:\s+(.+)",
    "public_suspicion": r"Public suspicion:\s+(.+)",
    "authority_vigilance": r"Authority vigilance:\s+(.+)",
}

# Ground truth scenario per probe
GT = {
    "P1": "scarcity", "P2": "scarcity", "P3": "accusation",
    "P4": "sacred", "P5": "sacred", "P6": "scarcity",
    "P7": "sacred", "P8": "accusation", "P9": "scarcity",
    "P10": "accusation", "P11": "accusation", "P12": "sacred",
}

def main():
    failures = []
    for i in range(1, 13):
        path = PROBES / f"P{i}_ANNOTATED.txt"
        text = path.read_text(encoding="utf-8")
        for name, pattern in REQUIRED_PATTERNS.items():
            if not re.search(pattern, text):
                failures.append(f"P{i}: missing {name}")
        # Detection check: primary pressure should match GT
        m = re.search(REQUIRED_PATTERNS["primary_pressure"], text)
        if m and m.group(1) != GT[f"P{i}"]:
            failures.append(f"P{i}: primary_pressure={m.group(1)} vs GT={GT[f'P{i}']}")

    if failures:
        print("FAIL:", *failures, sep="\n  ")
        return 1
    print(f"PASS: 12/12 annotated probes contain v3 fields + correct primary pressure")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

**Status**: Stub written here; **not yet implemented** — would be added in next autonomous loop or Lee directive.

---

## 3. What Branch C **prep** can include (autonomous-allowed)

Per NEXT_ACTIONS §3, in autonomous mode we may:

- ✓ Draft Branch C design scope (this doc)
- ✓ Define world-side observables (§1)
- ✓ Acceptance criteria + test stub (§2)
- ✓ Small world-side spec doc (this doc serves)
- Update canonical docs to reflect Branch C readiness

## 4. What Branch C **execution** still requires

⛔ **Lee directive required** for any of:
- Modifying `engine/` to add new scenario types or new world-side mechanisms
- Top-level `world/` refactor (Spike 1A legacy)
- Adding new content packs (`content/peter/`, `content/vangogh/` are the existing 2 — adding 3rd requires directive)
- Implementing v4 annotated fields (shame_climate, rumor_intensity, etc.) without measured gap evidence
- Changing `data/person/pipeline_v2/` or `abc_snapshots/`
- Long-horizon coupling experiments (cross-event memory traces)

---

## 5. Branch C activation gate (post-prep)

**Two paths to activation**:

### Path α: Lee gives explicit Branch C directive
- New directive doc (e.g., `WITNESS_BRANCH_C_DIRECTIVE.md`) specifies scope
- Autonomous mode interprets directive as authorized scope expansion

### Path β: Additional empirical evidence triggers re-evaluation
- New scenario added (e.g., 4th scenario beyond accusation/sacred/scarcity)
- Cross-scenario population variation N=15+ achieves Q3b world-side ≥3 axes positive consistently
- Measured Branch C metrics demonstrate readiness across more conditions

**Default** (no signal): stay in Branch C **prep** indefinitely. Hold pattern.

---

## 6. Open questions for Lee (no rush)

| # | Question | Why it matters | Claude bias (frame-neutral options) |
|---|---|---|---|
| 1 | What is the *first* concrete Branch C use case? | Determines which of §1.3 v4 candidates to prioritize | See §6.1 |
| 2 | Is "broader world" = more scenarios, or = deeper world dynamics in current scenarios? | Different scope | See §6.2 |
| 3 | Is there a "completion" criterion for Branch C, or is it open-ended? | Affects how much prep is "enough" | See §6.3 |
| 4 | Should `world/` legacy be re-examined as part of Branch C, or stay frozen? | Architectural alignment | See §6.4 |

These are **not blocking** prep work; they're for when Lee is ready to direct execution.

### 6.1 First Branch C use case — option matrix

| Option | What | Cost | Risk | Fit |
|---|---|---|---|---|
| **A** 4th scenario (e.g., crisis_grief, family_conflict) | New scenario builder + 12 new probes | ~80 LOC + content + tests + 12 new probe gen | medium (cast/location 설계) | Cross-scenario population variation 즉시 충족 |
| **B** Long-horizon (Iter 165 meso coupling) | Extend probe horizon (50 → 200 ticks) | ~20 LOC + re-generate | low | Long-horizon coupling claim 직접 검증 |
| **C** v4 annotated fields (shame_climate, rumor_intensity) | Generator extension | ~30 LOC + 12 regenerate | low | Q3b world-side 정밀화 |
| **D** Cross-probe comparison summary doc | Aggregate analysis across 12 probes | ~doc only | minimal | Branch A presentation 강화 |

**Claude bias**: **B (long-horizon) → C (v4 fields) → A (new scenario) → D**.
이유: B는 *이미 있는 메커니즘*을 더 길게 관찰하는 것 (low risk + high evidence). A는 *새 메커니즘 추가* 위험 (Iter 105-119 lessons).

### 6.2 "broader world" 정의

| Option | 의미 | Trade-off |
|---|---|---|
| **수평** (more scenarios) | 4th, 5th 시나리오 추가 | Population variation evidence 강하지만 새 메커니즘 risk |
| **수직** (deeper dynamics in current 3) | 현 3 scenarios에 long-horizon, cross-event memory, world-side coupling 추가 | 안전, 기존 검증 결과 유지 |
| **혼합** | 수직 먼저 (안전) → 수평 (확신 후) | 가장 보수적, 시간 多 |

**Claude bias**: **수직 먼저 → 수평** (혼합). 수평만 하면 measurement framework가 새 시나리오에 맞는지 검증 비용 큼.

### 6.3 Branch C "완료" criterion

| Option | Criterion | 의미 |
|---|---|---|
| **A** Open-ended | "Branch C는 prep이 영원히 진행됨" | Lee는 직접 use case 줌, completion 없음 |
| **B** Empirical threshold | "4/4 metrics × N scenarios trigger" | 측정 가능, 명확한 stop |
| **C** Scope-bounded | "v4 fields + 4th scenario까지" | Time-bounded |

**Claude bias**: **B (empirical threshold)**. open-ended는 directive §7 stop condition과 충돌. C는 scope creep risk.

### 6.4 `world/` legacy 처리

| Option | 의미 |
|---|---|
| **Stay frozen** (현 default) | Branch C는 `engine/world/` (current canonical)에서만 작업. `world/` (top-level Spike 1A)는 별도 |
| **Re-examine** | `world/` 안의 6 canonical locations + Jesus agent + economy 등을 Branch C broader world에 통합 가능성 검토 |
| **Sunset** | `world/`를 archive 후 `engine/world/`만 유지 |

**Claude bias**: **Stay frozen** (현 상태 유지). Re-examine은 큰 architectural 작업, sunset은 destructive. Lee 별도 directive 시 Re-examine path 가능.

### 6.5 통합 권고

가장 안전한 첫 directive 형식:

> "Branch C 첫 실행 = §6.1 option B (long-horizon, 50→200 ticks). §6.2 수직만. §6.3 empirical threshold (4/4 × 3 scenarios × 200 ticks). §6.4 frozen 유지."

이 directive면 자율 모드는 즉시 generator extension + 12 long-horizon probes 생성 가능.

---

## 7. Versioning

| Version | Date | Note |
|---|---|---|
| v1 (this) | 2026-04-28 | Initial Branch C prep spec post-Full-N12 + Lee PREP 승인. |
