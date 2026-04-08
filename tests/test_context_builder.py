from v2x_sim.context_builder import ActorState, ContextBuilder


def test_context_builder_maps_actors_by_id() -> None:
    builder = ContextBuilder()
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

    context = builder.build(step=5, actors=actors)

    assert context.step == 5
    assert "vru_1" in context.actors
