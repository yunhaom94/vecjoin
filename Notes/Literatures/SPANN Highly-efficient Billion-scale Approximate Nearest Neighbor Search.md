1
2
0
2

v
o
N
5

]

B
D
.
s
c
[

1
v
6
6
5
8
0
.
1
1
1
2
:
v
i
X
r
a

SPANN: Highly-efﬁcient Billion-scale Approximate
Nearest Neighbor Search

Qi Chen1, ∗ Bing Zhao1, 2, † Haidong Wang1 Mingqin Li1 Chuanjie Liu1, 3, †

Zengzhong Li1 Mao Yang1
1Microsoft

2Peking University

Jingdong Wang1, 4, ∗, †
4Baidu

3Tencent

1{cheqi, haidwa, mingqli, jasol, maoyang}@microsoft.com

2its.bingzhao@pku.edu.cn

3liu.chuanjie@outlook.com

4wangjingdong@outlook.com

Abstract

The in-memory algorithms for approximate nearest neighbor search (ANNS) have
achieved great success for fast high-recall search, but are extremely expensive
when handling very large scale database. Thus, there is an increasing request for
the hybrid ANNS solutions with small memory and inexpensive solid-state drive
(SSD). In this paper, we present a simple but efﬁcient memory-disk hybrid indexing
and search system, named SPANN, that follows the inverted index methodology. It
stores the centroid points of the posting lists in the memory and the large posting
lists in the disk. We guarantee both disk-access efﬁciency (low latency) and
high recall by effectively reducing the disk-access number and retrieving high-
quality posting lists. In the index-building stage, we adopt a hierarchical balanced
clustering algorithm to balance the length of posting lists and augment the posting
list by adding the points in the closure of the corresponding clusters. In the search
stage, we use a query-aware scheme to dynamically prune the access of unnecessary
posting lists. Experiment results demonstrate that SPANN is 2× faster than the
state-of-the-art ANNS solution DiskANN to reach the same recall quality 90%
with same memory cost in three billion-scale datasets. It can reach 90% recall@1
and recall@10 in just around one millisecond with only 32GB memory cost. Code
is available at: https://github.com/microsoft/SPTAG.

1

Introduction

Vector nearest neighbor search has played an important role in information retrieval area, such
as multimedia search and web search, which provides relevant results by searching vectors with
minimum distance to the query vector. Exact solutions for K-nearest neighbor search [49, 40] are not
applicable in big data scenario due to substantial computation cost and high query latency. Therefore,
researchers have proposed many kinds of approximate nearest neighbor search (ANNS) algorithms in
the literature [11, 18, 38, 10, 14, 31, 34, 13, 29, 21, 16, 26, 42, 43, 33, 44, 37, 32, 19, 27, 9, 12, 39,
50, 20, 36]. However, most of the algorithms mainly focus on how to do low latency and high recall
search all in memory with ofﬂine pre-built indexes. When targeting to the super large scale vector
search scenarios, such as web search, the memory cost will become extremely expensive. There is an
increasing request for the hybrid ANNS solutions that use small memory and inexpensive disk to
serve the large scale datasets.

There are only a few approaches working on the hybrid ANNS solutions, including DiskANN [39]
and HM-ANN [36]. Both of them are graph based solutions. DiskANN uses Product Quantization

∗Corresponding author.
†Work done while at Microsoft.

35th Conference on Neural Information Processing Systems (NeurIPS 2021).

(PQ) [25] to compress the vectors stored in the memory while putting the navigating spread-out
graph along with the full-precision vectors on the disk. When a query comes, it traverses the graph
according to the distance of quantized vectors and then reranks the candidates according to distance
of the full-precision vectors. HM-ANN leverages the heterogeneous memory by placing pivot points
in the fast memory and navigable small world graph in the slow memory without data compression.
However, it consumes more than 1.5 times larger fast memory than DiskANN. Moreover, the slow
memory is still much expensive than disk. Therefore, due to the cheap serving cost, high recall and
low latency advantages of DiskANN, it has become the start-of-the-art for indexing billion-scale
datasets.

In this paper, we argue that the simple inverted index approach can also achieve state-of-the-art
performance for large scale datasets in terms of recall, latency and memory cost. We propose SPANN,
a simple but surprising efﬁcient memory-disk hybrid vector indexing and search system, that follows
the inverted index methodology. SPANN only stores the centroid points of the posting lists in the
memory while putting the large posting lists in the disk. We guarantee both low latency and high
recall by greatly reducing the number of disk accesses and improving the quality of posting lists.
In the index-building stage, we use a hierarchical balanced clustering method to balance the length
of posting lists and expand the posting list by adding the points in the closure of the corresponding
clusters. In the search stage, we use a query-aware scheme to dynamically prune the access of
unnecessary posting lists. Experiment results demonstrate that SPANN is more than two times faster
than the state-of-the-art disk-based ANNS algorithm DiskANN to reach the same recall quality 90%
with same memory cost in three billion-scale datasets. It can reach 90% recall@1 and recall@10
in just around one millisecond with only 10% of original memory cost. SPANN has already been
deployed into Microsoft Bing to support hundreds of billions scale vector search.

2 Background and Related Work

Given a set of data vectors X ∈ Rn×m (the data set contains n vectors with m-dimensional features)
and a query vector q ∈ Rm, the goal of vector search is to ﬁnd a vector p∗ from X, called nearest
neighbor, such that p∗ = arg minp∈X Dist(p, q). Similarly, we can deﬁne K-nearest neighbors. Due
to the substantial computation cost and high query latency of the exhaustive search, ANNS algorithms
are designed to speedup the search for the approximiate K-nearest neighbors in a large dataset in an
acceptable amount of time. Most of the ANNS algorithms in the literature mainly focus on the fast
high-recall search in the memory, including hash based methods [14, 24, 47, 48, 45, 46, 51], tree based
methods [11, 31, 44, 33], graph based methods [21, 16, 42, 32], and hybrid methods [43, 12, 23, 22].
However, with the explosive growth of the vector scale, the memory has become the bottleneck to
support large scale vector search. There are only a few approaches working on the ANNS solutions
for billon-scale datasets to minimize the memory cost. They can be divided into two categories:
inverted index based and graph based methods.

The inverted index based methods, such as IVFADC [26], FAISS [27] and IVFOADC+G+P [9],
split the vector space into K Voronoi regions by KMeans clustering and only do search in a few
regions that are closed to the query. To reduce the memory cost, they use vector quantization, e.g.
Product Quantization (PQ) [25], to compress the vectors and store them in the memory. The inverted
multi-index (IMI) [7] also uses PQ to compress vectors. It splits the feature space into multiple
orthogonal subspaces and constructs a separate codebook for each subspace. The full feature space
is produced as a Cartesian product of the corresponding subspaces. Multi-LOPQ[28] uses locally
optimized PQ codebook to encode the displacements in the IMI structure. GNO-IMI [8] optimizes
the IMI by using non-orthogonal codebooks to produce the centroids. Although they can cut down
the memory usage to less than 64GB for one billion 128 dimensional vectors, the recall@1 is very
low (only around 60%) due to lossy data compression. Although they can achieve better recall by
returning 10 to 100 times more candidates for further reranking, it is often not acceptable in many
scenarios.

The graph based methods include DiskANN [39] and HM-ANN [36]. Both of them adopt the hybrid
solution. DiskANN also stores the PQ compressed vectors in the memory while storing the navigating
spread-out graph along with the full-precision vectors on the disk. When a query comes, it traverses
the graph using best-ﬁrst manner according to the distance of quantized vectors and then reranks
the candidates according to distance of the full-precision vectors. Similarly, it uses the lossy data
compression which will inﬂuence the recall quality even though full-precision vector reranking can

2

Figure 1: Example of boundary vector miss-
ing due to partial search. If we search yel-
low point, we will search green posting list
ﬁrst since the centroid of green posting list
is closer to the yellow point although there
are some boundary points (colored red) in the
blue posting list that are much closer.

Figure 2: Different queries require different num-
ber of posting lists for search. To recall top one
result on SIFT1M dataset, we ﬁnd 80% of queries
only need to search 6 posting lists, while 99% of
queries need to search 114 posting lists.

help retrieve some missing candidates back. The high-cost random disk accesses limit the number of
graph traverse and candidate reranking. HM-ANN leverages the heterogeneous memory by placing
pivot points promoted by the bottom-up phase in the fast memory and navigable small world graph in
the slow memory without data compression. However, it will lead to more than 1.5 times larger fast
memory consumption. Moreover, the slow memory is still much expensive than disk and may be not
available in some platforms. The theoretical analysis of the limits and the beneﬁts of the graph based
methods are given in [35].

3 SPANN

In this paper, we propose SPANN, a simple but efﬁcient vector indexing and search system, that
follows the inverted index methodology. Different from previous inverted index based methods that
leverage the lossy data compression to reduce the memory cost, SPANN adopts a simple memory-disk
hybrid solution.

Index structure: The data vectors X are divided into N posting lists {X1, X2, · · · , XN }, X1 ∪
X2 ∪ ... ∪ XN = X3. The centroids of these posting lists, c1, c2, · · · , cN , are stored in the memory
as the fast coarse-grained index that point to the location of the corresponding posting lists in the
disk.

Partial search: When a query q comes, we ﬁnd the K closest centroids, {ci1, ci2, . . . , ciK}, K (cid:28)
N , and load the vectors in the posting lists Xi1 , Xi2, · · · , XiK that correspond to the closest K
centroids into memory for further ﬁne-grained search.

3.1 Challenges

Posting length limitation: Since all the posting lists are stored in the disk, in order to reduce the
disk accesses, we need to bound the length of each posting list so that it can be loaded into memory
in only a few disk reads. This requires us to not only partition the data into a large number of posting
lists but also balance the length of posting lists. This is very difﬁcult due to the substantial high
clustering cost and the balance partition problem itself. The imbalanced posting lists will lead to high
variance of query latency especially when posting lists are stored in the disk.

Boundary issue: The nearest neighbor vectors of a query q may locate in the boundary of multiple
posting lists. Since we only search a small number of relevant posting lists, some true neighbors of
q that located in other posting lists will be missing (Illustrated in Figure 1). If red points are only
represented by the centroid of blue posting list, they will be missing in the nearest neighbor search of
yellow point.

Diverse search difﬁculty: We ﬁnd that different queries may have different search difﬁculty. Some
queries only need to be searched in one or two posting lists while some queries require to be searched

3For convenience, we use X to denote both the matrix and the vector set.

3

020406080100120140#visited postings5060708090100Queries (%)(6, 81.78%)(12, 90.48%)(114, 99.02%)recall@1 = 100%in a large number of posting lists (Illustrated in Figure 2). If we search the same number of posting
lists for all queries, it will result in either low recall or long latency.

All of the above challenges are the reasons why all of previous inverted index approaches adopt lossy
data compression solution that stores all the compressed vectors and the posting lists in the memory.

3.2 Key techniques to address the challenges

In this paper, we introduce three key techniques that solve the above challenges to enable the memory-
disk hybrid solution. In the index-building stage, we ﬁrstly limit the length of the posting lists to
effectively reduce the number of disk accesses for each posting list in the online search. Then we
improves the quality of the posting list by expanding the points in the closure of the corresponding
posting lists. This increases the recall probability of the vectors located on the boundary of the
posting lists. In the search stage, we propose a query-aware scheme to dynamically prune the access
of unnecessary posting lists to ensure both high recall and low latency. The detail design of each
technique will be introduced in the following sections.

3.2.1 Posting length limitation

Limiting the length of posting lists means we need to partition the data vectors X into a large number
of posting lists X1, X2, · · · , XN . Balancing the length of posting lists means we need to minimize
the variance of the posting length (cid:80)N
To address the posting length balance problem, we can leverage the multi-constraint balanced
clustering algorithm [30] to partition the vectors evenly into multiple posting lists:

i=1(|Xi| − |X|/N )2.

min
H,C

||X − HC||2

F + λ

N
(cid:88)

|X|
(cid:88)
(

i=1

l=1

hli − |X|/N )2, s.t.

N
(cid:88)

i=1

hli = 1.

(1)

where C ∈ RN ×m is the centroids, H ∈ {0, 1}|X|×N represents the cluster assignment, (cid:80)|X|
l=1 hli
is the number of vectors assigned to the i-th cluster (i.e. |Xi|) and λ is a trade-off hyper parameter
between clustering and balance constraints.

However, we ﬁnd that when the vector number |X| and the partition number N are very large,
directly using multi-constraint balanced clustering algorithm cannot work due to the difﬁculty of
large N -partition balanced clustering problem and the extremely high clustering cost. Therefore, we
introduce a hierarchical multi-constraint balanced clustering technique (Figure 3) to not only reduce
the clustering time complexity from O(|X| ∗ m ∗ N ) to O(|X| ∗ m ∗ k ∗ logk(N )) (k is a small
constant) but also balance the length of posting lists. We cluster the vectors into a small number
(i.e. k) of clusters iteratively until each posting list contains limit number of vectors. By using this
technique, we can greatly reduce not only the length of each posting list (disk accesses) but also the
index build cost.

Moreover, since the number of centroids is very large, ﬁnding the nearest posting lists for a query
needs to consume large computation cost.
In order to make the navigating computation more
meaningful, we replace the centroid with the vector that is closest to the centroid to represent each
posting list. Then the wasted navigating computation is transformed to the distance computation for a
subset of real candidates.

What’s more, in order to quickly ﬁnd a small number of nearest posting lists for a query, we create
a memory SPTAG [12] (MIT license) index for all the vectors that represent the centorids of the
posting lists. SPTAG constructs space partition trees and a relative neighborhood graph as the vector
index which can speedup the nearest centroids search to sub-millisecond response time.

3.2.2 Posting list expansion

To deal with boundary issue, we need to increase the visibility for those vectors that are located in
the boundary of the posting lists. One simple way is to assign each vector to multiple close clusters.
However, it will increase the posting size signiﬁcantly leading to the heavy disk reads. Therefore, we
introduce a closure multi-cluster assignment solution for boundary vectors on the ﬁnal clustering step
– assign a vector to multiple closest clusters instead of only the closest one if the distance between the

4

Figure 3: Hierarchical balanced
clustering: iteratively balanced
partition the vectors in a large
cluster (yellow cluster) into a
small number of small clusters
(green clusters) until each clus-
ter only contains limit number
of vectors (blue clusters).

Figure 4: Closure clustering as-
signment: assign boundary vec-
tors (green points) to multiple
closest clusters if its distances
to these clusters are nearly the
same (blue and yellow clusters).

Figure 5: Representative replica-
tion: use RNG rule to reduce the
similarity of two close posting
lists. The orange point will be
assigned to blue and grey post-
ing lists although it is closer to
yellow list than grey list.

vector and these clusters are nearly the same (Figure 4 gives an example):

x ∈ Xij ⇐⇒ Dist(x, cij) ≤ (1 + (cid:15)1) × Dist(x, ci1),
Dist(x, ci1) ≤ Dist(x, ci2) ≤ · · · ≤ Dist(x, ciK)

(2)

This means we only duplicate the boundary vectors. For those vectors which are very close to the
centroid of a cluster, they still keep one copy. By doing so, we can effectively limit the capacity
increase due to closure cluster assignment while increasing the recall probability of these boundary
vectors: they will be recalled if any of their closest posting lists is searched.

Since each posting list is small and we use closure assignment which will result in some posting lists
that are very close to each other contain the same duplicated vectors (For example, the green vectors
belong to both yellow and blue clusters). Too many duplicated vectors in the close posting lists will
also waste the high-cost disk reads. Therefore, we further optimize the closure clustering assignment
by using RNG rule [41] to choose multiple representative clusters for the assignment of an boundary
vector in order to reduce the similarity of two close posting lists (Figure 5). RNG rule can be simply
deﬁned as we will skip the cluster ij for vector x if Dist(cij, x) > Dist(cij−1, cij). The insight
is two close posting lists are more likely to be both recalled by the navigating index. Instead of
storing similar vectors in close posting lists, it would be better to store different vectors to increase
the number of seen vectors in the online search. From the vector side, it is better to be represented by
posting lists located in different directions (blue and grey posting lists in the example) than just being
represented by posting lists located in the same direction (blue and yellow posting lists).

3.2.3 Query-aware dynamic pruning

In the index-search stage, to process different queries effectively with different resource budget, we
introduce the query-aware dynamic pruning technique to reduce the number of posting lists to be
searched according to the distance between query and centroids. Instead of searching closest K
posting lists for all queries, we dynamically decide a posting list to be searched only if the distance
between its centroid and query is almost the same as the distance between query and the closest
centroid:

q search−→ Xij ⇐⇒ Dist(q, cij) ≤ (1 + (cid:15)2) × Dist(q, ci1),
Dist(q, ci1) ≤ Dist(q, ci2) ≤ · · · ≤ Dist(q, ciK)

(3)

By further reducing those unnecessary posting lists in the closest K posting lists, we can signiﬁcantly
reduce the query latency while still preserving the high recall by leveraging the resource more
reasonably and effectively.

4 Experiment

In this section we ﬁrst present the experimental comparison of SPANN with the current state-of-the-art
ANNS algorithms. Then we conduct the ablation studies to further analyze the contribution of each
technique. Finally, we setup an experiment to demonstrate the scalability of SPANN solution in the
distributed search scenario.

5

4.1 Experiment setup

We conduct all the experiments on a workstation machine with Ubuntu 16.04.6 LTS, which is
equipped with two Intel Xeon 8171M CPU (2600 MHz frequency and 52 CPU cores), 128GB
memory and 2.6TB SSD organized in RAID-0. The datasets we use are as follows:

1. SIFT1M dataset [3] is the most commonly used dataset generated from images for evaluating
the performance of memory-based ANNS algorithms, which contains one million of 128-
dimensional ﬂoat SIFT descriptors as the base set and 10,000 query descriptors as the test
set.

2. SIFT1B dataset [3] is a classical dataset for evaluating the performance of ANNS algorithms
that support large scale vector search, which contains one billion of 128-dimensional byte
vectors as the base set and 10,000 query vectors as the test set.

3. DEEP1B dataset [8] is a dataset learned from deep image classiﬁcation model which contains
one billion of 96-dimensional ﬂoat vectors as the base set and 10,000 query vectors as the
test set.

4. SPACEV1B dataset [6] (O-UDA license) is a dataset from commercial search engine which
derives from production data. It represents another different content encoding – deep natural
language encoding. It contains one billion of 100-dimensional byte vectors as a base set and
29,316 query vectors as the test set.

The comparison metrics to demonstrate the performance are:

1. Recall: We compare the R vector ids returned by ANNS with the R ground truth vector ids
to calculate the recall@R. Since there exist multiple data vectors sharing the same distance
with the query vector, we also replace some of the ground truth vector ids with the vector
ids that sharing the same distance to the query vector in the recall calculation.
2. Latency: We use the query response time in milliseconds as the query latency.
3. VQ (Vector-Query): The product of the number of vectors and the number of queries
per second a machine can serve (which is introduced in GRIP [50]). It demonstrates the
serving capacity of the search engine which takes both query latency and memory cost into
consideration. The higher VQ the system has, the less resource cost it consumes. Here we
use the number of vectors per KB × the number of queries per second as the VQ capacity.

4.2 SPANN on single machine

In this section, we demonstrate that inverted index based SPANN solution can also achieve the state-
of-the-art performance in terms of recall, latency and memory cost. We ﬁrst compare SPANN with
the state-of-the-art billion-scale disk-based ANNS algorithms on three billion-scale datasets. Then
we conduct an experiment on SIFT1M dataset to compare the VQ capacity with the start-of-the-art
all-in-memory ANNS algorithms. For all the experiments in this section, we use the following hyper-
parameters for SPANN: 1) use at most 8 closure replicas for each vector in the closure clustering
assignment; 2) limit the max posting list size to 12KB for byte vectors and 48KB for ﬂoat vectors; 3)
set (cid:15)1 for posting list expansion to 10.0, and set (cid:15)2 for query-aware dynamic pruning with recall@1
and recall@10 to 0.6 and 7.0 , respectively. We increase the maximum number of posting lists to be
searched in order to get the different recall quality.

