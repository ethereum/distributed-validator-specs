from dataclasses import dataclass
from typing import (
    List,
)

from eth2spec.altair.mainnet import (
    AttestationData,
    Attestation,
    BeaconBlock,
    SignedBeaconBlock,
    compute_start_slot_at_epoch,
    compute_epoch_at_slot,
)

from dvspec.utils.helpers.signing import (
    compute_attestation_signing_root,
    compute_block_signing_root,
    compute_randao_reveal_signing_root,
)

from .utils.helpers.slashing_db import (
    get_slashing_db_data_for_pubkey,
    is_slashable_attestation_data,
    is_slashable_block,
)
from .eth_node_interface import (
    AttestationDuty,
    ProposerDuty,
    bn_get_fork_version,
    bn_submit_attestation,
    bn_submit_block,
    bn_submit_sync_committee_signature,
    rs_sign_attestation,
    rs_sign_randao_reveal,
    rs_sign_block,
)
from .consensus import (
    consensus_is_valid_attestation_data,
    consensus_is_valid_block,
    consensus_is_valid_sync_committee_contribution,
    consensus_on_attestation,
    consensus_on_block,
    consensus_on_sync_committee_contribution,
)
from .networking import (
    broadcast_threshold_signed_attestation,
    broadcast_threshold_signed_block,
    broadcast_threshold_signed_randao_reveal,
    construct_signed_attestation,
    construct_signed_randao_reveal,
    construct_signed_block,
    construct_signed_sync_committee_signature,
    listen_for_threshold_signed_attestations,
    listen_for_threshold_signed_blocks,
    listen_for_threshold_signed_randao_reveal,
    listen_for_threshold_signed_sync_committee_signatures,
)
from .utils.types import (
    BLSPubkey,
    SlashingDB,
    SlashingDBAttestation,
    SlashingDBBlock,
    ValidatorIndex,
    BLSSignature
)


@dataclass
class ValidatorIdentity:
    """Identity of the Ethereum validator.
    """
    # Ethereum public key
    pubkey: BLSPubkey
    # Index of Ethereum validator
    index: ValidatorIndex


@dataclass
class CoValidator:
    """Identity of distributed co-validator participating in the DV protocol.
    """
    # Identity of Ethereum validator that this co-validator performs duties for
    validator_identity: ValidatorIdentity
    # Secret-shared public key
    pubkey: BLSPubkey
    # Index of the co-validator in the distributed validator protocol
    index: ValidatorIndex


@dataclass
class DistributedValidator:
    """State object that tracks a single Ethereum validator being run using the distributed validator protocol.
    """
    validator_identity: ValidatorIdentity
    co_validators: List[CoValidator]
    slashing_db: SlashingDB


@dataclass
class State:
    distributed_validators: List[DistributedValidator]


def update_attestation_slashing_db(slashing_db: SlashingDB,
                                   attestation_data: AttestationData, pubkey: BLSPubkey) -> None:
    """Update slashing DB for the validator with pubkey with new attestation data.
    """
    assert not is_slashable_attestation_data(slashing_db, attestation_data, pubkey)
    slashing_db_data = get_slashing_db_data_for_pubkey(slashing_db, pubkey)
    slashing_db_attestation = SlashingDBAttestation(source_epoch=attestation_data.source.epoch,
                                                    target_epoch=attestation_data.target.epoch,
                                                    signing_root=attestation_data.hash_tree_root())
    slashing_db_data.signed_attestations.append(slashing_db_attestation)


def update_block_slashing_db(slashing_db: SlashingDB, block: BeaconBlock, pubkey: BLSPubkey) -> None:
    """Update slashing DB for the validator with pubkey with new block.
    """
    assert not is_slashable_block(slashing_db, block, pubkey)
    slashing_db_data = get_slashing_db_data_for_pubkey(slashing_db, pubkey)
    slashing_db_block = SlashingDBBlock(slot=block.slot,
                                        signing_root=block.hash_tree_root())
    slashing_db_data.signed_blocks.append(slashing_db_block)


