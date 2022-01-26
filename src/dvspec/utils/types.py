from eth2spec.altair.mainnet import (
    uint64,
    Bytes32,
    Epoch,
    BLSPubkey,
    BLSSignature,
    CommitteeIndex,
    Root,
    Slot,
    ValidatorIndex,
    Version,
)

from dataclasses import dataclass
from typing import (
    List,
)


"""
Basic Datatypes
"""


UInt64 = uint64
# UInt64 = int
# Bytes32 = bytes
# Bytes48 = bytes
# Bytes96 = bytes


"""
Aliased Data Types
"""

# Epoch = UInt64
# BLSPubkey = Bytes48
# BLSSignature = Bytes96
# CommitteeIndex = UInt64
CommitteeLength = UInt64
# Root = Bytes32
# Slot = UInt64
# ValidatorIndex = UInt64
# Version = UInt64


"""
Types for EIP-3076 Slashing DB.
See here for details:
https://eips.ethereum.org/EIPS/eip-3076
"""


@dataclass
class SlashingDBBlock:
    slot: Slot
    signing_root: Root


@dataclass
class SlashingDBAttestation:
    source_epoch: Epoch
    target_epoch: Epoch
    signing_root: Root


@dataclass
class SlashingDBData:
    pubkey: BLSPubkey
    signed_blocks: List[SlashingDBBlock]
    signed_attestations: List[SlashingDBAttestation]


@dataclass
class SlashingDB:
    interchange_format_version: Version
    genesis_validators_root: Root
    data: List[SlashingDBData]


"""
Types for talking to VCs and BNs
"""


@dataclass
class AttestationDuty:
    pubkey: BLSPubkey
    validator_index: ValidatorIndex
    committee_index: CommitteeIndex
    committee_length: UInt64
    committees_at_slot: UInt64
    validator_committee_index: ValidatorIndex  # TODO: Is this the correct datatype?
    slot: Slot


@dataclass
class ProposerDuty:
    pubkey: BLSPubkey
    validator_index: ValidatorIndex
    slot: Slot


@dataclass
class SyncCommitteeDuty:
    pubkey: BLSPubkey
    validator_index: ValidatorIndex
    validator_sync_committee_indices: List[ValidatorIndex]


@dataclass
class SyncCommitteeContribution:
    slot: Slot
    beacon_block_root: Root
    subcommittee_index: ValidatorIndex
    aggregation_bits: bytes


@dataclass
class SyncCommitteeSignature:
    slot: Slot
    beacon_block_root: Root
    validator_index: ValidatorIndex
    signature: BLSSignature
