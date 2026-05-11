# WITNESS — Pixel Event Playback 다음 넓은 진행 지시서

**Date:** 2026-05-02  
**Track:** Pixel Event Playback (PEP) MVP  
**Current state:** 3 candidate cutscene playback 구현 완료, 영상 검토 완료  
**Recommended case:** **PEP-B+** — 방향은 맞다. 다만 아직 “살아 있는 포켓몬식 관찰 화면”이라기보다는 “미니멀 cutscene prototype”에 가깝다. 정적 PSD보다는 명확히 낫지만, 바로 candidate 확장으로 가기 전 1회의 readability/staging 정리가 필요하다.

---

## 0. 현재 판단 요약

PEP는 PSD보다 나아졌다.

- 캐릭터가 실제로 걷는다.
- 말풍선, emote, facing change, step back, kneeling이 시간 순서로 발생한다.
- 첫 5초 안에 trigger → reaction 구조가 들어온다.
- relation line / wave / rift 없이 행동 순서로 사건을 전달하려는 방향은 맞다.

하지만 아직 부족하다.

- 캐릭터의 이동과 반응은 보이지만, 감정적 인과가 약하다.
- 배경이 넓고 비어 있어 “세계”보다 “테스트 스테이지”처럼 보인다.
- 말풍선과 emote가 작고 짧아 첫인상에서 놓치기 쉽다.
- scene 2는 특히 “좌우 분리”는 보이지만 “왼쪽 말 때문에 오른쪽이 무너진다”는 인과가 약하다.
- scene 3은 crowd semicircle은 보이지만 kneel/forgiveness reaction이 더 강조되어야 한다.

따라서 지금은 **PEP-A 확장 직전 단계**가 아니라 **PEP-B+ cleanup 단계**로 본다.

---

## 1. Scene별 관찰 verdict

### 1.1 C01_t15 — authority_pressure

**Observed:**

- Guard가 오른쪽에서 등장하고 왼쪽 focal 쪽으로 이동한다.
- `Stop.` 말풍선은 trigger로 기능한다.
- focal 쪽 fear emote와 step_back이 보여서 압박 상황은 읽힌다.
- witnesses가 바라보는 흐름은 존재하지만 매우 미세하다.

**Verdict:** `PASS-leaning WEAK`

**판단:**

이 scene은 셋 중 가장 읽힌다. 다만 guard가 위협적으로 다가온다기보다 오른쪽에서 작은 검은 캐릭터가 이동하는 느낌도 남아 있다. focal의 후퇴와 fear emote를 조금 더 명확히 하면 PASS로 올릴 수 있다.

---

### 1.2 C02_t25 — saturation_split

**Observed:**

- 좌우 두 그룹 구도는 보인다.
- 왼쪽 agent가 말풍선을 띄우고, 오른쪽 agent가 grief emote를 띄운다.
- 오른쪽 그룹이 조금 벌어지지만, 인과가 강하지 않다.
- 중앙 gap이 “사건으로 벌어진 분열”이라기보다 처음부터 떨어진 배치처럼 보일 수 있다.

**Verdict:** `WEAK`

**판단:**

현재 PEP에서 가장 약한 scene이다. 핵심은 이동량이나 캐릭터 크기가 아니라 **반응의 원인-결과 연결**이다. 왼쪽 confession 이후 오른쪽이 “돌아서고 물러나고 주변도 따라 갈라지는” 순서가 더 과장되어야 한다.

---

### 1.3 C03_t142 — confession_cluster

**Observed:**

- 중앙 speaker가 움직이고 말풍선을 띄운다.
- crowd semicircle은 가장 명확한 구도다.
- kneeling pose와 supporters inward move가 들어온다.
- forgiveness emote가 4.2초에 들어오지만 작아서 놓칠 수 있다.

**Verdict:** `WEAK-PASS`

**판단:**

방향은 좋다. scene 3은 PEP의 장점이 가장 잘 보인다. 다만 5초 안에 “중앙 confession → 군중 반응 → forgiveness”까지 한 번에 읽히기에는 supporter 반응과 emote가 약하다.

---

## 2. Final Case

```text
Final Case: PEP-B+
```

**Decision:**

- Pixel Event Playback 방향은 유지한다.
- Pixel Scene Director static 방식으로 돌아가지 않는다.
- Storyboard/comic fork로 바로 넘어가지 않는다.
- Candidate 확장 전에 **PEP Readability Cleanup 1회**를 수행한다.
- Cleanup 후에도 2개 이상 PASS가 나오면 PEP-A로 승격하고 candidate 5-7개 확장으로 이동한다.

