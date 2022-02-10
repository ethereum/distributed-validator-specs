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
    bn_get_attestation_duties_for_epoch,
    bn_get_proposer_duties_for_epoch,
    fill_attestation_duties_with_val_index,
    filter_and_fill_proposer_duties_with_val_index,
    bn_get_fork_version,
    rs_sign_attestation,
    rs_sign_randao_reveal,
    rs_sign_block,
)
from tests.helpers.networking import (
    broadcast_randao_reveal_signature_share,
    listen_for_randao_reveal_signature_shares,
    construct_signed_randao_reveal,
)
from tests.helpers.patch_dvspec import (
    replace_method_in_dvspec,
)


replace_method_in_dvspec("consensus_on_attestation", consensus_on_attestation)
replace_method_in_dvspec("consensus_on_block", consensus_on_block)
replace_method_in_dvspec("bn_get_fork_version", bn_get_fork_version)
replace_method_in_dvspec("rs_sign_attestation", rs_sign_attestation)
replace_method_in_dvspec("rs_sign_randao_reveal", rs_sign_randao_reveal)
replace_method_in_dvspec("rs_sign_block", rs_sign_block)
replace_method_in_dvspec("broadcast_randao_reveal_signature_share", broadcast_randao_reveal_signature_share)
replace_method_in_dvspec("listen_for_randao_reveal_signature_shares", listen_for_randao_reveal_signature_shares)
replace_method_in_dvspec("construct_signed_randao_reveal", construct_signed_randao_reveal)


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
    proposer_duties = bn_get_proposer_duties_for_epoch(current_epoch+1)
    filled_proposer_duties = filter_and_fill_proposer_duties_with_val_index(state, proposer_duties)
    while len(filled_proposer_duties) == 0:
        proposer_duties = bn_get_proposer_duties_for_epoch(current_epoch+1)
        filled_proposer_duties = filter_and_fill_proposer_duties_with_val_index(state, proposer_duties)
    proposer_duty = filled_proposer_duties[0]
    distributed_validator = get_distributed_validator_by_index(state, proposer_duty.validator_index)
    slashing_db = distributed_validator.slashing_db
    serve_proposer_duty(slashing_db, proposer_duty)
