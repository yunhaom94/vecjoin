2024 IEEE 40th International Conference on Data Engineering (ICDE)
| CAGRA:      |     |          | Highly |     |         | Parallel |           | Graph  | Construction |     |           |       |      | and |
| ----------- | --- | -------- | ------ | --- | ------- | -------- | --------- | ------ | ------------ | --- | --------- | ----- | ---- | --- |
| Approximate |     |          |        |     | Nearest |          | Neighbor  |        | Search       |     |           | for   | GPUs |     |
|             | 1st | Hiroyuki | Ootomo |     |         |          | 2nd Akira | Naruse |              |     | 3rd Corey | Nolet |      |     |
|             |     | NVIDIA   |        |     |         |          | NVIDIA    |        |              |     | NVIDIA    |       |      |     |
|             |     | Tokyo,   | Japan  |     |         |          | Tokyo,    | Japan  |              |     | Maryland, | USA   |      |     |
ORCID: 0000-0002-9522-3789 ORCID: 0000-0002-3140-0854 ORCID: 0000-0002-2117-7636
|     |     | 4th    |      |     |     |     | 5th    |       |     |     | 6th |           |     |     |
| --- | --- | ------ | ---- | --- | --- | --- | ------ | ----- | --- | --- | --- | --------- | --- | --- |
|     |     | Ray    | Wang |     |     |     | Tamas  | Feher |     |     |     | Yong Wang |     |     |
|     |     | NVIDIA |      |     |     |     | NVIDIA |       |     |     |     | NVIDIA    |     |     |
32300.4202.64106EDCI/9011.01 :IOD | EEEI 4202© 00.13$/42/2-5171-3053-8-979 | )EDCI( gnireenignE ataD no ecnerefnoC lanoitanretnI ht04 EEEI 4202
|     |     | Shanghai, | China |     |     |     | Munich, | Germany |     |     | Shanghai, | China |     |     |
| --- | --- | --------- | ----- | --- | --- | --- | ------- | ------- | --- | --- | --------- | ----- | --- | --- |
ORCID: 0000-0001-8982-0571 ORCID: 0000-0003-2095-4349 ORCID: 0009-0005-0906-8778
Abstract—Approximate Nearest Neighbor Search (ANNS) sue.Inmanypracticalapplications,exactresultsarenotalways
plays a critical role in various disciplines spanning data mining necessaryandANNScanstrikeabalancebetweenthroughput
| and artificial | intelligence, |     | from | information |     | retrieval | and com- |     |     |     |     |     |     |     |
| -------------- | ------------- | --- | ---- | ----------- | --- | --------- | -------- | --- | --- | --- | --- | --- | --- | --- |
andaccuracy,reducingthecomputationalburdenandenabling
| puter vision | to   | natural | language | processing |           | and recommender |         |             |          |           |     |        |     |               |
| ------------ | ---- | ------- | -------- | ---------- | --------- | --------------- | ------- | ----------- | -------- | --------- | --- | ------ | --- | ------------- |
|              |      |         |          |            |           |                 |         | the scaling | to large | datasets. | The | impact | and | use-cases for |
| systems.     | Data | volumes | have     | soared     | in recent | years           | and the |             |          |           |     |        |     |               |
ANNSarewidespreadandincludeseveraldisciplinesspanning
computationalcostofanexhaustiveexactnearestneighborsearch
dataminingandartificialintelligence,suchaslanguagemodels
| is often | prohibitive, | necessitating |     | the | adoption | of  | approximate |     |     |     |     |     |     |     |
| -------- | ------------ | ------------- | --- | --- | -------- | --- | ----------- | --- | --- | --- | --- | --- | --- | --- |
techniques.Thebalancedperformanceandrecallofgraph-based
|            |             |          |          |            |             |      |              | in natural      | language    | processing |      | [14], [30],       | computer | vision      |
| ---------- | ----------- | -------- | -------- | ---------- | ----------- | ---- | ------------ | --------------- | ----------- | ---------- | ---- | ----------------- | -------- | ----------- |
| approaches | have        | more     | recently | garnered   | significant |      | attention in |                 |             |            |      |                   |          |             |
|            |             |          |          |            |             |      |              | [2], [13],      | information | retrieval  |      | [17], recommender |          | systems,    |
| ANNS       | algorithms, | however, |          | only a few | studies     | have | explored     |                 |             |            |      |                   |          |             |
|            |             |          |          |            |             |      |              | and advertising |             | [3], [15]. | ANNS | also              | forms    | the core of |
harnessingthepowerofGPUsandmulti-coreprocessorsdespite
|                |     |        |           |          |     |                 |     | many important |     | classes | of data | science and | machine | learning |
| -------------- | --- | ------ | --------- | -------- | --- | --------------- | --- | -------------- | --- | ------- | ------- | ----------- | ------- | -------- |
| the widespread |     | use of | massively | parallel | and | general-purpose |     |                |     |         |         |             |         |          |
computing. To bridge this gap, we introduce a novel parallel algorithmssuchasclustering[20],classification[21],manifold
computing hardware-based proximity graph and search algo- learning and dimensionality reduction [22]. Various different
rithm.Byleveragingthehigh-performancecapabilitiesofmodern categories of algorithms for ANNS have been proposed and
hardware,ourapproachachievesremarkableefficiencygains.In
arewell-studied,includinghashing-based[4],tree-based[25],
| particular, | our | method | surpasses | existing | CPU | and | GPU-based |     |     |     |     |     |     |     |
| ----------- | --- | ------ | --------- | -------- | --- | --- | --------- | --- | --- | --- | --- | --- | --- | --- |
methods in constructing the proximity graph, demonstrating quantization-based [12], and graph-based methods.
higherthroughputinbothlarge-andsmall-batchsearcheswhile The graph-based method for ANNS relies on a proximity
maintaining compatible accuracy. In graph construction time, graph, or a graph that represents the similarity relationships
2.2–27×
our method, CAGRA, is faster than HNSW, which is among data points within a dataset. Graph-based methods
| one of     | the CPU | SOTA    | implementations. |            | In     | large-batch | query     |         |             |        |              |     |             |       |
| ---------- | ------- | ------- | ---------------- | ---------- | ------ | ----------- | --------- | ------- | ----------- | ------ | ------------ | --- | ----------- | ----- |
|            |         |         |                  |            |        |             |           | involve | two primary | steps: | constructing |     | a proximity | graph |
| throughput | in      | the 90% | to               | 95% recall | range, | our         | method is |         |             |        |              |     | k           |       |
33–77× faster than HNSW, and is 3.8–8.8× faster than the from a dataset and traversing it to find the closest nodes
SOTAimplementationsforGPU.Forasinglequery,ourmethod to the input query. The question of determining the optimal
is 3.4–53× faster than HNSW at 95% recall. proximity graph structure is not easily answered theoreti-
Index Terms—approximate nearest neighbors, graph-based, k-nearest
|             |            |     |        |            |         |     |     | cally. For | instance, | the graph   | quality   | as     | a        | neighbor |
| ----------- | ---------- | --- | ------ | ---------- | ------- | --- | --- | ---------- | --------- | ----------- | --------- | ------ | -------- | -------- |
| information | retrieval, |     | vector | similarity | search, | GPU |     |            |           |             |           |        |          |          |
|             |            |     |        |            |         |     |     | graph does | not       | necessarily | guarantee | higher | accuracy | [29].    |
Therefore,researchershavefocusedonoptimizingthegraph’s
|     |     |     | I. INTRODUCTION |     |     |     |     |            |               |     |               |     |              |     |
| --- | --- | --- | --------------- | --- | --- | --- | --- | ---------- | ------------- | --- | ------------- | --- | ------------ | --- |
|     |     |     |                 |     |     |     |     | efficiency | and structure |     | heuristically | and | empirically. | One |
The importance of Approximate Nearest Neighbor Search notable approach is the NSW (Navigable Small World) graph
(ANNS)hasgrownsignificantlywiththeincreasingvolumeof proposed by Malkov et al. [19], which leverages the Small
dataweencounter.ANNSisparticularlyrelevantinsolvingthe World phenomenon [27] to enhance the search performance
k Nearest Neighbor Search (k-NNS) problem, where we seek of the proximity graph. Building upon this idea, HNSW
k
to find the vectors closest to a given query vector, typically (Hierarchical Navigable Small World) [18] graphs address
using a distance like the L2 norm, from a dataset of vectors. issuespresentinNSW,whereafewnodeshavealargedegree,
The simplest exact solution for k-NNS involves exhaustively hindering the high-performance search. HNSW addresses this
calculating the distance between the query vector and all problem by introducing a hierarchical graph structure and
k
vectors in the dataset, then outputting the vectors of the setting an upper bound on the maximum degree. Another
(top-k)
smallest distances as results. However, this approach approachisNSG(NavigatingSpreading-outGraph),proposed
becomes infeasible for large datasets due to the sheer number by Fu et al. [8], which approximates a Monotonic Relative
of similarity computations required, making scalability an is- NeighborhoodGraph(MRNG)structuretohelpguaranteelow
| 2375-026X/24/$31.00 ©2024 IEEE |     |     |     |     |     |     |     | 4236 |     |     |     |     |     |     |
| ------------------------------ | --- | --- | --- | --- | --- | --- | --- | ---- | --- | --- | --- | --- | --- | --- |
DOI 10.1109/ICDE60146.2024.00323
Authorized licensed use limited to: The University of Toronto. Downloaded on August 02,2026 at 23:31:31 UTC from IEEE Xplore.  Restrictions apply.

search complexity. These are just a few examples of graph and large-batch queries. We harness software warp split-
structures used in ANNS, and numerous other graphs have tingandforgettablehashtablemanagementtoutilizethe
been well-studied in the field [29]. GPU resource efficiently.
When it comes to implementing graph-based ANNS meth- • We demonstrate that CAGRA achieves a higher perfor-
ods,fewstudieshaveintroducedhigh-performanceimplemen- mance in graph construction and query than the state-of-
tations optimized for data-center servers capable of harness- the-artgraph-basedANNSimplementationsforCPUand
ing the massive parallelism offered by GPUs. The memory GPU. In graph construction time, CAGRA is 2.2–27×
bandwidth to load the dataset vectors can be a bottleneck faster than HNSW. In large-batch query throughput in
of the search throughput, not only in graph-based, but also the 90% to 95% recall range, CAGRA is 33–77× faster
in other ANNS implementations. Since a GPU, typically has than HNSW and is 3.8–8.8× faster than the SOTA
high memory bandwidth, it is potentially suitable for ANNS. implementations for GPU. For a single query, CAGRA
One notable implementation is SONG [33], which stands as is 3.4–53× faster than HNSW at 95% recall.
the first graph search implementation on GPUs, using various
II. BACKGROUND
optimization techniques. These techniques include employing
A. Approximate Nearest Neighbor search
the open addressing hash table and performing multi-query
searches within a warp. With these optimizations, SONG has In the k-NNS problem, we obtain k vectors
higher throughput than IVFPQ on GPU included in FAISS x i1 ,x i2 ,...,x ik ∈ Rn that satisfy the following condition
[11] and HNSW on CPU. Similarly, GANNS is a GPU- from a dataset D∈Rn×N:
friendly graph search and construction method tailored for i 1 ,i 2 ,...,i k =k-argminiDistance(x i ,q), (1)
NSW, HNSW, and k nearest neighbor graphs on GPUs [32].
This approach further advances the efficiency of graph-based
whereq∈Rn isagivenqueryvector,k-argmini isthetop-k
argumentsinascendingorder,andDistance(·)(Rn×Rn →R)
ANNSonGPUarchitecturesbymodifyingdatastructuresfor
isadistancemeasure.ThedistanceistypicallytheL2normor
GPUsandreducingtheiroperationtime.Additionally,Grohet
cosinesimilarity.Althoughk-ANNSobtainsk similarvectors
al.presentGGNN,afastgraphconstructionandsearchmethod
to a given query vector, the results are not always exact. We
designed explicitly for GPUs [9]. Their work also improves
evaluate the accuracy of the results for a query as recall:
theoverallperformanceofANNSonGPUsbyimprovingdata
structures for GPUs and utilizing fast shared memory. Some recall=|U ∩U |/|U |, (2)
ANNS NNS NNS
studies have pointed out and managed the issue that graph
whereU isthesetofresultingvectorsobtainedbyANNS
construction can be time-consuming by using the advantage ANNS
and U is by NNS. We denote the recall of k-ANNS as
that a proximity graph can be reused once it is constructed. NNS
“recall@k”. There is typically a trade-off between the recall
Unfortunately, there still remains a critical challenge in ef-
and throughput (QPS; Query Per Second).
ficiently designing proximity graphs that are well-suited for
GPU architectures in both construction and search. Despite B. CUDA
the progress made in using GPUs for graph-based ANNS, The GPU, or Graphics Processing Unit, has been broadly
mostexistingstudiesfocusonadaptingoroptimizingexisting used for general-purpose computing in recent years, whereas
graphs for GPU utilization rather than specifically designing it was initially developed strictly for graphics processing.
proximity graphs from the ground up to fully leverage the NVIDIAproposesandhasbeendevelopingCUDA,whichal-
GPU’s capabilities in both graph construction and subsequent lowsustoleveragethehigh-performancecomputingcapability
search operations. of the GPU for general-purpose computing. While the GPU
This paper proposes 1) a proximity graph suitable for has higher parallelism and memory bandwidth than the CPU,
parallel computing in graph construction and query search we have to be able to abstract parallelism from an algorithm
and 2) a fast ANNS graph construction and search imple- and map it to the architecture of the GPU to leverage its high
mentation, CAGRA (Cuda Anns GRAph-based), optimized performance. Therefore, not all applications can gain higher
forNVIDIAGPU.Ourgraphissearchimplementation-centric performancebyjustusingtheGPU. Webrieflyintroducethe
anddesignedtoincreasetheefficiencyofamassivelyparallel architecture of NVIDIA GPU in the following sections, and
computing device, like the GPU, rather than theoretical graph further information on the architecture can be found in [23].
quality. 1) Threadhierarchy: IntheNVIDIAGPUthreadhierarchy,
The summary of our contributions is as follows: 32threadsinagroupcalled“warp”executethesameinstruc-
• We propose a proximity graph for ANNS and its con- tion simultaneously. On the other hand, different instructions
struction method suitable for massively parallel com- arenotexecutedinawarpinparallel,leadingtoaperformance
puting. This method reduces the memory footprint and degradation called “warp divergence”. A group of up to 32
usage, which can be the performance bottleneck in the warpscomposesaCTA(CooperativeThreadArray),orthread
graph optimization process, by avoiding exact similarity block, and a CTA is executed on a single GPU streaming
computation. multiprocessor (SM). The SM is like a core in a multi-core
• WeprovideasearchimplementationoptimizedforGPU, CPU, and since there are many SMs on recent GPUs, we can
which is designed to gain high throughput in both single launch and operate multiple CTAs at a time.
4237
Authorized licensed use limited to: The University of Toronto. Downloaded on August 02,2026 at 23:31:31 UTC from IEEE Xplore. Restrictions apply.

