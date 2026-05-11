# WITNESS — 5-Minute Verbal Demo Script

> 화면 없이 *말로만* 5분 안에 시스템을 설명. 화상 면접 / 카페 미팅 / 전화 인터뷰에서 활용.

---

## 0. 핵심 원칙

- 시청자가 *화면을 보지 못함* — 모든 표현이 *말로 이미지를 그릴 수 있어야* 함.
- "도트 12개 × 3 그룹 × 200 tick"처럼 *숫자 + 구체적 단위*로 그림 그리기.
- 말 시작 30초 안에 *프로젝트가 뭔지*를 전달. 그 다음 디테일.
- 5분 → 1,200-1,500 단어 (한국어 기준 ~1,000-1,200자/분 × 5분).
- 면접관이 중간에 끊고 질문하기를 기대 — script 그대로 외우지 말고 *블록 단위*로 스킵 가능하게.
- 끝에는 "한계 + 다음 단계"로 *솔직함의 신호*를 남김.

---

## 1. 시간 분배

```
0:00 ─ 0:30   한 줄 소개 + 30초 elevator
0:30 ─ 1:30   Layer 1 — Simulation Engine (1분)
1:30 ─ 2:30   Layer 2-3 — Observer / Candidate Pipeline (1분)
2:30 ─ 3:30   Layer 4 — Visual Explorer (1분)
3:30 ─ 4:30   Cross-seed comparison + observer-not-evaluator (1분)
4:30 ─ 5:00   한계와 다음 단계 (30초)
```

---

## 2. 한국어 script

### 0:00 ─ 0:30 — 한 줄 소개

> *"제가 'WITNESS'라는 개인 연구 프로젝트를 직접 설계·구현했는데, 한 줄로 말씀드리면 *Agent-based World Simulation Explorer*입니다. 즉, 다중 에이전트 시뮬레이션 엔진이랑, 그 결과를 도트 기반으로 시각화해서 흥미로운 순간을 자동으로 찾아주는 visual explorer가 결합된 시스템입니다. 4-layer 아키텍처에 2,640개 이상 unit test가 있고, 시각화 레이어는 vanilla JS + SVG로 외부 의존성이 0입니다."*

---

### 0:30 ─ 1:30 — Layer 1: Simulation Engine

> *"엔진부터 말씀드릴게요. 시뮬레이션 안에는 12개 에이전트가 있고, 각자 fear, hope, shame, drives 같은 독립적인 state vector를 가지고 시간에 따라 변합니다. 이벤트는 hazard rate Poisson process로 발생하는데, 식으로 말씀드리면 P(event) = 1 - exp(-h·dt)입니다. 누적된 state가 임계치를 넘으면 trigger가 fire되는 구조입니다.*
>
> *재미있는 부분은 — 동일한 엔진 코드가 세 가지 시나리오를 돌립니다. 베드로의 수난 서사, 반 고흐의 회화 활동, 탈레랑의 정치 협상. 엔진 layer에는 'engine 내부에 도메인 코드 절대 금지'라는 강한 architectural constraint가 있고, grep으로 자동 검증합니다. 'grep -r peter engine/' 명령이 0건을 반환해야 합니다.*
>
> *시나리오 추가는 content/[name]/ 폴더에 데이터만 떨어뜨리면 됩니다 — 엔진 수정은 0건. 이게 cross-scenario universality 검증의 핵심입니다."*

---

### 1:30 ─ 2:30 — Layer 2-3: Observer / Candidate Pipeline

