"""Simple non-contextual Thompson Sampling for 2 communication actions.

This module implements a pedagogical Beta-Bernoulli Thompson Sampling policy.
Each arm (direct / infrastructure) maintains a Beta posterior:
- alpha: pseudo-count of successes
- beta: pseudo-count of failures

At each decision, one sample is drawn from each arm's posterior and the arm
with the largest sample is selected.
"""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Mapping

from .communication_model import CommunicationMode
from .context_builder import Context


@dataclass(slots=True)
class ArmBetaParams:
    """Posterior parameters for one Bernoulli arm."""

    alpha: float = 1.0
    beta: float = 1.0


class ThompsonSamplingStrategy:
    """Non-contextual Thompson Sampling over two actions.

    Actions:
    - `CommunicationMode.DIRECT`
    - `CommunicationMode.RSU` (infrastructure)

    Rewards are expected to be binary:
    - 1: success-at-deadline (or equivalent)
    - 0: otherwise
    """

    def __init__(
        self,
        *,
        prior_alpha: float = 1.0,
        prior_beta: float = 1.0,
        rng: random.Random | None = None,
    ) -> None:
        if prior_alpha <= 0 or prior_beta <= 0:
            raise ValueError("prior_alpha and prior_beta must be > 0")

        self.rng = rng or random.Random()
        self.params: dict[CommunicationMode, ArmBetaParams] = {
            CommunicationMode.DIRECT: ArmBetaParams(alpha=prior_alpha, beta=prior_beta),
            CommunicationMode.RSU: ArmBetaParams(alpha=prior_alpha, beta=prior_beta),
        }

    def select_action(self) -> CommunicationMode:
        """Sample from each posterior and return the best action."""
        direct_sample = self.rng.betavariate(
            self.params[CommunicationMode.DIRECT].alpha,
            self.params[CommunicationMode.DIRECT].beta,
        )
        infra_sample = self.rng.betavariate(
            self.params[CommunicationMode.RSU].alpha,
            self.params[CommunicationMode.RSU].beta,
        )

        if direct_sample >= infra_sample:
            return CommunicationMode.DIRECT
        return CommunicationMode.RSU

    def choose_mode(self, context: Context) -> CommunicationMode:
        """Compatibility hook with the simulator strategy interface."""
        _ = context
        return self.select_action()

    def update(self, action: CommunicationMode, reward: int | bool) -> None:
        """Update posterior parameters from observed binary reward."""
        if action not in self.params:
            raise ValueError(f"Unknown action: {action}")

        if reward not in (0, 1, False, True):
            raise ValueError("reward must be binary (0 or 1)")

        arm = self.params[action]
        if int(reward) == 1:
            arm.alpha += 1.0
        else:
            arm.beta += 1.0

    def get_arm_params(self) -> Mapping[CommunicationMode, ArmBetaParams]:
        """Return read-only-like mapping of current Beta parameters."""
        return self.params


class ThompsonPolicy(ThompsonSamplingStrategy):
    """Backward-compatible wrapper kept for existing project imports."""

    def select_mode(self) -> CommunicationMode:
        return self.select_action()

    def update(self, mode: CommunicationMode, reward: float) -> None:  # type: ignore[override]
        binary_reward = 1 if reward >= 0.5 else 0
        super().update(mode, binary_reward)
