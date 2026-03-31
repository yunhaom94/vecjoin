Red-Blue Pebbling Revisited:
Near Optimal Parallel Matrix-Matrix Multiplication
Technical Report

Grzegorz Kwasniewski1, Marko Kabi´c2,3, Maciej Besta1,
Joost VandeVondele2,3, Raffaele Solc`a2,3, Torsten Hoefler1
1Department of Computer Science, ETH Zurich, 2ETH Zurich, 3Swiss National Supercomputing Centre (CSCS)

9
1
0
2

c
e
D
3
1

]

C
C
.
s
c
[

3
v
6
0
6
9
0
.
8
0
9
1
:
v
i
X
r
a

ABSTRACT
We propose COSMA: a parallel matrix-matrix multiplication algo-
rithm that is near communication-optimal for all combinations of
matrix dimensions, processor counts, and memory sizes. The key
idea behind COSMA is to derive an optimal (up to a factor of 0.03%
for 10MB of fast memory) sequential schedule and then parallelize
it, preserving I/O optimality. To achieve this, we use the red-blue
pebble game to precisely model MMM dependencies and derive
a constructive and tight sequential and parallel I/O lower bound
proofs. Compared to 2D or 3D algorithms, which fix processor
decomposition upfront and then map it to the matrix dimensions, it
3 times. COSMA outper-
reduces communication volume by up to
forms the established ScaLAPACK, CARMA, and CTF algorithms
in all scenarios up to 12.8x (2.2x on average), achieving up to 88%
of Piz Daint’s peak performance. Our work does not require any
hand tuning and is maintained as an open source implementation.

√

1 INTRODUCTION
Matrix-matrix multiplication (MMM) is one of the most fundamen-
tal building blocks in scientific computing, used in linear algebra
algorithms [13, 15, 42], (Cholesky and LU decomposition [42], eigen-
value factorization [13], triangular solvers [15]), machine learn-
ing [6], graph processing [4, 8, 18, 36, 44, 52], computational chem-
istry [21], and others. Thus, accelerating MMM routines is of great
significance for many domains. In this work, we focus on mini-
mizing the amount of transferred data in MMM, both across the
memory hierarchy (vertical I/O) and between processors (horizontal
I/O, aka “communication”)1.

The path to I/O optimality of MMM algorithms is at least 50
years old. The first parallel MMM algorithm is by Cannon [10],
which works for square matrices and square processor decomposi-
tions. Subsequent works [24, 25] generalized the MMM algorithm to
rectangular matrices, different processor decompositions, and com-
munication patterns. PUMMA [17] package generalized previous
works to transposed matrices and different data layouts. SUMMA al-
gorithm [56] further extended it by optimizing the communication,
introducing pipelining and communication–computation overlap.
This is now a state-of-the-art so-called 2D algorithm (it decomposes
processors in a 2D grid) used e.g., in ScaLAPACK library [14].

Agarwal et al. [1] showed that in a presence of extra memory,
one can do better and introduces a 3D processor decomposition.
The 2.5D algorithm by Solomonik and Demmel [53] effectively

This is an extended version of the SC’19 publication (DOI 10.1145/3295500.3356181)
Changes in the original submission are listed in the Appendix
1We also focus only on “classical” MMM algorithms which perform n3 multiplications
and additions. We do not analyze Strassen-like routines [54], as in practice they are
usually slower [19].

Figure 1: Percentage of peak flop/s across the experiments ranging from 109 to 18,432
cores achieved by COSMA and the state-of-the-art libraries (Sec. 9).

Figure 2: Illustratory evolution of MMM algorithms reaching the I/O lower bound.

interpolates between those two results, depending on the avail-
able memory. However, Demmel et al. showed that algorithms
optimized for square matrices often perform poorly when matrix
dimensions vary significantly [22]. Such matrices are common in
many relevant areas, for example in machine learning [60, 61] or
computational chemistry [45, 49]. They introduced CARMA [22], a
recursive algorithm that achieves asymptotic lower bounds for all
configurations of dimensions and memory sizes. This evolution for
chosen steps is depicted symbolically in Figure 2.

Unfortunately, we observe several limitations with state-of-the
art algorithms. ScaLAPACK [14] (an implementation of SUMMA)
supports only the 2D decomposition, which is communication–
inefficient in the presence of extra memory. Also, it requires a user
to fine-tune parameters such as block sizes or a processor grid size.
CARMA supports only scenarios when the number of processors
is a power of two [22], a serious limitation, as the number of pro-
cessors is usually determined by the available hardware resources.
Cyclops Tensor Framework (CTF) [50] (an implementation of the
2.5D decomposition) can utilize any number of processors, but its
decompositions may be far from optimal (§ 9). We also emphasize
that asymptotic complexity is an insufficient measure of practical per-
√
formance. We later (§ 6.2) identify that CARMA performs up to
3
more communication. Our observations are summarized in Table 1.
Their practical implications are shown in Figure 1, where we see
that all existing algorithms perform poorly for some configurations.

1

LIMITEDMEMORYEXTRAMEMORYLIMITEDMEMORYEXTRAMEMORY020406080100TALLMATRICESSQUARE MATRICESmaximumgeometric meanSTRONGSCALINGScaLAPACK [14]CARMA []COSMA (this work)CTF []% of peak performanceSTRONGSCALING2250YearWorst-case I/O costnaive PUMMA [17]Cannon's [10]SUMMA [56]CARMA [22]COSMA[here]1D2D2.5D & 3D2019decomp.of all matricesrectangularmatricesenchanced communicationpattern"2.5D" [53]optimized for non-squarematricesoptimal decomp. inall scenarioslower bounduse of excessmemory19691994199720112013<1969

Technical Report, 2019,

G. Kwasniewski et al.

2D [56]

2.5D [53]

recursive [22]

COSMA (this work)

Input: User–specified grid

Split m and n

Step 1
Step 2 Map matrices to processor grid Map matrices to processor grid

Available memory
Split m, n, k

Available memory, matrix dimensions

Available memory, matrix dimensions

Split recursively the largest dimension

Find the optimal sequential schedule

Map matrices to recursion tree

Map sequential domain to matrices

(cid:7) Requires manual tuning
(cid:7) Asymptotically more comm.

- Optimal for m = n
(cid:7) Inefficient for m (cid:28) n or n (cid:28) m
(cid:7) Inefficient for some p

√

- Asymptotically optimal for all m, n, k, p
(cid:7) Up to
(cid:7) p must be a power of 2

3 times higher comm. cost

- Optimal for all m, n, k
- Optimal for all p
-- Best time-to-solution

Table 1: Intuitive comparison between the COSMA algorithm and the state-of-the-art 2D, 2.5D, and recursive decompositions. C = AB, A ∈ Rm×k , B ∈ Rk ×n

√

√

In this work, we present COSMA (Communication Optimal S-
partition-based Matrix multiplication Algorithm): an algorithm
that takes a new approach to multiplying matrices and alleviates
the issues above. COSMA is I/O optimal for all combinations of
parameters (up to the factor of
S + 1−1), where S is the size of
S/(
the fast memory2). The driving idea is to develop a general method
of deriving I/O optimal schedules by explicitly modeling data reuse
in the red-blue pebble game. We then parallelize the sequential
schedule, minimizing the I/O between processors, and derive an
optimal domain decomposition. This is in contrast with the other
discussed algorithms, which fix the processor grid upfront and then
map it to a sequential schedule for each processor. We outline the
algorithm in § 3. To prove its optimality, we first provide a new
constructive proof of a sequential I/O lower bound (§ 5.2.7), then
we derive the communication cost of parallelizing the sequential
schedule (§ 6.2), and finally we construct an I/O optimal parallel
schedule (§ 6.3). The detailed communication analysis of COSMA,
2D, 2.5D, and recursive decompositions is presented in Table 3. Our
algorithm reduces the data movement volume by a factor of up
3 ≈ 1.73x compared to the asymptotically optimal recursive
to
decomposition and up to max{m, n, k} times compared to the 2D
algorithms, like Cannon’s [39] or SUMMA [56].

√

Our implementation enables transparent integration with the
ScaLAPACK data format [16] and delivers near-optimal computa-
tion throughput. We later (§ 7) show that the schedule naturally ex-
presses communication–computation overlap, enabling even higher
speedups using Remote Direct Memory Access (RDMA). Finally,
our I/O-optimal approach is generalizable to other linear algebra
kernels. We provide the following contributions:
• We propose COSMA: a distributed MMM algorithm that is nearly-
S + 1 − 1)) for any combination
S/(

√

√

optimal (up to the factor of
of input parameters (§ 3).

• Based on the red-blue pebble game abstraction [34], we provide
a new method of deriving I/O lower bounds (Lemma 4), which
may be used to generate optimal schedules (§ 4).

• Using Lemma 4, we provide a new constructive proof of the
sequential MMM I/O lower bound. The proof delivers constant
S+ − 1)(§ 5).
factors tight up to
• We extend the sequential proof to parallel machines and provide

S/(

√

√

I/O optimal parallel MMM schedule (§ 6.3).

• We reduce memory footprint for communication buffers and
guarantee minimal local data reshuffling by using a blocked data
layout (§ 7.6) and a static buffer pre-allocation (§ 7.5), providing
compatibility with the ScaLAPACK format.

2Throughout this paper we use the original notation from Hong and Kung to denote
the memory size S . In literature, it is also common to use the symbol M [2, 3, 33].

2

• We evaluate the performance of COSMA, ScaLAPACK, CARMA,
and CTF on the CSCS Piz Daint supercomputer for an extensive
selection of problem dimensions, memory sizes, and numbers of
processors, showing significant I/O reduction and the speedup
of up to 8.3 times over the second-fastest algorithm (§ 9).

2 BACKGROUND
We first describe our machine model (§ 2.1) and computation model
(§ 2.2). We then define our optimization goal: the I/O cost (§ 2.3).

2.1 Machine Model
We model a parallel machine with p processors, each with local
memory of size S words. A processor can send and receive from
any other processor up to S words at a time. To perform any
computation, all operands must reside in processor’ local memory.
If shared memory is present, then it is assumed that it has infinite
capacity. A cost of transferring a word from the shared to the local
memory is equal to the cost of transfer between two local memories.

2.2 Computation Model
We now briefly specify a model of general computation; we use this
model to derive the theoretical I/O cost in both the sequential and
parallel setting. An execution of an algorithm is modeled with the
computational directed acyclic graph (CDAG) G = (V , E) [11, 28, 47].
A vertex v ∈ V represents one elementary operation in the given
computation. An edge (u, v) ∈ E indicates that an operation v
depends on the result of u. A set of all immediate predecessors (or
successors) of a vertex are its parents (or children). Two selected
subsets I, O ⊂ V are inputs and outputs, that is, sets of vertices that
have no parents (or no children, respectively).
Red-Blue Pebble Game Hong and Kung’s red-blue pebble game
[34] models an execution of an algorithm in a two-level memory
structure with a small-and-fast as well as large-and-slow memory.
A red (or a blue) pebble placed on a vertex of a CDAG denotes that
the result of the corresponding elementary computation is inside
the fast (or slow) memory. In the initial (or terminal) configuration,
only inputs (or outputs) of the CDAG have blue pebbles. There can
be at most S red pebbles used at any given time. A complete CDAG
calculation is a sequence of moves that lead from the initial to the
terminal configuration. One is allowed to: place a red pebble on any
vertex with a blue pebble (load), place a blue pebble on any vertex
with a red pebble (store), place a red pebble on a vertex whose par-
ents all have red pebbles (compute), remove any pebble, red or blue,
from any vertex (free memory). An I/O optimal complete CDAG
calculation corresponds to a sequence of moves (called pebbling of

I/O Optimal Parallel Matrix Multiplication

Technical Report, 2019,

a graph) which minimizes loads and stores. In the MMM context, it
is an order in which all n

3 multiplications are performed.

2.3 Optimization Goals
Throughout this paper we focus on the input/output (I/O) cost of
an algorithm. The I/O cost Q is the total number of words trans-
ferred during the execution of a schedule. On a sequential or shared
memory machine equipped with small-and-fast and slow-and-big
memories, these transfers are load and store operations from and
to the slow memory (also called the vertical I/O). For a distributed
machine with a limited memory per node, the transfers are commu-
nication operations between the nodes (also called the horizontal
I/O). A schedule is I/O optimal if it minimizes the I/O cost among all
schedules of a given CDAG. We also model a latency cost L, which
is a maximum number of messages sent by any processor.

2.4 State-of-the-Art MMM Algorithms
Here we briefly describe strategies of the existing MMM algorithms.
Throughout the whole paper, we consider matrix multiplication
C = AB, where A ∈ Rm×k , B ∈ Rk ×n, C ∈ Rm×n , where m, n, and
k are matrix dimensions. Furthermore, we assume that the size of
each matrix element is one word, and that S < min{mn, mk, nk},
that is, none of the matrices fits into single processor’s fast memory.
We compare our algorithm with the 2D, 2.5D, and recursive de-
compositions (we select parameters for 2.5D to also cover 3D). We
√
assume a square processor grid [
p, 1] for the 2D variant, analo-
p,
gously to Cannon’s algorithm [10], and a cubic grid [(cid:112)p/c, (cid:112)p/c, c]
for the 2.5D variant [53], where c is the amount of the “extra” mem-
ory c = pS/(mk + nk). For the recursive decomposition, we assume
that in each recursion level we split the largest dimension m, n,
or k in half, until the domain per processor fits into memory. The
detailed complexity analysis of these decompositions is in Table 3.
We note that ScaLAPACK or CTF can handle non-square decompo-
sitions, however they create different problems, as discussed in § 1.
Moreover, in § 9 we compare their performance with COSMA and
measure significant speedup in all scenarios.

√

3 COSMA: HIGH-LEVEL DESCRIPTION
COSMA decomposes processors by parallelizing the near optimal
sequential schedule under constraints: (1) equal work distribution
and (2) equal memory size per processor. Such a local sequential
schedule is independent of matrix dimensions. Thus, intuitively,
instead of dividing a global domain among p processors (the top-
down approach), we start from deriving a near I/O optimal sequential
schedule. We then parallelize it, minimizing the I/O and latency
costs Q, L (the bottom-up approach); Figure 3 presents more details.
COSMA is sketched in Algorithm 1. In Line 1 we derive a
sequential schedule, which consists of series of a ×a outer products.
(Figure 4 b). In Line 2, each processor is assigned to compute b
of these products, forming a local domain D (Figure 4 c), that is
each D contains a × a × b vertices (multiplications to be performed
- the derivation of a and b is presented in § 6.3). In Line 3, we
find a processor grid G that evenly distributes this domain by the
matrix dimensions m, n, and k. If the dimensions are not divisible
by a or b, this function also evaluates new values of aopt and bopt
by fitting the best matching decomposition, possibly not utilizing
some processors (§ 7.1, Figure 4 d-f). The maximal number of idle
processors is a tunable parameter δ . In Line 5, we determine the
initial decomposition of matrices A, B, and C to the submatrices

3

(a) 3D domain decomposition

(b) COSMA decomposition

Figure 3: Domain decomposition using p = 8 processors. In scenario (a), a straight-
forward 3D decomposition divides every dimension in p1/3 = 2. In scenario (b),
COSMA starts by finding a near optimal sequential schedule and then parallelizes it
minimizing crossing data reuse VR, i (§ 5). The total communication volume is reduced
by 17% compared to the former strategy.

that are local for each processor. COSMA may handle any
Al , Bl , Cl
initial data layout, however, an optimal block-recursive one (§ 7.6)
may be achieved in a preprocessing phase. In Line 6, we compute
the size of the communication step, that is, how many of bopt
outer products assigned to each processor are computed in a single
round, minimizing the latency (§ 6.3). In Line 7 we compute the
number of sequential steps (Lines 8–11) in which every processor:
(1) distributes and updates its local data Al
among the grid
(Line 10). Finally, the partial
G (Line 9), and (2) multiplies Al
results Cl

are reduced over G (Line 12).

I/O Complexity of COSMA Lines 2–7 require no communi-
cation (assuming that the parameters m, n, k, p, S are already dis-
tributed). The loop in Lines 8-11 executes (cid:6)2ab/(S − a
2)(cid:7) times. In
Line 9, each processor receives |Al | + |Bl | elements. Sending the
2 communicated elements. In § 6.3
partial results in Line 12 adds a
we derive the optimal values for a and b, which yield a total of
min (cid:110)

(cid:17)2/3 (cid:111) elements communicated.

and Bl

and Bl

, 3 (cid:16) mnk

S + 2 · mnk
√
S

p

P

Algorithm 1 COSMA
Input: matrices A ∈ Rm×k, B ∈ Rk ×n ,

number of processors: p, memory size: S , computation-I/O tradeoff ratio ρ

Output: matrix C = AB ∈ Rm×n
1: a ← F indSeqSchedul e(S, m, n, k, p)
2: b ← P ar all el izeSched(a, m, n, k, p)
3: (G, aopt , bopt ) ← F it Ranks(m, n, k, a, b, p, δ )
4: for all pi ∈ {1 . . . p } do in parallel
5:

(Al , Bl , Cl ) ← Get Dat aDecomp(A, B, G, pi )

(cid:46) sequential I/O optimality (§ 5)
(cid:46) parallel I/O optimality (§ 6)

(cid:46) latency-minimizing size of a step (6.3)

(cid:46) number of steps

(Al , Bl ) ← Dist r Dat a(Al , Bl , G, j, pi )
Cl ← Mul t iply(Al , Bl , j)

end for
C ← Reduce(Cl , G)

(cid:46) compute locally

(cid:46) reduce the partial results

6:

7:

s ←

(cid:23)

(cid:22) S −a

2
opt
2aopt
(cid:109)

(cid:108) bopt
s

t ←
for j ∈ {1 . . . t } do

8:
9:
10:
11:
12:
13: end for

Step 2: Map computation tothe process griddomainperprocessdivide by p1/3ACBStep 1: Find the process grid"Top-down" (e.g., 3D)I/Obetweendomainsrequired!no reusedomain per processorproductsABCStep 1: Sequential scheduleStep 2: Parallel schedule Minimize crossing      seriesof outerproducts"Bottom-up" (COSMA)No I/ObetweendomainsTechnical Report, 2019,

G. Kwasniewski et al.

4 ARBITRARY CDAGS: LOWER BOUNDS
We now present a mathematical machinery for deriving I/O lower
bounds for general CDAGs. We extend the main lemma by Hong
and Kung [34], which provides a method to find an I/O lower bound
for a given CDAG. That lemma, however, does not give a tight
bound, as it overestimates a reuse set size (cf. Lemma 3). Our key
result here, Lemma 4, allows us to derive a constructive proof of
a tighter I/O lower bound for a sequential execution of the MMM
CDAG (§ 5).

The driving idea of both Hong and Kung’s and our approach is
to show that some properties of an optimal pebbling of a CDAG (a
problem which is PSPACE-complete [40]) can be translated to the
properties of a specific partition of the CDAG (a collection of subsets
Vi of the CDAG; these subsets form subcomputations, see § 2.2).
One can use the properties of this partition to bound the number
of I/O operations of the corresponding pebbling. Hong and Kung
use a specific variant of this partition, denoted as S-partition [34].
We first introduce our generalization of S-partition, called X -
partition, that is the base of our analysis. We describe symbols used
in our analysis in Table 2.

M
M
M

m, n, k
A, B
C = AB
p

Matrix dimensions
Input matrices A ∈ Rm×k and B ∈ Rk ×n
Output matrix C ∈ Rm×n
The number of processors

s G
h
p
a
r
g

P r ed(v)

Succ(v)

A directed acyclic graph G = (V , E)
A set of immediate predecessors of a vertex v :
P r ed (v) = {u : (u, v) ∈ E }
A set of immediate successors of a vertex v :
Succ(v) = {u : (v, u) ∈ E }
The number of red pebbles (size of the fast memory)
An i -th subcomputation of an S -partition

y
t
i
x
e
l
p
m
o
c
O

/
I

S
Vi
Dom(Vi ), Min(Vi ) Dominator and minimum sets of subcomputation Vi
The reuse set: a set of vertices containing red pebbles
VR,i
(just before Vi starts) and used by Vi
The smallest cardinality of a valid S -partition
H (S )
The maximum size of the reuse set
R(S )
The I/O cost of a schedule (a number of I/O operations)
Q
The computational intensity of Vi
ρi
ρ = maxi {ρi }
The maximum computational intensity

s S = {V1, . . . , Vh } The sequential schedule (an ordered set of Vi )

P = {S1, . . . , Sp } The parallel schedule (a set of sequential schedules Sj )
Dj = (cid:208)
a, b

The local domain (a set of vertices in Sj
Sizes of a local domain: | Dj | = a

e
l
u
d
e
h
c
S

Vi ∈Sj

Vi

b

2

Table 2: The most important symbols used in the paper.

X -Partitions Before we define X -partitions, we first need to
define two sets, the dominator set and the minimum set. Given a
subset Vi ∈ V , define a dominator set Dom(Vi ) as a set of vertices
in V , such that every path from any input of a CDAG to any vertex
in Vi must contain at least one vertex in Dom(Vi ). Define also the
minimum set Min(Vi ) as the set of all vertices in Vi that do not have
any children in Vi .

Now, given a CDAG G = (V , E), let V1, V2, . . . Vh ∈ V be a series
of subcomputations that (1) are pairwise disjoint (∀i, j,i(cid:44)jVi ∩ Vj =
∅), (2) cover the whole CDAG ((cid:208)
i Vi = V ), (3) have no cyclic
dependencies between them, and (4) their dominator and minimum
sets are at most of size X (∀i (|Dom(Vi )| ≤ X ∧ |Min(Vi )| ≤ X )).
These subcomputations Vi correspond to some execution order (a
schedule) of the CDAG, such that at step i, only vertices in Vi are
pebbled. We call this series an X -partition or a schedule of the CDAG
and denote this schedule with S(X ) = {V1, . . . , Vh }.

4.1 Existing General I/O Lower Bound
Here we need to briefly bring back the original lemma by Hong and
Kung, together with an intuition of its proof, as we use a similar
method for our Lemma 3.

4

Intuition The key notion in the existing bound is to use
X = 2S-partitions for a given fast memory size S. For any sub-
computation Vi , if |Dom(Vi )| = 2S, then at most S of them could
contain a red pebble before Vi begins. Thus, at least S additional peb-
bles need to be loaded from the memory. The similar argument goes
for Min(Vi ). Therefore, knowing the lower bound on the number
of sets Vi in a valid 2S-partition, together with the observation that
each Vi performs at least S I/O operations, we phrase the lemma by
Hong and Kung:

Lemma 1 ( [34]). The minimal number Q of I/O operations for
any valid execution of a CDAG of any I/O computation is bounded
by

Q ≥ S · (H (2S) − 1)

(1)

Proof. Assume that we know the optimal complete calculation
of the CDAG, where a calculation is a sequence of allowed moves
in the red-blue pebble game [34]. Divide the complete calculation
into h consecutive subcomputations V1, V2, ..., Vh
, such that during
the execution of Vi , i < h, there are exactly S I/O operations, and
in Vh
there are at most S operations. Now, for each Vi , we define
two subsets of V , VR,i and VB,i . VR,i contains vertices that have red
pebbles placed on them just before Vi begins. VB,i contains vertices
that have blue pebbles placed on them just before Vi begins, and
have red pebbles placed on them during Vi . Using these definitions,
we have: (cid:182) VR,i ∪ VB,i = Dom(Vi ), (cid:183) |VR,i | ≤ S, (cid:184) |VB,i | ≤ S, and
(cid:185) |VR,i ∪ VB,i | ≤ |VR,i | + |VB,i | ≤ 2S. We define similar subsets
WB,i and WR,i for the minimum set Min(Vi ). WB,i contains all
vertices in Vi that have a blue pebble placed on them during Vi , and
WR,i contains all vertices in Vi that have a red pebble at the end of
Vi . By the definition of Vi , |WB,i | ≤ S, by the constraint on the red
pebbles, we have |WR,i | ≤ S, and by te definition of the minimum
set,Min(Vi ) ⊂ WR,i ∪ WB,i . Finally, by the definition of S-partition,
(cid:3)
form a valid 2S-partition of the CDAG.
V1, V2, ..., Vh

4.2 Generalized I/O Lower Bounds

4.2.1 Data Reuse. A more careful look at sets VR,i , VB,i ,WR,i ,
and WB,i allows us to refine the bound on the number of I/O oper-
ations on a CDAG. By definition, VB,i is a set of vertices on which
we place a red pebble using the load rule; We call VB,i a load set of
Vi . Furthermore, WB,i contains all the vertices on which we place
a blue pebble during the pebbling of Vi ; We call WB,i a store set of
Vi . However, we impose more strict VR,i and WR,i definitions: VR,i
contains vertices that have red pebbles placed on them just before
Vi begins and – for each such vertex v ∈ VR,i – at least one child of
v is pebbled during the pebbling of Vi using the compute rule of the
red-blue pebble game. We call VR,i a reuse set of Vi . Similarly, WR,i
contains vertices that have red pebbles placed on them after Vi ends
and were pebbled during Vi and – for each such vertex v ∈ WR,i –
at least one child of v is pebbled during the pebbling of Vi+1 using the
compute rule of the red-blue pebble game. We call WR,i a cache set
of Vi . Therefore, if Qi is the number of I/O operations during the
subcomputation Vi , then Qi ≥ |VB,i | + |WB,i |.

We first observe that, given the optimal complete calculation,
one can divide this calculation into subcomputations such that each
subcomputation Vi performs an arbitrary number of Y I/O oper-
ations. We still have |VR,i | ≤ S, |WR,i | ≤ S, 0 ≤ |WB,i | (by the
definition of the red-blue pebble game rules). Moreover, observe

I/O Optimal Parallel Matrix Multiplication

Technical Report, 2019,

that, because we perform exactly Y I/O operations in each subcom-
putation, and all the vertices in VB,i by definition have to be loaded,
|VB,i | ≤ Y . A similar argument gives 0 ≤ |WB,i | ≤ Y .

Denote an upper bound on |VR,i | and |WR,i | as R(S)
(∀i max{|VR,i |, |WR,i |} ≤ R(S) ≤ S). Further, denote a lower bound
on |VB,i | and |WB,i | as T (S) (∀i 0 ≤ T (S) ≤ min{|VB,i |, |WB,i |}). We
can use R(S) and T (S) to tighten the bound on Q. We call R(S) a
maximum reuse and T (S) a minimum I/O of a CDAG.

4.2.2 Reuse-Based Lemma. We now use the above definitions
and observations to generalize the result of Hong and Kung [34].

Lemma 2. An optimal complete calculation of a CDAG G = (V , E),
which performs q I/O operations, is associated with an X -partition of
G such that

q ≥ (X − R(S) + T (S)) · (h − 1)
for any value of X ≥ S, where h is the number of subcomputations
in the X -partition, R(S) is the maximum reuse set size, and T (S) is
the minimum I/O in the given X -partition.

Proof. We use analogous reasoning as in the original lemma.
We associate the optimal pebbling with h consecutive subcompu-
with the difference that each subcomputation Vi
tations V1, . . . Vh
performs Y = X − R(S) + T (S) I/O operations. Within those Y
operations, we consider separately qi,s store and qi,l
load oper-
ations. For each Vi we have qi,s + qi,l
= Y , qi,s ≥ T (S), and
qi,l ≤ Y − T (S) = X − R(S).

∀i : |VB,i | ≤ ql,i ≤ Y − T (S)
∀i : |VR,i | ≤ qs,i ≤ R(S) ≤ S

Since VR,i ∪ VB,i = Dom(Vi ):

|Dom(Vi )| ≤ |VR,i | + |VB,i |
|Dom(Vi )| ≤ R(S) + Y − T (R) = X

By an analogous construction for store operations, we show
that |Min(Vi )| ≤ X . To show that S(X ) = {V1 . . . Vh } meets the
remaining properties of a valid X -partition S(X ), we use the same
reasoning as originally done [34].

Therefore, a complete calculation performing q > (X − R(S) +
T (S)) · (h − 1) I/O operations has an associated S(X ), such that
|S(X )| = h (if q = (X −R(S)+T (S))·(h −1), then |S(X )| = h −1). (cid:3)

From the previous lemma, we obtain a tighter I/O lower bound.

Lemma 3. Denote H (X ) as the minimum number of subcomputa-
tions in any valid X -partition of a CDAG G = (V , E), for any X ≥ S.
The minimal number Q of I/O operations for any valid execution of a
CDAG G = (V , E) is bounded by

Q ≥ (X − R(S) + T (S)) · (H (X ) − 1)

(2)

where R(S) is the maximum reuse set size and T (S) is the minimum
I/O set size. Moreover, we have

H (X ) ≥

|V |
|Vmax |

(3)

where Vmax = arg max
in the CDAG schedule S(X ) = {V1, . . . , Vh }.

Vi ∈S(X ) |Vi | is the largest subset of vertices

Proof. By definition, H (X ) = minS(X ) |S(X )| ≤ h, so Q ≥
(X − R(S) + T (S)) · (H (X ) − 1) immediately follows from Lemma 2.
To prove Eq. (3), observe that Vmax by definition is the largest
subset in the optimal X -partition. As the subsets are disjoint, any
other subset covers fewer remaining vertices to be pebbled than
Vmax . Because there are no cyclic dependencies between subsets,
we can order them topologically as V1, V2, ...VH (X ). To ensure that
the indices are correct, we also define V0 ≡ ∅. Now, define Wi to
be the set of vertices not included in any subset from 1 to i, that is
Wi = V − (cid:208)i
j=1 Vj . Clearly, W0 = V and WH (X ) = ∅. Then, we have

∀i

|Vi | ≤ |Vmax |

|Wi | = |Wi−1| − |Vi | ≥ |Wi−1| − |Vmax | ≥ |V | − i |Vmax |

|WH (X )| = 0 ≥ |V | − H (X ) · |Vmax |

that is, after H (X ) steps, we have H (X )|Vmax | ≥ |V |.

(cid:3)
From this lemma, we derive the following lemma that we use to

prove a tight I/O lower bound for MMM (Theorem 1):

Lemma 4. Define the number of computations performed by Vi for

one loaded element as the computational intensity ρi =
of the subcomputation Vi . Denote ρ = maxi (ρi ) ≤
to
be the maximal computational intensity. Then, the number of I/O
operations Q is bounded by Q ≥ |V |/ρ.

|Vi |
X − |VR, i |+|WB,i |
|Vmax |
X −R(S )+T (S )

Proof. Note that the term H (X ) − 1 in Equation 2 emerges from
a fact that the last subcomputation may execute less than Y −R(S) +
T (S) I/O operations, since |VH (X )| ≤ |Vmax |. However, because ρ
is defined as maximal computational intensity, then performing
|VH (S )| computations requires at least QH (S ) ≥ |VH (S )|/ρ. The total
number of I/O operations therefore is:

Q =

H (X )
(cid:213)

i=1

Qi ≥

H (X )
(cid:213)

i=1

|Vi |
ρ

=

|V |
ρ

(cid:3)

√

√

S/(

5 TIGHT I/O LOWER BOUNDS FOR MMM
In this section, we present our main theoretical contribution: a con-
structive proof of a tight I/O lower bound for classical matrix-matrix
multiplication. In § 6, we extend it to the parallel setup (Theorem 2).
S + 1 − 1)), and
This result is tight (up to diminishing factor
therefore may be seen as the last step in the long sequence of im-
proved bounds. Hong and Kung [34] derived an asymptotic bound
(cid:17) for the sequential case. Irony et al. [33] extended the
Ω
lower bound result to a parallel machine with p processes, each
having a fast private memory of size S, proving the
− S
lower bound on the communication volume per process. Recently,
Smith and van de Gein [48] proved a tight sequential lower bound
√
S − 2S. Our proof improves the
(up to an additive term) of 2mnk/
additive term and extends it to a parallel schedule.

√
S

n3
2p

(cid:16)
n

3/

√

√

S

4

Theorem 1 (Seqential Matrix Multiplication I/O lower
bound). Any pebbling of MMM CDAG which multiplies matrices of
sizes m × k and k × n by performing mnk multiplications requires a
minimum number of 2mnk√
S

+ mn I/O operations.

The proof of Theorem 1 requires Lemmas 5 and 6, which in turn,

require several definitions.

5

Technical Report, 2019,

G. Kwasniewski et al.

Intuition: Restricting the analysis to greedy schedules provides explicit infor-
mation of a state of memory (sets Vr , VR, r , WB,r ), and to a corresponding
CDAG pebbling. Additional constraints (§ 5.2.7) guarantee feasibility of a
derived schedule (and therefore, lower bound tightness).

5.1 Definitions

5.1.1 Vertices, Projections, and Edges in the MMM CDAG. The
set of vertices of MMM CDAG G = (V , E) consists of three subsets
V = A ∪ B ∪ C, which correspond to elements in matrices A, B, and
mnk partial sums of C. Each vertex v is defined uniquely by a pair
(M,T ), where M ∈ {a, b, c} determines to which subset A, B, C
vertex v belongs to, and T ∈ Nd is a vector of coordinates, d = 2 for
M = a ∨ b and d = 3 for M = c. E.g., v = (a, (1, 5)) ∈ A is a vertex
associated with element (1, 5) in matrix A, and v = (c, (3, 6, 8)) ∈ C
is associated with 8th partial sum of element (3, 6) of matrix C.

For every t3th partial update of element (t1, t2) in matrix C, and
an associated point v = (c, (t1, t2, t3)) ∈ C we define ϕc (v) = (t1, t2)
to be a projection of this point to matrix C, ϕa (v) = (a, (t1, t3)) ∈ A
is its projection to matrix A, and ϕb (v) = (b, (t3, t2)) ∈ B is its
projection to matrix B. Note that while ϕa (v), ϕb (v) ∈ V , projection
ϕc (v) (cid:60) V has not any associated point in V . Instead, vertices
associated with all k partial updates of an element of C have the
same projection ϕc (v):

v=(c,(p1,p2,p3)),w =(c,(q1,q2,q3))∈ C : (p1 = q1) ∧ (p2 = q2)
∀

⇐⇒ ϕc (p) = ϕc (q)

(4)

As a consequence, ϕc ((c, (t1, t2, t3))) = ϕc ((c, (t1, t2, t3 − 1))).
A t3th update of (t1, t2) element in matrix C of a classical MMM
is formulated as C(t1, t2, t3) = C(t1, t2, t3 − 1) + A(t1, t3) · B(t3, t2).
Therefore for each v = (c, (t1, t2, t3)) ∈ C, t3 > 1, we have following
edges in the CDAG: (ϕa (v), v), (ϕb (v), v), (c, (t1, t2, t3 − 1)), v) ∈ E.
5.1.2 α, β, γ, Γ. For a given subcomputation Vr ⊆ C, we denote
its projection to matrix A as αr = ϕa (Vr ) = {v : v = ϕa (c), c ∈ Vr },
its projection to matrix B as βr = ϕb (Vr ), and its projection to
matrix C as γr = ϕc (Vr ). We further define Γr ⊂ C as a set of
all vertices in C that have a child in Vr . The sets α, β, Γ therefore
correspond to the inputs of Vr that belong to matrices A, B, and
previous partial results of C, respectively. These inputs form a
minimal dominator set of Vr :

Dom(Vr ) = αr ∪ βr ∪ Γr

(5)

Because Min(Vr ) ⊂ C, and each vertex v ∈ C has at most one
child w with ϕc (v) = ϕc (w) (Equation 4), the projection ϕc (Min(Vr ))
is also equal to γr :

ϕc (Vr ) = ϕc (Γr ) = ϕc (Min(Vr )) = γr

(6)

5.1.3 Red(). Define Red(r ) as the set of all vertices that have
red pebbles just before subcomputation Vr starts, with Red(1) = ∅.
We further have Red(P), P ⊂ V is the set of all vertices in some
subset P that have red pebbles and Red(ϕc (P)) is a set of unique
pairs of first two coordinates of vertices in P that have red pebbles.
5.1.4 Greedy schedule. We call a schedule S = {V1, . . . , Vh }
greedy if during every subcomputation Vr every vertex u that will
hold a red pebble either has a child in Vr or belongs to Vr :

∀r : Red(r ) ⊂ αr −1 ∪ βr −1 ∪ Vr −1

(7)

6

5.2 I/O Optimality of Greedy Schedules

Lemma 5. Any greedy schedule that multiplies matrices of sizes
m × k and k × n using mnk multiplications requires a minimum
number of 2mnk√
S

+ mn I/O operations.

Proof. We start by creating an X -partition for an MMM CDAG
(the values of Y and R(S) are parameters that we determine in the
course of the proof). The proof is divided into the following 6 steps
(Sections 5.2.1 to 5.2.6).

5.2.1 Red Pebbles During and After Subcomputation. Observe
that each vertex in c = (t1, t2, t3) ∈ C, t1 = 1 . . . m, t2 = 1 . . . n, t3 =
1 . . . k − 1 has only one child c = (t1, t2, t3 + 1). Therefore, we
can assume that in an optimal schedule there are no two vertices
(t1, t2, t3), (t1, t2, t3 + f ) ∈ C, f ∈ N+ that simultaneously hold a
red vertex, as when the vertex (t1, t2, t3 + 1) is pebbled, a red pebble
can be immediately removed from (t1, t2, t3):

|Red(Vr )| = |ϕc (Red(Vr ))|
(8)
On the other hand, for every vertex v, if all its predecessors
Pred(v) have red pebbles, then vertex v may be immediately com-
puted, freeing a red pebble from its predecessor w ∈ C, due to the
fact, that v is the only child of w:

∀v ∈V ∀r : Pred(v) ⊂ Dom(Vr ) ∪ Vr =⇒ ∃t ≤r v ∈ Vt
Furthermore, after subcomputation Vr , all vertices in Vr that

(9)

have red pebbles are in its minimum set:

Red(r + 1) ∩ Vr = Red(r + 1) ∩ Min(Vr )
Combining this result with the definition of a greedy schedule

(10)

(Equation 7), we have

Red(r + 1) ⊆ αr ∪ βr ∪ Min(Vr )

(11)

5.2.2

Surface and volume of subcomputations. By the definition
of X -partition, the computation is divided into H (X ) subcomputa-
tions Vr ⊂ C, r ∈ {1, . . . H (X )}, such that Dom(Vr ), Min(Vr ) ≤ X .

Inserting Equations 5, 6, and 8, we have:

|Dom(Vr )| = |αr | + |βr | + |γr | ≤ X
|Min(Vr )| = |γr | ≤ X
On the other hand, the Loomis-Whitney inequality [41] bounds

(12)

the volume of Vr :

Vr ≤ (cid:112)|αr ||βr ||γr |
(13)
Consider sets of all different indices accessed by projections αr ,

βr , γr :

T1 = {t1,1, . . . , t1,a }, |T1| = a
T2 = {t2,1, . . . , t2,b }, |T2| = b
T3 = {t3,1, . . . , t3,c }, |T3| = c
αr ⊆ {(t1, t3) : t1 ∈ T1, t3 ∈ T3}
βr ⊆ {(t3, t2) : t3 ∈ T3, t2 ∈ T2}
γr ⊆ {(t1, t2) : t1 ∈ T1, t2 ∈ T2}
Vr ⊆ {(t1, t2, t3) : t1 ∈ T1, t2 ∈ T2, t3 ∈ T3}

(14)

(15)

(16)

(17)

I/O Optimal Parallel Matrix Multiplication

Technical Report, 2019,

For fixed sizes of the projections |αr |, |βr |, |γr |, then the volume
|Vr | is maximized when left and right side of Inequalities 14 to 16
are equal. Using 5 and 9 we have that 17 is an equality too, and:

|αr | = ac, |βr | = bc, |γr | = ab, |Vr | = abc,

(18)

achieving the upper bound (Equation 13).

5.2.3 Reuse set VR,r and store set WB,r . Consider two subse-
quent computations, Vr and Vr +1. After Vr , αr , βr , and Vr may
have red pebbles (Equation 7). On the other hand, for the domi-
nator set of Vr +1 we have |Dom(Vr +1)| = |αr +1| + |βr +1| + |γr +1|.
Then, the reuse set VR,i+1 is an intersection of those sets. Since
αr ∩ βr = αr ∩ γr = βr ∩ γr = ∅, we have (confront Equation 11):

(19)

VR,r +1 ⊆ (αr ∩ αr +1) ∪ (βr ∩ βr +1) ∪ (Min(Vr ) ∩ Γr +1)
|VR,r +1| ≤ |αr ∩ αr +1| + |βr ∩ βr +1| + |γr ∩ γr +1|
Note that vertices in αr and βr are inputs of the computation:
therefore, by the definition of the red-blue pebble game, they start
in the slow memory (they already have blue pebbles). Min(Vr ),
on the other hand, may have only red pebbles placed on them.
Furthermore, by the definition of the S-partition, these vertices
have children that have not been pebbled yet. They either have
to be reused forming the reuse set VR,r +1, or stored back, forming
WB,r and requiring the placement of the blue pebbles. Because
Min(Vr ) ∈ C and C ∩ A = C ∩ B = ∅, we have:

WB,r ⊆ Min(Vr ) \ Γr +1
|WB,r | ≤ |γr \ γr +1|

(20)

5.2.4 Overlapping computations. Consider two subcomputations
Vr and Vr +1. Denote shared parts of their projections as αs =
αr ∩ αr +1, βs = βr ∩ βr +1, and γs = γr ∩ γr +1. Then, there are two
possibilities:

(1) Vr and Vr +1 are not cubic, resulting in their volume smaller
than the upper bound |Vr +1| < (cid:112)|αr +1||βr +1||γr +1| (Equa-
tion 13),

again |Vr +1|

(Equation 9). Therefore,

(2) Vr and Vr +1 are cubic. If all overlapping projections are
not empty, then they generate an overlapping computa-
tion, that is, there exist vertices v, such that ϕik (v) ∈
αs , ϕk j (v) ∈ βs , ϕi j (v) ∈ γs . Because we consider greedy
schedules, those vertices cannot belong to computation
<
Vr +1
(cid:112)|αr +1||βr +1||γr +1|. Now consider sets of all different
indices accessed by those rectangular projections (Sec-
tion 5.2.2, Inequalities 14 to 16). Fixing two non-empty
projections we define all three sets T1,T2,T3, which in
turn, generate the third (non-empty) projection, result-
ing again in overlapping computations which reduce the
size of |Vr +1|. Therefore, for cubic subcomputations, their
volume is maximized |Vr +1| = (cid:112)|αr +1||βr +1||γr +1| if at
most one of the overlapping projections is non-empty (and
therefore, there is no overlapping computation).

maximize ρr =

|Vr |
X − R(S) + T (S)

≥

|Vr |
Dom(Vr ) − |VR,r | + |WB,r |

subject to:

|Dom(Vr )| ≤ X
|VR,r | ≤ S
To maximize the computational intensity, for a fixed number of
I/O operations, the subcomputation size |Vr | is maximized. Based
on Observation 5.2.4, it is maximized only if at most one of the
overlapping projections αr ∩αr +1, βr ∩ βr +1, γr ∩γr +1 is not empty.
Inserting Equations 13, 12, 19, and 20, we have the following three
equations for the computational intensity, depending on the non-
empty projection:

αr ∩ αr +1 (cid:44) ∅ :
(cid:112)|αr ||βr ||γr |
|αr | + |βr | + |γr | − |αr ∩ αr +1| + |γr |

βr ∩ βr +1 (cid:44) ∅ :
(cid:112)|αr ||βr ||γr |
|αr | + |βr | + |γr | − |βr ∩ βr +1| + |γr |

ρr =

ρr =

(21)

(22)

γr ∩ γr +1 (cid:44) ∅ :
(cid:112)|αr ||βr ||γr |
|αr | + |βr | + |γr | − |γr ∩ γr +1| + |γr \ γr +1|
ρr is maximized when γr = γr +1, γr ∩ γr +1 (cid:44) ∅, γr \ γr +1 = ∅

ρr =

(23)

(Equation 23).

Then, inserting Equations 18, we have:
maximize ρr = abc
ac + cb
subject to:
ab + ac + cb ≤ X
ab ≤ S
a, b, c ∈ N+,
where X is a free variable. Simple optimization technique using

Lagrange multipliers yields the result:

√

a = b = (cid:98)
√
|αr | = |βr | = (cid:98)
√
S(cid:99)2
|Vr | = (cid:98)

S(cid:99), c = 1,
S(cid:99), |γr | = (cid:98)
√
S(cid:99)2 + 2(cid:98)

√
S(cid:99)2
√

S(cid:99)

,

, X = (cid:98)
√

ρr =

(cid:98)

S(cid:99)
2

(24)

(25)

From now on, to keep the calculations simpler, we use assume

√

that

S ∈ N+.

5.2.6 MMM I/O complexity of greedy schedules. By the compu-

tational intensity corollary (cf. page 4 in the main paper):

Q ≥

|V |
ρ

=

2mnk
√
S

5.2.5 Maximizing computational intensity. Computational inten-
sity ρr of a subcomputation Vr is an upper bound on ratio between
its size |Vr | and the number of I/O operations required. The number
of I/O operations is minimized when ρ is maximized (Lemma 4):

This is the I/O cost of putting a red pebble at least once on every
vertex in C. Note however, that we did not put any blue pebbles
on the outputs yet (all vertices in C had only red pebbles placed
on them during the execution). By the definition of the red-blue

7

Technical Report, 2019,

G. Kwasniewski et al.

pebble game, we need to place blue pebbles on mn output vertices,
corresponding to the output matrix C, resulting in additional mn
I/O operations, yielding final bound

The solution to this problem is

Q ≥

2mnk
√
S

+ mn

(cid:3)

bopt =

(cid:113)








2 S +
(cid:113)

<








2 − 1

(S − 1)3 − S + 1
S − 2

(cid:113)

(S − 1)3 − S

(S − 1)3 − S + 1

√
S

√
S

<









(27)

(28)

aopt =

−









(cid:25)

(cid:109)

1 for i1 = 1 : (cid:108) m
aopt
(cid:24)
n
bopt

for j1 = 1 :

2

for r = 1 : k

3
4
5
6

for i2 = i1 · T : min((i1 + 1) · aopt , m)

for j2 = j1 · T : min((j1 + 1) · bopt , n)

C(i2, j2) = C(i2, j2) + A(i2, r ) · B(r, j2)

Listing 1: Pseudocode of near optimal sequential MMM

5.3 Greedy vs Non-greedy Schedules
In § 5.2.6, it is shown that the I/O lower bound for any greedy sched-
ule is Q ≥ 2mnk√
+ mn. Furthermore, Listing 1 provide a schedule
S
that attains this lower bound (up to a aopt bopt /S factor). To prove
that this bound applies to any schedule, we need to show, that any
non-greedy cannot perform better (perform less I/O operations)
than the greedy schedule lower bound.

Lemma 6. Any non-greedy schedule computing classical matrix

+ mn I/O operations.

multiplication performs at least 2mnk√
S
Proof. Lemma 3 applies to any schedule and for any value of
X . Clearly, for any general schedule we cannot directly model
VR,i , VB,i , WR,i , and WB,i , and therefore T (S) and R(S). However,
it is always true that 0 ≤ T (S) and R(S) ≤ S. Also, the dominator
set formed in Equation 5 applies for any subcomputation, as well
as a bound on |Vr | from Inequality 13. We can then rewrite the
computational intensity maximization problem:

maximize ρr =

(cid:112)|αr ||βr ||γr |
|αr | + |βr | + |γr | − S

≤

|Vr |
X − R(S) + T (S)
subject to:
S < |αr | + |βr | + |γr | = X

(29)

This is maximized for |αr | = |βr | = |γr | = X /3, yielding

(X /3)3/2
X − S
Because mnk/ρr is a valid lower bound for any X > S (Lemma 4),
we want to find such value Xopt for which ρr is minimal, yielding
the highest (tightest) lower bound on Q:

ρr =

minimize ρr =

subject to:

(X /3)3/2
X − S

(26)

8

X ≥ S

(30)

5.2.7 Attainability of the Lower Bound. Restricting the analysis
to greedy schedules provides explicit information of a state of mem-
ory (sets Vr , VR,r , WB,r ), and therefore, to a corresponding CDAG
pebbling. In Section 5.2.5, it is proven that an optimal greedy sched-
ule is composed of mnk
outer product calculations, while loading
R(S )
(cid:112)R(S) elements of each of matrices A and B. While the lower bound
is achieved for R(S) = S, such a schedule is infeasible, as at least
some additional red pebbles, except the ones placed on the reuse
set VR,r , have to be placed on 2(cid:112)R(S) vertices of A and B.

A direct way to obtain a feasible greedy schedule is to set X = S,
ensuring that the dominator set can fit into the memory. Then each
subcomputation is an outer-product of column-vector of matrix
S + 1 − 1 values. Such a
A and row-vector of B, both holding
schedule performs 2mnk
√
S +1−1
S +1−1
more than a lower bound, which quickly approach 1 for large S.
Listing 1 provides a pseudocode of this algorithm, which is a well-
known rank-1 update formulation of MMM. However, we can do
better.

+ mn I/O operations, a factor of

√
S√

√

Let’s consider a generalized case of such subcomputation Vr .

Assume, that in each step:

(1) a elements of A (forming αr ) are loaded,
(2) b elements of B (forming βr ) are loaded,
(3) ab partial results of C are kept in the fast memory (forming

Γr )

(4) ab values of C are updated (forming Vr ),
(5) no store operations are performed.

Each vertex in αr has b children in Vr (each of which has also a
parent in βr ). Similarly, each vertex in βr has a children in Vr ,
each of which has also a parent in αr . We first note, that ab < S
(otherwise, we cannot do any computation while keeping all ab
partial results in fast memory). Any red vertex placed on αr should
not be removed from it until all b children are pebbled, requiring
red-pebbling of corresponding b vertices from βr . But, in turn, any
red pebble placed on a vertex in βr should not be removed until all
a children are red pebbled.

Therefore, either all a vertices in αr , or all b vertices in βr have
to be hold red pebbles at the same time, while at least one additional
red pebble is needed on βr (or αr ). W.l.o.g., assume we keep red
pebbles on all vertices of αr . We then have:

maximize ρr = ab
a + b
subject to:
ab + a + 1 ≤ S
a, b ∈ N+,

I/O Optimal Parallel Matrix Multiplication

Technical Report, 2019,

which, in turn, is minimized for X = 3S. This again shows, that
the upper bound on maximum computational intensity for any
S/2, which matches the bound for greedy schedules
schedule is
(cid:3)
(Equation 25).

√

We note that Smith and van de Gein [48] in their paper also
bounded the number of computations (interpreted geometrically
as a subset in a 3D space) by its surface and obtained an analo-
gous result for this surface (here, a dominator and minimum set
sizes). However, using computational intensity lemma, our bound
is tighter by 2S (+mn, counting storing the final result).
Proof of Theorem 1:
Lemma 5 establishes that the I/O lower bound for any greedy sched-
S + mn. Lemma 6 establishes that no other
ule is Q = 2mnk/
schedule can perform less I/O operations.

√

(cid:3)

√
S√

Corollary: The greedy schedule associated with an X = S-partition

performs at most
more I/O operations than a lower bound.
The optimal greedy schedule is associated with an X = aopt bopt +
aopt + bopt -partition and performs
I/O operations.

S +1−1

S (aopt +bopt )
aopt bopt

√

6 OPTIMAL PARALLEL MMM
We now derive the schedule of COSMA from the results from § 5.2.7.
The key notion is the data reuse, that determines not only the se-
quential execution, as discussed in § 4.2 , but also the parallel
scheduling. Specifically, if the data reuse set spans across multiple
local domains, then this set has to be communicated between these
domains, increasing the I/O cost (Figure 3). We first introduce a
formalism required to parallelize the sequential schedule (§ 6.1).
In § 6.2, we generalize parallelization strategies used by the 2D,
2.5D, and recursive decompositions, deriving their communication
cost and showing that none of them is optimal in the whole range
of parameters. We finally derive the optimal decomposition (Find-
OptimalDomain function in Algorithm 1) by expressing it as an
optimization problem (§ 6.3), and analyzing its I/O and latency cost.
The remaining steps in Algorithm 1: FitRanks, GetDataDecomp, as
well as DistrData and Reduce are discussed in § 7.1, § 7.6, and § 7.2,
respectively. For a distributed machine, we assume that all matrices
fit into collective memories of all processors: pS ≥ mn + mk + nk.
For a shared memory setting, we assume that all inputs start in a
common slow memory.

6.1 Sequential and Parallel Schedules
We now describe how a parallel schedule is formed from a sequential
one. The sequential schedule S partitions the CDAG G = (V , E)
into H (S) subcomputations Vi . The parallel schedule P divides S
among p processors: P = {D1, . . . Dp }, (cid:208)p
j=1 Dj = S. The set Dj
assigned to processor j forms a local domain of j (Fig. 4c).
of all Vk
are dependent, that is,
∃u, ∃v : u ∈ Dk ∧ v ∈ Dl ∧ (u, v) ∈ E, then u has to be com-
municated from processor k to l. The total number of vertices com-
municated between all processors is the I/O cost Q of schedule P.
We say that the parallel schedule Popt is communication–optimal
if Q(Popt ) is minimal among all possible parallel schedules.

If two local domains Dk

and Dl

The vertices of MMM CDAG may be arranged in an [m × n × k]
3D grid called an iteration space [59]. The orthonormal vectors i, j, k
correspond to the loops in Lines 1-3 in Listing 1 (Figure 3a). We call

9

Figure 4: (a) An MMM CDAG as a 3D grid (iteration space). Each vertex in it (except
for the vertices in the bottom layer) has three parents - blue (matrix A), red (matrix B),
and yellow (partial result of matrix C) and one yellow child (except for vertices in the
top layer). (b) A union of inputs of all vertices in Vi form the dominator set Dom(Vi )
(two blue, two red and four dark yellow). Using approximation
S ,
we have |Dom(Vi,opt )| = S . (c) A local domain D consists of b subcomputations
Vi , each of a dominator size |Dom(Vi )| = a2 + 2a. (d-f) Different parallelization
schemes of near optimal sequential MMM for p = 24 > p1 = 6.

S + 1 − 1 ≈

√

√

a schedule P parallelized in dimension d if we “cut” the CDAG along
dimension d. More formally, each local domain Dj , j = 1 . . . p is a
grid of size either [m/p, n, k], [m, n/p, k], or [m, n, k/p]. The sched-
ule may also be parallelized in two dimensions (d1d2) or three di-
mensions (d1d2d3) with a local domain size [m/pm, n/pn, k/pk ] for
= p. We call G = [pm, pn, pk ]
some pm, pn, pk
the processor grid of a schedule. E.g., Cannon’s algorithm is par-
allelized in dimensions ij , with the processor grid [
p, 1].
COSMA, on the other hand, may use any of the possible paral-
lelizations, depending on the problem parameters.

, such that pmpnpk

p,

√

√

√

√

S ×

6.2 Parallelization Strategies for MMM
The sequential schedule S (§ 5) consists of mnk/S elementary outer
product calculations, arranged in
S × k “blocks” (Figure 4).
The number p1 = mn/S of dependency-free subcomputations Vi
(i.e., having no parents except for input vertices) in S determines
the maximum degree of parallelism of Popt for which no reuse set
VR,i crosses two local domains Dj , Dk
. The optimal schedule is par-
allelized in dimensions ij. There is no communication between the
domains (except for inputs and outputs), and all I/O operations are
performed inside each Dj following the sequential schedule. Each
processor is assigned to p1/p local domains Dj of size (cid:2)√
√
S, k(cid:3),
S,
Sk + S I/O operations (Theorem 1), giving
S) + mn/p I/O operations per processor.
When p > p1, the size of local domains |Dj | is smaller than
S × k. Then, the schedule has to either be parallelized in
S ×
dimension k, or has to reduce the size of the domain in ij plane.
The former option creates dependencies between the local domains,
which results in additional communication (Figure 4e). The latter
does not utilize the whole available memory, making the sequen-
tial schedule not I/O optimal and decreasing the computational
intensity ρ (Figure 4d). We now analyze three possible paralleliza-
tion strategies (Figure 4) which generalize 2D, 2.5D, and recursive
decomposition strategies; see Table 3 for details.

√
each of which requires 2
√
a total of Q = 2mnk/(p

√

√

Schedule Pi j The schedule is parallelized in dimensions i and j.
The processor grid is Gi j = (cid:2) m
. Because all
dependencies are parallel to dimension k, there are no dependencies
√
S,
between Dj except for the inputs and the outputs. Because a <

a , 1(cid:3), where a = (cid:113) mn

a , n

p

Crossing dependencies!Crossing dependencies!(d)(e)(f)(a) MMM CDAG(b) Optimal ijkmatrix Amatrix B3D itera�on spacematrix C(c) Local domainoutput size: input size: elementselementselementsTechnical Report, 2019,

G. Kwasniewski et al.

√

S/2.

the corresponding sequential schedule has a reduced computational
intensity ρi j <

Schedule Pi jk

The schedule is parallelized in all dimensions.
(cid:3). The computational in-

, pS
The processor grid is Gi jk
mn
=
tensity ρi jk
S/2 is optimal. The parallelization in k dimension
creates dependencies between local domains, requiring communi-
cation and increasing the I/O cost.

= (cid:2) m√
S

, n√
S

√

,

p

√

(cid:1)1/3

, k
ac

(cid:113) S
3

(cid:3), where ac = min (cid:110) (cid:0) mnk

Schedule Pcubic
, n
ac

The schedule is parallelized in all dimensions.
(cid:111). Be-
The grid is (cid:2) m
ac
√
S, the corresponding computational intensity ρcubic
cause ac <
S/2 is not optimal. The parallelization in k dimension creates
<
dependencies between local domains, increasing communication.
Schedules of the State-of-the-Art Decompositions If m = n,
the Pi j scheme is reduced to the classical 2D decomposition (e.g.,
is reduced to the 2.5D decompo-
Cannon’s algorithm [10]), and Pi jk
sition [53]. CARMA [22] asymptotically reaches the Pcubic
scheme,
guaranteeing that the longest dimension of a local cuboidal domain
is at most two times larger than the smallest one. We present
a detailed complexity analysis comparison for all algorithms in
Table 3.

6.3 I/O Optimal Parallel Schedule
Observe that none of those schedules is optimal in the whole range
of parameters. As discussed in § 5, in sequential scheduling, interme-
diate results of C are not stored to the memory: they are consumed
(reused) immediately by the next sequential step. Only the final re-
sult of C in the local domain is sent. Therefore, the optimal parallel
schedule Popt minimizes the communication, that is, sum of the in-
puts’ sizes plus the output size, under the sequential I/O constraint
on subcomputations ∀Vi ∈Dj ∈ Popt
|Dom(Vi )| ≤ S ∧ |Min(Vi )| ≤ S.
The local domain Dj is a grid of size [a × a × b], containing b
outer products of vectors of length a. The optimization problem
of finding Popt using the computational intensity (Lemma 4) is
formulated as follows:

maximize ρ =

2

a
b
ab + ab + a2

subject to:
2 ≤ S (the I/O constraint)

(the load balance constraint)

a
b = mnk
p

2

a

pS ≥ mn + mk + nk (matrices must fit into memory)

2 ≤ S is binding (changes to equality) for

The I/O constraint a
p ≤ mnk

S 3/2 . Therefore, the solution to this problem is:
a = min (cid:110)√
(cid:17)1/3(cid:111)
(cid:16)mnk
S,
p

, b = max (cid:110)mnk
pS

(cid:16)mnk
p

,

(cid:17)1/3(cid:111)

(32)

The I/O complexity of this schedule is:

Q ≥

2

a
b
ρ

= min (cid:110) 2mnk
√
S

+ S, 3(cid:16)mnk
p

(cid:17) 2
3 (cid:111)

(33)

p
This can be intuitively interpreted geometrically as follows: if we
imagine the optimal local domain ”growing” with the decreasing
number of processors, then it stays cubic as long as it is still ”small
S). After that point, its face in
enough” (its side is smaller than

√

√

√

the ij plane stays constant
dimension. This schedule effectively switches from Pi jk
once there is enough memory (S ≥ (mnk/p)2/3).

S and it ”grows” only in the k
to Pcubic

S ×

Theorem 2. The I/O complexity of a classic Matrix Multiplication
algorithm executed on p processors, each of local memory size S ≥
mn+mk+nk
p

is

Q ≥ min (cid:110) 2mnk
√
S

p

+ S, 3(cid:16)mnk
p

(cid:17) 2
3 (cid:111)

Proof. The theorem is a direct consequence of Lemma 3 and
the computational intensity (Lemma 4). The load balance constraint
enforces a size of each local domain |Dj | = mnk/p. The I/O cost
is then bounded by |Dj |/ρ. Schedule Popt maximizes ρ by the
(cid:3)
formulation of the optimization problem (Equation 31).
I/O-Latency Trade-off As showed in this section, the local
domain D of the near optimal schedule P is a grid of size [a ×a ×b],
where a, b are given by Equation (32). The corresponding sequential
schedule S is a sequence of b outer products of vectors of length
a. Denote the size of the communicated inputs in each step by
Ist ep = 2a. This corresponds to b steps of communication (the
latency cost is L = b).

The number of steps (latency) is equal to the total communication
volume of D divided by the volume per step L = Q/Ist ep . To reduce
the latency, one either has to decrease Q or increase Ist ep , under the
2 ≤ S (otherwise we cannot fit both
memory constraint that Ist ep +a
the inputs and the outputs in the memory). Express Ist ep = a · h,
where h is the number of sequential subcomputations Vi we merge
in one communication. We can express the I/O-latency trade-off:

min(Q, L)
subject to:

(31)

2

a

(load balance constraint)

Q = 2ab + a

2

, L = b
h

2 + 2ah ≤ S (I/O constraint)

a
b = mnk
p

√

+ a

2 and L = 2mnk
Solving this problem, we have Q = 2mnk
pa(S −a2)
pa
S. Increasing a we reduce the I/O cost Q and increase
where a ≤
the latency cost L. For minimal value of Q (Theorem 2), L = (cid:108) 2ab
(cid:109),
S −a2
pS , (mnk/p)1/3}.
where a = min{
Based on our experiments, we observe that the I/O cost is vastly
greater than the latency cost, therefore our schedule by default
minimizes Q and uses extra memory (if any) to reduce L.

√
S, (mnk/p)1/3} and b = max{ mnk

,

7 IMPLEMENTATION
We now present implementation optimizations that further increase
the performance of COSMA on top of the speedup due to our near
I/O optimal schedule. The algorithm is designed to facilitate the
overlap of communication and computation § 7.3. For this, to
leverage the RDMA mechanisms of current high-speed network
interfaces, we use the MPI one-sided interface § 7.4. In addition, our
implementation also offers alternative efficient two-sided commu-
nication back end that uses MPI collectives. We also use a blocked

10

I/O Optimal Parallel Matrix Multiplication

Technical Report, 2019,

Decomposition
Parallel schedule P

grid [pm × pn × pk ]

domain size

2D [56]
Pi j for m = n
√
(cid:2)√
p × 1(cid:3)
(cid:105)

p ×

× n√
p

× k

(cid:104) m√

p

2.5D [53]
Pi jk for m = n
(cid:104)(cid:112)p/c × (cid:112)p/c × c
(cid:20)

m√

p/c

× n√

p/c

× k
c

(cid:105)

recursive [22]
Pcubic

pS
mk +nk

; c =
(cid:21)

[2a1 × 2a2 × 2a3 ]; a1 + a2 + a3 = log2(p)
(cid:104) m
2a1 × n

2a1 × k
2a1

(cid:105)

COSMA (this paper)
Popt

(cid:3); a, b : Equation 32

(cid:2) m
a × k
a × n
b
[a × a × b]

I/O cost Q

latency cost L

k√
p

(m + n) + mn
p

2k log2 (

√

p)

I/O cost Q

latency cost L

√

2n2(
2k log2 (

p + 1)/p
√

I/O cost

latency cost L

p3/2/2
p 3/2 log2 (

p)/4

“General case”:

(cid:17)

(cid:16)

√

5/2

3/2

k (m+n)

+ mnS

(cid:16) mnk
p

2 min (cid:110)√
(cid:16)33/2mnk

+ 3 log2

pS
mk +nk

(k (m+n))
p
S
(k (m+n))
3/2(km+k n−mn)

3 mnk
,
√
S
p
pS 3/2(cid:17) + 3 log2(p)
(cid:16)
(cid:17)
/
pS
Square matrices, “limited memory”: m = n = k, S = 2n2/p, p = 23n
2n2(
√

2n2 (cid:16)(cid:112)3/2p + 1/2p2/3(cid:17)
(cid:0) 3
p log2(p)
p)
2
“Tall” matrices, “extra” memory available: m = n = √
3p/4
1

p4/3/2 + p1/3
1

p + 1)/p

(cid:1) 3/2 √

√

p

√

p, k = p3/2/4, S = 2nk/p2/3, p = 23n+1

√

p + 1)/p

2n2(
√

p log2(p)

(cid:16)3 − 21/3(cid:17)

/24/3 ≈ 0.69p

p
1

(cid:17) 2/3 (cid:111) + (cid:16) mnk

p

(cid:17) 2/3

(cid:17) 2/3 (cid:111)

√

min (cid:110) 2mnk
p
S
2 log2

2ab
S −a

+ S, 3 (cid:16) mnk
(cid:16) mn
2
a

(cid:17)

p

Table 3: The comparison of complexities of 2D, 2.5D, recursive, and COSMA algorithms. The 3D decomposition is a special case of 2.5D, and can be obtained by instantiating
c = p1/3 in the 2.5D case. In addition to the general analysis, we show two special cases. If the matrices are square and there is no extra memory available, 2D, 2.5D and COSMA
achieves tight communication lower bound 2n2/
3 times more communication. If one dimension is much larger than the others and there is extra
memory available, 2D, 2.5D and CARMA decompositions perform O(p1/2), O(p1/3), and 8% more communication than COSMA, respectively. For simplicity, we assume that
parameters are chosen such that all divisions have integer results.

p, whereas CARMA performs

√

√

(a) 1 × 5 × 13 grid

(b) 4 × 4 × 4 grid with one idle processor

Figure 5: Processor decomposition for square matrices and 65 processors. (a) To utilize
all resources, the local domain is drastically stretched. (b) Dropping one processor
results in a symmetric grid which increases the computation per processor by 1.5%,
but reduces the communication by 36%.

data layout § 7.6, a grid-fitting technique § 7.1, and an optimized
binary broadcast tree using static information about the communi-
cation pattern (§ 7.2) together with the buffer swapping (§ 7.5). For
the local matrix operations, we use BLAS routines for highest per-
formance. Our code is publicly available at https://github.com/eth-
cscs/COSMA.

7.1 Processor Grid Optimization
Throughout the paper, we assume all operations required to assess
the decomposition (divisions, roots) result in natural numbers. We
note that in practice it is rarely the case, as the parameters usually
emerge from external constraints, like a specification of a performed
calculation or hardware resources (§ 8). If matrix dimensions are
not divisible by the local domain sizes a, b (Equation 32), then a
straightforward option is to use the floor function, not utilizing the
“boundary” processors whose local domains do not fit entirely in
the iteration space, which result in more computation per proces-
sor. The other option is to find factors of p and then construct the
processor grid by matching the largest factors with largest matrix di-
mensions. However, if the factors of p do not match m, n, and k, this
may result in a suboptimal decomposition. Our algorithm allows
to not utilize some processors (increasing the computation volume
per processor) to optimize the grid, which reduces the communi-
cation volume. Figure 5 illustrates the comparison between these

options. We balance this communication–computation trade-off by
”stretching” the local domain size derived in § 6.3 to fit the global
domain by adjusting its width, height, and length. The range of this
tuning (how many processors we drop to reduce communication)
depends on the hardware specification of the machine (peak flop/s,
memory and network bandwidth). For our experiments on the Piz
Daint machine we chose the maximal number of unutilized cores
to be 3%, accounting for up to 2.4 times speedup for the square
matrices using 2,198 cores (§ 9).

7.2 Enhanced Communication Pattern
As shown in Algorithm 1, COSMA by default executes in t = 2ab
S −a2
2)/2
rounds. In each round, each processor receives s = ab/t = (S −a
elements of A and B. Thus, the input matrices are broadcast among
the i and j dimensions of the processor grid. After the last round,
the partial results of C are reduced among the k dimension. The
communication pattern is therefore similar to ScaLAPACK or CTF.
To accelerate the collective communication, we implement our
own binary broadcast tree, taking advantage of the known data lay-
out, processor grid, and communication pattern. Knowing the initial
data layout § 7.6 and the processor grid § 7.1, we craft the binary
reduction tree in all three dimensions i, j, and k such that the dis-
tance in the grid between communicating processors is minimized.
Our implementation outperforms the standard MPI broadcast from
the Cray-MPICH 3.1 library by approximately 10%.

7.3 Communication–Computation Overlap
The sequential rounds of the algorithm ti = 1, . . . , t, naturally
express communication–computation overlap. Using double buffer-
ing, at each round ti we issue an asynchronous communication
(using either MPI Get or MPI Isend / MPI Irecv § 7.4) of the data
required at round ti+1, while locally processing the data received
in a previous round. We note that, by the construction of the local
domains Dj § 6.3, the extra memory required for double buffering
is rarely an issue. If we are constrained by the available memory,
2,
then the space required to hold the partial results of C, which is a

11

singleidle processTechnical Report, 2019,

G. Kwasniewski et al.

is much larger than the size of the receive buffers s = (S − a
not, then there is extra memory available for the buffering.

2)/2. If

Number of rounds: The minimum number of rounds, and
therefore latency, is t = 2ab
S −a2 (§ 6.3) . However, to exploit more
overlap, we can increase the number of rounds t2 > t. In this way,
in one round we communicate less data s2 = ab/t2 < s, allowing
the first round of computation to start earlier.

7.4 One-Sided vs Two-Sided Communication
To reduce the latency [27] we implemented communication using
MPI RMA [32]. This interface utilizes the underlying features of
Remote Direct Memory Access (RDMA) mechanism, bypassing the
OS on the sender side and providing zero-copy communication:
data sent is not buffered in a temporary address, instead, it is written
directly to its location.

All

communication windows

are pre-allocated using
MPI Win allocate with the size of maximum message in the broad-
cast tree 2s−1
D (§ 7.2). Communication in each step is performed
using the MPI Get and MPI Accumulate routines.

For compatibility reasons, as well as for the performance com-
parison, we also implemented a communication back-end using
MPI two-sided (the message passing abstraction).

7.5 Communication Buffer Optimization
The binary broadcast tree pattern is a generalization of the recursive
structure of CARMA. However, CARMA in each recursive step
dynamically allocates new buffers of the increasing size to match
the message sizes 2s−1
D, causing an additional runtime overhead.
To alleviate this problem, we pre-allocate initial, send, and re-
ceive buffers for each of matrices A, B, and C of the maximum size
of the message ab/t, where t = 2ab
S −a2 is the number of steps in
COSMA (Algorithm 1). Then, in each level s of the communication
tree, we move the pointer in the receive buffer by 2s−1
D elements.

and Bl, j

7.6 Blocked Data Layout
COSMA’s schedule induces the optimal initial data layout, since
for each Dj it determines its dominator set Dom(Dj ), that is, el-
ements accessed by processor j. Denote Al, j
subsets of
elements of matrices A and B that initially reside in the local mem-
ory of processor j. The optimal data layout therefore requires that
Al, j , Bl, j ⊂ Dom(Dj ). However, the schedule does not specify ex-
actly which elements of Dom(Dj ) should be in Al, j
. As a
consequence of the communication pattern § 7.2, each element of
is communicated to дm , дn processors, respectively.
Al, j
To prevent data reshuffling, we therefore split each of Dom(Dj )
into дm and дn smaller blocks, enforcing that consecutive blocks
are assigned to processors that communicate first. This is unlike the
distributed CARMA implementation [22], which uses the cyclic dis-
tribution among processors in the recursion base case and requires
local data reshuffling after each communication round. Another
advantage of our blocked data layout is a full compatibility with
the block-cyclic one, which is used in other linear-algebra libraries.

and Bl, j

and Bl, j

scenarios include both synthetic square matrices, in which all algo-
rithms achieve their peak performance, as well as “flat” (two large
dimensions) and real-world “tall-and-skinny” (one large dimension)
cases with uneven number of processors.

Comparison Targets
As a comparison, we use the widely used ScaLAPACK library as
provided by Intel MKL (version: 18.0.2.199)3, as well as Cyclops
Tensor Framework4, and the original CARMA implementation5.
We manually tune ScaLAPACK parameters to achieve its maximum
performance. Our experiments showed that on Piz Daint it achieves
the highest performance when run with 4 MPI ranks per compute
node, 9 cores per rank. Therefore, for each matrix sizes/node count
configuration, we recompute the optimal rank decomposition for
ScaLAPACK. Remaining implementations use default decomposi-
tion strategy and perform best utilizing 36 ranks per node, 1 core
per rank.

Infrastructure and Implementation Details
All implementations were compiled using the GCC 6.2.0 compiler.
We use Cray-MPICH 3.1 implementation of MPI. The parallelism
within a rank of ScaLAPACK6 is handled internally by the MKL
BLAS (with GNU OpenMP threading) version 2017.4.196. To profile
MPI communication volume, we use the mpiP version 3.4.1 [57].

Experimental Setup and Architectures
We run our experiments on the CPU partition of CSCS Piz Daint,
which has 1,813 XC40 nodes with dual-socket Intel Xeon E5-2695
v4 processors (2 · 18 cores, 3.30 GHz, 45 MiB L3 shared cache, 64
GiB DDR3 RAM), interconnected by the Cray Aries network with
a dragonfly network topology. We set p to a number of available
cores7 and S to the main memory size per core (§ 2.1). To addition-
ally capture cache size per core, the model can be extended to a
three-level memory hierarchy. However, cache-size tiling is already
handled internally by the MKL.

Matrix Dimensions and Number of Cores
We use square (m = n = k), “largeK” (m = n (cid:28) k), “largeM” (m (cid:29)
n = k), and “flat” (m = n (cid:29) k) matrices. The matrix dimensions and
number of cores are (1) powers of two m = 2r1 , n = 2r2 , m = 2r3 , (2)
determined by the real-life simulations or hardware architecture
3 + 1.
(available nodes on a computer), (3) chosen adversarially, e.g, n
Tall matrix dimensions are taken from an application benchmark,
namely the calculation of the random phase approximation (RPA)
energy of water molecules [21]. There, to simulate w molecules,
2. In the
the sizes of the matrices are m = n = 136w and k = 228w
strong scaling scenario, we use w = 128 as in the original paper,
yielding m = n = 17,408, k = 3,735,552. For performance runs, we
scale up to 512 nodes (18,432 cores).

Selection of Benchmarks
We perform both strong scaling and memory scaling experiments.
The memory scaling scenario fixes the input size per core ( pS
, I =
I
mn + mk + nk), as opposed to the work per core ( mnk
(cid:44) const).
p

8 EVALUATION
We evaluate COSMA’s communication volume and performance
against other state-of-the-art implementations with various com-
binations of matrix dimensions and memory requirements. These

3the latest version available on Piz Daint when benchmarks were performed (August
2018). No improvements of P[S,D,C,Z]GEMM have been reported in the MKL release
notes since then.
4https://github.com/cyclops-community/ctf, commit ID 244561c on May 15, 2018
5https://github.com/lipshitz/CAPS, commit ID 7589212 on July 19, 2013
6only ScaLAPACK uses multiple cores per ranks
7for ScaLAPACK, actual number of MPI ranks is p/9

12

I/O Optimal Parallel Matrix Multiplication

Technical Report, 2019,

= const), and (2)

performance, compared to ¡5% of CTF and ScaLAPACK, showing
excellent strong scaling characteristics.

We evaluate two cases: (1) ”limited memory” ( pS
I
”extra memory” ( p2/3S

= const).

I

To provide more information about the impact of communication
optimizations on the total runtime, for each of the matrix shapes we
also separately measure time spent by COSMA on different parts
of the code. for each matrix shape we present two extreme cases of
strong scaling - with smallest number of processors (most compute-
intense) and with the largest (most communication-intense). To
additionally increase information provided, we perform these mea-
surements with and without communication–computation overlap.

Programming Models
We use either the RMA or the Message Passing models. CTF also
uses both models, whereas CARMA and ScaLAPACK use MPI two-
sided (Message Passing).

Experimentation Methodology
For each combination of parameters, we perform 5 runs, each with
different node allocation. As all the algorithms use BLAS routines
for local matrix computations, for each run we execute the kernels
three times and take the minimum to compensate for the BLAS
setup overhead. We report median and 95% confidence intervals of
the runtimes.

9 RESULTS
We now present the experimental results comparing COSMA with
the existing algorithms. For both strong and memory scaling, we
measure total communication volume and runtime on both square
and tall matrices. Our experiments show that COSMA always
communicates least data and is the fastest in all scenarios.

Summary and Overall Speedups
As discussed in § 8, we evaluate three benchmarks – strong scaling,
“limited memory” (no redundant copies of the input are possible),
1/3 extra copies of the input can fit into
and “extra memory” (p
combined memory of all cores). Each of them we test for square,
“largeK”, “largeM”, and , “flat” matrices, giving twelve cases in total.
In Table 4, we present arithmetic mean of total communication
volume per MPI rank across all core counts. We also report the
summary of minimum, geometric mean, and maximum speedups
vs the second best-performing algorithm.

√

√

S/(

Communication Volume
As analyzed in § 5 and § 6, COSMA reaches I/O lower bound (up to
S + 1 − 1)). Moreover, optimizations presented
the factor of
in § 7 secure further improvements compared to other state-of-the-
art algorithms. In all cases, COSMA performs least communication.
Total communication volume for square and “largeK” scenarios is
shown in Figures 6 and 10.

Square Matrices
Figure 8 presents the % of achieved peak hardware performance for
square matrices in all three scenarios. As COSMA is based on the
near optimal schedule, it achieves the highest performance in all
cases. Moreover, its performance pattern is the most stable: when
the number of cores is not a power of two, the performance does
not vary much compared to all remaining three implementations.
We note that matrix dimensions in the strong scaling scenarios
(m = n = k = 214) are very small for distributed setting. Yet
even in this case COSMA maintains relatively high performance
for large numbers of cores: using 4k cores it achieves 35% of peak

13

Tall and Skinny Matrices
Figure 10 presents the results for “largeK” matrices - due to space
constraints, the symmetric “largeM” case is For strong scaling,
the minimum number of cores is 2048 (otherwise, the matrices of
size m = n =17,408, k =3,735,552 do not fit into memory). Again,
COSMA shows the most stable performance with a varying number
of cores.

“Flat” Matrices
Matrix dimensions for strong scaling are set to m = n = 217 =131,072
and k = 29 =512. Our weak scaling scenario models the rank-k
update kernel, with fixed k =256, and m = n scaling accordingly
for the “limited” and “extra” memory cases. Such kernels take
most of the execution time in, e.g., matrix factorization algorithms,
where updating Schur complements is performed as a rank-k gemm
operation [31].

Unfavorable Number of Processors
Due to the processor grid optimization (§ 7.1), the performance
is stable and does not suffer from unfavorable combinations of
parameters. E.g., the runtime of COSMA for square matrices m =
n = k =16,384 on p1 =9,216= 210 · 32 cores is 142 ms. Adding an
extra core (p2 =9,217= 13 · 709), does not change COSMA’s runtime,
as the optimal decomposition does not utilize it. On the other hand,
CTF for p1 runs in 600 ms, while for p2 the runtime increases to
1613 ms due to a non-optimal processor decomposition.

Communication-Computation Breakdown
In Figure 12 we present the total runtime breakdown of COSMA
into communication and computation routines. Combined

with the comparison of communication volumes (Figures 6 and 7,
Table 4) we see the importance of our I/O optimizations for dis-
tributed setting even for traditionally compute-bound MMM. E.g.,
for square or “flat” matrix and 16k cores, COSMA communicates
more than two times less than the second-best (CARMA). Assuming
constant time-per-MB, COSMA would be 40% slower if it communi-
cated that much, being slower than CARMA by 30%. For “largeK”,
the situation is even more extreme, with COSMA suffering 2.3 times
slowdown if communicating as much as the second-best algorithm,
CTF, which communicates 10 times more.

Detailed Statistical Analysis
Figure 13 provides a distribution of the achieved peak performance
across all numbers of cores for all six scenarios. It can be seen that,
for example, in the strong scaling scenario and square matrices,
COSMA is comparable to the other implementations (especially
CARMA). However, for tall-and-skinny matrices with limited mem-
ory available, COSMA lowest achieved performance is higher than
the best performance of CTF and ScaLAPACK.

10 RELATED WORK
Works on data movement minimization may be divided into two
categories: applicable across memory hierarchy (vertical, also called
I/O minimization), or between parallel processors (horizontal, also
called communication minimization). Even though they are “two
sides of the same coin”, in literature they are often treated as sep-
arate topics. In our work we combine them: analyze trade–offs
between communication optimal (distributed memory) and I/O
optimal schedule (shared memory).

Technical Report, 2019,

G. Kwasniewski et al.

(a) Strong scaling, n = m = k = 16,384

2/3
3
Figure 6: Total communication volume per core carried out by COSMA, CTF, ScaLAPACK and CARMA for square matrices, as measured by the mpiP profiler.

(b) Limited memory, n = m = k =

(c) Extra memory,n = m = k =

(cid:113) pS
3

(cid:113)

p

S

(a) Strong scaling, n = m =17,408, k = 3,735,552

(b) Limited memory,m = n = 979p

1
3 , k =1.184p

2
3

(c) Extra memory,,m = n = 979p

2
9 , k =1.184p

4
9

Figure 7: Total communication volume per core carried out by COSMA, CTF, ScaLAPACK and CARMA for “largeK” matrices, as measured by the mpiP profiler.

(a) Strong scaling, n = m = k = 16,384

(b) Limited memory, n = m = k =

(cid:113) pS
3

(c) Extra memory, m = n = k =

(cid:113)

p

2/3
3

S

Figure 8: Achieved % of peak performance by COSMA, CTF, ScaLAPACK and CARMA for square matrices, strong and weak scaling. We show median and 95% confidence intervals.

shape benchmark

strong scaling
limited memory
extra memory

strong scaling
limited memory
extra memory

strong scaling
limited memory
extra memory

strong scaling
limited memory
extra memory

overall

total comm. volume per rank [MB]

speedup

ScaLAPACK CTF CARMA COSMA min mean max
4.81
2.99
4.73

1.07
1.23
1.14

1.94
1.71
2.03

203
816
303

222
986
350

195
799
291

107
424
151

2636
368
133

3507
989
122

134
47
15

2278
541
152

2024
672
77

68
101
15

659
128
48

541
399
77

10
26
10

545
88
35

410
194
29

7
8
3

1.24
1.30
1.31

1.31
1.42
1.35

1.21
1.31
1.5

2.00
2.61
2.55

6.55
8.26
6.70

2.22
3.22
1.7
2.27
1.76
2.8
4.02 12.81
3.41
2.07
3.59
2.29

1.07

2.17 12.81

Table 4: Average communication volume per MPI rank and measured speedup of
COSMA vs the second-best algorithm across all core counts for each of the scenarios.
10.1 General I/O Lower Bounds
Hong and Kung [34] analyzed the I/O complexity for general CDAGs
in their the red-blue pebble game, on which we base our work. As

14

√
S

3/

(cid:16)
n

(cid:17) for
a special case, they derived an asymptotic bound Ω
MMM. Elango et al. [23] extended this work to the red-blue-white
game and Liu and Terman [40] proved that it is also P-SPACE com-
plete. Irony et al. [33] extended the MMM lower bound result to
a parallel machine with p processors, each having a fast private
memory of size S, proving the
− S lower bound on the
√
2
communication volume per processor. Chan [12] studied differ-
ent variants of pebble games in the context of memory space and
parallel time. Aggarwal and Vitter [2] introduced a two-memory
machine that models a blocked access and latency in an external
storage. Arge et al. [3] extended this model to a parallel machine.
Solomonik et al. [51] combined the communication, synchroniza-
tion, and computation in their general cost model and applied it
to several linear algebra algorithms. Smith and van de Geijn [48]
S − 2S for MMM. They
derived a sequential lower bound 2mnk/

n3
2p

√

√

S

●●●●●●●●●●●●●●●●CARMA [21]CTF [49]COSMA (this work)ScaLAPACK [14]4564901281812563621282565121,0242,048# of coresMB communicated per core2250●●●●●●●●●●●CARMA [21]CTF [49]COSMA (this work)ScaLAPACK [14]2563625127241,0241,4481282565121,0242,048# of coresMB communicated per core5022●●●●●●●●●●●●CARMA [21]CTF [49]COSMA (this work)ScaLAPACK [14]1812563625121282565121,0242,048# of coresMB communicated per core2250●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●CARMA [21]CTF [49]COSMA (this work)ScaLAPACK [14]2563625127241,0241,4482,0481282565121,0242,048# of coresMB communicated per core5022●●●●●●●●●●●●CARMA [21]CTF [49]COSMA (this work)ScaLAPACK [14]4564901281812563625127241,0241282565121,0242,048# of coresMB communicated per core5022●●●●●●●●●●●●CARMA [21]CTF [49]COSMA (this work)ScaLAPACK [14]324564901281812561282565121,0242,048# of coresMB communicated per core2250●●●●●●●●●●●●●●●●●●●●●●●●●●●●CARMA [21]CTF [49]COSMA (this work)ScaLAPACK [14]0204060802561,0244,09616,384# of cores% peak performance2250●●●●●●●●●●●●●●●●●●●●●●●●●●●●CARMA []CTF []COSMA (this work)ScaLAPACK [14]2550752561,0244,09616,384# of cores% peak performance2250●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●CARMA [21]CTF [49]COSMA (this work)ScaLAPACK [14]0204060802561,0244,09616,384# of cores% peak performance5022ACBACBCBAACBI/O Optimal Parallel Matrix Multiplication

Technical Report, 2019,

(a) Strong scaling, n = m = k = 16,384

(b) Limited memory, n = m = k =

(cid:113) pS
3

(c) Extra memory, m = n = k = (cid:112)(p2/3S )/3

Figure 9: Total runtime of COSMA, CTF, ScaLAPACK and CARMA for square matrices, strong and weak scaling. We show median and 95% confidence intervals.

(a) Strong scaling, n = m =17,408, k = 3,735,552

(b) Limited memory, m = n = 979p

1
3 , k =1.184p

2
3

(c) Extra memory,m = n = 979p

2
9 , k =1.184p

4
9

Figure 10: Achieved % of peak performance by COSMA, CTF, ScaLAPACK and CARMA for “largeK” matrices. We show median and 95% confidence intervals.

(a) Strong scaling, n = m =17,408, k = 3,735,552

(b) Limited memory, m = n = 979p

1
3 , k =1.184p

2
3

(c) Extra memory, m = n = 979p

2
9 , k =1.184p

4
9

Figure 11: Total runtime of COSMA, CTF, ScaLAPACK and CARMA for “largeK” matrices, strong and weak scaling. We show median and 95% confidence intervals.

as in the external memory model, nor the cost of computation. We
motivate it by assuming that the block size is significantly smaller
than the input size, the data is layout contiguously in the memory,
and that the computation is evenly distributed among processors.

10.2 Shared Memory Optimizations
I/O optimization for linear algebra includes such techniques as
loop tiling and skewing [59], interchanging and reversal [58]. For
programs with multiple loop nests, Kennedy and McKinley [35]
showed various techniques for loop fusion and proved that in gen-
eral this problem is NP-hard. Later, Darte [20] identified cases when
this problem has polynomial complexity.

Toledo [55] in his survey on Out-Of-Core (OOC) algorithms
analyzed various I/O minimizing techniques for dense and sparse

Figure 12: Time distribution of COSMA communication and computation kernels
for strong scaling executed on the smallest and the largest core counts for each of the
matrix shapes. Left bar: no communication–computation overlap. Right bar: overlap
enabled.

showed that the leading factor 2mnk/
S is tight. We improve this
result by 1) improving an additive factor of 2S, but more importantly
2) generalizing the bound to a parallel machine. Our work uses a
simplified model, not taking into account the memory block size,

√

15

●●●●●●●●1285122,0482561,0244,09616,384# of corestotal time [ms]●CARMA [21] COSMA (this work) CTF [46] ScaLAPACK [51] 502214●●●●●●●●4,09616,38465,536262,1442561,0244,09616,384# of corestotal time [ms]●CARMA [] 22COSMA (this work) CTF [] ScaLAPACK [1450●●●●●●●●2,0488,19232,7682561,0244,09616,384# of corestotal time [ms]●CARMA [21] COSMA (this work) CTF [46] ScaLAPACK [51] 225014●●●●●●●●●●●●CARMA [21]CTF [49]COSMA (this work)ScaLAPACK [14]02550754,0968,19216,384# of cores% peak performance5022●●●●●●●●●●●●●●●●●●●●●●●●●●●●CARMA [21]CTF [49]COSMA (this work)ScaLAPACK [14]02040602561,0244,09616,384# of cores% peak performance2250●●●●●●●●●●●●●●●●●●●●●●●●●●●●CARMA [21]CTF [49]COSMA (this work)ScaLAPACK [14]02040602561,0244,09616,384# of cores% peak performance2250●●●16,38465,536262,1444,0968,19216,384# of corestotal time [ms]●CARMA [21] COSMA (this work) CTF [46] ScaLAPACK [51502214llllllll 1,024 4,09616,38465,536   256 1,024 4,09616,384# of corestotal time [ms]lCARMA [21] COSMA (this work) CTF [46] ScaLAPACK [51] llllllll  5122,0488,192   256 1,024 4,09616,384# of corestotal time [ms]lCARMA [21] COSMA (this work) CTF [46] ScaLAPACK [51] 0255075100% of total runtimesending inputs A and Bsending output Ccomputationothertotal time executedwith overlapACBACBCBAACBcommuni-cationSQUARELARGE KLARGE MFLAT2,04818,4322,04818,4322,04818,4322,04818,432processor count2,04818,4322,04818,4322,04818,432Technical Report, 2019,

G. Kwasniewski et al.

Figure 13: Distribution of achieved % of peak performance of the algorithms across all number of cores for “flat” and square matrices.

Figure 14: Distribution of achieved % of peak performance of the algorithms across all number of cores for tall-and-skinny matrices.

matrices. Mohanty [43] in his thesis optimized several OOC algo-
rithms. Irony et al. [33] proved the I/O lower bound of classical
MMM on a parallel machine. Ballard et al. [5] proved analogous
results for Strassen’s algorithm. This analysis was extended by
Scott et al. [46] to a general class of Strassen-like algorithms.

Although we consider only dense matrices, there is an extensive
literature on sparse matrix I/O optimizations. Bender et al. [7] ex-
tended Aggarwal’s external memory model [2] and showed I/O com-
plexity of
the sparse matrix-vector (SpMV) multiplication.
Greiner [29] extended those results and provided I/O complexi-
ties of other sparse computations.

10.3 Distributed Memory Optimizations
Distributed algorithms for dense matrix multiplication date back to
the work of Cannon [10], which has been analyzed and extended
many times [30] [39]. In the presence of extra memory, Aggarwal
et al. [1] included parallelization in the third dimension. Solomonik
and Demmel [53] extended this scheme with their 2.5D decom-
position to arbitrary range of the available memory, effectively
interpolating between Cannon’s 2D and Aggarwal’s 3D scheme. A
recursive, memory-oblivious MMM algorithm was introduced by
Blumofe et al. [9] and extended to rectangular matrices by Frigo et
al. [26]. Demmel el al. [22] introduced CARMA algorithm which
achieves the asymptotic complexity for all matrix and memory
sizes. We compare COSMA with these algorithms, showing that we
achieve better results both in terms of communication complexity
and the actual runtime performance. Lazzaro et al. [38] used the
2.5D technique for sparse matrices, both for square and rectangu-
lar grids. Koanantakool et al. [37] observed that for sparse-dense
MMM, 1.5D decomposition performs less communication than 2D
and 2.5D schemes, as it distributes only the sparse matrix.

11 CONCLUSIONS
In this work we present a new method (Lemma 3) for assessing tight
I/O lower bounds of algorithms using their CDAG representation
and the red-blue pebble game abstraction. As a use case, we prove a
tight bound for MMM, both for a sequential (Theorem 1) and parallel

16

S +1−1

, which is less than 0.04% from the lower bound for 10MB of

(Theorem 2) execution. Furthermore, our proofs are constructive:
our COSMA algorithm is near I/O optimal (up to the factor of
√
S√
fast memory) for any combination of matrix dimensions, number of
processors and memory sizes. This is in contrast with the current
state-of-the-art algorithms, which are communication-inefficient
in some scenarios.

To further increase the performance, we introduce a series of
optimizations, both on an algorithmic level (processor grid opti-
mization (§ 7.1) and blocked data layout (§ 7.6)) and hardware-
related (enhanced communication pattern (§ 7.2), communication–
computation overlap (§ 7.3), one-sided (§ 7.4) communication). The
experiments confirm the superiority of COSMA over the other
analyzed algorithms - our algorithm significantly reduces commu-
nication in all tested scenarios, supporting our theoretical analysis.
Most importantly, our work is of practical importance, being main-
tained as an open-source implementation and achieving a time-to-
solution speedup of up to 12.8x times compared to highly optimized
state-of-the-art libraries.

The important feature of our method is that it does not require
any manual parameter tuning and is generalizable to other machine
models (e.g., multiple levels of memory) and linear algebra kernels
(e.g., LU or Cholesky decompositions), both for dense and sparse
matrices. We believe that the “bottom-up” approach will lead to
developing more efficient distributed algorithms in the future.

Acknowledgements
We thank Yishai Oltchik and Niels Gleinig for invaluable help with
the theoretical part of the paper, and Simon Pintarelli for advice
and support with the implementation. We also thank CSCS for the
compute hours needed to conduct all experiments. This project has
received funding from the European Research Council (ERC) under
the European Union’s Horizon2020 programme (grant agreement
DAPP, No.678880), and additional funding from the Platform for
Advanced Scientific Computing (PASC).

'flat' extra memory'flat', limited memory'flat', strong scalingsquare extra memorysquare, limited memorysquare, strong scaling0255075100% peak performanceCOSMA (this work) ScaLAPACK [14] CTF [] CARMA [21] from left to right:495022'largeK', extra memory'largeK', limited memory'largeK', strong scaling'largeM', extra memory'largeM', limited memory'largeM', strong scaling0255075100% peak performanceCOSMA (this work)ScaLAPACK [14]CTF []CARMA [21]from left to right:495022I/O Optimal Parallel Matrix Multiplication

Technical Report, 2019,

[41] Lynn Loomis and Hassler Whitney. 1949. An inequality related to the isoperi-

metric inequality. (1949).

[42] Carl D Meyer. 2000. Matrix analysis and applied linear algebra. SIAM.
[43] Sraban Kumar Mohanty. 2010. I/O Efficient Algorithms for Matrix Computations.

CoRR abs/1006.1307 (2010).

[44] Andrew Y Ng et al. 2002. On spectral clustering: Analysis and an algorithm. In

NIPS.

[45] Donald W. Rogers. 2003. Computational Chemistry Using the PC. John Wiley &

[46]

Sons, Inc.
Jacob Scott et al. 2015. Matrix multiplication I/O-complexity by path routing. In
SPAA.

[47] Ravi Sethi. 1973. Complete Register Allocation Problems. In STOC.
[48] Tyler Michael Smith and Robert A. van de Geijn. 2017. Pushing the Bounds for

Matrix-Matrix Multiplication. CoRR abs/1702.02017 (2017).

[49] Raffaele Solc`a, Anton Kozhevnikov, Azzam Haidar, Stanimire Tomov, Jack Don-
garra, and Thomas C. Schulthess. 2015. Efficient Implementation of Quan-
tum Materials Simulations on Distributed CPU-GPU Systems. In Proceedings
of the International Conference for High Performance Computing, Networking,
Storage and Analysis (SC ’15). ACM, New York, NY, USA, Article 10, 12 pages.
https://doi.org/10.1145/2807591.2807654

