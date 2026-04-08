"""Communication channel selection abstractions."""

from dataclasses import dataclass
from enum import Enum

from .context_builder import SimulationContext
from .danger_detector import DangerEvent


class CommunicationMode(str, Enum):
    """Candidate communication modes in V2X."""

    DIRECT = "direct"
    RSU = "rsu"


@dataclass(slots=True)
class CommunicationDecision:
    """Decision output produced by a communication policy/model."""

    mode: CommunicationMode
    reason: str


class CommunicationModel:
    """Base communication decision model.

    Later this class can delegate mode selection to baseline or MAB policies.
    """

    def choose_mode(
        self,
        event: DangerEvent,
        context: SimulationContext,
    ) -> CommunicationDecision:
        """Select communication mode for one danger event.

        Placeholder behavior currently defaults to direct communication.
        """
        _ = (event, context)
        return CommunicationDecision(
            mode=CommunicationMode.DIRECT,
            reason="Default skeleton policy",
        )
