# Legend

**Source**: Legend.pdf
**Format**: .pdf

---

| The VLDB    | Journal         | manuscript  | No. |     |        |            |     |     |
| ----------- | --------------- | ----------- | --- | --- | ------ | ---------- | --- | --- |
| (will be    | inserted by the | editor)     |     |     |        |            |     |     |
| Efficient   | Graph           | Embedding   |     | at  | Scale: | Optimizing |     |     |
| CPU-GPU-SSD |                 | Integration |     |     |        |            |     |     |
Zhonggen Li · Xiangyu Ke · Yifan Zhu · Yunjun Gao · Feifei Li
6202 raM 21  ]CD.sc[  3v85290.5052:viXra
Received:date/Accepted:date
| Abstract        | Graphembeddingsmapgraphnodestocon- |              |              |     | 1 Introduction |     |     |     |
| --------------- | ---------------------------------- | ------------ | ------------ | --- | -------------- | --- | --- | --- |
| tinuous vectors | and are                            | foundational | to community | de- |                |     |     |     |
tection, recommendation, and many scientific applica- Graphs are a fundamental model for representing re-
tions. At billion-scale, however, existing graph embed- lationships across domains [16,21,8]. Recent advances
ding systems face a trade-off: they either rely on large in graph machine learning have expanded the scope of
in-memory footprints across many GPUs (limited scal- graph analytics to tasks such as link prediction [61,63,
ability) or repeatedly stream data from disk (incurring 53] and node classification [39,55,48]. Central to these
severe I/O overhead and low GPU utilization). successes are graph embeddings – continuous vector
Inthispaper,weproposeLegend,alightweighthete- representations that capture structural properties of
rogeneous system for graph embedding that systemat- nodes and serve as the basis for applications in recom-
ically redesigns data management across CPU, GPU, mendation systems [49,54,25], dialogue and conversa-
andNVMeSSDresources.Legendcombinesthreeprac- tional agents [59,5], drug discovery [58,50,14], etc. De-
tical ideas: (1) a prefetch-friendly embedding-loading spite the success, acquiring high-quality graph embed-
order that lets GPUs efficiently prefetch necessary em- dings entails prohibitive computational overhead, hin-
beddingsdirectlyfromNVMeSSDwithlowI/Oampli- dering the scalability of large-scale graphs [56].
fication;(2)ahigh-throughputGPU–SSDdirect-access Toscaleembeddingtrainingtolargegraphs,arange
drivertunedfortheaccesspatternsofembeddingtrain- of systems have been proposed, including Amazon’s
ing; and (3) a customized parallel execution strategy DGL-KE [57], Meta’s PyTorch Big Graph (PBG) [18],
that maximizes GPU utilization. Together, these com- Marius[27],andGE2 [56].ThesesystemsleverageGPUs
ponents let Legend store and stream vast embedding to accelerate computation, but real-world graphs often
data without overprovisioning GPU memory or suffer- contain millions or even billions of nodes, so storing
ing I/O stalls. Extensive experiments on billion-scale embeddings and optimizer state entirely in GPU mem-
graphs demonstrate that Legend speeds up end-to-end ory1 becomesimpractical[27,56].Asaresult,twodom-
workloads by up to 4.8× versus state-of-the-art sys- inant engineering strategies have emerged: (i) RAM-
tems, and matches their performance on the largest basedsystems(e.g.,DGL-KEandGE2)keepembeddings
andoptimizerstateinhostRAMandtransferrequired
| workloads | while using | only one quarter | of  | the GPUs. |            |              |                 |            |
| --------- | ----------- | ---------------- | --- | --------- | ---------- | ------------ | --------------- | ---------- |
|           |             |                  |     |           | partitions | to GPUs over | PCIe on demand. | (ii) Disk- |
Keywords Graph Embedding · Heterogeneous based systems (such as PBG and Marius) persist em-
Hardware Architecture · Data Partition · GPU beddingsondiskandstreampartitionsintoRAM(and
Acceleration then to GPUs) as needed. Figures 1(a) and (b) illus-
tratethearchitecturesofRAM-basedsystemsandDisk-
Gao((cid:0))
ZhonggenLi·Xiangyu Ke·YifanZhu·Yunjun based systems, respectively. Although both approaches
ZhejiangUniversity,Hangzhou,China
|               |                |                     |     |     | enable large-scale | training, | each has important | limita- |
| ------------- | -------------- | ------------------- | --- | --- | ------------------ | --------- | ------------------ | ------- |
| E-mail:{zgli, | xiangyu.ke,xtf | z,gaoyj}@zju.edu.cn |     |     |                    |           |                    |         |
Feifei Li 1 For instance, the Freebase86M dataset—comprising 86
AlibabaGroup,Hangzhou,China million nodes—demands 68 GB of memory to store 100-
lifeifei@alibaba-inc.com dimensionalembeddings and optimizerstates.

2 ZhonggenLietal.
CPU RAM CPU R
DD
A
iiss
M
kk ssggnniiddddeebbmm
CPU RAM
o
h
p
a
t
s
im
in
i
v
z
e
e
s
G
tig
P
a
U
te
-
d
sid
G
e
P
co
U
m
–S
p
S
u
D
tat
d
io
ir
n
e
s
c
.
t
A
a
l
c
th
ce
o
s
u
s
gh
in
p
o
r
t
io
h
r
er
wo
d
r
o
k
-
EE mains [15,1,31], applying this model to graph embed-
PCIe PCIe SSD PCIe ding and maximizing GPU utilization during training
raises three key challenges:
Batchs GPU GPU GPU Batchs
(a) RAM-based System (b) Disk-based System (c) Legend – Task Mapping.Existingembeddingworkflowsare
Fig. 1 Comparisonofsystemarchitectures. notengineeredforaCPU–GPU–SSDhardwarestack
and thus perform poorly when naively ported. For
example, systems that treat the NVMe device as
tions. RAM-based designs are constrained by host-
a slow disk (e.g., Marius) overload the CPU with
memory capacity and incur high provisioning costs: on
transfer work, while approaches that treat the SSD
a billion-node dataset (Twitter), RAM-based deploy-
likeRAM(e.g.,GE2)sufferbecauseSSD-GPUband-
mentsinflatedevicecostssubstantially(Table1).Disk-
width is substantially lower than RAM-GPU band-
baseddesignsavoidlargeRAMfootprintsbutintroduce
width (three times lower as shown in Table 1).
long data paths (disk-CPU-GPU) and suffer from sub-
– I/O Bottlenecks. Even with GPU–SSD direct ac-
optimal GPU utilization; in our measurements, disk-
cess (eliminating some CPU-mediated copies), I/O
based systems exhibit average GPU utilization of only
remains a nontrivial fraction of end-to-end training
about 58%, resulting in reduced end-to-end efficiency.
time – in our measurements, it accounts for over
These trade-offs motivate a rethinking of data place-
25% of the pipeline. The lower raw transfer rates
mentandI/OstrategiesacrossCPU,GPU,andNVMe
of SSDs versus RAM, therefore, remain a limiting
tierstoimprovebothscalabilityandutilizationforbill-
factor for throughput.
ion-scale graph embedding workloads.
– Computational Intensity.Oncetherequiredem-
Inadditiontothestorage-related inefficiencies,cur-
bedding shards and optimizer state are resident on
rent graph-embedding systems suffer from two critical
the GPU, downstream steps (batch construction,
computational bottlenecks: First, many systems (e.g.,
negativesampling,andweightupdates)involvecom-
Marius) remain CPU-centric for tasks such as batch
putationally intensive element-wise and reduction
construction, negative sampling, and embedding up-
operations (e.g., exponentiation, matrix multiplica-
dates.ThisCPUdependenceincreasesCPU–GPUcom-
tion). These operations must be carefully organized
municationandunderutilizesacceleratorcompute,pro-
to saturate the GPU; otherwise, GPU-side batch
ducing substantial per-batch slowdowns (up to 26× in
computation becomes the dominant bottleneck.
our measurements; see Table 1). Second, even systems
that offload batch construction to the GPU (e.g., GE2)
In this paper, we propose Legend, a scalable graph-
can still exhibit suboptimal GPU utilization because
embedding system that tightly integrates CPU, GPU
theirdesignsemphasizeembedding-frameworkfeatures
and NVMe SSD resources and applies three comple-
over training-path optimizations. In our experiments,
mentaryoptimizationfamiliestoaddresstheaforemen-
theGPU-sidebatchcomputationdominatesend-to-end
tionedchallengesofSSD-backedtraining.Belowwesum-
batch time – accounting for more than 80% of process-
marizeeachcomponent;implementationandformalde-
ing – thereby becoming the principal performance bot-
tails are presented in §3–§6.
tleneck.Together,thesetwolimitations,excessive CPU
dependence and inefficient GPU use, significantly re- Storage Arrangement and Task Allocation. To
duce throughput and hamper the scalability of billion- exploit the capacity and bandwidth characteristics of
scale embedding workloads. the platform in Figure 1(c), Legend separates hot and
Recently, NVMe SSDs have gained traction due to coldstate:graphtopologyandfrequentlyaccessedmeta-
their favorable balance of cost and performance [13,32, data remain in host RAM, while large, infrequently ac-
7]. Recent advances in NVMe SSDs offer an attractive cessed arrays (node embeddings and optimizer state)
cost–performance trade-off for large-scale storage [13, are resident on NVMe SSD. Control and orchestration
32,7]. Accordingly, we adopt the architecture in Fig- tasksaremappedtotheCPU,whereasheavylinearal-
ure 1(c), which replaces conventional RAM- or disk- gebraandper-batchcomputationexecuteontheGPU.
backedstoragewithNVMeSSDsandenablesGPU–SSD This partitioning reduces host-memory pressure, keeps
direct access to provide both economical capacity and latency-sensitive graph data immediately available in
lower-latency data movement. To realize efficient em- RAM, and leverages the GPU for compute-intensive
bedding training on this platform, we (i) map graph- kernels, yielding a pragmatic trade-off between capac-
embedding tasks across CPU, GPU, and SSD, and (ii) ity, bandwidth, and compute.

EfficientGraphEmbeddingatScale:OptimizingCPU-GPU-SSDIntegration 3
Table 1 Statistics of cost and efficiency on dataset Twitter (Edges: 1.3B, Nodes: 41.6M). Prices of devices are taken from
Amazonwhenwriting the paper.Ourexperimentsevaluatethebandwidths,throughputs,andexecution overheads.
Systems Storagecost Computingcost Comm.bandwidth Comp.throughput Batchtime Totaltime
|     | GE2  | 2.02$/GB |     | 33.2k$ |          |     |                    |     | 6.75×106 |     |         |        |     |       |
| --- | ---- | -------- | --- | ------ | -------- | --- | ------------------ | --- | -------- | --- | ------- | ------ | --- | ----- |
|     | [56] |          |     |        | (A100×4) |     | 10.05GB/s(CPU-GPU) |     |          |     | edges/s | 18.5ms |     | 32min |
Marius[27] 0.13$/GB 8.3k $(A100×1) 3.12GB/s(SSD-CPU) 1.49×106 edges/s 315.6ms 146min
|     |        | 0.13$/GB |     | 8.3k$ |          |     |                   |     | 7.18×106 |     |         |        |     |       |
| --- | ------ | -------- | --- | ----- | -------- | --- | ----------------- | --- | -------- | --- | ------- | ------ | --- | ----- |
|     | Legend |          |     |       | (A100×1) |     | 3.06GB/s(SSD-GPU) |     |          |     | edges/s | 12.0ms |     | 30min |
I/OOptimizations.Weintroducetwotechniquestai- Comprehensive experiments demonstrate the effi-
loredforGPU–SSDembeddingtraining:(i)Prefetch- ciency and scalability of Legend. It achieves a speedup
friendlyembeddingordering.Forexistinggraphem- of up to 4.8× compared to the state-of-the-art graph
bedding systems, embeddings are usually partitioned embedding systems. Legend is also lightweight and ex-
and loaded to the GPU in an I/O-optimized order [18, hibits comparable performance on a single GPU to the
57]. Although prefetching is supported in some exist- state-of-the-art system using 4 GPUs on the billion-
(§
ing graph embedding systems [27], the loading orders scale Twitter dataset 7).
| hinder | the | effective       | overlap | of  | the I/O     | and | computa-  |             |     |     |                   |     |     |             |
| ------ | --- | --------------- | ------- | --- | ----------- | --- | --------- | ----------- | --- | --- | ----------------- | --- | --- | ----------- |
|        |     |                 |         |     |             |     |           | In summary, |     | our | key contributions |     | are | as follows: |
| tion,  | and | the CPU-managed |         |     | prefetching | to  | RAM fails |             |     |     |                   |     |     |             |
to tackle the bottleneck of CPU-GPU data transfer, – We design a workflow to reasonably allocate tasks
|         |     |             |      |          |           |     |          | for graph | embedding |     | in  | the CPU-GPU-NVMe |     | SSD |
| ------- | --- | ----------- | ---- | -------- | --------- | --- | -------- | --------- | --------- | --- | --- | ---------------- | --- | --- |
| leading | to  | significant | data | transfer | overhead. |     | We prove |           |           |     |     |                  |     |     |
that generating a prefetch-friendly order while mini- heterogeneous systems, considering the respective
|        |     |       |       |         |          |     |              | characteristics |     | of  | each hardware |     | component | (§ 3). |
| ------ | --- | ----- | ----- | ------- | -------- | --- | ------------ | --------------- | --- | --- | ------------- | --- | --------- | ------ |
| mizing | I/O | times | is an | NP-hard | problem. |     | To get prac- |                 |     |     |               |     |           |        |
tical, we implement an efficient order-generation algo- – WeprovetheNP-hardnessofidentifyingaprefetch-
|       |       |     |                     |     |     |          |          | friendly | iteration |     | order | and propose | a   | heuristic al- |
| ----- | ----- | --- | ------------------- | --- | --- | -------- | -------- | -------- | --------- | --- | ----- | ----------- | --- | ------------- |
| rithm | based | on  | a column-separation |     |     | covering | strategy |          |           |     |       |             |     |               |
that produces a partition-swap order supporting effec- gorithmtosolvetheproblem(§4).Andwedevisea
customizedGPU-SSDdirectaccessmechanism(§5)
| tive | I/O–compute |     | overlap; | this | order | achieves | I/O la- |     |     |     |     |     |     |     |
| ---- | ----------- | --- | -------- | ---- | ----- | -------- | ------- | --- | --- | --- | --- | --- | --- | --- |
tency comparable to state-of-the-art heuristics while to achieve efficient I/O during embedding training.
– WeoptimizethebatchcomputationontheGPUby
enablingGPU-drivenprefetchesdirectlyfromSSDinto
GPU memory. (ii) Customized GPU-SSD direct devising a specific parallel strategy and exploiting
|        |         |     |               |     |         |         |        | the computation |     |     | and storage | resources |     | to enhance |
| ------ | ------- | --- | ------------- | --- | ------- | ------- | ------ | --------------- | --- | --- | ----------- | --------- | --- | ---------- |
| access | driver. |     | Off-the-shelf |     | GPU–SSD | drivers | expose |                 |     |     |             |           |     |            |
(§
substantialoverheadfromfine-grainedlockinganddoor- GPU utilization 6).
– Weconductcomprehensiveevaluationsdemonstrat-
belloperationswhenusednaivelyforembeddingwork-
loads [36,31,23]. In Legend we redesign NVMe queue ing that Legend outperforms existing graph embed-
dingsystems,achievingupto4.8×speedupforlarge-
| management |     | for | our access | patterns: |     | queue | positions |     |     |     |     |     |     |     |
| ---------- | --- | --- | ---------- | --------- | --- | ----- | --------- | --- | --- | --- | --- | --- | --- | --- |
(§
are precomputed so threads can concurrently enqueue scale graph embedding 7).
| and | dequeue | without |     | costly | locks, and | we  | use a full- |     |     |     |     |     |     |     |
| --- | ------- | ------- | --- | ------ | ---------- | --- | ----------- | --- | --- | --- | --- | --- | --- | --- |
Therestofthispaperisorganizedasfollows.Section
| coalesced |          | doorbell | ringing  | and | batch        | polling | strategy |           |            |     |                |     |          |        |
| --------- | -------- | -------- | -------- | --- | ------------ | ------- | -------- | --------- | ---------- | --- | -------------- | --- | -------- | ------ |
|           |          |          |          |     |              |         |          | 2 briefly | introduces |     | the background |     | of graph | embed- |
| to        | minimize | doorbell | overhead |     | and maximize |         | through- |           |            |     |                |     |          |        |
ding,GPUarchitectures,anddataaccessmechanismin
put.Thesechangesremovethepartial-coalescingineffi-
|          |     |               |            |           |               |        |          | NVMe SSD.       | Section |             | 3 presents  | the                   | workflow   | design in |
| -------- | --- | ------------- | ---------- | --------- | ------------- | ------ | -------- | --------------- | ------- | ----------- | ----------- | --------------------- | ---------- | --------- |
| ciencies |     | of prior      | approaches | and       | substantially |        | increase |                 |         |             |             |                       |            |           |
|          |     |               |            |           |               |        |          | Legend. Section |         | 4 describes |             | the prefetch-friendly |            | load-     |
| GPU–SSD  |     | communication |            | bandwidth |               | (§ 5). |          |                 |         |             |             |                       |            |           |
|          |     |               |            |           |               |        |          | ing order.      | Section | 5           | and Section | 6                     | illustrate | the opti- |
Computation Optimizations.Toefficientlyperform mization on SSD and GPU, respectively. Section 7 ex-
thecalculationsduringembedding,wedesignaparallel
|     |     |     |     |     |     |     |     | hibits the | experimental |     | results. | Section | 8   | reviews the |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | ------------ | --- | -------- | ------- | --- | ----------- |
strategy tailored to graph embedding learning work- related studies. We conclude the paper in Section 9.
| loads | that | fully | leverages | Tensor | cores, | registers, | and |     |     |     |     |     |     |     |
| ----- | ---- | ----- | --------- | ------ | ------ | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
sharedmemoryintheGPU.Thisstrategyreducesheavy
| memory |     | access | while ensuring |     | high | parallelism. | Addi- |     |     |     |     |     |     |     |
| ------ | --- | ------ | -------------- | --- | ---- | ------------ | ----- | --- | --- | --- | --- | --- | --- | --- |
tionally, we identify redundant calculations and reuse 2 Preliminaries
| intermediate |     | results | to  | further | reduce | computational |     |     |     |     |     |     |     |     |
| ------------ | --- | ------- | --- | ------- | ------ | ------------- | --- | --- | --- | --- | --- | --- | --- | --- |
costs (§ 6). These optimizations address the neglected In this section, we first provide an overview of graph
issue of embedding computation in existing graph em- embedding learning. Subsequently, we offer a concise
bedding systems, fully utilizing GPU resources, and description ofGPU architecture, following thedata ac-
achieving higher GPU utilization. cess mechanism of NVMe SSD.

| 4   |     |     |     |     |     |     |     |     |     |     | ZhonggenLietal. |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --------------- | --- |
A D
|     |     | B   |     |     | A B | A   |     |     |           |     | A   |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --------- | --- | --- | --- |
|     |     |     |     |     |     |     |     | A B | Gradients |     |     |     |
|     |     |     |     |     | A C | B   |     |     |           |     | B   |     |
|     | A   |     | A   | D   |     |     |     | A C |           |     |     |     |
C
|     |     |     |     |     |     | C   |     |     | GPU |     | C   |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|     |     |     | B   | C   |     |     |     | B C |     |     |     |     |
|     |     |     |     |     | B E | D   |     |     |     |     |     |     |
|     | D   |     |     |     |     |     |     |     |     |     | D   |     |
|     |     | E   |     |     |     |     |     | B E |     |     |     |     |
|     |     |     |     |     | B D | E   |     |     |     |     | E   |     |
Loss function L
B D
|     | Graph |     | Positive Edge  |     | Negative Edge  | Embedding  |     |     |     |     | Embedding  |     |
| --- | ----- | --- | -------------- | --- | -------------- | ---------- | --- | --- | --- | --- | ---------- | --- |
Selection Sampling Retrieval Batch Assembly Batch Computation Update
Fig. 2 Exampleofgraphembedding.
2.1 Graph Embedding Learning theparallelismofGPUs,SGDisperformedonbatches.
|     |     |     |     |     |     |     | Specifically, | a batch | is composed | of  | embeddings | cor- |
| --- | --- | --- | --- | --- | --- | --- | ------------- | ------- | ----------- | --- | ---------- | ---- |
Following PBG [18], Marius [27] and GE2 [56], we focus responding to both positive edges and negative edges.
on the multi-relation graphs denoted by G=(V,R,E), For each positive edge (edges from E), several negative
where V represents the set of nodes (entities), R is the edges are sampled using negative sampling algorithms.
set of edge (relation) types and E is the set of edges. All edges in E are iterated by being split into batches.
Each edge e ∈ E is a triplet denoted as e = (s,r,d), AsshowninFigure2,thebatchprocesscomprises6key
wheresisthesourcenode,r istherelationtype,andd stages:(1)Positiveedgeselection: fetchafixednumber
isthedestinationnode.Thetriplet(s,r,d)signifiesthat ofedgesfromE inorder(e.g.,(A,D)and(B,C)inFig-
entityshasarelationshiprwithentityd,indicatingthe ure 2), serving as positive edges that reflect true graph
presence of an edge between s and d. Although Legend connectivity.(2)Negative edge sampling:generateneg-
primarilytargetsmulti-relationgraphs,it’salsocapable ativesamplesbysamplingnodepairsfromV (thesam-
of handling graphs without relation types. plednodepairsarehighlylikelytobedisconnecteddue
Anembeddingisavectorθoffixeddimension.Dur- to the sparsity of the graph, e.g., B and C for edge
ing graph embedding learning, the elements in the em- (A,D), E and D for edge (B,C) in Figure 2). (3) Em-
beddingvectorsofeachnodeandrelationtypeareiter- beddingretrieval:retrievecurrentembeddingsfornodes
atively updated based on their previous values. Specif- and relations associated with both positive and nega-
ically, graph embedding learning uses a score function tive edges. These embeddings act as trainable param-
f(θ ,θ ,θ ), where θ , θ and θ represent the embed- eters in the downstream loss computation. (4) Batch
|     | s r | d   | s   | r   | d   |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
ding vectors of s,r,d in the triplet e = (s,r,d). There assembly: package the edges with their corresponding
are various score functions (i.e., embedding models) embeddings into a batch, enabling parallelized compu-
proposed for multi-relation graph embedding, such as tation of the contrastive loss (Equation 1). (5) Batch
ComplEx [41] and DistMult [51], which share a sim- computation: computes the loss function based on the
ilar computing procedure. Our work aims to acceler- current embeddings and calculates gradients according
ate the computing process of graph embedding, which to the loss function. (6) Embedding update: the origi-
is orthogonal to specific score functions. The goal of nal node embeddings are updated using the calculated
graph embedding learning is to maximize f(θ ,θ ,θ ) gradients. Whenalledgesaretraversedonce,anepoch
s r d
)for(s′,r′,d′)
for(s,r,d)∈Eandminimizef(θ s′ ,θ r′ ,θ d′ is completed. It always requires several epochs to en-
∈/ E, where e=(s,r,d) is referred to as a positive edge sure the convergence of the updated embeddings. It’s
e′ =(s′,r′,d′)
and is known as a negative edge, respec- worth noting that existing graph embedding systems
tively. This objective is achieved using the contrastive ignore the optimization of the time-consuming batch
| loss | function, | as  | shown | in Equation | 1.       |     |              |         |               |           |     |              |
| ---- | --------- | --- | ----- | ----------- | -------- | --- | ------------ | ------- | ------------- | --------- | --- | ------------ |
|      |           |     |       |             |          |     | computation, | which   | significantly | restricts |     | the training |
|      |           |     |       |             |          |     | efficiency   | and GPU | utilization.  |           |     |              |
|      | (cid:88)  |     |       |             | (cid:88) |     |              |         |               |           |     |              |
L=− (f(θ ,θ ,θ )−log( ef(θ s′,θ r′,θ d′))) As the number of nodes in a graph can easily reach
|     |           |     | s   | r d |               |     |           |                  |             |           |       |            |
| --- | --------- | --- | --- | --- | ------------- | --- | --------- | ---------------- | ----------- | --------- | ----- | ---------- |
|     |           |     |     |     |               |     | hundreds  | of millions,     | the limited | memory    |       | cannot ac- |
|     | (s,r,d)∈E |     |     |     | (s′,r′,d′)∈/E |     |           |                  |             |           |       |            |
|     |           |     |     |     |               |     | commodate | such large-scale |             | embedding | data. | To en-     |
(1)
|     |     |     |     |     |     |     | able scalable | graph | embedding | training, |     | we adopt a |
| --- | --- | --- | --- | --- | --- | --- | ------------- | ----- | --------- | --------- | --- | ---------- |
The loss function is optimized by stochastic gradi- partition-basedschemesimilartoPBG.Asillustratedin
entdescent(SGD),whichfurtherpromotestheupdates Figure 3, PBG divides the node embeddings into sev-
ofembeddings.TheembeddingmodelsemployAdagrad eral equal-sized partitions ({P ,P ,P ,P }) based on
|     |     |     |     |     |     |     |     |     |     | 0 1 | 2 3 |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
astheoptimizerforembeddingupdates.Tofullyutilize the node IDs, and stores them on the disk. In practi-

EfficientGraphEmbeddingatScale:OptimizingCPU-GPU-SSDIntegration 5
Memory Buffer paradigm, requiring all threads in a warp to execute
|     |     |     |     | (0,0) (0,1) | (0,2) | (0,3) |     |           |              |     |                |     |     |              |
| --- | --- | --- | --- | ----------- | ----- | ----- | --- | --------- | ------------ | --- | -------------- | --- | --- | ------------ |
|     |     |     |     | [0] [1]     | [4]   | [9]   |     |           |              |     |                |     |     |              |
|     |     | P P |     |             |       |       |     | identical | instructions |     | synchronously. |     | The | hierarchical |
0 1
(1,0) (1,1) (1,2) (1,3) execution model in CUDA further aggregates warps
|     |     |     |     | [2] [3]     | [6]   | [11]  |     |             |              |       |     |           |     |               |
| --- | --- | --- | --- | ----------- | ----- | ----- | --- | ----------- | ------------ | ----- | --- | --------- | --- | ------------- |
|     |     |     |     |             |       |       |     | into thread | blocks,      | which | are | scheduled |     | on individual |
|     |     |     |     | (2,0) (2,1) | (2,2) | (2,3) |     |             |              |       |     |           |     |               |
|     |     |     |     |             |       |       |     | SMs for     | computation. |       |     |           |     |               |
|     |     |     |     | [5] [7]     | [8]   | [13]  |     |             |              |       |     |           |     |               |
( 3 , 0 ) ( 3 , 1 ) ( 3 , 2 ) ( 3 , 3 ) ModernGPUsfeaturetwotypesofcomputingcores:
|     | P   | P 1 P 2 | P   |     |     |     |     |     |     |     |     |     |     |     |
| --- | --- | ------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
0 3 [ 1 0 ] [ 1 2 ] [ 1 4 ] [ 1 5 ] CUDAcoresandTensorcores.CUDAcoresserveasthe
|     |     | Disk |     | Edge Buckets |     |     |     |     |     |     |     |     |     |     |
| --- | --- | ---- | --- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
primarycomputationalunitsforgeneral-purposetasks,
Fig.3 Partition-basedtrainingscheme.P i denotesthenode while Tensor cores are specialized for efficient matrix
partitionand[j]denotesthecalculatingorder.
|     |     |     |     |     |     |     |     | multiplication, |     | enabling | the | multiplication |     | of fixed-size |
| --- | --- | --- | --- | --- | --- | --- | --- | --------------- | --- | -------- | --- | -------------- | --- | ------------- |
matriceswithinasingleclockcycle[60].TheGPUtyp-
cal implementations, optimizer states are stored along- ically has multiple levels of memory hierarchy, consist-
|          |      |             |     |          |      |             |     | ing of | global | memory, | shared | memory, | and | registers. |
| -------- | ---- | ----------- | --- | -------- | ---- | ----------- | --- | ------ | ------ | ------- | ------ | ------- | --- | ---------- |
| side the | node | embeddings, |     | although | they | are omitted |     |        |        |         |        |         |     |            |
in Figure 3 for simplicity. Correspondingly, the edges Globalmemory,sharedamongallthreadsontheGPU,
providesthelargestcapacitybuthasrelativelylowI/O
| are grouped | into | several | buckets, | where | the | bucket | ID  |     |     |     |     |     |     |     |
| ----------- | ---- | ------- | -------- | ----- | --- | ------ | --- | --- | --- | --- | --- | --- | --- | --- |
(i,j) indicates that the source nodes of these edges are bandwidth.Whenthreadsinawarpcollectivelyreador
|         |         |           |     |             |             |     |       | write contiguous |     | addresses | of  | global | memory, | it can be |
| ------- | ------- | --------- | --- | ----------- | ----------- | --- | ----- | ---------------- | --- | --------- | --- | ------ | ------- | --------- |
| located | in node | partition | P   | i , and the | destination |     | nodes |                  |     |           |     |        |         |           |
are located in node partition P . performed by a single I/O transaction, which is called
j
|     |     |     |     |     |     |     |     | coalesced | memory | access.Sharedmemory,accessibleby |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | ------ | -------------------------------- | --- | --- | --- | --- |
Duringtraining,theedgebucketsareprocessedina
specificorder,suchastheorderdenotedby“[k]”inside allthreadswithineachthreadblock,offershigherband-
|           |        |     |        |                |     |            |     | width but | with | a limited | capacity |     | of only | several tens |
| --------- | ------ | --- | ------ | -------------- | --- | ---------- | --- | --------- | ---- | --------- | -------- | --- | ------- | ------------ |
| each edge | bucket | in  | Figure | 3. To retrieve |     | the embed- |     |           |      |           |          |     |         |              |
dings related to the edges within each edge bucket, the ofKBs.Registersprovidethefastestdataaccessamong
|     |     |     |     |     |     |     |     | these memory |     | structures, | which | are | private | to individ- |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------ | --- | ----------- | ----- | --- | ------- | ----------- |
correspondingnodepartitionsarerequiredtobeloaded
intothememorybufferfromthedisk.Forexample,the ual threads once declared [3,30].
| buffer in  | Figure  | 3 contains |                            | P and P   | , supporting |       | the    |          |        |             |      |              |     |           |
| ---------- | ------- | ---------- | -------------------------- | --------- | ------------ | ----- | ------ | -------- | ------ | ----------- | ---- | ------------ | --- | --------- |
|            |         |            |                            | 0         | 1            |       |        |          |        |             |      |              |     |           |
| training   | of edge | buckets    | {(0,0),(0,1),(1,0),(1,1)}, |           |              |       | as     |          |        |             |      |              |     |           |
|            |         |            |                            |           |              |       |        | 2.3 Data | Access | Mechanism   |      | of NVMe      | SSD |           |
| the source | nodes   | and        | destination                | nodes     | of           | edges | within |          |        |             |      |              |     |           |
| these edge | buckets | are        | all                        | from node | partition    | P     | and    |          |        |             |      |              |     |           |
|            |         |            |                            |           |              |       | 0      | The NVMe | SSD    | facilitates | data | transmission |     | by lever- |
P 1 .Astheedgebucketsareprocessedinorder,thenode aging queue pairs, which consist of submission queues
| partitions | in  | the memory |     | buffer are | continuously |     | up- |           |            |     |        |        |          |       |
| ---------- | --- | ---------- | --- | ---------- | ------------ | --- | --- | --------- | ---------- | --- | ------ | ------ | -------- | ----- |
|            |     |            |     |            |              |     |     | (SQs) and | completion |     | queues | (CQs). | Multiple | queue |
dated. The node partitions in the memory buffer at pairs in an NVMe SSD enable parallel responses to re-
| any given | time | are referred |     | to as the | buffer | state. | For |     |     |     |     |     |     |     |
| --------- | ---- | ------------ | --- | --------- | ------ | ------ | --- | --- | --- | --- | --- | --- | --- | --- |
quests,ensuringhighthroughput[36,23].WhenaCPU
instance,thecurrentbufferstateinFigure3is{P 0 ,P 1 }. or GPU requests data, it first constructs NVMe com-
Itisimportanttonotethattheorderinwhichnode
|     |     |     |     |     |     |     |     | mands | following | the NVMe | protocol. |     | These | commands |
| --- | --- | --- | --- | --- | --- | --- | --- | ----- | --------- | -------- | --------- | --- | ----- | -------- |
partitions are loaded and edge buckets are processed specifytherequesttype(read/write),requestsize(typ-
significantlyaffectstheI/Otimesbetweenthediskand
|     |     |     |     |     |     |     |     | ically 512B | or  | 4KB), | request | address, | data | placement |
| --- | --- | --- | --- | --- | --- | --- | --- | ----------- | --- | ----- | ------- | -------- | ---- | --------- |
thememorybuffer.Forexample,iftheedgebucketsare address, and other parameters. Subsequently, it places
| iterated | in the | order | of {(0,0),(1,3),(1,0)}, |     |     | the | I/O |             |     |            |     |        |             |         |
| -------- | ------ | ----- | ----------------------- | --- | --- | --- | --- | ----------- | --- | ---------- | --- | ------ | ----------- | ------- |
|          |        |       |                         |     |     |     |     | the command |     | at the end | of  | an SQ. | Afterwards, | it sig- |
time is 4, as P 0 is loaded twice and other partitions nalstotheNVMecontrollerbywritingtheupdatedtail
| are loaded | once. | In  | contrast, | iterating | in  | the order | of  |     |     |     |     |     |     |     |
| ---------- | ----- | --- | --------- | --------- | --- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
pointerintothedoorbellregisteroftheNVMeSSDvia
{(0,0),(1,0),(1,3)}reducestheI/Otimeto3,sinceP 0 PCIe, indicating that new commands have been added
| is loaded | only | once. |     |     |     |     |     |        |          |           |     |       |             |       |
| --------- | ---- | ----- | --- | --- | --- | --- | --- | ------ | -------- | --------- | --- | ----- | ----------- | ----- |
|           |      |       |     |     |     |     |     | to the | SQ. This | operation | is  | known | as doorbell | ring- |
ing,whichcomesatahighcost.Therefore,someefforts
|     |     |     |     |     |     |     |     | are dedicated |     | to reducing | the | doorbell | ringing | times. |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------- | --- | ----------- | --- | -------- | ------- | ------ |
2.2 GPU Architecture The NVMe controller processes the commands, trans-
|     |     |     |     |     |     |     |     | fers the | requested | data | to the | host | memory, | and places |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | --------- | ---- | ------ | ---- | ------- | ---------- |
Moderngraphicsprocessingunits(GPUs)arecomposed completion entries into the CQ. Finally, the CPU or
of numerous streaming multiprocessors (SMs), where GPU retrieves the completion entries from the CQ and
each SM operates as an independent processing unit informs the NVMe controller by writing the new head
containing dozens or hundreds of computational cores. pointertothedoorbellregister,signifyingthatthenew
Within the CUDA programming framework, threads entries in the CQ have been processed [36].
aregroupedinto32-memberexecutionunitscalledwarps AlthoughdataaccesstotheNVMeSSDfollowsthe
thatfollowaSIMT(SingleInstructionMultipleThreads) aboveprotocol,theaccessdriverishighlycustomizable

| 6   |     |     |     |     |     | ZhonggenLietal. |     |
| --- | --- | --- | --- | --- | --- | --------------- | --- |
for different workloads in distinct applications. For ex- Control Flow Data Flow
ample, some customized NVMe drivers implement the Ei: Node Embeddings Si: Optimizer States Ei/Si: Updated Data
protocolintheuserspaceoftheoperatingsystemtore-
|     |     |     |     | NVMe SSD |     | GPU |     |
| --- | --- | --- | --- | -------- | --- | --- | --- |
ducetheoverheadoftheCPUsoftwarestack[52],while
| others implement                                   | the protocol | on the GPU | to achieve | E S         | ⑦         |             |         |
| -------------------------------------------------- | ------------ | ---------- | ---------- | ----------- | --------- | ----------- | ------- |
|                                                    |              |            |            | 0 0 E1 S1   | V N       | SQ0 CQ0 …   | SQn CQn |
|                                                    |              |            |            | E 0 ' S 0 ' | M         |             |         |
| higherthroughputbyemployingsubstantialthreads[36]. |              |            |            |             | C e ⑥     |             |         |
|                                                    |              |            |            |             | rellortno | Queue Pairs |         |
T h e q u e u e m a n a g em e n t a n d d o o r b el l r in g i n g s t ra t eg i es ⑧
|     |     |     |     | E2 S2 E3 S3 |     |     |     |
| --- | --- | --- | --- | ----------- | --- | --- | --- |
ar e a ls o r e d es ig n e d to r e d u c er e d u n d a n t o v e r he a d . H o w - (0,0) (0,1)
|     |     |     |     |     |     | E 0 | S 0 |
| --- | --- | --- | --- | --- | --- | --- | --- |
ever, existing NVMe drivers are not specifically opti- CPU E S E1 S1
|     |     |     |     |     |     | (1,0) (1,1) 2 | 2   |
| --- | --- | --- | --- | --- | --- | ------------- | --- |
RAM
| mized for | graph embedding | tasks. Therefore, | we pro- |     |     |     |     |
| --------- | --------------- | ----------------- | ------- | --- | --- | --- | --- |
③
pose a new driver customized for the graph embedding (0,0) (0,1) (0,2) (0,3) Rel. Embs.
|     |     |     |     |     | ①   | Batch |     |
| --- | --- | --- | --- | --- | --- | ----- | --- |
Rel. Stas.
workload to achieve significant throughput, which will (1,0) (1,1) (1,2) (1,3) ④
②
| be detailed | in Section 5. |     |     | (2,0) (2,1) (2,2) (2,3) |     |     |     |
| ----------- | ------------- | --- | --- | ----------------------- | --- | --- | --- |
⑤
|            |           |     |     | (3,0) (3,1) (3,2) (3,3) |     | Tensor CUDA |           |
| ---------- | --------- | --- | --- | ----------------------- | --- | ----------- | --------- |
|            |           |     |     | Edge Buckets            |     | Cores Cores | Gradients |
| 3 Workflow | in Legend |     |     |                         |     |             |           |
Fig. 4 WorkflowofLegend.
Inthissection,weintroducetheworkflowofLegend,fo-
| cusing on | storage arrangement, | task assignment | across |     |     |     |     |
| --------- | -------------------- | --------------- | ------ | --- | --- | --- | --- |
different hardware components, and the overall data overhead and failing to fully utilize the bandwidth be-
flow among each hardware component. tween the SSD and GPU. Considering the significant
Following the partition schema used in PBG [18], overhead during embeddingtransmission, we design an
GE2
Marius [27] and [56] (see Section 2.1 and Figure I/O-efficient partition loading order and a customized
3), Legend divides the graph’s nodes into n equal-sized high-throughput GPU-SSD direct access driver to re-
partitions based on their IDs (n = 4 in Figure 4). As ducetheI/OoverheadbetweentheGPUandtheNVMe
a result, the node embeddings are split into n corre- SSD, which will be introduced in Section 4 and 5. (2)
sponding partitions, and the edges are distributed into The edges, which require significantly less space com-
buckets. For example, the edge bucket (1,2) in Figure pared to embeddings and optimizer states, are stored
4 indicates that the source nodes of the edges in this inRAMandpartitionedintoedgebucketsaccordingto
edge bucket belong to node partition 1, while the des- their source and destination nodes. Storing the edges
tination nodes are from node partition 2. We carefully in RAM rather than NVMe SSD offers two key ad-
design the data placement and task mapping strate- vantages. First, since the CPU controls the graph em-
gies during graph embedding to make full use of the bedding learning process, it can effectively track the
unique characteristics of the CPU, GPU, and NVMe GPU’sprogress—specifically,whichedgebucketiscur-
SSD. Next, we will introduce how Legend maps storage rentlybeingprocessed.Asaresult,theCPUcantrans-
and tasks to the architecture of CPU-GPU-SSD. fer new edge buckets to the GPU on time and instruct
Storage Arrangement. Legend adopts a three-tiered the GPU to fetch the required embedding data from
storage architecture to separately store node embed- theNVMeSSD.Second,althoughthetheoreticalband-
dings, edges, and relation embeddings. (1) Node em- width of RAM and SSD to GPU is the same, the ac-
beddings and optimizer states are stored in the NVMe tual bandwidth between RAM and GPU is more than
SSD,whichoccupiesthemajorityofmemoryspacedur- 3 times higher than that between the NVMe SSD and
ingthegraphembeddinglearningprocess.Tomaximize GPU in our experiments (Table 1) due to the hard-
thebandwidthandmakefulluseofthehighparallelism ware restriction. Thus, storing edge buckets in RAM
of NVMe SSD, the embeddings and optimizer states of allows for efficient and synchronous transfers from the
each partition are stored in consecutive memory ad- CPU to the GPU, reducing the GPU’s idle time. (3)
dresses. This allows embedding and optimizer states For multi-relation graphs, the number of relation types
of a partition to be loaded simultaneously with a sin- is typically small, necessitating frequent synchronous
gle kernel on the GPU. As shown in Figure 4, E and updates [27]. Consequently, we store the relation em-
0
S are embeddings and optimizer states of node par- beddings (denoted as Rel. Embs.) and optimizer states
0
tition 0, which are stored consecutively. Otherwise, if (denoted as Rel. Stas.) in the global memory of the
thecompletenodeembeddingsandoptimizerstatesare GPU, following the design of existing graph embed-
storedintheNVMeSSDinsteadofbeingstoredinpar- ding systems [57,27,56]. Besides, there is a buffer in
titions, accessing one partition is required to perform theGPUtotemporarilyholdtheembeddingsandopti-
with two requests, leading to additional data transfer mizerstatesofpartialnodepartitions.AlthoughLegend

EfficientGraphEmbeddingatScale:OptimizingCPU-GPU-SSDIntegration 7
differs from prior systems by placing the buffer on the needforfrequentcommunicationbetweentheCPUand
GPU and transferring data directly from SSDs to the GPU. Second, the node embeddings are updated syn-
buffer, its buffer management strategy is conceptually chronously,avoidingthestalenessissuesencounteredin
similar: embeddings of node partitions are evicted and some graph embedding systems, such as Marius. Third,
loaded in a specific order. both negative edge sampling and embedding retrieval
Tasks Mapping. Considering the powerful ability of areparallelizabletasks,makingthemwell-suitedforex-
|         |                |         |        |      |             | ecution | on the | GPU. |     |     |     |     |     |
| ------- | -------------- | ------- | ------ | ---- | ----------- | ------- | ------ | ---- | --- | --- | --- | --- | --- |
| the CPU | to handle      | complex | logic  | and  | control     | tasks,  |        |      |     |     |     |     |     |
| the CPU | is responsible | for     | moving | data | and sending |         |        |      |     |     |     |     |     |
commands to the GPU and NVMe SSD in Legend, co- WhenLegendfinishesthecalculationofallfouredge
ordinatingandcontrollingtheprocessesoftasksonvar-
|     |     |     |     |     |     | buckets | in Figure | 4, it | has | to exchange | an  | embedding |     |
| --- | --- | --- | --- | --- | --- | ------- | --------- | ----- | --- | ----------- | --- | --------- | --- |
ioushardwarecomponents.Meanwhile,consideringthe andoptimizerstatepartitionintheGPUbuffer(E and
0
| powerful | parallel computing |     | capability | of  | the GPU, | it  |     |     |     |     |     |     |     |
| -------- | ------------------ | --- | ---------- | --- | -------- | --- | --- | --- | --- | --- | --- | --- | --- |
S inourexample)withanotherpartitionintheNVMe
0
takes on all computing tasks to achieve more efficient SSD (E and S in our example). Due to the limited
2 2
graphembeddingcomputation.Consideringtheunder-
|     |     |     |     |     |     | bandwidth | between | the | SSD | and GPU, | the | data trans- |     |
| --- | --- | --- | --- | --- | --- | --------- | ------- | --- | --- | -------- | --- | ----------- | --- |
utilization of the GPU during computation, we design fer is not completed immediately. However, the GPU
| an optimized | parallel | strategy | and | reorganize | the | com-   |               |     |       |             |           |     |     |
| ------------ | -------- | -------- | --- | ---------- | --- | ------ | ------------- | --- | ----- | ----------- | --------- | --- | --- |
|              |          |          |     |            |     | has no | computational |     | tasks | during data | exchange, |     | re- |
puting procedures to fully utilize the resources on the sulting in low utilization. Consequently, necessary data
| GPU, which | will be | illustrated | in  | Section | 6. Based | on            |     |           |       |             |     |             |     |
| ---------- | ------- | ----------- | --- | ------- | -------- | ------------- | --- | --------- | ----- | ----------- | --- | ----------- | --- |
|            |         |             |     |         |          | is prefetched |     | by Legend | at an | appropriate |     | time before |     |
thisstrategy,theCPUfirsttransfersedgebucketsfrom being used, which will be introduced in Section 4. The
RAM to the GPU, and the GPU subsequently con- CPU⑥launchesadataaccesskernelattheappropriate
structs batches as well as computes gradients. Once time to have the GPU offload E and S to the NVMe
|         |              |     |       |        |         |      |        |        |     | 0      | 0         |        |     |
| ------- | ------------ | --- | ----- | ------ | ------- | ---- | ------ | ------ | --- | ------ | --------- | ------ | --- |
| the CPU | detects that | the | edges | on the | GPU are | go-  |        |        |     |        |           |        |     |
|         |              |     |       |        |         | SSD, | and to | load E | and | S into | the GPU’s | global |     |
|         |              |     |       |        |         |      |        | 2      |     | 2      |           |        |     |
ing to be used up, it instructs the GPU to fetch the memory,whichisthekeyoperationofprefetching.The
| next embedding | partition |     | from | the SSD. | Afterwards, |     |             |        |         |         |        |         |     |
| -------------- | --------- | --- | ---- | -------- | ----------- | --- | ----------- | ------ | ------- | ------- | ------ | ------- | --- |
|                |           |     |      |          |             | GPU | data access | kernel | employs | several | thread | blocks, |     |
the CPU transfers new edge buckets to the GPU, and each with several threads to simultaneously construct
| a new round | of processing |     | begins | in the same | way. |      |          |     |         |      |      |             |     |
| ----------- | ------------- | --- | ------ | ----------- | ---- | ---- | -------- | --- | ------- | ---- | ---- | ----------- | --- |
|             |               |     |        |             |      | NVMe | commands | and | enqueue | them | into | the submis- |     |
Specifically, assume that the nodes are divided into sion queues. Subsequently, each submission queue ⑦
four partitions and that the buffer in the GPU global has a dedicated thread to ring the doorbells located in
memorycanaccommodatetwopartitionsatatime,i.e., the controller of the NVMe SSD, informing the NVMe
the buffer capacity is 2. Initially, the embeddings and SSD that there are new data access requests to pro-
optimizer states of partition 0 and partition 1 reside in cess. The NVMe controller ⑧ retrieves the data and
the GPU global memory and are randomly initialized, transfersthedatatotherequiredaddressesintheGPU
as shown in Figure 4. With partition 0 and partition 1, global memory using DMA (details will be introduced
the GPU conducts the computation of 4 edge buckets, inSection5).Meanwhile,theGPUcalculatesgradients
namely {(0,0),(0,1),(1,0),(1,1)}, as the source and for the remaining edge buckets during data exchange.
destination nodes of the edges within these edge buck- Forinstance,inFigure4,whentheGPUhascompleted
etsarelocatedinthesetwonodepartitions.Todothis, thecalculationofedgebuckets{(0,0),(0,1),(1,0)},the
asdepictedinFigure4,theCPU①fetchesedgebuckets
|     |     |     |     |     |     | CPU | launches | a data | access | kernel on | the | GPU to | ex- |
| --- | --- | --- | --- | --- | --- | --- | -------- | ------ | ------ | --------- | --- | ------ | --- |
{(0,0),(0,1),(1,0),(1,1)} from RAM and ② transfers change E and S with E and S . This is because E
|     |     |     |     |     |     |     | 0   | 0   | 2   | 2   |     |     | 0   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
③
them to the GPU global memory. The GPU then and S 0 will not be used for the computation of next
fetches a fixed number of edges (i.e., positive edges) edge buckets (i.e., {(1,1),(1,2),(2,1),(2,2)}), instead,
from the edge buckets, samples negative edges for each E 2 ,S 2 will be used. At the same time of this partition
positive edge, and retrieves the corresponding embed- exchange between the GPU and NVMe SSD, the GPU
dings and optimizer states from {{E 0 ,E 1 },{S 0 ,S 1 }} continues computing the edge bucket (1,1), which will
to construct a batch. Next, the gradients of this batch not be affected by this exchange. Legend implements
④
are calculated using Tensor cores and CUDA cores, the kernel parallelism of data access and edge bucket
which will be detailed in Section 6. The embeddings computation through CUDA streams. By parallelizing
and the optimizer states in the global memory are ⑤ the data access kernel and the computing kernel, the
updatedbytheGPUwiththecomputedgradients.The data transfer overhead can be hidden in the computa-
advantages of sampling negative edges and construct- tion of the remaining edge buckets, achieving overall
ing batches on the GPU are threefold. First, the cor- performance improvement. Furthermore, GPU waiting
responding embeddings of the trained edge buckets are time is eliminated by prefetching the data that needs
storedintheGPUratherthaninRAM,minimizingthe to be calculated, thereby increasing GPU utilization.

|     | 8   |     |     |     |     |     |     |     |     |     |     |     |     |     | ZhonggenLietal. |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --------------- | --- | --- | --- |
Calculated Edge buckets Edge buckets being calculated Edge buckets to calculate {(0,0),(0,1),(1,0),(1,1)}}asshowninFigure5(b).Th-
Destination Node Partition isexchangeprioritizesthecomputationofedgebuckets
|     |     |     | 0 1 2 | 3 4 | 0 1 | 2 3 4 |     | 0 1 2 3 | 4   |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | ----- | --- | --- | ----- | --- | ------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
n oititraP r e la t ed t o th e p ar t it i o n E b ef o r e s w ap p i n g it o u t fo r
|     |     | 0        | 1 2 4 |     | 0     | 1 1 | 0     |     | 1 5 |                                                     |          |          |            | 2     |         |            |                  |     |
| --- | --- | -------- | ----- | --- | ----- | --- | ----- | --- | --- | --------------------------------------------------- | -------- | -------- | ---------- | ----- | ------- | ---------- | ---------------- | --- |
|     |     | 1        | 3 6 7 |     | 1     | 1 3 | 1     |     | 1 7 |                                                     |          |          |            |       |         |            |                  |     |
|     |     |          |       |     |       |     |       |     |     | E . T hu                                            | s ,w e   | ca n e x | c h a ng   | e E w | i t h E | d u r in   | g ca l cu la t - |     |
|     |     |  ed 2    | 5 8 9 |     | 2     |     | 2     |     |     | 3                                                   |          |          |            | 2     | 3       |            |                  |     |
|     |     | oN       |       |     |       |     |       |     |     | ingtheremainingedgebuckets(i.e.,{(0,0),(0,1),(1,0), |          |          |            |       |         |            |                  |     |
|     |     | 3        |       |     | 31012 |     | 3     |     |     |                                                     |          |          |            |       |         |            |                  |     |
|     |     |  ecruo 4 |       |     | 4     |     | 41416 |     |     |                                                     |          |          |            |       |         |            |                  |     |
|     |     |          |       |     |       |     |       |     |     | (1,1)}).                                            | However, | this     | adjustment |       | is only | applicable | in               |     |
S
E , E , E E , E , E E , E , E the initial buffer state. In the subsequent buffer state,
|     |     |     | Buffer× Cannot be prefetched 0 1 | 2   | 0   | 1 3 |     | 0 1 | 4   |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | -------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Swap E with E as depicted in the second subfigure in Figure 5(b), the
2 3
(a) The edge bucket iteration order in Marius. edge buckets are all related to E , hindering the evic-
3
|     |     |     |     |     |     |     |     |     |     | tion of | E 3 and | the | prefetching |     | of the | next | partition. |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ------- | ------- | --- | ----------- | --- | ------ | ---- | ---------- | --- |
Destination Node Partition
|     |     |     |     |     |     |     |     |     |     | The underlying |     | issue | is that | the | partition | swapped | in  |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | -------------- | --- | ----- | ------- | --- | --------- | ------- | --- | --- |
Calculated Edge buckets Edge buckets being calculated n 0 1 2 3 4 0 1 2 3 4 0 1 2 3 4
|     |     | oititraP 0 | 6 7 1 |     | 0   | 1 1 | 0   |     | 1 5 |     |     |     |     |     |     |     |     |     |
| --- | --- | ---------- | ----- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Edge buckets to calculate d ur i n g t h e pr e v io u s b u ff e r s t a t e is i m m ed i a t e ly e v ict e d
|     |     | 1   | 8 9 3 |     | 1   | 1 3 | 1   |     | 1 7 |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | ----- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
 ed in t h e n e xt b u ff e r s t at e , l e a v i ng i n s uffi c i e n t ti m e f o r
