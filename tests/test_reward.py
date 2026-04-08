import pytest

from v2x_sim.communication_model import CommunicationMode, CommunicationResult
from v2x_sim.reward import compute_reward


def test_compute_reward_success_fast() -> None:
    result = CommunicationResult(
        mode_chosen=CommunicationMode.DIRECT,
        success=True,
        latency_ms=20.0,
        success_probability=0.9,
        reward=0.0,
    )

    reward = compute_reward(result=result, deadline_ms=100.0)

    assert reward > 0.0
    assert reward == pytest.approx(0.9)


def test_compute_reward_success_late() -> None:
    result = CommunicationResult(
        mode_chosen=CommunicationMode.RSU,
        success=True,
        latency_ms=150.0,
        success_probability=0.7,
        reward=0.0,
    )

    reward = compute_reward(result=result, deadline_ms=100.0)

    assert reward <= 0.2
    assert reward == pytest.approx(-0.05)


def test_compute_reward_failure() -> None:
    result = CommunicationResult(
        mode_chosen=CommunicationMode.RSU,
        success=False,
        latency_ms=80.0,
        success_probability=0.0,
        reward=0.0,
    )

    reward = compute_reward(result=result, deadline_ms=100.0)

    assert reward == pytest.approx(-1.0)
