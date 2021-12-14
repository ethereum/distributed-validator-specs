from typing import (
    Iterator,
)
from eth2spec.altair.mainnet import (
    SLOTS_PER_EPOCH,
    config,
)

from dvspec.utils.types import (
    Slot,
    Epoch,
)

GENESIS_TIME = 0

"""
Time Methods
"""


def time_generator() -> Iterator[int]:
    time = GENESIS_TIME
    while True:
        yield time
        time += 1


timer = time_generator()


def get_current_time() -> int:
    # Returns current time
    return next(timer)


def compute_slot_at_time(time: int) -> Slot:
    return (time - GENESIS_TIME) // config.SECONDS_PER_SLOT


def compute_epoch_at_time(time: int) -> Epoch:
    return compute_slot_at_time(time) // SLOTS_PER_EPOCH