[50] Edgar Solomonik et al. 2013. Cyclops tensor framework: Reducing commu-
nication and eliminating load imbalance in massively parallel contractions. In
IPDPS.

[51] Edgar Solomonik et al. 2016. Trade-Offs Between Synchronization, Communica-

tion, and Computation in Parallel Linear Algebra omputations. TOPC (2016).

[52] E. Solomonik et al. 2017. Scaling Betweenness Centrality using Communication-

Efficient Sparse Matrix Multiplication. In SC.

[53] Edgar Solomonik and James Demmel. 2011. Communication-Optimal Parallel
2.5D Matrix Multiplication and LU Factorization Algorithms. In EuroPar.
[54] Volker Strassen. 1969. Gaussian Elimination is Not Optimal. Numer. Math. (1969).
[55] Sivan Toledo. 1999. A survey of out-of-core algorithms in numerical linear

algebra. External Memory Algorithms and Visualization (1999).

[56] Robert A Van De Geijn and Jerrell Watts. 1997. SUMMA: Scalable universal
matrix multiplication algorithm. Concurrency: Practice and Experience 9, 4 (1997),
255–274.
Jeffrey S Vetter and Michael O McCracken. 2001. Statistical scalability analysis
of communication operations in distributed applications. ACM SIGPLAN Notices
36, 7 (2001), 123–132.