---

## 3. 다음 목표 — PEP Readability Cleanup

### 목표

첫 5초 안에 다음 문장이 더 쉽게 나오도록 만든다.

```text
C01: 권위자가 다가오고, focal이 겁먹고 물러난다.
C02: 왼쪽의 고백/발화 때문에 오른쪽이 상처받고 집단이 갈라진다.
C03: 중앙 고백을 군중이 보고, 무너진 인물과 용서 반응이 생긴다.
```

### 핵심 원칙

```text
더 많은 기능이 아니라, 더 강한 staging.
```

이번 cleanup은 feature expansion이 아니다. 새 anchor, 새 scenario, 새 engine metric, 새 UI 기능을 만들지 않는다.

---

## 4. 허용 작업 범위

### 수정 허용

- `scripts/visual/build_event_playbacks.py`
- `data/visual/event_playbacks.json`
- `visual/pixel_event_playback.html`
- `docs/visual/PIXEL_EVENT_PLAYBACK_REVIEW.md`
- `docs/visual/PIXEL_EVENT_PLAYBACK_GRAMMAR.md`
- `scripts/visual/validate_event_playbacks.py`
- `tests/test_visual/test_event_playbacks.py`

### 수정 금지

- `visual/explorer.html`
- `visual/pixel_world_static.html`
- `visual/pixel_scene.html`
- engine core
- observer core
- story renderer
- scenario files
- anchor 생성 로직

---

## 5. Cleanup 작업 지시

## 5.1 Viewer readability 개선

파일:

```text
visual/pixel_event_playback.html
```

### A. Stage framing 개선

현재 22×13 stage가 너무 넓고 비어 보인다. 전체 world map은 아니지만, focused stage 감각을 더 강하게 만든다.

허용 방향:

- canvas 크기는 유지해도 된다.
- 실제 action zone은 중앙 16×10 정도로 압축한다.
- 배경 props를 scene_type별로 최소 추가한다.
- props는 장식이 아니라 사건 맥락을 보여야 한다.

Scene별 props 제안:

```text
C01 authority_pressure:
- guard side에 작은 post/gate/shadow strip
- focal 쪽에 압박 공간을 암시하는 narrow path
- stone plaza가 guard 이동을 가리지 않도록 조정

C02 saturation_split:
- 중앙 빈 공간을 “gap”으로 읽히게 하는 바닥 색 차이 또는 crack-like tile 2-3개
- 단, PSD-LC1처럼 빨간 rift/line으로 돌아가지 말 것

C03 confession_cluster:
- 중앙 stone plaza를 confession circle처럼 사용
- crowd semicircle이 더 자연스럽게 보이도록 floor focus만 약하게 강조
```

금지:

- relation line
- wave
- aura
- rift overlay
- debug line
- 미니맵/전체맵

---

### B. Sprite/action 가독성 개선

현재 sprite는 작지만 크기만의 문제는 아니다. 그래도 motion readability를 위해 **role-based visual emphasis**는 허용한다.

허용:

- focal/authority/supporter만 scale `1.15~1.25`
- crowd/witness는 scale `1.0`
- emote는 현재보다 1.25배
- speech bubble은 현재보다 약간 더 명확하게 유지

금지:

- 모든 캐릭터를 크게 만드는 방식
- 캐릭터 크기만 키워서 해결하려는 방식

구현 제안:

```js
function actorScale(actor) {
  if (actor.role.includes("focal")) return 1.2;
  if (actor.role === "authority") return 1.2;
  if (actor.role === "supporter") return 1.1;
  return 1.0;
}
```

---

### C. Emote visibility 개선

현재 emote는 의미는 있지만 작다. 첫 5초 테스트에서는 놓치기 쉽다.

수정:

- emote 기본 지속시간을 최소 1800ms 이상으로 유지
- emote pop scale을 `0.4 → 1.2` 정도로 더 선명하게
- fear/grief/forgiveness 색과 형태를 더 구분
- grief는 단일 물방울보다 “고개 숙임 + 물방울” 조합이 좋다

단, emote가 사건의 주인공이 되면 안 된다. 행동 이후의 반응으로 보여야 한다.

---

### D. Facing change 강화

