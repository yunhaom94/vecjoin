Scalable and Robust Set Similarity Join

Tobias Christiani, Rasmus Pagh, Johan Sivertsen

IT University of Copenhagen, Denmark
{tobc, pagh, jovt}@itu.dk

8
1
0
2

r
a

M
2

]

B
D
.
s
c
[

3
v
4
1
8
6
0
.
7
0
7
1
:
v
i
X
r
a

Abstract—Set similarity join is a fundamental and well-
studied database operator. It is usually studied in the
exact setting where the goal is to compute all pairs of sets
that exceed a given similarity threshold (measured e.g. as
Jaccard similarity). But set similarity join is often used
in settings where 100% recall may not be important —
indeed, where the exact set similarity join is itself only an
approximation of the desired result set.

We present a new randomized algorithm for set sim-
ilarity join that can achieve any desired recall up to
100%, and show theoretically and empirically that it
signiﬁcantly improves on existing methods. The present
state-of-the-art exact methods are based on preﬁx-ﬁltering,
the performance of which depends on the data set having
many rare tokens. Our method is robust against the
absence of such structure in the data. At 90% recall our
algorithm is often more than an order of magnitude faster
than state-of-the-art exact methods, depending on how well
a data set lends itself to preﬁx ﬁltering. Our experiments on
benchmark data sets also show that the method is several
times faster than comparable approximate methods. Our
algorithm makes use of recent theoretical advances in high-
dimensional sketching and indexing that we believe to be
of wider relevance to the data engineering community.

I. INTRODUCTION

It is increasingly important for data processing and
analysis systems to be able to work with data that
is imprecise, incomplete, or noisy. Similarity join has
emerged as a fundamental primitive in data cleaning and
entity resolution over the last decade [1], [2], [3]. In this
paper we focus on set similarity join: Given collections
R and S of sets the task is to compute

R

S

sim(x, y)

λ

R (cid:46)(cid:47)λ S =

(x, y)
{

∈

×

|
where sim(
,
) is a similarity measure and λ is a thresh-
·
·
old parameter. We deal with sets x, y
,
}
where the number d of distinct tokens can be naturally
thought of as the dimensionality of the data.

1, . . . , d

⊆ {

≥

}

Many measures of set similarity exist [4], but perhaps
the most well-known such measure is the Jaccard simi-
larity,

J(x, y) =

x
|

y

/
|

x
|

∩

y

|

∪

.

{

and

the sets x =

IT, University,
For example,
{
University,
Copenhagen
=
y
}
Copenhagen, Denmark
have Jaccard similarity
}
J(x, y) = 1/2 which could suggest
they both
that
correspond to the same entity. In the context of entity
to ﬁnd a set T that contains
resolution we want
(x, y)
S if and only if x and y correspond to the
R
same entity. The quality of the result can be measured
in terms of precision
and recall
(R (cid:46)(cid:47)λ S)
T
/
|
|
(R (cid:46)(cid:47)λ S)
, both of which should be as
|
|
high as possible. We will be interested in methods that
achieve 100% precision, but that might not have 100%
recall. We refer to methods with 100% recall as exact,
and others as approximate.

R (cid:46)(cid:47)λ S

/
|
|

×

∈

∩

∩

T

T

|

|

A. Our Contributions

We present a new approximate set similarity join algo-
rithm: Chosen Path Similarity Join (CPSJOIN). We cover
its theoretical underpinnings, and show experimentally
that it achieves high recall with a substantial speedup
compared to state-of-the-art exact techniques. The key
ideas behind CPSJOIN are:

• A new recursive ﬁltering technique inspired by
the recently proposed ChosenPath index for set
similarity search [5], adding new ideas to make
the method parameter-free, near-linear space, and
adaptive to a given data set.

• Apply efﬁcient sketches for estimating set similar-
ity [6] that take advantage of modern hardware.
We compare CPSJOIN to the exact set similarity join
algorithms in the comprehensive empirical evaluation
of Mann et al. [7], using the same data sets, and to
other approximate set similarity join methods suggested
in the literature. We ﬁnd that CPSJOIN outperforms
other approximate methods and scales better than exact
methods when the sets are relatively large (100 tokens
or more) and the similarity threshold is low (e.g. Jaccard
similarity 0.5) where we see speedups of more than
an order of magnitude at 90% recall. The ﬁnding that
exact methods are faster in the case of high similarity
thresholds, when the average set size is small, and

when sets have many rare tokens, whereas approximate
methods are faster in the case of low similarity thresh-
olds and when sets are large, is consistent with theory
and is further corroborated by experiments on synthetic
datasets.

B. Related Work

For space reasons we present just a sample of the
most related previous work, and refer to the book of
Augsten and B¨ohlen [1] for a survey of algorithms for
exact similarity join in relational databases, covering set
similarity joins as well as joins based on string similarity.
Exact Similarity Join: Early work on similarity join
focused on the important special case of detecting near-
duplicates with similarity close to 1, see e.g. [8], [3].
A sequence of results starting with the seminal paper of
Bayardo et al. [9] studied the range of thresholds that
could be handled. Recently, Mann et al. [7] conducted a
comprehensive study of 7 state-of-the-art algorithms for
exact set similarity join for Jaccard similarity threshold
λ
. These algorithms all use the
}
idea of preﬁx ﬁltering [2], which generates a sequence
of candidate pairs of sets that includes all pairs with
similarity above the threshold. The methods differ in how
much additional ﬁltering is carried out. For example, [10]
applies additional length and sufﬁx ﬁlters to prune the
candidate pairs.

0.5, 0.6, 0.7, 0.8, 0.9

∈ {

Preﬁx ﬁltering uses an inverted index that for each
element stores a list of the sets in the collection contain-
ing that element. Given a set x, assume that we wish to
ﬁnd all sets y such that
> t. A valid result set
∪
y must be contained in at least one of the inverted lists
t elements of x, or
associated with any subset of
t. In particular, to speed up
we would have
the search, preﬁx ﬁltering looks at the elements of x that
have the shortest inverted lists.

x
|

x
|

x
|

| ≤

| −

∪

y

y

|

The main ﬁnding by Mann et al. is that while more
advanced ﬁltering techniques do yield speedups on some
data sets, an optimized version of the basic preﬁx ﬁlter-
ing method (referred to as “ALL”) is always competitive
within a factor 2.16, and most often the fastest of the
algorithms. For this reason we will be comparing our
results against ALL.

Locality-Sensitive Hashing: Locality-sensitive hash-
ing (LSH) is a theoretically well-founded randomized
method for generating candidate pairs [11]. A family
of locality-sensitive hash functions is a distribution over
functions with the property that
the probability that
similar points (or sets in our case) are more likely to have
the same function value. We know only of a few papers

using LSH techniques to solve similarity join. Cohen et
al. [12] used LSH techniques for set similarity join in a
knowledge discovery context before the advent of preﬁx
ﬁltering. They sketch a way of choosing parameters
suitable for a given data set, but we are not aware of
existing implementations of this approach. Chakrabarti et
al. [13] improved plain LSH with an adaptive similarity
estimation technique, BayesLSH, that reduces the cost of
checking candidate pairs and typically improves upon an
implementation of the basic preﬁx ﬁltering method by 2–
20
. Our experiments include a comparison against both
methods [12], [13]. We refer to the survey paper [14] for
an overview of newer theoretical developments on LSH-
based similarity joins, but point out that these develop-
ments have not matured sufﬁciently to yield practical
improvements.

×

Distance Estimation: Similar to BayesLSH [13] we
make use of algorithms for similarity estimation, but in
contrast to BayesLSH we use algorithms that make use
of bit-level parallelism. This approach works when there
exists a way of picking a random hash function h such
that

Pr[h(x) = h(y)] = sim(x, y)

(1)

for every choice of sets x and y. Broder et al. [15]
presented such a hash function for Jaccard similarity,
now known as “minhash” or “minwise hashing”. In the
context of distance estimation, 1-bit minwise hashing of
Li and K¨onig [6] maps minhash values to a compact
sketch, often using just 1 or 2 machine words. Still, this
is sufﬁcient information to be able to estimate the Jaccard
similarity of two sets x and y just based on the Hamming
distance of their sketches.

Locality-Sensitive Mappings: Several recent theoret-
ical advances in high-dimensional indexing [16], [17],
[5] have used an approach that can be seen as a general-
ization of LSH. We refer to this approach as locality-
sensitive mappings (also known as locality-sensitive
ﬁlters in certain settings). The idea is to construct a
function F , mapping a set x into a set of machine words,
such that:

• If sim(x, y)

λ then F (x)

F (y) is nonempty

with some ﬁxed probability ϕ > 0.

≥

∩

• If sim(x, y) < λ, then the expected intersection size

∩

F (y)
|

F (x)
E[
|

] is “small”.
Here the exact meaning of “small” depends on the differ-
sim(x, y), but in a nutshell, if it is the case that
ence λ
almost all pairs have similarity signiﬁcantly below λ then
= 0 for almost all pairs.
F (y)
we can expect
Performing the similarity join amounts to identifying all

F (x)

−

∩

|

|

∩

F (y)

= ∅ (for
candidate pairs x, y for which F (x)
example by creating an inverted index), and computing
the similarity of each candidate pair. To our knowledge
these indexing methods have not been tried out
in
practice, probably because they are rather complicated.
An exception is the recent paper [5], which is relatively
simple, and indeed our join algorithm is inspired by the
index described in that paper.

II. PRELIMINARIES

The CPSJOIN algorithm solves the (λ, ϕ)-similarity
join problem with a probabilistic guarantee on recall,
formalized as follows:

Deﬁnition 1. An algorithm solves the (λ, ϕ)-similarity
(0, 1) and recall
join problem with threshold λ
S (cid:46)(cid:47)λ R
probability ϕ
(0, 1) if for every (x, y)
S (cid:46)(cid:47)λ R of the algorithm satisﬁes
the output L
ϕ.
L]
Pr[(x, y)

∈

∈

∈
⊆
≥

∈

It is important to note that the probability is over the
random choices made by the algorithm, and not over a
random choice of (x, y). This means that for any (x, y)
∈
S (cid:46)(cid:47)λ R the probability that the pair is not reported in r
independent repetitions of the algorithm is bounded by
ϕ)r. For example if ϕ = 0.9 it takes just r = 3
(1
repetitions to bound the recall to at least 99.9%.

−

A. Similarity Measures

Our algorithm can be used with a broad range of
similarity measures through randomized embeddings.
This allows it to be used with, for example, Jaccard and
cosine similarity thresholds.

Embeddings map data from one space to another while
approximately preserving distances, with accuracy that
can be tuned. In our case we are interested in embeddings
that map data to sets of tokens. We can transform any
so-called LSHable similarity measure sim, where we
can choose h to make (1) hold, into a set similarity
measure by the following randomized embedding: For a
parameter t pick hash functions h1, . . . , ht independently
from a family satisfying (1). The embedding of x is the
following set of size t:

f (x) =

(i, hi(x))
{

|

i = 1, . . . , t

.

}

f (y) is t

It follows from (1) that the expected size of the intersec-
sim(x, y). Furthermore, it follows
tion f (x)
from standard concentration inequalities that the size of
the intersection will be close to the expectation with high
probability. For our experiments with Jaccard similarity

∩

·

thresholds
precision for > 90% recall.

≥

0.5, we found that t = 64 gave sufﬁcient

In summary we can perform the similarity join
R (cid:46)(cid:47)λ S for any LSHable similarity measure by creating
two corresponding relations R(cid:48) =
f (x)
and
{
, and computing R(cid:48) (cid:46)(cid:47)λ S(cid:48) with
S(cid:48) =
y
}
respect to the similarity measure

f (y)

R

∈

∈

S

x

}

