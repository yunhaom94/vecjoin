# Ideas
This document contains the ideas and notes for the project.

## Project Name
GPU-AVSJ

## Piloting Idea
*Piloting idea is a single short paragraph that describes the initial idea for the project, could be big could also be small. This should not be changed.*

Using GPUs to do approximate vector similarity join for large, high-dimensional datasets. A main focus should be the use of DMA to reduce the overhead of data transfer between disk and VRAM.


## Main Ideas
*Main ideas are the core concepts and features of the project. This should be a short list between 3-5 ideas that can be changed as the project evolves. **Important:** this section should evolve over time, and the ideas should be refined and updated as the project progresses, and finally becomes a detailed design document for the project.*


### GPU-Accelerated Approximate Vector Similarity Join Overview
Given a database set `D` and a query set `Q` of high-dimensional vectors, find all pairs (d, q) with distance below a threshold (or top-k closest pairs). The system uses a two-level approach:
- **Coarse-level:** Clustering-based partitioning of both `D` and `Q` independently. Centroid distances prune partition pairs before any data is loaded.
- **Fine-level:** Per-partition vector indices on `D` (IVF, CAGRA, IVF-RaBitQ, etc.) prune individual vector comparisons on GPU.

**Target scale:** Billions of vectors at ~1000 dimensions (4KB/vector, ~4TB total).

### Workflow:
1. Use random samples to cluster `D` and `Q` into coarse partition blocks.
   - Done on CPU and assign each vector to its nearest centroid - assign vectors to clusters on disk.
   - Block sizes for D blocks and Q blocks are tuning parameters.

2. Use triangle inequality-based pruning to determine which partition pairs (D_i, Q_j) need to be compared based on centroid distances, and generate a bipartite join graph
   - This is done on CPU.
   - TODO: explore better pruning techniques (Implementation: make this extendable)

3. Find the optimal schedule of block pairs to load into VRAM (see Block Scheduling).
   - This is done on CPU
   - Make scheduling method pluggable, start with random order
  
4. Follow the sequence, using GPU Direct Storage (GDS) for direct disk→VRAM transfers. For evicted blocks, create a "Victim Cache" in RAM to hold recently evicted blocks for potential reuse, reducing redundant disk reads. The RAM cache size is a tuning parameter.

5. For each loaded block pair (D_i, Q_j), execute the comparison on GPU using the per-partition index for second-level pruning, then compute distances for candidate pairs using GEMM. (See Block-Pair Comparison Using Indices)
   1. Implementation: make indexing method pluggable

6. Filter results and sort to get final output.
   1. Store results and sort on CPU
   2. TODO: check if make sense to do it on GPU

#### Block Scheduling
The idea: nested loop-join, but only partial pairs are compared. We need to find the most optimal order to schedule the block pairs to be loaded in to the VRAM. 

In a block nested loop join, the most optimal schedule is to pin blocks of D in VRAM and stream blocks of Q against it, and have pinned as block as many as possible. However, we cannot say the same for our use case.
Formulation.



**Modeling of scheduling sub-problem:**
After the partition size is determined, the scheduling problem is to find the optimal order of block pairs (D_i, Q_j) to load into VRAM. 

Given a cache size (VRAM budget), we want to find out the sequence of loading all block pairs that minimizes the load count. The problem can be formulated as follows: Given a set of pairs of blocks to load (A, a), (A, b), (B, a), (C, c) where upper and lower case are both page id and a cache size C with Belady algorithm as eviction policy, find the sequence of loading these blocks that minimizes the total load count.

Modeling: Bipartite Graph Bandwidth Reduction

- Represent workload as an (m+n) × (m+n) symmetric adjacency matrix for the bipartite graph of D-blocks and Q-blocks. 

M = [ 0   A]
    [ A^T 0]

- Run Reverse Cuthill-McKee (RCM) to get a 1D ordering of all blocks that tightly groups connected nodes 
- Stream blocks into the VRAM cache following this exact 1D RCM sequence.
- Use Belady's algorithm to evict blocks that won't be needed for the longest time in the 1D sequence.

TODO: show this is near optimal
TODO: I nope we can find a theoretical lower bound

#### Block-Pair Comparison Using Indices
Once a block pair (D_i, Q_j) is loaded into VRAM, the system uses the second-level index to prune and execute the comparison entirely on GPU.

