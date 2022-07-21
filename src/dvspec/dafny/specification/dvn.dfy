include "../commons.dfy"
include "dvc_spec.dfy"
include "consensus.dfy"
include "network.dfy"

abstract module DV 
{
    import opened Types
    import opened CommonFunctions
    import opened NetworkSpec
    import opened ConsensusSpec
    import opened DVCNode_Spec
    import opened DVCNode_Externs_Proofs

    datatype Adversary = Adversary(
        nodes: set<BLSPubkey>
    )

    datatype DVState = DVState(
        all_nodes: set<BLSPubkey>,
        honest_nodes_states: map<BLSPubkey, DVCNodeState>,
        adversary: Adversary,
        dv_pubkey: BLSPubkey,
        consensus_on_attestation_data: imaptotal<Slot, ConsensusInstance<AttestationData>>,
        att_network: NetworkSpec.Network<AttestationShare>,
        all_attestations_created: set<Attestation>,
        construct_signed_attestation_signature: (set<AttestationShare>) -> Optional<BLSSignature>
    )

    datatype Event = 
    | AdeversaryTakingStep(node: BLSPubkey, new_attestation_shares_sent: set<MessaageWithRecipient<AttestationShare>>,
        messagesReceivedByTheNode: set<AttestationShare>)
    | HonestNodeTakingStep(node: BLSPubkey, event: Types.Event, nodeOutputs: DVCNode_Spec.Outputs)

    predicate Init(
        s: DVState,
        initial_attestation_slashing_db: set<SlashingDBAttestation>
    )
    {
        && s.honest_nodes_states.Keys !! s.adversary.nodes !! {s.dv_pubkey}
        && s.all_nodes == s.honest_nodes_states.Keys + s.adversary.nodes
        && s.honest_nodes_states.Keys != {}
        && |s.adversary.nodes| <= f(|s.all_nodes|)
        && (                            
            forall 
                att_shares: set<AttestationShare>
                ::
                (
                    && exists verifiable_att_shares: set<AttestationShare>, data: AttestationData, fork_version: Version ::
                        && verifiable_att_shares <= att_shares
                        && var signing_root := compute_attestation_signing_root(data, fork_version);
                        && |verifiable_att_shares| >= quorum(|s.all_nodes|)
                        && (forall att_share |
                                att_share in verifiable_att_shares ::
                                && att_share.data == data 
                                && exists signer :: 
                                    && signer in s.all_nodes
                                    && verify_bls_siganture(signing_root, att_share.signature, signer)
                        )
                )
                <==>
                    s.construct_signed_attestation_signature(att_shares).isPresent()
        )    
        &&
            (
            forall 
                att_shares: set<AttestationShare>
                ::
                    var constructed_sig := s.construct_signed_attestation_signature(att_shares);
                    constructed_sig.isPresent() ==>  
                        forall verifiable_att_shares: set<AttestationShare>, data: AttestationData, fork_version: Version |
                            && verifiable_att_shares <= att_shares
                            && |verifiable_att_shares| >= quorum(|s.all_nodes|)
                            && (forall att_share |
                                    att_share in verifiable_att_shares :: att_share.data == data)
                            ::
                                    && var signing_root := compute_attestation_signing_root(data, fork_version);
                                    verify_bls_siganture(signing_root, constructed_sig.safe_get(), s.dv_pubkey)

        )   
        && s.all_attestations_created == {}
        && (
            forall n | n in s.honest_nodes_states.Keys ::
                DVCNode_Spec.Init(s.honest_nodes_states[n], s.dv_pubkey, s.all_nodes, s.construct_signed_attestation_signature, initial_attestation_slashing_db, n)
        )      
        &&  NetworkSpec.Init(s.att_network, s.all_nodes)
        &&  (
            forall ci | ci in  s.consensus_on_attestation_data.Values ::
                ConsensusSpec.Init(ci, s.all_nodes, s.honest_nodes_states.Keys)
        )
    }

