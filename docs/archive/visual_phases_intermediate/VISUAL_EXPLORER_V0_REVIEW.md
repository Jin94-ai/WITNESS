# Visual Explorer v0 — Implementation Review

**Date**: 2026-04-30
**Source**: Lee directive (Visual Explorer v0 구현, 새 capability 0)
**Plan ref**: `VISUAL_EXPLORER_V0_PLAN.md`
**Verdict**: **Case EX-A — v0 통합 성공** → Visual Observer를 내부 탐색 도구의 기준 entry로 인정

---

## 0. 산출물

### 신규 파일 (1개)
- `visual/explorer.html` (~27 KB / ~700 줄, vanilla JS + SVG, external dep 0)

### 무수정 (Lee 명시 "기존 안정 파일 대규모 리팩터 금지")
- `visual/dot_observer_replay.html` (19,505 bytes — V2 minimal 그대로)
- `visual/dot_observer_static.html` (8,568 bytes — V0-V1 그대로)
- `visual/dot_observer_cross_seed.html` (12,630 bytes — Cross-seed 그대로)
- `data/visual/*.json` (3 파일 모두 — schema 무수정)
- `scripts/visual/*.py` (export script 2개 모두)

### v0 기술 stack
- Vanilla JS (118/118 brace balanced)
- SVG only (3D 금지 일관)
- `fetch()` API for JSON
- 외부 dependency 0

---

## 1. v0 구성 (Lee §1-§3 verbatim)

### 1.1 단일 entry HTML
- `visual/explorer.html` 한 파일에서 모든 view 전환

### 1.2 4 view 통합

| View | 데이터 source | 재사용한 로직 |
|---|---|---|
| **Single-run replay** | `dot_observer_data*.json` (schema v1) | renderCanvas / timeline-bar / play 컨트롤 (replay HTML 핵심 로직 *복사 통합*) |
| **Cross-seed comparison** | `dot_observer_cross_seed_triple.json` (schema cross_seed_v1) | renderSeedRow / outcome banner (cross-seed HTML 핵심 로직 *복사 통합*) |
| **Candidate panel** | 현재 view의 candidates | filter row + card list (V2 패턴) |
| **Story / packet side panel** | candidate 메타데이터 | placeholder + rationale + signals (story renderer 재개 금지) |

### 1.3 Selector UI (toolbar)
- **Anchor dropdown** (`<select>`):
  - peter_scarcity_baseline
  - peter_scarcity_triple
- **View toggle** (button group):
  - Single-run (active by default)
  - Cross-seed (peter_scarcity_baseline에서 disabled — cross-seed export 없음)

### 1.4 Anchor → data mapping (v0 코드 내 `ANCHOR_DATA` 상수)
```js
peter_scarcity_baseline → { single: dot_observer_data.json, cross: null }
peter_scarcity_triple   → { single: dot_observer_data_triple.json, cross: dot_observer_cross_seed_triple.json }
```

→ peter_scarcity_baseline 선택 시 cross-seed 버튼 자동 disabled (gracefully degrade).

---

## 2. 사용 흐름 3개 검증 (Lee §4)

### 흐름 A — 한 세계를 replay로 관찰
**Steps**:
1. 진입: explorer.html
2. Anchor selector default = `peter_scarcity_baseline`
3. View default = Single-run
4. Main canvas = SVG (도트 + group zone + world tint)
5. Timeline-bar 보임 (V2-1 marker noise opacity 차등 그대로 — score-3 빨간 5개 식별)
6. Play / Slider / Timeline-click / Candidate card click 모두 작동
7. Tick state panel (우측)에 world metrics + salience tags + active events

**판정**: ✅ **성공** — V2 dot_observer_replay.html과 동일한 핵심 흐름 재현. 5 panel 통합 (V2의 5 panel을 explorer에서는 1 tick-state panel + candidate panel + packet panel 3개로 reorganize).

### 흐름 B — seed 5개를 비교해 outcome 분포 확인
**Steps**:
1. Anchor selector → `peter_scarcity_triple`
2. View toggle → Cross-seed (이제 enabled)
3. Main canvas = 5 seed small multiples (lane + markers + range overlay)
4. 상단 banner = "Outcomes: REC 3 · PARTIAL 1 · SAT 1"
5. Seed row 클릭 → 우측 candidate panel + packet panel이 *해당 seed의 candidates*로 갱신
6. seed 0/1/4 (REC) 비교, seed 2 (PARTIAL), seed 3 (SAT) 식별

