include "../commons.dfy"
include "../implementation/dvc_implementation.dfy"


abstract module DVCNode_Spec {
    import opened Types 
    import opened CommonFunctions
    import opened DVCNode_Implementation`PublicInterface
    import opened DVCNode_Externs

    function {:axiom} bn_get_fork_version(slot: Slot): Version

    function {:axiom} bn_get_validator_index(bnState: BNState, state_id: Root, validator_id: BLSPubkey): (vi: Optional<ValidatorIndex>)
    requires state_id in bnState.state_roots_of_imported_blocks

    function {:axiom} bn_get_epoch_committees(bnState: BNState, state_id: Root, index: CommitteeIndex): (sv: seq<ValidatorIndex>) 
    requires state_id in bnState.state_roots_of_imported_blocks   

    function {:axiom} rs_sign_attestation(
        attestation_data: AttestationData, 
        fork_version: Version, 
        signing_root: Root,
        rs: RSState
    ): BLSSignature
    requires signing_root == compute_attestation_signing_root(attestation_data, fork_version)

    lemma {:axiom} rs_attestation_sign_and_verification_propetries<T>()
    ensures forall attestation_data, fork_version, signing_root, rs |
                    rs_sign_attestation.requires(attestation_data, fork_version, signing_root, rs) ::
                    verify_bls_siganture(
                        signing_root,
                        rs_sign_attestation(attestation_data, fork_version, signing_root, rs),
                        rs.pubkey
                    )
    ensures forall signing_root, signature, pubkey ::
        verify_bls_siganture(signing_root, signature, pubkey) <==>
            exists attestation_data, fork_version ::
            var rs := RSState(pubkey);
            && rs_sign_attestation.requires(attestation_data, fork_version, signing_root, rs)
            && signature == rs_sign_attestation(attestation_data, fork_version, signing_root, rs)

    ensures forall ad1, fv1, sr1, pk1, ad2, fv2, sr2, pk2 ::
            && rs_sign_attestation.requires(ad1, fv1, sr1, pk1)
            && rs_sign_attestation.requires(ad2, fv2, sr2, pk2)
            && rs_sign_attestation(ad1, fv1, sr1, pk1) == rs_sign_attestation(ad2, fv2, sr2, pk2) 
            ==>
            && sr1 == sr2 
            && pk1 == pk2      

    datatype BNState = BNState(
        state_roots_of_imported_blocks: set<Root>   
    )

    function getInitialBN(): BNState
    {
        BNState(
            state_roots_of_imported_blocks := {}
        )
    }    

    datatype RSState = RSState(
        pubkey: BLSPubkey
    )

    function getInitialRS(
        pubkey: BLSPubkey
    ): RSState
    {
        RSState(
            pubkey := pubkey
        )
    }  

    datatype DVCNodeState = DVCNodeState(
        current_attesation_duty: Optional<AttestationDuty>,
        attestation_duties_queue: seq<AttestationDuty>,
        attestation_slashing_db: AttestationSlashingDB,
        attestation_shares_db: AttestationSignatureShareDB,
        attestation_share_to_broadcast: Optional<AttestationShare>,
        peers: set<BLSPubkey>,
        construct_signed_attestation_signature: (set<AttestationShare>) -> Optional<BLSSignature>,
        // TODO: Note difference with spec.py
        dv_pubkey: BLSPubkey,
        future_att_consensus_instances_already_decided: set<Slot>,
        bn: BNState,
        rs: RSState
    )    

    datatype Outputs = Outputs(
        att_shares_sent: set<MessaageWithRecipient<AttestationShare>>,
        att_consensus_commands_sent: set<ConsensusCommand>,
        attestations_submitted: set<Attestation>
    )    

    function getEmptyOuputs(): Outputs
    {
        Outputs(
            {},
            {},
            {}
        )
    }  


    function multicast<M>(m: M, receipients: set<BLSPubkey>): set<MessaageWithRecipient<M>>
    {
        addRecepientsToMessage(m, receipients)
    }

    datatype DVCNodeStateAndOuputs = DVCNodeStateAndOuputs(
        state: DVCNodeState,
        outputs: Outputs
    )

    datatype Event = 
    | ServeAttstationDuty(attestation_duty: AttestationDuty)
    | AttConsensusDecided(id: Slot, decided_attestation_data: AttestationData)
    | ReceviedAttesttionShare(attestation_share: AttestationShare)
    | ImportedNewBlock(block: BeaconBlock)
    | ResendAttestationShares
    | NoEvent


    predicate Init(
        s: DVCNodeState,
        dv_pubkey: BLSPubkey,
        peers: set<BLSPubkey>,
        construct_signed_attestation_signature: (set<AttestationShare>) -> Optional<BLSSignature>
    )
    {
        s == DVCNodeState(
            current_attesation_duty := None,
            attestation_duties_queue := [],
            attestation_slashing_db := {},
            attestation_shares_db := map[],
            attestation_share_to_broadcast := None,
            peers := peers,
            construct_signed_attestation_signature := construct_signed_attestation_signature,
            dv_pubkey := dv_pubkey,
            future_att_consensus_instances_already_decided := {},
            bn := getInitialBN(),
            rs := s.rs
        )
    }

    predicate Next(
        s: DVCNodeState,
        event: Event,
        s': DVCNodeState,
        outputs: Outputs
    )
    {
        var newNodeStateAndOutputs := DVCNodeStateAndOuputs(
            state := s',
            outputs := outputs
        );

        match event 
            case ServeAttstationDuty(attestation_duty) => 
                f_serve_attestation_duty(s, attestation_duty) == newNodeStateAndOutputs
            case AttConsensusDecided(id, decided_attestation_data) => 
                && f_att_consensus_decided.requires(s, id,  decided_attestation_data)
                && f_att_consensus_decided(s, id,  decided_attestation_data) == newNodeStateAndOutputs
            case ReceviedAttesttionShare(attestation_share) => 
                f_listen_for_attestation_shares(s, attestation_share) == newNodeStateAndOutputs
            case ImportedNewBlock(block) => 
                f_listen_for_new_imported_blocks.requires(s, block)
                && f_listen_for_new_imported_blocks(s, block) == newNodeStateAndOutputs
            case ResendAttestationShares => 
                f_resend_attestation_share(s) == newNodeStateAndOutputs
            case NoEvent => 
                DVCNodeStateAndOuputs(state := s, outputs := getEmptyOuputs() ) == newNodeStateAndOutputs
    }

    function f_serve_attestation_duty(
        process: DVCNodeState,
        attestation_duty: AttestationDuty
    ): DVCNodeStateAndOuputs
    {
        f_check_for_next_queued_duty(
            process.(
                attestation_duties_queue := process.attestation_duties_queue + [attestation_duty]
            )
        )
    }    

    function f_check_for_next_queued_duty(process: DVCNodeState): DVCNodeStateAndOuputs
    decreases process.attestation_duties_queue
    {
        if process.attestation_duties_queue != [] then
            
                if process.attestation_duties_queue[0].slot in process.future_att_consensus_instances_already_decided then
                    f_check_for_next_queued_duty(process.(
                        attestation_duties_queue := process.attestation_duties_queue[1..]
                    ))
                else
                    f_start_next_duty(process, process.attestation_duties_queue[0])
                
        else 
            DVCNodeStateAndOuputs(
                state := process,
                outputs := getEmptyOuputs()
            )

    }         

    function f_start_next_duty(process: DVCNodeState, attestation_duty: AttestationDuty): DVCNodeStateAndOuputs
    {
        DVCNodeStateAndOuputs(
            state :=  process.(
                        attestation_shares_db := map[],
                        attestation_share_to_broadcast := None,
                        current_attesation_duty := Some(attestation_duty)
            ),
            outputs := getEmptyOuputs().(
                att_consensus_commands_sent := {ConsensusCommand.Start(attestation_duty.slot)}
            )
        )        
    }      

    function get_aggregation_bits(
        index: nat
    ): seq<bool>
    {
        seq(index, i => if i + 1 == index then true else false)
    } 

    function f_update_attestation_slashing_db(attestation_slashing_db: AttestationSlashingDB, attestation_data: AttestationData, attestation_duty_pubkey: BLSPubkey): AttestationSlashingDB     
    {
        // assert not is_slashable_attestation_data(attestation_slashing_db, attestation_data, pubkey)
        // TODO: Is the following required given that each co-validator only handles one pubkey?
        // slashing_db_data = get_slashing_db_data_for_pubkey(attestation_slashing_db, pubkey)
        var slashing_db_attestation := SlashingDBAttestation(
                                            source_epoch := attestation_data.source.epoch,
                                            target_epoch := attestation_data.target.epoch,
                                            signing_root := hash_tree_root(attestation_data));
        
        attestation_slashing_db + {slashing_db_attestation}
    }      

    function f_att_consensus_decided(
        process: DVCNodeState,
        id: Slot,
        decided_attestation_data: AttestationData
    ): DVCNodeStateAndOuputs
    requires process.current_attesation_duty.isPresent()
    {
        var local_current_attestation_duty := process.current_attesation_duty.safe_get();
        var attestation_slashing_db := f_update_attestation_slashing_db(process.attestation_slashing_db, decided_attestation_data, local_current_attestation_duty.pubkey);

        var fork_version := bn_get_fork_version(compute_start_slot_at_epoch(decided_attestation_data.target.epoch));
        var attestation_signing_root := compute_attestation_signing_root(decided_attestation_data, fork_version);
        var attestation_signature_share := rs_sign_attestation(decided_attestation_data, fork_version, attestation_signing_root, process.rs);
        // TODO: What is attestation_signature_share.aggregation_bits?
        var attestation_with_signature_share := AttestationShare(
                aggregation_bits := get_aggregation_bits(local_current_attestation_duty.validator_index),
                data := decided_attestation_data, 
                signature :=attestation_signature_share
            ); 

        DVCNodeStateAndOuputs(
            state := process.(
                attestation_share_to_broadcast := Some(attestation_with_signature_share)
            ),
            outputs := getEmptyOuputs().(
                att_shares_sent := multicast(attestation_with_signature_share, process.peers)
            )
        )         
    }    

    function f_listen_for_attestation_shares(
        process: DVCNodeState,
        attestation_share: AttestationShare
    ): DVCNodeStateAndOuputs
    {
        var k := (attestation_share.data, attestation_share.aggregation_bits);

        var newProcess := process.(
            attestation_shares_db := 
                process.attestation_shares_db[k := 
                                        getOrDefault(process.attestation_shares_db, k, {}) + 
                                        {attestation_share}
                                    ]
        );

                    
        if process.construct_signed_attestation_signature(newProcess.attestation_shares_db[k]).isPresent() then
        
            var aggregated_attestation := 
                    Attestation(
                        aggregation_bits := attestation_share.aggregation_bits,
                        data := attestation_share.data,
                        signature := process.construct_signed_attestation_signature(newProcess.attestation_shares_db[k]).safe_get()
                    );

            DVCNodeStateAndOuputs(
                state := newProcess,
                outputs := getEmptyOuputs().(
                    attestations_submitted := {aggregated_attestation} 
                )
            ) 
        else 
            DVCNodeStateAndOuputs(
                state := newProcess,
                outputs := getEmptyOuputs()
            ) 
    }
 
    predicate isMyAttestation(
        a: Attestation,
        process: DVCNodeState,
        block: BeaconBlock,
        valIndex: Optional<ValidatorIndex>
    )
    requires block.body.state_root in process.bn.state_roots_of_imported_blocks
    {
            && var committee := bn_get_epoch_committees(process.bn, block.body.state_root, a.data.index);
            && valIndex.Some?
            && valIndex.v in committee
            && var i:nat :| i < |committee| && committee[i] == valIndex.v;
            && i < |a.aggregation_bits|
            && a.aggregation_bits[i]
            && (process.current_attesation_duty.isPresent() ==> a.data.slot >= process.current_attesation_duty.safe_get().slot)            
    }

    function f_listen_for_new_imported_blocks(
        process: DVCNodeState,
        block: BeaconBlock
    ): DVCNodeStateAndOuputs
    requires block.body.state_root in process.bn.state_roots_of_imported_blocks
    {
        var valIndex := bn_get_validator_index(process.bn, block.body.state_root, process.dv_pubkey);
         
        var s := set a |
                && a in block.body.attestations
                && isMyAttestation(a, process, block, valIndex)
            ::
                a.data.slot;

        var newProces := process.(
            future_att_consensus_instances_already_decided := process.future_att_consensus_instances_already_decided + s
        );

        if process.current_attesation_duty.isPresent() && process.current_attesation_duty.safe_get().slot in process.future_att_consensus_instances_already_decided then
            // Stop(current_attesation_duty.safe_get().slot);
            var r := f_check_for_next_queued_duty(newProces);
            DVCNodeStateAndOuputs(
                state := r.state,
                outputs := r.outputs.(
                    att_consensus_commands_sent := r.outputs.att_consensus_commands_sent + {ConsensusCommand.Stop(process.current_attesation_duty.safe_get().slot)}
                )
            )
        else
            DVCNodeStateAndOuputs(
                state := newProces,
                outputs := getEmptyOuputs()
            )
    }    
  
    function f_resend_attestation_share(
        process: DVCNodeState
    ): DVCNodeStateAndOuputs
    {
        DVCNodeStateAndOuputs(
            state := process,
            outputs := getEmptyOuputs().(
                att_shares_sent :=
                    if process.attestation_share_to_broadcast.isPresent() then
                        multicast(process.attestation_share_to_broadcast.safe_get(), process.peers)
                    else
                        {}
                    )
        )

    }        
}

abstract module DVCNode_Externs_Proofs refines DVCNode_Externs
{
    import opened DVCNode_Spec

    function toBNState(bn: BeaconNode): BNState
    reads bn
    {
        BNState(
            state_roots_of_imported_blocks := bn.state_roots_of_imported_blocks
        )
    }

    class BeaconNode...
    {
        method get_fork_version...
        ensures bn_get_fork_version(s) == v

        method get_validator_index...
        ensures state_id in this.state_roots_of_imported_blocks ==> bn_get_validator_index(toBNState(this),state_id, validator_id) == vi

        method get_epoch_committees...
        ensures state_id in this.state_roots_of_imported_blocks ==> bn_get_epoch_committees(toBNState(this), state_id, index) == sv
    }


    class RemoteSigner...
    {
        method sign_attestation...
        ensures rs_sign_attestation(attestation_data, fork_version, signing_root, toRSState(this)) == s
    }

    function toRSState(
        rs: RemoteSigner
    ): RSState
    reads rs 
    {
        RSState(
            pubkey := rs.pubkey
        )
    }

}