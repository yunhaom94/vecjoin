DiskANN++: Efficient Page-based Search over
Isomorphic Mapped Graph Index using
Query-sensitivity Entry Vertex

Jiongkang Ni1, Xiaoliang Xu1, Yuxiang Wang1, Can Li1, Jiajie Yao2, Shihai Xiao2, Xuecang Zhang2
1 Hangzhou Dianzi University, Hangzhou, China, 2 Huawei Technologies Co., Ltd, Hangzhou, China
{hananoyuuki,xxl,lsswyx,lic}@hdu.edu.cn, {yaojiajie1,xiaoshihai,zhangxuecang}@huawei.com

3
2
0
2

v
o
N
0
3

]

R

I
.
s
c
[

5
v
2
0
4
0
0
.
0
1
3
2
:
v
i
X
r
a

Abstract—Given a vector dataset X and a query vector ⃗xq,
graph-based Approximate Nearest Neighbor Search (ANNS) aims
to build a graph index G and approximately return vectors
with minimum distances to ⃗xq by searching over G. The main
drawback of graph-based ANNS is that a graph index would
be too large to fit into the memory especially for large-scale X .
To solve this, a Product Quantization (PQ)-based hybrid method
called DiskANN is proposed to store a low-dimensional PQ index
in memory and retain a graph index in SSD, to reduce memory
overhead while ensuring a high search accuracy. However, it
suffers from two I/O issues that significantly affect the overall ef-
ficiency: (1) long routing path from the entry vertex to the query’s
neighborhood and (2) redundant I/O requests during the routing
process. We propose an optimized DiskANN++ to overcome above
issues. Specifically, for the first issue, we present a query-sensitive
entry vertex selection strategy to replace DiskANN’s static graph-
central entry vertex by a dynamically determined entry vertex
that is close to the query. For the second I/O issue, we present
an isomorphic mapping on DiskANN’s graph index to optimize the
SSD layout and propose an asynchronously optimized Pagesearch
based on the optimized SSD layout as an alternative to DiskANN’s
Beamsearch. Comprehensive experimental studies on real-world
datasets demonstrate our DiskANN++’s superiority on efficiency,
e.g., we achieve a notable 1.5 X to 2.2 X improvement on QPS
compared to DiskANN, given the same accuracy constraint.

I. INTRODUCTION

Approximate Nearest Neighbor Search (ANNS) [1], [2] has
been widely studied recently, which is fundamental for many
real-world applications, such as recommendation systems [3],
[4], information retrieval [5], [6], data mining [7], [8], and
pattern recognition [9], [10]. Given a vector dataset X and
a query vector ⃗xq ∈ X , ANNS aims to return approximate
nearest neighbors to ⃗xq from X with minimum distance [11].
ANNS is generally categorized as four types: hashing-based
[12], [13], tree-based [14], [15], quantization-based [16], [17],
and graph-based [18], [19] methods. Among them, graph-
based ANNS attracts more attention and has been regarded as
the most promising one due to its impressive efficiency and
effectiveness over large-scale datasets [11], [18], [20]–[25].

Graph-based ANNS uses a graph index (e.g., NSG [18],
HNSW [19], etc.) maintained in the memory to facilitate
approximate nearest neighbors retrieval. Each vertex in a graph
index represents a vector in X , and an edge between two
vertices defines a neighbor relationship. During the retrieval
phase, a graph routing over the graph index is conducted,
starting from an entry vertex and iteratively exploring the

graph index towards the query ⃗xq until it converges [19]. The
main limitation comes from the heavyweight memory overhead
of a graph index. The memory overhead significantly increases
as X increases, e.g., using HNSW for a billion-scale X in 128
dimensions would consume around 800 GB memory, which
largely exceeds the RAM capacity on a workstation.

Existing solutions. Many efforts have been made to allevi-
ate the memory issue of graph-based ANNS for large-scale
datasets [20], [26], [27]. The basic idea is to introduce external
drives (e.g., SSD) to store high-dimensional vectors, thereby
reducing memory overhead. SPANN [20] clusters on the
dataset and uses the centroids to construct a spatial partitioning
tree (SPT) that resides in memory. High-dimensional vectors
within each cluster are stored on SSD. BBANN [26] conducts
balanced clustering on the dataset and uses the clustered
centroids to build a graph index maintained in memory. High-
dimensional vectors within each cluster are stored on SSD. The
search accuracy of the above methods is significantly affected
by the coarse-grained SPT or graph index built on clustered
centroids, resulting in a noticeable accuracy loss [28].

DiskANN [27]. This inspires DiskANN, a Product Quanti-
zation (PQ)-based hybrid (memory+SSD) method that aims
to reduce memory overhead while ensuring a high search
accuracy. It first conducts PQ for original high-dimensional
vectors to obtain the quantized low-dimensional vectors, then
stores a PQ index for quantized vectors in memory and a
graph index for original vectors in SSD. PQ index serves for
lossy distance calculations, based on which initial candidate
neighbors are provided. Graph index serves for re-ranking
candidate neighbors based on original vectors, which is a post-
verification of lossy distances, so as to enhance the search
accuracy. We refer readers to [27] and §II for more details.
DiskANN has been widely deployed in the industry such as
Bing search of Microsoft [29] and many follow-up works
present variants of DiskANN to support their own scenarios,
e.g., Filter-DiskANN for filtered search [30], OOD-DiskANN
for cross-modal search [31], and Fresh-DiskANN for stream-
ing search [32]. Although DiskANN and its variants achieve
a good performance on both memory overhead and search
accuracy, they all ignore the important I/O issue (frequent
SSD I/O requests for candidates re-ranking) that significantly
affect the queries per second (QPS). In general, the latency

Fig. 1: Search examples on DiskANN (top) and DiskANN++ (bottom), given the same query vertex and the Vamana graph
index with the same topological structure but different SSD layout.

of accessing SSD is 10X+ greater than that of accessing
memory, the more the SSD I/O requests, the more the time
for DiskANN. We next discuss the I/O issue of DiskANN.

I/O issue of DiskANN. Figure 1 (top) illustrates the search
process of DiskANN on the Vamana graph index. Vertices in
Vamana are assigned to SSD pages in a round-robin, e.g., 6
pages for 18 vertices in this example. Given a query vertex
(the red star), DiskANN adopts beamsearch (discussed in §II)
to retrieve the top-k results. It starts from the static entry
vertex (i.e., the central vertex of a graph index) to explore
a routing path towards query’s neighborhood. We call this
the nearest neighbor approaching (NN approaching) phase
[33]. DiskANN first reads SSD to get the Page-5 involving
then takes v1 as candidate for node
the entry vertex v1,
expansion and discard the other nodes. In the step of node
expansion, DiskANN computes the distances between candi-
dates’ neighbors to query and requests SSD Page-4 to obtain
the closest vertex v2. It repeats until the search locates in
the neighborhood of query (indicated by a red dashed circle).
NN approaching stops when v4 is explored. Next, DiskANN
goes into the nearest neighbor refine (NN refine) phase to find
the top-k nearest neighbors to query via a nearly brute-force
vertex traversal in the query’s neighborhood, and both Page-0
and Page-4 are requested to obtain v4’s two neighbors v5, v6.
The I/O issue of DiskANN is two-fold: (1) Long routing
path in NN approaching phase and (2) Redundant I/O requests
in NN refine phase. For (1), since DiskANN takes the graph-
central vertex as a static entry vertex for all queries, it would
result in a long routing path in NN approaching phase, when
the query is far away from the entry vertex. In above example,
it needs 3 hops from v1 to query’s neighborhood, yielding
4 SSD I/O requests out of the total 6 requests. In practice,
queries often arrive randomly, which leads to a large number
of long routing paths, so that affecting the overall efficiency.
For (2), since DiskANN adopts a random SSD layout, it would
result in redundant I/O requests in NN refine phase, when
vertices on the same SSD page have less closeness in the
graph index. In this example, each accessed page only involves

one useful vertex for beamsearch, reducing the data value of
each I/O request and leading two redundant I/O requests of
Page-0 and Page-4. Actually, they have been accessed in NN
approaching phase, however, DiskANN does not know they
would be required later and directly discard them as instead.
The aforementioned I/O issue inspires our study in this
paper to shorten the routing path and improve the effectiveness
of each I/O request (i.e., making an I/O request carry more
useful vertices), so that significantly reduces the total number
of I/O requests and increases the overall QPS of DiskANN.
Our solution. We next briefly introduce our solution below.
(1) Query-sensitive entry vertex selection (§III). For the long
routing path problem, we present a query-sensitive entry vertex
selection strategy to dynamically determine the entry vertex
in run-time instead of the original static graph-central entry
vertex (§III-A). Given a vector dataset X and a Vamana graph
built for X , we first cluster the dataset to acquire Ncluster
centroids, then we take each centroid as a query to perform
ANNS on Vamana to find its top-1 nearest vertex, and finally
we add all the Ncluster nearest vertices and the graph-central
vertex into an entry vertex candidate list. For each incoming
query ⃗xq, we linearly scan the candidate list and employ the
nearest vertex to ⃗xq as the entry vertex. In Figure 1 (bottom),
we may select v3 as the entry vertex, leading a 1-hop routing
path to query’s neighborhood. In §III-B, we leverage the
monotonicity of MSNET [34], [35] to theoretically prove that
using query-sensitive entry vertex would result in a shorter
routing path than that of graph-central entry vertex. The shorter
routing path usually indicates the less SSD I/O requests.

For redundant I/O issue, we present: isomorphic mapping

of graph index and page-level optimization to beamsearch.
(2) Isomorphic mapping of graph index (§IV). Here, we pro-
pose an isomorphic mapping on Vamana to optimize the SSD
layout. We first apply an injective mapping via star packing
[36] on the original Vamana. It effectively assigns the vertices
with great closeness into the same SSD page, so that increasing
the data value of each individual I/O request. Then, we apply
bin packing based on First Fit Decreasing (FFD) to make the

𝑣1𝑣4𝑣2𝑣6𝑣5𝑣3𝑣1𝑣4𝑣6𝑣30123𝑣5𝑣245SSD pagesOriginal VamanaNN approachingNN refine𝑣4𝑣6𝑣5𝑣3𝑣3𝑣40123𝑣5𝑣645SSD pagesIsomorphic VamanaNN approachingNN refinePackingMergingRead pages𝑣2𝑣5𝑣3𝑣4𝑣6𝑣5𝑣6𝑣2𝑣4TURN 3TURN 4TURN 1TURN 2TURN 5Page 5Page 4Page 1Page 0Page4Page0𝑣1candidatesdiscardIsomorphic Mapping (Section 4)node expansionTop-k𝑣4𝑣5𝑣6Beamsearch𝑣4TURN 1TURN 2Page 1Page 4candidatespage heapnode expansionTop-k𝑣4𝑣5𝑣6𝑣3𝑣6𝑣5page expansionPagesearch(Section 5)DiskANNDiskANN++Graph-central entry vertexQuery（Section 3）Read pagesQuery-sensitive entry vertex(c) show results using beamsearch and pagesearch with the
same static entry vertex, we found that the SSD I/O requests
in NN refine phase are reduced by at least 50%. Figure 2
(d) shows the results using pagesearch with query-sensitive
entry vertex, i.e., our DiskANN++. Comparing with DiskANN
(Figure 2 (a)), ours achieves a better I/O efficiency in both two
phases, leading to a 2 X improvement on QPS.
Contributions. Our contributions can be concluded as follows.
• We propose a query-sensitive entry vertex selection strat-
egy to determine entry vertex dynamically (§III-A) and
prove its effectiveness theoretically (§III-B).

• We present an isomorphic mapping on Vamana to refine
the SSD layout (§IV-A) and analyze its effectiveness
using a metric of page compactness (§IV-B).

• We design a novel search algorithm called Pagesearch
with page-level optimizations based on the refined SSD
layout (§V), which utilizes idle CPU resources to update
global candidates with more valuable vertices.

• Extensive experiments (§VI) conducted on eight public
and commercial datasets with different types and scales,
show that our solution achieves a notable QPS improve-
ment ranging from 1.5 X to 2.2 X.

II. PRELIMINARY
Definition 1. ANNS [11]. Given a vector dataset X , a query
vector ⃗xq, and a parameter ε > 0, the goal of ANNS is to find
the top-k vectors {⃗x1, · · · , ⃗xk} from X that are approximate
nearest neighbors to ⃗xq. We say a vector ⃗xi ∈ X is an approx-
imate nearest neighbor to ⃗xq if δ(⃗xi, ⃗xq) ≤ (1 + ε) · δ(⃗x∗
i , ⃗xq),
where ⃗x∗
i ∈ X is the i-th nearest neighbor vector of ⃗xq and ε is
an relaxation parameter controlling the top-k results’ quality.

Definition 2. Graph index. Given a vector dataset X and a
non-negative distance threshold ¯δ, the graph index of X w.r.t.
¯δ is a graph G = (V, E) with the vertex set V and edge set
E. (1) There is a bijection ϕ : X → V , ∀⃗xv ∈ X , ∃v ∈ V
satisfying v = ϕ(⃗xv), i.e., each vertex v ∈ V corresponds to
a vector ⃗xv ∈ X . (2) For any two vertices vi, vj ∈ V (i ̸= j),
there exists an edge e(vi, vj) ∈ E iff δ(⃗xvi , ⃗xvj ) < ¯δ.
Definition 3. Recall@k. Given a query vector ⃗xq, R∗ records
the ground-truth nearest neighbors with k vectors from X and
R records k approximate nearest neighbors returned by ANNS.
Then we define the Recall@k as follows.

Recall@k =

|R∗ ∩ R|
|R∗|

=

|R∗ ∩ R|
k

(1)

Definition 4. Queries Per Second (QPS). QPS is a metric
indicating the number of queries that an ANNS method can
handle per second. Suppose an ANNS method processes Nq
queries withinT seconds, then we have QPS = Nq/T .

Briefly introduction to DiskANN. We briefly introduce the
SSD layout of the graph index and beamsearch used in
DiskANN, which is important for understanding our solution.
Original SSD layout. DiskANN employs a straightforward
method to store the graph index G = (V, E) in SSD.

Fig. 2: Performance comparison on deep100M.

injective mapping also surjective, i.e., converting the injection
to bijection (or isomorphic mapping), thereby ensuring that the
original graph’s topology and addressing mode are preserved
in the new SSD layout. In Figure 1 (bottom), we show the
refined SSD layout with colored vertices. Note that, vertices
that are close to each other are likely to be assigned to the
same SSD page. Suppose we start search from v3 and v4 is
the next-hop vertex of routing. Since they are retained in the
same SSD page, we only need one SSD I/O request for Page-1
to access them simultaneously. Similarly, we only require one
SSD I/O request for Page-4 to access v5 and v6 simultaneously.

(3) Page-level optimizations to beamsearch (§V). On the ba-
sis of the refined SSD layout above, we present a new search
algorithm with page-level optimizations called Pagesearch as
an alternative to beamsearch. The basic idea is to harness the
idle CPU resources during SSD I/O requests to further mitigate
the search latency. Since we apply isomorphic mapping on
Vamana, each page contains more valuable vertices that would
be used in the future. So, we design a novel component called
page heap to asynchronously cache the valuable vertices from
previously accessed pages. Next, we expand search from the
cached valuable vertices via an asynchronous page expansion
using the idle CPU resources while waiting the results of SSD
I/O requests. The vertices obtained by page expansions would
be added into the global candidates for the node expansion of
beamsearch. In a nutshell, the page expansion is a complement
to node expansion by providing more useful candidates from
the previously accessed pages. It is a concurrent operation with
SSD I/O requests without introducing extra latency.

Figure 2 shows an ablation analysis of DiskANN using
beamsearch and pagesearch with static entry vertex and query-
sensitive entry vertex (four combinations in total), given the
same queries under the same recall@100 of 99%. The X-axis
is the sequence of I/O requests and Y-axis shows the average
vector distance over all accessed vertices in an I/O request to
the query. We use the blue (orange) points in plot to represent
the I/O requests in NN approaching (NN refine) phase. As
more I/O requests are performed, the search is getting closer to
the query. Figure 2 (a)-(b) show results using beamsearch with
different entry vertex strategies, we found that using query-
sensitive entry vertex would significantly reduce the SSD I/O
requests in NN approaching phase from 32 to 8. Figure 2 (a)-

50% cutoff50% cutoffAlgorithm 1: Beamsearch(G, ⃗xq, B, Ls, k)
Input: G, ⃗xq, B, Ls, k of top-k
Output: approximate nearest top-k neighbors R to ⃗xq
// Initialization: lines 1-3

1 ve ← central vertex of G ;
2 C ← {ve} ;
3 R ← ∅ ;
4 do
5

/* static entry vertex */
/* candidates initialized as {ve} */
/* top-k results initialized as ∅ */

F ← top-B unvisited vertices from C for expansion ;
// prepare SSD I/O requests: line 6-10
P ← ∅ ;
for vi ∈ F do

/* page placeholders */

Pj ← register read for page containing bvi ;
P ← P ∪ Pj ;

end
// SSD I/O requests: line 11
read all required pages in P from SSD ;
// Node expansion: lines 12-15
for vi ∈ F do

bvi = ⟨⃗xvi , N (vi)⟩ ← obtained from P ;
NeighborExpansion(⃗xq, bvi , C, R, Ls, k) ;

6

7

8

9

10

11

12

13

14

end
15
16 while F ̸= ∅;
17 return R;

Algorithm 2: NeighborExpansion(⃗xq, bv, C, R, Ls, k)
Input: ⃗xq, bv = ⟨⃗xv, N (v)⟩, C,R, Ls, k of top-k

pop back from C ;

/* sort C by PQ distance to ⃗xq */

1 C ← C ∪ N (v) ;
2 while |C| > Ls do
3
4 end
5 R ← R ∪ {⃗xv} ; /* sort R by full distance to ⃗xq */
6 while |R| > k do
7
8 end

pop back from R ;

Definition 5. Data block. Given a vertex v ∈ V , we define the
data block of v as bv = ⟨⃗xv, N (v)⟩, which is the basic unit for
SSD storage. (1) ⃗xv ∈ X is the vector of v. (2) N (v) recodes
the identities of v’s neighbors in G. (3) We use v to indicate
the identity of the data block bv, denoted by bv.ID = v.

DiskANN stores the data blocks of all |V | vertices to SSD
pages in a round-robin with page alignment. We use L =
{P1, · · · , Pn} to denote the SSD layout with n pages and each
P = {bv1, · · · , bvb } contains b data blocks. For simplicity, in
the rest of this paper, we use L.IDs = {P1.IDs, · · · , Pn.IDs}
to denote the logic view of a layout that only consists of the
identities of all data blocks, where P.IDs = {v1, · · · , vb}.
Beamsearch. Beamsearch is the core search algorithm of
DiskANN, but the details are ignored in [27]. Given an SSD-
resident graph index G = (V, E) of the vector dataset X , query
vector ⃗xq, beam size B, search width Ls, and the size k of top-
k results, Algorithm 1 shows the procedure of beamsearch. (1)
It starts search from a static graph-central entry vertex ve ∈ V
with a candidate set C = {ve} and an empty top-k results
R (lines 1-3). It’s worth mentioning that vertices in C are
ranked in ascending order of their PQ distances to ⃗xq using the
memory-resident quantized vectors. While the vertices in R
are ranked in ascending order of their full distances to ⃗xq using
the SSD-resident original vectors. (2) It chooses the unvisited
top-B vertices (at most B) from C, denoted by F and creates

a page placeholder Pj into P to register read request (line 6-
10). Finally, it reads all required pages from SSD (line 11). (3)
It uses all vertices from F to perform node expansion (lines
12-15). The node expansion phase mainly consists of B times
NeighborExpansion (Algorithm 2). NeighborExpansion uses a
data block bv = ⟨⃗xv, N (v)⟩ to update C with the neighbors
N (v) in ascending order of PQ distance to ⃗xq and ensure C’s
length ≤ Ls. Then, it updates the top-k results R with ⃗xv in
ascending order of full distance to ⃗xq and ensure R ’s length
≤ k. The re-ranking operation to R is the key to guarantee
the search accuracy. (4) It repeats above until no new vertex
is visited and returns R as the top-k results.
Problem definition. Given a vector dataset X , a memory
constraint M , a graph index G built for X , and a query vector
⃗xq, DiskANN aims to maintain a PQ index within M size in
memory and leverage the SSD-resident G to return the top-k
approximate nearest neighbors to ⃗xq with a high Recall@k.
Our goal. On this basis, our goal in this paper is: Given the
conditions unchanged, we aim to design a refined SSD layout
of graph index and a new search algorithm based on such
layout, to retrieve the top-k results having the same Recall@k
as DiskANN, while improving the QPS by reducing the SSD
I/O requests, i.e., increasing QPS without sacrificing accuracy.

III. QUERY-SENSITIVE ENTRY VERTEX

To solve the first I/O issue of DiskANN, we present a query-

sensitive entry vertex selection strategy discussed in §III-A.

A. Method Overview

Offline candidate entry vertices generation. Given a vector
dataset X and the Vamana graph index G of X , we generate
the entry vertex candidates as follows. First, we employ the
mini-batch-kmeans [37] to cluster X into Ncluster clusters
{c1, · · · , cNcluster}. Second, we take each ci’s centroid as
an input query ⃗xq to find its top-1 nearest neighbor from
G. Finally, we record all the nearest neighbors for Ncluster
centroids in a linear table as the entry vertex candidates.
Online entry vertex selection. Since each candidate is a
representative vertex of a partition of X , it’s reasonable to
take it as the entry vertex when the incoming query locates
in the same partition. To this end, given the candidate entry
vertices and a query vertex ⃗xq, we select a candidate entry
vertex with the closest distance to ⃗xq as the entry vertex.

B. Theoretical Analysis of Effectiveness

We next

theoretically prove that using query-sensitivity
entry vertex can provide a tighter upper bound on the routing
length than that of graph-central entry vertex. Since the
graph index of DiskANN is developed based on Monotonic
Search Network (MSNET) [27], similar to [18], we leverage
MSNET’s monotonicity to complete our analysis.

Definition 6. Monotonic Path. Given a graph index G(V, E)
for a vector dataset X . Let vs, vt ∈ V , an l-hop path P(vs, vt)
from vs to vt is a Monotonic Path, iff ∃v1, · · · , vl+1 ∈ V (v1 =
vs, vl+1 = vt) satisfying: (1) each pair of adjacent vertices in

P has an edge e(vi, vi+1) ∈ E, (2) δ(ϕ−1(vt), ϕ−1(vi+1)) <
δ(ϕ−1(vt), ϕ−1(vi)), where ϕ−1(v) denotes v’s vector ⃗xv ∈ X
(Definition 2). This implies that the greater the number of hops
(in a path) from vi to vt, the larger the vector distance between
them. We call such a path a monotonic path MP(vs, vt).

Definition 7. Monotonic Search Network. Given a graph
index G(V, E) for a vector dataset X . G is a Monotonic
Search Network, iff ∀vs, vt ∈ V, ∃MP(vs, vt) on G.

We provide a theorem showing the relation between the
entry vertex and the upper bound on a routing path’s length.

Theorem 1. Given a vector dataset X distributed in a unit
sphere B in Rd, a MSNET G(V, E), and a query ⃗xq ∈ B. For
query-sensitivity entry vertex, we have Ncluster entry vertex
}, where vcj is the top-1 nearest
candidates {vc1, · · · , vcNcluster
neighbor to the centroid of cluster cj. For the static entry
vertex used in DiskANN, we use vc0 to denote the graph-
central vertex. ⃗xq∗ is the top-1 nearest neighbor of ⃗xq within X
(vq∗ = ϕ(⃗xq∗ ) is the vertex in G). Given above assumptions,
the following inequality holds for ∃j ∈ {1, · · · , Ncluster}:

(cid:12)MP(vcj , vq∗ )(cid:12)
(cid:12)

(cid:12) ≤ |MP(vc0 , vq∗ )|

,

(2)

where |MP(·, ·)| represents the upper bound on the length of
a Monotonic Path, i.e., the number of hops.

Proof. We prove this theorem with the following two cases.
Case 1. Suppose Ncluster = 1, then we have vc1 = vc0 . This
is because c1 is the entire graph G and the central vertex of G
actually is the top-1 nearest neighbor of c1’s centroid. Thus,
we have |MP(vc1 , vq∗ )| = |MP(vc0, vq∗ )|.
Case 2. For Ncluster > 1, we introduce the concept of open
sphere to derive the upper bound on a routing path’s length.
Let H(⃗xq∗ , θ) denotes an open sphere in Rd with center ⃗xq∗
and radius θ, Hvol(⃗xq∗ , θ) denotes the volume of H(⃗xq∗ , θ).
Considering a monotonic path MP(vcj , vq∗ ) involving ver-
tices {v1, · · · , vl+1, vq∗ } (v1 = vcj
is an entry vertex), for
simplicity, we use the notation Voli to denote the volume of a
sphere, i.e., Voli = Hvol(⃗xq∗ , δ(⃗xq∗ , ⃗xvi)), for i ∈ {1, 2, ..., l}.
Since the volume of a sphere is calculated as

Hvol(·, θ) =

√

(
Γ( d

πθ)d
2 ) + 1

,

then we have the following for i ∈ {1, 2, ..., l}:

Voli+1
Voli

= (

δ(⃗xq∗ , ⃗xvi+1)
δ(⃗xq∗ , ⃗xvi)

)d

.

cj,

cluster

its diameter

(cid:12)δ(⃗xq∗ , ⃗xvi ) − δ(⃗xq∗ , ⃗xvj )(cid:12)

We next show the relationship between δ(⃗xq∗ , ⃗xvi+1)
and δ(⃗xq∗ , ⃗xvi). Given a
is
R = max(δ(⃗xu, ⃗xv)) for ⃗xu, ⃗xv ∈ cj. We use R∗ =
min (cid:12)
(cid:12) to represent the minimum dis-
tance difference in any monotonic path MP(vs, vq∗ ) from an
arbitrary vertex vs to vq∗ , where vi, vj ∈ MP(vs, vq∗ ) for
i ̸= j. According to Definition 6, we have δ(⃗xq∗ , ⃗xvi) >
δ(⃗xq∗ , ⃗xvi+1), so that δ(⃗xq∗ , ⃗xvi) − δ(⃗xq∗ , ⃗xvi+1) ≥ R∗ >
0 naturally holds. Thereby, due to R ≥ δ(⃗xq∗ , ⃗xvi) ≥

(3)

(4)

δ(⃗xq∗ , ⃗xvi ) − δ(⃗xq∗ , ⃗xvi+1) ≥ R∗, we have

R · (δ(⃗xq∗ , ⃗xvi ) − δ(⃗xq∗ , ⃗xvi+1 )) ≥ δ(⃗xq∗ , ⃗xvi ) · R∗

⇒

R − R∗
R

≥

δ(⃗xq∗ , ⃗xvi+1 )
δ(⃗xq∗ , ⃗xvi )

.

According to Eq. 4 and Eq. 5, we have

Voli+1
Voli

≤ (

R − R∗
R

)d

.

Given Vol = Hvol(⃗xq∗ , R), we have:

Voll+1 ≤ Voll · (

≤ Vol1 · (

R − R∗
R
R − R∗
R

)d

)ld ≤ Vol · (

R − R∗
R

)ld

⇒ log(Voll+1) ≤ log(Vol) + ld · log(

R − R∗
R

)

⇒ l ≤

log(δ(⃗xq∗ , ⃗xvl+1 )) − log(R)
log(R − R∗) − log(R)

≜ f (R)

.

(5)

(6)

(7)

Above derivation shows the upper bound on the length of l

is f (R), we next analyze the monotonicity of f (R) as

df
dR

=

+

[log R − log(R − R∗)]

1
R
(log(R − R∗) − log(R))2
(log R − log δ(⃗xq∗ , ⃗xvl+1 ))(

1

R−R∗ − 1

R

(log(R − R∗) − log(R))2

(8)

)

.

Since we have the following inequalities:

• log R − log(R − R∗) > 0
,
• log R − log δ(⃗xq∗ , ⃗xvl+1) > 0
> 0
•

R−R∗ − 1

R

1

,

,

f (R) is monotonically increasing. Moreover, since we assume
Ncluster > 1, we have R ≤ 1
(cid:12)
(cid:12)MP(vcj , vq∗ )(cid:12)

2 and the following holds.

) + 1 = |MP(vc0 , vq∗ )|

