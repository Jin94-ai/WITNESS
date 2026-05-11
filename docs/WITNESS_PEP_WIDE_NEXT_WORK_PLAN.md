# WITNESS — Pixel Event Playback 다음 작업계획서

## 0. 현재 결론

Pixel Scene Director Static은 `PW-SC-B`로 freeze한다. 정적 이미지에 선, cue, wave를 계속 추가하는 방식은 상호작용과 사건 흐름을 직관적으로 전달하기 어렵다.

현재 전환 방향은 **Pixel Event Playback**이다.

핵심 목표는 전체 replay나 playable이 아니라, `story_ready candidate 1개`를 **10~20초짜리 짧은 포켓몬식 사건 재생**으로 번역하는 것이다.

```text
candidate → event_playback_script → pixel_event_playback.html → 5초 이해 테스트
```

현재 업로드된 기준 파일:

- `visual/pixel_event_playback.html`
- `data/visual/event_playbacks.json`

현재 구현은 3개 playback, Canvas primitive, play/pause/replay, hide packet, requestAnimationFrame 기반 애니메이션, fixed tile stage까지 도달했다. 다음 단계는 새 기능을 무작정 추가하는 것이 아니라 **연출 문법을 안정화하고, 화면만 봐도 사건이 읽히도록 만드는 것**이다.

---

## 1. 현재 PEP 구현 진단

### 1.1 잘 된 점

- 정적 scene보다 방향은 맞다.
- `move`, `face`, `step_back`, `speech`, `emote`, `pose_change`, `crowd_react` 이벤트 구조는 최소한의 사건 재생 문법으로 적절하다.
- `Play / Pause / Replay`만 둔 것도 맞다. timeline scrub을 넣지 않은 결정은 유지한다.
- packet hide 기능이 있어 5초 테스트를 실제로 수행할 수 있다.
- Phaser/PixiJS 없이 Canvas primitive로 검증하는 것도 현재 단계에서는 맞다.

### 1.2 아직 약한 점

현재 JSON timeline을 보면 움직임은 생겼지만, 아직 **행동의 의미가 약할 가능성**이 높다.

예상 리스크:

1. **걸어감이 목적 없이 보일 수 있음**  
   guard가 이동하고, agent가 한 칸 움직이지만, 왜 움직였는지 시각적으로 강조되지 않을 수 있다.

2. **말풍선 텍스트가 너무 약함**  
   `...`, `...!?`는 말하고 있다는 신호는 되지만, 사건의 성격은 거의 전달하지 않는다.

3. **facing 변화가 작아서 crowd reaction이 안 보일 수 있음**  
   8x8 픽셀 캐릭터에서 고개 방향만 바뀌는 것은 5초 안에 읽히기 어렵다.

4. **emote가 늦게 등장함**  
   일부 장면은 5초 이후에 핵심 감정 emote가 나와서 5초 테스트에서 안 보일 수 있다.

5. **장면별 hook이 부족함**  
   포켓몬식 이벤트는 첫 1~2초 안에 “이 장면은 무엇을 봐야 하는가”가 나와야 한다.

### 1.3 잠정 판정

코드/JSON 기준으로는 `PEP-B` 가능성이 높다.

이유:

- 정적 PSD보다는 분명 개선됐다.
- 하지만 5초 안에 “누가 누구에게 무엇을 했다”가 바로 보일 정도로 사건 연출이 강하지 않을 가능성이 있다.
- 따라서 다음 작업은 대규모 확장이 아니라 **PEP Staging Grammar Cleanup + 후보 확장 준비**가 맞다.

---

## 2. 다음 세션 목표

다음 세션은 바로 앞에 보이는 작은 버그 하나만 고치는 식으로 가지 않는다. 아래 순서대로 한 번에 넓게 진행한다.

### 목표 A — 현재 PEP의 연출 문법 강화

3개 scene의 5초 이해도를 높인다.

핵심은 sprite 품질이 아니라 **이벤트 타이밍, 행동 대비, 반응 순서**다.

### 목표 B — playback script grammar 문서화

`event_playback_v1`을 단순 JSON 산출물이 아니라 WITNESS visual layer의 중간 표현으로 정리한다.

