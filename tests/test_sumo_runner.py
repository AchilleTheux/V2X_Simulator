from v2x_sim.sumo_runner import SumoConfig, SumoRunner


def test_runner_lifecycle() -> None:
    runner = SumoRunner(SumoConfig(scenario_file="dummy.sumocfg"))

    assert not runner.is_running
    runner.start()
    assert runner.is_running

    step = runner.step()
    assert step == 1

    runner.stop()
    assert not runner.is_running
