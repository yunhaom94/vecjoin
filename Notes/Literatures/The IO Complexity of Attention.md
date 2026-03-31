The I/O Complexity of Attention, or
How Optimal is Flash Attention?

Barna Saha∗

Christopher Ye∗

February 13, 2024

Abstract

Self-attention is at the heart of the popular Transformer architecture, yet suffers from
quadratic time and memory complexity. In a recent significant development, FlashAttention
shows that the I/O complexity of attention is the true bottleneck in scaling Transformers.
Given two levels of memory hierarchy, a fast cache (e.g. GPU on-chip SRAM) where computa-
tion happens and a slow memory (e.g. GPU high-bandwidth memory) where the data resides,
the I/O complexity measures the number of accesses to the slow memory. FlashAttention is
an I/O-aware algorithm for self-attention that requires N 2d2
M I/O operations where N is the
dimension of the attention matrix, d is the head-dimension and M is the size of cache. However,
is this I/O complexity optimal? The known lower bound only rules out an I/O complexity of
o(N d) when M = Θ(N d), since the output of the attention mechanism that needs to be written
in the slow memory is Ω(N d). The main question that remained open after FlashAttention is
whether this I/O complexity is optimal for any value of M.

We resolve the above question in its full generality by showing an I/O complexity lower
bound that matches the upper bound provided by FlashAttention for any values of M ≥ d2
within any constant factors. Further, we give a better algorithm with lower I/O complexity
for M < d2, and show that it is optimal as well. Moreover, our lower bounds do not rely on
using combinatorial matrix multiplication for computing the attention matrix. We show even
if one uses fast matrix multiplication, the above I/O complexity bounds cannot be improved.
We do so by introducing a new communication complexity protocol for matrix compression,
and connecting communication complexity to I/O complexity. To the best of our knowledge,
this is the first work to establish a connection between communication complexity and I/O
complexity, and we believe this connection could be of independent interest and will find many
more applications in proving I/O complexity lower bounds in future.

4
2
0
2

b
e
F
2
1

]