[57]

[58] Michael E. Wolf and Monica S. Lam. 1991. A Data Locality Optimizing Algorithm.

In PLDI.

[59] Michael Wolfe. 1989. More iteration space tiling. In Supercomputing’89: Proceed-
ings of the 1989 ACM/IEEE conference on Supercomputing. IEEE, 655–664.
[60] Nan Xiong. 2018. Optimizing Tall-and-Skinny Matrix-Matrix Multiplication on

GPUs. Ph.D. Dissertation. UC Riverside.

[61] Qinqing Zheng and John D. Lafferty. 2016. Convergence Analysis for Rectangular
Matrix Completion Using Burer-Monteiro Factorization and Gradient Descent.
CoRR (2016).

REFERENCES
[1] R. C. Agarwal et al. 1995. A three-dimensional approach to parallel matrix

multiplication. IBM J. Res. Dev. (1995).

[2] Alok Aggarwal and S. Vitter, Jeffrey. [n. d.]. The Input/Output Complexity of

Sorting and Related Problems. CACM (Sept. [n. d.]).

[3] Lars Arge et al. 2008. In SPAA.
[4] Ariful Azad et al. 2015. Parallel triangle counting and enumeration using matrix

algebra. In IPDPSW.

[5] Grey Ballard et al. 2012. Graph expansion and communication costs of fast