### 목표 C — candidate 확장 가능성 준비

PEP가 통과할 경우 3개에서 5~7개로 확장할 수 있도록 builder와 review 절차를 정리한다.

### 목표 D — 실패 시 storyboard/comic 전환 조건 명확화

PEP도 직관성이 약하면 더 이상 pixel game 형식을 붙잡지 않고, storyboard/comic panel 방식으로 넘어간다.

---

## 3. 작업 범위

## 3.1 이번에 허용되는 작업

허용:

- `visual/pixel_event_playback.html` 개선
- `data/visual/event_playbacks.json` timeline 보정
- `scripts/visual/build_event_playbacks.py` 보정
- `docs/visual/PIXEL_EVENT_PLAYBACK_REVIEW.md` 업데이트
- `docs/visual/PIXEL_EVENT_PLAYBACK_GRAMMAR.md` 신규 작성
- `docs/visual/PIXEL_EVENT_PLAYBACK_NEXT.md` 또는 본 계획서 반영
- 필요 시 `docs/INDEX.md`, `progress.md`, `lessons.md` 업데이트

허용되는 animation:

- walk
- face
- step back
- approach
- speech bubble
- emote pop
- kneel/collapse pose transition
- short crowd reaction
- hold / pause beat
- screen attention cue, 단 debug overlay가 아니라 연출 효과로 제한

## 3.2 금지되는 작업

금지:

- full replay 구현
- timeline scrub 구현
- playable/player control
- pathfinding
- physics
- combat
- 새 scenario
- 새 anchor
- 새 engine metric
- story renderer 재개
- visual/explorer.html 수정
- visual/pixel_world_static.html 수정
- visual/pixel_scene.html 추가 patch
- React/Phaser/PixiJS 도입
- 외부 asset 도입
- 월드 전체 지도 구현

---

## 4. 핵심 전략: “움직임”이 아니라 “연출”을 고친다

현재 문제는 캐릭터가 움직이느냐가 아니다. 이미 움직인다. 다음 질문은 이것이다.

```text
그 움직임이 사건으로 읽히는가?
```

따라서 다음 세션에서는 다음 원칙을 적용한다.

### 4.1 5초 안에 핵심 사건이 나와야 한다

각 scene의 감정 emote, 핵심 반응, 방향 전환은 5초 안에 반드시 보여야 한다.

현재 위험:

- C01 fear emote가 8초에 나옴 → 5초 테스트에 늦다.
- C02 grief emote가 5.2초에 나옴 → 거의 늦다.
- C03 forgiveness emote가 7.8초에 나옴 → 5초 테스트에 늦다.

수정 방향:

```text
핵심 emote는 2.5~4.5초 사이에 등장시킨다.
후반부 6~12초는 hold / aftermath / secondary reaction으로 쓴다.
```

### 4.2 행동 전후 대비를 만든다

좋은 사건 재생은 이 구조를 가진다.

```text
before → trigger → reaction → aftermath
```

각 scene은 이 순서를 따라야 한다.

- before: 누가 어디에 있는가
- trigger: 누가 행동을 시작하는가
- reaction: 누가 영향을 받는가
- aftermath: 장면의 새 상태가 무엇인가

### 4.3 crowd reaction은 facing만으로 부족하다

8x8 sprite에서 facing 변화는 약하다. crowd reaction은 최소 하나 이상의 추가 행동이 필요하다.

가능한 보강:

- one-step inward
- one-step backward
- small jump/shock frame
- `?`, `!`, tear, plus emote
- brief pause after reaction
- actor state color 변화는 최소화하되 필요 시 허용

### 4.4 말풍선은 “...”만으로 충분하지 않다

텍스트를 길게 쓰면 story renderer가 되지만, 너무 추상적이면 장면이 안 읽힌다.

허용 가능한 짧은 text:

```text
"..."        침묵/고백 전조
"!"          충격
"...?"       의문/동요
"Forgive"    너무 직접적이라 가능하면 피함
"I..."       고백 시작 느낌
"Stop"       authority 압박
"Enough"     authority 압박
```

추천:

