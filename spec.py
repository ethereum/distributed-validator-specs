from test import (
    get_current_time,
    BeaconNode,
    ValidatorClient,
    calculate_attestation_time,
    consensus,
)
from eth2spec.phase0.mainnet import (
    Attestation,
)

def attestation_duty_loop():
    # run in a loop forever
    attestation_duty = beacon_node.get_next_attestation_duty()
    while get_current_time() < calculate_attestation_time(attestation_duty.slot):
        pass

    # Obtain lock on consensus process here - only a single consensus instance
    # should be running at any given time
    attestation_data = consensus(attestation_duty.slot)

    # 1. Threshold sign attestation from local VC
    threshold_signed_attestation_data = validator_client.sign_attestation(attestation_data)
    # 2. Broadcast threshold signed attestation
    # TODO
    # 3. Reconstruct complete signed attestation by combining threshold signed attestations
    complete_signed_attestation_data = threshold_signed_attestation_data
    complete_signed_attestation = Attestation(data=complete_signed_attestation_data)
    # 4. Send complete signed attestation to BN for broadcast
    beacon_node.broadcast_attestation(complete_signed_attestation)
    
    # Release lock on consensus process here

    print(
        f"Duty Slot: {attestation_duty.slot}, Attestation Slot: {attestation_data.slot}")

beacon_node = BeaconNode()
validator_client = ValidatorClient()

while True:
    attestation_duty_loop()
