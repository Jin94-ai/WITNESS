# Crowd Dynamics — Independent Meso-Layer (Phase 3 우선 1)

**작성:** 2026-04-24
**목적:** 군중을 "개인의 합"이 아니라 **phase transition 있는 집단 동학** 으로 모델링.

---

## 0. 핵심 전환

**Before:** 현재 engine/world/primitives.py 의 `crowd_density` (scalar 0-1). "얼마나 많은 사람이 있는가" 만 담음.

**After:** Crowd는 independent meso-layer. 밀도 뿐 아니라 **emotional alignment, clustering, volatility, accusation amplification** 을 가짐.

---

## 1. Crowd State Variables

`engine/world/crowd/crowd_state.py` (신규 제안) 에 담을 state:

```python
@dataclass
class CrowdState:
    # Density
    density: float                      # 0-1 (개인당 공간)

    # Alignment (군중 정서 방향)
    dominant_emotion: str               # "anger"|"fear"|"awe"|"mourning"|"celebration"|"indifferent"
    alignment_strength: float           # 0-1 (얼마나 한 방향으로 정렬)
    fragmentation: float                # 0-1 (반대 의견 비율)

    # Dynamics
    volatility: float                   # 0-1 (정서 변화 속도)
    contagion_susceptibility: float     # 0-1 (정서 전염성)

    # Focus
    focus_target: str | None            # 지금 주목하는 대상/인물 role
    blame_concentration: float          # 0-1 (특정 대상에 비난 집중도)

    # Information
    rumor_intensity: float              # 0-1 (domain: informational layer와 coupling)
    false_belief_ratio: float           # 0-1 (왜곡된 정보 비율)

    # Accusation amplification
    accusation_amplification: float     # 0-1 (공개 고발 에너지)
```

---

## 2. Crowd Dynamics (매 tick)

### 2.1 Decay/Drift (사람 없이도 진행)
- `density decay`: 시간 경과 + 시간대 (night → 0.1 × 1.0)
- `alignment_strength decay`: HL=10 tick (정서 희미해짐)
- `dominant_emotion drift`: 약한 markov → "indifferent" 회귀
- `volatility decay`: HL=8

### 2.2 Contagion (emotional propagation)
Crowd 내부 전염:
```
alignment_strength[t+1] = alignment_strength[t]
    + contagion_susceptibility × dominant_emotion_intensity × 0.1
```
- 고밀도 + 고전염성 + 강한 정서 → alignment 급상승 (phase transition 시점)

### 2.3 Accusation amplification
Specific role (예: outsider, stigmatized) 에 대한 비난:
```
blame_concentration[target_role][t+1] = 
    blame_concentration[target_role][t] × 0.9  // decay
    + rumor_intensity × alignment_strength × 0.3  // boost
```
**Phase transition:** blame_concentration > 0.7 AND alignment_strength > 0.6 AND dominant_emotion in {anger, fear} → "lynch mode" tipping.

### 2.4 Fragmentation dynamics
- Opposing actors (예: authority_priest defending outsider) 이 있으면 fragmentation ↑
- Fragmentation ≥ 0.5 이면 alignment_strength ceiling 0.7 로 제한

---

## 3. Crowd Phase Transitions

### 3.1 네 가지 phase

| Phase | 조건 | 특성 |
|---|---|---|
| `idle` | density < 0.3 OR alignment_strength < 0.3 | 개인 행동 우세 |
| `gathered` | density > 0.5, alignment_strength 0.3-0.6 | 함께 있지만 통일 없음 |
| `aligned` | density > 0.5, alignment_strength > 0.6 | 집단 에너지 |
| `lynch_mode` | aligned + blame_concentration > 0.7 + dominant in {anger, fear} | 비난 폭발 직전 |

### 3.2 Transition events

Phase 변화는 event로 발화:
- `idle → gathered`: `crowd_gathering`
- `gathered → aligned`: `crowd_alignment_forming`
- `aligned → lynch_mode`: `crowd_blame_crystallizing`
- `lynch_mode → violent_action` (if tipping): `crowd_violent_act` (external event, not agent)

---

## 4. Agent ↔ Crowd Coupling

### 4.1 Crowd → Agent (pressure 경로)

기존 `social_threat` / `shame_exposure` 계산 확장:
```
social_threat = crowd.alignment_strength × crowd.accusation_amplification × 5.0
shame_exposure = crowd.blame_concentration[agent.role] × 10.0
```

신규 pressure 후보 (선택):
- `crowd_energy` — 집단 일체감 흡수 시 동요
- `isolation_from_crowd` — 지배 정서 배제 시 위협

### 4.2 Agent → Crowd (action 경로)

Agent action 이 crowd state에 직접 영향:

| Action | Crowd effect |
|---|---|
| `assert_loyalty` (공개) | alignment_strength ↑ 0.05 (group 편) |
| `deny` (공개 accusation 시) | accusation_amplification ↑ 0.1 |
| `confess` (공개) | blame_concentration ↑ 0.15 (on self), alignment_strength ↑ 0.1 |
| `flee` | alignment_strength ↓ 0.05 (누가 도망치면 군중 응집 흔들림) |
| `assert_loyalty` (minority) | fragmentation ↑ 0.1 |
| Authority `publicly defends` | fragmentation ↑ 0.15 |

---

## 5. 구현 최소 (Phase 5 micro-world 필요 전)

### 5.1 CrowdState dataclass 도입
`engine/world/crowd/state.py`

### 5.2 Coupling 연결 점
- `engine/world/pressure.py::compute` 에서 crowd_state 읽어 social_threat/shame_exposure 계산에 반영
- `engine/person/loop.py` tick step에 `crowd.update()` 추가

### 5.3 Phase transition detection
- `engine/world/crowd/phase.py`

---

## 6. 검증 기준 (Phase 3 §5.7)

| 기준 | 달성 방식 |
|---|---|
| Crowd가 사람 없이 state 갱신 | decay / drift 자동 |
| Phase transition 발생 | alignment + blame 조건 감지 |
| 다른 layer와 coupling | Informational (rumor), Symbolic (honor/shame), Institutional (authority response) |

---

## 7. Micro-world 적용 예시 (Phase 5 연계)

**시나리오:** 12명 crowd participant + 1 outsider + 1 accuser + 2 authority defenders.

**기대 dynamics:**
1. Rumor seed (informational layer) 로 blame target = outsider 설정
2. Crowd alignment 강해지면서 → lynch_mode 접근
3. Authority defenders → fragmentation 주입 → alignment ceiling 제한
4. **Tipping point**: authority 영향력 < rumor+crowd 이면 lynch 발생. 그 반대면 dispersal.

이 flow가 특정 인물 없이도 generated story-like arc 를 형성.

---

**End of crowd dynamics.**
