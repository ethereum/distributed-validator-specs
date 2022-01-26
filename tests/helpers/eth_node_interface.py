import random
from eth2spec.altair.mainnet import (
    MAX_COMMITTEES_PER_SLOT,
    SLOTS_PER_EPOCH,
    TARGET_COMMITTEE_SIZE,
    Attestation,
    AttestationData,
    BeaconBlock,
    Checkpoint,
    Version,
    compute_epoch_at_slot,
    compute_start_slot_at_epoch,
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
    Slot,
    ValidatorIndex,
)
from dvspec.spec import (
    State,
)

VALIDATOR_SET_SIZE = SLOTS_PER_EPOCH

"""
Ethereum node interface methods
"""


def bn_get_fork_version(slot: Slot) -> Version:
    return Version('0x00000000')


def bn_get_attestation_duties_for_epoch(validator_indices: List[ValidatorIndex], epoch: Epoch) -> List[AttestationDuty]:
    attestation_duties = []
    for validator_index in validator_indices:
        start_slot_at_epoch = compute_start_slot_at_epoch(epoch)
        attestation_slot = start_slot_at_epoch + random.randrange(SLOTS_PER_EPOCH)
        attestation_duty = AttestationDuty(pubkey=BLSPubkey(str(validator_index).zfill(48*2)),
                                           validator_index=validator_index,
                                           committee_index=random.randrange(MAX_COMMITTEES_PER_SLOT),
                                           committee_length=TARGET_COMMITTEE_SIZE,
                                           committees_at_slot=MAX_COMMITTEES_PER_SLOT,
                                           validator_committee_index=random.randrange(TARGET_COMMITTEE_SIZE),
                                           slot=attestation_slot)
        attestation_duties.append(attestation_duty)
    return attestation_duties


def bn_produce_attestation_data(slot: Slot, committee_index: CommitteeIndex) -> AttestationData:
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
        proposer_duties.append(ProposerDuty(pubkey=BLSPubkey(str('').zfill(48*2)),
                               validator_index=validator_indices[i], slot=i))
    return proposer_duties


def bn_produce_block(slot: Slot, randao_reveal: BLSSignature, graffiti: Bytes32) -> BeaconBlock:
    block = BeaconBlock()
    block.slot = slot
    block.body.randao_reveal = randao_reveal
    block.body.graffiti = graffiti
    return block


def rs_sign_attestation(attestation_data: AttestationData, fork_version: Version, signing_root: Root) -> BLSSignature:
    return BLSSignature(str(signing_root.hex()).zfill(96*2))


def rs_sign_randao_reveal(epoch: Epoch, fork_version: Version, signing_root: Root) -> BLSSignature:
    return BLSSignature(str(signing_root.hex()).zfill(96*2))


def rs_sign_block(block: BeaconBlock, fork_version: Version, signing_root: Root) -> BLSSignature:
    return BLSSignature(str(signing_root.hex()).zfill(96*2))


"""
Helpers for Ethereum node interaface methods
"""


def fill_attestation_duties_with_val_index(state: State,
                                           attestation_duties: List[AttestationDuty]) -> List[AttestationDuty]:
    val_index_to_pubkey = {}
    for dv in state.distributed_validators:
        val_index_to_pubkey[dv.validator_identity.index] = dv.validator_identity.pubkey
    for att_duty in attestation_duties:
        att_duty.pubkey = val_index_to_pubkey[att_duty.validator_index]
    return attestation_duties


def filter_and_fill_proposer_duties_with_val_index(state: State,
                                                   proposer_duties: List[ProposerDuty]) -> List[ProposerDuty]:
    filtered_proposer_duties = []
    val_index_to_pubkey = {}
    for dv in state.distributed_validators:
        val_index_to_pubkey[dv.validator_identity.index] = dv.validator_identity.pubkey
    for pro_duty in proposer_duties:
        if pro_duty.validator_index in val_index_to_pubkey:
            pro_duty.pubkey = val_index_to_pubkey[pro_duty.validator_index]
            filtered_proposer_duties.append(pro_duty)
    return filtered_proposer_duties
