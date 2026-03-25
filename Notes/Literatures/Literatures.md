# Literatures
This document contains a list of literatures that is relevant to this project. Each literature is formatted in the following way, and each literature is separated by a horizontal line (---). The ./Notes/Literatures/ folder contains the full papers of the literatures listed in this file, with name format "{title}.pdf".

---
- **Title**: The title of the literature.
- **Author(s)**: The author(s) of the literature.
- **Year**: The year the literature was published.
- **Venue**: The venue where the literature was published (e.g., journal, conference).
- **Summary**: A brief summary of the literature. This should include the main ideas or methodology used in the literature, as well as any key findings or conclusions.
- **Relevance**: A brief explanation of how this literature is relevant to the project.
---

---
- **Title**: DiskJoin: Disk-Based Similarity Join for Billion-Scale Vector Datasets
- **Author(s)**: (See paper for full author list)
- **Year**: 2025/2026
- **Venue**: SIGMOD 2026
- **Link**: https://arxiv.org/abs/2508.18494
- **Summary**: Proposes a disk-based approach for exact/approximate vector similarity join on billion-scale datasets using a single machine with NVMe SSDs. Key techniques: (1) bucket-based partitioning where vectors are clustered and stored contiguously on disk, (2) task ordering via graph reordering (Gorder-style objective) to maximize temporal locality in bucket cache, (3) Belady's optimal caching algorithm (applicable because the full access sequence is predetermined), (4) probabilistic pruning of bucket pairs using arccos-based volume bounds to control recall-efficiency tradeoff. Achieves 50-1000x speedup over alternatives with read amplification near 1.0. Cross-join variant partitions both datasets independently into a bipartite bucket graph.
- **Relevance**: Directly relevant to our data scheduling design. DiskJoin solves the disk→RAM scheduling problem for vector similarity join; we extend this to the disk→RAM→VRAM three-tier setting. Key ideas we adapt: independent partitioning of D and Q (bipartite bucket graph), centroid-distance pruning, and the predetermined access schedule enabling optimal caching (Belady's). Our hierarchical two-level partitioning extends their single-level approach to handle the GPU data movement hierarchy.
---

---
- **Title**: Billion-scale similarity search with GPUs
- **Author(s)**: Jeff Johnson, Matthijs Douze, Herve Jegou
- **Year**: 2017
- **Venue**: IEEE Transactions on Big Data (also arXiv 1702.08734)
- **Summary**: The foundational paper for GPU-accelerated vector similarity search, introducing the FAISS library. Proposes a highly optimized GPU k-selection algorithm that operates at up to 55% of peak theoretical performance, enabling nearest neighbor implementations 8.5x faster than prior GPU state of the art. Designs optimized GPU implementations for brute-force search, approximate search via inverted file (IVF) indexes with product quantization (PQ), and compressed-domain search. Key contributions include tiled multi-pass k-selection, efficient IVF-PQ layout for GPU memory hierarchy, and multi-GPU sharding strategies (index sharding and data sharding). Demonstrates billion-scale k-NN graph construction on 4 GPUs.
- **Relevance**: The baseline GPU vector search system our work builds upon. FAISS's IVF-PQ index design and multi-GPU sharding strategies directly inform our per-partition GPU index design. Its k-selection algorithm and GPU memory hierarchy optimizations are foundational. Our system extends FAISS's single-level IVF approach to a two-level hierarchical partitioning scheme with out-of-core data scheduling.
---

---
- **Title**: CAGRA: Highly Parallel Graph Construction and Approximate Nearest Neighbor Search for GPUs
- **Author(s)**: Hiroyuki Ootomo, Akira Naruse, Corey Nolet, Ray Wang, Tamas Feher, Yong Wang
- **Year**: 2024
- **Venue**: ICDE 2024 (also arXiv 2308.15136)
- **Summary**: Introduces CAGRA, a GPU-optimized graph-based ANNS algorithm that achieves orders-of-magnitude speedups over CPU graph methods. Key innovations: (1) GPU-parallel graph construction that is 2.2-27x faster than HNSW, (2) a search algorithm designed around GPU parallelism achieving 33-77x higher throughput than HNSW in large-batch queries at 90-95% recall, and (3) 3.8-8.8x faster than prior GPU ANNS methods. The algorithm uses a multi-kernel pipeline with hashmap-based visited-node tracking for efficient parallel graph traversal. Integrated into the NVIDIA RAPIDS cuVS library.
- **Relevance**: CAGRA is one of the candidate per-partition GPU indexes in our system. Its graph-based approach offers high recall at high throughput within GPU memory, making it suitable for fine-grained pruning once a partition is loaded into VRAM. Understanding its memory footprint (graph adjacency lists + vectors) is critical for our VRAM budget allocation. Its construction cost is also relevant for the index-building phase of our partitions.
---

---
- **Title**: Tagore: Scalable Graph Indexing using GPUs for Approximate Nearest Neighbor Search
- **Author(s)**: Zhonggen Li, Xiangyu Ke, Yifan Zhu, Bocheng Yu, Baihua Zheng, Yunjun Gao
- **Year**: 2025
- **Venue**: SIGMOD 2026
- **Summary**: Presents a GPU-accelerated library for constructing refinement-based graph indexes (NSG, Vamana) at scale. Key contributions: (1) GNN-Descent, a GPU-specific algorithm for k-NN graph initialization using a two-phase descent procedure with highly parallelized neighbor updates; (2) CFS, a universal pruning formulation with two generalized GPU kernels for parallel processing complex neighbor dependencies; (3) for datasets exceeding GPU memory, an asynchronous GPU-CPU-disk indexing framework with cluster-aware caching that minimizes disk I/O. Achieves 1.32x to 112.79x speedup over prior methods while maintaining index quality.
- **Relevance**: Directly relevant for our out-of-core GPU processing design. Tagore's asynchronous GPU-CPU-disk framework with cluster-aware caching addresses the same multi-tier data movement challenge we face, albeit for index construction rather than join execution. Their cluster-aware caching mechanism -- which ensures data locality by processing clusters of nearby vectors together -- provides a concrete precedent for our hierarchical partition scheduling. Their technique of overlapping GPU computation with disk I/O via asynchronous pipelines informs our double-buffering approach.
---

---
- **Title**: High-Throughput, Cost-Effective Billion-Scale Vector Search with a Single GPU (GustANN)
- **Author(s)**: Haodi Jiang, Hao Guo, Minhui Xie, Jiwu Shu, Youyou Lu
- **Year**: 2025
- **Venue**: SIGMOD 2025 (Proc. ACM Manag. Data)
- **Summary**: Proposes GustANN, a GPU-centric, CPU-assisted architecture for billion-scale graph-based vector search using GPU+SSD. Key techniques: (1) memory-efficient GPU kernels that minimize VRAM usage during graph search, allowing higher concurrency for GPU and SSD access; (2) CPU-assisted transfer to address the PCIe bandwidth bottleneck on the GPU side; (3) pivot search for inter-SSD load balancing across multiple NVMe drives. Achieves at least 2.50x higher throughput than existing ANNS systems and is 2.62x more cost-effective (measured in $/QPS). (Note: Full text PDF was not available for download.)
- **Relevance**: Highly relevant as it addresses the same GPU+SSD architecture for billion-scale vector workloads. GustANN's memory-efficient GPU kernels and CPU-assisted PCIe transfer directly inform our VRAM budget management and data movement pipeline. Their approach of maximizing GPU concurrency while managing limited VRAM is analogous to our challenge of fitting partition data, indexes, and result buffers within VRAM.
---

---
- **Title**: Vector and Line Quantization for Billion-scale Similarity Search on GPUs (VLQ-ADC)
- **Author(s)**: Wei Chen, Jincai Chen, Fuhao Zou, Yuan-Fang Li, Ping Lu, Qiang Wang, Wei Zhao
- **Year**: 2019
- **Venue**: Future Generation Computer Systems (also arXiv 1901.00275)
- **Summary**: Proposes a hierarchical inverted index structure using vector and line quantization for GPU-based billion-scale ANN search. The two-level quantization first uses coarse vector quantization to partition data, then applies line quantization within each partition to further subdivide the search space, generating more indexed regions while maintaining comparable memory consumption. The system VLQ-ADC significantly outperforms FAISS and other GPU/CPU baselines on SIFT1B and DEEP1B datasets in both accuracy and search speed.
- **Relevance**: Directly relevant to our hierarchical partitioning design. VLQ-ADC's two-level index -- coarse partitioning for data organization followed by fine-grained quantization within partitions -- is conceptually similar to our coarse partitions (for DMA-sized data movement) with per-partition indexes (IVF/CAGRA) for GPU-side pruning. Their GPU implementation insights for hierarchical inverted indexes inform our per-partition index layout in VRAM.
---

---
- **Title**: IVF-RaBitQ (GPU): GPU-Native Approximate Nearest Neighbor Search with Fast Index Build and Search
- **Author(s)**: Jifan Shi, Jianyang Gao, James Xia, Tamas Bela Feher, Cheng Long
- **Year**: 2026
- **Venue**: arXiv preprint (arXiv 2602.23999), integrated into NVIDIA cuVS
- **Summary**: Presents a GPU-native ANNS solution integrating the cluster-based IVF method with RaBitQ quantization for efficient low-bit encoding. Key contributions: (1) scalable GPU-native RaBitQ quantization for fast, accurate index building; (2) GPU-native distance computation schemes for quantized codes with a fused search kernel achieving high throughput at high recall; (3) strong performance frontier across recall, throughput, build time, and storage. At recall ~0.95, achieves 2.2x higher QPS than CAGRA while building indexes 7.7x faster. Compared to IVF-PQ, delivers 2.7x higher throughput while avoiding raw vector access for reranking.
- **Relevance**: A strong candidate for our per-partition GPU index. IVF-RaBitQ's compact storage footprint (low-bit quantization avoids storing raw vectors for reranking) is advantageous for our VRAM-constrained setting where we need to fit partition data, index, and result buffers. Its fast build time is also relevant since we may need to construct per-partition indexes. The IVF-based structure naturally aligns with our two-level partitioning hierarchy.
---

---
- **Title**: SIVF: GPU-Resident IVF Index for Streaming Vector Analytics
- **Author(s)**: Dongfang Zhao
- **Year**: 2026
- **Venue**: arXiv preprint (arXiv 2601.11808)
- **Summary**: Presents a GPU-native IVF index that enables high-velocity, in-place mutation via novel data structures and algorithms. Key innovations: (1) conflict-free slab allocation for GPU-resident dynamic lists; (2) coalesced search on non-contiguous memory layouts; (3) achieves deletion latency orders of magnitude lower than baseline. Integrated into FAISS. On a 12-GPU cluster, achieves near-linear scalability with 4.07M vectors/s ingestion throughput and 108.5M vectors/s deletion throughput.
- **Relevance**: Relevant for understanding GPU-resident IVF index implementation details. SIVF's slab-based memory allocation on GPU and coalesced search over non-contiguous memory provide practical insights for our per-partition IVF index that must reside in VRAM alongside data and result buffers. Their approach to managing dynamic GPU memory is relevant for our VRAM budget allocation.
---

---
- **Title**: GPU-Initiated On-Demand High-Throughput Storage Access in the BaM System Architecture
- **Author(s)**: Zaid Qureshi, Vikram Sharma Mailthody, Isaac Gelado, Seungwon Min, Amna Masood, Jeongmin Park, Jinjun Xiong, C.J. Newburn, Dmitri Vainbrand, I-Hsin Chung, Michael Garland, William Dally, Wen-mei Hwu
- **Year**: 2023
- **Venue**: ASPLOS 2023
- **Summary**: Presents the BaM (Big Accelerator Memory) system architecture enabling GPU-initiated, on-demand storage access bypassing the CPU. Key components: (1) a fine-grained software cache on GPU to coalesce storage requests and minimize I/O amplification; (2) high-throughput GPU-to-SSD command queues enabling massive GPU thread concurrency to fully utilize storage devices and PCIe interconnect; (3) GPUDirect-based data path that removes CPU from the storage access critical path. Achieves 1.0-1.49x end-to-end speedup for graph analytics while reducing hardware costs by up to 21.7x over host-memory baselines. Speeds up data-analytics workloads by 5.3x over CPU-initiated storage access.
- **Relevance**: Foundational for our GPU-SSD data path design. BaM demonstrates that GPU-initiated storage access via GPUDirect can eliminate CPU bottlenecks for data-intensive GPU workloads. Their fine-grained software cache on GPU and high-throughput I/O queue design directly inform our disk→VRAM data transfer mechanism. While our current design uses CPU-mediated DMA (host staging), BaM's GPU-initiated approach represents a possible alternative for reducing data movement latency and CPU overhead in our three-tier hierarchy.
---

---
- **Title**: Cost-Efficient LLM Training with Lifetime-Aware Tensor Offloading via GPUDirect Storage (TERAIO)
- **Author(s)**: Ziqi Yuan, Haoyang Zhang, Yirui Eric Zhou, Apoorve Mohan, I-Hsin Chung, Seetharami Seelam, Jian Huang
- **Year**: 2025
- **Venue**: arXiv preprint (arXiv 2506.06472)
- **Summary**: Presents TERAIO, a lifetime-aware tensor offloading framework that uses GPUDirect Storage for direct GPU-SSD data migration. Key insights: (1) only 1.7% of allocated GPU memory is active at any time in LLM training, creating large offloading opportunities; (2) tensor lifetime profiling enables optimized offloading/prefetching plans; (3) GPUDirect Storage allows direct tensor migration between GPUs and SSDs, bypassing CPU and maximizing SSD bandwidth utilization. Achieves 1.47x average improvement over ZeRO-Offload/Infinity, reaching 80.7% of ideal unlimited-GPU-memory performance.
- **Relevance**: Relevant for our GPU memory management and data scheduling design. TERAIO's use of GPUDirect Storage for direct GPU-SSD transfer and its lifetime-aware prefetching/eviction policy provide a concrete example of the kind of multi-tier memory management we need. Their profiling-based approach to determining when tensors should be offloaded/prefetched is analogous to our predetermined task schedule that enables optimal caching across the disk→RAM→VRAM hierarchy.
---

---
- **Title**: Legion: Automatically Pushing the Envelope of Multi-GPU System for Billion-Scale GNN Training
- **Author(s)**: Jie Sun, Li Su, Zuocheng Shi, Wenting Shen, Zeke Wang, Lei Wang, Jie Zhang, Yong Li, Wenyuan Yu, Jingren Zhou, Fei Wu
- **Year**: 2023
- **Venue**: USENIX ATC 2023 (also arXiv 2305.16588)
- **Summary**: Proposes Legion, a multi-GPU GNN training system for billion-scale graphs. Key innovations: (1) hierarchical graph partitioning that clusters vertices with similar access patterns, significantly improving multi-GPU cache hit rates; (2) a unified multi-GPU cache that jointly caches graph topology and feature data, minimizing PCIe traffic by caching the hottest data; (3) automatic cache management that adapts cache plans to hardware specifications and graph properties to maximize training throughput. Supports billion-scale GNN training on a single multi-GPU machine, outperforming state-of-the-art cache-based systems.
- **Relevance**: Highly relevant to our multi-tier cache management design. Legion addresses the same fundamental challenge we face: managing a hierarchy of storage (disk → host RAM → GPU VRAM) for data that far exceeds GPU memory. Their hierarchical partitioning for cache locality, unified cache management across the memory hierarchy, and automatic adaptation to hardware constraints provide directly transferable design principles. Their approach of clustering data by access patterns to improve cache performance parallels our coarse partitioning strategy for DMA-efficient data movement.
---

---
- **Title**: SPANN: Highly-efficient Billion-scale Approximate Nearest Neighbor Search
- **Author(s)**: Qi Chen, Bing Zhao, Haidong Wang, Mingqin Li, Chuanjie Liu, Zengzhong Li, Mao Yang, Jingdong Wang
- **Year**: 2021
- **Venue**: NeurIPS 2021 (also arXiv 2111.08566)
- **Summary**: Presents SPANN, a memory-disk hybrid ANNS system using inverted index methodology. Stores centroid points of posting lists in memory and large posting lists on disk. Key techniques: (1) hierarchical balanced clustering for balanced posting list lengths; (2) posting list augmentation by adding points in the closure of corresponding clusters to improve recall; (3) query-aware dynamic pruning of unnecessary posting list accesses. Achieves 2x faster search than DiskANN at 90% recall with the same memory budget on billion-scale datasets, with latency around 1ms using only 32GB memory.
- **Relevance**: Relevant to our partitioning and data scheduling design. SPANN's approach of keeping centroid metadata in RAM while storing full posting lists on disk parallels our two-level hierarchy where coarse partition centroids guide scheduling decisions while full partition data resides on disk/RAM. Their hierarchical balanced clustering and posting list augmentation techniques inform our coarse partition construction. The query-aware pruning of posting list accesses is analogous to our centroid-distance-based pruning of partition pairs.
---

---
- **Title**: Xling: A Learned Filter Framework for Accelerating High-Dimensional Approximate Similarity Join (XJoin)
- **Author(s)**: Yifan Wang, Vyom Pathak, Daisy Zhe Wang
- **Year**: 2024
- **Venue**: arXiv preprint (arXiv 2402.13397)
- **Summary**: Proposes Xling, a generic framework for building learning-based metric space filters to accelerate high-dimensional similarity join. Uses a regression model to predict whether a query point has enough neighbors, enabling the skipping of queries without neighbors. XJoin integrates this filter into loop-based similarity join methods, reducing unnecessary neighbor searches. The framework supports transferability to new datasets without retraining and can be plugged into any loop-based similarity join method.
- **Relevance**: Relevant as a complementary pruning technique for our similarity join. XJoin's learned filter approach could be used to skip query vectors that are unlikely to have join partners in a given database partition, reducing unnecessary GPU computation. This is complementary to our centroid-distance-based pruning and could provide additional speedup for skewed data distributions.
---

---
- **Title**: Evaluating Modern GPU Interconnect: PCIe, NVLink, NV-SLI, NVSwitch and GPUDirect
- **Author(s)**: Ang Li, Shuaiwen Leon Song, Jieyang Chen, Jiajia Li, Xu Liu, Nathan Tallent, Kevin Barker
- **Year**: 2019
- **Venue**: IEEE Transactions on Parallel and Distributed Systems (also arXiv 1903.04611)
- **Summary**: Comprehensive evaluation of five GPU interconnect technologies (PCIe, NVLink-V1, NVLink-V2, NVLink-SLI, NVSwitch) across six high-end platforms including DGX-1, DGX-2, and Summit supercomputer. Key findings: (1) identifies four new types of GPU communication network NUMA effects caused by NVLink topology, connectivity, routing, and PCIe chipset design; (2) demonstrates that GPU combination choice significantly impacts communication efficiency; (3) provides practical bandwidth measurements and latency characterization for different interconnect types. Offers guidance for GPU task allocation, scheduling, and communication-oriented tuning.
- **Relevance**: Relevant for understanding the PCIe/NVLink bandwidth constraints that govern our DMA data movement between host RAM and GPU VRAM. The measured PCIe and NVLink bandwidths directly constrain our double-buffering and data streaming design. Their NUMA effect observations are important for multi-GPU extensions of our system where partition-to-GPU assignment must consider interconnect topology.
---

---
- **Title**: Efficient exact K-nearest neighbor graph construction for billion-scale datasets using GPUs with tensor cores (flyKNNG)
- **Author(s)**: Zhuoran Ji, Cho-Li Wang
- **Year**: 2022
- **Venue**: ICS 2022 (International Conference on Supercomputing)
- **Summary**: Presents flyKNNG, a GPU k-NN graph construction algorithm for billion-scale datasets that leverages tensor core matrix multiplication units. Key innovations: (1) deploys distance matrix calculation to matrix multiplication units (tensor cores); (2) on-the-fly top-k selection to avoid materializing the full distance matrix in device memory; (3) co-designed distance calculation and top-k selection for optimized data reuse and instruction-level parallelism. Achieves 4.67x speedup over FAISS/cuML for k-NN graph construction. (Note: Full text PDF was not available for download.)
- **Relevance**: Relevant for our GPU-side brute-force distance computation within partitions. flyKNNG's on-the-fly top-k selection during distance matrix computation avoids materializing the full NxM distance matrix, which is critical when processing large partition pairs in VRAM with limited buffer space. Their tensor-core-optimized distance computation informs our GPU kernel design for the block nested loop join within partitions.
---

---
- **Title**: Revisiting Co-Processing for Hash Joins on the Coupled CPU-GPU Architecture
- **Author(s)**: Jiong He, Mian Lu, Bingsheng He
- **Year**: 2013
- **Venue**: VLDB 2013 (arXiv 1307.1955)
- **Summary**: Studies GPU co-processing for hash joins on coupled CPU-GPU architectures (AMD APUs). Key contributions: (1) explores fine-grained CPU-GPU co-processing mechanisms for hash joins with and without partitioning; (2) extends cost models to automatically guide design decisions across the CPU-GPU co-processing design space; (3) demonstrates that fine-grained co-processing achieves up to 53% improvement over CPU-only, 35% over GPU-only, and 28% over conventional co-processing. Studies both no-partition hash join and radix-partition hash join variants on GPU.
- **Relevance**: Relevant background for GPU join processing design. While focused on equi-joins rather than similarity joins, the GPU join processing principles -- partitioning strategies, CPU-GPU co-processing, and memory hierarchy management -- transfer to our block nested loop similarity join. Their cost modeling approach for balancing GPU and CPU workloads informs our task scheduling between host-side data staging and GPU-side join computation.
---

---
- **Title**: DiskANN++: Efficient Page-based Search over Isomorphic Mapped Graph Index using Query-sensitivity Entry Vertex
- **Author(s)**: Jiongkang Ni, Xiaoliang Xu, Yuxiang Wang, Can Li, Jiajie Yao, Shihai Xiao, Xuecang Zhang
- **Year**: 2023
- **Venue**: arXiv preprint (arXiv 2310.00402)
- **Summary**: Optimizes DiskANN's disk-based graph search by addressing two I/O issues: (1) long routing paths from the static entry vertex to the query's neighborhood, addressed by a query-sensitive entry vertex selection strategy; (2) redundant I/O requests during routing, addressed by an isomorphic mapping that optimizes SSD page layout and an asynchronous Pagesearch algorithm. Achieves 1.5-2.2x QPS improvement over DiskANN at the same accuracy.
- **Relevance**: Relevant for understanding SSD layout optimization and I/O reduction techniques for disk-resident vector indexes. DiskANN++'s page-aligned SSD layout optimization and asynchronous I/O are relevant to our disk→RAM data staging design, where partition data must be stored contiguously for efficient sequential reads.
---

---
- **Title**: Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs
- **Author(s)**: Yu. A. Malkov, D. A. Yashunin
- **Year**: 2018
- **Venue**: IEEE Transactions on Pattern Analysis and Machine Intelligence (also arXiv 1603.09320)
- **Summary**: Introduces HNSW, a graph-based approximate nearest neighbor search algorithm using a hierarchical multi-layer structure of proximity graphs. Elements are inserted into layers with exponentially decaying probability, creating a skip-list-like hierarchy where upper layers contain long-range links for fast coarse navigation and lower layers provide fine-grained local search. The algorithm achieves logarithmic search complexity scaling and strong recall-throughput tradeoffs. HNSW set a new state of the art for in-memory ANN search and became the most widely adopted graph-based ANN algorithm, serving as the backbone of production vector databases (e.g., Milvus, Qdrant, Weaviate) and as the CPU baseline against which GPU methods are benchmarked.
- **Relevance**: HNSW is the foundational graph-based ANN algorithm that CAGRA, Tagore (NSG/Vamana construction on GPU), and DiskANN build upon. Understanding HNSW's multi-layer graph structure, greedy beam search, and neighbor selection heuristics is essential background for evaluating the per-partition GPU index options in our system. HNSW's CPU-only design and its memory-bound nature (storing full graph in RAM) motivate the GPU-accelerated and disk-aware approaches our project pursues.
---

---
- **Title**: DiskANN: Fast Accurate Billion-point Nearest Neighbor Search on a Single Node
- **Author(s)**: Suhas Jayaram Subramanya, Fnu Devvrit, Harsha Vardhan Simhadri, Ravishankar Krishnawamy, Rohan Kadekodi
- **Year**: 2019
- **Venue**: NeurIPS 2019 (also arXiv 1907.05275)
- **Summary**: Proposes the Vamana graph index and DiskANN system for billion-scale ANN search on a single machine with SSDs. Key contributions: (1) the Vamana graph index, which builds a bounded-degree directed graph with a single global medoid entry point and a robust pruning rule (alpha-pruning) that controls the graph's degree vs. recall tradeoff; (2) a disk-based search algorithm that stores the graph and compressed (PQ) vectors in SSD pages, performs beam search with asynchronous I/O, and uses an in-memory PQ codebook for candidate re-ranking; (3) demonstrates billion-scale search with 5ms latency at 95%+ recall using a single machine with 64GB RAM and SSDs, making billion-scale ANN accessible without distributed clusters.
- **Relevance**: DiskANN established the paradigm of SSD-resident vector indexes with in-memory compressed representations for billion-scale search. Its Vamana graph construction is the foundation for CAGRA (GPU-parallelized Vamana) and Tagore. DiskANN's SSD page layout strategy and asynchronous I/O beam search directly inform our understanding of disk-based vector data management. Our system differs in that we perform similarity join (not single-query search) and target GPU execution, but DiskANN's disk I/O optimization techniques are foundational context.
---

---
- **Title**: RaBitQ: Quantizing High-Dimensional Vectors with a Theoretically Optimal Algorithm
- **Author(s)**: Jianyang Gao, Cheng Long
- **Year**: 2024
- **Venue**: SIGMOD 2024 (also arXiv 2405.12497)
- **Summary**: Proposes RaBitQ, a randomized quantization method that encodes high-dimensional vectors using single-bit codes with theoretical error bounds. Unlike heuristic quantization methods (PQ, OPQ, ScaNN), RaBitQ provides a rigorous theoretical framework: it projects normalized vectors onto a random orthogonal basis and rounds each coordinate to the nearest bit, achieving near-optimal quantization error. Key innovations include an efficient estimator for inner product/distance computation from quantized codes and a reranking strategy that avoids accessing raw vectors. Achieves competitive recall-QPS tradeoffs with 32x compression (1 bit per dimension) while providing theoretical guarantees on estimation error.
- **Relevance**: RaBitQ is the underlying quantization method for IVF-RaBitQ (GPU), one of our primary candidate per-partition indexes. Understanding its theoretical foundations — particularly the single-bit encoding, error bounds, and distance estimation without raw vector access — is essential for reasoning about our system's accuracy guarantees and VRAM footprint. The ability to avoid raw vector reranking is especially valuable in our VRAM-constrained setting where storing both quantized codes and raw vectors per partition would double memory requirements.
---

---
- **Title**: Product Quantization for Nearest Neighbor Search
- **Author(s)**: Hervé Jégou, Matthijs Douze, Cordelia Schmid
- **Year**: 2011
- **Venue**: IEEE Transactions on Pattern Analysis and Machine Intelligence
- **Summary**: Introduces product quantization (PQ), a vector compression technique that decomposes high-dimensional vectors into subvectors and quantizes each subspace independently with a small codebook. Distances between a query vector and compressed database vectors are approximated using precomputed lookup tables (ADC — asymmetric distance computation), enabling fast exhaustive search over billions of vectors with compact codes (e.g., 8 bytes per 128-d vector). Combined with an inverted file index (IVF) for non-exhaustive search, IVF-PQ became the dominant paradigm for large-scale approximate nearest neighbor search. The paper also introduces the IVFADC structure that combines coarse quantization for candidate selection with PQ for distance approximation.
- **Relevance**: PQ is the foundational compression technique underlying FAISS's IVF-PQ index, one of our candidate per-partition GPU indexes. The IVF-PQ structure — coarse quantizer for inverted file partitioning, PQ codes for compressed distance estimation — is the template for all IVF-based indexes in our system. Understanding PQ's subspace decomposition, codebook training, and ADC distance computation is prerequisite background for RaBitQ (which improves upon PQ's heuristic approach with theoretical guarantees) and for the GPU kernel design that must perform lookup-table-based distance computation in VRAM. (Note: Full text PDF was not available for download.)
---

---
- **Title**: Access Path Selection in a Relational Database Management System
- **Author(s)**: P. Griffiths Selinger, M. M. Astrahan, D. D. Chamberlin, R. A. Lorie, T. G. Price
- **Year**: 1979
- **Venue**: ACM SIGMOD International Conference on Management of Data
- **Summary**: Describes the System R query optimizer, the first cost-based optimizer for relational databases. Introduces the dynamic programming approach to selecting access paths (indexes, join orders, join methods) for SQL queries, with closed-form I/O cost formulas for different access paths. Established the plan enumeration + cost estimation paradigm used by virtually all modern database systems.
- **Relevance**: Context for the classic join-scheduling formalization. The Selinger-style DP-over-join-orderings approach contrasts with DiskJoin's MECC graph formulation — Selinger optimizes which order to execute joins with cost formulas, while MECC optimizes the traversal order of a bipartite partition graph to minimize cache misses.
---

---
- **Title**: Join Processing in Database Systems with Large Main Memories
- **Author(s)**: Leonard D. Shapiro
- **Year**: 1986
- **Venue**: ACM Transactions on Database Systems (TODS), Vol. 11, No. 3
- **Summary**: Comprehensive analysis of join algorithms (nested loop, sort-merge, hash join variants including hybrid hash join) under varying memory sizes. Shows that hybrid hash join is optimal for large-memory environments by keeping some partitions in memory while spilling others to disk. Provides I/O cost formulas accounting for buffer allocation and partition sizing.
- **Relevance**: Foundational I/O cost models for nested block loop join. The tradeoffs analyzed — partition size vs. number of passes, buffer allocation vs. I/O cost — directly parallel our coarse partition sizing and VRAM-adaptive partitioning decisions.
---

---
- **Title**: Query Evaluation Techniques for Large Databases
- **Author(s)**: Goetz Graefe
- **Year**: 1993
- **Venue**: ACM Computing Surveys, Vol. 25, No. 2
- **Summary**: Landmark 100+ page survey covering sorting, hashing, all join algorithms (nested loops, sort-merge, hash, index-based), aggregation, the iterator (Volcano-style) execution model, buffer management, and parallel query evaluation. The most comprehensive reference on physical query processing in relational databases.
- **Relevance**: Context for the classic approach to join scheduling via closed-form I/O cost formulas. The partitioning and scheduling tradeoffs discussed (partition granularity, buffer allocation, I/O overlap) are directly analogous to our coarse partition sizing and VRAM budget allocation problems.
---

---
- **Title**: Buffer Management in Relational Database Systems
- **Author(s)**: Giovanni Maria Sacco, Mario Schkolnick
- **Year**: 1986
- **Venue**: ACM Transactions on Database Systems (TODS), Vol. 11, No. 4
- **Summary**: Introduces the hot-set model for characterizing buffer requirements of relational queries. A query's hot set is the minimum buffer pages needed to avoid thrashing. Proposes DP/greedy algorithms for optimal buffer page assignment across concurrent queries and integrates buffer allocation into query optimization.
- **Relevance**: Alternative formalization of join scheduling through buffer allocation optimization. The hot-set model's approach — characterizing minimum cache requirements per operation and optimizing allocation — is conceptually related to our VRAM budget allocation problem where D partition data, index, Q buffers, and result buffers compete for limited VRAM.
---

---
- **Title**: NOCAP: Near-Optimal Correlation-Aware Partitioning Joins
- **Author(s)**: Zhaoxing Zhu, Xiao Hu, Manos Athanassoulis
- **Year**: 2023
- **Venue**: Proceedings of the ACM on Management of Data (PACMMOD), Vol. 1, No. 4
- **Summary**: Formalizes hybrid hash join partition-to-memory assignment as a knapsack-style optimization problem, exploiting data correlations between partition sizes and join selectivities. By solving a knapsack problem (which partitions to keep in memory given a budget), the join significantly reduces I/O compared to random hash-based partition assignment.
- **Relevance**: Closest analog to DiskJoin's MECC formulation in spirit. Both NOCAP and MECC pose join scheduling as combinatorial optimization over which partitions to cache. NOCAP uses knapsack (which partitions to keep), MECC uses graph edge-covering (what order to process pairs). Both exploit the known-a-priori workload for offline optimization.
---


---
- **Title**: Ginex: SSD-enabled Billion-scale Graph Neural Network Training on a Single Machine via Provably Optimal In-memory Caching
- **Author(s)**: Yeonhong Park, Sunhong Min, Jae W. Lee
- **Year**: 2022
- **Venue**: PVLDB, Vol. 15, No. 11 (VLDB 2022)
- **Summary**: First SSD-based GNN training system for billion-node graphs on a single machine. Separates GNN's sample and gather phases (inspector-executor model) so the access sequence is known before execution, enabling Belady's optimal cache replacement for feature vectors. Achieves up to 2.67x throughput improvement over SSD-extended PyTorch Geometric.
- **Relevance**: Almost identical conceptual insight to DiskJoin. Both exploit predetermined access sequences to apply Belady's optimal caching — Ginex via the sampling phase, DiskJoin via the bipartite bucket graph. Validates the "predetermined access sequence → Belady's caching" pattern applicable to our system.
---

---
- **Title**: P-OPT: Practical Optimal Cache Replacement for Graph Analytics
- **Author(s)**: Vignesh Balaji, Neal Crago, Aamer Jaleel, Brandon Lucia
- **Year**: 2021
- **Venue**: IEEE International Symposium on High-Performance Computer Architecture (HPCA 2021)
- **Summary**: Emulates Belady's MIN optimal cache replacement for graph analytics by using the transpose of a graph's adjacency matrix to predict future memory accesses. Achieves near-optimal cache hit rates without expensive offline profiling, demonstrating that structured workloads (graph processing) enable practical optimal caching infeasible for general workloads.
- **Relevance**: Same conceptual insight as DiskJoin and Ginex — exploiting workload structure for optimal caching. Reinforces the design principle underlying our data scheduling: the predetermined partition-pair access sequence enables optimal caching across our disk→RAM→VRAM hierarchy.
---

---
- **Title**: Speedup Graph Processing by Graph Ordering (Gorder)
- **Author(s)**: Hao Wei, Jeffrey Xu Yu, Can Lu, Xuemin Lin
- **Year**: 2016
- **Venue**: ACM SIGMOD International Conference on Management of Data (SIGMOD 2016)
- **Summary**: Proposes Gorder, a graph vertex reordering algorithm that greedily optimizes a neighborhood-based locality score so that frequently co-accessed vertices are stored nearby in memory. Uses a sliding window greedy algorithm. Demonstrates significant speedups (up to 3-5x) across multiple graph algorithms including BFS, PageRank, and SSSP.
- **Relevance**: Direct ancestor of DiskJoin's task ordering technique. DiskJoin adapts Gorder's objective function to reorder the bipartite bucket graph. Our system can apply the same Gorder-style reordering to partition-pair scheduling at both the RAM and VRAM cache levels.
---

---
- **Title**: Graph Reordering for Cache-Efficient Near Neighbor Search
- **Author(s)**: Benjamin Coleman, Santiago Segarra, Alexander J. Smola, Anshumali Shrivastava
- **Year**: 2022
- **Venue**: Advances in Neural Information Processing Systems (NeurIPS 2022)
- **Summary**: Applies graph reordering techniques to ANN graph indices (HNSW, NSG) to reduce cache misses during search. Demonstrates that graph-based ANN search suffers from poor cache locality and that reordering vertex IDs so nearby graph vertices are stored in nearby memory locations significantly improves QPS.
- **Relevance**: Bridges graph reordering (Gorder) with vector search workloads. Demonstrates the applicability of locality-aware reordering to ANN indices, relevant both for our partition-level scheduling and potentially for within-partition GPU cache performance with graph-based indexes (CAGRA/HNSW).
---

---
- **Title**: A Closer Look at Lightweight Graph Reordering
- **Author(s)**: Priyank Faldu, Jeff Diamond, Boris Grot
- **Year**: 2019
- **Venue**: IEEE International Symposium on Workload Characterization (IISWC 2019)
- **Summary**: Evaluates lightweight graph reordering techniques and proposes Degree-Based Grouping (DBG), a simple reordering that segregates high-degree vertices into contiguous memory. Key finding: even simple reorderings capture the majority of the cache benefit of expensive algorithms like Gorder, at a fraction of the preprocessing cost.
- **Relevance**: Practical insight for our partition ordering. If lightweight reordering captures most of the cache benefit, our partition-pair scheduling may not need full Gorder optimization — a simpler heuristic could achieve comparable I/O reduction. Especially relevant given our moderate partition count (~100-200).
---

---
- **Title**: GridGraph: Large-Scale Graph Processing on a Single Machine Using 2-Level Hierarchical Partitioning
- **Author(s)**: Xiaowei Zhu, Wentao Han, Wenguang Chen
- **Year**: 2015
- **Venue**: USENIX Annual Technical Conference (USENIX ATC 2015)
- **Summary**: Out-of-core graph processing system using 2D partitioning (vertex chunks × edge blocks) with a dual sliding window for streaming edges. Selective scheduling of edge blocks based on which vertex chunks are cached minimizes I/O for graphs far exceeding main memory.
- **Relevance**: Same partition-order-for-locality principle as our system. GridGraph's 2D edge grid is structurally analogous to our bipartite bucket graph: edge blocks connect source/destination vertex chunks just as partition pairs connect D and Q partitions.
---

---
- **Title**: X-Stream: Edge-Centric Graph Processing Using Streaming Partitions
- **Author(s)**: Amitabha Roy, Ivo Mihailovic, Willy Zwaenepoel
- **Year**: 2013
- **Venue**: ACM Symposium on Operating Systems Principles (SOSP 2013)
- **Summary**: Introduces an edge-centric scatter-gather model for out-of-core graph processing that streams edges sequentially from disk. Partitions vertices so each partition's state fits in memory, then streams edges through — maximizing sequential I/O bandwidth rather than performing random accesses.
- **Relevance**: Conceptually similar to our block nested loop join: pin one partition in fast memory, stream the other data through. X-Stream demonstrates that sequential streaming with cache-sized partitions is effective for out-of-core processing.
---

---
- **Title**: Scheduling Multiprocessor Tasks with Equal Processing Times as a Mixed Graph Coloring Problem
- **Author(s)**: Yuri N. Sotskov, Ekaterina I. Mihova
- **Year**: 2021
- **Venue**: Algorithms (MDPI), Vol. 14, No. 8, Article 246
- **Summary**: Reduces multiprocessor scheduling with simultaneous tasks and precedence constraints to a mixed graph coloring problem. Vertices are tasks, edges are conflicts (cannot overlap), arcs are precedence constraints. Connects scheduling theory to graph coloring theory.
- **Relevance**: Example of task scheduling formalized as a graph problem, providing context for DiskJoin's MECC formalization. Graph coloring addresses resource conflict avoidance, while MECC addresses cache reuse maximization — both demonstrate that graph-based formalization enables principled scheduling.
---

---
- **Title**: Developing Graph-Based Co-Scheduling Algorithms on Multicore Computers
- **Author(s)**: Ligang He, Hao Zhu, Stephen A. Jarvis
- **Year**: 2016
- **Venue**: IEEE Transactions on Parallel and Distributed Systems (TPDS), Vol. 27, No. 6
- **Summary**: Formalizes job co-scheduling on shared-cache multicore processors as graph partitioning, where vertices are jobs and edge weights encode cache contention. Proposes algorithms for optimal/near-optimal job groupings that minimize shared cache interference.
- **Relevance**: Example of scheduling as graph partitioning for cache sharing. He et al.'s graph encodes cache contention (conflict avoidance), while DiskJoin's bucket graph encodes cache sharing (locality maximization) — both use graph structure for cache-aware scheduling.
---

---
- **Title**: I/O Complexity: The Red-Blue Pebble Game
- **Author(s)**: Jia-Wei Hong, H. T. Kung
- **Year**: 1981
- **Venue**: STOC 1981
- **Summary**: Foundational paper formalizing I/O complexity of computations under a two-level memory hierarchy using the red-blue pebble game model. Red pebbles represent fast memory (cache) slots, blue pebbles represent slow memory (disk). Proves the Ω(n³/√M) I/O lower bound for dense matrix multiplication with cache size M. Establishes that data movement, not computation, is the fundamental bottleneck for many algorithms when data exceeds fast memory.
- **Relevance**: Theoretical foundation for Formulation E (Sparse Join Matrix Traversal). The pebble game directly models our VRAM (red pebbles) vs. disk/RAM (blue pebbles) hierarchy. The I/O lower bound framework can be applied to derive theoretical lower bounds on the data movement cost of our partitioned similarity join under VRAM budget C'. Extensions by Ballard et al. (2013) adapt these bounds to sparse computations, directly applicable to our sparse join matrix J.
---

---
- **Title**: Optimizing the Performance of Sparse Matrix-Vector Multiplication (Tiling Optimizations for Sparse Matrix Computations)
- **Author(s)**: Eun-Jin Im, Katherine Yelick
- **Year**: 2001
- **Venue**: International Journal of High Performance Computing Applications (IJHPCA)
- **Summary**: Introduces cache-aware tiling for sparse matrix operations, specifically row-panel decomposition for SpMM where panel height is chosen so all accessed dense-matrix columns fit in cache. Develops an analytical model for selecting panel height based on cache size and nonzero distribution. Also covers register blocking and cache blocking with automatic block size selection based on matrix structure and hardware parameters.
- **Relevance**: Directly validates Formulation E's panel decomposition approach. Their row-panel tiling for SpMM — where panel height controls cache occupancy of column data — is structurally identical to our panel traversal of the join matrix J, where panel height controls how many Q-blocks must be cached in VRAM. Their analytical model for panel height selection based on nonzero distribution informs our panel sizing under VRAM budget C'.
---

---
- **Title**: Communication Optimal Parallel Multiplication of Sparse Random Matrices
- **Author(s)**: Grey Ballard, Aydin Buluc, James Demmel, Laura Grigori, Benjamin Lipshitz, Oded Schwartz, Sivan Toledo
- **Year**: 2013
- **Venue**: SPAA 2013 (ACM Symposium on Parallelism in Algorithms and Architectures)
- **Summary**: Extends Hong-Kung I/O lower bounds to sparse matrix-matrix multiplication (SpMM). Proves that for sparse matrices, the I/O lower bound depends on the sparsity structure (nonzero pattern), not just the total nonzero count. Shows that for Erdos-Renyi random sparse matrices, 1D and 2D decompositions are communication-optimal under certain density conditions. Establishes that sparse I/O complexity is fundamentally determined by the interaction between sparsity pattern and cache/memory hierarchy.
- **Relevance**: Key theoretical reference for Formulation E. Proves that the I/O cost of traversing our sparse join matrix J depends on J's specific nonzero pattern — which we control by choosing partition counts (m, n). This means our choice of (m, n) affects not just the number of nonzeros (surviving pairs) but the I/O complexity of processing them. Their lower bounds could yield a theoretical contribution: proving that our panel-based traversal is near-optimal for the join matrix's sparsity structure.
---

---
- **Title**: Hypergraph Partitioning for Sparse Matrix-Matrix Multiplication
- **Author(s)**: Grey Ballard, Alex Druinsky, Nicholas Knight, Oded Schwartz
- **Year**: 2015
- **Venue**: ACM Transactions on Parallel Computing (TOPC)
- **Summary**: Shows that minimizing communication (data movement) in SpMM is equivalent to hypergraph partitioning. Each nonzero entry contributes to hyperedges capturing data reuse patterns. Standard hypergraph partitioning tools (PaToH, Zoltan) can produce SpMM schedules with significantly less communication than naive 1D/2D decompositions. Demonstrates that hypergraph models capture reuse structure missed by simpler graph-based partitioning.
- **Relevance**: Directly maps to our scheduling problem. The hypergraph model for SpMM data reuse is equivalent to modeling Q-block reuse across D-partition groups in our join: each Q-block is a hyperedge connecting all D-partitions that access it. Hypergraph partitioning tools (PaToH, hMETIS) could be applied directly to our join matrix J to find near-optimal panel decompositions. This provides a concrete algorithmic alternative to Gorder-style greedy reordering.
---

---
- **Title**: Track Join: Distributed Joins with Minimal Network Traffic
- **Author(s)**: Orestis Polychroniou, Rajkumar Sen, Kenneth A. Ross
- **Year**: 2014
- **Venue**: SIGMOD 2014
- **Summary**: Introduces Track Join, a distributed join algorithm that explicitly constructs a sparse matrix of partition-pair interactions (the "tracking matrix") to minimize network data transfer. The tracking matrix records which partitions of the probe relation are needed by each partition of the build relation. By analyzing this matrix, Track Join transfers only the necessary data, achieving minimal network traffic for distributed hash joins.
- **Relevance**: Closest database analog to Formulation E. Track Join's tracking matrix is structurally identical to our join matrix J[m,n] — both are sparse binary matrices where nonzeros indicate which partition pairs need processing. The key difference: Track Join treats the tracking matrix as given by the data and optimizes data movement based on it, while our Formulation E co-optimizes the matrix structure (via m, n) and traversal schedule. Track Join validates the "sparse matrix view of partitioned joins" abstraction in the database community.
---

---
- **Title**: Optimizing Main-Memory Join on Modern Hardware
- **Author(s)**: Stefan Manegold, Peter Boncz, Martin Kersten
- **Year**: 2002
- **Venue**: IEEE Transactions on Knowledge and Data Engineering (TKDE)
- **Summary**: Develops a detailed analytical cost model for radix-partitioned hash joins on modern hardware, where partition count is the key tuning parameter. The cost model accounts for cache line sizes, TLB effects, and multi-level memory hierarchy. Shows that the optimal partition count depends on the hardware cache hierarchy and derives it analytically. The cost model has the form: total_cost = f(num_partitions) = partition_cost(p) + probe_cost(p), where p controls cache behavior during probing.
- **Relevance**: Closest methodological analog to Formulation C's joint optimization over (m, n). Their analytical cost model parameterized by partition count, optimized against the hardware memory hierarchy, is structurally identical to our T(m,n) = |D| + ρ_Q(m,n,C') · |Q| optimized against VRAM budget. Their finding that optimal partition count is hardware-dependent (cache size determines the sweet spot) parallels our VRAM-adaptive partitioning where optimal (m, n) depends on available VRAM C.
---

---
- **Title**: Dostoevsky: Better Space-Time Trade-Offs for LSM-Tree Based Key-Value Stores via Adaptive Removal of Superfluous Merging
- **Author(s)**: Niv Dayan, Stratos Idreos
- **Year**: 2018
- **Venue**: SIGMOD 2018
- **Summary**: Introduces Lazy Leveling, a hybrid merge policy for LSM-trees that interpolates between leveling and tiering to optimize the read/write/space amplification tradeoff. Key methodology: parameterizes the merge policy with continuous variables (size ratios, tiering fractions per level) and uses calculus to find the optimal configuration that minimizes a weighted cost function including I/O amplification. Achieves Pareto-optimal tradeoffs across the full read/write/space spectrum.
- **Relevance**: Methodological precedent for Formulation C's continuous relaxation approach. Dostoevsky parameterizes a discrete design space (merge policies) with continuous variables and optimizes an I/O amplification cost function — structurally identical to our approach of parameterizing partition counts (m, n) and optimizing T(m,n) = |D| + ρ_Q · |Q|. Citing this as a methodological analog strengthens the positioning of Formulation C as a principled approach rather than ad-hoc tuning.
---

---
- **Title**: Evaluation Techniques for Storage Hierarchies
- **Author(s)**: R. L. Mattson, J. Gecsei, D. R. Slutz, I. L. Traiger
- **Year**: 1970
- **Venue**: IBM Systems Journal, Vol. 9, No. 2
- **Summary**: Introduces stack distance (reuse distance) analysis — the foundational theory for characterizing cache behavior with a scalar. Defines the inclusion property: if a reference hits in a cache of size M, it also hits in any cache of size M' > M. This enables computing the miss rate as a monotone function of cache size from a single pass over the access trace. The stack distance distribution fully determines cache performance for all LRU-family replacement policies.
- **Relevance**: Theoretical foundation for Formulation C's ρ_Q as a function of C'. The inclusion function (miss rate vs. cache size) is exactly the relationship between our reuse factor ρ_Q and effective cache budget C'. Stack distance theory justifies collapsing schedule-dependent cache behavior into a scalar: given the access trace (determined by σ), ρ_Q(C') is a well-defined monotone function. This provides the theoretical grounding for the empirical estimation approach — sample the access trace on learning data, compute the stack distance distribution, and predict ρ_Q for any C'.
---