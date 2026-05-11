# Asset 03 — Configuration Explainer: MIXED Accusation (P_CV_01)

**Probe ID**: P_CV_01
**Scenario**: accusation (S4 cast variation, full cast n=10)
**Configuration**: full cast (10 agents) + standard placement
**Outcome class**: **MIXED** — accusation 후 cohort split (한쪽 회복, 한쪽 굳음)
**Why it matters**: P10 (recovery)와 *direct contrast*. 같은 accusation pressure가 cast 구성에 따라 *outcome class*가 다름.

---

## Narrative

광장 한쪽 끝에서 누군가의 이름이 작게 입에 올랐다. 그 이름이 거리 끝까지 닿기 전에, 발걸음의 결이 한 박자 어긋났다. 권위의 시선은 거리 한 모서리에서 늘 한 박자 늦게 따라왔다. 그러나 그 자리에 머무를 수만은 없는 일이 곧 일어났다.

한 사람이 제자를 가리켰다. 그것은 작게 시작되었지만, 분명한 손가락질이었다. 주위 사람들의 눈빛이 한 박자 늦게 따라왔다. 비난은 흩어지지 않고 한 방향으로 모였다. 사람들의 눈은 거리의 사람들에게로 향했고, 다른 곳을 보던 사람도 결국 그 방향을 따라 고개를 돌렸다. 드문드문 고백이 새어 나왔다. 듣는 사람도, 말하는 사람도 그 무게에 익숙하지 않았다. 한 사람이 손을 들려다 멈추고, 그 손을 천천히 내려놓았다. 그러나 사람들의 반응은 한 결이 아니었다.

한쪽에서는 사람들이 다시 모이려 했다. 누군가는 자신의 잘못을 입에 올렸고, 다른 자리는 그 말을 받아들이지 못했다. 같은 사건 아래에서도 사람들의 발걸음은 갈라졌다. 한 시각이 지났을 때, 두 자리의 공기는 서로 다른 결로 굳어 가고 있었다.

거리에서는 누군가의 입에서 시작된 고백이 다음 사람으로 넘어갔고, 그 흐름이 짐을 조금씩 덜어 갔다. 윗방에서는 같은 말이 오가도 누구의 어깨에서도 짐이 풀리지 않았다. 두 자리는 가까이 있었지만, 다른 결의 시간이 흘렀다.

그리고 그 모든 결은 결국 한 모양으로 굳어 갔다.

갈라진 자리는 좁혀지지 않았다. 누구의 잘못도 분명히 가려지지 않은 채, 사람들은 서로 다른 결로 굳었다. 한쪽에서는 손가락이 거두어졌고, 다른 쪽에서는 그 손가락의 그림자가 그대로 남았다. 어느 쪽이 옳았는지는 끝내 분명해지지 않았다. 두 결의 시간이 한 거리 위에서 천천히 다른 결로 멀어져 갔다.

가장 무거웠던 자리들 중 어떤 곳은 풀렸고, 어떤 곳은 그대로였다. 두 자리가 같은 거리에 머물렀지만, 같은 결의 시간을 살지 않았다.

한 번 떨어진 이름의 자국은 거리 위에 그대로였다.

---

## 읽는 방법

이 asset의 핵심은 **P10과의 direct contrast**다.

| Aspect | P10 (asset 02) | P_CV_01 (이 asset) |
|---|---|---|
| Scenario | accusation | accusation |
| Cast | baseline (S5 placement) | full n=10 (S4 cast) |
| Outcome | RECOVERY_DOMINATED | MIXED |
| Pattern | 거리 전체 회복 | 두 자리 split (회복 vs 굳음) |

같은 accusation pressure → **다른 outcome**. *cast 구성*만 달라도 cohort routing이 달라지고, 결국 outcome class가 갈라진다.

### Configuration-dependence specific

> "한쪽에서는 손가락이 거두어졌고, 다른 쪽에서는 그 손가락의 그림자가 그대로 남았다."

이 한 문장이 *MIXED accusation의 핵심*. 같은 손가락질이지만 *어느 cohort에 닿았는지*에 따라 전혀 다른 결.

External eval (GPT-5.5)이 이를 *configuration-dependence existence evidence*로 검증:
> "Mixed outcomes appear when one cohort receives enough recovery signal while another remains capped or stuck."

---

## Configuration-dependence demo

P10 + P_CV_01 + Trilogy를 함께 보면 *configuration-sensitive divergence*의 3 layer 모두 보임:

1. **P10 (REC)**: 전체 회복 — 가장 *uniform* outcome
2. **P_CV_01 (MIXED)**: cohort split — *partial* configuration sensitivity
3. **Trilogy Act III (REC after 3 accusations)**: nonmonotonic — accusation 횟수가 늘어도 결말이 SAT가 아닌 REC

이 3 layer가 *configuration as core variable*임을 보여준다.

---

## Caveat

→ `appendix_method_caveat.md` 참조.

이 outcome도 *single-seed snapshot*. 같은 P_CV_01 configuration의 다른 seed에서는 RECOVERY 또는 SATURATION이 나올 수 있다. *Existence evidence이지 deterministic prediction이 아님*.
