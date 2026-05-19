import random

import pytest

from v2x_sim.bandit import EpsilonGreedyStrategy, UCBStrategy
from v2x_sim.communication_model import CommunicationMode


def test_ucb_explores_each_arm_before_using_scores() -> None:
    strategy = UCBStrategy()

    first = strategy.select_action()
    strategy.update(first, 1)
    second = strategy.select_action()

    assert first == CommunicationMode.DIRECT
    assert second == CommunicationMode.RSU


def test_ucb_updates_empirical_mean() -> None:
    strategy = UCBStrategy()

    strategy.update(CommunicationMode.DIRECT, 1)
    strategy.update(CommunicationMode.DIRECT, 0)

    stats = strategy.get_arm_stats()[CommunicationMode.DIRECT]
    assert stats.count == 2
    assert stats.value == pytest.approx(0.5)


def test_epsilon_greedy_uses_best_empirical_arm_when_not_exploring() -> None:
    strategy = EpsilonGreedyStrategy(epsilon=0.0, rng=random.Random(0))

    strategy.update(CommunicationMode.DIRECT, 0)
    strategy.update(CommunicationMode.RSU, 1)

    assert strategy.select_action() == CommunicationMode.RSU


def test_bandit_invalid_reward_raises() -> None:
    strategy = UCBStrategy()

    with pytest.raises(ValueError):
        strategy.update(CommunicationMode.DIRECT, 2)  # type: ignore[arg-type]


def test_epsilon_must_be_probability() -> None:
    with pytest.raises(ValueError):
        EpsilonGreedyStrategy(epsilon=1.5)


def test_ucb_exploration_weight_must_be_non_negative() -> None:
    with pytest.raises(ValueError):
        UCBStrategy(exploration_weight=-1.0)
