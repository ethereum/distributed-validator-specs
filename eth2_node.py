from eth2spec.phase0.mainnet import (
    Container,
    Slot,
    AttestationData,
    Attestation,
    ValidatorIndex,
)

class AttestationDuty(Container):
    # TODO: Update schema to include committee_index etc. as defined
    # in https://ethereum.github.io/beacon-APIs/#/
    slot: Slot
    validator_index: ValidatorIndex


# Beacon Node
def bn_get_next_attestation_duty() -> AttestationDuty:
    pass

def bn_broadcast_attestation(attestation: Attestation) -> None:
    pass
        
# Validator Client
def vc_is_slashable(attestation_data: AttestationData, validator_index: ValidatorIndex) -> bool:
    # TODO: Should we use validator index or pubkey?
    pass

# TODO: What object does the VC sign? 
# Is it the same object that the BN accepts for broadcast?
def vc_sign_attestation(attestation_data: AttestationData, validator_index: ValidatorIndex) -> AttestationData:
    pass