|     |     | 2    | 2 4 5 |     | 2      |     | 2   |     |     |     |     |     |     |     |     |     |     |     |
| --- | --- | ---- | ----- | --- | ------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|     |     | oN 3 |       |     | 3 1012 |     | 3   |     |     |     |     |     |     | 2   |     |     |     |     |
 ecruo p r efe t ch i n g . A lt h o u g h G E [ 5 6] e m p lo y s a n o t h e r s tr a t-
|     |     | 4   |         |     | 4       |     | 41416 |         |     |           |           |           |         |          |           |         |                    |     |
| --- | --- | --- | ------- | --- | ------- | --- | ----- | ------- | --- | --------- | --------- | --------- | ------- | -------- | --------- | ------- | ------------------ | --- |
|     |     |     |         |     |         |     |       |         |     | e g y t o | r e d u c | e t h e I | / O t i | m e s (i | .e ., n o | d e p a | r t i t io n e x - |     |
|     |     | S   | E, E, E |     | E, E, E |     |       | E, E, E |     |           |           |           |         |          |           |         |                    |     |
|     |     |     | 0 1     | 2   | 0       | 1 3 |       | 0 1     | 4   |           |           |           |         |          |           |         |                    |     |
e√r ×  Cannot be prefetc hed change counts), it also fails to support prefetching due
|     |     |     | B uff |  Can be prefetched  |  afte | r   |                |     |     |              |          |     |     |     |     |     |     |     |
| --- | --- | --- | ----- | ------------------- | ----- | --- | -------------- | --- | --- | ------------ | -------- | --- | --- | --- | --- | --- | --- | --- |
|     |     |     |       | the 5th edge bucket |       |     | Swap E  with E |     |     | to a similar | problem. |     |     |     |     |     |     |     |
|     |     |     |       |                     |       |     | 3              | 4   |     |              |          |     |     |     |     |     |     |     |
|     |     |     |       | Swap E with E       | 2     | 3   |                |     |     |              |          |     |     |     |     |     |     |     |
Fromtheprecedingdiscussion,weobservethatpar-
(b) The modified edge bucket iteration order for prefetching.
titionprefetchingcanbeachievediftherecentlyloaded
Fig.5 PartitionloadingorderinMarius.Thenumbersinside
|     |                |     |     |                             |     |     |     |     |     | partition | is not  | immediately |     | swapped   |           | out of | the GPU |     |
| --- | -------------- | --- | --- | --------------------------- | --- | --- | --- | --- | --- | --------- | ------- | ----------- | --- | --------- | --------- | ------ | ------- | --- |
|     | theedgebuckets |     |     | denotetheircalculatedorder. |     |     |     |     |     |           |         |             |     |           |           |        |         |     |
|     |                |     |     |                             |     |     |     |     |     | memory    | buffer. | During      | the | partition | exchange, |        | we cal- |     |
culatetheedgebucketsunrelatedtotheexchangedpar-
Calculated Edge buckets Edge buckets being calculated  Edge buckets to calculate
Destination Node P4artitEiondge titions, ensuring the overlap of computation and data
|     |     |     | Bucket | Ordering |     |     |     |     |     |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | ------ | -------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
0 1 2 3 4 5 0 1 2 3 4 5 0 1 2 3 4 5 0 1 2 3 4 5 tran0sfe1r.2I3n4ou5rproble0m1s2et3tin4g5,weassu0m1e2th3e4n5umber 0 1 2 3 4 5
n
| oititraP 0 6 1 7 |     | 0   |     | 1 2 | 0   |     | 1 7 | 0   | 2   | 0 0 |     | 0   |     |     | 0   |     | 0   |     |
| ---------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
1 2 3 4 1 1 1 o f 1 pa r t it io n 2s5 2 is7 n ( n 1 > 3 ) a 2n 9 d t h e b u 1 ff e r c ap a c it y ( th e 1
|             | I n | th i s s e | c t i o n , | w e il l u | s t r a t | e o u r p | ro p o se | d p a r t | it i o n lo a d | -   |     |     |     |     |     |     |       |     |
| ----------- | --- | ---------- | ----------- | ---------- | --------- | --------- | --------- | --------- | --------------- | --- | --- | --- | --- | --- | --- | --- | ----- | --- |
|  ed 2 8 5 9 |     | 2          |             | 1 0        | 2         |           |           | 2         |                 | 2   |     | 2   |     |     | 2   |     | 3 3 2 | 35  |
in g o r d 3e r1 a n d1 t h e c o r r e s p o n d i n g e 1d 5g e b u c k e t i t e ra ti o n n u m b e r o f p a r tit i o n s th a t c a n b e lo a d e d ) in t h e G P U ’ s
| oN 3 |     |     | 3 1 | 1 4 | 3   |     |     | 3   |     | 3   |     | 3   | 3 0 | 3 1 | 3   |     | 3   |     |
| ---- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
 ecruo 4 4 4r l1a8 1I 6/ 1O9 4m 2 2 g l o4 b a l2 6 m e m o r y i s fix 4 e d a t 3 f o r p ro b l4 e m si m p l i fic a ti o n .4 36
