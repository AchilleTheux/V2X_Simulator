"""Baseline decision strategies for communication mode selection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .communication_model import CommunicationMode
from .context_builder import Context
from .danger_detector import DangerEvent


class DecisionStrategy(Protocol):
    """Common interface for all baseline decision strategies."""

    def choose_mode(self, context: Context) -> CommunicationMode:
        """Return the communication mode selected for the given context."""

    def update(self, action: CommunicationMode, reward: int) -> None:
        """Update strategy from binary reward (1=success in time, 0=otherwise)."""


class _NoLearningStrategy:
    """Mixin for strategies that do not learn from feedback."""

    def update(self, action: CommunicationMode, reward: int) -> None:
        _ = (action, reward)


class AlwaysDirectStrategy(_NoLearningStrategy):
    """Always chooses direct VRU <-> vehicle communication."""

    def choose_mode(self, context: Context) -> CommunicationMode:
        _ = context
        return CommunicationMode.DIRECT


class AlwaysInfrastructureStrategy(_NoLearningStrategy):
    """Always chooses infrastructure (RSU) communication."""

    def choose_mode(self, context: Context) -> CommunicationMode:
        _ = context
        return CommunicationMode.RSU


@dataclass(slots=True)
class ThresholdHeuristicStrategy(_NoLearningStrategy):
    """Simple readable heuristic based on context features.

    Decision rule:
    1. If RSU is unavailable -> choose DIRECT (fallback).
    2. If an obstacle is present and RSU is available -> choose RSU.
    3. Otherwise, choose DIRECT when distance is below a threshold.
    4. In all other cases -> choose RSU.
    """

    direct_distance_threshold_m: float = 6.0

    def choose_mode(self, context: Context) -> CommunicationMode:
        if not context.rsu_available:
            return CommunicationMode.DIRECT

        if context.obstacle_present:
            return CommunicationMode.RSU

        if context.distance <= self.direct_distance_threshold_m:
            return CommunicationMode.DIRECT

        return CommunicationMode.RSU


class BaselinePolicy:
    """Backward-compatible baseline policy using only event distance.

    This class is kept for compatibility with previous steps of the project.
    New code should prefer `ThresholdHeuristicStrategy` on full `Context`.
    """

    def __init__(self, direct_distance_m: float = 3.0) -> None:
        self.direct_distance_m = direct_distance_m

    def choose_mode(self, event: DangerEvent) -> CommunicationMode:
        if event.distance_m <= self.direct_distance_m:
            return CommunicationMode.DIRECT
        return CommunicationMode.RSU