4.2.1 Comparison with state-of-the-art billion-scale disk-based ANNS algorithms

We choose the state-of-the-art disk-based ANNS algorithms that can support billion-scale datasets
as our comparison targets. we do not compare with HM-ANN [36] since it is not open sourced
and the required PMM hardware may not be available in some platforms. Therefore, we compare
SPANN only with the state-of-the-art billion-scale disk-based ANNS algorithm DiskANN. We use
the default hyper parameters for DiskANN (same as the paper [39] for SIFT1B and SPACEV1B, and
the pre-build index provided by [2] for DEEP1B).

We carefully adjust the navigating memory index size of SPANN by choosing suitable number of
posting lists (about 10-12% of total vector number) to ensure both the algorithms consume the same
amount of memory (about 32GB for SIFT1B and SPACEV1B datasets and 60GB for DEEP1B

6

(a)

(b)

(c)

Figure 6: SPANN vs. DiskANN on (a) SIFT1B, (b) SPACEV1B, and (c) DEEP1B.

dataset). Figure 6(a) demonstrates the performance for SIFT1B dataset. From the results, we ﬁnd
SPANN signiﬁcantly outperforms DiskANN in both recall@1 and recall@10 especially in the low
query latency budget (less than 4ms). Especially, SPANN is more than two times faster than DiskANN
to reach the 95% recall@1 and recall@10.

