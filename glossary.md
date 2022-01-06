# Glossary

## Ethereum Concepts

- **Validator**: A public key participating in proof-of-stake validation of Ethereum. In Phase 0, validators are expected to perform attestation & block proposal duties for beacon chain blocks.
- **Validator Client (VC)**: Software to perform the duties of Validators. The VC has access to the private key of the Validators.
- **Consensus Client (CC)**: A consensus client's duty is to run the proof of stake consensus layer of Ethereum, often referred to as the beacon chain. Examples of Consensus clients include:

  - [Prysm](https://docs.prylabs.network/docs/how-prysm-works/beacon-node)
  - [Teku](https://docs.teku.consensys.net/en/stable/)
  - [Lighthouse](https://lighthouse-book.sigmaprime.io/api-bn.html)
  - [Nimbus](https://nimbus.guide/)
  - [Lodestar](https://github.com/ChainSafe/lodestar)

- **Execution Client (EC)**: An execution client (formerly known as an Eth1 client) specialises in running the EVM and managing the transaction pool for the Ethereum network. These clients provide execution payloads to consensus clients for inclusion into blocks. Examples of execution clients include:

  - [Go-Ethereum](https://geth.ethereum.org/)
  - [Nethermind](https://docs.nethermind.io/nethermind/)
  - [Erigon](https://github.com/ledgerwatch/erigon)

## Distributed Validator Concepts

- **Distributed Validator (DV)**: A group of participants collboratively performing the duties of a single Validator on the Ethereum network. The Validator's private key is secret-shared among the participants so that a complete signature cannot be formed without some majority threshold of participants.
- **Co-Validator**: A threshold BLS public key participating in the DV protocol for a _particular_ Validator.
- **Distributed Validator Client (DVC)**: Software to participate as a Co-Validator by running the DV protocol (or, to participate as multiple Co-Validators that are each associated with a different Validator). The DVC has access to an SECP256K1 key that serves as its authentication to its peers, along with a distributed validator client certificate, which authorises this DVC to act on behalf of a given distributed validator key share.
- **Distributed Validator Node**: A distributed validator node is the set of clients an operator needs to configure and run to fulfil the duties of a Distributed Validator Operator. An operator may also run redundant execution and consensus clients, an execution payload relayer like [mev-boost](https://github.com/flashbots/mev-boost), or other monitoring or telemetry services on the same hardware to ensure optimal performance.
- **Distributed Validator Cluster**: A distributed validator cluster is a collection of distributed validator nodes connected together to service a set of distributed validators generated during a DVK ceremony.
- **Distributed Validator Key**: A distributed validator key is one persistent BLS public key emulated by a group of distributed validator key shares completing threshold signing together.
- **Distributed Validator Key Share**: A distributed validator key share is one BLS private key that is part of the collection of shares that together can sign on behalf of the group distributed validator key.
- **Distributed Validator Key Generation Ceremony**: A distributed key generation ceremony where a number of parties can come together to trustlessly create a distributed validator key, its associated deposit and exit data, and each parties' distributed validator key share and DVC certificate.

## Example

An illustrative example for usage of terms described above:

- Ethereum Validator with pubkey `0xa5c91...` is operated as a Distributed Validator.
- 4 Co-Validators are participating in the Distributed Validator for Validator `0xa5c91...`.
- The private key associated with `0xa5c91...` was generated during a distributed validator key generation ceremony using _3-of-4_ secret-sharing among the 4 Co-Validators such that a _3-of-4_ threshold signature scheme is setup.
  - In simpler terms, the private key for `0xa5c91...` is split into 4 pieces, each in the custody of one of the Co-Validators such that at least 3 of them have to collaborate to produce a signature from `0xa5c91...`.
- Each Co-Validator is running the Distributed Validator Client software to participate the in the Distributed Validator.