(cid:12) = f (R) + 1 ≤ f (

(9)

1
2

C. Complexity Analysis

Complexity. The time complexity of offline candidates gener-
ation stems from the mini-batch-kmean, which is O(r·Nbatch ·
Ncluster·d) [37], where r is the number of clustering iterations,
Nbatch is the mini-batch size, Ncluster is the number of entry
vertices, and d is the dimensionality of a vector dominating
the distance calculation’s cost. The time complexity of online
entry vertex selection arises from the distance calculations
between each candidate and ⃗xq, which is O(Ncluster · d).
Remarks. (1) The efficiency improvement brought by query-
sensitivity entry vertex comes from the trade-off between the
time spent for online entry vertex selection (in memory) and
the time saved for SSD I/O. Since reading an SSD page is at
least 10 X slower than that of reading memory, it’s natural that
we have a good efficiency compared with DiskANN. (2) In
practical, we prefer a smaller Ncluster to decrease the overhead
of query-sensitivity entry vertex selection, when SSD’s I/O
bandwidth is large (or we say that SSD I/O is fast). Otherwise,
a larger Ncluster would be better. We experimentally show
Nclsuter’s effect under diverse SSD I/O bandwidth in §VI-E.

Fig. 3: Isomorphic mapping on a graph index

IV. ISOMORPHIC MAPPING ON VAMANA

In this section, we present an isomorphic mapping on
Vamana to refine its SSD layout, thus increasing the data value
of each SSD page (§IV-A), then analyze its effectiveness via
algebraic connectivity [38] (§IV-B), and show its complexity
(§IV-C). In §V-B, we will discuss how to use such a refined
SSD layout to accelerate search via a page-based search.

A. Pack-Merge-based Method

4

5

6

7

8

9

10

11

12

13

14

15

16

Given the page capacity of b, DiskANN writes data blocks
to SSD pages in a round-robin (Figure 3 (a)). In this way, we
can quickly compute a given vertex’s resident page, yielding
an efficient SSD addressing. For example, given a vertex vi,
bvi is the i%b-th data block of the ⌈ i

b ⌉-th SSD page.

We aim to refine the SSD layout by increasing the data value
of each SSD page while keeping the original addressing mode
unchanged. Achieving this is non-trivial. Edge-based graph
partitioning methods [39]–[41] suffer from the redundancy in
vertices, e.g., one vertex would appear multiple times in differ-
ent SSD pages, invalidating original addressing mode. Vertex-
based graph partitioning methods [42]–[44] fail to ensure that
each SSD page contains the same number of vertices, also
undermining the calculation of SSD offsets. Graph reordering
method [45] keeps the addressing mode unchanged, but they
load the entire graph and construct a reverse index in memory
render them inapplicable to large-scale graphs. We compare
our solution to representative reordering methods in §VI.

Different from them, we present a low-memory overhead,
low-time complexity lightweight isomorphic mapping on Va-
mana, while retaining the original rapid SSD addressing mode.
Definition 8 (Isomorphic mapping). Given two SSD layouts
L and L′ for graphs G = (V, E) and G′ = (V ′, E′). We
say f : L.IDs → L′.IDs is an isomorphic mapping on their
logical view (or logical layout), iff f is a bijection satisfying
three conditions: (1) L and L′ contain the same number of
data blocks. (2) ∀bvi, bvj ∈ L, if their identities vi ̸= vj, then
f (vi) ̸= f (vj). (3) ∀bvi, bvj ∈ L, if ∃e(vi, vj) ∈ E, then
i = f (vi) and v′
e(v′
i, v′
Figure 3(c) shows an isomorphic mapped SSD layout of a
graph. Each data block bv of v ∈ V has a mapped bv′ of v′ ∈
V ′ and all the data blocks on SSD pages retain the ascending
order of vertex ID, thus we can efficiently access SSD pages
using the same addressing mode as DiskANN. Since there
exists various isomorphic mapping f , we need to implement
one that can increase the data value of SSD pages. So, we

j) ∈ E′ where v′

j = f (vj).

Algorithm 3: Packing(G, L.IDs, b)
Input: G, L.IDs, b
Output: temporary logical layout ˜L.IDs with finj
// Initialization: line 1

1 Visit ← ∅, ˜L.IDs ← ∅, newID ← 1, finj ← ∅;

// Star packing: lines 2-18

2 for v ∈ V && v /∈ Visit do
3

Visit ← Visit ∪ {v} ;
˜P .IDs ← {v} ; /* a new temporary logical page */
sort N (v) ⊆ V in ascending order of PQ distance;
// update ˜P .IDs with at most b vertices
for vi ∈ N (v) in order do
if | ˜P .IDs| < b then

˜P .IDs ← ˜P .IDs ∪ {vi} ;
Visit ← Visit ∪ {vi} ;

else

end

break ;

end
if | ˜P .IDs| < b then

pad ˜P .IDs with zero ;

end
˜L.IDs ← ˜L.IDs ∪ ˜P .IDs

/* page alignment */

17
18 end

// Injection from L.IDs → ˜L.IDs: lines 19-26

19 for ˜P .IDs ⊂ ˜L.IDs do
for vi ∈ ˜P .IDs do
20
j = newID++;
finj.put(vi, ˜vj) ; /* update with finj(vi) = ˜vj */
update ˜P .IDs with ˜vj;

22

21

23

24

end
newID = (⌈ newID

25
26 end
27 return ˜L.IDs and finj ;

b ⌉ − 1) · b + 1;

present our pack-merge-based method to return a logical layout
L′.IDs with an isomorphic mapping f : L.IDs → L′.IDs. It
consists of two steps: packing (Algorithm 3) and merging
(Algorithm 4). Packing aims to return a temporary logical
layout ˜L.IDs by an injection finj from L.IDs (Figure 3(b))
layout L′.IDs
and merging aims to return a final
by a surjection fsurj from ˜L.IDs. The isomorphic mapping
f = fsurj(finj(·)) is a bijection from L.IDs to L′.IDs.

logical

Packing stage. Given a graph index G = (V, E) and a page
capacity b, Algorithm 3 returns ˜L.IDs with finj by three steps.
Initialization. We initialize a set Visit = ∅ to avoid repeated
visits, a temporary logical layout ˜L.IDs = ∅, a vertex ID
iterator newID from 1, and an empty map finj (line 1).

Star packing. For each unvisited vertex v ∈ V , we add it to a
temporary logical page ˜P .IDs and mark it as a visited vertex
(lines 3-4). Then, we add v’s (b − 1) nearest neibhors (using
PQ distance) from G to the same logic page ˜P .IDs (lines 5-
13). If N (v) < b, we pad ˜P .IDs with zeros (lines 14-16).
We next add ˜P .IDs to ˜L.IDs and repeat above (line 17) until
all vertices have been visited. Since v and its (b − 1) nearest
neighbors belong to the same page, the induced graph of them
is a star-derived graph. In §IV-B, we provide an effectiveness
analysis using the properties of star-derived graph.
Injective mapping. Given a ˜L.IDs, we obtain the injection finj

(cid:1842)(cid:2869)(cid:1842)(cid:2870)(cid:1842)(cid:2871)(cid:1842)(cid:2872)v1v2v3v4v5v6v7v8v9v10v11v12v12v1v2v3v4v5v6v7v8v9v10v11(cid:1842)(cid:3560)(cid:2869)(cid:1842)(cid:3560)(cid:2870)(cid:1842)(cid:3560)(cid:2871)(cid:1842)(cid:3560)(cid:2872)(cid:1842)(cid:3560)(cid:2873)(cid:1842)(cid:2869)(cid:4593)(cid:1842)(cid:2870)(cid:4593)(cid:1842)(cid:2871)(cid:4593)(cid:1842)(cid:2872)(cid:4593)(cid:817)v1(cid:817)v1(cid:817)v2(cid:817)v2(cid:817)v3(cid:817)v3(cid:817)v4(cid:817)v4(cid:817)v5(cid:817)v5(cid:817)v6(cid:817)v6(cid:817)v7(cid:817)v7(cid:817)v8(cid:817)v8(cid:817)v9(cid:817)v9(cid:817)v10(cid:817)v10(cid:817)v11(cid:817)v11(cid:817)v13(cid:817)v13v1(cid:1314)v1(cid:1314)v2(cid:1314)v2(cid:1314)v3(cid:1314)v3(cid:1314)v4(cid:1314)v4(cid:1314)v5(cid:1314)v5(cid:1314)v6(cid:1314)v6(cid:1314)v7(cid:1314)v7(cid:1314)v8(cid:1314)v8(cid:1314)v9(cid:1314)v9(cid:1314)v10(cid:1314)v10(cid:1314)v11(cid:1314)v11(cid:1314)v12(cid:1314)v12(cid:1314)(cid:817)v1(cid:817)v1(cid:817)v2(cid:817)v2(cid:817)v3(cid:817)v3(cid:817)v4(cid:817)v4(cid:817)v5(cid:817)v5(cid:817)v6(cid:817)v6(cid:817)v7(cid:817)v7(cid:817)v8(cid:817)v8(cid:817)v9(cid:817)v9(cid:817)v10(cid:817)v10(cid:817)v11(cid:817)v11(cid:817)v13(cid:817)v13v1(cid:1314)v1(cid:1314)v2(cid:1314)v2(cid:1314)v3(cid:1314)v3(cid:1314)v4(cid:1314)v4(cid:1314)v5(cid:1314)v5(cid:1314)v6(cid:1314)v6(cid:1314)v7(cid:1314)v7(cid:1314)v8(cid:1314)v8(cid:1314)v9(cid:1314)v9(cid:1314)v10(cid:1314)v10(cid:1314)v11(cid:1314)v11(cid:1314)v12(cid:1314)v12(cid:1314)(cid:373)(cid:286)(cid:396)(cid:336)(cid:286)(a)Original layout(c)Isomorphic mapped layout(b)Temporary layout(cid:296)(cid:349)(cid:374)(cid:361)(cid:894)(cid:3)(cid:3)(cid:3)(cid:3)(cid:895)(cid:1089)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)v1(cid:817)v1(cid:817)v1(cid:296)(cid:349)(cid:374)(cid:361)(cid:894)(cid:3)(cid:3)(cid:3)(cid:3)(cid:895)(cid:1089)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)v7(cid:817)v2(cid:817)v2(cid:296)(cid:349)(cid:374)(cid:361)(cid:894)(cid:3)(cid:3)(cid:3)(cid:3)(cid:895)(cid:1089)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)v12(cid:817)v3(cid:817)v3......(cid:296)(cid:400)(cid:437)(cid:396)(cid:361)(cid:894)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)(cid:895)(cid:1089)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)(cid:817)v10(cid:817)v10v10(cid:1314)v10(cid:1314)(cid:296)(cid:400)(cid:437)(cid:396)(cid:361)(cid:894)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)(cid:895)(cid:1089)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)(cid:817)v10v10(cid:1314)(cid:296)(cid:400)(cid:437)(cid:396)(cid:361)(cid:894)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)(cid:895)(cid:1089)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)v11(cid:1314)v11(cid:1314)(cid:817)v11(cid:817)v11(cid:296)(cid:400)(cid:437)(cid:396)(cid:361)(cid:894)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)(cid:895)(cid:1089)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)v11(cid:1314)(cid:817)v11(cid:296)(cid:400)(cid:437)(cid:396)(cid:361)(cid:894)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)(cid:895)(cid:1089)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)v12(cid:1314)v12(cid:1314)(cid:817)v13(cid:817)v13(cid:296)(cid:400)(cid:437)(cid:396)(cid:361)(cid:894)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)(cid:895)(cid:1089)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)v12(cid:1314)(cid:817)v13...(cid:296)(cid:400)(cid:437)(cid:396)(cid:361)(cid:894)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)(cid:895)(cid:1089)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)(cid:817)v10v10(cid:1314)(cid:296)(cid:400)(cid:437)(cid:396)(cid:361)(cid:894)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)(cid:895)(cid:1089)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)v11(cid:1314)(cid:817)v11(cid:296)(cid:400)(cid:437)(cid:396)(cid:361)(cid:894)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)(cid:895)(cid:1089)(cid:3)(cid:3)(cid:3)(cid:3)(cid:3)v12(cid:1314)(cid:817)v13Algorithm 4: Merging( ˜L.IDs, b)
Input: ˜L.IDs, b
Output: final logical layout L′.IDs with fsurj
// Initialization: lines 1-2

