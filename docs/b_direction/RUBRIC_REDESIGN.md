# Rubric Redesign (Phase 7)

**작성:** 2026-04-24
**목적:** 기존 rubric 한계를 해결하고 population/world-level 평가 준비.

---

## 0. 전제 (기존 Phase H 결과)

Phase G/H 재설계가 **이미** distance → structure 중심으로 이동함:
- Character critic 재작성 (smoothness 제거)
- Scene response critic 신설
- Context break critic 신설
- Novelty structured_deviation 재정의

**본 Phase 7 (B direction)** 은 그 위에:
- World-level 평가 확장
- Population-level 평가 확장
- Reference set 운영 정책

을 추가.

---

## 1. 현재 rubric 의 구조적 강점/약점 (Phase H 후)

### 강점
- 4축 독립 (single composite 없음)
- Scene-response + context-break 이 alt/noise 부분 분리
- Motif layer와 자연스럽게 결합

### 약점 (Phase 7 보강 대상)
- **Population-level 평가 없음** — 개별 agent trajectory만 평가
- **World-level 평가 없음** — crowd/rumor/institution state 평가 축 없음
- **Reference set 정책 명문화 부족** — gold truth로 취급될 위험 (Lee §9.4)
- **Phase G G4 confusion matrix 의 alternative 약함** (55% 목표 70%+)

---

## 2. 평가 축 5 레벨 (B direction)

### Level 1: Character (기존 — Phase H 유지)
- `character_consistency`: profile alignment, relation stability, recovery plausibility
- 단일 agent 내 trajectory 평가

### Level 2: Scene (기존 — Phase H 유지)
- `scene_response_fit`: 장면 → motif → action 정합성
- Scene 단위

### Level 3: Trajectory (기존 + 강화)
- `context_break_score`
- `structured_novelty`
- Canon compatibility (drift)
- Trajectory 단위

### Level 4: **Population (신규)**
- 여러 agent 집단의 motif distribution 다양성
- Role × Archetype 조합 따른 motif 분산도
- Pressure response variance across agents
- Target: 같은 world 에서 role diversity 가 motif diversity 로 이어지는가

**측정:**
- `motif_diversity_index` — Shannon entropy of motif distribution across agents
- `role_archetype_distinctness` — 같은 role 안에서 archetype 차이가 motif 차이로 드러나는가

### Level 5: **World (신규)**
- World state evolution의 coherence
- Cross-layer coupling 활성도
- Emergent event vs seeded event 비율

**측정:**
- `emergent_event_fraction` — 전체 event 중 scripted 비율 (낮을수록 emergent)
- `cross_layer_coupling_activity` — 매 tick coupling trigger 수
- `phase_transition_observed` — crowd / rumor / institutional phase transition 발생 여부

---

## 3. Reference Set Policy

Lee §9.4: *"reference trajectories는 calibration용이며, gold truth로 절대화하지 않는다"*.

### 3.1 원칙

1. **Calibration only** — threshold, critic weight 조정용
2. **Not ground truth** — Rule #13 판정 최종 기준 아님
3. **Sanity-checked** — human review 거친 것만 신뢰
4. **Regenerable** — GPT 재생성 필요 시 기존 세트 대체 가능

### 3.2 Reference Set 갱신 정책

| 상황 | 조치 |
|---|---|
| 새 rubric critic 추가 | 기존 reference set 재평가. 재분류 필요 시 v3 생성 |
| Phase transition 관련 critic 도입 | 기존 reference 로 calibration 어려움. 새 reference spawn 필요 |
| Population-level 평가 | 단일 trajectory reference → multi-agent reference 필요 |
| Human sanity check 결과 flag | 해당 trajectory 제외 (Rule #19 임시 해제) 또는 재라벨링 |

### 3.3 Set versioning

- `witness_trajectories_45.json` (v0.1, 2026-04-23 Phase G)
- `witness_trajectories_45_v2.json` (Phase H.3 re-labeled)
- 향후 `witness_trajectories_100_v3.json` (Population probe 대상, 확장 필요)

### 3.4 Gold truth 대체

Reference 만 믿지 말고:
- Multi-rubric cross-check (독립 critic 조합)
- Human sanity check (Lee direct review)
- Counterfactual test (agent 제거 시 flow 유지?)

---

## 4. World-level Evaluation Sketch (Level 5 세부)

### 4.1 측정 항목 후보

#### `world_coherence`
- Layer 간 coupling 활성화 빈도
- Cross-layer contradiction 검출

#### `emergence_ratio`
- emergent event / total event
- emergent motif transition / total transition

#### `phase_robustness`
- Phase transition이 counterfactual perturbation 에 robust 한가
- 1 agent 제거 시 crowd phase transition 유지?

#### `story_density`
- Tipping points per 20 tick
- Tipping point별 pressure cascade 길이

### 4.2 World-level 공식 초안

```python
def world_evaluation(world_state, trajectory) -> dict:
    return {
        "emergent_fraction": len(emergent_events) / len(total_events),
        "phase_transitions": count_phase_transitions(trajectory),
        "cross_layer_activations": sum_coupling_triggers(trajectory),
        "story_density": tipping_points_per_100_tick(trajectory),
        "counterfactual_robustness": run_counterfactual_suite(world_state),
    }
```

### 4.3 Population-level 공식 초안

```python
def population_evaluation(agents: list[Agent], trajectories: list) -> dict:
    motif_dists = [compute_motif_dist(t) for t in trajectories]
    return {
        "motif_diversity_across_agents": shannon_entropy(motif_dists),
        "role_archetype_distinctness": compute_within_role_variance(agents, trajectories),
        "pressure_response_variance": compute_pressure_variance(trajectories),
        "agent_similarity_clusters": cluster_agents_by_motif_signature(agents),
    }
```

---

## 5. Rubric 구조 최종 (Phase 7 후 목표)

```
RubricEvaluator.evaluate(
    records: list[dict],              # single agent trajectory (기존)
    profile: PersonaProfile,          # profile alignment (Phase H+)
    role: RoleCluster,                # NEW: role affordance check
    world_state: WorldState,          # NEW: world-level features
    population: list[Agent] | None,   # optional: population-level
) -> MultiLevelReport
```

**MultiLevelReport:**
- Level 1-3: single-agent (기존)
- Level 4: population (if population provided)
- Level 5: world (world_state)

---

## 6. Phase 7 완료 기준 (Lee §9.6)

| 기준 | 달성 방식 |
|---|---|
| canonical/alt/noise가 critic 구조로 분리 | Phase H 완료 + Phase 7 population/world 축 추가 시 강화 |
| World-level evaluation 확장 방향 문서화 | §4 World-level sketch |

---

## 7. 구현 로드맵

1. Level 4 (population) 측정 공식 — `engine/rubric/population_critic.py`
2. Level 5 (world) 측정 공식 — `engine/rubric/world_critic.py`
3. MultiLevelReport 통합 — rubric_evaluator 확장
4. Reference set v3 — population 단위 reference 5-10개
5. World-level reference — micro-world run 3개 저장 → baseline

**Phase 5 micro-world 구현 후에 Phase 7 일부 측정 가능.**

---

**End of Rubric Redesign.**