G
L
.
s
c
[

1
v
3
4
4
7
0
.
2
0
4
2
:
v
i
X
r
a

∗University of California, San Diego. The authors are partially supported by NSF grants 1652303, 1909046,

2112533, and HDR TRIPODS Phase II grant 2217058.

1

1

Introduction

Transformer models [VSP+17] have emerged as the architecture of choice for a variety of applications
including natural language processing and computer vision. The self-attention module at the heart
of the Transformer architecture requires quadratic time and memory complexity. Thus despite its
In a seminal paper, [DFE+22] proposes
popularity, Transformers are slow and memory-hungry.
FlashAttention, an IO-aware algorithm for self-attention. Given two levels of memory hierarchy,
a fast cache (e.g. GPU on-chip SRAM) where computation happens and a slow memory (e.g.
GPU high-bandwidth memory) where the data resides, the I/O complexity measures the number of
accesses to the slow memory. [DFE+22] argues that I/O complexity is indeed the true bottleneck in
achieving wall-clock speed up, and provide an algorithm that achieves an I/O complexity of O( N 2d2
M )
where N is the dimension of the attention matrix, d is the head-dimension and M is the cache size.
In self-attention, three input matrices Q, K, V ∈ RN ×d are used to compute softmax(QKT )V where
A = exp(QKT ) is the attention matrix. For M = Θ(N d), the above I/O complexity bound becomes
N d which is also needed just to write the output of self-attention to slow memory. This leaves a
tantalizing open question whether FlashAttention I/O complexity is optimal for any values of M .
We resolve this question in affirmative for any value of M as long as M ≥ d2. Moreover, for
M < d2, we give a better algorithm than FlashAttention and also show the bound is optimal.
Indeed as we prove for M ≤ d2, the I/O complexity of self-attention is at least as high as the I/O
complexity of computing matrix multiplication of two N × d and d × N matrices. For M ≥ d2 which
is also the more practical regime, our proof of optimality of FlashAttention brings in several new
ideas.

First, we show that FlashAttention which uses combinatorial matrix multiplication has optimal
I/O complexity by utilizing the famous red-blue pebble game from the early eighties [HK81]. However,
it may still be possible to improve FlashAttention by utilizing fast matrix multiplication [GU18,
WXXZ23] to obtain lower I/O complexity. We rule out any such possibilities. We prove a general
lower bound against all such algorithms. We introduce a new matrix compression problem, and
show that it has a high communication complexity. Next, we establish a connection between the
communication complexity of a matrix compression protocol with the I/O complexity of attention.
To the best of our knowledge, this is the first work that shows a connection between communication
complexity and I/O complexity, which may have further valuable theoretical consequences. We
show even when the input matrix entries are restricted to binary, the lower bound holds within
polylogarithmic factors by utilizing Binary BCH codes [Hoc59, BR60] from coding theory to prove
lower bounds against binary matrix compression.

1.1 Related Work

Many papers have studied attention, a key bottleneck of the transformer architecture [VSP+17]
which has become the predominant architecture in applications such as natural language pro-
cessing. Many approximate notions have been studied to reduce its compute and memory con-
straints [BMR+20, KVPF20, KKL20, ZGD+20, CDW+21, CLD+21, AS23, HJK+23]. Algorithms
such as FlashAttention have made significant practical gains by designing I/O-aware algorithms
[DFE+22, Dao23].

The role of learning under bounded space constraints has been studied primarily in the context
of bounded memory, with applications including Online Learning [SWXZ22, PR23, PZ23], continual
learning [CPP22], convex optimization [WS19, MSSV22, CP23], and others [Raz19, SSV19, GLM20].
In this work, we instead consider learning in the context of a two-level memory hierarchy with a
bounded cache. While the algorithm has unlimited memory, it can only access a small portion of

2

this memory at any given time, and is charged for every access to memory. We believe that the
task of minimizing I/O complexity is both theoretically interesting and practically significant, as
I/O operations often form a key computational bottleneck in practice.

There is a long-line of work on I/O complexity [HK81, AV88, PS14a]. Within this body of work,
many papers have focused on the problem of matrix multiplication [BDHS12, BDH+12, PS14b,
SHS15, BS17].

1.2 Our Contributions

We study the I/O complexity of attention on a two-level memory hierarchy. The attention mech-
anism takes inputs Q, K, V ∈ RN ×d and computes softmax(QKT )V (see Section 2.1) where A =
exp(QKT ) is the attention matrix. Our first result resolves the I/O complexity of any algorithm
computing attention using the standard matrix multiplication algorithm. This answers an open
question of [DFE+22] and shows that FlashAttention is optimal among this class of algorithms.

Theorem 3.1. The I/O complexity of attention with standard matrix multiplication is

(cid:18)

Θ

min

(cid:18) N 2d
√
M

,

N 2d2
M

(cid:19)(cid:19)

We divide the analysis into two cases, the large cache (M ≥ d2) and small cache (M < d2) case.
When M < d2, we show that attention and matrix multiplication are equivalent. In the small cache
setting, N 2d2
> N 2, so we can explicitly write QKT to memory while computing atten-
tion. Thus, any algorithm computing attention in fact computes QKT , establishing an equivalence
between attention and matrix multiplication.

M > N 2d√

M

In the more interesting large cache case, when M ≥ d2, the upper bound is given by the
breakthrough FlashAttention algorithm [DFE+22]. In this setting, the I/O complexity approaches
O(N d) as cache size increases, providing significant practical improvements, despite the theoretical
time complexity remaining O(N 2d). To prove a matching lower bound, we use the red-blue pebble
game of [HK81]. Executing an algorithm A on a machine with cache size M is equivalent to
playing the red-blue pebble game on the computational directed acyclic graph G corresponding
to A. Specifically, the partitioning lemma (Lemma 2.7) states that any successful execution of A
corresponds to a partition of G where each part corresponds to a sub-computation of A with no
I/O operations (called a M -partition). Thus, it suffices to prove a lower bound on the size of any
M -partition to obtain a I/O complexity lower bound for A on a machine with cache size M . Our
lower bound on the partition size then follows from a careful analysis of the computational graph
of attention (Figure 1). Specifically, we show that any part Vi in the partition can only compute
M 2
d2 + M ≤ 2M 2

entries in the product QKT .

We then extend our lower bound in the large cache (M ≥ d2) case to arbitrary algorithms for
I/O

attention. More precisely, we show that even with fast matrix multiplication (FMM), Ω
operations are required to compute attention.

(cid:16) N 2d2
M

(cid:17)

d2

where q > N . The I/O complexity of attention (with any

Theorem 4.8. Suppose Q, K ∈ FN ×d
(cid:16)

q

(cid:16) N 2d2

matrix multiplication algorithm) is Ω

M , N 2(cid:17)(cid:17)
To establish a general lower bound, we can no longer reason about a specific computational
graph. Instead, we appeal to communication complexity, a useful tool for proving lower bounds
for learning [DKS19, KLMY19], specifically space-bounded learning [CPP22]. To the best of our
knowledge, this is the first application of communication complexity to I/O complexity lower bounds.

min

.

3

For simplicity, assume that A performs I/O operations in batches of size M (Lemma 4.1 shows
that this can be assumed without loss of generality). Within each batch, A can only access the
cache of size M , with no further I/O operations. In order to give a lower bound on the number of
batches, we argue that A cannot make too much progress in each batch. In the context of attention,
we measure progress as the number of entries computed in QKT (regardless of whether these entries
are written to memory).

Formally, we introduce the B-entry matrix compression problem (Definition 4.2) and argue
that any algorithm making too much progress on a given batch gives an efficient communication
protocol (Theorem 4.4). We then complete the argument by giving a lower bound on the communi-
cation complexity of the matrix compression problem (Lemma 4.6). Our lower bound follows from
constructing input matrices satisfying strong linear independence constraints. For large q, this is
achieved by Vandermonde matrices.

Finally, we relax the constraint q > N and consider the special case q = 2, i.e. Q, K, V are
binary matrices and obtain a lower bound tight up to polylogarithmic factors. Our lower bound
uses Binary BCH codes [Hoc59, BR60] to construct matrices satisfying strong linear independence
constraints.

Theorem 4.14. Suppose Q, K ∈ {0, 1}N ×d. The I/O complexity of attention (with any matrix
, N 2(cid:17)(cid:17)
multiplication algorithm) is Ω

min

(cid:16)

.

(cid:16) N 2d2
M log2 N

In the small cache setting (M < d2), Theorem 4.17 gives a simple equivalence between attention

and rectangular matrix multiplication.

2 Preliminaries

Given a matrix A ∈ Rn×m, we index an individual entry as A[i, j]. The i-th row is denoted A[i] while
the j-th column is denoted A[∗, j]. A[i1 : i2, j1 : j2] denotes a block of A consisting of entries (i, j)
where i ∈ [i1, i2] and j ∈ [j1, j2]. Given a block size B, the block A[(i−1)·B +1 : i·B, (j −1)·B +1 :
j · B] is denoted A(B)[i, j].

AT , A−1 denote the transpose and inverse of A.
For a vector v ∈ Rn, we similarly denote entries v[i], a contiguous block of entries as v[i1 : i2],
and the i-th block of size B as v(B)[i]. Let diag(v) denote the matrix D ∈ Rn×n with D[i, i] = v[i].

2.1 The Attention Mechanism

Given input matrices Q, K, V ∈ RN ×d, the attention mechanism computes D−1AV where the
attention matrix A = exp(QKT ) is computed by taking exponents entry-wise and D = diag(A · 1)
is the diagonal matrix containing row-sums of A.

2.2 The Memory Hierarchy

In this work, we assume that the memory hierarchy has two levels: the small but fast layer (called
the cache) and the large slow layer (called the memory). We assume that the memory is unbounded
while the cache is bounded by some size constraint M . Furthermore, computations only occur on
the cache.

4

2.3 Red-Blue Pebble Game

We require the red-blue pebble game of [HK81], designed to model computations on a two-level
memory hierarchy. Inspired by the pebble game often used to model space-bounded computation,
[HK81] develops the red-blue pebble game to model I/O complexity. As with the standard peb-
ble game, the red-blue pebble game is played on a directed acyclic graph, where nodes represent
computations and edges represent dependencies. Throughout the game, pebbles can be added to,
removed from, or recolored between red and blue in the graph, where red pebbles represent data in
cache and blue pebbles represent data in slow memory. Given an upper bound on the number of
red pebbles (cache size), the goal is to minimize the number of pebble recolorings (I/O operations)
over the course of a computation. The game is defined formally below.

Definition 2.1 (Red-Blue Pebble Game [HK81]). Let G be a directed acyclic graph with a set of
input vertices containing at least all vertices with no parents, and a set of output vertices containing
at least all vertices with no children. A configuration is a pair of subsets of vertices, one containing
all vertices with red pebbles, and the other containing all vertices with blue pebbles. Note that a
vertex can have a red pebble, a blue pebble, both, or neither.

The initial (resp. terminal) configuration is one in which only input (resp. output) vertices
contain pebbles, and all of these pebbles are blue. The rules of the red-blue pebble game are as
follows:

R1 (Input) A red pebble may be placed on any vertex with a blue pebble.
R2 (Output) A blue pebble may be placed on any vertex with a red pebble.
R3 (Compute) A red pebble may be placed on a vertex if all its parents have red pebbles.
R4 (Delete) A pebble may be removed from any vertex.

A transition is an ordered pair of configurations where the second can be obtained from the first
following one of the above rules. A calculation is a sequence of configurations, where each suc-
cessive pair forms a transition. A complete calculation is a calculation that begins with the initial
configuration and ends with the terminal configuration.

In typical instances, including our paper, the input and output vertices are disjoint. Furthermore,
the input vertices are typically exactly those with no parents, while the output vertices are exactly
those with no children. To model a bounded cache, we assume that there are at most M red pebbles
on the graph at any given time, while any number of blue pebbles can be placed on the graph. Given
a graph G, we are interested in the I/O complexity.

Definition 2.2 (I/O Complexity [HK81]). Given a graph G and integer M , the I/O complexity
Q(G, M ) is defined by the minimum number of transitions according to rules R1 and R2 required
by any complete calculation. When the underlying graph G is clear, we omit G and write Q(M ).

To obtain I/O complexity lower bounds, [HK81] show that any complete calculation induces a
M -partition. Roughly speaking, a M -partition partitions the vertex set such that each part can be
computed completely using only 2M I/O operations. A lower bound on the size of any M -partition
then implies a lower bound on the I/O complexity of the computational graph.

Before defining the M -partition, we give the necessary definitions of dominator sets, minimum

sets, and vertex subset dependence.

Definition 2.3 (Dominator Set). Let G be a directed acylic graph and S ⊂ V a subset. D ⊂ V is
a dominator set of S if for every path from an input vertex of G to a vertex in S contains a vertex
in D.

5

Definition 2.4 (Minimum Set). Let G be a directed acylic graph and S ⊂ V a subset. The minimum
set of S, denoted M , is the subset of vertices in S with no children in S.

Definition 2.5 (Vertex Subset Dependence). Let G be a directed acyclic graph, with S, T ⊂ V
disjoint subsets. T depends on S if there exists an edge (s, t) ∈ E with s ∈ S, t ∈ T .

We now give the definition of an M -partition (called an S-partition in [HK81]).

Definition 2.6 (M -partition [HK81]). Let G be a directed acyclic graph. A family of subset {Vi}h
is a M -partition of G if the following properties hold:
P1 (Partition) The sets Vi are disjoint and V = (cid:83)h
P2 (Dominator) For each Vi, there exists a dominator set Di of size at most M .
P3 (Minimum) For each Vi, the set of minimum vertices Mi has size at most M .
P4 (Acyclic) There is no cyclic dependence among vertex sets {Vi}h

i=1 Vi.

i=1.

i=1

Roughly speaking, a M -partition partitions the vertex set such that each part can be computed
In particular, every node in a single part V ′ can be
completely using only 2M I/O operations.
reached by placing red pebbles at the dominator vertices and using Rule R3. This can be thought
of as the initial state of the cache at some point, and without any further reads from memory, every
node on V ′ can be computed. Then, after the computation, the values at the minimum vertices
can be written to memory. This corresponds to at most M write operations. The following lemma
relates I/O complexity to the size of M -partitions.

Lemma 2.7 (Theorem 3.1 of [HK81]). Let G be a directed acyclic graph. Any complete calculation
of the red-blue pebble game on G, using at most M red pebbles, is associated with a 2M -partition of
G such that,

M · h ≥ Q(G, M ) ≥ M · (h − 1)

where h is the number of vertex subsets in the 2M -partition.

In particular, the partitioning lemma of [HK81] shows that it suffices to prove a lower bound on

the size of any 2M -partition to obtain a lower bound on the I/O complexity.

Lemma 2.8 (Lemma 3.1 of [HK81]). For any directed acyclic graph G, let P (G, M ) denote the
minimum size of any M -partition of G. Then,

Q(G, M ) ≥ M · (P (G, 2M ) − 1)

2.4 Computational Graph for the Attention Mechanism

Figure 1 gives a computational graph modelling the attention mechanism [DFE+22, Dao23]. In this
computational graph, we assume that matrix products are computed using the standard algorithm,
that is, we compute (AB)ij = (cid:80)

k AikBkj for all i, j.

The attention mechanism begins by computing the matrix product QKT . In the vertex set L1,
ℓj}i,j,ℓ. Then, each entry (QKT )ij is computed
there are N 2d vertices representing the values {QiℓKT
by summing the appropriate vertices in L1, i.e. the node (QKT )ij = (cid:80)
ℓ QiℓKT
ℓj. In particular, each
entry (QKT )ij is connected to L1 via a summation tree. Note that all nodes in the summation
trees are disjoint. The summation tree can be thought of as a balanced binary tree with d leaves,
although the exact structure of the tree (i.e. order of summation) can be arbitrary. For a more
detailed description of the computational graph of the standard matrix multiplication algorithm,
see [HK81]. We define the set of level-1 vertices to be all nodes in the computational graph that

6

Figure 1: Computational Graph for the Attention Mechanism.

are in vertex sets L1, QKT , or one of the intermediate nodes in the N 2 summation trees between
the two layers. Figure 2 illustrates an example summation tree.

Then, each entry in A is computed by taking the exponent of the corresponding entry in QKT .
Each node in D is computed by summing over the rows of A. As above, this is realized in the graph
by N disjoint summation trees and D−1 is computed by taking the multiplicative inverse of each
element in D. The matrix product is computed as in the first step, first by storing all N 2d products
in the intermediate layer L2 = {AikVkj}i,k,j and computing AV via N d disjoint summation trees.
Finally, each node in O is computed by scaling each entry of AV by the appropriate factor in D−1.
Although we have (roughly) described the computational graph of FlashAttention-2 [Dao23]
and there are different ways to implement attention, all algorithms begin by computing the product
QKT , and our lower bounds will hold for any algorithm computing this matrix product.

3

I/O Complexity of Attention

In this section, we present a tight characterization of the I/O complexity of any algorithm computing
attention exactly using the standard matrix multiplication algorithm.

Theorem 3.1. The I/O complexity of attention with standard matrix multiplication is

(cid:18)

Θ

min

(cid:18) N 2d
√
M

,

N 2d2
M

(cid:19)(cid:19)

At the crossover point M = d2, observe N 2d√
M = N 2. We define M ≥ d2 as the large
M
cache regime, and M < d2 as the small cache regime. We are primarily interested in the large cache

= N 2d2

7

𝑸𝑳𝟏𝑲𝑸𝑲𝑻𝑨𝑫𝑫#𝟏𝑽𝑳𝟐𝑨𝑽𝑶Figure 2: A single summation tree with d = 4. Orange vertices denote inputs from Q. Yellow
vertices denote inputs from K. Grey and green vertices denote level-1 vertices. Observe that these
are disjoint for each summation tree. The green vertex specifically denotes an entry in QKT . Solid
edges denote multiplications and dotted edges denote additions. Vertices in the blue box denote
vertices in L1.

regime, since this is where I/O complexity is sub-quadratic. This is the regime where FlashAttention
outperforms standard implementations of attention, since we can avoid writing the entire N × N
matrix QKT to memory.

3.1 Large Cache: M = Ω(d2)

For large M = Ω(d2), we show that the following result of [DFE+22] is optimal in terms of I/O
complexity.

Theorem 3.2 (Theorem 2 of [DFE+22]). FlashAttention has I/O complexity O

(cid:16) N 2d2
M

(cid:17)

.

To prove a matching lower bound, we bound the number of level-1 vertices in each part of a
M -partition. This gives a lower bound on the size of any partition, implying an I/O complexity
lower bound via Lemma 2.8.

Lemma 3.3. Suppose M = Ω(d2) and let P be a M -partition of the computational graph in Figure
(cid:17)
1. Let V ′ ∈ P. Then, V ′ contains at most O

level-1 vertices.

(cid:16) M 2
d

Proof. First, since V ′ has a dominator set D′ of at most M , and each summation tree in the
computational graph is disjoint, there are at most M level-1 summation trees containing a dominator
vertex. Next, since V ′ has at most M minimum vertices, disjointness again implies that at most M
level-1 summation trees contain a minimum vertex. See Figure 3 for an example of V ′ containing
dominator and minimum vertices.

Suppose V ′ contains level-1 vertices not in any of the above 2M summation trees (at most M

trees containing a dominator and another at most M containing minimum vertices).

Consider a tree T containing level-1 vertices that does not intersect D′ or contain a minimum
vertex. We denote such a tree as extra. Since T does not contain any minimum vertices, the root
r of T , representing some entry (QKT )[i, j], must be in V ′. There are 2d input vertices with paths
ℓ=1. We denote the i-inputs of T as the set {Q[i, ℓ]}d
to r, namely the inputs {Q[i, ℓ], KT [ℓ, j]}d
ℓ=1
and the j-inputs as the set {KT [ℓ, j]}d
ℓ=1. On each path, all vertices but the inputs are in T . Since
T contains no vertices in D′, D′ must contain all 2d input vertices. For example, in Figure 2, V ′

8

𝐿!𝑄!"𝑄!#𝑄!$𝑄!%𝐾&"𝐾&#𝐾&$𝐾&%𝑄!"𝐾#"𝑄!$𝐾#$𝑄!%𝐾#%𝑄!&𝐾#&𝑄𝐾!"#	(a) {Qi2, Kj2, Qi1Kj1} are dominator vertices,

{M } is the minimum vertex.

(b) {Qi1Kj1, Qi2Kj2} are dominator vertices,
ij} is the minimum vertex.

