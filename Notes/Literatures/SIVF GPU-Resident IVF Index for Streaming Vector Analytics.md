SIVF: GPU-Resident IVF Index for Streaming Vector Analytics
Dongfang Zhao (dzhao@uw.edu)

6
2
0
2

b
e
F
9

]

B
D
.
s
c
[

2
v
8
0
8
1
1
.
1
0
6
2
:
v
i
X
r
a

Abstract
GPU-accelerated Inverted File (IVF) index is one of the industry
standards for large-scale vector analytics but relies on static VRAM
layouts that hinder real-time mutability. Our benchmark and anal-
ysis reveal that existing designs of GPU IVF necessitate expensive
CPU-GPU data transfers for index updates, causing system latency
to spike from milliseconds to seconds in streaming scenarios. We
present SIVF, a GPU-native index that enables high-velocity, in-
place mutation via a series of new data structures and algorithms,
such as conflict-free slab allocation and coalesced search on non-
contiguous memory. SIVF has been implemented and integrated
into the open-source vector search library, Faiss. Evaluation against
baselines with diverse vector datasets demonstrates that SIVF re-
duces deletion latency by orders of magnitude compared to the
baseline. Furthermore, distributed experiments on a 12-GPU cluster
reveal that SIVF exhibits near perfect linear scalability, achieving
an aggregate ingestion throughput of 4.07 million vectors/s and a
deletion throughput of 108.5 million vectors/s.

1 Introduction
Real-world vector analytics applications, ranging from search en-
gines to dynamic retrieval-augmented generation (RAG) of large
language models (LLMs), increasingly operate on streaming data
where timeliness is critical [30, 38]. These systems necessitate
a sliding-window model where expired vectors must be invali-
dated promptly as new vectors arrive to maintain bounded memory
footprint. However, existing GPU-accelerated approximate nearest
neighbor (ANN) indices are predominantly optimized for static,
write-once-read-many workloads [33, 55].

To quantify the gap between insertion and eviction performance,
we conducted benchmarks with the industry-standard Faiss li-
brary [21] and the state-of-the-art graph index CAGRA (cuVS) [39]
on an NVIDIA RTX 6000 GPU hosted at the Chameleon Cloud [24].
We utilized the SIFT1M dataset [23] to simulate a realistic sliding-
window scenario, measuring the wall-clock latency of ingesting
10,000 new vectors and evicting the oldest 10,000.

As illustrated in Figure 1(a), we observe a drastic asymmetry
between insertion and physical deletion. While GPU parallelism
accelerates insertion to ∼28 ms for IVF, the eviction process is sig-
nificantly slower. For Faiss IVF, physical deletion spikes the latency
to ∼200 ms (∼7.1× slower) due to the contiguous memory layout
necessitating expensive data shifting. The situation is catastrophic
for graph-based indices: CAGRA incurs a deletion latency of over
3,000 ms (∼92× slower) as the topology requires reconstruction to
maintain connectivity.

A common alternative is lazy deletion (aka tombstone), which
marks vectors as invalid to avoid immediate physical movement.
However, this strategy merely defers the cost. As shown in Fig-
ure 1(b), tombstone mechanisms suffer from poor scalability due to
the 𝑂 (𝑁 ) complexity of garbage collection (compaction). Based on
our microbenchmarks, the compaction pause scales linearly with
index size. While negligible at small scales, the latency is projected

(a) Physical deletion overhead.

(b) Tombstone scalability trap.

Figure 1: The dilemma of mutability on GPUs.

to exceed 360 ms at 50 million vectors and reach nearly 700 ms at
100 million vectors. These results confirm a fundamental limitation:
current GPU indices lack an efficient mutability mechanism that
is both low-latency (unlike physical deletion) and scalable (unlike
tombstones), necessitating a new indexing method ideally with a
constant cost, as represented by SIVF that we will present.

Our analysis of the Faiss source code [7] further reveals that
this performance asymmetry stems from a rigid class hierarchy
that enforces a fallback to host-side processing on CPUs. In the
library’s architecture, the data eviction interface is defined in the ab-
stract base class faiss::Index via the remove_ids virtual method.
While CPU-based implementations override this method to pro-
vide efficient in-memory deletion logic (e.g., memmove), the GPU
counterparts inherit the base implementation which lacks native
support. Consequently, current GPU indices rely on a CPU-GPU
Roundtrip pattern for eviction. That is, to delete even a single vector,
the system must transfer the entire index state from VRAM to host
memory, perform the compaction on the CPU, and re-upload the
modified index to the device. This heavy I/O burden saturates the
PCIe bus and prevents the system from utilizing the GPU’s compute
throughput, capping the maximum sustainable ingestion rate in
streaming scenarios.

The lack of a GPU-resident eviction operator is not an over-
sight, but a consequence of how GPU IVF indices are engineered
for throughput. To maximize memory coalescing and bandwidth
utilization, inverted lists are typically stored in pre-allocated con-
tiguous buffers. In this setting, naive tombstone deletion is hard to
make practical. First, tombstones provide only logical deletion and
do not reclaim space, so under a sliding-window workload dead
entries accumulate and lists grow, forcing queries to scan and filter
more invalid slots unless compaction is performed. Second, com-
paction and slot reuse in VRAM require bulk data movement and
careful synchronization with concurrent queries and updates under
the GPU memory model. In addition, standard inverted file (IVF)
indices lack an ID-to-Location mapping. Without a reverse index,
locating a specific ID for deletion requires scanning all inverted
lists, an operation with 𝑂 (𝑁 ) complexity that negates the benefits
of GPU acceleration. These constraints make naive GPU eviction
prohibitively inefficient.

InsertionDeletion101102103104Latency (ms)28207281983330307.1xSlower92xSlowerIVF(Py)IVF(C++)CAGRA020406080100Index Scale (Millions)0100200300400500600700800Latency (ms)368ms(Laggy)688ms(Freeze)SIVFTombstone

To resolve these limitations, we propose SIVF, a GPU-resident in-
dexing method that supports high-throughput mutability through
four specialized device-side algorithms. First, to enable nonblocking
writes, we design a Lock-Free Ingestion protocol (Algorithms 1 & 2)
that manages a pool of fixed-size slabs. This protocol utilizes atomic
Compare-And-Swap for slot reservation and speculative head up-
dates, allowing concurrent threads to append to linked lists without
global locks. Second, to guarantee data consistency under CUDA’s
relaxed memory model, we apply a strict publication ordering;
the kernel issues device-wide memory fences (__threadfence())
before committing validity bits, ensuring readers never observe par-
tially initialized payloads. Third, to mitigate the latency of pointer
chasing, we propose Warp-Cooperative Search (Algorithm 3). By
aligning the slab capacity (𝐶 = 32) with the hardware warp width,
this algorithm enables threads to cooperatively load and evalu-
ate non-contiguous memory blocks while preserving coalesced
access patterns. Finally, we address deletion by maintaining a GPU-
resident Address Translation Table along with lazy eviction (Algo-
rithm 4), allowing SIVF to decouple logical removal from physical
data movement, which makes eviction to a constant-time operation.
SIVF has been implemented and integrated into Faiss [7] as a
new index through the GpuIndexSIVF class. Our implementation
leverages CUDA for device-side kernels and employs a dual-view
memory management strategy to maintain the consistency between
host and device states. All new algorithms as well as key data struc-
tures are encapsulated within a SlabManager class that abstracts
the complexity of dynamic memory operations on the GPU.

We have evaluated SIVF against a comprehensive set of base-
lines within Faiss, including CAGRA (cuVS) [39], IVF [21], Flat [7],
HNSW [35], NSG [9], and LSH [5]. Our evaluation was carried out
on six datasets representing a variety of modalities, dimensions, and
scalability: synthetic [7], Deep1B [51], SIFT1M [23], T2I-1B [43],
GIST1M [23], and DINO10B [1]. Experimental results show that
SIVF achieves up to 1765x reduction in deletion latency compared
to CPU fallback baselines and improves ingestion throughput by
36x to 120x compared to existing GPU indices. Furthermore, dis-
tributed evaluations on a 12-GPU cluster demonstrate that SIVF
exhibits near-perfect linear scalability, reaching an aggregate dele-
tion throughput of 108.5 million vectors/s and 159.3K vectors/s for
high-fidelity search. In end-to-end sliding window scenarios, SIVF
delivers a 163x to 262x speedup with a negligible memory overhead
less than 0.8 percent, effectively closing the gap between static and
streaming vector analytics performance.

In summary, this paper makes the following contributions:

• We identify the CPU-GPU bottleneck in existing GPU vec-
tor indices when being used for sliding-window scenarios,
demonstrating that the lack of native deletion support ren-
ders them unsuitable for streaming vector analytics.

• We propose a new indexing method, namely SIVF, that
synthesizes a series of GPU-optimized data structures and
algorithms for streaming vector analytics. This design en-
ables 𝑂 (1) time complexity for deletion and constant-time
insertion overhead with negligible memory overhead.
• We implement SIVF in the state-of-the-art vector search
library Faiss and evaluate SIVF against a broad spectrum
of baselines including GPU CAGRA, GPU Flat, GPU IVF,

Dongfang Zhao (dzhao@uw.edu)

HNSW, NSG, and LSH on 6 representative datasets and a
12-GPU cluster. The results demonstrate that SIVF achieves
up to 1765x reduction in deletion latency, up to 120x faster
ingestion compared to existing GPU indices, and exhibits
near perfect linear scalability in distributed environments
reaching 108.5 million vectors/s for deletion and 4.07 million
vectors/s for ingestion on 12 GPUs. These advancements
transform vector search from a static retrieval task into an
integral component of real-time vector data analytics.

2 Related Work

Optimization of Graph-Based Indices. Graph-based indices re-
main the state-of-the-art for high-recall retrieval. To address per-
formance bottlenecks in production, frameworks like VSAG [56]
optimize memory access patterns and parameter tuning, while
SOAR [44] improves indexing structures. Of note, CAGRA [39]
establishes a new state-of-the-art for static graph construction and
search throughput on GPUs; however, it is fundamentally designed
for write-once-read-many workloads and lacks native support for
the efficient, fine-grained in-place deletions required by streaming
applications. Navigational efficiency is a key optimization target;
SHG [12] introduces a hierarchical graph with shortcuts to by-
pass redundant levels, and probabilistic routing methods [34] have
been proposed to enhance traversal. Several works focus on dis-
tance metric optimizations: ADA-NNS [22] utilizes angular distance
guidance to filter irrelevant neighbors, DADE [6] accelerates com-
parisons via data-aware distance estimation in lower dimensions,
and HSCG [42] adapts the Monotonic Relative Neighbor Graph for
cosine similarity using hemi-sphere centroids. Efforts to improve
graph construction and maintenance include LIGS [4], which em-
ploys locality-sensitive hashing (LSH) to simulate proximity graphs
for faster updates, and CSPG [52], which crosses sparse proximity
graphs. Addressing robustness, Hua et al. [14] propose dynami-
cally detecting and fixing graph hardness for out-of-distribution
queries. MIRAGE-ANNS [46] attempts to bridge the gap between
incremental and refinement-based construction. Furthermore, theo-
retical frameworks like Subspace Collision [49] provide guarantees
on result quality via clustering-based indexing. Collectively, while
these approaches maximize navigational efficiency for static data,
they fundamentally rely on complex edge dependencies that are
prohibitively expensive to maintain on GPUs. Unlike SIVF, they
lack the architectural support for 𝑂 (1) lock-free mutation, render-
ing them unsuitable for high-churn streaming workloads where
sub-millisecond update latency is critical.

Attribute-Filtered and Hybrid Search. The integration of struc-
tured constraints with vector analytics has led to a surge in Filtered
ANN research. Li et al. [27] provide a comprehensive taxonomy
and benchmark of these methods. For range filtering, UNIFY [31]
introduces a segmented inclusive graph to support pre-, post-, and
hybrid filtering strategies. Dynamic environments are addressed
by DIGRA [20], which uses a multi-way tree structure for dynamic
graph indexing, and RangePQ [54], which offers a linear-space
indexing scheme for range-filtered updates. Peng et al. [40] pro-
pose dynamic segment graphs to handle mixed streams of data and
queries. Regarding specific constraints, Wang et al. [47] present a
robust framework for general attribute constraints. Engels et al. [8]

SIVF: GPU-Resident IVF Index for Streaming Vector Analytics

focus on window filters, while WoW [48] develops a window-graph
based index to handle window-to-window incremental construc-
tion. However, these contributions primarily optimize algorithmic
filtering logic rather than the underlying storage architecture. They
remain constrained by the static memory layouts of standard GPU
indices, whereas SIVF fundamentally redesigns the VRAM manage-
ment to enable the high-throughput, in-place mutability that is a
prerequisite for such dynamic operations.

Quantization and Scalability. To manage high-dimensional data
at scale, quantization and system-level optimizations are critical.
RaBitQ [11] and its extended version [10] provide theoretical error
bounds for bitwise quantization with flexible compression rates.
SymphonyQG [13] integrates quantization codes directly with
graph structures to reduce memory access overhead, while Lo-
RANN [19] utilizes low-rank matrix factorization for compression.
In terms of system architecture, Tagore [29] leverages GPUs for ac-
celerating graph index construction. For distributed environments,
HARMONY [50] employs a multi-granularity partition strategy to
balance load. WebANNS [32] enables efficient search within web
browsers via WebAssembly. From a theoretical perspective, Indyk
and Xu [18] analyze the worst-case performance limits of popular
implementations. Finally, DARTH [2] introduces declarative recall
targets through adaptive early termination to balance performance
and result quality. While these techniques reduce storage footprints
or distribute load, they predominantly operate on static memory
layouts that are brittle under frequent updates. SIVF addresses a
complementary challenge: it provides the dynamic memory sub-
strate that allows these scalable architectures to support real-time
streams without succumbing to VRAM fragmentation or locking
overheads.

GPU Acceleration. Recent HPC work highlights how careful ker-
nel and data-layout design can unlock GPU performance across
data-intensive workloads. FZ-GPU demonstrates a fully parallel
compression pipeline with both warp-aware bitwise operations and
shared-memory efficiency [53]. For sparse linear algebra, SpMV de-
signs reduce preprocessing overhead while improving load balance
and memory access locality [3], and GPU-aware preconditioning
further emphasizes locality and coalescence as first-order concerns
on modern GPU architectures [25]. Beyond compute kernels, GPU-
enabled asynchronous checkpoint caching and prefetching treat
GPU memory as a first-class tier to improve end-to-end throughput
for I/O-heavy workflows [36]. Format choices and composition are
also critical for irregular workloads, as shown by automatic sparse
format composition for SpMM that avoids expensive autotuning
while delivering strong performance [41]. Another line of work fo-
cuses on reliability, debugging, and cluster-scale GPU management,
which together shape how GPU-centric systems are built and op-
erated. GPU-FPX provides low-overhead floating-point exception
tracking for NVIDIA GPUs [28], FPBOXer improves scalable input
generation for triggering floating-point exceptions in GPU pro-
grams [45], and FloatGuard extends whole-program exception de-
tection to AMD GPUs and highlights cross-vendor portability con-
cerns [37]. At the application and cluster level, SIMCoV-GPU studies
multi-node, multi-GPU acceleration for irregular agent-based sim-
ulations [26], FASOP automates fast search for near-optimal trans-
former parallelization on heterogeneous GPU clusters [17], and

serverless platforms motivate GPU sharing and scheduling mecha-
nisms such as ESG and FluidFaaS [15, 16]. However, applying these
general-purpose HPC optimizations to vector search remains non-
trivial due to the irregular memory access patterns of IVF traversal.
SIVF bridges this gap by tailoring these micro-architectural princi-
ples, specifically warp-aligned slabs and lock-free synchronization,
to construct the first GPU-resident index capable of sustaining
high-velocity updates without compromising retrieval integrity.

3 Design and Implementation of SIVF
This section presents the design and implementation of SIVF for
high-concurrency updates on GPUs. We first introduce the Slab-
based Dynamic Memory Allocator (SDMA) in Section 3.1, which
represents each IVF list as a linked chain of fixed-capacity slabs
with per-list head pointers 𝐻 [·] and per-slab metadata

(next, valid_count, validity_bitmap),

summarized in Algorithm 1. Building on SDMA, we describe the
parallel ingestion (Section 3.2) in which each thread inserts one
vector by reserving a slot via atomicCAS on valid_count and pub-
lishing visibility by setting a validity bit after __threadfence()
(Algorithm 2). We then present a warp-cooperative search (Sec-
tion 3.3) that assigns one warp to one query and evaluates one slab
per traversal step by consulting the validity bitmap before reading
payloads (Algorithm 3). We detail lazy eviction (Section 3.4), which
performs constant-time deletion by looking up coordinates in the
address table T and atomically clearing the corresponding bitmap
bit (Algorithm 4). We demonstrate the theoretical properties of SIVF
in Section 3.5 and discuss implementation details in Section 3.6.

Data Model and Assumptions. To ensure 𝑂 (1) address resolution
without hashing collisions, SIVF operates on a dense identifier
space 𝑣𝑖𝑑 ∈ [0, 𝑁𝑚𝑎𝑥 ), where 𝑁𝑚𝑎𝑥 is the pre-configured capacity.
In production environments, sparse or non-integer external IDs
(e.g., 64-bit UUIDs) are mapped to this internal dense range via a
lightweight host-side registry. Furthermore, SIVF enforces strong
consistency for data updates via a “delete-then-insert” semantic:
overwriting an existing 𝑣𝑖𝑑 involves atomically clearing its existing
validity bit (logical deletion) before the new payload becomes visible.
This design ensures that the validity bitmap serves as the single
source of truth for searchers.

3.1 Slab-based Memory Management
We propose a Slab-based Dynamic Memory Allocator (SDMA)
that replaces monolithic, variable-length inverted lists with linked
chains of fixed-size blocks on GPU. SDMA pre-allocates a contigu-
ous slab pool; each slab stores up to 𝐶 vectors and a lightweight
metadata header 𝑀 = ⟨𝑛𝑛𝑒𝑥𝑡, 𝑏𝑣𝑎𝑙𝑖𝑑, cnt⟩, where 𝑛𝑛𝑒𝑥𝑡 is the next-
slab pointer, 𝑏𝑣𝑎𝑙𝑖𝑑 is a 𝐶-bit validity bitmap, and cnt tracks the
number of active vectors. We set 𝐶 = 32 to match the GPU warp
size. Each IVF list ℓ is represented by a head pointer 𝐻 [ℓ] to the first
slab in its chain. Algorithm 1 summarizes these core primitives.

Allocation draws a fresh slab id from a global stack pointer 𝑃𝑡𝑜𝑝
via 𝑠 = atomicSub(𝑃𝑡𝑜𝑝, 1) − 1, initializes its metadata, and links
it to the list head 𝐻 [ℓ] using an atomic compare-and-swap (CAS)
operation. Insertion for a vector id 𝑣𝑖𝑑 first resolves the target slab

Algorithm 1 Core operations of SDMA

1: Global State: slab pool metadata and data, per-list head point-

ers 𝐻 [·], stack pointer 𝑃top, address table T

2: Input: vector identifier 𝑣id, vector 𝑥, list assignment ℓ
3: procedure Insert(𝑣id, 𝑥, ℓ)
4:

𝑠 ← 𝐻 [ℓ]
while 𝑠 is invalid or no free slot exists in slab 𝑠 do

𝑠new ← atomicSub(𝑃top, 1) − 1
Initialize metadata 𝑠new with 𝑏valid = 0, 𝑛next = 𝑠
Update 𝐻 [ℓ] to 𝑠new via atomicCAS
𝑠 ← 𝐻 [ℓ]

end while
Reserve a free slot 𝑜 in slab 𝑠 via atomic update of 𝑐valid
Write 𝑥 to slab data[𝑠][𝑜]
Atomically set bit 𝑜 in 𝑏valid
T (𝑣id) ← ⟨𝑠, 𝑜⟩

14:
15: end procedure
16: procedure Delete(𝑣id)
⟨𝑠, 𝑜⟩ ← T (𝑣id)
17:
if ⟨𝑠, 𝑜⟩ ≠ INVALID then

18:

𝑜𝑙𝑑_𝑚𝑎𝑝 ← Atomically clear bit 𝑜 in 𝑏valid of slab 𝑠
if bit 𝑜 was set in 𝑜𝑙𝑑_𝑚𝑎𝑝 then

T (𝑣id) ← INVALID
𝑜𝑙𝑑_𝑐𝑛𝑡 ← atomicSub(&slab_meta[𝑠].cnt, 1)
if 𝑜𝑙𝑑_𝑐𝑛𝑡 == 1 then

Atomically push 𝑠 back to 𝑃top stack
slab_meta[𝑠].𝑏valid ← 0

end if

end if

5:

6:

7:

8:

9:

10:

11:

12:

13:

19:

20:

21:

22:

23:

24:

25:

26:

27:

28:
end if
29: end procedure

𝑠, reserves a free slot 𝑜, writes the payload, and finally commits
visibility by atomically setting bit 𝑜 in 𝑏𝑣𝑎𝑙𝑖𝑑 .

To support 𝑂 (1) physical deletion without expensive garbage
collection, SDMA maintains an address table T mapping each id
to its physical coordinate T (𝑣𝑖𝑑 ) = ⟨𝑠, 𝑜⟩. The deletion operation
performs a direct lookup and atomically clears bit 𝑜 in 𝑏𝑣𝑎𝑙𝑖𝑑 . Unlike
tombstone-based designs, SDMA performs immediate reclamation:
it atomically decrements the slab’s occupancy counter cnt. If cnt
drops to zero, the slab is instantly recycled by pushing it back to
the global free stack 𝑃𝑡𝑜𝑝 , making it available for future insertions.

3.2 Lock-free Parallel Ingestion
SIVF uses a fully parallel ingestion kernel in which each CUDA
thread inserts one vector into its assigned IVF list ℓ. Each list is
a singly linked chain of fixed-capacity slabs, with head pointer
𝐻 [ℓ] and per-slab metadata valid_count, validity_bitmap, and
next. Insertion follows a reserve-write-publish protocol. A thread
first reads the current head slab ℎ = 𝐻 [ℓ] and attempts to re-
serve a slot by incrementing slab_meta[ℎ].valid_count using
atomicCAS; the reserved slot index is the old counter value 𝑐. On
success, the thread writes the payload to slab data[ℎ][𝑐] and the
id to slab_ids[ℎ][𝑐], updates the address table T (𝑣𝑖𝑑 ) ← ⟨ℎ, 𝑐⟩,

Dongfang Zhao (dzhao@uw.edu)

then executes __threadfence() and sets the corresponding va-
lidity bit using atomicOr. The validity bit is the only publication
signal read by search, so this ordering ensures that a reader observ-
ing the bit set never sees partially initialized payload or a missing
table entry. If the head slab is absent or full, the thread allocates
a new slab id from the global pool via atomicSub on 𝑃𝑡𝑜𝑝 , initial-
izes its metadata (valid_count, validity_bitmap, next), executes
__threadfence(), and attempts to publish it as the new head with
atomicCAS(&H[ℓ], h, s_new). If head publication fails under
contention (i.e., another thread updated the head first), the thread
immediately reclaims the allocated slab to the global free list to
prevent memory leaks and retries the operation. If the slab pool is
exhausted, the insertion fails fast for that element and returns an
error to the caller, which can throttle the update stream or retry
later, rather than silently dropping updates. The full per-thread
protocol is described in Algorithm 2.

3.3 Coalesced Search on Non-Contiguous Slabs
SIVF stores each inverted list as a linked chain of fixed-capacity
slabs, which replaces contiguous scans with traversal via next. To
retain high GPU throughput, we use a warp-cooperative search
kernel that matches slab capacity to the warp width (𝐶 = 32). The
kernel launches one warp per query. The warp first stages the
query vector into shared memory, then probes 𝑛𝑝𝑟𝑜𝑏𝑒 coarse lists
returned by the quantizer. For each probed list ℓ, the warp traverses
the slab chain starting from 𝑠 = 𝐻 [ℓ]. At each slab 𝑠, lane 𝑗 consults
slab_meta[𝑠].validity_bitmap and evaluates slot 𝑗 only if the
corresponding bit is set. If set, the lane loads the payload from slab
data[𝑠][𝑗], retrieves the label from slab_ids[𝑠][𝑗], computes
the distance to the shared query, and updates a small per-lane top-𝑘
structure kept in registers. After traversal, lanes write their local
top-𝑘 candidates to shared memory and one lane merges them into
the final top-𝑘 result for the query. To ensure termination under
unexpected corruption, traversal is bounded and the kernel breaks
on self-loops. Algorithm 3 summarizes the procedure.

|

3.4 Lazy Eviction via Address Translation Table
SIVF supports constant-time deletion by combining an Address
Translation Table (ATT) with bitmap-based lazy eviction. The ATT
T maps each identifier 𝑢 to its physical coordinate in the slab pool
as a 64-bit value T [𝑢] = (idx𝑠𝑙𝑎𝑏 ≪ 32)
idx𝑠𝑙𝑜𝑡 , or INVALID
if absent. Given T [𝑢], a deletion thread decodes (idx𝑠𝑙𝑎𝑏, idx𝑠𝑙𝑜𝑡 )
and clears the corresponding bit in the slab validity bitmap us-
ing an atomic read-modify-write (atomicAnd with 𝑚𝑎𝑠𝑘 =∼ (1 ≪
idx𝑠𝑙𝑜𝑡 )). To handle duplicates and races, the kernel uses the pre-
update bitmap value to detect a 1 → 0 transition. Bookkeeping and
reclamation occur strictly on this transition: the thread decrements
the slab’s valid_count and marks T [𝑢] as INVALID. If the decre-
mented valid_count drops to zero, implying the slab has become
fully empty, the thread atomically pushes the slab index back to the
global free stack 𝑃𝑡𝑜𝑝 . This immediate reclamation strategy allows
SIVF to reuse memory for new insertions without requiring heavy
background compaction. Algorithm 4 summarizes the procedure.

SIVF: GPU-Resident IVF Index for Streaming Vector Analytics

Algorithm 2 Lock-free ingestion protocol in SIVF
1: Input: vector 𝑥, identifier 𝑣𝑖𝑑 , list assignment ℓ
2: Global: head array 𝐻 [·], slab_meta, slab_data, free list, stack

pointer 𝑃𝑡𝑜𝑝 , address table T

3: 𝑎𝑡𝑡𝑒𝑚𝑝𝑡𝑠 ← 0
4: while 𝑎𝑡𝑡𝑒𝑚𝑝𝑡𝑠 < MAX_INSERT_ATTEMPTS do
5:

𝑎𝑡𝑡𝑒𝑚𝑝𝑡𝑠 ← 𝑎𝑡𝑡𝑒𝑚𝑝𝑡𝑠 + 1
ℎ ← 𝐻 [ℓ]
if ℎ ≠ −1 then

𝑐 ← slab_meta[ℎ].valid_count
if 𝑐 < 𝐶 then

if atomicCAS(&slab_meta[ℎ].cnt, 𝑐, 𝑐 + 1) then

Write payload 𝑥 to slab_data[ℎ][𝑐]
Write identifier to slab_id_buffer[ℎ][𝑐]
T (𝑣𝑖𝑑 ) ← ⟨ℎ, 𝑐⟩
__threadfence()
atomicOr(&slab_meta[h].valid_bitmap, mask)
return

end if

end if

end if
𝑡 ← atomicSub(𝑃𝑡𝑜𝑝, 1)
if 𝑡 ≤ 0 then

atomicAdd(𝑃𝑡𝑜𝑝, 1)
return

end if
𝑠𝑛𝑒𝑤 ← free_list[𝑡 − 1]
Set slab_meta[𝑠𝑛𝑒𝑤].valid_count ← 1
Set slab_meta[𝑠𝑛𝑒𝑤].validity_bitmap ← 0
Set slab_meta[𝑠𝑛𝑒𝑤].next ← ℎ
__threadfence()
if atomicCAS(&𝐻 [ℓ], ℎ, 𝑠𝑛𝑒𝑤) == ℎ then
Write payload 𝑥 to slab_data[𝑠𝑛𝑒𝑤][0]
Write identifier to slab_id_buffer[𝑠𝑛𝑒𝑤][0]
T (𝑣𝑖𝑑 ) ← ⟨𝑠𝑛𝑒𝑤, 0⟩
__threadfence()
atomicOr(&slab_meta[s_new].validity_bitmap)
return

else

𝑡𝑟𝑒𝑡 ← atomicAdd(𝑃𝑡𝑜𝑝, 1)
free_list[𝑡𝑟𝑒𝑡 ] ← 𝑠𝑛𝑒𝑤

6:

7:

8:

9:

10:

11:

12:

13:

14:

15:

16:

17:

18:

19:

20:

21:

22:

23:

24:

25:

26:

27:

28:

29:

30:

31:

32:

33:

34:

35:

36:

37:

38:

39:

40:
end if
41: end while

3.5 Theoretical Analysis
3.5.1 Correctness. We prove three properties. The first establishes
the correctness of parallel ingestion in Algorithm 2. The second
shows that search in Algorithm 3 is safe under concurrent ingestion
and deletion. The third proves that lazy eviction in Algorithm 4 is
linearizable with a clear linearization point.

We use the same state as the pseudocode. For each list id ℓ, 𝐻 [ℓ]
stores the head slab id. Each slab 𝑠 has metadata slab_meta[𝑠] in-
cluding next, valid_count, and a 32-bit validity_bitmap. A slot
(𝑠, 𝑜) is logically present if and only if bit 𝑜 in the bitmap is 1. Pay-
loads and ids are stored in slab_data[𝑠][𝑜] and slab_ids[𝑠][𝑜].

Algorithm 3 Warp-cooperative search in SIVF

1: Input: queries 𝑄, probed list ids 𝑐𝑜𝑎𝑟𝑠𝑒_𝑖𝑑𝑠, head array 𝐻 [·]
2: Input: slab metadata and data, buffer 𝑠𝑙𝑎𝑏_𝑖𝑑𝑠, 𝑘, 𝑛𝑝𝑟𝑜𝑏𝑒
3: Output: top-𝑘 distances and labels for each query
4: for each query index 𝑞 in parallel do
Launch one warp for query 𝑞
5:
Copy 𝑄 [𝑞] into shared memory
Initialize per-thread local top-𝑘 lists in registers
for 𝑝 = 0 to 𝑛𝑝𝑟𝑜𝑏𝑒 − 1 do
ℓ ← 𝑐𝑜𝑎𝑟𝑠𝑒_𝑖𝑑𝑠 [𝑞, 𝑝]
if ℓ is invalid then
continue

6:

7:

8:

9:

10:

11:

12:

13:

14:

15:

16:

17:

18:

19:

20:

21:

22:

23:

24:

25:

26:

27:

28:

end if
𝑠 ← 𝐻 [ℓ]
while 𝑠 is valid and traversal bound not exceeded do

𝑚𝑑 ← 𝑠𝑙𝑎𝑏_𝑚𝑒𝑡𝑎[𝑠]
if 𝑚𝑑.𝑛𝑒𝑥𝑡 = 𝑠 then

break

end if
if 𝑗 < 32 and 𝑚𝑑.𝑣𝑎𝑙𝑖𝑑𝑖𝑡𝑦_𝑏𝑖𝑡𝑚𝑎𝑝 [ 𝑗] is set then

Load vector x𝑠,𝑗 from slab data
Compute 𝑑 (q, x𝑠,𝑗 )
𝑖𝑑 ← 𝑠𝑙𝑎𝑏_𝑖𝑑𝑠 [𝑠, 𝑗]
Insert (𝑑, 𝑖𝑑) into local top-𝑘

end if
𝑠 ← 𝑚𝑑.𝑛𝑒𝑥𝑡

end while

end for
Write local top-𝑘 lists to shared memory
One thread merges 32 lists and writes final top-𝑘 outputs

29:
30: end for

The address table T maps a vector id 𝑢 to a coordinate (𝑠, 𝑜) encoded
in coord, or INVALID.

Theorem 3.1 (Parallel ingestion is safe and linearizable). Consider
any concurrent execution of Algorithm 2. For every insertion that
returns successfully, there exists a unique slot (𝑠, 𝑜) such that: (i) the
insertion operation writes the payload and id into that slot, then sets
bit 𝑜 in validity_bitmap exactly once, (ii) once the bit is set, the slot
contains a fully initialized payload and id, and (iii) the insertion can
be linearized at the atomic bit set operation atomicOr that makes the
slot visible.

Proof. We first argue the uniqueness of the chosen slot for a

successful insertion.

In the existing head case, the code reads

𝑐 = slab_meta[ℎ].valid_count,
and attempts to reserve index 𝑐 using an atomic compare-and-swap
(CAS). Since the CAS operation atomically verifies that the count is
still 𝑐 before incrementing it to 𝑐 +1, only one thread can succeed for
any specific snapshot of the counter. Therefore, among concurrent
contenders for the same slab ℎ, at most one insertion obtains a
given index 𝑐. In the new slab case, the thread publishes its new
slab as the head using atomicCAS(&H[ℓ], h, s_new); only one
thread can win this publication for a fixed old head value ℎ, and

Algorithm 4 Lazy eviction with slab-wise reclamation in SIVF

1: Input: deletion identifiers 𝑈 = {𝑢1, . . . , 𝑢𝑚 }
2: Global: Address Table T , slab metadata, free list, stack pointer

𝑃𝑡𝑜𝑝

3: for each 𝑢 in 𝑈 in parallel do
4:

𝑐𝑜𝑜𝑟𝑑 ← T [𝑢]
if 𝑐𝑜𝑜𝑟𝑑 == INVALID then

5:

6:

7:

8:

9:

10:

11:

12:

13:

14:

15:

16:

17:

18:

19:

continue

end if
idx𝑠𝑙𝑎𝑏 ← 𝑐𝑜𝑜𝑟𝑑 ≫ 32
idx𝑠𝑙𝑜𝑡 ← 𝑐𝑜𝑜𝑟𝑑 & (232 − 1)
𝑚𝑎𝑠𝑘 ← ∼ (1 ≪ idx𝑠𝑙𝑜𝑡 )
𝑜𝑙𝑑_𝑚𝑎𝑝 ← atomicAnd(slab[idx𝑠𝑙𝑎𝑏 ].bitmap, 𝑚𝑎𝑠𝑘)
if ((𝑜𝑙𝑑_𝑚𝑎𝑝 ≫ idx𝑠𝑙𝑜𝑡 ) & 1) == 1 then

𝑜𝑙𝑑_𝑐𝑛𝑡 = atomicSub(&slab_meta[idx𝑠𝑙𝑎𝑏 ].cnt, 1)
T [𝑢] ← INVALID
if 𝑜𝑙𝑑_𝑐𝑛𝑡 == 1 then

𝑡 ← atomicAdd(𝑃𝑡𝑜𝑝, 1)
free_list[𝑡] ← idx𝑠𝑙𝑎𝑏
slab_meta[idx𝑠𝑙𝑎𝑏 ].bitmap ← 0

end if

end if

20:
21: end for

the winner uses slot 𝑜 = 0 in its newly allocated slab. Thus, every
successful insertion selects exactly one slot (𝑠, 𝑜).

We next argue that the chosen slot is initialized before it be-
comes visible. In both code paths, after reserving the slot, the
writer performs the payload write to slab_data[𝑠][𝑜] and the
id write to slab_ids[𝑠][𝑜], then writes T (𝑣𝑖𝑑 ) ← ⟨𝑠, 𝑜⟩, executes
__threadfence(), and only after the fence performs atomicOr
to set bit 𝑜 in the bitmap. The memory consistency semantics of
__threadfence() ensure that all prior global writes are committed
to memory before any subsequent atomic operation by the same
thread becomes visible to other threads. Therefore, any observer
that sees bit 𝑜 as set is guaranteed to see the fully initialized payload
and id.

Finally, we justify linearizability of a successful insertion with the
atomic bit set as the linearization point. The membership predicate
used throughout the design is exactly the bitmap bit. Before the
atomicOr, the bit is 0, so the slot is logically absent to any search
warp. After the atomicOr takes effect, the bit is 1, so the slot is
logically present. Since atomicOr executes atomically on the bitmap
word, the state transition 0 → 1 occurs at a single instant. At
that instant, the slot becomes visible and, by the fence ordering
established above, it is valid. Thus, the insertion is linearizable. □

Theorem 3.2 (Search safety under concurrent ingestion and dele-
tion). In any concurrent execution of Algorithms 2, 3, and 4, every
payload and id read performed by Algorithm 3 is fully initialized.

Proof. Algorithm 3 reads a slot (𝑠, 𝑗) only if it first observes
that bit 𝑗 in slab_meta[𝑠].validity_bitmap is set. When the
search observes the bit set, the slot must have been published by a
successful insertion. By Theorem 3.1, the publication point is the
atomic bit set in Algorithm 2, and the payload and id writes occur

Dongfang Zhao (dzhao@uw.edu)

before the fence, which ensures they complete before the bit set.
The same memory consistency guarantee implies that once the bit
set is visible to a search warp, the earlier payload and id writes
are also visible. Therefore, the search cannot observe a partially
initialized payload or id.

Deletion does not write payloads or ids. Algorithm 4 only clears
the validity bit and, upon slab reclamation, resets the bitmap to 0
before returning the slab to the free pool. Hence, even if a search
races with a delete or a subsequent slab reuse, the primary guard is
the bitmap state. If the search sees the bit as 0, it skips the slot. If it
sees the bit as 1, it reads a payload and id that were fully initialized
before the corresponding bitmap set operation (whether from the
original insertion or a reuse). In neither case does the search read
corrupted or partially written data.

Algorithm 3 also terminates because its traversal is bounded,
and it includes an explicit self-loop guard (md.next == s) before
following next. Concurrent insertions can add a new head slab, but
they do not require the search to revisit already visited slabs within
□
the traversal bound.

Theorem 3.3 (Lazy eviction is linearizable and makes deleted vec-
tors invisible). Consider any concurrent execution of Algorithms 3
and 4. For any delete request on 𝑢 such that T [𝑢] ≠ INVALID and
decodes to (idx𝑠𝑙𝑎𝑏, idx𝑠𝑙𝑜𝑡 ), define

𝑚𝑎𝑠𝑘 = ∼(1 ≪ idx𝑠𝑙𝑜𝑡 ).
Then the atomic operation 𝑜𝑙𝑑_𝑚𝑎𝑝 ← 𝑎𝑡𝑜𝑚𝑖𝑐𝐴𝑛𝑑 () in Algorithm 4
constitutes the linearization point for logical deletion. After this atomic
operation takes effect, the slot becomes logically absent from the search
space. Repeated deletes of the same id are idempotent and safe.

Proof. If T [𝑢] = INVALID, Algorithm 4 performs no state

change and the delete is linearized at the INVALID check.

Otherwise, the delete decodes coord into (idx𝑠𝑙𝑎𝑏, idx𝑠𝑙𝑜𝑡 ), com-

putes 𝑚𝑎𝑠𝑘, and executes

𝑜𝑙𝑑_𝑚𝑎𝑝 ← atomicAnd(slab_meta[idx𝑠𝑙𝑎𝑏 ].bitmap, 𝑚𝑎𝑠𝑘)

to clear the corresponding bit. Since atomicAnd is an atomic read-
modify-write instruction on the GPU, the transition of the validity
bit from 1 to 0 (or 0 to 0) occurs at a single, indivisible instant. We
designate this instant as the linearization point.

Algorithm 3 uses the validity bit as the sole membership predi-
cate. Because the search warp reads the bitmap atomically before
accessing any payload, any search that observes the bitmap after
the linearization point will see the bit as 0, skip the slot, and ex-
clude the vector from the results. Physical payload reclamation is
not required for correctness because logical membership is fully
determined by the validity bit.

To handle duplicates, Algorithm 4 uses the return value old_cnt
to detect if it was the specific thread that caused the 1 → 0 transi-
tion. If so, it performs bookkeeping (e.g., updating counters). If the
bit was already 0, the operation is effectively a no-op on the logical
□
state. Thus, the deletion mechanism is idempotent.

3.5.2 Time Complexity. We analyze the time complexity relative
to the total number of vectors 𝑁 , the number of lists 𝑛𝑙𝑖𝑠𝑡 , and
dimensionality 𝐷. For ingestion, SIVF guarantees strict 𝑂 (1) time
complexity as it requires only atomic counter updates and pointer

SIVF: GPU-Resident IVF Index for Streaming Vector Analytics

manipulation to append data, independent of the current list size.
Similarly, deletion achieves 𝑂 (1) complexity by utilizing the Ad-
dress Translation Table for constant-time lookup followed by a
single atomic bitmap invalidation, completely eliminating the need
for memory compaction or data movement. For search, the com-
plexity remains 𝑂 (𝑛𝑝𝑟𝑜𝑏𝑒 · (𝑁 /𝑛𝑙𝑖𝑠𝑡 ) · 𝐷), where 𝑛𝑝𝑟𝑜𝑏𝑒 is the
user-configured number of lists to scan; while the linked-slab lay-
out introduces minor pointer-chasing overhead, it preserves the
asymptotic complexity class of inverted file search.

Space Complexity. The total space complexity is dominated
3.5.3
by the vector payload, scaling linearly as 𝑂 (𝑁 · 𝐷). The structural
overhead consists of the Address Translation Table (𝑂 (𝑁 ), 8 bytes
per entry) and slab metadata. Since metadata is amortized over the
fixed slab capacity (𝐶 = 32), its footprint is negligible compared to
high-dimensional payloads. Regarding memory efficiency, unlike
dynamic arrays that typically reserve up to 2× capacity to amortize
resizing costs, SIVF grows in fine-grained increments of single slabs.
Although lazy deletion introduces sparse internal fragmentation
(unused slots within active slabs), the immediate reclamation of
fully empty slabs bounds this waste, ensuring the total memory
footprint remains proportional to the active dataset size.

3.6 System Implementation
We implement SIVF as a fully integrated extension to the GPU
components of the widely-adopted Faiss library [7]. Our implemen-
tation represents a significant systems engineering effort, involving
approximately 13,000 lines of code as of January 2026. The major-
ity of this codebase consists of optimized C++ and CUDA system
implementation (spanning the core Faiss integration, slab memory
management, and distributed MPI runtime), while the remaining
lines comprise Python and Bash utility scripts for experimental
orchestration. We have open-sourced the complete implementation
and evaluation scripts on GitHub.

The core architecture centers on the GpuIndexSIVF class, a di-
rect subclass of Faiss’s GpuIndex. This class integrates our custom
SlabManager to orchestrate dynamic memory on the GPU. Un-
like standard static models, SlabManager maintains a monolithic
memory pool and a device-side free list stack, enabling both warp-
aligned allocation and 𝑂 (1) slab recycling without host interven-
tion. To support high-concurrency operations, we implemented spe-
cialized GPU-native kernels for insertion, deletion, and search (en-
capsulated in SIVFAppend, SIVFDelete, and SIVFSearch). These
operators interact with lock-free metadata structures via atomic
state transitions to ensure data consistency during simultaneous
read and write access.

Integrating these dynamic components into the static resource
management of Faiss presented multiple challenges. Unlike stan-
dard Faiss indices which rely on flat arrays managed through the
DeviceTensor class, SIVF implements its own allocator to mini-
mize fragmentation overhead. We reconcile this by overriding the
virtual addImpl and searchImpl methods, allowing SIVF to serve
as a drop-in replacement in existing pipelines. Furthermore, our
design adheres to the GpuResources context provided by Faiss.

3.7 Distributed Scale-out Architecture
To support large-scale datasets exceeding single-device memory
capacity, we extended SIVF with a shared-nothing, data-parallel
distributed architecture.

The global dataset is partitioned into disjoint shards, distributed
across 𝑃 GPU workers. Unlike model-parallel approaches that split
inverted lists across devices (which incurs heavy synchronization
overheads during ingestion), SIVF employs Data Sharding. Incom-
ing vectors are routed to workers via a deterministic partitioning
capabilities (e.g., round-robin or hash-based routing). This allows
each GPU to ingest data into its local SIVF index independently,
enabling the aggregate ingestion throughput to scale linearly with
the cluster size, as evidenced in our evaluation (Section 4.7).

Query processing follows a Scatter-Gather pattern. The client
broadcasts the query vector to all workers via MPI. Each worker
performs a warp-cooperative search on its local shard to retrieve
the top-𝑘 candidates. A global reduction step (implemented via
MPI_Gather or tree-based reduction) merges the partial results to
produce the final global top-𝑘. For deletion, since SIVF maintains a
dense ID space, deletion requests are broadcast to all workers. Each
worker checks its local Address Translation Table (ATT). Due to
the disjoint partitioning, the target ID exists on at most one worker,
which then executes the lock-free lazy eviction locally.

4 Evaluation
4.1 Experimental Setup
To ensure a comprehensive evaluation, we adopt a two-tiered base-
line strategy. First, our primary baseline is the standard Faiss GPU
IVF, which serves as a direct architectural counterpart; this allows
us to isolate the performance gains specifically attributable to our
proposed memory management innovations, excluding confound-
ing factors from differing algorithmic paradigms. Second, to posi-
tion SIVF within the broader indexing landscape, we in Section 4.6
compare against representative non-IVF indices, including GPU
CAGRA [39] (dynamic graph), GPU Flat (brute-force), HNSW [35]
(dynamic graph), NSG [9] (static graph), and LSH [5] (hashing).

Most experiments were conducted on a bare-metal node from
the Chameleon Cloud testbed [24] (CHI@UC site). The platform
is equipped with dual-socket Intel Xeon Gold 6126 CPUs (Skylake
microarchitecture), providing a total of 24 physical cores (48 threads
with Hyper-Threading) clocked at 2.60 GHz. The host memory
consists of 192 GiB of RAM. For acceleration, the node features an
NVIDIA Quadro RTX 6000 GPU with 24 GB of GDDR6 VRAM. The
system runs on a Ubuntu 24.04 environment with the CUDA toolkit
installed: Driver ver. 560.35.05 and CUDA ver. 12.6. Each reported
data point represents the average of at least three independent
executions. Error bars are omitted in figures where the standard
deviation is negligible to maintain visual clarity.

4.2 Microbenchmarks
Ingestion. We evaluate ingestion throughput against the stan-
4.2.1
dard Faiss GPU IVFFlat baseline, varying database size (𝑁𝐵: 1M–
4M) and cluster count (𝑛𝑙𝑖𝑠𝑡 : 1024–16384). As shown in Figure 2,
SIVF achieves consistent performance advantages with up to 2.65×
speedup.

Dongfang Zhao (dzhao@uw.edu)

or 𝑠𝑙), and (iii) deletion batch size (𝑏). These control logical head-
room, pre-allocated memory for bursts, and the trade-off between
amortization and freshness. Figures 4 and 5 summarize the results.
Figures 4 and 5 illustrate the impact of pre-allocation strate-
gies and batch sizes on system performance. Insertion through-
put correlates positively with memory provisioning, peaking at
3.23M vec/s with a 𝑚𝑎𝑥𝑣𝑒𝑐_𝑓 𝑎𝑐𝑡𝑜𝑟 of 1.5 and larger batches, as gen-
erous pre-allocation minimizes dynamic resizing and contention.
While deletion throughput is sensitive to batching under tight con-
straints (dropping to 1.08M vec/s), increasing the 𝑠𝑙𝑎𝑏_𝑓 𝑎𝑐𝑡𝑜𝑟 or
𝑚𝑎𝑥𝑣𝑒𝑐_𝑓 𝑎𝑐𝑡𝑜𝑟 effectively decouples performance from resource
limitations, stabilizing throughput at ≈1.7M vec/s. End-to-end la-
tency remains robust across all settings, with insertions ranging
from 3.09–3.69 ms and deletions achieving sub-millisecond perfor-
mance (0.58–0.93 ms). This 3×–5× speed advantage for deletions
stems from SIVF’s lock-free bitmap mechanism, while the observed
latency reduction with larger batches confirms that amortizing ker-
nel launch overheads is a key driver for high-velocity streaming
mutations.

