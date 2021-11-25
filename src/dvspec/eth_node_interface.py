from typing import List
from eth2spec.phase0.mainnet import (
    Attestation,
    AttestationData,
    BeaconBlock,
    SignedBeaconBlock,
)

from dvspec.utils.types import (
    AttestationDuty,
    BLSSignature,
    Bytes32,
    CommitteeIndex,
    Epoch,
    ProposerDuty,
    Slot,
    ValidatorIndex,
)


# Beacon Node Interface

def bn_get_attestation_duties_for_epoch(validator_indices: List[ValidatorIndex], epoch: Epoch) -> List[AttestationDuty]:
    # TODO: Define typing here:
    # What's the size of validator_indices & the returned attestation_duties?
    """Fetch attestation duties for the validator indices in the epoch.
    Uses https://ethereum.github.io/beacon-APIs/#/ValidatorRequiredApi/getAttesterDuties
    """
    pass


def bn_get_attestation_data(slot: Slot, committee_index: CommitteeIndex) -> AttestationData:
    """Produces attestation data for the given slot & committee index.
    Uses https://ethereum.github.io/beacon-APIs/#/ValidatorRequiredApi/produceAttestationData
    """
    pass


def bn_submit_attestation(attestation: Attestation) -> None:
    """Submit attestation to BN for Ethereum p2p gossip.
    Uses https://ethereum.github.io/beacon-APIs/#/Beacon/submitPoolAttestations
    """
    pass


def bn_get_proposer_duties_for_epoch(epoch: Epoch) -> List[ProposerDuty]:
    """Fetch proposer duties for all proposers in the epoch.
    Uses https://ethereum.github.io/beacon-APIs/#/ValidatorRequiredApi/getProposerDuties
    """
    pass


def bn_produce_block(slot: Slot, randao_reveal: BLSSignature, graffiti: Bytes32) -> BeaconBlock:
    """Produces valid block for given slot using provided data
    Uses https://ethereum.github.io/beacon-APIs/#/ValidatorRequiredApi/produceBlockV2
    """
    pass


def bn_submit_block(block: SignedBeaconBlock) -> None:
    """Submit block to BN for Ethereum p2p gossip.
    Uses https://ethereum.github.io/beacon-APIs/#/ValidatorRequiredApi/publishBlock
    """
    pass


# Validator Client Interface


def vc_sign_attestation(attestation_data: AttestationData, attestation_duty: AttestationDuty) -> Attestation:
    """Returns a signed attestations that is constructed using the given attestation data & attestation duty.
    This endpoint does not exist in beacon-APIs.
    """
    # See note about attestation construction here:
    # https://github.com/ethereum/beacon-APIs/blame/05c1bc142e1a3fb2a63c79098743776241341d08/validator-flow.md#L35-L37
    pass


def vc_sign_block(block: BeaconBlock, proposer_duty: ProposerDuty) -> SignedBeaconBlock:
    """Returns a signed beacon block using the validator index given in the proposer duty.
    This endpoint does not exist in beacon-APIs.
    """
    pass