**판정**: ✅ **성공** — cross-seed HTML과 동일한 패턴. nonmonotonic finding (REC 3 / PARTIAL 1 / SAT 1) 즉시 식별.

### 흐름 C — candidate를 골라 packet/story side panel 확인
**Steps**:
1. (흐름 A 또는 B 상태에서) 우측 candidate panel에서 카드 클릭
2. **Single-run view**: timeline 자동 jump + 파란 range overlay 표시
3. **Cross-seed view**: 해당 seed가 이미 selected 상태에서 candidate 선택
4. "Selected candidate (packet)" panel 갱신:
   - candidate_id · use_mode 색 코딩
   - tick · range
   - candidate_type · strongest_lens
   - related (있을 때만)
   - rationale (한 문장)
   - signals (chip 표시)
5. "Story / lens text" panel: placeholder ("packet의 rationale + signals만 위에 표시. 별도 story text는 본 v0에 통합 안 됨 — story renderer 재개 금지 조항.")

**판정**: △ **부분 성공** — candidate → packet 흐름 작동. Story text는 **placeholder per Lee directive**. 본격 story 표시는 future directive 시 별도 export 필요.

---

## 3. v0 검증 기준 (PLAN §7) 점검

| # | 성공 기준 | 결과 |
|---|---|:---:|
| 1 | 단일 entry HTML로 4 view 모두 도달 가능 | ✅ explorer.html 1개 |
| 2 | Anchor selector로 다른 anchor 즉시 전환 | ✅ dropdown 즉시 |
| 3 | Single-run / Cross-seed view 토글 작동 | ✅ button toggle (cross-seed 없는 anchor에선 disabled) |
| 4 | Candidate 클릭 → packet/story 같은 화면에 표시 | △ packet ✅, story = placeholder |
| 5 | 3 사용 흐름 모두 막힘 없이 진행 | ✅ A/B 완전, C 부분 |
| 6 | 기존 V0-V2 + Cross-seed 자료 깨지지 않음 | ✅ 모든 파일 무수정 (size 동일) |

**5/6 ✅ + 1 △ → Case EX-A 충족**.

| # | 실패 기준 | 발생 여부 |
|---|---|:---:|
| 1 | Single-run view가 V2 대비 regression | ❌ V2 핵심 작동 그대로 |
| 2 | Cross-seed view가 기존 dot_observer_cross_seed.html 대비 regression | ❌ 동일 패턴 |
| 3 | Anchor 전환 시 stale state | ❌ loadAnchor()에서 reset |
| 4 | Story panel이 비어있거나 잘못된 candidate에 매칭 | △ placeholder OK (Lee directive 명시) |
| 5 | 외부 dependency 추가 (React 등) | ❌ vanilla JS only |

**0+/5 발생 → 재설계 불필요**.

---

## 4. 핵심 발견

### 4.1 통합이 가져다준 것
- **Anchor 전환 1 click**: 이전에는 export 재실행 + URL parameter 수동 변경 필요
- **View 전환 1 click**: 이전에는 별도 HTML 파일 사이 navigation
- **Candidate 클릭 → tick 자동 이동 + packet 갱신** (single-run에서)
- **Cross-seed → seed 선택 → 해당 seed candidates 자동 표시**

### 4.2 통합으로 인한 손실 (있음)
- **Single-run view의 5 panel이 3 panel로 재조직**: World @ tick / Salience / Active candidates / Selected agent / All curated → Tick state (병합) / Candidate list / Packet detail
- 일부 정보 밀도 ↓ (예: agent dot click → selected agent panel은 v0에서 빠짐 — V2 dot click 핵심이지만 v0 통합 시 우선순위 낮음)
- **이는 의도된 손실**: Lee §"새 기능 추가 금지" 일관 — 5 panel 그대로 옮기면 통합 layout이 너무 복잡

