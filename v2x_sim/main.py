"""Entry point for the V2X simulation skeleton."""

import argparse

from .communication_model import CommunicationModel
from .context_builder import ContextBuilder
from .danger_detector import DangerDetector
from .logger import build_logger
from .metrics import MetricsCollector
from .sumo_runner import SumoConfig, SumoRunner


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="V2X communication simulator skeleton")
    parser.add_argument("--scenario", default="scenarios/example.sumocfg")
    parser.add_argument("--steps", type=int, default=10)
    parser.add_argument("--gui", action="store_true", help="Launch SUMO GUI")
    return parser.parse_args()


def run() -> int:
    """Run a minimal simulation loop with placeholders."""
    args = parse_args()
    log = build_logger()

    runner = SumoRunner(
        SumoConfig(
            scenario_file=args.scenario,
            use_gui=args.gui,
        )
    )
    context_builder = ContextBuilder()
    detector = DangerDetector()
    comm_model = CommunicationModel()
    metrics = MetricsCollector()

    runner.start()
    try:
        for _ in range(args.steps):
            step = runner.step()
            metrics.record_step()

            # Placeholder: actor extraction from SUMO is not wired yet.
            context = context_builder.build(step=step, actors=[])
            danger_events = detector.detect(context)

            for event in danger_events:
                metrics.record_danger_event()
                decision = comm_model.choose_mode(event=event, context=context)
                metrics.record_mode(decision.mode)
    finally:
        runner.stop()

    log.info("Simulation summary: %s", metrics.summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
