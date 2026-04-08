from pathlib import Path

import pytest

from v2x_sim.communication_model import CommunicationMode
from v2x_sim.metrics import (
    AlertMetricsRecord,
    ContextSummary,
    MetricsCollector,
    aggregate_alert_metrics,
    export_alert_records_csv,
)


def _record(
    *,
    mode: CommunicationMode,
    success: bool,
    latency_ms: float,
    reward: float,
) -> AlertMetricsRecord:
    return AlertMetricsRecord(
        time_s=1.0,
        context=ContextSummary(
            distance_m=3.0,
            danger=True,
            rsu_available=True,
            rsu_load=0.3,
            obstacle_present=False,
        ),
        strategy="threshold",
        mode_chosen=mode,
        success=success,
        latency_ms=latency_ms,
        reward=reward,
        vru_id="ped_0",
        vehicle_id="veh_0",
    )


def test_aggregate_alert_metrics_basic() -> None:
    records = [
        _record(mode=CommunicationMode.DIRECT, success=True, latency_ms=40.0, reward=0.9),
        _record(mode=CommunicationMode.RSU, success=False, latency_ms=120.0, reward=-1.0),
        _record(mode=CommunicationMode.DIRECT, success=True, latency_ms=60.0, reward=0.7),
    ]

    summary = aggregate_alert_metrics(records)

    assert summary.total_alerts == 3
    assert summary.success_count == 2
    assert summary.failure_count == 1
    assert summary.success_rate == pytest.approx(2 / 3)
    assert summary.average_latency_ms == pytest.approx((40.0 + 120.0 + 60.0) / 3)
    assert summary.cumulative_reward == pytest.approx(0.6)
    assert summary.direct_ratio == pytest.approx(2 / 3)
    assert summary.infrastructure_ratio == pytest.approx(1 / 3)


def test_aggregate_alert_metrics_empty() -> None:
    summary = aggregate_alert_metrics([])

    assert summary.total_alerts == 0
    assert summary.success_rate == 0.0
    assert summary.average_latency_ms == 0.0
    assert summary.cumulative_reward == 0.0
    assert summary.direct_ratio == 0.0
    assert summary.infrastructure_ratio == 0.0


def test_export_alert_records_csv(tmp_path: Path) -> None:
    records = [_record(mode=CommunicationMode.DIRECT, success=True, latency_ms=30.0, reward=0.95)]

    output = export_alert_records_csv(records, tmp_path / "alerts.csv")

    content = output.read_text(encoding="utf-8")
    assert "time_s" in content
    assert "mode_chosen" in content
    assert "direct" in content


def test_metrics_collector_summary_contains_expected_keys() -> None:
    metrics = MetricsCollector()
    metrics.record_step()
    metrics.record_alert(
        _record(mode=CommunicationMode.DIRECT, success=True, latency_ms=50.0, reward=0.8)
    )

    summary = metrics.summary()

    assert summary["total_steps"] == 1
    assert summary["total_danger_events"] == 1
    assert summary["direct_count"] == 1
    assert summary["rsu_count"] == 0
    assert summary["total_alerts"] == 1
    assert summary["success_rate"] == 1.0