{

|

|

∩

/t .
f (y)
|

B(f (x), f (y)) =

f (x)
|
This measure is the special case of Braun-Blanquet
similarity where the sets are known to have size t [4].
Our implementation will take advantage of the set size t
being ﬁxed, though it is easy to extend to general Braun-
Blanquet similarity.

(2)

The class of LSHable similarity measures is large, as
discussed in [18]. If approximation errors are tolerable,
even edit distance can be handled by our algorithm [19],
[20].

B. Notation

· · ·

We are interested in sets S where an element, x
∈
S is a set with elements from some universe [d] =
, d
1, 2, 3,
. To avoid confusion we sometimes use
{
}
S and “token” for the elements of x.
“record” for x
Throughout this paper we will think of a record x both
as a set of tokens from [d], as well as a vector from
0, 1
}

d, where:

∈

{

(cid:40)

xi =

1 if i
∈
0 if i /
∈

x
x

is clear that
1, 4, 5
}

It
The set
1, d
}

{

{

these representations are equivalent.
, 0),
is equivalent to (1, 0, 0, 1, 1, 0,

· · ·

is equivalent to (1, 0,

, 0, 1), etc.

· · ·

III. OVERVIEW OF APPROACH

Our high-level approach is recursive and works as
R

follows. To compute R (cid:46)(cid:47)λ S we consider each x
and either:

∈

1) Compare x to each record in S (referred to as

“brute forcing” x), or

2) create several subproblems Si (cid:46)(cid:47)λ Ri with x

S, and solve them recursively.

∈

Ri

R, Si

⊆

⊆

The approach of [5] corresponds to choosing option 2
until reaching a certain level k of the recursion, where
we ﬁnish the recursion by choosing option 1. This makes
sense for certain worst-case data sets, but we propose an
improved parameter-free method that is better at adapting
to the given data distribution. In our method the decision
on which option to choose depends on the size of S

(cid:54)
∈

(cid:80)

and the average similarity of x to the records of S. We
choose option 1 if S has size below some (constant)
threshold, or if the average Braun-Blanquet similarity of
x and S, 1
y∈S B(x, y), is close to the threshold λ.
|S|
In the former case it is cheap to ﬁnish the recursion. In
S will have B(x, y)
the latter case many records y
larger than or close to λ, so we do not expect to be able
to produce output pairs with x in sublinear time in
.
|
If neither of these pruning conditions apply we choose
option 2 and include x in recursive subproblems as
described below. But ﬁrst we note that the decision of
which option to use can be made efﬁciently for each x,
S can be
since the average similarity of pairs from R
×
computed from token frequencies in time O(t
).
R
|
Pseudocode for a self-join version of CPSJOIN is pro-
vided in Algorithm 1 and 2.

S
+t
|

S
|

|

|

A. Recursion

We would like to ensure that for each pair (x, y)
∈
R (cid:46)(cid:47)λ S the pair is computed in one of the recursive
Ri (cid:46)(cid:47)λ Si for some i. In
subproblems, i.e., that (x, y)
particular, we want the expected number of subproblems
containing (x, y) to be at least 1, i.e.,

∈

|

∈

E[

i
|{

(x, y)

Ri (cid:46)(cid:47)λ Si

]
}|
R (cid:46)(cid:47)λ S we
To achieve (3) for every pair (x, y)
proceed as follows: for each i
we recurse
with probability 1/(λt) on the subproblem Ri (cid:46)(cid:47)λ Si
with sets

∈
1, . . . , d

∈ {

(3)

≥

1.

}

Ri =
Si =

x
{
y
{

∈

R

S

|

i

i

∈

x

y

}

|

}

∈

∈
where t denotes the size of records in R and S. It is
not hard to check that (3) is satisﬁed for every pair
(x, y) with B(x, y)
λ. Of course, expecting one
subproblem to contain (x, y) does not directly imply a
good probability that (x, y) is contained in at least one
subproblem. But it turns out that we can use results from
the theory of branching processes to show such a bound;
details are provided in section IV.

≥

IV. CHOSEN PATH SIMILARITY JOIN

The CPSJOIN algorithm solves the (λ, ϕ)-set similar-
ity join (Deﬁnition 1) for every choice of λ
(0, 1) and
with a guarantee on ϕ that we will lower bound in the
analysis.

∈

To simplify the exposition we focus on a self-join
version where we are given a set S of n subsets of [d] and
we wish to report L
S (cid:46)(cid:47)λ S. Handling a general join
S (cid:46)(cid:47)λ R follows the overview in section III and requires

⊆

R
no new ideas: Essentially consider a self-join on S
R for output.
but make sure to consider only pairs in S
We also make the simplifying assumption that all sets in
S have a ﬁxed size t. As argued in section II-A the
general case can be reduced to this one by embedding.

×

∪

A. Description

The CPSJoin algorithm (see Algorithm 1 for pseu-
docode) works by recursively splitting the data set on
elements of [d] that are selected according to a random
process, forming a recursion tree with S at the root and
subsets of S that are non-increasing in size as we get
further down the tree. The randomized splitting has the
property that the probability of a pair of sets (x, y) being
in a random subproblem is increasing as a function of
x
|

∩
Before each recursive splitting step we run the
BRUTEFORCE subprocedure (see Algorithm 2 for pseu-
docode) that identiﬁes subproblems that are best solved
by brute force. It has two parts:

.
|

y

