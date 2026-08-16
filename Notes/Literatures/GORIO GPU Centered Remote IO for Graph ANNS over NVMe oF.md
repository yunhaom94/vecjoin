# GORIO

**Source**: GORIO.pdf
**Format**: .pdf

---

GORIO: GPU-Centered Remote I/O for Graph ANNS over
NVMe-oF
Technical Report

Gen Zhang
NUDT
China

Shan Huang
NUDT
China

Wenhao Gu
NUDT
China

Xinhai Chen
NUDT
China

Abstract

Graph-based approximate nearest neighbor search (ANNS) is in-
creasingly used in vector databases and retrieval-augmented gener-
ation services, but large vector indexes often exceed the memory
capacity of a single GPU server. NVMe over Fabrics (NVMe-oF)
provides an attractive storage-disaggregation substrate, yet existing
remote storage paths are still largely CPU-centered: the CPU forms
I/O requests, drives transport progress, and determines when GPU
computation can resume. This organization is poorly matched to
graph ANNS, where the next data access is discovered inside GPU
graph traversal.

This paper presents GORIO, a system study that extends GPU-
centered local I/O to remote storage and specializes the resulting
substrate for graph ANNS over NVMe-oF. GORIO keeps query
evolution, page-miss generation, pending-query state, and resume
decisions on the GPU, while the CPU acts only as an NVMe-oF trans-
port and completion proxy. The design has two layers: a GPU-direct
remote I/O path that turns local page-cache misses into split-phase
remote operations, and ANNS-specific scheduling mechanisms that
overlap graph traversal with remote page service. On a SIFT1M
DiskANN-style graph workload over an RDMA NVMe-oF path,
GORIO is 1.31× faster than the state-of-the-art remote-I/O refer-
ence path and 4.89× faster than the direct remote page-cache path.
These results demonstrate a concrete GPU-centered remote I/O
substrate for graph ANNS.

Keywords

ANNS, vector databases, GPU-centric storage, NVMe-oF, GPU-
Direct, disaggregated storage

1 Introduction

Approximate nearest neighbor search (ANNS) is a core operator
in vector databases and retrieval-augmented generation (RAG)
pipelines. Graph-based indexes such as HNSW and DiskANN are
widely used because they provide an effective latency-recall trade-
off at scale [12, 22]. At the same time, vector collections continue
to grow beyond the memory budget of a single GPU server, making
disaggregated storage an attractive deployment model.

NVMe over Fabrics (NVMe-oF) appears to be a natural fit for this
setting: storage capacity can be scaled independently from GPU
compute, and RDMA-based transports can provide high bandwidth
and low CPU-copy overhead. However, remote graph ANNS is

not just a bandwidth problem. The search process is fine-grained
and data-dependent: each query repeatedly expands graph nodes,
computes distances, updates a candidate frontier, and discovers the
next pages to fetch. If these page misses are handled by a CPU-
centered remote I/O path, the GPU loses ownership of the search
schedule exactly where the workload is most irregular.

Two observations motivate GORIO. (1) Remote storage. Lo-
cal GPU-centered storage systems such as BaM showed that GPU
threads can directly issue fine-grained storage-backed accesses
through a GPU-visible page cache [19]. That model is attractive
for ANNS, but production deployments often disaggregate storage
from GPU compute. A remote miss traverses queue pairs, an RNIC,
a target-side NVMe stack, and a return path before the data is vis-
ible to the GPU, so local GPU I/O mechanisms cannot be reused
without a remote completion and transport design.

(2) ANNS specialization. Graph ANNS does not need only GPU-
accessible data movement; it also needs page-cache residency, miss
tracking, and GPU-side pending/resume semantics for many small,
data-dependent page misses. A naive remote BaM path therefore
tends to degenerate into repeated “GPU page miss, submit remote
read, busy wait for page ready,” which leaves little room for useful
overlap across queries.

GORIO follows these observations with a narrower design prin-
ciple: keep the graph-search semantics on the GPU, but do not
require the GPU to implement the whole NVMe-oF transport stack.
The GPU owns runnable-query selection, outstanding page-miss
state, and resume decisions. The CPU remains present only as a
thin proxy that submits NVMe-oF commands, polls completions,
and publishes completion state back to GPU-visible memory.