2) Memory hierarchy: In the memory hierarchy of the non-fixed degree for each node has an advantage in that
GPU, the device memory has the largest size, and all threads we can reduce the less important distance computation
can access the same memory space. Shared memory, on the by keeping only essential edge connections. However,
other hand, is a local memory used within each CTA and all in the case of GPU, too small a degree doesn’t fully
thethreadsintheCTAsharethememoryspace.Whilethesize saturate the computing resources allocated to each CTA,
of shared memory is much smaller than the device memory, leading to lower hardware utilization. Rather, it is better
ithaslowerlatencyandhigherbandwidth.Registersarelocal toexpandthesearchspaceusingalltheavailablecompute
data storage for each thread and have lower latency than the resources, as it won’t increase the overall compute time.
shared memory. Another advantage is that fixing the degree allows more
|            |      |     |     |     |     |     | uniform | computation, |          | thus  | creating  | less   | load  | imbalance |
| ---------- | ---- | --- | --- | --- | --- | --- | ------- | ------------ | -------- | ----- | --------- | ------ | ----- | --------- |
| C. Related | work |     |     |     |     |     |         |              |          |       |           |        |       |           |
|            |      |     |     |     |     |     | during  | the          | parallel | graph | traversal | phase, | which | would     |
Variousalgorithmsforgraph-basedANNSwereintroduced lead to low hardware utilization. We set the degree de-
inSec.Isowefocusthissectionspecificallyonhighlyparal- pendingonthedatasetandrequiredrecallandthroughput.
| lel and GPU-accelerated |     | graph-based |     | ANNS | implementations |     |                |     |       |     |            |           |     |          |
| ----------------------- | --- | ----------- | --- | ---- | --------------- | --- | -------------- | --- | ----- | --- | ---------- | --------- | --- | -------- |
|                         |     |             |     |      |                 |     | • Directional. |     | Since | the | out-degree | is fixed, | the | graph is |
whilst outlining how our contributions compare to them. naturally directional.
1) SONG: SONGisthefirstgraph-basedANNimplemen- • No hierarchy. HNSW, for instance, employs a hier-
tationforGPUproposedbyZhaoetal.[33].UnlikeCAGRA, archical graph to determine the initial nodes on the
| this method | does | not contribute |     | a faster | graph | construction |        |        |          |     |        |      |         |        |
| ----------- | ---- | -------------- | --- | -------- | ----- | ------------ | ------ | ------ | -------- | --- | ------ | ---- | ------- | ------ |
|             |      |                |     |          |       |              | bottom | layer. | However, |     | in the | case | of GPU, | we can |
technique and relies on other methods like NSW [19], NSG obtaincompatibleinitialnodesbyrandomlypickingsome
[8], and DPG [16]. SONG proposes a dataset and several nodes and comparing their distances to the query, thus
optimizations for the GPU, in which they use open address employing the high parallelism and memory bandwidth
| hash table, | bounded | priority | queue, | and | dynamic | allocation |     |     |     |     |     |     |     |     |
| ----------- | ------- | -------- | ------ | --- | ------- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
ofGPU.ThedetailofthesearchalgorithmisinSec.IV.
reduction.Theyhaveachieved10–180×speedupontheGPU
|     |     |     |     |     |     |     | Two | main steps | are | involved | in  | the construction |     | of the |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | --- | -------- | --- | ---------------- | --- | ------ |
compared to single-threaded HNSW on CPU. CAGRAgraph:1)buildingak-NNgraphand2)optimizingit
2) GGNN: GGNN is a GPU-friendly implementation of toenhancesearchrecallandthroughput.Wechosek-NNgraph
graph-basedANNSproposedbyGrohetal.[9]that,likeCA-
|     |     |     |     |     |     |     | as the base | graph | because | the | fixed | out-degree | graph | is well- |
| --- | --- | --- | --- | --- | --- | --- | ----------- | ----- | ------- | --- | ----- | ---------- | ----- | -------- |
GRA,providesbothahigh-throughputsearchimplementation suitedforefficientGPUoperations,andwecanrapidlybuildit
| and a fast | graph | construction | technique |     | that can | utilize high |     |     |     |     |     |     |     |     |
| ---------- | ----- | ------------ | --------- | --- | -------- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- |
usingnearestneighborsdescent(NN-descent)[29]evenonthe
parallelism.GGNNwasdemonstratedtooutperformSONGin
|             |                                      |     |     |     |     |     | GPU [28].    | The      | following | section | outlines | the         | heuristic | graph      |
| ----------- | ------------------------------------ | --- | --- | --- | --- | --- | ------------ | -------- | --------- | ------- | -------- | ----------- | --------- | ---------- |
| large-batch | searches.                            |     |     |     |     |     |              |          |           |         |          |             |           |            |
|             |                                      |     |     |     |     |     | optimization | approach |           | and its | parallel | computation |           | algorithm. |
| 3) GANNS:   | GANNSisalsoaGPU-acceleratedgraphcon- |     |     |     |     |     |              |          |           |         |          |             |           |            |
struction and search method proposed by Yu et al. [32]. They A. Graph optimization
propose a GPU-based NSW graph construction method and The primary objective of CAGRA graph optimization is
| show that | both the | proximity | graph | construction |     | and search |            |              |     |       |     |              |     |           |
| --------- | -------- | --------- | ----- | ------------ | --- | ---------- | ---------- | ------------ | --- | ----- | --- | ------------ | --- | --------- |
|           |          |           |       |              |     |            | to enhance | reachability |     | among | a   | large number |     | of nodes. |
performance are better than SONG. Reachability is characterized by two properties: 1) whether
Unfortunately, between GGNN and GANNS, it is unclear we can traverse from any arbitrary node to another arbitrary
which is the state-of-the-art graph-based ANNS GPU imple- node and 2) the number of nodes we can traverse from one
| mentation | since | there is | no study | on  | comparison | between |             |             |     |        |         |             |     |     |
| --------- | ----- | -------- | -------- | --- | ---------- | ------- | ----------- | ----------- | --- | ------ | ------- | ----------- | --- | --- |
|           |       |          |          |     |            |         | node within | a specified |     | number | of path | traversals. |     |     |
them. In addition, all of the above GPU implementations are To assess property 1), we measure the number of strongly
focusedonapplicationswithalargenumberofqueries.Tothe connected components (CC) in the graph. The number of CC
best of our knowledge, no GPU implementation outperforms is determined as follows:
| the CPU | implementation |     | for applications |     | with | small-batch |       |       |           |      |     |          |       |        |
| ------- | -------------- | --- | ---------------- | --- | ---- | ----------- | ----- | ----- | --------- | ---- | --- | -------- | ----- | ------ |
|         |                |     |                  |     |      |             | There | is no | guarantee | that | the | base kNN | graph | is not |
queries.Inthispaper,wewillshowthatCAGRAoutperforms disconnected [20], and the weak CC represents the number
both the CPU and GPU in graph construction and search. of subgraphs in the graph. Additionally, in the case of a
directionaledgegraph,theremaybescenarioswheretraversal
|         |          | III. CAGRAGRAPH |     |        |     |                 |                 |      |               |     |               |               |         |           |
| ------- | -------- | --------------- | --- | ------ | --- | --------------- | --------------- | ---- | ------------- | --- | ------------- | ------------- | ------- | --------- |
|         |          |                 |     |        |     |                 | from one        | node | to another    | is  | not possible, |               | even if | the graph |
| In this | section, | we explain      | the | design | and | features of the |                 |      |               |     |               |               |         |           |
|         |          |                 |     |        |     |                 | is not entirely |      | disconnected. |     | A graph       | is considered |         | strongly  |
CAGRA graph. While some graphs are designed to follow or connected when an arbitrary node in the graph can reach
approximategraphswithsometheoreticalproperties,including any other node. The number of strong CC is the count of
| monotonicity, | the           | CAGRA     | graph | is a search | implementation- |             |             |           |            |           |        |       |        |            |
| ------------- | ------------- | --------- | ----- | ----------- | --------------- | ----------- | ----------- | --------- | ---------- | --------- | ------ | ----- | ------ | ---------- |
|               |               |           |       |             |                 |             | node groups | in        | the graph, | where     | each   | group | forms  | a strongly |
| centric and   | heuristically | optimized |       | graph.      | The             | CAGRA graph |             |           |            |           |        |       |        |            |
|               |               |           |       |             |                 |             | connected   | subgraph. |            | A smaller | number | of    | strong | CC are     |
has the following features: preferred because a larger number of CC can lead to more
• Fixed out-degree (d). By fixing the out-degree, we can unreachable nodes starting from a search start node.
utilize the massive parallelism of GPU effectively. Most To assess property 2), we utilize the average 2-hop node
(N
graph-basedANNSalgorithmsbuildandutilizenon-fixed count 2hop ) for all nodes in the graph as the metric. The
out-degreegraphs.Insingle-threadexecutiononaCPU,a 2-hop node count of a given node is defined as the number
4238
Authorized licensed use limited to: The University of Toronto. Downloaded on August 02,2026 at 23:31:31 UTC from IEEE Xplore.  Restrictions apply.

