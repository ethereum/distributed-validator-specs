import eth2spec.phase0.mainnet as eth2spec

from .eth_node_interface import (
    AttestationData,
    BeaconBlock,
)
from .utils.types import (
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
    matching_slashing_db_data = [data for data in slashing_db.data if data.pubkey == pubkey]
    if matching_slashing_db_data == []:
        return True
    assert len(matching_slashing_db_data) == 1
    slashing_db_data = matching_slashing_db_data[0]
    # Check for EIP-3076 conditions:
    # https://eips.ethereum.org/EIPS/eip-3076#conditions
    if slashing_db_data.signed_attestations != []:
        min_target = min(attn.target_epoch for attn in slashing_db_data.signed_attestations)
        min_source = min(attn.source_epoch for attn in slashing_db_data.signed_attestations)
        if attestation_data.target.epoch <= min_target:
            return True
        if attestation_data.source.epoch < min_source:
            return True
    for past_attn in slashing_db_data.signed_attestations:
        past_attn_data = AttestationData(source=past_attn.source_epoch, target=past_attn.target_epoch)
        if eth2spec.is_slashable_attestation_data(past_attn_data, attestation_data):
            return True
    return False


def is_slashable_block(slashing_db: SlashingDB, block: BeaconBlock, pubkey: BLSPubkey) -> bool:
    matching_slashing_db_data = [data for data in slashing_db.data if data.pubkey == pubkey]
    if matching_slashing_db_data == []:
        return False
    assert len(matching_slashing_db_data) == 1
    slashing_db_data = matching_slashing_db_data[0]
    # Check for EIP-3076 conditions:
    # https://eips.ethereum.org/EIPS/eip-3076#conditions
    if slashing_db_data.signed_blocks != []:
        min_block = slashing_db_data.signed_blocks[0]
        for b in slashing_db_data.signed_blocks[1:]:
            if b.slot < min_block.slot:
                min_block = b
        if block.slot < min_block.slot:
            return True
    for past_block in slashing_db_data.signed_blocks:
        if past_block.slot == block.slot:
            if past_block.signing_root() != block.hash_tree_root():
                return True
    return False


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
