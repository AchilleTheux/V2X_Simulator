"""Builds normalized simulation context objects.

This module is the bridge between raw simulator state and model-friendly
structures consumed by danger detection and communication policies.
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class ActorState:
    """State of a single actor in the scene."""

    actor_id: str
    actor_type: str
    x: float
    y: float
    speed: float
    heading: float


@dataclass(slots=True)
class SimulationContext:
    """Snapshot of the scene at one simulation step."""

    step: int
    actors: dict[str, ActorState] = field(default_factory=dict)


class ContextBuilder:
    """Converts simulator output to a normalized `SimulationContext`."""

    def build(self, step: int, actors: list[ActorState]) -> SimulationContext:
        """Create context snapshot from a list of actor states."""
        actor_map = {actor.actor_id: actor for actor in actors}
        return SimulationContext(step=step, actors=actor_map)
