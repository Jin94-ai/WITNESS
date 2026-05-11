# WITNESS — Pixel Event Playback MVP 계획서

## 1. 현재 판단

Pixel Scene Director Static MVP는 **PW-SC-B로 freeze**한다.

정적 이미지 방식은 기존 dashboard보다 나아졌지만, 사용자가 기대한 “포켓몬 픽셀게임처럼 도트 캐릭터들이 움직이고 서로 상호작용하고 대화하며 사건이 일어나는 느낌”을 제공하지 못한다.

핵심 문제는 캐릭터 크기나 cue 부족이 아니다.  
정적 화면 하나로 상호작용과 사건 흐름을 읽히게 하려는 medium 자체가 한계다.

선, wave, rift, relation cue를 추가해도 결국 diagram/UI overlay처럼 보일 위험이 크다.

---

## 2. 방향 결정

### Freeze

**Pixel Scene Director Static track은 여기서 freeze한다.**

추가 static composition patch는 금지한다.

기존 산출물은 보존한다.

- `visual/pixel_scene.html` 보존
- `docs/visual/PIXEL_SCENE_DIRECTOR_REVIEW.md`에 Final Case: `PW-SC-B` 기록
- 실패 이유 기록: `static image cannot communicate interaction/flow clearly enough`
- Pixel Scene Director는 “static summary artifact”로 freeze
- static cue / line / rift patch 추가 금지

### New Track

다음 방향은 **Pixel Event Playback MVP**로 전환한다.

---

## 3. 새 목표

전체 world replay가 아니라, selected candidate 1개를 **10~20초짜리 짧은 pixel event playback**으로 보여준다.

```text
candidate 1개 = short cutscene playback
```

사용자는 포켓몬식 타일맵 화면에서 agent들이 걷고, 멈추고, 서로 바라보고, 말풍선을 띄우고, 반응하는 모습을 관찰한다.

중요한 구분:

- full replay 아님
- timeline scrub 아님
- playable 아님
- player intervention 아님
- 전체 world map 아님
- story renderer 아님

선택된 candidate를 사람이 이해할 수 있는 짧은 visual playback으로 번역하는 것이 목표다.

---

## 4. 새 이름

```text
Pixel Event Playback MVP
```

약칭:

```text
PEP MVP
```

---

## 5. 참고 방향

Generative Agents / Smallville 계열처럼 agent가 환경 안에서 이동하고 대화하고 반응하는 관찰형 sandbox 감각을 목표로 한다.

단, WITNESS에서는 다음을 지킨다.

- LLM agent를 새로 붙이지 않는다.
- 기존 Observer / Candidate 데이터를 기반으로 짧은 playback script를 derive한다.
- 새 engine metric을 추가하지 않는다.
- 새 scenario를 추가하지 않는다.
- 새 anchor를 추가하지 않는다.

---

## 6. 새 산출물

이번 MVP의 산출물은 4개다.

| 파일 | 내용 |
|---|---|
| `scripts/visual/build_event_playbacks.py` | candidate를 event playback script로 변환 |
| `data/visual/event_playbacks.json` | 3개 candidate playback 데이터 |
| `visual/pixel_event_playback.html` | Canvas 기반 pixel playback viewer |
| `docs/visual/PIXEL_EVENT_PLAYBACK_REVIEW.md` | 5초 테스트, PEP-A/B/C 판정 문서 |

---

## 7. 대상 범위

### Anchor

```text
peter_scarcity_baseline only
```

### Candidate 3개 유지

| Candidate | Scene Type | 목표 |
|---|---|---|
| `C01_t15` | authority pressure | guard 접근, focal 위축, witness 반응 |
| `C02_t25` | saturation split | confession 이후 grief response와 집단 분리 |
| `C03_t142` | confession cluster | 중앙 confession, crowd witness, forgiveness response |

---

## 8. Event Playback Schema 초안

