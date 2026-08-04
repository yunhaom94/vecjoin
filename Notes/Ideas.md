# Ideas
This document contains the ideas and notes for the project.

## Project Name
GPU-AVSJ

## Piloting Idea
*Piloting idea is a single short paragraph that describes the initial idea for the project, could be big could also be small. This should not be changed.*

Using GPUs to do approximate vector similarity join for large, high-dimensional datasets. A main focus should be the use of DMA to reduce the overhead of data transfer between disk and VRAM.


## Main Ideas
*Main ideas are the core concepts and features of the project. This should be a short list between 3-5 ideas that can be changed as the project evolves. **Important:** this section should evolve over time, and the ideas should be refined and updated as the project progresses, and finally becomes a detailed design document for the project.*

Single main line:

> Build an out-of-core GPU vector similarity join runtime with exact and approximate modes for billion-scale `D`-`Q` datasets. After coarse pruning exposes the fully known set of surviving bipartite block-pair tasks, compile it into cache, prefetch, GPU execution, and result-output decisions across SSD, DRAM, and HBM.

Vector similarity join, not independent ANN queries, is the main abstraction. The system co-designs coarse partitioning, pruning, and scheduling with fine per-partition GPU search.

### 1. Static Workload and Two-Level Design
Given a database set `D` and a query set `Q` of high-dimensional vectors:

- exact mode outputs all pairs `(d, q)` below epsilon or exact per-query top-k;
- approximate mode outputs recall-measured threshold pairs or approximate per-query top-k; match/duplicate groups are derived from emitted pairs;
- initial scale target: billions of approximately 1,000-dimensional FP32 vectors, about 4 KB per vector and 4 TB per billion vectors;
- coarse level: independently cluster `D` and `Q`, then prune partition pairs with centroid-distance bounds before vector-block I/O;
- fine level: use a per-`D_i` GPU index such as IVF/IVF-PQ, CAGRA, or IVF-RaBitQ to prune individual comparisons inside each surviving block pair.

Why this is a join: the complete query set exposes reuse across many vectors and permits global data-movement scheduling. Independent ANN queries discard that opportunity.

### 2. Access-Graph Compiler
Offline graph construction:

- sample `D` and `Q` independently; cluster and assign vectors to their nearest centroid on CPU;
- materialize each coarse partition contiguously on SSD;
- tune `D`-block and `Q`-block sizes independently;
- for metric threshold joins, safely prune `(D_i, Q_j)` when `dist(c_i, c_j) - r_i - r_j > epsilon`, using partition centroids `c` and radii `r`;
- for top-k, compare the same lower bound with the current kth-distance upper bound; treat learned filters as approximate unless they provide a safe bound.

The surviving work becomes a bipartite access graph:

```text
G = (D_blocks, Q_blocks, E)
```

Each edge `(D_i, Q_j)` is a block-pair task. The compiler linearizes the fully known graph into a finite access trace; that ordered trace exposes next use and reuse distance for prefetch and eviction.

Compiler settings and responsibilities:

- build/prune the graph and compile the schedule on CPU; keep pruning and scheduling implementations pluggable;
- minimize weighted transfer cost across SSD-to-DRAM and DRAM-to-HBM under configured cache budgets; report block reload count as a simpler proxy;
- order block-pair tasks to maximize reuse in DRAM and HBM;
- derive prefetch decisions and use Belady-style future-aware eviction for a fixed trace.

Candidate scheduling baselines:

- row-major / block nested loop, pinning `D` blocks while sweeping `Q` blocks;
- random;
- DiskJoin/Gorder-style graph ordering;
- Reverse Cuthill-McKee node ordering with a deterministic incident-edge/task traversal;
- oracle/Belady trace simulation.

### 3. Multi-Tier GPU Runtime
The runtime executes the compiled schedule over SSD, DRAM, and GPU HBM.

Initial object placement:

- SSD: contiguous vector partitions and durable per-`D_i` index artifacts, fetched on demand;
- DRAM: coarse centroids, access-graph/schedule metadata, victim blocks, and cached index artifacts when budget permits;
- HBM: resident `D_i`/`Q_j` blocks, loaded index state, block cache, staging buffers, and result buffers.

Core mechanisms:

