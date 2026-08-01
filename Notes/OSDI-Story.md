# OSDI Story for Out-of-Core GPU Vector Similarity Join

## One-Sentence Thesis

Vector similarity join should not be executed as millions or billions of independent ANN queries. Because the full join workload is known before execution, the system can compile the bipartite partition-pair graph into an out-of-core GPU execution plan that coordinates SSD, host memory, GPU memory, GPU kernels, and result materialization.

## What OSDI Precedents Teach Us

### Vector Systems Are OSDI Material When They Expose a Systems Mismatch

- **Quake (OSDI 2025)**: vector search enters OSDI by showing that dynamic/skewed workloads break static indexes, then solving it with adaptive partitioning, a cost model, recall estimation, and NUMA-aware execution.
- **PipeANN (OSDI 2025)**: the key story is not "faster DiskANN"; it is that best-first graph search is mismatched with SSD latency/parallelism, and relaxing the dependency order enables pipelined I/O.
- **FlowANN (OSDI 2026)**: turns graph search into a dependency-analysis problem. Step-level dependencies are too strict; node-level discovery/expansion windows enable CPU/GPU tiering and async transfer.
- **Helmsman (OSDI 2026)**: succeeds as an operational systems paper: production-scale vector workloads, cost pressure, all-flash storage, userspace I/O, learned pruning, and GPU build pipelines.

Lesson for us: do not sell "GPU vector join is faster." Sell "vector join exposes a new access-pattern contract that existing vector systems do not use."

### Multi-Tier GPU I/O Papers Need Layout + Scheduler + Runtime

- **CoPilotIO (OSDI 2026)**: limited GPU memory makes I/O part of the GPU compute stack. The paper identifies CPU-centric vs GPU-centric I/O tradeoffs and redesigns the CPU/GPU responsibility split.
- **Strata (OSDI 2026)**: hierarchical GPU/CPU/SSD caching becomes OSDI-worthy because the paper combines layout transformation, transfer mechanisms, and cache-aware scheduling.

Lesson for us: a VRAM cache alone is too small as a contribution. The story must combine partition layout, prefetch/eviction schedule, GPU work formation, and output/backpressure handling.

### DB Papers Work at OSDI When They Change the System Interface

- **Epic (OSDI 2024)**: predetermined transaction batches and known read/write sets remove version-search overhead. This is the closest analogy: known future information replaces dynamic runtime overhead.
- **Tigon (OSDI 2025)**: database structures are redesigned for CXL's coherence/bandwidth constraints.
- **Motor (OSDI 2024)**: MVCC version layout is redesigned because linked chains are bad over disaggregated memory.
- **Noria (OSDI 2018)**: relational queries become a dynamic, partially-stateful dataflow runtime.
- **QOOP (OSDI 2018)**: query planning becomes a cross-layer interface between planner, execution engine, and scheduler.
- **Akkio (OSDI 2018)**: locality is managed by promoting micro-shards to first-class migration units.
- **MapReduce (OSDI 2004)**: a data-processing idea becomes a systems paper by hiding partitioning, scheduling, communication, and failures behind a useful restricted abstraction.

Lesson for us: DB vocabulary is acceptable, but the paper should define a systems interface: "join graph as a future access trace" or "access graph compiler", not merely "a new join operator."

## Proposed OSDI Framing

### Problem

Large AI/data systems increasingly store TBs to PBs of embeddings on SSD-backed machines while using GPUs for compute. Many tasks are not single-query vector search:

- near-duplicate detection across new and historical corpora;
- offline retrieval evaluation and index refresh;
- content moderation or clustering pipelines comparing two large embedding sets;
- graph/KNN construction and cross-corpus matching;
- RAG corpus maintenance where batches of query/document embeddings are known together.

These tasks are vector similarity joins: given large sets `D` and `Q`, find all pairs under a threshold or top-k pairs. Both inputs can exceed host memory and GPU memory.

### Why Existing Systems Are Insufficient

- **Batch ANN systems** process queries independently, so they miss cross-query reuse of database partitions and cannot optimize a global access trace.
- **GPU ANN systems** assume the index or most active graph state is resident in GPU memory, or optimize one query stream over a single index.
- **DiskJoin** exploits the known join schedule, but stops at disk-to-DRAM scheduling and CPU execution.
- **Naive GPU block nested loop** keeps the compute primitive but loses the system: it reloads blocks, stalls on transfer, may materialize dense distance matrices, and does not coordinate result output.

### Key Observation

A vector join is not an online request stream. After coarse partitioning and pruning, it is a known bipartite graph:

`G = (D_blocks, Q_blocks, E)`

Each edge `(D_i, Q_j)` is a block-pair task. This graph is a complete future access trace modulo scheduling. That extra knowledge enables planning that is unavailable to ordinary ANN search:

- choose an edge order that maximizes block reuse in VRAM and host memory;
- precompute future reuse distances for eviction decisions;
- prefetch blocks before use and overlap I/O with GPU kernels;
- choose block granularity and per-partition index format using a cost model;
- form GPU work units that avoid dense distance materialization when pruning is sparse.

