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

Formal join semantics, for distance function `delta`:

$$
J_\epsilon(D,Q)=\{(d,q)\in D\times Q:\delta(d,q)\leq\epsilon\}.
$$

$$
N_k(q)=\operatorname*{arg\,min}_{S\subseteq D,\ |S|=k}
\sum_{d\in S}\delta(d,q),
\qquad
J_k(D,Q)=\bigcup_{q\in Q}\{(d,q):d\in N_k(q)\}.
$$

- approximate threshold quality: $\operatorname{Recall}(\widehat J_\epsilon)=|\widehat J_\epsilon\cap J_\epsilon|/|J_\epsilon|$;
- approximate top-k quality: $\operatorname{Recall@}k=|Q|^{-1}\sum_{q\in Q}|\widehat N_k(q)\cap N_k(q)|/k$;
- exact modes require safe coarse pruning and exhaustive/guaranteed fine execution over every retained pair; approximate modes may additionally prune candidates and report recall.

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

Safe coarse-pruning formulation for metric `delta`:

$$
D=\biguplus_{i=1}^{n_D}D_i,
\qquad
Q=\biguplus_{j=1}^{n_Q}Q_j,
$$

$$
r_i^D=\max_{d\in D_i}\delta(d,c_i^D),
\qquad
r_j^Q=\max_{q\in Q_j}\delta(q,c_j^Q),
$$

$$
L_{ij}=\max\{0,\delta(c_i^D,c_j^Q)-r_i^D-r_j^Q\}
\leq \delta(d,q)
\quad \forall(d,q)\in D_i\times Q_j.
$$

- threshold graph: $E_\epsilon=\{(i,j):L_{ij}\leq\epsilon\}$; discard `(i,j)` when $L_{ij}>\epsilon$;
- top-k with current per-query upper bounds $U_q$: $L_{i,q}=\max\{0,\delta(c_i^D,q)-r_i^D\}$; retain `(i,j)` iff $\exists q\in Q_j:L_{i,q}\leq U_q$;
- coarser blockwise top-k test: discard `(i,j)` when $L_{ij}>\max_{q\in Q_j}U_q$;
- every retained edge is executed once; pruning changes `E`, while scheduling permutes `E`.

Joint scheduling, placement, and routing formulation:

- objects $\mathcal O=\{D_i,Q_j,I_i,\ldots\}$ have sizes $s_o$; task $e_t=(i,j)$ requires $\{D_i,Q_j\}\subseteq\mathcal A(e_t)$ in HBM, plus `I_i` for an indexed path;
- schedule $\pi=(e_1,\ldots,e_{|E|})\in\operatorname{Perm}(E)$;
- $x^H_{o,t},x^R_{o,t}\in\{0,1\}$ denote HBM/DRAM residency; $y^r_{o,t}\in\{0,1\}$ denotes a transfer on data route $r\in\mathcal R_d$;
- data routes $\mathcal R_d=\{S\!\to\!R,S\!\to\!H,R\!\to\!H,H\!\to\!R\}$ cover staged/direct reads, promotion, and demotion; result output uses $H\!\to\!S$;
- route cost $\phi_r(s)=\alpha_r s+\beta_r$ combines bandwidth/byte cost and per-request overhead.

$$
C^*=\min_{\pi\in\operatorname{Perm}(E)}
\min_{x,y\ \mathrm{feasible\ for}\ \pi}
\left[
\sum_{t=1}^{|E|}\sum_{o\in\mathcal O}\sum_{r\in\mathcal R_d}
\phi_r(s_o)y^r_{o,t}
+\sum_{t=1}^{|E|}\phi_{H\to S}(z_{e_t})
\right],
$$

subject to

$$
\sum_o s_o x^H_{o,t}+B_t^{\mathrm{stage}}+B_t^{\mathrm{out}}\leq C_H,
\qquad
\sum_o s_o x^R_{o,t}\leq C_R,
$$

$$
x^H_{o,t}=1\quad\forall o\in\mathcal A(e_t),
$$

plus legal transfer/residency transitions and dependency-safe prefetch deadlines. Here `S`, `R`, and `H` denote SSD, DRAM, and HBM; $z_e$ is task output size. The fixed-trace placement problem is the inner minimization; joint access-graph compilation also chooses `pi`.

