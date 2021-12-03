from dvspec.utils.types import (
    BLSPubkey,
    Root,
    SlashingDB,
    ValidatorIndex,
    List,
)
from dvspec.spec import (
    CoValidator,
    DistributedValidator,
    State,
    ValidatorIdentity,
)


"""
Helpers for State
"""


def build_distributed_validator(validator_identity: ValidatorIdentity,
                                num_covalidators: int = 4) -> DistributedValidator:
    co_validators = []
    for i in range(1, num_covalidators):
        co_validators.append(CoValidator(validator_identity=validator_identity, pubkey=BLSPubkey(0x00), index=i))
    slashing_db = SlashingDB(interchange_format_version=5,
                             genesis_validators_root=Root(),
                             data=[])
    distributed_validator = DistributedValidator(validator_identity=validator_identity,
                                                 co_validators=co_validators,
                                                 slashing_db=slashing_db)
    return distributed_validator


def build_state(num_distributed_validators: int) -> State:
    distributed_validators = []
    for i in range(num_distributed_validators):
        validator_identity = ValidatorIdentity(pubkey=BLSPubkey(i), index=i)
        distributed_validators.append(build_distributed_validator(validator_identity))
    state = State(distributed_validators=distributed_validators)
    return state


def get_validator_indices(state: State) -> List[ValidatorIndex]:
    validator_indices = []
    for dv in state.distributed_validators:
        validator_indices.append(dv.validator_identity.index)
    return validator_indices


def get_distributed_validator_by_index(state: State, validator_index: ValidatorIndex) -> DistributedValidator:
    dv_list = []
    for dv in state.distributed_validators:
        if dv.validator_identity.index == validator_index:
            dv_list.append(dv)
    assert len(dv_list) == 1
    return dv_list[0]
