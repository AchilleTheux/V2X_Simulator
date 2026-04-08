from unittest.mock import patch

from v2x_sim.main import parse_args


def test_parse_args_defaults() -> None:
    with patch("sys.argv", ["prog"]):
        args = parse_args()

    assert args.steps == 50
    assert args.gui is False
    assert args.scenario == "scenarios/minimal_v2x/scenario.sumocfg"
    assert args.step_length == 0.1
