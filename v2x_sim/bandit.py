"""Additional bandit strategies for communication mode selection."""

from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Mapping

from .communication_model import CommunicationMode
from .context_builder import Context


ARMS: tuple[CommunicationMode, CommunicationMode] = (
    CommunicationMode.DIRECT,
    CommunicationMode.RSU,
)


@dataclass(slots=True)
class ArmStats:
    """Empirical statistics for one bandit arm."""

    count: int = 0
    value: float = 0.0


class UCBStrategy:
    """Upper Confidence Bound strategy over direct and infrastructure modes.

    The strategy maximizes:
        empirical_mean + exploration_weight * sqrt(log(total_pulls) / arm_pulls)

    Rewards are expected to be binary:
    - 1: communication succeeded before the deadline
    - 0: failure or late communication
    """

    def __init__(self, *, exploration_weight: float = 2.0) -> None:
        if exploration_weight < 0:
            raise ValueError("exploration_weight must be >= 0")

        self.exploration_weight = exploration_weight
        self.stats: dict[CommunicationMode, ArmStats] = {
            arm: ArmStats() for arm in ARMS
        }
        self.total_count = 0

    def select_action(self) -> CommunicationMode:
        """Return the arm with the highest UCB score."""
        for arm in ARMS:
            if self.stats[arm].count == 0:
                return arm

        log_total = math.log(self.total_count)
        scores = {
            arm: self.stats[arm].value
            + self.exploration_weight * math.sqrt(log_total / self.stats[arm].count)
            for arm in ARMS
        }
        return max(ARMS, key=lambda arm: scores[arm])

    def choose_mode(self, context: Context) -> CommunicationMode:
        """Compatibility hook with the simulator strategy interface."""
        _ = context
        return self.select_action()

    def update(self, action: CommunicationMode, reward: int | bool) -> None:
        """Update empirical mean from observed binary reward."""
        _validate_action_and_reward(action, reward)

        arm = self.stats[action]
        arm.count += 1
        self.total_count += 1
        arm.value += (int(reward) - arm.value) / arm.count

    def get_arm_stats(self) -> Mapping[CommunicationMode, ArmStats]:
        """Return current empirical statistics."""
        return self.stats


class EpsilonGreedyStrategy:
    """Epsilon-greedy strategy over direct and infrastructure modes.

    With probability epsilon, the strategy explores randomly. Otherwise, it
    chooses the arm with the best empirical mean reward.
    """

    def __init__(
        self,
        *,
        epsilon: float = 0.1,
        rng: random.Random | None = None,
    ) -> None:
        if not 0.0 <= epsilon <= 1.0:
            raise ValueError("epsilon must be in [0, 1]")

        self.epsilon = epsilon
        self.rng = rng or random.Random()
        self.stats: dict[CommunicationMode, ArmStats] = {
            arm: ArmStats() for arm in ARMS
        }
        self.total_count = 0

    def select_action(self) -> CommunicationMode:
        """Return an exploratory or greedy communication mode."""
        for arm in ARMS:
            if self.stats[arm].count == 0:
                return arm

        if self.rng.random() < self.epsilon:
            return self.rng.choice(ARMS)

        return max(ARMS, key=lambda arm: self.stats[arm].value)

    def choose_mode(self, context: Context) -> CommunicationMode:
        """Compatibility hook with the simulator strategy interface."""
        _ = context
        return self.select_action()

    def update(self, action: CommunicationMode, reward: int | bool) -> None:
        """Update empirical mean from observed binary reward."""
        _validate_action_and_reward(action, reward)

        arm = self.stats[action]
        arm.count += 1
        self.total_count += 1
        arm.value += (int(reward) - arm.value) / arm.count

    def get_arm_stats(self) -> Mapping[CommunicationMode, ArmStats]:
        """Return current empirical statistics."""
        return self.stats


def _validate_action_and_reward(action: CommunicationMode, reward: int | bool) -> None:
    if action not in ARMS:
        raise ValueError(f"Unknown action: {action}")
    if reward not in (0, 1, False, True):
        raise ValueError("reward must be binary (0 or 1)")