> *"엔진이 매 tick마다 snapshot을 내보내면, observer layer가 그걸 받아서 8가지 salience tag로 분류합니다. 예를 들면 cohort split — 그룹이 두 개로 갈라지는 순간, saturation lock — 어떤 상태가 임계치에서 멈추는 순간, agent state shift — 특정 에이전트의 상태가 급격히 변하는 순간 같은 거예요.*
>
> *그 다음에 candidate extraction / curation pipeline이 있는데, 이게 흥미로운 순간들을 찾아서 *3가지 use mode*로 분류합니다. 'suitable for narrative review' (서사로 검토할 만한), 'observation only' (관찰용으로만 보관), 'low-activity hold' (활동 적은 후보, 보존). 핵심은 — 시스템이 자동으로 'good story / bad story' 판정을 안 합니다. 'observer-not-evaluator' 디자인 원칙이라고 부릅니다.*
>
> *왜 이렇게 했냐면 — 시스템이 quality 판정을 자동화하면 결정 로직이 black-box가 됩니다. 시스템은 'where to look'을 카테고리화만 하고, 'why it matters'는 panel에 rationale + signals로 외부화합니다. 사용자가 disagree하고 override 할 수 있어요."*

---

### 2:30 ─ 3:30 — Layer 4: Visual Explorer

> *"마지막 레이어는 visual explorer인데, 이게 가장 시각적으로 보여드리고 싶은 부분이에요. self-contained HTML 파일 한 개에 vanilla JS + SVG, 외부 의존성 0입니다. ~700 줄짜리 단일 파일.*
>
> *화면을 그려보시면 — 800×500 SVG 캔버스 위에 도트 12개랑 그룹 zone 3개가 떠 있어요. 도트 색은 agent state, 도트 크기는 intensity, zone 색은 group mode, 배경 tint는 world mood — 이렇게 multi-channel color encoding으로 정보를 운반합니다.*
>
> *그 아래에 200 tick짜리 timeline bar가 있어요. timeline에는 salience marker가 점점이 찍혀 있는데, 노란색은 low salience, 주황색은 mid, 빨간색 굵은 marker는 high salience moment입니다. timeline을 슬라이더로 scrub하면 도트랑 zone이 색이랑 크기가 바뀌면서 시뮬레이션이 시간에 따라 흐르는 게 보입니다.*
>
> *오른쪽에는 candidate panel이 있고, candidate를 클릭하면 timeline cursor가 그 시점으로 점프하면서 packet panel에 'why surfaced' rationale + signals + classification이 표시됩니다.*
>
> *왜 도트인지 — 12 agent가 매 tick 동시에 변하는데 캐릭터 그래픽을 쓰면 시청자 시선이 'who is this character'에 끌려갑니다. 이 도구의 주인공은 *시스템 자체*라서 도트가 적합합니다. 의식적인 디자인 선택입니다."*

---

### 3:30 ─ 4:30 — Cross-seed comparison

> *"가장 중요한 view를 마지막에 말씀드릴게요. cross-seed view입니다.*
>
> *동일한 configuration을 5개 seed로 돌립니다. 화면에는 5개의 가로 행이 떠 있고, 각 행이 한 seed의 trajectory를 mini-timeline으로 보여줍니다. 화면 위쪽에는 outcome distribution banner가 있어요 — 예를 들어 'REC 3 · PARTIAL 1 · SAT 1'. 이게 무슨 뜻이냐면, 똑같은 input config인데 seed 5개 중 3개는 회복 (REC), 1개는 부분 회복 (PARTIAL), 1개는 saturation에 갇힘 (SAT). 세 가지 다른 outcome class가 동시에 나옵니다.*
>
> *왜 이게 중요하냐면 — single seed로 시뮬레이션 돌리고 'configuration sensitivity 있다 / 없다'를 결론짓는 패턴이 너무 흔합니다. cross-seed view는 이 함정을 *시각으로* 막는 도구입니다. 한 화면에 distribution이 보이니까 'sensitivity가 있긴 한데 어느 방향인지 single seed로는 모른다'는 게 강제로 보입니다.*
>
> *제가 이 시스템에 만들어 놓은 8-rule self-evaluation framework가 있는데, 8번 규칙이 'sensitivity claim을 하려면 5+ seed ensemble 필수'입니다. cross-seed view가 그 규칙의 실천 도구입니다 — anti-bias engineering이 슬로건이 아니라 시각으로 강제됩니다."*

