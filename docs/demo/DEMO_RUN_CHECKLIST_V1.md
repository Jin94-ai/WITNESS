# WITNESS Demo Run Checklist v1

**Date**: 2026-04-30
**Source**: `docs/plan.md` Phase 6
**Purpose**: 시연 시작 5-10분 전 *자체 점검*. 모든 항목 ✅ 확인 후 시연 시작.

---

## 0. 사용 방법

각 항목 옆 `[ ]`을 `[x]`로 표시하며 진행. 한 항목이라도 ❌이면 *시연 시작 금지*.

---

## A. 데이터 파일 존재 확인

```bash
ls -la data/visual/
```

다음 4개 파일 모두 존재해야 함:

- [ ] `dot_observer_data.json` (~824 KB)
- [ ] `dot_observer_data_triple.json` (~824 KB)
- [ ] `dot_observer_cross_seed_triple.json` (~275 KB)
- [ ] `dot_observer_data_vangogh.json` (~595 KB)

**누락 시**: `INTERNAL_DEMO_PACKAGE_V1.md` §3.2 export 명령 재실행.

---

## B. HTTP server 실행

프로젝트 루트에서:

```bash
python -m http.server 8000
```

- [ ] 서버 시작 메시지 (`Serving HTTP on 0.0.0.0 port 8000`) 확인
- [ ] 포트 충돌 시 다른 port 사용 (예: 8001)

**검증**:
```bash
curl -sI http://localhost:8000/visual/explorer.html | head -1
```
→ `HTTP/1.0 200 OK`

- [ ] HTTP 200 응답 확인

---

## C. explorer.html 접속

브라우저에서:
```
http://localhost:8000/visual/explorer.html
```

- [ ] 페이지 로드 (5초 이내)
- [ ] 상단 toolbar 표시 (Anchor dropdown + View toggle)
- [ ] 좌측 main view 영역 표시
- [ ] 우측 panel 영역 표시 (Candidates / Selected packet / Story / Tick state)

**JavaScript 에러 확인** (브라우저 console):
- [ ] F12 → Console 탭 → 에러 0건

---

## D. 화면 1: peter_baseline 검증

데모 시작 시점:
- Anchor dropdown: `peter_scarcity_baseline`
- View toggle: Single-run

확인:
- [ ] 화면 좌측 SVG canvas에 도트 12개 + group zone 3개 + world tint 표시
- [ ] Timeline-bar에 marker들 표시 (yellow noise + score-3 5개 빨간 marker visible)
- [ ] 우측 candidate panel에 8개 카드 (filter ON: SR 5 / OO 0 / LH 3)
- [ ] Tick state panel에 mood / blame / suspicion / vigilance 표시

**기능 점검**:
- [ ] Slider drag → tick 이동 작동
- [ ] Play 버튼 클릭 → tick 자동 진행 (10 ticks/sec)
- [ ] Pause 버튼 클릭 → 정지
- [ ] Timeline-bar의 빨간 marker 클릭 → 해당 tick으로 jump (toast 메시지 1.4s)
- [ ] Candidate 카드 (예: `C03_t142`) 클릭 → tick 142 jump + 파란 range overlay

---

## E. 화면 2: peter_triple cross-seed 검증

전환:
- Anchor dropdown → `peter_scarcity_triple`
- View toggle → Cross-seed

확인:
- [ ] Cross-seed 버튼이 enabled (이전엔 baseline에서 disabled였을 것)
- [ ] 상단 banner: "Outcomes: REC 3 · PARTIAL 1 · SAT 1"
- [ ] 5 seed rows 표시 (각 row에 lane + markers + candidate strip)
- [ ] 각 row 우측 outcome tag (REC 녹색 / PARTIAL 회색 / SAT 빨강)

**기능 점검**:
- [ ] Seed 0 row 클릭 → selected 강조 + candidate panel 갱신 (8 candidates)
- [ ] Seed 3 row 클릭 → SAT outcome candidate panel 갱신 (9 candidates)
- [ ] Toast 메시지 표시 (`→ seed 3 선택 (outcome=SAT, ...)`)

---

## F. 화면 3: vangogh 검증

전환:
- Anchor dropdown → `vangogh_sacred_baseline`

확인:
- [ ] View 자동으로 Single-run (vangogh는 cross-seed 없음)
- [ ] Cross-seed 버튼 자동 disabled
- [ ] Timeline-bar 거의 yellow only (score-2/3 marker 0)
- [ ] Group lane 거의 정적 (mode change 1)
- [ ] Candidate panel 6 카드 (모두 회색 = low_activity_hold)

**기능 점검**:
- [ ] Filter row "story_ready" 클릭 → "필터된 후보 없음" 표시
- [ ] Filter "story_ready" 다시 클릭 (활성화) → 6개 다시 표시
- [ ] Candidate (예: `E02_t100_public_denial`) 클릭 → tick 100 jump + packet 갱신

---

## G. Candidate panel + Packet panel 통합 점검

화면 1 (peter_baseline)으로 돌아가서:

- [ ] `C01_t15` 카드 클릭 → packet panel에 6 sections 표시:
  - [ ] ID: C01_t15 · story_ready
  - [ ] LOCATION: tick 15 · range 13-17 (5 ticks 폭)
  - [ ] CLASSIFICATION: type=person · lens=person
  - [ ] WHY SURFACED: rationale 한 문장
  - [ ] SIGNALS: 3 chip (authority_vigilance_spike / cohort_split / agent_state_shift)

