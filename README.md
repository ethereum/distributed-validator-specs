# Ethereum Distributed Validator Specification

Distributed Validators allow for implementing an Ethereum validator using a set of distributed nodes in a way that improves the resilience as compared to running a client on a single machine.

## Introduction

### Motivation
Ethereum validators participate in the proof-of-stake protocol by signing messages (such as blocks or attestations) using their staking private key. The staking key is accessible only by the validator client software, which schedules the creation & signing of messages according to the duties assigned to the validator. Some risks involved in a traditional validator client setup are:
- The staking private key resides in one location. If an adversary gains access to this key, it can create conflicting messages that result in slashing of the validator's deposit.
    - Stakers who do not operate their own validator need to hand over their staking private key to the operator. They must trust the operator for the security of their staking private key.
- If the validator client software is unable to create timely messages to perform validator duties, the validator suffers an inactivity leak that reduces its balance.
    - This could happen due to causes such as software crashes, loss of network connection, hardware faults, etc.

The Distributed Validator protocol presents a solution to mitigate the risks & concerns mentioned above. In addition, this protocol can be used to enable advanced staking setups such as decentralized staking pools.

### Basic Concepts

The two fundamental concept behind Distributed Validators are:
- **secret-sharing**: a secret is split into *N* shares such that at least *M* shares need to be combined to reconstruct the secret (known as *(M,N)-*secret-sharing).
- **threshold signatures**: a private key is split into *N* pieces such that creating a signature from the corresponding public key over some data requires combining signatues from at least *M* pieces of the private key on the same data (known as *(M,N)-*threshold signatures).

Ethereum proof-of-stake uses the BLS12-381 siganture scheme, in which the private keys can be *(M,N)-*secret-shared to implement *(M,N)-*threshold signatures.

**Note**: Refer to the [glossary](glossary.md) for an explanation of new terms introduced in the Distributed Validator specifications.

An Ethereum Validator's private key is secret-shared into *N* pieces, each assigned to a Co-Validator, such that at least *M* pieces are required to create a complete signature from the Validator. The Co-Validators collectively participate in the Distributed Validator protocol to generate blocks & attestations signed by the Validator that satisfy the Validator's assigned duties.

### General Architecture

![General Architecture](figures/general-architecture.png)

This specification presents a way to implement Distributed Validator Client software as middleware between the Beacon Node and Validator Client. 

### Desired Guarantees
- Safety: 
    - Under the assumption of an asynchronous network, the Validator is never slashed unless more than 2/3rd of the Co-Validators are Byzantine.
    - Under the assumption of a synchronous network, the Validator is never slashed unless more than 1/3rd of the Co-Validators are Byzantine.
- No Deadlock: The protocol never ends up in a deadlock state where no progress can be made
- Liveness: The protocol will eventually produce a new attestation/block, under partially synchronous network

### Assumptions
- This specification assumes [some leader-based consensus protocol](src/dvspec/consensus.py) for the DV nodes to decide on signing upon the same attestation/block.
- We disregard the voting on the "correct" Ethereum fork for now - this functionality will be added in a future update.

### Design Rationale
- Validity of attestation data must be checked against the slashing DB at the beginning of the consensus process
- If the consensus process returns an attestation, then the slashing DB must allow it at that time
- There can only be one consensus process running at any given moment
- Slashing DB cannot be updated when a consensus process is running
- Consensus processes for attestation duties must be spawned in increasing order of slot

## Spec

The distributed validator [specification](src/dvspec/spec.py) defines the behavior of the distributed validator regarding attestation & block production processes. It utilizes the [standard Ethereum node interface](src/dvspec/eth_node_interface.py) to communicate with the associated Beacon Node & Validator Client.

### Attestation Production Process

![UML for Attestation Production Process](figures/dv-attestation-production-process.png)

### Block Production Process

![UML for Block Production Process](figures/dv-block-production-process.png)
