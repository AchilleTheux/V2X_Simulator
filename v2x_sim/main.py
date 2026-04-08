"""Simulation entrypoint wiring SUMO, danger detection, strategies and rewards."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import random
from typing import Literal

from .baseline import (
    AlwaysDirectStrategy,
    AlwaysInfrastructureStrategy,
    DecisionStrategy,
    ThresholdHeuristicStrategy,
)
from .communication_model import (
    CommunicationMode,
    CommunicationParameters,
    CommunicationResult,
    simulate_direct,
    simulate_infrastructure,
)
from .context_builder import ContextBuilder
from .danger_detector import assess_proximity_danger
from .logger import build_logger
from .reward import compute_reward
from .sumo_runner import RoadUserState, SumoConfig, SumoRunner

StrategyName = Literal["always_direct", "always_infrastructure", "threshold"]


@dataclass(slots=True)
class AlertRecord:
    """Stores one dangerous interaction and communication outcome."""

    time_s: float
    vru_id: str
    vehicle_id: str
    distance_m: float
    mode: CommunicationMode
    success: bool
    latency_ms: float
    reward: float


def parse_args() -> argparse.Namespace:
    """Parse command-line options for the non-MAB end-to-end simulation."""
    parser = argparse.ArgumentParser(description="Run V2X simulation loop without MAB")
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
    parser.add_argument(
        "--strategy",
        choices=["always_direct", "always_infrastructure", "threshold"],
        default="threshold",
        help="Communication decision strategy to apply when danger is detected",
    )
    parser.add_argument(
        "--danger-distance-m",
        type=float,
        default=5.0,
        help="Distance threshold used to trigger danger alerts",
    )
    parser.add_argument(
        "--heuristic-distance-threshold-m",
        type=float,
        default=6.0,
        help="Distance threshold for ThresholdHeuristicStrategy",
    )
    parser.add_argument(
        "--reward-deadline-ms",
        type=float,
        default=100.0,
        help="Deadline used by compute_reward",
    )
    parser.add_argument("--seed", type=int, default=42, help="Seed for deterministic random draws")
    parser.add_argument(
        "--log-alerts",
        action="store_true",
        help="Log one line per danger alert and communication result",
    )
    return parser.parse_args()


def build_strategy(name: StrategyName, threshold_m: float) -> DecisionStrategy:
    """Return a strategy instance from CLI strategy name."""
    if name == "always_direct":
        return AlwaysDirectStrategy()
    if name == "always_infrastructure":
        return AlwaysInfrastructureStrategy()
    if name == "threshold":
        return ThresholdHeuristicStrategy(direct_distance_threshold_m=threshold_m)
    raise ValueError(f"Unknown strategy: {name}")


def _summarize_alerts(records: list[AlertRecord]) -> dict[str, float | int]:
    total_alerts = len(records)
    successes = sum(1 for record in records if record.success)
    failures = total_alerts - successes
    average_latency_ms = (
        sum(record.latency_ms for record in records) / total_alerts if total_alerts > 0 else 0.0
    )
    cumulative_reward = sum(record.reward for record in records)

    return {
        "alerts": total_alerts,
        "successes": successes,
        "failures": failures,
        "avg_latency_ms": average_latency_ms,
        "cumulative_reward": cumulative_reward,
    }


def _simulate_with_mode(
    *,
    mode: CommunicationMode,
    context_builder: ContextBuilder,
    simulation_time: float,
    vru_state: RoadUserState,
    vehicle_state: RoadUserState,
    rng: random.Random,
    comm_params: CommunicationParameters,
) -> tuple[CommunicationResult, float]:
    """Simulate communication using selected mode and return result + distance."""
    context = context_builder.build_decision_context(
        simulation_time=simulation_time,
        vru_position=(vru_state.x, vru_state.y),
        vehicle_position=(vehicle_state.x, vehicle_state.y),
        vru_speed=vru_state.speed,
        vehicle_speed=vehicle_state.speed,
    )

    if mode == CommunicationMode.DIRECT:
        result = simulate_direct(context=context, rng=rng, params=comm_params)
    else:
        result = simulate_infrastructure(context=context, rng=rng, params=comm_params)

    # Compute reward explicitly in the integration loop so policy evaluation stays clear.
    result.reward = compute_reward(result=result, deadline_ms=comm_params.reward_deadline_ms)
    return result, context.distance


def run() -> int:
    """Run complete non-MAB simulation loop over existing modules."""
    args = parse_args()
    log = build_logger()

    strategy = build_strategy(
        name=args.strategy,
        threshold_m=args.heuristic_distance_threshold_m,
    )
    context_builder = ContextBuilder(danger_distance_m=args.danger_distance_m)
    rng = random.Random(args.seed)
    comm_params = CommunicationParameters(reward_deadline_ms=args.reward_deadline_ms)

    runner = SumoRunner(
        SumoConfig(
            scenario_file=args.scenario,
            use_gui=args.gui,
            step_length=args.step_length,
        )
    )

    records: list[AlertRecord] = []

    try:
        runner.start()
    except (FileNotFoundError, RuntimeError) as exc:
        log.error("Unable to start SUMO simulation: %s", exc)
        return 1

    log.info(
        "Running simulation | strategy=%s | steps=%d | danger_distance=%.2f m",
        args.strategy,
        args.steps,
        args.danger_distance_m,
    )

    try:
        for _ in range(args.steps):
            snapshot = runner.step()

            for vru_id, vru_state in snapshot.pedestrians.items():
                for vehicle_id, vehicle_state in snapshot.vehicles.items():
                    danger = assess_proximity_danger(
                        vru_position=(vru_state.x, vru_state.y),
                        vehicle_position=(vehicle_state.x, vehicle_state.y),
                        danger_threshold_m=args.danger_distance_m,
                        vru_speed=vru_state.speed,
                        vehicle_speed=vehicle_state.speed,
                    )

                    if not danger.is_danger:
                        continue

                    decision_context = context_builder.build_decision_context(
                        simulation_time=snapshot.time_s,
                        vru_position=(vru_state.x, vru_state.y),
                        vehicle_position=(vehicle_state.x, vehicle_state.y),
                        vru_speed=vru_state.speed,
                        vehicle_speed=vehicle_state.speed,
                    )
                    mode = strategy.choose_mode(decision_context)

                    result, distance_m = _simulate_with_mode(
                        mode=mode,
                        context_builder=context_builder,
                        simulation_time=snapshot.time_s,
                        vru_state=vru_state,
                        vehicle_state=vehicle_state,
                        rng=rng,
                        comm_params=comm_params,
                    )

                    record = AlertRecord(
                        time_s=snapshot.time_s,
                        vru_id=vru_id,
                        vehicle_id=vehicle_id,
                        distance_m=distance_m,
                        mode=result.mode_chosen,
                        success=result.success,
                        latency_ms=result.latency_ms,
                        reward=result.reward,
                    )
                    records.append(record)

                    if args.log_alerts:
                        log.info(
                            "ALERT t=%.2f | %s-%s | d=%.2f m | mode=%s | success=%s | latency=%.1f ms | reward=%.3f",
                            record.time_s,
                            record.vru_id,
                            record.vehicle_id,
                            record.distance_m,
                            record.mode.value,
                            record.success,
                            record.latency_ms,
                            record.reward,
                        )
    except RuntimeError as exc:
        log.error("Simulation error: %s", exc)
        return 1
    finally:
        runner.stop()

    summary = _summarize_alerts(records)
    log.info("Simulation summary")
    log.info("  alerts: %d", summary["alerts"])
    log.info("  successes: %d", summary["successes"])
    log.info("  failures: %d", summary["failures"])
    log.info("  avg_latency_ms: %.2f", summary["avg_latency_ms"])
    log.info("  cumulative_reward: %.3f", summary["cumulative_reward"])

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
