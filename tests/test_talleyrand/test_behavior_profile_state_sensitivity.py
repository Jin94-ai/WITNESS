"""Talleyrand behavior_profile state sensitivity diagnostic (Iter 69-70).

Iter 69 발견: 원래 profile (base 2.5-3.0, multipliers 0.1-0.2)에서
state→action 예측이 majority 수준 (학습 불가능).

Iter 70 조치: base 낮추고 multipliers scale 키움 (0.4-0.9 범위).
empirical 재측정: majority 0.535 → logit acc 0.551 (+1.6%, marginal).

**finding**: base_weight dominance 해소는 필요조건이지만 충분조건 아님.
주요 bottleneck은 (a) 5개 action만 존재, (b) regime 전환 이벤트로 state가
discrete-step으로 reset되어 intra-regime 학습 signal이 약함.

Stage 2 학습이 의미 있으려면 Talleyrand scenario에 추가 조치 필요:
- 더 많은 action 종류 (currently 5 → 7-10)
- state-varying 중간 canonical events (regime 전환 사이에 "특정 대사
  파견", "책 출간" 같은 이벤트)
- state_noise_scale 증가로 intra-regime 탐색 다양성
"""

from __future__ import annotations

import json
from pathlib import Path

CONTENT = Path(__file__).resolve().parent.parent.parent / "content"


def _profile():
    return json.loads(
        (CONTENT / "talleyrand" / "behavior_profile.json").read_text(encoding="utf-8"),
    )


class TestCurrentProfileState:
    """Iter 70 post-retuning profile state를 lock-in.

    base_weight와 multiplier scale이 더 이상 극단적 불균형이 아님.
    """

    def test_base_weights_moderated(self):
        """Iter 70: base_weights 0.2~1.0 범위 (Iter 69의 2.5-3.0 에서 감소)."""
        p = _profile()
        bases = [a["weight_formula"]["base_weight"] for a in p["actions"]]
        assert max(bases) <= 1.2, "Iter 70 튜닝 이후 base ≤ 1.2 권장"
        assert min(bases) > 0

    def test_multiplier_scales_meaningful(self):
        """Iter 70: multipliers scale ≥ 0.4 (Iter 69의 0.1-0.2 에서 증가)."""
        p = _profile()
        seen_large_scale = False
        for action in p["actions"]:
            for mult in action["weight_formula"].get("state_multipliers", []):
                scale = mult["params"].get("scale", 0.0)
                if scale >= 0.4:
                    seen_large_scale = True
        assert seen_large_scale, (
            "모든 multiplier scale < 0.4. 이는 Iter 69 원래 상태로 되돌아간 것. "
            "Iter 70 튜닝 의도 유실. lessons 17 업데이트 필요."
        )


class TestDocumentedLimitation:
    """Iter 69-70 발견의 permanent 기록."""

    def test_iter_69_finding_documented(self):
        lessons = (
            Path(__file__).resolve().parent.parent.parent / "lessons.md"
        ).read_text(encoding="utf-8")
        assert ("Iter 69" in lessons) or ("behavior_profile" in lessons and "state sensitivity" in lessons)