This paper presents this design as a working system over real
NVMe-oF. To the best of our knowledge, GORIO is the first GPU-
direct remote storage substrate designed specifically for graph
ANNS. The contribution is not simply another backend for an ex-
isting scheduler. GORIO extends GPU-centered local page-cache
I/O to disaggregated storage, then adds ANNS-specific scheduling
and proxy mechanisms so graph-search ownership remains on the
GPU.

In summary, this paper makes the following contributions:

• We identify the mismatch between CPU-centered NVMe-oF
scheduling and GPU-resident graph ANNS traversal. To the
best of our knowledge, GORIO is the first GPU-direct remote
storage substrate designed specifically for graph ANNS.

1

arXiv:2607.04415v2  [cs.DC]  7 Jul 2026Technical Report, 2026,

Zhang et al.

• We extend the GPU-centered local I/O model to remote
NVMe-oF storage by converting GPU page-cache misses
into split-phase remote operations with GPU-visible com-
pletion state.

• We specialize this remote I/O substrate for graph ANNS
using persistent GPU scheduling, controlled CPU proxying,
completion-ready tables, and lock-free request descriptors.
• We compare GORIO against state-of-the-art reference paths:
GORIO is 1.31× faster than the remote-I/O reference path on
SIFT1M and 4.89× faster than the direct remote page-cache
path.

2 Background and Motivation
2.1 GPU-Centered Local and Remote I/O

GPU-centered storage systems move fine-grained I/O initiation
closer to GPU computation. BaM is a representative example: GPU
threads access a GPU-resident page cache, generate storage-backed
page misses, and use GPU-visible metadata to determine when a
page becomes available [19]. This design is a natural match for
irregular GPU workloads because the processor that discovers a
miss also owns the dependent computation.

However, local GPU-centered I/O does not directly match pro-
duction storage deployments where capacity is often disaggre-
gated from GPU compute. In an NVMe-oF deployment, a page miss
crosses an RNIC, remote queue pairs, an SPDK or kernel transport
stack, and a remote NVMe namespace before data becomes visible to
the GPU. Existing local designs do not address how GPU-generated
misses are published to a remote transport, how completions be-
come visible to GPU code, or how the CPU can provide transport
progress without taking over application scheduling. These issues
make remote GPU-centered I/O a distinct design problem rather
than a direct reuse of local GPU storage mechanisms.

Motivation 1. GPU-centered I/O must be extended from
local devices to remote NVMe-oF storage. Production de-
ployments often disaggregate storage from GPU compute,
so a practical GPU-centered design must preserve GPU-
owned miss generation and completion visibility across the
network.

2.2 ANNS and GPU-Direct Storage

Graph ANNS repeatedly expands graph nodes, evaluates vector
distances, updates candidate queues, and discovers the next pages
to fetch. When the graph or vector payload is not resident in GPU
memory, page misses are created by the graph traversal itself. This
makes ANNS sensitive not only to storage bandwidth but also to
who owns pending state and resume decisions.

GPU-direct storage paths such as GDS and GPU-centered lo-
cal I/O mechanisms can move data into GPU-accessible memory,
but graph ANNS also requires overlap across many small, data-
dependent misses. A conventional page-read path does not provide
page-cache residency, miss tracking, and GPU-side resume seman-
tics. CPU-centered ANNS systems can recover overlap by coordi-
nating many query lanes on the host, but then the CPU owns the

2

irregular search schedule. Existing work therefore does not specifi-
cally optimize the remote setting in which graph ANNS needs both
GPU-resident scheduling and NVMe-oF transport progress.

The key requirement is split-phase remote page service: GPU
traversal issues or registers a miss, the affected work becomes
pending, independent graph work continues, and the GPU resumes
the dependent work when the remote page becomes visible. GORIO
targets this requirement by extending GPU-centered local I/O to
remote NVMe-oF and specializing it for graph ANNS.

Motivation 2. Remote GPU-direct data movement is not
sufficient for graph ANNS. The system must also provide
page-cache residency, miss tracking, and GPU-side pend-
ing/resume semantics so thousands of irregular graph page
misses can overlap with useful traversal work.

3 Design
3.1 Overall Framework

GORIO starts from the GPU-centered local I/O model introduced
by BaM: GPU threads access a GPU-resident page cache, generate
page misses, and use GPU-visible state to decide when computa-
tion can continue. The key difference is that GORIO extends this
model across an NVMe-oF fabric. A page miss no longer targets
a local NVMe device; it becomes a remote I/O request that must
cross RDMA queue pairs, an SPDK initiator, and a remote NVMe
namespace before the page becomes visible in GPU memory.

