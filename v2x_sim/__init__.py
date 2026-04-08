"""V2X communication simulator skeleton package."""

from .baseline import BaselinePolicy
from .communication_model import CommunicationDecision, CommunicationMode, CommunicationModel
from .context_builder import (
    ActorState,
    Context,
    ContextBuilder,
    SimulationContext,
    build_context,
    compute_distance,
)
from .danger_detector import (
    DangerAssessment,
    DangerDetector,
    DangerEvent,
    assess_proximity_danger,
    euclidean_distance,
)
from .metrics import MetricsCollector
from .sumo_runner import RoadUserState, SimulationStepSnapshot, SumoConfig, SumoRunner
from .thompson import ThompsonPolicy

__all__ = [
    "ActorState",
    "BaselinePolicy",
    "CommunicationDecision",
    "CommunicationMode",
    "CommunicationModel",
    "Context",
    "ContextBuilder",
    "DangerAssessment",
    "DangerDetector",
    "DangerEvent",
    "MetricsCollector",
    "RoadUserState",
    "SimulationStepSnapshot",
    "SimulationContext",
    "SumoConfig",
    "SumoRunner",
    "ThompsonPolicy",
    "build_context",
    "compute_distance",
    "assess_proximity_danger",
    "euclidean_distance",
]
