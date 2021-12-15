from typing import List

from eth2spec.altair.mainnet import Attestation, SignedBeaconBlock

from .utils.types import (
    SyncCommitteeSignature,
)

"""
Networking Specification
"""


def broadcast_threshold_signed_attestation(threshold_signed_attestation: Attestation) -> None:
    """Broadcasts a threshold signed attestation among DV peer nodes.
    """
    pass


def listen_for_threshold_signed_attestations() -> List[Attestation]:
    """Returns a list of any threshold signed attestations that can be combined to construct
    a complete signed attestation.
    """
    pass


def construct_signed_attestation(threshold_signed_attestations: List[Attestation]) -> Attestation:
    """Construct a complete signed attestation from threshold signed attestations.
    """
    pass


def broadcast_threshold_signed_block(threshold_signed_block: SignedBeaconBlock) -> None:
    """Broadcasts a threshold signed beacon block among DV peer nodes.
    """
    pass


def listen_for_threshold_signed_blocks() -> List[SignedBeaconBlock]:
    """Returns a list of any threshold signed blocks that can be combined to construct
    a complete signed block.
    """
    pass


def construct_signed_block(threshold_signed_blocks: List[SignedBeaconBlock]) -> SignedBeaconBlock:
    """Construct a complete signed block from threshold signed blocks.
    """
    pass


def broadcast_threshold_signed_sync_committee_signature(
        threshold_signed_sync_committee_signature: SyncCommitteeSignature) -> None:
    """Broadcasts a threshold signed sync committee signature among DV peer nodes.
    """
    pass


def listen_for_threshold_signed_sync_committee_signatures() -> List[SyncCommitteeSignature]:
    """Returns a list of any threshold signed sync committee signatures that can be combined to construct
    a complete signed block.
    """
    pass


def construct_signed_sync_committee_signature(
        threshold_signed_sync_committee_signatures: List[SyncCommitteeSignature]) -> SyncCommitteeSignature:
    """Construct a complete signed sync committee signature from threshold signed sync committee signatures.
    """
    pass