The design preserves the GPU-centered ownership of graph
search while adding a remote transport layer. The GPU owns query
evolution, page-miss generation, pending state, and resume de-
cisions. CPU workers do not interpret candidate queues, graph
frontiers, or query termination. They only translate GPU-produced
page requests into NVMe-oF commands and publish completion
state back to GPU-visible memory.

GORIO therefore contains three modules, matching Figure 1: (1)
Remote storage, which provides disaggregated NVMe capacity
through RDMA NVMe-oF; (2) GPU-side optimization, which
maintains the page cache, ready table, pending state, and resume
queue inside GPU-visible memory; and (3) CPU transport proxy,
which submits NVMe-oF requests, polls completions, and publishes
page-ready state without owning graph-search semantics.

Figure 1 shows the GORIO organization. GPU search blocks
execute graph traversal and access the BaM page cache. On a remote
miss, they publish request descriptors into GPU-visible request
structures. CPU proxy workers consume these descriptors, submit
NVMe-oF reads through SPDK, poll completions, and update GPU-
visible completion state. The GPU scheduler then uses this state to
resume pending queries.

3.2 Remote I/O Design

The remote I/O layer converts a GPU page-cache miss into a split-
phase NVMe-oF operation. First, GPU code allocates a cache slot
and atomically reserves a request-descriptor slot. The descriptor
records the page identifier, target cache slot, and dependency meta-
data needed to resume the blocked graph-search work, then be-
comes visible to the CPU proxy through a ready flag. This keeps

GORIO: GPU-Centered Remote I/O for Graph ANNS over NVMe-oF

Technical Report, 2026,

GPU-owned graph execution

CPU transport proxy

Remote storage

persistent GPU scheduler
query/lane state

miss descriptors

request queue
batching

NVMe-oF read

RDMA NVMe-oF
queue pairs

resume

GPU page cache
ready table + resume queue

cache fill + ready bit

SPDK workers
submit / poll

page data

NVMe namespace
graph pages

query state and resume stay on GPU

transport progress only

block-granularity page service

Figure 1: GORIO architecture. The GPU owns graph-search state, page-miss generation, pending queues, and resume decisions.
CPU workers are restricted to NVMe-oF request submission, polling, and completion publication into GPU-visible page-cache
state.

request allocation and dependency tracking on the GPU side in-
stead of serializing miss generation through a CPU-owned submit
path.

Second, CPU proxy workers consume ready descriptors and
submit RDMA NVMe-oF reads through SPDK. The proxy handles
transport progress but not graph-search state. Returned page data
is placed into GPU-accessible cache pages.

Third, completion publication is decoupled from query sched-
uling. Each GPU page-cache slot has a GPU-visible ready-table
entry. When a CPU worker completes a remote read and fills the
cache slot, it marks the corresponding ready entry. GPU code tests
this per-slot state when resuming a pending page miss, avoiding a
shared completion queue on the GPU search path.

3.3 GPU-Side Optimization and CPU Proxy

Graph ANNS produces many small, data-dependent misses, so the
remote I/O layer must be paired with GPU-side scheduling. GORIO
runs a persistent scheduler kernel. Search blocks repeatedly claim
work, execute graph traversal, and either finish a query or mark it
pending on a missing page. A pending query yields the block so
that the block can work on another ready query rather than waiting
in place for the remote page.

The CPU proxy is necessary because NVMe-oF/SPDK queue-
pair progress is host-managed. However, the proxy remains outside
graph-search semantics. GORIO exposes only page-level descriptors
to the CPU proxy. The proxy batches submissions and completions,
controls outstanding remote I/O, and publishes ready state, but it
does not inspect candidate queues, graph frontiers, or query termi-
nation state. This division keeps ANNS scheduling GPU-centered
while using the CPU for the transport operations that NVMe-oF
software stacks already support efficiently.

4 Implementation

GORIO is implemented in C, C++, CUDA, and SPDK. It extends a
BaM-based GPU page-cache path with an SPDK NVMe-oF initiator
and integrates it with a GustANN-derived graph-search workload.

3

The remote target is accessed through an RDMA NVMe-oF trans-
port, and GPU data return uses GPU-accessible cache pages.

