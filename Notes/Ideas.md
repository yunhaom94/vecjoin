# Ideas
This document contains the ideas and notes for the project.

## Piloting Idea
*Piloting idea is a single short paragraph that describes the initial idea for the project, could be big could also be small. This should not be changed.*

Using GPUs to do approximate vector similarity join for large, high-dimensional datasets. A main focus should be the use of DMA to reduce the overhead of data transfer between disk and VRAM.


## Main Ideas
*Main ideas are the core concepts and features of the project. This should be a short list between 3-5 ideas that can be changed as the project evolves. **Important:** this section should evolve over time, and the ideas should be refined and updated as the project progresses, and finally becomes a detailed design document for the project.*


### 1. GPU-Accelerated Approximate Vector Similarity Join
Given a database set `D` and a query set `Q` of high-dimensional vectors, find all pairs (d, q) with distance below a threshold (or top-k closest pairs). The system uses a two-level approach:
- **Coarse-level:** Clustering-based partitioning of both `D` and `Q` independently. Centroid distances prune partition pairs before any data is loaded.
- **Fine-level:** Per-partition vector indices on `D` (IVF, CAGRA, IVF-RaBitQ, etc.) prune individual vector comparisons on GPU.

This unifies the index-based search and data scheduling into a single design — coarse partitions are data movement units, per-partition indices are the search/pruning mechanism.


#### 2 Theoretical Formulation

**Problem setup:**
- **Target scale:** Billions of vectors at ~1000 dimensions (4KB/vector, ~4TB total).
- Both `D` and `Q` are partitioned **independently** using k-means clustering (following DiskJoin). This produces a **bipartite bucket graph** G(m,n) where edges represent coarse partition pairs that need comparison.
- **Construction:** Use a **learning set** (random sample) to determine cluster centers. Stream the full dataset from disk, assigning each vector to its nearest center. Avoids loading 4TB into memory.
- Partitions are units of DMA transfer between disk/RAM/VRAM, sized so that a partition pair fits in VRAM with room for double-buffering.
- **VRAM-adaptive:** Partition count is determined by available VRAM. The algorithm adapts to different GPU memory sizes (e.g., 80GB A100 → ~115 partitions; 12GB consumer GPU → more partitions, same algorithm).

**Variables:**
- m, n: partition counts for D and Q
- s_D = |D|/m, s_Q = |Q|/n: block sizes
- σ: schedule (ordering of block pairs)
- E(m,n): surviving edges after coarse pruning
- C: VRAM capacity, B: bandwidth, L: per-transfer latency
- t_comp(s_D, s_Q): GPU compute time per pair
- R: result buffer size, idx(s_D): index size per D-block

**VRAM constraints:**
- s_D + idx(s_D) + 2·s_Q + R ≤ C  (VRAM feasibility, double-buffered Q)
- C' = C - s_D - idx(s_D) - R  (effective cache budget for Q blocks)
- recall(m, n) ≥ τ  (accuracy)

**Unified Objective — Pipelined Join Time:**
- `min_{m, n, σ}  Σᵢ [(s_D + idx(s_D))/B + L]  +  Σ_k max(t_comp(s_D, s_Q), t_xfer(k | σ, C'))`
- First term: m D-block transition bubbles (unavoidable pipeline stalls)
- Second term: pipelined pair processing; t_xfer = 0 if Q cached, s_Q/B + L if miss

**Key tradeoff triangle:**
- More partitions → tighter pruning (fewer edges) but more blocks to schedule, also more compute because within each partition pair, the index is smaller → less pruning → more GPU compute time
- Fewer partitions → less scheduling overhead but coarser pruning (more wasted I/O)
- Cache capacity C determines reuse potential — more blocks fitting → more reuse