def serve_attestation_duty(slashing_db: SlashingDB, attestation_duty: AttestationDuty) -> None:
    """
    Attestation Production Process:
    1. At the start of every epoch, get attestation duties for epoch+1 by running
        bn_get_attestation_duties_for_epoch(validator_indices, epoch+1)
    2. For each attestation_duty received in Step 1, schedule
        serve_attestation_duty(slashing_db, attestation_duty) at 1/3rd way through the slot
        attestation_duty.slot
    See notes here:
    https://github.com/ethereum/beacon-APIs/blob/05c1bc142e1a3fb2a63c79098743776241341d08/validator-flow.md#attestation
    """
    # TODO: Is lock on consensus the best way to do this? Does lock on slashing DB work?
    # Obtain lock on consensus_on_attestation here.
    # Only a single consensus_on_attestation instance should be
    # running at any given time
    attestation_data = consensus_on_attestation(slashing_db, attestation_duty)
    assert consensus_is_valid_attestation_data(slashing_db, attestation_data, attestation_duty)
    # Release lock on consensus_on_attestation here.
    # Add attestation to slashing DB
    update_attestation_slashing_db(slashing_db, attestation_data, attestation_duty.pubkey)
    # Sign attestation using RS
    # TODO: Reuse fork version from here in compute_domain
    fork_version = bn_get_fork_version(compute_start_slot_at_epoch(attestation_data.target.epoch))
    attestation_signing_root = compute_attestation_signing_root(attestation_data)
    attestation_threshold_signature = rs_sign_attestation(attestation_data, attestation_signing_root, fork_version)
    # TODO: What is threshold_signed_attestation.aggregation_bits?
    threshold_signed_attestation = Attestation(data=attestation_data, signature=attestation_threshold_signature)
    # TODO: Should we just gossip & recombine the threshold signatures without attestation data?
    broadcast_threshold_signed_attestation(threshold_signed_attestation)


def serve_proposer_duty(slashing_db: SlashingDB, proposer_duty: ProposerDuty) -> None:
    """"
    Block Production Process:
    1. At the start of every epoch, get proposer duties for epoch+1 by running
        bn_get_proposer_duties_for_epoch(epoch+1)
    2. For each proposer_duty received in Step 1 for our validators, schedule
        serve_proposer_duty(proposer_duty) at beginning of slot proposer_duty.slot
    See notes here:
    https://github.com/ethereum/beacon-APIs/blob/05c1bc142e1a3fb2a63c79098743776241341d08/validator-flow.md#block-proposing
    """
    # TODO: Is lock on consensus the best way to do this? Does lock on slashing DB work?
    # Obtain lock on consensus_on_block here.
    # Only a single consensus_on_block instance should be
    # running at any given time
    fork_version = bn_get_fork_version(proposer_duty.slot)
    # Sign randao_reveal using RS
    randao_reveal_signing_root = compute_randao_reveal_signing_root(proposer_duty.slot)
    threshold_signed_randao_reveal = rs_sign_randao_reveal(compute_epoch_at_slot(proposer_duty.slot),
                                                           fork_version, randao_reveal_signing_root)
    broadcast_threshold_signed_randao_reveal(threshold_signed_randao_reveal)
    randao_reveal = threshold_randao_reveal_combination()
    block = consensus_on_block(slashing_db, proposer_duty, randao_reveal)
    assert consensus_is_valid_block(slashing_db, block, proposer_duty, randao_reveal)
    # Release lock on consensus_on_block here.
    # Add block to slashing DB
    update_block_slashing_db(slashing_db, block, proposer_duty.pubkey)
    # Sign block using RS
    block_signing_root = compute_block_signing_root(block)
    block_threshold_signature = rs_sign_block(block, fork_version, block_signing_root)
    threshold_signed_block = SignedBeaconBlock(message=block, signature=block_threshold_signature)
    broadcast_threshold_signed_block(threshold_signed_block)


