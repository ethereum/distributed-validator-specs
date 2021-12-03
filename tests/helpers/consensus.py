from eth2spec.phase0.mainnet import (
    AttestationData,
    BeaconBlock,
)
from dvspec.utils.types import (
    AttestationDuty,
    ProposerDuty,
    SlashingDB,
)
from dvspec.utils.helpers import (
    is_slashable_attestation_data,
    is_slashable_block,
)
from dvspec.consensus import (
    consensus_is_valid_attestation_data,
    consensus_is_valid_block,
)

from tests.helpers.eth_node_interface import (
    bn_produce_attestation_data,
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
    attestation_data = bn_produce_attestation_data(attestation_duty.slot, attestation_duty.committee_index)
    assert consensus_is_valid_attestation_data(slashing_db, attestation_data)
    return attestation_data


def consensus_on_block(slashing_db: SlashingDB, proposer_duty: ProposerDuty) -> AttestationData:
    """Consensus protocol between distributed validator nodes for block values.
    Returns the decided value.
    If this DV is the leader, it must use `bn_produce_block` for the proposed value.
    The consensus protocol must use `consensus_is_valid_block` to determine
    validity of the proposed block value.
    """
    pass