1. If S is below some constant size, controlled by
the parameter limit, we report S (cid:46)(cid:47)λ S exactly
2) distance computations
using a simple loop with O(
S
|
|
(BRUTEFORCEPAIRS) and exit
the recursion. In our
experiments we have set limit to 250, with the precise
choice seemingly not having a large effect as shown
experimentally in Section VI-B.

∈

2. If S is larger than limit the second part acti-
S we check whether the expected
vates: for every x
number of distance computations involving x is going
to decrease by continuing the recursion. If this is not
the case, we immediately compare x against every point
in S (BRUTEFORCEPOINT), reporting close pairs, and
proceed by removing x from S. The BRUTEFORCE
procedure is then run again on the reduced set.

This procedure where we choose to handle some
points by brute force crucially separates our algorithm
from many other approximate similarity join methods
in the literature that typically are LSH-based [21], [12].
By efﬁciently being able to remove points at the “right”
time, before they generate too many expensive compar-
isons further down the tree, we are able to beat the
performance of other approximate similarity join tech-
niques in both theory and practice. Another beneﬁt of
this approach is that it reduces the number of parameters
compared to the usual LSH setting where the depth of
the tree has to be selected by the user.

B. Comparison to Chosen Path

The CPSJOIN algorithm is inspired by the CHOSEN
PATH algorithm [5] for the approximate near neighbor

Algorithm 1: CPSJOIN(S, λ)
∅.

[d] initialize Sj
∈
←
BRUTEFORCE(S, λ)
SEEDHASHFUNCTION()

S do

∈
for j

x do
if r(j) < 1

∈

λ|x| then Sj

←
= ∅ do CPSJOIN(Sj, λ)

1 For j
2 S
←
3 r
←
4 for x
5

6

7 for Sj

n in addition to the space required to store the output.
Finally, the CHOSEN PATH data structure only has to
report a single point that is approximately similar to a
query point, and can report points with similarity < λ.
To solve the approximate similarity join problem the
CPSJOIN algorithm has to satisfy reporting guarantees
for every pair of points (x, y) in the exact join.

C. Analysis

Sj

x

}

∪ {

Algorithm 2: BRUTEFORCE(S, λ)
1, ε
Global parameters: limit

≥

0.

≥

1 Initialize empty map count[ ] with default value 0.
2 if
3

limit then

S
| ≤
|
BRUTEFORCEPAIRS(S, λ)
return ∅
S do

4

5 for x
6

∈
for j

7

8 for x
if
9

10

11

x do
∈
count[j]

←

count[j] + 1

j∈x(count[j]

S do
∈
(cid:80)
1
1)/t > (1
|S|−1
BRUTEFORCEPOINT(S, x, λ)
x
return BRUTEFORCE(S

−

, λ)
}

\ {

ε)λ then

−

12 return S

problem and uses the same underlying random splitting
tree that we will refer to as the Chosen Path Tree. In
the approximate near neighbor problem, the task is to
construct a data structure that takes a query point and
correctly reports an approximate near neighbor, if such
a point exists in the data set. Using the CHOSEN PATH
data structure directly to solve the (λ, ϕ)-set similarity
join problem has several drawbacks that we avoid in
the CPSJOIN algorithm. First, the CHOSEN PATH data
structure is parameterized in a non-adaptive way to
provide guarantees for worst-case data, vastly increasing
the amount of work done compared to the optimal
parameterization when data is not worst-case. Our re-
cursion rule avoids this and instead continuously adapts
to the distribution of distances as we traverse down the
tree. Secondly, the data structure uses space O(n1+ρ)
where ρ > 0, storing the Chosen Path Tree of size
O(nρ) for every data point. The CPSJOIN algorithm,
instead of storing the whole tree, essentially performs
a depth-ﬁrst traversal, using only near-linear space in

⊆

The Chosen Path Tree for a set x

[d] is deﬁned
by a random process: at each node, starting from the
[0, 1]
root, we sample a random hash function r : [d]
x such that
and construct children for every element j
r(j) < 1
λ|x| . Nodes at depth k in the tree are identiﬁed
by their path p = (j1, . . . , jk). Formally, the set of nodes
at depth k > 0 in the Chosen Path Tree for x is given
by

→

∈

(cid:26)

Fk(x) =

p

j

p

|

◦

∈

Fk−1(x)

∧

rp(j) <

(cid:27)

xj
x
λ
|
|

j denotes vector concatenation and F0(x) = ∅.
where p
The subset of the data set S that survives to a node with
path p = (j1, . . . , jk) is given by

◦

Sp =

S

x

{

∈

|

xj1 = 1

∧ · · · ∧

.
xjk = 1
}

The random process underlying the Chosen Path Tree
belongs to the well studied class of Galton-Watson
branching processes [22]. Originally these where devised
to answer questions about the growth and decline of
family names in a model of population growth assuming
i.i.d. offspring for every member of the population across
generations [23]. In order to make statements about the
properties of the CPSJOIN algorithm we study in turn the
branching processes of the Chosen Path Tree associated
with a point x, a pair of points (x, y), and a set of points
S. Note that we use the same random hash functions for
different points in S.

≥

≥

1 and ε

1) Brute Force: The BRUTEFORCE subprocedure de-
scribed by Algorithm 2 takes two global parameters:
0. The parameter limit controls
limit
the minimum size of S before we discard the CPSJOIN
algorithm for a simple exact similarity join by brute force
pairwise distance computations. The second parameter,
ε > 0, controls the sensitivity of the BRUTEFORCE
step to the expected number of comparisons that a point
S will generate if allowed to continue in the
x
branching process. The larger ε the more aggressively
we will resort to the brute force procedure. In practice
we typically think of ε as a small constant, say ε = 0.05,

∈

(cid:54)
≈

but for some of our theoretical results we will need a sub-
1/ log(n) to show certain running
constant setting of ε
time guarantees. The BRUTEFORCE step removes a point
x from the Chosen Path branching process,
instead
opting to compare it against every other point y
S,
if it satisﬁes the condition
1

∈

(cid:88)

x

y

/t > (1

ε)λ.

S

|

| −

1

|

y∈S\{x}

∩

|

−

In the pseudocode of Algorithm 2 we let count denote
a hash table that keeps track of the number of times each
[d] appears in S. This allows us to evaluate
element j
S
the condition in equation (IV-C1) for an element x
x
in time O(
|
1

) by rewriting it as
|

∈

∈

(cid:88)

(count[j]

1)/t > (1

ε)λ.

−

−

S
|

| −

1

j∈x

We claim that this condition minimizes the expected
number of comparisons performed by the algorithm:
Consider a node in the Chosen Path Tree associated with
a set of points S while running the CPSJOIN algorithm.
S, we can either remove it from S
For a point x
1 comparisons, or we can
immediately at a cost of
| −
choose to let continue in the branching process (possibly
into several nodes) and remove it later. The expected
number of comparisons if we let it continue k levels
before removing it from every node that it is contained
in, is given by

∈

S

|

(cid:88)

y∈S\{x}

(cid:18) 1
λ

x
|

∩
t

y

|

(cid:19)k

.

This expression is convex and increasing in the similarity
S, allowing us
x
|
to state the following observation:

/t between x and other points y
|

∈

∩

y

Observation 2 (Recursion). Let ε = 0 and consider a
set S containing a point x
S such that x satisﬁes
the recursion condition in equation (IV-C1). Then the
expected number of comparisons involving x if we con-
1. If
tinue branching exceeds
| −
x does not satisfy the condition, the opposite is observed.

1 at every depth k

S
|

≥

∈

y

y

{

x

S

∩

∈

(1

| |

let S(cid:48) =
/t
be the subset
≤
of points in S that are not too similar to x. For every
S(cid:48) the expected number of vertices in the Chosen
y
Path Tree at depth k that contain both x and y is upper
bounded by

ε)λ

−

∈

}

|

Fk(x

E[
|

] =

y)
|

∩

(cid:19)k

(cid:18) 1
λ

x
|

∩
t

y

|

(1

−

≤

ε)k

≤

e−εk.

S(cid:48)
Since
|
following bound:

| ≤

n we use Markov’s inequality to show the

Lemma 3. Let x, y
S satisfy that
ε)λ
then the probability that there exists a vertex at depth k
in the Chosen Path Tree that contains x and y is at most
e−εk.

/t
|

x
|

(1

≤

−

∩

∈

y

If x does not share any paths with points that have
similarity that falls below the threshold for brute forcing,
then the only points that remain are ones that will cause
x to be brute forced. This observation leads to the
following probabilistic bound on the tree depth:

Lemma 4. With high probability the maximal depth
of paths explored by the CPSJOIN algorithm is
O(log(n)/ε).

y

∩

≥

x
|

/t
|

3) Correctness: Let x and y be two sets of equal
size t such that B(x, y) =
λ. We are
interested in lower bounding the probability that there
exists a path of length k in the Chosen Path Tree that has
= ∅].
been chosen by both x and y, i.e. Pr [Fk(x
Agresti [24] showed an upper bound on the probability
that a branching process becomes extinct after at most
k steps. We use it to show the following lower bound
on the probability of a close pair of points colliding at
depth k in the Chosen Path Tree.

y)

∩

Lemma 5 (Agresti [24]). If sim(x, y)
k > 0 we have that Pr[Fk(x

y)

≥
= ∅]

λ then for every

1
k+1 .

∩
The bound on the depth of the Chosen Path Tree for
x explored by the CPSJOIN algorithm in Lemma 4 then
implies a lower bound on ϕ.

≥

2) Tree Depth: We proceed by bounding the maximal
depth of the set of paths in the Chosen Path Tree that
are explored by the CPSJOIN algorithm. Having this
information will allow us to bound the space usage of
the algorithm and will also form part of the argument
for the correctness guarantee. Assume that the parameter
limit in the BRUTEFORCE step is set to some constant
S and
value, say limit = 100. Consider a point x