---

### 4:30 ─ 5:00 — 한계와 다음 단계

> *"한계도 솔직히 말씀드릴게요. 첫째, contemplative 시나리오 (반 고흐 같은 정적인 동역학)에서는 8 salience tag로 잘 surface가 안 됩니다. 시스템이 가짜 salience를 만들지 않고 'low-activity'로 정직하게 분류하지만, 이것 자체가 한계입니다. 둘째, 모바일 / 반응형 미지원, desktop only. 셋째, story renderer는 의도적으로 freeze.*
>
> *다음은 두 갈래로 보고 있어요. 단기로는 multi-anchor cross-seed 확장이랑 sacred-dynamics 인코딩 튜닝, 장기로는 observable world engine 확장이나 narrative renderer 통합 중에서 *사용자 reviewer feedback을 보고* 결정할 예정입니다. 새 기능 추가보다 현 시스템의 사용성 검증이 먼저라는 디시플린입니다.*
>
> *— 여기까지가 5분 데모입니다. 화면이 있으면 cross-seed view 하나만 보여드려도 'configuration sensitivity가 시각으로 보인다'는 핵심 메시지가 한 번에 전달돼요."*

---

## 3. English script

### 0:00 ─ 0:30 — One-liner

> *"WITNESS is a personal research project I designed and built — in one line, an Agent-based World Simulation Explorer. It pairs a multi-agent simulation engine with a dot-based visual explorer that auto-detects interesting moments. Four-layer architecture, 2,640-plus unit tests, visualization is vanilla JS + SVG with zero external dependencies."*

---

### 0:30 ─ 1:30 — Simulation Engine

> *"The engine — twelve agents, each maintaining its own state vector — fear, hope, shame, drives, beliefs — evolving over time. Events fire through a hazard-rate Poisson process: P(event) equals 1 minus exp of negative h dt. State accumulates, triggers fire when thresholds cross.*
>
> *The interesting part is that the same engine code runs three different scenarios — Peter's Passion narrative, Van Gogh's creative practice, Talleyrand's political negotiation. The engine layer prohibits domain hardcoding, and that prohibition is grep-verified — running 'grep -r peter engine/' must return zero hits.*
>
> *Adding a scenario means dropping data into 'content slash name slash'. Engine modification is exactly zero. That's the cross-scenario universality validation."*

---

### 1:30 ─ 2:30 — Observer / Candidate Pipeline

> *"As the engine produces snapshots per tick, an observer layer tags them with eight salience signal types — cohort split when a group divides, saturation lock when a state plateaus at threshold, agent state shift for sharp individual changes, and so on.*
>
> *Then a candidate extraction and curation pipeline sorts those moments into three use modes — suitable for narrative review, observation only, low-activity hold. The crucial part — the system never auto-judges 'good story versus bad story'. We call this the observer-not-evaluator design principle.*
>
> *Why? Because automating quality judgment turns the decision logic into a black box. The system categorizes 'where to look' and externalizes 'why it matters' as rationale and signals in a side panel. The user can disagree and override the classification."*

---

### 2:30 ─ 3:30 — Visual Explorer

> *"The fourth layer is the visual explorer — and this is the most visual part. Self-contained HTML — vanilla JS plus SVG, zero dependencies, about 700 lines, single file.*
>
> *Picture an 800 by 500 SVG canvas with twelve dots and three group zones. Dot fill color encodes agent state; dot size encodes intensity; zone fill encodes group mode; background tint encodes world mood — multi-channel color encoding all running simultaneously.*
>
> *Below the canvas, a 200-tick timeline bar with salience markers — dim yellow for low, orange for mid, bold red for high salience moments. Drag the slider, and dots and zones change color and size as the simulation flows in time.*
>
> *On the right, a candidate panel. Click a candidate, and the timeline cursor jumps to that tick while the side panel updates with the rationale, signals, and classification.*
>
> *Why dots? With twelve agents updating every tick, character graphics would draw attention to 'who is this character'. The subject of this tool is the system itself, not the avatars. So dots — a deliberate design choice."*

