# Ethereum Distributed Validator Specification

This repo is WIP. Dumping stuff here for now, will clean up soon.

## General Architecture

`Beacon Node <--> SSV Node <--> Validator Client`

SSV Node sits in the middle of the BN and VC. The VC implementation is unchanged (or minimal necessary changes).

## Desired Properties
- Safety: Validator is never slashed unless `X` fraction of the SSV-VC nodes are Byzantine, even under asynchronous network
- No Deadlock: The protocol never ends up in a deadlock state where no progress can be made
- Liveness: The protocol will eventually produce a new attestation/block, under partially synchronous network


## Design Rationale
- Validity of attestation data must be checked against the slashing DB at the beginning of the consensus process
- If the consensus process returns an attestation, then the slashing DB must allow it at that time
- There can only be one consensus process running at any given moment
- Slashing DB cannot be updated when a consensus process is running
- Consensus processes for attestation duties must be spawned in increasing order of slot

## Spec

Assuming some round based consensus protocol with leader.

### Attestation Production

Leader:
- Get attestation data from BN
- Propose attestation in consensus protocol

Node:
- Follow consensus protocol: wait for proposal, make pre-vote, etc.
- To determine validity of the proposal, check against for unslashability in the slashing DB.
- When consensus returns a value, submit value to VC for threshold signing
- Broadcast & combine threshold signed values to generate complete signed value
- Send complete signed value to BN for p2p gossip

Disregard voting for the correct fork for now. 
