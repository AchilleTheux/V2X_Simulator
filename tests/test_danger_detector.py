import math

import pytest

from v2x_sim.context_builder import ActorState, SimulationContext
from v2x_sim.danger_detector import (
    DangerDetector,
    assess_proximity_danger,
    euclidean_distance,
)


def test_euclidean_distance_basic() -> None:
    distance = euclidean_distance((0.0, 0.0), (3.0, 4.0))
    assert distance == pytest.approx(5.0)


def test_assess_proximity_above_threshold() -> None:
    result = assess_proximity_danger(
        vru_position=(0.0, 0.0),
        vehicle_position=(10.0, 0.0),
        danger_threshold_m=5.0,
    )

    assert result.distance_m == pytest.approx(10.0)
    assert result.is_danger is False


def test_assess_proximity_below_threshold() -> None:
    result = assess_proximity_danger(
        vru_position=(1.0, 1.0),
        vehicle_position=(2.0, 2.0),
        danger_threshold_m=2.0,
    )

    assert result.distance_m == pytest.approx(math.sqrt(2.0))
    assert result.is_danger is True


def test_numeric_stability_large_coordinates() -> None:
    result = assess_proximity_danger(
        vru_position=(1_000_000.0, 1_000_000.0),
        vehicle_position=(1_000_003.0, 1_000_004.0),
        danger_threshold_m=10.0,
    )

    assert math.isfinite(result.distance_m)
    assert result.distance_m == pytest.approx(5.0)


def test_detector_builds_danger_event_from_context() -> None:
    context = SimulationContext(
        step=7,
        actors={
            "ped_0": ActorState(
                actor_id="ped_0",
                actor_type="pedestrian",
                x=0.0,
                y=0.0,
                speed=1.2,
                heading=0.0,
            ),
            "veh_0": ActorState(
                actor_id="veh_0",
                actor_type="vehicle",
                x=1.0,
                y=1.0,
                speed=8.0,
                heading=0.0,
            ),
        },
    )

    detector = DangerDetector(danger_distance_m=2.0)
    events = detector.detect(context)

    assert len(events) == 1
    assert events[0].step == 7
    assert events[0].vru_id == "ped_0"
    assert events[0].vehicle_id == "veh_0"