4.3 Real-world Datasets
We benchmark SIVF using four popular real-world datasets rep-
resenting diverse modalities and varying degrees of cluster skew-
ness: Deep1B [51] (96 dimensions, deep features, imbalance fac-
tor I = 1.23), SIFT1M [23] (128 dimensions, vision, I = 1.24),
T2I-1B [43] (200 dimensions, multimodal/RAG, I = 1.21), and
GIST1M [23] (960 dimensions, high-dim features, I = 1.76). The
high imbalance factor of GIST1M, in particular, stresses the al-
locator’s ability to handle non-uniform distributions. While the
subset size (1M vectors) fits within GPU memory, these experi-
ments validate performance within the active window of streaming
applications. Section 4.4 will report their stability under high-churn
workloads.

As shown in Figure 6, SIVF dominates ingestion scalability across
all dimensions. On Deep1B, SIVF achieves a peak throughput of
4.38M vec/s (120× speedup over the baseline’s 36.4K vec/s). This ad-
vantage persists on SIFT1M (3.78M vec/s, 105×) and T2I-1B (2.91M
vec/s, 84×). Even on high-dimensional GIST1M, SIVF maintains
852.7K vec/s (36× speedup), confirming that our pre-allocated slab
architecture effectively saturates GPU bandwidth by eliminating
dynamic resizing overhead.

