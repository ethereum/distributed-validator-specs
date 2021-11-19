from typing import List
from eth2spec.phase0.mainnet import (
    Container, uint64,
    BLSPubkey,
    Slot,
    Epoch,
    AttestationData,
    Attestation,
    ValidatorIndex, CommitteeIndex
)

class AttestationDuty(Container):
    pubkey: BLSPubkey
    validator_index: ValidatorIndex
    committee_index: CommitteeIndex
    committee_length: uint64
    committees_at_slot: uint64
    validator_committee_index: ValidatorIndex # TODO: Is this the correct datatype?
    slot: Slot


# Beacon Node Interface

def bn_get_attestation_duties_for_epoch(self, validator_indices: List[ValidatorIndex], epoch: Epoch) -> List[AttestationDuty]:
    # TODO: Define typing here:
    # What's the size of validator_indices & the returned attestation_duties?
    """Fetch attestation duties for the validator indices in the epoch.
    Uses https://ethereum.github.io/beacon-APIs/#/ValidatorRequiredApi/getAttesterDuties
    """
    pass

def bn_get_attestation_data(self, slot: Slot, committee_index: CommitteeIndex) -> AttestationData:
    """Produces attestation data for the given slot & committee index.
    Uses https://ethereum.github.io/beacon-APIs/#/ValidatorRequiredApi/produceAttestationData
    """
    pass

def bn_submit_attestation(self, attestation: Attestation) -> None:
    """Submit attestation to BN for p2p gossip.
    Uses https://ethereum.github.io/beacon-APIs/#/Beacon/submitPoolAttestations
    """
    pass


# Validator Client Interface

def vc_is_slashable(self, attestation_data: AttestationData, validator_pubkey: BLSPubkey) -> bool:
    """Checks whether the attestation data is slashable according to the anti-slashing database.
    This is a new endpoint for the VC.
    """
    pass

def vc_sign_attestation(self, attestation_data: AttestationData, attestation_duty: AttestationDuty) -> Attestation:
    """Returns a signed attestations that is constructed using the given attestation data & attestation duty.
    """
    # See note about attestation construction here: https://github.com/ethereum/beacon-APIs/blame/05c1bc142e1a3fb2a63c79098743776241341d08/validator-flow.md#L35-L37
    pass