---

### 3:30 ─ 4:30 — Cross-seed comparison

> *"And the most important view, last. Cross-seed comparison.*
>
> *Run the same configuration with five different seeds. The screen shows five horizontal lanes — each lane is one seed's trajectory as a mini-timeline. At the top, an outcome distribution banner — for example, 'REC three, PARTIAL one, SAT one'. Same input config, but five seeds produce three distinct outcome classes — three recoveries, one partial, one saturation lock.*
>
> *Why this matters — single-seed runs claiming 'configuration sensitivity exists' or 'doesn't exist' is a common pattern. The cross-seed view blocks that trap visually — the distribution is right there on screen, so 'sensitivity exists but a single seed can't tell you direction' is forced into view.*
>
> *I built an 8-rule self-evaluation framework for the system, and rule eight mandates 5-plus seed ensemble for any sensitivity claim. The cross-seed view is the operational practice of that rule — anti-bias engineering as visual enforcement, not a slogan."*

---

### 4:30 ─ 5:00 — Limitations and next steps

> *"Honest about the limitations. First, contemplative scenarios — Van Gogh-style quiet dynamics — don't surface well through the eight salience tags. The system classifies them as 'low-activity' rather than auto-tuning to fake salience, but that's a real limitation. Second, desktop only — no mobile or responsive support. Third, the story renderer is intentionally frozen.*
>
> *Next steps split short-term and long-term. Short-term — multi-anchor cross-seed expansion and tuning salience encoding for sacred dynamics. Long-term — extending into an observable world engine or integrating a narrative renderer, but that decision waits on usability feedback from the current system. The discipline is reviewer feedback before new features.*
>
> *— That's the 5-minute demo. With a screen, the cross-seed view alone delivers the main message — configuration sensitivity made visual — in one glance."*

---

## 4. 90-second compressed version

### 한국어 (~90s)

> *"'WITNESS'는 다중 에이전트 시뮬레이션 + 비주얼 익스플로러입니다. 12 에이전트가 hazard-driven Poisson process로 상호작용하면서 상태가 변하고, 동일 엔진 코드가 3 시나리오 (베드로, 반 고흐, 탈레랑)를 content-only 차이로 돌립니다. 엔진 layer에 도메인 하드코딩 금지가 grep으로 자동 검증돼요.*
>
> *Observer layer가 8 salience tag로 흥미로운 순간을 자동 surface하고, candidate를 3 use mode로 분류만 합니다 — quality 판정은 사람이 (observer-not-evaluator).*
>
> *Visual explorer는 vanilla JS + SVG, 0 dependency, ~700 줄 단일 HTML. 200 tick × 12 agent를 도트랑 zone으로 표시. cross-seed view에서는 5 seeds × 200 ticks를 small-multiples로 배치해서 'REC 3 / PARTIAL 1 / SAT 1' 같은 outcome 분포를 직접 보여줍니다 — single-seed bias를 시각으로 차단.*
>
> *2,640+ unit test, 8-rule anti-bias framework. 한계는 sacred dynamics 인코딩 부족 + desktop only. internal exploration 단계로 의도적으로 코드 공개 보류 중입니다."*

### English (~90s)