The implementation follows the three modules in Section 3.
Remote storage. The remote storage module uses SPDK as an
NVMe-oF initiator and connects to a remote NVMe namespace
over RDMA. A BaM-derived page-cache path translates a GPU-
generated graph page miss into a remote page read. The returned
data is placed in GPU-accessible cache pages, so the graph-search
kernel can consume the page without copying it through a host-
side staging buffer. This module provides capacity disaggregation
while preserving the page-cache abstraction expected by GPU-side
traversal.

GPU-side optimization. The GPU module contains the ANNS
traversal kernels, the GPU page cache, request descriptors, ready-
table entries, and pending/resume state. When a traversal step
discovers a missing page, GPU code records the dependency and
publishes a descriptor rather than blocking in place. The persistent
scheduler then switches to other ready work. When the ready table
indicates that the remote page has arrived, the scheduler resumes
the corresponding query state. This keeps irregular graph-search
control flow on the GPU.

CPU transport proxy. The CPU proxy module provides the
SPDK submit/poll loop needed by the NVMe-oF software stack.
Workers consume GPU-produced descriptors, submit remote reads,
poll completions, fill the corresponding GPU cache slots, and
publish ready state. The proxy also implements batching and
outstanding-depth control so the transport is served regularly with-
out turning the CPU into a graph scheduler. It does not inspect
candidate queues, graph frontiers, or query termination state.

5 Evaluation
5.1 Setup
Environment. The evaluation uses a SIFT1M DiskANN-style graph
workload with 10,000 queries and recall@10 evaluation. The exper-
iments use two servers connected through an InfiniBand NVMe-oF
path. Table 1 summarizes the hardware and software environment.

Technical Report, 2026,

Zhang et al.

Table 1: Experimental platform.

Component

Configuration

Servers
CPU
Memory
GPU
Network
Remote SSD

OS
CUDA
SPDK

Two servers
Intel Xeon Silver 4316, 40 CPUs per server
512 GB per server
NVIDIA L40S, 48 GB memory
NVIDIA ConnectX-6 InfiniBand, 200 Gbps
Huawei HWE6AP443T8L00LN, 3.84 TB enter-
prise NVMe SSD
Ubuntu 22.04
CUDA 13.0
SPDK 25.09

Table 2: End-to-end SIFT1M results over 10,000 queries.

System

Time

QPS Speedup

G-Gust
GustANN
G-ABaM
BaM
GDS

0.99 s 10,058 1.31× vs. GustANN; 121× vs. GDS
1.30 s
1.77 s
8.66 s
120.19 s

7,680 reference
5,650 4.89× vs. BaM; 68× vs. GDS
1,155 14× vs. GDS
83 baseline

All reported times are the benchmark search time printed by the
application.

Comparison. We compare five execution paths that separate the
remote-I/O substrate from the ANNS-specific scheduling layer. The
short name GustANN denotes the SPDK-backed GustANN imple-
mentation and serves as the state-of-the-art remote-I/O reference.
G-Gust keeps the GustANN-style asynchronous query scheduler
but replaces its remote backend with the tuned GORIO remote I/O
path, isolating the benefit of the remote substrate. BaM follows the
BaM-style demand-paged execution model over NVMe-oF, in which
GPU page misses issue remote reads and wait for page readiness.
G-ABaM adds the ANNS-specific GPU scheduling and CPU-proxy
mechanisms on top of that BaM-derived remote path. GDS is a
GDS-based page-read baseline.

Benchmark. All systems are evaluated on the SIFT1M DiskANN-
style graph workload. Each run searches 10,000 query vectors
against the same on-disk graph index and reports top-10 nearest-
neighbor results.

Metrics. We report end-to-end search time, throughput, and
Recall@10. Throughput is computed as 10000/time queries per
second (QPS). All reported times are the benchmark search time
printed by the application.

5.2 End-to-End Results and Analysis

Table 2 summarizes the end-to-end results. Each run searches 10,000
SIFT1M queries, so throughput is computed as 10000/time.

The first comparison is between G-Gust and GustANN. Both
paths use a GustANN-style asynchronous query scheduler, so the
comparison isolates the remote-I/O substrate. G-Gust improves
search time from 1.30 s to 0.99 s, or 1.31× higher throughput. This
indicates that the tuned GORIO backend provides a lower-overhead
remote page service than the SPDK-backed reference path under the
same high-level scheduler. The improvement comes from extending