The performance results for SPACEV1B and DEEP1B datasets are shown in Figure 6(b) and 6(c). It
also demonstrates that SPANN outperforms DiskANN in both recall@1 and recall@10 when query
latency budget is small (less than 4ms). Especially, DiskANN cannot achieve good recall quality
(90%) in less than 4ms in SPACEV1B dataset, while SPANN can obtain a recall of 90% in just around
1ms. For DEEP1B dataset, SPANN can also be more than two times faster than DiskANN to reach
the good recall quality (90%).

4.2.2 Comparison with state-of-the-art all-in-memory ANNS algorithms

Then we conduct an experiment on SIFT1M dataset to compare the VQ capacity with the start-of-
the-art all-in-memory ANNS algorithms, NSG [19], HNSW [32], SCANN [20], NGT-ONNG [23],
NGT-PANNG [22] and N2 [4]. These algorithms have presented state-of-the-art performance in
the ann-benchmarks [1]. We choose VQ capacity instead of latency as the comparison metric
since these algorithms use much more memory to trade for low latency. However, memory is an
expensive resource which has become the bottleneck for those algorithms to support large scale
datasets. Therefore, we should take both memory and latency into consideration in the performance
comparison. We take the SIFT1M dataset as an example due to the memory bottleneck of our test
machine. We believe that the observation can be generalized to billion scale datasets.

