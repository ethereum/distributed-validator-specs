from eth2spec.altair.mainnet import (
    AttestationData,
    BeaconBlock,
    DomainType,
    Domain,
    compute_domain,
    DOMAIN_BEACON_ATTESTER,
    DOMAIN_BEACON_PROPOSER,
    DOMAIN_RANDAO,
    compute_signing_root,
    compute_start_slot_at_epoch,
    compute_epoch_at_slot,
)

from ...eth_node_interface import (
    bn_get_fork_version,
    bn_get_genesis_validators_root,
)

from ..types import (
    Root,
    Slot,
    Epoch,
)

"""
Signing Helper Functions
"""


def dvc_compute_domain(domain_type: DomainType, epoch: Epoch) -> Domain:
    """Computes the signature domain for that domain type & epoch.
    Communicates with the BN to get necessary state objects"""
    genesis_validators_root = bn_get_genesis_validators_root()
    fork_version = bn_get_fork_version(compute_start_slot_at_epoch(epoch))
    return compute_domain(domain_type, fork_version, genesis_validators_root)


def compute_attestation_signing_root(attestation_data: AttestationData) -> Root:
    domain = compute_domain(DOMAIN_BEACON_ATTESTER, attestation_data.target.epoch)
    return compute_signing_root(attestation_data, domain)


def compute_randao_reveal_signing_root(slot: Slot) -> Root:
    domain = compute_domain(DOMAIN_RANDAO, compute_epoch_at_slot(slot))
    return compute_signing_root(compute_epoch_at_slot(slot), domain)


def compute_block_signing_root(block: BeaconBlock) -> Root:
    domain = compute_domain(DOMAIN_RANDAO, DOMAIN_BEACON_PROPOSER, compute_epoch_at_slot(block.slot))
    return compute_signing_root(block, domain)
