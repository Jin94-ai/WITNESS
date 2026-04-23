# WORLD_SPIKE_4.md — Variable intervention experiments

> Draft (2026-04-21, end of Spike 3). Not yet executed.
> Target session: a fresh Claude Code run after external LLM review of
> [SPIKE_1_REVIEW.md](../world/SPIKE_1_REVIEW.md) +
> [SPIKE_2_REVIEW.md](../world/SPIKE_2_REVIEW.md) +
> [SPIKE_3_REVIEW.md](../world/SPIKE_3_REVIEW.md).

---

## 배경

Spike 1/2/3 완료 후 현 상태:
- 6-layer world engine (calendar, crowd, economy, politics, rumours, factions) 작동
- Person × World integration (Spike 2) + per-day Sync bridge 정상
- Cross-layer chain 검증 완료: Judas → rumour → jesus_movement
  (62% collapse, pharisees control 0% — specificity 증명)
- 1118 tests green, ruff/mypy clean

Spike 4 목표: **intervention-as-experiment** — 변수 하나 바꾸고 앙상블 비교.

이것이 Witness 궁극 질문의 직접 구현:
- "예수가 존재하지 않았다면 예루살렘은 어떻게 됐는가?"
- "빌라도가 관대했다면 십자가 대신 다른 결과?"
- "유월절이 한 달 늦었다면 체포 타이밍은?"
- "열심당이 더 강했다면?"

---

## 절대 규칙 (유지)

1. engine/ public interface 수정 금지
2. content/ 기존 파일 수정 금지 (신규 intervention spec 파일만 허용)
3. 기존 1118 tests 유지
4. ABSOLUTE RULE #9 (same-tick feedback 금지) 유지
5. 모든 intervention은 **override/deepcopy** 방식 — 원본 content 불변

---

## Spike 4 범위

### 4-A: InterventionSpec 스키마

```python
# world/intervention/spec.py
@dataclass
class InterventionSpec:
    intervention_id: str
    description: str
    # 하나 이상:
    faction_influence_scale: dict[str, float] | None = None
    faction_remove: list[str] | None = None
    rumor_seed_boost: float | None = None
    agent_remove: list[str] | None = None
    hazard_rate_scale: float | None = None
    calendar_shift_days: int | None = None
    # 등등 — intervention 타입별 얇은 필드
```

YAML/JSON으로도 저장 가능 (content/interventions/*.json).

### 4-B: InterventionEngine

```python
class InterventionEngine:
    def apply(self, spec: InterventionSpec,
              world_config: WorldConfig,
              base_config: SimulationConfig) -> tuple[WorldConfig, SimulationConfig]:
        """Deep-copy configs then mutate per spec fields.
        Never modifies inputs."""
```

각 intervention 타입별로 `_apply_faction_remove`, `_apply_hazard_scale` 등
private 메서드. 알려지지 않은 spec 필드는 silent ignore (forward-compat).

### 4-C: BatchInterventionRunner

```python
class BatchInterventionRunner:
    def run_batch(
        self, spec: InterventionSpec, n_seeds: int = 10,
    ) -> InterventionBatchResult:
        # 1. Control: base configs, N seeds
        # 2. Intervention: apply spec, N seeds (same seed range)
        # 3. Compare metrics across both arms
```

### 4-D: 비교 메트릭

| Metric | 계산 |
|---|---|
| outcome shift | 평균 peter_final_fear Δ |
| rumour collapse | rumours_seeded Δ |
| faction shift | jesus_movement influence Δ |
| trigger count Δ | total_triggers Δ |
| KL divergence | arrest-tick distribution |
| Cohen's d | standardised effect size on key metrics |
| Permutation p-value | non-parametric significance |

### 4-E: 최소 intervention 3종

1. **remove_jesus_movement_faction** — Factions에서 jesus_movement 제거
   예상: rumour intensity 약화 (jesus movement 관련 소문 없음), 그러나 Judas는 유지되므로 Judas-origin rumours는 유지
   *이 점검: 우리가 정말 "jesus_movement" 이름으로 변수 고립했는가?*

2. **hazard_scale_0.5** — 모든 hazard rate 50%
   예상: arrest mean tick 후반으로 이동, trigger count 감소 비선형

3. **lenient_pilate** — `pilate_bonus = 0`, `approach_lead_days = 0`, `crowd_trigger_threshold *= 1.5`
   예상: alertness 낮음 유지, trigger chain 완화

각 실험 결과 `docs/world/paper_data/intervention_{id}.json`에 저장.

### 4-F: 데모 + 리포트

```
scripts/demo_spike4_interventions.py
→ 3 intervention 실행 후 아래 테이블 출력:

Intervention          Peter fear Δ   Rumour Δ   JM Δ   Cohen's d   p-value
remove_jesus_movement    -0.02         -0%      -100%    ...        ...
hazard_scale_0.5         -0.4          -10%     -5%      ...        ...
lenient_pilate           -1.2          -30%     -20%     ...        ...
```

---

## 테스트 전략

1. **InterventionSpec 단위**: deepcopy 확인 (원본 불변), 필드 조합 여러 개 적용
2. **Integration**: `remove_jesus_movement` 실행 → jesus_movement_final_influence == 0
3. **Null intervention**: empty spec → control과 완전히 동일한 결과 (seed 동일)
4. **Statistical battery**: 3개 intervention 모두에서 control vs intervention 차이가 seed-invariant 직접 증명

최소 새 테스트 10–15개. 기존 1118 tests 유지.

---

## 성공 기준

1. InterventionSpec + InterventionEngine + BatchInterventionRunner 3개 모듈 완성
2. 3종 intervention 모두 에러 없이 10-seed 앙상블 실행
3. 각 intervention에서 최소 하나의 메트릭이 control 대비 |Cohen's d| > 0.5
4. Null intervention (empty spec)가 control과 bit-exact (permutation p-value = 1.0)
5. `docs/world/paper_data/intervention_*.json` 3개 생성
6. 기존 1118 tests green 유지
7. ruff/mypy world/ clean

---

## 하지 않을 것

- 예수 Agent (아직 content/jesus/ 미작성)
- 새 world (arles_1888 같은)
- intervention chain (여러 개 동시 적용) — 1회 1개만
- LLM 기반 intervention narration

---

## 연관 외부 리뷰

[docs/world/SPIKE_3_REVIEW.md](../world/SPIKE_3_REVIEW.md) Q5 (counterfactual
specificity threshold), Q7 ("engine universality" 범위) — 이 두 답변이
Spike 4의 threshold 설정에 영향.

---

## 자율 진행 규칙

- Phase 4A → 4B → 4C → 4D → 4E → 4F 순서
- 각 단계 완료 후 pytest + ruff 검증
- 실패 시 3회 재시도, 4번째는 설계 재검토
- 완료 후 보고: 산출물 목록, 3개 intervention의 Cohen's d 표, 예상 외 결과

---

**이 문서는 draft.** 실제 실행 전에:
- Gemini / ChatGPT 에 review 받을 것 (SPIKE_3 결과 + 이 draft 동시 제공)
- Intervention spec 스키마 필드를 content와 함께 확정
- 3종 minimal intervention의 파라미터 값 확정