initial rank
= index of the neighbor node Sorted by distance in each row
Neighbor node list Neighbor node list Neighbor node list Neighbor node list
rank-based construct
1 2 3 reordering+pruning 1 2 3 reversed graph 1 2 3 merge 1 2 3
6 4 6 4 6 4 6 4
Dataset 5 5 5 5
Initial kNN graph reordered+pruned graph reversed graph CAGRA graph
Initial graph construction Optimization
Fig.1. ConstructionflowoftheCAGRAgraph.
of nodes that can be reached in two steps from the node. Its W initial rank N D o e t t o d u e r t a o b u l r e able d r # o u d t e e t s ou fr r o a m ble X
maximum value is determined as Nmax =d+d2 where d is
the degree of the graph. A higher a 2 v h e o r p age 2-hop node count 2 2 C 2 2 2 C 2 C 2
indicates that more nodes can be explored during specific 1 B 3 1 D 1 B 3 1 D 1 B D
search iteration steps. A 2 4 A 2 4 A 2 1
In the CAGRA graph optimization, two key techniques are 1 X 1 X 0 1 X
employed on the initial kNN graph: reordering and reverse 5 5 5
edge addition. Reordering is a technique that reorders each
edge of the initial kNN graph in an order that increases the E E 0 E
diversity of the graph, rather than in the order of its length,
Fig.2. CAGRAedgereorderingandpruningflow.Weassumepruningedges
and has the primary effect of increasing 2-hop node counts. from the node X. Left: The initial rank of the edges from X and other
Reverseedgeadditionisatechniqueoftenusedinothergraph- relatededges.Middle:Possibletwo-hoproutes,classifiedasdetourableand
based ANN implementations and improves node reachability not detourable by Eq. 3. We use the rank instead of the distance. Right:
The number of detourable routes of each node connected to X. The edges
while reducing strong CC values.
arediscardedfromtheendofthelistorderedbythenumberofdetourable
routes.Inthisexample,thenodesA,B,andEarepreservedastheneighbors
ofnodeX,althoughthenodeEisthefarthestintheinitialneighborsofnode
B. Graph construction and optimization algorithm
X inthedistance.
The CAGRA graph is a directed graph where the degree,
d, of all nodes is the same. The construction of the graph In the reordering edges step, we determine the significance
consists of two stages: 1) construction of an initial graph and of an edge, rank, to prune the edges at the end of the entire
2) optimization, as shown in Fig. 1. optimization.Existingpruningalgorithmspruneanedgefrom
1) Initial graph construction: We construct a k-NN graph one node to another if it can be bypassed using another route
as an initial graph where the degree of each node is k = (detourable route) that satisfies certain criteria. For instance,
d init . We use NN-Descent [5] to construct the graph and will in NGT [10], it defines the detourable route from X to Y as
typically set d init to be 2d or 3d, where d is the degree of a pair of two edges as follows:
the final CAGRA graph. As a final step in this process, we
sort the connected node list of each node in ascending order (e X→Z ,e Z→Y) s.t. max(w X→Z ,w Z→Y)<w X→Y , (3)
basedondistancefromthesourcenode.Thissortingoperation where e ·→· and w ·→· denote a directed edge between two
can be efficiently executed in parallel using GPUs since no nodesandthedistance,respectively,andZ isanodewithadi-
dependencyexistsinthecomputationforeachindividualnode rectconnectionfromXandadirectconnectiontoY.Basedon
list. We assume that the initial k-NN graph has sufficient thispruning,weconsidertworeorderingtechniques,distance-
connectivityamongnodes.AndthegoaloftheCAGRAgraph based and rank-based reordering, and adopt rank-based in
optimizationistoreducethedegreeofthegraphtoreducethe the CAGRA graph optimization. While the complexity of
size while preserving the reachability. both the reordering operations is O(Nd3), the distance-based
2) Graph optimization: The optimization process involves strategy requires distance calculations between one node and
two steps: 1) reordering edges, and 2) adding reverse edges. its neighbors.
It takes the initial graph as input and produces the CAGRA In distance-based reordering, we first count the number of
graph as output. This process offers notable advantages: i) it detourableroutesforeachedgeandreorderthenodelistbythe
no longer requires the dataset or distance computation, and counts in ascending. A smaller number of detourable routes
ii) it allows for many computations to be executed in parallel for an edge indicates that this edge is more important to keep
without complex dependencies. the 2-hop node counts. Then, we set the position of an edge
4239
Authorized licensed use limited to: The University of Toronto. Downloaded on August 02,2026 at 23:31:31 UTC from IEEE Xplore. Restrictions apply.

in the node list as a rank of the edge, which is an indicator TABLEI
of the importance of the edge. The computation of distance- DATASETSUSEDINTHEEVALUATIONS
b d a e s to e u d ra re b o le rd r e o r u in te g s h fo as re h a ig ch h e p d a g ra e ll i e n li p sm ara s l i l n el c . e H w o e we c v a e n r, c w ou e n n t e t e h d e Dim(n) Size(N) Datatype C de A g G re R e A (d g ) raph
SIFT-1M1 128 1M float 32
to compute the distances on the fly during the operation or
GIST-1M1 960 1M float 48
makeadistancetablebeforetheoperation,makingthismethod GloVe-200[24] 200 1183514 float 80
impractical for a large dataset. In the former case, we need NYTimes[1] 256 290K float 64
N×d ×(d −1) distance computations, and in the latter DEEP-1M2 96 1M float 32
case,w in e it need i a ni d t istancetablewithN×d entriesonmemory, DEEP-10M2 96 10M float 32
init DEEP-100M[31] 96 100M float 32
where N is the size of the dataset.
Forrank-basedreordering,wesetthepositionoftheedgein
the neighbor node list, which is sorted by distance at the end
of the initial graph construction, as the initial rank, similar
to distance-based reordering. Then, we reorder the edges in
the same way as distance-based reordering, but we use the
initial rank instead of the distance, as shown in Fig. 2. In
other words, we approximate the distance by the initial rank.
This approximation allows us not to compute the impractical
amount of distance computations and not to store the large
size of the distance table in memory. We set the order index
of a node as the rank, the same as distance-based. We adopt
rank-based reordering in the CAGRA graph optimization and
only keep top d neighbors for each node (pruning).
Afterreordering,wecreateareversedgraphwherealledges Fig. 3. The 2-hop node counts and strong CC comparison among a k-NN
have opposite directions of the reordered and pruned graph. graph,partiallyandfullyoptimizedgraphsbyCAGRAfromaninitialk-NN
graph.Thenumberineachbracketinthelabelisthedegreeofthegraph(d),
Sincethenumberofincomingedgespernode,orin-degree,is
andwesetthedegreeoftheinitialgraphasd
init
=3d.
not fixed in the reordered graph, the out-degree of each node
in the reversed graph is also not fixed. However, we set the
upper bound of the degree to d because of an attribute of the Q-A3 Does rank-based reordering have compatible recall
next operation. And we make the reversed graph so that the with distance-based?
reversed edges are sorted by the rank in the pruned graph in
We use the datasets in Table I. All experiments are
ascending order. It means “Someone who considers you are
conductedonaDGXA100serverequippedwithAMDEPYC
more important is also more important to you”. The process
of adding reverse edges has a complexity of O(Nd). 7742CPU(64cores)andNVIDIAA100(80GB)GPU,high-
end processors released within a similar timeframe. We put
Finally, we merge the pruned graph and reversed graph. In
boththedatasetandgraphonthedevicememoryoftheGPU.
this process, we basically take d/2 children for each parent
In the CAGRA graph construction, we build an initial k-NN
node from each graph and interleave them. When the number
graph on GPU and optimize it on CPU.
of children for a parent node in the reversed edge graph is
fewer than d/2, we compensate them by taking from the 1) Q-A1: Connected components and 2-hop node count:
In the CAGRA graph construction, two optimizations are
pruned graph.
To find an optimal d, we build graphs with different performed on the initial k-NN graph: reordering and reverse
edge addition. Then, how much effect does each optimization
numbers, such as 32, 64, and 96, and measure their search
have? To evaluate this, we have compared the properties of
performance.Thereisnodeterministicwaytofindtheparam-
a standard k-NN graph, a partially optimized CAGRA graph
eter in a single shot since it depends on the dataset and user
(using only one optimization), and a fully optimized CAGRA
requirements. This is not unlike the hyper-parameters ofother
graph (using both optimizations).
methods,forexample,themaximumout-degreeoftheHNSW
The results of the 2-hop node count and the strong CC
(libhnsw)graph.Increasingtheout-degreeimprovestherecall
experiments are shown in Fig. 3. In the case of the 2-hop
while the search throughput degrades.
node count, we observe that both optimizations increase the
average 2-hop count, and the effect of the reordering is more
C. Evaluation of the CAGRA graph and optimization
significant compared to the reverse edge addition. The results
This section reveals the following question: also show that reverse edge addition significantly affects the
Q-A1 HowmuchdotheCCand2-hopnodecountsimprove strong CC more than reordering.
with the CAGRA graph optimization?
Q-A2 How fast is rank-based reordering compared to 1DatasetsforANNS:http://corpus-texmex.irisa.fr/
distance-based? 2First1Mand10MvectorsofDEEP-100Mdataset[31].
4240
Authorized licensed use limited to: The University of Toronto. Downloaded on August 02,2026 at 23:31:31 UTC from IEEE Xplore. Restrictions apply.

