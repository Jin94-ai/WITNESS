# Life Arc Seed Diversity — Engine-driven 검증

> *anchor: peter, seeds: [0, 7, 11], full_passion: True*

이 문서는 *베드로 공생애 시뮬레이션*이 진짜 engine-driven임을 보여준다. 다른 seed → 다른 observer dump → 같은 정경 사건에 대해 베드로가 *다른 행동*을 선택. 사건 description / scripture_ref는 `canonical_events.json`에서 verbatim, 선택은 engine `action_histories`에서 직접 인용된다.

**총 15개 정경 사건 중 11개에서 seed별 다른 선택.**

| 일째 | 사건 | seed 0 | seed 7 | seed 11 |
|---:|:---|:---|:---|:---|
| 0.2 ⚡ | 예수께서 시몬의 배에 오르사 무리를 가르치심 (눅 5:3) | **그물 손질 계속 (밤새 허탕)** `wash_nets` | **가까이서 말씀 경청** `listen_attentively` | **가까이서 말씀 경청** `listen_attentively` |
| 0.7 ⚡ | '깊은 데로 가서 그물을 내려 고기를 잡으라' — 어부 전문성… *(눅 5:4)* | **'말씀에 의지하여' 그물을 내림** `obey_reluctantly` | **'말씀에 의지하여' 그물을 내림** `obey_reluctantly` | **밤새 허탕임을 항변** `protest_fishing_expertise` |
| 1.7 ⚡ | '주여 나를 떠나소서 나는 죄인이로소이다' — 베드로의 두려움… *(눅 5:8)* | **무릎 꿇고 죄인임을 고백** `confess_sinfulness` | **놀라 그대로 굳어 있음** `freeze_in_shock` | **무릎 꿇고 죄인임을 고백** `confess_sinfulness` |
| 2.5 | '무서워하지 말라 이제 후로는 네가 사람을 취하리라' — 모든… *(눅 5:10)* | **배와 그물과 동업자를 두고 예수를 따름** `leave_everything_follow` | **배와 그물과 동업자를 두고 예수를 따름** `leave_everything_follow` | **배와 그물과 동업자를 두고 예수를 따름** `leave_everything_follow` |
| 68.5 ⚡ | '너희는 나를 누구라 하느냐' → 베드로 '주는 그리스도시요 … *(마 16:16)* | **제자들 앞에서 공개 고백** `confess_publicly` | **너무 큰 말임을 느껴 망설임** `hesitate_theological_weight` | **제자들 앞에서 공개 고백** `confess_publicly` |
| 70.0 | '인자가 많은 고난을 받고 장로들과 대제사장들과 서기관들에게 … *(마 16:21)* | **'주여 그리 마옵소서 이 일이 결코 주…** `protest_rebuke_jesus` | **'주여 그리 마옵소서 이 일이 결코 주…** `protest_rebuke_jesus` | **'주여 그리 마옵소서 이 일이 결코 주…** `protest_rebuke_jesus` |
| 101.6 ⚡ | 예루살렘 입성. 군중이 호산나를 외침 *(마 21, 막 11, 눅 19)* | **예수의 표정을 주시하며 조용히 따라감** `watch_quietly` | **군중과 함께 열광적으로 동참** `join_crowd` | **군중과 함께 열광적으로 동참** `join_crowd` |
| 110.9 ⚡ | 발씻음. 예수가 제자들의 발을 씻김 *(요 13:1-17)* | **발씻음을 거부함** `resist_washing` | **순종하여 발씻음을 받음** `accept_washing` | **발씻음을 거부함** `resist_washing` |
| 113.1 ⚡ | 겟세마네 기도. 예수가 기도하는 동안 제자들이 잠듦 *(마 26:36-46)* | **피로에 잠듦** `fall_asleep` | **피로에 잠듦** `fall_asleep` | **깨어 기도함** `stay_awake` |
| 113.8 ⚡ | 체포. 유다의 배반, 무리가 예수를 체포 *(마 26:47-56, 요 18:1-11)* | **멀리서 따라감** `follow_at_distance` | **도주** `flee` | **멀리서 따라감** `follow_at_distance` |
| 114.8 ⚡ | 대제사장 집 마당. 여종이 베드로를 알아봄 (1차 부인) *(마 26:69-70)* | **고백: 나는 그의 제자다** `confess` | _(미발화)_ | **부인: 나는 그를 모른다** `deny` |
| 115.0 | 두 번째 사람이 알아봄 (2차 부인) *(마 26:71-72)* | **맹세하며 부인** `deny` | **맹세하며 부인** `deny` | **맹세하며 부인** `deny` |
| 115.3 ⚡ | 세 번째 추궁. 저주하며 부인 (3차 부인) *(마 26:73-74)* | **저주하며 부인: 나는 그 사람을 알지 …** `deny` | **고백** `confess` | **고백** `confess` |
| 119.9 ⚡ | 빈 무덤 소식. 달려감 *(눅 24:12, 요 20:3-10)* | **숨어 있음** `stay_hiding` | **무덤으로 달려감** `run_to_tomb` | **무덤으로 달려감** `run_to_tomb` |
| 130.8 | 디베랴 호수. 153마리 물고기. 회복의 장면 *(요 21)* | **배에 머물러 있음** `stay_on_boat` | **배에 머물러 있음** `stay_on_boat` | **배에 머물러 있음** `stay_on_boat` |

⚡ = 같은 정경 사건에 대해 두 seed 이상이 다른 선택

*이 표는 `scripts/narrative/demo_life_arc_seed_diversity.py`에서 자동 생성. 선택 텍스트는 `canonical_events.json` action_options.description (한국어)에서, 선택 자체는 engine action_histories에서 인용된다.*