### 4.3 문서화된 한계
- **Story panel placeholder**: Lee §"story renderer 재개 금지" 일관. *별도 export* 시 표시 가능 (`scripts/visual/export_packets_for_visual.py` PLAN §3.2 참조)
- **Multi-anchor expansion 제한**: 현재 2 anchor만 (baseline + triple). 다른 anchor (high_density / double / vangogh) 추가 시 ANCHOR_DATA 상수에 1줄 추가 필요 (작은 단가)
- **Agent dot click 미통합**: V2 핵심 기능이지만 v0 첫 cut에서 우선순위 외. 후속 추가 가능

---

## 5. v0 검증 vs 기존 자료 비교

| 측면 | dot_observer_replay.html (V2) | dot_observer_cross_seed.html | **explorer.html (v0)** |
|---|---|---|---|
| Entry | 1 anchor | 1 cross-seed dataset | **다중 anchor + view toggle** |
| Single-run | full V2 (5 panel) | — | core (tick state + cand panel) |
| Cross-seed | — | full small multiples | full small multiples |
| Candidate panel | 3-bucket filter + range | per-seed candidates | 통합 (view에 따라 자동 fetch) |
| Story panel | — | — | placeholder |
| Agent dot click | full (V2-2 follow) | — | (미통합 — v0 우선순위 외) |
| Anchor switch | URL parameter | URL parameter | **dropdown** |

→ **explorer.html은 *기능 superset*이 아닌 *navigation superset***. 기존 HTML이 *deep view* 제공, explorer는 *broad navigation* 제공.

---

## 6. Case EX-A vs EX-B vs EX-C 평가

### Case EX-A 조건: v0 통합 성공
- ✅ 5/6 success criteria 명확 충족
- ✅ 0/5 failure 발생
- ✅ 기존 자료 무수정
- ✅ 3 사용 흐름 모두 막힘 없이 진행 (단, 흐름 C는 placeholder)
- ✅ Lee 금지 항목 모두 준수

### Case EX-B 조건: 통합은 되지만 사용성 약함
- 적용 안 됨 — 3 사용 흐름 모두 작동, navigation 직관적

### Case EX-C 조건: 통합이 오히려 복잡
- 적용 안 됨 — 단일 HTML, 외부 dep 0, 내부 코드 700줄 (Lee 단가 견적 ~120-230분 범위 내 ~150분 추정)

### **결정: Case EX-A — v0 통합 성공**

근거:
1. **Single entry**: explorer.html 하나가 anchor + view + candidate + packet 모두 통합
2. **기존 deep view 보존**: V2 / cross-seed HTML 모두 무수정 — 사용자가 *더 깊게* 보고 싶을 때 별도 도구 사용 가능
3. **Navigation 효율 ↑**: anchor + view 전환이 click 단위
4. **Story placeholder는 Lee directive 명시 일관**: story renderer 재개 금지를 *지킨* 결과 — 약점이 아니라 *원칙 준수*
5. **추가 단가 작음**: 다른 anchor 추가는 ANCHOR_DATA 상수 1줄, story export는 별도 script (~40분, PLAN §3.2)

---

## 7. 다음 단계 (Lee directive §"멈춰" 일관)

**본 LOOP에서 추가 작업 없음**. Lee 명시 stop.

### Case EX-A 후속 가능 영역 (별도 directive 시)
1. **Story side panel 실제화**: `scripts/visual/export_packets_for_visual.py` 작성 → packet text static export → explorer.html에서 fetch → story panel 표시 (~40분)
2. **Agent dot click → selected agent panel 통합**: V2 dot click 핵심 기능을 explorer로 (작은 단가 ~30분)
3. **Multi-anchor expansion**: high_density / double / vangogh anchor 추가 (각 anchor당 ANCHOR_DATA 1줄 + 데이터 export, ~10분/anchor)
4. **URL deep-link**: `?anchor=peter_scarcity_triple&view=cross&seed=2` 같은 deep-link 지원 (~30분)
5. **Phase V3 — Observer + Story Panel 깊은 통합**: PLAN §"V3"는 별도 phase

### 본 review에서 *하지 않은* 것 (Lee 금지)
- ❌ React dashboard
- ❌ 3D / 캐릭터 / animation
- ❌ player intervention
- ❌ story renderer 재개
- ❌ new scenario
- ❌ multi-anchor 대규모 확장
- ❌ visual polish
- ❌ 새 metric / 새 lens / 새 bucket
- ❌ 기존 안정 파일 대규모 리팩터