facing change가 너무 미세하면 crowd reaction이 안 보인다.

수정:

- facing change 직후 300~500ms 정도 작은 head-turn pop 또는 blink를 줄 수 있다.
- 별도 event type 추가 없이 actor state에 `lastFacedAt` 같은 ephemeral render state를 둘 수 있다.
- 이것은 debug overlay가 아니라 visual feedback이다.

금지:

- 시선선
- 화살표
- relation line

---

## 5.2 Timeline staging cleanup

파일:

```text
scripts/visual/build_event_playbacks.py
```

이 cleanup은 새 event type 추가 없이 기존 8종만 사용한다.

### C01_t15 — authority_pressure

현재도 가장 강하다. 최소 수정.

수정 목표:

```text
guard approach → Stop. → focal fear → focal retreat
```

수정 제안:

- guard spawn은 600~800ms 유지
- guard speech는 `Stop.` 유지
- guard 이동은 너무 길게 보이지 않도록 1.2s~4.0s 사이 도착
- focal fear emote는 2.8~3.0s 유지
- focal step_back은 fear 직후 200ms 이내
- agent_03도 함께 후퇴하되, main focal은 agent_09로 유지

권장 timeline:

```text
0ms    focal/witness spawn
600ms  guard spawn
1000ms guard speech: Stop.
1200ms guard move to pressure distance
2400ms witnesses face guard
2800ms agent_09 fear emote
3000ms agent_09 step_back
3200ms agent_03 step_back
4200ms guard reaches pressure distance / hold
```

---

### C02_t25 — saturation_split

가장 중요한 cleanup 대상.

수정 목표:

```text
agent_03 speaks → agent_05 turns away → grief → right group withdraws
```

현재 약점:

- 오른쪽 grief가 독립된 아이콘처럼 보인다.
- 좌측 발화가 오른쪽 반응의 원인으로 충분히 읽히지 않는다.
- gap widening이 약하다.

수정 제안:

1. agent_03 speech를 더 명확히 한다.

```text
text: "I..." 또는 "I did."
```

`I did.`는 story renderer가 아니라 minimal visual speech cue로 허용 가능하다. 너무 설명적이면 `I...` 유지.

2. agent_05 reaction을 더 빠르고 과장한다.

```text
2600ms face right
2800ms step_back 또는 move to x=16
3100ms grief emote
3400ms pose_change: kneeling 또는 bowed 추가 검토
```

`bowed` pose를 새로 추가해도 event type은 추가되지 않는다. 단, 구현 부담이 크면 kneeling 재사용 가능.

3. right witnesses도 뒤따라 물러난다.

```text
3800ms agent_02 move right/up
4000ms agent_08 move right/down
```

4. left group은 speaker를 바라보며 고정한다.

이렇게 해야 “분열”이 단순 배치가 아니라 사건 결과처럼 보인다.

---

### C03_t142 — confession_cluster

수정 목표:

```text
speaker steps in → confession speech → crowd watches → kneeler collapses → supporters move inward
```

수정 제안:

- agent_09 speech는 1.4~1.6s 유지
- crowd_react는 2.2~2.4s 유지
- agent_03 kneel은 2.8~3.0s 유지
- supporters inward move는 3.2~3.4s로 조금 빠르게
- forgiveness emote는 4.0~4.2s 유지하되 더 크게/길게
- 7초 이후 second forgiveness pulse는 불필요하면 제거한다. 5초 테스트에서는 오히려 전체 duration을 늘리는 의미가 약하다.

---

## 5.3 Grammar 업데이트

파일:

```text
docs/visual/PIXEL_EVENT_PLAYBACK_GRAMMAR.md
```

추가할 섹션:

```md
## Readability Cleanup Rules

- 첫 5초 안에 trigger, primary reaction, visible aftermath가 모두 보여야 한다.
- reaction은 emote 하나로 끝내지 않는다. facing/move/pose 중 최소 하나가 동반되어야 한다.
- group split scene은 양쪽 actor가 모두 움직여야 한다. 한쪽만 말하고 한쪽만 emote하면 인과가 약하다.
- crowd scene은 crowd_react 이후 supporter move 또는 kneel이 1초 안에 따라와야 한다.
- visual emphasis는 role-based scale까지만 허용한다. relation line/wave/aura 금지.
```

---

## 5.4 Validator 강화

파일:

```text
scripts/visual/validate_event_playbacks.py
```

