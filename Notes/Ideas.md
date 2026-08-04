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

> Build a batch-streaming, out-of-core GPU vector similarity join runtime for continuous semantic deduplication and corpus hygiene. Each micro-batch exposes a bounded future access graph; the runtime compiles that graph into cache, prefetch, GPU execution, and result-output decisions across SSD, DRAM, and HBM.

Static vector join is the per-batch execution primitive, not a separate project direction. Streaming vector search, fresh ANN indexes, and general stream processing are related work, not the main abstraction.

### 1. Workload: Continuous Semantic Dedup and Corpus Hygiene
Large AI/RAG systems continuously ingest documents, images, videos, code, chat memories, and chunks. Each new batch must be compared against a historical corpus and sometimes against itself to identify near-duplicates, redundant chunks, stale versions, or semantically equivalent records.

- `D`: historical corpus, usually much larger than RAM/HBM.
- `Q_t`: newly ingested embeddings in micro-batch `t`.
- Output: duplicate/match pairs `(q, d)`, duplicate groups, or top-k candidate edges.
- Time target: nearline batch completion, usually seconds to minutes rather than single-query milliseconds.
- Streaming property: adjacent batches are often correlated by source, tenant, topic, crawler shard, user/session, or ingestion pipeline, creating cross-batch locality.

Why this is a join: semantic dedup needs all matching pairs/groups above a threshold, not only one nearest neighbor per incoming vector. A single-query ANN API can find candidates, but it misses the chance to coordinate data movement for thousands or millions of vectors known together.

### 2. Access-Graph Compiler
After coarse partitioning and pruning, each batch becomes a bipartite access graph:

```text
G_t = (D_blocks, Q_t_blocks, E_t)
```

Each edge `(D_i, Q_j)` is a block-pair task. This graph is a bounded future access trace: the system can know which blocks will be reused, when they will be reused, what should be prefetched, and when cached data can be evicted.

Compiler responsibilities:

- partition `D` and each `Q_t` into coarse blocks;
- prune impossible or unlikely block pairs using centroid bounds and optional learned filters;
- order block-pair tasks to maximize reuse in DRAM and HBM;
- use Belady-style future-aware eviction for a fixed trace;
- extend scheduling across batches by preserving hot `D` blocks, recent `Q` blocks, and reusable per-partition index state.

Candidate scheduling baselines:

- row-major / block nested loop;
- random;
- DiskJoin/Gorder-style graph ordering;
- Reverse Cuthill-McKee over the bipartite block graph;
- oracle/Belady trace simulation.

### 3. Multi-Tier GPU Runtime
The runtime executes the compiled schedule over SSD, DRAM, and GPU HBM.

Core mechanisms:

- contiguous disk layout for coarse partitions;
- pinned host staging buffers and/or GPUDirect Storage path;
- DRAM victim cache for recently evicted partitions;
- HBM block cache with future-aware eviction;
- double buffering and multiple CUDA streams for load, compute, and output;
- asynchronous result sink with bounded buffers so output does not stall compute;
- instrumentation for SSD bandwidth, PCIe/H2D bandwidth, GPU utilization, cache hits, stalls, and result backpressure.

The central claim is that access-graph compilation changes end-to-end multi-tier execution. Layout, I/O paths, caches, and runtime mechanisms support that claim; they are not a venue-driven component checklist. A VRAM cache alone would not test the access-graph hypothesis.

### 4. Join-Aware GPU Execution
For each scheduled block pair `(D_i, Q_j)`, execute similarity join on GPU without materializing a dense `|D_i| x |Q_j|` distance matrix when possible.

Execution options:

- exact threshold join with tiled streaming distance computation and immediate select/compact;
- top-k join with on-the-fly selection, similar in spirit to flyKNNG;
- approximate join using a per-partition index on `D_i` such as IVF, CAGRA, or IVF-RaBitQ;
- SDDMM/gather-aware execution when candidate pairs are sparse;
- adaptive switch between dense tile scan and indexed candidate mode based on candidate density.

Open design tension: aggressive fine-grained pruning can create irregular candidate lists that are hard to feed into GEMM/Tensor Cores efficiently.

SimJoin-inspired reuse-aware indexed mode:

- compile a shallow proximity forest over each `Q_j` once; reuse the forest across all matched `D_i` partitions;
- for each resident `D_i`, search forest roots from the local graph entry point, then process ready children in GPU frontier batches;
- seed each child with compact `D_i`-local state, preferably the closest visited point/top-r seeds rather than the full parent window (soft work sharing);
- group siblings with overlapping frontiers into shared candidate slabs: dense microtiles/GEMM for high overlap, gather/SDDMM for low overlap;
- cut long forest edges, cap depth/window state, and fall back to the local entry point or dense scan for empty seeds, large windows, OOD queries, or high candidate density;
- keep this as the inner `(D_i, Q_j)` executor; the outer access-graph schedule still prioritizes SSD/DRAM/HBM movement.

### 5. Streaming State and Freshness
The streaming extension carries useful state across batches.

- Keep hot `D` partitions and their index metadata resident across batches when reuse is likely.
- Keep recent `Q` partitions for within-window dedup, e.g. `Q_t x Q_{t-w:t-1}`.
- Treat inserts/deletes to `D` as partition/index maintenance work, but do not make fresh ANN indexing the main contribution.
- Schedule with freshness deadlines and output backpressure in mind.

The main novelty is not only that new data arrives. It is that every micro-batch provides enough known future to compile a join plan, while the batch sequence provides locality and drift that a static join cannot use.


## Minor Ideas
*Minor ideas are supplementary concepts, features, writing points in the paper, or anything that is not directly related to one of the main ideas. This should be a list of any sizes that can be changed as the project evolves. Each idea should come with a detailed description.*

- **Learned pruning filters:** XJoin/Xling-style learned filters could complement centroid-distance pruning by predicting whether a query block is likely to have enough matches in a database block.
- **GPUDirect Storage:** BaM, CoPilotIO, and TERAIO show that GPU/SSD data paths can bypass or reduce CPU involvement. GDS is useful but should be an executor option, not the central novelty.
- **Partition size tuning:** Smaller partitions improve coarse pruning but increase scheduling overhead and may weaken second-level indexes. Larger partitions improve transfer granularity but reduce pruning and may exceed HBM. The right point is workload/hardware dependent.
- **Theoretical angle:** The block-pair schedule resembles a cache-aware traversal of a sparse bipartite graph. Possible foundations include Belady caching, reuse distance, Gorder, sparse tiling, and red-blue pebbling, but we should avoid overclaiming optimality.
- **Secondary use cases:** RAG memory maintenance, content moderation, nearline recommendation candidate refresh, embedding-model migration, retrieval regression testing, and cross-corpus entity resolution are good supporting examples, but continuous semantic dedup/corpus hygiene should remain the flagship.


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