- C01 guard speech: `Stop.` 또는 `Enough.`
- C02 confession speech: `I...`
- C03 confession speech: `I...`

단, 최종적으로 텍스트 의존을 줄여야 한다. 말풍선은 사건의 시작 신호일 뿐이다.

---

## 5. Scene별 구체 작업

## 5.1 C01_t15 — authority_pressure

현재 구조:

- focal 2명 spawn
- guard 1초 등장
- guard 2초부터 천천히 접근
- witness 3초에 guard를 봄
- focal 4초에 step_back
- guard 6초 말풍선
- agent_09 8초 fear emote

문제:

- fear emote가 너무 늦다.
- guard 말풍선도 6초라 5초 테스트에서 늦다.
- step_back이 먼저 나오지만 왜 물러나는지 신호가 약하다.

수정안:

```text
0.0s focal + witnesses spawn
0.8s guard spawn, facing left
1.2s guard speech: "Stop." 또는 "Enough."
1.5s guard move toward focal
2.4s witnesses face guard/focal
3.0s focal_09 fear emote
3.2s focal_09 step_back
3.4s focal_03 step_back
4.2s guard stops near pressure distance
5.0s hold: focal backed away, witnesses watching
6.5s optional second guard micro-step or pose hold
```

기대 문장:

```text
“guard가 다가오며 제지하고, focal들이 위축된다.”
```

Pass 조건:

- 5초 안에 guard 압박과 focal 후퇴가 보여야 한다.
- 말풍선을 가려도 guard→focal 방향성이 보여야 한다.

## 5.2 C02_t25 — saturation_split

현재 구조:

- 좌우 그룹 spawn
- agent_03이 1초에 한 칸 이동
- 2.2초 speech
- 3초 left witnesses face speaker
- 4초 agent_05 turns away
- 4.5초 step_back
- 5.2초 grief emote
- 6초 이후 right witnesses 이동

문제:

- grief가 5초 이후라 테스트에 늦다.
- right group이 “분열”이 아니라 그냥 늦게 움직이는 것처럼 보일 수 있다.
- 좌 confession → 우 grief의 인과가 약하다.

수정안:

```text
0.0s two groups spawn with clear gap
0.8s agent_03 step forward
1.5s agent_03 speech: "I..."
2.2s left witnesses face agent_03
2.8s agent_05 face away / turn right
3.2s agent_05 grief emote
3.5s agent_05 step_back
4.0s right witnesses step slightly away from center
4.8s hold: left group facing speaker, right group withdrawn
6.0s optional secondary reaction: one right witness faces agent_05
```

추가 연출 후보:

- center gap을 시각적으로 키우기 위해 right group의 이동을 더 빨리 한다.
- rift line 같은 overlay는 기본 금지. 필요하면 아주 약한 ground crack만 가능하지만, 먼저 timeline만으로 해결한다.

기대 문장:

```text
“왼쪽의 고백 때문에 오른쪽이 뒤로 물러나며 갈라진다.”
```

Pass 조건:

- agent_03이 trigger라는 점이 보여야 한다.
- agent_05가 reaction target이라는 점이 보여야 한다.
- 좌우 group gap이 5초 안에 더 벌어져야 한다.

## 5.3 C03_t142 — confession_cluster

현재 구조:

- crowd semicircle spawn
- agent_09 1초 중앙 이동
- 2.2초 speech
- 3초 crowd_react
- 4초 agent_03 kneeling
- 6초 supporter inward move
- 7.8초 forgiveness emote

문제:

- forgiveness 반응이 7.8초라 5초 테스트에서 늦다.
- crowd_react가 facing만 바뀌므로 약할 수 있다.
- kneeling은 좋지만 reaction chain이 늦다.

수정안:

```text
0.0s crowd semicircle spawn, all idle
0.8s agent_09 step to center
1.6s agent_09 speech: "I..."
2.4s all crowd face center
3.0s agent_03 kneel/collapse
3.5s supporters agent_06/12 step inward
4.2s forgiveness emote on supporters
5.0s hold: crowd watches, supporters closer, kneeler down
7.0s optional second forgiveness pulse or silent hold
```

기대 문장:

