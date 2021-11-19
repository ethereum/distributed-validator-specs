import random
from eth2spec.phase0.mainnet import (
    SLOTS_PER_EPOCH, TARGET_COMMITTEE_SIZE,
    Checkpoint,
    is_slashable_attestation_data,
    compute_start_slot_at_epoch,
    compute_epoch_at_slot,
    config,
)
from eth2_node import (
    List,
    Slot, Epoch, BLSPubkey, ValidatorIndex, CommitteeIndex,
    Attestation, AttestationData,
    AttestationDuty,
)


VALIDATOR_INDICES = [1, 2, 3]
GENESIS_TIME = 0

def time_generator():
    time = GENESIS_TIME
    while True:
        yield time
        time += 1

timer = time_generator()

def get_current_time():
    # Returns current time
    return next(timer)


# Beacon Node Methods

def bn_get_attestation_duties_for_epoch(validator_indices: List[ValidatorIndex], epoch: Epoch) -> List[AttestationDuty]:
    attestation_duties = []
    for validator_index in validator_indices:
        start_slot_at_epoch = compute_start_slot_at_epoch(epoch)
        attestation_slot = start_slot_at_epoch + random.randrange(SLOTS_PER_EPOCH)
        attestation_duty = AttestationDuty(validator_index=validator_index,
                                            committee_length=TARGET_COMMITTEE_SIZE,
                                            validator_committee_index=random.randrange(TARGET_COMMITTEE_SIZE),
                                            slot=attestation_slot)
        attestation_duties.append(attestation_duty)
    return attestation_duties

def bn_get_attestation_data(slot: Slot, committee_index: CommitteeIndex) -> AttestationData:
    attestation_data = AttestationData( slot=slot,
                                        index=committee_index,
                                        source=Checkpoint(epoch=min(compute_epoch_at_slot(slot) - 1, 0)),
                                        target=Checkpoint(epoch=compute_epoch_at_slot(slot)))
    return attestation_data

def bn_submit_attestation(attestation: Attestation) -> None:
    pass


# Validator Client Methods

slashing_db = {}

def update_slashing_db(attestation_data, validator_pubkey):
    """Check that the attestation data is not slashable for the validator and
    add attestation to slashing DB.
    """
    if validator_pubkey not in slashing_db:
        slashing_db[validator_pubkey] = set()
    assert not vc_is_slashable(attestation_data, validator_pubkey)
    slashing_db[validator_pubkey].add(attestation_data)

def vc_is_slashable(attestation_data: AttestationData, validator_pubkey: BLSPubkey) -> bool:
    if validator_pubkey in slashing_db:
        for past_attestation_data in slashing_db[validator_pubkey]:
            if is_slashable_attestation_data(past_attestation_data, attestation_data):
                return True
    return False

def vc_sign_attestation(attestation_data: AttestationData, attestation_duty) -> Attestation:
    update_slashing_db(attestation_data, attestation_duty.pubkey)
    attestation = Attestation(data=attestation_data)
    attestation.aggregation_bits[attestation_duty.validator_committee_index] = 1
    return attestation

# Misc. Methods


def calculate_attestation_time(slot):
    return config.SECONDS_PER_SLOT * slot + GENESIS_TIME

def is_valid_attestation_data(slot, attestation_data):
    # Determines if `attestation_data` is valid for `slot`
    return attestation_data.slot == slot

def consensus(attestation_duty):
    # Returns decided value for consensus instance at `slot`
    attestation_data = AttestationData()
    attestation_data.slot = attestation_duty.slot
    attestation_data.target.epoch = attestation_duty.slot
    is_valid_attestation_data(attestation_duty.slot, attestation_data)
    return attestation_data
