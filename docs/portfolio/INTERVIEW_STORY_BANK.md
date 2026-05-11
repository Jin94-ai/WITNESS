# WITNESS — Interview Story Bank

> 면접에서 자주 받을 9가지 질문에 대한 답변 모음. 각 답변은 *short (30-60s)* + *long (~2 min)* 두 버전. 한국어 + 영어.

---

## 0. 사용 원칙

- 면접관에게 *세 번 이상* 들리면 의심받음 → 같은 표현 반복하지 않음. 본 문서의 표현을 *어휘 풀*로 사용.
- 숫자는 *항상* 포함 (2,640+ tests, 5 seeds, 0 deps 등). 없으면 임팩트 약함.
- 첫 30초로 *반드시* claim + reason + concrete evidence 1개를 전달. 디테일은 follow-up 후.
- *솔직하게 한계 인정* → 신뢰 ↑. 모르는 것 인정 → 신뢰 ↑.

---

## Q1. "이 프로젝트가 뭔가요?" (30-second elevator)

### 한국어 — short (30s)

> *"WITNESS는 다중 에이전트 시뮬레이션과 비주얼 익스플로러로 구성된 시스템입니다. 역사적 인물(베드로, 반 고흐 등)을 에이전트로 모델링해서 시뮬레이션을 돌리고, 그 안에서 'story candidate'라고 부르는 흥미로운 순간을 자동으로 찾아내서 도트 기반 화면으로 보여줍니다. 4-layer 아키텍처에 2,640+ 테스트, 시각화는 vanilla JS + SVG로 외부 의존성이 0입니다."*

### 한국어 — long (~2 min)