Most of these algorithms are graph based algorithms. For NSG, we get the pre-built index from [5]
and run the performance test with varying SEARCH_L from 1 to 256 which controls the quality of
the search results. For HNSW (nmslib), SCANN, NGT-ONNG, NGT-PANNG and N2 we use the
hyper parameters they provided in the ann-benchmarks [1] that achieve the best performance for the
SIFT1M dataset.

Figure 7 and 8 demonstrate the VQ capacity and query latency of all the algorithms on recall@1
and recall@10. We can see from the result that SPANN achieves the best VQ capacity consistently
across almost all the recall levels. This means although SPANN cannot achieve as low latency as the
all-in-memory ANNS algorithms due to the high-cost disk accesses during the search, it can obtain
the best serving capacity in the large scale vector search scenario.

4.2.3 Ablation studies

In this section, we conduct a set of experiments to do the ablation studies on each of our techniques
in the SIFT1M dataset.

7

0123456latency (ms)889092949698100recall@1 (%)SPANNDiskANN0123456latency (ms)889092949698100recall@10 (%)SPANNDiskANN0123456latency (ms)86889092949698100recall@1 (%)SPANNDiskANN0123456latency (ms)86889092949698100recall@10 (%)SPANNDiskANN0123456latency (ms)85.087.590.092.595.097.5100.0recall@1 (%)SPANNDiskANN0123456latency (ms)85.087.590.092.595.097.5100.0recall@10 (%)SPANNDiskANNFigure 7: VQ of different ANNS indices

