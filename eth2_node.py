from eth2spec.phase0.mainnet import (
    Container,
    Slot,
    AttestationData,
    Attestation,
)

class AttestationDuty(Container):
    # TODO: Update schema to include committee_index etc. as defined
    # in https://ethereum.github.io/beacon-APIs/#/
    slot: Slot

class BeaconNodeTemplate:
    def get_next_attestation_duty(self) -> AttestationDuty:
        pass

    def broadcast_attestation(self, attestation: Attestation) -> None:
        pass
        
class ValidatorClientTemplate:
    def is_slashable(self, attestation_data: AttestationData) -> bool:
        pass

    # TODO: What object does the VC sign? 
    # Is it the same object that the BN accepts for broadcast?
    def sign_attestation(self, attestation_data: AttestationData) -> AttestationData:
        pass
