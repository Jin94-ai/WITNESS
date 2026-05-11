# WITNESS — Internal Demo Package v1

**Date**: 2026-04-30
**Source**: `docs/plan.md` Phase 6 + `TEXT_VISUAL_ROLE_REASSESSMENT.md` Case TV-A
**Scope**: **Internal** — public demo 아님. Lee 본인 + 잠재적 이해관계자 1-2명 manual 시연.
**기준 entry**: `visual/explorer.html`
**소요 시간**: 5분

---

## 0. 핵심 메시지 (반드시 전달)

> **WITNESS는 텍스트 이야기 생성기가 아니라, 움직이는 세계를 도트 기반으로 관찰하고, 그 안에서 이야기 후보를 발견하는 *world simulation explorer*다.**

이 한 문장이 데모 끝까지 *유일한 anchoring message*. 시연자는 매 화면에서 이 메시지로 *연결*해야 함.

---

## 1. 데모 목적

### 1.1 What this demo IS
- *내부* 프로젝트 점검 도구
- WITNESS 현재 상태를 *5분에 압축*해서 전달
- 시연자(Lee 본인)의 *외부 이해관계자 설명용* 백업 자료

### 1.2 What this demo is NOT
- ❌ Public product demo
- ❌ Story 생성 시연 (story renderer 재개 금지 일관)
- ❌ Playable / interactive prototype
- ❌ Performance / scale benchmark
- ❌ Engine validation / paper-grade evidence

---

## 2. 대상 사용자

### 2.1 Primary
- **Lee 본인**: 프로젝트 현재 상태 *self-check*, 다음 단계 결정 보조
- **시연 환경**: 본인 desktop, 자체 진행 가능

### 2.2 Secondary (manual demo, 시연자 동행 필수)
- 프로젝트 이해관계자 1-2명 (개발자 / 연구자 / 협업자)
- WITNESS 설명을 *말로 보충* 가능한 청중

### 2.3 Out of scope (이 데모 대상 아님)
- 일반 public 사용자 (UI / 안내문 부족)
- AI 비전공 청중 (배경 설명 부족)
- 모바일 / 태블릿 사용자 (desktop 800×500 가정)

---

## 3. 실행 준비

### 3.1 데이터 파일 존재 확인 (1회 export 후 영구 보존)

다음 파일이 모두 있어야 함:

| 파일 | 크기 | 용도 |
|---|---|---|
| `data/visual/dot_observer_data.json` | ~824 KB | 화면 1 (peter_baseline) |
| `data/visual/dot_observer_data_triple.json` | ~824 KB | 보조 (peter_triple single-seed) |
| `data/visual/dot_observer_cross_seed_triple.json` | ~275 KB | 화면 2 (peter_triple cross-seed) |
| `data/visual/dot_observer_data_vangogh.json` | ~595 KB | 화면 3 (vangogh) |

### 3.2 데이터 export 명령 (이미 완료된 상태, 재실행 시)

```bash
# 화면 1 — peter_baseline
python scripts/visual/export_dot_observer_data.py
# → data/visual/dot_observer_data.json

# 화면 2 — peter_triple (single + cross-seed 둘 다)
python scripts/visual/export_dot_observer_data.py \
    --anchor peter_scarcity_triple \
    --output data/visual/dot_observer_data_triple.json
python scripts/visual/export_cross_seed_visual_data.py \
    --anchor peter_scarcity_triple --seeds 0 1 2 3 4 \
    --output data/visual/dot_observer_cross_seed_triple.json

# 화면 3 — vangogh
python scripts/visual/export_dot_observer_data.py \
    --anchor vangogh_sacred_baseline \
    --output data/visual/dot_observer_data_vangogh.json
```

### 3.3 explorer.html 실행

```bash
# 프로젝트 루트에서
python -m http.server 8000

# 브라우저 (Chrome / Firefox 권장)
http://localhost:8000/visual/explorer.html
```

### 3.4 데모 환경 권장
- **창 크기**: 1280×800 이상 (Explorer 좌우 layout 필요)
- **브라우저 zoom**: 100% (UI 비율 정상)
- **데모 시작 전**: anchor dropdown = `peter_scarcity_baseline`, view = Single-run, filter 3개 모두 ON 상태로 시작

---

## 4. 5분 데모 전체 흐름

### 시간 budget

