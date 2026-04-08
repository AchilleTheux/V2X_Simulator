"""Metrics structures, aggregation helpers and CSV export."""

from __future__ import annotations

from collections import Counter
import csv
from dataclasses import dataclass
from pathlib import Path

from .communication_model import CommunicationMode


@dataclass(slots=True, frozen=True)
class ContextSummary:
    """Compact context snapshot stored with each alert event."""

    distance_m: float
    danger: bool
    rsu_available: bool
    rsu_load: float
    obstacle_present: bool


@dataclass(slots=True, frozen=True)
class AlertMetricsRecord:
    """Single alert event record for offline analysis/comparison."""

    time_s: float
    context: ContextSummary
    strategy: str
    mode_chosen: CommunicationMode
    success: bool
    latency_ms: float
    reward: float
    vru_id: str | None = None
    vehicle_id: str | None = None


@dataclass(slots=True, frozen=True)
class MetricsSummary:
    """Aggregated metrics across all alert records."""

    total_alerts: int
    success_count: int
    failure_count: int
    success_rate: float
    average_latency_ms: float
    cumulative_reward: float
    direct_ratio: float
    infrastructure_ratio: float


def aggregate_alert_metrics(records: list[AlertMetricsRecord]) -> MetricsSummary:
    """Aggregate alert-level records into evaluation-ready summary metrics."""
    total_alerts = len(records)
    if total_alerts == 0:
        return MetricsSummary(
            total_alerts=0,
            success_count=0,
            failure_count=0,
            success_rate=0.0,
            average_latency_ms=0.0,
            cumulative_reward=0.0,
            direct_ratio=0.0,
            infrastructure_ratio=0.0,
        )

    success_count = sum(1 for record in records if record.success)
    failure_count = total_alerts - success_count
    average_latency_ms = sum(record.latency_ms for record in records) / total_alerts
    cumulative_reward = sum(record.reward for record in records)

    direct_count = sum(1 for record in records if record.mode_chosen == CommunicationMode.DIRECT)
    infrastructure_count = sum(
        1 for record in records if record.mode_chosen == CommunicationMode.RSU
    )

    return MetricsSummary(
        total_alerts=total_alerts,
        success_count=success_count,
        failure_count=failure_count,
        success_rate=success_count / total_alerts,
        average_latency_ms=average_latency_ms,
        cumulative_reward=cumulative_reward,
        direct_ratio=direct_count / total_alerts,
        infrastructure_ratio=infrastructure_count / total_alerts,
    )


def export_alert_records_csv(records: list[AlertMetricsRecord], output_path: str | Path) -> Path:
    """Export alert-level records to CSV for post-run comparison."""
    path = Path(output_path)
    if path.parent and not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "time_s",
        "vru_id",
        "vehicle_id",
        "strategy",
        "mode_chosen",
        "success",
        "latency_ms",
        "reward",
        "distance_m",
        "danger",
        "rsu_available",
        "rsu_load",
        "obstacle_present",
    ]

    with path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "time_s": f"{record.time_s:.3f}",
                    "vru_id": record.vru_id or "",
                    "vehicle_id": record.vehicle_id or "",
                    "strategy": record.strategy,
                    "mode_chosen": record.mode_chosen.value,
                    "success": record.success,
                    "latency_ms": f"{record.latency_ms:.3f}",
                    "reward": f"{record.reward:.6f}",
                    "distance_m": f"{record.context.distance_m:.3f}",
                    "danger": record.context.danger,
                    "rsu_available": record.context.rsu_available,
                    "rsu_load": f"{record.context.rsu_load:.6f}",
                    "obstacle_present": record.context.obstacle_present,
                }
            )

    return path


class MetricsCollector:
    """In-memory metrics collector for one simulation run."""

    def __init__(self) -> None:
        self.total_steps = 0
        self.total_danger_events = 0
        self.mode_counts: Counter[str] = Counter()
        self.alert_records: list[AlertMetricsRecord] = []

    def record_step(self) -> None:
        self.total_steps += 1

    def record_danger_event(self) -> None:
        self.total_danger_events += 1

    def record_mode(self, mode: CommunicationMode) -> None:
        self.mode_counts[mode.value] += 1

    def record_alert(self, record: AlertMetricsRecord) -> None:
        """Store one alert event and update basic counters."""
        self.alert_records.append(record)
        self.record_danger_event()
        self.record_mode(record.mode_chosen)

    def aggregate(self) -> MetricsSummary:
        """Return aggregated metrics over all recorded alerts."""
        return aggregate_alert_metrics(self.alert_records)

    def export_csv(self, output_path: str | Path) -> Path:
        """Export recorded alerts to CSV."""
        return export_alert_records_csv(self.alert_records, output_path)

    def summary(self) -> dict[str, float | int]:
        """Backward-compatible dictionary summary."""
        aggregated = self.aggregate()
        return {
            "total_steps": self.total_steps,
            "total_danger_events": self.total_danger_events,
            "direct_count": self.mode_counts[CommunicationMode.DIRECT.value],
            "rsu_count": self.mode_counts[CommunicationMode.RSU.value],
            "total_alerts": aggregated.total_alerts,
            "success_rate": aggregated.success_rate,
            "average_latency_ms": aggregated.average_latency_ms,
            "cumulative_reward": aggregated.cumulative_reward,
            "direct_ratio": aggregated.direct_ratio,
            "infrastructure_ratio": aggregated.infrastructure_ratio,
        }