Bu(cid:1)er
entry: Node index and distance to the query
|     |     |     |     |     |     |     |     | Internal top-M | Candidates list |              |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | -------------- | --------------- | ------------ | --- | --- | --- |
|     |     |     |     |     |     |     |     | (length=M)     |                 | (length=p*d) |     |     |     |
Search algorithm
0Random sampling
Sample random nodes and calculate the distance to the query.
Fig.4. CAGRAgraphoptimizationtimecomparisonwithrank-anddistance- The results are stored in the candidates list.
basedreordering.
Dummy large distances (e.g. FLT_MAX)
1 Update internal top-M
Obtain the top M smallest distance entries and
store them in the internal top-M list.
|     |     |     |     |     |     |     |     | 3 Distance calculation |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------------------- | --- | --- | --- | --- | --- |
Calculate the distance between the query and each node in the
candidate list if it is for the (cid:2)rst time to be the candidate.
|     |     |     |     |     |     |     |     |     | 2 Candidate list index update |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ----------------------------- | --- | --- | --- | --- |
Store the neighbor indices of a parent node.
The distances are large dummy large values.
|     |     |     |     |     |     |     |     |     | i=3 | i=5 4 | 1 9 |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ----- | --- | --- | --- |
Parentnode
9
|     |     |     |     |     |     |     |     | Proximity graph | 3   |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --------------- | --- | --- | --- | --- | --- |
1
Fig. 5. CAGRA search performance comparison between the graphs opti- 4
5
mizedbyrank-anddistance-basedreordering.CAGRAperformsrank-based
reorderingwhileCAGRA(distance-based)performsdistance-based.
|     |     |     |     |     |     |     | Fig. 6. Top: | The buffer | layout | used in | the CAGRA | search. | Bottom: The |
| --- | --- | --- | --- | --- | --- | --- | ------------ | ---------- | ------ | ------- | --------- | ------- | ----------- |
algorithmoftheCAGRAsearch.
| 2) Q-A2:    | The            | reordering    | method’s      | advantage         |       | on compute   |              |             |                 |         |     |        |               |
| ----------- | -------------- | ------------- | ------------- | ----------------- | ----- | ------------ | ------------ | ----------- | --------------- | ------- | --- | ------ | ------------- |
|             |                |               |               |                   |       |              |              |             | IV. CAGRASEARCH |         |     |        |               |
| time: In    | the reordering |               | optimization, | we                | avoid | the distance |              |             |                 |         |     |        |               |
|             |                |               |               |                   |       |              | In this      | section,    | we explain      | CAGRA’s |     | search | algorithm and |
| computation | altogether,    | reducing      |               | the computational |       | overhead,    |              |             |                 |         |     |        |               |
|             |                |               |               |                   |       |              | how we       | map it onto | the GPU.        |         |     |        |               |
| and leading | to faster      | optimization. |               | So then,          | how   | does that    |              |             |                 |         |     |        |               |
| improve     | the total      | optimization  |               | time? We          | have  | measured the | A. Algorithm |             |                 |         |     |        |               |
optimizationtime,asshowninFig.4.Therank-basedCAGRA
|              |           |      |                    |     |     |              | The CAGRA         | search | algorithm   |     | uses  | a sequential    | memory |
| ------------ | --------- | ---- | ------------------ | --- | --- | ------------ | ----------------- | ------ | ----------- | --- | ----- | --------------- | ------ |
| optimization | is faster | than | the distance-based |     | for | all datasets |                   |        |             |     |       |                 |        |
|              |           |      |                    |     |     |              | buffer consisting | of     | an internal |     | top-M | list (typically | known  |
1.9×.
| by as much | as  | Furthermore, |     | while | we were | still able |     |     |     |     |     |     |     |
| ---------- | --- | ------------ | --- | ----- | ------- | ---------- | --- | --- | --- | --- | --- | --- | --- |
asapriorityqueueinotheralgorithms)anditscandidatelist,
| to perform     | the rank-based |      | optimization, |            | we experienced | an      |               |            |         |           |           |              |               |
| -------------- | -------------- | ---- | ------------- | ---------- | -------------- | ------- | ------------- | ---------- | ------- | --------- | --------- | ------------ | ------------- |
|                |                |      |               |            |                |         | as shown      | at the top | of Fig. | 6. The    | length    | of the       | internal top- |
| out-of-memory  | error          | that | prevented     | us from    | performing     | the     |               |            |         |           |           |              |               |
|                |                |      |               |            |                |         | M list is     | M(≥ k),    | and the | candidate |           | list is p×d, | where p       |
| distance-based | optimization   |      | on            | DEEP-100M. | These          | results |               |            |         |           |           |              |               |
|                |                |      |               |            |                |         | is the number | of source  | nodes   | of        | the graph | traversed    | in each       |
showthatrank-basedoptimizationisfasterthandistance-based iteration,anddisthedegreeoftheCAGRAgraph.Eachbuffer
| and supports | larger | datasets. |     |     |     |     |         |                |      |            |     |        |               |
| ------------ | ------ | --------- | --- | --- | --- | --- | ------- | -------------- | ---- | ---------- | --- | ------ | ------------- |
|              |        |           |     |     |     |     | element | is a key/value | pair | containing |     | a node | index and the |
3) Q-A3:Seachperformancecomparisontodistance-based corresponding distance between the node and the query.
AsshownatthebottomofFig.6,Thesearchcalculationis
| optimization: | The       | recall     | that a | graph can | potentially | achieve     |             |     |     |     |     |     |     |
| ------------- | --------- | ---------- | ------ | --------- | ----------- | ----------- | ----------- | --- | --- | --- | --- | --- | --- |
| and the       | number of | iterations | to     | obtain a  | specific    | recall will | as follows: |     |     |     |     |     |     |
vary by the graph construction methods, including the re- 0 Random sampling(initializationstep):Wechoosep×d
| ordering | priority | criteria | in the | CAGRA | graph | optimization. |           |        |      |         |       |                 |     |
| -------- | -------- | -------- | ------ | ----- | ----- | ------------- | --------- | ------ | ---- | ------- | ----- | --------------- | --- |
|          |          |          |        |       |       |               | uniformly | random | node | indices | using | a pseudo-random |     |
In CAGRA, we reduce the graph optimization time, avoiding numbergeneratorandcomputethedistancebetweeneach
distance computation and instead using rank as the priority nodeandthequery.Theresultsarestoredinthecandidate
criteria. So then, does the CAGRA graph have the compatible list. We set the internal top-M list with dummy entries
searchperformancecomparedtodistance-basedoptimization?
|     |     |     |     |     |     |     | where | the distance | values |     | are large | enough | to be the |
| --- | --- | --- | --- | --- | --- | --- | ----- | ------------ | ------ | --- | --------- | ------ | --------- |
To answer this question, we have tested both rank-based and last in the next 1 sorting process. For instance, if the
distance-based reordering during CAGRA graph optimization distance is stored in float data type, FLT_MAX.
and measured the throughput and recall of a query search 1 Internal top-M list update: We pick up top-M nodes
processusingthegraph,asshowninFig.5.Thisconfirmsthe
|     |     |     |     |     |     |     | with | the smallest | distance | in  | the entire | buffer | and store |
| --- | --- | --- | --- | --- | --- | --- | ---- | ------------ | -------- | --- | ---------- | ------ | --------- |
top-M
recall-throughput balance is almost the same while the rank- the results in the internal list.
based graph construction time is shorter, as demonstrated in 2 Candidate list index update (graph traversal step): We
| Q-A2. |     |     |     |     |     |     | pick | up all neighbor |     | indices | of the | top-p | nodes in the |
| ----- | --- | --- | --- | --- | --- | --- | ---- | --------------- | --- | ------- | ------ | ----- | ------------ |
4241
Authorized licensed use limited to: The University of Toronto. Downloaded on August 02,2026 at 23:31:31 UTC from IEEE Xplore.  Restrictions apply.