4

GPU-centered page-cache I/O to the remote setting with GPU-
visible data placement and a lightweight SPDK/NVMe-oF transport
path, reducing the cost of fine-grained graph page misses.

The second comparison is between G-ABaM and BaM. These two
paths share the same remote BaM-derived page-cache substrate, so
the comparison isolates the ANNS-specific optimization layer. G-
ABaM replaces blocking page waits with persistent GPU scheduling,
controlled transport proxying, GPU-visible completion publication,
and lock-free request descriptors. The result reduces search time
from 8.66 s to 1.77 s, a 4.89× throughput improvement. This shows
that the main cost in the direct BaM-style NVMe-oF path is not
simply remote bandwidth; it is the loss of useful GPU work while
graph traversal waits for remote pages. G-ABaM improves perfor-
mance by turning page misses into split-phase events: issue the
miss, yield blocked work, run other ready work, and resume when
the page becomes visible in the GPU cache.

The third comparison is against GDS. All GORIO variants sub-
stantially outperform this GDS page-read baseline: G-Gust is about
121× faster, G-ABaM is about 68× faster, and BaM is about 14×
faster. This confirms that GPU-resident graph ANNS requires a
fine-grained asynchronous storage path rather than a conventional
page-read path. GDS provides GPU-accessible data movement, but
it does not by itself provide the queueing, page-cache residency,
miss tracking, and GPU-side resume semantics needed to overlap
thousands of irregular graph page misses.

Result Takeaway. The results directly address the two
challenges identified in Section 2. First, GORIO demon-
strates that GPU-centered I/O can be extended to real
NVMe-oF storage and outperform the remote-I/O reference
path. Second, GORIO demonstrates that ANNS-specific
split-phase miss handling removes the blocking behavior
of a direct remote page-cache path, improving throughput
by 4.89× while preserving GPU ownership of graph search.
Together, GORIO outperforms the GPU Direct Storage base-
line by up to 121×.

6 Related Work
GPU-centric storage. BaM showed that GPU threads can initiate
fine-grained storage-backed accesses directly through a software
cache and high-throughput queueing substrate [19]. GORIO builds
on this idea by extending GPU-centered page-cache I/O from lo-
cal NVMe devices to remote NVMe-oF storage, where descriptor
publication, completion visibility, and transport proxying become
first-order design issues.

Disk-resident ANNS. DiskANN and Starling study page lay-
out, graph locality, and I/O-efficient search for disk-resident vector
indexes [22, 27]. GORIO focuses on a different layer: how GPU-
side graph traversal should drive remote I/O and resume execution
over an NVMe-oF fabric. To the best of our knowledge, prior disk-
resident ANNS systems do not provide a GPU-direct remote storage
path specialized for graph traversal over NVMe-oF.

Host-centric remote storage paths. Kernel NVMe-oF and
SPDK provide efficient remote block access, but they remain CPU-
centered in request formation and progress [14, 21]. GORIO keeps
SPDK as a transport mechanism while moving page-miss ownership
and graph-search scheduling back to the GPU.

GORIO: GPU-Centered Remote I/O for Graph ANNS over NVMe-oF

Technical Report, 2026,

Asynchronous GPU-storage integration. Recent work on
asynchronous GPU-storage access shows that split-phase is-
sue/consume semantics improve overlap for irregular GPU work-
loads [30]. GORIO applies this principle to remote graph ANNS,
where fabric latency makes pending/resume behavior central.

7 Discussion
7.1 Why GPU-Centered Remote I/O Matters

The GORIO result with a GustANN-style scheduler shows that
the remote substrate can support high-performance ANNS when
paired with an effective asynchronous scheduler. GORIO moves
this ownership into GPU-resident execution, where graph traversal
discovers page misses and naturally owns pending/resume state.
This design has three advantages. First, query state remains local
to GPU computation, which is a clean fit for increasingly GPU-
resident vector search pipelines. Second, CPU resources are used
for transport progress rather than graph scheduling, which matters
when one host serves multiple GPUs or multiple tenants. Third,
the GPU scheduler exposes page-miss and lane-state information
directly, making coalescing and selective retrieval optimizations
easier to express.

7.2 Future Work

