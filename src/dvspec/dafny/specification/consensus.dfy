include "../commons.dfy"

// Note: Only safety properties are expressed at the moment.
module ConsensusSpec
{
    import opened Types 

    datatype InCommand = 
    | Start(node: BLSPubkey)
    | Stop(node: BLSPubkey)

    datatype OutCommand<D> = 
    | Decided(node: BLSPubkey, value: D)

    datatype HonestNodeStatus = NEVER_STARTED | STARTED | DECIDED | STOPPED

    datatype ConsensusInstance<D(!new, 0)> = ConsensusInstance(
        all_nodes: set<BLSPubkey>,
        decided_value: Optional<D>,
        honest_nodes_status: map<BLSPubkey, HonestNodeStatus>
    )    


    function f(n:nat): nat
    requires n > 0 
    {
        (n-1)/3
    }

    function quorum(n:nat):nat
    // returns ceil(2n/3)

    function getRunningNodes<D(!new, 0)>(
        s: ConsensusInstance
    ): set<BLSPubkey> 
    {
        set n | 
            && n in s.honest_nodes_status
            && s.honest_nodes_status[n] in {STARTED, DECIDED}
    }

    predicate isConditionForSafetyTrue<D(!new, 0)>(
        s: ConsensusInstance
    )
    {
        quorum(|s.all_nodes|) <= |s.honest_nodes_status|
    }

    predicate isNodeRunning<D(!new, 0)>(
        s: ConsensusInstance,
        node: BLSPubkey
    )
    {
        && node in s.honest_nodes_status.Keys
        && s.honest_nodes_status[node] in {STARTED, DECIDED}
    }

    predicate Init<D(!new, 0)>(
        s: ConsensusInstance, 
        all_nodes: set<BLSPubkey>, 
        honest_nodes: set<BLSPubkey>)
    {
        && s.all_nodes == all_nodes
        && !s.decided_value.isPresent()
        && s.honest_nodes_status.Keys == honest_nodes
        && forall t | t in s.honest_nodes_status.Values :: t == NEVER_STARTED
    }

    predicate Next<D(!new, 0)>(
        s: ConsensusInstance,
        input: Optional<InCommand>,
        validityPredicate: D -> bool,
        s': ConsensusInstance,
        output: Optional<OutCommand>
    )
    {
        exists s'': ConsensusInstance ::
            // First we let the consensus protocol and the various nodes possibly decide on a value
            && NextConsensusDecides(s, validityPredicate, s'')
            // Then we let the node take an input/output step
            && NextNodeStep(s'', input, s', output)

    }

    predicate NextNodeStep<D(!new, 0)>(
        s: ConsensusInstance,
        input: Optional<InCommand>,
        s': ConsensusInstance,
        output: Optional<OutCommand>
    )
    {
        && (
            || (
                && input.isPresent()
                && !output.isPresent()
                && input.safe_get().Start?
                && var n := input.safe_get().node;
                && n in s.honest_nodes_status.Keys 
                && s.honest_nodes_status[n] in {NEVER_STARTED, STARTED}
                && s' == s.(
                    honest_nodes_status := s.honest_nodes_status[n := STARTED]
                )
                
            )
            || (
                && input.isPresent()
                && !output.isPresent()
                && input.safe_get().Stop?
                && var n := input.safe_get().node;
                && n in s.honest_nodes_status.Keys 
                && s.honest_nodes_status[n] == STARTED
                && s' == s.(
                    honest_nodes_status := s.honest_nodes_status[n := STOPPED]
                )
                
            )    
            || (
                && !input.isPresent()
                && output.isPresent()
                && var n := output.safe_get().node;
                && n in s.honest_nodes_status.Keys 
                && s.honest_nodes_status[n] in {DECIDED}
                &&  if isConditionForSafetyTrue(s) then
                        && s.decided_value.isPresent()
                        && output.safe_get().value == s.decided_value.safe_get()
                        && s' == s
                    else
                        s' == s
            )      
        )
     
    }

    predicate NextConsensusDecides<D(!new, 0)>(
        s: ConsensusInstance,
        validityPredicate: D -> bool,
        s': ConsensusInstance
    )
    {
        && (
            || (
                && (isConditionForSafetyTrue(s) ==>
                                                    && s'.decided_value.isPresent()
                                                    && (s.decided_value.isPresent() ==> s'.decided_value == s.decided_value)
                                                    && validityPredicate(s'.decided_value.safe_get())
                )
                && s'.honest_nodes_status.Keys == s.honest_nodes_status.Keys
                && forall n | n in s.honest_nodes_status.Keys ::
                    if s.honest_nodes_status[n] == STARTED then 
                        s'.honest_nodes_status[n] in {STARTED, DECIDED}
                    else 
                        s'.honest_nodes_status[n] == s.honest_nodes_status[n]
                && s'.all_nodes == s.all_nodes
            ) 
            || (
                s' == s
            )
        )
     
    }    

    // datatype Consensus = ConsensusInstance 
    // (
    //     consensus_on_attestation_data: imaptotal<Slot, DVSAttestationConsensusData>
    // )
}