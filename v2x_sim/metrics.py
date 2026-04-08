"""Metrics collection for simulation episodes."""

from collections import Counter

from .communication_model import CommunicationMode


class MetricsCollector:
    """Collects lightweight counters for experiments."""

    def __init__(self) -> None:
        self.total_steps = 0
        self.total_danger_events = 0
        self.mode_counts: Counter[str] = Counter()

    def record_step(self) -> None:
        """Increment total simulation steps."""
        self.total_steps += 1

    def record_danger_event(self) -> None:
        """Increment total detected danger events."""
        self.total_danger_events += 1

    def record_mode(self, mode: CommunicationMode) -> None:
        """Increment selected communication mode counter."""
        self.mode_counts[mode.value] += 1

    def summary(self) -> dict[str, int]:
        """Return a serializable summary snapshot."""
        return {
            "total_steps": self.total_steps,
            "total_danger_events": self.total_danger_events,
            "direct_count": self.mode_counts[CommunicationMode.DIRECT.value],
            "rsu_count": self.mode_counts[CommunicationMode.RSU.value],
        }
