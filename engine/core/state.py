"""에이전트 상태 모델.

시뮬레이션의 최소 단위인 에이전트의 상태를 정의한다.
모든 수치는 0.0~10.0 범위의 float이며, Pydantic validator로 강제한다.
AgentState는 불변 스냅샷으로 사용한다 (model_copy로 갱신).
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class PhysicalState(BaseModel):
    """물리적 상태. 피로, 배고픔, 건강, 위치."""

    fatigue: float = Field(default=0.0, ge=0.0, le=10.0, description="피로도")
    hunger: float = Field(default=0.0, ge=0.0, le=10.0, description="배고픔")
    health: float = Field(default=10.0, ge=0.0, le=10.0, description="건강")
    location: str = Field(default="unknown", description="현재 위치 ID")


class EmotionalState(BaseModel):
    """감정 상태. 각 감정은 0(없음)~10(극대) 범위.

    v1.2 Phase-linked life architecture: `awe` 추가 (소명 phase 기적 목격,
    변화산 등 경외 중심 사건 모델링). default 0.0 = backward compat.
    """

    fear: float = Field(default=0.0, ge=0.0, le=10.0, description="두려움")
    hope: float = Field(default=5.0, ge=0.0, le=10.0, description="희망")
    grief: float = Field(default=0.0, ge=0.0, le=10.0, description="슬픔")
    confusion: float = Field(default=0.0, ge=0.0, le=10.0, description="혼란")
    love: float = Field(default=5.0, ge=0.0, le=10.0, description="사랑")
    awe: float = Field(default=0.0, ge=0.0, le=10.0, description="경외 (v1.2)")


class Relationship(BaseModel):
    """다른 에이전트와의 관계."""

    target_id: str = Field(description="관계 대상 에이전트 ID")
    trust: float = Field(default=5.0, ge=0.0, le=10.0, description="신뢰")
    love: float = Field(default=5.0, ge=0.0, le=10.0, description="사랑")
    awe: float = Field(default=0.0, ge=0.0, le=10.0, description="경외")
    understanding: float = Field(default=5.0, ge=0.0, le=10.0, description="이해")


class DomainState(BaseModel):
    """도메인 고유 상태의 추상 기반 클래스.

    engine/은 이 클래스만 안다. 구체적인 도메인 상태
    (예: FaithJourneyState)는 content/ 쪽에서 상속하여 정의한다.
    """

    type: str = Field(default="base", description="도메인 상태 타입 식별자")


class SlowState(BaseModel):
    """비가역적 누적 흔적. 항상성으로 복원되지 않는 영구적 상태.

    사건이 남기는 '상처', '결정 이력', '정체성 변화'를 추적한다.
    fast state(emotions)는 중앙으로 수렴하지만, slow state는 축적된다.

    인물 비종속 네이밍: 어떤 인물��� 위반 행동이든
    동일한 추상 변수로 표현 가능.
    """

    moral_injury: float = Field(
        default=0.0, ge=0.0, le=10.0,
        description="도덕적 상처. 자신의 신념/가치에 반하는 행동 후 누적.",
    )
    breach_count: float = Field(
        default=0.0, ge=0.0,
        description="자기파괴적/위반적 행동 누적. (위반, 자해, 약속 파기, 폭발 등)",
    )
    event_trauma: float = Field(
        default=0.0, ge=0.0, le=10.0,
        description="사건 트라우마. 극한 사건 경험/목격 후 누적.",
    )
    identity_shift: float = Field(
        default=0.0, ge=-10.0, le=10.0,
        description="정체성 변화. 양수=강화/성장, 음수=붕괴/해체.",
    )
    trust_scar: float = Field(
        default=0.0, ge=0.0, le=10.0,
        description="관계 상처. 관계 단절이나 고립 후 누적.",
    )


class LatentDriveState(BaseModel):
    """v1.0 Latent Drive Bottleneck 학습 결과 (예약 필드).

    예측 학습된 잠재 drive 축. 3~8차원 권장.
    이름은 학습 후 해석 (attachment, shame, calling 등).

    v0.x에서는 None 유지 (backward compatible).
    v1.0 학습 엔진 도입 시 활성화.

    참조: DESIGN_LATENT_DRIVE.md
    """

    values: list[float] = Field(
        default_factory=list,
        description="잠재 drive 벡터 (차원 d = 3~8)",
    )
    dim: int = Field(default=0, ge=0, description="latent dim")


class AgentBelief(BaseModel):
    """v1.1 한 agent가 다른 agent에 대해 갖는 추정 (목격자 정체성).

    관측에 기반한 target agent의 상태/drive 추정.
    Bayesian belief update로 갱신 (v1.1 relational extension).

    v0.x에서는 사용되지 않음 (dict 비어있음).
    v1.1 도입 시 per-agent observation history가 축적됨.

    참조: TRACE_SCHEMA.md §2.3 belief_update
    """

    target_id: str = Field(description="추정 대상 에이전트 ID")
    estimated_state: dict[str, float] = Field(
        default_factory=dict,
        description="field_path → estimated value (e.g. 'emotions.fear': 7.0)",
    )
    confidence: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="추정 신뢰도 (관측 횟수 기반)",
    )
    observation_count: int = Field(
        default=0, ge=0,
        description="target agent 행동을 관측한 횟수",
    )


class AgentState(BaseModel):
    """에이전트의 전체 상태 스냅샷.

    불변으로 사용한다. 상태 갱신 시 model_copy(update=...)로 새 인스턴스를 생성.

    네 층의 상태:
    - fast state (emotions): 항상성으로 중앙 수렴. 현재 감정.
    - slow state: 비가역적 누적. 사건의 흔적.
    - drive_state (v1.0+): 학습된 latent drive. None이면 symbolic rule only.
    - beliefs (v1.1+): 타 agent에 대한 추정. Witness 목격자 정체성의 핵심.
    """

    agent_id: str = Field(description="에이전트 고유 ID")
    tick: int = Field(default=0, ge=0, description="현재 시뮬레이션 tick")
    physical: PhysicalState = Field(default_factory=PhysicalState)
    emotions: EmotionalState = Field(default_factory=EmotionalState)
    slow_state: SlowState = Field(default_factory=SlowState)
    relationships: dict[str, Relationship] = Field(default_factory=dict)
    domain_state: DomainState | None = Field(default=None)
    drive_state: LatentDriveState | None = Field(
        default=None,
        description="v1.0 학습된 latent drive (None = symbolic rule only, backward compat)",
    )
    beliefs: dict[str, AgentBelief] = Field(
        default_factory=dict,
        description="target_id → AgentBelief (v1.1 relational). v0.x에서는 empty.",
    )


def clamp(value: float, min_val: float = 0.0, max_val: float = 10.0) -> float:
    """값을 [min_val, max_val] 범위로 제한한다."""
    return max(min_val, min(max_val, value))


def get_nested_value(state: AgentState, field_path: str) -> float | str | None:
    """점(.) 구분 경로로 AgentState의 중첩 필드 값을 가져온다.

    Args:
        state: 에이전트 상태
        field_path: 점 구분 경로 (예: "emotions.fear", "physical.fatigue")

    Returns:
        해당 필드의 값. 경로가 유효하지 않으면 None.
    """
    parts = field_path.split(".")
    current: object = state
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, BaseModel):
            current = getattr(current, part, None)
        else:
            return None
        if current is None:
            return None
    if isinstance(current, (float, int, str)):
        return current
    return None


def set_nested_value(state: AgentState, field_path: str, value: float | str) -> AgentState:
    """점(.) 구분 경로로 AgentState의 중첩 필드 값을 설정한 새 상태를 반환한다.

    원본 state는 변경하지 않는다.

    Args:
        state: 원본 에이전트 상태
        field_path: 점 구분 경로 (예: "emotions.fear")
        value: 설정할 값

    Returns:
        갱신된 새 AgentState 인스턴스
    """
    parts = field_path.split(".")
    if len(parts) == 1:
        return state.model_copy(update={parts[0]: value})

    # 2-depth: "emotions.fear" -> emotions 객체를 복사하며 fear 갱신
    top_field = parts[0]
    top_obj = getattr(state, top_field, None)

    if top_obj is None:
        return state

    if isinstance(top_obj, BaseModel):
        if len(parts) == 2:
            new_sub = top_obj.model_copy(update={parts[1]: value})
        else:
            # 3+ depth (relationships 등): 재귀적 처리는 필요시 확장
            return state
        return state.model_copy(update={top_field: new_sub})

    if isinstance(top_obj, dict) and len(parts) >= 2:
        # relationships.<target_id>.<field> 같은 경우 (예: relationships.ally.trust)
        dict_key = parts[1]
        if dict_key in top_obj and len(parts) == 3:
            inner_obj = top_obj[dict_key]
            if isinstance(inner_obj, BaseModel):
                new_inner = inner_obj.model_copy(update={parts[2]: value})
                new_dict = {**top_obj, dict_key: new_inner}
                return state.model_copy(update={top_field: new_dict})

    return state
