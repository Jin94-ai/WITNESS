# Curated Anchor Set (J-Alpha)

**Date**: 2026-04-28
**Phase**: J-Alpha Step A3
**Source**: `WITNESS_CREATIVE_IP_TRACK_IMPROVED_DIRECTIVE.md` §4.4 Step A3
**Total**: 10 trajectories (2 anchors × 5 seeds each)

---

## 1. 선정 기준

- Peter anchor 1개 + Van Gogh anchor 1개 (Lee directive § 4.2)
- 각 5 seeds (seeds 0-4)
- 핵심 가설 검증: "같은 anchor 5 seeds가 서로 다른 한국어 이야기로 읽히는가"
- 기존 infrastructure 재사용 (annotated probe 생성기 그대로)

---

## 2. Anchor 1 — Peter Passion (scarcity scenario)

### 2.1 정체
- **Scenario type**: scarcity (Peter passion 환경 중 scarcity slice)
- **Cast**: scarcity 12 agents (merchant + family + 5 laborer + authority + 2 enforcer + 2 crowd + outsider + elite_strategist)
- **Placement**: baseline (granary / poor_quarter / marketplace 분산)
- **Seed events**: 1 accusation against merchant @ t5, 1 guard_approaches @ t15
- **Generator**: `scripts/b_direction/run_scarcity_scene.py` 또는 `generate_scarcity_depth_variations.py` (single/baseline 설정)

### 2.2 5 seeds 사용
- Seed 0: 기존 P_S2_02 base (single/baseline) 와 동일 — 기존 cross-seed 결과 활용 가능
- Seed 1-4: 동일 anchor + 다른 seed → 새로 simulation

### 2.3 기대 arc 차이 (Branch C cross-seed 측정 결과 §6.9 참조)
seeds 0-4에서 scarcity single/baseline modal 분포:
- s0: SATURATION
- s1: RECOVERY (Branch C cross-seed test 데이터)
- s2: SATURATION
- s3: PARTIAL
- s4: RECOVERY

→ **5 seeds 중 최소 2-3 종 outcome 분포** 예상. 핵심 가설 검증에 유리.

### 2.4 왜 이 anchor를 선택했는가
- scarcity는 baseline + Branch C 모두에서 가장 cohort-rich 시나리오 (12 agents, 3 cohorts, blame target deterministic = fisher_laborer)
- cross-seed sensitivity가 single/baseline에서 가장 다양 (Branch C measure 결과)
- 한국어 prose에서 "곡식이 비어 가는 계절" 도입 + 시장/곡물 창고/빈민가 location semantic 풍부

---

## 3. Anchor 2 — Van Gogh / Sacred (sacred scenario)

### 3.1 정체
- **Scenario type**: sacred (Van Gogh 시나리오는 별도 simulator지만 J-Alpha에서는 *sacred 시나리오*로 대체 — 같은 engine, 같은 story pipeline 작동)
- **Cast**: sacred 8 agents (prophet + priest + 3 disciple + 2 crowd + family)
- **Placement**: baseline (temple_outer_court / temple_inner / city_street)
- **Seed events**: 1 prayer_invitation @ t10, 1 miracle_witnessed @ t30, 1 public_accusation against spiritual_wanderer @ t50, 1 miracle_witnessed @ t250
- **Generator**: `scripts/b_direction/run_sacred_gathering.py` 또는 `generate_event_density_variations.py` (med/even 설정)

### 3.2 5 seeds 사용
- Seed 0-4

### 3.3 기대 arc 차이
sacred는 cross-seed에서 *가장 안정적* (Branch C cross-seed 측정 결과 §6.9: sacred clustered → 5/5 unanimous RECOVERY).
- 5 seeds 모두 비슷한 outcome 가능성 높음
- 차이는 timing rhythm + agent 반응에서

→ **5 seeds 중 1-2 종 outcome 분포** 예상. variation 적게 나올 수도. 검증 가치는 sacred에서도 *읽기 어색하지 않은가* 확인.

### 3.4 왜 Van Gogh 대체 sacred?
- Lee directive Van Gogh anchor 1개 명시했지만, Van Gogh 별도 simulator는 story pipeline에 직접 연결되지 않음 (annotated probe 생성기가 sacred는 있지만 Van Gogh는 별도)
- sacred는 sacred 톤 (성전/기도/awe) 포함 — Van Gogh의 "spiritual collapse" 톤과 가장 가까운 substitute
- J-Alpha에서 *같은 engine, 같은 pipeline*으로 검증이 핵심이므로 Van Gogh 대체로 sacred 사용 합리

(참고: Van Gogh 직접 적용은 J-Beta에서. annotated probe format을 Van Gogh trace에서 추출하는 새 generator 필요.)

---

## 4. 보조 anchor (선택적, 보조용)

만약 위 2 anchor가 부족하면 다음 보조 anchor 사용:

### Anchor 3 — Branch C accusation
- accusation 시나리오 baseline + 5 seeds
- 차이: Peter scarcity와 다른 outcome 패턴 검증

→ J-Alpha 시간/budget 따라 선택. *최대 15 trajectories* 한도 (Lee directive § 4.2).

---

## 5. Total trajectories (J-Alpha 범위)

| Anchor | Seeds | Trajectories |
|---|---|---|
| Peter scarcity | 0-4 | 5 |
| Van Gogh→sacred | 0-4 | 5 |
| Branch C accusation (선택) | 0-4 | 5 (only if needed) |
| **Total** | **2-3 anchors × 5 seeds** | **10-15** |

→ Lee directive § 4.2 한도 (10-15 trajectories) 준수.

---

## 6. Generation 방법

각 anchor에 대해:

```python
# Anchor 1 — Peter scarcity
from scripts.b_direction.generate_scarcity_depth_variations import build_scarcity_depth_world
for seed in range(5):
    w = build_scarcity_depth_world(seed=seed, event_count="single", crowd_density="baseline")
    # → annotated probe 생성 → story pipeline → narrative output

# Anchor 2 — Van Gogh→sacred
from scripts.b_direction.generate_event_density_variations import build_sacred_density_world
for seed in range(5):
    w = build_sacred_density_world(seed=seed, miracle_ticks=[10, 100, 190])  # med/even
    # → annotated probe → story → narrative
```

→ Step A6 (5-variation demo)에서 새 generator script `scripts/story/generate_anchor_variations.py` 작성.

---

## 7. 산출 위치

- Annotated probes (intermediate): `docs/b_direction/readability_probes_anchor_alpha/{peter,vangogh}_seed{0-4}.txt`
- Stories (final): `outputs/creative_demo/{peter,vangogh}_anchor_5_variations_ko.txt`

각 .txt 파일에 5 seed 결과를 *연속*으로 묶음 (선택자 역할).

---

## 8. Versioning

| Version | Date | Note |
|---|---|---|
| v1 (this) | 2026-04-28 | J-Alpha Step A3. 2 anchors × 5 seeds = 10 trajectories. |
