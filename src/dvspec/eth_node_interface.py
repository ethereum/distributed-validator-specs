from typing import List
from eth2spec.phase0.mainnet import (
    Attestation,
    AttestationData,
    BeaconBlock,
    SignedBeaconBlock,
)

from .networking import (
    broadcast_threshold_signed_attestation,
    broadcast_threshold_signed_block
)
from .utils.types import (
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


def bn_produce_attestation_data(slot: Slot, committee_index: CommitteeIndex) -> AttestationData:
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

"""
The VC is connected to the BN through the DVC. The DVC pretends to be a proxy for the BN, except
when:
- VC asks for its attestation, block proposal, or sync  duties using the following methods:
    - https://ethereum.github.io/beacon-APIs/#/ValidatorRequiredApi/getAttesterDuties
    - https://ethereum.github.io/beacon-APIs/#/ValidatorRequiredApi/getProposerDuties
    - mhttps://ethereum.github.io/beacon-APIs/#/ValidatorRequiredApi/getSyncCommitteeDuties
- VC asks for new attestation data, block, or sync duty using the following methods:
    - https://ethereum.github.io/beacon-APIs/#/ValidatorRequiredApi/produceAttestationData
    - https://ethereum.github.io/beacon-APIs/#/ValidatorRequiredApi/produceBlockV2
    - https://ethereum.github.io/beacon-APIs/#/ValidatorRequiredApi/produceSyncCommitteeContribution
- VC submits new threshold signed attestation, block proposal, or sync duty using the following methods:
    - https://ethereum.github.io/beacon-APIs/#/Beacon/submitPoolAttestations
    - https://ethereum.github.io/beacon-APIs/#/ValidatorRequiredApi/publishBlock
    - https://ethereum.github.io/beacon-APIs/#/ValidatorRequiredApi/produceSyncCommitteeContribution
"""


def cache_attestation_data_for_vc(attestation_data: AttestationData, attestation_duty: AttestationDuty) -> None:
    """Cache attestation data to provide to VC when it seeks new attestation data using the following method:
    https://ethereum.github.io/beacon-APIs/#/ValidatorRequiredApi/produceAttestationData
    """
    pass


def cache_block_for_vc(block: BeaconBlock, proposer_duty: ProposerDuty) -> None:
    """Cache block to provide to VC when it seeks a new block using the following method:
    https://ethereum.github.io/beacon-APIs/#/ValidatorRequiredApi/produceAttestationData
    """
    pass


def capture_threshold_signed_attestation(threshold_signed_attestation: Attestation) -> None:
    """Captures a threshold signed attestation provided by the VC and starts the recombination process to
    construct a complete signed attestation to submit to the BN. The VC submits the attestation using the
    following method: https://ethereum.github.io/beacon-APIs/#/Beacon/submitPoolAttestations
    """
    broadcast_threshold_signed_attestation(threshold_signed_attestation)


def capture_threhold_signed_block(threshold_signed_block: SignedBeaconBlock) -> None:
    """Captures a threshold signed block provided by the VC and starts the recombination process to
    construct a complete signed block to submit to the BN. The VC submits the block using the following method:
    https://ethereum.github.io/beacon-APIs/#/ValidatorRequiredApi/publishBlock
    """
    broadcast_threshold_signed_block(threshold_signed_block)