현재 validator는 key reaction ≤ 5000ms를 체크한다. 이건 좋지만 충분하지 않다.

추가 권장 규칙:

1. `speech` must appear by 2500ms if playback has speech.
2. first key reaction must appear by 4500ms, not just 5000ms.
3. each playback must have at least one visible motion event before 4000ms.
4. `saturation_split` must include right-side retreat/move after speech.
5. `confession_cluster` must include crowd_react and pose_change before 4000ms.
6. `authority_pressure` must include authority move and focal step_back before 4500ms.

주의:

- 너무 semantic한 판단은 validator에 넣지 않는다.
- validator는 timing regression 방지용이다.
- 시각적 PASS/FAIL은 여전히 Lee/video 검증이 우선이다.

---

## 5.5 Unit test 강화

파일:

```text
tests/test_visual/test_event_playbacks.py
```

추가할 테스트:

```text
1. test_scene_01_has_authority_move_before_focal_retreat
2. test_scene_02_has_speaker_then_grief_then_right_group_withdrawal
3. test_scene_03_has_speech_crowd_react_kneel_supporter_inward_within_5s
4. test_no_new_event_types_introduced
5. test_no_relation_line_or_overlay_events
6. test_all_playbacks_have_visible_motion_before_4s
```

목적:

- 구현자가 다음 세션에서 feature를 늘리지 않고 staging만 고치도록 잠금.
- PEP의 핵심인 trigger → reaction → aftermath 순서를 회귀 방지.

---

## 6. Review 문서 업데이트

파일:

```text
docs/visual/PIXEL_EVENT_PLAYBACK_REVIEW.md
```

다음 내용을 기록한다.

```md
## Lee/Assistant Video Review — PEP MVP

### C01_t15 — authority_pressure
Verdict: PASS-leaning WEAK
Observed:
- Guard approach and Stop speech are visible.
- Focal fear/retreat is visible.
- Witness reaction is subtle.
Reason:
- Scene intent is readable, but pressure could be stronger through staging and emote visibility.

### C02_t25 — saturation_split
Verdict: WEAK
Observed:
- Left/right grouping is visible.
- Speaker and grief reaction exist.
- Causal connection remains weak.
Reason:
- The right-side retreat/split needs stronger visible reaction after the speech trigger.

### C03_t142 — confession_cluster
Verdict: WEAK-PASS
Observed:
- Crowd semicircle and central speech are visible.
- Kneeling and supporter inward movement exist.
- Forgiveness cue is small/subtle.
Reason:
- The scene structure is promising, but reaction needs more emphasis within the first 5 seconds.

## Final Case After PEP MVP

Case: PEP-B+

Decision:
- Continue Pixel Event Playback.
- Do one readability/staging cleanup.
- Do not expand candidates yet.
- Do not return to static Pixel Scene Director.
- Do not fork to storyboard/comic yet.
```

---

## 7. Completion checklist

PEP Readability Cleanup 완료 조건:

```text
1. build_event_playbacks.py timeline cleanup 완료
2. event_playbacks.json 재생성
3. pixel_event_playback.html viewer readability 개선 완료
4. validate_event_playbacks.py 강화
5. test_event_playbacks.py 강화
6. PIXEL_EVENT_PLAYBACK_GRAMMAR.md cleanup rules 추가
7. PIXEL_EVENT_PLAYBACK_REVIEW.md에 PEP-B+ 및 cleanup 기록
8. pytest tests/test_visual/test_event_playbacks.py 통과
9. 기존 PSD/Pixel World/Explorer 파일 0 변경 확인
10. 새 feature 추가 없이 중지
```

---

## 8. Cleanup 이후 분기

### PEP-A 승격 조건

Cleanup 후 영상 또는 5초 테스트에서 다음을 만족하면 PEP-A로 승격한다.

```text
- C01: PASS
- C02: WEAK-PASS 이상
- C03: PASS
- relation line 없이 사건 흐름이 보임
- 포켓몬식 관찰 방향이 명확히 느껴짐
```

PEP-A 다음 작업:

```text
candidate 3개 → 5~7개 확장
```

제약:

- peter_scarcity_baseline only
- 새 anchor 금지
- 새 scenario 금지
- 새 event type 금지
- 새 engine metric 금지
- PEP grammar 그대로 사용

---

### PEP-B 유지 조건

Cleanup 후에도 다음이면 PEP-B 유지.

