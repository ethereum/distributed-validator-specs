from pkgutil import iter_modules
import importlib

from eth2spec.phase0.mainnet import SLOTS_PER_EPOCH

import dvspec
from dvspec.spec import (
    serve_attestation_duty,
    serve_proposer_duty,
)

from helpers.time import (
    get_current_time,
    compute_epoch_at_time,
)
from tests.helpers.state import (
    build_state,
    get_validator_indices,
    get_distributed_validator_by_index,
)
from tests.helpers.consensus import (
    consensus_on_attestation,
    consensus_on_block,
)
from tests.helpers.eth_node_interface import (
    SLOTS_PER_EPOCH,
    bn_get_attestation_duties_for_epoch,
    bn_produce_attestation_data,
    bn_submit_attestation,
    bn_get_proposer_duties_for_epoch,
    bn_produce_block,
    fill_attestation_duties_with_val_index,
    filter_and_fill_proposer_duties_with_val_index,
)

# Replace unimplemented methods from dvspec by methods from the test module
def replace_module_method(module, method_name_string, replacement_method) -> None:
    try:
        getattr(module, method_name_string)
        setattr(module, method_name_string, replacement_method)
    except AttributeError:
        pass

def replace_method_in_dvspec(method_name_string, replacement_method) -> None:
    for dvspec_submodule_info in iter_modules(dvspec.__path__):
        dvspec_submodule = importlib.import_module(dvspec.__name__ + '.' + dvspec_submodule_info.name)
        replace_module_method(dvspec_submodule, method_name_string, replacement_method)

replace_method_in_dvspec("consensus_on_attestation", consensus_on_attestation)
replace_method_in_dvspec("consensus_on_block", consensus_on_block)


def test_basic_attestation() -> None:
    state = build_state(5)
    time = get_current_time()

    current_epoch = compute_epoch_at_time(time)
    validator_indices = get_validator_indices(state)
    attestation_duties = bn_get_attestation_duties_for_epoch(validator_indices, current_epoch+1)
    filled_attestation_duties = fill_attestation_duties_with_val_index(state, attestation_duties)
    attestation_duty = filled_attestation_duties[0]

    distributed_validator = get_distributed_validator_by_index(state, attestation_duty.validator_index)
    slashing_db = distributed_validator.slashing_db
    serve_attestation_duty(slashing_db, attestation_duty)


def test_basic_block() -> None:
    state = build_state(5)
    time = get_current_time()

    current_epoch = compute_epoch_at_time(time)
    validator_indices = get_validator_indices(state)
    proposer_duties = bn_get_proposer_duties_for_epoch(current_epoch+1)
    filled_proposer_duties = filter_and_fill_proposer_duties_with_val_index(state, proposer_duties)
    while len(filled_proposer_duties) == 0:
        proposer_duties = bn_get_proposer_duties_for_epoch(current_epoch+1)
        filled_proposer_duties = filter_and_fill_proposer_duties_with_val_index(state, proposer_duties)
    proposer_duty = filled_proposer_duties[0]
    distributed_validator = get_distributed_validator_by_index(state, proposer_duty.validator_index)
    slashing_db = distributed_validator.slashing_db
    serve_proposer_duty(slashing_db, proposer_duty)