| 시간 | 내용 |
|---|---|
| 0:00 - 0:30 | 도입 (한 줄 소개) |
| 0:30 - 2:00 | 화면 1 — peter_scarcity_baseline (격동의 기본) |
| 2:00 - 3:30 | 화면 2 — peter_scarcity_triple cross-seed (운명 분기) |
| 3:30 - 4:40 | 화면 3 — vangogh_sacred_baseline (다른 dynamics) |
| 4:40 - 5:00 | 마무리 |

→ 상세 대본은 `DEMO_SCRIPT_V1.md` 참조.

---

## 5. 반드시 보여줄 3 화면 — 핵심 포인트

### 화면 1: `peter_scarcity_baseline` Single-run

**Explorer 진입 상태**: anchor = baseline (default), view = Single-run (default)

**핵심 포인트** (~1.5분):
1. **Timeline의 5 score-3 빨간 marker** — 즉시 식별 (V2-1 marker noise 완화 효과)
2. **L1 zone 색 변화** (low_activity → partial → saturation → recovery, 12회 mode 변화)
3. **Candidate panel "story_ready 5"** — Q1-Q4 curation 결과
4. **Candidate 카드 클릭 → tick jump + 파란 range overlay** (V2-4)

**메시지**: *"세계가 흐르고, 어디가 중요한지 visual로 보인다. 시스템이 큐레이션한 5개 후보를 1 click으로 순회 가능."*

### 화면 2: `peter_scarcity_triple` Cross-seed

**Explorer 전환**: anchor → `peter_scarcity_triple`, view toggle → Cross-seed

**핵심 포인트** (~1.5분):
1. **Outcome banner**: `REC 3 · PARTIAL 1 · SAT 1` (nonmonotonic finding 즉시 식별)
2. **5 row lane 색 분포**: REC = 녹색 / SAT = 빨강 / PARTIAL = 회색 ending
3. **Score-3 marker 분포 차이** per seed (5/5/1/1/4)
4. **Seed 0 vs Seed 3 비교 클릭** — 같은 config가 정반대 운명

**메시지**: *"같은 anchor가 어떤 운명들을 낳을 수 있는지 — configuration sensitivity. 5 seeds는 통계 증명이 아니라 *시연*."*

### 화면 3: `vangogh_sacred_baseline` Single-run

**Explorer 전환**: anchor → `vangogh_sacred_baseline` (cross-seed 자동 disabled, view → Single-run)

**핵심 포인트** (~1.1분):
1. **Timeline 거의 yellow only** (148 score-1, score-2/3 모두 0) — 격동 anchor와 대비
2. **Group lane 거의 정적** (mode change 1회) — 단조 배경
3. **Candidate panel 6개 모두 회색** (low_activity_hold) — 다른 분류 결과
4. **Active events 다름**: miracle_witnessed, prayer_invitation 등 sacred-specific

**메시지**: *"다른 scenario family는 다른 dynamics. 시스템이 자동 판정 안 함 — 사용자가 분류 정보 보고 판단."*

---

## 6. 백업 CLI 도구 (시연자 보충 설명용)

데모 흐름에 *통합되지 않음*. 청중 질문 / 추가 설명 필요 시 시연자가 별도 터미널에서 호출.

### 6.1 특정 candidate 서사 보충
```bash
python examples/demo_observer_story.py --render-story C03_t142
# 또는
python examples/demo_observer_story.py --render-story C03_t142 --lens person
```
→ `render_candidate_story.py` 결과를 console에 출력. 데모 화면에는 표시 안 됨.

### 6.2 Full packet text
```bash
python examples/demo_observer_story.py --packet C03_t142
```
→ 6-field packet (Basic / Why / Lens / Story potential / Render / Human check) 텍스트.

### 6.3 3-lens 비교
```bash
python examples/demo_observer_story.py --compare-lenses C03_t142
```
→ person / event / world 3-lens narration 비교.

### 6.4 Curated 목록
```bash
python examples/demo_observer_story.py --curated
```
→ Q1-Q4 3-bucket 통합 출력.

→ **사용 원칙**: *데모 흐름에 끼워 넣지 말 것*. 청중 "그 후보가 정확히 무슨 이야기?" 같은 질문 시에만 보조.

---

## 7. 데모 성공 기준

### 7.1 Hard 기준 (반드시 충족)
1. ✅ 5분 안에 3 화면 모두 시연 완료
2. ✅ Explorer가 데모 중 0 에러 (HTTP 200, JS 에러 없음)
3. ✅ 핵심 메시지 한 문장이 *시작과 끝*에 명시됨
4. ✅ 청중이 "WITNESS는 X를 한다"를 한 문장으로 paraphrase 가능