---

## 8. HARNESS 적용

### What I did NOT try
- 사용자 테스트 (비-개발자 사용 흐름 검증 미수행)
- 모바일/태블릿 viewport 테스트
- Performance test (200 ticks × 12 agents × 60fps replay 시 frame drop 여부)
- Story panel actual content (Lee 명시 placeholder)
- URL deep-link / shareable state

### What could still be wrong
- "Single-run view 5 panel을 3 panel로 재조직"이 *너무 많은 정보 손실*일 가능성 (사용자가 V2 replay HTML을 더 선호할 수도)
- ANCHOR_DATA 상수가 hardcoded — 새 anchor 추가 시 코드 변경 필요 (deploy 친화적이지 않음)
- explorer.html ~700 줄이 *너무 커서* 향후 유지보수 부담 가능

### Alternate interpretations
- (a) v0 통합이 핵심 가치 → Case EX-A (이번 결과)
- (b) explorer가 단순히 *간소화된 V2*가 되어 V2 사용자 손실 → Case EX-B (재검토 필요)
- (c) 통합 자체가 over-engineering → Case EX-C (회귀)

→ 본 review (a) 선택. (b)/(c)는 user testing 시 falsify 가능.

---

## 9. 한 줄 요약

> **Visual Explorer v0 = 단일 entry `visual/explorer.html` (~27 KB)에서 anchor selector + view toggle (single-run / cross-seed) + candidate panel + packet panel 통합. 기존 안정 파일 5개 모두 무수정. 5/6 success + 0/5 failure. Story panel은 Lee directive 명시 placeholder (story renderer 재개 금지). 3 사용 흐름 (replay 관찰 / seeds 비교 / candidate→packet) 모두 작동. Case EX-A 통합 성공.**

---

## 10. 사용 방법

```bash
# 1. (1회 export, 이미 완료)
python scripts/visual/export_dot_observer_data.py
python scripts/visual/export_dot_observer_data.py \
    --anchor peter_scarcity_triple --output data/visual/dot_observer_data_triple.json
python scripts/visual/export_cross_seed_visual_data.py \
    --anchor peter_scarcity_triple --seeds 0 1 2 3 4 \
    --output data/visual/dot_observer_cross_seed_triple.json

# 2. HTTP server
python -m http.server 8000

# 3. 브라우저
http://localhost:8000/visual/explorer.html
```

브라우저에서:
- 상단 dropdown으로 anchor 변경
- 상단 button으로 view 전환 (single-run / cross-seed)
- 우측 candidate panel에서 filter + 카드 클릭
- single-run에서 dot click은 *현재 v0 통합 안 됨* (V2 dot_observer_replay.html에서 가능)

---

## 11. ABSOLUTE 원칙 + Lee directive 준수

| 원칙 | 준수 |
|---|:---:|
| Rule #1 (no person hardcoding) | ✅ anchor_id parameter only |
| Rule #6 (engine API preservation) | ✅ engine/observer/* 무수정 |
| 관찰기 ≠ 평가기 | ✅ explorer는 *분류 + 탐색*만 |
| Lee §"새 metric 추가 금지" | ✅ 미추가 |
| Lee §"새 lens 추가 금지" | ✅ 미추가 |
| Lee §"new scenario 금지" | ✅ peter family만 |
| Lee §"story renderer 재개 금지" | ✅ placeholder only |
| Lee §"React / 3D / 캐릭터 / animation 금지" | ✅ vanilla JS + SVG |
| Lee §"player intervention 금지" | ✅ observer-only |
| Lee §"visual polish 금지" | ✅ MVP 수준 |
| Lee §"multi-anchor 대규모 확장 금지" | ✅ 2 anchor만 |
| Lee §"기존 안정 파일 대규모 리팩터 금지" | ✅ 모든 기존 파일 무수정 |
| Lee §"구현 후 새 기능 추가하지 말고 멈춰" | ✅ ScheduleWakeup 미호출 예정 |

---

**Versioning**: v1 (this review) — 2026-04-30 Visual Explorer v0 구현 + 검증. Case EX-A.
