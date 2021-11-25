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
    SignedBeaconBlock,
)
from typing import (
    Dict,
    Iterator,
)

from dvspec.consensus import (
    is_slashable_attestation_data,
    is_slashable_block,
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
    Root,
    SlashingDB,
    SlashingDBAttestation,
    SlashingDBBlock,
    Slot,
    ValidatorIndex,
)
from dvspec.spec import (
    CoValidator,
    DistributedValidator,
    State,
    ValidatorIdentity,
)

VALIDATOR_SET_SIZE = SLOTS_PER_EPOCH
GENESIS_TIME = 0


validator_identity = ValidatorIdentity(pubkey=BLSPubkey(0x00), index=1234)
co_validators = []
for i in range(1, 4):
    co_validators.append(CoValidator(validator_identity=validator_identity, pubkey=BLSPubkey(0x00), index=i))
slashing_db = SlashingDB(interchange_format_version=5,
                         genesis_validators_root=Root(),
                         data=[])
distributed_validator = DistributedValidator(validator_identity=validator_identity,
                                             co_validators=co_validators,
                                             slashing_db=slashing_db)
distributed_validators = [distributed_validator]
state = State(distributed_validators=distributed_validators)


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


def update_attestation_slashing_db(attestation_data: AttestationData, validator_pubkey: BLSPubkey) -> None:
    """Check that the attestation data is not slashable for the validator and
    add attestation to slashing DB.
    """
    # Find the correct distributed validator
    distributed_validators = [dv for dv in state.distributed_validators
                              if dv.validator_identity.pubkey == validator_pubkey]
    assert len(distributed_validators) == 1
    distributed_validator = distributed_validators[0]
    # Find the correct slashing DB
    slashing_db = distributed_validator.slashing_db
    assert not is_slashable_attestation_data(slashing_db, attestation_data, validator_pubkey)
    slashing_db.data.signed_attestations.append(SlashingDBAttestation(source_epoch=attestation_data.source.epoch,
                                                                      target_epoch=attestation_data.target.epoch,
                                                                      signing_root=attestation_data.hash_tree_root()))
    # TODO: Check correct usage of signing_root ^^


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
    # Find the correct distributed validator
    distributed_validators = [dv for dv in state.distributed_validators
                              if dv.validator_identity.pubkey == validator_pubkey]
    assert len(distributed_validators) == 1
    distributed_validator = distributed_validators[0]
    # Find the correct slashing DB
    slashing_db = distributed_validator.slashing_db
    assert not is_slashable_block(slashing_db, block, validator_pubkey)
    slashing_db.data.signed_blocks.append(SlashingDBBlock(slot=block.slot,
                                                          signing_root=block.hash_tree_root()))
    # TODO: Check correct usage of signing_root ^^


def vc_sign_block(block: BeaconBlock, proposer_duty: ProposerDuty) -> SignedBeaconBlock:
    return SignedBeaconBlock(message=block)
