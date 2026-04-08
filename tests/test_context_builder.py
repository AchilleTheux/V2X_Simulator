import pytest

from v2x_sim.context_builder import (
    ActorState,
    Context,
    ContextBuilder,
    build_context,
    compute_distance,
)


def test_compute_distance_basic() -> None:
    assert compute_distance((0.0, 0.0), (3.0, 4.0)) == pytest.approx(5.0)


def test_build_context_below_threshold_sets_danger_true() -> None:
    context = build_context(
        simulation_time=1.0,
        vru_position=(0.0, 0.0),
        vehicle_position=(3.0, 4.0),
        danger_threshold_m=6.0,
    )

    assert isinstance(context, Context)
    assert context.distance == pytest.approx(5.0)
    assert context.danger is True
    assert context.obstacle_present is True
    assert context.rsu_available is False
    assert 0.0 <= context.rsu_load <= 1.0


def test_build_context_above_threshold_sets_danger_false() -> None:
    context = build_context(
        simulation_time=8.0,
        vru_position=(0.0, 0.0),
        vehicle_position=(10.0, 0.0),
        danger_threshold_m=5.0,
    )

    assert context.distance == pytest.approx(10.0)
    assert context.danger is False
    assert context.obstacle_present is False


def test_build_context_is_deterministic_for_same_inputs() -> None:
    c1 = build_context(
        simulation_time=18.0,
        vru_position=(2.0, 2.0),
        vehicle_position=(5.0, 6.0),
        danger_threshold_m=5.0,
    )
    c2 = build_context(
        simulation_time=18.0,
        vru_position=(2.0, 2.0),
        vehicle_position=(5.0, 6.0),
        danger_threshold_m=5.0,
    )

    assert c1 == c2


def test_context_builder_builds_scene_snapshot_and_decision_context() -> None:
    builder = ContextBuilder(danger_distance_m=2.0)
    actors = [
        ActorState(
            actor_id="vru_1",
            actor_type="pedestrian",
            x=0.0,
            y=1.0,
            speed=1.3,
            heading=90.0,
        )
    ]

    scene = builder.build(step=5, actors=actors)
    decision_context = builder.build_decision_context(
        simulation_time=5.0,
        vru_position=(0.0, 1.0),
        vehicle_position=(0.0, 2.0),
    )

    assert scene.step == 5
    assert "vru_1" in scene.actors
    assert decision_context.danger is True
