# Dafny Reference Implementation for Distributed Attestations

This folder contains the Dafny reference implementation section of the DVT protocol that is concerned with generating attestations.

## Description

The bulk of the implementation logic is contained in the `DVCNode` class.
An instance of this class refers to a DVC that handles the attestation creation logic of the DVT protocol for a single Distributed Validator public key.

The only public method of the `DVCNode` class is the `process_event` method.
This method must be executed on an instance `I` of `DVCNode` any time that a new event concerning attestation creation for the Distributed Validator public key handled by instance `I` occurs.
The implementation is not thread-safe, that is, for any instance of `DVCNode`, only one `process_event` method must be executing at any point in time.

`process_event` returns a value of type `Status` which indicates whether any error occurred in the processing of the event.
The formal verification analysis will prove that, as long as the components external to the `DVCNode` class (i.e. network, consensus, beacon node, remote signer and slashing db) behave as expected, no error can occur.
Therefore, if `process_event` indicates that an error occurred while processing the event, it means that one of the external components did not behave as expected.
Hence, recovery from error conditions is outside the scope of this reference implementation.

## Relevant features of the Dafny language

This section covers features of the Dafny language that are critical to the understanding of the reference implementation.

### General Features

- `trait`: A `trait` is an abstract superclass analogous to Java interfaces.
- `<var name> :| <boolean expression>`: Such-that assignment. The variable `<var name>` is assigned with any value that satisfies `<boolean expression>`. For example, `var a :| a > 6` assigns to the variable `a` any value such that `a > 6` is true, that is, any value strictly greater than 6.
- `ghost var <var_name>`: Variable used for verification purposes only.
- `{<statement>}`: There is not any special meaning associated with statements being enclosed between curly braces. This is just an artifice used to allow most of the formal verification work to be carried out in separate files. Essentially, curly braces create a sort of an "anchor" in the code that a separate file can use to indicate where to insert formal verification statements.
- `:- <method call>`: The behaviour of this statement is similar to how exceptions work in other languages. If the method being called returns `Status.Failure`, then Dafny does not execute the rest of the caller-method code and it propagates the failure by immediately returning `Status.Failure`.
- `requires <expression>`: This statement indicates that `<expression>` must be evaluated to `true` every time that a method is called. Except for the first `requires` statement in the `constructor`, the rest of the `requires` statement are for formal verification purposes only.

### Sets
<!-- I would like to mention `set x | P(x)` -->

- `set s | <boolean expression> :: <expression>`: This is the Dafny set comprehension expression. It corresponds to the set that includes all and only those values obtained by the evaluation of `<expression>` on the members of `s` that satisfy `<boolean expression>`.
For example, the expression `set s | 0 <= s <= 5 :: s*2` represents the set {0, 2, 4, 6, 8, 10}.
Note that `set x | <boolean expression>` is the short form of `set x | <boolean expression> :: x`.
Another way to define a set is by `var x := {1, 2}`.
`{}` represents an empty set.
- `|s|`: Cardinality or the number of elements in the set `s`.

### Maps

- `m[k]`: Access the element in the map `m` with key `k`.
- `m.[k := v]`: Map update. If `m` is a variable to type `map<T1,T2>`, then `m.[ k := v]` corresponds to the value held by the variable `m` with the exception that the value assigned to the key `k` is `v`. 
- `m.Keys`: If `m` is a variable to type `map<T1,T2>`, then `m.Keys` corresponds to the set of keys in the map held by the variable `m`.
- `m - set_of_keys_to_remove`: Map key removal. If `m` is a variable of type `map<T1,T2>` and `set_of_keys_to_remove` is of type `set<T1>`, then `m - set_of_keys_to_remove` corresponds to map `m` with the keys in `set_of_keys_to_remove` removed.
- `m.Keys`: If `m` is a variable to type `map<T1,T2>`, then `m.Keys` corresponds to the set of keys in the map held by the variable `m`.
- `|m|`: Cardinality or the number of keys in the map `m`.

### Sequences

- `s[i]`: Access the `i`-th element of the sequence `s`.
- `seq(n, f)`: Sequence comprehension expression. `n` is the number of elements in the resulting sequence. `f` needs to be of type `nat -> T`. The resulting sequence is a sequence of type `seq<T>` where `seq[i] == f(i)`.
- `|s|`: Cardinality or the number of elements in the sequence `s`.


### Tuples

- `(a, b)`: Tuple creation.
- `(a, b).<n>`: Access tuple `n`-th element. `(a, b).0` corresponds to `a`. `(a, b).1` corresponds to `b`.

### Datatypes

- `datatype`: Immutable structure. The keyword `datatype` in Dafny indicates an inductive datatype. However, for the purpose of this work, datatypes can be considered immutable field structures.
- 
    ```
    datatype <datatype name> = | <constructor 1>(<field 1>:<type1>, <field 2>: <type2>)
                               | <constructor 2>(<field 3>:<type3>)
    ```
    It defines `<datatype name>` as a datatype with the two constructors `<constructor 1>` and `<constructor 2>`.
- Assume the following definition  
    ```
    datatype D = | C1(a: nat, b: real)
                 | C2(c: int, d: bool)
    ```
- `C2(c := -5, d := true)`: Datatype construction. It evaluates to a value of type `D` built using `C2` where the value `-5` is assigned to the field `c` and value `true` is assigned to the field `d`.
- `C2(c := -5, b := true).<field name>`: Datatype field value access. `C2(c := -5, b := true).c` evaluates to the value of field `c` which is `-5` in this case. Similarly, `C2(c := -5, d := true).b` evaluates to the value of field `d` which is `true` in this case.
- 
    ```
    match d
    {
        case C1(a,b) => <statement 1>
        case C2(c,d) => <statement 2>
    }
    ```
    If `d` was constructed with constructor `C1`, then it executes `<statement 1>` with `a` set to `d.a` and `b` set to `d.b`. While, if `d` was constructed with constructor `C2`, then it executes `<statement 2>` with `c` set to `d.c` and `d` set to `d.d`. 

### Functions

- `function method <function name>(<par1>:<type 1>, <par 2>:<type 2>): <type 3>`: Function declaration. It declares a function named `<function name>` that takes two arguments of type `<type 1>` and `<type 2>` respectively and it returns a value of type `<type 3>`.
- The value returned by a function corresponds to the value obtained by evaluation the expression in its body.
For example,
    ``` 
    fuction foo(a:nat): nat
    {
        a * 2
    }
    ```
    returns the double of the value passed as a parameter 


## Less relevant features of the Dafny language

This section covers features of the Dafny language that are NOT critical to the understanding of the reference implementation.

- `modifies <locs>`: This statement indicates the set of memory locations that a method may modify. This statement is needed for formal verification purposes only.
- `reads *`: This statment indicates that a function can access any memory location. This statement is needed for formal verification purposes only.
- `ensures <expression>`: This statement indicates that `<expression>` must be evaluated to `true` every time that a method exists. It is only for formal verification purposes.

## TODOs

- Add documentation to the code.
- Add missing Dafny concepts.
