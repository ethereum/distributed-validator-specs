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


# Beacon Node
def bn_get_next_attestation_duty() -> AttestationDuty:
    # TODO: Add val index
    pass

def bn_broadcast_attestation(attestation: Attestation) -> None:
    pass
        
# Validator Client
def vc_is_slashable(attestation_data: AttestationData) -> bool:
    # TODO: Add val index
    pass

# TODO: What object does the VC sign? 
# Is it the same object that the BN accepts for broadcast?
def vc_sign_attestation(attestation_data: AttestationData) -> AttestationData:
    pass