- contiguous disk layout for coarse partitions;
- pinned host staging buffers and/or GPUDirect Storage path;
- DRAM victim cache for recently evicted partitions;
- HBM block cache with future-aware eviction;
- double buffering and multiple CUDA streams for load, compute, and output;
- asynchronous result sink with bounded buffers so output does not stall compute;
- per-pair GPU filter/select/compact, followed by host/sink merge, grouping, or ordering only when required; compare GPU finalization when output semantics justify it;
- instrumentation for SSD bandwidth, PCIe/H2D bandwidth, GPU utilization, cache hits, stalls, and result backpressure.

Primary tunables: `D`/`Q` block sizes, DRAM victim-cache budget, HBM cache budget and allocation across blocks/indexes/staging/results, transfer path, and result-buffer capacity.

The central claim is that access-graph compilation changes end-to-end multi-tier execution. Layout, I/O paths, caches, and runtime mechanisms support that claim; they are not a venue-driven component checklist. A VRAM cache alone would not test the access-graph hypothesis.

### 4. Join-Aware GPU Execution
For each scheduled block pair `(D_i, Q_j)`, execute similarity join on GPU without materializing a dense `|D_i| x |Q_j|` distance matrix when possible.

Indexed path: search `Q_j` against `D_i`'s fine index, generate candidate pairs, compute candidate distances, then filter/select/compact results.

Execution options:

- exact threshold join with tiled distance computation and immediate select/compact;
- top-k join with on-the-fly selection, similar in spirit to flyKNNG;
- approximate join using a pluggable per-partition index on `D_i` such as IVF/IVF-PQ, CAGRA, or IVF-RaBitQ;
- SDDMM/gather-aware execution when candidate pairs are sparse;
- adaptive switch between dense tile scan and indexed candidate mode based on candidate density.

Fine-index settings:

- co-tune index parameters and `D_i` size; small partitions may make the second index redundant;
- compare recall, build time, HBM footprint, and candidate density across index families;
- prebuild expensive graph indexes, cache/load them with `D_i`, and verify whether IVF/IVF-PQ adds enough pruning to justify a second clustering hierarchy.

Open design tension: aggressive fine-grained pruning can create irregular candidate lists that are hard to feed into GEMM/Tensor Cores efficiently.

SimJoin-inspired reuse-aware indexed mode:

- compile a shallow proximity forest over each `Q_j` once; reuse the forest across all matched `D_i` partitions;
- for each resident `D_i`, search forest roots from the local graph entry point, then process ready children in GPU frontier batches;
- seed each child with compact `D_i`-local state, preferably the closest visited point/top-r seeds rather than the full parent window (soft work sharing);
- group siblings with overlapping frontiers into shared candidate slabs: dense microtiles/GEMM for high overlap, gather/SDDMM for low overlap;
- cut long forest edges, cap depth/window state, and fall back to the local entry point or dense scan for empty seeds, large windows, OOD queries, or high candidate density;
- keep this as the inner `(D_i, Q_j)` executor; the outer access-graph schedule still prioritizes SSD/DRAM/HBM movement.


## Minor Ideas
*Minor ideas are supplementary concepts, features, writing points in the paper, or anything that is not directly related to one of the main ideas. This should be a list of any sizes that can be changed as the project evolves. Each idea should come with a detailed description.*

- **Streaming extension (side note):** Apply the static compiler to rolling `Q_t` micro-batches, each exposing a known graph for `Q_t x D`, optional `Q_t x Q_t`, and `Q_t x Q_{t-w:t-1}` joins. Target nearline completion in seconds to minutes; retain hot `D` partitions/index state and recent `Q` blocks; exploit source/tenant/topic/shard/session locality while handling drift; treat `D` inserts/deletes as maintenance; add freshness and output-backpressure constraints. This is an extension, not the main abstraction or contribution.
- **Learned pruning filters:** XJoin/Xling-style learned filters could complement centroid-distance pruning by predicting whether a query block is likely to have enough matches in a database block.
- **GPUDirect Storage:** BaM, CoPilotIO, and TERAIO show that GPU/SSD data paths can bypass or reduce CPU involvement. GDS is useful but should be an executor option, not the central novelty.
- **Partition size tuning:** Smaller partitions improve coarse pruning but increase scheduling overhead and may weaken second-level indexes. Larger partitions improve transfer granularity but reduce pruning and may exceed HBM. The right point is workload/hardware dependent.
- **Theoretical angle:** The block-pair schedule resembles a cache-aware traversal of a sparse bipartite graph. Possible foundations include Belady caching, reuse distance, Gorder, sparse tiling, and red-blue pebbling, but we should avoid overclaiming optimality.
- **Secondary use cases:** RAG memory maintenance, content moderation, nearline recommendation candidate refresh, embedding-model migration, retrieval regression testing, and cross-corpus entity resolution are good supporting examples, but semantic dedup/corpus hygiene should remain the flagship.


