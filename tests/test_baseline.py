from v2x_sim.baseline import (
    AlwaysDirectStrategy,
    AlwaysInfrastructureStrategy,
    BaselinePolicy,
    ThresholdHeuristicStrategy,
)
from v2x_sim.communication_model import CommunicationMode
from v2x_sim.context_builder import Context
from v2x_sim.danger_detector import DangerEvent


def _context(
    *,
    distance: float,
    obstacle_present: bool,
    rsu_available: bool,
) -> Context:
    return Context(
        simulation_time=0.0,
        vru_position=(0.0, 0.0),
        vehicle_position=(distance, 0.0),
        distance=distance,
        danger=distance < 5.0,
        rsu_available=rsu_available,
        rsu_load=0.3,
        obstacle_present=obstacle_present,
    )


def test_always_direct_strategy() -> None:
    strategy = AlwaysDirectStrategy()
    context = _context(distance=30.0, obstacle_present=True, rsu_available=False)

    assert strategy.choose_mode(context) == CommunicationMode.DIRECT


def test_always_infrastructure_strategy() -> None:
    strategy = AlwaysInfrastructureStrategy()
    context = _context(distance=2.0, obstacle_present=False, rsu_available=True)

    assert strategy.choose_mode(context) == CommunicationMode.RSU


def test_threshold_heuristic_direct_when_close_without_obstacle() -> None:
    strategy = ThresholdHeuristicStrategy(direct_distance_threshold_m=6.0)
    context = _context(distance=4.5, obstacle_present=False, rsu_available=True)

    assert strategy.choose_mode(context) == CommunicationMode.DIRECT


def test_threshold_heuristic_rsu_when_obstacle_present_and_available() -> None:
    strategy = ThresholdHeuristicStrategy(direct_distance_threshold_m=6.0)
    context = _context(distance=3.0, obstacle_present=True, rsu_available=True)

    assert strategy.choose_mode(context) == CommunicationMode.RSU


def test_threshold_heuristic_fallback_direct_when_rsu_unavailable() -> None:
    strategy = ThresholdHeuristicStrategy(direct_distance_threshold_m=6.0)
    context = _context(distance=25.0, obstacle_present=True, rsu_available=False)

    assert strategy.choose_mode(context) == CommunicationMode.DIRECT


def test_baseline_policy_backward_compatibility() -> None:
    policy = BaselinePolicy(direct_distance_m=3.0)

    near_event = DangerEvent(step=1, vru_id="v1", vehicle_id="car1", distance_m=2.0)
    far_event = DangerEvent(step=1, vru_id="v1", vehicle_id="car1", distance_m=10.0)

    assert policy.choose_mode(near_event) == CommunicationMode.DIRECT
    assert policy.choose_mode(far_event) == CommunicationMode.RSU