> *"WITNESS는 'Agent-based World Simulation Explorer'입니다. 핵심은 두 부분입니다.*
>
> *첫째, 시뮬레이션 엔진 — 12개 에이전트가 hazard-driven Poisson process로 상호작용하면서 상태가 변합니다. 베드로의 수난 서사, 반 고흐의 회화 활동, 탈레랑의 정치 협상 같은 시나리오를 동일한 엔진 코드로 돌립니다. 엔진 layer에는 도메인 하드코딩이 금지되어 있고, 2,640개 이상 unit test로 검증합니다.*
>
> *둘째, 비주얼 익스플로러 — 시뮬레이션 결과를 도트와 zone으로 표시하고, timeline scrubbing으로 200 tick을 빠르게 훑을 수 있습니다. 시스템이 자동으로 흥미로운 순간을 8가지 salience tag로 표시해서, 사용자는 'where to look'을 빠르게 찾고 옆 패널에서 'why it matters'를 읽습니다.*
>
> *재미있는 부분은 cross-seed view입니다. 동일한 configuration을 5개 다른 seed로 돌리면 REC 3 / PARTIAL 1 / SAT 1처럼 다른 outcome 분포가 나옵니다. 단일 seed run의 함정을 시각으로 막는 검증 도구입니다.*
>
> *최근 (Phase 3.05)에는 4-Axis Discovery Candidate Classifier를 29-cycle iteration으로 진화시켰습니다. 학습 loss로 사용 금지 (Rule #14), scalar 합산 금지, 모든 threshold uncalibrated 명시 같은 정직성 원칙을 시스템 contract로 코드화했고, 124+ rubric tests로 자동 검증합니다."*

### English — short

> *"WITNESS is a multi-agent simulation system paired with a visual explorer. It models historical figures as agents, runs simulations, auto-detects 'story candidates' (interesting moments), and shows them as a dot-based timeline. Four-layer architecture, 2,640+ tests, visualization is vanilla JS + SVG with zero dependencies."*

### English — long

> *"WITNESS is what I call an 'Agent-based World Simulation Explorer'. Two main parts.*
>
> *First, the simulation engine — 12 agents interact through a hazard-driven Poisson process; their state evolves over time. The same engine code runs three scenarios: Peter (Passion narrative), Van Gogh (creative practice), and Talleyrand (political negotiation). The engine layer prohibits domain hardcoding — verified by grep — and is covered by 2,640+ unit tests.*
>
> *Second, a visual explorer — it renders the simulation as dots and zones with timeline scrubbing across 200 ticks. The system auto-detects salient moments using 8 mechanically-defined tags. The visual answers 'where to look', and a side panel answers 'why it matters'.*
>
> *The interesting part is the cross-seed view. Running the same configuration across 5 different seeds produces a distribution like REC 3 / PARTIAL 1 / SAT 1 — three distinct outcome classes from identical input. The view exists specifically to block single-seed bias — it's a validation tool, not just a viewer."*

---

## Q2. "왜 만들었나요?"

### 한국어 — short

> *"개인 연구 프로젝트로 시작했습니다. 다중 에이전트 시뮬레이션이 만들어내는 emergent behavior가 흥미로웠는데, 텍스트 로그로는 도저히 따라잡을 수 없어서 — 'configuration sensitivity를 어떻게 직접 보여줄 수 있을까'라는 질문에서 비주얼 익스플로러를 만들게 됐습니다. 핵심 동기는 'simulation의 dynamics를 정직하게 보여주는 도구'를 만들고 싶었다는 점입니다."*

### 한국어 — long

> *"세 가지 동기가 있었습니다.*
>
> *첫째, simulation engineering 자체에 대한 흥미. 다중 에이전트가 시간에 따라 상호작용하면서 cohort split, saturation lock 같은 매크로 패턴이 emergent하게 나타납니다. 이걸 어떻게 모델링하고 검증할 것인가가 출발점이었습니다.*
>
> *둘째, 비주얼라이제이션 디자인 실험. 200 tick × 12 agent의 상태 변화를 텍스트 로그로 따라가는 건 비현실적이었습니다. 'where to look'을 시각으로 빠르게 찾고 'why it matters'를 텍스트로 읽는 두-단계 인터랙션을 직접 만들어보고 싶었습니다.*
>
> *셋째, anti-bias engineering. 시뮬레이션 결과를 single seed로 돌리고 'configuration sensitivity'를 주장하는 패턴이 너무 흔합니다. 5+ seed 앙상블을 강제하는 cross-seed 뷰를 디자인 차원에서 만들어보고 싶었습니다.*
>
> *공개 제품이 아니라 internal exploration / 연구 프로토타입입니다 — 그래서 코드 공개 결정도 의도적으로 보류 중입니다."*

### English — short

> *"Personal research project. I was interested in the emergent behavior of multi-agent simulations, but text logs couldn't keep up — that pushed me toward the visual explorer. The core motivation was making a tool that *honestly shows* the dynamics, including configuration sensitivity."*

### English — long

> *"Three motivations.*
>
> *First, simulation engineering itself — multi-agent interactions produce emergent macro patterns (cohort splits, saturation locks) that I wanted to model and validate.*
>
> *Second, a visualization design experiment — tracking 200 ticks × 12 agents through text logs is impractical. I wanted to build a two-step interaction (visual surfaces 'where to look', text surfaces 'why it matters') from scratch.*
>
> *Third, anti-bias engineering — single-seed runs claiming 'configuration sensitivity' is a common pattern. I wanted to design a cross-seed view that structurally enforces 5+ seed ensembles.*
>
> *It's an internal research prototype, not a public product — that's why I've intentionally held back on releasing the code."*

---

## Q3. "가장 어려웠던 점은?"

### 한국어 — short

> *"layer 분리를 끝까지 지키는 것. 시뮬레이션 엔진에 시나리오 specific 로직을 넣고 싶은 유혹이 매번 있었는데, 'engine layer에 도메인 하드코딩 금지' 규칙을 grep으로 자동 검증하면서 막았습니다. 결과적으로 같은 엔진 코드가 베드로, 반 고흐, 탈레랑 3 시나리오를 돌릴 수 있게 됐습니다."*

### 한국어 — long

> *"세 가지가 어려웠습니다.*
>
> *첫째, layer 분리. 새 기능을 넣을 때마다 어느 layer에 들어가야 하는지 결정해야 했고, 'engine layer에 도메인 코드 절대 금지' 규칙을 어기고 싶은 유혹이 매번 있었습니다. 'grep -r peter engine/'으로 자동 검증하는 규칙을 만들어서 시스템이 스스로 막게 했습니다.*
>
> *둘째, 결과 해석의 자기 편향. single seed로 결과를 보고 '이게 시그널이다'라고 결론짓는 패턴이 반복적으로 나왔습니다. 8-rule self-evaluation framework를 만들면서 'null hypothesis 선언 없이 수치 해석 금지', 'sensitivity claim에는 5+ seed 필수' 같은 규칙으로 명문화했습니다. 이게 cross-seed view 디자인의 직접적 동기가 됐습니다.*
>
> *셋째, scope 관리. 시각화에 React를 도입하거나 ML 기반 salience 스코어러를 추가하고 싶은 유혹이 자주 있었지만, 'internal exploration tool에 framework overhead는 liability'라는 원칙으로 vanilla JS + SVG를 끝까지 유지했습니다."*

### English — short

> *"Maintaining strict layer separation. Every new feature tempted me to put scenario-specific logic into the engine layer; I blocked that with a grep-verified rule prohibiting domain hardcoding. As a result, the same engine code now runs three independent scenarios."*

### English — long

> *"Three things were genuinely hard.*
>
> *First, layer separation. Each new feature raised the question of which layer it belonged in, and the temptation to break the 'no domain hardcoding in engine' rule was constant. I made it system-enforced via grep — running 'grep -r peter engine/' must return zero hits.*
>
> *Second, self-bias in result interpretation. I kept finding myself drawing conclusions from single-seed runs. I codified an 8-rule self-evaluation framework — including 'no number interpretation without declaring a null hypothesis' and '5+ seed ensemble required for any sensitivity claim'. That directly motivated the cross-seed view's design.*
>
> *Third, scope discipline. There were constant temptations to add React, an ML-based salience scorer, or 3D visualization. I held to 'framework overhead is a liability for an internal exploration tool' — vanilla JS + SVG, zero dependencies, all the way through."*

---

## Q4. "기술적으로 가장 중요한 결정은?"

### 한국어 — short

> *"4-layer additive architecture입니다. simulation → observer → curation → visualization 각 layer가 이전 layer를 절대 수정하지 않고 추가만 합니다. 덕분에 engine layer는 freeze 상태로도 visualization을 계속 발전시킬 수 있고, schema versioning (v1, cross_seed_v1)으로 layer 간 데이터 contract를 명시적으로 관리합니다."*

### 한국어 — long

> *"두 가지가 가장 중요했습니다.*
>
> *첫째, 4-layer additive architecture. 처음에는 모든 로직이 simulation runner에 섞여 있었는데, observer layer를 분리하면서 'snapshot은 simulation의 partial trace, candidate는 observer가 본 salient moment'라는 의미를 명확하게 분리했습니다. 이후 candidate curation, visual explorer는 모두 *이전 layer를 수정하지 않고* 추가됐습니다. 이 패턴 덕분에 engine을 freeze한 상태로도 visualization을 v0 → v0.1 → v0.2로 반복 발전시킬 수 있었습니다.*
>
> *둘째, observer-not-evaluator 디자인 원칙. 처음에는 candidate에 자동 quality score를 매기려고 했는데, 결국 'system이 quality 판정을 자동화하면 결정 로직이 black-box가 된다'는 결론에 이르렀습니다. 그래서 시스템은 8 salience tag로 categorize만 하고, quality 판정은 사람 reviewer에게 맡기는 구조로 갔습니다. 이게 시스템의 의사결정을 끝까지 interpretable하게 유지한 핵심 결정이었습니다."*

### English — short

> *"The 4-layer additive architecture. Each layer (simulation → observer → curation → visualization) extends the previous one without modifying it. That allowed the engine to freeze while the visualization continued iterating, and schema versioning (v1, cross_seed_v1) makes inter-layer data contracts explicit."*

### English — long

> *"Two decisions stand out.*
>
> *First, 4-layer additive architecture. Originally, all logic lived in the simulation runner. Separating the observer layer made meanings explicit — 'snapshot' is a simulation's partial trace, 'candidate' is what the observer saw as salient. After that, candidate curation and visual explorer were added without modifying earlier layers. The engine could freeze while the visualization iterated through v0 → v0.1 → v0.2.*
>
> *Second, the observer-not-evaluator design principle. I almost added an automatic quality score to candidates. I stopped because automating quality judgment would have made the decision logic a black box. The system now only categorizes via 8 salience tags; humans make the final call. This kept the system's reasoning interpretable end-to-end."*

---

## Q5. "왜 도트 비주얼인가요?"

### 한국어 — short

> *"세 가지 이유입니다. 첫째, scale — 12 agent가 매 tick 업데이트되는데 도트는 인지 부담이 적습니다. 둘째, encoding 채널 — color × size × stroke로 state, intensity, salience를 동시에 표현 가능. 셋째, 캐릭터 그래픽 같은 representation을 쓰면 시청자가 'who is this character'에 끌려가는데, 이 도구는 '시스템 dynamics'가 주인공이라 도트가 적합합니다."*

### 한국어 — long

> *"의식적인 디자인 선택이었습니다.*
>
> *첫째, cognitive load. 12 agent가 매 tick 동시에 변하는데, 캐릭터 그래픽이나 아이콘을 쓰면 시청자의 시선이 'who is this character'에 끌려갑니다. 도트는 representation 부담이 거의 없어서 시청자가 시스템의 dynamics 자체에 집중할 수 있습니다.*
>
> *둘째, multi-channel encoding. 도트 하나에 fill color (state), size (intensity), stroke (boundary marking)을 동시에 인코딩할 수 있습니다. 캐릭터 아이콘으로는 같은 정보 밀도를 만들기 어렵습니다.*
>
> *셋째, scaling. 현재 12 dot이지만 1000 dot까지 가도 비슷한 패턴이 작동합니다 (SVG는 한계 있어서 Canvas로 갈 거지만 — 디자인 패턴은 동일).*
>
> *넷째, 가장 중요한 점은 — 이 도구의 주인공은 캐릭터가 아니라 *시스템 자체*라는 디자인 의도입니다. 도트는 그 의도를 시각으로 강제하는 표현 방식입니다."*

### English — short

> *"Three reasons. First, scale — 12 agents updating every tick require a low-cognitive-load representation. Second, multi-channel encoding — color × size × stroke encode state, intensity, and salience simultaneously. Third, character graphics would draw attention to 'who is this character'; the system itself is the subject, not the avatars."*

### English — long

> *"This was a deliberate design choice.*
>
> *First, cognitive load. With 12 agents updating every tick, character graphics or icons would pull the viewer's attention into 'who is this character'. Dots carry almost no representational load, so the viewer focuses on the system's dynamics.*
>
> *Second, multi-channel encoding. A single dot can encode fill color (state), size (intensity), and stroke (boundary marking) simultaneously. Character icons can't carry that information density.*
>
> *Third, scaling. The current 12 dots could go to 1000 with similar patterns (SVG would need to switch to Canvas, but the design idiom holds).*
>
> *Fourth, and most importantly — the subject of this tool is the *system*, not the characters. Dots structurally enforce that intent in the visual."*

---

## Q6. "AI 프로젝트인데 LLM이 핵심인가요?"

### 한국어 — short

> *"아닙니다. 시뮬레이션 루프에는 LLM이 일절 들어가지 않습니다. salience detection, candidate curation 모두 mechanically-defined 룰로 돌아갑니다. 'AI'라는 단어가 LLM을 떠올리게 하는데, 이 프로젝트의 'agent'는 multi-agent simulation의 agent이지 LLM agent가 아닙니다. 의도적인 분리입니다 — 시스템 dynamics를 검증하는 게 먼저고, generative 레이어는 별도 결정으로 미뤘습니다."*

### 한국어 — long

> *"중요한 구분입니다. 'agent-based simulation'에서 'agent'는 multi-agent system의 의미입니다 — 각자 state를 가진 entity. LLM agent와는 다른 개념입니다.*
>
> *시뮬레이션 루프 자체에는 LLM이 들어가지 않습니다. agent state 변화는 hazard rate Poisson process로, salience tag는 mechanically-defined rule (cohort split, saturation lock 같은 명시적 조건)로, candidate curation은 deterministic algorithm (temporal diversity + near-duplicate reduction)으로 작동합니다.*
>
> *왜 이렇게 했는가 — 두 가지 이유입니다. 첫째, simulation dynamics를 먼저 검증하고 싶었습니다. 그 위에 LLM-based generative layer를 얹으면 두 layer의 오류가 합쳐져서 디버깅이 어려워집니다. 둘째, observer-not-evaluator 원칙 — quality 판정은 사람 reviewer에게 남겨두고 싶었습니다.*
>
> *추후 LLM 기반 narrative renderer를 추가하는 건 자연스러운 방향이지만, 현재는 의도적으로 보류 중입니다."*

### English — short

> *"No — there's no LLM in the simulation loop. Salience detection and candidate curation are all mechanically-defined rules. 'Agent' here means multi-agent simulation, not LLM agent. Deliberate separation: validate system dynamics first, defer the generative layer."*

### English — long

> *"Important distinction. 'Agent' in 'agent-based simulation' means an entity with state in a multi-agent system — different from 'LLM agent'.*
>
> *No LLM in the simulation loop. State transitions use a hazard-rate Poisson process; salience tags are mechanically-defined rules (cohort split, saturation lock — explicit conditions); candidate curation is a deterministic algorithm (temporal diversity + near-duplicate reduction).*
>
> *Two reasons for this. First, I wanted to validate the simulation dynamics first; layering an LLM-based generative on top would compound errors and complicate debugging. Second, the observer-not-evaluator principle — quality judgment is reserved for the human reviewer.*
>
> *Adding an LLM-based narrative renderer would be a natural next step, but it's intentionally on hold."*

---

## Q7. "테스트/검증은 어떻게 했나요?"

### 한국어 — short

> *"세 축으로 검증했습니다. 첫째, 2,640+ pytest unit test, 97%+ coverage. 둘째, Pattern-Oriented Modeling — bottleneck 탐지 (Cohen's d=-6.87, p<0.001), counterfactual ablation. 셋째, cross-seed (5 seeds × 200 ticks)로 configuration sensitivity 직접 가시화. 추가로 cross-scenario universality — 같은 엔진 코드가 Peter, Van Gogh, Talleyrand 3 시나리오를 content-only 차이로 돌립니다."*

### 한국어 — long

> *"검증 프레임워크를 multi-axis로 만들었습니다.*
>
> *Axis 1: unit test. 2,640+ pytest, 97%+ coverage on critical modules, ruff + mypy 0 errors. CI에서 ruff + mypy + pytest가 push마다 돌아갑니다.*
>
> *Axis 2: Pattern-Oriented Modeling (POM). simulation result에 expected pattern 5-8개를 등록해서 all-pass 비율로 측정합니다. 예를 들어 Peter scenario에서 sword_drawn 이벤트는 bottleneck이고 Phi=0.951로 나옵니다.*
>
> *Axis 3: counterfactual ablation. Judas 에이전트를 제거하면 arrest 발생률이 100%에서 0%로 떨어집니다 (Cohen's d=-6.87, permutation test p<0.001). 이게 'Judas는 시나리오의 structural keystone'을 정량적으로 보여줍니다.*
>
> *Axis 4: cross-seed sensitivity. 5 seeds × 200 ticks로 outcome distribution을 직접 시각화. single seed의 함정을 시각으로 막습니다.*
>
> *Axis 5: cross-scenario universality. 같은 엔진 코드가 Peter, Van Gogh, Talleyrand를 돌립니다. content/[name]/ 데이터만 다르고 engine 수정은 0입니다.*
>
> *그리고 8-rule self-evaluation framework로 보고서 자체의 자기 편향을 차단합니다 — null hypothesis 선언, falsifiability criterion, 5+ seed 앙상블 강제 등."*

### English — short

> *"Three axes. First, 2,640+ pytest unit tests with 97%+ coverage. Second, Pattern-Oriented Modeling — bottleneck detection (Cohen's d=-6.87, p<0.001) and counterfactual ablation. Third, cross-seed (5 seeds × 200 ticks) directly visualizes configuration sensitivity. Plus cross-scenario universality — same engine runs Peter, Van Gogh, and Talleyrand with content-only differences."*

### English — long

> *"Multi-axis validation framework.*
>
> *Axis 1 — unit testing. 2,640+ pytest, 97%+ coverage on critical modules, ruff + mypy with 0 errors. CI runs lint + types + tests on every push.*
>
> *Axis 2 — Pattern-Oriented Modeling. Each scenario registers 5-8 expected patterns; pass rate is measured as the all-pass ratio. In the Peter scenario, the sword_drawn event is a structural bottleneck (Phi=0.951).*
>
> *Axis 3 — counterfactual ablation. Removing the Judas agent drops arrest rate from 100% to 0% (Cohen's d=-6.87, permutation p<0.001), quantitatively demonstrating that Judas is a structural keystone.*
>
> *Axis 4 — cross-seed sensitivity. 5 seeds × 200 ticks, with the outcome distribution directly visualized. Single-seed bias is blocked structurally.*
>
> *Axis 5 — cross-scenario universality. Same engine runs Peter, Van Gogh, and Talleyrand. Only `content/[name]/` differs; the engine is untouched.*
>
> *On top of all this, an 8-rule self-evaluation framework guards against bias in the reports themselves — mandating null-hypothesis declaration, falsifiability criteria, and 5+ seed ensembles for sensitivity claims."*

---

## Q8. "한계는 무엇인가요?"

### 한국어 — short

> *"네 가지를 솔직히 말씀드립니다. 첫째, 단일 seed bias — cross-seed view 전에 만든 일부 검증 결과는 single-seed 한정. 둘째, sacred dynamics (반 고흐 같은 contemplative 시나리오)는 8 salience tag로 잘 surface 안 됨 (시스템이 인정함). 셋째, 모바일 / 반응형 미지원 — desktop only. 넷째, story renderer는 의도적으로 freeze 상태."*

### 한국어 — long

> *"여러 한계가 있습니다.*
>
> *첫째, single-seed bias. cross-seed view를 만들기 전에 시행한 일부 검증 결과는 single-seed 한정입니다. 그 점을 8-rule framework H8에 명시적으로 명문화해서, 향후 ensemble re-test가 falsification path 역할을 하도록 했습니다.*
>
> *둘째, sacred dynamics 한계. 반 고흐 같은 contemplative 시나리오는 8 salience tag로 잘 surface가 안 됩니다 (timeline이 거의 비어 있음). 시스템이 자동 튜닝으로 가짜 salience를 만들지 않고, 'low-activity candidate'로 분류해서 정직하게 보여줍니다 — 이게 observer-not-evaluator 원칙의 결과지만, 동시에 한계이기도 합니다.*
>
> *셋째, scaling. 현재 12 agent까지는 SVG로 잘 작동하지만, 1000 agent급은 Canvas로 가야 하고 데이터 export도 trim 필요. 모바일 / 반응형은 미지원, desktop only.*
>
> *넷째, story renderer는 의도적으로 freeze. 별도 CLI tool로 narrative generation 기능이 있지만, 비주얼 익스플로러와 통합하지 않았습니다 — 두 도구의 책임을 분리하고 싶었습니다.*
>
> *다섯째, public release 미실시. internal exploration 단계로 의도적으로 보류 중입니다 — LICENSE, branch 전략, asset capture 등이 결정되지 않았습니다."*

### English — short

> *"Four honestly. First, some pre-cross-seed validations were single-seed only. Second, contemplative scenarios (like Van Gogh) don't surface well through the 8 salience tags — system shows that honestly rather than auto-tuning. Third, desktop-only — no mobile/responsive support. Fourth, the story renderer is intentionally frozen — a separate CLI tool, not integrated."*

### English — long

> *"Several real limitations.*
>
> *First, single-seed bias in some early validations — pre-cross-seed work was single-seed only. I codified this in the H8 rule of the self-evaluation framework so that any future ensemble re-test serves as a falsification path.*
>
> *Second, sacred-dynamics limitation. Contemplative scenarios like Van Gogh don't surface well through the 8 salience tags (the timeline is almost empty). The system doesn't auto-tune to fake salience; it classifies them as 'low-activity candidates' honestly. That's a consequence of the observer-not-evaluator principle, but it's also a real limitation.*
>
> *Third, scaling. SVG works for 12 agents but 1,000 would need Canvas, and data export would need trimming. Desktop-only — no mobile/responsive.*
>
> *Fourth, the story renderer is intentionally frozen. A separate CLI tool generates narration but is not integrated into the visual explorer — I wanted to separate responsibilities cleanly.*
>
> *Fifth, no public release. The project is intentionally held back at the internal-exploration stage — LICENSE, branch strategy, and asset capture haven't been decided yet."*

---

## Q9. "다음에 뭘 개선할 건가요?"

### 한국어 — short

> *"세 갈래가 있습니다. 첫째, sacred dynamics용 추가 salience tag 디자인 (현 8 tag는 external-pressure dynamics에 튜닝됨). 둘째, multi-anchor cross-seed expansion (현재는 1 anchor만 cross-seed 데이터 보유). 셋째, Canvas 기반 visual layer로 1000+ agent까지 scaling — 단, 이 모든 건 현 Visual Explorer v0.2의 사용성 검증 후에 결정합니다."*

### 한국어 — long

> *"단기 / 중기 / 장기로 나눠서 말씀드립니다.*
>
> *단기 (1-2주): Visual Explorer v0.2의 demo asset 캡처 (screenshot, GIF), 포트폴리오 문서 정제, v0.2 roadmap 정리.*
>
> *중기 (1-3개월): 첫째, multi-anchor cross-seed 확장 — 현재는 peter_scarcity_triple만 cross-seed 데이터 보유. 둘째, sacred-dynamics용 salience encoding tuning — 현 8 tag는 external-pressure dynamics에 편향됨. 셋째, Van Gogh cross-seed validation — Peter scenario 다음 단계.*
>
> *장기 (별도 fork decision): 네 가지 옵션이 있습니다. (a) Visual Explorer를 observable world engine으로 확장, (b) story / IP asset 개발 (renderer 재개), (c) simulation 연구 / 논문 검증, (d) playable prototype (intervention / what-if). 각 갈래는 trade-off가 다르고, 단기/중기 단계의 사용 데이터를 보고 결정할 예정입니다.*
>
> *그리고 가장 중요한 — 새 기능을 추가하기 전에 *현 시스템 사용자의 reviewer feedback*을 먼저 받고 결정하려고 합니다. premature optimization을 막는 디자인 원칙입니다."*

### English — short

> *"Three directions. First, design additional salience tags for contemplative scenarios (current 8 are tuned for external-pressure dynamics). Second, multi-anchor cross-seed expansion (only one anchor has cross-seed data right now). Third, Canvas-based visual layer for 1,000+ agent scaling — but all of this is conditional on usability feedback from the current v0.2."*

### English — long

> *"Short-term, mid-term, long-term.*
>
> *Short-term (1-2 weeks): asset capture (screenshots, GIFs) for the v0.2 demo, portfolio document polishing, v0.2 roadmap consolidation.*
>
> *Mid-term (1-3 months): first, multi-anchor cross-seed expansion — currently only peter_scarcity_triple has cross-seed data. Second, salience-encoding tuning for sacred dynamics — the current 8 tags are biased toward external-pressure scenarios. Third, Van Gogh cross-seed validation as the natural next scenario after Peter.*
>
> *Long-term (separate fork decision): four options on the table — (a) extend the visual explorer into an observable world engine, (b) develop story/IP assets (resume the renderer), (c) simulation research / paper validation, (d) playable prototype (intervention / what-if). Each option has different trade-offs, so I'm waiting for usage data from the short/mid-term stages before committing.*
>
> *And most importantly — I want to get reviewer feedback on the current system before adding any new features. It's a design discipline against premature optimization."*

---

## 10. 자주 받는 follow-up 질문 (mini bank)

### Q. "Why Python for the engine?"
> *"Pydantic for schema validation, mature pytest ecosystem, and the 4-layer separation makes Python's slower runtime a non-issue at the engine throughput we need (~1,000-1,300 ticks/sec). For higher-throughput targets, the engine layer could port to a faster language without touching the visualization."*

### Q. "How long did this take?"
> *"It's been an ongoing internal exploration over [N months]. Most of the architecture decisions emerged through iteration — initial code had everything mixed in the simulation runner; the layer separation and observer-not-evaluator principle came from refactoring patterns I noticed."*

### Q. "What did you learn?"
> *"Three things. First, anti-bias engineering needs to be system-enforced, not just stated as a guideline (cross-seed view is the practice, not just the slogan). Second, additive layer architecture pays off — the engine could freeze while visualization iterated. Third, restraint matters — saying 'no' to ML scoring, React, and 3D was as important as building the parts I did keep."*

### Q. "Was this solo?"
> *"It's a personal research project — the architecture, engine, observer, and visualization are my work. I used LLM design partners for sanity-checking decisions, but the core code and design choices are mine."*

### Q. "How does this compare to [agent-based modeling framework like Mesa/NetLogo]?"
> *"Honest answer — this is more focused than a general framework. Mesa/NetLogo are domain-agnostic toolkits; WITNESS is opinionated about the observer-not-evaluator principle, additive layers, and visualization-for-validation. If I were building a general framework, I'd start from one of those. But for an internal exploration of one specific question (configuration sensitivity in narrative simulation), the focused stack works."*

### Q. "What would you do differently?"
> *"Two things. First, I'd write more tests *during* layer separation, not after — some refactoring rounds would have been smoother. Second, I'd version-tag the data export schema earlier — I had to retrofit the v1 / cross_seed_v1 distinction once the visualization started consuming both."*

---

## 11. 면접 디테일 팁

### Do
- ✅ 30초 안에 claim + reason + 1 concrete evidence 전달
- ✅ 숫자는 항상 포함 (2,640+ tests, 5 seeds, 0 deps)
- ✅ 한계는 *솔직하게* — single-seed bias, sacred dynamics, mobile 미지원
- ✅ "deliberate choice"로 표현 — 하지 않은 것에 이유가 있음을 보여줌
- ✅ "next iteration could absolutely add X" — 미래에 열린 시각

### Don't
- ❌ "그냥 만들었어요 / 자동으로 됐어요" — 디자인 의도 없는 것처럼 들림
- ❌ "AI 이야기 생성기" / "story generator" / "religious simulator"
- ❌ 한 번도 안 써본 기술을 "잘 안다"고 표현
- ❌ 자세한 종교 / 신학 디테일 — "historical figures" 정도로 추상화
- ❌ Lee directive 언급 — "design specifications" 또는 "project requirements"
- ❌ 한 답변에 5가지 디테일 다 넣기 — follow-up 질문 받으려고 의도적으로 1-2개씩만

---

## 12. ABSOLUTE 원칙 + Lee directive 준수

| 원칙 | 준수 |
|---|:---:|
| Lee §"코드 수정 금지" | ✅ |
| Lee §"public release 금지" | ✅ — 면접 답변 라이브러리만 |
| Lee §"내부 로그 삭제하지 말 것" | ✅ |

---

## 13. 한 줄 요약

> **9 핵심 질문 + follow-up mini bank × 한영 × short/long = 면접 답변 라이브러리. 본 doc은 *어휘 풀*, 면접에서 표현 그대로 외우지 말고 핵심만 가져갈 것.**

---

**Versioning**: v1 (this story bank) — 2026-05-01 stay-internal package.
