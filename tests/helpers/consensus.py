from eth2spec.phase0.altair import (
    AttestationData,
    BeaconBlock,
)
from dvspec.utils.types import (
    BLSSignature,
    Bytes32,
    AttestationDuty,
    ProposerDuty,
    SlashingDB,
)
from dvspec.consensus import (
    consensus_is_valid_attestation_data,
    consensus_is_valid_block,
)

from tests.helpers.eth_node_interface import (
    bn_produce_attestation_data,
    bn_produce_block,
)


"""
Consensus Specification
"""


def consensus_on_attestation(slashing_db: SlashingDB, attestation_duty: AttestationDuty) -> AttestationData:
    """Consensus protocol between distributed validator nodes for attestation values.
    Returns the decided value.
    If this DV is the leader, it must use `bn_produce_attestation_data` for the proposed value.
    The consensus protocol must use `consensus_is_valid_attestation_data` to determine
    validity of the proposed attestation value.
    """
    # TODO: Use this method in tests instead of dvspec.consensus.consensus_on_attestation
    attestation_data = bn_produce_attestation_data(attestation_duty.slot, attestation_duty.committee_index)
    assert consensus_is_valid_attestation_data(slashing_db, attestation_data, attestation_duty)
    return attestation_data


def consensus_on_block(slashing_db: SlashingDB, proposer_duty: ProposerDuty) -> BeaconBlock:
    """Consensus protocol between distributed validator nodes for block values.
    Returns the decided value.
    If this DV is the leader, it must use `bn_produce_block` for the proposed value.
    The consensus protocol must use `consensus_is_valid_block` to determine
    validity of the proposed block value.
    """
    # TODO: Use this method in tests instead of dvspec.consensus.consensus_on_block
    block = bn_produce_block(proposer_duty.slot, BLSSignature(b'0'*96), Bytes32(b'0'*32))
    assert consensus_is_valid_block(slashing_db, block, proposer_duty)
    return block