∈

Lemma 6. Let 0 < λ < 1 be constant. Then for every
= n points the CPSJOIN algorithm solves
set S of
the set similarity join problem with ϕ = Ω(ε/ log(n)).

S
|

|

Remark 7. This analysis is very conservative: if either
x or y is removed by the BRUTEFORCE step prior to
reaching the maximum depth then it only increases the
probability of collision. We note that similar guarantees
can be obtained when using fast pseudorandom hash

(cid:54)
(cid:54)
functions as shown in the paper introducing the CHOSEN
PATH algorithm [5].

4) Space Usage: We can obtain a trivial bound on
the space usage of the CPSJOIN algorithm by combin-
ing Lemma 4 with the observation that every call to
CPSJOIN on the stack uses additional space at most
O(n). The result is stated in terms of working space:
the total space usage when not accounting for the space
required to store the data set itself (our algorithms use
references to data points and only reads the data when
performing comparisons) as well as disregarding the
space used to write down the list of results.

Lemma 8. With high probability the working space of
the CPSJOIN algorithm is at most O(n log(n)/ε).

First consider the global strategy. We set k to balance
the contribution to the running time from the expected
number of vertices containing a point, given by (1/λ)k,
and the expected number of comparisons between pairs
of points at depth k, resulting in the following expected
running time for the global strategy:



O





min
k

n(1/λ)k +

(cid:88)

x,y∈S
x(cid:54)=y

(sim(x, y)/λ)k







.

The global strategy is a special case of the individual
case, and it must
≤
E[TGlobal]. The expected running time for the individual
strategy is upper bounded by:

therefore hold that E[TIndividual]

Remark 9. We conjecture that the expected working
space is O(n) due to the size of S being geometrically
decreasing in expectation as we proceed down the Cho-
sen Path Tree.



O



(cid:88)

x∈S

min
kx


(1/λ)kx +

(cid:88)





(sim(x, y)/λ)kx



 .

y∈S\{x}

We will now argue that the expected running time of the
CPSJOIN algorithm under the adaptive stopping criteria
is no more than a constant factor greater than E[TIndividual]
when we set the global parameters of the BRUTEFORCE
subroutine as follows:

limit = Θ(1),
log(1/λ)
log n

ε =

.

∈

S and consider a path p where x is removed in
Let x
from Sp by the BRUTEFORCE step. Let k(cid:48)
x denote the
depth of the node (length of p) at which x is removed.
Compared to the individual strategy that removes x at
depth kx we are in one of three cases, also displayed in
Figure 1.

1) The point x is removed from p at depth k(cid:48)
2) The point x is removed from p at depth k(cid:48)
3) The point x is removed from p at depth k(cid:48)

x = kx.
x < kx.
x > kx.

⊆

5) Running Time: We will bound the running time of
a solution to the general set similarity self-join problem
that uses several calls to the CPSJOIN algorithm in order
to piece together a list of results L
S (cid:46)(cid:47)λ S. In most of
the previous related work, inspired by Locality-Sensitive
Hashing, the ﬁne-grainedness of the randomized partition
of space, here represented by the Chosen Path Tree in
the CPSJOIN algorithm, has been controlled by a single
global parameter k [11], [21]. In the Chosen Path setting
this rule would imply that we run the splitting step with-
out performing any brute force comparison until reaching
depth k where we proceed by comparing x against every
other point in nodes containing x, reporting close pairs.
In recent work by Ahle et al. [25] it was shown how to
obtain additional performance improvements by setting
S. We refer to these
an individual depth kx for every x
stopping strategies as global and individual, respectively.
Together with our recursion strategy, this gives rise to the
following stopping criteria for when to compare a point
x against everything else contained in a node:
• Global: Fix a single depth k for every x
• Individual: For every x
∈
• Adaptive: Remove x when the expected number of
comparisons is non-decreasing in the tree-depth.
Let T denote the running time of our similarity join al-
gorithm. We aim to show the following relation between
the running time between the different stopping criteria
when applied to the Chosen Path Tree:

∈
S ﬁx a depth kx.

S.

∈

E[TAdaptive]

E[TIndividual]

E[TGlobal].

≤

≤

Fig. 1. Path termination depth in the Chosen Path Tree

Case1Case2Case3kxk0xk0xk0x∈

−

≤

k(cid:48)
x ≤

The underlying random process behind the Chosen Path
Tree is not affected by our choice of termination strategy.
In the ﬁrst case we therefore have that the expected run-
ning time is upper bounded by the same (conservative)
expression as the one used by the individual strategy. In
the second case we remove x earlier than we would have
under the individual strategy. For every x
S we have
that kx
1/ε since for larger values of kx the expected
number of nodes containing x exceeds n. We therefore
1/ε. Let S(cid:48) denote the set of
have that kx
points in the node where x was removed by the BRUTE-
FORCE subprocedure. There are two rules that could
= O(1) or
have triggered the removal of x: Either
the condition in equation (IV-C1) was satisﬁed. In the
ﬁrst case, the expected cost of following the individual
strategy would have been Ω(1) simply from the 1/λ
children containing x in the next step. This is no more
than a constant factor smaller than the adaptive strategy.
In the second case, when the condition in equation
(IV-C1) is activated we have that the expected number
of comparisons involving x resulting from S(cid:48) if we had
continued under the individual strategy is at least

S(cid:48)
|

|

(1

ε)1/ε

S(cid:48)
|

|

S(cid:48)
= Ω(
|

)
|

−

which is no better than what we get with the adaptive
strategy. In the third case where we terminate at depth
k(cid:48)
x > kx, if we retrace the path to depth kx we know
that x was not removed in this node,
implying that
the expected number of comparisons when continuing
the branching process on x is decreasing compared
to removing x at depth kx. We have shown that the
expected running time of the adaptive strategy is no
greater than a constant times the expected running time
of the individual strategy.

We are now ready to state our main theoretical con-
tribution, stated below as Theorem 10. The theorem
combines the above argument that compares the adaptive
strategy against
the individual strategy together with
Lemma 4 and Lemma 6, and uses O(log2 n) runs of
the CPSJOIN algorithm to solve the set similarity join
problem for every choice of constant parameters λ, ϕ.

Theorem 10. For every LSHable similarity measure
(0, 1) and
and every choice of constant threshold λ
probability of recall ϕ
(0, 1) we can solve the (λ, ϕ)-
set similarity join problem on every set S of n points
using working space ˜O(n) and with expected running

∈

∈

time


˜O



(cid:88)

x∈S





min
kx

(cid:88)

(sim(x, y)/λ)kx + (1/λ)kx







 .

y∈S\{x}

V. IMPLEMENTATION

We implement an optimized version of the CPSJOIN
algorithm for solving the Jaccard similarity self-join
problem. In our experiments (described in Section VI)
we compare the CPSJOIN algorithm against
the ap-
proximate methods of MinHash LSH [11], [15] and
BayesLSH [13], as well as the AllPairs [9] exact sim-
ilarity join algorithm. The code for our experiments is
written in C++ and uses the benchmarking framework
and data sets of the recent experimental survey on exact
similarity join algorithms by Mann et al. [7]. For our
implementation we assume that each set x is represented
as a list of 32-bit unsigned integers. We proceed by
describing the details of each implementation in turn.

A. Chosen Path Similarity Join

The implementation of the CPSJOIN algorithm fol-
lows the structure of the pseudocode in Algorithm 1 and
Algorithm 2, but makes use of a few heuristics, primarily
sampling and sketching, in order to speed things up. The
parameter setting is discussed and investigated experi-
mentally in section VI-B.

∈

1) Preprocessing: Before running the algorithm we
use the embedding described in section II-A. Speciﬁcally
t independent MinHash functions h1, . . . , ht are used
S to a list of t hash values
to map each set x
(h1(x), . . . , ht(x)). The MinHash function is imple-
mented using Zobrist hashing [26] from 32 bits to 64 bits
with 8-bit characters. We sample a MinHash function h
by sampling a random Zobrist hash function g and let
h(x) = argminj∈x g(j). Zobrist hashing (also known as
simple tabulation hashing) has been shown theoretically
to have strong MinHash properties and is very fast in
practice [27], [28]. We set t = 128 in our experiments,
see discussion later.

