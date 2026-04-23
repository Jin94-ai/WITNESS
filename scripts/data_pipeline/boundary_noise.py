"""Phase E -- Boundary-focused noise (spec §6).

Spec §6.3 verbatim:
    Phase A-D만으로 separability test 통과 시 Phase E 생략 가능.
    과도하게 noise 추가하면 오히려 학습 방해.
    Lee 판단으로 진행 여부 결정.

Phase D 결과 (2026-04-22): Linear 0.509 / Consistency 0.439 FAIL.
즉 Lee 판단으로 이 Phase E 적용 고려 가능 상태.

This module implements the spec §6.2 algorithm:
    if near decision boundary:
        σ = 0.8
    else:
        σ = 0.2

Decision boundary = action의 zone centroid에서 euclidean 거리.

사용: apply_boundary_noise(X, actions, zones_path) -> X_noised
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from scripts.data_pipeline.data_driven_zones import load_zones

# Feature names mapping (first 12 dims)
BASE_FEATURE_NAMES = [
    "fear", "hope", "grief", "confusion", "love",
    "fatigue", "hunger", "health",
    "moral_injury", "identity_shift", "event_trauma", "trust_scar",
]


def zone_centroid(zone: dict[str, tuple[float, float]]) -> np.ndarray:
    """Feature-space centroid of a zone (12-dim)."""
    c = np.zeros(12, dtype=np.float32)
    for i, feat in enumerate(BASE_FEATURE_NAMES):
        lo, hi = zone.get(feat, (0.0, 10.0))
        c[i] = (lo + hi) / 2
    return c


def distance_to_zone(x: np.ndarray, zone: dict[str, tuple[float, float]]) -> float:
    """Distance from state x (first 12 dims used) to zone centroid."""
    return float(np.linalg.norm(x[:12] - zone_centroid(zone)))


def apply_boundary_noise(
    X: np.ndarray, actions: list[str],
    zones_path: Path | str,
    *,
    near_sigma: float = 0.8,
    far_sigma: float = 0.2,
    near_threshold: float = 3.0,
    seed: int = 0,
) -> np.ndarray:
    """Add boundary-focused noise per spec §6.2.

    Args:
        X: (N, 15) feature matrix
        actions: list of action_id per row
        zones_path: data-driven zones JSON path
        near_sigma: noise std near decision boundary
        far_sigma: noise std far from boundary
        near_threshold: distance threshold in feature space units

    Returns:
        X_noised: (N, 15) array with noise added to first 12 dims (base feat).
                  Context dims 12-14 (event_id, time, hazard) untouched.
    """
    zones = load_zones(zones_path)
    rng = np.random.default_rng(seed)
    X_out = X.copy()

    n_near = 0
    n_far = 0
    for i, action in enumerate(actions):
        zone = zones.get(action)
        if zone is None:
            # Unknown zone → treat as far (weak noise)
            sigma = far_sigma
            n_far += 1
        else:
            dist = distance_to_zone(X[i], zone)
            if dist < near_threshold:
                sigma = near_sigma
                n_near += 1
            else:
                sigma = far_sigma
                n_far += 1
        # Noise only on base 12 features; clamp
        noise = rng.normal(0.0, sigma, size=12).astype(np.float32)
        X_out[i, :12] = np.clip(X_out[i, :12] + noise, 0.0, 10.0)
        # identity_shift allowed [-10, 10]
        X_out[i, 9] = np.clip(X_out[i, 9], -10.0, 10.0)

    return X_out, {"n_near": n_near, "n_far": n_far, "near_ratio": n_near / max(1, len(actions))}


__all__ = ["apply_boundary_noise", "distance_to_zone", "zone_centroid"]