|     | orde | r t o | e n h a n | ce th e | o v e | p o f | a nd | co  | p u ta t i o n . |          |     |     |     |        |     |        |     |     |
| --- | ---- | ----- | --------- | ------- | ----- | ----- | ---- | --- | ---------------- | -------- | --- | --- | --- | ------ | --- | ------ | --- | --- |
| 5   |      | 5     |           |         | 5     |       |      | 5 2 | 1 2 3 2          | 4 5 2 8o |     |     | 5   | s3 t2r | 5   | t3 a4s | 5   |     |
S A s d is c u s s ed in S ec t i o n 3 , w h e n th e GP U c o m p l e t e s T h is c n fi gu r a t i on e n ab le a i n in g o n da e t s o f a n y
E , E , E E , E , E E , E , E E , E , E E ,  E ,  E E ,  E ,  E E , E ,  E E , E , E
Buffer 0 1 2 0 3 2 0 3 4 0 5 4 size, a s1 t h5 e 4value of n i s1 a r5 b i3trary. To id e2n t5i f y3a load- 2 5 4
thetrainingofalledgebucketsassociatedwiththecur-
|     | S w | a p E   w it | h   E |     |     |     |     |     |     |     |     |     |     |     |     |     |     |     |
| --- | --- | ------------ | ----- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
r e n t p1 a r t i t i2ons in its global memory, it has to wait for ing order that supports prefetching, we first define the
|     |     |              |     |               |             |     |               |     |           | concept    | of a | Prefetching  | Supported |           | Order. |        |     |     |
| --- | --- | ------------ | --- | ------------- | ----------- | --- | ------------- | --- | --------- | ---------- | ---- | ------------ | --------- | --------- | ------ | ------ | --- | --- |
|     | the | transfer     | of  | the next      | partitions, |     | leading       | to  | reduced   |            |      |              |           |           |        |        |     |     |
|     | GPU | utilization. |     | If embeddings |             |     | and optimizer |     | states of |            |      |              |           |           |        |        |     |     |
|     |     |              |     |               |             |     |               |     |           | Definition | 1    | (Prefetching |           | Supported |        | Order) | A   |     |
thenextpartitionareprefetchedintotheGPU’sglobal
|     |     |     |     |     |     |     |     |     |     | Prefetching | Supported |     | Order | is  | a node | partition | load- |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ----------- | --------- | --- | ----- | --- | ------ | --------- | ----- | --- |
memorybeforebeingused,theGPUcanperformcalcu-
ingordersuchthatthereisatleastoneedgebucketnot
lationsforthesubsequentbatchwithoutincurringwait-
|     |         |           |          |             |               |          |                 |         |          | related     | to the | node          | partition | scheduled |      | for    | eviction in |     |
| --- | ------- | --------- | -------- | ----------- | ------------- | -------- | --------------- | ------- | -------- | ----------- | ------ | ------------- | --------- | --------- | ---- | ------ | ----------- | --- |
|     | ing     | time.     | Although | prefetching |               | is       | supported       | in      | existing |             |        |               |           |           |      |        |             |     |
|     |         |           |          |             |               |          |                 |         |          | each buffer | state. |               |           |           |      |        |             |     |
|     | graph   | embedding |          | systems     |               | [27],    | their partition |         | loading  |             |        |               |           |           |      |        |             |     |
|     | orders  | focus     | on       | reducing    |               | the node | partition       |         | exchange |             |        |               |           |           |      |        |             |     |
|     |         |           |          |             |               |          |                 |         |          | According   |        | to Definition |           | 1, in     | each | buffer | state, we   |     |
|     | counts, |           | missing  | many        | opportunities |          | to              | overlap | the I/O  |             |        |               |           |           |      |        |             |     |
canfirstcomputetheedgebucketsrelatedtotheparti-
|     | and | computation |     | during | prefetching. |     |     |     |     |     |     |     |     |     |     |     |     |     |
| --- | --- | ----------- | --- | ------ | ------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
tionthatwillbeevictedandsimultaneouslyloadanew
|     |         | We illustrate |             | the | issue | with     | Marius’s  | loading | order     |           |        |                 |             |     |         |        |         |     |
| --- | ------- | ------------- | ----------- | --- | ----- | -------- | --------- | ------- | --------- | --------- | ------ | --------------- | ----------- | --- | ------- | ------ | ------- | --- |
|     |         |               |             |     |       |          |           |         |           | partition | during | the             | computation |     | of the  | edge   | buckets |     |
|     | through |               | an example. |     | As    | depicted | in Figure |         | 5(a), the |           |        |                 |             |     |         |        |         |     |
|     |         |               |             |     |       |          |           |         |           | unrelated | to     | this partition. |             | The | loading | orders | in Mar- |     |
memorybufferisinitializedwithpartitions{E ,E ,E }. ius and GE2 do not qualify as a Prefetching Supported
|     |     |     |     |     |     |     |     |     | 0 1 2 |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ----- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Mariuscomputestheedgebucketsintheorderof{(0,0),
|     |     |     |     |     |     |     |     |     |     | Order, | as they | have | no edge | bucket | unrelated |     | to the |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ------ | ------- | ---- | ------- | ------ | --------- | --- | ------ | --- |
(0,1),(1,0),(0,2),(2,0),(1,1),(1,2),(2,1),(2,2)}.Next, partition that will be evicted in most buffer states. To
|     | partitionE |     | isevicted,andE |     |     | willbeswappedin.How- |     |     |     |                                   |     |     |     |     |           |     |          |     |
| --- | ---------- | --- | -------------- | --- | --- | -------------------- | --- | --- | --- | --------------------------------- | --- | --- | --- | --- | --------- | --- | -------- | --- |
|     |            |     | 2              |     |     | 3                    |     |     |     | effectivelyidentifythePrefetching |     |     |     |     | Supported |     | Order,we |     |
ever,E cannotbeprefetchedatthistimebecausethere explore its properties in Theorem 1.
3
isnoremainingedgebucketintheGPUmemorytocal-
culate while fetching E . The order in which node par- Theorem 1 For the buffer capacity of 3, a partition
3
titions are loaded or evicted is noted as the partition loading order is classified as a Prefetching Supported
loading order throughout the rest of this paper. Order if it satisfies two properties: (1) The partition
Toachieveprefetching,theedgebucketiterationor- that has just been swapped in each buffer state will not
dercanbeadjustedto{{(0,2),(2,0),(1,2),(2,1),(2,2)}, be immediately evicted in the subsequent buffer state.

EfficientGraphEmbeddingatScale:OptimizingCPU-GPU-SSDIntegration 9
(2)Anytwopartitionsmayappearconcurrentlyinmul- design problem. A node partition in the buffer is sub-
tiple buffer states, but only in consecutive buffer states. sequently swapped with a partition out of the buffer.
Each exchange operation above generates a new block
Proof. Without loss of generality, we consider the con- in the covering design problem. The requirement that
secutivebufferstates{E i ,E j ,E k },{E i ,E j ,E l },{E i ,E m all pairs of node partitions must coexist in the buffer
,E l },wherethebluecolorandtheunderlinedenotethe is equivalent to ensuring all C n 2 pairs are covered by
loadednodepartitioninthecurrentbufferstateandthe thesequenceofblocks.Acoveringdesignproblemsolu-
partition to be evicted, respectively. E i and E j appear tionwithmblocksimpliesavalidexchangesequenceof
concurrently in the first two consecutive buffer states. m−1 steps, as each block requires one exchange. Con-
For the buffer state {E i ,E j ,E k }, the edge buckets re- versely,anexchangesequenceoflengthkproducesk+1
lated to E i and E k have been calculated during load- blockscoveringallpairs.Toaddresstheconstraintthat
ing E j . E k is the node partition in the current buffer is introduced in the property (1) of Theorem 1, inter-
state that is going to be evicted. The edge buckets mediate blocks may be inserted (e.g., exchanging two
{(i,j),(j,i)} that are not related to E k must not have elementssequentially),whichonlypolynomiallyinflates
been calculated due to the property (2). Otherwise, if thesequencelengthandpreservesthereduction’svalid-
the property (2) is not satisfied, E i and E j can appear ity. Since the covering design problem is NP-hard, our
concurrently in a previous buffer state. Their corre- problem is also NP-hard.
spondingedgebuckets(i,j)and(j,i)havealreadybeen
calculatedatthatbufferstate.Thereforewecannotex-
The NP-hardness of this problem motivates us to
change E with E while calculating other edge buck-
k l devise an efficient heuristic algorithm. To this end, we
etsatbufferstate{E ,E ,E },leadingtothefailureof
i j k propose a column separation covering strategy to gen-
prefetching.Similarly,fornextbufferstate{E ,E ,E },
i j l erateanordersupportingprefetchingwhileminimizing
E isgoingtobeevicted.Edgebuckets{(i,l),(l,i)}are
j I/O times within one second. The key idea of the load-
notrelatedtoE andhavenotbeencalculated.Wecan
j ing order is to sequentially cover each column of edge
evictE andprefetchthenextnodepartitionwhilecal-
j buckets, greedily maximizing coverage in each column.
culating {(i,l),(l,i)}.
Figure6depictsanexampleofourproposednodeparti-
tionloadingorderandedgebucketiterationorderwith
It is important to note that the impact of the prop-
6 node partitions.
erty (2) in Theorem 1 is minimal in practical appli-
Initially, we cover edge buckets in the first column
cations. Without considering property (2), only 4 out
byswappingineachnodepartitioninorderoftheirID.
of 36 I/O times fail to support prefetching for 12 par-
Forexample,wecoveredgebuckets{(0,0),(1,0),(2,0),
titions, as demonstrated in experiments. Therefore, we
(3,0),(4,0),(5,0)} in column 0 by sequentially swap-
excludeproperty(2)fromthealgorithmdesign.Ourob-
pinginnodepartitions{E ,E ,E ,E ,E ,E }(thefirst
jective is to design an efficient algorithm to find an or- 0 1 2 3 4 5
fourbufferstatesinFigure6).Forsubsequentcolumns,
derthatsatisfiesproperty(1)whileminimizingtheI/O
we swap in node partitions starting from the maximal
times. We adopt the same swapping strategy as Mar-
ID in the current buffer state. If all edge buckets from
ius [27], which allows a single partition to be swapped
the maximal ID to n are covered, we then switch to
in each buffer state. Generating an order that satisfies
theminimalID.Forinstance,aftertransitioningtocol-
property(1)isstraightforward.However,identifyingan
umn1withthebufferstate{E ,E ,E },westartwith
order that meets property (1) while minimizing I/O 1 5 4
the node partition having the minimal ID to swap in,
times is an NP-hard problem, as proved in Theorem 2.
which is E . Subsequently, the buffer state changes to
3
{E ,E ,E }andedgebuckets{(3,1),(1,3),(3,5),(5,3)}
Theorem 2 With n partitions and a buffer capacity of 1 5 3
are covered. Since all edge buckets in column 1 are
3, the problem of identifying an order that meets prop-
covered, we move to column 2 after the buffer state
erty (1) while minimizing I/O times is NP-hard.
{E ,E ,E } by loading node partition E , and edge
1 5 3 2
Proof. We demonstrate that the problem is NP-hard buckets {(5,2),(2,5)} are covered. For column 2, we
viaareductionfromthecoveringdesignproblem[10],a again start with the minimal ID, which is 4, to swap
well-known NP-hard problem. Specifically, an instance in. Therefore, the buffer state changes to {E 2 ,E 5 ,E 4 },
ofthecoveringdesignproblemwithparameters(n,3,2), and all edge buckets have been covered by now. The
which seeks the minimum number of 3-element subsets procedures are formalized in Algorithm 1.
(blocks) covering all C2 pairs, is mapped to our prob- In Algorithm 1, we first generate the buffer states
n
lemasfollows.Thebufferisfirstinitializedwithabuffer relatedtonodepartition0(lines3-6).Inthewhileloop
state, corresponding to an initial block in the covering within lines 8-24, if all edge buckets in the current col-

0 1 2 3 4 0 1 2 3 4 0 1 2 3 4
0 1 2 4 0 11 0 15
1 3 6 7 1 13 1 17
2 5 8 9 2 2
3 31012 3
4 4 41416
E, E, E E, E, E E, E, E
0 1 2 0 1 3 0 1 4
Swap E with E
2 3
0 1 2 3 4 5 0 1 2 3 4 5 0 1 2 3 4 5 0 1 2 3 4 5 0 1 2 3 4 5 0 1 2 3 4 5 0 1 2 3 4 5 0 1 2 3 4 5
0 6 1 7 0 12 0 17 0 20 0 0 0 0
1 2 3 4 1 1 1 1 2527 1 29 1 1
2 8 5 9 2 10 2 2 2 2 2 33 2 35
3 313 1114 3 15 3 3 3 30 31 3 3
4 4 418 1619 4 22 4 26 4 4 4 36
5 5 5 521 2324 5 28 5 32 5 34 5
E, E, E E, E, E E, E, E E, E, E E, E, E E, E, E E, E, E E, E, E 0 1 2 0 3 2 0 3 4 0 5 4 1 5 4 1 5 3 2 5 3 2 5 4
10 ZhonggenLietal.
noititraPedoNecruoS
Calculated Edge buckets Edge buckets being calculated
Destination Node Partition
Buffer
noititraPedoNecruoS
Edge buckets tocalculate
Calculated Edge buckets Edge buckets being calculated 0 1 2 3 4 0 1 2 3 4 0 1 2 3 4
0 6 7 1 0 11 0 15
Edge buckets tocalculate 1 8 9 3 1 13 1 17
2 2 4 5 2 2
3 31012 3
4 4 41416
E,E, E E, E, E E, E, E
0 1 2 0 1 3 0 1 4
Swap E with E
2 3
Calculated Edgebuckets Edgebuckets being calculated Edgebuckets to calculate
Destination Node Partition
Buffer
Swap E with E
1 3
noititraPedoNecruoS
×Cannot be prefetched
(a) The edgebucket iteration order in Marius.
Destination Node Partition
Buffe√r Can be prefetched after × Cannot be prefetched
the 5thedge bucket Swap E 3 with E 4
(b) Themodified edge bucket iteration order forprefetching.
0 1 2 3 4 5 0 1 2 3 4 5 0 1 2 3 4 5 0 1 2 3 4 5
0 6 1 7 0 12 0 17 0 20
1 2 3 4 1 1 1
2 8 5 9 2 10 2 2
3 313 1114 3 15 3
4 4 418 1619 4 22
5 5 5 521 2324
E, E, E E, E, E E, E, E E, E, E 0 1 2 0 3 2 0 3 4 0 5 4
0 1 2 3 4 5 0 1 2 3 4 5 0 1 2 3 4 5 0 1 2 3 4 5
0 0 0 0
1 2527 1 29 1 1
2 2 2 33 2 35
3 3 30 31 3 3
4 26 4 4 4 36
5 28 5 32 5 34 5
E, E, E E, E, E E, E, E E, E, E
1 5 4 1 5 3 2 5 3 2 5 4
noititraP
edoN
ecruoS
Calculated Edge buckets Edge buckets being calculated Edge buckets to calculate
Destination Node Partition
Buffer
Swap E with E
1 3
Fig. 6 Order for prefetching in Legend. The numbers inside the edge buckets denote their calculated order. The blue color
indicatestheedgebucketsthatcanbecalculatedwhileprefetchingthenextpartition.E istheprefetchedpartition.E isthe
i j
node partitiontobe evictedinthenextbuffer state.
umn CurCol have been covered, we advance to the {E ,E ,E }firstcalculatesedgebucketsrelatedtoE .
0 3 2 2
next column by swapping node partition E with Similarly, E is replaced with E in advance right af-
CurCol 2 4
E and mark the corresponding edge buckets terthecalculationof{(2,3),(3,2)}.Andtheremaining
CurCol+1
as covered (lines 11-13). Then we select the maximal edge buckets are calculated at the same time. The fol-
ID in the current buffer as the node partition to evict, lowing buffer states adopt a similar process to prefetch
provided that subsequent IDs have corresponding edge thenextnodepartitionwhilecalculatingtheremaining
buckets that remain uncovered. Otherwise, we opt for edge buckets, significantly reducing the I/O overhead.
theminimalID(lines13-17).Iftheedgebucketsinthe AlthoughprefetchinghidesI/Ooverheadinthecom-
current column have not been fully accessed, we evict putation, it also raises the problem of whether the I/O
a node partition that was not just swapped in the last overhead can be completely covered. To this end, The-
buffer state (line 19). Finally, we greedily select a node orem3discussesthisproblemandprovesthatithasto
partition that covers the most edge buckets from the do with the dataset characteristics.
BeginID to swap in (lines 20-24).
Theorem 3 Using the loading order generated by Al-
Algorithm 2 generates the edge bucket iteration or-
gorithm 2, the I/O overhead can be completely covered
der according to the output of Algorithm 1. It first
by the computation when |E| ≥ 96d2 , where |E| and
covers the edge buckets related to the node partition |V|2 Mt(w+r)
|V| are the number of edges and nodes, d is the em-
scheduled for eviction in the next buffer state (lines 7-
bedding dimension, M is the buffer size in the global
13).Subsequently,itcalculatestheedgebucketsrelated
memory of GPU, t is the average computing time of an
to both the node partition that will be evicted and the
edge, w and r are the writing and reading throughput
one that was just swapped in (lines 14-19).
between the GPU and NVMe SSD.
Example. Figure 6 exhibits an example of the node
partition loading order output by Algorithm 1 and the Proof. Suppose the node embeddings are divided into
edge buckets iterating order generated by Algorithm 2. npartitions.Foreachedgebucket,theaveragenumber
Fortheinitialbufferstate{E ,E ,E },theedgebuck- ofedgesis |E|.Consequently,theaveragetimetocalcu-
0 1 2 n2
etsrelatedtoE
1
(i.e.,{(0,1),(1,0),(1,1),(1,2),(2,1)}) lateanedgebucketist∗|
n
E
2
|.Anexchangeofapartition,
are first calculated. Subsequently, E can be swapped includingwritingtheoldpartitionintotheNVMeSSD
1
withE inadvance.Theremainingedgebucketsinthe andloadingthenewoneintotheGPUbuffer.Eachpar-
3
initial buffer state (i.e., {(0,0),(0,2),(2,0),(2,2)}) are titioncontainsembeddingsandoptimizerstates,whose
calculated during thedata exchange.After the calcula- total size is 2∗P. As a result, an exchange of a par-
tion of the initial buffer state, the second buffer state tition requires time of 2∗P. Following the order output
w+r

EfficientGraphEmbeddingatScale:OptimizingCPU-GPU-SSDIntegration 11
Algorithm 1: Node partition loading order Algorithm 2: Edge buckets iterating order
Input: Node partitions n, buffer capacity 3 Input: Buffer states BufStates, node partitions n
Output: Buffer states in order. Output: Edge buckets iterating order.
1 EdgeBuckets←{0} n∗n , BufStates←{}; 1 EdgeBuckets←{0} n∗n , BufStates←{};
| 2 CurCol←0; |     |     |     |     |     |     | 2 IterOrder |     | ←{(0,1),(1,1),(1,0),(1,2),(2,1)}; |     |     |     |     |
| ----------- | --- | --- | --- | --- | --- | --- | ----------- | --- | --------------------------------- | --- | --- | --- | --- |
3 BufStates.append({0,1,2}); 3 Set the covered edge buckets to 1;
| Buf   | ←BufStates[−1]; |            |     |     |     |     | LoadedPar |                              | ←3; |     |     |     |     |
| ----- | --------------- | ---------- | --- | --- | --- | --- | --------- | ---------------------------- | --- | --- | --- | --- | --- |
| 4     |                 |            |     |     |     |     | 4         |                              |     |     |     |     |     |
|       |                 |            |     |     |     |     | for       | i in range(len(BufStates)-1) |     |     |     | do  |     |
| 5 for | i in            | range(3,n) |     | do  |     |     | 5         |                              |     |     |     |     |     |
ToEvict←BufStates[i]−BufStates[i+1];
| 6   | Buf | ←Buf | −{i−2}+{i}; |     |     |     | 6   |     |     |     |     |     |     |
| --- | --- | ---- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
7 BufStates.append(Buf); 7 for k ∈BufStates[i]−{LoadedPar} do
Set the covered edge buckets to 1; 8 if EdgeBuckets[ToEvict][k]=0 then
8
|         |     | sum(EdgeBuckets)<n2 |     |     |     |     | 9   | EdgeBuckets[ToEvict][k]=1; |     |     |     |     |     |
| ------- | --- | ------------------- | --- | --- | --- | --- | --- | -------------------------- | --- | --- | --- | --- | --- |
| 9 while |     |                     |     |     | do  |     |     |                            |     |     |     |     |     |
IterOrder.append((ToEvict,k));
| 10  | ToEvict←−1,ToLoad←−1; |     |     |     |     |     | 10  |     |     |     |     |     |     |
| --- | --------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
if sum(EdgeBuckets[CurCol])=n then 11 if EdgeBuckets[k][ToEvict]=0 then
11
|     |     | Buf | ←Buf | −{CurCol}+{CurCol+1}; |     |     | 12  | EdgeBuckets[k][ToEvict]=1; |     |     |     |     |     |
| --- | --- | --- | ---- | --------------------- | --- | --- | --- | -------------------------- | --- | --- | --- | --- | --- |
12
|     |     | BufStates.append(Buf); |     |     |     |     | 13  | IterOrder.append((k,ToEvict)); |     |     |     |     |     |
| --- | --- | ---------------------- | --- | --- | --- | --- | --- | ------------------------------ | --- | --- | --- | --- | --- |
13
Set the covered edge buckets to 1; if EdgeBuckets[ToEvict][LoadedPar]=0 then
| 14  |     |     |     |     |     |     | 14  |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
EdgeBuckets[ToEvict][LoadedPar]=1;
| 15  |     | if  |     |     |     |     | 15  |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
sum(EdgeBuckets[CurCol][max(Buf)+1:n]) 16 IterOrder.append((ToEvict,LoadedPar));
< n-max(Buf) then 17 if EdgeBuckets[LoadedPar][ToEvict]=0 then
| 16  |     | ToEvict←max(Buf); |     |     |     |     |     | EdgeBuckets[LoadedPar][ToEvict]=1; |     |     |     |     |     |
| --- | --- | ----------------- | --- | --- | --- | --- | --- | ---------------------------------- | --- | --- | --- | --- | --- |
18
|     |     | else |     |     |     |     |     | IterOrder.append((LoadedPar,ToEvict)); |     |     |     |     |     |
| --- | --- | ---- | --- | --- | --- | --- | --- | -------------------------------------- | --- | --- | --- | --- | --- |
| 17  |     |      |     |     |     |     | 19  |                                        |     |     |     |     |     |
ToEvict←min(Buf);
| 18  |     |     |     |     |     |     | 20  | LoadedPar | ←BufStates[i+1]−BufStates[i]; |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | ----------------------------- | --- | --- | --- | --- |
CurCol←CurCol+1;
| 19  |     |     |     |     |     |     | 21 return | IterOrder |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --------- | --------- | --- | --- | --- | --- | --- |
else
20
ToEvict←id∈
21
|     |     | BufStates[−1]∩BufStates[−2] |     |     |     | and |     |     |     |     |     |     |     |
| --- | --- | --------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
id̸=CurCol;
| 22  | BeginID |     | ←   |     |     |     |     |     |     |     |     |     |     |
| --- | ------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
(Buf −{ToEvict,CurCol})+CurCol+2; | E | ≈8×10−7≥10−7 is satisfied, confirming that I/O over-
| V | 2
ToLoad← the id that covers the most edge head can be completely hidden by computation.
23
|     | buckets |      | from BeginID         |     | to BeginID−1; |     |                                                 |     |     |     |     |     |     |
| --- | ------- | ---- | -------------------- | --- | ------------- | --- | ----------------------------------------------- | --- | --- | --- | --- | --- | --- |
|     | Buf     | ←Buf | −{ToEvict}+{ToLoad}; |     |               |     |                                                 |     |     |     |     |     |     |
| 24  |         |      |                      |     |               |     | Discussion.Ourproposedorderingstrategyfocuseson |     |     |     |     |     |     |
25 BufStates.append(Buf);
|           |     |             |     |              |     |     | single-GPU | optimization, |                | which | is  | valuable | especially |
| --------- | --- | ----------- | --- | ------------ | --- | --- | ---------- | ------------- | -------------- | ----- | --- | -------- | ---------- |
| 26        | Set | the covered |     | edge buckets | to  | 1;  |            |               |                |       |     |          |            |
|           |     |             |     |              |     |     | for users  | such          | as researchers |       | and | students | who have   |
| 27 return |     | BufStates   |     |              |     |     |            |               |                |       |     |          |            |
limitedGPUresources.TheexperimentalresultsinSec-
|              |     |     |         |            |     |                 | tion 7.2         | and Table | 4         | also demonstrate |     | that         | Legend is |
| ------------ | --- | --- | ------- | ---------- | --- | --------------- | ---------------- | --------- | --------- | ---------------- | --- | ------------ | --------- |
| by Algorithm |     | 2   | ensures | that there | are | at least 2 edge |                  |           |           |                  |     |              |           |
|              |     |     |         |            |     |                 | a cost-effective |           | solution. | Extending        |     | the ordering | strat-    |
buckets for computing during partition exchange. So if egy to multi-GPU settings introduces additional chal-
| the | inequality | 2t∗|E|≥2∗ |     | P , the | I/O overhead | can be |     |     |     |     |     |     |     |
| --- | ---------- | --------- | --- | ------- | ------------ | ------ | --- | --- | --- | --- | --- | --- | --- |
n2 w+r lenges and is left to future work. In this paragraph, we
completely covered by the calculation of edge buckets. only discuss possible strategies for multi-GPU environ-
| As the | buffer | size | is M | and it | can contain | 3 partitions |     |     |     |     |     |     |     |
| ------ | ------ | ---- | ---- | ------ | ----------- | ------------ | --- | --- | --- | --- | --- | --- | --- |
mentsasapotentialdirectionforfutureresearch.Prior
in our hypothesis, P can be calculated as M and the worksupportingmulti-GPU,suchasDGL-KE[57],em-
6
| minimum |     | n can | be calculated |     | as |V|∗d∗4∗2, | where 4 de- |       |           |           |     |              |         |     |
| ------- | --- | ----- | ------------- | --- | ------------- | ----------- | ----- | --------- | --------- | --- | ------------ | ------- | --- |
|         |     |       |               |     | M/3           |             | ploys | the METIS | algorithm |     | to partition | a graph | and |
notes the bytes of a float type. Substituting P and n assign subgraphs to GPUs. As shown in Figure 7, with
| into | the inequality |     | yields | |E| | 96d2 . |     |     |     |     |     |     |     |     |
| ---- | -------------- | --- | ------ | --- | ------ | --- | --- | --- | --- | --- | --- | --- | --- |
|V|2 ≥ Mt(w+r) METISpartitioning,mostedgesresidewithindiagonal
blocks,whichalignswellwithourprefetch-awareorder-
|     |     |     |     |     |     |     | ing strategy. | Specifically, |     | each | subgraph | on  | the GPU |
| --- | --- | --- | --- | --- | --- | --- | ------------- | ------------- | --- | ---- | -------- | --- | ------- |
Theorem 3 displays the condition that I/O over- can be further partitioned by node IDs, enabling the
| head | can | be completely |     | covered | by the | computation |                 |     |             |     |                 |          |     |
| ---- | --- | ------------- | --- | ------- | ------ | ----------- | --------------- | --- | ----------- | --- | --------------- | -------- | --- |
|      |     |               |     |         |        |             | straightforward |     | application |     | of the ordering | strategy | in  |
using our prefetching strategy. Legend has the metrics Legend for diagonal blocks. The remaining partitions
of t ≈ 10−7s, w ≈ 2G/s and r ≈ 3G/s in our ex- requireaneworderingstrategythatsupportsprefetch-
perimental setting (Section 7.1). With M = 15G and ing, as the partition ID on their horizontal and vertical
d = 100, the I/O overhead can be completely covered axesisnotidentical.Anotheroptionistoonlyprefetch
bythecomputationif |E| ≥10−7.Forinstance,theTwit- partitions for diagonal blocks, which have already cov-
|V|2
ter dataset has |E| = 1.46×109 and |V| = 4.16×107 ered the majority of edges. In this way, we can achieve
(see Table 2 for detailed information). The condition partial prefetching in multi-GPU scenarios.

12 ZhonggenLietal.
Processed with Processed with new and hinders the simultaneous execution of the data ac-
ordering in Legend ordering strategy
cess kernel and computing kernel.
Other methods employ GPU-SSD direct access for
GPU 0
specificapplicationssuchasDNNandGNNtraining[1,
31].Thesemethodsleverageexistingaccessmechanisms
GPU 1 implemented in GDRCopy [28] or BaM [36], without
optimizing the underlying access mechanism specific
for the I/O patterns of various applications. For graph
GPU 2
embedding, the embeddings and optimizer states are
stored continuously in large partitions in SSD, leading
GPU 3 to redundant door ringing and locks during data ac-
cess when employing existing data access mechanisms
Fig. 7 Adjacent matrix of a large graph after applying such as BaM. To implement a lightweight yet high-
METISpartitioning[57]. throughput NVMe SSD access kernel, we analyze the
specific workload of graph embedding learning and op-
timize the direct access mechanism.
5 Optimizations on GPU Direct Access to SSD
Inthecontextofgraphembeddinglearning,embed-
dings and optimizer states are loaded from NVMe SSD
In this section, we introduce our proposed optimiza-
to the GPU buffer only after the GPU has completed
tionsfortheGPU-SSDdirectaccessmechanism,includ-
thecomputationoftheedgebucketsrelatedtothenode
ing batch enqueue, full-coalesced doorbell ringing, and
partitions in the current buffer state. The data loading
batch polling techniques. These techniques are specifi-
times are determined once Algorithm 2 provides the
cally designed for graph embedding workloads and en-
order. Additionally, the size of the embedding and op-
hance the bandwidth between the GPU and SSD.
timizer states for each node partition is fixed, allowing
Previously,accesstoNVMeSSDreliedonthekernel for sequential access page by page. Such a workload
I/O stacks of the operating system, which involve con- leads to opportunities to reduce the complexity of the
text switching, data copying, interrupts, resource syn- queue management mechanism.
chronization, etc. As the latency of storage devices de- To avoid building complex I/O stacks from scratch,
creases, the CPU software stack becomes a bottleneck similar to BaM, we implement the GPU-SSD direct ac-
for I/O access [36]. Consequently, customized NVMe cess driver based on an open-source codebase [23]. We
SSDdriverssuchasSPDKhaveemergedtomoveallof will only introduce our contributions below. To max-
the necessary operations into userspace [52], reducing imize the parallelism and the I/O throughput of the
theCPUsoftwarestack’soverhead.Recently,toachieve NVMeSSD,weemploymultipleNVMequeuesanduti-
high-performance direct access between the GPU and lize several thread blocks, with each thread block man-
NVMeSSD,researchhasshiftedtowardsoffloadingI/O agingoneNVMequeuepair.Allthreadswithinathread
tasks from the CPU and reconstructing the user-level block can enqueue and dequeue on the corresponding
I/O stack on the GPU, aiming to reduce the stacks’ queue pair. This thread block allocation strategy sim-
overhead and enhance throughput by leveraging the plifies the management of queue pairs, as synchroniza-
massive parallelism of GPU threads. tion among threads within the same block is straight-
Amongthese,BaMachievesthestate-of-the-artper- forward and has low overhead.
formance[36].However,BaMisdesignedtohandlegen- Figure 8 depicts our proposed optimized procedure
eral workloads across various scenarios, incorporating forGPUdirectaccesstoNVMeSSD.Forclarity,Figure
complex mechanisms including parallel queue manage- 8 exhibits a single thread block with a single queue. In
ment strategies, atomic operations, caching strategies, practicalimplementation,weemploymultiplequeuesto
etc. The enqueue operation is designed to be serial by maximize the bandwidth between the GPU and SSD.
atomic operations to avoid concurrency conflicts, and The key idea of our proposed GPU direct access mech-
the doorbell ringing strategy only coalesces doorbell anism is to utilize the regular embedding access char-
writesofsomethreadstoovercomecomplexread/write acteristicstoprecomputethepositionsofqueueentries
workload, leading to redundant overhead of lock and and minimize the doorbell ringing time, avoiding the
doorbell ringing for data transfer in graph embedding. use of locks and atomic operations, as well as reducing
Moreover,BaMemploysnumerousthreadblocksonthe the overhead of doorbell ringing.
GPUtoachievehighthroughputbetweentheGPUand During the command construction phase, threads
NVMe SSD, which consumes valuable GPU resources in a block construct read/write commands in parallel,

EfficientGraphEmbeddingatScale:OptimizingCPU-GPU-SSDIntegration 13
GPU NVMe SSD ing strategy is the same as the enqueue phase. How-
t t
t
0 1
m
...
d
d d
m
m m
c
c c
m
1 0 tailol t d 0 t1 SQ 0 tm tailnew t t l 0 ast Do D o M rB A ell0 L R T C eM V N e h t
a
h v e e e
b
a
a
r d d ,
tc
o t t
h
o h o r e
p
b c n
o
a e
l
a l l
l
l c ¨ı
i
. u v
n
T e l
g
a o p t
s
e r o
t
e
r
l t d l
a
i h u n
t
e
e
c g
g
e e
y
s x t t h a r
s
a c e
p
t t
e
p e
c
p g o
i
y o
fi
ll l
c
i l c n i a n g
f
u
o
g o
r
s v e p
g
s e o
r
r r s
a
h e i
p
t e d i a
h
o u d n n ,
e
s d
m
w a a
b
e n n
e
t d d
d
e o
d
s r v i i
i
e g n
n
r n g
g
-
data transfer workload. Specifically, during the polling
headoldt0
E0 S0 phase, each thread t
i
within a thread block checks the
position of head +i in the CQ, where head is the
ti RReegg.. CQ old old
atomicAdd() 0 headpointeroftheCQandidenotesthethreadID.We
tm
re
headnew
E1 S1
m
m
a
em
in
o
ta
ry
in
, w
a
h
c
ic
o
h
un
is
te
i
r
ni
f
t
o
ia
r
li
e
z
a
e
c
d
h
w
C
it
Q
h 0
in
. W
th
h
e
e
G
n
P
a
U
th
’s
re
s
a
h
d
ar
d
e
e
d
-
ffu
tectsthatanentryhasbeeninsertedbytheNVMecon-
B
troller,itatomicallyadds1tothecounterbyusingthe
Fig. 8 Procedureof the GPUdirectaccessto NVMeSSD.
atomicAdd() operation in CUDA to avoid concurrency
conflict. The last thread t to increment this counter
requesting consecutive NVMe addresses. Subsequently, last
updates the head pointer of CQ to head and rings
thesethreadsneedtoinsertthecommandsintothesub- new
thedoorbelltotransfertheupdatedpositionofthelat-
mission queue (SQ). To achieve lock-free enqueue, we
est head pointer. The atomic operation has a low cost
design a batch enqueue strategy. Each thread t inserts
i
because the counter is located in shared memory, and
its command into the position tail +i of the corre-
old
the number of threads within a block is limited. This
sponding SQ, where tail denotes the current head
old
polling strategy can not only fully utilize thread paral-
pointerandidenotesthethreadID.Thisenqueuepro-
lelism,butalsoreducetheoverheadofdoorbellringing.
cess is parallelized among threads since each thread
As the size of required embeddings and optimizer
has a unique and determined position in the SQ. The
states is determined, threads in a thread block repeat
fixedsizeofembeddingssimplifiestheenqueueprocess,
the data access procedures synchronously until all the
allowing parallel operation without the complex data
pages of embedding and optimizer states in the NVMe
structures and atomic operations in BaM for correct
SSD are loaded. This GPU direct access driver and the
enqueueing. Following the enqueue process, the tail of
embedding training kernel run simultaneously on the
SQisupdatedtotail asshowninFigure8,whichis
new
GPU by utilizing CUDA streams.
synchronized with the doorbell registers subsequently.
ThedoorbellregistersintheNVMecontrollerarewrite-
only,necessitatingserialwritingfromthreads.Further- 6 Optimizations on GPU
more, the writing overhead of doorbell registers is high
because they are located in the NVMe SSD, and the Inthissection,wedescribeouroptimizationtechniques
writing needs to be performed through PCIe. As a re- forthebatchcomputationontheGPU,whichfullyex-
sult, we design a full-coalesced doorbell ringing mecha- ploit the resources on the GPU and significantly en-
nism to reduce the high cost, where a single thread (t hance GPU utilization. Batch computation is the core
0
in Figure 8) is assigned to ring the doorbell only after processinthegraphembeddingpipeline,whichinvolves
all the threads within a thread block (t ∼ t ) have two procedures. For each batch, it first calculates the
0 m
completedtheenqueueprocess,ratherthanringingthe score f(θ ,θ ,θ ) for positive edges and f(θ ,θ ,θ )
s r d s′ r′ d′
doorbell multiple times. for sampled negative edges (see Equation 1). Then it
Oncethedoorbellrings,theNVMecontrollerfetches calculates the gradients of the loss function L (Equa-
commands from the SQ in the GPU’s global memory. tion1)fortheembeddingvalues(θ ,θ ,θ ,θ ,θ ,θ ).
s r d s′ r′ d′
The NVMe controller analyzes these commands, re- Theembeddingvaluesarefinallyupdatedbasedonthe
trieves data from the NVMe SSD, and transfers the calculated gradients.
data to the specified addresses in the GPU buffer ac- Asmentionedabove,existingsystemsoftenoverlook
cording to the commands via Direct Memory Access GPU computation optimization, leading to underuti-
(DMA).Followingthis,theNVMecontrollerinsertsan lization of the GPU. In graph embedding systems, the
entryintothecompletionqueue(CQ)correspondingto time cost can be divided into three parts: CPU pro-
the entry in the SQ. cessing, CPU-GPU communication, and GPU comput-
To wait for the completion entries in the CQ, ex- ing [56]. As some tasks on the CPU are offloaded to
isting methods employ a polling strategy, where each the GPU and CPU-GPU communication is optimized,
thread polls the CQ for the completion entry it en- the overhead of GPU computing becomes more pro-
queuesduringtheenqueuephase,andthedoorbellring- nounced. For instance, both Marius [27] and GE2 [56]

| 14  |         |              |     |     |     |              |     |     |       |               |     |           | ZhonggenLietal. |     |
| --- | ------- | ------------ | --- | --- | --- | ------------ | --- | --- | ----- | ------------- | --- | --------- | --------------- | --- |
|     |         | t t          | t   |     |     |              |     |     |       |               |     |           |                 |     |
|     |         | 0 1...       | d/2 |     |     | Destination  |     |     |       |               |     |           | Pos.            |     |
|     |         |              |     |     |     | Node         |     |     | CUDA  |               |     |           | Score           |     |
|     |         | Source Node  |     |     |     |              |     |     | Cores |               |     |           |                 |     |
|     | 16 rows |              |     |     |     | Embedding    |     |     |       |               |     |           |                 |     |
|     |         | Embedding    |     |     |     |              |     | ++  |       | Intermediate  |     | shfl_sync |                 |     |
Results 2
|     |     |            |       |     |     | Int e rm e d i ate | F r a g   | .   in   |           |     |     |     |     |     |
| --- | --- | ---------- | ----- | --- | --- | ------------------ | --------- | -------- | --------- | --- | --- | --- | --- | --- |
|     |     | t 0 t 1... | t d/2 |     | **  |                    | R e g i s | t e rs   |           |     |     |     |     |     |
|     |     |            |       |     |     | R e su l t  1      |           |          | Frag. in  |     |     |     |     |     |
Registers
|     |     |           | Relation  |     |     |             |     | ++     |     | Intermediate  |     | reduce |     |     |
| --- | --- | --------- | --------- | --- | --- | ----------- | --- | ------ | --- | ------------- | --- | ------ | --- | --- |
|     |     |           |           |     |     |             |     |        |     | Exp Results 3 |     |        |     |     |
|     |     | Embedding |           |     |     | Destination |     | Tensor |     |               |     |        |     |     |
Cores
|     |     |     |     |        |     | Negative  | Frag. in  |     |     |     |     |           |     |     |
| --- | --- | --- | --- | ------ | --- | --------- | --------- | --- | --- | --- | --- | --------- | --- | --- |
|     |     |     |     | m rows |     |           | Registers |     |     |     |     |           |     |     |
|     |     |     |     |        |     | Node      |           |     |     |     |     | exp(Neg.  |     |     |
Score)
Embedding
Fig. 9 Optimizedprocedureoftheforwardphase.
have similar GPU computing overhead because they onlyoneaccesstoeachelementforthecross-calculation
use the same GPU computing engine. However, GE2 betweenthefirstandlasthalfelementsinsomeembed-
offloads some tasks to the GPU and reduces the CPU- ding models, such as ComplEx [41], avoiding redun-
GPUcommunicationcostbycustomizedloadingorder, dant memory access. It is also suitable for other em-
whichresultsintheGPUcomputingbecomingthemost bedding models without cross-calculation. Each thread
time-consuming part (more than 1/3). In Legend, the block handles 16 rows of embeddings in a batch, as
communication overhead is further reduced due to the subsequent calculations utilize Tensor cores, which ne-
node partition loading order that minimizes the I/O cessitate a fixed input size of 16×8×16 submatrices
times as well as the support of embedding prefetching, in each thread block.
| which makes |     | GPU computing |     | the primary |     | bottleneck |     |     |     |     |     |     |     |     |
| ----------- | --- | ------------- | --- | ----------- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
of graph embedding learning. Threads within a thread block retrieve the corre-
| Different | from | the computing |     | process | of  | DNNs and |          |     |          |      |            |      |            |     |
| --------- | ---- | ------------- | --- | ------- | --- | -------- | -------- | --- | -------- | ---- | ---------- | ---- | ---------- | --- |
|           |      |               |     |         |     |          | sponding |     | elements | from | the source | node | embeddings |     |
GNNswhichdirectlyperformmatrixmultiplicationbe- (θ ) and the relation embeddings (θ ), and calculate
|               |     |              |         |     |         |         | s   |              |     |         |           | r   |              |     |
| ------------- | --- | ------------ | ------- | --- | ------- | ------- | --- | ------------ | --- | ------- | --------- | --- | ------------ | --- |
| tween weights |     | (or adjacent | matrics | of  | graphs) | and em- |     |              |     |         |           |     |              |     |
|               |     |              |         |     |         |         | the | intermediate |     | results | according | to  | the operator | ⊗   |
beddings [44,33], the computing process of graph em- definedbytheembeddingmodel.Followingthecalcula-
beddingismorecomplexasshowninEquation1,which
|     |     |     |     |     |     |     | tionofθ |     | s ⊗θ r ,weobtainIntermediateResults1,which |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------- | --- | ------------------------------------------ | --- | --- | --- | --- | --- |
involves computation between θ , θ , θ and their cor- are stored in the registers of each thread and have not
|            |          |          |     | s r     | d       |        |     |      |         |        |       |         |     |          |
| ---------- | -------- | -------- | --- | ------- | ------- | ------ | --- | ---- | ------- | ------ | ----- | ------- | --- | -------- |
| responding | negative | samples, |     | leading | to more | memory |     |      |         |        |       |         |     |          |
|            |          |          |     |         |         |        | yet | been | written | to the | GPU’s | memory. | To  | minimize |
accesstransactionsandintermediateresults.Moreover, the access times of global memory, we first use the re-
| different | graph | embedding | models | (i.e., | f   | in Equation |       |        |              |     |         |     |          |        |
| --------- | ----- | --------- | ------ | ------ | --- | ----------- | ----- | ------ | ------------ | --- | ------- | --- | -------- | ------ |
|           |       |           |        |        |     |             | sults | stored | in registers | to  | compute | the | positive | scores |
1) have distinct computing processes. For example, the before writing them to global memory. Therefore, we
| graph embedding |     | model | ComplEx | [41] | requires | cross- |       |        |           |          |          |     |              |     |
| --------------- | --- | ----- | ------- | ---- | -------- | ------ | ----- | ------ | --------- | -------- | -------- | --- | ------------ | --- |
|                 |     |       |         |      |          |        | first | employ | a similar | parallel | strategy |     | to calculate | In- |
calculationofthefirsthalfdimensionsandthelasthalf termediate Results 2 by the destination node embed-
| dimensions | of  | the embedding. |     | To optimize |     | the compu- |       |     |         |              |        |     |        |             |
| ---------- | --- | -------------- | --- | ----------- | --- | ---------- | ----- | --- | ------- | ------------ | ------ | --- | ------ | ----------- |
|            |     |                |     |             |     |            | dings | (θ  | d ) and | Intermediate | Result | 1   | (θ s ⊗ | θ r ) using |
tation for graph embedding, our key idea is to design CUDAcores,withtheequationof(θ ⊗θ )⊕θ ,where
|              |     |                        |     |     |         |           |     |     |     |     |     | s   | r   | d   |
| ------------ | --- | ---------------------- | --- | --- | ------- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
| a customized |     | parallel computational |     |     | pattern | for graph |     |     |     |     |     |     |     |     |
⊗and⊕aredefinedbytheadoptedembeddingmodel.
embeddingontheGPUtoreducememoryaccess,max- Notably,IntermediateResult2remainsstoredinregis-
imizethereuseoftheintermediateresults,andleverage
tersandisdistributedamongthreads.Tosubsequently
variousGPUresources,includingTensorcoresandreg- calculate the positive scores from Intermediate Result
| isters, to | enhance | GPU | utilization. |     |     |     |     |              |     |             |           |     |           |       |
| ---------- | ------- | --- | ------------ | --- | --- | --- | --- | ------------ | --- | ----------- | --------- | --- | --------- | ----- |
|            |         |     |              |     |     |     | 2,  | we implement |     | a two-phase | reduction |     | strategy, | which |
As illustrated in Figure 9, we horizontally split a firstreduceselementswithinthreadsineachwarpusing
batch of embeddings into several chunks, distributing the inter-thread data exchange function shfl sync(),
eachchunkacrossthreadblocksintheGPUforsimulta- and second reduces the elements within warps in each
neous computation, fully utilizing the high parallelism row.Thetwo-phasereductionstrategyleveragesshared
of the GPU. For clarity, Figure 9 depicts the comput- memory only in the second phase, thereby reducing
ing procedure of a single thread block on the GPU. memoryaccessoverhead.Duringthecalculationofpos-
Each thread block contains several warps, with ⌈d/64⌉ itive scores, global memory access only happens when
warp(s) collaborating to process one row, where d rep- the data is loaded at the beginning and the positive
resents the embedding dimension. This design allows scoresarewrittenattheend.Consequently,weimprove
the ⌈d/64⌉ warp(s) to calculate the first half of the ele- theefficiencyofpositivescorecalculationbyoptimizing
mentsinarowbeforeprocessingthelasthalf.Itleadsto computation and memory access.

EfficientGraphEmbeddingatScale:OptimizingCPU-GPU-SSDIntegration 15
| For | the efficient |     | calculation | of  | negative | scores, | we  |         |                    |     |     |     |     |     |
| --- | ------------- | --- | ----------- | --- | -------- | ------- | --- | ------- | ------------------ | --- | --- | --- | --- | --- |
|     |               |     |             |     |          |         |     | Table 2 | DetailsofDatasets. |     |     |     |     |     |
designanoptimizedkernelspecificallyformultiplication-
|                 |       |        |      |                  |         |           |     | Graphs    |     | |V| |      | |E| | |R|  | Dim. Size |
| --------------- | ----- | ------ | ---- | ---------------- | ------- | --------- | --- | --------- | --- | --- | ---- | --- | ---- | --------- |
| based embedding |       | models | such | as               | ComplEx | [41]      | and |           |     |     |      |     |      |           |
|                 |       |        |      |                  |         |           |     | FB15k(FB) |     | 15k | 592k |     | 1345 | 100 13MB  |
| DistMult        | [51], | whose  | ⊕ is | a multiplication |         | operation |     |           |     |     |      |     |      |           |
in (θ ⊗θ )⊕θ′. Normally, a source node embedding LiveJournal (LJ) 4.8M 68M - 100 3.8GB
| s   | r   | d   |     |     |     |     |     |             |     |       |       |     |     |          |
| --- | --- | --- | --- | --- | --- | --- | --- | ----------- | --- | ----- | ----- | --- | --- | -------- |
|     |     |     |     |     |     |     |     | Twitter(TW) |     | 41.6M | 1.46B |     | -   | 100 32GB |
isrequiredtoperformelement-wisemultiplicationwith
|               |             |     |                  |        |           |              |      | Freebase86M(FM) |             | 86.1M | 304.7M |              | 14824 | 100 68GB    |
| ------------- | ----------- | --- | ---------------- | ------ | --------- | ------------ | ---- | --------------- | ----------- | ----- | ------ | ------------ | ----- | ----------- |
| a group       | of negative |     | node embeddings, |        |           | followed     | by a |                 |             |       |        |              |       |             |
| reduction     | of elements |     | in each          | row to | calculate | the          | neg- |                 |             |       |        |              |       |             |
| ative scores. | Given       | the | substantial      |        | number    | of multipli- |      |                 |             |       |        |              |       |             |
|               |             |     |                  |        |           |              |      | lated works     | [57,27,56]. |       | Table  | 2 summarizes |       | their prop- |
cation operations, we utilize Tensor cores, which can erties, where FB and FM are multi-type knowledge
| execute | fixed-size | matrix | multiplications |     |     | within | a sin- |         |          |        |     |        |          |         |
| ------- | ---------- | ------ | --------------- | --- | --- | ------ | ------ | ------- | -------- | ------ | --- | ------ | -------- | ------- |
|         |            |        |                 |     |     |        |        | graphs, | while LJ | and TW | are | social | networks | without |
gleclockcycle.WeadopttheTF32datatypeformatrix relationtypes.InTable2,Dim.denotestheembedding
multiplicationinTensorcores,requiringinputmatrices
|     |     |     |     |     |     |     |     | dimension, | and Size | indicates |     | the storage |     | requirements |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | -------- | --------- | --- | ----------- | --- | ------------ |
tobesized16×8.AsshowninFigure9,ineachthread for embeddings and optimizer states. Each dataset is
| block, the | Intermediate |     | Result | 1   | contains | exactly | 16  |         |                |     |           |            |     |             |
| ---------- | ------------ | --- | ------ | --- | -------- | ------- | --- | ------- | -------------- | --- | --------- | ---------- | --- | ----------- |
|            |              |     |        |     |          |         |     | divided | into training, |     | test, and | validation |     | subsets for |
rows,facilitatinghorizontaliteration.Inathreadblock, embedding training and evaluation.
| we employ | multiple |     | warps to | iterate | over | the negative |     |           |         |     |           |        |     |             |
| --------- | -------- | --- | -------- | ------- | ---- | ------------ | --- | --------- | ------- | --- | --------- | ------ | --- | ----------- |
|           |          |     |          |         |      |              |     | Embedding | models. |     | Following | Marius |     | and GE2, on |
nodeembeddingshorizontally,witheachwarphandling
|     |     |     |     |     |     |     |     | datasets | LJ and | TW  | we employ |     | the popular | model |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | ------ | --- | --------- | --- | ----------- | ----- |
16rowsofthenegativeembeddings.Eachwarploadsa
|          |               |       |        |                    |     |          |      | Dot [19]   | as they | lack relation |     | types. | On  | FB and FM, |
| -------- | ------------- | ----- | ------ | ------------------ | --- | -------- | ---- | ---------- | ------- | ------------- | --- | ------ | --- | ---------- |
| fragment | of embeddings |       | into   | registers          | and | feeds    | them |            |         |               |     |        |     |            |
|          |               |       |        |                    |     |          |      | we utilize | ComplEx | [41].         |     |        |     |            |
| into the | Tensor        | cores | to get | the multiplication |     | results. |      |            |         |               |     |        |     |            |
Considering that we need to use the exponent results Baselinesystems.WecompareLegendwithtwostate-
of the negative scores in the loss and gradients calcu- of-the-art graph embedding systems, i.e., Marius [27]
andGE2[56],whicharedisk-basedandRAM-basedsys-
| lation, we | perform | the | exponent | operation |     | in advance |     |     |     |     |     |     |     |     |
| ---------- | ------- | --- | -------- | --------- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
in registers before writing the results to global mem- temsrespectively.Amongthetwomethods,Mariussup-
GE2
ory (Intermediate Result 3 in Figure 9), which further ports only a single GPU, while can leverage mul-
reduces redundant memory access. Finally, we employ tiple GPUs for embedding training. We exclude DGL-
the reduction API in libtorch to reduce the elements in KE [57] and PBG [18] from the comparison, as Marius
Intermediate Result 3. and GE2 have been demonstrated to outperform them.
Duringgradientcomputing,wereusetheIntermedi- To ensure a fair comparison, we maintain identical hy-
ateResult1,2,and3inFigure9toeliminateredundant perparametersacrossthethreegraphembeddinglearn-
calculations. We also apply the same parallel strategy ing systems, including a learning rate of 0.1, a batch
as in Figure 9 to compute the gradients efficiently on size of 105, 103 negative samples per positive edge, 10
the GPU, which shares a similar computing process. epochs for TW and FM, 30 epochs for FB and LJ, etc.
The parallel strategy, memory access strategy, and the As the batch size affects the efficiency and quality, fix-
105
intermediate results reusing perform collaboratively to ing batch size uniformly at and negative samples
enhance GPU utilization and enable high-performance at103 enablesa)directhardwareefficiencycomparison
| gradient | computation |     | on large | datasets. |     |     |     |                |                                        |     |              |     |        |           |
| -------- | ----------- | --- | -------- | --------- | --- | --- | --- | -------------- | -------------------------------------- | --- | ------------ | --- | ------ | --------- |
|          |             |     |          |           |     |     |     | and b) quality | differences                            |     | attributable |     | solely | to system |
|          |             |     |          |           |     |     |     | design.        | LegendandMariususe8nodepartitionswitha |     |              |     |        |           |
buffercapacityof3(12GBoftheGPUglobalmemory)
7 Experiments for TW and 12 node partitions with a buffer capacity
GE2
|     |     |     |     |     |     |     |     | of 3 (17GB | of the | GPU | global | memory) |     | for FM. |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | ------ | --- | ------ | ------- | --- | ------- |
Inthissection,weevaluatetheperformanceofourpro- uses 16 node partitions and a buffer capacity of 4 on
| posed Legend |     | and conduct |     | a comparative |     | evaluation |     |        |            |     |         |          |     |           |
| ------------ | --- | ----------- | --- | ------------- | --- | ---------- | --- | ------ | ---------- | --- | ------- | -------- | --- | --------- |
|              |     |             |     |               |     |            |     | TW and | FM because |     | it only | supports | the | number of |
with state-of-the-art graph embedding systems. Source partitions of 4L and a fixed buffer capacity of 4. This
| code of | Legend | is publicly | available |     | 2.  |     |     |               |         |        |            |     |            |            |
| ------- | ------ | ----------- | --------- | --- | --- | --- | --- | ------------- | ------- | ------ | ---------- | --- | ---------- | ---------- |
|         |        |             |           |     |     |     |     | comparison    | is fair | as the | restricted |     | support    | for flexi- |
|         |        |             |           |     |     |     |     | ble partition | numbers | is     | exactly    | the | limitation | of GE2.    |
GE2
|     |     |     |     |     |     |     |     | Nonetheless, | we  | also apply | the | order | in  | with 16 |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------ | --- | ---------- | --- | ----- | --- | ------- |
7.1 Experiment Settings partitions to Legend, as referenced in Figure 18.
|     |     |     |     |     |     |     |     | Metrics. | We employ |     | Mean | Reciprocal | Rank | (MRR) |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | --------- | --- | ---- | ---------- | ---- | ----- |
Datasets.Forcomprehensiveevaluations,weuse4da-
|     |     |     |     |     |     |     |     | and Hits@k | as the | quality | metrics, |     | which | are widely |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | ------ | ------- | -------- | --- | ----- | ---------- |
tasetswithvaryingvolumes,previouslyemployedinre-
|     |     |     |     |     |     |     |     | used to | evaluate | the embeddings |     | [35,17,56,27]. |     | Higher |
| --- | --- | --- | --- | --- | --- | --- | --- | ------- | -------- | -------------- | --- | -------------- | --- | ------ |
2 https://github.com/ZJU-DAILY/Legend MMR and Hits@k values indicate better embedding