During preprocessing we also prepare sketches using
the 1-bit minwise hashing scheme of Li and K¨onig [6].
Let (cid:96) denote the length in 64-bit words of a sketch ˆx of
S. We construct sketches for a data set S by
a set x
independently sampling 64
(cid:96) MinHash functions hi and
×
Zobrist hash functions gi that map from 32 bits to 1 bit.
The ith bit of the sketch ˆx is then given by gi(hi(x)).
In the experiments we set (cid:96) = 8.

∈

2) Similarity Estimation Using Sketches: We use 1-bit
minwise hashing sketches for fast similarity estimation
in the BRUTEFORCEPAIRS and BRUTEFORCEPOINT
subroutines of the BRUTEFORCE step of the CPSJOIN
algorithm. Given two sketches, ˆx and ˆy, we compute the
number of bits in which they differ by going through the
sketches word for word, computing the popcount of their
XOR using the gcc builtin _mm_popcnt_u64 that
translates into a single instruction on modern hardware.
Let ˆJ(x, y) denote the estimated similarity of a pair
of sets (x, y). If ˆJ(x, y) is below a threshold ˆλ
λ,
we exclude the pair from further consideration. If the
estimated similarity is greater than ˆλ we compute the
exact similarity and report the pair if J(x, y)

λ.

≈

≥

The speedup from using sketches comes at the cost
of introducing false negatives: A pair of sets (x, y) with
λ may have an estimated similarity less than
J(x, y)
ˆλ, causing us to miss it. We let δ denote a parameter for
controlling the false negative probability of our sketches
and set ˆλ such that for sets (x, y) with J(x, y)
λ we
have that Pr[ ˆJ(x, y) < ˆλ] < δ. In our experiments we
set the sketch false negative probability to be δ = 0.05.

≥

≥

3) Recursion: In the recursive step of the CPSJOIN
algorithm (Algorithm 1) the set S is split into buckets
Sj using the following heuristic: Instead of sampling
a random hash function and evaluating it on each el-
ement j
x, we sample an expected 1/λ elements
from [t] and split S according to the corresponding
minhash values from the preprocessing step. This saves
the linear overhead in the size of our sets t, reducing
the time spent placing each set into buckets to O(1).
Internally, a collection of sets S is represented as a C++
std::vector<uint32_t> of set ids.

∈

∈

4) BruteForce: Having reduced the overhead for each
S to O(1) in the splitting step, we wish to
set x
do the same for the BRUTEFORCE step (described in
Algorithm 2), at least in the case where we do not
call
the BRUTEFORCEPAIRS or BRUTEFORCEPOINT
subroutines. The main problem is that we spend time
O(t) for each set when constructing the count hash
map and estimating the average similarity of x to sets
in S
. To get around this we construct a 1-bit
}
minwise hashing sketch ˆs of length 64
(cid:96) for the set
S using sampling and our precomputed 1-bit minwise
hashing sketches. The sketch ˆs is constructed as follows:
(cid:96) elements of S and set the ith
Randomly sample 64
bit of ˆs to be the ith bit of the ith sample from S. This
allows us to estimate the average similarity of a set x to
sets in S in time O((cid:96)) using word-level parallelism. A set

\ {

×

×

x

−

x is removed from S if its estimated average similarity
ε)λ. To further speed up the running
is greater than (1
time we only call the BRUTEFORCE subroutine once for
each call to CPSJOIN, calling BRUTEFORCEPOINT on
all points that pass the check rather than recomputing ˆs
each time a point is removed. Pairs of sets that pass the
sketching check are veriﬁed using the same veriﬁcation
procedure as the ALLPAIRS implementation by Mann et
al. [7]. In our experiments we set the parameter ε = 0.1.
Duplicates are removed by sorting and performing a
single linear scan.
5) Repetitions:

In theory, for any constant desired
(0, 1) it sufﬁces with O(log2 n) independent
recall ϕ
repetitions of the CPSJOIN algorithm. In practice this
number of repetitions is prohibitively large and we
therefore set the number of independent repetitions used
in our experiments to be ﬁxed at ten. With this setting
we were able to achieve more than 90% recall across all
datasets and similarity thresholds.

∈

B. MinHash LSH

We implement a locality-sensitive hashing similarity
join using MinHash according to the pseudocode in
Algorithm 3. A single run of the MINHASH algorithm
can be divided into two steps: First we split the sets into
buckets according to the hash values of k concatenated
MinHash functions h(x) = (h1(x), . . . , hk(x)). Next we
iterate over all non-empty buckets and run BRUTEFOR-
CEPAIRS to report all pairs of points with similarity
above the threshold λ. The BRUTEFORCEPAIRS sub-
routine is shared between the MINHASH and CPSJOIN
implementation. MINHASH therefore uses 1-bit minwise
sketches for similarity estimation in the same way as in
the implementation of the CPSJOIN algorithm described
above.

The parameter k can be set for each dataset and
similarity threshold λ to minimize the combined cost
of lookups and similarity estimations performed by algo-
rithm. This approach was mentioned by Cohen et al. [12]
but we were unable to ﬁnd an existing implementation.
In practice we set k to the value that results in the
minimum estimated running time when running the ﬁrst
part (splitting step) of the algorithm for values of k in the
range
and estimating the running time by
looking at the number of buckets and their sizes. Once
k is ﬁxed we know that each repetition of the algorithm
has probability at least λk of reporting a pair (x, y) with
λ. For a desired recall ϕ we can therefore
J(x, y)
set L =
ln(1/(1
. In our experiments we
(cid:101)
report the actual number of repetitions required to obtain

2, 3, . . . , 10
}

ϕ))/λk

≥
(cid:100)

−

{

a desired recall rather than using the setting of L required
for worst-case guarantees.

Algorithm 3: MINHASH(S, λ)
Parameters: k

1, L

1.

≥
1 to L do

≥

1 for i
2

←

Initialize hash map buckets[ ].
Sample k MinHash fcts. h
for x

←

S do
buckets[h(x)]

∈

for S(cid:48)

←
buckets do

∈

BRUTEFORCEPAIRS(S(cid:48), λ)

3

4

5

6

7

(h1, . . . , hk)

buckets[h(x)]

x

∪ {

}

C. AllPairs

To compare our approximate methods against a state-
of-the-art exact similarity join we use Bayardo et al.’s
ALLPAIRS algorithm [9] as recently implemented in
the set similarity join study by Mann et al. [7]. The
study by Mann et al. compares implementations of
several different exact similarity join methods and ﬁnds
that the simple ALLPAIRS algorithm is most often the
fastest choice. Furthermore, for Jaccard similarity, the
ALLPAIRS algorithm was at most 2.16 times slower than
the best out of six different competing algorithm across
all the data sets and similarity thresholds used, and for
most runs ALLPAIRS is at most 11% slower than the
best exact algorithm (see Table 7 in Mann et al. [7]).
Since our experiments run in the same framework and
using the same datasets and with the same thresholds
as Mann et al.’s study, we consider their ALLPAIRS
implementation to be a good representative of exact
similarity join methods for Jaccard similarity.

D. BayesLSH

For a comparison against previous experimental work
on approximate similarity joins we use an implementa-
tion of BAYESLSH in C as provided by the BAYESLSH
authors [13], [29]. The BayesLSH package features
a choice between ALLPAIRS and LSH as candidate
generation method. For the veriﬁcation step there is a
choice between BAYESLSH and BAYESLSH-lite. Both
veriﬁcation methods use sketching to estimate similar-
ities between candidate pairs. The difference between
BayesLSH and BayesLSH-lite is that the former uses
sketching to estimate the similarity of pairs that pass
the sketching check, whereas the latter uses an exact
similarity computation if a pair passes the sketching

check. Since the approximate methods in our CPSJOIN
and MINHASH implementations correspond to the ap-
proach of BayesLSH-lite we restrict our experiments to
this choice of veriﬁcation algorithm. In our experiments
we will use BAYESLSH to represent
the fastest of
the two candidate generation methods, combined with
BayesLSH-lite for the veriﬁcation step.

VI. EXPERIMENTS

∈ {

0.5, 0.6, 0.7, 0.8, 0.9

We run experiments using the implementations of
CPSJOIN, MINHASH, BAYESLSH, and ALLPAIRS de-
scribed in the previous section. In the experiments we
perform self-joins under Jaccard similarity for similarity
thresholds λ
. We are primarily
}
interested in measuring the join time of the algorithms,
but we also look at the number of candidate pairs (x, y)
considered by the algorithms during the join as a measure
of performance. Note that the preprocessing step of the
approximate methods only has to be performed once
for each set and similarity measure, and can be re-
used for different similarity joins, we therefore do not
count it towards our reported join times. In practice the
preprocessing time is at most a few minutes for the
largest data sets.

1) Data Sets: The performance is measured across
10 real world data sets along with 4 synthetic data
sets described in Table I. All datasets except for the
TOKENS datasets were provided by the authors of [7]
where descriptions and sources for each data set can
also be found. Note that we have excluded a synthetic
ZIPF dataset used in the study by Mann et al.[7] due
to it having no results for our similarity thresholds of
interest. Experiments are run on versions of the datasets
where duplicate records are removed and any records
containing only a single token are ignored.