### System Thesis

Build a future-aware out-of-core GPU vector join runtime that compiles the pruned join graph into a multi-tier execution plan.

The plan jointly decides:

1. disk layout and partition granularity;
2. edge ordering over the bipartite join graph;
3. RAM and VRAM cache placement, prefetch, and eviction;
4. per-block-pair GPU execution mode, such as exact streaming threshold join or indexed approximate join;
5. result buffering and writeback so output does not stall compute.

## Main Contributions To Aim For

### 1. Characterization

Show that existing approaches fail for different reasons:

- DiskJoin-style CPU execution removes much disk waste but leaves GPU compute unused.
- Batch ANN repeatedly loads/probes the same partitions and cannot exploit join-wide reuse.
- Naive GPU block join has high GPU peak compute but poor end-to-end utilization due to SSD/PCIe stalls, VRAM reloads, dense distance buffers, and result backpressure.
- Existing GPU out-of-core I/O systems do not use operator-level future knowledge.

Useful measurements:

- GPU utilization over time;
- SSD bandwidth and read amplification;
- PCIe/H2D bandwidth;
- VRAM block reload count;
- time breakdown: load, H2D, kernel, selection, output;
- distance matrix memory footprint vs streaming/candidate execution;
- sensitivity to result selectivity.

### 2. Access-Graph Compiler

Convert coarse-pruned partition pairs into a schedule optimized for multi-tier memory.

Possible components:

- graph reordering objective based on block reuse distance;
- RCM/Gorder/degree-based baselines;
- Belady-optimal eviction for a fixed trace;
- trace simulator for RAM and VRAM;
- lower bounds based on compulsory block loads and limited-cache reuse;
- cost model that chooses partition count and block size under GPU memory, index size, transfer bandwidth, and expected result size.

The novelty should not be only "use RCM." The novelty is an interface: expose join semantics as a future access graph and compile it into cache/prefetch decisions.

### 3. Multi-Tier GPU Executor

Implement the schedule as a real runtime:

- contiguous disk layout for partitions;
- pinned host staging buffers and/or GDS path;
- RAM victim cache for recently evicted blocks;
- VRAM block cache with future-aware eviction;
- multiple CUDA streams for load/compute/output;
- asynchronous result sink with bounded buffers;
- instrumentation for stalls and bandwidth.

The executor should make the paper look like Strata/CoPilotIO: layout, I/O path, and scheduler are inseparable.

### 4. GPU Join Kernels

Avoid making the system depend on a dense `|D_i| x |Q_j|` distance matrix.

Options:

- exact threshold join with tiled streaming distance computation and immediate select/compact;
- top-k join with on-the-fly heap/selection similar in spirit to flyKNNG;
- approximate join using per-partition IVF/RaBitQ/CAGRA to produce candidate pairs;
- SDDMM/gather-aware execution for sparse candidate pairs;
- adaptive switch between dense tile scan and indexed candidate mode based on candidate density.

This piece matters because OSDI reviewers will ask whether the runtime still works at large block sizes and high dimensions.

### 5. Evaluation

Baselines:

- DiskJoin or faithful reimplementation/trace-level comparison;
- FAISS/cuVS batch ANN;
- DiskANN/PipeANN-style per-query search, if feasible;
- naive GPU block nested loop;
- scheduler variants: row-major, DiskJoin ordering, RCM/Gorder, random, oracle/Belady fixed-trace;
- executor variants: no RAM cache, no VRAM cache, no prefetch, no async output, no streaming kernel.

Metrics:

- end-to-end runtime and cost per billion pair candidates;
- recall/precision for approximate mode;
- GPU utilization and stall reasons;
- SSD bytes, read amplification, request size distribution;
- H2D transfer volume and bandwidth;
- block reload count in RAM and VRAM;
- output throughput/backpressure;
- sensitivity to VRAM size, RAM size, SSD bandwidth, dimension, threshold/selectivity, partition count, and skew.

## Suggested Introduction Arc

1. Vector systems increasingly live on SSD-backed GPU machines, but not all vector workloads are online independent ANN search.
2. Vector similarity join is a core batch primitive for deduplication, retrieval evaluation, corpus maintenance, and graph construction. It compares two large sets and exposes massive reuse.
3. Existing systems choose the wrong abstraction: ANN engines optimize one query at a time; DiskJoin optimizes disk-resident CPU joins; GPU kernels optimize a block after data has already arrived.
4. The missing systems opportunity is that vector join has a known future. After partitioning and pruning, the workload is a bipartite access graph.
5. We turn that graph into a cross-tier execution plan, coordinating SSD, host memory, GPU memory, GPU compute, and output.
6. This design removes redundant movement and keeps GPUs busy, making out-of-core GPU vector joins practical on a single node or small server.

## Positioning Sentence

Prior vector search systems optimize how to find neighbors for one query stream; our system optimizes how to execute a known many-to-many vector workload over a memory hierarchy.