internal top-M list where they have not been parents. we can reduce the computation compared to the full top-M
The result node indices are stored in the candidate list. computation to the buffer. More specifically, we first sort the
top-M
This step does not calculate the distance between each candidate buffer and merge it with the internal buffer
node in the candidate list and the query. throughthemergeprocessofthebitonicsort[11].Weusethe
3 Distance calculation:Wecalculatethedistancebetween single warp-level bitonic sort when the candidate buffer size
each node in the candidate list and the query only if this is less or equal to 512, while we use a radix-based sort using
is the node’s first time being in the candidate list for within a single CTA when it is larger than 512. This design
the query. This conditional branch prunes unnecessary is based on the observation that when the candidate buffer is
computationssincedistancesdon’tneedtoberecomputed smallenough,wecanquicklysortthecandidatelistrightinthe
iftheywerealreadycomputedinapreviousiteration.For registersofasinglewarpwithoutthesharedmemoryfootprint,
instance, if a node has already been in the list and the while we need to use the shared memory when the list length
distance is is large, resulting in a performance degradation compared to
|     |         |        |         | top-M  |            |           | the | radix-based | sort. |     |     |     |     |
| --- | ------- | ------ | ------- | ------ | ---------- | --------- | --- | ----------- | ----- | --- | --- | --- | --- |
|     | • small | enough | to stay | in the | list, then | it should |     |             |       |     |     |     |     |
already be in the list. 3) Hashtableforvisitednodelistmanagement: In 3 ,we
• largeenoughnottobeinthetop-M list,thenitshould calculate the distance between the query and each node in
not be added again. the candidate list only the first time the node appears in the
|           |     |     |                                        |     |     |     | list. | This requires | a   | mechanism | for recording | whether | a node |
| --------- | --- | --- | -------------------------------------- | --- | --- | --- | ----- | ------------- | --- | --------- | ------------- | ------- | ------ |
| Weprocess |     | 1 ∼ | 3 iterativelyuntiltheindexnumbersinthe |     |     |     |       |               |     |           |               |         |        |
top-M listconverge,meaningtheyremainunchangedfromthe has been in the list before and, in a similar manner to the
|          |            |              |               |          | top-k       |        | SONG      | algorithm | [33],        | we    | use an open addressing |            | hash table |
| -------- | ---------- | ------------ | ------------- | -------- | ----------- | ------ | --------- | --------- | ------------ | ----- | ---------------------- | ---------- | ---------- |
| previous | iteration. |              | Finally, we   | output   | the entries | of the |           |           |              |       |                        |            |            |
|          | top-M      |              |               |          |             |        | to manage |           | the visited  | node  | list in the CAGRA      | search.    |            |
| internal |            | list         | as the result | of ANNS. |             |        |           |           |              |       |                        |            |            |
|          |            |              |               |          |             |        | The       | number    | of potential |       | entries in the         | hash table | is calcu-  |
| B.       | Elemental  | technologies | and           | designs  |             |        |           | I         | ×p×d,        |       | I                      |            |            |
|          |            |              |               |          |             |        | lated     | as max    |              | where | max represents         | the        | maximum    |
Thissectionexplainstheelementaltechnologiesanddesigns number of search iterations. We set the hash table size to
we use in the CAGRA search implementation on GPU. at least twice this value to reduce the likelihood of hash
| 1)  | Warp | splitting: | As described |     | in Sec. II-B1, | a warp | collisions. |     |     |     |     |     |     |
| --- | ---- | ---------- | ------------ | --- | -------------- | ------ | ----------- | --- | --- | --- | --- | --- | --- |
consistsof32threadsthatexecutethesameinstructionsimul- Ifweplacethehashtableinlimitedmemory,suchasshared
taneously,representingthesmallestparallelthreadgroupinthe memory, and it exceeds the memory’s capacity, we use a
hardware.IntheCAGRAsearchimplementation,weintroduce smaller hash table with periodic table resetting, meaning the
a software-level division of the warp into even smaller thread hash table evicts previously visited nodes at certain intervals.
groups, referred to as teams. Each team consists of a specific After resetting the table, we only register the nodes present
top-M
number of threads, which we term the team size. in the internal list to the hash table at that moment.
This division allows us to enhance GPU utilization for the Although this process may increase the number of distance
following reasons: Consider the latency of device memory computations, catastrophic recall degradation will not occur,
load,wherea128-bitloadinstructionisthemostefficient.We as mentioned in [33]. We refer to this type of hash table
typicallymaponedistancecomputationtoonewarpandutilize management, which is meant for limited memory and uses
warp shuffle instructions to compute it across the threads table resetting, as forgettable hash table management. We
collaboratively. However, when the dataset dimension is 96, setthenumberofentriesofthehashtableas28 ∼213 andthe
|     |     |     | float |     |     |     |     |     |     |     | ∼   |     |     |
| --- | --- | --- | ----- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
and the data type is (4-byte), the total bit length of reset interval as typically 1 4 depending on the graph and
|     |     |     |     |     |     |     |     |     | M,d, |     | p.  |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ---- | --- | --- | --- | --- |
a dataset vector is 3072 bits, which is smaller than the bit search parameters and This hash table management
length loaded when all 32 threads in a warp issue the 128-bit reducesthesharedmemoryusageperquery,typically≤4kB,
loadinstruction,4096bits.Consequently,thiswillleavesome resultinginhigherparallelefficiencyinalarge-batchqueryon
threads in the warp which do not issue the load instruction, almost all generation of NVIDIA GPUs.
resultingininefficientGPUusage.Nowconsidermappingone 4) 1-bit parented node management: In step 2 , we select
distancecomputationtoateamwithateamsizeof8,andone a specific number of nodes that have not previously been
team can load 1024 bits in one instruction. This allows the parentsandassigntheirneighborindicestothecandidatelist.
entirevectortobeloadedbyrepeatingtheloadingthreetimes To keep track of whether a node has acted as a parent, we
inallthreadsoftheteam.Additionally,theotherteamswithin utilize the Most Significant Bit (MSB) of the index variable
the same warp can calculate the distances between the query in the buffer as a flag for recording this information. An
and the other nodes in the candidate list, thereby maximizing alternative approach could involve using another hash table,
GPU utilization and efficiency. Although we split the warp but we choose not to adopt it due to a latency disadvantage.
into teams in software, we don’t encounter warp divergence We need to search the entry in the hash table if we use the
since all of the teams in each warp still execute the same alternative method, while we can check whether a node has
instructions. actedasaparentjustbyreadingtheMSBofthenodeindexin
|     | Top-M |     |     |     | top-M |     |     |     |     |     |     |     |     |
| --- | ----- | --- | --- | --- | ----- | --- | --- | --- | --- | --- | --- | --- | --- |
2) calculation: In 1 , we obtain distance the list. This method comes with a disadvantage, however, as
entries from the buffer. Since we can assume that the in- itimposesalimitationonthesizeofthedatasetandrestrictsit
dividual internal top-M list parts have already been sorted, tohalfofthemaximumvaluerepresentablebytheindexdata
4242
Authorized licensed use limited to: The University of Toronto. Downloaded on August 02,2026 at 23:31:31 UTC from IEEE Xplore.  Restrictions apply.

TABLEII : Internal top-M
Multi CTA mode
THESUMMARYOFTHEDIFFERENCEBETWEENTHESINGLE-AND
MULTI-CTAMODES.
Single CTA mode
single-CTA multi-CTA
small-batchor 0
Usecase large-batch query batch size
higherrecallisrequired
per1query singleCTA multipleCTA
Fig.7. TheruletochooseasuitableCAGRAsearchimplementation.
Hashtablelocation Sharedmemory Devicememory
Hashtablemanagement Forgettable Standard
offbetweenthroughputenhancementandthepotentialimpact
type. For instance, when the data type used is uint32_t, on recall.
the supported maximum size of the dataset is only 231−1, 2) Multi-CTA implementation: The multi-CTA implemen-
comparedtothemaximumvalueof232−1ifwedidn’tutilize tation is designed to map one query to multiple CTAs, with
a target batch size typically ranging from small values, such
the MSB for this flag.
as 1 ∼ 100. In contrast to the single-CTA implementation,
which launches only as many CTAs as the query batch size,
C. Implementation
the multi-CTA approach maximizes GPU resource utilization
This section explains the features and optimizations of the by employing multiple CTAs to process a single query. As
CAGRA search implementation on the GPU. The CAGRA a result, this implementation achieves higher GPU utilization
search contains separate implementations for single-CTA and and enhances query processing efficiency, even when dealing
multi-CTA.Whilethebasicsearchstrategyandoperationsare with small batch sizes.
the same in both implementations, mapping the hardware to In this implementation, the hash table is stored in device
the queries differs. The summary of these implementations is memory as it needs to be shared with multiple CTAs. Each
shown in Table II. CTA traverses graph nodes, managing its own internal top-M
1) Single-CTA implementation: As the name implies, the listandcandidatelistbysettingthenumberofparentnodesas
single-CTA implementation is designed to efficiently process 1whilesharingthehashtable.Therefore,whilewesearchup
queries by mapping each query to one CTA. The target to p×d nodes in each iteration in single-CTA, we search up
batch size for this implementation ranges from middle to to the number of CTA we launch ×d nodes in each iteration.
large values, such as 100 and above. Leveraging the parallel Since we typically set p = 1 to maximize the throughput
processingcapabilitiesofGPUs,multipleofthesesingle-CTAs of single-CTA, the number of nodes visited in each iteration
can be executed simultaneously, enabling efficient handling in multi-CTA is larger than in single-CTA, leading to higher
of multiple queries and effective GPU resource utilization. recall if the number of iterations is the same.
However, we note that relatively small batch sizes can leave We explored an alternative approach involving graph-
the GPU resources underutilized, leading to suboptimal per- sharding, which is commonly used for multi-node ANNS
formance. computations[11],withthegoalofmaximizingGPUresource
Toimplementthesingle-CTAapproach,wehavedeveloped utilizationforsmallbatchsizes.However,wedecidedagainst
a kernel function that handles the entire search process 0 it for practical reasons that pose challenges to execution
∼ 3 , placing the hash table in shared memory rather than optimizations,suchastherelianceonspecificgraphstructures
device memory. As part of our optimization exploration, we to create the subgraphs, as well as the shuffling and splitting
have also considered an alternative implementation involving of the indices to create sub-datasets of the target dataset.
separate kernel functions, with each function handling a spe- Subsequently, we independently built graphs for each sub-
cificstepofthesearchprocess( 0 ∼ 3 ).However,extensive dataset, similar to the graph construction method used in
testingrevealedthattheoverheadoflaunchingmultiplekernels GGNN[9].Duringthesearchphase,assigningeachsub-graph
outweighs any potential performance gains. As a result, we to a single CTA did result in high GPU resource utilization
have concluded that adopting the multi-kernel approach is when the number of sub-datasets was sufficiently large, how-
not advantageous, and we instead prefer our single-kernel ever, despite its potential advantages, this method presented
implementation. several issues. For example, determining the optimal number
In the throughput analysis of the implementation, we have of splits depends on factors such as the query batch size and
observed that the memory bandwidth of the device memory the hardware configuration, specifically the number of SMs
limits the performance of the kernel function when the query on the GPU. Creating a series of sub-graphs for each batch
batch size and the dimension of the dataset are large. We size and GPU configuration is not feasible in practice, and it
propose an approach involving low-precision data types for makes this approach impractical. Nevertheless, we recognize
dataset vectors to address the memory bandwidth limitations thattheshardingtechniquecouldbewell-suitedforextending
andenhanceoverallthroughput.Byreducingthememoryfoot- graph-based ANNS to a multi-GPU environment, where each
print,thisoptimizationtechniqueaimstoexpeditedatatransfer GPU is assigned to process one sub-graph independently.
between memory and processing units, thereby increasing 3) Implementation choice: As mentioned above, we have
throughput.However,itiscrucialtocarefullyassessthetrade- twoimplementationstargetingsmallandlargebatchsizesand
4243
Authorized licensed use limited to: The University of Toronto. Downloaded on August 02,2026 at 23:31:31 UTC from IEEE Xplore. Restrictions apply.

