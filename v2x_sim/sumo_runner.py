"""SUMO/TraCI runner utilities.

This module centralizes simulation control so upper layers can consume
structured snapshots instead of calling TraCI directly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import importlib
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class SumoConfig:
    """Configuration for launching a SUMO scenario through TraCI."""

    scenario_file: str
    use_gui: bool = False
    step_length: float | None = 0.1
    additional_args: tuple[str, ...] = field(default_factory=tuple)


@dataclass(slots=True)
class RoadUserState:
    """Kinematic state for one actor at a simulation step."""

    actor_id: str
    x: float
    y: float
    speed: float | None


@dataclass(slots=True)
class SimulationStepSnapshot:
    """Structured state returned after each TraCI simulation step."""

    time_s: float
    vehicles: dict[str, RoadUserState]
    pedestrians: dict[str, RoadUserState]


class SumoRunner:
    """Launch and step a SUMO simulation via TraCI."""

    def __init__(self, config: SumoConfig, traci_module: Any | None = None) -> None:
        self.config = config
        self._traci = traci_module
        self._is_running = False

    @property
    def is_running(self) -> bool:
        """Whether TraCI is currently connected."""
        return self._is_running

    def start(self) -> None:
        """Start SUMO and open a TraCI connection."""
        if self._is_running:
            raise RuntimeError("Simulation is already running.")

        scenario_path = Path(self.config.scenario_file)
        if not scenario_path.exists():
            raise FileNotFoundError(f"SUMO config file not found: {scenario_path}")

        traci = self._traci or self._load_traci()
        command = self._build_sumo_command(scenario_path)

        try:
            traci.start(command)
        except Exception as exc:  # pragma: no cover - depends on runtime SUMO env
            raise RuntimeError(
                f"Failed to start SUMO with command: {' '.join(command)}"
            ) from exc

        self._traci = traci
        self._is_running = True

    def step(self) -> SimulationStepSnapshot:
        """Advance simulation by one step and return a typed snapshot."""
        traci = self._ensure_running()

        traci.simulationStep()
        time_s = float(traci.simulation.getTime())

        vehicles = self._collect_vehicle_states(traci)
        pedestrians = self._collect_pedestrian_states(traci)

        return SimulationStepSnapshot(
            time_s=time_s,
            vehicles=vehicles,
            pedestrians=pedestrians,
        )

    def stop(self) -> None:
        """Close TraCI connection if open."""
        if not self._is_running or self._traci is None:
            return

        try:
            self._traci.close()
        except Exception:
            # Close errors should not hide caller errors in finally blocks.
            pass
        finally:
            self._is_running = False

    def __enter__(self) -> SumoRunner:
        self.start()
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.stop()

    def _build_sumo_command(self, scenario_path: Path) -> list[str]:
        binary = "sumo-gui" if self.config.use_gui else "sumo"
        command = [binary, "-c", str(scenario_path)]

        if self.config.step_length is not None:
            command.extend(["--step-length", str(self.config.step_length)])

        command.extend(self.config.additional_args)
        return command

    def _ensure_running(self) -> Any:
        if not self._is_running or self._traci is None:
            raise RuntimeError("Simulation is not running. Call start() first.")
        return self._traci

    @staticmethod
    def _load_traci() -> Any:
        try:
            return importlib.import_module("traci")
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "TraCI module not found. Install SUMO and ensure Python bindings "
                "are available in PYTHONPATH."
            ) from exc

    @staticmethod
    def _collect_vehicle_states(traci: Any) -> dict[str, RoadUserState]:
        states: dict[str, RoadUserState] = {}
        for vehicle_id in traci.vehicle.getIDList():
            x, y = traci.vehicle.getPosition(vehicle_id)
            speed = float(traci.vehicle.getSpeed(vehicle_id))
            states[vehicle_id] = RoadUserState(
                actor_id=vehicle_id,
                x=float(x),
                y=float(y),
                speed=speed,
            )
        return states

    @staticmethod
    def _collect_pedestrian_states(traci: Any) -> dict[str, RoadUserState]:
        states: dict[str, RoadUserState] = {}
        for person_id in traci.person.getIDList():
            x, y = traci.person.getPosition(person_id)
            speed: float | None
            if hasattr(traci.person, "getSpeed"):
                speed = float(traci.person.getSpeed(person_id))
            else:
                speed = None

            states[person_id] = RoadUserState(
                actor_id=person_id,
                x=float(x),
                y=float(y),
                speed=speed,
            )
        return states
