import random

import pytest

from v2x_sim.communication_model import CommunicationMode
from v2x_sim.thompson import ThompsonSamplingStrategy


def test_update_changes_beta_params() -> None:
    strategy = ThompsonSamplingStrategy(rng=random.Random(0))

    params_before = strategy.get_arm_params()[CommunicationMode.DIRECT]
    alpha_before = params_before.alpha
    beta_before = params_before.beta

    strategy.update(CommunicationMode.DIRECT, 1)
    strategy.update(CommunicationMode.DIRECT, 0)

    params_after = strategy.get_arm_params()[CommunicationMode.DIRECT]
    assert params_after.alpha == pytest.approx(alpha_before + 1.0)
    assert params_after.beta == pytest.approx(beta_before + 1.0)


def test_select_action_returns_valid_action() -> None:
    strategy = ThompsonSamplingStrategy(rng=random.Random(1))
    action = strategy.select_action()

    assert action in {CommunicationMode.DIRECT, CommunicationMode.RSU}


def test_invalid_reward_raises() -> None:
    strategy = ThompsonSamplingStrategy(rng=random.Random(2))

    with pytest.raises(ValueError):
        strategy.update(CommunicationMode.DIRECT, 2)  # type: ignore[arg-type]


def test_thompson_converges_towards_better_arm() -> None:
    rng_policy = random.Random(123)
    rng_env = random.Random(456)
    strategy = ThompsonSamplingStrategy(rng=rng_policy)

    true_success_prob = {
        CommunicationMode.DIRECT: 0.75,
        CommunicationMode.RSU: 0.45,
    }

    actions: list[CommunicationMode] = []
    for _ in range(1500):
        action = strategy.select_action()
        actions.append(action)

        reward = 1 if rng_env.random() < true_success_prob[action] else 0
        strategy.update(action, reward)

    # Look only at the tail to evaluate learned preference.
    tail = actions[-500:]
    direct_ratio = sum(1 for a in tail if a == CommunicationMode.DIRECT) / len(tail)

    assert direct_ratio >= 0.65