Several directions can further strengthen GORIO. First, a finer
lane/page-miss scheduler can expose more ready GPU work when
only part of a query is blocked by remote I/O. Second, miss coalesc-
ing can merge duplicate page requests across lanes or queries before
they reach the transport. Third, target-side selective materialization
can return only the graph records needed by active lanes, reduc-
ing useful-byte amplification for page-granularity reads. Fourth,
query-aware multipath steering can distribute remote reads across
multiple NVMe-oF paths based on query state and queue pressure.
The evaluation should also be expanded beyond SIFT1M. Larger
indexes and additional datasets are needed to characterize how
the remote substrate behaves under higher graph depth, larger
working sets, different recall targets, and multi-GPU or multi-tenant
deployments.

8 Conclusion

We presented GORIO, a system study that extends GPU-centered
local I/O to remote NVMe-oF storage and specializes it for graph
ANNS. GORIO converts GPU page-cache misses into split-phase
remote operations, publishes completion state back to GPU-visible
memory, and keeps ANNS pending/resume decisions on the GPU
while using the CPU as a transport proxy. Evaluation shows that
GORIO is 1.31× faster than the remote-I/O reference path and 4.89×
faster than the direct remote page-cache path with the same recall.
The result demonstrates that GPU-owned page-miss generation,
pending state, and resume decisions can drive real NVMe-oF storage
without moving graph-search scheduling back to the CPU.

References
[1] Chia-Hao Chang, Jihoon Han, Anand Sivasubramaniam, Vikram Sharma
Mailthody, Zaid Qureshi, and Wen-Mei Hwu. 2024. GMT: GPU Orchestrated
Memory Tiering for the Big Data Era. In Proceedings of the 29th ACM International
Conference on Architectural Support for Programming Languages and Operating
Systems, Volume 3 (ASPLOS ’24). doi:10.1145/3620666.3651353

5

[2] GNStor Authors. 2026. GNStor: Design of GPU-Native High-Performance Remote

All-Flash Array. Local PDF copy; bibliographic metadata unavailable.

[3] Jihoon Han, Anand Sivasubramaniam, Chia-Hao Chang, Vikram Sharma
Mailthody, Zaid Qureshi, and Wen-Mei Hwu. 2026. Asynchrony and GPUs:
Bridging this Dichotomy for I/O with AGIO. In Proceedings of the 31st ACM
International Conference on Architectural Support for Programming Languages and
Operating Systems, Volume 2 (ASPLOS ’26). doi:10.1145/3779212.3790130

[4] Yifan Hu, Shi Qiu, Jianqin Yan, Hao Chen, Xintao Wang, Lu Tang, Guangtao Xue,
and Yiming Zhang. 2025. TARDIS: A GPU-Centric KV Cache Service for Efficient
LLM Inference. In Proceedings of the 16th ACM SIGOPS Asia-Pacific Workshop on
Systems (APSys ’25).

[5] Yuchen Huang, Xiaopeng Fan, Song Yan, and Chuliang Weng. 2024. Neos: A
NVMe-GPUs Direct Vector Service Buffer in User Space. In Proceedings of the
40th IEEE International Conference on Data Engineering (ICDE ’24). doi:10.1109/
ICDE60146.2024.00289

[6] Haodi Jiang, Hao Guo, Minhui Xie, Jiwu Shu, and Youyou Lu. 2025. High-
Throughput, Cost-Effective Billion-Scale Vector Search with a Single GPU. Pro-
ceedings of the ACM on Management of Data 3, 6, Article 334 (2025). doi:10.1145/
3769799

[7] Arpandeep Khatua. 2022. Creating Large Real and Synthetic Graph Datasets for
GNN Applications. Master’s thesis. University of Illinois Urbana-Champaign.
[8] Shaobo Li, Yirui Eric Zhou, Yuqi Xue, Yuan Xu, and Jian Huang. 2025. Managing
Scalable Direct Storage Accesses for GPUs with GoFS. In Proceedings of the 31st
ACM Symposium on Operating Systems Principles (SOSP ’25).

[9] Zhonggen Li, Xiangyu Ke, Yifan Zhu, Yunjun Gao, and Feifei Li. 2026. Efficient
Graph Embedding at Scale: Optimizing CPU-GPU-SSD Integration. arXiv preprint
arXiv:2505.09258 (2026). https://arxiv.org/abs/2505.09258