### 7.2 Soft 기준 (충족 시 success)
1. ✅ 청중이 *왜 visual이 필요한지* 묻지 않음 (자연스럽게 이해)
2. ✅ Story text 부재가 *질문으로 나오지 않음* (또는 시연자가 자신 있게 답변)
3. ✅ vangogh의 조용함이 *"안 흥미롭다"*가 아닌 *"다른 dynamics"*로 받아들여짐
4. ✅ Cross-seed nonmonotonic finding이 *"5 seeds 통계 부족"* 비판으로 무력화 안 됨

### 7.3 데모 실패 신호
- ❌ 청중이 *"그래서 이게 무슨 이야기를 만든다는 거야?"* 5분 끝까지 묻고 있음
- ❌ Explorer 화면에서 데이터 로드 실패 / 클릭 무반응
- ❌ 시연자가 *"story text가 없어서..."* 변명조로 들어감

→ 실패 시: `INTERNAL_DEMO_PACKAGE_REVIEW.md` 의 Case D-B/C/D로 회귀.

---

## 8. 데모 흐름 다이어그램

```
[0:00-0:30 도입]
   "WITNESS = world simulation explorer"
        ↓
[0:30-2:00 화면 1]
   peter_baseline: 격동의 기본
   timeline 5 빨간 marker → candidate 5개 → click jump
        ↓
[2:00-3:30 화면 2]
   peter_triple cross-seed: 운명 분기
   banner "REC 3 / PARTIAL 1 / SAT 1" → 5 row 색 분포
        ↓
[3:30-4:40 화면 3]
   vangogh: 다른 dynamics
   yellow only timeline → 모두 회색 candidate → "조용한 흐름"
        ↓
[4:40-5:00 마무리]
   3 layer 역할 정리: Visual / Packet / Story
   "Visual + Packet으로 충분, Story는 선택"
```

---

## 9. 사용 권장 흐름

### 9.1 시연자 사전 준비 (5분 전)
1. `DEMO_RUN_CHECKLIST_V1.md` 항목 모두 ✅
2. 브라우저 1280×800 이상, zoom 100%
3. Explorer 미리 로드 (peter_baseline 화면)
4. CLI 백업 도구 *별도 터미널*에서 미리 한 번 실행해서 응답 확인

### 9.2 시연자 데모 중 자세
- *제 시간 안에* 화면 전환 (각 ~1.5분)
- 청중 질문은 *마지막 30초 이후* 받기 (흐름 끊김 방지)
- "story text가 없는데?" 질문 → "Visual + packet으로 충분, 별도 CLI 도구 있음" (자신 있게)
- "vangogh가 너무 조용한데?" 질문 → "*다른 dynamics 시연*. 시스템은 좋다 나쁘다 자동 판정 안 함" (자신 있게)

### 9.3 시연자 데모 후
- 청중 reaction 메모
- 5분 budget 실제 측정 (예상 vs 실제)
- 막힌 지점 / 자연스럽지 못한 전환 기록
- → `INTERNAL_DEMO_PACKAGE_REVIEW.md`에 반영 (별도 directive 시)

---

## 10. ABSOLUTE 원칙 + Lee directive 준수

| 원칙 | 준수 |
|---|:---:|
| Rule #1 (no person hardcoding) | ✅ visual layer person hardcoding 0 |
| Rule #6 (engine API preservation) | ✅ engine 무수정 |
| 관찰기 ≠ 평가기 | ✅ candidate 자동 quality verdict 0 |
| Lee §6 (renderer 재개 / 3D / React 등 금지) | ✅ 모두 미수행 |
| Lee §6 (시스템은 좋은 이야기/나쁜 이야기 자동 판정 안 함) | ✅ 데모에서 명시 |
| Lee §"public demo packaging 금지" | ✅ Internal scope 명시 |

---

## 11. 한 줄 요약

> **WITNESS Internal Demo Package v1 = 5분 / 3 화면 (peter_baseline → peter_triple cross-seed → vangogh) / explorer.html 단일 entry / story text 없이 Visual+Packet만으로 설명. 핵심 메시지: world simulation explorer.**

---

## 12. 동행 문서

- `DEMO_SCRIPT_V1.md` — 시간/화면/클릭/말 5분 대본
- `KNOWN_LIMITATIONS_V1.md` — 8 한계 명시
- `DEMO_RUN_CHECKLIST_V1.md` — 시연 전 자체 체크
- `INTERNAL_DEMO_PACKAGE_REVIEW.md` — 6 평가 + Case D 판정

---

**Versioning**: v1 (this package) — 2026-04-30 Phase 6 진행.
