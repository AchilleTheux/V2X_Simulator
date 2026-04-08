"""Simplified V2X communication channel simulation.

The model is intentionally lightweight and pedagogical:
- direct communication: lower latency, success degrades with distance/obstacle
- infrastructure communication (RSU): higher latency, influenced by RSU load,
  and forced failure when RSU is unavailable
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from .context_builder import Context


class RandomLike(Protocol):
    """Minimal RNG protocol used by simulation functions."""

    def random(self) -> float: ...

    def uniform(self, a: float, b: float) -> float: ...


class CommunicationMode(str, Enum):
    """Supported communication channels."""

    DIRECT = "direct"
    RSU = "rsu"


@dataclass(slots=True)
class CommunicationParameters:
    """Tunable parameters for simplified communication simulation."""

    direct_base_success_prob: float = 0.96
    direct_distance_success_slope: float = 0.03
    direct_obstacle_success_penalty: float = 0.35
    direct_base_latency_ms: float = 25.0
    direct_distance_latency_slope_ms: float = 1.2
    direct_obstacle_latency_penalty_ms: float = 12.0
    direct_latency_jitter_ms: float = 4.0

    rsu_base_success_prob: float = 0.97
    rsu_load_success_slope: float = 0.30
    rsu_obstacle_success_penalty: float = 0.05
    rsu_base_latency_ms: float = 70.0
    rsu_load_latency_slope_ms: float = 80.0
    rsu_obstacle_latency_penalty_ms: float = 6.0
    rsu_latency_jitter_ms: float = 6.0
    rsu_unavailable_latency_ms: float = 130.0

    min_success_prob: float = 0.01
    max_success_prob: float = 0.99

    reward_success_value: float = 1.0
    reward_latency_cost_per_ms: float = 0.002


@dataclass(slots=True)
class CommunicationResult:
    """Result of one communication attempt."""

    mode_chosen: CommunicationMode
    success: bool
    latency_ms: float
    success_probability: float
    reward: float


@dataclass(slots=True)
class CommunicationDecision:
    """Backward-compatible decision object."""

    mode: CommunicationMode
    reason: str


def simulate_direct(
    context: Context,
    rng: RandomLike,
    params: CommunicationParameters | None = None,
) -> CommunicationResult:
    """Simulate direct VRU <-> vehicle communication for one context."""
    p = params or CommunicationParameters()

    success_probability = p.direct_base_success_prob - p.direct_distance_success_slope * context.distance
    if context.obstacle_present:
        success_probability -= p.direct_obstacle_success_penalty
    success_probability = _clamp(success_probability, p.min_success_prob, p.max_success_prob)

    latency_ms = p.direct_base_latency_ms + p.direct_distance_latency_slope_ms * context.distance
    if context.obstacle_present:
        latency_ms += p.direct_obstacle_latency_penalty_ms
    latency_ms += rng.uniform(-p.direct_latency_jitter_ms, p.direct_latency_jitter_ms)
    latency_ms = max(1.0, latency_ms)

    success = rng.random() < success_probability
    reward = _compute_reward(success=success, latency_ms=latency_ms, params=p)

    return CommunicationResult(
        mode_chosen=CommunicationMode.DIRECT,
        success=success,
        latency_ms=latency_ms,
        success_probability=success_probability,
        reward=reward,
    )


def simulate_infrastructure(
    context: Context,
    rng: RandomLike,
    params: CommunicationParameters | None = None,
) -> CommunicationResult:
    """Simulate VRU <-> RSU <-> vehicle communication for one context."""
    p = params or CommunicationParameters()

    if not context.rsu_available:
        latency_ms = p.rsu_unavailable_latency_ms + rng.uniform(0.0, p.rsu_latency_jitter_ms)
        reward = _compute_reward(success=False, latency_ms=latency_ms, params=p)
        return CommunicationResult(
            mode_chosen=CommunicationMode.RSU,
            success=False,
            latency_ms=latency_ms,
            success_probability=0.0,
            reward=reward,
        )

    success_probability = p.rsu_base_success_prob - p.rsu_load_success_slope * context.rsu_load
    if context.obstacle_present:
        success_probability -= p.rsu_obstacle_success_penalty
    success_probability = _clamp(success_probability, p.min_success_prob, p.max_success_prob)

    latency_ms = p.rsu_base_latency_ms + p.rsu_load_latency_slope_ms * context.rsu_load
    if context.obstacle_present:
        latency_ms += p.rsu_obstacle_latency_penalty_ms
    latency_ms += rng.uniform(-p.rsu_latency_jitter_ms, p.rsu_latency_jitter_ms)
    latency_ms = max(1.0, latency_ms)

    success = rng.random() < success_probability
    reward = _compute_reward(success=success, latency_ms=latency_ms, params=p)

    return CommunicationResult(
        mode_chosen=CommunicationMode.RSU,
        success=success,
        latency_ms=latency_ms,
        success_probability=success_probability,
        reward=reward,
    )


class CommunicationModel:
    """Convenience wrapper around direct and infrastructure simulators."""

    def __init__(self, params: CommunicationParameters | None = None) -> None:
        self.params = params or CommunicationParameters()

    def choose_mode(self, context: Context) -> CommunicationDecision:
        """Choose a mode from deterministic expected reward approximation."""
        direct_score = _expected_reward_direct(context=context, params=self.params)
        rsu_score = _expected_reward_rsu(context=context, params=self.params)

        if direct_score >= rsu_score:
            return CommunicationDecision(mode=CommunicationMode.DIRECT, reason="Higher expected reward")
        return CommunicationDecision(mode=CommunicationMode.RSU, reason="Higher expected reward")


def _expected_reward_direct(*, context: Context, params: CommunicationParameters) -> float:
    p_success = params.direct_base_success_prob - params.direct_distance_success_slope * context.distance
    if context.obstacle_present:
        p_success -= params.direct_obstacle_success_penalty
    p_success = _clamp(p_success, params.min_success_prob, params.max_success_prob)

    latency = params.direct_base_latency_ms + params.direct_distance_latency_slope_ms * context.distance
    if context.obstacle_present:
        latency += params.direct_obstacle_latency_penalty_ms

    return p_success * params.reward_success_value - latency * params.reward_latency_cost_per_ms


def _expected_reward_rsu(*, context: Context, params: CommunicationParameters) -> float:
    if not context.rsu_available:
        return -params.rsu_unavailable_latency_ms * params.reward_latency_cost_per_ms

    p_success = params.rsu_base_success_prob - params.rsu_load_success_slope * context.rsu_load
    if context.obstacle_present:
        p_success -= params.rsu_obstacle_success_penalty
    p_success = _clamp(p_success, params.min_success_prob, params.max_success_prob)

    latency = params.rsu_base_latency_ms + params.rsu_load_latency_slope_ms * context.rsu_load
    if context.obstacle_present:
        latency += params.rsu_obstacle_latency_penalty_ms

    return p_success * params.reward_success_value - latency * params.reward_latency_cost_per_ms


def _compute_reward(*, success: bool, latency_ms: float, params: CommunicationParameters) -> float:
    success_part = params.reward_success_value if success else 0.0
    latency_cost = latency_ms * params.reward_latency_cost_per_ms
    return success_part - latency_cost


def _clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))