**Partition size tradeoff — transfer volume vs. transfer count:**
- Fewer coarse partitions → fewer DMA transfers (less latency overhead), but coarser pruning → more wasted data loaded.
- More coarse partitions → tighter pruning, less total data transferred, but more DMA transfers with higher per-transfer latency overhead.
- PCIe 4.0/5.0: latency ~5-10μs, bandwidth ~25-64 GB/s. Crossover at ~0.5-1 MB — coarse partitions should be well above this.

**Two regimes determined by t_comp vs. s_Q/B + L:**
- Compute-bound (t_comp > s_Q/B + L): I/O hidden, T ≈ |E| × t_comp. Schedule irrelevant. Optimize by reducing |E| × t_comp.
- I/O-bound (t_comp < s_Q/B + L): GPU idles, T ≈ total_data_transferred / B. Schedule critical. Formulations B/C/E apply.
- Crossover at critical s_D* where α(s_D) = 1/B (for IVF: compute sublinear in s_D, transfer linear in s_Q). Optimal design sits near crossover.

#### 2.1 Block Scheduling
The idea: nested loop-join, but only partial pairs are compared. We need to find the most optimal order to schedule the block pairs to be loaded in to the VRAM.

**Three modelings of the scheduling sub-problem:**
Each formulation below models a different approach to optimizing the schedule σ in the unified objective. All share the VRAM constraint (s_D + idx(s_D) + 2·s_Q + R ≤ C) and effective cache budget C' = C - s_D - idx(s_D) - R for Q-block reuse.

**Formulation B — Bipartite Edge Traversal with Cache (Combinatorial):**
- Two-stage: (1) choose m, n → determines G(m,n), block sizes s_D, s_Q, and cache budget C'; (2) find edge ordering σ minimizing Q-block cache misses under Belady's
- Stage 2: Minimum Fetches Bipartite Edge Ordering — min_σ |{Q-block cache misses}|, subject to ⌊C'/s_Q⌋ cached Q-blocks
- Stage 1: grid-search m, n to minimize Stage 2 cost, subject to s_D + idx(s_D) + 2·s_Q + R ≤ C and recall(m,n) ≥ τ
- NP-hard (Stage 2) → use heuristic (Gorder-style, greedy), grid-search Stage 1
- Clean separation, bipartite structure exploitable. Weakness: two-stage misses interactions; optimal (m,n) depends on Stage 2 heuristic

