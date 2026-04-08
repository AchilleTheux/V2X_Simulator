"""Thompson-sampling policy skeleton for future MAB integration."""

from dataclasses import dataclass

from .communication_model import CommunicationMode


@dataclass(slots=True)
class ArmStats:
    """Lightweight storage for one arm's reward counters."""

    successes: int = 1
    failures: int = 1


class ThompsonPolicy:
    """Minimal placeholder for a Thompson-sampling policy.

    Current implementation only stores counters. Probabilistic arm selection
    will be added in a later iteration.
    """

    def __init__(self) -> None:
        self.stats: dict[CommunicationMode, ArmStats] = {
            CommunicationMode.DIRECT: ArmStats(),
            CommunicationMode.RSU: ArmStats(),
        }

    def select_mode(self) -> CommunicationMode:
        """Return selected mode.

        TODO: sample from Beta distributions for each arm.
        """
        return CommunicationMode.DIRECT

    def update(self, mode: CommunicationMode, reward: float) -> None:
        """Update arm counters from observed reward.

        Reward convention for now:
        - reward >= 0.5 -> success
        - reward < 0.5  -> failure
        """
        arm = self.stats[mode]
        if reward >= 0.5:
            arm.successes += 1
        else:
            arm.failures += 1
