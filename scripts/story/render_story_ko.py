"""Render Korean story text from Narrative IR.

Per `docs/story/STORY_OUTPUT_SPEC.md` §5-§6. Reads
`data/story/narrative_ir/{probe_id}.json` and produces:
- `docs/story/generated/{probe_id}_summary_ko.txt`   (400-800자, 건조한 서사형)
- `docs/story/generated/{probe_id}_narrative_ko.txt` (1000-1800자, 감정 서사형)

Template-guided rendering. No LLM. Each IR field maps to one or more
sentence templates with light variation chosen by feature properties.

Forbidden output (per spec §6):
- raw IDs (P6, A1, L1)
- numbers (peak, final, t=N)
- meta phrases (이 시뮬레이션, 이 trajectory, 데이터에 따르면)

Usage:
    python scripts/story/render_story_ko.py P6
    python scripts/story/render_story_ko.py --all
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
IR_DIR = ROOT / "data" / "story" / "narrative_ir"
OUT_DIR = ROOT / "docs" / "story" / "generated"


# ============================================================
# Role / location semantic translation (forbidden raw IDs per spec §6)
# ============================================================

ROLE_KO = {
    "merchant": "상인",
    "fisher_laborer": "노동자",
    "laborer": "노동자",
    "beggar": "걸인",
    "family": "가족",
    "authority": "권위자",
    "authority_priest": "사제",
    "soldier_enforcer": "병사",
    "enforcer": "집행관",
    "crowd": "군중",
    "crowd_participant": "거리의 사람들",
    "outsider": "이방인",
    "elite_strategist": "지도자",
    "disciple_follower": "제자",
    "spiritual_wanderer": "방랑자",
    "prophet": "예언자",
}

# Location semantic by primary_pressure
LOC_BY_PRESSURE = {
    "scarcity": ["시장", "곡물 창고", "빈민가의 길목"],
    "accusation": ["광장", "관청 안마당", "거리"],
    "sacred": ["성전 바깥뜰", "성전 안", "거리"],
}


def role_ko(role_id: str) -> str:
    return ROLE_KO.get(role_id, "그 사람")


def _has_batchim(word: str) -> bool:
    """Korean 받침 detection — last char has trailing consonant?"""
    if not word:
        return False
    last = word[-1]
    if not (0xAC00 <= ord(last) <= 0xD7A3):
        return False  # not Hangul syllable
    return (ord(last) - 0xAC00) % 28 != 0


def josa(word: str, with_batchim: str, without_batchim: str) -> str:
    """Pick Korean particle based on 받침. e.g. josa('상인', '을', '를') -> '을'."""
    return with_batchim if _has_batchim(word) else without_batchim


def role_plural_ko(role_id: str) -> str:
    """Get plural Korean form. Avoids '들들' duplication."""
    base = role_ko(role_id)
    if base.endswith("들") or "사람들" in base:
        return base
    return base + "들"


def variant_pick(probe_id: str, slot: str, pool: list) -> str:
    """Loop C-3: Pick a sentence variant deterministically by probe_id+slot hash.

    Same probe_id + slot always returns same variant (reproducible). Different
    probe_ids get different variants from the pool, breaking P4=P5 identity.
    """
    if not pool:
        return ""
    h = hashlib.md5(f"{probe_id}|{slot}".encode("utf-8")).hexdigest()
    idx = int(h[:8], 16) % len(pool)
    return pool[idx]


# ============================================================
# Sentence builders per IR field
# ============================================================

OPENING_POOLS = {
    "scarcity": [
        "곡식이 비어 가는 계절이었다. 시장과 곡물 창고와 빈민가는 한 호흡을 공유했고, "
        "사람들의 눈치는 서로의 손끝으로 향했다. 부족함은 누구의 잘못도 아니었지만, "
        "그 사실은 사람들을 위로해 주지 않았다.",
        "거두는 손은 가벼웠다. 시장과 곡물 창고는 평소만큼 분주하지 않았고, "
        "빈민가의 골목은 작은 소문으로 채워졌다. 그 소문이 무엇을 향하는지 누구도 분명히 말하지 않았다.",
        "곡식이 모자란다는 말은 며칠 전부터 떠돌고 있었다. 시장의 가격은 흔들렸고, "
        "곡물 창고를 바라보는 눈빛은 더 길어졌다. 빈민가에서는 평소와 다른 침묵이 깔렸다.",
        # J-Beta Gate 1 자율 cycle additions:
        "곡식 자루가 가벼워질수록 사람들의 눈빛도 함께 가벼워지지는 않았다. "
        "시장의 가격은 흔들렸고, 그 흔들림은 손끝의 망설임으로 이어졌다. "
        "빈민가에서는 이미 며칠 전부터 작은 한숨들이 모이고 있었다.",
        "가뭄의 기색은 처음에는 시장의 끝자락에서 시작되었다. 곡물 창고로 향하는 발걸음이 한 박자 늦어졌고, "
        "빈민가의 문이 평소보다 일찍 닫혔다. 사람들은 그 변화를 입에 담지 않았지만, 모두 같은 무게를 느끼고 있었다.",
    ],
    "accusation": [
        "공기는 이미 무거웠다. 광장과 관청 안마당과 좁은 거리 사이로 의심이 흐르고 있었고, "
        "사람들은 그 흐름을 보지 않으려 애썼지만 보지 않을 수 없었다.",
        "그 자리에 서 있던 사람들은 알고 있었다. 무언가가 곧 시작될 것이라는 것을. "
        "광장과 관청 안마당의 공기는 평소보다 한 박자 더 짧았다.",
        "거리는 평소처럼 흐르지 않았다. 광장과 관청 안마당 사이를 오가는 발걸음이 지나치게 조심스러웠고, "
        "그 조심스러움이 오히려 무언가가 임박했다는 표지였다.",
        # Cycle 3 Patch F additions:
        "광장 한쪽 끝에서 누군가의 이름이 작게 입에 올랐다. "
        "그 이름이 거리 끝까지 닿기 전에, 발걸음의 결이 한 박자 어긋났다.",
        "관청 안마당의 그림자가 평소보다 길게 거리 위로 떨어졌다. "
        "그 그림자 안에서 사람들의 시선은 서로를 비껴 갔다.",
        "거리에는 평소와 같은 인사가 오갔다. "
        "그러나 그 인사 끝에 매번 한 박자 더 머무르는 시선이 있었다.",
    ],
    "sacred": [
        "성전 바깥뜰에 사람들이 모여 있었다. 안쪽에서 흘러나오는 기도 소리가 거리까지 닿았고, "
        "거리의 사람들은 무언가가 일어날 것을 예감했다. 그것이 무엇인지 분명히 말할 수 있는 사람은 없었지만, "
        "어떤 자리에서는 평소보다 더 길게 머무는 사람들이 보였다.",
        "성전을 향한 발걸음은 평소보다 많았다. 바깥뜰에 모인 사람들 사이에는 "
        "익숙한 침묵 같기도 하고 낯선 기다림 같기도 한 공기가 흘렀다. "
        "그 공기는 한 번에 깨질 수 있는 것이 아니었다.",
        "성전 안에서는 기도가 이어졌고, 바깥에서는 그 기도를 듣는 사람들이 늘어 갔다. "
        "그 늘어남 자체가 하나의 사건이 되어 가고 있었고, "
        "거리의 흐름은 평소와 다른 결로 자리를 옮기고 있었다.",
        # Cycle 3 Patch F additions:
        "성전의 첫 빛이 안마당에 닿기 전부터 사람들이 모이고 있었다. "
        "그 모임의 결은 평소의 모임과 한 박자 달랐다.",
        "성전 바깥 계단 위로 한 사람이 천천히 걸어 올라갔다. "
        "그 한 걸음마다 거리의 호흡이 한 박자씩 늦어졌다.",
        "기도 소리는 들리지 않았지만, 사람들은 그 소리가 시작될 자리에 모여 있었다. "
        "그 기다림 자체가 한 종류의 사건이었다.",
    ],
    "low": [
        "조용한 날이었다. 거리와 안뜰 모두 평소와 다르지 않았고, 오가는 인사도 어제와 같았다. "
        "어떤 자리에서 사람들이 평소보다 잠시 더 머물렀지만, 그것은 사건이라 부를 만한 것이 아니었다.",
        "특별한 일이 없는 날이었다. 사람들의 발걸음은 일상의 무게로 흘렀고, 거리에는 익숙한 소리만 남았다. "
        "어디선가 작은 움직임이 있었다 해도, 그것은 곧 평소의 결로 돌아갔다.",
    ],
    "other": [
        "사람들이 흩어져 있었다. 누구도 서로를 보지 않았지만, 작은 흔들림이 어디선가 시작되고 있었다.",
        "누구도 분명한 자리를 잡지 못한 시각이었다. 거리에 깔린 공기는 익숙하지 않았다.",
    ],
}


def _opening(opening: dict, pressure: str, dominant: str, probe_id: str = "") -> str:
    if opening["key"] != "opening":
        return ""
    if pressure == "scarcity":
        s = variant_pick(probe_id, "opening_scarcity", OPENING_POOLS["scarcity"])
    elif pressure == "accusation":
        s = variant_pick(probe_id, "opening_accusation", OPENING_POOLS["accusation"])
    elif pressure == "sacred":
        s = variant_pick(probe_id, "opening_sacred", OPENING_POOLS["sacred"])
    elif pressure == "none_clear" or dominant == "low_activity":
        s = variant_pick(probe_id, "opening_low", OPENING_POOLS["low"])
    else:
        s = variant_pick(probe_id, "opening_other", OPENING_POOLS["other"])
    if opening.get("has_authority") and pressure != "sacred":
        auth_pool = [
            " 권위의 시선은 한쪽 끝에서 모든 것을 지켜보고 있었다.",
            " 권위의 시선은 거리 한 모서리에서 늘 한 박자 늦게 따라왔다.",
            " 권위의 자리에서 내려오는 시선은 거리 위로 길게 떨어졌다.",
        ]
        s += variant_pick(probe_id, "opening_authority", auth_pool)
    return s


def _initial_tension(t: dict) -> str:
    if t["key"] == "tension_scarcity_accusation":
        target = role_ko(t.get("target_role") or "merchant")
        return (
            f"빈손이 늘어 가던 어느 시각, {target}의 이름이 처음 입에 올랐다. "
            "누군가 곡식을 숨겼다는 말이 시장 한구석에서 시작되었고, 그 말은 "
            "오래 걸리지 않아 거리 끝까지 닿았다."
        )
    if t["key"] == "tension_direct_accusation":
        target = role_ko(t.get("target_role") or "disciple_follower")
        return (
            f"한 사람이 {target}{josa(target, '을', '를')} 가리켰다. "
            "그것은 작게 시작되었지만, 분명한 손가락질이었다. "
            "주위 사람들의 눈빛이 한 박자 늦게 따라왔다."
        )
    if t["key"] == "tension_sacred_event":
        return (
            "성전 안에서 무언가가 일어났다. 사람들은 자기도 모르게 호흡을 멈췄고, "
            "그 침묵이 거리까지 흘러나왔다. 누구의 말도 그 순간을 정확히 옮기지 못했다. "
            "그 순간 이후 사람들의 자세는 한 박자 늦게 다시 자리를 잡기 시작했다."
        )
    if t["key"] == "tension_none":
        return "큰 사건은 없었다. 다만 작은 마찰들이 거리를 따라 가볍게 움직였고, 그 외에는 아무것도 멈추거나 시작되지 않았다."
    return "긴장은 조용히 시작되었다. 누구도 그것을 사건이라 부르지 않았지만, 무언가가 분명히 움직이고 있었다."


def _pressure_arc(arc: dict, pressure: str) -> str:
    parts = []
    # B-1: blame_band 3단계로 다르게 묘사
    blame_band = arc.get("blame_band", "absent")
    if blame_band == "dominant":
        target = arc.get("top_blame_target")
        if target and arc.get("top_blame_strong"):
            tk_plural = role_plural_ko(target)
            parts.append(
                f"비난은 흩어지지 않고 한 방향으로 모였다. 사람들의 눈은 {tk_plural}에게로 빠르게 향했고, "
                "그 무게는 거리 끝까지 같은 결로 쏟아졌다."
            )
        else:
            parts.append(
                "비난은 한 자리에 무겁게 내려앉았다. 다른 곳을 보던 사람도 결국 그 방향으로 끌려갔다."
            )
    elif blame_band == "strong":
        target = arc.get("top_blame_target")
        if target and arc.get("top_blame_strong"):
            tk_plural = role_plural_ko(target)
            parts.append(
                f"비난은 흩어지지 않고 한 방향으로 모였다. 사람들의 눈은 {tk_plural}에게로 향했고, "
                "다른 곳을 보던 사람도 결국 그 방향을 따라 고개를 돌렸다."
            )
        else:
            parts.append(
                "비난은 빠르게 한곳으로 모였다. 사람들은 누가 시작했는지 묻지 않은 채 그 방향으로 나아갔다."
            )
    elif blame_band == "weak":
        parts.append(
            "비난은 옅게라도 거리에 떠다녔다. 분명한 손가락질은 아니었지만, 누구도 그 흐름을 모르지는 않았다."
        )
    # absent → 비난 문장 생략
    if arc.get("suspicion_strong") and pressure != "sacred":
        parts.append("의심이 거리 위로 짙게 깔렸고, 누구의 인사도 가볍지 않았다. 작은 표정 하나가 큰 의미를 가졌다.")
    elif arc.get("suspicion_strong") and pressure == "sacred":
        parts.append("성전 바깥에서는 의심이, 안에서는 기도가 동시에 깊어졌다. 둘은 같은 자리에서 자라났지만 서로를 보지 못했다.")
    # D-2: authority_pattern으로 분기 (decayed/loosened/sustained)
    auth_pattern = arc.get("authority_pattern")
    if auth_pattern == "sustained":
        parts.append("권위의 시선은 끝까지 느슨해지지 않았고, 그 시선 아래에서 사람들의 발걸음은 더 조심스러워졌다.")
    elif auth_pattern == "loosened":
        parts.append("권위의 시선은 한참을 머물렀다가 천천히 옅어졌지만, 한번 깔린 무게는 거리에 흔적을 남겼다.")
    elif auth_pattern == "decayed":
        parts.append("권위의 시선은 한때 무거웠으나 시간이 흐르며 풀려 갔다.")
    if arc["confession_volume"] == "high":
        parts.append("고백은 멈추지 않고 이어졌고, 용서한다는 말도 그만큼 거리 위에 떠다녔다. 그러나 말이 많아질수록, 어떤 자리는 오히려 더 고요했다.")
    elif arc["confession_volume"] == "moderate":
        parts.append("드문드문 고백이 새어 나왔다. 듣는 사람도, 말하는 사람도 그 무게에 익숙하지 않았다.")
    elif arc["confession_volume"] == "low":
        parts.append("말은 줄어들었다. 사람들은 입을 다물었고, 침묵이 어떤 외침보다 무겁게 깔렸다.")
    if not parts:
        parts.append("흔들림은 천천히 커졌다. 누구도 그것을 막거나 키우지 않았지만, 그 자체로 흐름이 되었다.")
    return " ".join(parts)


def _group_response(resp: dict) -> str:
    rec, sat, par = resp["n_recovery"], resp["n_saturation"], resp["n_partial"]
    if resp.get("split"):
        return (
            "한쪽에서는 사람들이 다시 모이려 했다. 누군가는 자신의 잘못을 입에 올렸고, "
            "다른 자리는 그 말을 받아들이지 못했다. 같은 사건 아래에서도 사람들의 발걸음은 갈라졌다. "
            "한 시각이 지났을 때, 두 자리의 공기는 서로 다른 결로 굳어 가고 있었다."
        )
    if rec > 0 and sat == 0:
        return (
            "사람들은 흔들렸지만 다시 자리를 잡았다. 고백이 한 사람에서 다음 사람으로 옮겨 갔고, "
            "무거움은 조금씩 줄어들었다. 누가 먼저였는지는 분명하지 않았지만, 그 흐름은 거리 끝까지 닿았다."
        )
    if sat > 0 and rec == 0:
        return (
            "사람들은 자리에 굳었다. 고백이 있었어도 무거움은 풀리지 않았고, "
            "어떤 자리에서는 시간이 멈춘 것처럼 보였다. 같은 자세를 며칠 동안 유지하는 사람들의 모습이 거리에 남았다."
        )
    if par > 0 and rec == 0 and sat == 0:
        return (
            "사람들은 일부만 흔들렸다. 큰 무너짐도, 분명한 회복도 보이지 않았다. "
            "그 어중간한 자리에서 시간은 평소보다 느리게 흘렀고, 누구도 분명한 자세를 잡지 못한 채 "
            "다음 일이 무엇인지 짐작만 하고 있었다."
        )
    if resp.get("n_no_shame", 0) > 0:
        return (
            "사람들은 별다른 동요 없이 머물렀다. 사건은 그들 사이로 지나갔지만, 깊게 박히지는 않았다. "
            "거리는 평소의 결을 유지하고 있었다."
        )
    return "사람들은 각자의 자리에서 사건을 받아들였다. 같은 사건이었지만 그 자리마다 무게는 달랐다."


def _turning_point(tp: dict) -> str:
    if tp["key"] == "turning_recovery":
        return "어느 순간, 무거움이 더 이상 자라지 않았다. 거리는 천천히 다시 숨을 쉬기 시작했다."
    if tp["key"] == "turning_saturation":
        fm = tp.get("failure_mode")
        if fm == "shame_cap":
            return "더 이상 올라갈 수 없는 곳까지 무거움이 차올랐다. 사람들은 그 자리에 갇혔다."
        if fm == "no_forgiveness_uptake":
            return "용서한다는 말은 오갔지만, 누구의 어깨에서도 짐은 내려지지 않았다."
        if fm == "crowd_blame_persists":
            return "사람들의 비난은 풀리지 않은 채 거리에 남았다."
        if fm == "repeat_retrigger":
            return "사건은 한 번으로 끝나지 않았다. 같은 일이 거듭되며 사람들의 무게는 깊어졌다."
        return "회복의 길은 끝내 열리지 않았다."
    if tp["key"] == "turning_split":
        return "갈라진 자리는 좁혀지지 않았다. 누구의 잘못도 분명히 가려지지 않은 채, 사람들은 서로 다른 결로 굳었다."
    if tp["key"] == "turning_partial":
        return "흔들림은 그치지 않았지만, 더 깊이 가라앉지도 않았다. 어중간한 자리에서 사람들은 멈췄다."
    if tp["key"] == "turning_none":
        return "큰 변화는 없었다. 사건이라 부를 만한 일도 없이, 시간은 흘러갔다."
    return "결정적인 순간은 분명하지 않았다."


# Gate 1 자율 cycle #2 — scenario-specific RECOVERY pools (cross-scenario differentiation)
SCENARIO_RECOVERY_POOLS = {
    "scarcity": [
        "곡식이 채워지지는 않았지만, 사람들은 다시 손을 마주잡았다. 부족함의 무게는 남았어도 의심의 무게는 풀렸다.",
        "시장과 빈민가 사이의 발걸음이 다시 자연스러워졌다. 곡식이 넉넉해진 것은 아니었지만, 사람들의 시선은 평소의 결로 돌아갔다.",
        "곡식 자루를 바라보는 눈빛은 여전히 무거웠지만, 그 무게는 더 이상 서로를 향하지 않았다.",
        "비어 있는 자루는 그대로였지만, 그 비어 있음을 두고 서로를 의심하지는 않았다.",
        "곡물 창고와 빈민가 사이의 시선이 다시 평소의 결로 돌아갔다. 무게는 남았지만 그 무게는 함께 짊어지는 것이었다.",
    ],
    "accusation": [
        # Cycle 1 + 3 — 일반 REC tone (회복 명시)
        "비난이 닿았던 자리에서도 사람들은 다시 일어섰다. 손가락질의 끝은 어딘가에서 풀려났다.",
        "광장과 안마당의 공기는 여전히 무거웠지만, 그 무거움은 누구의 어깨도 더는 누르지 않았다.",
        "거리의 시선은 여전히 한 방향으로 모였지만, 그 방향에서 더 이상 무엇도 떨어지지 않았다.",
        "한 번 입에 올랐던 이름이 천천히 거리에서 흩어졌다. 그 이름은 누구의 것도 아닌 것으로 돌아갔다.",
        "관청 안마당의 그림자가 옅어지고, 광장의 발걸음은 다시 평소의 결을 찾아갔다.",
        # Cycle 4 Patch G — sharpness coexistence (회복 명시 + 잔재 명시, Lee v2 약점 #4 직접 대응)
        "손가락질의 끝은 거두어졌지만, 그 끝에서 떨어진 잔영은 거리 위에 잠시 머물렀다.",
        "이름이 거리에서 흩어졌어도, 그 이름이 처음 떨어진 자리는 한 박자 더 무거운 결을 지녔다.",
        "광장의 시선은 다시 흩어졌다. 그러나 어떤 시선은 처음 향했던 자리에서 한 번 더 멈췄다가 풀렸다.",
        "비난의 무게는 풀렸지만, 그 무게가 닿았던 어깨에는 옅은 자국이 남았다.",
        "손가락이 거두어진 후에도 그 손가락이 향했던 방향은 거리 위에 한동안 그대로였다.",
    ],
    "sacred": [
        "기도가 끝난 자리에서 사람들은 천천히 다시 자리를 잡았다. 무엇이 일어났는지 분명히 옮길 수 있는 사람은 없었지만, 모두 자기 결로 돌아갔다.",
        "성전의 침묵이 거리까지 흘러나왔던 그 자리에서, 사람들은 어깨를 폈다.",
        "기도와 의심이 한 자리에 깊었던 시간이 지나고, 사람들의 호흡은 평소의 결을 되찾았다.",
        "성전 바깥뜰에 모였던 사람들이 천천히 자기 자리로 돌아갔다. 무릎을 꿇었던 자세는 풀렸지만, 그 자세의 결은 옅게 남았다.",
        "기도 소리가 거두어진 후에도 거리는 그 침묵의 결을 잠시 지녔다. 그러나 그 결은 사람들의 어깨를 누르지 않았다.",
    ],
}

# Cycle 3 Patch D — scenario × outcome SAT pools. Lee 의도 (CYCLE_2_PLAN §2.2):
# scarcity SAT = 물성/식량/손끝/창고 / accusation SAT = 시선/이름/소문/공적 공간 /
# sacred SAT = 기도/기적/침묵/믿음의 잔상.
SCENARIO_SATURATION_POOLS = {
    "scarcity": [
        "곡식 자루는 같은 자리에 그대로였다. 그 무게를 옮길 수 있는 손은 어디에도 없었다.",
        "시장의 가격은 멈춘 채로 며칠을 흘렀고, 빈 자루는 점점 더 무거워 보였다.",
        "곡물 창고의 문은 닫힌 채였다. 그 문을 여는 결정은 누구의 자리에서도 내려오지 않았다.",
        "빈손에 무엇을 채울지 묻는 사람은 없었다. 손은 그 자리에 그대로 비어 있었다.",
        "시장 끝자락의 자루들은 며칠째 풀리지 않았다. 그 매듭을 풀 결정은 어느 자리에서도 내려오지 않았다.",
    ],
    "accusation": [
        "한 번 입에 오른 이름은 거두어지지 않았다. 그 이름 위에 다른 시선들이 계속 쌓여 갔다.",
        "광장의 한 자리에 손가락질의 잔상이 남아 있었다. 시선이 그 자리를 비켜 가는 동안에도, 이름은 그곳에 머물렀다.",
        "소문은 자기 결로 굳었다. 한 번 형태를 잡은 후로는 누구의 손도 그것을 풀지 못했다.",
        "관청 안마당의 그림자가 거리 위에 그대로 얹혔다. 그 그림자가 옮겨지는 신호는 어디에서도 오지 않았다.",
        "한 사람의 이름이 거리의 결로 굳었다. 그 이름은 거두어지지 않은 채 다음 시각으로 넘어갔다.",
    ],
    "sacred": [
        "성전 안의 침묵은 거리의 침묵으로 이어졌다. 그 두 침묵이 한 자리에서 만난 후로 어느 쪽도 다시 흩어지지 않았다.",
        "기도의 끝에서도 사람들은 같은 자세로 머물렀다. 무엇이 일어났는지, 무엇이 일어나지 않았는지 누구도 분명히 옮기지 못한 채였다.",
        "사람들의 시선은 성전 쪽을 향한 채 멈춰 있었다. 그 시선이 거두어지는 신호는 어디에서도 오지 않았다.",
        "성전 바깥의 한 자리에서 한 사람이 무릎을 꿇은 채 일어나지 않았다. 그 자리는 그대로 굳었다.",
        "기도 소리가 들렸던 자리에서 사람들의 자세는 그대로였다. 그 자세를 풀어 줄 손은 어디에도 닿지 않았다.",
    ],
}

# Cycle 7 Patch K — primary motif closing line (coherence ring).
# Lee 미명시 영역 — over-engineering 위험 인지 후 작은 patch만. Probe별 primary motif을
# narrative 마지막 잔향으로 명시. additive only이라 rollback 단순.
SCENARIO_MOTIF_CLOSING_POOLS = {
    "scarcity": [
        "곡식의 무게는 거리의 결과 함께 한동안 머물렀다.",
        "시장의 결은 다음 시각으로 천천히 옮겨 갔지만, 그 결의 흔적은 옅게라도 남았다.",
        "곡물 창고를 향한 시선이 거두어진 후에도, 그 시선이 머물렀던 자리는 평소와 같지 않았다.",
        "자루의 무게는 누구의 손에서도 완전히 풀리지 않았다.",
        "빈손과 찬손 사이의 결은 다음 며칠을 천천히 흘러갔다.",
    ],
    "accusation": [
        "한 번 떨어진 이름의 자국은 거리 위에 그대로였다.",
        "손가락이 향했던 방향의 결은 다음 시각까지 옅게라도 남았다.",
        "광장의 시선이 다시 평소의 결을 찾은 후에도, 그 시선이 한 번 모였던 자리는 평소와 같지 않았다.",
        "이름의 무게는 거두어지지 않은 채 거리의 결과 함께 흘러갔다.",
        "관청 안마당의 그림자가 옮겨 간 후에도, 그 그림자의 결은 거리 위에 잠시 머물렀다.",
    ],
    "sacred": [
        "성전 쪽으로 향했던 시선의 결은 다음 시각까지 옅게 남았다.",
        "기도 소리가 거두어진 후에도, 그 소리가 머물렀던 자리는 평소와 같지 않았다.",
        "성전 바깥뜰의 자리는 모임이 흩어진 후에도 그 결을 잠시 지녔다.",
        "침묵의 결은 거리의 결과 함께 다음 시각으로 흘러갔다.",
        "기도와 의심이 한 자리에 깊었던 시간은 거리 위에 옅게라도 남았다.",
    ],
}


def _motif_closing(probe_id: str, pressure_type: str) -> str:
    """Cycle 7 Patch K: probe별 primary motif closing line — narrative coherence ring."""
    pool = SCENARIO_MOTIF_CLOSING_POOLS.get(pressure_type)
    if not pool:
        return ""
    return variant_pick(probe_id, f"motif_closing_{pressure_type}", pool)


# Cycle 5 Patch I — scene-level micro-action beat (additive Stage 2.5).
# Lee 의도 = "scene-level local action beats" — omniscient observer 흐름 안에 *concrete
# individual action* zoom-in moment 삽입. Stage 2 (pressure_arc 끝) 직후 + transition_to_response
# 직전 위치. LOW_ACTIVITY는 별도 branch이므로 영향 없음.
SCENARIO_MICRO_ACTION_POOLS = {
    "scarcity": [
        "한 사람이 자기 손을 잠시 내려다보았다가, 다시 거리 쪽으로 들어 올렸다.",
        "두 발걸음이 시장 쪽으로 향하다가 한 박자 늦게 멈췄다.",
        "누군가 자루의 매듭을 만지작거리다가 다시 손을 내려놓았다.",
        "한 사람이 거리 끝쪽을 한참 바라보다가 천천히 고개를 돌렸다.",
        "자루를 들었던 손이 한 박자 흔들리다가 다시 자리를 잡았다.",
    ],
    "accusation": [
        "한 사람의 눈이 평소보다 길게 한 자리에 머물렀다.",
        "두어 걸음이 한쪽으로 향하다가 한 박자 늦게 다른 쪽으로 옮겨 갔다.",
        "한 사람이 손을 들려다 멈추고, 그 손을 천천히 내려놓았다.",
        "누군가의 시선이 한 사람의 얼굴에서 떨어지지 않았다. 그 시선은 거두어지지 않았다.",
        "한 사람의 발걸음이 광장 한가운데에서 한 박자 머뭇거렸다.",
    ],
    "sacred": [
        "한 사람이 무릎을 꿇으려다, 다시 자세를 잡았다.",
        "두 손이 마주잡혔다가 천천히 풀렸다.",
        "한 사람의 시선이 성전 쪽을 향하다가 다시 거리 쪽으로 돌아왔다.",
        "누군가 입을 열려다 그대로 닫았다. 그 침묵이 거리까지 닿았다.",
        "한 사람이 한 걸음 앞으로 나아갔다가, 그 자리에 다시 멈춰 섰다.",
    ],
}


def _micro_action(probe_id: str, pressure_type: str) -> str:
    """Cycle 5 Patch I: scene-level micro-action beat (Stage 2.5 zoom-in)."""
    pool = SCENARIO_MICRO_ACTION_POOLS.get(pressure_type)
    if not pool:
        return ""
    return variant_pick(probe_id, f"micro_action_{pressure_type}", pool)


# Cycle 4 Patch H — scenario × outcome PARTIAL pools (대칭성 회복).
# Cycle 3에서 REC/SAT/MIXED는 추가했지만 PARTIAL은 누락. PARTIAL 톤 = "어중간한 결".
SCENARIO_PARTIAL_POOLS = {
    "scarcity": [
        "곡식의 무게는 일부 풀렸고, 일부는 그대로였다. 자루의 한 끝은 가벼워졌지만 다른 끝은 여전히 무거웠다.",
        "시장의 가격은 한 박자 흔들리다 멈췄다. 분명한 끝도, 분명한 시작도 없는 시간이 흘렀다.",
        "곡물 창고의 문은 한 번 열렸다가 다시 닫혔다. 그 사이에 무엇이 옮겨졌는지는 분명하지 않았다.",
        "빈손에 무엇인가 채워지는 듯하다가 다시 비워졌다. 어느 쪽도 분명한 결을 잡지 못했다.",
        "거리의 자루들은 일부만 풀렸다. 나머지는 그 자리에서 여전히 같은 무게로 머물렀다.",
    ],
    "accusation": [
        "손가락은 거두어졌지만, 그 손가락이 향했던 방향은 그대로였다. 어느 쪽도 분명한 결을 잡지 못했다.",
        "이름은 천천히 흩어지다 한 자리에서 멈췄다. 그 이름이 완전히 사라지지도, 완전히 굳지도 않은 채였다.",
        "광장의 시선은 일부 풀렸고, 일부는 그대로였다. 어떤 자리는 다시 평소의 결을 찾았고 어떤 자리는 한 박자 멈춘 채였다.",
        "비난의 무게는 한 번 가벼워졌다가 다시 무거워졌다. 분명한 회복도 분명한 굳음도 아닌 시간이 흘렀다.",
        "관청 안마당의 그림자는 옅어지다 다시 짙어졌다. 어느 쪽으로도 분명한 끝이 오지 않았다.",
    ],
    "sacred": [
        "기도는 끝났지만 그 자리의 침묵은 풀리지 않았다. 사람들의 자세는 어중간한 결로 머물렀다.",
        "성전 바깥뜰의 모임은 일부 흩어졌고, 일부는 그대로였다. 어느 쪽도 분명한 결을 잡지 못했다.",
        "성전 안의 침묵이 거리까지 흘러나왔다가 한 자리에서 멈췄다. 그 침묵이 풀리는 신호도, 더 깊어지는 신호도 오지 않았다.",
        "기도 소리는 한 번 거두어졌다가 다시 시작되었다. 그 사이에 사람들의 결은 어느 쪽으로도 분명히 기울지 않았다.",
        "성전 쪽으로 향한 시선은 일부 거두어졌고, 일부는 그대로였다. 두 결이 같은 거리 위에 머물렀다.",
    ],
}

# Cycle 3 Patch E — scenario × outcome MIXED pools. cohort split이 scenario별로
# 어떤 자리에서 갈라지는지 차별화.
SCENARIO_MIXED_POOLS = {
    "scarcity": [
        "곡식의 무게가 한쪽에서는 풀리고, 다른 쪽에서는 더 깊게 가라앉았다. 같은 거리에 두 결의 시간이 흘렀다.",
        "빈민가의 손은 다시 펴졌고, 곡물 창고의 어깨는 그대로였다. 한 사건이 두 자리에 다른 결을 남겼다.",
        "시장의 가격은 한쪽 끝에서는 흔들리지 않았고, 다른 쪽에서는 여전히 가벼워지지 않았다.",
        "한 자리의 손은 다시 자루를 들었고, 다른 자리의 손은 비어 있는 채였다. 두 자리가 같은 거리에 머물렀지만 다른 결로 흘렀다.",
        "곡식이 한쪽에서는 옮겨지기 시작했고, 다른 쪽에서는 그 자리에 그대로였다. 같은 거리 안에 두 결이 흘렀다.",
    ],
    "accusation": [
        "한쪽에서는 손가락이 거두어졌고, 다른 쪽에서는 그 손가락의 그림자가 그대로 남았다.",
        "이름이 풀려난 자리와 이름이 굳은 자리가 같은 거리 안에 있었다. 시선은 두 자리를 다르게 비추었다.",
        "광장의 한 끝에서는 사람들이 다시 모였고, 다른 끝에서는 손가락질의 잔상이 그대로였다.",
        "한 사람의 이름은 풀려났고, 다른 사람의 이름은 그대로 굳었다. 두 이름이 같은 거리 위에 머물렀지만 무게는 달랐다.",
        "관청 안마당에서는 그림자가 옅어졌고, 광장 끝에서는 그대로였다. 같은 사건이 두 자리에 다른 결을 남겼다.",
    ],
    "sacred": [
        "성전 안의 침묵과 바깥의 술렁임이 한 자리에서 갈라졌다. 같은 사건 아래에서도 두 결의 호흡이 흘렀다.",
        "기도가 닿은 자리와 기도가 닿지 않은 자리가 같은 거리 위에 머물렀다.",
        "성전 쪽으로 향한 어떤 시선은 다시 거두어졌고, 다른 시선은 그대로 그곳에 남았다.",
        "한 자리에서는 무릎을 꿇었던 사람이 일어섰고, 다른 자리에서는 그대로 머물렀다. 두 자세가 같은 거리에 있었지만 같은 결을 살지 않았다.",
        "성전 바깥뜰의 한 끝에서는 사람들이 다시 모였고, 다른 끝에서는 그대로 흩어진 채였다.",
    ],
}

OUTCOME_POOLS = {
    "RECOVERY_DOMINATED": [
        # Fallback (scenario unknown 또는 'mixed'/'other') — scenario-specific보다 일반적
        "사람들은 다시 일어섰다. 자리에 따라 빠르고 더딤은 달랐지만, 무거움은 빠져나갔다.",
        "거리는 천천히 자기 결을 되찾았다. 회복은 한꺼번에 오지 않았지만, 사람들은 분명히 다시 움직이고 있었다.",
        "흔들림은 가라앉았다. 누가 먼저랄 것도 없이 사람들의 어깨에서 무게가 풀렸다.",
    ],
    "SATURATION_DOMINATED": [
        "사람들은 자리에 머물렀다. 어떤 자리는 시간이 흘러도 풀리지 않았다.",
        "사람들은 그곳에서 움직이지 않았다. 시간이 그들 곁만 비켜 흐르는 듯했다.",
        "무거움은 자리를 차지한 채 떠나지 않았다. 며칠이 지나도 사람들의 자세는 같았다.",
    ],
    "MIXED": [
        "한쪽은 회복했고, 다른 쪽은 굳었다. 같은 사건이 사람들에게 다른 모양을 남겼다.",
        "같은 사건 아래에서도 사람들의 결은 둘로 갈렸다. 한 자리는 다시 숨을 쉬었고, 다른 자리는 굳어 있었다.",
        "사건은 하나였지만, 그것이 남긴 자국은 두 가지였다. 누구는 일어섰고 누구는 그대로 있었다.",
    ],
    "PARTIAL": [
        "사람들은 어딘가에서 멈춰 있었다. 회복도 무너짐도 분명하지 않았다.",
        "흔들림은 그 자리에서 더 자라지도, 풀리지도 않았다. 어중간한 시간이 며칠을 채웠다.",
        "분명한 끝은 보이지 않았다. 사람들은 가만히 그 자리에 서 있었다.",
    ],
    "LOW_ACTIVITY": [
        "사건이라 할 만한 것은 없었다. 거리는 평소처럼 흘러갔다.",
        "거리는 평소와 다르지 않았다. 무엇이 시작되었는지조차 분명하지 않은 시간이었다.",
    ],
}

# J-Alpha Step A5 우선 항목 1: Ending hook pool (소설적 여운)
ENDING_HOOK_POOLS = {
    "RECOVERY_DOMINATED": [
        "다만 누구도 그 무거움이 정말 사라졌다고 확신하지는 못했다.",
        "그러나 풀린 어깨에서도 어떤 자세는 남아 있었다.",
        "회복은 끝이 아니라 또 다른 시작의 형태였다.",
    ],
    "SATURATION_DOMINATED": [
        "그러나 그 굳음 안에서도 작은 떨림이 멈추지 않았다.",
        "어떤 자리는 며칠이 지난 뒤에야 미세하게 움직였다.",
        "굳었지만 완전히 잠든 것은 아니었다.",
    ],
    "MIXED": [
        "그 갈림은 다음 며칠 동안 어느 한쪽으로도 분명히 기울지 않았다.",
        "두 결의 시간 사이에 누구도 분명한 자리를 잡지 못했다.",
        "어느 쪽이 옳았는지는 끝내 분명해지지 않았다.",
    ],
    "PARTIAL": [
        "그 어중간한 자리에서 사람들은 다음을 짐작만 하고 있었다.",
        "분명한 끝이 오지 않은 채 시간은 한 걸음씩 흘렀다.",
    ],
    "LOW_ACTIVITY": [
        "그러나 그 평온이 영원하지는 않으리라는 예감만은 어디선가 자라고 있었다.",
        "조용함 너머의 것은 아직 누구도 보지 못했다.",
    ],
}


def _outcome(out: dict, probe_id: str = "", pressure_type: str = "") -> str:
    fs = out["final_summary"]
    # Gate 1 자율 cycle #2: scenario-specific recovery pool first, fallback to OUTCOME_POOLS
    # Cycle 3 Patch D + E: SAT + MIXED도 scenario-specific pool 추가
    pool = None
    if fs == "RECOVERY_DOMINATED" and pressure_type in SCENARIO_RECOVERY_POOLS:
        pool = SCENARIO_RECOVERY_POOLS[pressure_type]
    elif fs == "SATURATION_DOMINATED" and pressure_type in SCENARIO_SATURATION_POOLS:
        pool = SCENARIO_SATURATION_POOLS[pressure_type]
    elif fs == "MIXED" and pressure_type in SCENARIO_MIXED_POOLS:
        pool = SCENARIO_MIXED_POOLS[pressure_type]
    elif fs == "PARTIAL" and pressure_type in SCENARIO_PARTIAL_POOLS:
        pool = SCENARIO_PARTIAL_POOLS[pressure_type]
    if pool is None:
        pool = OUTCOME_POOLS.get(fs)
    hook_pool = ENDING_HOOK_POOLS.get(fs)
    if not pool:
        return "마지막 자리는 분명하지 않았다."
    base = variant_pick(probe_id, f"outcome_{fs}_{pressure_type}", pool)
    if hook_pool:
        hook = variant_pick(probe_id, f"hook_{fs}", hook_pool)
        return f"{base} {hook}"
    return base


# Cycle 2 Patch A3: authority_residue 단일 문장 → outcome × pressure × probe별
# 다양화. Lee 식별 stock phrase 3 ("권위의 시선도 거두어지지 않았다")의 반복 차단.
AUTHORITY_RESIDUE_POOLS = {
    "RECOVERY_DOMINATED": [
        "권위의 시선은 거리 위에 머물렀지만, 그 시선의 무게는 더 이상 사람들의 어깨를 누르지 않았다.",
        "권위는 자리를 떠나지 않았다. 다만 그 자리에서 거리를 바라보는 결이 한 박자 부드러워졌다.",
        "권위의 자리는 그대로였지만, 그 자리에서 내려오는 공기는 평소의 결을 되찾고 있었다.",
    ],
    "SATURATION_DOMINATED": [
        "권위의 시선도 거두어지지 않았다. 시선이 닿는 자리에는 평소보다 느린 호흡이 깔렸다.",
        "권위는 같은 자리에서 같은 결로 거리를 내려다보았다. 그 시선 아래에서는 누구의 자세도 풀리지 않았다.",
        "권위의 무게는 며칠이 지나도 같은 자리에 그대로였다. 그 무게가 사라진다는 신호는 어디에서도 오지 않았다.",
    ],
    "MIXED": [
        "권위의 시선은 두 자리 모두에 닿았지만, 그 시선이 무엇을 보고 있는지는 자리에 따라 다르게 읽혔다.",
        "권위는 거리의 한쪽 결과 다른 쪽 결을 동시에 지켜보았다. 어느 쪽으로도 분명히 기울지 않았다.",
        "권위의 시선은 그대로였다. 그러나 그 시선 아래에서 두 자리는 다른 자세로 머물렀다.",
    ],
    "PARTIAL": [
        "권위의 시선은 어중간한 자리에 옅게 닿았다. 무엇을 단단히 누르지도, 풀어 주지도 않은 채였다.",
        "권위는 거기 있었지만, 그 자리에서 무엇을 바꾸지는 않았다.",
    ],
    "LOW_ACTIVITY": [
        "권위의 자리는 채워져 있었지만, 그 자리에서 내려오는 시선은 어느 곳에도 분명히 닿지 않았다.",
        "권위는 거기 있었다. 다만 어떤 사건도 그 시선을 향해 자라지 않았다.",
    ],
}


def _aftereffect(af: dict, probe_id: str = "", final_summary: str = "MIXED") -> str:
    parts = []
    if af.get("suspicion_strong_residue"):
        parts.append("의심은 거리 위에 짙게 남았고, 며칠이 지나도 가벼워지지 않았다. 사람들의 인사는 짧아졌고, 시선은 더 빨리 비켜갔다.")
    elif af.get("suspicion_residue"):
        parts.append("의심의 흔적은 옅게라도 거리 위에 머물렀다. 잠시 사라진 듯 보일 때도, 누군가의 발걸음에서 그것이 다시 살아났다.")
    if af.get("authority_residue"):
        auth_pool = AUTHORITY_RESIDUE_POOLS.get(final_summary) or AUTHORITY_RESIDUE_POOLS["MIXED"]
        parts.append(variant_pick(probe_id, f"authority_residue_{final_summary}", auth_pool))
    if af.get("blame_strong_residue"):
        parts.append("비난의 무게는 어깨 위에 그대로 얹혀 있었다. 누구의 손도 그것을 들어 주지 못했다.")
    elif af.get("blame_residue"):
        parts.append("비난은 가볍게라도 사람들 사이를 떠다녔다. 그것은 누구의 것도 아니었지만, 누구든 닿으면 흔적이 남았다.")
    if af.get("shame_residue_count", 0) > 0:
        # Cycle 2 Patch B3: shame residue 마무리도 outcome별 분기
        if final_summary == "SATURATION_DOMINATED":
            parts.append("가장 무거웠던 자리들은 그 무게를 내려놓지 못했다. 시간이 그곳만 비켜 흘러간 듯, 같은 침묵이 며칠을 이어졌다.")
        elif final_summary == "RECOVERY_DOMINATED":
            parts.append("가장 무거웠던 자리에서도 사람들은 천천히 어깨를 폈다. 다만 그 어깨에서 떨림이 완전히 가시지는 않았다.")
        elif final_summary == "MIXED":
            parts.append("가장 무거웠던 자리들 중 어떤 곳은 풀렸고, 어떤 곳은 그대로였다. 두 자리가 같은 거리에 머물렀지만, 같은 결의 시간을 살지 않았다.")
        else:
            parts.append("가장 무거웠던 자리들은 분명한 결을 잡지 못한 채 거리 위에 그대로 머물렀다.")
    if not parts:
        parts.append("거리는 천천히 다시 평소의 모양으로 돌아갔다. 그 흔적이 어딘가에 남았더라도, 사람들의 눈에는 잘 보이지 않았다.")
    return " ".join(parts)


# ============================================================
# Compose summary (Type 1 — 400-800자, 건조한 서사형)
# ============================================================

# Cycle 2 Patch C: LOW_ACTIVITY 전용 분기. Lee 의도 — "아무 일 없음"이 아니라
# "무언가 일어날 수 있었지만 끝내 일어나지 않음" 으로 처리. 5 요소: 작은 징후
# 2-3개 / 확산 안 되는 rumor / 반응 안 하는 crowd / 무심한 authority / 사건 못 됨 tension.
LOW_ACTIVITY_SIGN_POOL = [
    "한 사람이 잠시 발을 멈췄다가 다시 걸어갔다.",
    "어떤 자리에서는 평소보다 길게 머무는 사람들이 있었다.",
    "거리 한쪽 끝에서 작은 술렁임이 일었지만, 그 술렁임은 바로 가라앉았다.",
    "누군가 무엇인가를 말하려다 입을 다물었다.",
    "두어 사람의 시선이 같은 자리에 짧게 머물렀다가 흩어졌다.",
    "걸음의 결이 한 박자 어긋난 사람이 있었지만, 다시 평소의 결로 돌아왔다.",
]

LOW_ACTIVITY_RUMOR_POOL = [
    "한 사람이 말을 시작했지만, 두 번째 사람에게는 닿지 않았다. 소문은 거리 끝까지 가지 못했다.",
    "누군가의 말이 공기 중에 잠시 떠올랐다가 그대로 흩어졌다. 그 말을 따라간 사람은 없었다.",
    "소문은 한 자리에서만 돌았고, 옆 자리로 넘어가지 못했다. 그 이유를 묻는 사람도 없었다.",
]

LOW_ACTIVITY_CROWD_POOL = [
    "사람들의 발걸음은 평소처럼 흘렀다. 누구도 그 작은 술렁임을 향해 고개를 돌리지 않았다.",
    "거리는 평소의 결을 유지했고, 누구도 그것을 깨려 하지 않았다. 모이는 자리도, 흩어지는 자리도 만들어지지 않았다.",
    "사람들은 모두 자기 자리에 있었지만, 어디에도 모이지 않았다. 거리 위의 작은 흔들림은 누구의 결도 흔들지 못했다.",
]

LOW_ACTIVITY_AUTHORITY_POOL = [
    "권위의 시선은 다른 곳에 있었다. 거리 위의 작은 흔들림은 그 시선에 닿지 않았다.",
    "권위는 거기 있었지만, 보아야 할 것을 보지 않았다. 시선은 한 박자 늦게도 따라오지 않았다.",
    "권위의 자리는 비어 있는 듯도 했고 채워져 있는 듯도 했다. 분명한 것은 어떤 시선도 그곳에서 내려오지 않았다는 것이다.",
]

LOW_ACTIVITY_NON_EVENT_POOL = [
    "그것은 끝내 사건이 되지 못했다. 그러나 그렇기 때문에 거리에는 다른 종류의 무게가 깔렸다.",
    "무엇이 시작될 수 있었는지는 누구도 분명히 말하지 못했다. 다만 그것이 시작되지 않았다는 사실만이 남았다.",
    "사건은 자라기 직전에 멈췄고, 그 멈춤은 그 자체로 한 종류의 흔적을 남겼다.",
]


def _render_narrative_low_activity(ir: dict) -> str:
    """Patch C: LOW_ACTIVITY 전용 5-stage narrative — '부재의 긴장'."""
    pid = ir.get("probe_id", "")

    # Stage 1: 도입 — 평소 같은 거리 + 작은 징후 2-3개
    opening = _opening(ir["world_opening"], "other", "low_activity", pid)
    # variant_pick 2 different signs (slot으로 분리)
    sign_a = variant_pick(pid, "low_sign_a", LOW_ACTIVITY_SIGN_POOL)
    # second pool excluding first chosen
    remaining = [s for s in LOW_ACTIVITY_SIGN_POOL if s != sign_a]
    sign_b = variant_pick(pid, "low_sign_b", remaining or LOW_ACTIVITY_SIGN_POOL)
    s1 = f"{opening} {sign_a} {sign_b}"

    # Stage 2: 확산 안 되는 rumor
    s2 = variant_pick(pid, "low_rumor", LOW_ACTIVITY_RUMOR_POOL)

    # Stage 3: 반응 안 하는 crowd
    s3 = variant_pick(pid, "low_crowd", LOW_ACTIVITY_CROWD_POOL)

    # Stage 4: 무심한 authority
    s4 = variant_pick(pid, "low_authority", LOW_ACTIVITY_AUTHORITY_POOL)

    # Stage 5: 사건이 되지 못한 tension
    s5 = variant_pick(pid, "low_non_event", LOW_ACTIVITY_NON_EVENT_POOL)

    return "\n\n".join([s1, s2, s3, s4, s5])


def _render_summary_low_activity(ir: dict) -> str:
    """Patch C: LOW_ACTIVITY summary — narrative의 압축 버전 (3 stage)."""
    pid = ir.get("probe_id", "")
    opening = _opening(ir["world_opening"], "other", "low_activity", pid)
    sign = variant_pick(pid, "low_sign_summary", LOW_ACTIVITY_SIGN_POOL)
    crowd = variant_pick(pid, "low_crowd_summary", LOW_ACTIVITY_CROWD_POOL)
    non_event = variant_pick(pid, "low_non_event_summary", LOW_ACTIVITY_NON_EVENT_POOL)
    return f"{opening} {sign}\n\n{crowd}\n\n{non_event}"


def render_summary(ir: dict) -> str:
    fs = ir["outcome"].get("final_summary", "MIXED")
    if fs == "LOW_ACTIVITY":
        return _render_summary_low_activity(ir)

    pressure = ir["initial_tension"].get("key", "")
    pressure_type = "scarcity" if "scarcity" in pressure else (
        "accusation" if "accusation" in pressure else (
            "sacred" if "sacred" in pressure else "other"
        )
    )
    pid = ir.get("probe_id", "")
    paragraphs = []
    paragraphs.append(_opening(ir["world_opening"], pressure_type, ir["dominant_mode"], pid))
    paragraphs.append(_initial_tension(ir["initial_tension"]))
    paragraphs.append(_pressure_arc(ir["pressure_arc"], pressure_type))
    paragraphs.append(_group_response(ir["group_response"]))
    paragraphs.append(_outcome(ir["outcome"], pid, pressure_type))
    return "\n\n".join(p for p in paragraphs if p.strip())


# ============================================================
# Compose narrative (Type 2 — 1000-1800자, 감정 서사형, 5단 구조)
# ============================================================

TRANSITION_TO_PRESSURE = [
    "그러나 그 자리에 머무를 수만은 없는 일이 곧 일어났다.",
    "그 공기가 깊어지기 전, 거리에 작은 사건이 떨어졌다.",
    "그리고 이내, 모두의 시선이 한 자리로 쏠리는 일이 벌어졌다.",
]

TRANSITION_TO_RESPONSE = [
    "그러나 사람들의 반응은 한 결이 아니었다.",
    "사람들의 결은 그 무게 아래에서 갈라지기 시작했다.",
    "이 흐름 속에서, 사람들은 각자 다른 자리에서 다른 호흡을 가졌다.",
]

# Cycle 2 Patch A1+B1: outcome-conditional transition (was flat list — Lee
# identified "그리고 그 모든 결은 결국 한 모양으로 굳어 갔다." as stock phrase
# repeated across all outcomes). Now MIXED keeps the "한 모양으로 굳어" image,
# SAT closes inward, REC opens outward, PARTIAL stays ambiguous.
TRANSITION_TO_OUTCOME_BY_FS = {
    "RECOVERY_DOMINATED": [
        "그 흐름이 어디까지 닿을지가 다음 며칠의 호흡을 결정했다.",
        "이 풀림이 정말 풀림이었는지, 아니면 다음 무거움을 위한 잠시였는지는 분명하지 않았다.",
        "거리의 결이 다시 평소를 향해 옮겨 가고 있었다.",
    ],
    "SATURATION_DOMINATED": [
        "그 자리에서 시간은 더 이상 앞으로 나아가지 않았다.",
        "흐름이 멈춘 자리에서 다음을 묻는 사람은 없었다.",
        "사람들은 그곳에 머문 채, 다음을 기다리지 않았다.",
    ],
    "MIXED": [
        "그리고 그 모든 결은 결국 한 모양으로 굳어 갔다.",
        "두 결의 시간이 동시에 흐르며, 거리는 한 자리로 모이지 못했다.",
        "한 사건의 끝이 두 자리에서 다르게 닫혀 가고 있었다.",
    ],
    "PARTIAL": [
        "그 갈림의 끝은 한 점에서 모이지 않았다.",
        "어중간한 결이 거리 위에 그대로 머물렀다.",
        "회복도 무너짐도 자기 자리를 분명히 잡지 못한 시간이었다.",
    ],
    "LOW_ACTIVITY": [
        "그러나 무엇도 그 다음으로 자라지 않았다.",
        "흐름은 시작되기 전에 이미 가라앉고 있었다.",
        "사건이 될 뻔한 것이 사건이 되지 못한 채 흘러갔다.",
    ],
}

# Cycle 2 Patch A2+B3: outcome-conditional aftereffect transition. SAT은 잔류
# 강조, REC은 회복의 잔향, MIXED는 두 결, PARTIAL은 미완 감, LOW_ACTIVITY는
# 부재의 여운. 기존 "며칠이 지난 뒤..." 는 SAT 한정으로만 보존.
TRANSITION_TO_AFTEREFFECT_BY_FS = {
    "RECOVERY_DOMINATED": [
        "다음 날의 아침이 밝았을 때, 거리는 평소의 결로 돌아간 듯 보였지만 어딘가는 달라져 있었다.",
        "풀린 어깨가 다시 굽지 않을지를 누구도 묻지 않았다. 다만 그 어깨를 따라 거리가 함께 폈다.",
        "회복이 지나간 자리에는 그 회복의 흔적이 옅게라도 남아 있었다.",
    ],
    "SATURATION_DOMINATED": [
        "며칠이 지난 뒤, 사건이 끝난 자리에는 무언가가 남아 있었다.",
        "굳은 자리가 풀리지 않은 채로 시간만 흘렀다.",
        "그 침묵이 길어질수록, 거리는 그 침묵의 일부가 되어 갔다.",
    ],
    "MIXED": [
        "그 자리가 비워지고 며칠이 지나, 사건의 마지막 글자가 닫혀도, 거리는 그것을 완전히 잊지 못했다.",
        "한 자리의 회복과 다른 자리의 굳음이 같은 거리에 함께 머물렀다.",
        "두 결의 시간이 한 거리 위에서 천천히 다른 결로 멀어져 갔다.",
    ],
    "PARTIAL": [
        "그날 저녁이 깊어 가고 난 뒤에도, 거리는 그 흔적을 안고 흘렀다.",
        "분명하지 않은 끝이 거리 위에 그대로 얹혀 있었다.",
        "어떤 자세도 분명하지 않은 채로 다음 시각이 왔다.",
    ],
    "LOW_ACTIVITY": [
        "사건이 되지 못한 무엇이 거리 위에 옅게라도 남아 있었다.",
        "일어나지 않은 것이 일어난 것보다 더 무겁게 자리를 차지한 시간이었다.",
        "그 부재가 곧 한 종류의 흔적이 되어 갔다.",
    ],
}


def _transition_to_outcome(probe_id: str, fs: str) -> str:
    pool = TRANSITION_TO_OUTCOME_BY_FS.get(fs) or TRANSITION_TO_OUTCOME_BY_FS["MIXED"]
    return variant_pick(probe_id, f"transition_to_outcome_{fs}", pool)


def _transition_to_aftereffect(probe_id: str, fs: str) -> str:
    pool = TRANSITION_TO_AFTEREFFECT_BY_FS.get(fs) or TRANSITION_TO_AFTEREFFECT_BY_FS["MIXED"]
    return variant_pick(probe_id, f"transition_to_aftereffect_{fs}", pool)


def render_narrative(ir: dict) -> str:
    """5-stage structure with extra detail."""
    fs = ir["outcome"].get("final_summary", "MIXED")
    if fs == "LOW_ACTIVITY":
        return _render_narrative_low_activity(ir)

    pressure = ir["initial_tension"].get("key", "")
    pressure_type = "scarcity" if "scarcity" in pressure else (
        "accusation" if "accusation" in pressure else (
            "sacred" if "sacred" in pressure else "other"
        )
    )
    pid = ir.get("probe_id", "")

    # Stage 1: 도입
    s1 = _opening(ir["world_opening"], pressure_type, ir["dominant_mode"], pid)
    s1 += " " + variant_pick(pid, "transition_to_pressure", TRANSITION_TO_PRESSURE)
    # Stage 2: 압력 상승
    s2 = _initial_tension(ir["initial_tension"]) + " " + _pressure_arc(ir["pressure_arc"], pressure_type)
    # Stage 3: 반응 분기
    s3 = _group_response(ir["group_response"])
    # Stage 3 detail: cohort-specific (D-1: 의미 location names)
    cohort_detail = []
    cohorts = ir["group_response"].get("cohorts_detail", [])
    rec_cohort = next((c for c in cohorts if c["arc"] == "recovery"), None)
    sat_cohort = next((c for c in cohorts if c["arc"] == "saturation"), None)
    par_cohort = next((c for c in cohorts if c["arc"] == "partial"), None)
    if rec_cohort and sat_cohort:
        rec_loc = rec_cohort.get("location_name", "한쪽")
        sat_loc = sat_cohort.get("location_name", "다른 자리")
        cohort_detail.append(
            f"{rec_loc}에서는 누군가의 입에서 시작된 고백이 다음 사람으로 넘어갔고, "
            f"그 흐름이 짐을 조금씩 덜어 갔다. {sat_loc}에서는 같은 말이 오가도 "
            "누구의 어깨에서도 짐이 풀리지 않았다. 두 자리는 가까이 있었지만, 다른 결의 시간이 흘렀다."
        )
    elif sat_cohort and not rec_cohort:
        sat_loc = sat_cohort.get("location_name", "어떤 자리")
        # micro-variation by saturation count
        n_sat = ir["group_response"].get("n_saturation", 1)
        if n_sat >= 3:
            cohort_detail.append(
                f"{sat_loc}만이 아니었다. 같은 침묵이 여러 자리에 동시에 깔렸고, "
                "사람들은 어디서도 자기 자리를 떠나지 못했다."
            )
        else:
            cohort_detail.append(
                f"{sat_loc}에서는 사람들이 그저 그 자리에 머물렀다. "
                "고백도 외침도 그곳까지 닿지 않았고, 시간은 그 자리만 비켜 흐르는 듯했다."
            )
    elif rec_cohort and not sat_cohort:
        rec_loc = rec_cohort.get("location_name", "거리 한쪽")
        cohort_detail.append(
            f"{rec_loc}의 사람들은 흩어진 듯 보였지만, 한 사람이 입을 열자 다른 입들도 따라 열렸다. "
            "이 흐름은 한쪽에서 다른 쪽으로 천천히 번져 갔다."
        )
    elif par_cohort:
        par_loc = par_cohort.get("location_name", "그 자리")
        cohort_detail.append(
            f"{par_loc}의 사람들은 분명한 자리를 잡지 못했다. 떨어지지도, 다시 일어서지도 못한 채 어중간한 곳에서 머물렀다."
        )
    # Stage 4: 귀결
    s4 = _turning_point(ir["turning_point"]) + " " + _outcome(ir["outcome"], pid, pressure_type)
    # Stage 5: 사후 세계 (Cycle 2 Patch B3: outcome-aware)
    s5 = _aftereffect(ir["world_aftereffect"], pid, fs)

    # Cycle 5 Patch I: scene-level micro-action beat (Stage 2.5 zoom-in)
    micro = _micro_action(pid, pressure_type)
    if micro:
        s2 = s2 + " " + micro

    # Cycle 2 Patch A1+A2: outcome-conditional transitions (was flat list).
    s2_with_transition = s2 + " " + variant_pick(pid, "transition_to_response", TRANSITION_TO_RESPONSE)
    s3_extended = s3
    if cohort_detail:
        s3_extended += "\n\n" + "\n\n".join(cohort_detail)
    s3_with_transition = s3_extended + "\n\n" + _transition_to_outcome(pid, fs)
    s4_with_transition = s4 + " " + _transition_to_aftereffect(pid, fs)

    paragraphs = [s1]
    paragraphs.append(s2_with_transition)
    paragraphs.append(s3_with_transition)
    paragraphs.append(s4_with_transition)
    paragraphs.append(s5)
    # Cycle 7 Patch K — Stage 6: motif coherence ring (narrative 마지막 잔향)
    motif_closing = _motif_closing(pid, pressure_type)
    if motif_closing:
        paragraphs.append(motif_closing)
    return "\n\n".join(p for p in paragraphs if p.strip())


# ============================================================
# CLI
# ============================================================

def process(probe_id: str) -> tuple[str, str]:
    ir_path = IR_DIR / f"{probe_id}.json"
    if not ir_path.exists():
        raise FileNotFoundError(f"IR not found: {ir_path}")
    ir = json.loads(ir_path.read_text(encoding="utf-8"))
    summary = render_summary(ir)
    narrative = render_narrative(ir)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"{probe_id}_summary_ko.txt").write_text(summary, encoding="utf-8")
    (OUT_DIR / f"{probe_id}_narrative_ko.txt").write_text(narrative, encoding="utf-8")
    return summary, narrative


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python scripts/story/render_story_ko.py <P_id|--all>")
        return 2

    if sys.argv[1] == "--all":
        for n in range(1, 13):
            probe_id = f"P{n}"
            try:
                s, narr = process(probe_id)
                print(f"  {probe_id}: summary={len(s)}자, narrative={len(narr)}자")
            except FileNotFoundError:
                print(f"  {probe_id}: skipped")
    elif sys.argv[1] == "--branch-c":
        for prefix in ["P_PV", "P_CV", "P_ED", "P_S2"]:
            for n in range(1, 10):
                probe_id = f"{prefix}_{n:02d}"
                try:
                    s, narr = process(probe_id)
                    print(f"  {probe_id}: summary={len(s)}자, narrative={len(narr)}자")
                except FileNotFoundError:
                    print(f"  {probe_id}: skipped")
    else:
        s, narr = process(sys.argv[1])
        print("=== Summary (Type 1) ===")
        print(s)
        print()
        print("=== Narrative (Type 2) ===")
        print(narr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