matrix multiplication. JACM (2012).

[6] Tal Ben-Nun and Torsten Hoefler. 2018. Demystifying Parallel and Distributed
Deep Learning: An In-Depth Concurrency Analysis. CoRR abs/1802.09941 (2018).
[7] Michael A Bender et al. 2010. Optimal sparse matrix dense vector multiplication

in the I/O-model. TOCS (2010).

[8] Maciej Besta et al. 2017. SlimSell: A Vectorizable Graph Representation for

Breadth-First Search. In IPDPS.

[9] Robert D Blumofe et al. 1996. An analysis of dag-consistent distributed shared-

memory algorithms. In SPAA.

[10] Lynn Elliot Cannon. 1969. A Cellular Computer to Implement the Kalman Filter

Algorithm. Ph.D. Dissertation.

[11] Gregory J. Chaitin et al. 1981. Register allocation via coloring. Computer Lan-

guages (1981).

[12] S. M. Chan. 2013. Just a Pebble Game. In CCC.
[13] Fran`aoise Chatelin. 2012. Eigenvalues of Matrices: Revised Edition. Siam.
[14]

Jaeyoung Choi et al. 1992. ScaLAPACK: A scalable linear algebra library for
distributed memory concurrent computers. In FRONTIERS.
Jaeyoung Choi et al. 1996. Design and Implementation of the ScaLAPACK LU,
QR, and Cholesky Factorization Routines. Sci. Program. (1996).
J. Choi et al. 1996. ScaLAPACK: a portable linear algebra library for distributed
memory computers — design issues and performance. Comp. Phys. Comm. (1996).
Jaeyoung Choi, David W Walker, and Jack J Dongarra. 1994. PUMMA: Parallel
universal matrix multiplication algorithms on distributed memory concurrent
computers. Concurrency: Practice and Experience 6, 7 (1994), 543–570.

[15]

[16]

[17]

[18] Thomas H Cormen, Charles E Leiserson, Ronald L Rivest, and Clifford Stein.

2009. Introduction to algorithms. MIT press.

[19] Paolo D’Alberto and Alexandru Nicolau. 2008. Using recursion to boost ATLAS’s

performance. In High-Performance Computing. Springer.
[20] Alain Darte. 1999. On the complexity of loop fusion. In PACT.
[21] Mauro Del Ben et al. 2015. Enabling simulation at the fifth rung of DFT: Large
scale RPA calculations with excellent time to solution. Comp. Phys. Comm.
(2015).
J. Demmel et al. 2013. Communication-Optimal Parallel Recursive Rectangular
Matrix Multiplication. In IPDPS.

[22]

[23] V. Elango et al. 2013. Data access complexity: The red/blue pebble game revisited.

Technical Report.

[24] Geoffrey C Fox. 1988. Solving problems on concurrent processors. (1988).
[25] Geoffrey C Fox, Steve W Otto, and Anthony JG Hey. 1987. Matrix algorithms on
a hypercube I: Matrix multiplication. Parallel computing 4, 1 (1987), 17–31.

[26] M. Frigo et al. 1999. Cache-oblivious algorithms. In FOCS.
[27] R. Gerstenberger et al. 2013. Enabling Highly-Scalable Remote Memory Access

[28]

Programming with MPI-3 One Sided. In SC.
John R. Gilbert et al. 1979. The Pebbling Problem is Complete in Polynomial
Space. In STOC.

[29] Gero Greiner. 2012. Sparse matrix computations and their I/O complexity. Ph.D.

Dissertation. Technische Universit¨at M¨unchen.

[30] A. Gupta and V. Kumar. 1993. Scalability of Parallel Algorithms for Matrix

Multiplication. In ICPP.

[31] Azzam Haidar, Stanimire Tomov, Jack Dongarra, and Nicholas J Higham. 2018.
Harnessing GPU tensor cores for fast FP16 arithmetic to speed up mixed-
precision iterative refinement solvers. In Proceedings of the International Confer-
ence for High Performance Computing, Networking, Storage, and Analysis. IEEE
Press, 47.

[32] T. Hoefler et al. 2015. Remote Memory Access Programming in MPI-3. TOPC

(2015).

[33] Dror Irony et al. 2004. Communication Lower Bounds for Distributed-memory

Matrix Multiplication. JPDC (2004).

[34] Hong Jia-Wei and Hsiang-Tsung Kung. 1981. I/O complexity: The red-blue pebble

game. In STOC.

[35] Ken Kennedy and Kathryn S McKinley. 1993. Maximizing loop parallelism and

[36]

improving data locality via loop fusion and distribution. In LCPC.
Jeremy Kepner et al. 2016. Mathematical foundations of the GraphBLAS.
arXiv:1606.05790 (2016).

[37] Penporn Koanantakool et al. 2016. Communication-avoiding parallel sparse-

dense matrix-matrix multiplication. In IPDPS.

[38] Alfio Lazzaro et al. 2017.

Increasing the efficiency of sparse matrix-matrix

multiplication with a 2.5 D algorithm and one-sided MPI. In PASC.

[39] Hyuk-Jae Lee et al. 1997. Generalized Cannon’s Algorithm for Parallel Matrix

Multiplication. In ICS.

[40] Quanquan Liu. 2018. Red-Blue and Standard Pebble Games : Complexity and

Applications in the Sequential and Parallel Models.

17

Technical Report, 2019,

A CHANGE LOG
10.12.2019

• Added DOI (10.1145/3295500.3356181) of the SC’19 paper

version

G. Kwasniewski et al.

• Section 4.2.1 Data Reuse, last paragraph (Section 4 in the
SC’19 paper): WB,i corrected to WR,i in the definition of
R(S).

• Section 4.2.2 Reuse Based Lemma, Lemma 2: q ≥ (X −R(S)−
T (S)) · (h − 1) corrected to q ≥ (X − R(S) + T (S)) · (h − 1)
• Section 4.2.2 Reuse Based Lemma, Lemma 3 (Section 4,
Lemma 1 in the SC’19 paper): “T (S) is the minimum store
size” corrected to “T (S) is the minimum I/O size”

• Section 6.2 Parallelization Strategies
= (cid:2) m√
S

Schedule Pi jk
rected to (cid:2) m√
S

: processor grid Gi jk
, n√
S

, pS
mn

(cid:3)

for MMM,
(cid:3) cor-

, k
pS

, n√
S

18

