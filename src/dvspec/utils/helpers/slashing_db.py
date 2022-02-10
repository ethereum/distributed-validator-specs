import eth2spec.altair.mainnet as eth2spec
from eth2spec.altair.mainnet import (
    AttestationData,
    BeaconBlock,
)

from ..types import (
    BLSPubkey,
    SlashingDB,
    SlashingDBData,
)

"""
Slashing DB Helper Functions
"""


def get_slashing_db_data_for_pubkey(slashing_db: SlashingDB, pubkey: BLSPubkey) -> SlashingDBData:
    """Get SlashingDBData for the pubkey in the slashing_db.
    Returns empty SlashingDBData for the pubkey if matching entry is not found in slashing_db.
    """
    matching_slashing_db_data = [data for data in slashing_db.data if data.pubkey == pubkey]
    if matching_slashing_db_data == []:
        # No matching SlashingDBData found. Returning empty SlashingDBData.
        return SlashingDBData(pubkey=pubkey, signed_blocks=[], signed_attestations=[])
    assert len(matching_slashing_db_data) == 1
    slashing_db_data = matching_slashing_db_data[0]
    return slashing_db_data


def is_slashable_attestation_data(slashing_db: SlashingDB,
                                  attestation_data: AttestationData, pubkey: BLSPubkey) -> bool:
    """Checks if the attestation data is slashable according to the slashing DB.
    """
    slashing_db_data = get_slashing_db_data_for_pubkey(slashing_db, pubkey)
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
    """Checks if the block is slashable according to the slashing DB.
    """
    slashing_db_data = get_slashing_db_data_for_pubkey(slashing_db, pubkey)
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
            if past_block.signing_root != block.hash_tree_root():
                return True
    return False
