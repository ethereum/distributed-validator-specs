from dvspec.eth_node_interface import (
    AttestationDuty, ProposerDuty,
    AttestationData, BeaconBlock,
    vc_is_slashable_attestation_data,
    vc_is_slashable_block,
)


"""
Consensus Specification
"""

def consensus_is_valid_attestation_data(attestation_data: AttestationData, attestation_duty: AttestationDuty) -> bool:
    """Determines if the given attestation is valid for the attestation duty.
    """
    assert attestation_data.slot == attestation_duty.slot
    assert attestation_data.committee_index == attestation_duty.committee_index
    assert not vc_is_slashable_attestation_data(attestation_data, attestation_duty.pubkey)

def consensus_on_attestation(attestation_duty: AttestationDuty) -> AttestationData:
    """Consensus protocol between distributed validator nodes for attestation values.
    Returns the decided value.
    The consensus protocol must use `consensus_is_valid_attestation_data` to determine
    validity of the proposed attestation value.
    """
    pass

def consensus_is_valid_block(block: BeaconBlock, proposer_duty: ProposerDuty) -> bool:
    """Determines if the given block is valid for the proposer duty.
    """
    assert block.slot == proposer_duty.slot
    # TODO: Assert correct block.proposer_index
    assert not vc_is_slashable_block(block, proposer_duty.pubkey)

def consensus_on_block(proposer_duty: ProposerDuty) -> AttestationData:
    """Consensus protocol between distributed validator nodes for block values.
    Returns the decided value.
    The consensus protocol must use `consensus_is_valid_block` to determine
    validity of the proposed block value.
    """
    pass