```json
{
  "schema": "event_playback_v1",
  "playback_id": "playback_t15_authority_pressure",
  "candidate_id": "C01_t15",
  "tick": 15,
  "duration_ms": 12000,
  "scene_type": "authority_pressure",
  "map": {
    "mode": "focused_tile_stage",
    "width_tiles": 20,
    "height_tiles": 12,
    "camera": "fixed"
  },
  "actors": [
    {
      "id": "agent_09",
      "role": "focal",
      "start": {"x": 8, "y": 6},
      "state": "anxious"
    },
    {
      "id": "guard",
      "role": "authority",
      "start": {"x": 15, "y": 6},
      "state": "authority"
    }
  ],
  "timeline": [
    {
      "t": 0,
      "type": "spawn",
      "actor": "agent_09",
      "pose": "standing",
      "facing": "right"
    },
    {
      "t": 1200,
      "type": "move",
      "actor": "guard",
      "to": {"x": 12, "y": 6},
      "speed": "slow"
    },
    {
      "t": 2500,
      "type": "face",
      "actor": "agent_09",
      "target": "guard"
    },
    {
      "t": 3200,
      "type": "emote",
      "actor": "agent_09",
      "emote": "fear"
    },
    {
      "t": 5000,
      "type": "speech",
      "actor": "guard",
      "text": "...",
      "duration": 1600
    },
    {
      "t": 7000,
      "type": "step_back",
      "actor": "agent_09"
    },
    {
      "t": 8500,
      "type": "crowd_react",
      "actors": ["agent_03", "agent_06"],
      "reaction": "watch"
    }
  ],
  "rationale_short": "Guard approaches focal agent; witnesses turn toward pressure event."
}
```

---

## 9. 구현 원칙

### 9.1 Canvas Primitive Only

Canvas primitive only로 시작한다.

- 외부 asset 금지
- sprite sheet 없이도 8-bit 캐릭터를 frame별로 그린다.
- static scene과 달리 걷기 frame 2~3개는 허용한다.

### 9.2 제한된 Animation만 허용

허용되는 animation:

- walking
- facing change
- speech bubble
- emote pop
- small step back / approach
- crowd head turn
- kneel / collapse pose transition

### 9.3 금지되는 Animation

금지되는 animation:

- free roaming simulation
- pathfinding
- physics
- combat
- continuous world replay
- timeline scrub
- user-controlled movement

### 9.4 Interaction Readability 우선

상호작용은 선과 cue로 설명하지 말고 행동 순서로 보여준다.

우선순위:

1. actor가 target을 향해 이동한다.
2. actor가 target을 바라본다.
3. crowd가 사건 발생 후 반응한다.
4. grief / forgiveness / confession은 이펙트보다 행동 변화로 먼저 표현한다.

### 9.5 Camera

- fixed camera
- focused tile stage
- 20×12 또는 22×13 tile 정도
- 전체 world map 금지
- 한 candidate 장면만 보여준다.

### 9.6 UI

- scene selector 3개
- play / pause / replay 버튼
- speed 1x만 기본
- 오른쪽 packet panel은 유지 가능
- 단, 5초 테스트 때 packet panel을 가려도 이해되어야 한다.
- timeline scrub 금지

### 9.7 Visual Language

- 포켓몬식 top-down tile stage 감각
- agent는 tile 위를 한 칸 또는 반 칸씩 이동
- facing direction 중요
- 말풍선은 짧게
- emote는 최소화
- relation line은 기본적으로 사용하지 않는다.
- relation line이 필요하면 debug mode에서만 표시한다.

---

## 10. Scene별 Playback 설계

## 10.1 C01_t15 — Authority Pressure

### 목표 문장

```text
Guard가 다가오자 focal이 위축되고, 주변 인물들이 그 장면을 바라본다.
```

### Timeline

| Time | Event |
|---|---|
| 0s | focal center-left standing / anxious idle |
| 1s | guard appears right, facing left |
| 2s | guard walks toward focal |
| 3s | witnesses turn their heads toward guard/focal |
| 4s | focal shakes or steps back |
| 5s | guard stops within pressure distance |
| 6s | small speech bubble from guard |
| 8s | focal fear emote / pressure pulse |
| 10s | scene holds |

---

## 10.2 C02_t25 — Split Group

### 목표 문장

```text
왼쪽의 confession이 오른쪽 grief 반응을 만들고, 집단이 갈라진다.
```

### Timeline

| Time | Event |
|---|---|
| 0s | two loose groups visible |
| 1s | agent_3 steps forward left |
| 2s | agent_3 speech bubble |
| 3s | nearby agents face agent_3 |
| 4s | agent_5 on right turns away or steps back |
| 5s | grief emote on agent_5 |
| 6s | center gap widens by small reposition |
| 8s | left group stays watching, right side withdraws |
| 10s | scene holds |

