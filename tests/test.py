from dvspec.spec import (
    serve_attestation_duty,
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
from tests.helpers.eth_node_interface import (
    bn_get_attestation_duties_for_epoch,
    fill_attestation_duties_with_val_index,
)


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

    # TODO: Need to replace dvspec.consensus.consensus_on_attestation with
    # tests.helpers.consensus.consensus_on_attestation
    serve_attestation_duty(slashing_db, attestation_duty)
