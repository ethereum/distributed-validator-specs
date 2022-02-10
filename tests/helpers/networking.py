from typing import (
    List,
)

from dvspec.utils.types import (
    BLSSignature,
)


TEST_CACHE_RANDAO = None


def broadcast_randao_reveal_signature_share(randao_reveal_signature_share: BLSSignature) -> None:
    global TEST_CACHE_RANDAO
    TEST_CACHE_RANDAO = randao_reveal_signature_share


def listen_for_randao_reveal_signature_shares() -> List[BLSSignature]:
    global TEST_CACHE_RANDAO
    assert TEST_CACHE_RANDAO is not None
    return [TEST_CACHE_RANDAO]


def construct_signed_randao_reveal(value_signature_shares: List[BLSSignature]) -> BLSSignature:
    """Construct a complete signed randao reveal value from signature shares.
    """
    return value_signature_shares[0]
