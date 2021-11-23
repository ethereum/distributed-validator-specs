from dvspec.eth_node_interface import (
    AttestationDuty, ProposerDuty,
    AttestationData, BeaconBlock,
    bn_get_attestation_duties_for_epoch,
    bn_get_attestation_data,
    bn_submit_attestation,
    bn_get_proposer_duties_for_epoch,
    bn_produce_block,
    bn_submit_block,
    vc_is_slashable_attestation_data,
    vc_sign_attestation,
    vc_is_slashable_block,
    vc_sign_block,
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


"""
Attestation Production Process:
1. At the start of every epoch, get attestation duties for epoch+1 by running
    bn_get_attestation_duties_for_epoch(validator_indices, epoch+1)
2. For each attestation_duty recevied in Step 1, schedule
    serve_attestation_duty(attestation_duty) at 1/3rd way through the slot
    attestation_duty.slot

See notes here:
https://github.com/ethereum/beacon-APIs/blob/05c1bc142e1a3fb2a63c79098743776241341d08/validator-flow.md#attestation
"""

def serve_attestation_duty(attestation_duty):
    # Obtain lock on consensus_on_attestation here.
    # Only a single consensus_on_attestation instance should be
    # running at any given time
    attestation_data = consensus_on_attestation(attestation_duty)

    # 1. Threshold sign attestation from local VC
    threshold_signed_attestation = vc_sign_attestation(attestation_data, attestation_duty)
    # 2. Broadcast threshold signed attestation
    # 3. Reconstruct complete signed attestation by combining threshold signed attestations
    complete_signed_attestation = threshold_signed_attestation
    # 4. Send complete signed attestation to BN for broadcast
    bn_submit_attestation(complete_signed_attestation)

    # Release lock on consensus_on_attestation here.

"""
Block Production Process:
1. At the start of every epoch, get proposer duties for epoch+1 by running
    bn_get_proposer_duties_for_epoch(epoch+1)
2. For each proposer_duty recevied in Step 1 for our validators, schedule
    serve_proposer_duty(proposer_duty) at beginning of slot proposer_duty.slot

See notes here:
https://github.com/ethereum/beacon-APIs/blob/05c1bc142e1a3fb2a63c79098743776241341d08/validator-flow.md#block-proposing
"""

def serve_proposer_duty(proposer_duty):
    # Obtain lock on consensus_on_block here.
    # Only a single consensus_on_block instance should be
    # running at any given time
    block = consensus_on_block(proposer_duty)

    # 1. Threshold sign block from local VC
    threshold_signed_block = vc_sign_block(block, proposer_duty)
    # 2. Broadcast threshold signed block
    # 3. Reconstruct complete signed block by combining threshold signed blocks
    complete_signed_block = threshold_signed_block
    # 4. Send complete signed block to BN for broadcast
    bn_submit_block(complete_signed_block)

    # Release lock on consensus_on_block here.
