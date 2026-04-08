from unittest.mock import patch

import pytest

from v2x_sim.baseline import (
    AlwaysDirectStrategy,
    AlwaysInfrastructureStrategy,
    ThresholdHeuristicStrategy,
)
from v2x_sim.main import build_strategy, parse_args
from v2x_sim.thompson import ThompsonSamplingStrategy


def test_parse_args_defaults() -> None:
    with patch("sys.argv", ["prog"]):
        args = parse_args()

    assert args.steps == 50
    assert args.gui is False
    assert args.scenario == "scenarios/minimal_v2x/scenario.sumocfg"
    assert args.step_length == 0.1
    assert args.strategy == "threshold_heuristic"
    assert args.export_csv == ""


def test_build_strategy_variants() -> None:
    assert isinstance(build_strategy("always_direct", threshold_m=6.0), AlwaysDirectStrategy)
    assert isinstance(
        build_strategy("always_infrastructure", threshold_m=6.0), AlwaysInfrastructureStrategy
    )
    assert isinstance(build_strategy("threshold", threshold_m=6.0), ThresholdHeuristicStrategy)
    assert isinstance(
        build_strategy("threshold_heuristic", threshold_m=6.0), ThresholdHeuristicStrategy
    )
    assert isinstance(build_strategy("thompson", threshold_m=6.0), ThompsonSamplingStrategy)


def test_build_strategy_unknown_raises() -> None:
    with pytest.raises(ValueError):
        build_strategy("invalid", threshold_m=6.0)  # type: ignore[arg-type]
