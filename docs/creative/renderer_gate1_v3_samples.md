# Renderer Gate 1 v3 — 5 Sample Before/After (Cycle 2 patches applied)

**Date**: 2026-04-29
**Source**: Cycle 2 (Patch A + B + C) applied to `scripts/story/render_story_ko.py`
**Cycle 1 baseline**: `RENDERER_DIAGNOSIS_GATE1_V2_BUNDLE.md` §2 (5 sample)
**Lee 평가 양식**: `RENDERER_GATE1_V3_RESULTS.md`

---

## 0. Cycle 2 변경 요약

| Patch | 변경 | Stock phrase 차단 |
|---|---|---|
| A1 | TRANSITION_TO_OUTCOME flat → outcome-conditional dict | "그리고 그 모든 결은 결국 한 모양으로 굳어 갔다" → MIXED only |
| A2 | TRANSITION_TO_AFTEREFFECT flat → outcome-conditional dict | "며칠이 지난 뒤, 사건이 끝난 자리에는 무언가가 남아 있었다" → SAT only |
| A3 | _aftereffect authority_residue 단일 문장 → outcome × probe pool | "권위의 시선도 거두어지지 않았다" → SAT pool 1/3 |
| B3 | shame_residue 마무리도 outcome별 분기 | SAT/REC/MIXED/PARTIAL/LOW_ACTIVITY 각각 다른 결 |
| C  | LOW_ACTIVITY 전용 _render_narrative_low_activity() + _render_summary_low_activity() | "큰 사건은 없었다 / 평소처럼 흘러갔다" 패턴 → "부재의 긴장" 5 stage |

---

## 1. Sample 1 — P6 MIXED scarcity (good 유지 확인)

### Before (Cycle 1)
> ...그리고 그 모든 결은 결국 한 모양으로 굳어 갔다.
>
> 갈라진 자리는 좁혀지지 않았다. ... 그 자리가 비워지고 며칠이 지나, 사건의 마지막 글자가 닫혀도, 거리는 그것을 완전히 잊지 못했다.
>
> 의심의 흔적은 옅게라도 거리 위에 머물렀다. ... 권위의 시선도 거두어지지 않았다. 시선이 닿는 자리에는 평소보다 느린 호흡이 깔렸다. ... 가장 무거웠던 자리들은 그 무게를 내려놓지 못했다. 시간이 그곳만 비켜 흘러간 듯, 같은 침묵이 며칠을 이어졌다.

### After (Cycle 2)
> ...한 사건의 끝이 두 자리에서 다르게 닫혀 가고 있었다.
>
> 갈라진 자리는 좁혀지지 않았다. ... 그 자리가 비워지고 며칠이 지나, 사건의 마지막 글자가 닫혀도, 거리는 그것을 완전히 잊지 못했다.
>
> 의심의 흔적은 옅게라도 거리 위에 머물렀다. ... **권위의 시선은 그대로였다. 그러나 그 시선 아래에서 두 자리는 다른 자세로 머물렀다.** ... **가장 무거웠던 자리들 중 어떤 곳은 풀렸고, 어떤 곳은 그대로였다. 두 자리가 같은 거리에 머물렀지만, 같은 결의 시간을 살지 않았다.**

### Cycle 2 변화점
- "한 모양으로 굳어 갔다" → MIXED-specific "한 사건의 끝이 두 자리에서 다르게 닫혀 가고 있었다" (대비 강화)
- authority residue → MIXED-specific "두 자리는 다른 자세로 머물렀다" (회복 vs 굳음 대비 명시)
- shame residue 마무리 → MIXED-specific "어떤 곳은 풀렸고, 어떤 곳은 그대로였다" (분열의 잔향)

→ 길이: 1253자 → 1335자. cohort split 강조 더 강해짐.

---

## 2. Sample 2 — Scarcity Trilogy modal (Act I/II 차별화 확인)

### Before (Cycle 1)
- Act I (SAT): "회복의 길은 끝내 열리지 않았다. ... 어떤 자리는 며칠이 지난 뒤에야 미세하게 움직였다. 며칠이 지난 뒤, 사건이 끝난 자리에는 무언가가 남아 있었다."
- Act II (SAT): "그리고 그 모든 결은 결국 한 모양으로 굳어 갔다. 회복의 길은 끝내 열리지 않았다. ... 굳었지만 완전히 잠든 것은 아니었다. 며칠이 지난 뒤, 사건이 끝난 자리에는 무언가가 남아 있었다."
- Act III (REC): "그리고 그 모든 결은 결국 한 모양으로 굳어 갔다. 어느 순간, 무거움이 더 이상 자라지 않았다."

