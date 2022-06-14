include "../commons.dfy"
abstract module DVCNode_Implementation
{
    import opened Types
    import opened CommonFunctions
    import opened DVCNode_Externs: DVCNode_Externs

    export PublicInterface
        reveals DVCNode,
                AttestationSignatureShareDB
        provides
                DVCNode.serve_attestation_duty, 
                DVCNode.att_consensus_decided, 
                DVCNode.listen_for_attestation_shares,
                DVCNode.listen_for_new_imported_blocks,
                DVCNode.resend_attestation_share,
                DVCNode.bn
        provides Types, DVCNode_Externs

    type AttestationSignatureShareDB = map<(AttestationData, seq<bool>), set<AttestationShare>>   

    class DVCNode {

        var current_attesation_duty: Optional<AttestationDuty>;
        var attestation_duties_queue: seq<AttestationDuty>;
        // var pubkey: BLSPubkey;
        var attestation_slashing_db: AttestationSlashingDB;
        var attestation_shares_db: AttestationSignatureShareDB;
        var attestation_share_to_broadcast: Optional<AttestationShare>
        var construct_signed_attestation_signature: (set<AttestationShare>) -> Optional<BLSSignature>;
        var peers: set<BLSPubkey>;
        // TODO: Note difference with spec.py
        var dv_pubkey: BLSPubkey;
        var future_att_consensus_instances_already_decided: set<Slot>

        var att_consensus: Consensus;
        const network : Network
        const bn: BeaconNode;
        const rs: RemoteSigner;

        constructor(
            pubkey: BLSPubkey, 
            dv_pubkey: BLSPubkey,
            att_consensus: Consensus, 
            peers: set<BLSPubkey>,
            network: Network,
            bn: BeaconNode,
            rs: RemoteSigner,
            construct_signed_attestation_signature: (set<AttestationShare>) -> Optional<BLSSignature>)
        {
            current_attesation_duty := None;
            attestation_share_to_broadcast := None;
            attestation_shares_db := map[];

            // this.pubkey := pubkey;
            this.att_consensus := att_consensus;
            this.peers := peers;
            this.network := network;
            this.rs := rs;
            this.bn := bn;
            this.construct_signed_attestation_signature := construct_signed_attestation_signature;
            this.dv_pubkey := dv_pubkey;
            this.future_att_consensus_instances_already_decided := {};
        }

        method serve_attestation_duty(
            attestation_duty: AttestationDuty
        )
        modifies this
        {
            attestation_duties_queue := attestation_duties_queue + [attestation_duty];
            check_for_next_queued_duty();
        }

        method check_for_next_queued_duty()
        modifies this
        decreases attestation_duties_queue
        {
            if attestation_duties_queue != []
            {
                if attestation_duties_queue[0].slot in future_att_consensus_instances_already_decided
                {
                    attestation_duties_queue := attestation_duties_queue[1..];
                    check_for_next_queued_duty();
                }
                else
                {
                    start_next_duty(attestation_duties_queue[0]);
                }
            }
        }

        method start_next_duty(attestation_duty: AttestationDuty)
        modifies this
        {
            attestation_shares_db := map[];
            attestation_share_to_broadcast := None;
            current_attesation_duty := Some(attestation_duty);
            att_consensus.start(attestation_duty.slot);            
        }        

        method update_attestation_slashing_db(attestation_data: AttestationData, attestation_duty_pubkey: BLSPubkey)
        modifies this       
        {
            // assert not is_slashable_attestation_data(attestation_slashing_db, attestation_data, pubkey)
            // TODO: Is the following required given that each co-validator only handles one pubkey?
            // slashing_db_data = get_slashing_db_data_for_pubkey(attestation_slashing_db, pubkey)
            var slashing_db_attestation := SlashingDBAttestation(
                                                source_epoch := attestation_data.source.epoch,
                                                target_epoch := attestation_data.target.epoch,
                                                signing_root := hash_tree_root(attestation_data));
            attestation_slashing_db := attestation_slashing_db + {slashing_db_attestation};
        }

        method att_consensus_decided(
            id: Slot,
            decided_attestation_data: AttestationData
        ) returns (r: Status)
        modifies this
        {
            var local_current_attestation_duty :- current_attesation_duty.get();
            update_attestation_slashing_db(decided_attestation_data, local_current_attestation_duty.pubkey);
 
            var fork_version := bn.get_fork_version(compute_start_slot_at_epoch(decided_attestation_data.target.epoch));
            var attestation_signing_root := compute_attestation_signing_root(decided_attestation_data, fork_version);
            var attestation_signature_share := rs.sign_attestation(decided_attestation_data, fork_version, attestation_signing_root);
            // TODO: What is attestation_signature_share.aggregation_bits?
            var attestation_with_signature_share := AttestationShare(
                aggregation_bits := get_aggregation_bits(local_current_attestation_duty.validator_index),
                data := decided_attestation_data, 
                signature :=attestation_signature_share
            ); 

            attestation_share_to_broadcast := Some(attestation_with_signature_share);
            network.send_att_share(attestation_with_signature_share, peers);           
        }

        function method get_aggregation_bits(
            index: nat
        ): (s: seq<bool>)
        ensures |s| == index
        ensures forall i | 0 <= i < |s| :: if i == index - 1 then s[i] else !s[i]
        {
            seq(index, i => if i + 1 == index then true else false)
        }        