## Intro Skeleton

### 1. Opening: Vector Workloads Are Now Systems Infrastructure

Large AI and data pipelines increasingly revolve around embeddings: search, recommendation, RAG, deduplication, moderation, corpus refresh, and model evaluation. Existing systems usually frame the problem as online ANN search: given one query vector, search a large index for nearest neighbors.

### 2. Turn: Many Important Workloads Are Joins, Not Online Search

Many offline and maintenance tasks are naturally many-to-many. Given two large embedding sets `D` and `Q`, the system must find all similar pairs or top-k pairs across the two sets. Examples include new-vs-historical corpus deduplication, retrieval quality evaluation, cross-modal matching, kNN graph construction, and RAG corpus maintenance. This is vector similarity join, not merely batch ANN.

### 3. Pain Point: Join Scale Forces GPUs Into Out-of-Core Execution

Both `D` and `Q` can be terabytes in size and may exceed host memory, let alone GPU HBM. GPUs provide abundant compute, but the data must continuously move through SSD, host DRAM, and GPU HBM. At this scale, the core bottleneck is not just distance computation; it is how to keep the GPU fed without repeatedly moving the same vector blocks.

### 4. Why Existing Systems Fall Short

Batch ANN systems treat each query independently and miss cross-query block reuse. GPU ANN systems assume the index or active graph state mostly resides in HBM, or optimize a single query stream over one index. DiskJoin exploits global join structure, but only for disk-to-DRAM scheduling and CPU execution. Naive GPU block nested loop uses the GPU but suffers from block reloads, PCIe/SSD stalls, dense distance matrix materialization, and result backpressure.

### 5. Key Insight: Vector Join Has a Known Future

Unlike online ANN search, vector join exposes most of its access structure before execution. After coarse partitioning and pruning, the workload becomes a bipartite graph:

```text
G = (D_blocks, Q_blocks, E)
```

Each edge `(D_i, Q_j)` is a block-pair task. This graph is effectively a future access trace. The system can know which blocks will be reused, when they will be reused, what should be prefetched, and when cached data can be evicted.

### 6. Challenge: Known Future Does Not Automatically Yield a Fast System

The difficulty is multi-tier coordination. A good edge order for SSD may not be good for host DRAM, GPU HBM, kernel execution, and result output at the same time. Large partitions improve transfer granularity but may not fit in HBM; small partitions reduce memory pressure but increase I/O and launch overhead. Sparse candidate pairs make dense distance matrices wasteful, while high selectivity can make result output the bottleneck.

### 7. System: Future-Aware Out-of-Core GPU Vector Join

We design GPU-AVSJ / VecJoin, a future-aware out-of-core GPU vector join runtime. It compiles the pruned join graph into a multi-tier execution plan that jointly decides partition layout, block-pair ordering, RAM/VRAM caching, prefetch/eviction, GPU execution mode, and result buffering.

### 8. Contributions

1. **Characterization**: We show how batch ANN, DiskJoin-style CPU join, and naive GPU join bottleneck differently on out-of-core vector joins.
2. **Access-Graph Compiler**: We turn the bipartite vector join graph into a cache-aware execution schedule that exploits known-future access to reduce RAM and VRAM reloads.
3. **Multi-Tier GPU Runtime**: We implement a coordinated executor across SSD, DRAM, HBM, CUDA streams, and result sinks to hide I/O stalls and sustain GPU utilization.
4. **Join-Aware GPU Execution**: We design streaming threshold/top-k or indexed candidate execution that avoids materializing full distance matrices.
5. **Evaluation**: We evaluate against DiskJoin, batch ANN, and naive GPU baselines, reporting end-to-end runtime, read amplification, block reloads, GPU utilization, and stall breakdowns.

### 9. Results Placeholder

```text
On X real-world embedding datasets and Y synthetic workloads,
VecJoin improves end-to-end runtime by A-Bx over DiskJoin-style CPU execution,
C-Dx over batch ANN baselines, and reduces SSD read amplification by E% while
keeping GPU utilization above F%.
```

### One-Paragraph Version

Prior systems optimize vector search as independent queries. We show that vector similarity join exposes a stronger systems contract: the future access graph is known. By compiling this graph into a multi-tier GPU execution plan, we turn out-of-core vector join from an I/O-stalled GPU workload into a schedulable systems problem.

## Risk Checklist

- If the implementation is only a GPU distance kernel plus block loop, it is a SIGMOD/ICDE systems paper at best, not OSDI.
- If GDS is unavailable, the paper can still work, but the executor must clearly support high-throughput pinned-memory staging and show where GDS would or would not help.
- If result selectivity is high, output can dominate. The paper must define threshold/top-k workloads carefully and treat result materialization as a first-class pipeline stage.
- If approximate mode is weak, start with exact threshold/top-k plus scheduling and show an extensible index interface; do not make unproven ANN quality claims the central contribution.
- If scheduler optimality is hard, provide lower bounds and a trace simulator rather than overclaiming optimality.