{QK T

Figure 3: Two examples of summation trees containing dominator and minimum vertices. Blue
vertices denote elements of the partition Vi.

contains (QKT )[i, j] and none of the grey vertices, and therefore must contain all 2d = 8 input
vertices (orange and yellow).

For two extra trees Tij, Ti′j′ whose roots correspond to entries (QKT )[i, j], (QKT )[i′, j′] respec-
tively, observe that the i-inputs are equal if i = i′ and disjoint otherwise. Similarly, the j-inputs
are equal if j = j′ and disjoint otherwise. Suppose V ′ contains level-1 vertices in C extra level-1
summation trees. The C roots of these trees correspond to C entries in the matrix QKT . Suppose
the C entries have I distinct values in the row index. Choose one entry in C for each row index.
Each entry requires d i-input vertices to be placed in the dominator set, and furthermore these
input vertices are disjoint. Therefore, there are at least Id input vertices from Q in the dominator
set D′. By a similar argument, if the C entries have J distinct values in the column index, there
are at least Jd input vertices from K in the dominator set D′. In particular, if there are C extra
trees, then there are at least (I + J)d input vertices in the dominator set D′. Finally, we can bound
C by observing that I + J ≥ max(I, J) ≥

C since IJ ≥ C. In particular,

√

√

Cd ≤ (I + J)d ≤ |D′| ≤ M

so that C ≤ M 2
d2 .

In total, V ′ contains vertices in at most C + 2M level-1 trees. Each level-1 tree contains O(d)

level-1 vertices so that V ′ contains at most,

O

(cid:18) M 2
d

(cid:19)

+ M d

= O

(cid:19)

(cid:18) M 2
d

level-1 vertices, where we have used M = Ω(d2).

Using Lemma 2.8, we obtain a lower bound for computing attention using standard matrix
multiplication. In fact, since we have not used any other part of the computational graph, our lower
bound holds for any algorithm computing QKT using standard matrix multiplication.
(cid:17)

(cid:17)

Lemma 3.4. Suppose M = Ω(d2). Then, P (M ) = Ω

and Q(M ) = Ω

(cid:16) N 2d2
M

.

(cid:16) N 2d2
M 2

Proof. Note that there are Ω(N 2d) level-1 vertices. Since each part in the M -partition contains at
level-1 vertices, the lower bound on the number of parts in the M -partition follows
most O
immediately from Lemma 3.3.

(cid:16) M 2
d

(cid:17)

9

(%&(%'(%((%))*&)*')*()*)!!""#"!!$"#$!!%"#%!!&"#&*!"!"#	𝑄!"𝑄!#𝑄!$𝑄!%𝐾&"𝐾&#𝐾&$𝐾&%𝑄!"𝐾#"𝑄!$𝐾#$𝑄!%𝐾#%𝑄!&𝐾#&𝑄𝐾!"#	3.2 Small Cache: M = o(d2)

When M = o(d2), we show that attention is equivalent to matrix multiplication, establishing a
Θ
bound on the I/O complexity. We first show that there is an algorithm with I/O complexity

(cid:17)

(cid:16) N 2d√
(cid:16) N 2d√

M

M

(cid:17)

.

O

Theorem 3.5. There is an algorithm computing attention with I/O complexity O
more, this algorithm uses O (cid:0)N 2d(cid:1) time and O (cid:0)N d + N 2(cid:1) space.

(cid:17)

(cid:16) N 2d√

M

. Further-

√

M ×

× d√
M

blocks of size

High Level Overview Our algorithm follows standard techniques for reducing the I/O complex-
ity of matrix multiplication. In Phase 1, we compute A = exp(QKT ) and D = diag(A · 1). First, we
√
divide Q, K into N√
M
M
size block at a time. In Lines 3 and 5, we iterate over blocks of QKT . In Lines 7 and 9, we compute
each block of QKT by summing over
block matrix products. After computing QKT , we apply
exponents entry-wise and sum over rows in Lines 11 and 12 to compute the relevant blocks of A, D.
In Phase 2, we compute the matrix product D−1AV , storing the output in matrix O. We
× N√
M
M . Lines 16 and 18 iterates over blocks of O. Lines 20 and 22 compute a
matrix products and scaling by the approprite block

imagine D−1 as a vector and partition into N√
M
√

M and partition A into N√
M

M and proceed to compute QKT one

blocks of size
√

blocks of size

d√
M

M ×

M ×

√

√

√

√

√

M ×

M block of O by summing over N√
M
of D−1. This completes the overview of the algorithm.

10

Algorithm 1 SquareTilingAttention(Q, K, V, M )
Input : Matrices Q, K, V ∈ RN ×d, Cache size M
Output: D−1AV where A = exp(QKT ) and D = diag(A · 1)

(cid:107)

1 B ←

(cid:106)(cid:112)M/4
2 Phase 1: Compute D, A
3 for 1 ≤ i ≤ ⌈N/B⌉ do

4

5

6

7

8

9

10

11

12

Initialize d(B)[i] ← 0B in cache
for 1 ≤ j ≤ ⌈N/B⌉ do

Initialize AB[i, j] ← 0B×B in cache
for 1 ≤ ℓ ≤ ⌈d/B⌉ do

Read Q(B)[i, ℓ] and (KT )(B)[ℓ, j] into cache
Compute AB[i, j] ← AB[i, j] + Q(B)[i, ℓ](KT )(B)[ℓ, j] in cache
Delete Q(B)[i, ℓ] and (KT )(B)[ℓ, j] from cache

Compute AB[i, j] ← exp(AB[i, j]) and write AB[i, j] into memory
Compute d(B)[i] ← d(B)[i] + AB[i, j] · 1 in cache
Delete AB[i, j] from cache

13
14 Write d(B)[i] to memory and delete d(B)[i] from cache
15 Phase 2: Compute D−1AV
16 for 1 ≤ i ≤ ⌈N/B⌉ do

17

18

19

20

21

22

23

24

25

Read d(B)[i] into cache
for 1 ≤ j ≤ ⌈d/B⌉ do

Initialize O(B)[i, j] ← 0B×B in cache
for 1 ≤ k ≤ ⌈N/B⌉ do

Read A(B)[i, k] and V (B)[k, j] into cache
Compute O(B)[i, j] ← O(B)[i, j] + diag (cid:0)d(B)[i](cid:1)−1
Delete A(B)[i, k] and V (B)[k, j] from cache

A(B)[i, k]V (B)[k, j]

Write O(B)[i, j] to cache and delete O(B)[i, j] from cache

Delete d(B)[i] from cache

Correctness of Algorithm 1. We begin with Phase 1, showing that each block A(B)[i, j] is computed
correctly. Fix a block A(B)[i, j]. For any indices i′ ∈ [(i − 1)B + 1, iB] and j′ ∈ [(j − 1)B + 1, jB],

A[i′, j′] =

d
(cid:88)

ℓ′=1

Q[i, ℓ′]KT [ℓ′, j] =

⌈d/B⌉
(cid:88)

ℓB
(cid:88)

ℓ=1

ℓ′=(ℓ−1)B+1

Q[i, ℓ′]KT [ℓ′, j]

In Line 9, we iterate over i′, j′, ℓ′, adding Q[i′, ℓ′]KT [ℓ′, j′] to A[i′, j′]. After iterating over 1 ≤
ℓ ≤ ⌈d/B⌉, A(B)[i, j] is computed so that after applying exp entry-wise, we write the correct block
A(B)[i, j] into memory. Next, since d should contain row-sums,

d[i′] =

N
(cid:88)

j′=1

⌈N/B⌉
(cid:88)

jB
(cid:88)

A[i′, j′] =

A[i′, j′]

j=1

j′=(j−1)B+1

we correctly write d(B)[i] into memory. Throughout Phase 1, the number of items in cache is
3B2 + B ≤ 4B2 ≤ M .

11

Now, we proceed to Phase 2. Let D = diag(d) = diag(A · 1). Similarly, for i′ ∈ [(i − 1)B +

1, iB], j′ ∈ [(j − 1)B + 1, jB]

O[i′, j′] =

1
D[i′, i′]

N
(cid:88)

k′=1

A[i′, k′]V [k′, j′] =

⌈N/B⌉
(cid:88)

kB
(cid:88)

k=1

k′=(k−1)B+1

A[i′, k′]V [k′, j′]
D[i′, i′]

which is computed by the loop in Phase 2. In particular, Line 22 adds the appropriate value for each
block k. The overall size of cache required is B + 3B2 ≤ 4B2 ≤ M . Thus, Algorithm 1 correctly
computes O = D−1AV with cache size M .

I/O Complexity of Algorithm 1. In Phase 1, for each iteration through i, j, ℓ, the algorithm reads
O(B2) values from memory into cache. This dominates the I/O complexity of the algorithm. The
(cid:16) N 2d
B3 B2(cid:17)
I/O complexity of Phase 1 is therefore O

(cid:16) N 2d
B

(cid:16) N 2d√

= O

= O

(cid:17)

(cid:17)

.

M

Similarly for Phase 2, the I/O complexity is dominated by the reading A, V into the cache and

this has I/O complexity O

, thus bounding the overall I/O complexity.

(cid:16) N 2d√

(cid:17)

M

Time and Space Complexity of Algorithm 1. Since we use standard matrix multiplication, the over-
all time complexity is O(N 2d). The space required is O(N d + N 2) as the algorithm stores matrices
Q, K, V, M and the vector d.

We now show that this is tight for M ≤ d2. We proceed by a reduction to the I/O complexity

of matrix multiplication, invoking the following result.

Lemma 3.6 (Corollary 6.2 of [HK81]). Let A ∈ Rm×k and B ∈ Rk×n. The standard algorithm for
.
matrix multiplication satisfies Q(M ) = Ω

(cid:16) mkn√

(cid:17)

M

Theorem 3.7. Suppose M = o(d2). Then, the I/O complexity of attention using standard matrix
multiplication is at least Ω

(cid:16) N 2d√

(cid:17)

M

Proof. The lower bound follows from a reduction to matrix multiplication. We take advantage of
the fact that if M ≤ d2, N 2d√
≥ N 2, so the algorithm can afford to write the attention matrix
M
A explicitly to memory. Given an algorithm A for attention, we have the following algorithm for
matrix multiplication. Given inputs Q, K, we execute A with one modification: whenever an entry
of QKT is computed for the first time, write this entry to memory. Over the course of the algorithm,
this computes QKT and adds at most N 2 additional I/Os, which any attention algorithm must use
whenever M < d2. We give the reduction in terms of the computational graph below.

M

(cid:17)

Suppose for contradiction there is an algorithm A computing attention with I/O complexity
(cid:16) N 2d√
. Consider A as a complete calculation on the computational graph described in Figure 1.
o
Since A is a complete calculation and the set of input and output vertices are disjoint, every single
vertex in the graph must have a pebble on it at some configuration in the calculation. Consider
then the algorithm B which executes A with the following modifications:

1. Whenever a blue pebble is deleted from a vertex in QKT , do not delete.
2. Whenever a red pebble is placed on a vertex in QKT for the first time, place also a blue pebble

on this vertex.

The two properties guarantee that B will have at least the pebbles that A has, while any additional
pebbles must be blue, so that B respects the constraint on the overall number of red pebbles at any
given configuration. In particular, B is a valid calculation that computes QKT . We now analyze

12

the I/O complexity of B. If QA denotes the I/O complexity of A, the additional writes due to the
second rule imply an overall I/O complexity of,

QA + N 2 = o

(cid:19)

(cid:18) N 2d
√
M

Since B computes QKT , this contradicts Lemma 3.6.

4

I/O Complexity of Attention with Fast Matrix Multiplication

We can in fact lower bound the I/O complexity of any algorithm computing attention exactly, in-
cluding those using fast matrix multiplication. The only assumption we require is that the algorithm
computes the matrix product QKT explicitly (whether or not it writes the result to memory). Since
we do not make any further assumptions on the algorithm, the previous approach of analyzing a
computational directed acyclic graph is not sufficient [HK81]. Instead, we relate I/O complexity to
compression lower bounds. As discussed previously, we are primarily interested in the large cache
regime where M = Ω(d2).

4.1 Large Cache: M = Ω(d2)

Given some algorithm A and a sample execution, we split this computation into batches of roughly
M I/O operations each using the framework of [PS14a].

Lemma 4.1. [Theorem 3 of [PS14a]] Suppose A′ is an execution of algorithm A on a machine with
cache of size M . The execution A′ can be split into T epochs of at most M I/O operations, such
that in each epoch the algorithm A has access to a cache of size at most 2M and no I/O operations.
Furthermore, the I/O complexity of A′ is at least (T − 1)M .

Intuitively, the algorithm uses the extra M entries in the cache of size 2M to create a buffer for

the next M I/O operations.

Proof. Let A be any algorithm computing exact attention and A′ an arbitrary execution of A on
machine with a cache size of M bits. Note that given A′ all the decisions made by algorithm A are
already taken.

We proceed to simulate the execution A′ on a machine with cache size of 2M so that the
computation is split into epochs and I/O operations are performed only at the start and end of each
epoch. Split the cache into two pieces, one block of size M to simulate the cache of A and one block
as a buffer for I/O operations. At the start of the epoch, the simulation considers all of the M next
I/O operations, performs all read I/Os by filling the buffer. During the epoch, any I/O operation
is simulated by writing data between the two blocks of cache. Finally, at the end of the epoch, the
simulation takes all written entries in the buffer and writes them to memory. In particular, in each
epoch, no I/O operations are performed so that the algorithm only has access to only a cache of
size 2M with no I/O.

Finally, in every epoch except for the last, M I/O operations are performed, so the I/O com-

plexity of the execution A′ is at least (T − 1)M .

To show our lower bound, we will simplify the problem and assume the matrices Q, K, V have
entries in some finite field Fq. This is similar to the “indivisibility" assumptions of [AM98, PS14a],
as the field size fixes some bound on the amount of information in a single cache entry. Otherwise,

13

if each cache entry can hold an arbitrary real number, then even when M = 1 we could encode the
entire matrices Q, K in a single cache entry.

Under this assumption, we will assume the cache holds M elements of Fq, and we will corre-
spondingly define I/O complexity as the number of finite field elements read and written between the
memory hierarchy. In practice, matrices Q, K have arbitrary real entries. Since our lower bounds
only need to consider algorithms computing QKT , we may restrict the inputs to some finite field Fq
without loss of generality (choosing q large enough to avoid overflows under arithmetic operations)
and we can assume q is of polynomial size since we do not need to consider the softmax operation.
We will separately consider the cases q = 2 (i.e. every entry in the cache and the matrices is a single
bit) and the case for an arbitrarily large finite field of size q.

4.2

I/O Complexity and Compression

We will prove our I/O lower bound by arguing that any algorithm computing entries of QKT
amounts to an efficient compression protocol. First, we show a lower bound for any compression
protocol computing entries of QKT .

Definition 4.2 (Matrix Compression). Let B ≥ 0. In the B-entry matrix compression problem
MatrixEntryCompressionB Alice is given input matrices Q, K ∈ FN ×d
. Alice must send a
message to Bob so that Bob can compute at least B entries in QKT .

q

We review the definition of one-way communication complexity below.

Definition 4.3 (One-Way Communication Complexity). Let f : XA × XB → Y be an arbitrary
function. Suppose Alice has x ∈ XA and Bob has y ∈ XB. A one-way communication protocol
computing f is a pair of functions (E, D) such that D(E(x), y) = f (x, y) for all (x, y) ∈ XA × XB.
The complexity of the protocol is max(x,y) |E(x)|. The one-way communication complexity of f is
the complexity of the optimal protocol.

OneWayCC(f ) = min
(E,D)

max
(x,y)∈XA×XB

|E(x)|

The one-way communication complexity of MatrixEntryCompressionB is O(B log q), since
Alice can compute QKT and transmit the relevant B entries. Instead, if Bob computes a square sub-
matrix of QKT , Alice can instead send the relevant bits of Q, K, transmitting only O(d
B log q)
√
, showing that this is essentially tight.
entries. We give a lower bound of Ω
B log q, B log q)
Our key lemma states that any algorithm outputting many bits of QKT in one epoch (as
described in Lemma 4.1) gives an efficient compression protocol for MatrixEntryCompressionB.