Current trace-simulator specialization:

$$
C_{\mathrm{ops}}(\pi)=N_{S\to H}+N_{R\to H}+N_{H\to R},
$$

$$
C_{\mathrm{bytes}}(\pi)=
\sum_{r\in\{S\to H,R\to H,H\to R\}}\ \sum_{\text{transfers on }r}s_o.
$$

- equal 64 MiB blocks make $C_{\mathrm{bytes}}=64\ \mathrm{MiB}\cdot C_{\mathrm{ops}}$; the controlled sweep therefore compares ordering rather than object-size weighting;
- ultimate runtime objective: minimize dependency-constrained makespan with SSD, interconnect, GPU, and output overlap; byte/operation cost is the current scheduling surrogate.

Compiler settings and responsibilities:

- build/prune the graph and compile the schedule on CPU; keep pruning and scheduling implementations pluggable;
- minimize weighted transfer cost across SSD-to-DRAM and DRAM-to-HBM under configured cache budgets; report block reload count as a simpler proxy;
- order block-pair tasks to maximize reuse in DRAM and HBM;
- derive prefetch decisions and use Belady-style future-aware eviction for a fixed trace.

Candidate scheduling baselines:

- row-major / block nested loop, pinning `D` blocks while sweeping `Q` blocks;
- random;
- DiskJoin/Gorder-style graph ordering;
- Reverse Cuthill-McKee block ordering with the same D-grouped edge-emission policy as other grouped baselines;
- oracle/Belady trace simulation.

Grouped-baseline formulations, with $N(i)=\{j:(i,j)\in E\}$:

- any D-group order $\rho$ induces $\pi_\rho=\bigoplus_{i\in\rho}[(i,j):j\in N(i)]$; only group and within-group order vary in the controlled sweep;
- MECC/Gorder overlap score at step `t`: $g_t(i)=\sum_{h=\max(1,t-w)}^{t-1}|N(i)\cap N(i_h)|$; greedily choose an unscheduled `i` maximizing $g_t(i)$;
- adapted window: $w=\max\{1,\lfloor C_Q/\bar d\rfloor\}$, where $C_Q=\lfloor(C_H-s_D^{\max})/s_Q^{\max}\rfloor$ cached-side slots and $\bar d=|E|/|D_{\mathrm{active}}|$;
- RCM vertex order `p` heuristically reduces bipartite graph bandwidth $\operatorname{bw}(p)=\max_{(u,v)\in E}|p(u)-p(v)|$;
- D-grouped RCM: sort D vertices by `p`, then sort each $N(i)$ by the Q vertices' positions in `p`; bandwidth is a locality surrogate, not the multi-tier cost $C^*$.

Implemented block-RCM method:

- treat every `D_i` and `Q_j` block as a vertex in the undirected bipartite access graph; surviving comparison tasks are edges;
- per connected component: choose the minimum-degree unscheduled root, breadth-first traverse, enqueue unseen neighbors by increasing degree with deterministic block-ID ties, then reverse the component's BFS order;
- RCM returns a block-vertex order, not an edge schedule; filter the full order to obtain the D-group order;
- for each D block in that filtered order, emit all incident tasks contiguously; order its Q tasks by the Q endpoints' positions in the full RCM order;
- optional symmetric variant: filter to Q and emit one contiguous group per Q block; primary sweep fixes D grouping for every scheduler;
- sparse implementation only: `O(|V| + |E|)` storage and traversal plus local adjacency/incident-edge sorting; never materialize the dense comparison matrix or task line graph;
- baseline objective: reduce graph bandwidth/reuse distance; cache-independent, so it ignores `C_d`/`C_h`, cache policy, and tier-specific refill cost;
- controlled sweep: equal 64 MiB D/Q blocks; D-grouped row-major, MECC, and RCM differ only in group/within-group order;
- current result: MECC uses only 0.25% fewer aggregate total transfers than grouped RCM (`0.9975x`; 108/30/42 W/T/L); RCM is 0.36% better at degree 16; both beat grouped row-major by about 2.5% aggregate;
- implication: previous large MECC-RCM gap was a grouping/block-size confound; pursue cache-/tier-aware ordering against both competitive baselines.

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

