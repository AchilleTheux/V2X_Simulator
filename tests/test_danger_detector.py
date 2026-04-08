from v2x_sim.context_builder import SimulationContext
from v2x_sim.danger_detector import DangerDetector


def test_detector_returns_list() -> None:
    detector = DangerDetector(danger_distance_m=4.0)
    context = SimulationContext(step=1)

    events = detector.detect(context)

    assert isinstance(events, list)