min(d

√

(cid:16)

(cid:17)

Theorem 4.4. Let A′(Q, K) be an execution of an algorithm A on input Q, K on a machine with
cache of size M . Let Bt be the number of entries of QKT computed in the t-th epoch as described
in Lemma 4.1 and B′(Q, K) = maxt Bt. Define,

B∗ = min
Q,K

B′(Q, K)

so that on every input A computes at least B∗ entries of QKT on some epoch. Then, the one-way
communication complexity of MatrixEntryCompressionB∗ is at most 2M log q.

Proof. We will use A to construct a compression protocol. Given input matrices Q, K, we execute
A on Q, K to obtain an execution A′. As described in Lemma 4.1, the execution A′ can be split

14

into epochs, where in each epoch the algorithm A has access only to 2M finite field elements in
cache and reads no other inputs from memory in this epoch. Let t∗ be an epoch in which the
algorithm A computes B′(Q, K) entries of the product QKT . In particular, Alice can send to Bob
the state of the cache of size at most 2M at the beginning of the t∗-th epoch, so that Bob computes
B′(Q, K) ≥ B∗ entries of QKT .

4.3 Matrix Compression Lower Bounds

In this section, we prove a lower bound on the one-way communication complexity of the B-entry
MatrixEntryCompression problem. More precisely, we will show an upper bound on the number
of entries that can be computed given a message of size M . Our previous discussion then implies an
upper bound on the number of bits computed in each epoch, therefore lower bounding the number
of epochs and the I/O complexity.

√

As a warmup, we give a simple lower bound of

B log q.

Lemma 4.5. Let B ≥ 0. Then, the one-way communication complexity of MatrixEntryCompressionB
is at least

B log q.

√

Proof. Let I ⊂ [N ]2 denote any set of indices of the computed entries of QKT where |I| = B.
Define RI to be the distinct row indices in I and CI to be the distinct column indices in I so that
I ⊂ RI × CI .

Without loss of generality, assume |RI | ≥ |CI |. We claim there are at least q|RI | distinct values in
the entries of QKT indexed by I. In particular, let Q, K both be matrices with non-zero values only
in the first column. In K, we set every entry in the first column to 1. In this case, each row of QKT
will be the same, so we can assume the B entries are |RI | entries in a column of QKT . Since we
can arbitrarily set the entries of Q indexed by RI , we can obtain q|RI | different outputs. Since there
are at least q|RI | outputs, the message length M must be at least |RI | log q = max(|RI |, |CI |) log q
in order to unambiguously determine the correct output. Then,

B ≤ RI CI ≤ max(RI , CI )2 ≤

(cid:19)2

(cid:18) M
log q

Thus, M ≥

√

B log q.

We generalize this for matrices Q, K of dimension N × d with rank d ≥ 1.

Lemma 4.6. Suppose Q, K ∈ FN ×d

q

with finite field Fq of size q > N . Then, the one-way commu-

nication complexity of MatrixEntryCompressionB is at least min

(cid:18)

(cid:113) B
d

2 , B

4

(cid:19)

log q.

We show that for any set of B indices, there are more than qM possible values. Thus, a message

length of at least M log q is required to specify these entries exactly.

Proof. Let M denote the maximum message length in the communication protocol. Let I = [N ]2
denote the indices of QKT computed with B = |I|. Define RI to be the distinct row indices in I
and CI to be the distinct column indices in I so that I ⊂ RI × CI .

For each i ∈ RI , let Ri = {j s.t. (i, j) ∈ I} be the computed entries in the i-th row of QKT .
Similarly, for each j ∈ CI , let Cj = {i s.t. (i, j) ∈ I} be the computed entries in the j-th column
of QKT . Next, define LR = {i s.t. |Ri| ≥ d} and LC = {j s.t. |Cj| ≥ d}. We also define SR =
{(i, j) ∈ I s.t. i ̸∈ LR} and SC = {(i, j) ∈ I s.t. j ̸∈ LC}.

15

First, suppose max(|LR|, |LC|) ≥ (cid:112)B/2. Without loss of generality, assume |LR| ≥ (cid:112)B/2.
Since q > N , we fix K to be the Vandermonde matrix guaranteed by Lemma 4.7. In particular,
every subset of d columns in KT is linearly independent.

Fix some row i ∈ RI . We claim that there are at least qmin(|Ri|,d) distinct values in the Ri indices
of the i-th row. First, suppose |Ri| ≤ d. By the construction of matrix K and |Ri| ≤ d, the columns
of KT indexed by Ri are linearly independent. Then, for any ⃗v ∈ F|Ri|
, we can set the i-th row of
Q to be,

Q[i] = ⃗v (cid:0)K[r1]T K[r2]T . . . K[r|Ri|]T (cid:1)−1
where K[ri] is the ri-th row of K and Ri = {r1, . . . , r|Ri|}. In particular, this choice of Q[i] ensures
that the Ri entries of QKT are exactly ⃗v so that there are at least q|Ri| distinct values. Whenever
|Ri| > d, we simply take an arbitrary subset of Ri of size d, and use their linear independence to
proceed with the same argument, thus obtaining the lower bound of qmin(|Ri|,d).

q

Finally, note that the we can obtain these distinct values for each row in RI independently, since
we have fixed K as the Vandermonde matrix and for each row we only modify the entries of Q[i].
In particular, the total number of possible distinct values in all the entries of I is at least,

qmin(|Ri|,d)

(cid:89)

i∈RI

so that we obtain the following lower bound on the message length of the communication protocol
in order to unambiguously specify B entries,

M ≥





(cid:88)

i∈RI



min(|Ri|, d)

 log q

≥ (d|LR| + |SR|) log q

(cid:114)

≥ d

B
2

log q

(1)

where SR = {(i, j) ∈ I s.t. i ̸∈ LR} and the final inequality follows from our assumption on LR. In
particular, this implies M ≥ d(cid:112)B/2 log q as desired.

Finally, we consider the case max(|LR|, |LC|) < (cid:112)B/2. Then, the number of entries in LR × LC
2 . Note that any entry of I not in LR × LC must be in SR ∪ SC and therefore,

is at most B

B
2

≤ |SR| + |SC|

Assume without loss of generality |SR| ≥ |SC|. Equation 1 then implies M ≥ B

4 log q.

In our lower bound construction, we require matrices satisfying strong linear independence
constraints. Specifically, we require a N × d matrix such that every subset of d rows is linearly inde-
pendent. When the matrices have elements in a large finite field, this is obtained by Vandermonde
matrices.

Lemma 4.7. There is a N × d Vandermonde matrix with entries in a finite field Fq of size q > N
where every subset of d rows is linearly independent.

16

Proof. Consider the N × d Vandermonde matrix,








V =

1

. . . αd−1
1 α1 α2
1
. . . αd−1
1 α2 α2
2
...
...
...
...
. . .
N . . . αd−1
1 αN α2

2

N








where α1, α2, . . . , αN are distinct elements in Fq, since we choose q > N . Then, for any subset of d
rows, the determinant of this sub-matrix is,

(cid:89)

0 ̸=

1≤i<j≤d

(αki − αkj )

where k1, . . . , kd are the indices of the d rows. Since the determinant of this matrix is non-zero, the
rows are linearly independent.

We are now ready to prove the main result of this section. For M ≥ d2, this matches the upper

bound given by [DFE+22].

where q > N . The I/O complexity of attention (with any

Theorem 4.8. Suppose Q, K ∈ FN ×d
(cid:16)

q

matrix multiplication algorithm) is Ω

M , N 2(cid:17)(cid:17)
Proof. The theorem follows from combining Theorem 4.4 and Lemmas 4.1 and 4.6. Consider an
arbitrary algorithm A and its best execution A′, on an input Q, K, V with B′(Q, K) = B∗ as
described in Theorem 4.4.

(cid:16) N 2d2

min

.

Since q > N we apply Lemmas 4.1 and 4.6 and obtain

(cid:32)

(cid:114)

min

d

(cid:33)

B∗
2

,

B∗
4

log q ≤ 2M log q

In particular, the maximum number of entries of QKT computed in any epoch has the upper

bound,

B∗ = O

(cid:18)

max

(cid:18) M 2

d2 , M

(cid:19)(cid:19)

Then since the algorithm computes all N 2 values of QKT (regardless of whether these values

are written to memory from cache), the number of epochs is at least,

(cid:18)

T = Ω

min

(cid:18) N 2d2
M 2 ,

N 2
M

(cid:19)(cid:19)

Then, since the I/O complexity of A is at least (T − 1)M , this completes the lower bound.

Whenever M ≥ d2, we obtain a lower bound matching the O

(cid:17)

(cid:16) N 2d2
M

algorithm of [DFE+22].

17

4.4 Binary Matrix Compression Lower Bounds

In the previous section, we obtained a tight lower bound for the I/O complexity of attention when
the entries are allowed to come from a large finite field. We believe it is an interesting theoretical
question to investigate the I/O complexity with entries in smaller finite fields. Specifically, we will
consider the binary finite field F2 = {0, 1}.

The assumption q > N was only required to construct a matrix satisfying strong linear inde-
pendence constraints in Lemma 4.7. Even relaxing this constraint and considering q = 2, we can
still construct matrices satisfying fairly strong linear independence constraints using error correcting
codes. In fact, our previous use of Vandermonde matrices can be interpreted as using Reed-Solomon
codes by allowing for arbitrarily large finite fields. Recall that a linear code C ⊂ {0, 1}N is the null-
space of the parity check matrix H. Using Binary BCH codes, we can obtain a similar result with
binary matrices.

Lemma 4.9. There exists a matrix K ∈ {0, 1}N ×d such that every set of
independent.

2d

log(N +1) −1 rows is linearly

Before proving Lemma 4.9, we require several intermediate results. First, we state the following
standard lemma relating distance of linear codes to linear independence in the parity check matrix.

Lemma 4.10. A linear code has distance d, if and only if any (d − 1) columns of the parity check
matrix is linearly independent and there exist d columns that are linearly dependent.

Proof. Consider a code C of length n, dimension k, and distance d. Suppose there is a set of (d − 1)
linearly dependent columns. Then, there is a vector x with wt(x) ≤ d − 1 such that Hx = 0,
contradicting the minimum distance d of C. Since the distance of the code is d, there exists a vector
x such that Hx = 0 and wt(x) = d. In particular, there exists a subset of d independent columns.
To prove the converse, note that the conditions on H imply there exists a codeword of weight d

and no codeword of weight less than d, so that the minimum distance of the code is exactly d.

Next, we use the fact that binary BCH codes are optimal high rate codes. Recall that a code

with parity check matrix H of dimension d × N has dimension at least N − d.

Lemma 4.11. [Hoc59, BR60] For a length N = 2m − 1 and a distance s, there exists a code
BCH[N, s] with dimension at least N − (cid:6) s−1
2

(cid:7) log(N + 1).

We provide the definition of BCH codes. Recall an element α ∈ F in a finite field is a primitive

element if it generates the multiplicative group F∗.

Definition 4.12 ([Hoc59, BR60]). For length N = 2m − 1, distance s, and primitive element
α ∈ F∗

2m, the binary BCH code is defined,

BCH[N, s] = {(c0, . . . , cN −1) s.t. c(α) = . . . = c(αs−1) = 0}

where c(X) = c0 + c1X + . . . + cN −1X N −1.

The proof of Lemma 4.11 is a standard exercise.

Proof of Lemma 4.11. To show a lower bound on the dimension of the code, we argue that the parity
check matrix H does not have too many rows. We begin with a weaker bound of N −(s−1) log(N +1).
In particular, we show that each constraint c can be written as m = log(N + 1) linear constraints.

18

We choose a basis β = {β1 = 1, β2, . . . , βm} of Fm

2 as a vector space. For any x ∈ Fm
the linear map x (cid:55)→ αx which can be written as x (cid:55)→ Mαx for some matrix Mα ∈ Fm×m
represented in the above basis. Then, the constraint c(α) = 0 can be viewed as,

2

2 , consider
where x is















c0
0
...
0

+ Mα















c1
0
...
0

+ . . . + MαN −1








cN −1
0
...
0








=









0
0


...


0

Thus, each constraint c(αi) = 0 can be viewed as log(N + 1) linear constraints. Since there are s − 1
such constraints, this ensures the parity check matrix has dimension (s − 1) log(N + 1) × N .

c(γ2) = 0. In particular, (cid:4) s−1
2

We now prove the improved bound. This follows from the fact that c(γ) = 0 if and only if
(cid:7) relevant constraints.
It remains to show c(γ2) = 0 if and only if c(γ) = 0. Note that c(γ) = 0 if and only if c(γ)2 = 0.

(cid:5) constraints are redundant, leaving only (cid:6) s−1
2

Furthermore, for α, β ∈ Fm

2 , (α + β)2 = α2 + β2. Then,

0 = c(γ) = c(γ)2

= c2
0 + (c1γ)2 + . . . + (cN −1γN −1)2
= c0 + c1γ2 + . . . cN −1γ2(N −1) = c(γ2)

where we have used ci = c2

i for all coefficients ci ∈ F2.

We now prove Lemma 4.9 and describe the construction of the desired matrix K satisfying

strong linear independence constraints.

Proof. We assume without loss of generality that N = 2m − 1 for some m. If not, we at most double
N by choosing the minimum m such that 2m − 1 ≥ N and take any N -row sub-matrix.

From the construction of the code BCH[N, s], we observe that it has a parity check matrix H of
(cid:7) log(N + 1) × N . Since the code has distance s, from Lemma 4.9, any set of s − 1

dimension (cid:6) s−1
2
rows is linearly independent. In particular, if d = (cid:6) s−1
2

(cid:7) log(N + 1), we have,

s ≥

2d
log(N + 1)

giving the desired bound on s − 1. Thus, we choose K = H T .

Given the construction of the matrix K, we can prove the following analogues of Lemma 4.6
and Theorem 4.8. These results match the upper bound of Theorem 3.2 up to a O(log2 N ) factor.

Lemma 4.13. Suppose Q, K are binary N × d matrices. Then, the one-way communication com-
plexity of MatrixEntryCompressionB is at least Ω

√
B
log N , B

min

(cid:16) d

(cid:17)(cid:17)

(cid:16)

.

We modify LR = {i s.t. |Ri| ≥

Proof. The proof follows Lemma 4.6 closely, so we only point out the necessary modifications. Again
let M denote the maximum message length in the communication protocol and I = [N ]2 denote
the indices of QKT computed with B = |I|. Define RI , CI , {Ri}N

j=1 as in Lemma 4.6.
log(N +1) − 1} and define
We again consider first the case max(|LR|, |LC|) ≥ (cid:112)B/2 and assume |LR| ≥ (cid:112)B/2. Instead
of the Vandermonde matrix, we fix K to be the matrix guaranteed by Lemma 4.9. In particular,
every subset of

i=1, {Cj}N
log(N +1) − 1} and LC = {j s.t. |Cj| ≥

log(N +1) − 1 columns in KT is linearly independent.

SR and SC as before.

2d

2d

2d

19

Following an analogous argument as Lemma 4.6, we obtain the following lower bound on the

message length of the communication protocol in order to unambiguously specify B entries,

(cid:88)

M ≥

(cid:18)

min

|Ri|,

2d
log(N + 1)

(cid:19)

− 1

i∈RI
(cid:18)

≥

= Ω

2d
log(N + 1)
√
(cid:33)
(cid:32)

d
B
log N

(cid:19)

− 1

|LR| + |SR|

(2)

where the final inequality follows from our assumption on LR.

Finally, we consider the case max(|LR|, |LC|) < (cid:112)B/2. Again following similar arguments as

Lemma 4.6 and Equation 2, we have,

M ≥ max(|SR|, |SC|) ≥

B
4

so that M is at least the minimum of the two bounds.

We now state the I/O complexity lower bound of attention given binary input matrices.

Theorem 4.14. Suppose Q, K ∈ {0, 1}N ×d. The I/O complexity of attention (with any matrix
, N 2(cid:17)(cid:17)
multiplication algorithm) is Ω

min

(cid:16)

.

(cid:16) N 2d2
M log2 N

Proof. Following similar arguments as Theorem 4.8, we obtain,

(cid:32)

(cid:32)

Ω

min

√

B∗
d
log N

(cid:33)(cid:33)

, B∗

≤ 2M

where B∗ is as defined in Theorem 4.4. In particular, the maximum number of entries of QKT
computed in any epoch is at most,

B∗ = O

(cid:18)

max

(cid:18) M 2 log2 N
d2

, M

(cid:19)(cid:19)

which gives the I/O complexity lower bound,

(cid:18)

Ω

min

(cid:18) N 2d2

M log2 N

(cid:19)(cid:19)

, N 2

as desired.

4.5 Small Cache: M = o(d2)

In the small cache setting, we proved an equivalence between attention and matrix multiplication in
the setting where both are computed using the standard algorithm. We do the same for algorithms
using fast matrix multiplication.

Let QAtt(M ) denote the I/O complexity of attention on a machine with cache size M . Let
QM(a,b,c)(M ) denote the I/O complexity of multiplying a a × b matrix with a b × c matrix on a
machine with cache size M . First, we show matrix multiplication is more expensive than attention.

20

Lemma 4.15. For all M ,

QAtt(M ) = O (cid:0)QM(N,d,N )(M ) + QM(N,N,d)(M )(cid:1)

Proof. First, we use the given algorithm for rectangular matrix multiplication to compute QKT with
QM(N,d,N ) I/O operations. Then, note that computing softmax(QKT ) can be done in O(N 2) time
and therefore O(N 2) I/O complexity as each operation can be performed with O(1) I/O operations.
Finally, we use the given algorithm to compute softmax(QKT )V with QM(N,N,d). Then, the overall
I/O complexity is,

QAtt(M ) = O (cid:0)QM(N,d,N ) + N 2 + QM(N,N,d)
= O (cid:0)QM(N,d,N ) + QM(N,N,d)

(cid:1)

(cid:1)

since the I/O complexity of both matrix products is at least N 2, as either the input or output has
size N 2.

When M ≤ d2, the two are equivalent.

Lemma 4.16. Let M ≤ d2. Then, QAtt(M ) = Ω (cid:0)QM(N,d,N )(M )(cid:1).
Proof. First, consider any two input matrices Q, KT . We simulate the attention algorithm with the
following modification: whenever an entry (QKT )ij is computed for the first time, we write this
entry to memory. Our modified algorithm successfully computes the matrix product QKT using
at most O (cid:0)QAtt(M ) + N 2(cid:1) I/O operations. From Theorem 4.8, we have that whenever M ≤ d2,
QAtt(M ) = Ω(N 2). As a result, we compute Attention with O (QAtt(M )) I/O complexity.

As a corollary, we obtain the following equivalence in the small cache setting.

Theorem 4.17. Let M ≤ d2. Then,

QAtt(M ) = Ω (cid:0)QM(N,d,N )(M )(cid:1)
QAtt(M ) = O (cid:0)QM(N,d,N )(M ) + QM(N,N,d)(M )(cid:1)

5 Conclusion

We have established tight I/O complexity lower bounds for attention. Our lower bound in fact
holds for any algorithm computing matrix product QKT . We give a tight characterization of the
I/O complexity of algorithms using standard matrix multiplication, answering an open question of
[DFE+22].

Furthermore, in the regime of practical interest, where cache size M ≥ d2 is large, we extend our
lower bound to algorithms using fast matrix multiplication, showing that FlashAttention is optimal
even when fast matrix multiplication is allowed. Furthermore, we establish a connection between
communication complexity and I/O complexity, which may be of independent theoretical interest.
We leave the problem of establishing tight I/O complexity bounds for attention in the small
cache regime (M ≤ d2) (equivalently rectangular matrix multiplication) as an interesting open
problem.

Acknowledgements

We would like to thank Arya Mazumdar and Harry Sha for helpful discussions.

21

References

[AM98]

[AS23]

[AV88]

Lars Arge and Peter Bro Miltersen. On showing lower bounds for external-memory
computational geometry problems. In External Memory Algorithms, Proceedings of a
DIMACS Workshop, 1998. 13

Josh Alman and Zhao Song.
abs/2302.13214, 2023. 2

Fast attention requires bounded entries. CoRR,

Alok Aggarwal and Jeffrey Scott Vitter. The input/output complexity of sorting and
related problems. Commun. ACM, 1988. 3

[BDH+12] Grey Ballard, James Demmel, Olga Holtz, Benjamin Lipshitz, and Oded Schwartz.
Graph expansion analysis for communication costs of fast rectangular matrix multipli-
cation. In Mediterranean Conference on Algorithms MedAlg, 2012. 3

[BDHS12] Grey Ballard, James Demmel, Olga Holtz, and Oded Schwartz. Graph expansion and
communication costs of fast matrix multiplication. J. ACM, 59(6):32:1–32:23, 2012. 3

[BMR+20] Tom B. Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared Kaplan, Prafulla
Dhariwal, Arvind Neelakantan, Pranav Shyam, Girish Sastry, Amanda Askell, Sandhini
Agarwal, Ariel Herbert-Voss, Gretchen Krueger, Tom Henighan, Rewon Child, Aditya
Ramesh, Daniel M. Ziegler, Jeffrey Wu, Clemens Winter, Christopher Hesse, Mark
Chen, Eric Sigler, Mateusz Litwin, Scott Gray, Benjamin Chess, Jack Clark, Christopher
Berner, Sam McCandlish, Alec Radford, Ilya Sutskever, and Dario Amodei. Language
models are few-shot learners. In Neural Information Processing Systems, NeurIPS, 2020.
2

[BR60]

[BS17]

R. C. Bose and Dwijendra K. Ray-Chaudhuri. On A class of error correcting binary
group codes. Inf. Control., 3(1):68–79, 1960. 2, 4, 18

Gianfranco Bilardi and Lorenzo De Stefani. The I/O complexity of strassen’s matrix
multiplication with recomputation. In Algorithms and Data Structures WADS, 2017. 3

[CDW+21] Beidi Chen, Tri Dao, Eric Winsor, Zhao Song, Atri Rudra, and Christopher Ré. Scat-
In Neural Information Processing

terbrain: Unifying sparse and low-rank attention.
Systems, NeurIPS, 2021. 2

[CLD+21] Krzysztof Marcin Choromanski, Valerii Likhosherstov, David Dohan, Xingyou Song,
Andreea Gane, Tamás Sarlós, Peter Hawkins, Jared Quincy Davis, Afroz Mohiuddin,
Lukasz Kaiser, David Benjamin Belanger, Lucy J. Colwell, and Adrian Weller. Rethink-
ing attention with performers. In International Conference on Learning Representations,
ICLR, 2021. 2

[CP23]

Xi Chen and Binghui Peng. Memory-query tradeoffs for randomized convex optimiza-
tion. In Symposium on Foundations of Computer Science, FOCS, 2023. 2

[CPP22]

Xi Chen, Christos H. Papadimitriou, and Binghui Peng. Memory bounds for continual
learning. In Symposium on Foundations of Computer Science, FOCS, 2022. 2, 3

[Dao23]

Tri Dao. Flashattention-2: Faster attention with better parallelism and work partition-
ing. CoRR, abs/2307.08691, 2023. 2, 6, 7

22

[DFE+22] Tri Dao, Daniel Y. Fu, Stefano Ermon, Atri Rudra, and Christopher Ré. Flashattention:
In Neural Information

Fast and memory-efficient exact attention with io-awareness.
Processing SystemsNeurIPS, 2022. 2, 3, 6, 8, 17, 21

[DKS19]

Yuval Dagan, Gil Kur, and Ohad Shamir. Space lower bounds for linear prediction in
the streaming model. In Conference on Learning Theory, COLT, 2019. 3

[GLM20] Alon Gonen, Shachar Lovett, and Michal Moshkovitz. Towards a combinatorial char-
acterization of bounded-memory learning. In Neural Information Processing Systems,
NeurIPS, 2020. 2

[GU18]

Francois Le Gall and Florent Urrutia. Improved rectangular matrix multiplication using
powers of the coppersmith-winograd tensor. In Artur Czumaj, editor, Proceedings of
the Twenty-Ninth Annual ACM-SIAM Symposium on Discrete Algorithms, SODA 2018,
New Orleans, LA, USA, January 7-10, 2018, pages 1029–1046. SIAM, 2018. 2

[HJK+23]

Insu Han, Rajesh Jayaram, Amin Karbasi, Vahab Mirrokni, David P. Woodruff, and
Amir Zandieh. Hyperattention: Long-context attention in near-linear time. CoRR,
abs/2310.05869, 2023. 2

[HK81]

Jia-Wei Hong and Hsiang-Tsung Kung. I/o complexity: The red-blue pebble game. In
Symposium on Theory of Computing STOC, 1981. 2, 3, 5, 6, 12, 13

[Hoc59]

Alexis Hocquenghem. Codes correcteurs d’erreurs. Chiffers, 2:147–156, 1959. 2, 4, 18

[KKL20] Nikita Kitaev, Lukasz Kaiser, and Anselm Levskaya. Reformer: The efficient trans-

former. In International Conference on Learning Representations, ICLR, 2020. 2

[KLMY19] Daniel Kane, Roi Livni, Shay Moran, and Amir Yehudayoff. On communication com-
In Conference on Learning Theory, COLT, 2019.

plexity of classification problems.
3

[KVPF20] Angelos Katharopoulos, Apoorv Vyas, Nikolaos Pappas, and François Fleuret. Trans-
formers are rnns: Fast autoregressive transformers with linear attention. In International
Conference on Machine Learning, ICML, 2020. 2

[MSSV22] Annie Marsden, Vatsal Sharan, Aaron Sidford, and Gregory Valiant. Efficient convex
optimization requires superlinear memory. In Conference on Learning Theory, COLT,
2022. 2

[PR23]

[PS14a]

[PS14b]

[PZ23]

[Raz19]

Binghui Peng and Aviad Rubinstein. Near optimal memory-regret tradeoff for online
learning. In Symposium on Foundations of Computer Science, FOCS, 2023. 2

Rasmus Pagh and Francesco Silvestri. The input/output complexity of triangle enu-
meration. In Principles of Database Systems PODS, 2014. 3, 13

Rasmus Pagh and Morten Stöckel. The input/output complexity of sparse matrix mul-
tiplication. In European Symposium on Algorithms ESA, 2014. 3

Binghui Peng and Fred Zhang. Online prediction in sub-linear space. In Symposium on
Discrete Algorithms, SODA, 2023. 2

Ran Raz. Fast learning requires good memory: A time-space lower bound for parity
learning. J. ACM, 66(1):3:1–3:18, 2019. 2

23

[SHS15]

Jacob Scott, Olga Holtz, and Oded Schwartz. Matrix multiplication i/o-complexity by
path routing.
In Symposium on Parallelism in Algorithms and Architectures SPAA,
2015. 3

[SSV19]

Vatsal Sharan, Aaron Sidford, and Gregory Valiant. Memory-sample tradeoffs for linear
regression with small error. In Symposium on Theory of Computing, STOC, 2019. 2

[SWXZ22] Vaidehi Srinivas, David P. Woodruff, Ziyu Xu, and Samson Zhou. Memory bounds for

the experts problem. In Symposium on Theory of Computing, STOC, 2022. 2

[VSP+17] Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N.
Gomez, Lukasz Kaiser, and Illia Polosukhin. Attention is all you need.
In Neural
Information Processing Systems NeurIPS, 2017. 2

[WS19]

Blake E. Woodworth and Nathan Srebro. Open problem: The oracle complexity of
convex optimization with limited memory. In Conference on Learning Theory, COLT,
2019. 2

[WXXZ23] Virginia Vassilevska Williams, Yinzhan Xu, Zixuan Xu, and Renfei Zhou. New bounds

for matrix multiplication: from alpha to omega. CoRR, abs/2307.07970, 2023. 2

[ZGD+20] Manzil Zaheer, Guru Guruganesh, Kumar Avinava Dubey, Joshua Ainslie, Chris Alberti,
Santiago Ontañón, Philip Pham, Anirudh Ravula, Qifan Wang, Li Yang, and Amr
Ahmed. Big bird: Transformers for longer sequences. In Neural Information Processing
Systems, NeurIPS, 2020. 2

24

