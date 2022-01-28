from typing import (
    List,
)

from dvspec.utils.types import (
    BLSSignature,
)

TEST_CACHE_RANDAO = None

def broadcast_threshold_signed_randao_reveal(threshold_signed_randao_reveal: BLSSignature) -> None:
    global TEST_CACHE_RANDAO 
    TEST_CACHE_RANDAO = threshold_signed_randao_reveal


def listen_for_threshold_signed_randao_reveal() -> List[BLSSignature]:
    global TEST_CACHE_RANDAO
    assert TEST_CACHE_RANDAO is not None
    return [TEST_CACHE_RANDAO]


def construct_signed_randao_reveal(threshold_signed_values: List[BLSSignature]) -> BLSSignature:
    """Construct a complete signed randao reveal value from threshold signed values.
    """
    return  threshold_signed_values[0]