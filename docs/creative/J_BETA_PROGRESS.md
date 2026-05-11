# J-Beta Progress (Creative IP 트랙 일반화 — 시작)

**Date**: 2026-04-28
**Trigger**: Lee Gate 2 = **PASS (A)** → J-Beta 진행
**Phase**: J-Beta 1차 작업 — selector query API + anchor library 확장 + scarcity trilogy 발견

---

## 1. J-Beta 시작 작업 (이번 LOOP)

### 1.1 selector query API 확장 (J-Beta core)

`engine/story/selector.py`에 4 함수 추가:

| 함수 | 역할 |
|---|---|
| `get_anchor_by_id(anchor_id)` | exact id 검색, None on miss |
| `get_variations_by_anchor_id(anchor_id, max_seeds=5)` | id로 직접 5 variations |
| `query_anchors(scenario=, min_diversity=)` | filter 검색 (scenario / diversity threshold) |
| `get_top_arcs(arc_type)` | arc-dominant anchors (recovery/saturation/low_activity 등) |

→ J-Alpha "anchor variation bundler" → J-Beta "queryable anchor library".

### 1.2 Anchor library 확장 (J-Alpha 3 → J-Beta 5)

새 anchor 추가 (Branch C S2 cross-seed 측정 데이터 재사용):

| Anchor | Cell | 5-seed outcome 분포 | distinct |
|---|---|---|---|
| peter_scarcity_baseline (J-Alpha) | 1 acc / baseline density | SAT 2 / REC 2 / PARTIAL 1 | 3 |
| peter_scarcity_high_density (J-Alpha follow-up) | 1 acc / high density | SAT 2 / REC 2 / PARTIAL 1 | 3 |
| **peter_scarcity_double (J-Beta)** | 2 acc / baseline | SAT 3 / REC 2 | 2 |
| **peter_scarcity_triple (J-Beta)** | 3 acc / baseline | **REC 3 / SAT 2** | 2 |
| vangogh_sacred_baseline (J-Alpha FAIL) | sacred / 3 miracles even | PARTIAL 5 | 1 |

→ **scarcity trilogy** 형성 (1/2/3 accusations).

### 1.3 Tests

`tests/test_story/test_selector_alpha.py`:
- 11 → **27 tests**, 119/119 PASS in 0.25초
- 새 추가: TestQueryAPI (8) + TestTopArcs (5)

---

## 2. J-Beta 핵심 발견 — Scarcity Trilogy (Nonmonotonic Narrative)

### 2.1 Outcome 시퀀스 비교

**같은 scenario (scarcity), 같은 cast, 같은 placement, 다른 accusation 횟수**:

| Variation | 1 accusation | 2 accusations | 3 accusations |
|---|---|---|---|
| Seed 0 | SAT | SAT | REC |
| Seed 1 | REC | REC | REC |
| Seed 2 | SAT | SAT | SAT |
| Seed 3 | PARTIAL | SAT | SAT |
| Seed 4 | REC | REC | REC |
| Modal | SAT (2/5) | SAT (3/5) | **REC (3/5)** |

→ **1→2 accusations**: saturation 강화 (PARTIAL → SAT 추가)
→ **2→3 accusations**: **recovery 역전** (SAT 우세 → REC 우세)

### 2.2 IP 자산 narrative beat

이 trilogy는 직접적 *서사 hook*:

> 한 번의 비난은 어떤 자리를 굳히고,
> 두 번의 비난은 그 굳음을 깊게 했다.
> 그러나 세 번째 비난이 닿았을 때, 무언가가 풀려났다.

→ "**더 많은 무게가 어느 순간 짐을 덜어 줄 수 있다**"는 narrative paradox. 웹소설 anchor 가치 큼.

### 2.3 메커니즘 추정 (Branch C LOOP 70 hypothesis D)

