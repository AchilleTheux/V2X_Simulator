from pathlib import Path

import pytest

from v2x_sim.sumo_runner import SumoConfig, SumoRunner


class _FakeSimulationApi:
    def __init__(self) -> None:
        self.time_s = 0.0

    def getTime(self) -> float:
        return self.time_s


class _FakeVehicleApi:
    def getIDList(self) -> list[str]:
        return ["veh_0"]

    def getPosition(self, actor_id: str) -> tuple[float, float]:
        assert actor_id == "veh_0"
        return (10.0, 0.0)

    def getSpeed(self, actor_id: str) -> float:
        assert actor_id == "veh_0"
        return 13.89


class _FakePersonApi:
    def getIDList(self) -> list[str]:
        return ["ped_0"]

    def getPosition(self, actor_id: str) -> tuple[float, float]:
        assert actor_id == "ped_0"
        return (10.0, 1.5)

    def getSpeed(self, actor_id: str) -> float:
        assert actor_id == "ped_0"
        return 1.4


class _FakeTraci:
    def __init__(self) -> None:
        self.simulation = _FakeSimulationApi()
        self.vehicle = _FakeVehicleApi()
        self.person = _FakePersonApi()
        self.started_with: list[str] | None = None
        self.closed = False

    def start(self, cmd: list[str]) -> None:
        self.started_with = cmd

    def simulationStep(self) -> None:
        self.simulation.time_s += 0.1

    def close(self) -> None:
        self.closed = True


def test_runner_start_step_stop_with_mocked_traci(tmp_path: Path) -> None:
    sumocfg = tmp_path / "scenario.sumocfg"
    sumocfg.write_text("<configuration/>", encoding="utf-8")

    traci = _FakeTraci()
    runner = SumoRunner(
        config=SumoConfig(scenario_file=str(sumocfg), step_length=0.1),
        traci_module=traci,
    )

    runner.start()
    assert runner.is_running
    assert traci.started_with is not None
    assert traci.started_with[0] == "sumo"
    assert traci.started_with[1:3] == ["-c", str(sumocfg)]

    snapshot = runner.step()

    assert snapshot.time_s == pytest.approx(0.1)
    assert set(snapshot.vehicles) == {"veh_0"}
    assert set(snapshot.pedestrians) == {"ped_0"}
    assert snapshot.vehicles["veh_0"].speed == pytest.approx(13.89)
    assert snapshot.pedestrians["ped_0"].speed == pytest.approx(1.4)

    runner.stop()
    assert traci.closed
    assert not runner.is_running


def test_start_raises_if_sumocfg_missing() -> None:
    runner = SumoRunner(SumoConfig(scenario_file="does_not_exist.sumocfg"), traci_module=_FakeTraci())

    with pytest.raises(FileNotFoundError):
        runner.start()