[10] Xiaojian Liao, Youyou Lu, Zhe Yang, and Jiwu Shu. 2023. Efficient Crash Con-
sistency for NVMe over PCIe and RDMA. ACM Transactions on Storage 19, 1,
Article 7 (2023). doi:10.1145/3568428

[11] Vikram Sharma Mailthody. 2022. Application Support and Adaptation for High-
Throughput Accelerator Orchestrated Fine-Grain Storage Access. Ph. D. Dissertation.
University of Illinois Urbana-Champaign.

[12] Yury A. Malkov and Dmitry A. Yashunin. 2020. Efficient and Robust Approximate
Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs. IEEE
Transactions on Pattern Analysis and Machine Intelligence 42, 4 (2020), 824–836.
doi:10.1109/TPAMI.2018.2889473

[13] Seung Won Min, Kun Wu, Sitao Huang, Mert Hidayetoglu, Jinjun Xiong, Eiman
Ebrahimi, Deming Chen, and Wen mei Hwu. 2021. PyTorch-Direct: Enabling
GPU Centric Data Access for Very Large Graph Neural Network Training with
Irregular Accesses. arXiv preprint arXiv:2101.07956 (2021). https://arxiv.org/abs/
2101.07956

[14] NVM Express. 2021. NVM Express over Fabrics Specification, Revision
1.1a. https://nvmexpress.org/wp-content/uploads/NVMe-over-Fabrics-1.1a-
2021.07.12-Ratified.pdf. Ratified July 12, 2021; accessed for NVMe-oF trans-
port model and terminology.

[15] Jeongmin Brian Park, Vikram Sharma Mailthody, Zaid Qureshi, and Wen mei
Hwu. 2024. GIDS: Accelerating Sampling and Aggregation Operations in GNN
Frameworks with GPU Initiated Direct Storage Accesses. Proceedings of the VLDB
Endowment 17, 6 (2024), 1227–1240. doi:10.14778/3648160.3648166

[16] Phoenix Authors. 2025. Phoenix: A Refactored I/O Stack for GPU Direct Storage
without Phony Buffers. In Proceedings of the International Conference for High
Performance Computing, Networking, Storage, and Analysis (SC ’25). doi:10.1145/
3689031.3696080 Author names are not available in the local PDF copy.

[17] Shi Qiu, Weinan Liu, Yifan Hu, Jianqin Yan, Zhirong Shen, Xin Yao, Renhai Chen,
Gong Zhang, and Yiming Zhang. 2025. GeminiFS: A Companion File System
for GPUs. In Proceedings of the 23rd USENIX Conference on File and Storage
Technologies (FAST ’25).

[18] Zaid Qureshi. 2022. Infrastructure to Enable and Exploit GPU Orchestrated High-
Throughput Storage Access. Ph. D. Dissertation. University of Illinois Urbana-
Champaign.

[19] Zaid Qureshi, Vikram Sharma Mailthody, Isaac Gelado, Seungwon Min, Amna
Masood, Jeongmin Park, Jinjun Xiong, C. J. Newburn, Dmitri Vainbrand, I.-Hsin
Chung, Michael Garland, William Dally, and Wen mei Hwu. 2023. GPU-Initiated
On-Demand High-Throughput Storage Access in the BaM System Architecture. In
Proceedings of the 28th ACM International Conference on Architectural Support for
Programming Languages and Operating Systems, Volume 2 (ASPLOS ’23). 325–339.
doi:10.1145/3575693.3575748

[20] Ziyu Song, Jie Zhang, Jie Sun, Mo Sun, Zihan Yang, Zheng Zhang, Xuzheng Chen,
Fei Wu, Huajin Tang, and Zeke Wang. 2025. CAM: Asynchronous GPU-Initiated,
CPU-Managed SSD Management for Batching Storage Access. In Proceedings
of the 41st IEEE International Conference on Data Engineering (ICDE ’25). doi:10.
1109/ICDE65448.2025.00175

[21] SPDK Project. 2026. Storage Performance Development Kit (SPDK). https:

//spdk.io/. Accessed for system software description.

[22] Suhas Jayaram Subramanya, Rohan Kadekodi, Ravishankar Krishnaswamy, and
Harsha Vardhan Simhadri. 2019. DiskANN: Fast Accurate Billion-Point Nearest
Neighbor Search on a Single Node. In Advances in Neural Information Processing

Technical Report, 2026,

Zhang et al.

Systems 32 (NeurIPS 2019).