**Formulation C — Continuous Relaxation with Reuse Factor (Hybrid):**
- Total I/O volume: T(m, n) = ρ_D · |D| + ρ_Q · |Q|, where ρ is avg load count per block
- Pinned-D model: ρ_D = 1; ρ_Q = f(σ, ⌊C'/s_Q⌋), captures schedule quality as a scalar
- Cache slots for Q: k_Q = ⌊C'/s_Q⌋
- Joint optimization: min_{m,n} |D| + ρ_Q(m, n, C') · |Q|, s.t. s_D + idx(s_D) + 2·s_Q + R ≤ C, recall(m,n) ≥ τ
- ρ_Q estimable empirically from learning set — run a few (m,n) on sample data, fit, optimize
- Bridges combinatorial and analytical: schedule quality captured implicitly via ρ_Q

**Formulation E — Sparse Join Matrix Traversal:**
- Join matrix J is m × n binary matrix where J[i,j] = 1 iff (D_i, Q_j) ∈ E(m,n). Processing the join = visiting all nonzeros of J.
- I/O cost: T = s_D · Σᵢ loads(D_i) + s_Q · Σⱼ loads(Q_j). Minimize total block loads over row/column permutation and panel decomposition.
- **Panel traversal:** Group rows into panels of height h s.t. all Q-blocks touched by a panel fit in C'. Process panel-by-panel. Exactly SpMM tiling.
- **Row/column symmetry explicit** — doesn't privilege either relation (unlike pinned-D in C). Optimal may pin Q, pin D, or alternate.
- Panel height = cache allocation: h · s_D + idx(s_D) vs. C' budget for Q-blocks within each panel.
- **Novel twist vs. standard SpMM tiling:** we *choose* the sparsity pattern by choosing m, n. Problem = design a sparse matrix (via partitioning) cheapest to traverse under cache budget C'.
- Full formulation: min_{m, n, Π, σ} s_D · Σᵢ loads(D_i | Π, σ) + s_Q · Σⱼ loads(Q_j | Π, σ), where Π = panel decomposition, σ = row/col permutation, J(m,n) = join matrix from partitioning, subject to s_D + idx(s_D) + 2·s_Q + R ≤ C, recall(m,n) ≥ τ.
- Subsumes B and C: B is the edge ordering view; C is the continuous relaxation with ρ_Q absorbing panel structure.
- **Connections:** Hong & Kung red-blue pebble game (1981) gives I/O lower bounds for matrix computations under cache constraints → potential theoretical contribution. Sparse matrix reordering (RCM, METIS) directly applicable.

#### 2.2 Block-Pair Comparison Using Indices
Once a block pair (D_i, Q_j) is loaded into VRAM, the system uses a two-level index structure to prune and execute the comparison entirely on GPU.

**Coarse-level pruning (before data load):**
- If `dist(c_Di, c_Qj) - r_Di - r_Qj > threshold`, the entire coarse pair is skipped **before any data is loaded**. Evaluated on CPU using only coarse centroids (~0.5MB total).
- Q's coarse partitions use independent clustering with separate centers. No index is built on Q — Q vectors are queries streamed against D's index.

**Per-partition vector index (fine-level search on GPU):**
- Build a vector index (IVF, CAGRA, IVF-RaBitQ, etc.) within each coarse partition of `D`. The index structure serves as the fine-grained pruning mechanism.
- E.g., IVF on a ~10M-vector partition → ~3000 IVF clusters as fine-grained units.
- When a coarse pair (D_i, Q_j) is loaded into VRAM, Q_j's vectors are searched against D_i's index entirely on GPU.

**Index storage strategy:**

| Component | Size (example: 1B vectors, 1000d) | Location |
|---|---|---|
| Coarse centroids | ~115 × 1000d ≈ 0.5MB | RAM (always resident) |
| Per-partition IVF centroids | ~3000 × 1000d ≈ 12MB/partition, ~1.4GB total | RAM; loaded to VRAM per pair |
| Vector data | ~35GB per partition | Disk; loaded on-demand via DMA |


### 3. CUDA and GPU Optimization
Details TBD. Candidate per-partition index implementations: FAISS IVF-PQ, CAGRA (cuVS), IVF-RaBitQ (cuVS). flyKNNG's on-the-fly top-k during distance computation (avoids materializing full distance matrix) is relevant for the GPU kernel design.

## Minor Ideas
*Minor ideas are supplementary concepts, features, writing points in the paper, or anything that is not directly related to one of the main ideas. This should be a list of any sizes that can be changed as the project evolves. Each idea should come with a detailed description.*

- **Result set management on VRAM:** Result buffer sizing and async flush strategy. Double-buffered result output to overlap GPU compute with host transfer. Significant impact on VRAM budget observed in initial experiments.
- **Learned pruning filters:** XJoin/Xling's learned filters could complement centroid-distance pruning by predicting whether a query vector has enough neighbors in a partition, skipping unnecessary searches. Useful for skewed distributions.
- **GPUDirect Storage (GDS):** BaM and TERAIO show GPU-initiated SSD access can bypass CPU. Could enable direct disk→VRAM path, removing the RAM staging step for some transfers. Alternative to CPU-mediated DMA.
- Evaluations
  - The dataset to use
  - The evaluation metrics to use
  - The baselines to compare with (DiskJoin, FAISS, GustANN, Tagore)


## Notes
*Notes are any other thoughts, observations, or additional information that is relevant to the project but does not constitute as an "idea" which requires action. This can include things like background, potential challenges, or any other information that is useful for the project. This should be a list of any sizes that can be changed as the project evolves.*
- **Open question: Disk layout for coarse partitions.** After clustering, should we reorganize data on disk so each coarse partition is stored contiguously (like DiskJoin)? One-time preprocessing cost enables sequential DMA reads. How does this interact with GPUDirect Storage (GDS)?
- **Open question: Unbalanced partitions.** K-means on real data produces uneven clusters. Oversized partitions may not fit in VRAM with their pair. Options: balanced k-means, post-hoc splitting, or adaptive subdivision at runtime.
- **Gap in literature:** GPU-accelerated vector *similarity join* at billion scale is essentially unexplored. DiskJoin (SIGMOD 2026) is the only direct predecessor and is CPU-only. Most GPU vector search work focuses on single-query ANN, not all-pairs join. This confirms the novelty of the research direction.


## Foundations
*Any background of this project, including related work, previous research, or any other information that is relevant to the project. It should not be a list of literatures, but a summary of key concepts, background, SOTA solution patterns and remaining gaps in the literature that are relevant to the project.*

### 1. Problem Definition: Vector Similarity Join

Vector similarity join takes two sets of high-dimensional vectors — a database set D and a query set Q — and finds all pairs (d, q) whose distance is below a threshold ε (distance join) or returns the k closest pairs across the two sets (top-k join). This is fundamentally different from single-query approximate nearest neighbor (ANN) search, which processes one query at a time. Similarity join must process |Q| queries against |D| database vectors simultaneously, creating an opportunity for amortized computation and data reuse: the same database partition can serve multiple queries if they are spatially close. At billion scale (|D|, |Q| ~ 10⁹, d ~ 1000), the data volume (~4TB per set) far exceeds any single machine's RAM or GPU memory, making the problem I/O-bound and requiring principled data scheduling.

The join formulation also differs structurally from batch ANN search (running |Q| independent ANN queries). In batch ANN, each query independently probes an index; the system has no incentive to coordinate which data is loaded for which query. In a join, the system knows the full query set in advance. This enables global scheduling — deciding which (D_i, Q_j) partition pairs to load and in what order — and makes the entire I/O access pattern predetermined, which allows optimal caching (Belady's algorithm) and graph-based task ordering.

### 2. Approximate Nearest Neighbor Search: Indexing Approaches

ANN search on a single vector set underlies the fine-grained search within each partition of a similarity join system. The main indexing paradigms are:

**IVF (Inverted File Index).** Partitions the vector space into Voronoi cells via k-means clustering. At query time, only the closest cell(s) are searched. IVF's effectiveness depends on the number of cells (nlist), the number of cells probed per query (nprobe), and the distribution of vectors across cells. The coarse quantizer (cluster centroids) fits in memory while posting lists (vector subsets) can reside on disk or be loaded on demand. IVF naturally meshes with hierarchical partitioning: coarse partitions define data movement units, and IVF within a partition provides the fine-grained search structure.

**Graph-Based Indexes.** HNSW (Malkov & Yashunin, TPAMI 2018) constructs a multi-layer navigable small-world graph where upper layers contain sparse long-range connections for fast coarse navigation, and the bottom layer is a dense proximity graph for precise local search. HNSW achieves high recall with logarithmic search complexity and became the standard in-memory ANN algorithm. Vamana (DiskANN, Subramanya et al., NeurIPS 2019) simplified HNSW to a single-layer bounded-degree graph with a global entry point, enabling SSD-resident storage: the graph structure and PQ-compressed vectors are stored in SSD pages, and search proceeds via asynchronous beam search with I/O. Graph indexes generally offer higher recall at a given throughput compared to IVF methods, but have larger memory footprints (storing adjacency lists) and higher construction costs.

### 3. GPU-Accelerated Vector Search

GPU parallelism has been applied to ANN search with significant throughput gains over CPU implementations, but with distinct design constraints.

**FAISS (Johnson, Douze & Jégou, 2017)** provided the first GPU-optimized ANN library, with implementations of brute-force search, IVF-PQ, and multi-GPU sharding. Its key GPU contributions are a tiled multi-pass k-selection algorithm operating at ~55% of peak throughput and memory-hierarchy-aware IVF-PQ layouts. FAISS established that GPU ANN search is memory-bandwidth-bound (not compute-bound) for typical dimensions, and that IVF-PQ's lookup-table-based distance computation maps well to GPU shared memory.

**CAGRA (Ootomo et al., ICDE 2024)** brought graph-based ANN to GPU, achieving 33–77x higher throughput than CPU HNSW for large batch queries at 90–95% recall. CAGRA parallelizes both graph construction and search across GPU threads, using hashmap-based visited-node tracking. Its memory footprint includes the full graph adjacency lists plus vectors, which is relevant for VRAM budgeting.

**IVF-RaBitQ (GPU) (Shi et al., 2026)** combines IVF with RaBitQ quantization on GPU, achieving 2.2x higher QPS than CAGRA at ~95% recall while building indexes 7.7x faster. Its compact storage (no raw-vector reranking needed) makes it attractive for VRAM-constrained settings. This is integrated into NVIDIA's cuVS library alongside CAGRA.

**GustANN (Jiang et al., SIGMOD 2025)** targets billion-scale search on a single GPU + SSD, using memory-efficient GPU kernels to maximize query concurrency and CPU-assisted data transfer to overcome PCIe bottlenecks. It demonstrates that GPU+SSD architectures can be cost-effective ($/QPS) for billion-scale workloads.

A common thread: all existing GPU ANN systems focus on single-query or batch-query search against a single prebuilt index. None address the similarity join problem, where both D and Q are large and must be partitioned and scheduled through GPU memory.

### 4. Out-of-Core and Disk-Based Vector Search

When datasets exceed RAM capacity, vector indexes must be partially disk-resident, with I/O scheduling determining end-to-end performance.

**DiskANN** stores Vamana graph pages and PQ codes on SSD, performing beam search with asynchronous I/O. Its page-aligned layout ensures sequential disk reads, and the in-memory PQ codebook enables candidate pre-filtering before full-precision reranking from disk. DiskANN achieves 5ms latency at 95%+ recall for billion-point datasets on a single machine.

**SPANN (Chen et al., NeurIPS 2021)** uses a memory-disk hybrid IVF approach: cluster centroids remain in RAM while posting lists reside on disk. Hierarchical balanced clustering produces even-sized posting lists, and query-aware dynamic pruning skips unnecessary disk reads. SPANN's design — small in-memory index metadata guiding on-demand disk access — parallels our coarse-centroid-in-RAM / partition-data-on-disk hierarchy.

**DiskJoin (SIGMOD 2026)** is the only existing system purpose-built for disk-based vector similarity join. It independently partitions D and Q into buckets (clusters), producing a bipartite bucket graph. Key techniques include: (1) graph reordering (Gorder-style) to maximize temporal locality in the bucket cache, and (2) Belady's optimal caching (feasible because the full access sequence is predetermined by the join schedule). DiskJoin is CPU-only, achieving 50–1000x speedup over alternatives, but does not use GPU acceleration.

### 5. GPU Data Movement and Memory Hierarchy

Moving data through the disk → RAM → VRAM hierarchy is the central bottleneck for out-of-core GPU workloads. The relevant constraints are:

**PCIe bandwidth and latency.** PCIe 4.0 x16 provides ~25 GB/s bidirectional bandwidth with ~5–10μs per-transfer latency. PCIe 5.0 doubles bandwidth to ~64 GB/s. These numbers determine the minimum viable transfer size: below ~0.5–1 MB, per-transfer latency dominates, making fine-grained DMA inefficient. Coarse partitions must be sized well above this threshold.

**DMA and double-buffering.** Overlapping GPU compute with data transfer via CUDA streams and double-buffering is standard practice. While one buffer is being computed on, the next is being filled via DMA. This hides transfer latency as long as compute time exceeds transfer time for each buffer.

**GPUDirect Storage (GDS).** BaM (Qureshi et al., ASPLOS 2023) demonstrated GPU-initiated SSD access bypassing the CPU, with a fine-grained software cache on GPU to coalesce storage requests. TERAIO (Yuan et al., 2025) showed that GDS-based tensor offloading between GPU and SSD can achieve 80.7% of ideal unlimited-GPU-memory performance. These systems establish that a direct disk→VRAM path is feasible and can eliminate the RAM staging bottleneck, though at the cost of more complex GPU-side memory management.

**Multi-tier caching.** Legion (Sun et al., ATC 2023) addresses the disk→RAM→VRAM hierarchy for GNN training, using hierarchical graph partitioning based on access patterns and unified multi-GPU cache management. Tagore uses cluster-aware caching in its asynchronous GPU-CPU-disk indexing framework. Both systems demonstrate that access-pattern-aware caching and prefetching across the three-tier memory hierarchy is essential for GPU workloads with data exceeding VRAM.

### 6. Join Processing on GPUs

GPU join processing has been studied primarily for relational (equi-join) workloads, but the design principles transfer. Hash join co-processing on coupled CPU-GPU architectures (He et al., VLDB 2013) showed that fine-grained CPU-GPU co-processing with GPU-aware partitioning can outperform both CPU-only and GPU-only approaches. The key insight is that partitioning strategy (partition size, number) must be co-designed with the GPU memory hierarchy: partitions too small waste launch overhead, too large cause VRAM spillovers.

For vector similarity join specifically, the block nested loop pattern — pinning one partition in VRAM while streaming the other — is the natural GPU execution model. This mirrors the classical block nested loop join from relational databases, adapted to the GPU's VRAM-as-buffer constraint. The on-the-fly top-k selection technique from flyKNNG (Ji & Wang, ICS 2022) — computing distances via tensor-core matrix multiplication while maintaining a running top-k heap, avoiding full distance matrix materialization — is directly applicable to the GPU kernel executing each (D_i, Q_j) partition pair.

### 7. Gaps in the Literature

The literature on GPU vector search and disk-based vector join is extensive, but several gaps open up at their intersection:

- **No GPU-accelerated vector similarity join exists.** All GPU ANN systems (FAISS, CAGRA, IVF-RaBitQ, GustANN) target single-query or batch-query search. DiskJoin is the only similarity join system at scale, but it is CPU-only. The combination — GPU-accelerated join over billion-scale data with out-of-core scheduling — is unexplored.
- **Three-tier data movement for joins is unaddressed.** DiskJoin handles disk→RAM scheduling; GPU ANN systems assume data fits in VRAM. No existing system manages the full disk→RAM→VRAM hierarchy for a join workload where both D and Q must be partitioned and scheduled.
- **No integration of join-aware scheduling with GPU indexes.** Existing GPU ANN systems build one global index; they do not partition the index into VRAM-sized units coordinated with a global join schedule. The co-design of partition size (controlling DMA transfer granularity) with per-partition GPU index type (controlling search accuracy and VRAM footprint) is an open problem.
- **VRAM budget allocation for join workloads.** In single-query GPU ANN, the index occupies a fixed VRAM footprint. In a join, VRAM must be shared between the pinned D partition (data + index), streaming Q buffers, and result buffers. How to optimally divide this budget — especially given variable result set sizes across partition pairs — has no prior solution.
- **GPUDirect Storage for structured vector workloads.** BaM and TERAIO demonstrate GDS for irregular graph access and tensor offloading respectively, but GDS has not been applied to the structured, predictable access patterns of a partitioned vector join, where entire partitions are loaded sequentially.