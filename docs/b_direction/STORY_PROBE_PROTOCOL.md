# Story Probe Protocol (Phase 6)

**작성:** 2026-04-24
**목적:** 구조 우선 개발이 추상 설계로 끝나지 않게 **짧은 probe 로 구조 검증** 루프 확립.

---

## 0. Story Probe 가 아닌 것

- **완성 서사** 아님 — story ≠ probe
- **Peter canonical 재현 실험** 아님 — contrast 용
- **통계 수집** 아님 — 3-10개로 충분

Story probe = **20-40 tick trajectory 샘플, 구조가 만드는 흐름 관찰용**.

---

## 1. Probe 기본 속성

```python
@dataclass
class StoryProbe:
    probe_id: str
    probe_type: str              # "scene_test" | "agent_interaction" | "crowd_test" | "rumor_test"
    duration_ticks: int          # 20-40
    population: list[AgentConfig]
    world_setup: dict
    seed_events: list[dict]
    seed_rumors: list[dict]
    seed: int
    
    expected_patterns: list[str] # 검증할 pattern tags
    expected_divergence: dict    # role-archetype 기반 기대 차이
```

---

## 2. Probe Type 4종

### 2.1 Scene test (1 scene probe)
- 1 scene (accusation / sacred gathering / exchange)
- 20 tick
- 3-5 agents
- 목적: scene → motif → action fidelity 확인

### 2.2 Agent interaction probe
- 2-4 agents
- 20-30 tick
- 역할 충돌 / 화해 / 지속적 관계 테스트
- 예: disciple vs elite_strategist tension

### 2.3 Crowd probe
- 8-12 agents
- 30-40 tick
- Rumor + crowd phase transition
- 목적: meso-dynamics observable 확인

### 2.4 Rumor probe
- 5-8 agents + spatial setup
- 30 tick
- 1 rumor seed → propagation + distortion
- 목적: information layer 독립 동학 확인

---

## 3. Probe 실행 파이프라인

```python
def run_probe(probe: StoryProbe) -> ProbeResult:
    # 1. Initialize micro-world
    world = Micro-World.build(probe.world_setup, probe.population)
    
    # 2. Seed events/rumors
    world.inject_events(probe.seed_events)
    world.inject_rumors(probe.seed_rumors)
    
    # 3. Step probe.duration ticks
    trajectory = []
    for t in range(probe.duration_ticks):
        records = world.step()
        trajectory.append(records)
    
    # 4. Analyze
    result = ProbeResult(
        trajectory=trajectory,
        motif_distribution=compute_motif_dist(trajectory),
        rumor_spread=compute_rumor_spread(world),
        crowd_phases=compute_crowd_phase_sequence(world),
        role_divergence=compute_role_divergence(trajectory),
        tipping_points=detect_tipping_points(trajectory),
    )
    
    # 5. Evaluation
    evaluate_probe(result, probe.expected_patterns)
    return result
```

---

## 4. Probe 평가 기준 (Lee §8.3)

### A. 구조적 기준
1. **사건 자연 발생** — canonical_events.json 에 없는 emergent event (rumor spawn, crowd phase transition 등) 이 나타났는가?
2. **World process 영향** — agent action 이 pressure/state 뿐 아니라 world state (rumor, crowd, spatial) 도 바꿨는가?
3. **Action feedback** — action → world → 다음 tick pressure 로 반환되는 사이클이 관찰되는가?

### B. 인물 기준
1. **Profile 차이가 반응 차이로** — 같은 scene에서 다른 archetype 이 다른 motif 로 반응하는가?
2. **Same scene divergence** — agent_A: conceal, agent_B: confront in same event?
3. **Handcrafted patch 없이 그럴듯한가** — direct boost 없이 Peter-like / Judas-like 반응 일부 나오는가?

### C. 서사 기준
1. **평평함 방지** — trajectory가 monotonic하지 않은가? (모두 같은 action 반복 X)
2. **무작위 방지** — 무의미한 action sequence 아닌가?
3. **Small turning points** — pivotal tick (crowd tipping / rumor crystallize / agent role transition) 이 1개 이상?
4. **Story-likeness** — 인간 독자가 "이 일이 일어났다"를 서술할 수 있는가?