### After (Cycle 2)
- Act I (SAT): "**흐름이 멈춘 자리에서 다음을 묻는 사람은 없었다.** 회복의 길은 끝내 열리지 않았다. ... 어떤 자리는 며칠이 지난 뒤에야 미세하게 움직였다. 며칠이 지난 뒤, 사건이 끝난 자리에는 무언가가 남아 있었다."
- Act II (SAT): "**흐름이 멈춘 자리에서 다음을 묻는 사람은 없었다.** 회복의 길은 끝내 열리지 않았다. ... 굳었지만 완전히 잠든 것은 아니었다. **그 침묵이 길어질수록, 거리는 그 침묵의 일부가 되어 갔다.** ... **권위의 무게는 며칠이 지나도 같은 자리에 그대로였다. 그 무게가 사라진다는 신호는 어디에서도 오지 않았다.**"
- Act III (REC): "**거리의 결이 다시 평소를 향해 옮겨 가고 있었다.** ... 그러나 풀린 어깨에서도 어떤 자세는 남아 있었다. **풀린 어깨가 다시 굽지 않을지를 누구도 묻지 않았다. 다만 그 어깨를 따라 거리가 함께 폈다.** **권위는 자리를 떠나지 않았다. 다만 그 자리에서 거리를 바라보는 결이 한 박자 부드러워졌다.**"

### Cycle 2 변화점
- Act I/II 둘 다 SAT지만 세부 잔향이 다름 — Act II는 "침묵의 일부가 되어 갔다" + "권위의 무게는 그대로" (더 깊은 굳음)
- Act III는 REC-specific 결말 — "거리가 함께 폈다" / "권위 시선이 부드러워졌다"
- "한 모양으로 굳어 갔다" 사라짐 (Act II/III에서 모두 제거)

### 한계 (Cycle 2 미해결)
- Act I/II opening transition slot은 같은 hash로 같은 문장 ("흐름이 멈춘 자리에서 다음을 묻는 사람은 없었다") — pool 3 → 5 확장 필요. **Cycle 3 후보**.

---

## 3. Sample 3 — P9 SAT scarcity (report-like 탈출 시도)

### Before (Cycle 1)
> ...그 갈림의 끝은 한 점에서 모이지 않았다.
>
> 더 이상 올라갈 수 없는 곳까지 무거움이 차올랐다. ... 며칠이 지난 뒤, 사건이 끝난 자리에는 무언가가 남아 있었다.
>
> 권위의 시선도 거두어지지 않았다. 시선이 닿는 자리에는 평소보다 느린 호흡이 깔렸다. 가장 무거웠던 자리들은 그 무게를 내려놓지 못했다.

### After (Cycle 2)
> ...**그 자리에서 시간은 더 이상 앞으로 나아가지 않았다.**
>
> 더 이상 올라갈 수 없는 곳까지 무거움이 차올랐다. ... 며칠이 지난 뒤, 사건이 끝난 자리에는 무언가가 남아 있었다.
>
> **권위의 무게는 며칠이 지나도 같은 자리에 그대로였다. 그 무게가 사라진다는 신호는 어디에서도 오지 않았다.** 가장 무거웠던 자리들은 그 무게를 내려놓지 못했다.

### Cycle 2 변화점
- "그 갈림의 끝은 한 점에서 모이지 않았다" (PARTIAL 톤) → "그 자리에서 시간은 더 이상 앞으로 나아가지 않았다" (SAT 톤, 정지 강조)
- authority residue → "권위의 무게는 며칠이 지나도 같은 자리에 그대로였다" (보고서 톤 → 잔류감 강화)

### Lee가 v2에서 지적한 "saturation 압박이 문장 리듬으로 안 옴" 부분
- v3에서 SAT-specific 문장들이 짧고 닫힘 ("나아가지 않았다", "그대로였다", "오지 않았다")
- "거리의 공기 변화"라는 일반화 → 시간/무게의 정지로 구체화
- 다만 _initial_tension / _pressure_arc 단계는 변경 없음 — 이 부분 deeper rhythm tuning은 Cycle 3 후보

---

## 4. Sample 4 — P10 REC accusation (scenario tone 확보 시도)