In addition to the datasets from the study of Mann et
al. we add three synthetic datasets TOKENS10K, TO-
KENS15K, and TOKENS20K, designed to showcase the
robustness of the approximate methods. These datasets
have relatively few unique tokens, but each token appears
in many sets. Each of the TOKENS datasets were gener-
ated from a universe of 1000 tokens (d = 1000) and each
token is contained in respectively, 10, 000, 15, 000, and
20, 000 different sets as denoted by the name. The sets
in the TOKENS datasets were generated by sampling a
random subset of the set of possible tokens, rejecting
tokens that had already been used in more than the
maximum number of sets (10, 000 for TOKENS10K).
To sample sets with expected Jaccard similarity λ(cid:48) the
size of our sampled sets should be set to (2λ(cid:48)/(1+λ(cid:48)))d.

TABLE I
DATASET SIZE, AVERAGE SET SIZE, AND AVERAGE NUMBER OF
SETS THAT A TOKEN IS CONTAINED IN.

Dataset

# sets / 106

avg. set size

sets / tokens

AOL
BMS-POS
DBLP
ENRON
FLICKR
LIVEJ
KOSARAK
NETFLIX
ORKUT
SPOTIFY
UNIFORM
TOKENS10K
TOKENS15K
TOKENS20K

7.35
0.32
0.10
0.25
1.14
0.30
0.59
0.48
2.68
0.36
0.10
0.03
0.04
0.06

3.8
9.3
82.7
135.3
10.8
37.5
12.2
209.8
122.2
15.3
10.0
339.4
337.5
335.7

18.9
1797.9
1204.4
29.8
16.3
15.0
176.3
5654.4
37.5
7.4
4783.7
10000.0
15000.0
20000.0

∈ {

0.95, 0.85, 0.75, 0.65, 0.55
}

For λ(cid:48)
the TOKENS
datasets each have 100 random sets planted with ex-
pected Jaccard similarity λ(cid:48). This ensures an increasing
number of results for our experiments where we use
0.5, 0.6, 0.7, 0.8, 0.9
thresholds λ
. The remaining
}
sets have expected Jaccard similarity 0.2. We believe
that the TOKENS datasets give a good indication of the
performance on real-world data that has the property that
most tokens appear in a large number of sets.

∈ {

2) Recall: In our experiments we aim for a recall of
at least 90% for the approximate methods. In order to
achieve this for the CPSJOIN and MINHASH algorithms
we perform a number of repetitions after the prepro-
cessing step, stopping when the desired recall has been
achieved. This is done by measuring the recall against
the recall of ALLPAIRS and stopping when reaching
90%. In practice this approach is not feasible as the
size of the true result set is not known. However, it can
be efﬁciently estimated using sampling if it is not too
small. Another approach is to perform the number of
repetitions required to obtain the theoretical guarantees
on recall as described for CPSJOIN in Section IV-C and
for MINHASH in Section V-B. Unfortunately, with our
current analysis of the CPSJOIN algorithm the number
of repetitions required to guarantee theoretically a recall
of 90% far exceeds the number required in practice
as observed in our experiments where ten independent
repetitions always sufﬁce. For BAYESLSH using LSH as
the candidate generation method, the recall probability
with the default parameter setting is 95%, although we

experience a recall closer to 90% in our experiments.

3) Hardware: All experiments were run on an Intel
Xeon E5-2690v4 CPU at 2.60GHz with 35MB L3,256kB
L2 and 32kB L1 cache and 512GB of RAM. Since a
single experiment is always conﬁned to a single CPU
core we ran several experiments in parallel [30] to better
utilize our hardware.

A. Results

1) Join Time: Table II shows the average join time in
seconds over ﬁve independent runs, when approximate
methods are required to have at least 90% recall. We
have omitted timings for BAYESLSH since it was always
slower than all other methods, and in most cases it timed
out after 20 minutes when using LSH as candidate gen-
eration method. The join time for MINHASH is always
greater than the corresponding join time for CPSJOIN
except in a single setting: the dataset KOSARAK with
threshold λ = 0.5. Since CPSJOIN is typically 2
×
faster than MINHASH we can restrict our attention to
comparing ALLPAIRS and CPSJOIN where the picture
becomes more interesting.

−

4

×

−

50

Figure 2 shows the join time speedup that CPSJOIN
achieves over ALLPAIRS. We achieve speedups of be-
tween 2
for most of the datasets, with greater
speedups at low similarity thresholds. For a number of
the datasets the CPSJOIN algorithm is slower than ALL-
PAIRS for the thresholds considered here. Comparing
with Table I it seems that CPSJOIN generally performs
well on most data sets where tokens are contained in a
large number of sets on average (NETFLIX, UNIFORM,
DBLP), but is beaten by ALLPAIRS on datasets that
have a lot of “rare” tokens (SPOTIFY, FLICKR, AOL).
This is logical because rare tokens are exploited by the
sorted preﬁx-ﬁltering in ALLPAIRS. Without rare tokens
ALLPAIRS will be reading long inverted indexes. This
is a common theme among all the current state-of-the-
art exact methods examined in [7], including PPJOIN.
CPSJOIN is robust in the sense that it does not depend
on the presence of rare tokens in the data to perform well.
This difference is showcased with the synthetic TOKEN
data sets.

2) BayesLSH: The poor performance of BAYESLSH
compared to the other algorithms (BAYESLSH was
always slower) can most
likely be tracked down to
differences in the implementation of the candidate gener-
ation methods of BAYESLSH. The BAYESLSH imple-
mentation uses an older implementation of ALLPAIRS
compared to the implementation by Mann et al. [7]
which was shown to yield performance improvements

TABLE II
JOIN TIME IN SECONDS FOR CPSJOIN (CP), MINHASH (MH) AND ALLPAIRS (ALL) WITH AT LEAST ≥ 90% RECALL.

Threshold 0.5

Threshold 0.6

Threshold 0.7

Threshold 0.8

Threshold 0.9

Dataset

CP

MH

ALL

CP

MH

ALL

AOL
BMS-POS
DBLP
ENRON
FLICKR
KOSARAK
LIVEJ
NETFLIX
ORKUT
SPOTIFY
TOKENS10K
TOKENS15K
TOKENS20K
UNIFORM005

362.1
27.0
9.2
6.9
48.6
377.9
131.3
25.3
26.5
2.5
3.4
4.4
5.7
3.9

1329.9
40.0
22.1
16.4
68.0
311.1
279.4
121.8
115.7
9.3
4.8
6.2
12.0
6.6

483.5
62.5
127.9
78.0
17.2
73.1
571.7
1354.7
359.7
0.5
312.1
688.4
1264.1
54.1

113.4
7.1
2.5
4.4
30.9
62.7
48.7
8.2
15.4
1.5
2.9
4.0
4.0
1.6

444.2
13.7
10.1
9.9
37.2
89.2
129.6
60.0
60.1
3.4
3.9
7.1
11.4
3.0

117.8
20.9
63.8
23.2
6.0
14.4
145.3
520.4
106.4
0.3
236.8
535.3
927.0
27.6

CP

42.2
2.7
1.1
2.4
13.8
7.2
28.2
4.8
8.0
1.0
1.5
1.8
2.1
0.9

MH

ALL

CP

MH

ALL

CP MH

ALL

152.9
5.6
3.7
6.3
21.3
16.1
52.9
22.6
25.1
2.6
1.7
3.7
4.5
1.4

13.7
5.6
27.4
6.0
2.5
1.6
30.6
177.3
36.3
0.2
164.0
390.4
698.4
10.5

34.6
2.0
0.6
1.6
6.3
3.9
16.2
2.4
7.4
1.0
0.6
0.7
0.8
0.5

100.6
3.9
1.8
2.7
11.3
9.9
41.0
14.1
19.7
1.9
1.2
1.7
2.2
1.0

4.2
1.3
7.8
1.6
1.0
0.5
7.1
46.2
12.2
0.1
114.9
258.2
494.3
3.6

21.0
0.9
0.3
0.7
3.4
1.2
9.2
1.6
4.8
0.5
0.2
0.2
0.3
0.1

43.8
1.4
0.7
1.7
5.2
2.6
12.6
5.8
13.3
0.6
0.4
0.7
0.8
0.3

1.6
0.2
0.8
0.4
0.3
0.1
1.5
5.4
3.7
0.1
63.2
140.0
273.4
0.4

eration procedures. Further experiments to compare the
performance of BayesLSH sketching to 1-bit minwise
sketching for different parameter settings and similarity
thresholds would also be instructive.