Figure 8: Latency of different ANNS indices

Figure 9: Different numbers of centroids

Figure 10: Different types of centroid selection

Hierarchical balanced clustering There are three fast ways to partition the vectors on a single
machine into a large number of posting lists: 1) randomly choose a set of points as the posting list
centroids; 2) using hierarchical KMeans clustering (HC) to select centroids; 3) using hierarchical
balanced clustering (HBC) to generate a set of centroids. We compare the index quality by generating
16% points as the centroids using these three ways.

Figure 10 shows the recall and latency performance of these three centroid selection algorithms. For
both recall@1 and recall@10, we can see HBC centroid selection is better than random and HC
selections, which demonstrates that balance posting length is very important for inverted index based
methods. Moreover, HBC is very fast which clusters one million points into 160K clusters in only
around 50 seconds with 64 threads. The whole SPANN index can be built in around 2 minutes.

Moreover, how many centroids are needed? Small number of centroids can reduce the navigating
memory index size. However, large number of centroids usually means better performance. Therefore,
we need to make reasonable trade-off between the memory usage and the performance. Figure 9
compares the performance of different numbers of centroids. From the result, we can see that the
performance will increase signiﬁcantly with the growth of the centroid number when the centroid
number is small. However, when the number of centroids becomes large enough (16%), the per-
formance will not increase any more. Therefore, we can choose 16% of points as the centroids to
achieve both good search performance and small memory usage.

Closure clustering assignment To use closure clustering assignment, we need to assign a vector to
multiple closed clusters to increase its recall probability during the search. Then at most how many
closure replicas we need to duplicate for a vector to ensure the performance? Too small replicas
cannot help to retrieve those boundary vectors back. However, too many replicas will increase the
posting size greatly which will also affect the performance. Figure 11 demonstrates the performance
of different numbers of replicas for closure clustering assignment. From the result, we can see that
using more than one replicas improves the performance signiﬁcantly. However, when the number
of replicas is larger than 8, the performance cannot be improved any more. Therefore, we choose 8
replicas for all of our experiments.

Query-aware dynamic pruning In order to process different queries effectively during the online
search, we introduce the query-aware dynamic pruning technique to further reduce the number of
posting lists to be searched by pruning those unnecessary posting lists in the closest K posting lists.
We compare the performance with and without query-aware dynamic pruning in the Figure 12. From
the result, we can see that with query-aware dynamic pruning, we can further reduce the query latency
without recall drop especially when the latency budget is small. Note that, this technique can reduce
not only the query latency but also the resource usage for a query.

4.3 Extension of SPANN to distributed search scenario

Compared to the graph base approaches, the additional advantage for inverted index based SPANN
approach is that the partial search on the nearest posting lists idea can be easily extended to the

8

9092949698100recall@1 (%)010000200003000040000VQSPANNSCANNNSG HNSWNGT-ONNGNGT-PANNGN2889092949698100recall@10 (%)05000100001500020000250003000035000VQSPANNSCANNNSG HNSWNGT-ONNGNGT-PANNGN29092949698100recall@1 (%)0.000.250.500.751.001.251.50latency (ms)SPANNSCANNNSG HNSWNGT-ONNGNGT-PANNGN2889092949698100recall@10 (%)0.00.51.01.52.02.5latency (ms)SPANNSCANNNSG HNSWNGT-ONNGNGT-PANNGN212345latency (ms)85.087.590.092.595.097.5100.0recall@1 (%)4 % centroids8 % centroids16% centroids20 % centroids12345latency (ms)85.087.590.092.595.097.5100.0recall@10 (%)4% centroids8% centroids16% centroids20% centroids0.000.250.500.751.001.251.501.752.00latency (ms)949596979899100recall@1 (%)HBC centroidsHC centroidsRandom centroids0.51.01.52.02.5latency (ms)949596979899100recall@10 (%)HBC centroidsHC centroidsRandom centroidsFigure 11: Different numbers of closure replicas

