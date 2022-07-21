module Types 
{
    type ValidatorIndex = nat
    type Epoch = nat 
    type Slot = nat
    const SLOTS_PER_EPOCH := 32
    type {:extern "CommitteeIndex"} CommitteeIndex(!new, 0, ==)
    // type Attestation 
    type {:extern "BLSSignature"} BLSSignature(==, !new, 0)
    type {:extern "BLSPubkey"} BLSPubkey(==, !new, 0)
    type {:extern "Bytes32"} Bytes32(0)
    // type SignedBeaconBlock
    type {:extern "Root"} Root(==, 0, !new)
    type {:extern "SyncCommitteeSignature"} SyncCommitteeSignature
    type {:extern "SyncCommitteeDuty"} SyncCommitteeDuty   
    type {:extern "Version"} Version(!new)   
    datatype Checkpoint = Checkpoint(
        epoch: Epoch,
        root: Root
    )

    type {:extern "Domain"} Domain(==)
    // type AttestationDuty 
    datatype AttestationData = AttestationData(
        slot: Slot,
        index: CommitteeIndex,
        // LMD GHOST vote
        beacon_block_root: Root,
        // FFG vote
        source: Checkpoint,
        target: Checkpoint
    )
    // type ProposerDuty
    datatype BeaconBlock = BeaconBlock(
        body: BeaconBlockBody
        // ... Other fields irrelevant to this spec
    )

    datatype BeaconBlockBody = BeaconBlockBody(
        attestations: seq<Attestation>,
        state_root: Root
        // ... Other fields irrelevant to this spec
    )

    datatype Attestation = Attestation(
        aggregation_bits: seq<bool>,
        data: AttestationData,
        signature: BLSSignature
    )

    datatype AttestationShare = AttestationShare(
        aggregation_bits: seq<bool>,
        data: AttestationData,
        signature: BLSSignature
    )

    datatype AttestationDuty = AttestationDuty(
        pubkey: BLSPubkey,
        validator_index: ValidatorIndex,
        committee_index: CommitteeIndex,
        committee_length: nat,
        committees_at_slot: nat,
        validator_committee_index: ValidatorIndex,
        slot: Slot        
    )

    datatype ProposerDuty = ProposerDuty(
        pubkey: BLSPubkey,
        validator_index: ValidatorIndex,
        slot: Slot        
    )

    datatype SignedBeaconBlock = SignedBeaconBlock(
        message: BeaconBlock,
        signature: BLSSignature
    )

    datatype BlockSlashingDB = BlockSlashingDB
    type SlashingDBBlock(==, !new)

    datatype  SlashingDBAttestation = SlashingDBAttestation(
        source_epoch: Epoch,
        target_epoch: Epoch,
        signing_root: Optional<Root>
    )

    datatype Status =
    | Success
    | Failure(error: string)
    {
        predicate method IsFailure() { this.Failure?  }

        function method PropagateFailure(): Status
            requires IsFailure()
        {
            Status.Failure(this.error)
        }
    }   

    datatype Event = 
    | ServeAttstationDuty(attestation_duty: AttestationDuty)
    | AttConsensusDecided(id: Slot, decided_attestation_data: AttestationData)
    | ReceviedAttesttionShare(attestation_share: AttestationShare)
    | ImportedNewBlock(block: BeaconBlock)
    | ResendAttestationShares
    | NoEvent    

    type imaptotal<!T1(!new), T2> = x: imap<T1,T2> | forall e: T1 :: e in x.Keys witness *

    datatype Optional<T(0)> = Some(v: T) | None
    {
        predicate method isPresent()
        {
            this.Some?
        }

        method get() returns (o: Status, v: T)
        ensures isPresent() ==> o.Success? && v == safe_get()
        ensures !isPresent() ==> o.Failure?
        {
            if isPresent()
            {
                return Success, this.v;
            }
            else {
                var dummyVal;
                return Failure(""), dummyVal;
            }
        }

        function method safe_get(): T
        requires isPresent()
        {
            this.v
        } 

        function toSet(): set<T> 
        {
            if isPresent() then
                {this.v}
            else 
                {}
        }  

        static function toOptional(s: set<T>): (o: Optional<T>)
        requires |s| <= 1
        ensures o.isPresent() ==> s == {o.safe_get()}
        {
            if s == {} then
                None 
            else
                var e :| e in s;
                assert |s - {e}| == 0;
                Some(e)
        } 
    }        

    datatype MessaageWithRecipient<M> = MessaageWithRecipient(
        message: M,
        receipient: BLSPubkey
    ) 
}

