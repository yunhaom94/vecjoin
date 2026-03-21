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

### 2. Data Allocation and Scheduling
Since data is too large to fit in VRAM or even RAM, we partition data and schedule transfers across the disk → RAM → VRAM hierarchy, using DMA to minimize transfer overhead.

#### 2.1 Partitioning Strategy: Hierarchical Two-Level Partitioning
- **Target scale:** Billions of vectors at ~1000 dimensions (4KB/vector, ~4TB total).
- Both `D` and `Q` are partitioned **independently** using clustering (e.g., k-means). This produces a **bipartite bucket graph** where edges represent coarse partition pairs that need comparison.
- **Construction:** Use a **learning set** (random sample) to determine cluster centers. Stream the full dataset from disk, assigning each vector to its nearest center. Avoids loading 4TB into memory.

**Level 1 — Coarse Partitions (data movement units):**
- Units of DMA transfer between disk/RAM/VRAM.
- Sized so that a partition pair fits in VRAM with room for double-buffering.
- **VRAM-adaptive:** Partition count is determined by available VRAM. The algorithm adapts to different GPU memory sizes (e.g., 80GB A100 → ~115 partitions; 12GB consumer GPU → more partitions, same algorithm).
- **Coarse-level pruning:** If `dist(c_Di, c_Qj) - r_Di - r_Qj > threshold`, the entire coarse pair is skipped **before any data is loaded**. Evaluated on CPU using only coarse centroids (~0.5MB total).
- Q's coarse partitions use independent clustering with separate centers. No index is built on Q — Q vectors are queries streamed against D's index.

**Level 2 — Per-Partition Vector Index (search/pruning on GPU):**
- Build a vector index (IVF, CAGRA, etc.) within each coarse partition of `D`. The index structure serves as the fine-grained pruning mechanism.
- E.g., IVF on a ~10M-vector partition → ~3000 IVF clusters as fine-grained units.
- When a coarse pair (D_i, Q_j) is loaded into VRAM, Q_j's vectors are searched against D_i's index entirely on GPU.

**Partition size tradeoff — transfer volume vs. transfer count:**
- Fewer coarse partitions → fewer DMA transfers (less latency overhead), but coarser pruning → more wasted data loaded.
- More coarse partitions → tighter pruning, less total data transferred, but more DMA transfers with higher per-transfer latency overhead.
- PCIe 4.0/5.0: latency ~5-10μs, bandwidth ~25-64 GB/s. Crossover at ~0.5-1 MB — coarse partitions should be well above this.

#### 2.2 Execution Model: Block Nested Loop Join on GPU
- **Pin D_i in VRAM** (as large as possible), **stream Q_j partitions** through.
- D_i is loaded once and reused across all its neighboring Q partitions. Q partitions are streamed and evicted.
- This minimizes D reloads since D carries the index overhead that must stay pinned.
- **VRAM budget equation:**
  ```
  VRAM = D_i_data + D_i_index + 2 × Q_j_buf (double-buffer) + 2 × Result_buf (double-buffer) + Scratch
  ```
  - D_i_data should be maximized; everything else minimized.
  - **Result buffer is a key open problem** — was significant in initial experiments. Every GB for results = fewer D vectors pinned = more D reloads.
  - Possible approach: fixed result buffer with async flush to RAM when full (double-buffer results too), so GPU compute is never stalled.
  - The learning set could estimate result density per partition pair for smarter VRAM budget allocation.

#### 2.3 Index Storage Strategy
| Component | Size (example: 1B vectors, 1000d) | Location |
|---|---|---|
| Coarse centroids | ~115 × 1000d ≈ 0.5MB | RAM (always resident) |
| Per-partition IVF centroids | ~3000 × 1000d ≈ 12MB/partition, ~1.4GB total | RAM; loaded to VRAM per pair |
| Vector data | ~35GB per partition | Disk; loaded on-demand via DMA |

#### 2.4 Task Ordering and Caching (TBD)
- DiskJoin uses graph reordering (Gorder-style) to maximize cache reuse and Belady's optimal caching (possible because the full access sequence is predetermined). Both techniques are applicable to our bipartite bucket graph across the RAM and VRAM cache levels.
- Tagore and Legion provide precedent for multi-tier (disk→RAM→VRAM) caching with cluster-aware eviction.

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


# Notes
*Notes are any other thoughts, observations, or additional information that is relevant to the project but does not constitute as an "idea" which requires action. This can include things like background, potential challenges, or any other information that is useful for the project. This should be a list of any sizes that can be changed as the project evolves.*
- **Target scale:** Billions of vectors, ~1000 dimensions, float32 (4KB/vector, ~4TB total). Algorithm should be VRAM-adaptive (flexible partition count based on available GPU memory).
- **Open question: Disk layout for coarse partitions.** After clustering, should we reorganize data on disk so each coarse partition is stored contiguously (like DiskJoin)? One-time preprocessing cost enables sequential DMA reads. How does this interact with GPUDirect Storage (GDS)?
- **Open question: Unbalanced partitions.** K-means on real data produces uneven clusters. Oversized partitions may not fit in VRAM with their pair. Options: balanced k-means, post-hoc splitting, or adaptive subdivision at runtime.
- **Gap in literature:** GPU-accelerated vector *similarity join* at billion scale is essentially unexplored. DiskJoin (SIGMOD 2026) is the only direct predecessor and is CPU-only. Most GPU vector search work focuses on single-query ANN, not all-pairs join. This confirms the novelty of the research direction.
