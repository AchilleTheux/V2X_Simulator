"""Reward function for communication outcomes.

This module provides a simple and robust reward rule for V2X alerts:
- transmission failure -> negative reward
- successful and on-time alert -> positive reward (faster is better)
- successful but late alert -> low or slightly negative reward
"""

from __future__ import annotations

from typing import Protocol


class RewardInput(Protocol):
    """Minimal result interface required by `compute_reward`."""

    success: bool
    latency_ms: float


def compute_reward(result: RewardInput, deadline_ms: float) -> float:
    """Compute reward from communication result and deadline.

    Rationale:
    - Failures are strongly penalized (`-1.0`) because the alert is not received.
    - On-time successes get positive reward in `[0.5, 1.0]`, with a bonus for
      lower latency.
    - Late successes start with a low value and can become slightly negative,
      capped at `-0.3`, because the alert may still have some residual utility.
    """
    if deadline_ms <= 0:
        raise ValueError("deadline_ms must be > 0")

    if not result.success:
        return -1.0

    if result.latency_ms <= deadline_ms:
        normalized_latency = result.latency_ms / deadline_ms
        return 1.0 - 0.5 * normalized_latency

    lateness_ratio = (result.latency_ms - deadline_ms) / deadline_ms
    late_reward = 0.2 - 0.5 * lateness_ratio
    return max(-0.3, late_reward)
