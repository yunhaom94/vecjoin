# Plan
*This file outlines a list of items that need to be done for the project.*



## TODO List
*This is a list of tasks that need to be done for the project. This should be a living document that can be changed as the project evolves.*

- Baseline Design
    - Assume cache (max usable VRAM) x10 (adjustable to see which looks the best) = dataset size
    - Use FAISS (IVF) + Raw Nested Loop join
- SimJoin-inspired fine-search feasibility
    - Hold one representative `D_i` and its graph index fully resident in HBM; exclude outer I/O first
    - Build one query proximity graph/MST per correlated `Q_j`; cut into a shallow forest with bounded depth/cluster size
    - Compare at equal recall: independent batched graph search; MST reorder only; literal parent-window sliding; shallow forest + compact parent seeds; forest + sibling candidate microtiles
    - Workloads: correlated stream batch vs shuffled/OOD batch; sparse mean window `~1` and moderate window `~32-100`
    - Metrics: block-pair latency, distance computations, graph expansions, unique node/vector loads, HBM bytes, occupancy, p95 query work, seed/frontier memory, recall
    - Continue if shallow-forest reuse is `>=20%` faster than tuned independent GPU search with `<10%` slowdown on uncorrelated queries
    - If reorder-only captures most of the gain, keep ordering and drop stateful sliding

## Paper Outline
*This is a outline of the paper that we will write the project. This should be a list of sections, subsections, and summaries of what will be included in each section. This should be a living document that can be changed as the project evolves.* 

- [ ] Introduction
- [ ] Background and motivation
  - [ ]  ...
  - [ ]  ...



## Implementation Plan
*This is a outline of the implementation plan for the project. This should be a list of tasks that need to be done for the implementation of the project. This should be a living document that can be changed as the project evolves.*
- [ ] Data ingestion and parsing
- [ ] Add a per-`D_i` graph-index loader/cache and indexed `GraphJoiner` beside the exact dense joiner
- [ ] Compile per-`Q_j` shallow proximity forests; retain explicit query/global-ID maps after reordering
- [ ] Implement frontier/ready-queue batching with bounded device seed/frontier storage and local-entry fallback
- [ ] Add sibling candidate-slab execution and adaptive dense vs indexed dispatch
- [ ] Instrument fine-search work, HBM traffic, occupancy, state size, and recall separately from outer I/O


## Experiment Plan
Datasets Q x D
- DEEP1B  GoogLeNet 96D FP32 image - 100M x 900M
- SIFT1B 128D UINT8 image - 100M x 900M
- Text2Image-1B 200D FP32 multmodal CLIP - 50M (text) x 500M (image)
- LAION2B-en 768D FP16 text2img CLIP - 100M (text) x 1B (image)
- https://huggingface.co/datasets/CohereLabs/wikipedia-2023-11-embed-multilingual-v3  Cohere Embed V3 embedding model. 200M 1024D FP32 -  20M x 180M
- https://huggingface.co/datasets/Snowflake/mteb-retrieval-snowflake-arctic-embed-m-v1.5 30M 768D FP32 3M x 27M


For each dataset
- Find threshold for 
0.5 mean pairs per query (ppq)
1 mean ppq
1.5 mean ppq
2 mean ppq