---

## 10.3 C03_t142 — Confession Cluster

### 목표 문장

```text
중앙 confession을 crowd가 지켜보고, 일부가 forgiveness 반응으로 가까워진다.
```

### Timeline

| Time | Event |
|---|---|
| 0s | crowd semicircle idle |
| 1s | focal agent moves one step to center |
| 2s | speech bubble / confession emote |
| 3s | crowd faces center |
| 4s | second focal kneels or collapses |
| 5s | brief silence hold |
| 6s | two crowd members step slightly inward |
| 7s | forgiveness emote appears from crowd side |
| 9s | central group holds |
| 11s | fade/hold |

---

## 11. 검증 기준

각 scene을 packet panel 없이 5초 본다.

정지 이미지가 아니라 **재생 중 첫 5초**를 본다.

### PASS

- 5초 안에 “누가 누구에게 무엇을 하고 있는지” 말할 수 있다.
- 이동 / 시선 / 말풍선 / 반응 순서가 보인다.
- relation line 없이도 상호작용이 읽힌다.

### WEAK

- 움직임은 있지만 사건 의도는 여전히 애매하다.
- agent들이 걷긴 하는데 왜 움직이는지 모르겠다.
- 말풍선 없이는 이해가 안 된다.

### FAIL

- 그냥 캐릭터들이 움직이는 테스트 화면처럼 보인다.
- 사건이 아니라 UI/기술 데모처럼 보인다.
- 기존 static PSD와 이해도가 크게 다르지 않다.

---

## 12. 분기 기준

## 12.1 PEP-A

Pixel Event Playback이 통과.

다음은 candidate 5~7개 확장.

- 새 anchor는 아직 금지
- 새 scenario 금지
- 새 engine metric 금지
- story renderer 재개 금지

## 12.2 PEP-B

움직임은 도움이 되지만 연출이 약함.

추가 feature 금지.

timeline staging만 1회 cleanup.

가능한 cleanup:

- 이동 타이밍 조정
- facing 전환 명확화
- speech bubble 노출 시간 조정
- emote 과잉 제거
- crowd reaction timing 조정

## 12.3 PEP-C

움직여도 사건 이해가 안 됨.

이 경우 WITNESS visual은 pixel game 방식이 아니라 storyboard/comic panel approach로 전환한다.

---

## 13. 절대 금지

이번 MVP에서 금지:

- full replay 구현 금지
- timeline scrub 금지
- pathfinding 금지
- player intervention 금지
- playable 구현 금지
- story renderer 재개 금지
- 새 scenario 금지
- 새 anchor 금지
- 새 engine metric 금지
- visual/explorer.html 수정 금지
- visual/pixel_world_static.html 수정 금지
- 기존 pixel_scene.html 추가 patch 금지
- React / Phaser / PixiJS 도입 금지
- 외부 asset 금지

---

## 14. 이번 MVP에서 Phaser를 바로 쓰지 않는 이유

목표는 엔진 교체가 아니라 **interaction / flow 가설 검증**이다.

Canvas primitive로도 다음은 검증 가능하다.

- walking
- facing
- speech
- reaction playback
- short event staging

Phaser / Tilemap / Tiled는 Pixel Event Playback이 통과한 뒤 v0.3 또는 v0.4에서 검토한다.

---

## 15. 완료 조건

Pixel Event Playback MVP 완료 조건:

1. `scripts/visual/build_event_playbacks.py` 작성
2. `data/visual/event_playbacks.json` 생성
3. `visual/pixel_event_playback.html` 작성
4. 3 candidate playback 가능
5. play / pause / replay만 제공
6. packet panel 없이 5초 테스트 가능
7. `docs/visual/PIXEL_EVENT_PLAYBACK_REVIEW.md` 작성
8. `PEP-A / PEP-B / PEP-C` 판정
9. 추가 기능 없이 종료

---

## 16. 최종 요약

정적 장면을 더 고치는 단계는 끝났다.

Pixel Scene Director Static MVP는 `PW-SC-B`로 freeze한다.

다음은 “움직이는 짧은 사건 재생”으로 간다.

```text
Pixel Scene Director Static
→ freeze as PW-SC-B
→ Pixel Event Playback MVP
→ candidate 1개 = 10~20초 short cutscene playback
```