# def serve_sync_committee_duty(slashing_db: SlashingDB, sync_committee_duty: SyncCommitteeDuty) -> None:
#     """"
#     Sync Committee Signature Production Process:
#     TODO: What is the sequence here - do you query for next epoch's duties?
#     """
#     # TODO: Is lock on consensus the best way to do this?
#     # Obtain lock on consensus_on_sync_committee_contribution here.
#     # Only a single consensus_on_sync_committee_contribution instance should be
#     # running at any given time
#     sync_committee_contribution = consensus_on_sync_committee_contribution(sync_committee_duty)
#     # Release lock on consensus_on_block here.
#     # TODO: Update slashing DB with sync committee contribution
#     # Cache decided sync committee contribution value to provide to VC
#     cache_sync_committee_contribution_for_vc(sync_committee_contribution, sync_committee_duty)


def threshold_randao_reveal_combination() -> BLSSignature:
    """
    Threshold randao_reveal Combination Process:
    1. Always keep listening for threshold signed randao reveal values from other DVCs.
    2a. Whenever a set of threshold signed values are found in Step 1 that can be
        combined to construct a complete randao reveal, construct the complete value.
    3. Return the randao reveal.
    """
    # 1. Always listen for threshold signed randao reveal values from DV peers.
    threshold_signed_randao_reveals = listen_for_threshold_signed_randao_reveal()
    # 2. Reconstruct complete signed value by combining threshold signed values
    complete_signed_randao_reveal = construct_signed_randao_reveal(threshold_signed_randao_reveals)
    # 3. Return complete signed value
    return complete_signed_randao_reveal


def threshold_attestation_combination() -> None:
    """
    Threshold Attestation Combination Process:
    1. Always keep listening for threshold signed attestations from other DVCs.
    2a. Whenever a set of threshold signed attestations are found in Step 1 that can be
        combined to construct a complete signed attestation, construct the attestation.
    2b. Send the attestation to the beacon node for Ethereum p2p gossip.
    """
    # 1. Always listen for threshold signed blocks from DV peers.
    threshold_signed_attestations = listen_for_threshold_signed_attestations()
    # 2. Reconstruct complete signed block by combining threshold signed attestations
    complete_signed_attestation = construct_signed_attestation(threshold_signed_attestations)
    # 3. Send to beacon node for gossip
    bn_submit_attestation(complete_signed_attestation)


def threshold_signed_block_combination() -> None:
    """
    Threshold Block Combination Process:
    1. Always keep listening for threshold signed blocks using from other DVCs.
    2a. Whenever a set of threshold signed blocks are found in Step 1 that can be
        combined to construct a complete signed block, construct the block.
    2b. Send the block to the beacon node for Ethereum p2p gossip.
    """
    # 1. Always listen for threshold signed blocks from DV peers.
    threshold_signed_blocks = listen_for_threshold_signed_blocks()
    # 2. Reconstruct complete signed block by combining threshold signed blocks
    complete_signed_block = construct_signed_block(threshold_signed_blocks)
    # 3. Send to beacon node for gossip
    bn_submit_block(complete_signed_block)


# def threshold_signed_sync_committee_signature_combination() -> None:
#     """
#     Threshold Sync Committee Signature Combination Process:
#     1. Always keep listening for threshold signed sync committee signatures using
#         listen_for_threshold_signed_sync_committee_signatures.
#     2a. Whenever a set of threshold signed sync committee signatures are found in Step 1 that can be
#         combined to construct a complete signed sync committee signature, construct the sync committee
#         signature.
#     2b. Send the sync committee signature to the beacon node for Ethereum p2p gossip.
#     """
#     # 1. Always listen for threshold signed sync committee signatures from DV peers.
#     threshold_signed_sync_committee_signatures = listen_for_threshold_signed_sync_committee_signatures()
#     # 2. Reconstruct complete signed sync committee signature by combining threshold
#     #    signed sync committee signatures
#     complete_signed_sync_committee_signature = \
#         construct_signed_sync_committee_signature(threshold_signed_sync_committee_signatures)
#     # 3. Send to beacon node for gossip
#     bn_submit_sync_committee_signature(complete_signed_sync_committee_signature)