- **DMA hierarchy as a routing graph:** Treat SSD→HBM, SSD→DRAM→HBM/UVA, HBM→DRAM demotion, and HBM→SSD output as alternative paths; choose a path per object/access rather than assuming SSD→DRAM→HBM.
- **Joint multi-tier access-graph compiler (candidate core):** Extend DiskJoin's single-cache task ordering into joint edge ordering, transfer-path selection, residency, prefetch, and buffer allocation for `D`, `Q`, indexes, and results. One order controls both SSD reuse and DRAM↔HBM reuse; optimizing the tiers independently may conflict.
- **Storage as register allocation:** View block-pair tasks as instructions, `D`/`Q` blocks and indexes as operands, HBM as registers, DRAM as spill space, and direct SSD rereads as rematerialization. Split an object's lifetime at long reuse gaps and choose whether to keep, spill, or recreate it from storage.
- **Two-timescale scheduling heuristic:** Form DRAM-sized task epochs to preserve SSD-level reuse, then reorder edges inside each epoch for HBM reuse; allow one-shot objects to bypass DRAM through direct SSD→HBM DMA. Compare against a small-trace ILP/oracle.
- **Residency-aware bipartite tiling:** Cover the access graph with tiles whose required `D` blocks, `Q` blocks, indexes, staging space, and output reserve fit together in HBM. Greedily add blocks that cover many remaining edges per added byte; run dense tiles with GEMM, sparse tiles with indexed/gather execution, then order tiles by DRAM overlap.
- **Alternate scheduling and allocation:** Start from a DiskJoin/Gorder schedule, simulate tier placement, identify expensive spills/reloads, reweight those objects in the graph-ordering objective, and reorder or retile. Iterate until data-movement cost stops improving instead of deciding order and cache policy independently.
- **Selective DRAM victim admission:** If an HBM object already has a staged DRAM copy, retain it when useful; if it arrived through direct DMA, demote it only when future SSD-read savings exceed HBM→DRAM transfer, DRAM space, and interconnect contention. Otherwise drop and reread directly.
- **Cost-aware future HBM residency:** Use Belady as the equal-size/equal-refill-cost baseline. With variable block/index sizes and DRAM-versus-SSD refill costs, rank or select residency intervals by avoided weighted transfer cost, exact next use, and prefetch deadline rather than farthest-next-use alone.
- **Deadline-aware outstanding-I/O frontier:** Look ahead across independent block-pair tasks far enough to keep the SSD queue busy. Prioritize objects needed soon, but avoid fetching so early that they occupy HBM or staging space for a long time; expand the frontier when cache hits redirect requests away from storage.
- **Separate DMA data path from I/O control path:** The known outer access trace can use CPU-issued asynchronous GDS without GPU-side request management. Reserve GPU-initiated/query-grained requests for data-dependent inner graph search; avoid batch-wide completion barriers.
- **DMA-aware index and block granularity:** Co-tune `D`/`Q` block size, graph degree/node layout, and fetch grouping with SSD page size, IOPS, useful-byte fraction, and per-fetch GPU work. FlashANNS-style stale-frontier overlap applies only to approximate fine search, not exact dense execution.
- **Bound-tightening top-k schedule:** Process cheap or already-resident block pairs that are likely to find close candidates first. Use the improved kth-distance bounds to prune later block pairs, cancel their unissued prefetches, and recompile the remaining work in short epochs; scheduling then removes future I/O instead of only reordering it.
- **Output-aware scheduling and encoding:** Estimate each task's result density, choose pair lists, compressed IDs, or bitmaps accordingly, and size row bands using available output credits. Interleave high- and low-output tasks to smooth sink pressure; compact and write aligned chunks directly from HBM when no host processing is needed.
- **Novelty test against composed prior work:** Compare the joint compiler with DiskJoin ordering plus independent DRAM/HBM Belady, HetCache-style route selection, and GIDS-style lookahead. GDS, a DRAM victim cache, HBM Belady, or direct result writes alone are mechanisms, not the contribution.
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