1 L′ ← ∅, newID ← 1, fsurj ← ∅;
2 sort temporary logical pages of ˜L.IDs in descending order of
page size, i.e., the number of non-zero logical blocks;

3 for ∀ ˜Pi.IDs ⊂ ˜L.IDs in order do
if | ˜Pi.IDs| == b then
4
i .IDs ← ˜Pi.IDs ;
P ′
˜L.IDs ← ˜L.IDs \ ˜Pi.IDs ;

5

6

/* copy a logical page */

else

// FFD-based merge: lines 8-13
for ∀ ˜Pj.IDs ∈ ˜L.IDs in order do

if | ˜Pi.IDs| + | ˜Pj.IDs| ≤ b then

P ′.IDs ← ˜Pi.IDs + ˜Pj.IDs ; /* merge */
˜L.IDs ← ˜L.IDs \ ˜Pi.IDs ∪ ˜Pj.IDs ;

end

end

end
// Surjection from ˜L.IDs → L′.IDs: lines 15-21
for ∀˜vi ∈ P ′

j) ; /* update with finj(˜vi) = v′

j */

. IDs do
j = newID++;
fsurj.put(˜vi, v′
update P ′.IDs with v′
j;

end
newID = (⌈ newID
L′.IDs ← L′.IDs ∪ P ′.IDs;

b ⌉ − 1) · b + 1;

21
22 end
23 return L′.IDs and fsurj;

7

8

9

10

11

12

13

14

15

16

17

18

19

20

as follows. First, for each vertex vi ∈ ˜P .IDs ⊂ ˜L.IDs, we
update finj with an item f (vi) = ˜vj, where j = newID (lines
20-24). We next update newID (line 25) and repeat above until
all logical pages in ˜L.IDs have been visited.
Example 1. Figure 3(b) shows a temporary logical layout
obtained from Figure3(a). We use the same color to represent
vertices in the same temporary page. Given the page capacity
b = 3, we first assign v1 and its two nearest neighbors v7, v12
to the first page, pad non-full pages with zeros (e.g., the 4th
and 5th pages), and repeat this until all vertices are processed.
Next, we update the vertex IDs and update the injection finj
with finj(v1) = ˜v1, finj(v2) = ˜v5, finj(v3) = ˜v6, etc.

Merging stage. The temporary logical layout has one problem:
some pages are not full (as we pad zeros for nodes having
neighbors < b), and it
invalidates the original addressing
mode. We present a merging stage with the goal of imple-
menting a surjection fsurj : ˜L.IDs → L′.IDs to combine data
blocks from non-full pages to form a full page. Given a ˜L.IDs
and a page capacity b, we do merging (Algorithm 4) as follows.
Initialization. We initialize a final logical layout L′.IDs = ∅,
a vertex ID iterator newID from 1, and a map fsurj (line 1).

FFD-based merge. We first sort temporary logical pages of
˜L.IDs in descending order of page size. The logical page’s
size is the number of non-zero logical blocks in it, denoted by
| ˜P .IDs|. We retain the temporary logical pages with size = b
in L′.IDs (lines: 4-6 and 21) and merge others having size < b
to form new logical pages (lines: 8-13 and 21). Specifically,

we merge two temporary logical pages by bin packing based
on First-Fit-Decreasing (FFD): we iteratively merge the largest
non-full logical page with another smaller logical page to form
a new full logical page until no more merge can be performed.
Surjection mapping. Given a new logical page P ′.IDs that is
retained from ˜P .IDs (line 5) or merged by two logical pages
from ˜L.IDs (line 10), we obtain the surjection fsurj as follows.
For every vertex ˜v from P ′.IDs, we update fsurj with an item
fsurj(˜vi) = v′
j, where j = newID (lines 15-19). Next, we
update newID (line 20) and add P ′.IDs to L′.IDs (line 21).
We repeat above until all logical pages from ˜L.IDs have been
processed and return the final L′.IDs with fsurj (line 23).

Example 2. Figure 3(c) shows the final layout obtained from
Figure 3(b). We retain the first three full pages in the final
logical layout. For the 4th page, it contains only two valid
vertices so that we merge it with the 5th page. Then, we
update the vertex IDs and update the surjection fsurj with
fsurj(˜v10) = v′
12, etc.

12, and fsurj(˜v13) = v′

10, fsurj(˜v11) = v′

Update the SSD layout using finj and fsurj. Given the
original logical layout L.IDs and the output final logical layout
L′.IDs with two mappings finj and fsurj, we update SSD
layout L′ with the real data blocks as follows. Given a logical
page P.IDs ⊂ L.IDs, for each vertex vi ∈ P.IDs with data
block bvi = ⟨⃗xi, N (vi)⟩, we first get vi’s mapping vertex
v′
j)⟩,
j = fsurj(finj(vi)). Then, we form bv′
where ⃗xv′
j represent the same
vertex but with different IDs. For each vertex from N (vi),
we obtain its mapping vertex using fsurj(finj(·)) and add it
to N (v′
j). Finally, we write all reformed data blocks to their
corresponding positions in L′ according to L′.IDs.