```text
- 움직임은 있지만 감정적 인과가 약함
- C02가 여전히 애매함
- scene은 보이지만 world/live simulation 감각이 약함
```

PEP-B 다음 작업:

```text
PEP MVP를 partial success로 freeze하고, portfolio asset으로 정리한다.
이후 storyboard/comic panel approach를 별도 설계 doc으로 검토한다.
```

---

### PEP-C 조건

Cleanup 후에도 다음이면 PEP-C.

```text
- 3 scene 모두 캐릭터 테스트처럼 보임
- 사건을 설명하려면 packet panel이 필요함
- 움직임이 있어도 interaction/flow가 안 읽힘
```

PEP-C 다음 작업:

```text
Pixel visual track freeze.
Storyboard/comic panel approach 설계만 작성.
구현은 바로 하지 않는다.
```

---

## 9. 절대 금지

이번 cleanup에서 금지:

```text
- full replay 구현 금지
- timeline scrub 금지
- pathfinding 금지
- player intervention 금지
- playable 구현 금지
- story renderer 재개 금지
- 새 anchor 금지
- 새 scenario 금지
- 새 engine metric 금지
- React / Phaser / PixiJS 도입 금지
- 외부 asset 금지
- relation line / wave / aura / rift 재도입 금지
- visual/explorer.html 수정 금지
- visual/pixel_world_static.html 수정 금지
- visual/pixel_scene.html 수정 금지
```

---

## 10. 다음 세션 실행 프롬프트

```text
WITNESS PEP MVP video review result:
Final Case is PEP-B+.
Direction is validated, but not ready for candidate expansion.
Do exactly one PEP Readability Cleanup.

Goal:
Make the first 5 seconds of each playback more readable through staging, timing, pose/emote visibility, and focused stage composition.
Do not add new product features.
Do not add new anchors, scenarios, engine metrics, event types, replay, timeline scrub, pathfinding, player intervention, React/Phaser/PixiJS, external assets, relation lines, waves, aura, or rift overlays.

Allowed files:
- scripts/visual/build_event_playbacks.py
- data/visual/event_playbacks.json
- visual/pixel_event_playback.html
- scripts/visual/validate_event_playbacks.py
- tests/test_visual/test_event_playbacks.py
- docs/visual/PIXEL_EVENT_PLAYBACK_GRAMMAR.md
- docs/visual/PIXEL_EVENT_PLAYBACK_REVIEW.md

Do:
1. Record PEP-B+ review in PIXEL_EVENT_PLAYBACK_REVIEW.md.
2. Improve pixel_event_playback.html readability:
   - role-based scale 1.15-1.25 for focal/authority/supporter only
   - larger/clearer emotes
   - stronger facing-change feedback without lines
   - minimal scene-specific props/floor focus, no overlays
3. Improve timelines in build_event_playbacks.py:
   - C01: stronger guard approach → fear → retreat within 4.5s
   - C02: stronger speech → right turn-away → grief → right group withdrawal within 5s
   - C03: faster kneel/supporter inward/forgiveness reaction within 5s
4. Regenerate event_playbacks.json.
5. Strengthen validate_event_playbacks.py and tests:
   - first key reaction ≤ 4500ms
   - speech ≤ 2500ms
   - visible motion before 4000ms
   - scene-specific trigger → reaction order tests
6. Update GRAMMAR.md with readability cleanup rules.
7. Run:
   python scripts/visual/build_event_playbacks.py
   python scripts/visual/validate_event_playbacks.py data/visual/event_playbacks.json
   pytest tests/test_visual/test_event_playbacks.py
8. Stop. Do not expand candidates yet.

After cleanup, Lee will run another 5-second test.
If C01 PASS, C02 WEAK-PASS+, C03 PASS, then promote to PEP-A and expand to 5-7 candidates.
Otherwise freeze PEP as partial success and consider storyboard/comic approach.
```

---

## 11. 넓은 로드맵

```text
Now: PEP-B+ readability cleanup
↓
If improved: PEP-A candidate expansion within peter_scarcity_baseline
↓
If candidate expansion holds: portfolio demo asset / internal demo script update
↓
Only after that: consider Phaser/Tiled or richer sprite assets
```

Phaser/Tiled는 지금 도입하지 않는다. 현재 문제는 엔진 부족이 아니라 staging/readability다. Canvas primitive로 5초 가설을 먼저 통과시킨 뒤에야 엔진 교체를 검토한다.
