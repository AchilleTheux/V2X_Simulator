from v2x_sim.communication_model import CommunicationMode, CommunicationModel
from v2x_sim.context_builder import SimulationContext
from v2x_sim.danger_detector import DangerEvent


def test_choose_mode_defaults_to_direct() -> None:
    model = CommunicationModel()
    context = SimulationContext(step=10)
    event = DangerEvent(step=10, vru_id="vru_1", vehicle_id="veh_3", distance_m=2.0)

    decision = model.choose_mode(event=event, context=context)

    assert decision.mode == CommunicationMode.DIRECT