= ⃗xvi because both vi and v′

as ⟨⃗xv′

, N (v′

j

j

j

B. Effectiveness Analysis of Refined Layout

Since our intention is to increase the data value of each
SSD page, it is necessary to evaluate the compactness of an
SSD page after isomorphic mapping. We present a new metric
called page compactness based on two widely used metrics:
diameter and algebraic connectivity [38]. Graph diameter is
defined as the longest shortest path between any two vertices
of a graph. The larger the diameter, the less the closeness
between any two vertices. Given an SSD page consisting of
b data blocks, we compute the diameter of the induced graph
G[Vb] of these b vertices by Eq. 10, where shortest path(u, v)
returns the length of the shortest path between u and v.

diam(G[Vb]) = max
u,v∈Vb

shortest path(u, v)

(10)

Algebraic connectivity reflects the global connectivity of a
graph. It is the second-smallest eigenvalue of the Laplacian
matrix [38] of a graph. Given a induced graph G[Vb] of an
SSD page’s b vertices, it’s algebraic connectivity λ2(G[Vb])
is computed by Eq. 11, where Lap(G[Vb]) is the Laplacian
matrix of G[Vb] and ξ is the eigenvector of Lap(G[Vb]).

λ2(G[Vb]) = min

ξ⊥1
ξ̸=0

ξT Lap(G[Vb]) ξ
ξT ξ

(11)

TABLE I: Page compactness of two SSD layouts (original and
isomorphic) for Vamana built on different datasets.

SSD layout ↓

sift100M (R32)

deep100M (R32)

turing100M (R32)

original layout
isomorphic mapped layout
Given a graph G[Vb], its Laplacian matrix is computed as

0
0.547292

0.000004
0.658033

0
0.560141

Lap(i,j)(G[Vb]) =




deg(vi)
−1

0

if i = j
if i ̸= j, vi is adjacent to vj .
otherwise

(12)

Given above two metrics, we define page compactness as

γ(G[Vb]) =

λ2(G[Vb])
diam(G[Vb])

.

(13)

Note that, the smaller (larger) the diameter (algebraic con-
nectivity), the greater the page compactness. Table I provides
the page compactness of the original SSD layout and iso-
morphic mapped SSD layout of the Vamana built on three
datasets using the same R = 32. In DiskANN, R is the largest
out-degree of Vamana used to control the index construction.
Since DiskANN assigns data blocks on SSD in a round-robin,
vertices in an SSD page are almost disconnected in Vamana.
As a result, many SSD pages’ algebraic connectivity is close to
zero, resulting in a high probability that the page compactness
tends to zero. For ours, we assign a vertex’s b − 1 nearest
neighbors to the same page, so that the induced graph of them
is a typical star-derived graph. Given this premise, we prove
that the page compactness of ours must > 0.5 in Theorem 2.

Definition 9. Star-derived Graph. Given a graph G = (V, E)
with one central vertex v ∈ V and other |V | − 1 peripheral
vertices V \v. We call G a star graph if all peripheral vertices
have edges to v but no edges among themselves. Given another
graph G′ = (V, E′) with the same vertices as G and E′ ⊃ E,
G′ is a star-derived graph, i.e., derived from a star graph G.

Theorem 2. Given an SSD page of the isomorphic mapped
layout of Vamana, its page compactness must > 0.5.

Proof. A star graph’s diameter is fixed to 2 and its algebraic
connectivity is constantly at 1. Since a star-derived graph
allows connections among peripheral vertices, it may decrease
the diameter (i.e., a diameter diam(·) ≤ 2) and it would
certainly increase the algebraic connectivity (i.e., λ2(·) > 1).
As a result, the page compactness must > 0.5.

C. Complexity Analysis

Complexity. The complexity arises from both packing and
merging. Assuming that basic arithmetic operations can be
performed in O(1) time, the complexity of packing is O(|V | ·
R · d), where V is the node set of a graph G, R is the largest
out-degree, and d is the dimensions. This is because we need
to calculate the PQ distances between each v ∈ V and its R
neighbors and select the nearest b−1 neighbors to form an SSD
page. The complexity of merging is evidently O(b·N ). So, the
overall time complexity of the mapping is O(|V |·R·d+b·N ).

Fig. 4: The number of I/O requests (SSD I/O and cache I/O)
of beamsearch, cachedBeamsearch, and pagesearch.

V. PAGE-BASED SEARCH

We next discuss how to use the refined SSD layout of
isomorphic mapped Vamana to accelerate the beamsearch.
Straightforwardly, we can cache all the read SSD pages and
check them before requesting SSD pages to avoid redundant
SSD I/Os. It’s worth mentioning that this would not reduce the
total number of I/O requests but only replace a part of SSD I/O
requests with cache I/O requests. The greater the cache hit rate,
the larger the QPS is achieved. We implemented this method
called cachedBeamsearch and compare it with beamsearch.
Figure 4 shows that cachedBeamsearch has the same number
of I/O requests as beamsearch, of which only 10%-20% I/O
requests are hit in cache and most of the cached SSD pages are
unused for the node expansion of beamsearch. Moreover, the
CPU remained largely underutilized during the search process
due to the passive nature of cache requests. In order to take
the advantages of refined SSD layout, we propose an active
filtering-based asynchronous page expansion as a complement
to node expansion, thus forming a new pagesearch.

Figure 5 illustrates the pipelines of our pagesearch and
beamsearch. Pagesearch relies on a meticulously customized
page cache pool called page heap (§V-A). It involves four
basic operators: Cache(), Update(), Check2ret(), and Pop() (the
green components in Figure 5(b)), based on which we design a
page expansion strategy to actively filter more useful vertices
as candidates for node expansion. Besides, we leverage the
CPU’s stall cycle (shown in Figure 5(a)) to perform the
proposed page expansion asynchronously, when the SSD I/O
requests are processing at the same time. In this way, we
improve the CPU utilization so as to improve overall QPS.
Figure 4 shows that pagesearch (right bar) achieves nearly 50%
reduction of SSD I/O requests compared with beamsearch.

A. Page Heap

PageHeap is a page cache pool with four basic operators.
• Cache(). It caches a 4k-aligned page into the memory
pool and register vertices of a page into a circular queue.
• Update(). It first calculates the full vector distance be-
tween each vertex in a circular queue and a query. Then,
it updates a min-heap with these vertices using the above
distances and remove them from circular queue. This
min-heap would be used in the page expansion (see §V-B.
• Check2ret(). It checks whether a given page’s data block
exists in the memory pool. If the data block is found, it
is returned as the output, otherwise it reports none.

• Pop(). It popups the top-1 vertex having the minimum

distance to the given query, from the min-heap.

sift100Mdeep100Mturing100M025050075010001250Number of I/O requestsBeamSearchcachedBeamSearchPageSearchcache hitTABLE II: Statistics of datasets

Dataset
image 1
sift [47]
deep [48]
msong [49]
crawl [50]
turing [51]
glove-100 [52]
gist [47]

Dimension LID [46]

Query

Base (M:106, B:109)

100
128
96
420
300
100
100
960

15.3
16.6
17.6
18.0
27.4
30.5
34.3
35.0

10,000
10,000
10,000
200
10,000
100,000
10,000
1,000

100M
100M
10M∼1B
0.99M
1.99M
100M
1.18M
1M

prepared read requests asynchronously (line 13).
Page Expansion. During asynchronous reading, we Update()
page heap (line 14) and begin page expansion. We iteratively
Pop() one vertex from page heap and invoke NeighborEx-
pansion (Algorithm 2) to update both C and R with more
promising candidates (lines 15-22). We terminate the page
expansion when asynchronous SSD read completes (lines 18-
20), making it synchronized with the asynchronous read.
Node Expansion. When page expansion finishes, we execute
the same node expansion as beamsearch:
taking unvisited
node’s data block bvi from the memory pool of page heap
by invoking check2ret(), for further NeighborExpansion.

Pagesearch repeats the above read preparing, page expan-
sion, and node expansion until no more vertices are visited
(line 30) and returns the top-k results R (line 29).

VI. EVALUATION

We evaluate our DiskANN++, DiskANN, and other com-
petitors on eight large-scale datasets, to answer five questions:
Q1: Does DiskANN++ achieve a better QPS vs. recall@k than
others within a low memory footprint (§VI-B)?
Q2: Does DiskANN++ consistently outperform DiskANN
under various hardware resource constraints (§VI-C)?
Q3: How’s the scalability of DiskANN++ w.r.t. different
datasets (with various hardness) and data scales (§VI-D)?
Q4: What’s the parameter sensitivity of DiskANN++ (§VI-E)?
Q5: What is the contribution of each component individually
or in combination to DiskANN++ (§VI-F).

A. Experiment Settings

Datasets. Table II shows statistics of eight datasets, including
seven public datasets (msong [49], glove-100 [52], crawl
[50], gist [47], sift [47], deep [48], and turing [51]) and one
commercial dataset (image1). The slices of deep ranging from
1M to 1B were employed to evaluate the stability at scales.
Comparing Algorithms. We compared with three SSD-
based solutions: (1) SPANN [20]. (2) BBANN [26]. (3)
DiskANN [27]. For ours, we implemented three versions: (4)
DiskANN++ (w/o compression), (5) DiskANN++ (sq16), and
(6) DiskANN++ (sq8). Here, sq16 and sq8 are compression
ratio that means we compress a vector from fp32 to int16 or
int8. The larger the number, the smaller the compression ratio.
We study the effect of compression on DiskANN++ in §VI-B.
Resource Constraints. We default to employing 10% of the
dataset size as the memory constraint and use 8 threads for
search (one thread per query). This configuration enables full
usage of I/O resources when disk bandwidth and IOPS are

1Commercial image dataset provided by Huawei Technologies Co., Ltd.

Fig. 5: Pipeline of original beamsearch and our pagesearch.

Algorithm 5: Pagesearch(G, ⃗xq, ve, B, Ls, k)
Input: G, ⃗xq, ve, B, Ls, k of top-k
Output: approximate nearest top-k neighbors R to ⃗xq

/* candidate set initialized as {ve} */
/* top-k results initialized as ∅ */
/* PageHeap initialized as ∅ */

1 C ← {ve} ;
2 R ← ∅ ;
3 H ← ∅ ;
4 do
5

F ← top-B unvisited vertices from C for expansion ;
// prepare for SSD I/O requests: lines 6-12
P ← ∅ ; /* page placeholders initialized as ∅ */
for vi ∈ F do

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

27

if H.check2ret(vi) is none then

Pj ← register read for page containing bvi ;
P ← P ∪ Pj ;

end

end
// async SSD I/O requests: line 13
async read all pages in P from SSD ;
H.update() ;
// async page expansion: lines 15-22
while bvi = ⟨⃗xvi , N (vi)⟩ ← H.pop() is not none do

if vi is unvisited then

NeighborExpansion(⃗xq, bvi , C, R, Ls, k) ;
if async read done then

break ;

end

end

end
wait for async read done ;
H.cache(P) ;
// node expansion: lines 25-28
for unvisited vi ∈ F do

bvi = ⟨⃗xvi , N (vi)⟩ ← H.check2ret(vi) ;
NeighborExpansion(⃗xq, bvi , C, R, Ls, k) ;

28

end
return R
29
30 while F ̸= ∅;

B. Pagesearch

Given a graph index G = (V, E) of the vector dataset X ,
a query vector ⃗xq, beam size B, search width Ls, and k of
top-k results, Algorithm 5 shows the entire procedure.

Initialization. We initialize the candidate set C as {ve}, the
top-k results R = ∅, and the page heap H = ∅ (lines 1-3).

Read Preparing. We prepare SSD I/O requests for unvisited
top-B vertices from C, denoted by F. (1) For each vi ∈ F,
we invoke check2ret() to check if vi is cached and register a
page placeholder Pj into P (lines 6-12). (2) We submit the

Cache*Read prep.Node expansion(Alg.1 lines 8-15)Page expansion(Alg5. lines 15-22)N.E.Read prep.Graph read(Alg.1 line 7)timeCPUSSD(a) BeamSearchGraph read(Alg.5 line 13)CPUSSD(b) PagesearchChk2ret*N.E.N.E.Update*N.E.Pop*Pop*Node expansion(Alg.5 lines 25-28)N.E.N.E.Read prep.Read prep.stallSynchronizeFig. 6: QPS and DRAM usage vs. Recall@100 for SPANN, BBANN, DiskANN, and DiskANN++ (with sq16/sq8 compression)

Fig. 7: QPS and DRAM usage vs. Recall@10 for SPANN, BBANN, DiskANN, and DiskANN++ (with sq16/sq8 compression)

Fig. 8: QPS and DRAM usage vs. Recall@1 for SPANN, BBANN, DiskANN, and DiskANN++ (with sq16/sq8 compression)

not restricted. We also conducted experiments under varying
hardware conditions (§VI-C) via Docker, including 1 to 8
threads (i.e., running 1 to 8 queries concurrently), 4k random
I/O bandwidth (100-700MB/s), and 1-25% of the dataset size
as memory constraints.
Evaluation Metrics. We evaluate ANNS’s effectiveness by
recall@k (k = 1,10,100). We evaluate ANNS’s efficiency by
QPS and speedup. QPS exhibits an inverse correlation with
each query’s runtime. Speedup is defined as the ratio of QPS
achieved by DiskANN++ and DiskANN at the same recall@k.
Implementation Setup. For SPANN, BBANN, and DiskANN,
we use public implementations provided in their GitHub repos-
itories [53]–[55]. All algorithms were compiled in C++17,
retaining relevant SIMD and prefetching instructions. The
benchmark scripts were implemented using Bash and Python3.

All experiments were conducted on an Ubuntu 20.04 server
with CPU-10C20T 3.70GHz, SSD-PM981 2TB, DRAM-
32GB 2133Mb/s DDR4 x4.

Parameter Settings. In both DiskANN and DiskANN++, we
utilize identical graph construction parameters: R=32, L=500,
α1=1.0, α2=1.2, and the same PQ construction method: 8-bit
encoding (i.e., 256 pivots per chunk). The DRAM limit of in-
dex construction is set to 64GB, while in the index optimizing
and searching stage, the DRAM limit are 10% of the dataset
size. Under such memory constraints, the construction of the
index for 1 billion-sized slices is conducted in 10 slices and
then merged, following the method outlined in the original
DiskANN paper. In BBANN, we adopt index construction
parameters based on the recommended configurations in its
GitHub repository, with slight modifications: HNSW max

8085909510005001000QPSsift100M8085909510005001000deep100M8085909510005001000turing100M80859095100Recall@100010DRAM (GB)80859095100Recall@10001080859095100Recall@100020SPANNBBANNDiskANNDiskANN++DiskANN++ (sq16)DiskANN++ (sq8)8085909510005001000QPSsift100M8085909510005001000deep100M8085909510001000turing100M80859095100Recall@10010DRAM (GB)80859095100Recall@100580859095100Recall@10020SPANNBBANNDiskANNDiskANN++DiskANN++ (sq16)DiskANN++ (sq8)8085909510001000QPSsift100M8085909510001000deep100M8085909510001000turing100M80859095100Recall@1010DRAM (GB)80859095100Recall@10580859095100Recall@1020SPANNBBANNDiskANNDiskANN++DiskANN++ (sq16)DiskANN++ (sq8)Fig. 9: Effect of memory constraint on QPS and recall@100 of DiskANN and DiskANN++.

layers is set to 32, candidate set list’s size in construction is
set to 512, and block size is 4096KB. In SPANN, we directly
adopt the recommended parameter configuration it provides.

B. Effectiveness and Efficiency Evaluation

We set the same memory constraint (10% of the dataset size)
for DiskANN and DiskANN++. For SPANN and BBANN,
since they require at least 20% of the dataset size in mem-
ory to gain an acceptable recall (>85%) with recommended
parameters, we set the memory constraint for them as 20%.
recall@k. Figure 6-8 (top) demonstrate that
QPS vs.
DiskANN family of algorithms strikes a better balance be-
tween QPS and recall than that of SPANN and BBANN.
DiskANN++ achieves a 50%-100% improvement trend under
the same recall@k. For example, given the same recall@100
as 97% in deep100M, the QPS of DiskANN++ and DiskANN
are 605.3 and 310.2, leading a 95% improvement on QPS.
The same improvement hold for recall@1 and recall@10 as
well. In compression scenarios, DiskANN++ (sq16) shows
the similar trends as that without compression. Besides, the
sq16 compression slightly improves the QPS given the same
recall@k. This is because it reduces the word length of node
data by compressing vector with less precision loss, which
allows for accommodating more nodes in each SSD page.
Consequently,
increases the page expansion width (i.e.,
b) in pagesearch to a certain extent, thus accelerating the
convergence speed of searching. On the other hand, we found
that a noticeable drop occurs at high recall for sq8. This is
because the significant precision loss of original vector when
a strong compression is conducted.
Memory Usage. As shown in Figure 8-6 (bottom), SPANN
and BBANN consume more memory than DiskANN family of
algorithms and the memory usage increases as the precision
increases. The reason is two-folded: (1) SPANN and BBANN
inevitably require reading more disk clusters to achieve higher
precision, resulting in ever-increasing memory consumption,
and (2) SPANN and BBANN maintain SPT or graph index in
memory, which inherently require more memory. In contrast,
the DiskANN family of algorithms maintain a stable memory
footprint that is lower than others because the PQ is used to
obtain low-dimensional quantized vectors resident in memory.

it

C. Effect of Hardware Resources

Effect of I/O limits and # threads. We first study the effect of
hardware resources on DiskANN++ at a high recall@100 of

Fig. 10: Speedup of DiskANN++ of different (a) I/O band-
width, (b) # thread, and (c) dataset scale (deep: 10M∼1B).

97% on deep100M, sift100M, and turing100M, under varying
I/O bandwidth (Figure 10(a)) and # threads (Figure 10(b)).
From Figure 10(a)-(b), we found that DiskANN++ achieves
consistent speedup across varying I/O limits and # threads
(one thread per query) on the same dataset. The differences of
speedup across datasets is attributed to the impact of different
vector dimensions and local intrinsic dimensionality (LID) on
search lengths, as discussed in [56].
Effect of DRAM usage constraints. We study the impact
of memory constraints on the QPS and recall@k. We provide
results with fixed search parameters under memory constraints
at 1%-25% of the dataset size, e.g., the total size of sift100M
is 48GB, deep100M is 36GB, and turing is 37GB. As shown in
Figure 9, DiskANN++ consistently achieves higher recall than
DiskANN under various memory constraints. Additionally, it
demonstrates higher search speed (note the QPS curves). We
analyze that, within the DiskANN framework, the primary
impact of memory constraints lies in the compression ratio
of the PQ in memory, reflecting the loss of precision in the
original vectors. The larger the memory constraint, the less the
PQ precision’s loss. This directly influences the direction se-
lection at each hop during search. Lower PQ quality can result
in longer routing search paths. Worse still, it may lead to the
search being unable to correctly reach the query’s neighbors,
thereby failing to meet the desired recall requirements. From
the results shown in Figure 9, we can conclude that the recall
increases as memory constraint increases.

D. Scalability Evaluation

We evaluated the scalability of DiskANN++ across different
data scales (Figure 10(c)) and types of datasets (Table III)
given recall@100 of 97%. In Figure 10(c), the speedup is sta-
ble as the data scale increases. It is attributed to the adaptability

1510152025DRAM constraint (%)0200400QPSsift100M1510152025DRAM constraint (%)0200400QPSdeep100M1510152025DRAM constraint (%)0200400QPSturing100M050100Recall@100 (%)050100Recall@100 (%)050100Recall@100 (%)QPS (DiskANN)QPS (DiskANN++)Recall@100 (DiskANN)Recall@100 (DiskANN++)100300500700(a) I/O Limits (MB/s)1.01.52.0Speedup2468(b) Thread Number1.01.52.010M50M100M500M1B(c) Data scale12SpeedupDiskANN-baseDiskANN++ (sift100M)DiskANN++ (deep100M)DiskANN++ (turing100M)DiskANN-baseDiskANN++DiskANN++ (sq16)TABLE III: QPS and speedup results of different datasets

Datasets ↓

DiskANN

DiskANN++

DiskANN++ (sq16)

msong
crawl

LID
dataset
15.3
image
sift100M
16.6
deep100M 17.6
18.0
27.4
turing100M 30.5
34.3
glove-100
35.0
gist

QPS
117.07
523.32
605.31
653.35
1209.03
270.65
245.49
347.7
TABLE IV: Effect of Ncluster on speedup under different I/O
bandwidth (varied from 100 MB/s to 700 MB/s).

speedup
1.51x
1.48x
1.95x
1.50x
1.64x
2.44x
2.71x
1.00x

speedup
1.85x
1.69x
1.99x
1.90x
1.79x
2.61x
3.08x
1.36x

QPS
143.57
599.18
617.77
829.48
1318.63
289.77
278.83
474.93

QPS
77.53
354.1
310.24
435.99
738.2
110.70
90.66
348.32

Ncluster ↓

4096
8192
16384
32768
65536

100
1.176x
1.156x
1.180x
1.189x
1.240x

200
1.065x
1.086x
1.113x
1.159x
1.161x

I/O bandwidth (MB/s)
500
400
300
1.127x
1.189x
1.085x
1.175x
1.132x
1.126x
1.219x
1.237x
1.190x
1.418x
1.354x
1.225x
1.153x
1.275x
1.223x

600
1.213x
1.305x
1.334x
1.238x
1.124x

700
1.221x
1.166x
1.147x
1.077x
0.915x

of graph index to various data scales. Some classical studies
[18], [19] have indicated that the time complexity of graph
search is logarithmic which grows slowly with the increase of
data scale. From Table III, ours achieves at least 1.5X speedup
on most of the datasets except gist, due to its high vector
dimensionality of 960, which results in only one vertex per
page, limiting the effectiveness of pagesearch. However, after
augmenting the node capacity to 2 with node compression of
sq16, we achieved 1.36x improvement. We also noticed that
our DiskANN++ is scalable to the hardness of datasets. For
turing100M and glove-100 datasets that have a LID > 30 (with
a modest dimensionality of 100), we achieve at least 2.44x
speedup. This is because when searching on the dataset with
a larger LID, NN refine phase constitutes a larger proportion
and our pagesearch can effectively reduce the I/O requests.

E. Parameter Sensitivity

Effect of Ncluster. The cluster size Ncluster has a significant
impact on query-sensitive entry vertex selection strategy. So,
we study its influence in Figure 11. We found that increasing
Ncluster can effectively reduce routing hops and improve the
QPS, which aligns with the conclusion in Theorem 1 (§III-B).
However, the search performance does not infinitely improve
as Ncluster increases. This is because the time spent in entry
vertex selection cannot be ignored. For example, using an
excessively large Ncluster = 216 would increase the time on
entry vertex selection, leading to a bad search performance.
Therefore, it is necessary to carefully adjust Ncluster to achieve
a favorable trade-off. Furthermore, as search precision (re-
call@100) increases, the QPS improvement brought by query-
sensitive entry vertex selection strategy diminishes. This is
because the routing procedure requires more time in NN refine
step than NN approaching step to find the top-k with a high
recall, thus weakening the improvement brought by query-
sensitive entry vertex selection. We also study the effect of
Ncluster on speedup under different I/O bandwidth (Table IV).
It demonstrates that a smaller Ncluster is preferred to decrease
the overhead of online entry vertex selection, when SSD’s I/O
bandwidth is large (or SSD I/O is fast). Otherwise, a larger

Fig. 11: Effect of the query-sensitive entry vertex (with dif-
ferent Ncluster) under different recall@100 (deep100M).

Fig. 12: Effect of beamsize B on speedup (deep100M).
Ncluster is better. Moreover, we tested the improvement in
QPS under the maximum achievable bandwidth (with Ncluster
= 4096). We found that query-sensitivity entry vertex strategy
only consumes 0.04% of the memory usage and 0.64% of the
runtime, but also offers a 1.12X speedup in QPS.
Effect of beam size B. In Figure 12, speedup decreases as the
beam size increases. This is because increasing the beam size
explicitly expands the width of node expansion, allowing node
expansion to process more data blocks from page heap in each
iteration, resulting in fewer unprocessed data blocks in page
heap can be used for page expansion. However, as mentioned
in the original DiskANN paper, continuously increasing the
beam size is not conducive to load balancing for SSD across
different queries (the original paper suggests B = 2, 4, 8 for
better performance). Therefore, under such parameter settings,
DiskANN++ still exhibits at least 1.5X speedup.

F. Ablation Analysis

Effect of each component. We employ ablation analysis to
assess the contributions of query-sensitive entry vertex (A),
isomorphic mapping (B), and pagesearch (C) individually
within DiskANN++. The experiments compare DiskANN++
and DiskANN across QPS, mean # I/Os, and mean routing
length (i.e., hops), given recall@100=97% (high recall) and
recall@100=85% (low recall), across three common datasets:
sift100M, deep100M, and turing100M. From Table VI, we
conclude that: (1) The query-sensitive entry vertex has a
modest contribution at high recall and a more substantial
impact at low recall. And its contribution is independent of
other components. For enhanced persuasiveness, we record the
hop reduction attributed to the query-sensitive entry vertex for
each query in the official query set of deep [48] (refer to Figure
13). The left subfigure illustrates the relationship between
the hop reduction and the distance between the query and
central vertex (medoid) of graph index, and the right subfigure

20212223242526272829210211212213214215216Ncluster0.990.930.87recall@1000%-1%0%1%1%2%2%2%2%3%3%3%3%3%3%3%3%0%-3%1%2%4%8%6%7%8%9%9%9%10%11%11%11%11%0%-5%1%3%5%11%8%10%11%13%12%13%15%15%16%16%16%20212223242526272829210211212213214215216Ncluster0.990.930.87recall@1000%-1%0%1%1%2%2%2%2%3%2%2%2%2%1%1%-3%0%-4%0%3%3%7%6%7%7%10%9%10%10%9%7%2%-7%0%-5%1%4%6%15%10%12%15%16%15%16%17%15%12%7%-7%-0.050.000.050.100.150.200.250.30(a) Hop Count Reduction Radio(b) QPS Growth Radio124816Beam size1.41.61.8Speedupsift100M124816Beam size1.62.02.4deep100M124816Beam size1.41.82.2turing100MDiskANN++DiskANN++ (sq16)TABLE V: Overhead and speedup (at recall@100=97%) of randomOrder, parallelGorder, pack-merge (ours) using pagesearch.

DRAM usage (GB)

graph index
Vamana (sift100M R32)
Vamana (deep100M R32)
Vamana (turing100M R32)

randomOrder
2.2
1.9
2.0

parallelGorder
75.1 (MLE)
72.5 (MLE)
73.4 (MLE)

pack-merge
6.3
5.1
6.1

randomOrder
449.5
381.2
366.7

Runtime (sec)

parallelGorder
2739.1
2651.4
2644.8

Speedup with pagesearch

pack-merge
222.3
123.1
195.2

randomOrder
1.02x
1.08x
1.08x

parallelGorder
1.84x
2.15x
2.08x

pack-merge
1.69x
2.02x
1.88x

TABLE VI: Ablation analysis on query-sensitive entry vertex
(A), isomorphic mapping (B), and pagesearch (C).

Dataset
sift100M

components
-
A
B
C
AB
AC
BC
ABC

Dataset
deep100M

components
-
A
B
C
AB
AC
BC
ABC

Dataset
turing100M

components
-
A
B
C
AB
AC
BC
ABC

Recall@100=85%
DiskANN++

Recall@100=97%
DiskANN++

QPS
946.42 (1.00x)
1033.64 (1.09x)
959.8 (1.01x)
1065.09 (1.13x)
1022.24 (1.08x)
1152.38 (1.22x)
1281.32 (1.35x)
1412.35 (1.49x)

mean I/Os mean hops

181.54
164.57
181.54
179.24
164.57
163.79
148.32
133.41

24.66
22.51
24.66
24.38
22.51
22.41
20.58
18.72

QPS
385.88 (1.00x)
401.14 (1.04x)
387.17 (1.00x)
440.34 (1.14x)
397.41 (1.03x)
447.22 (1.16x)
660.6 (1.71x)
691.88 (1.79x)

mean I/Os mean hops

447.49
431.58
447.49
438.87
431.58
425.35
291.85
278.65

57.61
55.62
57.61
56.6
55.62
54.92
38.25
36.62

Recall@100=85%
DiskANN++

Recall@100=97%
DiskANN++

QPS
945.69 (1.00x)
1104.46 (1.17x)
928.85 (0.98x)
1043.07 (1.10x)
1096.92 (1.16x)
1156.4 (1.22x)
1296.92 (1.37x)
1523.41 (1.61x)

mean I/Os mean hops

184.15
153.7
184.15
177.15
153.7
153.66
142.83
118.89

25.06
21.25
25.06
24.19
21.25
21.23
19.92
16.99

QPS
308.78 (1.00x)
325.66 (1.05x)
305.81 (0.99x)
332.42 (1.08x)
324.25 (1.05x)
340.15 (1.10x)
588.93 (1.91x)
625.23 (2.02x)

mean I/Os mean hops

557.93
529.26
557.93
549.1
529.26
528.33
316.78
291.78

71.42
67.91
71.42
70.37
67.91
67.74
41.42
38.28

Recall@100=85%
DiskANN++

Recall@100=97%
DiskANN++

QPS
866.13 (1.00x)
990.49 (1.14x)
855.86 (0.99x)
988.52 (1.14x)
958.94 (1.11x)
1066.85 (1.23x)
1228.52 (1.42x)
1363.68 (1.57x)

mean I/Os mean hops

202.21
174.84
202.21
189.56
174.84
173.12
152.59
131.89

27.22
23.79
27.22
25.57
23.79
23.58
21.07
18.54

QPS
136.12 (1.00x)
140.21 (1.03x)
136.33 (1.00x)
153.48 (1.13x)
139.33 (1.02x)
155.43 (1.14x)
259.17 (1.90x)
265.95 (1.95x)

mean I/Os mean hops
1244.34
1215.26
1244.34
1203.58
1215.26
1187.15
714.63
694.09

157.5
153.81
157.5
152.33
153.81
150.33
91.37
88.84

provides a statistical overview of the query count for different
hop reduction. It is evident that queries positioned farther from
the medoid experience more substantial benefits. Practically,
there is a higher probability of a random high-dimensional
point falling at a greater distance compared to falling near a
fixed point. Hence, on average, queries exhibit a pronounced
reduction in hop count. (2) Using isomorphic mapping alone
does not accelerate beamsearch, because beamsearch doesn’t
have a mechanism to consider the highly-related vertices in
increase in
the same page. Remark: despite the potential
CPU cache prefetching effects (refer to [45]), in scenarios
related to disks in this context, SRAM prefetch optimization is
diluted to insignificance by a larger and slower proportion of
I/O operations. (3) Using pagesearch alone shows a limited
improvement. This is because the original SSD layout
is
established by a round-robin assignment, resulting a low
locality of vertices in the same page. So, pagesearch cannot
benefit more from original SSD layout. (4) The combination
of isomorphic mapping and pagesearch represents the primary
contribution, it brings more improvement on QPS at higher
recall. This is because pagesearch can effectively unleash the
potential of the refined SSD layout via isomorphic mapping.

Effect of different graph reordering methods. The key of
our isomorphic mapping is the pack-merge method (§IV-A).
We replace it by different graph reordering methods that can

Fig. 13: Relationship between the hop reduction and the
distance between the query and graph medoid (left). Query
count for different hop reduction (right).

also be used to refine the SSD layout, e.g., randomOrder and
Gorder [45], and evaluate their overhead (memory usage and
runtime) and speedup, using the same pagesearch. Consid-
ering the immense time complexity of Gorder, rendering it
impractical to complete in a foreseeable time, we adopted the
improved parallelGorder method used in OOD-DiskANN [31].
This method sacrifices some reorder effect to enhance runtime
speed. All requirements are conducted with 8 threads.

From Table V, we found that our pack-merge method is the
most efficient one that consumes modest memory and offers a
comparable QPS improvement as parallelGorder+pagesearch.
In contrast, since parallelGorder requires > 70GB memory to
perform, which largely exceeds the memory constraint (MLE
stands for memory limit exceed), its practical deployability is
significantly limited. Therefore, due to the lightweight nature
of the pack-merge-based method, we can easily optimize the
existing Vamana index on any device where DiskANN is
deployed, whether it is the machine used for index construction
or the one used for searching. This optimization can lead to a
substantial improvement in search performance.

VII. RELATED WORK

We review the relevant

technologies,

including ANNS,

graph-based ANNS, and DiskANN and its variants.
Approximate nearest neighbor search (ANNS). The re-
searches of ANNS are generally categorized as three types:
quantization-based [57]–[61], hash-based [12], [13], [62]–[65],
and graph-based [18], [19], [66]–[68] ANNS. Among them,
graph-based methods achieve a favourable tradeoff between
accuracy and efficiency [11], [21], [23], [24]. However, ex-
isting research has primarily focused on optimizing search
accuracy and efficiency but ignore the significant memory
overhead for maintaining the large graph index. This motivates
the following disk-resident graph-based ANNS.

Disk-resident graph-based ANNS. Most of the solutions
are based on hybrid indexing schemes that utilize both disk
and memory. GRIP [69] reduces the memory consumption
of a graph index by compressing high-dimensional vectors
to lower-dimensional ones. HM-ANN [70] addresses memory
challenges via heterogeneous storage solutions. SPANN [20]
is a partition tree-based method that maintains a small SPT in
memory but the full vectors in disk. BBANN [26] combines

0123456789101112131415Hop reduction1.01.5Distance frommedoid to query0123456789101112131415Hop reduction010002000Query counta memory resident invert index and on-disk graph index to
optimize search tasks. The search accuracy of above methods
is affected by the compressed vectors, low-quality invert index,
and SPT. So, researchers resort to DiskANN family of methods
to reduce memory overhead while ensuring a high accuracy.
DiskANN family of methods. DiskANN [27] introduces
PQ to assist graph-based ANNS and memory usage. It has
been widely deployed in the industry such as Bing search of
Microsoft [29] and many follow-up works present variants of
DiskANN, e.g., Filter-DiskANN for filtered search [30], OOD-
DiskANN for cross-modal search [31], and Fresh-DiskANN
for streaming search [32]. Although DiskANN and its variants
achieve a good performance on both memory overhead and
search accuracy, they all ignore the fact that frequent SSD I/O
would affect the overall QPS. This motivates us to address the
I/O issue of DiskANN while retaining its strengths.

VIII. CONCLUSION

This paper proposes DiskANN++ that consists of three
optimizations for DiskANN. (1) It expedites the convergence
of graph search to the query neighborhood by employing
query-sensitive entry vertex. (2) It applies isomorphic mapping
on Vamana to refine its SSD layout and enhance each SSD
page’s data value. (3) It replaces original beamsearch by a
new pagesearch based on the refined SSD layout with an
asynchronous page expansion. Experimental results shows that
DiskANN++ achieves a notable 1.5X to 2.2X improvement on
QPS compared to DiskANN across various hardware config-
urations and datasets, given the same accuracy constraint.

ACKNOWLEDGMENT

This work was supported by the National NSF of China
(62072149), the Primary R&D Plan of Zhejiang (2023C03198
and 2021C03156), and Fundamental Research Funds for the
Provincial Universities of Zhejiang (GK219909299001-006).

REFERENCES

[1] S. Arya and D. M. Mount, “Approximate nearest neighbor queries in

fixed dimensions.” in SODA, vol. 93, 1993, pp. 271–280.

[2] P. Indyk and R. Motwani, “Approximate nearest neighbors: towards
removing theƒƒ curse of dimensionality,” in Proceedings of the thirtieth
annual ACM symposium on Theory of computing, 1998, pp. 604–613.
[3] Q. Wang, H. Yin, T. Chen, J. Yu, A. Zhou, and X. Zhang, “Fast-
adapting and privacy-preserving federated recommender system,” The
VLDB Journal, vol. 31, no. 5, pp. 877–896, 2022.

[4] B. Sarwar, G. Karypis, J. Konstan, and J. Riedl, “Item-based collabo-
rative filtering recommendation algorithms,” in Proceedings of the 10th
international conference on World Wide Web, 2001, pp. 285–295.
[5] X. Xu, J. Liu, Y. Wang, and X. Ke, “Academic expert finding via (k, p)-
core based embedding over heterogeneous graphs,” in 2022 IEEE 38th
International Conference on Data Engineering (ICDE).
IEEE, 2022,
pp. 338–351.

[6] M. Flickner, H. Sawhney, W. Niblack, J. Ashley, Q. Huang, B. Dom,
M. Gorkani, J. Hafner, D. Lee, D. Petkovic et al., “Query by image and
video content: The qbic system,” computer, vol. 28, no. 9, pp. 23–32,
1995.

[7] D. A. Adeniyi, Z. Wei, and Y. Yongquan, “Automated web usage data
mining and recommendation system using k-nearest neighbor (knn)
classification method,” Applied Computing and Informatics, vol. 12,
no. 1, pp. 90–108, 2016.

[8] V. Bijalwan, V. Kumar, P. Kumari, and J. Pascual, “Knn based machine
learning approach for text and document mining,” International Journal
of Database Theory and Application, vol. 7, no. 1, pp. 61–70, 2014.

[9] T. Cover and P. Hart, “Nearest neighbor pattern classification,” IEEE
transactions on information theory, vol. 13, no. 1, pp. 21–27, 1967.

[10] C. J. Zhu, T. Zhu, H. Li, J. Bi, and M. Song, “Accelerating large-
scale molecular similarity search through exploiting high performance
computing,” in 2019 IEEE International Conference on Bioinformatics
and Biomedicine (BIBM).

IEEE, 2019, pp. 330–333.

[11] M. Wang, X. Xu, Q. Yue, and Y. Wang, “A comprehensive survey and
experimental comparison of graph-based approximate nearest neighbor
search,” Proceedings of the VLDB Endowment, vol. 14, pp. 1964–1978,
07 2021.

[12] A. Gionis, P. Indyk, R. Motwani et al., “Similarity search in high

dimensions via hashing,” in Vldb, vol. 99, no. 6, 1999, pp. 518–529.

[13] L. Gong, H. Wang, M. Ogihara, and J. Xu, “idec: indexable distance
estimating codes for approximate nearest neighbor search,” Proceedings
of the VLDB Endowment, vol. 13, no. 9, 2020.

[14] A. Arora, S. Sinha, P. Kumar, and A. Bhattacharya, “Hd-index: Pushing
the scalability-accuracy boundary for approximate knn search in high-
dimensional spaces,” Proceedings of the VLDB Endowment, vol. 11,
no. 8, 2018.

[15] C. Silpa-Anan and R. Hartley, “Optimised kd-trees for fast

image
descriptor matching,” in 2008 IEEE Conference on Computer Vision
and Pattern Recognition.

IEEE, 2008, pp. 1–8.

[16] H. Jegou, M. Douze, and C. Schmid, “Product quantization for nearest
neighbor search,” IEEE transactions on pattern analysis and machine
intelligence, vol. 33, no. 1, pp. 117–128, 2010.

[17] C.-Y. Chiu, A. Prayoonwong, and Y.-C. Liao, “Learning to index for
nearest neighbor search,” IEEE transactions on pattern analysis and
machine intelligence, vol. 42, no. 8, pp. 1942–1956, 2019.

[18] C. Fu, C. Xiang, C. Wang, and D. Cai, “Fast approximate nearest
neighbor search with the navigating spreading-out graph,” arXiv preprint
arXiv:1707.00143, 2017.

[19] Y. Malkov and D. Yashunin, “Efficient and robust approximate nearest
neighbor search using hierarchical navigable small world graphs,” IEEE
Transactions on Pattern Analysis and Machine Intelligence, vol. PP,
no. 4, pp. 824–836, 03 2016.

[20] Q. Chen, B. Zhao, H. Wang, M. Li, C. Liu, Z. Li, M. Yang, and J. Wang,
“Spann: Highly-efficient billion-scale approximate nearest neighborhood
search,” Advances in Neural Information Processing Systems, vol. 34,
pp. 5199–5212, 2021.

[21] M. Aum¨uller, E. Bernhardsson, and A. Faithfull, “Ann-benchmarks:
A benchmarking tool for approximate nearest neighbor algorithms,”
Information Systems, vol. 87, p. 101374, 2020.

[22] L. C. Shimomura, R. S. Oyamada, M. R. Vieira, and D. S. Kaster, “A
survey on graph-based methods for similarity searches in metric spaces,”
Information Systems, vol. 95, p. 101507, 2021.

[23] K. Aoyama, A. Ogawa, T. Hattori, T. Hori, and A. Nakamura, “Graph
index based query-by-example search on a large speech data set,” in
2013 IEEE International Conference on Acoustics, Speech and Signal
Processing.

IEEE, 2013, pp. 8520–8524.

[24] H. Hacid and T. Yoshida, “Neighborhood graphs for indexing and
retrieving multi-dimensional data,” Journal of Intelligent Information
Systems, vol. 34, pp. 93–111, 2010.

[25] R. Paredes and E. Ch´avez, “Using the k-nearest neighbor graph for prox-
imity searching in metric spaces,” in String Processing and Information
Retrieval: 12th International Conference, SPIRE 2005, Buenos Aires,
Argentina, November 2-4, 2005. Proceedings 12. Springer, 2005, pp.
127–138.

[26] H. Simhadri, G. Williams, M. Aum¨uller, M. Douze, A. Babenko,
D. Baranchuk, Q. Chen, L. Hosseini, R. Krishnaswamy, G. Srinivasa,
S. Subramanya, and J. Wang, “Results of the neurips’21 challenge on
billion-scale approximate nearest neighbor search,” 05 2022.

[27] S. Jayaram Subramanya, F. Devvrit, H. V. Simhadri, R. Krishnawamy,
and R. Kadekodi, “Diskann: Fast accurate billion-point nearest neighbor
search on a single node,” Advances in Neural Information Processing
Systems, vol. 32, 2019.

[28] M. Dobson, Z. Shen, G. E. Blelloch, L. Dhulipala, Y. Gu, H. V.
Simhadri, and Y. Sun, “Scaling graph-based anns algorithms to billion-
size datasets: A comparative analysis,” arXiv preprint arXiv:2305.04359,
2023.

[29] J. Zhang, Z. Liu, W. Han, S. Xiao, R. Zheng, Y. Shao, H. Sun, H. Zhu,
P. Srinivasan, W. Deng, Q. Zhang, and X. Xie, “Uni-retriever: Towards
learning the unified embedding based retriever in bing sponsored search,”
in KDD, 2022, pp. 4493–4501.

[58] T. Ge, K. He, Q. Ke, and J. Sun, “Optimized product quantization
for approximate nearest neighbor search,” in Proceedings of the IEEE
Conference on Computer Vision and Pattern Recognition, 2013, pp.
2946–2953.

[59] Y. Kalantidis and Y. Avrithis, “Locally optimized product quantization
for approximate nearest neighbor search,” In CVPR, pp. 2321–2328, 01
2014.

[60] J. Wang and T. Zhang, “Composite quantization,” IEEE Transactions on

Pattern Analysis and Machine Intelligence, vol. PP, 12 2017.

[61] Z. Pan, L. Wang, Y. Wang, and Y. Liu, “Product quantization with dual
codebooks for approximate nearest neighbor search,” Neurocomputing,
vol. 401, 03 2020.

[62] Y. Weiss, A. Torralba, and R. Fergus, “Spectral hashing,” in Advances
in Neural Information Processing Systems, D. Koller, D. Schuurmans,
Y. Bengio, and L. Bottou, Eds., vol. 21. Curran Associates, Inc., 2008.
[63] H. Xu, J. Wang, Z. Li, G. Zeng, S. Li, and N. Yu, “Complementary
hashing for approximate nearest neighbor search,” 11 2011, pp. 1631–
1638.

[64] Q. Huang, J. Feng, Q. Fang, W. Ng, and W. Wang, “Query-aware
locality-sensitive hashing scheme for lp norm,” The VLDB Journal,
vol. 26, no. 5, pp. 683–708, 2017.

[65] S. Karaman, X. Lin, X. Hu, and S.-F. Chang, “Unsupervised rank-
preserving hashing for large-scale image retrieval,” in Proceedings of
the 2019 on International Conference on Multimedia Retrieval, 2019,
pp. 192–196.

[66] K. Hajebi, Y. Abbasi-Yadkori, H. Shahbazi, and H. Zhang, “Fast
approximate nearest-neighbor search with k-nearest neighbor graph,” in
Twenty-Second International Joint Conference on Artificial Intelligence,
2011.

[67] Y. Malkov, A. Ponomarenko, A. Logvinov, and V. Krylov, “Approximate
nearest neighbor algorithm based on navigable small world graphs,”
Information Systems, vol. 45, pp. 61–68, 2014.

[68] C. Fu and D. Cai, “Efanna : An extremely fast approximate nearest

neighbor search algorithm based on knn graph,” 09 2016.

[69] M. Zhang and Y. He, “Grip: Multi-store capacity-optimized high-
performance nearest neighbor search for vector search engine,” in
Proceedings of the 28th ACM International Conference on Information
and Knowledge Management, 11 2019, pp. 1673–1682.

[70] J. Ren, M. Zhang, and D. Li, “Hm-ann: Efficient billion-point nearest
neighbor search on heterogeneous memory,” Advances in Neural Infor-
mation Processing Systems, vol. 33, pp. 10 672–10 684, 2020.

[30] S. Gollapudi, N. Karia, V. Sivashankar, R. Krishnaswamy, N. Begwani,
S. Raz, Y. Lin, Y. Zhang, N. Mahapatro, P. Srinivasan, A. Singh, and
H. V. Simhadri, “Filtered-diskann: Graph algorithms for approximate
nearest neighbor search with filters,” in Proceedings of the ACM Web
Conference 2023, 2023, p. 3406–3416.

[31] S. Jaiswal, R. Krishnaswamy, A. Garg, H. V. Simhadri, and S. Agrawal,
“Ood-diskann: Efficient and scalable graph anns for out-of-distribution
queries,” arXiv preprint arXiv:2211.12850, 2022.

[32] A. Singh, S. J. Subramanya, R. Krishnaswamy, and H. V. Simhadri,
“Freshdiskann: A fast and accurate graph-based ann index for streaming
similarity search,” arXiv preprint arXiv:2105.09613, 2021.

[33] X. Xu, M. Wang, Y. Wang, and D. Ma, “Two-stage routing with
optimized guided search and greedy algorithm on proximity graph,”
Knowledge-Based Systems, vol. 229, p. 107305, 07 2021.

[34] D. Dearholt, N. Gonzales, and G. Kurup, “Monotonic search networks

for computer vision databases,” vol. 2, 02 1988, pp. 548–553.

[35] D. Zhu and M. Zhang, “Understanding and generalizing monotonic prox-
imity graphs for approximate nearest neighbor search,” arXiv preprint
arXiv:2107.13052, 2021.

[36] M. Babenko and A. Gusakov, “New exact and approximation algorithms
for the star packing problem in undirected graphs,” Symposium on
Theoretical Aspects of Computer Science (STACS2011), vol. 9, 03 2011.
[37] K. Peng and Q. Huang, “Clustering approach based on mini batch
kmeans for intrusion detection system over big data,” IEEE Access,
vol. PP, pp. 1–1, 02 2018.
“Algebraic

graphs,” Czechoslovak
Mathematical Journal, vol. 23, pp. 298–305, 1973. [Online]. Available:
https://api.semanticscholar.org/CorpusID:117770486

[38] M. Fiedler,

connectivity

of

[39] C. Zhang, F. Wei, Q. Liu, Z. Tang, and Z. Li, “Graph edge partitioning

via neighborhood heuristic,” 08 2017, pp. 605–614.

[40] C. Xie, L. Yan, W.-J. Li, and Z. Zhang, “Distributed power-law graph
computing: Theoretical and empirical analysis,” Advances in Neural
Information Processing Systems, vol. 2, pp. 1673–1681, 01 2014.
[41] F. Petroni, L. Querzoni, K. Daudjee, S. Kamali, and G. Iacoboni, “Hdrf:
Stream-based partitioning for power-law graphs,” 10 2015, pp. 243–252.
[42] G. Karypis, V. Kumar, and S. Comput, “A fast and high quality
multilevel scheme for partitioning irregular graphs,” SIAM Journal on
Scientific Computing, vol. 20, 02 1970.

[43] I. Stanton and G. Kliot, “Streaming graph partitioning for large dis-

tributed graphs,” 09 2012.

[44] C. Tsourakakis, C. Gkantsidis, B. Radunovic, and M. Vojnovic, “Fennel:
Streaming graph partitioning for massive scale graphs,” 02 2014, pp.
333–342.

[45] H. Wei, J. Yu, C. Lu, and X. Lin, “Speedup graph processing by graph

ordering,” 06 2016, pp. 1813–1828.

[46] E. Facco, M. d’Errico, A. Rodriguez, and A. Laio, “Estimating the
intrinsic dimension of datasets by a minimal neighborhood information,”
Scientific Reports, vol. 7, 09 2017.

[47] Anon.

(2010) Datasets for approximate nearest neighbor search.

[Online]. Available: http://corpus-texmex.irisa.fr/

[48] A. Yandex and V. Lempitsky, “Efficient indexing of billion-scale datasets

of deep descriptors,” 06 2016, pp. 2055–2063.

[49] Song. (2011) Million song dataset benchmarks. [Online]. Available:

http://www.ifs.tuwien.ac.at/mir/msd/

[50] Crawl. (2023) Common crawl. [Online]. Available: http://commoncrawl.

org/

[51] H. Zhang, X. Song, C. Xiong, C. Rosset, P. Bennett, N. Craswell, and
S. Tiwary, “Generic intent representation in web search,” 07 2019, pp.
65–74.

[52] P.

Jeffrey, S. Richard, and D. M. Christopher.

Global vectors for word representation.
//nlp.stanford.edu/projects/glove/

(2015) Glove:
[Online]. Available: http:

[53] microsoft, “Sptag: A library for fast approximate nearest neighbor

search,” https://github.com/microsoft/SPTAG, 2023.

[54] Zilliztech, “Bbann: Block-based approximate nearest neighbor,” https:

//github.com/zilliztech/BBAnn, 2023.

[55] microsoft, “Diskann,” https://github.com/microsoft/DiskANN, 2023.
[56] W. Li, Y. Zhang, Y. Sun, W. Wang, M. Li, W. Zhang, and
X. Lin, “Approximate nearest neighbor search on high dimensional
data—experiments, analyses, and improvement,” IEEE Transactions on
Knowledge and Data Engineering, vol. 32, no. 8, pp. 1475–1488, 2019.
[57] H. J´egou, M. Douze, and C. Schmid, “Product quantization for nearest
neighbor search,” IEEE transactions on pattern analysis and machine
intelligence, vol. 33, pp. 117–28, 01 2011.

