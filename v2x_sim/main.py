"""Executable demonstration for driving SUMO with TraCI."""

from __future__ import annotations

import argparse

from .logger import build_logger
from .sumo_runner import RoadUserState, SumoConfig, SumoRunner


def parse_args() -> argparse.Namespace:
    """Parse command-line options for the TraCI demo script."""
    parser = argparse.ArgumentParser(description="Run minimal SUMO + TraCI demo")
    parser.add_argument(
        "--scenario",
        default="scenarios/minimal_v2x/scenario.sumocfg",
        help="Path to SUMO .sumocfg file",
    )
    parser.add_argument("--steps", type=int, default=50, help="Number of simulation steps")
    parser.add_argument("--gui", action="store_true", help="Launch sumo-gui instead of sumo")
    parser.add_argument(
        "--step-length",
        type=float,
        default=0.1,
        help="Override simulation step length (seconds)",
    )
    return parser.parse_args()


def _format_actor(prefix: str, state: RoadUserState) -> str:
    speed = f"{state.speed:.2f} m/s" if state.speed is not None else "n/a"
    return (
        f"  {prefix:<4} {state.actor_id:<12} "
        f"pos=({state.x:7.2f}, {state.y:7.2f}) speed={speed}"
    )


def run() -> int:
    """Run demonstration loop and print simulation state at each step."""
    args = parse_args()
    log = build_logger()

    runner = SumoRunner(
        SumoConfig(
            scenario_file=args.scenario,
            use_gui=args.gui,
            step_length=args.step_length,
        )
    )

    try:
        runner.start()
    except (FileNotFoundError, RuntimeError) as exc:
        log.error("Unable to start SUMO simulation: %s", exc)
        return 1

    log.info("Starting TraCI loop for %d steps", args.steps)

    try:
        for _ in range(args.steps):
            snapshot = runner.step()
            log.info(
                "t=%.2f s | vehicles=%d | pedestrians=%d",
                snapshot.time_s,
                len(snapshot.vehicles),
                len(snapshot.pedestrians),
            )

            for vehicle_id in sorted(snapshot.vehicles):
                log.info(_format_actor("veh", snapshot.vehicles[vehicle_id]))

            for person_id in sorted(snapshot.pedestrians):
                log.info(_format_actor("ped", snapshot.pedestrians[person_id]))
    except RuntimeError as exc:
        log.error("Simulation error: %s", exc)
        return 1
    finally:
        runner.stop()

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