Fig.8. Searchperformancecomparisonamongdifferentteamsizes. Fig.9. Searchperformancecomparisonbetweentwohashtablemanagement
methods:standardandforgettable.
weselecttheimplementationbasedonboththebatchsizeand
theinternaltop-M
size,asshowninFig.7.Weusethemulti-
CTAimplementationwhenthequerybatchsizeissmallerthan
| a threshold | b or | when | the internal | top-M | size | is larger | than |     |     |     |     |     |     |     |
| ----------- | ---- | ---- | ------------ | ----- | ---- | --------- | ---- | --- | --- | --- | --- | --- | --- | --- |
T
M
| a threshold | T,  | since | the computing |     | cost of | 1 is | large in |     |     |     |     |     |     |     |
| ----------- | --- | ----- | ------------- | --- | ------- | ---- | -------- | --- | --- | --- | --- | --- | --- | --- |
thesingle-CTAimplementationforthesecases,increasingthe
| computing | time.     | When   | the multi-CTA |                 | implementation |     | is not |     |     |     |     |     |     |     |
| --------- | --------- | ------ | ------------- | --------------- | -------------- | --- | ------ | --- | --- | --- | --- | --- | --- | --- |
| used, we  | fall back | to the | single-CTA    | implementation. |                |     | While  |     |     |     |     |     |     |     |
theproperthresholdsdependonthehardware,werecommend
| M       |     | b   |      |           |     |        |      |     |     |     |     |     |     |     |
| ------- | --- | --- | ---- | --------- | --- | ------ | ---- | --- | --- | --- | --- | --- | --- | --- |
| T = 512 | and | T = | “the | number of | SMs | on the | GPU” |     |     |     |     |     |     |     |
empirically.
| D. Evaluation | of      | the CAGRA |               | search implementation |     |     |     |                                                                  |                  |       |                 |       |           |     |
| ------------- | ------- | --------- | ------------- | --------------------- | --- | --- | --- | ---------------------------------------------------------------- | ---------------- | ----- | --------------- | ----- | --------- | --- |
|               |         |           |               |                       |     |     |     | Fig.10. Searchperformancecomparisonbetweensingle-CTAandmulti-CTA |                  |       |                 |       |           |     |
| This section  | reveals |           | the following | question:             |     |     |     |                                                                  |                  |       |                 |       |           |     |
|               |         |           |               |                       |     |     |     | implementations                                                  | for single-query | (top) | and large-batch | query | (bottom). | The |
Q-B1 How much effect does the warp splitting have on the batchsizeinlarge-batchquerysearchis10K.
throughput?
Q-B2 Howmucheffectdoestheforgettablehashhaveonthe
throughput?
|            |       |            |     |           |      |            |     | memory      | when using them | in   | single-CTA | in    | Fig. 9.   | In this |
| ---------- | ----- | ---------- | --- | --------- | ---- | ---------- | --- | ----------- | --------------- | ---- | ---------- | ----- | --------- | ------- |
| Q-B3 Which | cases | single-CTA |     | is faster | than | multi-CTA? |     |             |                 |      |            |       |           |         |
|            |       |            |     |           |      |            |     | experiment, | we reset the    | hash | table for  | every | iteration | in the  |
1) Q-B1: The effect of team size in throughput: We split forgettable hash. In both datasets, DEEP-1M and GloVe, we
| the warp    | into multiple |      | teams          | in software | to efficiently |         | utilize |                |                 |          |       |              |            |      |
| ----------- | ------------- | ---- | -------------- | ----------- | -------------- | ------- | ------- | -------------- | --------------- | -------- | ----- | ------------ | ---------- | ---- |
|             |               |      |                |             |                |         |         | have confirmed | the forgettable |          | hash  | achieves     | compatible | or   |
| the GPU     | resources,    | as   | mentioned      | in Sec.     | IV-B1.         | Then,   | how     |                |                 |          |       |              |            |      |
|             |               |      |                |             |                |         |         | higher search  | throughput      | compared | to    | the standard | hash.      | The  |
| much effect | does          | this | warp splitting | have?       | We             | compare | the     |                |                 |          |       |              |            |      |
|             |               |      |                |             |                |         |         | throughput     | gain observed   | in       | GloVe | is slightly  | smaller    | than |
performance among different team sizes for the DEEP-1M in DEEP-1M. This discrepancy can be attributed to the fact
| and GIST                                             | datasets     | in  | Fig. 8.    | In the    | evaluation | result  | for     |                |                |               |            |                  |         |         |
| ---------------------------------------------------- | ------------ | --- | ---------- | --------- | ---------- | ------- | ------- | -------------- | -------------- | ------------- | ---------- | ---------------- | ------- | ------- |
|                                                      |              |     |            |           |            |         |         | that in GloVe, | the overhead   | of            | hash table | operations       | becomes |         |
| DEEP-1M,                                             | a relatively |     | small      | dimension | dataset,   | we can  | gain    |                |                |               |            |                  |         |         |
|                                                      |              |     |            |           |            |         |         | relatively     | smaller when   | dealing       | with       | larger dimension |         | dataset |
| the highest                                          | performance  |     | when       | the team  | size       | is 4 or | 8 while |                |                |               |            |                  |         |         |
|                                                      |              |     |            |           |            |         |         | vectors,       | as the primary | computational |            | load shifted     |         | towards |
| maintainingrecall.Whentheteamsizeistoosmall,suchas2, |              |     |            |           |            |         |         | distance       | calculations.  |               |            |                  |         |         |
| the number                                           | of registers |     | per thread | becomes   | too        | large,  | leading |                |                |               |            |                  |         |         |
to performance degradation. On the other hand, in the search 3) Q-B3: Search performance comparison between single-
performanceforGIST,arelativelylargedimensiondataset,we andmulti-CTAimplementations: Wehavemeasuredthesearch
|     |     |     |     |     |     |     |     | performance | of the single- | and | multi-CTA | implementations |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ----------- | -------------- | --- | --------- | --------------- | --- | --- |
achievedthehighestperformancewhentheteamsizewas32.
Inthiscase,wecanutilizetheGPUresourcesefficientlyeven for the DEEP-1M and GloVe datasets, as shown in Fig. 10.
if we do not split the warp. Instead, decreasing the team size In the context of a single query, the multi-CTA approach
causes significant performance degradation due to increased outperforms the single-CTA approach for both the DEEP-
|     |     |     |     |     |     |     |     | 1M and | GloVe datasets. | However, | in  | a large-batch | query, | we  |
| --- | --- | --- | --- | --- | --- | --- | --- | ------ | --------------- | -------- | --- | ------------- | ------ | --- |
register usage.
2) Q-B2: The effect of forgettable hash table management observe divergent outcomes. For the DEEP-1M dataset, the
in throughput: When we place the hash table in shared single-CTAmethoddemonstratessuperiorsearchperformance.
memory, we use the forgettable hash table management, a On the other hand, in the case of GloVe, if a higher recall
small-size hash table that is reset periodically, instead of is required, the multi-CTA method achieves better results.
the standard hash table in device memory, as mentioned in This discrepancy can be attributed to the nature of the GloVe
Sec. IV-B3. Then, how much faster is the forgettable hash dataset, which is considered to be “harder” than DEEP-1M
on shared memory than the standard one on the device [16].AchievinghigherrecallontheGloVedatasetnecessitates
memory,andhowmuchrecallisreducedbytheperiodicreset? searching through more nodes, in other words, increasing
top-M,
We compare the search performance between the forgettable internal which is a requirement that the multi-CTA
hash in shared memory and the standard hash in device approach fulfills effectively.
4244
Authorized licensed use limited to: The University of Toronto. Downloaded on August 02,2026 at 23:31:31 UTC from IEEE Xplore.  Restrictions apply.

|     |     |     |     |     |     |     | Fig. 12. | The search | performance | comparison |     | between graphs | created | by  |
| --- | --- | --- | --- | --- | --- | --- | -------- | ---------- | ----------- | ---------- | --- | -------------- | ------- | --- |
Fig. 11. Graph construction time comparison among CAGRA and other CAGRAandNSSGusingNSSGsingle-threadedsearchimplementation.
graph-basedANNSimplementations.
|     |     |     |             |     |     |     | B. Q-C2:    | Graph | search     | quality |        |        |            |     |
| --- | --- | --- | ----------- | --- | --- | --- | ----------- | ----- | ---------- | ------- | ------ | ------ | ---------- | --- |
|     |     | V.  | EXPERIMENTS |     |     |     |             |       |            |         |        |        |            |     |
|     |     |     |             |     |     |     | To evaluate |       | the search | quality | of the | graph, | we compare |     |
We compare CAGRA with the following graph-based the search performance of the CAGRA graph to the NSSG
ANNS implementations: graph using the NSSG search implementation in both graphs.
1) GGNN [9]: One of the current state-of-the-art GPU To do so, we load the CAGRA graph into NSSG and use
implementation candidates. NSSGsearchtofindnearestneighbors.Usingthesamesearch
|                |       |             |        |                          |     |     | implementation |             | with different |             | graphs | allows us       | to directly |      |
| -------------- | ----- | ----------- | ------ | ------------------------ | --- | --- | -------------- | ----------- | -------------- | ----------- | ------ | --------------- | ----------- | ---- |
| 2) GANNS       | [32]: | One         | of the | current state-of-the-art |     | GPU |                |             |                |             |        |                 |             |      |
|                |       |             |        |                          |     |     | compare        | the quality | of             | the graphs. | Fig.   | 12 demonstrates |             | that |
| implementation |       | candidates. |        |                          |     |     |                |             |                |             |        |                 |             |      |
3) HNSW[18]:Well-knownstate-of-the-artimplementation whileakNNgraphresultsinlowsearchaccuracy,theCAGRA
and proximity graph for CPU. and NSG graphs show comparable performance. Although
|              |      |                   |         |           |        |           | many graphs           | have | high | performance, | we        | use NSSG  | since | its  |
| ------------ | ---- | ----------------- | ------- | --------- | ------ | --------- | --------------------- | ---- | ---- | ------------ | --------- | --------- | ----- | ---- |
| 4) NSSG      | [7]: | An implementation |         | with      | search | and graph |                       |      |      |              |           |           |       |      |
|              |      |                   |         |           |        |           | search implementation |      |      | is similar   | to CAGRA, | including |       | that |
| construction |      | processes         | similar | to CAGRA. |        | NSSG also |                       |      |      |              |           |           |       |      |
starts the search process with random sampling. thesearchprocessstartsfromtherandomsampling,andithas
betterorcompatiblesearchperformancecomparedtomostof
| While the  | out-degree   | of         | the CAGRA             | graph         | is         | fixed, it is |                    |       |          |        |                 |                       |               |     |
| ---------- | ------------ | ---------- | --------------------- | ------------- | ---------- | ------------ | ------------------ | ----- | -------- | ------ | --------------- | --------------------- | ------------- | --- |
|            |              |            |                       |               |            |              | them [29].         | If we | were     | to use | another         | search implementation |               |     |
| not fixed  | for the      | other      | four implementations. |               | Therefore, | we           |                    |       |          |        |                 |                       |               |     |
|            |              |            |                       |               |            |              | unsuitable         | for   | CAGRA,   | for    | instance,       | HNSW                  | or NSG,       | the |
| align the  | average      | out-degree | for                   | each dataset  | to         | make the     |                    |       |          |        |                 |                       |               |     |
|            |              |            |                       |               |            |              | search performance |       | would    | be     | disadvantageous | to                    | CAGRA.        | In  |
| comparison | between      | them       | as fair               | as possible.  |            |              |                    |       |          |        |                 |                       |               |     |
|            |              |            |                       |               |            |              | this evaluation,   |       | we first | build  | an NSSG         | graph                 | and calculate |     |
| In the     | experiments, | we         | answer                | the following | questions: |              |                    |       |          |        |                 |                       |               |     |
theaverageout-degreeofthegraph.Then,webuildaCAGRA
Q-C1 How fast is the CAGRA graph construction? graphforthedatasetsettingtheout-degreeasthelargestvalue
| Q-C2 How | comparable |     | is the search | quality | of the | CAGRA |           |          |        |         |            |     |           |     |
| -------- | ---------- | --- | ------------- | ------- | ------ | ----- | --------- | -------- | ------ | ------- | ---------- | --- | --------- | --- |
|          |            |     |               |         |        |       | less than | or equal | to the | average | out-degree | in  | multiples | of  |
graph?
|     |     |     |     |     |     |     | 16. The | comparison | of  | search | performance | is shown |     | in Fig. |
| --- | --- | --- | --- | --- | --- | --- | ------- | ---------- | --- | ------ | ----------- | -------- | --- | ------- |
Q-C3 How much better is the CAGRA search performance 12, and the results indicate that the search performance of
in batch processing? the CAGRA graph is almost at the same level as that of
| Q-C4 How | much   | better      | is the | CAGRA search | performance |     |            |              |        |      |                |       |          |     |
| -------- | ------ | ----------- | ------ | ------------ | ----------- | --- | ---------- | ------------ | ------ | ---- | -------------- | ----- | -------- | --- |
|          |        |             |        |              |             |     | the NSSG   | graph        | across | all  | four datasets. | In    | summary, | the |
| in       | online | processing? |        |              |             |     |            |              |        |      |                |       |          |     |
|          |        |             |        |              |             |     | evaluation | demonstrates |        | that | the CAGRA      | graph | achieves | a   |
Q-C5 Does CAGRA support large datasets? search performance comparable to the NSSG graph, which
|            |       |              |              |      |          |         | is one of | the highest-performance |                |     | graphs         | for ANNS. |       |        |
| ---------- | ----- | ------------ | ------------ | ---- | -------- | ------- | --------- | ----------------------- | -------------- | --- | -------------- | --------- | ----- | ------ |
| A. Q-C1:   | Graph | construction | time         |      |          |         |           |                         |                |     |                |           |       |        |
|            |       |              |              |      |          |         | C. Q-C3:  | Recall                  | and throughput |     | in large-batch |           | query | search |
| The result | of    | the graph    | construction | time | is shown | in Fig. |           |                         |                |     |                |           |       |        |
11.Wemeasuredtheentiregraphconstructiontime,including In the batch processing use of ANNS, large-batch search
memory allocation, dataset file load, and data movement. performanceiscrucial.ThisusecaseissuitableforGPUsince
NSSGfirstbuildsak-NNgraphexplicitlyandthenoptimizes
itiseasytoextractparallelism,andthismakesthebestuseof
itsimilarlytoCAGRA,whereasGGNN,GANNS,andHNSW the single-CTA implementation in CAGRA. Then, How fast
donot.Therefore,inthecaseofCAGRAandNSSG,weshow is CAGRA compared to other ANNS GPU implementations
k-NN
the breakdown of the initial graph build and its opti- and the state-of-the-art CPU implementation in large-batch
mizationtime,whiletheothersareonlytheentireconstruction search? We have compared the recall and throughput among
time.CAGRAiscompatiblewithorfasterthantheotherCPU CAGRA and the other methods, as shown in Fig. 13. Since
andGPUimplementations.Incomparingimplementationsfor thesearchimplementationofNSSGisnotmulti-threaded,and
|     |     | 1.1–31× |     |     |     | 1.0–6.1× |     |     |     |     |     |     |     |     |
| --- | --- | ------- | --- | --- | --- | -------- | --- | --- | --- | --- | --- | --- | --- | --- |
GPU, CAGRA is faster than GGNN, and using it would not be a fair comparison, we measured the
2.2–27×
than GANNS. And it is faster than HNSW. performance of NSSG using the search implementation for
4245
Authorized licensed use limited to: The University of Toronto. Downloaded on August 02,2026 at 23:31:31 UTC from IEEE Xplore.  Restrictions apply.

