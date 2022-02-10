from eth2spec.altair.mainnet import (
    AttestationData,
    BeaconBlock,
)

from .utils.types import (
    BLSSignature,
    AttestationDuty,
    ProposerDuty,
    SlashingDB,
)
from .utils.helpers.slashing_db import (
    is_slashable_attestation_data,
    is_slashable_block,
)


"""
Consensus Specification
"""


def consensus_is_valid_attestation_data(slashing_db: SlashingDB,
                                        attestation_data: AttestationData, attestation_duty: AttestationDuty) -> bool:
    """Determines if the given attestation is valid for the attestation duty.
    """
    return \
        attestation_data.slot == attestation_duty.slot and \
        attestation_data.index == attestation_duty.committee_index and \
        not is_slashable_attestation_data(slashing_db, attestation_data, attestation_duty.pubkey)


def consensus_on_attestation(slashing_db: SlashingDB, attestation_duty: AttestationDuty) -> AttestationData:
    """Consensus protocol between distributed validator nodes for attestation values.
    Returns the decided value.
    If this DV is the leader, it must use `bn_produce_attestation_data` for the proposed value.
    The consensus protocol must use `consensus_is_valid_attestation_data` to determine
    validity of the proposed attestation value.
    """
    pass


def consensus_is_valid_block(slashing_db: SlashingDB,
                             block: BeaconBlock, proposer_duty: ProposerDuty,
                             randao_reveal: BLSSignature) -> bool:
    """Determines if the given block is valid for the proposer duty.
    """
    # TODO: Add correct block.proposer_index check
    return block.slot == proposer_duty.slot and \
           block.body.randao_reveal == randao_reveal and \
           not is_slashable_block(slashing_db, block, proposer_duty.pubkey)


def consensus_on_block(slashing_db: SlashingDB,
                       proposer_duty: ProposerDuty, randao_reveal: BLSSignature) -> BeaconBlock:
    """Consensus protocol between distributed validator nodes for block values.
    Returns the decided value.
    If this DV is the leader, it must use `bn_produce_block` for the proposed value.
    The consensus protocol must use `consensus_is_valid_block` to determine
    validity of the proposed block value.
    """
    pass