Figure 7 highlights the critical performance divergence. Base-
line latency scales poorly due to CPU-GPU roundtrips, varying
from 1.2s (Deep1B) to 11.8s (GIST1M). In contrast, SIVF’s in-place
bitmap updates decouple latency from dimension, maintaining sub-
millisecond performance (< 0.9 ms) across all datasets. Notably on
GIST1M, SIVF reduces latency from 11,843 ms to 0.89 ms, a 13, 307×
improvement, validating its feasibility for real-time streams.

Figure 8 compares query throughput across diverse datasets.
The results demonstrate that SIVF fundamentally overcomes the
performance bottleneck typical of dynamic indexing without com-
promising retrieval accuracy. On Deep1B, SIVF outperforms the
baseline by 2.07x (59.8K vs 28.9K QPS). On SIFT1M, it retains a 1.5x
lead (40.9K vs 26.7K QPS), while on T2I-1B, it provides competi-
tive performance reaching 10.8K QPS. While microbenchmarks in
sparse scenarios (e.g., 𝑛𝑙𝑖𝑠𝑡 = 16384) may show efficiency ratios

Figure 2: Microbenchmark performance of vector ingestion.

Figure 3: Microbenchmark performance of vector deletion.

As shown in Fig. 2a, SIVF maintains a stable throughput of
≈4.2M vec/s as 𝑁𝐵 increases, significantly outperforming the base-
line (≈1.7M vec/s). This stability validates our lock-free SlabMan-
ager, which ensures 𝑂 (1) insertion cost independent of index oc-
cupancy, thereby avoiding the contiguous memory resizing over-
heads inherent to the baseline. While the baseline throughput de-
grades monotonically as 𝑛𝑙𝑖𝑠𝑡 increases (dropping from 2.2M to
1.7M vec/s), Fig. 2b shows that SIVF exhibits a performance sweet
spot at 𝑛𝑙𝑖𝑠𝑡 = 2048, peaking at 5.3M vec/s. At this optimal gran-
ularity, SIVF achieves a 2.65× speedup over the baseline. Even at
high 𝑛𝑙𝑖𝑠𝑡 = 4096, where scattered memory writes typically hin-
der performance, SIVF maintains robust throughput at 4.2M vec/s,
sustaining a 2.47× advantage over the baseline’s 1.7M vec/s. As
shown in Fig. 2c, SIVF outperforms the baseline across all configu-
rations, with speedups typically ranging from 2.4× to 2.9×. Even
under maximum contention (4M vectors, 𝑛𝑙𝑖𝑠𝑡 = 1024), SIVF retains
a 1.79× advantage, confirming the efficiency of the non-blocking,
slab-based pipeline for streaming scenarios.

