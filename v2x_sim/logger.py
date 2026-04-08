"""Logging helpers for simulation runs and metrics records."""

from __future__ import annotations

import logging

from .metrics import AlertMetricsRecord, MetricsSummary


def build_logger(name: str = "v2x_sim", level: int = logging.INFO) -> logging.Logger:
    """Create and configure a shared logger instance."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
        )
        logger.addHandler(handler)

    return logger


def log_alert_record(logger: logging.Logger, record: AlertMetricsRecord) -> None:
    """Log one alert event in a compact and readable format."""
    logger.info(
        "ALERT t=%.2f | %s-%s | strategy=%s | d=%.2f m | mode=%s | success=%s | latency=%.1f ms | reward=%.3f",
        record.time_s,
        record.vru_id or "vru?",
        record.vehicle_id or "veh?",
        record.strategy,
        record.context.distance_m,
        record.mode_chosen.value,
        record.success,
        record.latency_ms,
        record.reward,
    )


def log_metrics_summary(logger: logging.Logger, summary: MetricsSummary) -> None:
    """Log aggregated simulation metrics."""
    logger.info("Simulation summary")
    logger.info("  total_alerts: %d", summary.total_alerts)
    logger.info("  successes: %d", summary.success_count)
    logger.info("  failures: %d", summary.failure_count)
    logger.info("  success_rate: %.3f", summary.success_rate)
    logger.info("  average_latency_ms: %.2f", summary.average_latency_ms)
    logger.info("  cumulative_reward: %.3f", summary.cumulative_reward)
    logger.info("  direct_ratio: %.3f", summary.direct_ratio)
    logger.info("  infrastructure_ratio: %.3f", summary.infrastructure_ratio)