        method listen_for_attestation_shares(
            attestation_share: AttestationShare
        )
        modifies this
        {
            // TODO: Decide 
            // 1. whether to add att shares to db only if already served attestation duty
            // 2. when to wipe out the db
            var k := (attestation_share.data, attestation_share.aggregation_bits);
            attestation_shares_db := 
                attestation_shares_db[k := 
                                        getOrDefault(attestation_shares_db, k, {}) + 
                                        {attestation_share}
                                    ];
                        
            if construct_signed_attestation_signature(attestation_shares_db[k]).isPresent()
            {
                var aggregated_attestation := 
                        Attestation(
                            aggregation_bits := attestation_share.aggregation_bits,
                            data := attestation_share.data,
                            signature := construct_signed_attestation_signature(attestation_shares_db[k]).safe_get()
                        );
                bn.submit_attestation(aggregated_attestation); 
            }  
        }

        method listen_for_new_imported_blocks(
            block: BeaconBlock
        ) returns (s: Status)
        modifies this
        {
            var valIndex :- bn.get_validator_index(block.body.state_root, dv_pubkey);
            var i := 0;

            while i < |block.body.attestations|
            // for i := 0 to |block.body.attestations|
            {
                var a := block.body.attestations[i];
                var committee :- bn.get_epoch_committees(block.body.state_root, a.data.index);
                
                if
                && a in block.body.attestations
                // && a.data.slot == process.attestation_duty.slot 
                // && a.data.index == process.attestation_duty.committee_index
                && valIndex.Some?
                && valIndex.v in committee
                && var i:nat :| i < |committee| && committee[i] == valIndex.v;
                && i < |a.aggregation_bits|
                && a.aggregation_bits[i]
                && (current_attesation_duty.isPresent() ==> a.data.slot >= current_attesation_duty.safe_get().slot)
                {
                    future_att_consensus_instances_already_decided := future_att_consensus_instances_already_decided + {a.data.slot};
                }

                i := i + 1;
            }


            if current_attesation_duty.isPresent() && current_attesation_duty.safe_get().slot in future_att_consensus_instances_already_decided
            {
                att_consensus.stop(current_attesation_duty.safe_get().slot);
                check_for_next_queued_duty();
            }                                   
        }

        method resend_attestation_share(
        )
        modifies this
        {
            if attestation_share_to_broadcast.isPresent()
            {
                network.send_att_share(attestation_share_to_broadcast.safe_get(), peers);
            }
        }        
    }    
}

module DVCNode_Externs
{
    import opened Types
    import opened CommonFunctions

    class Consensus {
        ghost var consensus_commands_sent: seq<ConsensusCommand>

        constructor()
        {
            consensus_commands_sent := [];
        }

        method {:extern} start(
            id: Slot
        )
        ensures consensus_commands_sent == old(consensus_commands_sent) + [ConsensusCommand.Start(id)]

        method {:extern} stop(
            id: Slot
        )
        ensures consensus_commands_sent == old(consensus_commands_sent) + [ConsensusCommand.Stop(id)]        
    }     

    class Network  
    {
        ghost var att_shares_sent: seq<set<MessaageWithRecipient<AttestationShare>>>;

        constructor()
        {
            att_shares_sent := [];
        }

        method {:extern} send_att_share(att_share: AttestationShare, receipients: set<BLSPubkey>)
        ensures att_shares_sent == old(att_shares_sent)  + [addRecepientsToMessage(att_share, receipients)]
    }

    class BeaconNode
    {
        ghost var state_roots_of_imported_blocks: set<Root>;
        ghost const attestations_submitted: seq<Attestation>; 

        constructor()
        {
            attestations_submitted := [];
            state_roots_of_imported_blocks := {};
        }

        method {:extern} get_fork_version(s: Slot) returns (v: Version)

        method {:extern} submit_attestation(attestation: Attestation)
        ensures attestations_submitted == old(attestations_submitted) + [attestation]

        // https://ethereum.github.io/beacon-APIs/?urls.primaryName=v1#/Beacon/getEpochCommittees
        method {:extern} get_epoch_committees(
            state_id: Root,
            index: CommitteeIndex
        ) returns (s: Status, sv: seq<ValidatorIndex>)
        ensures state_id in state_roots_of_imported_blocks <==> s.Success?
        ensures uniqueSeq(sv)  

        // https://ethereum.github.io/beacon-APIs/#/Beacon/getStateValidator
        method {:extern} get_validator_index(
            state_id: Root,
            validator_id: BLSPubkey
        ) returns (s: Status, vi: Optional<ValidatorIndex>)
        ensures state_id in state_roots_of_imported_blocks <==> s.Success?
    }

    class RemoteSigner
    {
        const pubkey: BLSPubkey;

        constructor(
            pubkey: BLSPubkey
        )
        {
            this.pubkey := pubkey;
        }

        method {:extern} sign_attestation(
            attestation_data: AttestationData, 
            fork_version: Version, 
            signing_root: Root           
        ) returns (s: BLSSignature)
        requires signing_root == compute_attestation_signing_root(attestation_data, fork_version)

    }
}

