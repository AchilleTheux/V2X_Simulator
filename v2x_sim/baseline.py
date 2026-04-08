"""Simple baseline policy for mode selection."""

from .communication_model import CommunicationMode
from .danger_detector import DangerEvent


class BaselinePolicy:
    """Rule-based baseline policy.

    The goal is to provide an interpretable reference before MAB policies.
    """

    def __init__(self, direct_distance_m: float = 3.0) -> None:
        self.direct_distance_m = direct_distance_m

    def choose_mode(self, event: DangerEvent) -> CommunicationMode:
        """Select mode from a simple distance threshold rule."""
        if event.distance_m <= self.direct_distance_m:
            return CommunicationMode.DIRECT
        return CommunicationMode.RSU