3) TOKEN datasets: The TOKENS datasets clearly
favor the approximate join algorithms where CPSJOIN
is two to three orders of magnitude faster than ALL-
PAIRS. By increasing the number of times each token
appears in a set we can make the speedup of CPSJOIN
compared to ALLPAIRS arbitrarily large as shown by
the progression from TOKENS10 to TOKENS20. The
ALLPAIRS algorithm generates candidates by searching
through the lists of sets that contain a particular token,
starting with rare tokens. Since every token appears in a
large number of sets every list will be long.

Interestingly, the speedup of CPSJOIN is even greater
for higher similarity thresholds. We believe that this is
due to an increase in the gap between the similarity of
sets to be reported and the remaining sets that have an
average Jaccard similarity of 0.2. This is in line with
our theoretical analysis of CPSJOIN and most theoretical
work on approximate similarity search where the running
time guarantees usually depend on the approximation
factor.

4) Candidates and Veriﬁcation: Table IV compares
the number of pre-candidates, candidates, and results
generated by the ALLPAIRS and CPSJOIN algorithms
where the desired recall for CPSJOIN is set to be greater
than 90%. For ALLPAIRS the number of pre-candidates
denotes all pairs (x, y) investigated by the algorithm
that pass checks on their size so that it is possible that
J(x, y)
λ. The number of candidates is simply the
number of unique pre-candidates as duplicate pairs are

≥

Fig. 2.
ALLPAIRS.

Join time of CPSJOIN with at least 90% recall relative to

by using a more efﬁcient veriﬁcation procedure. The
LSH candidate generation method used by BAYESLSH
corresponds to the MINHASH splitting step, but with
k (the number of hash functions) ﬁxed to one. Our
technique for choosing k in the MINHASH algorithm,
aimed at minimizing the total join time, typically selects
k
in the experiments. It is therefore likely
that BAYESLSH can be competitive with the other
techniques by combining it with other candidate gen-

3, 4, 5, 6

∈ {

}

0.50.60.70.80.90.11.010.0100.01000.0ThresholdSpeedup(x)llllllllllllllllllAOLBMS−POSDBLPENRONFLICKRKOSARAKLIVEJNETFLIXORKUTSPOTIFYTOKENS10KTOKENS15KTOKENS20KUNIFORM005(a) limit ∈ {10, 50, 100, 250, 500}

(b) ε ∈ {0.0, 0.1, 0.2, 0.3, 0.4, 0.5}

(c) w ∈ {1, 2, 4, 8, 16}

Fig. 3. Relative join time for CPSJOIN with at least 80% recall and similarity threshold λ = 0.5 for different parameter settings of limit,
ε, and w.

removed explicitly by the ALLPAIRS algorithm.

For CPSJOIN we deﬁne the number of pre-candidates
to be all pairs (x, y) considered by the BRUTEFOR-
CEPAIRS and BRUTEFORCEPOINT subroutines of Al-
gorithm 2. The number of candidates are pre-candidate
pairs that pass size checks (similar to ALLPAIRS) and the
1-bit minwise sketching check as described in Section
V-A. Note that for CPSJOIN the number of candidates
may still contain duplicates as this is inherent to the
approximate method for candidate generation. Remov-
ing duplicates though the use of a hash table would
drastically increase the space usage of CPSJOIN. For
both ALLPAIRS and CPSJOIN the number of candidates
denotes the number of points that are passed to the exact
similarity veriﬁcation step of the ALLPAIRS implemen-
tation of Mann et al. [7].

Table IV shows that for ALLPAIRS there is not a great
difference between the number of pre-candidates and
number of candidates, while for CPSJOIN the number
of candidates is usually reduced by one or two orders
of magnitude for datasets where CPSJOIN performs
well. For datasets where CPSJOIN performs poorly such
as AOL, FLICKR, and KOSARAK there is less of a
decrease when going from pre-candidates to candidates.
It would appear that this is due to many duplicate pairs
from the candidate generation step and not a failure of
the sketching technique.

B. Parameters

To investigate how parameter settings affect the per-
formance of the CPSJOIN algorithm we run experiments

where we vary the brute force parameter limit, the
brute force aggressiveness parameter ε, and the sketch
length in words (cid:96). Table III shows the parameter settings
used during theses experiments and the ﬁnal setting
used for our join time experiments. Figure 3 shows
the CPSJOIN join time for different settings of the
parameters. By picking one parameter at a time we
are obviously ignoring possible interactions between the
parameters, but the stability of the join times lead us to
believe that these interactions have limited effect.

Figure 3 (a) shows the effect of the brute force limit
on the join time. Lowering limit causes the join time
to increase due to a combination of spending more time
splitting sets into buckets and due to the lower proba-
bility of recall from splitting at a deeper level. The join
time is relatively stable for limit

100, 250, 500

Figure 3 (b) shows the effect of brute force aggres-
siveness on the join time. As we increase ε, sets that
are close to the other elements in their buckets are more

∈ {

.
}

TABLE III
PARAMETERS OF THE CPSJOIN ALGORITHM, THEIR SETTING
DURING PARAMETER EXPERIMENTS, AND THEIR SETTING FOR
THE FINAL JOIN TIME EXPERIMENTS

Parameter Description

Test

Final

limit
(cid:96)
t
ε
δ

Brute force limit
Sketch word length
Size of MinHash set
Brute force aggressiveness
Sketch false negative prob.

100
4
128
0.0
0.1

250
8
128
0.1
0.05

01234561050100250500BF limit (index=250)Join timellllllllllllAOLBMS−POSDBLPENRONFLICKRKOSARAKLIVEJNETFLIXORKUTSPOTIFYUNIFORM005012345670.00.10.20.30.40.5Epsilon (index=0.1)Join timellllllllllll01234124816Words in sketch (index=8)Join timelllllllllllikely to be removed by brute force comparing them to
all other points. The tradeoff here is between the loss
of probability of recall by letting a point continue in
the CHOSEN PATH branching process versus the cost
of brute forcing the point. The join time is generally
increasing with ε, but it turns out that ε = 0.1 is a
slightly better setting than ε = 0.0 for almost all data
sets.

Figure 3 (c) shows the effect of sketch length on the
join time. There is a trade-off between the sketch simi-
larity estimation time and the precision of the estimate,
leading to fewer false positives. For a similarity threshold
of λ = 0.5 using only a single word negatively impacts
the performance on most datasets compared to using
two or more words. The cost of using longer sketches
seems neglible as it is only a few extra instructions per
similarity estimation so we opted to use (cid:96) = 8 words in
our sketches.

VII. CONCLUSION

−

We provided experimental and theoretical results on a
new randomized set similarity join algorithm, CPSJOIN,
and compared it experimentally to state-of-the-art exact
and approximate set similarity join algorithms. CPSJOIN
4 times faster than previous approximate
is typically 2
methods. Compared to exact methods it obtains speedups
of more than an order of magnitude on real-world
datasets, while keeping the recall above 90%. Among
the datasets used in these experiments we note that
NETFLIX and FLICKR represents two archetypes. On
average a token in the NETFLIX dataset appears in more
than 5000 sets while on average a token in the FLICKR
dataset appears in less than 20 sets. Our experiments
indicate that CPSJOIN brings large speedups to the
NETFLIX type datasets, while it is hard to improve upon
the perfomance of ALLPAIRS on the FLICKR type.

A direction for future work could be to tighten and
simplify the theoretical analysis. We conjecture that the
running time of the algorithm can be bounded by a
simpler function of the sum of similarities between pairs
of points in S. We note that recursive methods such
as ours lend themselves well to parallel and distributed
implementations since most of the computation happens
in independent, recursive calls. Further investigating this
is an interesting possibility.

TABLE IV
NUMBER OF PRE-CANDIDATES, CANDIDATES AND RESULTS FOR
ALL AND CP WITH AT LEAST 90% RECALL.

Dataset

AOL

BMS-POS

DBLP

ENRON

FLICKR

KOSARAK

LIVEJ

NETFLIX

ORKUT

SPOTIFY

TOKENS10K

TOKENS15K

TOKENS20K

UNIFORM005

Threshold 0.5
CP

ALL

Threshold 0.7
CP
ALL

8.5E+09
8.5E+09
1.3E+08
2.0E+09
1.8E+09
1.1E+07
6.6E+09
1.9E+09
1.7E+06
2.8E+09
1.8E+09
3.1E+06
5.7E+08
4.1E+08
6.6E+07
2.6E+09
2.5E+09
2.3E+08
9.0E+09
8.3E+09
2.4E+07
8.6E+10
1.3E+10
1.0E+06
5.1E+09
3.9E+09
9.0E+04
5.0E+06
4.8E+06
2.0E+04
1.5E+10
4.1E+08
1.3E+05
3.6E+10
9.6E+08
1.4E+05
6.4E+10
1.7E+09
1.4E+05
2.5E+09
2.0E+09
2.6E+05

