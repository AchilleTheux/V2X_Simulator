from unittest.mock import patch

import pytest

from v2x_sim.baseline import (
    AlwaysDirectStrategy,
    AlwaysInfrastructureStrategy,
    ThresholdHeuristicStrategy,
)
from v2x_sim.main import AlertRecord, _summarize_alerts, build_strategy, parse_args
from v2x_sim.communication_model import CommunicationMode


def test_parse_args_defaults() -> None:
    with patch("sys.argv", ["prog"]):
        args = parse_args()

    assert args.steps == 50
    assert args.gui is False
    assert args.scenario == "scenarios/minimal_v2x/scenario.sumocfg"
    assert args.step_length == 0.1
    assert args.strategy == "threshold"


def test_build_strategy_variants() -> None:
    assert isinstance(build_strategy("always_direct", threshold_m=6.0), AlwaysDirectStrategy)
    assert isinstance(
        build_strategy("always_infrastructure", threshold_m=6.0), AlwaysInfrastructureStrategy
    )
    assert isinstance(build_strategy("threshold", threshold_m=6.0), ThresholdHeuristicStrategy)


def test_summarize_alerts() -> None:
    records = [
        AlertRecord(
            time_s=1.0,
            vru_id="ped_0",
            vehicle_id="veh_0",
            distance_m=2.0,
            mode=CommunicationMode.DIRECT,
            success=True,
            latency_ms=40.0,
            reward=0.8,
        ),
        AlertRecord(
            time_s=2.0,
            vru_id="ped_1",
            vehicle_id="veh_1",
            distance_m=3.0,
            mode=CommunicationMode.RSU,
            success=False,
            latency_ms=120.0,
            reward=-1.0,
        ),
    ]

    summary = _summarize_alerts(records)

    assert summary["alerts"] == 2
    assert summary["successes"] == 1
    assert summary["failures"] == 1
    assert summary["avg_latency_ms"] == 80.0
    assert summary["cumulative_reward"] == pytest.approx(-0.2)
