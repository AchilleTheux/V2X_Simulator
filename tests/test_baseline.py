from v2x_sim.baseline import BaselinePolicy
from v2x_sim.communication_model import CommunicationMode
from v2x_sim.danger_detector import DangerEvent


def test_baseline_switches_mode_by_distance() -> None:
    policy = BaselinePolicy(direct_distance_m=3.0)

    near_event = DangerEvent(step=1, vru_id="v1", vehicle_id="car1", distance_m=2.0)
    far_event = DangerEvent(step=1, vru_id="v1", vehicle_id="car1", distance_m=10.0)

    assert policy.choose_mode(near_event) == CommunicationMode.DIRECT
    assert policy.choose_mode(far_event) == CommunicationMode.RSU
