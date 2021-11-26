from dataclasses import dataclass
from typing import (
    List,
)

from eth2spec.phase0.mainnet import Attestation

from .eth_node_interface import (
    AttestationDuty,
    ProposerDuty,
    bn_submit_attestation,
    bn_submit_block,
    cache_attestation_data_for_vc,
    cache_block_for_vc,
)
from .consensus import (
    consensus_on_attestation,
    consensus_on_block,
)
from .networking import (
    construct_signed_attestation,
    construct_signed_block,
    listen_for_threshold_signed_attestations,
    listen_for_threshold_signed_blocks
)
from .utils.types import (
    BLSPubkey,
    SlashingDB,
    UInt64
)


@dataclass
class ValidatorIdentity:
    """Identity of the Ethereum validator.
    """
    # Ethereum public key
    pubkey: BLSPubkey
    # Index of Ethereum validator
    index: UInt64


@dataclass
class CoValidator:
    """Identity of distributed co-validator participating in the DV protocol.
    """
    # Identity of Ethereum validator that this co-validator performs duties for
    validator_identity: ValidatorIdentity
    # Secret-shared public key
    pubkey: BLSPubkey
    # Index of the co-validator in the distributed validator protocol
    index: UInt64


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


def serve_attestation_duty(attestation_duty: AttestationDuty) -> None:
    """
    Attestation Production Process:
    1. At the start of every epoch, get attestation duties for epoch+1 by running
        bn_get_attestation_duties_for_epoch(validator_indices, epoch+1)
    2. For each attestation_duty received in Step 1, schedule
        serve_attestation_duty(attestation_duty) at 1/3rd way through the slot
        attestation_duty.slot
    See notes here:
    https://github.com/ethereum/beacon-APIs/blob/05c1bc142e1a3fb2a63c79098743776241341d08/validator-flow.md#attestation
    """
    # Obtain lock on consensus_on_attestation here.
    # Only a single consensus_on_attestation instance should be
    # running at any given time
    attestation_data = consensus_on_attestation(attestation_duty)
    # Release lock on consensus_on_attestation here.
    # Cache decided attestation data value to provide to VC
    cache_block_for_vc(attestation_data, attestation_duty)


def serve_proposer_duty(proposer_duty: ProposerDuty) -> None:
    """"
    Block Production Process:
    1. At the start of every epoch, get proposer duties for epoch+1 by running
        bn_get_proposer_duties_for_epoch(epoch+1)
    2. For each proposer_duty received in Step 1 for our validators, schedule
        serve_proposer_duty(proposer_duty) at beginning of slot proposer_duty.slot
    See notes here:
    https://github.com/ethereum/beacon-APIs/blob/05c1bc142e1a3fb2a63c79098743776241341d08/validator-flow.md#block-proposing
    """
    # Obtain lock on consensus_on_block here.
    # Only a single consensus_on_block instance should be
    # running at any given time
    block = consensus_on_block(proposer_duty)
    # Release lock on consensus_on_block here.
    # Cache decided block value to provide to VC
    cache_attestation_data_for_vc(block, proposer_duty)


def threshold_attestation_combination() -> None:
    """
    Threshold Attestation Combination Process:
    1. Always keep listening for threshold signed attestations using
        broadcast_threshold_signed_attestation.
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
    1. Always keep listening for threshold signed blocks using
        listen_for_threshold_signed_block.
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
