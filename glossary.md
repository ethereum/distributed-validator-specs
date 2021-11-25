# Glossary

## Ethereum Concepts

- Validator: A public key participating in proof-of-stake validation of Ethereum. In Phase 0, validators are expected to perform attestation & block proposal duties for beacon chain blocks.
- Validator Client (VC): Software to perform the duties of Validators. The VC has access to the private key of the Validators.

## Distributed Validator Concepts

- Distributed Validator (DV): A group of participants collboratively performing the duties of a Validator. The Validator's private key is secret-shared among the participants so that a complete signature cannot be formed without some majority threshold of participants.
- Co-Validator: A threshold BLS public key participating in the DV protocol for a particular Validator.
- Distributed Validator Client (DVC): Software to participate as a Co-Validator by running the DV protocol (or, to participate as multiple Co-Validators that are each associated with a different Validator). The DVC has access to the private key(s) of the Co-Validator(s), which is(are) the secret-shared threshold private key of the respective Validator(s).