from eth2_node import (
    AttestationData,
    AttestationDuty,
    Attestation,
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
    slot = 0
    while True:
        yield slot
        slot += 1

attestation_duty_source = attestation_duty_generator()

def bn_get_next_attestation_duty() -> AttestationDuty:
    slot = next(attestation_duty_source)
    return AttestationDuty(slot=slot)

def bn_broadcast_attestation(attestation: Attestation) -> None:
    pass

# Validator Client methods
vc_slashing_db = set()

def vc_is_slashable(attestation_data: AttestationData) -> bool:
    for past_attestation_data in vc_slashing_db:
        if is_slashable_attestation_data(past_attestation_data, attestation_data):
            return True
    return False

def vc_sign_attestation(attestation_data: AttestationData) -> AttestationData:
    assert not vc_is_slashable(attestation_data)
    vc_slashing_db.add(attestation_data)
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
