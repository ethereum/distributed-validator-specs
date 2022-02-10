# Ethereum Distributed Validator Specification

## Organization

The specifications are organized as follows:
- [`spec.py` - distributed validator specification](spec.py) defines the behavior of a Co-Validator regarding attestation & block production processes.
- [`eth_node_interface.py` - Ethereum node interface](eth_node_interface.py) describes the interface to communicate with the associated Beacon Node (BN) & Remote Signer (RS).
- [`consensus.py` - consensus specification](consensus.py) describes the basic structure for the consensus protocol used between Co-Validators.
- [`networking.py` - networking specification](networking.py) defines the required networking logic between Distributed Validator Clients.
- [`utils/` - utilities](utils/) contain type definitions and misc. helper functions for the specification.

## Operation of Distributed Validator Client (DVC)

### Communication between DVC and RS
The BN & RS communicate over HTTP in accordance with the [Ethereum Beacon Node API](https://github.com/ethereum/beacon-APIs/). **Note**: The RS API is not yet part of an Ethereum standard. The DV protocol is designed such that the DVC can operate as middleware between the BN & RS. Both the BN & RS are unaware of the presence of the DVC. The RS communicates with the DVC as they would with a BN.

The interaction between the DVC and RS is driven by the DVC. The RS hosts a server that allows incoming requests for signing Ethereum messages. The DVC instructs the RS to sign appropriate messages to serve the Validator's assigned duties.


The basic operation of the DVC is as follows:
1. Request duties from the BN at the start of every epoch
2. Schedule serving of the received duties at the appropriate times
3. When triggered to serve a duty:
    1. Form consensus with other Co-Validators over the data to be signed
    2. Instruct the RS to sign over the decided data.
    3. After getting the signature share from the RS, broadcast it to other Co-Validators
    4. Re-combination of signature shares after receiving enough signature shares
    5. Send the combined signature to the attached BN to be gossiped to the greater PoS network

### Anti-Slashing Measures at the DVC
VCs have an in-built slashing protection mechanism called the "slashing database" (a misnomer for "anti-slashing database"). The slashing database stores information about the messages that have been signed by the Validator. When new messages are to be signed, they are first checked against the slashing DB to ensure that a slashable pair of messages will not be produced (see - slashing rules for [attestations](https://github.com/ethereum/consensus-specs/blob/master/specs/phase0/beacon-chain.md#is_slashable_attestation_data) & [blocks](https://github.com/ethereum/consensus-specs/blob/master/specs/phase0/beacon-chain.md#proposer-slashings)). 

While forming consensus over data, it is essential for the DVC to check the validity of the data against this slashing DB. However, since the DVC does not have direct access to the RS's slashing DB (if any), it has to maintain a local cache of its state. The slashing DB at the DVC operates as follows:
1. When initializing the setup, the DVC requires input about the state of the RS's slashing DB (if any). When provided, the DVC will initialize a local slashing DB of its own with the given state.
2. While forming consensus, the DVC checks that the proposed consensus value is not slashable against its slashing DB.
3. When a consensus value is decided, the DVC adds the value to its slashing DB.

The initialization process can be carried out without change to the RS: with the RS and DVC shut down, manually export the RS's slashing DB and import it in the DVC. Automatic initialization of the DVC is not possible without changes to the RS implementation (this is a WIP feature in active discussion).


## Sequence Diagrams

### Attestation Production Process

![UML for Attestation Production Process](figures/dv-attestation-production-process.png)

### Block Production Process

![UML for Block Production Process](figures/dv-block-production-process.png)