Figure 12: W/O query-aware dynamic pruning

Figure 13: Data size and query access distribu-
tion across different machines

Figure 14: Comparison of recall, latency and
#machines dispatched in the end-to-end test

distributed search scenario, which can handle super large scale vector search with high efﬁciency and
low serving cost. The approach Pyramid [15] demonstrates the power of balanced partition and partial
search approach in the distributed scenario. To demonstrate the scalability of SPANN in distributed
search scenario, we partition the data vectors X evenly into M partitions {X1, X2, · · · , XM } by
using the multi-constraint balanced clustering and closure clustering assignment techniques in the
distributed index build stage, where M is the number of machines. In the online search stage, we
also adopt the query-aware dynamic pruning technique to reduce the number of dispatched machines,
which effectively limits the total cpu and IO cost for a query.

The only challenge for us is that there may have some hot-spot machines. Therefore, we need to
balance not only the data size but also the query access in each machine to avoid the hot spots. To
address the hot-spot challenge, we partition the vectors into multiple small partitions (larger than
machine number) and then use best-ﬁt bin-packing algorithm [17] to pack the small partitions into
large bins (the number of bins equals to the number of machines) according to the history query
access distribution. By doing so, we can effectively balance not only the data size but also the queries
processed on each machine.

We compare the optimized SPANN solution with traditional random partition and all dispatch solution
to demonstrate the effectiveness of workload reduction and scalability of SPANN in distributed search
scenario. We conduct the experiments below based on the SPACEV1B dataset and use about 100,000
query accesses history from production as the test workload. The workload is evenly split into three
sets: train, valid and test. The train set is used in ofﬂine distributed index build, and the test set is
used in the online search evaluation.

4.3.1 Workload reduction and scalability

Figure 13 shows the number of vectors and the number of test query accesses in each machine when
partitioning all the base vectors into 8, 16, and 32 partitions. From the result, we can see that SPANN
distributes all the data and query accesses evenly into different machines. Although it increases
the number of vectors in each machine by 20% due to closure assignment, it signiﬁcantly reduces
the query accesses in each machine compared to the random partition solution. Moreover, SPANN
can continually reduce the query accesses in each machine by using more machines while random
partition cannot. This means we can always add more machines to support more queries per second,
which demonstrates good scalability of our system. The reason why we can achieve good scalability
is that we effectively bound the number of machines to do the search for each query.

4.3.2 Analysis

Then we analyze how each technique affects the performance. We use 32 partitions case to do the
ablation study. We build SPANN single machine index for each partition and use the 29,316 query
vectors with ground truth as the test workload. Figure 14 demonstrates the recall, latency and the

9

1234latency (ms)708090100recall@1 (%)1 replica4 replicas8 replicas10 replicas0.51.01.52.02.53.03.5latency (ms)708090100recall@10 (%)1 replica4 replicas8 replicas10 replicas0.51.01.52.0latency (ms)949596979899100recall@1 (%)With dynamic cuttingWithout dynamic cutting0.51.01.52.02.5latency (ms)949596979899100recall@10 (%)With dynamic cuttingWithout dynamic cutting0510152025303540machine ID0.00.51.01.52.02.5#vectors1e8Random partitionBalanced clusteringSPANN0510152025303540machine ID020406080100query dispatched(%)Random partitionBalanced clusteringSPANN024681012latency (ms)94.595.095.596.096.597.0recall@10 (%)Random PartitionBalanced clusteringBalanced clustering + closureSPANNRandompartitionBalancedclusteringBalancedclustering+ closureSPANN05101520253035#machines dispatched32986.3average number of machines to dispatch in the end-to-end distributed search scenario. The left
ﬁgure shows that SPANN can achieve almost the best recall in each latency budget. In the right
ﬁgure, we can see that random partition solution needs to dispatch the query to all 32 machines for
search. Using multi-constraints balanced clustering technique can signiﬁcantly reduce the number
of dispatched machines to 9. By adding closure assignment, we can further reduce the number of
dispatched machines to 8. When all the techniques applied (including query-aware dynamic pruning
in the online search), we can ﬁnally reduce the number of dispatched machines to 6.3. This means we
can save about 80.3% of computation and IO cost for a query. Meanwhile, by reducing the number of
machines to search for a query, we can further reduce the query latency since we reduce the number
of candidates for ﬁnal aggregation.

5 Conclusion

In this paper, we introduce SPANN, a simple but surprising efﬁcient inverted index based ANNS
system, which achieves state-of-the-art performance for large scale datasets in terms of recall,
latency and memory cost. Different from previous inverted index based methods that use lossy data
compression to address the memory bottleneck, SPANN adopts a simple memory-disk hybrid solution
which only stores the centroids of the posting lists in the memory. We guarantee both low latency
and high recall by greatly reducing the number of disk accesses and improving the quality of posting
lists. Experiment results show SPANN can not only establish the new state-of-the-art performance for
billion scale datasets but also achieve good scalability when extended to distributed search scenario.
This demonstrates the ability of hierarchical SPANN to support super large scale vector search with
high efﬁciency and low serving cost.

6 Acknowledgements

