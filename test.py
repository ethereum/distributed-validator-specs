from eth2_node import (
    AttestationData,
    AttestationDuty,
    BeaconNodeTemplate,
    ValidatorClientTemplate,
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


class BeaconNode(BeaconNodeTemplate):
    def __init__(self):
        self.attestation_duty_source = self.attestation_duty_generator()

    def attestation_duty_generator(self):
        slot = 0
        while True:
            yield slot
            slot += 1

    def get_next_attestation_duty(self) -> AttestationDuty:
        slot = next(self.attestation_duty_source)
        return AttestationDuty(slot=slot)


class ValidatorClient(ValidatorClientTemplate):
    def __init__(self):
        self.slashing_db = set()

    def is_slashable(self, attestation_data: AttestationData) -> bool:
        for past_attestation_data in self.slashing_db:
            if is_slashable_attestation_data(past_attestation_data, attestation_data):
                return True
        return False

    def sign_attestation(self, attestation_data: AttestationData) -> AttestationData:
        assert not self.is_slashable(attestation_data)
        self.slashing_db.add(attestation_data)
        return attestation_data


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
