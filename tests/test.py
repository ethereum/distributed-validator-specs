import random

from eth2spec.phase0.mainnet import (
    MAX_COMMITTEES_PER_SLOT,
    SLOTS_PER_EPOCH,
    TARGET_COMMITTEE_SIZE,
    Attestation,
    AttestationData,
    BeaconBlock,
    Checkpoint,
    compute_epoch_at_slot,
    compute_start_slot_at_epoch,
    is_slashable_attestation_data,
    SignedBeaconBlock,
)
from typing import (
    Dict,
    Iterator,
)

from dvspec.utils.types import (
    AttestationDuty,
    BLSPubkey,
    BLSSignature,
    Bytes32,
    CommitteeIndex,
    Epoch,
    List,
    ProposerDuty,
    Slot,
    ValidatorIndex,
)

VALIDATOR_SET_SIZE = SLOTS_PER_EPOCH
VALIDATOR_INDICES = [1, 2, 3]
GENESIS_TIME = 0


def time_generator() -> Iterator[int]:
    time = GENESIS_TIME
    while True:
        yield time
        time += 1


timer = time_generator()


def get_current_time() -> int:
    # Returns current time
    return next(timer)


# Beacon Node Methods

def bn_get_attestation_duties_for_epoch(validator_indices: List[ValidatorIndex], epoch: Epoch) -> List[AttestationDuty]:
    attestation_duties = []
    for validator_index in validator_indices:
        start_slot_at_epoch = compute_start_slot_at_epoch(epoch)
        attestation_slot = start_slot_at_epoch + random.randrange(SLOTS_PER_EPOCH)
        attestation_duty = AttestationDuty(pubkey=BLSPubkey(0x00),
                                           validator_index=validator_index,
                                           committee_index=random.randrange(MAX_COMMITTEES_PER_SLOT),
                                           committee_length=TARGET_COMMITTEE_SIZE,
                                           committees_at_slot=MAX_COMMITTEES_PER_SLOT,
                                           validator_committee_index=random.randrange(TARGET_COMMITTEE_SIZE),
                                           slot=attestation_slot)
        attestation_duties.append(attestation_duty)
    return attestation_duties


def bn_get_attestation_data(slot: Slot, committee_index: CommitteeIndex) -> AttestationData:
    attestation_data = AttestationData(slot=slot,
                                       index=committee_index,
                                       source=Checkpoint(epoch=min(compute_epoch_at_slot(slot) - 1, 0)),
                                       target=Checkpoint(epoch=compute_epoch_at_slot(slot)))
    return attestation_data


def bn_submit_attestation(attestation: Attestation) -> None:
    pass


def bn_get_proposer_duties_for_epoch(epoch: Epoch) -> List[ProposerDuty]:
    proposer_duties = []
    validator_indices = [x for x in range(VALIDATOR_SET_SIZE)]
    random.shuffle(validator_indices)
    for i in range(SLOTS_PER_EPOCH):
        proposer_duties.append(ProposerDuty(pubkey=BLSPubkey(0x00), validator_index=validator_indices[i], slot=i))
    return proposer_duties


def bn_produce_block(slot: Slot, randao_reveal: BLSSignature, graffiti: Bytes32) -> BeaconBlock:
    block = BeaconBlock()
    block.slot = slot
    block.body.randao_reveal = randao_reveal
    block.body.graffiti = graffiti
    return block


# Validator Client Methods

attestation_slashing_db: Dict[BLSPubkey, AttestationData] = {}


def update_attestation_slashing_db(attestation_data: AttestationData, validator_pubkey: BLSPubkey) -> None:
    """Check that the attestation data is not slashable for the validator and
    add attestation to slashing DB.
    """
    if validator_pubkey not in attestation_slashing_db:
        attestation_slashing_db[validator_pubkey] = set()
    assert not vc_is_slashable_attestation_data(attestation_data, validator_pubkey)
    attestation_slashing_db[validator_pubkey].add(attestation_data)


def vc_is_slashable_attestation_data(attestation_data: AttestationData, validator_pubkey: BLSPubkey) -> bool:
    if validator_pubkey in attestation_slashing_db:
        for past_attestation_data in attestation_slashing_db[validator_pubkey]:
            if is_slashable_attestation_data(past_attestation_data, attestation_data):
                return True
    return False


def vc_sign_attestation(attestation_data: AttestationData, attestation_duty: AttestationDuty) -> Attestation:
    update_attestation_slashing_db(attestation_data, attestation_duty.pubkey)
    attestation = Attestation(data=attestation_data)
    attestation.aggregation_bits[attestation_duty.validator_committee_index] = 1
    return attestation


block_slashing_db: Dict[BLSPubkey, BeaconBlock] = {}


def update_block_slashing_db(block: BeaconBlock, validator_pubkey: BLSPubkey) -> None:
    """Check that the block is not slashable for the validator and
    add block to slashing DB.
    """
    if validator_pubkey not in block_slashing_db:
        block_slashing_db[validator_pubkey] = set()
    assert not vc_is_slashable_block(block, validator_pubkey)
    block_slashing_db[validator_pubkey].add(block)


def vc_is_slashable_block(block: BeaconBlock, validator_pubkey: BLSPubkey) -> bool:
    if validator_pubkey in block_slashing_db:
        for past_block in block_slashing_db[validator_pubkey]:
            if past_block.slot == block.slot:
                return True
    return False


def vc_sign_block(block: BeaconBlock, proposer_duty: ProposerDuty) -> SignedBeaconBlock:
    return SignedBeaconBlock(message=block)