**Per-partition vector index (fine-level search on GPU):**
- Build a vector index (IVF, CAGRA, IVF-RaBitQ, etc.) within each coarse partition of `D`. The index structure serves as the fine-grained pruning mechanism.
- E.g., IVF on a ~10M-vector partition → ~3000 IVF clusters as fine-grained units.
- When a coarse pair (D_i, Q_j) is loaded into VRAM, Q_j's vectors are searched against D_i's index to generate candidate pairs. 
- Finally, use GEMM to compute distances for candidates.

**Index storage strategy:**

| Component | Location |
|---|---|
| Coarse centroids  | RAM |
| D block indices |  RAM; loaded to VRAM per pair |
| Vector data | ~35GB per partition | Disk; loaded on-demand via DMA |


### 3. CUDA and GPU Optimization
Details TBD. Candidate per-partition index implementations: FAISS IVF-PQ, CAGRA (cuVS), IVF-RaBitQ (cuVS). flyKNNG's on-the-fly top-k during distance computation (avoids materializing full distance matrix) is relevant for the GPU kernel design.

## Minor Ideas
*Minor ideas are supplementary concepts, features, writing points in the paper, or anything that is not directly related to one of the main ideas. This should be a list of any sizes that can be changed as the project evolves. Each idea should come with a detailed description.*


- **Learned pruning filters:** XJoin/Xling's learned filters could complement centroid-distance pruning by predicting whether a query vector has enough neighbors in a partition, skipping unnecessary searches. Useful for skewed distributions.


- **GPUDirect Storage (GDS):** BaM and TERAIO show GPU-initiated SSD access can bypass CPU. Could enable direct disk→VRAM path, removing the RAM staging step for some transfers. Alternative to CPU-mediated DMA.
- Evaluations
  - The dataset to use
  - The evaluation metrics to use
  - The baselines to compare with (DiskJoin, FAISS, GustANN, Tagore)

- **Partition/block Size is the key tuning parameter**
- More partitions → tighter pruning (fewer edges) but more blocks to schedule, also more compute because within each partition pair, the index is smaller → less pruning → more GPU compute time
- Fewer partitions → less scheduling overhead but coarser pruning (more wasted I/O)
- The block size constraint is the VRAM budget: S_D (data) + D_S * 2 + indices + results < VRAM -> at least double buffer is needed to avoid I/O latency, so each block < (VRAM - index - result buffer) / 3

There is a sweet spot for partition size, because if the partition is too small, the 2nd level pruning is pointless, and we only relies on centroid rather than more advanced indices. However if its too big, we also loss pruning power of the 1 level centroids

^ after discussion, I don't think it is possible to analytically determine the optimal partition count.

Since we are pipelining data transfer, all we need to make sure the total I/O time is lower by the compute time. Include block size experiments.


## Notes
*Notes are any other thoughts, observations, or additional information that is relevant to the project but does not constitute as an "idea" which requires action. This can include things like background, potential challenges, or any other information that is useful for the project. This should be a list of any sizes that can be changed as the project evolves.*
- **Open question: Disk layout for coarse partitions.** After clustering, should we reorganize data on disk so each coarse partition is stored contiguously (like DiskJoin)? One-time preprocessing cost enables sequential DMA reads. How does this interact with GPUDirect Storage (GDS)?


- **Gap in literature:** GPU-accelerated vector *similarity join* at billion scale is essentially unexplored. DiskJoin (SIGMOD 2026) is the only direct predecessor and is CPU-only. Most GPU vector search work focuses on single-query ANN, not all-pairs join. This confirms the novelty of the research direction.










- **Related Work Note (SimJoin):** SimJoin (SIGMOD 2025) is not good for GPU because the spanning-tree-based join window sliding for sequential search.
- Scheduing modeling for reference:
    1: DiskJoin Style Bipartite Graph Reordering (for reference): Pin D-blocks, greedily order Q-blocks by the number of shared D-block neighbors (Gorder-style). This maximizes temporal locality in the block cache, reducing load count. The optimality of this heuristic depends on the degree distribution of the bipartite graph.

    2: Red-Blue Pebble Game on a graph where "completing an edge" requires 2 red pebbles: Use a Greedy BFS approach on the page-dependency graph. Start with the page that has the highest degree (most pairs) and process all its pairs consecutively to keep that page "red" (in cache) as long as possible. I think this is essentially the same as the DiskJoin approach.
    





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