    predicate Next(
        s: DVState,
        s': DVState 
    )
    {
        exists e ::
            NextEvent(s, e, s')
    }

    predicate NextEvent(
        s: DVState,
        event: Event,
        s': DVState
    )
    {
        && s'.honest_nodes_states.Keys == s.honest_nodes_states.Keys
        && (
            match event
                case HonestNodeTakingStep(node, nodeEvent, nodeOutputs) => 
                    && NextHonestNode(s, node, nodeEvent, nodeOutputs, s')
                case AdeversaryTakingStep(node, new_attestation_share_sent, messagesReceivedByTheNode) => 
                    NextAdversary(s, node, new_attestation_share_sent, messagesReceivedByTheNode, s')
        )

    }

    function add_block_to_bn(
        s: DVCNodeState,
        block: BeaconBlock
    ): DVCNodeState
    {
        s.(
            bn := s.bn.(
                state_roots_of_imported_blocks := s.bn.state_roots_of_imported_blocks + {block.body.state_root}
            )
        )
    }

    predicate NextHonestNode(
        s: DVState,
        node: BLSPubkey,
        nodeEvent: Types.Event,
        nodeOutputs: DVCNode_Spec.Outputs,
        s': DVState        
    ) 
    {
        && node in s.honest_nodes_states.Keys
        && var s_w_honest_node_states_updated :=
            if nodeEvent.ImportedNewBlock? then 
                s.(
                    honest_nodes_states := s.honest_nodes_states[node := add_block_to_bn(s.honest_nodes_states[node], nodeEvent.block)]
                )
            else 
                s 
            ;
        && NextHonestAfterAddingBlockToBn(s_w_honest_node_states_updated, node, nodeEvent, nodeOutputs, s' )
                
    }

    predicate NextHonestAfterAddingBlockToBn(
        s: DVState,
        node: BLSPubkey,
        nodeEvent: Types.Event,
        nodeOutputs: DVCNode_Spec.Outputs,
        s': DVState
    )
    {
        && s'.honest_nodes_states.Keys == s.honest_nodes_states.Keys
        && s'.dv_pubkey == s.dv_pubkey        
        && node in s.honest_nodes_states.Keys 
        && var new_node_state := s'.honest_nodes_states[node];
        && DVCNode_Spec.Next(s.honest_nodes_states[node], nodeEvent, new_node_state, nodeOutputs)
        && s'.honest_nodes_states == s.honest_nodes_states[
            node := new_node_state
        ]
        && s'.all_attestations_created == s.all_attestations_created + nodeOutputs.attestations_submitted
        && var messagesReceivedByTheNode :=
            match nodeEvent
                case ReceviedAttesttionShare(attestation_share) => {attestation_share}
                case _ => {}
            ;
        && NetworkSpec.Next(s.att_network, s'.att_network, node, nodeOutputs.att_shares_sent, messagesReceivedByTheNode)
        && (
            forall cid | cid in s.consensus_on_attestation_data.Keys ::
                var output := 
                    if nodeEvent.AttConsensusDecided? && nodeEvent.id == cid then 
                        Some(Decided(node, nodeEvent.decided_attestation_data))
                    else
                        None
                    ;

                && var validityPredicates := 
                    map n |
                            && n in s.honest_nodes_states.Keys 
                            && cid in s.honest_nodes_states[n].attestation_consensus_engine_state.attestation_consensus_active_instances.Keys
                        ::
                            s.honest_nodes_states[n].attestation_consensus_engine_state.attestation_consensus_active_instances[cid].validityPredicate
                    ;

                ConsensusSpec.Next(
                    s.consensus_on_attestation_data[cid],
                    validityPredicates,
                    s'.consensus_on_attestation_data[cid],
                    output
                )
        )      
        && s'.adversary == s.adversary
        && s'.construct_signed_attestation_signature == s.construct_signed_attestation_signature
    }    

    predicate NextAdversary(
        s: DVState,
        node: BLSPubkey,
        new_attestation_shares_sent: set<MessaageWithRecipient<AttestationShare>>,
        messagesReceivedByTheNode: set<AttestationShare>,
        s': DVState
    )
    {

        (
            && node in (s.all_nodes - s.honest_nodes_states.Keys)
            && (
                forall new_attestation_share_sent, signer | new_attestation_share_sent in new_attestation_shares_sent ::
                    verify_bls_siganture(new_attestation_share_sent.message.data, new_attestation_share_sent.message.signature, signer) ==> signer in s.adversary.nodes
            )
            && NetworkSpec.Next(s.att_network, s'.att_network, node, new_attestation_shares_sent, messagesReceivedByTheNode)
            && s.all_attestations_created <= s'.all_attestations_created
            && var new_aggregated_attestations_sent := s'.all_attestations_created - s.all_attestations_created;
            && (forall aggregated_attestation_sent | aggregated_attestation_sent in new_aggregated_attestations_sent ::
                    exists attestation_shares ::
                            && attestation_shares <= s'.att_network.allMessagesSent
                            // && var sig_shares := set x | x in attestation_shares :: x.signature;
                            && var constructed_sig := s.construct_signed_attestation_signature(attestation_shares);
                            && constructed_sig.isPresent()
                            && constructed_sig.safe_get() == aggregated_attestation_sent.signature
            )
            && s' == s.(
                honest_nodes_states := s'.honest_nodes_states,
                att_network := s'.att_network,
                consensus_on_attestation_data := s'.consensus_on_attestation_data,
                all_attestations_created := s'.all_attestations_created
            )            
        )         
    }


}