7.4E+09
1.4E+09
1.2E+08
9.2E+08
1.7E+08
1.0E+07
4.6E+08
4.6E+07
1.6E+06
3.7E+08
6.7E+07
2.9E+06
2.1E+09
1.1E+09
6.1E+07
4.7E+09
2.1E+09
2.1E+08
2.8E+09
3.6E+08
2.2E+07
1.3E+09
3.1E+07
9.5E+05
1.1E+09
1.3E+06
8.4E+04
1.2E+08
3.1E+05
1.8E+04
1.7E+08
5.7E+06
1.3E+05
3.0E+08
7.2E+06
1.3E+05
4.4E+08
8.8E+06
1.4E+05
3.7E+08
9.5E+06
2.4E+05

6.2E+08
6.2E+08
1.6E+06
2.7E+08
2.6E+08
2.0E+05
1.2E+09
7.2E+08
9.1E+03
2.0E+08
1.3E+08
1.2E+06
9.3E+07
6.3E+07
2.5E+07
7.4E+07
6.8E+07
4.4E+05
5.8E+08
5.6E+08
8.1E+05
1.0E+10
3.4E+09
2.4E+04
3.0E+08
2.6E+08
5.6E+03
4.7E+05
4.6E+05
2.0E+02
8.1E+09
4.1E+08
7.4E+04
1.9E+10
9.6E+08
7.5E+04
3.4E+10
1.7E+09
7.9E+04
6.5E+08
6.1E+08
1.4E+03

2.9E+09
3.1E+07
1.5E+06
3.3E+08
4.9E+06
1.8E+05
1.3E+08
4.3E+05
8.5E+03
1.5E+08
2.1E+07
1.2E+06
9.0E+08
3.8E+08
2.3E+07
4.2E+08
2.1E+07
4.1E+05
1.2E+09
1.8E+07
7.6E+05
4.3E+08
6.4E+05
2.2E+04
7.2E+08
8.1E+04
5.3E+03
8.5E+07
2.7E+03
1.9E+02
4.9E+07
1.9E+06
6.9E+04
8.1E+07
1.9E+06
6.9E+04
1.0E+08
1.9E+06
7.4E+04
1.3E+08
3.9E+04
1.3E+03

[17] T. Christiani, “A framework for similarity search with space-
time tradeoffs using locality-sensitive ﬁltering,” in Proc. 28th
Symp. on Discrete Algorithms (SODA). SIAM, 2017, pp. 31–
46.

[18] F. Chierichetti and R. Kumar, “LSH-preserving functions and
their applications,” Journal of the ACM, vol. 62, no. 5, p. 33,
2015.

[19] D. Chakraborty, E. Goldenberg, and M. Kouck`y, “Streaming al-
gorithms for embedding and computing edit distance in the low
distance regime.” in Proc. 48th Symp. on Theory of Computing
(STOC), 2016, pp. 712–725.

[20] H. Zhang and Q. Zhang, “EmbedJoin: Efﬁcient Edit Similarity

Joins via Embeddings,” ArXiv e-prints, Jan. 2017.

[21] R. Pagh, N. Pham, F. Silvestri, and M. St¨ockel, “I/O-efﬁcient
similarity join,” in Proc. 23rd European Symp. on Algorithms
(ESA), 2015, pp. 941–952.

[22] T. E. Harris, The theory of branching processes.

Courier

Corporation, 2002.

[23] H. W. Watson and F. Galton, “On the probability of the
extinction of families,” The Journal of
the Anthropological
Institute of Great Britain and Ireland, vol. 4, pp. 138–144, 1875.
[24] A. Agresti, “Bounds on the extinction time distribution of a
branching process,” Advances in Applied Probability, vol. 6,
pp. 322–335, 1974.

[25] T. D. Ahle, M. Aum¨uller, and R. Pagh, “Parameter-free locality
sensitive hashing for spherical range reporting,” in Proc. 28th
Symp. on Discrete Algorithms (SODA), 2017, pp. 239–256.
[26] A. L. Zobrist, “A new hashing method with application for game
playing,” ICCA journal, vol. 13, no. 2, pp. 69–73, 1970.
[27] M. Pˇatras¸cu and M. Thorup, “The power of simple tabulation
hashing,” Journal of the ACM, vol. 59, no. 3, pp. 14:1–14:50,
Jun. 2012.

[28] M. Thorup, “Fast and powerful hashing using tabulation,”
Commun. ACM, vol. 60, no. 7, pp. 94–101, Jun. 2017.
[Online]. Available: http://doi.acm.org/10.1145/3068772
[29] A. Chakrabarti, V. Satuluri, A. Srivathsan, and S. Parthasarathy,
“Locality sensitive hashing for similarity search and estima-
tion,” https://sites.google.com/site/lshallpairs/, 2012, [Accessed
15-May-2017].

[30] O. Tange, “Gnu parallel - the command-line power tool,”
;login: The USENIX Magazine, vol. 36, no. 1, pp. 42–47, Feb
2011. [Online]. Available: http://www.gnu.org/s/parallel

ACKNOWLEDGMENTS

The authors would like to thank Willi Mann for mak-
ing the source code and data sets of [7] available, Aniket
Chakrabarti for information about the implementation
of BayesLSH, and the anonymous reviewers for useful
suggestions.

REFERENCES

[1] N. Augsten and M. H. B¨ohlen, “Similarity joins in relational
database systems,” Synthesis Lectures on Data Management,
vol. 5, no. 5, pp. 1–124, 2013.

[2] S. Chaudhuri, V. Ganti, and R. Kaushik, “A primitive operator
for similarity joins in data cleaning,” in Proc. 22nd Conference
on Data Engineering (ICDE), 2006, p. 5.

[3] S. Sarawagi and A. Kirpal, “Efﬁcient set joins on similarity
predicates,” in Proc. SIGMOD International Conference on
Management of Data. ACM, 2004, pp. 743–754.

[4] S. Choi, S. Cha, and C. C. Tappert, “A survey of binary
similarity and distance measures,” J. Syst. Cybern. Informatics,
vol. 8, no. 1, pp. 43–48, 2010.

[5] T. Christiani and R. Pagh, “Set similarity search beyond min-
hash,” in Proc. 49th Symp. on Theory of Computing (STOC),
2017.

[6] P. Li and A. C. K¨onig, “Theory and applications of b-bit
minwise hashing,” Comm. of the ACM, vol. 54, no. 8, pp. 101–
109, 2011.

[7] W. Mann, N. Augsten, and P. Bouros, “An empirical evaluation
of set similarity join techniques,” Proc. VLDB Endowment,
vol. 9, no. 9, pp. 636–647, 2016.

[8] A. Z. Broder, “Identifying and ﬁltering near-duplicate docu-
ments,” in Proc. Symp. on Combinatorial Pattern Matching
(CPM). Springer, 2000, pp. 1–10.

[9] R. J. Bayardo, Y. Ma, and R. Srikant, “Scaling up all pairs
similarity search,” in Proc. 16th World Wide Web Conference
(WWW), 2007, pp. 131–140.

[10] C. Xiao, W. Wang, X. Lin, J. X. Yu, and G. Wang, “Efﬁcient
similarity joins for near-duplicate detection,” ACM Transactions
on Database Systems (TODS), vol. 36, no. 3, p. 15, 2011.
[11] A. Gionis, P. Indyk, and R. Motwani, “Similarity search in
high dimensions via hashing,” in Proc. 25th Conference on Very
Large Data Bases (VLDB), 1999, pp. 518–529.

[12] E. Cohen, M. Datar, S. Fujiwara, A. Gionis, P. Indyk, R. Mot-
wani, J. D. Ullman, and C. Yang, “Finding interesting as-
sociations without support pruning,” IEEE Transactions on
Knowledge and Data Engineering, vol. 13, no. 1, pp. 64–78,
2001.

[13] A. Chakrabarti, V. Satuluri, A. Srivathsan, and S. Parthasarathy,
“A bayesian perspective on locality sensitive hashing with ex-
tensions for kernel methods,” ACM Transactions on Knowledge
Discovery from Data (TKDD), vol. 10, no. 2, p. 19, 2015.
[14] R. Pagh, “Large-scale similarity joins with guarantees (invited
in Informatics,
Schloss Dagstuhl-Leibniz-Zentrum fuer Informatik,

talk),” in LIPIcs-Leibniz International Proc.
vol. 31.
2015.

[15] A. Z. Broder, S. C. Glassman, M. S. Manasse, and G. Zweig,
“Syntactic clustering of the web,” Computer Networks, vol. 29,
no. 8-13, pp. 1157–1166, 1997.

[16] A. Andoni, T. Laarhoven, I. Razenshteyn, and E. Waingarten,
“Optimal hashing-based time-space trade-offs for approximate
near neighbors,” in Proc. 28th Symp. on Discrete Algorithms
(SODA), 2017.

