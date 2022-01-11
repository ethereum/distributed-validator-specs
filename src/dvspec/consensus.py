from eth2spec.altair.mainnet import (
    AttestationData,
    BeaconBlock,
)

from .utils.types import (
    AttestationDuty,
    ProposerDuty,
    SlashingDB,
    SyncCommitteeDuty,
    SyncCommitteeContribution,
)
from .utils.helpers import (
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


def consensus_is_valid_block(slashing_db: SlashingDB, block: BeaconBlock, proposer_duty: ProposerDuty) -> bool:
    """Determines if the given block is valid for the proposer duty.
    """
     # TODO: Add correct block.proposer_index check \ 
    return block.slot == proposer_duty.slot and \
           not is_slashable_block(slashing_db, block, proposer_duty.pubkey)


def consensus_on_block(slashing_db: SlashingDB, proposer_duty: ProposerDuty) -> AttestationData:
    """Consensus protocol between distributed validator nodes for block values.
    Returns the decided value.
    If this DV is the leader, it must use `bn_produce_block` for the proposed value.
    The consensus protocol must use `consensus_is_valid_block` to determine
    validity of the proposed block value.
    """
    pass


# TODO: Does sync committee contribution need slashing DB?
def consensus_is_valid_sync_committee_contribution(sync_committee_contribution: SyncCommitteeContribution,
                                                   sync_committee_duty: SyncCommitteeDuty) -> bool:
    """Determines if the given sync committee contribution is valid for the sync committee duty.
    """
    pass


def consensus_on_sync_committee_contribution(sync_committee_duty: SyncCommitteeDuty) -> SyncCommitteeContribution:
    """Consensus protocol between distributed validator nodes for sync committee contribution values.
    Returns the decided value.
    If this DV is the leader, it must use `bn_produce_sync_committee_contribution` for the proposed value.
    The consensus protocol must use `consensus_is_valid_sync_committee_contribution` to determine
    validity of the proposed block value.
    """
    pass
