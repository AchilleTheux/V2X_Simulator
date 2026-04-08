"""SUMO runner abstraction.

This module isolates all interactions with SUMO/TraCI so that other modules
can stay framework-agnostic and easier to test.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class SumoConfig:
    """Configuration required to launch a SUMO scenario."""

    scenario_file: str
    use_gui: bool = False
    step_length: float = 0.1


class SumoRunner:
    """Minimal lifecycle wrapper around a SUMO simulation process."""

    def __init__(self, config: SumoConfig) -> None:
        self.config = config
        self._is_running = False
        self._current_step = 0

    @property
    def is_running(self) -> bool:
        """Return True when the simulation has been started."""
        return self._is_running

    def start(self) -> None:
        """Start the simulation process.

        TODO: connect this method to TraCI startup commands.
        """
        self._is_running = True

    def step(self) -> int:
        """Advance simulation by one tick and return current step index."""
        if not self._is_running:
            raise RuntimeError("Simulation is not running. Call start() first.")
        self._current_step += 1
        return self._current_step

    def stop(self) -> None:
        """Stop simulation and release resources."""
        self._is_running = False

    def get_actor_ids(self) -> list[str]:
        """Return actor IDs currently visible in the simulation.

        TODO: replace this placeholder with TraCI queries.
        """
        return []
