from test import (
    get_current_time,
    bn_get_next_attestation_duty,
    bn_broadcast_attestation,
    vc_sign_attestation,
    calculate_attestation_time,
    consensus,
)
from eth2spec.phase0.mainnet import (
    Attestation,
)

def attestation_duty_loop():
    # run in a loop forever
    attestation_duty = bn_get_next_attestation_duty()
    while get_current_time() < calculate_attestation_time(attestation_duty.slot):
        pass

    # Obtain lock on consensus process here - only a single consensus instance
    # should be running at any given time
    attestation_data = consensus(attestation_duty.slot)

    # 1. Threshold sign attestation from local VC
    threshold_signed_attestation_data = vc_sign_attestation(attestation_data, attestation_duty.validator_index)
    # 2. Broadcast threshold signed attestation
    # TODO
    # 3. Reconstruct complete signed attestation by combining threshold signed attestations
    complete_signed_attestation_data = threshold_signed_attestation_data
    complete_signed_attestation = Attestation(data=complete_signed_attestation_data)
    # 4. Send complete signed attestation to BN for broadcast
    bn_broadcast_attestation(complete_signed_attestation)

    # Release lock on consensus process here

    print(
        f"Duty Slot: {attestation_duty.slot}, Attestation Slot: {attestation_data.slot}")

while True:
    attestation_duty_loop()