Fig.15. GraphconstructiontimecomparisonbetweenCAGRAandHNSW
forDEEP-1M,10M,and100Mdatasets.
| Fig. 13. Large-batch | search performance | comparison | among CAGRA and |     |     |     |     |     |     |     |
| -------------------- | ------------------ | ---------- | --------------- | --- | --- | --- | --- | --- | --- | --- |
othergraph-basedANNSimplementations(batchsize=10K).CAGRA(FP32)
indicatesthatthedatasetisstoredinFP32,whileCAGRA(FP16)isconverted
toFP16.
Fig.16. SearchperformancecomparisonbetweenCAGRAandHNSWfor
|     |     |     |     | DEEP-1M, | 10M, and | 100M | datasets | in recall@10 | (top) | and recall@100 |
| --- | --- | --- | --- | -------- | -------- | ---- | -------- | ------------ | ----- | -------------- |
(bottom).Thebatchsizeis10K.
|     |     |     |     | D. Q-C4:    | Recall      | and throughput |                | in single-query |                | search       |
| --- | --- | --- | --- | ----------- | ----------- | -------------- | -------------- | --------------- | -------------- | ------------ |
|     |     |     |     | In the      | online      | processing     | use            | of ANNS,        | single-query   | per-         |
|     |     |     |     | formance    | is crucial. | In             | this use       | case, an        | implementation | for          |
|     |     |     |     | multi-batch | processing  |                | on GPU         | is typically    | unsuitable     | since        |
|     |     |     |     | it can not  | efficiently | utilize        | the            | GPU resources.  |                | In CAGRA,    |
|     |     |     |     | we propose  | the         | multi-CTA      | implementation |                 | to             | address this |
inefficiency.Then,HowfastisCAGRAcomparedtotheother
fastANNSimplementationsforCPUinsingle-query?Wehave
|     |     |     |     | compared | the recall | and     | throughput | of          | CAGRA | to the other |
| --- | --- | --- | --- | -------- | ---------- | ------- | ---------- | ----------- | ----- | ------------ |
|     |     |     |     | methods, | as shown   | in Fig. | 14.        | Our results | show  | that CAGRA   |
hasa3.4–53×highersearchperformancethanHNSWat95%
Fig.14. Single-querysearch performancecomparisonamongCAGRAand recall. Since the GGNN and GANNS methods are optimized
othergraph-basedANNSimplementations.CAGRA(FP32)indicatesthatthe
datasetisstoredinsingle-precisionFP32,whileCAGRA(FP16)isconverted for large-batch queries, their single-query throughputs are
tohalf-precisionFP16. much slower than even HNSW and NSSG on CPU. While
|            |              |                |                 | the performance |        | of CAGRA | (FP16) | and           | CAGRA   | (FP32) in  |
| ---------- | ------------ | -------------- | --------------- | --------------- | ------ | -------- | ------ | ------------- | ------- | ---------- |
|            |              |                |                 | SIFT, GloVe,    | and    | NYTimes  | are    | very similar, | CAGRA   | (FP16)     |
|            |              |                |                 | is slightly     | better | in GIST. | This   | discrepancy   | is from | the larger |
| the bottom | layer of the | HNSW graph. In | the performance |                 |        |          |        |               |         |            |
dimensionalityofGISTcomparedtotheotherdatasets,which
| measurement | of HNSW        | and NSSG, we          | have tried multiple |              |        |              |     |         |              |     |
| ----------- | -------------- | --------------------- | ------------------- | ------------ | ------ | ------------ | --- | ------- | ------------ | --- |
|             |                |                       |                     | require more | memory | bandwidth    |     | to load | the dataset. |     |
| OpenMP      | thread counts, | up to 64, and plotted | the fastest of      |              |        |              |     |         |              |     |
|             |                |                       |                     | E. Q-C5:     | Large  | size dataset |     |         |              |     |
| them. The   | results show   | that the performance  | of CAGRA is         |              |        |              |     |         |              |     |
higherthantheotherANNSmethodsonbothCPUandGPU. In recent years, the query operations for larger and larger
Inthe90%to95%recallrange,ourmethodis33–77×faster datasetsareattractingattention[26].So,doesCAGRAsupport
thanHNSWandis3.8–8.8×fasterthantheotherGPUimple-
|     |     |     |     | large datasets?, |     | and how | do larger | datasets | affect | CAGRA’s |
| --- | --- | --- | --- | ---------------- | --- | ------- | --------- | -------- | ------ | ------- |
mentations. Since the memory bandwidth of the device limits searchperformance?Wemeasuredthegraphconstructionand
the throughput of CAGRA, we can gain higher throughput search performance of CAGRA in the DEEP-1M, 10M, and
using half-precision (FP16) in dataset vector data type. We 100M datasets, as shown in Fig. 15 and Fig. 16. The graph
demonstrate that half-precision does not degrade the quality construction time increases proportionally with the dataset
of results while still benefitting from higher throughput. size.Duringthesearchperformancecomparisons,weobserve
4246
Authorized licensed use limited to: The University of Toronto. Downloaded on August 02,2026 at 23:31:31 UTC from IEEE Xplore.  Restrictions apply.