---

## 5. Probe Evaluation Checklist

각 probe 후 체크리스트:

```
[ ] 1. trajectory 내 최소 1 emergent event (canonical_events에 없음)
[ ] 2. rumor / crowd state 가 최소 2번 변화
[ ] 3. 최소 2 agent가 같은 scene에서 다른 motif 발동
[ ] 4. action → world state → 다음 pressure 순환 1개 이상 관찰
[ ] 5. 3 이상의 구별된 motif 활성 (collective)
[ ] 6. tipping point tick 위치 식별 가능
[ ] 7. 인간 독자 1문단 요약 가능 (story-like)
[ ] 8. role 차이가 action 차이 로 드러남
[ ] 9. 같은 world setup + 다른 seed에서 다른 trajectory (non-deterministic)
[ ] 10. 주요 agent 1명 제거 후 흐름 유지 (counterfactual robustness)
```

**7-10 green = structurally successful probe.**
**5-6 green = partial, 반복 조정.**
**≤4 green = structural gap — engine 재검토 필요.**

---

## 6. Probe Batch 운영

### 6.1 Batch 단위

한 번에 3-10 probes:
- 다양한 probe_type 조합
- 다른 seed (randomness 확인)
- 다른 role distribution

### 6.2 Iteration cycle

```
1. 구조 수정 (motif / coupling / affordance 등)
2. Batch 생성 (3-10 probes)
3. 각 probe evaluation
4. 공통 패턴 / 실패 패턴 분석
5. 구조 재조정
6. 다시 2.
```

### 6.3 Success condition (loop 종료)
- Batch의 60% 이상이 structural check 7+ green
- Story-like pattern 에서 handcrafted 개입 최소

---

## 7. Probe Batch 첫 사례 (로드맵 실행 시)

### Batch 1: Accusation dynamics
- Probe A: 10-agent accusation_scene, seed=0
- Probe B: same setup, seed=42
- Probe C: same setup, agent_01 (Peter analog) 제거
- Probe D: same setup, archetype modification (devoted → detached)
- Probe E: same setup, sacred_proximity +0.5

**비교 질문:** A/B 의 motif 분포 유사? C 에서 accusation 흐름 유지? D 에서 conceal 대신 withdraw 우세?

### Batch 2: Rumor propagation
- 5 probes with different network topologies
- merchant hub 있음/없음
- authority suppression 강/약
- 공간 분포 집중/분산

### Batch 3: Crowd phase transition
- 12-agent micro-world
- blame_concentration seed 다르게
- fragmentation injection 유무

---

## 8. Probe 저장 형식

```json
{
  "probe_id": "P001_accusation_seed0",
  "probe_type": "crowd_test",
  "duration_ticks": 30,
  "population": [...],
  "world_setup": {...},
  "seed": 0,
  "trajectory": [...],
  "analysis": {
    "motif_distribution": {...},
    "rumor_events": [...],
    "crowd_phase_sequence": [...],
    "tipping_points": [...],
    "role_divergence_score": 0.68
  },
  "evaluation_checklist": {
    "emergent_events": true,
    "rumor_state_changes": 3,
    ...
  },
  "human_summary": "Agent_01 upper_room 에서 accusation에 mild conceal 반응. agent_02 elite_strategist 쪽으로 role transition 시작. Tick 18 crowd alignment 급상승."
}
```

---

## 9. Phase 6 완료 기준 (Lee §8.6)

| 기준 | 달성 방식 |
|---|---|
| 구조 수정이 probe 결과 차이를 만드는지 읽기 가능 | Batch 1 before/after |
| Probe로 random log와 meaningful flow 구분 | checklist 7+ green = meaningful |

---

## 10. 반복 경계

**금지:** probe 결과가 nice 해 보인다고 구조 fixing 끊지 말 것. probe는 **구조 검증 도구**이지 **완성 기준** 아님.

**허용:** probe 3 batch에서 consistent pattern 이면 Phase 7 (rubric 재설계) 로 진행.

---

**End of Story Probe Protocol.**