4.2.2 Deletion. We evaluate the efficiency of the vector deletion
mechanism in SIVF by comparing it against the standard Faiss GPU
IVF baseline. The experiment measures latency and throughput
when removing a batch of 10,000 vectors from a populated index
of one million 128-dimensional vectors.

Figure 3 illustrates the performance comparison between the two
methods. The results indicate that the baseline Faiss implementation
incurs a substantial deletion latency of approximately 202.2 ms. In
stark contrast, SIVF completes the same batch deletion operation in
an average of 0.68 ms. This represents a massive speedup of 298.5×.
Correspondingly, deletion throughput surges from 4.9 × 104 vec/s
in the baseline to nearly 1.5 × 107 vec/s in SIVF.

4.2.3 Parameter Sensitivity and Ablation Study. We evaluate system
robustness by sweeping three parameters: (i) vector capacity fac-
tor (𝑚𝑎𝑥𝑣𝑒𝑐_𝑓 𝑎𝑐𝑡𝑜𝑟 , or 𝑚𝑣), (ii) slab pool redundancy (𝑠𝑙𝑎𝑏_𝑓 𝑎𝑐𝑡𝑜𝑟 ,

1M2M4MDatabase Size01234567Throughput (M vec/s)(a) ScalabilitySIVFVanilla102420484096Clusters (nlist)012345674.05.34.22.22.01.7(b) GranularitySIVFVanilla1M2M4MDatabase Size102420484096Clusters (nlist)2.76x2.88x1.79x2.85x2.09x2.61x2.51x2.40x2.48x(c) Speedup Factor1.82.02.22.42.62.8Speedup FactorFaiss IVF(Baseline)SIVF(Ours)10−1100101102103Deletion Latency (ms)202.2 ms0.677 ms298x Faster(a) Latency (Lower is Better)Faiss IVF(Baseline)SIVF(Ours)104105106107108Throughput (vecs/sec)4.9e+041.5e+07(b) Throughput (Higher is Better)SIVF: GPU-Resident IVF Index for Streaming Vector Analytics

Figure 4: Throughput sensitivity analysis.

Figure 5: Latency sensitivity analysis.

Figure 6: Ingestion throughput.

Figure 7: Deletion latency.

Figure 8: Search performance (QPS).

achieves strict recall parity, reaching identical maximum recall tar-
gets such as 95.2% on GIST1M and 94.1% on T2I-1B. This validates
that the non-contiguous slab architecture introduces no precision
loss. Second, SIVF maintains its throughput advantage even as the
search depth increases to target high recall regimes. The slab man-
agement layer ensures high memory coalescing efficiency during
vector traversal, which effectively masks the latency inherent in
pointer chasing. Third, the consistent gap between the SIVF and
baseline curves across the entire recall spectrum suggests that the
system successfully eliminates the traditional trade-off between
index flexibility and search performance.

4.4 End-to-End Streaming Performance
Sliding window. We evaluate real-time applicability using a
4.4.1
Sliding Window benchmark that mimics production streams. The
system maintains a fixed active window (𝑊 ) by ingesting a new
batch (𝐵) and evicting the oldest batch (𝐵) at each step. We test on
SIFT1M (𝑊 = 200K, 𝐵 = 10K) and GIST1M (𝑊 = 100K, 𝐵 = 5K).

As shown in Figure 10, the standard Faiss baseline suffers from
high latency due to the CPU-GPU roundtrip required for index
reconstruction, causing system freezes of 355 ms (SIFT1M) and
> 1.1 s (GIST1M) per update. In contrast, SIVF executes updates
strictly in VRAM via slab-based management, reducing per-step
latency to ≈ 2.2 ms (SIFT1M) and 4.2 ms (GIST1M). This yields
speedups of 163× and 262×, respectively. Notably, the performance
gap widens with dimensionality (GIST1M), where the baseline is
bottlenecked by PCIe saturation. SIVF eliminates this bottleneck,
maintaining single-digit millisecond latency and transforming the
GPU IVF index into a real-time streaming engine.

Long-term streaming. To validate SIVF’s stability under long-
4.4.2
term streaming, we conducted a fine-grained benchmark with a
reduced batch size of 𝐵 = 1, 000 over 1,000 continuous steps. As

Figure 9: Throughput-Recall Pareto frontier analysis across
four datasets (Deep1B, SIFT1M, T2I-1B, and GIST1M).

between 0.40x and 0.52x due to the physical trade-off of pointer
chasing, SIVF demonstrates that query performance on real world
datasets is highly adjustable through the 𝑛𝑙𝑖𝑠𝑡 and 𝑛𝑝𝑟𝑜𝑏𝑒 parame-
ters. By optimizing the coarse quantizer granularity, such as setting
𝑛𝑙𝑖𝑠𝑡 = 8192 for GIST1M and 𝑛𝑙𝑖𝑠𝑡 = 4096 for T2I-1B, SIVF maintains
parity or superior query throughput even as search reaches high
recall regimes.

Figure 9 illustrates the trade-off between query throughput and
retrieval quality measured by Recall@10. The results confirm that
SIVF provides a strictly superior operational envelope compared
to the contiguous baseline across all tested dimensions. First, SIVF

mv:1.1sl:1.0b:1024mv:1.1sl:1.0b:8192mv:1.1sl:1.3b:1024mv:1.1sl:1.3b:8192mv:1.5sl:1.0b:1024mv:1.5sl:1.0b:8192mv:1.5sl:1.3b:1024mv:1.5sl:1.3b:81920.00.51.01.52.02.53.03.54.0Throughput (M vec/s)2.712.882.912.932.952.942.943.23(a) Insertion Throughputmv:1.1sl:1.0b:1024mv:1.1sl:1.0b:8192mv:1.1sl:1.3b:1024mv:1.1sl:1.3b:8192mv:1.5sl:1.0b:1024mv:1.5sl:1.0b:8192mv:1.5sl:1.3b:1024mv:1.5sl:1.3b:81920.00.51.01.52.0Throughput (M vec/s)1.081.581.631.691.711.681.691.66(b) Deletion Throughputmv:1.1sl:1.0b:1024mv:1.1sl:1.0b:8192mv:1.1sl:1.3b:1024mv:1.1sl:1.3b:8192mv:1.5sl:1.0b:1024mv:1.5sl:1.0b:8192mv:1.5sl:1.3b:1024mv:1.5sl:1.3b:819201234Latency (ms)3.693.473.443.423.393.403.403.09(a) Insertion Latencymv:1.1sl:1.0b:1024mv:1.1sl:1.0b:8192mv:1.1sl:1.3b:1024mv:1.1sl:1.3b:8192mv:1.5sl:1.0b:1024mv:1.5sl:1.0b:8192mv:1.5sl:1.3b:1024mv:1.5sl:1.3b:81920.00.20.40.60.81.01.2Latency (ms)0.930.630.610.590.580.600.590.60(b) Deletion LatencyDeep1B(96D)SIFT1M(128D)T2I-1B(200D)GIST1M(960D)105106107108109Throughput (vec/s)36.4K35.9K34.6K23.5K4.38M3.78M2.91M852.7KFaiss BaselineSIVF (Ours)Deep1B(96D)SIFT1M(128D)T2I-1B(200D)GIST1M(960D)101103105107Latency (ms)1.2K1.6K2.4K11.8K0.860.860.870.89Faiss BaselineSIVF (Ours)Deep1B(96D)SIFT1M(128D)T2I-1B(200D)GIST1M(960D)104105106Query Throughput (QPS)28.9K26.7K5.5K1.8K59.8K40.9K10.8K1.9KFaiss BaselineSIVF (Ours)5060708090105Vectors/s (log)Deep1B (96D)Baseline (GPU IVF)SIVF (Ours)405060708090105SIFT1M (128D)7580859095Recall@10 (%)104Vectors/s (log)T2I-1B (200D)30405060708090Recall@10 (%)104GIST1M (960D)Dongfang Zhao (dzhao@uw.edu)

Table 3: Breakdown of GPU time during streaming updates.

Operation Category

GPU IVF

SIVF (Ours)

Data Transfer (PCIe)
Memory Mgmt (malloc/free)
Compute (Active Kernels)
Other Overheads

53.2%
39.2%
3.2%
4.4%

< 1.0%
< 1.0%
95.0%
≈ 4.0%

reveals a severe resource mismatch: 53.2% of the runtime is con-
sumed by host-to-device data transfer (cudaMemcpyAsync) via the
PCIe bus, and an additional 39.2% is spent on dynamic memory
management overheads (cudaMalloc or cudaFree). Consequently,
the actual GPU compute units (SMs) remain idle for over 96% of the
update cycle, with only 3.2% of time utilized for kernel execution.
In contrast, SIVF’s GPU-resident architecture eliminates these PCIe
roundtrips and OS-level allocations. As a result, the execution pro-
file is transformed: 95.0% of the time is dedicated to active kernel
execution, confirming that SIVF successfully shifts the workload
from being I/O-bound to compute-bound.

Further profiling with Nsight Compute confirms that SIVF satu-
rates on-device resources. During the ingestion phase on SIFT1M,
the quantization kernels achieve a Streaming Multiprocessor (SM)
utilization of 49.0%, indicating a healthy compute-bound workload.
Simultaneously, the slab selection kernels exhibit an effective mem-
ory bandwidth of 150.3 GB/s. This demonstrates that despite the
irregular memory access patterns inherent to linked-slab traversals,
SIVF’s warp-aligned design (𝐶 = 32) maintains sufficient coalescing
to utilize a significant fraction of the device’s memory bandwidth,
a property unattainable by pointer-based CPU data structures.

4.5.2 Memory Efficiency and Scalability. A common concern with
dynamic graph-based or list-based indices is the potential for mem-
ory bloating due to structural overhead, such as pointers and meta-
data, as well as fragmentation. To quantify the space complexity
of SIVF, we conducted a memory footprint analysis comparing the
allocated VRAM usage of SIVF against a theoretically compact ar-
ray baseline across varying dataset sizes ranging from 100K to 1M
vectors. Figure 11 illustrates the memory growth trends for both
SIFT1M and GIST1M. The results demonstrate that SIVF exhibits
deterministic linear scalability with negligible structural overhead.
For SIFT1M (𝑑 = 128), the overhead stabilizes at 0.77%, while for
the high-dimensional GIST1M (𝑑 = 960), it is merely 0.10%. This
efficiency stems from our coarse-grained slab design, where the
metadata cost (128-byte header) is amortized over 32 vectors.

We verified the efficacy of our memory reclamation strategy. In
a stress test (not shown in the figure) involving the deletion of 50%
of the dataset followed by immediate re-insertion, SIVF maintained
a constant memory footprint without triggering OS-level dealloca-
tion. The deletion operation completed in sub-millisecond time per
batch (e.g., 4.04 ms for 100K GIST vectors), confirming that memory
slots are logically reclaimed via bitmap toggling and immediately
available for reuse. This zero-cost reclamation ensures that SIVF
can sustain long-running streaming workloads without suffering
from memory leaks or fragmentation-induced bloat.

Figure 10: End-to-End Streaming Performance.

Table 1: Tail latency of deletion operations over 1,000 stream-
ing steps (Batch Size 𝐵 = 1, 000).

Dataset Dim Avg (ms) P99 (ms) Max (ms)
SIFT1M 128
GIST1M 960

0.58
0.53

0.08
0.08

0.10
0.10

Table 2: Search latency stability under mixed workload.

Dataset

Dim Avg (ms)

P99 (ms)

SIFT1M 128
GIST1M 960

0.25
0.69

0.41
0.78

shown in Table 1, the results confirm two critical characteristics.
First, the latency scales linearly: reducing the batch size by 10×
(compared to the standard batching in Fig. 7) reduces the average la-
tency proportionally (from ≈ 0.89 ms to ≈ 0.08 ms), confirming the
O(1) nature of our bitmap operations. Second, the performance is
exceptionally stable: the 99th percentile (P99) latency is nearly iden-
tical to the average (0.10 ms vs 0.08 ms) for both SIFT1M (128D) and
GIST1M (960D). This demonstrate that SIVF’s lock-free retry mech-
anism introduces negligible jitter even under continuous churn,
and its performance remains strictly dimension-agnostic.

4.4.3 Mixed operations. We evaluated search stability by inter-
leaving query batches within the sliding window loop (Insert →
Search → Delete). The results confirm that SIVF maintains sub-
millisecond retrieval latency even under continuous mutation. On
SIFT1M, the 99th percentile (P99) search latency was 0.41 ms (Avg:
0.25 ms). Notably, on the high-dimensional GIST1M, the system
exhibited negligible jitter with a P99 of 0.78 ms (Avg: 0.69 ms).
This stability verifies that our slab-based memory management pre-
vents the fragmentation-induced performance degradation typical
of dynamic GPU indices.

4.5 Hardware Utilization
4.5.1 Computation. To understand the micro-architectural drivers
of the observed performance divergence, we profiled the GPU exe-
cution pipeline during the streaming update phase using NVIDIA
Nsight Systems and Nsight Compute. Table 3 presents the break-
down of the total execution time. The baseline implementation

0123456789Sliding Window Step100101102103Latency per Step (ms) [Log Scale]~163x Faster(a) SIFT1M (128D)Faiss Baseline (Roundtrip)SIVF (Native In-Place)0123456789Sliding Window Step100101102103Latency per Step (ms) [Log Scale]~262x Faster(b) GIST1M (960D)Faiss Baseline (Roundtrip)SIVF (Native In-Place)SIVF: GPU-Resident IVF Index for Streaming Vector Analytics

Figure 11: Memory Efficiency and Scalability.

Table 4: Add throughput (K vec/s) and delete latency (ms).

Figure 12: Distributed performance on the 12-GPU cluster
(DINO10B dataset).

Method

SIFT1M

Add

Delete

T2I-1B

GIST1M

Add

Delete

Add

Delete

Faiss Flat [7]
nuVS CAGRA [39]
HNSW [35]
NSG [9]
LSH [5]
SIVF (this work)

9,308
305
25.1
3.7
823
2,229

833
3,030
39,835
266,224
13.7
0.95

5,957
259
25.8
3.2
461
5,183

1,163
3,773
39,141
314,315
16.4
1.52

1,907
97.1
0.6
0.7
38.4
452

1,040
10,215
334,113
278,101
8.5
1.31

4.6 Mainstream Indexes for Streaming Vectors
To position SIVF within the broader indexing landscape, we bench-
marked it against five representative non-IVF architectures: GPU
CAGRA [39] (graphs), Faiss GPU Flat (brute-force baseline, i.e., no
index), HNSW [35] (dynamic graphs), (3) LSH [5] (legacy hash-
based approaches), and (4) NSG [9] (static graphs). Table 4 sum-
marizes ingestion throughput and deletion latency across three
datasets: SIFT1M, T2I-1B, and GIST1M.

Table 4 reports the results of vector ingestion and deletion in a
streaming context across three datasets. CPU-based graph indices
(HNSW, NSG) suffer catastrophic performance degradation on high-
dimensional data, dropping to merely 600 vec/s on GIST1M due to
cache thrashing. They lack native support for deletion, necessitat-
ing full index reconstruction that incurs prohibitive latencies (e.g.,
over 330 seconds for HNSW on GIST1M). While GPU Flat achieves
high ingestion throughput by bypassing indexing overhead, its
deletion latencies remain high (> 1s) due to 𝑂 (𝑁 ) data compaction
and CPU-GPU synchronization. Notably, the state-of-the-art GPU
graph index, CAGRA, exhibits severe limitations in streaming sce-
narios; enforcing true physical deletion to prevent memory leaks
necessitates reconstruction, causing latencies to spike to over 10
seconds. In contrast, SIVF emerges as the only architecture enabling
holistic stream processing: it sustains GPU-class ingestion rates
(e.g., 452K vec/s on GIST1M, 4.6× faster than CAGRA) while pro-
viding millisecond eviction with immediate slot reuse (via bitmap
toggling), and slab-level reclamation when a slab becomes empty.

4.7 Scalability on Multi-Node GPU Clusters
We evaluated the scalability performance of SIVF on the Chameleon
TACC site [24]. Each node is equipped with dual-socket Intel Xeon
E5 CPUs running at 2.00 GHz and 128 GB of RAM. The compute
power is provided by NVIDIA Tesla P100 GPUs. The experimen-
tal environment leverages a total of 12 GPUs distributed across 4

Figure 13: Scalability across a 4-node cluster of 12 GPUs.

physical nodes (4 GPUs each on c11-01 and c11-04, and 2 GPUs
each on c11-03 and c11-22).

We evaluate SIVF against the primary baseline (Faiss GPU IVF-
Flat) using the 1024-dimensional DINO10B dataset [1] on the 12-
GPU cluster. Figure 12(a) highlights SIVF’s efficiency in handling
data updates. For ingestion, SIVF achieves a 2.69× speedup over the
baseline (4.07M vectors/s vs. 1.51M vectors/s). The most significant
performance gap is observed in deletion operations. SIVF achieves
a 1150× speedup, processing over 108M deletions per second com-
pared to the baseline’s 94K. Figure 12(b) plots the Pareto frontier
of Recall@10 versus throughput. SIVF exhibits zero recall loss and
retains over 95% of the baseline’s throughput.

Figure 13 shows near-linear scalability for 128-dimensional vec-
tors. On 12 GPUs, ingestion peaks at 45.5 million vec/s, and search
reaches 30.1K vectors/s (95% efficiency relative to the single-GPU
baseline). Deletion exhibits super-linear scaling, achieving 103.2 mil-
lion vectors/s. This efficiency boost stems from the compute-bound
nature of the workload: expanding the cluster increases aggregate
GPU cache capacity and reduces per-device contention for bitmap
synchronization, thereby outperforming linear projections.

5 Conclusion
This work addresses the immutability issues in GPU-accelerated
Inverted File (IVF) indices caused by static memory layouts. We
present SIVF, a GPU-native index enabling high-velocity, in-place
updates via slab-based memory management. By leveraging a lock-
free update mechanism and optimized slab traversal, SIVF effec-
tively masks the synchronization overhead typical of dynamic in-
dexing, allowing the system to fully exploit hardware parallelism.
Evaluation on a 12-GPU cluster demonstrates that SIVF achieves
near perfect linear scalability, reaching 4.07M vectors/s for inges-
tion and 108.5M vectors/s for deletion. Furthermore, SIVF maintains
high-accuracy search performance at 159.3K queries/s while keep-
ing memory overhead negligible.

100K200K500K1MNumber of Vectors0 MB100 MB200 MB300 MB400 MB500 MBVRAM UsageStable 0.77% Overhead(a) SIFT1M Memory GrowthCompact BaselineSIVF (Ours)100K200K500K1MNumber of Vectors0 MB500 MB1.0 GB1.5 GB2.0 GB2.5 GB3.0 GB3.5 GBVRAM UsageStable 0.10% Overhead(b) GIST1M Memory GrowthCompact BaselineSIVF (Ours)IngestionDeletion104105106107108109Throughput (vectors/s)1.5M94K4.1M2.7x108.5M1149x(a) Update Performance (12-Card)BaselineSIVF (Ours)0.800.850.900.951.00Recall@10400006000080000100000120000140000160000Total vectors/sMaintainHigh SearchEfficiency(b) Search Performance (12-Card)BaselineSIVF (Ours)1234681012Total GPUs10203040M vectors/sIngestion1234681012Total GPUs51015202530K queries/sSearch1234681012Total GPUs20406080100M vectors/sDeletionSIVFIdealReferences
[1] Caron, M., Touvron, H., Misra, I., Jegou, H., Mairal, J., Bojanowski, P.,
and Joulin, A. Emerging properties in self-supervised vision transformers.
In 2021 IEEE/CVF International Conference on Computer Vision (ICCV) (2021),
pp. 9630–9640.

[2] Chatzakis, M., Papakonstantinou, Y., and Palpanas, T. Darth: Declarative
recall through early termination for approximate nearest neighbor search. Proc.
ACM Manag. Data 3, 4 (Sept. 2025).

[3] Chu, G., He, Y., Dong, L., Ding, Z., Chen, D., Bai, H., Wang, X., and Hu, C.
Efficient algorithm design of optimizing spmv on gpu. In Proceedings of the 32nd
International Symposium on High-Performance Parallel and Distributed Computing
(New York, NY, USA, 2023), HPDC ’23, Association for Computing Machinery,
p. 115–128.

[4] Chung, J. W., Lin, H., and Zhao, W. Locality-sensitive indexing for graph-based
approximate nearest neighbor search. In Proceedings of the 48th International
ACM SIGIR Conference on Research and Development in Information Retrieval
(New York, NY, USA, 2025), SIGIR ’25, Association for Computing Machinery,
p. 2418–2428.

[5] Datar, M., Immorlica, N., Indyk, P., and Mirrokni, V. S. Locality-sensitive
hashing scheme based on p-stable distributions. In Proceedings of the Twentieth
Annual Symposium on Computational Geometry (New York, NY, USA, 2004), SCG
’04, Association for Computing Machinery, p. 253–262.

[6] Deng, L., Chen, P., Zeng, X., Wang, T., Zhao, Y., and Zheng, K. Efficient
data-aware distance comparison operations for high-dimensional approximate
nearest neighbor search. Proc. VLDB Endow. 18, 3 (Nov. 2024), 812–821.

[7] Douze, M., Guzhva, A., Deng, C., Johnson, J., Szilvasy, G., Mazaré, P.-E.,

Lomeli, M., Hosseini, L., and Jégou, H. The faiss library.

[8] Engels, J., Landrum, B., Yu, S., Dhulipala, L., and Shun, J. Approximate nearest
neighbor search with window filters. In Forty-first International Conference on
Machine Learning (2024).

[9] Fu, C., Xiang, C., Wang, C., and Cai, D. Fast approximate nearest neighbor
search with the navigating spreading-out graph. Proc. VLDB Endow. 12, 5 (Jan.
2019), 461–474.

[10] Gao, J., Gou, Y., Xu, Y., Yang, Y., Long, C., and Wong, R. C.-W. Practical and
asymptotically optimal quantization of high-dimensional vectors in euclidean
space for approximate nearest neighbor search. Proc. ACM Manag. Data 3, 3
(June 2025).

[11] Gao, J., and Long, C. Rabitq: Quantizing high-dimensional vectors with a
theoretical error bound for approximate nearest neighbor search. Proc. ACM
Manag. Data 2, 3 (May 2024).

[12] Gong, Z., Zeng, Y., and Chen, L. Accelerating approximate nearest neighbor
search in hierarchical graphs: Efficient level navigation with shortcuts. Proc.
VLDB Endow. 18, 10 (June 2025), 3518–3530.

[13] Gou, Y., Gao, J., Xu, Y., and Long, C. Symphonyqg: Towards symphonious
integration of quantization and graph for approximate nearest neighbor search.
Proc. ACM Manag. Data 3, 1 (Feb. 2025).

[14] Hua, Z., Mo, Q., Yao, Z., Cui, L., Liu, X., Wang, G., Wei, Z., Liu, X., Tang, T., Liu,
S., and Qu, L. Dynamically detect and fix hardness for efficient approximate
nearest neighbor search. Proc. ACM Manag. Data 3, 6 (Dec. 2025).

[15] Hui, X., Xu, Y., Guo, Z., and Shen, X. Esg: Pipeline-conscious efficient scheduling
of dnn workflows on serverless platforms with shareable gpus. In Proceedings of
the 33rd International Symposium on High-Performance Parallel and Distributed
Computing (New York, NY, USA, 2024), HPDC ’24, Association for Computing
Machinery, p. 42–55.

[16] Hui, X., Xu, Y., and Shen, X. Fluidfaas: A dynamic pipelined solution for
serverless computing with strong isolation-based gpu sharing. In Proceedings of
the 34th International Symposium on High-Performance Parallel and Distributed
Computing (New York, NY, USA, 2025), HPDC ’25, Association for Computing
Machinery.

[18]

[17] Hwang, S., Lee, E., Oh, H., and Yi, Y. Fasop: Fast yet accurate automated search
for optimal parallelization of transformers on heterogeneous gpu clusters. In
Proceedings of the 33rd International Symposium on High-Performance Parallel
and Distributed Computing (New York, NY, USA, 2024), HPDC ’24, Association
for Computing Machinery, p. 253–266.
Indyk, P., and Xu, H. Worst-case performance of popular approximate nearest
neighbor search implementations: Guarantees and limitations. In Advances in
Neural Information Processing Systems 36: Annual Conference on Neural Informa-
tion Processing Systems 2023, NeurIPS 2023, New Orleans, LA, USA, December 10
- 16, 2023 (2023), A. Oh, T. Naumann, A. Globerson, K. Saenko, M. Hardt, and
S. Levine, Eds.
Jääsaari, E., Hyvönen, V., and Roos, T. Lorann: Low-rank matrix factorization
for approximate nearest neighbor search. In Advances in Neural Information
Processing Systems 38: Annual Conference on Neural Information Processing Sys-
tems 2024, NeurIPS 2024, Vancouver, BC, Canada, December 10 - 15, 2024 (2024),
A. Globersons, L. Mackey, D. Belgrave, A. Fan, U. Paquet, J. M. Tomczak, and
C. Zhang, Eds.
Jiang, M., Yang, Z., Zhang, F., Hou, G., Shi, J., Zhou, W., Li, F., and Wang, S.

[20]

[19]

Dongfang Zhao (dzhao@uw.edu)

[21]

[22]

[23]

Digra: A dynamic graph indexing for approximate nearest neighbor search with
range filter. Proc. ACM Manag. Data 3, 3 (June 2025).
Johnson, J., Douze, M., and Jégou, H. Billion-scale similarity search with gpus.
IEEE Transactions on Big Data 7, 3 (2021), 535–547.
Jung, S., Park, Y., Lee, H., Oh, Y. H., and Lee, J. W. Angular distance-guided
neighbor selection for graph-based approximate nearest neighbor search. In
Proceedings of the ACM on Web Conference 2025 (New York, NY, USA, 2025),
WWW ’25, Association for Computing Machinery, p. 4014–4023.
Jégou, H., Douze, M., and Schmid, C. Product quantization for nearest neighbor
search. IEEE Transactions on Pattern Analysis and Machine Intelligence 33, 1 (2011),
117–128.

[24] Keahey, K., Anderson, J., Zhen, Z., Riteau, P., Ruth, P., Stanzione, D., Cevik,
M., Colleran, J., Gunawi, H. S., Hammock, C., Mambretti, J., Barnes, A.,
Halbach, F., Rocha, A., and Stubbs, J. Lessons learned from the chameleon
testbed. In Proceedings of the 2020 USENIX Annual Technical Conference (USENIX
ATC ’20). USENIX Association, July 2020.

[25] Laut, S., Borrell, R., and Casas, M. Extending sparse patterns to improve
inverse preconditioning on gpu architectures. In Proceedings of the 33rd Inter-
national Symposium on High-Performance Parallel and Distributed Computing
(New York, NY, USA, 2024), HPDC ’24, Association for Computing Machinery,
p. 200–213.

[26] Leyba, K., Hofmeyr, S., Forrest, S., Cannon, J., and Moses, M. Simcov-gpu:
Accelerating an agent-based model for exascale.
In Proceedings of the 33rd
International Symposium on High-Performance Parallel and Distributed Computing
(New York, NY, USA, 2024), HPDC ’24, Association for Computing Machinery,
p. 322–333.

[27] Li, M., Yan, X., Lu, B., Zhang, Y., Cheng, J., and Ma, C. Attribute filtering in
approximate nearest neighbor search: An in-depth experimental study. Proc.
ACM Manag. Data 3, 6 (Dec. 2025).

[28] Li, X., Laguna, I., Fang, B., Swirydowicz, K., Li, A., and Gopalakrishnan,
G. Design and evaluation of gpu-fpx: A low-overhead tool for floating-point
In Proceedings of the 32nd International
exception detection in nvidia gpus.
Symposium on High-Performance Parallel and Distributed Computing (New York,
NY, USA, 2023), HPDC ’23, Association for Computing Machinery, p. 59–71.

[29] Li, Z., Ke, X., Zhu, Y., Yu, B., Zheng, B., and Gao, Y. Scalable graph indexing
using gpus for approximate nearest neighbor search. Proc. ACM Manag. Data 3,
6 (Dec. 2025).

[30] Li, Z., Ke, X., Zhu, Y., Yu, B., Zheng, B., and Gao, Y. Scalable graph indexing
using gpus for approximate nearest neighbor search. In Proceedings of the 2026
International Conference on Management of Data (SIGMOD) (2026).

[31] Liang, A., Zhang, P., Yao, B., Chen, Z., Song, Y., and Cheng, G. Unify: Unified
index for range filtered approximate nearest neighbors search. Proc. VLDB Endow.
18, 4 (Dec. 2024), 1118–1130.

[32] Liu, M., Zhong, S., Yang, Q., Han, Y., Liu, X., and Ma, Y. Webanns: Fast and
efficient approximate nearest neighbor search in web browsers. In Proceedings
of the 48th International ACM SIGIR Conference on Research and Development
in Information Retrieval (New York, NY, USA, 2025), SIGIR ’25, Association for
Computing Machinery, p. 2483–2492.

[33] Lu, D., Feng, S., Zhou, J., Solleza, F., Schwarzkopf, M., and Çetintemel, U.
Vectraflow: Integrating vectors into stream processing. In Proceedings of the 2025
Conference on Innovative Data Systems Research (CIDR) (Jan. 2025).

[34] Lu, K., Xiao, C., and Ishikawa, Y. Probabilistic routing for graph-based approx-
imate nearest neighbor search. In Forty-first International Conference on Machine
Learning (2024).

[35] Malkov, Y. A., and Yashunin, D. A. Efficient and robust approximate nearest
neighbor search using hierarchical navigable small world graphs. IEEE Trans.
Pattern Anal. Mach. Intell. 42, 4 (Apr. 2020), 824–836.

[36] Maurya, A., Rafiqe, M. M., Tonellot, T., AlSalem, H. J., Cappello, F., and
Nicolae, B. Gpu-enabled asynchronous multi-level checkpoint caching and
prefetching.
In Proceedings of the 32nd International Symposium on High-
Performance Parallel and Distributed Computing (New York, NY, USA, 2023),
HPDC ’23, Association for Computing Machinery, p. 73–85.

[37] Miao, D., Laguna, I., and Rubio-González, C. Floatguard: Efficient whole-
program detection of floating-point exceptions in amd gpus. In Proceedings of
the 34th International Symposium on High-Performance Parallel and Distributed
Computing (New York, NY, USA, 2025), HPDC ’25, Association for Computing
Machinery.

[38] Mohoney, J., Sarda, D., Tang, M., Chowdhury, S. R., Pacaci, A., Ilyas, I. F.,
Rekatsinas, T., and Venkataraman, S. Quake: adaptive indexing for vector
search. In Proceedings of the 19th USENIX Conference on Operating Systems Design
and Implementation (USA, 2025), OSDI ’25, USENIX Association.

[39] Ootomo, H., Naruse, A., Nolet, C., Wang, R., Feher, T., and Wang, Y. CAGRA:
Highly Parallel Graph Construction and Approximate Nearest Neighbor Search
for GPUs . In 2024 IEEE 40th International Conference on Data Engineering (ICDE)
(Los Alamitos, CA, USA, May 2024), IEEE Computer Society, pp. 4236–4247.

[40] Peng, Z., Qiao, M., Zhou, W., Li, F., and Deng, D. Dynamic range-filtering
approximate nearest neighbor search. Proc. VLDB Endow. 18, 10 (June 2025),
3256–3268.

SIVF: GPU-Resident IVF Index for Streaming Vector Analytics

[41] Peng, Z., Thomadakis, P., Pienaar, J., and Kestor, G. Liteform: Lightweight and
automatic format composition for sparse matrix-matrix multiplication on gpus.
In Proceedings of the 34th International Symposium on High-Performance Parallel
and Distributed Computing (New York, NY, USA, 2025), HPDC ’25, Association
for Computing Machinery.

[42] Qiu, R., and Tang, J. Efficient approximate nearest neighbor search via hemi-

sphere centroids graph. Proc. ACM Manag. Data 3, 6 (Dec. 2025).

[43] simhadri, H. V., Aumüller, M., Douze, M., Baranchuk, D., Ingber, A., Liberty,
E., Williams, G., Landrum, B., Manohar, M. D., Karjikar, M., Dhulipala, L.,
Chen, M., Chen, Y., Ma, R., Zhang, K., Cai, Y., Shi, J., Zheng, W., Chen, Y.,
Yin, J., and Huang, B. Results of the big ANN: NeurIPS’23 competition. In
The Thirty-ninth Annual Conference on Neural Information Processing Systems
Datasets and Benchmarks Track (2025).

[44] Sun, P., Simcha, D., Dopson, D., Guo, R., and Kumar, S. SOAR: improved index-
ing for approximate nearest neighbor search. In Advances in Neural Information
Processing Systems 36: Annual Conference on Neural Information Processing Sys-
tems 2023, NeurIPS 2023, New Orleans, LA, USA, December 10 - 16, 2023 (2023),
A. Oh, T. Naumann, A. Globerson, K. Saenko, M. Hardt, and S. Levine, Eds.
[45] Tran, A., Laguna, I., and Gopalakrishnan, G. Fpboxer: Efficient input-
generation for targeting floating-point exceptions in gpu programs.
In Pro-
ceedings of the 33rd International Symposium on High-Performance Parallel and
Distributed Computing (New York, NY, USA, 2024), HPDC ’24, Association for
Computing Machinery, p. 83–93.

[46] Voruganti, S., and Özsu, M. T. Mirage-anns: Mixed approach graph-based
indexing for approximate nearest neighbor search. Proc. ACM Manag. Data 3, 3
(June 2025).

[47] Wang, M., Lv, L., Xu, X., Wang, Y., Yue, Q., and Ni, J. An efficient and robust
framework for approximate nearest neighbor search with attribute constraint.
In Advances in Neural Information Processing Systems 36: Annual Conference on
Neural Information Processing Systems 2023, NeurIPS 2023, New Orleans, LA, USA,
December 10 - 16, 2023 (2023), A. Oh, T. Naumann, A. Globerson, K. Saenko,
M. Hardt, and S. Levine, Eds.

[48] Wang, Z., Zhang, J., and Hu, W. Wow: A window-to-window incremental index

for range-filtering approximate nearest neighbor search. Proc. ACM Manag. Data
3, 6 (Dec. 2025).

[49] Wei, J., Lee, X., Liao, Z., Palpanas, T., and Peng, B. Subspace collision: An
efficient and accurate framework for high-dimensional approximate nearest
neighbor search. Proc. ACM Manag. Data 3, 1 (Feb. 2025).

[50] Xu, Q., Zhang, F., Li, C., Cao, L., Chen, Z., Zhai, J., and Du, X. Harmony: A
scalable distributed vector database for high-throughput approximate nearest
neighbor search. Proc. ACM Manag. Data 3, 4 (Sept. 2025).

[51] Yandex, A. B., and Lempitsky, V. Efficient indexing of billion-scale datasets
of deep descriptors. In 2016 IEEE Conference on Computer Vision and Pattern
Recognition (CVPR) (2016), pp. 2055–2063.

[52] Yang, M., Cai, Y., and Zheng, W. CSPG: crossing sparse proximity graphs
for approximate nearest neighbor search. In Advances in Neural Information
Processing Systems 38: Annual Conference on Neural Information Processing Sys-
tems 2024, NeurIPS 2024, Vancouver, BC, Canada, December 10 - 15, 2024 (2024),
A. Globersons, L. Mackey, D. Belgrave, A. Fan, U. Paquet, J. M. Tomczak, and
C. Zhang, Eds.

[53] Zhang, B., Tian, J., Di, S., Yu, X., Feng, Y., Liang, X., Tao, D., and Cappello,
F. Fz-gpu: A fast and high-ratio lossy compressor for scientific computing
applications on gpus. In Proceedings of the 32nd International Symposium on
High-Performance Parallel and Distributed Computing (New York, NY, USA, 2023),
HPDC ’23, Association for Computing Machinery, p. 129–142.

[54] Zhang, F., Jiang, M., Hou, G., Shi, J., Fan, H., Zhou, W., Li, F., and Wang,
S. Efficient dynamic indexing for range filtered approximate nearest neighbor
search. Proc. ACM Manag. Data 3, 3 (June 2025).

[55] Zhang, Z., Liu, F., Huang, G., Liu, X., and Jin, X. Fast vector query processing
for large datasets beyond GPU memory with reordered pipelining. In 21st USENIX
Symposium on Networked Systems Design and Implementation (NSDI 24) (Santa
Clara, CA, Apr. 2024), USENIX Association, pp. 23–40.

[56] Zhong, X., Li, H., Jin, J., Yang, M., Chu, D., Wang, X., Shen, Z., Jia, W., Gu, G.,
Xie, Y., Lin, X., Shen, H. T., Song, J., and Cheng, P. Vsag: An optimized search
framework for graph-based approximate nearest neighbor search. Proc. VLDB
Endow. 18, 12 (Aug. 2025), 5017–5030.