## Notes
*Notes are any other thoughts, observations, or additional information that is relevant to the project but does not constitute as an "idea" which requires action. This can include things like background, potential challenges, or any other information that is useful for the project. This should be a list of any sizes that can be changed as the project evolves.*

### Paper Positioning

One-sentence thesis:

> Vector similarity join should not be executed as millions or billions of independent ANN queries. Because each micro-batch exposes a bounded future access graph, the system can compile the join into a multi-tier GPU execution plan.

Positioning sentence:

> Prior vector search systems optimize how to find neighbors for one query stream; our system optimizes how to execute a known many-to-many vector workload over a memory hierarchy.

Venue positioning (corrected):

- **Correction:** The earlier judgment that GPU-AVSJ is not suitable for OSDI, and the associated fixed systems-component checklist, were wrong. The work is plausible for both OSDI and database venues.
- **No algorithm/system boundary:** Quake and PipeANN are OSDI papers with algorithmic cores; DiskJoin, VStream, GustANN, and Tagore show that database venues also accept storage, runtime, GPU, and cross-layer system contributions.
- **Same technical core, different emphasis:** A DB framing presents access-graph compilation as a vector-join physical algorithm/operator and leads with semantics, recall, runtime, I/O, and memory. An OSDI framing presents it as a bounded-future-trace execution mechanism and leads with data movement, stalls, utilization, and end-to-end execution.
- **Main venue difference is writing/community fit:** first-page problem, vocabulary, related work and baselines, causal chain, and which evidence is foregrounded. Research object, claim boundary, and evaluation closure are largely choices made in writing, not immutable properties of the artifact.
- **Writing still needs evidence:** framing cannot support claims absent from the results, but most core evidence is shared. Do not add streaming, SLOs, failure recovery, production deployment, or a fixed set of layout/I/O/cache/runtime components solely to look like OSDI.
- **Actual gate for either venue:** show that independent ANN execution creates a consequential bottleneck and that access-graph compilation causally improves end-to-end execution across strong baselines, datasets, memory budgets, and hardware conditions.

### Evaluation Plan

Primary workload: continuous semantic dedup / corpus hygiene.

- Historical corpus `D`: web/text/RAG chunks or public embedding datasets.
- Stream `Q_1...Q_T`: ingestion batches sampled by source/topic/time to preserve locality.
- Queries: `Q_t` vs `D`, `Q_t` vs `Q_t`, and optionally `Q_t` vs recent window `Q_{t-w:t-1}`.

Baselines:

- DiskJoin or faithful static/trace-level implementation;
- FAISS/cuVS batch ANN;
- DiskANN/PipeANN-style per-query search where feasible;
- naive GPU block nested loop;
- VStream-style independent streaming vector search if implementable;
- scheduler variants: row-major, random, DiskJoin/Gorder-style, RCM, Belady fixed trace, no cross-batch cache.

Metrics:

- end-to-end batch latency and sustained ingest throughput;
- duplicate-pair recall/precision or top-k recall;
- GPU utilization and stall breakdown;
- SSD bytes, DRAM/HBM bytes, read amplification, and block reload count;
- cross-batch cache hit rate;
- output volume, result sink throughput, and backpressure sensitivity;
- freshness lag under bursts.

### Risks

- If the system is only a GPU distance kernel plus block loop, the novelty is weak for either venue. The paper needs a new access-graph/join-aware insight with causal end-to-end evidence; additional components are supporting mechanisms, not a venue checklist.
- If the streaming story is only "new queries arrive," reviewers may reduce it to batch ANN. The use case must require join output: duplicate pairs, match groups, candidate edges, or relationship deltas.
- If GDS is unavailable, the paper can still work with pinned-memory staging, but the executor must clearly show where the bottleneck is and what the schedule controls.
- If result selectivity is high, output can dominate. Result buffering/backpressure must be part of the system, not an afterthought.
- If scheduler optimality is hard, provide lower bounds and trace simulation rather than overclaiming.
- Literal SimJoin is a poor GPU mapping: deep MST dependencies, priority queues, and ragged windows reduce occupancy. The contribution must be GPU-aware bounded-depth work sharing plus adaptive dense/sparse execution, not merely "SimJoin on GPU."
- SimJoin-style graph traversal is approximate and may miss disconnected in-range components. Preserve exact dense execution when exactness is required; retain local-entry/hybrid fallbacks and report recall for indexed mode.


