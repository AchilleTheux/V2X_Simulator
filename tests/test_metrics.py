from v2x_sim.communication_model import CommunicationMode
from v2x_sim.metrics import MetricsCollector


def test_metrics_summary_contains_expected_keys() -> None:
    metrics = MetricsCollector()
    metrics.record_step()
    metrics.record_danger_event()
    metrics.record_mode(CommunicationMode.DIRECT)

    summary = metrics.summary()

    assert summary["total_steps"] == 1
    assert summary["total_danger_events"] == 1
    assert summary["direct_count"] == 1
    assert summary["rsu_count"] == 0
