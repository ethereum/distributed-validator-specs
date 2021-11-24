from dvspec.eth_node_interface import (
    AttestationData,
    BeaconBlock,
)
from utils.types import (
    AttestationDuty,
    BLSPubkey,
    ProposerDuty,
    SlashingDB,
)

"""
Helper Functions
"""


def is_slashable_attestation_data(slashing_db: SlashingDB,
                                  attestation_data: AttestationData, pubkey: BLSPubkey) -> bool:
    pass


def is_slashable_block(slashing_db: SlashingDB, block: BeaconBlock, pubkey: BLSPubkey) -> bool:
    pass


"""
Consensus Specification
"""


def consensus_is_valid_attestation_data(slashing_db: SlashingDB,
                                        attestation_data: AttestationData, attestation_duty: AttestationDuty) -> bool:
    """Determines if the given attestation is valid for the attestation duty.
    """
    assert attestation_data.slot == attestation_duty.slot
    assert attestation_data.committee_index == attestation_duty.committee_index
    assert not is_slashable_attestation_data(slashing_db, attestation_data, attestation_duty.pubkey)
    return True


def consensus_on_attestation(attestation_duty: AttestationDuty) -> AttestationData:
    """Consensus protocol between distributed validator nodes for attestation values.
    Returns the decided value.
    The consensus protocol must use `consensus_is_valid_attestation_data` to determine
    validity of the proposed attestation value.
    """
    pass


def consensus_is_valid_block(slashing_db: SlashingDB, block: BeaconBlock, proposer_duty: ProposerDuty) -> bool:
    """Determines if the given block is valid for the proposer duty.
    """
    assert block.slot == proposer_duty.slot
    # TODO: Assert correct block.proposer_index
    assert not is_slashable_block(slashing_db, block, proposer_duty.pubkey)
    return True


def consensus_on_block(proposer_duty: ProposerDuty) -> AttestationData:
    """Consensus protocol between distributed validator nodes for block values.
    Returns the decided value.
    The consensus protocol must use `consensus_is_valid_block` to determine
    validity of the proposed block value.
    """
    pass
