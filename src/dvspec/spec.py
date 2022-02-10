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
    rs_sign_attestation,
    rs_sign_randao_reveal,
    rs_sign_block,
)
from .consensus import (
    consensus_is_valid_attestation_data,
    consensus_is_valid_block,
    consensus_on_attestation,
    consensus_on_block,
)
from .networking import (
    broadcast_attestation_signature_share,
    broadcast_block_signature_share,
    broadcast_randao_reveal_signature_share,
    construct_signed_attestation,
    construct_signed_randao_reveal,
    construct_signed_block,
    listen_for_attestation_signature_shares,
    listen_for_block_signature_shares,
    listen_for_randao_reveal_signature_shares,
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
    attestation_signature_share = rs_sign_attestation(attestation_data, attestation_signing_root, fork_version)
    # TODO: What is attestation_signature_share.aggregation_bits?
    attestation_signature_share = Attestation(data=attestation_data, signature=attestation_signature_share)
    # TODO: Should we just gossip & recombine the signature shares without attestation data?
    broadcast_attestation_signature_share(attestation_signature_share)


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
    randao_reveal_signature_share = rs_sign_randao_reveal(compute_epoch_at_slot(proposer_duty.slot),
                                                          fork_version, randao_reveal_signing_root)
    broadcast_randao_reveal_signature_share(randao_reveal_signature_share)
    randao_reveal = randao_reveal_combination()
    block = consensus_on_block(slashing_db, proposer_duty, randao_reveal)
    assert consensus_is_valid_block(slashing_db, block, proposer_duty, randao_reveal)
    # Release lock on consensus_on_block here.
    # Add block to slashing DB
    update_block_slashing_db(slashing_db, block, proposer_duty.pubkey)
    # Sign block using RS
    block_signing_root = compute_block_signing_root(block)
    block_signature_share = rs_sign_block(block, fork_version, block_signing_root)
    block_signature_share = SignedBeaconBlock(message=block, signature=block_signature_share)
    broadcast_block_signature_share(block_signature_share)


def randao_reveal_combination() -> BLSSignature:
    """
    randao_reveal Combination Process:
    1. Always keep listening for randao reveal signature shares from other DVCs.
    2a. Whenever a set of signature shares are found in Step 1 that can be
        combined to construct a complete randao reveal, construct the complete value.
    3. Return the randao reveal.
    """
    # 1. Always listen for randao reveal signature shares from DV peers.
    randao_reveal_signature_shares = listen_for_randao_reveal_signature_shares()
    # 2. Reconstruct complete signed value by combining signature shares
    complete_signed_randao_reveal = construct_signed_randao_reveal(randao_reveal_signature_shares)
    # 3. Return complete signed value
    return complete_signed_randao_reveal


def attestation_combination() -> None:
    """
    Attestation Combination Process:
    1. Always keep listening for attestation signature shares from other DVCs.
    2a. Whenever a set of attestation signature shares are found in Step 1 that can be
        combined to construct a complete signed attestation, construct the attestation.
    2b. Send the attestation to the beacon node for Ethereum p2p gossip.
    """
    # 1. Always listen for block signature shares from DV peers.
    attestation_signature_shares = listen_for_attestation_signature_shares()
    # 2. Reconstruct complete signed block by combining attestation signature shares
    complete_signed_attestation = construct_signed_attestation(attestation_signature_shares)
    # 3. Send to beacon node for gossip
    bn_submit_attestation(complete_signed_attestation)


def block_combination() -> None:
    """
    Block Combination Process:
    1. Always keep listening for block signature shares using from other DVCs.
    2a. Whenever a set of block signature shares are found in Step 1 that can be
        combined to construct a complete signed block, construct the block.
    2b. Send the block to the beacon node for Ethereum p2p gossip.
    """
    # 1. Always listen for block signature shares from DV peers.
    block_signature_shares = listen_for_block_signature_shares()
    # 2. Reconstruct complete signed block by combining block signature shares
    complete_signed_block = construct_signed_block(block_signature_shares)
    # 3. Send to beacon node for gossip
    bn_submit_block(complete_signed_block)
