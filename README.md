# Ethereum Distributed Validator Specification

Distributed Validators (DV) are a technique for distributing the job of an Ethereum validator among a set of distributed nodes in order to improve resilience (safety, liveness, or both) as compared to running a validator client on a single machine.

## Introduction

### Motivation

#### Traditional Validator Client Setup

Ethereum validators participate in the [proof-of-stake (PoS) protocol](https://github.com/ethereum/consensus-specs) by signing messages (such as blocks or attestations) using their staking private key. The staking key is accessible only by the validator client software, which schedules the creation & signing of messages according to the duties assigned to the validator. Some risks involved in a traditional validator client setup are:

- The staking private key resides in one location. If an adversary gains access to this key, it can create conflicting messages that result in slashing of the validator's deposit.
  - Stakers who do not operate their own validator need to hand over their staking private key to the operator. They must trust the operator for the security of their staking private key.
- If the validator client software is unable to create timely messages to perform validator duties, the validator suffers an inactivity leak that reduces its balance.
  - This could happen due to causes such as software crashes, loss of network connection, hardware faults, etc.
- If the Beacon Node to which the validator client is connected has a fault, a validator may end up following a minority fork resulting it appearing to be offline to the rest of the PoS protocol.

#### Distributed Validator Protocol

The Distributed Validator protocol presents a solution to mitigate the risks & concerns associated with traditional, single Validator Client setups. In addition, this protocol can be used to enable advanced staking setups such as decentralized staking pools.

### Basic Concepts

**Note**: Refer to the [glossary](glossary.md) for an explanation of new terms introduced in the Distributed Validator specifications.

The two fundamental concepts behind Distributed Validators are:

- **consensus**: the responsibilities of a single validator are split among several operators, who must work together to reach agreement on how to vote before signing any message.
- **_M-of-N_ threshold signatures**: the validator's staking key is split into _N_ pieces and each of the operators holds a share. When at least _M_ of the operators reach consensus on how to vote, they each sign the message with their share and a combined signature can be reconstructed from the shares.

Ethereum proof-of-stake uses the BLS signature scheme, in which the private keys can be _M-of-N_ secret-shared (using Shamir secret sharing) to implement _M-of-N_ threshold signatures.

By combining a suitable (safety-favouring) consensus algorithm with an _M-of-N_ threshold signature scheme, the DV protocol ensures that agreement is backed up by cryptography and at least _M_ operators agree about any decision.

### Resources

#### Implementations

The following are existing implementations of Distributed Validator technology (but not necessarily implementations of this specification).

- [`python-ssv`](https://github.com/dankrad/python-ssv): A proof-of-concept implementation of the distributed validator protocol in Python that interacts with the [Prysm Ethereum client](https://github.com/prysmaticlabs/prysm).
- [`ssv`](https://github.com/bloxapp/ssv): An implementation of the distributed validator protocol in Go that interacts with the [Prysm Ethereum client](https://github.com/prysmaticlabs/prysm).
- [`charon`](https://github.com/ObolNetwork/charon): An implementation of the protocol in Go that supports all clients that can validate over the [Beacon RESTful APIs](https://ethereum.github.io/beacon-APIs/#/ValidatorRequiredApi)

#### Documents

- [Distributed Validator Architecture Video Introduction](https://www.youtube.com/watch?v=awBX1SrXOhk)

### General Architecture

![General Architecture](figures/general-architecture.png)

This specification presents a way to implement Distributed Validator Client software as middleware between the Beacon Node (BN) and Validator Client (VC):

- all communication between the BN and VC is intercepted by the DVC in order for it to provide the additional DV functionality.
- the BN & VC are unaware of the presence of the DVC, i.e., they think they are connected to each other as usual.

### Assumptions

- We assume _N_ total nodes and an _M-of-N_ threshold signature scheme.
  - For general compatibility with BFT consensus protocols, we assume that `M = (2 * N / 3) + 1`.
- This specification assumes [some leader-based safety-favoring consensus protocol](src/dvspec/consensus.py) for the operators to decide on signing upon the same attestation/block. We assume that the consensus protocol runs successfully with _M_ correct nodes out of _N_ total nodes.
- We assume the usual prerequisites for safe operation of the Validator Client, such as an up-to-date anti-slashing database, correct system clock, etc.
- We disregard voting on the "correct" Ethereum fork for now - this functionality will be added in a future update.

### Desired Guarantees

- **Safety (against key theft)**:
  - The Validator's staking private key is secure unless security is compromised at more than _M_ of the _N_ operators.
- **Safety (against slashing)**:
  - Under the assumption of an asynchronous network, the Validator is never slashed unless more than 1/3rd of the operators are Byzantine.
  - Under the assumption of a synchronous network, the Validator is never slashed unless more than 2/3rds of the operators are Byzantine.
- **Liveness**: The protocol will eventually produce a new attestation/block under partially synchronous network unless more than 1/3rd of the operators are Byzantine.

## Specification

Technical details about the specification are described in [`src/dvspec/`](src/dvspec/).

## Developer Getting Started

This repo relies on [Python](https://www.python.org/), and uses [venv](https://docs.python.org/3/library/venv.html) to manage its dependencies.

To get started with this repo using [make](https://www.gnu.org/software/make/manual/make.html), run the following commands:

```sh
# Create virtual environment, download dependencies
make install

# Lint the specs
make venv_lint

# Execute the spec tests
make venv_test

# Get help
make help
```