thatasthedatasetsizegrows,CAGRA’srecalldeclinesslightly [12] Herve Je´gou, Matthijs Douze, and Cordelia Schmid. Product Quan-
|             |           |       |         |     |                 |     | tization | for Nearest | Neighbor |     | Search. | IEEE Transactions | on  | Pattern |
| ----------- | --------- | ----- | ------- | --- | --------------- | --- | -------- | ----------- | -------- | --- | ------- | ----------------- | --- | ------- |
| but follows | a similar | trend | to HNSW | and | the degradation | in  |          |             |          |     |         |                   |     |         |
AnalysisandMachineIntelligence,January2011.
| both recall | and | throughput | is not | significant. | Based | on our |             |        |          |        |          |            |        |        |
| ----------- | --- | ---------- | ------ | ------------ | ----- | ------ | ----------- | ------ | -------- | ------ | -------- | ---------- | ------ | ------ |
|             |     |            |        |              |       |        | [13] Tanaka | Kanji, | Chokushi | Yuuto, | and Ando | Masatoshi. | Mining | visual |
findings,webelievethatCAGRAremainscapableofhandling
|     |     |     |     |     |     |     | phrases | for long-term |     | visual SLAM. | In  | 2014 IEEE/RSJ | International |     |
| --- | --- | --- | --- | --- | --- | --- | ------- | ------------- | --- | ------------ | --- | ------------- | ------------- | --- |
ConferenceonIntelligentRobotsandSystems,September2014.
| larger datasets | while | maintaining |     | this trend | unless | the dataset |     |     |     |     |     |     |     |     |
| --------------- | ----- | ----------- | --- | ---------- | ------ | ----------- | --- | --- | --- | --- | --- | --- | --- | --- |
[14] UrvashiKhandelwal,OmerLevy,DanJurafsky,LukeZettlemoyer,and
| exceeds | the device | memory | capacity. | In  | these cases, | a multi- |      |        |                |         |               |     |         |          |
| ------- | ---------- | ------ | --------- | --- | ------------ | -------- | ---- | ------ | -------------- | ------- | ------------- | --- | ------- | -------- |
|         |            |        |           |     |              |          | Mike | Lewis. | Generalization | through | Memorization: |     | Nearest | Neighbor |
GPUshardingtechnique[6]discussedinSec.IV-C2anddata LanguageModels. 2020.
compression schemes, such as product quantization, are some [15] PingLi,WeijieZhao,ChaoWang,QiXia,AliceWu,andLijunPeng.
PracticewithGraph-basedANNAlgorithmsonSparseData:Chi-square
of the ways to address the memory capacity problem, though Two-towermodel,HNSW,SignCauchyProjections,June2023.
further performance investigation is required. [16] WenLi,YingZhang,YifangSun,WeiWang,MingjieLi,WenjieZhang,
|     |     |     |            |     |     |     | and                                                  | Xuemin | Lin. Approximate |     | Nearest | Neighbor | Search | on High |
| --- | --- | --- | ---------- | --- | --- | --- | ---------------------------------------------------- | ------ | ---------------- | --- | ------- | -------- | ------ | ------- |
|     |     |     |            |     |     |     | DimensionalData—Experiments,Analyses,andImprovement. |        |                  |     |         |          |        | IEEE    |
|     |     | VI. | CONCLUSION |     |     |     |                                                      |        |                  |     |         |          |        |         |
TransactionsonKnowledgeandDataEngineering,August2020.
[17] TingLiu,CharlesRosenberg,andHenryA.Rowley.ClusteringBillions
In this paper, we proposed a fast graph-based ANNS of Images with Large Scale Nearest Neighbor Search. In 2007 IEEE
method called CAGRA, which is designed to perform well Workshop on Applications of Computer Vision (WACV ’07), February
| on NVIDIA | GPUs | by harnessing |     | their | increased | computing | 2007. |     |     |     |     |     |     |     |
| --------- | ---- | ------------- | --- | ----- | --------- | --------- | ----- | --- | --- | --- | --- | --- | --- | --- |
capacity and superior memory bandwidth. CAGRA performs [18] Yu A. Malkov and D. A. Yashunin. Efficient and robust approximate
|     |     |     |     |     |     |     | nearest | neighbor | search | using | Hierarchical | Navigable | Small | World |
| --- | --- | --- | --- | --- | --- | --- | ------- | -------- | ------ | ----- | ------------ | --------- | ----- | ----- |
k-NN
a heuristic optimization to the initial graph to improve graphs. arXiv:1603.09320[cs],August2018. arXiv:1603.09320.
the reachability from each node to other nodes with a highly [19] YuryMalkov,AlexanderPonomarenko,AndreyLogvinov,andVladimir
|                    |                      |      |            |                  |       |             | Krylov.           | Approximate |                                   | nearest | neighbor | algorithm | based on | navigable |
| ------------------ | -------------------- | ---- | ---------- | ---------------- | ----- | ----------- | ----------------- | ----------- | --------------------------------- | ------- | -------- | --------- | -------- | --------- |
| parallel           | computation-friendly |      | algorithm. |                  | CAGRA | has better  |                   |             |                                   |         |          |           |          |           |
|                    |                      |      |            |                  |       |             | smallworldgraphs. |             | InformationSystems,September2014. |         |          |           |          |           |
| search performance |                      | than | other      | state-of-the-art |       | graph-based |                   |             |                                   |         |          |           |          |           |
[20] CoreyJ.Nolet,DivyeGala,AlexFender,MaheshDoijade,JoeEaton,
|     |     |     |     |     |     |     | Edward | Raff, | John Zedlewski, |     | Brad Rees, | and Tim | Oates. cuSLINK: |     |
| --- | --- | --- | --- | --- | --- | --- | ------ | ----- | --------------- | --- | ---------- | ------- | --------------- | --- |
ANNSimplementationsonbothCPUandGPUforbothlarge-
Single-linkageAgglomerativeClusteringontheGPU,June2023.
| batch and | single | queries. | CAGRA | is available |     | in the open- |            |           |       |       |        |           |             |       |
| --------- | ------ | -------- | ----- | ------------ | --- | ------------ | ---------- | --------- | ----- | ----- | ------ | --------- | ----------- | ----- |
|           |        |          |       |              |     |              | [21] Corey | J. Nolet, | Divye | Gala, | Edward | Raff, Joe | Eaton, Brad | Rees, |
source NVIDIA RAPIDS RAFT library, which can be found JohnZedlewski,andTimOates. GPUSemiringPrimitivesforSparse
on GitHub (https://github.com/rapidsai/raft). Neighborhood Methods. In Proceedings of Machine Learning and
Systems,pages95–109,2022.
[22] CoreyJ.Nolet,VictorLafargue,EdwardRaff,ThejaswiNanditale,Tim
REFERENCES Oates,JohnZedlewski,andJoshuaPatterson. BringingUMAPCloser
totheSpeedofLightwithGPUAcceleration.ProceedingsoftheAAAI
[1] Martin Aumu¨ller, Erik Bernhardsson, and Alexander Faithfull. ANN- ConferenceonArtificialIntelligence,May2021.
Benchmarks: A benchmarking tool for approximate nearest neighbor [23] NVIDIA. CUDAC++ProgrammingGuide. 2023.
algorithms. InformationSystems,January2020. [24] JeffreyPennington,RichardSocher,andChristopherManning. GloVe:
[2] NandanBanerjee,RyanC.Connolly,DimitriLisin,JimmyBriggs,and Global Vectors for Word Representation. In Proceedings of the 2014
MarioE.Munich. Viewmanagementforlifelongvisualmaps. In2019 Conference on Empirical Methods in Natural Language Processing
| IEEE/RSJ | International | Conference |     | on Intelligent | Robots | and Systems | (EMNLP),October2014. |     |     |     |     |     |     |     |
| -------- | ------------- | ---------- | --- | -------------- | ------ | ----------- | -------------------- | --- | --- | --- | --- | --- | --- | --- |
(IROS),November2019. [25] ChanopSilpa-AnanandRichardHartley. OptimisedKD-treesforfast
[3] Rihan Chen, Bin Liu, Han Zhu, Yaoxuan Wang, Qi Li, Buting Ma, image descriptor matching. In 2008 IEEE Conference on Computer
Qingbo Hua, Jun Jiang, Yunlong Xu, Hongbo Deng, and Bo Zheng. VisionandPatternRecognition,June2008.
ApproximateNearestNeighborSearchunderNeuralSimilarityMetric [26] HarshaVardhanSimhadri,GeorgeWilliams,MartinAumu¨ller,Matthijs
for Large-Scale Recommendation. In Proceedings of the 31st ACM Douze,ArtemBabenko,DmitryBaranchuk,QiChen,LucasHosseini,
International Conference on Information & Knowledge Management, Ravishankar Krishnaswamy, Gopal Srinivasa, Suhas Jayaram Subra-
October2022. manya, and Jingdong Wang. Results of the NeurIPS’21 Challenge
|           |               |            |       |        |           |              | on Billion-Scale |     | Approximate |     | Nearest | Neighbor | Search, May | 2022. |
| --------- | ------------- | ---------- | ----- | ------ | --------- | ------------ | ---------------- | --- | ----------- | --- | ------- | -------- | ----------- | ----- |
| [4] Mayur | Datar, Nicole | Immorlica, | Piotr | Indyk, | and Vahab | S. Mirrokni. |                  |     |             |     |         |          |             |       |
Locality-sensitive hashing scheme based on p-stable distributions. In Number:arXiv:2205.03763[cs].
Proceedings of the twentieth annual symposium on Computational [27] Jeffrey Travers and Stanley Milgram. An Experimental Study of the
|     |     |     |     |     |     |     | SmallWorldProblem. |     |     | Sociometry,December1969. |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------------------ | --- | --- | ------------------------ | --- | --- | --- | --- |
geometry,June2004.
[5] Wei Dong, Charikar Moses, and Kai Li. Efficient k-nearest neighbor [28] HuiWang,Wan-LeiZhao,XiangxiangZeng,andJianyeYang. Fastk-
graph construction for generic similarity measures. In Proceedings of NNGraphConstructionbyGPUbasedNN-Descent. InProceedingsof
the20thinternationalconferenceonWorldwideweb,March2011. the 30th ACM International Conference on Information & Knowledge
[6] Ishita Doshi, Dhritiman Das, Ashish Bhutani, Rajeev Kumar, Rushi Management,October2021.
Bhatt, and Niranjan Balasubramanian. LANNS: a web-scale approx- [29] Mengzhao Wang, Xiaoliang Xu, Qiang Yue, and Yuxiang Wang. A
imatenearestneighborlookupsystem,December2021. ComprehensiveSurveyandExperimentalComparisonofGraph-Based
|                                                                |     |     |     |                           |     |     | Approximate |                   | Nearest | Neighbor | Search. | arXiv:2101.12631 | [cs], | May |
| -------------------------------------------------------------- | --- | --- | --- | ------------------------- | --- | --- | ----------- | ----------------- | ------- | -------- | ------- | ---------------- | ----- | --- |
| [7] CongFu,ChangxuWang,andDengCai.                             |     |     |     | HighDimensionalSimilarity |     |     |             |                   |         |          |         |                  |       |     |
| SearchWithSatelliteSystemGraph:Efficiency,Scalability,andUnin- |     |     |     |                           |     |     | 2021.       | arXiv:2101.12631. |         |          |         |                  |       |     |
dexedQueryCompatibility.IEEETransactionsonPatternAnalysisand [30] FrankF.Xu,UriAlon,andGrahamNeubig.WhydoNearestNeighbor
|     |     |     |     |     |     |     | LanguageModelsWork?,January2023. |     |     |     |     | arXiv:2301.02828[cs]. |     |     |
| --- | --- | --- | --- | --- | --- | --- | -------------------------------- | --- | --- | --- | --- | --------------------- | --- | --- |
MachineIntelligence,pages4139–4150,August2022.
[8] Cong Fu, Chao Xiang, Changxu Wang, and Deng Cai. Fast approxi- [31] Artem Babenko Yandex and Victor Lempitsky. Efficient Indexing of
matenearestneighborsearchwiththenavigatingspreading-outgraph. Billion-ScaleDatasetsofDeepDescriptors. In2016IEEEConference
onComputerVisionandPatternRecognition(CVPR),June2016.
ProceedingsoftheVLDBEndowment,pages461–474,2019.
|     |     |     |     |     |     |     | [32] Yuanhang | Yu, | Dong | Wen, Ying | Zhang, | Lu Qin, | Wenjie Zhang, | and |
| --- | --- | --- | --- | --- | --- | --- | ------------- | --- | ---- | --------- | ------ | ------- | ------------- | --- |
[9] FabianGroh,LukasRuppert,PatrickWieschollek,andHendrikLensch.
GGNN:Graph-basedGPUNearestNeighborSearch.IEEETransactions Xuemin Lin. GPU-accelerated Proximity Graph Approximate Nearest
|     |     |     |     |     |     |     | Neighbor | Search | and | Construction. | In  | 2022 IEEE | 38th International |     |
| --- | --- | --- | --- | --- | --- | --- | -------- | ------ | --- | ------------- | --- | --------- | ------------------ | --- |
onBigData,2022.
ConferenceonDataEngineering(ICDE),May2022.
| [10] Masajiro | Iwasaki | and Daisuke | Miyazaki. |     | Optimization | of Indexing |     |     |     |     |     |     |     |     |
| ------------- | ------- | ----------- | --------- | --- | ------------ | ----------- | --- | --- | --- | --- | --- | --- | --- | --- |
Based on k-Nearest Neighbor Graph for Proximity Search in High- [33] WeijieZhao,ShulongTan,andPingLi. SONG:ApproximateNearest
NeighborSearchonGPU.In2020IEEE36thInternationalConference
| dimensionalData,October2018. |     |     | arXiv:1810.07355[cs]. |     |     |     |     |     |     |     |     |     |     |     |
| ---------------------------- | --- | --- | --------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
onDataEngineering(ICDE),April2020.
[11] JeffJohnson,MatthijsDouze,andHerveJegou.Billion-ScaleSimilarity
| SearchwithGPUs. |     | IEEETransactionsonBigData,July2021. |     |     |     |     |     |     |     |     |     |     |     |     |
| --------------- | --- | ----------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
4247
Authorized licensed use limited to: The University of Toronto. Downloaded on August 02,2026 at 23:31:31 UTC from IEEE Xplore.  Restrictions apply.