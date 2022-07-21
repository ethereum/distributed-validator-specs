include "../commons.dfy"

// Note: Only safety properties are expressed at the moment.
module ConsensusSpec
{
    import opened Types 

    datatype InCommand<!D> = 
    | Start(node: BLSPubkey)
    | Stop(node: BLSPubkey)

    datatype OutCommand<D> = 
    | Decided(node: BLSPubkey, value: D)

    datatype HonestNodeStatus = NOT_DECIDED | DECIDED

    datatype ConsensusInstance<!D(!new, 0)> = ConsensusInstance(
        all_nodes: set<BLSPubkey>,
        decided_value: Optional<D>,
        honest_nodes_status: map<BLSPubkey, HonestNodeStatus>,
        ghost honest_nodes_validity_functions: set<D -> bool>
    )    


    function f(n:nat): nat
    requires n > 0 
    {
        (n-1)/3
    }

    function quorum(n:nat):nat
    // returns ceil(2n/3)


    predicate isConditionForSafetyTrue<D(!new, 0)>(
        s: ConsensusInstance
    )
    {
        quorum(|s.all_nodes|) <= |s.honest_nodes_status|
    }

    predicate Init<D(!new, 0)>(
        s: ConsensusInstance, 
        all_nodes: set<BLSPubkey>, 
        honest_nodes: set<BLSPubkey>)
    {
        && s.all_nodes == all_nodes
        && !s.decided_value.isPresent()
        && s.honest_nodes_status.Keys == honest_nodes
        && forall t | t in s.honest_nodes_status.Values :: t == NOT_DECIDED
    }

    predicate Next<D(!new, 0)>(
        s: ConsensusInstance,
        honest_nodes_validity_predicates: map<BLSPubkey, D -> bool>,        
        s': ConsensusInstance,
        output: Optional<OutCommand>
    )
    {
        exists s'': ConsensusInstance ::
            // First we let the consensus protocol and the various nodes possibly decide on a value
            && NextConsensusDecides(s, honest_nodes_validity_predicates, s'')
            // Then we let the node take an input/output step
            && NextNodeStep(s'', honest_nodes_validity_predicates, s', output)

    }

    predicate NextNodeStep<D(!new, 0)>(
        s: ConsensusInstance,
        honest_nodes_validity_predicates: map<BLSPubkey, D -> bool>,
        s': ConsensusInstance,
        output: Optional<OutCommand>
    )
    {
        && output.isPresent()
        && var n := output.safe_get().node;
        && n in s.honest_nodes_status.Keys 
        && n in honest_nodes_validity_predicates.Keys
        && s.honest_nodes_status[n] in {DECIDED}
        &&  if isConditionForSafetyTrue(s) then
                && s.decided_value.isPresent()
                && output.safe_get().value == s.decided_value.safe_get()
                && s' == s
            else
                s' == s     
    }

    predicate NextConsensusDecides<D(!new, 0)>(
        s: ConsensusInstance,
        honest_nodes_validity_predicates: map<BLSPubkey, D -> bool>,    
        s': ConsensusInstance
    )
    {
        && s'.honest_nodes_validity_functions == s.honest_nodes_validity_functions + honest_nodes_validity_predicates.Values
        && (
            || (
                && (isConditionForSafetyTrue(s) ==>
                                                    && s'.decided_value.isPresent()
                                                    && (s.decided_value.isPresent() ==> s'.decided_value == s.decided_value)
                                                    && (exists vp | vp in s'.honest_nodes_validity_functions :: vp(s'.decided_value.safe_get()))
                )
                && s'.honest_nodes_status.Keys == s.honest_nodes_status.Keys
                && forall n | n in s.honest_nodes_status.Keys ::
                    if n in honest_nodes_validity_predicates then 
                        s.honest_nodes_status[n] == DECIDED ==> s'.honest_nodes_status[n] == DECIDED
                    else 
                        s'.honest_nodes_status[n] == s.honest_nodes_status[n]
                && s'.all_nodes == s.all_nodes
            ) 
            || (
                s' == s
            )
        )
     
    }    
}