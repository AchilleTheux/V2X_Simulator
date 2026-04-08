"""Danger proximity detection primitives."""

from dataclasses import dataclass

from .context_builder import SimulationContext


@dataclass(slots=True)
class DangerEvent:
    """Represents one proximity event between a VRU and a vehicle."""

    step: int
    vru_id: str
    vehicle_id: str
    distance_m: float


class DangerDetector:
    """Detects potentially unsafe situations in a scene.

    Current implementation is intentionally minimal.
    """

    def __init__(self, danger_distance_m: float = 5.0) -> None:
        self.danger_distance_m = danger_distance_m

    def detect(self, context: SimulationContext) -> list[DangerEvent]:
        """Return danger events found in the provided context.

        TODO: implement geometric checks between VRUs and vehicles.
        """
        _ = context
        return []
