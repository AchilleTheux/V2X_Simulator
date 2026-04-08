from unittest.mock import patch

from v2x_sim.main import parse_args


def test_parse_args_defaults() -> None:
    with patch("sys.argv", ["prog"]):
        args = parse_args()

    assert args.steps == 10
    assert args.gui is False
