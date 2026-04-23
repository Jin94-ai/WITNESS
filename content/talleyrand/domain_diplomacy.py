"""Talleyrand의 도메인 상태: 외교·생존 협상 심리.

3번째 시나리오 — ChatGPT 외부 리뷰 권장: Witness 엔진의 약점인
**협상/장기 정치 계산/점진적 구조 변화**를 시험하기 위한 Type A (협상형) 인물.

Peter(누적→임계→rare action)나 Van Gogh(좌절→결별)와 구조적으로 다름:
- 단일 결정적 사건 없이 **다체제 전환 속 지속 협상**이 동역학의 본질
- Ancien régime → 혁명 → Napoleon → 부르봉 복고 → 7월왕정 5 regime 생존
- "배반처럼 보이지만 사실은 체제 간 이동을 통한 지속적 적응"

도메인 state 축 (POM용):
- regime_alignment: 현 체제에 대한 공개적 충성도 (얼마나 드러내는가)
- leverage: 협상력 (정보, 인맥, 대체 불가능성)
- legitimacy_anchor: 내재적 정당성 vs 실용주의 기반
- reputation_ambiguity: 동시대가 느끼는 "배반자 vs 현실주의자" 평가 분산
- survival_streak: 현 체제에서의 연속 생존 tick
- network_depth: 다중 체제 인맥망 깊이
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from engine.core.state import DomainState  # noqa: I001

RegimeType = Literal[
    "ancien_regime",
    "revolution",
    "directory",
    "consulate",
    "empire",
    "bourbon_restoration",
    "july_monarchy",
]

AlignmentStance = Literal[
    "overt_loyal",       # 공공연한 충성 표명
    "pragmatic_serve",   # 실용적 봉사 (충성 표명 유보)
    "covert_maneuver",   # 은밀한 반체제 협상
    "strategic_exit",    # 체제 이탈 준비 중
    "post_regime",       # 체제 붕괴 후 재정렬 대기
]


class DiplomacyState(DomainState):
    """탈레랑 류 협상가의 도메인 상태.

    Peter/VG와 달리 단일 bottleneck 이벤트가 아닌 **지속적 균형 유지**를
    모델링. 체제 전환(regime change)은 hazard/canonical event로 들어오고,
    이 state는 에이전트의 선택적 반응을 기록.
    """

    type: str = Field(default="diplomacy", init=False)

    # 현 체제 관련
    current_regime: RegimeType = Field(
        default="ancien_regime",
        description="에이전트가 현재 활동하는 정치 체제.",
    )
    alignment_stance: AlignmentStance = Field(
        default="pragmatic_serve",
        description="현 체제에 대한 가시적 태도.",
    )
    survival_streak_ticks: float = Field(
        default=0.0, ge=0.0,
        description="현 체제에서의 연속 활동 tick (체제 바뀌면 0으로 reset).",
    )

    # 협상력
    leverage: float = Field(
        default=5.0, ge=0.0, le=10.0,
        description="협상력. 정보·인맥·대체 불가능성의 종합.",
    )
    legitimacy_anchor: float = Field(
        default=4.0, ge=0.0, le=10.0,
        description=(
            "내재적 정당성 (가문/직함/원칙 기반). 실용주의 협상가는 낮음. "
            "높을수록 '원칙'으로 행동, 낮을수록 '실용'."
        ),
    )

    # 대중 평판 (ambiguity가 핵심 — betray vs adapt 해석이 분산)
    reputation_ambiguity: float = Field(
        default=5.0, ge=0.0, le=10.0,
        description=(
            "동시대 평가의 분산도. 0=단일 해석(충신 혹은 배반자), "
            "10=해석 극단적 분산. 협상가의 생존 자원."
        ),
    )

    # 인맥망
    network_depth: float = Field(
        default=3.0, ge=0.0, le=10.0,
        description=(
            "다중 체제 교차 인맥망 깊이. 한 regime에 매인 적이 없을수록 높음. "
            "체제 전환 시 재배치 옵션 수 ≈ network_depth."
        ),
    )
    network_regime_span: int = Field(
        default=1, ge=1, le=7,
        description="인맥이 걸쳐 있는 regime 수. 최대는 Literal 총 regime 수.",
    )

    # 부정적 slow state (협상가도 한계 있음)
    moral_fatigue: float = Field(
        default=0.0, ge=0.0, le=10.0,
        description=(
            "다중 충성 유지의 누적 피로. moral_injury와 다름 — 원칙 위반이 "
            "아니라 '원칙 부재' 자체의 피로. Van Gogh의 isolation과도 다름."
        ),
    )
    compromise_count: int = Field(
        default=0, ge=0,
        description="이벤트-관측된 타협 횟수 (누적).",
    )

    # ------------------------------------------------------------------
    # v1.0 Stage 2: domain feature extractor (Iter 67)
    # ------------------------------------------------------------------
    # Iter 66 발견: base state_to_feature_vector는 domain_state 필드를 무시하여
    # Talleyrand action class가 drive 공간에서 분리 불가 (separability = 0.05).
    # 이 메서드가 Literal 필드를 one-hot + 수치 필드를 정규화한 벡터를 반환
    # → extended feature vector로 편입 → separability 회복 기대.

    _REGIMES = (
        "ancien_regime", "revolution", "directory", "consulate",
        "empire", "bourbon_restoration", "july_monarchy",
    )
    _STANCES = (
        "overt_loyal", "pragmatic_serve", "covert_maneuver",
        "strategic_exit", "post_regime",
    )

    def to_feature_vector(self) -> list[float]:
        """Domain state → 15-feature vector.

        Layout:
            [0:7]  regime one-hot (7 regimes)
            [7:12] stance one-hot (5 stances)
            [12]   leverage / 10
            [13]   network_regime_span / 7 (max 7)
            [14]   compromise_count / 10 (rough scale)
        """
        regime_onehot = [
            1.0 if self.current_regime == r else 0.0 for r in self._REGIMES
        ]
        stance_onehot = [
            1.0 if self.alignment_stance == s else 0.0 for s in self._STANCES
        ]
        scalars = [
            self.leverage / 10.0,
            self.network_regime_span / 7.0,
            min(self.compromise_count / 10.0, 1.0),
        ]
        return regime_onehot + stance_onehot + scalars
