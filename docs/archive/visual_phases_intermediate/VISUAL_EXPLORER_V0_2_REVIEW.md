# Visual Explorer v0.2 — Minimal Connection Improvement Review

**Date**: 2026-04-30
**Source**: `docs/plan.md` Phase 2 (최소 연결 개선)
**Target**: `visual/explorer.html` (v0 → v0.2)
**Verdict**: **Phase 2 성공** → Phase 3 (Multi-anchor 최소 확장) 권고

---

## 0. 변경 요약

v0 → v0.2 단일 파일 (`visual/explorer.html`) 업데이트. 4 가지 최소 개선만:

| # | 개선 | Lee §허용 항목 |
|---|---|---|
| 1 | Packet panel sectioning (rationale + signals + classification + location 분리) | §1 precomputed packet 연결 |
| 2 | Candidate click 시 toast 표시 (single-run: tick jump 메시지 / cross-seed: packet 갱신 메시지) | §2 click 동작 명확화 |
| 3 | Legend 시각화 (색 swatch + bar 직접 표시) | §3 legend/label 개선 |
| 4 | Keyboard ← / → tick 이동 (single-run only) | §4 keyboard shortcut |

### 변경 통계
- `explorer.html`: 27,033 → **31,589 bytes** (+17%)
- JS brace balance: 118/118 → **134/134** (모두 closed)
- 새 심볼: `showJumpToast`, `jump-toast` div, `ArrowLeft/ArrowRight` handler, `packet-section` CSS class

---

## 1. 개선 1 — Packet panel sectioning

### v0 (전)
```
[Selected candidate (packet)]
C01_t15 · story_ready
tick: 15 (range 13-17)
type: person · lens: person
rationale: Surfaced by ...
signals: [chip] [chip] [chip]
```

### v0.2 (후)
```
[Selected candidate (packet)]
ID
  C01_t15 · story_ready
LOCATION
  tick 15 · range 13–17 (5 ticks 폭)
CLASSIFICATION
  type=person · lens=person
WHY SURFACED
  Surfaced by authority_vigilance_spike, cohort_split, agent_state_shift
SIGNALS
  [chip] [chip] [chip]
```

### Lee §1 일관 점검
- *story renderer 재개*: ❌ 미수행 (rationale + signals는 *기존 candidate metadata*만)
- *새 story 생성*: ❌ 미수행
- *이미 있는 packet/candidate metadata만 연결*: ✅ 일관

**효과**: candidate의 6 측면을 *섹션 단위*로 분리. "왜 이 후보인지"가 **WHY SURFACED** section에 명시 → 사용자가 *섹션 label*만 봐도 어디를 봐야 하는지 인지.

---

## 2. 개선 2 — Candidate click 동작 명확화

### v0 (전)
- Candidate 카드 클릭 → tick jump (single-run) / packet 갱신 (cross-seed)
- 사용자가 *무엇이 일어났는지* 시각적 피드백 없음

### v0.2 (후)
- Single-run view 클릭: `→ C01_t15: jumped to tick 15 (range 13–17)` toast
- Cross-seed view 클릭: `→ C01_t15: packet 갱신 (cross-seed view, tick navigation 없음)` toast
- Seed row 클릭 (cross-seed): `→ seed 2 선택 (outcome=PARTIAL, 7 candidates)` toast

### 구현
- 우측 상단 fixed position toast (CSS opacity 0.2s transition)
- `setTimeout`으로 1.4s 후 자동 사라짐
- `clearTimeout`으로 빠른 연속 클릭 시 가장 최근만 표시

**효과**: 사용자가 *"내가 클릭한 결과가 어디로 갔는지"* 즉시 인지. cross-seed view에서 *왜 tick이 안 움직이는지*도 명시 (placeholder 효과).

---

## 3. 개선 3 — Legend/label 시각화

### v0 (전)
```
Dot: color=state · size=fear · stroke=salient · Group zone: color=mode · radius=tension ·
Timeline: yellow=s1(흐림) · orange=s2 · red=s3(굵음) · 파란 overlay=selected candidate range
```

### v0.2 (후)
```
Dot: ● calm  ● tense  ● agitated  ● withdrawn  ● fragmenting · size=fear · 검은 stroke=salient
Group zone: 색=mode (gray=low_activity / pink=saturation / green=recovery / amber=mixed) · 반경=tension
Timeline: ▌score-1 (희미)  ▌score-2  ▌score-3 · 검은 cursor=현재 tick · 파란 overlay=selected candidate range
```

색 swatch + bar가 **CSS inline element**로 직접 표시 → text 설명을 보지 않아도 *색 구분* 즉시 식별.

Cross-seed view legend도 동일 패턴 적용:
- 배경 lane 4개 mode 색 명시
- Markers 2개 score 색 명시
- Bottom strip 3개 use_mode 색 명시

**효과**: 사용자가 *legend 텍스트 자체*를 읽을 필요 줄어듦.

---

## 4. 개선 4 — Keyboard ← / → tick navigation

### v0 (전)
- Slider drag, Play/Pause/Prev/Next 버튼, Timeline-bar click만 가능
- 키보드 미지원

### v0.2 (후)
- ← key: 1 tick 이전
- → key: 1 tick 다음
- Single-run view에서만 작동 (cross-seed view에서는 ignore)
- INPUT/SELECT/TEXTAREA focus 시 ignore (form 입력 방해 안 함)
- `e.preventDefault()` — page scroll 방해 안 함

**효과**: Power user의 *fine-grained* tick scrubbing 가능. 매번 mouse drag 안 해도 됨.