module CommonFunctions{
    import opened Types

    function method getOrDefault<T1,T2>(M:map<T1,T2>, key:T1, default:T2): T2
    {
        if key in M.Keys then
            M[key]
        else
            default
    }      

    function method compute_start_slot_at_epoch(epoch: Epoch): Slot
    {
        epoch * SLOTS_PER_EPOCH
    }   

    datatype DomainTypes = 
        | DOMAIN_BEACON_ATTESTER


    // TDOO: What about the genesis_validator_root parameter?
    function method {:extern} compute_domain(
        domain_type: DomainTypes,
        fork_version: Version
    ): (domain: Domain)


    lemma {:axiom} compute_domain_properties()
    ensures forall d1, f1, d2, f2 :: compute_domain(d1, f2) == compute_domain(d2, f2) ==>
        && d1 == d2 
        && f1 == f2

    function method {:extern} compute_signing_root<T>(
        data: T,
        domain: Domain
    ): Root

    lemma {:axiom} compute_signing_root_properties<T>()
    ensures forall da1, do1, da2, do2 ::
        compute_signing_root<T>(da1, do1) == compute_signing_root<T>(da2, do2) ==>
            && da1 == da2 
            && do1 == do2

    // TODO: Fix Python code to match the following (Python code uses epoch)
    function method compute_attestation_signing_root(attestation_data: AttestationData, fork_version: Version): Root
    {
        var domain := compute_domain(DOMAIN_BEACON_ATTESTER, fork_version);
        compute_signing_root(attestation_data, domain)
    }

    predicate uniqueSeq<T(==)>(s: seq<T>)
    {
        forall i, j | 0 <= i < |s| && 0 <= j < |s| :: s[i] == s[j] ==> i == j
    }

    predicate {:extern} verify_bls_siganture<T>(
        data: T,
        signature: BLSSignature,
        pubkey: BLSPubkey
    )   

    function method {:extern} hash_tree_root<T>(data: T): Root 

    lemma {:axiom} hash_tree_root_properties<T>()
    ensures forall d1: T, d2: T :: hash_tree_root(d1) == hash_tree_root(d2) ==> d1 == d2


    function getMessagesFromMessagesWithRecipient<M>(mswr: set<MessaageWithRecipient<M>>): set<M>
    {
        set mwr | mwr in mswr :: mwr.message
    }

    function addReceipientToMessages<M>(sm: set<M>, r: BLSPubkey): set<MessaageWithRecipient<M>>
    {
        set m | m in sm :: MessaageWithRecipient(
            message :=  m,
            receipient := r
        )
    }

    function addRecepientsToMessage<M>(m: M, receipients: set<BLSPubkey>): set<MessaageWithRecipient<M>>
    {
        set r | r in receipients :: MessaageWithRecipient(message := m, receipient := r)
    }

    function setUnion<T>(sets:set<set<T>>):set<T>
    {
        set s, e | s in sets && e in s :: e
    } 

    function seqToSet<T>(s: seq<T>): (r: set<T>)
    {
        set e | e in s
    }

    lemma minOfSetOfIntExists(s: set<int>)
    requires s != {}
    ensures exists min :: 
                        && min in s 
                        && forall e | e in s :: min <= e 
    {
        if |s| == 1 {
            var e :| e in s;
            assert |s - {e}| == 0;
        } 
        else
        {
            var e :| e in s;
            var sMinusE := s - {e};
            assert |s| > 1;
            assert s == sMinusE + {e};
            assert |sMinusE| > 0;
            minOfSetOfIntExists(sMinusE);
            var mMinusE :| mMinusE in sMinusE && forall e' | e' in sMinusE :: e' >= mMinusE;
        }    
    }  

    lemma maxOfSetOfIntExists(s: set<int>)
    requires s != {}
    ensures exists min :: 
                        && min in s 
                        && forall e | e in s :: min >= e 
    {
        if |s| == 1 {
            var e :| e in s;
            assert |s - {e}| == 0;
        } 
        else
        {
            var e :| e in s;
            var sMinusE := s - {e};
            assert |s| > 1;
            assert s == sMinusE + {e};
            assert |sMinusE| > 0;
            maxOfSetOfIntExists(sMinusE);
            var mMinusE :| mMinusE in sMinusE && forall e' | e' in sMinusE :: e' <= mMinusE;
        }    
    }    

    function method {:opaque} minSet(s: set<int>): (min: int)
    requires s != {}
    ensures min in s 
    ensures forall e | e in s :: min <= e 
    {
        minOfSetOfIntExists(s);
        var e :| e in s && forall e' | e' in s :: e' >= e;
        e
    }

