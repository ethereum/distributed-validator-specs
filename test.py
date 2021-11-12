from eth2_node import (
    AttestationData,
    AttestationDuty,
    Attestation,
    ValidatorIndex,
)
from eth2spec.phase0.mainnet import (
    is_slashable_attestation_data,
)

def time_generator():
    time = 0
    while True:
        yield time
        time += 1


timer = time_generator()


def get_current_time():
    # Returns current time
    return next(timer)


# Beacon Node methods
def attestation_duty_generator():
    val_index = 1
    slot = 0
    while True:
        yield slot, val_index
        slot += 1

attestation_duty_source = attestation_duty_generator()

def bn_get_next_attestation_duty() -> AttestationDuty:
    slot, val_index = next(attestation_duty_source)
    return AttestationDuty(slot=slot, validator_index=val_index)

def bn_broadcast_attestation(attestation: Attestation) -> None:
    pass

# Validator Client methods
vc_slashing_db = {}

def vc_is_slashable(attestation_data: AttestationData, validator_index: ValidatorIndex) -> bool:
    if validator_index not in vc_slashing_db:
        vc_slashing_db[validator_index] = set()
    for past_attestation_data in vc_slashing_db[validator_index]:
        if is_slashable_attestation_data(past_attestation_data, attestation_data):
            return True
    return False

def vc_sign_attestation(attestation_data: AttestationData, validator_index: ValidatorIndex) -> AttestationData:
    assert not vc_is_slashable(attestation_data, validator_index)
    vc_slashing_db[validator_index].add(attestation_data)
    return attestation_data


# Other methods

def calculate_attestation_time(slot):
    return 12 * slot + 4

def is_valid_attestation_data(slot, attestation_data):
    # Determines if `attestation_data` is valid for `slot`
    return attestation_data.slot == slot

def consensus(slot):
    # Returns decided value for consensus instance at `slot`
    attestation_data = AttestationData()
    attestation_data.slot = slot
    attestation_data.target.epoch = slot
    is_valid_attestation_data(slot, attestation_data)
    return attestation_data