We would like to thank Ben Karsin and Murat Guney from Nvidia to help us further speedup the
SPANN index build with GPU, which runs more than ﬁve times faster than CPU version.

References

[1] Benchmarking nearest neighbors. http://ann-benchmarks.com/.

[2] Billion-scale anns benchmarks. http://big-ann-benchmarks.com/.

[3] Datasets for approximate nearest neighbor search. http://corpus-texmex.irisa.fr/.

[4] Lightweight approximate nearest neighbor algorithm (n2). https://github.com/kakao/n2.

[5] Nsg : Navigating spread-out graph for approximate nearest neighbor search. https://github.

com/ZJULearning/nsg.

[6] Spacev1b: A billion-scale vector dataset for text descriptors.

https://github.com/

microsoft/SPTAG/tree/master/datasets/SPACEV1B.

[7] Artem Babenko and Victor Lempitsky. The inverted multi-index. IEEE transactions on pattern

analysis and machine intelligence, 37(6):1247–1260, 2014.

[8] Artem Babenko and Victor Lempitsky. Efﬁcient indexing of billion-scale datasets of deep
descriptors. In Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition
(CVPR), pages 2055–2063, 2016.

[9] Dmitry Baranchuk, Artem Babenko, and Yury Malkov. Revisiting the inverted indices for
billion-scale approximate nearest neighbors. In Proceedings of the European Conference on
Computer Vision (ECCV), pages 202–216, 2018.

[10] Jeffrey S Beis and David G Lowe. Shape indexing using approximate nearest-neighbour search
in high-dimensional spaces. In Proceedings of the IEEE Conference on Computer Vision and
Pattern Recognition (CVPR), pages 1000–1006, 1997.

[11] Jon Louis Bentley. Multidimensional binary search trees used for associative searching. Com-

munications of the ACM, 18(9):509–517, 1975.

10

[12] Qi Chen, Haidong Wang, Mingqin Li, Gang Ren, Scarlett Li, Jeffery Zhu, Jason Li, Chuanjie
Liu, Lintao Zhang, and Jingdong Wang. SPTAG: A library for fast approximate nearest neighbor
search, 2018.

[13] Sanjoy Dasgupta and Yoav Freund. Random projection trees and low dimensional manifolds.
Proceedings of the 40th Annual ACM Symposium on Theory of Computing, pages 537–546,
2008.

[14] Mayur Datar, Nicole Immorlica, Piotr Indyk, and Vahab S. Mirrokni. Locality-sensitive hashing
scheme based on p-stable distributions. In Proceedings of the Twentieth Annual Symposium on
Computational Geometry, SCG, pages 253–262, 2004.

[15] Shiyuan Deng, Xiao Yan, KW Ng Kelvin, Chenyu Jiang, and James Cheng. Pyramid: A general
framework for distributed similarity search on large-scale datasets. In Proceedings of the IEEE
International Conference on Big Data (Big Data), pages 1066–1071. IEEE, 2019.

[16] Wei Dong, Moses Charikar, and Kai Li. Efﬁcient k-nearest neighbor graph construction for
generic similarity measures. In Proceedings of the 20th International Conference on World
Wide Web (WWW), pages 577–586, 2011.

[17] György Dósa and Jiˇrí Sgall. Optimal analysis of best ﬁt bin packing. In International Colloquium

on Automata, Languages, and Programming, pages 429–441, 2014.

[18] Jerome H. Freidman, Jon Louis Bentley, and Raphael Ari Finkel. An Algorithm for Finding
Best Matches in Logarithmic Expected Time. ACM Transactions on Mathematical Software,
3(3):209–226, 1977.

[19] Cong Fu, Chao Xiang, Changxu Wang, and Deng Cai. Fast approximate nearest neighbor search

with the navigating spreading-out graphs. PVLDB, 12(5):461 – 474, 2019.

[20] Ruiqi Guo, Philip Sun, Erik Lindgren, Quan Geng, David Simcha, Felix Chern, and Sanjiv
Kumar. Accelerating large-scale inference with anisotropic vector quantization. In Proceedings
of the 37th International Conference on Machine Learning (ICML), pages 3887–3896, 2020.

[21] Kiana Hajebi, Yasin Abbasi-Yadkori, Hossein Shahbazi, and Hong Zhang. Fast approximate
nearest-neighbor search with k-nearest neighbor graph. In Proceedings of the 22nd International
Joint Conference on Artiﬁcial Intelligence (IJCAI), pages 1312–1317, 2011.

[22] Masajiro Iwasaki. Pruned bi-directed k-nearest neighbor graph for proximity search.

In
International Conference on Similarity Search and Applications, pages 20–33. Springer, 2016.

[23] Masajiro Iwasaki and Daisuke Miyazaki. Optimization of indexing based on k-nearest neighbor
graph for proximity search in high-dimensional data. arXiv preprint arXiv:1810.07355, 2018.

[24] P. Jain, B. Kulis, and K. Grauman. Fast image search for learned metrics. In Proceedings of the
IEEE Conference on Computer Vision and Pattern Recognition (CVPR), pages 1–8, 2008.

[25] Herve Jegou, Matthijs Douze, and Cordelia Schmid. Product quantization for nearest neighbor
search. IEEE transactions on pattern analysis and machine intelligence, 33(1):117–128, 2010.

[26] Hervé Jégou, Romain Tavenard, Matthijs Douze, and Laurent Amsaleg. Searching in one billion
vectors: re-rank with source coding. In Proceedings of the IEEE International Conference on
Acoustics, Speech and Signal Processing (ICASSP), pages 861–864, 2011.

[27] Jeff Johnson, Matthijs Douze, and Hervé Jégou. Billion-scale similarity search with gpus. IEEE