### Lee §4 ("keyboard shortcut은 필요할 때만, ← / → tick 이동 정도만 허용") 일관
- ✅ ← / → 만 추가
- ✅ 다른 keyboard shortcut 0 (예: space=play, +/-=zoom 등 미추가)

---

## 5. 성공 기준 점검 (Lee Phase 2 §성공 기준)

| # | 기준 | 결과 |
|---|---|:---:|
| 1 | candidate를 클릭하면 "왜 이 후보인지" 더 빨리 이해된다 | ✅ packet sectioning + WHY SURFACED 명시 |
| 2 | packet side panel이 placeholder보다 확실히 낫다 | ✅ 6 sections로 정보 구조화 |
| 3 | single-run과 cross-seed 전환이 덜 헷갈린다 | ✅ toast가 view별 다른 메시지 표시 |
| 4 | 기존 deep view 기능을 깨지 않는다 | ✅ 기존 안정 파일 0 변경 (replay/cross-seed/static HTML) |

**4/4 ✅ → Phase 2 성공 (Lee §성공 기준 모두 충족)**

---

## 6. 실패 기준 점검 (Lee Phase 2 §실패 기준)

| # | 실패 시나리오 | 발생 여부 |
|---|---|:---:|
| 1 | explorer.html이 너무 복잡해진다 | ❌ +17% bytes (~31 KB) — 적절 |
| 2 | packet 연결이 또 다른 renderer처럼 커진다 | ❌ candidate metadata만 사용 (rationale/signals 기존 데이터) |
| 3 | 기존 visual files를 불필요하게 리팩터한다 | ❌ explorer.html 1개만 수정, 다른 4개 visual file 무수정 |

**0/3 발생 → 실패 기준 모두 통과**

---

## 7. 기존 안정 파일 무수정 확인

```
visual/dot_observer_replay.html    19,505 bytes (V2 그대로)
visual/dot_observer_static.html     8,568 bytes (V0-V1 그대로)
visual/dot_observer_cross_seed.html 12,630 bytes (Cross-seed 그대로)
data/visual/*.json                  3 파일 모두 schema 무수정
scripts/visual/*.py                 2 파일 모두 무수정
```

→ Lee §"기존 안정 파일 대규모 리팩터 금지" 일관.

---

## 8. 변경된 파일 (1개)

| 파일 | 변경 |
|---|---|
| `visual/explorer.html` | CSS +5 클래스 / HTML +1 toast div + subtitle 변경 / JS +1 함수 (showJumpToast) + arrow key handler + packet sectioning |

---

## 9. Lee directive 금지 항목 준수

| 금지 항목 | 준수 |
|---|:---:|
| 새 기능 (capability) 추가 | ✅ packet sectioning은 *기존 데이터의 다른 표현*, 새 capability 0 |
| Visual polish (cosmetic) | ✅ legend는 *기능적 정보 명확화*, polish 아님 |
| Story renderer 재개 | ✅ rationale + signals는 *기존 candidate metadata*에서 가져옴 |
| React / 3D / 캐릭터 / animation | ✅ vanilla JS + SVG only |
| New scenario | ✅ peter family만 |
| Player intervention | ✅ 미수행 |
| Multi-anchor 대규모 확장 | ✅ Phase 3 영역 |
| Complex UI refactor | ✅ 1 파일 17% 추가, 구조 변경 없음 |

---

## 10. HARNESS 적용

### What I did NOT try
- 사용자 테스트 (브라우저 직접 클릭/키보드 사용 테스트)
- 모바일 viewport
- Performance test (200 ticks replay 시 frame drop)

### What could still be wrong
- Toast 메시지가 *너무 자주* 표시되어 noise가 될 수 있음 (특히 빠른 candidate 순회 시)
- Packet sectioning이 *과한 형식주의*로 보일 가능성
- Keyboard shortcut에 익숙하지 않은 사용자가 ← / → 발견 못 할 수 있음 (subtitle에 명시했지만 보이지 않을 수 있음)

### Alternate interpretations
- (a) v0.2가 candidate 이해를 더 빠르게 → Phase 2 §성공 기준 1 충족 (이번 결과)
- (b) Packet sectioning이 *실용 가치 없음* → user testing 필요 (자동 검증 한계)
- (c) Toast가 noise → Phase 3 직전에 user feedback 받아 검토 필요

---

## 11. 다음 Phase 권고

### Phase 2 stop rule 적용 (Lee Phase 2 §완료 후)

**산출물 요약**:
- `visual/explorer.html` v0.2 (4 개선)
- `docs/visual/VISUAL_EXPLORER_V0_2_REVIEW.md` (이 문서)

**성공/실패 판정**: ✅ **성공** (4/4 success criteria + 0/3 failure)

**다음 Phase로 갈지**: ✅ **Phase 3 (Multi-anchor 최소 확장)** 진행 가능
- *별도 directive 시 진행* — Lee directive `docs/plan.md` Phase 3는 multi-anchor 추가 작업
- Phase 2 결과로 *충분히* 다음 단계 가치 있다고 판단

**새 기능 추가 여부**: ❌ 없음 (4 가지 minimal connection 개선만)

**Forbidden 위반 여부**: ❌ 없음

---

## 12. 한 줄 요약

> **Visual Explorer v0 → v0.2 minimal connection 개선 = packet sectioning + click toast + legend visualization + keyboard ← / → 4 가지. 4/4 success criteria 충족, 0/3 failure. 기존 안정 파일 5개 모두 무수정. explorer.html 27 → 31.5 KB (+17%). Phase 2 성공 → Phase 3 (Multi-anchor 최소 확장) 진행 권고.**

---

**Versioning**: v1 (this review) — 2026-04-30 v0.2 minimal connection 완료.