```text
“중앙 고백 뒤에 한 인물이 무너지고, 주변 사람들이 다가와 반응한다.”
```

Pass 조건:

- 5초 안에 confession → kneel → supporter inward reaction이 모두 보여야 한다.
- crowd가 단순 배치가 아니라 witness처럼 느껴져야 한다.

---

## 6. 코드 레벨 개선 계획

## 6.1 timeline timing cleanup

`event_playbacks.json` 또는 builder의 hand-authored timeline을 먼저 수정한다.

우선순위:

1. 핵심 speech를 1.2~2.2초로 당김
2. 핵심 emote를 3.0~4.5초로 당김
3. reaction movement를 3.5~5.0초로 당김
4. 6초 이후는 aftermath hold로 사용

## 6.2 event type 추가는 최대한 금지

새 event type을 늘리기 전에 기존 이벤트 조합으로 해결한다.

현재 event만으로 충분히 가능한 것:

- `move`
- `face`
- `step_back`
- `speech`
- `emote`
- `pose_change`
- `crowd_react`

단, 다음 1개는 검토 가능하다.

```json
{
  "type": "pause_beat",
  "duration": 600
}
```

하지만 실제 구현상 필요 없으면 추가하지 않는다. 타이밍 간격만으로도 hold는 가능하다.

## 6.3 visual emphasis 개선

필요할 경우 `pixel_event_playback.html`에서 다음만 개선한다.

허용:

- speech bubble 위치/크기 개선
- emote 크기 1.2~1.5배
- walking bob 2px → 3px
- step_back 이동 거리를 1 tile이 아니라 0.5 tile로 조정할 수 있는 `step_back` 옵션 추가
- kneeling sprite를 더 낮고 확실하게 수정
- authority sprite의 silhouette 강화

주의:

- 캐릭터를 너무 크게 키우는 것은 핵심 해결책이 아니다.
- line overlay는 추가하지 않는다.
- debug relation line은 만들더라도 기본 off.

## 6.4 rendering bug / robustness audit

다음 항목을 점검한다.

- `step_back`이 facing 반대 방향으로 정확히 작동하는가
- `face target`이 target의 최신 위치를 보고 계산되는가
- move 중에 다른 face 이벤트가 들어올 때 이상하지 않은가
- speech/emote가 actor head 위에 잘 보이는가
- duration 종료 후 actor pose가 standing으로 돌아오는 것이 kneeling을 깨지 않는가
- movement interpolation이 tile boundary에서 튀지 않는가
- depth sort가 y 기준으로 자연스러운가

---

## 7. 문서화 작업

## 7.1 PIXEL_EVENT_PLAYBACK_REVIEW.md 업데이트

추가할 섹션:

```md
## 7. Lee 5-Second Test — PEP Timing Cleanup

### Test Conditions
- Packet hidden
- First 5 seconds only
- No scene title reading
- One-sentence summary immediately after viewing

### C01_t15 — authority_pressure
Verdict: PASS / WEAK / FAIL
Observed:
Reason:

### C02_t25 — saturation_split
Verdict: PASS / WEAK / FAIL
Observed:
Reason:

### C03_t142 — confession_cluster
Verdict: PASS / WEAK / FAIL
Observed:
Reason:

## Final Case
PEP-A / PEP-B / PEP-C

Decision:
```

## 7.2 신규 문서: PIXEL_EVENT_PLAYBACK_GRAMMAR.md

목적:

`event_playback_v1`이 어떤 visual grammar를 쓰는지 명문화한다.

포함 내용:

- schema 개요
- actor roles
- event types
- timing rules
- 5-second readability rule
- scene composition rules
- forbidden patterns
- candidate expansion rules

핵심 문장:

```text
PEP는 simulation replay가 아니라 candidate cutscene translation이다.
```

## 7.3 lessons.md 업데이트

추가 교훈:

```text
L50 — Pixel event readability depends more on timing and reaction order than sprite detail. If the key emote/reaction appears after the first 5 seconds, the scene fails the observer test even when the full 12-second playback is coherent.
```

---

## 8. 테스트 계획

## 8.1 코드 테스트

필수:

