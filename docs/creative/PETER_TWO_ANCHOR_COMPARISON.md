# Peter Two-Anchor Comparison (J-Alpha follow-up)

**Date**: 2026-04-28
**Source**:
- `outputs/creative_demo/peter_scarcity_baseline_5_variations_ko.txt` (anchor 1)
- `outputs/creative_demo/peter_scarcity_high_density_5_variations_ko.txt` (anchor 2)
**Status**: 자율 발견 follow-up 결과. Van Gogh→sacred FAIL 보완.

---

## 1. 두 anchor 정의

같은 시나리오 (scarcity), 같은 cast, 같은 placement. **차이는 crowd density only**:

| Property | Anchor 1 (baseline) | Anchor 2 (high_density) |
|---|---|---|
| Anchor ID | `peter_scarcity_baseline` | `peter_scarcity_high_density` |
| marketplace density | 0.7 | 0.9 |
| poor_quarter density | 0.5 | 0.8 |
| Other settings | 동일 | 동일 |

→ **유일한 변수는 crowd density**.

---

## 2. 두 anchor outcome 분포 (5 seeds 각각)

| Seed | Anchor 1 (baseline) | Anchor 2 (high_density) |
|---|---|---|
| 0 | SATURATION_DOMINATED | SATURATION_DOMINATED |
| 1 | RECOVERY_DOMINATED | RECOVERY_DOMINATED |
| 2 | SATURATION_DOMINATED | SATURATION_DOMINATED |
| 3 | PARTIAL | PARTIAL |
| 4 | RECOVERY_DOMINATED | RECOVERY_DOMINATED |

→ **두 anchor 모두 동일한 5-seed outcome 시퀀스** (SAT/REC/SAT/PARTIAL/REC).

→ **3 distinct outcomes 분포 (SAT 2 / REC 2 / PARTIAL 1) 양 cell에서 reproduce**.

---

## 3. 흥미로운 발견 — Density 효과는 *outcome 분포 그대로*, narrative 톤만 변화?

같은 seed (예: seed 0 → 둘 다 SAT) 두 anchor의 narrative를 비교하면:

### Anchor 1 (baseline density)
> 곡식이 모자란다는 말은 며칠 전부터 떠돌고 있었다. 시장의 가격은 흔들렸고, 곡물 창고를 바라보는 눈빛은 더 길어졌다. 빈민가에서는 평소와 다른 침묵이 깔렸다.

### Anchor 2 (high density)
> [동일 도입 — opening pool은 outcome이 아니라 scenario에 의존]

**현재 한계**: opening은 scenario type만 보고 결정 → density 차이가 도입에 안 보임.

**그러나 cohort detail / pressure_arc는 density 영향 받을 가능성** (blame propagation 더 빠름).

---

## 4. Density 효과 검증 plan (J-Beta 영역)

같은 seed의 baseline vs high_density 두 narrative를 비교하면 차이가 *어디에서* 발생하는지 진단:

| Stage | density 영향 예상 |
|---|---|
| 도입 (opening) | 없음 (scenario-only) |
| 압력 상승 (pressure_arc) | medium — blame_band, top_blame_target 영향 |
| 반응 분기 (group_response) | high — cohort outcomes 자체가 simulation 결과 |
| 귀결 (outcome) | high — outcome category 자체 |
| 사후 (aftereffect) | medium — suspicion/authority residue 영향 |

→ **현재**: outcome이 같으면 텍스트 거의 같음 (variant_pick hash 미세 차이만).
→ **J-Beta**: density semantic을 IR atom에 추가 (예: `crowd_density_band` weak/normal/strong) → density-aware sentence pool.

---

## 5. Lee Gate 2 추가 input

`PETER_5_VARIATION_COMPARISON.md`의 5 항목 + 추가:

### 5.6 Two-anchor cross 비교
- Anchor 1 vs Anchor 2 두 시퀀스 (SAT/REC/SAT/PARTIAL/REC × 2) 비교 시 의미 있는 차이가 있는가?
- 같은 simulation 결과지만 *narrative tone* 차이가 있는가?
- IP 자산 가치 측면: 같은 seed의 두 cell 결과를 *같은 운명의 두 풍경*으로 활용 가능?

### 5.7 J-Beta density-aware narrative 가치
- density-aware sentence pool 도입 가치 있는가?
- 또는 anchor-by-cell 단위로 충분한가?

---

## 6. 자율 follow-up의 가치 (lessons L19 적용)

이번 cycle:
1. J-Alpha Step A6 결과 → Van Gogh→sacred 5/5 PARTIAL FAIL
2. 자율 디버깅 → `test_anchor_diversity.py` → scarcity_high_density READY 발견
3. selector 확장 → 3 anchors total
4. demo 재생성 → 두 cell의 같은 outcome 분포 reproduce 확인
5. 비교 doc (this) — Lee Gate 2 input 풍부화

**Lee directive 받기 전 자율 디버깅으로 Lee Gate 2 quality 향상**.

---

## 7. 산출 file pointer

| File | 내용 |
|---|---|
| `outputs/creative_demo/peter_scarcity_baseline_5_variations_ko.txt` | Anchor 1 5 stories |
| `outputs/creative_demo/peter_scarcity_high_density_5_variations_ko.txt` | Anchor 2 5 stories |
| `outputs/creative_demo/vangogh_sacred_baseline_5_variations_ko.txt` | VG FAIL evidence (transparency) |
| `docs/creative/PETER_5_VARIATION_COMPARISON.md` | Anchor 1 단독 5-variation 평가 |
| `docs/creative/PETER_TWO_ANCHOR_COMPARISON.md` | This — 두 anchor 비교 |
| `docs/creative/VARIATION_READING_REVIEW.md` | J-Alpha 종합 verdict |

---

## 8. 한 줄 요약

**같은 시나리오 + 같은 cast + 다른 density 두 cell이 같은 5-seed outcome 분포 (SAT/REC/SAT/PARTIAL/REC) 산출. density 효과는 outcome 분포가 아니라 propagation 톤에 잠복. J-Beta에서 density-aware sentence pool 도입 시 cell별 narrative 차이 surface 가능.**