> *"WITNESS is a multi-agent simulation paired with a visual explorer. Twelve agents interact via hazard-driven Poisson process; the same engine code runs three scenarios — Peter, Van Gogh, Talleyrand — with content-only differences. No-domain-hardcoding rule is grep-verified.*
>
> *An observer layer auto-surfaces interesting moments through 8 salience tags and sorts candidates into 3 use modes — categorize, never auto-judge quality, observer-not-evaluator design.*
>
> *Visual explorer is vanilla JS plus SVG, zero dependencies, ~700 lines, single HTML file. Dots and zones render 200 ticks × 12 agents. The cross-seed view places 5 seeds × 200 ticks in small-multiples and shows outcome distribution like 'REC 3 / PARTIAL 1 / SAT 1' directly — blocks single-seed bias visually.*
>
> *2,640-plus unit tests, 8-rule anti-bias framework. Limitations — sacred dynamics encoding gap, desktop only. Intentionally held back from public release at internal-exploration stage."*

---

## 5. 면접관 follow-up 대응 (script 중간에 끊겼을 때)

### "잠깐, [구체적 질문]을 더 자세히 말씀해주실 수 있나요?"

가장 자주 받는 질문 → 어느 시간 블록에서 deeper dive할 수 있는지:

| 면접관 질문 | Script 블록 | 추가 디테일 (참조) |
|---|---|---|
| "왜 도트인가요?" | 2:30 블록 | [INTERVIEW_STORY_BANK.md](INTERVIEW_STORY_BANK.md) Q5 |
| "엔진이 정확히 뭘 하나요?" | 0:30 블록 | [DEMO_GUIDE_FOR_PORTFOLIO.md](DEMO_GUIDE_FOR_PORTFOLIO.md) Q4 |
| "왜 React를 안 썼나요?" | 2:30 블록 | [DEMO_GUIDE_FOR_PORTFOLIO.md](DEMO_GUIDE_FOR_PORTFOLIO.md) Q2 |
| "1000 agent까지 scaling 가능한가요?" | 4:30 블록 (한계) | [DEMO_GUIDE_FOR_PORTFOLIO.md](DEMO_GUIDE_FOR_PORTFOLIO.md) Q3 |
| "LLM은 어디에 쓰였나요?" | 1:30 블록 | [INTERVIEW_STORY_BANK.md](INTERVIEW_STORY_BANK.md) Q6 |
| "테스트는 어떻게 했나요?" | 어디서든 | [INTERVIEW_STORY_BANK.md](INTERVIEW_STORY_BANK.md) Q7 |

---

## 6. 면접 디테일 팁 (말로 demo 시 특화)

### Do
- ✅ *숫자를 발음할 때 천천히* — "12 agents", "200 ticks", "5 seeds" 강조
- ✅ *그림을 말로 그리기* — "800×500 캔버스 위에 도트 12개", "5개 가로 행"
- ✅ *기술 용어 + 일상 용어 페어링* — "hazard-rate Poisson process — 즉, 시간이 갈수록 사건 발생 확률이 누적되는 모델"
- ✅ *마지막에 한계 언급* — 솔직함의 신호. 면접관 질문 받으려고 의도적으로 deep dive 하나는 남겨두기

### Don't
- ❌ "그냥 만들었어요 / 자동으로 됐어요"
- ❌ "AI 이야기 생성기" / "story generator"
- ❌ Lee 언급
- ❌ HARNESS H1-H8 verbatim
- ❌ 한 블록을 너무 길게 — 1분 안에 끊기
- ❌ 기술 디테일에 빠져서 *왜* 그렇게 했는지 안 말함

---

## 7. ABSOLUTE 원칙 + Lee directive 준수

| 원칙 | 준수 |
|---|:---:|
| Lee §"코드 수정 금지" | ✅ |
| Lee §"public release 금지" | ✅ — verbal demo script만, 화면 캡처 안 함 |
| Lee §"내부 로그 삭제하지 말 것" | ✅ |

---

## 8. 한 줄 요약

> **5분 verbal demo script (한영) + 90초 compressed version + 면접관 follow-up 대응 매핑. 본 doc은 *말로 데모 가능한 자료*, 화면 없이도 시스템을 그릴 수 있게 단어로 시각화 설계.**

---

**Versioning**: v1 (this verbal script) — 2026-05-01 stay-internal package.
