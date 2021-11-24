from typing import List

from eth2spec.phase0.mainnet import Attestation, SignedBeaconBlock

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
    """Broadcasts a threshold signed attestation among DV peer nodes.
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
    """Broadcasts a threshold signed beacon block among DV peer nodes.
    """
    pass