```bash
python scripts/visual/build_event_playbacks.py
python -m pytest
```

가능하면 별도 validator 추가:

```bash
python scripts/visual/validate_event_playbacks.py
```

검증 항목:

- schema_version 존재
- playback_count와 실제 playbacks 길이 일치
- actor id 중복 없음
- timeline t 오름차순
- timeline actor가 actors에 존재
- duration_ms를 넘는 event 없음
- move target tile이 stage 밖으로 나가지 않음
- 지원하지 않는 event type 없음

## 8.2 수동 5초 테스트

절차:

```bash
cd c:\Users\이진석\Desktop\Witness
python -m http.server 8000
```

브라우저:

```text
http://localhost:8000/visual/pixel_event_playback.html?scene=1
http://localhost:8000/visual/pixel_event_playback.html?scene=2
http://localhost:8000/visual/pixel_event_playback.html?scene=3
```

각 scene:

1. Hide packet
2. Replay
3. 첫 5초만 보기
4. 바로 한 문장 기록
5. PASS / WEAK / FAIL 기록

## 8.3 자동 캡처 대안

Win+G가 안 될 경우, 다음 중 하나 사용.

### 방법 A — browser frame capture helper

`pixel_event_playback.html`에 debug-only capture button을 넣는 방식은 이번 MVP에서는 보류한다. 대신 개발자 도구 screenshot이나 PowerPoint/OBS를 사용한다.

### 방법 B — 타임스탬프 스크린샷

각 scene에서 다음 타이밍을 캡처한다.

```text
0s / 1.5s / 3s / 5s / 8s
```

이 방식으로도 timeline staging 문제는 어느 정도 판단 가능하다.

---

## 9. 다음 분기

## 9.1 PEP-A — 통과

조건:

- 3개 중 최소 2개 PASS
- C03는 PASS 또는 강한 WEAK-PASS
- packet 없이 5초 안에 사건 문장이 나온다
- 움직임이 기술 데모가 아니라 사건으로 보인다

다음 작업:

1. candidate 5~7개로 확장
2. anchor는 여전히 `peter_scarcity_baseline` only
3. schema 변경 금지
4. 새 event type 추가 금지
5. `build_event_playbacks.py`의 대상 candidate만 확장
6. review 문서에 expansion smoke test 추가
7. portfolio asset 후보로 PEP를 연결

확장 후보 예시:

- P03_t66_agent_08
- C05_t147
- 기타 story_ready candidate 중 salience 높은 항목

## 9.2 PEP-B — 부분 통과

조건:

- 움직임은 도움이 되지만 사건이 아직 애매함
- 말풍선/패널 없이는 이해가 약함
- agent가 움직이긴 하지만 왜 움직이는지 모름

다음 작업:

1. timeline staging cleanup 1회만 수행
2. 핵심 reaction을 5초 안으로 당김
3. emote 크기/가시성 개선
4. speech text 최소 보강
5. crowd reaction을 facing-only에서 step/pose/emote 포함으로 보강
6. 다시 5초 테스트

2회 cleanup 후에도 B면:

```text
PEP partial success로 freeze.
Storyboard/comic approach 설계로 이동.
```

## 9.3 PEP-C — 실패

조건:

- 움직여도 사건이 안 읽힘
- 포켓몬식 화면이 오히려 기술 데모처럼 보임
- 정적 PSD보다 이해도가 크게 좋아지지 않음

다음 작업:

1. PEP freeze
2. failure memo 작성
3. storyboard/comic panel approach 설계
4. 구현은 바로 하지 않음

대안 방향:

```text
candidate 1개 = 1컷 또는 3컷 comic panel
말풍선, 시선, 거리, 프레이밍 중심
time axis는 panel sequence로 표현
```

---

## 10. 장기 방향

## 10.1 v0.2 내부 목표

WITNESS visual track의 v0.2 목표는 “멋진 게임 화면”이 아니다.

목표:

```text
Observer가 잡은 story_ready candidate를 사람이 5초 안에 이해할 수 있는 visual event로 번역한다.
```

## 10.2 v0.3 이후 검토

PEP가 통과하면 그때 다음을 검토한다.

