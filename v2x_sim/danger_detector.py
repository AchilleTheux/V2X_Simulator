"""Danger proximity detection primitives.

Current implementation focuses on simple geometric proximity and keeps clear
extension points for future TTC-based logic.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from .context_builder import ActorState, SimulationContext

Position = tuple[float, float]


@dataclass(slots=True)
class DangerAssessment:
    """Result of a pairwise danger assessment."""

    distance_m: float
    is_danger: bool
    ttc_s: float | None = None


@dataclass(slots=True)
class DangerEvent:
    """Represents one dangerous proximity event between a VRU and a vehicle."""

    step: int
    vru_id: str
    vehicle_id: str
    distance_m: float
    ttc_s: float | None = None


def euclidean_distance(point_a: Position, point_b: Position) -> float:
    """Return Euclidean distance between two 2D points."""
    dx = point_a[0] - point_b[0]
    dy = point_a[1] - point_b[1]
    return math.hypot(dx, dy)


def assess_proximity_danger(
    *,
    vru_position: Position,
    vehicle_position: Position,
    danger_threshold_m: float,
    vru_speed: float | None = None,
    vehicle_speed: float | None = None,
) -> DangerAssessment:
    """Assess danger using Euclidean distance and a configurable threshold.

    Parameters `vru_speed` and `vehicle_speed` are currently unused but kept as
    part of the pure function signature to make later TTC integration easier.
    """
    if danger_threshold_m < 0:
        raise ValueError("danger_threshold_m must be >= 0")

    distance_m = euclidean_distance(vru_position, vehicle_position)
    is_danger = distance_m < danger_threshold_m

    # TTC placeholder: to be computed in a future iteration.
    _ = (vru_speed, vehicle_speed)

    return DangerAssessment(
        distance_m=distance_m,
        is_danger=is_danger,
        ttc_s=None,
    )


class DangerDetector:
    """Detect dangerous VRU-vehicle proximity situations from a scene context."""

    def __init__(self, danger_distance_m: float = 5.0) -> None:
        self.danger_distance_m = danger_distance_m

    def detect_pair(
        self,
        *,
        vru_state: ActorState,
        vehicle_state: ActorState,
    ) -> DangerAssessment:
        """Evaluate one VRU/vehicle pair with the current threshold."""
        return assess_proximity_danger(
            vru_position=(vru_state.x, vru_state.y),
            vehicle_position=(vehicle_state.x, vehicle_state.y),
            danger_threshold_m=self.danger_distance_m,
            vru_speed=vru_state.speed,
            vehicle_speed=vehicle_state.speed,
        )

    def detect(self, context: SimulationContext) -> list[DangerEvent]:
        """Return all dangerous VRU-vehicle events present in the context."""
        events: list[DangerEvent] = []

        vru_states = [actor for actor in context.actors.values() if _is_vru(actor.actor_type)]
        vehicle_states = [
            actor for actor in context.actors.values() if _is_vehicle(actor.actor_type)
        ]

        for vru in vru_states:
            for vehicle in vehicle_states:
                result = self.detect_pair(vru_state=vru, vehicle_state=vehicle)
                if result.is_danger:
                    events.append(
                        DangerEvent(
                            step=context.step,
                            vru_id=vru.actor_id,
                            vehicle_id=vehicle.actor_id,
                            distance_m=result.distance_m,
                            ttc_s=result.ttc_s,
                        )
                    )

        return events


def _is_vru(actor_type: str) -> bool:
    normalized = actor_type.strip().lower()
    return normalized in {"pedestrian", "cyclist", "bicycle", "vru"}


def _is_vehicle(actor_type: str) -> bool:
    normalized = actor_type.strip().lower()
    return normalized in {"vehicle", "car", "passenger", "truck", "bus"}
