"""Context construction utilities for danger and decision layers."""

from __future__ import annotations

from dataclasses import dataclass, field
import math

Position = tuple[float, float]


@dataclass(slots=True, frozen=True)
class Context:
    """Decision-oriented context for one VRU/vehicle pair at one time step."""

    simulation_time: float
    vru_position: Position
    vehicle_position: Position
    distance: float
    danger: bool
    rsu_available: bool
    rsu_load: float
    obstacle_present: bool


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
    """Generic snapshot of all actors at one simulation step."""

    step: int
    actors: dict[str, ActorState] = field(default_factory=dict)


def compute_distance(vru_position: Position, vehicle_position: Position) -> float:
    """Compute Euclidean distance between VRU and vehicle."""
    return math.hypot(vru_position[0] - vehicle_position[0], vru_position[1] - vehicle_position[1])


def build_context(
    *,
    simulation_time: float,
    vru_position: Position,
    vehicle_position: Position,
    danger_threshold_m: float,
    vru_speed: float | None = None,
    vehicle_speed: float | None = None,
) -> Context:
    """Build a decision context from minimal simulation inputs.

    `vru_speed` and `vehicle_speed` are accepted now to simplify later
    integration of TTC-based features.
    """
    if danger_threshold_m < 0:
        raise ValueError("danger_threshold_m must be >= 0")

    distance = compute_distance(vru_position=vru_position, vehicle_position=vehicle_position)
    danger = distance < danger_threshold_m

    obstacle_present = _simulate_obstacle_present(simulation_time=simulation_time, distance=distance)
    rsu_available = _simulate_rsu_available(
        simulation_time=simulation_time,
        obstacle_present=obstacle_present,
    )
    rsu_load = _simulate_rsu_load(
        simulation_time=simulation_time,
        distance=distance,
        obstacle_present=obstacle_present,
    )

    # Placeholder for future TTC logic.
    _ = (vru_speed, vehicle_speed)

    return Context(
        simulation_time=float(simulation_time),
        vru_position=vru_position,
        vehicle_position=vehicle_position,
        distance=distance,
        danger=danger,
        rsu_available=rsu_available,
        rsu_load=rsu_load,
        obstacle_present=obstacle_present,
    )


class ContextBuilder:
    """Builds simulation and decision contexts.

    - `build(...)`: compatibility helper to aggregate all actors in a scene.
    - `build_decision_context(...)`: specialized VRU/vehicle context for policies.
    """

    def __init__(self, danger_distance_m: float = 5.0) -> None:
        self.danger_distance_m = danger_distance_m

    def build(self, step: int, actors: list[ActorState]) -> SimulationContext:
        """Create a scene snapshot from actor states."""
        actor_map = {actor.actor_id: actor for actor in actors}
        return SimulationContext(step=step, actors=actor_map)

    def build_decision_context(
        self,
        *,
        simulation_time: float,
        vru_position: Position,
        vehicle_position: Position,
        vru_speed: float | None = None,
        vehicle_speed: float | None = None,
    ) -> Context:
        """Create the decision context used by communication policies/MAB."""
        return build_context(
            simulation_time=simulation_time,
            vru_position=vru_position,
            vehicle_position=vehicle_position,
            danger_threshold_m=self.danger_distance_m,
            vru_speed=vru_speed,
            vehicle_speed=vehicle_speed,
        )


def _simulate_rsu_available(*, simulation_time: float, obstacle_present: bool) -> bool:
    """Deterministic RSU availability model for early experiments.

    Rule: RSU is unavailable for 5 seconds every 30-second cycle. If an
    obstacle is present, availability is forced to False.
    """
    cycle_time = simulation_time % 30.0
    in_unavailable_window = 10.0 <= cycle_time < 15.0
    return (not in_unavailable_window) and (not obstacle_present)


def _simulate_rsu_load(*, simulation_time: float, distance: float, obstacle_present: bool) -> float:
    """Deterministic RSU load in [0, 1] for testing.

    The load follows a simple sawtooth profile over time, then receives small
    deterministic increments when actors are close and when an obstacle exists.
    """
    phase = (simulation_time % 20.0) / 20.0
    load = 0.20 + 0.60 * phase

    if distance < 10.0:
        load += 0.05
    if obstacle_present:
        load += 0.15

    return min(1.0, max(0.0, load))


def _simulate_obstacle_present(*, simulation_time: float, distance: float) -> bool:
    """Deterministic obstacle signal for reproducible tests.

    Rule: an obstacle is present during the first 3 seconds of each 12-second
    cycle, and only when actors are within 20 meters.
    """
    return (simulation_time % 12.0) < 3.0 and distance <= 20.0
