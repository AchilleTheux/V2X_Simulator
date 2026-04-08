import random

import pytest

from v2x_sim.communication_model import (
    CommunicationParameters,
    simulate_direct,
    simulate_infrastructure,
)
from v2x_sim.context_builder import Context


def _context(
    *,
    distance: float,
    obstacle_present: bool,
    rsu_available: bool,
    rsu_load: float,
) -> Context:
    return Context(
        simulation_time=10.0,
        vru_position=(0.0, 0.0),
        vehicle_position=(distance, 0.0),
        distance=distance,
        danger=distance < 5.0,
        rsu_available=rsu_available,
        rsu_load=rsu_load,
        obstacle_present=obstacle_present,
    )


def test_infrastructure_fails_when_rsu_unavailable() -> None:
    context = _context(distance=3.0, obstacle_present=False, rsu_available=False, rsu_load=0.2)
    rng = random.Random(123)

    result = simulate_infrastructure(context=context, rng=rng)

    assert result.success is False
    assert result.success_probability == pytest.approx(0.0)


def test_direct_often_better_at_short_distance_without_obstacle() -> None:
    context = _context(distance=2.0, obstacle_present=False, rsu_available=True, rsu_load=0.1)
    params = CommunicationParameters()

    direct_results = [simulate_direct(context=context, rng=random.Random(1000 + i), params=params) for i in range(200)]
    infra_results = [
        simulate_infrastructure(context=context, rng=random.Random(2000 + i), params=params)
        for i in range(200)
    ]

    mean_direct_reward = sum(r.reward for r in direct_results) / len(direct_results)
    mean_infra_reward = sum(r.reward for r in infra_results) / len(infra_results)

    assert mean_direct_reward > mean_infra_reward


def test_direct_degrades_when_obstacle_is_present() -> None:
    without_obstacle = _context(distance=4.0, obstacle_present=False, rsu_available=True, rsu_load=0.2)
    with_obstacle = _context(distance=4.0, obstacle_present=True, rsu_available=True, rsu_load=0.2)
    params = CommunicationParameters()

    no_obstacle_results = [
        simulate_direct(context=without_obstacle, rng=random.Random(3000 + i), params=params)
        for i in range(300)
    ]
    obstacle_results = [
        simulate_direct(context=with_obstacle, rng=random.Random(4000 + i), params=params)
        for i in range(300)
    ]

    success_rate_no_obstacle = sum(1 for r in no_obstacle_results if r.success) / len(no_obstacle_results)
    success_rate_obstacle = sum(1 for r in obstacle_results if r.success) / len(obstacle_results)

    assert success_rate_obstacle < success_rate_no_obstacle


def test_infrastructure_latency_increases_with_rsu_load() -> None:
    params = CommunicationParameters(rsu_latency_jitter_ms=0.0)
    rng = random.Random(999)

    low_load_context = _context(distance=6.0, obstacle_present=False, rsu_available=True, rsu_load=0.1)
    high_load_context = _context(distance=6.0, obstacle_present=False, rsu_available=True, rsu_load=0.9)

    low_load_result = simulate_infrastructure(context=low_load_context, rng=rng, params=params)
    high_load_result = simulate_infrastructure(context=high_load_context, rng=rng, params=params)

    assert high_load_result.latency_ms > low_load_result.latency_ms