Transactions on Big Data, 2019.

[28] Yannis Kalantidis and Yannis Avrithis. Locally optimized product quantization for approximate
nearest neighbor search. In Proceedings of the IEEE Conference on Computer Vision and
Pattern Recognition (CVPR), pages 2321–2328, 2014.

[29] Brian Kulis and Trevor Darrell. Learning to hash with binary reconstructive embeddings. In
Advances in Neural Information Processing Systems, volume 22, pages 1042–1050, 2009.

[30] Hongfu Liu, Ziming Huang, Qi Chen, Mingqin Li, Yun Fu, and Lintao Zhang. Fast clustering
with ﬂexible balance constraints. In Proceedings of the IEEE International Conference on Big
Data (Big Data), pages 743–750. IEEE, 2018.

[31] Ting Liu, Andrew W Moore, Alexander Gray, and Ke Yang. An investigation of practical

approximate nearest neighbor algorithms. pages 825–832, 2004.

11

[32] Yu A Malkov and Dmitry A Yashunin. Efﬁcient and robust approximate nearest neighbor search
using hierarchical navigable small world graphs. IEEE transactions on pattern analysis and
machine intelligence, 42(4):824–836, 2018.

[33] Marius Muja and David G. Lowe. Scalable Nearest Neighbour Algorithms for High Dimensional
Data. IEEE Transactions on Pattern Analysis and Machine Intelligence, 36(11):2227–2240,
2014.

[34] David Nister and Henrik Stewenius. Scalable recognition with a vocabulary tree. In Proceedings
of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR), volume 2, pages
2161–2168, 2006.

[35] Liudmila Prokhorenkova and Aleksandr Shekhovtsov. Graph-based nearest neighbor search:
From practice to theory. In Proceedings of the International Conference on Machine Learning
(ICML), pages 7803–7813, 2020.

[36] Jie Ren, Minjia Zhang, and Dong Li. Hm-ann: Efﬁcient billion-point nearest neighbor search
on heterogeneous memory. In In Proceedings of the 34th International Conference on Neural
Information Processing Systems, volume 33, 2020.

[37] Anshumali Shrivastava and Ping Li. Asymmetric lsh (alsh) for sublinear time maximum
inner product search (mips). In Proceedings of the 27th International Conference on Neural
Information Processing Systems, volume 2, page 2321–2329, 2014.

[38] Robert F. Sproull. Reﬁnements to nearest-neighbor searching in k-dimensional trees. Algorith-

mica, 6(1-6):579–589, 1991.

[39] Suhas Jayaram Subramanya, Rohan Kadekodi, Ravishankar Krishaswamy, and Harsha Vardhan
Simhadri. Diskann: Fast accurate billion-point nearest neighbor search on a single node. In
Proceedings of the 33rd International Conference on Neural Information Processing Systems,
pages 13766–13776, 2019.

[40] Eric Sadit Tellez, Guillermo Ruiz, and Edgar Chavez. Singleton indexes for nearest neighbor

search. Information Systems, 60:50–68, 2016.

[41] Godfried T Toussaint. The relative neighbourhood graph of a ﬁnite planar set. Pattern recogni-

tion, 12(4):261–268, 1980.

[42] Jing Wang, Jingdong Wang, Gang Zeng, Zhuowen Tu, Rui Gan, and Shipeng Li. Scalable k-nn
graph construction for visual descriptors. In Proceedings of the IEEE Conference on Computer
Vision and Pattern Recognition (CVPR), pages 1106–1113, 2012.

[43] Jingdong Wang and Shipeng Li. Query-driven iterated neighborhood graph search for large
scale indexing. In Proceedings of the 20th ACM international conference on Multimedia, pages
179–188. ACM, 2012.

[44] Jingdong Wang, Naiyan Wang, You Jia, Jian Li, Gang Zeng, Hongbin Zha, and Xian Sheng
Hua. Trinary-projection trees for approximate nearest neighbor search. IEEE Transactions on
Pattern Analysis and Machine Intelligence, 36(2):388–403, 2014.

[45] Jingdong Wang and Ting Zhang. Composite quantization. IEEE Transactions on Pattern

Analysis and Machine Intelligence, 41(6):1308–1322, 2019.

[46] Jingdong Wang, Ting Zhang, Jingkuan Song, Nicu Sebe, and Heng Tao Shen. A survey on
learning to hash. IEEE Transactions on Pattern Analysis and Machine Intelligence, 40(4):769–
790, 2018.

[47] Yair Weiss, Antonio Torralba, and Rob Fergus. Spectral hashing.

In Advances in neural

information processing systems, pages 1753–1760, 2009.

[48] Hao Xu, Jingdong Wang, Zhu Li, Gang Zeng, Shipeng Li, and Nenghai Yu. Complementary
hashing for approximate nearest neighbor search. In Proceedings of the IEEE International
Conference on Computer Vision (ICCV), pages 1631–1638, 2011.

[49] Peter N Yianilos. Data Structures and Algorithms for Nearest Neighbor Search in General
Metric Spaces. Proceedings of the Fourth Annual ACM/SIGACT-SIAM Symposium on Discrete
Algorithms, pages 311–321, 1993.

[50] Minjia Zhang and Yuxiong He. Grip: Multi-store capacity-optimized high-performance nearest
In Proceedings of the 28th ACM International

neighbor search for vector search engine.
Conference on Information and Knowledge Management, pages 1673–1682, 2019.

12

[51] Ting Zhang, Chao Du, and Jingdong Wang. Composite quantization for approximate nearest
neighbor search. In Proceedings of the 31th International Conference on Machine Learning
(ICML), volume 32, pages 838–846, 2014.

13