## Foundations
*Any background of this project, including related work, previous research, or any other information that is relevant to the project. It should not be a list of literatures, but a summary of key concepts, background, SOTA solution patterns and remaining gaps in the literature that are relevant to the project.*

### 1. Problem Definition: Vector Similarity Join

Vector similarity join takes two sets of high-dimensional vectors, `D` and `Q`, and finds all pairs `(d, q)` whose distance is below a threshold epsilon, or returns the top-k closest pairs for each query vector. This differs from single-query ANN search because the system processes many query vectors together and can exploit cross-query reuse of database partitions.

In the batch-streaming version, the input is a sequence of query/update batches `Q_1, Q_2, ...` against a large historical corpus `D` and possibly a recent window of prior batches. The system should produce per-batch join results while maintaining enough state to exploit cross-batch locality and respect freshness constraints.

### 2. Relevant Prior Work

**GPU ANN systems** such as FAISS, CAGRA, IVF-RaBitQ, GustANN, FusionANNS, and FlowANN accelerate search over a single index. They are useful for per-partition execution and GPU/runtime design, but they do not optimize many-to-many join-wide data movement.

**Out-of-core vector search systems** such as DiskANN, SPANN, PipeANN, FlashANNS, and Helmsman optimize SSD-resident ANN search. They provide storage-layout and I/O-overlap techniques, but their abstraction is query-stream search, not join-graph execution.

**Vector similarity join systems** such as DiskJoin, SimJoin, and XJoin/Xling are closest algorithmically. DiskJoin is the direct static system predecessor because it exposes a bucket graph and uses graph ordering plus Belady caching, but it is CPU-only and does not handle rolling batches, HBM scheduling, or GPU result pipelines.

**SimJoin-style work sharing** orders queries with a proximity-graph MST and seeds a child search from its parent's result window. For GPU execution, use a bounded-depth forest and batch ready siblings/frontiers rather than a serial tree walk. Prefer compact soft seeds as in *Fast Approximate Vector Joins via Offline-Online Co-Design* (2026), which avoids empty-window and large-window pathologies. These methods optimize in-memory fine search, not out-of-core block scheduling.

**Streaming and fresh vector systems** such as VStream, FreshDiskANN, SPFresh, IP-DiskANN, OdinANN, SIVF, SVFusion, RTAMS-GANNS, and Slipstream address dynamic ingestion, index updates, or vector search inside stream processing. They motivate freshness and temporal locality, but they maintain search indexes rather than compile micro-batch join graphs.

**Stream/dataflow systems** such as D-Streams/Spark Streaming, Structured Streaming, MillWheel, Dataflow, Naiad, Differential Dataflow, Noria, and DBToaster provide micro-batch, event-time, state, and incremental-computation semantics. They do not understand vector-similarity access graphs or GPU/SSD/HBM scheduling.

### 3. Literature Gap

The gap is one sentence:

> Stream processors understand time and state, dynamic ANN systems understand index freshness, and static vector-join systems understand all-pairs similarity structure; none compile rolling vector-join micro-batches into a multi-tier GPU execution plan that exploits bounded future access within each batch and temporal locality across batches.

Concrete gaps:

- **No GPU-accelerated billion-scale vector similarity join:** DiskJoin is the closest direct predecessor but is CPU-only.
- **No three-tier join scheduler:** existing vector search systems do not manage `D` blocks, `Q` blocks, per-partition indexes, and result buffers together across SSD, DRAM, and HBM.
- **No batch-streaming vector join abstraction:** existing streaming vector systems optimize search or index freshness, not join output over a known micro-batch graph.
- **No join-aware GPU execution plan:** existing GPU ANN systems build one global index or optimize independent query batches; they do not coordinate partition layout, prefetch, eviction, and GPU kernels around a join graph.