- Phaser 또는 PixiJS 도입
- Tiled map 사용
- sprite sheet 도입
- richer tile props
- camera pan
- multi-candidate playlist
- exportable demo video

하지만 현재는 금지다. 지금은 engine 교체가 아니라 **medium fit 검증** 단계다.

## 10.3 playable은 아직 금지

Playable/intervention은 장기 가능성은 있지만, 현재는 visual observer 검증이 우선이다.

현재 순서:

```text
observer data → candidate → visual playback → 5-sec comprehension → expansion → portfolio/internal demo
```

Playable은 이 뒤에만 검토한다.

---

## 11. 다음 세션용 실행 프롬프트

```text
WITNESS — Pixel Event Playback 다음 세션 실행

현재 상태:
Pixel Scene Director Static은 PW-SC-B로 freeze됨.
Pixel Event Playback MVP는 구현 완료됨.
업로드된 기준 파일은 visual/pixel_event_playback.html, data/visual/event_playbacks.json.
현재 PEP는 움직임은 있으나, 5초 안에 사건 흐름이 충분히 읽히는지는 불확실함.

이번 세션 목표:
바로 앞의 작은 수정 하나만 하지 말고, PEP의 연출 문법을 넓게 안정화한다.
핵심은 sprite detail이 아니라 timing / reaction order / 5-second readability다.

진단:
- C01 fear emote와 guard speech가 늦음. 5초 안에 압박이 더 분명해야 함.
- C02 grief reaction이 5초 이후라 늦음. 좌 confession → 우 grief/split 인과를 5초 안에 보여야 함.
- C03 forgiveness reaction이 7.8초라 늦음. confession → kneel → supporter inward reaction이 5초 안에 보여야 함.
- crowd_react가 facing-only라 약할 수 있음.
- 말풍선 "..."만으로는 trigger가 약함.

작업:
1. event_playbacks.json 또는 build_event_playbacks.py에서 timeline timing cleanup.
2. 핵심 speech는 1.2~2.2초 사이로 당김.
3. 핵심 emote/reaction은 3.0~4.5초 사이로 당김.
4. 6초 이후는 aftermath hold로 사용.
5. C01: guard speech/approach/focal fear/step_back을 5초 안에 완료.
6. C02: agent_03 speech → agent_05 grief/step_back → right group withdrawal을 5초 안에 완료.
7. C03: agent_09 confession → agent_03 kneel → supporters inward/forgiveness를 5초 안에 완료.
8. pixel_event_playback.html에서 emote visibility, speech bubble readability, kneeling silhouette, walking bob만 필요 시 개선.
9. 새 event type은 가능하면 추가하지 말 것.
10. relation line / diagram overlay 추가 금지.
11. docs/visual/PIXEL_EVENT_PLAYBACK_GRAMMAR.md 작성.
12. docs/visual/PIXEL_EVENT_PLAYBACK_REVIEW.md에 Timing Cleanup 5초 테스트 영역 추가.
13. 필요하면 validate_event_playbacks.py 작성.
14. progress.md / lessons.md / docs/INDEX.md 갱신.

절대 금지:
full replay, timeline scrub, pathfinding, playable, player intervention, story renderer, 새 scenario, 새 anchor, 새 engine metric, React/Phaser/PixiJS, 외부 asset, visual/explorer.html 수정, visual/pixel_world_static.html 수정, visual/pixel_scene.html 추가 patch.

완료 조건:
- 3개 playback 모두 첫 5초 안에 trigger → reaction이 보이도록 timeline 조정.
- PEP grammar 문서 작성.
- review 문서에 Lee 5초 테스트 영역 준비.
- validator 또는 최소 JSON consistency check 통과.
- 추가 기능 없이 멈춤.
```

---

## 12. 최종 판단 기준

다음 테스트에서 이 질문 하나만 본다.

```text
첫 5초 안에 “누가 누구에게 무엇을 해서 어떤 반응이 일어났는가”가 보이는가?
```

보이면 PEP는 계속 간다.

안 보이면 pixel game 형식 자체를 더 붙잡지 말고 storyboard/comic으로 넘긴다.

