from typing import List

from eth2spec.altair.mainnet import Attestation, SignedBeaconBlock

from .utils.types import (
    SyncCommitteeSignature,
    BLSSignature
)

"""
Networking Specification
"""


def broadcast_attestation_signature_share(attestation_signature_share: Attestation) -> None:
    """Broadcasts attestation signature shares among DV peer nodes.
    """
    pass


def listen_for_randao_reveal_signature_shares() -> List[BLSSignature]:
    """Returns a list of any randao reveal signature shares that can be combined to construct
    a complete signed value.
    """
    pass


def listen_for_attestation_signature_shares() -> List[Attestation]:
    """Returns a list of any attestations signature shares that can be combined to construct
    a complete signed attestation.
    """
    pass


def construct_signed_randao_reveal(value_signature_shares: List[BLSSignature]) -> BLSSignature:
    """Construct a complete signed randao reveal value from signature shares.
    """
    pass


def construct_signed_attestation(attestation_signature_shares: List[Attestation]) -> Attestation:
    """Construct a complete signed attestation from attestation signature shares.
    """
    pass


def broadcast_randao_reveal_signature_share(randao_reveal_signature_share: BLSSignature) -> None:
    """Broadcasts randao reveal signature shares among DV peer nodes.
    """
    pass


def broadcast_block_signature_share(block_signature_share: SignedBeaconBlock) -> None:
    """Broadcasts beacon block signature shares among DV peer nodes.
    """
    pass


def listen_for_block_signature_shares() -> List[SignedBeaconBlock]:
    """Returns a list of any block signature shares that can be combined to construct
    a complete signed block.
    """
    pass


def construct_signed_block(block_signature_shares: List[SignedBeaconBlock]) -> SignedBeaconBlock:
    """Construct a complete signed block from block signature shares.
    """
    pass


def broadcast_sync_committee_signature_signature_share(
        sync_committee_signature_signature_share: SyncCommitteeSignature) -> None:
    """Broadcasts sync committee signature signature shares among DV peer nodes.
    """
    pass


def listen_for_sync_committee_signatures_signature_shares() -> List[SyncCommitteeSignature]:
    """Returns a list of any sync committee signature signature shares that can be combined to construct
    a complete signed block.
    """
    pass


def construct_signed_sync_committee_signature(
        sync_committee_signatures_signature_share: List[SyncCommitteeSignature]) -> SyncCommitteeSignature:
    """Construct a complete signed sync committee signature from sync committee signature signature shares.
    """
    pass