| 16  |     |     |     |     |     |     |     |     |     |     |     |     | ZhonggenLietal. |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --------------- | --- |
1 6
|       | 0 .2 4 |           |        |       |        |        | 1     | 1 0 0 |      |          |     | 5 0 0       |     |          |
| ----- | ------ | --------- | ------ | ----- | ------ | ------ | ----- | ----- | ---- | -------- | --- | ----------- | --- | -------- |
|       |        |           |        |       |        | 1 3 .6 |       | 8 7   | 6 .0 |          |     |             |     |          |
| ) s(  | 0      | .1 7 0 .1 | 7      | ) s(  | 1 2 .2 |        | ) s(  | 8 5 0 |      |          | )   |             |     |          |
|       | 0 .1 6 |           |        |       | 1 2    |        |       |       |      |          | s(  |             |     |          |
| e     |        |           |        | e     |        |        | e     |       |      |          | e   | 4 0 0 3 8 2 | .2  |          |
| mi    |        |           |        | mi    |        |        | mi    |       |      |          |     |             |     |          |
|       |        |           |        |       |        |        |       | 6 0 0 |      |          | mi  |             |     |          |
| T     |        |           |        | T     |        |        | T     |       | 4 3  | 9 .3     | T   |             | 3 1 | 5 .5     |
| h     | 0 .0 8 |           | 0 .0 7 | h     | 8      |        | h     |       |      |          | h   |             |     |          |
| c     |        |           |        | c     |        | 7 .1   | c     |       |      |          | c   | 3 0 0       |     |          |
| o     |        |           |        | o     |        |        | o     | 3 5 0 |      |          | o   |             |     | 2 4 3 .8 |
| p     |        |           |        | p     |        |        | p     |       |      | 1 8 1 .0 | p   |             |     |          |
| E     |        |           |        | E     |        |        | E     |       |      |          | E   |             |     |          |
|       | 0 .0 0 |           |        |       | 4      |        |       |       |      |          |     |             |     |          |
|       |        |           |        |       |        |        |       | 1 0 0 |      |          |     | 2 0 0       |     |          |
M a riu s G E 2 L e g e n d M a riu s G E 2 L e g e n d M a riu s G E 2 L e g e n d M a riu s G E 2 L e g e n d
|      |                                                | (a) FB |     |     | (b)  | LJ  |      | (c) | TW  |     |     | (d)  | FM  |     |
| ---- | ---------------------------------------------- | ------ | --- | --- | ---- | --- | ---- | --- | --- | --- | --- | ---- | --- | --- |
| Fig. | 10 Comparisonoftheaverageepochtimeusingasingle |        |     |     |      |     | GPU. |     |     |     |     |      |     |     |
|      | 1 .0                                           |        |     |     | 1 .0 |     | 1    | .0  |     |     |     | 1 .0 |     |     |
0 .8 0 .8 0 .7 4 6 0 .7 3 3 0 .7 4 7 0 .8 0 .8 0 .7 3 1 0 .7 6 4
|     |           |          |              |     |      |     |     |      |      |          |     | 0 .7 2 | 5   |     |
| --- | --------- | -------- | ------------ | --- | ---- | --- | --- | ---- | ---- | -------- | --- | ------ | --- | --- |
|     | 0 .6 0 .5 | 6 1 0 .5 | 7 3 0 .5 8 1 |     | 0 .6 |     | 0   | .6   |      |          |     | 0 .6   |     |     |
| R   |           |          |              | R   |      |     | R   |      |      |          | R   |        |     |     |
|     |           |          |              |     |      |     |     | 0 .4 | 1 4  | 0 .3 9 8 |     |        |     |     |
| R   | 0 .4      |          |              | R   | 0 .4 |     | R 0 | .4   |      |          | R   | 0 .4   |     |     |
| M   |           |          |              | M   |      |     | M   |      | 0 .3 | 1 2      | M   |        |     |     |
|     | 0 .2      |          |              |     | 0 .2 |     | 0   | .2   |      |          |     | 0 .2   |     |     |
|     | 0 .0      |          |              |     | 0 .0 |     | 0   | .0   |      |          |     | 0 .0   |     |     |
M a riu s G E 2 L e g e n d M a riu s G E 2 L e g e n d M a riu s G E 2 L e g e n d M a riu s G E 2 L e g e n d
|      |                                | (a) FB   |              |     | (b)      | LJ                |       | (c)     | TW   |          |     | (d)         | FM     |          |
| ---- | ------------------------------ | -------- | ------------ | --- | -------- | ----------------- | ----- | ------- | ---- | -------- | --- | ----------- | ------ | -------- |
| Fig. | 11 ComparisonofMRRusingasingle |          |              |     | GPU.     |                   |       |         |      |          |     |             |        |          |
|      | 1 .0                           |          |              |     | 1 .0     |                   | 1     | .0      |      |          |     | 1 .0        |        |          |
|      |                                |          |              |     | 0 .8 7 9 | 0 .8 8 0 0 .8 7 9 |       |         |      |          |     |             |        |          |
|      | 0 .7                           | 9 4 0 .8 | 0 1 0 .8 0 6 |     |          |                   |       |         |      |          |     |             |        | 0 .8 2 9 |
|      | 0 .8                           |          |              |     | 0 .8     |                   | 0     | .8      |      |          |     | 0 .8 0 .7 6 | 2 0 .7 | 7 2      |
| 0    | 0 .6                           |          |              | 0   | 0 .6     |                   | 0 0   | .6 0 .5 | 7 6  | 0 .5 5 5 | 0   | 0 .6        |        |          |
| 1    |                                |          |              | 1   |          |                   | 1     |         | 0 .4 | 8 7      | 1   |             |        |          |
| @ti  | 0 .4                           |          |              | @ti | 0 .4     |                   | @ti 0 | .4      |      |          | @ti | 0 .4        |        |          |
| H    |                                |          |              | H   |          |                   | H     |         |      |          | H   |             |        |          |
|      | 0 .2                           |          |              |     | 0 .2     |                   | 0     | .2      |      |          |     | 0 .2        |        |          |
|      | 0 .0                           |          |              |     | 0 .0     |                   | 0     | .0      |      |          |     | 0 .0        |        |          |
|      |                                |          | 2            |     |          | 2                 |       |         |      | 2        |     |             |        | 2        |
M a riu s G E L e g e n d M a riu s G E L e g e n d M a riu s G E L e g e n d M a riu s G E L e g e n d
|      |                                   | (a) FB |     |     | (b) | LJ   |     | (c) | TW  |     |     | (d) | FM  |     |
| ---- | --------------------------------- | ------ | --- | --- | --- | ---- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fig. | 12 ComparisonofHit@10usingasingle |        |     |     |     | GPU. |     |     |     |     |     |     |     |     |
quality.ConsistentwithGE2,weutilizepartofthetest
|        |       |            |                      |     |        |              |     | 1 1 0 0 |        |     |     | 4 0 0 |      |        |
| ------ | ----- | ---------- | -------------------- | --- | ------ | ------------ | --- | ------- | ------ | --- | --- | ----- | ---- | ------ |
| edges  | (106) | to compute | MRR                  | and | Hit@k, | as using the |     |         |        |     |     |       |      |        |
|        |       |            |                      |     |        |              | )   | 8       | 6 4 .1 |     | )   |       |      |        |
| entire | test  | set would  | be time-prohibitive. |     |        |              | s(  | 8 5 0   |        |     | s(  |       |      |        |
|        |       |            |                      |     |        |              |     |         |        |     | e   |       | 3    | 1 5 .5 |
|        |       |            |                      |     |        |              | e   |         |        |     |     | 3 0   | 8 .7 |        |
Platforms. All experiments are conducted on a server mi 6 0 0 mi 3 0 0
|     |     |     |     |     |     |     | T   |     |     |     | T   |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
with the system of Ubuntu 20.04, featuring an Intel 4 3 9 .3 h
|      |           |        |             |          |          |               | h c |       |           |           | c     |       |         |                 |
| ---- | --------- | ------ | ----------- | -------- | -------- | ------------- | --- | ----- | --------- | --------- | ----- | ----- | ------- | --------------- |
|      |           |        |             |          |          |               | o   | 3 5 0 |           |           | o     |       |         | 2 4 3 .8        |
| Xeon | Silver    | 4216   | CPU@2.10GHz |          | with 64  | cores, Nvidia | p   |       |           |           | p     |       |         |                 |
|      |           |        |             |          |          |               | E   |       |           | 1 8 1     | .0 E  |       |         |                 |
| A100 | GPU       | (40G), | and Samsung |          | 980 NVMe | SSD (1T).     |     |       |           |           |       |       |         |                 |
|      |           |        |             |          |          |               |     | 1 0 0 |           |           |       | 2 0 0 |         |                 |
|      |           |        |             |          |          |               |     | M     | a riu s G | E 2 L e g | e n d | M a   | riu s G | E 2 L e g e n d |
| We   | implement | Legend | in          | C++/CUDA | under    | Nvidia        |     |       |           |           |       |       |         |                 |
CUDA 11.1 and LibTorch 1.7.1. Legend can be easily (a) TW (b) FM
integratedintoPytorchbypybind,butthehostrunning
Fig.13 Comparisonoftheaverageepochtimewith3/4node
| Pytorch | needs       | to  | be equipped   | with    | an NVMe | SSD and |                      |          |             |                  |               |             |         |           |
| ------- | ----------- | --- | ------------- | ------- | ------- | ------- | -------------------- | -------- | ----------- | ---------------- | ------------- | ----------- | ------- | --------- |
|         |             |     |               |         |         |         | partitionsresidingin |          |             | memoryforMarius. |               |             |         |           |
| a GPU   | supporting  |     | GPUDirect     | RDMA.   |         |         |                      |          |             |                  |               |             |         |           |
|         |             |     |               |         |         |         | tems                 | using    | a single    | GPU              | is reported   | in          | Figure  | 10. The   |
|         |             |     |               |         |         |         | time                 | reported | in          | Figure           | 10 is         | the average |         | epoch du- |
|         |             |     |               |         |         |         | ration.              | To       | demonstrate |                  | the embedding |             | quality | trained   |
| 7.2     | Comparisons |     | with Existing | Systems |         |         |                      |          |             |                  |               |             |         |           |
|         |             |     |               |         |         |         | by                   | Legend,  | we          | report           | the MRR       | and         | Hit@10  | in Fig-   |
Firstly,weevaluatetheoverallperformanceofthecom- ure 11 and Figure 12, respectively. On average, Leg-
paredsystems.Thetrainingoverheadforthethreesys- end achieves a speedup of 2.6× over Marius and 2.0×

EfficientGraphEmbeddingatScale:OptimizingCPU-GPU-SSDIntegration 17
1 .0
0 .8
0 .6
0 .4 0 1 0 .3 9 8 0 .4 0 .3 1 2
0 .2
0 .0
R
R M
1 .0
0 .8 0 .7 2 9 0 .7 3 1 0 .7 6 4
0 .6
0 .4
0 .2
0 .0
M a riu s G E 2 L e g e n d
(a) TW
R
R M
M a riu s G E 2 L e g e n d
(b) FM
Fig. 14 Comparison of MRR with 3/4 node partitions in
memoryforMarius.
1 .0
0 .8
0 .6 0 .5 6 2 0 .5 5 5 0 .4 8 7
0 .4
0 .2
0 .0
0 1
@ti
H
1 .0
0 .8 2 9 0 .8 0 .7 6 5 0 .7 7 2
0 .6
0 .4
0 .2
0 .0
M a riu s G E 2 L e g e n d
(a) TW
0 1
@ti
H
Table 3 Performance comparison with different buffer size.
Thesecondcolumnreportstheratioofbuffersizetothetotal
partitions(buffersize /totalpartitions).
Methods Ratio Epochtime MRR Hit@10
2/8 918.0s 0.418 0.579
Marius 3/8 876.2s 0.414 0.576
4/8 864.2s 0.401 0.566
3/12 230.6s 0.412 0.574
Legend 3/8 181.0s 0.398 0.555
3/6 171.4s 0.406 0.570
tribute to accelerating the training process, except for
the I/O optimization. As shown in Figure 11 and 12,
the embedding quality trained by Legend is compara-
ble with those of Marius and GE2. Moreover, on FM,
Legendexhibitsrelativelyhigherembeddingquality.As
introduced in Section 3, Legend loads the entire node
partitionsintotheglobalmemoryoftheGPUandcon-
structsbatchesontheGPU,ensuringthattheupdated
M a riu s G E 2 L e g e n d embeddings from the last batch can be used imme-
(b) FM diately in the current batch, avoiding the problem of
staleness present in Marius. This advantage is more ap-
Fig. 15 Comparison of Hit@10 with 3/4 node partitions in
parent when more nodes are in a node partition. As a
memoryforMarius.
result, Legend achieves better performance on FM in
the metrics of MRR and Hit@10.
over GE2 while maintaining similar embedding qual-
OnFM,thespeedupofLegendisrelativelyinsignif-
ity. In optimal scenarios, Legend achieves a remark-
icant, which is due to the graph properties. The num-
able speedup of 4.8× over Marius on TW and 2.4×
speedup over GE2 on TW and FB. Noted that a larger ber of edges in FM is relatively small compared to the
number of vertices, where |E| ≈ 4 × 10−8 < 10−7.
host-side buffer could further benefit Marius, we also |V|2
expandthebuffersizeforMariusto6and9ondatasets According to Theorem 3, the I/O overhead between
TW and FM, respectively. As shown in Figure 13, 14 the GPU and NVMe SSD cannot be entirely covered
and 15, with 3/4 of the partitions retained in mem- by computation. Furthermore, the I/O times can reach
ory, Marius achieves epoch times of 864.1s (876.0s with 36 even though the node partition ordering algorithm
3/8 partitions in memory) on TW and 308.7s (382.2s is applied, exacerbating the I/O overhead. In contrast,
with 3/12 partitions in memory) on FM. The improve- thetrainingspeedofLegendismoresignificantonTW.
ment is marginal for TW, where computation domi- Using the records in Table 2, | | V E | | 2 ≈ 8×10−7 > 10−7
nates,butsignificantforFM,whereI/Oistheprimary on TW, which indicates the I/O overhead can be cov-
bottleneck. Besides, the comparable MRR and Hit@10 ered by computation. Consequently, this alleviates the
with expanded buffer indicate that the buffer size has bandwidth constraints between the GPU and NVMe
no significant impact on model quality. It’s worth not- SSD, leading to improved performance.
ingthatGE2 storesembeddingsandoptimizerstatesin To evaluate the effects of various buffer sizes on
RAM,whileLegendstoresthemintheNVMeSSD.Leg- embeddingquality,weconductadditionalexperiments.
end exhibits excellent scalability and efficiency on the Considering the larger capacity of RAM compared to
four datasets with various volumes. This is attributed the GPU, we conduct the experiments with Marius and
to the optimization of each hardware component and Legend, which use the same embedding models and
the workflow that orchestrates each hardware in the negative sampling strategies. The experiments evalu-
heterogeneous system by making full use of its unique ate the model quality and epoch time using different
characteristics.Althoughthesystemsloadalldatainto buffer sizes, while holding other parameters constant.
the GPU memory without I/O overhead during em- AsshowninTable3,themodelquality(MRR&Hit@10)
bedding learning on datasets FB and LJ, Legend still and buffer size have no definite correlation, indicating
demonstrates superior training speed. This indicates that the small buffer size does not substantially hinder
that the workflow and optimizations on the GPU con- the negative sampling diversity or downstream model

18 ZhonggenLietal.
   
  
  
  
  
 
                                     
 7 U D L Q L Q J  7 L P H   V 
     Q R L W D ] L O L W 8  8 3 *
Table 4 PerformanceonvariousnumberofGPUson TW.
Systems GPU(s) MRR Hit@10 Time(s)
1 0.312 0.487 439.3(2.43×)
GE2 2 0.299 0.473 315.2(1.74×)
4 0.284 0.456 192.5(1.06×)
Legend 1 0.398 0.555 181.0
 * (2
 0 D U L X V
 / H J H Q G 4 0
3 1 .4 0 3 2 .8 0 3 0
Fig. 16 GPUutilizationofLegend,GE2 andMariusonTW. 2 0
1 2 .1 0
quality. This is because for each vertex v ∈ V in the 1 0
graph, all edges involving v are traversed within one
0
epoch. Regardless of buffer size, every node partition
containing vertices u∈V\{v} will appear in the buffer
at least once together with the partition containing v
during that epoch. Thus, each vertex in V has the op-
portunity to be paired with v as a negative sample,
ensuring the diversity of the negative sampling.
To further validate the GPU utilization improve- ments from our proposed techniques, we assess GPU
utilization on the dataset TW. Figure 16 depicts the
variation in GPU utilization across the three systems
over time. The average GPU utilization of Legend is
96.79%,comparedto60.14%forMariusand59.85%for
GE2, even with prefetching enabled. As shown in Fig-
ure 16, GPU utilization periodically drops to zero for
MariusandGE2,indicatingthattheGPUisidleduring
data loading from the disk or RAM. In contrast, GPU
utilization of Legend remains consistently above 55%,
exceeding90%formostoftheduration.Thisenhanced
utilizationcanbeattributedtothreekeyfactors.First,
we offload batch construction and negative sampling
to the GPU, which improves the batch construction
speed. Second, we prefetch the node embeddings and
optimize the bandwidth between the GPU and NVMe
SSD, which reduces the data transfer overhead and the
GPUidletime.Third,wefurtheroptimizethetraining
ontheGPUbyacustomizedparallelstrategyanddata
reuse to maximize the resource utilization of the GPU.
PleasenotethatthepartitionorderinLegenddoesn’t
support prefetching across multiple GPUs, and access-
ing data from the NVMe SSD to multiple GPUs ad-
versely affects the throughput. We leave the support
for multi-GPU graph embedding for future work. Nev-
ertheless,wecompareLegendonasingleGPUwithGE2
on multi-GPU using dataset TW. Table 4 presents the
experimental results. Legend exhibits superior perfor-
mance compared to GE2. Particularly, when GE2 em-
ploys 4 GPUs, Legend still shows comparable perfor-
mance.NotethatasthenumberofGPUsincreases,the
) s
m(
e mi
T
h
ct
a
B
2 4
1 9 .1 0 1 8 .3 0 1 8
1 2 .1 0 1 2
6
0
M a riu s G E 2 L e g e n d
(a) FB
) s
m(
e mi
T
h
ct
a
B
M a riu s G E 2 L e g e n d
(b) LJ
3 3 0
3 1 5 .6 0 3 1 5
3 0 1 8 .5 0 1 5 1 2 .0 0
0
) s
m(
e
mi T h ct a
B
3 4 5
3 3 0 3 2 6 .4 0
3 1 5
3 8 .2 0 3 0 1 3 .8 0 1 5
0
M a riu s G E 2 L e g e n d
(c) TW
) s
m(
e
mi T h ct a
B
M a riu s G E 2 L e g e n d
(d) FM
Fig. 17 Averagebatchtimeofthe comparedsystems.
time overhead of GE2 does not decrease proportionally.
This phenomenon arises from the limited I/O band-
width between host and device memory, which con-
strainsdatatransferratestomultipleGPUs.Thisissue
can be mitigated by employing the NVMe SSD as the
primary data storage device. Since the NVMe SSD is
much cheaper than RAM, it is feasible to allocate one
NVMe SSD per GPU, thereby eliminating competition
forlimitedbandwidth,whichrepresentsapromisingdi-
rection for future research, and further demonstrates
the scalability of Legend.
7.3 Evaluations of the Workflow in Legend
To demonstrate the superiority of our proposed work-
flow introduced in Section 3, we first evaluate the av-
erage batch time across the three systems. Batch time
encompasses the entire process for a batch, including
batchconstruction,batchcomputation,andembedding
updates. The results are presented in Figure 17. Leg-
end exhibits superior performance for each batch com-
pared to GE2 and Marius. On average, Legend achieves
a speedup of 2.13× and 17.18× over GE2 and Marius,

EfficientGraphEmbeddingatScale:OptimizingCPU-GPU-SSDIntegration 19
Table5 EpochtimeofLegendwithandwithoutprefetching.
3 4 0
Graphs w/oPrefetching Prefetching Speedup 2 7 6 .6
2 6 0 2 3 3 .6 2 3 5 .0 TW 235.0s 181.0s 29.83%
FM 271.2s 243.8s 11.24% 1 8 1 .0 1 8 0
respectively. Notably, GE2 exhibits higher overhead on 1 0 0
datasets FB and FM. This is because the adopted em- bedding model is ComplEx, as outlined in Section 7.1.
Thisembeddingmodelincludesmorecomplexcomput-
ing operations, which are harmful to computing effi-
ciency. In Legend, we design a generalized parallel exe-
cution strategy for graph embedding models in Section
6,significantlyenhancingtheefficiency.Adetailedanal-
ysis of our proposed optimization on GPU computing
will be discussed in Section 7.6. On datasets TW and
FM, Marius constructs batches on the CPU and subse-
quentlytransfersthemtotheGPU,resultinginconsid-
erablecommunicationoverhead.Therefore,theaverage
batch time of Marius is more than 20× over Legend on
datasetsTW andFM,asshowninFigure17(c)and(d).
In contrast, both Legend and GE2 offload the tasks of
batch construction and negative sampling to the GPU,
which achieves significant speedups.
However, the batch time reported in Figure 17 only
partially reflects the advantages of our workflow. To
conduct a comprehensive evaluation, we omit all opti-
mization modules that can be removed, including the
modules of GPU optimization, edge bucket iteration
order,andprefetchingmechanism.Theremainingcom-
ponents can completely reflect the performance of the
workflow proposed in Section 3. The epoch times on
datasetsFB,LJ,TW andFM are0.12s,13.06s,291.89s
and 331.40s, respectively. Compared with the epoch
time in Figure 10, it still exhibits superiority over Mar-
ius and GE2 on most datasets.
7.4 Prefetch-friendly Order
Prefetching is one of the key strategies that alleviates
the limited bandwidth between the NVMe SSD and
the GPU in Legend. To evaluate the effectiveness of
prefetching,wecomparetheperformanceofLegendwith
and without prefetching on TW and FM. The results
are reported in Table 5. Legend benefits more from
prefetchingonTW thanonFM,whichcanbeattributed
to the properties of the graphs. As calculated in sub-
section 7.2, |E| ≈ 4 × 10−8 for FM while |E| ≈
|V|2 |V|2
8×10−7 for TW. The sparsity of FM results in an in-
complete covering of I/O overhead, leading to reduced
benefits from prefetching. Nonetheless, prefetching re-
mainseffectiveonFM,demonstratingthescalabilityof
)s(
e
mi T h c
o p
E
3 4 0
3 1 4 .2
3 0 0
2 7 3 .8 2 7 1 .2
2 6 0 2 4 3 .8
2 2 0
1 8 0
B E T A C O V E R L ege /o n d Pre.) L egend
(w
(a) TW
)s(
e
mi T h c
o p
E
B E T A C O V E R L ege /o n d Pre.) L egend
(w
(b) FM
Fig. 18 Epoch time of replacing the edge buckets iterating
order in Legend with BETA and COVER. Legend (w/o Pre.)
denotes the epoch time that computing edge buckets using
theorderproducedby Legendbutwithoutprefetching.
the prefetching strategy in Legend. Moreover, the edge
distribution of real-world graph datasets such as TW
andFM isalwaysskewed,andthedegreeisinapower-
law distribution, which is not friendly to the prefetch-
ingstrategy.Eventhoughinthisscenario,theresultsin
Table 5 demonstrate the effectiveness of the prefetch-
ingstrategy,asitcansignificantlyreducethecomputa-
tionandI/Ooverheadfordenseedgebuckets.Notably,
while Legend achieves an overall speedup of 4.8×, the
prefetching gain of 29.8% on TW highlights that its
breakthrough primarily stems from architectural inno-
vations. Specifically, direct GPU-SSD access and com-
putational optimization contribute more substantially
to the performance improvement, whereas prefetching
serves as a complementary optimization.
Next, we compare the I/O order algorithms pro-
posedinthestate-of-the-artsystemsbyapplyingtheor-
derusedinMariusnamedBETA,andtheorderproposed
in GE2 named COVER to Legend to demonstrate the
effectiveness of our prefetch-friendly order. Using the
same settings as in subsection 7.2, BETA and COVER
divide the node embeddings into 8 and 16 partitions
for TW, and into 12 and 16 partitions for FM. BETA
has the buffer capacity of 3, while COVER has a buffer
capacityof4.TheresultsaresummarizedinFigure18.
Recall that the prefetch-friendly order generating algo-
rithmaimstogenerateanorderthatsupportsprefetch-
ing while minimizing I/O times. A comparison among
BETA,COVER,andLegendwithoutprefetchingreveals
thecomparableI/OoverheadbetweenLegend(w/oPre.)
and BETA, which highlights the I/O efficiency of our
proposed order. Although BETA has I/O times close to
thetheoreticallowerbound,itsdesignisnotconducive
toprefetching,asdiscussedinSection4.Incontrast,the
ordering algorithm used in Legend exhibits similar I/O
overhead while supporting effective prefetching. Addi-
tionally, COVER used in GE2 has higher I/O overhead

20 ZhonggenLietal.
Table 6 I/O times and communication volume of different
1 1
orderingalgorithmswithvariousnumbersofpartitions.Sde-
1 0 .0 notesthesize ofnodeembeddings andoptimizerstates. 1 0
I/Otimes Communicationvolume 3 .1 3 .3
Par. 3 2 .5
BETA COVER Legend BETA COVER Legend
2 6 8 - 8 1.33S - 1.33S 1 8 15 - 16 1.88S - 2S
0
10 24 - 24 2.4S - 2.4S 12 34 - 36 2.83S - 3S
14 48 - 50 3.43S - 3.57S
16 63 80 66 3.94S 5S 4.13S
whenappliedtoLegend.Thisisbecauseitisspecifically
designed for training with multiple GPUs, which is not
optimized for single-GPU scenarios.
To further analyze the superiority of our proposed
node partition loading order, we summarize the I/O
times (counts of partition transfers) between the stor-
age and the computing device, and calculate the com-
munication volume for the three ordering algorithms
in Table 6. The communication volume uses the same
units as the partition size S. Since COVER can only
accommodate partition numbers of 4L, we report its
metrics when the number of partitions is 16. As shown
in Table 6, BETA and Legend have similar I/O times
and communication volumes within the evaluated par-
titions.Thisindicatesthatourproposedpartitionload-
ing order achieves comparable I/O times with BETA,
whichhasI/Otimesclosetothetheoreticallowerbound.
However, BETA does not support embedding prefetch-
ing as illustrated in Section 4. In contrast, the loading
order proposed in Legend supports efficient embedding
prefetching while achieving low I/O times. Addition-
ally, COVER is adopted by GE2 to overcome the issue
of I/O overhead within multiple GPUs. It is not op-
timized for a single GPU. In contrast, the communi-
cation volume remains unchanged with the increasing
number of GPUs. Devising a prefetching-friendly and
low-overhead ordering algorithm that supports multi-
ple GPUs like COVER is left to future work.
7.5 GPU Direct Access to NVMe SSD
As discussed in Section 5, we aim to design a GPU di-
rect access strategy to NVMe SSD that achieves high
performance as well as supports the simultaneous ex-
ecution of data access and batch calculation kernels.
To this end, we separately evaluate the bandwidth of
read/write and the ability to simultaneously execute
together with the calculation kernel.
We first compare the bandwidth of Legend with the
state-of-the-artGPUdirectaccessmethodnamedBaM.
Moreover, we also evaluate the bandwidth between the
)s/
B
G(
ht
di
w d n a B
1 3
1 1 .9 1 2
2 .2 2 .2
2 1 .6
1
0
B aM
B aM
(light)
L
egend
(C
G
P
E
U
2 -G PU )
(a) Read
)s/
B
G(
ht
di
w d n a B
B aM
B aM
(light)
L
egend
(C
G
P
E
U
2 -G PU )
(b) Write
Fig.19 BandwidthofGPUdirectaccesstoSSDontestdata
with volume of 128GB. GE2 is reported as the bandwidth
betweenCPUandGPU.
Data access kernel
d Gradient computing kernel n
e
g e
L
1.10s1.31s
M
a B
0s 0.22s 0.32s 0.66s 1.30s 2.06s Timeline
Fig. 20 Timelineofsimultaneousexecutionofkernels.
CPU and GPU achieved by GE2. For our evaluation,
the test data volume is set to 128 GB. We employ
4096threadblocksforBaM,eachcontaining32threads,
while for Legend, we employ 8 thread blocks, each con-
taining 32 threads. We also evaluate BaM with the
same settings as Legend, referred to as BaM (light).
As presented in Figure 19, Legend achieves compara-
ble I/O bandwidth to BaM. Notably, the writing band-
width of Legend outperforms BaM due to its high par-
allelqueuemanagementmechanismandlow-costdoor-
bell ringing strategy. Under the same settings, Legend
achieves higher I/O bandwidth than BaM (light). This
is because we propose a lightweight NVMe SSD driver
inSection5,whichutilizesfewerresourcesontheGPU
whileachievingbetterperformance.Theresultsdemon-
stratetheeffectivenessofournovelstrategies—lock-free
batch enqueuing, fully coalesced doorbell writes, and
batch polling, avoiding the complex locks and doorbell
operations in typical GPU-SSD direct access drivers.
For GE2, the communication bandwidth between the
CPUandGPUisover3timeshigherthanthatbetween
the GPU and NVMe SSD. This gap can be mitigated
by carefully prefetching data, as demonstrated in our
previous experiments.
To evaluate the capability of the GPU-SSD direct
data access kernel to execute concurrently with the
batch computing kernel, we run both kernels simulta-
neously by using CUDA streams. For the batch com-

EfficientGraphEmbeddingatScale:OptimizingCPU-GPU-SSDIntegration 21
4 0
3 0 2 4 .1 0 2 1 .6 0
2 0
1 0 .2 0 1 0
0
) s m(
e mi
T n
oit al
u
cl
a C
2 4
1 8 1 5 .6 0 1 6 .6 0
1 2 1 0 .5 0
6
0 M a riu s G E 2 L e g e n d
(a) FB
) s m(
e mi
T n
oit al
u
cl
a C M a riu s G E 2 L e g e n d
(b) LJ
2 4
1 8 1 6 .0 0 1 6 .3 0
1 2 1 0 .5 0 6
0
)
s
m(
e
mi
T n oit al u cl
a C
3 6
2 7 .3 0
2 7 2 5 .4 0
1 8 1 0 .4 0 9
0 M a riu s G E 2 L e g e n d
(c) TW
)
s
m(
e
mi
T n oit al u cl
a C
1 0 0
9 3 M ariu s 8 0 8 4 8 1 G E 2
L eg en d 6 0 5 7 5 5 5 9
5 1 4 3
4 0 3 1
2 0
4 0 1 0 0 0 0
M a riu s G E 2 L e g e n d
(d) FM
Fig. 21 Comparison of the average batch calculation time
forasinglebatch.
puting kernel, we fix the batch size at 105 and execute
the batch computation 100 times. The execution time-
lines are depicted in Figure 20. In Legend, both ker-
nelscanbeexecutedconcurrentlywithminimalperfor-
mance degradation. In contrast, the data access kernel
inBaMoccupiesasignificantamountofresources,seri-
ously affecting the execution performance of the batch
computingkernel.Byconsideringthespecificworkload
of graph embedding learning, we have simplified the
complexity of the GPU-SSD direct access driver and
designed novel direct access strategies, resulting in a
lightweight but high-performance GPU-NVMe SSD di-
rect access kernel.
7.6 Optimizations on the GPU
In this subsection, we evaluate the optimization tech-
niques applied to GPU computing, as proposed in Sec-
tion 6. To achieve this, we measure the average cal-
culation time per batch. The results are reported in
Figure 21. Marius and GE2 exhibit similar performance
across the four datasets, as they utilize the same train-
ing engine. The training overhead for both systems on
FB and FM is greater compared to LJ and TW. This
discrepancy arises because these datasets are different
types of graphs and employ distinct embedding mod-
els, as discussed in subsection 7.1. Specifically, FB and
FM areknowledgegraphswithmultipletypesofedges,
whichuseComplExmodel.Thesemethodscalculateem-
beddings of edges while LJ and TW don’t. Moreover,
the computing process of ComplEx involves cross cal-
) %(
n oitr
o p
or
P
(cid:7)(cid:1)(cid:6)(cid:3)(cid:2) (cid:7)(cid:1)(cid:6)(cid:4)(cid:2) (cid:7)(cid:1)(cid:6)(cid:5)(cid:2) (cid:7)(cid:1)(cid:6)(cid:6)(cid:2) = 1 0 0 %
U tiliz a tio n R a n g e
Fig. 22 Statistical information on the GPU utilization of
graph embedding systems during training on TW. The uti-
lizationofMariusremainsbelow95%.
1 6 1 2 .2 4 1 2 1 0 .1 3
8
4 .0 2 4
0
) s( e mi
T g nit
u p
m
o
C
1 6 1 4 .2 7 1 2 .6 2 1 2
8 5 .3 8
4
0
M a riu s G E 2 L e g e n d
(a) Dim=50
) s( e mi
T g nit
u p
m
o
C
M a riu s G E 2 L e g e n d
(b) Dim=100
2 0
1 6 .3 8
1 4 .7 4
1 5
1 0 8 .7 7
5
0
) s(
e
mi
T
g
nit
u
p
m
o
C
2 0
1 7 .7 6
1 6 .6 2
1 5
1 0 8 .4 8
5
0
M a riu s G E 2 L e g e n d
(c) Dim=150
) s(
e
mi
T
g
nit
u
p
m
o
C
M a riu s G E 2 L e g e n d
(d) Dim=200
Fig. 23 Comparison of the batch computing overhead with
variousembeddingdimensionsinthebatchsizeof50000using
theComplExembedding modelonFB.
culation, which is more complex and leads to higher
overhead. In Legend, we combine the batch calculation
processes for edge embeddings with those of node em-
beddings, eliminating redundant calculation. We also
deviseageneralizedparallelstrategytofullyutilizethe
computingandstorageresourcesontheGPU.Asacon-
sequence, the calculation overhead remains consistent
across the 4 datasets.
On LJ and TW, Legend achieves a speedup ratio of
1.5×-1.6×, while the speedup exceeds 2× on FB and
FM. This indicates that the parallel strategy and in-
termediate results reuse techniques proposed in Sec-
tion 6 are effective. Furthermore, we conduct statis-
tics on the GPU utilization of each graph embedding
system during the training process. As shown in Fig-
ure 22, the GPU utilization for Legend remains above
98% for 81.22% of the time, above 99% for 59% of

| 22  |     |     |     |     |     |     |     |     |     |     |     | ZhonggenLietal. |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --------------- | --- |
the time, and reaches 100% for 31.49% of the time. entities’ semantics. These multi-relation graph embed-
Incontrast,the proportionsoftimeduringwhichGPU ding models can be easily integrated into Legend.
| utilization | exceeds | 98%, | 99%, | and | 100% | for GE2 are |       |           |     |          |             |     |              |
| ----------- | ------- | ---- | ---- | --- | ---- | ----------- | ----- | --------- | --- | -------- | ----------- | --- | ------------ |
|             |         |      |      |     |      |             | Graph | embedding |     | systems. | Significant |     | efforts have |
51.48%,43.28%,and3.64%,respectively.Thus,theop- beendedicatedtodevelopingefficientsystemsforgraph
timizationoftrainingontheGPUsignificantlyimproves
embeddingtraining.GraphVite[62]employstheCPUto
GPU utilization, leading to a substantial reduction in generate random walks and sample negative edges on
| calculation | overhead. |     |     |     |     |     |         |         |           |     |           |          |         |
| ----------- | --------- | --- | --- | --- | --- | --- | ------- | ------- | --------- | --- | --------- | -------- | ------- |
|             |           |     |     |     |     |     | GPUs to | achieve | efficient |     | embedding | learning | on gen- |
Furthermore,toevaluatethescalabilityofthethree eral graphs. HET-KE [4] proposes a cache embedding
| graph embedding |     | systems | with | varying | embedding | di- |     |     |     |     |     |     |     |
| --------------- | --- | ------- | ---- | ------- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
tabletoreducethecommunicationoverheadamongdis-
mensions, we conduct experiments using ComplEx em- tributedmachines.DistGER[6]proposesanefficientdis-
beddingmodelwithabatchsizeof50000bysettingthe
|     |     |     |     |     |     |     | tributed | graph | embedding |     | system. | For massive | knowl- |
| --- | --- | --- | --- | --- | --- | --- | -------- | ----- | --------- | --- | ------- | ----------- | ------ |
embeddingdimensionto50,100,150,and200.Theexe- edgegraphs,PBG[18]proposesabatchednegativesam-
cutionoverheadsofthethreegraphembeddingsystems
|     |     |     |     |     |     |     | pling method |     | to reduce | memory | access | overhead. | DGL- |
| --- | --- | --- | --- | --- | --- | --- | ------------ | --- | --------- | ------ | ------ | --------- | ---- |
are depicted in Figure 23. Legend consistently outper- KE [57] overlaps the gradient update with batch pro-
| forms the | other | graph embedding |     | systems |     | with various |         |           |     |      |       |          |             |
| --------- | ----- | --------------- | --- | ------- | --- | ------------ | ------- | --------- | --- | ---- | ----- | -------- | ----------- |
|           |       |                 |     |         |     |              | cessing | to reduce | GPU | idle | time. | Kochsiek | et al. pro- |
embedding dimensions. It achieves a speedup ratio of videacomprehensiveexperimentalstudyoftheexisting
| 2.13× over | GE2 | and 2.42× | over | Marius, | which | demon- |           |       |           |     |          |            |       |
| ---------- | --- | --------- | ---- | ------- | ----- | ------ | --------- | ----- | --------- | --- | -------- | ---------- | ----- |
|            |     |           |      |         |       |        | knowledge | graph | embedding |     | training | techniques | [17]. |
strates the computational scalability of our proposed Following PBG, Marius [27] proposes a partition load-
| Legend | with various | embedding |     | dimensions. |     | The supe- |           |      |           |     |         |       |               |
| ------ | ------------ | --------- | --- | ----------- | --- | --------- | --------- | ---- | --------- | --- | ------- | ----- | ------------- |
|        |              |           |     |             |     |           | ing order | BETA | to reduce |     | the I/O | times | and pipelines |
rior performance of Legend is attributed to the opti- the training procedure on the CPU and GPU. GE2 [56]
mizationsofparallelstrategy,memoryaccess,andcom-
|     |     |     |     |     |     |     | designs | a general | negative |     | sampling | execution | model, |
| --- | --- | --- | --- | --- | --- | --- | ------- | --------- | -------- | --- | -------- | --------- | ------ |
puting process in Section 6. When the embedding di- and proposes a loading order to reduce I/O overhead
| mension | is 150, | the computing |     | overhead |     | of Legend is |     |     |     |     |     |     |     |
| ------- | ------- | ------------- | --- | -------- | --- | ------------ | --- | --- | --- | --- | --- | --- | --- |
betweenRAMandGPUs.Differentfromthem,ourpro-
similar to that when the dimension is 200. This is at- posedgraphembeddingsystem,Legend,employsGPU-
| tributed | to the | warp scheduling |     | model | of  | the GPU, |            |        |     |                   |     |       |          |
| -------- | ------ | --------------- | --- | ----- | --- | -------- | ---------- | ------ | --- | ----------------- | --- | ----- | -------- |
|          |        |                 |     |       |     |          | SSD direct | access | and | prefetch-friendly |     | order | to opti- |
where a small number of warps can be scheduled to mize the I/O efficiency, while utilizing a customized
| execute | concurrently | on  | a single | SM. |     |     |                     |     |          |     |           |             |      |
| ------- | ------------ | --- | -------- | --- | --- | --- | ------------------- | --- | -------- | --- | --------- | ----------- | ---- |
|         |              |     |          |     |     |     | GPU kernel          | to  | optimize | the | computing | efficiency. | Leg- |
|         |              |     |          |     |     |     | end is specifically |     | designed |     | for graph | embedding,  | but  |
8 Related Work the framework also has the potential to be adopted in
otherareassuchasout-of-coreGNNtraining[31],DNN
Graph embedding models. Extensive studies have training[1],andlarge-scalevectorsearch[15]withcus-
tomized optimizations.
beenconductedtoenhancethequalityofgraphembed-
dings. For general graphs, existing algorithms typically GPUdirectaccesstoNVMeSSD.Recentresearch
sampleedgesbasedonrandomwalks[38,42].Forexam- has studied the GPU-SSD direct access to meet the
ple, DeepWalk [34] employs the idea of Word2Vec [26], demand for low latency and large capacity. GPUDi-
generating a series of random walk paths and training rect Storage (GDS) [29] is a library supporting data
the embedding by the skip-gram model. Node2Vec [11] transmission between GPU and NVMe SSD through
improves DeepWalk, which balances the embedding re- a bounce buffer in the CPU’s memory and a direct
sultsbetweenhomogeneityandstructureofthenetwork memoryaccess(DMA)engine.However,GDSisstillre-
by adjusting the weights of random walks. LINE [40] stricted by the high-overhead software stacks. To com-
defines first-order and second-order similarity on the pletely break free from the limitations of the Linux
graph to constrain the learning of embeddings. In the software stacks, BaM [36] proposes a queue manage-
context of multi-relation graphs, all edges in the graph ment mechanism and caching strategy completely on
are used for embedding learning without sampling [18, the GPU to achieve high-throughput access to storage.
57,27,56]. Extensive multi-relation graph embedding There are also various customized GPU direct access
models have been developed, categorized into two pri- methods for specific applications such as DNN train-
marytypes:translationaldistancemodelsandsemantic ing[1],GNNtraining[31],vectorretrieval[15],anddata
matching models [43]. Translational distance models, analysis in OLAP [20]. These methods simply adopt
such as TransE [2] and TransH [47], employ distance- a GPU-SSD direct access library without optimizing
based scoring functions to evaluate the plausibility of the underlying access mechanism. The graph embed-
factsbetweenentities.Semanticmatchingmodels,such ding workflow has its specific I/O pattern as discussed
as DistMult [51] and ComplEx [41], utilize similarity- in Section 5. To maximize the bandwidth between the
based scoring functions to assess plausibility based on GPU and SSD during graph embedding, Legend cus-

EfficientGraphEmbeddingatScale:OptimizingCPU-GPU-SSDIntegration 23
| tomizes | the queue | management, |     | doorbell |     | ringing, and |       |          |         |      |        |           |     |       |
| ------- | --------- | ----------- | --- | -------- | --- | ------------ | ----- | -------- | ------- | ---- | ------ | --------- | --- | ----- |
|         |           |             |     |          |     |              | batch | training | of very | deep | neural | networks. | In: | FAST, |
pollingmechanismfortheGPU-SSDdirectaccessdriver pp.387–401(2021)
according to the graph embedding workload, signifi- 2. Bordes, A., Usunier, N., Garcia-Duran, A., Weston, J.,
|                 |     |     |             |           |     |     | Yakhnenko,       |     | O.: Translating |                           | embeddings |     | for modeling |     |
| --------------- | --- | --- | ----------- | --------- | --- | --- | ---------------- | --- | --------------- | ------------------------- | ---------- | --- | ------------ | --- |
| cantly reducing |     | the | data access | overhead. |     |     |                  |     |                 |                           |            |     |              |     |
|                 |     |     |             |           |     |     | multi-relational |     | data.           | NeurIPS26,2787–2795(2013) |            |     |              |     |
SpecializedGPUkernelsforgraphlearning.Com-
|     |     |     |     |     |     |     | 3. Cao, | J., Sen, | R., Interlandi, |     | M., | Arulraj, | J., Kim, | H.: |
| --- | --- | --- | --- | --- | --- | --- | ------- | -------- | --------------- | --- | --- | -------- | -------- | --- |
putational overhead is always a primary challenge for Gpudatabasesystemscharacterizationandoptimization.
graph learning. To tackle this challenge, recent stud- PVLDB17(3),441–454(2023)
4. Dong,S.,Miao,X.,Liu,P.,Wang,X.,Cui,B.,Li,J.:Het-
| ies have | designed | custom |     | GPU kernels | for | each mod- |     |     |     |     |     |     |     |     |
| -------- | -------- | ------ | --- | ----------- | --- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
kg:Communication-efficientknowledgegraphembedding
| ule in graph    | learning. |              | To  | achieve efficient |          | graph sam- |            |     |               |     |        |           |     |       |
| --------------- | --------- | ------------ | --- | ----------------- | -------- | ---------- | ---------- | --- | ------------- | --- | ------ | --------- | --- | ----- |
|                 |           |              |     |                   |          |            | training   | via | hotness-aware |     | cache. | In: ICDE, | pp. | 1754– |
| pling, gSamlper |           | [9] proposes |     | efficient         | sampling | kernels    | 1766(2022) |     |               |     |        |           |     |       |
withoperatorfusion,whileFlowWalker[24]implements 5. Edge, D., Trinh, H., Cheng, N., Bradley, J., Chao,
|     |     |     |     |     |     |     | A., Mody, |     | A., Truitt, | S., | Metropolitansky, |     | D., | Ness, |
| --- | --- | --- | --- | --- | --- | --- | --------- | --- | ----------- | --- | ---------------- | --- | --- | ----- |
asamplingkernelframeworkwithmemory-efficientop-
|              |         |     |         |           |     |              | R.O.,  | Larson,          | J.: From | local          | to global: | A   | graph          | rag ap- |
| ------------ | ------- | --- | ------- | --------- | --- | ------------ | ------ | ---------------- | -------- | -------------- | ---------- | --- | -------------- | ------- |
| timizations. | Another |     | general | operation | in  | graph learn- |        |                  |          |                |            |     |                |         |
|              |         |     |         |           |     |              | proach | to query-focused |          | summarization. |            |     | arXiv preprint |         |
ing is SDDMM/SpMM. FusedMM [37] design a uni- arXiv:2404.16130(2024)
fied SDDMM-SpMM kernel to avoid redundant inter- 6. Fang, P., Khan, A., Luo, S., Wang, F., Feng, D., Li,
|         |          |        |     |              |        |          | Z., Yin,                             | W., | Cao, | Y.: Distributed |     | graph | embedding   |     |
| ------- | -------- | ------ | --- | ------------ | ------ | -------- | ------------------------------------ | --- | ---- | --------------- | --- | ----- | ----------- | --- |
| mediate | results. | TC-GNN |     | [46] employs | Tensor | cores to |                                      |     |      |                 |     |       |             |     |
|         |          |        |     |              |        |          | withinformation-orientedrandomwalks. |     |      |                 |     |       | PVLDB16(7), |     |
achievemoreefficientSpMMongraphs.Moreover,HC-
1643–1656(2023)
SpMM [22] proposes a hybrid CUDA-Tensor kernel to 7. Fang, X., Zhang, F., Nong, J., Zhang, M., Hu, P., Chai,
fully utilize the heterogeneous GPU cores. GNN, as a Y., Du, X.: Enabling efficient nvm-based text analytics
|         |           |     |          |           |     |           | withoutdecompression. |     |     | In:ICDE,pp.3725–3738(2024) |     |     |     |     |
| ------- | --------- | --- | -------- | --------- | --- | --------- | --------------------- | --- | --- | -------------------------- | --- | --- | --- | --- |
| primary | framework |     | in graph | learning, | has | also been |                       |     |     |                            |     |     |     |     |
8. Fang,Y.,Yang,Y.,Zhang,W.,Lin,X.,Cao,X.:Effective
| studied | to design | specialized |     | GPU | kernels. | GNNAdvi- |               |     |           |        |      |       |               |     |
| ------- | --------- | ----------- | --- | --- | -------- | -------- | ------------- | --- | --------- | ------ | ---- | ----- | ------------- | --- |
|         |           |             |     |     |          |          | and efficient |     | community | search | over | large | heterogeneous |     |
sor [45] designs GPU kernels specially for GNN work- informationnetworks. PVLDB13(6),854–867(2020)
load to improve memory access and GPU utilization. 9. Gong, P., Liu, R., Mao, Z., Cai, Z., Yan, X., Li, C.,
|     |     |     |     |     |     |     | Wang, | M., | Li, Z.: gsampler: |     | General | and | efficient | gpu- |
| --- | --- | --- | --- | --- | --- | --- | ----- | --- | ----------------- | --- | ------- | --- | --------- | ---- |
PruneGNN[12]proposesSIMD-awarekernelstoexploit
|     |     |     |     |     |     |     | based | graph | sampling | for graph | learning. |     | In: SOSP, | pp. |
| --- | --- | --- | --- | --- | --- | --- | ----- | ----- | -------- | --------- | --------- | --- | --------- | --- |
matrix-operator-levelparallelism.Thegraphembedding
562–578(2023)
models, such as DistMult, have a different computing 10. Gordon, D.M., Patashnik, O., Kuperberg, G.: New con-
paradigm from graph sampling and SpMM. Legend de- structionsforcoveringdesigns. JournalofCombinatorial
Designs3(4),269–284(1995)
signsanoptimizedGPUkerneltoenhancethecomput-
11. Grover,A.,Leskovec,J.:node2vec:Scalablefeaturelearn-
| ing efficiency |     | of these | models. |     |     |     |                 |     |            |            |                        |        |       |       |
| -------------- | --- | -------- | ------- | --- | --- | --- | --------------- | --- | ---------- | ---------- | ---------------------- | ------ | ----- | ----- |
|                |     |          |         |     |     |     | ingfornetworks. |     | In:SIGKDD, |            | pp.855–864(2016)       |        |       |       |
|                |     |          |         |     |     |     | 12. Gurevin,    | D., | Shan,      | M., Huang, | S.,                    | Hasan, | M.A., | Ding, |
|                |     |          |         |     |     |     | C., Khan,       | O.: | Prunegnn:  |            | Algorithm-architecture |        |       | prun- |
9 Conclusion
|     |     |     |     |     |     |     | ingframeworkforgraphneuralnetworkacceleration. |     |     |     |     |     |     | In: |
| --- | --- | --- | --- | --- | --- | --- | ---------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
HPCA,pp.108–123(2024)
We introduce Legend, a lightweight graph embedding 13. Haas, G., Leis, V.: What modern nvme storage can do,
|          |        |                |     |               |     |               | and         | how to | exploit | it: high-performance |       |        | i/o for   | high- |
| -------- | ------ | -------------- | --- | ------------- | --- | ------------- | ----------- | ------ | ------- | -------------------- | ----- | ------ | --------- | ----- |
| system.  | Legend | systematically |     | integrates    |     | CPU, GPU,     |             |        |         |                      |       |        |           |       |
|          |        |                |     |               |     |               | performance |        | storage | engines.             | PVLDB | 16(9), | 2090–2102 |       |
| and NVMe | SSD    | resources,     |     | which perform |     | efficient and |             |        |         |                      |       |        |           |       |
(2023)
scalable embedding training. We carefully design the 14. He, Y., Zhang, Y., Gurukar, S., Parthasarathy, S.: Web-
workflowtoenableaseamlessintroductionoftheNVMe mile: democratizing network representation learning at
|          |     |        |     |            |       |              | scale.     | PVLDB15(12)(2022) |          |      |           |     |         |       |
| -------- | --- | ------ | --- | ---------- | ----- | ------------ | ---------- | ----------------- | -------- | ---- | --------- | --- | ------- | ----- |
| SSD into | the | system | and | distribute | tasks | according to |            |                   |          |      |           |     |         |       |
|          |     |        |     |            |       |              | 15. Huang, | Y.,               | Fan, X., | Yan, | S., Weng, | C.: | Neos: A | nvme- |
theuniquecharacteristicsofeachhardwarecomponent.
|            |     |        |     |             |           |       | gpusdirectvectorservicebufferinuserspace. |     |     |     |     |     | In:ICDE, |     |
| ---------- | --- | ------ | --- | ----------- | --------- | ----- | ----------------------------------------- | --- | --- | --- | --- | --- | -------- | --- |
| Meanwhile, | we  | design | an  | edge bucket | iteration | order |                                           |     |     |     |     |     |          |     |
pp.3767–3781(2024)
that minimizes the I/O times between GPU and SSD 16. Kim,J.,Guo,T.,Feng,K.,Cong,G.,Khan,A.,Choud-
whilesupportingefficientprefetching,andacustomized hury,F.M.:Denselyconnectedusercommunityandloca-
|         |        |        |        |                  |     |        | tion | cluster | search in | location-based |     | social | networks. | In: |
| ------- | ------ | ------ | ------ | ---------------- | --- | ------ | ---- | ------- | --------- | -------------- | --- | ------ | --------- | --- |
| GPU-SSD | direct | access | driver | to significantly |     | reduce |      |         |           |                |     |        |           |     |
SIGMOD,pp.2199–2209(2020)
I/Ooverhead.Furthermore,weproposeanefficientpar-
17. Kochsiek,A.,Gemulla,R.:Paralleltrainingofknowledge
allel strategy for graph embedding workload to opti- graph embedding models: a comparison of techniques.
mize the computation on the GPU, ensuring efficient PVLDB15(3),633–645(2021)
|              |                  |     |           |              |     |         | 18. Lerer,                                   | A., Wu,           | L., Shen, | J., | Lacroix,             | T.,      | Wehrstedt,  | L.,     |
| ------------ | ---------------- | --- | --------- | ------------ | --- | ------- | -------------------------------------------- | ----------------- | --------- | --- | -------------------- | -------- | ----------- | ------- |
| handling     | of billion-scale |     | datasets. | Experimental |     | results |                                              |                   |           |     |                      |          |             |         |
|              |                  |     |           |              |     |         | Bose,                                        | A., Peysakhovich, |           | A.: | Pytorch-biggraph:    |          |             | A large |
| consistently | demonstrate      |     | the       | superiority  | of  | Legend. |                                              |                   |           |     |                      |          |             |         |
|              |                  |     |           |              |     |         | scalegraphembeddingsystem.                   |                   |           |     | MLSys1,120–131(2019) |          |             |         |
|              |                  |     |           |              |     |         | 19. Leskovec,                                |                   | J.:       |     | Tutorial:            |          | Representa- |         |
|              |                  |     |           |              |     |         | tion                                         | learning          |           | on  |                      | networks |             | (2018). |
| References   |                  |     |           |              |     |         | Http://snap.stanford.edu/proj/embeddings-www |                   |           |     |                      |          |             |         |
20. Li,J.,Tseng,H.W.,Lin,C.,Papakonstantinou,Y.,Swan-
1. Bae, J., Lee, J., Jin, Y., Son, S., Kim, S., Jang, H., son, S.: Hippogriffdb: Balancing i/o and gpu bandwidth
Ham, T.J., Lee, J.W.: Flashneuron: Ssd-enabled large- inbigdataanalytics. PVLDB9(14),1647–1658(2016)

| 24  |     |     |     |     |     |     |     |     |     |     |     |     | ZhonggenLietal. |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --------------- | --- |
21. Li, X., Cheng, R., Chang, K.C.C., Shan, C., Ma, C., 40. Tang, J., Qu, M., Wang, M., Zhang, M., Yan, J., Mei,
Cao,H.:Onanalyzinggraphswithmotif-paths. PVLDB Q.:Line:Large-scaleinformationnetworkembedding.In:
| 14(6),1111–1123(2021) |     |     |     |     |     |     |     | WWW,pp.1067–1077(2015) |     |     |     |     |     |     |
| --------------------- | --- | --- | --- | --- | --- | --- | --- | ---------------------- | --- | --- | --- | --- | --- | --- |
E´.,
22. Li, Z., Ke, X., Zhu, Y., Gao, Y., Tu, Y.: Hc-spmm: Ac- 41. Trouillon, T., Welbl, J., Riedel, S., Gaussier,
celeratingsparsematrix-matrixmultiplicationforgraphs Bouchard, G.: Complex embeddings for simple link pre-
withhybridgpucores. In:ICDE, pp. 501–514 (2025) diction. In:ICML, pp.2071–2080 (2016)
|     |     |     |     |     |     |     |     | 42. Wang,J.,Huang,P.,Zhao,H.,Zhang,Z.,Zhao,B.,Lee, |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | -------------------------------------------------- | --- | --- | --- | --- | --- | --- |
23. Markussen,J.,Kristiansen,L.B.,Halvorsen,P.,Kielland-
D.L.:Billion-scalecommodityembeddingfore-commerce
Gyrud,H.,Stensland,H.K.,Griwodz,C.:Smartio:Zero-
|                                             |     |     |     |     |     |     |      | recommendation |     | in alibaba. |     | In: SIGKDD, |     | pp. 839–848 |
| ------------------------------------------- | --- | --- | --- | --- | --- | --- | ---- | -------------- | --- | ----------- | --- | ----------- | --- | ----------- |
| overheaddevicesharingthroughpcienetworking. |     |     |     |     |     |     | TOCS |                |     |             |     |             |     |             |
(2018)
38,1–78(2021)
|          |          |     |         |         |       |          |     | 43. Wang,Q.,Mao,Z.,Wang,B.,Guo,L.:Knowledgegraph |     |          |               |     |     |               |
| -------- | -------- | --- | ------- | ------- | ----- | -------- | --- | ------------------------------------------------ | --- | -------- | ------------- | --- | --- | ------------- |
| 24. Mei, | J., Sun, | S., | Li, C., | Xu, C., | Chen, | C., Liu, | Y., |                                                  |     |          |               |     |     |               |
|          |          |     |         |         |       |          |     | embedding:                                       |     | A survey | of approaches |     | and | applications. |
Wang,J.,Zhao,C.,Hou,X.,Guo,M.,etal.:Flowwalker:
TKDE29(12),2724–2743(2017)
Amemory-efficientandhigh-performancegpu-baseddy-
|       |       |        |      |            |       |     |        | 44. Wang,X.,Wei,Y.,Xiong,Y.,Huang,G.,Qian,X.,Ding, |     |         |            |     |             |          |
| ----- | ----- | ------ | ---- | ---------- | ----- | --- | ------ | -------------------------------------------------- | --- | ------- | ---------- | --- | ----------- | -------- |
| namic | graph | random | walk | framework. | PVLDB |     | 17(8), |                                                    |     |         |            |     |             |          |
|       |       |        |      |            |       |     |        | Y., Wang,                                          | M., | Li, L.: | Lightseq2: |     | Accelerated | training |
1788–1801(2024)
|           |          |            |     |        |     |          |       | for transformer-based |     |     | models | on gpus. | In: | SC, pp. 1–14 |
| --------- | -------- | ---------- | --- | ------ | --- | -------- | ----- | --------------------- | --- | --- | ------ | -------- | --- | ------------ |
| 25. Miao, | X., Shi, | Y., Zhang, | H., | Zhang, | X., | Nie, X., | Yang, |                       |     |     |        |          |     |              |
(2022)
Z.,Cui,B.:Het-gmp:Agraph-basedsystemapproachto
|         |       |           |       |           |     |             |     | 45. Wang, | Y., Feng, | B., | Li, G., | Li, S., | Deng, | L., Xie, Y., |
| ------- | ----- | --------- | ----- | --------- | --- | ----------- | --- | --------- | --------- | --- | ------- | ------- | ----- | ------------ |
| scaling | large | embedding | model | training. |     | In: SIGMOD, |     |           |           |     |         |         |       |              |
Ding,Y.:Gnnadvisor:Anadaptiveandefficientruntime
pp.470–480(2022)
|              |     |       |              |     |       |               |     | systemforgnnaccelerationongpus. |     |     |     |     | In:OSDI,pp.515– |     |
| ------------ | --- | ----- | ------------ | --- | ----- | ------------- | --- | ------------------------------- | --- | --- | --- | --- | --------------- | --- |
| 26. Mikolov, | T., | Chen, | K., Corrado, | G., | Dean, | J.: Efficient |     |                                 |     |     |     |     |                 |     |
531(2021)
| estimation   | of  | word     | representations |     | in vector       | space. | In: |               |       |                          |                 |            |     |              |
| ------------ | --- | -------- | --------------- | --- | --------------- | ------ | --- | ------------- | ----- | ------------------------ | --------------- | ---------- | --- | ------------ |
|              |     |          |                 |     |                 |        |     | 46. Wang,Y.,  | Feng, | B.,Wang,                 |                 | Z., Huang, | G., | Ding,Y.: Tc- |
| ICLRWorkshop |     | (2013)   |                 |     |                 |        |     |               |       |                          |                 |            |     |              |
|              |     |          |                 |     |                 |        |     | gnn: Bridging |       | sparse                   | gnn computation |            | and | dense tensor |
| 27. Mohoney, | J., | Waleffe, | R.,             | Xu, | H., Rekatsinas, |        | T., |               |       |                          |                 |            |     |              |
|              |     |          |                 |     |                 |        |     | coresongpus.  |       | In: ATC,pp.149–164(2023) |                 |            |     |              |
Venkataraman, S.: Marius: Learning massive graph em- 47. Wang,Z.,Zhang,J.,Feng,J.,Chen,Z.:Knowledgegraph
beddings on a single machine. In: OSDI, pp. 533–549 embedding by translating on hyperplanes. In: AAAI,
| (2021) |     |     |     |     |     |     |     | vol. 28,pp.1112–1119(2014) |     |     |     |     |     |     |
| ------ | --- | --- | --- | --- | --- | --- | --- | -------------------------- | --- | --- | --- | --- | --- | --- |
28. Nvidia: Nvidia gdrcopy: A low-latency gpu memory 48. Wen, Z., Fang, Y., Liu, Z.: Meta-inductive node classifi-
copy library based on gpudirect rdma. Https://github. cationacrossgraphs. In:SIGIR,pp.1219–1228(2021)
com/NVIDIA/gdrcopy 49. Xia, L., Huang, C., Xu, Y., Dai, P., Lu, M., Bo, L.:
29. Nvidia: Gpudirect storage (2019). Multi-behavior enhanced recommendation with cross-
Https://developer.nvidia.com/blog/gpudirect-storage interaction collaborative relation modeling. In: ICDE,
30. Owens,J.D.,Houston,M.,Luebke,D.,Green,S.,Stone, pp.1931–1936(2021)
J.E., Phillips, J.C.: Gpu computing. Proceedings of the 50. Xiaoxuan Zhang, X.L.: Predicting mirna-drug interac-
IEEE96(5),879–899(2008) tions via dual-channel network based on tcn and bilstm.
31. Park, J.B., Mailthody, V.S., Qureshi, Z., Hwu, W.: Ac- FCS 19(5),195,905(2025)
celerating sampling and aggregation operations in gnn 51. Yang, B., Yih, W., He, X., Gao, J., Deng, L.: Embed-
frameworks with gpu initiated direct storage accesses. ding entities and relations for learning and inference in
PVLDB17(6),1227–1240(2024) knowledge bases. In:ICLR,pp.1–12(2015)
32. Park,Y.,Min,S.,Lee,J.W.:Ginex:Ssd-enabledbillion- 52. Yang,Z.,Harris,J.R.,Walker,B.,Verkamp,D.,Liu,C.,
scale graph neural network training on a single ma- Chang, C., Cao, G., Stern, J., Verma, V., Paul, L.E.:
chine via provably optimal in-memory caching. PVLDB Spdk:Adevelopmentkittobuildhighperformancestor-
15(11),2626–2639(2022) ageapplications. In:IEEE CLOUD,pp.154–161(2017)
|     |     |     |     |     |     |     |     | 53. Yuan,H.,Liu,Y.,Zhang,Y.,Ai,X.,Wang,Q.,Chen,C., |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | -------------------------------------------------- | --- | --- | --- | --- | --- | --- |
33. Peng,J.,Chen,Z.,Shao,Y.,Shen,Y.,Chen,L.,Cao,J.:
|     |     |     |     |     |     |     |     | Gu, Y., | Yu, | G.: Comprehensive |     | evaluation |     | of gnn train- |
| --- | --- | --- | --- | --- | --- | --- | --- | ------- | --- | ----------------- | --- | ---------- | --- | ------------- |
Sancus:staleness-awarecommunication-avoidingfull-
|       |               |     |          |                |     |       |        | ing systems: |     | A data | management |     | perspective. | PVLDB |
| ----- | ------------- | --- | -------- | -------------- | --- | ----- | ------ | ------------ | --- | ------ | ---------- | --- | ------------ | ----- |
| graph | decentralized |     | training | in large-scale |     | graph | neural |              |     |        |            |     |              |       |
17(6),1241–1254(2024)
| networks.                        | PVLDB15(9),1937–1950(2022) |          |             |                   |               |     |        |                                                     |     |        |             |     |           |           |
| -------------------------------- | -------------------------- | -------- | ----------- | ----------------- | ------------- | --- | ------ | --------------------------------------------------- | --- | ------ | ----------- | --- | --------- | --------- |
|                                  |                            |          |             |                   |               |     |        | 54. Zhang,J.,Gao,C.,Jin,D.,Li,Y.:Group-buyingrecom- |     |        |             |     |           |           |
| 34. Perozzi,                     | B.,                        | Al-Rfou, | R., Skiena, |                   | S.: Deepwalk: |     | Online |                                                     |     |        |             |     |           |           |
|                                  |                            |          |             |                   |               |     |        | mendation                                           | for | social | e-commerce. |     | In: ICDE, | pp. 1536– |
| learningofsocialrepresentations. |                            |          |             | In:SIGKDD,pp.701– |               |     |        |                                                     |     |        |             |     |           |           |
1547(2021)
710(2014)
|          |                |                              |           |            |       |           |          | 55. Zhang,L.,Wang,S.,Liu,J.,Chang,X.,Lin,Q.,Wu,Y., |              |     |             |                     |          |         |
| -------- | -------------- | ---------------------------- | --------- | ---------- | ----- | --------- | -------- | -------------------------------------------------- | ------------ | --- | ----------- | ------------------- | -------- | ------- |
| 35. Qiu, | J., Dhulipala, |                              | L., Tang, | J.,        | Peng, | R., Wang, | C.:      |                                                    |              |     |             |                     |          |         |
|          |                |                              |           |            |       |           |          | Zheng,                                             | Q.: Mul-grn: |     | Multi-level | graph               | relation | network |
| Lightne: | A lightweight  |                              | graph     | processing |       | system    | for net- |                                                    |              |     |             |                     |          |         |
|          |                |                              |           |            |       |           |          | forfew-shotnodeclassification.                     |              |     |             | TKDE35(6),6085–6098 |          |         |
| work     | embedding.     | In:SIGMOD,pp.2281–2289(2021) |           |            |       |           |          |                                                    |              |     |             |                     |          |         |
(2022)
| 36. Qureshi, | Z., | Mailthody, | V.S., | Gelado, | I., | Min, | S., Ma- |                                                    |     |     |     |     |     |     |
| ------------ | --- | ---------- | ----- | ------- | --- | ---- | ------- | -------------------------------------------------- | --- | --- | --- | --- | --- | --- |
|              |     |            |       |         |     |      |         | 56. Zheng,C.,Jiang,G.,Yan,X.,Yin,P.,Zhou,Q.,Cheng, |     |     |     |     |     |     |
sood,A.,Park,J.,Xiong,J.,Newburn,C.J.,Vainbrand,
J.:Ge2:Ageneralandefficientknowledgegraphembed-
| D.,        | Chung, I.H., | et  | al.: Gpu-initiated |        | on-demand  |           | high- |                     |           |        |              |                 |             |               |
| ---------- | ------------ | --- | ------------------ | ------ | ---------- | --------- | ----- | ------------------- | --------- | ------ | ------------ | --------------- | ----------- | ------------- |
|            |              |     |                    |        |            |           |       | dinglearningsystem. |           |        | SIGMOD       | 2(3),1–27(2024) |             |               |
| throughput | storage      |     | access             | in the | bam system | architec- |       |                     |           |        |              |                 |             |               |
|            |              |     |                    |        |            |           |       | 57. Zheng,          | D., Song, | X.,    | Ma,          | C., Tan,        | Z.,         | Ye, Z., Dong, |
| ture.      | In:ASPLOS,   |     | pp.325–339         | (2023) |            |           |       |                     |           |        |              |                 |             |               |
|            |              |     |                    |        |            |           |       | J., Xiong,          | H.,       | Zhang, | Z., Karypis, |                 | G.: Dgl-ke: | Training      |
37. Rahman,M.K.,Sujon,M.H.,Azad,A.:Fusedmm:Auni-
|     |     |     |     |     |     |     |     | knowledge | graph | embeddings |     | at scale. |     | In: SIGIR, pp. |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | ----- | ---------- | --- | --------- | --- | -------------- |
fiedsddmm-spmmkernelforgraphembeddingandgraph
739–748(2020)
neuralnetworks. In:IPDPS, pp.256–266(2021) 58. Zhong,Z.,Mottin,D.:Knowledge-augmentedgraphma-
38. Ribeiro,L.F.,Saverese,P.H.,Figueiredo,D.R.:struc2vec: chine learning for drug discovery: From precision to in-
Learning node representations from structural identity. terpretability. In:SIGKDD, pp.5841–5842 (2023)
In:SIGKDD, pp.385–394(2017) 59. Zhou, Q., Yin, P., Yan, X., Li, C., Jiang, G., Cheng, J.:
39. Song,Z.,Zhang,Y.,King,I.:Towardsanoptimalasym- Atom: An efficient query serving system for embedding-
metric graph structure for robust semi-supervised node based knowledge graph reasoning with operator-level
classification. In:SIGKDD, pp.1656–1665(2022) batching. SIGMOD2(4),1–29(2024)

EfficientGraphEmbeddingatScale:OptimizingCPU-GPU-SSDIntegration 25
60. Zhu, M., Zhang, T., Gu, Z., Xie, Y.: Sparse tensor core: 62. Zhu, Z., Xu, S., Tang, J., Qu, M.: Graphvite: A high-
Algorithmandhardwareco-designforvector-wisesparse performancecpu-gpuhybridsystemfornodeembedding.
neural networks on modern gpus. In: MICRO, pp. 359– In:WWW,pp. 2494–2504(2019)
371(2019) 63. Zou, Y., Ding, Z., Shi, J., Guo, S., Su, C., Zhang, Y.:
61. Zhu, R., Zhao, K., Yang, H., Lin, W., Zhou, C., Ai, B., Embedx: A versatile, efficient and scalable platform to
Li,Y.,Zhou,J.:Aligraph:Acomprehensivegraphneural embed both graphs and high-dimensional sparse data.
networkplatform. PVLDB12(12),2094–2105(2019) PVLDB16(12),3543–3556(2023)