3-accusation cell의 recovery 우세는 *forgiveness cascade saturation*:
- 1 accusation → 한정적 forgiveness 발생
- 2 accusations → forgiveness 누적, 그러나 새 accusation의 무게가 더 큼
- 3 accusations → forgiveness가 *결정적 임계*를 넘어 cohort 회복 trigger

(L18 lessons §5 참조: hypothesis D는 scarcity-specific. accusation/sacred에서 같은 패턴은 안 나옴.)

---

## 3. 5-anchor library 활용 가능 query 예시

```python
from engine.story.selector import query_anchors, get_top_arcs

# scarcity 시나리오의 모든 anchor (4개)
scarcity = query_anchors(scenario="scarcity")

# READY (≥3 distinct outcomes) anchor만 (2개)
ready = query_anchors(min_diversity=3)

# saturation 우세 anchor (4 scarcity)
sat_anchors = get_top_arcs("saturation")

# scarcity trilogy 시퀀스
trilogy_ids = ["peter_scarcity_baseline", "peter_scarcity_double", "peter_scarcity_triple"]
trilogy = [get_anchor_by_id(aid) for aid in trilogy_ids]
```

→ J-Beta selector는 *queryable* — 검색 / filter / arc-targeted 가능.

---

## 4. 출력 file pointer (5 anchor demo)

| File | Outcomes |
|---|---|
| `outputs/creative_demo/peter_scarcity_baseline_5_variations_ko.txt` | SAT/REC/SAT/PARTIAL/REC (3 distinct) |
| `outputs/creative_demo/peter_scarcity_high_density_5_variations_ko.txt` | SAT/REC/SAT/PARTIAL/REC (3 distinct) |
| `outputs/creative_demo/peter_scarcity_double_5_variations_ko.txt` | SAT/REC/SAT/SAT/REC (2 distinct) |
| `outputs/creative_demo/peter_scarcity_triple_5_variations_ko.txt` | REC/REC/SAT/SAT/REC (2 distinct) |
| `outputs/creative_demo/vangogh_sacred_baseline_5_variations_ko.txt` | PARTIAL × 5 (FAIL transparency) |

→ **25 stories total** (5 anchors × 5 seeds).

---

## 5. 다음 J-Beta 작업 (자체 판단 우선순위)

| 작업 | 가치 |
|---|---|
| **scarcity trilogy bundled story** (3 anchor 시퀀스 한 파일) | HIGH — IP 자산 직접 가치 |
| Anchor library 추가 — accusation/sacred 다른 cell 측정 | MEDIUM |
| Style profile 확장 (소설 vs 웹소설 톤) | MEDIUM |
| 70+ trajectory 라벨링 (full taxonomy 도입) | MEDIUM (Lee directive § 6) |
| Density-aware sentence pool (J-Beta plan) | MEDIUM |
| `STORY_UNIT_TAXONOMY.md` full version | LOW (minimal taxonomy 충분) |

→ 다음 LOOP: **scarcity trilogy bundled story** (anchor 3개 outcome 시퀀스 narrative-level 비교 view) 우선.

---

## 6. Lee Gate 1 (Renderer Diagnosis) — Lee directive 따라 자율 cycle

Lee directive: "Gate 1 루프 진행" — Lee 직접 평가 없이 자율 진단.

→ J-Beta 작업 마무리 후 자율 renderer cycle:
1. 현재 5 anchor demo 직접 검토 (Claude 자가 진단)
2. `RENDERER_DIAGNOSIS_ALPHA.md` 자율 항목 채우기
3. 추가 renderer 1-2 항목 개선

---

## 7. 한 줄 요약

**J-Beta 시작: selector를 minimal bundler에서 queryable library로 확장 (4 query API). Anchor 3→5 (scarcity trilogy 추가). Scarcity trilogy 발견 — 1/2/3 accusations가 SAT/SAT/REC modal로 nonmonotonic, IP narrative beat 가치 큼. 119/119 tests PASS.**