    function method {:opaque} maxSet(s: set<int>): (max: int)
    requires s != {}
    ensures max in s 
    ensures forall e | e in s :: max >= e 
    {
        maxOfSetOfIntExists(s);
        var e :| e in s && forall e' | e' in s :: e' <= e;
        e
    }   

    function method get_target_epochs(att_slashing_db: set<SlashingDBAttestation>): (target_epochs: set<nat>)
    requires att_slashing_db != {}
    ensures target_epochs != {}
    {
        var target_epochs := set attn | attn in att_slashing_db :: attn.target_epoch;
        assert var e :| e in att_slashing_db; e.target_epoch in target_epochs;
        target_epochs
    }

    function method get_source_epochs(att_slashing_db: set<SlashingDBAttestation>): (source_epochs: set<nat>)
    requires att_slashing_db != {}
    ensures source_epochs != {}
    {
        var source_epochs := set attn | attn in att_slashing_db :: attn.source_epoch;
        assert var e :| e in att_slashing_db; e.source_epoch in source_epochs;
        source_epochs
    }    

    predicate method is_slashable_attestation_pair(data_1: SlashingDBAttestation, data_2: SlashingDBAttestation)
    {
        // Double vote - over approximated check compared to the 
        // code in the Eth reference implementation as
        // here we do not have all the fields of AttestationData
        || (data_1.target_epoch == data_2.target_epoch) 
        // Surround vote
        || (data_1.source_epoch < data_2.source_epoch && data_2.target_epoch < data_1.target_epoch)        
    }

    predicate is_slashable_attestation_data(att_slashing_db: set<SlashingDBAttestation>, attestation_data: AttestationData)
    {
        // Check for EIP-3076 conditions:
        // https://eips.ethereum.org/EIPS/eip-3076#conditions
        if att_slashing_db != {} then
            var min_target := minSet(get_target_epochs(att_slashing_db));
            var min_source := minSet(get_source_epochs(att_slashing_db));
            if attestation_data.target.epoch <= min_target then
                true 
            else if attestation_data.source.epoch < min_source then
                true
            else 
                var slashing_db_att_for_att_data := 
                    SlashingDBAttestation(
                        source_epoch := attestation_data.source.epoch,
                        target_epoch := attestation_data.target.epoch,
                        signing_root := None
                    );            
                exists past_attn | past_attn in att_slashing_db ::
                        is_slashable_attestation_pair(past_attn, slashing_db_att_for_att_data)
        else
            false        
    } by method 
    {
        // Check for EIP-3076 conditions:
        // https://eips.ethereum.org/EIPS/eip-3076#conditions
        if att_slashing_db != {} 
        {
            var min_target := minSet(get_target_epochs(att_slashing_db));
            var min_source := minSet(get_source_epochs(att_slashing_db));
            if attestation_data.target.epoch <= min_target
            {
                assert is_slashable_attestation_data(att_slashing_db, attestation_data);
                return true;
            }
            else if attestation_data.source.epoch < min_source
            {
                assert is_slashable_attestation_data(att_slashing_db, attestation_data);
                return true;
            }
            else 
            {
                var attns_to_check := att_slashing_db;
                var slashing_db_att_for_att_data := 
                    SlashingDBAttestation(
                        source_epoch := attestation_data.source.epoch,
                        target_epoch := attestation_data.target.epoch,
                        signing_root := None
                    );
                while attns_to_check != {}
                invariant var checked := att_slashing_db - attns_to_check;
                        forall a | a in checked :: !is_slashable_attestation_pair(a, slashing_db_att_for_att_data)
                {
                        var past_attn :| past_attn in attns_to_check;
                        if is_slashable_attestation_pair(past_attn, slashing_db_att_for_att_data)
                        {
                            assert is_slashable_attestation_data(att_slashing_db, attestation_data);
                            return true;
                        }

                        attns_to_check := attns_to_check - {past_attn};
                }
                assert !is_slashable_attestation_data(att_slashing_db, attestation_data);
                return false;
            }

        }
        else
        {
            assert !is_slashable_attestation_data(att_slashing_db, attestation_data);
            return false;
        }
    } 

    predicate method consensus_is_valid_attestation_data(
        slashing_db: set<SlashingDBAttestation>,
        attestation_data: AttestationData, 
        attestation_duty: AttestationDuty
    )
    {
        && attestation_data.slot == attestation_duty.slot
        && attestation_data.index == attestation_duty.committee_index
        && !is_slashable_attestation_data(slashing_db, attestation_data)   
    }      
}