WORK IN PROGRESS (while we iron out who says what!)

- Vertices
- Edges
- Path
- Backdoor Path
- Confounding / Deconfounding
- Markovian Model / semi-Markovian model / causal Bayesian network
- Parents(V)

## Tian & Pearl, 2004

> The most common such representation involves a Markovian model (also known as a causal Bayesian network). A Markovian model consists of a DAG G over a set V = {V1, ..., Vn } of variables, called a *causal graph*.

- Tian & Pearl, 2004, p. 562

> The probabilistic interpretation views *G* as representing conditional independence assertions: Each variable is independent of all its non-descendants given its direct parents in the graph. These assertions imply that the joint probability function *P(v) = P(v_1, ..., v_n)* factorizes according to the product *P(v) = Π_{i} P(V_i | pa_i)* where *pa_i* are (values of) the parents of variable *V_i* in the graph.

- Tian & Pearl, 2004, p. 562

*pa_i* is **exclusive**.

> Let *V* and *U* stand for the sets of observed and unobserved variables, respectively. In this paper, we assume that no *U* variable is a descendant of any *V* variable (called a semi-Markovian model). Then the observed probability distribution, *P(v)*, becomes a mixture of products: *P(v) = Σ_{u} Π_{i} P(v_{i} | pa_i, u^i) P(u)* where *Pa_i* and *U^i* stand for the sets of the observed and unobserved parents of *V_i*, and the summation ranges over all the *U* variables.

- Tian & Pearl, 2004, p. 562

## Santu Tikku, 2018

> For a directed graph G = (V, E) and a set of vertices W ⊆ V the sets Pa(W)_G , Ch(W)_G, An(W)_G and De(W)_G denote a set that
contains W in addition to its parents, children, ancestors and descendants in G, respectively.
- Santtu Tikku, Improving Identification Algorithms in Causal Inference, 2018, p. 8

Inclusive with given set.

> Contrary to usual graph theoretic conventions, we call a vertex without any descendants a root (typically referred to as sink). The root set of G is the set of all roots of G, which is {X ∈ V | De(X)G \ {X} = ∅}. The reason for this reversal of the names of sinks and roots is to retain consistency  with relevant literature (e.g. Shpitser and Pearl, 2006b) and other
important definitions.
 
- Santtu Tikku, Improving Identification Algorithms in Causal Inference, 2018, p. 8

> When a DAG is considered, we can relate an ordering of its vertices to its topological structure. This is useful especially when a causal interpretation is associated with the graph. A topological ordering π of a DAG G = (V, E) is an ordering of its vertices, such that if X is an ancestor of Y in G then X < Y in π. The subset of vertices that are less than V_j in π is denoted by V_π^{j-1}. 

- Santtu Tikku, Improving Identification Algorithms in Causal Inference, 2018, p. 8

> An algorithm by Kahn (1962) can be used to derive a topological ordering for any DAG.  First, we add the vertices without ancestors to the ordering in any order. At the next stage, we add all vertices such that their parents are already contained in the ordering. This is repeated until every vertex has been included. It should be noted that a DAG may have more than one ordering. 

- Santtu Tikku, Improving Identification Algorithms in Causal Inference, 2018, p. 8

- Backdoor Paths
- Definitions
- Sorting for ordering
