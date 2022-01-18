from typing import List
from eth2spec.altair.mainnet import (
    Attestation,
    AttestationData,
    BeaconBlock,
    SignedBeaconBlock,
    Version,
)

from .networking import (
    broadcast_threshold_signed_attestation,
    broadcast_threshold_signed_block,
    broadcast_threshold_signed_sync_committee_signature,
)
from .utils.types import (
    AttestationDuty,
    BLSSignature,
    Bytes32,
    CommitteeIndex,
    Epoch,
    ProposerDuty,
    Root,
    Slot,
    SyncCommitteeContribution,
    SyncCommitteeDuty,
    SyncCommitteeSignature,
    ValidatorIndex,
)


# Beacon Node Interface


def bn_get_genesis_validators_root() -> Root:
    """Fetch genesis validators root for the current chain.
    Uses https://ethereum.github.io/beacon-APIs/#/Beacon/getGenesis
    """
    pass


def bn_get_fork_version(slot: Slot) -> Version:
    """Fetch fork version for the given slot in the current chain.
    Uses https://ethereum.github.io/beacon-APIs/#/Beacon/getStateFork
    """
    pass


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


def bn_get_sync_committee_duties_for_epoch(validator_indices: List[ValidatorIndex],
                                           epoch: Epoch) -> List[SyncCommitteeDuty]:
    """Fetch sync committee duties for all validator indices in the epoch.
    Uses https://ethereum.github.io/beacon-APIs/#/ValidatorRequiredApi/submitPoolSyncCommitteeSignatures
    """
    pass


def bn_produce_sync_committee_contribution(slot: Slot,
                                           subcommittee_index: ValidatorIndex,
                                           beacon_block_root: Root) -> SyncCommitteeContribution:
    """Produces the sync committee contribution for the given params from the BN.
    Uses https://ethereum.github.io/beacon-APIs/#/ValidatorRequiredApi/produceSyncCommitteeContribution
    """
    pass


def bn_submit_sync_committee_signature(sync_committee_signature: SyncCommitteeSignature) -> None:
    """Submit sync committee signatures to the BN for Ethereum p2p gossip.
    Uses https://ethereum.github.io/beacon-APIs/#/ValidatorRequiredApi/submitPoolSyncCommitteeSignatures
    """
    pass


# Remote Signer Interface

"""
Remote Signer API: https://consensys.github.io/web3signer/web3signer-eth2.html
"""

def rs_sign_attestation(attestation_data: AttestationData, fork_version: Version, signing_root: Root) -> BLSSignature:
    """Instruct RS to sign attestation data using method:
    /api/v1/eth2/sign/attestation
    """
    pass


def rs_sign_randao_reveal(epoch: Epoch, fork_version: Version, signing_root: Root) -> BLSSignature:
    """Instruct RS to sign block using method:
    /api/v1/eth2/sign/randao_reveal
    """
    pass


def rs_sign_block(block: BeaconBlock, fork_version: Version, signing_root: Root) -> BLSSignature:
    """Instruct RS to sign block using method:
    /api/v1/eth2/sign/block_v2
    """
    pass


# TODO: Handle sync committee contributions correctly
# def cache_sync_committee_contribution_for_vc(sync_committee_contribution: SyncCommitteeContribution,
#                                              sync_committee_duty: SyncCommitteeDuty) -> None:
#     """Cache sync committee contribution to provide to VC when it seeks new data using the following method:
#     https://ethereum.github.io/beacon-APIs/#/ValidatorRequiredApi/produceSyncCommitteeContribution
#     """
#     pass