- [ ] Story / lens text panel 항상 placeholder 표시:
  > "packet의 rationale + signals만 위에 표시. 별도 story text는 본 v0에 통합 안 됨 — story renderer 재개 금지 조항."

---

## H. Keyboard shortcut (v0.2)

화면 1에서:
- [ ] **← key** 누름 → 1 tick 이전 이동
- [ ] **→ key** 누름 → 1 tick 다음 이동
- [ ] (Slider focus 상태에서 누르면 ignore — 정상)

---

## I. 백업 CLI 도구 사전 실행

별도 터미널에서:

```bash
python examples/demo_observer_story.py --packet C01_t15
```

- [ ] 6-field packet 텍스트 출력 (Korean rationale 포함)

```bash
python examples/demo_observer_story.py --render-story C03_t142
```

- [ ] Person lens narration + Detail table 출력

→ 데모 중 청중 질문 시 *별도 터미널에서 즉시 호출* 가능 상태로 만들어두기.

---

## J. 데모 환경 점검

- [ ] 화면 해상도 1280×800 이상
- [ ] 브라우저 zoom 100%
- [ ] 다른 브라우저 탭 / 알림 정리 (방해 요소 제거)
- [ ] 시연 도중 마우스 잘 보임 (cursor 크기 조정 권장)
- [ ] 음향 / 화면 공유 (원격 시연 시) 사전 테스트

---

## K. 5분 budget 자체 시연

마지막 점검 — *실제로 5분 안에 가능한지*:

1. [ ] 0:00-0:30 도입 (한 줄 소개)
2. [ ] 0:30-2:00 화면 1 (peter_baseline)
3. [ ] 2:00-3:30 화면 2 (peter_triple cross-seed)
4. [ ] 3:30-4:40 화면 3 (vangogh)
5. [ ] 4:40-5:00 마무리

**총 시간 측정** (스톱워치):
- 목표: 5분 (4:30 ~ 5:30 허용)
- 실제: ___분 ___초
- [ ] 5:30 이내 완료

**시간 초과 시**:
- 화면 1/2/3에서 *어느 화면이 길었나* 메모
- DEMO_SCRIPT_V1.md *시간 압축 옵션* (4분 모드) 검토

---

## L. 청중 시나리오 점검

청중이 다음 질문을 *반드시* 묻는다고 가정 (DEMO_SCRIPT_V1.md FAQ 참조):

- [ ] *"story text가 없는 거 같은데?"* → 답변 자신 있게 가능
- [ ] *"vangogh가 너무 조용한데, 흥미로워 보이지 않아."* → 답변 자신 있게 가능
- [ ] *"5 seeds로 통계가 충분한가?"* → 답변 자신 있게 가능
- [ ] *"이걸 누가 쓰는 거야?"* → "Internal tool" 명시 가능
- [ ] *"intervention / what-if는 안 되나?"* → "관찰자 모드 only, fork 결정 대상" 가능

---

## M. 최종 점검

- [ ] *모든* A-L 항목 ✅
- [ ] DEMO_SCRIPT_V1.md cheat sheet 즉시 참조 가능
- [ ] KNOWN_LIMITATIONS_V1.md 머릿속 정리됨
- [ ] *5분 budget 기준* 자기 시연 1회 완료
- [ ] 청중 도착 직전 *마지막 30초 자기 호흡 정리*

---

## 트러블슈팅

### 데이터 파일 누락
**증상**: explorer.html에서 빨간 에러 ("JSON 로드 실패")
**해결**:
```bash
python scripts/visual/export_dot_observer_data.py
python scripts/visual/export_dot_observer_data.py --anchor peter_scarcity_triple --output data/visual/dot_observer_data_triple.json
python scripts/visual/export_cross_seed_visual_data.py --anchor peter_scarcity_triple --seeds 0 1 2 3 4 --output data/visual/dot_observer_cross_seed_triple.json
python scripts/visual/export_dot_observer_data.py --anchor vangogh_sacred_baseline --output data/visual/dot_observer_data_vangogh.json
```

### HTTP server 포트 충돌
**증상**: `OSError: [Errno 48] Address already in use`
**해결**: 다른 port 사용
```bash
python -m http.server 8001
# → http://localhost:8001/visual/explorer.html
```

### Cross-seed 버튼이 disabled (peter_triple 선택 시에도)
**증상**: peter_triple anchor 선택했는데도 cross-seed 버튼 회색
**원인**: `dot_observer_cross_seed_triple.json` 누락 또는 schema 불일치
**해결**: A 항목 다시 export

### Browser console 에러
**증상**: F12 → Console에 빨간 에러 메시지
**해결**:
1. JSON 파일 무결성 확인 (`python -c "import json; json.load(open('data/visual/dot_observer_data.json'))"`)
2. 브라우저 cache 삭제 (Ctrl+Shift+R hard reload)
3. 다른 브라우저로 시도 (Chrome / Firefox)

---

## 한 줄 요약

> **시연 5-10분 전 A-M 13 sections 자체 점검. 모든 항목 ✅ 후 시연 시작. 트러블슈팅 4 케이스 사전 인지.**

---

**Versioning**: v1 (this checklist) — 2026-04-30 Phase 6 시연 전 점검.
