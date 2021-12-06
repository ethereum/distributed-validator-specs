# Ethereum Distributed Validator Specification

## Spec

The specifications are organized as follows:
- [`spec.py` - distributed validator specification](spec.py) defines the behavior of a Co-Validator regarding attestation & block production processes.
- [`eth_node_interface.py` - Ethereum node interface](eth_node_interface.py) describes the interface to communicate with the associated Beacon Node & Validator Client.
- [`consensus.py` - consensus specification](consensus.py) describes the basic structure for the consensus protocol used between Co-Validators.
- [`networking.py` - networking specification](networking.py) defines the required networking logic between Distributed Validator Clients.
- [`utils/` - utilities](utils/) contain type definitions and misc. helper functions for the specification.

### Attestation Production Process

![UML for Attestation Production Process](figures/dv-attestation-production-process.png)

### Block Production Process

![UML for Block Production Process](figures/dv-block-production-process.png)