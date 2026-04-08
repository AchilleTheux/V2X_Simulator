from v2x_sim.communication_model import CommunicationMode
from v2x_sim.thompson import ThompsonPolicy


def test_thompson_update_changes_counters() -> None:
    policy = ThompsonPolicy()

    before = policy.stats[CommunicationMode.DIRECT].successes
    policy.update(CommunicationMode.DIRECT, reward=1.0)
    after = policy.stats[CommunicationMode.DIRECT].successes

    assert after == before + 1
    assert policy.select_mode() in set(policy.stats.keys())
