from test import (
    bn_get_attestation_duties_for_epoch,
    bn_get_attestation_data,
    bn_submit_attestation,
    vc_is_slashable,
    vc_sign_attestation,
    consensus,
)

"""
1. At the start of every epoch, get attestation duties for epoch+1 by running
    bn_get_attestation_duties_for_epoch(validator_indices, epoch+1)
2. For each attestation_duty recevied in Step 1, schedule
    serve_attestation_duty(attestation_duty) at 1/3rd way through the slot
    attestation_duty.slot
"""

def serve_attestation_duty(attestation_duty):
    # Obtain lock on consensus process here - only a single consensus instance
    # should be running at any given time
    attestation_data = consensus(attestation_duty)

    # 1. Threshold sign attestation from local VC
    threshold_signed_attestation = vc_sign_attestation(attestation_data, attestation_duty)
    # 2. Broadcast threshold signed attestation
    # 3. Reconstruct complete signed attestation by combining threshold signed attestations
    complete_signed_attestation = threshold_signed_attestation
    # 4. Send complete signed attestation to BN for broadcast
    bn_submit_attestation(complete_signed_attestation)

    # Release lock on consensus process here