### Before (Cycle 1)
> ...그리고 그 모든 결은 결국 한 모양으로 굳어 갔다.
>
> 어느 순간, 무거움이 더 이상 자라지 않았다. ... 다음 날의 아침이 밝았을 때, 거리는 평소의 결로 돌아간 듯 보였지만 어딘가는 달라져 있었다.
>
> 거리는 천천히 다시 평소의 모양으로 돌아갔다.

### After (Cycle 2)
> ...**거리의 결이 다시 평소를 향해 옮겨 가고 있었다.**
>
> 어느 순간, 무거움이 더 이상 자라지 않았다. ... 다음 날의 아침이 밝았을 때, 거리는 평소의 결로 돌아간 듯 보였지만 어딘가는 달라져 있었다.
>
> 거리는 천천히 다시 평소의 모양으로 돌아갔다.

### Cycle 2 변화점
- "한 모양으로 굳어 갔다" (MIXED tone) → "거리의 결이 다시 평소를 향해 옮겨 가고 있었다" (REC tone, 호흡이 열림)
- 마무리 transition은 REC pool 사용 (이전과 동일 selection이지만 의도된 REC 톤)

### Lee가 v2에서 지적한 "accusation만의 날카로움 약함" 부분
- v3에서도 accusation-specific sharpness는 명시적으로 추가되지 않음
- 현재 cross-scenario REC differentiation은 SCENARIO_RECOVERY_POOLS["accusation"]에서만 작동 (이미 Cycle 1 자율 cycle #2에서 적용됨)
- accusation의 *initial tension* (한 사람이 제자를 가리켰다) 외에 mid-arc / outcome에서 accusation tone은 부족
- **Cycle 3 후보**: scenario × outcome 조합별 더 깊은 톤 분기 (현재 cross-scenario REC만 / SAT/MIXED는 미구현)

---

## 5. Sample 5 — P_PV_09 LOW_ACTIVITY (bad 탈출, 전용 branch)

### Before (Cycle 1) — 529자
> 특별한 일이 없는 날이었다. 사람들의 발걸음은 일상의 무게로 흘렀고, 거리에는 익숙한 소리만 남았다. 어디선가 작은 움직임이 있었다 해도, 그것은 곧 평소의 결로 돌아갔다. 권위의 시선은 한쪽 끝에서 모든 것을 지켜보고 있었다. 그 공기가 깊어지기 전, 거리에 작은 사건이 떨어졌다.
>
> 큰 사건은 없었다. 다만 작은 마찰들이 거리를 따라 가볍게 움직였고, 그 외에는 아무것도 멈추거나 시작되지 않았다. 말은 줄어들었다. ...
>
> 사람들은 별다른 동요 없이 머물렀다. 사건은 그들 사이로 지나갔지만, 깊게 박히지는 않았다. 거리는 평소의 결을 유지하고 있었다.
>
> 그리고 그 모든 결은 결국 한 모양으로 굳어 갔다.
>
> 큰 변화는 없었다. 사건이라 부를 만한 일도 없이, 시간은 흘러갔다. ...
>
> 거리는 천천히 다시 평소의 모양으로 돌아갔다.

### After (Cycle 2) — 409자, 5 stage 부재의 긴장
> 특별한 일이 없는 날이었다. 사람들의 발걸음은 일상의 무게로 흘렀고, 거리에는 익숙한 소리만 남았다. 어디선가 작은 움직임이 있었다 해도, 그것은 곧 평소의 결로 돌아갔다. 권위의 시선은 한쪽 끝에서 모든 것을 지켜보고 있었다. **누군가 무엇인가를 말하려다 입을 다물었다. 두어 사람의 시선이 같은 자리에 짧게 머물렀다가 흩어졌다.**
>
> **소문은 한 자리에서만 돌았고, 옆 자리로 넘어가지 못했다. 그 이유를 묻는 사람도 없었다.**
>
> **사람들은 모두 자기 자리에 있었지만, 어디에도 모이지 않았다. 거리 위의 작은 흔들림은 누구의 결도 흔들지 못했다.**
>
> **권위는 거기 있었지만, 보아야 할 것을 보지 않았다. 시선은 한 박자 늦게도 따라오지 않았다.**
>
> **그것은 끝내 사건이 되지 못했다. 그러나 그렇기 때문에 거리에는 다른 종류의 무게가 깔렸다.**

### Cycle 2 변화점 (Lee 의도 검증)

| Lee 요소 | Cycle 1 | Cycle 2 |
|---|---|---|
| 작은 징후 2-3개 | "큰 사건은 없었다" (부재 강조) | **"누군가 말하려다 입을 다물었다 / 두어 사람의 시선이 같은 자리에 짧게 머물렀다가 흩어졌다"** |
| 확산 안 되는 rumor | (없음) | **"소문은 한 자리에서만 돌았고, 옆 자리로 넘어가지 못했다"** |
| 반응 안 하는 crowd | "거리는 평소의 결을 유지하고 있었다" (일반화) | **"사람들은 모두 자기 자리에 있었지만, 어디에도 모이지 않았다"** |
| 무심한 authority | "권위의 시선은 한쪽 끝에서 모든 것을 지켜보고 있었다" (일반 opening) | **"권위는 거기 있었지만, 보아야 할 것을 보지 않았다"** |
| 사건 못 됨 tension | "큰 변화는 없었다. 사건이라 부를 만한 일도 없이" (부재의 사실 진술) | **"그것은 끝내 사건이 되지 못했다. 그러나 그렇기 때문에 거리에는 다른 종류의 무게가 깔렸다"** (부재의 의미) |

→ 길이는 짧아졌지만 (529 → 409자) 5 요소가 모두 명시적으로 등장. "아무 일 없음"이 아니라 "사건이 되지 못한 무엇"으로 처리됨.

---

## 6. 종합 비교

### 6.1 Lee Gate 1 v2 약점 5개 → Cycle 2 처리 상태

| Lee 약점 (v2) | Cycle 2 처리 |
|---|---|
| 반복 stock phrase 5/5 | **MIXED 1/5만 유지, 다른 outcome은 outcome-specific 변환** ✓ |
| outcome별 tension curve 미구분 | **Patch B (transition + authority + shame all outcome-conditional)** 부분 처리 |
| LOW_ACTIVITY 전용 branch 부재 | **Patch C 신설 5 stage** ✓ |
| Trilogy Act I/II 톤 차이 부족 | **Act II 권위 잔향 + 침묵의 일부 차별화** 부분 처리 (opening은 동일 hash 한계) |
| accusation 날카로움 부족 | **미해결 (Cycle 3 후보)** |

### 6.2 Cycle 2 PASS 여부 (Lee 정의 기준)

| 기준 | 결과 |
|---|---|
| 최소 3/5 good | Lee 평가 대기 (Gate 1 v3 양식 참조) |
| LOW_ACTIVITY가 bad 탈출 | Cycle 2 작업 완료, Lee 평가 대기 |
| P9 SAT가 report-like 탈출 | Patch B 적용됨, Lee 평가 대기 |
| P10 REC accusation이 scenario tone 확보 | 부분 적용, Lee 평가 대기 |
| Trilogy Act I/II 차별화 | Act II 권위 잔향만 차별화, opening 동일 — Lee 평가 대기 |

---

## 7. 작업 외 상태

### 7.1 회귀 테스트
- `pytest tests/test_story` — **119/119 PASS**
- `pytest -m "not slow and not archived"` — 1618 PASS, 14 skipped, **1 pre-existing failure** (test_engine/test_integrity:test_no_person_hardcoding_in_engine — engine/story/selector.py 파일 존재로 인한 violation, J-Beta 작업의 untracked 새 파일, Cycle 2와 무관)

### 7.2 변경 파일
- `scripts/story/render_story_ko.py` (608 → ~830 lines): Patch A + B + C
- `docs/story/generated/P6_narrative_ko.txt`, `P6_summary_ko.txt`
- `docs/story/generated/P9_narrative_ko.txt`, `P9_summary_ko.txt`
- `docs/story/generated/P10_narrative_ko.txt`, `P10_summary_ko.txt`
- `docs/story/generated/P_PV_09_narrative_ko.txt`, `P_PV_09_summary_ko.txt`
- `outputs/creative_demo/scarcity_trilogy_modal.txt`

### 7.3 변경 *없음*
- `engine/story/selector.py`, `engine/story/anchor_library.py`, 기타 engine/
- `scripts/story/extract_story_features.py`, `scripts/story/build_narrative_ir.py`
- IR schema, feature extraction
- 기타 96 baseline 및 Branch C narrative (재생성 가능하나 Cycle 2 5-sample 검증 외 범위)

---

## 8. 다음 단계 (Lee 입력 후)

1. Lee가 `RENDERER_GATE1_V3_RESULTS.md`에 5 sample 평가 입력
2. 4/5 PASS 기준 충족 → creative asset pack 진행 (Type B-2 경우 B + Renderer PASS 조합)
3. PARTIAL → Cycle 3 plan 작성 (scene-level agency / named motif / narrator distance)
4. FAIL → renderer core repair plan