[23] Jie Sun, Mo Sun, Zheng Zhang, Zuocheng Shi, Jun Xie, Zihan Yang, Jie Zhang,
Zeke Wang, and Fei Wu. 2025. Hyperion: Co-Optimizing SSD Access and GPU
Computation for Cost-Efficient GNN Training. In Proceedings of the 41st IEEE
International Conference on Data Engineering (ICDE ’25). doi:10.1109/ICDE65448.
2025.00031

[24] Jie Sun, Mo Sun, Zheng Zhang, Jun Xie, Zuocheng Shi, Zihan Yang, Jie Zhang,
Fei Wu, and Zeke Wang. 2023. Helios: An Efficient Out-of-core GNN Training
System on Terabyte-scale Graphs with In-memory Performance. arXiv preprint
arXiv:2310.00837 (2023). https://arxiv.org/abs/2310.00837

[25] Bing Tian, Haikun Liu, Yuhang Tang, Shihai Xiao, Zhuohui Duan, Xiaofei Liao,
Hai Jin, Xuecang Zhang, Junhua Zhu, and Yu Zhang. 2025. Towards High-
throughput and Low-latency Billion-scale Vector Search via CPU/GPU Collabo-
rative Filtering and Re-ranking. In Proceedings of the 23rd USENIX Conference on
File and Storage Technologies (FAST ’25).

[26] Karthik Venkatasubba, Saim Khan, Somesh Singh, Harsha Vardhan Simhadri,
and Jyothi Vedurada. 2025. BANG: Billion-Scale Approximate Nearest Neighbour
Search Using a Single GPU. IEEE Transactions on Big Data 11, 6 (2025), 3142–3157.
doi:10.1109/TBDATA.2025.3581085

[27] Mengzhao Wang, Weizhi Xu, Xiaomeng Yi, Songlin Wu, Zhangyang Peng, Xi-
angyu Ke, Yunjun Gao, Xiaoliang Xu, Rentong Guo, and Charles Xie. 2024.
Starling: An I/O-Efficient Disk-Resident Graph Index Framework for High-
Dimensional Vector Similarity Search on Data Segment. Proceedings of the ACM
on Management of Data 2, 1 (2024). doi:10.1145/3639264

[28] Yang Xiao, Mo Sun, Ziyu Song, Bing Tian, Jie Sun, Jie Zhang, Zeke Wang, Zonghui
Wang, Wenzhi Chen, and Fei Wu. 2026. FlashANNS: GPU-Driven Asynchronous
I/O Pipelining for Eliminating Storage-Compute Bottlenecks in Billion-Scale
Similarity Search. Proceedings of the ACM on Management of Data (2026). To
appear in SIGMOD.

[29] Minhui Xie, Youyou Lu, Yangyang Feng, and Jiwu Shu. 2024. A Recommendation
Model Inference System Based on GPU Direct Storage Access Architecture.
Journal of Computer Research and Development 61, 3 (2024), 589–599. doi:10.7544/
issn1000-1239.202330402

[30] Zhuoping Yang, Jinming Zhuang, Xingzhen Chen, Alex K. Jones, and Peipei Zhou.
2025. AGILE: Lightweight and Efficient Asynchronous GPU-SSD Integration.
In Proceedings of the International Conference for High Performance Computing,
Networking, Storage and Analysis (SC ’25). doi:10.1145/3712285.3759778

[31] Zili Zhang, Fangyue Liu, Gang Huang, Xuanzhe Liu, and Xin Jin. 2024. Fast
Vector Query Processing for Large Datasets Beyond GPU Memory with Reordered
Pipelining. In Proceedings of the 21st USENIX Symposium on Networked Systems
Design and Implementation (NSDI ’24).

[32] Hao Zhou, Yuanhui Chen, Wu Zeng, Lixiao Cui, Gang Wang, and Xiaoguang
Liu. 2025. GPComp: Using GPU and SSD-GPU Peer to Peer DMA to Accelerate
LSM-Tree Compaction for Key-Value Store. IEEE Transactions on Parallel and
Distributed Systems 36, 9 (2025), 1920–1936. doi:10.1109/TPDS.2025.3586616
[33] Yirui Eric Zhou. 2025. Managing Scalable Direct Storage Accesses for GPUs. Mas-

ter’s thesis. University of Illinois Urbana-Champaign.

6

